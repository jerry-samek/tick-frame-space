# Closed-Loop Graph Substrate Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implement a closed-loop graph substrate where total energy is conserved, cells see only differences, and orbital mechanics emerges from a hold-and-fire integer rule with wake bias — per spec `docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md`.

**Architecture:** Single-file vectorized substrate (`substrate.py`) implementing graph state + tick rule using numpy directed-edge arrays. Per-phase driver scripts that import substrate and run the experiment defined in the spec's §5. Coordinates kept analyst-side only; substrate sees only adjacency.

**Tech Stack:** Python 3.11+, numpy, scipy.spatial.cKDTree (RGG construction), matplotlib (visualization), pytest (unit tests).

**Spec reference:** All design decisions in `docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md`. This plan implements that spec.

---

## File Structure

```
experiments/133_closed_loop_substrate/
├── README.md                  # Quick start, phase summary
├── substrate.py               # Core: graph build + state + vectorized tick
├── metrics.py                 # Per-tick metrics + conservation check + clustering
├── visualization.py           # Radial bins, slope fit, orbit traces
├── phase1_sanity.py           # Phase 1 driver: conservation + diffusion
├── phase2_static_star.py      # Phase 2 driver: field formation, slope check
├── phase3_test_pattern.py     # Phase 3 driver: gradient response check
├── phase4_orbit.py            # Phase 4 driver: orbital mechanics
├── phase5_emergent.py         # Phase 5 driver: emergent orbit (stretch)
├── tests/
│   └── test_substrate.py      # Unit tests on small hand-verifiable graphs
└── results/                   # Output JSONs and PNGs (created at runtime)
```

**Boundary rules:**
- `substrate.py` knows nothing about phases or experiments — pure mechanics.
- `metrics.py` and `visualization.py` are analyst-side helpers; they may use coordinates.
- Phase drivers import substrate + metrics + visualization; they own initial conditions, run length, and success-criteria checks.
- `tests/` exercise correctness of substrate.py on tiny (≤20 cell) graphs where outputs can be hand-verified.

---

## Task 1: Project skeleton

**Files:**
- Create: `experiments/133_closed_loop_substrate/README.md`
- Create: `experiments/133_closed_loop_substrate/__init__.py`
- Create: `experiments/133_closed_loop_substrate/tests/__init__.py`
- Create: `experiments/133_closed_loop_substrate/results/.gitkeep`

- [ ] **Step 1: Create directory skeleton and README**

```bash
mkdir -p experiments/133_closed_loop_substrate/tests
mkdir -p experiments/133_closed_loop_substrate/results
touch experiments/133_closed_loop_substrate/__init__.py
touch experiments/133_closed_loop_substrate/tests/__init__.py
touch experiments/133_closed_loop_substrate/results/.gitkeep
```

Write `experiments/133_closed_loop_substrate/README.md`:

```markdown
# Experiment 133 — Closed-Loop Graph Substrate

Substrate orbital mechanics from a closed-loop, conservation-respecting,
differential-only graph dynamics. Cells hold integer energy, see only
differences, and fire when integer math allows. No `+1/tick`, no entity labels,
no coordinates in the substrate.

See spec: `docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md`

## Quick start

```bash
# Sanity (fast)
python -u phase1_sanity.py

# Field formation (~10 min on 100k nodes)
python -u phase2_static_star.py

# Gradient response (~5 min)
python -u phase3_test_pattern.py

# The goal — orbit
python -u phase4_orbit.py

# Stretch goal — emergent orbit
python -u phase5_emergent.py
```

## Phases

1. Conservation + diffusion sanity
2. Static star, 1/r² field formation
3. Test pattern in field (gradient response)
4. Orbit (Keplerian, with seeded tangential bias)
5. Emergent orbit (no seeded bias) — stretch goal

Success criteria and falsification per spec §5 and §8.
```

- [ ] **Step 2: Verify and commit**

```bash
ls -la experiments/133_closed_loop_substrate/
git add experiments/133_closed_loop_substrate/
git commit -m "experiment 133: skeleton and README"
```

Expected: directory tree exists, README readable.

---

## Task 2: RGG construction

**Files:**
- Create: `experiments/133_closed_loop_substrate/substrate.py` (initial scaffolding)
- Create: `experiments/133_closed_loop_substrate/tests/test_substrate.py`

The graph is built once at init: sample N points uniformly in unit cube, connect any two within radius ρ, return adjacency in directed-edge-list form (efficient for vectorization). Coordinates returned separately for analyst use.

- [ ] **Step 1: Write the failing test**

Append to `experiments/133_closed_loop_substrate/tests/test_substrate.py`:

```python
"""Unit tests for substrate.py.

Tests use small hand-verifiable graphs (N ≤ 20) so we can compute
expected outputs by hand. The vectorized implementation must match.
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from substrate import build_rgg


def test_build_rgg_basic_shapes():
    """RGG construction returns expected array shapes and dtypes."""
    coords, src, dst, back_edge = build_rgg(n_nodes=100, radius=0.2, seed=42)

    assert coords.shape == (100, 3)
    assert coords.dtype == np.float64

    # Directed edges: 2M entries (each undirected edge → 2 directed)
    assert src.shape == dst.shape == back_edge.shape
    assert src.ndim == 1
    assert src.dtype == np.int64

    # back_edge is an involution: back_edge[back_edge[i]] == i
    assert np.all(back_edge[back_edge] == np.arange(len(back_edge)))

    # Symmetry: for every directed edge (u, v), there's a directed edge (v, u)
    pairs = set(zip(src.tolist(), dst.tolist()))
    for u, v in pairs:
        assert (v, u) in pairs


def test_build_rgg_no_self_loops():
    coords, src, dst, _ = build_rgg(n_nodes=50, radius=0.3, seed=7)
    assert np.all(src != dst)


def test_build_rgg_radius_respected():
    """Edges only between points within radius."""
    coords, src, dst, _ = build_rgg(n_nodes=200, radius=0.15, seed=11)
    distances = np.linalg.norm(coords[src] - coords[dst], axis=1)
    assert np.all(distances <= 0.15 + 1e-9)
```

- [ ] **Step 2: Run test to verify failure**

```bash
cd experiments/133_closed_loop_substrate
python -m pytest tests/test_substrate.py::test_build_rgg_basic_shapes -v
```

Expected: ImportError or AttributeError (build_rgg not defined).

- [ ] **Step 3: Implement build_rgg in substrate.py**

Write `experiments/133_closed_loop_substrate/substrate.py`:

