# Pattern Coherence Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construct a sign-blind transactional renewal rule on a 3D signed-integer substrate, exhibit three pattern fixtures (K=4, K=6, K=8) as exact fixed points under that rule, and verify bit-identity at every K-tick boundary for 10,000 cycles.

**Architecture:** Sparse dict-based 3D integer canvas (matches v18 style). Substrate carries a single signed-integer γ per cell. Two-step tick: decay (every nonzero cell `-=1` in magnitude) followed by paint (find max-|γ| cell, min-positive-|γ| cell, paint their unique γ=0 common face-neighbor). All Phase 1 fixtures are Hamiltonian cycles on the cubic lattice satisfying the geometric constraint that every cycle-distance-2 pair's common face-neighbors are themselves pattern cells.

**Tech Stack:** Python 3, pytest. No numpy, no scipy, no matplotlib for Phase 1 — sparse dict and stdlib only.

**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md`

---

## File Structure

```
experiments/134_pattern_coherence/
├── README.md                # quick run instructions
├── __init__.py              # (empty)
├── substrate.py             # Canvas type alias + decay + face_neighbors
├── rule.py                  # bootstrap + find_c_max + find_c_min_positive + find_c0 + step_b + tick
├── fixtures.py              # F1 (2x2 K=4), F2 (2x3 perimeter K=6), F3 (3x3 ring K=8) cycle definitions
├── phase1_test.py           # the Phase 1 deliverable: bit-identity over 10,000 cycles for each fixture
├── tests/
│   ├── __init__.py
│   ├── test_substrate.py    # unit tests for decay + face_neighbors
│   ├── test_rule.py         # unit tests for bootstrap + find_* + step_b + tick
│   └── test_fixtures.py     # validates Hamiltonian-cycle property and geometric constraint
└── RESULTS.md               # written at end: pass/fail + hashes + anomalies
```

**File responsibilities:**
- `substrate.py` knows about the canvas data model and per-cell decay. No concept of "pattern" or "cycle".
- `rule.py` knows how to find pattern cells by their γ values and apply Step B. No knowledge of fixture geometry.
- `fixtures.py` knows the cycle cell lists and their cycle order. No knowledge of substrate or rule internals.
- `phase1_test.py` is the deliverable — runs each fixture for 10,000 cycles and asserts bit-identity at every K-tick boundary.
- `tests/` contains unit tests written during TDD; they are supporting evidence, not the deliverable.

---

## Task 1: Project scaffolding

**Files:**
- Create: `experiments/134_pattern_coherence/__init__.py`
- Create: `experiments/134_pattern_coherence/substrate.py`
- Create: `experiments/134_pattern_coherence/rule.py`
- Create: `experiments/134_pattern_coherence/fixtures.py`
- Create: `experiments/134_pattern_coherence/phase1_test.py`
- Create: `experiments/134_pattern_coherence/tests/__init__.py`
- Create: `experiments/134_pattern_coherence/tests/test_substrate.py`
- Create: `experiments/134_pattern_coherence/tests/test_rule.py`
- Create: `experiments/134_pattern_coherence/tests/test_fixtures.py`
- Create: `experiments/134_pattern_coherence/README.md`

- [ ] **Step 1: Create `__init__.py` (both top-level and tests/)**

```python
# experiments/134_pattern_coherence/__init__.py
# experiments/134_pattern_coherence/tests/__init__.py
```

Both files empty.

- [ ] **Step 2: Create `substrate.py` skeleton**

```python
# experiments/134_pattern_coherence/substrate.py
"""Signed-integer 3D sparse canvas with symmetric decay.

The substrate is a dict mapping (x, y, z) -> int. Cells with γ = 0 are
not stored. Decay subtracts 1 from each cell's magnitude (drift toward 0).
"""

Cell = tuple[int, int, int]
Canvas = dict[Cell, int]


def decay(canvas: Canvas) -> None:
    """Apply Step A: γ -= sign(γ) for every nonzero cell. In-place.
    Cells reaching γ = 0 are removed from the dict.
    """
    raise NotImplementedError


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    raise NotImplementedError
```

- [ ] **Step 3: Create `rule.py` skeleton**

```python
# experiments/134_pattern_coherence/rule.py
"""Sign-blind transactional renewal rule (Step A + Step B + tick).

See docs/superpowers/specs/2026-04-28-pattern-coherence-design.md.
"""

from .substrate import Canvas, Cell, decay, face_neighbors


def bootstrap(canvas: Canvas, cycle: list[Cell], sign: int = 1) -> None:
    """Seed canvas with cycle cells at γ = sign * K, sign * (K-1), ..., sign * 1.

    `cycle` is the Hamiltonian cycle in cycle order. `sign` is +1 (matter)
    or -1 (antimatter).
    """
    raise NotImplementedError


