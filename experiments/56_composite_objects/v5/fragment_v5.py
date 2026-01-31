"""
Integer Fragment Dynamics for V5

Converts V4 float-based fragment dynamics to scaled integer arithmetic.

Key Changes from V4:
- All positions, velocities use scaled integers (SCALE = 10^8)
- Replace numpy arrays with simple (x, y) tuples
- All arithmetic via FixedPoint class
- Perfect determinism, no float drift

Author: V5 Integer Conversion
Date: 2026-01-24
Based on: V4 fragmented_cloud.py (validated 200k ticks)
"""

from dataclasses import dataclass
from typing import List, Tuple
from fixed_point import FixedPoint


@dataclass
class FragmentV5:
    """
    Electron fragment with integer arithmetic.

    All positions and velocities are scaled integers: actual_value = value / SCALE

    Attributes:
        fragment_id: Unique identifier
        x, y: Position components (scaled integers)
        vx, vy: Velocity components (scaled integers)
        energy: Fragment energy (scaled integer)
        mass: Fragment mass (scaled integer)
        last_collision_tick: Tick of most recent collision
        collision_count: Total number of collisions
    """

    fragment_id: str
    x: int
    y: int
    vx: int
    vy: int
    energy: int
    mass: int

    # Collision tracking
    last_collision_tick: int = 0
    collision_count: int = 0

    @property
    def speed(self) -> int:
        """
        Current speed (magnitude of velocity).

        Returns:
            Scaled integer: sqrt(vx^2 + vy^2)
        """
        return FixedPoint.norm(self.vx, self.vy)

    @property
    def kinetic_energy(self) -> int:
        """
        Kinetic energy: KE = (1/2) × m × v²

        Returns:
            Scaled integer: (1/2) × mass × speed²
        """
        speed_val = self.speed
        v_squared = FixedPoint.multiply(speed_val, speed_val)
        m_times_v2 = FixedPoint.multiply(self.mass, v_squared)

        # Divide by 2 (multiply by 0.5)
        half = FixedPoint.from_float(0.5)
        return FixedPoint.multiply(half, m_times_v2)

    @property
    def distance_from_origin(self) -> int:
        """
        Distance from origin (proton position).

        Returns:
            Scaled integer: sqrt(x^2 + y^2)
        """
        return FixedPoint.norm(self.x, self.y)

    def update_position(self, dt_scaled: int = None):
        """
        Update position based on current velocity.

        position_new = position_old + velocity * dt

        Args:
            dt_scaled: Time step (scaled integer). Default = 1.0 (SCALE)
        """
        if dt_scaled is None:
            dt_scaled = FixedPoint.SCALE  # Default dt = 1.0

        # x_new = x_old + vx * dt
        self.x += FixedPoint.multiply(self.vx, dt_scaled)
        self.y += FixedPoint.multiply(self.vy, dt_scaled)

    def apply_acceleration(self, ax: int, ay: int, dt_scaled: int = None):
        """
        Apply acceleration to velocity.

        velocity_new = velocity_old + acceleration * dt

        Args:
            ax, ay: Acceleration components (scaled integers)
            dt_scaled: Time step (scaled integer). Default = 1.0 (SCALE)
        """
        if dt_scaled is None:
            dt_scaled = FixedPoint.SCALE  # Default dt = 1.0

        # vx_new = vx_old + ax * dt
        self.vx += FixedPoint.multiply(ax, dt_scaled)
        self.vy += FixedPoint.multiply(ay, dt_scaled)

    def to_dict(self) -> dict:
        """
        Convert to dictionary (for JSON serialization).

        Converts scaled integers to floats for readability.

        Returns:
            Dictionary with float values
        """
        return {
            "fragment_id": self.fragment_id,
            "x": FixedPoint.to_float(self.x),
            "y": FixedPoint.to_float(self.y),
            "vx": FixedPoint.to_float(self.vx),
            "vy": FixedPoint.to_float(self.vy),
            "energy": FixedPoint.to_float(self.energy),
            "mass": FixedPoint.to_float(self.mass),
            "speed": FixedPoint.to_float(self.speed),
            "kinetic_energy": FixedPoint.to_float(self.kinetic_energy),
            "distance_from_origin": FixedPoint.to_float(self.distance_from_origin),
            "last_collision_tick": self.last_collision_tick,
            "collision_count": self.collision_count,
        }


