"""
Experiment 128 v8 — Acceleration, not Velocity

The key fix: gravity and tangential reject are ACCELERATION (change of
forward direction), not velocity (added to forward direction).

Each routing decision:
  1. Compute acceleration = gravity + tangential_reject
  2. Update forward: new_forward = old_forward + acceleration * scale
  3. Route along new_forward

The forward direction accumulates bending over many hops.
Each bend is small. They add up to an orbit.
"""

import numpy as np

BASE_WEIGHT = 0.1
CHARGING_TIME = 50

STATE_CHARGING = 0
STATE_ROUTING = 1
STATE_TRANSIT = 2


class EntityBatch:
    def __init__(self, name, node_ids, n_groups, group_offset,
                 spectrum_is_star, substrate, tangential_strength=0.0):
        self.name = name
        self.N = len(node_ids)
        self.is_star = spectrum_is_star
        self.substrate = substrate
        self.tangential_strength = tangential_strength

        self.nodes = np.array(node_ids, dtype=np.int32)
        self.groups = np.array([group_offset + (i % n_groups) for i in range(self.N)], dtype=np.int32)
        self.states = np.full(self.N, STATE_CHARGING, dtype=np.int8)
        self.charge_ticks = np.zeros(self.N, dtype=np.int32)
        self.forward = np.zeros((self.N, 3), dtype=np.float32)  # current movement direction
        self.has_forward = np.zeros(self.N, dtype=bool)
        self.last_length = np.ones(self.N, dtype=np.float32)
        self.transit_dest = np.full(self.N, -1, dtype=np.int32)
        self.transit_src = np.full(self.N, -1, dtype=np.int32)
        self.transit_edge = np.full(self.N, -1, dtype=np.int32)
        self.transit_remaining = np.zeros(self.N, dtype=np.int32)
        self.hops = np.zeros(self.N, dtype=np.int64)

    def tick_transit(self, tick):
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

        self.last_length[arr_idx] = sub.conn_length(edges)
        is_star_arr = np.full(len(arr_idx), self.is_star)
        sub.deposit(edges, is_star_arr)

        # Set forward direction from the hop just completed
        dirs = sub.pos[dst] - sub.pos[src]
        norms = np.linalg.norm(dirs, axis=1, keepdims=True)
        valid = (norms > 1e-15).flatten()
        self.forward[arr_idx[valid]] = (dirs[valid] / norms[valid]).astype(np.float32)
        self.has_forward[arr_idx[valid]] = True

        self.nodes[arr_idx] = dst
        self.states[arr_idx] = STATE_CHARGING
        self.charge_ticks[arr_idx] = 0
        self.hops[arr_idx] += 1

    def tick_charging(self):
        mask = self.states == STATE_CHARGING
        self.charge_ticks[mask] += 1
        ready = mask & (self.charge_ticks >= CHARGING_TIME)
        self.states[ready] = STATE_ROUTING

    def tick_routing(self, rng):
        sub = self.substrate
        mask = self.states == STATE_ROUTING
        if not mask.any():
            return

        routing_idx = np.where(mask)[0]
        n_routing = len(routing_idx)
        my_nodes = self.nodes[routing_idx]

        nbr_nodes = sub.nbr_node[my_nodes]
        nbr_edges = sub.nbr_edge[my_nodes]
        nbr_dirs = sub.nbr_dir[my_nodes]
        nbr_valid = sub.nbr_mask[my_nodes]

        safe_edges = np.maximum(nbr_edges, 0)
        if self.is_star:
            matching = sub.conn_star[safe_edges].astype(np.float32)
        else:
            matching = sub.conn_planet[safe_edges].astype(np.float32)

        lengths = sub.conn_length(safe_edges)
        lengths = np.maximum(lengths, 0.01)
        density = matching / lengths
        density *= nbr_valid

        # GRAVITY (acceleration toward dense deposits)
        gravity = (density[:, :, None] * nbr_dirs).sum(axis=1)  # (n, 3)

        # TANGENTIAL REJECT (acceleration perpendicular to gravity)
        if self.tangential_strength > 0:
            grav_norm = np.linalg.norm(gravity, axis=1, keepdims=True)
            grav_dir = np.zeros_like(gravity)
            valid_g = (grav_norm > 1e-10).flatten()
            grav_dir[valid_g] = gravity[valid_g] / grav_norm[valid_g]

            z_hat = np.array([0, 0, 1], dtype=np.float32)
            tangential = np.cross(grav_dir, z_hat)
            tn = np.linalg.norm(tangential, axis=1, keepdims=True)
            valid_t = (tn > 1e-10).flatten()
            tangential[valid_t] /= tn[valid_t]
            tangential[~valid_t] = 0.0
            tangential *= grav_norm * self.tangential_strength
        else:
            tangential = np.zeros_like(gravity)

        # ACCELERATION = gravity + tangential (both are forces, not velocity)
        acceleration = gravity + tangential

        # UPDATE FORWARD: bend the existing direction by the acceleration
        # new_forward = old_forward + acceleration * scale
        # Scale: acceleration should BEND the direction, not overwhelm it.
        # Use last_length as the "mass" — longer last hop = more inertia
        old_fwd = self.forward[routing_idx].copy()
        has_fwd = self.has_forward[routing_idx]

        # Scale acceleration relative to forward magnitude
        # Forward has magnitude 1 (normalized). Acceleration is in deposit-density units.
        # We need a scale that makes the bending meaningful but not overwhelming.
        # Use 1/last_length: more inertia from longer hops = less bending
        inertia = self.last_length[routing_idx, None]  # (n, 1)
        inertia = np.maximum(inertia, 1.0)

        # Normalize acceleration to be comparable to forward
        acc_norm = np.linalg.norm(acceleration, axis=1, keepdims=True)
        acc_norm = np.maximum(acc_norm, 1e-10)
        acc_dir = acceleration / acc_norm

        # Bending amount: how much acceleration rotates the forward direction
        # Small number = gentle bend. Big number = sharp turn.
        bend_strength = 0.1  # fraction of forward that gets replaced by acceleration direction

        new_fwd = np.where(
            has_fwd[:, None],
            old_fwd * (1 - bend_strength) + acc_dir * bend_strength,
            acc_dir  # first hop: no forward, use acceleration as initial direction
        )

        # Normalize
        fn = np.linalg.norm(new_fwd, axis=1, keepdims=True)
        valid_f = (fn > 1e-15).flatten()
        new_fwd[valid_f] /= fn[valid_f]

        # Store updated forward for next routing decision
        self.forward[routing_idx] = new_fwd.astype(np.float32)
        self.has_forward[routing_idx] = True

        # ROUTE along the new forward direction
        alignment = (new_fwd[:, None, :] * nbr_dirs).sum(axis=2)
        alignment = np.maximum(alignment, 0.0)
        alignment *= nbr_valid
        weights = alignment + BASE_WEIGHT * nbr_valid.astype(np.float32)

        weight_sums = weights.sum(axis=1, keepdims=True)
        weight_sums = np.maximum(weight_sums, 1e-10)
        probs = weights / weight_sums

        cum_probs = probs.cumsum(axis=1)
        r = rng.random(n_routing)[:, None]
        chosen_k = (cum_probs < r).sum(axis=1)
        chosen_k = np.minimum(chosen_k, sub.degree[my_nodes] - 1)

        chosen_nb = nbr_nodes[np.arange(n_routing), chosen_k]
        chosen_edge = nbr_edges[np.arange(n_routing), chosen_k]
        chosen_lengths = sub.conn_length(chosen_edge)

        self.states[routing_idx] = STATE_TRANSIT
        self.transit_src[routing_idx] = my_nodes
        self.transit_dest[routing_idx] = chosen_nb
        self.transit_edge[routing_idx] = chosen_edge
        self.transit_remaining[routing_idx] = np.maximum(1, chosen_lengths.astype(np.int32))

    def com(self):
        return self.substrate.pos[self.nodes].mean(axis=0)

    def mean_radius(self):
        center = self.com()
        return float(np.linalg.norm(self.substrate.pos[self.nodes] - center, axis=1).mean())

    def total_hops(self):
        return int(self.hops.sum())
