# gamma_field_core.py
"""
Core (high-frequency) component of the GammaField.

- Stores core mask and values in reference (comoving) coordinates.
- Supports baking per-entity core emission, limited growth (pixels/tick),
  decay, and snapshot/diff helpers for sliding window.
"""

import numpy as np
from scipy.ndimage import binary_dilation  # optional; fallback provided

H = W = 512

class GammaFieldCore:
    def __init__(self, shape=(H, W), decay=0.99):
        self.shape = shape
        self.values = np.zeros(shape, dtype=np.float32)  # intensity
        self.mask = np.zeros(shape, dtype=bool)         # core occupancy
        self.decay = decay

    def bake_blob(self, center_ref, radius_px, intensity, kernel='gauss'):
        """
        Add a core blob in reference coordinates.
        center_ref: (x_idx, y_idx) in grid indices (reference)
        radius_px: radius in pixels (reference grid)
        intensity: peak intensity to add
        """
        cx, cy = int(center_ref[0]), int(center_ref[1])
        y, x = np.ogrid[:self.shape[0], :self.shape[1]]
        dist2 = (x - cx)**2 + (y - cy)**2
        mask = dist2 <= (radius_px**2)
        if kernel == 'gauss':
            sigma = max(1.0, radius_px / 2.0)
            add = intensity * np.exp(-dist2 / (2 * sigma * sigma))
        else:
            add = intensity * mask.astype(np.float32)
        self.values[mask] += add[mask]
        self.mask |= mask

    def decay_tick(self):
        self.values *= self.decay
        # optionally shrink mask where values drop below threshold
        self.mask &= (self.values > 1e-4)

    def grow_limited(self, max_growth=1, energy_split=0.1):
        """
        Dilate mask by max_growth pixels, add small energy to new pixels.
        energy_split: fraction of core energy moved to new pixels (0..1)
        """
        try:
            dilated = binary_dilation(self.mask, iterations=max_growth)
        except Exception:
            # fallback simple dilation
            from scipy.ndimage import grey_dilation
            dilated = grey_dilation(self.mask.astype(np.uint8), size=(3,3)) > 0

        new_pixels = dilated & (~self.mask)
        if not new_pixels.any():
            self.mask = dilated
            return

        total_core_energy = self.values[self.mask].sum()
        added_energy_total = total_core_energy * energy_split
        # distribute added energy proportionally (uniform)
        count_new = new_pixels.sum()
        if count_new > 0:
            add_per_pixel = added_energy_total / count_new
            self.values[new_pixels] += add_per_pixel
            # subtract from core to conserve (approx)
            self.values[self.mask] *= (1.0 - energy_split)
        self.mask = dilated

    def snapshot(self):
        return {
            'values': self.values.copy(),
            'mask': self.mask.copy()
        }

    def apply_snapshot(self, snap):
        self.values = snap['values'].copy()
        self.mask = snap['mask'].copy()
