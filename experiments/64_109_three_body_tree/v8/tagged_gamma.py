"""v8: Self-Subtracting Tagged Quanta.

v6 proved self-binding (D~1/M^2, v~c/M) but no attraction. Root cause: entity's
own gamma (~400 at center) drowns any signal from a distant entity (~0.05 at
10 hops). SNR is 1:8000.

The fix: self-subtraction. Each quantum is TAGGED with its source entity ID.
Self-gravitation uses TOTAL gamma (binding). Movement uses EXTERNAL gamma only
(total minus own tag). Signal from other entities is clean, not drowned.

Core physics:
    alpha_eff = alpha / (1 + G * total_gamma)   # binding from total
    external = total_gamma[nb] - tagged[self][nb] # self-subtracted gradient
    best_nb = argmax(external over neighbors)     # clean signal

Commit-counter from v5: entity sits for M ticks, then reads external gradient
and hops 1 position. v = c/M.

Usage:
    python tagged_gamma.py --verify
    python tagged_gamma.py --phase1
    python tagged_gamma.py --phase2
    python tagged_gamma.py --phase3
    python tagged_gamma.py --mass-sweep

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
# TaggedGammaField
# ===========================================================================

class TaggedGammaField(QuantumGammaField):
    """Integer stochastic gamma field with per-entity tagging.

    Each quantum is tagged with its source entity ID. The total gamma at
    each node is the sum of all tags. Self-gravitation (binding) uses total
    gamma. External gamma (for movement decisions) excludes the entity's
    own tagged quanta.
    """

    def __init__(self, *args, entity_ids=None, **kwargs):
        kwargs['G_attract'] = 0.0  # no v6c attraction bias
        super().__init__(*args, **kwargs)
        self.entity_ids = entity_ids or []
        self.tagged = {
            eid: np.zeros(self.n_nodes, dtype=np.int64)
            for eid in self.entity_ids
        }
        # self.gamma holds the total (kept in sync)
        self.sync_total()

    def sync_total(self):
        """Recompute total gamma from all tagged arrays."""
        if self.entity_ids:
            self.gamma = sum(self.tagged[eid] for eid in self.entity_ids)
        else:
            self.gamma = np.zeros(self.n_nodes, dtype=np.int64)

    def external_gamma(self, node, exclude_eid):
        """External gamma at node, excluding one entity's contribution."""
        return int(self.gamma[node]) - int(self.tagged[exclude_eid][node])

    def external_gamma_array(self, exclude_eid):
        """Full external gamma array, excluding one entity."""
        return self.gamma - self.tagged[exclude_eid]

    def spread(self):
        """Stochastic spread with per-entity tagging.

        alpha_eff computed from TOTAL gamma (self-gravitation for binding).
        Each entity's quanta spread independently with the same alpha_eff.
        Distribution is uniform to random neighbors.
        Conservation: exact per entity and total.
        """
        gamma_float = self.gamma.astype(np.float64)
        alpha_eff = self.alpha / (1.0 + self.G * gamma_float)
        alpha_eff = np.clip(alpha_eff, 0.0, 1.0)

        for eid in self.entity_ids:
            n_leaving = self.rng.binomial(self.tagged[eid], alpha_eff)
            self.tagged[eid] -= n_leaving
            self._distribute_uniform(n_leaving, self.tagged[eid])

        self.sync_total()

    def initialize_tagged_peak(self, eid, center_node, mass, smooth_ticks=10):
        """Place tagged quanta at center and smooth."""
        self.tagged[eid][center_node] += int(mass)
        self.sync_total()
        if smooth_ticks > 0:
            saved_G = self.G
            self.G = 0.0
            for _ in range(smooth_ticks):
                self.spread()
            self.G = saved_G

    def initialize_tagged_peaks(self, entity_centers, mass, smooth_ticks=10):
        """Place multiple tagged peaks and smooth together.

        entity_centers: dict {eid: center_node}
        """
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
        """Total quanta for one entity."""
        return int(np.sum(self.tagged[eid]))

    def tagged_peak_node(self, eid):
        """Node with highest concentration of entity's tagged quanta."""
        return int(np.argmax(self.tagged[eid]))


# ===========================================================================
# Entity (commit-counter)
# ===========================================================================

