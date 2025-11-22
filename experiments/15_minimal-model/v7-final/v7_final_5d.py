"""
v7a: Saturation Boundary Detection - 5D (Finest)

Tests extended T range with Finest damping values to map saturation boundary.
Reduced parameter set for quick validation.

Expected runs: 60 (3 gamma × 5 T × 4 alpha_0)
Expected time: ~40 minutes
"""

import itertools
import json
import csv
from datetime import datetime
from parallel_experiment_runner_adaptive import ParallelExperimentRunner
from experiment_wrapper import run_single_experiment_v7 as run_single_experiment
import numpy as np

# ============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

DIMENSION = 4
GRID_SIZE = (10, 10, 10, 10, 10)
M = 1
ALPHA_1 = 1.0

# Finest parameter set for saturation boundary detection
GAMMA_VALUES = [0.004]  # Boundary region
TIME_HORIZONS = [500,1000]  # Extended to find T_sat
ALPHA_0_VALUES = [0.8, 1.8]  # Representative sampling
NUM_SOURCES_LIST = [1,2,4]  # Single value (known to be independent)
GEOMETRIES = ['symmetric']  # Single value (known to be neutral)
PHASE_OFFSETS = [0]  # Single value (known to be neutral)

NUM_WORKERS = 11
OUTPUT_CSV = "v7a_finest_5d_results.csv"
OUTPUT_JSON = "v7a_finest_5d_results.json"

# ============================================================================
# MAIN EXECUTION
# ============================================================================

if __name__ == "__main__":
    print("=" * 80)
    print("v7a: SATURATION BOUNDARY DETECTION - 5D (Finest)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    print("Configuration:")
    print(f"  Dimension: {DIMENSION}D")
    print(f"  Grid size: {GRID_SIZE}")
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
    for num_sources, geometry, phase_offset, T, gamma, alpha_0 in itertools.product(
        NUM_SOURCES_LIST, GEOMETRIES, PHASE_OFFSETS,
        TIME_HORIZONS, GAMMA_VALUES, ALPHA_0_VALUES
    ):
        params = {
            'num_sources': num_sources,
            'geometry': geometry,
            'phase_offset': phase_offset,
            'T': T,
            'gamma': gamma,
            'alpha_0': alpha_0,
            'dimension': DIMENSION,
            'grid_sizes': GRID_SIZE,
            'alpha_1': ALPHA_1,
            'M': M
        }
        parameter_grid.append(params)

    print(f"Total parameter combinations: {len(parameter_grid)}")
    print(f"Expected time (30s avg per run): {len(parameter_grid) * 30 / 60:.1f} minutes")
    print("=" * 80)
    print()

    # Run experiments
    def progress_callback(completed, total, result, run_id=None):
        if result and 'statistics' in result:
            stats = result['statistics']
            print(f"[{completed}/{total}] gamma={result['gamma']:.4f}, T={result['T']:.0f}, "
                  f"Alpha_0={result['alpha_0']:.1f} → "
                  f"Salience: {stats['max_salience']:.2e}, "
                  f"Commits: {stats['agent_commit_count']}")

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
                'run_id', 'num_sources', 'geometry', 'phase_offset', 'T', 'gamma', 'alpha_0',
                'dimension', 'final_psi', 'max_salience', 'first_commit_time',
                'agent_commit_count', 'commit_rate'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for idx, result in enumerate(results):
                if result and 'statistics' in result:
                    stats = result['statistics']
                    row = {
                        'run_id': idx,
                        'num_sources': result['num_sources'],
                        'geometry': result['geometry'],
                        'phase_offset': result['phase_offset'],
                        'T': result['T'],
                        'gamma': result['gamma'],
                        'alpha_0': result['alpha_0'],
                        'dimension': result['dimension'],
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

    # Quick saturation detection
    print("=" * 80)
    print("SATURATION DETECTION")
    print("=" * 80)

    saturation_threshold = 1e7  # 10M is likely saturated based on v6-gpu

    for gamma in GAMMA_VALUES:
        print(f"\nGamma = {gamma}:")
        gamma_results = [r for r in results if r and r.get('gamma') == gamma]

        for T in sorted(set(r['T'] for r in gamma_results)):
            T_results = [r for r in gamma_results if r['T'] == T]
            if T_results:
                saliences = [r['statistics']['max_salience'] for r in T_results if 'statistics' in r]
                if saliences:
                    mean_sal = np.mean(saliences)
                    cv = np.std(saliences) / mean_sal if mean_sal > 0 else 0
                    saturated = mean_sal > saturation_threshold and cv < 0.01

                    status = "SATURATED" if saturated else "OK"
                    print(f"  T={T:5.0f}: mean={mean_sal:.2e}, CV={cv:.4f} [{status}]")

    print()
    print("Note: Saturation defined as mean > 10M AND CV < 0.01")
    print("See V7A_SATURATION_ANALYSIS.md for detailed analysis")
