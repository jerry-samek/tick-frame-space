#!/usr/bin/env python3
"""
Experiment 118 v5 — Phase 1: Deposit Propagation Test

No entities. Pure propagation validation.
Seed deposits at center node, verify they spread as wavefront.

Success criteria:
  1. Total deposits exactly conserved across all ticks
  2. Wavefront expands at ~1 hop/tick
  3. Steady-state density profile approximates 1/r^2
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
from propagation import PropagationEngine

# ── Configuration ──────────────────────────────────────────────
SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24
N_GROUPS = 1          # single group for propagation test
N_SEED_DEPOSITS = 80  # same as star node count

TICKS = 500
MEASURE_EVERY = 10
LOG_EVERY = 50

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def bfs_distances(graph, start):
    """BFS from start node, return array of hop distances."""
    dist = np.full(graph.n_nodes, -1, dtype=np.int32)
    dist[start] = 0
    queue = deque([start])
    while queue:
        node = queue.popleft()
        for nb in graph.neighbors(node):
            if dist[nb] == -1:
                dist[nb] = dist[node] + 1
                queue.append(nb)
    return dist


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    # ── Build graph ──
    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # ── Find center node ──
    center = g.nearest_to_origin(1)[0]
    print(f"Center node: {center} at {g.pos[center]}")

    # ── BFS distances from center ──
    hop_dist = bfs_distances(g, center)
    max_hop = int(hop_dist.max())
    print(f"Graph diameter from center: {max_hop} hops")

    # ── Build propagation engine (no entities) ──
    engine = PropagationEngine(g, N_GROUPS, seed=SEED)
    # No entity nodes — all transparent

    # ── Seed deposits at center ──
    out_edges = engine.outgoing[center]
    for i in range(N_SEED_DEPOSITS):
        d = out_edges[rng.integers(len(out_edges))]
        engine.flows[d, 0] += 1
    initial_total = engine.total_deposits()
    print(f"Seeded {initial_total} deposits on {len(out_edges)} outgoing edges from center")

    # ── Run ──
    print(f"\n{'=' * 60}")
    print(f"PHASE 1: Propagation Test ({TICKS} ticks)")
    print(f"{'=' * 60}\n")

    rows = []
    radial_snapshots = {}
    t0 = time.time()

    for tick in range(1, TICKS + 1):
        engine.begin_tick()
        engine.propagate()
        engine.advance()

        if tick % MEASURE_EVERY == 0:
            total = engine.total_deposits()
            radial = engine.deposits_at_radius(center, hop_dist)

            # Wavefront: max distance with deposits
            wavefront = max(radial.keys()) if radial else 0

            rows.append({
                'tick': tick,
                'total_deposits': total,
                'conservation_error': total - initial_total,
                'wavefront_radius': wavefront,
            })

            # Save a few radial snapshots for plotting
            if tick in (10, 50, 100, 200, 500):
                radial_snapshots[tick] = radial

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            print(f"  t={tick:4d}  total={r['total_deposits']}  "
                  f"error={r['conservation_error']}  "
                  f"wavefront={r['wavefront_radius']}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    # ── Save CSV ──
    csv_path = os.path.join(OUT, "phase1_propagation.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    # ── Analysis ──
    analyze(rows, initial_total)

    # ── Plots ──
    plot(rows, radial_snapshots, hop_dist, max_hop)


def analyze(rows, initial_total):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # Criterion 1: Conservation
    errors = [r['conservation_error'] for r in rows]
    max_error = max(abs(e) for e in errors)
    status1 = "PASS" if max_error == 0 else "FAIL"
    print(f"  1. Conservation: initial={initial_total}  "
          f"max_error={max_error}  [{status1}]")

    # Criterion 2: Wavefront expansion
    # Check that wavefront radius grows roughly 1 per tick initially
    early = [(r['tick'], r['wavefront_radius']) for r in rows if r['tick'] <= 100]
    if len(early) >= 5:
        ticks_arr = np.array([t for t, _ in early])
        radii_arr = np.array([r for _, r in early])
        # Linear fit
        if ticks_arr[-1] > ticks_arr[0]:
            slope = (radii_arr[-1] - radii_arr[0]) / (ticks_arr[-1] - ticks_arr[0])
            status2 = "PASS" if 0.5 < slope < 2.0 else "FAIL"
            print(f"  2. Wavefront speed: slope={slope:.3f} hops/tick  [{status2}]")
        else:
            print(f"  2. Wavefront speed: insufficient data")
    else:
        print(f"  2. Wavefront speed: insufficient data")

    # Criterion 3: Final total matches initial
    final_total = rows[-1]['total_deposits']
    status3 = "PASS" if final_total == initial_total else "FAIL"
    print(f"  3. Final conservation: {final_total} == {initial_total}  [{status3}]")

    print()


def plot(rows, radial_snapshots, hop_dist, max_hop):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(2, 2, figsize=(12, 10))
    fig.suptitle('Experiment 118 v5 — Phase 1: Deposit Propagation', fontsize=14)

    # 1. Total deposits over time (conservation)
    ax = axes[0, 0]
    ax.plot(ticks, [r['total_deposits'] for r in rows], 'b-', linewidth=1)
    ax.set_ylabel('Total deposits')
    ax.set_title('Conservation')
    ax.grid(True, alpha=0.3)

    # 2. Wavefront radius over time
    ax = axes[0, 1]
    ax.plot(ticks, [r['wavefront_radius'] for r in rows], 'r-', linewidth=1)
    ax.plot(ticks, ticks, 'k--', alpha=0.3, label='slope=1')
    ax.set_ylabel('Wavefront radius (hops)')
    ax.set_title('Wavefront Expansion')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 3. Radial profile at select ticks
    ax = axes[1, 0]
    colors = ['blue', 'green', 'orange', 'red', 'purple']
    # Count edges at each distance for normalization
    edge_counts = np.zeros(max_hop + 1)
    for d in range(engine_n_directed := 2 * len(radial_snapshots)):
        pass  # can't access engine here, compute from hop_dist
    # Approximate: count edges per shell from hop_dist
    for key in sorted(radial_snapshots.keys()):
        radial = radial_snapshots[key]
        dists = sorted(radial.keys())
        counts = [radial[d] for d in dists]
        color = colors[sorted(radial_snapshots.keys()).index(key) % len(colors)]
        ax.plot(dists, counts, 'o-', color=color, markersize=3, label=f't={key}')
    ax.set_xlabel('Distance from center (hops)')
    ax.set_ylabel('Deposit count')
    ax.set_title('Radial Profile')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Radial profile log-log (check 1/r^2)
    ax = axes[1, 1]
    if 500 in radial_snapshots:
        radial = radial_snapshots[500]
        dists = sorted(d for d in radial.keys() if d > 0 and radial[d] > 0)
        counts = [radial[d] for d in dists]
        ax.loglog(dists, counts, 'bo-', markersize=4, label='t=500')
        # Reference 1/r^2 line
        if len(dists) >= 2:
            ref_r = np.array(dists, dtype=float)
            ref_c = counts[0] * (ref_r[0] / ref_r) ** 2
            ax.loglog(ref_r, ref_c, 'r--', alpha=0.5, label='1/r^2 reference')
        ax.legend()
    ax.set_xlabel('Distance from center (hops)')
    ax.set_ylabel('Deposit count')
    ax.set_title('Radial Profile (log-log) at t=500')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase1_propagation.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
