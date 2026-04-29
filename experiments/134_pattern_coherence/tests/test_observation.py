"""Unit tests for observation primitives."""

import observation as o
import substrate as s


def test_count_alive_tagged_all_alive():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 2, (1, 1, 0): 1, (0, 1, 0): 4}
    pattern_id = {(0, 0, 0): "test", (1, 0, 0): "test",
                  (1, 1, 0): "test", (0, 1, 0): "test"}
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 4


def test_count_alive_tagged_some_expired():
    canvas = {(0, 0, 0): 3, (1, 0, 0): 2}
    pattern_id = {(0, 0, 0): "test", (1, 0, 0): "test",
                  (1, 1, 0): "test", (0, 1, 0): "test"}
    # (1, 1, 0) and (0, 1, 0) tagged but not in canvas (expired)
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 2


def test_count_alive_tagged_excludes_other_tags():
    canvas = {(0, 0, 0): 3, (10, 0, 0): 4}
    pattern_id = {(0, 0, 0): "test", (10, 0, 0): "planet"}
    assert o.count_alive_tagged(canvas, pattern_id, "test") == 1
    assert o.count_alive_tagged(canvas, pattern_id, "planet") == 1


def test_centroid_alive_tagged_all_alive():
    canvas = {(0, 0, 0): 3, (2, 0, 0): 2, (2, 2, 0): 1, (0, 2, 0): 4}
    pattern_id = {(0, 0, 0): "test", (2, 0, 0): "test",
                  (2, 2, 0): "test", (0, 2, 0): "test"}
    centroid = o.centroid_alive_tagged(canvas, pattern_id, "test")
    assert centroid == (1.0, 1.0, 0.0)


def test_centroid_alive_tagged_returns_none_when_none_alive():
    canvas: s.Canvas = {}
    pattern_id = {(0, 0, 0): "test"}
    assert o.centroid_alive_tagged(canvas, pattern_id, "test") is None


def test_canvas_hash_stable_across_dict_order():
    """Hash is stable regardless of dict insertion order."""
    canvas_a = {(0, 0, 0): 3, (1, 0, 0): 2}
    canvas_b = {(1, 0, 0): 2, (0, 0, 0): 3}
    assert o.canvas_hash(canvas_a) == o.canvas_hash(canvas_b)


def test_canvas_hash_differs_when_value_differs():
    canvas_a = {(0, 0, 0): 3}
    canvas_b = {(0, 0, 0): 4}
    assert o.canvas_hash(canvas_a) != o.canvas_hash(canvas_b)
