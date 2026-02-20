"""V5 Experiment runner: Pygame visualization + headless mode.

Usage:
  python experiment.py --visual                          # Interactive visualization
  python experiment.py --headless --ticks 10000          # Headless with CSV output
  python experiment.py --headless --ticks 10000 --seeds 2 --distance 20
  python experiment.py --headless --ticks 10000 --output output/run1
"""

import argparse
import math
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from constants import WORLD_RADIUS, INITIAL_MEMORY_SIZE
from grid import HexGrid2D, hex_to_pixel, HEX_DIR_VECTORS
from world import World
from metrics import MetricsTracker


def build_seed_positions(seeds: int, distance: int) -> list[tuple[int, int]]:
    """Create seed positions: first at origin, rest spaced along q-axis."""
    positions = [(0, 0)]
    for i in range(1, seeds):
        positions.append((distance * i, 0))
    return positions


def run_headless(args):
    """Run simulation without visualization, CSV output only."""
    grid = HexGrid2D(WORLD_RADIUS)
    seed_positions = build_seed_positions(args.seeds, args.distance)
    world = World(grid, seed_positions, initial_memory_size=INITIAL_MEMORY_SIZE)

    output_dir = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output")
    tracker = MetricsTracker(output_dir)

    print(f"V5 Headless (photonic emission): radius={WORLD_RADIUS}, seeds={args.seeds}, "
          f"distance={args.distance}, ticks={args.ticks}, "
          f"initial_memory={INITIAL_MEMORY_SIZE}")
    print(f"Output: {output_dir}")

    t0 = time.time()
    for tick in range(1, args.ticks + 1):
        world.step()
        tracker.log(world)

        if tick % 100 == 0:
            elapsed = time.time() - t0
            e_count = world.entity_count()
            sys_energy = world.total_system_energy()
            field_max = world.field.max_value()
            photon_max = world.photon_field.max_value()
            gen_counts = world.population_by_generation()
            gen_str = " ".join(f"g{g}:{c}" for g, c in sorted(gen_counts.items())[:5])
            print(f"  tick={tick:>6d}  entities={e_count:>6d}  "
                  f"sys_energy={sys_energy:>12.1f}  field_max={field_max:>8.2f}  "
                  f"photon_max={photon_max:>8.2f}  "
                  f"max_gen={world.max_generation}  "
                  f"repl={world.replication_events}  "
                  f"blocked={world.blocked_moves}  "
                  f"trapped={world.trapped_entities}  "
                  f"fail_repl={world.failed_replications}  "
                  f"[{gen_str}]  "
                  f"elapsed={elapsed:.1f}s")

    elapsed = time.time() - t0
    print(f"\nDone: {args.ticks} ticks in {elapsed:.1f}s "
          f"({args.ticks / elapsed:.0f} ticks/s)")
    print(f"Final: {world.entity_count()} entities, "
          f"system energy={world.total_system_energy():.1f}, "
          f"max generation={world.max_generation}")

    tracker.close()


