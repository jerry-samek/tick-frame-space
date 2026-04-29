# experiments/132_grow_until_observed/tests/test_profile.py
import pytest
from profile import threshold_profile, load_profile


def test_threshold_profile_simple():
    """Cells at distances 0, 1, 1, 2 from center; thresholds 100.5, 100.2, 100.2, 100.0."""
    thresholds = {
        (0, 0, 0): 100.5,
        (1, 0, 0): 100.2,
        (-1, 0, 0): 100.2,
        (2, 0, 0): 100.0,
    }
    profile = threshold_profile(thresholds, center=(0.0, 0.0, 0.0))
    # Distance bins: 0 → [100.5], 1 → [100.2, 100.2], 2 → [100.0]
    assert profile[0] == pytest.approx(100.5)
    assert profile[1] == pytest.approx(100.2)
    assert profile[2] == pytest.approx(100.0)


def test_threshold_profile_excludes_unrequested_distances():
    """Only distances present in input are in the profile."""
    thresholds = {(5, 0, 0): 99.5}
    profile = threshold_profile(thresholds, center=(0.0, 0.0, 0.0))
    assert 5 in profile
    assert 0 not in profile


def test_load_profile_simple():
    """Connectors at distances 1.0, 1.5, 2.5 (using midpoint distance from center)."""
    loads = {
        ((0, 0, 0), (1, 0, 0)): 3,  # midpoint at (0.5, 0, 0), dist 0.5 from origin
        ((1, 0, 0), (2, 0, 0)): 2,  # midpoint at (1.5, 0, 0), dist 1.5
        ((2, 0, 0), (3, 0, 0)): 1,  # midpoint at (2.5, 0, 0), dist 2.5
    }
    profile = load_profile(loads, center=(0.0, 0.0, 0.0))
    # Should bin by integer-rounded distance
    # 0.5 → bin 0 or 1 depending on rounding convention; let's use floor: bin 0
    assert profile[0] == pytest.approx(3.0)
    assert profile[1] == pytest.approx(2.0)
    assert profile[2] == pytest.approx(1.0)


def test_load_profile_averages_within_bin():
    """Multiple connectors at same distance bin: averaged."""
    loads = {
        ((0, 0, 0), (1, 0, 0)): 3,  # dist 0
        ((0, 0, 0), (0, 1, 0)): 5,  # dist 0
    }
    profile = load_profile(loads, center=(0.0, 0.0, 0.0))
    assert profile[0] == pytest.approx(4.0)  # average of 3 and 5
