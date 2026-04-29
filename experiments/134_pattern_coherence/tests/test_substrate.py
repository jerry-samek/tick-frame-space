"""Unit tests for substrate primitives."""

import substrate as s


def test_decay_empty_canvas_stays_empty():
    canvas = {}
    s.decay(canvas)
    assert canvas == {}


def test_decay_positive_cell_decreases_by_1():
    canvas = {(0, 0, 0): 5}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): 4}


def test_decay_negative_cell_increases_by_1():
    canvas = {(0, 0, 0): -5}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): -4}


def test_decay_positive_one_expires_to_removed():
    canvas = {(0, 0, 0): 1}
    s.decay(canvas)
    assert canvas == {}


def test_decay_negative_one_expires_to_removed():
    canvas = {(0, 0, 0): -1}
    s.decay(canvas)
    assert canvas == {}


def test_decay_multiple_cells_independent():
    canvas = {(0, 0, 0): 3, (1, 0, 0): -2, (2, 0, 0): 1}
    s.decay(canvas)
    assert canvas == {(0, 0, 0): 2, (1, 0, 0): -1}


def test_face_neighbors_origin_returns_six_cells():
    neighbors = s.face_neighbors((0, 0, 0))
    assert len(neighbors) == 6
    assert set(neighbors) == {
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    }


def test_face_neighbors_arbitrary_cell():
    neighbors = s.face_neighbors((5, -3, 7))
    assert set(neighbors) == {
        (6, -3, 7), (4, -3, 7),
        (5, -2, 7), (5, -4, 7),
        (5, -3, 8), (5, -3, 6),
    }
