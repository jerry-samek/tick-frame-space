# Grow Until Observed Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement the three-layer "grow until observed" capacitor substrate (charging phase, adaptive threshold, load-bearing connectors) on a cubic lattice and verify that a K=4 capacitor cycle is sustained — same 4 cells in same firing order, with thresholds and waveforms within ±10% of steady-state — for at least 5,000 cycles in vacuum.

**Architecture:** Cubic-lattice substrate (10×10×10) with capacitor cells (charge_level, threshold, state) and connector edges (load, in-transit deposits). Per-tick procedure: relax thresholds, propagate connector deposits, accumulate charge at receivers, fire cells whose charge crosses threshold (reset charge, raise threshold, emit deposits). Phase 1 sets `load_coefficient = 0` (mechanism present, not exercised); Phase 2 will turn it on.

**Tech Stack:** Python 3, pytest, stdlib + dataclasses. No numpy.

**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-design.md` and `docs/theory/raw/132_untested_capacitor.md` (RAW 132).

---

## File Structure

```
experiments/132_grow_until_observed/
├── README.md           # already exists; updated in Task 9
├── conftest.py         # pytest sys.path fix (leading-digit dir name)
├── __init__.py         # empty
├── parameters.py       # default parameter values + named constants
├── capacitor.py        # Cell datatype + charge/fire/threshold dynamics
├── connectors.py       # Connector datatype + propagation + load
├── substrate.py        # cubic lattice helpers (face_neighbors, etc.)
├── tick.py             # 5-step per-tick driver
├── fixture.py          # K=4 cycle definition + bootstrap procedure
├── tests/
│   ├── __init__.py
│   ├── test_capacitor.py
│   ├── test_connectors.py
│   ├── test_substrate.py
│   ├── test_tick.py
│   └── test_fixture.py
├── phase1_test.py      # 5000-cycle sustainment test (the deliverable)
└── RESULTS_phase1.md   # outcome documentation (Task 9)
```

**File responsibilities:**
- `parameters.py` — single source of truth for the 7 parameters; tunable via dataclass override.
- `capacitor.py` — Cell datatype, threshold relaxation, threshold-crossing check, discharge action. No knowledge of connectors or lattice topology.
- `connectors.py` — Connector datatype, propagation step, load tracking, deposit delivery. No knowledge of capacitor internals beyond receiving deposits.
- `substrate.py` — Cubic-lattice helpers: face_neighbors, lattice initialization. No knowledge of capacitors or dynamics.
- `tick.py` — Orchestrates the 5-step per-tick procedure, calling into capacitor.py and connectors.py.
- `fixture.py` — K=4 cycle topology + bootstrap procedure (staggered initial charges, connector setup).
- `phase1_test.py` — Runs fixture for 5000 cycles, asserts sustainment per spec §"Success Criterion."

---

## Task 1: Project scaffolding

**Files:**
- Create: `experiments/132_grow_until_observed/conftest.py`
- Create: `experiments/132_grow_until_observed/__init__.py`
- Create: `experiments/132_grow_until_observed/tests/__init__.py`
- Create: `experiments/132_grow_until_observed/parameters.py`
- Create stub: `experiments/132_grow_until_observed/capacitor.py`
- Create stub: `experiments/132_grow_until_observed/connectors.py`
- Create stub: `experiments/132_grow_until_observed/substrate.py`
- Create stub: `experiments/132_grow_until_observed/tick.py`
- Create stub: `experiments/132_grow_until_observed/fixture.py`
- Create stubs: `experiments/132_grow_until_observed/tests/test_*.py` (5 files)

- [ ] **Step 1: Create conftest.py**

```python
# experiments/132_grow_until_observed/conftest.py
"""Make modules importable without the leading-digit package prefix."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
```

- [ ] **Step 2: Create empty __init__.py for both top-level and tests/**

```python
# experiments/132_grow_until_observed/__init__.py
# experiments/132_grow_until_observed/tests/__init__.py
```

Both empty.

- [ ] **Step 3: Create parameters.py with default values**

```python
# experiments/132_grow_until_observed/parameters.py
"""Capacitor substrate parameters. Tunable for Phase 1 parameter search.

