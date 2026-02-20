"""Gamma field: expansion, diffusion, deposit, gradient.

Implements the zero-parameter field dynamics:
  Rule 3 -- Expansion: gamma[all] += 1.0 each tick (field energy source)
  Rule 4 -- Diffusion: average with neighbors (weight = 1/7 for hex)
  Rule 2 -- Deposit/Imprint: entity adds energy to gamma at its position

No harvest -- entities are sources, not sinks.
"""

import math

import numpy as np
from scipy.ndimage import convolve

from grid import Grid, HexGrid2D, Position, HEX_DIRS, HEX_DIR_VECTORS


def _build_hex_kernel() -> np.ndarray:
    """Build 3x3 convolution kernel for hex neighbor averaging.

    Hex axial coordinates stored as array[r+R, q+R].
    The 6 hex neighbors of (q,r) are:
      (q+1, r)   -> array offset (0, +1)
      (q+1, r-1) -> array offset (-1, +1)
      (q,   r-1) -> array offset (-1, 0)
      (q-1, r)   -> array offset (0, -1)
      (q-1, r+1) -> array offset (+1, -1)
      (q,   r+1) -> array offset (+1, 0)

    Kernel (row=dr, col=dq):
        dq: -1  0  +1
    dr:-1  [ 0  1  1 ]
    dr: 0  [ 1  1  1 ]
    dr:+1  [ 1  1  0 ]

    Each cell sums self + 6 neighbors then divides by 7.
    """
    kernel = np.array([
        [0, 1, 1],
        [1, 1, 1],
        [1, 1, 0],
    ], dtype=np.float64)
    return kernel


class GammaField:
    """The gamma field substrate -- energy builds hills, not wells."""

    def __init__(self, grid: Grid):
        self.grid = grid
        self.gamma = grid.make_field(fill=0.0)
        self._mask = grid.valid_mask()

        # Precompute neighbor count per cell for boundary normalization
        if isinstance(grid, HexGrid2D):
            self._hex_kernel = _build_hex_kernel()
            ones = np.zeros_like(self.gamma)
            ones[self._mask] = 1.0
            self._neighbor_counts = convolve(
                ones, self._hex_kernel, mode='constant', cval=0.0)
            self._neighbor_counts[self._neighbor_counts == 0] = 1.0

    def expand(self) -> None:
        """Rule 3: Every cell gains +1.0 per tick. Parameterless."""
        self.gamma[self._mask] += 1.0

    def diffuse(self) -> None:
        """Rule 4: Each cell averages with its neighbors.

        For hex: new[c] = (gamma[c] + sum(gamma[valid neighbors])) / n_valid
        Uses scipy convolution for performance.
        Propagation speed = 1 cell/tick = c. Parameterless.
        """
        summed = convolve(self.gamma, self._hex_kernel, mode='constant', cval=0.0)
        self.gamma[self._mask] = summed[self._mask] / self._neighbor_counts[self._mask]

    def deposit(self, pos: Position, amount: float) -> None:
        """Rule 2: Entity deposits energy to gamma at its position.

        Entity is a source, not a sink. Builds the hill.
        Parameterless.
        """
        if amount <= 0:
            return
        self.grid.add(self.gamma, pos, amount)

    def value_at(self, pos: Position) -> float:
        """Get gamma value at position."""
        return self.grid.get(self.gamma, pos)

    def gradient_at(self, pos: Position) -> tuple[float, float, float]:
        """Compute gradient direction and magnitude at position.

        Returns (gx, gy, magnitude) where (gx, gy) is the Cartesian
        gradient vector pointing uphill (toward highest gamma).

        Uses hex neighbor values to compute weighted direction vector.
        """
        gx, gy = 0.0, 0.0
        center_val = self.grid.get(self.gamma, pos)

        for i, (dq, dr) in enumerate(HEX_DIRS):
            nq, nr = pos[0] + dq, pos[1] + dr
            npos = (nq, nr)
            if not self.grid.is_valid(npos):
                continue
            nval = self.grid.get(self.gamma, npos)
            diff = nval - center_val
            ux, uy = HEX_DIR_VECTORS[i]
            gx += diff * ux
            gy += diff * uy

        magnitude = math.sqrt(gx * gx + gy * gy)
        return gx, gy, magnitude

    def get_neighbor_values(self, pos: Position) -> list[tuple[Position, float]]:
        """Return (position, gamma_value) for all neighbors of pos."""
        result = []
        for n in self.grid.neighbors(pos):
            result.append((n, self.grid.get(self.gamma, n)))
        return result

    def total_energy(self) -> float:
        """Total gamma energy across all valid cells."""
        return float(np.sum(self.gamma[self._mask]))

    def max_value(self) -> float:
        """Maximum gamma value across valid cells."""
        vals = self.gamma[self._mask]
        return float(np.max(vals)) if len(vals) > 0 else 0.0

    def mean_value(self) -> float:
        """Mean gamma value across valid cells."""
        vals = self.gamma[self._mask]
        return float(np.mean(vals)) if len(vals) > 0 else 0.0

    def min_value(self) -> float:
        """Minimum gamma value across valid cells."""
        vals = self.gamma[self._mask]
        return float(np.min(vals)) if len(vals) > 0 else 0.0
