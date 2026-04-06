#!/usr/bin/env python3
"""
Experiment 118 v9 Diagnostic: Tangential Motion Analysis

Four tests to determine what produces the ~2000 degrees of tangential motion:
  D3: Pure random walk (no deposits, no routing) — graph topology alone?
  D4: Frozen star (static deposit field) — star dynamics needed?
  D5: No planet deposits — planet trail feedback needed?
  Normal: Instrumented v9 run with per-hop routing decomposition (D1, D2, D6)

Usage:
  python phase2_diagnostic.py                     # normal instrumented run
  python phase2_diagnostic.py --random-walk       # D3
  python phase2_diagnostic.py --frozen-star       # D4
  python phase2_diagnostic.py --no-planet-deposit # D5
  python phase2_diagnostic.py --all               # run all four
"""

import os
import sys
import time
import csv
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph import Graph
from entity import Entity, EntityNode, BASE_WEIGHT, QuantumEmission
from propagation import ForwardTable, QuantumField

SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24
STAR_COUNT = 80
STAR_GROUPS = 4
PLANET_COUNT = 5
PLANET_GROUPS = 2

WARMUP_TICKS = 100000
SIM_TICKS = 200000
MEASURE_EVERY = 1000

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


def angular_displacement_2d(prev_pos, curr_pos, center):
    """Signed angular displacement around center in XY plane."""
    v0 = prev_pos[:2] - center[:2]
    v1 = curr_pos[:2] - center[:2]
    cross = v0[0]*v1[1] - v0[1]*v1[0]
    dot = v0[0]*v1[0] + v0[1]*v1[1]
    return np.arctan2(cross, dot)


def build_world(seed=SEED):
    """Build graph, star, warmup. Returns (graph, star, fwd, field, star_com, star_r, rng)."""
    rng = np.random.default_rng(seed)
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=seed)
    fwd = ForwardTable(g)

    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)
    field = QuantumField(g, fwd, max_age=100)

    print(f"Warmup: {WARMUP_TICKS} ticks...")
    t0 = time.time()
    for tick in range(1, WARMUP_TICKS + 1):
        events = star.tick(g, rng)
        idle_set = star.idle_node_set()
        for em in events:
            field.process_emission(em.group, em.src_node, em.dest_node, g, idle_set)
        field.tick(idle_set)
    elapsed = time.time() - t0
    star_com = star.com(g)
    star_r = star.mean_radius(g)
    print(f"  Done ({elapsed:.1f}s). star_r={star_r:.2f}")

    return g, star, fwd, field, star_com, star_r, rng


# ═══════════════════════════════════════════════════════════
# D3: RANDOM WALK TEST
# ═══════════════════════════════════════════════════════════

def run_random_walk(n_trials=20):
    """Pure random walk on graph — no deposits, no routing signal."""
    print(f"\n{'=' * 60}")
    print(f"D3: RANDOM WALK TEST ({n_trials} trials, {SIM_TICKS} ticks each)")
    print(f"{'=' * 60}\n")

    rng_build = np.random.default_rng(SEED)
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)

    # Use the same star COM as the full experiment (approximate — just use origin area)
    star_com = g.pos[g.nearest_to_origin(STAR_COUNT)].mean(axis=0)
    star_r = np.linalg.norm(g.pos[g.nearest_to_origin(STAR_COUNT)] - star_com, axis=1).mean()

    # Place planet at same location as in full experiment
    planet_nodes = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    start_node = planet_nodes[0]

    results = []
    for trial in range(n_trials):
        rng = np.random.default_rng(SEED + 1000 + trial)
        node = start_node
        cum_angle = 0.0
        total_abs_angle = 0.0
        prev_pos = g.pos[node].copy()

        for tick in range(SIM_TICKS):
            nbrs = g.neighbors(node)
            node = nbrs[rng.integers(len(nbrs))]
            curr_pos = g.pos[node]
            da = angular_displacement_2d(prev_pos, curr_pos, star_com)
            cum_angle += da
            total_abs_angle += abs(da)
            prev_pos = curr_pos.copy()

        results.append({
            'trial': trial,
            'net_degrees': np.degrees(cum_angle),
            'total_degrees': np.degrees(total_abs_angle),
        })
        print(f"  Trial {trial:2d}: net={np.degrees(cum_angle):.1f} deg  "
              f"total={np.degrees(total_abs_angle):.1f} deg")

    # Summary
    nets = [r['net_degrees'] for r in results]
    totals = [r['total_degrees'] for r in results]
    print(f"\n  Random walk: net={np.mean(nets):.1f} +/- {np.std(nets):.1f} deg")
    print(f"               total={np.mean(totals):.1f} +/- {np.std(totals):.1f} deg")
    print(f"  Compare v9:  net=474 deg, total=2254 deg")

    # Save
    csv_path = os.path.join(OUT, "d3_random_walk.csv")
    with open(csv_path, 'w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=results[0].keys())
        w.writeheader()
        w.writerows(results)

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('D3: Random Walk vs Routed Orbit', fontsize=14)

    ax1.hist(nets, bins=15, alpha=0.7, label='random walk')
    ax1.axvline(474, color='r', linestyle='--', linewidth=2, label='v9 net (474)')
    ax1.set_xlabel('Net degrees'); ax1.set_ylabel('Count')
    ax1.set_title('Net Angular Displacement'); ax1.legend()

    ax2.hist(totals, bins=15, alpha=0.7, label='random walk')
    ax2.axvline(2254, color='r', linestyle='--', linewidth=2, label='v9 total (2254)')
    ax2.set_xlabel('Total degrees'); ax2.set_ylabel('Count')
    ax2.set_title('Total Angular Displacement'); ax2.legend()

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "d3_random_walk.png"), dpi=150)
    plt.close()
    print(f"  Saved: d3_random_walk.csv, d3_random_walk.png")

    return results


