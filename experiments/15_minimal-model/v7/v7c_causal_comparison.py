"""
v7c: Comparative Causal Analysis (Focused)

Compares 3D vs 4D at matched absolute scales to determine if dimensional
differences are purely scale-dependent or reflect causal structure differences.

Grid configurations:
- 3D: 48³ = 110,592 points (baseline)
- 4D (matched): 18⁴ = 104,976 points (~95% of 3D)
- 4D (original): 16⁴ = 65,536 points (v6-gpu baseline)

Expected runs: 90 (3 configs × 2 gamma × 3 T × 5 alpha_0)
Expected time: ~1 hour
"""

import itertools
import json
import csv
from datetime import datetime
from parallel_experiment_runner_adaptive import ParallelExperimentRunner
from gpu_wave_solver import GPUWaveSolver
import numpy as np

# ============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

# Test configurations: (dimension, grid_size, label)
CONFIGS = [
    (3, (48, 48, 48), "3D_baseline"),       # 110,592 points
    (4, (18, 18, 18, 18), "4D_matched"),   # 104,976 points
    (4, (16, 16, 16, 16), "4D_original"),  # 65,536 points
]

M = 1
ALPHA_1 = 1.0

# Focused parameter set
GAMMA_VALUES = [0.001, 0.005]  # Low and high damping
TIME_HORIZONS = [100.0, 200.0, 500.0]  # Representative time scales
ALPHA_0_VALUES = [0.8, 1.2, 1.6, 2.0, 2.4]  # Representative field strengths
NUM_SOURCES_LIST = [2]  # Known to be independent
GEOMETRIES = ['symmetric']  # Known to be neutral
PHASE_OFFSETS = [0]  # Known to be neutral

NUM_WORKERS = 11
OUTPUT_CSV = "v7c_causal_comparison_results.csv"
OUTPUT_JSON = "v7c_causal_comparison_results.json"

# ============================================================================
# EXPERIMENT FUNCTION
# ============================================================================

