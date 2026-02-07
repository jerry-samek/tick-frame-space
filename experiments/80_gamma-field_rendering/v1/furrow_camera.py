# furrow_camera.py
"""
Simple 2D furrow camera: maps pixels to rays (2D lines) and samples fields.
Camera lives in physical coordinates; uses current scale s(t) to map reference coords.
"""

import numpy as np

class FurrowCamera2D:
    def __init__(self, screen_w=512, screen_h=512, fov=1.0, world_center=(0.5,0.5)):
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.fov = fov  # normalized physical extent fraction
        self.world_center = world_center
        self.pos = np.array([0.5, 0.5])  # center in physical coords (normalized)
        self.angle = 0.0  # rotation in radians
        self.furrow_depth = 1.0  # not used heavily in 2D sampling

    def pixel_to_physical(self, i, j, s):
        # reuse remap.pixel_to_physical semantics: compute physical coordinate
        extent = self.fov * s
        min_x = self.world_center[0] - extent / 2.0
        min_y = self.world_center[1] - extent / 2.0
        u = (i + 0.5) / self.screen_w
        v = (j + 0.5) / self.screen_h
        x_phys = min_x + u * extent
        y_phys = min_y + v * extent
        return x_phys, y_phys

    def move(self, dx, dy):
        self.pos += np.array([dx, dy])

    def rotate(self, dtheta):
        self.angle += dtheta
