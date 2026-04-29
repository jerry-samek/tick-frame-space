"""Signed-integer 3D sparse canvas with symmetric decay.

The substrate is a dict mapping (x, y, z) -> int. Cells with gamma = 0 are
not stored. Decay subtracts 1 from each cell's magnitude (drift toward 0).
"""

Cell = tuple[int, int, int]
Canvas = dict[Cell, int]


def decay(canvas: Canvas) -> None:
    """Apply Step A: gamma -= sign(gamma) for every nonzero cell. In-place.
    Cells reaching gamma = 0 are removed from the dict.
    """
    expired = []
    for cell, gamma in canvas.items():
        new = gamma - 1 if gamma > 0 else gamma + 1
        if new == 0:
            expired.append(cell)
        else:
            canvas[cell] = new
    for cell in expired:
        del canvas[cell]


def face_neighbors(cell: Cell) -> list[Cell]:
    """Return the 6 face-adjacent cells on the cubic lattice."""
    x, y, z = cell
    return [
        (x + 1, y, z), (x - 1, y, z),
        (x, y + 1, z), (x, y - 1, z),
        (x, y, z + 1), (x, y, z - 1),
    ]
