"""
Newtonian entity logic for Experiment 118 v12.

Identical to v11. The Same/Different extension rule is in graph.py's
Connector class — entity code doesn't change. The group tag passed to
connector.append() is used by the Connector to classify Same vs Different.
"""

import numpy as np

BASE_WEIGHT = 1.0
DEPOSIT_WEIGHT = 0.01   # low — direction dominates, deposits break ties
CHARGING_TIME = 50       # ticks of idle charging per hop

STATE_CHARGING = 0
STATE_ROUTING = 1
STATE_TRANSIT = 2


class EntityNode:
    __slots__ = ('node', 'group', 'spectrum', 'state',
                 'charge_ticks', 'arrival_dir', 'arrived_from',
                 'deflection', 'deposits_received',
                 'transit_edge', 'transit_dest', 'transit_src',
                 'transit_remaining', 'hops_completed', 'last_hop_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.state = STATE_CHARGING
        self.charge_ticks = 0
        self.arrival_dir = None     # None = first hop, no inertia yet
        self.arrived_from = None
        self.deflection = np.zeros(3)
        self.deposits_received = 0
        self.transit_edge = None
        self.transit_dest = None
        self.transit_src = None
        self.transit_remaining = 0
        self.hops_completed = 0
        self.last_hop_tick = 0

    def tick_transit(self, graph, tick):
        """Phase 1: process IN_TRANSIT nodes."""
        if self.state != STATE_TRANSIT:
            return
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            # ARRIVE: deposit on traversed connector
            dest = self.transit_dest
            ek = graph.edge_key(self.transit_src, dest)
            graph.connectors[ek].append(self.group, self.transit_src, dest)

            # Set arrival direction (for forward default)
            d = graph.pos[dest] - graph.pos[self.transit_src]
            n = np.linalg.norm(d)
            self.arrival_dir = d / n if n > 1e-15 else None

            self.arrived_from = self.transit_src
            self.node = dest
            self.state = STATE_CHARGING
            self.charge_ticks = 0
            self.deflection = np.zeros(3)
            self.deposits_received = 0
            self.last_hop_tick = tick

    def tick_charging(self, graph, own_node_set):
        """Phase 2: accumulate deflection from deposits arriving this tick."""
        if self.state != STATE_CHARGING:
            return

        # Read deposits on local connectors this tick
        for nb in graph.neighbors(self.node):
            ek = graph.edge_key(self.node, nb)
            c = graph.connectors[ek]
            if c.deposits_this_tick > 0:
                src = c.last_deposit_src
                # Skip own deposits (Trap 24)
                if src is not None and src == self.node:
                    continue
                if src is not None:
                    toward = graph.pos[self.node] - graph.pos[src]
                    n = np.linalg.norm(toward)
                    if n > 1e-15:
                        self.deflection += (toward / n) * c.deposits_this_tick
                        self.deposits_received += c.deposits_this_tick

        self.charge_ticks += 1
        if self.charge_ticks >= CHARGING_TIME:
            self.state = STATE_ROUTING

    def tick_routing(self, graph, rng):
        """Phase 3: route using forward default + deflection."""
        if self.state != STATE_ROUTING:
            return

        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.state = STATE_CHARGING
            self.charge_ticks = 0
            return

        # Build combined direction: forward (inertia) + deflection (gravity)
        if self.arrival_dir is not None:
            combined = self.arrival_dir + self.deflection
            n = np.linalg.norm(combined)
            combined = combined / n if n > 1e-15 else self.arrival_dir.copy()
        else:
            # First hop: use deflection only, or None for random
            n = np.linalg.norm(self.deflection)
            combined = self.deflection / n if n > 1e-15 else None

        # Score each outgoing connector
        weights = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            out_dir = graph.pos[nb] - graph.pos[self.node]
            out_n = np.linalg.norm(out_dir)

            # Direction alignment (inertia + gravity)
            if combined is not None and out_n > 1e-15:
                dir_score = np.dot(combined, out_dir / out_n)
                dir_score = max(0.0, dir_score)  # no backward hops
            else:
                dir_score = 0.0

            # Deposit count on connector (secondary signal)
            c = graph.edge(self.node, nb)
            dep_score = c.total * DEPOSIT_WEIGHT

            weights[i] = dir_score + dep_score + BASE_WEIGHT

        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nb = nbrs[chosen_idx]

        # Begin traversal
        ek = graph.edge_key(self.node, chosen_nb)
        c = graph.connectors[ek]
        self.state = STATE_TRANSIT
        self.transit_edge = ek
        self.transit_src = self.node
        self.transit_dest = chosen_nb
        self.transit_remaining = max(1, int(c.length))
        self.hops_completed += 1


class Entity:
    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def tick_transit(self, graph, tick):
        for en in self.entity_nodes:
            en.tick_transit(graph, tick)

    def tick_charging(self, graph):
        own = set(en.node for en in self.entity_nodes)
        for en in self.entity_nodes:
            en.tick_charging(graph, own)

    def tick_routing(self, graph, rng):
        for en in self.entity_nodes:
            en.tick_routing(graph, rng)

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

    def state_fractions(self):
        n = len(self.entity_nodes)
        ch = sum(1 for en in self.entity_nodes if en.state == STATE_CHARGING) / n
        rt = sum(1 for en in self.entity_nodes if en.state == STATE_ROUTING) / n
        tr = sum(1 for en in self.entity_nodes if en.state == STATE_TRANSIT) / n
        return ch, rt, tr

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def mean_deflection(self):
        """Mean deflection magnitude across charging nodes."""
        mags = [np.linalg.norm(en.deflection) for en in self.entity_nodes
                if en.state == STATE_CHARGING and en.charge_ticks > 0]
        return float(np.mean(mags)) if mags else 0.0

    def mean_charging_time(self, tick):
        times = [tick - en.last_hop_tick for en in self.entity_nodes
                 if en.state == STATE_CHARGING and en.last_hop_tick > 0]
        return float(np.mean(times)) if times else 0.0
