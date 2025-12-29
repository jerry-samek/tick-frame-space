from collections import defaultdict, deque
from typing import Dict, List, Optional, Tuple
import math

from .base import Observer


class PiDriftObserver(Observer):
    """
    Observer for π drift using geometric measurements from spatial positions.

    For entities positioned on circles at radius R from origin:
        π = circumference / diameter = circumference / (2 * R)

    The circumference is measured by:
        1. Grouping entities by radial distance from origin
        2. Sorting entities by angle around the circle
        3. Measuring chord lengths between adjacent points
        4. Summing to get approximate perimeter

    This provides a direct geometric measurement of π.
    """

    def __init__(self, max_radius: int = 10, log_interval: int = 10, output_dir: Optional[str] = None):
        super().__init__(name="PiDrift", log_interval=log_interval, output_dir=output_dir)

        self.max_radius = max_radius

        # Store π estimates over time
        # radius -> [π(t)]
        self.memory["pi_history"] = defaultdict(list)
        self.memory["geometric_pi_history"] = []

    def on_post_tick(self, state) -> None:
        tick = state.tick

        # Check if positions exist
        if not hasattr(state, 'positions') or len(state.positions) == 0:
            return

        # Group entities by radial distance from origin
        radial_shells = self._group_by_radius(state.positions)

        # Compute geometric π for each radius shell
        geometric_pi_estimates = self._estimate_geometric_pi(radial_shells)

        # Store history
        for radius, pi_val in geometric_pi_estimates.items():
            self.memory["pi_history"][radius].append(pi_val)

        # Store overall geometric π (average across all radii)
        if geometric_pi_estimates:
            avg_pi = sum(geometric_pi_estimates.values()) / len(geometric_pi_estimates)
            self.memory["geometric_pi_history"].append(avg_pi)

        # Compute drift (variance over time)
        pi_drift = self._compute_drift()

        # Logging
        if self.should_log(tick):
            for radius in sorted(radial_shells.keys()):
                entities_at_radius = radial_shells[radius]
                pi_estimate = geometric_pi_estimates.get(radius, 0.0)
                drift = pi_drift.get(radius, 0.0)

                data = {
                    "tick": tick,
                    "radius": radius,
                    "num_entities": len(entities_at_radius),
                    "pi_estimate": pi_estimate,
                    "pi_error": abs(pi_estimate - math.pi) if pi_estimate > 0 else 0.0,
                    "pi_drift": drift,
                }
                self.log_csv("pi_drift_geometric.csv", data)

            # Overall π estimate
            if geometric_pi_estimates:
                avg_pi = sum(geometric_pi_estimates.values()) / len(geometric_pi_estimates)
                avg_error = abs(avg_pi - math.pi)

                summary = (
                    f"[PiDrift t={tick}] "
                    f"Radii tracked: {len(radial_shells)}, "
                    f"Avg π: {avg_pi:.6f}, "
                    f"Error: {avg_error:.6e}, "
                    f"True π: {math.pi:.6f}\n"
                )
                self.log_text("pi_drift_log.txt", summary)

    # ---------------------------------------------------------
    # Geometric π calculation from positions
    # ---------------------------------------------------------
    def _group_by_radius(self, positions: Dict[int, Tuple[float, float, float]]) -> Dict[float, List[Tuple[int, Tuple[float, float, float]]]]:
        """
        Group entities by their radial distance from origin.
        Returns dict: radius -> [(entity_id, position), ...]
        """
        radial_shells = defaultdict(list)

        for entity_id, (x, y, z) in positions.items():
            # Calculate radius from origin (XY plane for 2D circles)
            radius = math.sqrt(x**2 + y**2)

            # Round radius to nearest 0.1 to group similar radii
            radius_bucket = round(radius, 1)

            if radius_bucket <= self.max_radius:
                radial_shells[radius_bucket].append((entity_id, (x, y, z)))

        return radial_shells

    def _estimate_geometric_pi(self, radial_shells: Dict[float, List[Tuple[int, Tuple[float, float, float]]]]) -> Dict[float, float]:
        """
        Estimate π from geometric positions.

        For each radius R with entities positioned on a circle:
            1. Sort entities by angle around the circle
            2. Measure perimeter by summing chord lengths between adjacent points
            3. π ≈ perimeter / (2 * R)

        Returns dict: radius -> π_estimate
        """
        pi_estimates = {}

        for radius, entities in radial_shells.items():
            if radius < 0.01:  # Skip origin
                continue

            if len(entities) < 3:  # Need at least 3 points for a circle
                continue

            # Sort entities by angle (atan2(y, x))
            entities_sorted = sorted(entities, key=lambda e: math.atan2(e[1][1], e[1][0]))

            # Calculate perimeter by summing chord lengths
            perimeter = 0.0
            for i in range(len(entities_sorted)):
                eid1, (x1, y1, z1) = entities_sorted[i]
                eid2, (x2, y2, z2) = entities_sorted[(i + 1) % len(entities_sorted)]

                # Chord length (3D distance)
                chord_length = math.sqrt((x2 - x1)**2 + (y2 - y1)**2 + (z2 - z1)**2)
                perimeter += chord_length

            # π = circumference / diameter = perimeter / (2 * radius)
            pi_estimate = perimeter / (2.0 * radius)
            pi_estimates[radius] = pi_estimate

        return pi_estimates

    # ---------------------------------------------------------
    # Drift computation
    # ---------------------------------------------------------
    def _compute_drift(self) -> Dict[int, float]:
        """
        Drift = variance of π(t, R) over time.
        """
        drift = {}

        for R, history in self.memory["pi_history"].items():
            if len(history) <= 1:
                drift[R] = 0.0
                continue

            mean_pi = sum(history) / len(history)
            variance = sum((x - mean_pi) ** 2 for x in history) / len(history)
            drift[R] = variance

        return drift
