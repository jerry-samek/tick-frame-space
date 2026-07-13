"""Sanity tests for Exp 137 instrument code (run before Phase 0)."""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from graphs import torus3d, torus2d, random_regular, binary_tree, bfs_distances, sample_bundle
from readout import dpr, dpr_raw, dpr_sub, mds_dim90_from_dist, corrmat
from dynamics import walk_matrix, run_ar1


def test_torus3d_degrees_and_ball():
    adj = torus3d(12)
    assert len(adj) == 1728
    assert all(len(set(nbrs)) == 6 for nbrs in adj)
    # von Neumann ball r=1 in 3D = center + 6
    assert len(bfs_distances(adj, 0, cutoff=1)) == 7


def test_torus2d_degrees():
    adj = torus2d(42)
    assert len(adj) == 1764
    assert all(len(set(nbrs)) == 4 for nbrs in adj)


def test_random_regular_simple_connected():
    adj = random_regular(1750, 3, np.random.default_rng(0))
    assert len(adj) == 1750
    assert all(len(nbrs) == 3 and len(set(nbrs)) == 3 for nbrs in adj)
    assert len(bfs_distances(adj, 0)) == 1750


def test_binary_tree():
    adj = binary_tree(10)
    assert len(adj) == 2047
    assert len(adj[0]) == 2  # root
    assert len(adj[2046]) == 1  # leaf


def test_dpr_identity_and_uniform():
    n = 64
    assert dpr_raw(np.eye(n)) == pytest.approx(n)
    # uniform correlation rho: eigs are 1+(n-1)rho and (1-rho) x (n-1)
    rho = 0.5
    c = np.full((n, n), rho)
    np.fill_diagonal(c, 1.0)
    top = 1 + (n - 1) * rho
    expected = n * n / (top**2 + (n - 1) * (1 - rho) ** 2)
    assert dpr_raw(c) == pytest.approx(expected)
    # removing the global mode of the uniform matrix leaves a flat spectrum
    assert dpr_sub(c) == pytest.approx(n - 1)


def test_mds_dim90_recovers_cloud_dimension():
    rng = np.random.default_rng(1)
    for k in (2, 3):
        pts = rng.standard_normal((200, k))
        d = np.linalg.norm(pts[:, None, :] - pts[None, :, :], axis=2)
        assert mds_dim90_from_dist(d) == k


def test_walk_matrix_rows_sum_to_one():
    adj = torus2d(6)
    p = walk_matrix(adj)
    assert np.allclose(np.asarray(p.sum(axis=1)).ravel(), 1.0)


def test_dynamics_shape_and_correlation_positive_control():
    adj = torus2d(20)
    rng = np.random.default_rng(2)
    center, taps, _ = sample_bundle(adj, 16, 4, rng)
    x = run_ar1(adj, taps, burn=200, steps=2000, rng=rng)  # frozen defaults (lazy walk, lam=0.99)
    assert x.shape == (2000, 16)
    c = corrmat(x)
    # neighbors on the lattice must correlate more than distant taps on average
    dist = bfs_distances(adj, int(taps[0]))
    near = [abs(c[0, i]) for i in range(1, 16) if dist[int(taps[i])] <= 2]
    far = [abs(c[0, i]) for i in range(1, 16) if dist[int(taps[i])] >= 6]
    if near and far:
        assert np.mean(near) > np.mean(far)
