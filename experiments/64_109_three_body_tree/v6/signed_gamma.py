"""v6 Signed Gamma: Dipole patterns on a graph.

The scalar gamma model proved self-binding, conservation, and radiation.
But peaks can't move because a symmetric positive scalar has no direction.

Change gamma from scalar to signed: each node holds a value in [-M, +M].
Self-gravitation operates on |gamma|: high |gamma| -> low spread.

Movement mechanism: asymmetry of signed pattern IS momentum.
    Symmetric signed peak (monopole) = stationary particle
    Asymmetric signed peak (dipole) = moving particle

A signed peak is a trit pattern:
    +gamma region (positive core)
    -gamma region (negative shell/wing)
    ~0 region (background)

Core physics:
    alpha_eff(node) = alpha / (1 + G * |gamma[node]|)   # absolute value!
    outflow = alpha_eff * gamma                          # signed
    inflow  = A @ (outflow / degrees)
    gamma_new = (gamma - outflow) + inflow               # exact conservation

Conservation:
    Total signed gamma is EXACTLY conserved (algebraic proof same as scalar).
    Total |gamma| is NOT conserved -- annihilation between +/- reduces it.

Usage:
    python signed_gamma.py --verify                # run tests
    python signed_gamma.py --test-monopole         # monopole stability
    python signed_gamma.py --test-dipole           # does dipole drift?
    python signed_gamma.py --test-attraction       # two-body attraction

February 2026
"""

import argparse
import json
import time
from collections import deque
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gamma_field import SelfGravitatingField, RESULTS_DIR, make_serializable


# ===========================================================================
# SignedGammaField
# ===========================================================================

