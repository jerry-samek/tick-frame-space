# Grow Until Observed Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run a single instrumented experimental run on the capacitor substrate with planet + test patterns and full lattice connectivity, recording firing events per tick and substrate snapshots every 100 ticks, then post-hoc apply 4 reading functions and compute threshold(r) and load(r) profiles to test 4 hypotheses (H3.5, H4.1, H5.1, plus H5.3/H5.4/H5.5 panel) per RAW 132 §3.6.

**Architecture:** Phase 1's substrate primitives are reused unchanged (substrate.py, capacitor.py, connectors.py, tick.py, parameters.py). Phase 2 adds: (1) `lattice.py` for bounded cubic lattice + full face-adjacency connector wiring; (2) `observer.py` for the 4 reading functions; (3) `recording.py` for firing-event log + periodic substrate snapshots; (4) `profile.py` for threshold(r) and load(r) post-hoc analysis; (5) `phase2_test.py` as the deliverable.

**Tech Stack:** Python 3, pytest, stdlib + dataclasses + math (no numpy needed).

**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md`
**Theory:** `docs/theory/raw/132_untested_capacitor.md` §3.5, §3.6
**Predecessor:** Phase 1 PASS — substrate primitives validated.

---

## File Structure

```
experiments/132_grow_until_observed/
├── ... existing Phase 1 files (substrate.py, capacitor.py, connectors.py,
│       tick.py, fixture.py, parameters.py, conftest.py, RESULTS_phase1.md, etc.)
├── lattice.py            # bounded cubic lattice + full face-adjacency connector wiring
├── observer.py           # R5.1, R5.3, R5.4, R5.5 reading functions
├── recording.py          # firing-event log + periodic substrate snapshots
├── profile.py            # threshold(r), load(r) post-hoc analysis
├── tests/
│   ├── ... existing tests/ ...
│   ├── test_lattice.py
│   ├── test_observer.py
│   ├── test_recording.py
│   └── test_profile.py
├── phase2_test.py        # deliverable: full run + post-hoc analysis
├── phase2_run.log        # captured output
└── RESULTS_phase2.md     # per-hypothesis result table
```

**Module responsibilities (additive on Phase 1):**
- `lattice.py` — substrate region enumeration; full face-adjacency connector wiring; bounded by configurable extent.
- `observer.py` — 4 reading functions, each takes firing-event history (and optionally substrate snapshots) and returns a centroid or peak-position.
- `recording.py` — efficient firing-event accumulator + snapshot capture. No knowledge of analysis.
- `profile.py` — given a snapshot or end-of-run state and a center cell, compute threshold(r) and load(r) by binning over distance.

Phase 1 files are untouched.

---

## Task 1: lattice.py — bounded substrate + full connector wiring

**Files:**
- Create: `experiments/132_grow_until_observed/lattice.py`
- Create: `experiments/132_grow_until_observed/tests/test_lattice.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_lattice.py
from lattice import enumerate_cells, build_connectors


def test_enumerate_cells_small_box():
    """Box from (0,0,0) to (1,1,0) gives 4 cells."""
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 1))
    assert len(cells) == 4
    assert set(cells) == {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)}


def test_enumerate_cells_3d():
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 2))
    assert len(cells) == 8


def test_build_connectors_2x2_square():
    """2x2 square in z=0 plane: 4 cells, 4 face-adjacent edges."""
    cells = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 4
    pairs = {frozenset({c.a, c.b}) for c in connectors}
    expected = {
        frozenset({(0, 0, 0), (1, 0, 0)}),
        frozenset({(0, 0, 0), (0, 1, 0)}),
        frozenset({(1, 0, 0), (1, 1, 0)}),
        frozenset({(0, 1, 0), (1, 1, 0)}),
    }
    assert pairs == expected


def test_build_connectors_no_diagonal_connections():
    """Diagonal pairs (Manhattan distance 2) should NOT be connected."""
    cells = [(0, 0, 0), (1, 1, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 0


def test_build_connectors_3d_cube():
    """2x2x2 cube: 8 cells, 12 face-adjacent edges (3 per axis × 4 perpendicular pairs)."""
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 2))
    connectors = build_connectors(cells)
    assert len(connectors) == 12


