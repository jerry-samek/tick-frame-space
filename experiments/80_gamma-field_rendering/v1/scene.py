# scene.py
"""
Scene and entity definitions in reference coordinates.
Entities are stored with reference positions and radii (in reference grid pixels).
"""

import numpy as np

class Entity:
    def __init__(self, uid, pos_ref, radius_ref, color=(1.0,1.0,1.0), emission=1.0, mode='comoving'):
        self.uid = uid
        self.pos_ref = np.array(pos_ref, dtype=float)  # normalized 0..1 or grid indices depending on convention
        self.radius_ref = radius_ref
        self.color = color
        self.emission = emission
        self.mode = mode  # 'comoving'|'conservative'|'dissipative'

    def copy(self):
        return {
            'uid': self.uid,
            'pos_ref': self.pos_ref.copy(),
            'radius_ref': float(self.radius_ref),
            'color': tuple(self.color),
            'emission': float(self.emission),
            'mode': self.mode
        }

def update_orbit(entity, center_ref, angular_speed, t):
    """
    Example: move entity in circular orbit in reference coords.
    center_ref: (x,y) in reference grid indices
    angular_speed: radians per tick
    """
    cx, cy = center_ref
    r = entity.radius_ref * 2.0  # example orbit radius
    x = cx + r * np.cos(angular_speed * t)
    y = cy + r * np.sin(angular_speed * t)
    entity.pos_ref = np.array([x, y])
