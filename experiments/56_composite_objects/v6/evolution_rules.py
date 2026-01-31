"""
Tick-Frame Evolution Rules - Cellular Automaton for Field Evolution

Implements local evolution rules for ternary field values {-1, 0, +1}.
Gamma field modulates pattern stability (high gamma = more persistent).

Author: V6 Grid-Based Implementation
Date: 2026-01-24
Based on: ONTOLOGY.md (patterns as emergent stable structures)
"""

import numpy as np
from planck_grid import PlanckGrid
from planck_jitter import PlanckJitter


class TickFrameEvolution:
    """Cellular automaton rules for tick-to-tick field evolution."""

    def __init__(
        self,
        grid: PlanckGrid,
        jitter: PlanckJitter,
        gamma_modulation_strength: float = 0.5,
        ca_creation_threshold: int = 5,
        creation_sensitivity: float = 0.0,
        field_decay_threshold: float = 0.0,
        field_decay_rate: float = 0.0
    ):
        """
        Initialize evolution rules.

        Args:
            grid: PlanckGrid to evolve
            jitter: PlanckJitter for zero-point fluctuations
            gamma_modulation_strength: How much gamma affects evolution (0.0-1.0)
            ca_creation_threshold: Base threshold for cell creation (default: 5 neighbors)
            creation_sensitivity: How much gamma affects creation threshold (0.0 = no effect)
            field_decay_threshold: Gamma threshold below which decay applies (0.0 = no decay)
            field_decay_rate: Probability of decay per tick in low-gamma regions (0.0-1.0)
        """
        self.grid = grid
        self.jitter = jitter
        self.gamma_strength = gamma_modulation_strength
        self.ca_creation_threshold = ca_creation_threshold
        self.creation_sensitivity = creation_sensitivity
        self.field_decay_threshold = field_decay_threshold
        self.field_decay_rate = field_decay_rate

    def evolve_one_tick(self):
        """
        Execute one tick of evolution:
        1. Apply jitter to all cells
        2. Apply local CA rules (modulated by gamma)
        3. Update grid field
        """
        # 1. Apply Planck-level jitter
        self.jitter.apply_jitter(self.grid)

        # 2. Apply local evolution rules
        new_field = self._apply_local_rules()

        # 3. Update grid
        self.grid.field = new_field

    def _apply_local_rules(self) -> np.ndarray:
        """
        Apply local cellular automaton rules to entire grid.

        Rule design (v1 - experimental):
        - Count neighbors with same sign as center
        - If majority same sign AND gamma > threshold → persist
        - If minority same sign OR gamma < threshold → decay toward zero
        - Gamma bias: High gamma increases survival threshold

        Returns:
            New field state (height x width)
        """
        new_field = self.grid.field.copy()
        height, width = self.grid.field.shape

        # Process interior cells (1-pixel border handled separately)
        for y in range(1, height - 1):
            for x in range(1, width - 1):
                new_field[y, x] = self._evolve_cell(x, y)

        # Handle borders with periodic boundary conditions
        new_field = self._apply_periodic_boundaries(new_field)

        return new_field

    def _evolve_cell(self, x: int, y: int) -> int:
        """
        Evolve single cell based on its 3×3 neighborhood.

        Args:
            x, y: Cell coordinates

        Returns:
            New cell value in {-1, 0, +1}
        """
        cell_value = self.grid.field[y, x]
        gamma = self.grid.get_gamma(x, y)

        # Extract 3×3 neighborhood
        neighbors = self.grid.field[y-1:y+2, x-1:x+2]

        # Count neighbors with same sign (excluding center)
        same_sign_count = 0
        total_neighbors = 0

        for dy in range(3):
            for dx in range(3):
                if dx == 1 and dy == 1:
                    continue  # Skip center cell
                neighbor_val = neighbors[dy, dx]
                total_neighbors += 1
                if neighbor_val == cell_value and cell_value != 0:
                    same_sign_count += 1

        # Survival threshold modulated by gamma
        # gamma ∈ [1.0, 2.0], normalized to [0, 1]
        gamma_normalized = (gamma - 1.0)  # ∈ [0, 1]
        gamma_bias = gamma_normalized * self.gamma_strength

        # Base threshold: need 3+ neighbors (out of 8) with same sign
        base_threshold = 3
        # Gamma reduces threshold (easier to survive in high-gamma regions)
        survival_threshold = base_threshold - (gamma_bias * 2)  # Reduces by up to 2

        # Evolution rules
        if cell_value == 0:
            # Empty cell: Check for spontaneous creation
            # Count positive and negative neighbors
            n_positive = np.sum(neighbors == 1)
            n_negative = np.sum(neighbors == -1)

            # Gamma-dependent creation threshold
            # Low gamma (edges) → higher threshold (harder to create)
            # High gamma (origin) → lower threshold (easier to create)
            creation_threshold = self.ca_creation_threshold + int((2.0 - gamma) * self.creation_sensitivity)

            # If strong majority of one sign, create that sign
            if n_positive >= creation_threshold:
                return 1
            elif n_negative >= creation_threshold:
                return -1
            else:
                return 0

        else:
            # Non-empty cell: Check for survival
            if same_sign_count >= survival_threshold:
                # Sufficient support → persist
                # But check for field decay in low-gamma regions
                if self.field_decay_threshold > 0 and gamma < self.field_decay_threshold:
                    # Outside high-gamma region, probabilistic decay
                    if np.random.random() < self.field_decay_rate:
                        return 0
                return cell_value
            else:
                # Insufficient support → decay toward zero
                return 0

    def _apply_periodic_boundaries(self, field: np.ndarray) -> np.ndarray:
        """
        Apply periodic boundary conditions (toroidal topology).

        For now, simple approach: just keep boundaries as-is.
        Full periodic BC would require wrapping logic.

        Args:
            field: Field array

        Returns:
            Field with boundaries handled
        """
        # TODO: Implement full periodic wrapping if needed
        # For now, just use reflective (keep current values)
        return field

    def evolve_n_ticks(self, n_ticks: int, progress_interval: int = 100) -> list[dict]:
        """
        Evolve grid for n ticks and track statistics.

        Args:
            n_ticks: Number of ticks to evolve
            progress_interval: Report progress every N ticks

        Returns:
            List of statistics dicts (one per progress_interval)
        """
        history = []

        for tick in range(n_ticks):
            self.evolve_one_tick()

            if (tick + 1) % progress_interval == 0:
                stats = self.grid.get_field_statistics()
                stats['tick'] = tick + 1
                history.append(stats)

                print(f"[{tick+1:6d}/{n_ticks:6d}] "
                      f"energy={stats['total_energy']:5d}, "
                      f"nonzero={stats['nonzero_fraction']*100:5.1f}%")

        return history


