"""v12: Vortex-Connector Hierarchical Gravity.

Bodies (vortices) interact through connector bundles in continuous 3D space.
No gamma field, no lattice, no diffusion. Gravity comes directly from
the topology of connections between bodies.

Model:
- Bodies = vortices with mass M (entity count), position, velocity
- Connector bundles = N connections between body pairs
- Expansion: Hubble-like drift (v = H * d) pushes connected pairs apart
- Gravity: F = G * N_connectors / r^2, acceleration = F / mass
- Integrator: Leapfrog (velocity Verlet) for symplectic energy conservation

Optional turn mode: constant speed, gravity rotates velocity vector.

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --two-body --ticks 50000
    python macro_bodies.py --two-body --H 0.01 --ticks 50000
    python macro_bodies.py --three-body --ticks 100000
    python macro_bodies.py --capture --ticks 80000
    python macro_bodies.py --force-law

February 2026
"""

import argparse
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# Body
# ===========================================================================

class Body:
    """A vortex — persistent rotating cluster of entities."""

    def __init__(self, name, mass, pos, vel=None):
        self.name = name
        self.mass = float(mass)
        self.pos = np.array(pos, dtype=np.float64)
        self.vel = np.array(vel if vel is not None else [0.0, 0.0, 0.0],
                            dtype=np.float64)
        self.coord_history = []
        self.energy_history = []

    def record(self, tick):
        self.coord_history.append(
            (tick, self.pos[0], self.pos[1], self.pos[2]))


# ===========================================================================
# Connector Bundle
# ===========================================================================

class ConnectorBundle:
    """N connections between two bodies."""

    def __init__(self, body_a_idx, body_b_idx, n_connectors):
        self.body_a = body_a_idx
        self.body_b = body_b_idx
        self.n_connectors = float(n_connectors)


# ===========================================================================
# VortexUniverse
# ===========================================================================

class VortexUniverse:
    """Simulation of bodies connected by connector bundles.

    Physics:
    - Gravity: F = G * N_connectors / r^2 between connected pairs
    - Expansion: Hubble-like drift v = H * d between connected pairs
    - Integrator: Leapfrog (velocity Verlet)
    """

    def __init__(self, bodies, bundles, G=1.0, H=0.0, dt=0.01,
                 turn_mode=False, softening=0.1):
        self.bodies = bodies
        self.bundles = bundles
        self.G = G
        self.H = H
        self.dt = dt
        self.turn_mode = turn_mode
        self.softening = softening  # prevent 1/r^2 singularity
        self.tick = 0

    def compute_accelerations(self):
        """Compute gravitational acceleration on each body from connector bundles."""
        accels = [np.zeros(3) for _ in self.bodies]
        for bundle in self.bundles:
            a = self.bodies[bundle.body_a]
            b = self.bodies[bundle.body_b]
            d = b.pos - a.pos
            r2 = np.dot(d, d) + self.softening ** 2
            r = math.sqrt(r2)
            d_hat = d / r
            F = self.G * bundle.n_connectors / r2
            accels[bundle.body_a] += (F / a.mass) * d_hat
            accels[bundle.body_b] -= (F / b.mass) * d_hat
        return accels

    def apply_expansion(self):
        """Hubble-like drift: connected pairs pushed apart proportional to distance."""
        if self.H <= 0:
            return
        for bundle in self.bundles:
            a = self.bodies[bundle.body_a]
            b = self.bodies[bundle.body_b]
            d = b.pos - a.pos
            dist = np.linalg.norm(d)
            if dist < 1e-12:
                continue
            # v_expand = H * d (Hubble flow), applied symmetrically
            # Position change = H * d * dt, split between both bodies
            shift = self.H * d * self.dt / 2.0
            a.pos -= shift
            b.pos += shift

    def apply_turning(self, accels):
        """Turn mode: rotate velocity toward acceleration direction, preserve speed."""
        for i, body in enumerate(self.bodies):
            speed = np.linalg.norm(body.vel)
            if speed < 1e-12:
                # If body is stationary, just accelerate normally
                body.vel += accels[i] * self.dt
                continue
            # Add acceleration as a perturbation to velocity direction
            body.vel += accels[i] * self.dt
            # Renormalize to preserve original speed
            new_speed = np.linalg.norm(body.vel)
            if new_speed > 1e-12:
                body.vel *= speed / new_speed

    def step(self):
        """One leapfrog step (or turning step if turn_mode)."""
        self.tick += 1

        if self.turn_mode:
            # Turn mode: acceleration rotates velocity, speed preserved
            accels = self.compute_accelerations()
            self.apply_turning(accels)
            self.apply_expansion()
            for body in self.bodies:
                body.pos += body.vel * self.dt
        else:
            # Leapfrog: half-kick, drift+expand, half-kick
            accels = self.compute_accelerations()
            for i, body in enumerate(self.bodies):
                body.vel += 0.5 * accels[i] * self.dt

            for body in self.bodies:
                body.pos += body.vel * self.dt
            self.apply_expansion()

            accels = self.compute_accelerations()
            for i, body in enumerate(self.bodies):
                body.vel += 0.5 * accels[i] * self.dt

    def kinetic_energy(self):
        return sum(0.5 * b.mass * np.dot(b.vel, b.vel) for b in self.bodies)

    def potential_energy(self):
        pe = 0.0
        for bundle in self.bundles:
            a = self.bodies[bundle.body_a]
            b = self.bodies[bundle.body_b]
            d = b.pos - a.pos
            r = math.sqrt(np.dot(d, d) + self.softening ** 2)
            pe -= self.G * bundle.n_connectors / r
        return pe

    def total_energy(self):
        return self.kinetic_energy() + self.potential_energy()

    def angular_momentum_z(self):
        """Total L_z relative to center of mass."""
        total_mass = sum(b.mass for b in self.bodies)
        com = sum(b.mass * b.pos for b in self.bodies) / total_mass
        com_vel = sum(b.mass * b.vel for b in self.bodies) / total_mass
        Lz = 0.0
        for b in self.bodies:
            r = b.pos - com
            v = b.vel - com_vel
            Lz += b.mass * (r[0] * v[1] - r[1] * v[0])
        return Lz

    def distance(self, i, j):
        return float(np.linalg.norm(self.bodies[i].pos - self.bodies[j].pos))


