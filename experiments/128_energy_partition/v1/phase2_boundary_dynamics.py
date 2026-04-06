#!/usr/bin/env python3
"""
Experiment 128 v1 — Phase 2: Boundary Dynamics

The boundary between star-dominant and planet-dominant regions is the
"orbital distance." Phase 1 showed it stabilizes based on mass ratio.

Phase 2 tests: can the boundary MOVE? If the planet source shifts
position (simulating orbital motion), does the boundary follow?
And critically: if we DON'T move the planet source but give it an
asymmetric emission pattern, does the boundary shift create apparent
motion?

Test A: Fixed sources, symmetric — baseline (should match Phase 1)
Test B: Planet source shifted mid-run — does boundary follow?
Test C: Asymmetric planet emission — directional bias creates boundary motion
Test D: Planet emission from boundary deposits — self-sustaining pattern shift
"""

import os
import time
import numpy as np
from collections import deque

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from graph import Graph, Connector

SEED = 42
N_NODES = 5000
SPHERE_R = 20.0
TARGET_K = 24

TICKS = 5000
MEASURE_EVERY = 50

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


class FwdTable:
    def __init__(self, graph):
        self._t = {}
        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                d = pos[node] - pos[nb]
                dl = np.linalg.norm(d)
                if dl < 1e-15:
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._t[(nb, node)] = others[0] if others else nb
                    continue
                d /= dl
                best, bd = nb, -2.0
                for n2 in graph.neighbors(node):
                    if n2 == nb:
                        continue
                    od = pos[n2] - pos[node]
                    ol = np.linalg.norm(od)
                    if ol < 1e-15:
                        continue
                    dot = np.dot(d, od / ol)
                    if dot > bd:
                        bd, best = dot, n2
                self._t[(nb, node)] = best

    def next(self, f, a):
        return self._t.get((f, a), a)


class Q:
    __slots__ = ('fam', 'node', 'frm', 'age')
    def __init__(self, f, n, fr):
        self.fam = f; self.node = n; self.frm = fr; self.age = 0


def bfs_distances(graph, starts):
    """BFS from multiple start nodes. Returns min distance to any start."""
    dist = np.full(graph.n_nodes, -1, dtype=np.int32)
    queue = deque()
    for s in starts:
        dist[s] = 0
        queue.append(s)
    while queue:
        node = queue.popleft()
        for nb in graph.neighbors(node):
            if dist[nb] == -1:
                dist[nb] = dist[node] + 1
                queue.append(nb)
    return dist


def find_boundary_profile(g, center_dist):
    """Star dominance fraction at each hop distance from center."""
    by_dist = {}
    seen = set()
    for (i, j), c in g.connectors.items():
        if (i, j) in seen:
            continue
        seen.add((i, j))
        d = min(center_dist[i], center_dist[j])
        if d < 0:
            continue
        by_dist.setdefault(d, []).append(
            1.0 if c.star_deposits > c.planet_deposits else 0.0
        )
    result = {}
    for d in sorted(by_dist.keys()):
        result[d] = float(np.mean(by_dist[d]))
    return result


def find_boundary_hop(profile):
    """Outermost hop distance where star fraction > 0.5."""
    boundary = 0
    for d in sorted(profile.keys()):
        if profile[d] > 0.5:
            boundary = d
    return boundary


def find_planet_com(g, center_pos):
    """Find the 'center of mass' of planet-dominant deposits."""
    total_weight = 0
    weighted_pos = np.zeros(3)
    seen = set()
    for (i, j), c in g.connectors.items():
        if (i, j) in seen:
            continue
        seen.add((i, j))
        if c.planet_deposits > c.star_deposits:
            net = c.planet_deposits - c.star_deposits
            mid = (g.pos[i] + g.pos[j]) / 2
            weighted_pos += net * mid
            total_weight += net
    if total_weight > 0:
        return weighted_pos / total_weight
    return center_pos


def reset_connectors(g):
    for c in g.connectors.values():
        c.star_deposits = 0
        c.planet_deposits = 0
        c.different_count = 0
        c.consumed_count = 0


