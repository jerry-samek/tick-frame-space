"""v10: Macro Bodies — Astronomical Entities on an Expanding Graph.

Scales the proven micro-rules (v1-v9) to astronomical bodies:
- Float64 gamma field (deterministic large-number limit of v6's integer field)
- Mass as a property (aggregate of 10^30 quanta, not individual counting)
- Self-subtraction via tagged fields (from v8)
- Continuous internal direction vector (from v9)
- Graph expansion via edge weight growth (NEW)

The "faking" is justified: at M~10^30, Binomial(n,p) = n*p exactly.
Everything else is preserved from micro: graph topology, c = 1 hop/tick,
self-gravitation, gradient-following with nudge.

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --phase1 --ticks 5000
    python macro_bodies.py --phase2 --ticks 50000
    python macro_bodies.py --phase2 --ticks 50000 --initial-momentum perpendicular
    python macro_bodies.py --phase3 --ticks 100000 --initial-momentum tangential
    python macro_bodies.py --force-law --ticks 30000
    python macro_bodies.py --kepler --ticks 200000

February 2026
"""

import argparse
import json
import math
import time
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# ContinuousGammaField — deterministic float64 tagged field
# ===========================================================================

class ContinuousGammaField:
    """Deterministic self-gravitating gamma field on a 3D periodic lattice.

    Each body has a separate tagged field layer. Total gamma = sum of all tags.
    Self-gravitation: alpha_eff = alpha / (1 + G * total_gamma).
    External gamma for body B = total - tagged[B].

    This is the large-number limit of v6's QuantumGammaField:
    Binomial(n, p) -> n*p, Multinomial -> uniform 1/k split.
    """

    def __init__(self, n_nodes, k=6, alpha=None, G=1.0, H=0.0, G_expand=None,
                 seed=42, body_ids=None):
        self.k = k
        self.G = G
        self.H = H  # Expansion rate per tick (suppressed near mass)
        self.G_expand = G_expand if G_expand is not None else G
        self.seed = seed

        # Build 3D periodic lattice
        side = round(n_nodes ** (1/3))
        actual_n = side ** 3
        self.side = side
        self.n_nodes = actual_n
        print(f"  Building lattice: side={side}, N={actual_n}, k={k}")
        t0 = time.time()

        G_grid = nx.grid_graph(dim=[side, side, side], periodic=True)
        sorted_nodes = sorted(G_grid.nodes())
        coord_map = {i: node for i, node in enumerate(sorted_nodes)}
        self.graph = nx.convert_node_labels_to_integers(G_grid, ordering='sorted')
        self.node_coords = coord_map
        self.coord_to_node = {v: k_node for k_node, v in coord_map.items()}

        # Adjacency
        self.neighbors = [list(self.graph.neighbors(i)) for i in range(actual_n)]
        self.A = nx.adjacency_matrix(self.graph, dtype=np.float64)
        self.degrees = np.array(self.A.sum(axis=1)).flatten()
        self.degrees = np.maximum(self.degrees, 1.0)

        elapsed = time.time() - t0
        print(f"    Built in {elapsed:.1f}s")

        # Speed of light
        self.alpha = alpha if alpha is not None else (1.0 / k)

        # Tagged fields
        self.body_ids = body_ids or []
        self.tagged = {
            bid: np.zeros(actual_n, dtype=np.float64)
            for bid in self.body_ids
        }
        self.gamma = np.zeros(actual_n, dtype=np.float64)

    def sync_total(self):
        if self.body_ids:
            self.gamma = sum(self.tagged[bid] for bid in self.body_ids)
        else:
            self.gamma[:] = 0.0

    def external_gamma(self, node, exclude_bid):
        return self.gamma[node] - self.tagged[exclude_bid][node]

    def spread(self):
        """Deterministic self-gravitating spread. Conserves gamma exactly."""
        alpha_eff = self.alpha / (1.0 + self.G * np.abs(self.gamma))
        alpha_eff = np.clip(alpha_eff, 0.0, 1.0)

        for bid in self.body_ids:
            outflow = alpha_eff * self.tagged[bid]
            per_edge = outflow / self.degrees
            inflow = self.A @ per_edge
            self.tagged[bid] = self.tagged[bid] - outflow + inflow

        self.sync_total()

    def expand(self):
        """Expansion: dilute gamma, suppressed near gamma wells.

        Far from mass (gamma ~ 0): full dilution by H per tick.
        Near mass (gamma >> 0): expansion suppressed, well stays deep.
        This is the Friedmann equation on the lattice: expansion rate
        depends on local energy density.

        Uses G_expand (not G) to control suppression. This allows
        G=0 (free spread, strong gradient) with G_expand>0 (sharp well).
        """
        if self.H <= 0:
            return
        H_local = self.H / (1.0 + self.G_expand * np.abs(self.gamma))
        dilution = 1.0 / (1.0 + H_local)
        for bid in self.body_ids:
            self.tagged[bid] *= dilution
        self.sync_total()

    def deposit(self, node, bid, amount):
        """Body deposits gamma at its current node."""
        self.tagged[bid][node] += amount
        self.gamma[node] += amount

    def total_gamma(self):
        return float(np.sum(self.gamma))

    def tagged_total(self, bid):
        return float(np.sum(self.tagged[bid]))

    def tagged_peak_node(self, bid):
        return int(np.argmax(self.tagged[bid]))

    def initialize_peak(self, bid, center_node, mass, smooth_ticks=20):
        """Place gamma mass at center, smooth with G=0 spread."""
        self.tagged[bid][center_node] += mass
        self.sync_total()
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def direction_vector(self, from_node, to_node):
        """Direction vector with periodic wrapping."""
        fc = self.node_coords[from_node]
        tc = self.node_coords[to_node]
        s = self.side
        dx = tc[0] - fc[0]
        dy = tc[1] - fc[1]
        dz = tc[2] - fc[2]
        if dx > s // 2: dx -= s
        if dx < -(s // 2): dx += s
        if dy > s // 2: dy -= s
        if dy < -(s // 2): dy += s
        if dz > s // 2: dz -= s
        if dz < -(s // 2): dz += s
        return (dx, dy, dz)

    def hop_distance(self, node_a, node_b):
        """Manhattan distance with periodic wrapping."""
        ca = self.node_coords[node_a]
        cb = self.node_coords[node_b]
        s = self.side
        dx = abs(ca[0] - cb[0])
        dy = abs(ca[1] - cb[1])
        dz = abs(ca[2] - cb[2])
        dx = min(dx, s - dx)
        dy = min(dy, s - dy)
        dz = min(dz, s - dz)
        return dx + dy + dz

    def euclidean_distance(self, node_a, node_b):
        """Euclidean distance with periodic wrapping."""
        ca = self.node_coords[node_a]
        cb = self.node_coords[node_b]
        s = self.side
        dx = abs(ca[0] - cb[0])
        dy = abs(ca[1] - cb[1])
        dz = abs(ca[2] - cb[2])
        dx = min(dx, s - dx)
        dy = min(dy, s - dy)
        dz = min(dz, s - dz)
        return math.sqrt(dx*dx + dy*dy + dz*dz)

    def place_at_coords(self, x, y, z):
        """Get node at (x,y,z) coordinates, wrapping periodically."""
        s = self.side
        return self.coord_to_node[(x % s, y % s, z % s)]

    def coords_of(self, node):
        """Return (x,y,z) coordinates of a node."""
        return self.node_coords[node]


# ===========================================================================
# MacroBody — single node with mass property
# ===========================================================================

class MacroBody:
    """Astronomical body on the graph.

    Mass determines:
    - Deposit amount per tick (mass * deposit_strength)
    - Commit mass = ticks between hops (heavier = slower)
    - Nudge strength = 1/commit_mass (heavier = harder to turn)

    Uses continuous internal direction vector from v9.
    """

    def __init__(self, bid, node, mass=1.0, commit_mass=10,
                 deposit_strength=1.0, gradient_coupling=1e-4,
                 edge_gamma_scale=0.0):
        self.bid = bid
        self.node = node
        self.mass = mass
        self.commit_mass = commit_mass
        self.deposit_strength = deposit_strength
        self.gradient_coupling = gradient_coupling
        self.edge_gamma_scale = edge_gamma_scale  # Gravitational time dilation
        self.nudge_strength = 1.0 / float(commit_mass)

        self.commit_counter = 0
        self.internal_direction = np.array([0.0, 0.0, 0.0])
        self.prev_node = node
        self.hops = 0
        self.hop_accumulator = np.array([0.0, 0.0, 0.0])

        # Tracking
        self.trajectory = []      # (tick, node)
        self.coord_history = []   # (tick, x, y, z) — continuous with wrapping
        self.velocity_history = [] # (tick, vx, vy, vz)

    def advance(self, field, tick=None):
        """Advance one tick. Deposit every tick. Hop every commit_mass ticks."""
        # Always deposit (body is always present at its node)
        field.deposit(self.node, self.bid, self.mass * self.deposit_strength)

        # Check commit window (with gravitational time dilation)
        # Near mass: external gamma is high → effective_commit increases → slower hops
        # This is variable edge length: shorter edges near mass = less physical distance/hop
        self.commit_counter += 1
        if self.edge_gamma_scale > 0:
            local_ext = field.external_gamma(self.node, self.bid)
            effective_commit = self.commit_mass * (1.0 + self.edge_gamma_scale * local_ext)
        else:
            effective_commit = self.commit_mass
        if self.commit_counter < effective_commit:
            return False
        self.commit_counter = 0

        neighbors = field.neighbors[self.node]
        if not neighbors:
            return False

        # 1. Compute gradient from external gamma at neighbors
        #    Raw gradient (NOT normalized) — magnitude encodes force law.
        #    gradient = Σ (direction_to_neighbor × external_gamma_at_neighbor)
        #    For 1/r potential on 3D lattice, |gradient| ∝ 1/r² -> Newtonian force.
        gx, gy, gz = 0.0, 0.0, 0.0
        for nb in neighbors:
            ext = field.external_gamma(nb, self.bid)
            d = field.direction_vector(self.node, nb)
            gx += d[0] * ext
            gy += d[1] * ext
            gz += d[2] * ext
        gmag = math.sqrt(gx*gx + gy*gy + gz*gz)

        # 2. Initialize or nudge internal direction
        #    Nudge = gradient_coupling × raw_gradient / commit_mass
        #    gradient_coupling converts gamma-gradient into angular deflection.
        #    The raw gradient preserves distance dependence (force law).
        dir_mag = np.linalg.norm(self.internal_direction)
        if dir_mag < 0.01:
            if gmag > 0:
                # First signal: set direction to gradient direction (unit)
                self.internal_direction = np.array([gx / gmag, gy / gmag,
                                                    gz / gmag])
            else:
                return False  # no signal, stay
        else:
            # Nudge proportional to gradient magnitude (force law!)
            nudge = self.nudge_strength * self.gradient_coupling * gmag
            nudge = min(nudge, 0.5)  # cap for stability
            if gmag > 0:
                self.internal_direction[0] += nudge * (gx / gmag)
                self.internal_direction[1] += nudge * (gy / gmag)
                self.internal_direction[2] += nudge * (gz / gmag)
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        # 3. Bresenham-like accumulator hop — distributes hops across axes
        #    proportional to internal_direction. This is the macro-limit of
        #    micro-scale connector switching patterns.
        self.hop_accumulator += self.internal_direction
        abs_acc = np.abs(self.hop_accumulator)
        axis = int(np.argmax(abs_acc))
        sign = 1 if self.hop_accumulator[axis] >= 0 else -1
        self.hop_accumulator[axis] -= sign

        cur = field.coords_of(self.node)
        target = list(cur)
        target[axis] += sign
        best_nb = field.place_at_coords(target[0], target[1], target[2])

        # 4. Move tagged gamma with the body
        amount = field.tagged[self.bid][self.node]
        if amount > 0:
            field.tagged[self.bid][self.node] = 0.0
            field.tagged[self.bid][best_nb] += amount
        self.prev_node = self.node
        self.node = best_nb
        self.hops += 1
        field.sync_total()
        return True

    def record(self, tick, field):
        self.trajectory.append((tick, self.node))
        c = field.coords_of(self.node)
        self.coord_history.append((tick, c[0], c[1], c[2]))


# ===========================================================================
# Newtonian Reference Solver
# ===========================================================================

def newtonian_two_body_period(m1, m2, r, G_eff):
    """Kepler period for two-body circular orbit. Returns ticks."""
    M = m1 + m2
    if M <= 0 or r <= 0 or G_eff <= 0:
        return float('inf')
    return 2 * math.pi * math.sqrt(r**3 / (G_eff * M))


def newtonian_circular_velocity(m_central, r, G_eff):
    """Circular orbital velocity. Returns hops/tick."""
    if m_central <= 0 or r <= 0 or G_eff <= 0:
        return 0.0
    return math.sqrt(G_eff * m_central / r)


# ===========================================================================
# Utilities
# ===========================================================================

def unwrap_coords(coord_history, side):
    """Unwrap periodic coordinates to continuous trajectory."""
    if len(coord_history) < 2:
        return coord_history
    result = [coord_history[0]]
    cumulative = [coord_history[0][1], coord_history[0][2], coord_history[0][3]]
    for i in range(1, len(coord_history)):
        tick = coord_history[i][0]
        for dim in range(3):
            raw = coord_history[i][dim + 1]
            prev = coord_history[i-1][dim + 1]
            delta = raw - prev
            if delta > side // 2:
                delta -= side
            elif delta < -(side // 2):
                delta += side
            cumulative[dim] += delta
        result.append((tick, cumulative[0], cumulative[1], cumulative[2]))
    return result


def compute_angular_momentum(bodies, field):
    """Z-component of angular momentum relative to system COM."""
    s = field.side
    # COM (periodic-aware, use first body as reference)
    if not bodies:
        return {}
    ref = field.coords_of(bodies[0].node)
    positions = []
    for body in bodies:
        c = field.coords_of(body.node)
        dx = c[0] - ref[0]
        dy = c[1] - ref[1]
        if dx > s // 2: dx -= s
        if dx < -(s // 2): dx += s
        if dy > s // 2: dy -= s
        if dy < -(s // 2): dy += s
        positions.append((ref[0] + dx, ref[1] + dy))

    com_x = sum(p[0] * b.mass for p, b in zip(positions, bodies)) / sum(b.mass for b in bodies)
    com_y = sum(p[1] * b.mass for p, b in zip(positions, bodies)) / sum(b.mass for b in bodies)

    result = {}
    for body, pos in zip(bodies, positions):
        rx = pos[0] - com_x
        ry = pos[1] - com_y
        vx = float(body.internal_direction[0])
        vy = float(body.internal_direction[1])
        result[body.bid] = body.mass * (rx * vy - ry * vx)
    return result


# ===========================================================================
# Plotting
# ===========================================================================

def plot_distances(records, pairs, title, filename, init_dists=None):
    """Plot pairwise distances over time."""
    fig, ax = plt.subplots(figsize=(14, 5))
    ticks = [r['tick'] for r in records]
    for pair in pairs:
        key = f'd_{pair}'
        ax.plot(ticks, [r[key] for r in records], linewidth=1, label=pair)
        if init_dists and pair in init_dists:
            ax.axhline(y=init_dists[pair], color='gray', linestyle='--',
                       alpha=0.3)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance (hops)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_trajectories_xy(bodies, field, filename, title="Trajectories (XY)"):
    """Plot body trajectories projected onto XY plane."""
    fig, ax = plt.subplots(figsize=(8, 8))
    s = field.side
    for body in bodies:
        if not body.coord_history:
            continue
        unwrapped = unwrap_coords(body.coord_history, s)
        xs = [c[1] for c in unwrapped]
        ys = [c[2] for c in unwrapped]
        ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
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
    """Plot total angular momentum over time."""
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


def plot_force_law(force_data, filename):
    """Plot measured acceleration vs distance, overlay 1/r^2."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    rs = [d['r'] for d in force_data]
    accels = [d['accel'] for d in force_data]

    ax1.plot(rs, accels, 'bo-', markersize=8, label='Measured')
    # Fit 1/r^n
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
    ax1.set_xlabel('Distance (hops)')
    ax1.set_ylabel('Acceleration (hops/tick$^2$)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Log-log
    if all(a > 0 for a in accels):
        ax2.loglog(rs, accels, 'bo-', markersize=8, label='Measured')
        if len(rs) >= 2:
            ax2.loglog(r_fit, a_fit, 'r--', label=f'n = {n_fit:.2f}')
        ax2.set_xlabel('Distance (hops)')
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

def run_verification():
    """Run all verification tests."""
    print("\n=== v10 MACRO BODIES VERIFICATION ===\n")
    passed = 0
    failed = 0

    # Test 1: Gamma conservation (float64 spread)
    print("Test 1: Gamma conservation (1000 ticks)")
    f = ContinuousGammaField(1000, k=6, G=10.0, body_ids=['A', 'B'])
    c = f.n_nodes // 2
    f.tagged['A'][c] = 500.0
    f.tagged['B'][c + 10] = 300.0
    f.sync_total()
    init_total = f.total_gamma()
    for _ in range(1000):
        f.spread()
    final_total = f.total_gamma()
    drift = abs(final_total - init_total)
    ok = drift < 1e-6
    print(f"  {'PASS' if ok else 'FAIL'}: {init_total:.1f} -> {final_total:.6f} "
          f"(drift={drift:.2e})")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 2: Peak retention with G > 0
    print("Test 2: Peak retention (G=10, 500 ticks)")
    f2 = ContinuousGammaField(8000, k=6, G=10.0, body_ids=['A'])
    center = f2.n_nodes // 2
    f2.initialize_peak('A', center, 1000.0, smooth_ticks=10)
    for _ in range(500):
        f2.spread()
    peak_val = f2.tagged['A'][f2.tagged_peak_node('A')]
    mean_val = f2.tagged_total('A') / f2.n_nodes
    ratio = peak_val / max(mean_val, 1e-10)
    ok = ratio > 10
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean ratio = {ratio:.0f}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 3: Self-subtraction correctness
    print("Test 3: External gamma = total - own")
    f3 = ContinuousGammaField(1000, k=6, G=10.0, body_ids=['A', 'B'])
    f3.tagged['A'][100] = 500.0
    f3.tagged['B'][200] = 300.0
    f3.sync_total()
    ok = (abs(f3.external_gamma(100, 'A') - 0.0) < 1e-10 and
          abs(f3.external_gamma(200, 'B') - 0.0) < 1e-10 and
          abs(f3.external_gamma(100, 'B') - 500.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 4: Dispersal at G=0
    print("Test 4: Full dispersal at G=0 (500 ticks)")
    f4 = ContinuousGammaField(1000, k=6, G=0.0, body_ids=['A'])
    c4 = f4.n_nodes // 2
    f4.tagged['A'][c4] = 1000.0
    f4.sync_total()
    for _ in range(500):
        f4.spread()
    peak_val = np.max(f4.tagged['A'])
    mean_val = np.mean(f4.tagged['A'])
    ratio = peak_val / max(mean_val, 1e-10)
    ok = ratio < 2.0  # nearly uniform
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean = {ratio:.3f} (want <2)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 5: MacroBody deposit accumulates
    print("Test 5: Body deposits each tick")
    f5 = ContinuousGammaField(1000, k=6, G=10.0, body_ids=['A'])
    body = MacroBody('A', f5.n_nodes // 2, mass=5.0, commit_mass=10,
                     deposit_strength=1.0)
    init = f5.total_gamma()
    for tick in range(10):
        body.advance(f5, tick)
    # 10 ticks * 5.0 mass * 1.0 deposit = 50.0 added
    expected = init + 50.0
    actual = f5.total_gamma()
    ok = abs(actual - expected) < 1e-6
    print(f"  {'PASS' if ok else 'FAIL'}: expected={expected:.1f}, got={actual:.6f}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 6: Body hops every commit_mass ticks
    print("Test 6: Hop timing = commit_mass")
    f6 = ContinuousGammaField(8000, k=6, G=0.0, body_ids=['A', 'B'])
    center6 = f6.n_nodes // 2
    # Place B's gamma far away to create gradient
    far = f6.place_at_coords(f6.side // 2 + 10, f6.side // 2, f6.side // 2)
    f6.tagged['B'][far] = 10000.0
    f6.sync_total()
    for _ in range(50):
        f6.spread()
    body6 = MacroBody('A', center6, mass=1.0, commit_mass=5,
                      deposit_strength=0.001)
    body6.internal_direction = np.array([1.0, 0.0, 0.0])
    hops_at = []
    for tick in range(25):
        moved = body6.advance(f6, tick)
        if moved:
            hops_at.append(tick)
    # Should hop at ticks 4, 9, 14, 19, 24 (every 5 ticks, 0-indexed counter)
    expected_hops = [4, 9, 14, 19, 24]
    ok = hops_at == expected_hops
    print(f"  {'PASS' if ok else 'FAIL'}: hops at {hops_at} "
          f"(expected {expected_hops})")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 7: Distance calculation (periodic)
    print("Test 7: Periodic distance")
    f7 = ContinuousGammaField(1000, k=6, G=0.0, body_ids=[])
    s = f7.side
    n1 = f7.place_at_coords(0, 0, 0)
    n2 = f7.place_at_coords(s - 1, 0, 0)
    d_hop = f7.hop_distance(n1, n2)
    d_euc = f7.euclidean_distance(n1, n2)
    ok = d_hop == 1 and abs(d_euc - 1.0) < 0.01
    print(f"  {'PASS' if ok else 'FAIL'}: hop={d_hop}, euc={d_euc:.2f} "
          f"(edge-to-edge on periodic lattice)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 8: Nudge direction (from v9)
    print("Test 8: Gradient nudges internal direction")
    f8 = ContinuousGammaField(8000, k=6, G=0.0, body_ids=['A', 'B'])
    center8 = f8.n_nodes // 2
    c8 = f8.coords_of(center8)
    # Place B's gamma in +Y direction
    y_node = f8.place_at_coords(c8[0], c8[1] + 5, c8[2])
    f8.tagged['B'][y_node] = 50000.0
    f8.sync_total()
    for _ in range(80):
        f8.spread()
    body8 = MacroBody('A', center8, mass=1.0, commit_mass=5,
                      deposit_strength=0.001, gradient_coupling=0.01)
    body8.internal_direction = np.array([1.0, 0.0, 0.0])  # start +X
    for tick in range(100):
        body8.advance(f8, tick)
    angle = math.atan2(body8.internal_direction[1],
                       body8.internal_direction[0]) * 180 / math.pi
    ok = angle > 5  # should deflect toward +Y
    print(f"  {'PASS' if ok else 'FAIL'}: angle={angle:.1f} deg "
          f"(started at 0 deg, expect >5 deg)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    print(f"\n=== RESULTS: {passed}/{passed+failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 1: Single Peak Stability
# ===========================================================================

def experiment_phase1(side=20, G=10.0, mass=100.0, deposit_strength=1.0,
                      commit_mass=10, ticks=5000):
    print("=" * 70)
    print("PHASE 1: Single Peak Stability")
    print("=" * 70)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, body_ids=['A'])
    center = field.place_at_coords(side // 2, side // 2, side // 2)
    field.initialize_peak('A', center, mass * 100, smooth_ticks=20)

    body = MacroBody('A', center, mass=mass, commit_mass=commit_mass,
                     deposit_strength=deposit_strength)

    init_total = field.total_gamma()
    print(f"\n  Initial gamma: {init_total:.1f}")
    print(f"  Body: mass={mass}, commit_mass={commit_mass}, "
          f"deposit={deposit_strength}")

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        body.advance(field, tick)
        if (tick + 1) % 1000 == 0:
            total = field.total_gamma()
            peak = field.tagged['A'][field.tagged_peak_node('A')]
            elapsed = time.time() - t0
            print(f"    Tick {tick+1:5d}: total={total:.1f}, peak={peak:.1f} "
                  f"({elapsed:.1f}s)")

    print(f"\n  Final gamma: {field.total_gamma():.1f}")
    print(f"  Body hops: {body.hops}")


# ===========================================================================
# Phase 2: Two-Body
# ===========================================================================

def experiment_phase2(side=40, G=10.0, H=0.0, mass=100.0, deposit_strength=1.0,
                      commit_mass=10, separation=20, ticks=50000,
                      initial_momentum='none', gradient_coupling=1e-4,
                      tag='', formation_ticks=0):
    # Antipodal check: separation=side/2 gives zero gradient by periodic symmetry
    if separation >= side // 2:
        old_side = side
        side = max(side, 3 * separation)
        print(f"  WARNING: separation={separation} >= side/2={old_side//2} "
              f"(antipodal dead zone). Increasing side to {side}.")

    print("=" * 70)
    print(f"PHASE 2: Two-Body -- {initial_momentum}")
    print("=" * 70)

    n = side ** 3
    body_ids = ['A', 'B']
    field = ContinuousGammaField(n, k=6, G=G, H=H, body_ids=body_ids)

    # Place bodies along X axis, centered in lattice
    cx, cy, cz = side // 2, side // 2, side // 2
    node_a = field.place_at_coords(cx - separation // 2, cy, cz)
    node_b = field.place_at_coords(cx + separation // 2, cy, cz)

    # Initialize gamma wells
    field.initialize_peak('A', node_a, mass * 50, smooth_ticks=30)
    field.initialize_peak('B', node_b, mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('A', node_a, mass=mass, commit_mass=commit_mass,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
        MacroBody('B', node_b, mass=mass, commit_mass=commit_mass,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
    ]

    # Set initial momentum
    if initial_momentum == 'perpendicular':
        bodies[0].internal_direction = np.array([0.0, 1.0, 0.0])
        bodies[1].internal_direction = np.array([0.0, -1.0, 0.0])
    elif initial_momentum == 'tangential':
        bodies[0].internal_direction = np.array([0.0, 1.0, 0.0])
        bodies[1].internal_direction = np.array([0.0, -1.0, 0.0])

    init_dist = field.hop_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  G={G}, H={H}, mass={mass}, commit_mass={commit_mass}, "
          f"deposit={deposit_strength}")
    print(f"  Initial separation: {init_dist} hops")
    print(f"  Momentum: {initial_momentum}")

    # Formation phase: deposit gamma without moving, let field establish
    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks (deposit only, no dynamics)")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_strength)
            field.spread()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

    # Run simulation
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand()
        for body in bodies:
            body.advance(field, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

        if (tick + 1) % diag_interval == 0:
            d = field.euclidean_distance(bodies[0].node, bodies[1].node)
            d_hop = field.hop_distance(bodies[0].node, bodies[1].node)
            records.append({
                'tick': tick + 1,
                'd_AB': d,
                'd_AB_hop': d_hop,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: d={d:.1f} (hop={d_hop}) "
                      f"hops_A={bodies[0].hops} hops_B={bodies[1].hops} "
                      f"L={L_total:+.2f} ({elapsed:.1f}s)")

    # Results
    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {init_dist} -> {final_d:.1f}")
    print(f"  Hops: A={bodies[0].hops}, B={bodies[1].hops}")
    print(f"  Gamma: {field.total_gamma():.1f}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.1f}, {max(dists):.1f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    if records:
        plot_distances(records, ['AB'],
                       f'Two-Body ({initial_momentum}): G={G}, mass={mass}',
                       RESULTS_DIR / f'phase2_distance{suffix}.png',
                       {'AB': init_dist})

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase2_trajectory{suffix}.png',
                             f'Trajectories ({initial_momentum})')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase2_Lz{suffix}.png')

    return records


# ===========================================================================
# Phase 3: Three-Body
# ===========================================================================

def experiment_phase3(side=40, G=10.0, H=0.0, mass=100.0, deposit_strength=1.0,
                      commit_mass=10, separation=20, ticks=100000,
                      initial_momentum='none', gradient_coupling=1e-4,
                      tag=''):
    # Antipodal check: separation=side/2 gives zero gradient by periodic symmetry
    if separation >= side // 2:
        old_side = side
        side = max(side, 3 * separation)
        print(f"  WARNING: separation={separation} >= side/2={old_side//2} "
              f"(antipodal dead zone). Increasing side to {side}.")

    print("=" * 70)
    print(f"PHASE 3: Three-Body -- {initial_momentum}")
    print("=" * 70)

    n = side ** 3
    body_ids = ['A', 'B', 'C']
    field = ContinuousGammaField(n, k=6, G=G, H=H, body_ids=body_ids)

    # Equilateral triangle in XY plane
    cx, cy, cz = side // 2, side // 2, side // 2
    # A at left, B at right, C at top
    half_sep = separation // 2
    y_offset = int(separation * 0.433)  # sin(60°) ≈ 0.866, half ≈ 0.433
    node_a = field.place_at_coords(cx - half_sep, cy, cz)
    node_b = field.place_at_coords(cx + half_sep, cy, cz)
    node_c = field.place_at_coords(cx, cy + y_offset, cz)

    for bid, node in [('A', node_a), ('B', node_b), ('C', node_c)]:
        field.initialize_peak(bid, node, mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('A', node_a, mass=mass, commit_mass=commit_mass,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
        MacroBody('B', node_b, mass=mass, commit_mass=commit_mass,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
        MacroBody('C', node_c, mass=mass, commit_mass=commit_mass,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
    ]

    if initial_momentum == 'tangential':
        # Tangential to centroid direction
        bodies[0].internal_direction = np.array([0.0, -1.0, 0.0])
        bodies[1].internal_direction = np.array([0.0, 1.0, 0.0])
        bodies[2].internal_direction = np.array([1.0, 0.0, 0.0])

    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  G={G}, mass={mass}, cm={commit_mass}, dep={deposit_strength}")
    print(f"  Separation: {separation}")

    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand()
        for body in bodies:
            body.advance(field, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

        if (tick + 1) % diag_interval == 0:
            d_AB = field.euclidean_distance(bodies[0].node, bodies[1].node)
            d_AC = field.euclidean_distance(bodies[0].node, bodies[2].node)
            d_BC = field.euclidean_distance(bodies[1].node, bodies[2].node)
            records.append({
                'tick': tick + 1,
                'd_AB': d_AB, 'd_AC': d_AC, 'd_BC': d_BC,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: AB={d_AB:.1f} AC={d_AC:.1f} "
                      f"BC={d_BC:.1f} L={L_total:+.2f} ({elapsed:.1f}s)")

    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    if records:
        plot_distances(records, ['AB', 'AC', 'BC'],
                       f'Three-Body ({initial_momentum})',
                       RESULTS_DIR / f'phase3_distance{suffix}.png')

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase3_trajectory{suffix}.png',
                             f'Three-Body Trajectories')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase3_Lz{suffix}.png')

    return records


# ===========================================================================
# Force Law Measurement
# ===========================================================================

def experiment_force_law(side=50, G=10.0, mass=100.0, deposit_strength=1.0,
                         ticks=30000, gradient_coupling=1e-4, tag=''):
    """Measure force law: gamma gradient magnitude vs distance.

    Two complementary measurements:
    1. DIRECT: Probe the raw gamma gradient at various distances from A's well.
       This is purely a field measurement — no body dynamics involved.
       If gradient ∝ 1/r² -> Newtonian force law confirmed.
    2. DYNAMIC: Release body B from rest at various distances, track infall
       trajectory, compute acceleration from d²r/dt².
    """
    print("=" * 70)
    print("FORCE LAW MEASUREMENT")
    print("=" * 70)

    # ---- Part 1: Direct gamma gradient measurement ----
    print("\n  PART 1: Direct gamma gradient vs distance")
    print("  " + "-" * 50)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, body_ids=['A'])
    cx, cy, cz = side // 2, side // 2, side // 2
    node_a = field.place_at_coords(cx, cy, cz)

    # A deposits and field spreads until quasi-steady-state
    body_a = MacroBody('A', node_a, mass=mass, commit_mass=999999,
                       deposit_strength=deposit_strength)
    formation_ticks = 5000
    print(f"    Formation: {formation_ticks} ticks (mass={mass}, "
          f"deposit={deposit_strength})...")
    for tick in range(formation_ticks):
        body_a.advance(field, tick)
        field.spread()

    total_deposited = mass * deposit_strength * formation_ticks
    print(f"    Total gamma deposited: {total_deposited:.0f}")
    print(f"    Field total: {field.total_gamma():.0f}")

    # Probe gradient at various distances along +X axis
    separations = [5, 8, 10, 12, 15, 18, 20, 25, 30]
    gradient_data = []
    print(f"\n    {'r':>5s} {'|grad|':>12s} {'gamma_at_r':>12s} "
          f"{'grad_toward':>12s}")
    for r in separations:
        if r >= side // 2 - 2:
            continue
        probe = field.place_at_coords(cx + r, cy, cz)
        neighbors = field.neighbors[probe]

        # Compute raw gradient (same as body would see)
        gx, gy, gz = 0.0, 0.0, 0.0
        for nb in neighbors:
            ext = field.tagged['A'][nb]  # A's field only
            d = field.direction_vector(probe, nb)
            gx += d[0] * ext
            gy += d[1] * ext
            gz += d[2] * ext
        gmag = math.sqrt(gx * gx + gy * gy + gz * gz)

        # Radial component (toward A = -X direction)
        grad_radial = -gx  # negative because A is in -X direction

        gamma_at_r = field.tagged['A'][probe]
        gradient_data.append({
            'r': r, 'gmag': gmag, 'gamma': gamma_at_r,
            'grad_radial': grad_radial,
        })
        print(f"    {r:5d} {gmag:12.4f} {gamma_at_r:12.4f} "
              f"{grad_radial:12.4f}")

    # Fit power law: gradient ∝ 1/r^n
    valid = [d for d in gradient_data if d['gmag'] > 0]
    n_fit = None
    if len(valid) >= 3:
        log_r = np.log([d['r'] for d in valid])
        log_g = np.log([d['gmag'] for d in valid])
        coeffs = np.polyfit(log_r, log_g, 1)
        n_fit = -coeffs[0]
        k_fit = np.exp(coeffs[1])
        print(f"\n    Fit: |gradient| ~ 1/r^{n_fit:.3f}  "
              f"(Newton = 2.0)")
        print(f"    k = {k_fit:.4f}")

    # ---- Part 2: Dynamic infall measurement ----
    print("\n  PART 2: Dynamic infall (trajectory-based)")
    print("  " + "-" * 50)

    test_seps = [8, 12, 16, 20]
    commit_mass_b = 5
    infall_data = []

    for sep in test_seps:
        print(f"\n    --- r0 = {sep} hops ---")
        field2 = ContinuousGammaField(n, k=6, G=G, body_ids=['A', 'B'])
        node_a2 = field2.place_at_coords(cx, cy, cz)
        node_b2 = field2.place_at_coords(cx + sep, cy, cz)

        # Only A's field forms (B doesn't exist during formation)
        body_a2 = MacroBody('A', node_a2, mass=mass, commit_mass=999999,
                            deposit_strength=deposit_strength)
        print(f"      Formation: {formation_ticks} ticks (A only)...")
        for tick in range(formation_ticks):
            body_a2.advance(field2, tick)
            field2.spread()

        # Now place B and track its trajectory
        body_b2 = MacroBody('B', node_b2, mass=mass * 0.01, commit_mass=commit_mass_b,
                            deposit_strength=deposit_strength * 0.01,
                            gradient_coupling=gradient_coupling)
        distances = []
        measurement_ticks = min(ticks, 20000)

        for tick in range(formation_ticks, formation_ticks + measurement_ticks):
            field2.spread()
            body_a2.advance(field2, tick)
            moved = body_b2.advance(field2, tick)

            if moved:
                d = field2.euclidean_distance(body_a2.node, body_b2.node)
                distances.append((tick, d))
                # Stop if B reaches A
                if d < 2:
                    break

        if len(distances) >= 4:
            ticks_arr = np.array([d[0] for d in distances], dtype=np.float64)
            dists_arr = np.array([d[1] for d in distances])

            # Velocity: dr/dt (per hop, so dt = commit_mass)
            dt_hop = float(commit_mass_b)
            velocities = np.diff(dists_arr) / dt_hop

            # Acceleration: dv/dt
            if len(velocities) >= 3:
                accels = np.diff(velocities) / dt_hop
                # Use early acceleration (before B moves much from starting r)
                n_early = min(5, len(accels))
                avg_accel = np.mean(accels[:n_early])
                avg_vel = np.mean(velocities[:n_early])
                print(f"      Hops: {len(distances)}, "
                      f"d: {distances[0][1]:.1f} -> {distances[-1][1]:.1f}")
                print(f"      Early avg velocity: {avg_vel:.6f} hops/tick")
                print(f"      Early avg accel:    {avg_accel:.8f} hops/tick^2")
                infall_data.append({
                    'r': sep, 'accel': abs(avg_accel),
                    'velocity': avg_vel,
                    'final_d': distances[-1][1],
                    'n_hops': len(distances),
                })
            else:
                print(f"      Not enough hops for acceleration ({len(distances)})")
        else:
            print(f"      Too few hops ({len(distances)})")

    # ---- Summary ----
    print("\n  === FORCE LAW SUMMARY ===")

    if gradient_data:
        print("\n  Direct gradient measurement:")
        print(f"  {'r':>5s} {'|gradient|':>12s} {'gamma(r)':>12s}")
        for d in gradient_data:
            print(f"  {d['r']:5d} {d['gmag']:12.4f} {d['gamma']:12.4f}")
        if n_fit is not None:
            print(f"\n  Power law: |gradient| ~ 1/r^{n_fit:.3f}")
            verdict = ('PASS (Newton)' if abs(n_fit - 2.0) < 0.3
                        else 'PARTIAL' if abs(n_fit - 2.0) < 0.5
                        else 'FAIL')
            print(f"  Verdict: {verdict}")

    if infall_data:
        print("\n  Dynamic infall:")
        print(f"  {'r':>5s} {'accel':>12s} {'velocity':>12s} {'hops':>6s}")
        for d in infall_data:
            print(f"  {d['r']:5d} {d['accel']:12.8f} "
                  f"{d['velocity']:12.6f} {d['n_hops']:6d}")

        if len(infall_data) >= 2 and all(d['accel'] > 0 for d in infall_data):
            log_r = np.log([d['r'] for d in infall_data])
            log_a = np.log([d['accel'] for d in infall_data])
            coeffs = np.polyfit(log_r, log_a, 1)
            n_dyn = -coeffs[0]
            print(f"\n  Dynamic fit: accel ~ 1/r^{n_dyn:.3f}")

    # Plot
    suffix = f"_{tag}" if tag else ""
    if gradient_data:
        plot_force_law([{'r': d['r'], 'accel': d['gmag']}
                        for d in gradient_data if d['gmag'] > 0],
                       RESULTS_DIR / f'force_law_gradient{suffix}.png')
    if infall_data and any(d['accel'] > 0 for d in infall_data):
        plot_force_law([d for d in infall_data if d['accel'] > 0],
                       RESULTS_DIR / f'force_law_dynamic{suffix}.png')

    return {'gradient': gradient_data, 'infall': infall_data}


# ===========================================================================
# Kepler Test
# ===========================================================================

def experiment_kepler(side=50, G=10.0, mass=100.0, deposit_strength=1.0,
                      commit_mass=10, ticks=200000, tag=''):
    """Test Kepler's third law: T² ∝ r³ at different separations."""
    print("=" * 70)
    print("KEPLER'S THIRD LAW TEST")
    print("=" * 70)

    separations = [10, 15, 20]
    kepler_data = []

    for sep in separations:
        print(f"\n  --- Separation = {sep} ---")
        records = experiment_phase2(
            side=side, G=G, mass=mass, deposit_strength=deposit_strength,
            commit_mass=commit_mass, separation=sep, ticks=ticks,
            initial_momentum='perpendicular',
            tag=f'kepler_r{sep}')

        if records and len(records) > 20:
            dists = [r['d_AB'] for r in records]
            ticks_arr = [r['tick'] for r in records]

            # Find period from distance oscillation
            # Count zero-crossings of (dist - mean_dist)
            mean_d = np.mean(dists)
            crossings = []
            for i in range(1, len(dists)):
                if (dists[i] - mean_d) * (dists[i-1] - mean_d) < 0:
                    crossings.append(ticks_arr[i])

            if len(crossings) >= 4:
                # Period = 2 × average half-period
                half_periods = [crossings[i+1] - crossings[i]
                                for i in range(len(crossings) - 1)]
                T = 2 * np.mean(half_periods)
                kepler_data.append({'r': sep, 'T': T, 'T2': T**2, 'r3': sep**3})
                print(f"    Period ~ {T:.0f} ticks ({len(crossings)} crossings)")
            else:
                print(f"    Not enough oscillations ({len(crossings)} crossings)")
        else:
            print(f"    No data")

    if len(kepler_data) >= 2:
        print("\n  === Kepler Summary ===")
        print(f"  {'r':>5s} {'T':>10s} {'T^2':>14s} {'r^3':>10s} {'T^2/r^3':>10s}")
        for d in kepler_data:
            ratio = d['T2'] / d['r3'] if d['r3'] > 0 else 0
            print(f"  {d['r']:5d} {d['T']:10.0f} {d['T2']:14.0f} "
                  f"{d['r3']:10d} {ratio:10.2f}")
        # If T²/r³ is constant -> Kepler confirmed
        ratios = [d['T2'] / d['r3'] for d in kepler_data if d['r3'] > 0]
        if ratios:
            cv = np.std(ratios) / np.mean(ratios) if np.mean(ratios) > 0 else 999
            print(f"\n  T^2/r^3 variation: CV = {cv:.3f} "
                  f"({'PASS (Kepler)' if cv < 0.1 else 'FAIL' if cv > 0.3 else 'PARTIAL'})")

    return kepler_data


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v10: Macro Bodies on Expanding Graph')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase1', action='store_true')
    parser.add_argument('--phase2', action='store_true')
    parser.add_argument('--phase3', action='store_true')
    parser.add_argument('--force-law', action='store_true')
    parser.add_argument('--kepler', action='store_true')

    parser.add_argument('--side', type=int, default=40)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--H', type=float, default=0.0,
                        help='Expansion rate per tick (suppressed near mass)')
    parser.add_argument('--mass', type=float, default=100.0)
    parser.add_argument('--deposit-strength', type=float, default=1.0)
    parser.add_argument('--commit-mass', type=int, default=10)
    parser.add_argument('--separation', type=int, default=20)
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--initial-momentum',
                        choices=['none', 'perpendicular', 'tangential'],
                        default='none')
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--gradient-coupling', type=float, default=1e-4,
                        help='Coupling constant: gradient magnitude -> angular nudge')
    parser.add_argument('--formation-ticks', type=int, default=0,
                        help='Ticks of deposit-only field formation before dynamics')

    args = parser.parse_args()

    if args.verify:
        run_verification()
    if args.phase1:
        experiment_phase1(side=args.side, G=args.G, mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass, ticks=args.ticks)
    if args.phase2:
        experiment_phase2(side=args.side, G=args.G, H=args.H, mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          initial_momentum=args.initial_momentum,
                          gradient_coupling=args.gradient_coupling,
                          tag=args.tag,
                          formation_ticks=args.formation_ticks)
    if args.phase3:
        experiment_phase3(side=args.side, G=args.G, H=args.H, mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          initial_momentum=args.initial_momentum,
                          gradient_coupling=args.gradient_coupling,
                          tag=args.tag)
    if args.force_law:
        experiment_force_law(side=max(args.side, 50), G=args.G,
                             mass=args.mass,
                             deposit_strength=args.deposit_strength,
                             ticks=args.ticks,
                             gradient_coupling=args.gradient_coupling,
                             tag=args.tag)
    if args.kepler:
        experiment_kepler(side=max(args.side, 50), G=args.G,
                          mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          ticks=args.ticks, tag=args.tag)

    if not any([args.verify, args.phase1, args.phase2, args.phase3,
                args.force_law, args.kepler]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
