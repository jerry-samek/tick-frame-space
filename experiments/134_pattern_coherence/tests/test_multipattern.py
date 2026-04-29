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


import pytest


def test_step_b_component_paints_F1_successor():
    """For an isolated F1 component mid-cycle, step_b_component should paint
    the unique cycle successor — same behavior as Phase 1's step_b."""
    canvas = {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component)
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_step_b_component_negative_pattern():
    canvas = {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component)
    assert canvas == {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
        (0, 1, 0): -4,
    }


def test_step_b_component_ignores_cells_outside_component():
    """If two F1 cycles are far apart, step_b_component on one should not
    affect or read from the other."""
    canvas = {
        # Component A
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        # Component B (far away, not in `component` arg)
        (10, 10, 0): 3,
        (11, 10, 0): 2,
        (11, 11, 0): 1,
    }
    component_a = {(0, 0, 0), (1, 0, 0), (1, 1, 0)}
    mp.step_b_component(canvas, component_a)
    # A's successor was painted
    assert canvas[(0, 1, 0)] == 4
    # B is unchanged
    assert canvas[(10, 10, 0)] == 3
    assert canvas[(11, 10, 0)] == 2
    assert canvas[(11, 11, 0)] == 1
    # B's would-be successor (10, 11, 0) was NOT painted
    assert (10, 11, 0) not in canvas


def test_step_b_component_raises_on_wedged():
    """Component with no valid c_0 raises ValueError."""
    # Two cells far apart in same "component" -- contrived setup since they
    # wouldn't normally be in one connected component, but step_b_component
    # operates on whatever set we hand it.
    canvas = {(0, 0, 0): 3, (10, 0, 0): 1}
    component = {(0, 0, 0), (10, 0, 0)}
    with pytest.raises(ValueError, match=r"(?i)wedged|no.*common"):
        mp.step_b_component(canvas, component)


def test_step_b_component_raises_on_non_uniqueness():
    """When merged 8-cell component (two F1s face-adjacent), c_max and c_min
    have multiple γ=0 face-neighbors → non-unique error (or wedge — either
    failure mode is acceptable; what matters is ValueError, not silent wrong
    output)."""
    # Two F1 squares face-adjacent at x=1 <-> x=2. Bootstrap-fresh values.
    canvas = {
        # Planet F1 just bootstrapped
        (0, 0, 0): 4,
        (1, 0, 0): 3,
        (1, 1, 0): 2,
        (0, 1, 0): 1,
        # Test F1 face-adjacent at x=2..3
        (2, 0, 0): 4,
        (3, 0, 0): 3,
        (3, 1, 0): 2,
        (2, 1, 0): 1,
    }
    component = {(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                 (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)}
    # The actual outcome may be wedge OR non-unique depending on which
    # cells iter picks for c_max and c_min. Either is acceptable; what
    # matters is that step_b_component raises ValueError, not silently
    # produces wrong output.
    with pytest.raises(ValueError):
        mp.step_b_component(canvas, component)