class SignedGammaField(SelfGravitatingField):
    """Gamma field with signed values [-M, +M].

    Self-gravitation operates on |gamma|. Signs are preserved through spread.
    Positive nodes send positive gamma, negative nodes send negative gamma.
    The RATE depends on |gamma|: high magnitude resists spreading.

    Total signed gamma is exactly conserved.
    Total |gamma| can decrease (annihilation when + meets -).
    """

    def spread(self):
        """Nonlinear spread with |gamma| self-gravitation.

        alpha_eff = alpha / (1 + G * |gamma|)
        outflow = alpha_eff * gamma           (signed!)
        per_edge = outflow / degrees
        inflow = A @ per_edge
        gamma_new = (gamma - outflow) + inflow

        Conservation: sum(outflow) = sum(inflow) algebraically.
        """
        alpha_eff = self.alpha / (1.0 + self.G * np.abs(self.gamma))
        outflow = alpha_eff * self.gamma
        per_edge = outflow / self.degrees
        inflow = self.A @ per_edge
        self.gamma = (self.gamma - outflow) + inflow

    def total_signed_gamma(self):
        """Total signed gamma (conserved quantity)."""
        return float(np.sum(self.gamma))

    def total_abs_gamma(self):
        """Total |gamma| (can decrease through annihilation)."""
        return float(np.sum(np.abs(self.gamma)))

    # --- Signed initialization ---------------------------------------------

    def initialize_monopole(self, center, mass, neg_frac=0.5,
                            neg_radius=2, smooth_ticks=3):
        """Symmetric signed pattern: positive core, negative shell.

        Places +mass at center. Distributes -mass*neg_frac uniformly
        over shell nodes at distance 1..neg_radius from center.
        Net charge = mass * (1 - neg_frac).

        Light smoothing with G=0 to avoid delta-spike artifacts.
        """
        self.gamma[center] += mass

        # BFS to find shell nodes
        shell_nodes = []
        visited = {center}
        queue = deque([(center, 0)])
        while queue:
            node, dist = queue.popleft()
            if 1 <= dist <= neg_radius:
                shell_nodes.append(node)
            if dist < neg_radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        if shell_nodes:
            neg_per_node = mass * neg_frac / len(shell_nodes)
            for node in shell_nodes:
                self.gamma[node] -= neg_per_node

        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def initialize_dipole(self, center, mass, direction='x',
                          neg_frac=0.8, smooth_ticks=3):
        """Asymmetric signed pattern along a lattice axis.

        Places +mass at center. Places -mass*neg_frac on nodes in the
        NEGATIVE direction (behind). This creates asymmetry that should
        push the pattern in the POSITIVE direction.

        Net charge = mass * (1 - neg_frac).
        """
        assert hasattr(self, 'node_coords'), \
            "Dipole initialization requires lattice graph"
        center_coord = self.node_coords[center]
        axis = {'x': 0, 'y': 1, 'z': 2}[direction]

        self.gamma[center] += mass

        # Find nodes within 2 hops that are in the -direction half
        neg_nodes = []
        visited = {center}
        queue = deque([(center, 0)])
        while queue:
            node, dist = queue.popleft()
            if dist > 0:
                coord = self.node_coords[node]
                delta = coord[axis] - center_coord[axis]
                # Handle periodic boundary
                if delta > self.side // 2:
                    delta -= self.side
                if delta < -self.side // 2:
                    delta += self.side
                if delta < 0:
                    neg_nodes.append(node)
            if dist < 2:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        if neg_nodes:
            neg_per = mass * neg_frac / len(neg_nodes)
            for node in neg_nodes:
                self.gamma[node] -= neg_per

        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    # --- Signed peak detection ---------------------------------------------

    def find_peaks_signed(self, min_abs_gamma=None):
        """Find peaks by |gamma| -- local maxima of absolute value.

        Returns list of (node, gamma_value, abs_gamma) sorted by
        |gamma| descending.
        """
        abs_gamma = np.abs(self.gamma)

        if min_abs_gamma is None:
            total_abs = self.total_abs_gamma()
            if total_abs > 0:
                min_abs_gamma = total_abs / self.n_nodes * 5.0
            else:
                min_abs_gamma = 0.0

        peaks = []
        for node in range(self.n_nodes):
            ag = abs_gamma[node]
            if ag < min_abs_gamma:
                continue
            is_peak = True
            for nb in self.neighbors[node]:
                if abs_gamma[nb] >= ag:
                    is_peak = False
                    break
            if is_peak:
                peaks.append((node, self.gamma[node], ag))

        return sorted(peaks, key=lambda x: -x[2])

    # --- Center of mass tracking -------------------------------------------

    def center_of_abs_gamma(self, ref_node, radius=10):
        """Compute center of |gamma| mass in lattice coords, relative to ref.

        Returns ((dx, dy, dz), total_weight) where dx,dy,dz are the
        displacement of the |gamma| center from ref_node.
        """
        assert hasattr(self, 'node_coords'), "Requires lattice graph"
        ref_coord = self.node_coords[ref_node]
        s = self.side

        visited = {ref_node}
        queue = deque([(ref_node, 0)])
        total_w = 0.0
        wx, wy, wz = 0.0, 0.0, 0.0

        while queue:
            node, dist = queue.popleft()
            w = abs(self.gamma[node])
            if w > 0:
                coord = self.node_coords[node]
                # Relative coords with periodic wrapping
                dx = coord[0] - ref_coord[0]
                dy = coord[1] - ref_coord[1]
                dz = coord[2] - ref_coord[2]
                if dx > s // 2: dx -= s
                if dx < -(s // 2): dx += s
                if dy > s // 2: dy -= s
                if dy < -(s // 2): dy += s
                if dz > s // 2: dz -= s
                if dz < -(s // 2): dz += s

                wx += w * dx
                wy += w * dy
                wz += w * dz
                total_w += w

            if dist < radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        if total_w > 0:
            wx /= total_w
            wy /= total_w
            wz /= total_w

        return (wx, wy, wz), total_w

    def signed_radial_profile(self, center, max_radius=10):
        """Signed gamma as function of hop distance from center.

        Returns list of dicts with: distance, mean_gamma, mean_abs_gamma,
        max_abs_gamma, n_nodes.
        """
        visited = {center}
        queue = deque([(center, 0)])
        shells = {}

        while queue:
            node, dist = queue.popleft()
            if dist not in shells:
                shells[dist] = []
            shells[dist].append(self.gamma[node])
            if dist < max_radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        profile = []
        for d in sorted(shells.keys()):
            vals = np.array(shells[d])
            profile.append({
                'distance': d,
                'mean_gamma': float(np.mean(vals)),
                'mean_abs_gamma': float(np.mean(np.abs(vals))),
                'max_abs_gamma': float(np.max(np.abs(vals))),
                'n_nodes': len(vals),
            })
        return profile


# ===========================================================================
# Verification tests
# ===========================================================================

def run_verification():
    """Run all signed gamma verification tests."""
    print("\n=== SIGNED GAMMA VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # ------------------------------------------------------------------
    # Test 1: Signed total conserved (G=0)
    # ------------------------------------------------------------------
    print("Test 1: Signed total conservation (G=0)")
    f1 = SignedGammaField(1000, k=6, G=0.0)
    c1 = f1.n_nodes // 2
    f1.gamma[c1] = 500.0
    # Place some negative gamma nearby
    for nb in f1.neighbors[c1][:3]:
        f1.gamma[nb] = -50.0
    initial_signed = f1.total_signed_gamma()
    for _ in range(500):
        f1.spread()
    final_signed = f1.total_signed_gamma()
    drift = abs(final_signed - initial_signed) / abs(initial_signed)
    if drift < 1e-10:
        print(f"  PASS: signed drift = {drift:.2e}")
        passed += 1
    else:
        print(f"  FAIL: signed drift = {drift:.2e}")
        failed += 1

    # ------------------------------------------------------------------
    # Test 2: Signed total conserved (G>0)
    # ------------------------------------------------------------------
    print("Test 2: Signed total conservation (G=5.0)")
    f2 = SignedGammaField(1000, k=6, G=5.0)
    c2 = f2.n_nodes // 2
    f2.gamma[c2] = 500.0
    for nb in f2.neighbors[c2][:3]:
        f2.gamma[nb] = -50.0
    initial_signed2 = f2.total_signed_gamma()
    for _ in range(500):
        f2.spread()
    final_signed2 = f2.total_signed_gamma()
    drift2 = abs(final_signed2 - initial_signed2) / abs(initial_signed2)
    if drift2 < 1e-10:
        print(f"  PASS: signed drift = {drift2:.2e}")
        passed += 1
    else:
        print(f"  FAIL: signed drift = {drift2:.2e}")
        failed += 1

    # ------------------------------------------------------------------
    # Test 3: Monopole |gamma| peak holds with G>0
    # ------------------------------------------------------------------
    print("Test 3: Monopole |gamma| peak stability (G=50)")
    f3 = SignedGammaField(8000, k=6, G=50.0)
    c3 = f3.n_nodes // 2
    f3.initialize_monopole(c3, mass=500.0, neg_frac=0.5,
                           neg_radius=2, smooth_ticks=3)
    peak_before = float(np.max(np.abs(f3.gamma)))
    for _ in range(500):
        f3.spread()
    peak_after = float(np.max(np.abs(f3.gamma)))
    retention = peak_after / peak_before
    if retention > 0.7:
        print(f"  PASS: peak |gamma| retained {retention*100:.1f}% "
              f"({peak_before:.2f} -> {peak_after:.2f})")
        passed += 1
    else:
        print(f"  FAIL: peak |gamma| retained only {retention*100:.1f}%")
        failed += 1

    # ------------------------------------------------------------------
    # Test 4: Monopole is stationary (center doesn't drift)
    # ------------------------------------------------------------------
    print("Test 4: Monopole stationary (center doesn't drift)")
    f4 = SignedGammaField(8000, k=6, G=50.0)
    c4 = f4.n_nodes // 2
    f4.initialize_monopole(c4, mass=500.0, neg_frac=0.5,
                           neg_radius=2, smooth_ticks=3)
    com_before, _ = f4.center_of_abs_gamma(c4, radius=8)
    for _ in range(500):
        f4.spread()
    com_after, _ = f4.center_of_abs_gamma(c4, radius=8)
    drift_dist = np.sqrt(sum((a - b)**2 for a, b in
                              zip(com_after, com_before)))
    if drift_dist < 0.5:
        print(f"  PASS: center drift = {drift_dist:.4f} hops "
              f"({com_before} -> {com_after})")
        passed += 1
    else:
        print(f"  FAIL: center drift = {drift_dist:.4f} hops")
        failed += 1

    # ------------------------------------------------------------------
    # Test 5: Annihilation reduces total |gamma|
    # ------------------------------------------------------------------
    print("Test 5: Annihilation reduces total |gamma|")
    f5 = SignedGammaField(1000, k=6, G=0.0)
    c5 = f5.n_nodes // 2
    # Place + and - next to each other
    f5.gamma[c5] = 100.0
    nbs5 = f5.neighbors[c5]
    f5.gamma[nbs5[0]] = -100.0
    abs_before = f5.total_abs_gamma()
    for _ in range(50):
        f5.spread()
    abs_after = f5.total_abs_gamma()
    if abs_after < abs_before:
        print(f"  PASS: |gamma| decreased {abs_before:.1f} -> {abs_after:.1f} "
              f"({(1-abs_after/abs_before)*100:.1f}% annihilation)")
        passed += 1
    else:
        print(f"  FAIL: |gamma| did not decrease ({abs_before:.1f} -> {abs_after:.1f})")
        failed += 1

    # ------------------------------------------------------------------
    # Test 6: G=0 signed gamma disperses to zero
    # ------------------------------------------------------------------
    print("Test 6: G=0 signed gamma disperses")
    f6 = SignedGammaField(1000, k=6, G=0.0)
    c6 = f6.n_nodes // 2
    f6.gamma[c6] = 100.0
    f6.gamma[f6.neighbors[c6][0]] = -100.0
    # With G=0, both + and - should disperse and annihilate
    for _ in range(2000):
        f6.spread()
    max_abs = float(np.max(np.abs(f6.gamma)))
    # Net signed total is 0, so everything should approach 0
    if max_abs < 0.1:
        print(f"  PASS: max |gamma| = {max_abs:.6f} (dispersed)")
        passed += 1
    else:
        print(f"  FAIL: max |gamma| = {max_abs:.6f} (not fully dispersed)")
        failed += 1

    # ------------------------------------------------------------------
    # Test 7: No NaN/Inf
    # ------------------------------------------------------------------
    print("Test 7: No NaN/Inf in signed spread")
    f7 = SignedGammaField(1000, k=6, G=10.0)
    c7 = f7.n_nodes // 2
    f7.gamma[c7] = 1000.0
    for nb in f7.neighbors[c7]:
        f7.gamma[nb] = -200.0
    for _ in range(500):
        f7.spread()
    has_nan = np.any(np.isnan(f7.gamma))
    has_inf = np.any(np.isinf(f7.gamma))
    if not has_nan and not has_inf:
        print(f"  PASS: no NaN or Inf")
        passed += 1
    else:
        print(f"  FAIL: NaN={has_nan}, Inf={has_inf}")
        failed += 1

    print(f"\n=== RESULTS: {passed} passed, {failed} failed "
          f"out of {passed + failed} ===\n")
    return failed == 0


# ===========================================================================
# Experiment: Monopole stability
# ===========================================================================

def test_monopole(n_nodes=8000, G=50.0, mass=500.0, neg_frac=0.5,
                  ticks=2000, measure_interval=50):
    """Test signed monopole stability and stationarity."""
    print("=" * 70)
    print("SIGNED MONOPOLE STABILITY TEST")
    print("=" * 70)

    field = SignedGammaField(n_nodes, k=6, G=G)
    center = field.n_nodes // 2
    field.initialize_monopole(center, mass=mass, neg_frac=neg_frac,
                               neg_radius=2, smooth_ticks=3)

    init_signed = field.total_signed_gamma()
    init_abs = field.total_abs_gamma()
    print(f"\n  Initial: signed_total={init_signed:.4f}, "
          f"abs_total={init_abs:.4f}")

    # Initial profile
    profile_init = field.signed_radial_profile(center, max_radius=8)
    print("  Initial radial profile:")
    for p in profile_init[:6]:
        print(f"    d={p['distance']}: mean={p['mean_gamma']:.4f}, "
              f"|mean|={p['mean_abs_gamma']:.4f}")

    records = []
    t0 = time.time()

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            signed_total = field.total_signed_gamma()
            abs_total = field.total_abs_gamma()
            peak_abs = float(np.max(np.abs(field.gamma)))
            com, com_weight = field.center_of_abs_gamma(center, radius=8)
            com_dist = np.sqrt(com[0]**2 + com[1]**2 + com[2]**2)

            signed_drift = abs(signed_total - init_signed) / abs(init_signed) \
                if abs(init_signed) > 0 else 0.0
            abs_change = (abs_total - init_abs) / init_abs

            records.append({
                'tick': tick + 1,
                'signed_total': signed_total,
                'abs_total': abs_total,
                'peak_abs': peak_abs,
                'com_x': com[0], 'com_y': com[1], 'com_z': com[2],
                'com_dist': com_dist,
                'signed_drift': signed_drift,
                'abs_change': abs_change,
            })

            if (tick + 1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:5d}: peak|g|={peak_abs:.3f} "
                      f"com_drift={com_dist:.4f} "
                      f"signed_drift={signed_drift:.2e} "
                      f"|g|_change={abs_change*100:.2f}% "
                      f"({elapsed:.1f}s)")

    # Final state
    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    print(f"  Final signed total: {field.total_signed_gamma():.4f} "
          f"(init: {init_signed:.4f})")
    print(f"  Final |gamma| total: {field.total_abs_gamma():.4f} "
          f"(init: {init_abs:.4f})")
    final_com, _ = field.center_of_abs_gamma(center, radius=8)
    final_com_dist = np.sqrt(sum(c**2 for c in final_com))
    print(f"  Final COM drift: {final_com_dist:.4f} hops")

    # Final profile
    profile_final = field.signed_radial_profile(center, max_radius=8)
    print("  Final radial profile:")
    for p in profile_final[:6]:
        print(f"    d={p['distance']}: mean={p['mean_gamma']:.4f}, "
              f"|mean|={p['mean_abs_gamma']:.4f}")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: Peak |gamma| over time
    ax = axes[0, 0]
    ax.plot([r['tick'] for r in records],
            [r['peak_abs'] for r in records], 'b-', linewidth=0.5)
    ax.set_ylabel('Peak |gamma|')
    ax.set_title('Peak Stability')

    # Panel 2: COM drift
    ax = axes[0, 1]
    ax.plot([r['tick'] for r in records],
            [r['com_dist'] for r in records], 'r-', linewidth=0.5)
    ax.set_ylabel('COM drift (hops)')
    ax.set_title('Stationarity (COM drift from init)')

    # Panel 3: Conservation
    ax = axes[1, 0]
    ax.plot([r['tick'] for r in records],
            [r['signed_drift'] for r in records], 'b-', linewidth=0.5,
            label='Signed drift')
    ax.set_ylabel('Relative drift')
    ax.set_yscale('log')
    ax.set_title('Conservation')
    ax.set_xlabel('Tick')

    # Panel 4: |gamma| total (annihilation)
    ax = axes[1, 1]
    ax.plot([r['tick'] for r in records],
            [r['abs_total'] for r in records], 'g-', linewidth=0.5)
    ax.set_ylabel('Total |gamma|')
    ax.set_title('Annihilation (|gamma| total)')
    ax.set_xlabel('Tick')

    fig.suptitle(f'Signed Monopole: G={G}, mass={mass}, neg_frac={neg_frac}',
                 fontsize=14)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"signed_monopole_G{G}_m{mass}.png", dpi=150)
    plt.close()
    print(f"  Plot saved to: {RESULTS_DIR / f'signed_monopole_G{G}_m{mass}.png'}")

    return records


# ===========================================================================
# Experiment: Dipole drift
# ===========================================================================

def test_dipole(n_nodes=8000, G=50.0, mass=500.0, neg_frac=0.8,
                ticks=2000, measure_interval=50):
    """Test if asymmetric signed pattern (dipole) drifts."""
    print("=" * 70)
    print("SIGNED DIPOLE DRIFT TEST")
    print("=" * 70)

    field = SignedGammaField(n_nodes, k=6, G=G)
    center = field.n_nodes // 2
    field.initialize_dipole(center, mass=mass, direction='x',
                             neg_frac=neg_frac, smooth_ticks=3)

    init_signed = field.total_signed_gamma()
    init_abs = field.total_abs_gamma()
    print(f"\n  Initial: signed_total={init_signed:.4f}, "
          f"abs_total={init_abs:.4f}")

    # Initial profile along x-axis
    center_coord = field.node_coords[center]
    print(f"  Center at lattice coord: {center_coord}")

    records = []
    t0 = time.time()

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            signed_total = field.total_signed_gamma()
            abs_total = field.total_abs_gamma()
            peak_abs = float(np.max(np.abs(field.gamma)))
            com, com_weight = field.center_of_abs_gamma(center, radius=10)
            com_dist = np.sqrt(com[0]**2 + com[1]**2 + com[2]**2)

            # Also find the node with highest |gamma|
            peak_node = int(np.argmax(np.abs(field.gamma)))
            peak_coord = field.node_coords[peak_node]
            peak_dist = field.hop_distance(center, peak_node)

            records.append({
                'tick': tick + 1,
                'signed_total': signed_total,
                'abs_total': abs_total,
                'peak_abs': peak_abs,
                'peak_node': peak_node,
                'peak_dist_from_init': peak_dist,
                'com_x': com[0], 'com_y': com[1], 'com_z': com[2],
                'com_dist': com_dist,
            })

            if (tick + 1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:5d}: peak|g|={peak_abs:.3f} "
                      f"peak_node={peak_node} (d={peak_dist}) "
                      f"com=({com[0]:.3f},{com[1]:.3f},{com[2]:.3f}) "
                      f"com_dist={com_dist:.4f} "
                      f"({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")
    final_com, _ = field.center_of_abs_gamma(center, radius=10)
    final_com_dist = np.sqrt(sum(c**2 for c in final_com))
    print(f"  Final COM displacement: ({final_com[0]:.4f}, "
          f"{final_com[1]:.4f}, {final_com[2]:.4f})")
    print(f"  Final COM distance: {final_com_dist:.4f} hops")

    # Check if peak node moved
    final_peak_node = int(np.argmax(np.abs(field.gamma)))
    final_peak_dist = field.hop_distance(center, final_peak_node)
    print(f"  Peak node: {center} -> {final_peak_node} "
          f"(distance: {final_peak_dist})")

    if final_com_dist > 0.5 or final_peak_dist > 0:
        print("  ** DIPOLE DRIFT DETECTED **")
    else:
        print("  No significant drift")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    ax.plot([r['tick'] for r in records],
            [r['peak_abs'] for r in records], 'b-', linewidth=0.5)
    ax.set_ylabel('Peak |gamma|')
    ax.set_title('Peak Stability')

    ax = axes[0, 1]
    ax.plot([r['tick'] for r in records],
            [r['com_x'] for r in records], 'r-', linewidth=0.5,
            label='x')
    ax.plot([r['tick'] for r in records],
            [r['com_y'] for r in records], 'g-', linewidth=0.5,
            label='y')
    ax.plot([r['tick'] for r in records],
            [r['com_z'] for r in records], 'b-', linewidth=0.5,
            label='z')
    ax.set_ylabel('COM displacement')
    ax.set_title('Dipole Drift (COM components)')
    ax.legend()

    ax = axes[1, 0]
    ax.plot([r['tick'] for r in records],
            [r['com_dist'] for r in records], 'r-', linewidth=0.5)
    ax.set_ylabel('COM drift (hops)')
    ax.set_title('Total COM drift')
    ax.set_xlabel('Tick')

    ax = axes[1, 1]
    ax.plot([r['tick'] for r in records],
            [r['abs_total'] for r in records], 'g-', linewidth=0.5)
    ax.set_ylabel('Total |gamma|')
    ax.set_title('Annihilation')
    ax.set_xlabel('Tick')

    fig.suptitle(f'Signed Dipole: G={G}, mass={mass}, neg_frac={neg_frac}',
                 fontsize=14)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"signed_dipole_G{G}_m{mass}.png", dpi=150)
    plt.close()
    print(f"  Plot saved to: {RESULTS_DIR / f'signed_dipole_G{G}_m{mass}.png'}")

    return records


