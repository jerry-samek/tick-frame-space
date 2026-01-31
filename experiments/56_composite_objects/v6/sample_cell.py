"""
Sample Cell - 5×5 (or 7×7) Block of Planck Cells

A sample cell defines the canvas on which a pattern exists.
It provides extract/apply operations for patterns on the grid.

Author: V6 Grid-Based Implementation
Date: 2026-01-24
Based on: STRUCTURE.md
"""

import numpy as np
from planck_grid import PlanckGrid
from pattern_library import PatternLibrary


class SampleCell:
    """5×5 (or NxN) block of Planck cells forming a pattern canvas."""

    def __init__(self, origin_x: int, origin_y: int, size: int = 5):
        """
        Initialize sample cell.

        Args:
            origin_x, origin_y: Top-left corner in Planck grid coordinates
            size: Sample size (5 for 5×5, 7 for 7×7, etc.)
        """
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.size = size

    @property
    def center_x(self) -> int:
        """Center x-coordinate (Planck grid coords)."""
        return self.origin_x + self.size // 2

    @property
    def center_y(self) -> int:
        """Center y-coordinate (Planck grid coords)."""
        return self.origin_y + self.size // 2

    def extract_pattern(self, grid: PlanckGrid) -> np.ndarray:
        """
        Extract pattern from grid at this sample's location.

        Args:
            grid: PlanckGrid to extract from

        Returns:
            NxN array of field values (copy)
        """
        return grid.extract_region(
            self.origin_x,
            self.origin_y,
            self.size,
            self.size
        )

    def apply_pattern(self, grid: PlanckGrid, pattern: np.ndarray):
        """
        Write pattern to grid at this sample's location.

        Args:
            grid: PlanckGrid to write to
            pattern: NxN array of field values
        """
        grid.write_region(self.origin_x, self.origin_y, pattern)

    def shift(self, dx: int, dy: int) -> 'SampleCell':
        """
        Create new SampleCell shifted by (dx, dy).

        Args:
            dx, dy: Shift in Planck cells

        Returns:
            New SampleCell at shifted position
        """
        return SampleCell(
            self.origin_x + dx,
            self.origin_y + dy,
            self.size
        )

    def contains_point(self, x: int, y: int) -> bool:
        """
        Check if point (x, y) is inside this sample cell.

        Args:
            x, y: Planck grid coordinates

        Returns:
            True if point is inside sample bounds
        """
        return (
            self.origin_x <= x < self.origin_x + self.size and
            self.origin_y <= y < self.origin_y + self.size
        )

    def overlaps(self, other: 'SampleCell') -> bool:
        """
        Check if this sample overlaps with another sample.

        Args:
            other: Another SampleCell

        Returns:
            True if samples overlap
        """
        # No overlap if one is completely to the left/right/above/below the other
        if (self.origin_x + self.size <= other.origin_x or
            other.origin_x + other.size <= self.origin_x or
            self.origin_y + self.size <= other.origin_y or
            other.origin_y + other.size <= self.origin_y):
            return False

        return True

    def get_overlap_region(self, other: 'SampleCell') -> tuple[int, int, int, int] | None:
        """
        Calculate overlapping region with another sample.

        Args:
            other: Another SampleCell

        Returns:
            (x, y, width, height) of overlap, or None if no overlap
        """
        if not self.overlaps(other):
            return None

        x1 = max(self.origin_x, other.origin_x)
        y1 = max(self.origin_y, other.origin_y)
        x2 = min(self.origin_x + self.size, other.origin_x + other.size)
        y2 = min(self.origin_y + self.size, other.origin_y + other.size)

        return (x1, y1, x2 - x1, y2 - y1)

    def distance_to(self, other: 'SampleCell') -> float:
        """
        Calculate distance to another sample (center-to-center).

        Args:
            other: Another SampleCell

        Returns:
            Euclidean distance between centers
        """
        dx = self.center_x - other.center_x
        dy = self.center_y - other.center_y
        return (dx*dx + dy*dy) ** 0.5

    def __repr__(self) -> str:
        return (
            f"SampleCell({self.size}×{self.size}, "
            f"origin=({self.origin_x}, {self.origin_y}), "
            f"center=({self.center_x}, {self.center_y}))"
        )


