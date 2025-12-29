"""
Substrate Laws for Tick-Frame Physics

This package contains pluggable evolution laws that implement
the SubstrateLaw protocol.

Available Laws:
    - Law000_XOR: Theoretical baseline (binary XOR parity)
    - LawQuaternion: 3D movement via quaternion algebra

Usage:
    from tick_engine.laws import Law000_XOR, LawQuaternion

    # Choose your physics
    law = Law000_XOR()
    # or
    law = LawQuaternion()
"""

from tick_engine.laws.law000_xor import Law000_XOR, create_line_graph, create_cycle_graph
from tick_engine.laws.law_quaternion import LawQuaternion, create_3d_seed_graph

__all__ = [
    'Law000_XOR',
    'LawQuaternion',
    'create_line_graph',
    'create_cycle_graph',
    'create_3d_seed_graph'
]
