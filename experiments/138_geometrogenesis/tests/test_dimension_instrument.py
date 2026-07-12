import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))
from dimension_instrument import short_cycle_density, classify_dimension
from graphs import torus2d, random_regular

def test_lattice_reads_manifold():
    r = classify_dimension(torus2d(24), np.random.default_rng(0))
    assert r["is_manifold"] is True
    assert r["cyc_density"] > 0.5  # square lattice: ~1 four-cycle per node

def test_random_regular_is_not_manifold():
    rng = np.random.default_rng(1)
    r = classify_dimension(random_regular(1728, 4, rng), rng)
    assert r["is_manifold"] is False  # the P1c null: d_s alone would say ~2
    assert r["cyc_density"] < 0.2     # locally tree-like

def test_classify_is_seed_deterministic():
    a = classify_dimension(torus2d(16), np.random.default_rng(5))
    b = classify_dimension(torus2d(16), np.random.default_rng(5))
    assert a == b