```python
"""Closed-loop graph substrate — core mechanics.

Spec: docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md

Substrate is a graph (RGG-constructed). Coordinates are returned to caller
but the substrate itself never references them — they are analyst-side only.

Directed-edge representation enables fully-vectorized tick updates via
numpy scatter operations (np.add.at).
"""

import numpy as np
from scipy.spatial import cKDTree


def build_rgg(n_nodes: int, radius: float, seed: int = 42):
    """Build a 3D random geometric graph.

    Args:
        n_nodes: number of cells
        radius: connection radius in unit cube [0,1]^3
        seed: numpy RNG seed for reproducibility

    Returns:
        coords: (N, 3) float64 — analyst-side only, never used by substrate
        src: (2M,) int64 — source cell of each directed edge
        dst: (2M,) int64 — dest cell of each directed edge
        back_edge: (2M,) int64 — for directed edge i, the index of (dst, src)
    """
    rng = np.random.default_rng(seed)
    coords = rng.random((n_nodes, 3), dtype=np.float64)

    tree = cKDTree(coords)
    pairs = tree.query_pairs(radius, output_type='ndarray')  # (M, 2), u < v

    if len(pairs) == 0:
        raise ValueError(f"No edges built; radius {radius} too small for n={n_nodes}")

    # Build directed edges: each undirected (u, v) → two directed (u→v) and (v→u)
    forward_src = pairs[:, 0]
    forward_dst = pairs[:, 1]
    backward_src = pairs[:, 1]
    backward_dst = pairs[:, 0]

    src = np.concatenate([forward_src, backward_src]).astype(np.int64)
    dst = np.concatenate([forward_dst, backward_dst]).astype(np.int64)

    # back_edge[i] = index j such that src[j] == dst[i] and dst[j] == src[i]
    # Forward edges occupy [0, M); backward edges occupy [M, 2M).
    # Forward edge i has back_edge i + M; backward edge i+M has back_edge i.
    M = len(pairs)
    back_edge = np.concatenate([
        np.arange(M, 2 * M, dtype=np.int64),
        np.arange(0, M, dtype=np.int64),
    ])

    return coords, src, dst, back_edge
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: 3 PASS.

- [ ] **Step 5: Commit**

```bash
git add experiments/133_closed_loop_substrate/substrate.py \
        experiments/133_closed_loop_substrate/tests/test_substrate.py
git commit -m "experiment 133: build_rgg with directed-edge representation"
```

---

## Task 3: Cell state initialization

**Files:**
- Modify: `experiments/133_closed_loop_substrate/substrate.py` (add `init_state`)
- Modify: `experiments/133_closed_loop_substrate/tests/test_substrate.py` (add tests)

State consists of `E` (per-cell integer energy) and `received` (per-directed-edge integer count of last tick's transmissions). At init, `received` is zero; `E` is whatever the caller seeds.

- [ ] **Step 1: Write the failing test**

Append to `tests/test_substrate.py`:

```python
from substrate import init_state


def test_init_state_zero():
    coords, src, dst, back_edge = build_rgg(n_nodes=20, radius=0.4, seed=3)
    n_directed = len(src)
    E, received = init_state(n_nodes=20, n_directed=n_directed, energy_init=None)

    assert E.shape == (20,)
    assert E.dtype == np.int64
    assert np.all(E == 0)

    assert received.shape == (n_directed,)
    assert received.dtype == np.int64
    assert np.all(received == 0)


def test_init_state_with_seed():
    coords, src, dst, back_edge = build_rgg(n_nodes=20, radius=0.4, seed=3)
    n_directed = len(src)

    energy_init = np.zeros(20, dtype=np.int64)
    energy_init[5] = 100  # seed 100 quanta at cell 5

    E, received = init_state(n_nodes=20, n_directed=n_directed, energy_init=energy_init)

    assert E[5] == 100
    assert E.sum() == 100
    assert np.all(received == 0)
```

- [ ] **Step 2: Run test to verify failure**

```bash
python -m pytest tests/test_substrate.py::test_init_state_zero -v
```

Expected: ImportError on `init_state`.

- [ ] **Step 3: Implement init_state**

Append to `substrate.py`:

```python
def init_state(n_nodes: int, n_directed: int, energy_init=None):
    """Initialize cell state and per-edge incoming history.

    Args:
        n_nodes: number of cells
        n_directed: number of directed edges (= 2M)
        energy_init: optional (N,) int array of initial energy per cell.
                     If None, all cells start at 0.

    Returns:
        E: (N,) int64 — per-cell energy
        received: (2M,) int64 — quanta received on each directed edge last tick
    """
    if energy_init is None:
        E = np.zeros(n_nodes, dtype=np.int64)
    else:
        E = np.asarray(energy_init, dtype=np.int64).copy()
        if E.shape != (n_nodes,):
            raise ValueError(f"energy_init shape {E.shape} != ({n_nodes},)")

    received = np.zeros(n_directed, dtype=np.int64)
    return E, received
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: 5 PASS (all previous tests + 2 new).

- [ ] **Step 5: Commit**

```bash
git add experiments/133_closed_loop_substrate/substrate.py \
        experiments/133_closed_loop_substrate/tests/test_substrate.py
git commit -m "experiment 133: cell state initialization"
```

---

## Task 4: Single-tick update (vectorized)

**Files:**
- Modify: `experiments/133_closed_loop_substrate/substrate.py` (add `tick`)
- Modify: `experiments/133_closed_loop_substrate/tests/test_substrate.py` (add tests)

This is the load-bearing function: one full tick of the closed-loop rule per spec §4.2. Fully vectorized using `np.add.at`. Conservation must hold exactly (integer arithmetic).

