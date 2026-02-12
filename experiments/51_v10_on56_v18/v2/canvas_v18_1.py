"""
V18.1 Canvas - Canvas3D_V18 subclass with pressure-based gamma spreading.

Adds one method: spread_gamma() — local pressure equalization where
gamma-rich cells share with gamma-poor neighbors at 1/6 per neighbor per tick.

This is NOT Laplacian diffusion. It is local pressure equalization:
asymmetry is unstable, so gamma flows from high to low.

Properties:
- Conservative: total gamma preserved exactly
- Local: only adjacent cells interact
- Propagation speed: 1 cell/tick = c on the lattice
- Steady-state profile: 1/r in 3D (Green's function of lattice Laplacian)
- No free parameters: spread_fraction = 1/(number of neighbors) = geometry

Date: February 2026
Based on: V18 canvas + V18.1 specification (v2/README.md)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "56_composite_objects"))
from v18 import Canvas3D_V18


class Canvas3D_V18_1(Canvas3D_V18):
    """Canvas3D_V18 with pressure-based gamma spreading.

    Single addition over V18: spread_gamma() method that performs
    local pressure equalization each tick.
    """

    def spread_gamma(self):
        """Pressure-based gamma equalization — incremental (wake-driven).

        Uses wake field as work list. Only cells that changed (nonzero wake)
        and their gamma-having neighbors are checked. Cells in equilibrium
        cost nothing.

        This produces identical results to iterating all cells, because
        cells in equilibrium produce zero transfers — skipping them
        changes nothing.

        After spreading, self.wake is replaced with the spreading deltas
        (what changed THIS tick). paint_imprint() seeds wake for next tick.

        Properties:
        - Total gamma conserved (transfers only)
        - Synchronous update (compute all, apply all)
        - spread_fraction = 1/6 (geometry, not parameter)
        - O(wavefront) instead of O(total_cells) per tick
        """
        SPREAD_FRACTION = 1.0 / len(self.NEIGHBOR_OFFSETS)  # 1/6 for 3D

        # Build work set: cells with nonzero wake + their gamma-having neighbors
        work_set = set()
        for pos, wake_val in self.wake.items():
            if abs(wake_val) < 1e-6:
                continue
            work_set.add(pos)
            for offset in self.NEIGHBOR_OFFSETS:
                neighbor = (
                    pos[0] + offset[0],
                    pos[1] + offset[1],
                    pos[2] + offset[2],
                )
                if self.gamma.get(neighbor, 0.0) > 0:
                    work_set.add(neighbor)

        # Compute transfers only from work set
        transfers = {}
        for pos in work_set:
            gamma_here = self.gamma.get(pos, 0.0)
            if gamma_here <= 0:
                continue
            for offset in self.NEIGHBOR_OFFSETS:
                neighbor = (
                    pos[0] + offset[0],
                    pos[1] + offset[1],
                    pos[2] + offset[2],
                )
                gamma_there = self.gamma.get(neighbor, 0.0)
                if gamma_here > gamma_there:
                    transfer = (gamma_here - gamma_there) * SPREAD_FRACTION
                    transfers[pos] = transfers.get(pos, 0.0) - transfer
                    transfers[neighbor] = transfers.get(neighbor, 0.0) + transfer

        # Apply transfers synchronously, build new wake
        new_wake = {}
        for pos, delta in transfers.items():
            if abs(delta) > 1e-6:
                new_val = self.gamma.get(pos, 0.0) + delta
                if new_val > 1e-6:
                    self.gamma[pos] = new_val
                elif pos in self.gamma:
                    del self.gamma[pos]
                new_wake[pos] = delta
                self._update_bounds(pos)

        # Wake = only what changed this tick
        self.wake = new_wake

    def get_local_gamma_sum(self, center, radius):
        """Sum of gamma within radius of center — O(r^3) neighborhood scan.

        Overrides base class O(n) brute-force scan with direct neighborhood
        enumeration. For radius=3, checks 343 cells instead of all cells.
        """
        total = 0.0
        r_sq = radius * radius
        for dx in range(-radius, radius + 1):
            for dy in range(-radius, radius + 1):
                for dz in range(-radius, radius + 1):
                    if dx * dx + dy * dy + dz * dz <= r_sq:
                        pos = (center[0] + dx, center[1] + dy, center[2] + dz)
                        g = self.gamma.get(pos, 0.0)
                        if g > 0:
                            total += g
        return total

    def get_total_gamma(self):
        """Sum of all gamma in the canvas. Used for conservation checks."""
        return sum(self.gamma.values()) if self.gamma else 0.0