class Entity:
    """An entity that moves via commit-counter, reading external gamma gradient.

    Sits for commit_mass ticks, then reads external gradient at neighbors
    and hops to the neighbor with highest external gamma. v = c/commit_mass.
    On hop, transfers ALL tagged quanta from old node to new node.
    """

    def __init__(self, eid, node, commit_mass=5):
        self.eid = eid
        self.node = node
        self.commit_mass = commit_mass
        self.commit_counter = 0
        self.prev_node = node
        self.hops = 0
        self.trajectory = []  # (tick, node) snapshots

    def advance(self, field, tick=None):
        """Advance one tick. Returns True if entity hopped."""
        self.commit_counter += 1
        if self.commit_counter >= self.commit_mass:
            self.commit_counter = 0

            # Read external gradient at neighbors
            best_nb = self.node
            best_ext = field.external_gamma(self.node, self.eid)
            for nb in field.neighbors[self.node]:
                ext = field.external_gamma(nb, self.eid)
                if ext > best_ext:
                    best_ext = ext
                    best_nb = nb

            # Move if gradient exists (neighbor has more external gamma)
            if best_nb != self.node:
                # Transfer ALL tagged quanta at old node to new node
                amount = field.tagged[self.eid][self.node]
                if amount > 0:
                    field.tagged[self.eid][self.node] -= amount
                    field.tagged[self.eid][best_nb] += amount
                self.prev_node = self.node
                self.node = best_nb
                self.hops += 1
                field.sync_total()
                return True
        return False

    def record(self, tick):
        """Record current position."""
        self.trajectory.append((tick, self.node))


# ===========================================================================
# Verification Tests
# ===========================================================================

def run_verification(seed=42):
    """Run all tagged gamma verification tests."""
    print("\n=== TAGGED GAMMA VERIFICATION TESTS ===\n")
    passed = 0
    failed = 0

    # Test 1: Per-entity conservation
    print("Test 1: Per-entity conservation (1000 ticks)")
    f = TaggedGammaField(1000, k=6, G=10.0, seed=seed, entity_ids=['A', 'B'])
    c = f.n_nodes // 2
    f.tagged['A'][c] = 500
    f.tagged['B'][c + 10] = 300
    f.sync_total()
    init_A = f.tagged_total('A')
    init_B = f.tagged_total('B')
    for _ in range(1000):
        f.spread()
    final_A = f.tagged_total('A')
    final_B = f.tagged_total('B')
    if final_A == init_A and final_B == init_B:
        print(f"  PASS: A={init_A}->{final_A}, B={init_B}->{final_B}")
        passed += 1
    else:
        print(f"  FAIL: A={init_A}->{final_A}, B={init_B}->{final_B}")
        failed += 1

    # Test 2: Total conservation
    print("Test 2: Total conservation")
    init_total = init_A + init_B
    final_total = f.total_gamma()
    if final_total == init_total:
        print(f"  PASS: total={init_total}->{final_total}")
        passed += 1
    else:
        print(f"  FAIL: total={init_total}->{final_total}")
        failed += 1

    # Test 3: No negatives
    print("Test 3: No negatives (500 ticks)")
    f3 = TaggedGammaField(1000, k=6, G=5.0, seed=seed, entity_ids=['X'])
    f3.tagged['X'][0] = 200
    f3.sync_total()
    neg_found = False
    for _ in range(500):
        f3.spread()
        if np.any(f3.tagged['X'] < 0):
            neg_found = True
            break
    if not neg_found:
        print(f"  PASS: min={f3.tagged['X'].min()}")
        passed += 1
    else:
        print(f"  FAIL: negative quanta found")
        failed += 1

    # Test 4: Reproducibility
    print("Test 4: Reproducibility (same seed)")
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
        print("  PASS: identical results")
        passed += 1
    else:
        diff = np.sum(np.abs(f4a.tagged['A'] - f4b.tagged['A']))
        print(f"  FAIL: diff={diff}")
        failed += 1

    # Test 5: Peak stability (single tagged peak self-binds)
    print("Test 5: Peak stability (G=10, 500 ticks)")
    f5 = TaggedGammaField(8000, k=6, G=10.0, seed=seed, entity_ids=['A'])
    center5 = f5.n_nodes // 2
    f5.initialize_tagged_peak('A', center5, 1000, smooth_ticks=10)
    peak_node = f5.tagged_peak_node('A')
    peak_val = f5.tagged['A'][peak_node]
    mean_val = f5.tagged_total('A') / f5.n_nodes
    for _ in range(500):
        f5.spread()
    peak_node2 = f5.tagged_peak_node('A')
    peak_val2 = f5.tagged['A'][peak_node2]
    mean_val2 = f5.tagged_total('A') / f5.n_nodes
    ratio = peak_val2 / max(mean_val2, 0.001)
    if ratio > 10:
        print(f"  PASS: peak={peak_val2}, mean={mean_val2:.3f}, ratio={ratio:.1f}")
        passed += 1
    else:
        print(f"  FAIL: peak={peak_val2}, mean={mean_val2:.3f}, ratio={ratio:.1f}")
        failed += 1

    # Test 6: External gamma correctness
    print("Test 6: External gamma correctness")
    f6 = TaggedGammaField(1000, k=6, G=10.0, seed=seed, entity_ids=['A', 'B'])
    f6.tagged['A'][100] = 500
    f6.tagged['B'][200] = 300
    f6.sync_total()
    # At node 100: A has 500, B has 0. External for A = total - A = 0
    ext_A_at_100 = f6.external_gamma(100, 'A')
    # At node 200: A has 0, B has 300. External for B = total - B = 0
    ext_B_at_200 = f6.external_gamma(200, 'B')
    # At node 100: External for B = total - B's contribution = 500
    ext_B_at_100 = f6.external_gamma(100, 'B')
    ok = ext_A_at_100 == 0 and ext_B_at_200 == 0 and ext_B_at_100 == 500
    if ok:
        print(f"  PASS: ext_A@100={ext_A_at_100}, ext_B@200={ext_B_at_200}, "
              f"ext_B@100={ext_B_at_100}")
        passed += 1
    else:
        print(f"  FAIL: ext_A@100={ext_A_at_100}, ext_B@200={ext_B_at_200}, "
              f"ext_B@100={ext_B_at_100}")
        failed += 1

    print(f"\n=== RESULTS: {passed}/{passed+failed} passed ===\n")
    return failed == 0


