"""v11: Macro Bodies on Random Geometric Graph — Topology-Only Gravity.

Tests whether gravity emerges purely from graph topology, without:
- Lattice anisotropy (k=6 cubic → isotropic RGG with k~50-100)
- Bresenham hop accumulator (unnecessary with high-k angular resolution)
- Hand-tuned time dilation (edge_gamma_scale removed entirely)

The graph IS the space. Nodes at random positions in periodic [0,L)^3 box,
connected if within radius r. Field spreading, gradient computation, and
body movement all derive from graph topology + embedding positions.

Hypothesis: v10's limitations (force law ~1/r^2.2, orbits only at r~2,
narrow capture basin) came from k=6 lattice anisotropy, not the physics.

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --phase1 --ticks 5000
    python macro_bodies.py --phase2 --ticks 30000 --initial-momentum perpendicular
    python macro_bodies.py --phase3 --ticks 50000 --initial-momentum tangential
    python macro_bodies.py --force-law --ticks 30000
    python macro_bodies.py --kepler --ticks 100000

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
from scipy.sparse import csr_matrix
from scipy.spatial import cKDTree

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# ContinuousGammaField — deterministic float64 tagged field on RGG
# ===========================================================================

class ContinuousGammaField:
    """Deterministic self-gravitating gamma field on a random geometric graph.

    Nodes are placed uniformly in a periodic [0, L)^3 box and connected
    if within distance r_connect. This gives an isotropic graph with
    tunable mean degree k.

    Each body has a separate tagged field layer. Total gamma = sum of all tags.
    Self-gravitation: alpha_eff = alpha / (1 + G * total_gamma).
    External gamma for body B = total - tagged[B].
    """

    def __init__(self, n_nodes, L=10.0, k_target=50, alpha=None, G=1.0,
                 H=0.0, G_expand=None, seed=42, body_ids=None):
        self.L = L
        self.G = G
        self.H = H
        self.G_expand = G_expand if G_expand is not None else G
        self.seed = seed
        self.n_nodes = n_nodes

        print(f"  Building RGG: N={n_nodes}, L={L:.1f}, k_target={k_target}")
        t0 = time.time()

        # Generate random node positions in periodic box
        rng = np.random.default_rng(seed)
        self.node_positions = rng.uniform(0, L, size=(n_nodes, 3))

        # Connection radius for target mean degree
        # k = n * (4/3) * pi * r^3 / L^3  =>  r = L * (3k / (4*pi*n))^(1/3)
        r_connect = L * (3.0 * k_target / (4.0 * np.pi * n_nodes)) ** (1.0 / 3.0)
        self.r_connect = r_connect

        # Build periodic KDTree and find all edges
        self._tree = cKDTree(self.node_positions, boxsize=L)
        pairs = self._tree.query_pairs(r_connect, output_type='ndarray')

        # Build sparse symmetric adjacency matrix
        if len(pairs) > 0:
            row = np.concatenate([pairs[:, 0], pairs[:, 1]])
            col = np.concatenate([pairs[:, 1], pairs[:, 0]])
            data = np.ones(len(row), dtype=np.float64)
            self.A = csr_matrix((data, (row, col)), shape=(n_nodes, n_nodes))
        else:
            self.A = csr_matrix((n_nodes, n_nodes), dtype=np.float64)

        # Neighbor lists
        self.neighbors = [[] for _ in range(n_nodes)]
        if len(pairs) > 0:
            for i, j in pairs:
                self.neighbors[i].append(j)
                self.neighbors[j].append(i)

        # Degrees
        self.degrees = np.array(self.A.sum(axis=1)).flatten()
        self.degrees = np.maximum(self.degrees, 1.0)
        self.k_actual = float(np.mean(self.degrees))

        elapsed = time.time() - t0
        print(f"    Built in {elapsed:.1f}s: {len(pairs)} edges, "
              f"k_actual={self.k_actual:.1f}, r_connect={r_connect:.3f}")

        # Check connectivity
        k_min = int(np.min(self.degrees))
        if k_min == 0:
            isolated = int(np.sum(self.degrees < 1.5))
            print(f"    WARNING: {isolated} isolated nodes (k_min={k_min})")

        # Diffusion rate: independent of k.
        # On k=6 cubic lattice, alpha=1/6 gives good field profiles.
        # We keep the same diffusion rate regardless of graph connectivity.
        # The "speed of light" (1 hop/tick) is separate from diffusion rate.
        self.alpha = alpha if alpha is not None else 0.15

        # Tagged fields
        self.body_ids = body_ids or []
        self.tagged = {
            bid: np.zeros(n_nodes, dtype=np.float64)
            for bid in self.body_ids
        }
        self.gamma = np.zeros(n_nodes, dtype=np.float64)

        # Mean edge length (for diagnostics)
        if len(pairs) > 0:
            deltas = (self.node_positions[pairs[:, 1]]
                      - self.node_positions[pairs[:, 0]])
            half_L = L / 2.0
            deltas = np.where(deltas > half_L, deltas - L, deltas)
            deltas = np.where(deltas < -half_L, deltas + L, deltas)
            self.mean_edge_length = float(np.mean(np.linalg.norm(deltas, axis=1)))
        else:
            self.mean_edge_length = 1.0

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
        """Expansion: dilute gamma, suppressed near gamma wells."""
        if self.H <= 0:
            return
        H_local = self.H / (1.0 + self.G_expand * np.abs(self.gamma))
        dilution = 1.0 / (1.0 + H_local)
        for bid in self.body_ids:
            self.tagged[bid] *= dilution
        self.sync_total()

    def deposit(self, node, bid, amount):
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
        """Periodic displacement vector in embedding space."""
        delta = self.node_positions[to_node] - self.node_positions[from_node]
        half_L = self.L / 2.0
        delta = np.where(delta > half_L, delta - self.L, delta)
        delta = np.where(delta < -half_L, delta + self.L, delta)
        return delta

    def euclidean_distance(self, node_a, node_b):
        """Euclidean distance with periodic wrapping."""
        return float(np.linalg.norm(self.direction_vector(node_a, node_b)))

    def nearest_node(self, position):
        """Find node nearest to a 3D position (periodic)."""
        pos = np.asarray(position) % self.L
        _, idx = self._tree.query(pos)
        return int(idx)

    def position_of(self, node):
        """Return (x, y, z) position of a node."""
        return self.node_positions[node]


# ===========================================================================
# MacroBody — single node with mass property
# ===========================================================================

class MacroBody:
    """Astronomical body on the graph.

    Movement: dot-product argmax over neighbors (works on any graph with
    sufficient angular resolution, k >= ~20).

    No time dilation — hop rate is constant everywhere. Testing whether
    topology alone produces stable orbits.
    """

    def __init__(self, bid, node, mass=1.0, commit_mass=10,
                 deposit_strength=1.0, gradient_coupling=1e-4):
        self.bid = bid
        self.node = node
        self.mass = mass
        self.commit_mass = commit_mass
        self.deposit_strength = deposit_strength
        self.gradient_coupling = gradient_coupling
        self.nudge_strength = 1.0 / float(commit_mass)

        self.commit_counter = 0
        self.internal_direction = np.array([0.0, 0.0, 0.0])
        self.prev_node = node
        self.hops = 0

        # Tracking
        self.trajectory = []
        self.coord_history = []
        self.velocity_history = []

    def advance(self, field, tick=None):
        """Advance one tick. Deposit every tick. Hop every commit_mass ticks."""
        field.deposit(self.node, self.bid, self.mass * self.deposit_strength)

        self.commit_counter += 1
        if self.commit_counter < self.commit_mass:
            return False
        self.commit_counter = 0

        neighbors = field.neighbors[self.node]
        if not neighbors:
            return False

        # 1. Compute gradient from external gamma at neighbors
        grad = np.zeros(3)
        for nb in neighbors:
            ext = field.external_gamma(nb, self.bid)
            d = field.direction_vector(self.node, nb)
            grad += d * ext
        gmag = np.linalg.norm(grad)

        # 2. Initialize or nudge internal direction
        dir_mag = np.linalg.norm(self.internal_direction)
        if dir_mag < 0.01:
            if gmag > 0:
                self.internal_direction = grad / gmag
            else:
                return False
        else:
            nudge = self.nudge_strength * self.gradient_coupling * gmag
            nudge = min(nudge, 0.5)
            if gmag > 0:
                grad_unit = grad / gmag
                self.internal_direction += nudge * grad_unit
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        # 3. Hop to neighbor with highest dot product to internal_direction
        best_nb = None
        best_dot = -np.inf
        for nb in neighbors:
            d = field.direction_vector(self.node, nb)
            d_norm = np.linalg.norm(d)
            if d_norm > 0:
                dot = np.dot(self.internal_direction, d / d_norm)
                if dot > best_dot:
                    best_dot = dot
                    best_nb = nb

        if best_nb is None:
            return False

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
        c = field.position_of(self.node)
        self.coord_history.append((tick, c[0], c[1], c[2]))


# ===========================================================================
# Newtonian Reference Solver
# ===========================================================================

def newtonian_two_body_period(m1, m2, r, G_eff):
    M = m1 + m2
    if M <= 0 or r <= 0 or G_eff <= 0:
        return float('inf')
    return 2 * math.pi * math.sqrt(r**3 / (G_eff * M))


def newtonian_circular_velocity(m_central, r, G_eff):
    if m_central <= 0 or r <= 0 or G_eff <= 0:
        return 0.0
    return math.sqrt(G_eff * m_central / r)


# ===========================================================================
# Utilities
# ===========================================================================

def unwrap_coords(coord_history, L):
    """Unwrap periodic coordinates to continuous trajectory."""
    if len(coord_history) < 2:
        return coord_history
    result = [coord_history[0]]
    cumulative = [coord_history[0][1], coord_history[0][2], coord_history[0][3]]
    half_L = L / 2.0
    for i in range(1, len(coord_history)):
        tick = coord_history[i][0]
        for dim in range(3):
            raw = coord_history[i][dim + 1]
            prev = coord_history[i-1][dim + 1]
            delta = raw - prev
            if delta > half_L:
                delta -= L
            elif delta < -half_L:
                delta += L
            cumulative[dim] += delta
        result.append((tick, cumulative[0], cumulative[1], cumulative[2]))
    return result


def compute_angular_momentum(bodies, field):
    """Z-component of angular momentum relative to system COM."""
    L_box = field.L
    half_L = L_box / 2.0
    if not bodies:
        return {}
    ref = field.position_of(bodies[0].node)
    positions = []
    for body in bodies:
        c = field.position_of(body.node)
        dx = c[0] - ref[0]
        dy = c[1] - ref[1]
        if dx > half_L: dx -= L_box
        if dx < -half_L: dx += L_box
        if dy > half_L: dy -= L_box
        if dy < -half_L: dy += L_box
        positions.append((ref[0] + dx, ref[1] + dy))

    total_mass = sum(b.mass for b in bodies)
    com_x = sum(p[0] * b.mass for p, b in zip(positions, bodies)) / total_mass
    com_y = sum(p[1] * b.mass for p, b in zip(positions, bodies)) / total_mass

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


def plot_trajectories_xy(bodies, field, filename, title="Trajectories (XY)"):
    fig, ax = plt.subplots(figsize=(8, 8))
    L = field.L
    for body in bodies:
        if not body.coord_history:
            continue
        unwrapped = unwrap_coords(body.coord_history, L)
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
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    rs = [d['r'] for d in force_data]
    accels = [d['accel'] for d in force_data]

    ax1.plot(rs, accels, 'bo-', markersize=8, label='Measured')
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
    ax1.set_ylabel('|Gradient|')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    if all(a > 0 for a in accels):
        ax2.loglog(rs, accels, 'bo-', markersize=8, label='Measured')
        if len(rs) >= 2:
            ax2.loglog(r_fit, a_fit, 'r--', label=f'n = {n_fit:.2f}')
        ax2.set_xlabel('Distance')
        ax2.set_ylabel('|Gradient|')
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
    print("\n=== v11 RGG MACRO BODIES VERIFICATION ===\n")
    passed = 0
    failed = 0

    # Test 1: Gamma conservation
    print("Test 1: Gamma conservation (1000 ticks)")
    f = ContinuousGammaField(500, L=5.0, k_target=30, G=10.0,
                              body_ids=['A', 'B'])
    n_a = f.nearest_node([2.5, 2.5, 2.5])
    n_b = f.nearest_node([3.5, 2.5, 2.5])
    f.tagged['A'][n_a] = 500.0
    f.tagged['B'][n_b] = 300.0
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
    f2 = ContinuousGammaField(1000, L=5.0, k_target=30, G=10.0,
                               body_ids=['A'])
    center = f2.nearest_node([2.5, 2.5, 2.5])
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
    f3 = ContinuousGammaField(500, L=5.0, k_target=30, G=10.0,
                               body_ids=['A', 'B'])
    n3a = f3.nearest_node([1.0, 2.5, 2.5])
    n3b = f3.nearest_node([4.0, 2.5, 2.5])
    f3.tagged['A'][n3a] = 500.0
    f3.tagged['B'][n3b] = 300.0
    f3.sync_total()
    ok = (abs(f3.external_gamma(n3a, 'A') - 0.0) < 1e-10 and
          abs(f3.external_gamma(n3b, 'B') - 0.0) < 1e-10 and
          abs(f3.external_gamma(n3a, 'B') - 500.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 4: Dispersal at G=0
    print("Test 4: Full dispersal at G=0 (500 ticks)")
    f4 = ContinuousGammaField(500, L=5.0, k_target=30, G=0.0,
                               body_ids=['A'])
    c4 = f4.nearest_node([2.5, 2.5, 2.5])
    f4.tagged['A'][c4] = 1000.0
    f4.sync_total()
    for _ in range(500):
        f4.spread()
    peak_val = np.max(f4.tagged['A'])
    mean_val = np.mean(f4.tagged['A'])
    ratio = peak_val / max(mean_val, 1e-10)
    ok = ratio < 2.0
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean = {ratio:.3f} (want <2)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 5: MacroBody deposit accumulates
    print("Test 5: Body deposits each tick")
    f5 = ContinuousGammaField(500, L=5.0, k_target=30, G=10.0,
                               body_ids=['A'])
    body = MacroBody('A', f5.nearest_node([2.5, 2.5, 2.5]),
                     mass=5.0, commit_mass=10, deposit_strength=1.0)
    init = f5.total_gamma()
    for tick in range(10):
        body.advance(f5, tick)
    expected = init + 50.0
    actual = f5.total_gamma()
    ok = abs(actual - expected) < 1e-6
    print(f"  {'PASS' if ok else 'FAIL'}: expected={expected:.1f}, "
          f"got={actual:.6f}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 6: Body hops every commit_mass ticks
    print("Test 6: Hop timing = commit_mass")
    f6 = ContinuousGammaField(1000, L=5.0, k_target=30, G=0.0,
                               body_ids=['A', 'B'])
    center6 = f6.nearest_node([2.5, 2.5, 2.5])
    far6 = f6.nearest_node([4.0, 2.5, 2.5])
    f6.tagged['B'][far6] = 10000.0
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
    expected_hops = [4, 9, 14, 19, 24]
    ok = hops_at == expected_hops
    print(f"  {'PASS' if ok else 'FAIL'}: hops at {hops_at} "
          f"(expected {expected_hops})")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 7: Periodic distance
    print("Test 7: Periodic distance wrapping")
    f7 = ContinuousGammaField(500, L=5.0, k_target=30, G=0.0,
                               body_ids=[])
    n7a = f7.nearest_node([0.1, 2.5, 2.5])
    n7b = f7.nearest_node([4.9, 2.5, 2.5])
    d_euc = f7.euclidean_distance(n7a, n7b)
    # These nodes should be close to each other via periodic wrapping
    # (both near the x=0/L boundary). Actual distance depends on nearest
    # node positions but should be < 1.0 for L=5 with 500 nodes.
    ok = d_euc < 1.5
    print(f"  {'PASS' if ok else 'FAIL'}: distance across boundary = {d_euc:.3f} "
          f"(want < 1.5)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 8: Gradient nudges direction
    print("Test 8: Gradient nudges internal direction")
    f8 = ContinuousGammaField(1000, L=5.0, k_target=30, G=0.0,
                               body_ids=['A', 'B'])
    center8 = f8.nearest_node([2.5, 2.5, 2.5])
    y_node = f8.nearest_node([2.5, 4.0, 2.5])
    f8.tagged['B'][y_node] = 50000.0
    f8.sync_total()
    for _ in range(80):
        f8.spread()
    body8 = MacroBody('A', center8, mass=1.0, commit_mass=5,
                      deposit_strength=0.001, gradient_coupling=0.001)
    body8.internal_direction = np.array([1.0, 0.0, 0.0])
    for tick in range(100):
        body8.advance(f8, tick)
    angle = math.atan2(body8.internal_direction[1],
                       body8.internal_direction[0]) * 180 / math.pi
    ok = abs(angle) > 5  # deflected from initial 0 deg
    print(f"  {'PASS' if ok else 'FAIL'}: angle={angle:.1f} deg "
          f"(started at 0, expect |angle| > 5)")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # Test 9: Degree distribution
    print("Test 9: RGG degree distribution")
    f9 = ContinuousGammaField(2000, L=10.0, k_target=50, G=0.0,
                               body_ids=[])
    k_mean = f9.k_actual
    k_rel_err = abs(k_mean - 50) / 50
    k_min = int(np.min(f9.degrees))
    ok = k_rel_err < 0.15 and k_min >= 1
    print(f"  {'PASS' if ok else 'FAIL'}: k_mean={k_mean:.1f} "
          f"(target=50, err={k_rel_err:.1%}), k_min={k_min}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    print(f"\n=== RESULTS: {passed}/{passed+failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 1: Single Peak Stability
# ===========================================================================

def experiment_phase1(n_nodes=5000, L=10.0, k_target=50, G=10.0,
                      mass=100.0, deposit_strength=1.0,
                      commit_mass=10, ticks=5000):
    print("=" * 70)
    print("PHASE 1: Single Peak Stability")
    print("=" * 70)

    field = ContinuousGammaField(n_nodes, L=L, k_target=k_target, G=G,
                                  body_ids=['A'])
    center = field.nearest_node([L/2, L/2, L/2])
    field.initialize_peak('A', center, mass * 50, smooth_ticks=20)

    body = MacroBody('A', center, mass=mass, commit_mass=commit_mass,
                     deposit_strength=deposit_strength)

    init_total = field.total_gamma()
    print(f"\n  Initial gamma: {init_total:.1f}")
    print(f"  Body: mass={mass}, commit_mass={commit_mass}")

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

def experiment_phase2(n_nodes=5000, L=10.0, k_target=50, G=10.0, H=0.0,
                      mass=100.0, deposit_strength=1.0,
                      commit_mass=10, separation=2.5, ticks=50000,
                      initial_momentum='none', gradient_coupling=1e-4,
                      tag='', formation_ticks=0):
    if separation >= L / 2:
        print(f"  WARNING: separation={separation} >= L/2={L/2} "
              f"(periodic image overlap)")

    print("=" * 70)
    print(f"PHASE 2: Two-Body -- {initial_momentum}")
    print("=" * 70)

    body_ids = ['A', 'B']
    field = ContinuousGammaField(n_nodes, L=L, k_target=k_target, G=G, H=H,
                                  body_ids=body_ids)

    cx, cy, cz = L / 2, L / 2, L / 2
    node_a = field.nearest_node([cx - separation / 2, cy, cz])
    node_b = field.nearest_node([cx + separation / 2, cy, cz])

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

    if initial_momentum in ('perpendicular', 'tangential'):
        bodies[0].internal_direction = np.array([0.0, 1.0, 0.0])
        bodies[1].internal_direction = np.array([0.0, -1.0, 0.0])

    init_dist = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  RGG: N={field.n_nodes}, k={field.k_actual:.1f}, L={L}")
    print(f"  G={G}, H={H}, mass={mass}, commit_mass={commit_mass}")
    print(f"  Initial separation: {init_dist:.2f}")
    print(f"  Momentum: {initial_momentum}")

    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks (deposit only)")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_strength)
            field.spread()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

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
            records.append({'tick': tick + 1, 'd_AB': d})

            Lz = compute_angular_momentum(bodies, field)
            L_total = sum(Lz.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: d={d:.2f} "
                      f"hops_A={bodies[0].hops} hops_B={bodies[1].hops} "
                      f"L={L_total:+.2f} ({elapsed:.1f}s)")

    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {init_dist:.2f} -> {final_d:.2f}")
    print(f"  Hops: A={bodies[0].hops}, B={bodies[1].hops}")
    print(f"  Gamma: {field.total_gamma():.1f}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.2f}, {max(dists):.2f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    if records:
        plot_distances(records, ['AB'],
                       f'Two-Body ({initial_momentum}): G={G}, k={field.k_actual:.0f}',
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

def experiment_phase3(n_nodes=5000, L=10.0, k_target=50, G=10.0, H=0.0,
                      mass=100.0, deposit_strength=1.0,
                      commit_mass=10, separation=2.5, ticks=100000,
                      initial_momentum='none', gradient_coupling=1e-4,
                      tag=''):
    if separation >= L / 2:
        print(f"  WARNING: separation={separation} >= L/2={L/2}")

    print("=" * 70)
    print(f"PHASE 3: Three-Body -- {initial_momentum}")
    print("=" * 70)

    body_ids = ['A', 'B', 'C']
    field = ContinuousGammaField(n_nodes, L=L, k_target=k_target, G=G, H=H,
                                  body_ids=body_ids)

    cx, cy, cz = L / 2, L / 2, L / 2
    half_sep = separation / 2
    y_offset = separation * 0.433
    node_a = field.nearest_node([cx - half_sep, cy, cz])
    node_b = field.nearest_node([cx + half_sep, cy, cz])
    node_c = field.nearest_node([cx, cy + y_offset, cz])

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
        bodies[0].internal_direction = np.array([0.0, -1.0, 0.0])
        bodies[1].internal_direction = np.array([0.0, 1.0, 0.0])
        bodies[2].internal_direction = np.array([1.0, 0.0, 0.0])

    print(f"\n  RGG: N={field.n_nodes}, k={field.k_actual:.1f}, L={L}")
    print(f"  G={G}, mass={mass}, cm={commit_mass}")
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

            Lz = compute_angular_momentum(bodies, field)
            L_total = sum(Lz.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: AB={d_AB:.2f} AC={d_AC:.2f} "
                      f"BC={d_BC:.2f} L={L_total:+.2f} ({elapsed:.1f}s)")

    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    if records:
        plot_distances(records, ['AB', 'AC', 'BC'],
                       f'Three-Body ({initial_momentum})',
                       RESULTS_DIR / f'phase3_distance{suffix}.png')

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase3_trajectory{suffix}.png',
                             'Three-Body Trajectories')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase3_Lz{suffix}.png')

    return records


# ===========================================================================
# Force Law Measurement
# ===========================================================================

def experiment_force_law(n_nodes=8000, L=15.0, k_target=50, G=10.0,
                         mass=100.0, deposit_strength=1.0,
                         ticks=30000, gradient_coupling=1e-4, tag=''):
    """Measure force law: gamma gradient magnitude vs distance."""
    print("=" * 70)
    print("FORCE LAW MEASUREMENT")
    print("=" * 70)

    print("\n  PART 1: Direct gamma gradient vs distance")
    print("  " + "-" * 50)

    field = ContinuousGammaField(n_nodes, L=L, k_target=k_target, G=G,
                                  body_ids=['A'])
    cx, cy, cz = L / 2, L / 2, L / 2
    node_a = field.nearest_node([cx, cy, cz])

    body_a = MacroBody('A', node_a, mass=mass, commit_mass=999999,
                       deposit_strength=deposit_strength)
    formation_ticks = 5000
    print(f"    Formation: {formation_ticks} ticks (mass={mass})...")
    for tick in range(formation_ticks):
        body_a.advance(field, tick)
        field.spread()

    total_deposited = mass * deposit_strength * formation_ticks
    print(f"    Total gamma deposited: {total_deposited:.0f}")
    print(f"    Field total: {field.total_gamma():.0f}")

    # Probe gradient at various distances along +X
    # Start probes well beyond r_connect to avoid near-field artifacts
    r_min_probe = 2.5 * field.r_connect
    r_max_probe = L / 2 - 2
    if r_max_probe > r_min_probe:
        separations = np.linspace(r_min_probe, r_max_probe, 8).tolist()
    else:
        separations = [r_min_probe]
    gradient_data = []
    print(f"    r_connect={field.r_connect:.3f}, probing r=[{r_min_probe:.1f}, {r_max_probe:.1f}]")
    print(f"\n    {'r':>6s} {'|grad|':>12s} {'gamma_at_r':>12s}")
    for r in separations:
        if r >= L / 2 - 0.5:
            continue
        probe = field.nearest_node([cx + r, cy, cz])
        actual_r = field.euclidean_distance(node_a, probe)
        neighbors = field.neighbors[probe]

        grad = np.zeros(3)
        for nb in neighbors:
            ext = field.tagged['A'][nb]
            d = field.direction_vector(probe, nb)
            grad += d * ext
        gmag = float(np.linalg.norm(grad))

        gamma_at_r = field.tagged['A'][probe]
        gradient_data.append({
            'r': actual_r, 'gmag': gmag, 'gamma': gamma_at_r,
        })
        print(f"    {actual_r:6.2f} {gmag:12.4f} {gamma_at_r:12.4f}")

    valid = [d for d in gradient_data if d['gmag'] > 0 and d['r'] > 0]
    n_fit = None
    if len(valid) >= 3:
        log_r = np.log([d['r'] for d in valid])
        log_g = np.log([d['gmag'] for d in valid])
        coeffs = np.polyfit(log_r, log_g, 1)
        n_fit = -coeffs[0]
        k_fit = np.exp(coeffs[1])
        print(f"\n    Fit: |gradient| ~ 1/r^{n_fit:.3f}  (Newton = 2.0)")

    # ---- Part 2: Dynamic infall ----
    print("\n  PART 2: Dynamic infall (trajectory-based)")
    print("  " + "-" * 50)

    test_seps = [2.0, 3.0, 4.0, 5.0]
    commit_mass_b = 5
    infall_data = []

    for sep in test_seps:
        if sep >= L / 2 - 1:
            continue
        print(f"\n    --- r0 = {sep:.1f} ---")
        field2 = ContinuousGammaField(n_nodes, L=L, k_target=k_target, G=G,
                                       body_ids=['A', 'B'])
        node_a2 = field2.nearest_node([cx, cy, cz])
        node_b2 = field2.nearest_node([cx + sep, cy, cz])

        body_a2 = MacroBody('A', node_a2, mass=mass, commit_mass=999999,
                            deposit_strength=deposit_strength)
        print(f"      Formation: {formation_ticks} ticks (A only)...")
        for tick in range(formation_ticks):
            body_a2.advance(field2, tick)
            field2.spread()

        body_b2 = MacroBody('B', node_b2, mass=mass * 0.01,
                            commit_mass=commit_mass_b,
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
                if d < field2.mean_edge_length:
                    break

        if len(distances) >= 4:
            dists_arr = np.array([d[1] for d in distances])
            dt_hop = float(commit_mass_b)
            velocities = np.diff(dists_arr) / dt_hop

            if len(velocities) >= 3:
                accels = np.diff(velocities) / dt_hop
                n_early = min(5, len(accels))
                avg_accel = np.mean(accels[:n_early])
                avg_vel = np.mean(velocities[:n_early])
                print(f"      Hops: {len(distances)}, "
                      f"d: {distances[0][1]:.2f} -> {distances[-1][1]:.2f}")
                print(f"      Early avg accel: {avg_accel:.8f}")
                infall_data.append({
                    'r': sep, 'accel': abs(avg_accel),
                    'velocity': avg_vel,
                    'final_d': distances[-1][1],
                    'n_hops': len(distances),
                })

    # Summary
    print("\n  === FORCE LAW SUMMARY ===")
    if gradient_data:
        print(f"\n  Direct gradient: n = {n_fit:.3f}" if n_fit else
              "\n  Direct gradient: insufficient data")
        verdict = ('PASS' if n_fit and abs(n_fit - 2.0) < 0.3
                   else 'PARTIAL' if n_fit and abs(n_fit - 2.0) < 0.5
                   else 'FAIL')
        print(f"  Verdict: {verdict}")

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

def experiment_kepler(n_nodes=8000, L=15.0, k_target=50, G=10.0,
                      mass=100.0, deposit_strength=1.0,
                      commit_mass=10, ticks=200000, tag=''):
    print("=" * 70)
    print("KEPLER'S THIRD LAW TEST")
    print("=" * 70)

    separations = [2.0, 3.0, 4.0]
    kepler_data = []

    for sep in separations:
        print(f"\n  --- Separation = {sep:.1f} ---")
        records = experiment_phase2(
            n_nodes=n_nodes, L=L, k_target=k_target, G=G,
            mass=mass, deposit_strength=deposit_strength,
            commit_mass=commit_mass, separation=sep, ticks=ticks,
            initial_momentum='perpendicular',
            tag=f'kepler_r{sep:.0f}')

        if records and len(records) > 20:
            dists = [r['d_AB'] for r in records]
            ticks_arr = [r['tick'] for r in records]

            mean_d = np.mean(dists)
            crossings = []
            for i in range(1, len(dists)):
                if (dists[i] - mean_d) * (dists[i-1] - mean_d) < 0:
                    crossings.append(ticks_arr[i])

            if len(crossings) >= 4:
                half_periods = [crossings[i+1] - crossings[i]
                                for i in range(len(crossings) - 1)]
                T = 2 * np.mean(half_periods)
                kepler_data.append({'r': sep, 'T': T, 'T2': T**2,
                                    'r3': sep**3})
                print(f"    Period ~ {T:.0f} ticks ({len(crossings)} crossings)")
            else:
                print(f"    Not enough oscillations ({len(crossings)} crossings)")

    if len(kepler_data) >= 2:
        print("\n  === Kepler Summary ===")
        print(f"  {'r':>6s} {'T':>10s} {'T^2':>14s} {'r^3':>10s} {'T^2/r^3':>10s}")
        for d in kepler_data:
            ratio = d['T2'] / d['r3'] if d['r3'] > 0 else 0
            print(f"  {d['r']:6.1f} {d['T']:10.0f} {d['T2']:14.0f} "
                  f"{d['r3']:10.1f} {ratio:10.2f}")
        ratios = [d['T2'] / d['r3'] for d in kepler_data if d['r3'] > 0]
        if ratios:
            cv = np.std(ratios) / np.mean(ratios) if np.mean(ratios) > 0 else 999
            print(f"\n  T^2/r^3 variation: CV = {cv:.3f} "
                  f"({'PASS' if cv < 0.1 else 'FAIL' if cv > 0.3 else 'PARTIAL'})")

    return kepler_data


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v11: Macro Bodies on Random Geometric Graph')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase1', action='store_true')
    parser.add_argument('--phase2', action='store_true')
    parser.add_argument('--phase3', action='store_true')
    parser.add_argument('--force-law', action='store_true')
    parser.add_argument('--kepler', action='store_true')

    parser.add_argument('--n-nodes', type=int, default=5000)
    parser.add_argument('--L', type=float, default=10.0,
                        help='Box side length (embedding units)')
    parser.add_argument('--k-target', type=int, default=50,
                        help='Target mean degree for RGG')
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--H', type=float, default=0.0)
    parser.add_argument('--mass', type=float, default=100.0)
    parser.add_argument('--deposit-strength', type=float, default=1.0)
    parser.add_argument('--commit-mass', type=int, default=10)
    parser.add_argument('--separation', type=float, default=2.5,
                        help='Initial body separation (embedding units)')
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--initial-momentum',
                        choices=['none', 'perpendicular', 'tangential'],
                        default='none')
    parser.add_argument('--tag', type=str, default='')
    parser.add_argument('--gradient-coupling', type=float, default=1e-4)
    parser.add_argument('--formation-ticks', type=int, default=0)

    args = parser.parse_args()

    if args.verify:
        run_verification()
    if args.phase1:
        experiment_phase1(n_nodes=args.n_nodes, L=args.L,
                          k_target=args.k_target, G=args.G,
                          mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass, ticks=args.ticks)
    if args.phase2:
        experiment_phase2(n_nodes=args.n_nodes, L=args.L,
                          k_target=args.k_target, G=args.G, H=args.H,
                          mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          initial_momentum=args.initial_momentum,
                          gradient_coupling=args.gradient_coupling,
                          tag=args.tag,
                          formation_ticks=args.formation_ticks)
    if args.phase3:
        experiment_phase3(n_nodes=args.n_nodes, L=args.L,
                          k_target=args.k_target, G=args.G, H=args.H,
                          mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          initial_momentum=args.initial_momentum,
                          gradient_coupling=args.gradient_coupling,
                          tag=args.tag)
    if args.force_law:
        experiment_force_law(n_nodes=max(args.n_nodes, 8000), L=max(args.L, 15.0),
                             k_target=args.k_target, G=args.G,
                             mass=args.mass,
                             deposit_strength=args.deposit_strength,
                             ticks=args.ticks,
                             gradient_coupling=args.gradient_coupling,
                             tag=args.tag)
    if args.kepler:
        experiment_kepler(n_nodes=max(args.n_nodes, 8000), L=max(args.L, 15.0),
                          k_target=args.k_target, G=args.G,
                          mass=args.mass,
                          deposit_strength=args.deposit_strength,
                          commit_mass=args.commit_mass,
                          ticks=args.ticks, tag=args.tag)

    if not any([args.verify, args.phase1, args.phase2, args.phase3,
                args.force_law, args.kepler]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
