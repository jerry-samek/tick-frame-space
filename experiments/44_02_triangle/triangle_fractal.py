import sys

import pygame

pygame.init()
WIDTH, HEIGHT = 900, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

# --- Signál vzniká zde ---
origin = [WIDTH // 2, HEIGHT // 2]

# --- Cílový bod (pro logiku) ---
target = [WIDTH // 2 + 150, HEIGHT // 2 - 100]

# --- Hranice (trojúhelník) ---
boundary = [
    [250, 550],
    [650, 550],
    [450, 200]
]

tick = 0
MAX_HISTORY = 40

# Každá entita = signál
entities = []


# --- Logická pravidla -----------------------------------------------------

def nand_step(x, y, tx, ty):
    dx = 1 if tx > x else -1 if tx < x else 0
    dy = 1 if ty > y else -1 if ty < y else 0
    return x + dx, y + dy


def nor_step(x, y, tx, ty):
    dx = 1 if tx == x else 0
    dy = 1 if ty == y else 0
    return x + dx, y + dy


def xor_step(x, y, tx, ty):
    dx = 1 if tx > x else -1 if tx < x else 0
    dy = 1 if ty > y else -1 if ty < y else 0
    if (dx != 0) ^ (dy != 0):
        return x + dx, y + dy
    return x, y


ops = ["NAND", "NOR", "XOR"]


# --- Geometrie ------------------------------------------------------------

def inside_triangle(px, py, A, B, C):
    denom = (B[1] - C[1]) * (A[0] - C[0]) + (C[0] - B[0]) * (A[1] - C[1])
    a = ((B[1] - C[1]) * (px - C[0]) + (C[0] - B[0]) * (py - C[1])) / denom
    b = ((C[1] - A[1]) * (px - C[0]) + (A[0] - C[0]) * (py - C[1])) / denom
    c = 1 - a - b
    return a >= 0 and b >= 0 and c >= 0


# --- Projekce do 2D (tick = hloubka) --------------------------------------

def project(x, y, age):
    f = min(age / MAX_HISTORY, 1.0)
    vanish = (WIDTH // 2, HEIGHT // 2)
    px = int(x * (1 - f) + vanish[0] * f)
    py = int(y * (1 - f) + vanish[1] * f)
    return px, py


# --- Main loop ------------------------------------------------------------

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit();
            sys.exit()

    tick += 1

    # 1) Každý tick vytvoříme novou entitu v originu
    entities.append([origin[0], origin[1], tick])

    # 2) Vybereme logické pravidlo podle ticku
    rule = ops[tick % 3]

    # 3) Posuneme všechny entity
    new_entities = []
    for x, y, born in entities:

        if rule == "NAND":
            nx, ny = nand_step(x, y, target[0], target[1])
        elif rule == "NOR":
            nx, ny = nor_step(x, y, target[0], target[1])
        else:
            nx, ny = xor_step(x, y, target[0], target[1])

        # 4) Entita přežije jen pokud je uvnitř hranic
        if inside_triangle(nx, ny, *boundary):
            new_entities.append([nx, ny, born])

    entities = new_entities

    # --- Render -----------------------------------------------------------

    screen.fill((0, 0, 0))

    # hranice
    pygame.draw.polygon(screen, (80, 80, 80), boundary, 1)

    # cílový bod
    pygame.draw.circle(screen, (255, 0, 0), target, 6)

    # signály
    for x, y, born in entities:
        age = tick - born
        px, py = project(x, y, age)
        color = (255 - (age * 5) % 255, (age * 3) % 255, 200)
        pygame.draw.circle(screen, color, (px, py), 3)

    pygame.display.flip()
    clock.tick(60)
