"""
V17 - Canvas Ontology with Sparse Storage

This module implements the canvas/renderer model for tick-frame physics
with sparse gamma storage for O(entities) memory instead of O(grid^3).

Key Classes:
    Canvas3D: Sparse gamma storage (dict-based)
    Renderer: Stateless entity that paints on the canvas
    TickEvolution: Orchestrates double-buffer evolution

Conceptual Model:
    Particle = Renderer Head (stateless temporal process)
        ↓ renders pattern to
    Tick Window = Canvas (accumulated state of all previous renderings)
        ↓ seen by renderer as
    Current State = Gamma field gradient (influences next render location)

Author: V17 Implementation
Date: 2026-02-01
Based on: V16 expanding evolution + canvas ontology discussion
"""

from .config_v17 import Config17, QuickTestConfig, StandardConfig, LongRunConfig
from .canvas import Canvas3D
from .renderer import Renderer
from .evolution import TickEvolution

__all__ = [
    'Config17',
    'QuickTestConfig',
    'StandardConfig',
    'LongRunConfig',
    'Canvas3D',
    'Renderer',
    'TickEvolution',
]

__version__ = '17.0.0'
