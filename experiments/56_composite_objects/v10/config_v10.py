"""
V10 Configuration - Parameter Simplification via Renormalization

Eliminates gamma_history_decay as a free parameter by using renormalization
instead of explicit decay. The "decay" effect emerges naturally from
normalizing history contributions against total accumulated history.

Key insight from V9: decay ≈ 0.85 × jitter is the coherence condition.
V10 aims to make this coupling emerge naturally without manual tuning.
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


class RenormalizationConfig(AcceleratorConfig):
    """Configuration for V10 renormalization experiments.

    Key difference from V9: No gamma_history_decay parameter.
    Instead, we use normalization to achieve natural decay.
    """

    # Inherit V8 base parameters
    # Grid: 100x100, 25 patterns, jitter=0.119

    # Experiment parameters
    num_ticks = 2000  # Longer run to see stability effects
    progress_interval = 100

    # Late gamma commit - always enabled
    gamma_late_commit_enabled = True
    gamma_window_size = 50
    gamma_imprint_k = 10.0

    # NO gamma_history_decay parameter - replaced by normalization
    # gamma_history_decay = REMOVED

    # Normalization type: 'global_sum', 'time_based', 'local_gamma'
    normalization_type = 'global_sum'

    # Normalization scale factor (for global_sum and local_gamma)
    # Controls how quickly normalization kicks in
    normalization_scale = 1000.0  # N in: history / (1 + sum(history) / N)

    # Disable projectile for pure cloud stability test
    projectile_delay = 99999  # Never fire

    # Stability measurement
    stability_measurement_start = 500  # Start measuring after this tick
    stability_measurement_interval = 50  # Measure every N ticks


# Normalization type configurations
class GlobalSumNormConfig(RenormalizationConfig):
    """Normalization by global sum of history."""
    normalization_type = 'global_sum'
    normalization_scale = 1000.0


class TimeBasedNormConfig(RenormalizationConfig):
    """Normalization by commit count (time-based)."""
    normalization_type = 'time_based'
    normalization_scale = 1.0  # Direct: history / (1 + commits)


class LocalGammaNormConfig(RenormalizationConfig):
    """Normalization by local gamma value."""
    normalization_type = 'local_gamma'
    normalization_scale = 1.0  # Direct: history / gamma_base


# Scale factor sweep configurations
NORMALIZATION_SCALES = [100.0, 500.0, 1000.0, 2000.0, 5000.0]


def create_normalization_config(
    norm_type: str,
    scale: float = 1000.0
) -> RenormalizationConfig:
    """Create a config with specific normalization settings.

    Args:
        norm_type: One of 'global_sum', 'time_based', 'local_gamma'
        scale: Normalization scale factor

    Returns:
        Configured RenormalizationConfig
    """
    config = RenormalizationConfig()
    config.normalization_type = norm_type
    config.normalization_scale = scale
    return config


if __name__ == "__main__":
    print("V10 Renormalization Configuration")
    print("=" * 50)

    config = RenormalizationConfig()
    print(f"Grid: {config.grid_width}x{config.grid_height}")
    print(f"Patterns: {config.n_patterns}")
    print(f"Jitter: {config.jitter_strength}")
    print(f"Ticks: {config.num_ticks}")
    print()
    print("Late Gamma Commit:")
    print(f"  Window size: {config.gamma_window_size}")
    print(f"  Imprint k: {config.gamma_imprint_k}")
    print(f"  Decay: NOT USED (renormalization instead)")
    print()
    print("Renormalization:")
    print(f"  Type: {config.normalization_type}")
    print(f"  Scale: {config.normalization_scale}")
    print()
    print("Normalization types to test:")
    print("  - global_sum: history / (1 + sum(history) / N)")
    print("  - time_based: history / (1 + commits)")
    print("  - local_gamma: history / gamma_base")
