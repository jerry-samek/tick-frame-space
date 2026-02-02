"""
V13 Layered Evolution - Evolution with per-entity layers and shared gamma.

Core mechanics:
1. Each tick, new entity spawns at origin (head prepending)
2. Jitter applies to each layer independently
3. Gamma field updated from all layers (shared memory)
4. Pull/Push model: gamma pulls, jitter pushes

The Pull/Push equilibrium:
- Gamma (memory) = attractive force
- Jitter = compensating back-pressure (the ONE constant)
- Pattern = where forces balance

Author: V13 Implementation
Date: 2026-01-31
Based on: V12d minimal evolution + multi-layer architecture
"""

import numpy as np
from typing import List, Optional

from multi_layer_grid import MultiLayerGrid
from entity import Entity, create_entity
from config_v13 import LayeredSubstrateConfig


class LayeredJitter:
    """Jitter that operates on individual layers with gamma-modulated push.

    The Pull/Push Model:
    - Gamma creates a "pull" toward high-gamma regions (memory attracts)
    - Jitter provides "push" as back-pressure (zero-point fluctuation)
    - Pattern survives where pull and push balance
    """

    def __init__(self, jitter_strength: float = 0.119, seed: int = 42):
        """Initialize layered jitter.

        Args:
            jitter_strength: Base probability of +1 or -1 (symmetric)
            seed: Random seed
        """
        self.jitter_strength = jitter_strength
        self.p_negative = jitter_strength
        self.p_zero = 1.0 - 2.0 * jitter_strength
        self.p_positive = jitter_strength
        self.rng = np.random.default_rng(seed)

    def apply_to_layer(self, layer: np.ndarray, gamma: Optional[np.ndarray] = None):
        """Apply jitter to a single layer in-place.

        If gamma is provided, jitter is modulated by gamma gradient:
        - High gamma regions get less jitter (pattern preserved)
        - Low gamma regions get full jitter (more fluctuation)

        Args:
            layer: 2D numpy array (modified in-place)
            gamma: Optional gamma field for modulation
        """
        if gamma is not None:
            # Modulate jitter by gamma - high gamma = less jitter
            # Normalize gamma to [0, 1] range
            gamma_max = np.max(gamma) if np.max(gamma) > 0 else 1.0
            gamma_norm = gamma / gamma_max

            # Higher gamma = lower jitter probability
            # This keeps patterns stable in high-memory regions
            effective_jitter = self.jitter_strength * (1.0 - 0.5 * gamma_norm)

            # Generate modulated jitter
            jitter = np.zeros_like(layer, dtype=np.int8)
            random_vals = self.rng.random(layer.shape)

            # Positive jitter where random < effective_jitter
            jitter[random_vals < effective_jitter] = 1
            # Negative jitter where random > (1 - effective_jitter)
            jitter[random_vals > (1.0 - effective_jitter)] = -1
        else:
            # Uniform jitter (no gamma modulation)
            jitter = self.rng.choice(
                [-1, 0, 1],
                size=layer.shape,
                p=[self.p_negative, self.p_zero, self.p_positive]
            )

        # Apply jitter with clamping to [-1, 0, +1]
        layer[:, :] = np.clip(layer + jitter, -1, 1).astype(np.int8)

    def __repr__(self) -> str:
        return f"LayeredJitter(strength={self.jitter_strength:.4f})"


