"""
Integer Random Number Generation for V5

Uses Python's random module to generate floats, then converts to scaled integers.
Simpler than implementing Box-Muller in pure integer arithmetic.

Author: V5 Integer Conversion
Date: 2026-01-24
"""

import random
import math
from fixed_point import FixedPoint


def gaussian_int(mean_scaled: int, std_scaled: int) -> int:
    """
    Generate Gaussian random number as scaled integer.

    Args:
        mean_scaled: Mean value (scaled integer)
        std_scaled: Standard deviation (scaled integer)

    Returns:
        Scaled integer: Gaussian(mean, std)
    """
    # Generate float using Python's random
    mean_float = FixedPoint.to_float(mean_scaled)
    std_float = FixedPoint.to_float(std_scaled)

    value_float = random.gauss(mean_float, std_float)

    # Convert back to scaled integer
    return FixedPoint.from_float(value_float)


def uniform_int(min_scaled: int, max_scaled: int) -> int:
    """
    Generate uniform random number as scaled integer.

    Args:
        min_scaled: Minimum value (scaled integer)
        max_scaled: Maximum value (scaled integer)

    Returns:
        Scaled integer: Uniform(min, max)
    """
    min_float = FixedPoint.to_float(min_scaled)
    max_float = FixedPoint.to_float(max_scaled)

    value_float = random.uniform(min_float, max_float)

    return FixedPoint.from_float(value_float)


def uniform_angle() -> int:
    """
    Generate random angle in [0, 2π] as scaled integer.

    Returns:
        Scaled integer: angle in radians
    """
    angle_float = random.uniform(0, 2 * math.pi)
    return FixedPoint.from_float(angle_float)
