#!/usr/bin/env python3
"""
Experiment 128 v1 — Phase 1: Deposit Patterns on a Graph

No entity hopping. Entities are REGIONS defined by deposit dominance.
Star deposits propagate outward from center. Planet deposits propagate
inward from a fixed position. Where they meet: consumption.

The boundary between star-dominant and planet-dominant regions IS the
"orbital distance." It should equilibrate from geometric dilution:
star flux ~ 1/r^2 at planet's position, balanced by planet's local rate.

No routing. No hopping. No entity nodes. Just deposits propagating
on a fixed graph, consuming each other at the boundary.
"""

import os
import time
import numpy as np
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# graph.py has Connector with star/planet deposit methods + consumption

SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24

STAR_CENTER = None       # nearest to origin (set after graph build)
STAR_RADIUS_NODES = 10   # star = 10 nodes nearest to origin (emission sources)
PLANET_DISTANCE = 12.0   # Euclidean distance from origin for planet source
PLANET_RADIUS_NODES = 3  # planet = 3 nodes near target distance

STAR_RATE = 1             # deposits per tick per star source node
PLANET_RATE = 1           # deposits per tick per planet source node

TICKS = 5000
MEASURE_EVERY = 100
LOG_EVERY = 500

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class ForwardTable:
    """Precomputed forward-continuation for deposit propagation."""

    def __init__(self, graph):
        self._table = {}
        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                incoming_dir = pos[node] - pos[nb]
                il = np.linalg.norm(incoming_dir)
                if il < 1e-15:
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._table[(nb, node)] = others[0] if others else nb
                    continue
                incoming_dir /= il
                best, best_dot = nb, -2.0
                for n2 in graph.neighbors(node):
                    if n2 == nb:
                        continue
                    od = pos[n2] - pos[node]
                    ol = np.linalg.norm(od)
                    if ol < 1e-15:
                        continue
                    d = np.dot(incoming_dir, od / ol)
                    if d > best_dot:
                        best_dot = d
                        best = n2
                self._table[(nb, node)] = best
        print(f"  Forward table: {len(self._table)} entries")

    def next_node(self, from_node, at_node):
        return self._table.get((from_node, at_node), at_node)


class PropQuantum:
    """A propagating deposit quantum."""
    __slots__ = ('family', 'node', 'from_node', 'age')

    def __init__(self, family, node, from_node):
        self.family = family
        self.node = node
        self.from_node = from_node
        self.age = 0


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


def boundary_analysis(graph, center, hop_dist):
    """Find the boundary: for each hop distance, is it star or planet dominant?"""
    by_dist = {}
    seen = set()
    for (i, j), c in graph.connectors.items():
        if (i, j) in seen:
            continue
        seen.add((i, j))
        d = min(hop_dist[i], hop_dist[j])
        if d < 0:
            continue
        net = c.star_deposits - c.planet_deposits
        by_dist.setdefault(d, []).append(net)

    result = {}
    for d in sorted(by_dist.keys()):
        vals = by_dist[d]
        result[d] = {
            'mean_net': float(np.mean(vals)),
            'star_dominant_frac': float(np.mean([1 if v > 0 else 0 for v in vals])),
            'mean_star': float(np.mean([max(0, v) for v in vals])),
            'n_connectors': len(vals),
        }
    return result


