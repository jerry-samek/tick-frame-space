"""
V7 Experiment: Motion Dynamics

Combined experiment that runs all motion tracking analyses:
- Velocity tracking
- MSD (Mean Squared Displacement) analysis
- Orbital motion detection
- Pattern identity tracking

Uses V6 optimal configuration (jitter=0.119, hybrid_strong).
"""

import sys
import os
import time
import json
import math
from pathlib import Path

# Add v6 to path
v6_path = Path(__file__).parent.parent / "v6"
sys.path.insert(0, str(v6_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import (
    track_pattern_positions,
    save_initial_pattern_positions,
    compute_field_center_of_mass,
)

# V7 modules
from config_v7 import MotionConfig, QuickTestConfig
from velocity_tracker import VelocityTracker
from motion_history import MotionHistory
from orbital_analyzer import OrbitalAnalyzer
from pattern_identity import PatternIdentityTracker


def initialize_gamma_field(grid: PlanckGrid, k: float):
    """Initialize radial gamma field: gamma(r) = 1 + k/r^2"""
    center_x = grid.width // 2
    center_y = grid.height // 2

    for y in range(grid.height):
        for x in range(grid.width):
            dx = x - center_x
            dy = y - center_y
            r_squared = dx * dx + dy * dy

            if r_squared < 1:
                gamma_val = 2.0
            else:
                gamma_val = 1.0 + k / r_squared

            gamma_clamped = min(2.0, max(1.0, gamma_val))
            grid.set_gamma(x, y, gamma_clamped)


def initialize_patterns(grid: PlanckGrid, library: PatternLibrary, config):
    """Initialize patterns at random positions around grid center."""
    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    for i in range(config.n_patterns):
        r = rng.normal(config.pattern_init_radius_mean, config.pattern_init_radius_std)
        r = max(config.pattern_size, r)
        theta = rng.uniform(0, 2 * math.pi)

        px = int(center_x + r * math.cos(theta))
        py = int(center_y + r * math.sin(theta))

        px = max(0, min(grid.width - config.pattern_size, px))
        py = max(0, min(grid.height - config.pattern_size, py))

        sample = SampleCell(px, py, size=config.pattern_size)
        instance = PatternInstance(sample, "monopole", instance_id=f"pattern_{i}")
        instance.write_to_grid(grid, library)

        patterns.append(instance)

    return patterns


def run_experiment(config, verbose: bool = True):
    """
    Run the full motion dynamics experiment.

    Args:
        config: Configuration object
        verbose: Print progress

    Returns:
        Dict with all results
    """
    if verbose:
        print("=" * 70)
        print("V7 Motion Dynamics Experiment")
        print("=" * 70)
        print()
        print(f"Configuration: {type(config).__name__}")
        print(f"  Grid: {config.grid_width}x{config.grid_height}")
        print(f"  Patterns: {config.n_patterns}")
        print(f"  Jitter: {config.jitter_strength}")
        print(f"  Ticks: {config.num_ticks:,}")
        print()

    # Initialize grid
    if verbose:
        print("Initializing grid and gamma field...")
    grid = PlanckGrid(config.grid_width, config.grid_height)
    initialize_gamma_field(grid, config.gamma_field_k)

    library = PatternLibrary(pattern_size=config.pattern_size)

    if verbose:
        print(f"Initializing {config.n_patterns} patterns...")
    patterns = initialize_patterns(grid, library, config)

    # Get grid center
    center = (grid.width // 2, grid.height // 2)

    # Initialize trackers
    velocity_tracker = VelocityTracker(
        n_patterns=config.n_patterns,
        window_size=config.velocity_window
    )
    motion_history = MotionHistory(
        n_patterns=config.n_patterns,
        max_length=config.max_trajectory_length
    )
    orbital_analyzer = OrbitalAnalyzer(
        n_patterns=config.n_patterns,
        center=center,
        window_size=config.angular_velocity_window
    )
    identity_tracker = PatternIdentityTracker(
        n_patterns=config.n_patterns,
        dissolution_threshold=config.dissolution_threshold,
        reformation_threshold=config.reformation_threshold,
        coherence_radius=config.coherence_radius
    )

    # Record initial positions and set reference energies
    initial_positions = save_initial_pattern_positions(patterns)
    for i, pattern in enumerate(patterns):
        cx = pattern.sample.center_x
        cy = pattern.sample.center_y
        energy = identity_tracker.compute_local_energy(grid, cx, cy)
        identity_tracker.set_reference_energy(i, energy)

    # Create jitter and evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    # History for periodic snapshots
    history = []
    start_time = time.time()

    if verbose:
        print()
        print(f"Running {config.num_ticks:,} ticks...")
        print()

    for tick in range(config.num_ticks):
        # Evolve one tick
        evolution.evolve_one_tick()

        # Track positions at sample interval
        if tick % config.position_sample_interval == 0:
            # Update pattern positions from field COM
            track_pattern_positions(grid, patterns, search_radius=15)

            # Record for all trackers
            for i, pattern in enumerate(patterns):
                cx = float(pattern.sample.center_x)
                cy = float(pattern.sample.center_y)

                velocity_tracker.record_position(i, cx, cy, tick)
                motion_history.record(i, cx, cy, tick)
                orbital_analyzer.record_position(i, cx, cy, tick)
                identity_tracker.update(i, grid, int(cx), int(cy), tick)

        # Progress report
        if verbose and (tick + 1) % config.progress_interval == 0:
            velocity_tracker.update_all_velocities()
            orbital_analyzer.update_all_states()

            vel_stats = velocity_tracker.get_velocity_statistics()
            orbital_stats = orbital_analyzer.get_statistics()
            identity_stats = identity_tracker.get_statistics()

            elapsed = time.time() - start_time
            ticks_per_sec = (tick + 1) / elapsed

            print(f"[{tick+1:6d}/{config.num_ticks:6d}] "
                  f"speed={vel_stats['mean_speed']:.4f}, "
                  f"omega={orbital_stats['mean_omega']:.6f}, "
                  f"alive={identity_stats['alive_count']}/{config.n_patterns}, "
                  f"({ticks_per_sec:.1f} t/s)")

            # Store snapshot
            history.append({
                "tick": tick + 1,
                "velocity": vel_stats,
                "orbital": orbital_stats,
                "identity": identity_stats,
            })

    elapsed = time.time() - start_time

    # Final analysis
    if verbose:
        print()
        print("=" * 70)
        print("FINAL ANALYSIS")
        print("=" * 70)
        print()

    # Update all trackers one last time
    velocity_tracker.update_all_velocities()
    orbital_analyzer.update_all_states()

    # MSD analysis
    msd_result = motion_history.analyze_msd(max_lag=config.msd_max_lag)

    # Get final statistics
    vel_final = velocity_tracker.get_velocity_statistics()
    orbital_final = orbital_analyzer.get_statistics()
    identity_final = identity_tracker.get_statistics()
    motion_stats = motion_history.get_statistics()

    if verbose:
        print("VELOCITY ANALYSIS:")
        print(f"  Mean speed: {vel_final['mean_speed']:.6f} cells/tick")
        print(f"  Speed std: {vel_final['std_speed']:.6f}")
        print(f"  Max speed: {vel_final['max_speed']:.6f}")
        print()

        print("MSD ANALYSIS:")
        print(f"  Alpha (scaling exponent): {msd_result.alpha:.3f}")
        print(f"  Diffusion coefficient: {msd_result.diffusion_coefficient:.6f}")
        print(f"  Fit R-squared: {msd_result.r_squared:.3f}")
        print(f"  Interpretation: {msd_result.interpret_alpha()}")
        print()

        print("ORBITAL ANALYSIS:")
        print(f"  Mean angular velocity: {orbital_final['mean_omega']:.6f} rad/tick")
        print(f"  Rotation coherence: {orbital_final['rotation_coherence']:.3f}")
        print(f"  Mean orbital period: {orbital_final['mean_period']:.1f} ticks")
        print(f"  omega(r) exponent beta: {orbital_final['omega_r_beta']:.3f}")
        print()

        print("PATTERN IDENTITY:")
        print(f"  Alive patterns: {identity_final['alive_count']}/{config.n_patterns}")
        print(f"  Mean lifetime fraction: {identity_final['mean_lifetime_fraction']:.3f}")
        print(f"  Total dissolutions: {identity_final['total_dissolutions']}")
        print(f"  Total reformations: {identity_final['total_reformations']}")
        print(f"  Mean coherence: {identity_final['mean_coherence']:.3f}")
        print()

        print("TRAJECTORY STATISTICS:")
        print(f"  Mean displacement: {motion_stats['mean_displacement']:.3f} cells")
        print(f"  Max displacement: {motion_stats['max_displacement']:.3f} cells")
        print()

        print(f"Performance: {config.num_ticks / elapsed:.1f} ticks/sec")
        print(f"Total time: {elapsed:.1f} seconds")
        print("=" * 70)

    # Compile results
    results = {
        "config": {
            "name": type(config).__name__,
            "num_ticks": config.num_ticks,
            "n_patterns": config.n_patterns,
            "jitter_strength": config.jitter_strength,
            "grid_size": config.grid_width,
        },
        "velocity": vel_final,
        "msd": {
            "alpha": msd_result.alpha,
            "diffusion_coefficient": msd_result.diffusion_coefficient,
            "r_squared": msd_result.r_squared,
            "interpretation": msd_result.interpret_alpha(),
        },
        "orbital": orbital_final,
        "identity": identity_final,
        "trajectory": motion_stats,
        "performance": {
            "ticks_per_sec": config.num_ticks / elapsed,
            "elapsed_seconds": elapsed,
        },
        "history": history,
    }

    return results


def main():
    """Run experiment with default configuration."""
    # Use quick test for demo, full config for real experiments
    import argparse

    parser = argparse.ArgumentParser(description="V7 Motion Dynamics Experiment")
    parser.add_argument("--quick", action="store_true", help="Run quick test (1k ticks)")
    parser.add_argument("--output", type=str, default="results/motion_dynamics.json",
                        help="Output file path")
    args = parser.parse_args()

    config = QuickTestConfig() if args.quick else MotionConfig()

    results = run_experiment(config, verbose=True)

    # Save results
    os.makedirs("results", exist_ok=True)
    with open(args.output, "w") as f:
        # Convert numpy arrays to lists for JSON serialization
        def convert(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            if isinstance(obj, np.floating):
                return float(obj)
            if isinstance(obj, np.integer):
                return int(obj)
            return obj

        json.dump(results, f, indent=2, default=convert)

    print()
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
