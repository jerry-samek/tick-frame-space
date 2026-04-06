"""
Experiment 128 v5 — Vectorized Substrate

The entire simulation as numpy arrays. No Python objects for connectors
or entities. Everything is an array indexed by edge_id or entity_id.

The simulation IS the connector arrays. Entities are masks.
Movement is changing which index the mask points at.
"""

import numpy as np
from scipy.spatial import cKDTree


class Substrate:
    """The universe: graph topology + connector state + entity state.

    All state is numpy arrays. All operations are vectorized.
    """

    def __init__(self, n_nodes, sphere_r, target_k, seed=42):
        self.rng = np.random.default_rng(seed)
        self.n_nodes = n_nodes
        self.sphere_r = sphere_r

        # Build graph
        self.pos = self._sample_sphere(n_nodes, sphere_r)
        rc = sphere_r * (target_k / n_nodes) ** (1.0 / 3.0)
        pairs = cKDTree(self.pos).query_pairs(rc)

        # Build edge list
        edges = []
        adj = [[] for _ in range(n_nodes)]
        for i, j in pairs:
            a, b = min(i, j), max(i, j)
            edges.append((a, b))
            adj[a].append(len(edges) - 1)  # edge index, not node
            adj[b].append(len(edges) - 1)

        self.n_edges = len(edges)
        self.edges = np.array(edges, dtype=np.int32)  # (n_edges, 2)

        # Padded adjacency: (n_nodes, max_k)
        degrees = [len(a) for a in adj]
        self.max_k = max(degrees)
        avg_k = np.mean(degrees)

        # For each node: neighbor node ids, edge ids, direction vectors
        self.nbr_node = np.full((n_nodes, self.max_k), -1, dtype=np.int32)
        self.nbr_edge = np.full((n_nodes, self.max_k), -1, dtype=np.int32)
        self.nbr_mask = np.zeros((n_nodes, self.max_k), dtype=bool)
        self.nbr_dir = np.zeros((n_nodes, self.max_k, 3), dtype=np.float32)
        self.degree = np.array(degrees, dtype=np.int32)

        for node in range(n_nodes):
            for k_idx, eid in enumerate(adj[node]):
                a, b = edges[eid]
                nb = b if a == node else a
                self.nbr_node[node, k_idx] = nb
                self.nbr_edge[node, k_idx] = eid
                self.nbr_mask[node, k_idx] = True
                d = self.pos[nb] - self.pos[node]
                dn = np.linalg.norm(d)
                if dn > 1e-15:
                    self.nbr_dir[node, k_idx] = d / dn

        # ── Connector state arrays ──
        initial_lengths = np.linalg.norm(
            self.pos[self.edges[:, 0]] - self.pos[self.edges[:, 1]], axis=1
        )
        self.conn_initial_len = initial_lengths.astype(np.float32)
        self.conn_star = np.zeros(self.n_edges, dtype=np.int32)
        self.conn_planet = np.zeros(self.n_edges, dtype=np.int32)
        self.conn_different = np.zeros(self.n_edges, dtype=np.int32)
        self.conn_consumed = np.zeros(self.n_edges, dtype=np.int32)

        print(f"Substrate: {n_nodes} nodes, {self.n_edges} edges, "
              f"avg_k={avg_k:.1f}, max_k={self.max_k}, rc={rc:.3f}")

    def _sample_sphere(self, n, r):
        pts = []
        rng = self.rng
        while len(pts) < n:
            batch = rng.uniform(-r, r, (n * 2, 3))
            good = batch[np.linalg.norm(batch, axis=1) <= r]
            pts.extend(good.tolist())
        return np.array(pts[:n], dtype=np.float32)

    def conn_length(self, edge_ids=None):
        """Effective length = initial + max(0, different)."""
        if edge_ids is None:
            return self.conn_initial_len + np.maximum(0, self.conn_different).astype(np.float32)
        return self.conn_initial_len[edge_ids] + np.maximum(0, self.conn_different[edge_ids]).astype(np.float32)

    def deposit(self, edge_ids, is_star):
        """Deposit on connectors. Vectorized Same/Different classification.

        is_star: boolean array — True for star deposits, False for planet.
        """
        star_mask = is_star
        planet_mask = ~is_star

        # Star deposits
        s_edges = edge_ids[star_mask]
        if len(s_edges) > 0:
            np.add.at(self.conn_star, s_edges, 1)
            # Same if star-dominant (star >= planet), Different otherwise
            dominant_is_star = self.conn_star[s_edges] >= self.conn_planet[s_edges]
            same = s_edges[dominant_is_star]
            diff = s_edges[~dominant_is_star]
            # Same: consume one Different
            if len(same) > 0:
                can_consume = self.conn_different[same] > 0
                np.add.at(self.conn_different, same[can_consume], -1)
                np.add.at(self.conn_consumed, same[can_consume], 1)
            # Different: extend
            if len(diff) > 0:
                np.add.at(self.conn_different, diff, 1)

        # Planet deposits
        p_edges = edge_ids[planet_mask]
        if len(p_edges) > 0:
            np.add.at(self.conn_planet, p_edges, 1)
            dominant_is_planet = self.conn_planet[p_edges] > self.conn_star[p_edges]
            same = p_edges[dominant_is_planet]
            diff = p_edges[~dominant_is_planet]
            if len(same) > 0:
                can_consume = self.conn_different[same] > 0
                np.add.at(self.conn_different, same[can_consume], -1)
                np.add.at(self.conn_consumed, same[can_consume], 1)
            if len(diff) > 0:
                np.add.at(self.conn_different, diff, 1)

    def nearest_to_origin(self, count):
        dists = np.linalg.norm(self.pos, axis=1)
        return np.argsort(dists)[:count]

    def stats(self):
        return (int(self.conn_star.sum() + self.conn_planet.sum()),
                int(self.conn_different.sum()),
                int(self.conn_consumed.sum()))