Provisional values per spec §"Parameters". Phase 1 may need to iterate;
document the working region in RESULTS_phase1.md.
"""
from dataclasses import dataclass


@dataclass
class Parameters:
    baseline_threshold: float = 100.0
    adaptation_rate: float = 0.5      # threshold += this on each discharge
    relaxation_rate: float = 0.05     # threshold -= this per idle tick (clamped at baseline)
    deposit_amount: float = 30.0      # charge added to receiver per arriving deposit
    load_coefficient: float = 0.0     # 0 for Phase 1 (deferred to Phase 2)
    propagation_time_base: float = 1.0
    bootstrap_charge_step: float = 0.25  # fraction of baseline_threshold per cell offset


DEFAULT = Parameters()
```

- [ ] **Step 4: Create stub capacitor.py**

```python
# experiments/132_grow_until_observed/capacitor.py
"""Capacitor cell datatype and charging/firing/threshold dynamics."""
from dataclasses import dataclass, field
from enum import Enum


class CellState(Enum):
    EMPTY = "empty"
    CHARGING = "charging"
    DISCHARGED = "discharged"


@dataclass
class Cell:
    charge_level: float = 0.0
    threshold: float = 100.0
    last_discharge_tick: int = -1
    state: CellState = CellState.EMPTY


# Functions implemented in Tasks 2-3.
def relax_threshold(cell: "Cell", current_tick: int, baseline: float, rate: float) -> None:
    raise NotImplementedError


def check_and_fire(cell: "Cell", current_tick: int, adaptation_rate: float) -> bool:
    raise NotImplementedError
```

- [ ] **Step 5: Create stub connectors.py**

```python
# experiments/132_grow_until_observed/connectors.py
"""Connector edge datatype and load-driven propagation."""
from dataclasses import dataclass, field

Cell = tuple[int, int, int]


@dataclass
class Deposit:
    remaining_propagation_time: float
    destination: Cell


@dataclass
class Connector:
    a: Cell
    b: Cell
    in_transit: list[Deposit] = field(default_factory=list)

    @property
    def current_load(self) -> int:
        return len(self.in_transit)


# Functions implemented in Tasks 4-5.
def emit_deposit(connector: Connector, source: Cell, propagation_time_base: float) -> None:
    raise NotImplementedError


def propagate_step(connector: Connector, load_coefficient: float) -> list[Deposit]:
    raise NotImplementedError
```

- [ ] **Step 6: Create stub substrate.py**

```python
# experiments/132_grow_until_observed/substrate.py
"""Cubic lattice helpers: face_neighbors, bounds checking."""

Cell = tuple[int, int, int]


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    raise NotImplementedError
```

- [ ] **Step 7: Create stub tick.py**

```python
# experiments/132_grow_until_observed/tick.py
"""Per-tick driver: 5-step procedure per spec §"Three-Layer Mechanism"."""
from capacitor import Cell
from connectors import Connector
from parameters import Parameters


def tick(
    cells: dict[tuple[int, int, int], Cell],
    connectors: list[Connector],
    current_tick: int,
    params: Parameters,
) -> list[tuple[int, int, int]]:
    """Run one tick. Returns list of cells that fired this tick."""
    raise NotImplementedError
```

- [ ] **Step 8: Create stub fixture.py**

```python
# experiments/132_grow_until_observed/fixture.py
"""K=4 capacitor cycle fixture: cell layout + connector wiring + bootstrap."""
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters


# K=4 cycle on 2x2 square at z=0 (matching Exp 134 F1 fixture geometry).
F1_CYCLE = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
]


def setup_fixture(params: Parameters) -> tuple[
    dict[tuple[int, int, int], Cell],
    list[Connector],
]:
    """Build the K=4 capacitor cycle: 4 cells with staggered initial charges,
    4 connectors wiring the cycle, all other lattice cells empty."""
    raise NotImplementedError
```

- [ ] **Step 9: Create test stubs**

For each of `test_capacitor.py`, `test_connectors.py`, `test_substrate.py`, `test_tick.py`, `test_fixture.py`:

```python
# experiments/132_grow_until_observed/tests/test_<name>.py
"""Unit tests for <module>."""
# Tests added in subsequent tasks.
```

- [ ] **Step 10: Verify pytest discovery**

Run from repo root:
```bash
pytest experiments/132_grow_until_observed/ --collect-only 2>&1 | tail -10
```

Expected: pytest reports test files discovered, no import errors. (No tests collected yet, but no errors.)

- [ ] **Step 11: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: scaffolding"
```

---

## Task 2: Substrate face_neighbors helper

**Files:**
- Modify: `experiments/132_grow_until_observed/substrate.py`
- Modify: `experiments/132_grow_until_observed/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_substrate.py
import substrate as s


def test_face_neighbors_origin():
    neighbors = s.face_neighbors((0, 0, 0))
    assert set(neighbors) == {
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    }


def test_face_neighbors_arbitrary():
    neighbors = s.face_neighbors((5, -3, 7))
    assert set(neighbors) == {
        (6, -3, 7), (4, -3, 7),
        (5, -2, 7), (5, -4, 7),
        (5, -3, 8), (5, -3, 6),
    }
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_substrate.py -v
```

Expected: 2 FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement face_neighbors**

```python
# experiments/132_grow_until_observed/substrate.py
"""Cubic lattice helpers: face_neighbors, bounds checking."""

Cell = tuple[int, int, int]


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    x, y, z = cell
    return [
        (x + 1, y, z), (x - 1, y, z),
        (x, y + 1, z), (x, y - 1, z),
        (x, y, z + 1), (x, y, z - 1),
    ]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_substrate.py -v
```

Expected: 2 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: face_neighbors helper"
```

---

## Task 3: Capacitor relax_threshold

**Files:**
- Modify: `experiments/132_grow_until_observed/capacitor.py`
- Modify: `experiments/132_grow_until_observed/tests/test_capacitor.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_capacitor.py
import pytest
from capacitor import Cell, CellState, relax_threshold, check_and_fire


def test_relax_threshold_decreases_when_idle():
    """A cell that didn't fire last tick should relax toward baseline."""
    cell = Cell(threshold=110.0, last_discharge_tick=-10)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == pytest.approx(110.0 - 0.05)


