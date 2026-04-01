"""
Graph substrate for Experiment 118 v6.

Random geometric graph in a 3D sphere. Connector = chain of deposits.
Length = initial geometric distance + deposit count. Append-only.
There is nothing underneath — the connector IS its deposits.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    """A connector between two nodes = a chain of deposits.

    Length = initial geometric distance + total deposits appended.
    The connector IS its deposits. Remove all deposits and only the
    primordial geometric link remains (the initial condition).
    """

    __slots__ = ('initial_length', 'deposits', 'total')

    def __init__(self, initial_length):
        self.initial_length = initial_length
        self.deposits = {}  # {group_tag: count}
        self.total = 0

    @property
    def length(self):
        return self.initial_length + self.total

    def append(self, group_tag):
        """Append one deposit. The single mutation operation."""
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1

    def matching_density(self, spectrum):
        """Fraction of total length that is matching deposits."""
        if self.length <= 0:
            return 0.0
        matching = sum(v for k, v in self.deposits.items() if k in spectrum)
        return matching / self.length

    def total_density(self):
        """Fraction of length that is deposits (vs primordial gap)."""
        if self.length <= 0:
            return 0.0
        return self.total / self.length


class Graph:
    """Random geometric graph in a 3D sphere."""

    def __init__(self, n_nodes, sphere_r, target_k, seed=42):
        self.n_nodes = n_nodes
        self.sphere_r = sphere_r
        self.target_k = target_k
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

    def edge(self, i, j):
        return self.connectors[(min(i, j), max(i, j))]

    def neighbors(self, node):
        return self.adj[node]

    def nearest_to_origin(self, count):
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count].tolist()
