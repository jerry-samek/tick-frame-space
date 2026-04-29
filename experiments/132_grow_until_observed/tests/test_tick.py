# experiments/132_grow_until_observed/tests/test_tick.py
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters
from tick import tick


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