class LayeredEvolution:
    """Evolution with per-entity layers and shared gamma.

    Each entity has its own field layer (temporal isolation).
    All entities share the gamma field (spatial coupling).
    """

    def __init__(self, grid: MultiLayerGrid, config: LayeredSubstrateConfig):
        """Initialize layered evolution.

        Args:
            grid: MultiLayerGrid to evolve
            config: V13 configuration
        """
        self.grid = grid
        self.config = config
        self.jitter = LayeredJitter(
            jitter_strength=config.jitter_strength,
            seed=config.random_seed
        )
        self.entities: List[Entity] = []
        self.tick_count = 0

        # Initialize energy field to config's energy_max (in case grid was
        # created without proper energy_max parameter)
        if config.time_dilation_enabled:
            self.grid.energy_field = np.ones(
                (grid.height, grid.width), dtype=np.float64
            ) * config.energy_max

    def create_entity(self, tick: int) -> Entity:
        """Create new entity at origin with its own layer.

        Args:
            tick: Current tick count

        Returns:
            New Entity instance
        """
        # Add new layer to grid
        layer_id = self.grid.add_layer()

        # Create entity
        entity = create_entity(
            tick=tick,
            layer_id=layer_id,
            origin=self.config.origin
        )

        # Initialize pattern at origin (single cell = +1)
        self._initialize_pattern(entity)

        self.entities.append(entity)
        return entity

    def _initialize_pattern(self, entity: Entity):
        """Initialize entity's pattern on its layer.

        Args:
            entity: Entity to initialize
        """
        layer = self.grid.get_layer(entity.layer_id)
        x, y = entity.position

        # Clamp to grid bounds
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))

        # Single cell at origin = +1
        layer[y, x] = 1

    def evolve_one_tick(self):
        """Execute one tick of evolution.

        Steps:
        1. Create new entity at origin
        2. Apply localized jitter around pattern centers
        3. Update entity positions based on pattern drift
        4. Update time dilation fields (load/energy)
        5. Update shared gamma from all layers (with spatially-varying decay)
        """
        self.tick_count += 1

        # 1. Create new entity at origin (head prepending)
        self.create_entity(self.tick_count)

        # 2. Apply localized jitter and track pattern centers
        for entity in self.entities:
            layer = self.grid.get_layer(entity.layer_id)
            self._evolve_entity_layer(entity, layer)

        # 3. Update time dilation fields (if enabled)
        if self.config.time_dilation_enabled:
            self._update_fields()

        # 4. Update shared gamma from all layers
        self._update_gamma()

    def _evolve_entity_layer(self, entity: Entity, layer: np.ndarray):
        """Evolve a single entity's layer.

        Applies localized jitter around the pattern center.
        Pattern center drifts based on jitter-induced imbalance.

        Args:
            entity: Entity being evolved
            layer: Entity's layer (modified in-place)
        """
        # Find current pattern center (center of mass of non-zero cells)
        nonzero_y, nonzero_x = np.nonzero(layer)

        if len(nonzero_x) == 0:
            # Pattern died - reinitialize at entity position
            x, y = entity.position
            x = max(0, min(self.grid.width - 1, x))
            y = max(0, min(self.grid.height - 1, y))
            layer[y, x] = 1
            return

        # Calculate center of mass
        center_x = np.mean(nonzero_x)
        center_y = np.mean(nonzero_y)

        # Apply jitter only to a local region around center
        # This prevents the pattern from spreading across the entire grid
        radius = 5 + len(nonzero_x) // 10  # Scale radius with pattern size
        radius = min(radius, 20)  # Cap at reasonable size

        x_min = max(0, int(center_x - radius))
        x_max = min(self.grid.width, int(center_x + radius + 1))
        y_min = max(0, int(center_y - radius))
        y_max = min(self.grid.height, int(center_y + radius + 1))

        # Get local region
        local = layer[y_min:y_max, x_min:x_max]
        local_gamma = self.grid.gamma[y_min:y_max, x_min:x_max]

        # Apply gamma-modulated jitter to local region
        self.jitter.apply_to_layer(local, gamma=local_gamma)

        # Update entity position to new center
        nonzero_y, nonzero_x = np.nonzero(layer)
        if len(nonzero_x) > 0:
            new_center_x = int(np.mean(nonzero_x))
            new_center_y = int(np.mean(nonzero_y))
            entity.position = (new_center_x, new_center_y)


    def _update_fields(self):
        """Update load and energy fields (Experiment 51 dynamics).

        Reaction-diffusion for load field:
            dL/dt = alpha * laplacian(L) + S(x,t) - gamma_damp * L^2

        Energy regeneration-drainage:
            dE/dt = R - D * L

        This creates time dilation: high load -> low energy -> slower gamma decay
        """
        # 1. Compute entity source field (where entities are)
        combined = self.grid.compute_combined_field()
        source = (np.abs(combined) > 0).astype(np.float64)

        # 2. Diffuse load field (discrete Laplacian with periodic boundary)
        L = self.grid.load_field
        laplacian = (
            np.roll(L, 1, axis=0) + np.roll(L, -1, axis=0) +
            np.roll(L, 1, axis=1) + np.roll(L, -1, axis=1) - 4 * L
        )

        # 3. Update load: diffusion + source - nonlinear damping
        self.grid.load_field = (
            L + self.config.load_diffusion * laplacian
            + source
            - self.config.load_damping * L * L
        )
        self.grid.load_field = np.clip(self.grid.load_field, 0, None)

        # 4. Update energy: regeneration - load-dependent drain
        E = self.grid.energy_field
        drain = self.config.energy_drain_rate * self.grid.load_field
        self.grid.energy_field = np.clip(
            E + self.config.energy_regen - drain,
            0, self.config.energy_max
        )

    def _update_gamma(self):
        """Update shared gamma field from combined layer state.

        Gamma = memory of where entities have been.
        All entities contribute to this shared memory.

        With time dilation enabled:
        - Local decay rate depends on energy field
        - Low energy (high load) = slower decay = time dilation
        - Creates "gravitational wells" in the memory field
        """
        # Combine all layers
        combined = self.grid.compute_combined_field()

        # Presence = any non-zero value
        presence = (np.abs(combined) > 0).astype(np.float64)

        if self.config.time_dilation_enabled:
            # Compute local decay rate from energy field
            # Low energy = high load = slower decay (time dilation effect)
            energy_ratio = self.grid.energy_field / self.config.energy_max

            # Interpolate between base decay (normal) and 0.999 (near-frozen)
            # energy_ratio = 1.0 -> decay = gamma_decay (normal)
            # energy_ratio = 0.0 -> decay = 0.999 (frozen, maximum dilation)
            local_decay = (
                self.config.gamma_decay * energy_ratio +
                0.999 * (1.0 - energy_ratio)
            )

            # Apply spatially-varying decay
            self.grid.gamma = (
                self.grid.gamma * local_decay +
                presence * self.config.gamma_imprint_strength
            )
        else:
            # Original uniform decay
            self.grid.gamma = (
                self.grid.gamma * self.config.gamma_decay +
                presence * self.config.gamma_imprint_strength
            )

    def evolve_n_ticks(
        self,
        n_ticks: int,
        progress_interval: int = 100,
        verbose: bool = True
    ) -> List[dict]:
        """Evolve for n ticks and track statistics.

        Args:
            n_ticks: Number of ticks to evolve
            progress_interval: Report progress every N ticks
            verbose: Print progress

        Returns:
            List of statistics dicts
        """
        history = []

        for tick in range(n_ticks):
            self.evolve_one_tick()

            if (tick + 1) % progress_interval == 0:
                stats = self.get_statistics()
                stats['tick'] = tick + 1
                history.append(stats)

                if verbose:
                    print(
                        f"[{tick+1:6d}/{n_ticks:6d}] "
                        f"entities={stats['entity_count']:4d}, "
                        f"energy={stats['total_energy']:5d}, "
                        f"gamma_sum={stats['gamma_sum']:.1f}"
                    )

        return history

    def get_statistics(self) -> dict:
        """Get current simulation statistics.

        Returns:
            Dict with entity count, energy, gamma stats, and time dilation fields
        """
        combined_stats = self.grid.get_combined_statistics()
        gamma_stats = self.grid.get_gamma_statistics()
        load_stats = self.grid.get_load_statistics()
        energy_stats = self.grid.get_energy_statistics()

        return {
            "entity_count": len(self.entities),
            "tick_count": self.tick_count,
            "total_energy": combined_stats["total_energy"],
            "nonzero_fraction": combined_stats["nonzero_fraction"],
            "layer_count": combined_stats["layer_count"],
            "gamma_sum": gamma_stats["gamma_sum"],
            "gamma_mean": gamma_stats["gamma_mean"],
            "gamma_max": gamma_stats["gamma_max"],
            # Time dilation fields
            "load_max": load_stats["load_max"],
            "load_mean": load_stats["load_mean"],
            "energy_min": energy_stats["energy_min"],
            "energy_mean": energy_stats["energy_mean"],
        }

    def __repr__(self) -> str:
        return (
            f"LayeredEvolution(tick={self.tick_count}, "
            f"entities={len(self.entities)}, "
            f"jitter={self.config.jitter_strength})"
        )


if __name__ == "__main__":
    from config_v13 import create_config

    print("LayeredEvolution Demo")
    print("=" * 70)

    # Create configuration
    config = create_config(grid_size=50)
    print(config.describe())
    print()

    # Create grid and evolution
    grid = MultiLayerGrid(config.grid_width, config.grid_height)
    evolution = LayeredEvolution(grid, config)

    print(f"Created: {evolution}")
    print()

    # Evolve for 100 ticks
    print("Evolving for 100 ticks...")
    print("-" * 70)
    history = evolution.evolve_n_ticks(100, progress_interval=20, verbose=True)
    print()

    # Final state
    print("=" * 70)
    print("FINAL STATE")
    print("=" * 70)
    stats = evolution.get_statistics()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print()

    # Visualize central region
    print("Combined field (central 30x30):")
    center_x = config.origin[0] - 15
    center_y = config.origin[1] - 15
    print(grid.visualize_combined_ascii(center_x, center_y, 30, 30))
    print()

    print("=" * 70)
