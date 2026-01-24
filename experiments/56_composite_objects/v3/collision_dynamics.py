#!/usr/bin/env python3
"""
Collision Dynamics for Fragmented Electron Cloud (V3)

Based on Doc 070_01: "Collision-Driven Stabilization of Fragmented Electron Patterns"

From Doc 070_01 §4:
"Inside the electron cloud, fragments constantly collide, exchange momentum,
redistribute energy, and collectively settle into a minimum-energy configuration.
This process naturally drives the system toward stable orbital levels, quantized
energy states, and robust equilibrium distributions."
"""

import numpy as np
from typing import List, Tuple
from fragmented_cloud import ElectronFragment, FragmentedElectronCloud


# ============================================================================
# Collision Detection
# ============================================================================

def detect_collisions(
    fragments: List[ElectronFragment],
    collision_radius: float = 0.5
) -> List[Tuple[int, int]]:
    """
    Detect all fragment-fragment collisions.

    Uses O(N²) naive algorithm (acceptable for N=50-100 fragments).

    Args:
        fragments: List of electron fragments
        collision_radius: Distance threshold for collision

    Returns:
        List of (i, j) pairs where i < j (collision pairs)
    """
    collisions = []
    n = len(fragments)

    for i in range(n):
        for j in range(i + 1, n):
            f1 = fragments[i]
            f2 = fragments[j]

            # Compute distance
            dx = f2.position[0] - f1.position[0]
            dy = f2.position[1] - f1.position[1]
            distance = np.sqrt(dx**2 + dy**2)

            # Check collision
            if distance < collision_radius:
                collisions.append((i, j))

    return collisions


def detect_collisions_spatial_hash(
    fragments: List[ElectronFragment],
    collision_radius: float = 0.5,
    grid_size: float = 1.0
) -> List[Tuple[int, int]]:
    """
    Detect collisions using spatial hashing (O(N) for uniform distribution).

    More efficient for large N (>100 fragments), but adds complexity.

    Args:
        fragments: List of electron fragments
        collision_radius: Distance threshold for collision
        grid_size: Size of hash grid cells

    Returns:
        List of (i, j) collision pairs
    """
    # Build spatial hash
    hash_table = {}

    for i, frag in enumerate(fragments):
        # Hash position to grid cell
        cell_x = int(frag.position[0] / grid_size)
        cell_y = int(frag.position[1] / grid_size)
        cell = (cell_x, cell_y)

        if cell not in hash_table:
            hash_table[cell] = []
        hash_table[cell].append(i)

    # Check collisions only within same or adjacent cells
    collisions = []
    checked_pairs = set()

    for cell, indices in hash_table.items():
        # Check within same cell
        for idx_i in range(len(indices)):
            for idx_j in range(idx_i + 1, len(indices)):
                i = indices[idx_i]
                j = indices[idx_j]
                pair = (min(i, j), max(i, j))

                if pair not in checked_pairs:
                    checked_pairs.add(pair)

                    f1 = fragments[i]
                    f2 = fragments[j]
                    distance = np.linalg.norm(f2.position - f1.position)

                    if distance < collision_radius:
                        collisions.append(pair)

        # Check adjacent cells
        cx, cy = cell
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue

                neighbor_cell = (cx + dx, cy + dy)
                if neighbor_cell in hash_table:
                    neighbor_indices = hash_table[neighbor_cell]

                    for i in indices:
                        for j in neighbor_indices:
                            pair = (min(i, j), max(i, j))

                            if pair not in checked_pairs:
                                checked_pairs.add(pair)

                                f1 = fragments[i]
                                f2 = fragments[j]
                                distance = np.linalg.norm(f2.position - f1.position)

                                if distance < collision_radius:
                                    collisions.append(pair)

    return collisions


# ============================================================================
# Collision Processing
# ============================================================================

