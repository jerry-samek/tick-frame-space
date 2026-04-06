#!/usr/bin/env python3
"""
Experiment 118 v11 -- Phase 2: Newtonian Orbital Test

Forward default (Newton I) + deposit deflection (Newton II).
Planet WITHOUT seeded kick. 50-tick charging phase.

The decisive test: does per-hop tangential component show COHERENT
orbital arcs (systematic sign during each swing) or RANDOM noise?
"""

import os
import time
import csv
import numpy as np

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


def tick_world(star, planet, graph, rng, tick):
    """One tick with three-phase ordering."""
    graph.reset_all_ticks()

    # Phase 1: transit arrivals (deposits happen here)
    star.tick_transit(graph, tick)
    if planet:
        planet.tick_transit(graph, tick)

    # Phase 2: charging entities accumulate deflection
    star.tick_charging(graph)
    if planet:
        planet.tick_charging(graph)

    # Phase 3: routing entities make hop decision
    star.tick_routing(graph, rng)
    if planet:
        planet.tick_routing(graph, rng)


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # Star
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)
    print(f"Star: {STAR_COUNT} nodes, mean_r={star.mean_radius(g):.2f}")

    # Warmup
    print(f"\n{'=' * 60}")
    print(f"WARMUP: Star equilibration ({WARMUP_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, WARMUP_TICKS + 1):
        tick_world(star, None, g, rng, tick)
        if tick % (WARMUP_TICKS // 5) == 0:
            elapsed = time.time() - t0
            ch, rt, tr = star.state_fractions()
            print(f"  t={tick:7d}  mean_r={star.mean_radius(g):.2f}  "
                  f"hops={star.total_hops()}  "
                  f"defl={star.mean_deflection():.3f}  "
                  f"C/R/T={ch:.2f}/{rt:.2f}/{tr:.2f}  "
                  f"({tick/elapsed:.0f} t/s)")

    star_com = star.com(g)
    star_r = star.mean_radius(g)
    print(f"\nStar equilibrated: mean_r={star_r:.2f}, hops={star.total_hops()}")

    # Planet
    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)

    p_com = planet.com(g)
    initial_dist = float(np.linalg.norm(p_com - star_com))
    print(f"\nPlanet: {PLANET_COUNT} nodes, dist={initial_dist:.2f}")
    print(f"  NO kick. Newton I (forward) + Newton II (deflection).")

    # Simulation
    rows = []
    print(f"\n{'=' * 60}")
    print(f"PHASE 2: Newtonian Orbital Test ({SIM_TICKS} ticks, NO kick)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        tick_world(star, planet, g, rng, tick)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com(g)
            p_com = planet.com(g)
            dist = float(np.linalg.norm(p_com - s_com))
            p_ch, p_rt, p_tr = planet.state_fractions()
            p_defl = planet.mean_deflection()

            rows.append({
                'tick': tick,
                'planet_star_dist': dist,
                'planet_x': p_com[0], 'planet_y': p_com[1], 'planet_z': p_com[2],
                'star_x': s_com[0], 'star_y': s_com[1], 'star_z': s_com[2],
                'star_mean_r': star.mean_radius(g),
                'planet_hops': planet.total_hops(),
                'planet_charging': p_ch,
                'planet_transit': p_tr,
                'planet_deflection': p_defl,
                'planet_deps_received': sum(en.deposits_received for en in planet.entity_nodes),
                'star_hops': star.total_hops(),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
                  f"p_defl={r['planet_deflection']:.3f}  "
                  f"p_deps={r['planet_deps_received']}  "
                  f"C/T={r['planet_charging']:.2f}/{r['planet_transit']:.2f}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {SIM_TICKS} ticks in {elapsed:.1f}s ({SIM_TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "phase2_results.csv")
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
    min_dist = min(dists)

    # 1. Attraction
    status1 = "PASS" if min_dist < initial_dist * 0.7 else "FAIL"
    print(f"  1. Attraction: initial={initial_dist:.2f}  min={min_dist:.2f}  [{status1}]")

    # 2. Bound
    escaped = dists[-1] > initial_dist * 2.0
    status2 = "PASS" if not escaped else "FAIL"
    print(f"  2. Bound: final={dists[-1]:.2f}  [{status2}]")

    # 3. Tangential
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
    status3 = "PASS" if total_abs > np.pi else "FAIL"
    print(f"  3. Tangential (NO KICK): net={np.degrees(total_net):.1f} deg  "
          f"total={np.degrees(total_abs):.1f} deg  [{status3}]")

    # 4. Hop rate
    if rows[-1]['planet_hops'] > 0:
        rate = rows[-1]['planet_hops'] / rows[-1]['tick'] * 1000
        print(f"  4. Planet hop rate: {rows[-1]['planet_hops']} hops, "
              f"{rate:.2f} per 1000 ticks")

    # 5. Oscillations
    mean_dist = np.mean(dists)
    crossings = sum(1 for i in range(1, len(dists))
                    if (dists[i-1] < mean_dist) != (dists[i] < mean_dist))
    print(f"  5. Oscillations: ~{crossings/2:.1f}")

    # 6. Deflection strength
    last_rows = [r for r in rows if r['tick'] > SIM_TICKS * 0.5]
    if last_rows:
        mean_defl = np.mean([r['planet_deflection'] for r in last_rows])
        mean_deps = np.mean([r['planet_deps_received'] for r in last_rows])
        print(f"  6. Planet deflection (late): mean={mean_defl:.4f}  "
              f"deps_received={mean_deps:.0f}")

    # 7. Coherence test: do angular increments correlate with orbital phase?
    if len(angles) > 20:
        # Split into chunks and check if sign is consistent within chunks
        chunk_size = len(angles) // 10
        coherence_scores = []
        for c in range(10):
            chunk = angles[c*chunk_size:(c+1)*chunk_size]
            if chunk:
                mean_sign = abs(np.mean(np.sign(chunk)))
                coherence_scores.append(mean_sign)
        mean_coherence = np.mean(coherence_scores)
        # Random walk: coherence ~ 0. Real orbit: coherence ~ 1.
        status7 = "PASS" if mean_coherence > 0.3 else "FAIL"
        print(f"  7. Angular coherence: {mean_coherence:.3f}  "
              f"[0=random, 1=orbit]  [{status7}]")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]
    n = len(ticks)

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v11 -- Newtonian Entities (NO KICK)', fontsize=14)

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
    ax.set_xlabel('X'); ax.set_ylabel('Y')
    ax.set_title('Trajectory (XY)')
    ax.legend(); ax.set_aspect('equal'); ax.grid(True, alpha=0.3)

    # 3. Angular position
    ax = axes[0, 2]
    cum_angle = [0]
    for i in range(1, n):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        cum_angle.append(cum_angle[-1] + np.arctan2(cross, dot))
    ax.plot(ticks, np.degrees(cum_angle), 'g-', linewidth=0.8)
    ax.set_ylabel('Cumulative angle (deg)')
    ax.set_title('Angular Position (orbit = steady trend)')
    ax.grid(True, alpha=0.3)

    # 4. Deflection magnitude
    ax = axes[1, 0]
    ax.plot(ticks, [r['planet_deflection'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Deflection magnitude')
    ax.set_title('Planet Deflection (gravity signal)')
    ax.grid(True, alpha=0.3)

    # 5. Planet state fractions
    ax = axes[1, 1]
    ax.plot(ticks, [r['planet_charging'] for r in rows], 'g-', linewidth=0.8, label='charging')
    ax.plot(ticks, [r['planet_transit'] for r in rows], 'b-', linewidth=0.8, label='transit')
    ax.set_ylabel('Fraction'); ax.set_title('Planet State')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 6. Star radius
    ax = axes[1, 2]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Radius'); ax.set_title('Star Mean Radius')
    ax.grid(True, alpha=0.3)

    # 7. Planet hops
    ax = axes[2, 0]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Cumulative hops'); ax.set_xlabel('Tick')
    ax.set_title('Planet Total Hops'); ax.grid(True, alpha=0.3)

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

    # 9. Deflection vs distance scatter
    ax = axes[2, 2]
    ax.scatter([r['planet_star_dist'] for r in rows],
               [r['planet_deflection'] for r in rows],
               s=2, alpha=0.3, c='purple')
    ax.set_xlabel('Distance from star'); ax.set_ylabel('Deflection')
    ax.set_title('Deflection vs Distance'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
