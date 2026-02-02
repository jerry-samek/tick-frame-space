"""
V16: Expanding Grid Zero-Parameter Model

Extends V15-3D with space expansion - grid grows over time to match
tick-frame physics where space expands with each tick.

Key changes from V15-3D:
- Grid expands by 1 cell per axis every N ticks
- Entity positions shift as grid expands (stay centered)
- Memory monitoring for safety
- Limited to 500 ticks for memory budget

Theory connection: In tick-frame physics, space expands with each tick.
Fixed grids are artificial - expanding grids better match the theory.

Author: V16 Implementation
Date: 2026-02-01
Based on: V15-3D + expanding grid mechanics
"""

from .config_v16 import SubstrateConfig16, create_config
from .entity import Entity, create_entity
from .expanding_grid import ExpandingGrid3D
from .expanding_evolution import ExpandingEvolution3D

__all__ = [
    'SubstrateConfig16',
    'create_config',
    'Entity',
    'create_entity',
    'ExpandingGrid3D',
    'ExpandingEvolution3D',
]
