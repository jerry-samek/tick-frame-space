"""
Graph substrate for Experiment 118 v5.

Random geometric graph in a 3D sphere with FIXED-LENGTH connectors.
Connectors never change after construction. Deposits travel on them
via the PropagationEngine, not stored on the connector itself.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    """Fixed-length edge between two nodes. Immutable after construction."""
    __slots__ = ('length',)

    def __init__(self, length):
        self.length = length


class Graph:
    """Random geometric graph in a 3D sphere.

    Nodes are placed uniformly in a sphere of given radius.
    Edges connect nodes within a connectivity radius derived from
    target average degree k. The graph is immutable after construction.
    """

    def __init__(self, n_nodes, sphere_r, target_k, seed=42):
        self.n_nodes = n_nodes
        self.sphere_r = sphere_r
        self.target_k = target_k
        self.rng = np.random.default_rng(seed)

        self.pos = self._sample_sphere(n_nodes)
        self.rc = sphere_r * (target_k / n_nodes) ** (1.0 / 3.0)
        self.adj = defaultdict(list)
        self.connectors = {}
        self.edge_list = []  # ordered list of (i, j) with i < j

        self._build_edges()

    def _sample_sphere(self, n):
        """Sample n points uniformly inside a 3D sphere."""
        pts = []
        while len(pts) < n:
            batch = self.rng.uniform(-self.sphere_r, self.sphere_r, (n * 2, 3))
            good = batch[np.linalg.norm(batch, axis=1) <= self.sphere_r]
            pts.extend(good.tolist())
        return np.array(pts[:n])

    def _build_edges(self):
        pairs = cKDTree(self.pos).query_pairs(self.rc)
        for i, j in sorted(pairs):
            key = (min(i, j), max(i, j))
            if key not in self.connectors:
                dist = np.linalg.norm(self.pos[i] - self.pos[j])
                self.connectors[key] = Connector(dist)
                self.edge_list.append(key)
                self.adj[i].append(j)
                self.adj[j].append(i)

        degs = [len(self.adj[n]) for n in range(self.n_nodes)]
        print(f"Graph: {self.n_nodes} nodes, {len(self.connectors)} edges, "
              f"avg_k={np.mean(degs):.1f}, rc={self.rc:.3f}")

    def edge(self, i, j):
        """Get connector between nodes i and j."""
        return self.connectors[(min(i, j), max(i, j))]

    def neighbors(self, node):
        """Return list of neighbor node indices."""
        return self.adj[node]

    def nearest_to_origin(self, count):
        """Return indices of `count` nodes closest to origin."""
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count].tolist()
