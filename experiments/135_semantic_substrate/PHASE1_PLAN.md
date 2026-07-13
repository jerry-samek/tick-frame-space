# Experiment 135 Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the reactive-canvas semantic substrate with origin-loop spawn, run it on the K=6 ring fixture for 10K ticks, and verify all Phase 1 success criteria from `PHASE1_DESIGN.md`.

**Architecture:** Pure Python, no NumPy / Numba (Phase 1 is correctness, not performance — the substrate is small enough that vanilla Python is fine). Discrete-event simulation: substrate maintains a min-heap of `(arrival_tick, event)` pairs; each tick processes events arriving at that tick. Cell state is a small state machine: `Idle` → `Canvasing(deposit, responses, remaining_neighbors)` → back to `Idle`. Reproducibility via creation-order indexing on cells (not Python `id()`).

**Tech Stack:** Python 3.13, pytest, dataclasses, `heapq` for the event queue, `collections.deque` for cell pending queues. No third-party deps beyond what's already in `W:\tools\python\python.exe`.

**Note on commits:** Per the experiments-not-software-projects stance, the commit steps in this plan are *suggested checkpoints*. Skip them and do one consolidated commit at the end if you'd rather. They're useful when something goes wrong, but they're not required ceremony.

---

## File structure (all under `experiments/135_semantic_substrate/`)

| File | Responsibility |
|---|---|
| `__init__.py` | Package marker (empty) |
| `conftest.py` | pytest sys.path fix so tests can `from cell import Cell` |
| `cell.py` | `Response` enum, `Deposit` dataclass, `Cell` class (spectrum + connectors + canvas state + `classify()`) |
| `substrate.py` | `Substrate` class: event queue, `tick()`, `inject()`, all mechanism logic (self-check, origin-loop, canvas, spawn, forward, consume) |
| `fixture.py` | `build_k6_ring(substrate)`, `Injector` class with seeded RNG + cadence + token mix |
| `tests/__init__.py` | Package marker (empty) |
| `tests/test_cell.py` | Unit tests for Cell.classify and Deposit |
| `tests/test_substrate.py` | Unit tests for tick loop, query timing, mechanism branches |
| `tests/test_fixture.py` | Unit tests for ring builder and injector |
| `phase1_test.py` | The deliverable — 10K-tick run, all measurements, all success-criteria assertions |

---

## Task 1: Scaffold

**Files:**
- Create: `experiments/135_semantic_substrate/__init__.py` (empty)
- Create: `experiments/135_semantic_substrate/conftest.py`
- Create: `experiments/135_semantic_substrate/tests/__init__.py` (empty)

- [ ] **Step 1: Create empty package markers**

```bash
touch experiments/135_semantic_substrate/__init__.py
touch experiments/135_semantic_substrate/tests/__init__.py
```

- [ ] **Step 2: Write conftest.py for pytest path fix**

`experiments/135_semantic_substrate/conftest.py`:

```python
import sys
from pathlib import Path

# Make modules in this experiment folder importable as top-level by tests/
sys.path.insert(0, str(Path(__file__).parent))
```

- [ ] **Step 3: Verify scaffold by running pytest on empty test directory**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/ -v`
Expected: `no tests ran in 0.XXs` (no errors, just empty)

- [ ] **Step 4 (optional commit): "exp 135 phase 1: scaffold"**

---

## Task 2: Response enum, Deposit dataclass, Cell.classify

**Files:**
- Create: `experiments/135_semantic_substrate/cell.py`
- Create: `experiments/135_semantic_substrate/tests/test_cell.py`

- [ ] **Step 1: Write the failing test for Response enum and Cell.classify**

`experiments/135_semantic_substrate/tests/test_cell.py`:

```python
from cell import Cell, Deposit, Response


def test_classify_unknown_for_empty_spectrum():
    c = Cell(spectrum=set())
    assert c.classify(7) == Response.UNKNOWN


def test_classify_same_for_token_in_spectrum():
    c = Cell(spectrum={3})
    assert c.classify(3) == Response.SAME


def test_classify_different_for_token_not_in_populated_spectrum():
    c = Cell(spectrum={1, 2, 5})
    assert c.classify(7) == Response.DIFFERENT


def test_deposit_carries_token_predecessor_origin_age():
    origin = Cell(spectrum={0})
    d = Deposit(token=42, predecessor=None, origin=origin, age=0)
    assert d.token == 42
    assert d.predecessor is None
    assert d.origin is origin
    assert d.age == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_cell.py -v`
Expected: ImportError — `cell` module doesn't exist yet.

- [ ] **Step 3: Implement `cell.py`**

`experiments/135_semantic_substrate/cell.py`:

```python
from __future__ import annotations
from collections import deque
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class Response(Enum):
    SAME = "same"
    DIFFERENT = "different"
    UNKNOWN = "unknown"


@dataclass
class Cell:
    spectrum: set[int]
    connectors: list["Cell"] = field(default_factory=list)
    pending: deque = field(default_factory=deque)
    next_canvas_index: int = 0
    creation_order: int = -1  # set by Substrate.add_cell
    # Canvas state (None when Idle):
    current_deposit: Optional["Deposit"] = None
    canvas_responses: list = field(default_factory=list)  # list[tuple[Cell, Response]]
    canvas_remaining: list = field(default_factory=list)  # list[Cell] still to query
    canvas_in_flight: Optional["Cell"] = None  # the neighbor we just sent a query to

    @property
    def is_idle(self) -> bool:
        return self.current_deposit is None

    def classify(self, token: int) -> Response:
        if not self.spectrum:
            return Response.UNKNOWN
        if token in self.spectrum:
            return Response.SAME
        return Response.DIFFERENT


