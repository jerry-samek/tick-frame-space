"""
Gamma Well System - Multiple moving gamma wells with superposition.

Manages gamma wells that can move and superimpose their effects.
Each well creates a γ(r) = k/r² contribution that is summed with others.

Author: V8 Moving Gamma Wells
Date: 2026-01-30
"""

import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

v6_path = Path(__file__).parent.parent / "v6"
sys.path.insert(0, str(v6_path))

from planck_grid import PlanckGrid


@dataclass
class GammaWell:
    """A single gamma well with position and strength."""
    well_id: str
    center_x: float
    center_y: float
    k: float  # Well strength (positive = attractive/deeper potential)

    def gamma_contribution(self, x: int, y: int) -> float:
        """Calculate gamma contribution at a point from this well."""
        dx = x - self.center_x
        dy = y - self.center_y
        r_squared = dx * dx + dy * dy

        if r_squared < 1.0:
            # At the center, cap the contribution
            return self.k
        else:
            return self.k / r_squared


class GammaWellSystem:
    """
    Manage multiple gamma wells that can move and superimpose.

    The total gamma field is:
        γ_total(x, y) = base_gamma + Σ k_i / r_i²

    where each well i contributes k_i / r_i² based on distance from well center.
    """

    def __init__(self, grid: PlanckGrid, base_gamma: float = 1.0):
        """
        Initialize gamma well system.

        Args:
            grid: The Planck grid to write gamma values to
            base_gamma: Background gamma value (typically 1.0)
        """
        self.grid = grid
        self.base_gamma = base_gamma
        self.wells: List[GammaWell] = []
        self._well_counter = 0

    def add_well(self, center_x: float, center_y: float, k: float, well_id: Optional[str] = None) -> str:
        """
        Add a gamma well at position with strength k.

        Args:
            center_x, center_y: Well center position
            k: Well strength (γ contribution = k/r²)
            well_id: Optional identifier; auto-generated if not provided

        Returns:
            The well's ID
        """
        if well_id is None:
            well_id = f"well_{self._well_counter}"
            self._well_counter += 1

        well = GammaWell(
            well_id=well_id,
            center_x=center_x,
            center_y=center_y,
            k=k
        )
        self.wells.append(well)
        return well_id

    def get_well(self, well_id: str) -> Optional[GammaWell]:
        """Get a well by its ID."""
        for well in self.wells:
            if well.well_id == well_id:
                return well
        return None

    def update_well_position(self, well_id: str, new_x: float, new_y: float) -> bool:
        """
        Move a well to a new position.

        Args:
            well_id: Which well to move
            new_x, new_y: New center position

        Returns:
            True if well was found and updated
        """
        well = self.get_well(well_id)
        if well is not None:
            well.center_x = new_x
            well.center_y = new_y
            return True
        return False

    def remove_well(self, well_id: str) -> bool:
        """
        Remove a well from the system.

        Args:
            well_id: Which well to remove

        Returns:
            True if well was found and removed
        """
        for i, well in enumerate(self.wells):
            if well.well_id == well_id:
                del self.wells[i]
                return True
        return False

    def compute_gamma_at(self, x: int, y: int) -> float:
        """
        Compute total gamma at a single point.

        Args:
            x, y: Grid position

        Returns:
            Total gamma value (clamped to [1.0, 2.0])
        """
        total = self.base_gamma

        for well in self.wells:
            total += well.gamma_contribution(x, y)

        # Clamp to valid gamma range
        return min(2.0, max(1.0, total))

    def compute_gamma_field(self, history_committer=None):
        """
        Recompute entire gamma field by superimposing all wells plus history layer.

        This updates the grid's gamma values for all cells.

        Args:
            history_committer: Optional GammaHistoryCommitter to add history layer
        """
        width = self.grid.width
        height = self.grid.height

        # Create coordinate arrays for vectorized computation
        y_coords, x_coords = np.mgrid[0:height, 0:width]

        # Start with base gamma
        gamma_field = np.full((height, width), self.base_gamma, dtype=np.float64)

        # Add contribution from each well
        for well in self.wells:
            dx = x_coords - well.center_x
            dy = y_coords - well.center_y
            r_squared = dx * dx + dy * dy

            # Avoid division by zero: clamp r_squared to minimum of 1.0
            r_squared_safe = np.maximum(r_squared, 1.0)
            contribution = well.k / r_squared_safe
            gamma_field += contribution

        # Add history layer contribution (additive)
        if history_committer is not None:
            gamma_field += history_committer.get_history_layer()

        # Clamp to valid range [1.0, 2.0]
        gamma_field = np.clip(gamma_field, 1.0, 2.0)

        # Write to grid (convert to uint8)
        gamma_uint8 = ((gamma_field - 1.0) * 255).astype(np.uint8)
        self.grid.gamma[:, :] = gamma_uint8

    def get_well_positions(self) -> List[Tuple[str, float, float, float]]:
        """
        Get current positions and strengths of all wells.

        Returns:
            List of (well_id, x, y, k) tuples
        """
        return [(w.well_id, w.center_x, w.center_y, w.k) for w in self.wells]

    def __repr__(self) -> str:
        return f"GammaWellSystem(base={self.base_gamma}, wells={len(self.wells)})"


if __name__ == "__main__":
    # Demo
    print("GammaWellSystem Demo")
    print("=" * 60)

    # Create grid and well system
    grid = PlanckGrid(100, 100)
    system = GammaWellSystem(grid, base_gamma=1.0)

    print(f"Created: {system}")
    print()

    # Add a central well (like the target cloud)
    target_id = system.add_well(50, 50, k=50.0, well_id="target")
    print(f"Added target well at center: {target_id}")

    # Add a projectile well (starts at edge)
    proj_id = system.add_well(90, 50, k=20.0, well_id="projectile")
    print(f"Added projectile well at edge: {proj_id}")

    # Compute initial field
    system.compute_gamma_field()

    # Sample gamma values
    print()
    print("Gamma values:")
    print(f"  At target center (50, 50): {grid.get_gamma(50, 50):.3f}")
    print(f"  At projectile (90, 50): {grid.get_gamma(90, 50):.3f}")
    print(f"  Between (70, 50): {grid.get_gamma(70, 50):.3f}")
    print(f"  Far away (10, 10): {grid.get_gamma(10, 10):.3f}")

    # Move projectile closer
    print()
    print("Moving projectile to (60, 50)...")
    system.update_well_position("projectile", 60, 50)
    system.compute_gamma_field()

    print("Gamma values after move:")
    print(f"  At target center (50, 50): {grid.get_gamma(50, 50):.3f}")
    print(f"  At projectile (60, 50): {grid.get_gamma(60, 50):.3f}")
    print(f"  Between (55, 50): {grid.get_gamma(55, 50):.3f}")

    print()
    print("Well positions:", system.get_well_positions())
    print("=" * 60)
