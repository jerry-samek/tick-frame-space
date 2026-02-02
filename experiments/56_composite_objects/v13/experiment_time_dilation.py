"""
V13 Experiment: Time Dilation Integration

Tests emergent time dilation from Experiment 51:
- Heavy entities (high tick_budget) create computational load
- Load depletes local energy field
- Low energy -> slower gamma decay -> time dilation
- Creates "gravitational wells" in the memory field

Hypothesis: gamma_half_life(r=5) > gamma_half_life(r=20)
(Memory decays slower near entity clusters than in empty space)

Author: V13 Implementation
Date: 2026-01-31
Based on: Experiment 51v9 (Goldilocks zone dynamics)
"""

import sys
import os
import time
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

import numpy as np

from multi_layer_grid import MultiLayerGrid
from entity import Entity
from config_v13 import LayeredSubstrateConfig, create_config
from layered_evolution import LayeredEvolution


def measure_gamma_halflife_by_radius(
    grid: MultiLayerGrid,
    origin: Tuple[int, int],
    radial_bins: List[Tuple[float, float]]
) -> Dict[str, float]:
    """Measure average gamma and effective decay rate by radial distance.

    Args:
        grid: MultiLayerGrid with gamma field
        origin: Center point (x, y)
        radial_bins: List of (r_min, r_max) tuples defining shells

    Returns:
        Dict with gamma stats per radial bin
    """
    origin_x, origin_y = origin

    # Create distance field
    y_coords, x_coords = np.ogrid[:grid.height, :grid.width]
    dx = x_coords - origin_x
    dy = y_coords - origin_y
    distances = np.sqrt(dx**2 + dy**2)

    results = {}
    for i, (r_min, r_max) in enumerate(radial_bins):
        mask = (distances >= r_min) & (distances < r_max)
        if np.any(mask):
            gamma_in_shell = grid.gamma[mask]
            energy_in_shell = grid.energy_field[mask]
            load_in_shell = grid.load_field[mask]

            results[f"shell_{i}_r{r_min:.0f}_{r_max:.0f}"] = {
                "gamma_mean": float(np.mean(gamma_in_shell)),
                "gamma_max": float(np.max(gamma_in_shell)),
                "energy_mean": float(np.mean(energy_in_shell)),
                "energy_min": float(np.min(energy_in_shell)),
                "load_mean": float(np.mean(load_in_shell)),
                "load_max": float(np.max(load_in_shell)),
                "cell_count": int(np.sum(mask)),
            }

    return results


