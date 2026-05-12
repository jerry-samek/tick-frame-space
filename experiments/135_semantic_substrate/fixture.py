from __future__ import annotations
import random

from cell import Cell
from substrate import Substrate


def build_k6_ring(substrate: Substrate) -> list[Cell]:
    cells = [Cell(spectrum={i}) for i in range(6)]
    for c in cells:
        substrate.add_cell(c)
    for i, c in enumerate(cells):
        prev_c = cells[(i - 1) % 6]
        next_c = cells[(i + 1) % 6]
        c.connectors.extend([prev_c, next_c])
    return cells


def attach_observer(
    substrate: Substrate,
    host: Cell,
    learning_threshold: int = 200,
    crystallization_size: int = 3,
) -> Cell:
    """Add a Learning observer cell bidirectionally connected to `host`."""
    observer = Cell(
        spectrum=set(),
        learning_threshold=learning_threshold,
        crystallization_size=crystallization_size,
    )
    substrate.add_cell(observer)
    host.connectors.append(observer)
    observer.connectors.append(host)
    return observer


class Injector:
    def __init__(
        self,
        seed: int,
        known_alphabet: tuple[int, ...] = (0, 1, 2, 3, 4, 5),
        unknown_alphabet: tuple[int, ...] = (6, 7, 8, 9, 10),
        known_probability: float = 0.5,
    ) -> None:
        self.rng = random.Random(seed)
        self.known_alphabet = known_alphabet
        self.unknown_alphabet = unknown_alphabet
        self.known_probability = known_probability

    def next_token(self) -> int:
        if self.rng.random() < self.known_probability:
            return self.rng.choice(self.known_alphabet)
        return self.rng.choice(self.unknown_alphabet)
