"""
Motion History - Trajectory storage and Mean Squared Displacement analysis.

Tracks position time-series and computes MSD for diffusion characterization.
"""

import math
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass, field


@dataclass
class TrajectoryPoint:
    """Single point in a trajectory."""
    tick: int
    x: float
    y: float


@dataclass
class MSDResult:
    """Result of MSD analysis."""
    lags: np.ndarray  # Time lags
    msd_values: np.ndarray  # MSD at each lag
    alpha: float  # Scaling exponent (MSD ~ t^alpha)
    diffusion_coefficient: float  # D from MSD = 4*D*t (2D)
    r_squared: float  # Quality of power-law fit

    def interpret_alpha(self) -> str:
        """Interpret the scaling exponent."""
        if self.alpha < 0.5:
            return "subdiffusion (strongly trapped)"
        elif self.alpha < 0.9:
            return "subdiffusion (weakly trapped)"
        elif self.alpha < 1.1:
            return "normal diffusion (random walk)"
        elif self.alpha < 1.5:
            return "superdiffusion (weak drift)"
        else:
            return "superdiffusion/ballistic (strong directed motion)"


class MotionHistory:
    """Store and analyze motion trajectories for multiple patterns."""

    def __init__(self, n_patterns: int, max_length: int = 1000):
        """
        Initialize motion history.

        Args:
            n_patterns: Number of patterns to track
            max_length: Maximum trajectory length per pattern
        """
        self.n_patterns = n_patterns
        self.max_length = max_length

        # Trajectories: list of TrajectoryPoint per pattern
        self.trajectories: List[List[TrajectoryPoint]] = [
            [] for _ in range(n_patterns)
        ]

    def record(self, pattern_id: int, x: float, y: float, tick: int):
        """
        Record a position in the trajectory.

        Args:
            pattern_id: Pattern index
            x, y: Position coordinates
            tick: Current tick number
        """
        point = TrajectoryPoint(tick, x, y)
        self.trajectories[pattern_id].append(point)

        # Trim if too long
        if len(self.trajectories[pattern_id]) > self.max_length:
            self.trajectories[pattern_id] = self.trajectories[pattern_id][-self.max_length:]

    def get_trajectory(self, pattern_id: int) -> List[TrajectoryPoint]:
        """Get trajectory for a pattern."""
        return self.trajectories[pattern_id]

    def get_trajectory_arrays(self, pattern_id: int) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """
        Get trajectory as numpy arrays.

        Returns:
            (ticks, xs, ys) arrays
        """
        traj = self.trajectories[pattern_id]
        if not traj:
            return np.array([]), np.array([]), np.array([])

        ticks = np.array([p.tick for p in traj])
        xs = np.array([p.x for p in traj])
        ys = np.array([p.y for p in traj])

        return ticks, xs, ys

    def compute_displacement(self, pattern_id: int) -> float:
        """
        Compute total displacement from initial to final position.

        Args:
            pattern_id: Pattern index

        Returns:
            Euclidean displacement
        """
        traj = self.trajectories[pattern_id]
        if len(traj) < 2:
            return 0.0

        dx = traj[-1].x - traj[0].x
        dy = traj[-1].y - traj[0].y
        return math.sqrt(dx * dx + dy * dy)

    def compute_msd_single(self, pattern_id: int, max_lag: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute Mean Squared Displacement for a single pattern.

        MSD(tau) = <|r(t+tau) - r(t)|^2>

        Args:
            pattern_id: Pattern index
            max_lag: Maximum lag in trajectory indices

        Returns:
            (lags, msd_values) arrays
        """
        traj = self.trajectories[pattern_id]
        n = len(traj)

        if n < 2:
            return np.array([]), np.array([])

        # Limit max_lag to trajectory length
        max_lag = min(max_lag, n - 1)

        lags = []
        msd_values = []

        for lag in range(1, max_lag + 1):
            squared_displacements = []

            for i in range(n - lag):
                dx = traj[i + lag].x - traj[i].x
                dy = traj[i + lag].y - traj[i].y
                squared_displacements.append(dx * dx + dy * dy)

            if squared_displacements:
                lags.append(lag)
                msd_values.append(np.mean(squared_displacements))

        return np.array(lags), np.array(msd_values)

    def compute_msd_ensemble(self, max_lag: int = 100) -> Tuple[np.ndarray, np.ndarray]:
        """
        Compute ensemble-averaged MSD across all patterns.

        Args:
            max_lag: Maximum lag

        Returns:
            (lags, msd_values) arrays
        """
        all_msd = []

        for pattern_id in range(self.n_patterns):
            lags, msd = self.compute_msd_single(pattern_id, max_lag)
            if len(msd) > 0:
                all_msd.append(msd)

        if not all_msd:
            return np.array([]), np.array([])

        # Pad shorter arrays with NaN
        max_len = max(len(m) for m in all_msd)
        padded = np.full((len(all_msd), max_len), np.nan)
        for i, m in enumerate(all_msd):
            padded[i, :len(m)] = m

        # Compute mean, ignoring NaN
        ensemble_msd = np.nanmean(padded, axis=0)
        lags = np.arange(1, max_len + 1)

        return lags, ensemble_msd

    def fit_msd_power_law(self, lags: np.ndarray, msd: np.ndarray) -> Tuple[float, float, float]:
        """
        Fit MSD to power law: MSD = A * t^alpha

        Args:
            lags: Time lags
            msd: MSD values

        Returns:
            (alpha, A, r_squared) where MSD = A * t^alpha
        """
        # Remove zeros and NaN
        valid = (lags > 0) & (msd > 0) & np.isfinite(msd)
        if np.sum(valid) < 2:
            return 1.0, 0.0, 0.0

        log_t = np.log(lags[valid])
        log_msd = np.log(msd[valid])

        # Linear regression in log-log space
        n = len(log_t)
        sum_x = np.sum(log_t)
        sum_y = np.sum(log_msd)
        sum_xy = np.sum(log_t * log_msd)
        sum_x2 = np.sum(log_t * log_t)

        denom = n * sum_x2 - sum_x * sum_x
        if abs(denom) < 1e-10:
            return 1.0, 0.0, 0.0

        alpha = (n * sum_xy - sum_x * sum_y) / denom
        log_A = (sum_y - alpha * sum_x) / n
        A = np.exp(log_A)

        # R-squared
        y_mean = np.mean(log_msd)
        ss_tot = np.sum((log_msd - y_mean) ** 2)
        y_pred = log_A + alpha * log_t
        ss_res = np.sum((log_msd - y_pred) ** 2)
        r_squared = 1 - ss_res / ss_tot if ss_tot > 0 else 0.0

        return float(alpha), float(A), float(r_squared)

    def analyze_msd(self, max_lag: int = 100) -> MSDResult:
        """
        Full MSD analysis with power-law fit.

        Args:
            max_lag: Maximum lag for MSD calculation

        Returns:
            MSDResult with lags, MSD values, and fit parameters
        """
        lags, msd = self.compute_msd_ensemble(max_lag)

        if len(msd) == 0:
            return MSDResult(
                lags=np.array([]),
                msd_values=np.array([]),
                alpha=1.0,
                diffusion_coefficient=0.0,
                r_squared=0.0
            )

        alpha, A, r_squared = self.fit_msd_power_law(lags, msd)

        # Diffusion coefficient: MSD = 4*D*t in 2D for alpha=1
        # For general alpha: D_eff = A / 4
        D = A / 4.0

        return MSDResult(
            lags=lags,
            msd_values=msd,
            alpha=alpha,
            diffusion_coefficient=D,
            r_squared=r_squared
        )

    def get_statistics(self) -> dict:
        """Get summary statistics for all trajectories."""
        lengths = [len(t) for t in self.trajectories]
        displacements = [self.compute_displacement(i) for i in range(self.n_patterns)]

        return {
            "n_patterns": self.n_patterns,
            "mean_trajectory_length": float(np.mean(lengths)),
            "max_trajectory_length": int(np.max(lengths)) if lengths else 0,
            "mean_displacement": float(np.mean(displacements)),
            "max_displacement": float(np.max(displacements)) if displacements else 0.0,
        }


if __name__ == "__main__":
    # Demo
    print("Motion History Demo")
    print("=" * 50)

    history = MotionHistory(n_patterns=3, max_length=500)

    # Simulate different motion types
    np.random.seed(42)

    for tick in range(200):
        # Pattern 0: Random walk
        if tick == 0:
            x0, y0 = 100.0, 100.0
        else:
            traj = history.get_trajectory(0)
            x0 = traj[-1].x + np.random.normal(0, 0.5)
            y0 = traj[-1].y + np.random.normal(0, 0.5)
        history.record(0, x0, y0, tick)

        # Pattern 1: Ballistic motion
        history.record(1, 100 + tick * 0.1, 100 + tick * 0.05, tick)

        # Pattern 2: Trapped (small oscillation)
        history.record(2, 100 + 0.5 * np.sin(tick * 0.1), 100 + 0.5 * np.cos(tick * 0.1), tick)

    print("\nTrajectory statistics:")
    stats = history.get_statistics()
    for k, v in stats.items():
        print(f"  {k}: {v}")

    print("\nMSD Analysis:")
    result = history.analyze_msd(max_lag=50)
    print(f"  Alpha (scaling exponent): {result.alpha:.3f}")
    print(f"  Diffusion coefficient: {result.diffusion_coefficient:.6f}")
    print(f"  R-squared: {result.r_squared:.3f}")
    print(f"  Interpretation: {result.interpret_alpha()}")
