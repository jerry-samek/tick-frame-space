"""
Integer Collision Physics for V5

Converts V4 float-based collision dynamics to scaled integer arithmetic.

Key Physics (Doc 070_01):
- Elastic/inelastic collisions conserve momentum
- Restitution coefficient controls energy dissipation
- Collision detection via spatial proximity

Author: V5 Integer Conversion
Date: 2026-01-24
Based on: V4 collision_dynamics.py (validated 200k ticks)
"""

from typing import List, Tuple
from fragment_v5 import FragmentV5, FragmentedCloudV5
from fixed_point import FixedPoint


def detect_collisions_v5(
    fragments: List[FragmentV5],
    collision_radius_scaled: int
) -> List[Tuple[int, int]]:
    """
    Detect all fragment-fragment collisions using integer arithmetic.

    O(N²) algorithm (acceptable for N=50-100 fragments).

    Args:
        fragments: List of electron fragments
        collision_radius_scaled: Distance threshold (scaled integer)

    Returns:
        List of (i, j) collision pairs where i < j
    """
    collisions = []
    n = len(fragments)

    for i in range(n):
        for j in range(i + 1, n):
            f1 = fragments[i]
            f2 = fragments[j]

            # Compute distance: sqrt((x2-x1)^2 + (y2-y1)^2)
            dx = f2.x - f1.x
            dy = f2.y - f1.y
            distance = FixedPoint.norm(dx, dy)

            # Check collision
            if distance < collision_radius_scaled:
                collisions.append((i, j))

    return collisions


def process_collision_v5(
    f1: FragmentV5,
    f2: FragmentV5,
    restitution_scaled: int,
    current_tick: int = 0
) -> None:
    """
    Process elastic/inelastic collision using integer arithmetic.

    Physics:
    - Conserve total momentum: p_total = p1 + p2
    - Exchange energy based on restitution coefficient
    - Update velocities in-place

    Args:
        f1: First fragment (modified in-place)
        f2: Second fragment (modified in-place)
        restitution_scaled: Coefficient of restitution (scaled integer)
        current_tick: Current simulation tick

    Restitution:
        e = 1.0 (SCALE) → perfectly elastic (energy conserved)
        e = 0.8 (0.8 * SCALE) → slight damping (V4 default)
        e = 0.0 → perfectly inelastic (maximum energy loss)
    """
    # Relative position: r_rel = r2 - r1
    rx_rel = f2.x - f1.x
    ry_rel = f2.y - f1.y

    # Relative velocity: v_rel = v2 - v1
    vx_rel = f2.vx - f1.vx
    vy_rel = f2.vy - f1.vy

    # Distance between fragments
    distance = FixedPoint.norm(rx_rel, ry_rel)

    if distance < 100:  # Threshold: 100 / SCALE = 1e-6
        # Fragments at same position (avoid division by zero)
        return

    # Unit normal vector: n_hat = r_rel / |r_rel|
    # nx_hat = rx_rel / distance
    nx_hat = FixedPoint.divide(rx_rel, distance)
    ny_hat = FixedPoint.divide(ry_rel, distance)

    # Relative velocity along line of centers: v_rel_n = v_rel · n_hat
    v_rel_n = FixedPoint.dot(vx_rel, vy_rel, nx_hat, ny_hat)

    # Skip if fragments already separating
    if v_rel_n >= 0:
        return

    # Reduced mass: μ = (m1 * m2) / (m1 + m2)
    m1_times_m2 = FixedPoint.multiply(f1.mass, f2.mass)
    m1_plus_m2 = f1.mass + f2.mass
    reduced_mass = FixedPoint.divide(m1_times_m2, m1_plus_m2)

    # Impulse magnitude: J = -(1 + e) * μ * v_rel_n
    # (1 + e)
    one_plus_e = FixedPoint.SCALE + restitution_scaled

    # -(1 + e) * μ
    term1 = FixedPoint.multiply(one_plus_e, reduced_mass)

    # -(1 + e) * μ * v_rel_n
    impulse_magnitude = FixedPoint.multiply(term1, v_rel_n)
    impulse_magnitude = -impulse_magnitude

    # Impulse vector (along line of centers): impulse = J * n_hat
    impulse_x = FixedPoint.multiply(impulse_magnitude, nx_hat)
    impulse_y = FixedPoint.multiply(impulse_magnitude, ny_hat)

    # Update velocities:
    # v1_new = v1_old - impulse / m1
    # v2_new = v2_old + impulse / m2

    delta_v1_x = FixedPoint.divide(impulse_x, f1.mass)
    delta_v1_y = FixedPoint.divide(impulse_y, f1.mass)

    delta_v2_x = FixedPoint.divide(impulse_x, f2.mass)
    delta_v2_y = FixedPoint.divide(impulse_y, f2.mass)

    f1.vx -= delta_v1_x
    f1.vy -= delta_v1_y

    f2.vx += delta_v2_x
    f2.vy += delta_v2_y

    # Update collision tracking
    f1.collision_count += 1
    f2.collision_count += 1
    f1.last_collision_tick = current_tick
    f2.last_collision_tick = current_tick