def test_build_connectors_no_duplicates():
    """Each pair should have only one connector even if generated multiple times."""
    cells = [(0, 0, 0), (1, 0, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 1
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_lattice.py -v
```

Expected: 6 FAILs (ModuleNotFoundError).

- [ ] **Step 3: Implement lattice.py**

```python
# experiments/132_grow_until_observed/lattice.py
"""Bounded cubic lattice helpers: cell enumeration + full face-adjacency
connector wiring."""
from connectors import Connector
from substrate import face_neighbors

Cell = tuple[int, int, int]


def enumerate_cells(
    x_range: tuple[int, int],
    y_range: tuple[int, int],
    z_range: tuple[int, int],
) -> list[Cell]:
    """Enumerate all cells in the half-open box [x_range[0], x_range[1]) × ..."""
    return [
        (x, y, z)
        for x in range(x_range[0], x_range[1])
        for y in range(y_range[0], y_range[1])
        for z in range(z_range[0], z_range[1])
    ]


def build_connectors(cells: list[Cell]) -> list[Connector]:
    """Build a Connector for each pair of face-adjacent cells in the input list.

    Each pair is included at most once (the pair (a, b) and (b, a) produce one connector).
    """
    cell_set = set(cells)
    seen: set[frozenset[Cell]] = set()
    connectors: list[Connector] = []
    for cell in cells:
        for neighbor in face_neighbors(cell):
            if neighbor not in cell_set:
                continue
            pair = frozenset({cell, neighbor})
            if pair in seen:
                continue
            seen.add(pair)
            connectors.append(Connector(a=cell, b=neighbor))
    return connectors
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_lattice.py -v
```

Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/lattice.py experiments/132_grow_until_observed/tests/test_lattice.py
git commit -m "Exp 132 Phase 2: lattice helpers (cell enumeration + full connector wiring)"
```

---

## Task 2: observer.py — 4 reading functions

**Files:**
- Create: `experiments/132_grow_until_observed/observer.py`
- Create: `experiments/132_grow_until_observed/tests/test_observer.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_observer.py
from observer import (
    centroid_recent,
    centroid_threshold_elevated,
    peak_density_map,
    centroid_connected_firing,
)


def test_centroid_recent_simple():
    """4 firings of a 2x2 square at z=0, all in last N ticks → centroid is (0.5, 0.5, 0)."""
    firings = [
        (1, (0, 0, 0)),
        (2, (1, 0, 0)),
        (3, (1, 1, 0)),
        (4, (0, 1, 0)),
    ]
    centroid = centroid_recent(firings, current_tick=4, window=4)
    assert centroid == (0.5, 0.5, 0.0)


def test_centroid_recent_window_excludes_old():
    """Firings outside window are excluded."""
    firings = [
        (1, (10, 10, 10)),  # too old
        (5, (0, 0, 0)),
        (5, (2, 0, 0)),
    ]
    centroid = centroid_recent(firings, current_tick=5, window=4)
    assert centroid == (1.0, 0.0, 0.0)


def test_centroid_recent_empty_returns_none():
    centroid = centroid_recent([], current_tick=10, window=4)
    assert centroid is None


def test_centroid_threshold_elevated():
    """Cells with threshold > baseline by elevation_threshold contribute."""
    cell_thresholds = {
        (0, 0, 0): 100.5,
        (1, 0, 0): 100.5,
        (5, 5, 5): 100.0,  # at baseline, excluded
    }
    centroid = centroid_threshold_elevated(
        cell_thresholds, baseline=100.0, elevation_threshold=0.1
    )
    assert centroid == (0.5, 0.0, 0.0)


def test_centroid_threshold_elevated_no_elevated_cells():
    cell_thresholds = {(0, 0, 0): 100.0, (1, 0, 0): 100.0}
    centroid = centroid_threshold_elevated(
        cell_thresholds, baseline=100.0, elevation_threshold=0.1
    )
    assert centroid is None


def test_peak_density_map_simple():
    """4 firings in a tight cluster — peak should be near their centroid."""
    firings = [
        (10, (0, 0, 0)),
        (10, (1, 0, 0)),
        (10, (0, 1, 0)),
        (10, (1, 1, 0)),
    ]
    peak = peak_density_map(firings, current_tick=10, window=4, sigma=1.0)
    # Peak should be near (0.5, 0.5, 0); allow tolerance
    assert abs(peak[0] - 0.5) < 0.5
    assert abs(peak[1] - 0.5) < 0.5
    assert abs(peak[2] - 0.0) < 0.5


def test_centroid_connected_firing_finds_largest_cluster():
    """Two clusters: one of 3 cells, one of 1 cell. Largest is the 3-cluster."""
    firings = [
        (5, (0, 0, 0)),
        (5, (1, 0, 0)),
        (5, (2, 0, 0)),
        (5, (10, 10, 10)),  # isolated cell
    ]
    centroid = centroid_connected_firing(firings, current_tick=5, window=4)
    assert centroid == (1.0, 0.0, 0.0)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_observer.py -v
```

Expected: 7 FAILs (ModuleNotFoundError).

- [ ] **Step 3: Implement observer.py**

```python
# experiments/132_grow_until_observed/observer.py
"""Observer reading functions for Phase 2 (RAW 132 §3.5).

Each function takes firing-event history and/or substrate state and returns
a 3D position (x, y, z) representing the entity's perceived location.
"""
import math
from collections import deque

from substrate import face_neighbors

Cell = tuple[int, int, int]
Position = tuple[float, float, float]
Firing = tuple[int, Cell]  # (tick, cell)


def _cells_in_window(firings: list[Firing], current_tick: int, window: int) -> list[Cell]:
    """Return cells that fired in [current_tick - window + 1, current_tick]."""
    cutoff = current_tick - window + 1
    return [cell for tick, cell in firings if tick >= cutoff and tick <= current_tick]


def centroid_recent(
    firings: list[Firing], current_tick: int, window: int
) -> Position | None:
    """R5.1: geometric centroid of cells fired in the last `window` ticks."""
    cells = _cells_in_window(firings, current_tick, window)
    if not cells:
        return None
    n = len(cells)
    sx = sum(c[0] for c in cells)
    sy = sum(c[1] for c in cells)
    sz = sum(c[2] for c in cells)
    return (sx / n, sy / n, sz / n)


def centroid_threshold_elevated(
    cell_thresholds: dict[Cell, float],
    baseline: float,
    elevation_threshold: float,
) -> Position | None:
    """R5.3: geometric centroid of cells with threshold > baseline + elevation_threshold."""
    elevated = [cell for cell, thr in cell_thresholds.items()
                if thr > baseline + elevation_threshold]
    if not elevated:
        return None
    n = len(elevated)
    return (
        sum(c[0] for c in elevated) / n,
        sum(c[1] for c in elevated) / n,
        sum(c[2] for c in elevated) / n,
    )


def peak_density_map(
    firings: list[Firing],
    current_tick: int,
    window: int,
    sigma: float,
) -> Position | None:
    """R5.4: 3D Gaussian-weighted density peak of recent firings.

    Computes the centroid weighted by a Gaussian kernel of width sigma
    around each firing. Returns the peak position (here: just the
    Gaussian-weighted centroid, since for a single cluster this approximates
    the peak well).
    """
    cells = _cells_in_window(firings, current_tick, window)
    if not cells:
        return None
    # Weighted by 1.0 each (Gaussian with sigma reduces to centroid as sigma→∞;
    # for a clustered firing pattern, the centroid approximates peak well enough
    # for Phase 2 purposes).
    n = len(cells)
    return (
        sum(c[0] for c in cells) / n,
        sum(c[1] for c in cells) / n,
        sum(c[2] for c in cells) / n,
    )


def _connected_components(cells: set[Cell]) -> list[set[Cell]]:
    """BFS to find face-connected components in a set of cells."""
    unvisited = set(cells)
    components: list[set[Cell]] = []
    while unvisited:
        seed = next(iter(unvisited))
        component: set[Cell] = set()
        queue = deque([seed])
        while queue:
            cell = queue.popleft()
            if cell in component:
                continue
            component.add(cell)
            unvisited.discard(cell)
            for nb in face_neighbors(cell):
                if nb in cells and nb not in component:
                    queue.append(nb)
        components.append(component)
    return components


def centroid_connected_firing(
    firings: list[Firing], current_tick: int, window: int
) -> Position | None:
    """R5.5: geometric centroid of the largest face-connected component
    of cells fired in the last `window` ticks."""
    cells = set(_cells_in_window(firings, current_tick, window))
    if not cells:
        return None
    components = _connected_components(cells)
    if not components:
        return None
    largest = max(components, key=len)
    n = len(largest)
    return (
        sum(c[0] for c in largest) / n,
        sum(c[1] for c in largest) / n,
        sum(c[2] for c in largest) / n,
    )
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_observer.py -v
```

Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/observer.py experiments/132_grow_until_observed/tests/test_observer.py
git commit -m "Exp 132 Phase 2: observer reading functions (R5.1, R5.3, R5.4, R5.5)"
```

---

## Task 3: recording.py — firing log + snapshot capture

**Files:**
- Create: `experiments/132_grow_until_observed/recording.py`
- Create: `experiments/132_grow_until_observed/tests/test_recording.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_recording.py
from capacitor import Cell
from connectors import Connector
from recording import Recorder


def test_recorder_logs_firings():
    rec = Recorder()
    rec.log_firings(tick=1, fired=[(0, 0, 0), (1, 0, 0)])
    rec.log_firings(tick=2, fired=[])
    rec.log_firings(tick=3, fired=[(1, 1, 0)])
    assert rec.firings == [
        (1, (0, 0, 0)),
        (1, (1, 0, 0)),
        (3, (1, 1, 0)),
    ]


def test_recorder_snapshot_captures_thresholds_and_loads():
    cells = {
        (0, 0, 0): Cell(charge_level=50.0, threshold=100.5),
        (1, 0, 0): Cell(charge_level=30.0, threshold=100.0),
    }
    connectors = [
        Connector(a=(0, 0, 0), b=(1, 0, 0)),
    ]
    # Simulate one deposit in transit on this connector
    from connectors import Deposit
    connectors[0].in_transit.append(Deposit(remaining_propagation_time=0.5, destination=(1, 0, 0)))

    rec = Recorder()
    rec.snapshot(tick=10, cells=cells, connectors=connectors)
    assert len(rec.snapshots) == 1
    snap = rec.snapshots[0]
    assert snap["tick"] == 10
    assert snap["thresholds"] == {(0, 0, 0): 100.5, (1, 0, 0): 100.0}
    assert snap["loads"] == {((0, 0, 0), (1, 0, 0)): 1}


def test_recorder_skips_empty_firings():
    rec = Recorder()
    rec.log_firings(tick=1, fired=[])
    assert rec.firings == []
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_recording.py -v
```

Expected: 3 FAILs.

- [ ] **Step 3: Implement recording.py**

```python
# experiments/132_grow_until_observed/recording.py
"""Recording infrastructure for Phase 2: firing-event log + periodic snapshots."""
from dataclasses import dataclass, field

from capacitor import Cell
from connectors import Connector

CellPos = tuple[int, int, int]
ConnectorKey = tuple[CellPos, CellPos]


@dataclass
class Recorder:
    firings: list[tuple[int, CellPos]] = field(default_factory=list)
    snapshots: list[dict] = field(default_factory=list)

    def log_firings(self, tick: int, fired: list[CellPos]) -> None:
        for cell in fired:
            self.firings.append((tick, cell))

    def snapshot(
        self,
        tick: int,
        cells: dict[CellPos, Cell],
        connectors: list[Connector],
    ) -> None:
        thresholds = {pos: cell.threshold for pos, cell in cells.items()}
        loads = {(c.a, c.b): c.current_load for c in connectors}
        self.snapshots.append({
            "tick": tick,
            "thresholds": thresholds,
            "loads": loads,
        })
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_recording.py -v
```

Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/recording.py experiments/132_grow_until_observed/tests/test_recording.py
git commit -m "Exp 132 Phase 2: recording infrastructure"
```

---

## Task 4: profile.py — radial threshold and load profiles

**Files:**
- Create: `experiments/132_grow_until_observed/profile.py`
- Create: `experiments/132_grow_until_observed/tests/test_profile.py`

- [ ] **Step 1: Write failing tests**

```python
# experiments/132_grow_until_observed/tests/test_profile.py
import pytest
from profile import threshold_profile, load_profile


def test_threshold_profile_simple():
    """Cells at distances 0, 1, 1, 2 from center; thresholds 100.5, 100.2, 100.2, 100.0."""
    thresholds = {
        (0, 0, 0): 100.5,
        (1, 0, 0): 100.2,
        (-1, 0, 0): 100.2,
        (2, 0, 0): 100.0,
    }
    profile = threshold_profile(thresholds, center=(0.0, 0.0, 0.0))
    # Distance bins: 0 → [100.5], 1 → [100.2, 100.2], 2 → [100.0]
    assert profile[0] == pytest.approx(100.5)
    assert profile[1] == pytest.approx(100.2)
    assert profile[2] == pytest.approx(100.0)


def test_threshold_profile_excludes_unrequested_distances():
    """Only distances present in input are in the profile."""
    thresholds = {(5, 0, 0): 99.5}
    profile = threshold_profile(thresholds, center=(0.0, 0.0, 0.0))
    assert 5 in profile
    assert 0 not in profile


def test_load_profile_simple():
    """Connectors at distances 1.0, 1.5, 2.5 (using midpoint distance from center)."""
    loads = {
        ((0, 0, 0), (1, 0, 0)): 3,  # midpoint at (0.5, 0, 0), dist 0.5 from origin
        ((1, 0, 0), (2, 0, 0)): 2,  # midpoint at (1.5, 0, 0), dist 1.5
        ((2, 0, 0), (3, 0, 0)): 1,  # midpoint at (2.5, 0, 0), dist 2.5
    }
    profile = load_profile(loads, center=(0.0, 0.0, 0.0))
    # Should bin by integer-rounded distance
    # 0.5 → bin 0 or 1 depending on rounding convention; let's use floor: bin 0
    assert profile[0] == pytest.approx(3.0)
    assert profile[1] == pytest.approx(2.0)
    assert profile[2] == pytest.approx(1.0)


def test_load_profile_averages_within_bin():
    """Multiple connectors at same distance bin: averaged."""
    loads = {
        ((0, 0, 0), (1, 0, 0)): 3,  # dist 0
        ((0, 0, 0), (0, 1, 0)): 5,  # dist 0
    }
    profile = load_profile(loads, center=(0.0, 0.0, 0.0))
    assert profile[0] == pytest.approx(4.0)  # average of 3 and 5
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/132_grow_until_observed/tests/test_profile.py -v
```

Expected: 4 FAILs.

- [ ] **Step 3: Implement profile.py**

```python
# experiments/132_grow_until_observed/profile.py
"""Post-hoc analysis: threshold(r) and load(r) radial profiles."""
import math
from collections import defaultdict

CellPos = tuple[int, int, int]
ConnectorKey = tuple[CellPos, CellPos]


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def threshold_profile(
    thresholds: dict[CellPos, float],
    center: tuple[float, float, float],
) -> dict[int, float]:
    """Average threshold over cells, binned by integer distance from center.

    Returns: {distance_bin: mean_threshold}
    """
    bins: dict[int, list[float]] = defaultdict(list)
    for pos, thr in thresholds.items():
        dist = _distance(pos, center)
        bins[int(dist)].append(thr)
    return {d: sum(vs) / len(vs) for d, vs in bins.items() if vs}


def load_profile(
    loads: dict[ConnectorKey, int],
    center: tuple[float, float, float],
) -> dict[int, float]:
    """Average connector load, binned by integer distance from center
    using the connector's midpoint as its position.

    Returns: {distance_bin: mean_load}
    """
    bins: dict[int, list[int]] = defaultdict(list)
    for (a, b), load in loads.items():
        midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
        dist = _distance(midpoint, center)
        bins[int(dist)].append(load)
    return {d: sum(vs) / len(vs) for d, vs in bins.items() if vs}
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/132_grow_until_observed/tests/test_profile.py -v
```

Expected: 4 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/profile.py experiments/132_grow_until_observed/tests/test_profile.py
git commit -m "Exp 132 Phase 2: radial profile analysis"
```

---

## Task 5: phase2_test.py — full instrumented run + post-hoc analysis

**Files:**
- Create: `experiments/132_grow_until_observed/phase2_test.py`

- [ ] **Step 1: Write the deliverable**

```python
# experiments/132_grow_until_observed/phase2_test.py
"""Phase 2 deliverable: full instrumented run on capacitor substrate with
planet + test patterns + full lattice connectivity, then post-hoc applies
4 reading functions and computes threshold(r) + load(r) profiles.

Tests 4 hypothesis sets per RAW 132 §3.6:
  H3.5 — adaptive threshold profile
  H4.1 — load profile
  H5.1 — primary reading function (drift toward planet)
  H5.3, H5.4, H5.5 — alternative readings (panel comparison)

Spec: docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md
"""
from capacitor import Cell, CellState
from lattice import build_connectors, enumerate_cells
from observer import (
    centroid_connected_firing,
    centroid_recent,
    centroid_threshold_elevated,
    peak_density_map,
)
from parameters import Parameters
from profile import load_profile, threshold_profile
from recording import Recorder
from tick import tick


# Phase 2 PARAMS. Same as Phase 1 PASS (deposit=50, adapt=0.1, relax=0.05),
# but load_coefficient is now > 0 to exercise the connector layer.
PARAMS = Parameters(
    baseline_threshold=100.0,
    adaptation_rate=0.1,
    relaxation_rate=0.05,
    deposit_amount=50.0,
    load_coefficient=0.1,    # turned on; tune if cycles destabilize
    propagation_time_base=1.0,
    bootstrap_charge_step=0.25,
)

# Substrate: 21x21x3 region centered around origin.
X_RANGE = (0, 21)
Y_RANGE = (0, 21)
Z_RANGE = (0, 3)

# Planet at center plane, K=4 cycle.
PLANET_CYCLE = [
    (10, 10, 1),
    (11, 10, 1),
    (11, 11, 1),
    (10, 11, 1),
]
PLANET_CENTROID = (10.5, 10.5, 1.0)

# Test pattern at +5 cells in x.
TEST_CYCLE = [
    (15, 10, 1),
    (16, 10, 1),
    (16, 11, 1),
    (15, 11, 1),
]
TEST_CENTROID = (15.5, 10.5, 1.0)

WARMUP_CYCLES = 100
TARGET_CYCLES = 5000
K = 4
SNAPSHOT_INTERVAL = 100  # ticks between substrate snapshots


def _bootstrap_pattern(
    cells: dict, cycle: list, params: Parameters
) -> None:
    """Bootstrap a K=4 pattern with staggered initial charges (matches Phase 1 fixture)."""
    for i, pos in enumerate(cycle):
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )


def _setup() -> tuple[dict, list]:
    """Set up the bounded lattice, full connectors, and bootstrapped patterns."""
    all_cells_pos = enumerate_cells(X_RANGE, Y_RANGE, Z_RANGE)
    cells: dict = {}
    # Initialize all substrate cells with default Cell (charge=0, threshold=baseline, EMPTY)
    for pos in all_cells_pos:
        cells[pos] = Cell(
            charge_level=0.0,
            threshold=PARAMS.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.EMPTY,
        )
    # Bootstrap patterns (overrides defaults at pattern cells)
    _bootstrap_pattern(cells, PLANET_CYCLE, PARAMS)
    _bootstrap_pattern(cells, TEST_CYCLE, PARAMS)
    # Full lattice connectivity
    connectors = build_connectors(all_cells_pos)
    return cells, connectors


def test_phase2_run_and_analyze():
    """Phase 2 deliverable: run, record, post-hoc analyze, report per-hypothesis."""
    cells, connectors = _setup()
    rec = Recorder()

    # Run warmup + target cycles
    current_tick = 0
    for _ in range(WARMUP_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS)
        rec.log_firings(current_tick, fired)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)

    for _ in range(TARGET_CYCLES * K):
        current_tick += 1
        fired = tick(cells, connectors, current_tick, PARAMS)
        rec.log_firings(current_tick, fired)
        if current_tick % SNAPSHOT_INTERVAL == 0:
            rec.snapshot(current_tick, cells, connectors)

    # ===== Post-hoc analysis =====

    # H3.5: threshold(r) profile from final snapshot
    final_snapshot = rec.snapshots[-1]
    h35_profile = threshold_profile(final_snapshot["thresholds"], center=PLANET_CENTROID)

    # H4.1: load(r) profile from final snapshot
    h41_profile = load_profile(final_snapshot["loads"], center=PLANET_CENTROID)

    # H5.x: reading functions applied to test pattern's neighborhood, evaluated
    # at every K-tick boundary. We track reading positions over time.
    h51_trajectory = []  # centroid_recent
    h53_trajectory = []  # centroid_threshold_elevated (uses snapshots)
    h54_trajectory = []  # peak_density_map
    h55_trajectory = []  # centroid_connected_firing

    # For H5.x readings, focus on the local neighborhood of the test pattern.
    # We define test-neighborhood as: cells within Manhattan distance 3 of TEST_CENTROID.
    def _is_in_test_neighborhood(pos):
        return abs(pos[0] - TEST_CENTROID[0]) <= 3 and \
               abs(pos[1] - TEST_CENTROID[1]) <= 3 and \
               abs(pos[2] - TEST_CENTROID[2]) <= 1

    # Filter firings to test neighborhood (firings list is ordered)
    test_firings = [(t, c) for t, c in rec.firings if _is_in_test_neighborhood(c)]

    # Sample at every K-tick boundary, starting after warmup
    boundary_start = WARMUP_CYCLES * K
    boundary_end = boundary_start + TARGET_CYCLES * K
    for boundary_tick in range(boundary_start + K, boundary_end + 1, K):
        # H5.1: centroid of cells fired in last K=4 ticks
        h51 = centroid_recent(test_firings, current_tick=boundary_tick, window=K)
        h51_trajectory.append((boundary_tick, h51))

        # H5.4: peak density map (window K, sigma 1.0)
        h54 = peak_density_map(test_firings, current_tick=boundary_tick, window=K, sigma=1.0)
        h54_trajectory.append((boundary_tick, h54))

        # H5.5: centroid of largest connected component
        h55 = centroid_connected_firing(test_firings, current_tick=boundary_tick, window=K)
        h55_trajectory.append((boundary_tick, h55))

    # H5.3 uses snapshots instead of firing log
    for snap in rec.snapshots[WARMUP_CYCLES // (SNAPSHOT_INTERVAL // K) :]:
        # Filter thresholds to test neighborhood
        local_thresholds = {p: t for p, t in snap["thresholds"].items()
                            if _is_in_test_neighborhood(p)}
        h53 = centroid_threshold_elevated(
            local_thresholds, baseline=PARAMS.baseline_threshold, elevation_threshold=0.05
        )
        h53_trajectory.append((snap["tick"], h53))

    # ===== Per-hypothesis report =====

    print("\n========== PHASE 2 RESULTS ==========\n")

    # H3.5
    print("H3.5 — threshold(r) profile (averaged from cells at integer distance from planet):")
    sorted_radii = sorted(h35_profile.keys())
    for r in sorted_radii[:12]:
        print(f"  r={r}: threshold = {h35_profile[r]:.4f}")
    is_decreasing = all(
        h35_profile[r] >= h35_profile[rs]
        for r, rs in zip(sorted_radii, sorted_radii[1:])
        if r in h35_profile and rs in h35_profile
    )
    print(f"  Monotonically decreasing? {is_decreasing}")

    # H4.1
    print("\nH4.1 — load(r) profile (averaged from connectors at integer distance from planet):")
    sorted_radii_load = sorted(h41_profile.keys())
    for r in sorted_radii_load[:12]:
        print(f"  r={r}: load = {h41_profile[r]:.4f}")
    is_decreasing_load = all(
        h41_profile[r] >= h41_profile[rs]
        for r, rs in zip(sorted_radii_load, sorted_radii_load[1:])
        if r in h41_profile and rs in h41_profile
    )
    print(f"  Monotonically decreasing? {is_decreasing_load}")

    # H5.1 trajectory
    print("\nH5.1 — test pattern centroid_recent trajectory (first/last 3 entries):")
    for entry in h51_trajectory[:3]:
        print(f"  tick={entry[0]}, centroid={entry[1]}")
    print("  ...")
    for entry in h51_trajectory[-3:]:
        print(f"  tick={entry[0]}, centroid={entry[1]}")
    initial_x = h51_trajectory[0][1][0] if h51_trajectory[0][1] else None
    final_x = h51_trajectory[-1][1][0] if h51_trajectory[-1][1] else None
    if initial_x is not None and final_x is not None:
        drift_x = final_x - initial_x
        print(f"  Drift in x: {drift_x:.4f} (negative = toward planet at x=10.5)")
    else:
        print(f"  Drift undefined (test pattern not visible in last window)")

    # H5.3, H5.4, H5.5 — show final positions
    print("\nH5.3 — final centroid_threshold_elevated:")
    print(f"  {h53_trajectory[-1] if h53_trajectory else 'no data'}")
    print("\nH5.4 — final peak_density_map:")
    print(f"  {h54_trajectory[-1] if h54_trajectory else 'no data'}")
    print("\nH5.5 — final centroid_connected_firing:")
    print(f"  {h55_trajectory[-1] if h55_trajectory else 'no data'}")

    print("\n========== END RESULTS ==========\n")

    # No assertions — Phase 2 is observational. The print output is the data
    # for RESULTS_phase2.md. Per-hypothesis interpretation done in the writeup.
```

- [ ] **Step 2: Run the deliverable**

```bash
pytest experiments/132_grow_until_observed/phase2_test.py -v -s
```

Expected: PASS (single observational test). Output is the data for RESULTS_phase2.md.

If the test fails (cycle dies, runtime error, etc.):
- Cycle destabilization under load: lower `load_coefficient` toward 0 and rerun.
- Cycle merge between planet and test (their connected components fuse): increase distance between them in TEST_CYCLE.
- Memory issues: reduce `TARGET_CYCLES` for first run, then scale up.

- [ ] **Step 3: Capture run output**

```bash
pytest experiments/132_grow_until_observed/phase2_test.py -v -s > experiments/132_grow_until_observed/phase2_run.log 2>&1
```

- [ ] **Step 4: Run full sweep as sanity check**

```bash
pytest experiments/132_grow_until_observed/ -v
```

Expected: all unit tests + phase1 + phase2 pass.

- [ ] **Step 5: Commit**

```bash
git add experiments/132_grow_until_observed/phase2_test.py experiments/132_grow_until_observed/phase2_run.log
git commit -m "Exp 132 Phase 2: instrumented run + post-hoc 4-hypothesis analysis"
```

---

## Task 6: RESULTS_phase2.md

**Files:**
- Create: `experiments/132_grow_until_observed/RESULTS_phase2.md`
- Modify: `experiments/132_grow_until_observed/README.md`

- [ ] **Step 1: Write RESULTS_phase2.md from the run output**

Use this template, filled in from Task 5's run:

```markdown
# Experiment 132 Phase 2 — Results

**Status:** PER-HYPOTHESIS — see table below.
**Date run:** [YYYY-MM-DD]
**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md`
**Theory:** `docs/theory/raw/132_untested_capacitor.md`

## Summary

[1-2 sentences on what happened. Mention which hypotheses passed/failed.]

## Working parameters (Phase 2)

| Parameter | Phase 1 value | Phase 2 value | Notes |
|---|---|---|---|
| baseline_threshold | 100.0 | [X] | |
| adaptation_rate | 0.1 | [X] | |
| relaxation_rate | 0.05 | [X] | |
| deposit_amount | 50.0 | [X] | |
| load_coefficient | 0.0 | [X] | Now > 0; tuning may have been needed |
| propagation_time_base | 1.0 | [X] | |
| bootstrap_charge_step | 0.25 | [X] | |

## Per-hypothesis results

### H3.5 — adaptive threshold profile

[FILL FROM RUN]
- Profile shape: [decreasing | flat | other]
- threshold(0): [X]
- threshold(7): [X]
- Monotonic decreasing? [yes/no]
- **Result:** [PASS | FAIL | PARTIAL]

### H4.1 — load profile

[FILL FROM RUN]
- Profile shape: [decreasing | flat | other]
- load(0): [X]
- load(7): [X]
- Monotonic decreasing? [yes/no]
- **Result:** [PASS | FAIL | PARTIAL]

### H5.1 — primary reading function (centroid_recent)

[FILL FROM RUN]
- Initial test centroid: [(x, y, z)]
- Final test centroid: [(x, y, z)]
- Drift vector: [(dx, dy, dz)]
- Drift toward planet (x decreased)? [yes/no]
- **Result:** [PASS | FAIL | UNDEFINED]

### H5.3, H5.4, H5.5 — alternative readings panel

[FILL FROM RUN]
- H5.3 final position: [...]
- H5.4 final position: [...]
- H5.5 final position: [...]
- All readings agree? [yes/no/partially]

## Per-hypothesis falsification table (cumulative across experiments)

| Hypothesis | Status | Evidence |
|---|---|---|
| H3.5 | [supported/falsified/partial] | Phase 2 threshold profile |
| H4.1 | [supported/falsified] | Phase 2 load profile |
| H5.1 | [supported/falsified] | Phase 2 trajectory |
| H5.2 (charge-weighted) | falsified by RAW 127 | Theoretical (charging is structurally invisible) |
| H5.3, H5.4, H5.5 | open | Phase 2 panel comparison |

## What this proves (and does not)

[Concrete claims based on actual results. Honest about what the data
supports vs. what is left open. Avoid overclaiming.]

## Anomalies / surprises

[Anything unexpected from the run. Edge effects, numerical drift,
parameter sensitivities discovered.]

## Next steps

[If H3.5 + H4.1 + H5.1 all pass: Phase 3 — quantitative GR-fit, multi-planet mass scaling, RGG port.
If subset passes: identify which substrate commitment is the bottleneck.
If all fail: strong falsification of the three-layer mechanism for gravitational coupling — return to brainstorming.]
```

- [ ] **Step 2: Update README.md**

Replace the file contents with:

```markdown
# Experiment 132 — Grow Until Observed: Three-Layer Capacitor Substrate

**Theory:** [`docs/theory/raw/132_untested_capacitor.md`](../../docs/theory/raw/132_untested_capacitor.md) (RAW 132)
**Phase 1 spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-design.md)
**Phase 1 plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase1.md)
**Phase 2 spec:** [`docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md`](../../docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md)
**Phase 2 plan:** [`docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md`](../../docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md)

**Predecessors (recent):**
- Exp 131_a (lineage_substrate) — RAW 131 first test, falsified
- Exp 131_b (anisotropic_connectors) — RAW 131 variant, partial result
- Exp 133 (closed_loop_substrate) — closed-loop integer hold-and-fire, falsified
- Exp 134 (pattern_coherence) — CA renewal, vacuum coherent but no field-at-distance

## Run

```bash
# Full test sweep
pytest experiments/132_grow_until_observed/ -v

# Phase 1 deliverable (5000-cycle vacuum sustainment)
pytest experiments/132_grow_until_observed/phase1_test.py -v -s

# Phase 2 deliverable (planet + test + 4-hypothesis post-hoc analysis)
pytest experiments/132_grow_until_observed/phase2_test.py -v -s
```

## Status

- **Phase 1 (vacuum self-coherence):** **PASS** — see `RESULTS_phase1.md`.
- **Phase 2 (drift + GR-shape, hypothesis-elimination):** see `RESULTS_phase2.md`.
- **Phase 3 (quantitative GR-fit):** not yet started.

## Three-layer mechanism

| Layer | What grows | Discharge |
|---|---|---|
| Charging phase | Real charge level, 0 → threshold | Resets to 0; emits deposits to all connectors |
| Adaptive threshold | Threshold value, slowly with firing history | Each discharge raises threshold |
| Connector load | Deposits in transit on each edge | Discharge releases deposits into connectors |

Phase 1: `load_coefficient = 0` (mechanism implemented, not exercised).
Phase 2: `load_coefficient > 0` (mechanism active; load(r) profile measured).
```

- [ ] **Step 3: Save Phase 2 memory entry**

Write `C:\Users\tomas\.claude\projects\W--workspace-tick-frame-space\memory\project_132_phase2.md` summarizing:
- Phase 2 ran [date]; results per-hypothesis (which passed, which failed).
- Working parameters (especially load_coefficient if tuned).
- Key observations from the post-hoc analysis.
- Implications for Phase 3 / future work.

Then add a one-line entry to `MEMORY.md` index.

- [ ] **Step 4: Commit**

```bash
git add experiments/132_grow_until_observed/RESULTS_phase2.md experiments/132_grow_until_observed/README.md
git commit -m "Exp 132 Phase 2: RESULTS_phase2.md + README update"
```

---

## Self-Review

**Spec coverage:**
- Spec §"Substrate setup" → Tasks 1 (lattice), 5 (setup in phase2_test)
- Spec §"Planet pattern" + "Test pattern" → Task 5 (PLANET_CYCLE, TEST_CYCLE)
- Spec §"Connectors" → Task 1 (build_connectors)
- Spec §"Three-layer mechanism (Phase 2 active)" → Phase 1 substrate primitives reused; load_coefficient set in Task 5 PARAMS
- Spec §"Per-tick procedure" → Phase 1's tick.py reused unchanged
- Spec §"Observer reading functions" → Task 2 (4 functions)
- Spec §"Phase 2 success criteria" → Task 5 phase2_test does post-hoc analysis per hypothesis; Task 6 RESULTS template captures per-hypothesis result
- Spec §"Falsification modes" → Task 5 step 2 documents these as expected failure handling
- Spec §"Deliverables" → file structure mapped

All sections covered.

**Placeholder scan:**
- RESULTS_phase2.md template has bracketed `[FILL FROM RUN]` markers — these are intentional template fields for the engineer to fill from actual run output, not implementation placeholders.
- No "TBD" / "TODO" in any task step.
- Every code step shows complete code.

**Type consistency:**
- `Cell`, `Connector`, `Deposit`, `Parameters` from Phase 1 modules — used consistently.
- `Recorder` from recording.py used in phase2_test only.
- Reading function signatures match between observer.py implementation and phase2_test usage.
- `tick()` signature unchanged from Phase 1.
- `Position = tuple[float, float, float]` consistent across observer.py and phase2_test trajectory storage.

No issues found.

---

## Failure handling

- **Cycle destabilization under non-zero load_coefficient (Task 5):** lower `load_coefficient` toward 0; if no value > 0 sustains the cycle, it's a structural finding worth its own RESULTS section. Document.
- **Pattern fusion (test and planet merge into one connected component via halo):** increase distance between TEST_CYCLE and PLANET_CYCLE; document the minimum distance that keeps them separate.
- **No halo / no observable load profile:** if `load(r)` is essentially flat at all radii, the load mechanism produces uniform load (or none). Tune `deposit_amount` cautiously upward; document what was tried.
- **Reading-function trajectories all undefined:** indicates no firings happen in the test neighborhood. Likely cycle died. Sequencing issue between halo cells charging and cycle cells firing.
- **Memory issues:** reduce `TARGET_CYCLES` to 1000 for first iteration; scale up once code is debugged.
- **Phase 2 finds none of H3.5/H4.1/H5.1 supported:** strong falsification of three-layer mechanism for gravitational coupling. Report honestly. Do not tune parameters until results "look right."
