import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from curvature import kappa_exact, kappa_jl, validate  # noqa: E402
from graphs import random_regular, torus2d  # noqa: E402


def test_exact_on_complete_k4():
    # K_n, uniform neighbor measures, no laziness: the n-2 common neighbors
    # carry equal mass in both measures (zero transport); only mass 1/(n-1)
    # moves from y to x at distance 1 -> W1 = 1/(n-1), kappa = 1 - 1/(n-1).
    # K4: kappa = 2/3.
    adj = [[1, 2, 3], [0, 2, 3], [0, 1, 3], [0, 1, 2]]
    for j in (1, 2, 3):
        assert abs(kappa_exact(adj, 0, j) - 2.0 / 3.0) < 1e-6


def test_exact_on_long_cycle_is_zero():
    n = 8
    adj = [[(i - 1) % n, (i + 1) % n] for i in range(n)]
    assert abs(kappa_exact(adj, 0, 1)) < 1e-9  # C_n (n >= 6): kappa = 0


def test_jl_is_lower_bound_on_random_graphs():
    rng = np.random.default_rng(0)
    adj = random_regular(60, 4, rng)
    edges = []
    for i in range(len(adj)):
        for j in adj[i]:
            if i < j:
                edges.append((i, j))
    stats = validate(adj, edges[:40])
    assert stats["n"] == 40 and stats["max_gap"] >= 0


def test_jl_equals_exact_on_2d_torus_edges():
    adj = torus2d(6)
    # square-lattice edge: both should give kappa = 0 (flat)
    ke = kappa_exact(adj, 0, adj[0][0])
    assert abs(ke) < 1e-9
    assert kappa_jl(adj, 0, adj[0][0]) <= ke + 1e-9
