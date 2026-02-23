"""v13: Entity-Vortex Orbital Mechanics — RAW 170 Implementation.

Tests RAW 170's core prediction: variable edge lengths from Result 6
(de/dt = 1/(1+α×M/r)) produce Keplerian orbits WITHOUT Newtonian equations.

Key changes from v10:
- Variable edge lengths (per-node per-direction, 6 values per node)
- Edge expansion via de/dt = H/(1 + alpha_expand * |gamma|) — uses gamma field as M/r proxy
- Gradient weighted by 1/edge_length — shorter edges = stronger effective gravity
- Removed edge_gamma_scale hack — speed variation comes from edge geometry
- Physical position tracking — cumulative distance in variable-metric space
- Gamma spread UNCHANGED (uniform, vectorized) — only gradient is edge-weighted

Usage:
    python macro_bodies.py --verify
    python macro_bodies.py --phase0 --ticks 10000
    python macro_bodies.py --phase1 --ticks 50000
    python macro_bodies.py --phase2 --ticks 50000 --initial-momentum tangential
    python macro_bodies.py --phase3 --ticks 200000
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
    with variable edge lengths (RAW 170 Result 6).

    Each body has a separate tagged field layer. Total gamma = sum of all tags.
    Self-gravitation: alpha_eff = alpha / (1 + G * total_gamma).
    External gamma for body B = total - tagged[B].

    NEW in v13: Edge lengths stored per-node per-direction (n_nodes, 6).
    Expansion grows edges, suppressed near mass. This IS the metric tensor.
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
        # Directions: 0=+x, 1=-x, 2=+y, 3=-y, 4=+z, 5=-z
        self.edge_lengths = np.ones((actual_n, 6), dtype=np.float64)

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
        """Deterministic self-gravitating spread. Conserves gamma exactly.

        Spread rate is UNIFORM (independent of edge length).
        Edge-length effects are captured in the gradient, not the spread.
        This preserves the sparse matrix multiplication (fast).
        """
        alpha_eff = self.alpha / (1.0 + self.G * np.abs(self.gamma))
        alpha_eff = np.clip(alpha_eff, 0.0, 1.0)

        for bid in self.body_ids:
            outflow = alpha_eff * self.tagged[bid]
            per_edge = outflow / self.degrees
            inflow = self.A @ per_edge
            self.tagged[bid] = self.tagged[bid] - outflow + inflow

        self.sync_total()

    def expand_edges(self):
        """Grow all edges. Suppressed near mass (RAW 170 Result 6).

        de/dt = H / (1 + alpha_expand * |gamma|)

        Uses total gamma at each node as proxy for M/r — the gamma
        profile IS the 1/r gravitational potential from 3D diffusion.
        Always >= 0: edges can slow but never shrink.
        """
        if self.H <= 0:
            return
        growth_rate = self.H / (1.0 + self.alpha_expand * np.abs(self.gamma))
        self.edge_lengths += growth_rate[:, np.newaxis]

        # Enforce symmetry: edge A→B must equal edge B→A
        for d_fwd in range(0, 6, 2):  # +x, +y, +z
            d_rev = d_fwd + 1           # -x, -y, -z
            fwd_nbs = self.neighbor_dirs[:, d_fwd]
            e_fwd = self.edge_lengths[:, d_fwd].copy()
            e_rev = self.edge_lengths[fwd_nbs, d_rev].copy()
            avg = 0.5 * (e_fwd + e_rev)
            self.edge_lengths[:, d_fwd] = avg
            self.edge_lengths[fwd_nbs, d_rev] = avg

    def gradient_weighted(self, node, exclude_bid):
        """Compute gamma gradient weighted by 1/edge_length.

        Shorter edges → neighbor contributes MORE to gradient.
        This naturally makes effective gravity stronger near mass
        (where edges are short from suppressed expansion).

        Returns: (gx, gy, gz, gmag)
        """
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
        """Unweighted gradient (same as v10, for comparison)."""
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
        """Mean edge length at a node."""
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
        """Approximate physical distance: hop distance × average edge length."""
        hop_d = self.hop_distance(node_a, node_b)
        avg_a = float(np.mean(self.edge_lengths[node_a]))
        avg_b = float(np.mean(self.edge_lengths[node_b]))
        return hop_d * 0.5 * (avg_a + avg_b)

    def place_at_coords(self, x, y, z):
        s = self.side
        return self.coord_to_node[(x % s, y % s, z % s)]

    def coords_of(self, node):
        return self.node_coords[node]

    def set_edges_from_gamma(self, scale=1e-4, mode='linear'):
        """Set edge lengths from gamma field (static metric from Result 6).

        Modes:
          'linear': e = 1 / (1 + scale * |gamma|)
          'log':    e = 1 / (1 + scale * log(1 + |gamma|))  — spreads variation
          'sqrt':   e = 1 / (1 + scale * sqrt(|gamma|))

        Shorter edges near mass, normal (=1) far from mass.
        """
        g = np.abs(self.gamma)
        if mode == 'log':
            effective = np.log1p(g)
        elif mode == 'sqrt':
            effective = np.sqrt(g)
        else:
            effective = g
        edge_factor = 1.0 / (1.0 + scale * effective)
        self.edge_lengths[:] = edge_factor[:, np.newaxis]
        # Enforce symmetry
        for d_fwd in range(0, 6, 2):
            d_rev = d_fwd + 1
            fwd_nbs = self.neighbor_dirs[:, d_fwd]
            avg = 0.5 * (self.edge_lengths[:, d_fwd] + self.edge_lengths[fwd_nbs, d_rev])
            self.edge_lengths[:, d_fwd] = avg
            self.edge_lengths[fwd_nbs, d_rev] = avg
        e_min = float(np.min(self.edge_lengths))
        e_max = float(np.max(self.edge_lengths))
        print(f"  Edges set ({mode}): e=[{e_min:.6f}, {e_max:.6f}], "
              f"ratio={e_max/max(e_min,1e-20):.1f}")

    def set_edges_schwarzschild(self, center_node, r_s=5.0):
        """Set edges analytically: e = 1 / (1 + r_s / max(r, 1)).

        Clean Schwarzschild-like metric. Tests orbit physics independently
        of gamma-to-edge conversion.
        r_s = Schwarzschild radius analog (controls metric strength).
        """
        for node_id in range(self.n_nodes):
            r = self.hop_distance(center_node, node_id)
            r = max(r, 1)
            e = 1.0 / (1.0 + r_s / r)
            self.edge_lengths[node_id, :] = e
        # Enforce symmetry
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
        """Measure average edge length vs hop distance from center."""
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
# MacroBody — single node with mass property and physical tracking
# ===========================================================================

class MacroBody:
    """Astronomical body on the graph.

    Key change from v10: NO edge_gamma_scale hack. Speed variation comes
    from variable edge lengths — each hop covers different physical distance.
    Near mass: short edges → less distance/hop → effective slow.
    Far from mass: long edges → more distance/hop → effective fast.
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
        self.hop_accumulator = np.array([0.0, 0.0, 0.0])
        self.cascade_buffer = np.array([0.0, 0.0, 0.0])  # queued expansion drift

        # Physical position tracking (cumulative, accounts for edge lengths)
        self.physical_position = np.array([0.0, 0.0, 0.0])
        self.total_physical_distance = 0.0

        # History
        self.trajectory = []
        self.coord_history = []
        self.physical_trajectory = []

    def advance(self, field, tick=None):
        """Advance one tick. Deposit every tick. Hop when commit counter ready.

        Speed variation from edge lengths via time dilation ONLY:
        - effective_commit = commit_mass / avg_edge_length(node)
        - Short edges (near mass) → more ticks per hop → slower coordinate speed
        - Gradient applied at hop time (not every tick) — same as v10
        - Raw gradient (not edge-weighted) — keeps force law at ~1/r^2.2
        - Edge lengths affect SPEED, not force. This is GR time dilation.
        """
        field.deposit(self.node, self.bid, self.mass * self.deposit_strength)

        # Time dilation: effective commit time depends on local edge length
        local_edge = field.avg_edge_length(self.node)
        effective_commit = self.commit_mass / max(local_edge, 0.01)

        self.commit_counter += 1
        if self.commit_counter < effective_commit:
            return False
        self.commit_counter = 0

        # 1. Compute raw gradient at hop time (not edge-weighted)
        gx, gy, gz, gmag = field.gradient_raw(self.node, self.bid)

        # 2. Nudge internal direction (same as v10)
        dir_mag = np.linalg.norm(self.internal_direction)
        if dir_mag < 0.01:
            if gmag > 0:
                self.internal_direction = np.array([gx / gmag, gy / gmag,
                                                    gz / gmag])
            else:
                return False
        else:
            nudge = self.nudge_strength * self.gradient_coupling * gmag
            nudge = min(nudge, 0.5)
            if gmag > 0:
                self.internal_direction[0] += nudge * (gx / gmag)
                self.internal_direction[1] += nudge * (gy / gmag)
                self.internal_direction[2] += nudge * (gz / gmag)
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        # 3. Bresenham-like accumulator hop
        self.hop_accumulator += self.internal_direction
        abs_acc = np.abs(self.hop_accumulator)
        axis = int(np.argmax(abs_acc))
        sign = 1 if self.hop_accumulator[axis] >= 0 else -1
        self.hop_accumulator[axis] -= sign

        cur = field.coords_of(self.node)
        target = list(cur)
        target[axis] += sign
        best_nb = field.place_at_coords(target[0], target[1], target[2])

        # 4. Get edge length for this hop
        d_idx = axis * 2 + (0 if sign > 0 else 1)
        hop_edge_length = field.edge_lengths[self.node, d_idx]

        # 5. Move tagged gamma with the body
        amount = field.tagged[self.bid][self.node]
        if amount > 0:
            field.tagged[self.bid][self.node] = 0.0
            field.tagged[self.bid][best_nb] += amount
        self.prev_node = self.node
        self.node = best_nb
        self.hops += 1

        # 6. Track physical position
        direction_3d = np.zeros(3)
        direction_3d[axis] = float(sign)
        self.physical_position += direction_3d * hop_edge_length
        self.total_physical_distance += hop_edge_length

        field.sync_total()
        return True

    def advance_cascade(self, field, tick=None, other_bodies=None):
        """Advance using cascade compensation model (cascade_update.md).

        TWO SEPARATE MOTIONS, TWO SEPARATE ACCUMULATORS:

        1. cascade_buffer: expansion drift. Every tick, asymmetric growth rates
           accumulate here. When any component reaches ±1, the body is PHYSICALLY
           DISPLACED — the expanding space moved it. Independent of internal_direction.

        2. hop_accumulator + internal_direction: the body's OWN movement.
           At commit time, the body hops in its internal_direction. The cascade
           never touches this. internal_direction stays constant.

        The orbit IS the combination: body hops tangentially (own motion)
        while cascade displaces it radially (expansion carries it toward mass).
        These are separate physical processes that both change the body's node.

        Uses direct M/r for growth rate (Result 6):
            growth(r) = H / (1 + alpha * M / r)
        """
        field.deposit(self.node, self.bid, self.mass * self.deposit_strength)

        # --- MOTION 1: Expansion drift (every tick) ---
        # Growth rate asymmetry accumulates in cascade_buffer.
        # This is the space expanding underneath the body.
        cascade_moved = False
        if field.H > 0 and other_bodies:
            for d_idx in range(6):
                nb = field.neighbor_dirs[self.node, d_idx]
                if nb < 0:
                    continue
                # Result 6: growth = H / (1 + alpha * M/r)
                mass_influence = 0.0
                for ob in other_bodies:
                    if ob.bid == self.bid:
                        continue
                    r = field.hop_distance(nb, ob.node)
                    if r > 0:
                        mass_influence += ob.mass / r
                growth_rate = field.H / (1.0 + field.alpha_expand * mass_influence)
                dx, dy, dz = DIR_VECTORS[d_idx]
                # Space expands more away from mass → body displaced toward mass
                self.cascade_buffer[0] -= dx * growth_rate
                self.cascade_buffer[1] -= dy * growth_rate
                self.cascade_buffer[2] -= dz * growth_rate

            # When buffer reaches ±1, the expansion has displaced body by 1 hop
            abs_buf = np.abs(self.cascade_buffer)
            while np.max(abs_buf) >= 1.0:
                axis = int(np.argmax(abs_buf))
                sign = 1 if self.cascade_buffer[axis] >= 0 else -1
                self.cascade_buffer[axis] -= sign

                cur = field.coords_of(self.node)
                target = list(cur)
                target[axis] += sign
                new_node = field.place_at_coords(target[0], target[1], target[2])

                # Move tagged gamma with the body
                amount = field.tagged[self.bid][self.node]
                if amount > 0:
                    field.tagged[self.bid][self.node] = 0.0
                    field.tagged[self.bid][new_node] += amount
                self.node = new_node
                cascade_moved = True
                abs_buf = np.abs(self.cascade_buffer)

        if cascade_moved:
            field.sync_total()

        # --- MOTION 2: Body's own hop (at commit time) ---
        # The body always goes "forward" — but "forward" is defined by local geometry.
        self.commit_counter += 1
        if self.commit_counter < self.commit_mass:
            return cascade_moved
        self.commit_counter = 0

        # Bresenham hop from body's internal direction
        self.hop_accumulator += self.internal_direction
        abs_acc = np.abs(self.hop_accumulator)
        if np.max(abs_acc) < 0.01:
            return cascade_moved

        axis = int(np.argmax(abs_acc))
        sign = 1 if self.hop_accumulator[axis] >= 0 else -1
        self.hop_accumulator[axis] -= sign

        cur = field.coords_of(self.node)
        target = list(cur)
        target[axis] += sign
        best_nb = field.place_at_coords(target[0], target[1], target[2])

        d_idx = axis * 2 + (0 if sign > 0 else 1)
        hop_edge_length = field.edge_lengths[self.node, d_idx]

        amount = field.tagged[self.bid][self.node]
        if amount > 0:
            field.tagged[self.bid][self.node] = 0.0
            field.tagged[self.bid][best_nb] += amount
        self.prev_node = self.node
        self.node = best_nb
        self.hops += 1

        direction_3d = np.zeros(3)
        direction_3d[axis] = float(sign)
        self.physical_position += direction_3d * hop_edge_length
        self.total_physical_distance += hop_edge_length

        # --- GEODESIC FRAME ROTATION ---
        # The entity always goes "forward." But "forward" is defined by local
        # edge lengths. Asymmetric edges tilt the local frame toward shorter
        # edges (toward mass). The entity thinks it's going straight.
        # The graph is curving its path. This IS geodesic motion.
        #
        # For each axis pair (+x/-x, +y/-y, +z/-z), compute the fractional
        # edge length asymmetry. This gives the frame tilt per hop.
        # e_minus < e_plus → tilt toward minus direction (toward mass).
        tilt = np.zeros(3)
        for ax in range(3):
            d_plus = ax * 2       # +x, +y, +z
            d_minus = ax * 2 + 1  # -x, -y, -z
            e_plus = field.edge_lengths[self.node, d_plus]
            e_minus = field.edge_lengths[self.node, d_minus]
            # Fractional asymmetry: (e_plus - e_minus) / (e_plus + e_minus)
            # Positive when e_plus > e_minus → tilt toward minus (shorter edge)
            e_sum = e_plus + e_minus
            if e_sum > 0:
                tilt[ax] = -(e_plus - e_minus) / e_sum  # toward shorter edge

        tilt_mag = np.linalg.norm(tilt)
        if tilt_mag > 0:
            self.internal_direction += tilt
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        field.sync_total()
        return True

    def record(self, tick, field):
        self.trajectory.append((tick, self.node))
        c = field.coords_of(self.node)
        self.coord_history.append((tick, c[0], c[1], c[2]))
        p = self.physical_position
        self.physical_trajectory.append((tick, p[0], p[1], p[2]))


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


