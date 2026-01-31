"""
V10 Experiment: Normalization Sweep

Test all three normalization approaches against V9 decay=0.10 baseline.

Normalization Options:
1. Global Sum: history / (1 + sum(history) / N)
2. Time-Based: history / (1 + commits)
3. Local Gamma: history / gamma_base

Success criteria: At least one normalization produces stability
without explicit decay parameter.

Physics question: Can "decay" emerge naturally from normalization
rather than being a free parameter?
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
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import track_pattern_positions

from gamma_wells_v10 import GammaWellSystemV10
from gamma_history_v10 import GammaHistoryCommitterV10
from config_v10 import RenormalizationConfig, create_normalization_config


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


def run_single_normalization_experiment(
    norm_type: str,
    norm_scale: float = 1000.0,
    verbose: bool = True
) -> Dict:
    """
    Run experiment with a single normalization configuration.

    Args:
        norm_type: 'global_sum', 'time_based', or 'local_gamma'
        norm_scale: Normalization scale factor
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = create_normalization_config(norm_type, norm_scale)

    if verbose:
        print(f"\n{'='*60}")
        print(f"NORMALIZATION: {norm_type} (scale={norm_scale})")
        print(f"{'='*60}")

    # Initialize
    grid = PlanckGrid(config.grid_width, config.grid_height)

    # Gamma well system (target only, no projectile)
    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # History committer with renormalization (NO decay parameter)
    history_committer = GammaHistoryCommitterV10(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        normalization_type=norm_type,
        normalization_scale=norm_scale
    )

    # Initial gamma field
    gamma_system.compute_gamma_field(history_committer)

    # Pattern library and cloud
    library = PatternLibrary(pattern_size=config.pattern_size)
    center = (center_x, center_y)
    cloud_patterns = initialize_cloud(grid, library, config)

    # Evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    # Tracking
    history = []
    commit_history = []

    start_time = time.time()

    for tick in range(config.num_ticks):
        # Evolve
        evolution.evolve_one_tick()

        # Record history
        history_committer.record_tick(cloud_patterns)

        # Check for commit
        if history_committer.should_commit():
            commit_stats = history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

            state = history_committer.get_state()
            commit_history.append({
                "tick": tick,
                "commit_number": commit_stats["commit_number"],
                "raw_history_sum": commit_stats["raw_history_sum"],
                "normalized_max": state["normalized_max"],
                "effective_norm_factor": state["effective_norm_factor"],
            })

        # Progress and measurement
        if (tick + 1) % config.progress_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center)
            hist_state = history_committer.get_state()

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_min": stats["r_min"],
                "r_max": stats["r_max"],
                "energy": stats["total_energy"],
                "raw_history_sum": hist_state["raw_history_sum"],
                "normalized_max": hist_state["normalized_max"],
                "effective_norm_factor": hist_state["effective_norm_factor"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f}±{stats['r_std']:.2f}, "
                      f"E={stats['total_energy']}, "
                      f"norm_max={hist_state['normalized_max']:.2f}, "
                      f"norm_factor={hist_state['effective_norm_factor']:.1f}")

    elapsed = time.time() - start_time

    # Final statistics
    final_stats = compute_cloud_stats(grid, cloud_patterns, center)
    final_history = history_committer.get_state()

    # Stability metrics (from second half of run)
    late_history = [h for h in history if h["tick"] >= config.stability_measurement_start]
    if late_history:
        r_std_values = [h["r_std"] for h in late_history]
        r_mean_values = [h["r_mean"] for h in late_history]
        energy_values = [h["energy"] for h in late_history]

        stability_metrics = {
            "r_std_mean": float(np.mean(r_std_values)),
            "r_std_std": float(np.std(r_std_values)),
            "r_mean_mean": float(np.mean(r_mean_values)),
            "r_mean_std": float(np.std(r_mean_values)),
            "energy_mean": float(np.mean(energy_values)),
            "energy_std": float(np.std(energy_values)),
        }
    else:
        stability_metrics = {}

    results = {
        "normalization_type": norm_type,
        "normalization_scale": norm_scale,
        "config": {
            "num_ticks": config.num_ticks,
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "n_patterns": config.n_patterns,
            "target_gamma_k": config.target_gamma_k,
            "jitter_strength": config.jitter_strength,
        },
        "final_stats": final_stats,
        "final_history": final_history,
        "stability_metrics": stability_metrics,
        "history": history,
        "commit_history": commit_history,
        "elapsed_seconds": elapsed,
    }

    if verbose:
        print(f"\nFinal: r={final_stats['r_mean']:.2f}±{final_stats['r_std']:.2f}, E={final_stats['total_energy']}")
        r_std_stability = stability_metrics.get('r_std_mean')
        if r_std_stability is not None:
            print(f"Stability (late): r_std_mean={r_std_stability:.3f}")
        else:
            print("Stability (late): N/A (not enough ticks)")
        print(f"Raw history sum: {final_history['raw_history_sum']:.1f}")
        print(f"Normalized max: {final_history['normalized_max']:.3f}")
        print(f"Effective norm factor: {final_history['effective_norm_factor']:.1f}")
        print(f"Time: {elapsed:.1f}s")

    return results


