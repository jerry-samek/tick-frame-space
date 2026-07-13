# experiments/132_grow_until_observed/phase2a5_analysis.py
"""Phase 2A.5 superposition analysis.

Given thresholds and loads from three runs (R1 planet-only, R2 test-only,
R3 combined), test whether R3 - R2 ≈ R1 — i.e., self-subtracting transport
holds.

Reports linearity statistic χ², monotonicity of entity-relative profiles,
and outcome category (1, 2, or 3 per spec).
"""
import math
from collections import defaultdict


def linearity_statistic(r1: dict, r2: dict, r3: dict) -> float:
    """χ² = sum over cells of (R3[c] - R2[c] - R1[c])^2 / (R1[c]+1)^2.

    The +1 in the denominator avoids divide-by-zero for cells with R1[c]=0.
    Both r1, r2, r3 are dicts mapping cell positions to values.
    """
    total = 0.0
    n = 0
    for cell in r1:
        v1 = r1.get(cell, 0)
        v2 = r2.get(cell, 0)
        v3 = r3.get(cell, 0)
        denom = (v1 + 1.0) ** 2
        total += (v3 - v2 - v1) ** 2 / denom
        n += 1
    return total / n if n > 0 else 0.0


def entity_relative_profile(
    r3: dict, r2: dict, center: tuple
) -> dict:
    """Compute (R3 - R2)(r) profile from given center.
    Returns dict mapping integer-distance bin to mean of (R3[c] - R2[c]) over cells at that bin.
    """
    bins = defaultdict(list)
    all_cells = set(r3.keys()) | set(r2.keys())
    for cell in all_cells:
        # Connector keys are pairs of cell positions; reduce to midpoint.
        if isinstance(cell[0], tuple):
            a, b = cell
            pos = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
        else:
            pos = cell
        dist = math.sqrt(sum((pos[i] - center[i]) ** 2 for i in range(3)))
        bin_idx = int(dist)
        bins[bin_idx].append(r3.get(cell, 0) - r2.get(cell, 0))
    return {d: sum(vs) / len(vs) for d, vs in bins.items() if vs}


def is_monotonic_decreasing(profile: dict) -> bool:
    """Check if profile values decrease monotonically with distance bin."""
    sorted_radii = sorted(profile.keys())
    if len(sorted_radii) < 2:
        return True
    return all(profile[a] >= profile[b] for a, b in zip(sorted_radii, sorted_radii[1:]))
