"""
Pattern Identity Tracker - Monitor pattern coherence and lifetime.

Tracks whether patterns persist as coherent field structures or dissolve/reform.
"""

import math
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import sys
from pathlib import Path

# Add v6 to path for imports
v6_path = Path(__file__).parent.parent / "v6"
sys.path.insert(0, str(v6_path))

from planck_grid import PlanckGrid


class PatternState(Enum):
    """Pattern lifecycle states."""
    ALIVE = "alive"  # Coherent pattern exists
    DISSOLVED = "dissolved"  # Pattern has dissolved
    REFORMED = "reformed"  # Pattern reformed after dissolution


@dataclass
class IdentitySnapshot:
    """Snapshot of pattern identity at a tick."""
    tick: int
    local_energy: float
    coherence: float
    state: PatternState


@dataclass
class LifetimeResult:
    """Result of lifetime analysis for a pattern."""
    initial_energy: float
    final_energy: float
    mean_energy: float
    energy_variance: float
    mean_coherence: float
    n_dissolutions: int
    n_reformations: int
    total_dissolved_ticks: int
    lifetime_fraction: float  # Fraction of time spent as ALIVE


class PatternIdentityTracker:
    """Track pattern identity and coherence over time."""

    def __init__(
        self,
        n_patterns: int,
        dissolution_threshold: float = 0.3,
        reformation_threshold: float = 0.7,
        coherence_radius: int = 7
    ):
        """
        Initialize identity tracker.

        Args:
            n_patterns: Number of patterns to track
            dissolution_threshold: Energy fraction below which pattern is dissolved
            reformation_threshold: Energy fraction above which pattern is reformed
            coherence_radius: Radius for local energy calculation
        """
        self.n_patterns = n_patterns
        self.dissolution_threshold = dissolution_threshold
        self.reformation_threshold = reformation_threshold
        self.coherence_radius = coherence_radius

        # History per pattern
        self.history: List[List[IdentitySnapshot]] = [
            [] for _ in range(n_patterns)
        ]

        # Reference energies (set at initialization)
        self.reference_energies: List[float] = [0.0] * n_patterns

        # Current states
        self.current_states: List[PatternState] = [PatternState.ALIVE] * n_patterns

    def set_reference_energy(self, pattern_id: int, energy: float):
        """
        Set reference energy for a pattern (typically initial energy).

        Args:
            pattern_id: Pattern index
            energy: Reference energy value
        """
        self.reference_energies[pattern_id] = energy

    def compute_local_energy(
        self,
        grid: PlanckGrid,
        center_x: int,
        center_y: int
    ) -> float:
        """
        Compute total field energy in local region around center.

        Args:
            grid: PlanckGrid with field values
            center_x, center_y: Center of search region

        Returns:
            Sum of |field| values in region
        """
        r = self.coherence_radius

        # Bounds
        x_min = max(0, center_x - r)
        x_max = min(grid.width, center_x + r + 1)
        y_min = max(0, center_y - r)
        y_max = min(grid.height, center_y + r + 1)

        total = 0.0
        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                total += abs(grid.get_cell(x, y))

        return total

    def compute_coherence(
        self,
        grid: PlanckGrid,
        center_x: int,
        center_y: int
    ) -> float:
        """
        Compute coherence (field concentration) around center.

        High coherence = field concentrated near center
        Low coherence = field spread out or absent

        Returns value in [0, 1].

        Args:
            grid: PlanckGrid with field values
            center_x, center_y: Center of search region

        Returns:
            Coherence metric
        """
        r = self.coherence_radius

        # Compute weighted mean distance from center
        x_min = max(0, center_x - r)
        x_max = min(grid.width, center_x + r + 1)
        y_min = max(0, center_y - r)
        y_max = min(grid.height, center_y + r + 1)

        total_energy = 0.0
        weighted_dist = 0.0

        for y in range(y_min, y_max):
            for x in range(x_min, x_max):
                energy = abs(grid.get_cell(x, y))
                if energy > 0:
                    dx = x - center_x
                    dy = y - center_y
                    dist = math.sqrt(dx * dx + dy * dy)
                    weighted_dist += energy * dist
                    total_energy += energy

        if total_energy < 1e-10:
            return 0.0  # No field = no coherence

        mean_dist = weighted_dist / total_energy
        max_dist = r * math.sqrt(2)  # Maximum possible distance

        # Coherence: 1 if all energy at center, 0 if all at edge
        coherence = 1.0 - (mean_dist / max_dist)
        return max(0.0, min(1.0, coherence))

    def update(
        self,
        pattern_id: int,
        grid: PlanckGrid,
        center_x: int,
        center_y: int,
        tick: int
    ):
        """
        Update identity state for a pattern.

        Args:
            pattern_id: Pattern index
            grid: Current grid state
            center_x, center_y: Pattern center coordinates
            tick: Current tick number
        """
        energy = self.compute_local_energy(grid, center_x, center_y)
        coherence = self.compute_coherence(grid, center_x, center_y)

        ref_energy = self.reference_energies[pattern_id]
        if ref_energy < 1e-10:
            ref_energy = energy  # Use first energy as reference
            self.reference_energies[pattern_id] = ref_energy

        # Determine state transition
        energy_ratio = energy / ref_energy if ref_energy > 0 else 0.0
        current_state = self.current_states[pattern_id]

        if current_state == PatternState.ALIVE or current_state == PatternState.REFORMED:
            if energy_ratio < self.dissolution_threshold:
                new_state = PatternState.DISSOLVED
            else:
                new_state = PatternState.ALIVE
        else:  # DISSOLVED
            if energy_ratio > self.reformation_threshold:
                new_state = PatternState.REFORMED
            else:
                new_state = PatternState.DISSOLVED

        self.current_states[pattern_id] = new_state

        # Record snapshot
        snapshot = IdentitySnapshot(
            tick=tick,
            local_energy=energy,
            coherence=coherence,
            state=new_state
        )
        self.history[pattern_id].append(snapshot)

    def get_current_state(self, pattern_id: int) -> PatternState:
        """Get current state for a pattern."""
        return self.current_states[pattern_id]

    def is_alive(self, pattern_id: int) -> bool:
        """Check if pattern is currently alive (ALIVE or REFORMED)."""
        state = self.current_states[pattern_id]
        return state in (PatternState.ALIVE, PatternState.REFORMED)

    def analyze_lifetime(self, pattern_id: int) -> LifetimeResult:
        """
        Analyze pattern lifetime and stability.

        Args:
            pattern_id: Pattern index

        Returns:
            LifetimeResult with statistics
        """
        hist = self.history[pattern_id]
        if not hist:
            return LifetimeResult(
                initial_energy=0.0,
                final_energy=0.0,
                mean_energy=0.0,
                energy_variance=0.0,
                mean_coherence=0.0,
                n_dissolutions=0,
                n_reformations=0,
                total_dissolved_ticks=0,
                lifetime_fraction=1.0
            )

        energies = [s.local_energy for s in hist]
        coherences = [s.coherence for s in hist]
        states = [s.state for s in hist]

        # Count state transitions
        n_dissolutions = 0
        n_reformations = 0
        for i in range(1, len(states)):
            if states[i] == PatternState.DISSOLVED and states[i-1] != PatternState.DISSOLVED:
                n_dissolutions += 1
            if states[i] == PatternState.REFORMED:
                n_reformations += 1

        # Time in dissolved state
        dissolved_ticks = sum(1 for s in states if s == PatternState.DISSOLVED)
        alive_ticks = len(states) - dissolved_ticks

        return LifetimeResult(
            initial_energy=energies[0] if energies else 0.0,
            final_energy=energies[-1] if energies else 0.0,
            mean_energy=float(np.mean(energies)) if energies else 0.0,
            energy_variance=float(np.var(energies)) if energies else 0.0,
            mean_coherence=float(np.mean(coherences)) if coherences else 0.0,
            n_dissolutions=n_dissolutions,
            n_reformations=n_reformations,
            total_dissolved_ticks=dissolved_ticks,
            lifetime_fraction=alive_ticks / len(states) if states else 1.0
        )

    def get_alive_count(self) -> int:
        """Get number of currently alive patterns."""
        return sum(1 for s in self.current_states if s != PatternState.DISSOLVED)

    def get_statistics(self) -> dict:
        """Get summary statistics across all patterns."""
        # Analyze all patterns
        results = [self.analyze_lifetime(i) for i in range(self.n_patterns)]

        mean_lifetime_fraction = np.mean([r.lifetime_fraction for r in results])
        total_dissolutions = sum(r.n_dissolutions for r in results)
        total_reformations = sum(r.n_reformations for r in results)
        mean_coherence = np.mean([r.mean_coherence for r in results])

        return {
            "alive_count": self.get_alive_count(),
            "alive_fraction": self.get_alive_count() / self.n_patterns,
            "mean_lifetime_fraction": float(mean_lifetime_fraction),
            "total_dissolutions": total_dissolutions,
            "total_reformations": total_reformations,
            "mean_coherence": float(mean_coherence),
        }


