"""
Test the 5 missing 4D runs with 30-minute constant timeout.
"""

import json
import time
from datetime import datetime
from parallel_experiment_runner import run_single_experiment

# Load missing runs
with open('missing_4d_runs.json', 'r') as f:
    missing_runs = json.load(f)

print("="*80)
print("4D MISSING RUNS TEST - 30 Minute Constant Timeout")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Testing {len(missing_runs)} configurations")
print(f"Timeout: 1800 seconds (30 minutes) per run")
print("="*80)
print()

DIMENSION = 4
GRID_SIZE = (16, 16, 16, 16)
M = 1
alpha_1 = 1.0

results = []
for i, params in enumerate(missing_runs):
    run_id = params['run_id']
    print(f"\n[{i+1}/{len(missing_runs)}] Testing Run ID {run_id}:")
    print(f"  num_sources={params['num_sources']}, geometry={params['geometry']}, "
          f"phase_offset={params['phase_offset']}")
    print(f"  T={params['T']}, gamma={params['gamma']}, alpha_0={params['alpha_0']}")

    start_time = time.time()

    try:
        result = run_single_experiment(
            num_sources=params['num_sources'],
            geometry=params['geometry'],
            phase_offset=params['phase_offset'],
            T=params['T'],
            gamma=params['gamma'],
            alpha_0=params['alpha_0'],
            dimension=DIMENSION,
            grid_sizes=GRID_SIZE,
            alpha_1=alpha_1,
            M=M
        )

        elapsed = time.time() - start_time

        if result is not None:
            print(f"  [OK] SUCCESS in {elapsed:.1f}s ({elapsed/60:.1f} min)")
            print(f"    Commits: {result['statistics']['agent_commit_count']}, "
                  f"Salience: {result['statistics']['max_salience']:.2f}")
            results.append({
                'run_id': run_id,
                'status': 'success',
                'elapsed_seconds': elapsed,
                'result': result
            })
        else:
            print(f"  [FAIL] FAILED in {elapsed:.1f}s (returned None)")
            results.append({
                'run_id': run_id,
                'status': 'failed',
                'elapsed_seconds': elapsed,
                'result': None
            })

    except Exception as e:
        elapsed = time.time() - start_time
        print(f"  [ERR] ERROR in {elapsed:.1f}s: {e}")
        results.append({
            'run_id': run_id,
            'status': 'error',
            'elapsed_seconds': elapsed,
            'error': str(e)
        })

print()
print("="*80)
print("RESULTS SUMMARY")
print("="*80)

success_count = sum(1 for r in results if r['status'] == 'success')
fail_count = sum(1 for r in results if r['status'] != 'success')

print(f"Successful: {success_count}/{len(results)}")
print(f"Failed: {fail_count}/{len(results)}")

if success_count > 0:
    times = [r['elapsed_seconds'] for r in results if r['status'] == 'success']
    print(f"Average time for success: {sum(times)/len(times)/60:.1f} minutes")
    print(f"Max time: {max(times)/60:.1f} minutes")

# Save results
with open('test_4d_missing_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print(f"\nCompleted: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print(f"Results saved to: test_4d_missing_results.json")