def plot_trajectories_xy(bodies, field, filename, title="Trajectories (XY)",
                         use_physical=False):
    fig, ax = plt.subplots(figsize=(8, 8))
    s = field.side
    for body in bodies:
        if use_physical and body.physical_trajectory:
            xs = [c[1] for c in body.physical_trajectory]
            ys = [c[2] for c in body.physical_trajectory]
        elif body.coord_history:
            unwrapped = unwrap_coords(body.coord_history, s)
            xs = [c[1] for c in unwrapped]
            ys = [c[2] for c in unwrapped]
        else:
            continue
        ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=body.bid)
        ax.plot(xs[0], ys[0], 'o', markersize=10)
        ax.plot(xs[-1], ys[-1], 's', markersize=8)
    ax.set_xlabel('X (physical)' if use_physical else 'X (hops)')
    ax.set_ylabel('Y (physical)' if use_physical else 'Y (hops)')
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
    """Plot average edge length vs hop distance from center."""
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
    """4-panel summary: trajectory, distance, angular momentum, edge profile."""
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

    # 4. Edge profile (snapshot around first body)
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
    print("\n=== v13 MACRO BODIES VERIFICATION ===\n")
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

    # Test 5: Edge expansion profile
    print("Test 5: Edge expansion suppressed near mass")
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

    # Test 7: Weighted gradient stronger near mass
    print("Test 7: Edge-weighted gradient > raw gradient near mass")
    gw_near = f5.gradient_weighted(f5.neighbor_dirs[center5, 0], 'A')
    gr_near = f5.gradient_raw(f5.neighbor_dirs[center5, 0], 'A')
    # Near mass: edges shorter, so 1/e > 1 → weighted > raw
    ok = gw_near[3] >= gr_near[3] * 0.8  # at least comparable
    print(f"  {'PASS' if ok else 'FAIL'}: weighted={gw_near[3]:.4f}, "
          f"raw={gr_near[3]:.4f}")
    passed += ok; failed += (not ok)

    # Test 8: Body hop timing (with uniform edges = commit_mass)
    print("Test 8: Hop timing with uniform edges")
    f8 = ContinuousGammaField(8000, k=6, G=0.0, body_ids=['A', 'B'])
    center8 = f8.n_nodes // 2
    far8 = f8.place_at_coords(f8.side // 2 + 10, f8.side // 2, f8.side // 2)
    f8.tagged['B'][far8] = 10000.0
    f8.sync_total()
    for _ in range(50):
        f8.spread()
    # With uniform edges (all=1.0), effective_commit = commit_mass/1.0 = 5
    body8 = MacroBody('A', center8, mass=1.0, commit_mass=5,
                      deposit_strength=0.001)
    body8.internal_direction = np.array([1.0, 0.0, 0.0])
    hops_at = []
    for tick in range(25):
        moved = body8.advance(f8, tick)
        if moved:
            hops_at.append(tick)
    expected_hops = [4, 9, 14, 19, 24]
    ok = hops_at == expected_hops
    print(f"  {'PASS' if ok else 'FAIL'}: hops at {hops_at} "
          f"(expected {expected_hops})")
    passed += ok; failed += (not ok)

    # Test 9: Physical distance tracking
    print("Test 9: Physical distance tracks edge lengths")
    f9 = ContinuousGammaField(1000, k=6, G=0.0, body_ids=['A'])
    # Set non-uniform edge lengths in +x direction
    for n in range(f9.n_nodes):
        f9.edge_lengths[n, 0] = 2.0  # +x edges = 2.0
        nb = f9.neighbor_dirs[n, 0]
        if nb >= 0:
            f9.edge_lengths[nb, 1] = 2.0  # symmetric
    body9 = MacroBody('A', f9.n_nodes // 2, mass=1.0, commit_mass=1,
                      deposit_strength=0.0)
    body9.internal_direction = np.array([1.0, 0.0, 0.0])
    for tick in range(5):
        body9.advance(f9, tick)
    expected_phys = 5 * 2.0  # 5 hops × edge_length 2.0
    ok = abs(body9.total_physical_distance - expected_phys) < 0.01
    print(f"  {'PASS' if ok else 'FAIL'}: physical_dist={body9.total_physical_distance:.2f} "
          f"(expected {expected_phys:.1f})")
    passed += ok; failed += (not ok)

    # Test 10: Gradient direction nudge
    print("Test 10: Gradient nudges internal direction")
    f10 = ContinuousGammaField(8000, k=6, G=0.0, body_ids=['A', 'B'])
    center10 = f10.n_nodes // 2
    c10 = f10.coords_of(center10)
    y_node = f10.place_at_coords(c10[0], c10[1] + 5, c10[2])
    f10.tagged['B'][y_node] = 50000.0
    f10.sync_total()
    for _ in range(80):
        f10.spread()
    body10 = MacroBody('A', center10, mass=1.0, commit_mass=5,
                       deposit_strength=0.001, gradient_coupling=0.01)
    body10.internal_direction = np.array([1.0, 0.0, 0.0])
    for tick in range(100):
        body10.advance(f10, tick)
    angle = math.atan2(body10.internal_direction[1],
                       body10.internal_direction[0]) * 180 / math.pi
    ok = angle > 5
    print(f"  {'PASS' if ok else 'FAIL'}: angle={angle:.1f} deg "
          f"(started at 0, expect >5)")
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
    print("PHASE 0: Edge Expansion Verification (Result 6)")
    print("=" * 70)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=['A'])
    center = field.place_at_coords(side // 2, side // 2, side // 2)

    # Formation: establish gamma well
    print(f"\n  Formation: {formation_ticks} ticks (deposit + spread, no expansion)")
    body = MacroBody('A', center, mass=mass, commit_mass=999999,
                     deposit_strength=deposit_strength)
    for tick in range(formation_ticks):
        body.advance(field, tick)
        field.spread()
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

    # Plot profiles at different times
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

    for t, profile in sorted(profiles.items()):
        rs = sorted(profile.keys())
        es = [profile[r] for r in rs]
        ax1.plot(rs, es, 'o-', markersize=4, label=f't={t}')
    ax1.set_xlabel('Distance from mass (hops)')
    ax1.set_ylabel('Average edge length')
    ax1.set_title('Edge Length Profile (Result 6)')
    ax1.legend()
    ax1.grid(True, alpha=0.3)

    # Gamma profile for reference
    rs_g = sorted(gamma_avg.keys())
    gs = [gamma_avg[r] for r in rs_g]
    ax2.semilogy(rs_g, gs, 'ro-', markersize=4)
    ax2.set_xlabel('Distance from mass (hops)')
    ax2.set_ylabel('Average gamma (log)')
    ax2.set_title('Gamma Field Profile')
    ax2.grid(True, alpha=0.3)

    fig.suptitle(f'Phase 0: Edge Expansion (side={side}, mass={mass}, '
                 f'H={H}, alpha_expand={alpha_expand})', fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'phase0_edge_expansion.png', dpi=150)
    plt.close(fig)
    print(f"\n  Saved: {RESULTS_DIR / 'phase0_edge_expansion.png'}")

    return profiles


# ===========================================================================
# Phase 1: Two-Body with Variable Edges
# ===========================================================================

def experiment_phase1(side=40, G=10.0, H=0.001, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=10.0,
                      star_commit=100, planet_commit=5,
                      deposit_strength=1.0, separation=15,
                      ticks=50000, gradient_coupling=1e-4,
                      formation_ticks=5000, tag='',
                      freeze_edges=False, edge_scale=0.0,
                      edge_mode='log', r_s=0.0,
                      cascade=False):
    if separation >= side // 2:
        side = max(side, 3 * separation)
        print(f"  WARNING: Increased side to {side}")

    print("=" * 70)
    print("PHASE 1: Two-Body with Variable Edge Lengths")
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
        MacroBody('star', node_star, mass=star_mass, commit_mass=star_commit,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
        MacroBody('planet', node_planet, mass=planet_mass,
                  commit_mass=planet_commit,
                  deposit_strength=deposit_strength * planet_mass / star_mass,
                  gradient_coupling=gradient_coupling),
    ]
    # Tangential initial momentum for planet
    bodies[1].internal_direction = np.array([0.0, 1.0, 0.0])

    init_dist = field.hop_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Star: mass={star_mass}, commit={star_commit}")
    print(f"  Planet: mass={planet_mass}, commit={planet_commit}")
    print(f"  Separation: {init_dist} hops")
    print(f"  H={H}, alpha_expand={alpha_expand}, gradient_coupling={gradient_coupling}")

    # Formation
    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks...")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_strength)
            field.spread()
            field.expand_edges()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

    # Set edges from gamma profile (static metric from Result 6)
    if edge_scale > 0:
        field.set_edges_from_gamma(scale=edge_scale, mode=edge_mode)
        field.H = 0.0  # no expansion — static metric
        # Diagnostics at key locations
        star_e = field.avg_edge_length(bodies[0].node)
        planet_e = field.avg_edge_length(bodies[1].node)
        gr = field.gradient_raw(bodies[1].node, 'planet')
        eff_cm = planet_commit / max(planet_e, 0.01)
        # For circular orbit at hop time:
        # nudge_per_hop = (1/commit_mass) * gc * gmag
        # hops_per_orbit ≈ 2π*r
        # total_turning = hops_per_orbit * nudge_per_hop = 2π
        # gc = commit_mass / (r * gmag)
        if gr[3] > 0:
            gc_needed = planet_commit / (separation * gr[3])
        else:
            gc_needed = float('inf')
        print(f"  Static metric: e_star={star_e:.6f}, e_planet={planet_e:.6f}")
        print(f"  At planet (r={separation}): |grad_raw|={gr[3]:.6f}")
        print(f"  Effective commit@planet: {eff_cm:.1f} ticks "
              f"(base={planet_commit})")
        print(f"  Calculated gc for circular orbit: {gc_needed:.4f}")

    # Schwarzschild analytic edges (bypass gamma-to-edge conversion)
    if r_s > 0:
        field.set_edges_schwarzschild(bodies[0].node, r_s=r_s)
        field.H = 0.0
        star_e = field.avg_edge_length(bodies[0].node)
        planet_e = field.avg_edge_length(bodies[1].node)
        gr = field.gradient_raw(bodies[1].node, 'planet')
        eff_cm = planet_commit / max(planet_e, 0.01)
        if gr[3] > 0:
            gc_needed = planet_commit / (separation * gr[3])
        else:
            gc_needed = float('inf')
        print(f"  Schwarzschild: e_star={star_e:.4f}, e_planet={planet_e:.4f}")
        print(f"  At planet (r={separation}): |grad_raw|={gr[3]:.6f}")
        print(f"  Effective commit@planet: {eff_cm:.1f} ticks")
        print(f"  Calculated gc: {gc_needed:.4f}")

    # Freeze edges after formation if requested
    if freeze_edges:
        field.H = 0.0
        near_e = field.avg_edge_length(bodies[0].node)
        far_node = field.place_at_coords(0, 0, 0)
        far_e = field.avg_edge_length(far_node)
        print(f"  FROZEN edges: e_star={near_e:.3f}, e_far={far_e:.3f}, "
              f"ratio={far_e/max(near_e,1e-10):.2f}")

    # Reduce star deposit during dynamics (gamma well already established)
    bodies[0].deposit_strength *= 0.001
    total_gamma_pre = field.total_gamma()
    print(f"  Pre-dynamics gamma: {total_gamma_pre:.0f}")

    # Run
    diag_interval = max(ticks // 100, 1)
    record_interval = max(ticks // 2000, 1)
    records = []
    ang_records = []

    if cascade:
        print(f"  MODE: CASCADE (no gradient_coupling)")
        # Diagnostic: predicted cascade drift rate at planet position
        planet = bodies[1]
        star_node = bodies[0].node
        test_drifts = []
        for d_idx in range(6):
            nb = field.neighbor_dirs[planet.node, d_idx]
            if nb < 0:
                continue
            mi = 0.0
            for ob in bodies:
                if ob.bid == planet.bid:
                    continue
                r = field.hop_distance(nb, ob.node)
                if r > 0:
                    mi += ob.mass / r
            gr = H / (1.0 + alpha_expand * mi)
            test_drifts.append((d_idx, gr, mi))
        print(f"  CASCADE DIAGNOSTICS at planet (r={separation}):")
        for d_idx, gr, mi in test_drifts:
            dvec = DIR_VECTORS[d_idx]
            print(f"    dir={dvec} M/r={mi:.1f} growth={gr:.6f}")
        # Net drift per tick
        net = np.zeros(3)
        for d_idx, gr, mi in test_drifts:
            net -= DIR_VECTORS[d_idx] * gr
        print(f"    Net drift/tick: [{net[0]:.6f}, {net[1]:.6f}, {net[2]:.6f}]")
        print(f"    |net|={np.linalg.norm(net):.6f}")
        print(f"    Hop speed: {1.0/planet_commit:.3f} hops/tick")
        print(f"    Ticks per cascade hop: {1.0/max(np.linalg.norm(net),1e-20):.0f}")
        orbit_period = 2 * math.pi * separation * planet_commit
        inspiral_time = separation / max(np.linalg.norm(net), 1e-20)
        print(f"    Orbit period: ~{orbit_period:.0f} ticks")
        print(f"    Inspiral time: ~{inspiral_time:.0f} ticks")
        print(f"    Orbits before inspiral: ~{inspiral_time/orbit_period:.1f}")

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        field.expand_edges()
        for body in bodies:
            if cascade:
                body.advance_cascade(field, tick, other_bodies=bodies)
            else:
                body.advance(field, tick)

        if (tick + 1) % record_interval == 0:
            for body in bodies:
                body.record(tick + 1, field)

        if (tick + 1) % diag_interval == 0:
            d = field.euclidean_distance(bodies[0].node, bodies[1].node)
            d_hop = field.hop_distance(bodies[0].node, bodies[1].node)
            d_phys = field.physical_distance_approx(bodies[0].node, bodies[1].node)
            records.append({
                'tick': tick + 1,
                'd_AB': d, 'd_AB_hop': d_hop, 'd_AB_phys': d_phys,
            })

            L = compute_angular_momentum(bodies, field)
            L_total = sum(L.values())
            ang_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 10) == 0:
                avg_e = field.avg_edge_length(bodies[0].node)
                print(f"    Tick {tick+1:7d}: d={d:.1f} (hop={d_hop}) "
                      f"e_star={avg_e:.3f} L={L_total:+.2f} ({elapsed:.1f}s)")

    final_d = field.euclidean_distance(bodies[0].node, bodies[1].node)
    print(f"\n  Distance: {init_dist} -> {final_d:.1f}")
    print(f"  Hops: star={bodies[0].hops}, planet={bodies[1].hops}")

    if records:
        dists = [r['d_AB'] for r in records]
        print(f"  Range: [{min(dists):.1f}, {max(dists):.1f}]")
        reversals = sum(1 for i in range(2, len(dists))
                        if (dists[i] - dists[i-1]) * (dists[i-1] - dists[i-2]) < 0)
        print(f"  Reversals: {reversals}")

    suffix = f"_{tag}" if tag else ""

    if records:
        plot_distances(records, ['AB'],
                       f'Two-Body (variable edges): star={star_mass}, planet={planet_mass}',
                       RESULTS_DIR / f'phase1_distance{suffix}.png',
                       {'AB': init_dist})

    if any(b.coord_history for b in bodies):
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase1_trajectory{suffix}.png',
                             'Two-Body Trajectories (hops)')
        plot_trajectories_xy(bodies, field,
                             RESULTS_DIR / f'phase1_trajectory_phys{suffix}.png',
                             'Two-Body Trajectories (physical)',
                             use_physical=True)

    if ang_records:
        plot_angular_momentum(ang_records,
                              RESULTS_DIR / f'phase1_Lz{suffix}.png')

    plot_summary_dashboard(bodies, field, records, ang_records,
                           RESULTS_DIR / f'phase1_summary{suffix}.png',
                           f'Phase 1: Star-Planet (r={separation})')

    return records


# ===========================================================================
# Phase 2: Force Law with Variable Edges
# ===========================================================================

def experiment_force_law(side=50, G=10.0, H=0.001, alpha_expand=1.0,
                         mass=1000.0, deposit_strength=1.0,
                         ticks=30000, gradient_coupling=1e-4,
                         formation_ticks=5000, tag=''):
    print("=" * 70)
    print("FORCE LAW: Gradient vs Distance (weighted and raw)")
    print("=" * 70)

    n = side ** 3
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=['A'])
    cx, cy, cz = side // 2, side // 2, side // 2
    node_a = field.place_at_coords(cx, cy, cz)

    body_a = MacroBody('A', node_a, mass=mass, commit_mass=999999,
                       deposit_strength=deposit_strength)

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

    # Plot comparison
    suffix = f"_{tag}" if tag else ""
    if gradient_data:
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))

        rs = [d['r'] for d in gradient_data]
        gw = [d['gmag_weighted'] for d in gradient_data]
        gr = [d['gmag_raw'] for d in gradient_data]

        ax1.plot(rs, gw, 'bo-', label='Edge-weighted', markersize=8)
        ax1.plot(rs, gr, 'rs-', label='Raw (v10-style)', markersize=8)
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
            ax2.set_title('Log-Log Comparison')
            ax2.legend()
            ax2.grid(True, alpha=0.3)

        fig.suptitle(f'Force Law: H={H}, alpha_expand={alpha_expand}',
                     fontweight='bold')
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'force_law_comparison{suffix}.png', dpi=150)
        plt.close(fig)

        # Individual force law plots
        plot_force_law([{'r': d['r'], 'accel': d['gmag_weighted']}
                        for d in gradient_data if d['gmag_weighted'] > 0],
                       RESULTS_DIR / f'force_law_weighted{suffix}.png',
                       ' (edge-weighted)')
        plot_force_law([{'r': d['r'], 'accel': d['gmag_raw']}
                        for d in gradient_data if d['gmag_raw'] > 0],
                       RESULTS_DIR / f'force_law_raw{suffix}.png',
                       ' (raw, v10-style)')

    return gradient_data


