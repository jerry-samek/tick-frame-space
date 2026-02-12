"""
Orbital test process for V18 canvas substrate.

Implements OrbitalTestProcess with integer velocity and gradient-based
acceleration, plus helpers for planet and ring process creation.

Part of Experiment 51: V10 orbital dynamics on V18 canvas substrate.
Tests whether PDE-free gamma accumulation can support orbital mechanics.

FORBIDDEN: No scipy, no Lorentz factor, no continuous positions,
no analytical gravitational profiles.

Date: February 2026
"""

import sys
import math
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

# Import V18 canvas and process
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "56_composite_objects"))
from v18 import Canvas3D_V18, Pos3D, SimpleDegenerateProcess


@dataclass
class TrajectoryPoint:
    """Record of process state at one tick."""
    tick: int
    position: Tuple[int, int, int]
    velocity: Tuple[int, int, int]
    distance_from_origin: float
    local_gamma: float
    gradient_mag: float
    skipped: bool


def get_smoothed_gradient(
    canvas: Canvas3D_V18,
    pos: Pos3D,
    sample_radius: int = 5,
) -> Tuple[float, float, float]:
    """Long-range gradient using local gamma sums at offset hemispheres.

    Standard get_gradient() samples pos+-1 per axis, which gives zero gradient
    at distances where no paint exists nearby. This function samples larger
    neighborhoods to detect mass asymmetry at any distance.

    Args:
        canvas: V18 canvas with gamma field
        pos: Position to compute gradient at
        sample_radius: Radius of sampling spheres and offset distance

    Returns:
        (gx, gy, 0.0) gradient components (2D restriction, gz=0)
    """
    gx = (
        canvas.get_local_gamma_sum(
            (pos[0] + sample_radius, pos[1], pos[2]), sample_radius
        )
        - canvas.get_local_gamma_sum(
            (pos[0] - sample_radius, pos[1], pos[2]), sample_radius
        )
    )
    gy = (
        canvas.get_local_gamma_sum(
            (pos[0], pos[1] + sample_radius, pos[2]), sample_radius
        )
        - canvas.get_local_gamma_sum(
            (pos[0], pos[1] - sample_radius, pos[2]), sample_radius
        )
    )
    # 2D restriction: no z-gradient
    return (gx, gy, 0.0)