def emit_and_propagate(g, fwd, quanta, star_sources, planet_sources,
                       star_rate, planet_rate, rng, max_age=50):
    """One tick of emission + propagation."""
    # Star emits
    for sn in star_sources:
        for _ in range(star_rate):
            nbrs = g.neighbors(sn)
            if nbrs:
                nb = nbrs[rng.integers(len(nbrs))]
                quanta.append(Q('star', nb, sn))
                g.connectors[g.edge_key(sn, nb)].deposit_star()

    # Planet emits
    for pn in planet_sources:
        for _ in range(planet_rate):
            nbrs = g.neighbors(pn)
            if nbrs:
                nb = nbrs[rng.integers(len(nbrs))]
                quanta.append(Q('planet', nb, pn))
                g.connectors[g.edge_key(pn, nb)].deposit_planet()

    # Propagate
    surviving = []
    for q in quanta:
        q.age += 1
        if q.age > max_age:
            continue
        nn = fwd.next(q.frm, q.node)
        ek = g.edge_key(q.node, nn)
        if ek not in g.connectors:
            continue
        if q.fam == 'star':
            g.connectors[ek].deposit_star()
        else:
            g.connectors[ek].deposit_planet()
        q.frm = q.node
        q.node = nn
        surviving.append(q)
    return surviving


def run_test(name, g, fwd, center, center_dist, star_sources, planet_sources_fn,
             star_rate, planet_rate, ticks, rng):
    """Run a single test. planet_sources_fn(tick) returns planet sources for that tick."""
    reset_connectors(g)
    quanta = []
    rows = []

    center_pos = g.pos[center]

    for tick in range(1, ticks + 1):
        planet_sources = planet_sources_fn(tick)
        quanta = emit_and_propagate(g, fwd, quanta, star_sources, planet_sources,
                                     star_rate, planet_rate, rng)

        if tick % MEASURE_EVERY == 0:
            prof = find_boundary_profile(g, center_dist)
            boundary = find_boundary_hop(prof)
            p_com = find_planet_com(g, center_pos)
            p_dist = np.linalg.norm(p_com - center_pos)
            consumed = sum(c.consumed_count for c in g.connectors.values())

            rows.append({
                'tick': tick,
                'boundary': boundary,
                'planet_com_dist': p_dist,
                'planet_com_x': p_com[0],
                'planet_com_y': p_com[1],
                'planet_com_z': p_com[2],
                'consumed': consumed,
            })

    print(f"  {name}: boundary={rows[-1]['boundary']}  "
          f"planet_com_dist={rows[-1]['planet_com_dist']:.2f}  "
          f"consumed={rows[-1]['consumed']}")
    return rows