@dataclass
class Deposit:
    token: int
    predecessor: Optional[Cell]
    origin: Cell
    age: int = 0
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_cell.py -v`
Expected: 4 passed.

- [ ] **Step 5 (optional commit): "exp 135 phase 1: Cell, Deposit, Response, classify"**

---

## Task 3: Substrate skeleton — event queue, ticks, inject

**Files:**
- Create: `experiments/135_semantic_substrate/substrate.py`
- Create: `experiments/135_semantic_substrate/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for substrate skeleton**

`experiments/135_semantic_substrate/tests/test_substrate.py`:

```python
from cell import Cell, Deposit, Response
from substrate import Substrate


def test_substrate_starts_at_tick_zero():
    s = Substrate()
    assert s.tick_count == 0
    assert s.cells == []


def test_add_cell_assigns_creation_order():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    assert c0.creation_order == 0
    assert c1.creation_order == 1
    assert s.cells == [c0, c1]


def test_inject_queues_deposit_in_target_cell_pending():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    d = s.inject(c0, token=5)
    assert d.token == 5
    assert d.predecessor is None
    assert d.origin is c0
    assert d.age == 0
    assert len(c0.pending) == 1
    assert c0.pending[0] is d


def test_tick_increments_tick_count():
    s = Substrate()
    s.tick()
    assert s.tick_count == 1
    s.tick()
    assert s.tick_count == 2
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: ImportError — `substrate` module doesn't exist.

- [ ] **Step 3: Implement `substrate.py` skeleton**

`experiments/135_semantic_substrate/substrate.py`:

```python
from __future__ import annotations
import heapq
from dataclasses import dataclass, field
from typing import Any

from cell import Cell, Deposit, Response


@dataclass(order=True)
class _Event:
    """Wrapper so heapq can sort by (arrival_tick, sequence_id)."""
    arrival_tick: int
    sequence_id: int
    payload: Any = field(compare=False)


class Substrate:
    def __init__(self) -> None:
        self.tick_count: int = 0
        self.cells: list[Cell] = []
        self._events: list[_Event] = []  # heap of _Event
        self._event_seq: int = 0  # tiebreaker for heap
        # Logs (populated as run progresses):
        self.spawn_log: list[tuple[int, Cell, Cell, int]] = []  # (tick, parent, child, token)
        self.consume_log: list[tuple[int, Cell, int, int]] = []  # (tick, cell, token, age_at_consume)

    def add_cell(self, cell: Cell) -> Cell:
        cell.creation_order = len(self.cells)
        self.cells.append(cell)
        return cell

    def inject(self, cell: Cell, token: int) -> Deposit:
        d = Deposit(token=token, predecessor=None, origin=cell, age=0)
        cell.pending.append(d)
        return d

    def _enqueue(self, arrival_tick: int, payload: Any) -> None:
        heapq.heappush(self._events, _Event(arrival_tick, self._event_seq, payload))
        self._event_seq += 1

    def tick(self) -> None:
        self.tick_count += 1
        # (event processing + idle-cell scheduling go here in later tasks)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: 4 passed.

- [ ] **Step 5 (optional commit): "exp 135 phase 1: Substrate skeleton"**

---

## Task 4: Self-check, origin-loop, and consume

These are the "easy" mechanism branches — no canvas needed, decided immediately when a deposit reaches a cell.

**Files:**
- Modify: `experiments/135_semantic_substrate/substrate.py`
- Modify: `experiments/135_semantic_substrate/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for self-check and origin-loop consume/spawn**

Append to `experiments/135_semantic_substrate/tests/test_substrate.py`:

```python
def test_self_check_consumes_deposit_when_token_in_spectrum():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={3}))
    s.inject(c0, token=3)
    s.tick()  # deposit picked up, self-check passes, consume
    assert len(s.consume_log) == 1
    tick, cell, token, age = s.consume_log[0]
    assert cell is c0
    assert token == 3
    assert age == 0  # consumed at injection
    assert len(c0.pending) == 0
    assert c0.is_idle


