"""
Graph substrate for Experiment 118 v12.

Same as v11 but Connector implements the Same/Different extension rule:
  - Same deposits reinforce (no length change)
  - Different deposits extend (length += 1)
  - First deposit on empty connector = Unknown -> extends
"""

import numpy as np
from scipy.spatial import cKDTree
from collections import defaultdict


class Connector:
    """Connector with Same/Different extension rule from RAW 113."""

    __slots__ = ('initial_length', 'deposits', 'total', 'different_count',
                 'same_count', 'deposits_this_tick', 'last_deposit_src',
                 'last_deposit_dst')

    def __init__(self, initial_length):
        self.initial_length = initial_length
        self.deposits = {}
        self.total = 0
        self.different_count = 0  # only Different deposits count for length
        self.same_count = 0
        self.deposits_this_tick = 0
        self.last_deposit_src = None
        self.last_deposit_dst = None

    @property
    def length(self):
        """Effective length = initial + Different deposits only."""
        return self.initial_length + self.different_count

    def _family_of(self, group_tag):
        if group_tag.startswith('s'):
            return 'star'
        elif group_tag.startswith('p'):
            return 'planet'
        return 'unknown'

    def _dominant_family(self):
        star = sum(v for k, v in self.deposits.items() if k.startswith('s'))
        planet = sum(v for k, v in self.deposits.items() if k.startswith('p'))
        if star == 0 and planet == 0:
            return None
        return 'star' if star >= planet else 'planet'

    def append(self, group_tag, src_node=None, dst_node=None):
        """Append deposit. Same = reinforce (no growth). Different = extend."""
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        self.deposits_this_tick += 1
        self.last_deposit_src = src_node
        self.last_deposit_dst = dst_node

        # Classify Same vs Different
        dominant = self._dominant_family()
        depositor_family = self._family_of(group_tag)

        if dominant is None:
            # First deposit — Unknown -> extends
            self.different_count += 1
        elif depositor_family != dominant:
            # Different family -> extends
            self.different_count += 1
        else:
            # Same family -> reinforces (no extension)
            self.same_count += 1

    def reset_tick(self):
        self.deposits_this_tick = 0
        self.last_deposit_src = None
        self.last_deposit_dst = None


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

    def total_same_different(self):
        """Global Same/Different deposit counts."""
        total_same = sum(c.same_count for c in self.connectors.values())
        total_diff = sum(c.different_count for c in self.connectors.values())
        return total_same, total_diff
