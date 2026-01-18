#!/usr/bin/env python3
"""
Experiment 52 (V12): Black Holes with Minimal Collision Physics

CRITICAL VALIDATION TEST: Does the stable c-speed ring from v11 survive
when we add realistic collision physics?

Based on v11 iteration 3 (100× mass, stable c-ring at r ≈ 10.1), but now
includes MINIMAL collision framework:
- Elastic scattering (hard-sphere approximation)
- Momentum conservation
- Speed limit enforcement (v ≤ c)

Does NOT include (see Experiment 55 for full framework):
- Pattern overlap computation
- Cell capacity limits
- Energy overflow (explosion regime)
- Composite object formation

Key Question: Ghost particle artifact vs real tick-frame prediction?
"""

import numpy as np
from typing import List, Dict, Tuple
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
from collision_physics import (
    CollisionDetector,
    ElasticScatteringResolver,
    process_collisions,
    compute_total_momentum,
    compute_total_kinetic_energy
)


@dataclass
class SimulationState:
    """Complete state of simulation at one moment."""
    tick: int
    field_stats: dict
    entity_states: List[dict]
    orbital_stats: List[dict]
    collision_stats: dict  # NEW: collision statistics


class Experiment52V12:
    """
    Test if black hole c-ring survives with collision physics.

    V12 KEY FEATURES (same as v11 iteration 3):
    - 100× planet mass (70,000 entities) - SUPERMASSIVE
    - 10× field source strength (scale = 75.0)
    - Test entities at various distances (r = 10-60)
    - Look for stable c-speed ring at r ≈ 10.1

    NEW IN V12:
    - Collision detection (same cell check)
    - Elastic scattering resolver
    - Momentum/energy conservation tracking
    """

    def __init__(self, config: ConfigurationSet, mass_multiplier: int = 100, allow_divergence: bool = False):
        self.config = config
        self.mass_multiplier = mass_multiplier
        self.allow_divergence = allow_divergence

        # Initialize field dynamics with STRONGER source
        self.fields = FieldDynamics(
            grid_size=config.simulation.grid_size,
            alpha=config.field.alpha,
            gamma=config.field.gamma_damp,
            scale=config.field.scale * (mass_multiplier / 10.0),  # Scale properly for 100×
            R=config.field.R,
            D=config.field.D,
            E_max=config.field.E_max,
            capacity_min=config.field.capacity_min,
            work_threshold=config.field.work_threshold,
            allow_divergence=allow_divergence  # Allow gamma → ∞ for black holes!
        )

        # Gradient following parameter (same as v10/v11)
        self.gradient_coupling = 0.01

        # NEW: Collision physics components
        self.collision_detector = CollisionDetector(grid_spacing=1.0)
        self.collision_resolver = ElasticScatteringResolver(restitution=1.0)  # Fully elastic

        # Create entities (also sets initial_momentum and initial_energy)
        self._create_entities()

        # Statistics
        self.snapshots: List[SimulationState] = []
        self.collision_history: List[Dict] = []
        self.start_time = None
        self.end_time = None

    def _create_entities(self):
        """Initialize all entities."""
        cfg = self.config

        print("Creating entities...")

        # SUPERMASSIVE planet cluster (100× more entities than baseline)
        planet_count = cfg.entities.planet_count * self.mass_multiplier
        self.planet_entities = generate_planet_cluster(
            center=cfg.entities.planet_center,
            radius=cfg.entities.planet_radius,
            count=planet_count,
            tick_budget=cfg.entities.planet_tick_budget,
            energy=cfg.field.E_max * 0.67
        )
        print(f"  Planet: {len(self.planet_entities)} entities (BLACK HOLE with COLLISIONS)")

        # Test entities at VARIOUS DISTANCES to find c-ring
        # Same configuration as v11 iteration 3
        test_distances = [10.0, 15.0, 20.0, 25.0, 30.0, 35.0, 40.0, 50.0, 60.0]
        test_velocities = [0.0, 0.1, 0.3, 0.5]  # Include STATIONARY entities!

        self.mobile_entities = generate_mobile_entities_random_velocities(
            center=cfg.entities.planet_center,
            distances=test_distances,
            velocities=test_velocities,
            count_per_config=1,  # 1 entity per (distance, velocity) combination
            c=cfg.simulation.c,
            random_direction=False  # Tangential for consistency
        )
        print(f"  Test entities: {len(self.mobile_entities)}")
        print(f"    Distances: {test_distances}")
        print(f"    Velocities: {test_velocities}")
        print(f"    Gradient coupling: {self.gradient_coupling}")
        print()
        print(f"  [V12] Collision physics: ENABLED (elastic scattering)")
        print()

        # Combined list for field computation
        self.all_entities = self.planet_entities + self.mobile_entities

        # Store initial conservation quantities
        print(f"[DEBUG] Computing initial momentum from {len(self.mobile_entities)} entities...")
        self.initial_momentum = compute_total_momentum(self.mobile_entities)
        print(f"[DEBUG] Initial momentum result: {self.initial_momentum}, type: {type(self.initial_momentum)}")
        self.initial_energy = compute_total_kinetic_energy(self.mobile_entities)
        print(f"[DEBUG] Initial energy result: {self.initial_energy}, type: {type(self.initial_energy)}")

        # Defensive check
        if self.initial_momentum is None:
            self.initial_momentum = np.zeros(2)
            print("[WARNING] Initial momentum was None, set to zero")
        if self.initial_energy is None:
            self.initial_energy = 0.0
            print("[WARNING] Initial energy was None, set to zero")

    def step(self):
        """Execute one simulation timestep with gradient following AND collision physics."""
        dt = self.config.simulation.dt
        grid_size = self.config.simulation.grid_size

        # 1. Update fields
        self.fields.step(self.all_entities, dt=dt)

        # 2. Get gamma field
        gamma_field = self.fields.get_gamma_grav()

        # 3. Update each mobile entity with gradient following
        for entity in self.mobile_entities:
            gamma_grav = self.fields.get_gamma_at_position(tuple(entity.position))

            # Update time
            entity.update_time(gamma_grav, dt_substrate=dt)

            # Compute gradient
            gamma_gradient = compute_gamma_gradient(
                position=entity.position,
                gamma_field=gamma_field,
                grid_size=grid_size,
                dx=1.0
            )

            # Update velocity (GRADIENT FOLLOWING)
            entity.update_velocity_gradient_following(
                gamma_gradient=gamma_gradient,
                dt=dt,
                coupling_constant=self.gradient_coupling
            )

            # Update position
            entity.update_position(dt=dt, grid_size=grid_size, wrap_boundaries=True)

        # 4. NEW: Process collisions AFTER all entity motion updates
        #    This is the key difference from v11!
        tick = len(self.snapshots) + 1

        # Store pre-collision momentum/energy for validation
        momentum_before = compute_total_momentum(self.mobile_entities)
        energy_before = compute_total_kinetic_energy(self.mobile_entities)

        # Process all collisions
        self.mobile_entities = process_collisions(
            self.mobile_entities,
            self.collision_detector,
            self.collision_resolver,
            tick
        )

        # Verify conservation
        momentum_after = compute_total_momentum(self.mobile_entities)
        energy_after = compute_total_kinetic_energy(self.mobile_entities)

        # Track conservation violations
        momentum_error = np.linalg.norm(momentum_after - momentum_before)
        energy_error = abs(energy_after - energy_before)

        if momentum_error > 1e-6:
            print(f"[WARNING] Tick {tick}: Momentum not conserved! Error = {momentum_error:.2e}")

        if energy_error > 1e-6:
            print(f"[WARNING] Tick {tick}: Energy not conserved! Error = {energy_error:.2e}")

    def run(self):
        """Run full simulation."""
        print(f"[DEBUG run() start] self.initial_momentum = {self.initial_momentum}, type = {type(self.initial_momentum)}")
        print(f"[DEBUG run() start] self.initial_energy = {self.initial_energy}, type = {type(self.initial_energy)}")

        cfg = self.config
        num_ticks = cfg.simulation.num_ticks
        snapshot_interval = cfg.simulation.snapshot_interval
        verbose = cfg.simulation.verbose

        print("=" * 70)
        print(f"EXPERIMENT 52 (V12) - {cfg.name}")
        print("=" * 70)
        print()
        print(f"Testing: C-RING STABILITY with COLLISION PHYSICS")
        print(f"Planet mass: {self.mass_multiplier}× baseline (SUPERMASSIVE)")
        print(f"Collision model: Elastic scattering (minimal framework)")
        print(f"Simulating {num_ticks} ticks...")
        print()

        if self.initial_momentum is not None:
            print(f"Initial momentum: {np.linalg.norm(self.initial_momentum):.6f}")
        else:
            print(f"[ERROR] Initial momentum is None!")

        if self.initial_energy is not None:
            print(f"Initial kinetic energy: {self.initial_energy:.6f}")
        else:
            print(f"[ERROR] Initial energy is None!")
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
        """Print progress update with collision statistics."""
        stats = self.fields.get_statistics()

        # Collision statistics
        num_collisions = len(self.collision_detector.collision_history)
        num_resolved = self.collision_resolver.total_collisions_resolved

        # Sample closest entity
        if len(self.mobile_entities) > 0:
            # Find entity closest to planet
            distances = [
                np.linalg.norm(e.position - np.array(self.config.entities.planet_center))
                for e in self.mobile_entities
            ]
            closest_idx = np.argmin(distances)
            closest = self.mobile_entities[closest_idx]

            # Conservation check
            current_momentum = compute_total_momentum(self.mobile_entities)
            current_energy = compute_total_kinetic_energy(self.mobile_entities)
            momentum_drift = np.linalg.norm(current_momentum - self.initial_momentum)
            energy_drift = abs(current_energy - self.initial_energy)

            print(f"Tick {tick}/{self.config.simulation.num_ticks}")
            print(f"  Field: L_max={stats['L_max']:.2f}, gamma_max={stats['gamma_max']:.2f}")
            print(f"  Closest entity: r={distances[closest_idx]:.1f}, v={closest.speed:.3f}c, "
                  f"gamma_eff={closest.gamma_eff_measured:.2f}")
            print(f"  Collisions: {num_collisions} detected, {num_resolved} resolved")
            print(f"  Conservation: dp={momentum_drift:.2e}, dE={energy_drift:.2e}")

    def _save_snapshot(self, tick: int):
        """Save current state snapshot with collision data."""
        field_stats = self.fields.get_statistics()

        entity_states = [
            entity.get_state_summary()
            for entity in self.mobile_entities
        ]

        orbital_stats = [
            compute_orbital_parameters(entity, self.config.entities.planet_center)
            for entity in self.mobile_entities
        ]

        # NEW: Collision statistics
        collision_stats = {
            'total_detected': len(self.collision_detector.collision_history),
            'total_resolved': self.collision_resolver.total_collisions_resolved,
            'momentum': compute_total_momentum(self.mobile_entities).tolist(),
            'kinetic_energy': compute_total_kinetic_energy(self.mobile_entities)
        }

        snapshot = SimulationState(
            tick=tick,
            field_stats=field_stats,
            entity_states=entity_states,
            orbital_stats=orbital_stats,
            collision_stats=collision_stats
        )

        self.snapshots.append(snapshot)

    def analyze_c_ring(self) -> Dict:
        """
        Analyze if c-speed ring survived with collisions.

        Compare with v11 iteration 3 baseline:
        - Ring radius: r ≈ 10.1
        - Ring thickness: single-entity thin
        - Orbital speeds: v ≈ c
        - Stability: persistent over 5000 ticks
        """
        if not self.snapshots:
            return {'status': 'no_data'}

        final_snapshot = self.snapshots[-1]

        # Find entities near c-speed (v > 0.9c)
        c_speed_entities = []
        for i, (entity_state, orbital_params) in enumerate(
            zip(final_snapshot.entity_states, final_snapshot.orbital_stats)
        ):
            speed = entity_state['speed']
            r_mean = orbital_params.get('r_mean', 0)

            if speed > 0.9:  # Near c-speed
                c_speed_entities.append({
                    'index': i,
                    'id': entity_state['id'],
                    'speed': speed,
                    'radius': r_mean,
                    'orbit_type': orbital_params.get('orbit_type', 'unknown')
                })

        # Check if c-ring exists (entities at r ≈ 10.1 with v ≈ c)
        c_ring_candidates = [
            e for e in c_speed_entities
            if 9.5 < e['radius'] < 11.5  # Within 1.0 of expected r = 10.1
        ]

        c_ring_exists = len(c_ring_candidates) > 0

        # Compute ring statistics if it exists
        if c_ring_exists:
            ring_radii = [e['radius'] for e in c_ring_candidates]
            ring_speeds = [e['speed'] for e in c_ring_candidates]

            ring_stats = {
                'count': len(c_ring_candidates),
                'radius_mean': np.mean(ring_radii),
                'radius_std': np.std(ring_radii),
                'speed_mean': np.mean(ring_speeds),
                'speed_std': np.std(ring_speeds)
            }
        else:
            ring_stats = None

        # Overall collision statistics
        total_collisions = final_snapshot.collision_stats['total_detected']
        total_resolved = final_snapshot.collision_stats['total_resolved']

        results = {
            'c_ring_exists': c_ring_exists,
            'c_ring_count': len(c_ring_candidates),
            'c_ring_stats': ring_stats,
            'c_ring_entities': c_ring_candidates,
            'total_c_speed_entities': len(c_speed_entities),
            'total_collisions': total_collisions,
            'total_resolved': total_resolved,
            'final_momentum': final_snapshot.collision_stats['momentum'],
            'final_energy': final_snapshot.collision_stats['kinetic_energy']
        }

        return results

    def print_results(self):
        """Print human-readable results comparing with v11."""
        analysis = self.analyze_c_ring()

        print("=" * 70)
        print("EXPERIMENT 52 V12 RESULTS - C-RING COLLISION VALIDATION")
        print("=" * 70)
        print()

        print("Critical Question: Does c-ring survive with collision physics?")
        print()

        # Collision summary
        print(f"Collision Statistics:")
        print(f"  Total collisions detected: {analysis['total_collisions']}")
        print(f"  Total collisions resolved: {analysis['total_resolved']}")
        print()

        # Conservation summary
        print("Conservation Laws:")
        final_momentum = np.array(analysis['final_momentum'])
        momentum_drift = np.linalg.norm(final_momentum - self.initial_momentum)
        energy_drift = abs(analysis['final_energy'] - self.initial_energy)

        print(f"  Initial momentum: {np.linalg.norm(self.initial_momentum):.6f}")
        print(f"  Final momentum:   {np.linalg.norm(final_momentum):.6f}")
        print(f"  Momentum drift:   {momentum_drift:.2e}")
        print(f"  Initial energy:   {self.initial_energy:.6f}")
        print(f"  Final energy:     {analysis['final_energy']:.6f}")
        print(f"  Energy drift:     {energy_drift:.2e}")
        print()

        # C-ring analysis
        print(f"C-Speed Entities (v > 0.9c): {analysis['total_c_speed_entities']}")

        if analysis['c_ring_exists']:
            stats = analysis['c_ring_stats']
            print()
            print("[SUCCESS] C-RING SURVIVED WITH COLLISIONS!")
            print(f"  Ring entity count: {stats['count']}")
            print(f"  Ring radius: {stats['radius_mean']:.2f} ± {stats['radius_std']:.2f}")
            print(f"  Ring speed:  {stats['speed_mean']:.3f}c ± {stats['speed_std']:.3f}c")
            print()
            print("Comparison with V11 Iteration 3 (ghost particles):")
            print("  V11 ring radius: r ≈ 10.1")
            print(f"  V12 ring radius: r ≈ {stats['radius_mean']:.1f}")
            print("  V11 ring speed:  v ≈ 1.0c")
            print(f"  V12 ring speed:  v ≈ {stats['speed_mean']:.2f}c")
            print()
            print("INTERPRETATION: Stable c-ring is NOT a ghost particle artifact!")
            print("This is a DISTINCTIVE TICK-FRAME PREDICTION (different from GR).")
        else:
            print()
            print("[FAILURE] C-RING DISPERSED WITH COLLISIONS")
            print("  No entities found at r ≈ 10.1 with v ≈ c")
            print()
            print("INTERPRETATION: V11 c-ring was ghost particle artifact.")
            print("Need full collision framework (Experiment 55) for realistic black holes.")

        print()


def main():
    """Run experiment with baseline configuration."""
    import sys

    config_name = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    allow_divergence = "--divergence" in sys.argv

    # Parse mass multiplier from command line
    mass_multiplier = 100  # Default (same as v11 iteration 3)
    for arg in sys.argv:
        if arg.startswith("--mass="):
            mass_multiplier = int(arg.split("=")[1])

    try:
        config = get_config(config_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(config.summary())
    print()

    if allow_divergence:
        print("*** DIVERGENCE MODE ENABLED ***")
        print("Allowing gamma -> infinity (black hole test)")
        print()

    print(f"*** MASS MULTIPLIER: {mass_multiplier}x ***")
    print(f"Planet entities: {700 * mass_multiplier}")
    print()

    # Create and run experiment with specified mass multiplier
    experiment = Experiment52V12(config, mass_multiplier=mass_multiplier, allow_divergence=allow_divergence)
    experiment.run()
    experiment.print_results()


if __name__ == "__main__":
    main()
