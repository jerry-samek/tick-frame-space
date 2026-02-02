"""
V16 Experiment: Expanding Grid Zero-Parameter Model

Tests the expanding grid model with same zero-parameter physics as V15-3D:
1. Fixed constants: SKIP_SENSITIVITY=0.01, GAMMA_IMPRINT=1.0, ENERGY_PER_TICK=1.0
2. Derived values: jitter = 1 - effective_gamma

V16-specific observations:
- Grid expands over time (space expansion)
- Pattern size relative to grid size (r_norm)
- Memory usage tracking
- Entity position tracking as grid expands

Success criteria:
1. Gamma accumulates but effective_gamma stays bounded [0, 1]
2. Jitter is high at edges, low at origin
3. Skip rate correlates with gradient (time dilation works)
4. Stable patterns form without ANY tuning
5. Memory stays within budget
6. Patterns find natural equilibrium size relative to grid

Comparison with V15-3D:
- V15-3D: Fixed grid, r_norm=0.89 (dispersed to edge)
- V16: Expanding grid, patterns should have room to find equilibrium

Author: V16 Implementation
Date: 2026-02-01
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

from expanding_grid import ExpandingGrid3D
from entity import Entity
from config_v16 import SubstrateConfig16, create_config
from expanding_evolution import ExpandingEvolution3D


def compute_spatial_distribution_3d(grid: ExpandingGrid3D, origin: Tuple[int, int, int]) -> Dict[str, float]:
    """Compute spatial distribution metrics relative to origin in 3D.

    Uses spherical shells for radial analysis.

    Args:
        grid: ExpandingGrid3D with entity layers
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

    # Normalize by half-grid (current size)
    half_grid = grid.current_size / 2.0
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
    grid: ExpandingGrid3D,
    origin: Tuple[int, int, int],
    num_shells: int = 10
) -> Dict[str, Any]:
    """Compute distribution of energy across spherical shells.

    Args:
        grid: ExpandingGrid3D with entity layers
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

    max_r = grid.current_size / 2.0
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


def run_v16_experiment(
    config: SubstrateConfig16,
    num_ticks: int = 500,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V16 expanding grid experiment.

    Args:
        config: V16 configuration (zero tunable parameters)
        num_ticks: Number of simulation ticks (capped by config.max_ticks)
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    # Cap ticks at config limit
    num_ticks = min(num_ticks, config.max_ticks)

    if verbose:
        print(f"\n{'='*70}")
        print(f"V16 EXPANDING GRID EXPERIMENT: initial={config.initial_size}^3")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    # Create grid and evolution
    grid = ExpandingGrid3D(
        initial_size=config.initial_size,
        expansion_rate=config.expansion_rate
    )
    evolution = ExpandingEvolution3D(grid, config)

    history = []
    expansion_events = []
    start_time = time.time()

    for tick in range(num_ticks):
        try:
            tick_info = evolution.evolve_one_tick()
        except MemoryError as e:
            if verbose:
                print(f"\n!!! MEMORY LIMIT REACHED at tick {tick+1}: {e}")
            break

        if tick_info["expanded"]:
            expansion_events.append({
                "tick": tick + 1,
                "new_size": tick_info["grid_size"],
                "memory_mb": tick_info["memory_mb"],
            })

        if (tick + 1) % verbose_interval == 0:
            stats = evolution.get_statistics()
            spatial = compute_spatial_distribution_3d(grid, grid.origin)
            dilation = compute_time_dilation_stats(evolution.entities)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            record = {
                "tick": tick + 1,
                "entity_count": stats["entity_count"],
                "total_energy": stats["total_energy"],
                # Grid expansion
                "grid_size": stats["grid_size"],
                "expansion_count": stats["expansion_count"],
                "memory_mb": stats["memory_mb"],
                # Raw gamma (accumulates forever in V16)
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
                elif r_norm > 0.8:
                    status = "DISPERSED?"
                elif 0.2 < r_norm < 0.6:
                    status = "EQUILIBRIUM"

                expand_marker = "*" if tick_info["expanded"] else " "
                print(
                    f"[{tick+1:5d}]{expand_marker} "
                    f"grid={stats['grid_size']:3d}^3, "
                    f"mem={stats['memory_mb']:6.1f}MB, "
                    f"e={stats['entity_count']:4d}, "
                    f"skip={stats['skip_rate']:.2f}, "
                    f"r={r_norm:.3f} [{status}] "
                    f"({tick_rate:.1f} t/s)"
                )

    elapsed = time.time() - start_time
    final_tick = evolution.tick_count
    final_stats = evolution.get_statistics()
    final_spatial = compute_spatial_distribution_3d(grid, grid.origin)
    final_dilation = compute_time_dilation_stats(evolution.entities)
    shell_dist = compute_shell_distribution(grid, grid.origin, num_shells=5)

    # Stability metrics (drift over late history)
    late_start = max(50, final_tick // 5)
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
        print(f"FINAL: tick={final_tick}, grid={final_stats['grid_size']}^3, "
              f"entities={final_stats['entity_count']}, "
              f"mem={final_stats['memory_mb']:.1f}MB")
        print(f"       skip_rate={final_stats['skip_rate']:.3f}, "
              f"r_norm={final_spatial['r_mean_norm']:.4f}")
        print(f"       gamma_range=[{final_stats['gamma_min']:.1f}, {final_stats['gamma_max']:.1f}], "
              f"eff_gamma_mean={final_stats['effective_gamma_mean']:.3f}")
        print(f"       jitter_mean={final_stats['jitter_mean']:.3f}, "
              f"dilation_mean={final_dilation['dilation_mean']:.3f}")
        if stability_metrics:
            print(f"       drift={stability_metrics['drift']:.6f}")
        print(f"       Time: {elapsed:.1f}s ({final_tick/elapsed:.1f} ticks/sec)")

        # Expansion summary
        print()
        print(f"EXPANSION SUMMARY:")
        print(f"  Initial size: {config.initial_size}^3 = {config.initial_size**3:,} cells")
        print(f"  Final size: {final_stats['grid_size']}^3 = {final_stats['grid_size']**3:,} cells")
        print(f"  Expansions: {final_stats['expansion_count']}")
        print(f"  Expansion rate: every {config.expansion_rate} ticks")

        # Shell distribution summary
        print()
        print("Spherical shell distribution:")
        for shell in shell_dist["shells"]:
            print(f"  Shell {shell['shell']}: r=[{shell['r_inner']:.1f}, {shell['r_outer']:.1f}], "
                  f"energy={shell['energy']}, density={shell['density']:.4f}")

    return {
        "config_name": "V16_EXPANDING_GRID",
        "initial_size": config.initial_size,
        "final_size": final_stats["grid_size"],
        "expansion_rate": config.expansion_rate,
        "dimensions": 3,
        "params": {
            "SKIP_SENSITIVITY": config.SKIP_SENSITIVITY,
            "GAMMA_IMPRINT": config.GAMMA_IMPRINT,
            "ENERGY_PER_TICK": config.ENERGY_PER_TICK,
            "note": "Zero tunable parameters - all fixed or derived",
        },
        "final_stats": {
            "tick_count": final_tick,
            "entity_count": final_stats["entity_count"],
            "total_energy": final_stats["total_energy"],
            "grid_size": final_stats["grid_size"],
            "expansion_count": final_stats["expansion_count"],
            "memory_mb": final_stats["memory_mb"],
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
        "expansion_events": expansion_events,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": final_tick,
        "ticks_per_second": final_tick / elapsed if elapsed > 0 else 0,
    }


def run_gamma_accumulation_test(config: SubstrateConfig16, verbose: bool = True) -> Dict[str, Any]:
    """Test that gamma accumulates but effective_gamma stays bounded.

    V16 key validation (same as V15):
    1. Gamma should accumulate (no decay)
    2. Effective gamma should stay in [0, 1]
    3. Jitter should vary inversely with effective gamma

    Args:
        config: V16 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("V16 GAMMA ACCUMULATION TEST (with expanding grid)")
        print("=" * 70)

    grid = ExpandingGrid3D(
        initial_size=config.initial_size,
        expansion_rate=config.expansion_rate
    )
    evolution = ExpandingEvolution3D(grid, config)

    test_ticks = min(150, config.max_ticks)
    if verbose:
        print(f"Running {test_ticks} ticks to verify gamma accumulation...")

    gamma_history = []

    for tick in range(test_ticks):
        try:
            evolution.evolve_one_tick()
        except MemoryError:
            if verbose:
                print(f"  Memory limit reached at tick {tick+1}")
            break

        if (tick + 1) % 30 == 0:
            stats = evolution.get_statistics()
            gamma_history.append({
                "tick": tick + 1,
                "grid_size": stats["grid_size"],
                "gamma_sum": stats["gamma_sum"],
                "gamma_max": stats["gamma_max"],
                "effective_gamma_mean": stats["effective_gamma_mean"],
                "jitter_mean": stats["jitter_mean"],
            })

            if verbose:
                print(f"  Tick {tick+1:4d}: grid={stats['grid_size']}^3, "
                      f"gamma_sum={stats['gamma_sum']:.1f}, "
                      f"eff_gamma={stats['effective_gamma_mean']:.3f}, "
                      f"jitter={stats['jitter_mean']:.3f}")

    if len(gamma_history) < 2:
        return {"test": "gamma_accumulation_v16", "passed": False, "error": "Insufficient data"}

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
        print(f"V16 GAMMA ACCUMULATION TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "gamma_accumulation_v16",
        "gamma_growing": gamma_growing,
        "effective_bounded": effective_bounded,
        "jitter_inverse": jitter_inverse,
        "gamma_history": gamma_history,
        "passed": passed,
    }


