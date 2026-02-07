import numpy as np
from dataclasses import dataclass, field
from scipy.ndimage import gaussian_filter

from constants import DELTA_H, ALPHA_IMPRINT, DECAY, SPREAD_SIGMA


# ==========================
# Hill (2D)
# ==========================

@dataclass
class Hill:
    height: np.ndarray          # shape (N, N)
    delta_H: float = DELTA_H
    alpha: float = ALPHA_IMPRINT
    decay: float = DECAY
    source: np.ndarray = field(default=None, repr=False)

    def __post_init__(self):
        n = self.height.shape[0]
        cx, cy = n // 2, n // 2
        Y, X = np.mgrid[0:n, 0:n]
        self.source = self.delta_H * np.exp(
            -0.5 * ((X - cx)**2 + (Y - cy)**2) / 30.0**2
        )

    def gradient_at(self, x: int, y: int) -> np.ndarray:
        """Returns (gx, gy) gradient vector using central differences."""
        n = self.height.shape[0]
        # gx
        if x <= 0:
            gx = self.height[y, 1] - self.height[y, 0]
        elif x >= n - 1:
            gx = self.height[y, n - 1] - self.height[y, n - 2]
        else:
            gx = self.height[y, x + 1] - self.height[y, x - 1]
        # gy
        if y <= 0:
            gy = self.height[1, x] - self.height[0, x]
        elif y >= n - 1:
            gy = self.height[n - 1, x] - self.height[n - 2, x]
        else:
            gy = self.height[y + 1, x] - self.height[y - 1, x]

        return np.array([gx, gy], dtype=float)

    def spread(self):
        """2D Gaussian diffusion."""
        self.height = gaussian_filter(self.height, sigma=SPREAD_SIGMA)

    def commit(self, imprint_field: np.ndarray):
        """Hill update: growth + imprint + spread + decay + renormalization (1A).
        Renormalization to [0,1] replaces overflow handling — dynamics depend
        only on hill shape, not absolute magnitude (Doc 094)."""
        self.height += self.source
        self.height += self.alpha * imprint_field
        self.spread()
        self.height *= self.decay
        np.maximum(self.height, 0.0, out=self.height)

        # Renormalize to [0, 1] — curvature-only dynamics (1A, Doc 094)
        h_min = np.min(self.height)
        h_max = np.max(self.height)
        denom = h_max - h_min + 1e-10
        self.height = (self.height - h_min) / denom
