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


import rule as r


def test_tick_multi_isolated_F1_invariant_over_K_ticks():
    """A single isolated F1 pattern under tick_multi should be a fixed point
    after K=4 ticks, just like Phase 1."""
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    initial = dict(canvas)
    for _ in range(4):
        mp.tick_multi(canvas)
    assert canvas == initial


def test_tick_multi_two_separated_F1s_both_invariant():
    """Two F1 patterns separated by 1 empty cell are independent components.
    Each should remain invariant over K=4 ticks of tick_multi."""
    canvas: s.Canvas = {}
    cycle_a = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    cycle_b = [(3, 0, 0), (4, 0, 0), (4, 1, 0), (3, 1, 0)]
    r.bootstrap(canvas, cycle_a, sign=1)
    r.bootstrap(canvas, cycle_b, sign=1)
    initial = dict(canvas)
    for _ in range(4):
        mp.tick_multi(canvas)
    assert canvas == initial


def test_tick_multi_failed_component_decays_quietly():
    """A component whose step_b_component raises ValueError (e.g., wedged
    contact between two patterns) should not crash tick_multi. The
    component's cells should continue to decay over subsequent ticks
    without renewal, and eventually expire to zero. Other components
    must continue normally."""
    canvas: s.Canvas = {}
    # Healthy component (will be invariant)
    healthy = [(10, 10, 0), (11, 10, 0), (11, 11, 0), (10, 11, 0)]
    r.bootstrap(canvas, healthy, sign=1)
    # Wedged component (two face-adjacent F1s — merged ambiguous component)
    r.bootstrap(canvas, [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)], sign=1)
    r.bootstrap(canvas, [(2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)], sign=1)

    # Run K ticks. Healthy component should be invariant; merged should
    # have lost cells (some / all expired without renewal).
    healthy_initial = {c: canvas[c] for c in healthy}
    for _ in range(4):
        mp.tick_multi(canvas)

    # Healthy survived
    for c in healthy:
        assert canvas.get(c) == healthy_initial[c], (
            f"healthy component cell {c} changed: was {healthy_initial[c]}, "
            f"now {canvas.get(c)}"
        )

    # At least some cells of the merged 8-cell component dissolved
    merged_cells = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0),
                    (2, 0, 0), (3, 0, 0), (3, 1, 0), (2, 1, 0)]
    n_alive = sum(1 for c in merged_cells if c in canvas)
    assert n_alive < 8, "expected some merged-component cells to dissolve, but all 8 alive"