if __name__ == "__main__":
    # Demo
    print("TickFrameEvolution Demo")
    print("=" * 70)

    # Create grid and jitter
    grid = PlanckGrid(50, 50)
    jitter = PlanckJitter.create_symmetric(jitter_strength=0.25)

    print(f"Grid: {grid}")
    print(f"Jitter: {jitter}")
    print()

    # Initialize with a simple pattern at center
    from pattern_library import PatternLibrary
    library = PatternLibrary(pattern_size=5)

    # Write monopole pattern at center
    monopole = library.get_pattern("monopole")
    grid.write_region(22, 22, monopole)

    # Initialize gamma field (radial 1/r²)
    center_x, center_y = 25, 25
    for y in range(grid.height):
        for x in range(grid.width):
            dx = x - center_x
            dy = y - center_y
            r_squared = dx*dx + dy*dy

            if r_squared < 1:
                gamma_val = 2.0
            else:
                gamma_val = 1.0 + 1.0 / r_squared  # k=1.0

            gamma_clamped = min(2.0, max(1.0, gamma_val))
            grid.set_gamma(x, y, gamma_clamped)

    print("Initialized monopole pattern at center (25, 25)")
    print("Initialized radial gamma field (gamma = 1 + 1/r^2)")
    print()

    stats_initial = grid.get_field_statistics()
    print(f"Initial: energy={stats_initial['total_energy']}, "
          f"nonzero={stats_initial['nonzero_fraction']*100:.1f}%")
    print()

    # Create evolution
    evolution = TickFrameEvolution(grid, jitter, gamma_modulation_strength=0.5)

    # Evolve for 1000 ticks
    print("Evolving for 1000 ticks...")
    print()
    history = evolution.evolve_n_ticks(1000, progress_interval=100)
    print()

    # Final statistics
    stats_final = grid.get_field_statistics()
    print("=" * 70)
    print("FINAL RESULTS")
    print("=" * 70)
    print(f"Initial energy: {stats_initial['total_energy']}")
    print(f"Final energy: {stats_final['total_energy']}")
    print(f"Energy change: {stats_final['total_energy'] - stats_initial['total_energy']}")
    print()
    print(f"Initial nonzero: {stats_initial['nonzero_fraction']*100:.1f}%")
    print(f"Final nonzero: {stats_final['nonzero_fraction']*100:.1f}%")
    print()

    # Visualize final state
    from planck_grid import visualize_grid_ascii
    print("Final grid state (central 30×30 region):")
    print(visualize_grid_ascii(grid, 10, 10, 30, 30))
    print()

    print("=" * 70)
