"""v9: Continuous Internal Direction Vector.

v8 proved attraction via self-subtraction (10->4 hops in 50K ticks). The entity
needs momentum to overshoot, orbit, and conserve angular momentum.

Key insight: the entity maintains a CONTINUOUS direction vector internally, not
quantized to the 6 lattice directions. Each commit window, the external gamma
gradient NUDGES this vector by a small amount (1/mass). The actual hop goes to
whichever lattice neighbor is closest to the internal vector. Over many hops,
small nudges accumulate and the internal vector rotates smoothly. When it crosses
the 45-degree boundary between two lattice directions, the hop switches axis.

Direction selection at each commit window:
    1. grad_unit = unit vector from weighted sum of neighbor directions by external gamma
    2. nudge_strength = 1.0 / commit_mass (heavier = harder to turn)
    3. internal_direction += nudge_strength * grad_unit, then re-normalize
    4. hop to neighbor with highest dot product with internal_direction

The internal direction is NEVER reset to the hop direction. It remembers the
fractional deflection between hops.

Usage:
    python tagged_gamma.py --verify
    python tagged_gamma.py --phase2 --ticks 50000
    python tagged_gamma.py --phase2 --ticks 50000 --initial-momentum perpendicular
    python tagged_gamma.py --phase3 --ticks 100000 --initial-momentum tangential

February 2026
"""

import argparse
import json
import math
import time
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v6'))
from quantum_gamma import QuantumGammaField
from gamma_field import RESULTS_DIR as V6_RESULTS_DIR, make_serializable

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# TaggedGammaField (identical to v8, plus direction_vector)
# ===========================================================================

class TaggedGammaField(QuantumGammaField):
    """Integer stochastic gamma field with per-entity tagging.

    Each quantum is tagged with its source entity ID. The total gamma at
    each node is the sum of all tags. Self-gravitation (binding) uses total
    gamma. External gamma (for movement decisions) excludes the entity's
    own tagged quanta.
    """

    def __init__(self, *args, entity_ids=None, **kwargs):
        kwargs['G_attract'] = 0.0
        super().__init__(*args, **kwargs)
        self.entity_ids = entity_ids or []
        self.tagged = {
            eid: np.zeros(self.n_nodes, dtype=np.int64)
            for eid in self.entity_ids
        }
        self.sync_total()

    def sync_total(self):
        if self.entity_ids:
            self.gamma = sum(self.tagged[eid] for eid in self.entity_ids)
        else:
            self.gamma = np.zeros(self.n_nodes, dtype=np.int64)

    def external_gamma(self, node, exclude_eid):
        return int(self.gamma[node]) - int(self.tagged[exclude_eid][node])

    def external_gamma_array(self, exclude_eid):
        return self.gamma - self.tagged[exclude_eid]

    def spread(self):
        gamma_float = self.gamma.astype(np.float64)
        alpha_eff = self.alpha / (1.0 + self.G * gamma_float)
        alpha_eff = np.clip(alpha_eff, 0.0, 1.0)

        for eid in self.entity_ids:
            n_leaving = self.rng.binomial(self.tagged[eid], alpha_eff)
            self.tagged[eid] -= n_leaving
            self._distribute_uniform(n_leaving, self.tagged[eid])

        self.sync_total()

    def initialize_tagged_peak(self, eid, center_node, mass, smooth_ticks=10):
        self.tagged[eid][center_node] += int(mass)
        self.sync_total()
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def initialize_tagged_peaks(self, entity_centers, mass, smooth_ticks=10):
        for eid, center in entity_centers.items():
            self.tagged[eid][center] += int(mass)
        self.sync_total()
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def tagged_total(self, eid):
        return int(np.sum(self.tagged[eid]))

    def tagged_peak_node(self, eid):
        return int(np.argmax(self.tagged[eid]))

    def direction_vector(self, from_node, to_node):
        """Direction vector with periodic wrapping on the lattice."""
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


# ===========================================================================
# Entity with Momentum
# ===========================================================================

