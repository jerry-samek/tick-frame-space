"""
Entity logic for Experiment 118 v15.

v13 routing (forward + gravity from accumulated density + length momentum)
plus REACTIVE CHARGING: entity waits for propagating quanta to arrive
before firing. Velocity = local quantum flux. Near star = fast, far = slow.
"""

import numpy as np

BASE_WEIGHT = 0.1
THRESHOLD = 1       # fire on first quantum arrival
MAX_WAIT = 200      # safety fallback (ticks)

STATE_CHARGING = 0
STATE_ROUTING = 1
STATE_TRANSIT = 2


class EntityNode:
    __slots__ = ('node', 'group', 'spectrum', 'state',
                 'charge', 'ticks_waiting',
                 'arrival_dir', 'arrived_from', 'last_traversal_length',
                 'transit_edge', 'transit_dest', 'transit_src',
                 'transit_remaining', 'hops_completed', 'last_hop_tick',
                 'triggered_by_quantum', 'triggered_by_timeout')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.state = STATE_CHARGING
        self.charge = 0
        self.ticks_waiting = 0
        self.arrival_dir = None
        self.arrived_from = None
        self.last_traversal_length = 1.0
        self.transit_edge = None
        self.transit_dest = None
        self.transit_src = None
        self.transit_remaining = 0
        self.hops_completed = 0
        self.last_hop_tick = 0
        self.triggered_by_quantum = 0  # count of quantum-triggered hops
        self.triggered_by_timeout = 0  # count of timeout-triggered hops

    def tick_transit(self, graph, tick, quantum_field):
        """Phase 1: process transit. On arrival: deposit + emit quantum."""
        if self.state != STATE_TRANSIT:
            return
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            dest = self.transit_dest
            ek = graph.edge_key(self.transit_src, dest)
            c = graph.connectors[ek]

            self.last_traversal_length = c.length

            # Deposit on arrival
            c.append(self.group, self.transit_src, dest)

            # Emit quantum into propagation system
            quantum_field.add(self.group, dest, self.transit_src)

            # Set arrival direction
            d = graph.pos[dest] - graph.pos[self.transit_src]
            n = np.linalg.norm(d)
            self.arrival_dir = d / n if n > 1e-15 else None

            self.arrived_from = self.transit_src
            self.node = dest
            self.state = STATE_CHARGING
            self.charge = 0
            self.ticks_waiting = 0
            self.last_hop_tick = tick

    def tick_charging(self, graph, quantum_field, tick):
        """Phase 3: reactive charging from propagating quanta."""
        if self.state != STATE_CHARGING:
            return

        # Check for quantum arrivals on local connectors
        arrivals = quantum_field.deposits_this_tick_at(self.node)
        self.charge += arrivals
        self.ticks_waiting += 1

        if self.charge >= THRESHOLD:
            self.state = STATE_ROUTING
            self.triggered_by_quantum += 1
        elif self.ticks_waiting >= MAX_WAIT:
            self.state = STATE_ROUTING
            self.triggered_by_timeout += 1

    def tick_routing(self, graph, rng):
        """Phase 4: forward + gravity routing (same as v13)."""
        if self.state != STATE_ROUTING:
            return

        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.state = STATE_CHARGING
            self.charge = 0
            self.ticks_waiting = 0
            return

        # GRAVITY: accumulated density field
        gravity = np.zeros(3)
        for nb in nbrs:
            c = graph.edge(self.node, nb)
            matching = sum(c.deposits.get(g, 0) for g in self.spectrum)
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

    def tick_transit(self, graph, tick, quantum_field):
        for en in self.entity_nodes:
            en.tick_transit(graph, tick, quantum_field)

    def tick_charging(self, graph, quantum_field, tick):
        for en in self.entity_nodes:
            en.tick_charging(graph, quantum_field, tick)

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

    def trigger_stats(self):
        q = sum(en.triggered_by_quantum for en in self.entity_nodes)
        t = sum(en.triggered_by_timeout for en in self.entity_nodes)
        return q, t

    def mean_charging_time(self, tick):
        times = [tick - en.last_hop_tick for en in self.entity_nodes
                 if en.state == STATE_CHARGING and en.last_hop_tick > 0]
        return float(np.mean(times)) if times else 0.0
