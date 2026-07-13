# experiments/132_grow_until_observed/tests/test_phase2a5_analysis.py
"""Unit tests for phase2a5_analysis."""
import pytest
from phase2a5_analysis import (
    entity_relative_profile,
    is_monotonic_decreasing,
    linearity_statistic,
)


def test_linearity_statistic_zero_when_perfect_superposition():
    """If R3 = R1 + R2 exactly at every cell, χ² = 0."""
    r1 = {(0, 0, 0): 5.0, (1, 0, 0): 3.0, (2, 0, 0): 1.0}
    r2 = {(0, 0, 0): 2.0, (1, 0, 0): 2.0, (2, 0, 0): 2.0}
    r3 = {(0, 0, 0): 7.0, (1, 0, 0): 5.0, (2, 0, 0): 3.0}
    assert linearity_statistic(r1, r2, r3) == pytest.approx(0.0)


def test_linearity_statistic_nonzero_when_violation():
    """If R3 deviates from R1+R2, χ² > 0."""
    r1 = {(0, 0, 0): 5.0, (1, 0, 0): 3.0}
    r2 = {(0, 0, 0): 2.0, (1, 0, 0): 2.0}
    # R3 differs from R1+R2 by +1 at each cell
    r3 = {(0, 0, 0): 8.0, (1, 0, 0): 6.0}
    chi2 = linearity_statistic(r1, r2, r3)
    assert chi2 > 0.0


def test_is_monotonic_decreasing_simple():
    """Simple monotonic and non-monotonic profiles."""
    assert is_monotonic_decreasing({0: 10.0, 1: 8.0, 2: 5.0, 3: 1.0})
    assert not is_monotonic_decreasing({0: 10.0, 1: 12.0, 2: 5.0})
    # Single-point and empty are trivially monotonic.
    assert is_monotonic_decreasing({})
    assert is_monotonic_decreasing({0: 5.0})


def test_entity_relative_profile_basic():
    """Two-cell example: difference (R3-R2) at distances 0 and 1 from origin."""
    r3 = {(0, 0, 0): 10.0, (1, 0, 0): 6.0}
    r2 = {(0, 0, 0): 4.0, (1, 0, 0): 2.0}
    profile = entity_relative_profile(r3, r2, center=(0.0, 0.0, 0.0))
    assert profile[0] == pytest.approx(6.0)
    assert profile[1] == pytest.approx(4.0)
