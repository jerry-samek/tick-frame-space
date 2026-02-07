# remap.py
"""
Remapping utilities: remap residual field between scales while keeping fixed 512 grid.
Clipping policy: anything outside source bounds contributes zero (discarded).
Intensity normalization: divide by scale^2 (2D) to approximate energy conservation.
"""

import numpy as np

def pixel_to_physical(i, j, s, world_center=(0.5, 0.5), base_extent=1.0):
    """
    Map pixel indices (i,j) in 512 grid to physical coordinates in normalized [0,1] range.
    base_extent is the physical size at s=1. world_center is normalized center.
    """
    H = W = 512
    extent = base_extent * s
    # physical min corner
    min_x = world_center[0] - extent / 2.0
    min_y = world_center[1] - extent / 2.0
    u = (i + 0.5) / W
    v = (j + 0.5) / H
    x_phys = min_x + u * extent
    y_phys = min_y + v * extent
    return x_phys, y_phys

def physical_to_source_uv(x_phys, y_phys, s_old, world_center=(0.5,0.5), base_extent=1.0):
    """
    Map physical coordinate to normalized uv in source field (0..1).
    """
    H = W = 512
    extent_old = base_extent * s_old
    min_x = world_center[0] - extent_old / 2.0
    min_y = world_center[1] - extent_old / 2.0
    u = (x_phys - min_x) / extent_old
    v = (y_phys - min_y) / extent_old
    return u, v

def bilinear_sample_field(field, u, v):
    """
    Sample field (512x512) at normalized coords u,v in [0,1] using bilinear interpolation.
    If outside [0,1], return 0.
    """
    H, W = field.shape
    if u < 0 or u > 1 or v < 0 or v > 1:
        return 0.0
    x = u * (W - 1)
    y = v * (H - 1)
    x0 = int(np.floor(x)); x1 = min(x0 + 1, W - 1)
    y0 = int(np.floor(y)); y1 = min(y0 + 1, H - 1)
    wx = x - x0; wy = y - y0
    v00 = field[y0, x0]; v10 = field[y0, x1]
    v01 = field[y1, x0]; v11 = field[y1, x1]
    return (v00 * (1 - wx) * (1 - wy) +
            v10 * wx * (1 - wy) +
            v01 * (1 - wx) * wy +
            v11 * wx * wy)

def remap_residual_to_fixed_grid(field_old, s_old, s_new, world_center=(0.5,0.5), base_extent=1.0):
    """
    Remap field_old (512x512) from scale s_old to new scale s_new, returning new 512x512.
    Values outside source bounds are treated as zero (discarded).
    Intensity normalized by (s_new/s_old)^2 (2D).
    """
    H = W = field_old.shape
    H = field_old.shape[0]
    field_new = np.zeros_like(field_old)
    scale_ratio = s_new / s_old
    for j in range(H):
        for i in range(H):
            x_phys, y_phys = pixel_to_physical(i, j, s_new, world_center, base_extent)
            u_src, v_src = physical_to_source_uv(x_phys, y_phys, s_old, world_center, base_extent)
            val = bilinear_sample_field(field_old, u_src, v_src)
            # normalize intensity for 2D
            field_new[j, i] = val / (scale_ratio * scale_ratio)
    return field_new
