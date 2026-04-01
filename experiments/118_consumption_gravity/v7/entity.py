"""
Entity logic for Experiment 118 v7.

Key change: traversal time proportional to connector length.
A node traversing a connector of length L takes L ticks, depositing
one quantum per tick. This creates time dilation (long connectors =
slow traversal) and self-limiting compound growth (L → 2L per traversal,
but traversal takes L ticks, so growth/time is linear).

Routing on absolute matching count (not density) to avoid saturation.
"""

import numpy as np

BASE_WEIGHT = 1.0  # thermal motion


class EntityNode:
    """A single entity node with IDLE/IN_TRANSIT states."""

    __slots__ = ('node', 'group', 'spectrum',
                 'in_transit', 'transit_edge', 'transit_dest',
                 'transit_remaining', 'hops_completed')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum  # frozenset of matching group tags
        self.in_transit = False
        self.transit_edge = None
        self.transit_dest = None
        self.transit_remaining = 0
        self.hops_completed = 0

    def tick(self, graph, rng):
        """One tick: either continue transit or make routing decision."""

        if self.in_transit:
            # Node is traversing — READING, not writing.
            # No deposit during transit. Capacitor is charging (RAW 126).
            self.transit_remaining -= 1

            if self.transit_remaining <= 0:
                # ARRIVED: capacitor fires, deposit ONE quantum at destination
                graph.connectors[self.transit_edge].append(self.group)
                self.node = self.transit_dest
                self.in_transit = False
                self.transit_edge = None
                self.transit_dest = None
                self.hops_completed += 1
            return

        # IDLE: make routing decision
        nbrs = graph.neighbors(self.node)
        if not nbrs:
            return

        # Route on ABSOLUTE matching count (not density)
        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            matching = sum(c.deposits.get(g, 0) for g in self.spectrum)
            scores[i] = matching

        weights = scores + BASE_WEIGHT
        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nb = nbrs[chosen_idx]

        # Begin traversal — time = connector length
        edge_key = (min(self.node, chosen_nb), max(self.node, chosen_nb))
        c = graph.connectors[edge_key]
        traverse_time = max(1, int(c.length))

        self.in_transit = True
        self.transit_edge = edge_key
        self.transit_dest = chosen_nb
        self.transit_remaining = traverse_time

        # First deposit of traversal
        c.append(self.group)
        self.transit_remaining -= 1

        if self.transit_remaining <= 0:
            # Very short connector — arrive immediately
            self.node = self.transit_dest
            self.in_transit = False
            self.transit_edge = None
            self.transit_dest = None
            self.hops_completed += 1


class Entity:
    """A collection of entity nodes."""

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
        """Current positions (only meaningful for IDLE nodes)."""
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

    def idle_fraction(self):
        """Fraction of nodes currently IDLE (not in transit)."""
        idle = sum(1 for en in self.entity_nodes if not en.in_transit)
        return idle / len(self.entity_nodes)

    def total_hops(self):
        """Total completed hops across all nodes."""
        return sum(en.hops_completed for en in self.entity_nodes)

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
