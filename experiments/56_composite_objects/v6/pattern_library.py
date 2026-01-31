"""
Pattern Library - Catalog of Known Stable Field Patterns

Patterns are 5×5 (or 7×7) configurations of ternary field values {-1, 0, +1}.
Stable patterns persist through jitter and evolution rules.

Author: V6 Grid-Based Implementation
Date: 2026-01-24
Based on: STRUCTURE.md
"""

import numpy as np
from typing import Optional, Dict


class PatternLibrary:
    """Registry of known field patterns."""

    def __init__(self, pattern_size: int = 5):
        """
        Initialize pattern library.

        Args:
            pattern_size: Size of patterns (5 = 5×5, 7 = 7×7)
        """
        self.pattern_size = pattern_size
        self.patterns: Dict[str, np.ndarray] = {}
        self.pattern_hashes: Dict[int, str] = {}

        # Initialize default patterns
        self._initialize_default_patterns()

    def _initialize_default_patterns(self):
        """Create initial set of test patterns."""

        if self.pattern_size == 5:
            # === 5×5 Patterns ===

            # Monopole: Simple radial positive pattern
            self.add_pattern("monopole", np.array([
                [ 0,  0,  0,  0,  0],
                [ 0,  0, +1,  0,  0],
                [ 0, +1, +1, +1,  0],
                [ 0,  0, +1,  0,  0],
                [ 0,  0,  0,  0,  0],
            ], dtype=np.int8))

            # Dipole: Vertical positive-negative pair
            self.add_pattern("dipole", np.array([
                [ 0,  0,  0,  0,  0],
                [ 0, +1, +1, +1,  0],
                [ 0, +1,  0, +1,  0],
                [ 0, -1, -1, -1,  0],
                [ 0,  0,  0,  0,  0],
            ], dtype=np.int8))

            # Quadrupole: Alternating +/- pattern
            self.add_pattern("quadrupole", np.array([
                [ 0, +1,  0, +1,  0],
                [+1,  0,  0,  0, +1],
                [ 0,  0,  0,  0,  0],
                [-1,  0,  0,  0, -1],
                [ 0, -1,  0, -1,  0],
            ], dtype=np.int8))

            # Rotating: Asymmetric pattern (simulates angular momentum)
            self.add_pattern("rotating", np.array([
                [ 0,  0, +1,  0,  0],
                [ 0,  0, +1, +1,  0],
                [ 0, +1, +1,  0,  0],
                [ 0, +1,  0,  0,  0],
                [ 0,  0,  0,  0,  0],
            ], dtype=np.int8))

            # Vortex: Circular pattern
            self.add_pattern("vortex", np.array([
                [ 0, +1, +1, +1,  0],
                [+1,  0,  0,  0, +1],
                [+1,  0,  0,  0, -1],
                [-1,  0,  0,  0, -1],
                [ 0, -1, -1, -1,  0],
            ], dtype=np.int8))

            # Unstable: High-energy pattern (should dissolve)
            self.add_pattern("unstable", np.array([
                [+1, -1, +1, -1, +1],
                [-1, +1, -1, +1, -1],
                [+1, -1, +1, -1, +1],
                [-1, +1, -1, +1, -1],
                [+1, -1, +1, -1, +1],
            ], dtype=np.int8))

        elif self.pattern_size == 7:
            # === 7×7 Patterns ===

            # Monopole: Larger radial pattern
            self.add_pattern("monopole", np.array([
                [ 0,  0,  0,  0,  0,  0,  0],
                [ 0,  0,  0, +1,  0,  0,  0],
                [ 0,  0, +1, +1, +1,  0,  0],
                [ 0, +1, +1, +1, +1, +1,  0],
                [ 0,  0, +1, +1, +1,  0,  0],
                [ 0,  0,  0, +1,  0,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0],
            ], dtype=np.int8))

            # Dipole: Vertical pair with stronger gradient
            self.add_pattern("dipole", np.array([
                [ 0,  0,  0,  0,  0,  0,  0],
                [ 0,  0, +1, +1, +1,  0,  0],
                [ 0, +1, +1, +1, +1, +1,  0],
                [ 0,  0,  0,  0,  0,  0,  0],
                [ 0, -1, -1, -1, -1, -1,  0],
                [ 0,  0, -1, -1, -1,  0,  0],
                [ 0,  0,  0,  0,  0,  0,  0],
            ], dtype=np.int8))

    def add_pattern(self, name: str, pattern: np.ndarray):
        """
        Add pattern to library.

        Args:
            name: Pattern identifier
            pattern: NxN array with values in {-1, 0, +1}
        """
        # Validate pattern
        if pattern.shape != (self.pattern_size, self.pattern_size):
            raise ValueError(
                f"Pattern must be {self.pattern_size}×{self.pattern_size}, "
                f"got {pattern.shape}"
            )

        if not np.all(np.isin(pattern, [-1, 0, 1])):
            raise ValueError("Pattern contains values outside {-1, 0, +1}")

        # Store pattern
        self.patterns[name] = pattern.copy()

        # Compute and store hash
        pattern_hash = self._hash_pattern(pattern)
        self.pattern_hashes[pattern_hash] = name

    def get_pattern(self, name: str) -> Optional[np.ndarray]:
        """
        Retrieve pattern by name.

        Returns:
            Copy of pattern array, or None if not found
        """
        if name not in self.patterns:
            return None
        return self.patterns[name].copy()

    def detect_pattern(self, sample: np.ndarray) -> Optional[str]:
        """
        Identify pattern in sample array.

        Args:
            sample: NxN array to identify

        Returns:
            Pattern name if recognized, None otherwise
        """
        if sample.shape != (self.pattern_size, self.pattern_size):
            return None

        pattern_hash = self._hash_pattern(sample)
        return self.pattern_hashes.get(pattern_hash, None)

    def _hash_pattern(self, pattern: np.ndarray) -> int:
        """
        Compute hash of pattern for fast lookup.

        Converts 5×5 ternary pattern to unique integer.
        Maps {-1, 0, +1} -> {0, 1, 2}, then interprets as base-3 number.

        Returns:
            Integer hash (unique for each pattern)
        """
        # Map {-1, 0, +1} -> {0, 1, 2}
        mapped = pattern.flatten() + 1

        # Compute base-3 representation
        hash_value = 0
        for i, v in enumerate(mapped):
            hash_value += int(v) * (3 ** i)

        return hash_value

    def list_patterns(self) -> list[str]:
        """Return list of all pattern names."""
        return list(self.patterns.keys())

    def get_pattern_energy(self, name: str) -> int:
        """
        Calculate total energy of pattern (sum of absolute values).

        Args:
            name: Pattern identifier

        Returns:
            Total energy, or 0 if pattern not found
        """
        pattern = self.get_pattern(name)
        if pattern is None:
            return 0
        return int(np.sum(np.abs(pattern)))

    def get_pattern_statistics(self, name: str) -> Optional[dict]:
        """
        Get statistical summary of pattern.

        Returns:
            Dict with counts and energy, or None if not found
        """
        pattern = self.get_pattern(name)
        if pattern is None:
            return None

        unique, counts = np.unique(pattern, return_counts=True)
        count_map = dict(zip(unique, counts))

        return {
            "name": name,
            "size": self.pattern_size,
            "n_negative": count_map.get(-1, 0),
            "n_zero": count_map.get(0, 0),
            "n_positive": count_map.get(1, 0),
            "total_energy": self.get_pattern_energy(name),
            "nonzero_fraction": (count_map.get(-1, 0) + count_map.get(1, 0)) / (self.pattern_size ** 2),
        }

    def __repr__(self) -> str:
        return f"PatternLibrary({self.pattern_size}×{self.pattern_size}, {len(self.patterns)} patterns)"


