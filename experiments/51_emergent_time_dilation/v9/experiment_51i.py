#!/usr/bin/env python3
"""
Experiment 51i (V9): Multi-Entity Gravitational-Relativistic Time Dilation

Main simulation integrating moving entities with dynamic field evolution.
"""

import numpy as np
from typing import List, Dict
import time
from dataclasses import dataclass

from config import ConfigurationSet, get_config
from entity_motion import MovingEntity, StationaryEntity, generate_planet_cluster, generate_mobile_entities
from field_dynamics import FieldDynamics


@dataclass
class SimulationState:
    """Complete state of simulation at one moment."""
    tick: int
    field_stats: dict
    entity_states: List[dict]


class Experiment51i:
    """
    Main experiment orchestrating entities and fields.
    """

    def __init__(self, config: ConfigurationSet):
        self.config = config

        # Initialize field dynamics
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

        # Planet cluster (stationary)
        self.planet_entities = generate_planet_cluster(
            center=cfg.entities.planet_center,
            radius=cfg.entities.planet_radius,
            count=cfg.entities.planet_count,
            tick_budget=cfg.entities.planet_tick_budget,
            energy=cfg.field.E_max * 0.67
        )
        print(f"  Planet: {len(self.planet_entities)} entities")

        # Mobile entities at various velocities
        velocities = [
            cfg.entities.v_slow,
            cfg.entities.v_moderate,
            cfg.entities.v_fast,
            cfg.entities.v_ultra
        ]

        self.mobile_entities = generate_mobile_entities(
            center=cfg.entities.planet_center,
            distances=cfg.entities.mobile_distances,
            velocities_per_distance=velocities,
            count_per_velocity=cfg.entities.mobile_count_per_velocity,
            c=cfg.simulation.c
        )
        print(f"  Mobile: {len(self.mobile_entities)} entities")
        print(f"    Velocities: {velocities}")
        print()

        # Combined list for field computation
        self.all_entities = self.planet_entities + self.mobile_entities

    def step(self):
        """Execute one simulation timestep."""
        dt = self.config.simulation.dt
        grid_size = self.config.simulation.grid_size

        # 1. Update fields based on current entity positions
        self.fields.step(self.all_entities, dt=dt)

        # 2. Update each mobile entity
        for entity in self.mobile_entities:
            # Get local gravitational time dilation
            gamma_grav = self.fields.get_gamma_at_position(tuple(entity.position))

            # Update entity's proper time
            entity.update_time(gamma_grav, dt_substrate=dt)

            # Update entity's position
            entity.update_position(dt=dt, grid_size=grid_size, wrap_boundaries=True)

    def run(self):
        """Run full simulation."""
        cfg = self.config
        num_ticks = cfg.simulation.num_ticks
        snapshot_interval = cfg.simulation.snapshot_interval
        verbose = cfg.simulation.verbose

        print("=" * 70)
        print(f"EXPERIMENT 51i (V9) - {cfg.name}")
        print("=" * 70)
        print()
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
        sample_entity = self.mobile_entities[0]

        print(f"Tick {tick}/{self.config.simulation.num_ticks}")
        print(f"  Field: L_max={stats['L_max']:.2f}, E_min={stats['E_min']:.2f}, gamma_max={stats['gamma_max']:.2f}")
        print(f"  Sample entity: tau={sample_entity.proper_time:.1f}, gamma_eff={sample_entity.gamma_eff_measured:.3f}")

    def _save_snapshot(self, tick: int):
        """Save current state snapshot."""
        field_stats = self.fields.get_statistics()

        entity_states = [
            entity.get_state_summary()
            for entity in self.mobile_entities
        ]

        snapshot = SimulationState(
            tick=tick,
            field_stats=field_stats,
            entity_states=entity_states
        )

        self.snapshots.append(snapshot)

    def get_results_summary(self) -> Dict:
        """Generate results summary."""
        if not self.snapshots:
            return {}

        final_snapshot = self.snapshots[-1]

        # Organize by velocity regime
        results_by_velocity = {}

        for entity_state in final_snapshot.entity_states:
            speed = entity_state['speed']

            # Bin by velocity
            if speed < 0.2:
                key = 'slow'
            elif speed < 0.7:
                key = 'moderate'
            elif speed < 0.95:
                key = 'fast'
            else:
                key = 'ultra'

            if key not in results_by_velocity:
                results_by_velocity[key] = []

            results_by_velocity[key].append(entity_state)

        # Compute statistics per velocity regime
        summary = {
            'config_name': self.config.name,
            'total_ticks': final_snapshot.tick,
            'elapsed_time': self.end_time - self.start_time if self.end_time else None,
            'final_field_stats': final_snapshot.field_stats,
            'velocity_regimes': {}
        }

        for regime, entities in results_by_velocity.items():
            gammas = [e['gamma_eff_measured'] for e in entities]
            gamma_SRs = [e['gamma_SR'] for e in entities]

            summary['velocity_regimes'][regime] = {
                'count': len(entities),
                'avg_gamma_eff': np.mean(gammas),
                'std_gamma_eff': np.std(gammas),
                'avg_gamma_SR': np.mean(gamma_SRs),
                'sample_entities': entities[:3]  # First 3 for inspection
            }

        return summary

    def print_results(self):
        """Print human-readable results."""
        summary = self.get_results_summary()

        print("=" * 70)
        print("EXPERIMENT RESULTS")
        print("=" * 70)
        print()

        print(f"Configuration: {summary['config_name']}")
        print(f"Total ticks simulated: {summary['total_ticks']}")
        print(f"Elapsed time: {summary.get('elapsed_time', 0):.1f}s")
        print()

        print("Final Field Statistics:")
        fs = summary['final_field_stats']
        print(f"  Load:   mean={fs['L_mean']:.3f}, max={fs['L_max']:.3f}")
        print(f"  Energy: mean={fs['E_mean']:.3f}, min={fs['E_min']:.3f}")
        print(f"  Gamma:  mean={fs['gamma_mean']:.3f}, max={fs['gamma_max']:.3f}, min={fs['gamma_min']:.3f}")
        print()

        print("Time Dilation by Velocity Regime:")
        print(f"{'Regime':<12} {'Count':<6} {'Avg v/c':<10} {'g_SR':<10} {'g_eff':<10} {'Status'}")
        print("-" * 70)

        for regime, data in summary['velocity_regimes'].items():
            status = "OK" if 1.0 < data['avg_gamma_eff'] < 20.0 else "WARN"
            print(f"{regime:<12} {data['count']:<6} {data['avg_gamma_SR']:.3f}      "
                  f"{data['avg_gamma_SR']:.3f}      {data['avg_gamma_eff']:.3f}      {status}")

        print()

        # Sample detailed entity
        print("Sample Entity Detail (slow regime):")
        if 'slow' in summary['velocity_regimes']:
            sample = summary['velocity_regimes']['slow']['sample_entities'][0]
            print(f"  ID: {sample['id']}")
            print(f"  Position: ({sample['position'][0]:.1f}, {sample['position'][1]:.1f})")
            print(f"  Speed: {sample['speed']:.3f}c")
            print(f"  g_SR: {sample['gamma_SR']:.3f}")
            print(f"  Proper time: {sample['proper_time']:.1f}")
            print(f"  Coordinate time: {sample['coordinate_time']}")
            print(f"  g_eff (measured): {sample['gamma_eff_measured']:.3f}")
        print()


def main():
    """Run experiment with specified configuration."""
    import sys

    # Parse config name from command line
    config_name = sys.argv[1] if len(sys.argv) > 1 else "baseline"

    # Load configuration
    try:
        config = get_config(config_name)
    except ValueError as e:
        print(f"Error: {e}")
        return

    print(config.summary())
    print()

    # Create and run experiment
    experiment = Experiment51i(config)
    experiment.run()
    experiment.print_results()


if __name__ == "__main__":
    main()
