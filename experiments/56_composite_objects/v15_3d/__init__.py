"""
V15-3D: Zero-Parameter Model in 3D

Extends V15 (2D) zero-parameter model to 3D while preserving:
1. Zero tunable parameters
2. Derived jitter from gamma
3. Time dilation via tick skipping
4. Pattern deformation mechanics

Key 3D changes:
- Position/Coordinates: (x, y, z) instead of (x, y)
- Grid shape: (depth, height, width) instead of (height, width)
- Gradient: 3 components (grad_x, grad_y, grad_z)
- Neighbors: 26 (3^3 - 1) instead of 8 (3^2 - 1)

Theory: 3D is the "Goldilocks" dimension (5% variance vs 22% for 2D).

Author: V15-3D Implementation
Date: 2026-02-01
Based on: V15 (2D) + 3D extensions
"""

from .config_v15_3d import SubstrateConfig3D, create_config
from .entity import Entity, create_entity
from .multi_layer_grid_3d import MultiLayerGrid3D
from .layered_evolution_3d import LayeredEvolution3D

__all__ = [
    'SubstrateConfig3D',
    'create_config',
    'Entity',
    'create_entity',
    'MultiLayerGrid3D',
    'LayeredEvolution3D',
]