def run_visual(args):
    """Run simulation with Pygame visualization."""
    try:
        import pygame
        import numpy as np
    except ImportError:
        print("Pygame and numpy required for visual mode: pip install pygame numpy")
        sys.exit(1)

    pygame.init()

    R = WORLD_RADIUS
    screen_w = 900
    screen_h_map = 800
    screen_h_hud = 140
    screen_h = screen_h_map + screen_h_hud

    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("V5 Gamma Field (Photonic Emission)")
    clock = pygame.time.Clock()

    _SQRT3 = math.sqrt(3)
    hex_size = screen_w / (_SQRT3 * (2 * R + 1) + _SQRT3)
    center_x = screen_w / 2
    center_y = screen_h_map / 2

    grid = HexGrid2D(R)
    seed_positions = build_seed_positions(args.seeds, args.distance)
    world = World(grid, seed_positions, initial_memory_size=INITIAL_MEMORY_SIZE)

    output_dir = args.output or os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "output")
    tracker = MetricsTracker(output_dir)

    def hex_to_screen(q, r):
        px, py = hex_to_pixel(q, r, hex_size)
        return center_x + px, center_y + py

    def hexagon_vertices(cx, cy, size):
        verts = []
        for i in range(6):
            angle = math.radians(60 * i - 30)
            verts.append((cx + size * math.cos(angle), cy + size * math.sin(angle)))
        return verts

    use_polygons = R <= 50

    if use_polygons:
        hex_polys = {}
        for pos in grid.all_cells():
            q, r = pos
            sx, sy = hex_to_screen(q, r)
            hex_polys[pos] = hexagon_vertices(sx, sy, hex_size)

    # Precompute sampled positions for gradient arrows (every SAMPLE_STEP cells)
    SAMPLE_STEP = 5
    sampled_positions = []
    for pos in grid.all_cells():
        q, r = pos
        if q % SAMPLE_STEP == 0 and r % SAMPLE_STEP == 0:
            sampled_positions.append(pos)

    def draw_gradient_arrows(field_obj, color, negate=False):
        """Draw gradient arrows at sampled positions.

        Args:
            field_obj: GammaField to compute gradients from
            color: RGB tuple for arrow color
            negate: if True, draw anti-gradient (arrows point downhill)
        """
        # Find max magnitude for scaling
        max_mag = 0.0
        grads = []
        for pos in sampled_positions:
            gx, gy, mag = field_obj.gradient_at(pos)
            grads.append((pos, gx, gy, mag))
            if mag > max_mag:
                max_mag = mag

        if max_mag < 1e-12:
            return

        arrow_max_len = hex_size * SAMPLE_STEP * 0.8
        for pos, gx, gy, mag in grads:
            if mag < 1e-12:
                continue
            q, r = pos
            sx, sy = hex_to_screen(q, r)
            isx, isy = int(sx), int(sy)

            # Normalize and scale by relative magnitude
            scale = (mag / max_mag) * arrow_max_len
            nx, ny = gx / mag, gy / mag
            if negate:
                nx, ny = -nx, -ny

            ex = isx + int(nx * scale)
            ey = isy + int(ny * scale)

            pygame.draw.line(screen, color, (isx, isy), (ex, ey), 2)
            # Arrowhead
            if scale > 4:
                perp_x, perp_y = -ny, nx
                head_len = min(scale * 0.3, 6)
                back_x = ex - int(nx * head_len)
                back_y = ey - int(ny * head_len)
                h1 = (back_x + int(perp_x * head_len * 0.5),
                       back_y + int(perp_y * head_len * 0.5))
                h2 = (back_x - int(perp_x * head_len * 0.5),
                       back_y - int(perp_y * head_len * 0.5))
                pygame.draw.polygon(screen, color, [(ex, ey), h1, h2])

    running = True
    paused = False
    show_gamma_grad = False
    show_photon_grad = False

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_g:
                    show_gamma_grad = not show_gamma_grad
                elif event.key == pygame.K_p:
                    show_photon_grad = not show_photon_grad

        if not paused:
            world.step()
            tracker.log(world)

        screen.fill((0, 0, 0))

        # --- Draw gamma field heatmap ---
        max_g = max(world.field.max_value(), 0.01)

        if use_polygons:
            for pos, verts in hex_polys.items():
                g = grid.get(world.field.gamma, pos)
                intensity = min(255, int(255 * g / max_g))
                pygame.draw.polygon(screen, (0, intensity, 0), verts)
        else:
            for pos in grid.all_cells():
                q, r = pos
                g = grid.get(world.field.gamma, pos)
                intensity = min(255, int(255 * g / max_g))
                sx, sy = hex_to_screen(q, r)
                screen.set_at((int(sx), int(sy)), (0, intensity, 0))

        # --- Draw entities ---
        for e in world.entities:
            q, r = e.pos
            sx, sy = hex_to_screen(q, r)
            isx, isy = int(sx), int(sy)

            # Color intensity = memory fill % (dark=empty, bright=full)
            fill = e.memory_fill_pct
            brightness = int(80 + 175 * fill)  # range 80-255
            # Hue by generation (cycle through colors)
            gen_hue = e.generation % 6
            if gen_hue == 0:
                color = (0, brightness, 0)           # green
            elif gen_hue == 1:
                color = (brightness, brightness, 0)  # yellow
            elif gen_hue == 2:
                color = (0, brightness, brightness)  # cyan
            elif gen_hue == 3:
                color = (brightness, int(brightness * 0.5), 0)  # orange
            elif gen_hue == 4:
                color = (int(brightness * 0.5), brightness, 0)  # lime
            else:
                color = (0, int(brightness * 0.5), brightness)  # teal

            pygame.draw.circle(screen, color, (isx, isy), 4)
            pygame.draw.circle(screen, (255, 255, 255), (isx, isy), 4, 1)

            # Draw heading arrow
            hx, hy = e.heading()
            h_mag = math.sqrt(hx * hx + hy * hy)
            if h_mag > 0.1:
                arrow_len = hex_size * 2.5
                ax = isx + int(hx / h_mag * arrow_len)
                ay = isy + int(hy / h_mag * arrow_len)
                pygame.draw.line(screen, (255, 255, 255), (isx, isy), (ax, ay), 1)

        # --- Draw gradient overlays ---
        if show_gamma_grad:
            draw_gradient_arrows(world.field, (255, 200, 0))       # yellow: gamma uphill
        if show_photon_grad:
            draw_gradient_arrows(world.photon_field, (255, 80, 80), negate=True)  # red: anti-photon

        # --- HUD ---
        font = pygame.font.SysFont("consolas", 14)
        hud_y = screen_h_map + 5

        sys_energy = world.total_system_energy()
        photon_max = world.photon_field.max_value()
        grad_str = ""
        if show_gamma_grad:
            grad_str += " [G:ON]"
        if show_photon_grad:
            grad_str += " [P:ON]"
        txt = font.render(
            f"tick={world.tick}  entities={world.entity_count()}  "
            f"sys_energy={sys_energy:.0f}  field_max={max_g:.2f}  "
            f"photon_max={photon_max:.2f}  "
            f"repl={world.replication_events}  "
            f"max_gen={world.max_generation}  "
            f"{'PAUSED' if paused else ''}{grad_str}",
            True, (200, 200, 200)
        )
        screen.blit(txt, (10, hud_y))
        hud_y += 18

        # Generation population
        gen_counts = world.population_by_generation()
        gen_str = "  ".join(f"g{g}:{c}" for g, c in sorted(gen_counts.items())[:8])
        txt = font.render(f"Generations: {gen_str}", True, (180, 180, 180))
        screen.blit(txt, (10, hud_y))
        hud_y += 18

        # Key hints
        txt = font.render(
            "Keys: SPACE=pause  G=gamma gradient  P=photon anti-gradient  ESC=quit",
            True, (120, 120, 120))
        screen.blit(txt, (10, hud_y))
        hud_y += 18

        # Top entities
        for i, e in enumerate(world.entities[:5]):
            q, r = e.pos
            hx, hy = e.heading()
            txt = font.render(
                f"#{e.id} ({q},{r}) mem={e.memory_cursor}/{e.memory_size} "
                f"gen={e.generation} h=({hx:.1f},{hy:.1f})",
                True, (160, 160, 160)
            )
            screen.blit(txt, (10, hud_y))
            hud_y += 16

        if world.entity_count() > 5:
            txt = font.render(
                f"... +{world.entity_count() - 5} more", True, (120, 120, 120))
            screen.blit(txt, (10, hud_y))

        pygame.display.flip()
        clock.tick(60)

    tracker.close()
    pygame.quit()


def main():
    parser = argparse.ArgumentParser(description="V5 Gamma Field Experiment (Photonic Emission)")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--visual", action="store_true", help="Run with Pygame visualization")
    mode.add_argument("--headless", action="store_true", help="Run headless (CSV only)")

    parser.add_argument("--ticks", type=int, default=5000, help="Number of ticks (headless)")
    parser.add_argument("--seeds", type=int, default=1, help="Number of seed entities")
    parser.add_argument("--distance", type=int, default=20, help="Distance between seeds")
    parser.add_argument("--output", type=str, default=None, help="Output directory for CSV")

    args = parser.parse_args()

    if not args.visual and not args.headless:
        args.visual = True

    if args.visual:
        run_visual(args)
    else:
        run_headless(args)


if __name__ == "__main__":
    main()
