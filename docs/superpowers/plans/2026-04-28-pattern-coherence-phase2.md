# Pattern Coherence Phase 2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Run the unmodified Phase 1 renewal rule on a multi-pattern substrate (connected-component-based Step B), place a test K=4 pattern face-adjacent / 1-cell-gap / 2-cell-gap from a planet K=4 pattern, capture three observables (identity, centroid, cycle invariance) per scenario over 1000 cycles, and document what actually happens at contact.

**Architecture:** Add three new modules layered on top of Phase 1's substrate/rule/fixtures. `multipattern.py` provides connected-component detection and per-component Step B with ValueError-tolerance per component. `observation.py` tracks pattern-of-origin tags and extracts the three observables. `scenarios.py` defines S1/S2/S3 placements. `phase2_test.py` runs all three scenarios, asserts S2/S3 are invariant (positive control), and records S1's full trajectory.

**Tech Stack:** Python 3, pytest, stdlib only (matches Phase 1).

**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md`

---

## File Structure

```
experiments/134_pattern_coherence/
├── ... existing Phase 1 files (unchanged) ...
├── multipattern.py       # connected_components, step_b_component, tick_multi
├── observation.py        # pattern_id tracker + observable extraction
├── scenarios.py          # S1, S2, S3 setup definitions
├── tests/
│   ├── ... existing tests/ ...
│   ├── test_multipattern.py
│   └── test_observation.py
├── phase2_test.py        # the deliverable: runs S1/S2/S3, captures observables, asserts
└── RESULTS_phase2.md     # written after run
```

**Module responsibilities:**
- `multipattern.py` knows connected-component topology and per-component Step B. Depends on `substrate.py` (face_neighbors) and `rule.py` (find_c0). Does NOT depend on observation or scenarios.
- `observation.py` knows pattern-tag bookkeeping and observable extraction. Depends only on substrate Cell type.
- `scenarios.py` is pure data — three named tuples of (planet_cycle, test_cycle, description). No logic.
- `phase2_test.py` orchestrates: bootstrap, run, capture, assert. Depends on everything.

---

## Task 1: Connected-component detection

**Files:**
- Create: `experiments/134_pattern_coherence/multipattern.py`
- Create: `experiments/134_pattern_coherence/tests/test_multipattern.py`

- [ ] **Step 1: Write failing tests for connected_components**

Create `tests/test_multipattern.py`:

```python
"""Unit tests for multipattern primitives."""

import multipattern as mp
import substrate as s


def test_empty_canvas_zero_components():
    assert mp.connected_components({}) == []


def test_single_cell_one_component():
    canvas = {(0, 0, 0): 5}
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0)}


def test_face_adjacent_cells_one_component():
    canvas = {(0, 0, 0): 5, (1, 0, 0): 3}
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0), (1, 0, 0)}


def test_diagonal_cells_two_components():
    """Diagonal cells (Manhattan distance 2) are NOT face-adjacent;
    they must be separate components."""
    canvas = {(0, 0, 0): 5, (1, 1, 0): 3}
    components = mp.connected_components(canvas)
    assert len(components) == 2


def test_F1_square_one_component():
    """Phase 1's F1 (2x2 square) — 4 cells form one connected component."""
    canvas = {
        (0, 0, 0): 4,
        (1, 0, 0): 3,
        (1, 1, 0): 2,
        (0, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)}


