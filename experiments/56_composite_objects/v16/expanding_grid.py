"""
V16 Expanding Grid - 3D grid with dynamic expansion.

Extends V15-3D MultiLayerGrid3D with space expansion mechanics:
- Grid grows over time (space expansion)
- Arrays are resized with zero padding
- Entity positions shift to stay at same relative location
- Memory monitoring for safety

Key features:
- get_effective_gamma(): Computes relative gamma (baseline-subtracted, normalized)
- maybe_expand(): Check if grid should expand this tick
- _expand_by_one(): Expand grid by 1 cell in each direction

Author: V16 Implementation
Date: 2026-02-01
Based on: V15-3D multi_layer_grid.py + expansion mechanics
"""

import numpy as np
from typing import Optional, Tuple, List


class ExpandingGrid3D:
    """3D Grid with N layers that expands over time.

    Each entity owns one layer. Layers are isolated from each other.
    The gamma field is shared - all entities contribute to it.

    Array indexing: [z, y, x] = [depth, height, width]

    Expansion: Grid grows by 2 cells per axis (1 on each side) every
    expansion_rate ticks. This simulates space expansion in tick-frame physics.
    """

    def __init__(self, initial_size: int, expansion_rate: int = 5):
        """Initialize 3D expanding grid.

        Args:
            initial_size: Initial grid dimension (cube: initial_size^3)
            expansion_rate: Expand grid every N ticks
        """
        self.initial_size = initial_size
        self.current_size = initial_size
        self.expansion_rate = expansion_rate
        self.tick_count = 0
        self.expansion_count = 0

        # List of 3D arrays, one per entity
        # Each layer has shape (size, size, size) with dtype int8
        self.layers: List[np.ndarray] = []

        # Shared gamma field (memory) - all entities contribute
        # Shape: (size, size, size), dtype float64
        # In V16: gamma accumulates forever (no decay), same as V15
        self.gamma = np.zeros((initial_size, initial_size, initial_size), dtype=np.float64)

    @property
    def depth(self) -> int:
        """Current grid depth (z-axis)."""
        return self.current_size

    @property
    def height(self) -> int:
        """Current grid height (y-axis)."""
        return self.current_size

    @property
    def width(self) -> int:
        """Current grid width (x-axis)."""
        return self.current_size

    @property
    def origin(self) -> Tuple[int, int, int]:
        """Origin always at center of current grid."""
        c = self.current_size // 2
        return (c, c, c)  # (x, y, z)

    def get_memory_usage_mb(self) -> float:
        """Estimate current memory usage in MB.

        Returns:
            Memory usage in megabytes
        """
        # Gamma: float64 = 8 bytes per cell
        gamma_bytes = self.gamma.nbytes

        # Layers: int8 = 1 byte per cell
        layer_bytes = sum(layer.nbytes for layer in self.layers)

        total_bytes = gamma_bytes + layer_bytes
        return total_bytes / (1024 * 1024)

    def should_expand(self) -> bool:
        """Check if grid should expand this tick.

        Returns:
            True if grid should expand
        """
        if self.tick_count == 0:
            return False
        return self.tick_count % self.expansion_rate == 0

    def expand(self) -> bool:
        """Expand grid by 1 cell in each direction (2 total per axis).

        Returns:
            True if expansion occurred
        """
        old_size = self.current_size
        new_size = old_size + 2  # +1 on each side

        # Expand gamma with zero padding
        new_gamma = np.zeros((new_size, new_size, new_size), dtype=np.float64)
        # Copy old gamma to center
        new_gamma[1:-1, 1:-1, 1:-1] = self.gamma
        self.gamma = new_gamma

        # Expand each entity layer
        for i, layer in enumerate(self.layers):
            new_layer = np.zeros((new_size, new_size, new_size), dtype=np.int8)
            new_layer[1:-1, 1:-1, 1:-1] = layer
            self.layers[i] = new_layer

        self.current_size = new_size
        self.expansion_count += 1

        return True

    def increment_tick(self):
        """Increment tick counter (called by evolution)."""
        self.tick_count += 1

    def add_layer(self) -> int:
        """Add new layer for new entity.

        Returns:
            Layer index (entity ID)
        """
        layer = np.zeros((self.current_size, self.current_size, self.current_size), dtype=np.int8)
        self.layers.append(layer)
        return len(self.layers) - 1

    def get_layer(self, layer_id: int) -> np.ndarray:
        """Get specific entity's field layer.

        Args:
            layer_id: Layer index (entity ID)

        Returns:
            3D numpy array of field values for this layer
        """
        if layer_id < 0 or layer_id >= len(self.layers):
            raise IndexError(f"Layer {layer_id} does not exist (have {len(self.layers)} layers)")
        return self.layers[layer_id]

    def get_layer_count(self) -> int:
        """Get number of layers (entities)."""
        return len(self.layers)

    def get_effective_gamma(self) -> np.ndarray:
        """Compute effective gamma (baseline-subtracted, normalized).

        Returns gamma normalized to [0, 1] range:
        effective_gamma = (gamma - min) / (max - min)

        This allows:
        - Gamma to accumulate forever without decay
        - Derived values (jitter) to stay bounded
        - Gradient to be preserved (adding constant doesn't change derivative)
        - Relative structure to be maintained

        Returns:
            3D array of effective gamma values in [0, 1]
        """
        g_min = self.gamma.min()
        g_max = self.gamma.max()

        # Avoid division by zero if gamma is uniform
        if g_max - g_min < 1e-10:
            return np.zeros_like(self.gamma)

        return (self.gamma - g_min) / (g_max - g_min)

    def compute_combined_field(self) -> np.ndarray:
        """Sum all layers for visualization/gamma computation.

        Returns:
            3D numpy array summing all layers
        """
        if not self.layers:
            return np.zeros((self.current_size, self.current_size, self.current_size), dtype=np.int8)

        # Sum all layers - result can exceed [-1, 1] range
        combined = np.sum(self.layers, axis=0)
        return combined

    def compute_gamma_gradient(self) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Compute gradient of gamma field in 3D.

        Returns:
            (grad_x, grad_y, grad_z) - gradient components with periodic boundary

        Note: Array indexing is [z, y, x], so:
            - grad_x uses axis=2 (width)
            - grad_y uses axis=1 (height)
            - grad_z uses axis=0 (depth)
        """
        gamma = self.gamma

        # Central difference with periodic boundary
        # axis=2 is x (width), axis=1 is y (height), axis=0 is z (depth)
        grad_x = (np.roll(gamma, -1, axis=2) - np.roll(gamma, 1, axis=2)) / 2.0
        grad_y = (np.roll(gamma, -1, axis=1) - np.roll(gamma, 1, axis=1)) / 2.0
        grad_z = (np.roll(gamma, -1, axis=0) - np.roll(gamma, 1, axis=0)) / 2.0

        return grad_x, grad_y, grad_z

    def compute_gamma_gradient_magnitude(self) -> np.ndarray:
        """Compute magnitude of 3D gamma gradient.

        Returns:
            3D array of gradient magnitudes (pull force at each position)
        """
        grad_x, grad_y, grad_z = self.compute_gamma_gradient()
        return np.sqrt(grad_x**2 + grad_y**2 + grad_z**2)

    def get_combined_statistics(self) -> dict:
        """Get statistics across all layers combined.

        Returns:
            Dict with energy, coverage, layer count
        """
        combined = self.compute_combined_field()

        total_energy = int(np.sum(np.abs(combined)))
        nonzero_count = int(np.count_nonzero(combined))
        total_cells = self.current_size ** 3

        return {
            "total_energy": total_energy,
            "nonzero_count": nonzero_count,
            "nonzero_fraction": nonzero_count / total_cells if total_cells > 0 else 0.0,
            "layer_count": len(self.layers),
            "total_cells": total_cells,
        }

    def get_layer_statistics(self, layer_id: int) -> dict:
        """Get statistics for a single layer.

        Args:
            layer_id: Layer index

        Returns:
            Dict with energy, coverage for this layer
        """
        layer = self.get_layer(layer_id)

        total_energy = int(np.sum(np.abs(layer)))
        nonzero_count = int(np.count_nonzero(layer))
        total_cells = self.current_size ** 3

        return {
            "layer_id": layer_id,
            "total_energy": total_energy,
            "nonzero_count": nonzero_count,
            "nonzero_fraction": nonzero_count / total_cells if total_cells > 0 else 0.0,
        }

    def get_gamma_statistics(self) -> dict:
        """Get statistics for the gamma field.

        Returns:
            Dict with gamma min, max, mean, sum, effective gamma stats, and gradient stats
        """
        grad_mag = self.compute_gamma_gradient_magnitude()
        effective = self.get_effective_gamma()

        return {
            "gamma_min": float(np.min(self.gamma)),
            "gamma_max": float(np.max(self.gamma)),
            "gamma_mean": float(np.mean(self.gamma)),
            "gamma_sum": float(np.sum(self.gamma)),
            "gamma_nonzero": int(np.count_nonzero(self.gamma)),
            "effective_gamma_mean": float(np.mean(effective)),
            "effective_gamma_max": float(np.max(effective)),
            "gradient_max": float(np.max(grad_mag)),
            "gradient_mean": float(np.mean(grad_mag)),
        }

    def get_expansion_statistics(self) -> dict:
        """Get statistics about grid expansion.

        Returns:
            Dict with expansion metrics
        """
        return {
            "initial_size": self.initial_size,
            "current_size": self.current_size,
            "expansion_count": self.expansion_count,
            "tick_count": self.tick_count,
            "expansion_rate": self.expansion_rate,
            "memory_usage_mb": self.get_memory_usage_mb(),
        }

    def get_slice_xy(self, z: int) -> np.ndarray:
        """Get XY slice at given Z coordinate.

        Args:
            z: Z coordinate (depth index)

        Returns:
            2D array (height, width) at z
        """
        z = max(0, min(self.depth - 1, z))
        return self.compute_combined_field()[z, :, :]

    def get_slice_xz(self, y: int) -> np.ndarray:
        """Get XZ slice at given Y coordinate.

        Args:
            y: Y coordinate (height index)

        Returns:
            2D array (depth, width) at y
        """
        y = max(0, min(self.height - 1, y))
        return self.compute_combined_field()[:, y, :]

    def get_slice_yz(self, x: int) -> np.ndarray:
        """Get YZ slice at given X coordinate.

        Args:
            x: X coordinate (width index)

        Returns:
            2D array (depth, height) at x
        """
        x = max(0, min(self.width - 1, x))
        return self.compute_combined_field()[:, :, x]

    def visualize_slice_ascii(
        self,
        plane: str = "xy",
        index: Optional[int] = None
    ) -> str:
        """Create ASCII visualization of a 2D slice.

        Args:
            plane: Which plane to slice ("xy", "xz", or "yz")
            index: Position along the perpendicular axis (default: center)

        Returns:
            ASCII art string
        """
        if plane == "xy":
            if index is None:
                index = self.depth // 2
            slice_2d = self.get_slice_xy(index)
            title = f"XY slice at z={index}"
        elif plane == "xz":
            if index is None:
                index = self.height // 2
            slice_2d = self.get_slice_xz(index)
            title = f"XZ slice at y={index}"
        elif plane == "yz":
            if index is None:
                index = self.width // 2
            slice_2d = self.get_slice_yz(index)
            title = f"YZ slice at x={index}"
        else:
            raise ValueError(f"Unknown plane: {plane}. Use 'xy', 'xz', or 'yz'.")

        lines = [title, "-" * len(title)]
        for row in slice_2d:
            line = ""
            for cell in row:
                if cell > 0:
                    line += "+" if cell == 1 else "#"  # # for >1
                elif cell < 0:
                    line += "-" if cell == -1 else "="  # = for <-1
                else:
                    line += "."
            lines.append(line)

        return "\n".join(lines)

    def __repr__(self) -> str:
        stats = self.get_combined_statistics()
        gamma_stats = self.get_gamma_statistics()
        return (
            f"ExpandingGrid3D({self.current_size}^3, "
            f"layers={stats['layer_count']}, "
            f"expansions={self.expansion_count}, "
            f"energy={stats['total_energy']}, "
            f"mem={self.get_memory_usage_mb():.1f}MB)"
        )


if __name__ == "__main__":
    print("V16 ExpandingGrid3D Demo")
    print("=" * 70)

    # Create expanding grid
    grid = ExpandingGrid3D(initial_size=10, expansion_rate=3)
    print(f"Created: {grid}")
    print(f"Initial origin: {grid.origin}")
    print()

    # Add layers and initialize patterns
    print("Adding 3 layers...")
    for i in range(3):
        layer_id = grid.add_layer()
        layer = grid.get_layer(layer_id)
        # Initialize at origin
        ox, oy, oz = grid.origin
        layer[oz, oy, ox] = 1
        print(f"  Added layer {layer_id}, set pattern at origin {grid.origin}")

    print(f"Grid: {grid}")
    print()

    # Simulate expansion
    print("Simulating 10 ticks with expansion...")
    for tick in range(1, 11):
        grid.increment_tick()

        if grid.should_expand():
            old_size = grid.current_size
            old_origin = grid.origin
            grid.expand()
            print(f"  Tick {tick}: EXPANDED {old_size}^3 -> {grid.current_size}^3, "
                  f"origin {old_origin} -> {grid.origin}")
        else:
            print(f"  Tick {tick}: size={grid.current_size}^3, origin={grid.origin}")

    print()
    print(f"Final: {grid}")
    print()

    # Expansion statistics
    print("Expansion statistics:")
    exp_stats = grid.get_expansion_statistics()
    for k, v in exp_stats.items():
        if isinstance(v, float):
            print(f"  {k}: {v:.2f}")
        else:
            print(f"  {k}: {v}")

    print()
    print("=" * 70)