# ===========================================================================
# Phase 1: Single Peak Sanity
# ===========================================================================

def experiment_phase1(n_nodes=8000, G=10.0, mass=1000, ticks=5000, seed=42):
    """Single tagged peak stability — should match v6c behavior."""
    print("=" * 70)
    print("PHASE 1: Single Tagged Peak Stability")
    print("=" * 70)

    field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed, entity_ids=['A'])
    nodes = field.place_peaks_equilateral(separation=10, n_peaks=1)
    center = nodes[0]
    field.initialize_tagged_peak('A', center, mass, smooth_ticks=10)

    init_total = field.tagged_total('A')
    init_peak = field.tagged['A'][field.tagged_peak_node('A')]
    print(f"\n  Initial: total={init_total}, peak={init_peak}")

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        if (tick + 1) % 1000 == 0:
            total = field.tagged_total('A')
            peak_node = field.tagged_peak_node('A')
            peak_val = field.tagged['A'][peak_node]
            elapsed = time.time() - t0
            print(f"    Tick {tick+1:5d}: total={total}, peak={peak_val}, "
                  f"peak_node={peak_node} ({elapsed:.1f}s)")

    final_total = field.tagged_total('A')
    peak_node = field.tagged_peak_node('A')
    final_peak = field.tagged['A'][peak_node]
    drift = abs(final_total - init_total)
    dist_from_center = field.hop_distance(center, peak_node)

    print(f"\n  Final: total={final_total} (drift={drift}), "
          f"peak={final_peak}, dist_from_start={dist_from_center}")
    print(f"  Conservation: {'PASS' if drift == 0 else 'FAIL'}")
    print(f"  Binding: {'PASS' if final_peak > 10 else 'FAIL'}")


# ===========================================================================
# Phase 2: Two-Body Attraction (THE TEST)
# ===========================================================================

