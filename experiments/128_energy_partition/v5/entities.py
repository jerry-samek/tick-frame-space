"""
Experiment 128 v5 — Vectorized Entity State

Entities are arrays of indices into the substrate. No Python objects.
All operations batched across all entities of the same type.
"""

import numpy as np

BASE_WEIGHT = 0.1
CHARGING_TIME = 50

STATE_CHARGING = 0
STATE_ROUTING = 1
STATE_TRANSIT = 2


class EntityBatch:
    """A batch of entity nodes (star or planet), all state as arrays."""

    def __init__(self, name, node_ids, n_groups, group_offset, spectrum_is_star, substrate):
        self.name = name
        self.N = len(node_ids)
        self.is_star = spectrum_is_star  # True for star entities
        self.substrate = substrate

        # State arrays
        self.nodes = np.array(node_ids, dtype=np.int32)
        self.groups = np.array([group_offset + (i % n_groups) for i in range(self.N)], dtype=np.int32)
        self.states = np.full(self.N, STATE_CHARGING, dtype=np.int8)
        self.charge_ticks = np.zeros(self.N, dtype=np.int32)
        self.arrival_dir = np.zeros((self.N, 3), dtype=np.float32)
        self.has_arrival_dir = np.zeros(self.N, dtype=bool)
        self.last_length = np.ones(self.N, dtype=np.float32)
        self.transit_dest = np.full(self.N, -1, dtype=np.int32)
        self.transit_src = np.full(self.N, -1, dtype=np.int32)
        self.transit_edge = np.full(self.N, -1, dtype=np.int32)
        self.transit_remaining = np.zeros(self.N, dtype=np.int32)
        self.hops = np.zeros(self.N, dtype=np.int64)

    def tick_transit(self, tick):
        """Phase 1: decrement transit counters, process arrivals."""
        sub = self.substrate
        mask = self.states == STATE_TRANSIT
        if not mask.any():
            return

        self.transit_remaining[mask] -= 1
        arrived = mask & (self.transit_remaining <= 0)

        if not arrived.any():
            return

        arr_idx = np.where(arrived)[0]
        src = self.transit_src[arr_idx]
        dst = self.transit_dest[arr_idx]
        edges = self.transit_edge[arr_idx]

        # Record length before deposit
        self.last_length[arr_idx] = sub.conn_length(edges)

        # Deposit on arrival connectors
        is_star_arr = np.full(len(arr_idx), self.is_star)
        sub.deposit(edges, is_star_arr)

        # Set arrival direction
        dirs = sub.pos[dst] - sub.pos[src]
        norms = np.linalg.norm(dirs, axis=1, keepdims=True)
        valid = (norms > 1e-15).flatten()
        self.arrival_dir[arr_idx[valid]] = (dirs[valid] / norms[valid]).astype(np.float32)
        self.has_arrival_dir[arr_idx[valid]] = True

        # Update state
        self.nodes[arr_idx] = dst
        self.states[arr_idx] = STATE_CHARGING
        self.charge_ticks[arr_idx] = 0
        self.hops[arr_idx] += 1

    def tick_charging(self):
        """Phase 2: increment charge counters."""
        mask = self.states == STATE_CHARGING
        self.charge_ticks[mask] += 1
        ready = mask & (self.charge_ticks >= CHARGING_TIME)
        self.states[ready] = STATE_ROUTING

    def tick_routing(self, rng):
        """Phase 3: vectorized routing decisions."""
        sub = self.substrate
        mask = self.states == STATE_ROUTING
        if not mask.any():
            return

        routing_idx = np.where(mask)[0]
        n_routing = len(routing_idx)
        my_nodes = self.nodes[routing_idx]

        # Gather neighbor data for all routing entities
        nbr_nodes = sub.nbr_node[my_nodes]     # (n_routing, max_k)
        nbr_edges = sub.nbr_edge[my_nodes]     # (n_routing, max_k)
        nbr_dirs = sub.nbr_dir[my_nodes]       # (n_routing, max_k, 3)
        nbr_valid = sub.nbr_mask[my_nodes]     # (n_routing, max_k)

        # Deposit density per neighbor connector
        # Use the entity's own spectrum for matching
        safe_edges = np.maximum(nbr_edges, 0)  # avoid -1 indexing
        if self.is_star:
            matching = sub.conn_star[safe_edges].astype(np.float32)
        else:
            matching = sub.conn_planet[safe_edges].astype(np.float32)

        lengths = sub.conn_length(safe_edges)
        lengths = np.maximum(lengths, 0.01)
        density = matching / lengths            # (n_routing, max_k)
        density *= nbr_valid                    # zero out invalid neighbors

        # GRAVITY: sum(density * direction) per entity
        gravity = (density[:, :, None] * nbr_dirs).sum(axis=1)  # (n_routing, 3)

        # FORWARD: last_length * arrival_dir
        fwd = self.last_length[routing_idx, None] * self.arrival_dir[routing_idx]  # (n_routing, 3)
        has_fwd = self.has_arrival_dir[routing_idx]
        fwd[~has_fwd] = 0.0

        # COMBINE
        combined = fwd + gravity                # (n_routing, 3)
        cn = np.linalg.norm(combined, axis=1, keepdims=True)
        valid_combined = (cn > 1e-15).flatten()
        combined[valid_combined] /= cn[valid_combined]
        # For invalid: use arrival_dir if available, else zero
        no_combined = ~valid_combined & has_fwd
        combined[no_combined] = self.arrival_dir[routing_idx[no_combined]]

        # SCORE: alignment of each neighbor with combined direction
        # (n_routing, max_k) = dot product of (n_routing, 1, 3) with (n_routing, max_k, 3)
        alignment = (combined[:, None, :] * nbr_dirs).sum(axis=2)  # (n_routing, max_k)
        alignment = np.maximum(alignment, 0.0)  # no backward hops
        alignment *= nbr_valid                   # zero invalid

        # Add base weight
        weights = alignment + BASE_WEIGHT * nbr_valid.astype(np.float32)

        # Weighted random choice per entity
        weight_sums = weights.sum(axis=1, keepdims=True)
        weight_sums = np.maximum(weight_sums, 1e-10)
        probs = weights / weight_sums            # (n_routing, max_k)

        # Vectorized weighted random choice using cumsum + searchsorted
        cum_probs = probs.cumsum(axis=1)         # (n_routing, max_k)
        r = rng.random(n_routing)[:, None]       # (n_routing, 1)
        chosen_k = (cum_probs < r).sum(axis=1)   # (n_routing,) — index of chosen neighbor
        chosen_k = np.minimum(chosen_k, sub.degree[my_nodes] - 1)  # clamp

        # Gather chosen neighbor info
        chosen_nb = nbr_nodes[np.arange(n_routing), chosen_k]
        chosen_edge = nbr_edges[np.arange(n_routing), chosen_k]
        chosen_lengths = sub.conn_length(chosen_edge)

        # Begin transit
        self.states[routing_idx] = STATE_TRANSIT
        self.transit_src[routing_idx] = my_nodes
        self.transit_dest[routing_idx] = chosen_nb
        self.transit_edge[routing_idx] = chosen_edge
        self.transit_remaining[routing_idx] = np.maximum(1, chosen_lengths.astype(np.int32))

    # ── Measurements ──

    def com(self):
        return self.substrate.pos[self.nodes].mean(axis=0)

    def mean_radius(self):
        center = self.com()
        dists = np.linalg.norm(self.substrate.pos[self.nodes] - center, axis=1)
        return float(dists.mean())

    def total_hops(self):
        return int(self.hops.sum())

    def state_counts(self):
        return (int((self.states == STATE_CHARGING).sum()),
                int((self.states == STATE_ROUTING).sum()),
                int((self.states == STATE_TRANSIT).sum()))
