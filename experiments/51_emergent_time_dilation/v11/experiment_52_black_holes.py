#!/usr/bin/env python3
"""
Experiment 52 (V11): Black Hole Event Horizons from Load Saturation

CRITICAL TEST: Do event horizons form naturally at extreme load saturation,
with no singularities inside (substrate continues updating)?

Based on v10 validated gradient-following physics, but with 10× mass.
Tests if natural horizon radius emerges at r_s ≈ 2GM/c².
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


@dataclass
class SimulationState:
    """Complete state of simulation at one moment."""
    tick: int
    field_stats: dict
    entity_states: List[dict]
    orbital_stats: List[dict]


class Experiment52:
    """
    Test if black hole event horizons emerge naturally.

    V11 KEY FEATURES:
    - 10× planet mass (7,000 entities)
    - 10× field source strength (scale = 7.5)
    - Test entities at various distances (r = 10-60)
    - Look for critical r_horizon where γ → ∞
    - Validate: stationary entities collapse inside horizon
    """

    def __init__(self, config: ConfigurationSet, mass_multiplier: int = 10, allow_divergence: bool = False):
        self.config = config
        self.mass_multiplier = mass_multiplier
        self.allow_divergence = allow_divergence

        # Initialize field dynamics with STRONGER source
        self.fields = FieldDynamics(
            grid_size=config.simulation.grid_size,
            alpha=config.field.alpha,
            gamma=config.field.gamma_damp,
            scale=config.field.scale * mass_multiplier,  # 10× stronger source!
            R=config.field.R,
            D=config.field.D,
            E_max=config.field.E_max,
            capacity_min=config.field.capacity_min,
            work_threshold=config.field.work_threshold,
            allow_divergence=allow_divergence  # Allow gamma → ∞ for black holes!
        )

        # Gradient following parameter (same as v10)
        self.gradient_coupling = 0.01

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

        # MASSIVE planet cluster (10× more entities)
        planet_count = cfg.entities.planet_count * self.mass_multiplier
        self.planet_entities = generate_planet_cluster(
            center=cfg.entities.planet_center,
            radius=cfg.entities.planet_radius,
            count=planet_count,
            tick_budget=cfg.entities.planet_tick_budget,
            energy=cfg.field.E_max * 0.67
        )
        print(f"  Planet: {len(self.planet_entities)} entities (BLACK HOLE CANDIDATE)")

        # Test entities at VARIOUS DISTANCES to find horizon
        # Expected horizon radius: r_s ≈ 2GM/c² (need to validate empirically)
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
        print(f"    Velocities: {test_velocities} (including stationary!)")
        print(f"    Gradient coupling: {self.gradient_coupling}")
        print()

        # Combined list for field computation
        self.all_entities = self.planet_entities + self.mobile_entities

    def step(self):
        """Execute one simulation timestep with gradient following."""
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

    def run(self):
        """Run full simulation."""
        cfg = self.config
        num_ticks = cfg.simulation.num_ticks
        snapshot_interval = cfg.simulation.snapshot_interval
        verbose = cfg.simulation.verbose

        print("=" * 70)
        print(f"EXPERIMENT 52 (V11) - {cfg.name}")
        print("=" * 70)
        print()
        print(f"Testing: BLACK HOLE EVENT HORIZON formation")
        print(f"Planet mass: {self.mass_multiplier}× baseline (SUPERMASSIVE)")
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

        # Sample closest entity
        if len(self.mobile_entities) > 0:
            # Find entity closest to planet
            distances = [
                np.linalg.norm(e.position - np.array(self.config.entities.planet_center))
                for e in self.mobile_entities
            ]
            closest_idx = np.argmin(distances)
            closest = self.mobile_entities[closest_idx]

            print(f"Tick {tick}/{self.config.simulation.num_ticks}")
            print(f"  Field: L_max={stats['L_max']:.2f}, gamma_max={stats['gamma_max']:.2f}")
            print(f"  Closest entity: r={distances[closest_idx]:.1f}, v={closest.speed:.3f}c, "
                  f"gamma_eff={closest.gamma_eff_measured:.2f}")

    def _save_snapshot(self, tick: int):
        """Save current state snapshot."""
        field_stats = self.fields.get_statistics()

        entity_states = [
            entity.get_state_summary()
            for entity in self.mobile_entities
        ]

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

    def analyze_horizon(self) -> Dict:
        """
        Analyze if event horizon formed.

        Looks for critical radius where:
        - Entities inside collapse (distance decreasing rapidly)
        - Entities outside orbit or escape
        - γ_grav shows sharp increase (saturation)
        """
        if not self.snapshots:
            return {'status': 'no_data'}

        final_snapshot = self.snapshots[-1]

        # Categorize entities by distance and fate
        collapsed = []
        orbiting = []
        escaping = []

        for i, (entity_state, orbital_params) in enumerate(
            zip(final_snapshot.entity_states, final_snapshot.orbital_stats)
        ):
            orbit_type = orbital_params.get('orbit_type', 'unknown')
            r_mean = orbital_params.get('r_mean', 0)

            if orbit_type == 'collapsing':
                collapsed.append((i, r_mean, entity_state))
            elif orbit_type in ['circular', 'elliptical']:
                orbiting.append((i, r_mean, entity_state))
            elif orbit_type == 'escaping':
                escaping.append((i, r_mean, entity_state))

        # Find horizon radius (boundary between collapse and orbit)
        if collapsed and orbiting:
            max_collapse_r = max(r for _, r, _ in collapsed)
            min_orbit_r = min(r for _, r, _ in orbiting)
            r_horizon_estimate = (max_collapse_r + min_orbit_r) / 2
            horizon_found = True
        else:
            r_horizon_estimate = None
            horizon_found = False

        # Gamma analysis at various radii
        gamma_profile = []
        for r in [10, 15, 20, 25, 30, 35, 40, 50, 60]:
            pos = (
                self.config.entities.planet_center[0] + r,
                self.config.entities.planet_center[1]
            )
            gamma = self.fields.get_gamma_at_position(pos)
            gamma_profile.append((r, gamma))

        results = {
            'horizon_found': horizon_found,
            'r_horizon_estimate': r_horizon_estimate,
            'total_entities': len(final_snapshot.entity_states),
            'collapsed': len(collapsed),
            'orbiting': len(orbiting),
            'escaping': len(escaping),
            'collapsed_details': collapsed,
            'orbiting_details': orbiting,
            'gamma_profile': gamma_profile
        }

        return results

    def print_results(self):
        """Print human-readable results."""
        analysis = self.analyze_horizon()

        print("=" * 70)
        print("EXPERIMENT 52 RESULTS - BLACK HOLE HORIZON TEST")
        print("=" * 70)
        print()

        print("Question: Do event horizons form naturally at extreme mass?")
        print()

        print(f"Total test entities: {analysis['total_entities']}")
        print(f"  Collapsed (inside horizon): {analysis['collapsed']}")
        print(f"  Orbiting (outside horizon): {analysis['orbiting']}")
        print(f"  Escaping: {analysis['escaping']}")
        print()

        if analysis['horizon_found']:
            print("[SUCCESS] Event horizon DETECTED!")
            print(f"   Estimated radius: r_horizon ≈ {analysis['r_horizon_estimate']:.1f}")
            print()
            print("Gamma Profile (time dilation vs distance):")
            for r, gamma in analysis['gamma_profile']:
                marker = " <-- HORIZON?" if abs(r - analysis['r_horizon_estimate']) < 5 else ""
                print(f"   r={r:2.0f}: gamma={gamma:6.2f}{marker}")
        else:
            print("[INCONCLUSIVE] No clear horizon boundary detected")
            print("   Either all entities collapsed or all orbited")
            print()
            print("Gamma Profile (time dilation vs distance):")
            for r, gamma in analysis['gamma_profile']:
                print(f"   r={r:2.0f}: gamma={gamma:6.2f}")

        print()

        # Detail collapsed entities
        if analysis['collapsed']:
            print("Collapsed Entity Details (INSIDE HORIZON):")
            for idx, r_mean, entity_state in analysis['collapsed_details'][:5]:
                print(f"  Entity {entity_state['id']}:")
                print(f"    Final distance: {r_mean:.1f}")
                print(f"    Final velocity: {entity_state['speed']:.3f}c")
                print(f"    Gamma_eff: {entity_state['gamma_eff_measured']:.2f}")

        # Detail orbiting entities
        if analysis['orbiting']:
            print()
            print("Orbiting Entity Details (OUTSIDE HORIZON):")
            for idx, r_mean, entity_state in analysis['orbiting_details'][:5]:
                print(f"  Entity {entity_state['id']}:")
                print(f"    Orbital distance: {r_mean:.1f}")
                print(f"    Orbital velocity: {entity_state['speed']:.3f}c")

        print()


def main():
    """Run experiment with baseline configuration."""
    import sys

    config_name = sys.argv[1] if len(sys.argv) > 1 else "baseline"
    allow_divergence = "--divergence" in sys.argv

    # Parse mass multiplier from command line
    mass_multiplier = 10  # Default
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
    experiment = Experiment52(config, mass_multiplier=mass_multiplier, allow_divergence=allow_divergence)
    experiment.run()
    experiment.print_results()


if __name__ == "__main__":
    main()