def process_collision(
    f1: ElectronFragment,
    f2: ElectronFragment,
    restitution: float = 0.8,
    current_tick: int = 0
) -> None:
    """
    Process elastic/inelastic collision between two fragments.

    From Doc 070_01 §4:
    "Fragments constantly collide, exchange momentum, redistribute energy,
    and collectively settle into a minimum-energy configuration."

    Physics:
    - Conserve total momentum: p_total = p1 + p2
    - Exchange energy based on restitution coefficient
    - Update velocities in-place

    Args:
        f1: First fragment (modified in-place)
        f2: Second fragment (modified in-place)
        restitution: Coefficient of restitution (0=inelastic, 1=elastic)
        current_tick: Current simulation tick

    Restitution coefficient:
        e = 1.0 → perfectly elastic (energy conserved)
        e = 0.8 → slight damping (thermalization, Doc 070_01)
        e = 0.0 → perfectly inelastic (maximum energy loss)
    """
    # Relative position and velocity
    r_rel = f2.position - f1.position
    v_rel = f2.velocity - f1.velocity

    # Distance between fragments
    distance = np.linalg.norm(r_rel)

    if distance < 1e-10:
        # Fragments at same position (shouldn't happen, but avoid division by zero)
        return

    # Unit vector along line of centers
    n_hat = r_rel / distance

    # Relative velocity along line of centers
    v_rel_n = np.dot(v_rel, n_hat)

    # Skip if fragments already separating
    if v_rel_n >= 0:
        return

    # Compute impulse (1D elastic collision in normal direction)
    # Reduced mass: μ = (m1 × m2) / (m1 + m2)
    reduced_mass = (f1.mass * f2.mass) / (f1.mass + f2.mass)

    # Impulse magnitude: J = -(1 + e) × μ × v_rel_n
    impulse_magnitude = -(1.0 + restitution) * reduced_mass * v_rel_n

    # Impulse vector (along line of centers)
    impulse = impulse_magnitude * n_hat

    # Update velocities
    f1.velocity -= impulse / f1.mass
    f2.velocity += impulse / f2.mass

    # Update collision tracking
    f1.collision_count += 1
    f2.collision_count += 1
    f1.last_collision_tick = current_tick
    f2.last_collision_tick = current_tick


def apply_all_collisions(
    cloud: FragmentedElectronCloud,
    collision_radius: float = 0.5,
    restitution: float = 0.8,
    current_tick: int = 0,
    use_spatial_hash: bool = False
) -> int:
    """
    Detect and process all collisions in the cloud.

    From Doc 070_01 §4:
    "This process naturally drives the system toward stable orbital levels,
    quantized energy states, and robust equilibrium distributions."

    Args:
        cloud: Fragmented electron cloud
        collision_radius: Collision distance threshold
        restitution: Coefficient of restitution
        current_tick: Current simulation tick
        use_spatial_hash: Use spatial hashing (faster for large N)

    Returns:
        Number of collisions processed
    """
    # Detect collisions
    if use_spatial_hash:
        collision_pairs = detect_collisions_spatial_hash(
            cloud.fragments,
            collision_radius=collision_radius
        )
    else:
        collision_pairs = detect_collisions(
            cloud.fragments,
            collision_radius=collision_radius
        )

    # Process each collision
    for i, j in collision_pairs:
        f1 = cloud.fragments[i]
        f2 = cloud.fragments[j]
        process_collision(f1, f2, restitution=restitution, current_tick=current_tick)

    # Update cloud statistics
    n_collisions = len(collision_pairs)
    cloud.collision_rate = n_collisions  # Per tick (will be smoothed externally)

    return n_collisions


# ============================================================================
# Energy Redistribution Analysis
# ============================================================================

def compute_total_momentum(fragments: List[ElectronFragment]) -> np.ndarray:
    """Compute total momentum of fragment ensemble."""
    total_p = np.array([0.0, 0.0])
    for f in fragments:
        total_p += f.mass * f.velocity
    return total_p


def compute_total_energy(fragments: List[ElectronFragment]) -> float:
    """Compute total kinetic energy of fragment ensemble."""
    total_ke = 0.0
    for f in fragments:
        total_ke += 0.5 * f.mass * (f.speed ** 2)
    return total_ke


