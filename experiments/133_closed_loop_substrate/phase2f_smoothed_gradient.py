#!/usr/bin/env python3
"""Phase 2f: Smoothed gradient measurement.

Phase 2e showed local |∇E| at each cell is dominated by noise (slope -0.1,
nearly isotropic direction past r=0.05). The macro density profile from
Phase 2d is smooth (ρ ∝ r^-1 at α=0), but per-cell gradient noise washes
out the predicted 1/r^2 force law.

This script tests whether SMOOTHED gradient (averaging over k-hop
neighborhoods) recovers a coherent 1/r^2 signal. If so, a test pattern
spanning ~k cells would feel Newton's force; if not, the rule's noise is
fundamental and no scale of test pattern would feel a coherent force.

Procedure:
  1. Run Phase 2d setup to steady state (α=0, source+sink)
  2. Smooth E by averaging with neighbors over k iterations (k = 3 and 5)
  3. Compute gradient of smoothed E
  4. Bin |∇E_smooth| and cos(angle to star) by radius
  5. Compare to Phase 2e's unsmoothed result
"""

import os
import sys
import json
import time
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from substrate import build_rgg, init_state, tick
from visualization import fit_loglog_slope


N_NODES = 100_000
RADIUS = 0.025
N_TICKS = 2_000
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20
SINK_RADIUS = 0.45
ALPHA = 0.0

SMOOTHING_LEVELS = [0, 1, 3, 5, 10]  # 0 = no smoothing (replicates Phase 2e)

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results')
os.makedirs(OUT_DIR, exist_ok=True)


