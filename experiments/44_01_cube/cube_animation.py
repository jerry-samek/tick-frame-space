import sys

import pygame

# --- Initialization ---
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Cube definition (2D square projected as cube vertices) ---
cube_vertices = [
    [-1, -1],
    [-1, 1],
    [1, -1],
    [1, 1]
]

# --- State ---
tick = 0
WINDOW = 50
EPSILON = 10
MAX_HISTORY = 20

cube_state = {
    "position": [WIDTH // 2, HEIGHT // 2, 0],  # X, Y, emergent Z
    "scale": 60,
    "operator": "A"
}

buffer = []
history = []


# --- NAND operator ---
def nand(a, b):
    return -1 if (a == 1 and b == 1) else 1


# --- Tickstream: substrate-driven
def tickstream(tick, buffer):
    x = (tick % 3) - 1
    if buffer:
        last_x, last_y = buffer[-1]
        y = nand(last_x, last_y)
    else:
        y = 0
    return x, y


# --- Operators ---
def operator_A(state, sx, sy):
    state["position"][0] += sx * 5
    state["position"][1] += sy * 5
    return state


def operator_B(state, sx, sy):
    state["position"][0] += nand(sx, sy) * 5
    state["position"][1] += sy * 5
    return state


def operator_C(state, sx, sy):
    state["scale"] += nand(sx, sy) * 2
    return state


operators = {
    "A": operator_A,
    "B": operator_B,
    "C": operator_C
}


# --- Helper functions ---
def project(point, pos, scale, offset, zoom):
    x, y = point
    x *= scale * zoom
    y *= scale * zoom
    px = int(pos[0] * zoom + x + offset[0])
    py = int(pos[1] * zoom + y + offset[1])
    return (px, py)


def measure_imbalance(buffer):
    return sum(abs(x) + abs(y) for x, y in buffer)


def choose_new_operator():
    return ["A", "B", "C"][(tick // WINDOW) % 3]


def log_commit(tick, operator, imbalance):
    print(f"Commit at tick {tick}: switched to {operator} (imbalance={imbalance})")


def apply_soft_bounds(state, center, radius=300, strength=0.01):
    dx = center[0] - state["position"][0]
    dy = center[1] - state["position"][1]
    dist = abs(dx) + abs(dy)
    if dist > radius:
        state["position"][0] += dx * strength
        state["position"][1] += dy * strength
    return state


# --- Main loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    tick += 1

    # Tickstream-driven motion
    state_x, state_y = tickstream(tick, buffer)

    # Apply operator
    cube_state = operators[cube_state["operator"]](cube_state, state_x, state_y)

    # Soft bounds to keep cube in view
    cube_state = apply_soft_bounds(cube_state, (WIDTH // 2, HEIGHT // 2))

    # Update buffer
    buffer.append((state_x, state_y))
    if len(buffer) > WINDOW:
        buffer.pop(0)

    # Emergent Z
    cube_state["position"][2] = sum(nand(x, y) for x, y in buffer)

    # Commit check
    imbalance = measure_imbalance(buffer)
    if imbalance > EPSILON and tick % WINDOW == 0:
        cube_state["operator"] = choose_new_operator()
        log_commit(tick, cube_state["operator"], imbalance)

    # Save history
    history.append(cube_state.copy())
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
        zoom = max(0.5, 1.0 / (1.0 + max_dist / 300.0))
    else:
        zoom = 1.0

    # Render
    screen.fill((0, 0, 0))

    for i, past_state in enumerate(history):
        depth = len(history) - i
        scale = past_state["scale"] * (0.95 ** depth)
        pos_x = past_state["position"][0]
        pos_y = past_state["position"][1] + min(depth * 5, 100)

        projected = [project(v, [pos_x, pos_y], scale, offset, zoom) for v in cube_vertices]

        # Point size modulation based on depth
        radius = max(1, int(6 * (1.0 - depth / MAX_HISTORY)))
        for p in projected:
            pygame.draw.circle(screen, (200, 200, 200), p, radius)

    pygame.display.flip()
    clock.tick(30)
