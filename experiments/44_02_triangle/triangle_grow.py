import sys

import pygame

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, 20)

# --- Initial target triangle ---
target_vertices = [[0, 300], [300, 150], [0, 150]]

cx = sum(x for x, y in target_vertices) / 3
cy = sum(y for x, y in target_vertices) / 3

offset_x = WIDTH // 2 - cx
offset_y = HEIGHT // 2 - cy

target_vertices = [[x + offset_x, y + offset_y] for x, y in target_vertices]

centroid = [WIDTH // 2, HEIGHT // 2]

tick = 0
MAX_HISTORY = 24

triangle_state = {
    "position": [WIDTH // 2, HEIGHT // 2],
    "operators": set(),
    "vertices": [
        [centroid[0], centroid[1], 0, (255, 0, 0)],
        [centroid[0], centroid[1], 0, (0, 255, 0)],
        [centroid[0], centroid[1], 0, (0, 0, 255)]
    ]
}

history = []


# --- Helpers ---
def centroid_calc(vertices):
    cx = sum(v[0] for v in vertices[:3]) / 3
    cy = sum(v[1] for v in vertices[:3]) / 3
    return cx, cy


def normalize(v):
    return 1 if v > 0 else -1 if v < 0 else 0


def transform_cw(x, y):
    return [x + normalize(y), y + normalize(-x)]


def transform_ccw(x, y):
    return [x + normalize(-y), y + normalize(x)]


def rotate_around_centroid(vertices, transform, tick):
    cx, cy = centroid_calc(vertices)
    shifted = [[x - cx, y - cy, t, c] for x, y, t, c in vertices[:3]]
    rotated = [transform(x, y) + [tick, c] for x, y, t, c in shifted]
    return [[x + cx, y + cy, t, c] for x, y, t, c in rotated]


# --- Operators ---
def operator_cw(state, tick):
    state["vertices"][:3] = rotate_around_centroid(state["vertices"], transform_cw, tick)
    return state


def operator_ccw(state, tick):
    state["vertices"][:3] = rotate_around_centroid(state["vertices"], transform_ccw, tick)
    return state


def operator_up(state, tick):
    state["vertices"][0][1] -= 1
    state["vertices"][0][2] = tick
    return state


def operator_down(state, tick):
    state["vertices"][0][1] += 1
    state["vertices"][0][2] = tick
    return state


operators = {
    "CW": operator_cw,
    "CCW": operator_ccw,
    "UP": operator_up,
    "DOWN": operator_down
}


# --- NAND/XOR growth ---
def grow_vertices(state, tick):
    new = []
    for (x, y, t, c), (tx, ty) in zip(state["vertices"][:3], target_vertices):
        dx, dy = tx - x, ty - y
        mx = 1 if dx != 0 else 0
        my = 1 if dy != 0 else 0
        if dx == 0 and dy == 0:
            new.append([x, y, t, c])
        else:
            sx = (1 if dx > 0 else -1) * mx
            sy = (1 if dy > 0 else -1) * my
            new.append([x + sx, y + sy, tick, c])
    state["vertices"][:3] = new
    return state


# --- Deterministic interior point ---
def add_fill_point(state, tick):
    v1, v2, v3 = state["vertices"][:3]

    a = ((tick % 3) - 1 + 1) / 2
    b = (((tick // 3) % 3) - 1 + 1) / 2
    if a + b > 1:
        a, b = 1 - a, 1 - b

    x = v1[0] + a * (v2[0] - v1[0]) + b * (v3[0] - v1[0])
    y = v1[1] + a * (v2[1] - v1[1]) + b * (v3[1] - v1[1])

    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    r = int(colors[0][0] * (1 - a - b) + colors[1][0] * a + colors[2][0] * b)
    g = int(colors[0][1] * (1 - a - b) + colors[1][1] * a + colors[2][1] * b)
    bcol = int(colors[0][2] * (1 - a - b) + colors[1][2] * a + colors[2][2] * b)

    state["vertices"].append([x, y, tick, (r, g, bcol)])
    return state


# --- Update target after manual change ---
def update_target(state):
    global target_vertices
    target_vertices = [[x, y] for x, y, t, c in state["vertices"][:3]]


# --- Projection ---
def project(v, offset, zoom, depth, vanish):
    x, y, t, c = v
    px = int(x * zoom + offset[0])
    py = int(y * zoom + offset[1])
    f = depth / MAX_HISTORY
    px = int(px * (1 - f) + vanish[0] * f)
    py = int(py * (1 - f) + vanish[1] * f)
    return px, py, t, c


# --- Main loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RIGHT: triangle_state["operators"].symmetric_difference_update({"CW"})
            if event.key == pygame.K_LEFT:  triangle_state["operators"].symmetric_difference_update({"CCW"})
            if event.key == pygame.K_UP:    triangle_state["operators"].symmetric_difference_update({"UP"})
            if event.key == pygame.K_DOWN:  triangle_state["operators"].symmetric_difference_update({"DOWN"})
            if event.key == pygame.K_SPACE: triangle_state["operators"].clear()

    tick += 1

    triangle_state = grow_vertices(triangle_state, tick)
    triangle_state = add_fill_point(triangle_state, tick)

    for op in list(triangle_state["operators"]):
        triangle_state = operators[op](triangle_state, tick)
        update_target(triangle_state)

    history.append([v[:] for v in triangle_state["vertices"]])
    if len(history) > MAX_HISTORY:
        history.pop(0)

    offset = (WIDTH // 2 - triangle_state["position"][0],
              HEIGHT // 2 - triangle_state["position"][1])
    vanish = (WIDTH // 2, HEIGHT // 2)

    screen.fill((0, 0, 0))

    for i, frame in enumerate(history):
        depth = len(history) - i
        projected = [project(v, offset, 1.0, depth, vanish) for v in frame]

        for px, py, t, c in projected:
            pygame.draw.circle(screen, c, (px, py), 2)

        tri = [(px, py) for px, py, t, c in projected[:3]]
        pygame.draw.polygon(screen, (200, 200, 200), tri, 1)

    pygame.display.flip()
    clock.tick(30)