def experiment_phase2(n_nodes=8000, G=10.0, mass=1000, commit_mass=5,
                      separation=10, ticks=50000, seed=42):
    """Two-body attraction test with commit-counter entities."""
    print("=" * 70)
    print("PHASE 2: Two-Body Attraction")
    print("=" * 70)
    print(f"\n  G={G}, mass={mass}, commit_mass={commit_mass}, "
          f"sep={separation}, ticks={ticks}")

    # --- Setup ---
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

    init_dist = field.hop_distance(entities[0].node, entities[1].node)
    init_total = field.total_gamma()
    print(f"  Initial distance: {init_dist} hops")
    print(f"  Initial total gamma: {init_total}")
    print(f"  Initial A peak: {field.tagged['A'][field.tagged_peak_node('A')]}")
    print(f"  Initial B peak: {field.tagged['B'][field.tagged_peak_node('B')]}")

    # Measure external gradient at start
    ext_A_toward_B = max(
        field.external_gamma(nb, 'A') for nb in field.neighbors[entities[0].node]
    )
    ext_A_here = field.external_gamma(entities[0].node, 'A')
    print(f"  Initial ext gradient at A: here={ext_A_here}, "
          f"best_neighbor={ext_A_toward_B}")

    # --- Run ---
    diag_interval = max(ticks // 20, 1)
    distances = []
    hop_counts = {'A': 0, 'B': 0}

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        for ent in entities:
            moved = ent.advance(field, tick)
            if moved:
                hop_counts[ent.eid] += 1

        if (tick + 1) % diag_interval == 0:
            d = field.hop_distance(entities[0].node, entities[1].node)
            distances.append((tick + 1, d))
            total = field.total_gamma()
            total_A = field.tagged_total('A')
            total_B = field.tagged_total('B')

            # External gradient at A
            ext_best = max(
                (field.external_gamma(nb, 'A')
                 for nb in field.neighbors[entities[0].node]),
                default=0
            )
            ext_here = field.external_gamma(entities[0].node, 'A')

            elapsed = time.time() - t0
            print(f"    Tick {tick+1:6d}: dist={d:3d} A_mass={total_A} "
                  f"B_mass={total_B} ext_grad={ext_best - ext_here:+d} "
                  f"hops_A={hop_counts['A']} hops_B={hop_counts['B']} "
                  f"total={total} ({elapsed:.1f}s)")

    # --- Results ---
    final_dist = field.hop_distance(entities[0].node, entities[1].node)
    print(f"\n  Final distance: {init_dist} -> {final_dist} hops")
    print(f"  Total hops: A={hop_counts['A']}, B={hop_counts['B']}")
    print(f"  Conservation: {field.total_gamma()} "
          f"(drift={abs(field.total_gamma() - init_total)})")

    if final_dist < init_dist:
        print(f"  ** ATTRACTION DETECTED: distance decreased by "
              f"{init_dist - final_dist} hops **")
    elif final_dist == init_dist:
        print(f"  No net movement")
    else:
        print(f"  Distance increased by {final_dist - init_dist} hops")

    # --- Control: no entity movement (Brownian baseline) ---
    print(f"\n  --- Control: field-only (no entity movement) ---")
    field_ctrl = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                                  entity_ids=entity_ids)
    nodes_ctrl = field_ctrl.place_peaks_equilateral(separation=separation,
                                                     n_peaks=2)
    field_ctrl.initialize_tagged_peaks(
        {'A': nodes_ctrl[0], 'B': nodes_ctrl[1]}, mass, smooth_ticks=10)

    ctrl_init_dist = field_ctrl.hop_distance(nodes_ctrl[0], nodes_ctrl[1])
    t0_ctrl = time.time()
    for tick in range(ticks):
        field_ctrl.spread()
    # Track peak positions (Brownian drift only)
    peak_A = field_ctrl.tagged_peak_node('A')
    peak_B = field_ctrl.tagged_peak_node('B')
    ctrl_final_dist = field_ctrl.hop_distance(peak_A, peak_B)
    elapsed_ctrl = time.time() - t0_ctrl
    print(f"    Control distance: {ctrl_init_dist} -> {ctrl_final_dist} hops "
          f"(peak-based, {elapsed_ctrl:.1f}s)")

    # --- Plot ---
    if distances:
        fig, ax = plt.subplots(figsize=(10, 5))
        ticks_arr = [d[0] for d in distances]
        dists_arr = [d[1] for d in distances]
        ax.plot(ticks_arr, dists_arr, 'b-', linewidth=1.5, label='Entity distance')
        ax.axhline(y=init_dist, color='gray', linestyle='--', alpha=0.5,
                    label=f'Initial ({init_dist})')
        ax.set_xlabel('Tick')
        ax.set_ylabel('Hop distance')
        ax.set_title(f'Two-Body: G={G}, mass={mass}, commit_mass={commit_mass}')
        ax.legend()
        ax.grid(True, alpha=0.3)
        fig.tight_layout()
        fig.savefig(RESULTS_DIR / 'phase2_distance.png', dpi=150)
        plt.close(fig)
        print(f"\n  Plot saved: {RESULTS_DIR / 'phase2_distance.png'}")

    return distances


