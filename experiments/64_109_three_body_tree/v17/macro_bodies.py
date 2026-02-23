"""v17: Mass Radiation Stabilizes Orbits.

v16 proved: growth asymmetry on a real graph produces bound oscillation (77
comoving reversals). But orbits decay from Hubble drag — expansion decays
comoving velocities as v ~ 1/a. The H=0 test confirmed the projection
mechanism is lossless (velocity perfectly preserved on a static graph).
All damping comes from expansion.

v17 adds mass radiation: a body deposits gamma, and that deposit IS mass loss.
As mass decreases, gravity weakens, the orbit widens. If mass loss rate matches
expansion rate, the orbit stabilizes: expansion shrinks comoving orbits while
mass loss widens them.

Physics change: one line — self.mass -= deposited in Entity.advance().
Mass decays exponentially: M(t) = M0 * (1 - deposit_rate)^t.

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --phase0 --n-nodes 10000 --ticks 10000
    python macro_bodies.py --phase1 --n-nodes 10000 --ticks 50000
    python macro_bodies.py --phase2 --n-nodes 10000 --ticks 50000

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
from scipy.spatial import KDTree
from scipy.sparse import lil_matrix, csr_matrix

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# RandomGeometricGraph — random 3D point cloud with k-NN connectivity
# ===========================================================================

class RandomGeometricGraph:
    """Random geometric graph with tagged gamma field and variable edge lengths.

    Replaces v15's ContinuousGammaField (cubic lattice) with a random 3D
    point cloud connected by k nearest neighbors.

    Edge rule: de/dt = H / (1 + alpha * (|gamma_A| + |gamma_B|))
    Each edge reads ONLY its own two endpoints. Local information only.
    """

    def __init__(self, n_nodes, k=6, alpha=None, G=1.0, H=0.0,
                 alpha_expand=1.0, seed=42, body_ids=None, radius=50.0):
        self.k = k
        self.G = G
        self.H = H
        self.alpha_expand = alpha_expand
        self.seed = seed
        self.radius = radius

        print(f"  Building random geometric graph: N={n_nodes}, k={k}, "
              f"radius={radius}, seed={seed}")
        t0 = time.time()

        self.n_nodes, self.positions = self._generate_points(n_nodes, radius, seed)
        self._build_graph(k)

        elapsed = time.time() - t0
        print(f"    Built in {elapsed:.1f}s: {self.n_nodes} nodes, "
              f"{self.n_edges} edges")

        # Speed of light
        self.alpha = alpha if alpha is not None else (1.0 / k)

        # Tagged fields
        self.body_ids = body_ids or []
        self.tagged = {
            bid: np.zeros(self.n_nodes, dtype=np.float64)
            for bid in self.body_ids
        }
        self.gamma = np.zeros(self.n_nodes, dtype=np.float64)

    def _generate_points(self, n_target, radius, seed):
        """Generate n_target points uniformly in a sphere via rejection sampling."""
        rng = np.random.default_rng(seed)
        points = []
        while len(points) < n_target:
            batch = rng.uniform(-radius, radius, size=(n_target * 2, 3))
            dists = np.linalg.norm(batch, axis=1)
            inside = batch[dists <= radius]
            points.append(inside)
            if sum(len(p) for p in points) >= n_target:
                break
        all_points = np.vstack(points)[:n_target]
        return n_target, all_points.astype(np.float64)

    def _build_graph(self, k):
        """Build k-NN graph with symmetrized edges."""
        tree = KDTree(self.positions)
        # Query k+1 because first result is the point itself
        distances, indices = tree.query(self.positions, k=k + 1)

        # Build edge set (symmetrized: if A->B exists, B->A must too)
        edge_set = set()
        for i in range(self.n_nodes):
            for j_idx in range(1, k + 1):  # skip self (index 0)
                j = indices[i, j_idx]
                a, b = min(i, j), max(i, j)
                edge_set.add((a, b))

        # Store edges as arrays
        edges = sorted(edge_set)
        self.n_edges = len(edges)
        self.edge_node_a = np.array([e[0] for e in edges], dtype=np.int64)
        self.edge_node_b = np.array([e[1] for e in edges], dtype=np.int64)

        # Edge lengths initialized to Euclidean distance
        pos_a = self.positions[self.edge_node_a]
        pos_b = self.positions[self.edge_node_b]
        self.edge_lengths = np.linalg.norm(pos_b - pos_a, axis=1).astype(np.float64)
        self.initial_mean_edge = float(np.mean(self.edge_lengths))
        self.last_growth = np.zeros(self.n_edges, dtype=np.float64)

        # Per-node neighbor list: node_neighbors[node] = [(nb_id, edge_idx), ...]
        self.node_neighbors = [[] for _ in range(self.n_nodes)]
        for edge_idx, (a, b) in enumerate(edges):
            self.node_neighbors[a].append((b, edge_idx))
            self.node_neighbors[b].append((a, edge_idx))

        # Sparse adjacency matrix for spread()
        A = lil_matrix((self.n_nodes, self.n_nodes), dtype=np.float64)
        for a, b in edges:
            A[a, b] = 1.0
            A[b, a] = 1.0
        self.A = csr_matrix(A)
        self.degrees = np.array(self.A.sum(axis=1)).flatten()
        self.degrees = np.maximum(self.degrees, 1.0)

        # Degree diagnostics
        actual_degrees = [len(nbs) for nbs in self.node_neighbors]
        print(f"    Degree: min={min(actual_degrees)}, max={max(actual_degrees)}, "
              f"mean={np.mean(actual_degrees):.1f}")
        print(f"    Edge length: min={np.min(self.edge_lengths):.2f}, "
              f"max={np.max(self.edge_lengths):.2f}, "
              f"mean={self.initial_mean_edge:.2f} (= hop threshold)")

    # --- Field operations (same algorithm as v15, different data structure) ---

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

    def expand_edges(self):
        """Grow all edges using two-endpoint rule.

        de/dt = H / (1 + alpha * (|gamma_A| + |gamma_B|))

        One vectorized operation over all edges. No loops, no symmetry
        enforcement needed (each edge stored once).
        """
        if self.H <= 0:
            self.last_growth[:] = 0.0
            return

        abs_gamma = np.abs(self.gamma)
        gamma_sum = abs_gamma[self.edge_node_a] + abs_gamma[self.edge_node_b]
        growth = self.H / (1.0 + self.alpha_expand * gamma_sum)
        self.last_growth = growth
        self.edge_lengths += growth

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
        self.tagged[bid][center_node] += mass
        self.sync_total()
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def move_gamma(self, bid, old_node, new_node):
        """Transfer tagged gamma from old_node to new_node inline."""
        amount = self.tagged[bid][old_node]
        if amount > 0:
            self.tagged[bid][old_node] = 0.0
            self.tagged[bid][new_node] += amount
            self.gamma[old_node] -= amount
            self.gamma[new_node] += amount

    # --- Geometry helpers ---

    def nearest_node(self, pos_3d):
        """Find the graph node closest to a 3D position."""
        dists = np.linalg.norm(self.positions - pos_3d, axis=1)
        return int(np.argmin(dists))

    def direction_vector(self, from_node, to_node):
        """Unit vector from from_node to to_node in 3D embedding."""
        delta = self.positions[to_node] - self.positions[from_node]
        norm = np.linalg.norm(delta)
        if norm < 1e-15:
            return np.zeros(3)
        return delta / norm

    def connector_direction(self, node, nb):
        """Unit vector from node toward neighbor nb."""
        return self.direction_vector(node, nb)

    def euclidean_distance(self, node_a, node_b):
        """Euclidean distance between two nodes in the 3D embedding."""
        return float(np.linalg.norm(
            self.positions[node_a] - self.positions[node_b]))

    def coords_of(self, node):
        """Return 3D position of a node."""
        return tuple(self.positions[node])

    def edge_profile_at(self, center_node, max_r=None, n_bins=20):
        """Compute average edge length in radial bins from center_node."""
        if max_r is None:
            max_r = self.radius
        center_pos = self.positions[center_node]

        # Compute distance from center for all nodes
        node_dists = np.linalg.norm(self.positions - center_pos, axis=1)

        # Bin edges by average distance of their endpoints from center
        bin_width = max_r / n_bins
        profile = {}

        for edge_idx in range(self.n_edges):
            a, b = self.edge_node_a[edge_idx], self.edge_node_b[edge_idx]
            avg_dist = 0.5 * (node_dists[a] + node_dists[b])
            bin_idx = int(avg_dist / bin_width)
            if bin_idx >= n_bins:
                continue
            r_center = (bin_idx + 0.5) * bin_width
            if r_center not in profile:
                profile[r_center] = []
            profile[r_center].append(self.edge_lengths[edge_idx])

        return {r: np.mean(vals) for r, vals in sorted(profile.items())}

    def gamma_profile_at(self, center_node, max_r=None, n_bins=20):
        """Compute average gamma in radial bins from center_node."""
        if max_r is None:
            max_r = self.radius
        center_pos = self.positions[center_node]
        node_dists = np.linalg.norm(self.positions - center_pos, axis=1)
        bin_width = max_r / n_bins
        profile = {}

        for node_id in range(self.n_nodes):
            r = node_dists[node_id]
            bin_idx = int(r / bin_width)
            if bin_idx >= n_bins:
                continue
            r_center = (bin_idx + 0.5) * bin_width
            if r_center not in profile:
                profile[r_center] = []
            profile[r_center].append(self.gamma[node_id])

        return {r: np.mean(vals) for r, vals in sorted(profile.items())}

    def avg_edge_length_at(self, node):
        """Average edge length of all edges connected to node."""
        nbs = self.node_neighbors[node]
        if not nbs:
            return 0.0
        return float(np.mean([self.edge_lengths[eidx] for _, eidx in nbs]))

    def growth_at_node(self, node):
        """Return list of (nb_id, edge_idx, last_growth) for all connectors."""
        return [(nb, eidx, self.last_growth[eidx])
                for nb, eidx in self.node_neighbors[node]]

    def growth_at_node_external(self, node, exclude_bid):
        """Compute growth for each connector using EXTERNAL gamma only.

        Excludes the body's own tagged gamma from the force calculation.
        This prevents self-gravity: a body shouldn't feel its own field.
        The edge expansion (expand_edges) still uses total gamma — this only
        affects the force computation in advance().

        In the binary case, each body's own gamma creates a huge symmetric
        suppression at its own position that drowns out the asymmetric signal
        from the other body. Excluding self-gamma fixes this.
        """
        ext_gamma = np.abs(self.gamma - self.tagged[exclude_bid])
        result = []
        for nb, eidx in self.node_neighbors[node]:
            g_a = ext_gamma[node]
            g_b = ext_gamma[nb]
            growth = self.H / (1.0 + self.alpha_expand * (g_a + g_b))
            result.append((nb, eidx, growth))
        return result


# ===========================================================================
# Entity — passive entity pushed by growth asymmetry (per-connector nudge)
# ===========================================================================

class Entity:
    """Entity on a random geometric graph with mass radiation.

    v17: mass radiation. Each tick, the entity deposits gamma proportional to
    its mass (deposited = mass * deposit_rate). That deposit IS mass loss:
    self.mass -= deposited. Mass decays exponentially: M(t) = M0*(1-deposit_rate)^t.
    When mass reaches 0, the body becomes "dark" — no gravity, still has velocity.

    Velocity/displacement split from v16: velocity is a persistent 3D vector
    changed only by acceleration (growth asymmetry = gravity). Displacement
    is per-connector: each tick, velocity is projected onto the best-aligned
    connector and added to that connector's accumulator. When any connector's
    accumulator reaches hop_threshold (initial mean edge length), the entity
    hops to that neighbor.
    """

    def __init__(self, bid, node, mass=1.0, deposit_rate=1.0, inertia=1.0,
                 stationary=False, radiate_mass=True):
        self.bid = bid
        self.node = node
        self.mass = mass
        self.deposit_rate = deposit_rate
        self.inertia = inertia
        self.stationary = stationary
        self.radiate_mass = radiate_mass

        self.velocity = np.zeros(3, dtype=np.float64)  # persistent 3D velocity
        self.disp = {}              # per-connector displacement accumulator
        self.hops = 0

        # History
        self.trajectory = []
        self.pos_history = []

    def advance(self, graph, tick=None):
        """Advance one tick.

        1. Deposit gamma
        2. Acceleration from growth asymmetry -> update velocity
        3. Project velocity onto best-aligned connector -> accumulate disp
        4. Hop when any connector's disp >= hop_threshold
        5. Transfer residual displacement to new node's best connector
        """
        deposited = self.mass * self.deposit_rate
        graph.deposit(self.node, self.bid, deposited)
        if self.radiate_mass:
            self.mass = max(self.mass - deposited, 0.0)

        if self.stationary:
            return False

        # --- Acceleration: growth asymmetry -> 3D force -> velocity ---
        # Use external gamma only (exclude self) to prevent self-gravity.
        if graph.H > 0:
            connectors = graph.growth_at_node_external(self.node, self.bid)
            if connectors:
                growths = [g for _, _, g in connectors]
                mean_growth = sum(growths) / len(growths)

                accel = np.zeros(3)
                for nb, eidx, growth in connectors:
                    push = (mean_growth - growth) / self.inertia
                    direction = graph.connector_direction(self.node, nb)
                    accel += direction * push

                self.velocity += accel

        # --- Velocity -> displacement: best-aligned connector ---
        conn_list = graph.node_neighbors[self.node]
        if not conn_list:
            return False

        best_nb = None
        best_proj = 0.0
        for nb, eidx in conn_list:
            direction = graph.connector_direction(self.node, nb)
            v_proj = float(np.dot(self.velocity, direction))
            if v_proj > best_proj:
                best_proj = v_proj
                best_nb = nb

        if best_nb is not None:
            self.disp[best_nb] = self.disp.get(best_nb, 0.0) + best_proj

        # --- Hop when displacement >= hop_threshold ---
        hop_threshold = graph.initial_mean_edge
        moved = False
        max_hops_per_tick = 10
        hops_this_tick = 0
        while hops_this_tick < max_hops_per_tick:
            best_nb = None
            best_disp = 0.0
            for nb, val in self.disp.items():
                if val > best_disp:
                    best_disp = val
                    best_nb = nb
            if best_disp < hop_threshold:
                break

            self.disp[best_nb] -= hop_threshold
            old_node = self.node
            graph.move_gamma(self.bid, old_node, best_nb)
            self._transfer_displacement(graph, old_node, best_nb)
            self.node = best_nb
            self.hops += 1
            hops_this_tick += 1
            moved = True

        return moved

    def _transfer_displacement(self, graph, old_node, new_node):
        """Transfer per-connector displacement to new node's best connector.

        Convert residual displacement to a 3D vector, project onto the
        best-aligned connector at the new node. Single-best projection
        prevents scatter across all connectors.
        """
        disp_3d = np.zeros(3)
        for nb, val in self.disp.items():
            if abs(val) < 1e-15:
                continue
            direction = graph.connector_direction(old_node, nb)
            disp_3d += direction * val

        self.disp = {}
        if np.linalg.norm(disp_3d) < 1e-15:
            return

        new_connectors = graph.node_neighbors[new_node]
        if not new_connectors:
            return

        best_nb = None
        best_proj = 0.0
        for nb, eidx in new_connectors:
            direction = graph.connector_direction(new_node, nb)
            proj = float(np.dot(disp_3d, direction))
            if proj > best_proj:
                best_proj = proj
                best_nb = nb

        if best_nb is not None and best_proj > 1e-15:
            self.disp[best_nb] = best_proj

    def set_velocity(self, velocity_3d):
        """Set initial velocity directly as a 3D vector."""
        self.velocity = np.asarray(velocity_3d, dtype=np.float64).copy()

    def get_momentum_3d(self, graph):
        """Return velocity (momentum = mass * velocity, but mass=1 for now)."""
        return self.velocity.copy()

    def record(self, tick, graph):
        self.trajectory.append((tick, self.node))
        pos = graph.coords_of(self.node)
        self.pos_history.append((tick, pos[0], pos[1], pos[2]))


# ===========================================================================
# Utilities
# ===========================================================================

def compute_angular_momentum(bodies, graph):
    """Compute angular momentum using reconstructed 3D momentum."""
    if not bodies:
        return {}

    # Center of mass
    total_mass = sum(b.mass for b in bodies)
    if total_mass < 1e-15:
        return {b.bid: 0.0 for b in bodies}
    com = np.zeros(3)
    for b in bodies:
        com += graph.positions[b.node] * b.mass
    com /= total_mass

    result = {}
    for body in bodies:
        r = graph.positions[body.node] - com
        v = body.get_momentum_3d(graph)
        # L_z = m * (r_x * v_y - r_y * v_x)
        result[body.bid] = body.mass * (r[0] * v[1] - r[1] * v[0])
    return result


# ===========================================================================
# Plotting
# ===========================================================================

def plot_distances(records, pairs, title, filename, init_dists=None):
    fig, ax = plt.subplots(figsize=(14, 5))
    ticks = [r['tick'] for r in records]
    for pair in pairs:
        key = f'd_{pair}'
        if key in records[0]:
            ax.plot(ticks, [r[key] for r in records], linewidth=1, label=pair)
            if init_dists and pair in init_dists:
                ax.axhline(y=init_dists[pair], color='gray', linestyle='--',
                           alpha=0.3)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Distance (Euclidean)')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_trajectories_xy(bodies, graph, filename, title="Trajectories (XY)"):
    fig, ax = plt.subplots(figsize=(8, 8))
    for body in bodies:
        if body.pos_history:
            xs = [c[1] for c in body.pos_history]
            ys = [c[2] for c in body.pos_history]
        else:
            continue
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


def plot_edge_profile(profile, filename, title="Edge Length vs Distance"):
    fig, ax = plt.subplots(figsize=(10, 6))
    rs = sorted(profile.keys())
    es = [profile[r] for r in rs]
    ax.plot(rs, es, 'bo-', markersize=6, label='Measured')
    ax.set_xlabel('Distance from mass (Euclidean)')
    ax.set_ylabel('Average edge length')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_summary_dashboard(bodies, graph, records, ang_records, filename,
                           title="Summary"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. Trajectory XY
    ax = axes[0, 0]
    for body in bodies:
        if body.pos_history:
            xs = [c[1] for c in body.pos_history]
            ys = [c[2] for c in body.pos_history]
            ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
            ax.plot(xs[0], ys[0], 'o', markersize=8)
    ax.set_aspect('equal')
    ax.set_title('Trajectories (XY)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    # 2. Distances
    ax = axes[0, 1]
    if records:
        ticks_arr = [r['tick'] for r in records]
        for key in records[0]:
            if key.startswith('d_'):
                ax.plot(ticks_arr, [r[key] for r in records], linewidth=1,
                        label=key[2:])
        ax.set_xlabel('Tick')
        ax.set_ylabel('Distance (Euclidean)')
        ax.set_title('Pairwise Distances')
        ax.legend()
        ax.grid(True, alpha=0.3)

    # 3. Angular momentum
    ax = axes[1, 0]
    if ang_records:
        ax.plot([r[0] for r in ang_records], [r[1] for r in ang_records],
                'r-', linewidth=1)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Total L_z')
        ax.set_title('Angular Momentum')
        ax.grid(True, alpha=0.3)

    # 4. Edge profile
    ax = axes[1, 1]
    if bodies:
        center = bodies[0].node
        profile = graph.edge_profile_at(center)
        rs = sorted(profile.keys())
        es = [profile[r] for r in rs]
        ax.plot(rs, es, 'go-', markersize=4)
        ax.set_xlabel('Distance from body A (Euclidean)')
        ax.set_ylabel('Avg edge length')
        ax.set_title('Edge Length Profile')
        ax.grid(True, alpha=0.3)

    fig.suptitle(title, fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification():
    print("\n=== v17 VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # Test 1: Gamma conservation (1000 ticks)
    print("Test 1: Gamma conservation (1000 ticks)")
    f = RandomGeometricGraph(500, k=6, G=10.0, seed=1, body_ids=['A', 'B'])
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
    passed += ok; failed += (not ok)

    # Test 2: Peak retention with G > 0
    print("Test 2: Peak retention (G=10, 500 ticks)")
    f2 = RandomGeometricGraph(2000, k=6, G=10.0, seed=2, body_ids=['A'])
    center = f2.nearest_node(np.array([0.0, 0.0, 0.0]))
    f2.initialize_peak('A', center, 1000.0, smooth_ticks=10)
    for _ in range(500):
        f2.spread()
    peak_val = f2.tagged['A'][f2.tagged_peak_node('A')]
    mean_val = f2.tagged_total('A') / f2.n_nodes
    ratio = peak_val / max(mean_val, 1e-10)
    ok = ratio > 10
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean ratio = {ratio:.0f}")
    passed += ok; failed += (not ok)

    # Test 3: Self-subtraction
    print("Test 3: External gamma = total - own")
    f3 = RandomGeometricGraph(500, k=6, G=10.0, seed=3, body_ids=['A', 'B'])
    f3.tagged['A'][100] = 500.0
    f3.tagged['B'][200] = 300.0
    f3.sync_total()
    ok = (abs(f3.external_gamma(100, 'A') - 0.0) < 1e-10 and
          abs(f3.external_gamma(200, 'B') - 0.0) < 1e-10 and
          abs(f3.external_gamma(100, 'B') - 500.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}")
    passed += ok; failed += (not ok)

    # Test 4: Dispersal at G=0
    print("Test 4: Full dispersal at G=0 (2000 ticks)")
    f4 = RandomGeometricGraph(500, k=6, G=0.0, seed=4, body_ids=['A'])
    c4 = f4.n_nodes // 2
    f4.tagged['A'][c4] = 1000.0
    f4.sync_total()
    for _ in range(2000):
        f4.spread()
    peak_val = np.max(f4.tagged['A'])
    mean_val = np.mean(f4.tagged['A'])
    ratio = peak_val / max(mean_val, 1e-10)
    ok = ratio < 2.0
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean = {ratio:.3f} (want <2)")
    passed += ok; failed += (not ok)

    # Test 5: Edge expansion suppressed near mass
    print("Test 5: Edge expansion suppressed near mass")
    f5 = RandomGeometricGraph(2000, k=6, G=10.0, H=0.01, alpha_expand=1.0,
                               seed=5, body_ids=['A'])
    center5 = f5.nearest_node(np.array([0.0, 0.0, 0.0]))
    f5.initialize_peak('A', center5, 5000.0, smooth_ticks=50)
    for _ in range(2000):
        f5.spread()
        f5.expand_edges()
    # Compare edge lengths near mass vs far from mass
    center_pos = f5.positions[center5]
    node_dists = np.linalg.norm(f5.positions - center_pos, axis=1)
    near_edges = []
    far_edges = []
    for eidx in range(f5.n_edges):
        a, b = f5.edge_node_a[eidx], f5.edge_node_b[eidx]
        avg_r = 0.5 * (node_dists[a] + node_dists[b])
        if avg_r < f5.radius * 0.2:
            near_edges.append(f5.edge_lengths[eidx])
        elif avg_r > f5.radius * 0.7:
            far_edges.append(f5.edge_lengths[eidx])
    near_avg = np.mean(near_edges) if near_edges else 0
    far_avg = np.mean(far_edges) if far_edges else 0
    ok = far_avg > near_avg * 1.5
    print(f"  {'PASS' if ok else 'FAIL'}: near={near_avg:.3f}, far={far_avg:.3f} "
          f"(ratio={far_avg/max(near_avg,1e-10):.2f})")
    passed += ok; failed += (not ok)

    # Test 6: Edge growth stored correctly
    print("Test 6: last_growth populated by expand_edges")
    f6 = RandomGeometricGraph(500, k=6, G=10.0, H=0.01, alpha_expand=1.0,
                               seed=6, body_ids=['A'])
    f6.tagged['A'][f6.n_nodes // 2] = 1000.0
    f6.sync_total()
    f6.expand_edges()
    ok = (np.max(f6.last_growth) > 0 and
          np.min(f6.last_growth) > 0 and
          np.min(f6.last_growth) < np.max(f6.last_growth))
    print(f"  {'PASS' if ok else 'FAIL'}: growth range = "
          f"[{np.min(f6.last_growth):.6f}, {np.max(f6.last_growth):.6f}]")
    passed += ok; failed += (not ok)

    # Test 7: Nudge accumulation produces hops on random graph
    print("Test 7: Nudge accumulation produces hops from growth asymmetry")
    f7 = RandomGeometricGraph(2000, k=6, G=10.0, H=0.1, alpha_expand=1.0,
                               seed=7, body_ids=['A', 'B'], radius=20.0)
    center7 = f7.nearest_node(np.array([0.0, 0.0, 0.0]))
    # Place massive gamma source near center
    offset_pos = np.array([5.0, 0.0, 0.0])
    off_node = f7.nearest_node(offset_pos)
    f7.initialize_peak('B', off_node, 100000.0, smooth_ticks=50)
    # Run expansion to establish growth asymmetry
    for _ in range(1000):
        f7.spread()
        f7.expand_edges()
    # Place test body and let it accumulate nudge (low inertia for responsiveness)
    body7 = Entity('A', center7, mass=0.001, deposit_rate=0.001, inertia=0.1)
    start_node = body7.node
    for tick in range(10000):
        body7.advance(f7, tick)
        f7.spread()
        f7.expand_edges()
    ok = body7.hops > 0 and body7.node != start_node
    print(f"  {'PASS' if ok else 'FAIL'}: hops={body7.hops}, "
          f"moved from {start_node} to {body7.node}")
    passed += ok; failed += (not ok)

    # Test 8: Velocity persists through hops (inertial motion)
    print("Test 8: Velocity persists through hops")
    f8 = RandomGeometricGraph(2000, k=6, G=0.0, H=0.1, seed=8,
                               body_ids=['A', 'B'])
    center8 = f8.nearest_node(np.array([0.0, 0.0, 0.0]))
    # Place massive source to create growth asymmetry for hopping
    off8 = f8.nearest_node(np.array([5.0, 0.0, 0.0]))
    f8.initialize_peak('B', off8, 100000.0, smooth_ticks=50)
    for _ in range(500):
        f8.spread()
        f8.expand_edges()
    body8 = Entity('A', center8, mass=0.001, deposit_rate=0.0, inertia=0.01)
    body8.set_velocity(np.array([0.0, 5.0, 0.0]))
    initial_vel = body8.velocity.copy()
    # Run until a hop happens
    for tick in range(1000):
        body8.advance(f8, tick)
        f8.spread()
        f8.expand_edges()
        if body8.hops > 0:
            break
    # Velocity should be close to initial (only modified by acceleration)
    post_vel = body8.velocity.copy()
    # The y-component should be preserved (acceleration is mostly radial/x)
    ok = body8.hops > 0 and abs(post_vel[1] - initial_vel[1]) < 2.0
    print(f"  {'PASS' if ok else 'FAIL'}: hops={body8.hops}, "
          f"v_pre=[{initial_vel[0]:+.2f},{initial_vel[1]:+.2f},{initial_vel[2]:+.2f}], "
          f"v_post=[{post_vel[0]:+.2f},{post_vel[1]:+.2f},{post_vel[2]:+.2f}]")
    passed += ok; failed += (not ok)

    # Test 9: move_gamma conserves gamma
    print("Test 9: move_gamma conserves gamma")
    f9 = RandomGeometricGraph(500, k=6, G=10.0, seed=9, body_ids=['A'])
    node_a = 50
    node_b = 51
    f9.tagged['A'][node_a] = 100.0
    f9.sync_total()
    total_before = f9.total_gamma()
    tagged_before = f9.tagged_total('A')
    f9.move_gamma('A', node_a, node_b)
    total_after = f9.total_gamma()
    tagged_after = f9.tagged_total('A')
    ok = (abs(total_after - total_before) < 1e-10 and
          abs(tagged_after - tagged_before) < 1e-10 and
          abs(f9.tagged['A'][node_a]) < 1e-10 and
          abs(f9.tagged['A'][node_b] - 100.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}: total {total_before:.1f}->{total_after:.1f}, "
          f"tagged {tagged_before:.1f}->{tagged_after:.1f}")
    passed += ok; failed += (not ok)

    print(f"\n=== RESULTS: {passed}/{passed + failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 0: Edge Expansion Verification
# ===========================================================================

def experiment_phase0(n_nodes=10000, k=6, G=10.0, H=0.01, alpha_expand=1.0,
                      mass=1000.0, deposit_strength=1.0, ticks=10000,
                      formation_ticks=5000, seed=42, tag='', radius=50.0):
    print("=" * 70)
    print("PHASE 0: Edge Expansion Verification (Random Graph)")
    print("=" * 70)

    graph = RandomGeometricGraph(n_nodes, k=k, G=G, H=H,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=['A'],
                                  radius=radius)
    center = graph.nearest_node(np.array([0.0, 0.0, 0.0]))

    # Formation: establish gamma well (no expansion)
    print(f"\n  Formation: {formation_ticks} ticks (deposit + spread, no expansion)")
    saved_H = graph.H
    graph.H = 0.0
    deposit_rate = deposit_strength * mass
    star = Entity('A', center, mass=mass, deposit_rate=deposit_rate,
                  inertia=1.0, stationary=True)
    for tick in range(formation_ticks):
        star.advance(graph, tick)
        graph.spread()
    graph.H = saved_H
    print(f"  Gamma total: {graph.total_gamma():.0f}")
    print(f"  Gamma at center: {graph.gamma[center]:.1f}")

    # Snapshot gamma profile
    gamma_profile = graph.gamma_profile_at(center)

    # Expansion phase
    print(f"\n  Expansion: {ticks} ticks (H={H}, alpha_expand={alpha_expand})")
    profiles = {}
    snapshot_ticks = [ticks // 4, ticks // 2, ticks]
    t0 = time.time()
    for tick in range(ticks):
        star.advance(graph, formation_ticks + tick)
        graph.spread()
        graph.expand_edges()

        if (tick + 1) in snapshot_ticks:
            profile = graph.edge_profile_at(center)
            profiles[tick + 1] = profile
            near_e = graph.avg_edge_length_at(center)
            far_node = graph.nearest_node(
                np.array([graph.radius * 0.8, 0.0, 0.0]))
            far_e = graph.avg_edge_length_at(far_node)
            elapsed = time.time() - t0
            print(f"    Tick {tick+1:6d}: e_near={near_e:.4f}, e_far={far_e:.4f}, "
                  f"ratio={far_e/max(near_e,1e-10):.2f} ({elapsed:.1f}s)")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for t, profile in sorted(profiles.items()):
        rs = sorted(profile.keys())
        es = [profile[r] for r in rs]
        ax1.plot(rs, es, 'o-', markersize=4, label=f't={t}')
    ax1.set_xlabel('Distance from mass (Euclidean)')
    ax1.set_ylabel('Average edge length')
    ax1.set_title('Edge Length Profile')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    rs_g = sorted(gamma_profile.keys())
    gs = [gamma_profile[r] for r in rs_g]
    ax2.semilogy(rs_g, gs, 'ro-', markersize=4)
    ax2.set_xlabel('Distance from mass (Euclidean)')
    ax2.set_ylabel('Average gamma (log)')
    ax2.set_title('Gamma Field Profile')
    ax2.grid(True, alpha=0.3)

    suffix = f"_{tag}" if tag else ""
    fig.suptitle(f'Phase 0: Edge Expansion (N={n_nodes}, k={k}, mass={mass}, '
                 f'H={H})', fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'phase0_edge_expansion{suffix}.png', dpi=150)
    plt.close(fig)
    print(f"\n  Saved: {RESULTS_DIR / f'phase0_edge_expansion{suffix}.png'}")

    return profiles


# ===========================================================================
# Phase 1: Star + Planet Orbit — THE Test
# ===========================================================================

def experiment_phase1(n_nodes=10000, k=6, G=0.0, H=0.1, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=1.0,
                      deposit_strength=1.0, formation_deposit=1.0,
                      separation=10.0,
                      ticks=50000, formation_ticks=10000, seed=42, tag='',
                      tangential_momentum=0.34, inertia=1.0, radius=50.0,
                      radiate_mass=True):
    print("=" * 70)
    print("PHASE 1: Star + Planet Orbit (Random Graph, One Stupid Rule)")
    print("  G=0 (free diffusion), continuous deposit, expanding edges")
    print("  Orbit in COMOVING coordinates; physical outward spiral = expansion")
    print("=" * 70)

    # Build graph with H=0 initially (no expansion during formation)
    graph = RandomGeometricGraph(n_nodes, k=k, G=G, H=0.0,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=['star', 'planet'],
                                  radius=radius)

    # Place star at center, planet at separation along x
    center_pos = np.array([0.0, 0.0, 0.0])
    planet_pos = np.array([separation, 0.0, 0.0])
    node_star = graph.nearest_node(center_pos)
    node_planet = graph.nearest_node(planet_pos)

    actual_sep = graph.euclidean_distance(node_star, node_planet)
    e0_mean = np.mean(graph.edge_lengths)
    print(f"\n  Graph: N={n_nodes}, k={k}, mean_edge={e0_mean:.2f}")
    print(f"  Star: mass={star_mass}, node={node_star}")
    print(f"  Planet: mass={planet_mass}, node={node_planet}")
    print(f"  Separation: {actual_sep:.2f} (requested {separation})")
    print(f"  H={H}, alpha_expand={alpha_expand}, G={G}")
    print(f"  formation_deposit={formation_deposit}, deposit_strength={deposit_strength}")
    print(f"  radiate_mass={radiate_mass}, inertia={inertia}")
    print(f"  tangential_momentum={tangential_momentum}")

    # Formation: deposit + spread only (NO expansion — keep edges at initial length)
    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks (deposit + spread, NO expansion)")
        ft0 = time.time()
        for ft in range(formation_ticks):
            graph.deposit(node_star, 'star', formation_deposit)
            graph.spread()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

    # Enable expansion for dynamics
    graph.H = H

    # Edge diagnostics
    planet_e = graph.avg_edge_length_at(node_planet)
    star_e = graph.avg_edge_length_at(node_star)
    print(f"  Edge profile: e_star={star_e:.4f}, e_planet={planet_e:.4f}")
    print(f"  Gamma: star={graph.gamma[node_star]:.1f}, "
          f"planet={graph.gamma[node_planet]:.3f}")

    bodies = [
        Entity('star', node_star, mass=star_mass,
               deposit_rate=deposit_strength,
               inertia=inertia, stationary=True,
               radiate_mass=radiate_mass),
        Entity('planet', node_planet, mass=planet_mass,
               deposit_rate=0.0,
               inertia=inertia, radiate_mass=radiate_mass),
    ]

    # Planet gets initial tangential velocity (y direction)
    bodies[1].set_velocity(np.array([0.0, tangential_momentum, 0.0]))
    init_vel = bodies[1].velocity
    print(f"  Planet initial velocity: [{init_vel[0]:.3f}, "
          f"{init_vel[1]:.3f}, {init_vel[2]:.3f}]")

    init_dist = graph.euclidean_distance(bodies[0].node, bodies[1].node)

    # Run
    diag_interval = max(ticks // 500, 1)
    print_interval = max(ticks // 10, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        graph.spread()
        graph.expand_edges()
        for body in bodies:
            body.advance(graph, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, graph)

        if (tick + 1) % diag_interval == 0:
            d = graph.euclidean_distance(bodies[0].node, bodies[1].node)
            a_scale = np.mean(graph.edge_lengths) / e0_mean
            d_comov = d / a_scale
            records.append({
                'tick': tick + 1, 'd_AB': d,
                'd_comov': d_comov, 'a_scale': a_scale,
                'mass_star': bodies[0].mass, 'mass_planet': bodies[1].mass,
                'vStar': bodies[0].velocity.copy(),
                'vPlanet': bodies[1].velocity.copy(),
            })

            L = compute_angular_momentum(bodies, graph)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % print_interval == 0:
                mom = bodies[1].get_momentum_3d(graph)
                print(f"    Tick {tick+1:7d}: d={d:.1f} d_c={d_comov:.2f} "
                      f"a={a_scale:.1f} "
                      f"mS={bodies[0].mass:.1f} mP={bodies[1].mass:.1f} "
                      f"L={L_total:+.2f} "
                      f"|v|={np.linalg.norm(mom):.3f}(z={mom[2]:+.3f}) "
                      f"hops={bodies[1].hops} ({elapsed:.1f}s)")

    final_d = graph.euclidean_distance(bodies[0].node, bodies[1].node)
    final_a = np.mean(graph.edge_lengths) / e0_mean
    print(f"\n  Distance: {init_dist:.2f} -> {final_d:.2f} "
          f"(comoving: {init_dist:.2f} -> {final_d/final_a:.2f})")
    print(f"  Mass: star={star_mass} -> {bodies[0].mass:.2f}, "
          f"planet={planet_mass} -> {bodies[1].mass:.2f}")
    print(f"  Hops: star={bodies[0].hops}, planet={bodies[1].hops}")
    print(f"  Scale factor: 1.00 -> {final_a:.2f}")
    final_mom = bodies[1].get_momentum_3d(graph)
    print(f"  Final velocity: [{final_mom[0]:.3f}, "
          f"{final_mom[1]:.3f}, {final_mom[2]:.3f}]")

    if records:
        dists = [r['d_AB'] for r in records]
        dists_c = [r['d_comov'] for r in records]
        print(f"  Physical range: [{min(dists):.2f}, {max(dists):.2f}]")
        print(f"  Comoving range: [{min(dists_c):.2f}, {max(dists_c):.2f}]")
        reversals_phys = sum(1 for i in range(2, len(dists))
                             if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        reversals_comov = sum(1 for i in range(2, len(dists_c))
                              if (dists_c[i] - dists_c[i-1]) *
                                 (dists_c[i-1] - dists_c[i-2]) < 0)
        print(f"  Reversals: physical={reversals_phys}, comoving={reversals_comov}")

    suffix = f"_{tag}" if tag else ""

    # Plot: physical AND comoving distances + mass + velocity
    if records:
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 14))
        ticks_arr = [r['tick'] for r in records]
        ax1.plot(ticks_arr, [r['d_AB'] for r in records], 'b-', linewidth=1,
                 label='Physical distance')
        ax1.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.3)
        ax1.set_xlabel('Tick')
        ax1.set_ylabel('Distance (Euclidean)')
        ax1.set_title('Physical Distance (expanding space)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(ticks_arr, [r['d_comov'] for r in records], 'r-', linewidth=1,
                 label='Comoving distance')
        ax2.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.3,
                     label='Initial separation')
        ax2.set_xlabel('Tick')
        ax2.set_ylabel('Distance (comoving)')
        ax2.set_title('Comoving Distance (orbit!)')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.plot(ticks_arr, [r['mass_star'] for r in records], 'g-', linewidth=1,
                 label='Star mass')
        ax3.plot(ticks_arr, [r['mass_planet'] for r in records], 'm-', linewidth=1,
                 label='Planet mass')
        ax3.set_xlabel('Tick')
        ax3.set_ylabel('Mass')
        ax3.set_title('Mass Decay (radiation)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        ax4.plot(ticks_arr, [np.linalg.norm(r['vPlanet']) for r in records],
                 'r-', linewidth=1, label='|v_planet|')
        ax4.plot(ticks_arr, [r['vPlanet'][2] for r in records],
                 'r--', linewidth=0.5, alpha=0.5, label='v_planet_z')
        ax4.set_xlabel('Tick')
        ax4.set_ylabel('Velocity')
        ax4.set_title('Planet Velocity (solid=|v|, dashed=v_z)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        fig.suptitle(f'Phase 1: Star-Planet (sep={separation}, v={tangential_momentum}, '
                     f'H={H})', fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase1_distance{suffix}.png', dpi=150)
        plt.close(fig)

    # Trajectory plots: XY and XZ, physical and comoving
    if any(b.pos_history for b in bodies):
        fig, axes = plt.subplots(2, 2, figsize=(14, 14))

        # XY physical
        ax = axes[0, 0]
        for body in bodies:
            if body.pos_history:
                xs = [c[1] for c in body.pos_history]
                ys = [c[2] for c in body.pos_history]
                ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
                ax.plot(xs[0], ys[0], 'o', markersize=10)
                ax.plot(xs[-1], ys[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Physical XY')
        ax.set_xlabel('X'); ax.set_ylabel('Y')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XZ physical
        ax = axes[0, 1]
        for body in bodies:
            if body.pos_history:
                xs = [c[1] for c in body.pos_history]
                zs = [c[3] for c in body.pos_history]
                ax.plot(xs, zs, '-', linewidth=0.8, alpha=0.7, label=body.bid)
                ax.plot(xs[0], zs[0], 'o', markersize=10)
                ax.plot(xs[-1], zs[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Physical XZ')
        ax.set_xlabel('X'); ax.set_ylabel('Z')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XY comoving
        ax = axes[1, 0]
        for body in bodies:
            if body.pos_history:
                xs_c, ys_c = [], []
                for i, (t, x, y, z) in enumerate(body.pos_history):
                    a_t = 1.0
                    for r in records:
                        if r['tick'] >= t:
                            a_t = r['a_scale']
                            break
                    xs_c.append(x / a_t)
                    ys_c.append(y / a_t)
                ax.plot(xs_c, ys_c, '-', linewidth=0.8, alpha=0.7,
                        label=body.bid)
                ax.plot(xs_c[0], ys_c[0], 'o', markersize=10)
                ax.plot(xs_c[-1], ys_c[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Comoving XY')
        ax.set_xlabel('X (comov)'); ax.set_ylabel('Y (comov)')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XZ comoving
        ax = axes[1, 1]
        for body in bodies:
            if body.pos_history:
                xs_c, zs_c = [], []
                for i, (t, x, y, z) in enumerate(body.pos_history):
                    a_t = 1.0
                    for r in records:
                        if r['tick'] >= t:
                            a_t = r['a_scale']
                            break
                    xs_c.append(x / a_t)
                    zs_c.append(z / a_t)
                ax.plot(xs_c, zs_c, '-', linewidth=0.8, alpha=0.7,
                        label=body.bid)
                ax.plot(xs_c[0], zs_c[0], 'o', markersize=10)
                ax.plot(xs_c[-1], zs_c[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Comoving XZ')
        ax.set_xlabel('X (comov)'); ax.set_ylabel('Z (comov)')
        ax.legend(); ax.grid(True, alpha=0.3)

        fig.suptitle(f'Phase 1: Trajectories', fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase1_trajectory{suffix}.png', dpi=150)
        plt.close(fig)

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase1_Lz{suffix}.png')

    # Summary dashboard with comoving
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    ax = axes[0, 0]
    for body in bodies:
        if body.pos_history:
            xs_c, ys_c = [], []
            for i, (t, x, y, z) in enumerate(body.pos_history):
                a_t = 1.0
                for r in records:
                    if r['tick'] >= t:
                        a_t = r['a_scale']
                        break
                xs_c.append(x / a_t)
                ys_c.append(y / a_t)
            ax.plot(xs_c, ys_c, '-', linewidth=0.8, alpha=0.7, label=body.bid)
            ax.plot(xs_c[0], ys_c[0], 'o', markersize=8)
    ax.set_aspect('equal')
    ax.set_title('Comoving Trajectories (XY)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    if records:
        ticks_arr = [r['tick'] for r in records]
        ax.plot(ticks_arr, [r['d_comov'] for r in records], 'r-', linewidth=1,
                label='Comoving')
        ax.plot(ticks_arr, [r['d_AB'] for r in records], 'b-', linewidth=0.5,
                alpha=0.3, label='Physical')
        ax.set_xlabel('Tick')
        ax.set_ylabel('Distance')
        ax.set_title('Distance (red=comoving, blue=physical)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    if ang_records:
        ax.plot([r[0] for r in ang_records], [r[1] for r in ang_records],
                'r-', linewidth=1)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Total L_z')
        ax.set_title('Angular Momentum')
        ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    if records:
        ax.plot(ticks_arr, [r['a_scale'] for r in records], 'g-', linewidth=1)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Scale factor a(t)')
        ax.set_title('Expansion (mean edge / initial)')
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Phase 1: Star-Planet (sep={separation}, v={tangential_momentum}, '
                 f'H={H})', fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'phase1_summary{suffix}.png', dpi=150)
    plt.close(fig)

    print(f"\n  Saved plots to {RESULTS_DIR}/")
    return records


# ===========================================================================
# Phase 2: Equal Mass Binary
# ===========================================================================

def experiment_phase2(n_nodes=10000, k=12, G=0.0, H=0.1, alpha_expand=1.0,
                      mass=100.0, deposit_strength=1.0, formation_deposit=1.0,
                      separation=10.0, ticks=20000, formation_ticks=10000,
                      seed=42, tag='',
                      tangential_momentum=0.34, inertia=1.0, radius=50.0,
                      radiate_mass=True):
    print("=" * 70)
    print("PHASE 2: Equal Mass Binary (Random Graph)")
    print("  Two equal masses with opposing tangential velocity.")
    print("  G=0 (free diffusion), continuous deposit, expanding edges")
    print("=" * 70)

    # Build graph with H=0 initially (no expansion during formation)
    graph = RandomGeometricGraph(n_nodes, k=k, G=G, H=0.0,
                                  alpha_expand=alpha_expand,
                                  seed=seed, body_ids=['A', 'B'],
                                  radius=radius)

    # Place bodies symmetrically
    half_sep = separation / 2.0
    pos_a = np.array([-half_sep, 0.0, 0.0])
    pos_b = np.array([half_sep, 0.0, 0.0])
    node_a = graph.nearest_node(pos_a)
    node_b = graph.nearest_node(pos_b)

    actual_sep = graph.euclidean_distance(node_a, node_b)
    e0_mean = np.mean(graph.edge_lengths)
    print(f"\n  Graph: N={n_nodes}, k={k}, mean_edge={e0_mean:.2f}")
    print(f"  Mass A = Mass B = {mass}")
    print(f"  Separation: {actual_sep:.2f} (requested {separation})")
    print(f"  tangential_momentum: +/-{tangential_momentum}")
    print(f"  Inertia: {inertia}")
    print(f"  H={H}, alpha_expand={alpha_expand}, G={G}")
    print(f"  formation_deposit={formation_deposit}, deposit_strength={deposit_strength}")
    print(f"  radiate_mass={radiate_mass}")

    # Formation: deposit + spread only (NO expansion)
    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks (deposit + spread, NO expansion)")
        ft0 = time.time()
        for ft in range(formation_ticks):
            graph.deposit(node_a, 'A', formation_deposit)
            graph.deposit(node_b, 'B', formation_deposit)
            graph.spread()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

    # Enable expansion
    graph.H = H

    print(f"  Gamma: A_node={graph.gamma[node_a]:.1f}, B_node={graph.gamma[node_b]:.1f}")

    bodies = [
        Entity('A', node_a, mass=mass,
               deposit_rate=deposit_strength,
               inertia=inertia, radiate_mass=radiate_mass),
        Entity('B', node_b, mass=mass,
               deposit_rate=deposit_strength,
               inertia=inertia, radiate_mass=radiate_mass),
    ]

    # Opposite tangential velocity
    bodies[0].set_velocity(np.array([0.0, tangential_momentum, 0.0]))
    bodies[1].set_velocity(np.array([0.0, -tangential_momentum, 0.0]))

    init_dist = graph.euclidean_distance(bodies[0].node, bodies[1].node)

    # Run
    diag_interval = max(ticks // 500, 1)
    print_interval = max(ticks // 10, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        graph.spread()
        graph.expand_edges()
        for body in bodies:
            body.advance(graph, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, graph)

        if (tick + 1) % diag_interval == 0:
            d = graph.euclidean_distance(bodies[0].node, bodies[1].node)
            a_scale = np.mean(graph.edge_lengths) / e0_mean
            d_comov = d / a_scale
            records.append({
                'tick': tick + 1, 'd_AB': d,
                'd_comov': d_comov, 'a_scale': a_scale,
                'mass_A': bodies[0].mass, 'mass_B': bodies[1].mass,
                'vA': bodies[0].velocity.copy(),
                'vB': bodies[1].velocity.copy(),
            })

            L = compute_angular_momentum(bodies, graph)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % print_interval == 0:
                ma = bodies[0].get_momentum_3d(graph)
                mb = bodies[1].get_momentum_3d(graph)
                print(f"    Tick {tick+1:7d}: d={d:.1f} d_c={d_comov:.2f} "
                      f"a={a_scale:.1f} "
                      f"mA={bodies[0].mass:.1f} mB={bodies[1].mass:.1f} "
                      f"L={L_total:+.2f} "
                      f"|vA|={np.linalg.norm(ma):.3f}(z={ma[2]:+.3f}) "
                      f"|vB|={np.linalg.norm(mb):.3f}(z={mb[2]:+.3f}) "
                      f"hops={bodies[0].hops}+{bodies[1].hops} ({elapsed:.1f}s)")

    final_d = graph.euclidean_distance(bodies[0].node, bodies[1].node)
    final_a = np.mean(graph.edge_lengths) / e0_mean
    print(f"\n  Distance: {init_dist:.2f} -> {final_d:.2f} "
          f"(comoving: {init_dist:.2f} -> {final_d/final_a:.2f})")
    print(f"  Mass: {mass} -> A={bodies[0].mass:.2f}, B={bodies[1].mass:.2f}")
    print(f"  Hops: A={bodies[0].hops}, B={bodies[1].hops}")
    print(f"  Scale factor: 1.00 -> {final_a:.2f}")

    if records:
        dists = [r['d_AB'] for r in records]
        dists_c = [r['d_comov'] for r in records]
        print(f"  Physical range: [{min(dists):.2f}, {max(dists):.2f}]")
        print(f"  Comoving range: [{min(dists_c):.2f}, {max(dists_c):.2f}]")
        reversals_phys = sum(1 for i in range(2, len(dists))
                             if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        reversals_comov = sum(1 for i in range(2, len(dists_c))
                              if (dists_c[i] - dists_c[i-1]) *
                                 (dists_c[i-1] - dists_c[i-2]) < 0)
        print(f"  Reversals: physical={reversals_phys}, comoving={reversals_comov}")

    suffix = f"_{tag}" if tag else ""

    # Plot: physical AND comoving distances + mass + velocity
    if records:
        fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(14, 14))
        ticks_arr = [r['tick'] for r in records]
        ax1.plot(ticks_arr, [r['d_AB'] for r in records], 'b-', linewidth=1,
                 label='Physical distance')
        ax1.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.3)
        ax1.set_xlabel('Tick')
        ax1.set_ylabel('Distance (Euclidean)')
        ax1.set_title('Physical Distance (expanding space)')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(ticks_arr, [r['d_comov'] for r in records], 'r-', linewidth=1,
                 label='Comoving distance')
        ax2.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.3,
                     label='Initial separation')
        ax2.set_xlabel('Tick')
        ax2.set_ylabel('Distance (comoving)')
        ax2.set_title('Comoving Distance')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        ax3.plot(ticks_arr, [r['mass_A'] for r in records], 'g-', linewidth=1,
                 label='Mass A')
        ax3.plot(ticks_arr, [r['mass_B'] for r in records], 'm-', linewidth=1,
                 label='Mass B')
        ax3.set_xlabel('Tick')
        ax3.set_ylabel('Mass')
        ax3.set_title('Mass Decay (radiation)')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        ax4.plot(ticks_arr, [np.linalg.norm(r['vA']) for r in records],
                 'b-', linewidth=1, label='|vA|')
        ax4.plot(ticks_arr, [np.linalg.norm(r['vB']) for r in records],
                 'r-', linewidth=1, label='|vB|')
        ax4.plot(ticks_arr, [r['vA'][2] for r in records],
                 'b--', linewidth=0.5, alpha=0.5, label='vA_z')
        ax4.plot(ticks_arr, [r['vB'][2] for r in records],
                 'r--', linewidth=0.5, alpha=0.5, label='vB_z')
        ax4.set_xlabel('Tick')
        ax4.set_ylabel('Velocity')
        ax4.set_title('Velocity (solid=|v|, dashed=v_z)')
        ax4.legend()
        ax4.grid(True, alpha=0.3)

        fig.suptitle(f'Phase 2: Binary (m={mass}, sep={separation}, '
                     f'v=+/-{tangential_momentum}, H={H})', fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase2_distance{suffix}.png', dpi=150)
        plt.close(fig)

    # Trajectory plots: XY and XZ, physical and comoving
    if any(b.pos_history for b in bodies):
        fig, axes = plt.subplots(2, 2, figsize=(14, 14))

        # XY physical
        ax = axes[0, 0]
        for body in bodies:
            if body.pos_history:
                xs = [c[1] for c in body.pos_history]
                ys = [c[2] for c in body.pos_history]
                ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
                ax.plot(xs[0], ys[0], 'o', markersize=10)
                ax.plot(xs[-1], ys[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Physical XY')
        ax.set_xlabel('X'); ax.set_ylabel('Y')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XZ physical
        ax = axes[0, 1]
        for body in bodies:
            if body.pos_history:
                xs = [c[1] for c in body.pos_history]
                zs = [c[3] for c in body.pos_history]
                ax.plot(xs, zs, '-', linewidth=0.8, alpha=0.7, label=body.bid)
                ax.plot(xs[0], zs[0], 'o', markersize=10)
                ax.plot(xs[-1], zs[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Physical XZ')
        ax.set_xlabel('X'); ax.set_ylabel('Z')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XY comoving
        ax = axes[1, 0]
        for body in bodies:
            if body.pos_history:
                xs_c, ys_c = [], []
                for i, (t, x, y, z) in enumerate(body.pos_history):
                    a_t = 1.0
                    for r in records:
                        if r['tick'] >= t:
                            a_t = r['a_scale']
                            break
                    xs_c.append(x / a_t)
                    ys_c.append(y / a_t)
                ax.plot(xs_c, ys_c, '-', linewidth=0.8, alpha=0.7,
                        label=body.bid)
                ax.plot(xs_c[0], ys_c[0], 'o', markersize=10)
                ax.plot(xs_c[-1], ys_c[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Comoving XY')
        ax.set_xlabel('X (comov)'); ax.set_ylabel('Y (comov)')
        ax.legend(); ax.grid(True, alpha=0.3)

        # XZ comoving
        ax = axes[1, 1]
        for body in bodies:
            if body.pos_history:
                xs_c, zs_c = [], []
                for i, (t, x, y, z) in enumerate(body.pos_history):
                    a_t = 1.0
                    for r in records:
                        if r['tick'] >= t:
                            a_t = r['a_scale']
                            break
                    xs_c.append(x / a_t)
                    zs_c.append(z / a_t)
                ax.plot(xs_c, zs_c, '-', linewidth=0.8, alpha=0.7,
                        label=body.bid)
                ax.plot(xs_c[0], zs_c[0], 'o', markersize=10)
                ax.plot(xs_c[-1], zs_c[-1], 's', markersize=8)
        ax.set_aspect('equal')
        ax.set_title('Comoving XZ')
        ax.set_xlabel('X (comov)'); ax.set_ylabel('Z (comov)')
        ax.legend(); ax.grid(True, alpha=0.3)

        fig.suptitle(f'Phase 2: Binary Trajectories', fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase2_trajectory{suffix}.png', dpi=150)
        plt.close(fig)

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase2_Lz{suffix}.png')

    # Summary dashboard
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    ax = axes[0, 0]
    for body in bodies:
        if body.pos_history:
            xs_c, ys_c = [], []
            for i, (t, x, y, z) in enumerate(body.pos_history):
                a_t = 1.0
                for r in records:
                    if r['tick'] >= t:
                        a_t = r['a_scale']
                        break
                xs_c.append(x / a_t)
                ys_c.append(y / a_t)
            ax.plot(xs_c, ys_c, '-', linewidth=0.8, alpha=0.7, label=body.bid)
            ax.plot(xs_c[0], ys_c[0], 'o', markersize=8)
    ax.set_aspect('equal')
    ax.set_title('Comoving Trajectories (XY)')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[0, 1]
    if records:
        ticks_arr = [r['tick'] for r in records]
        ax.plot(ticks_arr, [r['d_comov'] for r in records], 'r-', linewidth=1,
                label='Comoving')
        ax.plot(ticks_arr, [r['d_AB'] for r in records], 'b-', linewidth=0.5,
                alpha=0.3, label='Physical')
        ax.set_xlabel('Tick')
        ax.set_ylabel('Distance')
        ax.set_title('Distance (red=comoving, blue=physical)')
        ax.legend()
        ax.grid(True, alpha=0.3)

    ax = axes[1, 0]
    if ang_records:
        ax.plot([r[0] for r in ang_records], [r[1] for r in ang_records],
                'r-', linewidth=1)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Total L_z')
        ax.set_title('Angular Momentum')
        ax.grid(True, alpha=0.3)

    ax = axes[1, 1]
    if records:
        ax.plot(ticks_arr, [r['a_scale'] for r in records], 'g-', linewidth=1)
        ax.set_xlabel('Tick')
        ax.set_ylabel('Scale factor a(t)')
        ax.set_title('Expansion (mean edge / initial)')
        ax.grid(True, alpha=0.3)

    fig.suptitle(f'Phase 2: Equal Mass Binary (m={mass}, sep={separation})',
                 fontsize=14, fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'phase2_summary{suffix}.png', dpi=150)
    plt.close(fig)

    print(f"\n  Saved plots to {RESULTS_DIR}/")
    return records


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v17: Mass Radiation Stabilizes Orbits')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase0', action='store_true',
                        help='Edge expansion verification')
    parser.add_argument('--phase1', action='store_true',
                        help='Star + planet orbit test')
    parser.add_argument('--phase2', action='store_true',
                        help='Equal mass binary')

    # Graph parameters
    parser.add_argument('--n-nodes', type=int, default=10000,
                        help='Number of graph nodes (default 10000)')
    parser.add_argument('--k', type=int, default=12,
                        help='k nearest neighbors (default 12)')
    parser.add_argument('--seed', type=int, default=42,
                        help='Random seed (default 42)')
    parser.add_argument('--radius', type=float, default=50.0,
                        help='Sphere radius for graph nodes (default 50.0)')

    # Physics parameters
    parser.add_argument('--G', type=float, default=0.0,
                        help='Self-gravity (default 0.0 = free diffusion)')
    parser.add_argument('--H', type=float, default=0.1)
    parser.add_argument('--alpha-expand', type=float, default=1.0)
    parser.add_argument('--ticks', type=int, default=20000)
    parser.add_argument('--formation-ticks', type=int, default=10000)
    parser.add_argument('--deposit-strength', type=float, default=0.001,
                        help='Entity radiation rate (deposit_rate, default 0.001)')
    parser.add_argument('--formation-deposit', type=float, default=1.0,
                        help='Deposit per tick during formation phase (default 1.0)')
    parser.add_argument('--tag', type=str, default='')

    # Body parameters
    parser.add_argument('--star-mass', type=float, default=1000.0)
    parser.add_argument('--planet-mass', type=float, default=1.0)
    parser.add_argument('--separation', type=float, default=10.0,
                        help='Euclidean separation between bodies')
    parser.add_argument('--tangential-momentum', type=float, default=0.34,
                        help='Initial tangential velocity')
    parser.add_argument('--inertia', type=float, default=1.0)
    parser.add_argument('--binary-mass', type=float, default=100.0)
    parser.add_argument('--no-mass-loss', action='store_true',
                        help='Disable mass radiation (deposit gamma but keep mass constant)')

    args = parser.parse_args()

    if args.verify:
        run_verification()

    if args.phase0:
        experiment_phase0(n_nodes=args.n_nodes, k=args.k, G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          mass=args.star_mass,
                          deposit_strength=args.deposit_strength,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          seed=args.seed, tag=args.tag,
                          radius=args.radius)

    if args.phase1:
        experiment_phase1(n_nodes=args.n_nodes, k=args.k, G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          star_mass=args.star_mass,
                          planet_mass=args.planet_mass,
                          deposit_strength=args.deposit_strength,
                          formation_deposit=args.formation_deposit,
                          separation=args.separation,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          seed=args.seed, tag=args.tag,
                          tangential_momentum=args.tangential_momentum,
                          inertia=args.inertia,
                          radius=args.radius,
                          radiate_mass=not args.no_mass_loss)

    if args.phase2:
        experiment_phase2(n_nodes=args.n_nodes, k=args.k, G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          mass=args.binary_mass,
                          deposit_strength=args.deposit_strength,
                          formation_deposit=args.formation_deposit,
                          separation=args.separation,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          seed=args.seed, tag=args.tag,
                          tangential_momentum=args.tangential_momentum,
                          inertia=args.inertia,
                          radius=args.radius,
                          radiate_mass=not args.no_mass_loss)

    if not any([args.verify, args.phase0, args.phase1, args.phase2]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
