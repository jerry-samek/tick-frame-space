"""CALIBRATION GATE (spec section 9 / PREREG A.3).

The battery must SEPARATE the geometries: Poisson-3D (positive benchmark) reads distinctly
higher-dimensional than the 2D grid and the Eden blob; the tree is isolated by loop-density
(~0) and lowest spectral dim; the diffusion field is caught by Dirichlet-energy collapse.

If this fails, instruments are NOT trusted and no substrate result counts. Frozen at the gate.
Reference values (calibrated 2026-06-05): Poisson-3D d_s~2.5, d_H~2.6 (estimators read ~0.5 low;
WIN is benchmark-relative, not absolute 3.0).
"""
import networkx as nx
import battery as B
from nulls import poisson_3d, grid_2d, random_tree, eden_blob, diffusion_field


def test_gate_separates_3d_2d_tree_blob():
    g3, _ = poisson_3d(8000, seed=1)
    g2 = grid_2d(80)
    gt = random_tree(5000, seed=7)
    gb = eden_blob(4000, seed=7)
    r3, r2, rt, rb = (B.run_battery(g) for g in (g3, g2, gt, gb))

    # positive benchmark sits in the calibrated 3D band
    assert 2.2 <= r3["d_spectral"] <= 3.2
    assert 2.2 <= r3["d_hausdorff"] <= 3.2
    # 3D distinctly above 2D and the blob (margin > 0.4 on spectral)
    assert r3["d_spectral"] - r2["d_spectral"] > 0.4
    assert r3["d_spectral"] - rb["d_spectral"] > 0.4
    # tree isolated: ~no loops + lowest spectral; 2D/3D have loops
    assert rt["loop_density"] < 0.05
    assert r2["loop_density"] > 0.3 and r3["loop_density"] > 0.3
    assert rt["d_spectral"] < 1.6
    # 3D and 2D read flat (Ollivier-Ricci ~0)
    assert abs(r3["ricci_median"]) < 0.2


def test_gate_diffusion_oversmoothing_detected():
    g, pts, x = diffusion_field(3000, seed=7, steps=300)
    fresh = {u: 0.0 for u in g.nodes()}
    fresh[list(g.nodes())[0]] = 1.0
    # a homogenized field has near-zero Dirichlet energy vs a fresh point-source field
    assert B.dirichlet_energy(g, x) < 0.01 * B.dirichlet_energy(g, fresh)