class PatternInstance:
    """
    A pattern instance on the grid (combines SampleCell + pattern name).

    Represents one "field fragment" in the ontology.
    """

    def __init__(
        self,
        sample: SampleCell,
        pattern_name: str,
        instance_id: str | None = None
    ):
        """
        Initialize pattern instance.

        Args:
            sample: SampleCell defining location
            pattern_name: Name of pattern from PatternLibrary
            instance_id: Optional unique identifier for tracking
        """
        self.sample = sample
        self.pattern_name = pattern_name
        self.instance_id = instance_id or f"pattern_{id(self)}"

    def read_from_grid(self, grid: PlanckGrid, library: PatternLibrary) -> bool:
        """
        Read current state from grid and check if it matches expected pattern.

        Args:
            grid: PlanckGrid to read from
            library: PatternLibrary for pattern matching

        Returns:
            True if pattern still matches, False if degraded/changed
        """
        current = self.sample.extract_pattern(grid)
        detected = library.detect_pattern(current)

        return detected == self.pattern_name

    def write_to_grid(self, grid: PlanckGrid, library: PatternLibrary):
        """
        Write pattern to grid at sample location.

        Args:
            grid: PlanckGrid to write to
            library: PatternLibrary containing pattern
        """
        pattern = library.get_pattern(self.pattern_name)
        if pattern is not None:
            self.sample.apply_pattern(grid, pattern)

    def shift(self, dx: int, dy: int) -> 'PatternInstance':
        """
        Create new PatternInstance shifted by (dx, dy).

        Args:
            dx, dy: Shift in Planck cells

        Returns:
            New PatternInstance at shifted position
        """
        new_sample = self.sample.shift(dx, dy)
        return PatternInstance(
            new_sample,
            self.pattern_name,
            self.instance_id
        )

    def __repr__(self) -> str:
        return (
            f"PatternInstance(id={self.instance_id}, "
            f"pattern={self.pattern_name}, "
            f"center=({self.sample.center_x}, {self.sample.center_y}))"
        )


if __name__ == "__main__":
    # Demo
    print("SampleCell and PatternInstance Demo")
    print("=" * 70)

    # Create grid and library
    grid = PlanckGrid(50, 50)
    library = PatternLibrary(pattern_size=5)

    print(f"Grid: {grid}")
    print(f"Library: {library}")
    print()

    # Create sample cell
    sample1 = SampleCell(10, 10, size=5)
    print(f"Sample 1: {sample1}")
    print()

    # Create pattern instance
    instance1 = PatternInstance(sample1, "monopole", instance_id="monopole_001")
    print(f"Instance 1: {instance1}")
    print()

    # Write pattern to grid
    instance1.write_to_grid(grid, library)
    print("Written monopole pattern to grid at (10, 10)")
    print()

    # Verify pattern
    is_valid = instance1.read_from_grid(grid, library)
    print(f"Pattern validation: {is_valid}")
    print()

    # Visualize
    from planck_grid import visualize_grid_ascii
    print("Grid visualization (5×5 around pattern):")
    print(visualize_grid_ascii(grid, 8, 8, 10, 10))
    print()

    # Create second pattern
    sample2 = SampleCell(20, 20, size=5)
    instance2 = PatternInstance(sample2, "dipole", instance_id="dipole_001")
    instance2.write_to_grid(grid, library)
    print(f"Instance 2: {instance2}")
    print()

    # Check overlap
    print(f"Instances overlap? {sample1.overlaps(sample2)}")
    print(f"Distance between instances: {sample1.distance_to(sample2):.2f} Planck cells")
    print()

    # Test shift
    instance1_shifted = instance1.shift(5, 0)
    print(f"Instance 1 shifted: {instance1_shifted}")
    print(f"Now overlaps with instance 2? {instance1_shifted.sample.overlaps(sample2)}")
    print()

    print("=" * 70)
