"""Investigate why peaks don't attract.

The nonlinear spread alpha_eff = alpha / (1 + G * gamma) is purely local
and isotropic. It prevents dispersal but doesn't create directional flow.

For attraction, we need gamma to flow preferentially toward regions of
higher gamma. Options:

1. GRADIENT-DEPENDENT SPREAD: instead of reducing spread uniformly at
   high-gamma nodes, make spread asymmetric based on neighbor gamma values.
   A node sends MORE to neighbors with higher gamma (flow toward mass).

2. ABSORPTION: high-gamma nodes pull gamma from neighbors. Instead of
   reducing outflow, increase inflow. alpha_eff_inflow depends on the
   RECEIVING node's gamma.

3. PRESSURE MODEL: spread is driven by gamma DIFFERENCE (gradient), not
   gamma value. Flow from high to low (normal diffusion) MINUS a
   gravitational term that pulls flow toward high-gamma regions.

Let's test option 1: gradient-biased spread.
Instead of equal per_edge to all neighbors, weight by neighbor gamma:
  weight(j) = 1 + G_attract * gamma[j]
  flow(i->j) = outflow[i] * weight(j) / sum(weight(k) for k in neighbors(i))

This means gamma flows MORE toward high-gamma neighbors.
Combined with retention (alpha_eff depends on local gamma), this should:
- Hold peaks together (high gamma -> low alpha_eff -> less total outflow)
- Push leaked gamma toward other peaks (gradient-biased flow)
"""

import numpy as np
import scipy.sparse as sp
import time
from collections import deque
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gamma_field import SelfGravitatingField


class AttractingField(SelfGravitatingField):
    """Extension with gradient-biased spread for attraction."""

    def __init__(self, *args, G_attract=1.0, **kwargs):
        super().__init__(*args, **kwargs)
        self.G_attract = G_attract

    def spread_attracting(self):
        """Nonlinear spread with gradient bias.

        1. alpha_eff = alpha / (1 + G * gamma)  [retention at peaks]
        2. Outflow distributed to neighbors weighted by their gamma:
           flow(i->j) proportional to (1 + G_attract * gamma[j])

        This creates directional flow toward high-gamma regions (attraction)
        while retaining peaks (self-gravitation).

        Conservation: sum of outflow from i = outflow[i], distributed
        among neighbors. Sum in = sum out. Total conserved.
        """
        alpha_eff = self.alpha / (1.0 + self.G * self.gamma)
        outflow = alpha_eff * self.gamma

        # For each node, distribute outflow to neighbors weighted by
        # (1 + G_attract * gamma[neighbor])
        # This is more expensive than uniform spread (can't use simple spmv)
        # but still O(edges) per tick.

        gamma_new = self.gamma - outflow  # retained portion

        # Iterate over edges to compute weighted inflow
        # Use the sparse adjacency matrix structure
        A_csr = self.A.tocsr()
        for i in range(self.n_nodes):
            if outflow[i] <= 0:
                continue
            nbs = self.neighbors[i]
            if not nbs:
                gamma_new[i] += outflow[i]  # no neighbors, keep it
                continue

            # Weights for each neighbor
            weights = np.array([1.0 + self.G_attract * self.gamma[j]
                                for j in nbs])
            total_weight = weights.sum()
            if total_weight <= 0:
                gamma_new[i] += outflow[i]
                continue

            # Distribute
            for idx, j in enumerate(nbs):
                gamma_new[j] += outflow[i] * weights[idx] / total_weight

        self.gamma = gamma_new


