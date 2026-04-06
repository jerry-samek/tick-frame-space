#!/usr/bin/env python3
"""
Experiment 128 v4 — 500 Planet Nodes (vs v3's 5)

Same graph (500k, R=80), same star (10k nodes). Planet: 500 nodes.
Mass ratio 1:20 (planet:star). Both from tick 0.

Does the planet self-bind? Does the boundary stabilize?
Does the oscillation amplitude shrink from v3's 3-53 range?
"""

import os
import sys
import time
import csv
import numpy as np
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph import Graph
from entity import Entity

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


def place_cluster(graph, center_pos, target_dist, n_nodes):
    """Place n_nodes as a tight cluster at target_dist from center_pos."""
    dists = np.linalg.norm(graph.pos - center_pos, axis=1)
    seed_idx = np.argmin(np.abs(dists - target_dist))
    seed_pos = graph.pos[seed_idx]
    neighbor_dists = np.linalg.norm(graph.pos - seed_pos, axis=1)
    neighbor_dists[seed_idx] = np.inf
    nearest = np.argsort(neighbor_dists)
    cluster = [seed_idx]
    for n in nearest:
        if len(cluster) >= n_nodes:
            break
        cluster.append(n)
    return cluster


def tick_world(star, planet, graph, rng, tick):
    star.tick_transit(graph, tick)
    planet.tick_transit(graph, tick)
    star.tick_charging(graph)
    planet.tick_charging(graph)
    star.tick_routing(graph, rng)
    planet.tick_routing(graph, rng)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print(f"Building graph: N={N_NODES}, R={SPHERE_R}...")
    sys.stdout.flush()
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)")
    sys.stdout.flush()

    # Star
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    star_com = star.com(g)
    print(f"Star: {STAR_COUNT} nodes, initial r={star.mean_radius(g):.2f}")

    # Planet: 500 nodes at r~40
    planet_ids = place_cluster(g, star_com, 40.0, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)

    p_com = planet.com(g)
    initial_dist = float(np.linalg.norm(p_com - star_com))
    planet_r = planet.mean_radius(g)
    print(f"Planet: {PLANET_COUNT} nodes at r={initial_dist:.2f}, "
          f"planet_r={planet_r:.2f}")
    print(f"Mass ratio: 1:{STAR_COUNT//PLANET_COUNT} (planet:star)")
    print(f"Both from tick 0. No warmup.")
    sys.stdout.flush()

    # Run
    rows = []
    prev_tick = 0
    prev_time = time.time()

    print(f"\n{'=' * 60}")
    print(f"SIMULTANEOUS RUN ({TICKS} ticks)")
    print(f"{'=' * 60}\n")
    sys.stdout.flush()

    t0 = time.time()
    for tick in range(1, TICKS + 1):
        tick_world(star, planet, g, rng, tick)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com(g)
            p_com = planet.com(g)
            dist = float(np.linalg.norm(p_com - s_com))
            total_same, total_diff, total_consumed = g.total_same_different()

            rows.append({
                'tick': tick,
                'planet_star_dist': dist,
                'planet_x': p_com[0], 'planet_y': p_com[1], 'planet_z': p_com[2],
                'star_x': s_com[0], 'star_y': s_com[1], 'star_z': s_com[2],
                'star_mean_r': star.mean_radius(g),
                'planet_mean_r': planet.mean_radius(g),
                'planet_hops': planet.total_hops(),
                'star_hops': star.total_hops(),
                'total_same': total_same,
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
                  f"S/D/C={r['total_same']}/{r['total_different']}/{r['total_consumed']}  "
                  f"({recent_tps:.0f} t/s, ETA {remaining:.0f}min)")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s")

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

    # 1. Star radius
    if last:
        sr = np.mean([r['star_mean_r'] for r in last])
        print(f"  1. Star radius (late): {sr:.2f}")

    # 2. Planet radius (does it self-bind?)
    if last:
        pr = np.mean([r['planet_mean_r'] for r in last])
        print(f"  2. Planet radius (late): {pr:.2f}  "
              f"[compact if <15, diffuse if >30]")

    # 3. Distance
    print(f"  3. Distance: initial={initial_dist:.2f}  "
          f"min={min(dists):.2f}  max={max(dists):.2f}  "
          f"final={dists[-1]:.2f}")
    if last:
        mean_d = np.mean([r['planet_star_dist'] for r in last])
        std_d = np.std([r['planet_star_dist'] for r in last])
        print(f"     Late mean={mean_d:.2f}  std={std_d:.2f}  "
              f"(v3 was 3-53 range)")

    # 4. Consumption
    if rows:
        r = rows[-1]
        print(f"  4. Same={r['total_same']}  Diff={r['total_different']}  "
              f"Consumed={r['total_consumed']}")

    # 5. Tangential
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.degrees(np.arctan2(cross, dot)))

    total_net = sum(angles)
    total_abs = sum(abs(a) for a in angles)
    print(f"  5. Tangential: net={total_net:.1f}  total={total_abs:.1f}  "
          f"rev={total_net/360:.2f}")

    # 6. Coherence
    if len(angles) > 20:
        cs = len(angles) // 10
        coh = [abs(np.mean(np.sign(angles[c*cs:(c+1)*cs]))) for c in range(10)]
        print(f"  6. Coherence: {np.mean(coh):.3f}")

    # 7. Oscillations
    mean_dist = np.mean(dists)
    crossings = sum(1 for i in range(1, len(dists))
                    if (dists[i-1] < mean_dist) != (dists[i] < mean_dist))
    print(f"  7. Oscillations: ~{crossings/2:.1f}")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(3, 3, figsize=(18, 14))
    fig.suptitle(f'Experiment 128 v4: 500 Planet Nodes (500k graph, 10k star)',
                 fontsize=14)

    # 1. Distance
    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.5)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5)
    ax.set_ylabel('Distance'); ax.set_title('Planet-Star Distance')
    ax.grid(True, alpha=0.3)

    # 2. XY trajectory
    ax = axes[0, 1]
    px = [r['planet_x'] for r in rows]; py = [r['planet_y'] for r in rows]
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', markersize=8, label='start')
    ax.plot(px[-1], py[-1], 'ro', markersize=8, label='end')
    ax.plot(np.mean([r['star_x'] for r in rows]),
            np.mean([r['star_y'] for r in rows]),
            'y*', markersize=12, label='star')
    ax.set_aspect('equal'); ax.set_title('Trajectory (XY)')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 3. Angular position
    ax = axes[0, 2]
    angles = []
    for i in range(1, n):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.degrees(np.arctan2(cross, dot)))
    ax.plot(ticks[1:], np.cumsum(angles), 'g-', linewidth=0.8)
    ax.set_ylabel('Degrees'); ax.set_title('Angular Position')
    ax.grid(True, alpha=0.3)

    # 4. Star radius
    ax = axes[1, 0]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Radius'); ax.set_title('Star Mean Radius')
    ax.grid(True, alpha=0.3)

    # 5. Planet radius (self-binding?)
    ax = axes[1, 1]
    ax.plot(ticks, [r['planet_mean_r'] for r in rows], 'blue', linewidth=0.8)
    ax.set_ylabel('Radius'); ax.set_title('Planet Mean Radius (self-bind?)')
    ax.grid(True, alpha=0.3)

    # 6. Same / Different / Consumed
    ax = axes[1, 2]
    ax.plot(ticks, [r['total_same'] for r in rows], 'g-', linewidth=0.5, label='Same')
    ax.plot(ticks, [r['total_different'] for r in rows], 'r-', linewidth=0.5, label='Diff')
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'b--', linewidth=0.5, label='Consumed')
    ax.set_ylabel('Count'); ax.set_title('Same / Different / Consumed')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 7. Planet hops
    ax = axes[2, 0]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Total Hops'); ax.grid(True, alpha=0.3)

    # 8. Radial velocity
    ax = axes[2, 1]
    if n > 1:
        v_rad = []
        for i in range(1, n):
            dt = rows[i]['tick'] - rows[i-1]['tick']
            dd = rows[i]['planet_star_dist'] - rows[i-1]['planet_star_dist']
            v_rad.append(dd / dt * 1000 if dt > 0 else 0)
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.3, alpha=0.7)
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('dr/1000t'); ax.set_xlabel('Tick')
    ax.set_title('Radial Velocity'); ax.grid(True, alpha=0.3)

    # 9. Distance vs planet radius (correlation?)
    ax = axes[2, 2]
    ax.scatter([r['planet_star_dist'] for r in rows],
               [r['planet_mean_r'] for r in rows],
               s=3, alpha=0.3, c='purple')
    ax.set_xlabel('Distance from star'); ax.set_ylabel('Planet radius')
    ax.set_title('Planet Size vs Distance'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"Saved: results.png")


if __name__ == '__main__':
    run()
