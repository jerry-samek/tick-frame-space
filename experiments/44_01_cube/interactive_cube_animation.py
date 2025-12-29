import sys

import pygame

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

# --- Cube definition (square vertices) ---
cube_vertices = [
    [-1, -1],
    [-1, 1],
    [1, -1],
    [1, 1]
]

# --- State ---
tick = 0
MAX_HISTORY = 24

cube_state = {
    "position": [WIDTH // 2, HEIGHT // 2],
    "scale": 110,
    "operators": set(),  # multiple active operators
    "vertices": cube_vertices[:]  # current transformed vertices
}

history = []


# --- Discrete rotation operators ---
def operator_cw(state):
    # 90° clockwise: (x,y) -> (y,-x)
    state["vertices"] = [[y, -x] for x, y in state["vertices"]]
    return state


def operator_ccw(state):
    # 90° counterclockwise: (x,y) -> (-y,x)
    state["vertices"] = [[-y, x] for x, y in state["vertices"]]
    return state


def operator_up(state):
    # tilt up: increment y
    state["vertices"] = [[x, y + 1] for x, y in state["vertices"]]
    return state


def operator_down(state):
    # tilt down: decrement y
    state["vertices"] = [[x, y - 1] for x, y in state["vertices"]]
    return state


operators = {
    "CW": operator_cw,
    "CCW": operator_ccw,
    "UP": operator_up,
    "DOWN": operator_down
}


# --- Helper functions ---
def project(point, pos, scale, offset, zoom):
    x, y = point
    x *= scale * zoom
    y *= scale * zoom
    return (int(pos[0] * zoom + x + offset[0]),
            int(pos[1] * zoom + y + offset[1]))


def draw_text(surf, txt, x, y, color=(200, 200, 200)):
    img = font.render(txt, True, color)
    surf.blit(img, (x, y))


# --- Main loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT:
                cube_state["operators"].symmetric_difference_update({"CW"})
            elif event.key == pygame.K_LEFT:
                cube_state["operators"].symmetric_difference_update({"CCW"})
            elif event.key == pygame.K_UP:
                cube_state["operators"].symmetric_difference_update({"UP"})
            elif event.key == pygame.K_DOWN:
                cube_state["operators"].symmetric_difference_update({"DOWN"})
            elif event.key == pygame.K_SPACE:
                cube_state["operators"].clear()
            elif event.key == pygame.K_r:
                # Reset cube state when R is pressed
                cube_state["operators"].clear()
                cube_state["vertices"] = cube_vertices[:]
                # Reset position closer to center but less drastic
                cube_state["position"] = [WIDTH // 2, HEIGHT // 2 - 50]
                tick = 0
                history.clear()

    tick += 1

    # Apply all active operators (discrete transformations)
    for op in list(cube_state["operators"]):
        cube_state = operators[op](cube_state)

    # Save history snapshot
    history.append({
        "position": cube_state["position"][:],
        "scale": cube_state["scale"],
        "vertices": [v[:] for v in cube_state["vertices"]]
    })
    if len(history) > MAX_HISTORY:
        history.pop(0)

    # Observer offset
    offset_x = WIDTH // 2 - cube_state["position"][0]
    offset_y = HEIGHT // 2 - cube_state["position"][1]
    offset = (offset_x, offset_y)

    # Dynamic zoom
    if history:
        max_dist = max(abs(p["position"][0] - cube_state["position"][0]) +
                       abs(p["position"][1] - cube_state["position"][1])
                       for p in history)
        zoom = max(0.7, 1.0 / (1.0 + max_dist / 300.0))
    else:
        zoom = 1.0

    # Render
    screen.fill((0, 0, 0))

    for i, past_state in enumerate(history):
        depth = len(history) - i
        scale = past_state["scale"] * (0.95 ** depth)
        pos_x = past_state["position"][0]
        pos_y = past_state["position"][1] + min(depth * 6, 120)

        projected = [project(v, [pos_x, pos_y], scale, offset, zoom)
                     for v in past_state["vertices"]]

        radius = max(1, int(7 * (1.0 - depth / MAX_HISTORY)))
        for p in projected:
            pygame.draw.circle(screen, (200, 200, 200), p, radius)

    # HUD
    draw_text(screen, f"Active operators: {', '.join(cube_state['operators']) or 'None'}", 10, 10)
    draw_text(screen, "Left/Right: CW/CCW | Up/Down: Tilt | Space: Stop", 10, 30)

    pygame.display.flip()
    clock.tick(10)  # slower tick so discrete jumps are visible
