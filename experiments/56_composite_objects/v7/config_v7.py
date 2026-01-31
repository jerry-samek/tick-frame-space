"""
V7 Configuration - Motion Dynamics Experiments

Inherits V6 optimal stability parameters and adds motion tracking settings.
"""

import sys
from pathlib import Path

# Add v6 to path for imports
v6_path = Path(__file__).parent.parent / "v6"
sys.path.insert(0, str(v6_path))

from config_v6 import ValidationConfig10k


class MotionConfig(ValidationConfig10k):
    """Configuration for V7 motion dynamics experiments."""

    # Override to V6 optimal values from jitter sweep + hybrid_strong
    jitter_strength = 0.119  # Critical jitter (zero-point equilibrium)
    gamma_modulation_strength = 1.0
    creation_sensitivity = 2.0  # hybrid_strong
    field_decay_threshold = 1.5  # hybrid_strong
    field_decay_rate = 0.05  # hybrid_strong

    # Motion tracking settings
    position_sample_interval = 10  # Record position every N ticks
    velocity_window = 10  # Ticks for velocity averaging
    msd_max_lag = 500  # Maximum lag for MSD calculation

    # Trajectory settings
    max_trajectory_length = 1000  # Max positions to store per pattern
    trajectory_downsample = 1  # Store every Nth position

    # Pattern identity settings
    coherence_radius = 7  # Radius for local energy calculation
    dissolution_threshold = 0.3  # Energy fraction below which pattern is "dissolved"
    reformation_threshold = 0.7  # Energy fraction above which pattern is "reformed"

    # Orbital analysis settings
    angular_velocity_window = 50  # Ticks for angular velocity averaging

    # Experiment duration
    num_ticks = 10_000
    progress_interval = 500


class QuickTestConfig(MotionConfig):
    """Quick test configuration (1k ticks, smaller grid for speed)."""

    # Smaller grid for faster testing
    grid_width = 100
    grid_height = 100
    n_patterns = 25  # Fewer patterns for smaller grid
    pattern_init_radius_mean = 10.0  # Scale down radius

    num_ticks = 500
    progress_interval = 50
    position_sample_interval = 5
    msd_max_lag = 100


class LongRunConfig(MotionConfig):
    """Long run configuration (100k ticks)."""

    num_ticks = 100_000
    progress_interval = 5_000
    position_sample_interval = 50
    msd_max_lag = 5_000
    max_trajectory_length = 2000


if __name__ == "__main__":
    config = MotionConfig()
    print("V7 Motion Configuration")
    print("=" * 50)
    print(f"Grid: {config.grid_width}x{config.grid_height}")
    print(f"Patterns: {config.n_patterns}")
    print(f"Jitter: {config.jitter_strength}")
    print(f"Ticks: {config.num_ticks:,}")
    print()
    print("Motion tracking:")
    print(f"  Position sample interval: {config.position_sample_interval}")
    print(f"  Velocity window: {config.velocity_window}")
    print(f"  MSD max lag: {config.msd_max_lag}")
    print(f"  Max trajectory length: {config.max_trajectory_length}")
    print()
    print("Pattern identity:")
    print(f"  Coherence radius: {config.coherence_radius}")
    print(f"  Dissolution threshold: {config.dissolution_threshold}")
    print(f"  Reformation threshold: {config.reformation_threshold}")