# ===========================================================================
# Experiment: Two-body attraction
# ===========================================================================

def test_attraction(n_nodes=8000, G=50.0, mass=500.0, neg_frac=0.5,
                    separation=10, ticks=2000, measure_interval=50):
    """Test if two signed monopoles attract each other."""
    print("=" * 70)
    print("SIGNED TWO-BODY ATTRACTION TEST")
    print("=" * 70)

    field = SignedGammaField(n_nodes, k=6, G=G)
    nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)

    # Initialize both as monopoles simultaneously
    # First place both positive cores
    field.gamma[nodes[0]] += mass
    field.gamma[nodes[1]] += mass

    # Place negative shells for both
    for center_node in nodes:
        shell_nodes = []
        visited = {center_node}
        queue = deque([(center_node, 0)])
        while queue:
            node, dist = queue.popleft()
            if 1 <= dist <= 2:
                shell_nodes.append(node)
            if dist < 2:
                for nb in field.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))
        if shell_nodes:
            neg_per = mass * neg_frac / len(shell_nodes)
            for node in shell_nodes:
                field.gamma[node] -= neg_per

    # Light smoothing
    saved_G = field.G
    field.G = 0.0
    for _ in range(3):
        field.spread()
    field.G = saved_G

    init_signed = field.total_signed_gamma()
    init_abs = field.total_abs_gamma()
    init_dist = field.hop_distance(nodes[0], nodes[1])

    print(f"\n  Initial: signed_total={init_signed:.4f}, "
          f"abs_total={init_abs:.4f}")
    print(f"  Initial distance: {init_dist} hops")
    print(f"  Peak A: gamma={field.gamma[nodes[0]]:.4f}")
    print(f"  Peak B: gamma={field.gamma[nodes[1]]:.4f}")

    records = []
    t0 = time.time()

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            signed_total = field.total_signed_gamma()
            abs_total = field.total_abs_gamma()

            # Find the two highest |gamma| peaks
            peaks = field.find_peaks_signed()
            if len(peaks) >= 2:
                p0, p1 = peaks[0][0], peaks[1][0]
                d = field.hop_distance(p0, p1)
            elif len(peaks) == 1:
                p0 = peaks[0][0]
                p1 = p0
                d = 0
            else:
                p0 = p1 = nodes[0]
                d = -1

            # COM for each peak
            com_a, _ = field.center_of_abs_gamma(nodes[0], radius=6)
            com_b, _ = field.center_of_abs_gamma(nodes[1], radius=6)
            # COM distance between the two patterns
            com_sep = np.sqrt(sum((a - b + (field.node_coords[nodes[0]][i]
                              - field.node_coords[nodes[1]][i]))**2
                              for i, (a, b) in enumerate(zip(com_a, com_b))))

            records.append({
                'tick': tick + 1,
                'signed_total': signed_total,
                'abs_total': abs_total,
                'peak_dist': d,
                'peak_a_node': p0,
                'peak_b_node': p1,
                'com_sep': com_sep,
            })

            if (tick + 1) % 500 == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:5d}: peak_dist={d} "
                      f"com_sep={com_sep:.3f} "
                      f"|g|_total={abs_total:.1f} "
                      f"({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s")

    # Final state
    peaks_final = field.find_peaks_signed()
    if len(peaks_final) >= 2:
        final_dist = field.hop_distance(peaks_final[0][0], peaks_final[1][0])
    else:
        final_dist = 0
    print(f"  Distance: {init_dist} -> {final_dist} hops")
    print(f"  Signed total: {field.total_signed_gamma():.4f} "
          f"(init: {init_signed:.4f})")
    print(f"  |gamma| total: {field.total_abs_gamma():.4f} "
          f"(init: {init_abs:.4f})")

    if final_dist < init_dist:
        print("  ** ATTRACTION DETECTED **")
    elif final_dist == init_dist:
        print("  No movement")
    else:
        print("  Repulsion?!")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ax = axes[0, 0]
    ax.plot([r['tick'] for r in records],
            [r['peak_dist'] for r in records], 'b-', linewidth=0.5)
    ax.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylabel('Peak distance (hops)')
    ax.set_title('Peak-to-Peak Distance')

    ax = axes[0, 1]
    ax.plot([r['tick'] for r in records],
            [r['com_sep'] for r in records], 'r-', linewidth=0.5)
    ax.set_ylabel('COM separation')
    ax.set_title('Center-of-Mass Separation')

    ax = axes[1, 0]
    ax.plot([r['tick'] for r in records],
            [r['abs_total'] for r in records], 'g-', linewidth=0.5)
    ax.set_ylabel('Total |gamma|')
    ax.set_title('Annihilation')
    ax.set_xlabel('Tick')

    ax = axes[1, 1]
    signed_drift = [abs(r['signed_total'] - init_signed) /
                    abs(init_signed) if abs(init_signed) > 0 else 0
                    for r in records]
    ax.plot([r['tick'] for r in records], signed_drift,
            'b-', linewidth=0.5)
    ax.set_ylabel('Signed drift')
    ax.set_yscale('log')
    ax.set_title('Conservation')
    ax.set_xlabel('Tick')

    fig.suptitle(f'Two-Body Signed: G={G}, mass={mass}, sep={separation}',
                 fontsize=14)
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"signed_attraction_G{G}_m{mass}.png", dpi=150)
    plt.close()
    print(f"  Plot saved to: {RESULTS_DIR / f'signed_attraction_G{G}_m{mass}.png'}")

    # Parameter sweep
    print("\n" + "=" * 70)
    print("G SWEEP (signed two-body, 500 ticks each)")
    print("=" * 70)

    for G_val in [10.0, 50.0, 100.0, 200.0]:
        f2 = SignedGammaField(n_nodes, k=6, G=G_val)
        n2 = f2.place_peaks_equilateral(separation=separation, n_peaks=2)
        # Initialize both monopoles
        for cn in n2:
            f2.gamma[cn] += mass
            shell = []
            vis = {cn}
            q = deque([(cn, 0)])
            while q:
                nd, dd = q.popleft()
                if 1 <= dd <= 2:
                    shell.append(nd)
                if dd < 2:
                    for nb in f2.neighbors[nd]:
                        if nb not in vis:
                            vis.add(nb)
                            q.append((nb, dd + 1))
            if shell:
                np_val = mass * neg_frac / len(shell)
                for nd in shell:
                    f2.gamma[nd] -= np_val
        f2.G = 0.0
        for _ in range(3):
            f2.spread()
        f2.G = G_val

        for _ in range(500):
            f2.spread()

        peaks2 = f2.find_peaks_signed()
        if len(peaks2) >= 2:
            d2 = f2.hop_distance(peaks2[0][0], peaks2[1][0])
        elif len(peaks2) == 1:
            d2 = 0
        else:
            d2 = -1
        abs_total2 = f2.total_abs_gamma()
        signed_total2 = f2.total_signed_gamma()
        print(f"  G={G_val:6.1f}: dist={init_dist}->{d2}, "
              f"peaks={len(peaks2)}, "
              f"|g|={abs_total2:.1f}, "
              f"signed={signed_total2:.1f}")

    return records


