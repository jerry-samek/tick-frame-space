# experiments/132_grow_until_observed/lattice.py
"""Bounded cubic lattice helpers: cell enumeration + full face-adjacency
connector wiring."""
from connectors import Connector
from substrate import face_neighbors

Cell = tuple[int, int, int]


def enumerate_cells(
    x_range: tuple[int, int],
    y_range: tuple[int, int],
    z_range: tuple[int, int],
) -> list[Cell]:
    """Enumerate all cells in the half-open box [x_range[0], x_range[1]) x ..."""
    return [
        (x, y, z)
        for x in range(x_range[0], x_range[1])
        for y in range(y_range[0], y_range[1])
        for z in range(z_range[0], z_range[1])
    ]


def build_connectors(cells: list[Cell]) -> list[Connector]:
    """Build a Connector for each pair of face-adjacent cells in the input list.

    Each pair is included at most once (the pair (a, b) and (b, a) produce one connector).
    """
    cell_set = set(cells)
    seen: set[frozenset[Cell]] = set()
    connectors: list[Connector] = []
    for cell in cells:
        for neighbor in face_neighbors(cell):
            if neighbor not in cell_set:
                continue
            pair = frozenset({cell, neighbor})
            if pair in seen:
                continue
            seen.add(pair)
            connectors.append(Connector(a=cell, b=neighbor))
    return connectors
