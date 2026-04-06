#!/usr/bin/env python3
"""
Experiment 128 v6 — Deposit Dominance Tracking

Same physics as v5 (vectorized, 500k graph, 10k star, 500 planet).
NEW: tracks deposit dominance REGIONS instead of just entity node positions.

The entity IS where its deposits dominate. The star region, planet region,
and boundary emerge from the deposit field — independent of node positions.
"""

import os
import sys
import time
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from substrate import Substrate
from entities import EntityBatch
from dominance import dominance_map, dominance_by_distance, dominance_com, dominance_radius

SEED = 42
N_NODES = 500000
SPHERE_R = 80.0
TARGET_K = 24
STAR_COUNT = 10000
STAR_GROUPS = 4
PLANET_COUNT = 500
PLANET_GROUPS = 2

TICKS = 500000
MEASURE_EVERY = 5000
LOG_EVERY = 10000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def place_cluster(substrate, center_pos, target_dist, n_nodes):
    dists = np.linalg.norm(substrate.pos - center_pos, axis=1)
    seed_idx = np.argmin(np.abs(dists - target_dist))
    seed_pos = substrate.pos[seed_idx]
    neighbor_dists = np.linalg.norm(substrate.pos - seed_pos, axis=1)
    neighbor_dists[seed_idx] = np.inf
    nearest = np.argsort(neighbor_dists)[:n_nodes - 1]
    return np.concatenate([[seed_idx], nearest])


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print(f"Building substrate: N={N_NODES}, R={SPHERE_R}...")
    sys.stdout.flush()
    sub = Substrate(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)")
    sys.stdout.flush()

    star_ids = sub.nearest_to_origin(STAR_COUNT)
    star = EntityBatch("star", star_ids, STAR_GROUPS, 0, True, sub)
    star_com_init = star.com()

    planet_ids = place_cluster(sub, star_com_init, 40.0, PLANET_COUNT)
    planet = EntityBatch("planet", planet_ids, PLANET_GROUPS, STAR_GROUPS, False, sub)
    p_com_init = planet.com()
    initial_dist = float(np.linalg.norm(p_com_init - star_com_init))

    center_node = int(sub.nearest_to_origin(1)[0])

    print(f"Star: {STAR_COUNT} nodes, r={star.mean_radius():.2f}")
    print(f"Planet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}, r={planet.mean_radius():.2f}")
    print(f"Tracking deposit dominance regions.")
    sys.stdout.flush()

    rows = []
    prev_tick = 0
    prev_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"RUN ({TICKS} ticks)")
    print(f"{'=' * 60}\n")
    sys.stdout.flush()

    t0 = time.time()
    for tick in range(1, TICKS + 1):
        star.tick_transit(tick)
        planet.tick_transit(tick)
        star.tick_charging()
        planet.tick_charging()
        star.tick_routing(rng)
        planet.tick_routing(rng)

        if tick % MEASURE_EVERY == 0:
            # Node-based measurements
            s_com_nodes = star.com()
            p_com_nodes = planet.com()
            node_dist = float(np.linalg.norm(p_com_nodes - s_com_nodes))

            # Deposit dominance measurements
            s_com_dep, p_com_dep = dominance_com(sub)
            dep_dist = float(np.linalg.norm(p_com_dep - s_com_dep))
            s_dep_r = dominance_radius(sub, s_com_dep, is_star=True)
            p_dep_r = dominance_radius(sub, p_com_dep, is_star=False)
            dmap = dominance_map(sub)

            total_deps, total_diff, total_consumed = sub.stats()

            rows.append({
                'tick': tick,
                # Node-based
                'node_dist': node_dist,
                'star_node_r': star.mean_radius(),
                'planet_node_r': planet.mean_radius(),
                # Deposit-based
                'deposit_dist': dep_dist,
                'star_deposit_r': s_dep_r,
                'planet_deposit_r': p_dep_r,
                'star_dominant_edges': dmap['star_dominant'],
                'planet_dominant_edges': dmap['planet_dominant'],
                'empty_edges': dmap['empty'],
                # Consumption
                'total_different': total_diff,
                'total_consumed': total_consumed,
                # Hops
                'planet_hops': planet.total_hops(),
                # COM positions
                'dep_star_x': float(s_com_dep[0]), 'dep_star_y': float(s_com_dep[1]),
                'dep_planet_x': float(p_com_dep[0]), 'dep_planet_y': float(p_com_dep[1]),
            })

        if tick % LOG_EVERY == 0:
            now = time.time()
            recent_tps = (tick - prev_tick) / max(0.001, now - prev_time)
            prev_tick = tick
            prev_time = now
            remaining = (TICKS - tick) / max(1, recent_tps) / 60
            r = rows[-1]
            print(f"  t={tick:7d}  "
                  f"node_d={r['node_dist']:.1f}  dep_d={r['deposit_dist']:.1f}  "
                  f"star_r={r['star_deposit_r']:.1f}  planet_r={r['planet_deposit_r']:.1f}  "
                  f"S_edges={r['star_dominant_edges']}  P_edges={r['planet_dominant_edges']}  "
                  f"D/C={r['total_different']}/{r['total_consumed']}  "
                  f"({recent_tps:.0f} t/s, ETA {remaining:.0f}min)")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    # Dominance profile at end
    print("\nFinal dominance by distance:")
    dbd = dominance_by_distance(sub, center_node)
    for d in sorted(dbd.keys())[:20]:
        dd = dbd[d]
        print(f"  d={d:2d}: star={dd['star_frac']:.3f}  "
              f"planet={dd['planet_frac']:.3f}  "
              f"empty={dd['empty_frac']:.3f}  edges={dd['n_edges']}")

    analyze(rows, initial_dist)
    plot(rows, initial_dist)


