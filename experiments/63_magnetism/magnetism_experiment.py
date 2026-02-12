"""
Discrete Altermagnetism Experiment — v2
========================================
Tests whether the tick-frame gamma substrate independently discovers
altermagnetism from pure discrete rotation dynamics.

Three modes:
  frozen  — Original: equilibrate -> freeze -> probe (baseline, expected to fail)
  signed  — Signed tangential field: separate tang layer with omega sign
  live    — Live-field probing: entities + probes run simultaneously

Pure discrete operations: no continuous math, no pi, no floating-point angles.
Integer rotations, 8-step cycle, all direction vectors in {-1, 0, +1}.
"""

import os
import sys
import math
import json
import numpy as np
from scipy.ndimage import convolve
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from pathlib import Path
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)

# 8 discrete directions — all components in {-1, 0, +1}
DIRECTIONS = [
    (0, +1),   # 0: N
    (+1, +1),  # 1: NE
    (+1, 0),   # 2: E
    (+1, -1),  # 3: SE
    (0, -1),   # 4: S
    (-1, -1),  # 5: SW
    (-1, 0),   # 6: W
    (-1, +1),  # 7: NW
]

# Grid and timing defaults
GRID_SIZE = 64
ENTITY_SPACING = 16   # entities at 8, 24, 40, 56 along each axis
ENTITY_OFFSET = 8
EQUILIBRATION_TICKS = 1000
PROBE_TICKS = 2000
PROBE_RECORD_INTERVAL = 10
NUM_RUNS = 5
PROBE_SPEED = 0.5  # c = 1 cell/tick; probes must be sub-luminal
W_CENTER = 10.0
W_TANGENTIAL = 5.0
DEFAULT_LAG = 2
WARMUP_TICKS = 500

MODES = ["frozen", "signed", "live"]

# Rotation patterns: 4x4 arrays of omega (integer steps/tick)
PATTERNS = {
    "checkerboard": [
        [+1, -1, +1, -1],
        [-1, +1, -1, +1],
        [+1, -1, +1, -1],
        [-1, +1, -1, +1],
    ],
    "stripe": [
        [+2, +2, -2, -2],
        [+2, +2, -2, -2],
        [-2, -2, +2, +2],
        [-2, -2, +2, +2],
    ],
    "ferromagnetic": [
        [+1, +1, +1, +1],
        [+1, +1, +1, +1],
        [+1, +1, +1, +1],
        [+1, +1, +1, +1],
    ],
    "antiferromagnetic": [
        [+1, -1, +1, -1],
        [+1, -1, +1, -1],
        [+1, -1, +1, -1],
        [+1, -1, +1, -1],
    ],
}


# ---------------------------------------------------------------------------
# Gamma Field
# ---------------------------------------------------------------------------

class GammaField:
    """Discrete 2D gamma field with optional signed tangential layer."""

    def __init__(self, size: int):
        self.size = size
        self.gamma = np.zeros((size, size), dtype=np.float64)
        self.tang = np.zeros((size, size), dtype=np.float64)

    def deposit(self, x: int, y: int, amount: float):
        self.gamma[x % self.size, y % self.size] += amount

    def deposit_tang(self, x: int, y: int, amount: float):
        """Signed tangential deposit (amount can be negative)."""
        self.tang[x % self.size, y % self.size] += amount

    def spread(self):
        """Conservative 8-neighbor pressure equalization for both layers.

        Each cell averages with its 8 neighbors + itself (3x3 uniform kernel).
        Spread fraction = 1/9 — geometry of 8-connectivity, not a parameter.
        Periodic boundary via mode='wrap'.
        """
        kernel = np.ones((3, 3), dtype=np.float64) / 9.0
        self.gamma = convolve(self.gamma, kernel, mode="wrap")
        self.tang = convolve(self.tang, kernel, mode="wrap")

    def gradient_at(self, x: int, y: int):
        """Combined gradient: radial from gamma + tangential from tang."""
        s = self.size
        gx = (self.gamma[(x + 1) % s, y] - self.gamma[(x - 1) % s, y]) / 2.0
        gy = (self.gamma[x, (y + 1) % s] - self.gamma[x, (y - 1) % s]) / 2.0
        tx = (self.tang[(x + 1) % s, y] - self.tang[(x - 1) % s, y]) / 2.0
        ty = (self.tang[x, (y + 1) % s] - self.tang[x, (y - 1) % s]) / 2.0
        return gx + tx, gy + ty

    def interp_gradient(self, fx: float, fy: float):
        """Bilinear interpolation of gradient at continuous position."""
        s = self.size
        x0 = int(math.floor(fx)) % s
        y0 = int(math.floor(fy)) % s
        x1 = (x0 + 1) % s
        y1 = (y0 + 1) % s
        dx = fx - math.floor(fx)
        dy = fy - math.floor(fy)

        g00 = self.gradient_at(x0, y0)
        g10 = self.gradient_at(x1, y0)
        g01 = self.gradient_at(x0, y1)
        g11 = self.gradient_at(x1, y1)

        gx = (g00[0] * (1 - dx) * (1 - dy)
              + g10[0] * dx * (1 - dy)
              + g01[0] * (1 - dx) * dy
              + g11[0] * dx * dy)
        gy = (g00[1] * (1 - dx) * (1 - dy)
              + g10[1] * dx * (1 - dy)
              + g01[1] * (1 - dx) * dy
              + g11[1] * dx * dy)
        return gx, gy

    def copy(self):
        f = GammaField(self.size)
        f.gamma = self.gamma.copy()
        f.tang = self.tang.copy()
        return f


# ---------------------------------------------------------------------------
# Rotating Entity (pure integer rotation)
# ---------------------------------------------------------------------------

