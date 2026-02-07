"""
V17 Experiments - Canvas Ontology with Sparse Storage

Experiments to validate V17 behavior and compare with V16.

Experiments:
1. Quick Test: Basic functionality (100 ticks)
2. Standard Run: Normal experiment (1000 ticks)
3. Long Run: Extended experiment (10000 ticks) - only possible with sparse storage
4. Memory Comparison: Compare memory usage with V16

Author: V17 Implementation
Date: 2026-02-01
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import List, Dict, Any

import numpy as np

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from config_v17 import Config17, QuickTestConfig, StandardConfig, LongRunConfig
from canvas import Canvas3D
from renderer import Renderer
from evolution import TickEvolution


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
        print("V17 Quick Test (100 ticks)")
        print("=" * 70)

    config = QuickTestConfig(random_seed=seed)
    evolution = TickEvolution(config)

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
        print(f"  Renderers: {stats['renderer_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Skip rate: {stats['skip_rate']:.2%}")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

    return {
        "test": "quick",
        "config": repr(config),
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
        print("V17 Standard Test (1000 ticks)")
        print("=" * 70)

    config = StandardConfig(random_seed=seed)
    evolution = TickEvolution(config)

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
        print(f"  Renderers: {stats['renderer_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Skip rate: {stats['skip_rate']:.2%}")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

    return {
        "test": "standard",
        "config": repr(config),
        "stats": stats,
        "history": history,
    }


def run_long_test(ticks: int = 10000, seed: int = 42, verbose: bool = True) -> Dict[str, Any]:
    """Run long test (10000+ ticks) - only possible with sparse storage.

    Args:
        ticks: Number of ticks
        seed: Random seed
        verbose: Print progress

    Returns:
        Results dict
    """
    if verbose:
        print("=" * 70)
        print(f"V17 Long Run Test ({ticks} ticks)")
        print("=" * 70)
        print("Note: This would be impossible with V16 dense storage!")
        print()

    config = LongRunConfig(random_seed=seed)
    config.max_ticks = ticks
    evolution = TickEvolution(config)

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
        print(f"  Renderers: {stats['renderer_count']}")
        print(f"  Painted cells: {stats['painted_cells']}")
        print(f"  Memory: {stats['memory_mb']:.2f} MB")
        print(f"  Skip rate: {stats['skip_rate']:.2%}")
        print(f"  Mean radius: {stats['r_mean']:.1f}")
        print()

        # Radial distribution
        print("Radial distribution (every 5 shells, first 50):")
        radial = evolution.canvas.get_radial_distribution()
        for r in sorted(radial.keys())[:50:5]:
            bar_len = int(radial[r] / 50)
            bar = "#" * bar_len
            print(f"  r={r:3d}: gamma={radial[r]:8.1f} {bar}")
        print()

    return {
        "test": "longrun",
        "ticks": ticks,
        "config": repr(config),
        "stats": stats,
        "history": history,
    }


def run_memory_test(verbose: bool = True) -> Dict[str, Any]:
    """Test memory scaling with tick count.

    Args:
        verbose: Print progress

    Returns:
        Results dict with memory measurements
    """
    if verbose:
        print("=" * 70)
        print("V17 Memory Scaling Test")
        print("=" * 70)

    config = Config17(max_ticks=5000, random_seed=42)
    evolution = TickEvolution(config)

    measurements = []
    checkpoints = [100, 250, 500, 1000, 2000, 3000, 4000, 5000]

    start_time = time.time()
    tick = 0

    for checkpoint in checkpoints:
        # Evolve to checkpoint
        while tick < checkpoint:
            evolution.evolve_one_tick()
            tick += 1

        stats = evolution.get_statistics()
        measurements.append({
            "tick": checkpoint,
            "renderers": stats["renderer_count"],
            "painted_cells": stats["painted_cells"],
            "memory_mb": stats["memory_mb"],
            "skip_rate": stats["skip_rate"],
            "r_mean": stats["r_mean"],
        })

        if verbose:
            print(f"  Tick {checkpoint:5d}: "
                  f"painted={stats['painted_cells']:6d}, "
                  f"mem={stats['memory_mb']:.2f}MB, "
                  f"r_mean={stats['r_mean']:.1f}")

    elapsed = time.time() - start_time

    if verbose:
        print()
        print("Memory scaling analysis:")
        for m in measurements:
            cells_per_tick = m["painted_cells"] / m["tick"]
            mb_per_tick = m["memory_mb"] / m["tick"] * 1000  # KB per tick
            print(f"  Tick {m['tick']:5d}: "
                  f"{cells_per_tick:.2f} cells/tick, "
                  f"{mb_per_tick:.2f} KB/tick")
        print()
        print(f"Total elapsed: {elapsed:.2f}s")
        print()

    return {
        "test": "memory",
        "measurements": measurements,
        "elapsed_seconds": elapsed,
    }


def run_pattern_test(seed: int = 42, verbose: bool = True) -> Dict[str, Any]:
    """Test pattern formation and stability.

    Args:
        seed: Random seed
        verbose: Print progress

    Returns:
        Results dict
    """
    if verbose:
        print("=" * 70)
        print("V17 Pattern Formation Test")
        print("=" * 70)

    config = StandardConfig(random_seed=seed)
    evolution = TickEvolution(config)

    # Track renderer positions over time
    position_history = []

    for tick in range(500):
        evolution.evolve_one_tick()

        if tick % 50 == 0:
            # Record renderer positions
            positions = {
                r.entity_id: r.last_paint_pos
                for r in evolution.renderers
            }
            position_history.append({
                "tick": tick,
                "positions": positions,
            })

    stats = evolution.get_statistics()

    # Analyze pattern stability
    if verbose:
        print()
        print("Renderer position analysis (sample of 10):")
        for r in evolution.renderers[:10]:
            x, y, z = r.last_paint_pos
            dist = np.sqrt(x**2 + y**2 + z**2)
            print(f"  Entity {r.entity_id:3d}: "
                  f"pos={r.last_paint_pos}, "
                  f"r={dist:.1f}, "
                  f"dilation={r.time_dilation_factor:.2f}")
        print()

        # Radial distribution
        print("Radial distribution (first 20 shells):")
        radial = evolution.canvas.get_radial_distribution()
        for r in sorted(radial.keys())[:20]:
            bar_len = int(radial[r] / 10)
            bar = "#" * bar_len
            print(f"  r={r:3d}: gamma={radial[r]:6.1f} {bar}")
        print()

        # Visualization
        print("Canvas XY slice at z=0:")
        print(evolution.canvas.visualize_slice_ascii("xy", 0, 31))
        print()

    return {
        "test": "pattern",
        "stats": stats,
        "position_history": position_history,
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

    # Deep convert
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
    parser = argparse.ArgumentParser(description="V17 Canvas Ontology Experiments")
    parser.add_argument(
        "--test",
        choices=["quick", "standard", "longrun", "memory", "pattern", "all"],
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

    args = parser.parse_args()
    verbose = not args.quiet

    if args.test == "quick":
        results = run_quick_test(seed=args.seed, verbose=verbose)
    elif args.test == "standard":
        results = run_standard_test(seed=args.seed, verbose=verbose)
    elif args.test == "longrun":
        results = run_long_test(ticks=args.ticks, seed=args.seed, verbose=verbose)
    elif args.test == "memory":
        results = run_memory_test(verbose=verbose)
    elif args.test == "pattern":
        results = run_pattern_test(seed=args.seed, verbose=verbose)
    elif args.test == "all":
        all_results = {}
        all_results["quick"] = run_quick_test(seed=args.seed, verbose=verbose)
        all_results["standard"] = run_standard_test(seed=args.seed, verbose=verbose)
        all_results["memory"] = run_memory_test(verbose=verbose)
        all_results["pattern"] = run_pattern_test(seed=args.seed, verbose=verbose)
        results = all_results

    if args.save:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"v17_{args.test}_{timestamp}.json"
        save_results(results, filename)


if __name__ == "__main__":
    main()
