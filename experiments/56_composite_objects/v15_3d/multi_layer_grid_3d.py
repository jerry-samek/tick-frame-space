"""
V15-3D Multi-Layer Grid - 3D grid with relative gamma computation.

Extends V15 MultiLayerGrid to 3D:
- Grid shape: (depth, height, width) = (z, y, x)
- Gamma field: 3D array
- Gradient: 3 components (grad_x, grad_y, grad_z)

Key features (same as V15 2D):
- get_effective_gamma(): Computes relative gamma (baseline-subtracted, normalized)
  effective_gamma = (gamma - min) / (max - min)

This allows gamma to accumulate forever without decay, while
keeping derived values (like jitter) bounded in [0, 1].

Author: V15-3D Implementation
Date: 2026-02-01
Based on: V15 multi_layer_grid.py + 3D extensions
"""

import numpy as np
from typing import Optional, Tuple


class MultiLayerGrid3D:
    """3D Grid with N layers - one per entity.

    Each entity owns one layer. Layers are isolated from each other.
    The gamma field is shared - all entities contribute to it.

    Array indexing: [z, y, x] = [depth, height, width]
    """

    def __init__(self, depth: int, height: int, width: int):
        """Initialize 3D multi-layer grid.

        Args:
            depth: Grid depth in cells (z-axis)
            height: Grid height in cells (y-axis)
            width: Grid width in cells (x-axis)
        """
        self.depth = depth
        self.height = height
        self.width = width

        # List of 3D arrays, one per entity
        # Each layer has shape (depth, height, width) with dtype int8
        self.layers: list[np.ndarray] = []

        # Shared gamma field (memory) - all entities contribute
        # Shape: (depth, height, width), dtype float64
        # In V15: gamma accumulates forever (no decay)
        self.gamma = np.zeros((depth, height, width), dtype=np.float64)

    def add_layer(self) -> int:
        """Add new layer for new entity.

        Returns:
            Layer index (entity ID)
        """
        layer = np.zeros((self.depth, self.height, self.width), dtype=np.int8)
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
            return np.zeros((self.depth, self.height, self.width), dtype=np.int8)

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
        total_cells = self.depth * self.height * self.width

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
        total_cells = self.depth * self.height * self.width

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
            f"MultiLayerGrid3D({self.depth}x{self.height}x{self.width}, "
            f"layers={stats['layer_count']}, "
            f"energy={stats['total_energy']}, "
            f"gamma_range=[{gamma_stats['gamma_min']:.1f}, {gamma_stats['gamma_max']:.1f}])"
        )


if __name__ == "__main__":
    print("V15-3D MultiLayerGrid Demo")
    print("=" * 70)

    # Create 3D grid
    grid = MultiLayerGrid3D(20, 20, 20)
    print(f"Created: {grid}")
    print()

    # Add layers
    layer0 = grid.add_layer()
    layer1 = grid.add_layer()
    layer2 = grid.add_layer()
    print(f"Added 3 layers: {layer0}, {layer1}, {layer2}")
    print(f"Grid: {grid}")
    print()

    # Initialize patterns on each layer at origin (center)
    origin = (10, 10, 10)  # (x, y, z)
    # Array indexing is [z, y, x]
    grid.get_layer(0)[origin[2], origin[1], origin[0]] = 1  # Entity 0 at origin
    grid.get_layer(1)[origin[2], origin[1] + 1, origin[0]] = 1  # Entity 1 nearby
    grid.get_layer(2)[origin[2], origin[1], origin[0] + 1] = 1  # Entity 2 nearby

    print("Initialized patterns (each at ~origin):")
    for i in range(3):
        stats = grid.get_layer_statistics(i)
        print(f"  Layer {i}: energy={stats['total_energy']}")

    print()

    # Simulate gamma accumulation (no decay in V15!)
    print("Simulating gamma accumulation (no decay):")
    for tick in range(5):
        # Imprint at origin area
        grid.gamma[origin[2], origin[1], origin[0]] += 1.0
        grid.gamma[origin[2], origin[1] + 1, origin[0]] += 1.0
        grid.gamma[origin[2], origin[1], origin[0] + 1] += 1.0

    print(f"After 5 ticks of imprinting:")
    gamma_stats = grid.get_gamma_statistics()
    print(f"  Gamma sum: {gamma_stats['gamma_sum']:.1f}")
    print(f"  Gamma range: [{gamma_stats['gamma_min']:.1f}, {gamma_stats['gamma_max']:.1f}]")
    print(f"  Gamma nonzero: {gamma_stats['gamma_nonzero']}")
    print()

    # Test effective gamma
    print("Effective gamma (V15 feature):")
    effective = grid.get_effective_gamma()
    print(f"  Effective at origin: {effective[origin[2], origin[1], origin[0]]:.3f}")
    print(f"  Effective mean: {gamma_stats['effective_gamma_mean']:.6f}")
    print(f"  Effective max: {gamma_stats['effective_gamma_max']:.3f}")
    print()

    # Test 3D gradient
    print("3D Gradient:")
    grad_x, grad_y, grad_z = grid.compute_gamma_gradient()
    print(f"  Gradient shape: {grad_x.shape}")
    print(f"  Gradient max magnitude: {gamma_stats['gradient_max']:.3f}")
    print(f"  Gradient mean magnitude: {gamma_stats['gradient_mean']:.6f}")
    print()

    # Visualize slices
    print("XY slice at z=10 (center):")
    print(grid.visualize_slice_ascii("xy", 10))
    print()

    print("Combined statistics:")
    combined_stats = grid.get_combined_statistics()
    for k, v in combined_stats.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 70)
