"""
Experiment #64 — Three-Body Gravitational Dynamics
====================================================
Tests whether the V18.1 orbital substrate (pressure spreading + fractional
accumulator + trilinear interpolation + leapfrog) produces correct three-body
gravitational dynamics from pure gamma-field interactions.

Dense NumPy 3D array backend for performance (replaces sparse dict from V18.1).
Same physics: 1/6 pressure equalization, synchronous update, conservative.

Usage:
    python three_body_experiment.py --calibrate
    python three_body_experiment.py --phase 1
    python three_body_experiment.py --phase 1 --quick
    python three_body_experiment.py --phase 2
    python three_body_experiment.py --phase 2 --config counter-rotating
    python three_body_experiment.py --phase 3
    python three_body_experiment.py --all
    python three_body_experiment.py --all --quick --spread-interval 5

Date: February 2026
Substrate: V18.1 (dense NumPy reimplementation)
"""

import math
import json
import time
import argparse
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field as dataclass_field

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

RESULTS_DIR = Path(__file__).parent / "results"


# ===========================================================================
# GammaField3D — Dense NumPy gamma field with periodic boundaries
# ===========================================================================

class GammaField3D:
    """Dense 3D gamma field on periodic cubic lattice.

    Implements V18.1 pressure equalization using vectorized np.roll.
    Total gamma is conserved exactly (transfers only, no creation/destruction).
    """

    def __init__(self, size):
        self.size = size
        self.gamma = np.zeros((size, size, size), dtype=np.float64)

    def deposit(self, x, y, z, amount=1.0):
        """Deposit gamma at integer position (periodic wrapping)."""
        s = self.size
        self.gamma[int(x) % s, int(y) % s, int(z) % s] += amount

    def spread(self):
        """Pressure-based gamma equalization — vectorized V18.1 rule.

        Each cell shares (gamma_here - gamma_neighbor)/6 with each neighbor
        where gamma_here > gamma_neighbor. Synchronous update (compute all
        transfers, then apply).

        Spread fraction = 1/6 (geometry of 6-connectivity, not a parameter).

        Optimized: computes net delta in a single array, reusing temporaries.
        """
        g = self.gamma
        delta = np.zeros_like(g)

        for shift, axis in [(1, 0), (-1, 0), (1, 1), (-1, 1), (1, 2), (-1, 2)]:
            neighbor = np.roll(g, shift, axis=axis)
            diff = g - neighbor
            np.maximum(diff, 0.0, out=diff)
            diff *= (1.0 / 6.0)
            # Cell loses what it sends out
            delta -= diff
            # Neighbor gains what it receives (roll back)
            delta += np.roll(diff, -shift, axis=axis)

        self.gamma += delta

    def gradient_at(self, x, y, z):
        """Central-difference gradient at integer position (periodic)."""
        s = self.size
        xi, yi, zi = int(x) % s, int(y) % s, int(z) % s
        gx = (self.gamma[(xi + 1) % s, yi, zi] - self.gamma[(xi - 1) % s, yi, zi]) / 2.0
        gy = (self.gamma[xi, (yi + 1) % s, zi] - self.gamma[xi, (yi - 1) % s, zi]) / 2.0
        gz = (self.gamma[xi, yi, (zi + 1) % s] - self.gamma[xi, yi, (zi - 1) % s]) / 2.0
        return np.array([gx, gy, gz])

    def gradient_trilinear(self, pos):
        """Trilinear interpolation of gradient at fractional position.

        Computes gradient at 8 cube corners, then blends with trilinear weights.
        Ported from OrbitalTestProcessFloat._interp_gradient (experiment_orbital.py).
        """
        s = self.size
        fx, fy, fz = pos[0], pos[1], pos[2]
        x0 = int(math.floor(fx)) % s
        y0 = int(math.floor(fy)) % s
        z0 = int(math.floor(fz)) % s
        x1 = (x0 + 1) % s
        y1 = (y0 + 1) % s
        z1 = (z0 + 1) % s
        dx = fx - math.floor(fx)
        dy = fy - math.floor(fy)
        dz = fz - math.floor(fz)

        corners = [
            self.gradient_at(x0, y0, z0),
            self.gradient_at(x1, y0, z0),
            self.gradient_at(x0, y1, z0),
            self.gradient_at(x1, y1, z0),
            self.gradient_at(x0, y0, z1),
            self.gradient_at(x1, y0, z1),
            self.gradient_at(x0, y1, z1),
            self.gradient_at(x1, y1, z1),
        ]

        result = np.zeros(3)
        for i in range(3):
            c00 = corners[0][i] * (1 - dx) + corners[1][i] * dx
            c10 = corners[2][i] * (1 - dx) + corners[3][i] * dx
            c01 = corners[4][i] * (1 - dx) + corners[5][i] * dx
            c11 = corners[6][i] * (1 - dx) + corners[7][i] * dx
            c0 = c00 * (1 - dy) + c10 * dy
            c1 = c01 * (1 - dy) + c11 * dy
            result[i] = c0 * (1 - dz) + c1 * dz

        return result

    def gamma_trilinear(self, pos):
        """Trilinear interpolation of gamma at fractional position.

        Ported from OrbitalTestProcessFloat._interp_gamma (experiment_orbital.py).
        """
        s = self.size
        fx, fy, fz = pos[0], pos[1], pos[2]
        x0 = int(math.floor(fx)) % s
        y0 = int(math.floor(fy)) % s
        z0 = int(math.floor(fz)) % s
        x1 = (x0 + 1) % s
        y1 = (y0 + 1) % s
        z1 = (z0 + 1) % s
        dx = fx - math.floor(fx)
        dy = fy - math.floor(fy)
        dz = fz - math.floor(fz)

        g = self.gamma
        g000 = g[x0, y0, z0]
        g100 = g[x1, y0, z0]
        g010 = g[x0, y1, z0]
        g110 = g[x1, y1, z0]
        g001 = g[x0, y0, z1]
        g101 = g[x1, y0, z1]
        g011 = g[x0, y1, z1]
        g111 = g[x1, y1, z1]

        c00 = g000 * (1 - dx) + g100 * dx
        c10 = g010 * (1 - dx) + g110 * dx
        c01 = g001 * (1 - dx) + g101 * dx
        c11 = g011 * (1 - dx) + g111 * dx
        c0 = c00 * (1 - dy) + c10 * dy
        c1 = c01 * (1 - dy) + c11 * dy
        return c0 * (1 - dz) + c1 * dz

    def total_gamma(self):
        """Total gamma in field (for conservation check)."""
        return float(np.sum(self.gamma))

    def slice_xy(self, z):
        """2D XY slice at given z."""
        return self.gamma[:, :, int(z) % self.size].copy()

    def slice_xz(self, y):
        """2D XZ slice at given y."""
        return self.gamma[:, int(y) % self.size, :].copy()


# ===========================================================================
# MassiveBody — Rigid cluster with leapfrog dynamics
# ===========================================================================

