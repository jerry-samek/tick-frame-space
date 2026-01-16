"""
Baseline Validation: Sequential version (avoids Windows multiprocessing issues)

Tests 3D, 4D, 5D at key parameter points to ensure our infrastructure
produces consistent results with the original dimensional experiments.

Expected runtime: 5-10 minutes (sequential)
"""

import csv
import json
from datetime import datetime
from experiment_wrapper import run_single_experiment_v7 as run_single_experiment

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

OUTPUT_CSV = "../results/baseline_validation.csv"
OUTPUT_JSON = "../results/baseline_validation.json"

if __name__ == "__main__":
    print("=" * 80)
    print("BASELINE VALIDATION (Sequential)")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nValidating against Experiment #15 v7-final")
    print(f"Testing {len(VALIDATION_CONFIGS)} configurations across 3D, 4D, 5D")
    print(f"Expected runtime: ~5-10 minutes (sequential)\n")

    results = []
    for i, config in enumerate(VALIDATION_CONFIGS, 1):
        print(f"[{i}/{len(VALIDATION_CONFIGS)}] Running {config['dimension']}D, a0={config['alpha_0']}, gamma={config['gamma']}, Ms={config['num_sources']}, T={config['T']}...", end=' ', flush=True)

        result = run_single_experiment(
            num_sources=config['num_sources'],
            geometry='symmetric',
            phase_offset=0,
            T=config['T'],
            gamma=config['gamma'],
            alpha_0=config['alpha_0'],
            dimension=config['dimension'],
            grid_sizes=config['grid_size'],
            alpha_1=1.0,
            M=1,
            run_id=i-1
        )

        if result is not None:
            results.append(result)
            commits = result['statistics']['agent_commit_count']
            rate = result['statistics']['commit_rate']
            print(f"OK commits={commits}, rate={rate:.4f}")
        else:
            print("FAIL CFL violated")

    print(f"\n{'=' * 80}")
    print(f"VALIDATION COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total configs: {len(VALIDATION_CONFIGS)}")
    print(f"Successful: {len(results)}")
    print(f"Failed (CFL): {len(VALIDATION_CONFIGS) - len(results)}\n")

    # Summary statistics by dimension
    for dim in [3, 4, 5]:
        dim_results = [r for r in results if r['parameters']['dimension'] == dim]
        if dim_results:
            commit_rates = [r['statistics']['commit_rate'] for r in dim_results]
            avg_rate = sum(commit_rates) / len(commit_rates)
            print(f"{dim}D: {len(dim_results)} configs, avg commit rate: {avg_rate:.4f}")

    # Save results
    print(f"\nSaving to {OUTPUT_CSV}")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=list(results[0]['parameters'].keys()) +
                                                     list(results[0]['statistics'].keys()))
            writer.writeheader()
            for result in results:
                row = {**result['parameters'], **result['statistics']}
                writer.writerow(row)

    print(f"Saving to {OUTPUT_JSON}")
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
