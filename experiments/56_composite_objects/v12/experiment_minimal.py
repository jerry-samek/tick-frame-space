"""
V12d Experiment: Minimal Substrate (Jitter Only)

Hypothesis: Eliminate ALL CA parameters - entities persist, only jitter remains.

V12c used CA rules:
- ca_survival_threshold = 3
- ca_creation_threshold = 5
- creation_sensitivity = 2.0
- field_decay_threshold = 1.5
- field_decay_rate = 0.05

V12d eliminates ALL:
- No survival rules (entities persist forever)
- No creation rules (creation = tick)
- No decay rules (only forgetting via window)
- ONLY jitter remains

The key insight: On the substrate level, there is only ONE constant.
"Death" is actually forgetting - entities become unobservable outside
the observation window, not removed from the substrate.

Success criteria:
- Patterns still emerge/persist with jitter only
- Stability comparable to V12c
- Simpler model (1 parameter vs 6)

Author: V12d Implementation
Date: 2026-01-31
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

# V12 imports
from config_v12 import (
    TickUnifiedConfig, create_tick_unified_config,
    SubstrateConfig, create_substrate_config
)
from evolution_minimal import MinimalEvolution


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config) -> List:
    """Initialize cloud patterns with entity count = tick."""
    patterns = []
    center_x = grid.width // 2
    center_y = grid.height // 2

    rng = np.random.default_rng(config.random_seed)

    init_radius_mean = config.entity_tick_init_radius
    init_radius_std = init_radius_mean * 0.2

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

    r_mean = float(np.mean(radii)) if radii else 0.0
    r_std = float(np.std(radii)) if radii else 0.0

    half_grid = grid_size / 2.0
    r_mean_norm = r_mean / half_grid if half_grid > 0 else 0.0
    r_std_norm = r_std / half_grid if half_grid > 0 else 0.0

    area = grid_size * grid_size
    energy_density = stats["total_energy"] / area if area > 0 else 0.0
    pattern_count = len(patterns)
    pattern_density_2d = pattern_count / area if area > 0 else 0.0

    return {
        "r_mean": r_mean,
        "r_std": r_std,
        "r_min": float(np.min(radii)) if radii else 0.0,
        "r_max": float(np.max(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
        "pattern_count": pattern_count,
        "r_mean_norm": r_mean_norm,
        "r_std_norm": r_std_norm,
        "energy_density": energy_density,
        "pattern_density_2d": pattern_density_2d,
    }


def run_v12c_experiment(
    config: TickUnifiedConfig,
    num_ticks: int = 1000,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V12c experiment (tick-unified with CA rules).

    Args:
        config: TickUnifiedConfig instance
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    grid_size = config.grid_size

    if verbose:
        print(f"\n{'='*70}")
        print(f"V12c (CA RULES) EXPERIMENT: grid={grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    grid = PlanckGrid(config.grid_width, config.grid_height)

    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

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

    # V12c: Full CA rules
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    history = []
    start_time = time.time()

    if verbose:
        init_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
        print(f"[INIT ] patterns={init_stats['pattern_count']:4d}, "
              f"r_mean={init_stats['r_mean']:6.2f} (norm={init_stats['r_mean_norm']:.4f})")

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        if verbose and (tick + 1) % verbose_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_mean_norm": stats["r_mean_norm"],
                "energy_density": stats["energy_density"],
                "pattern_count": stats["pattern_count"],
            })

            status = "RUNNING"
            if stats["r_mean_norm"] < 0.01:
                status = "COLLAPSED?"
            elif stats["r_mean_norm"] > 0.5:
                status = "DISPERSED?"

            print(f"[{tick+1:5d}] r_mean={stats['r_mean']:6.2f} (norm={stats['r_mean_norm']:.4f}), "
                  f"E_dens={stats['energy_density']:.4f}, "
                  f"rate={tick_rate:.1f} t/s [{status}]")

    elapsed = time.time() - start_time
    final_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)

    # Stability metrics
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means_norm = [h["r_mean_norm"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means_norm)),
            "r_mean_norm_std": float(np.std(r_means_norm)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: r_mean={final_stats['r_mean']:.2f} (norm={final_stats['r_mean_norm']:.4f})")
        if stability_metrics:
            print(f"       drift={stability_metrics['r_mean_norm_std']:.5f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": "V12c",
        "grid_size": grid_size,
        "effective_tick": config.effective_tick,
        "n_patterns": config.n_patterns,
        "params": {
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "target_gamma_k": config.target_gamma_k,
            "jitter_strength": config.jitter_strength,
            "ca_survival_threshold": config.ca_survival_threshold,
            "ca_creation_threshold": config.ca_creation_threshold,
            "creation_sensitivity": config.creation_sensitivity,
            "field_decay_threshold": config.field_decay_threshold,
            "field_decay_rate": config.field_decay_rate,
        },
        "final_stats": final_stats,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_v12d_experiment(
    config: SubstrateConfig,
    num_ticks: int = 1000,
    verbose_interval: int = 50,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run V12d experiment (minimal substrate, jitter only).

    Args:
        config: SubstrateConfig instance
        num_ticks: Number of simulation ticks
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Results dictionary
    """
    grid_size = config.grid_size

    if verbose:
        print(f"\n{'='*70}")
        print(f"V12d (JITTER ONLY) EXPERIMENT: grid={grid_size}")
        print(f"{'='*70}")
        print(config.describe())
        print(f"\nRunning {num_ticks} ticks...")
        print("-" * 70)

    grid = PlanckGrid(config.grid_width, config.grid_height)

    gamma_system = GammaWellSystemV10(grid, base_gamma=1.0)
    center_x = grid.width // 2
    center_y = grid.height // 2
    gamma_system.add_well(center_x, center_y, k=config.target_gamma_k, well_id="target")

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

    # V12d: Minimal evolution - jitter only, no CA rules
    evolution = MinimalEvolution(grid, jitter)

    history = []
    start_time = time.time()

    if verbose:
        init_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
        print(f"[INIT ] patterns={init_stats['pattern_count']:4d}, "
              f"r_mean={init_stats['r_mean']:6.2f} (norm={init_stats['r_mean_norm']:.4f})")

    for tick in range(num_ticks):
        evolution.evolve_one_tick()
        history_committer.record_tick(cloud_patterns)

        if history_committer.should_commit():
            history_committer.commit()
            gamma_system.compute_gamma_field(history_committer)

        if verbose and (tick + 1) % verbose_interval == 0:
            stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)
            elapsed = time.time() - start_time
            tick_rate = (tick + 1) / elapsed if elapsed > 0 else 0

            history.append({
                "tick": tick + 1,
                "r_mean": stats["r_mean"],
                "r_std": stats["r_std"],
                "r_mean_norm": stats["r_mean_norm"],
                "energy_density": stats["energy_density"],
                "pattern_count": stats["pattern_count"],
            })

            status = "RUNNING"
            if stats["r_mean_norm"] < 0.01:
                status = "COLLAPSED?"
            elif stats["r_mean_norm"] > 0.5:
                status = "DISPERSED?"

            print(f"[{tick+1:5d}] r_mean={stats['r_mean']:6.2f} (norm={stats['r_mean_norm']:.4f}), "
                  f"E_dens={stats['energy_density']:.4f}, "
                  f"rate={tick_rate:.1f} t/s [{status}]")

    elapsed = time.time() - start_time
    final_stats = compute_cloud_stats(grid, cloud_patterns, center, grid_size)

    # Stability metrics
    late_start = max(100, num_ticks // 5)
    late_history = [h for h in history if h["tick"] >= late_start]

    stability_metrics = {}
    if late_history:
        r_means_norm = [h["r_mean_norm"] for h in late_history]
        stability_metrics = {
            "r_mean_norm_avg": float(np.mean(r_means_norm)),
            "r_mean_norm_std": float(np.std(r_means_norm)),
        }

    if verbose:
        print("-" * 70)
        print(f"FINAL: r_mean={final_stats['r_mean']:.2f} (norm={final_stats['r_mean_norm']:.4f})")
        if stability_metrics:
            print(f"       drift={stability_metrics['r_mean_norm_std']:.5f}")
        print(f"       Time: {elapsed:.1f}s ({num_ticks/elapsed:.1f} ticks/sec)")

    return {
        "config_name": "V12d",
        "grid_size": grid_size,
        "effective_tick": config.effective_tick,
        "n_patterns": config.n_patterns,
        "params": {
            "gamma_window_size": config.gamma_window_size,
            "gamma_imprint_k": config.gamma_imprint_k,
            "target_gamma_k": config.target_gamma_k,
            "jitter_strength": config.jitter_strength,
            "ca_survival_threshold": config.ca_survival_threshold,
            "ca_creation_threshold": config.ca_creation_threshold,
            "creation_sensitivity": config.creation_sensitivity,
            "field_decay_threshold": config.field_decay_threshold,
            "field_decay_rate": config.field_decay_rate,
        },
        "final_stats": final_stats,
        "stability_metrics": stability_metrics,
        "history": history,
        "elapsed_seconds": elapsed,
        "num_ticks": num_ticks,
    }


def run_comparison_experiment(
    grid_size: int,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Compare V12c (CA rules) vs V12d (jitter only) at a single scale.

    Args:
        grid_size: Grid dimension to test
        num_ticks: Number of ticks per experiment
        verbose_interval: Print status every N ticks
        verbose: Enable verbose output

    Returns:
        Comparison results
    """
    print("=" * 70)
    print(f"V12c vs V12d COMPARISON at grid={grid_size}")
    print("=" * 70)
    print()

    # Show parameter differences
    v12c_config = create_tick_unified_config(grid_size)
    v12d_config = create_substrate_config(grid_size)

    print("Parameter comparison:")
    print(f"{'Parameter':>25} | {'V12c':>12} | {'V12d':>12}")
    print("-" * 55)
    print(f"{'jitter_strength':>25} | {v12c_config.jitter_strength:>12.4f} | {v12d_config.jitter_strength:>12.4f}")
    print(f"{'ca_survival_threshold':>25} | {v12c_config.ca_survival_threshold:>12} | {'None':>12}")
    print(f"{'ca_creation_threshold':>25} | {v12c_config.ca_creation_threshold:>12} | {'None':>12}")
    print(f"{'creation_sensitivity':>25} | {v12c_config.creation_sensitivity:>12.2f} | {v12d_config.creation_sensitivity:>12.2f}")
    print(f"{'field_decay_threshold':>25} | {v12c_config.field_decay_threshold:>12.2f} | {v12d_config.field_decay_threshold:>12.2f}")
    print(f"{'field_decay_rate':>25} | {v12c_config.field_decay_rate:>12.3f} | {v12d_config.field_decay_rate:>12.3f}")
    print()
    print("V12c: 6 parameters (jitter + 5 CA rules)")
    print("V12d: 1 parameter (jitter only)")
    print()

    # Run both experiments
    v12c_results = run_v12c_experiment(
        v12c_config,
        num_ticks=num_ticks,
        verbose_interval=verbose_interval,
        verbose=verbose
    )

    v12d_results = run_v12d_experiment(
        v12d_config,
        num_ticks=num_ticks,
        verbose_interval=verbose_interval,
        verbose=verbose
    )

    # Compare results
    print("\n" + "=" * 70)
    print("COMPARISON SUMMARY")
    print("=" * 70)

    print(f"\n{'Metric':>20} | {'V12c':>12} | {'V12d':>12} | {'Diff':>10}")
    print("-" * 60)

    v12c_r = v12c_results["final_stats"]["r_mean_norm"]
    v12d_r = v12d_results["final_stats"]["r_mean_norm"]
    diff_r = v12d_r - v12c_r
    print(f"{'r_mean_norm':>20} | {v12c_r:>12.4f} | {v12d_r:>12.4f} | {diff_r:>+10.4f}")

    v12c_drift = v12c_results.get("stability_metrics", {}).get("r_mean_norm_std", -1)
    v12d_drift = v12d_results.get("stability_metrics", {}).get("r_mean_norm_std", -1)
    if v12c_drift >= 0 and v12d_drift >= 0:
        diff_drift = v12d_drift - v12c_drift
        print(f"{'drift':>20} | {v12c_drift:>12.5f} | {v12d_drift:>12.5f} | {diff_drift:>+10.5f}")

    v12c_e = v12c_results["final_stats"]["energy_density"]
    v12d_e = v12d_results["final_stats"]["energy_density"]
    diff_e = v12d_e - v12c_e
    print(f"{'energy_density':>20} | {v12c_e:>12.4f} | {v12d_e:>12.4f} | {diff_e:>+10.4f}")

    # Determine status
    v12c_stable = 0.01 <= v12c_r <= 0.5
    v12d_stable = 0.01 <= v12d_r <= 0.5

    print("\n" + "-" * 60)
    print(f"V12c status: {'STABLE' if v12c_stable else 'UNSTABLE'}")
    print(f"V12d status: {'STABLE' if v12d_stable else 'UNSTABLE'}")

    if v12c_stable and v12d_stable:
        print("\nBOTH STABLE - V12d (jitter only) works!")
        print("CA rules were NOT fundamental to pattern persistence.")
        if abs(diff_r) < 0.05:
            print("Similar behavior - CA rules had minimal effect.")
        elif diff_r > 0:
            print("V12d shows more expansion (no CA suppression).")
        else:
            print("V12d shows more contraction (unexpected).")
    elif v12d_stable and not v12c_stable:
        print("\nV12d BETTER: stable while V12c unstable!")
        print("CA rules were actually destabilizing.")
    elif v12c_stable and not v12d_stable:
        print("\nV12d WORSE: unstable while V12c stable.")
        print("CA rules provide essential structure.")
        print("Patterns NEED the CA rules - jitter alone is insufficient.")
    else:
        print("\nBOTH UNSTABLE at this scale.")

    return {
        "grid_size": grid_size,
        "v12c": v12c_results,
        "v12d": v12d_results,
        "comparison": {
            "r_diff": diff_r,
            "v12c_stable": v12c_stable,
            "v12d_stable": v12d_stable,
        }
    }


def run_minimal_sweep(
    grid_sizes: List[int] = None,
    num_ticks: int = 1000,
    verbose_interval: int = 100,
    verbose: bool = True
) -> Dict[str, Any]:
    """Run minimal substrate sweep across multiple grid sizes.

    Compares V12c (CA rules) vs V12d (jitter only).

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
    print("V12d MINIMAL SUBSTRATE SWEEP")
    print("=" * 70)
    print()
    print("Hypothesis: CA parameters are not fundamental - only jitter matters.")
    print()
    print("V12c: jitter + 5 CA parameters")
    print("V12d: jitter ONLY")
    print()
    print(f"Testing grid sizes: {grid_sizes}")
    print()

    all_results = {}
    summary_v12c = []
    summary_v12d = []

    for gs in grid_sizes:
        comparison = run_comparison_experiment(
            grid_size=gs,
            num_ticks=num_ticks,
            verbose_interval=verbose_interval,
            verbose=verbose
        )
        all_results[f"grid_{gs}"] = comparison

        # Extract summaries
        v12c = comparison["v12c"]
        v12d = comparison["v12d"]

        summary_v12c.append({
            "grid_size": gs,
            "r_mean_norm": v12c["final_stats"]["r_mean_norm"],
            "energy_density": v12c["final_stats"]["energy_density"],
            "drift": v12c.get("stability_metrics", {}).get("r_mean_norm_std", -1),
            "stable": comparison["comparison"]["v12c_stable"],
        })

        summary_v12d.append({
            "grid_size": gs,
            "r_mean_norm": v12d["final_stats"]["r_mean_norm"],
            "energy_density": v12d["final_stats"]["energy_density"],
            "drift": v12d.get("stability_metrics", {}).get("r_mean_norm_std", -1),
            "stable": comparison["comparison"]["v12d_stable"],
        })

    # Final comparison
    print("\n" + "=" * 70)
    print("FINAL COMPARISON: V12c (CA rules) vs V12d (jitter only)")
    print("=" * 70)

    print("\n--- V12c (6 parameters: jitter + 5 CA) ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'E_dens':>10} | {'Drift':>10} | {'Status':>10}")
    print("-" * 55)
    for row in summary_v12c:
        drift_str = f"{row['drift']:.6f}" if row['drift'] >= 0 else "N/A"
        status = "STABLE" if row['stable'] else "UNSTABLE"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | {drift_str:>10} | {status:>10}")

    print("\n--- V12d (1 parameter: jitter only) ---")
    print(f"{'Grid':>6} | {'r_norm':>8} | {'E_dens':>10} | {'Drift':>10} | {'Status':>10}")
    print("-" * 55)
    for row in summary_v12d:
        drift_str = f"{row['drift']:.6f}" if row['drift'] >= 0 else "N/A"
        status = "STABLE" if row['stable'] else "UNSTABLE"
        print(f"{row['grid_size']:>6} | {row['r_mean_norm']:>8.4f} | "
              f"{row['energy_density']:>10.4f} | {drift_str:>10} | {status:>10}")

    # Analysis
    v12c_stable_count = sum(1 for row in summary_v12c if row['stable'])
    v12d_stable_count = sum(1 for row in summary_v12d if row['stable'])

    print("\n" + "-" * 70)
    print("VERDICT:")
    print("-" * 70)

    print(f"\nV12c stable scales: {v12c_stable_count}/{len(grid_sizes)}")
    print(f"V12d stable scales: {v12d_stable_count}/{len(grid_sizes)}")

    if v12d_stable_count == len(grid_sizes):
        if v12c_stable_count == len(grid_sizes):
            print("\nSUCCESS: V12d (jitter only) is as stable as V12c (CA rules)")
            print("CA rules are NOT fundamental - eliminated 5 parameters!")
            print("The ONE CONSTANT hypothesis validated.")
        else:
            print("\nBONUS: V12d MORE stable than V12c!")
            print("CA rules were actually harmful.")
    elif v12d_stable_count > v12c_stable_count:
        print("\nPARTIAL SUCCESS: V12d more stable than V12c at some scales")
    elif v12d_stable_count == v12c_stable_count:
        print("\nNEUTRAL: Similar stability - V12d preferred for simplicity")
    else:
        print("\nFAILED: V12d less stable than V12c")
        print("CA rules provide essential structure.")
        print("The hypothesis that jitter alone suffices is REJECTED.")
        print()
        print("RISK MITIGATION:")
        print("- Jitter may need to be weaker")
        print("- Or gamma well needs to be stronger")
        print("- Or we need a different confinement mechanism")

    return {
        "all_results": all_results,
        "summary_v12c": summary_v12c,
        "summary_v12d": summary_v12d,
        "analysis": {
            "v12c_stable_count": v12c_stable_count,
            "v12d_stable_count": v12d_stable_count,
            "total_scales": len(grid_sizes),
            "v12d_as_good_or_better": v12d_stable_count >= v12c_stable_count,
        },
    }


def main():
    """Run V12d minimal substrate experiments."""
    import argparse

    parser = argparse.ArgumentParser(
        description="V12d Minimal Substrate Experiment (Jitter Only)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python experiment_minimal.py --ticks 1000
  python experiment_minimal.py --grid 100 --ticks 500
  python experiment_minimal.py --grids 50,100,200 --ticks 2000
        """
    )
    parser.add_argument("--ticks", type=int, default=1000, help="Number of ticks (default: 1000)")
    parser.add_argument("--grid", type=int, help="Single grid size to compare")
    parser.add_argument("--grids", type=str, help="Comma-separated grid sizes (default: 50,100,200)")
    parser.add_argument("--interval", type=int, default=100, help="Verbose output interval (default: 100)")
    parser.add_argument("--output", type=str, default="results/minimal_sweep.json")
    parser.add_argument("--quiet", action="store_true", help="Less verbose output")
    args = parser.parse_args()

    os.makedirs("results", exist_ok=True)

    if args.grid:
        # Single grid comparison
        results = run_comparison_experiment(
            grid_size=args.grid,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = f"results/minimal_grid_{args.grid}.json"
    elif args.grids:
        # Custom grid list
        grid_sizes = [int(g.strip()) for g in args.grids.split(',')]
        results = run_minimal_sweep(
            grid_sizes=grid_sizes,
            num_ticks=args.ticks,
            verbose_interval=args.interval,
            verbose=not args.quiet
        )
        output_file = args.output
    else:
        # Default sweep (50, 100, 200)
        results = run_minimal_sweep(
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
