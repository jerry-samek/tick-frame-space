"""Grid abstraction for v4 simulation.

Provides abstract Grid interface and HexGrid2D implementation.
Designed so a 3D grid can be swapped in later without changing
entity/field/world code.

Coordinate system (HexGrid2D):
  Axial (q, r) with implicit s = -q - r, pointy-top layout.
  Storage: 2D array indexed as array[r + R, q + R] where R = world radius.
"""

from abc import ABC, abstractmethod
from typing import Iterator
import math

import numpy as np


Position = tuple[int, ...]


# 6 axial direction vectors: E, NE, NW, W, SW, SE
HEX_DIRS = [(1, 0), (1, -1), (0, -1), (-1, 0), (-1, 1), (0, 1)]

_SQRT3 = math.sqrt(3)

# Precomputed Cartesian unit vectors for each hex direction (pointy-top)
HEX_DIR_VECTORS: list[tuple[float, float]] = []
for _dq, _dr in HEX_DIRS:
    _px = _SQRT3 * _dq + _SQRT3 / 2 * _dr
    _py = 1.5 * _dr
    _mag = math.sqrt(_px * _px + _py * _py)
    if _mag > 1e-12:
        HEX_DIR_VECTORS.append((_px / _mag, _py / _mag))
    else:
        HEX_DIR_VECTORS.append((0.0, 0.0))


class Grid(ABC):
    """Abstract grid interface for n-dimensional discrete spaces."""

    @abstractmethod
    def neighbors(self, pos: Position) -> list[Position]:
        """Return neighbor positions for the given position."""

    @abstractmethod
    def all_cells(self) -> Iterator[Position]:
        """Iterate over all valid cell positions."""

    @abstractmethod
    def neighbor_count(self) -> int:
        """Number of neighbors per cell (6 for hex, 26 for 3D cube)."""

    @abstractmethod
    def diffusion_weight(self) -> float:
        """Weight for averaging: 1 / (1 + neighbor_count).
        Hex: 1/7, 3D cube: 1/27."""

    @abstractmethod
    def is_valid(self, pos: Position) -> bool:
        """Check if position is within bounds."""

    @abstractmethod
    def cell_count(self) -> int:
        """Total number of valid cells."""

    @abstractmethod
    def make_field(self, fill: float = 0.0) -> np.ndarray:
        """Create a field array covering all cells, initialized to fill value."""

    @abstractmethod
    def get(self, field: np.ndarray, pos: Position) -> float:
        """Read value from field at position."""

    @abstractmethod
    def set(self, field: np.ndarray, pos: Position, val: float) -> None:
        """Set value in field at position."""

    @abstractmethod
    def add(self, field: np.ndarray, pos: Position, val: float) -> None:
        """Add value to field at position."""

    @abstractmethod
    def valid_mask(self) -> np.ndarray:
        """Boolean mask of valid cells in the field array."""


class HexGrid2D(Grid):
    """Hex grid using axial coordinates, pointy-top layout."""

    def __init__(self, radius: int):
        self.radius = radius
        self._side = 2 * radius + 1
        self._mask = self._make_valid_mask()
        self._cell_count = int(np.sum(self._mask))
        self._all_cells: list[Position] | None = None

    def _make_valid_mask(self) -> np.ndarray:
        R = self.radius
        side = self._side
        mask = np.zeros((side, side), dtype=bool)
        for r in range(-R, R + 1):
            for q in range(-R, R + 1):
                if self._is_valid_hex(q, r):
                    mask[r + R, q + R] = True
        return mask

    def _is_valid_hex(self, q: int, r: int) -> bool:
        s = -q - r
        return max(abs(q), abs(r), abs(s)) <= self.radius

    def neighbors(self, pos: Position) -> list[Position]:
        q, r = pos
        result = []
        for dq, dr in HEX_DIRS:
            nq, nr = q + dq, r + dr
            if self._is_valid_hex(nq, nr):
                result.append((nq, nr))
        return result

    def all_cells(self) -> Iterator[Position]:
        if self._all_cells is None:
            self._all_cells = []
            R = self.radius
            for r in range(-R, R + 1):
                for q in range(-R, R + 1):
                    if self._is_valid_hex(q, r):
                        self._all_cells.append((q, r))
        return iter(self._all_cells)

    def neighbor_count(self) -> int:
        return 6

    def diffusion_weight(self) -> float:
        return 1.0 / 7.0

    def is_valid(self, pos: Position) -> bool:
        q, r = pos
        return self._is_valid_hex(q, r)

    def cell_count(self) -> int:
        return self._cell_count

    def make_field(self, fill: float = 0.0) -> np.ndarray:
        field = np.full((self._side, self._side), fill, dtype=np.float64)
        # Zero out invalid cells
        field[~self._mask] = 0.0
        return field

    def get(self, field: np.ndarray, pos: Position) -> float:
        q, r = pos
        R = self.radius
        return float(field[r + R, q + R])

    def set(self, field: np.ndarray, pos: Position, val: float) -> None:
        q, r = pos
        R = self.radius
        field[r + R, q + R] = val

    def add(self, field: np.ndarray, pos: Position, val: float) -> None:
        q, r = pos
        R = self.radius
        field[r + R, q + R] += val

    def valid_mask(self) -> np.ndarray:
        return self._mask


def hex_distance(pos1: Position, pos2: Position) -> int:
    """Manhattan distance on hex grid."""
    dq = pos1[0] - pos2[0]
    dr = pos1[1] - pos2[1]
    ds = -dq - dr
    return max(abs(dq), abs(dr), abs(ds))


def hex_to_pixel(q: int, r: int, size: float) -> tuple[float, float]:
    """Convert axial hex coords to screen pixel coords (pointy-top)."""
    x = size * (_SQRT3 * q + _SQRT3 / 2 * r)
    y = size * (1.5 * r)
    return x, y
