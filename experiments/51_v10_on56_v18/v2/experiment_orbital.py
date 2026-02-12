"""
V18.1 Orbital Dynamics Experiment — with pressure-based gamma spreading.

Tests whether stable orbits emerge from V18 canvas substrate when local
pressure equalization (spread_gamma) is added. Single change from V1:
gamma-rich cells share with gamma-poor neighbors at 1/6 per neighbor per tick.

Usage:
    python experiment_orbital.py --planet-count 200 --speed-limit 5 --formation-ticks 500 --orbital-ticks 2000
    python experiment_orbital.py --planet-count 200 --speed-limit 5 --formation-ticks 500 --orbital-ticks 2000 --accumulator
    python experiment_orbital.py --planet-count 200 --speed-limit 5 --formation-ticks 500 --orbital-ticks 2000 --no-spreading
    python experiment_orbital.py --analytical --discrete --float-velocity --speed-limit 5 --orbital-ticks 2000

FORBIDDEN: No scipy, no Lorentz factor.
Note: float-velocity mode uses continuous velocity with integer lattice positions.

Date: February 2026
"""

import sys
import json
import math
import time
import argparse
import numpy as np
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple

# Import V18.1 canvas
from canvas_v18_1 import Canvas3D_V18_1

# Import V18 process
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "56_composite_objects"))
from v18 import SimpleDegenerateProcess, Pos3D

# Import reusable components from v1
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "v1"))
from orbital_process import (
    OrbitalTestProcess,
    TrajectoryPoint,
    get_smoothed_gradient,
    create_planet_processes,
    create_ring_processes,
)


class OrbitalTestProcess3D(OrbitalTestProcess):
    """OrbitalTestProcess with full 3D support (no z=0 restriction).

    The V1 OrbitalTestProcess hardcodes z=0 for 2D-only testing.
    This subclass enables out-of-plane motion (needed for T5).
    """

    def step(self, canvas, current_tick):
        """Execute one tick with 3D sign-only acceleration."""
        # 1. Read gradient (always use canvas.get_gradient for 3D)
        grad = canvas.get_gradient(self.center)
        grad_mag = math.sqrt(sum(g * g for g in grad))

        # 2. Skip check
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
                local_gamma=canvas.get_gamma(self.center),
                gradient_mag=grad_mag,
                skipped=True,
            ))
            return True

        # 3. Acceleration from gradient (integer, sign only, 3D)
        accel = tuple(
            int(np.sign(g)) if g != 0 else 0
            for g in grad
        )

        # 4. Update velocity (3D)
        vx = max(-self.max_speed, min(self.max_speed, self.velocity[0] + accel[0]))
        vy = max(-self.max_speed, min(self.max_speed, self.velocity[1] + accel[1]))
        vz = max(-self.max_speed, min(self.max_speed, self.velocity[2] + accel[2]))
        self.velocity = (vx, vy, vz)

        # 5. Move
        self.center = (
            self.center[0] + vx,
            self.center[1] + vy,
            self.center[2] + vz,
        )

        # 6. Record trajectory (no painting — test particle approximation)
        self.acts_count += 1
        dist = math.sqrt(
            self.center[0] ** 2 + self.center[1] ** 2 + self.center[2] ** 2
        )
        self.trajectory.append(TrajectoryPoint(
            tick=current_tick,
            position=self.center,
            velocity=self.velocity,
            distance_from_origin=dist,
            local_gamma=canvas.get_gamma(self.center),
            gradient_mag=grad_mag,
            skipped=False,
        ))

        return True


