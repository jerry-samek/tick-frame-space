"""Multi-pattern substrate logic: connected components and per-component Step B.

Layered on top of Phase 1's substrate.py and rule.py. Phase 1 modules are
unchanged; this module adds multi-pattern primitives that reuse them.
"""

from collections import deque

from substrate import Canvas, Cell, decay, face_neighbors
from rule import find_c0


def connected_components(canvas: Canvas) -> list[set[Cell]]:
    """Partition the nonzero cells of `canvas` into face-connected components.

    Returns a list of sets, where each set is a maximal collection of cells
    such that every pair is reachable by a path of face-adjacent nonzero cells.
    """
    unvisited = set(canvas.keys())
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
            for neighbor in face_neighbors(cell):
                if neighbor in canvas and neighbor not in component:
                    queue.append(neighbor)
        components.append(component)
    return components


def _find_c_max_in(canvas: Canvas, cells: set[Cell]) -> Cell:
    """Return the cell in `cells` with maximum |γ|. Raises if cells is empty."""
    if not cells:
        raise ValueError("component is empty; no max cell")
    return max(cells, key=lambda c: abs(canvas[c]))


def _find_c_min_positive_in(canvas: Canvas, cells: set[Cell]) -> Cell:
    """Return the cell in `cells` with minimum |γ| among nonzero values.
    Raises if no nonzero cells in `cells`.
    """
    nonzero = [c for c in cells if canvas.get(c, 0) != 0]
    if not nonzero:
        raise ValueError("component has no nonzero cells")
    return min(nonzero, key=lambda c: abs(canvas[c]))


def step_b_component(canvas: Canvas, component: set[Cell]) -> None:
    """Apply Step B locally to one connected component.

    Identifies c_max and c_min within the component, then finds the unique
    γ=0 face-neighbor of both (which may lie outside the component, since
    γ=0 cells are by definition not in any component) and paints it.

    Raises ValueError if c_max/c_min ambiguity produces no valid c_0 (wedge)
    or multiple valid c_0 candidates (non-uniqueness).
    """
    c_max = _find_c_max_in(canvas, component)
    c_min = _find_c_min_positive_in(canvas, component)
    c0 = find_c0(canvas, c_max, c_min)
    gamma_max = canvas[c_max]
    sign = 1 if gamma_max > 0 else -1
    canvas[c0] = sign * (abs(gamma_max) + 1)
