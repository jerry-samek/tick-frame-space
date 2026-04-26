"""Unit tests for substrate.py.

Tests use small hand-verifiable graphs (N <= 20) so we can compute
expected outputs by hand. The vectorized implementation must match.
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from substrate import build_rgg, init_state, tick


def test_build_rgg_basic_shapes():
    """RGG construction returns expected array shapes and dtypes."""
    coords, src, dst, back_edge = build_rgg(n_nodes=100, radius=0.2, seed=42)

    assert coords.shape == (100, 3)
    assert coords.dtype == np.float64

    # Directed edges: 2M entries (each undirected edge -> 2 directed)
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


def test_back_edge_swaps_src_dst():
    """back_edge[i] must point to the directed edge whose src/dst are swapped relative to i.

    This is stronger than the involution check — it locks down the contract that
    Task 4's tick rule depends on (received[back_edge[i]] = quanta arrived from
    the neighbor on edge i)."""
    coords, src, dst, back_edge = build_rgg(n_nodes=80, radius=0.25, seed=17)
    assert np.all(src[back_edge] == dst)
    assert np.all(dst[back_edge] == src)


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


def test_init_state_shape_mismatch():
    """init_state raises ValueError when energy_init shape mismatches n_nodes."""
    with pytest.raises(ValueError, match="energy_init shape"):
        init_state(n_nodes=20, n_directed=10, energy_init=np.zeros(19, dtype=np.int64))


def test_init_state_defensive_copy():
    """init_state copies energy_init so caller mutation does not bleed in."""
    energy_init = np.zeros(10, dtype=np.int64)
    energy_init[3] = 7
    E, _ = init_state(n_nodes=10, n_directed=20, energy_init=energy_init)
    energy_init[3] = 999  # mutate after the call
    assert E[3] == 7, "init_state must defensively copy energy_init"


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
        assert (E >= 0).all(), f"negative energy detected: min={E.min()}"


def test_tick_conservation_negative_alpha():
    """Conservation holds under α < 0 (a regime the experiment will sweep)."""
    rng = np.random.default_rng(789)
    coords, src, dst, back_edge = build_rgg(n_nodes=200, radius=0.18, seed=13)
    n_directed = len(src)

    energy_init = rng.integers(0, 100, size=200, dtype=np.int64)
    E, received = init_state(200, n_directed, energy_init)
    total_initial = E.sum()

    for _ in range(30):
        E, received = tick(E, received, src, dst, back_edge, alpha=-1.5)
        assert E.sum() == total_initial
        assert (E >= 0).all()


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
    # Star graph: 1 center + 3 leaves; 6 directed edges (3 undirected)
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
