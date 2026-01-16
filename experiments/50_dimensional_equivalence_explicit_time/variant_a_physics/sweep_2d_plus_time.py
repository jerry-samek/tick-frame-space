"""
Variant A: 2D + Time Parameter Sweep

Tests whether (2D spatial + 1D time) behaves like 3D spatially.

Hypothesis: If time is a true dimension, (2D+t) should match the 3D baseline.

Focused sweep: ~100 configurations covering key parameter ranges
Expected runtime: ~2-3 hours on CPU
"""

import csv
import json
import itertools
from datetime import datetime
import sys
sys.path.append('..')

from gpu_wave_solver import create_symmetric_config_nd, create_clustered_config_nd, run_gpu_simulation

#============================================================================
# EXPERIMENT CONFIGURATION
# ============================================================================

SPATIAL_DIM = 2
GRID_SIZE = (64, 64)  # Match 2D from v7-final
TIME_WINDOW_SIZE = 10

# Focused parameter ranges
ALPHA_0_VALUES = [0.8, 1.2, 1.6, 2.0, 2.4]  # 5 values (covers stable→unstable transition)
GAMMA_VALUES = [0.1, 0.2, 0.3]  # 3 values
NUM_SOURCES_LIST = [1, 2, 4]  # 3 values
GEOMETRIES = ['symmetric', 'clustered']  # 2 values
PHASE_OFFSETS = [0]  # 1 value (known to be neutral at high dimensions)
TIME_HORIZONS = [200, 500]  # 2 values

OUTPUT_CSV = "../results/variant_a_2d_plus_time.csv"
OUTPUT_JSON = "../results/variant_a_2d_plus_time.json"

# Calculate total: 5×3×3×2×1×2 = 180 configs

if __name__ == "__main__":
    print("=" * 80)
    print("VARIANT A: 2D + Time → Should behave like 3D?")
    print("=" * 80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nSpatial dimension: {SPATIAL_DIM}D")
    print(f"Time dimension: explicit (window size = {TIME_WINDOW_SIZE})")
    print(f"Total dimension (physics): {SPATIAL_DIM + 1}D")
    print(f"Grid: {GRID_SIZE} + time({TIME_WINDOW_SIZE})\n")

    # Build parameter grid
    param_grid = list(itertools.product(
        ALPHA_0_VALUES,
        GAMMA_VALUES,
        NUM_SOURCES_LIST,
        GEOMETRIES,
        PHASE_OFFSETS,
        TIME_HORIZONS
    ))

    print(f"Total configurations: {len(param_grid)}\n")

    results = []
    for i, (alpha_0, gamma, num_sources, geometry, phase, T) in enumerate(param_grid, 1):
        print(f"[{i}/{len(param_grid)}] a0={alpha_0}, g={gamma}, Ms={num_sources}, geom={geometry}, T={T}...", end=' ', flush=True)

        # Create source configuration
        if geometry == 'symmetric':
            config = create_symmetric_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0)
        else:
            config = create_clustered_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0)

        # Run simulation with explicit time dimension
        result = run_gpu_simulation(
            config=config,
            dimension=SPATIAL_DIM,
            grid_sizes=GRID_SIZE,
            alpha_0=alpha_0,
            alpha_1=1.0,
            gamma=gamma,
            M=1,
            T=T,
            time_window_size=TIME_WINDOW_SIZE
        )

        if result is not None:
            results.append(result)
            commits = result['statistics']['agent_commit_count']
            rate = result['statistics']['commit_rate']
            print(f"OK commits={commits}, rate={rate:.4f}")
        else:
            print("CFL violated")

    print(f"\n{'=' * 80}")
    print(f"SWEEP COMPLETE")
    print(f"{'=' * 80}")
    print(f"Total: {len(param_grid)}")
    print(f"Successful: {len(results)}")
    print(f"Failed: {len(param_grid) - len(results)}\n")

    # Save results
    print(f"Saving to {OUTPUT_CSV}")
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
