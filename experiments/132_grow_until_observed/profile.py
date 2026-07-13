# experiments/132_grow_until_observed/profile.py
"""Post-hoc analysis: threshold(r) and load(r) radial profiles."""
import math
from collections import defaultdict

CellPos = tuple[int, int, int]
ConnectorKey = tuple[CellPos, CellPos]


def _distance(a: tuple[float, float, float], b: tuple[float, float, float]) -> float:
    return math.sqrt(sum((a[i] - b[i]) ** 2 for i in range(3)))


def threshold_profile(
    thresholds: dict[CellPos, float],
    center: tuple[float, float, float],
) -> dict[int, float]:
    """Average threshold over cells, binned by integer distance from center.

    Returns: {distance_bin: mean_threshold}
    """
    bins: dict[int, list[float]] = defaultdict(list)
    for pos, thr in thresholds.items():
        dist = _distance(pos, center)
        bins[int(dist)].append(thr)
    return {d: sum(vs) / len(vs) for d, vs in bins.items() if vs}


def load_profile(
    loads: dict[ConnectorKey, int],
    center: tuple[float, float, float],
) -> dict[int, float]:
    """Average connector load, binned by integer distance from center
    using the connector's midpoint as its position.

    Returns: {distance_bin: mean_load}
    """
    bins: dict[int, list[int]] = defaultdict(list)
    for (a, b), load in loads.items():
        midpoint = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
        dist = _distance(midpoint, center)
        bins[int(dist)].append(load)
    return {d: sum(vs) / len(vs) for d, vs in bins.items() if vs}
