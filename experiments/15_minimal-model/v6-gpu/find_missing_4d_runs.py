"""
Identify the 5 missing 4D runs and their parameters.
"""

import pandas as pd
import itertools

# Read existing results
df = pd.read_csv("v6_gpu_4d_results.csv")
print(f"Found {len(df)} successful runs in CSV")

# Build full parameter grid (same as experiment)
num_sources_list = [1, 2, 4]
geometries = ['symmetric', 'clustered']
phase_offsets = [0, 1]
time_horizons = [100.0, 200.0, 500.0]
gamma_values = [0.001, 0.005]
alpha_0_values = [0.6, 0.8, 1.0, 1.2, 1.4, 1.6, 1.8, 2.0, 2.2, 2.4, 2.6]

parameter_grid = []
for num_sources, geometry, phase_offset, T, gamma, alpha_0 in itertools.product(
    num_sources_list, geometries, phase_offsets, time_horizons, gamma_values, alpha_0_values
):
    params = {
        'num_sources': num_sources,
        'geometry': geometry,
        'phase_offset': phase_offset,
        'T': T,
        'gamma': gamma,
        'alpha_0': alpha_0,
    }
    parameter_grid.append(params)

print(f"Total parameter combinations: {len(parameter_grid)}")

# Find missing configurations
missing_runs = []
for run_id, params in enumerate(parameter_grid):
    # Check if this configuration exists in results
    match = df[
        (df['num_sources'] == params['num_sources']) &
        (df['geometry'] == params['geometry']) &
        (df['phase_offset'] == params['phase_offset']) &
        (df['T'] == params['T']) &
        (df['gamma'] == params['gamma']) &
        (df['alpha_0'] == params['alpha_0'])
    ]

    if len(match) == 0:
        params['run_id'] = run_id
        missing_runs.append(params)

print(f"\nFound {len(missing_runs)} missing runs:")
print("="*80)

for i, params in enumerate(missing_runs):
    print(f"\nMissing Run {i+1}:")
    print(f"  Run ID: {params['run_id']}")
    print(f"  num_sources: {params['num_sources']}")
    print(f"  geometry: {params['geometry']}")
    print(f"  phase_offset: {params['phase_offset']}")
    print(f"  T: {params['T']}")
    print(f"  gamma: {params['gamma']}")
    print(f"  alpha_0: {params['alpha_0']}")

# Save to file for rerun
import json
with open('missing_4d_runs.json', 'w') as f:
    json.dump(missing_runs, f, indent=2)

print(f"\n\nSaved to missing_4d_runs.json")
