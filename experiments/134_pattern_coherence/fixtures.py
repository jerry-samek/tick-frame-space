"""Phase 1 pattern fixtures: Hamiltonian cycles on the cubic lattice.

Each fixture is a list of (x, y, z) cells in cycle order. Successive cells
(including last -> first) are face-adjacent. All cells lie in z = 0.

Geometric constraint (validated in tests/test_fixtures.py): every pair of
cells at cycle-distance 2 has all lattice common face-neighbors that are
themselves pattern cells. Required for the renewal rule's uniqueness.
"""

from substrate import Cell


F1_K4_SQUARE: list[Cell] = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
]


F2_K6_PERIMETER: list[Cell] = [
    (0, 0, 0),
    (1, 0, 0),
    (2, 0, 0),
    (2, 1, 0),
    (1, 1, 0),
    (0, 1, 0),
]


F3_K8_RING: list[Cell] = [
    # 4x2 rectangle perimeter. All 8 cells are on the perimeter (no interior),
    # so the 3x3-ring's "interior cell breaks geometric constraint" failure
    # mode does not arise.
    (0, 0, 0),
    (1, 0, 0),
    (2, 0, 0),
    (3, 0, 0),
    (3, 1, 0),
    (2, 1, 0),
    (1, 1, 0),
    (0, 1, 0),
]