class OrbitalTestProcessAccumulator(OrbitalTestProcess):
    """OrbitalTestProcess with fractional velocity accumulator (v18_04 spec).

    Accumulates raw gradient vector directly. Integer acceleration fires
    only when accumulator crosses integer boundary. Preserves angular
    momentum because radial gradient doesn't affect tangential accumulator.

    Key difference from sign-only: gradient MAGNITUDE matters.
    At r=30 (grad~0.01), accumulator fires every ~100 ticks.
    At r=5 (grad~0.5), accumulator fires every ~2 ticks.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.accel_accumulator = (0.0, 0.0, 0.0)

    def step(self, canvas, current_tick):
        """Execute one tick with raw gradient accumulator."""
        # 1. Read gradient (6 dict lookups)
        grad = canvas.get_gradient(self.center)
        grad_mag = math.sqrt(sum(g * g for g in grad))

        # 2. Skip check — deterministic, only in very high gamma
        gamma_local = canvas.get_gamma(self.center)
        if gamma_local * 0.001 >= 1.0:
            self.skips_count += 1
            dist = math.sqrt(
                self.center[0] ** 2 + self.center[1] ** 2 + self.center[2] ** 2
            )
            self.trajectory.append(TrajectoryPoint(
                tick=current_tick,
                position=self.center,
                velocity=self.velocity,
                distance_from_origin=dist,
                local_gamma=gamma_local,
                gradient_mag=grad_mag,
                skipped=True,
            ))
            return True

        # 3. Accumulate raw gradient (not normalized, not capped)
        if grad_mag > 0:
            self.accel_accumulator = (
                self.accel_accumulator[0] + grad[0],
                self.accel_accumulator[1] + grad[1],
                self.accel_accumulator[2] + grad[2],
            )

        # 4. Extract integer part (fires when accumulator crosses threshold)
        int_accel = (
            int(self.accel_accumulator[0]),
            int(self.accel_accumulator[1]),
            int(self.accel_accumulator[2]),
        )

        # 5. Keep fractional remainder
        self.accel_accumulator = (
            self.accel_accumulator[0] - int_accel[0],
            self.accel_accumulator[1] - int_accel[1],
            self.accel_accumulator[2] - int_accel[2],
        )

        # 6. Update velocity
        vx = self.velocity[0] + int_accel[0]
        vy = self.velocity[1] + int_accel[1]
        vz = self.velocity[2] + int_accel[2]

        # 7. Per-component speed clamp
        vx = max(-self.max_speed, min(self.max_speed, vx))
        vy = max(-self.max_speed, min(self.max_speed, vy))
        vz = max(-self.max_speed, min(self.max_speed, vz))
        self.velocity = (vx, vy, vz)

        # 8. Move
        self.center = (
            self.center[0] + vx,
            self.center[1] + vy,
            self.center[2] + vz,
        )

        # 9. Record trajectory (no painting — test particle approximation)
        self.acts_count += 1
        dist = math.sqrt(
            self.center[0] ** 2 + self.center[1] ** 2 + self.center[2] ** 2
        )
        self.trajectory.append(TrajectoryPoint(
            tick=current_tick,
            position=self.center,
            velocity=self.velocity,
            distance_from_origin=dist,
            local_gamma=gamma_local,
            gradient_mag=grad_mag,
            skipped=False,
        ))

        return True


class OrbitalTestProcessFloat(OrbitalTestProcess):
    """Float velocity with Bresenham-style integer position stepping.

    Velocity is continuous (float). Position is integer (lattice).
    A position accumulator converts float velocity to integer steps.
    Gradient and gamma are trilinearly interpolated at the fractional
    position to eliminate staircase-potential energy errors.

    Integration: Leapfrog (kick-drift-kick), symplectic.

    Like V10's float velocity, but on V18's integer lattice.
    """

    def __init__(self, *args, dt=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        # Override velocity as float
        self.velocity = tuple(float(v) for v in self.velocity)
        # Position accumulator for sub-integer movement
        self.pos_accumulator = (0.0, 0.0, 0.0)
        # Integration timestep
        self.dt = dt
        # Energy tracking: E = 0.5*|v|^2 - gamma(r)
        self.energy_history = []  # [(tick, KE, PE, E_total)]
        # Radial acceleration diagnostics
        self.total_radial_accel = 0.0
        self.total_radial_decel = 0.0
        self.radial_accel_count = 0
        self.radial_decel_count = 0

    def _frac_coords(self):
        """Return (floor_pos, frac) for trilinear interpolation.

        pos_accumulator is in (-1, 1). The true fractional position is
        center + pos_accumulator. We decompose into integer floor and
        [0,1) fractional offsets for interpolation.
        """
        ax, ay, az = self.pos_accumulator
        cx, cy, cz = self.center

        if ax >= 0:
            x0, fx = cx, ax
        else:
            x0, fx = cx - 1, ax + 1.0
        if ay >= 0:
            y0, fy = cy, ay
        else:
            y0, fy = cy - 1, ay + 1.0
        if az >= 0:
            z0, fz = cz, az
        else:
            z0, fz = cz - 1, az + 1.0

        return (x0, y0, z0), (fx, fy, fz)

    def _interp_gamma(self, canvas):
        """Trilinearly interpolate gamma at fractional position."""
        (x0, y0, z0), (fx, fy, fz) = self._frac_coords()
        gv = canvas.get_gamma

        # 8 corner lookups
        g000 = gv((x0,   y0,   z0))
        g100 = gv((x0+1, y0,   z0))
        g010 = gv((x0,   y0+1, z0))
        g110 = gv((x0+1, y0+1, z0))
        g001 = gv((x0,   y0,   z0+1))
        g101 = gv((x0+1, y0,   z0+1))
        g011 = gv((x0,   y0+1, z0+1))
        g111 = gv((x0+1, y0+1, z0+1))

        # Interpolate along x, then y, then z
        c00 = g000 * (1 - fx) + g100 * fx
        c10 = g010 * (1 - fx) + g110 * fx
        c01 = g001 * (1 - fx) + g101 * fx
        c11 = g011 * (1 - fx) + g111 * fx
        c0 = c00 * (1 - fy) + c10 * fy
        c1 = c01 * (1 - fy) + c11 * fy
        return c0 * (1 - fz) + c1 * fz

    def _interp_gradient(self, canvas):
        """Trilinearly interpolate gradient at fractional position.

        Computes gradient at each of the 8 cube corners, then blends.
        Each get_gradient call does 6 dict lookups, so 48 total.
        """
        (x0, y0, z0), (fx, fy, fz) = self._frac_coords()
        gg = canvas.get_gradient

        corners = [
            gg((x0,   y0,   z0)),
            gg((x0+1, y0,   z0)),
            gg((x0,   y0+1, z0)),
            gg((x0+1, y0+1, z0)),
            gg((x0,   y0,   z0+1)),
            gg((x0+1, y0,   z0+1)),
            gg((x0,   y0+1, z0+1)),
            gg((x0+1, y0+1, z0+1)),
        ]

        result = []
        for i in range(3):
            c00 = corners[0][i] * (1 - fx) + corners[1][i] * fx
            c10 = corners[2][i] * (1 - fx) + corners[3][i] * fx
            c01 = corners[4][i] * (1 - fx) + corners[5][i] * fx
            c11 = corners[6][i] * (1 - fx) + corners[7][i] * fx
            c0 = c00 * (1 - fy) + c10 * fy
            c1 = c01 * (1 - fy) + c11 * fy
            result.append(c0 * (1 - fz) + c1 * fz)

        return tuple(result)

    def step(self, canvas, current_tick):
        """Execute one tick with leapfrog + trilinear interpolation.

        KDK leapfrog with gradient/gamma interpolated at the true
        fractional position (center + pos_accumulator), not snapped
        to integer lattice.
        """
        dt = self.dt
        half_dt = dt * 0.5

        # 1. KICK: half-step velocity using interpolated gradient
        grad = self._interp_gradient(canvas)
        grad_mag = math.sqrt(sum(g * g for g in grad))

        v_half = (
            self.velocity[0] + grad[0] * half_dt,
            self.velocity[1] + grad[1] * half_dt,
            self.velocity[2] + grad[2] * half_dt,
        )

        # 2. DRIFT: full-step position using half-step velocity
        self.pos_accumulator = (
            self.pos_accumulator[0] + v_half[0] * dt,
            self.pos_accumulator[1] + v_half[1] * dt,
            self.pos_accumulator[2] + v_half[2] * dt,
        )
        int_step = (
            int(self.pos_accumulator[0]),
            int(self.pos_accumulator[1]),
            int(self.pos_accumulator[2]),
        )
        self.pos_accumulator = (
            self.pos_accumulator[0] - int_step[0],
            self.pos_accumulator[1] - int_step[1],
            self.pos_accumulator[2] - int_step[2],
        )
        self.center = (
            self.center[0] + int_step[0],
            self.center[1] + int_step[1],
            self.center[2] + int_step[2],
        )

        # 3. KICK: half-step velocity using interpolated gradient at NEW pos
        grad2 = self._interp_gradient(canvas)

        self.velocity = (
            v_half[0] + grad2[0] * half_dt,
            v_half[1] + grad2[1] * half_dt,
            v_half[2] + grad2[2] * half_dt,
        )

        # 4. Speed limit by vector normalization (preserves direction)
        speed = math.sqrt(sum(v * v for v in self.velocity))
        if speed > self.max_speed:
            scale = self.max_speed / speed
            self.velocity = tuple(v * scale for v in self.velocity)
            speed = self.max_speed

        # 5. Radial acceleration diagnostics
        x, y, z = self.center
        ax, ay, az = self.pos_accumulator
        rx, ry, rz = x + ax, y + ay, z + az
        r = math.sqrt(rx * rx + ry * ry + rz * rz)
        if r > 0.1:
            r_hat = (rx / r, ry / r, rz / r)
            avg_grad = ((grad[0] + grad2[0]) * 0.5,
                        (grad[1] + grad2[1]) * 0.5,
                        (grad[2] + grad2[2]) * 0.5)
            grad_radial = sum(g * rh for g, rh in zip(avg_grad, r_hat))
            if grad_radial < 0:
                self.total_radial_accel += grad_radial * dt
                self.radial_accel_count += 1
            else:
                self.total_radial_decel += grad_radial * dt
                self.radial_decel_count += 1

        # 6. Energy tracking: E = 0.5*|v|^2 - gamma(pos) [interpolated]
        local_gamma = self._interp_gamma(canvas)
        KE = 0.5 * speed * speed
        PE = -local_gamma
        E_total = KE + PE
        self.energy_history.append((current_tick, KE, PE, E_total))

        # 7. Record trajectory
        self.acts_count += 1
        self.trajectory.append(TrajectoryPoint(
            tick=current_tick,
            position=self.center,
            velocity=self.velocity,
            distance_from_origin=r,
            local_gamma=local_gamma,
            gradient_mag=grad_mag,
            skipped=False,
        ))

        return True


def initialize_analytical_field(canvas, center=(0, 0, 0), total_mass=45000, r_max=60):
    """Plant a 1/r gamma field directly — skip spreading entirely.

    gamma(r) = total_mass / (4 * pi * r)  for r >= 1

    This is the steady-state solution of the 1/6 spreading rule.
    Used to isolate velocity mechanics from field shape problems.

    total_mass matches formation output (~45,000) for comparison.
    r_max=60 covers all test process starting positions (max r=50).
    """
    t0 = time.time()
    placed_total = 0.0

    for x in range(-r_max, r_max + 1):
        for y in range(-r_max, r_max + 1):
            for z in range(-r_max, r_max + 1):
                r = math.sqrt(x * x + y * y + z * z)
                if r < 1:
                    r = 1  # Avoid singularity at origin
                if r > r_max:
                    continue

                gamma = total_mass / (4 * math.pi * r)

                if gamma > 1e-6:  # Don't store negligible values
                    pos = (center[0] + x, center[1] + y, center[2] + z)
                    canvas.gamma[pos] = gamma
                    placed_total += gamma
                    canvas._update_bounds(pos)

    # Rescale so total matches target
    scale = total_mass / placed_total
    for pos in canvas.gamma:
        canvas.gamma[pos] *= scale

    elapsed = time.time() - t0
    total = sum(canvas.gamma.values())
    print(f"  Analytical 1/r field: {len(canvas.gamma)} cells, "
          f"total gamma = {total:.0f}, r_max = {r_max}, "
          f"init time = {elapsed:.1f}s")


def initialize_discrete_field(canvas, planet_positions, paint_ticks=250, r_max=60):
    """Initialize gamma as superposition of N individual 1/r steady-state fields.

    Each planet at position p_i contributes: gamma += paint_ticks / (4*pi*|pos - p_i|)
    This is the steady-state of the spreading rule for N discrete sources.

    Total gamma = N * paint_ticks (matching what formation would produce).
    No artificial mass inflation — mass emerges from entity count x paint duration.
    """
    t0 = time.time()
    n_planets = len(planet_positions)
    target_total = n_planets * paint_ticks

    # For cells far from all planets, use single point-mass approximation
    # when r > 10 * cluster_radius
    cluster_radius = max(
        math.sqrt(px * px + py * py + pz * pz)
        for px, py, pz in planet_positions
    ) if planet_positions else 0
    approx_threshold = max(10.0, 10.0 * cluster_radius)

    cells_computed = 0
    for x in range(-r_max, r_max + 1):
        for y in range(-r_max, r_max + 1):
            for z in range(-r_max, r_max + 1):
                r_sq = x * x + y * y + z * z
                if r_sq > r_max * r_max:
                    continue

                r_from_origin = math.sqrt(r_sq)

                # Far-field approximation: treat all planets as single point mass
                if r_from_origin > approx_threshold:
                    if r_from_origin < 1:
                        r_from_origin = 1
                    gamma = target_total / (4 * math.pi * r_from_origin)
                else:
                    # Near-field: sum individual contributions
                    gamma = 0.0
                    for px, py, pz in planet_positions:
                        dx, dy, dz = x - px, y - py, z - pz
                        r = math.sqrt(dx * dx + dy * dy + dz * dz)
                        if r < 1:
                            r = 1
                        gamma += paint_ticks / (4 * math.pi * r)

                if gamma > 1e-6:
                    pos = (x, y, z)
                    canvas.gamma[pos] = gamma
                    canvas._update_bounds(pos)
                    cells_computed += 1

    # Rescale so total gamma matches N * paint_ticks
    placed_total = sum(canvas.gamma.values())
    if placed_total > 0:
        scale = target_total / placed_total
        for pos in canvas.gamma:
            canvas.gamma[pos] *= scale

    elapsed = time.time() - t0
    total = sum(canvas.gamma.values())
    print(f"  Discrete field ({n_planets} sources, {paint_ticks} paint_ticks): "
          f"{cells_computed} cells, total gamma = {total:.0f}, "
          f"r_max = {r_max}, init time = {elapsed:.1f}s")


@dataclass
class ExperimentConfig:
    planet_count: int = 200
    planet_spread_radius: int = 3
    planet_formation_ticks: int = 500
    orbital_test_ticks: int = 2000
    speed_limit: int = 5
    enable_spreading: bool = True
    use_accumulator: bool = False
    use_float_velocity: bool = False
    use_analytical: bool = False
    use_discrete: bool = False
    analytical_r_max: int = 60
    analytical_total_mass: float = 45000.0
    approach: str = "both"  # "A", "B", or "both"
    approach_b_radii: list = None
    approach_b_per_ring: int = 10
    wake_decay_rate: float = 0.05
    dt: float = 1.0
    random_seed: int = 42
    snapshot_interval: int = 100

    def __post_init__(self):
        if self.approach_b_radii is None:
            self.approach_b_radii = [20, 30, 50]


class OrbitalExperiment:
    """V18.1 Orbital experiment with pressure-based gamma spreading.

    Phase 0: Planet formation — create gamma mass at origin
    Phase 1: Orbital tests — inject test processes and observe dynamics
    """

    def __init__(self, config: ExperimentConfig):
        self.config = config
        self.canvas = Canvas3D_V18_1()
        self.planet_processes = []
        self.orbital_processes = []
        self.pure_v18_processes = []
        self.approach_b_trajectories = {}
        self.tick_count = 0
        self.gamma_profile = {}
        self.gradient_analysis = []
        self.gamma_history = []  # Total gamma per snapshot for conservation check
        self.field_diagnostics = {}  # v18_03 field diagnostics

        np.random.seed(config.random_seed)

    def run(self):
        """Run the full experiment."""
        if self.config.use_analytical:
            if self.config.use_discrete:
                field_type = "Discrete N-source 1/r"
            else:
                field_type = "Analytical 1/r"
        elif self.config.enable_spreading:
            field_type = "V18.1 (spread)"
        else:
            field_type = "V18 (no spreading)"

        if self.config.use_float_velocity:
            mode = "float-velocity"
        elif self.config.use_accumulator:
            mode = "accumulator"
        else:
            mode = "sign-only"

        print("=" * 60)
        print(f"{field_type} Orbital Dynamics Experiment ({mode})")
        print("=" * 60)
        print(f"  field_type        = {field_type}")
        print(f"  speed_limit       = {self.config.speed_limit}")
        print(f"  velocity_mode     = {mode}")
        if self.config.use_float_velocity and self.config.dt != 1.0:
            print(f"  dt                = {self.config.dt}")
        print(f"  orbital_ticks     = {self.config.orbital_test_ticks}")
        print(f"  seed              = {self.config.random_seed}")
        if self.config.use_analytical:
            print(f"  analytical_r_max  = {self.config.analytical_r_max}")
            if not self.config.use_discrete:
                print(f"  analytical_mass   = {self.config.analytical_total_mass}")
            print(f"  use_discrete      = {self.config.use_discrete}")
        else:
            print(f"  planet_count      = {self.config.planet_count}")
            print(f"  enable_spreading  = {self.config.enable_spreading}")
            print(f"  formation_ticks   = {self.config.planet_formation_ticks}")
        print()

        if self.config.use_analytical:
            self._phase0_analytical()
        else:
            self._phase0_planet_formation()
        self._phase1_orbital_tests()
        self._save_results()

    def _phase0_analytical(self):
        """Phase 0 (analytical): Plant 1/r gamma field directly."""
        if self.config.use_discrete:
            print(f"--- Phase 0: Discrete N-source 1/r Field ---")
            # Create planet positions (same as formation would)
            rng = np.random.default_rng(self.config.random_seed)
            planet_positions = []
            for _ in range(self.config.planet_count):
                x = int(rng.integers(
                    -self.config.planet_spread_radius,
                    self.config.planet_spread_radius + 1,
                ))
                y = int(rng.integers(
                    -self.config.planet_spread_radius,
                    self.config.planet_spread_radius + 1,
                ))
                z = 0
                planet_positions.append((x, y, z))
            print(f"  {len(planet_positions)} planet positions within "
                  f"radius {self.config.planet_spread_radius}")
            initialize_discrete_field(
                self.canvas,
                planet_positions,
                paint_ticks=self.config.planet_formation_ticks // 2,
                r_max=self.config.analytical_r_max,
            )
        else:
            print(f"--- Phase 0: Analytical 1/r Field ---")
            initialize_analytical_field(
                self.canvas,
                total_mass=self.config.analytical_total_mass,
                r_max=self.config.analytical_r_max,
            )

        # Record profile and run diagnostics (same as formation)
        self.gamma_profile = self.canvas.get_radial_distribution()

        # Print gamma profile
        print(f"\n  Gamma radial profile (analytical 1/r):")
        sorted_radii = sorted(self.gamma_profile.keys())
        max_gamma = max(self.gamma_profile.values()) if self.gamma_profile else 1
        for r in sorted_radii[:30]:
            bar = "#" * min(60, int(self.gamma_profile[r] / max_gamma * 60))
            print(f"    r={r:3d}: {self.gamma_profile[r]:8.1f}  {bar}")
        if len(sorted_radii) > 30:
            print(f"    ... ({len(sorted_radii) - 30} more shells)")

        # Gradient analysis
        print(f"\n  Gradient analysis at test distances:")
        print(f"    {'r':>4s} | {'std_grad':>10s} | {'local_gamma':>12s}")
        print(f"    {'':->4s}-+-{'':->10s}-+-{'':->12s}")

        test_distances = [5, 10, 15, 20, 25, 30, 40, 50]
        for r in test_distances:
            pos = (r, 0, 0)
            grad = self.canvas.get_gradient(pos)
            grad_mag = math.sqrt(sum(g * g for g in grad))
            local_gamma = self.canvas.get_local_gamma_sum(pos, 3)

            self.gradient_analysis.append({
                "distance": r,
                "standard_gradient_mag": grad_mag,
                "local_gamma": local_gamma,
            })
            print(f"    {r:4d} | {grad_mag:10.6f} | {local_gamma:12.1f}")

        # Diagnostics
        self._log_gamma_profile()
        self._log_gradient_profile()

        print()

    def _phase0_planet_formation(self):
        """Phase 0: Create gamma mass at origin, then spread the field.

        Split into two sub-phases for performance:
        - Phase 0a: Paint-only (200 processes paint, no spreading) — fast
        - Phase 0b: Spread-only (no painting, just spreading) — wavefront-only work

        Separating paint from spread avoids the O(total_cells) per tick
        bottleneck where every painted cell creates wake that propagates
        through the entire field.
        """
        ticks = self.config.planet_formation_ticks
        # Split: half for painting, half for spreading
        paint_ticks = ticks // 2
        spread_ticks = ticks - paint_ticks

        print(f"--- Phase 0: Planet Formation ({ticks} ticks) ---")
        print(f"  Phase 0a: Painting ({paint_ticks} ticks)")
        print(f"  Phase 0b: Spreading ({spread_ticks} ticks)")

        self.planet_processes = create_planet_processes(
            self.config.planet_count,
            self.config.planet_spread_radius,
            self.config.random_seed,
        )
        print(f"  Created {len(self.planet_processes)} planet processes "
              f"within radius {self.config.planet_spread_radius}")

        # Phase 0a: Paint-only — build gamma mass at center
        t0 = time.time()
        for tick in range(paint_ticks):
            for p in self.planet_processes:
                p.step(self.canvas)
            self.tick_count += 1

            if (tick + 1) % self.config.snapshot_interval == 0:
                elapsed = time.time() - t0
                stats = self.canvas.get_statistics()
                rate = (tick + 1) / elapsed if elapsed > 0 else 0
                total_gamma = self.canvas.get_total_gamma()
                self.gamma_history.append({
                    "tick": tick + 1,
                    "total_gamma": total_gamma,
                })
                print(f"  Paint {tick + 1:5d}/{paint_ticks} "
                      f"({elapsed:6.1f}s, {rate:.0f} t/s) | "
                      f"cells={stats['painted_cells']:6d}, "
                      f"gamma={total_gamma:8.0f}, "
                      f"r_max={stats['r_max']:5.1f}")

        paint_elapsed = time.time() - t0
        print(f"  Paint phase done in {paint_elapsed:.1f}s, "
              f"gamma={self.canvas.get_total_gamma():.0f}, "
              f"cells={len(self.canvas.gamma)}")

        # Phase 0b: Spread-only — extend field via pressure equalization
        if self.config.enable_spreading:
            # Seed wake from current gamma (all painted cells need initial spreading)
            for pos in list(self.canvas.gamma.keys()):
                self.canvas.wake[pos] = self.canvas.gamma[pos]

            t0_spread = time.time()
            for tick in range(spread_ticks):
                self.canvas.spread_gamma()
                self.tick_count += 1

                if (tick + 1) % self.config.snapshot_interval == 0:
                    elapsed = time.time() - t0_spread
                    stats = self.canvas.get_statistics()
                    rate = (tick + 1) / elapsed if elapsed > 0 else 0
                    total_gamma = self.canvas.get_total_gamma()
                    wake_size = len(self.canvas.wake)
                    self.gamma_history.append({
                        "tick": paint_ticks + tick + 1,
                        "total_gamma": total_gamma,
                    })
                    print(f"  Spread {tick + 1:5d}/{spread_ticks} "
                          f"({elapsed:6.1f}s, {rate:.0f} t/s) | "
                          f"cells={stats['painted_cells']:6d}, "
                          f"gamma={total_gamma:8.0f}, "
                          f"r_max={stats['r_max']:5.1f}, "
                          f"wake={wake_size:6d}")

            spread_elapsed = time.time() - t0_spread
            print(f"  Spread phase done in {spread_elapsed:.1f}s")

        # Record gamma radial profile
        self.gamma_profile = self.canvas.get_radial_distribution()

        # Print gamma profile
        print(f"\n  Gamma radial profile (after {ticks} ticks of formation):")
        sorted_radii = sorted(self.gamma_profile.keys())
        max_gamma = max(self.gamma_profile.values()) if self.gamma_profile else 1
        for r in sorted_radii[:30]:
            bar = "#" * min(60, int(self.gamma_profile[r] / max_gamma * 60))
            print(f"    r={r:3d}: {self.gamma_profile[r]:8.1f}  {bar}")
        if len(sorted_radii) > 30:
            print(f"    ... ({len(sorted_radii) - 30} more shells)")

        # Gradient analysis at test distances
        print(f"\n  Gradient analysis at test distances:")
        print(f"    {'r':>4s} | {'std_grad':>10s} | {'smooth_grad':>12s} | {'local_gamma':>12s}")
        print(f"    {'':->4s}-+-{'':->10s}-+-{'':->12s}-+-{'':->12s}")

        test_distances = [5, 10, 15, 20, 25, 30, 40, 50]
        for r in test_distances:
            pos = (r, 0, 0)
            grad = self.canvas.get_gradient(pos)
            grad_mag = math.sqrt(sum(g * g for g in grad))
            smooth_grad = get_smoothed_gradient(self.canvas, pos, 30)
            smooth_mag = math.sqrt(sum(g * g for g in smooth_grad))
            local_gamma = self.canvas.get_local_gamma_sum(pos, 3)

            self.gradient_analysis.append({
                "distance": r,
                "standard_gradient_mag": grad_mag,
                "smoothed_gradient_mag": smooth_mag,
                "local_gamma": local_gamma,
            })
            print(f"    {r:4d} | {grad_mag:10.6f} | {smooth_mag:12.4f} | {local_gamma:12.1f}")

        # Key Phase 0 validation
        if self.config.enable_spreading:
            print(f"\n  Phase 0 validation (spreading enabled):")
            nonzero_std = sum(1 for g in self.gradient_analysis if g["standard_gradient_mag"] > 0)
            print(f"    Standard gradient nonzero at {nonzero_std}/{len(test_distances)} test distances")

            if len(self.gradient_analysis) >= 2:
                g10 = next((g for g in self.gradient_analysis if g["distance"] == 10), None)
                g30 = next((g for g in self.gradient_analysis if g["distance"] == 30), None)
                if g10 and g30:
                    if g10["standard_gradient_mag"] > g30["standard_gradient_mag"] > 0:
                        print(f"    Gradient decreases with distance: PASS")
                    elif g30["standard_gradient_mag"] == 0:
                        print(f"    Gradient at r=30 is ZERO (field hasn't reached)")
                    else:
                        print(f"    Gradient does NOT decrease with distance")

        # v18_03 Part 1.1: Gamma profile along +x axis with power law fit
        self._log_gamma_profile()

        # v18_03 Part 1.2: Gradient falloff verification
        self._log_gradient_profile()

        print()

    def _log_gamma_profile(self, center=(0, 0, 0)):
        """v18_03 Part 1.1: Sample gamma along +x axis, fit power law."""
        distances = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50]
        print("\n  === GAMMA PROFILE gamma(r) ===")
        print(f"  {'r':>4}  {'gamma':>12}  {'gradient_mag':>12}")

        gamma_at_r = {}
        for r in distances:
            pos = (center[0] + r, center[1], center[2])
            gamma = self.canvas.get_gamma(pos)
            grad = self.canvas.get_gradient(pos)
            grad_mag = math.sqrt(sum(g * g for g in grad))
            gamma_at_r[r] = gamma
            print(f"  {r:>4}  {gamma:>12.4f}  {grad_mag:>12.6f}")

        # Power law fit: log(gamma) vs log(r)
        fit_points = [(r, g) for r, g in gamma_at_r.items()
                      if r >= 5 and g > 0]
        self.field_diagnostics = {
            "gamma_at_r": {str(r): g for r, g in gamma_at_r.items()},
        }

        if len(fit_points) >= 2:
            log_r = [math.log(r) for r, _ in fit_points]
            log_g = [math.log(g) for _, g in fit_points]
            n = len(log_r)
            sum_x = sum(log_r)
            sum_y = sum(log_g)
            sum_xy = sum(x * y for x, y in zip(log_r, log_g))
            sum_xx = sum(x * x for x in log_r)
            denom = n * sum_xx - sum_x ** 2
            if abs(denom) > 1e-12:
                slope = (n * sum_xy - sum_x * sum_y) / denom
                print(f"\n  Power law fit: gamma ~ r^({slope:.3f})")
                print(f"    (1/r would be -1.000, 1/r^2 would be -2.000)")
                self.field_diagnostics["power_law_exponent"] = slope
            else:
                print(f"\n  Power law fit: degenerate (all same distance)")
        else:
            print(f"\n  Power law fit: not enough nonzero points (need >= 2 at r>=5)")

    def _log_gradient_profile(self, center=(0, 0, 0)):
        """v18_03 Part 1.2: Gradient falloff with ratio analysis."""
        distances = [5, 10, 15, 20, 25, 30, 40, 50]
        print("\n  === GRADIENT FALLOFF ===")
        print(f"  {'r':>4}  {'grad_mag':>12}  {'ratio_to_prev':>14}  {'expected_1/r2':>14}")

        prev_r = None
        prev_grad = None
        gradient_at_r = {}
        for r in distances:
            pos = (center[0] + r, center[1], center[2])
            grad = self.canvas.get_gradient(pos)
            grad_mag = math.sqrt(sum(g * g for g in grad))
            gradient_at_r[r] = grad_mag

            ratio_str = ""
            expected_str = ""
            if prev_r is not None and prev_grad > 0 and grad_mag > 0:
                ratio_str = f"{grad_mag / prev_grad:.4f}"
                expected_str = f"{(prev_r / r) ** 2:.4f}"

            print(f"  {r:>4}  {grad_mag:>12.6f}  {ratio_str:>14}  {expected_str:>14}")
            prev_r = r
            prev_grad = grad_mag

        self.field_diagnostics["gradient_at_r"] = {
            str(r): g for r, g in gradient_at_r.items()
        }
        stats = self.canvas.get_statistics()
        self.field_diagnostics["total_gamma"] = self.canvas.get_total_gamma()
        self.field_diagnostics["painted_cells"] = stats["painted_cells"]
        self.field_diagnostics["field_r_max"] = stats["r_max"]
        self.field_diagnostics["formation_ticks"] = self.config.planet_formation_ticks
        self.field_diagnostics["n_planets"] = self.config.planet_count

    def _phase1_orbital_tests(self):
        """Phase 1: Pure test-particle orbital dynamics on static field.

        No painting, no spreading, no wave propagation.
        Test processes just read gradients and move.
        """
        total_ticks = self.config.orbital_test_ticks
        print(f"--- Phase 1: Orbital Tests ({total_ticks} ticks) ---")
        print(f"  Static field — no painting, no spreading")

        if self.config.approach in ("A", "both"):
            self._create_approach_a_processes()

        print()
        t0 = time.time()
        for tick in range(total_ticks):
            current_tick = self.config.planet_formation_ticks + tick

            # Pure test-particle: read gradient, update velocity, move
            for op in self.orbital_processes:
                op.step(self.canvas, current_tick)

            self.tick_count += 1

            # v18_03 Part 1.4: Periodic summary every snapshot_interval ticks
            if (tick + 1) % self.config.snapshot_interval == 0:
                elapsed = time.time() - t0
                rate = (tick + 1) / elapsed if elapsed > 0 else 0

                print(f"\n  --- Tick {tick + 1}/{total_ticks} "
                      f"({elapsed:.1f}s, {rate:.0f} t/s) ---")
                has_energy = self.config.use_float_velocity
                if has_energy:
                    print(f"  {'ID':>4} {'r':>7} {'speed':>6} {'L_z':>8} "
                          f"{'angle':>7} {'KE':>8} {'PE':>8} {'E_tot':>8} "
                          f"{'status':>10}")
                else:
                    print(f"  {'ID':>4} {'r':>7} {'speed':>6} {'L_z':>8} "
                          f"{'angle':>7} {'skips':>6} {'acts':>6} {'status':>10}")

                for op in self.orbital_processes:
                    if not op.trajectory:
                        continue
                    x, y, z = op.center
                    r = math.sqrt(x * x + y * y + z * z)
                    vx, vy, vz = op.velocity
                    speed = math.sqrt(vx * vx + vy * vy + vz * vz)
                    L_z = x * vy - y * vx
                    angle = math.degrees(math.atan2(y, x))

                    if r < 3:
                        status = "COLLAPSED"
                    elif r > 100:
                        status = "ESCAPED"
                    elif speed < 0.01:
                        status = "STUCK"
                    else:
                        status = "ACTIVE"

                    if has_energy and hasattr(op, 'energy_history') and op.energy_history:
                        _, KE, PE, E_tot = op.energy_history[-1]
                        print(f"  {op.label:>4} {r:>7.1f} {speed:>6.3f} "
                              f"{L_z:>8.1f} {angle:>6.1f}d "
                              f"{KE:>8.5f} {PE:>8.5f} {E_tot:>8.5f} "
                              f"{status:>10}")
                    else:
                        print(f"  {op.label:>4} {r:>7.1f} {speed:>6.2f} "
                              f"{L_z:>8.1f} {angle:>6.1f}d "
                              f"{op.skips_count:>6} {op.acts_count:>6} "
                              f"{status:>10}")

        # Final status
        print(f"\n  Final orbital process status:")
        for op in self.orbital_processes:
            if op.trajectory:
                last = op.trajectory[-1]
                x, y, z = op.center
                vx, vy, vz = op.velocity
                speed = math.sqrt(vx * vx + vy * vy + vz * vz)
                L_z = x * vy - y * vx
                if self.config.use_float_velocity:
                    vel_str = f"({vx:.3f}, {vy:.3f}, {vz:.3f})"
                else:
                    vel_str = str(op.velocity)
                print(f"    {op.label}: r={last.distance_from_origin:.1f}, "
                      f"v={vel_str}, |v|={speed:.3f}, L_z={L_z:.1f}, "
                      f"acts={op.acts_count}, skips={op.skips_count}")

        # Energy diagnostics for float-velocity processes
        if self.config.use_float_velocity:
            print(f"\n  === ENERGY DIAGNOSTICS (E = 0.5*v^2 - gamma) ===")
            print(f"  {'ID':>4} {'E_init':>10} {'E_final':>10} {'dE':>10} "
                  f"{'dE/E0':>8} {'rad_in':>10} {'rad_out':>10} "
                  f"{'in_n':>6} {'out_n':>6}")
            for op in self.orbital_processes:
                if not hasattr(op, 'energy_history') or len(op.energy_history) < 2:
                    continue
                E0 = op.energy_history[0][3]
                Ef = op.energy_history[-1][3]
                dE = Ef - E0
                dE_frac = dE / abs(E0) if abs(E0) > 1e-12 else float('inf')
                print(f"  {op.label:>4} {E0:>10.5f} {Ef:>10.5f} {dE:>+10.5f} "
                      f"{dE_frac:>+8.3f} {op.total_radial_accel:>+10.4f} "
                      f"{op.total_radial_decel:>+10.4f} "
                      f"{op.radial_accel_count:>6} {op.radial_decel_count:>6}")

            # Per-process energy timeline (sample 10 points)
            print(f"\n  === ENERGY TIMELINE (sampled) ===")
            for op in self.orbital_processes:
                if not hasattr(op, 'energy_history') or len(op.energy_history) < 10:
                    continue
                n = len(op.energy_history)
                indices = [int(i * (n - 1) / 9) for i in range(10)]
                samples = [op.energy_history[i] for i in indices]
                vals = " ".join(f"{s[3]:+.5f}" for s in samples)
                print(f"    {op.label}: {vals}")

        print()

    def _create_approach_a_processes(self):
        """Create Approach A orbital test processes with velocity."""
        base_id = self.config.planet_count + 1000
        sl = self.config.speed_limit

        if self.config.use_float_velocity:
            ProcessClass = OrbitalTestProcessFloat
            mode_str = "float-velocity"
        elif self.config.use_accumulator:
            ProcessClass = OrbitalTestProcessAccumulator
            mode_str = "accumulator"
        else:
            ProcessClass = OrbitalTestProcess3D
            mode_str = "sign-only"

        if self.config.use_float_velocity:
            # Auto-compute v_circular from measured gradient at each distance
            test_specs = [
                ("T1", (30, 0, 0), "y", "Circular attempt r=30"),
                ("T2", (30, 0, 0), None, "Radial infall control"),
                ("T3", (20, 0, 0), "y", "Closer orbit r=20"),
                ("T4", (50, 0, 0), "y", "Farther orbit r=50"),
                ("T5", (30, 0, 0), "z", "Out-of-plane orbit"),
                ("T6", (40, 0, 0), "y", "Medium distance r=40"),
            ]

            configs = []
            print(f"\n  Auto-computing v_circular from measured gradient:")
            print(f"    {'ID':>4} {'r':>4} {'grad_mag':>10} {'v_circ':>8} {'dir':>4}")
            for label, pos, tang_dir, desc in test_specs:
                if tang_dir is None:
                    # Radial infall: zero velocity
                    vel = (0.0, 0.0, 0.0)
                    configs.append((label, pos, vel, desc))
                    print(f"    {label:>4} {int(math.sqrt(sum(p*p for p in pos))):>4} "
                          f"{'---':>10} {'0.000':>8} {'---':>4}")
                    continue

                r = math.sqrt(sum(p * p for p in pos))
                grad = self.canvas.get_gradient(pos)
                grad_mag = math.sqrt(sum(g * g for g in grad))

                if grad_mag > 1e-10:
                    # v_circ = sqrt(a_eff * r), where a_eff = grad * dt
                    v_circ = math.sqrt(grad_mag * self.config.dt * r)
                else:
                    v_circ = 0.1  # Fallback — position likely outside field
                    desc += " [NO GRADIENT]"

                if tang_dir == "y":
                    vel = (0.0, v_circ, 0.0)
                elif tang_dir == "z":
                    vel = (0.0, 0.0, v_circ)
                else:
                    vel = (0.0, v_circ, 0.0)

                configs.append((label, pos, vel, desc))
                print(f"    {label:>4} {r:>4.0f} {grad_mag:>10.6f} "
                      f"{v_circ:>8.4f} {tang_dir:>4}")

            print()
        else:
            # Integer velocity: scale tangential velocity
            v_tang = max(1, sl * 3 // 5) if sl > 1 else 1
            configs = [
                ("T1", (30, 0, 0), (0, v_tang, 0), "Circular attempt r=30"),
                ("T2", (30, 0, 0), (0, 0, 0),      "Radial infall control"),
                ("T3", (20, 0, 0), (0, v_tang, 0), "Closer orbit r=20"),
                ("T4", (50, 0, 0), (0, v_tang, 0), "Farther orbit r=50"),
                ("T5", (30, 0, 0), (0, 0, v_tang), "Out-of-plane orbit"),
                ("T6", (40, 0, 0), (0, v_tang, 0), "Medium distance r=40"),
            ]

        print(f"  Approach A: {len(configs)} orbital test processes "
              f"(max_speed={sl}, mode={mode_str})")

        for i, (label, pos, vel, desc) in enumerate(configs):
            extra_kwargs = {}
            if self.config.use_float_velocity:
                extra_kwargs["dt"] = self.config.dt
            op = ProcessClass(
                process_id=base_id + i,
                center=pos,
                velocity=vel,
                label=label,
                max_speed=sl,
                skip_sensitivity=0.1,
                use_smoothed_gradient=False,
                gradient_sample_radius=30,
                **extra_kwargs,
            )
            self.orbital_processes.append(op)
            if self.config.use_float_velocity:
                vel_str = f"({vel[0]:.4f}, {vel[1]:.4f}, {vel[2]:.4f})"
            else:
                vel_str = str(vel)
            print(f"    {label}: pos={pos}, vel={vel_str} - {desc}")

    def _create_approach_b_processes(self):
        """Create Approach B pure V18 ring processes."""
        base_id = self.config.planet_count + 2000
        total = 0
        for radius in self.config.approach_b_radii:
            ring = create_ring_processes(
                base_id + total,
                radius,
                self.config.approach_b_per_ring,
            )
            self.pure_v18_processes.extend(ring)
            total += len(ring)
            print(f"  Approach B: {len(ring)} processes on ring r={radius}")

    def _save_results(self):
        """Save experiment results to JSON."""
        results_dir = Path(__file__).parent / "results"
        results_dir.mkdir(exist_ok=True)

        results = {
            "config": {
                "planet_count": self.config.planet_count,
                "planet_spread_radius": self.config.planet_spread_radius,
                "planet_formation_ticks": self.config.planet_formation_ticks,
                "orbital_test_ticks": self.config.orbital_test_ticks,
                "speed_limit": self.config.speed_limit,
                "enable_spreading": self.config.enable_spreading,
                "use_accumulator": self.config.use_accumulator,
                "use_float_velocity": self.config.use_float_velocity,
                "use_analytical": self.config.use_analytical,
                "use_discrete": self.config.use_discrete,
                "approach": self.config.approach,
                "approach_b_radii": self.config.approach_b_radii,
                "approach_b_per_ring": self.config.approach_b_per_ring,
                "wake_decay_rate": self.config.wake_decay_rate,
                "random_seed": self.config.random_seed,
                "total_ticks": self.tick_count,
            },
            "gamma_profile": {
                str(k): v for k, v in sorted(self.gamma_profile.items())
            },
            "gradient_analysis": self.gradient_analysis,
            "gamma_history": self.gamma_history,
            "field_diagnostics": getattr(self, "field_diagnostics", {}),
            "approach_a": {},
            "canvas_stats": self.canvas.get_statistics(),
        }

        # Approach A trajectories
        for op in self.orbital_processes:
            results["approach_a"][op.label] = {
                "config": {
                    "start_position": list(op.initial_position),
                    "initial_velocity": list(op.initial_velocity),
                    "max_speed": op.max_speed,
                    "velocity_mode": "float" if self.config.use_float_velocity
                                     else "accumulator" if self.config.use_accumulator
                                     else "sign-only",
                },
                "acts": op.acts_count,
                "skips": op.skips_count,
                "trajectory": [
                    {
                        "tick": tp.tick,
                        "position": list(tp.position),
                        "velocity": list(tp.velocity),
                        "r": tp.distance_from_origin,
                        "local_gamma": tp.local_gamma,
                        "gradient_mag": tp.gradient_mag,
                        "skipped": tp.skipped,
                    }
                    for tp in op.trajectory
                ],
            }

        # Build filename from config
        sl = self.config.speed_limit
        if self.config.use_analytical:
            field = "discrete" if self.config.use_discrete else "analytical"
        elif self.config.enable_spreading:
            field = "spread"
        else:
            field = "nospread"
        if self.config.use_float_velocity:
            mode = "float"
        elif self.config.use_accumulator:
            mode = "accum"
        else:
            mode = "sign"
        filename = f"orbital_sl{sl}_{field}_{mode}_p{self.config.planet_count}.json"
        filepath = results_dir / filename

        with open(filepath, "w") as f:
            json.dump(results, f, indent=2)

        stats = results["canvas_stats"]
        print(f"Results saved to {filepath}")
        print(f"  Canvas: {stats['painted_cells']} cells, "
              f"{stats['total_gamma']:.0f} total gamma, "
              f"r_max={stats['r_max']:.1f}")
        print(f"  Approach A: {len(self.orbital_processes)} processes")


def main():
    parser = argparse.ArgumentParser(
        description="V18.1 Orbital Dynamics Experiment — "
                    "Tests orbital mechanics with pressure-based gamma spreading"
    )
    parser.add_argument(
        "--planet-count", type=int, default=200,
        help="Number of planet processes (default: 200)",
    )
    parser.add_argument(
        "--speed-limit", type=int, default=5,
        help="Max velocity per component in cells/tick (default: 5)",
    )
    parser.add_argument(
        "--formation-ticks", type=int, default=500,
        help="Ticks for planet formation phase (default: 500)",
    )
    parser.add_argument(
        "--orbital-ticks", type=int, default=2000,
        help="Ticks for orbital test phase (default: 2000)",
    )
    parser.add_argument(
        "--approach", choices=["A", "B", "both"], default="both",
        help="Which approach to run (default: both)",
    )
    parser.add_argument(
        "--no-spreading", action="store_true",
        help="Disable gamma spreading (control run, same as V1)",
    )
    parser.add_argument(
        "--accumulator", action="store_true",
        help="Use velocity accumulator instead of sign-only acceleration (Phase 2)",
    )
    parser.add_argument(
        "--float-velocity", action="store_true",
        help="Use float velocity with Bresenham integer position (Phase 5)",
    )
    parser.add_argument(
        "--analytical", action="store_true",
        help="Use analytical 1/r field instead of formation+spreading",
    )
    parser.add_argument(
        "--discrete", action="store_true",
        help="Use discrete N-source superposition instead of single point mass",
    )
    parser.add_argument(
        "--analytical-r-max", type=int, default=60,
        help="Radius of analytical field (default: 60)",
    )
    parser.add_argument(
        "--analytical-mass", type=float, default=45000.0,
        help="Total mass of analytical field (default: 45000)",
    )
    parser.add_argument(
        "--seed", type=int, default=42,
        help="Random seed (default: 42)",
    )
    parser.add_argument(
        "--dt", type=float, default=1.0,
        help="Integration timestep for float-velocity mode (default: 1.0)",
    )
    parser.add_argument(
        "--snapshot-interval", type=int, default=100,
        help="Progress logging interval in ticks (default: 100)",
    )

    args = parser.parse_args()

    config = ExperimentConfig(
        planet_count=args.planet_count,
        speed_limit=args.speed_limit,
        planet_formation_ticks=args.formation_ticks,
        orbital_test_ticks=args.orbital_ticks,
        approach=args.approach,
        enable_spreading=not args.no_spreading,
        use_accumulator=args.accumulator,
        use_float_velocity=args.float_velocity,
        use_analytical=args.analytical,
        use_discrete=args.discrete,
        analytical_r_max=args.analytical_r_max,
        analytical_total_mass=args.analytical_mass,
        dt=args.dt,
        random_seed=args.seed,
        snapshot_interval=args.snapshot_interval,
    )

    experiment = OrbitalExperiment(config)
    experiment.run()


if __name__ == "__main__":
    main()
