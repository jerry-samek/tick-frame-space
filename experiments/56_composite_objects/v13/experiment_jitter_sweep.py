"""
V13 Jitter Sweep Experiment: Is Jitter Fundamental?

Investigates whether jitter strength 0.119 is fundamental or emergent.

Key questions:
1. What happens at jitter=0? (No randomness -> collapse?)
2. What happens at jitter=0.5? (Maximum symmetric -> dispersion?)
3. Is there a phase transition? (Critical point?)
4. Is 0.119 special or arbitrary within a stable range?

If jitter is fundamental, it should be 0 or 1.
If it's emergent, 0.119 might be within a stable range.

Author: V13 Jitter Investigation
Date: 2026-01-31
"""

import sys
import os
import json
import time
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from multi_layer_grid import MultiLayerGrid
from config_v13 import create_config
from layered_evolution import LayeredEvolution
from experiment_v13 import compute_spatial_distribution, run_v13_experiment


def classify_state(r_norm: float, drift: float) -> str:
    """Classify the final state based on r_norm and drift.

    Args:
        r_norm: Normalized mean radius
        drift: Standard deviation of r_norm over late history

    Returns:
        State classification string
    """
    if r_norm < 0.02:
        return "COLLAPSED"
    elif r_norm > 0.4:
        return "DISPERSED"
    elif drift > 0.05:
        return "UNSTABLE"
    else:
        return "STABLE"


