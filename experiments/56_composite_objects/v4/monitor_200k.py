#!/usr/bin/env python3
"""
Monitor 200k tick quantization study progress.

Periodically check and report on simulation status.
"""

import time
import os
import json
from pathlib import Path

result_file = Path('results/exp56a_v4_50frags_200k.json')
log_file = Path('results/quantization_200k.log')

print("Monitoring 200k tick quantization study...")
print(f"Looking for: {result_file}")
print()

# Monitor loop
start_time = time.time()
last_check_size = 0

while True:
    elapsed = time.time() - start_time

    # Check if results file exists (simulation complete)
    if result_file.exists():
        print(f"\n{'='*60}")
        print(f"SIMULATION COMPLETE! ({elapsed:.0f}s elapsed)")
        print(f"{'='*60}\n")

        # Load and display results
        data = json.load(open(result_file))
        r = data['results']

        print(f"  Fragments: {data['config']['n_fragments']}")
        print(f"  Jitter: {data['config']['jitter_strength']}")
        print(f"  Ticks: {data['config']['num_ticks']:,}")
        print()
        print(f"  Initial radius: {r['cloud_radius_initial']:.4f}")
        print(f"  Final radius: {r['cloud_radius_final']:.4f}")
        print(f"  Drift: {r['cloud_radius_drift_percent']:.2f}%")
        print(f"  Escaped: {r['n_escaped']}/50")
        print(f"  Success: {r['success']}")
        print()

        # Energy timeline
        snaps = data['snapshots']
        print("Energy Timeline:")
        checkpoints = [1000, 10000, 50000, 51600, 75000, 100000, 150000, 200000]
        for s in snaps:
            if s['tick'] in checkpoints:
                E = s.get('total_energy', 0)
                r_rms = s['cloud_radius_rms']
                print(f"  Tick {s['tick']:7d}: r={r_rms:7.2f}, E_total={E:10.6f}")

        print(f"\n{'='*60}")
        break

    # Check log file for progress
    if log_file.exists():
        log_size = log_file.stat().st_size

        # Only print update if log has grown
        if log_size > last_check_size:
            last_check_size = log_size

            # Find last progress line
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Look for most recent progress line
            progress_lines = [l for l in lines if l.startswith('[') and '/' in l]
            if progress_lines:
                last_progress = progress_lines[-1].strip()
                print(f"[{elapsed:6.0f}s] {last_progress}")

    # Wait before next check
    time.sleep(30)

print("\nMonitoring complete!")