def visualize_pattern(pattern: np.ndarray) -> str:
    """
    ASCII visualization of pattern.

    Args:
        pattern: NxN array

    Returns:
        ASCII art string
    """
    lines = []
    for row in pattern:
        line = ""
        for cell in row:
            if cell == 1:
                line += "+ "
            elif cell == -1:
                line += "- "
            else:
                line += ". "
        lines.append(line)

    return "\n".join(lines)


if __name__ == "__main__":
    # Demo
    print("PatternLibrary Demo")
    print("=" * 70)

    # Create library
    lib = PatternLibrary(pattern_size=5)
    print(f"Created: {lib}")
    print()

    # List patterns
    print("Available patterns:")
    for name in lib.list_patterns():
        stats = lib.get_pattern_statistics(name)
        print(f"  {name:12s} - energy={stats['total_energy']:2d}, nonzero={stats['nonzero_fraction']:5.1%}")
    print()

    # Visualize patterns
    for name in ["monopole", "dipole", "quadrupole", "rotating", "vortex", "unstable"]:
        pattern = lib.get_pattern(name)
        if pattern is not None:
            print(f"Pattern: {name}")
            print(visualize_pattern(pattern))
            print()

    # Test pattern detection
    test_pattern = lib.get_pattern("monopole")
    detected = lib.detect_pattern(test_pattern)
    print(f"Pattern detection test: {detected} (expected: monopole)")
    print()

    # Test hash uniqueness
    print("Hash uniqueness test:")
    hashes = set()
    for name in lib.list_patterns():
        pattern = lib.get_pattern(name)
        h = lib._hash_pattern(pattern)
        print(f"  {name:12s}: hash={h}")
        hashes.add(h)

    print(f"Total patterns: {len(lib.patterns)}, unique hashes: {len(hashes)}")
    print("=" * 70)