def run_expansion_test(config: SubstrateConfig16, verbose: bool = True) -> Dict[str, Any]:
    """Test that grid expansion works correctly.

    Verifies:
    1. Grid expands at expected rate
    2. Entity positions shift correctly
    3. Memory stays within budget

    Args:
        config: V16 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("V16 GRID EXPANSION TEST")
        print("=" * 70)

    grid = ExpandingGrid3D(
        initial_size=config.initial_size,
        expansion_rate=config.expansion_rate
    )
    evolution = ExpandingEvolution3D(grid, config)

    test_ticks = min(100, config.max_ticks)
    if verbose:
        print(f"Running {test_ticks} ticks to verify expansion mechanics...")
        print(f"  Expected expansion rate: every {config.expansion_rate} ticks")

    expansion_events = []
    entity_positions_before = {}

    for tick in range(test_ticks):
        # Track positions before tick
        if tick > 0 and tick % config.expansion_rate == config.expansion_rate - 1:
            for e in evolution.entities[:5]:  # Sample first 5
                entity_positions_before[e.entity_id] = e.position

        try:
            tick_info = evolution.evolve_one_tick()
        except MemoryError:
            if verbose:
                print(f"  Memory limit reached at tick {tick+1}")
            break

        if tick_info["expanded"]:
            expansion_events.append({
                "tick": tick + 1,
                "new_size": tick_info["grid_size"],
                "memory_mb": tick_info["memory_mb"],
            })

            if verbose:
                print(f"  Tick {tick+1:4d}: EXPANDED to {tick_info['grid_size']}^3, "
                      f"mem={tick_info['memory_mb']:.1f}MB")

    # Verify expansion occurred as expected
    expected_expansions = (test_ticks - 1) // config.expansion_rate
    actual_expansions = len(expansion_events)
    expansion_rate_correct = abs(actual_expansions - expected_expansions) <= 1

    # Verify grid size matches expectations
    expected_final_size = config.initial_size + (actual_expansions * 2)
    actual_final_size = grid.current_size
    size_correct = actual_final_size == expected_final_size

    # Verify memory is within budget
    memory_within_budget = grid.get_memory_usage_mb() <= config.max_memory_mb

    passed = expansion_rate_correct and size_correct and memory_within_budget

    if verbose:
        print()
        print(f"Verification:")
        print(f"  Expected expansions: {expected_expansions}, Actual: {actual_expansions}")
        print(f"  Expansion rate correct: {expansion_rate_correct}")
        print(f"  Expected final size: {expected_final_size}^3, Actual: {actual_final_size}^3")
        print(f"  Size correct: {size_correct}")
        print(f"  Memory: {grid.get_memory_usage_mb():.1f} MB (limit: {config.max_memory_mb} MB)")
        print(f"  Memory within budget: {memory_within_budget}")
        print("-" * 70)
        print(f"V16 EXPANSION TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "expansion_v16",
        "expected_expansions": expected_expansions,
        "actual_expansions": actual_expansions,
        "expansion_rate_correct": expansion_rate_correct,
        "expected_final_size": expected_final_size,
        "actual_final_size": actual_final_size,
        "size_correct": size_correct,
        "memory_within_budget": memory_within_budget,
        "expansion_events": expansion_events,
        "passed": passed,
    }


def run_stability_comparison(config: SubstrateConfig16, verbose: bool = True) -> Dict[str, Any]:
    """Compare V16 stability metrics with V15-3D baseline.

    V15-3D showed:
    - r_norm = 0.89 (dispersed to 89% of grid radius)
    - 0% variance (very stable)

    V16 should show:
    - Lower r_norm (patterns have room to find equilibrium)
    - Similar or better stability

    Args:
        config: V16 configuration
        verbose: Print details

    Returns:
        Comparison results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("V16 vs V15-3D STABILITY COMPARISON")
        print("=" * 70)

    grid = ExpandingGrid3D(
        initial_size=config.initial_size,
        expansion_rate=config.expansion_rate
    )
    evolution = ExpandingEvolution3D(grid, config)

    test_ticks = min(200, config.max_ticks)
    if verbose:
        print(f"Running {test_ticks} ticks to measure stability...")

    r_norm_history = []

    for tick in range(test_ticks):
        try:
            evolution.evolve_one_tick()
        except MemoryError:
            if verbose:
                print(f"  Memory limit reached at tick {tick+1}")
            break

        if (tick + 1) % 20 == 0:
            spatial = compute_spatial_distribution_3d(grid, grid.origin)
            r_norm_history.append({
                "tick": tick + 1,
                "r_norm": spatial["r_mean_norm"],
                "grid_size": grid.current_size,
            })

            if verbose and (tick + 1) % 50 == 0:
                print(f"  Tick {tick+1:4d}: grid={grid.current_size}^3, r_norm={spatial['r_mean_norm']:.4f}")

    if len(r_norm_history) < 4:
        return {"test": "stability_comparison", "passed": False, "error": "Insufficient data"}

    # Analyze late-phase stability
    late_history = r_norm_history[len(r_norm_history)//2:]
    r_norms = [h["r_norm"] for h in late_history]

    r_mean = float(np.mean(r_norms))
    r_std = float(np.std(r_norms))
    variance_pct = (r_std / r_mean * 100) if r_mean > 0 else 0.0

    # V15-3D baseline
    v15_3d_r_norm = 0.89
    v15_3d_variance = 0.0  # 0% variance

    # Comparison
    r_norm_lower = r_mean < v15_3d_r_norm  # Patterns not dispersed to edge
    stability_similar = variance_pct < 5.0  # Similar or better stability

    passed = stability_similar  # Main criterion

    if verbose:
        print()
        print(f"V16 Results (late phase):")
        print(f"  r_norm mean: {r_mean:.4f}")
        print(f"  r_norm std: {r_std:.4f}")
        print(f"  variance: {variance_pct:.2f}%")
        print()
        print(f"V15-3D Baseline:")
        print(f"  r_norm: {v15_3d_r_norm}")
        print(f"  variance: {v15_3d_variance}%")
        print()
        print(f"Comparison:")
        print(f"  r_norm lower than V15-3D (not at edge): {r_norm_lower}")
        print(f"  Stability similar or better (<5%): {stability_similar}")
        print("-" * 70)
        print(f"V16 STABILITY COMPARISON: {'PASSED' if passed else 'NEEDS INVESTIGATION'}")

    return {
        "test": "stability_comparison",
        "v16_r_norm_mean": r_mean,
        "v16_r_norm_std": r_std,
        "v16_variance_pct": variance_pct,
        "v15_3d_r_norm": v15_3d_r_norm,
        "v15_3d_variance": v15_3d_variance,
        "r_norm_lower": r_norm_lower,
        "stability_similar": stability_similar,
        "r_norm_history": r_norm_history,
        "passed": passed,
    }


def main():
    """Run V16 experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V16 Expanding Grid Zero-Parameter Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_v16.py --ticks 500
  python experiment_v16.py --ticks 100 --initial 15 --rate 5
  python experiment_v16.py --test gamma
  python experiment_v16.py --test expansion
  python experiment_v16.py --test stability
  python experiment_v16.py --all
        """
    )
    parser.add_argument("--ticks", type=int, default=500, help="Number of ticks (default: 500)")
    parser.add_argument("--initial", type=int, default=20, help="Initial grid size (default: 20)")
    parser.add_argument("--rate", type=int, default=5, help="Expansion rate (default: 5)")
    parser.add_argument("--memory", type=float, default=2000.0, help="Memory limit MB (default: 2000)")
    parser.add_argument("--interval", type=int, default=50, help="Verbose interval (default: 50)")
    parser.add_argument("--output", type=str, default="results/v16_experiment.json")
    parser.add_argument("--test", type=str, choices=["gamma", "expansion", "stability"],
                        help="Run specific test")
    parser.add_argument("--all", action="store_true", help="Run all validation tests")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    config = create_config(
        initial_size=args.initial,
        expansion_rate=args.rate,
        max_memory_mb=args.memory,
        max_ticks=args.ticks,
        random_seed=args.seed
    )

    results = {}

    if args.test == "gamma":
        results = run_gamma_accumulation_test(config, verbose=not args.quiet)
        output_file = "results/v16_gamma_test.json"
    elif args.test == "expansion":
        results = run_expansion_test(config, verbose=not args.quiet)
        output_file = "results/v16_expansion_test.json"
    elif args.test == "stability":
        results = run_stability_comparison(config, verbose=not args.quiet)
        output_file = "results/v16_stability_test.json"
    elif args.all:
        # Run all tests
        results = {
            "gamma_test": run_gamma_accumulation_test(config, verbose=not args.quiet),
            "expansion_test": run_expansion_test(config, verbose=not args.quiet),
            "stability_test": run_stability_comparison(config, verbose=not args.quiet),
        }
        # Summary
        all_passed = all(r.get("passed", False) for r in results.values()
                        if isinstance(r, dict) and "passed" in r)
        results["all_passed"] = all_passed

        if not args.quiet:
            print("\n" + "=" * 70)
            print("V16 VALIDATION SUMMARY")
            print("=" * 70)
            for name, r in results.items():
                if name != "all_passed" and isinstance(r, dict):
                    status = "PASSED" if r.get("passed", False) else "FAILED/N/A"
                    print(f"  {name}: {status}")
            print("-" * 70)
            print(f"  ALL TESTS: {'PASSED' if all_passed else 'SOME FAILED'}")
            print("=" * 70)

        output_file = "results/v16_all_tests.json"
    else:
        # Default: run main experiment
        results = run_v16_experiment(
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