def find_c_max(canvas: Canvas) -> Cell:
    """Return the cell with maximum |γ|. Raises if canvas is empty."""
    raise NotImplementedError


def find_c_min_positive(canvas: Canvas) -> Cell:
    """Return the cell with minimum |γ| among cells with γ != 0.
    Raises if canvas has no nonzero cells.
    """
    raise NotImplementedError


def find_c0(canvas: Canvas, c_max: Cell, c_min: Cell) -> Cell:
    """Return the unique γ = 0 cell that is face-adjacent to both c_max
    and c_min.

    Raises ValueError if no such cell exists (wedged) or if multiple
    such cells exist (non-uniqueness — fixture violates geometric
    constraint).
    """
    raise NotImplementedError


def step_b(canvas: Canvas) -> None:
    """Apply Step B: paint the cell c0 found by find_c0 to magnitude
    |γ[c_max]| + 1 with sign matching c_max. In-place.
    """
    raise NotImplementedError


def tick(canvas: Canvas) -> None:
    """One full substrate tick: decay (Step A) then paint (Step B). In-place."""
    raise NotImplementedError
```

- [ ] **Step 4: Create `fixtures.py` skeleton**

```python
# experiments/134_pattern_coherence/fixtures.py
"""Phase 1 pattern fixtures: Hamiltonian cycles on the cubic lattice.

Each fixture is a list of (x, y, z) cells in cycle order. Successive cells
(including last -> first) are face-adjacent on the cubic lattice. All cells
lie in the z = 0 plane for Phase 1.
"""

from .substrate import Cell

# F1, F2, F3 will be defined in Task 9.
```

- [ ] **Step 5: Create `phase1_test.py` skeleton**

```python
# experiments/134_pattern_coherence/phase1_test.py
"""Phase 1 deliverable: verify bit-identity at every K-tick boundary
for 10,000 cycles, for each fixture.

This is THE Phase 1 test. If this passes for all three fixtures, Phase 1
succeeded. If any fixture fails, Phase 1 failed and the failure mode
(drift, wedge, non-uniqueness) is informative on its own.
"""

# Tests will be written in Task 10.
```

- [ ] **Step 6: Create `tests/test_substrate.py`, `tests/test_rule.py`, `tests/test_fixtures.py` skeletons**

Each file:

```python
# experiments/134_pattern_coherence/tests/test_<name>.py
"""Unit tests for <module>."""

# Tests added during TDD tasks.
```

- [ ] **Step 7: Create `README.md`**

```markdown
# Experiment 134: Pattern Coherence (Phase 1)

See `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md` for the
full design and rationale.

## Run

From repo root:

```bash
pytest experiments/134_pattern_coherence/ -v
```

Phase 1 deliverable test:

```bash
pytest experiments/134_pattern_coherence/phase1_test.py -v
```

## Status

Phase 1 in progress. Results recorded in `RESULTS.md` after the run.
```

- [ ] **Step 8: Verify pytest discovers the package**

Run from repo root:
```bash
pytest experiments/134_pattern_coherence/ --collect-only
```

Expected: pytest reports it found the test files (no tests yet, but no import errors). If it reports import errors, fix the module structure before proceeding.

- [ ] **Step 9: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: scaffolding"
```

---

## Task 2: Substrate decay

**Files:**
- Modify: `experiments/134_pattern_coherence/substrate.py`
- Modify: `experiments/134_pattern_coherence/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for decay**

Append to `tests/test_substrate.py`:

```python
from experiments.pattern_coherence_134 import substrate as s
# Note: if module path differs (e.g., importable as
# experiments.134_pattern_coherence breaks because of leading digit),
# use the literal package path. See Step 1 fallback below.
```

**Import path note:** Python identifiers cannot start with a digit, so `experiments.134_pattern_coherence` is not importable as a normal package. Two options:
- (a) Add a `conftest.py` at `experiments/134_pattern_coherence/conftest.py` that does `sys.path.insert(0, os.path.dirname(__file__))` and import modules without the package prefix.
- (b) Test files use `import substrate as s` after pytest's rootdir discovery picks them up — pytest's default `rootdir` handling + `__init__.py` files make this work when tests are run as `pytest experiments/134_pattern_coherence/`.

**Use option (b).** Replace test imports with:

```python
# experiments/134_pattern_coherence/tests/test_substrate.py
import substrate as s


def test_decay_empty_canvas_stays_empty():
    canvas = {}
    s.decay(canvas)
    assert canvas == {}


