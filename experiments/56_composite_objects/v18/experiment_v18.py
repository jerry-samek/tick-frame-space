"""
V18 Experiments - Test suite for unified composite physics.

Tests:
1. Quick Test: Basic functionality (100 ticks)
2. Standard Test: Normal experiment (1000 ticks)
3. Long Run: Extended experiment (10000 ticks)

Author: V18 Implementation
Date: 2026-02-04
"""

import argparse
import json
import time
from pathlib import Path
from typing import Dict, Any
import sys

# Add parent directory for imports
sys.path.insert(0, str(Path(__file__).parent))

from evolution_v18 import TickEvolution_V18


def run_quick_test(seed: int = 42, verbose: bool = True) -> Dict[str, Any]:
    """Run quick test (100 ticks).

    Args:
        seed: Random seed
        verbose: Print progress

    Returns:
        Results dict
    """
    if verbose:
        print("=" * 70)
        print("V18 Quick Test (100 ticks)")
        print("=" * 70)

    evolution = TickEvolution_V18(max_ticks=100, random_seed=seed)

    start_time = time.time()
    history = evolution.evolve_n_ticks(100, progress_interval=20, verbose=verbose)
    elapsed = time.time() - start_time

    stats = evolution.get_statistics()
    stats["elapsed_seconds"] = elapsed
    stats["ticks_per_second"] = 100 / elapsed

    if verbose:
        print()
        print("Results:")
        print(f"  Elapsed: {elapsed:.2f}s ({100/elapsed:.1f} ticks/s)")
        print(f"  Processes: {stats['process_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

    return {
        "test": "quick",
        "stats": stats,
        "history": history,
    }


def run_standard_test(seed: int = 42, verbose: bool = True) -> Dict[str, Any]:
    """Run standard test (1000 ticks).

    Args:
        seed: Random seed
        verbose: Print progress

    Returns:
        Results dict
    """
    if verbose:
        print("=" * 70)
        print("V18 Standard Test (1000 ticks)")
        print("=" * 70)

    evolution = TickEvolution_V18(max_ticks=1000, random_seed=seed)

    start_time = time.time()
    history = evolution.evolve_n_ticks(1000, progress_interval=100, verbose=verbose)
    elapsed = time.time() - start_time

    stats = evolution.get_statistics()
    stats["elapsed_seconds"] = elapsed
    stats["ticks_per_second"] = 1000 / elapsed

    if verbose:
        print()
        print("Results:")
        print(f"  Elapsed: {elapsed:.2f}s ({1000/elapsed:.1f} ticks/s)")
        print(f"  Processes: {stats['process_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

    return {
        "test": "standard",
        "stats": stats,
        "history": history,
    }


def run_long_test(ticks: int = 10000, seed: int = 42, verbose: bool = True) -> Dict[str, Any]:
    """Run long test.

    Args:
        ticks: Number of ticks
        seed: Random seed
        verbose: Print progress

    Returns:
        Results dict
    """
    if verbose:
        print("=" * 70)
        print(f"V18 Long Run Test ({ticks} ticks)")
        print("=" * 70)

    evolution = TickEvolution_V18(max_ticks=ticks, random_seed=seed)

    start_time = time.time()
    history = evolution.evolve_n_ticks(ticks, progress_interval=500, verbose=verbose)
    elapsed = time.time() - start_time

    stats = evolution.get_statistics()
    stats["elapsed_seconds"] = elapsed
    stats["ticks_per_second"] = ticks / elapsed

    if verbose:
        print()
        print("Results:")
        print(f"  Elapsed: {elapsed:.2f}s ({ticks/elapsed:.1f} ticks/s)")
        print(f"  Processes: {stats['process_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

    return {
        "test": "longrun",
        "ticks": ticks,
        "stats": stats,
        "history": history,
    }


def save_results(results: Dict[str, Any], filename: str):
    """Save results to JSON file.

    Args:
        results: Results dict
        filename: Output filename
    """
    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    filepath = results_dir / filename

    # Convert non-serializable types
    import numpy as np

    def convert(obj):
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, tuple):
            return list(obj)
        return obj

    def deep_convert(obj):
        if isinstance(obj, dict):
            return {k: deep_convert(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [deep_convert(v) for v in obj]
        return convert(obj)

    serializable = deep_convert(results)

    with open(filepath, 'w') as f:
        json.dump(serializable, f, indent=2)

    print(f"Saved results to: {filepath}")


def main():
    """Run experiments based on command line arguments."""
    parser = argparse.ArgumentParser(description="V18 Unified Composite Physics Experiments")
    parser.add_argument(
        "--test",
        choices=["quick", "standard", "longrun", "all"],
        default="quick",
        help="Test to run (default: quick)"
    )
    parser.add_argument(
        "--ticks",
        type=int,
        default=10000,
        help="Number of ticks for longrun test (default: 10000)"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed (default: 42)"
    )
    parser.add_argument(
        "--save",
        action="store_true",
        help="Save results to JSON file"
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Minimal output"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output (same as default)"
    )

    args = parser.parse_args()
    verbose = not args.quiet

    if args.test == "quick":
        results = run_quick_test(seed=args.seed, verbose=verbose)
    elif args.test == "standard":
        results = run_standard_test(seed=args.seed, verbose=verbose)
    elif args.test == "longrun":
        results = run_long_test(ticks=args.ticks, seed=args.seed, verbose=verbose)
    elif args.test == "all":
        all_results = {}
        all_results["quick"] = run_quick_test(seed=args.seed, verbose=verbose)
        all_results["standard"] = run_standard_test(seed=args.seed, verbose=verbose)
        all_results["longrun"] = run_long_test(ticks=args.ticks, seed=args.seed, verbose=verbose)
        results = all_results

    if args.save:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"v18_{args.test}_{timestamp}.json"
        save_results(results, filename)


if __name__ == "__main__":
    main()
