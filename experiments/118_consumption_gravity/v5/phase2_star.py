#!/usr/bin/env python3
"""
Experiment 118 v5 — Phase 2: Star Equilibrium

80 star nodes, 4 groups, fixed graph, deposit propagation.
Entity nodes emit 1 deposit/tick, route via weighted random walk
based on incoming propagating deposits. Hop after emission.

Success criteria:
  1. COM drift < 2.0
  2. Radius stability: CV < 0.15 over last 20k ticks
  3. Star doesn't expand 4x (v4 went 3.84 -> 14.5)
  4. Boundary flux stabilizes (quasi-steady luminosity)
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
from entity import Entity


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
    star_group_indices = [i % STAR_GROUPS for i in range(STAR_COUNT)]
    star_spectrum = set(range(STAR_GROUPS))  # {0, 1, 2, 3}

    max_r = np.linalg.norm(g.pos[star_node_ids[-1]])
    print(f"Star: {STAR_COUNT} nodes, {STAR_GROUPS} groups, "
          f"max initial r={max_r:.2f}")
    print(f"Star spectrum: {star_spectrum}")

    star = Entity("star", star_node_ids, star_group_indices, star_spectrum)

    # ── Build propagation engine ──
    engine = PropagationEngine(g, STAR_GROUPS, seed=SEED)
    engine.update_entity_nodes(set(star_node_ids))

    initial_com = star.com(g)
    print(f"Initial COM: [{initial_com[0]:.2f}, {initial_com[1]:.2f}, {initial_com[2]:.2f}]")
    print(f"Initial mean radius: {star.mean_radius(g):.2f}")

    # ── BFS distances from center for radial profile ──
    center = g.nearest_to_origin(1)[0]
    hop_dist = bfs_distances(g, center)

    # ── Run ──
    rows = []
    radial_snapshots = {}
    print(f"\n{'=' * 60}")
    print(f"PHASE 2: Star Equilibrium ({TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()

    for tick in range(1, TICKS + 1):
        engine.begin_tick()
        star.absorb(engine)        # absorb 1/node, modifies flows in-place
        engine.propagate()         # redistribute remaining deposits (ALL nodes)
        star.emit_and_hop(engine, g, rng)  # emit 1/node + hop
        engine.advance()           # swap buffers

        # Update entity mask after hops (star nodes moved)
        engine.update_entity_nodes(set(star.node_indices()))

        if tick % MEASURE_EVERY == 0:
            com = star.com(g)
            com_drift = float(np.linalg.norm(com - initial_com))
            mean_r = star.mean_radius(g)
            max_r = star.max_radius(g)
            discharge = star.discharge_rate()
            total_dep = engine.total_deposits()
            flux, n_bnd = star.boundary_flux(engine, g)
            expected_total = engine.total_emitted - engine.total_absorbed

            rows.append({
                'tick': tick,
                'com_x': com[0], 'com_y': com[1], 'com_z': com[2],
                'com_drift': com_drift,
                'mean_radius': mean_r,
                'max_radius': max_r,
                'discharge_rate': discharge,
                'total_deposits': total_dep,
                'expected_deposits': expected_total,
                'conservation_error': total_dep - expected_total,
                'boundary_flux': flux,
                'boundary_edges': n_bnd,
                'total_emitted': engine.total_emitted,
                'total_absorbed': engine.total_absorbed,
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            # Capture radial deposit profile
            radial = engine.deposits_at_radius(center, hop_dist)
            radial_snapshots[tick] = radial
            radial_str = " ".join(f"d{d}={radial.get(d,0)}" for d in range(10))
            print(f"  t={tick:6d}  COM_drift={r['com_drift']:.2f}  "
                  f"mean_r={r['mean_radius']:.2f}  max_r={r['max_radius']:.2f}  "
                  f"deposits={r['total_deposits']}  "
                  f"flux={r['boundary_flux']}  "
                  f"err={r['conservation_error']}  "
                  f"({tps:.0f} t/s)")
            print(f"         radial: {radial_str}")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    # ── Save CSV ──
    csv_path = os.path.join(OUT, "phase2_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    # ── Analysis ──
    analyze(rows)

    # ── Plots ──
    plot(rows, radial_snapshots)


def analyze(rows):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # Criterion 1: COM drift < 2.0
    max_drift = max(r['com_drift'] for r in rows)
    final_drift = rows[-1]['com_drift']
    status1 = "PASS" if max_drift < 2.0 else "FAIL"
    print(f"  1. COM stability:  final={final_drift:.3f}  "
          f"max={max_drift:.3f}  [{status1}]")

    # Criterion 2: radius stability (last 20k ticks)
    last_rows = [r for r in rows if r['tick'] > 30000]
    if last_rows:
        radii = [r['mean_radius'] for r in last_rows]
        mean_r = np.mean(radii)
        std_r = np.std(radii)
        cv = std_r / mean_r if mean_r > 0 else float('inf')
        status2 = "PASS" if cv < 0.15 else "FAIL"
        print(f"  2. Radius stability (last 20k): mean={mean_r:.2f}  "
              f"std={std_r:.3f}  CV={cv:.3f}  [{status2}]")
        # Compare to initial
        initial_r = rows[0]['mean_radius']
        expansion = mean_r / initial_r if initial_r > 0 else float('inf')
        print(f"     Expansion ratio: {expansion:.2f}x (v4 was 3.8x)")

    # Criterion 3: conservation
    max_err = max(abs(r['conservation_error']) for r in rows)
    status3 = "PASS" if max_err == 0 else "FAIL"
    print(f"  3. Conservation: max_error={max_err}  [{status3}]")

    # Criterion 4: boundary flux stabilizes
    if last_rows:
        fluxes = [r['boundary_flux'] for r in last_rows]
        mean_flux = np.mean(fluxes)
        std_flux = np.std(fluxes)
        cv_flux = std_flux / mean_flux if mean_flux > 0 else float('inf')
        status4 = "PASS" if cv_flux < 0.30 else "FAIL"
        print(f"  4. Boundary flux (last 20k): mean={mean_flux:.1f}  "
              f"std={std_flux:.1f}  CV={cv_flux:.3f}  [{status4}]")

    print()


def plot(rows, radial_snapshots):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v5 — Phase 2: Star Equilibrium (forward propagation)',
                 fontsize=14)

    # 1. COM drift
    ax = axes[0, 0]
    ax.plot(ticks, [r['com_drift'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(2.0, color='r', linestyle='--', alpha=0.5, label='threshold=2.0')
    ax.set_ylabel('COM drift')
    ax.set_title('COM Stability')
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

    # 3. Total deposits
    ax = axes[0, 2]
    ax.plot(ticks, [r['total_deposits'] for r in rows], 'b-', linewidth=0.8, label='actual')
    ax.plot(ticks, [r['expected_deposits'] for r in rows], 'r--', linewidth=0.8, alpha=0.5, label='expected')
    ax.set_ylabel('Deposit count')
    ax.set_title('Total Deposits (conservation)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Boundary flux
    ax = axes[1, 0]
    ax.plot(ticks, [r['boundary_flux'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Deposits/tick')
    ax.set_title('Boundary Flux (star luminosity)')
    ax.grid(True, alpha=0.3)

    # 5. Emitted vs absorbed
    ax = axes[1, 1]
    ax.plot(ticks, [r['total_emitted'] for r in rows], 'g-', linewidth=0.8, label='emitted')
    ax.plot(ticks, [r['total_absorbed'] for r in rows], 'r-', linewidth=0.8, label='absorbed')
    ax.set_ylabel('Cumulative count')
    ax.set_title('Emitted vs Absorbed')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 6. Conservation error
    ax = axes[1, 2]
    ax.plot(ticks, [r['conservation_error'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Error')
    ax.set_title('Conservation Error')
    ax.grid(True, alpha=0.3)

    # 7. Radial deposit profile (linear)
    ax = axes[2, 0]
    colors = plt.cm.viridis(np.linspace(0, 1, len(radial_snapshots)))
    for (tick_num, radial), color in zip(sorted(radial_snapshots.items()), colors):
        dists = sorted(radial.keys())
        counts = [radial[d] for d in dists]
        ax.plot(dists, counts, 'o-', color=color, markersize=3, label=f't={tick_num}')
    ax.set_xlabel('Hop distance from center')
    ax.set_ylabel('Deposit count')
    ax.set_title('Radial Deposit Profile')
    ax.legend(fontsize=7)
    ax.grid(True, alpha=0.3)

    # 8. Radial deposit profile (log-log) — check for 1/r^2
    ax = axes[2, 1]
    if radial_snapshots:
        last_tick = max(radial_snapshots.keys())
        radial = radial_snapshots[last_tick]
        dists = sorted(d for d in radial.keys() if d > 0 and radial[d] > 0)
        if dists:
            counts = [radial[d] for d in dists]
            ax.loglog(dists, counts, 'bo-', markersize=4, label=f't={last_tick}')
            ref_r = np.array(dists, dtype=float)
            ref_c = counts[0] * (ref_r[0] / ref_r) ** 2
            ax.loglog(ref_r, ref_c, 'r--', alpha=0.5, label='1/r^2 reference')
            ax.legend()
    ax.set_xlabel('Hop distance from center')
    ax.set_ylabel('Deposit count')
    ax.set_title('Radial Profile (log-log)')
    ax.grid(True, alpha=0.3)

    # 9. Absorption rate over time
    ax = axes[2, 2]
    # Compute per-interval absorption rate
    absorbed_vals = [r['total_absorbed'] for r in rows]
    absorb_rate = [absorbed_vals[0] / rows[0]['tick']]
    for i in range(1, len(rows)):
        dt = rows[i]['tick'] - rows[i-1]['tick']
        da = absorbed_vals[i] - absorbed_vals[i-1]
        absorb_rate.append(da / dt if dt > 0 else 0)
    ax.plot(ticks, absorb_rate, 'r-', linewidth=0.8)
    ax.axhline(80, color='g', linestyle='--', alpha=0.5, label='emission rate (80/tick)')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Deposits/tick')
    ax.set_title('Absorption Rate vs Emission Rate')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
