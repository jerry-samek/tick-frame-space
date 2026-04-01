"""
Entity tick logic for Experiment 118 v5.

Entity nodes:
  - Always emit 1 deposit per tick (spontaneous emission)
  - Incoming deposits influence routing direction (weighted random walk)
  - Hop to the chosen neighbor after emitting

Measurement methods reused from v4.
"""

import numpy as np


class EntityNode:
    """A single node belonging to an entity (star or planet).

    Routes toward incoming deposits from other groups in spectrum,
    emits one deposit per tick, hops to chosen neighbor.
    """

    __slots__ = ('node', 'group_idx', 'spectrum_indices', 'fired_last_tick')

    def __init__(self, node, group_idx, spectrum_indices):
        self.node = node
        self.group_idx = group_idx          # integer group index
        self.spectrum_indices = spectrum_indices  # set of group indices considered Same
        self.fired_last_tick = False

    def absorb(self, engine):
        """ABSORB phase: consume one OTHER-GROUP deposit from spectrum.

        Absorbs from spectrum groups EXCLUDING own group. This prevents
        the node from eating its own trail (own-group deposits pass through).
        Matches RAW 118: consumption is transformation of Different into Same.

        Must be called BEFORE engine.propagate() so the absorbed deposit
        is removed from flows before redistribution. Modifies flows in-place.
        """
        absorb_groups = self.spectrum_indices - {self.group_idx}

        best_incoming = None
        best_count = 0
        for d in engine.incoming[self.node]:
            flow = engine.flows[d]
            matching = sum(int(flow[g]) for g in absorb_groups)
            if matching > best_count:
                best_count = matching
                best_incoming = d

        if best_incoming is not None and best_count > 0:
            for g in absorb_groups:
                if engine.absorb_one(best_incoming, g):
                    break

    def emit_and_hop(self, engine, graph, rng):
        """EMIT phase: route, emit one deposit, hop.

        Must be called AFTER engine.propagate() so emissions go into flows_next.
        """
        out_edges = engine.outgoing[self.node]
        if not out_edges:
            self.fired_last_tick = False
            return self.node

        routing_groups = self.spectrum_indices - {self.group_idx}

        # ROUTE: weight by incoming other-group deposits (read from flows)
        weights = np.ones(len(out_edges), dtype=np.float64)
        for i, d in enumerate(out_edges):
            rev = engine.reverse[d]
            flow = engine.flows[rev]
            for g in routing_groups:
                weights[i] += flow[g]

        weights /= weights.sum()
        chosen_idx = rng.choice(len(out_edges), p=weights)
        chosen_edge = out_edges[chosen_idx]

        # EMIT + HOP
        engine.emit(chosen_edge, self.group_idx)
        self.node = engine.dst[chosen_edge]
        self.fired_last_tick = True
        return self.node


class Entity:
    """A collection of nodes forming one body (star or planet).

    Manages EntityNodes and provides aggregate measurements.
    """

    def __init__(self, name, nodes, group_indices, spectrum_indices):
        """
        Args:
            name: Entity name (e.g. 'star', 'planet')
            nodes: List of initial node indices
            group_indices: List of integer group indices per node
            spectrum_indices: Set of group indices this entity considers Same
        """
        self.name = name
        self.spectrum_indices = spectrum_indices
        self.entity_nodes = [
            EntityNode(n, g, spectrum_indices)
            for n, g in zip(nodes, group_indices)
        ]

    def absorb(self, engine):
        """Phase 1: all nodes absorb. Call BEFORE engine.propagate()."""
        for en in self.entity_nodes:
            en.absorb(engine)

    def emit_and_hop(self, engine, graph, rng):
        """Phase 2: all nodes emit and hop. Call AFTER engine.propagate()."""
        for en in self.entity_nodes:
            en.emit_and_hop(engine, graph, rng)

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

    def boundary_flux(self, engine, graph):
        """Count deposits flowing outward through entity boundary this tick.

        Boundary = edges where one endpoint is entity, one is not.
        Flux = deposits on outward directed edges (entity -> non-entity)
        in the current flow buffer.

        Returns (total_flux, n_boundary_edges).
        """
        my_nodes = set(self.node_indices())
        total_flux = 0
        n_boundary = 0

        for en in self.entity_nodes:
            for nb in graph.neighbors(en.node):
                if nb not in my_nodes:
                    d = engine.directed_id(en.node, nb)
                    total_flux += int(engine.flows[d].sum())
                    n_boundary += 1

        return total_flux, n_boundary
