# test_entity_rendering.py
"""
Test to visualize entity position and its circle rendering.
Shows coordinates on screen to debug the rectangle problem.
"""

import numpy as np
import pygame
from scipy.ndimage import binary_dilation

pygame.init()
SCREEN = pygame.display.set_mode((512, 512))
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 20)

# Entity parameters
entity_center = np.array([256.0, 256.0])
orbit_radius = 80.0
entity_radius = 8  # radius in pixels
angular_speed = 0.01

clock_ticks = 0
running = True

# Create a test image with a circle
def draw_circle_at(pos, radius):
    """Draw a circle at position pos with given radius."""
    img = np.zeros((512, 512, 3), dtype=np.uint8)

    cx, cy = int(pos[0]), int(pos[1])
    y, x = np.ogrid[:512, :512]
    dist2 = (x - cx)**2 + (y - cy)**2
    mask = dist2 <= (radius**2)

    # Use gaussian for smooth circle
    sigma = max(1.0, radius / 2.0)
    intensity = np.exp(-dist2 / (2 * sigma * sigma))
    img[mask] = (255 * intensity[mask]).astype(np.uint8)

    # Also draw crosshair at actual position
    cv = int(pos[1])  # row
    cx_draw = int(pos[0])  # column

    # Horizontal line (row cv)
    if 0 <= cv < 512:
        img[cv, max(0, cx_draw-20):min(512, cx_draw+20)] = [0, 255, 0]

    # Vertical line (column cx_draw)
    if 0 <= cx_draw < 512:
        img[max(0, cv-20):min(512, cv+20), cx_draw] = [0, 255, 0]

    return img

frame_count = 0
while running:
    frame_count += 1
    t = frame_count

    CLOCK.tick(30)
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # Calculate entity position on circle
    angle = angular_speed * t
    entity_pos = entity_center + orbit_radius * np.array([np.cos(angle), np.sin(angle)])

    # Draw circle at entity position
    img = draw_circle_at(entity_pos, entity_radius)

    # Render using transpose like main.py does
    surf = pygame.surfarray.make_surface(np.transpose(img, (1, 0, 2)))
    SCREEN.blit(surf, (0, 0))

    # Draw debugging information
    text_lines = [
        f"Frame: {frame_count}",
        f"Angle: {angle:.2f} rad ({np.degrees(angle):.1f}°)",
        f"Entity pos (X,Y): ({entity_pos[0]:.1f}, {entity_pos[1]:.1f})",
        f"Entity at pixel (col, row): ({int(entity_pos[0])}, {int(entity_pos[1])})",
        f"Entity radius: {entity_radius} px",
        f"Orbit radius: {orbit_radius} px",
        "",
        "Green crosshair shows actual position",
        "Orange circle shows rendered blob"
    ]

    # Render text on black background strip
    y_offset = 5
    for line in text_lines:
        text_surf = FONT.render(line, True, (255, 255, 255))
        SCREEN.blit(text_surf, (5, y_offset))
        y_offset += 20

    pygame.display.flip()

pygame.quit()
print("Test completed. Check if the orange circles form a perfect circle pattern,")
print("and if the green crosshair marks the true center of the entity.")
