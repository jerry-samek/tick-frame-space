"""
Entity logic for Experiment 118 v9.

NO deposit-on-arrival. All deposits flow through the three-way partition.
When a node completes traversal, it emits a quantum toward a chosen
outgoing connector. The quantum's fate (store/move/radiate) is determined
by the receiving environment.
"""

import numpy as np

BASE_WEIGHT = 1.0


class QuantumEmission:
    """A quantum emitted by an entity node's capacitor discharge."""
    __slots__ = ('group', 'src_node', 'dest_node')

    def __init__(self, group, src_node, dest_node):
        self.group = group
        self.src_node = src_node    # node that emitted (arrival position)
        self.dest_node = dest_node  # target node (chosen by routing)


class EntityNode:
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
        return not self.in_transit and not self.fired_this_tick

    def tick(self, graph, rng):
        """One tick. Returns QuantumEmission if capacitor fires, else None."""
        self.fired_this_tick = False

        if self.in_transit:
            self.transit_remaining -= 1
            if self.transit_remaining <= 0:
                # ARRIVED — capacitor fires
                self.node = self.transit_dest
                self.in_transit = False
                self.fired_this_tick = True
                self.hops_completed += 1

                # Choose outgoing direction for the quantum
                nbrs = graph.neighbors(self.node)
                if not nbrs:
                    return None

                scores = np.empty(len(nbrs), dtype=np.float64)
                for i, nb in enumerate(nbrs):
                    c = graph.edge(self.node, nb)
                    matching = sum(c.deposits.get(g, 0) for g in self.spectrum)
                    scores[i] = matching

                weights = scores + BASE_WEIGHT
                weights /= weights.sum()
                chosen_idx = rng.choice(len(nbrs), p=weights)
                chosen_nb = nbrs[chosen_idx]

                # Emit quantum toward chosen neighbor
                # NO deposit on arrival connector — quantum handles all deposits
                return QuantumEmission(self.group, self.node, chosen_nb)
            return None

        # IDLE: begin traversal
        nbrs = graph.neighbors(self.node)
        if not nbrs:
            return None

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
    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick(self, graph, rng):
        emissions = []
        for en in self.entity_nodes:
            em = en.tick(graph, rng)
            if em is not None:
                emissions.append(em)
        return emissions

    def idle_node_set(self):
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

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def internal_connector_stats(self, graph):
        my_nodes = set(self.node_indices())
        lengths, seen = [], set()
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
        lengths, seen = [], set()
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
