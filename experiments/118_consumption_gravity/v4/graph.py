"""
Graph substrate for Experiment 118 v4.

Random geometric graph in a 3D sphere with append-only connectors.
Connector length = initial geometric distance + total deposits appended.
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    """Append-only buffer between two nodes.

    Deposits are only appended, never subtracted. The connector length
    grows by 1 for each deposit appended. This is the ONLY mutation.

    Routing uses PREVIOUS TICK's deposits only (not accumulated history).
    This prevents nodes from locking into static patterns on heavily-
    deposited connectors. The permanent deposit history still exists
    (affects length, available for analysis) but routing is reactive.
    """

    __slots__ = ('initial_length', 'deposits', 'total',
                 'prev_deposits', 'curr_deposits')

    def __init__(self, initial_length):
        self.initial_length = initial_length
        self.deposits = {}       # {group_tag: count} — permanent, all time
        self.total = 0
        self.prev_deposits = {}  # last tick's deposits (used for routing)
        self.curr_deposits = {}  # current tick's deposits (not yet visible)

    @property
    def length(self):
        """Length = initial geometric distance + total deposits appended."""
        return self.initial_length + self.total

    def append(self, group_tag):
        """Append one quantum. The only mutation operation."""
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        self.curr_deposits[group_tag] = self.curr_deposits.get(group_tag, 0) + 1

    def rotate(self):
        """Advance epoch: current deposits become previous, current cleared."""
        self.prev_deposits = self.curr_deposits
        self.curr_deposits = {}

    def recent_matching(self, spectrum):
        """Count of LAST TICK's deposits matching the spectrum."""
        return sum(v for k, v in self.prev_deposits.items() if k in spectrum)

    def recent_total(self):
        """Count of LAST TICK's deposits (any group)."""
        return sum(self.prev_deposits.values())

    def matching_density(self, spectrum):
        """Fraction of ALL deposits matching the given spectrum set."""
        if self.length <= 0:
            return 0.0
        matching = sum(v for k, v in self.deposits.items() if k in spectrum)
        return matching / self.length

    def foreign_density(self, spectrum):
        """Fraction of ALL deposits NOT matching the spectrum set."""
        if self.length <= 0:
            return 0.0
        foreign = sum(v for k, v in self.deposits.items() if k not in spectrum)
        return foreign / self.length

    def total_density(self):
        """Fraction of length that is deposits (vs initial geometric gap)."""
        if self.length <= 0:
            return 0.0
        return self.total / self.length

    def group_counts(self):
        """Return a copy of deposits dict."""
        return dict(self.deposits)


class Graph:
    """Random geometric graph in a 3D sphere.

    Nodes are placed uniformly in a sphere of given radius.
    Edges connect nodes within a connectivity radius derived from
    target average degree k.
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
        """Get connector between nodes i and j."""
        return self.connectors[(min(i, j), max(i, j))]

    def neighbors(self, node):
        """Return list of neighbor node indices."""
        return self.adj[node]

    def rotate_all(self):
        """Advance epoch on all connectors. Call once at the start of each tick."""
        for c in self.connectors.values():
            c.rotate()

    def nearest_to_origin(self, count):
        """Return indices of `count` nodes closest to origin."""
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count].tolist()
