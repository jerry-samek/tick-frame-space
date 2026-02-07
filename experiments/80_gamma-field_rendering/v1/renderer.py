# renderer.py
"""
Renderer glue: combine core and residual fields into an RGB image for display.
Simple linear blending and gamma correction.
"""

import numpy as np

def combine_core_residual(core_values, residual_field, core_weight=0.7, residual_weight=0.3):
    """
    core_values: 512x512 float (core intensity)
    residual_field: 512x512 float
    Returns RGB image (H,W,3) in 0..255 uint8
    """
    combined = core_weight * core_values + residual_weight * residual_field
    # simple tonemap: clamp and sqrt for mild contrast
    img = np.clip(combined, 0.0, None)
    img = np.sqrt(img)  # gamma-like
    # map to grayscale RGB
    img_rgb = np.stack([img, img, img], axis=-1)
    img_rgb = np.clip(img_rgb * 255.0, 0, 255).astype(np.uint8)
    return img_rgb
