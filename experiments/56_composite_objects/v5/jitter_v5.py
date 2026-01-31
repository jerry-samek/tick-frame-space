"""
Zero-Point Jitter for V5 (Integer Arithmetic)

Applies Gaussian velocity kicks to simulate quantum zero-point energy.

Author: V5 Integer Conversion
Date: 2026-01-24
Based on: V4 zero_point_jitter.py
"""

from fragment_v5 import FragmentV5, FragmentedCloudV5
from random_v5 import gaussian_int
from fixed_point import FixedPoint


def apply_jitter_v5(cloud: FragmentedCloudV5, jitter_strength_scaled: int):
    """
    Apply zero-point jitter to all fragments.

    Adds Gaussian velocity kicks: dv ~ N(0, jitter_strength)

    Args:
        cloud: Fragmented electron cloud
        jitter_strength_scaled: Standard deviation of velocity kicks (scaled integer)
    """
    mean_zero = 0

    for frag in cloud.fragments:
        # Generate Gaussian velocity kicks
        dvx = gaussian_int(mean_zero, jitter_strength_scaled)
        dvy = gaussian_int(mean_zero, jitter_strength_scaled)

        # Apply to velocity
        frag.vx += dvx
        frag.vy += dvy
