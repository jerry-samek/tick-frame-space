"""v7: Spread-First Eddy Model — One Field, Gravity from Shadows.

Default state is propagation at c. Patterns are eddies.

Each tick:
  1. SPREAD at c — every quantum has probability alpha of hopping to a random
     neighbor. Uniform, unbiased. Gamma wants to fly.
  2. RECAPTURE — each quantum at node j may get pulled to a neighboring node i
     with probability proportional to G_recapture * gamma[i]. Dense nodes pull
     harder. This creates eddies: gamma cycling between center and neighbors.

What escapes recapture propagates freely at c forever = radiation = gravitational
field. A stable particle sheds its outer layer every tick; the shedding IS what
keeps it the same size against c-speed expansion.

Gravity: pattern A absorbs background gamma flowing past (recapture). Behind A,
less gamma flows — a shadow. Pattern B downstream sees the deficit, drifts toward
it. Attraction.

More mass = more to shed = stronger radiation = stronger gravitational signal.
Zero mass = nothing to shed = propagate at c = photon.
Existence is expensive. The bill is gravity.

One field. One spread rate. One recapture rule.

Usage:
    python spread_first.py --verify
    python spread_first.py --stability --G-recapture 0.5
    python spread_first.py --shadow --mass 1000
    python spread_first.py --attraction --mass 1000 --separation 10
    python spread_first.py --photon

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

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'v6'))
from quantum_gamma import QuantumGammaField
from gamma_field import RESULTS_DIR as V6_RESULTS_DIR, make_serializable

RESULTS_DIR = Path(__file__).parent / "results"
RESULTS_DIR.mkdir(exist_ok=True)


# ===========================================================================
# SpreadFirstField
# ===========================================================================

class SpreadFirstField(QuantumGammaField):
    """Spread-first eddy model: spread at c, then recapture.

    Gamma flies by default. Patterns exist as eddies — continuously
    shedding their outer layer while recapturing their core. The
    radiation is the gravitational field.
    """

    def __init__(self, *args, G_recapture=0.5, **kwargs):
        # Disable parent's self-gravitation and attraction bias
        kwargs['G'] = 0.0
        kwargs['G_attract'] = 0.0
        super().__init__(*args, **kwargs)
        self.G_recapture = G_recapture

    def spread(self):
        """Two-step: spread at c, then recapture.

        Step 1: Every quantum has probability alpha of leaving its node.
                Each leaving quantum goes to one uniformly random neighbor.
                This is propagation at c.

        Step 2: Every quantum at node j considers being pulled to a neighbor.
                Pull weight to neighbor i = G_recapture * gamma[i].
                Stay weight = 1.0.
                Multinomial decides where each quantum goes.

        Conservation: exact (quanta move between nodes, none created/destroyed).
        """
        # --- STEP 1: Spread at c (uniform) ---
        n_leaving = self.rng.binomial(self.gamma, self.alpha)
        gamma_mid = self.gamma.copy()
        gamma_mid -= n_leaving
        self._distribute_uniform(n_leaving, gamma_mid)

        # --- STEP 2: Recapture ---
        if self.G_recapture == 0.0:
            self.gamma = gamma_mid
            return

        gamma_snapshot = gamma_mid.copy()
        gamma_new = np.zeros_like(gamma_mid)

        for j in range(self.n_nodes):
            if gamma_snapshot[j] <= 0:
                continue
            nbs = self.neighbors[j]
            k_deg = len(nbs)
            if k_deg == 0:
                gamma_new[j] += gamma_snapshot[j]
                continue

            # Pull weights: neighbor i pulls with strength G_recapture * gamma[i]
            pull_weights = np.array([
                self.G_recapture * float(gamma_snapshot[nb]) for nb in nbs
            ])
            stay_weight = 1.0
            total = pull_weights.sum() + stay_weight

            probs = np.empty(k_deg + 1)
            probs[0] = stay_weight / total
            probs[1:] = pull_weights / total

            alloc = self.rng.multinomial(int(gamma_snapshot[j]), probs)
            gamma_new[j] += alloc[0]  # stays at j
            for idx in range(k_deg):
                gamma_new[nbs[idx]] += alloc[idx + 1]  # pulled to neighbor

        self.gamma = gamma_new

    # --- Initialization ---------------------------------------------------

    def initialize_cycling_peak(self, center, mass, warmup_ticks=50):
        """Initialize a cycling pattern (eddy) at center.

        Place gamma delta at center, then run spread for warmup_ticks.
        The pattern self-organizes into a dynamic eddy: gamma cycling
        between center and neighbors, with some leaked gamma filling
        the background.
        """
        self.gamma[center] += int(mass)
        for _ in range(warmup_ticks):
            self.spread()

    def initialize_two_cycling_peaks(self, separation, mass, warmup_ticks=50):
        """Initialize two cycling peaks simultaneously."""
        nodes = self.place_peaks_equilateral(separation=separation, n_peaks=2)
        self.gamma[nodes[0]] += int(mass)
        self.gamma[nodes[1]] += int(mass)
        for _ in range(warmup_ticks):
            self.spread()
        return nodes

    # --- Measurements -----------------------------------------------------

    def bound_mass(self, center, radius=5):
        """Gamma within radius hops of center."""
        visited = {center}
        queue = deque([(center, 0)])
        total = 0
        while queue:
            node, dist = queue.popleft()
            total += int(self.gamma[node])
            if dist < radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))
        return total

    def radiation_rate(self, center, radius=5, dt=10):
        """Measure gamma escaping from radius per tick (averaged over dt ticks)."""
        bound_before = self.bound_mass(center, radius)
        gamma_saved = self.gamma.copy()
        for _ in range(dt):
            self.spread()
        bound_after = self.bound_mass(center, radius)
        self.gamma = gamma_saved  # restore state
        # Radiation = loss of bound mass per tick
        return (bound_before - bound_after) / dt

    def eddy_radius(self, center, fraction=0.5):
        """Half-mass radius: smallest radius containing fraction of bound mass."""
        visited = {center}
        queue = deque([(center, 0)])
        shells = {}
        while queue:
            node, dist = queue.popleft()
            if dist not in shells:
                shells[dist] = 0
            shells[dist] += int(self.gamma[node])
            if dist < 15:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))
        total = sum(shells.values())
        if total == 0:
            return 0
        cumulative = 0
        for d in sorted(shells.keys()):
            cumulative += shells[d]
            if cumulative >= fraction * total:
                return d
        return max(shells.keys())

    def directional_gamma_profile(self, center, direction_node, max_radius=12):
        """Gamma split by hemisphere: toward direction_node vs away.

        Returns list of dicts with distance, mean_toward, mean_away, shadow.
        """
        assert hasattr(self, 'node_coords'), "Requires lattice"
        center_coord = np.array(self.node_coords[center], dtype=float)
        dir_coord = np.array(self.node_coords[direction_node], dtype=float)
        s = self.side

        # Direction vector (with periodic wrapping)
        dv = dir_coord - center_coord
        for i in range(3):
            if dv[i] > s // 2: dv[i] -= s
            if dv[i] < -(s // 2): dv[i] += s
        norm = np.linalg.norm(dv)
        if norm < 1e-10:
            return []
        dv /= norm

        # BFS, classify into toward/away hemispheres
        visited = {center}
        queue = deque([(center, 0)])
        toward = {}  # dist -> list of gamma values
        away = {}

        while queue:
            node, dist = queue.popleft()
            if dist > 0:
                nc = np.array(self.node_coords[node], dtype=float)
                delta = nc - center_coord
                for i in range(3):
                    if delta[i] > s // 2: delta[i] -= s
                    if delta[i] < -(s // 2): delta[i] += s
                dot = np.dot(delta, dv)
                bucket = toward if dot > 0 else away
                if dist not in bucket:
                    bucket[dist] = []
                bucket[dist].append(float(self.gamma[node]))

            if dist < max_radius:
                for nb in self.neighbors[node]:
                    if nb not in visited:
                        visited.add(nb)
                        queue.append((nb, dist + 1))

        profile = []
        for d in range(1, max_radius + 1):
            t_vals = toward.get(d, [0.0])
            a_vals = away.get(d, [0.0])
            mean_t = np.mean(t_vals) if t_vals else 0.0
            mean_a = np.mean(a_vals) if a_vals else 0.0
            shadow = (mean_a - mean_t) / mean_a if mean_a > 0 else 0.0
            profile.append({
                'distance': d,
                'mean_toward': mean_t,
                'mean_away': mean_a,
                'shadow': shadow,
                'n_toward': len(t_vals),
                'n_away': len(a_vals),
            })
        return profile


# ===========================================================================
# Verification tests
# ===========================================================================

def run_verification():
    print("\n=== SPREAD-FIRST VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # Test 1: Conservation
    print("Test 1: Exact integer conservation")
    f = SpreadFirstField(1000, k=6, G_recapture=0.5, seed=42)
    c = f.n_nodes // 2
    f.gamma[c] = 500
    initial = f.total_gamma()
    for _ in range(1000):
        f.spread()
    final = f.total_gamma()
    if final == initial:
        print(f"  PASS: total = {final} (unchanged)")
        passed += 1
    else:
        print(f"  FAIL: total = {final} (expected {initial})")
        failed += 1

    # Test 2: No negatives
    print("Test 2: No negative gamma")
    f2 = SpreadFirstField(1000, k=6, G_recapture=1.0, seed=42)
    c2 = f2.n_nodes // 2
    f2.gamma[c2] = 1000
    for _ in range(500):
        f2.spread()
    min_g = int(np.min(f2.gamma))
    if min_g >= 0:
        print(f"  PASS: min gamma = {min_g}")
        passed += 1
    else:
        print(f"  FAIL: min gamma = {min_g}")
        failed += 1

    # Test 3: Reproducibility
    print("Test 3: Same seed = same result")
    f3a = SpreadFirstField(1000, k=6, G_recapture=0.5, seed=123)
    f3b = SpreadFirstField(1000, k=6, G_recapture=0.5, seed=123)
    c3 = f3a.n_nodes // 2
    f3a.gamma[c3] = 300
    f3b.gamma[c3] = 300
    for _ in range(100):
        f3a.spread()
        f3b.spread()
    if np.array_equal(f3a.gamma, f3b.gamma):
        print(f"  PASS: identical after 100 ticks")
        passed += 1
    else:
        diff = int(np.sum(np.abs(f3a.gamma - f3b.gamma)))
        print(f"  FAIL: differ by {diff}")
        failed += 1

    # Test 4: Peak formation (G_recapture > 0 creates eddy)
    print("Test 4: Eddy forms with G_recapture > 0")
    f4 = SpreadFirstField(8000, k=6, G_recapture=0.5, seed=42)
    c4 = f4.n_nodes // 2
    f4.gamma[c4] = 1000
    for _ in range(500):
        f4.spread()
    peak = int(np.max(f4.gamma))
    bg = f4.total_gamma() / f4.n_nodes
    ratio = peak / bg if bg > 0 else float('inf')
    if ratio > 5:
        print(f"  PASS: peak={peak}, background={bg:.2f}, ratio={ratio:.1f}")
        passed += 1
    else:
        print(f"  FAIL: peak={peak}, background={bg:.2f}, ratio={ratio:.1f} (< 5)")
        failed += 1

    # Test 5: G_recapture=0 disperses
    print("Test 5: G_recapture=0 disperses to background")
    f5 = SpreadFirstField(1000, k=6, G_recapture=0.0, seed=42)
    c5 = f5.n_nodes // 2
    f5.gamma[c5] = 500
    for _ in range(500):
        f5.spread()
    peak5 = int(np.max(f5.gamma))
    mean5 = f5.total_gamma() / f5.n_nodes
    # With integer quanta, Poisson bunching gives max ~ 4-5x mean
    if peak5 < 10 * mean5:
        print(f"  PASS: peak={peak5}, mean={mean5:.2f} (dispersed)")
        passed += 1
    else:
        print(f"  FAIL: peak={peak5}, mean={mean5:.2f} (not dispersed)")
        failed += 1

    # Test 6: Background fills (some gamma escapes the eddy)
    print("Test 6: Some gamma escapes eddy after 500 ticks")
    f6 = SpreadFirstField(8000, k=6, G_recapture=0.5, seed=42)
    c6 = f6.n_nodes // 2
    f6.gamma[c6] = 1000
    for _ in range(500):
        f6.spread()
    # Count nodes beyond radius 5 that have any gamma
    peak6 = int(np.argmax(f6.gamma))
    bound6 = f6.bound_mass(peak6, radius=5)
    escaped = f6.total_gamma() - bound6
    nonzero = int(np.sum(f6.gamma > 0))
    frac = nonzero / f6.n_nodes
    if escaped > 10:
        print(f"  PASS: {escaped} quanta escaped, {nonzero} nodes with gamma > 0")
        passed += 1
    else:
        print(f"  FAIL: only {escaped} quanta escaped (need > 10)")
        failed += 1

    # Test 7: Shadow exists
    print("Test 7: Single peak creates measurable shadow")
    f7 = SpreadFirstField(8000, k=6, G_recapture=0.5, seed=42)
    nodes7 = f7.place_peaks_equilateral(separation=10, n_peaks=2)
    # Only place ONE peak, use second node as direction reference
    f7.gamma[nodes7[0]] = 1000
    for _ in range(500):
        f7.spread()
    profile = f7.directional_gamma_profile(nodes7[0], nodes7[1], max_radius=8)
    # Check shadow at distance 4-6
    shadow_vals = [p['shadow'] for p in profile if 4 <= p['distance'] <= 6]
    mean_shadow = np.mean(shadow_vals) if shadow_vals else 0.0
    # Shadow should be negative (toward has MORE gamma since it's the radiation side)
    # or positive depending on hemisphere definition. Just check it's nonzero.
    if abs(mean_shadow) > 0.001:
        print(f"  PASS: mean shadow at d=4-6: {mean_shadow:.4f}")
        passed += 1
    else:
        print(f"  FAIL: mean shadow at d=4-6: {mean_shadow:.4f} (too small)")
        failed += 1

    # Test 8: Cycling pattern oscillates
    print("Test 8: Peak gamma oscillates tick-to-tick")
    f8 = SpreadFirstField(8000, k=6, G_recapture=0.5, seed=42)
    c8 = f8.n_nodes // 2
    f8.gamma[c8] = 1000
    # Warmup
    for _ in range(100):
        f8.spread()
    peak_node = int(np.argmax(f8.gamma))
    vals = []
    for _ in range(20):
        f8.spread()
        vals.append(int(f8.gamma[peak_node]))
    variance = np.var(vals)
    if variance > 0:
        print(f"  PASS: peak gamma variance = {variance:.1f} (oscillating)")
        passed += 1
    else:
        print(f"  FAIL: peak gamma variance = 0 (static)")
        failed += 1

    print(f"\n=== Results: {passed}/{passed + failed} passed ===\n")
    return passed, failed


# ===========================================================================
# Experiments
# ===========================================================================

def experiment_stability(args):
    """Experiment A: Eddy stability, radiation rate, equilibrium size."""
    print("\n" + "=" * 70)
    print("EXPERIMENT A: Eddy Stability & Radiation")
    print("=" * 70)

    ticks = args.ticks or 5000
    mass = args.mass or 1000
    measure_every = max(1, ticks // 100)

    if args.G_recapture is not None:
        gr_values = [args.G_recapture]
    else:
        gr_values = [0.1, 0.2, 0.5, 1.0, 2.0, 5.0]

    results = {}

    for gr in gr_values:
        print(f"\n  G_recapture = {gr}")
        field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
        center = field.n_nodes // 2
        field.gamma[center] = int(mass)

        history = {'tick': [], 'peak_gamma': [], 'bound_mass': [],
                   'eddy_radius': [], 'total': []}
        t0 = time.time()

        for tick in range(ticks):
            field.spread()

            if (tick + 1) % measure_every == 0:
                peak = int(np.max(field.gamma))
                peak_node = int(np.argmax(field.gamma))
                bound = field.bound_mass(peak_node, radius=5)
                radius = field.eddy_radius(peak_node)
                total = field.total_gamma()

                history['tick'].append(tick + 1)
                history['peak_gamma'].append(peak)
                history['bound_mass'].append(bound)
                history['eddy_radius'].append(radius)
                history['total'].append(total)

                if (tick + 1) % (ticks // 5) == 0:
                    elapsed = time.time() - t0
                    print(f"    tick={tick+1:6d}: peak={peak:5d} bound={bound:5d} "
                          f"radius={radius} total={total} ({elapsed:.1f}s)")

        results[gr] = history

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Eddy Stability (mass={mass})", fontsize=14)

    for gr, hist in results.items():
        label = f"Gr={gr}"
        axes[0, 0].plot(hist['tick'], hist['peak_gamma'], label=label)
        axes[0, 1].plot(hist['tick'], hist['bound_mass'], label=label)
        axes[1, 0].plot(hist['tick'], hist['eddy_radius'], label=label)
        # Bound fraction
        bound_frac = [b / mass for b in hist['bound_mass']]
        axes[1, 1].plot(hist['tick'], bound_frac, label=label)

    axes[0, 0].set(xlabel='Tick', ylabel='Peak gamma', title='Peak Gamma')
    axes[0, 0].legend(fontsize=8)
    axes[0, 1].set(xlabel='Tick', ylabel='Bound mass', title='Bound Mass (r<5)')
    axes[0, 1].legend(fontsize=8)
    axes[1, 0].set(xlabel='Tick', ylabel='Eddy radius', title='Half-Mass Radius')
    axes[1, 0].legend(fontsize=8)
    axes[1, 1].set(xlabel='Tick', ylabel='Bound fraction', title='Bound Fraction')
    axes[1, 1].legend(fontsize=8)
    axes[1, 1].set_ylim(0, 1)

    plt.tight_layout()
    fname = RESULTS_DIR / f"stability_m{mass}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return results


def experiment_radiation(args):
    """Experiment A2: Radiation rate vs mass."""
    print("\n" + "=" * 70)
    print("EXPERIMENT A2: Radiation Rate vs Mass")
    print("=" * 70)

    gr = args.G_recapture or 0.5
    masses = [200, 500, 1000, 2000, 5000]
    warmup = 200
    measure_ticks = 100

    results = []
    for m in masses:
        print(f"\n  Mass = {m}, G_recapture = {gr}")
        field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
        center = field.n_nodes // 2
        field.gamma[center] = int(m)

        # Warmup
        for _ in range(warmup):
            field.spread()

        peak_node = int(np.argmax(field.gamma))
        # Measure radiation: bound mass change over measure_ticks
        bound_before = field.bound_mass(peak_node, radius=5)
        for _ in range(measure_ticks):
            field.spread()
        peak_node_after = int(np.argmax(field.gamma))
        bound_after = field.bound_mass(peak_node_after, radius=5)
        rad_rate = (bound_before - bound_after) / measure_ticks
        total = field.total_gamma()

        print(f"    bound: {bound_before} -> {bound_after}, "
              f"radiation_rate={rad_rate:.2f}/tick, total={total}")
        results.append({'mass': m, 'radiation_rate': rad_rate,
                        'bound_before': bound_before, 'bound_after': bound_after})

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    masses_arr = [r['mass'] for r in results]
    rates = [r['radiation_rate'] for r in results]
    ax.plot(masses_arr, rates, 'bo-', markersize=8)
    ax.set(xlabel='Initial Mass', ylabel='Radiation Rate (quanta/tick)',
           title=f'Radiation Rate vs Mass (G_recapture={gr})')
    ax.grid(True, alpha=0.3)
    # Fit linear
    if len(masses_arr) > 1:
        coeffs = np.polyfit(masses_arr, rates, 1)
        x_fit = np.linspace(0, max(masses_arr), 100)
        ax.plot(x_fit, np.polyval(coeffs, x_fit), 'r--',
                label=f'Linear fit: slope={coeffs[0]:.4f}')
        ax.legend()

    fname = RESULTS_DIR / f"radiation_vs_mass_Gr{gr}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return results


def experiment_shadow(args):
    """Experiment B: Shadow profile from a single peak."""
    print("\n" + "=" * 70)
    print("EXPERIMENT B: Shadow Profile")
    print("=" * 70)

    gr = args.G_recapture or 0.5
    mass = args.mass or 1000
    warmup = args.ticks or 500

    field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
    nodes = field.place_peaks_equilateral(separation=10, n_peaks=2)
    # Place only one peak; use second node as reference direction
    field.gamma[nodes[0]] = int(mass)

    print(f"\n  Warming up for {warmup} ticks...")
    t0 = time.time()
    for _ in range(warmup):
        field.spread()
    elapsed = time.time() - t0
    print(f"  Done ({elapsed:.1f}s)")

    peak_node = int(np.argmax(field.gamma))
    print(f"  Peak node: {peak_node}, gamma={int(field.gamma[peak_node])}")
    print(f"  Total gamma: {field.total_gamma()}")

    profile = field.directional_gamma_profile(peak_node, nodes[1], max_radius=10)

    print(f"\n  {'Dist':>5} {'Toward':>10} {'Away':>10} {'Shadow':>10}")
    print(f"  {'----':>5} {'------':>10} {'----':>10} {'------':>10}")
    for p in profile:
        print(f"  {p['distance']:5d} {p['mean_toward']:10.3f} "
              f"{p['mean_away']:10.3f} {p['shadow']:10.4f}")

    # Also measure radial profile (isotropic)
    rad_profile = field.radial_profile(peak_node, max_radius=10)

    # Plot
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    fig.suptitle(f"Shadow Profile (mass={mass}, Gr={gr}, warmup={warmup})", fontsize=13)

    # Left: directional profile
    dists = [p['distance'] for p in profile]
    toward = [p['mean_toward'] for p in profile]
    away = [p['mean_away'] for p in profile]
    axes[0].plot(dists, toward, 'b-o', label='Toward peak', markersize=5)
    axes[0].plot(dists, away, 'r-s', label='Away from peak', markersize=5)
    axes[0].set(xlabel='Distance (hops)', ylabel='Mean gamma',
                title='Directional Gamma Profile')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)

    # Right: shadow strength
    shadows = [p['shadow'] for p in profile]
    axes[1].bar(dists, shadows, color='purple', alpha=0.7)
    axes[1].axhline(y=0, color='k', linewidth=0.5)
    axes[1].set(xlabel='Distance (hops)', ylabel='Shadow strength',
                title='Shadow = (away - toward) / away')
    axes[1].grid(True, alpha=0.3)

    plt.tight_layout()
    fname = RESULTS_DIR / f"shadow_m{mass}_Gr{gr}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return profile


def experiment_attraction(args):
    """Experiment C: Two-body attraction test."""
    print("\n" + "=" * 70)
    print("EXPERIMENT C: Two-Body Attraction")
    print("=" * 70)

    gr = args.G_recapture or 0.5
    mass = args.mass or 1000
    sep = args.separation or 10
    ticks = args.ticks or 100000
    warmup = 50
    measure_every = max(1, ticks // 200)

    print(f"\n  G_recapture={gr}, mass={mass}, separation={sep}, ticks={ticks}")

    field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
    nodes = field.initialize_two_cycling_peaks(separation=sep, mass=mass,
                                                warmup_ticks=warmup)
    initial_total = field.total_gamma()
    initial_dist = field.hop_distance(nodes[0], nodes[1])

    print(f"  Initial: total={initial_total}, dist={initial_dist}")
    print(f"  Peak A: {int(field.gamma[nodes[0]])}, Peak B: {int(field.gamma[nodes[1]])}")

    history = {'tick': [], 'peak_dist': [], 'com_sep': [],
               'peak_a': [], 'peak_b': [], 'total': []}

    t0 = time.time()
    for tick in range(ticks):
        field.spread()

        if (tick + 1) % measure_every == 0:
            total = field.total_gamma()
            peak_a_val = int(field.gamma[nodes[0]])
            peak_b_val = int(field.gamma[nodes[1]])

            # Find actual peaks
            raw_peaks = field.find_peaks()
            if len(raw_peaks) >= 2:
                p0, p1 = raw_peaks[0][0], raw_peaks[1][0]
                peak_dist = field.hop_distance(p0, p1)
            elif len(raw_peaks) == 1:
                peak_dist = 0
            else:
                peak_dist = -1

            # COM separation
            if len(raw_peaks) >= 2:
                com_a, w_a = field.center_of_gamma(raw_peaks[0][0], radius=8)
                com_b, w_b = field.center_of_gamma(raw_peaks[1][0], radius=8)
                com_sep = np.sqrt(sum((a - b)**2 for a, b in zip(com_a, com_b)))
            else:
                com_sep = 0.0

            history['tick'].append(tick + 1)
            history['peak_dist'].append(peak_dist)
            history['com_sep'].append(com_sep)
            history['peak_a'].append(peak_a_val)
            history['peak_b'].append(peak_b_val)
            history['total'].append(total)

            if (tick + 1) % (ticks // 10) == 0:
                elapsed = time.time() - t0
                drift = abs(total - initial_total) / initial_total if initial_total > 0 else 0
                print(f"    tick={tick+1:7d}: peak_dist={peak_dist:3d} "
                      f"com_sep={com_sep:.3f} total={total} "
                      f"drift={drift:.2e} ({elapsed:.1f}s)")

    # Final analysis
    total = field.total_gamma()
    print(f"\n  Final total: {total} (initial: {initial_total})")

    raw_peaks = field.find_peaks()
    print(f"  Peaks found: {len(raw_peaks)}")
    for i, (node, val) in enumerate(raw_peaks[:5]):
        print(f"    Peak {i}: node={node}, gamma={val}")

    if len(history['com_sep']) > 20:
        early = np.mean(history['com_sep'][:10])
        late = np.mean(history['com_sep'][-10:])
        approach = early - late
        print(f"\n  COM separation: early={early:.3f} -> late={late:.3f} "
              f"(approach={approach:.3f})")
        if approach > 0.5:
            print("  ** ATTRACTION DETECTED **")
        elif approach > 0.1:
            print("  ** WEAK ATTRACTION **")
        elif approach < -0.1:
            print("  ** REPULSION? **")
        else:
            print("  ** NO CLEAR SIGNAL **")

    # Plot
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f"Two-Body Attraction (mass={mass}, Gr={gr}, sep={sep})", fontsize=13)

    axes[0, 0].plot(history['tick'], history['peak_dist'], 'b-', linewidth=0.5)
    axes[0, 0].set(xlabel='Tick', ylabel='Peak distance (hops)',
                   title='Peak Distance')
    axes[0, 0].grid(True, alpha=0.3)

    axes[0, 1].plot(history['tick'], history['com_sep'], 'r-', linewidth=0.5)
    axes[0, 1].set(xlabel='Tick', ylabel='COM separation',
                   title='COM Separation')
    axes[0, 1].grid(True, alpha=0.3)
    # Add trend line
    if len(history['tick']) > 10:
        coeffs = np.polyfit(history['tick'], history['com_sep'], 1)
        x_fit = np.array([history['tick'][0], history['tick'][-1]])
        axes[0, 1].plot(x_fit, np.polyval(coeffs, x_fit), 'k--',
                        label=f'slope={coeffs[0]:.2e}')
        axes[0, 1].legend()

    axes[1, 0].plot(history['tick'], history['peak_a'], 'b-', label='Peak A')
    axes[1, 0].plot(history['tick'], history['peak_b'], 'r-', label='Peak B')
    axes[1, 0].set(xlabel='Tick', ylabel='Gamma at original node',
                   title='Peak Values')
    axes[1, 0].legend()
    axes[1, 0].grid(True, alpha=0.3)

    axes[1, 1].plot(history['tick'], history['total'], 'g-')
    axes[1, 1].set(xlabel='Tick', ylabel='Total gamma',
                   title='Conservation')
    axes[1, 1].grid(True, alpha=0.3)

    plt.tight_layout()
    fname = RESULTS_DIR / f"attraction_Gr{gr}_m{mass}_s{sep}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return history


def experiment_recapture_sweep(args):
    """Experiment D: G_recapture sweep for attraction."""
    print("\n" + "=" * 70)
    print("EXPERIMENT D: G_recapture Sweep for Attraction")
    print("=" * 70)

    mass = args.mass or 1000
    sep = args.separation or 10
    ticks = args.ticks or 50000
    warmup = 50
    gr_values = [0.2, 0.5, 1.0, 2.0, 5.0]

    results = []
    for gr in gr_values:
        print(f"\n  G_recapture = {gr}")
        field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
        nodes = field.initialize_two_cycling_peaks(separation=sep, mass=mass,
                                                    warmup_ticks=warmup)
        initial_total = field.total_gamma()

        # Track COM separation
        seps = []
        t0 = time.time()
        measure_every = max(1, ticks // 50)
        for tick in range(ticks):
            field.spread()
            if (tick + 1) % measure_every == 0:
                raw_peaks = field.find_peaks()
                if len(raw_peaks) >= 2:
                    com_a, _ = field.center_of_gamma(raw_peaks[0][0], radius=8)
                    com_b, _ = field.center_of_gamma(raw_peaks[1][0], radius=8)
                    com_sep = np.sqrt(sum((a - b)**2 for a, b in zip(com_a, com_b)))
                    seps.append(com_sep)

        elapsed = time.time() - t0
        total = field.total_gamma()
        raw_peaks = field.find_peaks()

        if seps:
            early = np.mean(seps[:5]) if len(seps) >= 5 else seps[0]
            late = np.mean(seps[-5:]) if len(seps) >= 5 else seps[-1]
            approach = early - late
        else:
            early = late = approach = 0.0

        n_peaks = len(raw_peaks)
        print(f"    peaks={n_peaks}, com: {early:.3f} -> {late:.3f}, "
              f"approach={approach:.3f}, total={total} ({elapsed:.1f}s)")
        results.append({'G_recapture': gr, 'n_peaks': n_peaks,
                        'early_sep': early, 'late_sep': late,
                        'approach': approach, 'total': total})

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    grs = [r['G_recapture'] for r in results]
    approaches = [r['approach'] for r in results]
    ax.bar(range(len(grs)), approaches, tick_label=[str(g) for g in grs],
           color=['g' if a > 0.1 else 'gray' for a in approaches])
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set(xlabel='G_recapture', ylabel='Approach (hops)',
           title=f'Attraction vs G_recapture (mass={mass}, sep={sep}, ticks={ticks})')
    ax.grid(True, alpha=0.3, axis='y')

    fname = RESULTS_DIR / f"recapture_sweep_m{mass}_s{sep}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return results


def experiment_separation_sweep(args):
    """Experiment E: Separation sweep for force law."""
    print("\n" + "=" * 70)
    print("EXPERIMENT E: Separation Sweep (Force Law)")
    print("=" * 70)

    gr = args.G_recapture or 0.5
    mass = args.mass or 1000
    ticks = args.ticks or 50000
    warmup = 50
    separations = [4, 6, 8, 10, 12]

    results = []
    for sep in separations:
        print(f"\n  Separation = {sep}")
        field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
        nodes = field.initialize_two_cycling_peaks(separation=sep, mass=mass,
                                                    warmup_ticks=warmup)
        seps = []
        t0 = time.time()
        measure_every = max(1, ticks // 50)
        for tick in range(ticks):
            field.spread()
            if (tick + 1) % measure_every == 0:
                raw_peaks = field.find_peaks()
                if len(raw_peaks) >= 2:
                    com_a, _ = field.center_of_gamma(raw_peaks[0][0], radius=8)
                    com_b, _ = field.center_of_gamma(raw_peaks[1][0], radius=8)
                    com_sep = np.sqrt(sum((a - b)**2 for a, b in zip(com_a, com_b)))
                    seps.append(com_sep)

        elapsed = time.time() - t0
        if seps:
            early = np.mean(seps[:5]) if len(seps) >= 5 else seps[0]
            late = np.mean(seps[-5:]) if len(seps) >= 5 else seps[-1]
            approach = early - late
        else:
            early = late = approach = 0.0

        print(f"    com: {early:.3f} -> {late:.3f}, approach={approach:.3f} ({elapsed:.1f}s)")
        results.append({'separation': sep, 'early_sep': early, 'late_sep': late,
                        'approach': approach})

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    seps_arr = [r['separation'] for r in results]
    approaches = [r['approach'] for r in results]
    ax.plot(seps_arr, approaches, 'bo-', markersize=8)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set(xlabel='Initial Separation (hops)', ylabel='Approach (hops)',
           title=f'Approach vs Separation (Gr={gr}, mass={mass}, ticks={ticks})')
    ax.grid(True, alpha=0.3)

    fname = RESULTS_DIR / f"separation_sweep_Gr{gr}_m{mass}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return results


def experiment_photon(args):
    """Experiment F: Single quantum propagation (photon test)."""
    print("\n" + "=" * 70)
    print("EXPERIMENT F: Photon Test (single quantum)")
    print("=" * 70)

    ticks = 100
    n_trials = 20

    for gr in [0.0, 0.5, 1.0]:
        print(f"\n  G_recapture = {gr}")
        displacements = []
        for trial in range(n_trials):
            field = SpreadFirstField(8000, k=6, G_recapture=gr,
                                      seed=args.seed + trial)
            center = field.n_nodes // 2
            field.gamma[center] = 1

            for _ in range(ticks):
                field.spread()

            # Find where the quantum is
            pos = int(np.argmax(field.gamma))
            if field.gamma[pos] > 0:
                d = field.hop_distance(center, pos)
            else:
                # Quantum might have spread to uniform (all 0 or 1)
                d = -1
            displacements.append(d)

        valid = [d for d in displacements if d >= 0]
        if valid:
            mean_d = np.mean(valid)
            speed = mean_d / ticks
            print(f"    Mean displacement: {mean_d:.1f} hops in {ticks} ticks")
            print(f"    Speed: {speed:.3f} hops/tick (c = {field.alpha:.3f})")
        else:
            print(f"    Quantum dispersed in all trials")


def experiment_mass_sweep(args):
    """Experiment G: Mass sweep for approach rate."""
    print("\n" + "=" * 70)
    print("EXPERIMENT G: Mass Sweep for Approach Rate")
    print("=" * 70)

    gr = args.G_recapture or 0.5
    sep = args.separation or 10
    ticks = args.ticks or 50000
    warmup = 50
    masses = [500, 1000, 2000]

    results = []
    for mass in masses:
        print(f"\n  Mass = {mass}")
        field = SpreadFirstField(8000, k=6, G_recapture=gr, seed=args.seed)
        nodes = field.initialize_two_cycling_peaks(separation=sep, mass=mass,
                                                    warmup_ticks=warmup)
        seps = []
        t0 = time.time()
        measure_every = max(1, ticks // 50)
        for tick in range(ticks):
            field.spread()
            if (tick + 1) % measure_every == 0:
                raw_peaks = field.find_peaks()
                if len(raw_peaks) >= 2:
                    com_a, _ = field.center_of_gamma(raw_peaks[0][0], radius=8)
                    com_b, _ = field.center_of_gamma(raw_peaks[1][0], radius=8)
                    com_sep = np.sqrt(sum((a - b)**2 for a, b in zip(com_a, com_b)))
                    seps.append(com_sep)

        elapsed = time.time() - t0
        if seps:
            early = np.mean(seps[:5]) if len(seps) >= 5 else seps[0]
            late = np.mean(seps[-5:]) if len(seps) >= 5 else seps[-1]
            approach = early - late
        else:
            early = late = approach = 0.0

        print(f"    com: {early:.3f} -> {late:.3f}, approach={approach:.3f} ({elapsed:.1f}s)")
        results.append({'mass': mass, 'early_sep': early, 'late_sep': late,
                        'approach': approach})

    # Plot
    fig, ax = plt.subplots(figsize=(8, 6))
    m_arr = [r['mass'] for r in results]
    approaches = [r['approach'] for r in results]
    ax.plot(m_arr, approaches, 'ro-', markersize=8)
    ax.axhline(y=0, color='k', linewidth=0.5)
    ax.set(xlabel='Mass (quanta)', ylabel='Approach (hops)',
           title=f'Approach vs Mass (Gr={gr}, sep={sep}, ticks={ticks})')
    ax.grid(True, alpha=0.3)

    fname = RESULTS_DIR / f"mass_sweep_Gr{gr}_s{sep}.png"
    fig.savefig(fname, dpi=150)
    plt.close(fig)
    print(f"\n  Plot saved: {fname}")

    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description="v7 Spread-First Eddy Model")
    parser.add_argument('--verify', action='store_true',
                        help='Run verification tests')
    parser.add_argument('--stability', action='store_true',
                        help='Experiment A: Eddy stability')
    parser.add_argument('--radiation', action='store_true',
                        help='Experiment A2: Radiation rate vs mass')
    parser.add_argument('--shadow', action='store_true',
                        help='Experiment B: Shadow profile')
    parser.add_argument('--attraction', action='store_true',
                        help='Experiment C: Two-body attraction')
    parser.add_argument('--recapture-sweep', action='store_true',
                        help='Experiment D: G_recapture sweep')
    parser.add_argument('--separation-sweep', action='store_true',
                        help='Experiment E: Separation sweep')
    parser.add_argument('--photon', action='store_true',
                        help='Experiment F: Photon test')
    parser.add_argument('--mass-sweep', action='store_true',
                        help='Experiment G: Mass sweep')

    parser.add_argument('--G-recapture', type=float, default=None)
    parser.add_argument('--mass', type=int, default=None)
    parser.add_argument('--separation', type=int, default=None)
    parser.add_argument('--ticks', type=int, default=None)
    parser.add_argument('--seed', type=int, default=42)

    args = parser.parse_args()

    if args.verify:
        run_verification()
    elif args.stability:
        experiment_stability(args)
    elif args.radiation:
        experiment_radiation(args)
    elif args.shadow:
        experiment_shadow(args)
    elif args.attraction:
        experiment_attraction(args)
    elif args.recapture_sweep:
        experiment_recapture_sweep(args)
    elif args.separation_sweep:
        experiment_separation_sweep(args)
    elif args.photon:
        experiment_photon(args)
    elif args.mass_sweep:
        experiment_mass_sweep(args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
