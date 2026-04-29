# experiments/132_grow_until_observed/tests/test_observer.py
from observer import (
    centroid_recent,
    centroid_threshold_elevated,
    peak_density_map,
    centroid_connected_firing,
)


def test_centroid_recent_simple():
    """4 firings of a 2x2 square at z=0, all in last N ticks - centroid is (0.5, 0.5, 0)."""
    firings = [
        (1, (0, 0, 0)),
        (2, (1, 0, 0)),
        (3, (1, 1, 0)),
        (4, (0, 1, 0)),
    ]
    centroid = centroid_recent(firings, current_tick=4, window=4)
    assert centroid == (0.5, 0.5, 0.0)


def test_centroid_recent_window_excludes_old():
    """Firings outside window are excluded."""
    firings = [
        (1, (10, 10, 10)),  # too old
        (5, (0, 0, 0)),
        (5, (2, 0, 0)),
    ]
    centroid = centroid_recent(firings, current_tick=5, window=4)
    assert centroid == (1.0, 0.0, 0.0)


def test_centroid_recent_empty_returns_none():
    centroid = centroid_recent([], current_tick=10, window=4)
    assert centroid is None


def test_centroid_threshold_elevated():
    """Cells with threshold > baseline by elevation_threshold contribute."""
    cell_thresholds = {
        (0, 0, 0): 100.5,
        (1, 0, 0): 100.5,
        (5, 5, 5): 100.0,  # at baseline, excluded
    }
    centroid = centroid_threshold_elevated(
        cell_thresholds, baseline=100.0, elevation_threshold=0.1
    )
    assert centroid == (0.5, 0.0, 0.0)


def test_centroid_threshold_elevated_no_elevated_cells():
    cell_thresholds = {(0, 0, 0): 100.0, (1, 0, 0): 100.0}
    centroid = centroid_threshold_elevated(
        cell_thresholds, baseline=100.0, elevation_threshold=0.1
    )
    assert centroid is None


def test_peak_density_map_simple():
    """4 firings in a tight cluster - peak should be near their centroid."""
    firings = [
        (10, (0, 0, 0)),
        (10, (1, 0, 0)),
        (10, (0, 1, 0)),
        (10, (1, 1, 0)),
    ]
    peak = peak_density_map(firings, current_tick=10, window=4, sigma=1.0)
    # Peak should be near (0.5, 0.5, 0); allow tolerance
    assert abs(peak[0] - 0.5) < 0.5
    assert abs(peak[1] - 0.5) < 0.5
    assert abs(peak[2] - 0.0) < 0.5


def test_centroid_connected_firing_finds_largest_cluster():
    """Two clusters: one of 3 cells, one of 1 cell. Largest is the 3-cluster."""
    firings = [
        (5, (0, 0, 0)),
        (5, (1, 0, 0)),
        (5, (2, 0, 0)),
        (5, (10, 10, 10)),  # isolated cell
    ]
    centroid = centroid_connected_firing(firings, current_tick=5, window=4)
    assert centroid == (1.0, 0.0, 0.0)