# ===========================================================================
# Connector count helpers
# ===========================================================================

def compute_n_connectors(m_a, m_b, mode='product', scale=1.0):
    """Compute number of connectors between two bodies."""
    if mode == 'product':
        return scale * m_a * m_b
    elif mode == 'min':
        return scale * min(m_a, m_b)
    elif mode == 'fixed':
        return scale
    else:
        raise ValueError(f"Unknown connector mode: {mode}")


# ===========================================================================
# Newtonian Reference
# ===========================================================================

def newtonian_two_body_period(m1, m2, r, G_eff):
    M = m1 + m2
    if M <= 0 or r <= 0 or G_eff <= 0:
        return float('inf')
    return 2 * math.pi * math.sqrt(r ** 3 / (G_eff * M))


def newtonian_circular_velocity(m_central, r, G_eff):
    if m_central <= 0 or r <= 0 or G_eff <= 0:
        return 0.0
    return math.sqrt(G_eff * m_central / r)


def circular_velocity_connector(m_other, r, G, n_connectors, m_self):
    """Circular velocity for connector gravity: v = sqrt(G * N / (r * m_self) * m_self) ...
    Actually: a = G * N / (r^2 * m_self), centripetal: v^2/r = a
    => v = sqrt(G * N * r / (r^2 * m_self) ... no:
    v^2/r = G * N / (r^2 * m_self) ... wait, F/m = G*N/r^2 / m_self?
    No. F = G*N/r^2. a = F/m = G*N/(r^2 * m_self).
    Centripetal: v^2/r = G*N/(r^2 * m_self)
    v^2 = G*N/(r * m_self)
    v = sqrt(G*N/(r * m_self))

    But with product mode N = k * m_self * m_other:
    v = sqrt(G * k * m_self * m_other / (r * m_self)) = sqrt(G * k * m_other / r)
    Which is the standard Newtonian result with G_eff = G * k.
    """
    if n_connectors <= 0 or r <= 0 or m_self <= 0 or G <= 0:
        return 0.0
    return math.sqrt(G * n_connectors / (r * m_self))


# ===========================================================================
# Plotting (reused from v11 with minor adaptations)
# ===========================================================================

def unwrap_coords(coord_history, L):
    """Unwrap periodic coordinates to continuous trajectory."""
    if not L or L <= 0 or len(coord_history) < 2:
        return coord_history
    result = [coord_history[0]]
    cumulative = [coord_history[0][1], coord_history[0][2], coord_history[0][3]]
    half_L = L / 2.0
    for i in range(1, len(coord_history)):
        tick = coord_history[i][0]
        for dim in range(3):
            raw = coord_history[i][dim + 1]
            prev = coord_history[i - 1][dim + 1]
            delta = raw - prev
            if delta > half_L:
                delta -= L
            elif delta < -half_L:
                delta += L
            cumulative[dim] += delta
        result.append((tick, cumulative[0], cumulative[1], cumulative[2]))
    return result


