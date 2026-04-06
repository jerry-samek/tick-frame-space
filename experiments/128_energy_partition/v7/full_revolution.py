#!/usr/bin/env python3
"""
Experiment 128 v7 — Tangential Reject Stream

Planet routes with tangential bias from its reject stream direction.
Star: pure gravity + forward (no tangential).
Planet: gravity + forward + tangential (perpendicular to gravity).

Test: does the tangential component produce angular motion in the
deposit dominance regions?
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
from dominance import dominance_map, dominance_com, dominance_radius

SEED = 42
N_NODES = 500000
SPHERE_R = 80.0
TARGET_K = 24
STAR_COUNT = 10000
STAR_GROUPS = 4
PLANET_COUNT = 500
PLANET_GROUPS = 2
TANGENTIAL_STRENGTH = 0.5  # planet reject stream tangential bias

TICKS = 7000000  # ~one full revolution at observed rate
MEASURE_EVERY = 10000
LOG_EVERY = 100000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def place_cluster(substrate, center_pos, target_dist, n_nodes):
    dists = np.linalg.norm(substrate.pos - center_pos, axis=1)
    seed_idx = np.argmin(np.abs(dists - target_dist))
    seed_pos = substrate.pos[seed_idx]
    nd = np.linalg.norm(substrate.pos - seed_pos, axis=1)
    nd[seed_idx] = np.inf
    nearest = np.argsort(nd)[:n_nodes - 1]
    return np.concatenate([[seed_idx], nearest])


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print(f"Building substrate: N={N_NODES}, R={SPHERE_R}...")
    sys.stdout.flush()
    sub = Substrate(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)")

    star_ids = sub.nearest_to_origin(STAR_COUNT)
    star = EntityBatch("star", star_ids, STAR_GROUPS, 0, True, sub,
                       tangential_strength=0.0)
    star_com = star.com()

    planet_ids = place_cluster(sub, star_com, 40.0, PLANET_COUNT)
    planet = EntityBatch("planet", planet_ids, PLANET_GROUPS, STAR_GROUPS, False, sub,
                         tangential_strength=TANGENTIAL_STRENGTH)

    p_com = planet.com()
    initial_dist = float(np.linalg.norm(p_com - star_com))

    print(f"Star: {STAR_COUNT} nodes, r={star.mean_radius():.2f}")
    print(f"Planet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}, "
          f"tangential={TANGENTIAL_STRENGTH}")
    sys.stdout.flush()

    rows = []
    prev_tick = 0
    prev_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"RUN ({TICKS} ticks, tangential_strength={TANGENTIAL_STRENGTH})")
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
            s_com_n = star.com()
            p_com_n = planet.com()
            node_dist = float(np.linalg.norm(p_com_n - s_com_n))

            s_com_d, p_com_d = dominance_com(sub)
            dep_dist = float(np.linalg.norm(p_com_d - s_com_d))
            s_dep_r = dominance_radius(sub, s_com_d, True)
            p_dep_r = dominance_radius(sub, p_com_d, False)
            dmap = dominance_map(sub)
            total_deps, total_diff, total_consumed = sub.stats()

            rows.append({
                'tick': tick,
                'node_dist': node_dist,
                'deposit_dist': dep_dist,
                'star_deposit_r': s_dep_r,
                'planet_deposit_r': p_dep_r,
                'star_dominant_edges': dmap['star_dominant'],
                'planet_dominant_edges': dmap['planet_dominant'],
                'total_different': total_diff,
                'total_consumed': total_consumed,
                'planet_hops': planet.total_hops(),
                'dep_star_x': float(s_com_d[0]), 'dep_star_y': float(s_com_d[1]),
                'dep_planet_x': float(p_com_d[0]), 'dep_planet_y': float(p_com_d[1]),
                'node_planet_x': float(p_com_n[0]), 'node_planet_y': float(p_com_n[1]),
            })

        if tick % LOG_EVERY == 0:
            now = time.time()
            recent_tps = (tick - prev_tick) / max(0.001, now - prev_time)
            prev_tick = tick
            prev_time = now
            remaining = (TICKS - tick) / max(1, recent_tps) / 60
            r = rows[-1]

            # Angular increment from deposit COMs
            if len(rows) >= 2:
                p0 = np.array([rows[-2]['dep_planet_x'], rows[-2]['dep_planet_y']])
                p1 = np.array([rows[-1]['dep_planet_x'], rows[-1]['dep_planet_y']])
                s = np.array([rows[-1]['dep_star_x'], rows[-1]['dep_star_y']])
                v0, v1 = p0 - s, p1 - s
                ang = np.degrees(np.arctan2(v0[0]*v1[1]-v0[1]*v1[0],
                                            v0[0]*v1[0]+v0[1]*v1[1]))
            else:
                ang = 0

            print(f"  t={tick:7d}  n_d={r['node_dist']:.1f}  dep_d={r['deposit_dist']:.1f}  "
                  f"s_r={r['star_deposit_r']:.1f}  p_r={r['planet_deposit_r']:.1f}  "
                  f"ang={ang:+.2f}  "
                  f"D/C={r['total_different']}/{r['total_consumed']}  "
                  f"({recent_tps:.0f} t/s, ETA {remaining:.0f}min)")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "full_rev_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    analyze(rows, initial_dist)
    plot(rows, initial_dist)


def analyze(rows, initial_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    last = [r for r in rows if r['tick'] > TICKS * 0.5]

    if last:
        print(f"  Deposit distance (late): {np.mean([r['deposit_dist'] for r in last]):.2f}")
        print(f"  Star deposit r (late): {np.mean([r['star_deposit_r'] for r in last]):.2f}")
        print(f"  Planet deposit r (late): {np.mean([r['planet_deposit_r'] for r in last]):.2f}")

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

    total_net = sum(angles)
    total_abs = sum(abs(a) for a in angles)
    print(f"\n  Deposit tangential: net={total_net:.1f}  total={total_abs:.1f}  "
          f"rev={total_net/360:.2f}")

    if len(angles) > 20:
        cs = len(angles) // 10
        coh = [abs(np.mean(np.sign(angles[c*cs:(c+1)*cs]))) for c in range(10)]
        print(f"  Deposit coherence: {np.mean(coh):.3f}")

    # Node tangential for comparison
    angles_n = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['node_planet_x'], rows[i-1]['node_planet_y']])
        p1 = np.array([rows[i]['node_planet_x'], rows[i]['node_planet_y']])
        s = np.array([rows[i]['dep_star_x'], rows[i]['dep_star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles_n.append(np.degrees(np.arctan2(cross, dot)))

    print(f"  Node tangential: net={sum(angles_n):.1f}  total={sum(abs(a) for a in angles_n):.1f}")
    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle(f'Experiment 128 v7: Tangential Reject Stream '
                 f'(strength={TANGENTIAL_STRENGTH})', fontsize=14)

    # 1. Distances
    ax = axes[0, 0]
    ax.plot(ticks, [r['node_dist'] for r in rows], 'b-', lw=0.5, alpha=0.5, label='nodes')
    ax.plot(ticks, [r['deposit_dist'] for r in rows], 'r-', lw=0.8, label='deposits')
    ax.set_ylabel('Distance'); ax.set_title('Node vs Deposit Distance')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 2. Deposit region trajectory
    ax = axes[0, 1]
    px = [r['dep_planet_x'] for r in rows]; py = [r['dep_planet_y'] for r in rows]
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], lw=0.8)
    ax.plot(px[0], py[0], 'go', ms=8, label='start')
    ax.plot(px[-1], py[-1], 'ro', ms=8, label='end')
    ax.plot(np.mean([r['dep_star_x'] for r in rows]),
            np.mean([r['dep_star_y'] for r in rows]), 'y*', ms=12, label='star')
    ax.set_aspect('equal'); ax.set_title('Deposit Region Trajectory')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 3. Deposit angular position
    ax = axes[0, 2]
    angles = []
    for i in range(1, n):
        p0 = np.array([rows[i-1]['dep_planet_x'], rows[i-1]['dep_planet_y']])
        p1 = np.array([rows[i]['dep_planet_x'], rows[i]['dep_planet_y']])
        s = np.array([rows[i]['dep_star_x'], rows[i]['dep_star_y']])
        v0, v1 = p0 - s, p1 - s
        angles.append(np.degrees(np.arctan2(v0[0]*v1[1]-v0[1]*v1[0],
                                            v0[0]*v1[0]+v0[1]*v1[1])))
    ax.plot(ticks[1:], np.cumsum(angles), 'g-', lw=0.8)
    ax.set_ylabel('Degrees'); ax.set_title('Deposit Angular Position')
    ax.grid(True, alpha=0.3)

    # 4. Region radii
    ax = axes[1, 0]
    ax.plot(ticks, [r['star_deposit_r'] for r in rows], 'orange', lw=0.8, label='star')
    ax.plot(ticks, [r['planet_deposit_r'] for r in rows], 'blue', lw=0.8, label='planet')
    ax.set_ylabel('Radius'); ax.set_title('Deposit Region Radii')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 5. Territory
    ax = axes[1, 1]
    ax.plot(ticks, [r['star_dominant_edges'] for r in rows], 'orange', lw=0.8, label='Star')
    ax.plot(ticks, [r['planet_dominant_edges'] for r in rows], 'blue', lw=0.8, label='Planet')
    ax.set_ylabel('Edges'); ax.set_title('Territory')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 6. Consumption
    ax = axes[1, 2]
    ax.plot(ticks, [r['total_different'] for r in rows], 'r-', lw=0.5, label='Diff')
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'b--', lw=0.5, label='Consumed')
    ax.set_ylabel('Count'); ax.set_title('Consumption')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 7. Node trajectory for comparison
    ax = axes[2, 0]
    npx = [r['node_planet_x'] for r in rows]; npy = [r['node_planet_y'] for r in rows]
    for i in range(1, n):
        ax.plot(npx[i-1:i+1], npy[i-1:i+1], '-', color=colors[i], lw=0.5)
    ax.plot(npx[0], npy[0], 'go', ms=6)
    ax.plot(npx[-1], npy[-1], 'ro', ms=6)
    ax.set_aspect('equal'); ax.set_title('Node Trajectory (comparison)')
    ax.grid(True, alpha=0.3)

    # 8. Per-step angular velocity (deposits)
    ax = axes[2, 1]
    ax.plot(ticks[1:], angles, 'g-', lw=0.3, alpha=0.7)
    ax.axhline(0, color='k', alpha=0.3)
    ax.set_ylabel('Deg/step'); ax.set_xlabel('Tick')
    ax.set_title('Deposit Angular Velocity'); ax.grid(True, alpha=0.3)

    # 9. Planet hops
    ax = axes[2, 2]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', lw=0.8)
    ax.set_ylabel('Hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Hops'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "full_rev_results.png"), dpi=150)
    plt.close()
    print(f"Saved: full_rev_results.png")


if __name__ == '__main__':
    run()
