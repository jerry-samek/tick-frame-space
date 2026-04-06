#!/usr/bin/env python3
"""
Experiment 128 v5 — Vectorized Substrate, 500 Planet Nodes

Same physics as v4 but all operations batched in numpy.
Target: 50-100 t/s (vs v4's 14 t/s).
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

    # Star
    star_ids = sub.nearest_to_origin(STAR_COUNT)
    star = EntityBatch("star", star_ids, STAR_GROUPS, 0, True, sub)
    star_com = star.com()
    print(f"Star: {STAR_COUNT} nodes, r={star.mean_radius():.2f}")

    # Planet
    planet_ids = place_cluster(sub, star_com, 40.0, PLANET_COUNT)
    planet = EntityBatch("planet", planet_ids, PLANET_GROUPS, STAR_GROUPS, False, sub)
    p_com = planet.com()
    initial_dist = float(np.linalg.norm(p_com - star_com))
    print(f"Planet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}, "
          f"r={planet.mean_radius():.2f}")
    print(f"Both from tick 0. Vectorized.")
    sys.stdout.flush()

    rows = []
    prev_tick = 0
    prev_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"SIMULTANEOUS RUN ({TICKS} ticks)")
    print(f"{'=' * 60}\n")
    sys.stdout.flush()

    t0 = time.time()
    for tick in range(1, TICKS + 1):
        # Phase 1: transit
        star.tick_transit(tick)
        planet.tick_transit(tick)

        # Phase 2: charging
        star.tick_charging()
        planet.tick_charging()

        # Phase 3: routing
        star.tick_routing(rng)
        planet.tick_routing(rng)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com()
            p_com = planet.com()
            dist = float(np.linalg.norm(p_com - s_com))
            total_deps, total_diff, total_consumed = sub.stats()

            rows.append({
                'tick': tick,
                'planet_star_dist': dist,
                'planet_x': float(p_com[0]), 'planet_y': float(p_com[1]),
                'planet_z': float(p_com[2]),
                'star_x': float(s_com[0]), 'star_y': float(s_com[1]),
                'star_z': float(s_com[2]),
                'star_mean_r': star.mean_radius(),
                'planet_mean_r': planet.mean_radius(),
                'planet_hops': planet.total_hops(),
                'star_hops': star.total_hops(),
                'total_different': total_diff,
                'total_consumed': total_consumed,
            })

        if tick % LOG_EVERY == 0:
            now = time.time()
            recent_tps = (tick - prev_tick) / max(0.001, now - prev_time)
            prev_tick = tick
            prev_time = now
            remaining = (TICKS - tick) / max(1, recent_tps) / 60
            r = rows[-1]
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"planet_r={r['planet_mean_r']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
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

    analyze(rows, initial_dist)
    plot(rows, initial_dist)


def analyze(rows, initial_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    dists = [r['planet_star_dist'] for r in rows]
    last = [r for r in rows if r['tick'] > TICKS * 0.5]

    if last:
        print(f"  1. Star radius (late): {np.mean([r['star_mean_r'] for r in last]):.2f}")
        print(f"  2. Planet radius (late): {np.mean([r['planet_mean_r'] for r in last]):.2f}")

    print(f"  3. Distance: initial={initial_dist:.2f}  "
          f"min={min(dists):.2f}  max={max(dists):.2f}  final={dists[-1]:.2f}")
    if last:
        print(f"     Late: mean={np.mean([r['planet_star_dist'] for r in last]):.2f}  "
              f"std={np.std([r['planet_star_dist'] for r in last]):.2f}")

    if rows:
        r = rows[-1]
        print(f"  4. Different={r['total_different']}  Consumed={r['total_consumed']}")

    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.degrees(np.arctan2(cross, dot)))

    print(f"  5. Tangential: net={sum(angles):.1f}  total={sum(abs(a) for a in angles):.1f}")

    if len(angles) > 20:
        cs = len(angles) // 10
        coh = [abs(np.mean(np.sign(angles[c*cs:(c+1)*cs]))) for c in range(10)]
        print(f"  6. Coherence: {np.mean(coh):.3f}")

    mean_d = np.mean(dists)
    crossings = sum(1 for i in range(1, len(dists))
                    if (dists[i-1] < mean_d) != (dists[i] < mean_d))
    print(f"  7. Oscillations: ~{crossings/2:.1f}")
    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)
    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle('Experiment 128 v5: Vectorized (500k, 10k star, 500 planet)', fontsize=14)

    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.5)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5)
    ax.set_ylabel('Distance'); ax.set_title('Planet-Star Distance'); ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    px = [r['planet_x'] for r in rows]; py = [r['planet_y'] for r in rows]
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', ms=8, label='start')
    ax.plot(px[-1], py[-1], 'ro', ms=8, label='end')
    ax.plot(np.mean([r['star_x'] for r in rows]),
            np.mean([r['star_y'] for r in rows]), 'y*', ms=12, label='star')
    ax.set_aspect('equal'); ax.set_title('Trajectory (XY)'); ax.legend(); ax.grid(True, alpha=0.3)

    ax = axes[0, 2]
    angles = []
    for i in range(1, n):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        angles.append(np.degrees(np.arctan2(v0[0]*v1[1]-v0[1]*v1[0], v0[0]*v1[0]+v0[1]*v1[1])))
    ax.plot(ticks[1:], np.cumsum(angles), 'g-', linewidth=0.8)
    ax.set_ylabel('Degrees'); ax.set_title('Angular Position'); ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Radius'); ax.set_title('Star Mean Radius'); ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    ax.plot(ticks, [r['planet_mean_r'] for r in rows], 'blue', linewidth=0.8)
    ax.set_ylabel('Radius'); ax.set_title('Planet Mean Radius'); ax.grid(True, alpha=0.3)

    ax = axes[1, 2]
    ax.plot(ticks, [r['total_different'] for r in rows], 'r-', linewidth=0.5, label='Diff')
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'b--', linewidth=0.5, label='Consumed')
    ax.set_ylabel('Count'); ax.set_title('Different / Consumed'); ax.legend(); ax.grid(True, alpha=0.3)

    ax = axes[2, 0]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Hops'); ax.set_xlabel('Tick'); ax.set_title('Planet Hops'); ax.grid(True, alpha=0.3)

    ax = axes[2, 1]
    if n > 1:
        v_rad = [(rows[i]['planet_star_dist']-rows[i-1]['planet_star_dist'])/(rows[i]['tick']-rows[i-1]['tick'])*1000
                 for i in range(1, n)]
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.3, alpha=0.7)
        ax.axhline(0, color='k', alpha=0.3)
    ax.set_ylabel('dr/1000t'); ax.set_xlabel('Tick'); ax.set_title('Radial Velocity'); ax.grid(True, alpha=0.3)

    ax = axes[2, 2]
    ax.scatter([r['planet_star_dist'] for r in rows],
               [r['planet_mean_r'] for r in rows], s=3, alpha=0.3, c='purple')
    ax.set_xlabel('Distance'); ax.set_ylabel('Planet radius')
    ax.set_title('Planet Size vs Distance'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"Saved: results.png")


if __name__ == '__main__':
    run()
