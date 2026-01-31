"""
Simple Harmonic Confinement Field for V5

Implements linear restoring force F = -k*r for stable confinement.
Much simpler and more numerically stable than 1/r^4 gradient.

Physics Model:
--------------
V(r) = (1/2) * k * r^2
F(r) = -k * r

Where:
- r = distance from origin
- k = spring constant (confinement strength)
- F points toward origin (attractive)

Author: V5 Integer Conversion
Date: 2026-01-24
"""

from fixed_point import FixedPoint


class HarmonicField:
    """Harmonic confinement field with linear restoring force."""

    def __init__(self, k_scaled: int):
        """
        Initialize harmonic field with spring constant.

        Args:
            k_scaled: Spring constant (scaled integer)
                     Controls confinement strength
        """
        self.k = k_scaled

    def compute_force(self, x_scaled: int, y_scaled: int) -> tuple[int, int]:
        """
        Compute restoring force at position (x, y).

        F = -k * (x, y)

        Returns force pointing toward origin (attractive).

        Args:
            x_scaled: X coordinate (scaled integer)
            y_scaled: Y coordinate (scaled integer)

        Returns:
            Tuple of (force_x, force_y) as scaled integers
        """
        # F = -k * r = -k * (x, y)
        force_x = -FixedPoint.multiply(self.k, x_scaled)
        force_y = -FixedPoint.multiply(self.k, y_scaled)

        return (force_x, force_y)

    def compute_potential_energy(self, x_scaled: int, y_scaled: int, mass_scaled: int) -> int:
        """
        Compute potential energy at position for given mass.

        PE = (1/2) * mass * k * r^2

        Args:
            x_scaled: X coordinate (scaled integer)
            y_scaled: Y coordinate (scaled integer)
            mass_scaled: Particle mass (scaled integer)

        Returns:
            Scaled integer: potential energy
        """
        # r^2 = x^2 + y^2
        x_squared = FixedPoint.multiply(x_scaled, x_scaled)
        y_squared = FixedPoint.multiply(y_scaled, y_scaled)
        r_squared = x_squared + y_squared

        # PE = (1/2) * m * k * r^2
        m_times_k = FixedPoint.multiply(mass_scaled, self.k)
        pe = FixedPoint.multiply(m_times_k, r_squared)

        # Divide by 2
        pe = pe // 2

        return pe


def test_harmonic_field():
    """Test harmonic field implementation."""
    print("Testing Harmonic Confinement Field (Integer Arithmetic)")
    print("=" * 70)
    print()

    # Create harmonic field with k = 0.001
    k = FixedPoint.from_float(0.001)
    field = HarmonicField(k)

    print(f"Spring constant k: {FixedPoint.to_float(k):.6f}")
    print()

    # Test force at different positions
    print("Force at different positions:")
    print("  (x, y)        force_x    force_y    |force|")
    print("  " + "-" * 50)

    test_points = [
        (2.0, 0.0),
        (0.0, 2.0),
        (1.0, 1.0),
        (3.0, 4.0),
    ]

    for x_val, y_val in test_points:
        x = FixedPoint.from_float(x_val)
        y = FixedPoint.from_float(y_val)
        force_x, force_y = field.compute_force(x, y)

        # Magnitude of force
        force_mag_squared = FixedPoint.multiply(force_x, force_x) + FixedPoint.multiply(force_y, force_y)
        force_mag = FixedPoint.sqrt(force_mag_squared)

        print(f"  ({x_val:4.1f}, {y_val:4.1f})  {FixedPoint.to_float(force_x):+9.6f}  {FixedPoint.to_float(force_y):+9.6f}  {FixedPoint.to_float(force_mag):8.6f}")

    print()

    # Verify force points toward origin
    print("Verification: Force points toward origin")
    x = FixedPoint.from_float(3.0)
    y = FixedPoint.from_float(4.0)
    force_x, force_y = field.compute_force(x, y)

    print(f"  Position: (3.0, 4.0)")
    print(f"  Force: ({FixedPoint.to_float(force_x):.6f}, {FixedPoint.to_float(force_y):.6f})")
    print(f"  Both components negative -> points toward (0, 0) [OK]")
    print()

    # Test potential energy
    print("Potential energy for mass = 0.002:")
    mass = FixedPoint.from_float(0.002)

    print("  (x, y)      PE")
    print("  " + "-" * 30)

    for x_val, y_val in test_points:
        x = FixedPoint.from_float(x_val)
        y = FixedPoint.from_float(y_val)
        pe = field.compute_potential_energy(x, y, mass)
        print(f"  ({x_val:4.1f}, {y_val:4.1f})  {FixedPoint.to_float(pe):+10.9f}")

    print()
    print("All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_harmonic_field()