def test_decay_positive_cell_decreases_by_1():
    canvas = {(0, 0, 0): 5}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): 4}


def test_decay_negative_cell_increases_by_1():
    canvas = {(0, 0, 0): -5}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): -4}


def test_decay_positive_one_expires_to_removed():
    canvas = {(0, 0, 0): 1}
    s.decay(canvas)
    assert canvas == {}, "γ=1 should decay to 0 and be removed from sparse dict"


def test_decay_negative_one_expires_to_removed():
    canvas = {(0, 0, 0): -1}
    s.decay(canvas)
    assert canvas == {}


def test_decay_multiple_cells_independent():
    canvas = {(0, 0, 0): 3, (1, 0, 0): -2, (2, 0, 0): 1}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): 2, (1, 0, 0): -1}
    # (2, 0, 0) decayed from 1 to 0, removed
```

Add `conftest.py` to make imports work:

```python
# experiments/134_pattern_coherence/conftest.py
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_substrate.py -v
```

Expected: 6 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement decay**

Replace the body of `decay` in `substrate.py`:

```python
def decay(canvas: Canvas) -> None:
    """Apply Step A: γ -= sign(γ) for every nonzero cell. In-place.
    Cells reaching γ = 0 are removed from the dict.
    """
    expired = []
    for cell, gamma in canvas.items():
        if gamma > 0:
            new = gamma - 1
        else:
            new = gamma + 1
        if new == 0:
            expired.append(cell)
        else:
            canvas[cell] = new
    for cell in expired:
        del canvas[cell]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_substrate.py -v
```

Expected: 6 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: substrate decay (Step A)"
```

---

## Task 3: Face-neighbors helper

**Files:**
- Modify: `experiments/134_pattern_coherence/substrate.py`
- Modify: `experiments/134_pattern_coherence/tests/test_substrate.py`

- [ ] **Step 1: Write failing tests for face_neighbors**

Append to `tests/test_substrate.py`:

```python
def test_face_neighbors_origin_returns_six_cells():
    neighbors = s.face_neighbors((0, 0, 0))
    assert len(neighbors) == 6
    assert set(neighbors) == {
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    }


def test_face_neighbors_arbitrary_cell():
    neighbors = s.face_neighbors((5, -3, 7))
    assert set(neighbors) == {
        (6, -3, 7), (4, -3, 7),
        (5, -2, 7), (5, -4, 7),
        (5, -3, 8), (5, -3, 6),
    }
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_substrate.py::test_face_neighbors_origin_returns_six_cells -v
```

Expected: FAIL with `NotImplementedError`.

- [ ] **Step 3: Implement face_neighbors**

Replace the body in `substrate.py`:

```python
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
pytest experiments/134_pattern_coherence/tests/test_substrate.py -v
```

Expected: all PASS (8 total now).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: face-neighbors helper"
```

---

## Task 4: Bootstrap

**Files:**
- Modify: `experiments/134_pattern_coherence/rule.py`
- Modify: `experiments/134_pattern_coherence/tests/test_rule.py`

- [ ] **Step 1: Write failing tests for bootstrap**

Replace contents of `tests/test_rule.py`:

```python
import pytest
import rule as r
import substrate as s