if __name__ == "__main__":
    # Demo (requires v6 imports)
    print("Pattern Identity Tracker Demo")
    print("=" * 50)

    try:
        from planck_grid import PlanckGrid

        # Create mock grid
        grid = PlanckGrid(50, 50)

        # Write a pattern at center
        for dy in range(-2, 3):
            for dx in range(-2, 3):
                if abs(dx) + abs(dy) <= 2:
                    grid.set_cell(25 + dx, 25 + dy, 1)

        tracker = PatternIdentityTracker(
            n_patterns=1,
            dissolution_threshold=0.3,
            reformation_threshold=0.7,
            coherence_radius=7
        )

        # Set reference energy
        initial_energy = tracker.compute_local_energy(grid, 25, 25)
        tracker.set_reference_energy(0, initial_energy)
        print(f"Initial energy: {initial_energy}")

        # Simulate evolution (pattern slowly dissolving then reforming)
        for tick in range(100):
            if tick < 30:
                # Stable
                pass
            elif tick < 50:
                # Dissolving
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if np.random.random() < 0.1:
                            grid.set_cell(25 + dx, 25 + dy, 0)
            elif tick < 70:
                # Fully dissolved
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        grid.set_cell(25 + dx, 25 + dy, 0)
            else:
                # Reforming
                for dy in range(-2, 3):
                    for dx in range(-2, 3):
                        if abs(dx) + abs(dy) <= 2:
                            grid.set_cell(25 + dx, 25 + dy, 1)

            tracker.update(0, grid, 25, 25, tick)

            if tick % 20 == 0:
                state = tracker.get_current_state(0)
                energy = tracker.compute_local_energy(grid, 25, 25)
                print(f"Tick {tick}: state={state.value}, energy={energy}")

        print("\nLifetime analysis:")
        result = tracker.analyze_lifetime(0)
        print(f"  Dissolutions: {result.n_dissolutions}")
        print(f"  Reformations: {result.n_reformations}")
        print(f"  Lifetime fraction: {result.lifetime_fraction:.2f}")
        print(f"  Mean coherence: {result.mean_coherence:.2f}")

    except ImportError as e:
        print(f"Could not import v6 modules: {e}")
        print("Run from v7 directory or ensure v6 is in path.")
