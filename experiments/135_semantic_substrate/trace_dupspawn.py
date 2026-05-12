"""
Trace the duplicate {8}-spawn at seed=42 in Phase 4.

Reuses TracingSubstrate from trace_4spawn. Finds ALL spawn events for any
duplicated token, then prints the SECOND duplicate's deposit life history
to confirm the race-condition hypothesis: the second deposit walked the
substrate before the first deposit's spawn was visible in c0's connectors.
"""
from __future__ import annotations
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from trace_4spawn import (
    TracingSubstrate,
    build_k6_ring,
    attach_observer,
    name_for_cell_id,
)
from fixture import Injector


def main():
    s = TracingSubstrate()
    ring = build_k6_ring(s)
    observers = [attach_observer(s, ring[i]) for i in range(6)]
    inj = Injector(seed=42)

    n_ticks = 10_000
    cadence = 30
    for t in range(1, n_ticks + 1):
        if t % cadence == 1:
            s.inject(ring[0], token=inj.next_token())
        s.tick()

    spawn_events = [ev for ev in s.trace_log if ev[0] == "spawn"]
    spawn_token_counts = Counter(ev[4] for ev in spawn_events)
    duplicates = [(tok, c) for tok, c in spawn_token_counts.items() if c > 1]

    print(f"All spawn events at seed=42 (post-fix run):")
    for ev in spawn_events:
        print(f"  t={ev[1]:5d}: token={ev[4]} deposit_seq={ev[3]} cell=c0")
    print(f"\nTokens spawned >1 times: {duplicates}")

    if not duplicates:
        print("No duplicates. Fix already addressed it (unexpected).")
        return

    # Take the first duplicate token, trace the SECOND deposit (the one that
    # spawned a duplicate after the first was already in place).
    dup_token = duplicates[0][0]
    dup_spawn_events = [ev for ev in spawn_events if ev[4] == dup_token]
    second_spawn = dup_spawn_events[1]
    second_seq = second_spawn[3]
    second_tick = second_spawn[1]

    print(f"\n=== Tracing 2nd dup-spawn deposit: token={dup_token} "
          f"seq_id={second_seq} spawn_tick={second_tick} ===")

    deposit_events = [
        ev for ev in s.trace_log
        if (
            (ev[0] in ("inject", "begin_handling", "spawn", "consume")
             and len(ev) > 3 and ev[3] == second_seq)
            or
            (ev[0] in ("bounce", "forward", "query", "response")
             and len(ev) > 4 and ev[4] == second_seq)
        )
    ]

    print(f"Deposit life ({len(deposit_events)} events):\n")
    for ev in deposit_events:
        kind = ev[0]
        tick = ev[1]
        cell_name = name_for_cell_id(ev[2], ring, observers, s.spawn_log, s.cells)
        if kind == "inject":
            print(f"  t={tick:5d}  INJECT     at {cell_name:20s} token={ev[4]}")
        elif kind == "begin_handling":
            pred = name_for_cell_id(ev[5], ring, observers, s.spawn_log, s.cells) if ev[5] else "None"
            dead = [name_for_cell_id(d, ring, observers, s.spawn_log, s.cells) for d in ev[6]]
            print(f"  t={tick:5d}  BEGIN      at {cell_name:20s} token={ev[4]} pred={pred} dead={dead}")
        elif kind == "query":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, s.cells)
            print(f"  t={tick:5d}    query    {cell_name:20s} -> {target:20s} token={ev[5]}")
        elif kind == "response":
            source = name_for_cell_id(ev[3], ring, observers, s.spawn_log, s.cells)
            print(f"  t={tick:5d}    response {source:20s} -> {cell_name:20s} {ev[5]}")
        elif kind == "forward":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, s.cells)
            print(f"  t={tick:5d}  FORWARD    {cell_name:20s} -> {target}")
        elif kind == "bounce":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, s.cells)
            print(f"  t={tick:5d}  BOUNCE     {cell_name:20s} -> {target}")
        elif kind == "spawn":
            print(f"  t={tick:5d}  SPAWN      at {cell_name:20s} token={ev[4]}  *** DUP ***")
        elif kind == "consume":
            print(f"  t={tick:5d}  CONSUME    at {cell_name:20s} token={ev[4]}")

    # Cross-reference: when did the first {dup_token} spawn happen?
    first_spawn = dup_spawn_events[0]
    print(f"\nFirst {dup_token}-spawn: tick={first_spawn[1]} (deposit_seq={first_spawn[3]})")
    print(f"Second {dup_token}-spawn: tick={second_spawn[1]} (deposit_seq={second_seq})")

    # When did the SECOND deposit do its FIRST canvas at c0?
    second_first_canvas = next(
        (ev for ev in deposit_events
         if ev[0] == "query" and ev[2] == id(ring[0])),
        None
    )
    if second_first_canvas:
        print(f"\nSecond deposit's first query at c0 was at tick {second_first_canvas[1]}.")
        print(f"First spawn was at tick {first_spawn[1]}.")
        if second_first_canvas[1] < first_spawn[1]:
            print(f"=> Confirmed: 2nd deposit BEGAN canvasing c0 BEFORE the 1st deposit spawned child_{{{dup_token}}}.")
            print(f"   The 2nd deposit's canvas list at c0 didn't include child_{{{dup_token}}}.")
            print(f"   Hence it walked the ring without finding Same and triggered origin-loop spawn (DUP).")
        else:
            print(f"=> 2nd deposit's first c0 canvas was AFTER 1st spawn.")
            print(f"   But still triggered dup → likely a different mechanism.")


if __name__ == "__main__":
    main()
