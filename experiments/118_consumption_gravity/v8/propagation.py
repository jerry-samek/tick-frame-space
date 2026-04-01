"""
In-flight quantum propagation for Experiment 118 v8.

Unabsorbed discharge quanta propagate through the graph at 1 hop/tick,
depositing on each connector they traverse (creating the momentum wake).
Forward-continuation table precomputed from graph geometry.
"""

import numpy as np


class InFlightQuantum:
    """A discharged quantum propagating through the graph."""

    __slots__ = ('group', 'node', 'last_edge_key', 'last_src', 'age')

    def __init__(self, group, node, last_edge_key, last_src):
        self.group = group
        self.node = node               # current node
        self.last_edge_key = last_edge_key  # (i,j) edge it arrived on
        self.last_src = last_src        # node it came from
        self.age = 0


class ForwardTable:
    """Precomputed forward-continuation table for the graph.

    For each (arriving_from, at_node) pair, stores the best forward
    neighbor — the outgoing edge most aligned with the arrival direction.
    """

    def __init__(self, graph):
        self.graph = graph
        self._table = {}  # (from_node, at_node) -> best_next_node
        self._build(graph)

    def _build(self, graph):
        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                # If quantum arrived at `node` from `nb`, where does it go?
                incoming_dir = pos[node] - pos[nb]
                incoming_len = np.linalg.norm(incoming_dir)
                if incoming_len < 1e-15:
                    # Degenerate — pick first non-reverse neighbor
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._table[(nb, node)] = others[0] if others else nb
                    continue
                incoming_dir /= incoming_len

                best_next = None
                best_dot = -2.0
                for n2 in graph.neighbors(node):
                    if n2 == nb:
                        continue  # don't go back
                    out_dir = pos[n2] - pos[node]
                    out_len = np.linalg.norm(out_dir)
                    if out_len < 1e-15:
                        continue
                    dot = np.dot(incoming_dir, out_dir / out_len)
                    if dot > best_dot:
                        best_dot = dot
                        best_next = n2

                if best_next is None:
                    best_next = nb  # dead end — go back
                self._table[(nb, node)] = best_next

        print(f"  Forward table: {len(self._table)} entries")

    def next_node(self, from_node, at_node):
        """Given quantum arrived at `at_node` from `from_node`, return next node."""
        return self._table.get((from_node, at_node), at_node)


class QuantumField:
    """Manages all in-flight quanta in the simulation."""

    def __init__(self, graph, forward_table):
        self.graph = graph
        self.forward = forward_table
        self.quanta = []
        self.total_created = 0
        self.total_absorbed = 0
        self.total_expired = 0
        self.max_age = 50  # quanta older than this are destroyed (prevent buildup)

    def add(self, group, at_node, from_node):
        """Create a new in-flight quantum."""
        edge_key = (min(at_node, from_node), max(at_node, from_node))
        self.quanta.append(InFlightQuantum(group, at_node, edge_key, from_node))
        self.total_created += 1

    def tick(self, idle_entity_set):
        """Propagate all in-flight quanta one hop.

        Quanta at idle entity nodes are absorbed.
        Others deposit on the forward connector and advance.
        Returns the set of nodes that absorbed a quantum this tick.
        """
        surviving = []
        absorbed_nodes = set()

        for q in self.quanta:
            q.age += 1

            # Expire old quanta (prevent infinite buildup)
            if q.age > self.max_age:
                self.total_expired += 1
                continue

            # Check: is current node an idle entity capacitor?
            if q.node in idle_entity_set and q.node not in absorbed_nodes:
                # ABSORBED — store on the connector it arrived on
                self.graph.connectors[q.last_edge_key].append(q.group)
                absorbed_nodes.add(q.node)
                idle_entity_set.discard(q.node)  # now busy
                self.total_absorbed += 1
                continue

            # CONTINUES — find forward node, deposit on connector, advance
            next_node = self.forward.next_node(q.last_src, q.node)
            edge_key = (min(q.node, next_node), max(q.node, next_node))

            if edge_key not in self.graph.connectors:
                # No connector — quantum lost (shouldn't happen in connected graph)
                self.total_expired += 1
                continue

            # Deposit on the connector (creates the momentum wake)
            self.graph.connectors[edge_key].append(q.group)

            # Advance
            q.last_src = q.node
            q.node = next_node
            q.last_edge_key = edge_key
            surviving.append(q)

        self.quanta = surviving
        return absorbed_nodes

    def count(self):
        return len(self.quanta)
