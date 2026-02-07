#!/usr/bin/env python3
# quick_test.py - Quick test to see the rendering issue

import numpy as np
import pygame

pygame.init()
SCREEN = pygame.display.set_mode((512, 512))

# Create simple test pattern
img = np.zeros((512, 512, 3), dtype=np.uint8)

# White square at (100:150, 100:150) in numpy [row, col]
img[100:150, 100:150] = [255, 255, 255]

# Red square at (300:350, 200:250)
img[300:350, 200:250] = [255, 0, 0]

print("Created image with:")
print("  White square at rows[100:150], cols[100:150]")
print("  Red square at rows[300:350], cols[200:250]")

# Try approach: transpose
print("\nTrying np.transpose(img, (1,0,2))...")
img_t = np.transpose(img, (1, 0, 2))
print(f"  Shape before: {img.shape}")
print(f"  Shape after: {img_t.shape}")

surf = pygame.surfarray.make_surface(img_t)
print(f"  Surface size: {surf.get_size()}")

SCREEN.blit(surf, (0, 0))
pygame.display.flip()

# Wait a moment
import time
time.sleep(3)

pygame.quit()

print("\nIf white square is at TOP-LEFT and red at BOTTOM-RIGHT:")
print("  => Rendering is CORRECT")
print("\nIf white square is at LEFT and red at BOTTOM:")
print("  => There's a coordinate issue")
