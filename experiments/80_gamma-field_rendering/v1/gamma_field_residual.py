# gamma_field_residual.py
"""
Residual (low-frequency) component of the GammaField.

- Stores a 512x512 float field in the fixed viewport grid.
- Supports baking diffuse emission, decay, and simple diagnostics.
"""

import numpy as np

H = W = 512

class GammaFieldResidual:
    def __init__(self, shape=(H, W), decay=0.995):
        self.shape = shape
        self.field = np.zeros(shape, dtype=np.float32)
        self.decay = decay

    def bake_point(self, phys_x_idx, phys_y_idx, strength, radius=3):
        """
        Add a diffuse contribution centered at integer grid indices.
        phys_x_idx, phys_y_idx: target indices in fixed 512 grid
        """
        cx, cy = int(phys_x_idx), int(phys_y_idx)
        y, x = np.ogrid[:self.shape[0], :self.shape[1]]
        dist2 = (x - cx)**2 + (y - cy)**2
        mask = dist2 <= (radius**2)
        sigma = max(1.0, radius / 2.0)
        add = strength * np.exp(-dist2 / (2 * sigma * sigma))
        # clip to bounds automatically via mask
        self.field[mask] += add[mask]

    def decay_tick(self):
        self.field *= self.decay

    def snapshot_lowres(self, factor=8):
        """
        Return a low-res copy for sliding window (e.g., 64x64).
        """
        h, w = self.shape
        fh, fw = h // factor, w // factor
        # simple block average
        return self.field.reshape(fh, factor, fw, factor).mean(axis=(1,3))

    def apply_lowres_snapshot(self, lowres, factor=8):
        # upsample by nearest for quick restore (used only for diagnostics)
        self.field = np.kron(lowres, np.ones((factor, factor))).astype(np.float32)
