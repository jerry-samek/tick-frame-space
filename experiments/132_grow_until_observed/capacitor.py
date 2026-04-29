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
    raise NotImplementedError


def check_and_fire(cell: "Cell", current_tick: int, adaptation_rate: float) -> bool:
    raise NotImplementedError