def run_normalization_sweep(verbose: bool = True) -> Dict:
    """
    Run full normalization type sweep.

    Tests global_sum, time_based, and local_gamma normalization.

    Returns:
        Combined results dictionary
    """
    print("=" * 70)
    print("V10 NORMALIZATION SWEEP EXPERIMENT")
    print("=" * 70)

    normalization_types = ['global_sum', 'time_based', 'local_gamma']
    print(f"Testing normalization types: {normalization_types}")
    print()

    all_results = {}
    summary = []

    for norm_type in normalization_types:
        results = run_single_normalization_experiment(
            norm_type,
            norm_scale=1000.0,
            verbose=verbose
        )
        all_results[norm_type] = results

        # Summary row
        summary.append({
            "norm_type": norm_type,
            "r_mean_final": results["final_stats"]["r_mean"],
            "r_std_final": results["final_stats"]["r_std"],
            "energy_final": results["final_stats"]["total_energy"],
            "r_std_stability": results["stability_metrics"].get("r_std_mean", -1),
            "normalized_max": results["final_history"]["normalized_max"],
            "effective_norm_factor": results["final_history"]["effective_norm_factor"],
        })

    # Print summary table
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"{'Type':>12} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>8} | "
          f"{'Stab(r_std)':>11} | {'Norm Max':>10} | {'Norm Factor':>11}")
    print("-" * 80)
    for row in summary:
        print(f"{row['norm_type']:>12} | {row['r_mean_final']:>8.2f} | "
              f"{row['r_std_final']:>8.3f} | {row['energy_final']:>8d} | "
              f"{row['r_std_stability']:>11.3f} | {row['normalized_max']:>10.3f} | "
              f"{row['effective_norm_factor']:>11.1f}")

    # Find best normalization
    best_stability = min(summary, key=lambda x: x["r_std_stability"] if x["r_std_stability"] >= 0 else float('inf'))
    print(f"\nMost stable (lowest r_std variation): {best_stability['norm_type']}")

    return {
        "all_results": all_results,
        "summary": summary,
        "best_stability": best_stability,
    }


def run_scale_sweep(norm_type: str = 'global_sum', verbose: bool = True) -> Dict:
    """
    Run normalization scale sweep for a specific normalization type.

    Args:
        norm_type: Normalization type to test
        verbose: Print progress

    Returns:
        Results dictionary
    """
    print("=" * 70)
    print(f"V10 SCALE SWEEP: {norm_type}")
    print("=" * 70)

    scales = [100.0, 500.0, 1000.0, 2000.0, 5000.0]
    print(f"Testing scales: {scales}")
    print()

    all_results = {}
    summary = []

    for scale in scales:
        results = run_single_normalization_experiment(
            norm_type,
            norm_scale=scale,
            verbose=verbose
        )
        all_results[f"scale_{scale}"] = results

        summary.append({
            "scale": scale,
            "r_mean_final": results["final_stats"]["r_mean"],
            "r_std_final": results["final_stats"]["r_std"],
            "energy_final": results["final_stats"]["total_energy"],
            "r_std_stability": results["stability_metrics"].get("r_std_mean", -1),
            "normalized_max": results["final_history"]["normalized_max"],
            "effective_norm_factor": results["final_history"]["effective_norm_factor"],
        })

    # Print summary table
    print("\n" + "=" * 80)
    print(f"SCALE SWEEP SUMMARY ({norm_type})")
    print("=" * 80)
    print(f"{'Scale':>10} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>8} | "
          f"{'Stab(r_std)':>11} | {'Norm Factor':>11}")
    print("-" * 80)
    for row in summary:
        print(f"{row['scale']:>10.0f} | {row['r_mean_final']:>8.2f} | "
              f"{row['r_std_final']:>8.3f} | {row['energy_final']:>8d} | "
              f"{row['r_std_stability']:>11.3f} | {row['effective_norm_factor']:>11.1f}")

    return {
        "norm_type": norm_type,
        "all_results": all_results,
        "summary": summary,
    }


def main():
    """Run normalization experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="V10 Normalization Experiments")
    parser.add_argument("--type", type=str, choices=['global_sum', 'time_based', 'local_gamma'],
                        help="Run single normalization type")
    parser.add_argument("--scale", type=float, default=1000.0, help="Normalization scale")
    parser.add_argument("--sweep-type", action="store_true", help="Run normalization type sweep")
    parser.add_argument("--sweep-scale", type=str, help="Run scale sweep for given type")
    parser.add_argument("--output", type=str, default="results/normalization_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.sweep_type:
        results = run_normalization_sweep(verbose=not args.quiet)
        output_file = args.output
    elif args.sweep_scale:
        results = run_scale_sweep(args.sweep_scale, verbose=not args.quiet)
        output_file = f"results/scale_sweep_{args.sweep_scale}.json"
    elif args.type:
        results = run_single_normalization_experiment(
            args.type,
            norm_scale=args.scale,
            verbose=not args.quiet
        )
        output_file = f"results/norm_{args.type}_{args.scale}.json"
    else:
        # Default: run type sweep
        results = run_normalization_sweep(verbose=not args.quiet)
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
