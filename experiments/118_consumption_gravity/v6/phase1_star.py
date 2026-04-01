#!/usr/bin/env python3
"""
Experiment 118 v6 — Phase 1: Star Equilibrium

v4's ontology (connector = deposits) + accumulated-density routing.
80 star nodes, 4 groups, BASE_WEIGHT=1.0 thermal motion.

Success criteria:
  1. Star compact: mean radius < 8 (< 2x initial ~3.84)
  2. COM stable: drift < 3.0
  3. Gradient exists: density at d=0 > density at d=4 by 5:1
  4. Routing directional: mean signal ratio > 3:1
  5. No runaway: max connector length < 1000 at 50k ticks
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

TICKS = 50000
MEASURE_EVERY = 500
LOG_EVERY = 5000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def bfs_distances(graph, start):
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


def density_profile(graph, star_spectrum, center, hop_dist):
    """Mean matching_density of connectors at each hop distance from center."""
    by_dist = {}  # {dist: [densities]}
    seen = set()
    for (i, j), c in graph.connectors.items():
        key = (i, j)
        if key in seen:
            continue
        seen.add(key)
        d_i = hop_dist[i]
        d_j = hop_dist[j]
        d = min(d_i, d_j)  # assign to closer shell
        if d < 0:
            continue
        dens = c.matching_density(star_spectrum)
        by_dist.setdefault(d, []).append(dens)

    result = {}
    for d in sorted(by_dist.keys()):
        vals = by_dist[d]
        result[d] = float(np.mean(vals))
    return result


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # Place star near origin
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}

    max_r = np.linalg.norm(g.pos[star_node_ids[-1]])
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={max_r:.2f}")

    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    # BFS from center for radial profile
    center = g.nearest_to_origin(1)[0]
    hop_dist = bfs_distances(g, center)

    initial_com = star.com(g)
    print(f"Initial COM: [{initial_com[0]:.2f}, {initial_com[1]:.2f}, {initial_com[2]:.2f}]")
    print(f"Initial mean radius: {star.mean_radius(g):.2f}")

    rows = []
    radial_snapshots = {}

    print(f"\n{'=' * 60}")
    print(f"PHASE 1: Star Equilibrium ({TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()

    for tick in range(1, TICKS + 1):
        star.tick(g, rng)

        if tick % MEASURE_EVERY == 0:
            com = star.com(g)
            com_drift = float(np.linalg.norm(com - initial_com))
            mean_r = star.mean_radius(g)
            max_r_val = star.max_radius(g)
            int_mean, int_max, int_count = star.internal_connector_stats(g)
            bnd_mean, bnd_max, bnd_count = star.boundary_connector_stats(g)
            routing_ratio = star.mean_routing_ratio(g)
            total_deps = sum(c.total for c in g.connectors.values())

            rows.append({
                'tick': tick,
                'com_drift': com_drift,
                'mean_radius': mean_r,
                'max_radius': max_r_val,
                'int_conn_mean': int_mean,
                'int_conn_max': int_max,
                'int_conn_count': int_count,
                'bnd_conn_mean': bnd_mean,
                'bnd_conn_max': bnd_max,
                'bnd_conn_count': bnd_count,
                'routing_ratio': routing_ratio,
                'total_deposits': total_deps,
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]

            # Radial density profile
            prof = density_profile(g, star_spectrum, center, hop_dist)
            radial_snapshots[tick] = prof
            prof_str = " ".join(f"d{d}={prof.get(d,0):.4f}" for d in range(10))

            print(f"  t={tick:6d}  COM={r['com_drift']:.2f}  "
                  f"mean_r={r['mean_radius']:.2f}  max_r={r['max_radius']:.2f}  "
                  f"ratio={r['routing_ratio']:.1f}  "
                  f"int={r['int_conn_mean']:.0f}/{r['int_conn_max']:.0f}  "
                  f"({tps:.0f} t/s)")
            print(f"         density: {prof_str}")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    # Save CSV
    csv_path = os.path.join(OUT, "phase1_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    analyze(rows)
    plot(rows, radial_snapshots)


def analyze(rows):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # 1. Star compact: mean radius < 8
    last_rows = [r for r in rows if r['tick'] > 30000]
    if last_rows:
        mean_r = np.mean([r['mean_radius'] for r in last_rows])
        status1 = "PASS" if mean_r < 8.0 else "FAIL"
        print(f"  1. Star compact: mean_r={mean_r:.2f}  [target <8.0]  [{status1}]")

    # 2. COM stable: drift < 3.0
    max_drift = max(r['com_drift'] for r in rows)
    status2 = "PASS" if max_drift < 3.0 else "FAIL"
    print(f"  2. COM stability: max_drift={max_drift:.2f}  [target <3.0]  [{status2}]")

    # 3. Routing directional: ratio > 3:1
    if last_rows:
        mean_ratio = np.mean([r['routing_ratio'] for r in last_rows])
        status4 = "PASS" if mean_ratio > 3.0 else "FAIL"
        print(f"  3. Routing ratio: mean={mean_ratio:.1f}  [target >3:1]  [{status4}]")

    # 4. No runaway
    max_conn = max(r['int_conn_max'] for r in rows)
    status5 = "PASS" if max_conn < 1000 else "FAIL"
    print(f"  4. Max connector: {max_conn:.0f}  [target <1000]  [{status5}]")

    # 5. Total deposits = 80 * tick
    expected = 80 * rows[-1]['tick']
    actual = rows[-1]['total_deposits']
    status6 = "PASS" if actual == expected else "FAIL"
    print(f"  5. Conservation: {actual} == {expected}  [{status6}]")

    print()


def plot(rows, radial_snapshots):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v6 — Phase 1: Star Equilibrium '
                 '(accumulated-density routing)', fontsize=14)

    # 1. COM drift
    ax = axes[0, 0]
    ax.plot(ticks, [r['com_drift'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(3.0, color='r', linestyle='--', alpha=0.5, label='threshold=3.0')
    ax.set_ylabel('COM drift')
    ax.set_title('COM Stability')
    ax.legend()
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

    # 3. Routing ratio
    ax = axes[0, 2]
    ax.plot(ticks, [r['routing_ratio'] for r in rows], 'purple', linewidth=0.8)
    ax.axhline(3.0, color='g', linestyle='--', alpha=0.5, label='target>3:1')
    ax.set_ylabel('Max/min ratio')
    ax.set_title('Routing Signal Ratio')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Internal connector lengths
    ax = axes[1, 0]
    ax.plot(ticks, [r['int_conn_mean'] for r in rows], 'b-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['int_conn_max'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.set_ylabel('Length')
    ax.set_title('Internal Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. Boundary connector lengths
    ax = axes[1, 1]
    ax.plot(ticks, [r['bnd_conn_mean'] for r in rows], 'g-', linewidth=0.8, label='mean')
    ax.plot(ticks, [r['bnd_conn_max'] for r in rows], 'r-', linewidth=0.8, alpha=0.5, label='max')
    ax.set_ylabel('Length')
    ax.set_title('Boundary Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 6. Total deposits
    ax = axes[1, 2]
    ax.plot(ticks, [r['total_deposits'] for r in rows], 'b-', linewidth=0.8)
    expected_line = [80 * r['tick'] for r in rows]
    ax.plot(ticks, expected_line, 'r--', alpha=0.5, label='expected (80×t)')
    ax.set_ylabel('Deposits')
    ax.set_title('Total Deposits')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 7. Radial density profile (linear)
    ax = axes[2, 0]
    colors = plt.cm.viridis(np.linspace(0, 1, len(radial_snapshots)))
    for (tick_num, prof), color in zip(sorted(radial_snapshots.items()), colors):
        dists = sorted(prof.keys())
        vals = [prof[d] for d in dists]
        ax.plot(dists, vals, 'o-', color=color, markersize=3, label=f't={tick_num}')
    ax.set_xlabel('Hop distance from center')
    ax.set_ylabel('Mean matching density')
    ax.set_title('Radial Density Profile')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 8. Radial density log-log
    ax = axes[2, 1]
    if radial_snapshots:
        last_tick = max(radial_snapshots.keys())
        prof = radial_snapshots[last_tick]
        dists = sorted(d for d in prof.keys() if d > 0 and prof[d] > 0)
        if dists:
            vals = [prof[d] for d in dists]
            ax.loglog(dists, vals, 'bo-', markersize=4, label=f't={last_tick}')
            ref_r = np.array(dists, dtype=float)
            ref_v = vals[0] * (ref_r[0] / ref_r) ** 2
            ax.loglog(ref_r, ref_v, 'r--', alpha=0.5, label='1/r^2 ref')
            ax.legend()
    ax.set_xlabel('Hop distance')
    ax.set_ylabel('Mean matching density')
    ax.set_title('Density Profile (log-log)')
    ax.grid(True, alpha=0.3)

    # 9. Density ratio d0/d4 over time
    ax = axes[2, 2]
    gradient_ticks = []
    gradient_ratios = []
    for tick_num in sorted(radial_snapshots.keys()):
        prof = radial_snapshots[tick_num]
        d0 = prof.get(0, 0) + prof.get(1, 0)  # near-center
        d4 = prof.get(4, 0) + prof.get(5, 0)  # mid-range
        if d4 > 0:
            gradient_ticks.append(tick_num)
            gradient_ratios.append(d0 / d4)
    if gradient_ticks:
        ax.plot(gradient_ticks, gradient_ratios, 'go-', markersize=4)
        ax.axhline(5.0, color='r', linestyle='--', alpha=0.5, label='target 5:1')
        ax.legend()
    ax.set_xlabel('Tick')
    ax.set_ylabel('Density ratio (near/far)')
    ax.set_title('Gradient Strength Over Time')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase1_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