class Entity:
    """Entity with continuous internal direction vector.

    At each commit window (every commit_mass ticks):
    1. Compute gradient unit vector from external gamma at neighbors
    2. NUDGE internal_direction by (1/mass) * gradient_unit
    3. Re-normalize internal_direction to unit length
    4. Hop to neighbor with highest dot product with internal_direction
    5. Do NOT overwrite internal_direction with hop direction

    The internal direction is continuous (not quantized to lattice). It
    accumulates small gradient nudges over many hops, enabling smooth turning.
    Heavier entities (higher commit_mass) nudge less per hop → wider turns.
    """

    def __init__(self, eid, node, commit_mass=5):
        self.eid = eid
        self.node = node
        self.commit_mass = commit_mass
        self.nudge_strength = 1.0 / float(commit_mass)
        self.commit_counter = 0
        self.internal_direction = np.array([0.0, 0.0, 0.0])
        self.prev_node = node
        self.hops = 0
        self.trajectory = []
        self.direction_history = []  # (tick, dx, dy, dz) for diagnostics
        self.hop_dir_counts = {(1,0,0):0, (-1,0,0):0, (0,1,0):0,
                               (0,-1,0):0, (0,0,1):0, (0,0,-1):0}

    def advance(self, field, tick=None):
        """Advance one tick. Returns True if entity hopped."""
        self.commit_counter += 1
        if self.commit_counter < self.commit_mass:
            return False
        self.commit_counter = 0

        neighbors = field.neighbors[self.node]
        if not neighbors:
            return False

        # 1. Compute gradient unit vector from external gamma
        gx, gy, gz = 0.0, 0.0, 0.0
        for nb in neighbors:
            ext = field.external_gamma(nb, self.eid)
            d = field.direction_vector(self.node, nb)
            gx += d[0] * float(ext)
            gy += d[1] * float(ext)
            gz += d[2] * float(ext)
        gmag = math.sqrt(gx*gx + gy*gy + gz*gz)
        if gmag > 0:
            gx /= gmag
            gy /= gmag
            gz /= gmag

        # 2. Initialize or nudge internal direction
        dir_mag = np.linalg.norm(self.internal_direction)
        if dir_mag < 0.01:
            # No direction yet: use pure gradient, or stay
            if gmag > 0:
                self.internal_direction = np.array([gx, gy, gz])
            else:
                return False  # no signal, no direction, stay
        else:
            # NUDGE: gradient rotates internal direction by 1/mass
            self.internal_direction[0] += self.nudge_strength * gx
            self.internal_direction[1] += self.nudge_strength * gy
            self.internal_direction[2] += self.nudge_strength * gz
            # Re-normalize
            new_mag = np.linalg.norm(self.internal_direction)
            if new_mag > 0:
                self.internal_direction /= new_mag

        # 3. Pick neighbor with highest dot product with internal direction
        best_nb = None
        best_dot = -1e30
        for nb in neighbors:
            d = field.direction_vector(self.node, nb)
            dot = (self.internal_direction[0] * d[0] +
                   self.internal_direction[1] * d[1] +
                   self.internal_direction[2] * d[2])
            if dot > best_dot:
                best_dot = dot
                best_nb = nb

        if best_nb is None:
            return False

        # 4. Hop: transfer tagged quanta, do NOT overwrite internal_direction
        amount = field.tagged[self.eid][self.node]
        if amount > 0:
            field.tagged[self.eid][self.node] -= amount
            field.tagged[self.eid][best_nb] += amount
        hop_d = field.direction_vector(self.node, best_nb)
        if hop_d in self.hop_dir_counts:
            self.hop_dir_counts[hop_d] += 1
        self.prev_node = self.node
        self.node = best_nb
        self.hops += 1
        field.sync_total()
        return True

    def record(self, tick):
        self.trajectory.append((tick, self.node))
        d = self.internal_direction
        self.direction_history.append((tick, float(d[0]), float(d[1]), float(d[2])))


# ===========================================================================
# Angular Momentum
# ===========================================================================

