"""
V11 Experiment: Well=Window Coupling Test

Tests the hypothesis that target_gamma_k = gamma_window_size is a valid coupling.

Physical meaning: The central gamma well represents "a pattern that has existed
for window_size ticks at full density." If this coupling is correct, stable
patterns should emerge across all window sizes.

Test matrix:
| window_size | target_gamma_k | Expected |
|-------------|----------------|----------|
| 25          | 25.0           | Weaker confinement |
| 50          | 50.0           | V10 baseline |
| 75          | 75.0           | Stronger confinement |
| 100         | 100.0          | Very strong confinement |

Success criterion: Stable patterns across all window sizes
(proves coupling is physically correct, not coincidental)
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import List, Dict

# Add paths
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
v9_path = Path(__file__).parent.parent / "v9"
v10_path = Path(__file__).parent.parent / "v10"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v9_path))
sys.path.insert(0, str(v10_path))

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

# V11 config
from config_v11 import WellWindowConfig, WINDOW_SIZES, create_window_config


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config) -> List:
    """Initialize cloud patterns."""
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
        instance = PatternInstance(sample, "monopole", instance_id=f"cloud_{i}")
        instance.write_to_grid(grid, library)
        patterns.append(instance)

    return patterns


def compute_cloud_stats(grid: PlanckGrid, patterns: List, center: tuple) -> Dict:
    """Compute cloud statistics."""
    track_pattern_positions(grid, patterns, search_radius=15)

    radii = []
    for p in patterns:
        dx = p.sample.center_x - center[0]
        dy = p.sample.center_y - center[1]
        r = math.sqrt(dx * dx + dy * dy)
        radii.append(r)

    stats = grid.get_field_statistics()

    return {
        "r_mean": float(np.mean(radii)) if radii else 0.0,
        "r_std": float(np.std(radii)) if radii else 0.0,
        "r_min": float(np.min(radii)) if radii else 0.0,
        "r_max": float(np.max(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
    }


def run_window_experiment(
    window_size: int,
    num_ticks: int = 2000,
    verbose: bool = True
) -> Dict:
    """
    Run V11 experiment with well=window coupling.

    Args:
        window_size: Window size (also sets well strength)
        num_ticks: Number of ticks to run
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = create_window_config(window_size)
    config.num_ticks = num_ticks

    if verbose:
        print(f"\n{'='*60}")
        print(f"V11 COUPLING TEST: window={window_size}, well={config.target_gamma_k}")
        print(f"{'='*60}")

    grid = PlanckGrid(config.grid_width, config.grid_height)

    # V10 gamma well system with V11 derived well strength
    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # V10 history committer with V11 window size
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

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        if (tick + 1) % config.progress_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center)
            hist_state = history_committer.get_state()

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "energy": stats["total_energy"],
                "normalized_max": hist_state["normalized_max"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f}±{stats['r_std']:.2f}, "
                      f"E={stats['total_energy']}, norm_max={hist_state['normalized_max']:.2f}")

    elapsed = time.time() - start_time

    final_stats = compute_cloud_stats(grid, cloud_patterns, center)
    final_history = history_committer.get_state()

    # Stability metrics (measure after initial transient)
    late_history = [h for h in history if h["tick"] >= config.stability_measurement_start]
    stability_metrics = {}
    if late_history:
        r_means = [h["r_mean"] for h in late_history]
        r_stds = [h["r_std"] for h in late_history]
        energies = [h["energy"] for h in late_history]

        stability_metrics = {
            "r_mean_avg": float(np.mean(r_means)),
            "r_mean_std": float(np.std(r_means)),  # Drift indicator
            "r_std_avg": float(np.mean(r_stds)),
            "energy_avg": float(np.mean(energies)),
            "energy_std": float(np.std(energies)),
        }

    if verbose:
        print(f"\nFinal: r={final_stats['r_mean']:.2f}±{final_stats['r_std']:.2f}")
        if stability_metrics:
            print(f"Stability: r_mean_avg={stability_metrics['r_mean_avg']:.2f}, "
                  f"drift={stability_metrics['r_mean_std']:.3f}")
        print(f"Time: {elapsed:.1f}s")

    return {
        "window_size": window_size,
        "target_gamma_k": config.target_gamma_k,
        "coupling": "well=window",
        "final_stats": final_stats,
        "final_history": final_history,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
    }