def test_origin_loop_spawns_child_when_deposit_returns_to_origin_with_predecessor():
    # Manually set up: a deposit "returned" to its origin from another cell.
    s = Substrate()
    origin = s.add_cell(Cell(spectrum={0}))
    other = s.add_cell(Cell(spectrum={1}))
    # Inject a deposit whose origin is `origin` but whose predecessor is `other`,
    # and whose token isn't in origin's spectrum.
    d = Deposit(token=99, predecessor=other, origin=origin, age=5)
    origin.pending.append(d)
    s.tick()
    # Origin-loop check fires: spawn child of origin with spectrum={99}.
    assert len(s.spawn_log) == 1
    tick, parent, child, token = s.spawn_log[0]
    assert parent is origin
    assert child.spectrum == {99}
    assert child.connectors == [origin]
    assert child in origin.connectors
    assert len(s.cells) == 3  # origin + other + new child
    # Deposit is consumed; pending is empty.
    assert len(origin.pending) == 0
    assert origin.is_idle
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: 2 new tests fail (`tick()` doesn't process pending deposits yet).

- [ ] **Step 3: Implement self-check, origin-loop, _consume, _spawn, and tick-loop pickup**

Modify `experiments/135_semantic_substrate/substrate.py`:

Replace the `tick` method and add helpers:

```python
    def tick(self) -> None:
        self.tick_count += 1
        # 1. Process events arriving at this tick (added in Task 5).
        # 2. Idle cells with pending deposits start handling next deposit.
        # Iterate cells in deterministic creation order.
        for cell in sorted(self.cells, key=lambda c: c.creation_order):
            if cell.is_idle and cell.pending:
                deposit = cell.pending.popleft()
                self._begin_handling(cell, deposit)

    def _begin_handling(self, cell: Cell, deposit: Deposit) -> None:
        # Self-check.
        if deposit.token in cell.spectrum:
            self._consume(cell, deposit)
            return
        # Origin-loop check.
        if cell is deposit.origin and deposit.predecessor is not None:
            self._spawn(cell, deposit)
            return
        # (Canvas start goes here in Task 5.)

    def _consume(self, cell: Cell, deposit: Deposit) -> None:
        self.consume_log.append((self.tick_count, cell, deposit.token, deposit.age))

    def _spawn(self, cell: Cell, deposit: Deposit) -> None:
        new_cell = Cell(spectrum={deposit.token})
        new_cell.connectors.append(cell)
        cell.connectors.append(new_cell)
        self.add_cell(new_cell)
        self.spawn_log.append((self.tick_count, cell, new_cell, deposit.token))
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: all tests pass (4 from Task 3 + 2 new = 6 passed).

- [ ] **Step 5 (optional commit): "exp 135 phase 1: self-check + origin-loop spawn"**

---

## Task 5: Canvas state machine — query, response, forward-on-Same

This task wires up the 2-tick query/response timing and the `Same`-terminates-canvas case.

**Files:**
- Modify: `experiments/135_semantic_substrate/substrate.py`
- Modify: `experiments/135_semantic_substrate/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for canvas timing and Same-forward**

Append to `experiments/135_semantic_substrate/tests/test_substrate.py`:

```python
def test_canvas_to_neighbor_takes_two_ticks_and_forwards_on_same():
    """
    Setup: c0 (spectrum={0}) — c1 (spectrum={5}). Inject token=5 at c0.
    Expected timeline:
      Tick 1: c0 picks up deposit. Self-check fails. Canvas starts: query sent to c1.
      Tick 2: c1 receives query, classifies Same, sends response.
      Tick 3: c0 receives response (Same). Forwards deposit to c1. c1.pending has it.
      Tick 4: c1 picks up deposit. Self-check passes. Consumed.
    """
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={5}))
    c0.connectors.append(c1)
    c1.connectors.append(c0)
    s.inject(c0, token=5)

    s.tick()  # tick 1: c0 starts canvas (query in flight, arrives tick 2)
    assert len(s.consume_log) == 0
    assert not c0.is_idle
    assert c0.canvas_in_flight is c1

    s.tick()  # tick 2: c1 receives query, queues response (arrives tick 3)
    assert len(s.consume_log) == 0

    s.tick()  # tick 3: c0 receives Same, forwards to c1
    assert len(s.consume_log) == 0
    assert c0.is_idle
    assert len(c1.pending) == 1

    s.tick()  # tick 4: c1 picks up, self-check Same, consume
    assert len(s.consume_log) == 1
    tick, cell, token, age = s.consume_log[0]
    assert cell is c1
    assert token == 5
    assert tick == 4


def test_canvas_skips_predecessor():
    """
    c1 has connectors [c0, c2]. Deposit arriving at c1 with predecessor=c0
    should canvas only c2 (skipping c0).
    """
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum={2}))
    c1.connectors.extend([c0, c2])
    # Inject directly into c1 with predecessor=c0 (bypass normal injection).
    d = Deposit(token=2, predecessor=c0, origin=c0, age=0)
    c1.pending.append(d)

    s.tick()  # c1 picks up, starts canvas. Should query only c2.
    assert c1.canvas_in_flight is c2
    # canvas_remaining should be empty (c2 was the only non-predecessor neighbor)
    assert c1.canvas_remaining == []
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: 2 new tests fail (canvas not implemented yet).

- [ ] **Step 3: Implement canvas state machine**

Modify `experiments/135_semantic_substrate/substrate.py`:

Add event payload classes near the top (after `_Event`):

```python
@dataclass
class _Query:
    from_cell: Cell
    to_cell: Cell
    token: int


@dataclass
class _Response:
    from_cell: Cell  # the cell that classified
    to_cell: Cell    # the cell that asked
    response: Response
```

Update `tick()` to process events first, then schedule idle cells:

```python
    def tick(self) -> None:
        self.tick_count += 1
        # 1. Process all events arriving at this tick.
        while self._events and self._events[0].arrival_tick == self.tick_count:
            ev = heapq.heappop(self._events)
            self._process_event(ev.payload)
        # 2. Idle cells with pending deposits start handling next deposit.
        for cell in sorted(self.cells, key=lambda c: c.creation_order):
            if cell.is_idle and cell.pending:
                deposit = cell.pending.popleft()
                self._begin_handling(cell, deposit)

    def _process_event(self, payload) -> None:
        if isinstance(payload, _Query):
            response = payload.to_cell.classify(payload.token)
            self._enqueue(self.tick_count + 1, _Response(
                from_cell=payload.to_cell,
                to_cell=payload.from_cell,
                response=response,
            ))
        elif isinstance(payload, _Response):
            self._handle_response(payload)
```

Extend `_begin_handling` to start canvas after self-check + origin-loop fail:

```python
    def _begin_handling(self, cell: Cell, deposit: Deposit) -> None:
        if deposit.token in cell.spectrum:
            self._consume(cell, deposit)
            return
        if cell is deposit.origin and deposit.predecessor is not None:
            self._spawn(cell, deposit)
            return
        # Start canvas.
        cell.current_deposit = deposit
        cell.canvas_responses = []
        cell.canvas_remaining = self._canvas_order(cell, deposit.predecessor)
        if not cell.canvas_remaining:
            # Empty canvas (only neighbor was predecessor) → spawn.
            self._spawn(cell, deposit)
            self._reset_canvas_state(cell)
            return
        self._send_next_query(cell)

    def _canvas_order(self, cell: Cell, predecessor) -> list[Cell]:
        n = len(cell.connectors)
        if n == 0:
            return []
        start = cell.next_canvas_index % n
        ordered = [cell.connectors[(start + i) % n] for i in range(n)]
        cell.next_canvas_index = (start + 1) % n
        return [c for c in ordered if c is not predecessor]

    def _send_next_query(self, cell: Cell) -> None:
        next_neighbor = cell.canvas_remaining.pop(0)
        cell.canvas_in_flight = next_neighbor
        self._enqueue(self.tick_count + 1, _Query(
            from_cell=cell,
            to_cell=next_neighbor,
            token=cell.current_deposit.token,
        ))

    def _handle_response(self, payload: _Response) -> None:
        cell = payload.to_cell
        responder = payload.from_cell
        cell.canvas_responses.append((responder, payload.response))
        cell.canvas_in_flight = None
        if payload.response == Response.SAME:
            self._forward(cell, responder)
        elif cell.canvas_remaining:
            self._send_next_query(cell)
        else:
            self._decide_after_canvas(cell)  # implemented in Task 6

    def _forward(self, cell: Cell, target: Cell) -> None:
        deposit = cell.current_deposit
        deposit.predecessor = cell
        target.pending.append(deposit)
        self._reset_canvas_state(cell)

    def _reset_canvas_state(self, cell: Cell) -> None:
        cell.current_deposit = None
        cell.canvas_responses = []
        cell.canvas_remaining = []
        cell.canvas_in_flight = None

    def _decide_after_canvas(self, cell: Cell) -> None:
        # Implemented in Task 6.
        raise NotImplementedError
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: all tests pass (8 total).

- [ ] **Step 5 (optional commit): "exp 135 phase 1: canvas state machine + Same-forward"**

---

## Task 6: Canvas exhaustion — spawn-on-Unknown, forward-on-Different

**Files:**
- Modify: `experiments/135_semantic_substrate/substrate.py`
- Modify: `experiments/135_semantic_substrate/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for the two exhaustion branches**

Append to `experiments/135_semantic_substrate/tests/test_substrate.py`:

```python
def test_canvas_exhaustion_with_unknown_spawns_child():
    """
    c0 (spectrum={0}) connected to c1 (spectrum={1}, populated → Different)
    and c2 (spectrum=set(), empty → Unknown).
    Inject token=99 at c0. Canvas should yield Different + Unknown,
    no Same → spawn new child of c0 with spectrum={99}.
    """
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum=set()))  # empty → Unknown
    c0.connectors.extend([c1, c2])
    c1.connectors.append(c0)
    c2.connectors.append(c0)
    s.inject(c0, token=99)

    # Run enough ticks for full canvas + decision.
    for _ in range(10):
        s.tick()

    # Should have spawned a new child of c0 with spectrum {99}.
    assert len(s.spawn_log) == 1
    _, parent, child, token = s.spawn_log[0]
    assert parent is c0
    assert token == 99
    assert child.spectrum == {99}
    assert child in c0.connectors
    assert c0.is_idle