def compute_angular_momentum(entities, field):
    """Compute z-component of angular momentum for each entity relative to COM.

    L_z = r_x * v_y - r_y * v_x
    Returns dict {eid: L_z}.
    """
    # System COM (average position, periodic-aware)
    s = field.side
    coords = []
    for ent in entities:
        c = field.node_coords[ent.node]
        coords.append(c)

    # Use first entity as reference for periodic wrapping
    ref = coords[0]
    com = [0.0, 0.0, 0.0]
    for c in coords:
        dx = c[0] - ref[0]
        dy = c[1] - ref[1]
        dz = c[2] - ref[2]
        if dx > s // 2: dx -= s
        if dx < -(s // 2): dx += s
        if dy > s // 2: dy -= s
        if dy < -(s // 2): dy += s
        if dz > s // 2: dz -= s
        if dz < -(s // 2): dz += s
        com[0] += ref[0] + dx
        com[1] += ref[1] + dy
        com[2] += ref[2] + dz
    n = len(entities)
    com = [c / n for c in com]

    result = {}
    for ent in entities:
        c = field.node_coords[ent.node]
        # r relative to COM (periodic wrapped)
        rx = c[0] - com[0]
        ry = c[1] - com[1]
        if rx > s // 2: rx -= s
        if rx < -(s // 2): rx += s
        if ry > s // 2: ry -= s
        if ry < -(s // 2): ry += s

        # v = internal direction (continuous, not quantized)
        vx = float(ent.internal_direction[0])
        vy = float(ent.internal_direction[1])

        result[ent.eid] = rx * vy - ry * vx

    return result


# ===========================================================================
# Trajectory Plotting
# ===========================================================================

def plot_trajectories(entities, field, filename, title="Trajectories (XY)"):
    """Plot entity trajectories projected onto XY plane."""
    fig, ax = plt.subplots(figsize=(8, 8))
    for ent in entities:
        if not ent.trajectory:
            continue
        xs = [field.node_coords[node][0] for _, node in ent.trajectory]
        ys = [field.node_coords[node][1] for _, node in ent.trajectory]
        ax.plot(xs, ys, '-', linewidth=0.8, alpha=0.7, label=ent.eid)
        # Mark start and end
        ax.plot(xs[0], ys[0], 'o', markersize=8)
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


def plot_internal_direction(entities, filename):
    """Plot internal direction angle (XY plane) over time for each entity."""
    fig, ax = plt.subplots(figsize=(12, 4))
    for ent in entities:
        if not ent.direction_history:
            continue
        ticks = [h[0] for h in ent.direction_history]
        angles = [math.atan2(h[2], h[1]) * 180 / math.pi
                  for h in ent.direction_history]
        ax.plot(ticks, angles, '-', linewidth=0.8, label=ent.eid)
    ax.set_xlabel('Tick')
    ax.set_ylabel('Direction angle (deg, XY plane)')
    ax.set_title('Internal Direction Rotation')
    ax.legend()
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


def plot_hop_histogram(entities, field, filename):
    """Histogram of hop directions for each entity. Orbits use all 4+ dirs."""
    labels = ['+X', '-X', '+Y', '-Y', '+Z', '-Z']
    dirs = [(1,0,0), (-1,0,0), (0,1,0), (0,-1,0), (0,0,1), (0,0,-1)]
    fig, axes = plt.subplots(1, len(entities), figsize=(5*len(entities), 4))
    if len(entities) == 1:
        axes = [axes]
    for ax, ent in zip(axes, entities):
        counts = [ent.hop_dir_counts.get(d, 0) for d in dirs]
        ax.bar(labels, counts)
        ax.set_title(f'{ent.eid} ({sum(counts)} hops)')
        ax.set_ylabel('Count')
    fig.suptitle('Hop Direction Histogram')
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification(seed=42):
    """Run all verification tests (v8 tests 1-6 + v9 momentum tests 7-10)."""
    print("\n=== v9 TAGGED GAMMA + MOMENTUM VERIFICATION ===\n")
    passed = 0
    failed = 0

    # --- v8 tests (1-6) ---

    print("Test 1: Per-entity conservation (1000 ticks)")
    f = TaggedGammaField(1000, k=6, G=10.0, seed=seed, entity_ids=['A', 'B'])
    c = f.n_nodes // 2
    f.tagged['A'][c] = 500
    f.tagged['B'][c + 10] = 300
    f.sync_total()
    init_A, init_B = f.tagged_total('A'), f.tagged_total('B')
    for _ in range(1000):
        f.spread()
    if f.tagged_total('A') == init_A and f.tagged_total('B') == init_B:
        print(f"  PASS")
        passed += 1
    else:
        print(f"  FAIL: A={init_A}->{f.tagged_total('A')}, B={init_B}->{f.tagged_total('B')}")
        failed += 1

    print("Test 2: Total conservation")
    if f.total_gamma() == init_A + init_B:
        print(f"  PASS")
        passed += 1
    else:
        print(f"  FAIL")
        failed += 1

    print("Test 3: No negatives (500 ticks)")
    f3 = TaggedGammaField(1000, k=6, G=5.0, seed=seed, entity_ids=['X'])
    f3.tagged['X'][0] = 200
    f3.sync_total()
    neg = False
    for _ in range(500):
        f3.spread()
        if np.any(f3.tagged['X'] < 0):
            neg = True
            break
    print(f"  {'PASS' if not neg else 'FAIL'}")
    passed += 0 if neg else 1
    failed += 1 if neg else 0

    print("Test 4: Reproducibility")
    f4a = TaggedGammaField(1000, k=6, G=10.0, seed=99, entity_ids=['A'])
    f4a.tagged['A'][50] = 100
    f4a.sync_total()
    for _ in range(200):
        f4a.spread()
    f4b = TaggedGammaField(1000, k=6, G=10.0, seed=99, entity_ids=['A'])
    f4b.tagged['A'][50] = 100
    f4b.sync_total()
    for _ in range(200):
        f4b.spread()
    if np.array_equal(f4a.tagged['A'], f4b.tagged['A']):
        print("  PASS")
        passed += 1
    else:
        print("  FAIL")
        failed += 1

    print("Test 5: Peak stability (G=10, 500 ticks)")
    f5 = TaggedGammaField(8000, k=6, G=10.0, seed=seed, entity_ids=['A'])
    center5 = f5.n_nodes // 2
    f5.initialize_tagged_peak('A', center5, 1000, smooth_ticks=10)
    for _ in range(500):
        f5.spread()
    peak_val = f5.tagged['A'][f5.tagged_peak_node('A')]
    mean_val = f5.tagged_total('A') / f5.n_nodes
    ratio = peak_val / max(mean_val, 0.001)
    if ratio > 10:
        print(f"  PASS: ratio={ratio:.0f}")
        passed += 1
    else:
        print(f"  FAIL: ratio={ratio:.0f}")
        failed += 1

    print("Test 6: External gamma correctness")
    f6 = TaggedGammaField(1000, k=6, G=10.0, seed=seed, entity_ids=['A', 'B'])
    f6.tagged['A'][100] = 500
    f6.tagged['B'][200] = 300
    f6.sync_total()
    ok = (f6.external_gamma(100, 'A') == 0 and
          f6.external_gamma(200, 'B') == 0 and
          f6.external_gamma(100, 'B') == 500)
    print(f"  {'PASS' if ok else 'FAIL'}")
    passed += 1 if ok else 0
    failed += 0 if ok else 1

    # --- v9 continuous direction tests (7-10) ---

    print("\nTest 7: Straight flight (no gradient -> keep direction)")
    f7 = TaggedGammaField(8000, k=6, G=10.0, seed=seed, entity_ids=['A'])
    center7 = f7.n_nodes // 2
    f7.tagged['A'][center7] = 100
    f7.sync_total()
    ent7 = Entity('A', center7, commit_mass=1)
    ent7.internal_direction = np.array([1.0, 0.0, 0.0])  # heading +X
    # With only own gamma (external=0), nudge=0, direction unchanged
    moved = ent7.advance(f7)
    if moved:
        d = f7.direction_vector(center7, ent7.node)
        if d[0] == 1 and d[1] == 0 and d[2] == 0:
            print(f"  PASS: moved to +X, dir={ent7.internal_direction}")
            passed += 1
        else:
            print(f"  FAIL: moved in {d}, expected +X")
            failed += 1
    else:
        print(f"  FAIL: didn't move")
        failed += 1

    print("Test 8: Gradual deflection (spread gradient rotates from +X)")
    # Place B's gamma at +Y offset and spread to create smooth gradient
    f8 = TaggedGammaField(8000, k=6, G=0.0, seed=seed, entity_ids=['A', 'B'])
    center8 = f8.n_nodes // 2
    coord8 = f8.node_coords[center8]
    s8 = f8.side
    # Place B's gamma 3 hops in +Y from center, spread to create smooth field
    y_coord8 = (coord8[0], (coord8[1] + 3) % s8, coord8[2])
    y_node8 = f8.coord_to_node[y_coord8]
    f8.tagged['B'][y_node8] = 10000
    f8.sync_total()
    # Spread to create gradient field (G=0 → uniform spread)
    for _ in range(50):
        f8.spread()
    ent8 = Entity('A', center8, commit_mass=5)  # nudge = 0.2 per hop
    ent8.internal_direction = np.array([1.0, 0.0, 0.0])  # heading +X
    # With spread gamma, gradient should persist as entity moves
    hop_dirs = []
    for i in range(50):  # 50 ticks = 10 hops at cm=5
        moved = ent8.advance(f8)
        if moved:
            d = f8.direction_vector(ent8.prev_node, ent8.node)
            hop_dirs.append(d)
    angle = math.atan2(ent8.internal_direction[1], ent8.internal_direction[0])
    angle_deg = angle * 180 / math.pi
    if angle_deg > 10:  # gradient nudges should rotate direction toward +Y
        switched = any(d[1] != 0 for d in hop_dirs)
        print(f"  PASS: angle={angle_deg:.1f}° after {len(hop_dirs)} hops, "
              f"hop_switch={switched}")
        passed += 1
    else:
        print(f"  FAIL: angle={angle_deg:.1f}° (expected >10°)")
        failed += 1

    print("Test 9: Direction rotation toward spread gamma source")
    # Place mass at center and spread to create radial gradient field
    f9 = TaggedGammaField(8000, k=6, G=0.0, seed=seed, entity_ids=['A', 'B'])
    center9 = f9.n_nodes // 2
    coord9 = f9.node_coords[center9]
    s9 = f9.side
    f9.tagged['B'][center9] = 20000
    f9.sync_total()
    # Spread to fill the lattice with gradient pointing toward center
    for _ in range(100):
        f9.spread()
    # Start entity 5 hops away in +X, heading +Y
    start_coord = ((coord9[0] + 5) % s9, coord9[1], coord9[2])
    start_node = f9.coord_to_node[start_coord]
    ent9 = Entity('A', start_node, commit_mass=5)
    ent9.internal_direction = np.array([0.0, 1.0, 0.0])  # heading +Y
    # Run for 100 hops, track direction angle
    angles = []
    for i in range(500):  # 500 ticks = 100 hops at cm=5
        ent9.advance(f9)
        if ent9.hops > 0 and ent9.hops % 10 == 0:
            a = math.atan2(ent9.internal_direction[1], ent9.internal_direction[0])
            angles.append(a * 180 / math.pi)
    if len(angles) >= 3:
        angle_range = max(angles) - min(angles)
        if angle_range > 5:  # at least some rotation
            print(f"  PASS: direction rotated {angle_range:.1f}° "
                  f"(start={angles[0]:.0f}°, end={angles[-1]:.0f}°)")
            passed += 1
        else:
            print(f"  FAIL: direction barely rotated ({angle_range:.1f}°), "
                  f"angles={[f'{a:.0f}' for a in angles[:5]]}")
            failed += 1
    else:
        print(f"  FAIL: not enough hops ({ent9.hops})")
        failed += 1

    print("Test 10: Mass controls turning radius")
    # Light entity (cm=1, nudge=1.0) vs heavy (cm=10, nudge=0.1)
    # Both start +X with spread +Y gradient. Light turns faster.
    def count_hops_to_turn(cm, seed_val):
        ft = TaggedGammaField(8000, k=6, G=0.0, seed=seed_val, entity_ids=['A', 'B'])
        ct = ft.n_nodes // 2
        cc = ft.node_coords[ct]
        st = ft.side
        # Place gamma 3 hops in +Y and spread
        yc = (cc[0], (cc[1] + 3) % st, cc[2])
        yn = ft.coord_to_node[yc]
        ft.tagged['B'][yn] = 10000
        ft.sync_total()
        for _ in range(50):
            ft.spread()
        ent = Entity('A', ct, commit_mass=cm)
        ent.internal_direction = np.array([1.0, 0.0, 0.0])
        for i in range(cm * 200):  # enough ticks
            ent.advance(ft)
            if ent.hops > 0:
                d = ft.direction_vector(ent.prev_node, ent.node)
                if d[1] != 0:  # first hop in Y direction
                    return ent.hops
        return -1

    light_hops = count_hops_to_turn(1, seed)
    heavy_hops = count_hops_to_turn(10, seed)
    if light_hops > 0 and heavy_hops > 0 and heavy_hops > light_hops:
        print(f"  PASS: light turns in {light_hops} hops, heavy in {heavy_hops}")
        passed += 1
    elif light_hops > 0 and heavy_hops == -1:
        print(f"  PASS: light turns in {light_hops} hops, heavy never turns")
        passed += 1
    else:
        print(f"  FAIL: light={light_hops}, heavy={heavy_hops}")
        failed += 1

    print(f"\n=== RESULTS: {passed}/{passed+failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 1: Single Peak Sanity
# ===========================================================================

def experiment_phase1(n_nodes=8000, G=10.0, mass=1000, ticks=5000, seed=42):
    """Single tagged peak stability."""
    print("=" * 70)
    print("PHASE 1: Single Tagged Peak Stability")
    print("=" * 70)

    field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed, entity_ids=['A'])
    nodes = field.place_peaks_equilateral(separation=10, n_peaks=1)
    center = nodes[0]
    field.initialize_tagged_peak('A', center, mass, smooth_ticks=10)

    init_total = field.tagged_total('A')
    print(f"\n  Initial: total={init_total}")

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        if (tick + 1) % 1000 == 0:
            total = field.tagged_total('A')
            peak_val = field.tagged['A'][field.tagged_peak_node('A')]
            elapsed = time.time() - t0
            print(f"    Tick {tick+1:5d}: total={total}, peak={peak_val} ({elapsed:.1f}s)")

    print(f"\n  Conservation: {'PASS' if field.tagged_total('A') == init_total else 'FAIL'}")


# ===========================================================================
# Phase 2: Two-Body
# ===========================================================================

def experiment_phase2(n_nodes=8000, G=10.0, mass=1000, commit_mass=5,
                      separation=10, ticks=50000, seed=42,
                      initial_momentum='none', tag=''):
    """Two-body test with optional initial momentum."""
    label = f"Phase 2 ({initial_momentum})"
    print("=" * 70)
    print(f"PHASE 2: Two-Body — {initial_momentum} momentum")
    print("=" * 70)
    print(f"\n  G={G}, mass={mass}, commit_mass={commit_mass}, "
          f"sep={separation}, ticks={ticks}")

    entity_ids = ['A', 'B']
    field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                             entity_ids=entity_ids)
    nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)
    field.initialize_tagged_peaks(
        {'A': nodes[0], 'B': nodes[1]}, mass, smooth_ticks=10)

    entities = [
        Entity('A', nodes[0], commit_mass=commit_mass),
        Entity('B', nodes[1], commit_mass=commit_mass),
    ]

    # Set initial direction
    if initial_momentum == 'perpendicular':
        # Peaks are along X axis. Give A direction +Y, B direction -Y.
        entities[0].internal_direction = np.array([0.0, 1.0, 0.0])
        entities[1].internal_direction = np.array([0.0, -1.0, 0.0])
        print(f"  Initial direction: A=(0,1,0), B=(0,-1,0)")

    init_dist = field.hop_distance(entities[0].node, entities[1].node)
    init_total = field.total_gamma()
    print(f"  Initial distance: {init_dist} hops")
    print(f"  Initial total gamma: {init_total}")

    # Run
    diag_interval = max(ticks // 50, 1)
    record_interval = max(ticks // 500, 1)
    distances = []
    ang_mom_records = []
    hop_counts = {'A': 0, 'B': 0}

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        for ent in entities:
            moved = ent.advance(field, tick)
            if moved:
                hop_counts[ent.eid] += 1

        # Record trajectory frequently
        if (tick + 1) % record_interval == 0:
            for ent in entities:
                ent.record(tick + 1)

        # Diagnostics less frequently
        if (tick + 1) % diag_interval == 0:
            d = field.hop_distance(entities[0].node, entities[1].node)
            distances.append((tick + 1, d))

            L = compute_angular_momentum(entities, field)
            L_total = sum(L.values())
            ang_mom_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 5) == 0:
                print(f"    Tick {tick+1:6d}: dist={d:3d} "
                      f"hops_A={hop_counts['A']} hops_B={hop_counts['B']} "
                      f"L_total={L_total:+.1f} ({elapsed:.1f}s)")

    # Results
    final_dist = field.hop_distance(entities[0].node, entities[1].node)
    print(f"\n  Final distance: {init_dist} -> {final_dist} hops")
    print(f"  Total hops: A={hop_counts['A']}, B={hop_counts['B']}")
    print(f"  Conservation: {field.total_gamma()} "
          f"(drift={abs(field.total_gamma() - init_total)})")

    if final_dist < init_dist:
        print(f"  ** ATTRACTION: distance decreased by {init_dist - final_dist} hops **")
    elif final_dist > init_dist:
        print(f"  Distance increased by {final_dist - init_dist} hops")

    # Check for oscillation
    if len(distances) > 10:
        dists_only = [d[1] for d in distances]
        d_min = min(dists_only)
        d_max = max(dists_only)
        if d_min < init_dist and d_max > init_dist:
            print(f"  ** OSCILLATION DETECTED: range [{d_min}, {d_max}] "
                  f"around initial {init_dist} **")

    # Plots
    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    # Distance plot
    if distances:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        ticks_arr = [d[0] for d in distances]
        dists_arr = [d[1] for d in distances]
        ax1.plot(ticks_arr, dists_arr, 'b-', linewidth=1)
        ax1.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.5)
        ax1.set_ylabel('Hop distance')
        ax1.set_title(f'Two-Body ({initial_momentum}): G={G}, mass={mass}, '
                       f'commit_mass={commit_mass}')
        ax1.grid(True, alpha=0.3)

        # Angular momentum
        if ang_mom_records:
            ax2.plot([r[0] for r in ang_mom_records],
                     [r[1] for r in ang_mom_records], 'r-', linewidth=1)
            ax2.set_xlabel('Tick')
            ax2.set_ylabel('Total L_z')
            ax2.set_title('Angular Momentum')
            ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase2_distance{suffix}.png', dpi=150)
        plt.close(fig)
        print(f"  Plot: {RESULTS_DIR / f'phase2_distance{suffix}.png'}")

    # Trajectory plot
    if any(ent.trajectory for ent in entities):
        plot_trajectories(entities, field,
                          RESULTS_DIR / f'phase2_trajectory{suffix}.png',
                          f'Trajectories ({initial_momentum})')
        print(f"  Plot: {RESULTS_DIR / f'phase2_trajectory{suffix}.png'}")

    # Internal direction angle plot
    if any(ent.direction_history for ent in entities):
        plot_internal_direction(entities,
                                RESULTS_DIR / f'phase2_direction{suffix}.png')
        print(f"  Plot: {RESULTS_DIR / f'phase2_direction{suffix}.png'}")

    # Hop direction histogram
    if any(ent.trajectory for ent in entities):
        plot_hop_histogram(entities, field,
                           RESULTS_DIR / f'phase2_hophist{suffix}.png')
        print(f"  Plot: {RESULTS_DIR / f'phase2_hophist{suffix}.png'}")

    return distances


# ===========================================================================
# Phase 3: Three-Body
# ===========================================================================

def experiment_phase3(n_nodes=8000, G=10.0, mass=1000, commit_mass=5,
                      separation=10, ticks=100000, seed=42,
                      initial_momentum='none', tag=''):
    """Three-body dynamics with optional tangential momentum."""
    print("=" * 70)
    print(f"PHASE 3: Three-Body — {initial_momentum} momentum")
    print("=" * 70)
    print(f"\n  G={G}, mass={mass}, commit_mass={commit_mass}, "
          f"sep={separation}, ticks={ticks}")

    entity_ids = ['A', 'B', 'C']
    field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                             entity_ids=entity_ids)
    nodes = field.place_peaks_equilateral(separation=separation, n_peaks=3)
    field.initialize_tagged_peaks(
        {'A': nodes[0], 'B': nodes[1], 'C': nodes[2]}, mass, smooth_ticks=10)

    entities = [
        Entity('A', nodes[0], commit_mass=commit_mass),
        Entity('B', nodes[1], commit_mass=commit_mass),
        Entity('C', nodes[2], commit_mass=commit_mass),
    ]

    # Set initial tangential direction
    if initial_momentum == 'tangential':
        # Equilateral triangle: A at center, B at +X, C at +X/2,+Y/2
        # Tangential = perpendicular to line from entity to centroid
        # Simple approximation for lattice: A→+Y, B→-Y, C→-X
        entities[0].internal_direction = np.array([0.0, 1.0, 0.0])
        entities[1].internal_direction = np.array([0.0, -1.0, 0.0])
        entities[2].internal_direction = np.array([-1.0, 0.0, 0.0])
        print(f"  Tangential direction: A=(0,1,0), B=(0,-1,0), C=(-1,0,0)")

    init_total = field.total_gamma()
    print(f"  Initial total gamma: {init_total}")

    diag_interval = max(ticks // 50, 1)
    record_interval = max(ticks // 500, 1)
    records = []
    ang_mom_records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        for ent in entities:
            ent.advance(field, tick)

        if (tick + 1) % record_interval == 0:
            for ent in entities:
                ent.record(tick + 1)

        if (tick + 1) % diag_interval == 0:
            d_AB = field.hop_distance(entities[0].node, entities[1].node)
            d_AC = field.hop_distance(entities[0].node, entities[2].node)
            d_BC = field.hop_distance(entities[1].node, entities[2].node)
            records.append({
                'tick': tick + 1,
                'd_AB': d_AB, 'd_AC': d_AC, 'd_BC': d_BC,
            })

            L = compute_angular_momentum(entities, field)
            L_total = sum(L.values())
            ang_mom_records.append((tick + 1, L_total))

            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 5) == 0:
                print(f"    Tick {tick+1:7d}: AB={d_AB} AC={d_AC} BC={d_BC} "
                      f"L={L_total:+.1f} ({elapsed:.1f}s)")

    total = field.total_gamma()
    print(f"\n  Final total: {total} (drift={abs(total - init_total)})")
    if records:
        last = records[-1]
        print(f"  AB: {records[0]['d_AB']} -> {last['d_AB']}")
        print(f"  AC: {records[0]['d_AC']} -> {last['d_AC']}")
        print(f"  BC: {records[0]['d_BC']} -> {last['d_BC']}")

    suffix = f"_{tag}" if tag else f"_{initial_momentum}"

    # Distance + angular momentum plot
    if records:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        ticks_arr = [r['tick'] for r in records]
        ax1.plot(ticks_arr, [r['d_AB'] for r in records], label='A-B')
        ax1.plot(ticks_arr, [r['d_AC'] for r in records], label='A-C')
        ax1.plot(ticks_arr, [r['d_BC'] for r in records], label='B-C')
        ax1.set_ylabel('Hop distance')
        ax1.set_title(f'Three-Body ({initial_momentum}): G={G}, mass={mass}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        if ang_mom_records:
            ax2.plot([r[0] for r in ang_mom_records],
                     [r[1] for r in ang_mom_records], 'r-')
            ax2.set_xlabel('Tick')
            ax2.set_ylabel('Total L_z')
            ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(RESULTS_DIR / f'phase3{suffix}.png', dpi=150)
        plt.close(fig)

    # Trajectory
    if any(ent.trajectory for ent in entities):
        plot_trajectories(entities, field,
                          RESULTS_DIR / f'phase3_trajectory{suffix}.png',
                          f'Three-Body Trajectories ({initial_momentum})')

    return records


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v9: Momentum as Identity Vector')
    parser.add_argument('--verify', action='store_true')
    parser.add_argument('--phase1', action='store_true')
    parser.add_argument('--phase2', action='store_true')
    parser.add_argument('--phase3', action='store_true')

    parser.add_argument('--n-nodes', type=int, default=8000)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--mass', type=int, default=1000)
    parser.add_argument('--commit-mass', type=int, default=5)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--seed', type=int, default=42)
    parser.add_argument('--initial-momentum',
                        choices=['none', 'perpendicular', 'tangential'],
                        default='none')
    parser.add_argument('--tag', type=str, default='',
                        help='Suffix for output filenames')

    args = parser.parse_args()

    if args.verify:
        run_verification(seed=args.seed)
    if args.phase1:
        experiment_phase1(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                          ticks=args.ticks, seed=args.seed)
    if args.phase2:
        experiment_phase2(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          seed=args.seed,
                          initial_momentum=args.initial_momentum,
                          tag=args.tag)
    if args.phase3:
        experiment_phase3(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          seed=args.seed,
                          initial_momentum=args.initial_momentum,
                          tag=args.tag)

    if not any([args.verify, args.phase1, args.phase2, args.phase3]):
        print("No experiment selected. Use --help for options.")


if __name__ == '__main__':
    main()
