"""
V13 Layered Substrate with Shared Memory

Key insight: Temporal isolation with spatial coupling via shared gamma field.

Like Prolog lists: [NewEntity | ExistingUniverse]
- Each tick, new entity spawns at origin (the "head")
- Gamma field pressure distributes entities naturally
- No position parameter needed - emergence only

Architecture:
- Per-Entity (Isolated): Each entity owns a field layer
- Shared (Coupled): One gamma field that all entities contribute to

The ONE constant: Jitter = 0.119 (from V12d)

Pull/Push Model:
- Gamma = Pull (memory attracts)
- Jitter = Push (back-pressure compensates)
- Pattern = where forces balance
"""

from .multi_layer_grid import MultiLayerGrid
from .entity import Entity, create_entity
from .config_v13 import LayeredSubstrateConfig, create_config
from .layered_evolution import LayeredEvolution, LayeredJitter

__all__ = [
    "MultiLayerGrid",
    "Entity",
    "create_entity",
    "LayeredSubstrateConfig",
    "create_config",
    "LayeredEvolution",
    "LayeredJitter",
]
