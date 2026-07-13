# experiments/132_grow_until_observed/tests/test_lattice.py
from lattice import enumerate_cells, build_connectors


def test_enumerate_cells_small_box():
    """Box from (0,0,0) to (1,1,0) gives 4 cells."""
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 1))
    assert len(cells) == 4
    assert set(cells) == {(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)}


def test_enumerate_cells_3d():
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 2))
    assert len(cells) == 8


def test_build_connectors_2x2_square():
    """2x2 square in z=0 plane: 4 cells, 4 face-adjacent edges."""
    cells = [(0, 0, 0), (1, 0, 0), (0, 1, 0), (1, 1, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 4
    pairs = {frozenset({c.a, c.b}) for c in connectors}
    expected = {
        frozenset({(0, 0, 0), (1, 0, 0)}),
        frozenset({(0, 0, 0), (0, 1, 0)}),
        frozenset({(1, 0, 0), (1, 1, 0)}),
        frozenset({(0, 1, 0), (1, 1, 0)}),
    }
    assert pairs == expected


def test_build_connectors_no_diagonal_connections():
    """Diagonal pairs (Manhattan distance 2) should NOT be connected."""
    cells = [(0, 0, 0), (1, 1, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 0


def test_build_connectors_3d_cube():
    """2x2x2 cube: 8 cells, 12 face-adjacent edges (3 per axis × 4 perpendicular pairs)."""
    cells = enumerate_cells(x_range=(0, 2), y_range=(0, 2), z_range=(0, 2))
    connectors = build_connectors(cells)
    assert len(connectors) == 12


def test_build_connectors_no_duplicates():
    """Each pair should have only one connector even if generated multiple times."""
    cells = [(0, 0, 0), (1, 0, 0)]
    connectors = build_connectors(cells)
    assert len(connectors) == 1
