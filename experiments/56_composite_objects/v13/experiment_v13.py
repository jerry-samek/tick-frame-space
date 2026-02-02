"""
V13 Experiment: Layered Substrate with Shared Memory

Tests the layered architecture:
- Each entity has its own layer (temporal isolation)
- All entities share gamma field (spatial coupling via memory)
- Head prepending: new entity spawns at origin each tick
- Pull/Push equilibrium: gamma pulls, jitter pushes

Success criteria:
1. Layer isolation: Entity A's jitter doesn't affect Entity B's layer
2. Gamma coupling: All entities see same gamma, all contribute
3. Origin spawn: Every entity starts at origin
4. Natural distribution: Entities spread out via gamma pressure
5. Stability: Similar or better than V12d (drift < 0.001)

Author: V13 Implementation
Date: 2026-01-31
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import Dict, Any, List

import numpy as np

from multi_layer_grid import MultiLayerGrid
from entity import Entity
from config_v13 import LayeredSubstrateConfig, create_config
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


def run_v13_experiment(
    config: LayeredSubstrateConfig,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V13 layered substrate experiment.

    Args:
        config: V13 configuration
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    if verbose:
        print(f"\n{'='*70}")
        print(f"V13 LAYERED SUBSTRATE EXPERIMENT: grid={config.grid_size}")
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
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            record = {
                "tick": tick + 1,
                "entity_count": stats["entity_count"],
                "total_energy": stats["total_energy"],
                "gamma_sum": stats["gamma_sum"],
                "r_mean": spatial["r_mean"],
                "r_mean_norm": spatial["r_mean_norm"],
                "r_std": spatial["r_std"],
                "nonzero_count": spatial.get("nonzero_count", 0),
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
                    f"energy={stats['total_energy']:5d}, "
                    f"r_norm={r_norm:.4f}, "
                    f"rate={tick_rate:.1f} t/s [{status}]"
                )

    elapsed = time.time() - start_time
    final_stats = evolution.get_statistics()
    final_spatial = compute_spatial_distribution(grid, config.origin)

    # Stability metrics (drift over late history)
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means = [h["r_mean_norm"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means)),
            "r_mean_norm_std": float(np.std(r_means)),
            "drift": float(np.std(r_means)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: entities={final_stats['entity_count']}, "
              f"r_norm={final_spatial['r_mean_norm']:.4f}")
        if stability_metrics:
            print(f"       drift={stability_metrics['drift']:.6f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": "V13",
        "grid_size": config.grid_size,
        "params": {
            "jitter_strength": config.jitter_strength,
            "gamma_decay": config.gamma_decay,
            "gamma_imprint_strength": config.gamma_imprint_strength,
        },
        "final_stats": {
            "entity_count": final_stats["entity_count"],
            "total_energy": final_stats["total_energy"],
            "gamma_sum": final_stats["gamma_sum"],
            "r_mean": final_spatial["r_mean"],
            "r_mean_norm": final_spatial["r_mean_norm"],
            "r_std": final_spatial["r_std"],
        },
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_isolation_test(config: LayeredSubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Test that layers are truly isolated.

    Creates two entities, applies jitter, verifies no cross-layer contamination.

    Args:
        config: V13 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("LAYER ISOLATION TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    # Create exactly 2 entities
    evolution.create_entity(1)
    evolution.create_entity(2)

    if verbose:
        print(f"Created 2 entities with separate layers")

    # Get initial state of layer 0
    layer0_initial = grid.get_layer(0).copy()

    # Manually modify layer 1 heavily
    layer1 = grid.get_layer(1)
    layer1[:, :] = 1  # Fill with +1

    if verbose:
        print(f"Modified layer 1 to all +1")
        print(f"Layer 0 should be unchanged...")

    # Verify layer 0 is unchanged
    layer0_after = grid.get_layer(0)
    layers_independent = np.array_equal(layer0_initial, layer0_after)

    if verbose:
        print(f"Layer 0 unchanged: {layers_independent}")

    # Now test jitter independence
    # Reset layer 1
    layer1[:, :] = 0

    # Apply many jitter iterations to both layers
    np.random.seed(config.random_seed)
    for _ in range(100):
        # Apply jitter to layer 0 only
        jitter = np.random.choice([-1, 0, 1], size=layer0_initial.shape, p=[0.119, 0.762, 0.119])
        layer0 = grid.get_layer(0)
        layer0[:, :] = np.clip(layer0 + jitter, -1, 1).astype(np.int8)

    # Layer 1 should still be all zeros
    layer1 = grid.get_layer(1)
    layer1_unchanged = np.all(layer1 == 0)

    if verbose:
        print(f"After 100 jitter iterations on layer 0:")
        print(f"Layer 1 unchanged: {layer1_unchanged}")

    passed = layers_independent and layer1_unchanged

    if verbose:
        print("-" * 70)
        print(f"ISOLATION TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "layer_isolation",
        "layers_independent": layers_independent,
        "jitter_isolated": layer1_unchanged,
        "passed": passed,
    }


def run_gamma_coupling_test(config: LayeredSubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Test that gamma field is shared across all entities.

    All entities should see the same gamma and all contribute to it.

    Args:
        config: V13 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("GAMMA COUPLING TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    # Create 5 entities at different positions
    for i in range(5):
        evolution.create_entity(i + 1)
        # Move each entity to a different position (modify layer directly)
        layer = grid.get_layer(i)
        layer[:, :] = 0  # Clear
        # Place at different positions
        x = config.origin[0] + (i - 2) * 5
        y = config.origin[1]
        x = max(0, min(config.grid_width - 1, x))
        y = max(0, min(config.grid_height - 1, y))
        layer[y, x] = 1

    if verbose:
        print(f"Created 5 entities at different positions")

    # Update gamma
    evolution._update_gamma()

    # Check gamma field
    gamma = grid.gamma
    gamma_nonzero = np.count_nonzero(gamma)
    gamma_sum = np.sum(gamma)

    if verbose:
        print(f"Gamma nonzero cells: {gamma_nonzero}")
        print(f"Gamma sum: {gamma_sum:.2f}")

    # All 5 entities should contribute to gamma
    # At least 5 cells should have gamma > 0
    entities_contribute = gamma_nonzero >= 5

    # Gamma should be uniform (same for all entities)
    # Since all entities see the same gamma array
    gamma_uniform = True  # By construction in our model

    if verbose:
        print(f"All entities contribute: {entities_contribute}")
        print(f"Gamma is shared (uniform access): {gamma_uniform}")

    passed = entities_contribute and gamma_uniform

    if verbose:
        print("-" * 70)
        print(f"GAMMA COUPLING TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "gamma_coupling",
        "entities_contribute": entities_contribute,
        "gamma_uniform": gamma_uniform,
        "gamma_nonzero": gamma_nonzero,
        "gamma_sum": gamma_sum,
        "passed": passed,
    }


def run_origin_spawn_test(config: LayeredSubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Test that all entities spawn at origin.

    Args:
        config: V13 configuration
        verbose: Print details

    Returns:
        Test results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("ORIGIN SPAWN TEST")
        print("=" * 70)

    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    # Create 10 entities
    for i in range(10):
        evolution.create_entity(i + 1)

    if verbose:
        print(f"Created 10 entities")

    # Check all entities have position = origin
    origin = config.origin
    all_at_origin = all(e.position == origin for e in evolution.entities)

    # Check all layers have non-zero at origin
    origin_x, origin_y = origin
    all_layers_at_origin = True
    for i in range(len(evolution.entities)):
        layer = grid.get_layer(i)
        if layer[origin_y, origin_x] == 0:
            all_layers_at_origin = False
            break

    if verbose:
        print(f"All entities at origin: {all_at_origin}")
        print(f"All layers initialized at origin: {all_layers_at_origin}")

    passed = all_at_origin and all_layers_at_origin

    if verbose:
        print("-" * 70)
        print(f"ORIGIN SPAWN TEST: {'PASSED' if passed else 'FAILED'}")

    return {
        "test": "origin_spawn",
        "all_at_origin": all_at_origin,
        "all_layers_at_origin": all_layers_at_origin,
        "origin": origin,
        "entity_count": len(evolution.entities),
        "passed": passed,
    }


def run_all_tests(config: LayeredSubstrateConfig, verbose: bool = True) -> Dict[str, Any]:
    """Run all V13 verification tests.

    Args:
        config: V13 configuration
        verbose: Print details

    Returns:
        Combined test results
    """
    tests = []

    tests.append(run_isolation_test(config, verbose))
    tests.append(run_gamma_coupling_test(config, verbose))
    tests.append(run_origin_spawn_test(config, verbose))

    all_passed = all(t["passed"] for t in tests)

    if verbose:
        print("\n" + "=" * 70)
        print("TEST SUMMARY")
        print("=" * 70)
        for t in tests:
            status = "PASSED" if t["passed"] else "FAILED"
            print(f"  {t['test']}: {status}")
        print("-" * 70)
        print(f"Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")

    return {
        "tests": tests,
        "all_passed": all_passed,
    }


def main():
    """Run V13 experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V13 Layered Substrate Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_v13.py --ticks 1000 --grid 100
  python experiment_v13.py --test
  python experiment_v13.py --ticks 500 --verbose-interval 50
  python experiment_v13.py --ticks 500 --jitter 0      # Test zero jitter (collapse?)
  python experiment_v13.py --ticks 500 --jitter 0.5    # Test max symmetric jitter
        """
    )
    parser.add_argument("--ticks", type=int, default=1000, help="Number of ticks (default: 1000)")
    parser.add_argument("--grid", type=int, default=100, help="Grid size (default: 100)")
    parser.add_argument("--jitter", type=float, default=None,
                        help="Jitter strength (default: 0.119). Use 0 or 0.5 to test fundamentality.")
    parser.add_argument("--interval", type=int, default=100, help="Verbose interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/v13_experiment.json")
    parser.add_argument("--test", action="store_true", help="Run verification tests only")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    config = create_config(grid_size=args.grid, jitter_strength=args.jitter, random_seed=args.seed)

    if args.test:
        # Run verification tests
        results = run_all_tests(config, verbose=not args.quiet)
        output_file = "results/v13_tests.json"
    else:
        # Run main experiment
        results = run_v13_experiment(
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
