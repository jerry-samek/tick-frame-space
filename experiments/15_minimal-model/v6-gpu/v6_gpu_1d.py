"""
V6 GPU Experiment: 1D Dimension

Combines GPU acceleration + CPU multiprocessing for maximum speed.
"""

import json
import csv
import os
from datetime import datetime
from parallel_experiment_runner import (
    ParallelExperimentRunner,
    build_parameter_grid,
    run_single_experiment
)

def save_result_to_csv(result, csv_file, write_header=False):
    """Append a single result to CSV file for continuous monitoring."""
    if result is None:
        return

    fieldnames = [
        'dimension', 'num_sources', 'geometry', 'phase_offset',
        'alpha_0', 'gamma', 'M', 'T',
        'has_commits', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'final_psi', 'max_salience'
    ]

    p = result['parameters']
    s = result['statistics']
    row = {
        'dimension': p['dimension'],
        'num_sources': p['num_sources'],
        'geometry': p['geometry'],
        'phase_offset': p['phase_offset'],
        'alpha_0': p['alpha_0'],
        'gamma': p['gamma'],
        'M': p['M'],
        'T': p['T'],
        'has_commits': s['has_commits'],
        'agent_commit_count': s['agent_commit_count'],
        'commit_rate': s['commit_rate'],
        'first_commit_time': s['first_commit_time'] if s['first_commit_time'] else '',
        'final_psi': s['final_psi'],
        'max_salience': s['max_salience']
    }

    mode = 'w' if write_header else 'a'
    with open(csv_file, mode, newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)

if __name__ == '__main__':
    DIMENSION = 1
    GRID_SIZE = (1000,)

    # Full parameter space (same as original V6)
    num_sources_list = [1, 2, 4]
    geometries = ['symmetric', 'clustered']
    phase_offsets = [0, 1]
    time_horizons = [100.0, 200.0, 500.0]
    gamma_values = [0.001, 0.005]
    M = 1
    alpha_1 = 1.0

    alpha_0_values = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]

    print("="*80)
    print(f"V6-GPU: {DIMENSION}D SWEEP (GPU + Multiprocessing)")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Grid: {GRID_SIZE}")

    # Build parameter grid
    parameter_grid = build_parameter_grid(
        num_sources_list=num_sources_list,
        geometries=geometries,
        phase_offsets=phase_offsets,
        time_horizons=time_horizons,
        gamma_values=gamma_values,
        alpha_0_values=alpha_0_values,
        dimension=DIMENSION,
        grid_sizes=GRID_SIZE,
        alpha_1=alpha_1,
        M=M
    )

    total = len(parameter_grid)
    print(f"Total runs: {total}")
    print("="*80)

    # Output files
    json_file = f"v6_gpu_{DIMENSION}d_results.json"
    csv_file = f"v6_gpu_{DIMENSION}d_results.csv"

    # Initialize CSV with header
    save_result_to_csv(None, csv_file, write_header=True)
    with open(csv_file, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'dimension', 'num_sources', 'geometry', 'phase_offset',
            'alpha_0', 'gamma', 'M', 'T',
            'has_commits', 'agent_commit_count', 'commit_rate',
            'first_commit_time', 'final_psi', 'max_salience'
        ])
        writer.writeheader()

    # Callback to save each result continuously
    def on_result(completed, total, result):
        if result:
            save_result_to_csv(result, csv_file)

    # Run in parallel with continuous output
    runner = ParallelExperimentRunner()  # Auto-detect CPU count
    results = runner.run_parameter_sweep(run_single_experiment, parameter_grid, on_result)

    # Save final JSON
    with open(json_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Results: {json_file}, {csv_file}")
    print(f"Successful runs: {len([r for r in results if r is not None])}/{total}")
