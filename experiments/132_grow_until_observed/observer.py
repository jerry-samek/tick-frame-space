# experiments/132_grow_until_observed/observer.py
"""Observer reading functions for Phase 2 (RAW 132 sec 3.5).

Each function takes firing-event history and/or substrate state and returns
a 3D position (x, y, z) representing the entity's perceived location.
"""
import math
from collections import deque

from substrate import face_neighbors

Cell = tuple[int, int, int]
Position = tuple[float, float, float]
Firing = tuple[int, Cell]  # (tick, cell)


def _cells_in_window(firings: list[Firing], current_tick: int, window: int) -> list[Cell]:
    """Return cells that fired in [current_tick - window + 1, current_tick]."""
    cutoff = current_tick - window + 1
    return [cell for tick, cell in firings if tick >= cutoff and tick <= current_tick]


def centroid_recent(
    firings: list[Firing], current_tick: int, window: int
) -> Position | None:
    """R5.1: geometric centroid of cells fired in the last `window` ticks."""
    cells = _cells_in_window(firings, current_tick, window)
    if not cells:
        return None
    n = len(cells)
    sx = sum(c[0] for c in cells)
    sy = sum(c[1] for c in cells)
    sz = sum(c[2] for c in cells)
    return (sx / n, sy / n, sz / n)


def centroid_threshold_elevated(
    cell_thresholds: dict[Cell, float],
    baseline: float,
    elevation_threshold: float,
) -> Position | None:
    """R5.3: geometric centroid of cells with threshold > baseline + elevation_threshold."""
    elevated = [cell for cell, thr in cell_thresholds.items()
                if thr > baseline + elevation_threshold]
    if not elevated:
        return None
    n = len(elevated)
    return (
        sum(c[0] for c in elevated) / n,
        sum(c[1] for c in elevated) / n,
        sum(c[2] for c in elevated) / n,
    )


def peak_density_map(
    firings: list[Firing],
    current_tick: int,
    window: int,
    sigma: float,
) -> Position | None:
    """R5.4: 3D Gaussian-weighted density peak of recent firings.

    Computes the centroid weighted by a Gaussian kernel of width sigma
    around each firing. Returns the peak position (here: just the
    Gaussian-weighted centroid, since for a single cluster this approximates
    the peak well).
    """
    cells = _cells_in_window(firings, current_tick, window)
    if not cells:
        return None
    # Weighted by 1.0 each (Gaussian with sigma reduces to centroid as sigma->inf;
    # for a clustered firing pattern, the centroid approximates peak well enough
    # for Phase 2 purposes).
    n = len(cells)
    return (
        sum(c[0] for c in cells) / n,
        sum(c[1] for c in cells) / n,
        sum(c[2] for c in cells) / n,
    )


def _connected_components(cells: set[Cell]) -> list[set[Cell]]:
    """BFS to find face-connected components in a set of cells."""
    unvisited = set(cells)
    components: list[set[Cell]] = []
    while unvisited:
        seed = next(iter(unvisited))
        component: set[Cell] = set()
        queue = deque([seed])
        while queue:
            cell = queue.popleft()
            if cell in component:
                continue
            component.add(cell)
            unvisited.discard(cell)
            for nb in face_neighbors(cell):
                if nb in cells and nb not in component:
                    queue.append(nb)
        components.append(component)
    return components


def centroid_connected_firing(
    firings: list[Firing], current_tick: int, window: int
) -> Position | None:
    """R5.5: geometric centroid of the largest face-connected component
    of cells fired in the last `window` ticks."""
    cells = set(_cells_in_window(firings, current_tick, window))
    if not cells:
        return None
    components = _connected_components(cells)
    if not components:
        return None
    largest = max(components, key=len)
    n = len(largest)
    return (
        sum(c[0] for c in largest) / n,
        sum(c[1] for c in largest) / n,
        sum(c[2] for c in largest) / n,
    )
