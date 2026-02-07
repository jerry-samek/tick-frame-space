# test_circle_offline.py
"""
Offline test to save rendered circles as PNG files to analyze the issue.
"""

import numpy as np
import pygame
from PIL import Image

# Create a simple circle manually
H, W = 512, 512
img = np.zeros((H, W, 3), dtype=np.uint8)

# Draw a circle at (256, 256) with radius 50
cx, cy = 256, 256
radius = 50

# Method: use numpy ogrid like in gamma_field_core
y, x = np.ogrid[:H, :W]
dist2 = (x - cx)**2 + (y - cy)**2
mask = dist2 <= (radius**2)

# Color the circle
img[mask] = [255, 0, 0]  # red

print(f"Circle created at ({cx}, {cy}) with radius {radius}")
print(f"Image shape: {img.shape}")
print(f"Pixels in circle: {mask.sum()}")

# Save original numpy array as-is
img_pil = Image.fromarray(img)
img_pil.save("test_original.png")
print("Saved: test_original.png (raw numpy array)")

# Test different rendering approaches
pygame.init()
screen = pygame.display.set_mode((512, 512))

# Test 0: Direct make_surface (wrong size interpretation)
try:
    surf0 = pygame.surfarray.make_surface(img)
    pygame.image.save(surf0, "test_0_direct.png")
    print(f"Test 0 (direct): Surface created with size {surf0.get_size()}")
except Exception as e:
    print(f"Test 0 failed: {e}")

# Test 1: Transposed (1,0,2)
try:
    img_trans = np.transpose(img, (1, 0, 2))
    surf1 = pygame.surfarray.make_surface(img_trans)
    pygame.image.save(surf1, "test_1_transpose.png")
    print(f"Test 1 (transpose): Surface created with size {surf1.get_size()}")
except Exception as e:
    print(f"Test 1 failed: {e}")

# Test 2: Swapaxes
try:
    img_swap = np.swapaxes(img, 0, 1)
    surf2 = pygame.surfarray.make_surface(img_swap)
    pygame.image.save(surf2, "test_2_swapaxes.png")
    print(f"Test 2 (swapaxes): Surface created with size {surf2.get_size()}")
except Exception as e:
    print(f"Test 2 failed: {e}")

# Test 3: No transformation, but understand what make_surface does
try:
    # According to pygame docs, make_surface expects (W, H, 3)
    # But numpy arrays are typically (H, W, 3)
    # So we need to figure out if make_surface interprets it differently

    # Create a test pattern: left half red, right half blue
    test = np.zeros((100, 200, 3), dtype=np.uint8)
    test[:, :100] = [255, 0, 0]  # left half
    test[:, 100:] = [0, 0, 255]  # right half

    test_pil = Image.fromarray(test)
    test_pil.save("test_pattern_orig.png")

    surf_test = pygame.surfarray.make_surface(test)
    pygame.image.save(surf_test, "test_pattern_pygame.png")
    print(f"Test pattern: Original shape {test.shape}, pygame surface size {surf_test.get_size()}")
except Exception as e:
    print(f"Test pattern failed: {e}")

pygame.quit()
print("\nAnalyze the generated PNG files to understand the rendering issue.")
