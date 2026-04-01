#!/usr/bin/env python3
"""
Experiment 118 v7 — Phase 0: Traversal Time Validation

Simple chain graph. One entity node traverses back and forth.
Verify: traversal takes length ticks, connector doubles per traversal,
growth is linear in real time.
"""

import numpy as np
from collections import defaultdict


class SimpleConnector:
    __slots__ = ('initial_length', 'deposits', 'total')

    def __init__(self, length):
        self.initial_length = length
        self.deposits = {}
        self.total = 0

    @property
    def length(self):
        return self.initial_length + self.total

    def append(self, tag):
        self.deposits[tag] = self.deposits.get(tag, 0) + 1
        self.total += 1


def run():
    # Simple chain: 0 -- 1 -- 2 -- 3 -- 4
    n = 5
    adj = defaultdict(list)
    connectors = {}
    initial_len = 3.0  # initial length per connector

    for i in range(n - 1):
        key = (i, i + 1)
        connectors[key] = SimpleConnector(initial_len)
        adj[i].append(i + 1)
        adj[i + 1].append(i)

    # One entity node at position 0, traversing toward 1
    node = 0
    group = 's0'
    in_transit = False
    transit_edge = None
    transit_dest = None
    transit_remaining = 0

    traversals = []
    tick = 0

    print(f"Chain: {n} nodes, initial connector length = {initial_len}")
    print(f"Entity at node {node}, will traverse toward node 1\n")

    # Run 500 ticks — entity bounces between 0 and 1
    for tick in range(1, 501):
        if in_transit:
            connectors[transit_edge].append(group)
            transit_remaining -= 1
            if transit_remaining <= 0:
                node = transit_dest
                in_transit = False
                traversals.append({
                    'tick': tick,
                    'arrived_at': node,
                    'edge': transit_edge,
                    'length_after': connectors[transit_edge].length,
                })
        else:
            # Always go to neighbor (bounce between 0 and 1)
            dest = adj[node][0]  # first neighbor
            key = (min(node, dest), max(node, dest))
            c = connectors[key]
            traverse_time = max(1, int(c.length))

            in_transit = True
            transit_edge = key
            transit_dest = dest
            transit_remaining = traverse_time

            # First deposit
            c.append(group)
            transit_remaining -= 1
            if transit_remaining <= 0:
                node = dest
                in_transit = False
                traversals.append({
                    'tick': tick,
                    'arrived_at': node,
                    'edge': key,
                    'length_after': c.length,
                })

    print(f"{'Trav#':>5}  {'Tick':>6}  {'Edge':>8}  {'Length':>10}  {'Duration':>10}")
    print("-" * 50)
    prev_tick = 0
    for i, t in enumerate(traversals):
        duration = t['tick'] - prev_tick
        print(f"{i+1:5d}  {t['tick']:6d}  {str(t['edge']):>8}  "
              f"{t['length_after']:10.1f}  {duration:10d}")
        prev_tick = t['tick']

    print(f"\nTotal traversals in 500 ticks: {len(traversals)}")

    # Check: does length double per traversal of the same edge?
    edge_01 = (0, 1)
    edge_traversals = [t for t in traversals if t['edge'] == edge_01]
    if len(edge_traversals) >= 2:
        print(f"\nEdge (0,1) traversals:")
        for i in range(1, len(edge_traversals)):
            ratio = edge_traversals[i]['length_after'] / edge_traversals[i-1]['length_after']
            print(f"  After traversal {i+1}: length={edge_traversals[i]['length_after']:.1f}, "
                  f"ratio to previous={ratio:.3f}")

    # Check: is growth linear in time?
    if len(traversals) >= 3:
        first = traversals[0]
        last = traversals[-1]
        time_elapsed = last['tick'] - first['tick']
        length_growth = last['length_after'] - first['length_after']
        print(f"\nGrowth rate: {length_growth:.1f} deposits over {time_elapsed} ticks "
              f"= {length_growth/time_elapsed:.3f} per tick")


if __name__ == '__main__':
    run()
