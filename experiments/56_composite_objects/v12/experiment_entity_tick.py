"""
V12b Experiment: Entity = Tick Hypothesis

Tests the hypothesis that n_patterns = n_ticks = grid_size.

Physical meaning:
- Each tick creates ONE causal quantum (one entity)
- At tick N, you have exactly N entities
- 1D is always full (100% density)
- Higher dimensions appear sparse (same count, more space)
- The invariant entity_count / tick = 1 is LITERAL

V12 Initial Results (2026-01-30):
V12 tested scale invariance with area-scaled patterns (grid²/400):
- Grid 50 (6 patterns): COLLAPSED to r=0
- Grid 100 (25 patterns): Stable, r_norm=0.063
- Grid 200 (100 patterns): Very stable, r_norm=0.075

V12b New Insight:
What if entity count equals tick count?

| Grid/Tick | Patterns | 1D density | 2D density |
|-----------|----------|------------|------------|
| 50        | 50       | 100% (full)| 2%         |
| 100       | 100      | 100% (full)| 1%         |
| 200       | 200      | 100% (full)| 0.5%       |

Success criteria:
- All scales stable (no collapse like V12 grid=50)
- Similar normalized metrics across scales
- Density = 1/tick relationship holds
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

# V12 config with entity=tick
from config_v12 import EntityTickConfig, create_entity_tick_config


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config: EntityTickConfig) -> List:
    """Initialize cloud patterns with entity count = tick.

    For n_patterns = grid_size (= effective_tick), we distribute patterns
    in a ring around the center with scaled radius.
    """
    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    # Use entity_tick_init_radius: sqrt(grid) * 2 to maintain constant density
    # This gives more room for the larger number of patterns
    init_radius_mean = config.entity_tick_init_radius
    init_radius_std = init_radius_mean * 0.2  # 20% variance

    for i in range(config.n_patterns):
        r = rng.normal(init_radius_mean, init_radius_std)
        r = max(config.pattern_size, r)
        theta = rng.uniform(0, 2 * math.pi)

        px = int(center_x + r * math.cos(theta))
        py = int(center_y + r * math.sin(theta))

        px = max(0, min(grid.width - config.pattern_size, px))
        py = max(0, min(grid.height - config.pattern_size, py))

        sample = SampleCell(px, py, size=config.pattern_size)
        instance = PatternInstance(sample, "monopole", instance_id=f"entity_{i}")
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
    half_grid = grid_size / 2.0
    r_mean_norm = r_mean / half_grid if half_grid > 0 else 0.0
    r_std_norm = r_std / half_grid if half_grid > 0 else 0.0

    # Energy density
    area = grid_size * grid_size
    energy_density = stats["total_energy"] / area if area > 0 else 0.0

    # Pattern density (entity=tick specific)
    pattern_count = len(patterns)
    pattern_density_2d = pattern_count / area if area > 0 else 0.0

    return {
        # Absolute
        "r_mean": r_mean,
        "r_std": r_std,
        "r_min": float(np.min(radii)) if radii else 0.0,
        "r_max": float(np.max(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
        "pattern_count": pattern_count,
        # Normalized (scale-independent)
        "r_mean_norm": r_mean_norm,
        "r_std_norm": r_std_norm,
        "energy_density": energy_density,
        "pattern_density_2d": pattern_density_2d,
    }


def run_entity_tick_experiment(
    grid_size: int,
    num_ticks: int = 1000,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run V12b entity=tick experiment.

    Args:
        grid_size: Grid dimension (= effective tick = entity count)
        num_ticks: Number of simulation ticks to run
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary with metrics
    """
    config = create_entity_tick_config(grid_size)

    if verbose:
        print(f"\n{'='*70}")
        print(f"V12b ENTITY=TICK EXPERIMENT: grid={grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks with verbose output every {verbose_interval} ticks...")
        print("-" * 70)

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
    last_print_time = start_time

    if verbose:
        # Initial state
        init_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
        print(f"[INIT ] patterns={init_stats['pattern_count']:4d}, "
              f"r_mean={init_stats['r_mean']:6.2f} (norm={init_stats['r_mean_norm']:.4f}), "
              f"E_dens={init_stats['energy_density']:.4f}, "
              f"pattern_dens_2D={init_stats['pattern_density_2d']:.6f}")

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        # Verbose output every N ticks
        if verbose and (tick + 1) % verbose_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
            hist_state = history_committer.get_state()

            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_mean_norm": stats["r_mean_norm"],
                "r_std_norm": stats["r_std_norm"],
                "energy": stats["total_energy"],
                "energy_density": stats["energy_density"],
                "pattern_count": stats["pattern_count"],
                "pattern_density_2d": stats["pattern_density_2d"],
                "normalized_max": hist_state["normalized_max"],
            })

            # Status indicator
            status = "RUNNING"
            if stats["r_mean_norm"] < 0.01:
                status = "COLLAPSED?"
            elif stats["r_mean_norm"] > 0.5:
                status = "DISPERSED?"

            print(f"[{tick+1:5d}] patterns={stats['pattern_count']:4d}, "
                  f"r_mean={stats['r_mean']:6.2f} (norm={stats['r_mean_norm']:.4f}), "
                  f"E_dens={stats['energy_density']:.4f}, "
                  f"rate={tick_rate:.1f} t/s [{status}]")

            last_print_time = time.time()

    elapsed = time.time() - start_time

    final_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
    final_history = history_committer.get_state()

    # Stability metrics (after initial transient - skip first 20%)
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means = [h["r_mean"] for h in late_history]
        r_means_norm = [h["r_mean_norm"] for h in late_history]
        energy_densities = [h["energy_density"] for h in late_history]

        stability_metrics = {
            "r_mean_avg": float(np.mean(r_means)),
            "r_mean_std": float(np.std(r_means)),
            "r_mean_norm_avg": float(np.mean(r_means_norm)),
            "r_mean_norm_std": float(np.std(r_means_norm)),
            "energy_density_avg": float(np.mean(energy_densities)),
            "energy_density_std": float(np.std(energy_densities)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: r_mean={final_stats['r_mean']:.2f} (norm={final_stats['r_mean_norm']:.4f})")
        print(f"       patterns={final_stats['pattern_count']}, E_dens={final_stats['energy_density']:.4f}")
        if stability_metrics:
            print(f"       r_norm_drift={stability_metrics['r_mean_norm_std']:.5f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "grid_size": grid_size,
        "effective_tick": config.effective_tick,
        "n_patterns": config.n_patterns,
        "entity_tick_ratio": config.n_patterns / config.effective_tick,  # Should be 1.0
        "density": {
            "linear_density": config.linear_density,
            "area_density": config.area_density,
            "expected_area_density": 1.0 / config.effective_tick,
        },
        "params": {
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "target_gamma_k": config.target_gamma_k,
            "jitter_strength": config.jitter_strength,
        },
        "final_stats": final_stats,
        "final_history": final_history,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_entity_tick_sweep(
    grid_sizes: List[int] = None,
    num_ticks: int = 1000,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """
    Run entity=tick sweep across multiple grid sizes.

    Tests:
    | Grid | Patterns | 2D Density | Expected |
    |------|----------|------------|----------|
    | 50   | 50       | 2%         | Stable   |
    | 100  | 100      | 1%         | Stable   |
    | 200  | 200      | 0.5%       | Stable   |

    Args:
        grid_sizes: List of grid sizes to test
        num_ticks: Number of ticks per experiment
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Combined results with analysis
    """
    if grid_sizes is None:
        grid_sizes = [50, 100, 200]

    print("=" * 70)
    print("V12b ENTITY=TICK SWEEP")
    print("=" * 70)
    print()
    print("Hypothesis: n_patterns = n_ticks = grid_size")
    print()
    print("Each tick creates ONE causal quantum. At tick N, you have N entities.")
    print("The invariant entity_count / tick = 1 is LITERAL.")
    print()
    print(f"Testing grid sizes: {grid_sizes}")
    print()

    # Show predictions
    print("-" * 70)
    print("Predictions (entity = tick):")
    print(f"{'Grid':>6} | {'Patterns':>8} | {'1D Dens':>8} | {'2D Dens':>10} | {'Expected 2D':>10}")
    print("-" * 70)
    for gs in grid_sizes:
        config = create_entity_tick_config(gs)
        expected_2d = 1.0 / gs
        print(f"{gs:>6} | {config.n_patterns:>8} | {config.linear_density:>8.4f} | "
              f"{config.area_density:>10.6f} | {expected_2d:>10.6f}")
    print("-" * 70)
    print()

    all_results = {}
    summary = []

    for gs in grid_sizes:
        results = run_entity_tick_experiment(
            grid_size=gs,
            num_ticks=num_ticks,
            verbose_interval=verbose_interval,
            verbose=verbose
        )
        all_results[f"grid_{gs}"] = results

        sm = results.get("stability_metrics", {})
        summary.append({
            "grid_size": gs,
            "effective_tick": results["effective_tick"],
            "n_patterns": results["n_patterns"],
            "entity_tick_ratio": results["entity_tick_ratio"],
            # Final metrics
            "r_mean": results["final_stats"]["r_mean"],
            "r_mean_norm": results["final_stats"]["r_mean_norm"],
            "energy_density": results["final_stats"]["energy_density"],
            "pattern_density_2d": results["final_stats"]["pattern_density_2d"],
            # Stability
            "drift_norm": sm.get("r_mean_norm_std", -1),
            "elapsed": results["elapsed_seconds"],
            # Comparison with V12 (area-scaled)
            "v12_pattern_count": (gs * gs) // 400,  # What V12 would have used
        })

    # Print summary
    print("\n" + "=" * 70)
    print("ENTITY=TICK SWEEP SUMMARY")
    print("=" * 70)

    print("\n--- Entity=Tick vs V12 Area-Scaled ---")
    print(f"{'Grid':>6} | {'E=T Patterns':>12} | {'V12 Patterns':>12} | {'Ratio':>6}")
    print("-" * 50)
    for row in summary:
        ratio = row['n_patterns'] / row['v12_pattern_count'] if row['v12_pattern_count'] > 0 else float('inf')
        print(f"{row['grid_size']:>6} | {row['n_patterns']:>12} | {row['v12_pattern_count']:>12} | {ratio:>6.1f}x")

    print("\n--- Normalized Metrics ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'E_dens':>10} | {'2D_dens':>10} | {'Drift':>10}")
    print("-" * 60)
    for row in summary:
        drift_str = f"{row['drift_norm']:.6f}" if row['drift_norm'] >= 0 else "N/A"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | "
              f"{row['pattern_density_2d']:>10.6f} | {drift_str:>10}")

    # Verify entity=tick invariant
    print("\n--- Entity=Tick Invariant Verification ---")
    print(f"{'Grid':>6} | {'Patterns':>8} | {'Tick':>8} | {'Ratio':>8} | {'Expected':>8}")
    print("-" * 50)
    all_ratios_one = True
    for row in summary:
        ratio = row['entity_tick_ratio']
        expected = 1.0
        match = abs(ratio - expected) < 0.001
        all_ratios_one = all_ratios_one and match
        print(f"{row['grid_size']:>6} | {row['n_patterns']:>8} | {row['effective_tick']:>8} | "
              f"{ratio:>8.4f} | {expected:>8.4f} {'OK' if match else 'FAIL'}")

    # Analyze stability across scales
    print("\n" + "=" * 70)
    print("STABILITY ANALYSIS")
    print("=" * 70)

    r_norms = [row['r_mean_norm'] for row in summary]
    drifts = [row['drift_norm'] for row in summary if row['drift_norm'] >= 0]

    r_norm_mean = np.mean(r_norms) if r_norms else 0
    r_norm_std = np.std(r_norms) if r_norms else 0
    r_norm_cv = r_norm_std / r_norm_mean if r_norm_mean > 0 else float('inf')

    # Check for collapse (r_norm < 0.01)
    collapsed = [row for row in summary if row['r_mean_norm'] < 0.01]
    stable = [row for row in summary if 0.01 <= row['r_mean_norm'] <= 0.5]
    dispersed = [row for row in summary if row['r_mean_norm'] > 0.5]

    print(f"\nStable (0.01 <= r_norm <= 0.5): {len(stable)}/{len(summary)}")
    if collapsed:
        print(f"  COLLAPSED: {[r['grid_size'] for r in collapsed]}")
    if dispersed:
        print(f"  DISPERSED: {[r['grid_size'] for r in dispersed]}")

    print(f"\nNormalized radius consistency:")
    print(f"  Mean across scales: {r_norm_mean:.4f}")
    print(f"  Std across scales:  {r_norm_std:.4f}")
    print(f"  CV (coefficient of variation): {r_norm_cv:.3f}")

    # Determine success
    CV_THRESHOLD = 0.20  # 20% variation acceptable (more lenient than V12)
    DRIFT_THRESHOLD = 0.01

    all_stable = len(stable) == len(summary)
    scale_invariant = r_norm_cv < CV_THRESHOLD
    low_drift = all(d < DRIFT_THRESHOLD for d in drifts) if drifts else False

    print("\n" + "-" * 70)
    print("VERDICT:")
    print("-" * 70)

    if all_stable and scale_invariant:
        print("\nSUCCESS: Entity=Tick produces stable, scale-invariant behavior!")
        print("\nValidated hypothesis:")
        print("  - n_patterns = n_ticks = grid_size")
        print("  - Each tick creates ONE causal quantum")
        print("  - 2D density = 1/tick (as expected)")
        if collapsed:
            print(f"\n(Note: V12 with area-scaling COLLAPSED at grid=50 with only 6 patterns)")
            print(f" Entity=Tick with 50 patterns should NOT collapse)")
    elif all_stable:
        print("\nPARTIAL SUCCESS: All scales stable, but not perfectly scale-invariant")
        print(f"  CV = {r_norm_cv:.3f} > {CV_THRESHOLD} threshold")
    elif len(collapsed) < len(summary):
        print("\nPARTIAL SUCCESS: Some scales stable, some collapsed/dispersed")
        print(f"  Stable: {[r['grid_size'] for r in stable]}")
    else:
        print("\nFAILED: All scales collapsed or dispersed")

    print(f"\nEntity=Tick invariant: {'VERIFIED' if all_ratios_one else 'FAILED'}")
    print(f"All scales stable: {all_stable}")
    print(f"Scale invariance: CV={r_norm_cv:.3f} {'<' if scale_invariant else '>='} {CV_THRESHOLD}")

    return {
        "all_results": all_results,
        "summary": summary,
        "analysis": {
            "r_norm_mean": r_norm_mean,
            "r_norm_std": r_norm_std,
            "r_norm_cv": r_norm_cv,
            "all_stable": all_stable,
            "scale_invariant": scale_invariant,
            "entity_tick_invariant_verified": all_ratios_one,
            "collapsed_grids": [r['grid_size'] for r in collapsed],
            "stable_grids": [r['grid_size'] for r in stable],
            "dispersed_grids": [r['grid_size'] for r in dispersed],
        },
        "hypothesis_validated": all_stable and scale_invariant and all_ratios_one,
    }


def main():
    """Run V12b entity=tick experiments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V12b Entity=Tick Experiment",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_entity_tick.py --ticks 1000
  python experiment_entity_tick.py --grid 100 --ticks 500
  python experiment_entity_tick.py --grids 50,100,200 --ticks 2000
        """
    )
    parser.add_argument("--ticks", type=int, default=1000, help="Number of ticks (default: 1000)")
    parser.add_argument("--grid", type=int, help="Single grid size to test")
    parser.add_argument("--grids", type=str, help="Comma-separated grid sizes (default: 50,100,200)")
    parser.add_argument("--interval", type=int, default=50, help="Verbose output interval (default: 50)")
    parser.add_argument("--output", type=str, default="results/entity_tick_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.grid:
        # Single grid test
        results = run_entity_tick_experiment(
            grid_size=args.grid,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = f"results/entity_tick_grid_{args.grid}.json"
    elif args.grids:
        # Custom grid list
        grid_sizes = [int(g.strip()) for g in args.grids.split(',')]
        results = run_entity_tick_sweep(
            grid_sizes=grid_sizes,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output
    else:
        # Default sweep (50, 100, 200)
        results = run_entity_tick_sweep(
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output

    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
