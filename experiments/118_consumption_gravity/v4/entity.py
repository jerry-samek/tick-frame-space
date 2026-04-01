"""
Entity tick logic for Experiment 118 v4.

Each node performs one operation per tick:
  READ -> DECIDE -> FIRE (append + hop) or IDLE

One quantum per tick per node. Append-only. No subtraction.
"""

import numpy as np


class EntityNode:
    """A single node belonging to an entity (star or planet).

    Each node has a group tag and a spectrum (set of group tags it
    considers 'Same'). The node routes toward the connector with the
    highest matching deposit density.
    """

    __slots__ = ('node', 'group', 'spectrum', 'fired_last_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum  # frozenset of group tags
        self.fired_last_tick = False

    def tick(self, graph, rng):
        """Execute one tick for this node.

        Weighted random walk: probability of choosing a connector is
        proportional to (1 + recent_other_group_deposits). This models
        the capacitor charging from all connectors (base weight 1) but
        charging faster from connectors with more deposits (higher weight).
        No deterministic lock-in. No added parameters.

        Graph.rotate_all() must be called before each tick batch.

        Returns the new node index (may be same if idle).
        """
        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.fired_last_tick = False
            return self.node

        # The routing spectrum: groups in spectrum EXCLUDING own group.
        routing_spectrum = self.spectrum - {self.group}

        # READ: compute weight for each neighbor connector
        # weight = 1 (base exploration) + recent other-group deposits
        weights = np.empty(len(nbrs))
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            weights[i] = 1.0 + c.recent_matching(routing_spectrum)

        # CHOOSE: weighted random selection
        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nbr = nbrs[chosen_idx]

        # FIRE: append one quantum and hop
        c = graph.edge(self.node, chosen_nbr)
        c.append(self.group)
        self.node = chosen_nbr
        self.fired_last_tick = True
        return self.node


class Entity:
    """A collection of nodes forming one body (star or planet).

    Manages a list of EntityNodes and provides aggregate measurements.
    """

    def __init__(self, name, nodes, groups, spectrum):
        """
        Args:
            name: Entity name (e.g. 'star', 'planet')
            nodes: List of initial node indices
            groups: List of group tags per node (same length as nodes)
            spectrum: Set of group tags this entity considers 'Same'
        """
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick(self, graph, rng):
        """Advance all nodes by one tick."""
        for en in self.entity_nodes:
            en.tick(graph, rng)

    def node_indices(self):
        """Current positions of all entity nodes."""
        return [en.node for en in self.entity_nodes]

    def com(self, graph):
        """Center of mass (geometric mean position of all nodes)."""
        indices = self.node_indices()
        return graph.pos[indices].mean(axis=0)

    def mean_radius(self, graph):
        """Mean distance of nodes from COM."""
        center = self.com(graph)
        indices = self.node_indices()
        dists = np.linalg.norm(graph.pos[indices] - center, axis=1)
        return float(np.mean(dists))

    def max_radius(self, graph):
        """Max distance of any node from COM."""
        center = self.com(graph)
        indices = self.node_indices()
        dists = np.linalg.norm(graph.pos[indices] - center, axis=1)
        return float(np.max(dists))

    def discharge_rate(self):
        """Fraction of nodes that fired last tick."""
        fired = sum(1 for en in self.entity_nodes if en.fired_last_tick)
        return fired / len(self.entity_nodes)

    def boundary_radiation(self, graph):
        """Total deposits on connectors where exactly one endpoint is an entity node.

        This measures the 'leak' — deposits radiating outward from the entity.
        """
        my_nodes = set(self.node_indices())
        total_deposits = 0
        n_boundary = 0

        for en in self.entity_nodes:
            for nb in graph.neighbors(en.node):
                if nb not in my_nodes:
                    c = graph.edge(en.node, nb)
                    # Count deposits from our spectrum groups on boundary connectors
                    for g, count in c.deposits.items():
                        if g in self.spectrum:
                            total_deposits += count
                    n_boundary += 1

        return total_deposits, n_boundary

    def internal_connector_stats(self, graph):
        """Stats for connectors where both endpoints are entity nodes.

        Returns (mean_length, max_length, count).
        """
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
        """Stats for connectors where exactly one endpoint is an entity node.

        Returns (mean_length, max_length, count).
        """
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