class RotatingEntity:
    """A fixed-position entity with discrete 8-step rotation."""

    def __init__(self, x: int, y: int, omega: int, lag: int, theta0: int = 0):
        self.x = x
        self.y = y
        self.omega = omega        # integer steps/tick, sign = handedness
        self.lag = lag             # integer ticks of imprint delay
        self.theta = theta0 % 8   # current orientation index (0-7)

    def tick(self):
        self.theta = (self.theta + self.omega) % 8

    def deposit(self, field: GammaField, w_center: float, w_tangential: float,
                use_signed_tang: bool = False):
        """Deposit gamma at center + directional imprint.

        use_signed_tang=False: tangential goes to gamma as |omega| (original).
        use_signed_tang=True:  tangential goes to tang field with omega sign.
        """
        field.deposit(self.x, self.y, w_center)
        lagged_theta = (self.theta - self.lag) % 8
        dx, dy = DIRECTIONS[lagged_theta]
        if use_signed_tang:
            field.deposit_tang(self.x + dx, self.y + dy,
                               w_tangential * self.omega)
        else:
            field.deposit(self.x + dx, self.y + dy,
                          w_tangential * abs(self.omega))


# ---------------------------------------------------------------------------
# Probe Entity (KDK leapfrog, continuous position)
# ---------------------------------------------------------------------------

class ProbeEntity:
    """A moving probe that couples to the gamma gradient via KDK leapfrog."""

    def __init__(self, x: float, y: float, vx: float, vy: float, label: str = ""):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.label = label
        self.trajectory = [(x, y)]
        self.initial_heading = math.atan2(vy, vx)

    def step(self, field: GammaField, dt: float = 1.0):
        """KDK leapfrog with periodic wrapping."""
        s = float(field.size)
        # Kick (half)
        gx, gy = field.interp_gradient(self.x, self.y)
        vx_half = self.vx + 0.5 * dt * gx
        vy_half = self.vy + 0.5 * dt * gy
        # Drift (full)
        self.x = (self.x + dt * vx_half) % s
        self.y = (self.y + dt * vy_half) % s
        # Kick (half) at new position
        gx2, gy2 = field.interp_gradient(self.x, self.y)
        self.vx = vx_half + 0.5 * dt * gx2
        self.vy = vy_half + 0.5 * dt * gy2

    def record(self):
        self.trajectory.append((self.x, self.y))

    def deflection_angle(self):
        """Angle between final displacement and initial heading."""
        if len(self.trajectory) < 2:
            return 0.0
        x0, y0 = self.trajectory[0]
        xf, yf = self.trajectory[-1]
        dx = xf - x0
        dy = yf - y0
        if abs(dx) < 1e-12 and abs(dy) < 1e-12:
            return 0.0
        actual_angle = math.atan2(dy, dx)
        return _wrap_angle(actual_angle - self.initial_heading)

    def speed(self):
        return math.sqrt(self.vx**2 + self.vy**2)


def _wrap_angle(a: float) -> float:
    """Wrap angle to [-pi, pi]."""
    while a > math.pi:
        a -= 2 * math.pi
    while a < -math.pi:
        a += 2 * math.pi
    return a


# ---------------------------------------------------------------------------
# Entity and probe construction helpers
# ---------------------------------------------------------------------------

def make_entities(pattern_name: str, rng: np.random.Generator, lag: int = DEFAULT_LAG):
    """Create 4x4 grid of rotating entities from a named pattern."""
    omega_grid = PATTERNS[pattern_name]
    entities = []
    for row in range(4):
        for col in range(4):
            x = ENTITY_OFFSET + col * ENTITY_SPACING
            y = ENTITY_OFFSET + row * ENTITY_SPACING
            omega = omega_grid[row][col]
            theta0 = int(rng.integers(0, 8))
            entities.append(RotatingEntity(x, y, omega, lag, theta0))
    return entities


def make_probes(speed: float = PROBE_SPEED):
    """Create 16 probes: 4 launch positions x 4 velocity directions."""
    s = GRID_SIZE
    # Launch positions: corners of centered region (1/4 and 3/4 marks)
    positions = [
        (s * 0.25, s * 0.25),
        (s * 0.75, s * 0.25),
        (s * 0.25, s * 0.75),
        (s * 0.75, s * 0.75),
    ]
    # 4 cardinal velocity directions
    velocities = [
        (0, +speed, "N"),
        (+speed, 0, "E"),
        (0, -speed, "S"),
        (-speed, 0, "W"),
    ]
    probes = []
    for pi, (px, py) in enumerate(positions):
        for vx, vy, vdir in velocities:
            label = f"P{pi}_{vdir}"
            probes.append(ProbeEntity(px, py, vx, vy, label))
    return probes


# ---------------------------------------------------------------------------
# Simulation core
# ---------------------------------------------------------------------------

def equilibrate(entities, field, ticks=EQUILIBRATION_TICKS,
                use_signed_tang=False):
    """Run entity rotation + deposit + field spreading for given ticks."""
    for _ in range(ticks):
        for e in entities:
            e.tick()
            e.deposit(field, W_CENTER, W_TANGENTIAL,
                      use_signed_tang=use_signed_tang)
        field.spread()


def run_probes(probes, field, ticks=PROBE_TICKS,
               record_interval=PROBE_RECORD_INTERVAL):
    """Advance probes through frozen field, recording trajectories."""
    for t in range(ticks):
        for p in probes:
            p.step(field)
            if (t + 1) % record_interval == 0:
                p.record()