class MassiveBody:
    """A rigid cluster of entities with KDK leapfrog dynamics.

    Point-source deposit: all gamma goes to one cell (body's center).
    Mass-conserving motion: withdraw from old position, deposit at new.
    No velocity drain — Bremsstrahlung is enhanced deposit only.
    """

    def __init__(self, label, center, n_entities, cluster_radius,
                 velocity=None, seed=42, color='blue'):
        self.label = label
        self.center = np.array(center, dtype=np.float64)
        self.velocity = np.array(velocity if velocity is not None else [0, 0, 0],
                                 dtype=np.float64)
        self.n_entities = n_entities
        self.cluster_radius = cluster_radius
        self.color = color
        self.pinned = False

        # Generate entity offsets within sphere (for reference / future use)
        rng = np.random.default_rng(seed)
        offsets = []
        while len(offsets) < n_entities:
            pt = rng.integers(-cluster_radius, cluster_radius + 1, size=3)
            if np.sum(pt ** 2) <= cluster_radius ** 2:
                offsets.append(pt)
        self.entity_offsets = np.array(offsets, dtype=np.int32)

        # Trajectory recording
        self.trajectory = []
        self.energy_history = []

        # Bremsstrahlung: last acceleration magnitude from kick().
        # Pinned bodies never kick, so this stays 0 — no radiation.
        self.last_accel = 0.0
        self.last_grad_mag = 0.0       # gradient magnitude at body position
        self.last_bremsstrahlung = 0.0  # KE drained by Bremsstrahlung (for field deposit)

        # Mass-conserving motion: track previous deposit cell
        self._prev_deposit_pos = None

    def deposit_formation(self, field):
        """Formation deposit: accumulate gamma to build the well. No withdrawal.

        Used during formation phase only. Deposits n_entities at center cell.
        Gamma accumulates over formation ticks to create the 1/r gravitational well.
        """
        s = field.size
        cx = int(round(self.center[0])) % s
        cy = int(round(self.center[1])) % s
        cz = int(round(self.center[2])) % s
        field.gamma[cx, cy, cz] += self.n_entities
        self._prev_deposit_pos = (cx, cy, cz)

    def deposit_dynamics(self, field):
        """Dynamics deposit: mass-conserving existence + Bremsstrahlung radiation.

        Existence: withdraw n_entities from old cell, deposit at new cell.
        This MOVES the body's gamma — no net existence gamma created.

        Radiation: deposit the drained KE from apply_bremsstrahlung_drain()
        into the field at the body's current position. Energy doesn't vanish —
        it becomes Bremsstrahlung radiation in the gamma field. Close encounters
        make the field brighter AND deeper — self-reinforcing gravitational wells.

        Withdrawal is capped at cell's current value to prevent negative gamma.
        The deficit (gamma that spread away between ticks) is a slow mass leak
        into the field — gravitational radiation from the body's existence.
        """
        s = field.size
        new_cx = int(round(self.center[0])) % s
        new_cy = int(round(self.center[1])) % s
        new_cz = int(round(self.center[2])) % s

        # Withdraw existence from previous cell
        if self._prev_deposit_pos is not None:
            ox, oy, oz = self._prev_deposit_pos
            withdraw = min(float(self.n_entities), float(field.gamma[ox, oy, oz]))
            field.gamma[ox, oy, oz] -= withdraw

        # Deposit existence at current cell
        field.gamma[new_cx, new_cy, new_cz] += self.n_entities

        # Bremsstrahlung radiation: drained KE distributed uniformly across field
        # (depositing at a single cell creates gradient spikes → runaway feedback)
        if self.last_bremsstrahlung > 1e-12:
            field.gamma += self.last_bremsstrahlung / field.gamma.size

        self._prev_deposit_pos = (new_cx, new_cy, new_cz)

    def deposit(self, field):
        """Legacy deposit for calibration (single field, accumulates)."""
        s = field.size
        cx = int(round(self.center[0])) % s
        cy = int(round(self.center[1])) % s
        cz = int(round(self.center[2])) % s
        field.gamma[cx, cy, cz] += self.n_entities
        # Bremsstrahlung distributed uniformly
        if self.last_bremsstrahlung > 1e-12:
            field.gamma += self.last_bremsstrahlung / field.gamma.size

    def kick(self, field, dt_half):
        """Half-step velocity update from field gradient."""
        if self.pinned:
            return
        grad = field.gradient_trilinear(self.center)
        grad_mag = float(np.linalg.norm(grad))
        self.velocity += grad * dt_half
        self.last_accel = grad_mag
        self.last_grad_mag = grad_mag

    def kick_with_gradient(self, grad, dt_half):
        """Half-step velocity update with pre-computed external gradient.

        Used with per-body fields where the external gradient (excluding
        self-field) is computed by the caller.
        """
        if self.pinned:
            return
        grad_mag = float(np.linalg.norm(grad))
        self.velocity += grad * dt_half
        self.last_accel = grad_mag
        self.last_grad_mag = grad_mag

    def drift(self, dt):
        """Full-step position update."""
        if self.pinned:
            return
        self.center += self.velocity * dt

    def apply_bremsstrahlung_drain(self, dt=1.0):
        """Asymptotic velocity drain — replaces hard v=1 clamp.

        Physics: faster entities moving through curved space (non-zero gradient)
        radiate energy into the field. drain = grad_mag * speed^3.
        At low speed (0.05c), drain ~ 0.000125 * grad (negligible).
        At 0.9c, drain ~ 0.729 * grad (massive).
        At 1.0c, drain would equal all energy — c is asymptotically unreachable.

        Drained KE is stored in last_bremsstrahlung for deposit into the field.
        """
        if self.pinned:
            self.last_bremsstrahlung = 0.0
            return
        speed = float(np.linalg.norm(self.velocity))
        if speed < 0.01:
            self.last_bremsstrahlung = 0.0
            return
        drain = self.last_grad_mag * speed ** 3
        drain_factor = max(1.0 - drain * dt, 0.01)  # never fully zero
        speed_before = speed
        self.velocity *= drain_factor
        speed_after = float(np.linalg.norm(self.velocity))
        # Drained KE = 0.5 * m * (v_before^2 - v_after^2)
        self.last_bremsstrahlung = 0.5 * self.n_entities * (speed_before**2 - speed_after**2)

    def wrap(self, grid_size):
        """Periodic wrapping."""
        self.center = self.center % grid_size

    def speed(self):
        return float(np.linalg.norm(self.velocity))

    def kinetic_energy(self):
        """KE = 0.5 * n_entities * |v|^2"""
        return 0.5 * self.n_entities * float(np.dot(self.velocity, self.velocity))

    def potential_energy(self, field):
        """PE = -gamma(center) * n_entities"""
        return -field.gamma_trilinear(self.center) * self.n_entities

    def record(self, tick, field=None, pe_override=None):
        """Record current state to trajectory."""
        self.trajectory.append({
            'tick': tick,
            'position': self.center.copy().tolist(),
            'velocity': self.velocity.copy().tolist(),
            'speed': self.speed(),
        })
        ke = self.kinetic_energy()
        if pe_override is not None:
            pe = pe_override
        elif field is not None:
            pe = self.potential_energy(field)
        else:
            pe = 0.0
        self.energy_history.append({
            'tick': tick,
            'KE': ke,
            'PE': pe,
            'E_total': ke + pe,
        })


def compute_com(bodies):
    """Center of mass of a list of bodies."""
    total_mass = sum(b.n_entities for b in bodies)
    if total_mass == 0:
        return np.zeros(3)
    com = sum(b.center * b.n_entities for b in bodies) / total_mass
    return com


def compute_angular_momentum(bodies, com=None):
    """Total angular momentum L = sum(m_i * (r_i - com) x v_i)."""
    if com is None:
        com = compute_com(bodies)
    L = np.zeros(3)
    for b in bodies:
        if b.pinned:
            continue
        r = b.center - com
        L += b.n_entities * np.cross(r, b.velocity)
    return L


def pairwise_distances(bodies):
    """Return dict of pairwise distances: {(label_i, label_j): dist}."""
    dists = {}
    for i in range(len(bodies)):
        for j in range(i + 1, len(bodies)):
            d = float(np.linalg.norm(bodies[i].center - bodies[j].center))
            dists[(bodies[i].label, bodies[j].label)] = d
    return dists


# ===========================================================================
# Simulation Engine
# ===========================================================================

