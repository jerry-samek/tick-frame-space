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
