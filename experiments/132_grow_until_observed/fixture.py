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
    4 connectors wiring the cycle.

    Bootstrap (per spec §"Initial bootstrap"):
      C0: charge = baseline_threshold (about to fire)
      C1: charge = 0.75 x baseline_threshold
      C2: charge = 0.50 x baseline_threshold
      C3: charge = 0.25 x baseline_threshold
    """
    cells: dict[tuple[int, int, int], Cell] = {}
    K = len(F1_CYCLE)
    for i, pos in enumerate(F1_CYCLE):
        # Cell at cycle position i gets charge = (1 - i*bootstrap_charge_step) * baseline_threshold
        # for K=4 with default 0.25: positions 0,1,2,3 -> fractions 1.00, 0.75, 0.50, 0.25
        fraction = 1.0 - i * params.bootstrap_charge_step
        cells[pos] = Cell(
            charge_level=fraction * params.baseline_threshold,
            threshold=params.baseline_threshold,
            last_discharge_tick=-1,
            state=CellState.CHARGING,
        )

    connectors: list[Connector] = []
    for i in range(K):
        a = F1_CYCLE[i]
        b = F1_CYCLE[(i + 1) % K]
        connectors.append(Connector(a=a, b=b))

    return cells, connectors