def run_live(entities, field, probes, warmup_ticks=WARMUP_TICKS,
             probe_ticks=PROBE_TICKS, record_interval=PROBE_RECORD_INTERVAL):
    """Live-field probing: warmup then entities + probes simultaneously."""
    # Phase 1: warmup (entities only, no probes)
    for _ in range(warmup_ticks):
        for e in entities:
            e.tick()
            e.deposit(field, W_CENTER, W_TANGENTIAL)
        field.spread()

    # Phase 2: live probing (entities AND probes simultaneously)
    for t in range(probe_ticks):
        for e in entities:
            e.tick()
            e.deposit(field, W_CENTER, W_TANGENTIAL)
        field.spread()
        for p in probes:
            p.step(field)
            if (t + 1) % record_interval == 0:
                p.record()


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def decompose_field(field: GammaField, entities):
    """Decompose gradient into radial and tangential components relative to entities.

    Returns (W_radial, W_tang_x, W_tang_y) arrays.
    """
    s = field.size
    W_radial = np.zeros((s, s))
    W_tang_x = np.zeros((s, s))
    W_tang_y = np.zeros((s, s))

    entity_positions = np.array([(e.x, e.y) for e in entities], dtype=np.float64)

    for i in range(s):
        for j in range(s):
            gx, gy = field.gradient_at(i, j)
            gmag = math.sqrt(gx**2 + gy**2)
            if gmag < 1e-12:
                continue

            # Find nearest entity (periodic distance)
            best_dist = float("inf")
            best_rx, best_ry = 0.0, 0.0
            for ex, ey in entity_positions:
                rx = i - ex
                ry = j - ey
                # Periodic wrapping to nearest image
                if rx > s / 2:
                    rx -= s
                elif rx < -s / 2:
                    rx += s
                if ry > s / 2:
                    ry -= s
                elif ry < -s / 2:
                    ry += s
                d = rx * rx + ry * ry
                if d < best_dist:
                    best_dist = d
                    best_rx = rx
                    best_ry = ry

            rmag = math.sqrt(best_dist)
            if rmag < 1e-12:
                W_radial[i, j] = gmag
                continue

            # Unit radial vector
            rx_hat = best_rx / rmag
            ry_hat = best_ry / rmag

            # Radial projection
            rad_comp = gx * rx_hat + gy * ry_hat
            W_radial[i, j] = rad_comp

            # Tangential = gradient - radial component
            W_tang_x[i, j] = gx - rad_comp * rx_hat
            W_tang_y[i, j] = gy - rad_comp * ry_hat

    return W_radial, W_tang_x, W_tang_y


def compute_net_magnetization(W_tang_x, W_tang_y):
    """M_net = magnitude of summed tangential gradient."""
    mx = np.sum(W_tang_x)
    my = np.sum(W_tang_y)
    return math.sqrt(mx**2 + my**2)


def compute_net_magnetization_signed(tang_field):
    """M_net from signed tangential field directly."""
    return abs(float(np.sum(tang_field)))


def compute_deflection_asymmetries(probes):
    """Compute N-S and E-W deflection asymmetries."""
    by_dir = {"N": [], "E": [], "S": [], "W": []}
    for p in probes:
        direction = p.label.split("_")[1]
        by_dir[direction].append(p.deflection_angle())

    mean_N = np.mean(by_dir["N"]) if by_dir["N"] else 0.0
    mean_S = np.mean(by_dir["S"]) if by_dir["S"] else 0.0
    mean_E = np.mean(by_dir["E"]) if by_dir["E"] else 0.0
    mean_W = np.mean(by_dir["W"]) if by_dir["W"] else 0.0

    A_NS = mean_N - mean_S
    A_EW = mean_E - mean_W
    return A_NS, A_EW, by_dir


def compute_conductivity_tensor(probes):
    """Conductivity tensor sigma_ij from mean perpendicular deflections."""
    by_dir = {"N": [], "E": [], "S": [], "W": []}
    for p in probes:
        direction = p.label.split("_")[1]
        by_dir[direction].append(p.deflection_angle())

    sigma = np.zeros((2, 2))
    sigma[0, 0] = np.mean([math.cos(d) for d in by_dir["N"]] +
                          [math.cos(d) for d in by_dir["S"]])
    sigma[0, 1] = np.mean([math.sin(d) for d in by_dir["N"]] +
                          [-math.sin(d) for d in by_dir["S"]])
    sigma[1, 0] = np.mean([math.sin(d) for d in by_dir["E"]] +
                          [-math.sin(d) for d in by_dir["W"]])
    sigma[1, 1] = np.mean([math.cos(d) for d in by_dir["E"]] +
                          [math.cos(d) for d in by_dir["W"]])
    return sigma


def fourier_symmetry(W_tang_magnitude):
    """Angular decomposition of tangential field via 2D FFT.

    Returns dict of {mode: power} for modes 1..8.
    """
    fft2 = np.fft.fft2(W_tang_magnitude)
    power = np.abs(fft2)**2
    s = W_tang_magnitude.shape[0]

    # Radial-angular decomposition of power spectrum
    freqs_x = np.fft.fftfreq(s)
    freqs_y = np.fft.fftfreq(s)
    fx, fy = np.meshgrid(freqs_x, freqs_y, indexing="ij")
    angles = np.arctan2(fy, fx)
    radii = np.sqrt(fx**2 + fy**2)

    # Angular power in bands (exclude DC and very low freq)
    mask = radii > 2.0 / s
    mode_power = {}
    for m in range(1, 9):
        cos_proj = np.sum(power[mask] * np.cos(m * angles[mask]))
        sin_proj = np.sum(power[mask] * np.sin(m * angles[mask]))
        mode_power[m] = math.sqrt(cos_proj**2 + sin_proj**2)

    # Normalize by total power
    total = sum(mode_power.values())
    if total > 0:
        for m in mode_power:
            mode_power[m] /= total

    return mode_power


# ---------------------------------------------------------------------------
# Single run
# ---------------------------------------------------------------------------

@dataclass
class RunResult:
    pattern: str
    seed: int
    mode: str
    M_net: float
    max_W_tang: float
    A_NS: float
    A_EW: float
    sigma: np.ndarray
    mode_power: dict
    deflections_by_dir: dict
    field_snapshot: np.ndarray
    tang_snapshot: np.ndarray
    W_radial: np.ndarray
    W_tang_x: np.ndarray
    W_tang_y: np.ndarray
    probe_trajectories: list


