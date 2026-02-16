"""v6 Quantum Gamma: Integer Stochastic Field on a Graph.

The continuous self-gravitating field (gamma_field.py) proved self-binding
and conservation, but peaks cannot move because deterministic diffusion
distributes outflow symmetrically to ALL neighbors. Perfect symmetry = no force.

At Planck scale, gamma values are integers (natural numbers). A single quantum
cannot split into 1/6 going to each neighbor -- it goes to ONE neighbor. This:
1. Gives each quantum a DIRECTION when it moves
2. Creates stochastic fluctuations at cluster boundaries
3. Makes the cluster's center-of-mass do a Brownian random walk
4. With gravitational bias -> biased random walk = attraction

Core physics:
    alpha_eff(node) = alpha / (1 + G * gamma[node])
    n_leaving = Binomial(gamma[node], alpha_eff)        # how many quanta leave
    destination = Multinomial(n_leaving, neighbor_probs) # each goes to ONE neighbor

Conservation: exact by construction (integer quanta move, none created/destroyed).

Usage:
    python quantum_gamma.py --verify                     # run tests
    python quantum_gamma.py --brownian --mass 1000       # Brownian motion
    python quantum_gamma.py --attraction --G-attract 0.5 # two-body test
    python quantum_gamma.py --mass-sweep                 # diffusion vs mass

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
# QuantumGammaField
# ===========================================================================

class QuantumGammaField(SelfGravitatingField):
    """Integer stochastic gamma field on a graph.

    Each node holds a non-negative integer number of gamma quanta.
    Each tick, each quantum independently decides to stay or hop
    to one random neighbor. Self-gravitation: high-density nodes
    have lower probability of quanta leaving.

    Total gamma is exactly conserved (integer arithmetic, no rounding).
    """

    def __init__(self, *args, G_attract=0.0, **kwargs):
        super().__init__(*args, **kwargs)
        # Override gamma to integer type
        self.gamma = np.zeros(self.n_nodes, dtype=np.int64)
        self.G_attract = G_attract
        self.rng = np.random.default_rng(kwargs.get('seed', 42))

    def spread(self):
        """Stochastic integer spread.

        For each node:
            1. alpha_eff = alpha / (1 + G * gamma[node])
            2. n_leaving = Binomial(gamma[node], alpha_eff)
            3. Each leaving quantum goes to one random neighbor
               (uniform, or biased by G_attract * gamma[neighbor])
        """
        gamma_float = self.gamma.astype(np.float64)
        alpha_eff = self.alpha / (1.0 + self.G * gamma_float)
        # Clip probability to [0, 1]
        alpha_eff = np.clip(alpha_eff, 0.0, 1.0)

        # How many quanta leave each node
        n_leaving = self.rng.binomial(self.gamma, alpha_eff)

        gamma_new = self.gamma.copy()
        gamma_new -= n_leaving  # retained portion

        # Distribute leaving quanta to neighbors
        if self.G_attract == 0.0:
            self._distribute_uniform(n_leaving, gamma_new)
        else:
            self._distribute_biased(n_leaving, gamma_new)

        self.gamma = gamma_new

    def _distribute_uniform(self, n_leaving, gamma_new):
        """Distribute leaving quanta uniformly to random neighbors."""
        for i in range(self.n_nodes):
            if n_leaving[i] <= 0:
                continue
            nbs = self.neighbors[i]
            k = len(nbs)
            if k == 0:
                gamma_new[i] += n_leaving[i]  # no neighbors, keep
                continue
            probs = np.full(k, 1.0 / k)
            alloc = self.rng.multinomial(int(n_leaving[i]), probs)
            for j in range(k):
                gamma_new[nbs[j]] += alloc[j]

    def _distribute_biased(self, n_leaving, gamma_new):
        """Distribute leaving quanta biased toward high-gamma neighbors."""
        for i in range(self.n_nodes):
            if n_leaving[i] <= 0:
                continue
            nbs = self.neighbors[i]
            k = len(nbs)
            if k == 0:
                gamma_new[i] += n_leaving[i]
                continue
            # Weights: higher gamma neighbor = higher probability
            weights = np.array([1.0 + self.G_attract *
                                float(self.gamma[nb]) for nb in nbs])
            weights = np.maximum(weights, 1e-10)  # safety
            probs = weights / weights.sum()
            alloc = self.rng.multinomial(int(n_leaving[i]), probs)
            for j in range(k):
                gamma_new[nbs[j]] += alloc[j]

    def total_gamma(self):
        """Total gamma (exact integer sum)."""
        return int(np.sum(self.gamma))

    # --- Initialization ---------------------------------------------------

    def initialize_peak(self, center_node, total_mass, smooth_ticks=10):
        """Place integer quanta at center, smooth with stochastic G=0 spread.

        Each quantum independently random-walks for smooth_ticks steps.
        Result is a natural integer distribution (approximate Gaussian).
        """
        self.gamma[center_node] += int(total_mass)
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def initialize_two_peaks(self, separation, mass, smooth_ticks=10):
        """Initialize two equal peaks simultaneously."""
        nodes = self.place_peaks_equilateral(separation=separation, n_peaks=2)
        # Place both deltas before smoothing
        self.gamma[nodes[0]] += int(mass)
        self.gamma[nodes[1]] += int(mass)
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G
        return nodes

    # --- Peak detection (override for integer) ----------------------------

    def find_peak_node(self):
        """Find node with highest gamma."""
        return int(np.argmax(self.gamma))

    # --- COM tracking (from signed_gamma.py) ------------------------------

    def center_of_gamma(self, ref_node, radius=10):
        """Compute center of gamma mass in lattice coords, relative to ref.

        Returns ((dx, dy, dz), total_weight).
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
            w = float(self.gamma[node])
            if w > 0:
                coord = self.node_coords[node]
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