# ===========================================================================
# Phase 3: Three-Body Dynamics
# ===========================================================================

def experiment_phase3(n_nodes=8000, G=10.0, mass=1000, commit_mass=5,
                      separation=10, ticks=100000, seed=42):
    """Three-body dynamics with tagged quanta."""
    print("=" * 70)
    print("PHASE 3: Three-Body Dynamics")
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

    init_total = field.total_gamma()
    print(f"  Initial total gamma: {init_total}")
    for i, ent in enumerate(entities):
        print(f"  Entity {ent.eid}: node={ent.node}")

    # Diagnostics
    diag_interval = max(ticks // 50, 1)
    records = []

    t0 = time.time()
    for tick in range(ticks):
        field.spread()
        for ent in entities:
            ent.advance(field, tick)

        if (tick + 1) % diag_interval == 0:
            d_AB = field.hop_distance(entities[0].node, entities[1].node)
            d_AC = field.hop_distance(entities[0].node, entities[2].node)
            d_BC = field.hop_distance(entities[1].node, entities[2].node)
            records.append({
                'tick': tick + 1,
                'd_AB': d_AB, 'd_AC': d_AC, 'd_BC': d_BC,
                'mass_A': field.tagged_total('A'),
                'mass_B': field.tagged_total('B'),
                'mass_C': field.tagged_total('C'),
            })
            elapsed = time.time() - t0
            if (tick + 1) % (diag_interval * 5) == 0:
                print(f"    Tick {tick+1:7d}: AB={d_AB} AC={d_AC} BC={d_BC} "
                      f"({elapsed:.1f}s)")

    # Results
    total = field.total_gamma()
    print(f"\n  Final total gamma: {total} (drift={abs(total - init_total)})")
    if records:
        first = records[0]
        last = records[-1]
        print(f"  AB: {first['d_AB']} -> {last['d_AB']}")
        print(f"  AC: {first['d_AC']} -> {last['d_AC']}")
        print(f"  BC: {first['d_BC']} -> {last['d_BC']}")

    # Plot
    if records:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8))
        ticks_arr = [r['tick'] for r in records]
        ax1.plot(ticks_arr, [r['d_AB'] for r in records], label='A-B')
        ax1.plot(ticks_arr, [r['d_AC'] for r in records], label='A-C')
        ax1.plot(ticks_arr, [r['d_BC'] for r in records], label='B-C')
        ax1.set_ylabel('Hop distance')
        ax1.set_title(f'Three-Body: G={G}, mass={mass}, commit_mass={commit_mass}')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        ax2.plot(ticks_arr, [r['mass_A'] for r in records], label='A')
        ax2.plot(ticks_arr, [r['mass_B'] for r in records], label='B')
        ax2.plot(ticks_arr, [r['mass_C'] for r in records], label='C')
        ax2.set_xlabel('Tick')
        ax2.set_ylabel('Tagged mass')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        fig.tight_layout()
        fig.savefig(RESULTS_DIR / 'phase3_three_body.png', dpi=150)
        plt.close(fig)
        print(f"\n  Plot saved: {RESULTS_DIR / 'phase3_three_body.png'}")

    return records


# ===========================================================================
# Parameter Sweeps
# ===========================================================================

def experiment_mass_sweep(n_nodes=8000, G=10.0, commit_mass=5, separation=10,
                          ticks=50000, seed=42):
    """Sweep initial mass, measure approach rate."""
    print("=" * 70)
    print("MASS SWEEP")
    print("=" * 70)

    masses = [500, 1000, 2000]
    results = []

    for m in masses:
        print(f"\n  mass={m}:")
        field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                                 entity_ids=['A', 'B'])
        nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)
        field.initialize_tagged_peaks(
            {'A': nodes[0], 'B': nodes[1]}, m, smooth_ticks=10)
        entities = [
            Entity('A', nodes[0], commit_mass=commit_mass),
            Entity('B', nodes[1], commit_mass=commit_mass),
        ]
        init_dist = field.hop_distance(entities[0].node, entities[1].node)

        t0 = time.time()
        for tick in range(ticks):
            field.spread()
            for ent in entities:
                ent.advance(field, tick)

        final_dist = field.hop_distance(entities[0].node, entities[1].node)
        delta = init_dist - final_dist
        elapsed = time.time() - t0
        results.append({
            'mass': m, 'init_dist': init_dist, 'final_dist': final_dist,
            'delta': delta,
        })
        print(f"    dist: {init_dist} -> {final_dist} (delta={delta}) "
              f"in {elapsed:.1f}s")

    print(f"\n  Summary:")
    for r in results:
        print(f"    mass={r['mass']:5d}: delta={r['delta']:+d} hops")
    return results