def run_single(pattern_name: str, seed: int, lag: int = DEFAULT_LAG,
               eq_ticks: int = EQUILIBRATION_TICKS,
               probe_ticks: int = PROBE_TICKS,
               probe_speed: float = PROBE_SPEED,
               mode: str = "frozen") -> RunResult:
    """Run one complete experiment in the specified mode."""
    rng = np.random.default_rng(seed)
    field = GammaField(GRID_SIZE)
    entities = make_entities(pattern_name, rng, lag)

    if mode == "frozen":
        # Original: equilibrate with unsigned gamma deposits, freeze, probe
        equilibrate(entities, field, eq_ticks, use_signed_tang=False)
        frozen_field = field.copy()
        probes = make_probes(probe_speed)
        run_probes(probes, frozen_field, probe_ticks)
        analysis_field = frozen_field

    elif mode == "signed":
        # Signed tang: equilibrate with signed tangential deposits, freeze, probe
        equilibrate(entities, field, eq_ticks, use_signed_tang=True)
        frozen_field = field.copy()
        probes = make_probes(probe_speed)
        run_probes(probes, frozen_field, probe_ticks)
        analysis_field = frozen_field

    elif mode == "live":
        # Live: warmup then entities + probes simultaneously
        probes = make_probes(probe_speed)
        run_live(entities, field, probes,
                 warmup_ticks=WARMUP_TICKS, probe_ticks=probe_ticks)
        analysis_field = field

    else:
        raise ValueError(f"Unknown mode: {mode}")

    # Decompose field
    W_radial, W_tang_x, W_tang_y = decompose_field(analysis_field, entities)
    W_tang_mag = np.sqrt(W_tang_x**2 + W_tang_y**2)
    max_W_tang = float(np.max(W_tang_mag))

    # Net magnetization: signed mode uses tang field directly
    if mode == "signed":
        M_net = compute_net_magnetization_signed(analysis_field.tang)
    else:
        M_net = compute_net_magnetization(W_tang_x, W_tang_y)

    # Probe analysis
    A_NS, A_EW, defl_by_dir = compute_deflection_asymmetries(probes)
    sigma = compute_conductivity_tensor(probes)
    mode_power = fourier_symmetry(W_tang_mag)

    trajectories = [(p.label, p.trajectory) for p in probes]

    return RunResult(
        pattern=pattern_name,
        seed=seed,
        mode=mode,
        M_net=M_net,
        max_W_tang=max_W_tang,
        A_NS=A_NS,
        A_EW=A_EW,
        sigma=sigma,
        mode_power=mode_power,
        deflections_by_dir=defl_by_dir,
        field_snapshot=analysis_field.gamma.copy(),
        tang_snapshot=analysis_field.tang.copy(),
        W_radial=W_radial,
        W_tang_x=W_tang_x,
        W_tang_y=W_tang_y,
        probe_trajectories=trajectories,
    )


# ---------------------------------------------------------------------------
# Statistical aggregation
# ---------------------------------------------------------------------------

@dataclass
class PatternStats:
    pattern: str
    mode: str
    M_net_mean: float
    M_net_std: float
    max_W_tang_mean: float
    A_NS_mean: float
    A_NS_std: float
    A_EW_mean: float
    A_EW_std: float
    sigma_mean: np.ndarray
    mode_power_mean: dict
    runs: list  # list of RunResult


def aggregate_runs(results: list) -> PatternStats:
    """Aggregate statistics over multiple runs of the same pattern."""
    pattern = results[0].pattern
    mode = results[0].mode
    M_nets = [r.M_net for r in results]
    max_tangs = [r.max_W_tang for r in results]
    A_NSs = [r.A_NS for r in results]
    A_EWs = [r.A_EW for r in results]
    sigmas = np.array([r.sigma for r in results])

    # Average mode power
    all_modes = [r.mode_power for r in results]
    mode_mean = {}
    for m in range(1, 9):
        mode_mean[m] = np.mean([mp[m] for mp in all_modes])

    return PatternStats(
        pattern=pattern,
        mode=mode,
        M_net_mean=np.mean(M_nets),
        M_net_std=np.std(M_nets),
        max_W_tang_mean=np.mean(max_tangs),
        A_NS_mean=np.mean(A_NSs),
        A_NS_std=np.std(A_NSs),
        A_EW_mean=np.mean(A_EWs),
        A_EW_std=np.std(A_EWs),
        sigma_mean=np.mean(sigmas, axis=0),
        mode_power_mean=mode_mean,
        runs=results,
    )


# ---------------------------------------------------------------------------
# Visualization
# ---------------------------------------------------------------------------