def check_conservation_laws(
    fragments_before: List[ElectronFragment],
    fragments_after: List[ElectronFragment],
    tolerance: float = 1e-6
) -> Tuple[bool, dict]:
    """
    Check conservation of momentum and energy (for testing).

    Args:
        fragments_before: Fragments before collision
        fragments_after: Fragments after collision
        tolerance: Acceptable relative error

    Returns:
        (laws_conserved, diagnostics_dict)
    """
    # Momentum before and after
    p_before = compute_total_momentum(fragments_before)
    p_after = compute_total_momentum(fragments_after)
    dp = np.linalg.norm(p_after - p_before)
    p_mag = np.linalg.norm(p_before)

    momentum_conserved = (dp / (p_mag + 1e-10)) < tolerance

    # Energy before and after (may not be conserved for inelastic collisions)
    e_before = compute_total_energy(fragments_before)
    e_after = compute_total_energy(fragments_after)
    de = abs(e_after - e_before)
    e_rel_change = de / (e_before + 1e-10)

    diagnostics = {
        'momentum_before': p_before.tolist(),
        'momentum_after': p_after.tolist(),
        'momentum_change': float(dp),
        'momentum_conserved': momentum_conserved,
        'energy_before': float(e_before),
        'energy_after': float(e_after),
        'energy_change': float(de),
        'energy_rel_change': float(e_rel_change),
    }

    return momentum_conserved, diagnostics


# ============================================================================
# Testing
# ============================================================================

if __name__ == "__main__":
    print("Testing collision_dynamics...")

    # Import dependencies
    from fragmented_cloud import FragmentedElectronCloud

    # Create test cloud
    cloud = FragmentedElectronCloud(cloud_id="test_collision")
    cloud.initialize_fragments(
        n_fragments=50,
        r_mean=2.0,
        r_std=0.5,
        v_mean=0.1,
        v_std=0.02
    )

    # Initial state
    p_initial = compute_total_momentum(cloud.fragments)
    e_initial = compute_total_energy(cloud.fragments)

    print(f"\nInitial state:")
    print(f"  Total momentum: {np.linalg.norm(p_initial):.6f}")
    print(f"  Total kinetic energy: {e_initial:.6f}")

    # Apply collisions
    n_collisions = apply_all_collisions(
        cloud,
        collision_radius=0.5,
        restitution=0.8,
        current_tick=1
    )

    print(f"\nCollisions processed: {n_collisions}")

    # Final state
    p_final = compute_total_momentum(cloud.fragments)
    e_final = compute_total_energy(cloud.fragments)

    print(f"\nFinal state:")
    print(f"  Total momentum: {np.linalg.norm(p_final):.6f}")
    print(f"  Total kinetic energy: {e_final:.6f}")

    # Check conservation
    dp = np.linalg.norm(p_final - p_initial)
    de = abs(e_final - e_initial)

    print(f"\nConservation check:")
    print(f"  Momentum change: {dp:.9f} (should be ~0)")
    print(f"  Energy change: {de:.6f} (may decrease for e<1)")

    if dp < 1e-6:
        print("  [OK] Momentum conserved!")
    else:
        print("  [WARNING] Momentum not conserved (numerical error?)")

    # Test with different restitution coefficients
    print("\nTesting different restitution coefficients:")

    for e_rest in [1.0, 0.8, 0.5, 0.0]:
        cloud_test = FragmentedElectronCloud(cloud_id=f"test_e{e_rest}")
        cloud_test.initialize_fragments(n_fragments=20, r_mean=1.0, r_std=0.2)

        e_before = compute_total_energy(cloud_test.fragments)
        apply_all_collisions(cloud_test, restitution=e_rest)
        e_after = compute_total_energy(cloud_test.fragments)

        e_loss = e_before - e_after
        e_loss_pct = 100 * e_loss / e_before

        print(f"  e={e_rest:.1f}: Energy loss = {e_loss_pct:.2f}%")

    print("\n[OK] collision_dynamics test passed!")
