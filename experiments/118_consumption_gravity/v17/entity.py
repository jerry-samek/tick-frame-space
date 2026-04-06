"""
Entity logic for Experiment 118 v17.

v16 base (forward + gravity + length momentum + consumption) PLUS
inter-group routing for internal circulation.

The gravity vector routes toward OTHER groups in spectrum (not own group).
Star node s0 routes toward {s1,s2,s3} deposits. Creates circulation:
s0 chases s1, s1 chases s2, etc. Star becomes a spinning body.

The connector Same/Different rule is unchanged: all star groups are Same
to each other. Internal connectors don't grow. Only the ROUTING changes.
"""

import numpy as np

BASE_WEIGHT = 0.1
CHARGING_TIME = 50

STATE_CHARGING = 0
STATE_ROUTING = 1
STATE_TRANSIT = 2


class EntityNode:
    __slots__ = ('node', 'group', 'spectrum', 'routing_spectrum', 'state',
                 'charge_ticks', 'arrival_dir', 'arrived_from',
                 'last_traversal_length',
                 'transit_edge', 'transit_dest', 'transit_src',
                 'transit_remaining', 'hops_completed', 'last_hop_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum  # full spectrum (for connector Same/Different)
        # Routing spectrum: OTHER groups in spectrum (for internal circulation)
        self.routing_spectrum = spectrum - {group}
        self.state = STATE_CHARGING
        self.charge_ticks = 0
        self.arrival_dir = None
        self.arrived_from = None
        self.last_traversal_length = 1.0
        self.transit_edge = None
        self.transit_dest = None
        self.transit_src = None
        self.transit_remaining = 0
        self.hops_completed = 0
        self.last_hop_tick = 0

    def tick_transit(self, graph, tick):
        if self.state != STATE_TRANSIT:
            return
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            dest = self.transit_dest
            ek = graph.edge_key(self.transit_src, dest)
            c = graph.connectors[ek]

            self.last_traversal_length = c.length
            c.append(self.group, self.transit_src, dest)

            d = graph.pos[dest] - graph.pos[self.transit_src]
            n = np.linalg.norm(d)
            self.arrival_dir = d / n if n > 1e-15 else None

            self.arrived_from = self.transit_src
            self.node = dest
            self.state = STATE_CHARGING
            self.charge_ticks = 0
            self.last_hop_tick = tick

    def tick_charging(self, graph):
        if self.state != STATE_CHARGING:
            return
        self.charge_ticks += 1
        if self.charge_ticks >= CHARGING_TIME:
            self.state = STATE_ROUTING

    def tick_routing(self, graph, rng):
        if self.state != STATE_ROUTING:
            return

        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.state = STATE_CHARGING
            self.charge_ticks = 0
            return

        # GRAVITY: route toward OTHER groups in spectrum (circulation!)
        # s0 routes toward {s1,s2,s3} deposits → internal circulation
        # Planet p0 routes toward {p1} deposits → planet cohesion
        gravity = np.zeros(3)
        for nb in nbrs:
            c = graph.edge(self.node, nb)
            matching = sum(c.deposits.get(g, 0) for g in self.routing_spectrum)
            density = matching / c.length if c.length > 0 else 0.0
            direction = graph.pos[nb] - graph.pos[self.node]
            dn = np.linalg.norm(direction)
            if dn > 1e-15:
                gravity += density * (direction / dn)

        # FORWARD: proportional to last traversal length
        if self.arrival_dir is not None:
            forward = self.last_traversal_length * self.arrival_dir
        else:
            forward = np.zeros(3)

        # COMBINE
        combined = forward + gravity
        cn = np.linalg.norm(combined)
        if cn > 1e-15:
            combined /= cn
        elif self.arrival_dir is not None:
            combined = self.arrival_dir.copy()
        else:
            combined = None

        # Score outgoing connectors
        weights = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            out_dir = graph.pos[nb] - graph.pos[self.node]
            on = np.linalg.norm(out_dir)
            if combined is not None and on > 1e-15:
                alignment = np.dot(combined, out_dir / on)
                weights[i] = max(0.0, alignment)
            else:
                weights[i] = 0.0
            weights[i] += BASE_WEIGHT

        weights /= weights.sum()
        chosen_idx = rng.choice(len(nbrs), p=weights)
        chosen_nb = nbrs[chosen_idx]

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
        for en in self.entity_nodes:
            en.tick_charging(graph)

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

    def state_fractions(self):
        n = len(self.entity_nodes)
        ch = sum(1 for en in self.entity_nodes if en.state == STATE_CHARGING) / n
        rt = sum(1 for en in self.entity_nodes if en.state == STATE_ROUTING) / n
        tr = sum(1 for en in self.entity_nodes if en.state == STATE_TRANSIT) / n
        return ch, rt, tr

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def mean_gravity_forward_ratio(self, graph):
        ratios = []
        for en in self.entity_nodes:
            if en.arrival_dir is None:
                continue
            gravity = np.zeros(3)
            for nb in graph.neighbors(en.node):
                c = graph.edge(en.node, nb)
                matching = sum(c.deposits.get(g, 0) for g in en.routing_spectrum)
                density = matching / c.length if c.length > 0 else 0
                direction = graph.pos[nb] - graph.pos[en.node]
                dn = np.linalg.norm(direction)
                if dn > 1e-15:
                    gravity += density * (direction / dn)
            grav_mag = np.linalg.norm(gravity)
            fwd_mag = en.last_traversal_length
            if fwd_mag > 0:
                ratios.append(grav_mag / fwd_mag)
        return float(np.mean(ratios)) if ratios else 0.0
