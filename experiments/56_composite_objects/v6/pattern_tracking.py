"""
Pattern Tracking - Center-of-Mass Detection for Field Patterns

Tracks actual field center-of-mass positions, not static initial coordinates.
Corrects the measurement flaw where 0.0% drift was artificial.

Key functions:
- compute_field_center_of_mass(): Finds actual COM from grid field values
- track_pattern_positions(): Updates all pattern positions based on field COM
- compute_pattern_drift_statistics(): Measures real spatial drift

Author: V6 Pattern Tracking Fix
Date: 2026-01-25
"""

import numpy as np
import math
from typing import List, Dict, Tuple
from planck_grid import PlanckGrid
from sample_cell import PatternInstance


def compute_field_center_of_mass(
    grid: PlanckGrid,
    search_center_x: int,
    search_center_y: int,
    search_radius: int = 15
) -> Tuple[float, float, float]:
    """
    Compute field-weighted center-of-mass in a local region.

    Args:
        grid: PlanckGrid with field values
        search_center_x: Center of search region (Planck cells)
        search_center_y: Center of search region (Planck cells)
        search_radius: Radius of search region (Planck cells)

    Returns:
        Tuple of (com_x, com_y, total_field_energy) where:
        - com_x, com_y: Field-weighted center-of-mass coordinates
        - total_field_energy: Sum of absolute field values in region
    """
    # Define search bounds (clamp to grid)
    x_min = max(0, search_center_x - search_radius)
    x_max = min(grid.width, search_center_x + search_radius + 1)
    y_min = max(0, search_center_y - search_radius)
    y_max = min(grid.height, search_center_y + search_radius + 1)

    # Accumulate weighted position and total energy
    weighted_x = 0.0
    weighted_y = 0.0
    total_energy = 0.0

    for y in range(y_min, y_max):
        for x in range(x_min, x_max):
            field_value = grid.get_cell(x, y)
            abs_field = abs(field_value)

            if abs_field > 0:
                weighted_x += x * abs_field
                weighted_y += y * abs_field
                total_energy += abs_field

    # Compute center-of-mass
    if total_energy > 0:
        com_x = weighted_x / total_energy
        com_y = weighted_y / total_energy
    else:
        # No field found - return search center as fallback
        com_x = float(search_center_x)
        com_y = float(search_center_y)

    return (com_x, com_y, total_energy)


def track_pattern_positions(
    grid: PlanckGrid,
    patterns: List[PatternInstance],
    search_radius: int = 15
) -> None:
    """
    Update all pattern positions based on actual field center-of-mass.

    This MODIFIES the PatternInstance objects in-place, updating their
    origin_x and origin_y coordinates to match the current field COM.

    Args:
        grid: PlanckGrid with current field state
        patterns: List of PatternInstance objects to update
        search_radius: Radius around current position to search for COM
    """
    for pattern in patterns:
        # Current position (may be outdated)
        current_center_x = pattern.sample.center_x
        current_center_y = pattern.sample.center_y

        # Compute actual field center-of-mass
        com_x, com_y, energy = compute_field_center_of_mass(
            grid,
            int(current_center_x),
            int(current_center_y),
            search_radius
        )

        # Update pattern origin to match COM
        # origin_x/y is top-left corner, center is origin + size//2
        pattern.sample.origin_x = int(round(com_x - pattern.sample.size // 2))
        pattern.sample.origin_y = int(round(com_y - pattern.sample.size // 2))


def compute_pattern_drift_statistics(
    patterns: List[PatternInstance],
    grid: PlanckGrid,
    initial_positions: List[Tuple[float, float]]
) -> Dict[str, float]:
    """
    Compute drift statistics from actual field positions vs initial positions.

    Args:
        patterns: List of PatternInstance with CURRENT field-tracked positions
        grid: PlanckGrid (for center reference)
        initial_positions: List of (x, y) tuples with INITIAL field COM positions

    Returns:
        Dict with drift statistics:
        - r_mean_initial: Mean radius from grid center at t=0
        - r_mean_current: Mean radius from grid center now
        - r_drift_percent: Percent change in mean radius
        - com_drift_mean: Mean displacement from initial COM (Planck cells)
        - com_drift_max: Maximum displacement from initial COM (Planck cells)
    """
    center_x = grid.width // 2
    center_y = grid.height // 2

    # Current positions and radii
    current_radii = []
    com_displacements = []

    for i, pattern in enumerate(patterns):
        # Current position (field-tracked COM)
        curr_x = pattern.sample.center_x
        curr_y = pattern.sample.center_y

        # Radius from grid center
        dx = curr_x - center_x
        dy = curr_y - center_y
        r = math.sqrt(dx*dx + dy*dy)
        current_radii.append(r)

        # Displacement from initial COM
        if i < len(initial_positions):
            init_x, init_y = initial_positions[i]
            disp_x = curr_x - init_x
            disp_y = curr_y - init_y
            displacement = math.sqrt(disp_x*disp_x + disp_y*disp_y)
            com_displacements.append(displacement)

    # Initial radii (from saved initial positions)
    initial_radii = []
    for init_x, init_y in initial_positions:
        dx = init_x - center_x
        dy = init_y - center_y
        r = math.sqrt(dx*dx + dy*dy)
        initial_radii.append(r)

    # Compute statistics
    r_mean_initial = float(np.mean(initial_radii)) if initial_radii else 0.0
    r_mean_current = float(np.mean(current_radii)) if current_radii else 0.0

    if r_mean_initial > 0:
        r_drift_percent = abs(r_mean_current - r_mean_initial) / r_mean_initial * 100
    else:
        r_drift_percent = 0.0

    com_drift_mean = float(np.mean(com_displacements)) if com_displacements else 0.0
    com_drift_max = float(np.max(com_displacements)) if com_displacements else 0.0

    return {
        "r_mean_initial": r_mean_initial,
        "r_mean_current": r_mean_current,
        "r_drift_percent": r_drift_percent,
        "com_drift_mean": com_drift_mean,
        "com_drift_max": com_drift_max,
        "r_std_current": float(np.std(current_radii)) if current_radii else 0.0,
    }


def save_initial_pattern_positions(
    patterns: List[PatternInstance]
) -> List[Tuple[float, float]]:
    """
    Save initial pattern center positions for drift calculation.

    Call this ONCE at t=0 after initializing patterns.

    Args:
        patterns: List of PatternInstance objects

    Returns:
        List of (center_x, center_y) tuples for each pattern
    """
    return [(float(p.sample.center_x), float(p.sample.center_y)) for p in patterns]


def get_pattern_field_energies(
    grid: PlanckGrid,
    patterns: List[PatternInstance],
    search_radius: int = 7
) -> List[float]:
    """
    Get total field energy around each pattern's current position.

    Args:
        grid: PlanckGrid with field values
        patterns: List of PatternInstance objects
        search_radius: Radius to sum field energy

    Returns:
        List of total field energy for each pattern
    """
    energies = []

    for pattern in patterns:
        center_x = pattern.sample.center_x
        center_y = pattern.sample.center_y

        _, _, energy = compute_field_center_of_mass(
            grid,
            int(center_x),
            int(center_y),
            search_radius
        )

        energies.append(energy)

    return energies
