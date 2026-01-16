"""
Baseline Validation: Quick test to verify setup matches Experiment #15 v7-final

Tests 3D, 4D, 5D at key parameter points to ensure our infrastructure
produces consistent results with the original dimensional experiments.

Expected runtime: 2-3 minutes
"""

import csv
import json
from datetime import datetime
from parallel_experiment_runner_adaptive import ParallelExperimentRunner
from experiment_wrapper import run_single_experiment_v7 as run_single_experiment
from gpu_wave_solver import create_symmetric_config_nd

# Quick validation configs (5 per dimension = 15 total)
VALIDATION_CONFIGS = [
    # 3D validation points
    {'dimension': 3, 'grid_size': (48, 48, 48), 'alpha_0': 0.8, 'gamma': 0.1, 'num_sources': 1, 'T': 200},
    {'dimension': 3, 'grid_size': (48, 48, 48), 'alpha_0': 1.4, 'gamma': 0.2, 'num_sources': 2, 'T': 200},
    {'dimension': 3, 'grid_size': (48, 48, 48), 'alpha_0': 2.0, 'gamma': 0.3, 'num_sources': 1, 'T': 500},
    {'dimension': 3, 'grid_size': (48, 48, 48), 'alpha_0': 2.4, 'gamma': 0.1, 'num_sources': 2, 'T': 500},
    {'dimension': 3, 'grid_size': (48, 48, 48), 'alpha_0': 1.8, 'gamma': 0.2, 'num_sources': 4, 'T': 200},

    # 4D validation points
    {'dimension': 4, 'grid_size': (16, 16, 16, 16), 'alpha_0': 0.8, 'gamma': 0.1, 'num_sources': 1, 'T': 200},
    {'dimension': 4, 'grid_size': (16, 16, 16, 16), 'alpha_0': 1.4, 'gamma': 0.2, 'num_sources': 2, 'T': 200},
    {'dimension': 4, 'grid_size': (16, 16, 16, 16), 'alpha_0': 2.0, 'gamma': 0.3, 'num_sources': 1, 'T': 500},
    {'dimension': 4, 'grid_size': (16, 16, 16, 16), 'alpha_0': 2.4, 'gamma': 0.1, 'num_sources': 2, 'T': 500},
    {'dimension': 4, 'grid_size': (16, 16, 16, 16), 'alpha_0': 1.8, 'gamma': 0.2, 'num_sources': 4, 'T': 200},

    # 5D validation points
    {'dimension': 5, 'grid_size': (10, 10, 10, 10, 10), 'alpha_0': 0.8, 'gamma': 0.1, 'num_sources': 1, 'T': 200},
    {'dimension': 5, 'grid_size': (10, 10, 10, 10, 10), 'alpha_0': 1.4, 'gamma': 0.2, 'num_sources': 2, 'T': 200},
    {'dimension': 5, 'grid_size': (10, 10, 10, 10, 10), 'alpha_0': 2.0, 'gamma': 0.3, 'num_sources': 1, 'T': 500},
    {'dimension': 5, 'grid_size': (10, 10, 10, 10, 10), 'alpha_0': 2.4, 'gamma': 0.1, 'num_sources': 2, 'T': 500},
    {'dimension': 5, 'grid_size': (10, 10, 10, 10, 10), 'alpha_0': 1.8, 'gamma': 0.2, 'num_sources': 4, 'T': 200},
]

NUM_WORKERS = 11
OUTPUT_CSV = "../results/baseline_validation.csv"
OUTPUT_JSON = "../results/baseline_validation.json"

if __name__ == "__main__":
    print("=" * 80)
    print("BASELINE VALIDATION")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nValidating against Experiment #15 v7-final")
    print(f"Testing {len(VALIDATION_CONFIGS)} configurations across 3D, 4D, 5D")
    print(f"Expected runtime: ~2-3 minutes\n")

    # Build task list
    tasks = []
    for config in VALIDATION_CONFIGS:
        tasks.append({
            'dimension': config['dimension'],
            'grid_sizes': config['grid_size'],
            'alpha_0': config['alpha_0'],
            'alpha_1': 1.0,
            'gamma': config['gamma'],
            'M': 1,
            'T': config['T'],
            'num_sources': config['num_sources'],
            'geometry': 'symmetric',
            'phase_offset': 0
        })

    print(f"Total tasks: {len(tasks)}")
    print(f"Workers: {NUM_WORKERS}\n")

    # Run experiments
    runner = ParallelExperimentRunner(num_workers=NUM_WORKERS)
    results, stopped_early = runner.run_parameter_sweep(
        simulation_func=run_single_experiment,
        parameter_grid=tasks
    )

    # Filter out None results
    valid_results = [r for r in results if r is not None]

    if stopped_early:
        print("\n⚠ WARNING: Experiment stopped early due to errors")

    print(f"\n{'=' * 80}")
    print(f"VALIDATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total configs: {len(tasks)}")
    print(f"Successful: {len(valid_results)}")
    print(f"Failed (CFL): {len(tasks) - len(valid_results)}\n")

    # Summary statistics by dimension
    for dim in [3, 4, 5]:
        dim_results = [r for r in valid_results if r['parameters']['dimension'] == dim]
        if dim_results:
            commit_rates = [r['statistics']['commit_rate'] for r in dim_results]
            avg_rate = sum(commit_rates) / len(commit_rates)
            print(f"{dim}D: {len(dim_results)} configs, avg commit rate: {avg_rate:.4f}")

    # Save results
    print(f"\nSaving to {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        if valid_results:
            writer = csv.DictWriter(f, fieldnames=list(valid_results[0]['parameters'].keys()) +
                                                     list(valid_results[0]['statistics'].keys()))
            writer.writeheader()
            for result in valid_results:
                row = {**result['parameters'], **result['statistics']}
                writer.writerow(row)

    print(f"Saving to {OUTPUT_JSON}")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(valid_results, f, indent=2)

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
