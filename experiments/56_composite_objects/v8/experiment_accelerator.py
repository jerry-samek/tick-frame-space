"""
V8 Experiment: Particle Accelerator

Fire projectiles at the stabilized pattern cloud and observe:
- Scattering behavior
- Energy transfer
- Cloud response (excitation, ionization, damage)
"""

import sys
import os
import time
import json
import math
from pathlib import Path

# Add v6 and v7 to path
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary
from sample_cell import SampleCell, PatternInstance
from planck_jitter import PlanckJitter
from evolution_rules import TickFrameEvolution
from pattern_tracking import track_pattern_positions, save_initial_pattern_positions

from config_v8 import AcceleratorConfig
from projectile import Projectile
from gamma_wells import GammaWellSystem
from gamma_history import GammaHistoryCommitter


def create_gamma_well_system(grid: PlanckGrid, config) -> GammaWellSystem:
    """
    Create gamma well system with target well at center.

    Args:
        grid: The Planck grid
        config: AcceleratorConfig with gamma_field_k or target_gamma_k

    Returns:
        Configured GammaWellSystem with target well
    """
    system = GammaWellSystem(grid, base_gamma=1.0)

    # Add target well at grid center
    center_x = grid.width // 2
    center_y = grid.height // 2

    # Use target_gamma_k if available, otherwise fall back to gamma_field_k
    target_k = getattr(config, 'target_gamma_k', config.gamma_field_k)
    system.add_well(center_x, center_y, k=target_k, well_id="target")

    return system


def initialize_gamma_field(grid: PlanckGrid, k: float):
    """Initialize radial gamma field (legacy, single well at center)."""
    center_x = grid.width // 2
    center_y = grid.height // 2

    for y in range(grid.height):
        for x in range(grid.width):
            dx = x - center_x
            dy = y - center_y
            r_squared = dx * dx + dy * dy

            if r_squared < 1:
                gamma_val = 2.0
            else:
                gamma_val = 1.0 + k / r_squared

            gamma_clamped = min(2.0, max(1.0, gamma_val))
            grid.set_gamma(x, y, gamma_clamped)


def initialize_cloud(grid: PlanckGrid, library: PatternLibrary, config):
    """Initialize target cloud patterns."""
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


def compute_cloud_statistics(grid: PlanckGrid, patterns: list, center: tuple) -> dict:
    """Compute cloud statistics."""
    # Update pattern positions from field
    track_pattern_positions(grid, patterns, search_radius=15)

    # Compute radii and energies
    radii = []
    for p in patterns:
        dx = p.sample.center_x - center[0]
        dy = p.sample.center_y - center[1]
        r = math.sqrt(dx * dx + dy * dy)
        radii.append(r)

    # Total field energy
    stats = grid.get_field_statistics()

    return {
        "r_mean": float(np.mean(radii)) if radii else 0.0,
        "r_std": float(np.std(radii)) if radii else 0.0,
        "total_energy": stats["total_energy"],
        "coverage": stats["nonzero_fraction"],
    }


