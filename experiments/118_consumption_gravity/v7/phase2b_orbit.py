#!/usr/bin/env python3
"""
Experiment 118 v7 -- Phase 2b: Orbital Test

Planet placed at Euclidean distance ~18 from STAR COM (not origin).
Initial tangential kick: 2-3 planet nodes start IN_TRANSIT on connectors
perpendicular to star-planet radial direction. 200k tick run.

Key questions:
  1. Does tangential motion persist or dissipate?
  2. Does the trajectory trace an orbit?
  3. Do star-facing connectors grow faster at this distance?
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
from entity import Entity, EntityNode, BASE_WEIGHT

# ── Configuration ──────────────────────────────────────────────
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
LOG_EVERY = 20000

PLANET_TARGET_DIST = 18.0  # from star COM, not origin

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class PlanetNode(EntityNode):
    """Planet node routing on TOTAL deposit count."""

    def tick(self, graph, rng):
        if self.in_transit:
            self.transit_remaining -= 1
            if self.transit_remaining <= 0:
                graph.connectors[self.transit_edge].append(self.group)
                self.node = self.transit_dest
                self.in_transit = False
                self.transit_edge = None
                self.transit_dest = None
                self.hops_completed += 1
            return

        nbrs = graph.neighbors(self.node)
        if not nbrs:
            return

        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            scores[i] = c.total

        weights = scores + BASE_WEIGHT
        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nb = nbrs[chosen_idx]

        edge_key = (min(self.node, chosen_nb), max(self.node, chosen_nb))
        c = graph.connectors[edge_key]
        traverse_time = max(1, int(c.length))

        self.in_transit = True
        self.transit_edge = edge_key
        self.transit_dest = chosen_nb
        self.transit_remaining = traverse_time

        c.append(self.group)
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            self.node = self.transit_dest
            self.in_transit = False
            self.transit_edge = None
            self.transit_dest = None
            self.hops_completed += 1


class Planet:
    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            PlanetNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick(self, graph, rng):
        for en in self.entity_nodes:
            en.tick(graph, rng)

    def node_indices(self):
        return [en.node for en in self.entity_nodes]

    def com(self, graph):
        return graph.pos[self.node_indices()].mean(axis=0)

    def mean_radius(self, graph):
        center = self.com(graph)
        dists = np.linalg.norm(graph.pos[self.node_indices()] - center, axis=1)
        return float(np.mean(dists))

    def idle_fraction(self):
        return sum(1 for en in self.entity_nodes if not en.in_transit) / len(self.entity_nodes)

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def connector_stats_by_direction(self, graph, star_com):
        star_facing = []
        other = []
        for en in self.entity_nodes:
            planet_pos = graph.pos[en.node]
            planet_dist = np.linalg.norm(planet_pos - star_com)
            for nb in graph.neighbors(en.node):
                nb_dist = np.linalg.norm(graph.pos[nb] - star_com)
                c = graph.edge(en.node, nb)
                if nb_dist < planet_dist:
                    star_facing.append(c.length)
                else:
                    other.append(c.length)
        return star_facing, other


def seed_tangential_kick(planet, graph, star_com):
    """Set 3 of 5 planet nodes to IN_TRANSIT on tangential connectors.

    For each node, find the neighbor whose direction from the planet node
    is most perpendicular to the star-planet radial direction.
    """
    kicked = 0
    for en in planet.entity_nodes:
        if kicked >= 3:
            break

        planet_pos = graph.pos[en.node]
        radial = planet_pos - star_com
        radial_len = np.linalg.norm(radial)
        if radial_len < 1e-10:
            continue
        radial /= radial_len

        # Find most tangential neighbor
        best_nb = None
        best_perp = -1.0
        for nb in graph.neighbors(en.node):
            nb_dir = graph.pos[nb] - planet_pos
            nb_len = np.linalg.norm(nb_dir)
            if nb_len < 1e-10:
                continue
            nb_dir /= nb_len
            # Perpendicularity = |sin(angle)| = |cross product magnitude|
            cross = np.linalg.norm(np.cross(radial, nb_dir))
            if cross > best_perp:
                best_perp = cross
                best_nb = nb

        if best_nb is None:
            continue

        # Start traversal on this tangential connector
        edge_key = (min(en.node, best_nb), max(en.node, best_nb))
        c = graph.connectors[edge_key]
        traverse_time = max(1, int(c.length))

        en.in_transit = True
        en.transit_edge = edge_key
        en.transit_dest = best_nb
        en.transit_remaining = traverse_time

        c.append(en.group)
        en.transit_remaining -= 1
        if en.transit_remaining <= 0:
            en.node = en.transit_dest
            en.in_transit = False
            en.transit_edge = None
            en.transit_dest = None
            en.hops_completed += 1

        kicked += 1
        print(f"  Kicked node {en.node} -> {best_nb} (perp={best_perp:.3f}, "
              f"traverse={traverse_time} ticks)")

    print(f"  Tangential kick applied to {kicked} nodes")


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # ── Star ──
    star_node_ids = g.nearest_to_origin(STAR_COUNT)
    star_groups = [f"s{i % STAR_GROUPS}" for i in range(STAR_COUNT)]
    star_spectrum = {f"s{i}" for i in range(STAR_GROUPS)}
    star = Entity("star", star_node_ids, star_groups, star_spectrum)

    print(f"Star: {STAR_COUNT} nodes, initial mean_r={star.mean_radius(g):.2f}")

    # ── Warmup ──
    print(f"\n{'=' * 60}")
    print(f"WARMUP: Star equilibration ({WARMUP_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, WARMUP_TICKS + 1):
        star.tick(g, rng)
        if tick % (WARMUP_TICKS // 5) == 0:
            elapsed = time.time() - t0
            print(f"  t={tick:7d}  mean_r={star.mean_radius(g):.2f}  "
                  f"hops={star.total_hops()}  ({tick/elapsed:.0f} t/s)")

    star_com = star.com(g)
    print(f"\nStar equilibrated: COM=[{star_com[0]:.2f}, {star_com[1]:.2f}, "
          f"{star_com[2]:.2f}], mean_r={star.mean_radius(g):.2f}")

    # ── Place planet at distance ~18 from STAR COM ──
    dists_from_star = np.linalg.norm(g.pos - star_com, axis=1)
    candidates = np.argsort(np.abs(dists_from_star - PLANET_TARGET_DIST))
    planet_node_ids = candidates[:PLANET_COUNT].tolist()
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}

    planet = Planet("planet", planet_node_ids, planet_groups, planet_spectrum)
    p_com = planet.com(g)
    initial_dist = float(np.linalg.norm(p_com - star_com))

    print(f"\nPlanet: {PLANET_COUNT} nodes")
    print(f"  COM=[{p_com[0]:.2f}, {p_com[1]:.2f}, {p_com[2]:.2f}]")
    print(f"  Distance from star COM: {initial_dist:.2f}")

    # ── Tangential kick ──
    print(f"\nApplying tangential kick...")
    seed_tangential_kick(planet, g, star_com)

    # ── Simulation ──
    rows = []
    print(f"\n{'=' * 60}")
    print(f"PHASE 2b: Orbital Test ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        star.tick(g, rng)
        planet.tick(g, rng)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com(g)
            p_com = planet.com(g)
            dist = float(np.linalg.norm(p_com - s_com))

            sf_lens, ot_lens = planet.connector_stats_by_direction(g, s_com)
            sf_mean = float(np.mean(sf_lens)) if sf_lens else 0
            sf_max = float(np.max(sf_lens)) if sf_lens else 0
            ot_mean = float(np.mean(ot_lens)) if ot_lens else 0
            ot_max = float(np.max(ot_lens)) if ot_lens else 0

            rows.append({
                'tick': tick,
                'planet_star_dist': dist,
                'planet_x': p_com[0], 'planet_y': p_com[1], 'planet_z': p_com[2],
                'star_x': s_com[0], 'star_y': s_com[1], 'star_z': s_com[2],
                'star_mean_r': star.mean_radius(g),
                'planet_mean_r': planet.mean_radius(g),
                'planet_idle': planet.idle_fraction(),
                'planet_hops': planet.total_hops(),
                'sf_conn_mean': sf_mean,
                'sf_conn_max': sf_max,
                'sf_conn_count': len(sf_lens),
                'other_conn_mean': ot_mean,
                'other_conn_max': ot_max,
                'other_conn_count': len(ot_lens),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            sf_ratio = r['sf_conn_mean'] / r['other_conn_mean'] if r['other_conn_mean'] > 0 else 0
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
                  f"sf={r['sf_conn_mean']:.0f}/{r['sf_conn_max']:.0f}  "
                  f"ot={r['other_conn_mean']:.0f}/{r['other_conn_max']:.0f}  "
                  f"sf/ot={sf_ratio:.2f}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {SIM_TICKS} ticks in {elapsed:.1f}s ({SIM_TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "phase2b_results.csv")
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
    max_dist = max(dists)

    # 1. Attraction
    status1 = "PASS" if min_dist < initial_dist * 0.7 else "FAIL"
    print(f"  1. Attraction: initial={initial_dist:.2f}  min={min_dist:.2f}  [{status1}]")

    # 2. Binding
    escaped = dists[-1] > initial_dist * 1.5
    status2 = "PASS" if not escaped else "FAIL"
    print(f"  2. Bound: final={dists[-1]:.2f}  escaped={escaped}  [{status2}]")

    # 3. Star-facing growth
    last_rows = [r for r in rows if r['tick'] > SIM_TICKS * 0.5]
    if last_rows:
        sf = np.mean([r['sf_conn_mean'] for r in last_rows])
        ot = np.mean([r['other_conn_mean'] for r in last_rows])
        ratio = sf / ot if ot > 0 else 0
        status3 = "PASS" if ratio > 1.3 else "FAIL"
        print(f"  3. Star-facing growth: sf={sf:.1f}  other={ot:.1f}  "
              f"ratio={ratio:.2f}  [{status3}]")

    # 4. Tangential motion
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angles.append(np.arctan2(cross, dot))
    total_angle = sum(angles)  # signed — net rotation
    total_abs = sum(abs(a) for a in angles)
    status4 = "PASS" if total_abs > np.pi else "FAIL"
    print(f"  4. Tangential: net={np.degrees(total_angle):.1f} deg  "
          f"total={np.degrees(total_abs):.1f} deg  [{status4}]")

    # 5. Oscillation count
    crossings = 0
    mean_dist = np.mean(dists)
    for i in range(1, len(dists)):
        if (dists[i-1] < mean_dist) != (dists[i] < mean_dist):
            crossings += 1
    n_oscillations = crossings / 2
    print(f"  5. Oscillations: ~{n_oscillations:.1f} (crossings={crossings})")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v7 -- Phase 2b: Orbital Test (tangential kick)',
                 fontsize=14)

    # 1. Distance
    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5,
               label=f'initial={initial_dist:.1f}')
    ax.set_ylabel('Distance')
    ax.set_title('Planet-Star Distance')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. XY trajectory
    ax = axes[0, 1]
    px = [r['planet_x'] for r in rows]
    py = [r['planet_y'] for r in rows]
    sx = [r['star_x'] for r in rows]
    sy = [r['star_y'] for r in rows]
    # Color by time
    n = len(px)
    colors = plt.cm.viridis(np.linspace(0, 1, n))
    for i in range(1, n):
        ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], py[0], 'go', markersize=10, label='start')
    ax.plot(px[-1], py[-1], 'ro', markersize=10, label='end')
    ax.plot(np.mean(sx), np.mean(sy), 'y*', markersize=15, label='star')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Trajectory (XY, colored by time)')
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # 3. XZ trajectory
    ax = axes[0, 2]
    pz = [r['planet_z'] for r in rows]
    for i in range(1, n):
        ax.plot(px[i-1:i+1], pz[i-1:i+1], '-', color=colors[i], linewidth=0.8)
    ax.plot(px[0], pz[0], 'go', markersize=10, label='start')
    ax.plot(px[-1], pz[-1], 'ro', markersize=10, label='end')
    ax.set_xlabel('X')
    ax.set_ylabel('Z')
    ax.set_title('Trajectory (XZ)')
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # 4. Connector lengths
    ax = axes[1, 0]
    ax.plot(ticks, [r['sf_conn_mean'] for r in rows], 'r-', linewidth=0.8,
            label='star-facing')
    ax.plot(ticks, [r['other_conn_mean'] for r in rows], 'g-', linewidth=0.8,
            label='other')
    ax.set_ylabel('Mean length')
    ax.set_title('Planet Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 5. SF/other ratio
    ax = axes[1, 1]
    ratios = [r['sf_conn_mean'] / r['other_conn_mean']
              if r['other_conn_mean'] > 0 else 0 for r in rows]
    ax.plot(ticks, ratios, 'purple', linewidth=0.8)
    ax.axhline(1.0, color='k', linestyle='--', alpha=0.3)
    ax.set_ylabel('Ratio')
    ax.set_title('Star-Facing / Other Ratio')
    ax.grid(True, alpha=0.3)

    # 6. Star radius stability
    ax = axes[1, 2]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Radius')
    ax.set_title('Star Mean Radius')
    ax.grid(True, alpha=0.3)

    # 7. Radial velocity
    ax = axes[2, 0]
    if len(rows) > 1:
        v_rad = []
        for i in range(1, len(rows)):
            dt = rows[i]['tick'] - rows[i-1]['tick']
            dd = rows[i]['planet_star_dist'] - rows[i-1]['planet_star_dist']
            v_rad.append(dd / dt * 1000 if dt > 0 else 0)
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.5, alpha=0.7)
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('dr / 1000 ticks')
    ax.set_xlabel('Tick')
    ax.set_title('Radial Velocity')
    ax.grid(True, alpha=0.3)

    # 8. Angular position over time
    ax = axes[2, 1]
    cum_angle = [0]
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0, v1 = p0 - s, p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        cum_angle.append(cum_angle[-1] + np.arctan2(cross, dot))
    ax.plot(ticks, np.degrees(cum_angle), 'g-', linewidth=0.8)
    ax.set_ylabel('Cumulative angle (deg)')
    ax.set_xlabel('Tick')
    ax.set_title('Angular Position')
    ax.grid(True, alpha=0.3)

    # 9. Planet hops
    ax = axes[2, 2]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Cumulative hops')
    ax.set_xlabel('Tick')
    ax.set_title('Planet Total Hops')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2b_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
