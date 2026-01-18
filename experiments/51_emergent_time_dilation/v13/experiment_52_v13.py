#!/usr/bin/env python3
"""
Experiment 52 (V13): Black Hole with Full Collision Physics

Tests what black hole structure emerges when combining:
- V12's supermassive field (100× mass, gamma → infinity)
- Experiment 55's three-regime collision framework
- Perfect energy/momentum conservation

Key Question: Does an accretion disk, stable structures, or complete dispersion emerge?
"""

import numpy as np
from typing import List, Dict
import time
import json
from pathlib import Path

from config import ConfigurationSet, get_config
from field_dynamics import FieldDynamics
from entity_adapter import (
    PatternEntity,
    create_planet_cluster_pattern_entities,
    create_test_particles_mixed
)
from collision_integration import CollisionManager
from entity_motion import compute_gamma_gradient


class BlackHoleSimulation:
    """
    Black hole simulation with full collision physics.

    Combines supermassive field (v12) with three-regime collisions (Exp 55).
    """

    def __init__(
        self,
        mass_multiplier: int = 100,
        num_ticks: int = 5000,
        snapshot_interval: int = 100
    ):
        self.mass_multiplier = mass_multiplier
        self.num_ticks = num_ticks
        self.snapshot_interval = snapshot_interval

        # Configuration
        self.config = get_config("baseline")
        self.grid_size = self.config.simulation.grid_size
        self.c = self.config.simulation.c

        # Field dynamics with SUPERMASSIVE source
        print("Initializing field dynamics...")
        self.fields = FieldDynamics(
            grid_size=self.grid_size,
            alpha=self.config.field.alpha,
            gamma=self.config.field.gamma_damp,
            scale=self.config.field.scale * (mass_multiplier / 10.0),  # Scale for 100×
            R=self.config.field.R,
            D=self.config.field.D,
            E_max=self.config.field.E_max,
            capacity_min=self.config.field.capacity_min,
            work_threshold=self.config.field.work_threshold,
            allow_divergence=True  # Allow gamma → ∞ for black holes
        )

        # Collision manager
        print("Initializing collision physics...")
        self.collision_manager = CollisionManager(
            E_max=self.config.field.E_max,
            grid_size=self.grid_size,
            c=self.c
        )

        # Gradient following strength
        self.gradient_coupling = 0.01

        # Create entities
        self._create_entities()

        # Tracking
        self.snapshots = []
        self.conservation_history = []
        self.start_time = None
        self.end_time = None

    def _create_entities(self):
        """Initialize supermassive black hole + test particles."""
        print("\nCreating entities...")

        # SUPERMASSIVE planet cluster (100× baseline)
        planet_count = self.config.entities.planet_count * self.mass_multiplier
        center = self.config.entities.planet_center

        self.planet_entities = create_planet_cluster_pattern_entities(
            center=center,
            radius=self.config.entities.planet_radius,
            count=planet_count,
            energy=self.config.field.E_max * 0.67
        )
        print(f"  [OK] Planet cluster: {len(self.planet_entities)} entities (SUPERMASSIVE)")

        # Test particles at various distances (mixed protons/electrons)
        test_distances = [15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0]
        test_velocities = [0.0, 0.1, 0.3, 0.5]  # Fraction of c

        self.mobile_entities = create_test_particles_mixed(
            center=center,
            distances=test_distances,
            velocities=test_velocities,
            c=self.c
        )
        print(f"  [OK] Test particles: {len(self.mobile_entities)}")
        print(f"    Distances: {test_distances}")
        print(f"    Velocities: {test_velocities}")
        print(f"    Types: Mixed protons/electrons")

        # All entities
        self.all_entities = self.planet_entities + self.mobile_entities
        print(f"  [OK] Total entities: {len(self.all_entities)}")
        print()

    def run(self):
        """Execute simulation."""
        print("=" * 70)
        print("EXPERIMENT 52 V13: BLACK HOLE WITH FULL COLLISION PHYSICS")
        print("=" * 70)
        print()
        print(f"Configuration:")
        print(f"  Grid: {self.grid_size}×{self.grid_size}")
        print(f"  Ticks: {self.num_ticks}")
        print(f"  Mass multiplier: {self.mass_multiplier}×")
        print(f"  Collision physics: THREE-REGIME (merge/explode/excite)")
        print(f"  Conservation tracking: ENABLED")
        print()

        self.start_time = time.time()

        for tick in range(self.num_ticks):
            # Update fields every 10 ticks (expensive)
            if tick % 10 == 0:
                self.fields.step(self.all_entities, dt=1.0)

            # Get gamma field
            gamma_field = self.fields.get_gamma_grav()

            # Update mobile entities (planet entities are stationary)
            for entity in self.mobile_entities:
                # Gradient-following acceleration
                pos = entity.position
                grad = compute_gamma_gradient(pos, gamma_field, self.grid_size)
                acceleration = -self.gradient_coupling * grad

                entity.apply_acceleration(acceleration)
                entity.clamp_speed(self.c)
                entity.update_position(dt=1.0)

            # Process collisions (ALL entities)
            self.all_entities, collision_stats = self.collision_manager.process_all_collisions(
                self.all_entities,
                tick
            )

            # Update mobile entities list (some may have been destroyed/created)
            # Planet entities remain separate (stationary)
            planet_ids = {e.entity_id for e in self.planet_entities}
            self.mobile_entities = [e for e in self.all_entities if e.entity_id not in planet_ids]

            # Conservation check
            conservation = self.collision_manager.check_conservation(
                self.all_entities,
                tick,
                verbose=(tick % 1000 == 0)
            )
            self.conservation_history.append(conservation)

            # Snapshot
            if tick % self.snapshot_interval == 0:
                self._save_snapshot(tick, collision_stats, conservation)

                if tick % 1000 == 0:
                    elapsed = time.time() - self.start_time
                    self._print_status(tick, elapsed, collision_stats, conservation)

        self.end_time = time.time()
        self._print_final_summary()

    def _save_snapshot(self, tick: int, collision_stats: Dict, conservation: Dict):
        """Save snapshot of current state."""
        # Analyze mobile entities
        mobile_data = []
        for entity in self.mobile_entities:
            r = np.linalg.norm(entity.position - np.array(self.config.entities.planet_center))
            v = np.linalg.norm(entity.velocity)

            mobile_data.append({
                'id': entity.entity_id,
                'pattern_type': entity.pattern.pattern_type.value,
                'position': tuple(entity.position),
                'velocity': tuple(entity.velocity),
                'radius': float(r),
                'speed': float(v),
                'energy': float(entity.pattern.energy),
                'mass': float(entity.pattern.mass)
            })

        snapshot = {
            'tick': tick,
            'field_stats': self.fields.get_statistics(),
            'collision_stats': collision_stats,
            'conservation': {
                'dp_magnitude': float(conservation['dp_magnitude']),
                'dE_magnitude': float(conservation['dE_magnitude'])
            },
            'entity_counts': {
                'total': len(self.all_entities),
                'planet': len(self.planet_entities),
                'mobile': len(self.mobile_entities)
            },
            'mobile_entities': mobile_data
        }

        self.snapshots.append(snapshot)

    def _print_status(self, tick: int, elapsed: float, collision_stats: Dict, conservation: Dict):
        """Print current status."""
        print(f"Tick {tick:5d} ({elapsed:.1f}s):")
        print(f"  Entities: {len(self.all_entities)} (planet: {len(self.planet_entities)}, mobile: {len(self.mobile_entities)})")
        print(f"  Collisions: {collision_stats.get('num_cells_with_collisions', 0)} cells")
        print(f"  Regimes: M={collision_stats.get('collisions_by_regime', {}).get('merge', 0)}, "
              f"X={collision_stats.get('collisions_by_regime', {}).get('explode', 0)}, "
              f"E={collision_stats.get('collisions_by_regime', {}).get('excite', 0)}")
        print(f"  Conservation: |dp|={conservation['dp_magnitude']:.6f}, |dE|={conservation['dE_magnitude']:.6f}")
        print()

    def _print_final_summary(self):
        """Print final experiment summary."""
        print()
        print("=" * 70)
        print("SIMULATION COMPLETE")
        print("=" * 70)
        print()

        elapsed = self.end_time - self.start_time
        print(f"Runtime: {elapsed:.1f} seconds ({elapsed/60:.1f} minutes)")
        print(f"Ticks: {self.num_ticks}")
        print(f"Time per tick: {elapsed/self.num_ticks*1000:.2f} ms")
        print()

        # Final entity counts
        print(f"Final entity count: {len(self.all_entities)}")
        print(f"  Planet entities: {len(self.planet_entities)}")
        print(f"  Mobile entities: {len(self.mobile_entities)}")
        print()

        # Collision statistics
        collision_stats = self.collision_manager.get_statistics()
        print(f"Collision statistics:")
        print(f"  Total collisions: {collision_stats['total_collisions']}")
        print(f"  Merge: {collision_stats['merge_count']}")
        print(f"  Explode: {collision_stats['explode_count']}")
        print(f"  Excite: {collision_stats['excite_count']}")
        print()

        # Conservation
        final_conservation = self.conservation_history[-1]
        initial_conservation = self.conservation_history[0]
        print(f"Conservation (initial -> final):")
        print(f"  Momentum drift: {initial_conservation['dp_magnitude']:.6f} -> {final_conservation['dp_magnitude']:.6f}")
        print(f"  Energy drift: {initial_conservation['dE_magnitude']:.6f} -> {final_conservation['dE_magnitude']:.6f}")
        print()

        # Check if conservation held
        if final_conservation['dp_magnitude'] < 0.1 and final_conservation['dE_magnitude'] < 0.1:
            print("  [OK] CONSERVATION LAWS MAINTAINED")
        else:
            print("  [WARNING] CONSERVATION VIOLATIONS DETECTED")
        print()

    def save_results(self, output_dir: Path):
        """Save results to JSON."""
        output_dir.mkdir(parents=True, exist_ok=True)

        results = {
            'experiment': 'Experiment 52 V13: Black Hole with Full Collision Physics',
            'config': {
                'mass_multiplier': self.mass_multiplier,
                'num_ticks': self.num_ticks,
                'grid_size': self.grid_size,
                'allow_divergence': True
            },
            'runtime': {
                'start_time': self.start_time,
                'end_time': self.end_time,
                'elapsed_seconds': self.end_time - self.start_time
            },
            'final_counts': {
                'total_entities': len(self.all_entities),
                'planet_entities': len(self.planet_entities),
                'mobile_entities': len(self.mobile_entities)
            },
            'collision_statistics': self.collision_manager.get_statistics(),
            'conservation': {
                'initial': {
                    'dp': float(self.conservation_history[0]['dp_magnitude']),
                    'dE': float(self.conservation_history[0]['dE_magnitude'])
                },
                'final': {
                    'dp': float(self.conservation_history[-1]['dp_magnitude']),
                    'dE': float(self.conservation_history[-1]['dE_magnitude'])
                }
            },
            'snapshots': self.snapshots
        }

        output_file = output_dir / "experiment_52_v13_results.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"Results saved to: {output_file}")

        return results


if __name__ == "__main__":
    # Run experiment
    sim = BlackHoleSimulation(
        mass_multiplier=100,
        num_ticks=5000,
        snapshot_interval=100
    )

    sim.run()

    # Save results
    output_dir = Path(__file__).parent / "results"
    results = sim.save_results(output_dir)

    print()
    print("=" * 70)
    print("Next: Analyze results to identify structure")
    print("=" * 70)
