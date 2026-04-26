"""Unit tests for substrate.py.

Tests use small hand-verifiable graphs (N <= 20) so we can compute
expected outputs by hand. The vectorized implementation must match.
"""

import numpy as np
import pytest

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from substrate import build_rgg, init_state


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
