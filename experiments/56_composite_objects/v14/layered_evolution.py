"""
V14 Layered Evolution - Evolution with tick skipping for time dilation.

Replaces V13's reaction-diffusion fields with simple tick skipping:
- Entity in gravitational well (high gamma gradient) skips ticks
- skip_probability = |gamma_gradient| * sensitivity
- sensitivity = 1 - gamma_decay (derived from existing parameter)

Core mechanics:
1. Each tick, new entity spawns at origin (head prepending)
2. For each entity: check skip probability based on gamma gradient
3. If skipping: accumulate tick count, no imprint
4. If acting: apply jitter, imprint ONCE (regardless of accumulated skips)
5. Update gamma with uniform decay

The key insight: Time dilation emerges from tick skipping without any new parameters.

Author: V14 Implementation
Date: 2026-01-31
Based on: V13 layered_evolution.py (simplified)
"""

import numpy as np
from typing import List, Optional

from multi_layer_grid import MultiLayerGrid
from entity import Entity, create_entity
from config_v14 import LayeredSubstrateConfig


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
    """Evolution with per-entity layers and tick skipping for time dilation.

    Each entity has its own field layer (temporal isolation).
    All entities share the gamma field (spatial coupling).

    V14 simplification: Time dilation via tick skipping instead of
    reaction-diffusion fields.
    """

    def __init__(self, grid: MultiLayerGrid, config: LayeredSubstrateConfig):
        """Initialize layered evolution.

        Args:
            grid: MultiLayerGrid to evolve
            config: V14 configuration
        """
        self.grid = grid
        self.config = config
        self.jitter = LayeredJitter(
            jitter_strength=config.jitter_strength,
            seed=config.random_seed
        )
        self.rng = np.random.default_rng(config.random_seed + 1000)  # Separate RNG for skipping
        self.entities: List[Entity] = []
        self.tick_count = 0

        # Statistics for tick skipping
        self.total_skips = 0
        self.total_acts = 0

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

    def _compute_skip_probability(self, position: tuple) -> float:
        """Compute probability to skip tick based on gamma gradient.

        Entity in gravitational well (high gradient) has higher skip probability.
        This is the core time dilation mechanism.

        Args:
            position: Entity position (x, y)

        Returns:
            Skip probability in [0, 0.9]
        """
        x, y = position
        gamma = self.grid.gamma
        h, w = gamma.shape

        # Clamp position to grid
        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))

        # Compute gradient at position (central difference with wrapping)
        grad_x = (gamma[y, (x + 1) % w] - gamma[y, (x - 1) % w]) / 2.0
        grad_y = (gamma[(y + 1) % h, x] - gamma[(y - 1) % h, x]) / 2.0
        pull = np.sqrt(grad_x**2 + grad_y**2)

        # Sensitivity derived from gamma_decay
        # Higher decay = faster fading = less pull effect = lower sensitivity
        sensitivity = self.config.skip_sensitivity  # = 1 - gamma_decay

        # Skip probability: pull * sensitivity
        # Capped at 0.9 to ensure entity can always eventually act
        skip_prob = min(pull * sensitivity, 0.9)

        return float(skip_prob)

    def evolve_one_tick(self):
        """Execute one tick of evolution.

        Steps:
        1. Create new entity at origin
        2. For each entity: check skip, evolve if acting
        3. Update shared gamma (uniform decay)
        """
        self.tick_count += 1

        # 1. Create new entity at origin (head prepending)
        self.create_entity(self.tick_count)

        # 2. For each entity: check skip probability, evolve if acting
        for entity in self.entities:
            skip_prob = self._compute_skip_probability(entity.position)

            if self.rng.random() < skip_prob:
                # Skip this tick - entity experiences time dilation
                entity.skip_tick()
                self.total_skips += 1
            else:
                # Entity acts - apply jitter and imprint
                entity.act_tick()
                self.total_acts += 1

                layer = self.grid.get_layer(entity.layer_id)
                self._evolve_entity_layer(entity, layer)

                # Imprint ONCE at entity position (regardless of accumulated skips)
                self._imprint_gamma(entity.position)

        # 3. Apply uniform gamma decay
        self.grid.gamma *= self.config.gamma_decay

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

    def _imprint_gamma(self, position: tuple):
        """Imprint gamma at position.

        Always imprints strength=1.0 (one action = one imprint).
        This maintains energy conservation regardless of skip accumulation.

        Args:
            position: (x, y) position to imprint
        """
        x, y = position
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))

        self.grid.gamma[y, x] += self.config.gamma_imprint_strength

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
                        f"gamma_sum={stats['gamma_sum']:.1f}, "
                        f"skip_rate={stats['skip_rate']:.2f}"
                    )

        return history

    def get_statistics(self) -> dict:
        """Get current simulation statistics.

        Returns:
            Dict with entity count, energy, gamma stats, and skip stats
        """
        combined_stats = self.grid.get_combined_statistics()
        gamma_stats = self.grid.get_gamma_statistics()

        # Compute average time dilation across entities
        if self.entities:
            avg_dilation = sum(e.time_dilation_factor for e in self.entities) / len(self.entities)
        else:
            avg_dilation = 1.0

        # Global skip rate
        total = self.total_acts + self.total_skips
        skip_rate = self.total_skips / total if total > 0 else 0.0

        return {
            "entity_count": len(self.entities),
            "tick_count": self.tick_count,
            "total_energy": combined_stats["total_energy"],
            "nonzero_fraction": combined_stats["nonzero_fraction"],
            "layer_count": combined_stats["layer_count"],
            "gamma_sum": gamma_stats["gamma_sum"],
            "gamma_mean": gamma_stats["gamma_mean"],
            "gamma_max": gamma_stats["gamma_max"],
            "gradient_max": gamma_stats["gradient_max"],
            "gradient_mean": gamma_stats["gradient_mean"],
            # Tick skipping stats
            "total_skips": self.total_skips,
            "total_acts": self.total_acts,
            "skip_rate": skip_rate,
            "avg_time_dilation": avg_dilation,
        }

    def __repr__(self) -> str:
        return (
            f"LayeredEvolution(tick={self.tick_count}, "
            f"entities={len(self.entities)}, "
            f"jitter={self.config.jitter_strength}, "
            f"skip_rate={self.total_skips/(self.total_acts+self.total_skips+1):.2f})"
        )


if __name__ == "__main__":
    from config_v14 import create_config

    print("V14 LayeredEvolution Demo")
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

    # Time dilation distribution
    print("Time dilation factors (sample of entities):")
    for entity in evolution.entities[:10]:
        print(f"  Entity {entity.entity_id}: dilation={entity.time_dilation_factor:.2f} "
              f"(acts={entity.total_acts}, skips={entity.total_skips})")
    print()

    # Visualize central region
    print("Combined field (central 30x30):")
    center_x = config.origin[0] - 15
    center_y = config.origin[1] - 15
    print(grid.visualize_combined_ascii(center_x, center_y, 30, 30))
    print()

    print("=" * 70)
