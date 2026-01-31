"""
V9 Experiment: Fine-Grained Decay Scan

Find the exact critical threshold between stable (r~3) and collapsed (r=0) states.
Based on initial sweep: transition is between decay=0.1 (stable) and decay=0.2 (collapsed).

Test values: 0.01, 0.05, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20
"""

import sys
import os
import json
from pathlib import Path

# Add paths
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))

from experiment_decay_sweep import run_single_decay_experiment

# Fine-grained decay values around the critical threshold
FINEGRAINED_DECAY_VALUES = [0.01, 0.05, 0.08, 0.10, 0.12, 0.14, 0.16, 0.18, 0.20]


def run_finegrained_sweep(verbose: bool = True) -> dict:
    """Run fine-grained decay sweep."""
    print("=" * 70)
    print("V9 FINE-GRAINED DECAY SCAN")
    print("=" * 70)
    print(f"Testing decay values: {FINEGRAINED_DECAY_VALUES}")
    print("Looking for critical threshold between stable (r~3) and collapsed (r=0)")
    print()

    all_results = {}
    summary = []

    for decay in FINEGRAINED_DECAY_VALUES:
        results = run_single_decay_experiment(decay, verbose=verbose)
        all_results[f"decay_{decay}"] = results

        summary.append({
            "decay": decay,
            "r_mean_final": results["final_stats"]["r_mean"],
            "r_std_final": results["final_stats"]["r_std"],
            "energy_final": results["final_stats"]["total_energy"],
            "history_max": results["final_history"]["history_max"],
            "structured": results["final_stats"]["r_mean"] > 1.5,  # threshold for "structured"
        })

    # Print summary
    print("\n" + "=" * 70)
    print("FINE-GRAINED SUMMARY")
    print("=" * 70)
    print(f"{'Decay':>6} | {'r_mean':>8} | {'Energy':>8} | {'Hist Max':>10} | {'State':>10}")
    print("-" * 70)

    for row in summary:
        state = "STABLE" if row["structured"] else "COLLAPSED"
        print(f"{row['decay']:>6.2f} | {row['r_mean_final']:>8.2f} | "
              f"{row['energy_final']:>8d} | {row['history_max']:>10.1f} | {state:>10}")

    # Find critical threshold
    stable = [s for s in summary if s["structured"]]
    collapsed = [s for s in summary if not s["structured"]]

    if stable and collapsed:
        max_stable = max(s["decay"] for s in stable)
        min_collapsed = min(s["decay"] for s in collapsed)
        critical_threshold = (max_stable + min_collapsed) / 2
        print(f"\nCritical threshold: {max_stable} < decay_crit < {min_collapsed}")
        print(f"Estimated: decay_crit ~ {critical_threshold:.3f}")
    else:
        critical_threshold = None
        print("\nCould not determine critical threshold (all same state)")

    return {
        "all_results": all_results,
        "summary": summary,
        "critical_threshold": critical_threshold,
    }


def main():
    os.makedirs("results", exist_ok=True)

    results = run_finegrained_sweep(verbose=True)

    output_file = "results/decay_finegrained.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
