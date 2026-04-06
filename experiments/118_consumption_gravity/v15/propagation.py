"""
Propagating quanta for Experiment 118 v15.

Quanta propagate at c=1 hop/tick using forward-continuation.
Each hop: deposit on the traversed connector (GROWS it if Different).
The quantum BUILDS the connector as it travels — the road is created
by the radiation, not pre-existing.
"""

import numpy as np


class ForwardTable:
    """Precomputed forward-continuation for graph geometry."""

    def __init__(self, graph):
        self.graph = graph
        self._table = {}

        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                incoming_dir = pos[node] - pos[nb]
                incoming_len = np.linalg.norm(incoming_dir)
                if incoming_len < 1e-15:
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._table[(nb, node)] = others[0] if others else nb
                    continue
                incoming_dir /= incoming_len

                best_next = None
                best_dot = -2.0
                for n2 in graph.neighbors(node):
                    if n2 == nb:
                        continue
                    out_dir = pos[n2] - pos[node]
                    out_len = np.linalg.norm(out_dir)
                    if out_len < 1e-15:
                        continue
                    dot = np.dot(incoming_dir, out_dir / out_len)
                    if dot > best_dot:
                        best_dot = dot
                        best_next = n2

                if best_next is None:
                    best_next = nb
                self._table[(nb, node)] = best_next

        print(f"  Forward table: {len(self._table)} entries")

    def next_node(self, from_node, at_node):
        return self._table.get((from_node, at_node), at_node)


class Quantum:
    __slots__ = ('group', 'node', 'from_node', 'age')

    def __init__(self, group, node, from_node):
        self.group = group
        self.node = node
        self.from_node = from_node
        self.age = 0


class QuantumField:
    """Manages propagating quanta that build connectors."""

    def __init__(self, graph, forward_table, max_hops=500):
        self.graph = graph
        self.forward = forward_table
        self.max_hops = max_hops
        self.quanta = []
        self.total_created = 0
        self.total_expired = 0
        self.total_deposits = 0

        # Per-tick: which nodes had quanta deposit on their connectors
        self._deposits_at = {}  # node -> count of deposits this tick

    def add(self, group, node, from_node):
        self.quanta.append(Quantum(group, node, from_node))
        self.total_created += 1

    def tick(self, graph):
        """Propagate all quanta one hop. Each deposits on traversed connector."""
        self._deposits_at = {}
        surviving = []

        for q in self.quanta:
            q.age += 1
            if q.age > self.max_hops:
                self.total_expired += 1
                continue

            next_node = self.forward.next_node(q.from_node, q.node)
            ek = graph.edge_key(q.node, next_node)

            if ek not in graph.connectors:
                self.total_expired += 1
                continue

            # Deposit on the connector — BUILDS it (grows if Different)
            graph.connectors[ek].append(q.group, q.node, next_node)
            self.total_deposits += 1

            # Track which nodes received deposits this tick
            # Both endpoints of the connector "see" the quantum pass
            self._deposits_at[q.node] = self._deposits_at.get(q.node, 0) + 1
            self._deposits_at[next_node] = self._deposits_at.get(next_node, 0) + 1

            q.from_node = q.node
            q.node = next_node
            surviving.append(q)

        self.quanta = surviving

    def deposits_this_tick_at(self, node):
        """How many quanta deposited on connectors of this node this tick."""
        return self._deposits_at.get(node, 0)

    def count(self):
        return len(self.quanta)