def plot_field_heatmaps(stats: PatternStats):
    """Plot gamma, W_radial, W_tangential (+ tang for signed mode)."""
    run = stats.runs[0]
    is_signed = stats.mode == "signed"
    ncols = 4 if is_signed else 3
    fig, axes = plt.subplots(1, ncols, figsize=(6 * ncols, 5))
    fig.suptitle(f"Field Decomposition: {stats.pattern} [{stats.mode}]", fontsize=14)

    ax_idx = 0

    # Gamma field
    im0 = axes[ax_idx].imshow(run.field_snapshot.T, origin="lower", cmap="inferno")
    axes[ax_idx].set_title("Gamma Field")
    plt.colorbar(im0, ax=axes[ax_idx], shrink=0.8)
    ax_idx += 1

    # Tang field (signed mode only)
    if is_signed:
        vmax_t = max(abs(run.tang_snapshot.min()), abs(run.tang_snapshot.max()), 1e-10)
        im_t = axes[ax_idx].imshow(run.tang_snapshot.T, origin="lower", cmap="RdBu_r",
                                    vmin=-vmax_t, vmax=vmax_t)
        axes[ax_idx].set_title(f"Tang Field (M_net={run.M_net:.1f})")
        plt.colorbar(im_t, ax=axes[ax_idx], shrink=0.8)
        ax_idx += 1

    # W_radial
    vmax_r = max(abs(run.W_radial.min()), abs(run.W_radial.max()), 1e-10)
    im1 = axes[ax_idx].imshow(run.W_radial.T, origin="lower", cmap="RdBu_r",
                               vmin=-vmax_r, vmax=vmax_r)
    axes[ax_idx].set_title("W_radial")
    plt.colorbar(im1, ax=axes[ax_idx], shrink=0.8)
    ax_idx += 1

    # W_tangential magnitude + quiver
    W_tang_mag = np.sqrt(run.W_tang_x**2 + run.W_tang_y**2)
    im2 = axes[ax_idx].imshow(W_tang_mag.T, origin="lower", cmap="viridis")
    axes[ax_idx].set_title(f"W_tangential (max={float(np.max(W_tang_mag)):.2f})")
    plt.colorbar(im2, ax=axes[ax_idx], shrink=0.8)
    step = 4
    xs = np.arange(0, GRID_SIZE, step)
    ys = np.arange(0, GRID_SIZE, step)
    X, Y = np.meshgrid(xs, ys, indexing="ij")
    U = run.W_tang_x[::step, ::step]
    V = run.W_tang_y[::step, ::step]
    axes[ax_idx].quiver(X, Y, U, V, color="white", alpha=0.6, scale_units="xy")

    # Mark entity positions on all panels
    for e_ax in axes:
        for row in range(4):
            for col in range(4):
                ex = ENTITY_OFFSET + col * ENTITY_SPACING
                ey = ENTITY_OFFSET + row * ENTITY_SPACING
                e_ax.plot(ex, ey, "w+", markersize=6, markeredgewidth=1.5)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"field_{stats.mode}_{stats.pattern}.png", dpi=150)
    plt.close(fig)


def plot_trajectories(stats: PatternStats):
    """Plot probe trajectories on tangential field background."""
    run = stats.runs[0]
    W_tang_mag = np.sqrt(run.W_tang_x**2 + run.W_tang_y**2)

    fig, ax = plt.subplots(1, 1, figsize=(8, 8))
    ax.imshow(W_tang_mag.T, origin="lower", cmap="viridis", alpha=0.5)
    ax.set_title(f"Probe Trajectories: {stats.pattern} [{stats.mode}]")

    colors = plt.cm.tab10(np.linspace(0, 1, 16))
    for idx, (label, traj) in enumerate(run.probe_trajectories):
        xs = [p[0] for p in traj]
        ys = [p[1] for p in traj]
        ax.plot(xs, ys, "-", color=colors[idx], linewidth=0.8, label=label)
        ax.plot(xs[0], ys[0], "o", color=colors[idx], markersize=4)
        ax.plot(xs[-1], ys[-1], "s", color=colors[idx], markersize=4)

    ax.set_xlim(0, GRID_SIZE)
    ax.set_ylim(0, GRID_SIZE)
    ax.legend(fontsize=6, ncol=4, loc="upper right")
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"trajectories_{stats.mode}_{stats.pattern}.png", dpi=150)
    plt.close(fig)


def plot_fourier_symmetry(stats: PatternStats):
    """Plot FFT angular power spectrum for one pattern."""
    fig, ax = plt.subplots(1, 1, figsize=(8, 5))
    modes = list(range(1, 9))
    powers = [stats.mode_power_mean[m] for m in modes]
    ax.bar(modes, powers, color="steelblue", edgecolor="black")
    ax.set_xlabel("Angular Mode m")
    ax.set_ylabel("Normalized Power")
    ax.set_title(f"Fourier Symmetry: {stats.pattern} [{stats.mode}]")
    ax.set_xticks(modes)
    dominant = max(stats.mode_power_mean, key=stats.mode_power_mean.get)
    ax.annotate(f"Dominant: m={dominant}", xy=(dominant, powers[dominant - 1]),
                xytext=(dominant + 0.5, powers[dominant - 1] * 1.1),
                arrowprops=dict(arrowstyle="->"), fontsize=10)
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"fourier_{stats.mode}_{stats.pattern}.png", dpi=150)
    plt.close(fig)


def plot_summary_comparison(mode_stats: dict, mode_name: str):
    """Bar charts comparing M_net, A_NS, A_EW across patterns for one mode."""
    names = list(mode_stats.keys())
    n = len(names)

    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    fig.suptitle(f"Cross-Pattern Comparison [{mode_name}]", fontsize=14)
    x = np.arange(n)
    width = 0.6

    # M_net
    vals = [mode_stats[p].M_net_mean for p in names]
    errs = [2 * mode_stats[p].M_net_std for p in names]
    axes[0].bar(x, vals, width, yerr=errs, capsize=5, color="coral", edgecolor="black")
    axes[0].set_ylabel("M_net")
    axes[0].set_title("Net Magnetization")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(names, rotation=30, ha="right")

    # A_NS
    vals = [mode_stats[p].A_NS_mean for p in names]
    errs = [2 * mode_stats[p].A_NS_std for p in names]
    axes[1].bar(x, vals, width, yerr=errs, capsize=5, color="steelblue", edgecolor="black")
    axes[1].set_ylabel("A_NS (rad)")
    axes[1].set_title("N-S Asymmetry")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(names, rotation=30, ha="right")

    # A_EW
    vals = [mode_stats[p].A_EW_mean for p in names]
    errs = [2 * mode_stats[p].A_EW_std for p in names]
    axes[2].bar(x, vals, width, yerr=errs, capsize=5, color="seagreen", edgecolor="black")
    axes[2].set_ylabel("A_EW (rad)")
    axes[2].set_title("E-W Asymmetry")
    axes[2].set_xticks(x)
    axes[2].set_xticklabels(names, rotation=30, ha="right")

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"summary_{mode_name}.png", dpi=150)
    plt.close(fig)


