# experiments/132_grow_until_observed/conftest.py
"""Make modules importable without the leading-digit package prefix."""
import os
import sys
sys.path.insert(0, os.path.dirname(__file__))