def run_to_steady_state():
    print(f"Building RGG: N={N_NODES}, radius={RADIUS}")
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=SEED)
    n_directed = len(src)

    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]
    star_cell_E = STAR_MASS // STAR_CELLS
    sink_mask = distances > SINK_RADIUS

    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] = star_cell_E + BACKGROUND_PER_CELL
    energy_init[sink_mask] = 0

    E, received = init_state(N_NODES, n_directed, energy_init)

    print(f"Running {N_TICKS} ticks at alpha={ALPHA} to steady state...")
    t0 = time.time()
    for t in range(1, N_TICKS + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        E[star_idx] = star_cell_E + BACKGROUND_PER_CELL
        E[sink_mask] = 0
        if t % 500 == 0:
            print(f"  tick {t}, total_E={int(E.sum()):,}, "
                  f"({t/(time.time()-t0):.0f} t/s)")

    return coords, src, dst, E, distances


def smooth_field(E_float, src, dst, n_nodes, k):
    """Apply k iterations of neighbor-averaging smoothing.

    At each iteration: E_new[c] = (E[c] + sum E[neighbors]) / (1 + degree)
    """
    if k == 0:
        return E_float.copy()

    degree = np.bincount(src, minlength=n_nodes).astype(np.float64)
    inv_denom = 1.0 / np.maximum(1.0 + degree, 1.0)

    E_s = E_float.copy()
    for _ in range(k):
        # Sum of neighbor values for each cell
        sum_neighbors = np.zeros(n_nodes, dtype=np.float64)
        np.add.at(sum_neighbors, src, E_s[dst])
        E_s = (E_s + sum_neighbors) * inv_denom
    return E_s


def compute_gradient(E_float, coords, src, dst, n_nodes):
    """Per-cell gradient via neighbor finite differences."""
    delta_E = E_float[dst] - E_float[src]
    delta_pos = coords[dst] - coords[src]
    dist_sq = (delta_pos ** 2).sum(axis=1)
    dist_sq = np.where(dist_sq > 0, dist_sq, 1.0)
    weights = delta_E / dist_sq
    contributions = weights[:, None] * delta_pos

    grad = np.zeros((n_nodes, 3), dtype=np.float64)
    np.add.at(grad, src, contributions)

    degree = np.bincount(src, minlength=n_nodes).astype(np.float64)
    degree = np.where(degree > 0, degree, 1.0)
    grad = grad / degree[:, None]

    return grad


def analyze(grad, coords, distances, label):
    grad_mag = np.linalg.norm(grad, axis=1)

    radial_to_star = STAR_CENTER[None, :] - coords
    r = np.linalg.norm(radial_to_star, axis=1)
    radial_to_star_unit = np.where(
        r[:, None] > 0,
        radial_to_star / np.maximum(r, 1e-9)[:, None],
        0.0,
    )
    grad_unit = np.where(
        grad_mag[:, None] > 0,
        grad / np.maximum(grad_mag, 1e-9)[:, None],
        0.0,
    )
    cos_alignment = (grad_unit * radial_to_star_unit).sum(axis=1)

    interior_mask = (r > 0.02) & (r < SINK_RADIUS) & (grad_mag > 1e-9)
    r_int = r[interior_mask]
    g_int = grad_mag[interior_mask]
    cos_int = cos_alignment[interior_mask]

    n_bins = 25
    bin_edges = np.logspace(np.log10(r_int.min()), np.log10(r_int.max()), n_bins + 1)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    g_binned = np.zeros(n_bins)
    cos_binned = np.zeros(n_bins)
    counts = np.zeros(n_bins, dtype=int)
    bin_idx = np.digitize(r_int, bin_edges) - 1
    for i in range(n_bins):
        mask = bin_idx == i
        if mask.any():
            g_binned[i] = g_int[mask].mean()
            cos_binned[i] = cos_int[mask].mean()
            counts[i] = int(mask.sum())

    slope, intercept, r2 = fit_loglog_slope(bin_centers, g_binned)
    overall_cos = float(cos_int.mean())

    print(f"\n=== {label} ===")
    print(f"  slope = {slope:>7.3f}  r² = {r2:>5.3f}  "
          f"overall cos(θ) = {overall_cos:+.3f}")

    # Print first 10 bins so we can see how cos behaves with radius
    print(f"  bins (first 10): r, |∇E|, cos, count")
    for i in range(min(10, n_bins)):
        if counts[i] > 0:
            print(f"    r={bin_centers[i]:>6.4f}  "
                  f"|∇E|={g_binned[i]:>10.3e}  "
                  f"cos={cos_binned[i]:+.3f}  "
                  f"n={counts[i]:>5d}")

    return {
        'label': label,
        'slope': float(slope),
        'r_squared': float(r2),
        'overall_cos': overall_cos,
        'r_centers': bin_centers.tolist(),
        'grad_mag_binned': g_binned.tolist(),
        'cos_binned': cos_binned.tolist(),
        'counts': counts.tolist(),
    }


def main():
    coords, src, dst, E, distances = run_to_steady_state()
    n_nodes = E.shape[0]

    print(f"\nFinal E stats: max={int(E.max())}, mean={E.mean():.2f}, total={int(E.sum()):,}")

    E_float = E.astype(np.float64)

    results = []
    for k in SMOOTHING_LEVELS:
        E_s = smooth_field(E_float, src, dst, n_nodes, k)
        grad = compute_gradient(E_s, coords, src, dst, n_nodes)
        result = analyze(grad, coords, distances, f"smoothing k={k}")
        results.append(result)

    with open(os.path.join(OUT_DIR, 'phase2f_smoothed_gradients.json'), 'w') as f:
        json.dump(results, f, indent=2)

    # Final summary
    print("\n=== SUMMARY ===")
    print(f"{'k':>3s}  {'slope':>7s}  {'r²':>5s}  {'cos':>+6s}")
    for r in results:
        print(f"{int(r['label'].split('=')[1]):>3d}  "
              f"{r['slope']:>+7.3f}  "
              f"{r['r_squared']:>5.3f}  "
              f"{r['overall_cos']:>+.3f}")

    # Verdict
    best = min(results, key=lambda r: abs(r['slope'] + 2.0))
    if -2.5 < best['slope'] < -1.5 and best['r_squared'] > 0.5 and best['overall_cos'] > 0.5:
        print(f"\n>>> Phase 2f: Newton-shaped gradient recovered at smoothing k="
              f"{int(best['label'].split('=')[1])}.")
        print(">>> A test pattern spanning ~k cells would feel coherent 1/r^2 force.")
    elif any(r['overall_cos'] > 0.4 and r['r_squared'] > 0.4 for r in results):
        coherent = [r for r in results if r['overall_cos'] > 0.4 and r['r_squared'] > 0.4]
        print(f"\n>>> Phase 2f: smoothing recovers coherent radial structure but slope "
              f"differs from -2 (best: {best['slope']:+.3f}).")
    else:
        print(f"\n>>> Phase 2f: even with k={max(SMOOTHING_LEVELS)} smoothing, no coherent "
              f"Newton-shaped gradient. Rule noise is fundamental.")


if __name__ == '__main__':
    main()
