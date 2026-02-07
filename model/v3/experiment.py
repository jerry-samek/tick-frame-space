import os
import sys
import math

import numpy as np
import pygame

# Allow imports from this directory when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from constants import WORLD_RADIUS, ENTITY_COLORS
from entity import Entity, next_entity_id
from hill import Hill
from world import World
from csv_logger import CSVLogger
from hex_grid import hex_to_pixel, is_valid_hex, make_valid_mask


# ==========================
# Pygame visualization (2D hex heatmap)
# ==========================

def hexagon_vertices(cx: float, cy: float, size: float) -> list[tuple[float, float]]:
    """Compute 6 vertices for a pointy-top hexagon centered at (cx, cy)."""
    verts = []
    for i in range(6):
        angle = math.radians(60 * i - 30)  # pointy-top: start at -30 deg
        verts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
    return verts


def run():
    pygame.init()
    R = WORLD_RADIUS
    side = 2 * R + 1

    screen_w = 800
    screen_h_map = 800
    screen_h_hud = 120
    screen_h = screen_h_map + screen_h_hud

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("2D Hex Hill + Entities (V3)")

    clock = pygame.time.Clock()

    # Compute hex size to fit the hex grid in the screen
    # The hex grid spans sqrt(3) * (2R+1) * size in x-direction
    _SQRT3 = math.sqrt(3)
    hex_size = screen_w / (_SQRT3 * (2 * R + 1) + _SQRT3)
    # Center offset: pixel coords of hex (0,0) on screen
    center_x = screen_w / 2
    center_y = screen_h_map / 2

    # Pre-compute valid mask
    valid_mask = make_valid_mask(R)

    # Initial hex hill — flat (entities build their own hills)
    h0 = np.zeros((side, side), dtype=float)

    hill = Hill(height=h0, radius=R)

    # Single entity at origin with bootstrap energy
    entity0 = Entity(
        id=next_entity_id(),
        q=0, r=0,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=0.0,
        energy=0.15,
    )

    imprint = np.zeros((side, side), dtype=float)
    leak = np.zeros((side, side), dtype=float)

    world = World(hill=hill, entities=[entity0],
                  imprint_field=imprint, leak_field=leak)

    # CSV logger
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    logger = CSVLogger(output_dir)

    running = True
    tick = 0

    # Pre-compute hex polygon vertices for all valid cells (for rendering)
    # For large R, this is heavy — use dot rendering instead
    use_polygons = R <= 50

    if use_polygons:
        hex_polys = {}  # (q, r) -> list of vertex tuples
        for r in range(-R, R + 1):
            for q in range(-R, R + 1):
                if is_valid_hex(q, r, R):
                    px, py = hex_to_pixel(q, r, hex_size)
                    sx = center_x + px
                    sy = center_y + py
                    hex_polys[(q, r)] = hexagon_vertices(sx, sy, hex_size)

    def hex_to_screen(q, r):
        px, py = hex_to_pixel(q, r, hex_size)
        return center_x + px, center_y + py

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        tick += 1
        world.commit_step(tick)

        logger.log_tick(tick, world)

        screen.fill((0, 0, 0))

        # --- Draw hex heatmap ---
        max_h = max(np.max(world.hill.height), 0.01)

        if use_polygons:
            for (q, r), verts in hex_polys.items():
                h = world.hill.height[r + R, q + R]
                intensity = min(255, int(255 * h / max_h))
                color = (0, intensity, 0)
                pygame.draw.polygon(screen, color, verts)
        else:
            # Dot rendering for large grids
            for r_i in range(-R, R + 1):
                for q_i in range(-R, R + 1):
                    if not is_valid_hex(q_i, r_i, R):
                        continue
                    h = world.hill.height[r_i + R, q_i + R]
                    intensity = min(255, int(255 * h / max_h))
                    sx, sy = hex_to_screen(q_i, r_i)
                    screen.set_at((int(sx), int(sy)), (0, intensity, 0))

        # --- Draw imprint overlay (blue) ---
        imp_threshold = 0.01
        for r_i in range(-R, R + 1):
            for q_i in range(-R, R + 1):
                if not is_valid_hex(q_i, r_i, R):
                    continue
                if world.imprint_field[r_i + R, q_i + R] > imp_threshold:
                    sx, sy = hex_to_screen(q_i, r_i)
                    pygame.draw.circle(screen, (80, 80, 255), (int(sx), int(sy)), 1)

        # --- Draw leak overlay (red) ---
        leak_threshold = 0.01
        for r_i in range(-R, R + 1):
            for q_i in range(-R, R + 1):
                if not is_valid_hex(q_i, r_i, R):
                    continue
                if world.leak_field[r_i + R, q_i + R] > leak_threshold:
                    sx, sy = hex_to_screen(q_i, r_i)
                    pygame.draw.circle(screen, (255, 80, 80), (int(sx), int(sy)), 1)

        # --- Draw entity trails with fade ---
        for i, e in enumerate(world.entities):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            trail_len = len(e.trail)
            for j, (tq, tr) in enumerate(e.trail):
                alpha = 0.15 + 0.45 * (j / max(trail_len - 1, 1))
                faded = (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha))
                sx, sy = hex_to_screen(tq, tr)
                pygame.draw.circle(screen, faded, (int(sx), int(sy)), 1)

        # --- Draw entities as colored circles + direction arrows ---
        for i, e in enumerate(world.entities):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            sx, sy = hex_to_screen(e.q, e.r)
            isx, isy = int(sx), int(sy)
            pygame.draw.circle(screen, color, (isx, isy), 5)
            pygame.draw.circle(screen, (255, 255, 255), (isx, isy), 5, 1)

            # Direction arrow from heading vector
            arrow_len = 12
            hx = e.heading[0]
            hy = e.heading[1]
            hmag = math.sqrt(hx * hx + hy * hy)
            if hmag > 1e-6:
                ex = int(sx + arrow_len * hx / hmag)
                ey = int(sy + arrow_len * hy / hmag)
                pygame.draw.line(screen, (255, 255, 255), (isx, isy), (ex, ey), 1)

            # Perpendicular component arrow (cyan)
            px = e.last_perp[0]
            py = e.last_perp[1]
            pmag = math.sqrt(px * px + py * py)
            if pmag > 1e-6 and abs(e.last_mem_bias) > 0.01:
                perp_len = 8
                epx = int(sx + perp_len * e.last_mem_bias * px / pmag)
                epy = int(sy + perp_len * e.last_mem_bias * py / pmag)
                pygame.draw.line(screen, (0, 255, 255), (isx, isy), (epx, epy), 1)

        # --- Console dump (first 20 ticks) ---
        if tick <= 20:
            for e in world.entities:
                mem_str = ",".join(str(int(m)) for m in e.memory)
                print(f"tick={tick} #{e.id} pos=({e.q},{e.r}) "
                      f"{e.last_outcome:<8s} hdiff={e.last_move_height_diff:+.4f} "
                      f"mem=[{mem_str}] chiral={e.last_mem_bias:+.2f} "
                      f"step={e.last_step}")

        # --- HUD ---
        font = pygame.font.SysFont("consolas", 14)
        hud_y = screen_h_map + 5

        txt = font.render(
            f"tick={tick}  entities={len(world.entities)}  "
            f"max_h={max_h:.2f}  repl={world.replication_events}  merge={world.merge_events}",
            True, (200, 200, 200)
        )
        screen.blit(txt, (10, hud_y))
        hud_y += 18

        for i, e in enumerate(world.entities[:5]):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            txt = font.render(
                f"#{e.id} ({e.q},{e.r}) E={e.energy:.2f} {e.last_outcome:<8s} "
                f"chiral={e.last_mem_bias:+.2f} step={e.last_step} "
                f"hdiff={e.last_move_height_diff:+.3f}",
                True, color
            )
            screen.blit(txt, (10, hud_y))
            hud_y += 16

        if len(world.entities) > 5:
            txt = font.render(f"... +{len(world.entities) - 5} more", True, (150, 150, 150))
            screen.blit(txt, (10, hud_y))

        pygame.display.flip()
        clock.tick(60)

    logger.close()
    pygame.quit()

if __name__ == "__main__":
    run()