def experiment_sep_sweep(n_nodes=8000, G=10.0, mass=1000, commit_mass=5,
                         ticks=50000, seed=42):
    """Sweep initial separation, measure approach rate."""
    print("=" * 70)
    print("SEPARATION SWEEP")
    print("=" * 70)

    separations = [4, 6, 8, 10]
    results = []

    for sep in separations:
        print(f"\n  separation={sep}:")
        field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                                 entity_ids=['A', 'B'])
        nodes = field.place_peaks_equilateral(separation=sep, n_peaks=2)
        field.initialize_tagged_peaks(
            {'A': nodes[0], 'B': nodes[1]}, mass, smooth_ticks=10)
        entities = [
            Entity('A', nodes[0], commit_mass=commit_mass),
            Entity('B', nodes[1], commit_mass=commit_mass),
        ]
        init_dist = field.hop_distance(entities[0].node, entities[1].node)

        t0 = time.time()
        for tick in range(ticks):
            field.spread()
            for ent in entities:
                ent.advance(field, tick)

        final_dist = field.hop_distance(entities[0].node, entities[1].node)
        delta = init_dist - final_dist
        elapsed = time.time() - t0
        results.append({
            'sep': sep, 'init_dist': init_dist, 'final_dist': final_dist,
            'delta': delta,
        })
        print(f"    dist: {init_dist} -> {final_dist} (delta={delta}) "
              f"in {elapsed:.1f}s")

    print(f"\n  Summary:")
    for r in results:
        print(f"    sep={r['sep']:3d}: delta={r['delta']:+d} hops")
    return results


def experiment_commit_sweep(n_nodes=8000, G=10.0, mass=1000, separation=10,
                            ticks=50000, seed=42):
    """Sweep commit_mass, measure velocity and approach rate."""
    print("=" * 70)
    print("COMMIT MASS SWEEP")
    print("=" * 70)

    commit_masses = [1, 3, 5, 10]
    results = []

    for cm in commit_masses:
        print(f"\n  commit_mass={cm}:")
        field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                                 entity_ids=['A', 'B'])
        nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)
        field.initialize_tagged_peaks(
            {'A': nodes[0], 'B': nodes[1]}, mass, smooth_ticks=10)
        entities = [
            Entity('A', nodes[0], commit_mass=cm),
            Entity('B', nodes[1], commit_mass=cm),
        ]
        init_dist = field.hop_distance(entities[0].node, entities[1].node)

        t0 = time.time()
        for tick in range(ticks):
            field.spread()
            for ent in entities:
                ent.advance(field, tick)

        final_dist = field.hop_distance(entities[0].node, entities[1].node)
        delta = init_dist - final_dist
        total_hops = entities[0].hops + entities[1].hops
        v_avg = total_hops / (2 * ticks)  # average speed per entity
        elapsed = time.time() - t0
        results.append({
            'commit_mass': cm, 'init_dist': init_dist,
            'final_dist': final_dist, 'delta': delta,
            'v_avg': v_avg, 'expected_v': 1.0 / cm,
        })
        print(f"    dist: {init_dist} -> {final_dist} (delta={delta}) "
              f"v_avg={v_avg:.4f} (expected c/{cm}={1.0/cm:.4f}) "
              f"in {elapsed:.1f}s")

    print(f"\n  Summary:")
    for r in results:
        print(f"    commit_mass={r['commit_mass']:3d}: delta={r['delta']:+d} "
              f"v={r['v_avg']:.4f} (c/{r['commit_mass']}={r['expected_v']:.4f})")
    return results


