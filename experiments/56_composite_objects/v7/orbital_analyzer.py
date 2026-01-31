"""
Orbital Analyzer - Detect and characterize orbital motion around gamma center.

Computes angular position, angular velocity, and orbital parameters.
"""

import math
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class OrbitalState:
    """Orbital state for a single pattern."""
    theta: float  # Angular position (radians, -pi to pi)
    r: float  # Radial distance from center
    omega: float  # Angular velocity (rad/tick)
    vr: float  # Radial velocity (towards/away from center)

    @property
    def period(self) -> float:
        """Orbital period in ticks (inf if not rotating)."""
        if abs(self.omega) < 1e-10:
            return float('inf')
        return 2 * math.pi / abs(self.omega)

    @property
    def is_prograde(self) -> bool:
        """True if rotating counter-clockwise (positive omega)."""
        return self.omega > 0


class OrbitalAnalyzer:
    """Analyze orbital motion for multiple patterns."""

    def __init__(self, n_patterns: int, center: Tuple[float, float], window_size: int = 50):
        """
        Initialize orbital analyzer.

        Args:
            n_patterns: Number of patterns to track
            center: (x, y) center of orbital system (gamma center)
            window_size: Window for averaging angular velocity
        """
        self.n_patterns = n_patterns
        self.center = center
        self.window_size = window_size

        # History: (tick, theta, r) per pattern
        self.history: List[List[Tuple[int, float, float]]] = [
            [] for _ in range(n_patterns)
        ]

        # Current orbital states
        self.states: List[Optional[OrbitalState]] = [None] * n_patterns

    def record_position(self, pattern_id: int, x: float, y: float, tick: int):
        """
        Record position and update angular state.

        Args:
            pattern_id: Pattern index
            x, y: Position coordinates
            tick: Current tick number
        """
        dx = x - self.center[0]
        dy = y - self.center[1]

        r = math.sqrt(dx * dx + dy * dy)
        theta = math.atan2(dy, dx)

        self.history[pattern_id].append((tick, theta, r))

        # Trim history
        if len(self.history[pattern_id]) > self.window_size * 2:
            self.history[pattern_id] = self.history[pattern_id][-self.window_size * 2:]

    def _unwrap_angle(self, angles: List[float]) -> np.ndarray:
        """
        Unwrap angles to handle -pi/pi wraparound.

        Args:
            angles: List of angles

        Returns:
            Unwrapped angles (can go beyond -pi, pi)
        """
        if len(angles) == 0:
            return np.array([])

        unwrapped = [angles[0]]
        for i in range(1, len(angles)):
            diff = angles[i] - angles[i-1]

            # Handle wraparound
            if diff > math.pi:
                diff -= 2 * math.pi
            elif diff < -math.pi:
                diff += 2 * math.pi

            unwrapped.append(unwrapped[-1] + diff)

        return np.array(unwrapped)

    def compute_angular_velocity(self, pattern_id: int) -> Optional[float]:
        """
        Compute averaged angular velocity for a pattern.

        Uses linear regression on unwrapped angle.

        Args:
            pattern_id: Pattern index

        Returns:
            Angular velocity (rad/tick) or None
        """
        hist = self.history[pattern_id]
        if len(hist) < 2:
            return None

        # Use last window_size points
        recent = hist[-self.window_size:] if len(hist) >= self.window_size else hist

        ticks = np.array([h[0] for h in recent], dtype=float)
        thetas = [h[1] for h in recent]

        # Unwrap angles
        unwrapped = self._unwrap_angle(thetas)

        if len(unwrapped) < 2:
            return None

        # Linear regression: theta = omega * t + b
        t_mean = np.mean(ticks)
        theta_mean = np.mean(unwrapped)

        t_var = np.sum((ticks - t_mean) ** 2)
        if t_var < 1e-10:
            return 0.0

        omega = np.sum((ticks - t_mean) * (unwrapped - theta_mean)) / t_var

        return float(omega)

    def compute_radial_velocity(self, pattern_id: int) -> Optional[float]:
        """
        Compute radial velocity (dr/dt) for a pattern.

        Args:
            pattern_id: Pattern index

        Returns:
            Radial velocity or None
        """
        hist = self.history[pattern_id]
        if len(hist) < 2:
            return None

        # Simple: (r_final - r_initial) / dt
        t1, _, r1 = hist[-2]
        t2, _, r2 = hist[-1]

        dt = t2 - t1
        if dt <= 0:
            return 0.0

        return (r2 - r1) / dt

    def update_state(self, pattern_id: int):
        """Update orbital state for a pattern."""
        hist = self.history[pattern_id]
        if not hist:
            self.states[pattern_id] = None
            return

        # Current position
        _, theta, r = hist[-1]

        # Angular and radial velocities
        omega = self.compute_angular_velocity(pattern_id)
        vr = self.compute_radial_velocity(pattern_id)

        if omega is None:
            omega = 0.0
        if vr is None:
            vr = 0.0

        self.states[pattern_id] = OrbitalState(
            theta=theta,
            r=r,
            omega=omega,
            vr=vr
        )

    def update_all_states(self):
        """Update orbital states for all patterns."""
        for i in range(self.n_patterns):
            self.update_state(i)

    def get_state(self, pattern_id: int) -> Optional[OrbitalState]:
        """Get orbital state for a pattern."""
        return self.states[pattern_id]

    def get_omega_distribution(self) -> List[float]:
        """Get angular velocities for all patterns with valid states."""
        omegas = []
        for state in self.states:
            if state is not None:
                omegas.append(state.omega)
        return omegas

    def get_rotation_coherence(self) -> float:
        """
        Measure coherence of rotation direction.

        Returns:
            Value in [-1, 1]:
            +1 = all rotating same direction (prograde)
            -1 = all rotating same direction (retrograde)
            0 = mixed or no rotation
        """
        omegas = self.get_omega_distribution()
        if not omegas:
            return 0.0

        # Fraction with positive omega
        n_prograde = sum(1 for o in omegas if o > 0)
        n_retrograde = sum(1 for o in omegas if o < 0)
        n_total = len(omegas)

        if n_total == 0:
            return 0.0

        return (n_prograde - n_retrograde) / n_total

    def get_mean_orbital_period(self) -> float:
        """Get mean orbital period across patterns with significant rotation."""
        periods = []
        for state in self.states:
            if state is not None and abs(state.omega) > 1e-6:
                periods.append(state.period)

        if not periods:
            return float('inf')

        return float(np.mean(periods))

    def get_omega_vs_radius(self) -> Tuple[np.ndarray, np.ndarray]:
        """
        Get angular velocity vs radius relationship.

        Returns:
            (radii, omegas) arrays for patterns with valid states
        """
        radii = []
        omegas = []

        for state in self.states:
            if state is not None:
                radii.append(state.r)
                omegas.append(state.omega)

        return np.array(radii), np.array(omegas)

    def fit_omega_r_power_law(self) -> Tuple[float, float, float]:
        """
        Fit omega(r) to power law: omega = A * r^beta

        Keplerian: beta = -1.5
        Rigid body: beta = 0

        Returns:
            (beta, A, r_squared)
        """
        radii, omegas = self.get_omega_vs_radius()

        if len(radii) < 3:
            return 0.0, 0.0, 0.0

        # Filter valid points (positive r, non-zero omega)
        valid = (radii > 1.0) & (np.abs(omegas) > 1e-10)
        if np.sum(valid) < 3:
            return 0.0, 0.0, 0.0

        log_r = np.log(radii[valid])
        log_omega = np.log(np.abs(omegas[valid]))

        # Linear regression in log-log
        n = len(log_r)
        sum_x = np.sum(log_r)
        sum_y = np.sum(log_omega)
        sum_xy = np.sum(log_r * log_omega)
        sum_x2 = np.sum(log_r * log_r)

        denom = n * sum_x2 - sum_x * sum_x
        if abs(denom) < 1e-10:
            return 0.0, 0.0, 0.0

        beta = (n * sum_xy - sum_x * sum_y) / denom
        log_A = (sum_y - beta * sum_x) / n
        A = np.exp(log_A)

        # R-squared
        y_mean = np.mean(log_omega)
        ss_tot = np.sum((log_omega - y_mean) ** 2)
        y_pred = log_A + beta * log_r
        ss_res = np.sum((log_omega - y_pred) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

        return float(beta), float(A), float(r_squared)

    def get_statistics(self) -> dict:
        """Get summary statistics for orbital motion."""
        omegas = self.get_omega_distribution()
        if not omegas:
            return {
                "mean_omega": 0.0,
                "std_omega": 0.0,
                "rotation_coherence": 0.0,
                "mean_period": float('inf'),
                "n_rotating": 0,
                "omega_r_beta": 0.0,
            }

        n_rotating = sum(1 for o in omegas if abs(o) > 1e-6)
        beta, _, r2 = self.fit_omega_r_power_law()

        return {
            "mean_omega": float(np.mean(omegas)),
            "std_omega": float(np.std(omegas)),
            "rotation_coherence": self.get_rotation_coherence(),
            "mean_period": self.get_mean_orbital_period(),
            "n_rotating": n_rotating,
            "omega_r_beta": beta,
            "omega_r_fit_r2": r2,
        }


if __name__ == "__main__":
    # Demo
    print("Orbital Analyzer Demo")
    print("=" * 50)

    center = (100.0, 100.0)
    analyzer = OrbitalAnalyzer(n_patterns=3, center=center, window_size=20)

    # Simulate different orbital behaviors
    for tick in range(100):
        # Pattern 0: Circular orbit at r=20, period=100 ticks
        omega0 = 2 * math.pi / 100
        theta0 = omega0 * tick
        r0 = 20.0
        x0 = center[0] + r0 * math.cos(theta0)
        y0 = center[1] + r0 * math.sin(theta0)
        analyzer.record_position(0, x0, y0, tick)

        # Pattern 1: Faster orbit at r=10
        omega1 = 2 * math.pi / 50  # Twice as fast
        theta1 = omega1 * tick
        r1 = 10.0
        x1 = center[0] + r1 * math.cos(theta1)
        y1 = center[1] + r1 * math.sin(theta1)
        analyzer.record_position(1, x1, y1, tick)

        # Pattern 2: Stationary
        analyzer.record_position(2, center[0] + 30, center[1], tick)

    analyzer.update_all_states()

    print("\nOrbital states:")
    for i in range(3):
        state = analyzer.get_state(i)
        if state:
            print(f"  Pattern {i}: omega={state.omega:.4f} rad/tick, "
                  f"r={state.r:.1f}, period={state.period:.1f} ticks")

    print("\nStatistics:")
    stats = analyzer.get_statistics()
    for k, v in stats.items():
        print(f"  {k}: {v}")
