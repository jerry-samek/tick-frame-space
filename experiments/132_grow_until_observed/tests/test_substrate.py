# experiments/132_grow_until_observed/tests/test_substrate.py
import substrate as s


def test_face_neighbors_origin():
    neighbors = s.face_neighbors((0, 0, 0))
    assert set(neighbors) == {
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    }


def test_face_neighbors_arbitrary():
    neighbors = s.face_neighbors((5, -3, 7))
    assert set(neighbors) == {
        (6, -3, 7), (4, -3, 7),
        (5, -2, 7), (5, -4, 7),
        (5, -3, 8), (5, -3, 6),
    }
