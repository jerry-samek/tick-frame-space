# experiments/132_grow_until_observed/substrate.py
"""Cubic lattice helpers: face_neighbors, bounds checking."""

Cell = tuple[int, int, int]


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    x, y, z = cell
    return [
        (x + 1, y, z), (x - 1, y, z),
        (x, y + 1, z), (x, y - 1, z),
        (x, y, z + 1), (x, y, z - 1),
    ]
