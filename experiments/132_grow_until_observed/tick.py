"""Per-tick driver: 5-step procedure per spec §"Three-Layer Mechanism".

Order:
  1. Threshold relaxation for all cells.
  2. Connector propagation (advance deposits, collect arrivals).
  3. Charge accumulation (add arriving deposits to receiver charge).
  4. Threshold check + firing (cells whose charge >= threshold fire).
  5. State cleanup (DISCHARGED -> EMPTY).
"""
from capacitor import Cell, CellState, check_and_fire, relax_threshold
from connectors import Connector, emit_deposit, propagate_step
from parameters import Parameters

Cell_t = tuple[int, int, int]


def build_connector_index(
    connectors: list[Connector],
) -> dict[Cell_t, list[Connector]]:
    """Build a mapping from each cell position to the list of connectors that
    touch it. Used to avoid an O(connectors) scan per fire in tick()."""
    index: dict[Cell_t, list[Connector]] = {}
    for conn in connectors:
        index.setdefault(conn.a, []).append(conn)
        index.setdefault(conn.b, []).append(conn)
    return index


def tick(
    cells: dict[tuple[int, int, int], Cell],
    connectors: list[Connector],
    current_tick: int,
    params: Parameters,
    connector_index: dict[Cell_t, list[Connector]] | None = None,
) -> list[tuple[int, int, int]]:
    """Run one tick. Returns list of cells that fired this tick.

    If `connector_index` is provided, it is used in Step 4 instead of scanning
    the full connector list. For small substrates the build cost of the index
    is negligible; for large substrates callers should build it once and reuse.
    """
    if connector_index is None:
        connector_index = build_connector_index(connectors)

    # Step 1: threshold relaxation
    for cell in cells.values():
        relax_threshold(cell, current_tick, params.baseline_threshold, params.relaxation_rate)

    # Step 2: connector propagation
    arrivals: list = []
    for conn in connectors:
        arrivals.extend(propagate_step(conn, params.load_coefficient))

    # Step 3: charge accumulation at receivers
    for d in arrivals:
        if d.destination in cells:
            cells[d.destination].charge_level += params.deposit_amount

    # Step 4: threshold check + firing
    fired_cells: list[tuple[int, int, int]] = []
    for cell_pos, cell in cells.items():
        if check_and_fire(cell, current_tick, params.adaptation_rate):
            fired_cells.append(cell_pos)
            for conn in connector_index.get(cell_pos, []):
                emit_deposit(conn, source=cell_pos, propagation_time_base=params.propagation_time_base)

    # Step 5: state cleanup
    for cell in cells.values():
        if cell.state == CellState.DISCHARGED:
            cell.state = CellState.EMPTY

    return fired_cells
