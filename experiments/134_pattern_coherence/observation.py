"""Pattern-of-origin tagging and observable extraction for Phase 2.

The substrate dynamics ignore tags; this module is measurement-only.
"""

import hashlib

from substrate import Canvas, Cell

PatternIdMap = dict[Cell, str]


def count_alive_tagged(canvas: Canvas, pattern_id: PatternIdMap, tag: str) -> int:
    """Count cells with the given tag that are still alive (in canvas)."""
    return sum(1 for cell, t in pattern_id.items() if t == tag and cell in canvas)


def centroid_alive_tagged(
    canvas: Canvas, pattern_id: PatternIdMap, tag: str
) -> tuple[float, float, float] | None:
    """Geometric centroid of cells with the given tag that are still alive.
    Returns None if no such cells remain."""
    alive = [cell for cell, t in pattern_id.items() if t == tag and cell in canvas]
    if not alive:
        return None
    n = len(alive)
    sx = sum(c[0] for c in alive)
    sy = sum(c[1] for c in alive)
    sz = sum(c[2] for c in alive)
    return (sx / n, sy / n, sz / n)


def canvas_hash(canvas: Canvas) -> str:
    """Stable SHA-256 hash of canvas state, dict-order-independent."""
    items = sorted(canvas.items())
    return hashlib.sha256(repr(items).encode()).hexdigest()