def test_bootstrap_4_cell_cycle_positive_sign():
    """Cycle [A, B, C, D] should seed γ values [4, 3, 2, 1]
    (cell at cycle position i gets γ = K - i)."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    assert canvas == {
        (0, 0, 0): 4,
        (1, 0, 0): 3,
        (1, 1, 0): 2,
        (0, 1, 0): 1,
    }


def test_bootstrap_4_cell_cycle_negative_sign():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=-1)
    assert canvas == {
        (0, 0, 0): -4,
        (1, 0, 0): -3,
        (1, 1, 0): -2,
        (0, 1, 0): -1,
    }


def test_bootstrap_6_cell_cycle():
    canvas: s.Canvas = {}
    cycle = [(i, 0, 0) for i in range(6)]
    # Linear chain — not a real Hamiltonian cycle, but the bootstrap
    # function doesn't validate cycle geometry. That's fixtures.py's job.
    r.bootstrap(canvas, cycle, sign=1)
    assert canvas == {(0, 0, 0): 6, (1, 0, 0): 5, (2, 0, 0): 4,
                      (3, 0, 0): 3, (4, 0, 0): 2, (5, 0, 0): 1}
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 3 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement bootstrap**

Replace the body of `bootstrap` in `rule.py`:

```python
def bootstrap(canvas: Canvas, cycle: list[Cell], sign: int = 1) -> None:
    """Seed canvas with cycle cells at γ = sign * K, sign * (K-1), ..., sign * 1.

    `cycle` is the Hamiltonian cycle in cycle order. `sign` is +1 (matter)
    or -1 (antimatter).
    """
    if sign not in (1, -1):
        raise ValueError(f"sign must be +1 or -1, got {sign}")
    K = len(cycle)
    for i, cell in enumerate(cycle):
        canvas[cell] = sign * (K - i)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: bootstrap helper"
```

---

## Task 5: find_c_max and find_c_min_positive

**Files:**
- Modify: `experiments/134_pattern_coherence/rule.py`
- Modify: `experiments/134_pattern_coherence/tests/test_rule.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_rule.py`:

```python
def test_find_c_max_single_positive_cell():
    canvas = {(0, 0, 0): 5}
    assert r.find_c_max(canvas) == (0, 0, 0)


def test_find_c_max_picks_largest_magnitude():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 7, (2, 0, 0): 5}
    assert r.find_c_max(canvas) == (1, 0, 0)


def test_find_c_max_negative_pattern():
    canvas = {(0, 0, 0): -3, (1, 0, 0): -7, (2, 0, 0): -5}
    assert r.find_c_max(canvas) == (1, 0, 0), "max |γ| = 7, regardless of sign"


def test_find_c_max_empty_canvas_raises():
    canvas: s.Canvas = {}
    with pytest.raises(ValueError):
        r.find_c_max(canvas)


def test_find_c_min_positive_picks_smallest_nonzero_magnitude():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 7, (2, 0, 0): 1}
    assert r.find_c_min_positive(canvas) == (2, 0, 0)


def test_find_c_min_positive_negative_pattern():
    canvas = {(0, 0, 0): -3, (1, 0, 0): -7, (2, 0, 0): -1}
    assert r.find_c_min_positive(canvas) == (2, 0, 0)


def test_find_c_min_positive_empty_canvas_raises():
    canvas: s.Canvas = {}
    with pytest.raises(ValueError):
        r.find_c_min_positive(canvas)
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 7 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement find_c_max and find_c_min_positive**

Replace bodies in `rule.py`:

```python
def find_c_max(canvas: Canvas) -> Cell:
    """Return the cell with maximum |γ|. Raises if canvas is empty."""
    if not canvas:
        raise ValueError("canvas is empty; no max cell")
    return max(canvas.keys(), key=lambda c: abs(canvas[c]))


def find_c_min_positive(canvas: Canvas) -> Cell:
    """Return the cell with minimum |γ| among cells with γ != 0.
    Raises if canvas has no nonzero cells.
    """
    nonzero = [c for c in canvas if canvas[c] != 0]
    if not nonzero:
        raise ValueError("canvas has no nonzero cells")
    return min(nonzero, key=lambda c: abs(canvas[c]))
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: all PASS (10 total).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: find_c_max + find_c_min_positive"
```

---

## Task 6: find_c0

**Files:**
- Modify: `experiments/134_pattern_coherence/rule.py`
- Modify: `experiments/134_pattern_coherence/tests/test_rule.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_rule.py`:

```python
def test_find_c0_returns_unique_zero_neighbor_of_both():
    """Setup mimics F1 (2x2 square) state after Step A at tick 5:
    C0=(0,0,0)=3, C1=(1,0,0)=2, C2=(1,1,0)=1, C3=(0,1,0)=γ=0 (just expired).
    c_max = C0, c_min = C2. find_c0 should return C3.
    """
    canvas = {
        (0, 0, 0): 3,   # C0 = c_max
        (1, 0, 0): 2,   # C1
        (1, 1, 0): 1,   # C2 = c_min
        # (0, 1, 0): just expired, γ=0, NOT in dict
    }
    c_max = (0, 0, 0)
    c_min = (1, 1, 0)
    assert r.find_c0(canvas, c_max, c_min) == (0, 1, 0)


def test_find_c0_wedged_state_raises():
    """If no γ=0 cell is face-adjacent to both c_max and c_min, raise."""
    # Place c_max and c_min far apart so they have no common face-neighbor.
    canvas = {(0, 0, 0): 3, (10, 0, 0): 1}
    with pytest.raises(ValueError, match=r"(?i)wedged|no.*common"):
        r.find_c0(canvas, (0, 0, 0), (10, 0, 0))


def test_find_c0_non_uniqueness_raises():
    """If multiple γ=0 cells are face-adjacent to both c_max and c_min,
    raise — fixture violates the geometric constraint."""
    # c_max and c_min 2 apart in x with no other pattern cells between
    # them; (1, 0, 0), (1, 0, 1), (1, 0, -1) are all common face-neighbors
    # at γ=0.
    canvas = {(0, 0, 0): 3, (2, 0, 0): 1}
    with pytest.raises(ValueError, match=r"(?i)multiple|non-unique|ambiguous"):
        r.find_c0(canvas, (0, 0, 0), (2, 0, 0))
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 3 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement find_c0**

Replace the body in `rule.py`:

```python
def find_c0(canvas: Canvas, c_max: Cell, c_min: Cell) -> Cell:
    """Return the unique γ = 0 cell that is face-adjacent to both c_max
    and c_min.

    Raises ValueError if no such cell exists (wedged) or if multiple
    such cells exist (non-uniqueness — fixture violates geometric
    constraint).
    """
    max_neighbors = set(face_neighbors(c_max))
    min_neighbors = set(face_neighbors(c_min))
    common = max_neighbors & min_neighbors
    candidates = [c for c in common if canvas.get(c, 0) == 0]
    if len(candidates) == 0:
        raise ValueError(
            f"wedged state: no γ=0 cell face-adjacent to both "
            f"c_max={c_max} and c_min={c_min}"
        )
    if len(candidates) > 1:
        raise ValueError(
            f"non-unique c0 (multiple candidates {candidates}): "
            f"fixture violates the geometric constraint that "
            f"cycle-distance-2 pairs have all common face-neighbors "
            f"as pattern cells"
        )
    return candidates[0]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: all PASS (13 total).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: find_c0 paint-target"
```

---

## Task 7: step_b (paint)

**Files:**
- Modify: `experiments/134_pattern_coherence/rule.py`
- Modify: `experiments/134_pattern_coherence/tests/test_rule.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_rule.py`:

```python
def test_step_b_paints_with_correct_magnitude_and_sign_positive():
    """F1 mid-cycle state (after Step A): paint should land on the
    expired cell (0,1,0) at γ = 4 (= |γ[c_max]| + 1)."""
    canvas = {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
    }
    r.step_b(canvas)
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_step_b_paints_with_correct_sign_negative():
    canvas = {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
    }
    r.step_b(canvas)
    assert canvas == {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
        (0, 1, 0): -4,
    }
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 2 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement step_b**

Replace the body in `rule.py`:

```python
def step_b(canvas: Canvas) -> None:
    """Apply Step B: paint the cell c0 found by find_c0 to magnitude
    |γ[c_max]| + 1 with sign matching c_max. In-place.
    """
    c_max = find_c_max(canvas)
    c_min = find_c_min_positive(canvas)
    c0 = find_c0(canvas, c_max, c_min)
    gamma_max = canvas[c_max]
    sign = 1 if gamma_max > 0 else -1
    canvas[c0] = sign * (abs(gamma_max) + 1)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: all PASS (15 total).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: step_b paint operation"
```

---

## Task 8: tick (Step A + Step B)

**Files:**
- Modify: `experiments/134_pattern_coherence/rule.py`
- Modify: `experiments/134_pattern_coherence/tests/test_rule.py`

- [ ] **Step 1: Write failing tests**

Append to `tests/test_rule.py`:

```python
def test_tick_one_step_on_F1_bootstrap():
    """Bootstrap F1, then one tick. Expected: each cell decayed by 1,
    and the just-expired cell (0,1,0) repainted to γ=4."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    # After bootstrap: {(0,0,0):4, (1,0,0):3, (1,1,0):2, (0,1,0):1}

    r.tick(canvas)
    # After Step A: {(0,0,0):3, (1,0,0):2, (1,1,0):1}  (0,1,0 expired)
    # After Step B: paint (0,1,0) at γ=4
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_tick_period_K_returns_to_bootstrap_state():
    """After K ticks of F1 (K=4), canvas state should equal the
    state right after bootstrap. This is the fixed-point property."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    initial_state = dict(canvas)

    K = 4
    for _ in range(K):
        r.tick(canvas)

    assert canvas == initial_state, (
        f"After K={K} ticks, expected fixed-point return to "
        f"{initial_state}, got {canvas}"
    )


def test_tick_period_K_negative_pattern():
    """Same as above, antimatter."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=-1)
    initial_state = dict(canvas)

    K = 4
    for _ in range(K):
        r.tick(canvas)

    assert canvas == initial_state
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: 3 FAILs with `NotImplementedError`.