# ═══════════════════════════════════════════════════════════
# D4: FROZEN STAR
# ═══════════════════════════════════════════════════════════

def run_frozen_star():
    """Star stops after warmup. Static deposit field. Only planet moves."""
    print(f"\n{'=' * 60}")
    print(f"D4: FROZEN STAR ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    g, star, fwd, field, star_com, star_r, rng = build_world()

    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)
    initial_dist = float(np.linalg.norm(planet.com(g) - star_com))
    print(f"  Planet dist={initial_dist:.2f}. Star FROZEN.")

    rows = []
    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        # Star does NOT tick. Only planet.
        planet_events = planet.tick(g, rng)
        idle_set = planet.idle_node_set()
        for em in planet_events:
            field.process_emission(em.group, em.src_node, em.dest_node, g, idle_set)
        field.tick(idle_set)

        if tick % MEASURE_EVERY == 0:
            p_com = planet.com(g)
            rows.append({
                'tick': tick,
                'dist': float(np.linalg.norm(p_com - star_com)),
                'px': p_com[0], 'py': p_com[1], 'pz': p_com[2],
            })

    elapsed = time.time() - t0
    # Compute total angle
    total_abs = 0.0
    total_net = 0.0
    for i in range(1, len(rows)):
        da = angular_displacement_2d(
            np.array([rows[i-1]['px'], rows[i-1]['py'], rows[i-1]['pz']]),
            np.array([rows[i]['px'], rows[i]['py'], rows[i]['pz']]),
            star_com)
        total_net += da
        total_abs += abs(da)

    print(f"  Done ({elapsed:.1f}s). net={np.degrees(total_net):.1f} deg  "
          f"total={np.degrees(total_abs):.1f} deg")

    plot_diagnostic_orbit(rows, star_com, initial_dist, "D4: Frozen Star",
                          "d4_frozen_star.png")
    return np.degrees(total_net), np.degrees(total_abs)


# ═══════════════════════════════════════════════════════════
# D5: NO PLANET DEPOSIT
# ═══════════════════════════════════════════════════════════

