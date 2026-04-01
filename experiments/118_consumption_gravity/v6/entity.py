"""
Entity logic for Experiment 118 v6.

Entities route via accumulated deposit density on connectors.
One deposit per tick per node. Append-only. No propagation engine.
The connector IS the deposits.
"""

import numpy as np


BASE_WEIGHT = 1.0  # thermal motion — prevents total collapse


class EntityNode:
    """A single entity node. Routes toward densest matching deposits."""

    __slots__ = ('node', 'group', 'spectrum', 'fired_last_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum  # frozenset of matching group tags
        self.fired_last_tick = False

    def tick(self, graph, rng):
        """READ → ROUTE → DEPOSIT → HOP.

        Routes on accumulated deposit density: matching_deposits / length.
        A connector with 500 star deposits out of 600 total → density 0.83.
        A connector with 2 star deposits out of 100 total → density 0.02.
        Ratio: 40:1 — strong directional signal.
        """
        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.fired_last_tick = False
            return self.node

        # READ: accumulated matching density per connector
        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            scores[i] = c.matching_density(self.spectrum)

        # ROUTE: weighted random choice with thermal base
        weights = scores + BASE_WEIGHT
        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nbr = nbrs[chosen_idx]

        # DEPOSIT: append one deposit (connector grows by 1)
        c = graph.edge(self.node, chosen_nbr)
        c.append(self.group)

        # HOP
        self.node = chosen_nbr
        self.fired_last_tick = True
        return self.node


class Entity:
    """A collection of nodes forming one body."""

    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick(self, graph, rng):
        for en in self.entity_nodes:
            en.tick(graph, rng)

    def node_indices(self):
        return [en.node for en in self.entity_nodes]

    def com(self, graph):
        indices = self.node_indices()
        return graph.pos[indices].mean(axis=0)

    def mean_radius(self, graph):
        center = self.com(graph)
        indices = self.node_indices()
        dists = np.linalg.norm(graph.pos[indices] - center, axis=1)
        return float(np.mean(dists))

    def max_radius(self, graph):
        center = self.com(graph)
        indices = self.node_indices()
        dists = np.linalg.norm(graph.pos[indices] - center, axis=1)
        return float(np.max(dists))

    def discharge_rate(self):
        fired = sum(1 for en in self.entity_nodes if en.fired_last_tick)
        return fired / len(self.entity_nodes)

    def internal_connector_stats(self, graph):
        """Stats for connectors where both endpoints are entity nodes."""
        my_nodes = set(self.node_indices())
        lengths = []
        seen = set()
        for en in self.entity_nodes:
            for nb in graph.neighbors(en.node):
                if nb in my_nodes:
                    key = (min(en.node, nb), max(en.node, nb))
                    if key not in seen:
                        seen.add(key)
                        lengths.append(graph.connectors[key].length)
        if not lengths:
            return 0.0, 0.0, 0
        return float(np.mean(lengths)), float(np.max(lengths)), len(lengths)

    def boundary_connector_stats(self, graph):
        """Stats for connectors where one endpoint is entity, one is not."""
        my_nodes = set(self.node_indices())
        lengths = []
        seen = set()
        for en in self.entity_nodes:
            for nb in graph.neighbors(en.node):
                if nb not in my_nodes:
                    key = (min(en.node, nb), max(en.node, nb))
                    if key not in seen:
                        seen.add(key)
                        lengths.append(graph.connectors[key].length)
        if not lengths:
            return 0.0, 0.0, 0
        return float(np.mean(lengths)), float(np.max(lengths)), len(lengths)

    def mean_routing_ratio(self, graph):
        """Mean ratio of max/min routing score across entity nodes.

        Measures how directional the routing signal is. >3:1 means strong.
        """
        ratios = []
        for en in self.entity_nodes:
            nbrs = graph.neighbors(en.node)
            if len(nbrs) < 2:
                continue
            scores = [graph.edge(en.node, nb).matching_density(self.spectrum)
                      for nb in nbrs]
            mn = min(scores)
            mx = max(scores)
            if mn > 0:
                ratios.append(mx / mn)
            elif mx > 0:
                ratios.append(float('inf'))
        if not ratios:
            return 0.0
        # Cap infinities for mean computation
        capped = [min(r, 1000.0) for r in ratios]
        return float(np.mean(capped))