def plot_mode_comparison(all_mode_stats: dict):
    """Side-by-side comparison of M_net and deflection across all modes."""
    modes_present = sorted(all_mode_stats.keys())
    patterns = list(PATTERNS.keys())
    n_modes = len(modes_present)
    n_patterns = len(patterns)
    colors = {"frozen": "#e74c3c", "signed": "#3498db", "live": "#2ecc71"}

    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle("Mode Comparison", fontsize=14)

    x = np.arange(n_patterns)
    width = 0.8 / n_modes

    for i, mode in enumerate(modes_present):
        stats = all_mode_stats[mode]
        m_nets = [stats[p].M_net_mean if p in stats else 0 for p in patterns]
        defls = [math.sqrt(stats[p].A_NS_mean**2 + stats[p].A_EW_mean**2)
                 if p in stats else 0 for p in patterns]

        offset = (i - n_modes / 2 + 0.5) * width
        c = colors.get(mode, "#999999")
        axes[0].bar(x + offset, m_nets, width, label=mode, color=c, edgecolor="black")
        axes[1].bar(x + offset, defls, width, label=mode, color=c, edgecolor="black")

    axes[0].set_ylabel("M_net")
    axes[0].set_title("Net Magnetization")
    axes[0].set_xticks(x)
    axes[0].set_xticklabels(patterns, rotation=30, ha="right")
    axes[0].set_yscale("symlog", linthresh=1.0)
    axes[0].legend()

    axes[1].set_ylabel("|Deflection|")
    axes[1].set_title("Deflection Magnitude")
    axes[1].set_xticks(x)
    axes[1].set_xticklabels(patterns, rotation=30, ha="right")
    axes[1].legend()

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "mode_comparison.png", dpi=150)
    plt.close(fig)


def plot_velocity_comparison(vel_reports: dict):
    """Bar chart: deflection at low vs high speed for each mode."""
    modes_present = sorted(vel_reports.keys())
    n = len(modes_present)

    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(n)
    width = 0.35

    lows = [vel_reports[m]["defl_low"] for m in modes_present]
    highs = [vel_reports[m]["defl_high"] for m in modes_present]
    v_lo = vel_reports[modes_present[0]]["v_low"]
    v_hi = vel_reports[modes_present[0]]["v_high"]

    ax.bar(x - width / 2, lows, width, label=f"v={v_lo}", color="#3498db", edgecolor="black")
    ax.bar(x + width / 2, highs, width, label=f"v={v_hi}", color="#e74c3c", edgecolor="black")

    ax.set_ylabel("|Deflection|")
    ax.set_title("Velocity Dependence by Mode")
    ax.set_xticks(x)
    ax.set_xticklabels(modes_present)
    ax.legend()

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "velocity_comparison.png", dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# Success criteria evaluation
# ---------------------------------------------------------------------------

