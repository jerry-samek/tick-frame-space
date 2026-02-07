"""
V17 Canvas - Sparse 3D gamma storage.

The canvas is the tick window state - the accumulated paint from all
previous renderings. It uses sparse (dict-based) storage so only
cells with paint are stored.

Ontological principle: The canvas IS the state. No external memory -
the accumulated paint is the only state that persists between ticks.

Key features:
- Sparse storage: Dict[Tuple[int,int,int], float]
- O(1) lookup for any position (returns 0.0 if not painted)
- Gradient computation from sparse neighbors
- Local region sampling for effective_gamma

Author: V17 Implementation
Date: 2026-02-01
"""

import sys
from typing import Dict, Tuple, Optional, Iterator
import numpy as np


Pos3D = Tuple[int, int, int]


class Canvas3D:
    """The tick window state - sparse gamma storage.

    The canvas holds all the "paint" that entities have deposited
    over time. It uses a dict for O(1) access and O(painted_cells)
    memory instead of O(grid^3).

    Conceptually: This is the accumulated state of the universe
    at the current tick. Renderers (entities) see this canvas
    and decide where to paint next.
    """

    # Neighbor offsets for 6-connected gradient computation
    NEIGHBOR_OFFSETS = [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ]

    def __init__(self):
        """Initialize empty canvas."""
        # Sparse storage: only non-zero gamma values
        self.gamma: Dict[Pos3D, float] = {}
        self.tick_count: int = 0

        # Track bounding box for statistics
        self._min_coords: Optional[Pos3D] = None
        self._max_coords: Optional[Pos3D] = None

    # ========================================================================
    # Core Operations
    # ========================================================================

    def get_gamma(self, pos: Pos3D) -> float:
        """Get gamma at position (0.0 if never painted).

        Args:
            pos: (x, y, z) position

        Returns:
            Gamma value at position (0.0 if unpainted)
        """
        return self.gamma.get(pos, 0.0)

    def paint(self, pos: Pos3D, strength: float = 1.0):
        """Add paint to canvas at position.

        Args:
            pos: (x, y, z) position to paint
            strength: Amount of paint to add (default 1.0)
        """
        self.gamma[pos] = self.gamma.get(pos, 0.0) + strength
        self._update_bounds(pos)

    def _update_bounds(self, pos: Pos3D):
        """Update bounding box to include position.

        Args:
            pos: New position to include
        """
        x, y, z = pos
        if self._min_coords is None:
            self._min_coords = pos
            self._max_coords = pos
        else:
            mx, my, mz = self._min_coords
            Mx, My, Mz = self._max_coords
            self._min_coords = (min(mx, x), min(my, y), min(mz, z))
            self._max_coords = (max(Mx, x), max(My, y), max(Mz, z))

    # ========================================================================
    # Gradient Computation
    # ========================================================================

    def get_gradient(self, pos: Pos3D) -> Tuple[float, float, float]:
        """Compute gradient at position from neighboring gamma.

        Uses central difference with sparse neighbors.
        For positions without paint, gradient points toward painted regions.

        Args:
            pos: (x, y, z) position

        Returns:
            (grad_x, grad_y, grad_z) - gradient vector pointing uphill
        """
        x, y, z = pos

        # Central difference for each axis
        grad_x = (self.get_gamma((x + 1, y, z)) - self.get_gamma((x - 1, y, z))) / 2.0
        grad_y = (self.get_gamma((x, y + 1, z)) - self.get_gamma((x, y - 1, z))) / 2.0
        grad_z = (self.get_gamma((x, y, z + 1)) - self.get_gamma((x, y, z - 1))) / 2.0

        return (grad_x, grad_y, grad_z)

    def get_gradient_magnitude(self, pos: Pos3D) -> float:
        """Compute magnitude of gradient at position.

        Args:
            pos: (x, y, z) position

        Returns:
            Gradient magnitude (pull strength)
        """
        gx, gy, gz = self.get_gradient(pos)
        return np.sqrt(gx**2 + gy**2 + gz**2)

    # ========================================================================
    # Local Region Sampling
    # ========================================================================

    def get_local_region(self, center: Pos3D, radius: int) -> Dict[Pos3D, float]:
        """Get gamma values in region around center.

        Returns only painted cells within the cube [-radius, +radius].
        Used for effective_gamma calculation.

        Args:
            center: Center position (x, y, z)
            radius: Radius of cube to sample

        Returns:
            Dict of {position: gamma} for painted cells in region
        """
        cx, cy, cz = center
        region = {}

        # Directly probe positions in the cube (O(radius^3) which is small)
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    pos = (cx + dx, cy + dy, cz + dz)
                    if pos in self.gamma:
                        region[pos] = self.gamma[pos]

        return region

    def get_effective_gamma(self, center: Pos3D, radius: int = 3) -> float:
        """Compute effective gamma at position (normalized local gamma).

        Effective gamma is the local gamma normalized to [0, 1].
        High effective gamma = high memory cost = low jitter.

        Args:
            center: Position to compute effective gamma at
            radius: Radius for local sampling

        Returns:
            Effective gamma in [0, 1]
        """
        local = self.get_local_region(center, radius)

        if not local:
            return 0.0

        values = list(local.values())
        g_min = min(values)
        g_max = max(values)

        # Current position's gamma
        g_here = self.get_gamma(center)

        # Normalize to [0, 1]
        if g_max - g_min < 1e-10:
            return 0.0

        return (g_here - g_min) / (g_max - g_min)

    # ========================================================================
    # Statistics and Memory
    # ========================================================================

    @property
    def painted_cells(self) -> int:
        """Number of cells with paint."""
        return len(self.gamma)

    @property
    def gamma_sum(self) -> float:
        """Total paint on canvas."""
        return sum(self.gamma.values()) if self.gamma else 0.0

    def get_memory_usage_mb(self) -> float:
        """Estimate current memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        # sys.getsizeof for the dict itself plus overhead per entry
        # Each entry: tuple key (3 ints) + float value + dict overhead
        # Approximately 100 bytes per entry
        return (len(self.gamma) * 100) / (1024 * 1024)

    def get_bounds(self) -> Tuple[Pos3D, Pos3D]:
        """Get bounding box of painted region.

        Returns:
            (min_coords, max_coords) or ((0,0,0), (0,0,0)) if empty
        """
        if self._min_coords is None:
            return ((0, 0, 0), (0, 0, 0))
        return (self._min_coords, self._max_coords)

    def get_statistics(self) -> dict:
        """Get canvas statistics.

        Returns:
            Dict with gamma statistics
        """
        if not self.gamma:
            return {
                "painted_cells": 0,
                "gamma_sum": 0.0,
                "gamma_min": 0.0,
                "gamma_max": 0.0,
                "gamma_mean": 0.0,
                "memory_mb": 0.0,
                "bounds": ((0, 0, 0), (0, 0, 0)),
            }

        values = list(self.gamma.values())
        return {
            "painted_cells": len(values),
            "gamma_sum": sum(values),
            "gamma_min": min(values),
            "gamma_max": max(values),
            "gamma_mean": sum(values) / len(values),
            "memory_mb": self.get_memory_usage_mb(),
            "bounds": self.get_bounds(),
        }

    def get_positions(self) -> Iterator[Pos3D]:
        """Iterate over all painted positions.

        Yields:
            (x, y, z) positions with paint
        """
        return iter(self.gamma.keys())

    def get_radial_distribution(self, origin: Pos3D = (0, 0, 0)) -> Dict[int, float]:
        """Get gamma distribution by radial distance from origin.

        Args:
            origin: Center point for radial measurement

        Returns:
            Dict of {radius: total_gamma_at_radius}
        """
        ox, oy, oz = origin
        radial = {}

        for pos, gamma in self.gamma.items():
            px, py, pz = pos
            r = int(np.sqrt((px - ox)**2 + (py - oy)**2 + (pz - oz)**2))
            radial[r] = radial.get(r, 0.0) + gamma

        return radial

    # ========================================================================
    # Visualization
    # ========================================================================

    def get_slice_xy(self, z: int) -> Dict[Tuple[int, int], float]:
        """Get XY slice at given Z as sparse dict.

        Args:
            z: Z coordinate

        Returns:
            Dict of {(x, y): gamma} for this slice
        """
        return {(x, y): g for (x, y, pz), g in self.gamma.items() if pz == z}

    def get_slice_xz(self, y: int) -> Dict[Tuple[int, int], float]:
        """Get XZ slice at given Y as sparse dict.

        Args:
            y: Y coordinate

        Returns:
            Dict of {(x, z): gamma} for this slice
        """
        return {(x, z): g for (x, py, z), g in self.gamma.items() if py == y}

    def get_slice_yz(self, x: int) -> Dict[Tuple[int, int], float]:
        """Get YZ slice at given X as sparse dict.

        Args:
            x: X coordinate

        Returns:
            Dict of {(y, z): gamma} for this slice
        """
        return {(y, z): g for (px, y, z), g in self.gamma.items() if px == x}

    def visualize_slice_ascii(
        self,
        plane: str = "xy",
        index: int = 0,
        size: int = 21
    ) -> str:
        """Create ASCII visualization of a 2D slice.

        Args:
            plane: Which plane to slice ("xy", "xz", or "yz")
            index: Position along the perpendicular axis
            size: Size of visualization (centered on origin)

        Returns:
            ASCII art string
        """
        half = size // 2

        if plane == "xy":
            slice_data = self.get_slice_xy(index)
            title = f"XY slice at z={index}"
            get_key = lambda i, j: (i - half, j - half)
        elif plane == "xz":
            slice_data = self.get_slice_xz(index)
            title = f"XZ slice at y={index}"
            get_key = lambda i, j: (i - half, j - half)
        elif plane == "yz":
            slice_data = self.get_slice_yz(index)
            title = f"YZ slice at x={index}"
            get_key = lambda i, j: (i - half, j - half)
        else:
            raise ValueError(f"Unknown plane: {plane}. Use 'xy', 'xz', or 'yz'.")

        lines = [title, "-" * len(title)]

        for j in range(size):
            line = ""
            for i in range(size):
                key = get_key(i, j)
                gamma = slice_data.get(key, 0.0)
                if gamma > 5:
                    line += "#"
                elif gamma > 2:
                    line += "+"
                elif gamma > 0:
                    line += "."
                else:
                    line += " "
            lines.append(line)

        return "\n".join(lines)

    def __repr__(self) -> str:
        stats = self.get_statistics()
        return (
            f"Canvas3D(painted={stats['painted_cells']}, "
            f"sum={stats['gamma_sum']:.1f}, "
            f"mem={stats['memory_mb']:.2f}MB)"
        )


if __name__ == "__main__":
    print("V17 Canvas3D Demo")
    print("=" * 70)

    # Create canvas and paint some cells
    canvas = Canvas3D()
    print(f"Empty canvas: {canvas}")
    print()

    # Paint a simple pattern
    print("Painting a cross pattern at origin...")
    for i in range(-5, 6):
        canvas.paint((i, 0, 0), 1.0)
        canvas.paint((0, i, 0), 1.0)
        canvas.paint((0, 0, i), 1.0)

    print(f"After painting: {canvas}")
    print()

    # Paint more at center
    for _ in range(10):
        canvas.paint((0, 0, 0), 1.0)

    print(f"After adding center mass: {canvas}")
    print()

    # Test gradient
    print("Gradient tests:")
    for pos in [(0, 0, 0), (1, 0, 0), (5, 0, 0), (10, 0, 0)]:
        grad = canvas.get_gradient(pos)
        mag = canvas.get_gradient_magnitude(pos)
        print(f"  pos={pos}: gradient={grad}, magnitude={mag:.3f}")
    print()

    # Test effective gamma
    print("Effective gamma tests:")
    for pos in [(0, 0, 0), (3, 0, 0), (10, 0, 0)]:
        eff = canvas.get_effective_gamma(pos, radius=3)
        print(f"  pos={pos}: effective_gamma={eff:.3f}")
    print()

    # Statistics
    print("Statistics:")
    stats = canvas.get_statistics()
    for k, v in stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.4f}")
        else:
            print(f"  {k}: {v}")
    print()

    # Radial distribution
    print("Radial distribution:")
    radial = canvas.get_radial_distribution()
    for r in sorted(radial.keys())[:10]:
        print(f"  r={r}: gamma={radial[r]:.1f}")
    print()

    # ASCII visualization
    print("XY slice at z=0:")
    print(canvas.visualize_slice_ascii("xy", 0, 21))
    print()

    print("=" * 70)
