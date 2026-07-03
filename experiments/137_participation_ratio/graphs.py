"""Fixture graphs for Exp 137 Phase 0 (known-geometry substrates).

All generators return an adjacency list: list[list[int]].
"""

from collections import deque

import numpy as np


def torus3d(L=12):
    """3D torus, von Neumann (6-neighbor)."""
    n = L * L * L
    adj = [[] for _ in range(n)]
    for x in range(L):
        for y in range(L):
            for z in range(L):
                i = x + L * y + L * L * z
                for dx, dy, dz in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
                    j = ((x + dx) % L) + L * ((y + dy) % L) + L * L * ((z + dz) % L)
                    adj[i].append(j)
                    adj[j].append(i)
    return adj


def torus2d(L=42):
    """2D torus, von Neumann (4-neighbor)."""
    n = L * L
    adj = [[] for _ in range(n)]
    for x in range(L):
        for y in range(L):
            i = x + L * y
            for dx, dy in ((1, 0), (0, 1)):
                j = ((x + dx) % L) + L * ((y + dy) % L)
                adj[i].append(j)
                adj[j].append(i)
    return adj


def random_regular(n=1750, d=3, rng=None, max_tries=50):
    """Random d-regular graph: configuration model + double-edge-swap repair.

    Pure rejection is hopeless for d >= 4 (P(simple) ~ exp(-(d^2-1)/4)), so
    self-loops/multi-edges are repaired by swapping with random good edges.
    """
    assert (n * d) % 2 == 0
    rng = rng or np.random.default_rng()
    for _ in range(max_tries):
        stubs = np.repeat(np.arange(n), d)
        rng.shuffle(stubs)
        pairs = [(int(a), int(b)) for a, b in stubs.reshape(-1, 2)]
        edges = set()
        bad = []
        for a, b in pairs:
            key = (min(a, b), max(a, b))
            if a == b or key in edges:
                bad.append((a, b))
            else:
                edges.add(key)
        guard = 0
        while bad and guard < 100000:
            guard += 1
            u, v = bad.pop(rng.integers(len(bad)))
            x, y = list(edges)[rng.integers(len(edges))]
            # rewire (u,v)+(x,y) -> (u,x)+(v,y)
            k1, k2 = (min(u, x), max(u, x)), (min(v, y), max(v, y))
            if u != x and v != y and k1 not in edges and k2 not in edges and k1 != k2:
                edges.discard((min(x, y), max(x, y)))
                edges.add(k1)
                edges.add(k2)
            else:
                bad.append((u, v))
        if bad:
            continue
        adj = [[] for _ in range(n)]
        for a, b in edges:
            adj[a].append(b)
            adj[b].append(a)
        if len(bfs_distances(adj, 0)) == n:  # connected
            return adj
    raise RuntimeError("failed to generate a simple connected regular graph")


def binary_tree(depth=10):
    """Balanced binary tree; 2^(depth+1) - 1 nodes."""
    n = 2 ** (depth + 1) - 1
    adj = [[] for _ in range(n)]
    for i in range(n):
        for c in (2 * i + 1, 2 * i + 2):
            if c < n:
                adj[i].append(c)
                adj[c].append(i)
    return adj


def bfs_distances(adj, source, cutoff=None):
    """Graph distances from source. Returns {node: dist}; bounded by cutoff if given."""
    dist = {source: 0}
    q = deque([source])
    while q:
        u = q.popleft()
        if cutoff is not None and dist[u] >= cutoff:
            continue
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


def sample_bundle(adj, n_tap, radius, rng):
    """Observer bundle: n_tap nodes sampled uniformly from a graph-distance ball.

    Re-draws the center until the ball holds at least n_tap nodes (pre-registered rule).
    Returns (center, taps ndarray, dist_from_center dict).
    """
    n = len(adj)
    while True:
        center = int(rng.integers(n))
        ball = bfs_distances(adj, center, cutoff=radius)
        if len(ball) >= n_tap:
            nodes = np.array(sorted(ball))
            taps = rng.choice(nodes, size=n_tap, replace=False)
            return center, np.sort(taps), ball
