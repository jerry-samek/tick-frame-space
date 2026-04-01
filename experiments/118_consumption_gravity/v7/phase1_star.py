#!/usr/bin/env python3
"""
Experiment 118 v7 — Phase 1: Star Equilibrium

Traversal time proportional to connector length. Routing on absolute
matching count. The star binds via time dilation: center nodes are
trapped on long connectors, boundary nodes move freely.

Success criteria:
  1. Star mean radius < 2x initial (~3.84 -> target <8)
  2. COM drift < 3.0
  3. Internal connectors longer than boundary connectors (time well)
  4. Idle fraction decreases over time (more nodes in transit)
  5. No runaway: linear growth in real time
"""

import os
import time
import csv
import numpy as np
from collections import deque

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

TICKS = 100000  # longer because traversals take time
MEASURE_EVERY = 1000
LOG_EVERY = 10000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}

    max_r = np.linalg.norm(g.pos[star_node_ids[-1]])
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={max_r:.2f}")

    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    initial_com = star.com(g)
    print(f"Initial COM: [{initial_com[0]:.2f}, {initial_com[1]:.2f}, {initial_com[2]:.2f}]")
    print(f"Initial mean radius: {star.mean_radius(g):.2f}")

    rows = []

    print(f"\n{'=' * 60}")
    print(f"PHASE 1: Star Equilibrium ({TICKS} ticks, traversal-time model)")
    print(f"{'=' * 60}\n")

    t0 = time.time()

    for tick in range(1, TICKS + 1):
        star.tick(g, rng)

        if tick % MEASURE_EVERY == 0:
            com = star.com(g)
            com_drift = float(np.linalg.norm(com - initial_com))
            mean_r = star.mean_radius(g)
            max_r_val = star.max_radius(g)
            idle = star.idle_fraction()
            hops = star.total_hops()
            int_mean, int_max, int_count = star.internal_connector_stats(g)
            bnd_mean, bnd_max, bnd_count = star.boundary_connector_stats(g)
            total_deps = sum(c.total for c in g.connectors.values())

            rows.append({
                'tick': tick,
                'com_drift': com_drift,
                'mean_radius': mean_r,
                'max_radius': max_r_val,
                'idle_fraction': idle,
                'total_hops': hops,
                'int_conn_mean': int_mean,
                'int_conn_max': int_max,
                'int_conn_count': int_count,
                'bnd_conn_mean': bnd_mean,
                'bnd_conn_max': bnd_max,
                'bnd_conn_count': bnd_count,
                'total_deposits': total_deps,
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            int_bnd_ratio = r['int_conn_mean'] / r['bnd_conn_mean'] if r['bnd_conn_mean'] > 0 else 0
            print(f"  t={tick:7d}  COM={r['com_drift']:.2f}  "
                  f"mean_r={r['mean_radius']:.2f}  "
                  f"idle={r['idle_fraction']:.2f}  "
                  f"hops={r['total_hops']}  "
                  f"int={r['int_conn_mean']:.0f}/{r['int_conn_max']:.0f}  "
                  f"bnd={r['bnd_conn_mean']:.0f}/{r['bnd_conn_max']:.0f}  "
                  f"ratio={int_bnd_ratio:.2f}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "phase1_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    analyze(rows)
    plot(rows)


def analyze(rows):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    last_rows = [r for r in rows if r['tick'] > TICKS * 0.6]

    # 1. Star compact
    if last_rows:
        mean_r = np.mean([r['mean_radius'] for r in last_rows])
        status1 = "PASS" if mean_r < 8.0 else "FAIL"
        print(f"  1. Star compact: mean_r={mean_r:.2f}  [target <8.0]  [{status1}]")

    # 2. COM stable
    max_drift = max(r['com_drift'] for r in rows)
    status2 = "PASS" if max_drift < 3.0 else "FAIL"
    print(f"  2. COM stability: max_drift={max_drift:.2f}  [target <3.0]  [{status2}]")

    # 3. Time well: internal > boundary
    if last_rows:
        int_mean = np.mean([r['int_conn_mean'] for r in last_rows])
        bnd_mean = np.mean([r['bnd_conn_mean'] for r in last_rows])
        ratio = int_mean / bnd_mean if bnd_mean > 0 else 0
        status3 = "PASS" if ratio > 1.5 else "FAIL"
        print(f"  3. Time well: int/bnd={ratio:.2f}  "
              f"(int={int_mean:.0f}, bnd={bnd_mean:.0f})  [target >1.5]  [{status3}]")

    # 4. Idle fraction decreases (time dilation)
    if len(rows) >= 10:
        early_idle = np.mean([r['idle_fraction'] for r in rows[:5]])
        late_idle = np.mean([r['idle_fraction'] for r in rows[-5:]])
        status4 = "PASS" if late_idle < early_idle else "FAIL"
        print(f"  4. Time dilation: idle {early_idle:.3f} -> {late_idle:.3f}  [{status4}]")

    # 5. No runaway
    max_conn = max(r['int_conn_max'] for r in rows)
    status5 = "PASS" if max_conn < 100000 else "FAIL"
    print(f"  5. Max connector: {max_conn:.0f}  [target <100000]  [{status5}]")

    print()


def plot(rows):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v7 — Phase 1: Star Equilibrium '
                 '(traversal-time model)', fontsize=14)

    # 1. COM drift
    ax = axes[0, 0]
    ax.plot(ticks, [r['com_drift'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(3.0, color='r', linestyle='--', alpha=0.5)
    ax.set_ylabel('COM drift')
    ax.set_title('COM Stability')
    ax.grid(True, alpha=0.3)

    # 2. Mean and max radius
    ax = axes[0, 1]
    ax.plot(ticks, [r['mean_radius'] for r in rows], 'b-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['max_radius'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.axhline(8.0, color='g', linestyle='--', alpha=0.5, label='target<8')
    ax.set_ylabel('Radius')
    ax.set_title('Star Radius')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Idle fraction
    ax = axes[0, 2]
    ax.plot(ticks, [r['idle_fraction'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Fraction idle')
    ax.set_title('Idle Fraction (time dilation)')
    ax.grid(True, alpha=0.3)

    # 4. Internal vs boundary connector lengths
    ax = axes[1, 0]
    ax.plot(ticks, [r['int_conn_mean'] for r in rows], 'b-', linewidth=0.8, label='internal mean')
    ax.plot(ticks, [r['bnd_conn_mean'] for r in rows], 'g-', linewidth=0.8, label='boundary mean')
    ax.set_ylabel('Length')
    ax.set_title('Internal vs Boundary Connector Length')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. Internal connector max
    ax = axes[1, 1]
    ax.plot(ticks, [r['int_conn_max'] for r in rows], 'r-', linewidth=0.8)
    ax.set_ylabel('Length')
    ax.set_title('Internal Connector Max Length')
    ax.grid(True, alpha=0.3)

    # 6. Total hops over time
    ax = axes[1, 2]
    ax.plot(ticks, [r['total_hops'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Cumulative hops')
    ax.set_title('Total Hops (should slow down)')
    ax.grid(True, alpha=0.3)

    # 7. Total deposits
    ax = axes[2, 0]
    ax.plot(ticks, [r['total_deposits'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Deposits')
    ax.set_xlabel('Tick')
    ax.set_title('Total Deposits')
    ax.grid(True, alpha=0.3)

    # 8. Int/bnd ratio over time
    ax = axes[2, 1]
    ratios = [r['int_conn_mean'] / r['bnd_conn_mean']
              if r['bnd_conn_mean'] > 0 else 0 for r in rows]
    ax.plot(ticks, ratios, 'g-', linewidth=0.8)
    ax.axhline(1.5, color='r', linestyle='--', alpha=0.5, label='target>1.5')
    ax.set_ylabel('Ratio')
    ax.set_xlabel('Tick')
    ax.set_title('Internal/Boundary Length Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 9. Effective hop rate (hops per 1000 ticks)
    ax = axes[2, 2]
    hop_rates = []
    for i in range(1, len(rows)):
        dt = rows[i]['tick'] - rows[i-1]['tick']
        dh = rows[i]['total_hops'] - rows[i-1]['total_hops']
        hop_rates.append(dh / dt * 1000 if dt > 0 else 0)
    if hop_rates:
        ax.plot(ticks[1:], hop_rates, 'orange', linewidth=0.8)
    ax.set_ylabel('Hops per 1000 ticks')
    ax.set_xlabel('Tick')
    ax.set_title('Effective Hop Rate (should decrease)')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase1_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
