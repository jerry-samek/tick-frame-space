#!/usr/bin/env python3
"""Phase 2e: Direct gradient field measurement.

Phase 2d showed source+sink yields ρ(r) ∝ r^(-1) at α=0, which
algebraically implies |∇ρ| ∝ r^(-2) = Newton's gravity. Phase 3b's
dynamical drift test was inconclusive because the test pattern
dissipated faster than it could move.

This script tests the algebraic claim directly: compute the gradient
vector at every cell from the steady-state E field, then check both
its magnitude (does it scale as 1/r^2?) and its direction (does it
point toward the star?).

No test pattern needed — we measure the force field that any test
pattern WOULD feel at every location.
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
N_TICKS = 2_000  # source/sink reaches steady state by ~tick 500
SEED = 42

STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20
SINK_RADIUS = 0.45
ALPHA = 0.0  # cleanest density slope (−0.99) → predicted gradient slope −1.99

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
            print(f"  tick {t}, total_E={int(E.sum()):,}, ({t/(time.time()-t0):.0f} t/s)")

    return coords, src, dst, E, distances


def compute_gradient_field(coords, src, dst, E):
    """At each cell, estimate ∇E using neighbor finite differences:
        ∇E(c) ≈ Σ_n (E[n] - E[c]) · (n - c) / |n - c|^2
    Vectorized via np.add.at over directed edges.
    """
    n_nodes = E.shape[0]

    # For each directed edge (c → n), contribution to ∇E(c) is:
    #   (E[n] - E[c]) * (coords[n] - coords[c]) / |coords[n] - coords[c]|^2
    delta_E = (E[dst] - E[src]).astype(np.float64)  # (2M,)
    delta_pos = coords[dst] - coords[src]            # (2M, 3)
    dist_sq = (delta_pos ** 2).sum(axis=1)           # (2M,)
    dist_sq = np.where(dist_sq > 0, dist_sq, 1.0)
    weights = delta_E / dist_sq                       # (2M,)
    contributions = weights[:, None] * delta_pos      # (2M, 3)

    grad = np.zeros((n_nodes, 3), dtype=np.float64)
    np.add.at(grad, src, contributions)

    # Normalize by per-cell degree (so each gradient is the AVERAGE directional contribution)
    degree = np.bincount(src, minlength=n_nodes).astype(np.float64)
    degree = np.where(degree > 0, degree, 1.0)
    grad = grad / degree[:, None]

    return grad


def main():
    coords, src, dst, E, distances = run_to_steady_state()

    print(f"\nFinal E stats: max={int(E.max())}, mean={E.mean():.2f}, total={int(E.sum()):,}")

    # Compute gradient at each cell
    grad = compute_gradient_field(coords, src, dst, E)
    grad_mag = np.linalg.norm(grad, axis=1)

    # Radial unit vector from cell to star (for directional check)
    # Note: sign convention — gradient points toward HIGHER E, which should be toward star
    radial_to_star = STAR_CENTER[None, :] - coords  # (N, 3) vector from cell to star
    r = np.linalg.norm(radial_to_star, axis=1)
    radial_to_star_unit = np.where(
        r[:, None] > 0,
        radial_to_star / np.maximum(r, 1e-9)[:, None],
        0.0,
    )

    # Cosine of angle between ∇E and radial-to-star (1 = perfectly aligned, attractive force)
    grad_unit = np.where(
        grad_mag[:, None] > 0,
        grad / np.maximum(grad_mag, 1e-9)[:, None],
        0.0,
    )
    cos_alignment = (grad_unit * radial_to_star_unit).sum(axis=1)

    # Filter to interior cells (inside sink, with measurable gradient, not too close to star)
    interior_mask = (r > 0.02) & (r < SINK_RADIUS) & (grad_mag > 1e-9)
    n_interior = int(interior_mask.sum())
    print(f"\nInterior cells (0.02 < r < {SINK_RADIUS}, |∇E| > 0): {n_interior}")

    # === Magnitude analysis: log-log fit |∇E| vs r ===
    r_int = r[interior_mask]
    g_int = grad_mag[interior_mask]
    cos_int = cos_alignment[interior_mask]

    # Bin by distance, take MEAN |∇E| per bin
    n_bins = 25
    bin_edges = np.logspace(np.log10(r_int.min()), np.log10(r_int.max()), n_bins + 1)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    g_binned = np.zeros(n_bins)
    cos_binned = np.zeros(n_bins)
    counts = np.zeros(n_bins)
    bin_idx = np.digitize(r_int, bin_edges) - 1
    for i in range(n_bins):
        mask = bin_idx == i
        if mask.any():
            g_binned[i] = g_int[mask].mean()
            cos_binned[i] = cos_int[mask].mean()
            counts[i] = mask.sum()

    print("\n=== Gradient magnitude vs radius ===")
    print(f"{'r':>8s}  {'|∇E|':>10s}  {'cos(θ)':>8s}  count")
    for i in range(n_bins):
        if counts[i] > 0:
            print(f"  {bin_centers[i]:>6.4f}  {g_binned[i]:>10.4f}  "
                  f"{cos_binned[i]:>+7.3f}  {int(counts[i]):>6d}")

    slope, intercept, r2 = fit_loglog_slope(bin_centers, g_binned)
    print(f"\nMagnitude slope = {slope:.3f}  (Newton: -2.0)  r² = {r2:.3f}")

    # === Direction analysis: average alignment ===
    # Aggregate cos in distance bins to see if it stays ≈ 1.0 across radii
    overall_cos = cos_int.mean()
    print(f"\nOverall mean cos(angle to star direction): {overall_cos:+.3f}")
    print(f"  (1.0 = field perfectly attractive, -1.0 = perfectly repulsive, 0.0 = isotropic noise)")

    # === Save results ===
    with open(os.path.join(OUT_DIR, 'phase2e_gradient_field.json'), 'w') as f:
        json.dump({
            'alpha': ALPHA,
            'slope': float(slope),
            'r_squared': float(r2),
            'overall_cos_alignment': float(overall_cos),
            'r_centers': bin_centers.tolist(),
            'grad_magnitude_binned': g_binned.tolist(),
            'cos_alignment_binned': cos_binned.tolist(),
            'counts': counts.tolist(),
        }, f, indent=2)

    # === Verdict ===
    if -2.5 < slope < -1.5 and r2 > 0.5 and overall_cos > 0.5:
        print("\n>>> Phase 2e PASS: gradient field is Newton-shaped AND radially attractive.")
        print(">>> Substrate gravity is real (static profile demonstrates the force law).")
    elif overall_cos > 0.5 and r2 > 0.5:
        print(f"\n>>> Phase 2e PARTIAL: attractive radial field with slope {slope:.3f} (not -2).")
        print(">>> Force law exists but exponent differs from Newton.")
    elif overall_cos < 0.0:
        print("\n>>> Phase 2e ANTI: gradient points AWAY from star (repulsive).")
    else:
        print("\n>>> Phase 2e UNCLEAR: weak correlation, see numbers above.")


if __name__ == '__main__':
    main()
