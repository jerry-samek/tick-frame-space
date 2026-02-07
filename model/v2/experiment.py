import os
import sys

import numpy as np
import pygame

# Allow imports from this directory when run as a script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from constants import WORLD_SIZE, ENTITY_COLORS
from entity import Entity, next_entity_id
from hill import Hill
from world import World
from csv_logger import CSVLogger


# ==========================
# Pygame visualization (2D top-down heatmap)
# ==========================

def run():
    pygame.init()
    n = WORLD_SIZE
    screen_w = 600
    screen_h_map = 600
    screen_h_hud = 120
    screen_h = screen_h_map + screen_h_hud

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("2D Hill + Entities (V2)")

    clock = pygame.time.Clock()

    # Initial 2D hill — Gaussian peak at center
    Y, X = np.mgrid[0:n, 0:n]
    cx, cy = n // 2, n // 2
    h0 = 5.0 * np.exp(-0.5 * ((X - cx)**2 + (Y - cy)**2) / 20.0**2)

    hill = Hill(height=h0)

    # Initial entities — three around the peak
    entity0 = Entity(
        id=next_entity_id(),
        x=cx + 5, y=cy,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[cy, cx + 5],
        energy=1.0,
    )
    entity1 = Entity(
        id=next_entity_id(),
        x=cx - 5, y=cy,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[cy, cx - 5],
        energy=1.0,
    )
    entity2 = Entity(
        id=next_entity_id(),
        x=cx, y=cy + 5,
        memory=np.array([1, 0, -1, 1], dtype=int),
        baseline_h=h0[cy + 5, cx],
        energy=1.0,
    )

    imprint = np.zeros((n, n), dtype=float)
    leak = np.zeros((n, n), dtype=float)

    world = World(hill=hill, entities=[entity0, entity1, entity2],
                  imprint_field=imprint, leak_field=leak)

    # CSV logger
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "output")
    logger = CSVLogger(output_dir)

    running = True
    tick = 0

    # Scale factor from world coords to screen coords
    scale = screen_w / n  # 600 / 200 = 3.0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        tick += 1
        world.commit_step(tick)

        logger.log_tick(tick, world)

        screen.fill((0, 0, 0))

        # --- Draw 2D heatmap ---
        max_h = max(np.max(world.hill.height), 1.0)
        normalized = world.hill.height / max_h

        # Green channel intensity = height (dark to bright green)
        surface_array = np.zeros((n, n, 3), dtype=np.uint8)
        surface_array[:, :, 1] = (normalized * 255).astype(np.uint8)

        # pygame.surfarray expects (width, height, 3) — transpose from (rows, cols) to (x, y)
        surf = pygame.surfarray.make_surface(surface_array.transpose(1, 0, 2))
        surf = pygame.transform.scale(surf, (screen_w, screen_h_map))
        screen.blit(surf, (0, 0))

        # --- Draw imprint overlay (blue dots) ---
        imp_threshold = 0.01
        imp_coords = np.argwhere(world.imprint_field > imp_threshold)
        for (iy, ix) in imp_coords:
            sx = int(ix * scale + scale / 2)
            sy = int(iy * scale + scale / 2)
            pygame.draw.circle(screen, (80, 80, 255), (sx, sy), 1)

        # --- Draw leak overlay (red dots) ---
        leak_threshold = 0.01
        leak_coords = np.argwhere(world.leak_field > leak_threshold)
        for (iy, ix) in leak_coords:
            sx = int(ix * scale + scale / 2)
            sy = int(iy * scale + scale / 2)
            pygame.draw.circle(screen, (255, 80, 80), (sx, sy), 1)

        # --- Draw entity trails with fade (3B) ---
        for i, e in enumerate(world.entities):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            trail_len = len(e.trail)
            for j, (tx, ty) in enumerate(e.trail):
                # Older positions fade more (linear fade from 0.15 to 0.6)
                alpha = 0.15 + 0.45 * (j / max(trail_len - 1, 1))
                faded = (int(color[0] * alpha), int(color[1] * alpha), int(color[2] * alpha))
                sx = int(tx * scale + scale / 2)
                sy = int(ty * scale + scale / 2)
                pygame.draw.circle(screen, faded, (sx, sy), 1)

        # --- Draw entities as colored circles + direction arrows ---
        for i, e in enumerate(world.entities):
            color = ENTITY_COLORS[i % len(ENTITY_COLORS)]
            sx = int(e.x * scale + scale / 2)
            sy = int(e.y * scale + scale / 2)
            pygame.draw.circle(screen, color, (sx, sy), 5)
            # White outline for visibility
            pygame.draw.circle(screen, (255, 255, 255), (sx, sy), 5, 1)

            # Direction arrow from heading vector (3A — shows smooth intent)
            arrow_len = 12
            hx = e.heading[0]
            hy = e.heading[1]
            hmag = np.sqrt(hx * hx + hy * hy)
            if hmag > 1e-6:
                ex = int(sx + arrow_len * hx / hmag)
                ey = int(sy + arrow_len * hy / hmag)
                pygame.draw.line(screen, (255, 255, 255), (sx, sy), (ex, ey), 1)

            # Perpendicular component arrow (cyan)
            px = e.last_perp[0]
            py = e.last_perp[1]
            pmag = np.sqrt(px * px + py * py)
            if pmag > 1e-6 and abs(e.last_mem_bias) > 0.01:
                perp_len = 8
                epx = int(sx + perp_len * e.last_mem_bias * px / pmag)
                epy = int(sy + perp_len * e.last_mem_bias * py / pmag)
                pygame.draw.line(screen, (0, 255, 255), (sx, sy), (epx, epy), 1)

        # --- Console dump (first 20 ticks) ---
        if tick <= 20:
            for e in world.entities:
                mem_str = ",".join(str(int(m)) for m in e.memory)
                print(f"tick={tick} #{e.id} pos=({e.x},{e.y}) "
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
                f"#{e.id} ({e.x},{e.y}) E={e.energy:.2f} {e.last_outcome:<8s} "
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
