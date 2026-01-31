"""
V9 Configuration - Decay Sweep Experiments

Tests gamma_history_decay values from 0.1 to 0.9 to determine
optimal memory persistence for stable, physically accurate confinement.

Hypothesis:
- decay=0.0 (V8): Perfect memory, possibly unrealistic permanence
- decay=1.0: No memory, no confinement effect
- decay=0.3-0.7: "Goldilocks zone" for physically realistic behavior?
"""

import sys
from pathlib import Path

# Add v6, v7, v8 to path
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
v8_path = Path(__file__).parent.parent / "v8"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))
sys.path.insert(0, str(v8_path))

from config_v8 import AcceleratorConfig


class DecaySweepConfig(AcceleratorConfig):
    """Configuration for V9 decay sweep experiments."""

    # Inherit V8 base parameters
    # Grid: 100x100, 25 patterns, jitter=0.119

    # Experiment parameters
    num_ticks = 2000  # Longer run to see stability effects
    progress_interval = 100

    # Late gamma commit - always enabled for decay experiments
    gamma_late_commit_enabled = True
    gamma_window_size = 50
    gamma_imprint_k = 10.0

    # Decay value to test (will be overridden per experiment)
    gamma_history_decay = 0.5  # Default middle value

    # Disable projectile for pure cloud stability test
    projectile_delay = 99999  # Never fire

    # Stability measurement
    stability_measurement_start = 500  # Start measuring after this tick
    stability_measurement_interval = 50  # Measure every N ticks


# Pre-defined decay configurations
DECAY_VALUES = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]


def create_decay_config(decay: float) -> DecaySweepConfig:
    """Create a config with specific decay value."""
    config = DecaySweepConfig()
    config.gamma_history_decay = decay
    return config


if __name__ == "__main__":
    print("V9 Decay Sweep Configuration")
    print("=" * 50)

    config = DecaySweepConfig()
    print(f"Grid: {config.grid_width}x{config.grid_height}")
    print(f"Patterns: {config.n_patterns}")
    print(f"Jitter: {config.jitter_strength}")
    print(f"Ticks: {config.num_ticks}")
    print()
    print("Late Gamma Commit:")
    print(f"  Window size: {config.gamma_window_size}")
    print(f"  Imprint k: {config.gamma_imprint_k}")
    print(f"  Decay: {config.gamma_history_decay}")
    print()
    print(f"Decay values to test: {DECAY_VALUES}")