def run_accelerator_experiment(config, verbose: bool = True) -> dict:
    """
    Run a single accelerator experiment.

    Args:
        config: AcceleratorConfig with all parameters
        verbose: Print progress

    Returns:
        Results dictionary
    """
    # Get gamma well parameters
    target_gamma_k = getattr(config, 'target_gamma_k', config.gamma_field_k)
    projectile_gamma_k = getattr(config, 'projectile_gamma_k', 0.0)

    # Get late gamma commit parameters
    gamma_late_commit_enabled = getattr(config, 'gamma_late_commit_enabled', False)
    gamma_window_size = getattr(config, 'gamma_window_size', 50)
    gamma_imprint_k = getattr(config, 'gamma_imprint_k', 10.0)
    gamma_history_decay = getattr(config, 'gamma_history_decay', 0.0)

    if verbose:
        print("=" * 70)
        print("V8 Particle Accelerator Experiment")
        print("=" * 70)
        print()
        print(f"Grid: {config.grid_width}x{config.grid_height}")
        print(f"Cloud patterns: {config.n_patterns}")
        print(f"Jitter: {config.jitter_strength}")
        print()
        print("Projectile:")
        print(f"  Speed: {config.projectile_speed} cells/tick")
        print(f"  Impact parameter: {config.impact_parameter}")
        print(f"  Start radius: {config.projectile_start_radius}")
        print(f"  Fire delay: {config.projectile_delay} ticks")
        print(f"  Gamma well k: {projectile_gamma_k}")
        print()
        print("Gamma Wells:")
        print(f"  Target k: {target_gamma_k}")
        print(f"  Projectile k: {projectile_gamma_k}")
        print()
        if gamma_late_commit_enabled:
            print("Late Gamma Commit (Existence Log):")
            print(f"  Window size: {gamma_window_size} ticks")
            print(f"  Imprint strength k: {gamma_imprint_k}")
            print(f"  History decay: {gamma_history_decay}")
            print()

    # Initialize grid
    grid = PlanckGrid(config.grid_width, config.grid_height)

    # Create gamma well system with target well
    gamma_system = create_gamma_well_system(grid, config)

    # Create history committer if late commit is enabled
    history_committer = None
    if gamma_late_commit_enabled:
        history_committer = GammaHistoryCommitter(
            grid,
            window_size=gamma_window_size,
            imprint_strength=gamma_imprint_k,
            decay=gamma_history_decay
        )

    # Compute initial gamma field
    gamma_system.compute_gamma_field(history_committer)

    library = PatternLibrary(pattern_size=config.pattern_size)
    center = (grid.width // 2, grid.height // 2)

    # Initialize cloud
    cloud_patterns = initialize_cloud(grid, library, config)

    # Create evolution
    jitter = PlanckJitter.create_symmetric(config.jitter_strength, seed=config.random_seed)
    evolution = TickFrameEvolution(
        grid, jitter,
        gamma_modulation_strength=config.gamma_modulation_strength,
        creation_sensitivity=config.creation_sensitivity,
        field_decay_threshold=config.field_decay_threshold,
        field_decay_rate=config.field_decay_rate
    )

    # History
    history = []
    projectile = None
    projectile_history = []

    # Phases
    phase = "stabilize"  # stabilize -> projectile_flight -> post_impact

    # Stats before/after
    stats_before = None
    stats_after = None
    impact_tick = None

    start_time = time.time()

    if verbose:
        print(f"Running {config.num_ticks} ticks...")
        print()

    for tick in range(config.num_ticks):
        # Phase transitions
        if tick == config.projectile_delay:
            # Fire projectile
            phase = "projectile_flight"
            projectile = Projectile.create_toward_center(
                grid=grid,
                library=library,
                pattern_name=config.projectile_pattern,
                start_radius=config.projectile_start_radius,
                approach_angle=config.projectile_angle,
                speed=config.projectile_speed,
                impact_parameter=config.impact_parameter,
                tick_created=tick,
                gamma_k=projectile_gamma_k
            )
            projectile.write_to_grid()

            # Add projectile's gamma well if it has one
            if projectile_gamma_k > 0:
                proj_wx, proj_wy = projectile.get_gamma_well_position()
                gamma_system.add_well(proj_wx, proj_wy, k=projectile_gamma_k, well_id="projectile")
                gamma_system.compute_gamma_field(history_committer)

            # Record pre-impact stats
            stats_before = compute_cloud_statistics(grid, cloud_patterns, center)

            if verbose:
                print(f"[{tick:4d}] PROJECTILE FIRED at r={config.projectile_start_radius}"
                      + (f" with gamma well k={projectile_gamma_k}" if projectile_gamma_k > 0 else ""))

        # Update projectile if active
        if projectile is not None and projectile.state.active:
            # Clear, evolve, then rewrite projectile
            projectile.clear_from_grid()

        # Evolve the field (including cloud)
        evolution.evolve_one_tick()

        # Record positions for history (if late commit enabled)
        if history_committer is not None:
            history_committer.record_tick(cloud_patterns)

            # Also record projectile if active
            if projectile is not None and projectile.state.active:
                history_committer.record_projectile_tick(projectile)

            # Check for window boundary - commit to gamma field
            if history_committer.should_commit():
                commit_stats = history_committer.commit()
                # Recompute gamma field with updated history layer
                gamma_system.compute_gamma_field(history_committer)
                if verbose:
                    print(f"[{tick:4d}] GAMMA COMMIT #{commit_stats['commit_number']} - "
                          f"history_max={commit_stats['history_max']:.3f}")

        # Update projectile position
        if projectile is not None and projectile.state.active:
            still_active = projectile.update(tick)

            # Update projectile's gamma well position
            if projectile_gamma_k > 0 and still_active:
                proj_wx, proj_wy = projectile.get_gamma_well_position()
                gamma_system.update_well_position("projectile", proj_wx, proj_wy)
                gamma_system.compute_gamma_field(history_committer)

            # Record projectile state
            projectile_history.append({
                "tick": tick,
                "x": projectile.state.x,
                "y": projectile.state.y,
                "r": projectile.state.r,
                "active": projectile.state.active,
            })

            # Check for impact
            if projectile.state.tick_impact == tick:
                impact_tick = tick
                phase = "post_impact"
                if verbose:
                    print(f"[{tick:4d}] IMPACT at r={projectile.state.r:.1f}")

            if not still_active:
                # Remove projectile's gamma well when it leaves the grid
                if projectile_gamma_k > 0:
                    gamma_system.remove_well("projectile")
                    gamma_system.compute_gamma_field(history_committer)
                if verbose:
                    print(f"[{tick:4d}] Projectile left grid")

        # Progress
        if verbose and (tick + 1) % config.progress_interval == 0:
            stats = compute_cloud_statistics(grid, cloud_patterns, center)
            proj_r = projectile.state.r if projectile else "-"
            proj_status = "active" if (projectile and projectile.state.active) else "inactive"

            print(f"[{tick+1:4d}/{config.num_ticks:4d}] "
                  f"cloud_r={stats['r_mean']:.1f}, "
                  f"energy={stats['total_energy']}, "
                  f"proj_r={proj_r}, "
                  f"phase={phase}")

            history.append({
                "tick": tick + 1,
                "phase": phase,
                "cloud_stats": stats,
            })

    elapsed = time.time() - start_time

    # Final stats
    stats_after = compute_cloud_statistics(grid, cloud_patterns, center)

    if verbose:
        print()
        print("=" * 70)
        print("RESULTS")
        print("=" * 70)
        print()

        if stats_before:
            print("Before impact:")
            print(f"  Cloud r_mean: {stats_before['r_mean']:.2f}")
            print(f"  Total energy: {stats_before['total_energy']}")
            print()

        print("After experiment:")
        print(f"  Cloud r_mean: {stats_after['r_mean']:.2f}")
        print(f"  Total energy: {stats_after['total_energy']}")
        print()

        if stats_before:
            r_change = stats_after['r_mean'] - stats_before['r_mean']
            e_change = stats_after['total_energy'] - stats_before['total_energy']
            print("Changes:")
            print(f"  Delta r_mean: {r_change:+.2f} cells")
            print(f"  Delta energy: {e_change:+d}")
            print()

        if impact_tick:
            print(f"Impact occurred at tick {impact_tick}")
        else:
            print("No impact detected")

        if history_committer is not None:
            print()
            print("Late Gamma Commit (Existence Log):")
            final_state = history_committer.get_state()
            print(f"  Total commits: {final_state['total_commits']}")
            print(f"  History max gamma: {final_state['history_max']:.4f}")
            print(f"  History mean gamma: {final_state['history_mean']:.6f}")

        print()
        print(f"Performance: {config.num_ticks / elapsed:.1f} ticks/sec")
        print("=" * 70)

    # Compile results
    results = {
        "config": {
            "projectile_speed": config.projectile_speed,
            "impact_parameter": config.impact_parameter,
            "projectile_delay": config.projectile_delay,
            "jitter_strength": config.jitter_strength,
            "n_patterns": config.n_patterns,
            "target_gamma_k": target_gamma_k,
            "projectile_gamma_k": projectile_gamma_k,
            "gamma_late_commit_enabled": gamma_late_commit_enabled,
            "gamma_window_size": gamma_window_size if gamma_late_commit_enabled else None,
            "gamma_imprint_k": gamma_imprint_k if gamma_late_commit_enabled else None,
            "gamma_history_decay": gamma_history_decay if gamma_late_commit_enabled else None,
        },
        "stats_before": stats_before,
        "stats_after": stats_after,
        "impact_tick": impact_tick,
        "projectile_history": projectile_history,
        "history": history,
        "elapsed_seconds": elapsed,
        "gamma_history_final": history_committer.get_state() if history_committer else None,
    }

    return results


def main():
    """Run accelerator experiment with default config."""
    import argparse

    parser = argparse.ArgumentParser(description="V8 Particle Accelerator")
    parser.add_argument("--speed", type=float, default=0.5, help="Projectile speed")
    parser.add_argument("--impact", type=float, default=0.0, help="Impact parameter")
    parser.add_argument("--output", type=str, default="results/accelerator.json")
    args = parser.parse_args()

    config = AcceleratorConfig()
    config.projectile_speed = args.speed
    config.impact_parameter = args.impact

    os.makedirs("results", exist_ok=True)

    results = run_accelerator_experiment(config, verbose=True)

    with open(args.output, "w") as f:
        json.dump(results, f, indent=2, default=lambda x: float(x) if hasattr(x, 'item') else x)

    print()
    print(f"Results saved to {args.output}")


if __name__ == "__main__":
    main()
