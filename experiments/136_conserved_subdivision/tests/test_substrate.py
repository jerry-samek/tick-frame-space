from fractions import Fraction
from substrate import Substrate


def test_genesis_single_cell_measure_one():
    s = Substrate()
    assert len(s.leaves) == 1
    assert sum(c.measure for c in s.leaves) == Fraction(1)


def test_first_boundary_two_leaves_conserved():
    s = Substrate(); s.tick()
    assert len(s.leaves) == 2
    assert sum(c.measure for c in s.leaves) == Fraction(1)


def test_conservation_exact_over_many_ticks():
    s = Substrate()
    for _ in range(8):
        s.tick()
        assert sum(c.measure for c in s.leaves) == Fraction(1)


def test_append_only_history_grows_never_shrinks():
    s = Substrate(); n0 = s.node_count()
    s.tick()
    assert s.node_count() > n0
    assert all(nid in s.nodes for nid in s._all_ids_before_last_tick)


def test_address_is_bitstring_path():
    s = Substrate(); s.tick()
    assert sorted(c.address for c in s.leaves) == ["0", "1"]
