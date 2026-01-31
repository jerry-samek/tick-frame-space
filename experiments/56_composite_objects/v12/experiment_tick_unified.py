"""
V12c Experiment: Tick-Unified Parameters

Hypothesis: All gamma parameters = tick (eliminate empirical ratios).

V12b used empirical ratios:
- gamma_window_size = tick / 2
- gamma_imprint_k = tick / 10
- target_gamma_k = window = tick / 2

V12c simplifies to 1:1:1:
- gamma_window_size = tick
- gamma_imprint_k = tick
- target_gamma_k = tick

The dimensional density argument:
- 1D: see all n entities
- 2D: see n/n^2 = 1/n fraction
- 3D: see n/n^3 = 1/n^2 fraction

"We add 1 for each tick to the window" - so window = tick.

Parameter comparison at tick=100:

| Parameter    | V12b | V12c | Change |
|--------------|------|------|--------|
| window       | 50   | 100  | 2x     |
| imprint      | 10   | 100  | 10x    |
| well         | 50   | 100  | 2x     |
| window/imprint | 5  | 1    | 5x→1x  |

Success criteria:
- All scales stable (no collapse)
- Similar or better stability than V12b
- Fewer empirical constants needed (8 → 6)
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import List, Dict, Any

# Add paths
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
v9_path = Path(__file__).parent.parent / "v9"
v10_path = Path(__file__).parent.parent / "v10"
v11_path = Path(__file__).parent.parent / "v11"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v9_path))
sys.path.insert(0, str(v10_path))
sys.path.insert(0, str(v11_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import track_pattern_positions

# V10 imports (renormalization-based)
from gamma_wells_v10 import GammaWellSystemV10
from gamma_history_v10 import GammaHistoryCommitterV10

# V12 configs
from config_v12 import (
    EntityTickConfig, create_entity_tick_config,
    TickUnifiedConfig, create_tick_unified_config
)


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config) -> List:
    """Initialize cloud patterns with entity count = tick."""
    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    init_radius_mean = config.entity_tick_init_radius
    init_radius_std = init_radius_mean * 0.2

    for i in range(config.n_patterns):
        r = rng.normal(init_radius_mean, init_radius_std)
        r = max(config.pattern_size, r)
        theta = rng.uniform(0, 2 * math.pi)

        px = int(center_x + r * math.cos(theta))
        py = int(center_y + r * math.sin(theta))

        px = max(0, min(grid.width - config.pattern_size, px))
        py = max(0, min(grid.height - config.pattern_size, py))

        sample = SampleCell(px, py, size=config.pattern_size)
        instance = PatternInstance(sample, "monopole", instance_id=f"entity_{i}")
        instance.write_to_grid(grid, library)
        patterns.append(instance)

    return patterns


def compute_cloud_stats(
    grid: PlanckGrid,
    patterns: List,
    center: tuple,
    grid_size: int
) -> Dict[str, Any]:
    """Compute cloud statistics with normalized metrics."""
    track_pattern_positions(grid, patterns, search_radius=15)

    radii = []
    for p in patterns:
        dx = p.sample.center_x - center[0]
        dy = p.sample.center_y - center[1]
        r = math.sqrt(dx * dx + dy * dy)
        radii.append(r)

    stats = grid.get_field_statistics()

    r_mean = float(np.mean(radii)) if radii else 0.0
    r_std = float(np.std(radii)) if radii else 0.0

    half_grid = grid_size / 2.0
    r_mean_norm = r_mean / half_grid if half_grid > 0 else 0.0
    r_std_norm = r_std / half_grid if half_grid > 0 else 0.0

    area = grid_size * grid_size
    energy_density = stats["total_energy"] / area if area > 0 else 0.0
    pattern_count = len(patterns)
    pattern_density_2d = pattern_count / area if area > 0 else 0.0

    return {
        "r_mean": r_mean,
        "r_std": r_std,
        "r_min": float(np.min(radii)) if radii else 0.0,
        "r_max": float(np.max(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
        "pattern_count": pattern_count,
        "r_mean_norm": r_mean_norm,
        "r_std_norm": r_std_norm,
        "energy_density": energy_density,
        "pattern_density_2d": pattern_density_2d,
    }


def run_single_experiment(
    config,
    config_name: str,
    num_ticks: int = 1000,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run a single experiment with given config.

    Args:
        config: Configuration object (EntityTickConfig or TickUnifiedConfig)
        config_name: Name for logging (e.g., "V12b" or "V12c")
        num_ticks: Number of simulation ticks to run
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary with metrics
    """
    grid_size = config.grid_size

    if verbose:
        print(f"\n{'='*70}")
        print(f"{config_name} EXPERIMENT: grid={grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    grid = PlanckGrid(config.grid_width, config.grid_height)

    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    history_committer = GammaHistoryCommitterV10(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        normalization_type=config.normalization_type,
        normalization_scale=config.normalization_scale
    )

    gamma_system.compute_gamma_field(history_committer)

    library = PatternLibrary(pattern_size=config.pattern_size)
    center = (center_x, center_y)
    cloud_patterns = initialize_cloud(grid, library, config)

    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    history = []
    start_time = time.time()

    if verbose:
        init_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
        print(f"[INIT ] patterns={init_stats['pattern_count']:4d}, "
              f"r_mean={init_stats['r_mean']:6.2f} (norm={init_stats['r_mean_norm']:.4f})")

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        if verbose and (tick + 1) % verbose_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_mean_norm": stats["r_mean_norm"],
                "energy_density": stats["energy_density"],
                "pattern_count": stats["pattern_count"],
            })

            status = "RUNNING"
            if stats["r_mean_norm"] < 0.01:
                status = "COLLAPSED?"
            elif stats["r_mean_norm"] > 0.5:
                status = "DISPERSED?"

            print(f"[{tick+1:5d}] r_mean={stats['r_mean']:6.2f} (norm={stats['r_mean_norm']:.4f}), "
                  f"E_dens={stats['energy_density']:.4f}, "
                  f"rate={tick_rate:.1f} t/s [{status}]")

    elapsed = time.time() - start_time
    final_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)

    # Stability metrics (after initial transient)
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means_norm = [h["r_mean_norm"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means_norm)),
            "r_mean_norm_std": float(np.std(r_means_norm)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: r_mean={final_stats['r_mean']:.2f} (norm={final_stats['r_mean_norm']:.4f})")
        if stability_metrics:
            print(f"       drift={stability_metrics['r_mean_norm_std']:.5f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": config_name,
        "grid_size": grid_size,
        "effective_tick": config.effective_tick,
        "n_patterns": config.n_patterns,
        "params": {
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "target_gamma_k": config.target_gamma_k,
            "window_imprint_ratio": config.gamma_window_size / config.gamma_imprint_k if config.gamma_imprint_k > 0 else 0,
            "jitter_strength": config.jitter_strength,
        },
        "final_stats": final_stats,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_comparison_experiment(
    grid_size: int,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Compare V12b (tick-ratio) vs V12c (tick-unified) at a single scale.

    Args:
        grid_size: Grid dimension to test
        num_ticks: Number of ticks per experiment
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Comparison results
    """
    print("=" * 70)
    print(f"V12b vs V12c COMPARISON at grid={grid_size}")
    print("=" * 70)
    print()

    # Show parameter differences
    v12b_config = create_entity_tick_config(grid_size)
    v12c_config = create_tick_unified_config(grid_size)

    print("Parameter comparison:")
    print(f"{'Parameter':>20} | {'V12b':>10} | {'V12c':>10} | {'Change':>10}")
    print("-" * 60)
    print(f"{'window':>20} | {v12b_config.gamma_window_size:>10} | {v12c_config.gamma_window_size:>10} | {v12c_config.gamma_window_size/v12b_config.gamma_window_size:>9.1f}x")
    print(f"{'imprint':>20} | {v12b_config.gamma_imprint_k:>10.1f} | {v12c_config.gamma_imprint_k:>10.1f} | {v12c_config.gamma_imprint_k/v12b_config.gamma_imprint_k:>9.1f}x")
    print(f"{'well':>20} | {v12b_config.target_gamma_k:>10.1f} | {v12c_config.target_gamma_k:>10.1f} | {v12c_config.target_gamma_k/v12b_config.target_gamma_k:>9.1f}x")
    w2i_v12b = v12b_config.gamma_window_size / v12b_config.gamma_imprint_k
    w2i_v12c = v12c_config.gamma_window_size / v12c_config.gamma_imprint_k
    print(f"{'window/imprint':>20} | {w2i_v12b:>10.1f} | {w2i_v12c:>10.1f} | {w2i_v12b:>4.0f}:1->{w2i_v12c:.0f}:1")
    print()

    # Run both experiments
    v12b_results = run_single_experiment(
        v12b_config, "V12b",
        num_ticks=num_ticks,
        verbose_interval=verbose_interval,
        verbose=verbose
    )

    v12c_results = run_single_experiment(
        v12c_config, "V12c",
        num_ticks=num_ticks,
        verbose_interval=verbose_interval,
        verbose=verbose
    )

    # Compare results
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Metric':>20} | {'V12b':>12} | {'V12c':>12} | {'Diff':>10}")
    print("-" * 60)

    v12b_r = v12b_results["final_stats"]["r_mean_norm"]
    v12c_r = v12c_results["final_stats"]["r_mean_norm"]
    diff_r = v12c_r - v12b_r
    print(f"{'r_mean_norm':>20} | {v12b_r:>12.4f} | {v12c_r:>12.4f} | {diff_r:>+10.4f}")

    v12b_drift = v12b_results.get("stability_metrics", {}).get("r_mean_norm_std", -1)
    v12c_drift = v12c_results.get("stability_metrics", {}).get("r_mean_norm_std", -1)
    if v12b_drift >= 0 and v12c_drift >= 0:
        diff_drift = v12c_drift - v12b_drift
        print(f"{'drift':>20} | {v12b_drift:>12.5f} | {v12c_drift:>12.5f} | {diff_drift:>+10.5f}")

    v12b_e = v12b_results["final_stats"]["energy_density"]
    v12c_e = v12c_results["final_stats"]["energy_density"]
    diff_e = v12c_e - v12b_e
    print(f"{'energy_density':>20} | {v12b_e:>12.4f} | {v12c_e:>12.4f} | {diff_e:>+10.4f}")

    # Determine status
    v12b_stable = 0.01 <= v12b_r <= 0.5
    v12c_stable = 0.01 <= v12c_r <= 0.5

    print("\n" + "-" * 60)
    print(f"V12b status: {'STABLE' if v12b_stable else 'UNSTABLE'}")
    print(f"V12c status: {'STABLE' if v12c_stable else 'UNSTABLE'}")

    if v12b_stable and v12c_stable:
        if abs(diff_r) < 0.05:
            print("\nBOTH STABLE with similar behavior - V12c simplification works!")
        elif diff_r > 0:
            print("\nBOTH STABLE - V12c shows slightly more expansion")
        else:
            print("\nBOTH STABLE - V12c shows slightly more contraction")
    elif v12c_stable and not v12b_stable:
        print("\nV12c BETTER: stable while V12b unstable!")
    elif v12b_stable and not v12c_stable:
        print("\nV12c WORSE: unstable while V12b stable - need ratio adjustment")
    else:
        print("\nBOTH UNSTABLE at this scale")

    return {
        "grid_size": grid_size,
        "v12b": v12b_results,
        "v12c": v12c_results,
        "comparison": {
            "r_diff": diff_r,
            "v12b_stable": v12b_stable,
            "v12c_stable": v12c_stable,
        }
    }


def run_tick_unified_sweep(
    grid_sizes: List[int] = None,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run tick-unified sweep across multiple grid sizes.

    Compares V12b (empirical ratios) vs V12c (all = tick).

    Args:
        grid_sizes: List of grid sizes to test
        num_ticks: Number of ticks per experiment
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Combined results with analysis
    """
    if grid_sizes is None:
        grid_sizes = [50, 100, 200]

    print("=" * 70)
    print("V12c TICK-UNIFIED SWEEP")
    print("=" * 70)
    print()
    print("Hypothesis: All gamma parameters = tick (1:1:1 ratio)")
    print()
    print("V12b: window=tick/2, imprint=tick/10 (5:1 ratio)")
    print("V12c: window=tick, imprint=tick (1:1 ratio)")
    print()
    print(f"Testing grid sizes: {grid_sizes}")
    print()

    all_results = {}
    summary_v12b = []
    summary_v12c = []

    for gs in grid_sizes:
        comparison = run_comparison_experiment(
            grid_size=gs,
            num_ticks=num_ticks,
            verbose_interval=verbose_interval,
            verbose=verbose
        )
        all_results[f"grid_{gs}"] = comparison

        # Extract summaries
        v12b = comparison["v12b"]
        v12c = comparison["v12c"]

        summary_v12b.append({
            "grid_size": gs,
            "r_mean_norm": v12b["final_stats"]["r_mean_norm"],
            "energy_density": v12b["final_stats"]["energy_density"],
            "drift": v12b.get("stability_metrics", {}).get("r_mean_norm_std", -1),
            "stable": comparison["comparison"]["v12b_stable"],
        })

        summary_v12c.append({
            "grid_size": gs,
            "r_mean_norm": v12c["final_stats"]["r_mean_norm"],
            "energy_density": v12c["final_stats"]["energy_density"],
            "drift": v12c.get("stability_metrics", {}).get("r_mean_norm_std", -1),
            "stable": comparison["comparison"]["v12c_stable"],
        })

    # Final comparison
    print("\n" + "=" * 70)
    print("FINAL COMPARISON: V12b vs V12c")
    print("=" * 70)

    print("\n--- V12b (tick/2, tick/10) ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'E_dens':>10} | {'Drift':>10} | {'Status':>10}")
    print("-" * 55)
    for row in summary_v12b:
        drift_str = f"{row['drift']:.6f}" if row['drift'] >= 0 else "N/A"
        status = "STABLE" if row['stable'] else "UNSTABLE"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | {drift_str:>10} | {status:>10}")

    print("\n--- V12c (tick, tick) ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'E_dens':>10} | {'Drift':>10} | {'Status':>10}")
    print("-" * 55)
    for row in summary_v12c:
        drift_str = f"{row['drift']:.6f}" if row['drift'] >= 0 else "N/A"
        status = "STABLE" if row['stable'] else "UNSTABLE"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | {drift_str:>10} | {status:>10}")

    # Analysis
    v12b_stable_count = sum(1 for row in summary_v12b if row['stable'])
    v12c_stable_count = sum(1 for row in summary_v12c if row['stable'])

    print("\n" + "-" * 70)
    print("VERDICT:")
    print("-" * 70)

    print(f"\nV12b stable scales: {v12b_stable_count}/{len(grid_sizes)}")
    print(f"V12c stable scales: {v12c_stable_count}/{len(grid_sizes)}")

    if v12c_stable_count == len(grid_sizes):
        if v12b_stable_count == len(grid_sizes):
            print("\nSUCCESS: V12c (1:1:1 ratio) is as stable as V12b (5:1 ratio)")
            print("The simpler model works! Eliminated 2 empirical constants.")
        else:
            print("\nBONUS: V12c MORE stable than V12b!")
    elif v12c_stable_count > v12b_stable_count:
        print("\nPARTIAL SUCCESS: V12c more stable than V12b at some scales")
    elif v12c_stable_count == v12b_stable_count:
        print("\nNEUTRAL: Similar stability - V12c may still be preferred for simplicity")
    else:
        print("\nFAILED: V12c less stable than V12b")
        print("The 5:1 ratio may be necessary, not just empirical")

    return {
        "all_results": all_results,
        "summary_v12b": summary_v12b,
        "summary_v12c": summary_v12c,
        "analysis": {
            "v12b_stable_count": v12b_stable_count,
            "v12c_stable_count": v12c_stable_count,
            "total_scales": len(grid_sizes),
            "v12c_as_good_or_better": v12c_stable_count >= v12b_stable_count,
        },
    }


def main():
    """Run V12c tick-unified experiments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V12c Tick-Unified Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_tick_unified.py --ticks 1000
  python experiment_tick_unified.py --grid 100 --ticks 500
  python experiment_tick_unified.py --grids 50,100,200 --ticks 2000
        """
    )
    parser.add_argument("--ticks", type=int, default=1000, help="Number of ticks (default: 1000)")
    parser.add_argument("--grid", type=int, help="Single grid size to compare")
    parser.add_argument("--grids", type=str, help="Comma-separated grid sizes (default: 50,100,200)")
    parser.add_argument("--interval", type=int, default=100, help="Verbose output interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/tick_unified_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.grid:
        # Single grid comparison
        results = run_comparison_experiment(
            grid_size=args.grid,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = f"results/tick_unified_grid_{args.grid}.json"
    elif args.grids:
        # Custom grid list
        grid_sizes = [int(g.strip()) for g in args.grids.split(',')]
        results = run_tick_unified_sweep(
            grid_sizes=grid_sizes,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output
    else:
        # Default sweep (50, 100, 200)
        results = run_tick_unified_sweep(
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
