"""
V14: Parameter Elimination via Tick Skipping

Simplifies time dilation from V13's reaction-diffusion fields to emergent
tick skipping based on gamma gradient (gravitational pull).

Key insight: Entity in gravitational well must "pay" for the pull by skipping ticks.

Parameter reduction: 10 → 2 (80% reduction from V13)
- jitter_strength: 0.119 (push force)
- gamma_decay: 0.99 (memory persistence, determines skip sensitivity)

Author: V14 Implementation
Date: 2026-01-31
Based on: V13 + tick skipping concept
"""

from .config_v14 import LayeredSubstrateConfig, create_config
from .entity import Entity, create_entity
from .multi_layer_grid import MultiLayerGrid
from .layered_evolution import LayeredEvolution

__all__ = [
    'LayeredSubstrateConfig',
    'create_config',
    'Entity',
    'create_entity',
    'MultiLayerGrid',
    'LayeredEvolution',
]
