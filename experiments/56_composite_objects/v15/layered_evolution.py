"""
V15 Layered Evolution - Zero-parameter evolution with derived jitter.

Key changes from V14:
1. NO gamma decay - gamma accumulates forever
2. Jitter derived from effective gamma: jitter = 1 - effective_gamma
3. Position-dependent jitter (high gamma = low jitter, low gamma = high jitter)

Physical model:
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - effective_gamma left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

Behavior by region:
- Origin (dense): gamma_eff ~1.0, jitter ~0.0, frozen/time-dilated
- Mid-range: gamma_eff ~0.5, jitter ~0.5, balanced
- Edge (sparse): gamma_eff ~0.0, jitter ~1.0, mobile/normal time

Author: V15 Implementation
Date: 2026-01-31
Based on: V14 layered_evolution.py (gamma decay removed, jitter derived)
"""

import numpy as np
from typing import List, Optional

from multi_layer_grid import MultiLayerGrid
from entity import Entity, create_entity
from config_v15 import SubstrateConfig


class LayeredJitter:
    """Jitter with position-dependent strength derived from gamma.

    In V15, jitter_strength is NOT a parameter - it's derived from
    the local effective gamma value:
        jitter_strength = 1 - effective_gamma

    High gamma regions (memory-rich) have low jitter (patterns preserved).
    Low gamma regions (memory-poor) have high jitter (fluctuation).
    """

    def __init__(self, seed: int = 42):
        """Initialize layered jitter.

        Args:
            seed: Random seed
        """
        self.rng = np.random.default_rng(seed)

    def apply_to_layer_with_derived_jitter(
        self,
        layer: np.ndarray,
        effective_gamma: np.ndarray,
        local_region: Optional[tuple] = None
    ):
        """Apply jitter to a layer with position-dependent strength.

        Jitter strength at each position = 1 - effective_gamma at that position.
        This means:
        - High gamma regions: low jitter (patterns preserved)
        - Low gamma regions: high jitter (more fluctuation)

        Args:
            layer: 2D numpy array (modified in-place)
            effective_gamma: 2D array of effective gamma values [0, 1]
            local_region: Optional (y_min, y_max, x_min, x_max) to apply only to region
        """
        if local_region is not None:
            y_min, y_max, x_min, x_max = local_region
            layer_slice = layer[y_min:y_max, x_min:x_max]
            gamma_slice = effective_gamma[y_min:y_max, x_min:x_max]
        else:
            layer_slice = layer
            gamma_slice = effective_gamma

        # Derive jitter strength from gamma: jitter = 1 - gamma_eff
        # Clamp to [0.01, 0.99] for stability
        jitter_strength = np.clip(1.0 - gamma_slice, 0.01, 0.99)

        # Generate random values
        random_vals = self.rng.random(layer_slice.shape)

        # Positive jitter where random < jitter_strength
        # Negative jitter where random > (1 - jitter_strength)
        jitter = np.zeros_like(layer_slice, dtype=np.int8)
        jitter[random_vals < jitter_strength] = 1
        jitter[random_vals > (1.0 - jitter_strength)] = -1

        # Apply jitter with clamping to [-1, 0, +1]
        layer_slice[:, :] = np.clip(layer_slice + jitter, -1, 1).astype(np.int8)

    def __repr__(self) -> str:
        return "LayeredJitter(derived from gamma)"


