#!/usr/bin/env python3
"""
Experiment 118 v17 -- Inter-Group Rotation + Consumption

v16 consumption rule + inter-group routing for internal circulation.
Star nodes route toward OTHER star groups (s0->{s1,s2,s3}).
Star becomes a spinning body, not a diffusing cloud.
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

SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24
STAR_COUNT = 80
STAR_GROUPS = 4
PLANET_COUNT = 5
PLANET_GROUPS = 2

WARMUP_TICKS = 200000
SIM_TICKS = 300000
MEASURE_EVERY = 2000
LOG_EVERY = 30000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def place_planet_cluster(graph, star_com, star_radius, n_nodes):
    dists = np.linalg.norm(graph.pos - star_com, axis=1)
    min_dist = star_radius + 3.0
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


def density_profile(graph, spectrum, center, hop_dist, max_d=10):
    """Mean matching density of connectors at each hop distance."""
    by_dist = {}
    seen = set()
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
    result = {}
    for d in sorted(by_dist.keys()):
        result[d] = float(np.mean(by_dist[d]))
    return result


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

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)
    print(f"Star: {STAR_COUNT} nodes, mean_r={star.mean_radius(g):.2f}")

    center = g.nearest_to_origin(1)[0]
    hop_dist = bfs_distances(g, center)

    # Warmup
    print(f"\n{'=' * 60}")
    print(f"WARMUP ({WARMUP_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, WARMUP_TICKS + 1):
        tick_world(star, None, g, rng, tick)
        if tick % (WARMUP_TICKS // 5) == 0:
            elapsed = time.time() - t0
            total_same, total_diff, total_consumed = g.total_same_different()
            gf_ratio = star.mean_gravity_forward_ratio(g)
            prof = density_profile(g, star_spectrum, center, hop_dist)
            d0 = prof.get(0, 0) + prof.get(1, 0)
            d5 = prof.get(4, 0) + prof.get(5, 0)
            grad = d0 / max(0.01, d5)
            print(f"  t={tick:7d}  mean_r={star.mean_radius(g):.2f}  "
                  f"hops={star.total_hops()}  "
                  f"g/f={gf_ratio:.1f}  "
                  f"grad={grad:.1f}  "
                  f"S/D/C={total_same}/{total_diff}/{total_consumed}  "
                  f"({tick/elapsed:.0f} t/s)")

    star_com = star.com(g)
    star_r = star.mean_radius(g)
    total_same, total_diff, total_consumed = g.total_same_different()
    print(f"\nStar: mean_r={star_r:.2f}, hops={star.total_hops()}")
    print(f"Same={total_same}, Different={total_diff}")

    prof = density_profile(g, star_spectrum, center, hop_dist)
    prof_str = " ".join(f"d{d}={prof.get(d,0):.1f}" for d in range(8))
    print(f"Density profile: {prof_str}")

    # Planet
    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)

    p_com = planet.com(g)
    initial_dist = float(np.linalg.norm(p_com - star_com))
    print(f"\nPlanet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}")
    print(f"  NO kick. Accumulated density + Same rule + length momentum.")

    # Simulation
    rows = []
    print(f"\n{'=' * 60}")
    print(f"PHASE 2 ({SIM_TICKS} ticks, NO kick)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
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
                'planet_hops': planet.total_hops(),
                'star_hops': star.total_hops(),
                'total_same': total_same,
                'total_different': total_diff,
                'total_consumed': total_consumed,
                'star_gf_ratio': star.mean_gravity_forward_ratio(g),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
                  f"g/f={r['star_gf_ratio']:.1f}  "
                  f"S/D/C={r['total_same']}/{r['total_different']}/{r.get('total_consumed',0)}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {SIM_TICKS} ticks in {elapsed:.1f}s ({SIM_TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "phase2_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    analyze(rows, initial_dist, g, star_spectrum, center, hop_dist)
    plot(rows, initial_dist, g, star_spectrum, center, hop_dist)


def analyze(rows, initial_dist, graph, spectrum, center, hop_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    dists = [r['planet_star_dist'] for r in rows]
    last_rows = [r for r in rows if r['tick'] > SIM_TICKS * 0.5]

    # 1. Star compact
    if last_rows:
        sr = np.mean([r['star_mean_r'] for r in last_rows])
        status1 = "PASS" if sr < 8.0 else "FAIL"
        print(f"  1. Star compact: mean_r={sr:.2f}  [target <8]  [{status1}]")

    # 2. Attraction
    min_dist = min(dists)
    status2 = "PASS" if min_dist < initial_dist * 0.7 else "FAIL"
    print(f"  2. Attraction: initial={initial_dist:.2f}  min={min_dist:.2f}  [{status2}]")

    # 3. Bound
    escaped = dists[-1] > initial_dist * 2.0
    status3 = "PASS" if not escaped else "FAIL"
    print(f"  3. Bound: final={dists[-1]:.2f}  [{status3}]")

    # 4. Density gradient
    prof = density_profile(graph, spectrum, center, hop_dist)
    d0 = prof.get(0, 0) + prof.get(1, 0)
    d4 = prof.get(4, 0) + prof.get(5, 0)
    grad = d0 / max(0.01, d4)
    status4 = "PASS" if grad > 3.0 else "FAIL"
    print(f"  4. Density gradient: d0-1={d0:.1f}  d4-5={d4:.1f}  "
          f"ratio={grad:.1f}  [target >3]  [{status4}]")

    # 5. Gravity/forward ratio
    if last_rows:
        gf = np.mean([r['star_gf_ratio'] for r in last_rows])
        status5 = "PASS" if gf > 3.0 else "FAIL"
        print(f"  5. Star g/f ratio: {gf:.1f}  [target >3]  [{status5}]")

    # 6. Tangential
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.arctan2(cross, dot))
    total_abs = sum(abs(a) for a in angles)
    total_net = sum(angles)
    status6 = "PASS" if total_abs > np.pi else "FAIL"
    print(f"  6. Tangential: net={np.degrees(total_net):.1f}  "
          f"total={np.degrees(total_abs):.1f}  [{status6}]")

    # 7. Coherence
    if len(angles) > 20:
        chunk_size = len(angles) // 10
        coherence = []
        for c in range(10):
            chunk = angles[c*chunk_size:(c+1)*chunk_size]
            if chunk:
                coherence.append(abs(np.mean(np.sign(chunk))))
        mc = np.mean(coherence)
        status7 = "PASS" if mc > 0.3 else "FAIL"
        print(f"  7. Coherence: {mc:.3f}  [{status7}]")

    # 8. Oscillations
    mean_dist = np.mean(dists)
    crossings = sum(1 for i in range(1, len(dists))
                    if (dists[i-1] < mean_dist) != (dists[i] < mean_dist))
    print(f"  8. Oscillations: ~{crossings/2:.1f}")

    print()


def plot(rows, initial_dist, graph, spectrum, center, hop_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v16 -- Density + Same Rule + Length Momentum (NO KICK)',
                 fontsize=13)

    # 1. Distance
    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5,
               label=f'initial={initial_dist:.1f}')
    ax.set_ylabel('Distance'); ax.set_title('Planet-Star Distance')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 2. XY trajectory
    ax = axes[0, 1]
    px = [r['planet_x'] for r in rows]
    py = [r['planet_y'] for r in rows]
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', markersize=10, label='start')
    ax.plot(px[-1], py[-1], 'ro', markersize=10, label='end')
    ax.plot(np.mean([r['star_x'] for r in rows]),
            np.mean([r['star_y'] for r in rows]),
            'y*', markersize=15, label='star')
    ax.set_xlabel('X'); ax.set_ylabel('Y'); ax.set_title('Trajectory (XY)')
    ax.legend(); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

    # 3. Angular position
    ax = axes[0, 2]
    cum = [0]
    for i in range(1, n):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        cum.append(cum[-1] + np.arctan2(cross, dot))
    ax.plot(ticks, np.degrees(cum), 'g-', linewidth=0.8)
    ax.set_ylabel('Cumulative angle (deg)'); ax.set_title('Angular Position')
    ax.grid(True, alpha=0.3)

    # 4. Star radius
    ax = axes[1, 0]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.axhline(8.0, color='g', linestyle='--', alpha=0.5, label='target<8')
    ax.set_ylabel('Radius'); ax.set_title('Star Mean Radius')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 5. Gravity/forward ratio
    ax = axes[1, 1]
    ax.plot(ticks, [r['star_gf_ratio'] for r in rows], 'purple', linewidth=0.8)
    ax.axhline(3.0, color='g', linestyle='--', alpha=0.5, label='target>3')
    ax.set_ylabel('Gravity/Forward'); ax.set_title('Star G/F Ratio')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 6. Same vs Different
    ax = axes[1, 2]
    ax.plot(ticks, [r['total_same'] for r in rows], 'g-', linewidth=0.8, label='Same')
    ax.plot(ticks, [r['total_different'] for r in rows], 'r-', linewidth=0.8, label='Different')
    ax.plot(ticks, [r.get('total_consumed', 0) for r in rows], 'b--', linewidth=0.8, label='Consumed')
    ax.set_ylabel('Cumulative'); ax.set_title('Same vs Different')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 7. Density profile at end
    ax = axes[2, 0]
    prof = density_profile(graph, spectrum, center, hop_dist)
    d_list = sorted(prof.keys())
    ax.bar(d_list, [prof[d] for d in d_list], color='steelblue', alpha=0.7)
    ax.set_xlabel('Hop distance'); ax.set_ylabel('Mean matching density')
    ax.set_title('Density Profile'); ax.grid(True, alpha=0.3)

    # 8. Radial velocity
    ax = axes[2, 1]
    if n > 1:
        v_rad = []
        for i in range(1, n):
            dt = rows[i]['tick'] - rows[i-1]['tick']
            dd = rows[i]['planet_star_dist'] - rows[i-1]['planet_star_dist']
            v_rad.append(dd / dt * 1000 if dt > 0 else 0)
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.5, alpha=0.7)
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('dr / 1000 ticks'); ax.set_xlabel('Tick')
    ax.set_title('Radial Velocity'); ax.grid(True, alpha=0.3)

    # 9. Planet hops
    ax = axes[2, 2]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Cumulative hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Hops'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
