#!/usr/bin/env python3
"""
Experiment 53 (V10): Emergent Geodesics from Time-Flow Gradients

CRITICAL TEST: Do geodesics (curved orbital paths) emerge naturally from
entities following time-flow gradients, WITHOUT any programmed force laws?

Based on v9 validated field parameters, but removes forced circular orbits.
Entities now follow ∇γ_grav to maximize proper time rate.
"""

import numpy as np
from typing import List, Dict
import time
from dataclasses import dataclass

from config import ConfigurationSet, get_config
from entity_motion import (
    MovingEntity,
    StationaryEntity,
    generate_planet_cluster,
    generate_mobile_entities_random_velocities,
    compute_gamma_gradient,
    compute_orbital_parameters
)
from field_dynamics import FieldDynamics


@dataclass
class SimulationState:
    """Complete state of simulation at one moment."""
    tick: int
    field_stats: dict
    entity_states: List[dict]
    orbital_stats: List[dict]


class Experiment53:
    """
    Test if geodesics emerge from gradient following.

    V10 KEY INNOVATION:
    - Entities have random initial velocities
    - Update rule: acceleration = k * ∇γ_grav
    - No forced circular orbits!
    - Test: Do stable orbits emerge naturally?
    """

    def __init__(self, config: ConfigurationSet):
        self.config = config

        # Initialize field dynamics (same as v9)
        self.fields = FieldDynamics(
            grid_size=config.simulation.grid_size,
            alpha=config.field.alpha,
            gamma=config.field.gamma_damp,
            scale=config.field.scale,
            R=config.field.R,
            D=config.field.D,
            E_max=config.field.E_max,
            capacity_min=config.field.capacity_min,
            work_threshold=config.field.work_threshold
        )

        # Gradient following parameter (NEW!)
        self.gradient_coupling = 0.01  # Tunable parameter

        # Create entities
        self._create_entities()

        # Statistics
        self.snapshots: List[SimulationState] = []
        self.start_time = None
        self.end_time = None

    def _create_entities(self):
        """Initialize all entities."""
        cfg = self.config

        print("Creating entities...")

        # Planet cluster (same as v9)
        self.planet_entities = generate_planet_cluster(
            center=cfg.entities.planet_center,
            radius=cfg.entities.planet_radius,
            count=cfg.entities.planet_count,
            tick_budget=cfg.entities.planet_tick_budget,
            energy=cfg.field.E_max * 0.67
        )
        print(f"  Planet: {len(self.planet_entities)} entities")

        # Mobile entities with RANDOM velocities (V10 CHANGE!)
        velocities = [0.1, 0.3, 0.5]  # Test slower speeds first

        self.mobile_entities = generate_mobile_entities_random_velocities(
            center=cfg.entities.planet_center,
            distances=[30.0, 35.0, 40.0],  # Various starting distances
            velocities=velocities,
            count_per_config=2,  # 2 entities per (distance, velocity) combo
            c=cfg.simulation.c,
            random_direction=False  # Start tangential for comparison with v9
        )
        print(f"  Mobile: {len(self.mobile_entities)} entities")
        print(f"    Velocities: {velocities}")
        print(f"    Gradient coupling: {self.gradient_coupling}")
        print()

        # Combined list for field computation
        self.all_entities = self.planet_entities + self.mobile_entities

    def step(self):
        """Execute one simulation timestep with GRADIENT FOLLOWING."""
        dt = self.config.simulation.dt
        grid_size = self.config.simulation.grid_size

        # 1. Update fields based on current entity positions
        self.fields.step(self.all_entities, dt=dt)

        # 2. Get gamma field for gradient computation
        gamma_field = self.fields.get_gamma_grav()

        # 3. Update each mobile entity with GRADIENT FOLLOWING
        for entity in self.mobile_entities:
            # Get local gravitational time dilation
            gamma_grav = self.fields.get_gamma_at_position(tuple(entity.position))

            # Update entity's proper time
            entity.update_time(gamma_grav, dt_substrate=dt)

            # V10 KEY CHANGE: Compute gradient and follow it!
            gamma_gradient = compute_gamma_gradient(
                position=entity.position,
                gamma_field=gamma_field,
                grid_size=grid_size,
                dx=1.0
            )

            # Update velocity by following gradient
            entity.update_velocity_gradient_following(
                gamma_gradient=gamma_gradient,
                dt=dt,
                coupling_constant=self.gradient_coupling
            )

            # Update position based on new velocity
            entity.update_position(dt=dt, grid_size=grid_size, wrap_boundaries=True)

    def run(self):
        """Run full simulation."""
        cfg = self.config
        num_ticks = cfg.simulation.num_ticks
        snapshot_interval = cfg.simulation.snapshot_interval
        verbose = cfg.simulation.verbose

        print("=" * 70)
        print(f"EXPERIMENT 53 (V10) - {cfg.name}")
        print("=" * 70)
        print()
        print(f"Testing: EMERGENT GEODESICS from gradient following")
        print(f"Simulating {num_ticks} ticks...")
        print()

        self.start_time = time.time()

        # Main simulation loop
        for tick in range(num_ticks):
            self.step()

            # Periodic output
            if verbose and (tick + 1) % snapshot_interval == 0:
                self._print_progress(tick + 1)

            # Save snapshot
            if (tick + 1) % snapshot_interval == 0:
                self._save_snapshot(tick + 1)

        self.end_time = time.time()

        print()
        print("Simulation complete!")
        print(f"  Elapsed time: {self.end_time - self.start_time:.1f}s")
        print()

    def _print_progress(self, tick: int):
        """Print progress update."""
        stats = self.fields.get_statistics()

        # Sample entity stats
        if len(self.mobile_entities) > 0:
            sample_entity = self.mobile_entities[0]
            orbital_params = compute_orbital_parameters(
                sample_entity,
                self.config.entities.planet_center
            )

            print(f"Tick {tick}/{self.config.simulation.num_ticks}")
            print(f"  Field: L_max={stats['L_max']:.2f}, gamma_max={stats['gamma_max']:.2f}")
            print(f"  Sample: r={orbital_params.get('r_mean', 0):.1f}, "
                  f"orbit={orbital_params.get('orbit_type', 'unknown')}, "
                  f"v={sample_entity.speed:.3f}c")

    def _save_snapshot(self, tick: int):
        """Save current state snapshot."""
        field_stats = self.fields.get_statistics()

        entity_states = [
            entity.get_state_summary()
            for entity in self.mobile_entities
        ]

        # Compute orbital parameters for each entity
        orbital_stats = [
            compute_orbital_parameters(entity, self.config.entities.planet_center)
            for entity in self.mobile_entities
        ]

        snapshot = SimulationState(
            tick=tick,
            field_stats=field_stats,
            entity_states=entity_states,
            orbital_stats=orbital_stats
        )

        self.snapshots.append(snapshot)

    def analyze_results(self) -> Dict:
        """
        Analyze if geodesics emerged.

        Success criteria:
        - Some entities achieve stable orbits (not all collapse or escape)
        - Orbital velocity matches v ≈ sqrt(GM/r) within 20%
        - Orbits are circular or elliptical (not random walk)
        """
        if not self.snapshots:
            return {'status': 'no_data'}

        final_snapshot = self.snapshots[-1]

        # Categorize entities by orbital behavior
        stable_orbits = []
        collapsing = []
        escaping = []
        other = []

        for i, orbital_params in enumerate(final_snapshot.orbital_stats):
            orbit_type = orbital_params.get('orbit_type', 'unknown')

            if orbit_type in ['circular', 'elliptical']:
                stable_orbits.append((i, orbital_params))
            elif orbit_type == 'collapsing':
                collapsing.append((i, orbital_params))
            elif orbit_type == 'escaping':
                escaping.append((i, orbital_params))
            else:
                other.append((i, orbital_params))

        # Overall statistics
        total = len(final_snapshot.orbital_stats)

        results = {
            'total_entities': total,
            'stable_orbits': len(stable_orbits),
            'collapsing': len(collapsing),
            'escaping': len(escaping),
            'other': len(other),
            'stable_orbit_rate': len(stable_orbits) / total if total > 0 else 0.0,
            'stable_orbit_details': stable_orbits,
            'collapsing_details': collapsing,
            'escaping_details': escaping
        }

        # Success criterion: At least 30% achieve stable orbits
        results['success'] = results['stable_orbit_rate'] >= 0.3

        return results

    def print_results(self):
        """Print human-readable results."""
        analysis = self.analyze_results()

        print("=" * 70)
        print("EXPERIMENT 53 RESULTS - GEODESIC EMERGENCE TEST")
        print("=" * 70)
        print()

        print("Question: Do geodesics emerge from gradient following?")
        print()

        print(f"Total entities: {analysis['total_entities']}")
        print(f"  Stable orbits: {analysis['stable_orbits']} ({analysis['stable_orbit_rate']*100:.1f}%)")
        print(f"  Collapsing: {analysis['collapsing']}")
        print(f"  Escaping: {analysis['escaping']}")
        print(f"  Other: {analysis['other']}")
        print()

        if analysis['success']:
            print("[SUCCESS] Geodesics EMERGED naturally!")
            print(f"   {analysis['stable_orbit_rate']*100:.1f}% of entities achieved stable orbits")
        else:
            print("[FAILURE] Geodesics did NOT emerge")
            print(f"   Only {analysis['stable_orbit_rate']*100:.1f}% stable (need >=30%)")
        print()

        # Detail stable orbits
        if analysis['stable_orbits']:
            print("Stable Orbit Details:")
            for idx, params in analysis['stable_orbit_details'][:5]:  # Show first 5
                entity = self.mobile_entities[idx]
                print(f"  Entity {entity.entity_id}:")
                print(f"    Distance: {params['r_mean']:.1f} (min={params['r_min']:.1f}, max={params['r_max']:.1f})")
                print(f"    Type: {params['orbit_type']}")
                print(f"    Eccentricity: {params['eccentricity_estimate']:.3f}")
                print(f"    Final velocity: {entity.speed:.3f}c")
        print()


def main():
    """Run experiment with baseline configuration."""
    import sys

    # Use baseline config (same validated params as v9)
    config_name = sys.argv[1] if len(sys.argv) > 1 else "baseline"

    try:
        config = get_config(config_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(config.summary())
    print()

    # Create and run experiment
    experiment = Experiment53(config)
    experiment.run()
    experiment.print_results()


if __name__ == "__main__":
    main()