class FragmentedCloudV5:
    """
    Collection of fragments with integer arithmetic.

    Maintains cloud-level statistics using scaled integers.
    """

    def __init__(self, cloud_id: str = "electron_cloud"):
        """Initialize empty cloud."""
        self.cloud_id = cloud_id
        self.fragments: List[FragmentV5] = []

        # Collective properties (scaled integers)
        self.center_of_mass_x = 0
        self.center_of_mass_y = 0
        self.total_mass = 0
        self.total_energy = 0
        self.total_kinetic_energy = 0
        self.cloud_radius_rms = 0
        self.cloud_radius_mean = 0

        # Angular momentum (scaled integer)
        self.angular_momentum = 0

        # Statistics
        self.total_collisions = 0
        self.collision_rate = FixedPoint.from_float(0.0)

    def add_fragment(self, fragment: FragmentV5):
        """Add a fragment to the cloud."""
        self.fragments.append(fragment)
        self.total_mass += fragment.mass
        self.total_energy += fragment.energy

    def update_statistics(self):
        """
        Compute collective properties from fragment states.

        All calculations use scaled integer arithmetic.
        """
        if len(self.fragments) == 0:
            return

        # Center of mass
        total_mass = sum(f.mass for f in self.fragments)
        if total_mass == 0:
            return

        com_x_sum = sum(FixedPoint.multiply(f.mass, f.x) for f in self.fragments)
        com_y_sum = sum(FixedPoint.multiply(f.mass, f.y) for f in self.fragments)

        self.center_of_mass_x = FixedPoint.divide(com_x_sum, total_mass)
        self.center_of_mass_y = FixedPoint.divide(com_y_sum, total_mass)

        # Cloud radius statistics
        radii = [f.distance_from_origin for f in self.fragments]

        # Mean radius
        self.cloud_radius_mean = sum(radii) // len(radii)

        # RMS radius: sqrt(mean(r^2))
        r_squared_sum = sum(FixedPoint.multiply(r, r) for r in radii)
        r_squared_mean = r_squared_sum // len(radii)
        self.cloud_radius_rms = FixedPoint.sqrt(r_squared_mean)

        # Total kinetic energy
        self.total_kinetic_energy = sum(f.kinetic_energy for f in self.fragments)

        # Angular momentum: L_z = sum(m * (x * vy - y * vx))
        L_z = 0
        for f in self.fragments:
            # x * vy
            x_vy = FixedPoint.multiply(f.x, f.vy)
            # y * vx
            y_vx = FixedPoint.multiply(f.y, f.vx)
            # x * vy - y * vx
            cross = x_vy - y_vx
            # m * cross
            L_z += FixedPoint.multiply(f.mass, cross)

        self.angular_momentum = L_z

        # Update total mass and energy
        self.total_mass = total_mass
        self.total_energy = sum(f.energy for f in self.fragments)

    def get_statistics_dict(self) -> dict:
        """
        Get cloud statistics as dictionary (float values).

        Returns:
            Dictionary with float values for readability
        """
        return {
            "cloud_id": self.cloud_id,
            "n_fragments": len(self.fragments),
            "center_of_mass": (
                FixedPoint.to_float(self.center_of_mass_x),
                FixedPoint.to_float(self.center_of_mass_y)
            ),
            "total_mass": FixedPoint.to_float(self.total_mass),
            "total_energy": FixedPoint.to_float(self.total_energy),
            "total_kinetic_energy": FixedPoint.to_float(self.total_kinetic_energy),
            "cloud_radius_mean": FixedPoint.to_float(self.cloud_radius_mean),
            "cloud_radius_rms": FixedPoint.to_float(self.cloud_radius_rms),
            "angular_momentum": FixedPoint.to_float(self.angular_momentum),
            "total_collisions": self.total_collisions,
            "collision_rate": FixedPoint.to_float(self.collision_rate),
        }


