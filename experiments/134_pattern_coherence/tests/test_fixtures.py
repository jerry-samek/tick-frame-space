"""Validate that F1, F2, F3 are valid Hamiltonian cycles and satisfy the geometric constraint."""

import fixtures as f
from substrate import face_neighbors


def _is_face_adjacent(a, b):
    return tuple(b) in set(face_neighbors(a))


def _is_valid_hamiltonian_cycle(cycle):
    if len(cycle) != len(set(cycle)):
        return False, "duplicate cells"
    for i in range(len(cycle)):
        a = cycle[i]
        b = cycle[(i + 1) % len(cycle)]
        if not _is_face_adjacent(a, b):
            return False, f"cells {a} and {b} not face-adjacent"
    return True, None


def _satisfies_geometric_constraint(cycle):
    """Every cycle-distance-2 pair's lattice common face-neighbors are pattern cells."""
    K = len(cycle)
    pattern_set = set(cycle)
    for i in range(K):
        x = cycle[i]
        y = cycle[(i + 2) % K]
        common = set(face_neighbors(x)) & set(face_neighbors(y))
        for c in common:
            if c not in pattern_set:
                return False, f"({x}, {y}) has common face-neighbor {c} not in pattern"
    return True, None


def test_F1_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F1_K4_SQUARE)
    assert ok, msg


def test_F1_has_K_4():
    assert len(f.F1_K4_SQUARE) == 4


def test_F1_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F1_K4_SQUARE)
    assert ok, msg


def test_F2_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F2_K6_PERIMETER)
    assert ok, msg


def test_F2_has_K_6():
    assert len(f.F2_K6_PERIMETER) == 6


def test_F2_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F2_K6_PERIMETER)
    assert ok, msg


def test_F3_is_valid_hamiltonian_cycle():
    ok, msg = _is_valid_hamiltonian_cycle(f.F3_K8_RING)
    assert ok, msg


def test_F3_has_K_8():
    assert len(f.F3_K8_RING) == 8


def test_F3_satisfies_geometric_constraint():
    ok, msg = _satisfies_geometric_constraint(f.F3_K8_RING)
    assert ok, msg
