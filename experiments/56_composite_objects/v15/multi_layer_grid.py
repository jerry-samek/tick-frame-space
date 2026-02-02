"""
V15 Multi-Layer Grid - Grid with relative gamma computation.

Key addition from V14:
- get_effective_gamma(): Computes relative gamma (baseline-subtracted, normalized)
  effective_gamma = (gamma - min) / (max - min)

This allows gamma to accumulate forever without decay, while
keeping derived values (like jitter) bounded in [0, 1].

Author: V15 Implementation
Date: 2026-01-31
Based on: V14 multi_layer_grid.py + effective gamma
"""

import numpy as np
from typing import Optional


class MultiLayerGrid:
    """Grid with N layers - one per entity.

    Each entity owns one layer. Layers are isolated from each other.
    The gamma field is shared - all entities contribute to it.

    V15 addition: get_effective_gamma() for relative normalization.
    """

    def __init__(self, width: int, height: int):
        """Initialize multi-layer grid.

        Args:
            width: Grid width in cells
            height: Grid height in cells
        """
        self.width = width
        self.height = height

        # List of 2D arrays, one per entity
        # Each layer has shape (height, width) with dtype int8
        self.layers: list[np.ndarray] = []

        # Shared gamma field (memory) - all entities contribute
        # Shape: (height, width), dtype float64
        # In V15: gamma accumulates forever (no decay)
        self.gamma = np.zeros((height, width), dtype=np.float64)

    def add_layer(self) -> int:
        """Add new layer for new entity.

        Returns:
            Layer index (entity ID)
        """
        layer = np.zeros((self.height, self.width), dtype=np.int8)
        self.layers.append(layer)
        return len(self.layers) - 1

    def get_layer(self, layer_id: int) -> np.ndarray:
        """Get specific entity's field layer.

        Args:
            layer_id: Layer index (entity ID)

        Returns:
            2D numpy array of field values for this layer
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
            2D array of effective gamma values in [0, 1]
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
            2D numpy array summing all layers
        """
        if not self.layers:
            return np.zeros((self.height, self.width), dtype=np.int8)

        # Sum all layers - result can exceed [-1, 1] range
        combined = np.sum(self.layers, axis=0)
        return combined

    def compute_gamma_gradient(self) -> tuple[np.ndarray, np.ndarray]:
        """Compute gradient of gamma field.

        Returns:
            (grad_x, grad_y) - gradient components with periodic boundary
        """
        gamma = self.gamma

        # Central difference with periodic boundary
        grad_x = (np.roll(gamma, -1, axis=1) - np.roll(gamma, 1, axis=1)) / 2.0
        grad_y = (np.roll(gamma, -1, axis=0) - np.roll(gamma, 1, axis=0)) / 2.0

        return grad_x, grad_y

    def compute_gamma_gradient_magnitude(self) -> np.ndarray:
        """Compute magnitude of gamma gradient.

        Returns:
            2D array of gradient magnitudes (pull force at each position)
        """
        grad_x, grad_y = self.compute_gamma_gradient()
        return np.sqrt(grad_x**2 + grad_y**2)

    def get_combined_statistics(self) -> dict:
        """Get statistics across all layers combined.

        Returns:
            Dict with energy, coverage, layer count
        """
        combined = self.compute_combined_field()

        total_energy = int(np.sum(np.abs(combined)))
        nonzero_count = int(np.count_nonzero(combined))
        total_cells = self.width * self.height

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
        total_cells = self.width * self.height

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

    def visualize_combined_ascii(
        self,
        x: int = 0,
        y: int = 0,
        width: Optional[int] = None,
        height: Optional[int] = None
    ) -> str:
        """Create ASCII visualization of combined field.

        Args:
            x, y: Top-left corner
            width, height: Region size (defaults to full grid)

        Returns:
            ASCII art string
        """
        if width is None:
            width = self.width - x
        if height is None:
            height = self.height - y

        combined = self.compute_combined_field()
        region = combined[y:y+height, x:x+width]

        lines = []
        for row in region:
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
            f"MultiLayerGrid({self.width}x{self.height}, "
            f"layers={stats['layer_count']}, "
            f"energy={stats['total_energy']}, "
            f"gamma_range=[{gamma_stats['gamma_min']:.1f}, {gamma_stats['gamma_max']:.1f}])"
        )


if __name__ == "__main__":
    print("V15 MultiLayerGrid Demo")
    print("=" * 70)

    # Create grid
    grid = MultiLayerGrid(20, 20)
    print(f"Created: {grid}")
    print()

    # Add layers
    layer0 = grid.add_layer()
    layer1 = grid.add_layer()
    layer2 = grid.add_layer()
    print(f"Added 3 layers: {layer0}, {layer1}, {layer2}")
    print(f"Grid: {grid}")
    print()

    # Initialize patterns on each layer at origin
    origin = (10, 10)
    grid.get_layer(0)[origin[1], origin[0]] = 1  # Entity 0 at origin
    grid.get_layer(1)[origin[1] + 1, origin[0]] = 1  # Entity 1 nearby
    grid.get_layer(2)[origin[1], origin[0] + 1] = 1  # Entity 2 nearby

    print("Initialized patterns (each at ~origin):")
    for i in range(3):
        stats = grid.get_layer_statistics(i)
        print(f"  Layer {i}: energy={stats['total_energy']}")

    print()
    print("Combined field (20x20):")
    print(grid.visualize_combined_ascii())
    print()

    # Simulate gamma accumulation (no decay in V15!)
    print("Simulating gamma accumulation (no decay):")
    for tick in range(5):
        # Imprint at origin
        grid.gamma[origin[1], origin[0]] += 1.0
        grid.gamma[origin[1] + 1, origin[0]] += 1.0
        grid.gamma[origin[1], origin[0] + 1] += 1.0

    print(f"After 5 ticks of imprinting:")
    gamma_stats = grid.get_gamma_statistics()
    print(f"  Gamma sum: {gamma_stats['gamma_sum']:.1f}")
    print(f"  Gamma range: [{gamma_stats['gamma_min']:.1f}, {gamma_stats['gamma_max']:.1f}]")
    print(f"  Gamma nonzero: {gamma_stats['gamma_nonzero']}")
    print()

    # Test effective gamma
    print("Effective gamma (V15 addition):")
    effective = grid.get_effective_gamma()
    print(f"  Effective at origin: {effective[origin[1], origin[0]]:.3f}")
    print(f"  Effective mean: {gamma_stats['effective_gamma_mean']:.6f}")
    print(f"  Effective max: {gamma_stats['effective_gamma_max']:.3f}")
    print()

    print("Combined statistics:")
    combined_stats = grid.get_combined_statistics()
    for k, v in combined_stats.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 70)
