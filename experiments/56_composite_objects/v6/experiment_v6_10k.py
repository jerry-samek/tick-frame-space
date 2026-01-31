"""
V6 10k Tick Validation Experiment

Tests pattern confinement over 10,000 ticks with optimal parameters from tuning.

Parameters (from tuning results):
- Jitter strength: 0.01 (1% chance of ±1 per cell per tick)
- Gamma modulation: 1.0 (increased from 0.5 for longer stability)
- Gamma field k: 100.0

Success criteria:
- Cloud radius drift < 10% over 10k ticks
- Patterns remain confined (not spread throughout the grid)
- Field energy grows moderately (not explosive)

Author: V6 Grid-Based Implementation
Date: 2026-01-24
"""

import time
import math
import json
from config_v6 import ValidationConfig10k
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


def main():
    """Run 10k tick validation experiment."""

    print("=" * 70)
    print("V6 10k Tick Validation Experiment")
    print("=" * 70)
    print()

    # Load configuration
    config = ValidationConfig10k()

    print("Configuration:")
    print(f"  Grid: {config.grid_width}x{config.grid_height} Planck cells")
    print(f"  Patterns: {config.n_patterns}")
    print(f"  Jitter strength: {config.jitter_strength:.3f}")
    print(f"  Gamma modulation: {config.gamma_modulation_strength:.1f}")
    print(f"  Gamma field k: {config.gamma_field_k:.1f}")
    print(f"  Ticks: {config.num_ticks:,}")
    print()

    # Create grid
    print("Initializing grid and gamma field...")
    grid = PlanckGrid(config.grid_width, config.grid_height)
    initialize_gamma_field(grid, config.gamma_field_k)

    # Create pattern library
    library = PatternLibrary(pattern_size=config.pattern_size)

    # Initialize patterns
    print(f"Initializing {config.n_patterns} patterns...")
    patterns = initialize_patterns(grid, library, config)

    # Initial statistics
    stats_initial = compute_pattern_statistics(patterns, grid)
    field_stats_initial = grid.get_field_statistics()

    print()
    print("Initial state:")
    print(f"  Mean radius: {stats_initial['r_mean']:.2f} Planck cells")
    print(f"  Std radius: {stats_initial['r_std']:.2f}")
    print(f"  Range: [{stats_initial['r_min']:.2f}, {stats_initial['r_max']:.2f}]")
    print(f"  Field energy: {field_stats_initial['total_energy']}")
    print(f"  Nonzero cells: {field_stats_initial['nonzero_fraction']*100:.1f}%")
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
                "r_min": stats["r_min"],
                "r_max": stats["r_max"],
                "field_energy": field_stats["total_energy"],
                "nonzero_fraction": field_stats["nonzero_fraction"],
            }
            history.append(record)

            print(f"[{tick+1:7d}/{config.num_ticks:7d}] "
                  f"r_mean={stats['r_mean']:6.2f}, "
                  f"r_std={stats['r_std']:5.2f}, "
                  f"energy={field_stats['total_energy']:6d}, "
                  f"nonzero={field_stats['nonzero_fraction']*100:5.1f}%")

    elapsed = time.time() - start_time

    # Final statistics
    stats_final = compute_pattern_statistics(patterns, grid)
    field_stats_final = grid.get_field_statistics()

    print()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print()

    print("Cloud radius:")
    print(f"  Initial: {stats_initial['r_mean']:.2f} Planck cells")
    print(f"  Final: {stats_final['r_mean']:.2f} Planck cells")

    drift_percent = abs(stats_final['r_mean'] - stats_initial['r_mean']) / stats_initial['r_mean'] * 100
    print(f"  Drift: {drift_percent:.2f}%")
    print()

    print("Field energy:")
    print(f"  Initial: {field_stats_initial['total_energy']}")
    print(f"  Final: {field_stats_final['total_energy']}")
    print(f"  Growth: {field_stats_final['total_energy'] - field_stats_initial['total_energy']}")
    print()

    print("Grid coverage:")
    print(f"  Initial: {field_stats_initial['nonzero_fraction']*100:.1f}%")
    print(f"  Final: {field_stats_final['nonzero_fraction']*100:.1f}%")
    print()

    print(f"Performance: {config.num_ticks / elapsed:.1f} ticks/sec")
    print(f"Total time: {elapsed/60:.1f} minutes")
    print()

    # Validation
    success = drift_percent < config.max_radius_drift_percent

    if success:
        print("VALIDATION: SUCCESS")
        print(f"  Drift {drift_percent:.2f}% < {config.max_radius_drift_percent:.1f}% threshold")
    else:
        print("VALIDATION: FAILED")
        print(f"  Drift {drift_percent:.2f}% >= {config.max_radius_drift_percent:.1f}% threshold")

    print("=" * 70)

    # Save results
    results = {
        "config": {
            "jitter_strength": config.jitter_strength,
            "gamma_modulation_strength": config.gamma_modulation_strength,
            "gamma_field_k": config.gamma_field_k,
            "n_patterns": config.n_patterns,
            "num_ticks": config.num_ticks,
        },
        "initial": {
            "r_mean": stats_initial["r_mean"],
            "r_std": stats_initial["r_std"],
            "r_min": stats_initial["r_min"],
            "r_max": stats_initial["r_max"],
            "field_energy": field_stats_initial["total_energy"],
            "nonzero_fraction": field_stats_initial["nonzero_fraction"],
        },
        "final": {
            "r_mean": stats_final["r_mean"],
            "r_std": stats_final["r_std"],
            "r_min": stats_final["r_min"],
            "r_max": stats_final["r_max"],
            "field_energy": field_stats_final["total_energy"],
            "nonzero_fraction": field_stats_final["nonzero_fraction"],
        },
        "drift_percent": drift_percent,
        "success": success,
        "ticks_per_sec": config.num_ticks / elapsed,
        "elapsed_minutes": elapsed / 60,
        "history": history,
    }

    with open("results/v6_validation_10k.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to results/v6_validation_10k.json")


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
