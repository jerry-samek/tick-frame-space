# analyze_coordinates.py
"""
Analyze the coordinate system and find why circles appear as rectangles.
This script visualizes the actual coordinates and the rendered output.
"""

import numpy as np
from gamma_field_core import GammaFieldCore
from gamma_field_residual import GammaFieldResidual
from renderer import combine_core_residual

# Create fields
core = GammaFieldCore()
res = GammaFieldResidual()

# Test 1: Static circle at (256, 256)
print("=" * 70)
print("TEST 1: Static circle at center (256, 256)")
print("=" * 70)

center = (256, 256)
radius = 50

core.bake_blob(center_ref=center, radius_px=radius, intensity=5.0)
img1 = combine_core_residual(core.values, res.field)

# Analyze the rendered image
# Find the bounding box of non-zero pixels
nonzero = np.where(img1[:, :, 0] > 0)
if len(nonzero[0]) > 0:
    y_min, y_max = nonzero[0].min(), nonzero[0].max()
    x_min, x_max = nonzero[1].min(), nonzero[1].max()
    height = y_max - y_min
    width = x_max - x_min
    center_y = (y_min + y_max) / 2
    center_x = (x_min + x_max) / 2

    print(f"Bounding box in image:")
    print(f"  X (columns): {x_min} to {x_max} (width = {width})")
    print(f"  Y (rows):    {y_min} to {y_max} (height = {height})")
    print(f"  Center:      ({center_x:.1f}, {center_y:.1f})")
    print(f"  Expected center: {center}")
    print(f"  Aspect ratio (width/height): {width/height:.3f}")
else:
    print("No pixels rendered!")

print()

# Test 2: Circle at (200, 256) - offset in X
print("=" * 70)
print("TEST 2: Circle at X=200, Y=256 (offset in X)")
print("=" * 70)

core = GammaFieldCore()  # Reset
res = GammaFieldResidual()
center2 = (200, 256)

core.bake_blob(center_ref=center2, radius_px=radius, intensity=5.0)
img2 = combine_core_residual(core.values, res.field)

nonzero2 = np.where(img2[:, :, 0] > 0)
if len(nonzero2[0]) > 0:
    y_min, y_max = nonzero2[0].min(), nonzero2[0].max()
    x_min, x_max = nonzero2[1].min(), nonzero2[1].max()
    height = y_max - y_min
    width = x_max - x_min
    center_y = (y_min + y_max) / 2
    center_x = (x_min + x_max) / 2

    print(f"Bounding box in image:")
    print(f"  X (columns): {x_min} to {x_max} (width = {width})")
    print(f"  Y (rows):    {y_min} to {y_max} (height = {height})")
    print(f"  Center:      ({center_x:.1f}, {center_y:.1f})")
    print(f"  Expected center: {center2}")
    print(f"  Aspect ratio (width/height): {width/height:.3f}")
else:
    print("No pixels rendered!")

print()

# Test 3: Circle at (256, 200) - offset in Y
print("=" * 70)
print("TEST 3: Circle at X=256, Y=200 (offset in Y)")
print("=" * 70)

core = GammaFieldCore()  # Reset
res = GammaFieldResidual()
center3 = (256, 200)

core.bake_blob(center_ref=center3, radius_px=radius, intensity=5.0)
img3 = combine_core_residual(core.values, res.field)

nonzero3 = np.where(img3[:, :, 0] > 0)
if len(nonzero3[0]) > 0:
    y_min, y_max = nonzero3[0].min(), nonzero3[0].max()
    x_min, x_max = nonzero3[1].min(), nonzero3[1].max()
    height = y_max - y_min
    width = x_max - x_min
    center_y = (y_min + y_max) / 2
    center_x = (x_min + x_max) / 2

    print(f"Bounding box in image:")
    print(f"  X (columns): {x_min} to {x_max} (width = {width})")
    print(f"  Y (rows):    {y_min} to {y_max} (height = {height})")
    print(f"  Center:      ({center_x:.1f}, {center_y:.1f})")
    print(f"  Expected center: {center3}")
    print(f"  Aspect ratio (width/height): {width/height:.3f}")
else:
    print("No pixels rendered!")

print()
print("=" * 70)
print("SUMMARY")
print("=" * 70)
print("""
If aspect ratio ≠ 1.0, then circles are being rendered as rectangles/ellipses.
This would indicate a problem in the coordinate transformation.

Possible causes:
1. bake_blob uses (cx, cy) incorrectly
2. numpy ogrid is not creating the correct distance field
3. The rendering/transposition is distorting the image
""")