# ===========================================================================
# Phase 3: Three-Body (Star + Planet + Moon)
# ===========================================================================

def experiment_phase3(side=80, G=10.0, H=0.001, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=10.0, moon_mass=0.1,
                      star_commit=100, planet_commit=5, moon_commit=1,
                      deposit_strength=1.0, planet_sep=15, moon_sep=3,
                      ticks=200000, gradient_coupling=1e-4,
                      formation_ticks=10000, tag='',
                      freeze_edges=False):
    if planet_sep + moon_sep >= side // 2:
        side = max(side, 3 * (planet_sep + moon_sep))
        print(f"  WARNING: Increased side to {side}")

    print("=" * 70)
    print("PHASE 3: Three-Body (Star + Planet + Moon)")
    print("=" * 70)

    n = side ** 3
    body_ids = ['star', 'planet', 'moon']
    field = ContinuousGammaField(n, k=6, G=G, H=H, alpha_expand=alpha_expand,
                                  body_ids=body_ids)

    cx, cy, cz = side // 2, side // 2, side // 2
    node_star = field.place_at_coords(cx, cy, cz)
    node_planet = field.place_at_coords(cx + planet_sep, cy, cz)
    node_moon = field.place_at_coords(cx + planet_sep + moon_sep, cy, cz)

    # Initialize star's gamma well
    field.initialize_peak('star', node_star, star_mass * 50, smooth_ticks=30)

    bodies = [
        MacroBody('star', node_star, mass=star_mass, commit_mass=star_commit,
                  deposit_strength=deposit_strength,
                  gradient_coupling=gradient_coupling),
        MacroBody('planet', node_planet, mass=planet_mass,
                  commit_mass=planet_commit,
                  deposit_strength=deposit_strength * planet_mass / star_mass,
                  gradient_coupling=gradient_coupling),
        MacroBody('moon', node_moon, mass=moon_mass,
                  commit_mass=moon_commit,
                  deposit_strength=deposit_strength * moon_mass / star_mass,
                  gradient_coupling=gradient_coupling),
    ]

    # Tangential initial momentum
    bodies[1].internal_direction = np.array([0.0, 1.0, 0.0])  # planet orbits star
    bodies[2].internal_direction = np.array([0.0, 1.0, 0.0])  # moon orbits planet

    print(f"\n  Lattice: side={side}, N={field.n_nodes}")
    print(f"  Star: mass={star_mass}, commit={star_commit}")
    print(f"  Planet: mass={planet_mass}, commit={planet_commit}, r={planet_sep}")
    print(f"  Moon: mass={moon_mass}, commit={moon_commit}, r_planet={moon_sep}")

    # Formation
    if formation_ticks > 0:
        print(f"  Formation: {formation_ticks} ticks...")
        ft0 = time.time()
        for ft in range(formation_ticks):
            for body in bodies:
                field.deposit(body.node, body.bid,
                              body.mass * body.deposit_strength)
            field.spread()
            field.expand_edges()
        print(f"  Formation done in {time.time()-ft0:.1f}s")

    # Freeze edges after formation if requested
    if freeze_edges:
        field.H = 0.0
        near_e = field.avg_edge_length(bodies[0].node)
        far_node = field.place_at_coords(0, 0, 0)
        far_e = field.avg_edge_length(far_node)
        print(f"  FROZEN edges: e_star={near_e:.3f}, e_far={far_e:.3f}, "
              f"ratio={far_e/max(near_e,1e-10):.2f}")

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
                       'Three-Body: Star-Planet-Moon',
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
                           'Phase 3: Star-Planet-Moon')

    return records


