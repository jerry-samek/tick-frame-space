# experiments/132_grow_until_observed/substrate.py
"""Cubic lattice helpers: face_neighbors, bounds checking."""

Cell = tuple[int, int, int]


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    raise NotImplementedError