- [ ] **Step 3: Implement tick**

Replace the body in `rule.py`:

```python
def tick(canvas: Canvas) -> None:
    """One full substrate tick: decay (Step A) then paint (Step B). In-place."""
    decay(canvas)
    step_b(canvas)
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_rule.py -v
```

Expected: all PASS (18 total).

- [ ] **Step 5: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: tick combining Step A + Step B"
```

---

## Task 9: Fixtures F1, F2, F3

**Files:**
- Modify: `experiments/134_pattern_coherence/fixtures.py`
- Modify: `experiments/134_pattern_coherence/tests/test_fixtures.py`

- [ ] **Step 1: Write failing tests for fixture validity**

Replace contents of `tests/test_fixtures.py`:

```python
import fixtures as f
from substrate import face_neighbors


def _is_face_adjacent(a, b):
    return tuple(b) in set(face_neighbors(a))


def _is_valid_hamiltonian_cycle(cycle):
    """All consecutive pairs (including last->first) face-adjacent.
    All cells distinct."""
    if len(cycle) != len(set(cycle)):
        return False, "duplicate cells"
    for i in range(len(cycle)):
        a = cycle[i]
        b = cycle[(i + 1) % len(cycle)]
        if not _is_face_adjacent(a, b):
            return False, f"cells {a} and {b} not face-adjacent"
    return True, None