def evaluate_criteria(all_mode_stats: dict, vel_reports: dict = None):
    """Evaluate pass/fail against success criteria per mode.

    Mode-specific criteria:
      frozen — informational only (expected to fail, baseline reference)
      signed — compensated magnetism, ferromagnetic M_net >> 0,
               antiferromagnetic M_net ~ 0, pattern specificity
      live   — velocity dependence (faster probes deflect more)

    all_mode_stats: {mode: {pattern: PatternStats}}
    vel_reports: {mode: {v_low, v_high, defl_low, defl_high, scales}}
    """
    lines = []
    mode_results = {}

    for mode in sorted(all_mode_stats.keys()):
        mode_stats = all_mode_stats[mode]
        mode_pass = True
        is_frozen = mode == "frozen"
        is_live = mode == "live"

        expected = {
            "frozen": "INFORMATIONAL (baseline, not scored)",
            "signed": "EXPECTED TO PASS (compensated magnetism + pattern specificity)",
            "live": "EXPECTED TO PASS (velocity-dependent deflection)",
        }

        lines.append("")
        lines.append("=" * 60)
        lines.append(f"MODE: {mode.upper()} — {expected.get(mode, '')}")
        lines.append("=" * 60)

        def log(msg, passed=True):
            nonlocal mode_pass
            status = "PASS" if passed else "FAIL"
            if not passed:
                mode_pass = False
            lines.append(f"  [{status}] {msg}")

        def info(msg, _passed=True):
            """Informational result that doesn't affect pass/fail."""
            lines.append(f"  [INFO] {msg}")

        report = info if (is_frozen or is_live) else log

        # Altermagnetic candidates
        for name in ["checkerboard", "stripe"]:
            if name not in mode_stats:
                continue
            s = mode_stats[name]
            lines.append(f"\n  --- {name.upper()} (altermagnetic candidate) ---")

            if mode == "signed" and "ferromagnetic" in mode_stats:
                ferro_m = mode_stats["ferromagnetic"].M_net_mean
                ratio = s.M_net_mean / ferro_m if ferro_m > 0 else 0
                report(f"Compensated magnetism: M_net/M_net_ferro = {ratio:.6f} (need < 0.01)",
                       abs(ratio) < 0.01)
            else:
                ratio = s.M_net_mean / s.max_W_tang_mean if s.max_W_tang_mean > 0 else float("inf")
                report(f"Compensated magnetism: |M_net|/max|W_tang| = {ratio:.4f} (need < 0.1)",
                       abs(ratio) < 0.1)

            aniso = abs(s.A_NS_mean) > 0.1 or abs(s.A_EW_mean) > 0.1
            report(f"Anisotropic transport: |A_NS|={abs(s.A_NS_mean):.4f}, "
                   f"|A_EW|={abs(s.A_EW_mean):.4f} (need > 0.1)", aniso)

        # Control patterns
        for name, expected_desc in [("ferromagnetic", "M_net >> 0"),
                                    ("antiferromagnetic", "M_net ~ 0, isotropic")]:
            if name not in mode_stats:
                continue
            s = mode_stats[name]
            lines.append(f"\n  --- {name.upper()} (control: {expected_desc}) ---")

            if name == "ferromagnetic":
                report(f"M_net = {s.M_net_mean:.4f} (expect >> 0)", s.M_net_mean > 1.0)
                info(f"Transport: |A_NS|={abs(s.A_NS_mean):.4f}, "
                     f"|A_EW|={abs(s.A_EW_mean):.4f}")
            else:
                if mode == "signed" and "ferromagnetic" in mode_stats:
                    ferro_m = mode_stats["ferromagnetic"].M_net_mean
                    ratio = s.M_net_mean / ferro_m if ferro_m > 0 else 0
                    report(f"M_net ~ 0: ratio to ferro = {ratio:.6f}", abs(ratio) < 0.5)
                else:
                    ratio = s.M_net_mean / s.max_W_tang_mean if s.max_W_tang_mean > 0 else float("inf")
                    report(f"M_net ~ 0: ratio = {ratio:.4f}", abs(ratio) < 0.5)
                info(f"Transport: |A_NS|={abs(s.A_NS_mean):.4f}, "
                     f"|A_EW|={abs(s.A_EW_mean):.4f}")

        # Pattern specificity
        lines.append("\n  --- PATTERN SPECIFICITY ---")
        pattern_names = [n for n in ["checkerboard", "stripe"] if n in mode_stats]
        if len(pattern_names) == 2:
            s1, s2 = mode_stats[pattern_names[0]], mode_stats[pattern_names[1]]
            distinct = (abs(s1.A_NS_mean - s2.A_NS_mean) > 0.05 or
                        abs(s1.A_EW_mean - s2.A_EW_mean) > 0.05 or
                        abs(s1.M_net_mean - s2.M_net_mean) > 0.5)
            report(f"Checkerboard vs stripe produce distinct results", distinct)

        # Velocity dependence
        if vel_reports and mode in vel_reports:
            vr = vel_reports[mode]
            lines.append("\n  --- VELOCITY DEPENDENCE ---")
            vel_log = log if is_live else info
            vel_log(f"Faster deflects more: v={vr['v_high']} -> {vr['defl_high']:.6f} vs "
                    f"v={vr['v_low']} -> {vr['defl_low']:.6f}", vr["scales"])

        lines.append(f"\n  MODE RESULT: {'PASS' if mode_pass else 'FAIL'}")
        mode_results[mode] = mode_pass

    # Overall: signed and live must pass; frozen is informational
    lines.append("")
    lines.append("=" * 60)
    lines.append("OVERALL RESULTS")
    lines.append("=" * 60)
    for m, p in mode_results.items():
        tag = " (baseline, not scored)" if m == "frozen" else ""
        lines.append(f"  {m}: {'PASS' if p else 'FAIL'}{tag}")

    # Overall pass = signed pass AND live pass (frozen excluded)
    overall = True
    if "signed" in mode_results:
        overall = overall and mode_results["signed"]
    if "live" in mode_results:
        overall = overall and mode_results["live"]

    verdict = "OVERALL: PASS" if overall else "OVERALL: FAIL (see individual modes)"
    lines.append(verdict)
    lines.append("=" * 60)

    report = "\n".join(lines)
    return overall, report


# ---------------------------------------------------------------------------
# Velocity dependence test
# ---------------------------------------------------------------------------

def velocity_dependence_test(pattern_name: str = "checkerboard", seed: int = 42,
                             mode: str = "frozen"):
    """Run probes at v=0.2 and v=0.7, compare deflection magnitudes."""
    V_LOW = 0.2
    V_HIGH = 0.7

    results = {}
    for v in [V_LOW, V_HIGH]:
        results[v] = run_single(pattern_name, seed, probe_speed=v, mode=mode)

    defl_low = math.sqrt(results[V_LOW].A_NS**2 + results[V_LOW].A_EW**2)
    defl_high = math.sqrt(results[V_HIGH].A_NS**2 + results[V_HIGH].A_EW**2)

    return {
        "v_low": V_LOW,
        "v_high": V_HIGH,
        "defl_low": defl_low,
        "defl_high": defl_high,
        "scales": defl_high > defl_low,
    }


# ---------------------------------------------------------------------------
# Main experiment
# ---------------------------------------------------------------------------