def run():
    t_start = time.time()

    print("Building graph...")
    from graph import Graph
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)

    print("Building forward table...")
    fwd = ForwardTable(g)
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # Star source nodes: nearest to origin
    center = g.nearest_to_origin(1)[0]
    star_sources = g.nearest_to_origin(STAR_RADIUS_NODES)
    hop_dist = bfs_distances(g, center)

    # Planet source nodes: cluster near target distance
    dists = np.linalg.norm(g.pos - g.pos[center], axis=1)
    planet_candidates = np.argsort(np.abs(dists - PLANET_DISTANCE))
    planet_seed = planet_candidates[0]
    # Cluster: seed + nearest neighbors
    nb_dists = np.linalg.norm(g.pos - g.pos[planet_seed], axis=1)
    nb_dists[planet_seed] = np.inf
    planet_sources = [planet_seed] + np.argsort(nb_dists)[:PLANET_RADIUS_NODES-1].tolist()

    star_com = g.pos[star_sources].mean(axis=0)
    planet_com = g.pos[planet_sources].mean(axis=0)
    initial_dist = np.linalg.norm(planet_com - star_com)

    print(f"Star: {len(star_sources)} source nodes near origin")
    print(f"Planet: {len(planet_sources)} source nodes at r~{PLANET_DISTANCE}")
    print(f"Initial distance: {initial_dist:.2f}")
    print(f"Star rate: {STAR_RATE * len(star_sources)}/tick total")
    print(f"Planet rate: {PLANET_RATE * len(planet_sources)}/tick total")

    # Propagation
    quanta = []
    rows = []
    MAX_AGE = 50  # quanta expire after 50 hops

    print(f"\n{'=' * 60}")
    print(f"PHASE 1: Deposit Pattern Propagation ({TICKS} ticks)")
    print(f"{'=' * 60}\n")

    t0 = time.time()
    for tick in range(1, TICKS + 1):
        # Star emits from each source node
        for sn in star_sources:
            for _ in range(STAR_RATE):
                # Emit in a random outgoing direction
                nbrs = g.neighbors(sn)
                if nbrs:
                    nb = nbrs[np.random.randint(len(nbrs))]
                    quanta.append(PropQuantum('star', sn, sn))
                    # First deposit on the source connector
                    ek = g.edge_key(sn, nb)
                    g.connectors[ek].deposit_star()
                    quanta[-1].node = nb
                    quanta[-1].from_node = sn

        # Planet emits from each source node
        for pn in planet_sources:
            for _ in range(PLANET_RATE):
                nbrs = g.neighbors(pn)
                if nbrs:
                    nb = nbrs[np.random.randint(len(nbrs))]
                    quanta.append(PropQuantum('planet', pn, pn))
                    ek = g.edge_key(pn, nb)
                    g.connectors[ek].deposit_planet()
                    quanta[-1].node = nb
                    quanta[-1].from_node = pn

        # Propagate all quanta
        surviving = []
        for q in quanta:
            q.age += 1
            if q.age > MAX_AGE:
                continue

            next_node = fwd.next_node(q.from_node, q.node)
            ek = g.edge_key(q.node, next_node)

            if ek not in g.connectors:
                continue

            # Deposit on traversed connector
            if q.family == 'star':
                g.connectors[ek].deposit_star()
            else:
                g.connectors[ek].deposit_planet()

            q.from_node = q.node
            q.node = next_node
            surviving.append(q)

        quanta = surviving

        if tick % MEASURE_EVERY == 0:
            ba = boundary_analysis(g, center, hop_dist)
            # Find boundary: last hop distance where star is dominant
            boundary_hop = 0
            for d in sorted(ba.keys()):
                if ba[d]['star_dominant_frac'] > 0.5:
                    boundary_hop = d

            total_consumed = sum(c.consumed_count for c in g.connectors.values())
            total_star = sum(c.star_deposits for c in g.connectors.values())
            total_planet = sum(c.planet_deposits for c in g.connectors.values())

            rows.append({
                'tick': tick,
                'boundary_hop': boundary_hop,
                'total_star': total_star,
                'total_planet': total_planet,
                'total_consumed': total_consumed,
                'active_quanta': len(quanta),
            })

        if tick % LOG_EVERY == 0:
            elapsed = time.time() - t0
            r = rows[-1]
            print(f"  t={tick:5d}  boundary={r['boundary_hop']}  "
                  f"star={r['total_star']}  planet={r['total_planet']}  "
                  f"consumed={r['total_consumed']}  quanta={r['active_quanta']}  "
                  f"({tick/elapsed:.0f} t/s)")

    elapsed = time.time() - t0
    print(f"\nDone: {TICKS} ticks in {elapsed:.1f}s ({TICKS/elapsed:.0f} t/s)")

    ba = boundary_analysis(g, center, hop_dist)
    analyze(rows, ba, initial_dist)
    plot(rows, ba, g, center, hop_dist)