def _satisfies_geometric_constraint(cycle):
    """For every pair of cycle-distance-2 cells, all common
    face-neighbors on the lattice must be pattern cells."""
    K = len(cycle)
    pattern_set = set(cycle)
    for i in range(K):
        x = cycle[i]
        y = cycle[(i + 2) % K]  # cycle-distance-2 pair (forward)
        x_neighbors = set(face_neighbors(x))
        y_neighbors = set(face_neighbors(y))
        common = x_neighbors & y_neighbors
        for c in common:
            if c not in pattern_set:
                return False, (
                    f"cycle-distance-2 pair ({x}, {y}) has common "
                    f"face-neighbor {c} that is not a pattern cell"
                )
    return True, None


def test_F1_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F1_K4_SQUARE)
    assert ok, msg


def test_F1_has_K_4():
    assert len(f.F1_K4_SQUARE) == 4


def test_F1_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F1_K4_SQUARE)
    assert ok, msg


def test_F2_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F2_K6_PERIMETER)
    assert ok, msg


def test_F2_has_K_6():
    assert len(f.F2_K6_PERIMETER) == 6


def test_F2_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F2_K6_PERIMETER)
    assert ok, msg


def test_F3_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F3_K8_RING)
    assert ok, msg


def test_F3_has_K_8():
    assert len(f.F3_K8_RING) == 8


def test_F3_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F3_K8_RING)
    assert ok, msg
```

- [ ] **Step 2: Run tests to verify they fail**

```bash
pytest experiments/134_pattern_coherence/tests/test_fixtures.py -v
```

Expected: 9 FAILs with `AttributeError` (fixtures not yet defined).

- [ ] **Step 3: Define fixtures**

Replace contents of `fixtures.py`:

```python
"""Phase 1 pattern fixtures: Hamiltonian cycles on the cubic lattice.

Each fixture is a list of (x, y, z) cells in cycle order. Successive cells
(including last -> first) are face-adjacent on the cubic lattice. All cells
lie in the z = 0 plane for Phase 1.

Geometric constraint (validated in tests/test_fixtures.py): every pair of
cells at cycle-distance 2 has all lattice common face-neighbors that are
themselves pattern cells. This is required for the renewal rule's
uniqueness in Step B.
"""

from substrate import Cell


# F1: 2x2 square in z=0 plane, K=4. Smallest non-degenerate fixture.
F1_K4_SQUARE: list[Cell] = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
]


# F2: 2x3 rectangle perimeter in z=0 plane, K=6. Has an internal lattice
# adjacency (1,0,0)<->(1,1,0) that is NOT a cycle adjacency — tests
# robustness of the rule to non-cycle pattern adjacencies.
F2_K6_PERIMETER: list[Cell] = [
    (0, 0, 0),
    (1, 0, 0),
    (2, 0, 0),
    (2, 1, 0),
    (1, 1, 0),
    (0, 1, 0),
]


# F3: 3x3 hollow ring (perimeter of 3x3 grid, interior (1,1,0) excluded),
# K=8. All pattern adjacencies are cycle adjacencies (no internal bridges).
F3_K8_RING: list[Cell] = [
    (0, 0, 0),
    (1, 0, 0),
    (2, 0, 0),
    (2, 1, 0),
    (2, 2, 0),
    (1, 2, 0),
    (0, 2, 0),
    (0, 1, 0),
]
```

- [ ] **Step 4: Run tests to verify they pass**

```bash
pytest experiments/134_pattern_coherence/tests/test_fixtures.py -v
```

Expected: 9 PASS.

If any geometric-constraint test fails, the fixture is invalid for the rule and the spec must be revisited.

- [ ] **Step 5: Run all unit tests as a sanity sweep**

```bash
pytest experiments/134_pattern_coherence/tests/ -v
```

Expected: all PASS (~27 total).

- [ ] **Step 6: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: fixtures F1, F2, F3 with validation"
```

