# test_circle_rendering.py
"""
Direct test of circle rendering to identify the rectangle problem.
"""

import numpy as np
import pygame

pygame.init()

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

# Test different rendering approaches
screen = pygame.display.set_mode((512, 512))
pygame.display.set_caption("Circle Test - Press Q to exit")

clock = pygame.time.Clock()
running = True
test_case = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                running = False
            elif event.key == pygame.K_SPACE:
                test_case = (test_case + 1) % 3

    screen.fill((0, 0, 0))

    if test_case == 0:
        # Direct make_surface (wrong size interpretation)
        surf = pygame.surfarray.make_surface(img)
        title = "Test 0: Direct make_surface (img shape=(H,W,3))"
    elif test_case == 1:
        # Transposed (1,0,2)
        surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
        title = "Test 1: Transposed (1,0,2)"
    else:
        # Swapaxes
        surf = pygame.surfarray.make_surface(np.swapaxes(img, 0, 1))
        title = "Test 2: Swapaxes(0,1)"

    screen.blit(surf, (0, 0))
    pygame.display.set_caption(title + " - Press SPACE to cycle, Q to exit")
    clock.tick(60)

pygame.quit()
print("Done. Circle should appear at center of screen in all cases as red circle.")