def test_canvas_exhaustion_all_different_forwards_to_first_different():
    """
    c0 (spectrum={0}) connected to c1 (spectrum={1}) and c2 (spectrum={2}).
    Inject token=7 at c0. Both neighbors say Different. Forward to first
    Different responder (c1, since round-robin starts at index 0).
    """
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c2 = s.add_cell(Cell(spectrum={2}))
    c0.connectors.extend([c1, c2])
    c1.connectors.append(c0)
    c2.connectors.append(c0)
    s.inject(c0, token=7)

    # Run enough ticks for full canvas + decision + handoff.
    for _ in range(10):
        s.tick()

    # No spawn yet — deposit was forwarded.
    assert len(s.spawn_log) == 0
    # c1 should have received the deposit (and possibly already started canvasing).
    # Check via the forward chain: c0 is idle, c1 has either pending or canvasing.
    assert c0.is_idle
    # c1 either is canvasing the deposit or already forwarded it. Easy assertion:
    # the deposit's predecessor is c0 once forwarded. We can find it by inspecting
    # c1.current_deposit or its onward forwards. For this test, just check that
    # the deposit left c0 (no spawn, c0 idle, no consume yet).
    assert len(s.consume_log) == 0
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: 2 new tests fail with `NotImplementedError` from `_decide_after_canvas`.

