"""
Parameter Tuning Experiment for V6

Tests different jitter strengths and gamma modulation values.
Goal: Find parameters that confine patterns without dissolution.

Author: V6 Grid-Based Implementation
Date: 2026-01-24
"""

import time
import math
import json
from config_v6 import get_tuning_configs
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution


def initialize_gamma_field(grid: PlanckGrid, k: float):
    """
    Initialize radial gamma field: gamma(r) = 1 + k/r^2

    Args:
        grid: PlanckGrid to initialize
        k: Field strength
    """
    center_x = grid.width // 2
    center_y = grid.height // 2

    for y in range(grid.height):
        for x in range(grid.width):
            dx = x - center_x
            dy = y - center_y
            r_squared = dx*dx + dy*dy

            if r_squared < 1:
                gamma_val = 2.0
            else:
                gamma_val = 1.0 + k / r_squared

            gamma_clamped = min(2.0, max(1.0, gamma_val))
            grid.set_gamma(x, y, gamma_clamped)


def initialize_patterns(grid: PlanckGrid, library: PatternLibrary, config):
    """
    Initialize n_patterns monopole patterns at random positions.

    Args:
        grid: PlanckGrid to place patterns on
        library: PatternLibrary containing patterns
        config: Configuration with pattern parameters

    Returns:
        List of PatternInstance objects
    """
    import numpy as np

    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    for i in range(config.n_patterns):
        # Random radius (Gaussian)
        r = rng.normal(config.pattern_init_radius_mean, config.pattern_init_radius_std)
        r = max(config.pattern_size, r)  # At least one pattern size away from center

        # Random angle
        theta = rng.uniform(0, 2 * math.pi)

        # Position in Planck cells
        px = int(center_x + r * math.cos(theta))
        py = int(center_y + r * math.sin(theta))

        # Clamp to grid bounds
        px = max(0, min(grid.width - config.pattern_size, px))
        py = max(0, min(grid.height - config.pattern_size, py))

        # Create sample cell and pattern instance
        sample = SampleCell(px, py, size=config.pattern_size)
        instance = PatternInstance(sample, "monopole", instance_id=f"pattern_{i}")

        # Write pattern to grid
        instance.write_to_grid(grid, library)

        patterns.append(instance)

    return patterns


def compute_pattern_statistics(patterns: list[PatternInstance], grid: PlanckGrid):
    """
    Compute cloud radius statistics from pattern positions.

    Args:
        patterns: List of PatternInstance
        grid: PlanckGrid (for center reference)

    Returns:
        Dict with radius statistics
    """
    center_x = grid.width // 2
    center_y = grid.height // 2

    radii = []
    for pattern in patterns:
        dx = pattern.sample.center_x - center_x
        dy = pattern.sample.center_y - center_y
        r = math.sqrt(dx*dx + dy*dy)
        radii.append(r)

    if not radii:
        return {
            "r_mean": 0.0,
            "r_std": 0.0,
            "r_min": 0.0,
            "r_max": 0.0,
        }

    import numpy as np
    radii_arr = np.array(radii)

    return {
        "r_mean": float(np.mean(radii_arr)),
        "r_std": float(np.std(radii_arr)),
        "r_min": float(np.min(radii_arr)),
        "r_max": float(np.max(radii_arr)),
    }