def run_formation(field, depositing_bodies, formation_ticks, log_interval=100):
    """Formation phase: deposit + spread, no motion."""
    print(f"  Formation: {formation_ticks} ticks")
    t0 = time.time()
    gamma_initial = field.total_gamma()

    for tick in range(formation_ticks):
        for body in depositing_bodies:
            body.deposit(field)
        field.spread()

        if (tick + 1) % log_interval == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            gamma_now = field.total_gamma()
            print(f"    Formation tick {tick + 1:5d}/{formation_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"gamma={gamma_now:.0f}")

    elapsed = time.time() - t0
    gamma_final = field.total_gamma()
    dg = abs(gamma_final - gamma_initial) / max(gamma_initial, 1e-10)
    print(f"  Formation done in {elapsed:.1f}s, "
          f"gamma: {gamma_initial:.0f} -> {gamma_final:.0f} "
          f"(drift={dg:.2e})")


def diagnose_field_readiness(field, center, label="", test_radii=None):
    """Print gradient magnitude at key distances from center.

    Field is NOT ready for dynamics if grad_mag at r=30 is above ~0.01
    (too steep -> bodies immediately hit speed of light) or effectively
    zero (field hasn't spread far enough).

    Good range: grad_mag(r=30) ~ 0.0001 to 0.005
    """
    if test_radii is None:
        test_radii = [5, 10, 15, 20, 30, 40, 50]
    center = np.asarray(center, dtype=np.float64)

    print(f"\n  Field readiness diagnostic{' — ' + label if label else ''}:")
    print(f"    {'r':>4} {'gamma':>12} {'grad_mag':>12} {'status':>12}")
    print(f"    {'':->4}-+-{'':->12}-+-{'':->12}-+-{'':->12}")

    for r in test_radii:
        pos = center.copy()
        pos[0] += r
        if pos[0] >= field.size:
            continue
        g = field.gamma_trilinear(pos)
        grad = field.gradient_trilinear(pos)
        grad_mag = float(np.linalg.norm(grad))

        if grad_mag < 1e-8:
            status = "NOT REACHED"
        elif grad_mag > 0.01:
            status = "TOO STEEP"
        else:
            status = "ok"

        print(f"    {r:4d} | {g:12.6f} | {grad_mag:12.6f} | {status:>12}")

    # Highlight the critical r=30 check
    pos_30 = center.copy()
    pos_30[0] += 30
    if pos_30[0] < field.size:
        grad_30 = field.gradient_trilinear(pos_30)
        mag_30 = float(np.linalg.norm(grad_30))
        if mag_30 < 1e-8:
            print(f"    ** r=30 gradient is ZERO — field hasn't spread far enough. "
                  f"Increase formation ticks.")
        elif mag_30 > 0.01:
            print(f"    ** r=30 gradient is {mag_30:.6f} (> 0.01) — too steep, "
                  f"bodies will hit c immediately. Increase formation ticks.")
        else:
            v_circ = math.sqrt(mag_30 * 30)
            print(f"    ** r=30 gradient={mag_30:.6f}, v_circ~{v_circ:.4f}c — "
                  f"field looks ready")


def run_dynamics(field, bodies, dynamics_ticks, dt=1.0, max_speed=1.0,
                 spread_interval=1, log_interval=100, snapshot_interval=1000,
                 grid_size=128, detect_ejection=True, detect_collision=True):
    """Dynamics phase with KDK leapfrog.

    Returns diagnostics dict with energy, angular momentum, distances, events.
    """
    depositing_bodies = [b for b in bodies if not b.pinned or b.pinned]  # all deposit
    moving_bodies = [b for b in bodies if not b.pinned]

    diagnostics = {
        'energy': [],
        'angular_momentum': [],
        'distances': [],
        'events': [],
        'field_snapshots': [],
    }

    print(f"  Dynamics: {dynamics_ticks} ticks, dt={dt}, "
          f"spread_interval={spread_interval}")
    t0 = time.time()

    for tick in range(dynamics_ticks):
        # === COMMIT PHASE: spread previous tick's deposits ===
        if tick % spread_interval == 0:
            field.spread()

        # === READ PHASE: all gradient reads from committed field state ===
        # KDK leapfrog
        half_dt = dt * 0.5
        for body in moving_bodies:
            body.kick(field, half_dt)
        for body in moving_bodies:
            body.drift(dt)
        for body in moving_bodies:
            body.kick(field, half_dt)
            body.apply_bremsstrahlung_drain(dt)
            body.wrap(grid_size)

        # === WRITE PHASE: deposits after all reads (transactional isolation) ===
        for body in depositing_bodies:
            body.deposit(field)

        # Record every log_interval
        if (tick + 1) % log_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

            # Energy
            total_ke = sum(b.kinetic_energy() for b in bodies)
            total_pe = sum(b.potential_energy(field) for b in bodies)
            diagnostics['energy'].append({
                'tick': tick + 1,
                'KE': total_ke,
                'PE': total_pe,
                'E_total': total_ke + total_pe,
                'gamma_total': field.total_gamma(),
            })

            # Angular momentum
            com = compute_com(bodies)
            L = compute_angular_momentum(bodies, com)
            diagnostics['angular_momentum'].append({
                'tick': tick + 1,
                'Lx': float(L[0]),
                'Ly': float(L[1]),
                'Lz': float(L[2]),
                'L_mag': float(np.linalg.norm(L)),
            })

            # Pairwise distances
            dists = pairwise_distances(bodies)
            dist_entry = {'tick': tick + 1}
            for (la, lb), d in dists.items():
                dist_entry[f"{la}-{lb}"] = d
            diagnostics['distances'].append(dist_entry)

            # Detection
            if detect_ejection:
                for body in moving_bodies:
                    d_com = float(np.linalg.norm(body.center - com))
                    if d_com > 0.8 * grid_size:
                        event = f"EJECTION: {body.label} at tick {tick+1}, d_com={d_com:.1f}"
                        if event not in [e.get('msg') for e in diagnostics['events']]:
                            diagnostics['events'].append({
                                'type': 'ejection',
                                'body': body.label,
                                'tick': tick + 1,
                                'd_com': d_com,
                                'msg': event,
                            })
                            print(f"    *** {event}")

            if detect_collision:
                for i in range(len(moving_bodies)):
                    for j in range(i + 1, len(moving_bodies)):
                        d = float(np.linalg.norm(
                            moving_bodies[i].center - moving_bodies[j].center))
                        if d < 10:
                            event = (f"CLOSE ENCOUNTER: {moving_bodies[i].label}-"
                                     f"{moving_bodies[j].label} at tick {tick+1}, d={d:.1f}")
                            diagnostics['events'].append({
                                'type': 'close_encounter',
                                'bodies': [moving_bodies[i].label, moving_bodies[j].label],
                                'tick': tick + 1,
                                'distance': d,
                                'msg': event,
                            })

        # Field snapshots
        if (tick + 1) % snapshot_interval == 0:
            com = compute_com(bodies)
            snap_z = int(round(com[2])) % grid_size
            diagnostics['field_snapshots'].append({
                'tick': tick + 1,
                'slice_xy': field.slice_xy(snap_z),
                'z': snap_z,
            })

        # Progress logging
        if (tick + 1) % log_interval == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            body_info = "  ".join(
                f"{b.label}:v={b.speed():.4f}"
                for b in moving_bodies
            )
            print(f"    Tick {tick + 1:6d}/{dynamics_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) {body_info}")

    elapsed = time.time() - t0
    print(f"  Dynamics done in {elapsed:.1f}s")
    return diagnostics


def run_dynamics_multibody(per_body_fields, bodies, dynamics_ticks, dt=1.0,
                           max_speed=1.0, spread_interval=1, log_interval=100,
                           snapshot_interval=1000, grid_size=128,
                           detect_ejection=True, detect_collision=True):
    """Dynamics with per-body fields: no self-gravity, mass-conserving motion.

    Each body deposits into its own field. The gradient for each body is
    computed from the sum of ALL OTHER bodies' fields — the body never
    sees its own gamma well. This eliminates the self-gravity artifact
    that was freezing bodies.

    Mass-conserving: existence deposit withdraws from old cell, deposits at new.
    Bremsstrahlung: extra |accel| * n_entities deposited (new gamma, not withdrawn).
    No velocity drain: Bremsstrahlung is deposit-only.
    """
    moving_bodies = [b for b in bodies if not b.pinned]

    diagnostics = {
        'energy': [],
        'angular_momentum': [],
        'distances': [],
        'events': [],
        'field_snapshots': [],
    }

    # Gradient diagnostic at start (external only)
    print(f"\n  Gradient at body centers (external only, start of dynamics):")
    for body in moving_bodies:
        grad = np.zeros(3)
        for other in bodies:
            if other.label != body.label:
                grad += per_body_fields[other.label].gradient_trilinear(body.center)
        grad_mag = float(np.linalg.norm(grad))
        grad_dir = grad / grad_mag if grad_mag > 1e-12 else grad
        print(f"    {body.label}: |grad|={grad_mag:.6f}, "
              f"dir=({grad_dir[0]:+.3f},{grad_dir[1]:+.3f},{grad_dir[2]:+.3f})")

    total_gamma = sum(bf.total_gamma() for bf in per_body_fields.values())
    print(f"\n  Dynamics: {dynamics_ticks} ticks, dt={dt}, "
          f"spread_interval={spread_interval}, gamma_total={total_gamma:.0f}")
    t0 = time.time()

    for tick in range(dynamics_ticks):
        # === COMMIT PHASE: spread previous tick's deposits ===
        if tick % spread_interval == 0:
            for bf in per_body_fields.values():
                bf.spread()

        # === READ PHASE: all gradient reads from committed field state ===
        # KDK leapfrog with external gradients
        half_dt = dt * 0.5
        for body in moving_bodies:
            grad = np.zeros(3)
            for other in bodies:
                if other.label != body.label:
                    grad += per_body_fields[other.label].gradient_trilinear(body.center)
            body.kick_with_gradient(grad, half_dt)

        for body in moving_bodies:
            body.drift(dt)

        for body in moving_bodies:
            grad = np.zeros(3)
            for other in bodies:
                if other.label != body.label:
                    grad += per_body_fields[other.label].gradient_trilinear(body.center)
            body.kick_with_gradient(grad, half_dt)
            body.apply_bremsstrahlung_drain(dt)
            body.wrap(grid_size)

        # === WRITE PHASE: deposits after all reads (transactional isolation) ===
        for body in bodies:
            if body.pinned:
                body.deposit_formation(per_body_fields[body.label])
            else:
                body.deposit_dynamics(per_body_fields[body.label])

        # Record and diagnostics every log_interval
        if (tick + 1) % log_interval == 0:
            for body in bodies:
                ext_gamma = sum(
                    per_body_fields[other.label].gamma_trilinear(body.center)
                    for other in bodies if other.label != body.label
                )
                pe = -ext_gamma * body.n_entities
                body.record(tick + 1, pe_override=pe)

            # Energy
            total_ke = sum(b.kinetic_energy() for b in bodies)
            total_pe = 0.0
            for b in bodies:
                ext_gamma = sum(
                    per_body_fields[other.label].gamma_trilinear(b.center)
                    for other in bodies if other.label != b.label
                )
                total_pe += -ext_gamma * b.n_entities
            total_gamma = sum(bf.total_gamma() for bf in per_body_fields.values())
            diagnostics['energy'].append({
                'tick': tick + 1,
                'KE': total_ke,
                'PE': total_pe,
                'E_total': total_ke + total_pe,
                'gamma_total': total_gamma,
            })

            # Angular momentum
            com = compute_com(bodies)
            L = compute_angular_momentum(bodies, com)
            diagnostics['angular_momentum'].append({
                'tick': tick + 1,
                'Lx': float(L[0]),
                'Ly': float(L[1]),
                'Lz': float(L[2]),
                'L_mag': float(np.linalg.norm(L)),
            })

            # Pairwise distances
            dists = pairwise_distances(bodies)
            dist_entry = {'tick': tick + 1}
            for (la, lb), d in dists.items():
                dist_entry[f"{la}-{lb}"] = d
            diagnostics['distances'].append(dist_entry)

            # Detection
            if detect_ejection:
                for body in moving_bodies:
                    d_com = float(np.linalg.norm(body.center - com))
                    if d_com > 0.8 * grid_size:
                        event = f"EJECTION: {body.label} at tick {tick+1}, d_com={d_com:.1f}"
                        if event not in [e.get('msg') for e in diagnostics['events']]:
                            diagnostics['events'].append({
                                'type': 'ejection',
                                'body': body.label,
                                'tick': tick + 1,
                                'd_com': d_com,
                                'msg': event,
                            })
                            print(f"    *** {event}")

            if detect_collision:
                for i in range(len(moving_bodies)):
                    for j in range(i + 1, len(moving_bodies)):
                        d = float(np.linalg.norm(
                            moving_bodies[i].center - moving_bodies[j].center))
                        if d < 10:
                            event = (f"CLOSE ENCOUNTER: {moving_bodies[i].label}-"
                                     f"{moving_bodies[j].label} at tick {tick+1}, d={d:.1f}")
                            diagnostics['events'].append({
                                'type': 'close_encounter',
                                'bodies': [moving_bodies[i].label, moving_bodies[j].label],
                                'tick': tick + 1,
                                'distance': d,
                                'msg': event,
                            })

        # Field snapshots (total field from sum of per-body fields)
        if (tick + 1) % snapshot_interval == 0:
            com = compute_com(bodies)
            snap_z = int(round(com[2])) % grid_size
            total_arr = sum(bf.gamma for bf in per_body_fields.values())
            diagnostics['field_snapshots'].append({
                'tick': tick + 1,
                'slice_xy': total_arr[:, :, snap_z].copy(),
                'z': snap_z,
            })

        # Progress logging
        if (tick + 1) % log_interval == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            body_info = "  ".join(
                f"{b.label}:v={b.speed():.4f}" for b in moving_bodies
            )
            total_gamma = sum(bf.total_gamma() for bf in per_body_fields.values())
            print(f"    Tick {tick + 1:6d}/{dynamics_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) {body_info} "
                  f"gamma={total_gamma:.0f}")

    elapsed = time.time() - t0
    print(f"  Dynamics done in {elapsed:.1f}s")
    return diagnostics


# ===========================================================================
# Calibration
# ===========================================================================

def run_calibration(grid_size=128, formation_ticks=500, dynamics_ticks=5000,
                    spread_interval=1):
    """Single cluster + test particle infall calibration.

    Measures:
    - Infall time and max velocity
    - v_circular estimate at r=30
    - Gradient profile validation
    """
    print("=" * 60)
    print("CALIBRATION: Single cluster + test particle infall")
    print("=" * 60)
    print(f"  Grid: {grid_size}^3, formation: {formation_ticks}, "
          f"dynamics: {dynamics_ticks}")

    field = GammaField3D(grid_size)
    center = grid_size // 2

    # Create massive cluster at grid center
    cluster = MassiveBody(
        label="Cluster",
        center=[center, center, center],
        n_entities=200,
        cluster_radius=5,
        seed=42,
        color='red',
    )
    cluster.pinned = True  # Cluster stays, keeps depositing

    # Test particle at r=80 from center (or grid_size//2 - 16 for small grids)
    r_start = min(80, grid_size // 2 - 16)
    test_particle = MassiveBody(
        label="TestParticle",
        center=[center + r_start, center, center],
        n_entities=1,
        cluster_radius=0,
        velocity=[0, 0, 0],
        seed=99,
        color='blue',
    )

    # Formation (cluster only)
    run_formation(field, [cluster], formation_ticks)

    diagnose_field_readiness(field, [center, center, center], label="calibration")

    # Report gradient profile
    print("\n  Gradient profile after formation:")
    print(f"    {'r':>4} {'gamma':>12} {'grad_mag':>12}")
    for r in [5, 10, 15, 20, 30, 40, 50, 60]:
        if center + r >= grid_size:
            break
        pos = np.array([center + r, center, center], dtype=np.float64)
        g = field.gamma_trilinear(pos)
        grad = field.gradient_trilinear(pos)
        grad_mag = float(np.linalg.norm(grad))
        print(f"    {r:4d} {g:12.4f} {grad_mag:12.6f}")

    # Estimate v_circular at r=30
    r_circ = 30
    pos_circ = np.array([center + r_circ, center, center], dtype=np.float64)
    grad_circ = field.gradient_trilinear(pos_circ)
    grad_mag_circ = float(np.linalg.norm(grad_circ))
    v_circ = math.sqrt(grad_mag_circ * r_circ) if grad_mag_circ > 0 else 0
    print(f"\n  v_circular at r={r_circ}: {v_circ:.4f} "
          f"(grad_mag={grad_mag_circ:.6f})")

    # Dynamics (test particle only moves, cluster keeps depositing)
    print()
    diagnostics = run_dynamics(
        field, [cluster, test_particle],
        dynamics_ticks=dynamics_ticks,
        spread_interval=spread_interval,
        log_interval=100,
        snapshot_interval=1000,
        grid_size=grid_size,
        detect_ejection=False,
        detect_collision=False,
    )

    # Analyze infall
    max_speed = 0
    infall_tick = None
    for entry in test_particle.trajectory:
        s = entry['speed']
        if s > max_speed:
            max_speed = s
        dist = math.sqrt(sum((entry['position'][i] - center) ** 2 for i in range(3)))
        if dist < 5 and infall_tick is None:
            infall_tick = entry['tick']

    print(f"\n  Calibration results:")
    print(f"    Max velocity: {max_speed:.4f}c")
    print(f"    Infall tick:  {infall_tick}")
    print(f"    v_circular at r={r_circ}: {v_circ:.4f}c")

    # Plot
    _plot_calibration(test_particle, center, grid_size)

    # Save calibration data
    calibration = {
        'grid_size': grid_size,
        'formation_ticks': formation_ticks,
        'dynamics_ticks': dynamics_ticks,
        'max_speed': max_speed,
        'infall_tick': infall_tick,
        'v_circular_r30': v_circ,
        'gradient_at_r30': grad_mag_circ,
        'trajectory': test_particle.trajectory,
        'energy': diagnostics['energy'],
    }

    return calibration, v_circ


def _plot_calibration(test_particle, center, grid_size):
    """Plot calibration infall trajectory."""
    if not test_particle.trajectory:
        return

    ticks = [t['tick'] for t in test_particle.trajectory]
    dists = [math.sqrt(sum((t['position'][i] - center) ** 2 for i in range(3)))
             for t in test_particle.trajectory]
    speeds = [t['speed'] for t in test_particle.trajectory]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle("Calibration: Test Particle Infall", fontsize=14)

    ax1.plot(ticks, dists, 'b-', linewidth=0.8)
    ax1.set_xlabel("Tick")
    ax1.set_ylabel("Distance from center")
    ax1.set_title("Infall Distance")
    ax1.grid(True, alpha=0.3)

    ax2.plot(ticks, speeds, 'r-', linewidth=0.8)
    ax2.axhline(y=0.5, color='orange', linestyle='--', label='0.5c')
    ax2.axhline(y=1.0, color='red', linestyle='--', label='1.0c')
    ax2.set_xlabel("Tick")
    ax2.set_ylabel("Speed (c)")
    ax2.set_title("Speed vs Time")
    ax2.legend()
    ax2.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "calibration_infall.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: calibration_infall.png")


# ===========================================================================
# Phase 1: Equal-Mass Three-Body
# ===========================================================================

def run_phase1(grid_size=256, formation_ticks=500, dynamics_ticks=20000,
               spread_interval=1, use_tangential_velocity=False):
    """Phase 1: Three equal-mass bodies in triangular configuration.

    Uses per-body fields with translation optimization: form ONE reference
    field, then translate to each body's position. This is 1× formation cost
    instead of 3× (spreading is translation-invariant on periodic grid).
    """
    print("=" * 60)
    print("PHASE 1: Equal-Mass Three-Body Problem")
    print("=" * 60)
    print(f"  Grid: {grid_size}^3, formation: {formation_ticks}, "
          f"dynamics: {dynamics_ticks}, spread_interval: {spread_interval}")

    c = grid_size // 2  # center

    # Equilateral triangle in XY plane, separation ~100 cells.
    sep = 100
    R = sep / math.sqrt(3)  # ~58

    if use_tangential_velocity:
        v_tang = 0.02
        vel_a = [0, +v_tang, 0]
        vel_b = [0, -v_tang, 0]
        vel_c = [+v_tang, 0, 0]
        print(f"  Using tangential velocities: {v_tang}c")
    else:
        vel_a = vel_b = vel_c = [0, 0, 0]
        print(f"  Using zero initial velocities (Pythagorean problem)")

    # Vertices at 90°, 210°, 330° so A is above center on y-axis
    bodies = [
        MassiveBody("A",
                     center=[c, c + R, c],
                     n_entities=50, cluster_radius=5,
                     velocity=vel_a, seed=42, color='red'),
        MassiveBody("B",
                     center=[c + R * math.cos(math.radians(330)),
                             c + R * math.sin(math.radians(330)), c],
                     n_entities=50, cluster_radius=5,
                     velocity=vel_b, seed=43, color='green'),
        MassiveBody("C",
                     center=[c + R * math.cos(math.radians(210)),
                             c + R * math.sin(math.radians(210)), c],
                     n_entities=50, cluster_radius=5,
                     velocity=vel_c, seed=44, color='blue'),
    ]

    print(f"\n  Body positions:")
    for b in bodies:
        print(f"    {b.label}: center={b.center.tolist()}, "
              f"n={b.n_entities}, r={b.cluster_radius}")

    # --- Per-body fields with translation optimization ---
    # All bodies have equal mass (200 entities). Form ONE reference field
    # at grid center, then translate to each body's position via np.roll.
    # Spreading is translation-invariant on a periodic grid, so the
    # translated fields are exact.

    ref_center = [c, c, c]
    ref_body = MassiveBody("ref", center=ref_center, n_entities=50,
                            cluster_radius=5, seed=42)
    ref_field = GammaField3D(grid_size)

    print(f"\n  Formation (reference field, translate to 3 positions):")
    t0 = time.time()
    for tick in range(formation_ticks):
        ref_body.deposit_formation(ref_field)
        ref_field.spread()
        if (tick + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            print(f"    Formation tick {tick + 1:5d}/{formation_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"gamma={ref_field.total_gamma():.0f}")

    elapsed = time.time() - t0
    print(f"  Reference field done in {elapsed:.1f}s, "
          f"gamma={ref_field.total_gamma():.0f}")

    # Translate reference field to each body's position
    per_body_fields = {}
    for body in bodies:
        shift = tuple(int(round(body.center[i])) - ref_center[i] for i in range(3))
        bf = GammaField3D(grid_size)
        bf.gamma = np.roll(ref_field.gamma, shift=shift, axis=(0, 1, 2)).copy()
        per_body_fields[body.label] = bf
        # Set initial deposit position for mass-conserving dynamics
        body._prev_deposit_pos = (
            int(round(body.center[0])) % grid_size,
            int(round(body.center[1])) % grid_size,
            int(round(body.center[2])) % grid_size,
        )
        print(f"    {body.label}: translated by {shift}, "
              f"gamma={bf.total_gamma():.0f}")

    # Diagnose field readiness using total field
    total_field = GammaField3D(grid_size)
    total_field.gamma = sum(bf.gamma for bf in per_body_fields.values())
    com = compute_com(bodies)
    diagnose_field_readiness(total_field, com, label="phase 1")

    # Dynamics with per-body fields
    diagnostics = run_dynamics_multibody(
        per_body_fields, bodies,
        dynamics_ticks=dynamics_ticks,
        spread_interval=spread_interval,
        log_interval=100,
        snapshot_interval=1000,
        grid_size=grid_size,
    )

    # Analysis
    print(f"\n  Events detected: {len(diagnostics['events'])}")
    for event in diagnostics['events'][:20]:
        print(f"    {event['msg']}")

    if diagnostics['energy']:
        E0 = diagnostics['energy'][0]['E_total']
        Ef = diagnostics['energy'][-1]['E_total']
        dE = abs(Ef - E0) / abs(E0) if abs(E0) > 1e-10 else 0
        print(f"\n  Energy conservation: E0={E0:.2f}, Ef={Ef:.2f}, dE/E={dE:.4f}")

    # Plots
    plot_trajectories_3d(bodies, "phase1", grid_size)
    plot_trajectories_projections(bodies, "phase1", grid_size)
    plot_distances(diagnostics, "phase1")
    plot_energy(diagnostics, "phase1")
    plot_angular_momentum(diagnostics, "phase1")
    plot_field_slices(diagnostics, "phase1")

    return bodies, diagnostics


# ===========================================================================
# Phase 2: Asymmetric Mass (Proto-Atomic)
# ===========================================================================

PHASE2_CONFIGS = {
    'co-rotating': {
        'light1': {'pos_offset': [30, 0, 0], 'vel_dir': [0, 1, 0]},
        'light2': {'pos_offset': [0, 30, 0], 'vel_dir': [-1, 0, 0]},
    },
    'counter-rotating': {
        'light1': {'pos_offset': [30, 0, 0], 'vel_dir': [0, 1, 0]},
        'light2': {'pos_offset': [0, 30, 0], 'vel_dir': [1, 0, 0]},
    },
    'orthogonal': {
        'light1': {'pos_offset': [30, 0, 0], 'vel_dir': [0, 1, 0]},
        'light2': {'pos_offset': [0, 0, 30], 'vel_dir': [0, 0, -1]},
    },
    'single': {
        'light1': {'pos_offset': [30, 0, 0], 'vel_dir': [0, 1, 0]},
    },
}


def run_phase2(config_name='co-rotating', grid_size=128, formation_ticks=500,
               dynamics_ticks=20000, spread_interval=1, v_orb=0.03):
    """Phase 2: Heavy nucleus + light orbiting bodies.

    Uses per-body fields. Nucleus (pinned) forms its field during formation.
    Light bodies get empty fields (they start depositing during dynamics).
    """
    print("=" * 60)
    print(f"PHASE 2: Asymmetric Mass — {config_name}")
    print("=" * 60)
    print(f"  Grid: {grid_size}^3, formation: {formation_ticks}, "
          f"dynamics: {dynamics_ticks}, v_orb: {v_orb}")

    config = PHASE2_CONFIGS[config_name]
    c = grid_size // 2

    # Nucleus: pinned at center
    nucleus = MassiveBody(
        label="Nucleus",
        center=[c, c, c],
        n_entities=700,
        cluster_radius=8,
        seed=42,
        color='red',
    )
    nucleus.pinned = True

    bodies = [nucleus]

    # Light bodies
    for light_name, light_cfg in config.items():
        off = light_cfg['pos_offset']
        vel_dir = np.array(light_cfg['vel_dir'], dtype=np.float64)
        vel = vel_dir * v_orb

        body = MassiveBody(
            label=light_name.replace('light', 'L'),
            center=[c + off[0], c + off[1], c + off[2]],
            n_entities=5,
            cluster_radius=1,
            velocity=vel.tolist(),
            seed=50 + len(bodies),
            color='blue' if 'light1' in light_name else 'green',
        )
        bodies.append(body)

    print(f"\n  Bodies:")
    for b in bodies:
        pin_str = " (PINNED)" if b.pinned else ""
        print(f"    {b.label}: center={b.center.tolist()}, "
              f"n={b.n_entities}, v={b.velocity.tolist()}{pin_str}")

    # Per-body fields: nucleus gets formation, light bodies start empty
    per_body_fields = {b.label: GammaField3D(grid_size) for b in bodies}

    # Formation (nucleus only)
    print(f"\n  Formation (nucleus only):")
    t0 = time.time()
    nuc_field = per_body_fields[nucleus.label]
    for tick in range(formation_ticks):
        nucleus.deposit_formation(nuc_field)
        nuc_field.spread()
        if (tick + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = (tick + 1) / elapsed if elapsed > 0 else 0
            print(f"    Formation tick {tick + 1:5d}/{formation_ticks} "
                  f"({elapsed:6.1f}s, {rate:.0f} t/s) "
                  f"gamma={nuc_field.total_gamma():.0f}")
    elapsed = time.time() - t0
    print(f"  Formation done in {elapsed:.1f}s, "
          f"gamma={nuc_field.total_gamma():.0f}")

    # Set initial deposit positions for light bodies
    for body in bodies:
        if not body.pinned:
            body._prev_deposit_pos = (
                int(round(body.center[0])) % grid_size,
                int(round(body.center[1])) % grid_size,
                int(round(body.center[2])) % grid_size,
            )

    diagnose_field_readiness(nuc_field, [c, c, c], label=f"phase 2 ({config_name})")

    # Dynamics with per-body fields
    diagnostics = run_dynamics_multibody(
        per_body_fields, bodies,
        dynamics_ticks=dynamics_ticks,
        spread_interval=spread_interval,
        log_interval=100,
        snapshot_interval=1000,
        grid_size=grid_size,
        detect_ejection=True,
        detect_collision=False,
    )

    # Orbital analysis
    light_bodies = [b for b in bodies if not b.pinned]
    orbital_elements = compute_orbital_elements(light_bodies, nucleus.center)

    # Plots
    tag = f"phase2_{config_name}"
    plot_trajectories_3d(bodies, tag, grid_size)
    plot_trajectories_projections(bodies, tag, grid_size)
    plot_distances(diagnostics, tag)
    plot_energy(diagnostics, tag)
    plot_angular_momentum(diagnostics, tag)
    plot_field_slices(diagnostics, tag)
    plot_orbital_elements(orbital_elements, tag)

    return bodies, diagnostics, orbital_elements


def compute_orbital_elements(light_bodies, center):
    """Compute orbital elements (a, e, inclination) from trajectory data."""
    elements = {}
    center = np.array(center)

    for body in light_bodies:
        body_elements = {'a': [], 'e': [], 'i': [], 'ticks': []}

        for entry in body.trajectory:
            pos = np.array(entry['position'])
            vel = np.array(entry['velocity'])
            r_vec = pos - center
            r = np.linalg.norm(r_vec)
            v = np.linalg.norm(vel)

            if r < 1e-6 or v < 1e-10:
                continue

            # Specific angular momentum
            h_vec = np.cross(r_vec, vel)
            h = np.linalg.norm(h_vec)

            # Semi-latus rectum and eccentricity (using vis-viva approximation)
            # For our substrate: "GM" is emergent from field, approximate from gradient
            # Use energy-based approach: E = 0.5*v^2 - mu/r => a = -mu/(2E)
            # We don't have explicit mu, so use geometric estimates

            # Semi-major axis estimate from average of apoapsis and periapsis
            # Simple: a ~ r (current distance as rough estimate)
            a = r

            # Eccentricity from e_vec = (v x h)/mu - r_hat
            # Without mu, estimate from r and v
            # Circular orbit: v_circ = sqrt(mu/r), e = |v/v_circ - 1| approximately
            # Use h^2 / (mu * a * (1-e^2)) identity... skip, just record r
            e = 0.0  # placeholder

            # Inclination from angular momentum vector
            if h > 1e-10:
                cos_i = h_vec[2] / h
                i_deg = math.degrees(math.acos(max(-1, min(1, cos_i))))
            else:
                i_deg = 0

            body_elements['a'].append(a)
            body_elements['e'].append(e)
            body_elements['i'].append(i_deg)
            body_elements['ticks'].append(entry['tick'])

        elements[body.label] = body_elements

    return elements


# ===========================================================================
# Phase 3: Magnetic Emergence Detection
# ===========================================================================

def run_phase3(phase2_results, grid_size=128):
    """Phase 3: Post-processing on Phase 2 field snapshots.

    Analyzes tangential gradient decomposition, asymmetry sign,
    inter-orbit coupling, and velocity-dependent deflection.
    """
    print("=" * 60)
    print("PHASE 3: Magnetic Emergence Detection")
    print("=" * 60)

    results = {}

    # Process each Phase 2 configuration
    for config_name, (bodies, diagnostics, orbital_elements) in phase2_results.items():
        print(f"\n  Analyzing: {config_name}")

        # Get last field snapshot
        if not diagnostics['field_snapshots']:
            print(f"    No field snapshots available, skipping")
            continue

        last_snap = diagnostics['field_snapshots'][-1]
        field_slice = last_snap['slice_xy']
        center = grid_size // 2

        # 1. Tangential gradient decomposition at multiple radii
        tang_analysis = tangential_decomposition(field_slice, center,
                                                  radii=[20, 25, 30, 35, 40])

        # 2. Orbital coupling metrics
        coupling = {}
        light_bodies = [b for b in bodies if not b.pinned]
        for body in light_bodies:
            if body.trajectory:
                dists = [math.sqrt(sum((t['position'][i] - center) ** 2
                                       for i in range(3)))
                         for t in body.trajectory]
                speeds = [t['speed'] for t in body.trajectory]
                coupling[body.label] = {
                    'mean_r': float(np.mean(dists)),
                    'std_r': float(np.std(dists)),
                    'mean_speed': float(np.mean(speeds)),
                    'std_speed': float(np.std(speeds)),
                    'n_points': len(dists),
                }

        results[config_name] = {
            'tangential': tang_analysis,
            'coupling': coupling,
        }

        print(f"    Tangential analysis at radii 20-40:")
        for r_data in tang_analysis:
            print(f"      r={r_data['radius']:2d}: "
                  f"mean_tang={r_data['mean_tangential']:.6f}, "
                  f"fourier_m1={r_data['fourier_modes'].get(1, 0):.4f}")

    # 3. Compare co-rotating vs counter-rotating
    comparison = compare_configurations(results)

    # Plot
    plot_tangential_analysis(results, grid_size)

    return results, comparison


def tangential_decomposition(field_slice, center, radii=None):
    """Angular decomposition of gamma field at given radii from center.

    At each radius, samples gamma around a circle in the XY plane,
    computes tangential gradient component, and Fourier modes.
    """
    if radii is None:
        radii = [20, 25, 30, 35, 40]

    results = []
    n_samples = 64  # angular samples

    for r in radii:
        gamma_angular = []
        tangential_grad = []
        angles = np.linspace(0, 2 * np.pi, n_samples, endpoint=False)

        for theta in angles:
            x = center + r * math.cos(theta)
            y = center + r * math.sin(theta)

            # Sample gamma (bilinear on 2D slice)
            xi = int(x) % field_slice.shape[0]
            yi = int(y) % field_slice.shape[1]
            gamma_angular.append(field_slice[xi, yi])

            # Tangential direction: (-sin(theta), cos(theta))
            # Gradient in the slice (central differences)
            s = field_slice.shape[0]
            gx = (field_slice[(xi + 1) % s, yi] - field_slice[(xi - 1) % s, yi]) / 2.0
            gy = (field_slice[xi, (yi + 1) % s] - field_slice[xi, (yi - 1) % s]) / 2.0

            tang_dir = np.array([-math.sin(theta), math.cos(theta)])
            tang_comp = gx * tang_dir[0] + gy * tang_dir[1]
            tangential_grad.append(tang_comp)

        gamma_angular = np.array(gamma_angular)
        tangential_grad = np.array(tangential_grad)

        # Fourier decomposition of angular profile
        fft = np.fft.fft(gamma_angular)
        power = np.abs(fft) ** 2
        total_power = np.sum(power[1:])  # exclude DC
        fourier_modes = {}
        for m in range(1, 9):
            if m < len(power):
                fourier_modes[m] = float(power[m] / total_power) if total_power > 0 else 0

        results.append({
            'radius': r,
            'mean_gamma': float(np.mean(gamma_angular)),
            'std_gamma': float(np.std(gamma_angular)),
            'mean_tangential': float(np.mean(tangential_grad)),
            'std_tangential': float(np.std(tangential_grad)),
            'max_tangential': float(np.max(np.abs(tangential_grad))),
            'fourier_modes': fourier_modes,
        })

    return results


def compare_configurations(results):
    """Compare co-rotating vs counter-rotating configurations."""
    comparison = {}

    if 'co-rotating' in results and 'counter-rotating' in results:
        co = results['co-rotating']
        counter = results['counter-rotating']

        # Compare tangential means
        for i, r_co in enumerate(co['tangential']):
            r_counter = counter['tangential'][i]
            r = r_co['radius']
            comparison[f"r={r}"] = {
                'co_tang': r_co['mean_tangential'],
                'counter_tang': r_counter['mean_tangential'],
                'sign_reversal': (r_co['mean_tangential'] * r_counter['mean_tangential'] < 0),
            }

        # Compare orbital stability
        for key in ['light1', 'light2']:
            label = key.replace('light', 'L')
            if label in co.get('coupling', {}) and label in counter.get('coupling', {}):
                comparison[f"{label}_stability"] = {
                    'co_std_r': co['coupling'][label]['std_r'],
                    'counter_std_r': counter['coupling'][label]['std_r'],
                }

    if 'single' in results:
        comparison['single_baseline'] = results['single'].get('coupling', {})

    # Print summary
    print(f"\n  Configuration comparison:")
    for key, val in comparison.items():
        if isinstance(val, dict) and 'sign_reversal' in val:
            tag = "MAGNETIC SIGNATURE" if val['sign_reversal'] else "no reversal"
            print(f"    {key}: co={val['co_tang']:.6f}, "
                  f"counter={val['counter_tang']:.6f} -> {tag}")

    return comparison


# ===========================================================================
# Plotting Functions
# ===========================================================================

def plot_trajectories_3d(bodies, tag, grid_size):
    """3D trajectory plot, color-coded per body."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection='3d')

    for body in bodies:
        if not body.trajectory:
            continue
        xs = [t['position'][0] for t in body.trajectory]
        ys = [t['position'][1] for t in body.trajectory]
        zs = [t['position'][2] for t in body.trajectory]
        ax.plot(xs, ys, zs, '-', color=body.color, linewidth=0.5,
                label=f"{body.label} (n={body.n_entities})", alpha=0.8)
        # Mark start and end
        if xs:
            ax.scatter([xs[0]], [ys[0]], [zs[0]], color=body.color, s=50, marker='o')
            ax.scatter([xs[-1]], [ys[-1]], [zs[-1]], color=body.color, s=50, marker='s')

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title(f"3D Trajectories — {tag}")
    ax.legend(fontsize=8)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"trajectories_3d_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: trajectories_3d_{tag}.png")


def plot_trajectories_projections(bodies, tag, grid_size):
    """XY, XZ, YZ projection panels."""
    fig, axes = plt.subplots(1, 3, figsize=(18, 5))
    fig.suptitle(f"Trajectory Projections — {tag}", fontsize=14)

    projections = [
        (0, 1, "X", "Y", "XY"),
        (0, 2, "X", "Z", "XZ"),
        (1, 2, "Y", "Z", "YZ"),
    ]

    for ax, (i, j, xlabel, ylabel, title) in zip(axes, projections):
        for body in bodies:
            if not body.trajectory:
                continue
            coords_i = [t['position'][i] for t in body.trajectory]
            coords_j = [t['position'][j] for t in body.trajectory]
            ax.plot(coords_i, coords_j, '-', color=body.color, linewidth=0.5,
                    label=body.label, alpha=0.8)
            if coords_i:
                ax.plot(coords_i[0], coords_j[0], 'o', color=body.color, markersize=6)
                ax.plot(coords_i[-1], coords_j[-1], 's', color=body.color, markersize=6)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.set_aspect('equal')
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"projections_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: projections_{tag}.png")


def plot_distances(diagnostics, tag):
    """Pairwise distance vs tick."""
    if not diagnostics['distances']:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ticks = [d['tick'] for d in diagnostics['distances']]

    # Get all pair keys
    pair_keys = [k for k in diagnostics['distances'][0].keys() if k != 'tick']
    colors_cycle = plt.cm.tab10(np.linspace(0, 1, max(len(pair_keys), 1)))

    for i, key in enumerate(pair_keys):
        vals = [d.get(key, 0) for d in diagnostics['distances']]
        ax.plot(ticks, vals, '-', color=colors_cycle[i], linewidth=0.8, label=key)

    ax.set_xlabel("Tick")
    ax.set_ylabel("Distance")
    ax.set_title(f"Pairwise Distances — {tag}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"distances_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: distances_{tag}.png")


def plot_energy(diagnostics, tag):
    """KE, PE, total E vs time."""
    if not diagnostics['energy']:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ticks = [e['tick'] for e in diagnostics['energy']]
    KE = [e['KE'] for e in diagnostics['energy']]
    PE = [e['PE'] for e in diagnostics['energy']]
    E_total = [e['E_total'] for e in diagnostics['energy']]

    ax.plot(ticks, KE, 'r-', linewidth=0.8, label='KE')
    ax.plot(ticks, PE, 'b-', linewidth=0.8, label='PE')
    ax.plot(ticks, E_total, 'k-', linewidth=1.2, label='E_total')

    ax.set_xlabel("Tick")
    ax.set_ylabel("Energy")
    ax.set_title(f"Energy — {tag}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"energy_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: energy_{tag}.png")


def plot_angular_momentum(diagnostics, tag):
    """L_x, L_y, L_z, |L| vs time."""
    if not diagnostics['angular_momentum']:
        return

    fig, ax = plt.subplots(figsize=(12, 5))
    ticks = [a['tick'] for a in diagnostics['angular_momentum']]
    Lx = [a['Lx'] for a in diagnostics['angular_momentum']]
    Ly = [a['Ly'] for a in diagnostics['angular_momentum']]
    Lz = [a['Lz'] for a in diagnostics['angular_momentum']]
    L_mag = [a['L_mag'] for a in diagnostics['angular_momentum']]

    ax.plot(ticks, Lx, 'r-', linewidth=0.5, label='Lx', alpha=0.7)
    ax.plot(ticks, Ly, 'g-', linewidth=0.5, label='Ly', alpha=0.7)
    ax.plot(ticks, Lz, 'b-', linewidth=0.5, label='Lz', alpha=0.7)
    ax.plot(ticks, L_mag, 'k-', linewidth=1.0, label='|L|')

    ax.set_xlabel("Tick")
    ax.set_ylabel("Angular Momentum")
    ax.set_title(f"Angular Momentum — {tag}")
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"angular_momentum_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: angular_momentum_{tag}.png")


def plot_field_slices(diagnostics, tag):
    """Gamma field XY slices at key moments."""
    snapshots = diagnostics.get('field_snapshots', [])
    if not snapshots:
        return

    n = min(len(snapshots), 6)
    indices = [int(i * (len(snapshots) - 1) / max(n - 1, 1)) for i in range(n)]
    selected = [snapshots[i] for i in indices]

    fig, axes = plt.subplots(1, n, figsize=(4 * n, 4))
    if n == 1:
        axes = [axes]

    for ax, snap in zip(axes, selected):
        sl = snap['slice_xy']
        im = ax.imshow(sl.T, origin='lower', cmap='inferno',
                       vmin=0, vmax=max(np.max(sl), 1e-6))
        ax.set_title(f"t={snap['tick']}, z={snap['z']}")
        plt.colorbar(im, ax=ax, shrink=0.7)

    fig.suptitle(f"Gamma Field Slices — {tag}", fontsize=13)
    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"field_slices_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: field_slices_{tag}.png")


def plot_orbital_elements(orbital_elements, tag):
    """Plot orbital radius and inclination vs time."""
    if not orbital_elements:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle(f"Orbital Elements — {tag}", fontsize=14)

    colors_cycle = ['blue', 'green', 'orange', 'purple']

    for idx, (label, elems) in enumerate(orbital_elements.items()):
        if not elems['ticks']:
            continue
        color = colors_cycle[idx % len(colors_cycle)]

        axes[0].plot(elems['ticks'], elems['a'], '-', color=color,
                     linewidth=0.5, label=f"{label} r", alpha=0.8)
        axes[1].plot(elems['ticks'], elems['i'], '-', color=color,
                     linewidth=0.5, label=f"{label} i", alpha=0.8)

    axes[0].set_xlabel("Tick")
    axes[0].set_ylabel("Orbital Distance")
    axes[0].set_title("Distance from Nucleus")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    axes[1].set_xlabel("Tick")
    axes[1].set_ylabel("Inclination (deg)")
    axes[1].set_title("Orbital Inclination")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / f"orbital_elements_{tag}.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: orbital_elements_{tag}.png")


def plot_tangential_analysis(results, grid_size):
    """Tangential gradient analysis plots for Phase 3."""
    configs = list(results.keys())
    if not configs:
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.suptitle("Phase 3: Tangential Gradient Analysis", fontsize=14)
    colors = {'co-rotating': 'blue', 'counter-rotating': 'red',
              'orthogonal': 'green', 'single': 'gray'}

    # Mean tangential gradient vs radius
    for config_name in configs:
        tang = results[config_name].get('tangential', [])
        if not tang:
            continue
        radii = [t['radius'] for t in tang]
        means = [t['mean_tangential'] for t in tang]
        stds = [t['std_tangential'] for t in tang]
        c = colors.get(config_name, 'black')
        axes[0].errorbar(radii, means, yerr=stds, fmt='o-', color=c,
                         label=config_name, capsize=3)

    axes[0].axhline(y=0, color='black', linestyle='--', alpha=0.3)
    axes[0].set_xlabel("Radius from Nucleus")
    axes[0].set_ylabel("Mean Tangential Gradient")
    axes[0].set_title("Tangential Asymmetry vs Radius")
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Fourier mode power
    for config_name in configs:
        tang = results[config_name].get('tangential', [])
        if not tang:
            continue
        # Average Fourier modes across radii
        avg_modes = {}
        for m in range(1, 9):
            vals = [t['fourier_modes'].get(m, 0) for t in tang]
            avg_modes[m] = np.mean(vals)
        modes = list(avg_modes.keys())
        powers = list(avg_modes.values())
        c = colors.get(config_name, 'black')
        axes[1].plot(modes, powers, 'o-', color=c, label=config_name)

    axes[1].set_xlabel("Fourier Mode m")
    axes[1].set_ylabel("Normalized Power")
    axes[1].set_title("Angular Fourier Decomposition")
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    fig.savefig(RESULTS_DIR / "tangential_analysis.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: tangential_analysis.png")


# ===========================================================================
# JSON Export
# ===========================================================================

def save_results(all_results, filename="experiment_results.json"):
    """Save all numerical data to JSON."""

    def make_serializable(obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [make_serializable(v) for v in obj]
        return obj

    clean = make_serializable(all_results)

    path = RESULTS_DIR / filename
    with open(path, 'w') as f:
        json.dump(clean, f, indent=2, default=str)
    print(f"\n  Results saved to: {path}")


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification():
    """Quick verification tests for correctness."""
    print("=" * 60)
    print("VERIFICATION TESTS")
    print("=" * 60)
    all_passed = True

    # Test 1: Spreading conservation
    print("\n  Test 1: Spreading conservation")
    field = GammaField3D(32)
    field.deposit(16, 16, 16, 1000.0)
    gamma_before = field.total_gamma()
    for _ in range(500):
        field.spread()
    gamma_after = field.total_gamma()
    drift = abs(gamma_after - gamma_before) / gamma_before
    passed = drift < 1e-10
    print(f"    Before: {gamma_before:.6f}, After: {gamma_after:.6f}, "
          f"Drift: {drift:.2e} -> {'PASS' if passed else 'FAIL'}")
    all_passed &= passed

    # Test 2: Spreading profile (1/r steady state)
    print("\n  Test 2: Spreading profile (should approach 1/r)")
    field = GammaField3D(64)
    c = 32
    for _ in range(1000):
        field.deposit(c, c, c, 1.0)
        field.spread()
    # Check gamma at various distances
    print(f"    {'r':>4} {'gamma':>12} {'expected_1/r':>12} {'ratio':>8}")
    g_at_5 = field.gamma[c + 5, c, c]
    for r in [5, 10, 15, 20, 25]:
        g = field.gamma[c + r, c, c]
        expected_ratio = 5.0 / r  # relative to r=5
        actual_ratio = g / g_at_5 if g_at_5 > 0 else 0
        print(f"    {r:4d} {g:12.4f} {expected_ratio:12.4f} {actual_ratio:8.4f}")

    # Test 3: Gradient direction
    print("\n  Test 3: Gradient points toward gamma hill")
    grad = field.gradient_at(c + 10, c, c)
    points_inward = grad[0] < 0  # Should point toward center (negative x)
    print(f"    Gradient at (c+10,c,c): ({grad[0]:.6f}, {grad[1]:.6f}, {grad[2]:.6f})")
    print(f"    Points toward center: {'PASS' if points_inward else 'FAIL'}")
    all_passed &= points_inward

    # Test 4: Trilinear smoothness
    print("\n  Test 4: Trilinear interpolation smoothness")
    pos_int = np.array([c + 10.0, c, c])
    pos_frac = np.array([c + 10.5, c, c])
    g_int = field.gamma_trilinear(pos_int)
    g_frac = field.gamma_trilinear(pos_frac)
    g_next = field.gamma_trilinear(np.array([c + 11.0, c, c]))
    # Fractional should be between integer neighbors
    between = min(g_int, g_next) <= g_frac <= max(g_int, g_next)
    print(f"    gamma(10.0)={g_int:.4f}, gamma(10.5)={g_frac:.4f}, "
          f"gamma(11.0)={g_next:.4f}")
    print(f"    Interpolation between neighbors: {'PASS' if between else 'FAIL'}")
    all_passed &= between

    # Test 5: Gradient scaling (1/r field -> 1/r^2 gradient)
    print("\n  Test 5: Gradient scaling")
    g10 = np.linalg.norm(field.gradient_at(c + 10, c, c))
    g20 = np.linalg.norm(field.gradient_at(c + 20, c, c))
    if g10 > 0 and g20 > 0:
        ratio = g20 / g10
        expected = (10.0 / 20.0) ** 2  # 0.25 for 1/r^2
        print(f"    grad(r=10)={g10:.6f}, grad(r=20)={g20:.6f}")
        print(f"    Ratio: {ratio:.4f} (expected ~{expected:.4f} for 1/r^2)")
    else:
        print(f"    Gradient too small to test")

    print(f"\n  Overall: {'ALL PASSED' if all_passed else 'SOME FAILED'}")
    return all_passed


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Experiment #64 — Three-Body Gravitational Dynamics"
    )
    parser.add_argument(
        "--calibrate", action="store_true",
        help="Run calibration (single cluster + test particle infall)",
    )
    parser.add_argument(
        "--phase", type=int, choices=[1, 2, 3],
        help="Run specific phase (1=equal-mass, 2=asymmetric, 3=magnetic)",
    )
    parser.add_argument(
        "--all", action="store_true",
        help="Run all phases",
    )
    parser.add_argument(
        "--verify", action="store_true",
        help="Run verification tests only",
    )
    parser.add_argument(
        "--quick", action="store_true",
        help="Quick mode: 128^3 grid, fewer ticks",
    )
    parser.add_argument(
        "--config", type=str, default=None,
        choices=list(PHASE2_CONFIGS.keys()),
        help="Phase 2 configuration (default: run all)",
    )
    parser.add_argument(
        "--spread-interval", type=int, default=1,
        help="Spread every N ticks (default: 1, higher = faster)",
    )
    parser.add_argument(
        "--formation-ticks", type=int, default=None,
        help="Override formation ticks",
    )
    parser.add_argument(
        "--dynamics-ticks", type=int, default=None,
        help="Override dynamics ticks",
    )
    parser.add_argument(
        "--v-orb", type=float, default=None,
        help="Override orbital velocity for Phase 2 (default: from calibration or 0.03)",
    )
    parser.add_argument(
        "--tangential-velocity", action="store_true",
        help="Phase 1: use small tangential velocities instead of zero",
    )
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Quick mode overrides
    if args.quick:
        grid_1 = 128
        dynamics_1 = args.dynamics_ticks or 5000
        grid_2 = 128
        dynamics_2 = args.dynamics_ticks or 5000
    else:
        grid_1 = 256
        dynamics_1 = args.dynamics_ticks or 20000
        grid_2 = 128
        dynamics_2 = args.dynamics_ticks or 20000

    formation = args.formation_ticks or 1000
    spread_interval = args.spread_interval
    v_orb = args.v_orb or 0.03

    all_results = {}

    if args.verify:
        run_verification()
        return

    if args.calibrate or args.all:
        cal, v_circ = run_calibration(
            grid_size=128,
            formation_ticks=formation,
            dynamics_ticks=args.dynamics_ticks or 5000,
            spread_interval=spread_interval,
        )
        all_results['calibration'] = cal
        # Don't use auto-calibrated v_circ for Phase 2 — it's computed from
        # a snapshot of a non-stationary field (continuous deposition during
        # dynamics changes the gradient profile). 0.03c is the right ballpark
        # based on the test particle showing 0.05c max at r=48.
        print(f"\n  Calibrated v_circ = {v_circ:.4f}c (informational only, "
              f"v_orb stays at {v_orb:.4f}c)")

    if args.phase == 1 or args.all:
        bodies, diag = run_phase1(
            grid_size=grid_1,
            formation_ticks=formation,
            dynamics_ticks=dynamics_1,
            spread_interval=spread_interval,
            use_tangential_velocity=args.tangential_velocity,
        )
        all_results['phase1'] = {
            'energy': diag['energy'],
            'angular_momentum': diag['angular_momentum'],
            'distances': diag['distances'],
            'events': [e for e in diag['events'] if 'msg' in e],
            'trajectories': {b.label: b.trajectory for b in bodies},
        }

    if args.phase == 2 or args.all:
        phase2_results = {}
        configs_to_run = [args.config] if args.config else list(PHASE2_CONFIGS.keys())

        for config_name in configs_to_run:
            bodies, diag, orb_elem = run_phase2(
                config_name=config_name,
                grid_size=grid_2,
                formation_ticks=formation,
                dynamics_ticks=dynamics_2,
                spread_interval=spread_interval,
                v_orb=v_orb,
            )
            phase2_results[config_name] = (bodies, diag, orb_elem)
            all_results[f'phase2_{config_name}'] = {
                'energy': diag['energy'],
                'angular_momentum': diag['angular_momentum'],
                'distances': diag['distances'],
                'events': [e for e in diag['events'] if 'msg' in e],
                'trajectories': {b.label: b.trajectory for b in bodies},
                'orbital_elements': orb_elem,
            }

        # Phase 3 runs on Phase 2 results
        if args.phase == 2 or args.all:
            if len(phase2_results) > 1:
                p3_results, comparison = run_phase3(phase2_results, grid_size=grid_2)
                all_results['phase3'] = {
                    'tangential_analysis': {
                        k: v.get('tangential', [])
                        for k, v in p3_results.items()
                    },
                    'comparison': comparison,
                }

    if args.phase == 3:
        print("Phase 3 requires Phase 2 results. Run with --phase 2 or --all.")
        return

    # Save all results
    if all_results:
        save_results(all_results)

    print("\n" + "=" * 60)
    print("EXPERIMENT #64 COMPLETE")
    print("=" * 60)


if __name__ == "__main__":
    main()
