import numpy as np
import networkx as nx
import battery as B
from nulls import poisson_3d, grid_2d, random_tree


def _dominance_poset(n, dim, seed):
    rng = np.random.default_rng(seed)
    X = rng.random((n, dim))
    rel = {i: set() for i in range(n)}
    for i in range(n):
        dom = np.all(X >= X[i], axis=1) & np.any(X > X[i], axis=1)
        for j in np.nonzero(dom)[0]:
            if j != i:
                rel[i].add(int(j))
    return rel


# --- Hausdorff ---
# NOTE: graph dimension estimators read ~0.4-0.5 LOW in absolute terms on finite graphs
# (a known bias). Bands are the CALIBRATED references (Poisson-3D ~2.5), frozen at the gate;
# WIN is benchmark-relative per spec section 9, not absolute 3.0.
def test_hausdorff_3d_calibrated():
    g, _ = poisson_3d(8000, seed=1)
    assert 2.2 <= B.hausdorff_dim(g) <= 3.2

def test_hausdorff_grid_near_2():
    assert 1.5 <= B.hausdorff_dim(grid_2d(80)) <= 2.2


# --- spectral ---
def test_spectral_3d_calibrated():
    g, _ = poisson_3d(8000, seed=1)
    assert 2.2 <= B.spectral_dim(g) <= 3.2

def test_spectral_tree_low():
    assert B.spectral_dim(random_tree(5000, seed=2)) <= 1.6


# --- poset ordering dim (dominance) ---
def test_poset_dim_2d_near_2():
    assert 1.6 <= B.poset_ordering_dim(_dominance_poset(600, 2, 0)) <= 2.4

def test_poset_dim_3d_near_3():
    assert 2.5 <= B.poset_ordering_dim(_dominance_poset(800, 3, 0)) <= 3.6


# --- loops / dirichlet ---
def test_loop_density_tree_zero_grid_positive():
    assert B.loop_density(random_tree(500, seed=0)) == 0.0
    assert B.loop_density(grid_2d(20)) > 0.0

def test_dirichlet_zero_on_constant_field():
    g = grid_2d(10)
    assert B.dirichlet_energy(g, {u: 1.0 for u in g}) == 0.0


# --- ricci ---
# Calibration finding: Ollivier-Ricci edge-MEDIAN flags POSITIVE curvature (clustered/complete)
# vs FLAT (~0); it does NOT flag sparse trees as negative (pendant edges dominate, ~0 median).
# Tree/hyperbolic detection therefore relies on spectral-dim + loop-density, not Ricci.
def test_ricci_complete_positive():
    assert B.ricci_summary(nx.complete_graph(12))["median"] > 0.2

def test_ricci_grid_flat():
    assert -0.25 <= B.ricci_summary(grid_2d(25))["median"] <= 0.25


# --- betti ---
def test_betti_solid_ball():
    rng = np.random.default_rng(0); X = []
    while len(X) < 600:
        p = rng.uniform(-1, 1, 3)
        if np.linalg.norm(p) <= 1:
            X.append(p)
    b = B.betti_from_points(np.array(X), max_edge=0.5)
    assert b[0] == 1 and b[1] == 0
