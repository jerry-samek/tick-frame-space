# utils.py
"""
Small helpers: clamp, lerp, color conversions.
"""

import numpy as np

def clamp(x, a, b):
    return max(a, min(b, x))

def srgb_to_linear(c):
    return (c / 255.0) ** 2.2

def linear_to_srgb(c):
    return int((c ** (1/2.2)) * 255)
