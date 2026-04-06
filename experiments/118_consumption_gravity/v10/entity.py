"""
Reactive entity logic for Experiment 118 v10.

Entities fire in RESPONSE to incoming deposits, not spontaneously.
Three states: CHARGING (idle, waiting) -> FIRING (route + discharge) -> IN_TRANSIT.

Momentum from trigger direction: the incoming deposit came from a specific
direction. The outgoing discharge is biased forward.
"""

import numpy as np

BASE_WEIGHT = 1.0
THRESHOLD = 1  # fire as soon as 1 deposit arrives

STATE_CHARGING = 0
STATE_FIRING = 1
STATE_TRANSIT = 2


class EntityNode:
    __slots__ = ('node', 'group', 'spectrum', 'state',
                 'charge', 'trigger_src', 'trigger_deposits',
                 'transit_edge', 'transit_dest', 'transit_src',
                 'transit_remaining', 'hops_completed',
                 'arrived_from', 'last_hop_tick')

    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.state = STATE_CHARGING
        self.charge = 0
        self.trigger_src = None       # node the triggering deposit came from
        self.trigger_deposits = 0     # deposit count on triggering connector
        self.transit_edge = None
        self.transit_dest = None
        self.transit_src = None
        self.transit_remaining = 0
        self.hops_completed = 0
        self.arrived_from = None      # node we arrived from (for deposit-on-arrival)
        self.last_hop_tick = 0

    def tick_transit(self, graph, tick):
        """Process IN_TRANSIT state. Called in phase 1 of tick loop."""
        if self.state != STATE_TRANSIT:
            return
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            # ARRIVE: deposit on traversed connector
            ek = graph.edge_key(self.transit_src, self.transit_dest)
            graph.connectors[ek].append(self.group, self.transit_src, self.transit_dest)
            self.arrived_from = self.transit_src
            self.node = self.transit_dest
            self.state = STATE_CHARGING
            self.charge = 0
            self.trigger_src = None
            self.last_hop_tick = tick

    def tick_charging(self, graph, own_entity_nodes):
        """Process CHARGING state. Called in phase 2 of tick loop.

        Check local connectors for deposits this tick from OTHER entities.
        Self-deposits (from nodes in own_entity_nodes arriving this tick)
        should NOT self-trigger.
        """
        if self.state != STATE_CHARGING:
            return

        own_nodes = own_entity_nodes
        for nb in graph.neighbors(self.node):
            ek = graph.edge_key(self.node, nb)
            c = graph.connectors[ek]
            if c.deposits_this_tick > 0:
                # Check: was this deposit from our own entity arriving?
                # Self-triggering is prevented by checking if source is in own nodes
                # AND the deposit just happened this tick (it's the arrival deposit)
                src = c.last_deposit_src
                if src is not None and src == self.node:
                    continue  # deposit was from us hopping away — skip
                # External deposit detected
                self.charge += c.deposits_this_tick
                self.trigger_src = src if src != self.node else c.last_deposit_dst
                self.trigger_deposits = c.deposits_this_tick

        if self.charge >= THRESHOLD:
            self.state = STATE_FIRING

    def tick_firing(self, graph, rng):
        """Process FIRING state. Called in phase 3 of tick loop."""
        if self.state != STATE_FIRING:
            return

        nbrs = graph.neighbors(self.node)
        if not nbrs:
            self.state = STATE_CHARGING
            self.charge = 0
            return

        # Routing: total deposit count per connector
        scores = np.empty(len(nbrs), dtype=np.float64)
        for i, nb in enumerate(nbrs):
            c = graph.edge(self.node, nb)
            scores[i] = c.total

        # Momentum bias from trigger direction
        momentum = np.zeros(len(nbrs), dtype=np.float64)
        if self.trigger_src is not None:
            trigger_dir = graph.pos[self.node] - graph.pos[self.trigger_src]
            trigger_len = np.linalg.norm(trigger_dir)
            if trigger_len > 1e-15:
                trigger_dir /= trigger_len
                strength = self.trigger_deposits

                for i, nb in enumerate(nbrs):
                    out_dir = graph.pos[nb] - graph.pos[self.node]
                    out_len = np.linalg.norm(out_dir)
                    if out_len > 1e-15:
                        forward = np.dot(trigger_dir, out_dir / out_len)
                        momentum[i] = strength * max(0.0, forward)

        weights = scores + momentum + BASE_WEIGHT
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
        self.charge = 0
        self.trigger_src = None
        self.trigger_deposits = 0
        self.hops_completed += 1


class Entity:
    def __init__(self, name, nodes, groups, spectrum):
        self.name = name
        self.spectrum = frozenset(spectrum)
        self.entity_nodes = [
            EntityNode(n, g, self.spectrum) for n, g in zip(nodes, groups)
        ]

    def seed_deposits(self, graph):
        """Bootstrap: each entity node deposits on all local connectors.

        The entity's presence IS the first deposit event. Without this,
        the reactive system is permanently frozen.
        """
        for en in self.entity_nodes:
            for nb in graph.neighbors(en.node):
                ek = graph.edge_key(en.node, nb)
                graph.connectors[ek].append(en.group, en.node, nb)
        print(f"  {self.name}: seeded deposits on local connectors")

    def tick_transit(self, graph, tick):
        for en in self.entity_nodes:
            en.tick_transit(graph, tick)

    def tick_charging(self, graph):
        own_nodes = set(en.node for en in self.entity_nodes)
        for en in self.entity_nodes:
            en.tick_charging(graph, own_nodes)

    def tick_firing(self, graph, rng):
        for en in self.entity_nodes:
            en.tick_firing(graph, rng)

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
        charging = sum(1 for en in self.entity_nodes if en.state == STATE_CHARGING) / n
        transit = sum(1 for en in self.entity_nodes if en.state == STATE_TRANSIT) / n
        firing = sum(1 for en in self.entity_nodes if en.state == STATE_FIRING) / n
        return charging, firing, transit

    def total_hops(self):
        return sum(en.hops_completed for en in self.entity_nodes)

    def mean_charging_time(self, tick):
        """Mean ticks since last hop for CHARGING nodes."""
        times = [tick - en.last_hop_tick for en in self.entity_nodes
                 if en.state == STATE_CHARGING and en.last_hop_tick > 0]
        return float(np.mean(times)) if times else 0.0
