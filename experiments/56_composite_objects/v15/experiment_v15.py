"""
V15 Experiment: Zero-Parameter Model Validation

Tests the zero-parameter model where ALL behavior emerges from:
1. Fixed constants: SKIP_SENSITIVITY=0.01, GAMMA_IMPRINT=1.0, ENERGY_PER_TICK=1.0
2. Derived values: jitter = 1 - effective_gamma

Success criteria:
1. Gamma accumulates but effective_gamma stays bounded [0, 1]
2. Jitter is high at edges, low at origin
3. Skip rate correlates with gradient (time dilation works)
4. Stable patterns form without ANY tuning

Author: V15 Implementation
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
from config_v15 import SubstrateConfig, create_config
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


def run_v15_experiment(
    config: SubstrateConfig,
    num_ticks: int = 500,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V15 zero-parameter experiment.

    Args:
        config: V15 configuration (zero tunable parameters)
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"V15 ZERO-PARAMETER EXPERIMENT: grid={config.grid_size}")
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
                # Raw gamma (accumulates forever in V15)
                "gamma_sum": stats["gamma_sum"],
                "gamma_max": stats["gamma_max"],
                "gamma_min": stats["gamma_min"],
                # Effective gamma (bounded [0, 1])
                "effective_gamma_mean": stats["effective_gamma_mean"],
                # Gradient
                "gradient_max": stats["gradient_max"],
                # Spatial
                "r_mean": spatial["r_mean"],
                "r_mean_norm": spatial["r_mean_norm"],
                "r_std": spatial["r_std"],
                "nonzero_count": spatial.get("nonzero_count", 0),
                # Time dilation
                "skip_rate": stats["skip_rate"],
                "dilation_mean": dilation["dilation_mean"],
                # Derived jitter
                "jitter_mean": stats["jitter_mean"],
                "jitter_std": stats["jitter_std"],
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
                    f"[{tick+1:5d}] e={stats['entity_count']:4d}, "
                    f"skip={stats['skip_rate']:.2f}, "
                    f"eff_gamma={stats['effective_gamma_mean']:.3f}, "
                    f"jitter={stats['jitter_mean']:.3f}, "
                    f"r={r_norm:.4f} [{status}]"
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
        jitter_means = [h["jitter_mean"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means)),
            "r_mean_norm_std": float(np.std(r_means)),
            "drift": float(np.std(r_means)),
            "skip_rate_avg": float(np.mean(skip_rates)),
            "skip_rate_std": float(np.std(skip_rates)),
            "jitter_mean_avg": float(np.mean(jitter_means)),
            "jitter_mean_std": float(np.std(jitter_means)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: entities={final_stats['entity_count']}, "
              f"skip_rate={final_stats['skip_rate']:.3f}, "
              f"r_norm={final_spatial['r_mean_norm']:.4f}")
        print(f"       gamma_range=[{final_stats['gamma_min']:.1f}, {final_stats['gamma_max']:.1f}], "
              f"eff_gamma_mean={final_stats['effective_gamma_mean']:.3f}")
        print(f"       jitter_mean={final_stats['jitter_mean']:.3f}, "
              f"dilation_mean={final_dilation['dilation_mean']:.3f}")
        if stability_metrics:
            print(f"       drift={stability_metrics['drift']:.6f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": "V15_ZERO_PARAM",
        "grid_size": config.grid_size,
        "params": {
            "SKIP_SENSITIVITY": config.SKIP_SENSITIVITY,
            "GAMMA_IMPRINT": config.GAMMA_IMPRINT,
            "ENERGY_PER_TICK": config.ENERGY_PER_TICK,
            "note": "Zero tunable parameters - all fixed or derived",
        },
        "final_stats": {
            "entity_count": final_stats["entity_count"],
            "total_energy": final_stats["total_energy"],
            "gamma_sum": final_stats["gamma_sum"],
            "gamma_min": final_stats["gamma_min"],
            "gamma_max": final_stats["gamma_max"],
            "effective_gamma_mean": final_stats["effective_gamma_mean"],
            "r_mean": final_spatial["r_mean"],
            "r_mean_norm": final_spatial["r_mean_norm"],
            "r_std": final_spatial["r_std"],
            "skip_rate": final_stats["skip_rate"],
            "jitter_mean": final_stats["jitter_mean"],
            "jitter_std": final_stats["jitter_std"],
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


def run_gamma_accumulation_test(config: SubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Test that gamma accumulates but effective_gamma stays bounded.

    V15 key validation:
    1. Gamma should accumulate (no decay)
    2. Effective gamma should stay in [0, 1]
    3. Jitter should vary inversely with effective gamma

    Args:
        config: V15 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("GAMMA ACCUMULATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    test_ticks = 300
    if verbose:
        print(f"Running {test_ticks} ticks to verify gamma accumulation...")

    gamma_history = []

    for tick in range(test_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % 50 == 0:
            stats = evolution.get_statistics()
            gamma_history.append({
                "tick": tick + 1,
                "gamma_sum": stats["gamma_sum"],
                "gamma_max": stats["gamma_max"],
                "effective_gamma_mean": stats["effective_gamma_mean"],
                "jitter_mean": stats["jitter_mean"],
            })

            if verbose:
                print(f"  Tick {tick+1:4d}: gamma_sum={stats['gamma_sum']:.1f}, "
                      f"gamma_max={stats['gamma_max']:.1f}, "
                      f"eff_gamma={stats['effective_gamma_mean']:.3f}, "
                      f"jitter={stats['jitter_mean']:.3f}")

    # Verify:
    # 1. Gamma sum increased (no decay)
    gamma_growing = gamma_history[-1]["gamma_sum"] > gamma_history[0]["gamma_sum"]

    # 2. Effective gamma stayed bounded
    effective_bounded = all(0 <= h["effective_gamma_mean"] <= 1 for h in gamma_history)

    # 3. Jitter inversely correlated with effective gamma
    # As effective_gamma increases, jitter should decrease
    eff_gammas = [h["effective_gamma_mean"] for h in gamma_history]
    jitters = [h["jitter_mean"] for h in gamma_history]

    # Simple check: correlation should be negative
    if len(eff_gammas) > 2:
        correlation = np.corrcoef(eff_gammas, jitters)[0, 1]
        jitter_inverse = correlation < 0
    else:
        jitter_inverse = True  # Not enough data

    passed = gamma_growing and effective_bounded and jitter_inverse

    if verbose:
        print()
        print(f"Verification:")
        print(f"  Gamma growing (no decay): {gamma_growing}")
        print(f"  Effective gamma bounded [0,1]: {effective_bounded}")
        print(f"  Jitter inversely correlated: {jitter_inverse}")
        if len(eff_gammas) > 2:
            print(f"    (correlation: {correlation:.3f})")
        print("-" * 70)
        print(f"GAMMA ACCUMULATION TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "gamma_accumulation",
        "gamma_growing": gamma_growing,
        "effective_bounded": effective_bounded,
        "jitter_inverse": jitter_inverse,
        "gamma_history": gamma_history,
        "passed": passed,
    }


def run_jitter_variation_test(config: SubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Test that jitter varies spatially (high at edges, low at origin).

    Args:
        config: V15 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("JITTER SPATIAL VARIATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    # Run for enough ticks to build up gamma at origin
    test_ticks = 200
    if verbose:
        print(f"Running {test_ticks} ticks to build up gamma field...")

    evolution.evolve_n_ticks(test_ticks, progress_interval=50, verbose=verbose)

    # Compute jitter at different positions
    origin = config.origin
    effective_gamma = grid.get_effective_gamma()

    # Sample positions
    positions = {
        "origin": origin,
        "near_origin": (origin[0] + 5, origin[1] + 5),
        "mid_range": (origin[0] + 15, origin[1] + 15),
        "edge": (origin[0] + 30, origin[1] + 30),
    }

    jitter_by_position = {}
    for name, pos in positions.items():
        x, y = pos
        x = max(0, min(grid.width - 1, x))
        y = max(0, min(grid.height - 1, y))

        eff_gamma = effective_gamma[y, x]
        jitter = 1.0 - eff_gamma
        jitter_by_position[name] = {
            "position": (x, y),
            "effective_gamma": float(eff_gamma),
            "jitter": float(jitter),
        }

    if verbose:
        print()
        print("Jitter by position:")
        for name, data in jitter_by_position.items():
            print(f"  {name:12s}: pos={data['position']}, "
                  f"eff_gamma={data['effective_gamma']:.3f}, "
                  f"jitter={data['jitter']:.3f}")

    # Verify: jitter at edge > jitter at origin
    # (because effective_gamma at edge < effective_gamma at origin)
    jitter_origin = jitter_by_position["origin"]["jitter"]
    jitter_edge = jitter_by_position["edge"]["jitter"]
    jitter_varies = jitter_edge > jitter_origin

    passed = jitter_varies

    if verbose:
        print()
        print(f"Verification:")
        print(f"  Jitter at edge ({jitter_edge:.3f}) > jitter at origin ({jitter_origin:.3f}): {jitter_varies}")
        print("-" * 70)
        print(f"JITTER VARIATION TEST: {'PASSED' if passed else 'NEEDS INVESTIGATION'}")

    return {
        "test": "jitter_variation",
        "jitter_by_position": jitter_by_position,
        "jitter_varies": jitter_varies,
        "passed": passed,
    }


def run_emergence_validation(config: SubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Validate that stable patterns emerge with zero parameters.

    Args:
        config: V15 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("PATTERN EMERGENCE VALIDATION")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    test_ticks = 300
    if verbose:
        print(f"Running {test_ticks} ticks to test pattern emergence...")
        print()

    # Collect our own history with spatial distribution
    history = []
    for tick in range(test_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % 50 == 0:
            stats = evolution.get_statistics()
            spatial = compute_spatial_distribution(grid, config.origin)
            history.append({
                "tick": tick + 1,
                "r_mean_norm": spatial["r_mean_norm"],
                "skip_rate": stats["skip_rate"],
            })

            if verbose:
                print(f"[{tick+1:5d}] skip={stats['skip_rate']:.2f}, "
                      f"r_norm={spatial['r_mean_norm']:.4f}")

    # Analyze late-phase stability
    late_history = history[len(history)//2:]  # Second half

    if late_history:
        r_norms = [h["r_mean_norm"] for h in late_history]
        skip_rates = [h["skip_rate"] for h in late_history]

        r_stable = np.std(r_norms) < 0.1  # Less than 10% variation
        skip_stable = np.std(skip_rates) < 0.1

        # Pattern didn't collapse (r > 0) and didn't explode (r < 0.5)
        r_bounded = 0.01 < np.mean(r_norms) < 0.5

        passed = r_stable and skip_stable and r_bounded
    else:
        passed = False
        r_stable = False
        skip_stable = False
        r_bounded = False

    if verbose:
        print()
        print("Pattern emergence validation:")
        print(f"  Radial distribution stable: {r_stable}")
        print(f"  Skip rate stable: {skip_stable}")
        print(f"  Pattern bounded (not collapsed, not exploded): {r_bounded}")
        print("-" * 70)
        print(f"EMERGENCE VALIDATION: {'PASSED' if passed else 'NEEDS TUNING'}")

    return {
        "test": "emergence_validation",
        "r_stable": r_stable,
        "skip_stable": skip_stable,
        "r_bounded": r_bounded,
        "passed": passed,
    }


def main():
    """Run V15 experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V15 Zero-Parameter Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_v15.py --ticks 500 --grid 100
  python experiment_v15.py --test gamma
  python experiment_v15.py --test jitter
  python experiment_v15.py --test emergence
  python experiment_v15.py --all
        """
    )
    parser.add_argument("--ticks", type=int, default=500, help="Number of ticks (default: 500)")
    parser.add_argument("--grid", type=int, default=100, help="Grid size (default: 100)")
    parser.add_argument("--interval", type=int, default=100, help="Verbose interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/v15_experiment.json")
    parser.add_argument("--test", type=str, choices=["gamma", "jitter", "emergence"], help="Run specific test")
    parser.add_argument("--all", action="store_true", help="Run all validation tests")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    config = create_config(
        grid_size=args.grid,
        random_seed=args.seed
    )

    results = {}

    if args.test == "gamma":
        results = run_gamma_accumulation_test(config, verbose=not args.quiet)
        output_file = "results/v15_gamma_test.json"
    elif args.test == "jitter":
        results = run_jitter_variation_test(config, verbose=not args.quiet)
        output_file = "results/v15_jitter_test.json"
    elif args.test == "emergence":
        results = run_emergence_validation(config, verbose=not args.quiet)
        output_file = "results/v15_emergence_test.json"
    elif args.all:
        # Run all tests
        results = {
            "gamma_test": run_gamma_accumulation_test(config, verbose=not args.quiet),
            "jitter_test": run_jitter_variation_test(config, verbose=not args.quiet),
            "emergence_test": run_emergence_validation(config, verbose=not args.quiet),
        }
        # Summary
        all_passed = all(r.get("passed", False) for r in results.values())
        results["all_passed"] = all_passed

        if not args.quiet:
            print("\n" + "=" * 70)
            print("V15 VALIDATION SUMMARY")
            print("=" * 70)
            for name, r in results.items():
                if name != "all_passed":
                    status = "PASSED" if r.get("passed", False) else "FAILED"
                    print(f"  {name}: {status}")
            print("-" * 70)
            print(f"  ALL TESTS: {'PASSED' if all_passed else 'SOME FAILED'}")
            print("=" * 70)

        output_file = "results/v15_all_tests.json"
    else:
        # Default: run main experiment
        results = run_v15_experiment(
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