# ===========================================================================
# Verification tests
# ===========================================================================

def run_verification():
    """Run all quantum gamma verification tests."""
    print("\n=== QUANTUM GAMMA VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # Test 1: Conservation
    print("Test 1: Exact integer conservation (G=1)")
    f1 = QuantumGammaField(1000, k=6, G=1.0, seed=42)
    c1 = f1.n_nodes // 2
    f1.gamma[c1] = 500
    initial = f1.total_gamma()
    for _ in range(1000):
        f1.spread()
    final = f1.total_gamma()
    if final == initial:
        print(f"  PASS: total = {final} (unchanged from {initial})")
        passed += 1
    else:
        print(f"  FAIL: total = {final} (expected {initial})")
        failed += 1

    # Test 2: G=0 disperses
    print("Test 2: G=0 disperses quanta")
    f2 = QuantumGammaField(1000, k=6, G=0.0, seed=42)
    c2 = f2.n_nodes // 2
    f2.gamma[c2] = 100
    peak_init = int(f2.gamma[c2])
    for _ in range(500):
        f2.spread()
    peak_final = int(f2.gamma[c2])
    if peak_final < peak_init // 2:
        print(f"  PASS: peak {peak_init} -> {peak_final} (dispersed)")
        passed += 1
    else:
        print(f"  FAIL: peak {peak_init} -> {peak_final} (not dispersed)")
        failed += 1

    # Test 3: G>0 retains more than G=0
    print("Test 3: G>0 retains peak better than G=0")
    f3a = QuantumGammaField(1000, k=6, G=0.0, seed=42)
    f3b = QuantumGammaField(1000, k=6, G=1.0, seed=42)
    c3 = f3a.n_nodes // 2
    f3a.gamma[c3] = 500
    f3b.gamma[c3] = 500
    for _ in range(500):
        f3a.spread()
        f3b.spread()
    peak_g0 = int(np.max(f3a.gamma))
    peak_g1 = int(np.max(f3b.gamma))
    if peak_g1 > peak_g0:
        print(f"  PASS: G=1 peak={peak_g1} > G=0 peak={peak_g0}")
        passed += 1
    else:
        print(f"  FAIL: G=1 peak={peak_g1} not > G=0 peak={peak_g0}")
        failed += 1

    # Test 4: No negative gamma
    print("Test 4: No negative gamma")
    f4 = QuantumGammaField(1000, k=6, G=2.0, seed=42)
    c4 = f4.n_nodes // 2
    f4.gamma[c4] = 1000
    for _ in range(500):
        f4.spread()
    min_g = int(np.min(f4.gamma))
    if min_g >= 0:
        print(f"  PASS: min gamma = {min_g} >= 0")
        passed += 1
    else:
        print(f"  FAIL: min gamma = {min_g} < 0")
        failed += 1

    # Test 5: Reproducibility
    print("Test 5: Same seed = same result")
    f5a = QuantumGammaField(1000, k=6, G=1.0, seed=123)
    f5b = QuantumGammaField(1000, k=6, G=1.0, seed=123)
    c5 = f5a.n_nodes // 2
    f5a.gamma[c5] = 200
    f5b.gamma[c5] = 200
    for _ in range(100):
        f5a.spread()
        f5b.spread()
    if np.array_equal(f5a.gamma, f5b.gamma):
        print(f"  PASS: identical states after 100 ticks")
        passed += 1
    else:
        diff = np.sum(np.abs(f5a.gamma - f5b.gamma))
        print(f"  FAIL: states differ (total abs diff = {diff})")
        failed += 1

    # Test 6: Conservation with G_attract
    print("Test 6: Conservation with G_attract > 0")
    f6 = QuantumGammaField(1000, k=6, G=1.0, G_attract=1.0, seed=42)
    c6 = f6.n_nodes // 2
    f6.gamma[c6] = 300
    f6.gamma[f6.neighbors[c6][0]] = 200
    initial6 = f6.total_gamma()
    for _ in range(500):
        f6.spread()
    final6 = f6.total_gamma()
    if final6 == initial6:
        print(f"  PASS: total = {final6} (unchanged with G_attract)")
        passed += 1
    else:
        print(f"  FAIL: total = {final6} (expected {initial6})")
        failed += 1

    print(f"\n=== RESULTS: {passed} passed, {failed} failed "
          f"out of {passed + failed} ===\n")
    return failed == 0


# ===========================================================================
# Experiment A: Brownian motion of a single cluster
# ===========================================================================

def test_brownian(n_nodes=8000, G=1.0, mass=1000, ticks=10000,
                  smooth_ticks=10, measure_interval=10, seed=42):
    """Test if a cluster's COM does a Brownian random walk."""
    print("=" * 70)
    print("QUANTUM BROWNIAN MOTION TEST")
    print("=" * 70)

    field = QuantumGammaField(n_nodes, k=6, G=G, seed=seed)
    center = field.n_nodes // 2
    field.initialize_peak(center, mass, smooth_ticks=smooth_ticks)

    init_total = field.total_gamma()
    peak_node = field.find_peak_node()
    print(f"\n  G={G}, mass={mass}, ticks={ticks}")
    print(f"  Initial: total={init_total}, peak={int(field.gamma[peak_node])} "
          f"at node {peak_node}")

    records = []
    t0 = time.time()

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            com, com_weight = field.center_of_gamma(center, radius=12)
            com_dist = np.sqrt(com[0]**2 + com[1]**2 + com[2]**2)
            peak_g = int(np.max(field.gamma))
            peak_n = field.find_peak_node()

            records.append({
                'tick': tick + 1,
                'com_x': com[0], 'com_y': com[1], 'com_z': com[2],
                'com_dist': com_dist,
                'peak_gamma': peak_g,
                'peak_node': peak_n,
                'total': field.total_gamma(),
            })

            if (tick + 1) % (ticks // 5) == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:6d}: com=({com[0]:.3f},{com[1]:.3f},"
                      f"{com[2]:.3f}) dist={com_dist:.4f} "
                      f"peak={peak_g} total={field.total_gamma()} "
                      f"({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s ({ticks/elapsed:.0f} ticks/s)")
    print(f"  Final total: {field.total_gamma()} (init: {init_total})")

    # Analyze: RMS displacement vs time
    ticks_arr = np.array([r['tick'] for r in records])
    dist_arr = np.array([r['com_dist'] for r in records])

    # Fit: dist^2 = 2*D*t (in 3D: 6*D*t, but we use radial dist)
    dist2 = dist_arr ** 2
    # Linear fit of dist^2 vs tick
    if len(ticks_arr) > 10:
        coeffs = np.polyfit(ticks_arr, dist2, 1)
        D_fit = coeffs[0] / 6.0  # 3D diffusion: <r^2> = 6*D*t
        print(f"  Diffusion coefficient D = {D_fit:.6f} hops^2/tick")
        print(f"  RMS displacement at T={ticks}: "
              f"{dist_arr[-1]:.4f} hops")
    else:
        D_fit = 0.0

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Panel 1: COM trajectory components
    ax = axes[0, 0]
    ax.plot(ticks_arr, [r['com_x'] for r in records], 'r-',
            linewidth=0.3, alpha=0.7, label='x')
    ax.plot(ticks_arr, [r['com_y'] for r in records], 'g-',
            linewidth=0.3, alpha=0.7, label='y')
    ax.plot(ticks_arr, [r['com_z'] for r in records], 'b-',
            linewidth=0.3, alpha=0.7, label='z')
    ax.set_ylabel('COM displacement (hops)')
    ax.set_title('COM Random Walk')
    ax.legend()

    # Panel 2: COM distance (should grow as sqrt(t))
    ax = axes[0, 1]
    ax.plot(ticks_arr, dist_arr, 'k-', linewidth=0.3, alpha=0.7)
    if D_fit > 0:
        t_fit = np.linspace(1, ticks, 200)
        ax.plot(t_fit, np.sqrt(6 * D_fit * t_fit), 'r--',
                linewidth=1, label=f'sqrt(6Dt), D={D_fit:.2e}')
        ax.legend()
    ax.set_ylabel('COM distance (hops)')
    ax.set_title('RMS Displacement')

    # Panel 3: dist^2 vs time (should be linear)
    ax = axes[1, 0]
    ax.plot(ticks_arr, dist2, 'k-', linewidth=0.3, alpha=0.7)
    if D_fit > 0:
        ax.plot(ticks_arr, coeffs[0] * ticks_arr + coeffs[1], 'r--',
                linewidth=1, label=f'Linear fit (D={D_fit:.2e})')
        ax.legend()
    ax.set_ylabel('COM distance^2')
    ax.set_xlabel('Tick')
    ax.set_title('Diffusion (dist^2 vs t)')

    # Panel 4: Peak gamma (stability)
    ax = axes[1, 1]
    ax.plot(ticks_arr, [r['peak_gamma'] for r in records], 'b-',
            linewidth=0.3)
    ax.set_ylabel('Peak gamma')
    ax.set_xlabel('Tick')
    ax.set_title('Peak Stability')

    fig.suptitle(f'Quantum Brownian Motion: G={G}, M={mass}', fontsize=14)
    plt.tight_layout()
    path = RESULTS_DIR / f"quantum_brownian_G{G}_M{mass}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Plot saved: {path}")

    return records, D_fit


