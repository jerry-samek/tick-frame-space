# experiments/132_grow_until_observed/capacitor.py
"""Capacitor cell datatype and charging/firing/threshold dynamics."""
from dataclasses import dataclass, field
from enum import Enum


class CellState(Enum):
    EMPTY = "empty"
    CHARGING = "charging"
    DISCHARGED = "discharged"


@dataclass
class Cell:
    charge_level: float = 0.0
    threshold: float = 100.0
    last_discharge_tick: int = -1
    state: CellState = CellState.EMPTY


# Functions implemented in Tasks 2-3.
def relax_threshold(cell: "Cell", current_tick: int, baseline: float, rate: float) -> None:
    """Relax threshold toward baseline if cell didn't just fire.

    Skipped on the tick immediately after firing (adaptation already happened).
    Clamped at baseline (threshold never goes below it).
    """
    if cell.last_discharge_tick == current_tick - 1:
        return
    cell.threshold = max(baseline, cell.threshold - rate)


def check_and_fire(cell: "Cell", current_tick: int, adaptation_rate: float) -> bool:
    raise NotImplementedError
