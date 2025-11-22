"""
V6 Parallel Launcher

Launches all 5 dimensional experiments in parallel as background processes.
"""

import subprocess
import os
from datetime import datetime

print("="*80)
print("V6: PARALLEL DIMENSIONAL SWEEP LAUNCHER")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Dimension scripts
dimension_scripts = [
    "v6_dimension_1d.py",
    "v6_dimension_2d.py",
    "v6_dimension_3d.py",
    "v6_dimension_4d.py",
    "v6_dimension_5d.py"
]

# Launch each dimension in background
processes = []

for script in dimension_scripts:
    dim = script.split('_')[2].replace('.py', '').upper()
    log_file = f"v6_{dim}_log.txt"

    print(f"Launching {dim}...")
    print(f"  Script: {script}")
    print(f"  Log: {log_file}")

    # Start process in background, redirecting output to log file
    with open(log_file, 'w') as log:
        process = subprocess.Popen(
            ['python', script],
            stdout=log,
            stderr=subprocess.STDOUT,
            cwd=os.getcwd()
        )

    processes.append((dim, process, log_file))
    print(f"  PID: {process.pid}\n")

print("="*80)
print(f"All {len(processes)} dimensions launched in parallel!")
print("="*80)

print("\nProcess Summary:")
print(f"{'Dimension':<12} {'PID':<10} {'Log File'}")
print("-"*60)
for dim, proc, log in processes:
    print(f"{dim:<12} {proc.pid:<10} {log}")

print("\n" + "="*80)
print("MONITORING INSTRUCTIONS")
print("="*80)
print("\nTo monitor progress, check log files:")
for dim, proc, log in processes:
    print(f"  tail -f {log}")

print("\nTo check if processes are still running:")
print("  ps aux | grep v6_dimension")

print("\nTo kill all processes if needed:")
for dim, proc, log in processes:
    print(f"  kill {proc.pid}  # {dim}")

print("\nExpected completion time:")
print("  1D: ~5-10 minutes")
print("  2D: ~15-30 minutes")
print("  3D: ~1-2 hours")
print("  4D: ~2-4 hours")
print("  5D: ~3-6 hours")

print("\nResults will be saved as:")
print("  v6_1d_results.json/.csv")
print("  v6_2d_results.json/.csv")
print("  v6_3d_results.json/.csv")
print("  v6_4d_results.json/.csv")
print("  v6_5d_results.json/.csv")

print("\n" + "="*80)
print("All experiments running in background!")
print("This launcher can now exit.")
print("="*80)