class LayeredEvolution:
    """Evolution with derived jitter and no gamma decay.

    V15 changes from V14:
    1. NO gamma_decay parameter - gamma accumulates forever
    2. Jitter derived from effective_gamma (position-dependent)
    3. All behavior emerges from the energy budget model

    Each entity has its own field layer (temporal isolation).
    All entities share the gamma field (spatial coupling).
    """

    def __init__(self, grid: MultiLayerGrid, config: SubstrateConfig):
        """Initialize layered evolution.

        Args:
            grid: MultiLayerGrid to evolve
            config: V15 configuration (zero tunable parameters)
        """
        self.grid = grid
        self.config = config
        self.jitter = LayeredJitter(seed=config.random_seed)
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

        # Fixed skip sensitivity (the only remaining constant in V15)
        sensitivity = self.config.skip_sensitivity

        # Skip probability: pull * sensitivity
        # Capped at 0.9 to ensure entity can always eventually act
        skip_prob = min(pull * sensitivity, 0.9)

        return float(skip_prob)

    def _compute_jitter_strength(self, position: tuple) -> float:
        """Compute jitter strength at position from effective gamma.

        Jitter = energy budget leftover after gamma cost.
        jitter_strength = 1 - effective_gamma

        Args:
            position: Entity position (x, y)

        Returns:
            Jitter strength in [0.01, 0.99]
        """
        effective = self.grid.get_effective_gamma()
        x, y = position

        # Clamp to grid bounds
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))

        local_gamma = effective[y, x]

        # Jitter = 1 - gamma_cost
        # Clamp to [0.01, 0.99] for stability
        return max(0.01, min(0.99, 1.0 - local_gamma))

    def evolve_one_tick(self):
        """Execute one tick of evolution.

        Steps:
        1. Create new entity at origin
        2. For each entity: check skip, evolve if acting
        3. Update gamma (NO DECAY in V15 - just add imprints)
        """
        self.tick_count += 1

        # 1. Create new entity at origin (head prepending)
        self.create_entity(self.tick_count)

        # Get effective gamma for this tick (computed once, used for all entities)
        effective_gamma = self.grid.get_effective_gamma()

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
                self._evolve_entity_layer(entity, layer, effective_gamma)

                # Imprint ONCE at entity position (regardless of accumulated skips)
                self._imprint_gamma(entity.position)

        # V15: NO gamma decay!
        # Gamma accumulates forever.
        # We use effective_gamma (relative values) for derived quantities.

    def _evolve_entity_layer(
        self,
        entity: Entity,
        layer: np.ndarray,
        effective_gamma: np.ndarray
    ):
        """Evolve a single entity's layer with derived jitter.

        Applies localized jitter around the pattern center.
        Jitter strength is derived from effective_gamma (not a parameter).

        Args:
            entity: Entity being evolved
            layer: Entity's layer (modified in-place)
            effective_gamma: Current effective gamma field [0, 1]
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

        # Apply jitter with position-dependent strength derived from gamma
        self.jitter.apply_to_layer_with_derived_jitter(
            layer,
            effective_gamma,
            local_region=(y_min, y_max, x_min, x_max)
        )

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

        self.grid.gamma[y, x] += self.config.gamma_imprint

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
                        f"gamma_eff_mean={stats['effective_gamma_mean']:.3f}, "
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

        # Compute jitter variation (from effective gamma)
        effective = self.grid.get_effective_gamma()
        jitter_field = 1.0 - effective
        jitter_mean = float(np.mean(jitter_field))
        jitter_std = float(np.std(jitter_field))

        return {
            "entity_count": len(self.entities),
            "tick_count": self.tick_count,
            "total_energy": combined_stats["total_energy"],
            "nonzero_fraction": combined_stats["nonzero_fraction"],
            "layer_count": combined_stats["layer_count"],
            # Raw gamma (accumulates forever)
            "gamma_sum": gamma_stats["gamma_sum"],
            "gamma_mean": gamma_stats["gamma_mean"],
            "gamma_max": gamma_stats["gamma_max"],
            "gamma_min": gamma_stats["gamma_min"],
            # Effective gamma (normalized to [0, 1])
            "effective_gamma_mean": gamma_stats["effective_gamma_mean"],
            "effective_gamma_max": gamma_stats["effective_gamma_max"],
            # Gradient stats
            "gradient_max": gamma_stats["gradient_max"],
            "gradient_mean": gamma_stats["gradient_mean"],
            # Tick skipping stats
            "total_skips": self.total_skips,
            "total_acts": self.total_acts,
            "skip_rate": skip_rate,
            "avg_time_dilation": avg_dilation,
            # Derived jitter stats
            "jitter_mean": jitter_mean,
            "jitter_std": jitter_std,
        }

    def __repr__(self) -> str:
        stats = self.get_statistics() if self.tick_count > 0 else {}
        skip_rate = stats.get('skip_rate', 0.0)
        jitter_mean = stats.get('jitter_mean', 0.5)
        return (
            f"LayeredEvolution(tick={self.tick_count}, "
            f"entities={len(self.entities)}, "
            f"skip_rate={skip_rate:.2f}, "
            f"jitter_mean={jitter_mean:.2f})"
        )


if __name__ == "__main__":
    from config_v15 import create_config

    print("V15 LayeredEvolution Demo (Zero Parameters)")
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

    # V15-specific: show jitter variation
    print("V15 Derived Jitter:")
    print(f"  Jitter mean: {stats['jitter_mean']:.4f}")
    print(f"  Jitter std: {stats['jitter_std']:.4f}")
    print("  (Jitter = 1 - effective_gamma, derived not tuned)")
    print()

    # Time dilation distribution
    print("Time dilation factors (sample of entities):")
    for entity in evolution.entities[:10]:
        jitter_at_pos = evolution._compute_jitter_strength(entity.position)
        print(f"  Entity {entity.entity_id}: dilation={entity.time_dilation_factor:.2f}, "
              f"jitter={jitter_at_pos:.2f}, "
              f"(acts={entity.total_acts}, skips={entity.total_skips})")
    print()

    # Visualize central region
    print("Combined field (central 30x30):")
    center_x = config.origin[0] - 15
    center_y = config.origin[1] - 15
    print(grid.visualize_combined_ascii(center_x, center_y, 30, 30))
    print()

    print("=" * 70)