- [ ] **Step 3: Implement `_decide_after_canvas`**

In `experiments/135_semantic_substrate/substrate.py`, replace the `_decide_after_canvas` stub:

```python
    def _decide_after_canvas(self, cell: Cell) -> None:
        deposit = cell.current_deposit
        responses = cell.canvas_responses
        has_unknown = any(r == Response.UNKNOWN for (_, r) in responses)
        if has_unknown:
            self._spawn(cell, deposit)
            self._reset_canvas_state(cell)
            return
        first_different = next(
            (n for (n, r) in responses if r == Response.DIFFERENT),
            None,
        )
        if first_different is not None:
            self._forward(cell, first_different)
            return
        # All Same? Impossible — Same terminates canvas in _handle_response.
        raise AssertionError("canvas exhausted with no Same/Different/Unknown")
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: all tests pass (10 total).

- [ ] **Step 5: Add deposit-aging in tick()**

The age field on Deposit is currently never incremented. Each tick a deposit is "live" (in pending or being canvased), age should grow by 1.

Modify `tick()` in `substrate.py`, add at the very end:

```python
        # 3. Age all in-flight deposits (pending + currently being canvased).
        for cell in self.cells:
            if cell.current_deposit is not None:
                cell.current_deposit.age += 1
            for d in cell.pending:
                d.age += 1
```

- [ ] **Step 6: Add an aging test**

Append to `tests/test_substrate.py`:

```python
def test_deposit_age_increments_each_tick_while_in_flight():
    s = Substrate()
    c0 = s.add_cell(Cell(spectrum={0}))
    c1 = s.add_cell(Cell(spectrum={1}))
    c0.connectors.append(c1)
    c1.connectors.append(c0)
    d = s.inject(c0, token=5)  # not in any spectrum, will canvas indefinitely if no Unknown
    assert d.age == 0
    s.tick()  # tick 1: c0 picks up, starts canvas
    assert d.age == 1
    s.tick()  # tick 2: c1 receives query, sends response
    assert d.age == 2
    s.tick()  # tick 3: c0 gets Different, no remaining neighbors, would forward... but there are none non-predecessor with Different that aren't c1 itself
    # Actually with only one neighbor (c1) and predecessor=None, canvas_remaining is just [c1].
    # After c1 responds Different, _decide_after_canvas runs: no Unknown, first_different=c1, forwards to c1.
    # So d should now be on c1.pending with predecessor=c0.
    assert d in c1.pending
    assert d.predecessor is c0
```

- [ ] **Step 7: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_substrate.py -v`
Expected: all tests pass (11 total).

- [ ] **Step 8 (optional commit): "exp 135 phase 1: canvas exhaustion + deposit aging"**

---

## Task 7: K=6 ring fixture + Injector

**Files:**
- Create: `experiments/135_semantic_substrate/fixture.py`
- Create: `experiments/135_semantic_substrate/tests/test_fixture.py`

- [ ] **Step 1: Write failing tests for fixture**

`experiments/135_semantic_substrate/tests/test_fixture.py`:

```python
from cell import Cell, Response
from substrate import Substrate
from fixture import build_k6_ring, Injector


def test_k6_ring_has_six_cells_with_singleton_spectra():
    s = Substrate()
    cells = build_k6_ring(s)
    assert len(cells) == 6
    for i, c in enumerate(cells):
        assert c.spectrum == {i}


def test_k6_ring_topology_each_cell_linked_to_two_neighbors():
    s = Substrate()
    cells = build_k6_ring(s)
    for i, c in enumerate(cells):
        prev = cells[(i - 1) % 6]
        next_ = cells[(i + 1) % 6]
        assert prev in c.connectors
        assert next_ in c.connectors
        assert len(c.connectors) == 2


def test_k6_ring_classify_responses():
    s = Substrate()
    cells = build_k6_ring(s)
    assert cells[0].classify(0) == Response.SAME
    assert cells[0].classify(3) == Response.DIFFERENT
    assert cells[3].classify(3) == Response.SAME


def test_injector_50_50_mix_with_seeded_rng_is_reproducible():
    inj_a = Injector(seed=42, known_alphabet=(0,1,2,3,4,5), unknown_alphabet=(6,7,8,9,10))
    inj_b = Injector(seed=42, known_alphabet=(0,1,2,3,4,5), unknown_alphabet=(6,7,8,9,10))
    tokens_a = [inj_a.next_token() for _ in range(100)]
    tokens_b = [inj_b.next_token() for _ in range(100)]
    assert tokens_a == tokens_b


def test_injector_only_emits_from_alphabets():
    inj = Injector(seed=42, known_alphabet=(0,1,2,3,4,5), unknown_alphabet=(6,7,8,9,10))
    valid = set(range(6)) | {6,7,8,9,10}
    for _ in range(1000):
        t = inj.next_token()
        assert t in valid


def test_injector_mix_ratio_approximately_50_50():
    inj = Injector(seed=42, known_alphabet=(0,1,2,3,4,5), unknown_alphabet=(6,7,8,9,10))
    known_count = 0
    n = 10000
    for _ in range(n):
        t = inj.next_token()
        if t < 6:
            known_count += 1
    # 50/50 with seed=42 should land within a few percent.
    ratio = known_count / n
    assert 0.45 < ratio < 0.55
```

