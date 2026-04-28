"""Unit tests for multipattern primitives."""

import multipattern as mp
import substrate as s


def test_empty_canvas_zero_components():
    assert mp.connected_components({}) == []


def test_single_cell_one_component():
    canvas = {(0, 0, 0): 5}
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0)}


def test_face_adjacent_cells_one_component():
    canvas = {(0, 0, 0): 5, (1, 0, 0): 3}
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0), (1, 0, 0)}


def test_diagonal_cells_two_components():
    """Diagonal cells (Manhattan distance 2) are NOT face-adjacent;
    they must be separate components."""
    canvas = {(0, 0, 0): 5, (1, 1, 0): 3}
    components = mp.connected_components(canvas)
    assert len(components) == 2


def test_F1_square_one_component():
    """Phase 1's F1 (2x2 square) — 4 cells form one connected component."""
    canvas = {
        (0, 0, 0): 4,
        (1, 0, 0): 3,
        (1, 1, 0): 2,
        (0, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert components[0] == {(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)}


def test_two_separated_F1_squares_two_components():
    """Two F1 squares with 1 empty cell between them = 2 components."""
    canvas = {
        # First F1 at x=0..1
        (0, 0, 0): 4, (1, 0, 0): 3, (1, 1, 0): 2, (0, 1, 0): 1,
        # Second F1 at x=3..4 (gap of 1 empty cell at x=2)
        (3, 0, 0): 4, (4, 0, 0): 3, (4, 1, 0): 2, (3, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 2


def test_two_face_adjacent_F1_squares_one_component():
    """Two F1 squares with NO gap (face-adjacent) = 1 merged component."""
    canvas = {
        # First F1 at x=0..1
        (0, 0, 0): 4, (1, 0, 0): 3, (1, 1, 0): 2, (0, 1, 0): 1,
        # Second F1 at x=2..3 (face-adjacent: (1,0,0) <-> (2,0,0))
        (2, 0, 0): 4, (3, 0, 0): 3, (3, 1, 0): 2, (2, 1, 0): 1,
    }
    components = mp.connected_components(canvas)
    assert len(components) == 1
    assert len(components[0]) == 8
