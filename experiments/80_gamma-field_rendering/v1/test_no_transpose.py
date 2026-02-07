# test_no_transpose.py
"""
Test rendering WITHOUT transpose to see if that's the issue.
"""

import numpy as np
import pygame
from gamma_field_core import GammaFieldCore
from gamma_field_residual import GammaFieldResidual
from renderer import combine_core_residual

pygame.init()
SCREEN = pygame.display.set_mode((512, 512))
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 20)

# Create fields
core = GammaFieldCore()
res = GammaFieldResidual()

# Entity that orbits
orbit_center = np.array([256.0, 256.0])
orbit_radius = 80.0
entity_radius = 8
angular_speed = 0.01

frame = 0
running = True

while running:
    frame += 1
    CLOCK.tick(30)

    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # Reset fields
    core = GammaFieldCore()
    res = GammaFieldResidual()

    # Entity position on circle
    angle = angular_speed * frame
    entity_pos = orbit_center + orbit_radius * np.array([np.cos(angle), np.sin(angle)])

    # Bake
    core.bake_blob(center_ref=entity_pos, radius_px=entity_radius, intensity=5.0)

    # Render
    img = combine_core_residual(core.values, res.field)

    # Try TWO approaches side by side
    # Left half: direct (no transpose, but wrong size)
    # Right half: transposed (correct size but axes swapped)

    # Approach 1: Try to render directly
    # We need to handle the size mismatch - pygame expects (W, H, 3)
    # Create a new surface manually
    surf = pygame.Surface((512, 512))

    # Draw the image pixel by pixel (slow but accurate)
    for y in range(512):
        for x in range(512):
            color = tuple(img[y, x].astype(int))
            surf.set_at((x, y), color)

    SCREEN.blit(surf, (0, 0))

    # Draw info
    text = FONT.render(f"Frame {frame} | Angle {angle:.2f} rad | Pos ({entity_pos[0]:.0f}, {entity_pos[1]:.0f})", True, (255,255,255))
    SCREEN.blit(text, (5, 5))

    pygame.display.flip()

    if frame > 600:  # Run for ~20 seconds at 30 fps
        running = False

pygame.quit()
print("Test complete. Entity should trace a perfect circle on screen.")