def run_time_dilation_experiment(
    config: LayeredSubstrateConfig,
    num_ticks: int = 500,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run time dilation experiment.

    Tests that:
    1. Dense entity clusters create high load fields
    2. High load drains local energy
    3. Low energy regions have slower gamma decay
    4. This creates "gravitational wells" in the gamma field

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
        print(f"V13 TIME DILATION EXPERIMENT: grid={config.grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    # Create grid and evolution
    grid = MultiLayerGrid(config.grid_width, config.grid_height, config.energy_max)
    evolution = LayeredEvolution(grid, config)

    # Define radial bins for analysis
    # Adjust bins based on grid size to ensure we capture far regions
    half_grid = max(config.grid_size // 2, 35)  # Ensure we have some far region
    radial_bins = [
        (0, 5),      # Core: r < 5 (should have highest load, lowest energy)
        (5, 10),     # Inner: 5 <= r < 10
        (10, 20),    # Middle: 10 <= r < 20
        (20, half_grid),    # Far: 20 <= r < half_grid
    ]

    history = []
    radial_history = []
    start_time = time.time()

    for tick in range(num_ticks):
        evolution.evolve_one_tick()

        if (tick + 1) % verbose_interval == 0:
            stats = evolution.get_statistics()
            radial = measure_gamma_halflife_by_radius(grid, config.origin, radial_bins)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            record = {
                "tick": tick + 1,
                **stats,
            }
            history.append(record)
            radial_history.append({"tick": tick + 1, **radial})

            if verbose:
                # Extract key metrics for display
                core_energy = radial.get("shell_0_r0_5", {}).get("energy_mean", config.energy_max)
                far_energy = radial.get(f"shell_4_r30_{half_grid}", {}).get("energy_mean", config.energy_max)
                core_load = radial.get("shell_0_r0_5", {}).get("load_max", 0)

                print(
                    f"[{tick+1:5d}] entities={stats['entity_count']:4d}, "
                    f"load_max={stats['load_max']:.2f}, "
                    f"E_core={core_energy:.1f}, E_far={far_energy:.1f}, "
                    f"rate={tick_rate:.1f} t/s"
                )

    elapsed = time.time() - start_time
    final_stats = evolution.get_statistics()
    final_radial = measure_gamma_halflife_by_radius(grid, config.origin, radial_bins)

    # Compute time dilation metrics
    core_data = final_radial.get("shell_0_r0_5", {})
    far_data = final_radial.get(f"shell_3_r20_{half_grid}", {})

    dilation_metrics = {}
    if core_data and far_data:
        # Energy ratio: core should be lower than far (depleted by load)
        energy_ratio = core_data.get("energy_mean", 1) / max(far_data.get("energy_mean", 1), 0.001)

        # Gamma ratio: core should be higher (slower decay = memory persists)
        gamma_ratio = core_data.get("gamma_mean", 0) / max(far_data.get("gamma_mean", 0.001), 0.001)

        dilation_metrics = {
            "energy_ratio_core_vs_far": energy_ratio,
            "gamma_ratio_core_vs_far": gamma_ratio,
            "core_load_max": core_data.get("load_max", 0),
            "core_energy_mean": core_data.get("energy_mean", 0),
            "far_energy_mean": far_data.get("energy_mean", 0),
            "core_gamma_mean": core_data.get("gamma_mean", 0),
            "far_gamma_mean": far_data.get("gamma_mean", 0),
        }

    if verbose:
        print("-" * 70)
        print("TIME DILATION ANALYSIS:")

        def fmt(val, fmt_str=".3f"):
            """Format value, handling None/missing."""
            if val is None or val == "N/A":
                return "N/A"
            try:
                return f"{val:{fmt_str}}"
            except (ValueError, TypeError):
                return str(val)

        print(f"  Energy ratio (core/far): {fmt(dilation_metrics.get('energy_ratio_core_vs_far'))}")
        print(f"  Gamma ratio (core/far): {fmt(dilation_metrics.get('gamma_ratio_core_vs_far'))}")
        print(f"  Core load_max: {fmt(dilation_metrics.get('core_load_max'), '.2f')}")
        print(f"  Core energy: {fmt(dilation_metrics.get('core_energy_mean'), '.2f')}")
        print(f"  Far energy: {fmt(dilation_metrics.get('far_energy_mean'), '.2f')}")
        print("-" * 70)
        print(f"Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

        # Interpretation
        energy_ratio = dilation_metrics.get('energy_ratio_core_vs_far')
        if energy_ratio is None:
            print("\nRESULT: Could not compute energy ratio (check radial bins)")
        elif energy_ratio < 0.9:
            print("\nRESULT: Time dilation DETECTED - energy depleted near entities")
        elif energy_ratio < 1.0:
            print("\nRESULT: Weak time dilation - slight energy depletion")
        else:
            print("\nRESULT: No time dilation - energy uniform (check parameters)")

    return {
        "config_name": "V13_time_dilation",
        "time_dilation_enabled": config.time_dilation_enabled,
        "grid_size": config.grid_size,
        "params": {
            "jitter_strength": config.jitter_strength,
            "gamma_decay": config.gamma_decay,
            "load_diffusion": config.load_diffusion,
            "load_damping": config.load_damping,
            "energy_regen": config.energy_regen,
            "energy_max": config.energy_max,
            "energy_drain_rate": config.energy_drain_rate,
        },
        "final_stats": final_stats,
        "dilation_metrics": dilation_metrics,
        "final_radial": final_radial,
        "history": history,
        "radial_history": radial_history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_baseline_comparison(
    grid_size: int = 100,
    num_ticks: int = 500,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run both baseline (no dilation) and dilation experiments for comparison.

    Args:
        grid_size: Grid dimension
        num_ticks: Number of ticks
        verbose: Print details

    Returns:
        Combined results
    """
    if verbose:
        print("\n" + "=" * 70)
        print("BASELINE VS TIME DILATION COMPARISON")
        print("=" * 70)

    # Run baseline (time dilation disabled)
    config_baseline = create_config(grid_size=grid_size)
    config_baseline.time_dilation_enabled = False

    if verbose:
        print("\n[1/2] Running BASELINE (uniform decay)...")

    baseline_results = run_time_dilation_experiment(
        config_baseline,
        num_ticks=num_ticks,
        verbose_interval=num_ticks // 5,
        verbose=verbose
    )

    # Run with time dilation
    config_dilation = create_config(grid_size=grid_size)
    config_dilation.time_dilation_enabled = True

    if verbose:
        print("\n[2/2] Running WITH TIME DILATION...")

    dilation_results = run_time_dilation_experiment(
        config_dilation,
        num_ticks=num_ticks,
        verbose_interval=num_ticks // 5,
        verbose=verbose
    )

    # Compare
    if verbose:
        print("\n" + "=" * 70)
        print("COMPARISON SUMMARY")
        print("=" * 70)

        print("\n| Metric                  | Baseline | With Dilation |")
        print("|-------------------------|----------|---------------|")

        b_stats = baseline_results.get("final_stats", {})
        d_stats = dilation_results.get("final_stats", {})

        print(f"| gamma_mean              | {b_stats.get('gamma_mean', 0):8.3f} | {d_stats.get('gamma_mean', 0):13.3f} |")
        print(f"| gamma_max               | {b_stats.get('gamma_max', 0):8.3f} | {d_stats.get('gamma_max', 0):13.3f} |")
        print(f"| load_max                | {b_stats.get('load_max', 0):8.3f} | {d_stats.get('load_max', 0):13.3f} |")
        print(f"| energy_min              | {b_stats.get('energy_min', 0):8.3f} | {d_stats.get('energy_min', 0):13.3f} |")

        b_dil = baseline_results.get("dilation_metrics", {})
        d_dil = dilation_results.get("dilation_metrics", {})

        print(f"| energy_ratio (core/far) | {b_dil.get('energy_ratio_core_vs_far', 1.0):8.3f} | {d_dil.get('energy_ratio_core_vs_far', 1.0):13.3f} |")
        print(f"| gamma_ratio (core/far)  | {b_dil.get('gamma_ratio_core_vs_far', 1.0):8.3f} | {d_dil.get('gamma_ratio_core_vs_far', 1.0):13.3f} |")

    return {
        "baseline": baseline_results,
        "dilation": dilation_results,
        "comparison": {
            "baseline_gamma_mean": baseline_results.get("final_stats", {}).get("gamma_mean", 0),
            "dilation_gamma_mean": dilation_results.get("final_stats", {}).get("gamma_mean", 0),
            "baseline_energy_ratio": baseline_results.get("dilation_metrics", {}).get("energy_ratio_core_vs_far", 1.0),
            "dilation_energy_ratio": dilation_results.get("dilation_metrics", {}).get("energy_ratio_core_vs_far", 1.0),
        }
    }


def main():
    """Run time dilation experiment."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V13 Time Dilation Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_time_dilation.py --ticks 500 --grid 100
  python experiment_time_dilation.py --compare
  python experiment_time_dilation.py --ticks 1000 --no-dilation  # Baseline only
        """
    )
    parser.add_argument("--ticks", type=int, default=500, help="Number of ticks (default: 500)")
    parser.add_argument("--grid", type=int, default=100, help="Grid size (default: 100)")
    parser.add_argument("--interval", type=int, default=100, help="Verbose interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/v13_time_dilation.json")
    parser.add_argument("--compare", action="store_true", help="Run baseline comparison")
    parser.add_argument("--no-dilation", action="store_true", help="Disable time dilation (baseline)")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")

    # Time dilation parameter overrides
    parser.add_argument("--load-diffusion", type=float, default=None, help="Load diffusion (alpha)")
    parser.add_argument("--load-damping", type=float, default=None, help="Load damping")
    parser.add_argument("--energy-regen", type=float, default=None, help="Energy regeneration")
    parser.add_argument("--energy-max", type=float, default=None, help="Max energy")
    parser.add_argument("--energy-drain", type=float, default=None, help="Energy drain rate")

    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.compare:
        # Run baseline comparison
        results = run_baseline_comparison(
            grid_size=args.grid,
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = "results/v13_dilation_comparison.json"
    else:
        # Create config
        config = create_config(grid_size=args.grid, random_seed=args.seed)
        config.time_dilation_enabled = not args.no_dilation

        # Apply parameter overrides
        if args.load_diffusion is not None:
            config.load_diffusion = args.load_diffusion
        if args.load_damping is not None:
            config.load_damping = args.load_damping
        if args.energy_regen is not None:
            config.energy_regen = args.energy_regen
        if args.energy_max is not None:
            config.energy_max = args.energy_max
        if args.energy_drain is not None:
            config.energy_drain_rate = args.energy_drain

        # Run experiment
        results = run_time_dilation_experiment(
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