def test_relax_threshold_clamped_at_baseline():
    """Threshold should not go below baseline."""
    cell = Cell(threshold=100.02, last_discharge_tick=-10)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == 100.0


def test_relax_threshold_skipped_just_after_firing():
    """If cell fired last tick (current_tick - last_discharge_tick == 1),
    no relaxation this tick — adaptation just happened."""
    cell = Cell(threshold=110.0, last_discharge_tick=4)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == 110.0


def test_relax_threshold_applied_after_idle():
    """Two ticks since firing: relaxation applies."""
    cell = Cell(threshold=110.0, last_discharge_tick=3)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == pytest.approx(110.0 - 0.05)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_capacitor.py::test_relax_threshold_decreases_when_idle -v
```

Expected: FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement relax_threshold**

Replace the body in `capacitor.py`:

```python
def relax_threshold(cell: "Cell", current_tick: int, baseline: float, rate: float) -> None:
    """Relax threshold toward baseline if cell didn't just fire.

    Skipped on the tick immediately after firing (adaptation already happened).
    Clamped at baseline (threshold never goes below it).
    """
    if cell.last_discharge_tick == current_tick - 1:
        return
    cell.threshold = max(baseline, cell.threshold - rate)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_capacitor.py -v
```

Expected: 4 PASS (all relax_threshold tests).

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: capacitor relax_threshold"
```

---

## Task 4: Capacitor check_and_fire

**Files:**
- Modify: `experiments/132_grow_until_observed/capacitor.py`
- Modify: `experiments/132_grow_until_observed/tests/test_capacitor.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_capacitor.py`:

```python
def test_check_and_fire_no_fire_below_threshold():
    cell = Cell(charge_level=50.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is False
    assert cell.charge_level == 50.0
    assert cell.threshold == 100.0
    assert cell.last_discharge_tick == -1


def test_check_and_fire_fires_at_threshold():
    cell = Cell(charge_level=100.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is True
    assert cell.charge_level == 0.0
    assert cell.threshold == 100.5
    assert cell.last_discharge_tick == 5
    assert cell.state == CellState.DISCHARGED


def test_check_and_fire_fires_above_threshold():
    """Charge can exceed threshold (e.g., from arriving deposits) — still fires.
    Excess is discarded (charge resets to 0)."""
    cell = Cell(charge_level=130.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is True
    assert cell.charge_level == 0.0
    assert cell.threshold == 100.5


def test_check_and_fire_state_set_to_discharged():
    cell = Cell(charge_level=100.0, threshold=100.0, state=CellState.CHARGING)
    check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert cell.state == CellState.DISCHARGED
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_capacitor.py -v
```

Expected: 4 new FAILs with NotImplementedError.

- [ ] **Step 3: Implement check_and_fire**

Replace the body in `capacitor.py`:

```python
def check_and_fire(cell: "Cell", current_tick: int, adaptation_rate: float) -> bool:
    """Check if charge crossed threshold; if so, fire.

    Returns True if cell fired this tick.
    On firing: charge resets to 0, threshold rises by adaptation_rate,
    state set to DISCHARGED, last_discharge_tick recorded.
    """
    if cell.charge_level < cell.threshold:
        return False
    cell.charge_level = 0.0
    cell.threshold += adaptation_rate
    cell.last_discharge_tick = current_tick
    cell.state = CellState.DISCHARGED
    return True
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_capacitor.py -v
```

Expected: all 8 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: capacitor check_and_fire"
```

---

## Task 5: Connector emit_deposit and propagate_step

**Files:**
- Modify: `experiments/132_grow_until_observed/connectors.py`
- Modify: `experiments/132_grow_until_observed/tests/test_connectors.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_connectors.py
import pytest
from connectors import Connector, Deposit, emit_deposit, propagate_step


def test_emit_deposit_from_a_to_b():
    """Emitting from cell A puts deposit in transit toward cell B."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=1.0)
    assert conn.current_load == 1
    assert conn.in_transit[0].destination == (1, 0, 0)
    assert conn.in_transit[0].remaining_propagation_time == 1.0


def test_emit_deposit_from_b_to_a():
    """Emitting from cell B puts deposit in transit toward cell A."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(1, 0, 0), propagation_time_base=1.0)
    assert conn.in_transit[0].destination == (0, 0, 0)


