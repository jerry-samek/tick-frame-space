#!/usr/bin/env python3
"""
Configuration for Experiment 51i (V9) - Multi-Entity Gravitational-Relativistic Time Dilation

Defines parameter sets for baseline and sweep configurations.
"""

from dataclasses import dataclass
from typing import List, Tuple
import numpy as np


@dataclass
class FieldParameters:
    """Parameters for load and energy field dynamics."""
    # Load field (reaction-diffusion)
    alpha: float = 0.012      # Diffusion coefficient
    gamma_damp: float = 0.0005  # Nonlinear damping
    scale: float = 0.75       # Source strength scaling

    # Energy field (regeneration-drainage)
    R: float = 1.2            # Regeneration rate per tick
    E_max: float = 15.0       # Maximum energy capacity
    D: float = 0.01           # Load-dependent drain coefficient

    # Computational thresholds
    capacity_min: float = 0.1  # Minimum capacity for work
    work_threshold: float = 0.5  # Minimum energy to perform work


@dataclass
class EntityConfiguration:
    """Configuration for entity populations."""
    # Planet cluster
    planet_count: int = 700
    planet_radius: float = 10.0
    planet_center: Tuple[float, float] = (50.0, 50.0)
    planet_tick_budget: int = 1

    # Mobile entities
    mobile_count_per_velocity: int = 5  # 5 entities per velocity regime
    mobile_distances: List[float] = None  # Orbital radii
    mobile_tick_budget: int = 1

    # Velocity regimes (in units of c)
    v_slow: float = 0.1
    v_moderate: float = 0.5
    v_fast: float = 0.9
    v_ultra: float = 0.99

    def __post_init__(self):
        if self.mobile_distances is None:
            self.mobile_distances = [15.0, 25.0, 35.0, 45.0]


@dataclass
class SimulationParameters:
    """Overall simulation parameters."""
    grid_size: int = 100
    num_ticks: int = 5000  # Substrate ticks to simulate
    dt: float = 1.0        # Time step (in substrate tick units)
    c: float = 1.0         # Speed of light (grid units per tick)

    # Output control
    snapshot_interval: int = 100  # Save state every N ticks
    verbose: bool = True


class ConfigurationSet:
    """
    Complete configuration for an experimental run.
    """
    def __init__(
        self,
        name: str = "baseline",
        field: FieldParameters = None,
        entities: EntityConfiguration = None,
        simulation: SimulationParameters = None
    ):
        self.name = name
        self.field = field or FieldParameters()
        self.entities = entities or EntityConfiguration()
        self.simulation = simulation or SimulationParameters()

    def __repr__(self):
        return f"ConfigurationSet(name='{self.name}')"

    def summary(self) -> str:
        """Return human-readable summary of configuration."""
        lines = [
            f"Configuration: {self.name}",
            "",
            "Field Parameters:",
            f"  alpha={self.field.alpha}, gamma={self.field.gamma_damp}, scale={self.field.scale}",
            f"  R={self.field.R}, E_max={self.field.E_max}, D={self.field.D}",
            "",
            "Entity Configuration:",
            f"  Planet: {self.entities.planet_count} entities at r<{self.entities.planet_radius}",
            f"  Mobile: {self.entities.mobile_count_per_velocity} per velocity × 4 velocities = {self.entities.mobile_count_per_velocity * 4} total",
            f"  Velocities: {self.entities.v_slow}c, {self.entities.v_moderate}c, {self.entities.v_fast}c, {self.entities.v_ultra}c",
            "",
            "Simulation:",
            f"  Grid: {self.simulation.grid_size}×{self.simulation.grid_size}",
            f"  Duration: {self.simulation.num_ticks} ticks",
            f"  Speed of light: c = {self.simulation.c}",
        ]
        return "\n".join(lines)


# ============================================================================
# Predefined Configurations
# ============================================================================

def baseline_config() -> ConfigurationSet:
    """
    Baseline configuration (Goldilocks parameters between V7 and V8).
    """
    return ConfigurationSet(
        name="baseline",
        field=FieldParameters(
            alpha=0.012,
            gamma_damp=0.0005,
            scale=0.75,
            R=1.2,
            E_max=15.0,
            D=0.01
        ),
        entities=EntityConfiguration(
            planet_count=700,
            planet_radius=10.0,
            mobile_count_per_velocity=5,
            mobile_distances=[15.0, 25.0, 35.0, 45.0],
            v_slow=0.1,
            v_moderate=0.5,
            v_fast=0.9,
            v_ultra=0.99
        ),
        simulation=SimulationParameters(
            grid_size=100,
            num_ticks=5000,
            snapshot_interval=100
        )
    )


