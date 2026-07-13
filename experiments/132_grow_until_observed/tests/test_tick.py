# experiments/132_grow_until_observed/tests/test_tick.py
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters
from tick import build_connector_index, tick


def _make_simple_setup():
    """Two cells connected by one bidirectional connector. Cell A has charge=100,
    threshold=100 — about to fire. Cell B is empty."""
    cell_a = Cell(charge_level=100.0, threshold=100.0)
    cell_b = Cell(charge_level=0.0, threshold=100.0)
    cells = {(0, 0, 0): cell_a, (1, 0, 0): cell_b}
    connectors = [Connector(a=(0, 0, 0), b=(1, 0, 0))]
    return cells, connectors


def test_tick_cell_fires_emits_deposit():
    """Cell A at threshold fires; deposit emitted into the connector."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    fired = tick(cells, connectors, current_tick=1, params=params)
    assert fired == [(0, 0, 0)]
    assert cells[(0, 0, 0)].charge_level == 0.0
    assert cells[(0, 0, 0)].threshold == 100.5
    assert connectors[0].current_load == 1
    assert connectors[0].in_transit[0].destination == (1, 0, 0)


def test_tick_deposit_propagates_then_arrives():
    """Tick 1: A fires, deposit in transit (propagation_time=1).
    Tick 2: deposit arrives at B, B's charge increases by deposit_amount."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    tick(cells, connectors, current_tick=1, params=params)
    # After tick 1, deposit is in transit with remaining_propagation_time = 1.0
    fired = tick(cells, connectors, current_tick=2, params=params)
    # Tick 2: propagation step decrements to 0, deposit arrives at B,
    # B's charge += deposit_amount (30). B did not fire (charge 30 < threshold 100).
    assert fired == []
    assert cells[(1, 0, 0)].charge_level == 30.0
    assert connectors[0].current_load == 0


def test_tick_threshold_relaxes_when_idle():
    """A cell with elevated threshold and no firing for several ticks
    should see its threshold relax."""
    cell = Cell(charge_level=0.0, threshold=110.0, last_discharge_tick=-100)
    cells = {(0, 0, 0): cell}
    connectors = []
    params = Parameters(baseline_threshold=100.0, relaxation_rate=0.05)
    tick(cells, connectors, current_tick=5, params=params)
    assert cell.threshold == 110.0 - 0.05


def test_tick_state_resets_to_empty_after_discharge():
    """After firing, state is DISCHARGED transiently, then EMPTY at end of tick."""
    cells, connectors = _make_simple_setup()
    params = Parameters()
    tick(cells, connectors, current_tick=1, params=params)
    assert cells[(0, 0, 0)].state == CellState.EMPTY


def test_tick_with_precomputed_index_matches_unindexed():
    """Running tick() with a precomputed connector_index must yield identical
    results to running it without (which builds the index internally)."""
    # Build two identical fixtures and run them in parallel for many ticks.
    cells_a, connectors_a = _make_simple_setup()
    cells_b, connectors_b = _make_simple_setup()
    params = Parameters()

    index_b = build_connector_index(connectors_b)

    fired_a_log = []
    fired_b_log = []
    for t in range(1, 21):
        fired_a_log.append(tick(cells_a, connectors_a, current_tick=t, params=params))
        fired_b_log.append(
            tick(cells_b, connectors_b, current_tick=t, params=params, connector_index=index_b)
        )

    # Firing histories must match exactly.
    assert fired_a_log == fired_b_log

    # Final cell states must match exactly.
    for pos in cells_a:
        assert cells_a[pos].charge_level == cells_b[pos].charge_level
        assert cells_a[pos].threshold == cells_b[pos].threshold
        assert cells_a[pos].state == cells_b[pos].state
        assert cells_a[pos].last_discharge_tick == cells_b[pos].last_discharge_tick

    # Connector loads must match exactly.
    assert connectors_a[0].current_load == connectors_b[0].current_load


def test_build_connector_index_maps_endpoints():
    """build_connector_index returns a dict mapping each endpoint to its connectors."""
    c1 = Connector(a=(0, 0, 0), b=(1, 0, 0))
    c2 = Connector(a=(1, 0, 0), b=(2, 0, 0))
    c3 = Connector(a=(0, 0, 0), b=(0, 1, 0))
    index = build_connector_index([c1, c2, c3])
    # Compare by identity (Connector is not hashable due to mutable list field).
    assert {id(x) for x in index[(0, 0, 0)]} == {id(c1), id(c3)}
    assert {id(x) for x in index[(1, 0, 0)]} == {id(c1), id(c2)}
    assert {id(x) for x in index[(2, 0, 0)]} == {id(c2)}
    assert {id(x) for x in index[(0, 1, 0)]} == {id(c3)}
