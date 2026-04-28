"""Multi-pattern substrate logic: connected components and per-component Step B.

Layered on top of Phase 1's substrate.py and rule.py. Phase 1 modules are
unchanged; this module adds multi-pattern primitives that reuse them.
"""

from collections import deque

from substrate import Canvas, Cell, decay, face_neighbors


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