# ===========================================================================
# Neg-frac sweep: how does neg_frac affect behavior?
# ===========================================================================

def test_neg_frac_sweep(n_nodes=8000, G=50.0, mass=500.0, ticks=1000):
    """Sweep neg_frac to understand its role."""
    print("=" * 70)
    print("NEG_FRAC SWEEP (monopole stability)")
    print("=" * 70)

    results = []
    for nf in [0.0, 0.1, 0.3, 0.5, 0.7, 0.9, 1.0]:
        field = SignedGammaField(n_nodes, k=6, G=G)
        c = field.n_nodes // 2
        field.initialize_monopole(c, mass=mass, neg_frac=nf,
                                   neg_radius=2, smooth_ticks=3)

        init_signed = field.total_signed_gamma()
        init_abs = field.total_abs_gamma()
        peak_init = float(np.max(np.abs(field.gamma)))

        for _ in range(ticks):
            field.spread()

        final_signed = field.total_signed_gamma()
        final_abs = field.total_abs_gamma()
        peak_final = float(np.max(np.abs(field.gamma)))
        com, _ = field.center_of_abs_gamma(c, radius=8)
        com_dist = np.sqrt(sum(x**2 for x in com))

        results.append({
            'neg_frac': nf,
            'init_signed': init_signed,
            'final_signed': final_signed,
            'init_abs': init_abs,
            'final_abs': final_abs,
            'peak_init': peak_init,
            'peak_final': peak_final,
            'com_drift': com_dist,
        })

        print(f"  nf={nf:.1f}: peak {peak_init:.2f}->{peak_final:.2f} "
              f"({peak_final/peak_init*100:.0f}%), "
              f"|g| {init_abs:.0f}->{final_abs:.0f} "
              f"({final_abs/init_abs*100:.0f}%), "
              f"signed {init_signed:.1f}->{final_signed:.1f}, "
              f"com_drift={com_dist:.4f}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    nfs = [r['neg_frac'] for r in results]

    ax = axes[0]
    ax.plot(nfs, [r['peak_final']/r['peak_init']*100 for r in results],
            'bo-')
    ax.set_xlabel('neg_frac')
    ax.set_ylabel('Peak retention (%)')
    ax.set_title('Peak Stability vs neg_frac')

    ax = axes[1]
    ax.plot(nfs, [r['final_abs']/r['init_abs']*100 for r in results],
            'go-')
    ax.set_xlabel('neg_frac')
    ax.set_ylabel('|gamma| retention (%)')
    ax.set_title('Annihilation vs neg_frac')

    ax = axes[2]
    ax.plot(nfs, [r['com_drift'] for r in results], 'ro-')
    ax.set_xlabel('neg_frac')
    ax.set_ylabel('COM drift (hops)')
    ax.set_title('Stationarity vs neg_frac')

    plt.tight_layout()
    plt.savefig(RESULTS_DIR / f"signed_neg_frac_sweep_G{G}.png", dpi=150)
    plt.close()
    print(f"  Plot saved to: {RESULTS_DIR / f'signed_neg_frac_sweep_G{G}.png'}")

    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v6 Signed Gamma: Dipole patterns on a graph')

    parser.add_argument('--verify', action='store_true',
                        help='Run verification tests')
    parser.add_argument('--test-monopole', action='store_true',
                        help='Monopole stability test')
    parser.add_argument('--test-dipole', action='store_true',
                        help='Dipole drift test')
    parser.add_argument('--test-attraction', action='store_true',
                        help='Two-body attraction test')
    parser.add_argument('--test-neg-frac', action='store_true',
                        help='neg_frac sweep')
    parser.add_argument('--all', action='store_true',
                        help='Run all experiments')

    parser.add_argument('--n-nodes', type=int, default=8000)
    parser.add_argument('--G', type=float, default=50.0)
    parser.add_argument('--mass', type=float, default=500.0)
    parser.add_argument('--neg-frac', type=float, default=0.5)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--ticks', type=int, default=2000)
    parser.add_argument('--measure-interval', type=int, default=50)

    args = parser.parse_args()

    if args.verify:
        return 0 if run_verification() else 1

    if args.test_monopole or args.all:
        test_monopole(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                      neg_frac=args.neg_frac, ticks=args.ticks,
                      measure_interval=args.measure_interval)

    if args.test_dipole or args.all:
        test_dipole(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                    neg_frac=args.neg_frac, ticks=args.ticks,
                    measure_interval=args.measure_interval)

    if args.test_attraction or args.all:
        test_attraction(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                        neg_frac=args.neg_frac, separation=args.separation,
                        ticks=args.ticks,
                        measure_interval=args.measure_interval)

    if args.test_neg_frac or args.all:
        test_neg_frac_sweep(n_nodes=args.n_nodes, G=args.G,
                            mass=args.mass, ticks=args.ticks)

    if not any([args.test_monopole, args.test_dipole, args.test_attraction,
                args.test_neg_frac, args.all]):
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
