"""
V15-3D Layered Evolution - Zero-parameter evolution with derived jitter in 3D.

Extends V15 LayeredEvolution to 3D:
- 3D positions: (x, y, z)
- 3D gradient for skip probability
- 3D center of mass calculation
- 3D local region extraction for jitter

Key features (same as V15 2D):
1. NO gamma decay - gamma accumulates forever
2. Jitter derived from effective gamma: jitter = 1 - effective_gamma
3. Position-dependent jitter (high gamma = low jitter, low gamma = high jitter)

Physical model:
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - effective_gamma left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY

Author: V15-3D Implementation
Date: 2026-02-01
Based on: V15 layered_evolution.py + 3D extensions
"""

import numpy as np
from typing import List, Optional, Tuple

from multi_layer_grid_3d import MultiLayerGrid3D
from entity import Entity, create_entity
from config_v15_3d import SubstrateConfig3D


class LayeredJitter3D:
    """Jitter with position-dependent strength derived from gamma in 3D.

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
        local_region: Optional[Tuple[int, int, int, int, int, int]] = None
    ):
        """Apply jitter to a 3D layer with position-dependent strength.

        Jitter strength at each position = 1 - effective_gamma at that position.
        This means:
        - High gamma regions: low jitter (patterns preserved)
        - Low gamma regions: high jitter (more fluctuation)

        Args:
            layer: 3D numpy array (modified in-place)
            effective_gamma: 3D array of effective gamma values [0, 1]
            local_region: Optional (z_min, z_max, y_min, y_max, x_min, x_max) to apply only to region
        """
        if local_region is not None:
            z_min, z_max, y_min, y_max, x_min, x_max = local_region
            layer_slice = layer[z_min:z_max, y_min:y_max, x_min:x_max]
            gamma_slice = effective_gamma[z_min:z_max, y_min:y_max, x_min:x_max]
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
        layer_slice[:, :, :] = np.clip(layer_slice + jitter, -1, 1).astype(np.int8)

    def __repr__(self) -> str:
        return "LayeredJitter3D(derived from gamma)"


class LayeredEvolution3D:
    """Evolution with derived jitter and no gamma decay in 3D.

    V15-3D changes from V15 2D:
    - All arrays are 3D: (depth, height, width) = (z, y, x)
    - Gradient is 3D: (grad_x, grad_y, grad_z)
    - Center of mass is 3D
    - Local regions are 3D cubes

    Core mechanics (unchanged from V15):
    - NO gamma_decay parameter - gamma accumulates forever
    - Jitter derived from effective_gamma (position-dependent)
    - All behavior emerges from the energy budget model
    """

    def __init__(self, grid: MultiLayerGrid3D, config: SubstrateConfig3D):
        """Initialize 3D layered evolution.

        Args:
            grid: MultiLayerGrid3D to evolve
            config: V15-3D configuration (zero tunable parameters)
        """
        self.grid = grid
        self.config = config
        self.jitter = LayeredJitter3D(seed=config.random_seed)
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
        x, y, z = entity.position

        # Clamp to grid bounds
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))
        z = max(0, min(self.grid.depth - 1, z))

        # Single cell at origin = +1
        # Array indexing: [z, y, x]
        layer[z, y, x] = 1

    def _compute_skip_probability(self, position: Tuple[int, int, int]) -> float:
        """Compute probability to skip tick based on 3D gamma gradient.

        Entity in gravitational well (high gradient) has higher skip probability.
        This is the core time dilation mechanism.

        Args:
            position: Entity position (x, y, z)

        Returns:
            Skip probability in [0, 0.9]
        """
        x, y, z = position
        gamma = self.grid.gamma
        d, h, w = gamma.shape

        # Clamp position to grid
        x = max(0, min(w - 1, x))
        y = max(0, min(h - 1, y))
        z = max(0, min(d - 1, z))

        # Compute 3D gradient at position (central difference with wrapping)
        grad_x = (gamma[z, y, (x + 1) % w] - gamma[z, y, (x - 1) % w]) / 2.0
        grad_y = (gamma[z, (y + 1) % h, x] - gamma[z, (y - 1) % h, x]) / 2.0
        grad_z = (gamma[(z + 1) % d, y, x] - gamma[(z - 1) % d, y, x]) / 2.0

        # 3D magnitude
        pull = np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

        # Fixed skip sensitivity (the only remaining constant in V15)
        sensitivity = self.config.skip_sensitivity

        # Skip probability: pull * sensitivity
        # Capped at 0.9 to ensure entity can always eventually act
        skip_prob = min(pull * sensitivity, 0.9)

        return float(skip_prob)

    def _compute_jitter_strength(self, position: Tuple[int, int, int]) -> float:
        """Compute jitter strength at position from effective gamma.

        Jitter = energy budget leftover after gamma cost.
        jitter_strength = 1 - effective_gamma

        Args:
            position: Entity position (x, y, z)

        Returns:
            Jitter strength in [0.01, 0.99]
        """
        effective = self.grid.get_effective_gamma()
        x, y, z = position

        # Clamp to grid bounds
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))
        z = max(0, min(self.grid.depth - 1, z))

        # Array indexing: [z, y, x]
        local_gamma = effective[z, y, x]

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
        """Evolve a single entity's layer with derived jitter in 3D.

        Applies localized jitter around the pattern center.
        Jitter strength is derived from effective_gamma (not a parameter).

        Args:
            entity: Entity being evolved
            layer: Entity's 3D layer (modified in-place)
            effective_gamma: Current effective gamma field [0, 1]
        """
        # Find current pattern center (center of mass of non-zero cells)
        # Array indexing: [z, y, x]
        nonzero_z, nonzero_y, nonzero_x = np.nonzero(layer)

        if len(nonzero_x) == 0:
            # Pattern died - reinitialize at entity position
            x, y, z = entity.position
            x = max(0, min(self.grid.width - 1, x))
            y = max(0, min(self.grid.height - 1, y))
            z = max(0, min(self.grid.depth - 1, z))
            layer[z, y, x] = 1
            return

        # Calculate 3D center of mass
        center_x = np.mean(nonzero_x)
        center_y = np.mean(nonzero_y)
        center_z = np.mean(nonzero_z)

        # Apply jitter only to a local 3D region around center
        # This prevents the pattern from spreading across the entire grid
        # Use smaller radius for 3D (more cells per radius increment)
        radius = 3 + len(nonzero_x) // 50  # Scale radius with pattern size
        radius = min(radius, 10)  # Cap at reasonable size for 3D

        x_min = max(0, int(center_x - radius))
        x_max = min(self.grid.width, int(center_x + radius + 1))
        y_min = max(0, int(center_y - radius))
        y_max = min(self.grid.height, int(center_y + radius + 1))
        z_min = max(0, int(center_z - radius))
        z_max = min(self.grid.depth, int(center_z + radius + 1))

        # Apply jitter with position-dependent strength derived from gamma
        self.jitter.apply_to_layer_with_derived_jitter(
            layer,
            effective_gamma,
            local_region=(z_min, z_max, y_min, y_max, x_min, x_max)
        )

        # Update entity position to new 3D center
        nonzero_z, nonzero_y, nonzero_x = np.nonzero(layer)
        if len(nonzero_x) > 0:
            new_center_x = int(np.mean(nonzero_x))
            new_center_y = int(np.mean(nonzero_y))
            new_center_z = int(np.mean(nonzero_z))
            entity.position = (new_center_x, new_center_y, new_center_z)

    def _imprint_gamma(self, position: Tuple[int, int, int]):
        """Imprint gamma at position.

        Always imprints strength=1.0 (one action = one imprint).
        This maintains energy conservation regardless of skip accumulation.

        Args:
            position: (x, y, z) position to imprint
        """
        x, y, z = position
        x = max(0, min(self.grid.width - 1, x))
        y = max(0, min(self.grid.height - 1, y))
        z = max(0, min(self.grid.depth - 1, z))

        # Array indexing: [z, y, x]
        self.grid.gamma[z, y, x] += self.config.gamma_imprint

    def evolve_n_ticks(
        self,
        n_ticks: int,
        progress_interval: int = 50,
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
            f"LayeredEvolution3D(tick={self.tick_count}, "
            f"entities={len(self.entities)}, "
            f"skip_rate={skip_rate:.2f}, "
            f"jitter_mean={jitter_mean:.2f})"
        )


if __name__ == "__main__":
    from config_v15_3d import create_config

    print("V15-3D LayeredEvolution Demo (Zero Parameters)")
    print("=" * 70)

    # Create configuration (smaller grid for demo)
    config = create_config(grid_size=20)
    print(config.describe())
    print()

    # Create grid and evolution
    grid = MultiLayerGrid3D(config.grid_depth, config.grid_height, config.grid_width)
    evolution = LayeredEvolution3D(grid, config)

    print(f"Created: {evolution}")
    print()

    # Evolve for 50 ticks
    print("Evolving for 50 ticks...")
    print("-" * 70)
    history = evolution.evolve_n_ticks(50, progress_interval=10, verbose=True)
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
    print("V15-3D Derived Jitter:")
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

    # Visualize central slice
    print("XY slice at z=center:")
    print(grid.visualize_slice_ascii("xy", config.origin[2]))
    print()

    print("=" * 70)