def run_no_planet_deposit():
    """Planet routes but doesn't deposit. Only star deposits."""
    print(f"\n{'=' * 60}")
    print(f"D5: NO PLANET DEPOSIT ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    g, star, fwd, field, star_com, star_r, rng = build_world()

    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)
    initial_dist = float(np.linalg.norm(planet.com(g) - star_com))
    print(f"  Planet dist={initial_dist:.2f}. Planet deposits DISABLED.")

    rows = []
    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        # Star ticks normally
        star_events = star.tick(g, rng)
        idle_set = star.idle_node_set()
        for em in star_events:
            field.process_emission(em.group, em.src_node, em.dest_node, g, idle_set)

        # Planet ticks but discard its emissions (no deposits)
        planet.tick(g, rng)  # routes and hops, but emissions are thrown away

        field.tick(idle_set)

        if tick % MEASURE_EVERY == 0:
            p_com = planet.com(g)
            rows.append({
                'tick': tick,
                'dist': float(np.linalg.norm(p_com - star_com)),
                'px': p_com[0], 'py': p_com[1], 'pz': p_com[2],
            })

    elapsed = time.time() - t0
    total_abs = 0.0
    total_net = 0.0
    for i in range(1, len(rows)):
        da = angular_displacement_2d(
            np.array([rows[i-1]['px'], rows[i-1]['py'], rows[i-1]['pz']]),
            np.array([rows[i]['px'], rows[i]['py'], rows[i]['pz']]),
            star_com)
        total_net += da
        total_abs += abs(da)

    print(f"  Done ({elapsed:.1f}s). net={np.degrees(total_net):.1f} deg  "
          f"total={np.degrees(total_abs):.1f} deg")

    plot_diagnostic_orbit(rows, star_com, initial_dist,
                          "D5: No Planet Deposit", "d5_no_planet_deposit.png")
    return np.degrees(total_net), np.degrees(total_abs)


# ═══════════════════════════════════════════════════════════
# NORMAL INSTRUMENTED RUN (D1, D2, D6)
# ═══════════════════════════════════════════════════════════

def run_instrumented():
    """Full v9 run with per-hop routing decomposition."""
    print(f"\n{'=' * 60}")
    print(f"D1/D2/D6: INSTRUMENTED RUN ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    g, star, fwd, field, star_com, star_r, rng = build_world()

    planet_ids = place_planet_cluster(g, star_com, star_r, PLANET_COUNT)
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}
    planet = Entity("planet", planet_ids, planet_groups, planet_spectrum)
    initial_dist = float(np.linalg.norm(planet.com(g) - star_com))
    print(f"  Planet dist={initial_dist:.2f}. Full instrumentation.")

    hop_log = []  # per-hop records
    rows = []     # per-interval records

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        # Capture planet state BEFORE tick for hop detection
        prev_nodes = {en: en.node for en in planet.entity_nodes}
        prev_transit = {en: en.in_transit for en in planet.entity_nodes}

        star_events = star.tick(g, rng)
        planet_events = planet.tick(g, rng)

        idle_set = star.idle_node_set() | planet.idle_node_set()
        for em in star_events + planet_events:
            field.process_emission(em.group, em.src_node, em.dest_node, g, idle_set)
        field.tick(idle_set)

        # Detect planet hops (node changed and was previously in transit completing)
        for en in planet.entity_nodes:
            if prev_transit[en] and not en.in_transit and en.node != prev_nodes[en]:
                # A hop just completed — log the routing decision
                s_com = star.com(g)
                p_pos = g.pos[en.node]
                dist = np.linalg.norm(p_pos - s_com)

                # The node just arrived and made a routing decision (if it emitted)
                # We can infer the chosen direction from the emission
                for em in planet_events:
                    if em.src_node == en.node:
                        chosen_pos = g.pos[em.dest_node]
                        hop_dir = chosen_pos - p_pos
                        hop_len = np.linalg.norm(hop_dir)
                        if hop_len > 1e-10:
                            hop_dir /= hop_len

                        radial_dir = s_com - p_pos
                        radial_len = np.linalg.norm(radial_dir)
                        if radial_len > 1e-10:
                            radial_dir /= radial_len

                        radial_comp = np.dot(hop_dir, radial_dir)
                        cross = np.cross(radial_dir, hop_dir)
                        tang_mag = np.linalg.norm(cross)

                        # Score info
                        nbrs = g.neighbors(en.node)
                        scores = []
                        for nb in nbrs:
                            c = g.edge(en.node, nb)
                            scores.append(sum(c.deposits.get(gg, 0)
                                              for gg in en.spectrum))
                        scores.sort(reverse=True)

                        hop_log.append({
                            'tick': tick,
                            'distance': dist,
                            'radial_component': radial_comp,
                            'tangential_magnitude': tang_mag,
                            'best_score': scores[0] if scores else 0,
                            'second_score': scores[1] if len(scores) > 1 else 0,
                            'margin': (scores[0] - scores[1]) / max(1, scores[0])
                                      if len(scores) > 1 else 1.0,
                        })
                        break

        if tick % MEASURE_EVERY == 0:
            p_com = planet.com(g)
            rows.append({
                'tick': tick,
                'dist': float(np.linalg.norm(p_com - star.com(g))),
                'px': p_com[0], 'py': p_com[1], 'pz': p_com[2],
            })

    elapsed = time.time() - t0
    print(f"  Done ({elapsed:.1f}s). {len(hop_log)} hops logged.")

    # Save hop log
    if hop_log:
        csv_path = os.path.join(OUT, "d1_hop_log.csv")
        with open(csv_path, 'w', newline='') as f:
            w = csv.DictWriter(f, fieldnames=hop_log[0].keys())
            w.writeheader()
            w.writerows(hop_log)

    # Compute total angle
    total_net = 0.0
    total_abs = 0.0
    s_com = star_com
    for i in range(1, len(rows)):
        da = angular_displacement_2d(
            np.array([rows[i-1]['px'], rows[i-1]['py'], rows[i-1]['pz']]),
            np.array([rows[i]['px'], rows[i]['py'], rows[i]['pz']]), s_com)
        total_net += da
        total_abs += abs(da)
    print(f"  Angle: net={np.degrees(total_net):.1f}  total={np.degrees(total_abs):.1f}")

    # Plots
    plot_instrumented(hop_log, rows, star_com, initial_dist)
    return hop_log, np.degrees(total_net), np.degrees(total_abs)