def apply_all_collisions_v5(
    cloud: FragmentedCloudV5,
    collision_radius_scaled: int,
    restitution_scaled: int,
    current_tick: int = 0
) -> int:
    """
    Detect and process all collisions in the cloud.

    Args:
        cloud: Fragmented electron cloud
        collision_radius_scaled: Collision distance threshold (scaled integer)
        restitution_scaled: Coefficient of restitution (scaled integer)
        current_tick: Current simulation tick

    Returns:
        Number of collisions processed
    """
    # Detect collisions
    collision_pairs = detect_collisions_v5(
        cloud.fragments,
        collision_radius_scaled=collision_radius_scaled
    )

    # Process each collision
    for i, j in collision_pairs:
        f1 = cloud.fragments[i]
        f2 = cloud.fragments[j]

        process_collision_v5(
            f1, f2,
            restitution_scaled=restitution_scaled,
            current_tick=current_tick
        )

    # Update total collision count
    n_collisions = len(collision_pairs)
    cloud.total_collisions += n_collisions

    return n_collisions


def test_collision_v5():
    """Test suite for integer collision physics."""
    print("Testing V5 Integer Collision Physics")
    print("=" * 70)

    # Test 1: Collision detection
    print("\nTest 1: Collision Detection")

    frag1 = FragmentV5(
        fragment_id="test_1",
        x=FixedPoint.from_float(0.0),
        y=FixedPoint.from_float(0.0),
        vx=FixedPoint.from_float(0.1),
        vy=FixedPoint.from_float(0.0),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(0.002),
    )

    frag2 = FragmentV5(
        fragment_id="test_2",
        x=FixedPoint.from_float(0.3),  # Distance = 0.3
        y=FixedPoint.from_float(0.0),
        vx=FixedPoint.from_float(-0.1),
        vy=FixedPoint.from_float(0.0),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(0.002),
    )

    frag3 = FragmentV5(
        fragment_id="test_3",
        x=FixedPoint.from_float(1.0),  # Distance = 1.0
        y=FixedPoint.from_float(0.0),
        vx=FixedPoint.from_float(0.0),
        vy=FixedPoint.from_float(0.1),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(0.002),
    )

    fragments = [frag1, frag2, frag3]
    collision_radius = FixedPoint.from_float(0.5)

    collisions = detect_collisions_v5(fragments, collision_radius)

    print(f"  Fragments: 3")
    print(f"  Collision radius: {FixedPoint.to_float(collision_radius):.2f}")
    print(f"  Detected collisions: {len(collisions)}")
    print(f"  Collision pairs: {collisions}")

    expected = [(0, 1)]  # Only frag1-frag2 should collide (distance 0.3 < 0.5)
    detected_ok = collisions == expected

    print(f"  Expected: {expected}")
    print(f"  Result: [{'PASS' if detected_ok else 'FAIL'}]")

    # Test 2: Head-on elastic collision
    print("\nTest 2: Head-On Elastic Collision")

    frag_a = FragmentV5(
        fragment_id="A",
        x=FixedPoint.from_float(0.0),
        y=FixedPoint.from_float(0.0),
        vx=FixedPoint.from_float(1.0),
        vy=FixedPoint.from_float(0.0),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(1.0),
    )

    frag_b = FragmentV5(
        fragment_id="B",
        x=FixedPoint.from_float(0.1),
        y=FixedPoint.from_float(0.0),
        vx=FixedPoint.from_float(-1.0),
        vy=FixedPoint.from_float(0.0),
        energy=FixedPoint.from_float(1.0),
        mass=FixedPoint.from_float(1.0),
    )

    print(f"  Before collision:")
    print(f"    A: vx={FixedPoint.to_float(frag_a.vx):.4f}, vy={FixedPoint.to_float(frag_a.vy):.4f}")
    print(f"    B: vx={FixedPoint.to_float(frag_b.vx):.4f}, vy={FixedPoint.to_float(frag_b.vy):.4f}")

    # Elastic collision (e = 1.0)
    restitution = FixedPoint.from_float(1.0)
    process_collision_v5(frag_a, frag_b, restitution, current_tick=0)

    print(f"  After collision (elastic, e=1.0):")
    print(f"    A: vx={FixedPoint.to_float(frag_a.vx):.4f}, vy={FixedPoint.to_float(frag_a.vy):.4f}")
    print(f"    B: vx={FixedPoint.to_float(frag_b.vx):.4f}, vy={FixedPoint.to_float(frag_b.vy):.4f}")

    # For equal mass head-on elastic collision, velocities should swap
    expected_vx_a = -1.0
    expected_vx_b = 1.0

    vx_a_ok = abs(FixedPoint.to_float(frag_a.vx) - expected_vx_a) < 0.01
    vx_b_ok = abs(FixedPoint.to_float(frag_b.vx) - expected_vx_b) < 0.01

    print(f"  Expected: A.vx ~= {expected_vx_a:.4f}, B.vx ~= {expected_vx_b:.4f}")
    print(f"  Result: [{'PASS' if vx_a_ok and vx_b_ok else 'FAIL'}]")

    # Test 3: Cloud collision processing
    print("\nTest 3: Cloud Collision Processing")

    cloud = FragmentedCloudV5("test_cloud")

    # Create 5 fragments in a line
    for i in range(5):
        f = FragmentV5(
            fragment_id=f"frag_{i}",
            x=FixedPoint.from_float(i * 0.3),
            y=FixedPoint.from_float(0.0),
            vx=FixedPoint.from_float(0.0),
            vy=FixedPoint.from_float(0.0),
            energy=FixedPoint.from_float(1.0),
            mass=FixedPoint.from_float(0.002),
        )
        cloud.add_fragment(f)

    collision_radius = FixedPoint.from_float(0.5)
    restitution = FixedPoint.from_float(0.8)

    n_collisions = apply_all_collisions_v5(
        cloud,
        collision_radius_scaled=collision_radius,
        restitution_scaled=restitution,
        current_tick=10
    )

    print(f"  Fragments: 5 (spaced 0.3 apart)")
    print(f"  Collision radius: {FixedPoint.to_float(collision_radius):.2f}")
    print(f"  Collisions detected: {n_collisions}")
    print(f"  Total collision count: {cloud.total_collisions}")

    # With spacing=0.3 and radius=0.5, expect 4 collisions: (0,1), (1,2), (2,3), (3,4)
    expected_collisions = 4
    collisions_ok = n_collisions == expected_collisions

    print(f"  Expected collisions: {expected_collisions}")
    print(f"  Result: [{'PASS' if collisions_ok else 'FAIL'}]")

    print("\n" + "=" * 70)
    print("V5 Collision Physics Tests Complete")


if __name__ == "__main__":
    test_collision_v5()