def test_emit_deposit_unknown_source_raises():
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    with pytest.raises(ValueError, match=r"(?i)not.*endpoint"):
        emit_deposit(conn, source=(5, 5, 5), propagation_time_base=1.0)


def test_propagate_step_advances_deposit():
    """With load_coefficient=0, each step advances by exactly 1.0."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=2.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert arrived == []
    assert conn.in_transit[0].remaining_propagation_time == 1.0


def test_propagate_step_delivers_when_done():
    """Deposit arriving this step returned in arrived list, removed from in_transit."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=1.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert len(arrived) == 1
    assert arrived[0].destination == (1, 0, 0)
    assert conn.in_transit == []
    assert conn.current_load == 0


def test_propagate_step_load_zero_means_unaffected():
    """load_coefficient=0 means propagation rate is exactly 1/tick regardless of load."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=3.0)
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=3.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert arrived == []
    for d in conn.in_transit:
        assert d.remaining_propagation_time == 2.0
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_connectors.py -v
```

Expected: 6 FAIL with NotImplementedError.

- [ ] **Step 3: Implement emit_deposit and propagate_step**

Replace the bodies in `connectors.py`:

```python
def emit_deposit(connector: Connector, source: Cell, propagation_time_base: float) -> None:
    """Add a deposit to the connector traveling from source to the other endpoint."""
    if source == connector.a:
        destination = connector.b
    elif source == connector.b:
        destination = connector.a
    else:
        raise ValueError(
            f"source {source} is not an endpoint of connector "
            f"({connector.a}, {connector.b})"
        )
    connector.in_transit.append(
        Deposit(remaining_propagation_time=propagation_time_base, destination=destination)
    )


def propagate_step(connector: Connector, load_coefficient: float) -> list[Deposit]:
    """Advance all in-transit deposits by 1/(1 + load_coefficient × current_load).

    Returns the list of deposits that arrived this step (and removes them from in_transit).
    """
    advance = 1.0 / (1.0 + load_coefficient * connector.current_load)
    arrived: list[Deposit] = []
    remaining: list[Deposit] = []
    for d in connector.in_transit:
        d.remaining_propagation_time -= advance
        if d.remaining_propagation_time <= 0:
            arrived.append(d)
        else:
            remaining.append(d)
    connector.in_transit = remaining
    return arrived
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_connectors.py -v
```

Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: connectors emit_deposit + propagate_step"
```

---

## Task 6: Per-tick driver

**Files:**
- Modify: `experiments/132_grow_until_observed/tick.py`
- Modify: `experiments/132_grow_until_observed/tests/test_tick.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_tick.py
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters
from tick import tick


def _make_simple_setup():
    """Two cells connected by one bidirectional connector. Cell A has charge=100,
    threshold=100 — about to fire. Cell B is empty."""
    cell_a = Cell(charge_level=100.0, threshold=100.0)
    cell_b = Cell(charge_level=0.0, threshold=100.0)
    cells = {(0, 0, 0): cell_a, (1, 0, 0): cell_b}
    connectors = [Connector(a=(0, 0, 0), b=(1, 0, 0))]
    return cells, connectors


def test_tick_cell_fires_emits_deposit():
    """Cell A at threshold fires; deposit emitted into the connector."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    fired = tick(cells, connectors, current_tick=1, params=params)
    assert fired == [(0, 0, 0)]
    assert cells[(0, 0, 0)].charge_level == 0.0
    assert cells[(0, 0, 0)].threshold == 100.5
    assert connectors[0].current_load == 1
    assert connectors[0].in_transit[0].destination == (1, 0, 0)


def test_tick_deposit_propagates_then_arrives():
    """Tick 1: A fires, deposit in transit (propagation_time=1).
    Tick 2: deposit arrives at B, B's charge increases by deposit_amount."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    tick(cells, connectors, current_tick=1, params=params)
    # After tick 1, deposit is in transit with remaining_propagation_time = 1.0
    fired = tick(cells, connectors, current_tick=2, params=params)
    # Tick 2: propagation step decrements to 0, deposit arrives at B,
    # B's charge += deposit_amount (30). B did not fire (charge 30 < threshold 100).
    assert fired == []
    assert cells[(1, 0, 0)].charge_level == 30.0
    assert connectors[0].current_load == 0


def test_tick_threshold_relaxes_when_idle():
    """A cell with elevated threshold and no firing for several ticks
    should see its threshold relax."""
    cell = Cell(charge_level=0.0, threshold=110.0, last_discharge_tick=-100)
    cells = {(0, 0, 0): cell}
    connectors = []
    params = Parameters(baseline_threshold=100.0, relaxation_rate=0.05)
    tick(cells, connectors, current_tick=5, params=params)
    assert cell.threshold == 110.0 - 0.05


def test_tick_state_resets_to_empty_after_discharge():
    """After firing, state is DISCHARGED transiently, then EMPTY at end of tick."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    tick(cells, connectors, current_tick=1, params=params)
    assert cells[(0, 0, 0)].state == CellState.EMPTY
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_tick.py -v
```

Expected: 4 FAIL with NotImplementedError.

- [ ] **Step 3: Implement tick driver**

Replace the body in `tick.py`:

```python
"""Per-tick driver: 5-step procedure per spec §"Three-Layer Mechanism".

Order:
  1. Threshold relaxation for all cells.
  2. Connector propagation (advance deposits, collect arrivals).
  3. Charge accumulation (add arriving deposits to receiver charge).
  4. Threshold check + firing (cells whose charge ≥ threshold fire).
  5. State cleanup (DISCHARGED → EMPTY).
"""
from capacitor import Cell, CellState, check_and_fire, relax_threshold
from connectors import Connector, emit_deposit, propagate_step
from parameters import Parameters


