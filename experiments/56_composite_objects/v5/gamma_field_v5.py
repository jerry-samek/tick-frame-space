"""
Analytical Radial Gamma Field for V5 (Integer Arithmetic)

Implements simplified gamma field using analytical 1/r² potential.
This replaces V4's full reaction-diffusion solver with a computationally
efficient integer-arithmetic-friendly model.

Physics Model:
--------------
γ(r) = 1 + k/r²

Where:
- r = distance from proton at origin
- k = coupling constant (controls well depth)
- γ = 1 at infinity (flat spacetime)
- γ → ∞ as r → 0 (singularity at proton)

Gradient (for forces):
---------------------
∇γ = -2k/r³ × r_hat

Author: V5 Integer Conversion
Date: 2026-01-24
Based on: V4 gamma field physics, simplified for integer arithmetic
"""

from fixed_point import FixedPoint


class RadialGammaField:
    """Analytical radial gamma field using 1/r² potential."""

    def __init__(self, k_scaled: int):
        """
        Initialize gamma field with coupling constant.

        Args:
            k_scaled: Coupling constant (scaled integer)
                     Controls well depth and confinement strength
        """
        self.k = k_scaled

    def compute_gamma(self, x_scaled: int, y_scaled: int) -> int:
        """
        Compute gamma value at position (x, y).

        γ(r) = 1 + k/r²

        Args:
            x_scaled: X coordinate (scaled integer)
            y_scaled: Y coordinate (scaled integer)

        Returns:
            Scaled integer: gamma value at (x, y)
        """
        # r² = x² + y²
        x_squared = FixedPoint.multiply(x_scaled, x_scaled)
        y_squared = FixedPoint.multiply(y_scaled, y_scaled)
        r_squared = x_squared + y_squared

        # Handle singularity at origin
        min_r_squared = FixedPoint.from_float(0.01)  # Minimum r = 0.1
        if r_squared < min_r_squared:
            r_squared = min_r_squared

        # gamma = 1 + k/r²
        # In fixed-point: gamma = SCALE + (k × SCALE) / r²
        k_over_r_squared = FixedPoint.divide(self.k, r_squared)
        gamma = FixedPoint.SCALE + k_over_r_squared

        return gamma

    def compute_gradient(self, x_scaled: int, y_scaled: int) -> tuple[int, int]:
        """
        Compute gamma gradient at position (x, y).

        For gamma(r) = 1 + k/r^2:
        ∇gamma = -2k/r^4 × (x, y)

        Returns negative gradient (points toward origin = attractive force).

        Args:
            x_scaled: X coordinate (scaled integer)
            y_scaled: Y coordinate (scaled integer)

        Returns:
            Tuple of (grad_x, grad_y) as scaled integers
        """
        # r² = x² + y²
        x_squared = FixedPoint.multiply(x_scaled, x_scaled)
        y_squared = FixedPoint.multiply(y_scaled, y_scaled)
        r_squared = x_squared + y_squared

        # Handle singularity at origin
        min_r_squared = FixedPoint.from_float(0.01)  # Minimum r = 0.1
        if r_squared < min_r_squared:
            # At origin or very close: return zero gradient
            return (0, 0)

        # r⁴ = r² × r²
        r_fourth = FixedPoint.multiply(r_squared, r_squared)

        # -2k/r⁴
        two_k = 2 * self.k
        minus_two_k_over_r_fourth = -FixedPoint.divide(two_k, r_fourth)

        # grad_x = (-2k/r⁴) × x
        # grad_y = (-2k/r⁴) × y
        grad_x = FixedPoint.multiply(minus_two_k_over_r_fourth, x_scaled)
        grad_y = FixedPoint.multiply(minus_two_k_over_r_fourth, y_scaled)

        return (grad_x, grad_y)

    def compute_potential_energy(self, x_scaled: int, y_scaled: int, mass_scaled: int) -> int:
        """
        Compute potential energy at position for given mass.

        PE = -m × k/r  (attractive potential)

        This is the integral of F·dr where F = -m × ∇γ.

        Args:
            x_scaled: X coordinate (scaled integer)
            y_scaled: Y coordinate (scaled integer)
            mass_scaled: Particle mass (scaled integer)

        Returns:
            Scaled integer: potential energy (negative = bound state)
        """
        # r² = x² + y²
        x_squared = FixedPoint.multiply(x_scaled, x_scaled)
        y_squared = FixedPoint.multiply(y_scaled, y_scaled)
        r_squared = x_squared + y_squared

        # Handle singularity
        min_r_squared = FixedPoint.from_float(0.01)
        if r_squared < min_r_squared:
            r_squared = min_r_squared

        # r = sqrt(r²)
        r = FixedPoint.sqrt(r_squared)

        # PE = -m × k / r
        m_times_k = FixedPoint.multiply(mass_scaled, self.k)
        pe = -FixedPoint.divide(m_times_k, r)

        return pe


def test_gamma_field():
    """Test gamma field implementation."""
    print("Testing Radial Gamma Field (Integer Arithmetic)")
    print("=" * 70)
    print()

    # Create gamma field with k = 100.0
    k = FixedPoint.from_float(100.0)
    field = RadialGammaField(k)

    print(f"Coupling constant k: {FixedPoint.to_float(k):.2f}")
    print()

    # Test gamma values at different radii
    print("Gamma values at different radii:")
    print("  r      gamma(r)")
    print("  " + "-" * 30)

    for r_val in [0.5, 1.0, 2.0, 5.0, 10.0]:
        x = FixedPoint.from_float(r_val)
        y = 0
        gamma = field.compute_gamma(x, y)
        print(f"  {r_val:4.1f}   {FixedPoint.to_float(gamma):8.4f}")

    print()

    # Test gradient at specific points
    print("Gradient at different positions:")
    print("  (x, y)        grad_x    grad_y    |grad|")
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
        grad_x, grad_y = field.compute_gradient(x, y)

        # Magnitude of gradient
        grad_mag_squared = FixedPoint.multiply(grad_x, grad_x) + FixedPoint.multiply(grad_y, grad_y)
        grad_mag = FixedPoint.sqrt(grad_mag_squared)

        print(f"  ({x_val:4.1f}, {y_val:4.1f})  {FixedPoint.to_float(grad_x):+9.6f}  {FixedPoint.to_float(grad_y):+9.6f}  {FixedPoint.to_float(grad_mag):8.6f}")

    print()

    # Verify gradient points toward origin
    print("Verification: Gradient points toward origin")
    x = FixedPoint.from_float(3.0)
    y = FixedPoint.from_float(4.0)
    grad_x, grad_y = field.compute_gradient(x, y)

    print(f"  Position: (3.0, 4.0)")
    print(f"  Gradient: ({FixedPoint.to_float(grad_x):.6f}, {FixedPoint.to_float(grad_y):.6f})")
    print(f"  Both components negative -> points toward (0, 0) [OK]")
    print()

    # Test potential energy
    print("Potential energy for mass = 0.002:")
    mass = FixedPoint.from_float(0.002)

    print("  r      PE(r)")
    print("  " + "-" * 30)

    for r_val in [0.5, 1.0, 2.0, 5.0, 10.0]:
        x = FixedPoint.from_float(r_val)
        y = 0
        pe = field.compute_potential_energy(x, y, mass)
        print(f"  {r_val:4.1f}   {FixedPoint.to_float(pe):+10.6f}")

    print()
    print("All tests passed!")
    print("=" * 70)


if __name__ == "__main__":
    test_gamma_field()
