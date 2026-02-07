"""Hex grid utilities using axial coordinates (pointy-top layout).

Coordinate system:
  (q, r) with implicit s = -q - r
  Storage: 2D array indexed as array[r + R, q + R] where R = world radius.
"""

import math
import numpy as np

# 6 axial direction vectors: E, NE, NW, W, SW, SE
HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

# Precomputed Cartesian unit vectors for each hex direction (pointy-top)
_SQRT3 = math.sqrt(3)
HEX_DIR_VECTORS = []
for dq, dr in HEX_DIRS:
    px = _SQRT3 * dq + _SQRT3 / 2 * dr
    py = 1.5 * dr
    mag = math.sqrt(px * px + py * py)
    if mag > 1e-12:
        HEX_DIR_VECTORS.append((px / mag, py / mag))
    else:
        HEX_DIR_VECTORS.append((0.0, 0.0))


def hex_to_pixel(q: int, r: int, size: float) -> tuple[float, float]:
    """Convert axial hex coords to screen pixel coords (pointy-top)."""
    x = size * (_SQRT3 * q + _SQRT3 / 2 * r)
    y = size * (1.5 * r)
    return x, y


def hex_distance(q1: int, r1: int, q2: int, r2: int) -> int:
    """Manhattan distance on hex grid."""
    dq = q1 - q2
    dr = r1 - r2
    ds = -dq - dr
    return max(abs(dq), abs(dr), abs(ds))


def hex_neighbors(q: int, r: int) -> list[tuple[int, int]]:
    """Return the 6 neighbor coordinates."""
    return [(q + dq, r + dr) for dq, dr in HEX_DIRS]


def hex_ring_cells(cq: int, cr: int, radius: int) -> list[tuple[int, int]]:
    """All cells at exactly `radius` distance from (cq, cr).
    Returns empty list for radius 0."""
    if radius <= 0:
        return [(cq, cr)] if radius == 0 else []
    cells = []
    # Start at the "bottom-left" corner of the ring
    q = cq + HEX_DIRS[4][0] * radius
    r = cr + HEX_DIRS[4][1] * radius
    for direction in range(6):
        for _ in range(radius):
            cells.append((q, r))
            q += HEX_DIRS[direction][0]
            r += HEX_DIRS[direction][1]
    return cells


def is_valid_hex(q: int, r: int, radius: int) -> bool:
    """Check if (q, r) is within the hexagonal world of given radius."""
    s = -q - r
    return max(abs(q), abs(r), abs(s)) <= radius


def rotate_cw(dir_idx: int) -> int:
    """Rotate direction index clockwise by 1 step."""
    return (dir_idx + 1) % 6


def rotate_ccw(dir_idx: int) -> int:
    """Rotate direction index counter-clockwise by 1 step."""
    return (dir_idx + 5) % 6


def hex_get(array: np.ndarray, q: int, r: int, radius: int) -> float:
    """Read value from hex array at axial coords."""
    return float(array[r + radius, q + radius])


def hex_set(array: np.ndarray, q: int, r: int, radius: int, val: float):
    """Set value in hex array at axial coords."""
    array[r + radius, q + radius] = val


def hex_add(array: np.ndarray, q: int, r: int, radius: int, val: float):
    """Add value to hex array at axial coords."""
    array[r + radius, q + radius] += val


def make_valid_mask(radius: int) -> np.ndarray:
    """Create boolean mask of valid hex cells within radius.
    Shape: (2*radius+1, 2*radius+1)."""
    side = 2 * radius + 1
    mask = np.zeros((side, side), dtype=bool)
    for r in range(-radius, radius + 1):
        for q in range(-radius, radius + 1):
            if is_valid_hex(q, r, radius):
                mask[r + radius, q + radius] = True
    return mask
