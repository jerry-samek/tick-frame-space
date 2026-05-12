from cell import Cell, Deposit, Response, State


def test_classify_unknown_for_empty_spectrum():
    c = Cell(spectrum=set())
    assert c.classify(7) == Response.UNKNOWN


def test_classify_same_for_token_in_spectrum():
    c = Cell(spectrum={3})
    assert c.classify(3) == Response.SAME


def test_classify_different_for_token_not_in_populated_spectrum():
    c = Cell(spectrum={1, 2, 5})
    assert c.classify(7) == Response.DIFFERENT


def test_deposit_carries_token_predecessor_origin_age():
    origin = Cell(spectrum={0})
    d = Deposit(token=42, predecessor=None, origin=origin, age=0)
    assert d.token == 42
    assert d.predecessor is None
    assert d.origin is origin
    assert d.age == 0


# ---------- Phase 2: learning ----------

def test_empty_cell_starts_in_learning_state():
    c = Cell(spectrum=set())
    assert c.state == State.LEARNING


def test_preset_spectrum_cell_starts_crystallized():
    c = Cell(spectrum={3})
    assert c.state == State.CRYSTALLIZED


def test_classify_increments_obs_counter():
    c = Cell(spectrum=set())
    c.classify(5)
    c.classify(5)
    c.classify(7)
    assert c.obs_counter[5] == 2
    assert c.obs_counter[7] == 1


def test_learning_cell_crystallizes_after_threshold_observations():
    c = Cell(spectrum=set(), learning_threshold=10, crystallization_size=3)
    # Inject 10 tokens with clear top-3.
    stream = [10, 10, 10, 10, 11, 11, 11, 12, 12, 13]
    for t in stream:
        c.classify(t)
    assert c.state == State.CRYSTALLIZED
    assert c.spectrum == {10, 11, 12}


def test_learning_cell_returns_unknown_during_learning():
    c = Cell(spectrum=set(), learning_threshold=100)
    # Few observations — still in learning.
    assert c.classify(5) == Response.UNKNOWN
    assert c.state == State.LEARNING


def test_crystallized_cell_classifies_normally():
    c = Cell(spectrum=set(), learning_threshold=5, crystallization_size=2)
    for t in [3, 3, 3, 4, 4]:
        c.classify(t)
    assert c.state == State.CRYSTALLIZED
    assert c.spectrum == {3, 4}
    # Now classification works.
    assert c.classify(3) == Response.SAME
    assert c.classify(4) == Response.SAME
    assert c.classify(99) == Response.DIFFERENT


def test_crystallized_cell_spectrum_is_frozen():
    c = Cell(spectrum=set(), learning_threshold=5, crystallization_size=2)
    for t in [1, 1, 1, 2, 2]:
        c.classify(t)
    spectrum_before = set(c.spectrum)
    # Continue observing — heavy bias toward NEW tokens.
    for t in [99] * 100:
        c.classify(t)
    assert c.spectrum == spectrum_before  # frozen
    assert c.state == State.CRYSTALLIZED
