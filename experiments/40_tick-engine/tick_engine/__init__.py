"""
Unified Tick-Frame Physics Engine

A pluggable, law-agnostic engine for exploring tick-frame physics theories.

Basic Usage:
    >>> from tick_engine.core import Substrate, TickEngine, VisualizationEngine
    >>> from tick_engine.laws import Law000_XOR
    >>>
    >>> law = Law000_XOR()
    >>> substrate = Substrate(graph, initial_state, law)
    >>> engine = TickEngine(substrate)
    >>> engine.start()
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

__version__ = '1.0.0'
