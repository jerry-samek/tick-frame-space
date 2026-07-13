# experiments/132_grow_until_observed/tests/test_capacitor.py
import pytest
from capacitor import Cell, CellState, relax_threshold, check_and_fire


def test_relax_threshold_decreases_when_idle():
    """A cell that didn't fire last tick should relax toward baseline."""
    cell = Cell(threshold=110.0, last_discharge_tick=-10)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == pytest.approx(110.0 - 0.05)


def test_relax_threshold_clamped_at_baseline():
    """Threshold should not go below baseline."""
    cell = Cell(threshold=100.02, last_discharge_tick=-10)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == 100.0


def test_relax_threshold_skipped_just_after_firing():
    """If cell fired last tick (current_tick - last_discharge_tick == 1),
    no relaxation this tick — adaptation just happened."""
    cell = Cell(threshold=110.0, last_discharge_tick=4)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == 110.0


def test_relax_threshold_applied_after_idle():
    """Two ticks since firing: relaxation applies."""
    cell = Cell(threshold=110.0, last_discharge_tick=3)
    relax_threshold(cell, current_tick=5, baseline=100.0, rate=0.05)
    assert cell.threshold == pytest.approx(110.0 - 0.05)


def test_check_and_fire_no_fire_below_threshold():
    cell = Cell(charge_level=50.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is False
    assert cell.charge_level == 50.0
    assert cell.threshold == 100.0
    assert cell.last_discharge_tick == -1


def test_check_and_fire_fires_at_threshold():
    cell = Cell(charge_level=100.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is True
    assert cell.charge_level == 0.0
    assert cell.threshold == 100.5
    assert cell.last_discharge_tick == 5
    assert cell.state == CellState.DISCHARGED


def test_check_and_fire_fires_above_threshold():
    """Charge can exceed threshold (e.g., from arriving deposits) — still fires.
    Excess is discarded (charge resets to 0)."""
    cell = Cell(charge_level=130.0, threshold=100.0)
    fired = check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert fired is True
    assert cell.charge_level == 0.0
    assert cell.threshold == 100.5


def test_check_and_fire_state_set_to_discharged():
    cell = Cell(charge_level=100.0, threshold=100.0, state=CellState.CHARGING)
    check_and_fire(cell, current_tick=5, adaptation_rate=0.5)
    assert cell.state == CellState.DISCHARGED
