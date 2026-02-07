#!/usr/bin/env python3
# verify_rendering.py

import numpy as np
from PIL import Image
from gamma_field_core import GammaFieldCore
from gamma_field_residual import GammaFieldResidual
from renderer import combine_core_residual

# Create a circle at (256, 256)
core = GammaFieldCore()
res = GammaFieldResidual()

entity_pos = (256.0, 256.0)
entity_radius = 50

core.bake_blob(center_ref=entity_pos, radius_px=entity_radius, intensity=5.0)
img = combine_core_residual(core.values, res.field)

# Save as PNG
img_pil = Image.fromarray(img)
img_pil.save("circle_numpy.png")

# Also save transposed version
img_trans = np.transpose(img, (1, 0, 2))
img_trans_pil = Image.fromarray(img_trans)
img_trans_pil.save("circle_transposed.png")

# Analyze both
for name, array in [("numpy", img), ("transposed", img_trans)]:
    nonzero = np.where(array[:, :, 0] > 0)
    if len(nonzero[0]) > 0:
        y_vals = nonzero[0]
        x_vals = nonzero[1]
        width = x_vals.max() - x_vals.min()
        height = y_vals.max() - y_vals.min()
        aspect = width / height if height > 0 else 0
        print(f"{name:12}: width={width:3d}, height={height:3d}, aspect={aspect:.3f}")

print("\nSaved circle_numpy.png and circle_transposed.png")
print("Open these to see if the circles look the same or different")