---

## Task 10: Phase 1 deliverable — bit-identity over 10,000 cycles

**Files:**
- Modify: `experiments/134_pattern_coherence/phase1_test.py`

- [ ] **Step 1: Write the Phase 1 deliverable test**

Replace contents of `phase1_test.py`:

```python
"""Phase 1 deliverable: verify bit-identity at every K-tick boundary
for 10,000 cycles, for each fixture.

This is THE Phase 1 test. If this passes for all three fixtures, Phase 1
succeeded. If any fixture fails, Phase 1 failed and the failure mode
(drift, wedge, non-uniqueness) is informative on its own.

The test is transactional: state is sampled at K-tick boundaries, framed
as 'the pattern's renewal transaction completed correctly,' not 'the
pattern looks the same at random samples.'
"""

import hashlib

import pytest

import fixtures as f
import rule as r
import substrate as s


N_CYCLES = 10_000


def _canvas_hash(canvas: s.Canvas) -> str:
    """Stable hash of canvas state. Sorts items so dict iteration order
    doesn't matter."""
    items = sorted(canvas.items())
    return hashlib.sha256(repr(items).encode()).hexdigest()


def _run_fixture_phase1(cycle, sign):
    """Bootstrap, advance through one full cycle, snapshot reference hash,
    then run N_CYCLES more cycles, asserting hash stays identical at each
    K-tick boundary."""
    K = len(cycle)
    canvas: s.Canvas = {}
    r.bootstrap(canvas, cycle, sign=sign)

    # Advance one full cycle so the canvas is in a clean steady state
    # (bootstrap itself produces a steady state, but this also exercises
    # the tick() path before we sample the reference).
    for _ in range(K):
        r.tick(canvas)
    reference_hash = _canvas_hash(canvas)
    reference_state = dict(canvas)

    # Run N_CYCLES more cycles; check at each K-tick boundary.
    for n in range(1, N_CYCLES + 1):
        for _ in range(K):
            r.tick(canvas)
        h = _canvas_hash(canvas)
        if h != reference_hash:
            # Find the diverging cells for diagnostic
            diff = {
                cell: (reference_state.get(cell), canvas.get(cell))
                for cell in set(reference_state) | set(canvas)
                if reference_state.get(cell) != canvas.get(cell)
            }
            pytest.fail(
                f"Drift at cycle n={n} (substrate tick {(n+1)*K}): "
                f"hash changed from {reference_hash[:12]}... "
                f"to {h[:12]}...; diverging cells: {diff}"
            )

    return reference_hash


def test_F1_K4_square_bit_identity_10000_cycles_positive():
    h = _run_fixture_phase1(f.F1_K4_SQUARE, sign=1)
    print(f"\nF1 K=4 (matter) reference hash: {h}")


def test_F1_K4_square_bit_identity_10000_cycles_negative():
    h = _run_fixture_phase1(f.F1_K4_SQUARE, sign=-1)
    print(f"\nF1 K=4 (antimatter) reference hash: {h}")


def test_F2_K6_perimeter_bit_identity_10000_cycles():
    h = _run_fixture_phase1(f.F2_K6_PERIMETER, sign=1)
    print(f"\nF2 K=6 reference hash: {h}")


def test_F3_K8_ring_bit_identity_10000_cycles():
    h = _run_fixture_phase1(f.F3_K8_RING, sign=1)
    print(f"\nF3 K=8 reference hash: {h}")
```

- [ ] **Step 2: Run the deliverable**

```bash
pytest experiments/134_pattern_coherence/phase1_test.py -v -s
```

Expected: 4 PASS. The reference hashes are printed in the `-s` output for the record.

If a test FAILs:
- **Drift:** the failure message identifies the cycle n and diverging cells. This is the falsification result. Record in RESULTS.md and stop — do not silently fix.
- **Wedge / non-uniqueness:** Step B raises `ValueError`. The fixture is invalid for the rule; revisit fixture design.

- [ ] **Step 3: Capture run output**

Save the output for RESULTS.md:

```bash
pytest experiments/134_pattern_coherence/phase1_test.py -v -s > experiments/134_pattern_coherence/phase1_run.log 2>&1
```

- [ ] **Step 4: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: bit-identity test over 10000 cycles"
```

---

## Task 11: RESULTS.md and README update

**Files:**
- Create: `experiments/134_pattern_coherence/RESULTS.md`
- Modify: `experiments/134_pattern_coherence/README.md`

- [ ] **Step 1: Write RESULTS.md**

Create `RESULTS.md` with this template, filled in from the run output:

```markdown
# Experiment 134 Phase 1 — Results

