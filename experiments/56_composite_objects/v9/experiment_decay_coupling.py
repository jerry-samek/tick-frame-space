"""
V9 Experiment: Jitter-Decay Coupling Test

Tests the hypothesis that optimal decay equals jitter strength.

Discovery:
- Jitter strength (V6/V7 optimal): 0.119
- Critical decay threshold (V9): ~0.12-0.13

Hypothesis: These are the SAME physical constant - the "coherence scale"
of the tick-frame substrate.

Physical interpretation:
- Jitter = spatial fluctuation amplitude per tick
- Decay = temporal memory loss per window
- If decay ≈ jitter: Natural equilibrium at the noise floor

This experiment tests:
- decay = 0.10 (below jitter, stable baseline)
- decay = 0.119 (equals jitter, hypothesized optimal)
- decay = 0.30 (above jitter, collapsed baseline)
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
from config_v9 import DecaySweepConfig, create_decay_config

# The critical values to test
JITTER_STRENGTH = 0.119  # From V6/V7 optimal tuning
COUPLING_TEST_DECAYS = [0.10, JITTER_STRENGTH, 0.30]


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


def run_coupling_experiment(decay: float, jitter_override: float = None, verbose: bool = True) -> Dict:
    """
    Run experiment with a single decay value.

    Args:
        decay: The gamma_history_decay value to test
        jitter_override: Optional jitter value (default: use JITTER_STRENGTH)
        verbose: Print progress

    Returns:
        Results dictionary
    """
    config = create_decay_config(decay)

    # Use override jitter if provided
    jitter_value = jitter_override if jitter_override is not None else JITTER_STRENGTH

    # Determine relationship to jitter
    if decay < jitter_value - 0.01:
        relationship = "BELOW jitter"
    elif decay > jitter_value + 0.01:
        relationship = "ABOVE jitter"
    else:
        relationship = "EQUALS jitter"

    # Compute ratio
    ratio = decay / jitter_value if jitter_value > 0 else 0

    if verbose:
        print(f"\n{'='*60}")
        print(f"DECAY = {decay:.3f} ({relationship})")
        print(f"Jitter = {jitter_value:.3f}")
        print(f"Ratio (decay/jitter) = {ratio:.3f}")
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

    # Evolution (use override jitter if provided)
    jitter = PlanckJitter.create_symmetric(jitter_value, seed=config.random_seed)
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
        "jitter": jitter_value,
        "ratio": ratio,
        "relationship": relationship,
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


def run_coupling_test(verbose: bool = True) -> Dict:
    """
    Run the full jitter-decay coupling test.

    Tests three decay values:
    - 0.10: Below jitter (stable baseline)
    - 0.119: Equals jitter (hypothesized optimal)
    - 0.30: Above jitter (collapsed baseline)

    Returns:
        Combined results dictionary
    """
    print("=" * 70)
    print("JITTER-DECAY COUPLING TEST")
    print("=" * 70)
    print(f"Jitter strength: {JITTER_STRENGTH}")
    print(f"Testing decay values: {COUPLING_TEST_DECAYS}")
    print()
    print("Hypothesis: Optimal decay equals jitter strength")
    print("  - decay < jitter: Stable but over-rigid (too much memory)")
    print("  - decay = jitter: Natural equilibrium at noise floor")
    print("  - decay > jitter: Collapse (memory fades too fast)")
    print()

    all_results = {}
    summary = []

    for decay in COUPLING_TEST_DECAYS:
        results = run_coupling_experiment(decay, verbose=verbose)
        all_results[f"decay_{decay:.3f}"] = results

        # Summary row
        summary.append({
            "decay": decay,
            "relationship": results["relationship"],
            "r_mean_final": results["final_stats"]["r_mean"],
            "r_std_final": results["final_stats"]["r_std"],
            "energy_final": results["final_stats"]["total_energy"],
            "r_std_stability": results["stability_metrics"].get("r_std_mean", -1),
            "history_max": results["final_history"]["history_max"],
        })

    # Print summary table
    print("\n" + "=" * 70)
    print("COUPLING TEST SUMMARY")
    print("=" * 70)
    print(f"{'Decay':>8} | {'Relation':>14} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>8} | {'Hist Max':>10}")
    print("-" * 70)
    for row in summary:
        print(f"{row['decay']:>8.3f} | {row['relationship']:>14} | {row['r_mean_final']:>8.2f} | "
              f"{row['r_std_final']:>8.3f} | {row['energy_final']:>8d} | {row['history_max']:>10.1f}")

    # Analysis
    print("\n" + "=" * 70)
    print("ANALYSIS")
    print("=" * 70)

    # Check if decay=jitter is optimal
    jitter_result = next((r for r in summary if abs(r["decay"] - JITTER_STRENGTH) < 0.001), None)
    below_result = next((r for r in summary if r["decay"] == 0.10), None)
    above_result = next((r for r in summary if r["decay"] == 0.30), None)

    if jitter_result and below_result and above_result:
        print(f"\nStructure preservation (r_mean):")
        print(f"  decay=0.10:  r={below_result['r_mean_final']:.2f}")
        print(f"  decay=0.119: r={jitter_result['r_mean_final']:.2f}")
        print(f"  decay=0.30:  r={above_result['r_mean_final']:.2f}")

        print(f"\nEnergy retention:")
        print(f"  decay=0.10:  E={below_result['energy_final']}")
        print(f"  decay=0.119: E={jitter_result['energy_final']}")
        print(f"  decay=0.30:  E={above_result['energy_final']}")

        # Determine if coupling hypothesis is supported
        jitter_stable = jitter_result['r_mean_final'] > 1.0
        below_stable = below_result['r_mean_final'] > 1.0
        above_collapsed = above_result['r_mean_final'] < 1.0

        print(f"\nHypothesis validation:")
        print(f"  decay=0.10 stable?    {below_stable} (expected: True)")
        print(f"  decay=0.119 stable?   {jitter_stable} (hypothesis: True, optimal)")
        print(f"  decay=0.30 collapsed? {above_collapsed} (expected: True)")

        if jitter_stable and below_stable and above_collapsed:
            # Compare energy between jitter and below
            if jitter_result['energy_final'] >= below_result['energy_final']:
                print("\n>>> HYPOTHESIS SUPPORTED: decay=jitter produces equal or better energy")
                print(">>> This suggests jitter and decay are the SAME physical constant")
            else:
                energy_diff = below_result['energy_final'] - jitter_result['energy_final']
                energy_pct = 100 * energy_diff / below_result['energy_final']
                print(f"\n>>> HYPOTHESIS PARTIALLY SUPPORTED: decay=jitter is stable")
                print(f">>> But decay=0.10 has {energy_pct:.1f}% more energy")
                print(">>> Coupling exists but optimal point may be slightly below jitter")
        elif not jitter_stable:
            print("\n>>> HYPOTHESIS REJECTED: decay=jitter causes collapse")
            print(">>> The critical threshold is slightly below jitter strength")
        else:
            print("\n>>> INCONCLUSIVE: Unexpected behavior in baseline values")

    return {
        "all_results": all_results,
        "summary": summary,
        "jitter_strength": JITTER_STRENGTH,
        "hypothesis": "decay = jitter produces optimal equilibrium",
    }


def main():
    """Run jitter-decay coupling experiment."""
    import argparse

    parser = argparse.ArgumentParser(description="V9 Jitter-Decay Coupling Test")
    parser.add_argument("--single", type=float, help="Run single decay value only")
    parser.add_argument("--jitter", type=float, help="Override jitter strength (default: 0.119)")
    parser.add_argument("--output", type=str, default="results/decay_coupling.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.single is not None:
        results = run_coupling_experiment(args.single, jitter_override=args.jitter, verbose=not args.quiet)
        jitter_str = f"_j{args.jitter:.2f}" if args.jitter else ""
        output_file = f"results/coupling_{args.single:.3f}{jitter_str}.json"
    else:
        results = run_coupling_test(verbose=not args.quiet)
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