def strong_field_config() -> ConfigurationSet:
    """
    Stronger gravitational field (closer to V7).
    """
    config = baseline_config()
    config.name = "strong_field"
    config.field.alpha = 0.011
    config.field.gamma_damp = 0.0007
    config.field.scale = 0.85
    config.field.R = 1.0
    config.field.E_max = 12.0
    return config


def weak_field_config() -> ConfigurationSet:
    """
    Weaker gravitational field (closer to V8).
    """
    config = baseline_config()
    config.name = "weak_field"
    config.field.alpha = 0.014
    config.field.gamma_damp = 0.0003
    config.field.scale = 0.65
    config.field.R = 1.5
    config.field.E_max = 20.0
    return config


def fast_motion_config() -> ConfigurationSet:
    """
    More entities at higher velocities (emphasize SR effects).
    """
    config = baseline_config()
    config.name = "fast_motion"
    config.entities.mobile_count_per_velocity = 8
    config.entities.v_slow = 0.3
    config.entities.v_moderate = 0.7
    config.entities.v_fast = 0.95
    config.entities.v_ultra = 0.995
    return config


def dense_planet_config() -> ConfigurationSet:
    """
    Denser planet cluster (stronger gravitational field).
    """
    config = baseline_config()
    config.name = "dense_planet"
    config.entities.planet_count = 1500
    config.entities.planet_radius = 8.0
    return config


# ============================================================================
# Parameter Sweep Utilities
# ============================================================================

def parameter_sweep_configs(
    base_config: ConfigurationSet = None,
    param_name: str = "alpha",
    values: List[float] = None
) -> List[ConfigurationSet]:
    """
    Generate configuration sweep over a single parameter.

    Args:
        base_config: Starting configuration (default: baseline)
        param_name: Field parameter to sweep (e.g., 'alpha', 'R', 'E_max')
        values: List of values to test

    Returns:
        List of configurations with varied parameter

    Example:
        configs = parameter_sweep_configs(
            param_name='alpha',
            values=[0.010, 0.012, 0.014, 0.016]
        )
    """
    if base_config is None:
        base_config = baseline_config()

    if values is None:
        # Default sweep ranges
        defaults = {
            'alpha': np.linspace(0.010, 0.015, 5),
            'gamma_damp': np.linspace(0.0003, 0.0007, 5),
            'scale': np.linspace(0.6, 0.9, 5),
            'R': np.linspace(1.0, 1.5, 5),
            'E_max': np.linspace(12.0, 20.0, 5),
            'D': np.linspace(0.005, 0.015, 5)
        }
        values = defaults.get(param_name, [0.012])

    configs = []
    for i, value in enumerate(values):
        # Clone base config
        import copy
        config = copy.deepcopy(base_config)
        config.name = f"{base_config.name}_sweep_{param_name}_{i}"

        # Set parameter
        if hasattr(config.field, param_name):
            setattr(config.field, param_name, value)
        else:
            raise ValueError(f"Unknown parameter: {param_name}")

        configs.append(config)

    return configs


# ============================================================================
# Configuration Registry
# ============================================================================

CONFIGURATIONS = {
    "baseline": baseline_config,
    "strong_field": strong_field_config,
    "weak_field": weak_field_config,
    "fast_motion": fast_motion_config,
    "dense_planet": dense_planet_config,
}


def get_config(name: str = "baseline") -> ConfigurationSet:
    """
    Retrieve configuration by name.

    Args:
        name: Configuration name (see CONFIGURATIONS dict)

    Returns:
        ConfigurationSet instance

    Available configurations:
        - baseline: Goldilocks parameters (recommended starting point)
        - strong_field: Stronger gravitational field
        - weak_field: Weaker gravitational field
        - fast_motion: More high-velocity entities
        - dense_planet: Denser planet cluster
    """
    if name not in CONFIGURATIONS:
        available = ", ".join(CONFIGURATIONS.keys())
        raise ValueError(f"Unknown configuration: {name}. Available: {available}")

    return CONFIGURATIONS[name]()


def list_configurations() -> List[str]:
    """Return list of available configuration names."""
    return list(CONFIGURATIONS.keys())


if __name__ == "__main__":
    # Demo: Print all available configurations
    print("=" * 70)
    print("EXPERIMENT 51i (V9) - AVAILABLE CONFIGURATIONS")
    print("=" * 70)
    print()

    for name in list_configurations():
        config = get_config(name)
        print(config.summary())
        print()
        print("-" * 70)
        print()
