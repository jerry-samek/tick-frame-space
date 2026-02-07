"""
V18 Canvas - Unified gamma field with wake tracking.

Stores:
- gamma[pos] = accumulated gamma at position
- wake[pos] = ∂gamma/∂t (time derivative of gamma)
- process_paint[process_id] = set of positions painted by this process

Key difference from V17:
- V17: Canvas stores only paint, renderer state is separate
- V18: Canvas + processes together form complete state, wake is explicit

Author: V18 Implementation
Date: 2026-02-04
Based on: V17 Canvas3D, RAW-083 Unified Imprint Principle
"""

import sys
from typing import Dict, Tuple, Optional, Set, Iterator
import numpy as np


Pos3D = Tuple[int, int, int]


class Canvas3D_V18:
    """Unified gamma field with wake (∂gamma/∂t) tracking.

    Conceptually:
    - gamma[pos] = amount of "paint" (presence/imprint) at pos
    - wake[pos] = rate of change ∂gamma/∂t at pos
    - process_paint[process_id] = cells painted by this process

    The canvas maintains the complete state visible to all processes.
    Each process reads from canvas, computes state transition, paints back.
    """

    # 6-connected neighbors for gradient computation
    NEIGHBOR_OFFSETS = [
        (1, 0, 0), (-1, 0, 0),
        (0, 1, 0), (0, -1, 0),
        (0, 0, 1), (0, 0, -1),
    ]

    def __init__(self):
        """Initialize empty canvas."""
        # Sparse storage: only non-zero values
        self.gamma: Dict[Pos3D, float] = {}
        self.wake: Dict[Pos3D, float] = {}  # NEW: time derivative

        # Track which process painted which cells
        # Used for wake attribution and multi-process physics
        self.process_paint: Dict[int, Set[Pos3D]] = {}

        self.tick_count: int = 0

        # Bounding box for statistics
        self._min_coords: Optional[Pos3D] = None
        self._max_coords: Optional[Pos3D] = None

    # ========================================================================
    # Core Operations
    # ========================================================================

    def get_gamma(self, pos: Pos3D) -> float:
        """Get gamma (paint) at position.

        Args:
            pos: (x, y, z) position

        Returns:
            Gamma value (0.0 if never painted)
        """
        return self.gamma.get(pos, 0.0)

    def get_wake(self, pos: Pos3D) -> float:
        """Get wake (∂gamma/∂t) at position.

        Args:
            pos: (x, y, z) position

        Returns:
            Wake value (0.0 if not changing)
        """
        return self.wake.get(pos, 0.0)

    def paint_imprint(
        self,
        process_id: int,
        profile: Dict[Pos3D, float],
        center: Pos3D
    ):
        """Paint unified imprint from a process.

        Args:
            process_id: ID of painting process
            profile: {relative_pos: strength} dict relative to center
            center: (x, y, z) center position for imprint
        """
        # Track which process paints where
        if process_id not in self.process_paint:
            self.process_paint[process_id] = set()

        # Paint each cell in profile
        for rel_pos, strength in profile.items():
            pos = (
                center[0] + rel_pos[0],
                center[1] + rel_pos[1],
                center[2] + rel_pos[2],
            )

            old_gamma = self.gamma.get(pos, 0.0)
            new_gamma = old_gamma + strength

            self.gamma[pos] = new_gamma
            self.process_paint[process_id].add(pos)

            # Update bounding box
            self._update_bounds(pos)

            # Wake is the derivative: ∂gamma/∂t = new_gamma - old_gamma
            # (over one tick, so Δt=1)
            delta_gamma = new_gamma - old_gamma
            self.wake[pos] = self.wake.get(pos, 0.0) + delta_gamma

    def get_gradient(self, pos: Pos3D) -> Tuple[float, float, float]:
        """Compute gradient of gamma field at position.

        Uses 6-connected neighbors (Manhattan distance 1).

        Args:
            pos: (x, y, z) position

        Returns:
            (gx, gy, gz) - gradient components
        """
        gx = (self.get_gamma((pos[0] + 1, pos[1], pos[2])) -
              self.get_gamma((pos[0] - 1, pos[1], pos[2]))) / 2.0

        gy = (self.get_gamma((pos[0], pos[1] + 1, pos[2])) -
              self.get_gamma((pos[0], pos[1] - 1, pos[2]))) / 2.0

        gz = (self.get_gamma((pos[0], pos[1], pos[2] + 1)) -
              self.get_gamma((pos[0], pos[1], pos[2] - 1))) / 2.0

        return (gx, gy, gz)

    def get_wake_gradient(self, pos: Pos3D) -> Tuple[float, float, float]:
        """Compute gradient of wake field (∂²gamma/∂t∂x) at position.

        This is the "pressure" gradient - how fast wake changes spatially.
        Important for expansion resistance and quantum pressure.

        Args:
            pos: (x, y, z) position

        Returns:
            (gx, gy, gz) - wake gradient components
        """
        gx = (self.get_wake((pos[0] + 1, pos[1], pos[2])) -
              self.get_wake((pos[0] - 1, pos[1], pos[2]))) / 2.0

        gy = (self.get_wake((pos[0], pos[1] + 1, pos[2])) -
              self.get_wake((pos[0], pos[1] - 1, pos[2]))) / 2.0

        gz = (self.get_wake((pos[0], pos[1], pos[2] + 1)) -
              self.get_wake((pos[0], pos[1], pos[2] - 1))) / 2.0

        return (gx, gy, gz)

    def get_local_gamma_sum(self, center: Pos3D, radius: int) -> float:
        """Sum of gamma within radius of center (for local energy budget).

        Args:
            center: (x, y, z) center
            radius: search radius

        Returns:
            Sum of gamma in region
        """
        total = 0.0
        for pos, gamma_val in self.gamma.items():
            dx = pos[0] - center[0]
            dy = pos[1] - center[1]
            dz = pos[2] - center[2]
            dist_sq = dx*dx + dy*dy + dz*dz
            if dist_sq <= radius * radius:
                total += gamma_val
        return total

    def get_effective_gamma(self, center: Pos3D, local_radius: int = 3) -> float:
        """Normalized local gamma (cost for maintaining imprint).

        This is the "resistance" a process experiences from expansion.
        Higher local gamma = higher cost to maintain presence.

        Args:
            center: (x, y, z) center position
            local_radius: radius for local sampling

        Returns:
            Effective gamma (normalized, 0-1 range)
        """
        local_sum = self.get_local_gamma_sum(center, local_radius)
        # Normalize: assume 100.0 local gamma = "full resistance"
        return min(1.0, local_sum / 100.0)

    def clear_process_paint(self, process_id: int):
        """Remove a process's paint records.

        Note: Does NOT remove gamma from canvas. Gamma persists.
        This just clears tracking of which process painted where.

        Args:
            process_id: ID of process to clear
        """
        if process_id in self.process_paint:
            del self.process_paint[process_id]

    def decay_wake(self, decay_rate: float = 0.1):
        """Gradually decay wake field (dissipation).

        Args:
            decay_rate: fraction of wake to decay per tick (0.1 = 10%)
        """
        for pos in list(self.wake.keys()):
            self.wake[pos] *= (1.0 - decay_rate)
            if abs(self.wake[pos]) < 1e-6:
                del self.wake[pos]

    def get_radial_distribution(self) -> Dict[int, float]:
        """Get gamma distribution by radial shell.

        Returns:
            {radius: total_gamma_in_shell}
        """
        distribution = {}
        for pos, gamma_val in self.gamma.items():
            r = int(np.sqrt(pos[0]**2 + pos[1]**2 + pos[2]**2))
            distribution[r] = distribution.get(r, 0.0) + gamma_val
        return distribution

    def get_statistics(self) -> Dict[str, any]:
        """Get canvas statistics for logging.

        Returns:
            Dict with painted_cells, total_gamma, total_wake, etc.
        """
        painted_cells = len(self.gamma)
        total_gamma = sum(self.gamma.values())
        total_wake = sum(abs(w) for w in self.wake.values())

        # Memory estimate
        memory_bytes = (
            painted_cells * 40 +  # Dict overhead per entry
            len(self.wake) * 40 +
            sum(len(cells) for cells in self.process_paint.values()) * 16
        )
        memory_mb = memory_bytes / (1024 * 1024)

        # Radial stats
        if self.gamma:
            positions = np.array(list(self.gamma.keys()))
            radii = np.sqrt(np.sum(positions**2, axis=1))
            r_mean = float(np.mean(radii))
            r_max = float(np.max(radii))
        else:
            r_mean = 0.0
            r_max = 0.0

        return {
            'painted_cells': painted_cells,
            'total_gamma': total_gamma,
            'total_wake': total_wake,
            'memory_mb': memory_mb,
            'r_mean': r_mean,
            'r_max': r_max,
        }

    # ========================================================================
    # Private Helpers
    # ========================================================================

    def _update_bounds(self, pos: Pos3D):
        """Update bounding box."""
        if self._min_coords is None:
            self._min_coords = pos
            self._max_coords = pos
        else:
            self._min_coords = tuple(min(a, b) for a, b in zip(self._min_coords, pos))
            self._max_coords = tuple(max(a, b) for a, b in zip(self._max_coords, pos))