def run_window_sweep(
    window_sizes: List[int] = None,
    num_ticks: int = 2000,
    verbose: bool = True
) -> Dict:
    """
    Run window sweep with well=window coupling.

    Tests the coupling hypothesis across multiple window sizes.

    Args:
        window_sizes: List of window sizes to test
        num_ticks: Number of ticks per experiment
        verbose: Print progress

    Returns:
        Combined results dictionary
    """
    if window_sizes is None:
        window_sizes = WINDOW_SIZES

    print("=" * 70)
    print("V11 WELL=WINDOW COUPLING SWEEP")
    print("=" * 70)
    print()
    print("Hypothesis: target_gamma_k = gamma_window_size")
    print("Physical meaning: Well represents 'eternal pattern' accumulation")
    print()
    print(f"Testing window sizes: {window_sizes}")
    print()

    all_results = {}
    summary = []

    for ws in window_sizes:
        results = run_window_experiment(
            window_size=ws,
            num_ticks=num_ticks,
            verbose=verbose
        )
        all_results[f"window_{ws}"] = results

        summary.append({
            "window_size": ws,
            "well_k": results["target_gamma_k"],
            "r_mean": results["final_stats"]["r_mean"],
            "r_std": results["final_stats"]["r_std"],
            "energy": results["final_stats"]["total_energy"],
            "drift": results["stability_metrics"].get("r_mean_std", -1),
            "elapsed": results["elapsed_seconds"],
        })

    # Print comparison table
    print("\n" + "=" * 70)
    print("WINDOW SWEEP SUMMARY")
    print("=" * 70)
    print(f"{'Window':>8} | {'Well k':>8} | {'r_mean':>8} | {'r_std':>8} | {'Drift':>8} | {'Energy':>8}")
    print("-" * 70)
    for row in summary:
        drift_str = f"{row['drift']:.4f}" if row['drift'] >= 0 else "N/A"
        print(f"{row['window_size']:>8} | {row['well_k']:>8.1f} | {row['r_mean']:>8.2f} | "
              f"{row['r_std']:>8.3f} | {drift_str:>8} | {row['energy']:>8d}")

    # Analyze coupling validity
    print("\n" + "=" * 70)
    print("COUPLING ANALYSIS")
    print("=" * 70)

    # Check if all experiments are stable (drift < threshold)
    drift_threshold = 0.5  # Max acceptable drift in r_mean
    stable_count = sum(1 for row in summary if row['drift'] >= 0 and row['drift'] < drift_threshold)

    print(f"Stable experiments (drift < {drift_threshold}): {stable_count}/{len(summary)}")

    if stable_count == len(summary):
        print("\nSUCCESS: All window sizes produce stable patterns!")
        print("The well=window coupling is validated.")
        print(f"Parameter reduction: 9 -> 8 (target_gamma_k derived from gamma_window_size)")
    elif stable_count >= len(summary) / 2:
        print("\nPARTIAL SUCCESS: Most window sizes produce stable patterns.")
        print("The coupling may need adjustment for extreme values.")
    else:
        print("\nFAILED: Coupling does not produce consistent stability.")
        print("The well=window relationship may be coincidental for window=50.")

    # Additional analysis: check r_mean scaling
    print("\n--- Confinement Analysis ---")
    if len(summary) >= 2:
        # Expect larger windows to have similar confinement (normalized by well strength)
        r_means = [row['r_mean'] for row in summary]
        windows = [row['window_size'] for row in summary]

        # Normalized radius (r / sqrt(well_k)) should be roughly constant if coupling is correct
        normalized_r = [row['r_mean'] / math.sqrt(row['well_k']) if row['well_k'] > 0 else 0
                       for row in summary]
        norm_std = np.std(normalized_r) if normalized_r else 0
        norm_mean = np.mean(normalized_r) if normalized_r else 0

        print(f"Normalized radii (r/sqrt(k)): {[f'{r:.2f}' for r in normalized_r]}")
        print(f"Normalized r_mean: {norm_mean:.3f}, std: {norm_std:.3f}")

        if norm_std < 0.5:
            print("Confinement scales correctly with well strength (good coupling).")
        else:
            print("Confinement does not scale uniformly (coupling may need refinement).")

    return {
        "all_results": all_results,
        "summary": summary,
        "coupling_validated": stable_count == len(summary),
    }


def main():
    """Run V11 coupling experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="V11 Well=Window Coupling Test")
    parser.add_argument("--ticks", type=int, default=2000, help="Number of ticks")
    parser.add_argument("--window", type=int, help="Single window size to test")
    parser.add_argument("--windows", type=str, help="Comma-separated window sizes")
    parser.add_argument("--output", type=str, default="results/coupling_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.window:
        # Single window test
        results = run_window_experiment(
            window_size=args.window,
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = f"results/window_{args.window}.json"
    elif args.windows:
        # Custom window list
        window_sizes = [int(w.strip()) for w in args.windows.split(',')]
        results = run_window_sweep(
            window_sizes=window_sizes,
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = args.output
    else:
        # Default sweep
        results = run_window_sweep(
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