def run_jitter_sweep(
    jitter_values: List[float],
    grid_size: int = 100,
    num_ticks: int = 500,
    random_seed: int = 42,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run experiment for multiple jitter values.

    Args:
        jitter_values: List of jitter strengths to test
        grid_size: Grid dimension
        num_ticks: Ticks per experiment
        random_seed: Random seed (same for all runs)
        verbose: Print progress

    Returns:
        Sweep results dictionary
    """
    if verbose:
        print("=" * 70)
        print("JITTER SWEEP EXPERIMENT: Is Jitter Fundamental?")
        print("=" * 70)
        print(f"Grid size: {grid_size}")
        print(f"Ticks per experiment: {num_ticks}")
        print(f"Jitter values: {len(jitter_values)} ({min(jitter_values):.3f} to {max(jitter_values):.3f})")
        print("-" * 70)

    results = []
    start_time = time.time()

    for i, jitter in enumerate(jitter_values):
        if verbose:
            print(f"\n[{i+1}/{len(jitter_values)}] Testing jitter={jitter:.3f}...")

        # Run experiment
        config = create_config(
            grid_size=grid_size,
            jitter_strength=jitter,
            random_seed=random_seed
        )

        result = run_v13_experiment(
            config,
            num_ticks=num_ticks,
            verbose_interval=num_ticks,  # Only print final
            verbose=False
        )

        # Extract key metrics
        r_norm = result["final_stats"]["r_mean_norm"]
        drift = result["stability_metrics"].get("drift", 0.0)
        state = classify_state(r_norm, drift)

        record = {
            "jitter": jitter,
            "r_norm": r_norm,
            "r_std": result["final_stats"]["r_std"],
            "entity_count": result["final_stats"]["entity_count"],
            "drift": drift,
            "state": state,
            "elapsed": result["elapsed_seconds"],
        }
        results.append(record)

        if verbose:
            print(f"    r_norm={r_norm:.4f}, drift={drift:.6f}, state={state}")

    elapsed = time.time() - start_time

    # Analyze results
    stable_range = [r for r in results if r["state"] == "STABLE"]
    collapsed = [r for r in results if r["state"] == "COLLAPSED"]
    dispersed = [r for r in results if r["state"] == "DISPERSED"]

    # Find phase transitions
    transitions = []
    for i in range(1, len(results)):
        if results[i]["state"] != results[i-1]["state"]:
            transitions.append({
                "from_jitter": results[i-1]["jitter"],
                "to_jitter": results[i]["jitter"],
                "from_state": results[i-1]["state"],
                "to_state": results[i]["state"],
            })

    analysis = {
        "stable_count": len(stable_range),
        "collapsed_count": len(collapsed),
        "dispersed_count": len(dispersed),
        "stable_jitter_range": [
            min(r["jitter"] for r in stable_range) if stable_range else None,
            max(r["jitter"] for r in stable_range) if stable_range else None,
        ],
        "transitions": transitions,
        "is_0119_special": False,  # Will be determined below
    }

    # Check if 0.119 is special
    if stable_range:
        jitter_0119 = [r for r in results if abs(r["jitter"] - 0.119) < 0.01]
        if jitter_0119:
            # Check if 0.119 is at a boundary or in the middle
            stable_min = min(r["jitter"] for r in stable_range)
            stable_max = max(r["jitter"] for r in stable_range)
            if stable_min < 0.119 < stable_max:
                analysis["is_0119_special"] = False
                analysis["0119_position"] = "middle_of_stable_range"
            else:
                analysis["is_0119_special"] = True
                analysis["0119_position"] = "boundary_of_stable_range"

    if verbose:
        print("\n" + "=" * 70)
        print("SWEEP RESULTS")
        print("=" * 70)
        print(f"Total experiments: {len(results)}")
        print(f"Stable: {analysis['stable_count']}")
        print(f"Collapsed: {analysis['collapsed_count']}")
        print(f"Dispersed: {analysis['dispersed_count']}")
        if analysis["stable_jitter_range"][0] is not None:
            print(f"Stable range: [{analysis['stable_jitter_range'][0]:.3f}, {analysis['stable_jitter_range'][1]:.3f}]")
        print(f"\nPhase transitions: {len(transitions)}")
        for t in transitions:
            print(f"  {t['from_state']} -> {t['to_state']} at jitter={t['from_jitter']:.3f}->{t['to_jitter']:.3f}")
        print(f"\nIs 0.119 special? {analysis['is_0119_special']}")
        if "0119_position" in analysis:
            print(f"  Position: {analysis['0119_position']}")
        print(f"\nTotal time: {elapsed:.1f}s")

    return {
        "sweep_params": {
            "grid_size": grid_size,
            "num_ticks": num_ticks,
            "random_seed": random_seed,
            "jitter_values": jitter_values,
        },
        "results": results,
        "analysis": analysis,
        "elapsed_seconds": elapsed,
    }


def plot_sweep_results(sweep_data: Dict[str, Any], output_path: str = None):
    """Generate plots from sweep results.

    Args:
        sweep_data: Results from run_jitter_sweep
        output_path: Path to save plot (optional)
    """
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not available, skipping plots")
        return

    results = sweep_data["results"]

    jitters = [r["jitter"] for r in results]
    r_norms = [r["r_norm"] for r in results]
    drifts = [r["drift"] for r in results]
    states = [r["state"] for r in results]

    # Color map for states
    state_colors = {
        "STABLE": "green",
        "COLLAPSED": "red",
        "DISPERSED": "blue",
        "UNSTABLE": "orange",
    }
    colors = [state_colors.get(s, "gray") for s in states]

    fig, axes = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

    # Top: r_norm vs jitter
    ax1 = axes[0]
    ax1.scatter(jitters, r_norms, c=colors, s=50, zorder=3)
    ax1.axvline(x=0.119, color="purple", linestyle="--", alpha=0.7, label="0.119 (tuned)")
    ax1.axhline(y=0.02, color="red", linestyle=":", alpha=0.5, label="collapse threshold")
    ax1.axhline(y=0.4, color="blue", linestyle=":", alpha=0.5, label="dispersion threshold")
    ax1.set_ylabel("r_norm (normalized radius)")
    ax1.set_title("Jitter Sweep: Is 0.119 Fundamental?")
    ax1.legend(loc="upper right")
    ax1.grid(True, alpha=0.3)

    # Bottom: drift vs jitter
    ax2 = axes[1]
    ax2.scatter(jitters, drifts, c=colors, s=50, zorder=3)
    ax2.axvline(x=0.119, color="purple", linestyle="--", alpha=0.7)
    ax2.axhline(y=0.05, color="orange", linestyle=":", alpha=0.5, label="instability threshold")
    ax2.set_xlabel("Jitter Strength")
    ax2.set_ylabel("Drift (stability)")
    ax2.legend(loc="upper right")
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()

    if output_path:
        plt.savefig(output_path, dpi=150)
        print(f"Plot saved to {output_path}")
    else:
        plt.show()


def main():
    """Run jitter sweep experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="Jitter Sweep: Is Jitter Fundamental?",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_jitter_sweep.py                    # Default sweep
  python experiment_jitter_sweep.py --steps 41         # Finer resolution
  python experiment_jitter_sweep.py --ticks 1000       # Longer runs
  python experiment_jitter_sweep.py --binary-only      # Test only 0, 0.5, 0.119
        """
    )
    parser.add_argument("--ticks", type=int, default=500,
                        help="Ticks per experiment (default: 500)")
    parser.add_argument("--grid", type=int, default=100,
                        help="Grid size (default: 100)")
    parser.add_argument("--steps", type=int, default=21,
                        help="Number of jitter values to test (default: 21)")
    parser.add_argument("--min-jitter", type=float, default=0.0,
                        help="Minimum jitter value (default: 0.0)")
    parser.add_argument("--max-jitter", type=float, default=0.5,
                        help="Maximum jitter value (default: 0.5)")
    parser.add_argument("--binary-only", action="store_true",
                        help="Test only fundamental values: 0, 0.5, 0.119")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed (default: 42)")
    parser.add_argument("--output", type=str, default="results/jitter_sweep.json",
                        help="Output JSON file")
    parser.add_argument("--plot", type=str, default=None,
                        help="Output plot file (optional)")
    parser.add_argument("--quiet", action="store_true",
                        help="Less verbose output")

    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    # Determine jitter values to test
    if args.binary_only:
        jitter_values = [0.0, 0.119, 0.5]
    else:
        jitter_values = list(np.linspace(args.min_jitter, args.max_jitter, args.steps))
        # Ensure 0.119 is included
        if 0.119 not in jitter_values:
            jitter_values.append(0.119)
            jitter_values.sort()

    # Run sweep
    sweep_data = run_jitter_sweep(
        jitter_values=jitter_values,
        grid_size=args.grid,
        num_ticks=args.ticks,
        random_seed=args.seed,
        verbose=not args.quiet
    )

    # Save results
    with open(args.output, "w") as f:
        json.dump(sweep_data, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else str(x))

    print(f"\nResults saved to {args.output}")

    # Generate plot if requested
    if args.plot:
        plot_sweep_results(sweep_data, args.plot)

    # Print conclusion
    analysis = sweep_data["analysis"]
    print("\n" + "=" * 70)
    print("CONCLUSION")
    print("=" * 70)

    if analysis["collapsed_count"] > 0 and analysis["dispersed_count"] > 0:
        print("FINDING: Phase transitions exist!")
        print(f"  - Collapse occurs at low jitter (below ~{analysis['stable_jitter_range'][0]:.3f})")
        print(f"  - Dispersion occurs at high jitter (above ~{analysis['stable_jitter_range'][1]:.3f})")

        if not analysis["is_0119_special"]:
            print("\nIMPLICATION: 0.119 is NOT fundamental!")
            print("  - It's within a stable range, not at a special point")
            print("  - Any value in the stable range would work")
            print("  - Jitter is EMERGENT from the balance of push/pull forces")
        else:
            print("\nIMPLICATION: 0.119 may be near a critical point")
            print("  - Further investigation needed")
    elif analysis["stable_count"] == len(sweep_data["results"]):
        print("FINDING: All tested values are stable")
        print("  - No phase transitions detected in this range")
        print("  - Need to test wider range or jitter > 0.5")
    else:
        print("FINDING: Unexpected pattern")
        print("  - Review results manually")


if __name__ == "__main__":
    main()
