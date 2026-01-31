"""
Planck Cell Grid - Discrete 2D Grid for Tick-Frame Physics

Each cell holds a ternary field value {-1, 0, +1}.
Gamma field values stored separately as uint8 (0-255).

Author: V6 Grid-Based Implementation
Date: 2026-01-24
Based on: ONTOLOGY.md and STRUCTURE.md
"""

import numpy as np
from typing import Tuple


class PlanckGrid:
    """2D grid of discrete Planck cells with ternary field states."""

    def __init__(self, width: int, height: int):
        """
        Initialize Planck cell grid.

        Args:
            width: Grid width in Planck cells
            height: Grid height in Planck cells
        """
        self.width = width
        self.height = height

        # Field state: {-1, 0, +1} per cell
        # Shape: (height, width)
        # dtype: int8 (-128 to 127, but we only use -1, 0, +1)
        self.field = np.zeros((height, width), dtype=np.int8)

        # Gamma field: modulator for pattern stability
        # Shape: (height, width)
        # dtype: uint8 (0-255), represents gamma in [1.0, 2.0]
        #   gamma_actual = 1.0 + (gamma_uint8 / 255.0)
        self.gamma = np.zeros((height, width), dtype=np.uint8)

    def get_cell(self, x: int, y: int) -> int:
        """Get field value at cell (x, y)."""
        return int(self.field[y, x])

    def set_cell(self, x: int, y: int, value: int):
        """
        Set field value at cell (x, y).

        Args:
            value: Must be in {-1, 0, +1}
        """
        if value not in (-1, 0, 1):
            raise ValueError(f"Field value must be -1, 0, or +1, got {value}")
        self.field[y, x] = value

    def get_gamma(self, x: int, y: int) -> float:
        """
        Get gamma value at cell (x, y).

        Returns:
            float in range [1.0, 2.0]
        """
        gamma_uint8 = self.gamma[y, x]
        return 1.0 + (gamma_uint8 / 255.0)

    def set_gamma(self, x: int, y: int, gamma_value: float):
        """
        Set gamma value at cell (x, y).

        Args:
            gamma_value: float in range [1.0, 2.0]
        """
        if not (1.0 <= gamma_value <= 2.0):
            raise ValueError(f"Gamma must be in [1.0, 2.0], got {gamma_value}")

        # Convert to uint8
        gamma_uint8 = int((gamma_value - 1.0) * 255)
        self.gamma[y, x] = gamma_uint8

    def extract_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """
        Extract rectangular region from grid.

        Args:
            x, y: Top-left corner
            width, height: Region size

        Returns:
            Copy of field values in region (shape: height × width)
        """
        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise ValueError(f"Region ({x}, {y}, {width}, {height}) out of bounds")

        return self.field[y:y+height, x:x+width].copy()

    def write_region(self, x: int, y: int, region: np.ndarray):
        """
        Write rectangular region to grid.

        Args:
            x, y: Top-left corner
            region: 2D array of field values
        """
        height, width = region.shape

        if x < 0 or y < 0 or x + width > self.width or y + height > self.height:
            raise ValueError(f"Region ({x}, {y}, {width}, {height}) out of bounds")

        # Validate all values are in {-1, 0, +1}
        if not np.all(np.isin(region, [-1, 0, 1])):
            raise ValueError("Region contains values outside {-1, 0, +1}")

        self.field[y:y+height, x:x+width] = region

    def clear(self):
        """Set all field values to 0."""
        self.field.fill(0)

    def count_nonzero(self) -> int:
        """Count number of cells with non-zero field values."""
        return int(np.count_nonzero(self.field))

    def total_energy(self) -> int:
        """
        Calculate total field energy (sum of absolute values).

        Returns:
            Sum of |field_value| over all cells
        """
        return int(np.sum(np.abs(self.field)))

    def get_field_statistics(self) -> dict:
        """
        Get statistical summary of field state.

        Returns:
            Dict with counts of -1, 0, +1 cells and energy
        """
        unique, counts = np.unique(self.field, return_counts=True)
        count_map = dict(zip(unique, counts))

        return {
            "n_negative": count_map.get(-1, 0),
            "n_zero": count_map.get(0, 0),
            "n_positive": count_map.get(1, 0),
            "total_cells": self.width * self.height,
            "total_energy": self.total_energy(),
            "nonzero_fraction": self.count_nonzero() / (self.width * self.height),
        }

    def __repr__(self) -> str:
        stats = self.get_field_statistics()
        return (
            f"PlanckGrid({self.width}×{self.height}, "
            f"nonzero={stats['nonzero_fraction']:.1%}, "
            f"energy={stats['total_energy']})"
        )


def visualize_grid_ascii(grid: PlanckGrid, x: int = 0, y: int = 0, width: int = 20, height: int = 20) -> str:
    """
    Create ASCII visualization of grid region.

    Args:
        grid: PlanckGrid to visualize
        x, y: Top-left corner of region
        width, height: Region size

    Returns:
        ASCII art string with '+' for +1, '-' for -1, '.' for 0
    """
    region = grid.extract_region(x, y, width, height)

    lines = []
    for row in region:
        line = ""
        for cell in row:
            if cell == 1:
                line += "+"
            elif cell == -1:
                line += "-"
            else:
                line += "."
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    print("PlanckGrid Demo")
    print("=" * 60)

    # Create small grid
    grid = PlanckGrid(20, 20)
    print(f"Created: {grid}")
    print()

    # Set some cells
    grid.set_cell(10, 10, 1)
    grid.set_cell(10, 11, 1)
    grid.set_cell(10, 12, 1)
    grid.set_cell(9, 11, -1)
    grid.set_cell(11, 11, -1)

    print("After setting some cells:")
    print(visualize_grid_ascii(grid, 5, 5, 15, 15))
    print()
    print(f"Stats: {grid.get_field_statistics()}")
    print()

    # Test region operations
    pattern = np.array([
        [0, 1, 0],
        [1, 1, 1],
        [0, 1, 0],
    ], dtype=np.int8)

    grid.write_region(5, 5, pattern)
    print("After writing 3×3 pattern at (5, 5):")
    print(visualize_grid_ascii(grid, 0, 0, 20, 20))
    print()

    # Test gamma field
    grid.set_gamma(10, 10, 1.5)
    grid.set_gamma(10, 11, 1.8)
    print(f"Gamma at (10, 10): {grid.get_gamma(10, 10):.3f}")
    print(f"Gamma at (10, 11): {grid.get_gamma(10, 11):.3f}")
    print()

    print("=" * 60)