def run_single_experiment(num_sources, geometry, phase_offset, T, gamma, alpha_0,
                          dimension, grid_sizes, alpha_1, M, config_label, run_id=None):
    """Run a single wave solver experiment"""
    try:
        solver = GPUWaveSolver(
            dimension=dimension,
            grid_sizes=grid_sizes,
            alpha_1=alpha_1,
            M=M
        )

        # Set up sources
        center = tuple(g // 2 for g in grid_sizes)
        offset_distance = min(grid_sizes) // 4

        if num_sources == 1:
            positions = [center]
        elif num_sources == 2:
            if geometry == 'symmetric':
                positions = [
                    tuple(c - offset_distance if i == 0 else c for i, c in enumerate(center)),
                    tuple(c + offset_distance if i == 0 else c for i, c in enumerate(center))
                ]
            else:  # clustered
                positions = [
                    center,
                    tuple(c + offset_distance if i == 0 else c for i, c in enumerate(center))
                ]
        elif num_sources == 4:
            if geometry == 'symmetric':
                positions = [
                    tuple(c - offset_distance if i < 2 else c for i, c in enumerate(center)),
                    tuple(c + offset_distance if i < 2 else c for i, c in enumerate(center)),
                    tuple(c - offset_distance if 0 < i < 3 else c for i, c in enumerate(center)),
                    tuple(c + offset_distance if 0 < i < 3 else c for i, c in enumerate(center))
                ]
            else:  # clustered
                positions = [
                    center,
                    tuple(c + offset_distance if i == 0 else c for i, c in enumerate(center)),
                    tuple(c + offset_distance if i == 1 else c for i, c in enumerate(center)),
                    tuple(c + offset_distance if i == 0 else c + offset_distance if i == 1 else c
                          for i, c in enumerate(center))
                ]

        for idx, pos in enumerate(positions):
            phase = np.pi * phase_offset if idx % 2 == 1 else 0.0
            solver.add_sinusoidal_source(position=pos, alpha_0=alpha_0, phase=phase)

        # Run simulation
        statistics = solver.run(T=T, gamma=gamma)

        # Compute grid points
        grid_points = np.prod(grid_sizes)

        return {
            'config_label': config_label,
            'num_sources': num_sources,
            'geometry': geometry,
            'phase_offset': phase_offset,
            'T': T,
            'gamma': gamma,
            'alpha_0': alpha_0,
            'dimension': dimension,
            'grid_size': grid_sizes,
            'grid_points': int(grid_points),
            'statistics': statistics
        }

    except Exception as e:
        print(f"Error in experiment: {e}")
        return None

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("v7c: COMPARATIVE CAUSAL ANALYSIS (FOCUSED)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Grid Configurations:")
    for dim, grid, label in CONFIGS:
        points = np.prod(grid)
        print(f"  {label}: {dim}D, grid={grid}, points={points:,}")
    print()
    print("Parameters:")
    print(f"  Gamma values: {GAMMA_VALUES}")
    print(f"  Time horizons: {TIME_HORIZONS}")
    print(f"  Alpha_0 values: {ALPHA_0_VALUES}")
    print(f"  Sources: {NUM_SOURCES_LIST}")
    print(f"  Geometries: {GEOMETRIES}")
    print(f"  Phase offsets: {PHASE_OFFSETS}")
    print(f"  Workers: {NUM_WORKERS}")
    print()

    # Build parameter grid
    parameter_grid = []
    for (dimension, grid_sizes, config_label), num_sources, geometry, phase_offset, T, gamma, alpha_0 in itertools.product(
        CONFIGS, NUM_SOURCES_LIST, GEOMETRIES, PHASE_OFFSETS,
        TIME_HORIZONS, GAMMA_VALUES, ALPHA_0_VALUES
    ):
        params = {
            'num_sources': num_sources,
            'geometry': geometry,
            'phase_offset': phase_offset,
            'T': T,
            'gamma': gamma,
            'alpha_0': alpha_0,
            'dimension': dimension,
            'grid_sizes': grid_sizes,
            'alpha_1': ALPHA_1,
            'M': M,
            'config_label': config_label
        }
        parameter_grid.append(params)

    print(f"Total parameter combinations: {len(parameter_grid)}")
    print(f"Expected time (20s avg per run): {len(parameter_grid) * 20 / 60:.1f} minutes")
    print("=" * 80)
    print()

    # Run experiments
    def progress_callback(completed, total, result, run_id=None):
        if result and 'statistics' in result:
            stats = result['statistics']
            print(f"[{completed}/{total}] {result['config_label']}: "
                  f"gamma={result['gamma']:.4f}, T={result['T']:.0f}, α₀={result['alpha_0']:.1f} → "
                  f"Salience: {stats['max_salience']:.2e}, Commits: {stats['agent_commit_count']}")

    runner = ParallelExperimentRunner(num_workers=NUM_WORKERS)
    results, stopped_early = runner.run_parameter_sweep(
        simulation_func=run_single_experiment,
        parameter_grid=parameter_grid,
        progress_callback=progress_callback
    )

    print()
    print("=" * 80)
    print("EXPERIMENT COMPLETED")
    print("=" * 80)
    print(f"Successful runs: {len(results)}/{len(parameter_grid)}")
    print(f"Stopped early: {stopped_early}")

    # Save results
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)

    with open(OUTPUT_CSV, 'w', newline='') as f:
        if results:
            fieldnames = [
                'run_id', 'config_label', 'dimension', 'grid_points',
                'num_sources', 'geometry', 'phase_offset', 'T', 'gamma', 'alpha_0',
                'final_psi', 'max_salience', 'first_commit_time',
                'agent_commit_count', 'commit_rate'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for idx, result in enumerate(results):
                if result and 'statistics' in result:
                    stats = result['statistics']
                    row = {
                        'run_id': idx,
                        'config_label': result['config_label'],
                        'dimension': result['dimension'],
                        'grid_points': result['grid_points'],
                        'num_sources': result['num_sources'],
                        'geometry': result['geometry'],
                        'phase_offset': result['phase_offset'],
                        'T': result['T'],
                        'gamma': result['gamma'],
                        'alpha_0': result['alpha_0'],
                        'final_psi': stats['final_psi'],
                        'max_salience': stats['max_salience'],
                        'first_commit_time': stats.get('first_commit_time', 0),
                        'agent_commit_count': stats['agent_commit_count'],
                        'commit_rate': stats.get('commit_rate', 0)
                    }
                    writer.writerow(row)

    print(f"Results saved to: {OUTPUT_CSV}, {OUTPUT_JSON}")
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    # Quick comparison analysis
    print("=" * 80)
    print("QUICK COMPARISON")
    print("=" * 80)
    print()

    for config_label in ["3D_baseline", "4D_matched", "4D_original"]:
        config_results = [r for r in results if r and r.get('config_label') == config_label]
        if config_results:
            saliences = [r['statistics']['max_salience'] for r in config_results if 'statistics' in r]
            commits = [r['statistics']['agent_commit_count'] for r in config_results if 'statistics' in r]

            if saliences:
                print(f"{config_label}:")
                print(f"  Mean salience: {np.mean(saliences):.2e} (±{np.std(saliences):.2e})")
                print(f"  Mean commits: {np.mean(commits):.1f} (±{np.std(commits):.1f})")
                print(f"  CV: {np.std(saliences) / np.mean(saliences):.4f}")
                print()

    print("Key Question: Does 4D (matched scale) behave like 3D or like 4D (original)?")
    print("  → If like 3D: Differences are scale-dependent")
    print("  → If like 4D (original): Differences reflect dimensional structure")
    print()
    print("See V7C_CAUSAL_ANALYSIS.md for detailed comparison")
