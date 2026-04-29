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


def emit_deposit(connector: Connector, source: Cell, propagation_time_base: float) -> None:
    """Add a deposit to the connector traveling from source to the other endpoint."""
    if source == connector.a:
        destination = connector.b
    elif source == connector.b:
        destination = connector.a
    else:
        raise ValueError(
            f"source {source} is not an endpoint of connector "
            f"({connector.a}, {connector.b})"
        )
    connector.in_transit.append(
        Deposit(remaining_propagation_time=propagation_time_base, destination=destination)
    )


def propagate_step(connector: Connector, load_coefficient: float) -> list[Deposit]:
    """Advance all in-transit deposits by 1/(1 + load_coefficient * current_load).

    Returns the list of deposits that arrived this step (and removes them from in_transit).
    """
    advance = 1.0 / (1.0 + load_coefficient * connector.current_load)
    arrived: list[Deposit] = []
    remaining: list[Deposit] = []
    for d in connector.in_transit:
        d.remaining_propagation_time -= advance
        if d.remaining_propagation_time <= 0:
            arrived.append(d)
        else:
            remaining.append(d)
    connector.in_transit = remaining
    return arrived