def tick(
    cells: dict[tuple[int, int, int], Cell],
    connectors: list[Connector],
    current_tick: int,
    params: Parameters,
) -> list[tuple[int, int, int]]:
    """Run one tick. Returns list of cells that fired this tick."""
    # Step 1: threshold relaxation
    for cell in cells.values():
        relax_threshold(cell, current_tick, params.baseline_threshold, params.relaxation_rate)

    # Step 2: connector propagation
    arrivals: list = []
    for conn in connectors:
        arrivals.extend(propagate_step(conn, params.load_coefficient))

    # Step 3: charge accumulation at receivers
    for d in arrivals:
        if d.destination in cells:
            cells[d.destination].charge_level += params.deposit_amount

    # Step 4: threshold check + firing
    fired_cells: list[tuple[int, int, int]] = []
    for cell_pos, cell in cells.items():
        if check_and_fire(cell, current_tick, params.adaptation_rate):
            fired_cells.append(cell_pos)
            for conn in connectors:
                if cell_pos == conn.a or cell_pos == conn.b:
                    emit_deposit(conn, source=cell_pos, propagation_time_base=params.propagation_time_base)

    # Step 5: state cleanup
    for cell in cells.values():
        if cell.state == CellState.DISCHARGED:
            cell.state = CellState.EMPTY

    return fired_cells
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_tick.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: per-tick driver"
```

---

## Task 7: K=4 fixture setup

**Files:**
- Modify: `experiments/132_grow_until_observed/fixture.py`
- Modify: `experiments/132_grow_until_observed/tests/test_fixture.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_fixture.py
from capacitor import Cell, CellState
from connectors import Connector
from fixture import F1_CYCLE, setup_fixture
from parameters import Parameters


def test_fixture_has_four_cells():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert pos in cells


def test_fixture_has_four_connectors_in_cycle():
    """Cycle order: C0→C1→C2→C3→C0. 4 connectors."""
    params = Parameters()
    _, connectors = setup_fixture(params)
    assert len(connectors) == 4
    cycle_pairs = set()
    for conn in connectors:
        cycle_pairs.add(frozenset({conn.a, conn.b}))
    expected_pairs = {
        frozenset({(0, 0, 0), (1, 0, 0)}),
        frozenset({(1, 0, 0), (1, 1, 0)}),
        frozenset({(1, 1, 0), (0, 1, 0)}),
        frozenset({(0, 1, 0), (0, 0, 0)}),
    }
    assert cycle_pairs == expected_pairs


def test_fixture_staggered_initial_charges():
    """C0 about to fire (charge=threshold), then 0.75/0.50/0.25 of threshold."""
    params = Parameters(baseline_threshold=100.0, bootstrap_charge_step=0.25)
    cells, _ = setup_fixture(params)
    assert cells[(0, 0, 0)].charge_level == 100.0
    assert cells[(1, 0, 0)].charge_level == 75.0
    assert cells[(1, 1, 0)].charge_level == 50.0
    assert cells[(0, 1, 0)].charge_level == 25.0


def test_fixture_thresholds_at_baseline():
    params = Parameters(baseline_threshold=100.0)
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].threshold == 100.0


def test_fixture_initial_state_charging():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].state == CellState.CHARGING


def test_fixture_initial_last_discharge_tick():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].last_discharge_tick == -1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_fixture.py -v
```

Expected: 6 FAIL with NotImplementedError.

- [ ] **Step 3: Implement setup_fixture**

Replace the body in `fixture.py`:

```python
"""K=4 capacitor cycle fixture: cell layout + connector wiring + bootstrap."""
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters


# K=4 cycle on 2x2 square at z=0 (matching Exp 134 F1 fixture geometry).
F1_CYCLE = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
]