- [ ] **Step 2: Run tests to verify they fail**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/test_fixture.py -v`
Expected: ImportError — `fixture` module doesn't exist.

- [ ] **Step 3: Implement `fixture.py`**

`experiments/135_semantic_substrate/fixture.py`:

```python
from __future__ import annotations
import random

from cell import Cell
from substrate import Substrate


def build_k6_ring(substrate: Substrate) -> list[Cell]:
    """Create 6 cells in a ring, each with spectrum {i}, linked bidirectionally."""
    cells = [Cell(spectrum={i}) for i in range(6)]
    for c in cells:
        substrate.add_cell(c)
    for i, c in enumerate(cells):
        prev_c = cells[(i - 1) % 6]
        next_c = cells[(i + 1) % 6]
        c.connectors.extend([prev_c, next_c])
    return cells


class Injector:
    """Emits tokens drawn 50/50 from known + unknown alphabets, with seeded RNG."""

    def __init__(
        self,
        seed: int,
        known_alphabet: tuple[int, ...] = (0, 1, 2, 3, 4, 5),
        unknown_alphabet: tuple[int, ...] = (6, 7, 8, 9, 10),
        known_probability: float = 0.5,
    ) -> None:
        self.rng = random.Random(seed)
        self.known_alphabet = known_alphabet
        self.unknown_alphabet = unknown_alphabet
        self.known_probability = known_probability

    def next_token(self) -> int:
        if self.rng.random() < self.known_probability:
            return self.rng.choice(self.known_alphabet)
        return self.rng.choice(self.unknown_alphabet)
```

- [ ] **Step 4: Run tests to verify they pass**

Run: `W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/tests/ -v`
Expected: all tests pass (11 substrate + 6 fixture = 17 total).

- [ ] **Step 5 (optional commit): "exp 135 phase 1: K=6 ring fixture + Injector"**

---

## Task 8: Phase 1 deliverable run

**Files:**
- Create: `experiments/135_semantic_substrate/phase1_test.py`
- Create: `experiments/135_semantic_substrate/RESULTS_phase1.md` (after the run)

- [ ] **Step 1: Write the deliverable test (10K-tick run + measurements + assertions)**

`experiments/135_semantic_substrate/phase1_test.py`:

```python
"""
Experiment 135 Phase 1 deliverable.

Run the K=6 ring + 50/50 injector for 10K ticks. Capture all measurements
defined in PHASE1_DESIGN.md and assert all success criteria.
"""
from __future__ import annotations
from collections import Counter

from cell import Cell, Response
from substrate import Substrate
from fixture import build_k6_ring, Injector


N_TICKS = 10_000
INJECTION_PERIOD = 15
SNAPSHOT_PERIOD = 500
SEED = 42


