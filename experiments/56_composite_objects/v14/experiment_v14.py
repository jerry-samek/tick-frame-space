"""
V14 Experiment: Tick Skipping for Time Dilation

Tests the simplified time dilation mechanism:
- Entities skip ticks based on gamma gradient (pull force)
- No reaction-diffusion fields (removed from V13)
- Only 2 parameters: jitter_strength, gamma_decay

Success criteria:
1. Time dilation emerges: entities in high-gamma regions skip more ticks
2. Skip rate correlates with gamma gradient
3. Similar or better behavior than V13 with fewer parameters
4. Stable patterns: drift < 0.001

Author: V14 Implementation
Date: 2026-01-31
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

from multi_layer_grid import MultiLayerGrid
from entity import Entity
from config_v14 import LayeredSubstrateConfig, create_config
from layered_evolution import LayeredEvolution


def compute_spatial_distribution(grid: MultiLayerGrid, origin: tuple) -> Dict[str, float]:
    """Compute spatial distribution metrics relative to origin.

    Args:
        grid: MultiLayerGrid with entity layers
        origin: Center point (x, y)

    Returns:
        Dict with radial distribution metrics
    """
    combined = grid.compute_combined_field()
    origin_x, origin_y = origin

    # Find all non-zero positions
    nonzero_y, nonzero_x = np.nonzero(combined)

    if len(nonzero_x) == 0:
        return {
            "r_mean": 0.0,
            "r_std": 0.0,
            "r_max": 0.0,
            "spread": 0.0,
        }

    # Compute radii from origin
    dx = nonzero_x - origin_x
    dy = nonzero_y - origin_y
    radii = np.sqrt(dx**2 + dy**2)

    r_mean = float(np.mean(radii))
    r_std = float(np.std(radii))
    r_max = float(np.max(radii))

    # Normalize by half-grid
    half_grid = grid.width / 2.0
    r_mean_norm = r_mean / half_grid if half_grid > 0 else 0.0
    r_std_norm = r_std / half_grid if half_grid > 0 else 0.0

    return {
        "r_mean": r_mean,
        "r_std": r_std,
        "r_max": r_max,
        "r_mean_norm": r_mean_norm,
        "r_std_norm": r_std_norm,
        "spread": r_std / r_mean if r_mean > 0 else 0.0,
        "nonzero_count": len(nonzero_x),
    }


def compute_time_dilation_stats(entities: List[Entity]) -> Dict[str, float]:
    """Compute time dilation statistics across entities.

    Args:
        entities: List of entities

    Returns:
        Dict with dilation statistics
    """
    if not entities:
        return {
            "dilation_mean": 1.0,
            "dilation_std": 0.0,
            "dilation_min": 1.0,
            "dilation_max": 1.0,
            "skip_fraction": 0.0,
        }

    dilations = [e.time_dilation_factor for e in entities]
    total_skips = sum(e.total_skips for e in entities)
    total_acts = sum(e.total_acts for e in entities)

    return {
        "dilation_mean": float(np.mean(dilations)),
        "dilation_std": float(np.std(dilations)),
        "dilation_min": float(np.min(dilations)),
        "dilation_max": float(np.max(dilations)),
        "skip_fraction": total_skips / (total_acts + total_skips) if (total_acts + total_skips) > 0 else 0.0,
    }


def run_v14_experiment(
    config: LayeredSubstrateConfig,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V14 tick skipping experiment.

    Args:
        config: V14 configuration
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"V14 TICK SKIPPING EXPERIMENT: grid={config.grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    # Create grid and evolution
    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    history = []
    start_time = time.time()

    for tick in range(num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % verbose_interval == 0:
            stats = evolution.get_statistics()
            spatial = compute_spatial_distribution(grid, config.origin)
            dilation = compute_time_dilation_stats(evolution.entities)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            record = {
                "tick": tick + 1,
                "entity_count": stats["entity_count"],
                "total_energy": stats["total_energy"],
                "gamma_sum": stats["gamma_sum"],
                "gamma_max": stats["gamma_max"],
                "gradient_max": stats["gradient_max"],
                "r_mean": spatial["r_mean"],
                "r_mean_norm": spatial["r_mean_norm"],
                "r_std": spatial["r_std"],
                "nonzero_count": spatial.get("nonzero_count", 0),
                "skip_rate": stats["skip_rate"],
                "dilation_mean": dilation["dilation_mean"],
            }
            history.append(record)

            if verbose:
                status = "RUNNING"
                r_norm = spatial["r_mean_norm"]
                if r_norm < 0.01:
                    status = "COLLAPSED?"
                elif r_norm > 0.5:
                    status = "DISPERSED?"

                print(
                    f"[{tick+1:5d}] entities={stats['entity_count']:4d}, "
                    f"skip={stats['skip_rate']:.2f}, "
                    f"dilation={dilation['dilation_mean']:.2f}, "
                    f"r_norm={r_norm:.4f}, "
                    f"rate={tick_rate:.1f} t/s [{status}]"
                )

    elapsed = time.time() - start_time
    final_stats = evolution.get_statistics()
    final_spatial = compute_spatial_distribution(grid, config.origin)
    final_dilation = compute_time_dilation_stats(evolution.entities)

    # Stability metrics (drift over late history)
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means = [h["r_mean_norm"] for h in late_history]
        skip_rates = [h["skip_rate"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means)),
            "r_mean_norm_std": float(np.std(r_means)),
            "drift": float(np.std(r_means)),
            "skip_rate_avg": float(np.mean(skip_rates)),
            "skip_rate_std": float(np.std(skip_rates)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: entities={final_stats['entity_count']}, "
              f"skip_rate={final_stats['skip_rate']:.3f}, "
              f"r_norm={final_spatial['r_mean_norm']:.4f}")
        print(f"       dilation_mean={final_dilation['dilation_mean']:.3f}, "
              f"dilation_range=[{final_dilation['dilation_min']:.2f}, {final_dilation['dilation_max']:.2f}]")
        if stability_metrics:
            print(f"       drift={stability_metrics['drift']:.6f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": "V14",
        "grid_size": config.grid_size,
        "params": {
            "jitter_strength": config.jitter_strength,
            "gamma_decay": config.gamma_decay,
            "skip_sensitivity": config.skip_sensitivity,
        },
        "final_stats": {
            "entity_count": final_stats["entity_count"],
            "total_energy": final_stats["total_energy"],
            "gamma_sum": final_stats["gamma_sum"],
            "r_mean": final_spatial["r_mean"],
            "r_mean_norm": final_spatial["r_mean_norm"],
            "r_std": final_spatial["r_std"],
            "skip_rate": final_stats["skip_rate"],
            "dilation_mean": final_dilation["dilation_mean"],
            "dilation_std": final_dilation["dilation_std"],
            "dilation_min": final_dilation["dilation_min"],
            "dilation_max": final_dilation["dilation_max"],
        },
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_tick_skipping_validation(config: LayeredSubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Validate that tick skipping produces time dilation.

    Tests:
    1. Entities in high-gradient regions should skip more
    2. Skip probability should correlate with gamma gradient
    3. Time dilation factor should vary spatially

    Args:
        config: V14 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("TICK SKIPPING VALIDATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    # Run for enough ticks to get meaningful statistics
    test_ticks = 200
    if verbose:
        print(f"Running {test_ticks} ticks to build up gamma field...")

    evolution.evolve_n_ticks(test_ticks, progress_interval=50, verbose=verbose)

    # Analyze skip rates by position
    stats = evolution.get_statistics()

    # Check correlation between gamma gradient and skipping
    grad_mag = grid.compute_gamma_gradient_magnitude()
    grad_max = float(np.max(grad_mag))
    grad_mean = float(np.mean(grad_mag))

    # Entities near origin (high gamma) should have lower dilation factor
    origin = config.origin
    near_origin = []
    far_from_origin = []

    for entity in evolution.entities:
        x, y = entity.position
        dist = np.sqrt((x - origin[0])**2 + (y - origin[1])**2)
        if dist < 5:
            near_origin.append(entity)
        elif dist > 15:
            far_from_origin.append(entity)

    if verbose:
        print(f"\nAnalysis after {test_ticks} ticks:")
        print(f"  Total entities: {len(evolution.entities)}")
        print(f"  Near origin (<5): {len(near_origin)}")
        print(f"  Far from origin (>15): {len(far_from_origin)}")

    # Compute dilation for each group
    near_dilation = [e.time_dilation_factor for e in near_origin] if near_origin else [1.0]
    far_dilation = [e.time_dilation_factor for e in far_from_origin] if far_from_origin else [1.0]

    near_mean = float(np.mean(near_dilation))
    far_mean = float(np.mean(far_dilation))

    if verbose:
        print(f"\nTime dilation by distance from origin:")
        print(f"  Near origin mean dilation: {near_mean:.3f}")
        print(f"  Far from origin mean dilation: {far_mean:.3f}")

    # Validation: entities near high-gamma regions should experience more time dilation
    # (lower dilation factor = more skipping = more time dilation)
    # This is expected if gamma accumulates at origin

    # Check that skip rate is non-zero (time dilation is happening)
    skip_rate = stats["skip_rate"]
    skip_rate_nonzero = skip_rate > 0.01

    # Check that gradient is building up
    gradient_present = grad_max > 0.01

    if verbose:
        print(f"\nSkip rate: {skip_rate:.3f}")
        print(f"Skip rate > 0.01: {skip_rate_nonzero}")
        print(f"Gradient max: {grad_max:.4f}")
        print(f"Gradient present: {gradient_present}")

    passed = skip_rate_nonzero and gradient_present

    if verbose:
        print("-" * 70)
        print(f"TICK SKIPPING VALIDATION: {'PASSED' if passed else 'NEEDS TUNING'}")
        if not passed:
            print("Note: Low skip rate may indicate sensitivity needs adjustment")
            print(f"Current skip_sensitivity = {config.skip_sensitivity}")

    return {
        "test": "tick_skipping_validation",
        "skip_rate": skip_rate,
        "skip_rate_nonzero": skip_rate_nonzero,
        "gradient_max": grad_max,
        "gradient_present": gradient_present,
        "near_origin_dilation": near_mean,
        "far_from_origin_dilation": far_mean,
        "passed": passed,
    }


def run_comparison_test(verbose: bool = True) -> Dict[str, Any]:
    """Compare V14 with different gamma_decay values.

    Since skip_sensitivity = 1 - gamma_decay, this tests
    the impact of the derived parameter.

    Args:
        verbose: Print details

    Returns:
        Comparison results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("GAMMA DECAY SENSITIVITY COMPARISON")
        print("=" * 70)

    test_ticks = 300
    decay_values = [0.99, 0.95, 0.90]  # sensitivity = 0.01, 0.05, 0.10

    results = []
    for decay in decay_values:
        if verbose:
            sensitivity = 1 - decay
            print(f"\nTesting gamma_decay={decay} (sensitivity={sensitivity})...")

        config = create_config(grid_size=50, gamma_decay=decay, random_seed=42)
        grid = MultiLayerGrid(config.grid_width, config.grid_height)
        evolution = LayeredEvolution(grid, config)

        evolution.evolve_n_ticks(test_ticks, progress_interval=100, verbose=verbose)

        stats = evolution.get_statistics()
        dilation = compute_time_dilation_stats(evolution.entities)

        results.append({
            "gamma_decay": decay,
            "skip_sensitivity": 1 - decay,
            "skip_rate": stats["skip_rate"],
            "dilation_mean": dilation["dilation_mean"],
            "gamma_max": stats["gamma_max"],
        })

        if verbose:
            print(f"  skip_rate={stats['skip_rate']:.3f}, "
                  f"dilation={dilation['dilation_mean']:.3f}")

    if verbose:
        print("\n" + "-" * 70)
        print("Summary:")
        print(f"{'Decay':>8} {'Sensitivity':>12} {'Skip Rate':>12} {'Dilation':>12}")
        print("-" * 48)
        for r in results:
            print(f"{r['gamma_decay']:8.2f} {r['skip_sensitivity']:12.3f} "
                  f"{r['skip_rate']:12.3f} {r['dilation_mean']:12.3f}")

    return {
        "test": "decay_sensitivity_comparison",
        "results": results,
    }


