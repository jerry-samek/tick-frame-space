import numpy as np
from dataclasses import dataclass, field

from constants import ALPHA_IMPRINT, DECAY, SPREAD_FRACTION, WORLD_RADIUS
from hex_grid import (
    hex_neighbors, hex_get, hex_set,
    is_valid_hex, make_valid_mask, HEX_DIR_VECTORS,
)


# ==========================
# Hill (hex grid)
# ==========================

@dataclass
class Hill:
    height: np.ndarray          # shape (2R+1, 2R+1)
    radius: int = WORLD_RADIUS
    alpha: float = ALPHA_IMPRINT
    decay: float = DECAY
    _valid_mask: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        self._valid_mask = make_valid_mask(self.radius)
        # Zero out invalid cells on initial height
        self.height[~self._valid_mask] = 0.0

    def height_at(self, q: int, r: int) -> float:
        """Read height at axial coords."""
        return hex_get(self.height, q, r, self.radius)

    def set_height(self, q: int, r: int, val: float):
        """Set height at axial coords."""
        hex_set(self.height, q, r, self.radius, val)

    def gradient_at(self, q: int, r: int) -> np.ndarray:
        """Weighted vector sum of 6 neighbor height differences (spec Option B).
        Returns Cartesian 2D vector."""
        R = self.radius
        hc = hex_get(self.height, q, r, R)
        gx, gy = 0.0, 0.0
        for i, (nq, nr) in enumerate(hex_neighbors(q, r)):
            if is_valid_hex(nq, nr, R):
                nh = hex_get(self.height, nq, nr, R)
            else:
                nh = hc  # boundary: treat as same height (reflect)
            diff = nh - hc
            gx += diff * HEX_DIR_VECTORS[i][0]
            gy += diff * HEX_DIR_VECTORS[i][1]
        return np.array([gx, gy], dtype=float)

    def spread(self):
        """Hex neighbor averaging diffusion.
        Each valid cell keeps (1 - 6*fraction), shares fraction to each neighbor.
        Boundary neighbors reflect back (their share stays with the cell)."""
        R = self.radius
        frac = SPREAD_FRACTION
        keep = 1.0 - 6 * frac
        new_height = np.zeros_like(self.height)

        for r in range(-R, R + 1):
            for q in range(-R, R + 1):
                if not is_valid_hex(q, r, R):
                    continue
                h = self.height[r + R, q + R]
                reflected = 0.0
                new_height[r + R, q + R] += keep * h
                for nq, nr in hex_neighbors(q, r):
                    if is_valid_hex(nq, nr, R):
                        new_height[nr + R, nq + R] += frac * h
                    else:
                        reflected += frac * h
                new_height[r + R, q + R] += reflected

        self.height = new_height

    def commit(self, imprint_field: np.ndarray):
        """Hill update: entity-built imprints + spread + decay.
        No source term, no renormalization — hills grow from entity imprints."""
        self.height += self.alpha * imprint_field
        self.spread()
        self.height *= self.decay
        np.maximum(self.height, 0.0, out=self.height)
        self.height[~self._valid_mask] = 0.0
