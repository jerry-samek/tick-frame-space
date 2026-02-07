# test_transpose_effect.py
"""
Test the effect of transpose on rendering.
Shows both transposed and non-transposed versions side by side.
"""

import numpy as np
import pygame
from gamma_field_core import GammaFieldCore
from gamma_field_residual import GammaFieldResidual
from renderer import combine_core_residual

pygame.init()

# Create a test image with a circle at (300, 200)
core = GammaFieldCore()
res = GammaFieldResidual()

center = (300, 200)  # X=300 (sloupeček), Y=200 (řádek)
radius = 40

core.bake_blob(center_ref=center, radius_px=radius, intensity=5.0)
img = combine_core_residual(core.values, res.field)

print(f"Circle at position: X={center[0]}, Y={center[1]}")
print(f"Image shape: {img.shape}")

# Find actual position in image
nonzero = np.where(img[:, :, 0] > 0)
if len(nonzero[0]) > 0:
    y_min, y_max = nonzero[0].min(), nonzero[0].max()
    x_min, x_max = nonzero[1].min(), nonzero[1].max()
    center_y = (y_min + y_max) / 2
    center_x = (x_min + x_max) / 2
    print(f"Actual rendered position: X={center_x:.0f}, Y={center_y:.0f}")

# Create two surfaces: one without transpose, one with transpose
screen = pygame.display.set_mode((1024, 512))
clock = pygame.time.Clock()

# Without transpose: (512, 512, 3) directly
try:
    surf_no_trans = pygame.surfarray.make_surface(img)
except:
    # If it fails due to size mismatch, use swapaxes to make it (W, H, 3)
    surf_no_trans = pygame.surfarray.make_surface(np.swapaxes(img, 0, 1))

# With transpose: (512, 512, 3) -> (512, 512, 3) but with swapped axes
img_trans = np.transpose(img, (1, 0, 2))
surf_with_trans = pygame.surfarray.make_surface(img_trans)

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((0, 0, 0))

    # Draw left side: without transpose
    screen.blit(surf_no_trans, (0, 0))
    font = pygame.font.Font(None, 24)
    text_left = font.render("No Transpose", True, (255, 255, 255))
    screen.blit(text_left, (10, 10))
    text_left2 = font.render(f"Expected at X=300,Y=200", True, (255, 255, 0))
    screen.blit(text_left2, (10, 40))

    # Draw right side: with transpose
    screen.blit(surf_with_trans, (512, 0))
    text_right = font.render("With Transpose (1,0,2)", True, (255, 255, 255))
    screen.blit(text_right, (512+10, 10))
    text_right2 = font.render(f"Swapped X<->Y", True, (255, 255, 0))
    screen.blit(text_right2, (512+10, 40))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

print("\nCompare the two images:")
print("Left:  Circle should be at X=300 (right side), Y=200 (near top)")
print("Right: If transpose swaps axes, circle should be at Y=300 (right side), X=200 (near top)")
print("       Which means position becomes (200, 300) instead of (300, 200)")