def test_attraction():
    """Test if gradient-biased spread produces attraction."""
    print("=" * 70)
    print("TEST: Gradient-biased spread for peak attraction")
    print("=" * 70)

    # Parameters
    n_nodes = 8000
    G_retain = 50.0      # self-gravitation (retention)
    G_attract = 1.0      # attraction bias
    mass = 500.0
    separation = 10
    ticks = 500

    print(f"\n  G_retain={G_retain}, G_attract={G_attract}, "
          f"mass={mass}, sep={separation}")

    # Build field with attraction
    field = AttractingField(n_nodes, k=6, G=G_retain,
                             G_attract=G_attract)

    # Place two peaks
    nodes = field.place_peaks_equilateral(separation=separation, n_peaks=2)

    # Initialize simultaneously
    field.gamma[nodes[0]] = mass
    field.gamma[nodes[1]] = mass
    saved_G = field.G
    field.G = 0.0
    for _ in range(10):
        field.spread()
    field.G = saved_G

    initial_dist = field.hop_distance(nodes[0], nodes[1])
    initial_gamma = field.total_gamma()
    print(f"  Initial distance: {initial_dist} hops")
    print(f"  Initial total gamma: {initial_gamma:.4f}")
    print(f"  Initial peak A: {field.gamma[nodes[0]]:.4f}")
    print(f"  Initial peak B: {field.gamma[nodes[1]]:.4f}")

    # Run
    t0 = time.time()
    for tick in range(ticks):
        field.spread_attracting()

        if (tick + 1) % 100 == 0:
            total = field.total_gamma()
            drift = abs(total - initial_gamma) / initial_gamma
            peak_a = field.gamma[nodes[0]]
            peak_b = field.gamma[nodes[1]]

            # Find actual peak locations
            raw_peaks = field.find_peaks()
            if len(raw_peaks) >= 2:
                p0, p1 = raw_peaks[0][0], raw_peaks[1][0]
                d = field.hop_distance(p0, p1)
            elif len(raw_peaks) == 1:
                d = 0
            else:
                d = -1

            elapsed = time.time() - t0
            print(f"    Tick {tick+1:5d}: peak_A={peak_a:.3f} peak_B={peak_b:.3f} "
                  f"dist={d} total={total:.2f} drift={drift:.2e} "
                  f"({elapsed:.1f}s)")

    # Final state
    total = field.total_gamma()
    drift = abs(total - initial_gamma) / initial_gamma
    print(f"\n  Final total gamma: {total:.4f} (drift={drift:.2e})")
    print(f"  Final peak A (original node): {field.gamma[nodes[0]]:.4f}")
    print(f"  Final peak B (original node): {field.gamma[nodes[1]]:.4f}")

    raw_peaks = field.find_peaks()
    print(f"  Final peaks found: {len(raw_peaks)}")
    for i, (node, val) in enumerate(raw_peaks[:5]):
        print(f"    Peak {i}: node={node}, gamma={val:.4f}")

    if len(raw_peaks) >= 2:
        final_dist = field.hop_distance(raw_peaks[0][0], raw_peaks[1][0])
        print(f"\n  Distance: {initial_dist} -> {final_dist} hops")
        if final_dist < initial_dist:
            print("  ** ATTRACTION DETECTED **")
        elif final_dist == initial_dist:
            print("  No movement")
        else:
            print("  Repulsion?!")

    # Also test with different G_attract values
    print("\n" + "=" * 70)
    print("G_attract SWEEP (200 ticks each)")
    print("=" * 70)

    for ga in [0.0, 0.1, 1.0, 5.0, 10.0]:
        field2 = AttractingField(n_nodes, k=6, G=G_retain, G_attract=ga)
        nodes2 = field2.place_peaks_equilateral(separation=separation,
                                                  n_peaks=2)
        field2.gamma[nodes2[0]] = mass
        field2.gamma[nodes2[1]] = mass
        field2.G = 0.0
        for _ in range(10):
            field2.spread()
        field2.G = G_retain

        for _ in range(200):
            field2.spread_attracting()

        raw = field2.find_peaks()
        if len(raw) >= 2:
            d = field2.hop_distance(raw[0][0], raw[1][0])
        elif len(raw) == 1:
            d = 0
        else:
            d = -1
        total = field2.total_gamma()
        drift = abs(total - 2 * mass) / (2 * mass)
        print(f"  G_attract={ga:5.1f}: dist={initial_dist}->{d}, "
              f"peaks={len(raw)}, drift={drift:.2e}")


if __name__ == '__main__':
    test_attraction()
