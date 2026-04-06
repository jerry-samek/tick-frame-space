#!/usr/bin/env python3
"""
Experiment 128 v2 — Large Scale: 500k nodes, 10k star, real statistics

The honest test: v13 mechanism (entity routing on real graph, no hand-coded
momentum) at a scale where statistics should produce classical behavior.

N_star=10,000 → binding/thermal ratio = 10,000 (vs 80 in previous runs).
The star should self-bind. The deposit gradient should be steep.
The planet should see a directional signal.

500k nodes, R=80, 10k star, 5 planet. ~8 hour run.
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
PLANET_COUNT = 5
PLANET_GROUPS = 2

WARMUP_TICKS = 500000     # long warmup for 10k nodes to equilibrate
SIM_TICKS = 700000        # long sim for multiple orbital periods
MEASURE_EVERY = 5000
LOG_EVERY = 10000   # frequent logging for overnight monitoring

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


def density_profile(graph, spectrum, center, hop_dist, max_d=20):
    by_dist = {}
    seen = set()
    sample = 0
    for (i, j), c in graph.connectors.items():
        if (i, j) in seen:
            continue
        seen.add((i, j))
        d = min(hop_dist[i], hop_dist[j])
        if d < 0 or d >= max_d:
            continue
        matching = sum(v for k, v in c.deposits.items() if k in spectrum)
        density = matching / c.length if c.length > 0 else 0
        by_dist.setdefault(d, []).append(density)
        sample += 1
        if sample > 100000:  # sample limit for performance
            break
    result = {}
    for d in sorted(by_dist.keys()):
        result[d] = float(np.mean(by_dist[d]))
    return result


def place_planet_cluster(graph, star_com, star_radius, n_nodes):
    dists = np.linalg.norm(graph.pos - star_com, axis=1)
    min_dist = star_radius + 10.0
    beyond = np.where(dists >= min_dist)[0]
    if len(beyond) < n_nodes:
        beyond = np.argsort(dists)[-n_nodes:]
    seed_idx = beyond[np.argmin(dists[beyond])]
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
    if planet:
        planet.tick_transit(graph, tick)
    star.tick_charging(graph)
    if planet:
        planet.tick_charging(graph)
    star.tick_routing(graph, rng)
    if planet:
        planet.tick_routing(graph, rng)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print(f"Building graph: N={N_NODES}, R={SPHERE_R}...")
    sys.stdout.flush()
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)")
    sys.stdout.flush()

    # Star: 10k nodes nearest to origin
    print(f"Placing star: {STAR_COUNT} nodes...")
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    initial_star_r = star.mean_radius(g)
    print(f"  Star initial mean_r={initial_star_r:.2f}")
    sys.stdout.flush()

    center = g.nearest_to_origin(1)[0]

    # Warmup
    print(f"\n{'=' * 60}")
    print(f"WARMUP ({WARMUP_TICKS} ticks, star only)")
    print(f"{'=' * 60}\n")
    sys.stdout.flush()

    t0 = time.time()
    for tick in range(1, WARMUP_TICKS + 1):
        tick_world(star, None, g, rng, tick)

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            total_same, total_diff, total_consumed = g.total_same_different()
            sr = star.mean_radius(g)
            print(f"  t={tick:7d}  star_r={sr:.2f}  "
                  f"hops={star.total_hops()}  "
                  f"S/D/C={total_same}/{total_diff}/{total_consumed}  "
                  f"({tps:.0f} t/s, ETA {(WARMUP_TICKS-tick)/tps/60:.0f}min)")
            sys.stdout.flush()

    star_com = star.com(g)
    star_r = star.mean_radius(g)
    total_same, total_diff, total_consumed = g.total_same_different()
    print(f"\nStar equilibrated: mean_r={star_r:.2f}")
    print(f"Same={total_same}, Different={total_diff}, Consumed={total_consumed}")
    sys.stdout.flush()

    # Density profile
    hop_dist = bfs_distances(g, center)
    prof = density_profile(g, star_spectrum, center, hop_dist)
    print("Density profile:", " ".join(f"d{d}={prof.get(d,0):.2f}" for d in range(15)))
    sys.stdout.flush()

    # Planet
    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)

    p_com = planet.com(g)
    initial_dist = float(np.linalg.norm(p_com - star_com))
    print(f"\nPlanet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}")
    print(f"NO kick. v13 mechanism at 10k-star scale.")
    sys.stdout.flush()

    # Simulation
    rows = []
    print(f"\n{'=' * 60}")
    print(f"SIMULATION ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")
    sys.stdout.flush()

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        tick_world(star, planet, g, rng, tick)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com(g)
            p_com = planet.com(g)
            dist = float(np.linalg.norm(p_com - s_com))

            rows.append({
                'tick': tick,
                'planet_star_dist': dist,
                'planet_x': p_com[0], 'planet_y': p_com[1], 'planet_z': p_com[2],
                'star_x': s_com[0], 'star_y': s_com[1], 'star_z': s_com[2],
                'star_mean_r': star.mean_radius(g),
                'planet_hops': planet.total_hops(),
                'star_hops': star.total_hops(),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
                  f"({tps:.0f} t/s, ETA {(SIM_TICKS-tick)/tps/60:.0f}min)")
            sys.stdout.flush()

    elapsed = time.time() - t0
    print(f"\nDone: {SIM_TICKS} ticks in {elapsed:.1f}s ({SIM_TICKS/elapsed:.0f} t/s)")
    sys.stdout.flush()

    # Save CSV
    csv_path = os.path.join(OUT, "results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    # Analysis
    analyze(rows, initial_dist, g, star_spectrum, center, hop_dist)
    plot(rows, initial_dist)


def analyze(rows, initial_dist, graph, spectrum, center, hop_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    dists = [r['planet_star_dist'] for r in rows]
    last = [r for r in rows if r['tick'] > SIM_TICKS * 0.5]

    # 1. Star radius
    if last:
        sr = np.mean([r['star_mean_r'] for r in last])
        print(f"  1. Star radius (late): {sr:.2f}  [COMPACT if <15]")

    # 2. Attraction
    print(f"  2. Attraction: initial={initial_dist:.2f}  min={min(dists):.2f}")

    # 3. Bound
    print(f"  3. Bound: final={dists[-1]:.2f}")

    # 4. Density gradient
    prof = density_profile(graph, spectrum, center, hop_dist)
    d0 = prof.get(0, 0) + prof.get(1, 0)
    d5 = prof.get(5, 0) + prof.get(6, 0)
    d10 = prof.get(10, 0) + prof.get(11, 0)
    print(f"  4. Density: d0-1={d0:.2f}  d5-6={d5:.2f}  d10-11={d10:.2f}")
    if d5 > 0:
        print(f"     Gradient: d0/d5={d0/d5:.1f}x  d0/d10={d0/max(0.01,d10):.1f}x")

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
        mc = np.mean(coh)
        print(f"  6. Coherence: {mc:.3f}")

    # 7. Oscillations
    mean_dist = np.mean(dists)
    crossings = sum(1 for i in range(1, len(dists))
                    if (dists[i-1] < mean_dist) != (dists[i] < mean_dist))
    print(f"  7. Oscillations: ~{crossings/2:.1f}")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Experiment 128 v2: Large Scale (500k nodes, 10k star)', fontsize=14)

    # 1. Distance
    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.5)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5)
    ax.set_ylabel('Distance'); ax.set_title('Planet-Star Distance')
    ax.grid(True, alpha=0.3)

    # 2. XY trajectory
    ax = axes[0, 1]
    px = [r['planet_x'] for r in rows]
    py = [r['planet_y'] for r in rows]
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

    # 5. Planet hops
    ax = axes[1, 1]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Total Hops')
    ax.grid(True, alpha=0.3)

    # 6. Radial velocity
    ax = axes[1, 2]
    if n > 1:
        v_rad = []
        for i in range(1, n):
            dt = rows[i]['tick'] - rows[i-1]['tick']
            dd = rows[i]['planet_star_dist'] - rows[i-1]['planet_star_dist']
            v_rad.append(dd / dt * 1000 if dt > 0 else 0)
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.5, alpha=0.7)
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('dr/1000 ticks'); ax.set_xlabel('Tick')
    ax.set_title('Radial Velocity'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "results.png"), dpi=150)
    plt.close()
    print(f"Saved: results.png")


if __name__ == '__main__':
    run()
