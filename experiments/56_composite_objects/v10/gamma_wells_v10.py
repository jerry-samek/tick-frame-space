"""
Gamma Well System V10 - Extended to support V10 renormalization history.

Key difference from V8: Supports 'local_gamma' normalization mode
by passing the base gamma field to the history committer.

Author: V10 Renormalization
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
            return self.k
        else:
            return self.k / r_squared


class GammaWellSystemV10:
    """
    Manage multiple gamma wells with support for V10 renormalization.

    The total gamma field is:
        γ_total(x, y) = base_gamma + Σ k_i / r_i² + normalize(history)

    Key difference from V8: The history contribution is normalized,
    and for 'local_gamma' mode, we pass the base gamma to the normalizer.
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
        """Move a well to a new position."""
        well = self.get_well(well_id)
        if well is not None:
            well.center_x = new_x
            well.center_y = new_y
            return True
        return False

    def remove_well(self, well_id: str) -> bool:
        """Remove a well from the system."""
        for i, well in enumerate(self.wells):
            if well.well_id == well_id:
                del self.wells[i]
                return True
        return False

    def compute_base_gamma_field(self) -> np.ndarray:
        """
        Compute gamma field from wells only (no history).

        Returns:
            Base gamma field array (not clamped, for use in normalization)
        """
        width = self.grid.width
        height = self.grid.height

        y_coords, x_coords = np.mgrid[0:height, 0:width]

        gamma_field = np.full((height, width), self.base_gamma, dtype=np.float64)

        for well in self.wells:
            dx = x_coords - well.center_x
            dy = y_coords - well.center_y
            r_squared = dx * dx + dy * dy
            r_squared_safe = np.maximum(r_squared, 1.0)
            contribution = well.k / r_squared_safe
            gamma_field += contribution

        return gamma_field

    def compute_gamma_field(self, history_committer=None):
        """
        Recompute entire gamma field by superimposing all wells plus history layer.

        This updates the grid's gamma values for all cells.

        V10 difference: For 'local_gamma' normalization, we pass the base
        gamma field to the history committer for normalization.

        Args:
            history_committer: Optional GammaHistoryCommitterV10 to add history layer
        """
        # Compute base gamma from wells
        gamma_field = self.compute_base_gamma_field()

        # Add history layer contribution (normalized)
        if history_committer is not None:
            # Check if this is a V10 committer (has normalization_type)
            if hasattr(history_committer, 'normalization_type'):
                # V10 committer - use get_history_layer with gamma_base
                if history_committer.normalization_type == 'local_gamma':
                    history_layer = history_committer.get_history_layer(gamma_base=gamma_field)
                else:
                    history_layer = history_committer.get_history_layer()
            else:
                # V8 committer - simple get_history_layer()
                history_layer = history_committer.get_history_layer()

            gamma_field += history_layer

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
        return f"GammaWellSystemV10(base={self.base_gamma}, wells={len(self.wells)})"


if __name__ == "__main__":
    # Demo
    print("GammaWellSystemV10 Demo")
    print("=" * 60)

    grid = PlanckGrid(100, 100)
    system = GammaWellSystemV10(grid, base_gamma=1.0)

    print(f"Created: {system}")

    target_id = system.add_well(50, 50, k=50.0, well_id="target")
    print(f"Added target well at center: {target_id}")

    # Compute base gamma
    base_gamma = system.compute_base_gamma_field()
    print(f"\nBase gamma at (50, 50): {base_gamma[50, 50]:.3f}")
    print(f"Base gamma at (10, 10): {base_gamma[10, 10]:.3f}")

    # Compute full field
    system.compute_gamma_field()
    print(f"\nGrid gamma at (50, 50): {grid.get_gamma(50, 50):.3f}")
    print(f"Grid gamma at (10, 10): {grid.get_gamma(10, 10):.3f}")

    print("=" * 60)