def experiment_g_sweep(n_nodes=8000, mass=1000, commit_mass=5, separation=10,
                       ticks=50000, seed=42):
    """Sweep G (self-gravitation), measure binding + approach rate."""
    print("=" * 70)
    print("G SWEEP")
    print("=" * 70)

    g_values = [1.0, 5.0, 10.0, 20.0]
    results = []

    for G in g_values:
        print(f"\n  G={G}:")
        field = TaggedGammaField(n_nodes, k=6, G=G, seed=seed,
                                 entity_ids=['A', 'B'])
        nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)
        field.initialize_tagged_peaks(
            {'A': nodes[0], 'B': nodes[1]}, mass, smooth_ticks=10)
        entities = [
            Entity('A', nodes[0], commit_mass=commit_mass),
            Entity('B', nodes[1], commit_mass=commit_mass),
        ]
        init_dist = field.hop_distance(entities[0].node, entities[1].node)

        t0 = time.time()
        for tick in range(ticks):
            field.spread()
            for ent in entities:
                ent.advance(field, tick)

        final_dist = field.hop_distance(entities[0].node, entities[1].node)
        delta = init_dist - final_dist
        mass_A = field.tagged_total('A')
        mass_B = field.tagged_total('B')
        elapsed = time.time() - t0
        results.append({
            'G': G, 'init_dist': init_dist, 'final_dist': final_dist,
            'delta': delta, 'mass_A': mass_A, 'mass_B': mass_B,
        })
        print(f"    dist: {init_dist} -> {final_dist} (delta={delta}) "
              f"mass_A={mass_A} mass_B={mass_B} in {elapsed:.1f}s")

    print(f"\n  Summary:")
    for r in results:
        print(f"    G={r['G']:5.1f}: delta={r['delta']:+d} "
              f"mass_A={r['mass_A']} mass_B={r['mass_B']}")
    return results


# ===========================================================================
# CLI
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(
        description='v8: Self-Subtracting Tagged Quanta')
    parser.add_argument('--verify', action='store_true',
                        help='Run verification tests')
    parser.add_argument('--phase1', action='store_true',
                        help='Single peak stability')
    parser.add_argument('--phase2', action='store_true',
                        help='Two-body attraction (THE test)')
    parser.add_argument('--phase3', action='store_true',
                        help='Three-body dynamics')
    parser.add_argument('--mass-sweep', action='store_true',
                        help='Mass parameter sweep')
    parser.add_argument('--sep-sweep', action='store_true',
                        help='Separation parameter sweep')
    parser.add_argument('--commit-sweep', action='store_true',
                        help='Commit mass sweep')
    parser.add_argument('--g-sweep', action='store_true',
                        help='G parameter sweep')

    # Parameters
    parser.add_argument('--n-nodes', type=int, default=8000)
    parser.add_argument('--G', type=float, default=10.0)
    parser.add_argument('--mass', type=int, default=1000)
    parser.add_argument('--commit-mass', type=int, default=5)
    parser.add_argument('--separation', type=int, default=10)
    parser.add_argument('--ticks', type=int, default=50000)
    parser.add_argument('--seed', type=int, default=42)

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
                          seed=args.seed)
    if args.phase3:
        experiment_phase3(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                          commit_mass=args.commit_mass,
                          separation=args.separation, ticks=args.ticks,
                          seed=args.seed)
    if args.mass_sweep:
        experiment_mass_sweep(n_nodes=args.n_nodes, G=args.G,
                              commit_mass=args.commit_mass,
                              separation=args.separation, ticks=args.ticks,
                              seed=args.seed)
    if args.sep_sweep:
        experiment_sep_sweep(n_nodes=args.n_nodes, G=args.G, mass=args.mass,
                             commit_mass=args.commit_mass, ticks=args.ticks,
                             seed=args.seed)
    if args.commit_sweep:
        experiment_commit_sweep(n_nodes=args.n_nodes, G=args.G,
                                mass=args.mass, separation=args.separation,
                                ticks=args.ticks, seed=args.seed)
    if args.g_sweep:
        experiment_g_sweep(n_nodes=args.n_nodes, mass=args.mass,
                           commit_mass=args.commit_mass,
                           separation=args.separation, ticks=args.ticks,
                           seed=args.seed)

    if not any([args.verify, args.phase1, args.phase2, args.phase3,
                args.mass_sweep, args.sep_sweep, args.commit_sweep,
                args.g_sweep]):
        print("No experiment selected. Use --help for options.")
        print("Quick start: python tagged_gamma.py --verify")


if __name__ == '__main__':
    main()
