"""
Deposit propagation engine for Experiment 118 v5.

Deposits travel on fixed-length connectors at 1 hop/tick.
DIRECTED propagation: deposits continue in a straight line through
the graph, choosing the most forward-aligned outgoing edge at each
node. This produces beams (not diffusion), giving 1/r^2 geometric
falloff and a real density gradient.

Double-buffered numpy arrays indexed by directed edge ID.
"""

import numpy as np
from collections import defaultdict


class PropagationEngine:
    """Manages deposit flows across directed graph edges.

    Each undirected edge (a,b) produces 2 directed edges:
      - 2*eid     : a -> b (deposits arriving at b)
      - 2*eid + 1 : b -> a (deposits arriving at a)

    Flows are double-buffered:
      - flows      : current tick's arrivals (read buffer)
      - flows_next : next tick's arrivals (write buffer)
    """

    def __init__(self, graph, n_groups, seed=42):
        self.graph = graph
        self.n_groups = n_groups
        self.rng = np.random.default_rng(seed)
        self.n_nodes = graph.n_nodes
        self.n_edges = len(graph.edge_list)
        self.n_directed = 2 * self.n_edges

        # Build directed edge index arrays
        self.src = np.empty(self.n_directed, dtype=np.int32)
        self.dst = np.empty(self.n_directed, dtype=np.int32)
        self.reverse = np.empty(self.n_directed, dtype=np.int32)

        # Map (node_a, node_b) -> directed edge id (a->b)
        self._directed_id = {}

        for eid, (a, b) in enumerate(graph.edge_list):
            d_ab = 2 * eid
            d_ba = 2 * eid + 1
            self.src[d_ab], self.dst[d_ab] = a, b
            self.src[d_ba], self.dst[d_ba] = b, a
            self.reverse[d_ab] = d_ba
            self.reverse[d_ba] = d_ab
            self._directed_id[(a, b)] = d_ab
            self._directed_id[(b, a)] = d_ba

        # Per-node incoming and outgoing directed edge lists
        self.incoming = [[] for _ in range(self.n_nodes)]
        self.outgoing = [[] for _ in range(self.n_nodes)]
        for d in range(self.n_directed):
            self.incoming[self.dst[d]].append(d)
            self.outgoing[self.src[d]].append(d)

        # Build deterministic forward redirect (straight-line propagation)
        self._build_forward_redirect()

        # Flow buffers: (n_directed, n_groups) int32
        self.flows = np.zeros((self.n_directed, n_groups), dtype=np.int32)
        self.flows_next = np.zeros((self.n_directed, n_groups), dtype=np.int32)

        # Entity node mask
        self._is_entity = np.zeros(self.n_nodes, dtype=bool)

        # Conservation tracking
        self.total_emitted = 0
        self.total_absorbed = 0

        print(f"PropagationEngine: {self.n_directed} directed edges, "
              f"{n_groups} groups, forward propagation")

    def _build_forward_redirect(self):
        """Precompute forward redirect: for each directed edge A->B,
        find the outgoing edge B->C that best continues the direction A->B.

        Uses embedded coordinates (dot product of direction vectors).
        Computed once at construction — propagation is deterministic.
        """
        pos = self.graph.pos
        self.forward_redirect = np.zeros(self.n_directed, dtype=np.int32)

        for d in range(self.n_directed):
            a = self.src[d]
            b = self.dst[d]
            incoming_dir = pos[b] - pos[a]
            incoming_len = np.linalg.norm(incoming_dir)

            if incoming_len < 1e-15:
                outs = self.outgoing[b]
                self.forward_redirect[d] = outs[0] if outs else d
                continue
            incoming_dir /= incoming_len

            best_edge = self.reverse[d]  # fallback: go back (shouldn't happen)
            best_dot = -2.0
            for out_d in self.outgoing[b]:
                if out_d == self.reverse[d]:
                    continue  # don't go back to A
                c = self.dst[out_d]
                out_dir = pos[c] - pos[b]
                out_len = np.linalg.norm(out_dir)
                if out_len < 1e-15:
                    continue
                dot = np.dot(incoming_dir, out_dir / out_len)
                if dot > best_dot:
                    best_dot = dot
                    best_edge = out_d

            self.forward_redirect[d] = best_edge

        print(f"  Forward redirect table built ({self.n_directed} entries)")

    def directed_id(self, node_a, node_b):
        """Get directed edge ID for edge a -> b."""
        return self._directed_id[(node_a, node_b)]

    def update_entity_nodes(self, node_set):
        """Update which nodes are claimed by entities."""
        self._is_entity[:] = False
        for n in node_set:
            self._is_entity[n] = True

    def begin_tick(self):
        """Prepare for a new tick: clear write buffer."""
        self.flows_next[:] = 0

    def propagate(self):
        """Directed propagation: deposits continue in a straight line.

        Each deposit follows the precomputed forward_redirect — the
        outgoing edge most aligned with its incoming direction. This
        produces beams, not diffusion, giving 1/r^2 geometric falloff.

        Entity nodes absorb 1 deposit/tick BEFORE this step (modifying
        flows in-place). The remaining deposits pass through all nodes.
        """
        has_deposits = self.flows.any(axis=1)
        active_idx = np.nonzero(has_deposits)[0]

        if len(active_idx) > 0:
            targets = self.forward_redirect[active_idx]
            np.add.at(self.flows_next, targets, self.flows[active_idx])

    def advance(self):
        """Swap flow buffers. Call after all processing is done."""
        self.flows, self.flows_next = self.flows_next, self.flows

    def emit(self, directed_edge, group_idx):
        """Place one deposit on a directed edge in flows_next."""
        self.flows_next[directed_edge, group_idx] += 1
        self.total_emitted += 1

    def absorb_one(self, directed_edge, group_idx):
        """Remove one deposit from current flows on a directed edge.

        Returns True if a deposit was absorbed, False if none available.
        """
        if self.flows[directed_edge, group_idx] > 0:
            self.flows[directed_edge, group_idx] -= 1
            self.total_absorbed += 1
            return True
        return False

    def absorb_at(self, node):
        """Remove and return all arriving deposits at a node."""
        total = 0
        for d in self.incoming[node]:
            total += int(self.flows[d].sum())
        self.total_absorbed += total
        return total

    def arrivals_per_edge_at(self, node):
        """Return list of (directed_edge_id, flow_array) for incoming edges with deposits."""
        result = []
        for d in self.incoming[node]:
            if self.flows[d].any():
                result.append((d, self.flows[d]))
        return result

    def total_deposits(self):
        """Total deposits currently in the flow buffers."""
        return int(self.flows.sum())

    def total_deposits_by_group(self):
        """Per-group deposit totals in current flows."""
        return self.flows.sum(axis=0)

    def deposits_at_radius(self, center_node, hop_distances):
        """Count deposits on edges at each hop distance from center."""
        edge_deposits = self.flows.sum(axis=1)
        nonzero = edge_deposits > 0
        if not nonzero.any():
            return {}
        active_edges = np.nonzero(nonzero)[0]
        active_deposits = edge_deposits[active_edges]
        active_dists = hop_distances[self.src[active_edges]]

        result = {}
        for dist in np.unique(active_dists):
            mask = active_dists == dist
            result[int(dist)] = int(active_deposits[mask].sum())
        return result