The rule (recap from spec):
1. For each directed edge i with source cell c, compute `I_local[i] = received[back_edge[i]]` (what arrived through the back-edge last tick — i.e., from the neighbor on this edge).
2. Compute `mean(I)` per cell, broadcast to per-edge.
3. `w_e = max(0, 1 + α·(mean - I_local))`.
4. Normalize w per cell (sum to 1 across cell's outgoing edges).
5. `target_e = E[src] · w_e`. `outgoing[e] = floor(target_e)`.
6. `R[c] = E[c] − Σ outgoing[e for e in cell c]`. Cell holds R.
7. `received_per_cell[c] = Σ outgoing[e for e in incoming edges to c]` = `np.add.at(zeros(N), dst, outgoing)`.
8. `E_new = R + received_per_cell`.
9. `received_new = outgoing` (this becomes next tick's input).

- [ ] **Step 1: Write the failing test (conservation)**

Append to `tests/test_substrate.py`:

```python
from substrate import tick


def test_tick_conservation_random_init():
    """Total energy is invariant under a single tick on random init."""
    rng = np.random.default_rng(123)
    coords, src, dst, back_edge = build_rgg(n_nodes=200, radius=0.2, seed=99)
    n_directed = len(src)

    energy_init = rng.integers(0, 50, size=200, dtype=np.int64)
    E, received = init_state(200, n_directed, energy_init)

    total_before = E.sum()
    E_new, received_new = tick(E, received, src, dst, back_edge, alpha=0.0)
    total_after = E_new.sum()

    assert total_before == total_after, f"{total_before} != {total_after}"


def test_tick_conservation_many_ticks():
    """Conservation holds over many ticks with non-trivial alpha."""
    rng = np.random.default_rng(456)
    coords, src, dst, back_edge = build_rgg(n_nodes=300, radius=0.18, seed=11)
    n_directed = len(src)

    energy_init = rng.integers(0, 100, size=300, dtype=np.int64)
    E, received = init_state(300, n_directed, energy_init)

    total_initial = E.sum()
    for _ in range(50):
        E, received = tick(E, received, src, dst, back_edge, alpha=2.0)
        assert E.sum() == total_initial


def test_tick_isolated_cell_unchanged():
    """A cell with degree 0 retains its energy forever."""
    # Build graph where node 0 has no edges (use radius too small)
    coords = np.array([[0.5, 0.5, 0.5], [0.0, 0.0, 0.0], [0.1, 0.0, 0.0]])
    # Manually construct edges: only between node 1 and node 2
    src = np.array([1, 2], dtype=np.int64)
    dst = np.array([2, 1], dtype=np.int64)
    back_edge = np.array([1, 0], dtype=np.int64)

    E = np.array([42, 10, 10], dtype=np.int64)
    received = np.zeros(2, dtype=np.int64)

    E_new, _ = tick(E, received, src, dst, back_edge, alpha=0.0)

    assert E_new[0] == 42, "Isolated cell must retain energy"


def test_tick_low_energy_holds():
    """With α=0 and E < degree, cell holds all energy (target floors to 0)."""
    # Two cells, one edge between them
    src = np.array([0, 1], dtype=np.int64)
    dst = np.array([1, 0], dtype=np.int64)
    back_edge = np.array([1, 0], dtype=np.int64)

    # Each cell has degree 1; E = 0 means target = 0; E = 5 means target = 5
    # With α=0, w = 1, normalized to 1, target = E*1 = E
    # So with degree=1, all energy goes through the single edge each tick (no holding)
    # For real holding, we need degree > 1. Build a star: 1 center + 3 leaves.

    # 4 nodes: 0 center, 1/2/3 leaves; 6 directed edges (3 undirected)
    src = np.array([0, 0, 0, 1, 2, 3], dtype=np.int64)
    dst = np.array([1, 2, 3, 0, 0, 0], dtype=np.int64)
    # back_edge: for edge 0 (0→1), back is edge 3 (1→0)
    back_edge = np.array([3, 4, 5, 0, 1, 2], dtype=np.int64)

    E = np.array([2, 0, 0, 0], dtype=np.int64)  # center has 2, leaves have 0
    received = np.zeros(6, dtype=np.int64)

    E_new, received_new = tick(E, received, src, dst, back_edge, alpha=0.0)

    # Center has degree 3, E=2. target = 2*(1/3) = 0.666 per edge → floor = 0 each.
    # Residue = 2. Cell holds all of it. Receives 0 (leaves had 0).
    assert E_new[0] == 2, f"Expected center to hold 2, got {E_new[0]}"
    assert E_new[1:].sum() == 0, "Leaves should have received nothing"
```

- [ ] **Step 2: Run tests to verify failure**

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: 4 new tests FAIL (tick not defined).

- [ ] **Step 3: Implement tick (vectorized)**

Append to `substrate.py`:

```python
def tick(E, received, src, dst, back_edge, alpha: float):
    """Execute one tick of the closed-loop substrate rule.

    Per spec §4.2:
      1. I_local[i] = received[back_edge[i]] (what came in last tick via back-edge)
      2. w_e = max(0, 1 + α·(mean(I) − I_local)), normalized per cell
      3. target_e = E[src] · w_e; outgoing[e] = floor(target_e)
      4. residue R[c] = E[c] − sum of outgoing on c's outgoing edges (held to next tick)
      5. received_per_cell[c] = sum of outgoing on c's incoming edges
      6. E_new = R + received_per_cell
      7. received_new = outgoing

    Args:
        E: (N,) int64 — current cell energy
        received: (2M,) int64 — quanta received on each directed edge last tick
        src, dst, back_edge: (2M,) int64 — directed-edge structure
        alpha: float — wake-bias strength

    Returns:
        E_new: (N,) int64 — cell energy after tick
        received_new: (2M,) int64 — quanta sent on each directed edge this tick
    """
    n_nodes = E.shape[0]
    n_directed = src.shape[0]

    # Step 1: incoming-via-back-edge per directed edge
    # For directed edge i (src=c, dst=n), I_local[i] = quanta cell c received from n last tick.
    # That arrived through the back-edge (n→c), whose index is back_edge[i].
    I_local = received[back_edge].astype(np.float64)

    # Step 2: compute mean(I) per cell, broadcast to per directed edge
    sum_I_per_cell = np.zeros(n_nodes, dtype=np.float64)
    np.add.at(sum_I_per_cell, src, I_local)
    degree = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(degree, src, 1)
    mean_I_per_cell = np.zeros(n_nodes, dtype=np.float64)
    nonzero = degree > 0
    mean_I_per_cell[nonzero] = sum_I_per_cell[nonzero] / degree[nonzero]
    mean_I_per_edge = mean_I_per_cell[src]  # (2M,)

    # Wake-bias weights per directed edge
    w = 1.0 + alpha * (mean_I_per_edge - I_local)
    w = np.maximum(w, 0.0)  # clamp negatives (occurs when α large)

    # Normalize per cell (sum to 1 across cell's outgoing edges)
    sum_w_per_cell = np.zeros(n_nodes, dtype=np.float64)
    np.add.at(sum_w_per_cell, src, w)
    sum_w_per_edge = sum_w_per_cell[src]
    # Avoid division by zero: if cell's total w is 0 (all edges clamped), fall back to uniform
    fallback = sum_w_per_edge == 0
    if fallback.any():
        # Per-cell fallback to 1/degree
        w[fallback] = 1.0
        # Recompute affected sums
        sum_w_per_cell = np.zeros(n_nodes, dtype=np.float64)
        np.add.at(sum_w_per_cell, src, w)
        sum_w_per_edge = sum_w_per_cell[src]
    sum_w_per_edge = np.where(sum_w_per_edge > 0, sum_w_per_edge, 1.0)
    w = w / sum_w_per_edge

    # Step 3: targets and floors
    E_per_edge = E[src].astype(np.float64)
    target = E_per_edge * w
    outgoing = np.floor(target).astype(np.int64)

    # Step 4: residue per cell (E − sum of outgoing on its outgoing edges)
    sent_per_cell = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(sent_per_cell, src, outgoing)
    residue = E - sent_per_cell

    # Step 5: received per cell (sum of outgoing on its incoming directed edges)
    # An incoming edge to cell c is one with dst[i] == c.
    received_per_cell = np.zeros(n_nodes, dtype=np.int64)
    np.add.at(received_per_cell, dst, outgoing)

    # Step 6: new energy
    E_new = residue + received_per_cell

    # Step 7: new per-edge incoming = this tick's outgoing
    received_new = outgoing

    return E_new, received_new
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: all PASS (9 total now).

- [ ] **Step 5: Add an explicit conservation assertion test under wake bias**

Append to `tests/test_substrate.py`:

```python
def test_tick_wake_bias_creates_asymmetry():
    """With α large and biased history, outgoing distribution is asymmetric."""
    # Star graph: center + 3 leaves
    src = np.array([0, 0, 0, 1, 2, 3], dtype=np.int64)
    dst = np.array([1, 2, 3, 0, 0, 0], dtype=np.int64)
    back_edge = np.array([3, 4, 5, 0, 1, 2], dtype=np.int64)

    # Center has E=300, has received heavily on edge from leaf 1 (back_edge of edge 0→1 is 1→0)
    # received[3] (1→0) = 100, received[4] (2→0) = 0, received[5] (3→0) = 0
    received = np.array([0, 0, 0, 100, 0, 0], dtype=np.int64)
    E = np.array([300, 0, 0, 0], dtype=np.int64)

    E_new, received_new = tick(E, received, src, dst, back_edge, alpha=10.0)

    # Center fires 300 across 3 edges. Edge 0 (0→1) was heavily fed back by 1→0.
    # Wake bias favors NOT sending back. So outgoing on edge 0 should be smallest.
    out_to_1 = received_new[0]
    out_to_2 = received_new[1]
    out_to_3 = received_new[2]

    assert out_to_1 < out_to_2, f"Expected backflow penalty: {out_to_1} >= {out_to_2}"
    assert out_to_1 < out_to_3, f"Expected backflow penalty: {out_to_1} >= {out_to_3}"
    assert out_to_1 + out_to_2 + out_to_3 == 300, "Conservation violated"
```

```bash
python -m pytest tests/test_substrate.py::test_tick_wake_bias_creates_asymmetry -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add experiments/133_closed_loop_substrate/substrate.py \
        experiments/133_closed_loop_substrate/tests/test_substrate.py
git commit -m "experiment 133: vectorized tick rule with conservation tests"
```

---

## Task 5: Metrics + clustering helpers

**Files:**
- Create: `experiments/133_closed_loop_substrate/metrics.py`
- Modify: `experiments/133_closed_loop_substrate/tests/test_substrate.py`

Per-tick metrics for logging + post-hoc clustering for entity centroid measurement (analyst-side).

- [ ] **Step 1: Write the failing test for metrics**

Append to `tests/test_substrate.py`:

```python
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from metrics import per_tick_summary


def test_per_tick_summary_returns_expected_keys():
    rng = np.random.default_rng(7)
    E = rng.integers(0, 100, size=50, dtype=np.int64)

    src = np.array([0, 0, 1], dtype=np.int64)
    dst = np.array([1, 2, 0], dtype=np.int64)

    summary = per_tick_summary(E, src)

    assert 'total_energy' in summary
    assert 'max_E' in summary
    assert 'mean_E' in summary
    assert 'n_firing_cells' in summary
    assert summary['total_energy'] == int(E.sum())
    assert summary['max_E'] == int(E.max())
```

- [ ] **Step 2: Run to verify failure**

```bash
python -m pytest tests/test_substrate.py::test_per_tick_summary_returns_expected_keys -v
```

Expected: ImportError.

- [ ] **Step 3: Implement metrics.py**

Write `experiments/133_closed_loop_substrate/metrics.py`:

```python
"""Per-tick metrics + post-hoc entity clustering.

Spec §5: per-tick metrics include total_energy, n_firing_cells, max/mean E,
and cluster centroids (analyst-side, using saved coordinates).
"""

import numpy as np


def per_tick_summary(E, src):
    """Compute lightweight per-tick metrics.

    Args:
        E: (N,) int64 — current cell energy
        src: (2M,) int64 — to compute per-cell degree

    Returns:
        dict with keys: total_energy, max_E, mean_E, n_firing_cells
        where n_firing_cells = #cells with E ≥ degree (proxy: E ≥ 1
        is the looser proxy used here; "firing" defined per edge).
    """
    degree = np.bincount(src, minlength=E.shape[0]).astype(np.int64)
    firing = (E >= degree) & (degree > 0)

    return {
        'total_energy': int(E.sum()),
        'max_E': int(E.max()),
        'mean_E': float(E.mean()),
        'n_firing_cells': int(firing.sum()),
    }


def cluster_high_energy(E, coords, threshold_quantile=0.95):
    """Identify high-energy clusters via thresholding + spatial neighbors.

    Analyst-side use only — uses coordinates. NOT used by the substrate.

    Args:
        E: (N,) int — cell energy
        coords: (N, 3) float — analyst coords
        threshold_quantile: only cells with E above this quantile considered

    Returns:
        list of dicts: [{'centroid': (x,y,z), 'mass': total_E, 'cell_count': n}, ...]
        sorted descending by mass
    """
    from scipy.spatial import cKDTree
    from scipy.cluster.hierarchy import fcluster, linkage

    threshold = np.quantile(E, threshold_quantile)
    high_idx = np.where(E > threshold)[0]
    if len(high_idx) < 2:
        if len(high_idx) == 1:
            i = high_idx[0]
            return [{'centroid': tuple(coords[i]), 'mass': int(E[i]), 'cell_count': 1}]
        return []

    high_coords = coords[high_idx]
    high_E = E[high_idx]

    # Single-linkage clustering with cutoff distance
    # Cutoff chosen as roughly the typical edge length of the RGG
    # (caller can adjust by passing a different threshold_quantile).
    linkage_matrix = linkage(high_coords, method='single')
    cluster_ids = fcluster(linkage_matrix, t=0.05, criterion='distance')

    clusters = []
    for cid in np.unique(cluster_ids):
        mask = cluster_ids == cid
        cells = high_idx[mask]
        masses = E[cells]
        total_mass = int(masses.sum())
        if total_mass == 0:
            continue
        # Mass-weighted centroid
        centroid = (coords[cells] * masses[:, None]).sum(axis=0) / total_mass
        clusters.append({
            'centroid': tuple(centroid.tolist()),
            'mass': total_mass,
            'cell_count': int(mask.sum()),
        })

    clusters.sort(key=lambda c: -c['mass'])
    return clusters
```

- [ ] **Step 4: Run tests to verify pass**

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: all PASS.

- [ ] **Step 5: Add clustering test**

Append to `tests/test_substrate.py`:

```python
from metrics import cluster_high_energy


def test_cluster_high_energy_finds_obvious_cluster():
    """A clear concentration is identified as a single cluster."""
    n = 100
    coords = np.random.default_rng(42).random((n, 3))
    E = np.zeros(n, dtype=np.int64)
    # Put 5 high-energy cells near (0.5, 0.5, 0.5)
    for i in range(5):
        coords[i] = [0.5 + i * 0.005, 0.5, 0.5]
        E[i] = 100

    clusters = cluster_high_energy(E, coords, threshold_quantile=0.9)
    assert len(clusters) >= 1
    # Top cluster's mass should be close to 500 (5 × 100)
    assert clusters[0]['mass'] >= 400
    assert clusters[0]['cell_count'] >= 4
```

```bash
python -m pytest tests/test_substrate.py -v
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add experiments/133_closed_loop_substrate/metrics.py \
        experiments/133_closed_loop_substrate/tests/test_substrate.py
git commit -m "experiment 133: metrics + clustering helpers"
```

---

## Task 6: Visualization helpers

**Files:**
- Create: `experiments/133_closed_loop_substrate/visualization.py`

Two analyst-side helpers: radial-density binning + slope fit (for Phase 2's −1.968 check), and orbit-trace plotting (for Phase 4). Both use coordinates; substrate doesn't.

- [ ] **Step 1: Implement visualization.py**

Write `experiments/133_closed_loop_substrate/visualization.py`:

```python
"""Analyst-side visualization for closed-loop substrate experiments.

These helpers use coordinates and have no role in the substrate dynamics.
They produce PNGs and return numerical fit results.
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt


def radial_density_profile(E, coords, center, n_bins=30, r_min=None, r_max=None):
    """Bin cell energies by radial distance from a center point.

    Args:
        E: (N,) int — cell energy
        coords: (N, 3) float
        center: (3,) center coordinates
        n_bins: number of log-spaced radial bins
        r_min, r_max: bin range; defaults: (1.5×min nonzero distance, 0.7×max distance)

    Returns:
        r_centers: (n_bins,) bin centers
        density: (n_bins,) mean E per cell in each bin
    """
    r = np.linalg.norm(coords - np.asarray(center)[None, :], axis=1)
    if r_min is None:
        r_min = np.maximum(r.min(), 1e-3) * 1.5
    if r_max is None:
        r_max = r.max() * 0.7

    bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), n_bins + 1)
    bin_indices = np.digitize(r, bin_edges) - 1

    r_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    density = np.zeros(n_bins)
    for i in range(n_bins):
        mask = bin_indices == i
        if mask.any():
            density[i] = E[mask].mean()

    return r_centers, density


def fit_loglog_slope(r, density, density_floor=1e-6):
    """Fit log-log slope of density vs r in regions where density > floor.

    Returns:
        slope: float — fitted slope (e.g., −2 for 1/r²)
        intercept: float
        r_squared: float — goodness of fit
    """
    mask = (density > density_floor) & (r > 0)
    if mask.sum() < 3:
        return float('nan'), float('nan'), float('nan')

    log_r = np.log(r[mask])
    log_d = np.log(density[mask])
    slope, intercept = np.polyfit(log_r, log_d, 1)
    pred = slope * log_r + intercept
    ss_res = np.sum((log_d - pred) ** 2)
    ss_tot = np.sum((log_d - log_d.mean()) ** 2)
    r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')

    return float(slope), float(intercept), float(r_squared)


def plot_radial_profile(r, density, slope=None, out_path=None, title=''):
    """Save log-log radial density plot."""
    fig, ax = plt.subplots(figsize=(6, 5))
    mask = density > 0
    ax.loglog(r[mask], density[mask], 'o-', label='measured')
    if slope is not None and not np.isnan(slope):
        # Reference line at fitted slope through first valid point
        idx0 = np.where(mask)[0][0]
        ref = density[idx0] * (r / r[idx0]) ** slope
        ax.loglog(r, ref, 'r--', label=f'slope={slope:.3f}', alpha=0.7)
    ax.set_xlabel('r (graph hop / euclidean distance)')
    ax.set_ylabel('mean energy density')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=120)
    plt.close(fig)


def plot_trajectory(positions, star_pos=None, out_path=None, title=''):
    """Plot a 2D projection of an orbit trace.

    Args:
        positions: (T, 3) array of centroid positions over time
        star_pos: (3,) optional — star centroid for reference
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    ax.plot(positions[:, 0], positions[:, 1], '-', linewidth=0.8)
    ax.plot(positions[0, 0], positions[0, 1], 'go', label='start')
    ax.plot(positions[-1, 0], positions[-1, 1], 'r^', label='end')
    if star_pos is not None:
        ax.plot(star_pos[0], star_pos[1], 'k*', markersize=15, label='star')
    ax.set_xlabel('x')
    ax.set_ylabel('y')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    if out_path:
        fig.savefig(out_path, dpi=120)
    plt.close(fig)
```

- [ ] **Step 2: Smoke-test the helpers**

Run from a Python REPL or temp script:

```bash
python -c "
import sys, os
sys.path.insert(0, 'experiments/133_closed_loop_substrate')
import numpy as np
from visualization import radial_density_profile, fit_loglog_slope, plot_radial_profile

rng = np.random.default_rng(0)
coords = rng.random((1000, 3))
center = np.array([0.5, 0.5, 0.5])
r = np.linalg.norm(coords - center, axis=1)
E = (10.0 / np.maximum(r, 0.05)**2).astype(np.int64)

r_c, d = radial_density_profile(E, coords, center, n_bins=15)
slope, intercept, r2 = fit_loglog_slope(r_c, d)
print(f'slope={slope:.3f} (target ~ -2.0), r²={r2:.3f}')
"
```

Expected: slope close to −2 (synthetic 1/r² data).

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/visualization.py
git commit -m "experiment 133: analyst-side visualization helpers"
```

---

## Task 7: Phase 1 driver — conservation + diffusion sanity

**Files:**
- Create: `experiments/133_closed_loop_substrate/phase1_sanity.py`

Spec §5 Phase 1: random uniform energy across all cells; run 1000 ticks; verify total energy invariant; verify with α=0 distribution stays roughly uniform; verify with α>0 no instability.

- [ ] **Step 1: Implement phase1_sanity.py**

Write `experiments/133_closed_loop_substrate/phase1_sanity.py`:

```python
#!/usr/bin/env python3
"""Phase 1: Conservation + diffusion sanity.

Per spec §5 Phase 1:
  - random uniform energy across all cells
  - run 1000 ticks
  - verify: total energy invariant every tick (built-in assertion)
  - α=0: distribution stays statistically uniform (pure diffusion baseline)
  - α>0: no obvious instability (no runaway concentration, no explosive osc.)

Failure here = bug, not physics. Must pass before later phases mean anything.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary


N_NODES = 50_000      # smaller for fast Phase 1
RADIUS = 0.04         # tuned for mean degree ~12
N_TICKS = 1_000
ENERGY_PER_CELL = 100  # avg energy per cell; needs to be >> degree for active flow
SEED = 42

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def run(alpha: float):
    print(f"=== Phase 1 sanity, α={alpha} ===")
    rng = np.random.default_rng(SEED)
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    mean_degree = n_directed / N_NODES
    print(f"  edges (directed): {n_directed:,}, mean degree: {mean_degree:.1f}")

    energy_init = rng.integers(
        ENERGY_PER_CELL // 2, (3 * ENERGY_PER_CELL) // 2,
        size=N_NODES, dtype=np.int64,
    )
    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial:,}, mean E per cell: {energy_init.mean():.1f}")

    E, received = init_state(N_NODES, n_directed, energy_init)

    log = []
    t0 = time.time()
    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=alpha)

        # Conservation invariant — fail loudly if violated
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(
                f"CONSERVATION VIOLATED at tick {t}: {total} != {total_initial}"
            )

        if t % 100 == 0:
            summary = per_tick_summary(E, src)
            summary['tick'] = t
            summary['alpha'] = alpha
            summary['std_E'] = float(np.std(E))
            log.append(summary)
            elapsed = time.time() - t0
            rate = t / elapsed
            eta = (N_TICKS - t) / rate
            print(
                f"  tick {t:>5d} max_E={summary['max_E']:>5d} "
                f"std_E={summary['std_E']:>6.2f} firing={summary['n_firing_cells']:>6d} "
                f"({rate:.0f} t/s, eta {eta:.0f}s)"
            )

    # Save summary
    out_path = os.path.join(OUT_DIR, f'phase1_alpha{alpha}.json')
    with open(out_path, 'w') as f:
        json.dump(log, f, indent=2)
    print(f"  saved {out_path}")

    # Sanity checks
    final_std = log[-1]['std_E']
    initial_std = float(np.std(energy_init))
    if alpha == 0.0:
        # Pure diffusion: std should NOT increase. Allow some fluctuation due to
        # threshold-firing dynamics (cells holding integer residues).
        if final_std > 1.5 * initial_std:
            print(f"  WARN: std grew from {initial_std:.2f} to {final_std:.2f} at α=0 — investigate")
        else:
            print(f"  OK: std stable at α=0 ({initial_std:.2f} → {final_std:.2f})")
    else:
        # With wake bias, some structure may form, but not runaway.
        max_E = log[-1]['max_E']
        if max_E > 10 * ENERGY_PER_CELL:
            print(f"  WARN: max_E={max_E} indicates possible runaway concentration")
        else:
            print(f"  OK: max_E={max_E} bounded")

    return log


if __name__ == '__main__':
    log_alpha0 = run(alpha=0.0)
    log_alpha1 = run(alpha=1.0)
    print("\nPhase 1 complete. Conservation passed all ticks.")
```

- [ ] **Step 2: Run Phase 1**

```bash
cd experiments/133_closed_loop_substrate
python -u phase1_sanity.py 2>&1 | tee results/phase1.log
```

Expected:
- Both runs (α=0 and α=1) complete 1000 ticks each
- No `AssertionError` (conservation holds)
- "OK: std stable at α=0"
- "OK: max_E bounded" at α=1

If the std-stable check fails or max_E shows runaway, **stop and investigate** before proceeding to Phase 2. The rule may need revision per spec §8 falsification matrix.

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/phase1_sanity.py \
        experiments/133_closed_loop_substrate/results/phase1.log \
        experiments/133_closed_loop_substrate/results/phase1_alpha*.json
git commit -m "experiment 133: phase 1 sanity passes — conservation + diffusion"
```

---

## Task 8: Phase 2 driver — static star, field formation

**Files:**
- Create: `experiments/133_closed_loop_substrate/phase2_static_star.py`

Spec §5 Phase 2: seed one heavy concentration (~1000 quanta in ~50 cells) plus background uniform; run 10k ticks; measure persistence + 1/r² slope.

- [ ] **Step 1: Implement phase2_static_star.py**

Write `experiments/133_closed_loop_substrate/phase2_static_star.py`:

```python
#!/usr/bin/env python3
"""Phase 2: Static star, field formation.

Per spec §5 Phase 2:
  - 1 heavy concentration (~1000 quanta in ~50 cells) + background uniform
  - run 10k ticks
  - measure: cluster persistence, gradient slope (target ~ -2.0, ref -1.968 from 128 v11)

Success: persistent star + 1/r² field. Failure modes per spec §8.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary, cluster_high_energy
from visualization import radial_density_profile, fit_loglog_slope, plot_radial_profile


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 10_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000      # total quanta in star
STAR_CELLS = 50       # number of cells star spans
BACKGROUND_PER_CELL = 20
ALPHA = 1.0           # tunable: try a few values if first attempt is unstable

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 2: static star, alpha={ALPHA}")

    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)
    print(f"  directed edges: {n_directed:,}, mean degree: {n_directed/N_NODES:.1f}")

    # Seed: star at STAR_CENTER, background uniform
    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS  # spread star mass evenly across star cells

    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial:,} (background {BACKGROUND_PER_CELL}/cell, "
          f"star ~{STAR_MASS} concentrated in {STAR_CELLS} cells)")

    E, received = init_state(N_NODES, n_directed, energy_init)

    log = []
    t0 = time.time()
    snapshot_ticks = [10, 100, 500, 1000, 2500, 5000, 7500, 10000]

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)

        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}: {total} != {total_initial}")

        if t in snapshot_ticks or t % 1000 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.99)
            if clusters:
                top = clusters[0]
                star_centroid = top['centroid']
                star_observed_mass = top['mass']
                star_drift = float(np.linalg.norm(np.array(star_centroid) - STAR_CENTER))
            else:
                star_centroid = (None, None, None)
                star_observed_mass = 0
                star_drift = float('nan')

            summary = per_tick_summary(E, src)
            summary['tick'] = t
            summary['star_centroid'] = star_centroid
            summary['star_observed_mass'] = star_observed_mass
            summary['star_drift'] = star_drift
            log.append(summary)

            elapsed = time.time() - t0
            rate = t / elapsed
            print(f"  tick {t:>6d} star_mass={star_observed_mass:>5d} "
                  f"drift={star_drift:.4f} max_E={summary['max_E']} "
                  f"({rate:.0f} t/s)")

    # Final field-slope measurement
    r_centers, density = radial_density_profile(E, coords, STAR_CENTER, n_bins=25)
    slope, intercept, r2 = fit_loglog_slope(r_centers, density)
    print(f"\nField slope = {slope:.3f}  (target: ~ -2.0, 128 v11 ref: -1.968)  r²={r2:.3f}")

    # Persistence verdict
    final_top = cluster_high_energy(E, coords, threshold_quantile=0.99)
    persisted = bool(final_top) and final_top[0]['mass'] >= 0.5 * STAR_MASS

    print(f"Star persistence: {persisted} (final mass: {final_top[0]['mass'] if final_top else 0})")

    # Save outputs
    with open(os.path.join(OUT_DIR, 'phase2_log.json'), 'w') as f:
        json.dump(log, f, indent=2)

    plot_radial_profile(
        r_centers, density, slope=slope,
        out_path=os.path.join(OUT_DIR, 'phase2_field.png'),
        title=f'Phase 2: field, slope={slope:.3f}',
    )

    print(f"\nSummary written to {OUT_DIR}/phase2_log.json")
    print(f"Field plot: {OUT_DIR}/phase2_field.png")

    # Phase 2 verdict per spec §5
    if persisted and -2.3 < slope < -1.7:
        print("\nPhase 2 PASS: star persists + field is 1/r²-shaped.")
    else:
        print("\nPhase 2 ATTENTION: see falsification matrix in spec §8.")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run Phase 2**

```bash
cd experiments/133_closed_loop_substrate
python -u phase2_static_star.py 2>&1 | tee results/phase2.log
```

Expected (if rule works):
- Conservation passes every tick
- Star persists with most of its mass after 10k ticks
- `slope` between roughly −1.7 and −2.3

If star dissolves or slope is way off, consult spec §8 falsification matrix and either:
- Tune α (try 0.5, 2.0, 5.0)
- Increase STAR_MASS
- Investigate: is firing too sparse? (look at `n_firing_cells` log)

Don't proceed to Phase 3 until Phase 2 passes.

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/phase2_static_star.py \
        experiments/133_closed_loop_substrate/results/phase2*
git commit -m "experiment 133: phase 2 — static star and field formation"
```

---

## Task 9: Phase 3 driver — test pattern in field

**Files:**
- Create: `experiments/133_closed_loop_substrate/phase3_test_pattern.py`

Spec §5 Phase 3: Phase 2's star + small test pattern (10–50 quanta) seeded at hop-distance ~30; measure drift toward star matches local gradient.

- [ ] **Step 1: Implement phase3_test_pattern.py**

Write `experiments/133_closed_loop_substrate/phase3_test_pattern.py`:

```python
#!/usr/bin/env python3
"""Phase 3: Test pattern in field.

Per spec §5 Phase 3:
  - Phase 2 setup + small test pattern (10-50 quanta) at hop ~30 from star
  - run 5k ticks
  - measure: does test pattern's centroid drift toward star?
  - measure: drift consistent with local field gradient (Newton's 2nd)?

Success: test pattern accelerates toward star matching field. Gravity earned.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary, cluster_high_energy
from visualization import plot_trajectory


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 5_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
PLANET_CENTER = np.array([0.7, 0.5, 0.5])  # offset radially from star
STAR_MASS = 1000
PLANET_MASS = 30
STAR_CELLS = 50
PLANET_CELLS = 5
BACKGROUND_PER_CELL = 20
ALPHA = 1.0  # match Phase 2 winning value

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 3: test pattern in field, alpha={ALPHA}")

    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)

    # Seed star
    d_star = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:STAR_CELLS]

    # Seed planet
    d_planet = np.linalg.norm(coords - PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:PLANET_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS
    energy_init[planet_idx] += PLANET_MASS // PLANET_CELLS

    total_initial = int(energy_init.sum())
    print(f"  total energy: {total_initial}")

    E, received = init_state(N_NODES, n_directed, energy_init)

    planet_positions = []  # (T, 3) trajectory of planet centroid
    log = []
    t0 = time.time()

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 50 == 0 or t == 1:
            # Identify clusters; planet is the second-most-massive (star is first)
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.99)
            planet_centroid = None
            if len(clusters) >= 2:
                planet_centroid = clusters[1]['centroid']
            elif len(clusters) == 1:
                # If clusters merged, treat the only cluster's centroid as planet position
                planet_centroid = clusters[0]['centroid']

            if planet_centroid is not None:
                planet_positions.append(planet_centroid)

            if t % 500 == 0:
                summary = per_tick_summary(E, src)
                summary['tick'] = t
                if planet_centroid is not None:
                    summary['planet_centroid'] = planet_centroid
                    summary['planet_distance_from_star'] = float(
                        np.linalg.norm(np.array(planet_centroid) - STAR_CENTER)
                    )
                log.append(summary)
                rate = t / (time.time() - t0)
                pd = summary.get('planet_distance_from_star', float('nan'))
                print(f"  tick {t:>5d} planet_dist={pd:.4f} max_E={summary['max_E']} "
                      f"({rate:.0f} t/s)")

    # Verdict: did the planet drift toward the star?
    if planet_positions:
        planet_positions = np.array(planet_positions)
        initial_dist = np.linalg.norm(planet_positions[0] - STAR_CENTER)
        final_dist = np.linalg.norm(planet_positions[-1] - STAR_CENTER)
        drift = initial_dist - final_dist
        print(f"\nInitial distance to star: {initial_dist:.4f}")
        print(f"Final distance to star:   {final_dist:.4f}")
        print(f"Drift (positive = inward): {drift:+.4f}")

        if drift > 0.01:
            print("Phase 3 PASS: test pattern drifted toward star (gravity-like response).")
        elif drift > 0:
            print("Phase 3 WEAK: small drift toward star, gradient response detected but weak.")
        else:
            print("Phase 3 ATTENTION: planet did not drift toward star — see spec §8.")
    else:
        print("Phase 3 FAIL: planet cluster not identifiable.")

    # Save outputs
    with open(os.path.join(OUT_DIR, 'phase3_log.json'), 'w') as f:
        json.dump(log, f, indent=2)
    if planet_positions is not None and len(planet_positions) > 0:
        plot_trajectory(
            planet_positions, star_pos=STAR_CENTER,
            out_path=os.path.join(OUT_DIR, 'phase3_drift.png'),
            title='Phase 3: planet drift in field',
        )


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run Phase 3**

```bash
cd experiments/133_closed_loop_substrate
python -u phase3_test_pattern.py 2>&1 | tee results/phase3.log
```

Expected: drift > 0 (planet moves toward star).

If planet doesn't drift, falsification matrix says either field is too weak or pattern coherence is too low. Check Phase 2 slope more carefully.

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/phase3_test_pattern.py \
        experiments/133_closed_loop_substrate/results/phase3*
git commit -m "experiment 133: phase 3 — test pattern drift toward star"
```

---

## Task 10: Phase 4 driver — orbit (the goal)

**Files:**
- Create: `experiments/133_closed_loop_substrate/phase4_orbit.py`

Spec §5 Phase 4: Phase 3 setup + tangential bias on planet (initial wake-bias state non-zero in tangential direction); seek closed orbit + Keplerian T² ∝ a³.

The seeded tangential bias is implemented by initializing `received` with non-zero values on the planet cells' edges in the chosen tangential direction.

- [ ] **Step 1: Implement phase4_orbit.py**

Write `experiments/133_closed_loop_substrate/phase4_orbit.py`:

```python
#!/usr/bin/env python3
"""Phase 4: Orbit — the goal.

Per spec §5 Phase 4:
  - Phase 3 setup
  - tangential bias seeded on planet (initial wake-bias state biased tangentially)
  - run for several orbital periods
  - measure: closed trajectory, T² ∝ a³, coherence over many orbits

Success: stable Keplerian orbit within 5–10%. The weekend goal.
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from metrics import per_tick_summary, cluster_high_energy
from visualization import plot_trajectory


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 30_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
PLANET_CENTER = np.array([0.7, 0.5, 0.5])
STAR_MASS = 1000
PLANET_MASS = 30
STAR_CELLS = 50
PLANET_CELLS = 5
BACKGROUND_PER_CELL = 20
ALPHA = 1.0

# Tangential direction (perpendicular to star→planet vector, in xy plane)
TANGENT = np.array([0.0, 1.0, 0.0])
TANGENT_BIAS_QUANTA = 50  # quanta to seed in tangential direction per planet cell

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def seed_tangential_bias(received, planet_idx, src, dst, coords, tangent, mass_per_cell):
    """For each planet cell, seed non-zero `received` on the edge most aligned with `tangent`.

    This puts the wake-bias machinery in a state where the planet 'just received'
    energy from the trailing direction, so its first-tick outflow biases tangentially-forward.
    """
    for cell in planet_idx:
        # Find directed edges incoming to this cell
        in_edges = np.where(dst == cell)[0]
        if len(in_edges) == 0:
            continue

        # For each incoming edge, the source-to-cell vector
        sources = src[in_edges]
        directions = coords[cell] - coords[sources]
        norms = np.linalg.norm(directions, axis=1)
        norms = np.where(norms > 0, norms, 1)
        directions = directions / norms[:, None]

        # Pick the edge whose incoming direction best aligns with `tangent`.
        # (We want energy "to be coming from behind" relative to forward = tangent.)
        alignment = directions @ tangent
        best = int(np.argmax(alignment))
        received[in_edges[best]] += mass_per_cell


def main():
    rng = np.random.default_rng(SEED)
    print(f"Phase 4: orbit, alpha={ALPHA}, tangent_bias={TANGENT_BIAS_QUANTA}")

    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)

    d_star = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:STAR_CELLS]

    d_planet = np.linalg.norm(coords - PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:PLANET_CELLS]

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += STAR_MASS // STAR_CELLS
    energy_init[planet_idx] += PLANET_MASS // PLANET_CELLS

    total_initial = int(energy_init.sum())

    E, received = init_state(N_NODES, n_directed, energy_init)

    # Seed tangential bias by editing `received` directly
    seed_tangential_bias(received, planet_idx, src, dst, coords, TANGENT,
                         mass_per_cell=TANGENT_BIAS_QUANTA)
    # The bias adds to total energy via the wake mechanism, so update budget assertion baseline
    # — actually no: `received` is wake-history, not actual energy. Energy balance unaffected.

    planet_positions = []
    t0 = time.time()
    log = []

    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 25 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.995)
            if len(clusters) >= 2:
                planet_centroid = clusters[1]['centroid']
                planet_positions.append((t, planet_centroid))

            if t % 500 == 0:
                rate = t / (time.time() - t0)
                if planet_positions:
                    last_pos = np.array(planet_positions[-1][1])
                    dist = float(np.linalg.norm(last_pos - STAR_CENTER))
                else:
                    dist = float('nan')
                print(f"  tick {t:>6d} planet_dist={dist:.4f} ({rate:.0f} t/s)")

    # Save trajectory
    if planet_positions:
        traj = np.array([p[1] for p in planet_positions])
        ticks_at = np.array([p[0] for p in planet_positions])

        # Detect orbit: does trajectory return near start?
        start_pos = traj[0]
        distances_from_start = np.linalg.norm(traj - start_pos, axis=1)
        # First tick where it returns within 0.05 of start (after at least 100 ticks of motion)
        returned = np.where((distances_from_start < 0.05) & (ticks_at > ticks_at[0] + 1000))[0]
        period_ticks = ticks_at[returned[0]] if len(returned) > 0 else None

        plot_trajectory(traj, star_pos=STAR_CENTER,
                        out_path=os.path.join(OUT_DIR, 'phase4_orbit.png'),
                        title=f'Phase 4: orbit trajectory ({len(traj)} samples)')

        with open(os.path.join(OUT_DIR, 'phase4_traj.json'), 'w') as f:
            json.dump({
                'ticks': ticks_at.tolist(),
                'positions': traj.tolist(),
                'period_ticks': int(period_ticks) if period_ticks is not None else None,
            }, f, indent=2)

        if period_ticks is not None:
            print(f"\nPhase 4: planet returned to start near tick {period_ticks} → orbit detected")
        else:
            print("\nPhase 4: no closed orbit detected within run length — increase ticks or tune α/tangent_bias")

    print("Phase 4 done.")


if __name__ == '__main__':
    main()
```

- [ ] **Step 2: Run Phase 4**

```bash
cd experiments/133_closed_loop_substrate
python -u phase4_orbit.py 2>&1 | tee results/phase4.log
```

This is the long run — 30k ticks. Expect tens of minutes wall-clock at 100k nodes.

Expected outcomes:
- Conservation passes
- Planet trajectory either:
  - **PASS:** closed orbit detected, trajectory plot shows ellipse
  - **FAIL — fall-in:** trajectory spirals into star
  - **FAIL — escape:** trajectory leaves region
  - **FAIL — no curve:** trajectory drifts straight

If FAIL, tune `TANGENT_BIAS_QUANTA` (try 20, 100, 200) or `ALPHA` (Phase 2's winning value may not be optimal here).

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/phase4_orbit.py \
        experiments/133_closed_loop_substrate/results/phase4*
git commit -m "experiment 133: phase 4 — orbital mechanics attempt"
```

If orbit succeeds: **the goal is reached.** Update memory.

---

## Task 11: Phase 5 driver — emergent orbit (stretch goal)

**Files:**
- Create: `experiments/133_closed_loop_substrate/phase5_emergent.py`

Spec §5 Phase 5: same setup as Phase 4 minus the tangential bias. Test whether orbit emerges from substrate dynamics alone.

- [ ] **Step 1: Implement phase5_emergent.py**

Write `experiments/133_closed_loop_substrate/phase5_emergent.py`:

```python
#!/usr/bin/env python3
"""Phase 5: Emergent orbit (stretch goal).

Per spec §5 Phase 5:
  - same setup as Phase 4 minus the seeded tangential bias
  - if a coherent orbit emerges anyway, renewal-not-identity is earned in
    the strongest possible sense

Don't be disappointed if this fails. Phase 4 success is already the weekend win.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import everything from phase4 and override TANGENT_BIAS_QUANTA to 0
import phase4_orbit
phase4_orbit.TANGENT_BIAS_QUANTA = 0
phase4_orbit.OUT_DIR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'results'
)


