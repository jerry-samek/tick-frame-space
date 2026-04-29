# experiments/132_grow_until_observed/recording.py
"""Recording infrastructure for Phase 2: firing-event log + periodic snapshots."""
from dataclasses import dataclass, field

from capacitor import Cell
from connectors import Connector

CellPos = tuple[int, int, int]
ConnectorKey = tuple[CellPos, CellPos]


@dataclass
class Recorder:
    firings: list[tuple[int, CellPos]] = field(default_factory=list)
    snapshots: list[dict] = field(default_factory=list)

    def log_firings(self, tick: int, fired: list[CellPos]) -> None:
        for cell in fired:
            self.firings.append((tick, cell))

    def snapshot(
        self,
        tick: int,
        cells: dict[CellPos, Cell],
        connectors: list[Connector],
    ) -> None:
        thresholds = {pos: cell.threshold for pos, cell in cells.items()}
        loads = {(c.a, c.b): c.current_load for c in connectors}
        self.snapshots.append({
            "tick": tick,
            "thresholds": thresholds,
            "loads": loads,
        })
