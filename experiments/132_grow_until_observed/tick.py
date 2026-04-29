# experiments/132_grow_until_observed/tick.py
"""Per-tick driver: 5-step procedure per spec §"Three-Layer Mechanism"."""
from capacitor import Cell
from connectors import Connector
from parameters import Parameters


def tick(
    cells: dict[tuple[int, int, int], Cell],
    connectors: list[Connector],
    current_tick: int,
    params: Parameters,
) -> list[tuple[int, int, int]]:
    """Run one tick. Returns list of cells that fired this tick."""
    raise NotImplementedError