def test_two_separated_F1_squares_two_components():
    """Two F1 squares with 1 empty cell between them = 2 components."""
    canvas = {
        # First F1 at x=0..1
        (0, 0, 0): 4, (1, 0, 0): 3, (1, 1, 0): 2, (0, 1, 0): 1,
        # Second F1 at x=3..4 (gap of 1 empty cell at x=2)
        (3, 0, 0): 4, (4, 0, 0): 3, (4, 1, 0): 2, (3, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 2


def test_two_face_adjacent_F1_squares_one_component():
    """Two F1 squares with NO gap (face-adjacent) = 1 merged component."""
    canvas = {
        # First F1 at x=0..1
        (0, 0, 0): 4, (1, 0, 0): 3, (1, 1, 0): 2, (0, 1, 0): 1,
        # Second F1 at x=2..3 (face-adjacent: (1,0,0) <-> (2,0,0))
        (2, 0, 0): 4, (3, 0, 0): 3, (3, 1, 0): 2, (2, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert len(components[0]) == 8
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 7 FAILs with `ModuleNotFoundError` or `AttributeError`.

- [ ] **Step 3: Implement connected_components**

Create `multipattern.py`:

```python
"""Multi-pattern substrate logic: connected components and per-component Step B.

Layered on top of Phase 1's substrate.py and rule.py. Phase 1 modules are
unchanged; this module adds multi-pattern primitives that reuse them.
"""

from collections import deque

from substrate import Canvas, Cell, decay, face_neighbors


def connected_components(canvas: Canvas) -> list[set[Cell]]:
    """Partition the nonzero cells of `canvas` into face-connected components.

    Returns a list of sets, where each set is a maximal collection of cells
    such that every pair is reachable by a path of face-adjacent nonzero cells.
    """
    unvisited = set(canvas.keys())
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
            for neighbor in face_neighbors(cell):
                if neighbor in canvas and neighbor not in component:
                    queue.append(neighbor)
        components.append(component)
    return components
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/multipattern.py experiments/134_pattern_coherence/tests/test_multipattern.py
git commit -m "Exp 134 Phase 2: connected_components"
```

---

## Task 2: Per-component Step B

**Files:**
- Modify: `experiments/134_pattern_coherence/multipattern.py`
- Modify: `experiments/134_pattern_coherence/tests/test_multipattern.py`

- [ ] **Step 1: Write failing tests for step_b_component**

Append to `tests/test_multipattern.py`:

```python
import pytest


def test_step_b_component_paints_F1_successor():
    """For an isolated F1 component mid-cycle, step_b_component should paint
    the unique cycle successor — same behavior as Phase 1's step_b."""
    canvas = {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component)
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_step_b_component_negative_pattern():
    canvas = {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component)
    assert canvas == {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
        (0, 1, 0): -4,
    }


def test_step_b_component_ignores_cells_outside_component():
    """If two F1 cycles are far apart, step_b_component on one should not
    affect or read from the other."""
    canvas = {
        # Component A
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        # Component B (far away, not in `component` arg)
        (10, 10, 0): 3,
        (11, 10, 0): 2,
        (11, 11, 0): 1,
    }
    component_a = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component_a)
    # A's successor was painted
    assert canvas[(0, 1, 0)] == 4
    # B is unchanged
    assert canvas[(10, 10, 0)] == 3
    assert canvas[(11, 10, 0)] == 2
    assert canvas[(11, 11, 0)] == 1
    # B's would-be successor (10, 11, 0) was NOT painted
    assert (10, 11, 0) not in canvas


def test_step_b_component_raises_on_wedged():
    """Component with no valid c_0 raises ValueError."""
    # Two cells far apart in same "component" -- contrived setup since they
    # wouldn't normally be in one connected component, but step_b_component
    # operates on whatever set we hand it.
    canvas = {(0, 0, 0): 3, (10, 0, 0): 1}
    component = {(0, 0, 0), (10, 0, 0)}
    with pytest.raises(ValueError, match=r"(?i)wedged|no.*common"):
        mp.step_b_component(canvas, component)


def test_step_b_component_raises_on_non_uniqueness():
    """When merged 8-cell component (two F1s face-adjacent), c_max and c_min
    have multiple γ=0 face-neighbors → non-unique error."""
    # Two F1 squares face-adjacent. After one decay tick, both have a γ=0
    # cell at their cycle's "tail" position. The merged component's c_max
    # and c_min may share multiple γ=0 face-neighbors.
    canvas = {
        # Planet F1 mid-cycle (one decay applied: γ values 3, 2, 1, 0-removed)
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        # Test F1 mid-cycle, face-adjacent at x=2
        (2, 0, 0): 3,
        (3, 0, 0): 2,
        (3, 1, 0): 1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0),
                 (2, 0, 0), (3, 0, 0), (3, 1, 0)}
    # The actual outcome may be wedge OR non-unique depending on which
    # cells iter picks for c_max and c_min. Either is acceptable; what
    # matters is that step_b_component raises ValueError, not silently
    # produces wrong output.
    with pytest.raises(ValueError):
        mp.step_b_component(canvas, component)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 5 new FAILs.

- [ ] **Step 3: Implement step_b_component**

Append to `multipattern.py`:

```python
from rule import find_c0


def _find_c_max_in(canvas: Canvas, cells: set[Cell]) -> Cell:
    """Return the cell in `cells` with maximum |γ|. Raises if cells is empty."""
    if not cells:
        raise ValueError("component is empty; no max cell")
    return max(cells, key=lambda c: abs(canvas[c]))


def _find_c_min_positive_in(canvas: Canvas, cells: set[Cell]) -> Cell:
    """Return the cell in `cells` with minimum |γ| among nonzero values.
    Raises if no nonzero cells in `cells`.
    """
    nonzero = [c for c in cells if canvas.get(c, 0) != 0]
    if not nonzero:
        raise ValueError("component has no nonzero cells")
    return min(nonzero, key=lambda c: abs(canvas[c]))


def step_b_component(canvas: Canvas, component: set[Cell]) -> None:
    """Apply Step B locally to one connected component.

    Identifies c_max and c_min within the component, then finds the unique
    γ=0 face-neighbor of both (which may lie outside the component, since
    γ=0 cells are by definition not in any component) and paints it.

    Raises ValueError if c_max/c_min ambiguity produces no valid c_0 (wedge)
    or multiple valid c_0 candidates (non-uniqueness).
    """
    c_max = _find_c_max_in(canvas, component)
    c_min = _find_c_min_positive_in(canvas, component)
    c0 = find_c0(canvas, c_max, c_min)
    gamma_max = canvas[c_max]
    sign = 1 if gamma_max > 0 else -1
    canvas[c0] = sign * (abs(gamma_max) + 1)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 12 PASS (7 from Task 1 + 5 new).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 2: step_b_component"
```

---

## Task 3: tick_multi (decay + per-component Step B with failure tolerance)

**Files:**
- Modify: `experiments/134_pattern_coherence/multipattern.py`
- Modify: `experiments/134_pattern_coherence/tests/test_multipattern.py`

- [ ] **Step 1: Write failing tests for tick_multi**

Append to `tests/test_multipattern.py`:

```python
import rule as r


def test_tick_multi_isolated_F1_invariant_over_K_ticks():
    """A single isolated F1 pattern under tick_multi should be a fixed point
    after K=4 ticks, just like Phase 1."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    initial = dict(canvas)
    for _ in range(4):
        mp.tick_multi(canvas)
    assert canvas == initial


def test_tick_multi_two_separated_F1s_both_invariant():
    """Two F1 patterns separated by 1 empty cell are independent components.
    Each should remain invariant over K=4 ticks of tick_multi."""
    canvas: s.Canvas = {}
    cycle_a = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    cycle_b = [(3, 0, 0), (4, 0, 0), (4, 1, 0), (3, 1, 0)]
    r.bootstrap(canvas, cycle_a, sign=1)
    r.bootstrap(canvas, cycle_b, sign=1)
    initial = dict(canvas)
    for _ in range(4):
        mp.tick_multi(canvas)
    assert canvas == initial


def test_tick_multi_failed_component_decays_quietly():
    """A component whose step_b_component raises ValueError (e.g., wedged
    contact between two patterns) should not crash tick_multi. The
    component's cells should continue to decay over subsequent ticks
    without renewal, and eventually expire to zero. Other components
    must continue normally."""
    canvas: s.Canvas = {}
    # Healthy component (will be invariant)
    healthy = [(10, 10, 0), (11, 10, 0), (11, 11, 0), (10, 11, 0)]
    r.bootstrap(canvas, healthy, sign=1)
    # Wedged component (two face-adjacent F1s — merged ambiguous component)
    r.bootstrap(canvas, [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], sign=1)
    r.bootstrap(canvas, [(2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)], sign=1)

    # Run K ticks. Healthy component should be invariant; merged should
    # have lost cells (some / all expired without renewal).
    healthy_initial = {c: canvas[c] for c in healthy}
    for _ in range(4):
        mp.tick_multi(canvas)

    # Healthy survived
    for c in healthy:
        assert canvas.get(c) == healthy_initial[c], (
            f"healthy component cell {c} changed: was {healthy_initial[c]}, "
            f"now {canvas.get(c)}"
        )

    # At least some cells of the merged 8-cell component dissolved
    merged_cells = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                    (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)]
    n_alive = sum(1 for c in merged_cells if c in canvas)
    assert n_alive < 8, "expected some merged-component cells to dissolve, but all 8 alive"
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 3 new FAILs.

- [ ] **Step 3: Implement tick_multi**

Append to `multipattern.py`:

```python
def tick_multi(canvas: Canvas) -> None:
    """One full substrate tick on a multi-pattern canvas:
        Step A — decay (every nonzero cell)
        Step B — for each connected component, apply step_b_component
                 with per-component failure tolerance (a wedged or
                 non-unique component's ValueError is caught; the
                 component's cells will continue to decay on subsequent
                 ticks without renewal).

    Other components are unaffected by one component's failure.
    """
    decay(canvas)
    components = connected_components(canvas)
    for component in components:
        try:
            step_b_component(canvas, component)
        except ValueError:
            # Component failed (wedged or non-unique). Its cells will
            # continue to decay without renewal on subsequent ticks. Move
            # on; do not crash tick_multi.
            continue
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_multipattern.py -v
```

Expected: 15 PASS (12 + 3 new).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 2: tick_multi with per-component fault tolerance"
```

---

## Task 4: Pattern-tag tracker

**Files:**
- Create: `experiments/134_pattern_coherence/observation.py`
- Create: `experiments/134_pattern_coherence/tests/test_observation.py`

- [ ] **Step 1: Write failing tests**

Create `tests/test_observation.py`:

```python
"""Unit tests for observation primitives."""

import observation as o
import substrate as s


def test_count_alive_tagged_all_alive():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 2, (1, 1, 0): 1, (0, 1, 0): 4}
    pattern_id = {(0, 0, 0): "test", (1, 0, 0): "test",
                  (1, 1, 0): "test", (0, 1, 0): "test"}
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 4


def test_count_alive_tagged_some_expired():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 2}
    pattern_id = {(0, 0, 0): "test", (1, 0, 0): "test",
                  (1, 1, 0): "test", (0, 1, 0): "test"}
    # (1, 1, 0) and (0, 1, 0) tagged but not in canvas (expired)
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 2


def test_count_alive_tagged_excludes_other_tags():
    canvas = {(0, 0, 0): 3, (10, 0, 0): 4}
    pattern_id = {(0, 0, 0): "test", (10, 0, 0): "planet"}
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 1
    assert o.count_alive_tagged(canvas, pattern_id, "planet") == 1


def test_centroid_alive_tagged_all_alive():
    canvas = {(0, 0, 0): 3, (2, 0, 0): 2, (2, 2, 0): 1, (0, 2, 0): 4}
    pattern_id = {(0, 0, 0): "test", (2, 0, 0): "test",
                  (2, 2, 0): "test", (0, 2, 0): "test"}
    centroid = o.centroid_alive_tagged(canvas, pattern_id, "test")
    assert centroid == (1.0, 1.0, 0.0)


def test_centroid_alive_tagged_returns_none_when_none_alive():
    canvas: s.Canvas = {}
    pattern_id = {(0, 0, 0): "test"}
    assert o.centroid_alive_tagged(canvas, pattern_id, "test") is None


def test_canvas_hash_stable_across_dict_order():
    """Hash is stable regardless of dict insertion order."""
    canvas_a = {(0, 0, 0): 3, (1, 0, 0): 2}
    canvas_b = {(1, 0, 0): 2, (0, 0, 0): 3}
    assert o.canvas_hash(canvas_a) == o.canvas_hash(canvas_b)


def test_canvas_hash_differs_when_value_differs():
    canvas_a = {(0, 0, 0): 3}
    canvas_b = {(0, 0, 0): 4}
    assert o.canvas_hash(canvas_a) != o.canvas_hash(canvas_b)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_observation.py -v
```

Expected: 7 FAILs (ModuleNotFoundError).

- [ ] **Step 3: Implement observation primitives**

Create `observation.py`:

```python
"""Pattern-of-origin tagging and observable extraction for Phase 2.

The substrate dynamics ignore tags; this module is measurement-only.
"""

import hashlib

from substrate import Canvas, Cell

PatternIdMap = dict[Cell, str]


def count_alive_tagged(canvas: Canvas, pattern_id: PatternIdMap, tag: str) -> int:
    """Count cells with the given tag that are still alive (in canvas)."""
    return sum(1 for cell, t in pattern_id.items() if t == tag and cell in canvas)


def centroid_alive_tagged(
    canvas: Canvas, pattern_id: PatternIdMap, tag: str
) -> tuple[float, float, float] | None:
    """Geometric centroid of cells with the given tag that are still alive.
    Returns None if no such cells remain."""
    alive = [cell for cell, t in pattern_id.items() if t == tag and cell in canvas]
    if not alive:
        return None
    n = len(alive)
    sx = sum(c[0] for c in alive)
    sy = sum(c[1] for c in alive)
    sz = sum(c[2] for c in alive)
    return (sx / n, sy / n, sz / n)


def canvas_hash(canvas: Canvas) -> str:
    """Stable SHA-256 hash of canvas state, dict-order-independent."""
    items = sorted(canvas.items())
    return hashlib.sha256(repr(items).encode()).hexdigest()
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_observation.py -v
```

Expected: 7 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/observation.py experiments/134_pattern_coherence/tests/test_observation.py
git commit -m "Exp 134 Phase 2: observation primitives (tag tracker, centroid, hash)"
```

---

## Task 5: Scenarios definition

**Files:**
- Create: `experiments/134_pattern_coherence/scenarios.py`

- [ ] **Step 1: Define the three scenarios**

Create `scenarios.py`:

```python
"""Phase 2 test scenarios: planet + test pattern placements.

Each scenario is a dict with planet_cycle, test_cycle, and a description.
The cycles are lists of (x, y, z) cells in cycle order, ready for
rule.bootstrap().
"""

# Planet is the same in all scenarios: F1 (2x2 square at origin).
PLANET_CYCLE = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]


SCENARIOS = {
    "S1_face_adjacent": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)],
        "description": (
            "Test pattern's (2,0,0) is face-adjacent to planet's (1,0,0). "
            "Planet and test fuse into one 8-cell connected component at "
            "bootstrap. Predicted: contact-ambiguity dissolution."
        ),
    },
    "S2_one_cell_gap": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(3, 0, 0), (4, 0, 0), (4, 1, 0), (3, 1, 0)],
        "description": (
            "1-cell empty gap at (2,0,0) between nearest cells. Patterns are "
            "separate connected components. Positive control for substrate "
            "locality. Predicted: both invariant for 1000 cycles."
        ),
    },
    "S3_two_cell_gap": {
        "planet_cycle": PLANET_CYCLE,
        "test_cycle": [(4, 0, 0), (5, 0, 0), (5, 1, 0), (4, 1, 0)],
        "description": (
            "2-cell empty gap. Same predicted behavior as S2; runs as a "
            "second positive control."
        ),
    },
}
```

- [ ] **Step 2: Verify scenarios import cleanly**

```bash
python -c "
import sys, os
sys.path.insert(0, 'experiments/134_pattern_coherence')
import scenarios
for name, s in scenarios.SCENARIOS.items():
    print(name, len(s['test_cycle']), s['description'][:60])
"
```

Expected: 3 lines printed, no errors.

- [ ] **Step 3: Commit**

```bash
git add experiments/134_pattern_coherence/scenarios.py
git commit -m "Exp 134 Phase 2: scenario definitions S1/S2/S3"
```

---

## Task 6: Phase 2 deliverable test (the experiment itself)

**Files:**
- Create: `experiments/134_pattern_coherence/phase2_test.py`

- [ ] **Step 1: Write the Phase 2 deliverable**

Create `phase2_test.py`:

```python
"""Phase 2 deliverable: contact physics on multi-pattern substrate.

Runs each scenario (S1, S2, S3), captures three observables (identity,
centroid, cycle invariance) over 1000 cycles, asserts on positive controls
(S2, S3 must be invariant), and records S1's full trajectory.

Spec: docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md
"""

import multipattern as mp
import observation as o
import rule as r
import scenarios as sc
import substrate as s

K = 4
N_CYCLES = 1000


def _setup(planet_cycle, test_cycle):
    """Bootstrap planet and test patterns; return (canvas, pattern_id)."""
    canvas: s.Canvas = {}
    pattern_id: o.PatternIdMap = {}
    r.bootstrap(canvas, planet_cycle, sign=1)
    for cell in planet_cycle:
        pattern_id[cell] = "planet"
    r.bootstrap(canvas, test_cycle, sign=1)
    for cell in test_cycle:
        pattern_id[cell] = "test"
    return canvas, pattern_id


def _run_scenario(name: str) -> dict:
    """Run a scenario for N_CYCLES cycles, capturing all three observables."""
    sc_def = sc.SCENARIOS[name]
    canvas, pattern_id = _setup(sc_def["planet_cycle"], sc_def["test_cycle"])

    initial_centroid = o.centroid_alive_tagged(canvas, pattern_id, "test")
    cycle_hashes: list[str] = []
    identity_trajectory: list[tuple[int, int]] = []
    centroid_trajectory: list[tuple[int, tuple[float, float, float] | None]] = []

    for cycle_n in range(1, N_CYCLES + 1):
        for _ in range(K):
            mp.tick_multi(canvas)
        cycle_hashes.append(o.canvas_hash(canvas))
        identity_trajectory.append(
            (cycle_n, o.count_alive_tagged(canvas, pattern_id, "test"))
        )
        centroid_trajectory.append(
            (cycle_n, o.centroid_alive_tagged(canvas, pattern_id, "test"))
        )

    reference_hash = cycle_hashes[0]
    first_break = None
    for i, h in enumerate(cycle_hashes, start=1):
        if h != reference_hash:
            first_break = i
            break

    final_n_alive = identity_trajectory[-1][1]
    final_centroid = centroid_trajectory[-1][1]
    drift = None
    if final_centroid is not None and initial_centroid is not None:
        drift = tuple(final_centroid[i] - initial_centroid[i] for i in range(3))

    return {
        "name": name,
        "description": sc_def["description"],
        "n_cycles_run": N_CYCLES,
        "reference_hash": reference_hash,
        "first_break": first_break,
        "initial_centroid": initial_centroid,
        "final_centroid": final_centroid,
        "drift_vector": drift,
        "final_n_test_alive": final_n_alive,
        "identity_trajectory": identity_trajectory,
        "centroid_trajectory": centroid_trajectory,
    }


def test_S1_face_adjacent_records_contact_event():
    """S1: face-adjacent patterns. We do not predict the exact outcome,
    we record it. The test passes by virtue of completing the run; the
    output (printed for the record) is what RESULTS_phase2.md captures."""
    result = _run_scenario("S1_face_adjacent")
    print(f"\nS1 final n_test_alive: {result['final_n_test_alive']}")
    print(f"S1 first_break: {result['first_break']}")
    print(f"S1 initial centroid: {result['initial_centroid']}")
    print(f"S1 final centroid: {result['final_centroid']}")
    print(f"S1 drift vector: {result['drift_vector']}")
    print(f"S1 identity (first 10 cycles): {result['identity_trajectory'][:10]}")
    print(f"S1 reference hash: {result['reference_hash']}")
    # No assertions — S1 is observational. The print output is the record.


def test_S2_one_cell_gap_is_invariant():
    """S2: 1-cell gap. Positive control. Predicted: invariant for all 1000 cycles,
    centroid stationary, all 4 test cells alive throughout."""
    result = _run_scenario("S2_one_cell_gap")
    print(f"\nS2 reference hash: {result['reference_hash']}")

    assert result["first_break"] is None, (
        f"S2 (positive control) violated invariance at cycle {result['first_break']}: "
        f"the rule has unexpected coupling across a 1-cell gap"
    )
    assert result["final_n_test_alive"] == 4, (
        f"S2 lost {4 - result['final_n_test_alive']} test cells; expected all 4 alive"
    )
    assert result["drift_vector"] == (0.0, 0.0, 0.0), (
        f"S2 centroid drifted by {result['drift_vector']}; expected stationary"
    )


def test_S3_two_cell_gap_is_invariant():
    """S3: 2-cell gap. Second positive control. Same predictions as S2."""
    result = _run_scenario("S3_two_cell_gap")
    print(f"\nS3 reference hash: {result['reference_hash']}")

    assert result["first_break"] is None, (
        f"S3 violated invariance at cycle {result['first_break']}"
    )
    assert result["final_n_test_alive"] == 4
    assert result["drift_vector"] == (0.0, 0.0, 0.0)
```

- [ ] **Step 2: Run the deliverable**

```bash
pytest experiments/134_pattern_coherence/phase2_test.py -v -s
```

Expected — run completes; S2 and S3 PASS as positive controls; S1 PASSES (it's observational, no assertions). The `-s` output captures S1's identity trajectory, centroid drift, and final state for RESULTS_phase2.md.

If S2 or S3 FAIL: the rule has unexpected coupling. Stop, investigate. Do not paper over.

- [ ] **Step 3: Capture run output**

```bash
pytest experiments/134_pattern_coherence/phase2_test.py -v -s > experiments/134_pattern_coherence/phase2_run.log 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add experiments/134_pattern_coherence/phase2_test.py
git commit -m "Exp 134 Phase 2: deliverable test (S1/S2/S3 with all 3 observables)"
```

---

## Task 7: Run all tests as sanity sweep

- [ ] **Step 1: Run the full test suite**

```bash
pytest experiments/134_pattern_coherence/ -v
```

Expected: all tests pass (Phase 1 unit tests + Phase 1 deliverable + Phase 2 unit tests + Phase 2 deliverable).

If anything fails that wasn't expected, stop and investigate before writing RESULTS.

---

## Task 8: RESULTS_phase2.md write-up

**Files:**
- Create: `experiments/134_pattern_coherence/RESULTS_phase2.md`

- [ ] **Step 1: Write RESULTS_phase2.md from the run output**

Use this template, filled in from the actual run:

```markdown
# Experiment 134 Phase 2 — Results

**Status:** [PASS — predicted decoherence confirmed | UNEXPECTED — describe what happened | FAIL — positive control failed]
**Date run:** [YYYY-MM-DD]
**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-pattern-coherence-phase2.md`
**Phase 1 result:** PASSED 2026-04-28 (see RESULTS.md)

## Summary

[1-2 sentences on what happened.]

## Per-scenario observations

### S1: face-adjacent (contact event)

- First break (canvas hash changed at cycle): [n]
- Initial centroid of test pattern: [(x, y, z)]
- Final centroid: [(x, y, z) or None]
- Drift vector: [(dx, dy, dz) or N/A]
- Final n_test_alive: [count of test cells still alive at cycle 1000]
- Identity trajectory (first 10 cycles): [list]
- Reference hash: [hash from run]

[Narrative description of what happened — did patterns dissolve? Did
test pattern slide? Did one side dominate the other in the
ambiguous lookup?]

### S2: 1-cell gap (positive control)

- First break: [None expected | actual]
- Final n_test_alive: [4 expected]
- Drift vector: [(0, 0, 0) expected]
- Reference hash: [hash]

[PASS / FAIL note. If failed, this is an unexpected-coupling result — diagnose.]

### S3: 2-cell gap (positive control)

[Same fields as S2.]

## What this proves (or falsifies)

[Concrete claims. E.g.:
- "Gravity-at-a-distance is unearnable in this substrate ontology" — confirmed by S2/S3 invariance.
- "Same-sign contact produces mutual decoherence" — confirmed/falsified by S1 outcome.
- "The rule has emergent X behavior" — if S1 produced something unexpected.]

## Next steps

[Based on the result, where should research go from here?
- If decoherence as predicted: the substrate's contact behavior is fully characterized for same-sign. Phase 3 (opposite-sign annihilation) is the natural next step.
- If something graceful happens at S1: investigate the rule's tie-breaking; document the trajectory; consider whether Phase 2.5 (rule modification for tie-breaking) has emerged organically rather than being engineered.
- If S2/S3 fail: the substrate has unexpected coupling. Phase 2 must restart with a corrected rule.]
```

- [ ] **Step 2: Update README.md to reference Phase 2 results**

Modify `experiments/134_pattern_coherence/README.md`:

```markdown
# Experiment 134: Pattern Coherence

See:
- `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md` (Phase 1 spec)
- `docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md` (Phase 2 spec)
- `RESULTS.md` (Phase 1 outcome)
- `RESULTS_phase2.md` (Phase 2 outcome)

## Run

```bash
# Full test sweep (all phases)
pytest experiments/134_pattern_coherence/ -v

# Phase 1 deliverable
pytest experiments/134_pattern_coherence/phase1_test.py -v -s

# Phase 2 deliverable
pytest experiments/134_pattern_coherence/phase2_test.py -v -s
```

## Status

Phase 1: see `RESULTS.md`.
Phase 2: see `RESULTS_phase2.md`.
Phase 3 (opposite-sign annihilation): not yet started.
```

- [ ] **Step 3: Commit**

```bash
git add experiments/134_pattern_coherence/RESULTS_phase2.md experiments/134_pattern_coherence/README.md
git commit -m "Exp 134 Phase 2: RESULTS_phase2.md + README update"
```

---

## Self-Review

**Spec coverage:**
- Section 1 (multi-pattern rule architecture: connected components, per-component Step B, fault tolerance) → Tasks 1, 2, 3
- Section 1 (pattern_id parallel dict for measurement) → Task 4
- Section 2 (single K=4 planet, three scenarios S1/S2/S3) → Task 5
- Section 3 (three observables: identity, centroid, cycle invariance) → Tasks 4 + 6
- Section 3 (success criteria: S2/S3 invariant assertions, S1 observational) → Task 6
- Section 3 (run length 1000 cycles) → Task 6 (`N_CYCLES = 1000`)
- Section 3 (deliverables file structure) → Task layout
- Open questions on tie-breaking determinism → Captured in S1's record (no assertions, just print + RESULTS template note)

All sections covered. No gaps.

**Placeholder scan:**
- RESULTS_phase2.md template has bracketed `[fill in]` markers — these are intentional template fields for the engineer to fill from actual run output, not implementation placeholders.
- No "TBD" / "TODO" / "implement later" in any task step.
- Every code step shows complete code.

**Type consistency:**
- `Canvas`, `Cell` from substrate.py — used consistently
- `PatternIdMap = dict[Cell, str]` defined in observation.py — used consistently in phase2_test.py
- `connected_components(canvas) -> list[set[Cell]]` — `set[Cell]` used consistently in step_b_component
- `tick_multi(canvas) -> None` — used consistently
- Function names match between definition (Tasks 1, 2, 3, 4) and consumption (Task 6)

No issues found.

---

## Failure handling

- **Connected-component test failures (Task 1):** likely a BFS/iteration bug. The test cases are minimal and exhaustive; debug by tracing the algorithm on the failing case.
- **step_b_component non-uniqueness test (Task 2):** if it doesn't raise on the merged 8-cell scenario, either the geometry happens to give a unique c_0 by accident (unexpected — rare on this geometry) or `find_c0` is silently returning one without checking. Inspect the merged-component candidates manually.
- **tick_multi failed-component test (Task 3):** if the healthy component is also affected by the merged component's failure, fault-isolation in tick_multi is broken. Check the try/except scope.
- **Phase 2 deliverable S2/S3 failures (Task 6):** **DO NOT paper over.** This indicates unexpected long-range coupling — the rule isn't strictly local somehow. Stop, file a follow-up investigation, do not modify S2/S3 to make tests pass.
- **Phase 2 deliverable S1 trajectory unclear:** S1 has no assertions; its output is data. If the print output is too sparse to write RESULTS_phase2.md, add more print statements (e.g., centroid every 10 cycles) and rerun. This is a documentation issue, not a test failure.