def run():
    t_start = time.time()
    rng = np.random.default_rng(SEED)

    print("Building graph...")
    g = Graph(N_NODES, SPHERE_R, TARGET_K, seed=SEED)
    print("Building forward table...")
    fwd = FwdTable(g)
    center = g.nearest_to_origin(1)[0]
    center_dist = bfs_distances(g, [center])
    center_pos = g.pos[center]
    print(f"  ({time.time() - t_start:.1f}s)\n")

    # Star: 80 sources near origin
    star_sources = g.nearest_to_origin(80)

    # Planet position A: at r~12
    dists = np.linalg.norm(g.pos - center_pos, axis=1)
    p_cands_a = np.argsort(np.abs(dists - 12.0))
    p_seed_a = p_cands_a[0]
    nb_d = np.linalg.norm(g.pos - g.pos[p_seed_a], axis=1)
    nb_d[p_seed_a] = np.inf
    planet_a = [p_seed_a] + np.argsort(nb_d)[:2].tolist()

    # Planet position B: at r~12 but different angle (90 degrees)
    # Find a node at ~12 distance that's far from planet_a
    p_pos_a = g.pos[p_seed_a]
    dist_from_pa = np.linalg.norm(g.pos - p_pos_a, axis=1)
    # Want: r~12 from center AND far from planet_a
    score = np.abs(dists - 12.0) + 0.5 * (15.0 - np.minimum(dist_from_pa, 15.0))
    p_seed_b = np.argmin(score)
    nb_d2 = np.linalg.norm(g.pos - g.pos[p_seed_b], axis=1)
    nb_d2[p_seed_b] = np.inf
    planet_b = [p_seed_b] + np.argsort(nb_d2)[:2].tolist()

    print(f"Star: {len(star_sources)} sources")
    print(f"Planet A: {len(planet_a)} sources at r={dists[p_seed_a]:.2f}")
    print(f"Planet B: {len(planet_b)} sources at r={dists[p_seed_b]:.2f}")
    print(f"A-B distance: {np.linalg.norm(g.pos[p_seed_a] - g.pos[p_seed_b]):.2f}")

    all_results = {}

    # Test A: Fixed sources (baseline)
    print(f"\n--- Test A: Fixed sources (baseline) ---")
    rows_a = run_test("A: Fixed", g, fwd, center, center_dist,
                      star_sources, lambda t: planet_a, 1, 1, TICKS, rng)
    all_results['A'] = rows_a

    # Test B: Planet source shifts from A to B at mid-run
    print(f"\n--- Test B: Planet shifts A->B at t=2500 ---")
    rows_b = run_test("B: Shift", g, fwd, center, center_dist,
                      star_sources,
                      lambda t: planet_a if t < 2500 else planet_b,
                      1, 1, TICKS, rng)
    all_results['B'] = rows_b

    # Test C: Planet alternates A/B every 500 ticks (oscillation)
    print(f"\n--- Test C: Planet oscillates A<->B every 500 ticks ---")
    rows_c = run_test("C: Oscillate", g, fwd, center, center_dist,
                      star_sources,
                      lambda t: planet_a if (t // 500) % 2 == 0 else planet_b,
                      1, 1, TICKS, rng)
    all_results['C'] = rows_c

    # Test D: Planet source tracks its own deposit COM
    # The planet emits from wherever its deposit pattern is strongest
    print(f"\n--- Test D: Planet emits from deposit COM (self-tracking) ---")
    reset_connectors(g)
    quanta_d = []
    rows_d = []
    current_planet = list(planet_a)  # start at A

    for tick in range(1, TICKS + 1):
        quanta_d = emit_and_propagate(g, fwd, quanta_d, star_sources,
                                       current_planet, 1, 1, rng)

        if tick % MEASURE_EVERY == 0:
            prof = find_boundary_profile(g, center_dist)
            boundary = find_boundary_hop(prof)
            p_com = find_planet_com(g, center_pos)
            p_dist = np.linalg.norm(p_com - center_pos)

            rows_d.append({
                'tick': tick,
                'boundary': boundary,
                'planet_com_dist': p_dist,
                'planet_com_x': p_com[0],
                'planet_com_y': p_com[1],
                'planet_com_z': p_com[2],
                'consumed': sum(c.consumed_count for c in g.connectors.values()),
            })

        # Every 200 ticks: update planet source to nearest nodes to deposit COM
        if tick % 200 == 0:
            p_com = find_planet_com(g, center_pos)
            p_dists_from_com = np.linalg.norm(g.pos - p_com, axis=1)
            current_planet = np.argsort(p_dists_from_com)[:3].tolist()

    print(f"  D: Self-track: boundary={rows_d[-1]['boundary']}  "
          f"planet_com_dist={rows_d[-1]['planet_com_dist']:.2f}")
    all_results['D'] = rows_d

    plot_all(all_results, center_pos)


def plot_all(all_results, center_pos):
    fig, axes = plt.subplots(3, 4, figsize=(20, 12))
    fig.suptitle('Experiment 128 Phase 2: Boundary Dynamics', fontsize=14)

    for col, (key, name) in enumerate([
        ('A', 'A: Fixed'),
        ('B', 'B: Shift at t=2500'),
        ('C', 'C: Oscillate 500t'),
        ('D', 'D: Self-tracking'),
    ]):
        rows = all_results[key]
        ticks = [r['tick'] for r in rows]

        # Row 1: Boundary hop distance
        ax = axes[0, col]
        ax.plot(ticks, [r['boundary'] for r in rows], 'b-', linewidth=0.8)
        ax.set_ylabel('Boundary (hops)')
        ax.set_title(name)
        ax.set_ylim(-0.5, 9.5)
        ax.grid(True, alpha=0.3)

        # Row 2: Planet deposit COM distance from center
        ax = axes[1, col]
        ax.plot(ticks, [r['planet_com_dist'] for r in rows], 'g-', linewidth=0.8)
        ax.set_ylabel('Planet COM dist')
        ax.grid(True, alpha=0.3)

        # Row 3: Planet COM trajectory (XY)
        ax = axes[2, col]
        px = [r['planet_com_x'] for r in rows]
        py = [r['planet_com_y'] for r in rows]
        n = len(px)
        colors = plt.cm.viridis(np.linspace(0, 1, n))
        for i in range(1, n):
            ax.plot(px[i-1:i+1], py[i-1:i+1], '-', color=colors[i], linewidth=0.8)
        ax.plot(px[0], py[0], 'go', markersize=8)
        ax.plot(px[-1], py[-1], 'ro', markersize=8)
        ax.plot(center_pos[0], center_pos[1], 'y*', markersize=12)
        ax.set_xlabel('X')
        ax.set_ylabel('Y')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    png_path = os.path.join(OUT, "phase2_results.png")
    plt.savefig(png_path, dpi=150)
    plt.close()
    print(f"\nSaved: {png_path}")


if __name__ == '__main__':
    run()