def plot_diagnostic_orbit(rows, star_com, initial_dist, title, filename):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle(title, fontsize=14)

    ticks = [r['tick'] for r in rows]
    ax1.plot(ticks, [r['dist'] for r in rows], 'b-', linewidth=0.8)
    ax1.axhline(initial_dist, color='r', linestyle='--', alpha=0.5)
    ax1.set_ylabel('Distance'); ax1.set_title('Planet-Star Distance'); ax1.grid(True, alpha=0.3)

    px = [r['px'] for r in rows]; py = [r['py'] for r in rows]
    n = len(px)
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax2.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax2.plot(px[0], py[0], 'go', markersize=8)
    ax2.plot(px[-1], py[-1], 'ro', markersize=8)
    ax2.plot(star_com[0], star_com[1], 'y*', markersize=15)
    ax2.set_aspect('equal'); ax2.set_title('Trajectory (XY)'); ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, filename), dpi=150)
    plt.close()
    print(f"  Saved: {filename}")


def plot_instrumented(hop_log, rows, star_com, initial_dist):
    if not hop_log:
        return

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('D1/D2/D6: Per-Hop Routing Analysis', fontsize=14)

    hl_ticks = [h['tick'] for h in hop_log]
    radials = [h['radial_component'] for h in hop_log]
    tangs = [h['tangential_magnitude'] for h in hop_log]
    margins = [h['margin'] for h in hop_log]
    dists = [h['distance'] for h in hop_log]

    # D1: Radial component per hop
    ax = axes[0, 0]
    ax.scatter(hl_ticks, radials, s=1, alpha=0.3, c='blue')
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('Radial component'); ax.set_title('D1: Radial Component per Hop')
    ax.grid(True, alpha=0.3)

    # D1: Tangential magnitude per hop
    ax = axes[0, 1]
    ax.scatter(hl_ticks, tangs, s=1, alpha=0.3, c='green')
    ax.set_ylabel('Tangential magnitude'); ax.set_title('D1: Tangential Magnitude per Hop')
    ax.grid(True, alpha=0.3)

    # D2: Cumulative tangential (from orbit rows)
    ax = axes[0, 2]
    cum = [0]
    for i in range(1, len(rows)):
        da = angular_displacement_2d(
            np.array([rows[i-1]['px'], rows[i-1]['py'], rows[i-1]['pz']]),
            np.array([rows[i]['px'], rows[i]['py'], rows[i]['pz']]), star_com)
        cum.append(cum[-1] + da)
    ax.plot([r['tick'] for r in rows], np.degrees(cum), 'g-', linewidth=0.8)
    ax.set_ylabel('Cumulative angle (deg)'); ax.set_title('D2: Angular Accumulation')
    ax.grid(True, alpha=0.3)

    # D6: Score margin histogram
    ax = axes[1, 0]
    ax.hist(margins, bins=50, alpha=0.7)
    ax.set_xlabel('Margin (best-second)/best'); ax.set_ylabel('Count')
    ax.set_title('D6: Score Margin'); ax.grid(True, alpha=0.3)

    # Radial component vs distance
    ax = axes[1, 1]
    ax.scatter(dists, radials, s=1, alpha=0.3)
    ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_xlabel('Distance from star'); ax.set_ylabel('Radial component')
    ax.set_title('Radial Component vs Distance'); ax.grid(True, alpha=0.3)

    # Tangential vs distance
    ax = axes[1, 2]
    ax.scatter(dists, tangs, s=1, alpha=0.3, c='green')
    ax.set_xlabel('Distance from star'); ax.set_ylabel('Tangential magnitude')
    ax.set_title('Tangential vs Distance'); ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(os.path.join(OUT, "d1_d2_d6_instrumented.png"), dpi=150)
    plt.close()
    print(f"  Saved: d1_d2_d6_instrumented.png")


