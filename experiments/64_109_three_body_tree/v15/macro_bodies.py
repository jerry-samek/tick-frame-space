"""v15: One Mechanism — Growth Asymmetry Nudge.

v14 proved cascade drift was the dominant binding mechanism. The edge profile
flattened to 1% variation but bodies stayed bound through growth rate asymmetry.

v15 strips to ONE mechanism: the nudge buffer. No internal_direction, no frame
rotation, no Bresenham, no commit cycle. Entity is passive — the graph pushes it.

    nudge_buffer += (growth_minus - growth_plus) / inertia   per axis
    when |component| >= 1  →  hop in that direction

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --phase0 --ticks 10000
    python macro_bodies.py --phase1 --ticks 50000
    python macro_bodies.py --phase2 --ticks 50000
    python macro_bodies.py --phase3 --ticks 200000
    python macro_bodies.py --force-law --ticks 30000

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

# Direction index mapping: 0=+x, 1=-x, 2=+y, 3=-y, 4=+z, 5=-z
DIR_VECTORS = np.array([
    [1, 0, 0], [-1, 0, 0],
    [0, 1, 0], [0, -1, 0],
    [0, 0, 1], [0, 0, -1],
], dtype=np.float64)

OPPOSITE_DIR = [1, 0, 3, 2, 5, 4]  # opposite direction index


# ===========================================================================
# ContinuousGammaField — deterministic float64 tagged field with edge lengths
# ===========================================================================

class ContinuousGammaField:
    """Deterministic self-gravitating gamma field on a 3D periodic lattice
    with variable edge lengths.

    v14 edge rule: de/dt = H / (1 + alpha * (gamma_A + gamma_B))
    Each edge reads ONLY its own two endpoints. Local information only.
    """

    def __init__(self, n_nodes, k=6, alpha=None, G=1.0, H=0.0,
                 alpha_expand=1.0, seed=42, body_ids=None):
        self.k = k
        self.G = G
        self.H = H
        self.alpha_expand = alpha_expand
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

        # Edge lengths: per-node per-direction, initialized to 1.0
        self.edge_lengths = np.ones((actual_n, 6), dtype=np.float64)

        # Last growth rates per edge (for local cascade drift)
        self.last_growth = np.zeros((actual_n, 6), dtype=np.float64)

        # Neighbor direction mapping: neighbor_dirs[node, dir] = neighbor_node_id
        self.neighbor_dirs = np.full((actual_n, 6), -1, dtype=np.int64)
        for node_id in range(actual_n):
            cx, cy, cz = self.node_coords[node_id]
            for nb in self.neighbors[node_id]:
                ncx, ncy, ncz = self.node_coords[nb]
                dx = (ncx - cx) % side
                dy = (ncy - cy) % side
                dz = (ncz - cz) % side
                if dx == side - 1: dx = -1
                if dy == side - 1: dy = -1
                if dz == side - 1: dz = -1
                if dx == 1 and dy == 0 and dz == 0:
                    d_idx = 0
                elif dx == -1 and dy == 0 and dz == 0:
                    d_idx = 1
                elif dx == 0 and dy == 1 and dz == 0:
                    d_idx = 2
                elif dx == 0 and dy == -1 and dz == 0:
                    d_idx = 3
                elif dx == 0 and dy == 0 and dz == 1:
                    d_idx = 4
                elif dx == 0 and dy == 0 and dz == -1:
                    d_idx = 5
                else:
                    continue
                self.neighbor_dirs[node_id, d_idx] = nb

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

    def expand_edges(self):
        """Grow all edges using TWO-ENDPOINT rule (v14).

        de/dt = H / (1 + alpha * (|gamma_A| + |gamma_B|))

        Each edge reads ONLY its own two endpoints' gamma.
        Shorter edges near mass (both endpoints have high gamma).
        Normal growth far from mass (low gamma at both endpoints).

        Stores per-edge growth in self.last_growth for nudge buffer.
        """
        if self.H <= 0:
            self.last_growth[:] = 0.0
            return

        abs_gamma = np.abs(self.gamma)

        for d in range(6):
            nbs = self.neighbor_dirs[:, d]
            gamma_sum = abs_gamma + abs_gamma[nbs]  # both endpoints
            growth = self.H / (1.0 + self.alpha_expand * gamma_sum)
            self.last_growth[:, d] = growth
            self.edge_lengths[:, d] += growth

        # Enforce symmetry: edge A->B must equal edge B->A
        for d_fwd in range(0, 6, 2):  # +x, +y, +z
            d_rev = d_fwd + 1           # -x, -y, -z
            fwd_nbs = self.neighbor_dirs[:, d_fwd]
            e_fwd = self.edge_lengths[:, d_fwd].copy()
            e_rev = self.edge_lengths[fwd_nbs, d_rev].copy()
            avg = 0.5 * (e_fwd + e_rev)
            self.edge_lengths[:, d_fwd] = avg
            self.edge_lengths[fwd_nbs, d_rev] = avg

    def neighbor_in_direction(self, node, axis, sign):
        """O(1) lookup: return neighbor node in given axis (+1/-1 sign)."""
        d_idx = axis * 2 + (0 if sign > 0 else 1)
        return int(self.neighbor_dirs[node, d_idx])

    def move_gamma(self, bid, old_node, new_node):
        """Transfer tagged gamma from old_node to new_node inline.

        Updates both self.tagged[bid] and self.gamma directly — no
        sync_total needed.
        """
        amount = self.tagged[bid][old_node]
        if amount > 0:
            self.tagged[bid][old_node] = 0.0
            self.tagged[bid][new_node] += amount
            self.gamma[old_node] -= amount
            self.gamma[new_node] += amount

    def gradient_weighted(self, node, exclude_bid):
        """Compute gamma gradient weighted by 1/edge_length."""
        gx, gy, gz = 0.0, 0.0, 0.0
        for d_idx in range(6):
            nb = self.neighbor_dirs[node, d_idx]
            if nb < 0:
                continue
            ext = self.gamma[nb] - self.tagged[exclude_bid][nb]
            e_len = self.edge_lengths[node, d_idx]
            weight = 1.0 / max(e_len, 1e-10)
            dx, dy, dz = DIR_VECTORS[d_idx]
            gx += dx * weight * ext
            gy += dy * weight * ext
            gz += dz * weight * ext
        gmag = math.sqrt(gx * gx + gy * gy + gz * gz)
        return gx, gy, gz, gmag

    def gradient_raw(self, node, exclude_bid):
        """Unweighted gradient (for comparison/diagnostics)."""
        gx, gy, gz = 0.0, 0.0, 0.0
        for d_idx in range(6):
            nb = self.neighbor_dirs[node, d_idx]
            if nb < 0:
                continue
            ext = self.gamma[nb] - self.tagged[exclude_bid][nb]
            dx, dy, dz = DIR_VECTORS[d_idx]
            gx += dx * ext
            gy += dy * ext
            gz += dz * ext
        gmag = math.sqrt(gx * gx + gy * gy + gz * gz)
        return gx, gy, gz, gmag

    def avg_edge_length(self, node):
        return float(np.mean(self.edge_lengths[node]))

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

    def direction_vector(self, from_node, to_node):
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
        ca = self.node_coords[node_a]
        cb = self.node_coords[node_b]
        s = self.side
        dx = abs(ca[0] - cb[0])
        dy = abs(ca[1] - cb[1])
        dz = abs(ca[2] - cb[2])
        dx = min(dx, s - dx)
        dy = min(dy, s - dy)
        dz = min(dz, s - dz)
        return math.sqrt(dx * dx + dy * dy + dz * dz)

    def physical_distance_approx(self, node_a, node_b):
        hop_d = self.hop_distance(node_a, node_b)
        avg_a = float(np.mean(self.edge_lengths[node_a]))
        avg_b = float(np.mean(self.edge_lengths[node_b]))
        return hop_d * 0.5 * (avg_a + avg_b)

    def place_at_coords(self, x, y, z):
        s = self.side
        return self.coord_to_node[(x % s, y % s, z % s)]

    def coords_of(self, node):
        return self.node_coords[node]

    def set_edges_schwarzschild(self, center_node, r_s=5.0):
        """Set edges analytically: e = 1 / (1 + r_s / max(r, 1)).
        For comparison with emergent metric. Not used in main experiments.
        """
        for node_id in range(self.n_nodes):
            r = self.hop_distance(center_node, node_id)
            r = max(r, 1)
            e = 1.0 / (1.0 + r_s / r)
            self.edge_lengths[node_id, :] = e
        for d_fwd in range(0, 6, 2):
            d_rev = d_fwd + 1
            fwd_nbs = self.neighbor_dirs[:, d_fwd]
            avg = 0.5 * (self.edge_lengths[:, d_fwd] + self.edge_lengths[fwd_nbs, d_rev])
            self.edge_lengths[:, d_fwd] = avg
            self.edge_lengths[fwd_nbs, d_rev] = avg
        e_min = float(np.min(self.edge_lengths))
        e_max = float(np.max(self.edge_lengths))
        print(f"  Schwarzschild edges (r_s={r_s}): e=[{e_min:.4f}, {e_max:.4f}], "
              f"ratio={e_max/max(e_min,1e-20):.1f}")

    def edge_profile_at(self, center_node, max_r=None):
        if max_r is None:
            max_r = self.side // 2 - 1
        profile = {}
        for node_id in range(self.n_nodes):
            r = self.hop_distance(center_node, node_id)
            if r > max_r:
                continue
            avg_e = float(np.mean(self.edge_lengths[node_id]))
            if r not in profile:
                profile[r] = []
            profile[r].append(avg_e)
        return {r: np.mean(vals) for r, vals in sorted(profile.items())}


# ===========================================================================
# MacroBody — passive entity pushed by growth asymmetry
# ===========================================================================

class MacroBody:
    """Astronomical body on the graph.

    v15: ONE buffer — nudge_buffer is both force accumulator AND momentum.

    Each tick:
      1. Deposit gamma at current node
      2. Read last_growth asymmetry per axis → accumulate in nudge_buffer / inertia
      3. When any component reaches +/-1 → hop in that direction
      4. After hop: local edge asymmetry rotates the nudge_buffer (geodesic tilt)

    The geometry curves the momentum. One buffer. One mechanism.
    """

    def __init__(self, bid, node, mass=1.0, deposit_rate=1.0, inertia=1.0):
        self.bid = bid
        self.node = node
        self.mass = mass
        self.deposit_rate = deposit_rate
        self.inertia = inertia

        self.nudge_buffer = np.array([0.0, 0.0, 0.0])
        self.hops = 0

        # History
        self.trajectory = []
        self.coord_history = []

    def advance(self, field, tick=None):
        """Advance one tick. The graph pushes the entity via growth asymmetry.

        1. Deposit gamma at current node
        2. Read last_growth asymmetry per axis, accumulate in nudge_buffer / inertia
        3. When any component reaches +/-1, hop in that direction
        4. After hop: rotate nudge_buffer by local edge asymmetry
        """
        field.deposit(self.node, self.bid, self.mass * self.deposit_rate)

        # Accumulate growth asymmetry into nudge buffer
        if field.H > 0:
            for ax in range(3):
                d_plus = ax * 2       # +x, +y, +z
                d_minus = ax * 2 + 1  # -x, -y, -z
                g_plus = field.last_growth[self.node, d_plus]
                g_minus = field.last_growth[self.node, d_minus]
                # More growth on one side → body nudged toward the other
                self.nudge_buffer[ax] += (g_minus - g_plus) / self.inertia

        # Hop when any component reaches +/-1
        moved = False
        abs_buf = np.abs(self.nudge_buffer)
        while np.max(abs_buf) >= 1.0:
            axis = int(np.argmax(abs_buf))
            sign = 1 if self.nudge_buffer[axis] >= 0 else -1
            self.nudge_buffer[axis] -= sign

            new_node = field.neighbor_in_direction(self.node, axis, sign)
            field.move_gamma(self.bid, self.node, new_node)
            self.node = new_node
            self.hops += 1
            moved = True

            # Geodesic tilt: local edge asymmetry deflects the nudge_buffer.
            # Shorter edges point toward mass. The geometry curves momentum.
            for ax in range(3):
                e_plus = field.edge_lengths[self.node, ax * 2]
                e_minus = field.edge_lengths[self.node, ax * 2 + 1]
                e_sum = e_plus + e_minus
                if e_sum > 0:
                    self.nudge_buffer[ax] += -(e_plus - e_minus) / e_sum

            abs_buf = np.abs(self.nudge_buffer)

        return moved

    def record(self, tick, field):
        self.trajectory.append((tick, self.node))
        c = field.coords_of(self.node)
        self.coord_history.append((tick, c[0], c[1], c[2]))


# ===========================================================================
# Utilities
# ===========================================================================

def unwrap_coords(coord_history, side):
    if len(coord_history) < 2:
        return coord_history
    result = [coord_history[0]]
    cumulative = [coord_history[0][1], coord_history[0][2], coord_history[0][3]]
    for i in range(1, len(coord_history)):
        tick = coord_history[i][0]
        for dim in range(3):
            raw = coord_history[i][dim + 1]
            prev = coord_history[i - 1][dim + 1]
            delta = raw - prev
            if delta > side // 2:
                delta -= side
            elif delta < -(side // 2):
                delta += side
            cumulative[dim] += delta
        result.append((tick, cumulative[0], cumulative[1], cumulative[2]))
    return result


def compute_angular_momentum(bodies, field):
    """Compute angular momentum using nudge_buffer as velocity proxy."""
    s = field.side
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

    total_mass = sum(b.mass for b in bodies)
    com_x = sum(p[0] * b.mass for p, b in zip(positions, bodies)) / total_mass
    com_y = sum(p[1] * b.mass for p, b in zip(positions, bodies)) / total_mass

    result = {}
    for body, pos in zip(bodies, positions):
        rx = pos[0] - com_x
        ry = pos[1] - com_y
        vx = float(body.nudge_buffer[0])
        vy = float(body.nudge_buffer[1])
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
        if key in records[0]:
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
    fig, ax = plt.subplots(figsize=(8, 8))
    s = field.side
    for body in bodies:
        if body.coord_history:
            unwrapped = unwrap_coords(body.coord_history, s)
            xs = [c[1] for c in unwrapped]
            ys = [c[2] for c in unwrapped]
        else:
            continue
        ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
        ax.plot(xs[0], ys[0], 'o', markersize=10)
        ax.plot(xs[-1], ys[-1], 's', markersize=8)
    ax.set_xlabel('X (hops)')
    ax.set_ylabel('Y (hops)')
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


def plot_force_law(force_data, filename, title_extra=''):
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
        ax1.set_title(f'Force Law{title_extra}: n = {n_fit:.3f} (Newton = 2.0)')
    ax1.set_xlabel('Distance (hops)')
    ax1.set_ylabel('|Gradient|')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    if all(a > 0 for a in accels):
        ax2.loglog(rs, accels, 'bo-', markersize=8, label='Measured')
        if n_fit is not None:
            ax2.loglog(r_fit, a_fit, 'r--', label=f'n = {n_fit:.2f}')
        ax2.set_xlabel('Distance (hops)')
        ax2.set_ylabel('|Gradient|')
        ax2.set_title('Log-Log')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_edge_profile(profile, filename, title="Edge Length vs Distance",
                      theory_func=None):
    fig, ax = plt.subplots(figsize=(10, 6))
    rs = sorted(profile.keys())
    es = [profile[r] for r in rs]
    ax.plot(rs, es, 'bo-', markersize=6, label='Measured')
    if theory_func:
        r_fine = np.linspace(max(1, min(rs)), max(rs), 200)
        e_theory = [theory_func(r) for r in r_fine]
        ax.plot(r_fine, e_theory, 'r--', label='Theory', alpha=0.7)
    ax.set_xlabel('Distance from mass (hops)')
    ax.set_ylabel('Average edge length')
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_summary_dashboard(bodies, field, records, ang_records, filename,
                           title="Summary"):
    fig, axes = plt.subplots(2, 2, figsize=(14, 12))

    # 1. Trajectory XY
    ax = axes[0, 0]
    s = field.side
    for body in bodies:
        if body.coord_history:
            unwrapped = unwrap_coords(body.coord_history, s)
            xs = [c[1] for c in unwrapped]
            ys = [c[2] for c in unwrapped]
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
        ax.set_ylabel('Distance (hops)')
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
        profile = field.edge_profile_at(center, max_r=min(30, field.side // 2 - 1))
        rs = sorted(profile.keys())
        es = [profile[r] for r in rs]
        ax.plot(rs, es, 'go-', markersize=4)
        ax.set_xlabel('Distance from body A (hops)')
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
    print("\n=== v15 MACRO BODIES VERIFICATION ===\n")
    passed = 0
    failed = 0

    # Test 1: Gamma conservation
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
    passed += ok; failed += (not ok)

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
    passed += ok; failed += (not ok)

    # Test 3: Self-subtraction
    print("Test 3: External gamma = total - own")
    f3 = ContinuousGammaField(1000, k=6, G=10.0, body_ids=['A', 'B'])
    f3.tagged['A'][100] = 500.0
    f3.tagged['B'][200] = 300.0
    f3.sync_total()
    ok = (abs(f3.external_gamma(100, 'A') - 0.0) < 1e-10 and
          abs(f3.external_gamma(200, 'B') - 0.0) < 1e-10 and
          abs(f3.external_gamma(100, 'B') - 500.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}")
    passed += ok; failed += (not ok)

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
    ok = ratio < 2.0
    print(f"  {'PASS' if ok else 'FAIL'}: peak/mean = {ratio:.3f} (want <2)")
    passed += ok; failed += (not ok)

    # Test 5: Two-endpoint edge expansion
    print("Test 5: Two-endpoint expansion suppressed near mass")
    f5 = ContinuousGammaField(8000, k=6, G=10.0, H=0.01, alpha_expand=1.0,
                               body_ids=['A'])
    center5 = f5.n_nodes // 2
    f5.initialize_peak('A', center5, 5000.0, smooth_ticks=50)
    for _ in range(2000):
        f5.spread()
        f5.expand_edges()
    near_edge = float(np.mean(f5.edge_lengths[center5]))
    far_node = f5.place_at_coords(0, 0, 0)
    far_edge = float(np.mean(f5.edge_lengths[far_node]))
    ok = far_edge > near_edge * 1.5
    print(f"  {'PASS' if ok else 'FAIL'}: near={near_edge:.3f}, far={far_edge:.3f} "
          f"(ratio={far_edge/near_edge:.2f})")
    passed += ok; failed += (not ok)

    # Test 6: Edge symmetry after expansion
    print("Test 6: Edge symmetry (A->B = B->A)")
    max_asym = 0.0
    for d_fwd in range(0, 6, 2):
        d_rev = d_fwd + 1
        for node_id in range(min(1000, f5.n_nodes)):
            nb = f5.neighbor_dirs[node_id, d_fwd]
            if nb >= 0:
                e1 = f5.edge_lengths[node_id, d_fwd]
                e2 = f5.edge_lengths[nb, d_rev]
                max_asym = max(max_asym, abs(e1 - e2))
    ok = max_asym < 1e-10
    print(f"  {'PASS' if ok else 'FAIL'}: max asymmetry = {max_asym:.2e}")
    passed += ok; failed += (not ok)

    # Test 7: last_growth stored correctly
    print("Test 7: last_growth populated by expand_edges")
    f7 = ContinuousGammaField(1000, k=6, G=10.0, H=0.01, alpha_expand=1.0,
                               body_ids=['A'])
    f7.tagged['A'][f7.n_nodes // 2] = 1000.0
    f7.sync_total()
    f7.expand_edges()
    ok = (np.max(f7.last_growth) > 0 and
          np.min(f7.last_growth) > 0 and
          np.min(f7.last_growth) < np.max(f7.last_growth))
    print(f"  {'PASS' if ok else 'FAIL'}: growth range = "
          f"[{np.min(f7.last_growth):.6f}, {np.max(f7.last_growth):.6f}]")
    passed += ok; failed += (not ok)

    # Test 8: Nudge accumulation produces hops from growth asymmetry
    print("Test 8: Nudge buffer accumulates and produces hops from growth asymmetry")
    f8 = ContinuousGammaField(8000, k=6, G=10.0, H=0.1, alpha_expand=1.0,
                               body_ids=['A', 'B'])
    center8 = f8.n_nodes // 2
    # Place a massive gamma source close to create strong asymmetry
    off_node = f8.place_at_coords(f8.side // 2 + 3, f8.side // 2, f8.side // 2)
    f8.initialize_peak('B', off_node, 100000.0, smooth_ticks=50)
    # Run expansion to establish growth asymmetry
    for _ in range(1000):
        f8.spread()
        f8.expand_edges()
    # Now place a test body at center and let it accumulate nudge
    body8 = MacroBody('A', center8, mass=0.001, deposit_rate=0.001, inertia=1.0)
    start_node = body8.node
    for tick in range(10000):
        body8.advance(f8, tick)
        f8.spread()
        f8.expand_edges()
    # Body should have hopped (growth asymmetry near massive source)
    ok = body8.hops > 0 and body8.node != start_node
    print(f"  {'PASS' if ok else 'FAIL'}: hops={body8.hops}, "
          f"nudge_buf={body8.nudge_buffer}")
    passed += ok; failed += (not ok)

    # Test 9: Nudge buffer preserves momentum with H=0
    print("Test 9: Nudge buffer preserves momentum with H=0 (no growth)")
    f9 = ContinuousGammaField(8000, k=6, G=0.0, H=0.0, body_ids=['A'])
    center9 = f9.n_nodes // 2
    body9 = MacroBody('A', center9, mass=0.001, deposit_rate=0.0, inertia=1.0)
    body9.nudge_buffer = np.array([0.5, 0.3, 0.0])
    initial_nudge = body9.nudge_buffer.copy()
    for tick in range(100):
        body9.advance(f9, tick)
    # With H=0, no growth → no nudge accumulation → buffer unchanged (no hops since < 1)
    ok = np.allclose(body9.nudge_buffer, initial_nudge)
    print(f"  {'PASS' if ok else 'FAIL'}: nudge preserved = {body9.nudge_buffer} "
          f"(initial = {initial_nudge})")
    passed += ok; failed += (not ok)

    # Test 10: move_gamma conserves gamma
    print("Test 10: move_gamma conserves gamma")
    f10 = ContinuousGammaField(1000, k=6, G=10.0, body_ids=['A'])
    node_a = 50
    node_b = 51
    f10.tagged['A'][node_a] = 100.0
    f10.sync_total()
    total_before = f10.total_gamma()
    tagged_before = f10.tagged_total('A')
    f10.move_gamma('A', node_a, node_b)
    total_after = f10.total_gamma()
    tagged_after = f10.tagged_total('A')
    ok = (abs(total_after - total_before) < 1e-10 and
          abs(tagged_after - tagged_before) < 1e-10 and
          abs(f10.tagged['A'][node_a]) < 1e-10 and
          abs(f10.tagged['A'][node_b] - 100.0) < 1e-10)
    print(f"  {'PASS' if ok else 'FAIL'}: total {total_before:.1f}->{total_after:.1f}, "
          f"tagged {tagged_before:.1f}->{tagged_after:.1f}")
    passed += ok; failed += (not ok)

    print(f"\n=== RESULTS: {passed}/{passed + failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 0: Edge Expansion Verification
# ===========================================================================

def experiment_phase0(side=20, G=10.0, H=0.01, alpha_expand=1.0,
                      mass=1000.0, deposit_strength=1.0, ticks=10000,
                      formation_ticks=5000):
    print("=" * 70)
    print("PHASE 0: Edge Expansion Verification (Two-Endpoint Rule)")
    print("=" * 70)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=['A'])
    center = field.place_at_coords(side // 2, side // 2, side // 2)

    # Formation: establish gamma well (no expansion)
    print(f"\n  Formation: {formation_ticks} ticks (deposit + spread, no expansion)")
    saved_H = field.H
    field.H = 0.0
    deposit_rate = deposit_strength * mass
    body = MacroBody('A', center, mass=mass, deposit_rate=deposit_rate,
                     inertia=1.0)
    for tick in range(formation_ticks):
        body.advance(field, tick)
        field.spread()
    field.H = saved_H
    print(f"  Gamma total: {field.total_gamma():.0f}")
    print(f"  Gamma at center: {field.gamma[center]:.1f}")

    # Snapshot gamma profile
    gamma_profile = {}
    max_r = min(side // 2 - 1, 30)
    for node_id in range(field.n_nodes):
        r = field.hop_distance(center, node_id)
        if r > max_r:
            continue
        if r not in gamma_profile:
            gamma_profile[r] = []
        gamma_profile[r].append(field.gamma[node_id])
    gamma_avg = {r: np.mean(vals) for r, vals in sorted(gamma_profile.items())}

    # Expansion phase
    print(f"\n  Expansion: {ticks} ticks (H={H}, alpha_expand={alpha_expand})")
    profiles = {}
    snapshot_ticks = [ticks // 4, ticks // 2, ticks]
    t0 = time.time()
    for tick in range(ticks):
        body.advance(field, formation_ticks + tick)
        field.spread()
        field.expand_edges()

        if (tick + 1) in snapshot_ticks:
            profile = field.edge_profile_at(center, max_r=max_r)
            profiles[tick + 1] = profile
            near_e = float(np.mean(field.edge_lengths[center]))
            far_node = field.place_at_coords(0, 0, 0)
            far_e = float(np.mean(field.edge_lengths[far_node]))
            elapsed = time.time() - t0
            print(f"    Tick {tick+1:6d}: e_near={near_e:.4f}, e_far={far_e:.4f}, "
                  f"ratio={far_e/max(near_e,1e-10):.2f} ({elapsed:.1f}s)")

    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for t, profile in sorted(profiles.items()):
        rs = sorted(profile.keys())
        es = [profile[r] for r in rs]
        ax1.plot(rs, es, 'o-', markersize=4, label=f't={t}')
    ax1.set_xlabel('Distance from mass (hops)')
    ax1.set_ylabel('Average edge length')
    ax1.set_title('Edge Length Profile (Two-Endpoint Rule)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    rs_g = sorted(gamma_avg.keys())
    gs = [gamma_avg[r] for r in rs_g]
    ax2.semilogy(rs_g, gs, 'ro-', markersize=4)
    ax2.set_xlabel('Distance from mass (hops)')
    ax2.set_ylabel('Average gamma (log)')
    ax2.set_title('Gamma Field Profile')
    ax2.grid(True, alpha=0.3)

    fig.suptitle(f'Phase 0: Two-Endpoint Expansion (side={side}, mass={mass}, '
                 f'H={H}, alpha={alpha_expand})', fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'phase0_edge_expansion.png', dpi=150)
    plt.close(fig)
    print(f"\n  Saved: {RESULTS_DIR / 'phase0_edge_expansion.png'}")

    return profiles


# ===========================================================================
# Phase 1: Two-Body with Emergent Metric
# ===========================================================================

def experiment_phase1(side=40, G=10.0, H=0.001, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=1.0,
                      deposit_strength=1.0, separation=10,
                      ticks=50000, formation_ticks=5000, tag='',
                      freeze_edges=False, r_s=0.0,
                      tangential_nudge=0.3, inertia=1.0):
    if separation >= side // 2:
        side = max(side, 3 * separation)
        print(f"  WARNING: Increased side to {side}")

    print("=" * 70)
    print("PHASE 1: Two-Body with Nudge Buffer (One Mechanism)")
    print("=" * 70)

    n = side ** 3
    body_ids = ['star', 'planet']
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=body_ids)

    cx, cy, cz = side // 2, side // 2, side // 2
    node_star = field.place_at_coords(cx, cy, cz)
    node_planet = field.place_at_coords(cx + separation, cy, cz)

    field.initialize_peak('star', node_star, star_mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('star', node_star, mass=star_mass,
                  deposit_rate=deposit_strength * star_mass,
                  inertia=inertia),
        MacroBody('planet', node_planet, mass=planet_mass,
                  deposit_rate=deposit_strength * planet_mass,
                  inertia=inertia),
    ]
    # Planet gets initial tangential nudge (momentum)
    bodies[1].nudge_buffer = np.array([0.0, tangential_nudge, 0.0])

    init_dist = field.hop_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Star: mass={star_mass}")
    print(f"  Planet: mass={planet_mass}, tangential_nudge={tangential_nudge}")
    print(f"  Inertia: {inertia}")
    print(f"  Separation: {init_dist} hops")
    print(f"  H={H}, alpha_expand={alpha_expand}, G={G}")

    # Formation: deposit + spread + gentle expansion (no advance)
    if formation_ticks > 0:
        saved_H = field.H
        field.H = min(field.H, 0.001)  # cap expansion to build edges gently
        print(f"  Formation: {formation_ticks} ticks (deposit + spread + expand H={field.H})")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_rate)
            field.spread()
            field.expand_edges()
        print(f"  Formation done in {time.time()-ft0:.1f}s")
        field.H = saved_H

    # Schwarzschild edges (for comparison tests only)
    if r_s > 0:
        field.set_edges_schwarzschild(bodies[0].node, r_s=r_s)
        field.H = 0.0

    # Freeze edges after formation if requested
    if freeze_edges:
        field.H = 0.0
        near_e = field.avg_edge_length(bodies[0].node)
        far_node = field.place_at_coords(0, 0, 0)
        far_e = field.avg_edge_length(far_node)
        print(f"  FROZEN edges: e_star={near_e:.3f}, e_far={far_e:.3f}, "
              f"ratio={far_e/max(near_e,1e-10):.2f}")

    # Edge profile diagnostic
    profile = field.edge_profile_at(bodies[0].node, max_r=min(25, side // 2 - 1))
    planet_e = field.avg_edge_length(bodies[1].node)
    star_e = field.avg_edge_length(bodies[0].node)
    print(f"  Edge profile: e_star={star_e:.4f}, e_planet={planet_e:.4f}")

    # Reduce star deposit during dynamics
    bodies[0].deposit_rate *= 0.001
    total_gamma_pre = field.total_gamma()
    print(f"  Pre-dynamics gamma: {total_gamma_pre:.0f}")

    # Run
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand_edges()
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
                'd_AB': d, 'd_AB_hop': d_hop,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                avg_e = field.avg_edge_length(bodies[0].node)
                nb = bodies[1].nudge_buffer
                print(f"    Tick {tick+1:7d}: d={d:.1f} (hop={d_hop}) "
                      f"e_star={avg_e:.3f} L={L_total:+.2f} "
                      f"nudge=[{nb[0]:+.3f},{nb[1]:+.3f},{nb[2]:+.3f}] "
                      f"({elapsed:.1f}s)")

    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {init_dist} -> {final_d:.1f}")
    print(f"  Hops: star={bodies[0].hops}, planet={bodies[1].hops}")
    print(f"  Final nudge_buffer planet: {bodies[1].nudge_buffer}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.1f}, {max(dists):.1f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['AB'],
                       f'Two-Body (v15): star={star_mass}, planet={planet_mass}',
                       RESULTS_DIR / f'phase1_distance{suffix}.png',
                       {'AB': init_dist})

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase1_trajectory{suffix}.png',
                             'Two-Body Trajectories (hops)')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase1_Lz{suffix}.png')

    plot_summary_dashboard(bodies, field, records, ang_records,
                           RESULTS_DIR / f'phase1_summary{suffix}.png',
                           f'Phase 1: Star-Planet (r={separation})')

    return records


# ===========================================================================
# Phase 2: Equal Mass Binary (THE ACID TEST)
# ===========================================================================

def experiment_phase2(side=60, G=1.0, H=0.001, alpha_expand=1.0,
                      mass=100.0, deposit_strength=1.0,
                      separation=15, ticks=50000, formation_ticks=10000,
                      tag='', freeze_edges=False,
                      tangential_nudge=0.3, inertia=1.0):
    if separation >= side // 2:
        side = max(side, 3 * separation)
        print(f"  WARNING: Increased side to {side}")

    print("=" * 70)
    print("PHASE 2: Equal Mass Binary (Acid Test) — Nudge Buffer Only")
    print("  Two equal masses. Neither is 'the star.'")
    print("  Do they orbit their common center of mass?")
    print("=" * 70)

    n = side ** 3
    body_ids = ['A', 'B']
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=body_ids)

    cx, cy, cz = side // 2, side // 2, side // 2
    node_a = field.place_at_coords(cx - separation // 2, cy, cz)
    node_b = field.place_at_coords(cx + separation // 2, cy, cz)

    # Both bodies contribute to gamma equally
    field.initialize_peak('A', node_a, mass * 50, smooth_ticks=30)
    field.initialize_peak('B', node_b, mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('A', node_a, mass=mass,
                  deposit_rate=deposit_strength * mass,
                  inertia=inertia),
        MacroBody('B', node_b, mass=mass,
                  deposit_rate=deposit_strength * mass,
                  inertia=inertia),
    ]
    # Opposite tangential nudges — should orbit center of mass
    bodies[0].nudge_buffer = np.array([0.0, tangential_nudge, 0.0])
    bodies[1].nudge_buffer = np.array([0.0, -tangential_nudge, 0.0])

    init_dist = field.hop_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Mass A = Mass B = {mass}")
    print(f"  Tangential nudge: +/-{tangential_nudge}")
    print(f"  Inertia: {inertia}")
    print(f"  Separation: {init_dist} hops")
    print(f"  H={H}, alpha_expand={alpha_expand}, G={G}")

    # Formation: deposit + spread + gentle expansion (no advance)
    if formation_ticks > 0:
        saved_H = field.H
        field.H = min(field.H, 0.001)  # cap expansion to build edges gently
        print(f"  Formation: {formation_ticks} ticks (deposit + spread + expand H={field.H})")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_rate)
            field.spread()
            field.expand_edges()
        print(f"  Formation done in {time.time()-ft0:.1f}s")
        field.H = saved_H

    if freeze_edges:
        field.H = 0.0
        print(f"  FROZEN edges")

    # Edge profile at midpoint
    mid_node = field.place_at_coords(cx, cy, cz)
    mid_e = field.avg_edge_length(mid_node)
    a_e = field.avg_edge_length(bodies[0].node)
    b_e = field.avg_edge_length(bodies[1].node)
    print(f"  Edges: A={a_e:.4f}, mid={mid_e:.4f}, B={b_e:.4f}")

    total_gamma_pre = field.total_gamma()
    print(f"  Pre-dynamics gamma: {total_gamma_pre:.0f}")

    # Run
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand_edges()
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
                'd_AB': d, 'd_AB_hop': d_hop,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                nba = bodies[0].nudge_buffer
                nbb = bodies[1].nudge_buffer
                print(f"    Tick {tick+1:7d}: d={d:.1f} (hop={d_hop}) "
                      f"L={L_total:+.2f} "
                      f"nbA=[{nba[0]:+.2f},{nba[1]:+.2f}] "
                      f"nbB=[{nbb[0]:+.2f},{nbb[1]:+.2f}] "
                      f"({elapsed:.1f}s)")

    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {init_dist} -> {final_d:.1f}")
    print(f"  Hops: A={bodies[0].hops}, B={bodies[1].hops}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.1f}, {max(dists):.1f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['AB'],
                       f'Equal Mass Binary (v15): m={mass}',
                       RESULTS_DIR / f'phase2_distance{suffix}.png',
                       {'AB': init_dist})

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase2_trajectory{suffix}.png',
                             'Equal Mass Binary Trajectories')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase2_Lz{suffix}.png')

    plot_summary_dashboard(bodies, field, records, ang_records,
                           RESULTS_DIR / f'phase2_summary{suffix}.png',
                           f'Phase 2: Equal Mass Binary (m={mass})')

    return records


# ===========================================================================
# Phase 3: Three-Body (Star + Planet + Moon)
# ===========================================================================

def experiment_phase3(side=80, G=10.0, H=0.001, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=10.0, moon_mass=0.1,
                      deposit_strength=1.0, planet_sep=15, moon_sep=3,
                      ticks=200000, formation_ticks=10000, tag='',
                      freeze_edges=False,
                      tangential_nudge=0.3, inertia=1.0):
    if planet_sep + moon_sep >= side // 2:
        side = max(side, 3 * (planet_sep + moon_sep))
        print(f"  WARNING: Increased side to {side}")

    print("=" * 70)
    print("PHASE 3: Three-Body (Star + Planet + Moon) — Nudge Buffer Only")
    print("=" * 70)

    n = side ** 3
    body_ids = ['star', 'planet', 'moon']
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=body_ids)

    cx, cy, cz = side // 2, side // 2, side // 2
    node_star = field.place_at_coords(cx, cy, cz)
    node_planet = field.place_at_coords(cx + planet_sep, cy, cz)
    node_moon = field.place_at_coords(cx + planet_sep + moon_sep, cy, cz)

    field.initialize_peak('star', node_star, star_mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('star', node_star, mass=star_mass,
                  deposit_rate=deposit_strength * star_mass,
                  inertia=inertia),
        MacroBody('planet', node_planet, mass=planet_mass,
                  deposit_rate=deposit_strength * planet_mass,
                  inertia=inertia),
        MacroBody('moon', node_moon, mass=moon_mass,
                  deposit_rate=deposit_strength * moon_mass,
                  inertia=inertia),
    ]

    # Planet and moon get tangential nudges (initial momentum)
    bodies[1].nudge_buffer = np.array([0.0, tangential_nudge, 0.0])
    bodies[2].nudge_buffer = np.array([0.0, tangential_nudge, 0.0])

    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Star: mass={star_mass}")
    print(f"  Planet: mass={planet_mass}, r={planet_sep}, "
          f"tangential_nudge={tangential_nudge}")
    print(f"  Moon: mass={moon_mass}, r_planet={moon_sep}, "
          f"tangential_nudge={tangential_nudge}")
    print(f"  Inertia: {inertia}")

    # Formation: deposit + spread + gentle expansion (no advance)
    if formation_ticks > 0:
        saved_H = field.H
        field.H = min(field.H, 0.001)  # cap expansion to build edges gently
        print(f"  Formation: {formation_ticks} ticks (deposit + spread + expand H={field.H})")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_rate)
            field.spread()
            field.expand_edges()
        print(f"  Formation done in {time.time()-ft0:.1f}s")
        field.H = saved_H

    if freeze_edges:
        field.H = 0.0

    # Run
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand_edges()
        for body in bodies:
            body.advance(field, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

        if (tick + 1) % diag_interval == 0:
            d_sp = field.euclidean_distance(bodies[0].node, bodies[1].node)
            d_sm = field.euclidean_distance(bodies[0].node, bodies[2].node)
            d_pm = field.euclidean_distance(bodies[1].node, bodies[2].node)
            records.append({
                'tick': tick + 1,
                'd_SP': d_sp, 'd_SM': d_sm, 'd_PM': d_pm,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                print(f"    Tick {tick+1:7d}: SP={d_sp:.1f} SM={d_sm:.1f} "
                      f"PM={d_pm:.1f} L={L_total:+.2f} ({elapsed:.1f}s)")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['SP', 'SM', 'PM'],
                       'Three-Body: Star-Planet-Moon (v15)',
                       RESULTS_DIR / f'phase3_distance{suffix}.png')

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase3_trajectory{suffix}.png',
                             'Three-Body Trajectories')

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase3_Lz{suffix}.png')

    plot_summary_dashboard(bodies, field, records, ang_records,
                           RESULTS_DIR / f'phase3_summary{suffix}.png',
                           'Phase 3: Star-Planet-Moon (v15)')

    return records


# ===========================================================================
# Force Law Measurement
# ===========================================================================

def experiment_force_law(side=50, G=10.0, H=0.001, alpha_expand=1.0,
                         mass=1000.0, deposit_strength=1.0,
                         ticks=30000, formation_ticks=5000, tag=''):
    print("=" * 70)
    print("FORCE LAW: Gradient vs Distance (weighted and raw)")
    print("=" * 70)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=['A'])
    cx, cy, cz = side // 2, side // 2, side // 2
    node_a = field.place_at_coords(cx, cy, cz)

    deposit_rate = deposit_strength * mass
    body_a = MacroBody('A', node_a, mass=mass, deposit_rate=deposit_rate,
                       inertia=1.0)

    # Formation with expansion
    print(f"\n  Formation: {formation_ticks} ticks (mass={mass}, H={H})...")
    for tick in range(formation_ticks):
        body_a.advance(field, tick)
        field.spread()
        field.expand_edges()
    print(f"  Gamma total: {field.total_gamma():.0f}")

    # Measure gradient at various distances
    separations = [3, 5, 8, 10, 12, 15, 18, 20, 25]
    gradient_data = []

    print(f"\n  {'r':>5s} {'|grad_w|':>12s} {'|grad_r|':>12s} "
          f"{'ratio':>8s} {'avg_e':>8s}")
    for r in separations:
        if r >= side // 2 - 2:
            continue
        probe = field.place_at_coords(cx + r, cy, cz)

        gw = field.gradient_weighted(probe, 'A')
        gr = field.gradient_raw(probe, 'A')
        avg_e = field.avg_edge_length(probe)
        ratio = gw[3] / max(gr[3], 1e-20)

        gradient_data.append({
            'r': r, 'gmag_weighted': gw[3], 'gmag_raw': gr[3],
            'ratio': ratio, 'avg_e': avg_e,
        })
        print(f"  {r:5d} {gw[3]:12.4f} {gr[3]:12.4f} "
              f"{ratio:8.3f} {avg_e:8.4f}")

    # Fit power laws
    for label, key in [('Weighted', 'gmag_weighted'), ('Raw', 'gmag_raw')]:
        valid = [d for d in gradient_data if d[key] > 0]
        if len(valid) >= 3:
            log_r = np.log([d['r'] for d in valid])
            log_g = np.log([d[key] for d in valid])
            coeffs = np.polyfit(log_r, log_g, 1)
            n_fit = -coeffs[0]
            print(f"\n  {label} fit: |gradient| ~ 1/r^{n_fit:.3f} "
                  f"(Newton = 2.0)")

    suffix = f"_{tag}" if tag else ""
    if gradient_data:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        rs = [d['r'] for d in gradient_data]
        gw = [d['gmag_weighted'] for d in gradient_data]
        gr = [d['gmag_raw'] for d in gradient_data]

        ax1.plot(rs, gw, 'bo-', label='Edge-weighted', markersize=8)
        ax1.plot(rs, gr, 'rs-', label='Raw', markersize=8)
        ax1.set_xlabel('Distance (hops)')
        ax1.set_ylabel('|Gradient|')
        ax1.set_title('Gradient Comparison')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        if all(g > 0 for g in gw) and all(g > 0 for g in gr):
            ax2.loglog(rs, gw, 'bo-', label='Weighted', markersize=8)
            ax2.loglog(rs, gr, 'rs-', label='Raw', markersize=8)
            ax2.set_xlabel('Distance (hops)')
            ax2.set_ylabel('|Gradient|')
            ax2.set_title('Log-Log')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

        fig.suptitle(f'Force Law: H={H}, alpha={alpha_expand}',
                     fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'force_law_comparison{suffix}.png', dpi=150)
        plt.close(fig)

        plot_force_law([{'r': d['r'], 'accel': d['gmag_weighted']}
                        for d in gradient_data if d['gmag_weighted'] > 0],
                       RESULTS_DIR / f'force_law_weighted{suffix}.png',
                       ' (edge-weighted)')
        plot_force_law([{'r': d['r'], 'accel': d['gmag_raw']}
                        for d in gradient_data if d['gmag_raw'] > 0],
                       RESULTS_DIR / f'force_law_raw{suffix}.png',
                       ' (raw)')

    return gradient_data


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v15: One Mechanism — Growth Asymmetry Nudge')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase0', action='store_true',
                        help='Edge expansion verification')
    parser.add_argument('--phase1', action='store_true',
                        help='Two-body with nudge buffer')
    parser.add_argument('--phase2', action='store_true',
                        help='Equal mass binary (acid test)')
    parser.add_argument('--phase3', action='store_true',
                        help='Three-body: star + planet + moon')
    parser.add_argument('--force-law', action='store_true',
                        help='Force law measurement')

    parser.add_argument('--side', type=int, default=40)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--H', type=float, default=0.001)
    parser.add_argument('--alpha-expand', type=float, default=1.0,
                        help='Expansion suppression strength')
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--formation-ticks', type=int, default=5000)
    parser.add_argument('--freeze-edges', action='store_true',
                        help='Freeze edge lengths after formation (H=0 during dynamics)')
    parser.add_argument('--r-s', type=float, default=0.0,
                        help='Schwarzschild radius for analytic edges (comparison). 0=disabled.')
    parser.add_argument('--deposit-strength', type=float, default=1.0)
    parser.add_argument('--tag', type=str, default='')

    # Body parameters
    parser.add_argument('--star-mass', type=float, default=1000.0)
    parser.add_argument('--planet-mass', type=float, default=1.0)
    parser.add_argument('--moon-mass', type=float, default=0.1)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--moon-distance', type=int, default=3)

    # v15-specific
    parser.add_argument('--inertia', type=float, default=1.0,
                        help='Inertia for all bodies (default 1.0)')
    parser.add_argument('--tangential-nudge', type=float, default=0.3,
                        help='Initial tangential nudge for orbiting bodies')

    # Phase 2 specific
    parser.add_argument('--binary-mass', type=float, default=100.0,
                        help='Mass of each body in equal-mass binary')

    args = parser.parse_args()

    if args.verify:
        run_verification()

    if args.phase0:
        experiment_phase0(side=args.side, G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          mass=args.star_mass,
                          deposit_strength=args.deposit_strength,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks)

    if args.phase1:
        experiment_phase1(side=args.side, G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          star_mass=args.star_mass,
                          planet_mass=args.planet_mass,
                          deposit_strength=args.deposit_strength,
                          separation=args.separation,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag,
                          freeze_edges=args.freeze_edges,
                          r_s=args.r_s,
                          tangential_nudge=args.tangential_nudge,
                          inertia=args.inertia)

    if args.phase2:
        experiment_phase2(side=max(args.side, 60), G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          mass=args.binary_mass,
                          deposit_strength=args.deposit_strength,
                          separation=args.separation,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag,
                          freeze_edges=args.freeze_edges,
                          tangential_nudge=args.tangential_nudge,
                          inertia=args.inertia)

    if args.phase3:
        experiment_phase3(side=max(args.side, 80), G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          star_mass=args.star_mass,
                          planet_mass=args.planet_mass,
                          moon_mass=args.moon_mass,
                          deposit_strength=args.deposit_strength,
                          planet_sep=args.separation,
                          moon_sep=args.moon_distance,
                          ticks=args.ticks,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag,
                          freeze_edges=args.freeze_edges,
                          tangential_nudge=args.tangential_nudge,
                          inertia=args.inertia)

    if args.force_law:
        experiment_force_law(side=max(args.side, 50), G=args.G, H=args.H,
                             alpha_expand=args.alpha_expand,
                             mass=args.star_mass,
                             deposit_strength=args.deposit_strength,
                             ticks=args.ticks,
                             formation_ticks=args.formation_ticks,
                             tag=args.tag)

    if not any([args.verify, args.phase0, args.phase1, args.phase2,
                args.phase3, args.force_law]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
