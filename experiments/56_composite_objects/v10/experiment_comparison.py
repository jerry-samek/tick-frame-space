"""
V10 Experiment: Comparison with V9 Baseline

Compare V10 renormalization approaches against V9 decay=0.10 baseline.

This validates whether renormalization can replace explicit decay
while maintaining stability.
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
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v9_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import track_pattern_positions

# V9 imports (decay-based)
from gamma_wells import GammaWellSystem
from gamma_history import GammaHistoryCommitter

# V10 imports (renormalization-based)
from gamma_wells_v10 import GammaWellSystemV10
from gamma_history_v10 import GammaHistoryCommitterV10
from config_v10 import RenormalizationConfig


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


def run_v9_baseline(decay: float = 0.10, num_ticks: int = 2000, verbose: bool = True) -> Dict:
    """
    Run V9 experiment with explicit decay (baseline).

    Args:
        decay: Decay parameter (V9 optimal is 0.10)
        num_ticks: Number of ticks to run
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = RenormalizationConfig()
    config.num_ticks = num_ticks

    if verbose:
        print(f"\n{'='*60}")
        print(f"V9 BASELINE: decay={decay}")
        print(f"{'='*60}")

    # Initialize
    grid = PlanckGrid(config.grid_width, config.grid_height)

    # V9 gamma well system (original)
    gamma_system = GammaWellSystem(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # V9 history committer WITH decay
    history_committer = GammaHistoryCommitter(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        decay=decay
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
                "history_max": hist_state["history_max"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f}±{stats['r_std']:.2f}, "
                      f"E={stats['total_energy']}, hist_max={hist_state['history_max']:.1f}")

    elapsed = time.time() - start_time

    final_stats = compute_cloud_stats(grid, cloud_patterns, center)
    final_history = history_committer.get_state()

    # Stability metrics
    late_history = [h for h in history if h["tick"] >= config.stability_measurement_start]
    stability_metrics = {}
    if late_history:
        stability_metrics = {
            "r_std_mean": float(np.mean([h["r_std"] for h in late_history])),
            "r_mean_mean": float(np.mean([h["r_mean"] for h in late_history])),
            "energy_mean": float(np.mean([h["energy"] for h in late_history])),
        }

    if verbose:
        print(f"\nFinal: r={final_stats['r_mean']:.2f}±{final_stats['r_std']:.2f}")
        if stability_metrics:
            print(f"Stability: r_std_mean={stability_metrics['r_std_mean']:.3f}")
        print(f"Time: {elapsed:.1f}s")

    return {
        "method": "v9_decay",
        "decay": decay,
        "final_stats": final_stats,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
    }


def run_v10_normalization(
    norm_type: str,
    norm_scale: float = 1000.0,
    num_ticks: int = 2000,
    verbose: bool = True
) -> Dict:
    """
    Run V10 experiment with renormalization.

    Args:
        norm_type: 'global_sum', 'time_based', or 'local_gamma'
        norm_scale: Normalization scale factor
        num_ticks: Number of ticks to run
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = RenormalizationConfig()
    config.num_ticks = num_ticks
    config.normalization_type = norm_type
    config.normalization_scale = norm_scale

    if verbose:
        print(f"\n{'='*60}")
        print(f"V10 NORMALIZATION: {norm_type} (scale={norm_scale})")
        print(f"{'='*60}")

    grid = PlanckGrid(config.grid_width, config.grid_height)

    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # V10 history committer WITHOUT decay
    history_committer = GammaHistoryCommitterV10(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        normalization_type=norm_type,
        normalization_scale=norm_scale
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
                "effective_norm_factor": hist_state["effective_norm_factor"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f}±{stats['r_std']:.2f}, "
                      f"E={stats['total_energy']}, norm_max={hist_state['normalized_max']:.2f}")

    elapsed = time.time() - start_time

    final_stats = compute_cloud_stats(grid, cloud_patterns, center)
    final_history = history_committer.get_state()

    late_history = [h for h in history if h["tick"] >= config.stability_measurement_start]
    stability_metrics = {}
    if late_history:
        stability_metrics = {
            "r_std_mean": float(np.mean([h["r_std"] for h in late_history])),
            "r_mean_mean": float(np.mean([h["r_mean"] for h in late_history])),
            "energy_mean": float(np.mean([h["energy"] for h in late_history])),
        }

    if verbose:
        print(f"\nFinal: r={final_stats['r_mean']:.2f}±{final_stats['r_std']:.2f}")
        if stability_metrics:
            print(f"Stability: r_std_mean={stability_metrics['r_std_mean']:.3f}")
        print(f"Effective norm factor: {final_history['effective_norm_factor']:.1f}")
        print(f"Time: {elapsed:.1f}s")

    return {
        "method": f"v10_{norm_type}",
        "normalization_type": norm_type,
        "normalization_scale": norm_scale,
        "final_stats": final_stats,
        "final_history": final_history,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
    }


def run_comparison(num_ticks: int = 2000, verbose: bool = True) -> Dict:
    """
    Run full comparison: V9 baseline vs V10 normalization approaches.

    Returns:
        Combined results dictionary
    """
    print("=" * 70)
    print("V10 vs V9 COMPARISON EXPERIMENT")
    print("=" * 70)
    print("Comparing V9 (decay=0.10) against V10 normalization approaches")
    print()

    all_results = {}
    summary = []

    # V9 baseline
    v9_results = run_v9_baseline(decay=0.10, num_ticks=num_ticks, verbose=verbose)
    all_results["v9_baseline"] = v9_results
    summary.append({
        "method": "V9 decay=0.10",
        "r_mean": v9_results["final_stats"]["r_mean"],
        "r_std": v9_results["final_stats"]["r_std"],
        "energy": v9_results["final_stats"]["total_energy"],
        "r_std_stability": v9_results["stability_metrics"].get("r_std_mean", -1),
    })

    # V10 normalization approaches
    for norm_type in ['global_sum', 'time_based', 'local_gamma']:
        v10_results = run_v10_normalization(
            norm_type,
            norm_scale=1000.0,
            num_ticks=num_ticks,
            verbose=verbose
        )
        all_results[f"v10_{norm_type}"] = v10_results
        summary.append({
            "method": f"V10 {norm_type}",
            "r_mean": v10_results["final_stats"]["r_mean"],
            "r_std": v10_results["final_stats"]["r_std"],
            "energy": v10_results["final_stats"]["total_energy"],
            "r_std_stability": v10_results["stability_metrics"].get("r_std_mean", -1),
        })

    # Print comparison table
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Method':>20} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>8} | {'Stability':>10}")
    print("-" * 70)
    for row in summary:
        stability = row['r_std_stability']
        stability_str = f"{stability:.3f}" if stability >= 0 else "N/A"
        print(f"{row['method']:>20} | {row['r_mean']:>8.2f} | {row['r_std']:>8.3f} | "
              f"{row['energy']:>8d} | {stability_str:>10}")

    # Find best V10 approach
    v10_methods = [s for s in summary if s['method'].startswith('V10')]
    if v10_methods:
        best_v10 = min(v10_methods, key=lambda x: x['r_std_stability'] if x['r_std_stability'] >= 0 else float('inf'))
        v9_stability = summary[0]['r_std_stability']

        print(f"\nBest V10 approach: {best_v10['method']}")
        if v9_stability >= 0 and best_v10['r_std_stability'] >= 0:
            if v9_stability > 0:
                ratio = best_v10['r_std_stability'] / v9_stability
                print(f"Stability ratio (V10/V9): {ratio:.2f}")
                if ratio < 1.2:
                    print("SUCCESS: V10 achieves comparable stability without explicit decay!")
                else:
                    print("NOTE: V10 stability is lower than V9 baseline")
            else:
                # V9 has perfect stability (r_std = 0)
                if best_v10['r_std_stability'] < 0.1:
                    print("SUCCESS: V10 achieves comparable stability (both near-perfect)!")
                else:
                    print(f"V9 achieved perfect stability; V10 stability: {best_v10['r_std_stability']:.3f}")

    return {
        "all_results": all_results,
        "summary": summary,
    }


def main():
    """Run comparison experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="V10 vs V9 Comparison")
    parser.add_argument("--ticks", type=int, default=2000, help="Number of ticks")
    parser.add_argument("--output", type=str, default="results/comparison.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    results = run_comparison(num_ticks=args.ticks, verbose=not args.quiet)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {args.output}")


if __name__ == "__main__":
    main()
