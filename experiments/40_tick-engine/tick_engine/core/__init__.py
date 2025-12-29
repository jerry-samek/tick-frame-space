"""
Core engine components for tick-frame physics simulation.

This module contains the law-agnostic engine infrastructure:
    - law_interface.py - Protocol for defining laws
    - substrate.py - Generic graph + state container
    - tick_engine.py - Asynchronous tick producer
    - visualization_engine.py - Asynchronous visualization consumer
"""

from tick_engine.core.law_interface import SubstrateLaw, StateType
from tick_engine.core.substrate import Substrate
from tick_engine.core.tick_engine import TickEngine, TickSnapshot
from tick_engine.core.visualization_engine import VisualizationEngine

__all__ = [
    'SubstrateLaw',
    'StateType',
    'Substrate',
    'TickEngine',
    'TickSnapshot',
    'VisualizationEngine'
]
