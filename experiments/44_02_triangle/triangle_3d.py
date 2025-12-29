import sys

import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

# --- Trojúhelník ---
triangle_vertices = [
    [0, -1, 0],  # horní
    [-1, 1, 0],  # levý dolní
    [1, 1, 0]  # pravý dolní
]

# --- State ---
tick = 0
MAX_HISTORY = 24

triangle_state = {
    "position": [WIDTH // 2, HEIGHT // 2],
    "scale": 120,
    "operators": set(),
    "vertices": [v[:] for v in triangle_vertices]
}

history = []
render_mode = 0  # 0 = body, 1 = body+čáry, 2 = body+čáry+výplň


# --- Pomocné funkce ---
def centroid(vertices):
    cx = sum(v[0] for v in vertices) / len(vertices)
    cy = sum(v[1] for v in vertices) / len(vertices)
    return cx, cy


def rotate_around_centroid(vertices, transform, tick):
    cx, cy = centroid(vertices)
    shifted = [[x - cx, y - cy, t] for x, y, t in vertices]
    rotated = [transform(x, y) + [tick] for x, y, t in shifted]
    return [[x + cx, y + cy, t] for x, y, t in rotated]


# --- Transformace ---
def transform_cw(x, y): return [y, -x]


def transform_ccw(x, y): return [-y, x]


# --- Operátory ---
def operator_cw(state, tick):
    state["vertices"] = rotate_around_centroid(state["vertices"], transform_cw, tick)
    return state


def operator_ccw(state, tick):
    state["vertices"] = rotate_around_centroid(state["vertices"], transform_ccw, tick)
    return state


def operator_up(state, tick):
    verts = state["vertices"]
    verts[0][1] -= 1
    verts[0][2] = tick
    state["vertices"] = verts
    return state


def operator_down(state, tick):
    verts = state["vertices"]
    verts[0][1] += 1
    verts[0][2] = tick
    state["vertices"] = verts
    return state


operators = {
    "CW": operator_cw,
    "CCW": operator_ccw,
    "UP": operator_up,
    "DOWN": operator_down
}


# --- Projekce s perspektivou ---
def project(vertex, pos, scale, offset, zoom, depth, vanish_point):
    x, y, t = vertex
    x *= scale * zoom
    y *= scale * zoom
    px = int(pos[0] * zoom + x + offset[0])
    py = int(pos[1] * zoom + y + offset[1])

    # perspektivní sbíhání k vanishing pointu
    factor = depth / MAX_HISTORY
    px = int(px * (1 - factor) + vanish_point[0] * factor)
    py = int(py * (1 - factor) + vanish_point[1] * factor)

    return (px, py, t)


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
                triangle_state["operators"].symmetric_difference_update({"CW"})
            elif event.key == pygame.K_LEFT:
                triangle_state["operators"].symmetric_difference_update({"CCW"})
            elif event.key == pygame.K_UP:
                triangle_state["operators"].symmetric_difference_update({"UP"})
            elif event.key == pygame.K_DOWN:
                triangle_state["operators"].symmetric_difference_update({"DOWN"})
            elif event.key == pygame.K_SPACE:
                triangle_state["operators"].clear()
            elif event.key == pygame.K_TAB:
                render_mode = (render_mode + 1) % 3

    tick += 1

    # Apply operators
    for op in list(triangle_state["operators"]):
        triangle_state = operators[op](triangle_state, tick)

    # Save history
    history.append({
        "position": triangle_state["position"][:],
        "scale": triangle_state["scale"],
        "vertices": [v[:] for v in triangle_state["vertices"]]
    })
    if len(history) > MAX_HISTORY:
        history.pop(0)

    # Observer offset
    offset_x = WIDTH // 2 - triangle_state["position"][0]
    offset_y = HEIGHT // 2 - triangle_state["position"][1]
    offset = (offset_x, offset_y)

    vanish_point = (WIDTH // 2, HEIGHT // 2)
    zoom = 1.0

    # Render
    screen.fill((0, 0, 0))

    for i, past_state in enumerate(history):
        depth = len(history) - i
        scale = past_state["scale"] * (0.95 ** depth)
        pos_x = past_state["position"][0]
        pos_y = past_state["position"][1] + min(depth * 6, 120)

        projected = [project(v, [pos_x, pos_y], scale, offset, zoom, depth, vanish_point)
                     for v in past_state["vertices"]]

        radius = max(1, int(7 * (1.0 - depth / MAX_HISTORY)))

        # Barva podle stáří
        for px, py, t in projected:
            age_factor = max(0, min(1, (tick - t) / MAX_HISTORY))
            color = (int(200 * (1 - age_factor)), int(200 * (1 - age_factor)), 200)
            pygame.draw.circle(screen, color, (px, py), radius)

        # Postprocessing: čáry a výplň
        if render_mode >= 1:
            pygame.draw.polygon(screen, (150, 150, 150), [(px, py) for px, py, _ in projected], 1)
        if render_mode == 2:
            pygame.draw.polygon(screen, (50, 50, 200), [(px, py) for px, py, _ in projected], 0)

    # HUD
    draw_text(screen, f"Active operators: {', '.join(triangle_state['operators']) or 'None'}", 10, 10)
    draw_text(screen, "Left/Right: CW/CCW | Up/Down: Tilt | Space: Stop", 10, 30)
    draw_text(screen, f"Render mode: {render_mode} (TAB to cycle)", 10, 50)

    pygame.display.flip()
    clock.tick(10)
