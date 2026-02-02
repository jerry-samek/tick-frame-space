"""
V16 Expanding Evolution - Zero-parameter evolution with expanding grid.

Extends V15-3D LayeredEvolution with space expansion:
- Grid expands every N ticks
- Entity positions shift when grid expands
- Memory monitoring for safety
- All physics mechanics unchanged from V15-3D

Key features:
1. NO gamma decay - gamma accumulates forever
2. Jitter derived from effective gamma: jitter = 1 - effective_gamma
3. Position-dependent jitter (high gamma = low jitter, low gamma = high jitter)
4. Grid expansion simulates space expansion in tick-frame physics

Physical model:
- Entity receives 1 energy per tick
- Entity pays gamma_cost = effective_gamma to maintain memory/presence
- Entity has jitter_budget = 1 - effective_gamma left for movement
- Skip probability = |gradient| * SKIP_SENSITIVITY
- Space expands every expansion_rate ticks

Author: V16 Implementation
Date: 2026-02-01
Based on: V15-3D layered_evolution.py + expansion mechanics
"""

import numpy as np
from typing import List, Optional, Tuple

from expanding_grid import ExpandingGrid3D
from entity import Entity, create_entity
from config_v16 import SubstrateConfig16


class LayeredJitter3D:
    """Jitter with position-dependent strength derived from gamma in 3D.

    In V16 (same as V15), jitter_strength is NOT a parameter - it's derived from
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


class ExpandingEvolution3D:
    """Evolution with derived jitter, no gamma decay, and expanding grid.

    V16 changes from V15-3D:
    - Grid expands every N ticks
    - Entity positions shift when grid expands
    - Memory monitoring for safety

    Core mechanics (unchanged from V15):
    - NO gamma_decay parameter - gamma accumulates forever
    - Jitter derived from effective_gamma (position-dependent)
    - All behavior emerges from the energy budget model
    """

    def __init__(self, grid: ExpandingGrid3D, config: SubstrateConfig16):
        """Initialize expanding evolution.

        Args:
            grid: ExpandingGrid3D to evolve
            config: V16 configuration (zero tunable parameters)
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

        # Expansion tracking
        self.last_expansion_tick = 0

    def create_entity(self, tick: int) -> Entity:
        """Create new entity at origin with its own layer.

        Args:
            tick: Current tick count

        Returns:
            New Entity instance
        """
        # Add new layer to grid
        layer_id = self.grid.add_layer()

        # Create entity at current origin (center of current grid)
        entity = create_entity(
            tick=tick,
            layer_id=layer_id,
            origin=self.grid.origin
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

    def _shift_all_entity_positions(self, delta: int = 1):
        """Shift all entity positions after grid expansion.

        Args:
            delta: Amount to shift in each dimension
        """
        for entity in self.entities:
            entity.shift_position(delta)

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

        # Fixed skip sensitivity (the only remaining constant in V16)
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

    def evolve_one_tick(self) -> dict:
        """Execute one tick of evolution.

        Steps:
        1. Increment tick count
        2. Check for grid expansion
        3. Create new entity at origin
        4. For each entity: check skip, evolve if acting
        5. Update gamma (NO DECAY in V16 - just add imprints)

        Returns:
            Dict with tick info (expanded, memory_mb, etc.)
        """
        self.tick_count += 1
        self.grid.increment_tick()

        tick_info = {
            "tick": self.tick_count,
            "expanded": False,
            "grid_size": self.grid.current_size,
            "memory_mb": self.grid.get_memory_usage_mb(),
        }

        # Check for grid expansion
        if self.grid.should_expand():
            self.grid.expand()
            self._shift_all_entity_positions(delta=1)
            tick_info["expanded"] = True
            tick_info["grid_size"] = self.grid.current_size
            tick_info["memory_mb"] = self.grid.get_memory_usage_mb()
            self.last_expansion_tick = self.tick_count

        # Memory safety check
        if tick_info["memory_mb"] > self.config.max_memory_mb:
            raise MemoryError(
                f"Memory limit exceeded: {tick_info['memory_mb']:.1f} MB > "
                f"{self.config.max_memory_mb} MB at tick {self.tick_count}"
            )

        # Create new entity at origin (head prepending)
        self.create_entity(self.tick_count)

        # Get effective gamma for this tick (computed once, used for all entities)
        effective_gamma = self.grid.get_effective_gamma()

        # For each entity: check skip probability, evolve if acting
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

        # V16: NO gamma decay!
        # Gamma accumulates forever.
        # We use effective_gamma (relative values) for derived quantities.

        return tick_info

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
            tick_info = self.evolve_one_tick()

            if (tick + 1) % progress_interval == 0:
                stats = self.get_statistics()
                stats['tick'] = tick + 1
                stats['expanded_this_tick'] = tick_info['expanded']
                history.append(stats)

                if verbose:
                    expand_marker = " [EXPANDED]" if tick_info['expanded'] else ""
                    print(
                        f"[{tick+1:6d}/{n_ticks:6d}] "
                        f"grid={stats['grid_size']:3d}^3, "
                        f"entities={stats['entity_count']:4d}, "
                        f"mem={stats['memory_mb']:.1f}MB, "
                        f"gamma_eff={stats['effective_gamma_mean']:.3f}, "
                        f"skip={stats['skip_rate']:.2f}"
                        f"{expand_marker}"
                    )

        return history

    def get_statistics(self) -> dict:
        """Get current simulation statistics.

        Returns:
            Dict with entity count, energy, gamma stats, expansion stats, and skip stats
        """
        combined_stats = self.grid.get_combined_statistics()
        gamma_stats = self.grid.get_gamma_statistics()
        expansion_stats = self.grid.get_expansion_statistics()

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
            # Grid expansion
            "grid_size": self.grid.current_size,
            "expansion_count": expansion_stats["expansion_count"],
            "memory_mb": expansion_stats["memory_usage_mb"],
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
        grid_size = stats.get('grid_size', self.grid.current_size)
        memory_mb = stats.get('memory_mb', 0.0)
        return (
            f"ExpandingEvolution3D(tick={self.tick_count}, "
            f"grid={grid_size}^3, "
            f"entities={len(self.entities)}, "
            f"mem={memory_mb:.1f}MB, "
            f"skip_rate={skip_rate:.2f})"
        )


if __name__ == "__main__":
    from config_v16 import create_config

    print("V16 ExpandingEvolution3D Demo (Zero Parameters + Expanding Grid)")
    print("=" * 70)

    # Create configuration (quick test)
    config = create_config(
        initial_size=15,
        expansion_rate=5,
        max_ticks=50,
        max_memory_mb=500
    )
    print(config.describe())
    print()

    # Create grid and evolution
    grid = ExpandingGrid3D(
        initial_size=config.initial_size,
        expansion_rate=config.expansion_rate
    )
    evolution = ExpandingEvolution3D(grid, config)

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

    # Expansion summary
    print("EXPANSION SUMMARY:")
    print(f"  Initial size: {config.initial_size}^3")
    print(f"  Final size: {stats['grid_size']}^3")
    print(f"  Expansions: {stats['expansion_count']}")
    print(f"  Memory: {stats['memory_mb']:.1f} MB")
    print()

    # Time dilation distribution
    print("Time dilation factors (sample of entities):")
    for entity in evolution.entities[:10]:
        jitter_at_pos = evolution._compute_jitter_strength(entity.position)
        print(f"  Entity {entity.entity_id}: dilation={entity.time_dilation_factor:.2f}, "
              f"jitter={jitter_at_pos:.2f}, pos={entity.position}")
    print()

    # Visualize central slice
    print("XY slice at z=center:")
    print(grid.visualize_slice_ascii("xy", grid.origin[2]))
    print()

    print("=" * 70)