def test_fragment_v5():
    """Test suite for FragmentV5 integer dynamics."""
    print("Testing FragmentV5 Integer Dynamics")
    print("=" * 70)

    # Test 1: Fragment creation
    print("\nTest 1: Fragment Creation")
    frag = FragmentV5(
        fragment_id="test_01",
        x=FixedPoint.from_float(1.0),
        y=FixedPoint.from_float(2.0),
        vx=FixedPoint.from_float(0.1),
        vy=FixedPoint.from_float(0.2),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(0.002),
    )

    print(f"  Position: ({FixedPoint.to_float(frag.x):.4f}, {FixedPoint.to_float(frag.y):.4f})")
    print(f"  Velocity: ({FixedPoint.to_float(frag.vx):.4f}, {FixedPoint.to_float(frag.vy):.4f})")
    print(f"  Speed: {FixedPoint.to_float(frag.speed):.6f}")
    print(f"  Distance: {FixedPoint.to_float(frag.distance_from_origin):.6f}")
    print(f"  KE: {FixedPoint.to_float(frag.kinetic_energy):.8f}")

    # Expected values (for validation)
    import math
    expected_speed = math.sqrt(0.1**2 + 0.2**2)
    expected_dist = math.sqrt(1.0**2 + 2.0**2)
    expected_ke = 0.5 * 0.002 * expected_speed**2

    actual_speed = FixedPoint.to_float(frag.speed)
    actual_dist = FixedPoint.to_float(frag.distance_from_origin)
    actual_ke = FixedPoint.to_float(frag.kinetic_energy)

    speed_ok = abs(actual_speed - expected_speed) < 1e-6
    dist_ok = abs(actual_dist - expected_dist) < 1e-6
    ke_ok = abs(actual_ke - expected_ke) < 1e-8

    print(f"  Speed check: {actual_speed:.6f} vs {expected_speed:.6f} [{'PASS' if speed_ok else 'FAIL'}]")
    print(f"  Distance check: {actual_dist:.6f} vs {expected_dist:.6f} [{'PASS' if dist_ok else 'FAIL'}]")
    print(f"  KE check: {actual_ke:.8f} vs {expected_ke:.8f} [{'PASS' if ke_ok else 'FAIL'}]")

    # Test 2: Position update
    print("\nTest 2: Position Update")
    initial_x = FixedPoint.to_float(frag.x)
    initial_y = FixedPoint.to_float(frag.y)

    frag.update_position()  # dt = 1.0 (default)

    new_x = FixedPoint.to_float(frag.x)
    new_y = FixedPoint.to_float(frag.y)

    expected_x = initial_x + 0.1 * 1.0
    expected_y = initial_y + 0.2 * 1.0

    x_ok = abs(new_x - expected_x) < 1e-6
    y_ok = abs(new_y - expected_y) < 1e-6

    print(f"  x: {initial_x:.4f} -> {new_x:.4f} (expected {expected_x:.4f}) [{'PASS' if x_ok else 'FAIL'}]")
    print(f"  y: {initial_y:.4f} -> {new_y:.4f} (expected {expected_y:.4f}) [{'PASS' if y_ok else 'FAIL'}]")

    # Test 3: Acceleration application
    print("\nTest 3: Acceleration Application")
    initial_vx = FixedPoint.to_float(frag.vx)
    initial_vy = FixedPoint.to_float(frag.vy)

    ax = FixedPoint.from_float(0.05)
    ay = FixedPoint.from_float(-0.1)
    frag.apply_acceleration(ax, ay)  # dt = 1.0 (default)

    new_vx = FixedPoint.to_float(frag.vx)
    new_vy = FixedPoint.to_float(frag.vy)

    expected_vx = initial_vx + 0.05 * 1.0
    expected_vy = initial_vy - 0.1 * 1.0

    vx_ok = abs(new_vx - expected_vx) < 1e-6
    vy_ok = abs(new_vy - expected_vy) < 1e-6

    print(f"  vx: {initial_vx:.4f} -> {new_vx:.4f} (expected {expected_vx:.4f}) [{'PASS' if vx_ok else 'FAIL'}]")
    print(f"  vy: {initial_vy:.4f} -> {new_vy:.4f} (expected {expected_vy:.4f}) [{'PASS' if vy_ok else 'FAIL'}]")

    # Test 4: Cloud statistics
    print("\nTest 4: Cloud Statistics")
    cloud = FragmentedCloudV5("test_cloud")

    # Add 3 fragments
    for i in range(3):
        f = FragmentV5(
            fragment_id=f"frag_{i}",
            x=FixedPoint.from_float(1.0 + i),
            y=FixedPoint.from_float(2.0 - i * 0.5),
            vx=FixedPoint.from_float(0.1),
            vy=FixedPoint.from_float(0.1 * (i + 1)),
            energy=FixedPoint.from_float(1.0),
            mass=FixedPoint.from_float(0.002),
        )
        cloud.add_fragment(f)

    cloud.update_statistics()
    stats = cloud.get_statistics_dict()

    print(f"  Fragments: {stats['n_fragments']}")
    print(f"  Total mass: {stats['total_mass']:.6f}")
    print(f"  Total energy: {stats['total_energy']:.4f}")
    print(f"  Mean radius: {stats['cloud_radius_mean']:.4f}")
    print(f"  RMS radius: {stats['cloud_radius_rms']:.4f}")
    print(f"  Angular momentum: {stats['angular_momentum']:.6f}")

    n_ok = stats['n_fragments'] == 3
    mass_ok = abs(stats['total_mass'] - 0.006) < 1e-8
    energy_ok = abs(stats['total_energy'] - 3.0) < 1e-6

    print(f"  Fragment count: [{'PASS' if n_ok else 'FAIL'}]")
    print(f"  Total mass: [{'PASS' if mass_ok else 'FAIL'}]")
    print(f"  Total energy: [{'PASS' if energy_ok else 'FAIL'}]")

    print("\n" + "=" * 70)
    print("FragmentV5 Tests Complete")


if __name__ == "__main__":
    test_fragment_v5()
