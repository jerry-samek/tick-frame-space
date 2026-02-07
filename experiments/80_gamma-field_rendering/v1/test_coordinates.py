# test_coordinates.py
"""
Test script to debug coordinate system and rendering issues.
"""

import numpy as np
import pygame

# Test 1: Simple circle rendering
print("=" * 60)
print("TEST 1: Circle rendering with different transpose options")
print("=" * 60)

H, W = 512, 512
img = np.zeros((H, W, 3), dtype=np.uint8)

# Draw a circle at (256, 256) with radius 50
cx, cy = 256, 256
radius = 50

y, x = np.ogrid[:H, :W]
dist2 = (x - cx)**2 + (y - cy)**2
mask = dist2 <= (radius**2)
img[mask] = [255, 128, 0]  # orange circle

print(f"Circle center (logical): ({cx}, {cy})")
print(f"Image shape: {img.shape}")
print(f"Circle pixels count: {mask.sum()}")

# Test rendering with pygame
pygame.init()
screen = pygame.display.set_mode((512, 512))

# Option A: No transpose (direct)
print("\nOption A: Direct image (no transpose)")
surf_a = pygame.surfarray.make_surface(img)
print(f"Surface size: {surf_a.get_size()}")

# Option B: Transpose (1, 0, 2)
print("\nOption B: Transpose (1,0,2) - swap H and W")
surf_b = pygame.surfarray.make_surface(np.transpose(img, (1,0,2)))
print(f"Surface size: {surf_b.get_size()}")

# Test 2: Coordinate mapping
print("\n" + "=" * 60)
print("TEST 2: Understanding pygame vs numpy indexing")
print("=" * 60)

print("""
NumPy/OpenCV convention:
  - img[row, col] or img[y, x]
  - First dimension is vertical (rows = Y)
  - Second dimension is horizontal (cols = X)
  - Shape is (H, W, C)

Pygame convention:
  - Surface is created from (W, H) or interpreted as (W, H)
  - pygame.surfarray.make_surface expects (width, height, channels)
  - But numpy arrays are (height, width, channels)
  
Transpose (1,0,2):
  - (H, W, C) -> (W, H, C) 
  - This SWAPS the spatial dimensions
  - This is WRONG for displaying a standard image!
""")

# Test 3: Check what make_surface actually does
print("\n" + "=" * 60)
print("TEST 3: Direct pygame behavior")
print("=" * 60)

# Create a simple test pattern
test_img = np.zeros((100, 200, 3), dtype=np.uint8)  # 100 height, 200 width
test_img[:, :100] = [255, 0, 0]  # Left half red
test_img[:, 100:] = [0, 0, 255]  # Right half blue

print(f"Test image shape: {test_img.shape} (H=100, W=200)")
print("Expected: Red vertical bar on left (width 100), Blue on right (width 100)")

surf_test = pygame.surfarray.make_surface(test_img)
print(f"Surface size after make_surface: {surf_test.get_size()}")
print("If size is (100, 200): make_surface treats first dim as W, second as H - WRONG!")
print("If size is (200, 100): dimensions got swapped - might need transpose or different indexing")

pygame.quit()

print("\n" + "=" * 60)
print("CONCLUSION")
print("=" * 60)
print("""
The issue is likely:
1. make_surface expects (W, H, C) but gets (H, W, C) from numpy
2. We need to either:
   - Use np.transpose(img, (1, 0, 2)) to convert (H,W,C) -> (W,H,C) OR
   - Use numpy swapaxes or proper rotation
   
But the current code DOES use transpose(1,0,2), which should be correct!
So the problem might be elsewhere - in how coordinates are baked.

Check: Are (x,y) coordinates being passed correctly to bake_blob?
""")
