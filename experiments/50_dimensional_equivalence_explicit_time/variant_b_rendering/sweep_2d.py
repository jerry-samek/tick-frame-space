"""Variant B: 2D with Sliding Window Storage. Time in storage only, physics remains 2D. Expected runtime: ~2-3 hours"""
import csv, json, itertools, sys
from datetime import datetime
sys.path.append('..')
from gpu_wave_solver import create_symmetric_config_nd, create_clustered_config_nd, run_gpu_simulation

SPATIAL_DIM, GRID_SIZE, TIME_WINDOW_SIZE = 2, (64,64), 10
ALPHA_0_VALUES, GAMMA_VALUES, NUM_SOURCES_LIST = [0.8,1.2,1.6,2.0,2.4], [0.1,0.2,0.3], [1,2,4]
GEOMETRIES, PHASE_OFFSETS, TIME_HORIZONS = ['symmetric','clustered'], [0], [200,500]
OUTPUT_CSV, OUTPUT_JSON = "../results/variant_b_2d.csv", "../results/variant_b_2d.json"

if __name__ == "__main__":
    print("="*80 + "\nVARIANT B: 2D with Time Storage (physics=2D, storage has time)\n" + "="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nPhysics: {SPATIAL_DIM}D, Grid: {GRID_SIZE}, Time window: {TIME_WINDOW_SIZE}\n")
    param_grid = list(itertools.product(ALPHA_0_VALUES, GAMMA_VALUES, NUM_SOURCES_LIST, GEOMETRIES, PHASE_OFFSETS, TIME_HORIZONS))
    print(f"Total configurations: {len(param_grid)}\n")
    results = []
    for i, (alpha_0, gamma, num_sources, geometry, phase, T) in enumerate(param_grid, 1):
        print(f"[{i}/{len(param_grid)}] a0={alpha_0}, g={gamma}, Ms={num_sources}, geom={geometry}, T={T}...", end=' ', flush=True)
        config = create_symmetric_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0) if geometry == 'symmetric' else create_clustered_config_nd(num_sources, SPATIAL_DIM, 1.0, alpha_0)
        result = run_gpu_simulation(config=config, dimension=SPATIAL_DIM, grid_sizes=GRID_SIZE, alpha_0=alpha_0, alpha_1=1.0, gamma=gamma, M=1, T=T, time_window_size=TIME_WINDOW_SIZE)
        if result:
            results.append(result)
            print(f"OK commits={result['statistics']['agent_commit_count']}, rate={result['statistics']['commit_rate']:.4f}")
        else:
            print("CFL violated")
    print(f"\n{'='*80}\nSWEEP COMPLETE\n{'='*80}\nSuccessful: {len(results)}/{len(param_grid)}\n")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=list(results[0]['parameters'].keys()) + list(results[0]['statistics'].keys()))
            writer.writeheader()
            for result in results:
                writer.writerow({**result['parameters'], **result['statistics']})
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n" + "="*80)
