"""
V11 Configuration - Parameter Unification via Well=Window Coupling

Key insight: target_gamma_k = gamma_window_size (both are temporal measures)

Physical meaning: The central gamma well represents "a pattern that has existed
for window_size ticks at full density." An eternal pattern accumulates gamma
equal to the window size - the well IS the steady-state of accumulated history.

Parameters reduced: 9 → 8 (target_gamma_k derived from gamma_window_size)
"""

import sys
from pathlib import Path

# Add parent versions to path
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
v10_path = Path(__file__).parent.parent / "v10"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))
sys.path.insert(0, str(v10_path))

from config_v10 import RenormalizationConfig


class WellWindowConfig(RenormalizationConfig):
    """Configuration with well=window coupling.

    Key change from V10: target_gamma_k is derived, not independent.

    The central well strength equals the window size because:
    - gamma_window_size = how many ticks of history we track
    - A pattern that has "always existed" accumulates gamma = window_size
    - Therefore, the well strength (representing eternal presence) = window_size

    This reduces the parameter count from 9 to 8.
    """

    # Primary temporal parameter
    gamma_window_size = 50  # Ticks per history window

    # Derived parameter (DO NOT SET DIRECTLY)
    # target_gamma_k is computed as a property

    # Use time_based normalization (recommended from V10)
    normalization_type = 'time_based'

    # Experiment settings
    num_ticks = 2000
    progress_interval = 100

    @property
    def target_gamma_k(self) -> float:
        """Central well strength derived from window size.

        Physical interpretation: An eternal pattern at full density
        accumulates gamma equal to one full window of presence.
        """
        return float(self.gamma_window_size)

    def __init__(self, window_size: int = 50):
        """Initialize with specific window size.

        Args:
            window_size: Ticks per history window (also sets well strength)
        """
        super().__init__()
        self.gamma_window_size = window_size
        # Note: target_gamma_k is computed via property, not stored


# Window size sweep configurations
WINDOW_SIZES = [25, 50, 75, 100]


class Window25Config(WellWindowConfig):
    """Window=25 (weaker confinement)."""
    gamma_window_size = 25


class Window50Config(WellWindowConfig):
    """Window=50 (V10 baseline)."""
    gamma_window_size = 50


class Window75Config(WellWindowConfig):
    """Window=75 (stronger confinement)."""
    gamma_window_size = 75


class Window100Config(WellWindowConfig):
    """Window=100 (very strong confinement)."""
    gamma_window_size = 100


def create_window_config(window_size: int) -> WellWindowConfig:
    """Create a config with specific window size.

    Args:
        window_size: Ticks per history window (also sets well strength)

    Returns:
        Configured WellWindowConfig
    """
    config = WellWindowConfig(window_size)
    return config


if __name__ == "__main__":
    print("V11 Well=Window Configuration")
    print("=" * 60)
    print()
    print("KEY INSIGHT: target_gamma_k = gamma_window_size")
    print()
    print("Physical meaning: The central well represents 'a pattern")
    print("that has existed for window_size ticks at full density.'")
    print()
    print("Parameter reduction: 9 -> 8 (well strength derived)")
    print()
    print("=" * 60)
    print()

    for ws in WINDOW_SIZES:
        config = create_window_config(ws)
        print(f"Window={ws}:")
        print(f"  gamma_window_size = {config.gamma_window_size}")
        print(f"  target_gamma_k    = {config.target_gamma_k} (derived)")
        print(f"  gamma_imprint_k   = {config.gamma_imprint_k}")
        print(f"  jitter_strength   = {config.jitter_strength}")
        print()

    print("=" * 60)
    print()
    print("Fixed 'game rules' (5):")
    config = WellWindowConfig()
    print(f"  ca_survival_threshold = {config.ca_survival_threshold}")
    print(f"  ca_creation_threshold = {config.ca_creation_threshold}")
    print(f"  field_decay_threshold = {config.field_decay_threshold}")
    print(f"  field_decay_rate      = {config.field_decay_rate}")
    print(f"  creation_sensitivity  = {config.creation_sensitivity}")
    print()
    print("Tunable physics parameters (3 remaining independent):")
    print(f"  jitter_strength       = {config.jitter_strength}")
    print(f"  gamma_window_size     = {config.gamma_window_size} (also sets well)")
    print(f"  gamma_imprint_k       = {config.gamma_imprint_k}")
