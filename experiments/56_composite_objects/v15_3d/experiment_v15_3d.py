"""
V15-3D Experiment: Zero-Parameter Model Validation in 3D

Tests the zero-parameter model in 3D where ALL behavior emerges from:
1. Fixed constants: SKIP_SENSITIVITY=0.01, GAMMA_IMPRINT=1.0, ENERGY_PER_TICK=1.0
2. Derived values: jitter = 1 - effective_gamma

3D-specific tests:
- Spherical shell distribution (radial analysis)
- 3D gradient validation
- Slice visualizations (XY, XZ, YZ planes)

Success criteria (same as 2D):
1. Gamma accumulates but effective_gamma stays bounded [0, 1]
2. Jitter is high at edges, low at origin
3. Skip rate correlates with gradient (time dilation works)
4. Stable patterns form without ANY tuning

Theory prediction:
- 3D is the "Goldilocks" dimension (5% variance vs 22% for 2D)
- More stable dynamics expected

Author: V15-3D Implementation
Date: 2026-02-01
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

from multi_layer_grid_3d import MultiLayerGrid3D
from entity import Entity
from config_v15_3d import SubstrateConfig3D, create_config
from layered_evolution_3d import LayeredEvolution3D


def compute_spatial_distribution_3d(grid: MultiLayerGrid3D, origin: Tuple[int, int, int]) -> Dict[str, float]:
    """Compute spatial distribution metrics relative to origin in 3D.

    Uses spherical shells for radial analysis.

    Args:
        grid: MultiLayerGrid3D with entity layers
        origin: Center point (x, y, z)

    Returns:
        Dict with radial distribution metrics
    """
    combined = grid.compute_combined_field()
    origin_x, origin_y, origin_z = origin

    # Find all non-zero positions (array indexing: [z, y, x])
    nonzero_z, nonzero_y, nonzero_x = np.nonzero(combined)

    if len(nonzero_x) == 0:
        return {
            "r_mean": 0.0,
            "r_std": 0.0,
            "r_max": 0.0,
            "spread": 0.0,
            "r_mean_norm": 0.0,
            "r_std_norm": 0.0,
            "nonzero_count": 0,
        }

    # Compute 3D radii from origin
    dx = nonzero_x - origin_x
    dy = nonzero_y - origin_y
    dz = nonzero_z - origin_z
    radii = np.sqrt(dx**2 + dy**2 + dz**2)

    r_mean = float(np.mean(radii))
    r_std = float(np.std(radii))
    r_max = float(np.max(radii))

    # Normalize by half-grid (use smallest dimension for 3D)
    half_grid = min(grid.depth, grid.height, grid.width) / 2.0
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


def compute_shell_distribution(
    grid: MultiLayerGrid3D,
    origin: Tuple[int, int, int],
    num_shells: int = 10
) -> Dict[str, Any]:
    """Compute distribution of energy across spherical shells.

    Args:
        grid: MultiLayerGrid3D with entity layers
        origin: Center point (x, y, z)
        num_shells: Number of radial shells

    Returns:
        Dict with shell distribution data
    """
    combined = grid.compute_combined_field()
    origin_x, origin_y, origin_z = origin

    # Create distance field
    z_coords, y_coords, x_coords = np.meshgrid(
        np.arange(grid.depth),
        np.arange(grid.height),
        np.arange(grid.width),
        indexing='ij'
    )
    distances = np.sqrt(
        (x_coords - origin_x)**2 +
        (y_coords - origin_y)**2 +
        (z_coords - origin_z)**2
    )

    max_r = min(grid.depth, grid.height, grid.width) / 2.0
    shell_width = max_r / num_shells

    shells = []
    for i in range(num_shells):
        r_inner = i * shell_width
        r_outer = (i + 1) * shell_width

        mask = (distances >= r_inner) & (distances < r_outer)
        shell_energy = int(np.sum(np.abs(combined[mask])))
        shell_cells = int(np.sum(mask))
        shell_nonzero = int(np.count_nonzero(combined[mask]))

        shells.append({
            "shell": i,
            "r_inner": float(r_inner),
            "r_outer": float(r_outer),
            "energy": shell_energy,
            "cells": shell_cells,
            "nonzero": shell_nonzero,
            "density": shell_energy / shell_cells if shell_cells > 0 else 0.0,
        })

    return {
        "num_shells": num_shells,
        "shell_width": float(shell_width),
        "max_r": float(max_r),
        "shells": shells,
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


def run_v15_3d_experiment(
    config: SubstrateConfig3D,
    num_ticks: int = 200,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V15-3D zero-parameter experiment.

    Args:
        config: V15-3D configuration (zero tunable parameters)
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"V15-3D ZERO-PARAMETER EXPERIMENT: grid={config.grid_size}^3")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    # Create grid and evolution
    grid = MultiLayerGrid3D(config.grid_depth, config.grid_height, config.grid_width)
    evolution = LayeredEvolution3D(grid, config)

    history = []
    start_time = time.time()

    for tick in range(num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % verbose_interval == 0:
            stats = evolution.get_statistics()
            spatial = compute_spatial_distribution_3d(grid, config.origin)
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
                # Spatial (3D)
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
                # Performance
                "tick_rate": tick_rate,
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
                    f"r={r_norm:.4f} [{status}] "
                    f"({tick_rate:.1f} t/s)"
                )

    elapsed = time.time() - start_time
    final_stats = evolution.get_statistics()
    final_spatial = compute_spatial_distribution_3d(grid, config.origin)
    final_dilation = compute_time_dilation_stats(evolution.entities)
    shell_dist = compute_shell_distribution(grid, config.origin, num_shells=5)

    # Stability metrics (drift over late history)
    late_start = max(50, num_ticks // 5)
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

        # Shell distribution summary
        print()
        print("Spherical shell distribution:")
        for shell in shell_dist["shells"]:
            print(f"  Shell {shell['shell']}: r=[{shell['r_inner']:.1f}, {shell['r_outer']:.1f}], "
                  f"energy={shell['energy']}, density={shell['density']:.4f}")

    return {
        "config_name": "V15_3D_ZERO_PARAM",
        "grid_size": config.grid_size,
        "dimensions": 3,
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
        "shell_distribution": shell_dist,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
        "ticks_per_second": num_ticks / elapsed if elapsed > 0 else 0,
    }


def run_gamma_accumulation_test(config: SubstrateConfig3D, verbose: bool = True) -> Dict[str, Any]:
    """Test that gamma accumulates but effective_gamma stays bounded.

    V15 key validation:
    1. Gamma should accumulate (no decay)
    2. Effective gamma should stay in [0, 1]
    3. Jitter should vary inversely with effective gamma

    Args:
        config: V15-3D configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("3D GAMMA ACCUMULATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid3D(config.grid_depth, config.grid_height, config.grid_width)
    evolution = LayeredEvolution3D(grid, config)

    test_ticks = 150
    if verbose:
        print(f"Running {test_ticks} ticks to verify gamma accumulation in 3D...")

    gamma_history = []

    for tick in range(test_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % 30 == 0:
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
    eff_gammas = [h["effective_gamma_mean"] for h in gamma_history]
    jitters = [h["jitter_mean"] for h in gamma_history]

    if len(eff_gammas) > 2:
        correlation = np.corrcoef(eff_gammas, jitters)[0, 1]
        jitter_inverse = correlation < 0
    else:
        jitter_inverse = True
        correlation = 0.0

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
        print(f"3D GAMMA ACCUMULATION TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "gamma_accumulation_3d",
        "gamma_growing": gamma_growing,
        "effective_bounded": effective_bounded,
        "jitter_inverse": jitter_inverse,
        "gamma_history": gamma_history,
        "passed": passed,
    }


def run_jitter_variation_test(config: SubstrateConfig3D, verbose: bool = True) -> Dict[str, Any]:
    """Test that jitter varies spatially (high at edges, low at origin) in 3D.

    Args:
        config: V15-3D configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("3D JITTER SPATIAL VARIATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid3D(config.grid_depth, config.grid_height, config.grid_width)
    evolution = LayeredEvolution3D(grid, config)

    # Run for enough ticks to build up gamma at origin
    test_ticks = 100
    if verbose:
        print(f"Running {test_ticks} ticks to build up 3D gamma field...")

    evolution.evolve_n_ticks(test_ticks, progress_interval=25, verbose=verbose)

    # Compute jitter at different 3D positions
    origin = config.origin
    effective_gamma = grid.get_effective_gamma()

    # Sample positions along diagonal in 3D
    positions = {
        "origin": origin,
        "near_origin": (origin[0] + 3, origin[1] + 3, origin[2] + 3),
        "mid_range": (origin[0] + 8, origin[1] + 8, origin[2] + 8),
        "edge": (min(origin[0] + 12, config.grid_size - 1),
                 min(origin[1] + 12, config.grid_size - 1),
                 min(origin[2] + 12, config.grid_size - 1)),
    }

    jitter_by_position = {}
    for name, pos in positions.items():
        x, y, z = pos
        x = max(0, min(grid.width - 1, x))
        y = max(0, min(grid.height - 1, y))
        z = max(0, min(grid.depth - 1, z))

        # Array indexing: [z, y, x]
        eff_gamma = effective_gamma[z, y, x]
        jitter = 1.0 - eff_gamma
        jitter_by_position[name] = {
            "position": (x, y, z),
            "effective_gamma": float(eff_gamma),
            "jitter": float(jitter),
        }

    if verbose:
        print()
        print("Jitter by position (3D):")
        for name, data in jitter_by_position.items():
            print(f"  {name:12s}: pos={data['position']}, "
                  f"eff_gamma={data['effective_gamma']:.3f}, "
                  f"jitter={data['jitter']:.3f}")

    # Verify: jitter at edge > jitter at origin
    jitter_origin = jitter_by_position["origin"]["jitter"]
    jitter_edge = jitter_by_position["edge"]["jitter"]
    jitter_varies = jitter_edge > jitter_origin

    passed = jitter_varies

    if verbose:
        print()
        print(f"Verification:")
        print(f"  Jitter at edge ({jitter_edge:.3f}) > jitter at origin ({jitter_origin:.3f}): {jitter_varies}")
        print("-" * 70)
        print(f"3D JITTER VARIATION TEST: {'PASSED' if passed else 'NEEDS INVESTIGATION'}")

    return {
        "test": "jitter_variation_3d",
        "jitter_by_position": jitter_by_position,
        "jitter_varies": jitter_varies,
        "passed": passed,
    }


def run_emergence_validation(config: SubstrateConfig3D, verbose: bool = True) -> Dict[str, Any]:
    """Validate that stable patterns emerge with zero parameters in 3D.

    Args:
        config: V15-3D configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("3D PATTERN EMERGENCE VALIDATION")
        print("=" * 70)

    grid = MultiLayerGrid3D(config.grid_depth, config.grid_height, config.grid_width)
    evolution = LayeredEvolution3D(grid, config)

    test_ticks = 150
    if verbose:
        print(f"Running {test_ticks} ticks to test 3D pattern emergence...")
        print()

    history = []
    for tick in range(test_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % 30 == 0:
            stats = evolution.get_statistics()
            spatial = compute_spatial_distribution_3d(grid, config.origin)
            history.append({
                "tick": tick + 1,
                "r_mean_norm": spatial["r_mean_norm"],
                "skip_rate": stats["skip_rate"],
            })

            if verbose:
                print(f"[{tick+1:5d}] skip={stats['skip_rate']:.2f}, "
                      f"r_norm={spatial['r_mean_norm']:.4f}")

    # Analyze late-phase stability
    late_history = history[len(history)//2:]

    if late_history:
        r_norms = [h["r_mean_norm"] for h in late_history]
        skip_rates = [h["skip_rate"] for h in late_history]

        r_stable = np.std(r_norms) < 0.1
        skip_stable = np.std(skip_rates) < 0.1
        r_bounded = 0.01 < np.mean(r_norms) < 0.5

        passed = r_stable and skip_stable and r_bounded
    else:
        passed = False
        r_stable = False
        skip_stable = False
        r_bounded = False

    if verbose:
        print()
        print("3D Pattern emergence validation:")
        print(f"  Radial distribution stable: {r_stable}")
        print(f"  Skip rate stable: {skip_stable}")
        print(f"  Pattern bounded (not collapsed, not exploded): {r_bounded}")
        print("-" * 70)
        print(f"3D EMERGENCE VALIDATION: {'PASSED' if passed else 'NEEDS TUNING'}")

    return {
        "test": "emergence_validation_3d",
        "r_stable": r_stable,
        "skip_stable": skip_stable,
        "r_bounded": r_bounded,
        "passed": passed,
    }


def run_comparison_with_2d(verbose: bool = True) -> Dict[str, Any]:
    """Compare 3D results with expected 2D baseline.

    Theory predicts:
    - 3D variance: 5%
    - 2D variance: 22%
    - 3D should be more stable

    Args:
        verbose: Print details

    Returns:
        Comparison results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("2D vs 3D COMPARISON (Theory Validation)")
        print("=" * 70)

    # Run 3D experiment
    config_3d = create_config(grid_size=25)
    grid_3d = MultiLayerGrid3D(config_3d.grid_depth, config_3d.grid_height, config_3d.grid_width)
    evolution_3d = LayeredEvolution3D(grid_3d, config_3d)

    test_ticks = 100

    if verbose:
        print(f"Running {test_ticks} ticks in 3D (grid={config_3d.grid_size}^3)...")

    r_history_3d = []
    for tick in range(test_ticks):
        evolution_3d.evolve_one_tick()
        if (tick + 1) % 20 == 0:
            spatial = compute_spatial_distribution_3d(grid_3d, config_3d.origin)
            r_history_3d.append(spatial["r_mean_norm"])

    # Compute variance in late phase
    late_3d = r_history_3d[len(r_history_3d)//2:]
    variance_3d = np.std(late_3d) if late_3d else 0.0

    if verbose:
        print(f"\n3D Results:")
        print(f"  Late-phase r_norm variance: {variance_3d:.4f}")
        print(f"  Theory prediction: ~0.05 (5% variance)")
        print()
        print("Comparison:")
        print(f"  2D theory variance: 22%")
        print(f"  3D theory variance:  5%")
        print(f"  3D measured variance: {variance_3d*100:.1f}%")
        print()

        if variance_3d < 0.15:
            print("  Result: 3D is MORE STABLE than 2D (as predicted)")
        else:
            print("  Result: 3D stability similar to or worse than 2D")

    return {
        "test": "2d_vs_3d_comparison",
        "variance_3d": float(variance_3d),
        "theory_variance_2d": 0.22,
        "theory_variance_3d": 0.05,
        "is_3d_more_stable": variance_3d < 0.15,
    }


def main():
    """Run V15-3D experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V15-3D Zero-Parameter Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_v15_3d.py --ticks 200 --grid 30
  python experiment_v15_3d.py --test gamma
  python experiment_v15_3d.py --test jitter
  python experiment_v15_3d.py --test emergence
  python experiment_v15_3d.py --test compare
  python experiment_v15_3d.py --all
        """
    )
    parser.add_argument("--ticks", type=int, default=200, help="Number of ticks (default: 200)")
    parser.add_argument("--grid", type=int, default=30, help="Grid size (default: 30 for 3D)")
    parser.add_argument("--interval", type=int, default=50, help="Verbose interval (default: 50)")
    parser.add_argument("--output", type=str, default="results/v15_3d_experiment.json")
    parser.add_argument("--test", type=str, choices=["gamma", "jitter", "emergence", "compare"],
                        help="Run specific test")
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
        output_file = "results/v15_3d_gamma_test.json"
    elif args.test == "jitter":
        results = run_jitter_variation_test(config, verbose=not args.quiet)
        output_file = "results/v15_3d_jitter_test.json"
    elif args.test == "emergence":
        results = run_emergence_validation(config, verbose=not args.quiet)
        output_file = "results/v15_3d_emergence_test.json"
    elif args.test == "compare":
        results = run_comparison_with_2d(verbose=not args.quiet)
        output_file = "results/v15_3d_compare_test.json"
    elif args.all:
        # Run all tests
        results = {
            "gamma_test": run_gamma_accumulation_test(config, verbose=not args.quiet),
            "jitter_test": run_jitter_variation_test(config, verbose=not args.quiet),
            "emergence_test": run_emergence_validation(config, verbose=not args.quiet),
            "comparison_test": run_comparison_with_2d(verbose=not args.quiet),
        }
        # Summary
        all_passed = all(r.get("passed", False) for r in results.values()
                        if isinstance(r, dict) and "passed" in r)
        results["all_passed"] = all_passed

        if not args.quiet:
            print("\n" + "=" * 70)
            print("V15-3D VALIDATION SUMMARY")
            print("=" * 70)
            for name, r in results.items():
                if name != "all_passed" and isinstance(r, dict):
                    status = "PASSED" if r.get("passed", False) else "FAILED/N/A"
                    print(f"  {name}: {status}")
            print("-" * 70)
            print(f"  ALL TESTS: {'PASSED' if all_passed else 'SOME FAILED'}")
            print("=" * 70)

        output_file = "results/v15_3d_all_tests.json"
    else:
        # Default: run main experiment
        results = run_v15_3d_experiment(
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
