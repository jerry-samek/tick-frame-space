"""
V13 Multi-Layer Grid - Grid with N layers, one per entity.

Each entity has its own field layer for temporal isolation.
All entities share a common gamma field for spatial coupling.

Key insight: Layers provide temporal isolation, gamma provides coupling.
- Each layer evolves independently (no interference)
- Gamma accumulates from all layers (shared memory)
- Jitter acts on each layer independently

Author: V13 Implementation
Date: 2026-01-31
Based on: V12d (jitter only) + Prolog head-prepending model
"""

import numpy as np
from typing import Optional


class MultiLayerGrid:
    """Grid with N layers - one per entity.

    Each entity owns one layer. Layers are isolated from each other.
    The gamma field is shared - all entities contribute to it.
    """

    def __init__(self, width: int, height: int, energy_max: float = 15.0):
        """Initialize multi-layer grid.

        Args:
            width: Grid width in cells
            height: Grid height in cells
            energy_max: Maximum energy capacity (for field initialization)
        """
        self.width = width
        self.height = height

        # List of 2D arrays, one per entity
        # Each layer has shape (height, width) with dtype int8
        self.layers: list[np.ndarray] = []

        # Shared gamma field (memory) - all entities contribute
        # Shape: (height, width), dtype float64
        self.gamma = np.zeros((height, width), dtype=np.float64)

        # Time dilation fields (from Experiment 51)
        # Load field: computational load from entities (reaction-diffusion)
        self.load_field = np.zeros((height, width), dtype=np.float64)

        # Energy field: available observer capacity (depletes under load)
        self.energy_field = np.ones((height, width), dtype=np.float64) * energy_max

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
            Dict with gamma min, max, mean, sum
        """
        return {
            "gamma_min": float(np.min(self.gamma)),
            "gamma_max": float(np.max(self.gamma)),
            "gamma_mean": float(np.mean(self.gamma)),
            "gamma_sum": float(np.sum(self.gamma)),
            "gamma_nonzero": int(np.count_nonzero(self.gamma)),
        }

    def get_load_statistics(self) -> dict:
        """Get statistics for the load field (time dilation).

        Returns:
            Dict with load min, max, mean, sum
        """
        return {
            "load_min": float(np.min(self.load_field)),
            "load_max": float(np.max(self.load_field)),
            "load_mean": float(np.mean(self.load_field)),
            "load_sum": float(np.sum(self.load_field)),
        }

    def get_energy_statistics(self) -> dict:
        """Get statistics for the energy field (observer capacity).

        Returns:
            Dict with energy min, max, mean
        """
        return {
            "energy_min": float(np.min(self.energy_field)),
            "energy_max": float(np.max(self.energy_field)),
            "energy_mean": float(np.mean(self.energy_field)),
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
        return (
            f"MultiLayerGrid({self.width}×{self.height}, "
            f"layers={stats['layer_count']}, "
            f"energy={stats['total_energy']})"
        )


if __name__ == "__main__":
    print("MultiLayerGrid Demo")
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

    # Test gamma field
    combined = grid.compute_combined_field()
    presence = np.abs(combined) > 0
    grid.gamma = presence.astype(np.float64) * 1.0
    print("Gamma field (from presence):")
    gamma_stats = grid.get_gamma_statistics()
    print(f"  Gamma sum: {gamma_stats['gamma_sum']:.1f}")
    print(f"  Gamma nonzero: {gamma_stats['gamma_nonzero']}")
    print()

    print("Combined statistics:")
    combined_stats = grid.get_combined_statistics()
    for k, v in combined_stats.items():
        print(f"  {k}: {v}")

    print()
    print("=" * 70)
