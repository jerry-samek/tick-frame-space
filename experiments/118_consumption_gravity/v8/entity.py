"""
Entity logic for Experiment 118 v8.

v7 model + store/move partition from RAW 128.
Discharge produces a quantum that checks next node's capacitor:
  - Idle -> absorbed (stored, connector grows)
  - Busy -> in-flight quantum (momentum)
"""

import numpy as np

BASE_WEIGHT = 1.0


class DischargeEvent:
    """A discharge from an entity node's capacitor."""
    __slots__ = ('group', 'edge_key', 'dest_node', 'src_node')

    def __init__(self, group, edge_key, dest_node, src_node):
        self.group = group
        self.edge_key = edge_key
        self.dest_node = dest_node
        self.src_node = src_node


class EntityNode:
    """Entity node with capacitor state tracking."""

    __slots__ = ('node', 'group', 'spectrum',
                 'in_transit', 'transit_edge', 'transit_dest', 'transit_src',
                 'transit_remaining', 'hops_completed',
                 'fired_this_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.in_transit = False
        self.transit_edge = None
        self.transit_dest = None
        self.transit_src = None
        self.transit_remaining = 0
        self.hops_completed = 0
        self.fired_this_tick = False

    def is_idle(self):
        """Is this node's capacitor available to absorb?"""
        return not self.in_transit and not self.fired_this_tick

    def tick(self, graph, rng):
        """One tick. Returns DischargeEvent if capacitor fires, else None."""
        self.fired_this_tick = False

        if self.in_transit:
            self.transit_remaining -= 1
            if self.transit_remaining <= 0:
                # ARRIVED: capacitor fires -> discharge event
                self.node = self.transit_dest
                self.in_transit = False
                self.fired_this_tick = True
                self.hops_completed += 1

                return DischargeEvent(
                    self.group,
                    self.transit_edge,
                    self.transit_dest,
                    self.transit_src,
                )
            return None

        # IDLE: make routing decision
        nbrs = graph.neighbors(self.node)
        if not nbrs:
            return None

        # Route on absolute matching count (includes wake deposits)
        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            matching = sum(c.deposits.get(g, 0) for g in self.spectrum)
            scores[i] = matching

        weights = scores + BASE_WEIGHT
        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nb = nbrs[chosen_idx]

        edge_key = (min(self.node, chosen_nb), max(self.node, chosen_nb))
        c = graph.connectors[edge_key]
        traverse_time = max(1, int(c.length))

        self.transit_src = self.node
        self.in_transit = True
        self.transit_edge = edge_key
        self.transit_dest = chosen_nb
        self.transit_remaining = traverse_time
        return None


class Entity:
    """Collection of entity nodes."""

    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick(self, graph, rng):
        """Tick all nodes. Returns list of DischargeEvents."""
        events = []
        for en in self.entity_nodes:
            ev = en.tick(graph, rng)
            if ev is not None:
                events.append(ev)
        return events

    def idle_node_set(self):
        """Set of node indices where entity capacitor is idle."""
        return {en.node for en in self.entity_nodes if en.is_idle()}

    def node_indices(self):
        return [en.node for en in self.entity_nodes]

    def com(self, graph):
        return graph.pos[self.node_indices()].mean(axis=0)

    def mean_radius(self, graph):
        center = self.com(graph)
        dists = np.linalg.norm(graph.pos[self.node_indices()] - center, axis=1)
        return float(np.mean(dists))

    def max_radius(self, graph):
        center = self.com(graph)
        dists = np.linalg.norm(graph.pos[self.node_indices()] - center, axis=1)
        return float(np.max(dists))

    def idle_fraction(self):
        return sum(1 for en in self.entity_nodes if en.is_idle()) / len(self.entity_nodes)

    def transit_fraction(self):
        return sum(1 for en in self.entity_nodes if en.in_transit) / len(self.entity_nodes)

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def internal_connector_stats(self, graph):
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