def run_all():
    """Run all diagnostics and produce summary."""
    print("=" * 60)
    print("DIAGNOSTIC SUITE: Tangential Motion Analysis")
    print("=" * 60)

    # D3 first — most decisive
    rw_results = run_random_walk(n_trials=20)

    # D4: Frozen star
    d4_net, d4_total = run_frozen_star()

    # D5: No planet deposit
    d5_net, d5_total = run_no_planet_deposit()

    # Normal instrumented
    hop_log, d_net, d_total = run_instrumented()

    # Summary
    rw_nets = [r['net_degrees'] for r in rw_results]
    rw_totals = [r['total_degrees'] for r in rw_results]

    print(f"\n{'=' * 60}")
    print("DIAGNOSTIC SUMMARY")
    print(f"{'=' * 60}\n")
    print(f"  {'Test':<25} {'Net (deg)':>12} {'Total (deg)':>12}")
    print(f"  {'-'*25} {'-'*12} {'-'*12}")
    print(f"  {'v9 normal (reference)':<25} {'474':>12} {'2254':>12}")
    print(f"  {'D3 random walk (mean)':<25} {np.mean(rw_nets):>12.1f} {np.mean(rw_totals):>12.1f}")
    print(f"  {'D3 random walk (std)':<25} {np.std(rw_nets):>12.1f} {np.std(rw_totals):>12.1f}")
    print(f"  {'D4 frozen star':<25} {d4_net:>12.1f} {d4_total:>12.1f}")
    print(f"  {'D5 no planet deposit':<25} {d5_net:>12.1f} {d5_total:>12.1f}")
    print(f"  {'Instrumented':<25} {d_net:>12.1f} {d_total:>12.1f}")

    # Decision table
    rw_similar = np.mean(rw_totals) > 1500  # within ~30% of v9's 2254
    print(f"\n  D3 random walk ~ orbit? {'YES' if rw_similar else 'NO'}")
    if rw_similar:
        print(f"  --> Graph topology alone explains tangential motion.")
        print(f"  --> Deposits and routing are irrelevant for tangential component.")
    else:
        print(f"  D4 frozen ~ orbit? {'YES' if d4_total > 1500 else 'NO'}")
        print(f"  D5 no-deposit ~ orbit? {'YES' if d5_total > 1500 else 'NO'}")

    # Save summary
    with open(os.path.join(OUT, "diagnostic_summary.txt"), 'w') as f:
        f.write("Diagnostic Summary\n")
        f.write(f"v9 reference: net=474, total=2254\n")
        f.write(f"D3 random walk: net={np.mean(rw_nets):.1f}+/-{np.std(rw_nets):.1f}, "
                f"total={np.mean(rw_totals):.1f}+/-{np.std(rw_totals):.1f}\n")
        f.write(f"D4 frozen star: net={d4_net:.1f}, total={d4_total:.1f}\n")
        f.write(f"D5 no planet dep: net={d5_net:.1f}, total={d5_total:.1f}\n")
        f.write(f"Instrumented: net={d_net:.1f}, total={d_total:.1f}\n")


if __name__ == '__main__':
    if '--all' in sys.argv:
        run_all()
    elif '--random-walk' in sys.argv:
        run_random_walk()
    elif '--frozen-star' in sys.argv:
        run_frozen_star()
    elif '--no-planet-deposit' in sys.argv:
        run_no_planet_deposit()
    else:
        run_all()
