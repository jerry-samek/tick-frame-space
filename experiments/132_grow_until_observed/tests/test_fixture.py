# experiments/132_grow_until_observed/tests/test_fixture.py
from capacitor import Cell, CellState
from connectors import Connector
from fixture import F1_CYCLE, setup_fixture
from parameters import Parameters


def test_fixture_has_four_cells():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert pos in cells


def test_fixture_has_four_connectors_in_cycle():
    """Cycle order: C0->C1->C2->C3->C0. 4 connectors."""
    params = Parameters()
    _, connectors = setup_fixture(params)
    assert len(connectors) == 4
    cycle_pairs = set()
    for conn in connectors:
        cycle_pairs.add(frozenset({conn.a, conn.b}))
    expected_pairs = {
        frozenset({(0, 0, 0), (1, 0, 0)}),
        frozenset({(1, 0, 0), (1, 1, 0)}),
        frozenset({(1, 1, 0), (0, 1, 0)}),
        frozenset({(0, 1, 0), (0, 0, 0)}),
    }
    assert cycle_pairs == expected_pairs


def test_fixture_staggered_initial_charges():
    """C0 about to fire (charge=threshold), then 0.75/0.50/0.25 of threshold."""
    params = Parameters(baseline_threshold=100.0, bootstrap_charge_step=0.25)
    cells, _ = setup_fixture(params)
    assert cells[(0, 0, 0)].charge_level == 100.0
    assert cells[(1, 0, 0)].charge_level == 75.0
    assert cells[(1, 1, 0)].charge_level == 50.0
    assert cells[(0, 1, 0)].charge_level == 25.0


def test_fixture_thresholds_at_baseline():
    params = Parameters(baseline_threshold=100.0)
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].threshold == 100.0


def test_fixture_initial_state_charging():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].state == CellState.CHARGING


def test_fixture_initial_last_discharge_tick():
    params = Parameters()
    cells, _ = setup_fixture(params)
    for pos in F1_CYCLE:
        assert cells[pos].last_discharge_tick == -1
