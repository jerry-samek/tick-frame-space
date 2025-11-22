"""
V6 Experiment: 1D Dimension
Can run independently in parallel with other dimensions.
"""

import numpy as np
import json
import csv
from datetime import datetime
from dimensional_wave_solver import (
    run_dimensional_simulation,
    create_symmetric_config_nd,
    create_clustered_config_nd
)

DIMENSION = 1
GRID_SIZE = (1000,)

# Parameters from test plan
num_sources_list = [1, 2, 4]
geometries = ['symmetric', 'clustered']
phase_offsets = [0, 1]  # 0=in-phase, 1=anti-phase
time_horizons = [100.0, 200.0, 500.0]
gamma_values = [0.001, 0.005]
M = 1
alpha_1 = 0.0

# Alpha_0 sweep around expected threshold region
alpha_0_values = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]

print("="*80)
print(f"V6: {DIMENSION}D SWEEP")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Grid: {GRID_SIZE}")

total = len(num_sources_list) * len(geometries) * len(phase_offsets) * \
        len(time_horizons) * len(gamma_values) * len(alpha_0_values)
print(f"Total runs: {total}")
print("="*80)

results = []
run_count = 0

for num_sources in num_sources_list:
    print(f"\nM_s = {num_sources}")

    for geometry in geometries:
        for phase_offset in phase_offsets:
            phase_label = "in-phase" if phase_offset == 0 else "anti-phase"

            for T in time_horizons:
                for gamma in gamma_values:
                    print(f"  {geometry}, {phase_label}, T={T:.0f}s, gamma={gamma:.4f}")

                    threshold_found = False

                    for alpha_0 in alpha_0_values:
                        run_count += 1

                        # Create config
                        if geometry == 'symmetric':
                            config = create_symmetric_config_nd(num_sources, DIMENSION, 1.0, alpha_0)
                        else:
                            config = create_clustered_config_nd(num_sources, DIMENSION, 1.0, alpha_0)

                        # Apply phase
                        if phase_offset == 1 and num_sources > 1:
                            config.phases = [i % 2 for i in range(num_sources)]

                        # Run
                        result = run_dimensional_simulation(
                            config, DIMENSION, GRID_SIZE, alpha_0, alpha_1, gamma, M, T
                        )

                        if result is None:
                            continue

                        result['parameters']['geometry'] = geometry
                        result['parameters']['phase_offset'] = phase_offset
                        results.append(result)

                        stats = result['statistics']
                        has_commits = stats['has_commits']

                        if has_commits and not threshold_found:
                            threshold_found = True
                            print(f"    alpha_0={alpha_0:.2f}: THRESHOLD ({stats['agent_commit_count']} commits)")

                        if run_count % 50 == 0:
                            print(f"    Progress: {run_count}/{total}")

# Save
json_file = f"v6_{DIMENSION}d_results.json"
csv_file = f"v6_{DIMENSION}d_results.csv"

with open(json_file, 'w') as f:
    json.dump(results, f, indent=2)

with open(csv_file, 'w', newline='') as f:
    writer = csv.DictWriter(f, fieldnames=[
        'dimension', 'num_sources', 'geometry', 'phase_offset',
        'alpha_0', 'gamma', 'M', 'T',
        'has_commits', 'agent_commit_count', 'commit_rate',
        'first_commit_time', 'final_psi', 'max_salience'
    ])
    writer.writeheader()
    for r in results:
        p = r['parameters']
        s = r['statistics']
        writer.writerow({
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
        })

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Results: {json_file}, {csv_file}")
