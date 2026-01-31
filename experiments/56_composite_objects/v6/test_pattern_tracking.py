"""
Test Pattern Tracking - Validate COM Detection vs Static Measurement

Quick test (1000 ticks) comparing:
1. OLD method: Static initial coordinates (gives artificial 0.0% drift)
2. NEW method: Field-weighted center-of-mass tracking (real drift)

This demonstrates the measurement flaw and validates the fix.

Author: V6 Pattern Tracking Validation
Date: 2026-01-25
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
from pattern_tracking import (
    track_pattern_positions,
    save_initial_pattern_positions,
    compute_pattern_drift_statistics,
)


def initialize_gamma_field(grid: PlanckGrid, k: float):
    """Initialize radial gamma field: gamma(r) = 1 + k/r^2"""
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
    """Initialize n_patterns monopole patterns at random positions."""
    import numpy as np

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


def compute_static_statistics(static_positions: list[tuple[float, float]], grid: PlanckGrid):
    """OLD method: Read static initial coordinates (artificial measurement)."""
    center_x = grid.width // 2
    center_y = grid.height // 2

    radii = []
    for (x, y) in static_positions:
        dx = x - center_x  # Static coordinates (never change)
        dy = y - center_y
        r = math.sqrt(dx*dx + dy*dy)
        radii.append(r)

    import numpy as np
    return {
        "r_mean": float(np.mean(radii)) if radii else 0.0,
        "r_std": float(np.std(radii)) if radii else 0.0,
    }


def main():
    """Run pattern tracking validation test (1000 ticks)."""

    print("=" * 70)
    print("V6 Pattern Tracking Validation Test")
    print("=" * 70)
    print()
    print("Comparing two measurement methods:")
    print("  1. OLD: Static initial coordinates (artificial 0.0% drift)")
    print("  2. NEW: Field-weighted center-of-mass (real drift)")
    print()

    # Load configuration
    config = ValidationConfig10k()
    config.num_ticks = 1000  # Quick test

    print("Configuration:")
    print(f"  Grid: {config.grid_width}x{config.grid_height} Planck cells")
    print(f"  Patterns: {config.n_patterns}")
    print(f"  Jitter strength: {config.jitter_strength:.3f}")
    print(f"  Gamma modulation: {config.gamma_modulation_strength:.1f}")
    print(f"  Ticks: {config.num_ticks:,}")
    print()

    # Create grid and initialize
    print("Initializing grid and gamma field...")
    grid = PlanckGrid(config.grid_width, config.grid_height)
    initialize_gamma_field(grid, config.gamma_field_k)

    library = PatternLibrary(pattern_size=config.pattern_size)

    print(f"Initializing {config.n_patterns} patterns...")
    patterns = initialize_patterns(grid, library, config)

    # Save initial positions for both methods
    initial_positions = save_initial_pattern_positions(patterns)  # NEW method: COM tracking
    static_positions = save_initial_pattern_positions(patterns)   # OLD method: static coordinates

    # Initial statistics (both methods start the same)
    stats_static_initial = compute_static_statistics(static_positions, grid)
    stats_com_initial = compute_pattern_drift_statistics(patterns, grid, initial_positions)

    print()
    print("Initial state (both methods):")
    print(f"  Mean radius: {stats_static_initial['r_mean']:.2f} Planck cells")
    print(f"  Std radius: {stats_static_initial['r_std']:.2f}")
    print()

    # Create jitter and evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(grid, jitter, gamma_modulation_strength=config.gamma_modulation_strength)

    # Run evolution
    print(f"Evolving for {config.num_ticks:,} ticks...")
    print()

    start_time = time.time()
    progress_interval = 100

    for tick in range(config.num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % progress_interval == 0:
            # OLD method: Read static coordinates (never change)
            stats_static = compute_static_statistics(static_positions, grid)

            # NEW method: Track actual field COM
            track_pattern_positions(grid, patterns, search_radius=15)
            stats_com = compute_pattern_drift_statistics(patterns, grid, initial_positions)

            print(f"[{tick+1:6d}/{config.num_ticks:6d}] "
                  f"Static: r_mean={stats_static['r_mean']:6.2f}, "
                  f"COM: r_mean={stats_com['r_mean_current']:6.2f}, "
                  f"drift={stats_com['com_drift_mean']:5.2f}")

    elapsed = time.time() - start_time

    # Final statistics
    stats_static_final = compute_static_statistics(static_positions, grid)

    # Track COM one last time for NEW method
    track_pattern_positions(grid, patterns, search_radius=15)
    stats_com_final = compute_pattern_drift_statistics(patterns, grid, initial_positions)

    print()
    print("=" * 70)
    print("RESULTS COMPARISON")
    print("=" * 70)
    print()

    print("OLD Method (Static Coordinates):")
    print(f"  Initial r_mean: {stats_static_initial['r_mean']:.6f}")
    print(f"  Final r_mean: {stats_static_final['r_mean']:.6f}")
    drift_static = abs(stats_static_final['r_mean'] - stats_static_initial['r_mean']) / stats_static_initial['r_mean'] * 100
    print(f"  Drift: {drift_static:.6f}%")
    print()

    print("NEW Method (Field COM Tracking):")
    print(f"  Initial r_mean: {stats_com_initial['r_mean_initial']:.6f}")
    print(f"  Final r_mean: {stats_com_final['r_mean_current']:.6f}")
    print(f"  Radius drift: {stats_com_final['r_drift_percent']:.2f}%")
    print(f"  Mean COM displacement: {stats_com_final['com_drift_mean']:.2f} Planck cells")
    print(f"  Max COM displacement: {stats_com_final['com_drift_max']:.2f} Planck cells")
    print()

    print(f"Performance: {config.num_ticks / elapsed:.1f} ticks/sec")
    print(f"Total time: {elapsed:.1f} seconds")
    print()

    # Validation
    if drift_static < 0.01:
        print("VALIDATION: OLD method shows artificial 0.0% drift (as expected)")
    else:
        print(f"WARNING: OLD method shows {drift_static:.2f}% drift (unexpected)")

    if stats_com_final['com_drift_mean'] > 0.1:
        print(f"VALIDATION: NEW method detects real drift ({stats_com_final['com_drift_mean']:.2f} cells)")
    else:
        print("INFO: NEW method shows very low drift (patterns may be truly stable)")

    print("=" * 70)

    # Save results
    results = {
        "old_method": {
            "initial_r_mean": stats_static_initial["r_mean"],
            "final_r_mean": stats_static_final["r_mean"],
            "drift_percent": drift_static,
        },
        "new_method": {
            "initial_r_mean": stats_com_initial["r_mean_initial"],
            "final_r_mean": stats_com_final["r_mean_current"],
            "radius_drift_percent": stats_com_final["r_drift_percent"],
            "com_drift_mean": stats_com_final["com_drift_mean"],
            "com_drift_max": stats_com_final["com_drift_max"],
        },
        "performance": {
            "ticks_per_sec": config.num_ticks / elapsed,
            "elapsed_seconds": elapsed,
        },
    }

    with open("results/pattern_tracking_test.json", "w") as f:
        json.dump(results, f, indent=2)

    print()
    print("Results saved to results/pattern_tracking_test.json")


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
