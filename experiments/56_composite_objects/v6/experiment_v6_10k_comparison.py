"""
V6 10k Tick Validation - Configuration Comparison

Tests three field confinement configurations over 10,000 ticks:
- decay_high: Field decay only (aggressive)
- hybrid_high: Hybrid approach (aggressive creation limit)
- hybrid_strong: Hybrid approach (very aggressive both mechanisms)

Goal: Compare field coverage and pattern stability at 10k ticks.

Author: V6 Phase 4A Validation
Date: 2026-01-25
"""

import time
import math
import json
from config_v6 import (
    FieldConfinementDecayHighConfig,
    FieldConfinementHybridHighConfig,
    FieldConfinementHybridStrongConfig,
)
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


def run_10k_validation(config_name: str, config):
    """Run single 10k tick validation with given configuration."""

    print(f"\n{'='*70}")
    print(f"Configuration: {config_name}")
    print(f"{'='*70}")
    print(f"Jitter strength: {config.jitter_strength:.3f}")
    print(f"Gamma modulation: {config.gamma_modulation_strength:.1f}")
    print(f"Creation sensitivity: {config.creation_sensitivity:.1f}")
    print(f"Decay threshold: {config.field_decay_threshold:.1f}")
    print(f"Decay rate: {config.field_decay_rate:.3f}")
    print(f"Ticks: 10,000")
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
    print(f"  Field coverage: {field_stats_initial['nonzero_fraction']*100:.1f}%")
    print()

    # Create jitter and evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid,
        jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        ca_creation_threshold=config.ca_creation_threshold,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    # Run evolution
    print(f"Evolving for 10,000 ticks...")
    print()

    start_time = time.time()
    history = []
    num_ticks = 10_000
    progress_interval = 500

    for tick in range(num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % progress_interval == 0:
            stats = compute_pattern_statistics(patterns, grid)
            field_stats = grid.get_field_statistics()

            record = {
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "field_energy": field_stats["total_energy"],
                "field_coverage": field_stats["nonzero_fraction"],
            }
            history.append(record)

            print(f"[{tick+1:7d}/{num_ticks:7d}] "
                  f"r_mean={stats['r_mean']:6.2f}, "
                  f"energy={field_stats['total_energy']:6d}, "
                  f"coverage={field_stats['nonzero_fraction']*100:5.1f}%")

    elapsed = time.time() - start_time

    # Final statistics
    stats_final = compute_pattern_statistics(patterns, grid)
    field_stats_final = grid.get_field_statistics()

    print()
    print(f"{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Pattern drift:")
    print(f"  Initial r_mean: {stats_initial['r_mean']:.2f}")
    print(f"  Final r_mean: {stats_final['r_mean']:.2f}")

    drift_percent = abs(stats_final['r_mean'] - stats_initial['r_mean']) / stats_initial['r_mean'] * 100
    print(f"  Drift: {drift_percent:.2f}%")
    print()

    print(f"Field coverage:")
    print(f"  Initial: {field_stats_initial['nonzero_fraction']*100:.1f}%")
    print(f"  Final: {field_stats_final['nonzero_fraction']*100:.1f}%")
    print()

    print(f"Field energy:")
    print(f"  Initial: {field_stats_initial['total_energy']}")
    print(f"  Final: {field_stats_final['total_energy']}")
    energy_growth = field_stats_final['total_energy'] / field_stats_initial['total_energy']
    print(f"  Growth: {energy_growth:.1f}×")
    print()

    print(f"Performance: {num_ticks / elapsed:.1f} ticks/sec")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print(f"{'='*70}")

    # Return summary
    return {
        "config_name": config_name,
        "creation_sensitivity": config.creation_sensitivity,
        "decay_threshold": config.field_decay_threshold,
        "decay_rate": config.field_decay_rate,
        "initial_r_mean": stats_initial["r_mean"],
        "final_r_mean": stats_final["r_mean"],
        "drift_percent": drift_percent,
        "initial_coverage": field_stats_initial["nonzero_fraction"],
        "final_coverage": field_stats_final["nonzero_fraction"],
        "initial_energy": field_stats_initial["total_energy"],
        "final_energy": field_stats_final["total_energy"],
        "energy_growth": energy_growth,
        "ticks_per_sec": num_ticks / elapsed,
        "elapsed_minutes": elapsed / 60,
        "history": history,
    }


def main():
    """Run 10k validation for three configurations."""

    print("V6 Phase 4A: 10k Tick Validation - Configuration Comparison")
    print("=" * 70)
    print()
    print("Testing three field confinement configurations:")
    print("  1. decay_high: Field decay only (aggressive)")
    print("  2. hybrid_high: Hybrid approach (aggressive creation limit)")
    print("  3. hybrid_strong: Hybrid approach (very aggressive both mechanisms)")
    print()

    configs = {
        "decay_high": FieldConfinementDecayHighConfig(),
        "hybrid_high": FieldConfinementHybridHighConfig(),
        "hybrid_strong": FieldConfinementHybridStrongConfig(),
    }

    # Override num_ticks to 10k
    for config in configs.values():
        config.num_ticks = 10_000

    results = []

    for config_name, config in configs.items():
        result = run_10k_validation(config_name, config)
        results.append(result)

    # Summary comparison
    print()
    print()
    print("=" * 70)
    print("SUMMARY COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Config':<20} {'Creation':>10} {'Decay Thr':>10} {'Decay Rate':>10} "
          f"{'Drift %':>10} {'Final Cov %':>12} {'Energy Growth':>14}")
    print("-" * 90)

    for result in results:
        print(f"{result['config_name']:<20} "
              f"{result['creation_sensitivity']:>10.1f} "
              f"{result['decay_threshold']:>10.1f} "
              f"{result['decay_rate']:>10.3f} "
              f"{result['drift_percent']:>10.2f} "
              f"{result['final_coverage']*100:>12.1f} "
              f"{result['energy_growth']:>14.1f}×")

    print()

    # Find best configuration
    best = min(results, key=lambda r: r["final_coverage"])
    print(f"Best configuration (lowest coverage): {best['config_name']}")
    print(f"  Final coverage: {best['final_coverage']*100:.1f}%")
    print(f"  Drift: {best['drift_percent']:.2f}%")
    print(f"  Energy growth: {best['energy_growth']:.1f}×")
    print(f"  Creation sensitivity: {best['creation_sensitivity']:.1f}")
    print(f"  Decay threshold: {best['decay_threshold']:.1f}")
    print(f"  Decay rate: {best['decay_rate']:.3f}")

    print()

    # Save results
    with open("results/v6_10k_comparison.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Results saved to results/v6_10k_comparison.json")
    print("=" * 70)


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
