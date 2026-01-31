"""
V6 Phase 5: Jitter Sweep to Counteract Gravitational Collapse

Tests jitter strengths: 0.02, 0.03, 0.04, 0.05
Goal: Find minimum jitter needed to counteract radial gamma field attraction.

Uses CORRECTED COM tracking (not static coordinates).

Author: V6 Phase 5 Jitter Sweep
Date: 2026-01-25
"""

import time
import math
import json
from config_v6 import (
    FieldConfinementBaselineConfig,
    JitterSweepConfig03,
    JitterSweepConfig04,
    JitterSweepConfig05,
    JitterSweepConfig06,
    JitterSweepConfig07,
    JitterSweepConfig08,
    JitterSweepConfig09,
    JitterSweepConfig10,
    JitterSweepConfig11,
    JitterSweepConfig115,
    JitterSweepConfig117,
    JitterSweepConfig119,
    JitterSweepConfig12,
    JitterSweepConfig13,
    JitterSweepConfig14,
    JitterSweepConfig15,
    JitterSweepConfig30,
)
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


def run_jitter_test(config_name: str, config):
    """Run single jitter test with COM tracking."""

    print(f"\n{'='*70}")
    print(f"Configuration: {config_name}")
    print(f"{'='*70}")
    print(f"Jitter strength: {config.jitter_strength:.3f}")
    print(f"Gamma modulation: {config.gamma_modulation_strength:.1f}")
    print(f"Ticks: 100,000")
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

    # Save initial positions for COM tracking
    initial_positions = save_initial_pattern_positions(patterns)

    # Initial statistics
    stats_initial = compute_pattern_drift_statistics(patterns, grid, initial_positions)
    field_stats_initial = grid.get_field_statistics()

    print(f"Initial pattern distribution:")
    print(f"  Mean radius: {stats_initial['r_mean_initial']:.2f} Planck cells")
    print(f"  Std radius: {stats_initial['r_std_current']:.2f}")
    print(f"  Field energy: {field_stats_initial['total_energy']}")
    print(f"  Field coverage: {field_stats_initial['nonzero_fraction']*100:.1f}%")
    print()

    # Create jitter and evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(grid, jitter, gamma_modulation_strength=config.gamma_modulation_strength)

    # Run evolution
    print(f"Evolving for 100,000 ticks...")
    print()

    start_time = time.time()
    history = []
    num_ticks = 100000
    progress_interval = 100

    for tick in range(num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % progress_interval == 0:
            # Track actual field COM
            track_pattern_positions(grid, patterns, search_radius=15)
            stats = compute_pattern_drift_statistics(patterns, grid, initial_positions)
            field_stats = grid.get_field_statistics()

            record = {
                "tick": tick + 1,
                "r_mean_current": stats["r_mean_current"],
                "com_drift_mean": stats["com_drift_mean"],
                "r_drift_percent": stats["r_drift_percent"],
                "field_energy": field_stats["total_energy"],
                "field_coverage": field_stats["nonzero_fraction"],
            }
            history.append(record)

            print(f"[{tick+1:6d}/{num_ticks:6d}] "
                  f"r_mean={stats['r_mean_current']:6.2f}, "
                  f"drift={stats['com_drift_mean']:5.2f}, "
                  f"r_drift%={stats['r_drift_percent']:5.1f}%")

    elapsed = time.time() - start_time

    # Final statistics
    track_pattern_positions(grid, patterns, search_radius=15)
    stats_final = compute_pattern_drift_statistics(patterns, grid, initial_positions)
    field_stats_final = grid.get_field_statistics()

    print()
    print(f"{'='*70}")
    print("RESULTS")
    print(f"{'='*70}")
    print(f"Pattern drift (COM-tracked):")
    print(f"  Initial r_mean: {stats_initial['r_mean_initial']:.2f}")
    print(f"  Final r_mean: {stats_final['r_mean_current']:.2f}")
    print(f"  Radius drift: {stats_final['r_drift_percent']:.2f}%")
    print(f"  Mean COM displacement: {stats_final['com_drift_mean']:.2f} Planck cells")
    print()

    print(f"Field coverage:")
    print(f"  Initial: {field_stats_initial['nonzero_fraction']*100:.1f}%")
    print(f"  Final: {field_stats_final['nonzero_fraction']*100:.1f}%")
    print()

    print(f"Performance: {num_ticks / elapsed:.1f} ticks/sec")
    print(f"Total time: {elapsed:.1f} seconds")
    print(f"{'='*70}")

    # Return summary
    return {
        "config_name": config_name,
        "jitter_strength": config.jitter_strength,
        "initial_r_mean": stats_initial["r_mean_initial"],
        "final_r_mean": stats_final["r_mean_current"],
        "r_drift_percent": stats_final["r_drift_percent"],
        "com_drift_mean": stats_final["com_drift_mean"],
        "com_drift_max": stats_final["com_drift_max"],
        "initial_coverage": field_stats_initial["nonzero_fraction"],
        "final_coverage": field_stats_final["nonzero_fraction"],
        "initial_energy": field_stats_initial["total_energy"],
        "final_energy": field_stats_final["total_energy"],
        "ticks_per_sec": num_ticks / elapsed,
        "elapsed_seconds": elapsed,
        "history": history,
    }


def main():
    """Run jitter sweep for four configurations."""

    print("V6 Phase 5: Jitter Sweep to Counteract Gravitational Collapse")
    print("=" * 70)
    print()
    print("Testing jitter strengths to find stability threshold:")
    print("  1. jitter_0.02: 2% (baseline - known to collapse)")
    print("  2. jitter_0.03: 3% (moderate kinetic resistance)")
    print("  3. jitter_0.04: 4% (strong kinetic resistance)")
    print("  4. jitter_0.05: 5% (very strong kinetic resistance)")
    print()
    print("Using CORRECTED COM tracking (not static coordinates).")
    print()

    configs = {
        #"jitter_0.115": JitterSweepConfig115(),              # 10%
        #"jitter_0.117": JitterSweepConfig117(),              # 10%
        #"jitter_0.119": JitterSweepConfig119(),              # 10%
        "jitter_0.12": JitterSweepConfig12(),              # 10%
        "jitter_0.13": JitterSweepConfig13(),              # 10%
        "jitter_0.14": JitterSweepConfig14(),              # 10%
        "jitter_0.15": JitterSweepConfig15(),              # 10%
    }

    # Override num_ticks to 100,000 for short-term validation
    for config in configs.values():
        config.num_ticks = 100_000

    results = []

    for config_name, config in configs.items():
        result = run_jitter_test(config_name, config)
        results.append(result)

    # Summary comparison
    print()
    print()
    print("=" * 70)
    print("SUMMARY COMPARISON")
    print("=" * 70)
    print()

    print(f"{'Config':<15} {'Jitter':>8} {'Initial r':>10} {'Final r':>10} "
          f"{'r Drift %':>10} {'COM Drift':>12}")
    print("-" * 75)

    for result in results:
        print(f"{result['config_name']:<15} "
              f"{result['jitter_strength']:>8.3f} "
              f"{result['initial_r_mean']:>10.2f} "
              f"{result['final_r_mean']:>10.2f} "
              f"{result['r_drift_percent']:>10.2f} "
              f"{result['com_drift_mean']:>12.2f}")

    print()

    # Find best configuration (lowest drift)
    best = min(results, key=lambda r: r["r_drift_percent"])
    print(f"Best configuration (lowest radius drift): {best['config_name']}")
    print(f"  Jitter strength: {best['jitter_strength']:.3f}")
    print(f"  Radius drift: {best['r_drift_percent']:.2f}%")
    print(f"  Mean COM displacement: {best['com_drift_mean']:.2f} Planck cells")

    print()

    # Stability threshold analysis
    print("Stability Analysis:")
    for result in results:
        if result['r_drift_percent'] < 10.0:
            status = "STABLE"
        elif result['r_drift_percent'] < 30.0:
            status = "MARGINAL"
        else:
            status = "UNSTABLE (collapsing)"

        print(f"  {result['config_name']}: {status} (drift={result['r_drift_percent']:.1f}%)")

    print()

    # Save results
    with open("results/jitter_sweep_100k.12-15.json", "w") as f:
        json.dump(results, f, indent=2)

    print("Results saved to results/jitter_sweep_100k.12-15.json")
    print("=" * 70)


if __name__ == "__main__":
    import os
    os.makedirs("results", exist_ok=True)
    main()
