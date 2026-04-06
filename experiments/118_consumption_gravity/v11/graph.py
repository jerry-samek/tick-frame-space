"""
Graph substrate for Experiment 118 v10.

Same as v7-v9 but Connector tracks per-tick deposits and deposit direction
for reactive entity triggering.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    """Connector = chain of deposits. Tracks per-tick activity for triggering."""

    __slots__ = ('initial_length', 'deposits', 'total',
                 'deposits_this_tick', 'last_deposit_src', 'last_deposit_dst')

    def __init__(self, initial_length):
        self.initial_length = initial_length
        self.deposits = {}
        self.total = 0
        self.deposits_this_tick = 0
        self.last_deposit_src = None
        self.last_deposit_dst = None

    @property
    def length(self):
        return self.initial_length + self.total

    def append(self, group_tag, src_node=None, dst_node=None):
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        self.deposits_this_tick += 1
        self.last_deposit_src = src_node
        self.last_deposit_dst = dst_node

    def reset_tick(self):
        self.deposits_this_tick = 0


class Graph:
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

    def edge_key(self, i, j):
        return (min(i, j), max(i, j))

    def neighbors(self, node):
        return self.adj[node]

    def nearest_to_origin(self, count):
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count].tolist()

    def reset_all_ticks(self):
        for c in self.connectors.values():
            c.reset_tick()