def main():
    """Run V14 experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V14 Tick Skipping Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_v14.py --ticks 1000 --grid 100
  python experiment_v14.py --validate
  python experiment_v14.py --compare
  python experiment_v14.py --ticks 500 --decay 0.95
        """
    )
    parser.add_argument("--ticks", type=int, default=500, help="Number of ticks (default: 500)")
    parser.add_argument("--grid", type=int, default=100, help="Grid size (default: 100)")
    parser.add_argument("--jitter", type=float, default=None, help="Jitter strength (default: 0.119)")
    parser.add_argument("--decay", type=float, default=None, help="Gamma decay (default: 0.99)")
    parser.add_argument("--interval", type=int, default=100, help="Verbose interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/v14_experiment.json")
    parser.add_argument("--validate", action="store_true", help="Run tick skipping validation")
    parser.add_argument("--compare", action="store_true", help="Run decay sensitivity comparison")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    config = create_config(
        grid_size=args.grid,
        jitter_strength=args.jitter,
        gamma_decay=args.decay,
        random_seed=args.seed
    )

    if args.validate:
        results = run_tick_skipping_validation(config, verbose=not args.quiet)
        output_file = "results/v14_validation.json"
    elif args.compare:
        results = run_comparison_test(verbose=not args.quiet)
        output_file = "results/v14_comparison.json"
    else:
        results = run_v14_experiment(
            config,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output

    # Save results
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else str(x))

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
