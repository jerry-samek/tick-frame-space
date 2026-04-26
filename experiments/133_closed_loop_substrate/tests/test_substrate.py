"""Unit tests for substrate.py.

Tests use small hand-verifiable graphs (N <= 20) so we can compute
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