# ===========================================================================
# Experiment B: Two-body attraction
# ===========================================================================

def test_attraction(n_nodes=8000, G=1.0, G_attract=0.5, mass=1000,
                    separation=10, ticks=10000, smooth_ticks=10,
                    measure_interval=10, seed=42):
    """Test if gravitational bias produces attraction between clusters."""
    print("=" * 70)
    print("QUANTUM TWO-BODY ATTRACTION TEST")
    print("=" * 70)

    field = QuantumGammaField(n_nodes, k=6, G=G, G_attract=G_attract,
                               seed=seed)
    nodes = field.initialize_two_peaks(separation=separation, mass=mass,
                                        smooth_ticks=smooth_ticks)

    init_total = field.total_gamma()
    init_dist = field.hop_distance(nodes[0], nodes[1])
    print(f"\n  G={G}, G_attract={G_attract}, mass={mass}, sep={separation}")
    print(f"  Initial: total={init_total}, dist={init_dist}")

    records = []
    t0 = time.time()

    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_interval == 0:
            # Track COM of each cluster
            com_a, w_a = field.center_of_gamma(nodes[0], radius=8)
            com_b, w_b = field.center_of_gamma(nodes[1], radius=8)

            # COM separation (accounting for base separation)
            base_coord_a = field.node_coords[nodes[0]]
            base_coord_b = field.node_coords[nodes[1]]
            s = field.side
            # Total displacement: base + com shift
            sep_x = (base_coord_b[0] - base_coord_a[0] +
                     com_b[0] - com_a[0])
            sep_y = (base_coord_b[1] - base_coord_a[1] +
                     com_b[1] - com_a[1])
            sep_z = (base_coord_b[2] - base_coord_a[2] +
                     com_b[2] - com_a[2])
            # Periodic wrapping
            if sep_x > s // 2: sep_x -= s
            if sep_x < -(s // 2): sep_x += s
            if sep_y > s // 2: sep_y -= s
            if sep_y < -(s // 2): sep_y += s
            if sep_z > s // 2: sep_z -= s
            if sep_z < -(s // 2): sep_z += s
            com_sep = np.sqrt(sep_x**2 + sep_y**2 + sep_z**2)

            # Also find the two biggest peak nodes
            peaks = field.find_peaks()
            if len(peaks) >= 2:
                peak_dist = field.hop_distance(peaks[0][0], peaks[1][0])
            elif len(peaks) == 1:
                peak_dist = 0
            else:
                peak_dist = -1

            records.append({
                'tick': tick + 1,
                'com_sep': com_sep,
                'peak_dist': peak_dist,
                'total': field.total_gamma(),
                'mass_a': w_a, 'mass_b': w_b,
            })

            if (tick + 1) % (ticks // 5) == 0:
                elapsed = time.time() - t0
                print(f"    Tick {tick+1:6d}: com_sep={com_sep:.3f} "
                      f"peak_dist={peak_dist} "
                      f"total={field.total_gamma()} "
                      f"({elapsed:.1f}s)")

    elapsed = time.time() - t0
    print(f"\n  Done in {elapsed:.1f}s ({ticks/elapsed:.0f} ticks/s)")
    print(f"  Final total: {field.total_gamma()} (init: {init_total})")

    # Final distance
    final_com_sep = records[-1]['com_sep'] if records else 0
    final_peak_dist = records[-1]['peak_dist'] if records else -1
    print(f"  COM separation: {init_dist:.1f} -> {final_com_sep:.3f}")
    print(f"  Peak distance: {init_dist} -> {final_peak_dist}")

    if final_com_sep < init_dist - 0.5:
        print("  ** ATTRACTION DETECTED (COM) **")
    elif final_peak_dist >= 0 and final_peak_dist < init_dist:
        print("  ** ATTRACTION DETECTED (peak) **")
    else:
        print("  No significant attraction")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    ticks_arr = [r['tick'] for r in records]

    ax = axes[0, 0]
    ax.plot(ticks_arr, [r['com_sep'] for r in records], 'b-',
            linewidth=0.3, alpha=0.7)
    ax.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylabel('COM separation')
    ax.set_title('Center-of-Mass Separation')

    ax = axes[0, 1]
    ax.plot(ticks_arr, [r['peak_dist'] for r in records], 'r-',
            linewidth=0.3, alpha=0.7)
    ax.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylabel('Peak distance (hops)')
    ax.set_title('Peak-to-Peak Distance')

    ax = axes[1, 0]
    ax.plot(ticks_arr, [r['mass_a'] for r in records], 'b-',
            linewidth=0.3, label='A')
    ax.plot(ticks_arr, [r['mass_b'] for r in records], 'r-',
            linewidth=0.3, label='B')
    ax.set_ylabel('Cluster mass')
    ax.set_xlabel('Tick')
    ax.set_title('Mass in each cluster')
    ax.legend()

    ax = axes[1, 1]
    ax.plot(ticks_arr, [r['total'] for r in records], 'g-',
            linewidth=0.3)
    ax.set_ylabel('Total gamma')
    ax.set_xlabel('Tick')
    ax.set_title('Conservation')

    fig.suptitle(f'Two-Body: G={G}, G_attract={G_attract}, M={mass}',
                 fontsize=14)
    plt.tight_layout()
    path = RESULTS_DIR / f"quantum_attraction_G{G}_Ga{G_attract}_M{mass}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"  Plot saved: {path}")

    return records


# ===========================================================================
# Experiment C: Mass-dependent diffusion
# ===========================================================================

def test_mass_sweep(n_nodes=8000, G=1.0, ticks=10000, measure_interval=10,
                    seed=42):
    """Measure diffusion coefficient as function of mass."""
    print("=" * 70)
    print("MASS-DEPENDENT DIFFUSION SWEEP")
    print("=" * 70)

    masses = [100, 300, 500, 1000, 2000, 5000]
    results = []

    for M in masses:
        print(f"\n  --- M = {M} ---")
        field = QuantumGammaField(n_nodes, k=6, G=G, seed=seed)
        center = field.n_nodes // 2
        field.initialize_peak(center, M, smooth_ticks=10)

        com_dists_sq = []
        t0 = time.time()

        for tick in range(ticks):
            field.spread()

            if (tick + 1) % measure_interval == 0:
                com, _ = field.center_of_gamma(center, radius=12)
                d2 = com[0]**2 + com[1]**2 + com[2]**2
                com_dists_sq.append((tick + 1, d2))

        elapsed = time.time() - t0
        ticks_arr = np.array([x[0] for x in com_dists_sq])
        d2_arr = np.array([x[1] for x in com_dists_sq])

        # Fit D from <r^2> = 6*D*t
        if len(ticks_arr) > 10:
            coeffs = np.polyfit(ticks_arr, d2_arr, 1)
            D = coeffs[0] / 6.0
        else:
            D = 0.0

        final_rms = np.sqrt(d2_arr[-1]) if len(d2_arr) > 0 else 0
        peak_g = int(np.max(field.gamma))
        total = field.total_gamma()

        results.append({
            'mass': M,
            'D': D,
            'final_rms': final_rms,
            'peak_gamma': peak_g,
            'total': total,
        })

        print(f"    D = {D:.6f}, RMS = {final_rms:.4f}, "
              f"peak = {peak_g}, total = {total} ({elapsed:.1f}s)")

    # Summary
    print(f"\n  {'Mass':>6} {'D':>12} {'D*M':>12} {'D*M^2':>12} "
          f"{'RMS':>10} {'Peak':>6}")
    print("  " + "-" * 65)
    for r in results:
        print(f"  {r['mass']:6d} {r['D']:12.6f} "
              f"{r['D']*r['mass']:12.4f} "
              f"{r['D']*r['mass']**2:12.2f} "
              f"{r['final_rms']:10.4f} {r['peak_gamma']:6d}")

    # Plot
    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    ms = [r['mass'] for r in results]
    Ds = [r['D'] for r in results]

    ax = axes[0]
    ax.loglog(ms, [max(d, 1e-10) for d in Ds], 'bo-')
    ax.set_xlabel('Mass')
    ax.set_ylabel('Diffusion coeff D')
    ax.set_title('D vs Mass (log-log)')

    ax = axes[1]
    ax.plot(ms, [r['D'] * r['mass'] for r in results], 'ro-')
    ax.set_xlabel('Mass')
    ax.set_ylabel('D * M')
    ax.set_title('D*M vs Mass (const if D ~ 1/M)')

    ax = axes[2]
    ax.plot(ms, [r['final_rms'] for r in results], 'go-')
    ax.set_xlabel('Mass')
    ax.set_ylabel(f'RMS displacement at T={ticks}')
    ax.set_title('Mobility vs Mass')

    plt.tight_layout()
    path = RESULTS_DIR / f"quantum_mass_sweep_G{G}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n  Plot saved: {path}")

    return results


# ===========================================================================
# Experiment D: G_attract sweep for two-body
# ===========================================================================

def test_attract_sweep(n_nodes=8000, G=1.0, mass=1000, separation=10,
                       ticks=5000, measure_interval=10, seed=42):
    """Sweep G_attract to find the threshold for attraction."""
    print("=" * 70)
    print("G_ATTRACT SWEEP (two-body)")
    print("=" * 70)

    g_attracts = [0.0, 0.1, 0.5, 1.0, 2.0, 5.0]
    results = []

    for ga in g_attracts:
        print(f"\n  --- G_attract = {ga} ---")
        field = QuantumGammaField(n_nodes, k=6, G=G, G_attract=ga, seed=seed)
        nodes = field.initialize_two_peaks(separation=separation, mass=mass,
                                            smooth_ticks=10)

        init_dist = field.hop_distance(nodes[0], nodes[1])

        # Track COM separation over time
        com_seps = []
        t0 = time.time()

        for tick in range(ticks):
            field.spread()

            if (tick + 1) % measure_interval == 0:
                com_a, _ = field.center_of_gamma(nodes[0], radius=8)
                com_b, _ = field.center_of_gamma(nodes[1], radius=8)
                base_a = field.node_coords[nodes[0]]
                base_b = field.node_coords[nodes[1]]
                s = field.side
                sx = base_b[0] - base_a[0] + com_b[0] - com_a[0]
                sy = base_b[1] - base_a[1] + com_b[1] - com_a[1]
                sz = base_b[2] - base_a[2] + com_b[2] - com_a[2]
                if sx > s//2: sx -= s
                if sx < -(s//2): sx += s
                if sy > s//2: sy -= s
                if sy < -(s//2): sy += s
                if sz > s//2: sz -= s
                if sz < -(s//2): sz += s
                com_seps.append((tick + 1, np.sqrt(sx**2 + sy**2 + sz**2)))

        elapsed = time.time() - t0

        final_sep = com_seps[-1][1] if com_seps else init_dist
        # Compute mean separation in last 10% of run
        late = com_seps[len(com_seps)*9//10:]
        mean_late_sep = np.mean([s[1] for s in late]) if late else final_sep

        results.append({
            'G_attract': ga,
            'init_dist': init_dist,
            'final_sep': final_sep,
            'mean_late_sep': mean_late_sep,
            'total': field.total_gamma(),
            'com_seps': com_seps,
        })

        print(f"    sep: {init_dist:.1f} -> {final_sep:.3f} "
              f"(mean late: {mean_late_sep:.3f}) "
              f"total={field.total_gamma()} ({elapsed:.1f}s)")

    # Summary
    print(f"\n  {'G_attract':>10} {'Init':>6} {'Final':>8} "
          f"{'MeanLate':>10} {'Delta':>8}")
    print("  " + "-" * 50)
    for r in results:
        delta = r['mean_late_sep'] - r['init_dist']
        print(f"  {r['G_attract']:10.1f} {r['init_dist']:6.1f} "
              f"{r['final_sep']:8.3f} {r['mean_late_sep']:10.3f} "
              f"{delta:+8.3f}")

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    for r in results:
        ticks_arr = [s[0] for s in r['com_seps']]
        seps_arr = [s[1] for s in r['com_seps']]
        ax.plot(ticks_arr, seps_arr, linewidth=0.3, alpha=0.7,
                label=f"Ga={r['G_attract']}")
    ax.axhline(y=results[0]['init_dist'], color='gray', linestyle='--',
               alpha=0.5)
    ax.set_xlabel('Tick')
    ax.set_ylabel('COM separation')
    ax.set_title('Separation vs Time')
    ax.legend(fontsize=8)

    ax = axes[1]
    gas = [r['G_attract'] for r in results]
    deltas = [r['mean_late_sep'] - r['init_dist'] for r in results]
    ax.plot(gas, deltas, 'bo-')
    ax.axhline(y=0, color='gray', linestyle='--', alpha=0.5)
    ax.set_xlabel('G_attract')
    ax.set_ylabel('Mean separation change')
    ax.set_title('Attraction vs G_attract')

    plt.tight_layout()
    path = RESULTS_DIR / f"quantum_attract_sweep_G{G}_M{mass}.png"
    plt.savefig(path, dpi=150)
    plt.close()
    print(f"\n  Plot saved: {path}")

    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v6 Quantum Gamma: Integer Stochastic Field')

    parser.add_argument('--verify', action='store_true',
                        help='Run verification tests')
    parser.add_argument('--brownian', action='store_true',
                        help='Brownian motion test (single cluster)')
    parser.add_argument('--attraction', action='store_true',
                        help='Two-body attraction test')
    parser.add_argument('--mass-sweep', action='store_true',
                        help='Mass-dependent diffusion sweep')
    parser.add_argument('--attract-sweep', action='store_true',
                        help='G_attract sweep for two-body')
    parser.add_argument('--all', action='store_true',
                        help='Run all experiments')

    parser.add_argument('--n-nodes', type=int, default=8000)
    parser.add_argument('--G', type=float, default=1.0)
    parser.add_argument('--G-attract', type=float, default=0.5)
    parser.add_argument('--mass', type=int, default=1000)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--ticks', type=int, default=10000)
    parser.add_argument('--smooth-ticks', type=int, default=10)
    parser.add_argument('--measure-interval', type=int, default=10)
    parser.add_argument('--seed', type=int, default=42)

    args = parser.parse_args()

    if args.verify:
        return 0 if run_verification() else 1

    ran_any = False

    if args.brownian or args.all:
        test_brownian(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                      ticks=args.ticks, smooth_ticks=args.smooth_ticks,
                      measure_interval=args.measure_interval, seed=args.seed)
        ran_any = True

    if args.attraction or args.all:
        test_attraction(n_nodes=args.n_nodes, G=args.G,
                        G_attract=args.G_attract, mass=args.mass,
                        separation=args.separation, ticks=args.ticks,
                        smooth_ticks=args.smooth_ticks,
                        measure_interval=args.measure_interval,
                        seed=args.seed)
        ran_any = True

    if args.mass_sweep or args.all:
        test_mass_sweep(n_nodes=args.n_nodes, G=args.G, ticks=args.ticks,
                        measure_interval=args.measure_interval, seed=args.seed)
        ran_any = True

    if args.attract_sweep or args.all:
        test_attract_sweep(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                           separation=args.separation, ticks=args.ticks // 2,
                           measure_interval=args.measure_interval,
                           seed=args.seed)
        ran_any = True

    if not ran_any:
        parser.print_help()
        return 1

    return 0


if __name__ == '__main__':
    exit(main())