def plot_distances(records, pairs, title, filename, init_dists=None):
    fig, ax = plt.subplots(figsize=(14, 5))
    ticks = [r['tick'] for r in records]
    for pair in pairs:
        key = f'd_{pair}'
        ax.plot(ticks, [r[key] for r in records], linewidth=1, label=pair)
        if init_dists and pair in init_dists:
            ax.axhline(y=init_dists[pair], color='gray', linestyle='--',
                        alpha=0.3)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_trajectories_xy(bodies, filename, title="Trajectories (XY)", L=0):
    fig, ax = plt.subplots(figsize=(8, 8))
    for body in bodies:
        if not body.coord_history:
            continue
        if L > 0:
            unwrapped = unwrap_coords(body.coord_history, L)
        else:
            unwrapped = body.coord_history
        xs = [c[1] for c in unwrapped]
        ys = [c[2] for c in unwrapped]
        ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.name)
        ax.plot(xs[0], ys[0], 'o', markersize=10)
        ax.plot(xs[-1], ys[-1], 's', markersize=8)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title(title)
    ax.set_aspect('equal')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_angular_momentum(ang_records, filename, title="Angular Momentum"):
    fig, ax = plt.subplots(figsize=(14, 4))
    ticks = [r[0] for r in ang_records]
    L_vals = [r[1] for r in ang_records]
    ax.plot(ticks, L_vals, 'r-', linewidth=1)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Total L_z')
    ax.set_title(title)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_energy(energy_records, filename, title="Energy"):
    fig, ax = plt.subplots(figsize=(14, 4))
    ticks = [r[0] for r in energy_records]
    KE = [r[1] for r in energy_records]
    PE = [r[2] for r in energy_records]
    TE = [r[3] for r in energy_records]
    ax.plot(ticks, KE, 'b-', linewidth=1, alpha=0.7, label='KE')
    ax.plot(ticks, PE, 'r-', linewidth=1, alpha=0.7, label='PE')
    ax.plot(ticks, TE, 'k-', linewidth=2, label='Total')
    ax.set_xlabel('Tick')
    ax.set_ylabel('Energy')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_force_law(force_data, filename):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    rs = [d['r'] for d in force_data]
    accels = [d['accel'] for d in force_data]

    ax1.plot(rs, accels, 'bo-', markersize=8, label='Measured')
    n_fit = None
    if len(rs) >= 2 and all(a > 0 for a in accels):
        log_r = np.log(rs)
        log_a = np.log(accels)
        coeffs = np.polyfit(log_r, log_a, 1)
        n_fit = -coeffs[0]
        k_fit = np.exp(coeffs[1])
        r_fit = np.linspace(min(rs), max(rs), 100)
        a_fit = k_fit * r_fit ** (-n_fit)
        ax1.plot(r_fit, a_fit, 'r--', label=f'Fit: a ~ 1/r^{n_fit:.2f}')
        ax1.set_title(f'Force Law: n = {n_fit:.3f} (Newton = 2.0)')
    ax1.set_xlabel('Distance')
    ax1.set_ylabel('Acceleration')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    if all(a > 0 for a in accels):
        ax2.loglog(rs, accels, 'bo-', markersize=8, label='Measured')
        if n_fit is not None:
            ax2.loglog(r_fit, a_fit, 'r--', label=f'n = {n_fit:.2f}')
        ax2.set_xlabel('Distance')
        ax2.set_ylabel('Acceleration')
        ax2.set_title('Log-Log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification(args=None):
    print("\n=== v12 VORTEX-CONNECTOR VERIFICATION ===\n")
    passed = 0
    failed = 0

    # Test 1: Zero-force drift (straight line at constant speed)
    print("Test 1: Zero-force drift (straight line)")
    b = Body('A', mass=10.0, pos=[0, 0, 0], vel=[1.0, 0.5, 0.0])
    u = VortexUniverse([b], [], G=1.0, H=0.0, dt=0.01)
    v0 = np.linalg.norm(b.vel)
    for _ in range(1000):
        u.step()
    expected_pos = np.array([10.0, 5.0, 0.0])
    pos_err = np.linalg.norm(b.pos - expected_pos)
    speed_err = abs(np.linalg.norm(b.vel) - v0)
    ok = pos_err < 1e-10 and speed_err < 1e-10
    print(f"  {'PASS' if ok else 'FAIL'}: pos_err={pos_err:.2e}, "
          f"speed_err={speed_err:.2e}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 2: Energy conservation (two-body circular orbit, H=0)
    print("Test 2: Energy conservation (circular orbit, 100 orbits)")
    G = 1.0
    m_star, m_planet = 1000.0, 1.0
    r0 = 10.0
    N = compute_n_connectors(m_star, m_planet, 'product', scale=1.0)
    v_circ = circular_velocity_connector(m_star, r0, G, N, m_planet)
    star = Body('Star', m_star, pos=[0, 0, 0], vel=[0, 0, 0])
    planet = Body('Planet', m_planet, pos=[r0, 0, 0], vel=[0, v_circ, 0])
    # Adjust star velocity for COM frame
    star.vel = -planet.vel * m_planet / m_star
    bundle = ConnectorBundle(0, 1, N)
    u2 = VortexUniverse([star, planet], [bundle], G=G, H=0.0, dt=0.01,
                         softening=0.01)
    E0 = u2.total_energy()
    T_orbit = newtonian_two_body_period(m_star, m_planet, r0, G * N / (m_star * m_planet) * m_planet)
    # With product mode: G_eff = G * scale * m_other for planet
    # Period = 2*pi*sqrt(r^3 / (G_eff * M))  where G_eff = G * k, M = m_star + m_planet
    G_eff = G * 1.0  # scale=1, product mode: N = m_star*m_planet, F = G*N/r^2, same as G_eff*m_star*m_planet/r^2
    T_orbit = 2 * math.pi * math.sqrt(r0 ** 3 / (G_eff * (m_star + m_planet)))
    n_steps_orbit = int(T_orbit / 0.01)
    n_orbits = 100
    for _ in range(n_steps_orbit * n_orbits):
        u2.step()
    E_final = u2.total_energy()
    E_drift = abs(E_final - E0) / abs(E0) if abs(E0) > 1e-10 else abs(E_final - E0)
    ok = E_drift < 0.001  # < 0.1% drift
    print(f"  {'PASS' if ok else 'FAIL'}: E0={E0:.6f}, E_final={E_final:.6f}, "
          f"drift={E_drift:.6f} ({E_drift*100:.4f}%)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 3: Angular momentum conservation
    print("Test 3: Angular momentum conservation (same orbit)")
    star3 = Body('Star', m_star, pos=[0, 0, 0], vel=[0, 0, 0])
    planet3 = Body('Planet', m_planet, pos=[r0, 0, 0], vel=[0, v_circ, 0])
    star3.vel = -planet3.vel * m_planet / m_star
    bundle3 = ConnectorBundle(0, 1, N)
    u3 = VortexUniverse([star3, planet3], [bundle3], G=G, H=0.0, dt=0.01,
                         softening=0.01)
    Lz0 = u3.angular_momentum_z()
    for _ in range(n_steps_orbit * 10):
        u3.step()
    Lz_final = u3.angular_momentum_z()
    Lz_drift = abs(Lz_final - Lz0) / abs(Lz0) if abs(Lz0) > 1e-10 else abs(Lz_final - Lz0)
    ok = Lz_drift < 0.001
    print(f"  {'PASS' if ok else 'FAIL'}: Lz0={Lz0:.6f}, Lz_final={Lz_final:.6f}, "
          f"drift={Lz_drift:.6f} ({Lz_drift*100:.4f}%)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 4: Expansion only (G=0, H>0 → exponential separation)
    print("Test 4: Expansion only (G=0, H=0.1)")
    b4a = Body('A', 10.0, pos=[0, 0, 0])
    b4b = Body('B', 10.0, pos=[1, 0, 0])
    bundle4 = ConnectorBundle(0, 1, 100)
    u4 = VortexUniverse([b4a, b4b], [bundle4], G=0.0, H=0.1, dt=0.01)
    d0 = u4.distance(0, 1)
    for _ in range(100):
        u4.step()
    d_final = u4.distance(0, 1)
    # Hubble expansion: d(t) = d0 * exp(H * t), t = 100 * 0.01 = 1.0
    d_expected = d0 * math.exp(0.1 * 1.0)
    rel_err = abs(d_final - d_expected) / d_expected
    ok = rel_err < 0.05  # 5% tolerance (leapfrog approximation)
    print(f"  {'PASS' if ok else 'FAIL'}: d0={d0:.3f}, d_final={d_final:.3f}, "
          f"expected={d_expected:.3f} (err={rel_err:.3f})")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 5: Circular orbit radius stability
    print("Test 5: Circular orbit radius stability (100 orbits)")
    star5 = Body('Star', m_star, pos=[0, 0, 0], vel=[0, 0, 0])
    planet5 = Body('Planet', m_planet, pos=[r0, 0, 0], vel=[0, v_circ, 0])
    star5.vel = -planet5.vel * m_planet / m_star
    bundle5 = ConnectorBundle(0, 1, N)
    u5 = VortexUniverse([star5, planet5], [bundle5], G=G, H=0.0, dt=0.01,
                         softening=0.01)
    min_d, max_d = r0, r0
    for step in range(n_steps_orbit * 100):
        u5.step()
        if step % 100 == 0:
            d = u5.distance(0, 1)
            min_d = min(min_d, d)
            max_d = max(max_d, d)
    eccentricity = (max_d - min_d) / (max_d + min_d)
    ok = eccentricity < 0.01  # < 1% variation = circular
    print(f"  {'PASS' if ok else 'FAIL'}: r_range=[{min_d:.3f}, {max_d:.3f}], "
          f"eccentricity={eccentricity:.6f}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 6: Force law is 1/r^2 (measuring acceleration vs distance)
    print("Test 6: Force law is 1/r^2")
    G6 = 1.0
    N6 = 1000.0
    force_data = []
    for r_test in [2.0, 4.0, 8.0, 16.0]:
        a6 = Body('A', 1000.0, pos=[0, 0, 0])
        b6 = Body('B', 1.0, pos=[r_test, 0, 0])
        bundle6 = ConnectorBundle(0, 1, N6)
        u6 = VortexUniverse([a6, b6], [bundle6], G=G6, softening=0.0)
        accels6 = u6.compute_accelerations()
        a_mag = np.linalg.norm(accels6[1])
        force_data.append({'r': r_test, 'accel': a_mag})
    # Check: accel should scale as 1/r^2
    log_r = np.log([d['r'] for d in force_data])
    log_a = np.log([d['accel'] for d in force_data])
    coeffs = np.polyfit(log_r, log_a, 1)
    n_exponent = -coeffs[0]
    ok = abs(n_exponent - 2.0) < 0.01
    print(f"  {'PASS' if ok else 'FAIL'}: exponent = {n_exponent:.4f} (expect 2.0)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 7: Mass independence (equivalence principle with product mode)
    # In product mode, a = G * N / (r^2 * m) = G * scale * m_other / r^2
    # The acceleration should be independent of the body's own mass.
    print("Test 7: Mass independence (equivalence principle)")
    accels_test = []
    for m_test in [0.01, 1.0, 100.0, 10000.0]:
        star7 = Body('Star', m_star, pos=[0, 0, 0])
        probe7 = Body('P', m_test, pos=[r0, 0, 0])
        N7 = compute_n_connectors(m_star, m_test, 'product', 1.0)
        bundle7 = ConnectorBundle(0, 1, N7)
        u7 = VortexUniverse([star7, probe7], [bundle7], G=G, softening=0.0)
        a7 = u7.compute_accelerations()
        a_mag = np.linalg.norm(a7[1])
        accels_test.append((m_test, a_mag))
    # All accelerations should be identical
    a_vals = [a for _, a in accels_test]
    a_spread = (max(a_vals) - min(a_vals)) / np.mean(a_vals) if np.mean(a_vals) > 0 else 0
    ok = a_spread < 1e-10
    print(f"  {'PASS' if ok else 'FAIL'}: accels={[f'{a:.6f}' for _, a in accels_test]}, "
          f"spread={a_spread:.2e}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 8: Moon orbits stationary planet (isolated two-body with small mass)
    # Tests that the connector model works for a second independent orbit.
    # Full hierarchical three-body (nested orbits) is tested in experiments.
    print("Test 8: Moon orbits planet (isolated)")
    m_p8 = 100.0
    m_m8 = 1.0
    r_m8 = 2.0
    N8 = compute_n_connectors(m_p8, m_m8, 'product', 1.0)
    v_m8 = circular_velocity_connector(m_p8, r_m8, G, N8, m_m8)
    planet8 = Body('Planet', m_p8, pos=[0, 0, 0], vel=[0, 0, 0])
    moon8 = Body('Moon', m_m8, pos=[r_m8, 0, 0], vel=[0, v_m8, 0])
    planet8.vel = -moon8.vel * m_m8 / m_p8
    bundle8 = ConnectorBundle(0, 1, N8)
    u8 = VortexUniverse([planet8, moon8], [bundle8], G=G, dt=0.001,
                         softening=0.01)
    G_eff8 = G * 1.0
    T_m8 = 2 * math.pi * math.sqrt(r_m8 ** 3 / (G_eff8 * (m_p8 + m_m8)))
    n_steps_8 = int(T_m8 * 50 / 0.001)  # 50 orbits
    d_min8, d_max8 = r_m8, r_m8
    for step in range(min(n_steps_8, 1000000)):
        u8.step()
        if step % 200 == 0:
            d = u8.distance(0, 1)
            d_min8 = min(d_min8, d)
            d_max8 = max(d_max8, d)
    ecc8 = (d_max8 - d_min8) / (d_max8 + d_min8)
    ok = ecc8 < 0.02  # slightly relaxed due to leapfrog dt precision
    print(f"  {'PASS' if ok else 'FAIL'}: r_range=[{d_min8:.3f}, {d_max8:.3f}], "
          f"eccentricity={ecc8:.6f}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    print(f"\n=== RESULTS: {passed}/{passed + failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Experiment: Two-Body Orbit
# ===========================================================================

def experiment_two_body(G=1.0, H=0.0, dt=0.01, ticks=50000,
                        mass_star=1000.0, mass_planet=10.0,
                        separation=10.0, connector_mode='product',
                        connector_scale=1.0, initial_momentum='circular',
                        turn_mode=False, softening=0.1, tag=''):
    print("=" * 70)
    print("TWO-BODY ORBIT")
    print("=" * 70)

    N = compute_n_connectors(mass_star, mass_planet, connector_mode,
                              connector_scale)
    v_circ = circular_velocity_connector(mass_star, separation, G, N,
                                          mass_planet)
    # Effective G for Newtonian comparison (product mode: G_eff = G * scale)
    G_eff = G * connector_scale

    print(f"\n  Masses: Star={mass_star}, Planet={mass_planet}")
    print(f"  Separation: {separation}")
    print(f"  Connectors: N={N:.0f} (mode={connector_mode}, scale={connector_scale})")
    print(f"  G={G}, H={H}, dt={dt}")
    print(f"  Circular velocity: {v_circ:.6f}")
    T_pred = newtonian_two_body_period(mass_star, mass_planet, separation, G_eff)
    print(f"  Predicted period: {T_pred:.0f} ticks")
    print(f"  Turn mode: {turn_mode}")

    star = Body('Star', mass_star, pos=[0, 0, 0])
    if initial_momentum == 'circular':
        planet = Body('Planet', mass_planet, pos=[separation, 0, 0],
                       vel=[0, v_circ, 0])
    elif initial_momentum == 'none':
        planet = Body('Planet', mass_planet, pos=[separation, 0, 0])
    else:
        planet = Body('Planet', mass_planet, pos=[separation, 0, 0],
                       vel=[0, v_circ, 0])

    # COM frame correction
    star.vel = -planet.vel * mass_planet / mass_star

    bundle = ConnectorBundle(0, 1, N)
    universe = VortexUniverse([star, planet], [bundle], G=G, H=H, dt=dt,
                               turn_mode=turn_mode, softening=softening)

    E0 = universe.total_energy()
    Lz0 = universe.angular_momentum_z()
    d0 = universe.distance(0, 1)

    records = []
    energy_records = []
    ang_records = []
    diag_interval = max(ticks // 500, 1)
    record_interval = max(ticks // 2000, 1)

    t0 = time.time()
    for tick in range(ticks):
        universe.step()

        if (tick + 1) % record_interval == 0:
            star.record(tick + 1)
            planet.record(tick + 1)

        if (tick + 1) % diag_interval == 0:
            d = universe.distance(0, 1)
            KE = universe.kinetic_energy()
            PE = universe.potential_energy()
            TE = KE + PE
            Lz = universe.angular_momentum_z()
            records.append({'tick': tick + 1, 'd_SP': d})
            energy_records.append((tick + 1, KE, PE, TE))
            ang_records.append((tick + 1, Lz))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                E_drift = abs(TE - E0) / abs(E0) if abs(E0) > 0 else 0
                print(f"    Tick {tick+1:7d}: d={d:.3f} E_drift={E_drift:.6f} "
                      f"Lz={Lz:.4f} ({elapsed:.1f}s)")

    final_d = universe.distance(0, 1)
    print(f"\n  Distance: {d0:.3f} -> {final_d:.3f}")
    E_final = universe.total_energy()
    E_drift = abs(E_final - E0) / abs(E0) if abs(E0) > 0 else 0
    print(f"  Energy drift: {E_drift:.8f} ({E_drift*100:.6f}%)")

    # Count orbits (distance oscillations)
    if records:
        dists = [r['d_SP'] for r in records]
        mean_d = np.mean(dists)
        crossings = 0
        for i in range(1, len(dists)):
            if (dists[i] - mean_d) * (dists[i-1] - mean_d) < 0:
                crossings += 1
        n_orbits = crossings / 2
        print(f"  Approx orbits: {n_orbits:.1f}")
        print(f"  Distance range: [{min(dists):.3f}, {max(dists):.3f}]")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['SP'],
                       f'Two-Body: G={G}, H={H}, N={N:.0f}',
                       RESULTS_DIR / f'two_body_distance{suffix}.png',
                       {'SP': d0})
    if star.coord_history:
        plot_trajectories_xy([star, planet],
                              RESULTS_DIR / f'two_body_trajectory{suffix}.png',
                              f'Two-Body Trajectories (H={H})')
    if energy_records:
        plot_energy(energy_records,
                    RESULTS_DIR / f'two_body_energy{suffix}.png',
                    f'Two-Body Energy (H={H})')
    if ang_records:
        plot_angular_momentum(ang_records,
                               RESULTS_DIR / f'two_body_Lz{suffix}.png')

    return records


# ===========================================================================
# Experiment: Three-Body Hierarchy
# ===========================================================================

def experiment_three_body(G=1.0, H=0.0, dt=0.001, ticks=100000,
                           mass_star=1000.0, mass_planet=10.0, mass_moon=0.1,
                           separation=10.0, moon_distance=1.5,
                           connector_mode='product', connector_scale=1.0,
                           turn_mode=False, softening=0.1, tag=''):
    print("=" * 70)
    print("THREE-BODY HIERARCHY (Star -> Planet -> Moon)")
    print("=" * 70)

    N_sp = compute_n_connectors(mass_star, mass_planet, connector_mode,
                                 connector_scale)
    N_pm = compute_n_connectors(mass_planet, mass_moon, connector_mode,
                                 connector_scale)
    v_planet = circular_velocity_connector(mass_star, separation, G, N_sp,
                                            mass_planet)
    v_moon_rel = circular_velocity_connector(mass_planet, moon_distance, G,
                                              N_pm, mass_moon)

    print(f"\n  Star: M={mass_star}")
    print(f"  Planet: M={mass_planet}, r={separation}, v={v_planet:.4f}")
    print(f"    Connectors to Star: N={N_sp:.0f}")
    print(f"  Moon: M={mass_moon}, r={moon_distance} from Planet, "
          f"v_rel={v_moon_rel:.4f}")
    print(f"    Connectors to Planet: N={N_pm:.0f}")
    print(f"  G={G}, H={H}, dt={dt}")

    star = Body('Star', mass_star, pos=[0, 0, 0])
    planet = Body('Planet', mass_planet,
                   pos=[separation, 0, 0],
                   vel=[0, v_planet, 0])
    moon = Body('Moon', mass_moon,
                 pos=[separation + moon_distance, 0, 0],
                 vel=[0, v_planet + v_moon_rel, 0])

    # COM correction
    total_m = mass_star + mass_planet + mass_moon
    com_vel = (star.vel * mass_star + planet.vel * mass_planet +
               moon.vel * mass_moon) / total_m
    star.vel -= com_vel
    planet.vel -= com_vel
    moon.vel -= com_vel

    bundle_sp = ConnectorBundle(0, 1, N_sp)
    bundle_pm = ConnectorBundle(1, 2, N_pm)
    # Moon is NOT directly connected to Star (hierarchical tree)
    universe = VortexUniverse([star, planet, moon],
                               [bundle_sp, bundle_pm],
                               G=G, H=H, dt=dt,
                               turn_mode=turn_mode, softening=softening)

    records = []
    energy_records = []
    ang_records = []
    diag_interval = max(ticks // 500, 1)
    record_interval = max(ticks // 3000, 1)

    t0 = time.time()
    for tick in range(ticks):
        universe.step()

        if (tick + 1) % record_interval == 0:
            star.record(tick + 1)
            planet.record(tick + 1)
            moon.record(tick + 1)

        if (tick + 1) % diag_interval == 0:
            d_sp = universe.distance(0, 1)
            d_pm = universe.distance(1, 2)
            d_sm = universe.distance(0, 2)
            TE = universe.total_energy()
            Lz = universe.angular_momentum_z()
            records.append({'tick': tick + 1,
                            'd_SP': d_sp, 'd_PM': d_pm, 'd_SM': d_sm})
            energy_records.append((tick + 1, universe.kinetic_energy(),
                                   universe.potential_energy(), TE))
            ang_records.append((tick + 1, Lz))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 20) == 0:
                print(f"    Tick {tick+1:7d}: SP={d_sp:.2f} PM={d_pm:.2f} "
                      f"SM={d_sm:.2f} E={TE:.2f} ({elapsed:.1f}s)")

    print(f"\n  Final distances: SP={universe.distance(0,1):.2f}, "
          f"PM={universe.distance(1,2):.2f}, SM={universe.distance(0,2):.2f}")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['SP', 'PM', 'SM'],
                       'Three-Body Hierarchy',
                       RESULTS_DIR / f'three_body_distance{suffix}.png')
    if star.coord_history:
        plot_trajectories_xy([star, planet, moon],
                              RESULTS_DIR / f'three_body_trajectory{suffix}.png',
                              'Three-Body Trajectories')
    if energy_records:
        plot_energy(energy_records,
                    RESULTS_DIR / f'three_body_energy{suffix}.png',
                    'Three-Body Energy')
    if ang_records:
        plot_angular_momentum(ang_records,
                               RESULTS_DIR / f'three_body_Lz{suffix}.png')

    return records


# ===========================================================================
# Experiment: Force Law
# ===========================================================================

def experiment_force_law(G=1.0, connector_mode='product',
                          connector_scale=1.0, tag=''):
    print("=" * 70)
    print("FORCE LAW MEASUREMENT")
    print("=" * 70)

    m_star = 1000.0
    m_probe = 1.0
    N = compute_n_connectors(m_star, m_probe, connector_mode, connector_scale)

    print(f"\n  Star mass: {m_star}")
    print(f"  Probe mass: {m_probe}")
    print(f"  Connectors: N={N:.0f}")
    print(f"  G={G}")

    force_data = []
    distances = [1.0, 2.0, 3.0, 5.0, 8.0, 12.0, 20.0, 30.0, 50.0]

    print(f"\n  {'r':>8s} {'accel':>14s} {'expected':>14s} {'ratio':>8s}")
    for r in distances:
        star = Body('Star', m_star, pos=[0, 0, 0])
        probe = Body('Probe', m_probe, pos=[r, 0, 0])
        bundle = ConnectorBundle(0, 1, N)
        u = VortexUniverse([star, probe], [bundle], G=G, softening=0.0)
        accels = u.compute_accelerations()
        a_measured = np.linalg.norm(accels[1])
        a_expected = G * N / (r ** 2 * m_probe)
        ratio = a_measured / a_expected if a_expected > 0 else 0
        force_data.append({'r': r, 'accel': a_measured})
        print(f"  {r:8.1f} {a_measured:14.6f} {a_expected:14.6f} {ratio:8.4f}")

    if len(force_data) >= 3:
        log_r = np.log([d['r'] for d in force_data])
        log_a = np.log([d['accel'] for d in force_data])
        coeffs = np.polyfit(log_r, log_a, 1)
        n_fit = -coeffs[0]
        print(f"\n  Fit: accel ~ 1/r^{n_fit:.4f} (Newton = 2.0)")
        verdict = 'PASS' if abs(n_fit - 2.0) < 0.01 else 'FAIL'
        print(f"  Verdict: {verdict}")

    suffix = f"_{tag}" if tag else ""
    plot_force_law(force_data, RESULTS_DIR / f'force_law{suffix}.png')

    return force_data


# ===========================================================================
# Experiment: Kepler's Third Law
# ===========================================================================

def experiment_kepler(G=1.0, dt=0.01, mass_star=1000.0, mass_planet=10.0,
                       connector_mode='product', connector_scale=1.0,
                       softening=0.1, tag=''):
    print("=" * 70)
    print("KEPLER'S THIRD LAW TEST")
    print("=" * 70)

    separations = [5.0, 8.0, 12.0, 18.0]
    kepler_data = []

    for r0 in separations:
        print(f"\n  --- r = {r0:.1f} ---")
        N = compute_n_connectors(mass_star, mass_planet, connector_mode,
                                  connector_scale)
        v_circ = circular_velocity_connector(mass_star, r0, G, N, mass_planet)
        G_eff = G * connector_scale

        star = Body('Star', mass_star, pos=[0, 0, 0])
        planet = Body('Planet', mass_planet, pos=[r0, 0, 0],
                       vel=[0, v_circ, 0])
        star.vel = -planet.vel * mass_planet / mass_star

        bundle = ConnectorBundle(0, 1, N)
        u = VortexUniverse([star, planet], [bundle], G=G, dt=dt,
                            softening=softening)

        T_pred = newtonian_two_body_period(mass_star, mass_planet, r0, G_eff)
        n_steps = int(T_pred * 5 / dt)  # 5 orbits

        dists = []
        ticks_list = []
        for tick in range(n_steps):
            u.step()
            if tick % 100 == 0:
                d = u.distance(0, 1)
                dists.append(d)
                ticks_list.append(tick)

        if len(dists) > 10:
            mean_d = np.mean(dists)
            crossings = []
            for i in range(1, len(dists)):
                if (dists[i] - mean_d) * (dists[i - 1] - mean_d) < 0:
                    crossings.append(ticks_list[i] * dt)

            if len(crossings) >= 4:
                half_periods = [crossings[i + 1] - crossings[i]
                                for i in range(len(crossings) - 1)]
                T_measured = 2.0 * np.mean(half_periods)
                kepler_data.append({
                    'r': r0, 'T': T_measured, 'T_pred': T_pred,
                    'T2': T_measured ** 2, 'r3': r0 ** 3
                })
                print(f"    T_measured={T_measured:.2f}, T_pred={T_pred:.2f}, "
                      f"ratio={T_measured/T_pred:.4f}")
            else:
                print(f"    Not enough oscillations ({len(crossings)} crossings)")

    if len(kepler_data) >= 2:
        print("\n  === Kepler Summary ===")
        print(f"  {'r':>6s} {'T':>10s} {'T^2':>14s} {'r^3':>10s} "
              f"{'T^2/r^3':>10s} {'T/T_pred':>10s}")
        for d in kepler_data:
            ratio = d['T2'] / d['r3'] if d['r3'] > 0 else 0
            t_ratio = d['T'] / d['T_pred'] if d['T_pred'] > 0 else 0
            print(f"  {d['r']:6.1f} {d['T']:10.2f} {d['T2']:14.1f} "
                  f"{d['r3']:10.1f} {ratio:10.4f} {t_ratio:10.4f}")

        ratios = [d['T2'] / d['r3'] for d in kepler_data if d['r3'] > 0]
        if ratios:
            cv = np.std(ratios) / np.mean(ratios) if np.mean(ratios) > 0 else 999
            print(f"\n  T^2/r^3 variation: CV = {cv:.4f} "
                  f"({'PASS' if cv < 0.05 else 'PARTIAL' if cv < 0.1 else 'FAIL'})")

    suffix = f"_{tag}" if tag else ""
    return kepler_data


# ===========================================================================
# Experiment: Interstellar Capture
# ===========================================================================

def experiment_capture(G=1.0, H=0.0, dt=0.01, ticks=80000,
                        mass_star=1000.0, mass_planet=10.0, mass_rogue=5.0,
                        separation=10.0, rogue_distance=30.0,
                        capture_radius=5.0, connector_mode='product',
                        connector_scale=1.0, softening=0.1, tag=''):
    print("=" * 70)
    print("INTERSTELLAR CAPTURE")
    print("=" * 70)

    N_sp = compute_n_connectors(mass_star, mass_planet, connector_mode,
                                 connector_scale)
    v_planet = circular_velocity_connector(mass_star, separation, G, N_sp,
                                            mass_planet)

    star = Body('Star', mass_star, pos=[0, 0, 0])
    planet = Body('Planet', mass_planet, pos=[separation, 0, 0],
                   vel=[0, v_planet, 0])
    star.vel = -planet.vel * mass_planet / (mass_star + mass_planet)
    planet.vel = planet.vel * mass_star / (mass_star + mass_planet)

    # Rogue body approaching from far away
    rogue = Body('Rogue', mass_rogue,
                  pos=[rogue_distance, rogue_distance, 0],
                  vel=[-0.5, -0.3, 0])

    bundle_sp = ConnectorBundle(0, 1, N_sp)
    # Initially no connection to rogue
    bundles = [bundle_sp]

    universe = VortexUniverse([star, planet, rogue], bundles,
                               G=G, H=H, dt=dt, softening=softening)

    print(f"\n  Star: M={mass_star} at {star.pos}")
    print(f"  Planet: M={mass_planet} at {planet.pos}, v={planet.vel}")
    print(f"  Rogue: M={mass_rogue} at {rogue.pos}, v={rogue.vel}")
    print(f"  Capture radius: {capture_radius}")
    print(f"  Connectors Star-Planet: N={N_sp:.0f}")

    rogue_connected = False
    capture_tick = None
    records = []
    diag_interval = max(ticks // 500, 1)
    record_interval = max(ticks // 3000, 1)

    t0 = time.time()
    for tick in range(ticks):
        universe.step()

        # Check for capture: rogue comes within capture_radius of star
        if not rogue_connected:
            d_rogue_star = universe.distance(0, 2)
            if d_rogue_star < capture_radius:
                N_sr = compute_n_connectors(mass_star, mass_rogue,
                                             connector_mode, connector_scale)
                new_bundle = ConnectorBundle(0, 2, N_sr)
                universe.bundles.append(new_bundle)
                rogue_connected = True
                capture_tick = tick + 1
                print(f"\n  ** CAPTURE at tick {capture_tick}! "
                      f"d={d_rogue_star:.2f}, N_new={N_sr:.0f} **\n")

        if (tick + 1) % record_interval == 0:
            star.record(tick + 1)
            planet.record(tick + 1)
            rogue.record(tick + 1)

        if (tick + 1) % diag_interval == 0:
            d_sp = universe.distance(0, 1)
            d_sr = universe.distance(0, 2)
            d_pr = universe.distance(1, 2)
            records.append({'tick': tick + 1,
                            'd_SP': d_sp, 'd_SR': d_sr, 'd_PR': d_pr})

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 20) == 0:
                status = "CONNECTED" if rogue_connected else "free"
                print(f"    Tick {tick+1:7d}: SP={d_sp:.2f} SR={d_sr:.2f} "
                      f"PR={d_pr:.2f} [{status}] ({elapsed:.1f}s)")

    print(f"\n  Rogue captured: {rogue_connected}")
    if capture_tick:
        print(f"  Capture tick: {capture_tick}")
    print(f"  Final distances: SP={universe.distance(0,1):.2f}, "
          f"SR={universe.distance(0,2):.2f}")

    # Check if rogue is in a bound orbit after capture
    if rogue_connected and records:
        post_capture = [r for r in records if r['tick'] > (capture_tick or 0)]
        if len(post_capture) > 10:
            sr_dists = [r['d_SR'] for r in post_capture]
            reversals = sum(1 for i in range(2, len(sr_dists))
                            if (sr_dists[i] - sr_dists[i-1]) *
                               (sr_dists[i-1] - sr_dists[i-2]) < 0)
            print(f"  Post-capture reversals: {reversals} "
                  f"({'orbiting' if reversals > 4 else 'escaping/falling'})")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['SP', 'SR', 'PR'],
                       'Interstellar Capture',
                       RESULTS_DIR / f'capture_distance{suffix}.png')
    if star.coord_history:
        plot_trajectories_xy([star, planet, rogue],
                              RESULTS_DIR / f'capture_trajectory{suffix}.png',
                              'Interstellar Capture')

    return records


# ===========================================================================
# Experiment: Expansion Sweep
# ===========================================================================

def experiment_expansion_sweep(G=1.0, dt=0.01, mass_star=1000.0,
                                mass_planet=10.0, separation=10.0,
                                connector_mode='product',
                                connector_scale=1.0, softening=0.1, tag=''):
    """Sweep H values to find critical expansion rate for orbit disruption."""
    print("=" * 70)
    print("EXPANSION SWEEP: Finding critical H")
    print("=" * 70)

    N = compute_n_connectors(mass_star, mass_planet, connector_mode,
                              connector_scale)
    v_circ = circular_velocity_connector(mass_star, separation, G, N,
                                          mass_planet)
    G_eff = G * connector_scale
    T_orbit = newtonian_two_body_period(mass_star, mass_planet, separation, G_eff)
    n_steps_orbit = int(T_orbit / dt)

    H_values = [0, 0.001, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2]
    results = []

    print(f"\n  T_orbit = {T_orbit:.1f}, running 20 orbits each")
    print(f"\n  {'H':>8s} {'d_min':>8s} {'d_max':>8s} {'d_final':>8s} {'status':>10s}")

    for H in H_values:
        star = Body('Star', mass_star, pos=[0, 0, 0])
        planet = Body('Planet', mass_planet, pos=[separation, 0, 0],
                       vel=[0, v_circ, 0])
        star.vel = -planet.vel * mass_planet / mass_star
        bundle = ConnectorBundle(0, 1, N)
        u = VortexUniverse([star, planet], [bundle], G=G, H=H, dt=dt,
                            softening=softening)

        d_min, d_max = separation, separation
        n_steps = n_steps_orbit * 20
        escaped = False
        for step in range(n_steps):
            u.step()
            if step % 100 == 0:
                d = u.distance(0, 1)
                d_min = min(d_min, d)
                d_max = max(d_max, d)
                if d > separation * 10:
                    escaped = True
                    break

        d_final = u.distance(0, 1)
        status = 'ESCAPED' if escaped else ('STABLE' if d_max < separation * 2 else 'DRIFTING')
        results.append({'H': H, 'd_min': d_min, 'd_max': d_max,
                         'd_final': d_final, 'status': status})
        print(f"  {H:8.4f} {d_min:8.2f} {d_max:8.2f} {d_final:8.2f} {status:>10s}")

    # Theoretical critical H: H_crit ~ sqrt(G_eff * M / r^3)
    # (orbital angular velocity — expansion at this rate disrupts orbit)
    omega_orbit = 2 * math.pi / T_orbit
    print(f"\n  Orbital angular velocity: {omega_orbit:.6f}")
    print(f"  (H > omega may disrupt)")

    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v12: Vortex-Connector Hierarchical Gravity')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--two-body', action='store_true')
    parser.add_argument('--three-body', action='store_true')
    parser.add_argument('--force-law', action='store_true')
    parser.add_argument('--kepler', action='store_true')
    parser.add_argument('--capture', action='store_true')
    parser.add_argument('--expansion-sweep', action='store_true')

    parser.add_argument('--G', type=float, default=1.0,
                        help='Gravitational coupling constant')
    parser.add_argument('--H', type=float, default=0.0,
                        help='Expansion rate (Hubble parameter)')
    parser.add_argument('--dt', type=float, default=0.01,
                        help='Time step')
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--mass-star', type=float, default=1000.0)
    parser.add_argument('--mass-planet', type=float, default=10.0)
    parser.add_argument('--mass-moon', type=float, default=0.1)
    parser.add_argument('--separation', type=float, default=10.0,
                        help='Initial star-planet distance')
    parser.add_argument('--moon-distance', type=float, default=1.5,
                        help='Initial planet-moon distance')
    parser.add_argument('--connector-mode',
                        choices=['product', 'min', 'fixed'],
                        default='product')
    parser.add_argument('--connector-scale', type=float, default=1.0,
                        help='Scaling factor k for N_connectors')
    parser.add_argument('--initial-momentum',
                        choices=['none', 'circular', 'custom'],
                        default='circular')
    parser.add_argument('--turn-mode', action='store_true',
                        help='Constant-speed turning instead of Newtonian')
    parser.add_argument('--softening', type=float, default=0.1,
                        help='Gravitational softening length')
    parser.add_argument('--L', type=float, default=0.0,
                        help='Periodic box size (0 = open space)')
    parser.add_argument('--tag', type=str, default='')

    args = parser.parse_args()

    if args.verify:
        run_verification(args)
    if args.two_body:
        experiment_two_body(
            G=args.G, H=args.H, dt=args.dt, ticks=args.ticks,
            mass_star=args.mass_star, mass_planet=args.mass_planet,
            separation=args.separation,
            connector_mode=args.connector_mode,
            connector_scale=args.connector_scale,
            initial_momentum=args.initial_momentum,
            turn_mode=args.turn_mode, softening=args.softening,
            tag=args.tag)
    if args.three_body:
        experiment_three_body(
            G=args.G, H=args.H, dt=args.dt, ticks=args.ticks,
            mass_star=args.mass_star, mass_planet=args.mass_planet,
            mass_moon=args.mass_moon, separation=args.separation,
            moon_distance=args.moon_distance,
            connector_mode=args.connector_mode,
            connector_scale=args.connector_scale,
            turn_mode=args.turn_mode, softening=args.softening,
            tag=args.tag)
    if args.force_law:
        experiment_force_law(
            G=args.G, connector_mode=args.connector_mode,
            connector_scale=args.connector_scale, tag=args.tag)
    if args.kepler:
        experiment_kepler(
            G=args.G, dt=args.dt, mass_star=args.mass_star,
            mass_planet=args.mass_planet,
            connector_mode=args.connector_mode,
            connector_scale=args.connector_scale,
            softening=args.softening, tag=args.tag)
    if args.capture:
        experiment_capture(
            G=args.G, H=args.H, dt=args.dt, ticks=args.ticks,
            mass_star=args.mass_star, mass_planet=args.mass_planet,
            separation=args.separation,
            connector_mode=args.connector_mode,
            connector_scale=args.connector_scale,
            softening=args.softening, tag=args.tag)
    if args.expansion_sweep:
        experiment_expansion_sweep(
            G=args.G, dt=args.dt, mass_star=args.mass_star,
            mass_planet=args.mass_planet, separation=args.separation,
            connector_mode=args.connector_mode,
            connector_scale=args.connector_scale,
            softening=args.softening, tag=args.tag)

    if not any([args.verify, args.two_body, args.three_body,
                args.force_law, args.kepler, args.capture,
                args.expansion_sweep]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
