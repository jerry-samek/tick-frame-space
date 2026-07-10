import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from instrument import shell_counts, fit_exponent, classify  # noqa: E402
from graphs import torus3d, torus2d, binary_tree, random_regular  # noqa: E402


def test_torus3d_is_polynomial_exponent_2():
    adj = torus3d(10)
    nbar = shell_counts(adj, sources=list(range(0, 1000, 20)))
    f = fit_exponent(nbar)
    assert f["cls"] == "poly"
    assert 1.6 < f["e_hat"] < 2.4


def test_torus2d_is_polynomial_exponent_1():
    adj = torus2d(24)
    nbar = shell_counts(adj, sources=list(range(0, 576, 12)))
    f = fit_exponent(nbar)
    assert f["cls"] == "poly"
    assert 0.7 < f["e_hat"] < 1.3


def test_tree_is_exponential():
    adj = binary_tree(10)
    nbar = shell_counts(adj, sources=[0])
    f = fit_exponent(nbar)
    assert f["cls"] == "exp"
    assert f["rate_exp"] > 0.3


def test_expander_is_exponential():
    rng = np.random.default_rng(0)
    adj = random_regular(1728, 6, rng)
    f = classify(adj, rng)
    assert f["cls"] == "exp"
    assert f["rate_exp"] > 0.3


def test_classify_is_seed_deterministic():
    adj = torus3d(8)
    a = classify(adj, np.random.default_rng(5))
    b = classify(adj, np.random.default_rng(5))
    assert a == b
