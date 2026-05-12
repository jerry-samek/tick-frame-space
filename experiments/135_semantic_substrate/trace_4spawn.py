"""
Trace the {4}-spawn anomaly at seed=42 in Phase 4.

Adds deposit-level tracing via a Substrate subclass that overrides hot
methods. Runs Phase 4 at seed=42, finds the spawn event with token=4,
walks back through trace_log to print that deposit's full life history.

Goal: identify the mechanism that allows a known token (4) to trigger
origin-loop spawn at c0 in 59% of seeds.
"""
from __future__ import annotations
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cell import Cell, Deposit, Response, State
from substrate import Substrate
from fixture import Injector


# ----------------------------------------------------------------------------
# Tracing substrate
# ----------------------------------------------------------------------------

class TracingSubstrate(Substrate):
    def __init__(self):
        super().__init__()
        self.trace_log: list = []
        self._next_seq = 0

    def inject(self, cell, token):
        deposit = super().inject(cell, token)
        self._next_seq += 1
        deposit.seq_id = self._next_seq  # seq_id stable across the deposit's life
        self.trace_log.append(("inject", self.tick_count, id(cell), deposit.seq_id, token))
        return deposit

    def _begin_handling(self, cell, deposit):
        pred_id = id(deposit.predecessor) if deposit.predecessor else None
        dead_ids = sorted(id(c) for c in deposit.dead_paths)
        self.trace_log.append((
            "begin_handling", self.tick_count, id(cell), deposit.seq_id,
            deposit.token, pred_id, dead_ids,
        ))
        super()._begin_handling(cell, deposit)

    def _bounce(self, cell):
        deposit = cell.current_deposit
        target = deposit.predecessor
        self.trace_log.append((
            "bounce", self.tick_count, id(cell), id(target), deposit.seq_id,
        ))
        super()._bounce(cell)

    def _forward(self, cell, target):
        deposit = cell.current_deposit
        self.trace_log.append((
            "forward", self.tick_count, id(cell), id(target), deposit.seq_id,
        ))
        super()._forward(cell, target)

    def _send_next_query(self, cell):
        deposit = cell.current_deposit
        next_neighbor = cell.canvas_remaining[0]
        self.trace_log.append((
            "query", self.tick_count, id(cell), id(next_neighbor),
            deposit.seq_id, deposit.token,
        ))
        super()._send_next_query(cell)

    def _handle_response(self, payload):
        cell = payload.to_cell
        deposit = cell.current_deposit
        self.trace_log.append((
            "response", self.tick_count, id(cell), id(payload.from_cell),
            deposit.seq_id if deposit else None, payload.response.value,
        ))
        super()._handle_response(payload)

    def _spawn(self, cell, deposit):
        self.trace_log.append((
            "spawn", self.tick_count, id(cell), deposit.seq_id, deposit.token,
        ))
        super()._spawn(cell, deposit)

    def _consume(self, cell, deposit):
        self.trace_log.append((
            "consume", self.tick_count, id(cell), deposit.seq_id, deposit.token,
        ))
        super()._consume(cell, deposit)


# ----------------------------------------------------------------------------
# Fixture
# ----------------------------------------------------------------------------

def build_k6_ring(substrate):
    cells = [Cell(spectrum={i}) for i in range(6)]
    for c in cells:
        substrate.add_cell(c)
    for i, c in enumerate(cells):
        c.connectors.extend([cells[(i - 1) % 6], cells[(i + 1) % 6]])
    return cells


def attach_observer(substrate, host, learning_threshold=15, crystallization_size=1):
    obs = Cell(
        spectrum=set(),
        learning_threshold=learning_threshold,
        crystallization_size=crystallization_size,
    )
    substrate.add_cell(obs)
    host.connectors.append(obs)
    obs.connectors.append(host)
    return obs


# ----------------------------------------------------------------------------
# Run + analyse
# ----------------------------------------------------------------------------

def run_traced_phase4(seed=42, n_ticks=10_000, cadence=30):
    s = TracingSubstrate()
    ring = build_k6_ring(s)
    observers = [attach_observer(s, ring[i]) for i in range(6)]
    inj = Injector(seed=seed)

    for t in range(1, n_ticks + 1):
        if t % cadence == 1:
            s.inject(ring[0], token=inj.next_token())
        s.tick()

    return s, ring, observers


def name_for_cell_id(cell_id, ring, observers, spawn_log, all_cells):
    """Return human-readable name for a cell, given its id."""
    for i, c in enumerate(ring):
        if id(c) == cell_id:
            return f"c{i}"
    for i, o in enumerate(observers):
        if id(o) == cell_id:
            return f"obs_c{i}"
    for tick, parent, child, token in spawn_log:
        if id(child) == cell_id:
            spec = sorted(child.spectrum)
            return f"child_{spec}@t{tick}"
    return f"unknown_id_{cell_id}"


