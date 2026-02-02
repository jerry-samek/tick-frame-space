"""
V15: Zero-Parameter Model

Eliminates ALL tunable parameters from V14:
- jitter_strength: REMOVED (derived from gamma)
- gamma_decay: REMOVED (gamma accumulates forever, use relative values)

Key insights:
1. Jitter = energy budget leftover
   - Entity gets 1 energy per tick
   - Pays gamma_cost = local_gamma to maintain memory
   - jitter_budget = 1 - gamma_cost (what's left for movement)

2. Gamma doesn't decay - use relative values
   - Gamma accumulates forever (no decay)
   - effective_gamma = (local - min) / (max - min) for normalization
   - Prevents infinity, preserves relative structure
   - Gradient unaffected (adding constant doesn't change derivatives)

3. Skip sensitivity = fixed constant (0.01)

Parameter reduction: 2 → 0 (100% reduction from V14)

Author: V15 Implementation
Date: 2026-01-31
Based on: V14 + gamma-derived jitter, no decay
"""

from .config_v15 import SubstrateConfig, create_config
from .entity import Entity, create_entity
from .multi_layer_grid import MultiLayerGrid
from .layered_evolution import LayeredEvolution

__all__ = [
    'SubstrateConfig',
    'create_config',
    'Entity',
    'create_entity',
    'MultiLayerGrid',
    'LayeredEvolution',
]