**Status:** [PASS | FAIL]
**Date run:** [YYYY-MM-DD]
**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md`

## Summary

Phase 1 verified bit-identity at every K-tick boundary for [N] of 4 fixture
configurations (F1 matter, F1 antimatter, F2, F3) over 10,000 cycles each.

## Reference hashes

| Fixture | K | Sign | Reference hash | Cycles verified |
|---------|---|------|----------------|-----------------|
| F1 (2x2 square) | 4 | +1 | [hash from run]   | 10,000 |
| F1 (2x2 square) | 4 | -1 | [hash from run]   | 10,000 |
| F2 (2x3 perimeter) | 6 | +1 | [hash from run] | 10,000 |
| F3 (3x3 ring) | 8 | +1 | [hash from run]   | 10,000 |

## Anomalies

[None | describe any]

## Failure mode (if applicable)

[Drift cell + tick + diff | wedge cell | non-uniqueness candidates | N/A]

## What this proves

The renewal rule (sign-blind, transactional, single paint per tick) realizes
exact fixed-point invariance for three pattern fixtures spanning K = 4, 6, 8.
This validates:

- Doc 28's "renewal not preservation" commitment as operational on a
  discrete signed-integer substrate.
- The rule's sign-blindness — same rule supports matter and antimatter
  patterns; antimatter is the natural CP-mirror, not engineered.
- Transactional renewal — pattern is bit-identical at every K-tick
  boundary; substrate-tick samples between boundaries are not.

## What this does not prove

- Pattern shape emergence (Phase 1 fixtures are predetermined).
- Drift under external γ field (Phase 2 — not yet started).
- Annihilation (Phase 3 — not yet started).
- Pattern coherence under field gradients beyond the renewal cycle's K.
```

- [ ] **Step 2: Update README.md**

Replace contents:

```markdown
# Experiment 134: Pattern Coherence (Phase 1)

See `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md` for the
full design and rationale, and `RESULTS.md` for the Phase 1 outcome.

## Run

From repo root:

```bash
# Full test sweep (unit + Phase 1 deliverable)
pytest experiments/134_pattern_coherence/ -v

# Phase 1 deliverable only (bit-identity over 10,000 cycles per fixture)
pytest experiments/134_pattern_coherence/phase1_test.py -v -s
```

## Status

Phase 1: see `RESULTS.md`.
Phase 2 / Phase 3: not yet started; design sketches in the spec.
```

- [ ] **Step 3: Commit**

```bash
git add experiments/134_pattern_coherence/
git commit -m "Exp 134 Phase 1: RESULTS.md + README"
```

---

## Self-Review

Spec coverage:
- Section 1 substrate (signed-int 3D lattice + decay) → Tasks 2, 3
- Section 1 fixtures F1/F2/F3 → Tasks 9 (defined) + 10 (verified)
- Section 1 geometric constraint → Task 9 validation tests
- Section 2 Step A → Task 2
- Section 2 Step B → Tasks 5, 6, 7
- Section 2 bootstrap → Task 4
- Section 2 sign-blindness → Task 7 (negative-sign test) + Task 10 (F1 antimatter test)
- Section 2 transactional renewal proof → verified empirically by Task 10
- Section 3 success criterion (bit-identity at K-tick boundaries) → Task 10
- Section 3 falsification modes → diagnostic logic in Task 10's `_run_fixture_phase1`
- Section 3 deliverables list → matches Task 1's scaffolding + Task 11's RESULTS.md
- Section 3 "what we don't do" → respected (no planet, no drift, no annihilation, no plotting)

All sections covered. No gaps.

---

## Failure handling

If any task's tests fail in unexpected ways:

- **Import errors / pytest discovery failures** at Task 1: the leading-digit
  package name issue from the import-path note. Use `conftest.py` with
  `sys.path.insert(0, dirname(__file__))` and import modules without a
  package prefix (e.g., `import substrate as s`, not
  `import experiments.134_pattern_coherence.substrate`).
- **find_c0 wedged or non-unique on a real fixture** at Task 10: not an
  implementation bug — it means the fixture violates the geometric
  constraint. The validation tests in Task 9 should catch this; if they
  pass and Task 10 still fails this way, there's a bug in either
  `_satisfies_geometric_constraint` or `find_c0`. Inspect the failing
  fixture's cycle and lattice neighborhood.
- **Drift at some specific cycle n** at Task 10: this is the falsification
  result. Record exactly which cycle, which cells diverged, and what the
  γ values were before and after. Do NOT debug into a fix; this is data.
  Update RESULTS.md with the failure and stop.
