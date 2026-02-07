# core_growth.py
"""
Utilities for controlled core growth and energy bookkeeping.
"""

import numpy as np
from scipy.ndimage import binary_dilation

def morphological_dilate(mask, radius=1):
    """
    Dilate boolean mask by radius (iterations).
    """
    return binary_dilation(mask, iterations=radius)

def distribute_growth_energy(core_values, new_pixels_mask, fraction=0.1):
    """
    Compute energy to add to new pixels based on existing core energy.
    fraction: fraction of core energy to move into new pixels.
    Returns an array of same shape with added energy at new pixels.
    """
    total_core = core_values.sum()
    added_total = total_core * fraction
    count_new = new_pixels_mask.sum()
    if count_new == 0:
        return np.zeros_like(core_values)
    add_per = added_total / count_new
    added = np.zeros_like(core_values)
    added[new_pixels_mask] = add_per
    return added