# ===========================================================================
# Kepler Test
# ===========================================================================

def experiment_kepler(side=50, G=10.0, H=0.001, alpha_expand=1.0,
                      star_mass=1000.0, planet_mass=10.0,
                      star_commit=100, planet_commit=5,
                      deposit_strength=1.0, ticks=200000,
                      gradient_coupling=1e-4, formation_ticks=5000, tag=''):
    print("=" * 70)
    print("KEPLER'S THIRD LAW TEST")
    print("=" * 70)

    separations = [10, 15, 20, 25]
    kepler_data = []

    for sep in separations:
        if sep >= side // 2:
            continue
        print(f"\n  --- Separation = {sep} ---")
        records = experiment_phase1(
            side=side, G=G, H=H, alpha_expand=alpha_expand,
            star_mass=star_mass, planet_mass=planet_mass,
            star_commit=star_commit, planet_commit=planet_commit,
            deposit_strength=deposit_strength, separation=sep,
            ticks=ticks, gradient_coupling=gradient_coupling,
            formation_ticks=formation_ticks,
            tag=f'kepler_r{sep}')

        if records and len(records) > 20:
            dists = [r['d_AB'] for r in records]
            ticks_arr = [r['tick'] for r in records]
            mean_d = np.mean(dists)
            crossings = []
            for i in range(1, len(dists)):
                if (dists[i] - mean_d) * (dists[i - 1] - mean_d) < 0:
                    crossings.append(ticks_arr[i])

            if len(crossings) >= 4:
                half_periods = [crossings[i + 1] - crossings[i]
                                for i in range(len(crossings) - 1)]
                T = 2 * np.mean(half_periods)
                kepler_data.append({'r': sep, 'T': T, 'T2': T**2, 'r3': sep**3})
                print(f"    Period ~ {T:.0f} ticks ({len(crossings)} crossings)")
            else:
                print(f"    Not enough oscillations ({len(crossings)} crossings)")

    if len(kepler_data) >= 2:
        print("\n  === Kepler Summary ===")
        print(f"  {'r':>5s} {'T':>10s} {'T^2':>14s} {'r^3':>10s} {'T^2/r^3':>10s}")
        for d in kepler_data:
            ratio = d['T2'] / d['r3'] if d['r3'] > 0 else 0
            print(f"  {d['r']:5d} {d['T']:10.0f} {d['T2']:14.0f} "
                  f"{d['r3']:10d} {ratio:10.2f}")
        ratios = [d['T2'] / d['r3'] for d in kepler_data if d['r3'] > 0]
        if ratios:
            cv = np.std(ratios) / np.mean(ratios) if np.mean(ratios) > 0 else 999
            print(f"\n  T^2/r^3 variation: CV = {cv:.3f} "
                  f"({'PASS' if cv < 0.1 else 'FAIL' if cv > 0.3 else 'PARTIAL'})")

        # Plot
        suffix = f"_{tag}" if tag else ""
        fig, ax = plt.subplots(figsize=(8, 6))
        r3s = [d['r3'] for d in kepler_data]
        t2s = [d['T2'] for d in kepler_data]
        ax.plot(r3s, t2s, 'bo-', markersize=10)
        if len(kepler_data) >= 2:
            coeffs = np.polyfit(r3s, t2s, 1)
            x_fit = np.linspace(0, max(r3s) * 1.1, 100)
            ax.plot(x_fit, np.polyval(coeffs, x_fit), 'r--',
                    label=f'Linear fit (slope={coeffs[0]:.1f})')
        ax.set_xlabel('r³')
        ax.set_ylabel('T²')
        ax.set_title("Kepler's Third Law: T² vs r³")
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'kepler_T2_r3{suffix}.png', dpi=150)
        plt.close(fig)

    return kepler_data


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v13: Entity-Vortex Orbital Mechanics (RAW 170)')

    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase0', action='store_true',
                        help='Edge expansion verification')
    parser.add_argument('--phase1', action='store_true',
                        help='Two-body with variable edges')
    parser.add_argument('--phase3', action='store_true',
                        help='Three-body: star + planet + moon')
    parser.add_argument('--force-law', action='store_true',
                        help='Force law measurement')
    parser.add_argument('--kepler', action='store_true',
                        help="Kepler's third law test")

    parser.add_argument('--side', type=int, default=40)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--H', type=float, default=0.001)
    parser.add_argument('--alpha-expand', type=float, default=1.0,
                        help='Expansion suppression strength (Result 6)')
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--formation-ticks', type=int, default=5000)
    parser.add_argument('--gradient-coupling', type=float, default=1e-4)
    parser.add_argument('--freeze-edges', action='store_true',
                        help='Freeze edge lengths after formation (H=0 during dynamics)')
    parser.add_argument('--edge-scale', type=float, default=0.0,
                        help='Set edges from gamma: e=1/(1+scale*f(gamma)). 0=disabled.')
    parser.add_argument('--edge-mode', type=str, default='log',
                        choices=['linear', 'log', 'sqrt'],
                        help='Edge scaling mode: linear, log, or sqrt')
    parser.add_argument('--r-s', type=float, default=0.0,
                        help='Schwarzschild radius for analytic edges. 0=disabled.')
    parser.add_argument('--cascade', action='store_true',
                        help='Use cascade compensation model (no gradient_coupling)')
    parser.add_argument('--deposit-strength', type=float, default=1.0)
    parser.add_argument('--tag', type=str, default='')

    # Body parameters
    parser.add_argument('--star-mass', type=float, default=1000.0)
    parser.add_argument('--planet-mass', type=float, default=10.0)
    parser.add_argument('--moon-mass', type=float, default=0.1)
    parser.add_argument('--star-commit', type=int, default=100)
    parser.add_argument('--planet-commit', type=int, default=5)
    parser.add_argument('--moon-commit', type=int, default=1)
    parser.add_argument('--separation', type=int, default=15)
    parser.add_argument('--moon-distance', type=int, default=3)

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
                          star_commit=args.star_commit,
                          planet_commit=args.planet_commit,
                          deposit_strength=args.deposit_strength,
                          separation=args.separation,
                          ticks=args.ticks,
                          gradient_coupling=args.gradient_coupling,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag,
                          freeze_edges=args.freeze_edges,
                          edge_scale=args.edge_scale,
                          edge_mode=args.edge_mode,
                          r_s=args.r_s,
                          cascade=args.cascade)

    if args.phase3:
        experiment_phase3(side=max(args.side, 80), G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          star_mass=args.star_mass,
                          planet_mass=args.planet_mass,
                          moon_mass=args.moon_mass,
                          star_commit=args.star_commit,
                          planet_commit=args.planet_commit,
                          moon_commit=args.moon_commit,
                          deposit_strength=args.deposit_strength,
                          planet_sep=args.separation,
                          moon_sep=args.moon_distance,
                          ticks=args.ticks,
                          gradient_coupling=args.gradient_coupling,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag,
                          freeze_edges=args.freeze_edges)

    if args.force_law:
        experiment_force_law(side=max(args.side, 50), G=args.G, H=args.H,
                             alpha_expand=args.alpha_expand,
                             mass=args.star_mass,
                             deposit_strength=args.deposit_strength,
                             ticks=args.ticks,
                             gradient_coupling=args.gradient_coupling,
                             formation_ticks=args.formation_ticks,
                             tag=args.tag)

    if args.kepler:
        experiment_kepler(side=max(args.side, 50), G=args.G, H=args.H,
                          alpha_expand=args.alpha_expand,
                          star_mass=args.star_mass,
                          planet_mass=args.planet_mass,
                          star_commit=args.star_commit,
                          planet_commit=args.planet_commit,
                          deposit_strength=args.deposit_strength,
                          ticks=args.ticks,
                          gradient_coupling=args.gradient_coupling,
                          formation_ticks=args.formation_ticks,
                          tag=args.tag)

    if not any([args.verify, args.phase0, args.phase1, args.phase3,
                args.force_law, args.kepler]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