def run_tuning_experiment(config_name: str, config):
    """Run single tuning experiment with given configuration."""

    print(f"\n{'='*70}")
    print(f"Configuration: {config_name}")
    print(f"{'='*70}")
    print(f"Jitter strength: {config.jitter_strength:.3f}")
    print(f"Gamma modulation: {config.gamma_modulation_strength:.1f}")
    print(f"Gamma field k: {config.gamma_field_k:.1f}")
    print(f"Ticks: {config.num_ticks:,}")
    print()

    # Create grid
    grid = PlanckGrid(config.grid_width, config.grid_height)

    # Initialize gamma field
    print("Initializing gamma field...")
    initialize_gamma_field(grid, config.gamma_field_k)

    # Create pattern library
    library = PatternLibrary(pattern_size=config.pattern_size)

    # Initialize patterns
    print(f"Initializing {config.n_patterns} patterns...")
    patterns = initialize_patterns(grid, library, config)

    # Initial statistics
    stats_initial = compute_pattern_statistics(patterns, grid)
    field_stats_initial = grid.get_field_statistics()

    print(f"Initial pattern distribution:")
    print(f"  Mean radius: {stats_initial['r_mean']:.2f} Planck cells")
    print(f"  Std radius: {stats_initial['r_std']:.2f}")
    print(f"  Range: [{stats_initial['r_min']:.2f}, {stats_initial['r_max']:.2f}]")
    print(f"  Field energy: {field_stats_initial['total_energy']}")
    print()

    # Create jitter and evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(grid, jitter, gamma_modulation_strength=config.gamma_modulation_strength)

    # Run evolution
    print(f"Evolving for {config.num_ticks:,} ticks...")
    print()

    start_time = time.time()
    history = []

    for tick in range(config.num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % config.progress_interval == 0:
            stats = compute_pattern_statistics(patterns, grid)
            field_stats = grid.get_field_statistics()

            record = {
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "field_energy": field_stats["total_energy"],
                "nonzero_fraction": field_stats["nonzero_fraction"],
            }
            history.append(record)

            print(f"[{tick+1:6d}/{config.num_ticks:6d}] "
                  f"r_mean={stats['r_mean']:6.2f}, "
                  f"energy={field_stats['total_energy']:5d}, "
                  f"nonzero={field_stats['nonzero_fraction']*100:5.1f}%")

    elapsed = time.time() - start_time

    # Final statistics
    stats_final = compute_pattern_statistics(patterns, grid)
    field_stats_final = grid.get_field_statistics()

    print()
    print(f"{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Initial r_mean: {stats_initial['r_mean']:.2f}")
    print(f"Final r_mean: {stats_final['r_mean']:.2f}")

    drift_percent = abs(stats_final['r_mean'] - stats_initial['r_mean']) / stats_initial['r_mean'] * 100
    print(f"Drift: {drift_percent:.2f}%")
    print()

    print(f"Initial field energy: {field_stats_initial['total_energy']}")
    print(f"Final field energy: {field_stats_final['total_energy']}")
    print()

    print(f"Performance: {config.num_ticks / elapsed:.1f} ticks/sec")
    print(f"{'='*70}")

    # Return summary
    return {
        "config_name": config_name,
        "jitter_strength": config.jitter_strength,
        "gamma_modulation_strength": config.gamma_modulation_strength,
        "gamma_field_k": config.gamma_field_k,
        "initial_r_mean": stats_initial["r_mean"],
        "final_r_mean": stats_final["r_mean"],
        "drift_percent": drift_percent,
        "initial_energy": field_stats_initial["total_energy"],
        "final_energy": field_stats_final["total_energy"],
        "ticks_per_sec": config.num_ticks / elapsed,
        "history": history,
    }


def main():
    """Run all tuning experiments."""

    print("V6 Parameter Tuning Experiments")
    print("=" * 70)
    print()

    configs = get_tuning_configs()
    results = []

    for config_name, config in configs.items():
        result = run_tuning_experiment(config_name, config)
        results.append(result)

    # Summary comparison
    print()
    print()
    print("=" * 70)
    print("SUMMARY COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Config':<30} {'Jitter':>8} {'Gamma':>7} {'Drift %':>10} {'Final Energy':>15}")
    print("-" * 70)

    for result in results:
        print(f"{result['config_name']:<30} "
              f"{result['jitter_strength']:>8.3f} "
              f"{result['gamma_modulation_strength']:>7.1f} "
              f"{result['drift_percent']:>10.2f} "
              f"{result['final_energy']:>15,}")

    print()

    # Find best configuration (lowest drift)
    best = min(results, key=lambda r: r["drift_percent"])
    print(f"Best configuration (lowest drift): {best['config_name']}")
    print(f"  Drift: {best['drift_percent']:.2f}%")
    print(f"  Jitter: {best['jitter_strength']:.3f}")
    print(f"  Gamma modulation: {best['gamma_modulation_strength']:.1f}")
    print()

    # Save results
    with open("results/tuning_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Results saved to results/tuning_results.json")
    print("=" * 70)


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
