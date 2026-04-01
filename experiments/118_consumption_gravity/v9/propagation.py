"""
Three-way partition propagation for Experiment 118 v9.

Every discharged quantum propagates through the graph. At each node:
  - Entity idle -> ABSORBED (store): deposit on arrival connector
  - Entity busy / no entity, forward path -> MOVE: deposit + continue forward
  - Entity busy / no entity, sideways path -> RADIATE: deposit + continue sideways

All deposits come through this system. No deposit-on-arrival bypass.
"""

import numpy as np

MOVE_ALIGNMENT_THRESHOLD = 0.3  # dot product > this = forward (momentum)


class InFlightQuantum:
    __slots__ = ('group', 'node', 'last_src', 'age', 'classification')

    def __init__(self, group, node, last_src):
        self.group = group
        self.node = node
        self.last_src = last_src
        self.age = 0
        self.classification = None  # set on first hop: 'move' or 'radiate'


class ForwardTable:
    """Precomputed forward-continuation for the graph."""

    def __init__(self, graph):
        self.graph = graph
        self._table = {}  # (from_node, at_node) -> best_next_node
        self._alignment = {}  # (from_node, at_node) -> dot product of best forward
        self._build(graph)

    def _build(self, graph):
        pos = graph.pos
        for node in range(graph.n_nodes):
            for nb in graph.neighbors(node):
                incoming_dir = pos[node] - pos[nb]
                incoming_len = np.linalg.norm(incoming_dir)
                if incoming_len < 1e-15:
                    others = [n2 for n2 in graph.neighbors(node) if n2 != nb]
                    self._table[(nb, node)] = others[0] if others else nb
                    self._alignment[(nb, node)] = 0.0
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
                    best_dot = -1.0
                self._table[(nb, node)] = best_next
                self._alignment[(nb, node)] = best_dot

        print(f"  Forward table: {len(self._table)} entries")

    def next_node(self, from_node, at_node):
        return self._table.get((from_node, at_node), at_node)

    def alignment(self, from_node, at_node):
        return self._alignment.get((from_node, at_node), 0.0)


class QuantumField:
    """Manages all in-flight quanta with three-way partition tracking."""

    def __init__(self, graph, forward_table, max_age=100):
        self.graph = graph
        self.forward = forward_table
        self.quanta = []
        self.max_age = max_age

        # Partition counters
        self.total_stored = 0
        self.total_moved = 0
        self.total_radiated = 0
        self.total_expired = 0

        # Per-tick counters (reset each tick)
        self.tick_stored = 0
        self.tick_moved = 0
        self.tick_radiated = 0

    def add(self, group, at_node, from_node):
        """Create a new in-flight quantum at at_node, arriving from from_node."""
        self.quanta.append(InFlightQuantum(group, at_node, from_node))

    def process_emission(self, group, src_node, dest_node, graph, idle_set):
        """Process a freshly emitted quantum from src_node toward dest_node.

        The quantum has already been aimed at dest_node by the entity's routing.
        Check if dest_node can absorb it. If not, it becomes in-flight.
        Either way, deposit on the connector between src and dest.
        """
        edge_key = (min(src_node, dest_node), max(src_node, dest_node))

        if dest_node in idle_set:
            # STORED: absorbed at destination
            graph.connectors[edge_key].append(group)
            idle_set.discard(dest_node)
            self.total_stored += 1
            self.tick_stored += 1
        else:
            # CONTINUES: deposit on this connector and become in-flight
            graph.connectors[edge_key].append(group)
            self.add(group, dest_node, src_node)

    def tick(self, idle_set):
        """Propagate all in-flight quanta one hop.

        Each quantum:
          - Check current node: idle entity? -> ABSORBED (store)
          - Otherwise: continue to forward node, deposit, classify
        """
        self.tick_stored = 0
        self.tick_moved = 0
        self.tick_radiated = 0

        surviving = []

        for q in self.quanta:
            q.age += 1

            if q.age > self.max_age:
                self.total_expired += 1
                continue

            # Check: can current node absorb?
            if q.node in idle_set:
                # ABSORBED (store) — deposit on the connector it arrived on
                edge_key = (min(q.node, q.last_src), max(q.node, q.last_src))
                if edge_key in self.graph.connectors:
                    self.graph.connectors[edge_key].append(q.group)
                idle_set.discard(q.node)
                self.total_stored += 1
                self.tick_stored += 1
                continue

            # CONTINUES — find next node via forward continuation
            next_node = self.forward.next_node(q.last_src, q.node)
            alignment = self.forward.alignment(q.last_src, q.node)
            edge_key = (min(q.node, next_node), max(q.node, next_node))

            if edge_key not in self.graph.connectors:
                self.total_expired += 1
                continue

            # Deposit on the traversed connector (quantum marks its path)
            self.graph.connectors[edge_key].append(q.group)

            # Classify on first hop
            if q.classification is None:
                if alignment > MOVE_ALIGNMENT_THRESHOLD:
                    q.classification = 'move'
                else:
                    q.classification = 'radiate'

            # Track
            if q.classification == 'move':
                self.total_moved += 1
                self.tick_moved += 1
            else:
                self.total_radiated += 1
                self.tick_radiated += 1

            # Advance
            q.last_src = q.node
            q.node = next_node
            surviving.append(q)

        self.quanta = surviving

    def count(self):
        return len(self.quanta)
