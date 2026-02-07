#!/usr/bin/env python3
# test_final_diagnosis.py
"""
Final diagnosis test: Create a simple square pattern and see how pygame renders it.
"""

import numpy as np
import pygame

pygame.init()

# Create a simple test pattern: white square at specific coordinates
img_h = 512
img_w = 512
img = np.zeros((img_h, img_w, 3), dtype=np.uint8)

# Draw a white square from (100, 100) to (150, 150) in [row, column] indexing
img[100:150, 100:150] = [255, 255, 255]

# Draw a red square from (300, 200) to (350, 250)
img[300:350, 200:250] = [255, 0, 0]

print(f"Image shape: {img.shape}")
print("Drew white square at rows[100:150], cols[100:150]")
print("Drew red square at rows[300:350], cols[200:250]")

# Test different rendering approaches
screen = pygame.display.set_mode((1024, 512))
pygame.display.set_caption("Test pygame rendering")

# Approach 1: No transformation
print("\nApproach 1: Direct image")
try:
    # This should treat first dim as width
    surf1 = pygame.surfarray.make_surface(img.copy())
    print(f"  Surface size: {surf1.get_size()}")
    print(f"  Expected: (512, 512)")
except Exception as e:
    print(f"  Error: {e}")
    surf1 = None

# Approach 2: Transpose (1, 0, 2) -  swap H and W
print("\nApproach 2: Transpose (1,0,2)")
img_trans = np.transpose(img, (1, 0, 2))
surf2 = pygame.surfarray.make_surface(img_trans)
print(f"  Image after transpose shape: {img_trans.shape}")
print(f"  Surface size: {surf2.get_size()}")
print(f"  Expected: (512, 512)")

# Draw and analyze
clock = pygame.time.Clock()
running = True
mode = 0

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                mode = (mode + 1) % 2

    screen.fill((50, 50, 50))

    if mode == 0 and surf1:
        screen.blit(surf1, (0, 0))
        text_str = "Approach 1: Direct image"
        expected = "White at top-left (rows 100-150, cols 100-150)"
        expected2 = "Red at (rows 300-350, cols 200-250)"
    else:
        screen.blit(surf2, (0, 0))
        text_str = "Approach 2: Transposed (1,0,2)"
        expected = "After transpose axes swap"
        expected2 = "Coordinates should be (cols, rows) = (width, height)"

    font = pygame.font.Font(None, 20)
    text1 = font.render(text_str, True, (255, 255, 255))
    text2 = font.render(expected, True, (255, 255, 0))
    text3 = font.render(expected2, True, (255, 255, 0))
    screen.blit(text1, (10, 10))
    screen.blit(text2, (10, 35))
    screen.blit(text3, (10, 60))

    text_space = font.render("Press SPACE to toggle", True, (200, 200, 200))
    screen.blit(text_space, (10, 85))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()

print("\nAnalysis:")
print("If white square appears at top-left and red lower-right: correct rendering")
print("If they appear at different positions: there's a coordinate mapping issue")