def main():
    print("Running Phase 4 at seed=42 with deposit-level tracing...")
    s, ring, observers = run_traced_phase4(seed=42)

    # All cells, including spawned, for naming
    all_cells = list(s.cells)

    # Find the {4}-spawn event in the trace log.
    spawn_4_events = [
        ev for ev in s.trace_log
        if ev[0] == "spawn" and ev[4] == 4
    ]
    if not spawn_4_events:
        print("NO {4}-spawn event found at seed=42. Either bug not reproduced "
              "(check test reproducibility) or trace logic broken.")
        return

    print(f"Found {len(spawn_4_events)} spawn event(s) with token=4:")
    for ev in spawn_4_events:
        print(f"  {ev}")

    # The first {4}-spawn event — that's the bug.
    target_event = spawn_4_events[0]
    spawn_tick = target_event[1]
    spawn_cell_id = target_event[2]
    deposit_id = target_event[3]

    print(f"\n=== Target deposit: id={deposit_id}, spawned-{{4}} at tick={spawn_tick}, "
          f"at cell {name_for_cell_id(spawn_cell_id, ring, observers, s.spawn_log, all_cells)} ===")

    # Find ALL events for this deposit (the deposit's full life history).
    # deposit_id is now seq_id (stable across the deposit's life).
    deposit_events = [
        ev for ev in s.trace_log
        if (
            (ev[0] in ("inject", "begin_handling", "spawn", "consume") and len(ev) > 3 and ev[3] == deposit_id)
            or
            (ev[0] in ("bounce", "forward", "query", "response") and len(ev) > 4 and ev[4] == deposit_id)
        )
    ]

    print(f"\n=== Deposit life history ({len(deposit_events)} events) ===\n")
    for ev in deposit_events:
        kind = ev[0]
        tick = ev[1]
        cell_name = name_for_cell_id(ev[2], ring, observers, s.spawn_log, all_cells)
        if kind == "inject":
            token = ev[4]
            print(f"  t={tick:5d}  INJECT     at {cell_name:20s} token={token}")
        elif kind == "begin_handling":
            token = ev[4]
            pred = name_for_cell_id(ev[5], ring, observers, s.spawn_log, all_cells) if ev[5] else "None"
            dead = [name_for_cell_id(d, ring, observers, s.spawn_log, all_cells) for d in ev[6]]
            print(f"  t={tick:5d}  BEGIN      at {cell_name:20s} token={token} pred={pred} dead={dead}")
        elif kind == "query":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, all_cells)
            token = ev[5]
            print(f"  t={tick:5d}    query    {cell_name:20s} -> {target:20s} token={token}")
        elif kind == "response":
            source = name_for_cell_id(ev[3], ring, observers, s.spawn_log, all_cells)
            resp = ev[5]
            print(f"  t={tick:5d}    response {source:20s} -> {cell_name:20s} {resp}")
        elif kind == "forward":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, all_cells)
            print(f"  t={tick:5d}  FORWARD    {cell_name:20s} -> {target}")
        elif kind == "bounce":
            target = name_for_cell_id(ev[3], ring, observers, s.spawn_log, all_cells)
            print(f"  t={tick:5d}  BOUNCE     {cell_name:20s} -> {target}")
        elif kind == "spawn":
            token = ev[4]
            print(f"  t={tick:5d}  SPAWN      at {cell_name:20s} token={token}  *** ANOMALY ***")
        elif kind == "consume":
            token = ev[4]
            print(f"  t={tick:5d}  CONSUME    at {cell_name:20s} token={token}")

    # Also print the substrate state at the time of spawn.
    print("\n=== Substrate state at time of spawn ===")
    print(f"c0.connectors order: {[name_for_cell_id(id(c), ring, observers, s.spawn_log, all_cells) for c in ring[0].connectors]}")
    print(f"c0.next_canvas_index: {ring[0].next_canvas_index} / {len(ring[0].connectors)}")
    print(f"\nObserver states:")
    for i, o in enumerate(observers):
        print(f"  obs_c{i}: state={o.state.value} spectrum={sorted(o.spectrum)} obs_count={sum(o.obs_counter.values())}")
    print(f"\nSpawn log up to tick {spawn_tick}:")
    for tick, parent, child, token in s.spawn_log:
        if tick <= spawn_tick:
            print(f"  t={tick:5d}: parent={name_for_cell_id(id(parent), ring, observers, s.spawn_log, all_cells)} "
                  f"child_spectrum={sorted(child.spectrum)} token={token}")


if __name__ == "__main__":
    main()