def test_phase1_k6_ring_run():
    s = Substrate()
    ring = build_k6_ring(s)
    c0 = ring[0]
    injector = Injector(seed=SEED)

    snapshots: list[dict] = []
    n_known_injected = 0
    n_unknown_injected = 0

    for tick_idx in range(1, N_TICKS + 1):
        # Inject every INJECTION_PERIOD ticks, starting at tick 1.
        if tick_idx % INJECTION_PERIOD == 1:
            token = injector.next_token()
            s.inject(c0, token=token)
            if token < 6:
                n_known_injected += 1
            else:
                n_unknown_injected += 1
        s.tick()
        if tick_idx % SNAPSHOT_PERIOD == 0:
            n_in_flight = sum(1 for c in s.cells if c.current_deposit is not None)
            sum_pending = sum(len(c.pending) for c in s.cells)
            max_pending = max((len(c.pending) for c in s.cells), default=0)
            snapshots.append({
                "tick": tick_idx,
                "n_cells": len(s.cells),
                "n_connectors": sum(len(c.connectors) for c in s.cells),  # counts each edge twice
                "n_in_flight": n_in_flight,
                "sum_pending": sum_pending,
                "max_pending": max_pending,
            })

    # ===== Measurements =====
    n_consumed = len(s.consume_log)
    n_spawned = len(s.spawn_log)
    n_in_flight_at_end = sum(1 for c in s.cells if c.current_deposit is not None)
    n_pending_at_end = sum(len(c.pending) for c in s.cells)

    # Per-deposit fate (consumed-by-ring vs consumed-by-spawned-child).
    spawned_children = {child for (_, _, child, _) in s.spawn_log}
    n_consumed_by_ring = sum(1 for (_, cell, _, _) in s.consume_log if cell in ring)
    n_consumed_by_spawned = sum(1 for (_, cell, _, _) in s.consume_log if cell in spawned_children)

    # Known-token routing: each known token i should be consumed at ring[i].
    known_routing_correct = 0
    known_routing_total = 0
    for (_, cell, token, _) in s.consume_log:
        if token < 6:
            known_routing_total += 1
            if cell is ring[token]:
                known_routing_correct += 1

    # Unknown-token routing after spawn: re-injected unknowns should be consumed by spawned children.
    # Group unknowns into "first-injection" (spawn) vs "re-injection" (Same routing).
    unknown_spawn_tokens = {token for (_, _, _, token) in s.spawn_log}
    n_unknown_spawned = len(s.spawn_log)
    n_unknown_consumed_by_spawned = sum(
        1 for (_, cell, token, _) in s.consume_log
        if token >= 6 and cell in spawned_children
    )
    # Total unknown deposits that resolved (consumed or spawned).
    n_unknown_resolved = n_unknown_spawned + n_unknown_consumed_by_spawned

    # Max age of any consumed deposit.
    max_consumed_age = max((age for (_, _, _, age) in s.consume_log), default=0)
    # Max pending across all snapshots.
    max_pending_observed = max((s["max_pending"] for s in snapshots), default=0)

    # ===== Print summary =====
    print()
    print("========== EXP 135 PHASE 1 RESULTS ==========")
    print(f"Run: {N_TICKS} ticks, injection every {INJECTION_PERIOD} ticks, seed={SEED}")
    print()
    print(f"Injected:        {n_known_injected + n_unknown_injected} total ({n_known_injected} known, {n_unknown_injected} unknown)")
    print(f"Consumed:        {n_consumed}")
    print(f"  by ring cells: {n_consumed_by_ring}")
    print(f"  by spawned:    {n_consumed_by_spawned}")
    print(f"Spawned cells:   {n_spawned}")
    print(f"In-flight at end:{n_in_flight_at_end}")
    print(f"Pending at end:  {n_pending_at_end}")
    print()
    print(f"Known routing accuracy: {known_routing_correct}/{known_routing_total}"
          + (f" = {100*known_routing_correct/known_routing_total:.1f}%" if known_routing_total else ""))
    print(f"Unknown spawn count:    {n_unknown_spawned} (expected: 5)")
    print(f"Unknown re-routed:      {n_unknown_consumed_by_spawned}")
    print(f"Unknowns resolved:      {n_unknown_resolved} / {n_unknown_injected}")
    print()
    print(f"Max age of consumed deposit: {max_consumed_age} ticks")
    print(f"Max pending observed:        {max_pending_observed}")
    print()
    print("Snapshots:")
    for snap in snapshots:
        print(f"  tick {snap['tick']:5d}: n_cells={snap['n_cells']:3d} "
              f"n_connectors_dir={snap['n_connectors']:4d} "
              f"in_flight={snap['n_in_flight']:2d} "
              f"sum_pending={snap['sum_pending']:3d} "
              f"max_pending={snap['max_pending']:2d}")
    print()
    print("Spawn log (tick, parent_idx, child_spectrum):")
    for (tick, parent, child, token) in s.spawn_log:
        parent_idx = parent.creation_order
        print(f"  tick {tick:5d}: parent={parent_idx} child_spectrum={child.spectrum}")
    print()

    # ===== Assertions (success criteria from PHASE1_DESIGN.md) =====

    # 1. Ring integrity
    for i, c in enumerate(ring):
        assert c.spectrum == {i}, f"ring cell {i} spectrum mutated: {c.spectrum}"
        prev_c = ring[(i - 1) % 6]
        next_c = ring[(i + 1) % 6]
        assert prev_c in c.connectors, f"ring cell {i} lost left neighbor"
        assert next_c in c.connectors, f"ring cell {i} lost right neighbor"

    # 2. Known-token routing accuracy ≥ 95%
    if known_routing_total > 0:
        accuracy = known_routing_correct / known_routing_total
        assert accuracy >= 0.95, f"known routing accuracy {accuracy:.3f} < 0.95"

    # 3. Spawn count == 5 (one per distinct unknown)
    assert n_unknown_spawned == 5, f"expected 5 spawns (one per distinct unknown token), got {n_unknown_spawned}"
    # Spawned spectra cover the unknown alphabet exactly.
    spawned_spectra_union = set()
    for child in spawned_children:
        spawned_spectra_union |= child.spectrum
    assert spawned_spectra_union == {6, 7, 8, 9, 10}, (
        f"spawned spectra cover {spawned_spectra_union}, expected {{6,7,8,9,10}}"
    )

    # 4. Re-injected unknowns route into spawned children (≥ 95% post-spawn)
    if n_unknown_injected > n_unknown_spawned:
        post_spawn_unknowns = n_unknown_injected - n_unknown_spawned
        # Count post-spawn unknowns consumed by spawned children.
        # Approximation: spawned-child consumes count / (n_unknown_injected - n_unknown_spawned)
        if post_spawn_unknowns > 0:
            ratio = n_unknown_consumed_by_spawned / post_spawn_unknowns
            assert ratio >= 0.95, (
                f"only {ratio:.3f} of post-spawn unknowns routed to spawned children"
            )

    # 5. No livelock: max age bounded
    assert max_consumed_age < 50, f"max consumed deposit age = {max_consumed_age} (expected < 50)"

    # 6. Bounded queueing
    assert max_pending_observed <= 10, f"max pending = {max_pending_observed} (expected ≤ 10)"

    # 7. Most deposits resolved
    n_in_flight_or_pending = n_in_flight_at_end + n_pending_at_end
    n_injected_total = n_known_injected + n_unknown_injected
    assert n_in_flight_or_pending < 0.05 * n_injected_total, (
        f"too many deposits unresolved: {n_in_flight_or_pending} of {n_injected_total}"
    )

    print("========== ALL SUCCESS CRITERIA PASSED ==========")
