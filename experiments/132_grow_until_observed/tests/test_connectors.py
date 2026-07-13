# experiments/132_grow_until_observed/tests/test_connectors.py
import pytest
from connectors import Connector, Deposit, emit_deposit, propagate_step


def test_emit_deposit_from_a_to_b():
    """Emitting from cell A puts deposit in transit toward cell B."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=1.0)
    assert conn.current_load == 1
    assert conn.in_transit[0].destination == (1, 0, 0)
    assert conn.in_transit[0].remaining_propagation_time == 1.0


def test_emit_deposit_from_b_to_a():
    """Emitting from cell B puts deposit in transit toward cell A."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(1, 0, 0), propagation_time_base=1.0)
    assert conn.in_transit[0].destination == (0, 0, 0)


def test_emit_deposit_unknown_source_raises():
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    with pytest.raises(ValueError, match=r"(?i)not.*endpoint"):
        emit_deposit(conn, source=(5, 5, 5), propagation_time_base=1.0)


def test_propagate_step_advances_deposit():
    """With load_coefficient=0, each step advances by exactly 1.0."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=2.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert arrived == []
    assert conn.in_transit[0].remaining_propagation_time == 1.0


def test_propagate_step_delivers_when_done():
    """Deposit arriving this step returned in arrived list, removed from in_transit."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=1.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert len(arrived) == 1
    assert arrived[0].destination == (1, 0, 0)
    assert conn.in_transit == []
    assert conn.current_load == 0


def test_propagate_step_load_zero_means_unaffected():
    """load_coefficient=0 means propagation rate is exactly 1/tick regardless of load."""
    conn = Connector(a=(0, 0, 0), b=(1, 0, 0))
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=3.0)
    emit_deposit(conn, source=(0, 0, 0), propagation_time_base=3.0)
    arrived = propagate_step(conn, load_coefficient=0.0)
    assert arrived == []
    for d in conn.in_transit:
        assert d.remaining_propagation_time == 2.0
