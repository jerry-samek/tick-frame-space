#!/usr/bin/env python3
"""
Experiment 118 v7 — Phase 2: Planet Introduction

Star pre-equilibrated from Phase 1 (100k ticks). Planet placed at
graph distance ~16 from origin. Planet routes on TOTAL deposit count
(Option A — any deposits attract, not just matching).

Key test: do star-facing connectors grow faster than others?
This would confirm the geometric bottleneck mechanism.
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

WARMUP_TICKS = 100000   # star-only equilibration
SIM_TICKS = 100000       # with planet
MEASURE_EVERY = 1000
LOG_EVERY = 10000

PLANET_DISTANCE = 16.0   # Euclidean distance from origin for placement

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class PlanetNode(EntityNode):
    """Planet node that routes on TOTAL deposit count (any group)."""

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

        # Route on TOTAL deposit count (any group — gravity)
        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            scores[i] = c.total  # total deposits, any group

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
    """Planet entity using total-count routing."""

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
        """Split planet connectors into star-facing and other.

        Star-facing: the neighbor is closer to star_com than the planet node.
        Returns (star_facing_lengths, other_lengths).
        """
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


def bfs_distance_from(graph, start):
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

    initial_star_com = star.com(g)
    print(f"Star: {STAR_COUNT} nodes, initial COM=[{initial_star_com[0]:.2f}, "
          f"{initial_star_com[1]:.2f}, {initial_star_com[2]:.2f}], "
          f"mean_r={star.mean_radius(g):.2f}")

    # ── Warmup: star only ──
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

    # ── Place planet ──
    # Find nodes near the target distance from origin
    dists_from_origin = np.linalg.norm(g.pos, axis=1)
    candidates = np.argsort(np.abs(dists_from_origin - PLANET_DISTANCE))
    planet_node_ids = candidates[:PLANET_COUNT].tolist()
    planet_groups = [f"p{i % PLANET_GROUPS}" for i in range(PLANET_COUNT)]
    planet_spectrum = {f"p{i}" for i in range(PLANET_GROUPS)}

    planet = Planet("planet", planet_node_ids, planet_groups, planet_spectrum)
    planet_initial_com = planet.com(g)
    planet_star_dist = float(np.linalg.norm(planet_initial_com - star_com))

    print(f"\nPlanet: {PLANET_COUNT} nodes at r~{PLANET_DISTANCE:.0f}")
    print(f"  COM=[{planet_initial_com[0]:.2f}, {planet_initial_com[1]:.2f}, "
          f"{planet_initial_com[2]:.2f}]")
    print(f"  Distance from star COM: {planet_star_dist:.2f}")

    # ── Simulation: star + planet ──
    rows = []
    print(f"\n{'=' * 60}")
    print(f"PHASE 2: Planet Orbit Test ({SIM_TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, SIM_TICKS + 1):
        star.tick(g, rng)
        planet.tick(g, rng)

        if tick % MEASURE_EVERY == 0:
            s_com = star.com(g)
            p_com = planet.com(g)
            dist = float(np.linalg.norm(p_com - s_com))

            # Decompose into radial and tangential
            radial_dir = (p_com - s_com)
            radial_dist = np.linalg.norm(radial_dir)
            if radial_dist > 0:
                radial_dir /= radial_dist

            sf_lens, other_lens = planet.connector_stats_by_direction(g, s_com)
            sf_mean = float(np.mean(sf_lens)) if sf_lens else 0
            sf_max = float(np.max(sf_lens)) if sf_lens else 0
            ot_mean = float(np.mean(other_lens)) if other_lens else 0
            ot_max = float(np.max(other_lens)) if other_lens else 0

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
                'other_conn_count': len(other_lens),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            tps = tick / elapsed
            r = rows[-1]
            sf_ratio = r['sf_conn_mean'] / r['other_conn_mean'] if r['other_conn_mean'] > 0 else 0
            print(f"  t={tick:7d}  dist={r['planet_star_dist']:.2f}  "
                  f"star_r={r['star_mean_r']:.2f}  "
                  f"p_idle={r['planet_idle']:.2f}  "
                  f"p_hops={r['planet_hops']}  "
                  f"sf={r['sf_conn_mean']:.0f}/{r['sf_conn_max']:.0f}  "
                  f"ot={r['other_conn_mean']:.0f}/{r['other_conn_max']:.0f}  "
                  f"sf/ot={sf_ratio:.2f}  "
                  f"({tps:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {SIM_TICKS} ticks in {elapsed:.1f}s ({SIM_TICKS/elapsed:.0f} t/s)")

    csv_path = os.path.join(OUT, "phase2_results.csv")
    with open(csv_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)
    print(f"Saved: {csv_path}")

    analyze(rows, planet_star_dist)
    plot(rows, planet_star_dist)


def analyze(rows, initial_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    dists = [r['planet_star_dist'] for r in rows]
    min_dist = min(dists)
    max_dist = max(dists)
    final_dist = dists[-1]

    # 1. Planet moves toward star
    moved_inward = min_dist < initial_dist * 0.9
    status1 = "PASS" if moved_inward else "FAIL"
    print(f"  1. Attraction: initial={initial_dist:.2f}  min={min_dist:.2f}  [{status1}]")

    # 2. Star-facing connectors grow faster
    last_rows = [r for r in rows if r['tick'] > SIM_TICKS * 0.5]
    if last_rows:
        sf = np.mean([r['sf_conn_mean'] for r in last_rows])
        ot = np.mean([r['other_conn_mean'] for r in last_rows])
        ratio = sf / ot if ot > 0 else 0
        status2 = "PASS" if ratio > 1.5 else "FAIL"
        print(f"  2. Star-facing growth: sf={sf:.1f}  other={ot:.1f}  "
              f"ratio={ratio:.2f}  [{status2}]")

    # 3. Radial oscillation (bound state)
    if len(dists) > 20:
        # Check if distance has at least one local min after initial approach
        mid = len(dists) // 3
        post_approach = dists[mid:]
        has_min = min(post_approach) < max(post_approach) * 0.8
        status3 = "PASS" if has_min and max_dist > min_dist * 1.2 else "FAIL"
        print(f"  3. Binding: min={min_dist:.2f}  max={max_dist:.2f}  "
              f"range={max_dist-min_dist:.2f}  [{status3}]")

    # 4. Any tangential motion
    # Compute angle swept around star COM
    angles = []
    for i in range(1, len(rows)):
        p0 = np.array([rows[i-1]['planet_x'], rows[i-1]['planet_y']])
        p1 = np.array([rows[i]['planet_x'], rows[i]['planet_y']])
        s = np.array([rows[i]['star_x'], rows[i]['star_y']])
        v0 = p0 - s
        v1 = p1 - s
        cross = v0[0]*v1[1] - v0[1]*v1[0]
        dot = v0[0]*v1[0] + v0[1]*v1[1]
        angle = np.arctan2(cross, dot)
        angles.append(angle)
    total_angle = abs(sum(angles))
    status4 = "PASS" if total_angle > np.pi / 4 else "FAIL"
    print(f"  4. Tangential motion: total angle swept = {np.degrees(total_angle):.1f} deg  [{status4}]")

    print()


def plot(rows, initial_dist):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(3, 3, figsize=(18, 12))
    fig.suptitle('Experiment 118 v7 -- Phase 2: Planet Orbit Test', fontsize=14)

    # 1. Planet-star distance
    ax = axes[0, 0]
    ax.plot(ticks, [r['planet_star_dist'] for r in rows], 'b-', linewidth=0.8)
    ax.axhline(initial_dist, color='r', linestyle='--', alpha=0.5, label=f'initial={initial_dist:.1f}')
    ax.set_ylabel('Distance')
    ax.set_title('Planet-Star Distance')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. 2D trajectory (XY projection)
    ax = axes[0, 1]
    ax.plot([r['planet_x'] for r in rows], [r['planet_y'] for r in rows],
            'b-', linewidth=0.5, alpha=0.7)
    ax.plot(rows[0]['planet_x'], rows[0]['planet_y'], 'go', markersize=8, label='start')
    ax.plot(rows[-1]['planet_x'], rows[-1]['planet_y'], 'ro', markersize=8, label='end')
    ax.plot([r['star_x'] for r in rows], [r['star_y'] for r in rows],
            'y-', linewidth=0.3, alpha=0.5)
    ax.plot(rows[-1]['star_x'], rows[-1]['star_y'], 'y*', markersize=12, label='star')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('Trajectory (XY)')
    ax.legend()
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.3)

    # 3. Star-facing vs other connector lengths
    ax = axes[0, 2]
    ax.plot(ticks, [r['sf_conn_mean'] for r in rows], 'r-', linewidth=0.8, label='star-facing mean')
    ax.plot(ticks, [r['other_conn_mean'] for r in rows], 'g-', linewidth=0.8, label='other mean')
    ax.set_ylabel('Length')
    ax.set_title('Planet Connector Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 4. Star-facing / other ratio
    ax = axes[1, 0]
    ratios = [r['sf_conn_mean'] / r['other_conn_mean']
              if r['other_conn_mean'] > 0 else 0 for r in rows]
    ax.plot(ticks, ratios, 'purple', linewidth=0.8)
    ax.axhline(1.0, color='k', linestyle='--', alpha=0.3)
    ax.set_ylabel('Ratio')
    ax.set_title('Star-Facing / Other Length Ratio')
    ax.grid(True, alpha=0.3)

    # 5. Star mean radius (does star stay bound?)
    ax = axes[1, 1]
    ax.plot(ticks, [r['star_mean_r'] for r in rows], 'orange', linewidth=0.8)
    ax.set_ylabel('Radius')
    ax.set_title('Star Mean Radius During Sim')
    ax.grid(True, alpha=0.3)

    # 6. Planet idle fraction
    ax = axes[1, 2]
    ax.plot(ticks, [r['planet_idle'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Fraction idle')
    ax.set_title('Planet Idle Fraction')
    ax.grid(True, alpha=0.3)

    # 7. Star-facing connector max
    ax = axes[2, 0]
    ax.plot(ticks, [r['sf_conn_max'] for r in rows], 'r-', linewidth=0.8, label='star-facing')
    ax.plot(ticks, [r['other_conn_max'] for r in rows], 'g-', linewidth=0.8, label='other')
    ax.set_ylabel('Max length')
    ax.set_xlabel('Tick')
    ax.set_title('Connector Max Lengths')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 8. Planet hops over time
    ax = axes[2, 1]
    ax.plot(ticks, [r['planet_hops'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Cumulative hops')
    ax.set_xlabel('Tick')
    ax.set_title('Planet Total Hops')
    ax.grid(True, alpha=0.3)

    # 9. Radial velocity (distance change per interval)
    ax = axes[2, 2]
    if len(rows) > 1:
        v_rad = []
        for i in range(1, len(rows)):
            dt = rows[i]['tick'] - rows[i-1]['tick']
            dd = rows[i]['planet_star_dist'] - rows[i-1]['planet_star_dist']
            v_rad.append(dd / dt * 1000 if dt > 0 else 0)
        ax.plot(ticks[1:], v_rad, 'b-', linewidth=0.5, alpha=0.7)
        ax.axhline(0, color='k', linestyle='-', alpha=0.3)
    ax.set_ylabel('Distance change / 1000 ticks')
    ax.set_xlabel('Tick')
    ax.set_title('Radial Velocity')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