def analyze(rows, ba, initial_dist):
    print(f"\n{'=' * 60}")
    print("ANALYSIS")
    print(f"{'=' * 60}\n")

    # Boundary
    late = [r for r in rows if r['tick'] > TICKS * 0.5]
    if late:
        mean_b = np.mean([r['boundary_hop'] for r in late])
        print(f"  Boundary (hop distance, late): {mean_b:.1f}")

    # Deposit profile
    print(f"\n  Deposit dominance by hop distance:")
    print(f"  {'Hop':>4} {'MeanNet':>10} {'StarFrac':>10} {'Connectors':>10}")
    for d in sorted(ba.keys()):
        b = ba[d]
        print(f"  {d:>4d} {b['mean_net']:>10.1f} {b['star_dominant_frac']:>10.3f} {b['n_connectors']:>10d}")

    # Consumption
    final = rows[-1]
    print(f"\n  Total star deposits: {final['total_star']}")
    print(f"  Total planet deposits: {final['total_planet']}")
    print(f"  Total consumed: {final['total_consumed']}")
    print()


def plot(rows, ba, graph, center, hop_dist):
    ticks = [r['tick'] for r in rows]

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    fig.suptitle('Experiment 128 v1 -- Phase 1: Deposit Patterns on Graph', fontsize=14)

    # 1. Boundary hop distance over time
    ax = axes[0, 0]
    ax.plot(ticks, [r['boundary_hop'] for r in rows], 'b-', linewidth=0.8)
    ax.set_ylabel('Boundary (hop distance)')
    ax.set_title('Star-Dominant Boundary')
    ax.grid(True, alpha=0.3)

    # 2. Star dominance fraction by hop distance
    ax = axes[0, 1]
    ds = sorted(ba.keys())
    fracs = [ba[d]['star_dominant_frac'] for d in ds]
    ax.bar(ds, fracs, color='orange', alpha=0.7)
    ax.axhline(0.5, color='r', linestyle='--', alpha=0.5, label='50% boundary')
    ax.set_xlabel('Hop distance from center')
    ax.set_ylabel('Fraction star-dominant')
    ax.set_title('Star Dominance vs Distance')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 3. Mean net deposit by hop distance
    ax = axes[0, 2]
    nets = [ba[d]['mean_net'] for d in ds]
    colors = ['orange' if n > 0 else 'blue' for n in nets]
    ax.bar(ds, nets, color=colors, alpha=0.7)
    ax.axhline(0, color='k', linewidth=0.5)
    ax.set_xlabel('Hop distance')
    ax.set_ylabel('Mean (star - planet) deposits')
    ax.set_title('Net Deposit Profile')
    ax.grid(True, alpha=0.3)

    # 4. Cumulative deposits
    ax = axes[1, 0]
    ax.plot(ticks, [r['total_star'] for r in rows], 'orange', linewidth=0.8, label='Star')
    ax.plot(ticks, [r['total_planet'] for r in rows], 'blue', linewidth=0.8, label='Planet')
    ax.set_ylabel('Total deposits')
    ax.set_title('Cumulative Deposits')
    ax.legend(); ax.grid(True, alpha=0.3)

    # 5. Consumption
    ax = axes[1, 1]
    ax.plot(ticks, [r['total_consumed'] for r in rows], 'green', linewidth=0.8)
    ax.set_ylabel('Consumed')
    ax.set_xlabel('Tick')
    ax.set_title('Cumulative Consumption')
    ax.grid(True, alpha=0.3)

    # 6. Active quanta
    ax = axes[1, 2]
    ax.plot(ticks, [r['active_quanta'] for r in rows], 'purple', linewidth=0.8)
    ax.set_ylabel('Count')
    ax.set_xlabel('Tick')
    ax.set_title('Active Quanta')
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase1_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"Saved: {png_path}")


if __name__ == '__main__':
    run()