def run_experiment(num_runs: int = NUM_RUNS, eq_ticks: int = EQUILIBRATION_TICKS,
                   probe_ticks: int = PROBE_TICKS, modes: list = None):
    """Run full experiment across all patterns and modes."""
    if modes is None:
        modes = MODES

    print("=" * 60)
    print("DISCRETE ALTERMAGNETISM EXPERIMENT — v2")
    print("=" * 60)
    print(f"Grid: {GRID_SIZE}x{GRID_SIZE}, Entities: 4x4, Spacing: {ENTITY_SPACING}")
    print(f"Equilibration: {eq_ticks} ticks, Probes: {probe_ticks} ticks")
    print(f"Runs per pattern: {num_runs}, Probe speed: {PROBE_SPEED}")
    print(f"W_center={W_CENTER}, W_tangential={W_TANGENTIAL}, lag={DEFAULT_LAG}")
    print(f"Modes: {', '.join(modes)}")
    print()

    all_mode_stats = {}  # {mode: {pattern: PatternStats}}

    for mode in modes:
        print(f"\n{'='*60}")
        print(f"MODE: {mode.upper()}")
        print(f"{'='*60}")

        mode_stats = {}
        for pattern_name in PATTERNS:
            print(f"  --- {pattern_name} ---")
            results = []
            for run_idx in range(num_runs):
                seed = 1000 * list(PATTERNS.keys()).index(pattern_name) + run_idx
                print(f"    Run {run_idx + 1}/{num_runs} (seed={seed})...",
                      end=" ", flush=True)
                r = run_single(pattern_name, seed, eq_ticks=eq_ticks,
                               probe_ticks=probe_ticks, mode=mode)
                print(f"M_net={r.M_net:.4f}, A_NS={r.A_NS:.4f}, A_EW={r.A_EW:.4f}")
                results.append(r)

            stats = aggregate_runs(results)
            mode_stats[pattern_name] = stats

            # Per-pattern plots
            print(f"    Generating plots for {pattern_name} [{mode}]...")
            plot_field_heatmaps(stats)
            plot_trajectories(stats)
            plot_fourier_symmetry(stats)

        all_mode_stats[mode] = mode_stats

        # Per-mode summary
        print(f"\n  Generating summary for [{mode}]...")
        plot_summary_comparison(mode_stats, mode)

    # Cross-mode comparison
    if len(modes) > 1:
        print("\nGenerating mode comparison plot...")
        plot_mode_comparison(all_mode_stats)

    # Velocity dependence per mode
    print("\nRunning velocity dependence tests...")
    vel_reports = {}
    for mode in modes:
        print(f"  Velocity test [{mode}]...", end=" ", flush=True)
        vr = velocity_dependence_test(mode=mode)
        vel_reports[mode] = vr
        tag = "MAGNETIC" if vr["scales"] else "GRAVITATIONAL"
        print(f"v_low={vr['defl_low']:.6f}, v_high={vr['defl_high']:.6f} -> {tag}")

    if len(modes) > 1:
        plot_velocity_comparison(vel_reports)

    # Evaluate success criteria
    passed, report = evaluate_criteria(all_mode_stats, vel_reports)
    print(report)

    # Save results
    save_results(all_mode_stats, report, vel_reports)

    return all_mode_stats, passed


def save_results(all_mode_stats: dict, criteria_report: str, vel_reports: dict):
    """Save numerical results to JSON and text report."""
    # Text report
    lines = ["DISCRETE ALTERMAGNETISM EXPERIMENT v2 — RESULTS", "=" * 50, ""]
    for mode, mode_stats in all_mode_stats.items():
        lines.append(f"--- MODE: {mode.upper()} ---")
        for name, s in mode_stats.items():
            lines.append(f"  Pattern: {name}")
            lines.append(f"    M_net:  {s.M_net_mean:.6f} +/- {2*s.M_net_std:.6f}")
            lines.append(f"    A_NS:   {s.A_NS_mean:.6f} +/- {2*s.A_NS_std:.6f}")
            lines.append(f"    A_EW:   {s.A_EW_mean:.6f} +/- {2*s.A_EW_std:.6f}")
            lines.append(f"    max_W_tang: {s.max_W_tang_mean:.6f}")
            lines.append(f"    sigma_mean:\n      {s.sigma_mean}")
            lines.append(f"    Fourier modes: {s.mode_power_mean}")
            lines.append("")
        lines.append("")

    lines.append("--- VELOCITY DEPENDENCE ---")
    for mode, vr in vel_reports.items():
        lines.append(f"  {mode}: v_low={vr['v_low']} -> {vr['defl_low']:.6f}, "
                     f"v_high={vr['v_high']} -> {vr['defl_high']:.6f}, "
                     f"scales={'yes' if vr['scales'] else 'no'}")
    lines.append("")
    lines.append(criteria_report)

    report_path = RESULTS_DIR / "experiment_report.txt"
    report_path.write_text("\n".join(lines))
    print(f"\nReport saved to: {report_path}")

    # JSON summary (no numpy arrays)
    summary = {}
    for mode, mode_stats in all_mode_stats.items():
        summary[mode] = {}
        for name, s in mode_stats.items():
            summary[mode][name] = {
                "M_net_mean": float(s.M_net_mean),
                "M_net_std": float(s.M_net_std),
                "max_W_tang_mean": float(s.max_W_tang_mean),
                "A_NS_mean": float(s.A_NS_mean),
                "A_NS_std": float(s.A_NS_std),
                "A_EW_mean": float(s.A_EW_mean),
                "A_EW_std": float(s.A_EW_std),
                "sigma_mean": s.sigma_mean.tolist(),
                "mode_power_mean": {str(k): float(v) for k, v in s.mode_power_mean.items()},
            }
    summary["velocity_dependence"] = {}
    for mode, vr in vel_reports.items():
        summary["velocity_dependence"][mode] = {
            "v_low": vr["v_low"],
            "v_high": vr["v_high"],
            "defl_low": vr["defl_low"],
            "defl_high": vr["defl_high"],
            "scales": vr["scales"],
        }
    json_path = RESULTS_DIR / "experiment_results.json"
    json_path.write_text(json.dumps(summary, indent=2))
    print(f"JSON saved to: {json_path}")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Discrete Altermagnetism Experiment v2")
    parser.add_argument("--runs", type=int, default=NUM_RUNS,
                        help=f"Runs per pattern (default: {NUM_RUNS})")
    parser.add_argument("--eq-ticks", type=int, default=EQUILIBRATION_TICKS,
                        help=f"Equilibration ticks (default: {EQUILIBRATION_TICKS})")
    parser.add_argument("--probe-ticks", type=int, default=PROBE_TICKS,
                        help=f"Probe ticks (default: {PROBE_TICKS})")
    parser.add_argument("--mode", choices=MODES + ["all"], default="all",
                        help="Which mode to run (default: all)")
    parser.add_argument("--smoke", action="store_true",
                        help="Quick smoke test (2 runs, 100 eq, 200 probe)")
    args = parser.parse_args()

    run_modes = MODES if args.mode == "all" else [args.mode]

    if args.smoke:
        print("*** SMOKE TEST MODE ***\n")
        run_experiment(num_runs=2, eq_ticks=100, probe_ticks=200, modes=run_modes)
    else:
        run_experiment(num_runs=args.runs, eq_ticks=args.eq_ticks,
                       probe_ticks=args.probe_ticks, modes=run_modes)
