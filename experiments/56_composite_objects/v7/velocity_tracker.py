"""
Velocity Tracker - Compute pattern velocities from position history.

Tracks instantaneous and averaged velocities for each pattern.
"""

import math
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class Velocity:
    """Velocity vector with components and derived quantities."""
    vx: float
    vy: float

    @property
    def speed(self) -> float:
        """Magnitude of velocity."""
        return math.sqrt(self.vx * self.vx + self.vy * self.vy)

    @property
    def direction(self) -> float:
        """Direction in radians (-pi to pi)."""
        return math.atan2(self.vy, self.vx)

    def __repr__(self) -> str:
        return f"Velocity(vx={self.vx:.4f}, vy={self.vy:.4f}, speed={self.speed:.4f})"


class VelocityTracker:
    """Track velocities for multiple patterns."""

    def __init__(self, n_patterns: int, window_size: int = 10):
        """
        Initialize velocity tracker.

        Args:
            n_patterns: Number of patterns to track
            window_size: Number of positions to average for smoothed velocity
        """
        self.n_patterns = n_patterns
        self.window_size = window_size

        # Position history per pattern: list of (tick, x, y)
        self.position_history: List[List[Tuple[int, float, float]]] = [
            [] for _ in range(n_patterns)
        ]

        # Current velocities
        self.velocities: List[Optional[Velocity]] = [None] * n_patterns

    def record_position(self, pattern_id: int, x: float, y: float, tick: int):
        """
        Record a position for a pattern.

        Args:
            pattern_id: Pattern index
            x, y: Position coordinates
            tick: Current tick number
        """
        self.position_history[pattern_id].append((tick, x, y))

        # Keep only window_size * 2 positions (for velocity calculation)
        max_history = self.window_size * 2
        if len(self.position_history[pattern_id]) > max_history:
            self.position_history[pattern_id] = self.position_history[pattern_id][-max_history:]

    def compute_instantaneous_velocity(self, pattern_id: int) -> Optional[Velocity]:
        """
        Compute instantaneous velocity from last two positions.

        Args:
            pattern_id: Pattern index

        Returns:
            Velocity or None if not enough history
        """
        history = self.position_history[pattern_id]
        if len(history) < 2:
            return None

        t1, x1, y1 = history[-2]
        t2, x2, y2 = history[-1]

        dt = t2 - t1
        if dt <= 0:
            return None

        vx = (x2 - x1) / dt
        vy = (y2 - y1) / dt

        return Velocity(vx, vy)

    def compute_averaged_velocity(self, pattern_id: int) -> Optional[Velocity]:
        """
        Compute velocity averaged over window.

        Uses linear regression for robustness.

        Args:
            pattern_id: Pattern index

        Returns:
            Averaged velocity or None if not enough history
        """
        history = self.position_history[pattern_id]
        if len(history) < 2:
            return None

        # Use last window_size positions
        recent = history[-self.window_size:] if len(history) >= self.window_size else history

        if len(recent) < 2:
            return None

        # Extract arrays
        ticks = np.array([p[0] for p in recent], dtype=float)
        xs = np.array([p[1] for p in recent], dtype=float)
        ys = np.array([p[2] for p in recent], dtype=float)

        # Linear regression: x = vx * t + b, y = vy * t + b
        # Using least squares
        t_mean = np.mean(ticks)
        x_mean = np.mean(xs)
        y_mean = np.mean(ys)

        t_var = np.sum((ticks - t_mean) ** 2)
        if t_var < 1e-10:
            return Velocity(0.0, 0.0)

        vx = np.sum((ticks - t_mean) * (xs - x_mean)) / t_var
        vy = np.sum((ticks - t_mean) * (ys - y_mean)) / t_var

        return Velocity(float(vx), float(vy))

    def update_all_velocities(self):
        """Update velocities for all patterns using averaged method."""
        for i in range(self.n_patterns):
            self.velocities[i] = self.compute_averaged_velocity(i)

    def get_velocity(self, pattern_id: int) -> Optional[Velocity]:
        """Get current velocity for a pattern."""
        return self.velocities[pattern_id]

    def get_speed_distribution(self) -> List[float]:
        """Get speeds for all patterns with valid velocities."""
        speeds = []
        for v in self.velocities:
            if v is not None:
                speeds.append(v.speed)
        return speeds

    def get_mean_speed(self) -> float:
        """Get mean speed across all patterns."""
        speeds = self.get_speed_distribution()
        return np.mean(speeds) if speeds else 0.0

    def get_speed_std(self) -> float:
        """Get standard deviation of speeds."""
        speeds = self.get_speed_distribution()
        return np.std(speeds) if speeds else 0.0

    def get_velocity_statistics(self) -> dict:
        """Get summary statistics for velocities."""
        speeds = self.get_speed_distribution()
        if not speeds:
            return {
                "mean_speed": 0.0,
                "std_speed": 0.0,
                "max_speed": 0.0,
                "min_speed": 0.0,
                "n_valid": 0,
            }

        return {
            "mean_speed": float(np.mean(speeds)),
            "std_speed": float(np.std(speeds)),
            "max_speed": float(np.max(speeds)),
            "min_speed": float(np.min(speeds)),
            "n_valid": len(speeds),
        }


if __name__ == "__main__":
    # Demo
    print("Velocity Tracker Demo")
    print("=" * 50)

    tracker = VelocityTracker(n_patterns=3, window_size=5)

    # Simulate positions over time
    # Pattern 0: Moving right at 0.1 cells/tick
    # Pattern 1: Moving diagonally
    # Pattern 2: Stationary

    for tick in range(20):
        tracker.record_position(0, 100 + tick * 0.1, 100, tick)
        tracker.record_position(1, 100 + tick * 0.05, 100 + tick * 0.05, tick)
        tracker.record_position(2, 100, 100, tick)

    tracker.update_all_velocities()

    print("\nVelocities:")
    for i in range(3):
        v = tracker.get_velocity(i)
        print(f"  Pattern {i}: {v}")

    print("\nStatistics:")
    stats = tracker.get_velocity_statistics()
    for k, v in stats.items():
        print(f"  {k}: {v}")
