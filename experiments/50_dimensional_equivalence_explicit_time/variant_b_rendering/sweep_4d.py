"""Variant B: 4D with Sliding Window. Time in storage, physics=4D. Expected runtime: ~30-60 min"""
import csv, json, itertools, sys
from datetime import datetime
sys.path.append('..')
from gpu_wave_solver import create_symmetric_config_nd, create_clustered_config_nd, run_gpu_simulation

SPATIAL_DIM, GRID_SIZE, TIME_WINDOW_SIZE = 4, (16,16,16,16), 10
ALPHA_0_VALUES, GAMMA_VALUES, NUM_SOURCES_LIST = [0.8,1.2,1.6,2.0,2.4], [0.1,0.2,0.3], [1,2,4]
GEOMETRIES, PHASE_OFFSETS, TIME_HORIZONS = ['symmetric','clustered'], [0], [200,500]
OUTPUT_CSV, OUTPUT_JSON = "../results/variant_b_4d.csv", "../results/variant_b_4d.json"

if __name__ == "__main__":
    print("="*80 + "\nVARIANT B: 4D with Time Storage\n" + "="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\nPhysics: {SPATIAL_DIM}D, Grid: {GRID_SIZE}\n")
    param_grid = list(itertools.product(ALPHA_0_VALUES, GAMMA_VALUES, NUM_SOURCES_LIST, GEOMETRIES, PHASE_OFFSETS, TIME_HORIZONS))
    print(f"Total: {len(param_grid)}\n")
    results = []
    for i, (a0, g, ms, geom, p, T) in enumerate(param_grid, 1):
        print(f"[{i}/{len(param_grid)}] a0={a0}, g={g}, Ms={ms}, T={T}...", end=' ', flush=True)
        cfg = create_symmetric_config_nd(ms, SPATIAL_DIM, 1.0, a0) if geom=='symmetric' else create_clustered_config_nd(ms, SPATIAL_DIM, 1.0, a0)
        res = run_gpu_simulation(cfg, SPATIAL_DIM, GRID_SIZE, a0, 1.0, g, 1, T, TIME_WINDOW_SIZE)
        if res:
            results.append(res)
            print(f"OK c={res['statistics']['agent_commit_count']}")
        else:
            print("CFL")
    print(f"\nDONE: {len(results)}/{len(param_grid)}")
    with open(OUTPUT_CSV, 'w', newline='') as f:
        if results:
            writer = csv.DictWriter(f, fieldnames=list(results[0]['parameters'].keys()) + list(results[0]['statistics'].keys()))
            writer.writeheader()
            for r in results:
                writer.writerow({**r['parameters'], **r['statistics']})
    with open(OUTPUT_JSON, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
