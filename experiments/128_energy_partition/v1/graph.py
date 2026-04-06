"""
Graph for Experiment 128 Phase 1.

Connector with star/planet deposit tracking and consumption.
Simplified from v16 — direct star/planet deposit methods instead of
group-tag-based family detection.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    __slots__ = ('initial_length', 'star_deposits', 'planet_deposits',
                 'different_count', 'consumed_count')

    def __init__(self, initial_length):
        self.initial_length = initial_length
        self.star_deposits = 0
        self.planet_deposits = 0
        self.different_count = 0
        self.consumed_count = 0

    @property
    def length(self):
        return self.initial_length + max(0, self.different_count)

    @property
    def dominant(self):
        if self.star_deposits > self.planet_deposits:
            return 'star'
        elif self.planet_deposits > self.star_deposits:
            return 'planet'
        return None

    @property
    def total(self):
        return self.star_deposits + self.planet_deposits

    def deposit_star(self):
        self.star_deposits += 1
        dom = self.dominant
        if dom == 'star' or dom is None:
            # Same: consume one Different
            if self.different_count > 0:
                self.different_count -= 1
                self.consumed_count += 1
        else:
            # Different: extend
            self.different_count += 1

    def deposit_planet(self):
        self.planet_deposits += 1
        dom = self.dominant
        if dom == 'planet' or dom is None:
            if self.different_count > 0:
                self.different_count -= 1
                self.consumed_count += 1
        else:
            self.different_count += 1


class Graph:
    def __init__(self, n_nodes, sphere_r, target_k, seed=42):
        self.n_nodes = n_nodes
        self.sphere_r = sphere_r
        self.rng = np.random.default_rng(seed)
        self.pos = self._sample_sphere(n_nodes)
        self.rc = sphere_r * (target_k / n_nodes) ** (1.0 / 3.0)
        self.adj = defaultdict(list)
        self.connectors = {}
        self._build_edges()

    def _sample_sphere(self, n):
        pts = []
        while len(pts) < n:
            batch = self.rng.uniform(-self.sphere_r, self.sphere_r, (n * 2, 3))
            good = batch[np.linalg.norm(batch, axis=1) <= self.sphere_r]
            pts.extend(good.tolist())
        return np.array(pts[:n])

    def _build_edges(self):
        pairs = cKDTree(self.pos).query_pairs(self.rc)
        for i, j in pairs:
            key = (min(i, j), max(i, j))
            dist = np.linalg.norm(self.pos[i] - self.pos[j])
            self.connectors[key] = Connector(dist)
            self.adj[i].append(j)
            self.adj[j].append(i)
        degs = [len(self.adj[n]) for n in range(self.n_nodes)]
        print(f"Graph: {self.n_nodes} nodes, {len(self.connectors)} edges, "
              f"avg_k={np.mean(degs):.1f}, rc={self.rc:.3f}")

    def edge_key(self, i, j):
        return (min(i, j), max(i, j))

    def neighbors(self, node):
        return self.adj[node]

    def nearest_to_origin(self, count):
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count].tolist()