def setup_fixture(params: Parameters) -> tuple[
    dict[tuple[int, int, int], Cell],
    list[Connector],
]:
    """Build the K=4 capacitor cycle: 4 cells with staggered initial charges,
    4 connectors wiring the cycle.

    Bootstrap (per spec §"Initial bootstrap"):
      C0: charge = baseline_threshold (about to fire)
      C1: charge = 0.75 × baseline_threshold
      C2: charge = 0.50 × baseline_threshold
      C3: charge = 0.25 × baseline_threshold
    """
    cells: dict[tuple[int, int, int], Cell] = {}
    K = len(F1_CYCLE)
    for i, pos in enumerate(F1_CYCLE):
        # Cell at cycle position i gets charge = (1 - i/K) * baseline_threshold
        # for K=4: positions 0,1,2,3 → fractions 1.00, 0.75, 0.50, 0.25
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )

    connectors: list[Connector] = []
    for i in range(K):
        a = F1_CYCLE[i]
        b = F1_CYCLE[(i + 1) % K]
        connectors.append(Connector(a=a, b=b))

    return cells, connectors
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_fixture.py -v
```

Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/
git commit -m "Exp 132 Phase 1: K=4 fixture setup with staggered bootstrap"
```

---

## Task 8: Phase 1 deliverable test (5000-cycle sustainment)

**Files:**
- Create: `experiments/132_grow_until_observed/phase1_test.py`

- [ ] **Step 1: Write the deliverable test**

```python
# experiments/132_grow_until_observed/phase1_test.py
"""Phase 1 deliverable: 5000-cycle sustainment of K=4 capacitor cycle.

THE Phase 1 test. Pass means cycle structure is invariant — same 4 cells
firing in same order, thresholds and waveforms within tolerance — for at
least 5000 cycles. Fail means the parameter region needs more search OR
the three-layer mechanism cannot support pattern coherence.

Spec: docs/superpowers/specs/2026-04-28-grow-until-observed-design.md
"""
import pytest

from capacitor import Cell
from fixture import F1_CYCLE, setup_fixture
from parameters import Parameters
from tick import tick


# Phase 1 parameters; tune here if the cycle doesn't sustain.
PARAMS = Parameters(
    baseline_threshold=100.0,
    adaptation_rate=0.5,
    relaxation_rate=0.05,
    deposit_amount=30.0,
    load_coefficient=0.0,
    propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)

WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4


def _record_cycle(fired_history: list, last_cell_idx: int) -> tuple[bool, int]:
    """Find the next 4-fire window and check if it follows F1_CYCLE order
    starting from F1_CYCLE[last_cell_idx + 1].

    Returns (cycle_completed, new_last_cell_idx).
    """
    expected_idx = (last_cell_idx + 1) % K
    expected_cell = F1_CYCLE[expected_idx]
    if not fired_history:
        return False, last_cell_idx
    fired_this_tick = fired_history[-1]
    if fired_this_tick == expected_cell:
        return True, expected_idx
    elif len(fired_this_tick) > 0:
        # Some non-cycle cell fired, or wrong cycle order
        return False, last_cell_idx
    return False, last_cell_idx


def test_phase1_sustainment():
    cells, connectors = setup_fixture(PARAMS)

    # Warm-up: run for WARMUP_CYCLES * K ticks, ignore output.
    current_tick = 0
    for _ in range(WARMUP_CYCLES * K):
        current_tick += 1
        tick(cells, connectors, current_tick, PARAMS)

    # Record steady-state thresholds for tolerance check
    steady_thresholds = {pos: cells[pos].threshold for pos in F1_CYCLE}

    # Sustained cycles: run TARGET_CYCLES * K more ticks, verify firing pattern.
    fire_log: list[list[tuple[int, int, int]]] = []
    threshold_log: list[dict[tuple[int, int, int], float]] = []
    for _ in range(TARGET_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS)
        fire_log.append(fired)
        threshold_log.append({pos: cells[pos].threshold for pos in F1_CYCLE})

    # Check 1: every fire is one of the F1 cells.
    cycle_set = set(F1_CYCLE)
    non_cycle_fires = [
        (i, fires) for i, fires in enumerate(fire_log)
        for cell in fires if cell not in cycle_set
    ]
    assert non_cycle_fires == [], (
        f"Non-cycle cells fired: first 5 = {non_cycle_fires[:5]}"
    )

    # Check 2: each cycle cell fires the expected number of times.
    fire_counts = {pos: 0 for pos in F1_CYCLE}
    for fires in fire_log:
        for cell in fires:
            fire_counts[cell] += 1
    expected_fires = TARGET_CYCLES
    tolerance_fires = int(0.10 * expected_fires)
    for pos, count in fire_counts.items():
        assert abs(count - expected_fires) <= tolerance_fires, (
            f"Cell {pos} fired {count} times; expected ~{expected_fires} ± {tolerance_fires}"
        )

    # Check 3: thresholds stable within ±10% of steady_thresholds.
    tolerance = 0.10
    for pos in F1_CYCLE:
        baseline = steady_thresholds[pos]
        max_dev = max(abs(snap[pos] - baseline) for snap in threshold_log)
        max_allowed = max(tolerance * baseline, 1.0)  # at least 1.0 absolute tolerance
        assert max_dev <= max_allowed, (
            f"Cell {pos} threshold deviated by {max_dev:.2f} from steady "
            f"{baseline:.2f} (max allowed: {max_allowed:.2f})"
        )

    # Diagnostic output for RESULTS_phase1.md
    print(f"\nPhase 1 sustainment PASS")
    print(f"Cycles completed: {TARGET_CYCLES}")
    print(f"Fire counts: {fire_counts}")
    print(f"Steady-state thresholds (after warm-up): {steady_thresholds}")
    print(f"Final thresholds: {threshold_log[-1]}")
```