# Override the output filenames so we don't overwrite Phase 4 results
def _patched_main():
    # Re-run main with bias=0 and different output names
    import json
    import time
    import numpy as np
    from substrate import build_rgg, init_state, tick
    from metrics import per_tick_summary, cluster_high_energy
    from visualization import plot_trajectory

    p = phase4_orbit
    print(f"Phase 5 (emergent): alpha={p.ALPHA}, tangent_bias=0")

    coords, src, dst, back_edge = build_rgg(p.N_NODES, p.RADIUS, seed=p.SEED)
    n_directed = len(src)

    d_star = np.linalg.norm(coords - p.STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(d_star)[:p.STAR_CELLS]
    d_planet = np.linalg.norm(coords - p.PLANET_CENTER[None, :], axis=1)
    planet_idx = np.argsort(d_planet)[:p.PLANET_CELLS]

    energy_init = np.full(p.N_NODES, p.BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] += p.STAR_MASS // p.STAR_CELLS
    energy_init[planet_idx] += p.PLANET_MASS // p.PLANET_CELLS
    total_initial = int(energy_init.sum())

    E, received = init_state(p.N_NODES, n_directed, energy_init)
    # NO tangential bias seed

    planet_positions = []
    t0 = time.time()
    for t in range(1, p.N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=p.ALPHA)
        total = int(E.sum())
        if total != total_initial:
            raise AssertionError(f"CONSERVATION at tick {t}")

        if t % 25 == 0:
            clusters = cluster_high_energy(E, coords, threshold_quantile=0.995)
            if len(clusters) >= 2:
                planet_positions.append((t, clusters[1]['centroid']))
            if t % 500 == 0:
                rate = t / (time.time() - t0)
                print(f"  tick {t}, {rate:.0f} t/s")

    if planet_positions:
        traj = np.array([pp[1] for pp in planet_positions])
        plot_trajectory(traj, star_pos=p.STAR_CENTER,
                        out_path=os.path.join(p.OUT_DIR, 'phase5_emergent.png'),
                        title='Phase 5: emergent (no tangent bias)')
        with open(os.path.join(p.OUT_DIR, 'phase5_traj.json'), 'w') as f:
            json.dump({
                'ticks': [int(pp[0]) for pp in planet_positions],
                'positions': [list(pp[1]) for pp in planet_positions],
            }, f, indent=2)

    print("Phase 5 done.")


if __name__ == '__main__':
    _patched_main()
```

- [ ] **Step 2: Run Phase 5**

```bash
cd experiments/133_closed_loop_substrate
python -u phase5_emergent.py 2>&1 | tee results/phase5.log
```

Expected: most likely no orbit (radial fall-in or no motion). Document whatever happens — even a partial result is informative.

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/phase5_emergent.py \
        experiments/133_closed_loop_substrate/results/phase5*
git commit -m "experiment 133: phase 5 — emergent orbit (stretch)"
```

---

## Task 12: Closure document

**Files:**
- Create: `experiments/133_closed_loop_substrate/CLOSURE.md`

Whatever the phases produce — pass, partial, fail — capture findings, parameter sweep results, and falsification table per spec §8 in a closure doc. Even a failure is publishable when it pins down which commitment is wrong.

- [ ] **Step 1: Write the closure document**

The closure doc should contain:

```markdown
# Experiment 133 — Closure

**Started:** 2026-04-26
**Closed:** [DATE WHEN TASKS COMPLETE]
**Spec:** docs/superpowers/specs/2026-04-26-closed-loop-graph-substrate-design.md

## Phase outcomes

| Phase | Result | Notes |
|-------|--------|-------|
| 1 — Conservation/diffusion sanity | [PASS/FAIL] | [details] |
| 2 — Static star + 1/r² | [PASS/FAIL/PARTIAL] | slope = [X], target -2.0 |
| 3 — Test pattern drift | [PASS/FAIL/PARTIAL] | drift = [X] |
| 4 — Orbit | [PASS/FAIL] | period = [X] ticks if PASS |
| 5 — Emergent orbit | [PASS/FAIL] | stretch goal |

## Parameter sweep
α values tried: ...
N_NODES tried: ...
TANGENT_BIAS_QUANTA tried: ...

## Falsification matrix (from spec §8)
[Map outcomes to spec's matrix and identify which row applies]

## Conclusion
[What did we earn? What broke? What does this tell us about the ontological commitments?]

## Next experiment
[If applicable: what's the next test, given what we learned]
```

Fill in the placeholders based on actual run outputs.

- [ ] **Step 2: Update memory**

If Phase 4 passed, write a project memory entry:
- File: `C:\Users\tomas\.claude\projects\W--workspace-tick-frame-space\memory\project_133_orbit_earned.md`
- Update: `MEMORY.md` index

If Phase 4 failed, write a closure memory:
- File: `project_133_closed_loop_closure.md`
- Capture which commitment broke per falsification matrix

- [ ] **Step 3: Commit**

```bash
git add experiments/133_closed_loop_substrate/CLOSURE.md
# also memory updates if applicable
git commit -m "experiment 133: closure"
```

---

## Self-Review Checklist

Before declaring this plan ready:

**Spec coverage:**
- §2 Ontological commitments → encoded in code by §3 (no coords stored), §4 (rule structure), tests for conservation/symmetry — ✓
- §3 Substrate spec → Task 2 (RGG), Task 3 (state) — ✓
- §4 Tick rule → Task 4 (vectorized tick) — ✓
- §5 Test plan, all 5 phases → Tasks 7–11 — ✓
- §6 Out of scope → not implemented (correctly) — ✓
- §8 Falsification matrix → referenced in each phase, applied in Task 12 — ✓

**No placeholders:** all tasks have full code; falsification responses noted; no "implement appropriate handling" — ✓

**Type consistency:** `E`, `received`, `src`, `dst`, `back_edge` consistent across all tasks — ✓

**File responsibilities:** substrate.py = pure mechanics; metrics/visualization = analyst-side; phase drivers = experiment specifics — ✓

**Frequent commits:** every task ends with a commit — ✓

---
