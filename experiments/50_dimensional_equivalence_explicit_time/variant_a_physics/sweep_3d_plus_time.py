"""
Variant A: 3D + Time Parameter Sweep
Tests whether (3D spatial + 1D time) behaves like 4D spatially.
Expected runtime: ~1-2 hours on CPU
"""

import csv
import json
import itertools
from datetime import datetime
import sys
sys.path.append('..')

from gpu_wave_solver import create_symmetric_config_nd, create_clustered_config_nd, run_gpu_simulation

SPATIAL_DIM = 3
GRID_SIZE = (48, 48, 48)
TIME_WINDOW_SIZE = 10

ALPHA_0_VALUES = [0.8, 1.2, 1.6, 2.0, 2.4]
GAMMA_VALUES = [0.1, 0.2, 0.3]
NUM_SOURCES_LIST = [1, 2, 4]
GEOMETRIES = ['symmetric', 'clustered']
PHASE_OFFSETS = [0]
TIME_HORIZONS = [200, 500]

OUTPUT_CSV = "../results/variant_a_3d_plus_time.csv"
OUTPUT_JSON = "../results/variant_a_3d_plus_time.json"

if __name__ == "__main__":
    print("=" * 80)
    print("VARIANT A: 3D + Time -> Should behave like 4D?")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSpatial dimension: {SPATIAL_DIM}D")
    print(f"Total dimension (physics): {SPATIAL_DIM + 1}D")
    print(f"Grid: {GRID_SIZE} + time({TIME_WINDOW_SIZE})\n")

    param_grid = list(itertools.product(
        ALPHA_0_VALUES, GAMMA_VALUES, NUM_SOURCES_LIST,
        GEOMETRIES, PHASE_OFFSETS, TIME_HORIZONS
    ))

    print(f"Total configurations: {len(param_grid)}\n")

    results = []
    for i, (alpha_0, gamma, num_sources, geometry, phase, T) in enumerate(param_grid, 1):
        print(f"[{i}/{len(param_grid)}] a0={alpha_0}, g={gamma}, Ms={num_sources}, geom={geometry}, T={T}...", end=' ', flush=True)

        config = create_symmetric_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0) if geometry == 'symmetric' else create_clustered_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0)

        result = run_gpu_simulation(
            config=config, dimension=SPATIAL_DIM, grid_sizes=GRID_SIZE,
            alpha_0=alpha_0, alpha_1=1.0, gamma=gamma, M=1, T=T,
            time_window_size=TIME_WINDOW_SIZE
        )

        if result is not None:
            results.append(result)
            print(f"OK commits={result['statistics']['agent_commit_count']}, rate={result['statistics']['commit_rate']:.4f}")
        else:
            print("CFL violated")

    print(f"\n{'=' * 80}\nSWEEP COMPLETE\n{'=' * 80}")
    print(f"Successful: {len(results)}/{len(param_grid)}\n")

    with open(OUTPUT_CSV, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=list(results[0]['parameters'].keys()) + list(results[0]['statistics'].keys()))
            writer.writeheader()
            for result in results:
                writer.writerow({**result['parameters'], **result['statistics']})

    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 80)
