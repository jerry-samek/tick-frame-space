# experiments/132_grow_until_observed/connectors.py
"""Connector edge datatype and load-driven propagation."""
from dataclasses import dataclass, field

Cell = tuple[int, int, int]


@dataclass
class Deposit:
    remaining_propagation_time: float
    destination: Cell


@dataclass
class Connector:
    a: Cell
    b: Cell
    in_transit: list[Deposit] = field(default_factory=list)

    @property
    def current_load(self) -> int:
        return len(self.in_transit)


# Functions implemented in Tasks 4-5.
def emit_deposit(connector: Connector, source: Cell, propagation_time_base: float) -> None:
    raise NotImplementedError


def propagate_step(connector: Connector, load_coefficient: float) -> list[Deposit]:
    raise NotImplementedError
