# main.py
"""
Minimal demo that ties modules together. Requires numpy and pygame.
Run to see a simple expanding residual and a comoving core blob that grows slowly.
"""

import pygame
import numpy as np
from gamma_field_core import GammaFieldCore
from gamma_field_residual import GammaFieldResidual
from remap import remap_residual_to_fixed_grid, pixel_to_physical, physical_to_source_uv
from core_growth import morphological_dilate, distribute_growth_energy
from sliding_window import SlidingWindow
from scene import Entity, update_orbit
from renderer import combine_core_residual

pygame.init()
SCREEN = pygame.display.set_mode((512, 512))
CLOCK = pygame.time.Clock()
FONT = pygame.font.Font(None, 20)

# instantiate
core = GammaFieldCore()
res = GammaFieldResidual()
window = SlidingWindow(max_size=32)

# example entity in reference grid indices (center)
# Entity orbits around (256, 256) with orbital radius
entity = Entity(uid=1, pos_ref=(256, 256), radius_ref=8, emission=5.0, mode='comoving')
orbit_center = np.array([256.0, 256.0])
orbit_radius = 80.0
angular_speed = 0.01  # radians per tick

s = 1.0
t = 0
running = True
while running:
    dt = CLOCK.tick(60) / 1000.0
    t += 1
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            running = False

    # Update entity position: circular orbit
    angle = angular_speed * t
    entity.pos_ref = orbit_center + orbit_radius * np.array([np.cos(angle), np.sin(angle)])

    # simulate: bake core and residual
    core.bake_blob(center_ref=entity.pos_ref, radius_px=entity.radius_ref, intensity=entity.emission)
    # map entity phys pos to fixed grid for residual bake (simple: use s to scale)
    phys_x = int(entity.pos_ref[0])  # already in grid indices for demo
    phys_y = int(entity.pos_ref[1])
    res.bake_point(phys_x, phys_y, strength=entity.emission * 0.1, radius=6)

    # occasionally expand s
    if t % 120 == 0:
        s_old = s
        s = s * 1.1  # expand 10%
        # remap residual conservatively
        res.field = remap_residual_to_fixed_grid(res.field, s_old, s)
        # grow core limited
        core.grow_limited(max_growth=1, energy_split=0.05)

    # decay
    core.decay_tick()
    res.decay_tick()

    # render
    img = combine_core_residual(core.values, res.field)
    # img shape: (512, 512, 3) = (height, width, 3) in numpy convention
    # img[row, col] = img[y, x] where row/y is vertical, col/x is horizontal
    #
    # pygame.surfarray.make_surface DOES NOT swap axes!
    # It simply interprets the array as (width, height, 3)
    # When we pass (512, 512, 3), pygame sees it as width=512, height=512
    # So the first dimension becomes X (width) and second becomes Y (height)
    # This is OPPOSITE to numpy's (height, width) convention!
    #
    # SOLUTION: Transpose to swap physical meaning of axes BEFORE rendering
    # We need (height, width, 3) -> (width, height, 3)
    # Using np.transpose(img, (1, 0, 2)) or np.swapaxes(img, 0, 1)
    #
    # BUT this swaps the data! So we get correct mapping:
    # Original img[y, x] with y=row, x=col
    # After swap: new_img[x, y] with x=col from first dim, y=row from second dim
    # pygame interprets new_img as [width, height] which is [x, y] - CORRECT!

    img_for_pygame = np.transpose(img, (1, 0, 2))  # (H,W,3) -> (W,H,3)
    surf = pygame.surfarray.make_surface(img_for_pygame)
    SCREEN.blit(surf, (0, 0))

    # Display coordinates on screen
    angle = angular_speed * t
    pos_text = FONT.render(
        f"T:{t:4d} | Pos:(x={entity.pos_ref[0]:6.1f}, y={entity.pos_ref[1]:6.1f}) | "
        f"Angle:{np.degrees(angle):6.1f}° | Scale:{s:.2f}",
        True, (255, 255, 255)
    )
    SCREEN.blit(pos_text, (5, 5))

    # Draw a crosshair at the actual entity position (for debugging)
    # entity.pos_ref = [x, y] where x is column, y is row
    # After swapaxes, pygame expects pygame_x = column, pygame_y = row
    # So screen position is (int(entity.pos_ref[0]), int(entity.pos_ref[1]))
    px = int(entity.pos_ref[0])  # x coordinate (column)
    py = int(entity.pos_ref[1])  # y coordinate (row)
    if 0 <= px < 512 and 0 <= py < 512:
        try:
            pygame.draw.circle(SCREEN, (0, 255, 0), (px, py), 3)
        except:
            pass

    pygame.display.flip()

    # sliding window snapshot (low-res)
    core_lr = core.snapshot()['values'][::8, ::8]
    res_lr = res.snapshot_lowres(factor=8)
    window.on_tick(s, [entity.copy()], core_lr, res_lr)

pygame.quit()
