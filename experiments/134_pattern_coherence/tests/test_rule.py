"""Unit tests for renewal rule primitives."""

import pytest

import rule as r
import substrate as s


def test_bootstrap_4_cell_cycle_positive_sign():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    assert canvas == {
        (0, 0, 0): 4,
        (1, 0, 0): 3,
        (1, 1, 0): 2,
        (0, 1, 0): 1,
    }


def test_bootstrap_4_cell_cycle_negative_sign():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=-1)
    assert canvas == {
        (0, 0, 0): -4,
        (1, 0, 0): -3,
        (1, 1, 0): -2,
        (0, 1, 0): -1,
    }


def test_bootstrap_invalid_sign_raises():
    with pytest.raises(ValueError):
        r.bootstrap({}, [(0, 0, 0)], sign=0)


def test_find_c_max_single_positive_cell():
    canvas = {(0, 0, 0): 5}
    assert r.find_c_max(canvas) == (0, 0, 0)


def test_find_c_max_picks_largest_magnitude():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 7, (2, 0, 0): 5}
    assert r.find_c_max(canvas) == (1, 0, 0)


def test_find_c_max_negative_pattern():
    canvas = {(0, 0, 0): -3, (1, 0, 0): -7, (2, 0, 0): -5}
    assert r.find_c_max(canvas) == (1, 0, 0)


def test_find_c_max_empty_canvas_raises():
    with pytest.raises(ValueError):
        r.find_c_max({})


def test_find_c_min_positive_picks_smallest_nonzero_magnitude():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 7, (2, 0, 0): 1}
    assert r.find_c_min_positive(canvas) == (2, 0, 0)


def test_find_c_min_positive_negative_pattern():
    canvas = {(0, 0, 0): -3, (1, 0, 0): -7, (2, 0, 0): -1}
    assert r.find_c_min_positive(canvas) == (2, 0, 0)


def test_find_c_min_positive_empty_canvas_raises():
    with pytest.raises(ValueError):
        r.find_c_min_positive({})


def test_find_c0_returns_unique_zero_neighbor_of_both():
    """F1 mid-cycle: c_max=(0,0,0)γ=3, c_min=(1,1,0)γ=1; expired (0,1,0)γ=0."""
    canvas = {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
    }
    assert r.find_c0(canvas, (0, 0, 0), (1, 1, 0)) == (0, 1, 0)


def test_find_c0_wedged_state_raises():
    canvas = {(0, 0, 0): 3, (10, 0, 0): 1}
    with pytest.raises(ValueError, match=r"(?i)wedged|no.*common"):
        r.find_c0(canvas, (0, 0, 0), (10, 0, 0))


def test_find_c0_non_uniqueness_raises():
    """c_max at (0,0,0) and c_min at (1,1,0) share two lattice common
    face-neighbors: (1,0,0) and (0,1,0). Both at gamma=0 (not in canvas) ->
    non-unique."""
    canvas = {(0, 0, 0): 3, (1, 1, 0): 1}
    with pytest.raises(ValueError, match=r"(?i)non-unique|multiple"):
        r.find_c0(canvas, (0, 0, 0), (1, 1, 0))


def test_step_b_paints_with_correct_magnitude_and_sign_positive():
    canvas = {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
    }
    r.step_b(canvas)
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_step_b_paints_with_correct_sign_negative():
    canvas = {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
    }
    r.step_b(canvas)
    assert canvas == {
        (0, 0, 0): -3,
        (1, 0, 0): -2,
        (1, 1, 0): -1,
        (0, 1, 0): -4,
    }


def test_tick_one_step_on_F1_bootstrap():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    r.tick(canvas)
    assert canvas == {
        (0, 0, 0): 3,
        (1, 0, 0): 2,
        (1, 1, 0): 1,
        (0, 1, 0): 4,
    }


def test_tick_period_K_returns_to_bootstrap_state():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=1)
    initial = dict(canvas)
    for _ in range(4):
        r.tick(canvas)
    assert canvas == initial


def test_tick_period_K_negative_pattern():
    canvas: s.Canvas = {}
    cycle = [(0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)]
    r.bootstrap(canvas, cycle, sign=-1)
    initial = dict(canvas)
    for _ in range(4):
        r.tick(canvas)
    assert canvas == initial