def analyze(rows, initial_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    last = [r for r in rows if r['tick'] > TICKS * 0.5]

    if last:
        print("  Node-based (entity node positions):")
        print(f"    Star r: {np.mean([r['star_node_r'] for r in last]):.2f}")
        print(f"    Planet r: {np.mean([r['planet_node_r'] for r in last]):.2f}")
        print(f"    Distance: {np.mean([r['node_dist'] for r in last]):.2f}")
        print()
        print("  Deposit-based (dominance regions):")
        print(f"    Star region r: {np.mean([r['star_deposit_r'] for r in last]):.2f}")
        print(f"    Planet region r: {np.mean([r['planet_deposit_r'] for r in last]):.2f}")
        print(f"    Region distance: {np.mean([r['deposit_dist'] for r in last]):.2f}")
        print(f"    Star edges: {np.mean([r['star_dominant_edges'] for r in last]):.0f}")
        print(f"    Planet edges: {np.mean([r['planet_dominant_edges'] for r in last]):.0f}")

    # Tangential from deposit COMs
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['dep_planet_x'], rows[i-1]['dep_planet_y']])
        p1 = np.array([rows[i]['dep_planet_x'], rows[i]['dep_planet_y']])
        s = np.array([rows[i]['dep_star_x'], rows[i]['dep_star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.degrees(np.arctan2(cross, dot)))

    print(f"\n  Deposit-based tangential: net={sum(angles):.1f}  "
          f"total={sum(abs(a) for a in angles):.1f}")

    if len(angles) > 20:
        cs = len(angles) // 10
        coh = [abs(np.mean(np.sign(angles[c*cs:(c+1)*cs]))) for c in range(10)]
        print(f"  Deposit-based coherence: {np.mean(coh):.3f}")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle('Experiment 128 v6: Deposit Dominance Tracking', fontsize=14)

    # 1. Distance: nodes vs deposits
    ax = axes[0, 0]
    ax.plot(ticks, [r['node_dist'] for r in rows], 'b-', linewidth=0.5, alpha=0.5, label='node COM')
    ax.plot(ticks, [r['deposit_dist'] for r in rows], 'r-', linewidth=0.8, label='deposit region')
    ax.axhline(initial_dist, color='k', linestyle='--', alpha=0.3)
    ax.set_ylabel('Distance'); ax.set_title('Node vs Deposit Distance')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 2. Deposit region trajectory (XY)
    ax = axes[0, 1]
    px = [r['dep_planet_x'] for r in rows]; py = [r['dep_planet_y'] for r in rows]
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', ms=8, label='start')
    ax.plot(px[-1], py[-1], 'ro', ms=8, label='end')
    ax.plot(np.mean([r['dep_star_x'] for r in rows]),
            np.mean([r['dep_star_y'] for r in rows]), 'y*', ms=12, label='star')
    ax.set_aspect('equal'); ax.set_title('Deposit Region Trajectory')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 3. Radii: node vs deposit
    ax = axes[0, 2]
    ax.plot(ticks, [r['star_node_r'] for r in rows], 'orange', linewidth=0.5, alpha=0.5, label='star nodes')
    ax.plot(ticks, [r['star_deposit_r'] for r in rows], 'red', linewidth=0.8, label='star deposits')
    ax.plot(ticks, [r['planet_deposit_r'] for r in rows], 'blue', linewidth=0.8, label='planet deposits')
    ax.set_ylabel('Radius'); ax.set_title('Region Radii')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 4. Dominance edge counts
    ax = axes[1, 0]
    ax.plot(ticks, [r['star_dominant_edges'] for r in rows], 'orange', linewidth=0.8, label='Star')
    ax.plot(ticks, [r['planet_dominant_edges'] for r in rows], 'blue', linewidth=0.8, label='Planet')
    ax.plot(ticks, [r['empty_edges'] for r in rows], 'gray', linewidth=0.5, label='Empty')
    ax.set_ylabel('Edge count'); ax.set_title('Dominance Territory')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 5. Different / Consumed
    ax = axes[1, 1]
    ax.plot(ticks, [r['total_different'] for r in rows], 'r-', linewidth=0.5, label='Different')
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'b--', linewidth=0.5, label='Consumed')
    ax.set_ylabel('Count'); ax.set_title('Consumption Dynamics')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 6. Angular position from deposit COMs
    ax = axes[1, 2]
    angles = []
    for i in range(1, n):
        p0 = np.array([rows[i-1]['dep_planet_x'], rows[i-1]['dep_planet_y']])
        p1 = np.array([rows[i]['dep_planet_x'], rows[i]['dep_planet_y']])
        s = np.array([rows[i]['dep_star_x'], rows[i]['dep_star_y']])
        v0, v1 = p0 - s, p1 - s
        angles.append(np.degrees(np.arctan2(v0[0]*v1[1]-v0[1]*v1[0], v0[0]*v1[0]+v0[1]*v1[1])))
    ax.plot(ticks[1:], np.cumsum(angles), 'g-', linewidth=0.8)
    ax.set_ylabel('Degrees'); ax.set_title('Deposit Angular Position')
    ax.grid(True, alpha=0.3)

    # 7. Star deposit region radius vs star node radius
    ax = axes[2, 0]
    ax.scatter([r['star_node_r'] for r in rows],
               [r['star_deposit_r'] for r in rows], s=3, alpha=0.3)
    ax.set_xlabel('Star node radius'); ax.set_ylabel('Star deposit radius')
    ax.set_title('Node vs Deposit Radius (star)'); ax.grid(True, alpha=0.3)

    # 8. Planet hops
    ax = axes[2, 1]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Hops'); ax.grid(True, alpha=0.3)

    # 9. Territory ratio over time
    ax = axes[2, 2]
    s_edges = [r['star_dominant_edges'] for r in rows]
    p_edges = [r['planet_dominant_edges'] for r in rows]
    ratio = [s/(s+p) if (s+p) > 0 else 0.5 for s, p in zip(s_edges, p_edges)]
    ax.plot(ticks, ratio, 'purple', linewidth=0.8)
    ax.axhline(0.5, color='k', linestyle='--', alpha=0.3)
    ax.set_ylabel('Star fraction'); ax.set_xlabel('Tick')
    ax.set_title('Territory Balance (star / total)'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"Saved: results.png")


if __name__ == '__main__':
    run()