class OrbitalTestProcess:
    """Test process with integer velocity for orbital dynamics testing.

    Standalone process (NOT a CompositeProcess subclass) with explicit
    velocity, gradient-based acceleration, per-component speed clamping,
    skip-based time dilation, and full trajectory recording.

    Physics:
    - Acceleration = sign(gradient) per axis (integer, from canvas gradient)
    - Velocity clamped per-component to [-max_speed, max_speed]
    - Skip check based on local gamma (time dilation)
    - When skipped: no velocity update, no movement, no painting
    - Paint single cell at position each active tick
    """

    def __init__(
        self,
        process_id: int,
        center: Pos3D,
        velocity: Tuple[int, int, int],
        label: str,
        max_speed: int = 1,
        skip_sensitivity: float = 0.1,
        use_smoothed_gradient: bool = False,
        gradient_sample_radius: int = 5,
    ):
        self.process_id = process_id
        self.center = center
        self.velocity = velocity
        self.label = label
        self.max_speed = max_speed
        self.skip_sensitivity = skip_sensitivity
        self.use_smoothed_gradient = use_smoothed_gradient
        self.gradient_sample_radius = gradient_sample_radius

        # Store initial state for results
        self.initial_position = center
        self.initial_velocity = velocity

        self.trajectory: List[TrajectoryPoint] = []
        self.acts_count = 0
        self.skips_count = 0

    def step(self, canvas: Canvas3D_V18, current_tick: int) -> bool:
        """Execute one tick of orbital process.

        Args:
            canvas: Shared V18 canvas
            current_tick: Current simulation tick number

        Returns:
            True (process always continues)
        """
        # 1. Read gradient (standard or smoothed)
        if self.use_smoothed_gradient:
            grad = get_smoothed_gradient(
                canvas, self.center, self.gradient_sample_radius
            )
        else:
            grad = canvas.get_gradient(self.center)

        grad_mag = math.sqrt(sum(g * g for g in grad))

        # 2. Skip check - BEFORE any state update
        # When skipped, entire tick is frozen (no velocity update, no move)
        gamma_cost = canvas.get_effective_gamma(self.center, local_radius=3)
        skip_prob = gamma_cost * self.skip_sensitivity

        if np.random.random() < skip_prob:
            self.skips_count += 1
            dist = math.sqrt(
                self.center[0] ** 2 + self.center[1] ** 2 + self.center[2] ** 2
            )
            self.trajectory.append(TrajectoryPoint(
                tick=current_tick,
                position=self.center,
                velocity=self.velocity,
                distance_from_origin=dist,
                local_gamma=canvas.get_local_gamma_sum(self.center, 3),
                gradient_mag=grad_mag,
                skipped=True,
            ))
            return True

        # 3. Acceleration from gradient (integer, sign only)
        accel = (
            int(np.sign(grad[0])) if grad[0] != 0 else 0,
            int(np.sign(grad[1])) if grad[1] != 0 else 0,
            0,  # 2D restriction
        )

        # 4. Update velocity
        vx = self.velocity[0] + accel[0]
        vy = self.velocity[1] + accel[1]

        # 5. Per-component speed clamp
        vx = max(-self.max_speed, min(self.max_speed, vx))
        vy = max(-self.max_speed, min(self.max_speed, vy))
        self.velocity = (vx, vy, 0)

        # 6. Move
        self.center = (
            self.center[0] + vx,
            self.center[1] + vy,
            0,
        )

        # 7. Paint at new position
        canvas.paint_imprint(self.process_id, {(0, 0, 0): 1.0}, self.center)

        # 8. Record trajectory point
        self.acts_count += 1
        dist = math.sqrt(
            self.center[0] ** 2 + self.center[1] ** 2 + self.center[2] ** 2
        )
        self.trajectory.append(TrajectoryPoint(
            tick=current_tick,
            position=self.center,
            velocity=self.velocity,
            distance_from_origin=dist,
            local_gamma=canvas.get_local_gamma_sum(self.center, 3),
            gradient_mag=grad_mag,
            skipped=False,
        ))

        return True


def create_planet_processes(
    count: int,
    spread_radius: int = 3,
    seed: int = 42,
) -> List[SimpleDegenerateProcess]:
    """Create planet processes distributed near origin in 2D (z=0).

    Args:
        count: Number of processes to create
        spread_radius: Max distance from origin for initial placement
        seed: Random seed for reproducible placement

    Returns:
        List of SimpleDegenerateProcess instances
    """
    rng = np.random.default_rng(seed)
    processes = []
    for i in range(count):
        x = int(rng.integers(-spread_radius, spread_radius + 1))
        y = int(rng.integers(-spread_radius, spread_radius + 1))
        p = SimpleDegenerateProcess(process_id=i, center=(x, y, 0))
        processes.append(p)
    return processes


def create_ring_processes(
    start_id: int,
    radius: int,
    count: int = 10,
) -> List[SimpleDegenerateProcess]:
    """Place processes equally spaced on circle of given radius, z=0.

    Args:
        start_id: Starting process ID
        radius: Ring radius from origin
        count: Number of processes on ring

    Returns:
        List of SimpleDegenerateProcess instances
    """
    processes = []
    for i in range(count):
        angle = 2 * math.pi * i / count
        x = int(round(radius * math.cos(angle)))
        y = int(round(radius * math.sin(angle)))
        p = SimpleDegenerateProcess(
            process_id=start_id + i,
            center=(x, y, 0),
        )
        processes.append(p)
    return processes
