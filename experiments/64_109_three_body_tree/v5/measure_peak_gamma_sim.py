"""Measure PEAK gamma at entity position via simulation on actual lattice.

Runs a single entity on a lattice graph for many deposit-move cycles
and measures the peak gamma at the entity's node just before each hop.
"""

import numpy as np
import sys
import os
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from three_body_graph import GammaFieldGraph

masses = [1, 2, 3, 5, 10, 20]
k = 6
decay = 0.9999
deposit_amount = 1.0
alpha = 1.0 / k
n_cycles = 500  # deposit-move cycles per mass

# Analytical prediction for one cycle (no background)
r = (1.0 - alpha) * decay

print("=" * 90)
print("PEAK GAMMA AT ENTITY POSITION: Simulation on 3D lattice")
print("=" * 90)
print()

# Build lattice
side = 21  # 21^3 = 9261 nodes (small but enough)
n_nodes = side ** 3
print(f"Building lattice: {side}^3 = {n_nodes} nodes, k={k}")
t0 = time.time()
fg = GammaFieldGraph(n_nodes, k=k, spread_fraction=alpha, decay=decay,
                     graph_type='lattice')
fg.add_field("entity")
print(f"  Built in {time.time()-t0:.1f}s")
print()

# Find center node
center = n_nodes // 2

for M in masses:
    # Reset field
    fg.fields["entity"] = np.zeros(n_nodes, dtype=np.float64)

    node = center
    prev_node = center
    peaks_at_hop = []  # peak gamma at entity position just before hopping
    peaks_after_deposit = []  # peak after all M deposits

    for cycle in range(n_cycles):
        # Sit for M ticks, depositing each tick
        for tick in range(M):
            fg.spread_all()
            # Mass-conserving deposit
            available = fg.fields["entity"][prev_node]
            withdraw = min(deposit_amount, available)
            fg.fields["entity"][prev_node] -= withdraw
            fg.fields["entity"][node] += deposit_amount

        # Record peak at entity position AFTER M deposits (just before hop)
        peak = fg.fields["entity"][node]
        peaks_at_hop.append(peak)

        # Move to a neighbor (cycle through neighbors deterministically)
        nbs = list(fg.graph.neighbors(node))
        prev_node = node
        node = nbs[cycle % len(nbs)]  # deterministic cycling

    # Steady-state peak (last 50% of cycles)
    ss_peaks = peaks_at_hop[n_cycles // 2:]
    ss_peak = np.mean(ss_peaks)
    ss_std = np.std(ss_peaks)

    # Analytical (one cycle, no background)
    peak_ana = deposit_amount * (1.0 - r**M) / (1.0 - r)

    # Total field energy
    total_field = float(np.sum(fg.fields["entity"]))

    print(f"Mass = {M}:")
    print(f"  Analytical (one cycle): {peak_ana:.4f}")
    print(f"  Simulated SS peak:      {ss_peak:.4f} +/- {ss_std:.4f}")
    print(f"  Ratio sim/analytical:   {ss_peak/peak_ana:.4f}")
    print(f"  Total field energy:     {total_field:.2f}")
    print(f"  Peak / M:               {ss_peak/M:.4f}")
    print(f"  Peak / M^2:             {ss_peak/M**2:.6f}")
    print()

# Now the key table
print()
print("=" * 90)
print("SUMMARY TABLE")
print("=" * 90)
print()
print(f"{'Mass':>5} | {'v=c/M':>7} | {'SS Peak':>10} | {'Peak/M':>8} | {'Peak*M':>8} | {'Peak/ln(M)':>10} | {'Analytical':>10}")
print("-" * 75)

# Re-run just to collect clean data
all_peaks = {}
for M in masses:
    fg.fields["entity"] = np.zeros(n_nodes, dtype=np.float64)
    node = center
    prev_node = center
    peaks = []

    for cycle in range(n_cycles):
        for tick in range(M):
            fg.spread_all()
            available = fg.fields["entity"][prev_node]
            withdraw = min(deposit_amount, available)
            fg.fields["entity"][prev_node] -= withdraw
            fg.fields["entity"][node] += deposit_amount

        peaks.append(fg.fields["entity"][node])
        nbs = list(fg.graph.neighbors(node))
        prev_node = node
        node = nbs[cycle % len(nbs)]

    ss = np.mean(peaks[n_cycles//2:])
    all_peaks[M] = ss
    peak_ana = deposit_amount * (1.0 - r**M) / (1.0 - r)
    logM = np.log(M) if M > 1 else 1.0
    print(f"{M:5d} | {1.0/M:7.4f} | {ss:10.4f} | {ss/M:8.4f} | {ss*M:8.2f} | {ss/logM:10.4f} | {peak_ana:10.4f}")

# Scaling analysis
print()
print("=" * 90)
print("SCALING: peak(M) / peak(1)")
print("=" * 90)
print()

p1 = all_peaks[1]
for M in masses:
    p = all_peaks[M]
    ratio = p / p1
    print(f"  M={M:3d}: ratio = {ratio:.4f}, M = {M}, sqrt(M) = {np.sqrt(M):.3f}, ln(M)+1 = {np.log(M)+1:.3f}")

# Check if peak(M) = A * (1 - exp(-B*M)) — saturating exponential
print()
print("=" * 90)
print("FIT: peak(M) = A * (1 - exp(-B * M))")
print("=" * 90)
print()
from scipy.optimize import curve_fit

def sat_exp(M, A, B):
    return A * (1.0 - np.exp(-B * M))

M_arr = np.array(masses, dtype=float)
P_arr = np.array([all_peaks[M] for M in masses])

try:
    popt, pcov = curve_fit(sat_exp, M_arr, P_arr, p0=[10.0, 0.2])
    A_fit, B_fit = popt
    print(f"  Best fit: peak = {A_fit:.4f} * (1 - exp(-{B_fit:.4f} * M))")
    print()
    for M in masses:
        pred = sat_exp(M, A_fit, B_fit)
        actual = all_peaks[M]
        print(f"  M={M:3d}: predicted={pred:.4f}, actual={actual:.4f}, error={abs(pred-actual)/actual*100:.2f}%")
except Exception as e:
    print(f"  Fit failed: {e}")