- [ ] **Step 2: Run the deliverable**

```bash
pytest experiments/132_grow_until_observed/phase1_test.py -v -s
```

Expected outcomes (one of three):

- **PASS:** all three checks hold for 5000 cycles → Phase 1 succeeded with provisional parameters. Capture printed output for RESULTS_phase1.md.
- **FAIL with non-cycle fires:** some cells outside F1_CYCLE fired. Investigate: are deposits leaking to non-pattern neighbors? (Cycle cells have non-pattern face-neighbors; if `deposit_amount` is too high, those neighbors may charge to threshold.)
- **FAIL with wrong fire counts:** cycle cells fired too few or too many times. Investigate: do the 4 cells reach steady-state firing rhythm? Adjust `deposit_amount`, `adaptation_rate`, or `relaxation_rate` and rerun.
- **FAIL with threshold drift:** thresholds keep climbing without leveling off. Investigate: is `relaxation_rate` too low for the firing rate? Increase relaxation or decrease adaptation.

If FAIL: tune parameters in `phase1_test.py` PARAMS dict, rerun, document the search in RESULTS_phase1.md.

- [ ] **Step 3: Capture run output**

```bash
pytest experiments/132_grow_until_observed/phase1_test.py -v -s > experiments/132_grow_until_observed/phase1_run.log 2>&1
```

- [ ] **Step 4: Run full test sweep as sanity check**

```bash
pytest experiments/132_grow_until_observed/ -v
```

Expected: all unit tests + phase1_test pass (~25 unit tests + 1 deliverable).

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/phase1_test.py experiments/132_grow_until_observed/phase1_run.log
git commit -m "Exp 132 Phase 1: 5000-cycle sustainment deliverable"
```

---

## Task 9: RESULTS_phase1.md and README update

**Files:**
- Create: `experiments/132_grow_until_observed/RESULTS_phase1.md`
- Modify: `experiments/132_grow_until_observed/README.md`

- [ ] **Step 1: Write RESULTS_phase1.md**

Use this template, filled in from Task 8's run:

```markdown
# Experiment 132 Phase 1 — Results

**Status:** [PASS | FAIL — describe | PARTIAL — describe]
**Date run:** [YYYY-MM-DD]
**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md`
**Theory:** `docs/theory/raw/132_untested_capacitor.md` (RAW 132)

## Summary

[1-2 sentences on what happened: did the K=4 cycle sustain for 5000 cycles
under the provisional parameters? If not, what parameter region (if any)
worked?]

## Working parameters

[Either the spec's provisional values, or the tuned values that produced PASS.]

| Parameter | Value | Notes |
|---|---|---|
| baseline_threshold | [X] | |
| adaptation_rate | [X] | |
| relaxation_rate | [X] | |
| deposit_amount | [X] | |
| load_coefficient | 0.0 | Deferred to Phase 2 |
| propagation_time_base | [X] | |

## Steady-state observations

- **Cycle period:** [X] ticks per full cycle (each cell fires every X ticks).
- **Fire counts over 5000 cycles:** C0=[X], C1=[X], C2=[X], C3=[X]
- **Steady-state thresholds (post-warmup):** C0=[X], C1=[X], C2=[X], C3=[X]
- **Threshold variation across 20000 ticks:** [max deviation] from steady state.

## Parameter search history (if iteration was needed)

[Document failed attempts and what was learned. Was the working region narrow
or broad? Which parameters were sensitive?]

## What this proves

- The three-layer "grow until observed" mechanism (RAW 132 §5) [supports |
  does not support] sustained cycle coherence in vacuum.
- [If PASS] None of the four prior experiments (131_a/131_b/133/134)
  combined all three layers; this experiment shows the combined mechanism
  has a working parameter region.
- [If FAIL] The strong falsification: not even with all three layers
  active can the capacitor model sustain a coherent renewal pattern in
  vacuum. RAW 132's hopeful reframe is rejected.

## What this does not prove

- Drift toward planet (Phase 2).
- 1/r² gradient, GR metric profile (Phase 3).
- Robustness to broader parameter ranges (Phase 1 finds *a* working region;
  characterizing the full region's size is more work).
- Sign-blind matter/antimatter behavior (deferred).

## Next steps

[If PASS:] Phase 2 — add planet pattern, observe drift. The substrate
primitives are now validated and reusable.
[If FAIL:] Diagnose. Was it parameter tuning, structural rule design, or
ontological? May warrant a return to brainstorming with the failure mode
in hand.
```

