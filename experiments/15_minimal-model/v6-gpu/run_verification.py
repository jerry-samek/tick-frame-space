"""
Run 1D-2D Verification Experiments

Launches 1D and 2D experiments sequentially to verify GPU+multiprocessing setup.
"""

import subprocess
import sys
from datetime import datetime

print("="*80)
print("V6-GPU VERIFICATION: 1D + 2D Experiments")
print("="*80)
print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# Run 1D
print("PHASE 1: Running 1D experiment...")
print("-"*80)
result_1d = subprocess.run([sys.executable, "v6_gpu_1d.py"], capture_output=False)

if result_1d.returncode != 0:
    print("\nERROR: 1D experiment failed!")
    sys.exit(1)

print("\n" + "="*80)
print("1D Complete! Starting 2D...")
print("="*80)
print()

# Run 2D
print("PHASE 2: Running 2D experiment...")
print("-"*80)
result_2d = subprocess.run([sys.executable, "v6_gpu_2d.py"], capture_output=False)

if result_2d.returncode != 0:
    print("\nERROR: 2D experiment failed!")
    sys.exit(1)

print("\n" + "="*80)
print("VERIFICATION COMPLETE!")
print("="*80)
print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()
print("Results:")
print("  1D: v6_gpu_1d_results.json, v6_gpu_1d_results.csv")
print("  2D: v6_gpu_2d_results.json, v6_gpu_2d_results.csv")
