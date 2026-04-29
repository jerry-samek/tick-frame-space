# experiments/132_grow_until_observed/fixture.py
"""K=4 capacitor cycle fixture: cell layout + connector wiring + bootstrap."""
from capacitor import Cell, CellState
from connectors import Connector
from parameters import Parameters


# K=4 cycle on 2x2 square at z=0 (matching Exp 134 F1 fixture geometry).
F1_CYCLE = [
    (0, 0, 0),
    (1, 0, 0),
    (1, 1, 0),
    (0, 1, 0),
]


def setup_fixture(params: Parameters) -> tuple[
    dict[tuple[int, int, int], Cell],
    list[Connector],
]:
    """Build the K=4 capacitor cycle: 4 cells with staggered initial charges,
    4 connectors wiring the cycle, all other lattice cells empty."""
    raise NotImplementedError