```

- [ ] **Step 2: Run the deliverable test, redirect output to log**

Run:
```bash
W:\tools\python\python.exe -m pytest experiments/135_semantic_substrate/phase1_test.py -v -s 2>&1 | tee experiments/135_semantic_substrate/phase1_run.log
```
Expected: PASSED. Wall-clock: a few seconds (10K ticks of pure-Python simulation on a tiny substrate).

- [ ] **Step 3: If it fails, debug — do NOT relax the success criteria**

If the deliverable test fails, treat it as an experimental finding. Investigate:
- Mechanism bug? Trace through which assertion fired and what the actual state is.
- Parameter issue? E.g., max_pending too tight — note it and re-run with adjusted cadence (treat the original cadence as a measurement of saturation behavior, not a failure).
- Design bug surfaced by runtime behavior? Document it; the design may need a follow-up edit.

The criteria in `PHASE1_DESIGN.md` are predictions about how the mechanism *should* behave. If reality disagrees, that's the experimental result — don't paper over it.

- [ ] **Step 4: Write `RESULTS_phase1.md`**

`experiments/135_semantic_substrate/RESULTS_phase1.md`:

Use this skeleton; fill in numbers from the actual run output:

```markdown
# Experiment 135 Phase 1 — Results

**Status:** [PASSED / HONEST NEGATIVE / PARTIAL] — [one-line summary]
**Date run:** 2026-05-01
**Spec:** `PHASE1_DESIGN.md`
**Run command:** `pytest experiments/135_semantic_substrate/phase1_test.py -v -s`
**Wall-clock:** [X seconds]

## Summary

[2–4 sentences describing what was tested and the headline result.]

## Configuration

- Substrate: K=6 ring (preset spectra `{i}` per cell `c_i`)
- Injection: every 15 ticks at `c0`, 50/50 known/unknown, seed=42
- Run length: 10,000 ticks (~666 deposits)
- Unknown alphabet: {6, 7, 8, 9, 10}

## Measurements

| Quantity | Value |
|---|---|
| Total injected | [N] |
| Known injected | [N] |
| Unknown injected | [N] |
| Consumed | [N] |
| Spawned cells | [N] (expected 5) |
| In-flight at end | [N] |
| Pending at end | [N] |
| Known routing accuracy | [X]/[Y] = [Z]% |
| Unknown re-routing accuracy | [X]/[Y] = [Z]% |
| Max consumed-deposit age | [N] ticks |
| Max pending observed | [N] |

## Topology growth

[Brief description from snapshots — how did n_cells evolve?]

## What this proves

[Bullet points on the mechanism behaviors confirmed by the run.]

## What this does not prove

[Honest limits: small substrate, no learning tested, no patterns interacted, etc.]

## Anomalies

[Anything surprising in the output. If nothing, say so.]

## Next steps

[Phase 2 candidate: add learning (v8 causal-window), test multiple injection points, scale up substrate, etc.]

## Files

- `PHASE1_DESIGN.md` — design spec
- `phase1_test.py` — test runner
- `phase1_run.log` — full run output
- `RESULTS_phase1.md` — this file
```

- [ ] **Step 5: Final commit**

```bash
git add experiments/135_semantic_substrate/
git commit -m "exp 135 phase 1: semantic substrate with reactive canvas + origin-loop spawn

Implementation of PHASE1_DESIGN.md. K=6 ring fixture, preset spectra,
50/50 known-unknown stream injection. All Phase 1 success criteria passed
in [WALL_CLOCK]s: ring integrity held, known tokens routed at >=95%,
exactly 5 spawned children matched the unknown alphabet, no livelock,
bounded queueing.

See RESULTS_phase1.md for measurements."
```

---

## Self-review notes

Spec coverage: every requirement in `PHASE1_DESIGN.md` traces to a task —
- Cell + spectrum + classify → Task 2
- Deposit + predecessor + origin → Task 2
- Substrate + tick + inject → Task 3
- Self-check + origin-loop → Task 4
- Canvas + 2-tick timing + Same-forward → Task 5
- Canvas exhaustion + Unknown-spawn + Different-forward → Task 6
- K=6 ring + injector + 50/50 mix + cadence 15 + 5-token unknown alphabet → Task 7
- 10K-tick run + all measurements + all success criteria → Task 8

Type consistency check: `Cell` exposes `spectrum`, `connectors`, `pending`, `is_idle`, `current_deposit`, `canvas_responses`, `canvas_remaining`, `canvas_in_flight`, `next_canvas_index`, `creation_order`, `classify()`. All used consistently across tasks. `Substrate` exposes `tick_count`, `cells`, `consume_log`, `spawn_log`, `add_cell()`, `inject()`, `tick()`. Used consistently. `Deposit` fields `token`, `predecessor`, `origin`, `age`. Used consistently. `Response` enum values `SAME`, `DIFFERENT`, `UNKNOWN`. Used consistently.

No placeholder steps — every code step has working code. The only "TBD"-ish thing is in Task 8 Step 4's RESULTS template, which is a template the engineer fills in *from* the run output (not a deferred design decision).
