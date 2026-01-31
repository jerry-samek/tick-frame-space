"""
V8 Configuration - Particle Accelerator Experiments

Extends V7 config with projectile parameters.
"""

import sys
from pathlib import Path

# Add v6 and v7 to path
v6_path = Path(__file__).parent.parent / "v6"
v7_path = Path(__file__).parent.parent / "v7"
sys.path.insert(0, str(v6_path))
sys.path.insert(0, str(v7_path))

from config_v7 import MotionConfig


class AcceleratorConfig(MotionConfig):
    """Configuration for V8 particle accelerator experiments."""

    # Use V7 optimal parameters for the target cloud
    # jitter_strength = 0.119
    # creation_sensitivity = 2.0
    # field_decay_threshold = 1.5
    # field_decay_rate = 0.05

    # Grid - use smaller for faster iteration
    grid_width = 100
    grid_height = 100
    n_patterns = 25
    pattern_init_radius_mean = 10.0

    # Projectile parameters
    projectile_pattern = "monopole"  # Pattern type for projectile
    projectile_start_radius = 40.0  # Distance from center where projectile starts
    projectile_angle = 0.0  # Angle of approach (radians, 0 = from right)
    projectile_speed = 0.5  # Cells per tick toward center
    projectile_delay = 100  # Ticks to let cloud stabilize before firing

    # Impact parameter (perpendicular offset from center line)
    # b = 0: head-on collision with cloud center
    # b > 0: grazing collision
    impact_parameter = 0.0

    # Gamma well parameters
    # Target well (static, at grid center)
    target_gamma_k = 50.0  # Gamma well strength for target cloud

    # Projectile well (moves with projectile)
    projectile_gamma_k = 20.0  # Gamma well strength for projectile (0 = no well)

    # Experiment settings
    num_ticks = 1000
    progress_interval = 50
    position_sample_interval = 5

    # Observation settings
    measure_before_ticks = 50  # Measure cloud state for N ticks before impact
    measure_after_ticks = 200  # Measure cloud state for N ticks after impact

    # Late gamma commit parameters (existence log)
    gamma_window_size = 50        # Ticks per sample window
    gamma_imprint_k = 10.0        # Imprint strength
    gamma_history_decay = 0.0     # 0 = no decay (accumulate), 1 = full reset
    gamma_late_commit_enabled = True  # Enable/disable late commit feature


class LowSpeedConfig(AcceleratorConfig):
    """Low-speed projectile (thermal-like)."""
    projectile_speed = 0.1  # Slow approach


class HighSpeedConfig(AcceleratorConfig):
    """High-speed projectile (relativistic-like)."""
    projectile_speed = 1.0  # Fast approach


class HeadOnConfig(AcceleratorConfig):
    """Head-on collision (b=0)."""
    impact_parameter = 0.0


class GrazingConfig(AcceleratorConfig):
    """Grazing collision (b=5)."""
    impact_parameter = 5.0


class MissConfig(AcceleratorConfig):
    """Near-miss (b=15, outside cloud)."""
    impact_parameter = 15.0


if __name__ == "__main__":
    config = AcceleratorConfig()
    print("V8 Accelerator Configuration")
    print("=" * 50)
    print(f"Grid: {config.grid_width}x{config.grid_height}")
    print(f"Target patterns: {config.n_patterns}")
    print(f"Jitter: {config.jitter_strength}")
    print()
    print("Projectile:")
    print(f"  Pattern: {config.projectile_pattern}")
    print(f"  Start radius: {config.projectile_start_radius}")
    print(f"  Speed: {config.projectile_speed} cells/tick")
    print(f"  Impact parameter: {config.impact_parameter}")
    print(f"  Delay before fire: {config.projectile_delay} ticks")
    print(f"  Gamma well k: {config.projectile_gamma_k}")
    print()
    print("Gamma Wells:")
    print(f"  Target k: {config.target_gamma_k}")
    print(f"  Projectile k: {config.projectile_gamma_k}")
