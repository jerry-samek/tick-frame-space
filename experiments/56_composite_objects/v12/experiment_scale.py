"""
V12 Experiment: Scale Invariance Test

Tests the hypothesis that parameters as tick-ratios produce scale-invariant behavior.

Method: Hybrid approach - fixed grids at different sizes, but parameters derived
from grid_size as "effective tick".

Test matrix:
| Grid Size | Window | Imprint | Well | Expected |
|-----------|--------|---------|------|----------|
| 50        | 25     | 5.0     | 25.0 | Stable (same ratios) |
| 100       | 50     | 10.0    | 50.0 | V11 baseline |
| 200       | 100    | 20.0    | 100.0 | Stable (same ratios) |

Success criterion: Patterns are stable at all scales with similar normalized metrics.
If successful, this validates that parameters are tick ratios, not absolute values.
"""

import sys
import os
import time
import json
import math
from pathlib import Path
from typing import List, Dict, Any

# Add paths
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
v9_path = Path(__file__).parent.parent / "v9"
v10_path = Path(__file__).parent.parent / "v10"
v11_path = Path(__file__).parent.parent / "v11"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v9_path))
sys.path.insert(0, str(v10_path))
sys.path.insert(0, str(v11_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import track_pattern_positions

# V10 imports (renormalization-based)
from gamma_wells_v10 import GammaWellSystemV10
from gamma_history_v10 import GammaHistoryCommitterV10

# V12 config
from config_v12 import TickRatioConfig, GRID_SIZES, create_tick_ratio_config


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config: TickRatioConfig) -> List:
    """Initialize cloud patterns with scaled parameters."""
    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    for i in range(config.n_patterns):
        r = rng.normal(config.pattern_init_radius_mean, config.pattern_init_radius_std)
        r = max(config.pattern_size, r)
        theta = rng.uniform(0, 2 * math.pi)

        px = int(center_x + r * math.cos(theta))
        py = int(center_y + r * math.sin(theta))

        px = max(0, min(grid.width - config.pattern_size, px))
        py = max(0, min(grid.height - config.pattern_size, py))

        sample = SampleCell(px, py, size=config.pattern_size)
        instance = PatternInstance(sample, "monopole", instance_id=f"cloud_{i}")
        instance.write_to_grid(grid, library)
        patterns.append(instance)

    return patterns


def compute_cloud_stats(
    grid: PlanckGrid,
    patterns: List,
    center: tuple,
    grid_size: int
) -> Dict[str, Any]:
    """Compute cloud statistics with normalized metrics."""
    track_pattern_positions(grid, patterns, search_radius=15)

    radii = []
    for p in patterns:
        dx = p.sample.center_x - center[0]
        dy = p.sample.center_y - center[1]
        r = math.sqrt(dx * dx + dy * dy)
        radii.append(r)

    stats = grid.get_field_statistics()

    # Absolute metrics
    r_mean = float(np.mean(radii)) if radii else 0.0
    r_std = float(np.std(radii)) if radii else 0.0

    # Normalized metrics (scale-independent)
    # Normalize radius by grid_size/2 (so center-to-edge = 1.0)
    half_grid = grid_size / 2.0
    r_mean_norm = r_mean / half_grid if half_grid > 0 else 0.0
    r_std_norm = r_std / half_grid if half_grid > 0 else 0.0

    # Normalize energy by grid area (energy density)
    area = grid_size * grid_size
    energy_density = stats["total_energy"] / area if area > 0 else 0.0

    return {
        # Absolute
        "r_mean": r_mean,
        "r_std": r_std,
        "r_min": float(np.min(radii)) if radii else 0.0,
        "r_max": float(np.max(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
        # Normalized (scale-independent)
        "r_mean_norm": r_mean_norm,
        "r_std_norm": r_std_norm,
        "energy_density": energy_density,
    }


def run_scale_experiment(
    grid_size: int,
    num_ticks: int = 2000,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run V12 scale experiment with tick-ratio parameters.

    Args:
        grid_size: Grid dimension (= effective tick)
        num_ticks: Number of ticks to run
        verbose: Print progress

    Returns:
        Results dictionary with absolute and normalized metrics
    """
    config = create_tick_ratio_config(grid_size)
    config.num_ticks = num_ticks

    if verbose:
        print(f"\n{'='*60}")
        print(f"V12 SCALE TEST: grid={grid_size} (tick={config.effective_tick})")
        print(f"{'='*60}")
        print(f"Derived: window={config.gamma_window_size}, "
              f"imprint={config.gamma_imprint_k:.1f}, well={config.target_gamma_k:.1f}")
        print(f"Patterns: {config.n_patterns}, init_radius: {config.pattern_init_radius_mean:.1f}")

    grid = PlanckGrid(config.grid_width, config.grid_height)

    # V10 gamma well system with V12 derived well strength
    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

    # V10 history committer with V12 derived parameters
    history_committer = GammaHistoryCommitterV10(
        grid,
        window_size=config.gamma_window_size,
        imprint_strength=config.gamma_imprint_k,
        normalization_type=config.normalization_type,
        normalization_scale=config.normalization_scale
    )

    gamma_system.compute_gamma_field(history_committer)

    library = PatternLibrary(pattern_size=config.pattern_size)
    center = (center_x, center_y)
    cloud_patterns = initialize_cloud(grid, library, config)

    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    history = []
    start_time = time.time()

    # Scale progress interval with grid size
    progress_interval = max(100, num_ticks // 20)

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        if (tick + 1) % progress_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
            hist_state = history_committer.get_state()

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_mean_norm": stats["r_mean_norm"],
                "r_std_norm": stats["r_std_norm"],
                "energy": stats["total_energy"],
                "energy_density": stats["energy_density"],
                "normalized_max": hist_state["normalized_max"],
            })

            if verbose:
                print(f"[{tick+1:4d}] r={stats['r_mean']:.2f} (norm={stats['r_mean_norm']:.3f}), "
                      f"E_dens={stats['energy_density']:.3f}")

    elapsed = time.time() - start_time

    final_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
    final_history = history_committer.get_state()

    # Stability metrics (after initial transient)
    late_start = max(500, num_ticks // 4)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means = [h["r_mean"] for h in late_history]
        r_means_norm = [h["r_mean_norm"] for h in late_history]
        energies = [h["energy"] for h in late_history]
        energy_densities = [h["energy_density"] for h in late_history]

        stability_metrics = {
            # Absolute
            "r_mean_avg": float(np.mean(r_means)),
            "r_mean_std": float(np.std(r_means)),  # Drift indicator
            # Normalized (scale-independent)
            "r_mean_norm_avg": float(np.mean(r_means_norm)),
            "r_mean_norm_std": float(np.std(r_means_norm)),
            "energy_density_avg": float(np.mean(energy_densities)),
            "energy_density_std": float(np.std(energy_densities)),
        }

    if verbose:
        print(f"\nFinal: r={final_stats['r_mean']:.2f} (norm={final_stats['r_mean_norm']:.3f})")
        if stability_metrics:
            print(f"Stability (normalized): r_norm_avg={stability_metrics['r_mean_norm_avg']:.3f}, "
                  f"drift={stability_metrics['r_mean_norm_std']:.4f}")
        print(f"Time: {elapsed:.1f}s")

    return {
        "grid_size": grid_size,
        "effective_tick": config.effective_tick,
        "params": {
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "target_gamma_k": config.target_gamma_k,
            "n_patterns": config.n_patterns,
            "jitter_strength": config.jitter_strength,
        },
        "ratios": {
            "window_ratio": config.WINDOW_RATIO,
            "imprint_ratio": config.IMPRINT_RATIO,
            "window_imprint_ratio": config.gamma_window_size / config.gamma_imprint_k,
        },
        "final_stats": final_stats,
        "final_history": final_history,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
    }


def run_scale_sweep(
    grid_sizes: List[int] = None,
    num_ticks: int = 2000,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run scale sweep to test tick-ratio invariance.

    Tests the hypothesis that parameters as tick-ratios produce
    scale-invariant behavior.

    Args:
        grid_sizes: List of grid sizes to test
        num_ticks: Number of ticks per experiment
        verbose: Print progress

    Returns:
        Combined results with scale-invariance analysis
    """
    if grid_sizes is None:
        grid_sizes = GRID_SIZES

    print("=" * 70)
    print("V12 SCALE INVARIANCE TEST")
    print("=" * 70)
    print()
    print("Hypothesis: Parameters as tick-ratios produce scale-invariant behavior")
    print()
    print("The tick-stream is the fundamental substrate:")
    print("  - Each tick adds 1 causal energy quantum")
    print("  - Grid size = 'effective tick' (visualization at tick N)")
    print()
    print(f"Testing grid sizes: {grid_sizes}")
    print()

    # Show parameter derivations
    print("-" * 70)
    print("Parameter derivations (tick ratios):")
    print(f"{'Grid':>6} | {'Tick':>6} | {'Window':>6} | {'Imprint':>8} | {'Well':>6} | {'Patterns':>8}")
    print("-" * 70)
    for gs in grid_sizes:
        config = create_tick_ratio_config(gs)
        print(f"{gs:>6} | {config.effective_tick:>6} | {config.gamma_window_size:>6} | "
              f"{config.gamma_imprint_k:>8.1f} | {config.target_gamma_k:>6.1f} | "
              f"{config.n_patterns:>8}")
    print("-" * 70)
    print()

    all_results = {}
    summary = []

    for gs in grid_sizes:
        results = run_scale_experiment(
            grid_size=gs,
            num_ticks=num_ticks,
            verbose=verbose
        )
        all_results[f"grid_{gs}"] = results

        sm = results.get("stability_metrics", {})
        summary.append({
            "grid_size": gs,
            "effective_tick": results["effective_tick"],
            "window": results["params"]["gamma_window_size"],
            "imprint": results["params"]["gamma_imprint_k"],
            "well": results["params"]["target_gamma_k"],
            "patterns": results["params"]["n_patterns"],
            # Absolute
            "r_mean": results["final_stats"]["r_mean"],
            "r_std": results["final_stats"]["r_std"],
            "energy": results["final_stats"]["total_energy"],
            # Normalized (scale-independent)
            "r_mean_norm": results["final_stats"]["r_mean_norm"],
            "r_std_norm": results["final_stats"]["r_std_norm"],
            "energy_density": results["final_stats"]["energy_density"],
            "drift_norm": sm.get("r_mean_norm_std", -1),
            "elapsed": results["elapsed_seconds"],
        })

    # Print summary table
    print("\n" + "=" * 70)
    print("SCALE SWEEP SUMMARY")
    print("=" * 70)

    # Absolute metrics
    print("\n--- Absolute Metrics ---")
    print(f"{'Grid':>6} | {'r_mean':>8} | {'r_std':>8} | {'Energy':>10}")
    print("-" * 40)
    for row in summary:
        print(f"{row['grid_size']:>6} | {row['r_mean']:>8.2f} | {row['r_std']:>8.3f} | "
              f"{row['energy']:>10d}")

    # Normalized metrics (scale-independent)
    print("\n--- Normalized Metrics (Scale-Independent) ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'std_norm':>8} | {'E_dens':>10} | {'Drift':>8}")
    print("-" * 55)
    for row in summary:
        drift_str = f"{row['drift_norm']:.5f}" if row['drift_norm'] >= 0 else "N/A"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | {row['r_std_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | {drift_str:>8}")

    # Scale invariance analysis
    print("\n" + "=" * 70)
    print("SCALE INVARIANCE ANALYSIS")
    print("=" * 70)

    # Check if normalized metrics are consistent across scales
    r_norms = [row['r_mean_norm'] for row in summary]
    e_densities = [row['energy_density'] for row in summary]
    drifts = [row['drift_norm'] for row in summary if row['drift_norm'] >= 0]

    r_norm_mean = np.mean(r_norms) if r_norms else 0
    r_norm_std = np.std(r_norms) if r_norms else 0
    r_norm_cv = r_norm_std / r_norm_mean if r_norm_mean > 0 else float('inf')

    e_dens_mean = np.mean(e_densities) if e_densities else 0
    e_dens_std = np.std(e_densities) if e_densities else 0
    e_dens_cv = e_dens_std / e_dens_mean if e_dens_mean > 0 else float('inf')

    print(f"\nNormalized radius (r/half_grid):")
    print(f"  Mean across scales: {r_norm_mean:.4f}")
    print(f"  Std across scales:  {r_norm_std:.4f}")
    print(f"  CV (coefficient of variation): {r_norm_cv:.3f}")

    print(f"\nEnergy density (E/area):")
    print(f"  Mean across scales: {e_dens_mean:.4f}")
    print(f"  Std across scales:  {e_dens_std:.4f}")
    print(f"  CV: {e_dens_cv:.3f}")

    # Determine success
    CV_THRESHOLD = 0.15  # 15% variation is acceptable
    DRIFT_THRESHOLD = 0.01  # Normalized drift threshold

    scale_invariant = r_norm_cv < CV_THRESHOLD
    stable = all(d < DRIFT_THRESHOLD for d in drifts) if drifts else False

    print("\n" + "-" * 70)
    print("VERDICT:")
    print("-" * 70)

    if scale_invariant and stable:
        print("\nSUCCESS: Scale-invariant and stable!")
        print("The tick-ratio model is VALIDATED.")
        print("\nConclusion: Parameters derive from tick (grid_size):")
        print("  - gamma_window_size = tick / 2")
        print("  - gamma_imprint_k = tick / 10")
        print("  - target_gamma_k = window (V11)")
    elif scale_invariant:
        print("\nPARTIAL SUCCESS: Scale-invariant but some instability.")
        print("Tick-ratio derivation is valid, but absolute stability needs work.")
    elif stable:
        print("\nPARTIAL SUCCESS: Stable but not scale-invariant.")
        print("Parameters may need scale-dependent adjustment.")
    else:
        print("\nFAILED: Neither scale-invariant nor stable.")
        print("The tick-ratio model needs revision.")

    print(f"\nScale invariance: {r_norm_cv:.3f} CV {'<' if scale_invariant else '>='} {CV_THRESHOLD} threshold")
    print(f"Stability: {'All' if stable else 'Not all'} drifts < {DRIFT_THRESHOLD}")

    return {
        "all_results": all_results,
        "summary": summary,
        "analysis": {
            "r_norm_mean": r_norm_mean,
            "r_norm_std": r_norm_std,
            "r_norm_cv": r_norm_cv,
            "e_dens_mean": e_dens_mean,
            "e_dens_std": e_dens_std,
            "e_dens_cv": e_dens_cv,
            "scale_invariant": scale_invariant,
            "stable": stable,
            "cv_threshold": CV_THRESHOLD,
            "drift_threshold": DRIFT_THRESHOLD,
        },
        "validated": scale_invariant and stable,
    }


def main():
    """Run V12 scale invariance experiments."""
    import argparse

    parser = argparse.ArgumentParser(description="V12 Scale Invariance Test")
    parser.add_argument("--ticks", type=int, default=2000, help="Number of ticks")
    parser.add_argument("--grid", type=int, help="Single grid size to test")
    parser.add_argument("--grids", type=str, help="Comma-separated grid sizes")
    parser.add_argument("--output", type=str, default="results/scale_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.grid:
        # Single grid test
        results = run_scale_experiment(
            grid_size=args.grid,
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = f"results/grid_{args.grid}.json"
    elif args.grids:
        # Custom grid list
        grid_sizes = [int(g.strip()) for g in args.grids.split(',')]
        results = run_scale_sweep(
            grid_sizes=grid_sizes,
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = args.output
    else:
        # Default sweep (50, 100, 200)
        results = run_scale_sweep(
            num_ticks=args.ticks,
            verbose=not args.quiet
        )
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
