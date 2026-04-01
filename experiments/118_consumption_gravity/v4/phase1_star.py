#!/usr/bin/env python3
"""
Experiment 118 v4 — Phase 1: Star Equilibrium

Goal: Demonstrate that 80 star nodes in 4 groups reach internal equilibrium
using only the one-quantum-per-tick append-only mechanic.

No planet. Star only. No subtraction. No EXTEND_RATE. No CONSUME_FRAC.
Connector length = initial geometric distance + total deposits appended.

Success criteria:
  1. Star COM stays approximately stationary (drift < 2 units)
  2. Star mean radius stabilizes (sigma < 15% of mean over last 20k ticks)
  3. Internal connectors grow at bounded rate (linear, not exponential)
  4. Boundary connectors accumulate deposits (radiation)
  5. Discharge rate stabilizes
"""

import os
import sys
import time
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph import Graph
from entity import Entity

# ── Configuration ──────────────────────────────────────────────
SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24

STAR_COUNT = 80
STAR_GROUPS = 4

TICKS = 50000
MEASURE_EVERY = 500
LOG_EVERY = 5000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    # ── Build graph ──
    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # ── Place star near origin ──
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}

    max_r = np.linalg.norm(g.pos[star_node_ids[-1]])
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={max_r:.2f}")
    print(f"Star spectrum: {star_spectrum}")

    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    initial_com = star.com(g)
    print(f"Initial COM: [{initial_com[0]:.2f}, {initial_com[1]:.2f}, {initial_com[2]:.2f}]")
    print(f"Initial mean radius: {star.mean_radius(g):.2f}")

    # ── Measurement storage ──
    rows = []

    # ── Run ──
    print(f"\n{'=' * 60}")
    print(f"PHASE 1: Star Equilibrium ({TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()

    for tick in range(1, TICKS + 1):
        g.rotate_all()   # advance epoch: last tick's deposits become visible
        star.tick(g, rng)

        if tick % MEASURE_EVERY == 0:
            com = star.com(g)
            com_drift = float(np.linalg.norm(com - initial_com))
            mean_r = star.mean_radius(g)
            max_r = star.max_radius(g)
            discharge = star.discharge_rate()
            int_mean, int_max, int_count = star.internal_connector_stats(g)
            bnd_mean, bnd_max, bnd_count = star.boundary_connector_stats(g)
            rad_deposits, rad_connectors = star.boundary_radiation(g)

            rows.append({
                'tick': tick,
                'com_x': com[0], 'com_y': com[1], 'com_z': com[2],
                'com_drift': com_drift,
                'mean_radius': mean_r,
                'max_radius': max_r,
                'discharge_rate': discharge,
                'int_conn_mean_len': int_mean,
                'int_conn_max_len': int_max,
                'int_conn_count': int_count,
                'bnd_conn_mean_len': bnd_mean,
                'bnd_conn_max_len': bnd_max,
                'bnd_conn_count': bnd_count,
                'radiation_deposits': rad_deposits,
                'radiation_connectors': rad_connectors,
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            print(f"  t={tick:6d}  COM_drift={r['com_drift']:.2f}  "
                  f"mean_r={r['mean_radius']:.2f}  max_r={r['max_radius']:.2f}  "
                  f"discharge={r['discharge_rate']:.2f}  "
                  f"int_len={r['int_conn_mean_len']:.1f}/{r['int_conn_max_len']:.1f}  "
                  f"bnd_len={r['bnd_conn_mean_len']:.1f}  "
                  f"radiation={r['radiation_deposits']:.0f}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    # ── Save CSV ──
    csv_path = os.path.join(OUT, "phase1_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    # ── Analysis ──
    analyze(rows)

    # ── Plots ──
    plot(rows)


def analyze(rows):
    """Check success criteria against the data."""
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # Criterion 1: COM drift < 2 units
    final_drift = rows[-1]['com_drift']
    max_drift = max(r['com_drift'] for r in rows)
    status1 = "PASS" if max_drift < 2.0 else "FAIL"
    print(f"  1. COM stability:  final_drift={final_drift:.3f}  "
          f"max_drift={max_drift:.3f}  [{status1}]")

    # Criterion 2: mean radius stabilizes (last 20k ticks, sigma < 15% of mean)
    last_rows = [r for r in rows if r['tick'] > 30000]
    if last_rows:
        radii = [r['mean_radius'] for r in last_rows]
        mean_r = np.mean(radii)
        std_r = np.std(radii)
        cv = std_r / mean_r if mean_r > 0 else float('inf')
        status2 = "PASS" if cv < 0.15 else "FAIL"
        print(f"  2. Radius stability (last 20k): mean={mean_r:.2f}  "
              f"std={std_r:.3f}  CV={cv:.3f}  [{status2}]")
    else:
        print("  2. Radius stability: not enough data")

    # Criterion 3: internal connectors not runaway (check growth rate)
    first_int = rows[0]['int_conn_mean_len']
    last_int = rows[-1]['int_conn_mean_len']
    int_max = rows[-1]['int_conn_max_len']
    # Linear growth: length ~ initial + rate * ticks. Exponential would be >> 1e6.
    status3 = "PASS" if int_max < 1e6 else "FAIL"
    print(f"  3. Internal connectors: start={first_int:.1f}  "
          f"end_mean={last_int:.1f}  end_max={int_max:.1f}  [{status3}]")

    # Criterion 4: radiation (boundary deposits > 0)
    final_rad = rows[-1]['radiation_deposits']
    status4 = "PASS" if final_rad > 0 else "FAIL"
    print(f"  4. Radiation: {final_rad:.0f} deposits on "
          f"{rows[-1]['radiation_connectors']} boundary connectors  [{status4}]")

    # Criterion 5: discharge rate stabilizes
    if last_rows:
        rates = [r['discharge_rate'] for r in last_rows]
        mean_rate = np.mean(rates)
        std_rate = np.std(rates)
        cv_rate = std_rate / mean_rate if mean_rate > 0 else float('inf')
        status5 = "PASS" if cv_rate < 0.15 else "FAIL"
        print(f"  5. Discharge rate (last 20k): mean={mean_rate:.3f}  "
              f"std={std_rate:.4f}  CV={cv_rate:.3f}  [{status5}]")
    else:
        print("  5. Discharge rate: not enough data")

    print()


def plot(rows):
    """Generate Phase 1 result plots."""
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 2, figsize=(14, 12))
    fig.suptitle('Experiment 118 v4 — Phase 1: Star Equilibrium', fontsize=14)

    # 1. COM drift
    ax = axes[0, 0]
    ax.plot(ticks, [r['com_drift'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('COM drift from initial')
    ax.set_title('COM Stability')
    ax.axhline(2.0, color='r', linestyle='--', alpha=0.5, label='threshold=2.0')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Mean and max radius
    ax = axes[0, 1]
    ax.plot(ticks, [r['mean_radius'] for r in rows], 'b-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['max_radius'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.set_ylabel('Radius')
    ax.set_title('Star Radius')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Internal connector lengths
    ax = axes[1, 0]
    ax.plot(ticks, [r['int_conn_mean_len'] for r in rows], 'b-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['int_conn_max_len'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.set_ylabel('Length')
    ax.set_title('Internal Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Boundary connector lengths
    ax = axes[1, 1]
    ax.plot(ticks, [r['bnd_conn_mean_len'] for r in rows], 'g-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['bnd_conn_max_len'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.set_ylabel('Length')
    ax.set_title('Boundary Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. Radiation
    ax = axes[2, 0]
    ax.plot(ticks, [r['radiation_deposits'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Total deposits')
    ax.set_xlabel('Tick')
    ax.set_title('Boundary Radiation (star deposits on boundary connectors)')
    ax.grid(True, alpha=0.3)

    # 6. Discharge rate
    ax = axes[2, 1]
    ax.plot(ticks, [r['discharge_rate'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Fraction fired')
    ax.set_xlabel('Tick')
    ax.set_title('Discharge Rate')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase1_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