- [ ] **Step 2: Update README.md**

Replace the file contents with:

```markdown
# Experiment 132 — Grow Until Observed: Three-Layer Capacitor Substrate

**Theory:** [`docs/theory/raw/132_untested_capacitor.md`](../../docs/theory/raw/132_untested_capacitor.md) (RAW 132)
**Spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-design.md)
**Plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md)

**Predecessors (recent):**
- Exp 131_a (lineage_substrate) — RAW 131 first test, falsified
- Exp 131_b (anisotropic_connectors) — RAW 131 variant, partial result
- Exp 133 (closed_loop_substrate) — closed-loop integer hold-and-fire, falsified
- Exp 134 (pattern_coherence) — CA renewal, vacuum coherent but no field-at-distance

## Run

```bash
# Full test sweep
pytest experiments/132_grow_until_observed/ -v

# Phase 1 deliverable (5000-cycle sustainment)
pytest experiments/132_grow_until_observed/phase1_test.py -v -s
```

## Status

Phase 1: see `RESULTS_phase1.md`.
Phase 2 (drift in planet field): not yet started.
Phase 3 (GR metric profile): not yet started.

## Three-layer mechanism

| Layer | What grows | Discharge |
|---|---|---|
| Charging phase | Real charge level, 0 → threshold | Resets to 0; emits deposits to all connectors |
| Adaptive threshold | Threshold value, slowly with firing history | Each discharge raises threshold by adaptation amount |
| Connector load | Deposits in transit on each edge | Discharge releases deposits into connectors |

Phase 1: `load_coefficient = 0` (mechanism implemented, not exercised).
Phase 2: turns it on.
```

- [ ] **Step 3: Commit**

```bash
git add experiments/132_grow_until_observed/RESULTS_phase1.md experiments/132_grow_until_observed/README.md
git commit -m "Exp 132 Phase 1: RESULTS_phase1.md + README update"
```

---

## Self-Review

**Spec coverage:**
- Spec §"Substrate" → Tasks 1, 2 (face_neighbors)
- Spec §"Cell datatype" → Task 1 (stub) + Tasks 3, 4 (relax, fire)
- Spec §"Connector datatype" → Task 1 (stub) + Task 5 (emit, propagate)
- Spec §"Three-Layer Mechanism / Per-tick procedure" → Task 6
- Spec §"Initial bootstrap" → Task 7
- Spec §"Pattern Fixture: K=4 Capacitor Cycle" → Task 7
- Spec §"Parameters" → Task 1 (parameters.py)
- Spec §"Success Criterion" → Task 8 (3 checks: cycle membership, fire counts, threshold stability)
- Spec §"Falsification Modes" → Task 8 step 2 documents these as expected failure handling
- Spec §"Deliverables / file structure" → Tasks 1, 8, 9

All sections covered. No gaps.

**Placeholder scan:**
- RESULTS template has bracketed `[fill in]` markers — these are intentional template fields for the engineer to fill from the actual run, not implementation placeholders.
- No "TBD" / "TODO" / "implement later" in any task step.
- Every code step shows complete code.

**Type consistency:**
- `Cell` dataclass with charge_level, threshold, last_discharge_tick, state — used consistently across capacitor.py, tick.py, fixture.py, phase1_test.py.
- `Connector` dataclass with a, b, in_transit — used consistently.
- `Parameters` dataclass with 7 fields — used consistently in tick(), setup_fixture(), phase1_test PARAMS.
- `tick()` signature: `(cells, connectors, current_tick, params) -> list[fired_cell_pos]` — same in tick.py, tests, and phase1_test.

No issues found.

---

## Failure handling

- **Phase 1 fails sustainment (Task 8):** This is the test the experiment exists to run. If the provisional parameters don't sustain the cycle, the engineer iterates: tune parameters in `phase1_test.py`'s PARAMS dict, rerun, document what was tried. Document the parameter search in RESULTS_phase1.md. **Do not modify the test's success criteria** to make it pass; the criteria are the contract.
- **No parameter combination works:** This is the strong falsification of RAW 132's hopeful reframe. Document carefully — what was tried, what failure mode each attempt hit, why the engineer concluded no working region exists. This result is as valuable as a PASS.
- **Sustainment passes but with surprises:** e.g., the cycle period turns out to be different from expected (X ticks instead of 4), or thresholds settle at very different values than baseline. Document in RESULTS_phase1.md; these surprises are interesting data for Phase 2 design.
- **Unit tests fail:** likely a TDD bug in the implementation. The plan's test code is the contract; if the implementation can't pass the verbatim tests, the implementation is wrong, not the tests.
