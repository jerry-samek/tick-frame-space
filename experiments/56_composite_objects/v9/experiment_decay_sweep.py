"""
V9 Experiment: Decay Sweep

Test gamma_history_decay values from 0.1 to 0.9 to find the optimal
memory persistence for stable, physically accurate confinement.

Metrics tracked:
- Cloud r_mean and r_std over time (stability)
- Energy retention
- History layer max/mean (memory accumulation)
- Time to reach equilibrium

Physics question:
- How much "memory" should spacetime have?
- Does fading memory produce more realistic dynamics?
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

from gamma_wells import GammaWellSystem
from gamma_history import GammaHistoryCommitter
from config_v9 import DecaySweepConfig, DECAY_VALUES, create_decay_config


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


def run_single_decay_experiment(decay: float, verbose: bool = True) -> Dict:
    """
    Run experiment with a single decay value.

    Args:
        decay: The gamma_history_decay value to test
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = create_decay_config(decay)

    if verbose:
        print(f"\n{'='*60}")
        print(f"DECAY = {decay:.1f}")
        print(f"{'='*60}")

    # Initialize
    grid = PlanckGrid(config.grid_width, config.grid_height)

    # Gamma well system (target only, no projectile)
    gamma_system = GammaWellSystem(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # History committer with specified decay
    history_committer = GammaHistoryCommitter(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        decay=decay
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
            commit_history.append({
                "tick": tick,
                "commit_number": commit_stats["commit_number"],
                "history_max": commit_stats["history_max"],
                "history_mean": commit_stats["history_mean"],
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
                "history_max": hist_state["history_max"],
                "history_mean": hist_state["history_mean"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f}±{stats['r_std']:.2f}, "
                      f"E={stats['total_energy']}, "
                      f"hist_max={hist_state['history_max']:.1f}")

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
        "decay": decay,
        "config": {
            "num_ticks": config.num_ticks,
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "n_patterns": config.n_patterns,
            "target_gamma_k": config.target_gamma_k,
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
        print(f"Stability (late): r_std_mean={stability_metrics.get('r_std_mean', 'N/A'):.3f}")
        print(f"History: max={final_history['history_max']:.1f}, mean={final_history['history_mean']:.3f}")
        print(f"Time: {elapsed:.1f}s")

    return results


def run_decay_sweep(verbose: bool = True) -> Dict:
    """
    Run full decay sweep across all values.

    Returns:
        Combined results dictionary
    """
    print("=" * 70)
    print("V9 DECAY SWEEP EXPERIMENT")
    print("=" * 70)
    print(f"Testing decay values: {DECAY_VALUES}")
    print()

    all_results = {}
    summary = []

    for decay in DECAY_VALUES:
        results = run_single_decay_experiment(decay, verbose=verbose)
        all_results[f"decay_{decay}"] = results

        # Summary row
        summary.append({
            "decay": decay,
            "r_mean_final": results["final_stats"]["r_mean"],
            "r_std_final": results["final_stats"]["r_std"],
            "energy_final": results["final_stats"]["total_energy"],
            "r_std_stability": results["stability_metrics"].get("r_std_mean", -1),
            "history_max": results["final_history"]["history_max"],
            "history_mean": results["final_history"]["history_mean"],
        })

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"{'Decay':>6} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>8} | {'Stab(r_std)':>11} | {'Hist Max':>10}")
    print("-" * 70)
    for row in summary:
        print(f"{row['decay']:>6.1f} | {row['r_mean_final']:>8.2f} | {row['r_std_final']:>8.3f} | "
              f"{row['energy_final']:>8d} | {row['r_std_stability']:>11.3f} | {row['history_max']:>10.1f}")

    # Find optimal decay
    # Criteria: Low r_std_stability (stable), reasonable energy, history not saturated
    best_stability = min(summary, key=lambda x: x["r_std_stability"] if x["r_std_stability"] >= 0 else float('inf'))
    print(f"\nMost stable (lowest r_std variation): decay={best_stability['decay']}")

    return {
        "all_results": all_results,
        "summary": summary,
        "best_stability": best_stability,
    }


def main():
    """Run decay sweep experiment."""
    import argparse

    parser = argparse.ArgumentParser(description="V9 Decay Sweep Experiment")
    parser.add_argument("--single", type=float, help="Run single decay value only")
    parser.add_argument("--output", type=str, default="results/decay_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.single is not None:
        results = run_single_decay_experiment(args.single, verbose=not args.quiet)
        output_file = f"results/decay_{args.single}.json"
    else:
        results = run_decay_sweep(verbose=not args.quiet)
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
