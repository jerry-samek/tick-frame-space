#!/usr/bin/env python3
"""R6 ratification (RAW 402): re-measure the 133 source+sink field as a clean
Green-function POTENTIAL test across >=20 seeds, with NO per-cell smoothing,
and obtain the force slope by ANALYTIC differentiation (force_slope = pot_slope - 1).

PRE-REGISTRATION (committed before running):
  Hypothesis H_R6: the alpha=0 source+sink diffusion produces the 3D Laplacian
  Green-function potential rho(r) ~ r^-1 (slope -1), converged (not a draining
  transient), robust across seeds. The phase2f '-0.65 force slope' was an
  analyst-side smoothing artifact; the correct force slope = pot_slope - 1 ~ -2.

  Observables:
    O1 (convergence, seed=42): potential slope on far-field shells r in [0.05,0.40]
       and total interior energy, snapshotted over ticks -> does slope stabilize?
    O2 (seed sweep, 20 seeds): final far-field potential slope; report median + IQR.

  Pre-committed verdicts:
    - CONVERGED if, in O1, the potential slope changes < 0.10 between the last two
      snapshots AND interior total_E changes < 5% over the last 1000 ticks.
    - GREEN-FUNCTION CONFIRMED if median potential slope across 20 seeds in [-1.15,-0.85]
      with IQR < 0.20. Then analytic force slope = median - 1 (report it).
    - OVERTURNED-TRANSIENT if not converged (slope still walking) -> the -0.99 was a transient.
    - OVERTURNED-SEED if median outside [-1.15,-0.85] or IQR >= 0.20 -> single-seed/fragile.
  NO smoothing. NO finite-difference force. Fit the potential; differentiate analytically.
"""
import sys, os, json, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from substrate import build_rgg, init_state, tick
from visualization import radial_density_profile, fit_loglog_slope

# EXACT phase2d config.
N_NODES = 100_000
RADIUS = 0.025
ALPHA = 0.0
STAR_CENTER = np.array([0.5, 0.5, 0.5])
STAR_MASS = 1000
STAR_CELLS = 50
BACKGROUND_PER_CELL = 20
SINK_RADIUS = 0.45

# far-field fit window: outside the source region, inside the sink.
FIT_RMIN, FIT_RMAX = 0.05, 0.40
FIT_BINS = 20


def setup(seed):
    coords, src, dst, back_edge = build_rgg(N_NODES, RADIUS, seed=seed)
    distances = np.linalg.norm(coords - STAR_CENTER[None, :], axis=1)
    star_idx = np.argsort(distances)[:STAR_CELLS]
    star_cell_E = STAR_MASS // STAR_CELLS
    sink_mask = distances > SINK_RADIUS
    energy_init = np.full(N_NODES, BACKGROUND_PER_CELL, dtype=np.int64)
    energy_init[star_idx] = star_cell_E + BACKGROUND_PER_CELL
    energy_init[sink_mask] = 0
    E, received = init_state(N_NODES, len(src), energy_init)
    interior = ~sink_mask
    return coords, src, dst, back_edge, E, received, star_idx, sink_mask, interior, star_cell_E


def far_field_slope(E, coords):
    r_c, dens = radial_density_profile(E, coords, STAR_CENTER,
                                       n_bins=FIT_BINS, r_min=FIT_RMIN, r_max=FIT_RMAX)
    slope, intercept, r2 = fit_loglog_slope(r_c, dens)
    return slope, r2


def run_seed(seed, n_ticks, snapshots=None):
    coords, src, dst, back_edge, E, received, star_idx, sink_mask, interior, star_cell_E = setup(seed)
    snaps = []
    for t in range(1, n_ticks + 1):
        E, received = tick(E, received, src, dst, back_edge, alpha=ALPHA)
        E[star_idx] = star_cell_E + BACKGROUND_PER_CELL
        E[sink_mask] = 0
        if snapshots and t in snapshots:
            s, r2 = far_field_slope(E, coords)
            snaps.append((t, s, r2, int(E[interior].sum())))
    s, r2 = far_field_slope(E, coords)
    return s, r2, int(E[interior].sum()), snaps


def main():
    print(f"R6 potential re-fit: N={N_NODES}, radius={RADIUS}, alpha={ALPHA}, "
          f"source+sink, fit window r in [{FIT_RMIN},{FIT_RMAX}]")

    # --- O1: convergence on seed=42 ---
    print("\n--- O1 CONVERGENCE (seed=42) ---")
    snap_ticks = [250, 500, 1000, 2000, 3000, 4000, 5000]
    t0 = time.time()
    s, r2, e_int, snaps = run_seed(42, max(snap_ticks), snapshots=set(snap_ticks))
    print(f"  (ran {max(snap_ticks)} ticks in {time.time()-t0:.0f}s)")
    print(f"  {'tick':>5} {'pot_slope':>10} {'r2':>6} {'interior_E':>12}")
    for (t, sl, rr, ei) in snaps:
        print(f"  {t:>5} {sl:>10.3f} {rr:>6.3f} {ei:>12,}")
    converged = False
    if len(snaps) >= 2:
        d_slope = abs(snaps[-1][1] - snaps[-2][1])
        e_prev, e_last = snaps[-2][3], snaps[-1][3]
        d_E = abs(e_last - e_prev) / max(e_prev, 1)
        converged = (d_slope < 0.10) and (d_E < 0.05)
        print(f"  last-step |d slope|={d_slope:.3f} (<0.10?), "
              f"interior_E change={100*d_E:.1f}% (<5%?) -> "
              f"{'CONVERGED' if converged else 'NOT converged'}")

    # --- O2: seed sweep ---
    n_seeds = 20
    sweep_ticks = max(snap_ticks)
    print(f"\n--- O2 SEED SWEEP ({n_seeds} seeds, {sweep_ticks} ticks each) ---")
    slopes, r2s = [], []
    for seed in range(n_seeds):
        ts = time.time()
        s, r2, e_int, _ = run_seed(seed, sweep_ticks)
        slopes.append(s); r2s.append(r2)
        print(f"  seed {seed:>2}: pot_slope={s:>7.3f}  r2={r2:>5.3f}  "
              f"interior_E={e_int:>11,}  ({time.time()-ts:.0f}s)")

    slopes = np.array(slopes); r2s = np.array(r2s)
    med = float(np.median(slopes))
    q1, q3 = np.percentile(slopes, [25, 75])
    iqr = float(q3 - q1)
    print(f"\n  potential slope: median={med:.3f}  IQR={iqr:.3f}  "
          f"[min {slopes.min():.3f}, max {slopes.max():.3f}]  mean r2={r2s.mean():.3f}")
    print(f"  ANALYTIC force slope = pot_slope - 1 = {med-1:.3f} (median)")

    print("\n========== R6 VERDICT ==========")
    print(f"O1 convergence: {'CONVERGED' if converged else 'NOT CONVERGED (transient)'}")
    green = (-1.15 <= med <= -0.85) and (iqr < 0.20)
    if green and converged:
        print(f"GREEN-FUNCTION CONFIRMED: potential slope {med:.3f} (IQR {iqr:.3f}); "
              f"analytic force slope {med-1:.3f} ~ -2. The substrate earns Newton's POTENTIAL; "
              f"the -0.65 'force' was a smoothing artifact (no smoothing used here).")
    elif not converged:
        print(f"OVERTURNED-TRANSIENT: slope had not converged at {sweep_ticks} ticks "
              f"-> the -0.99 was a transient, not a steady state.")
    elif not (-1.15 <= med <= -0.85):
        print(f"OVERTURNED-SHAPE: median slope {med:.3f} is not the 3D Green function (-1). "
              f"Integer quantization may alter the potential.")
    else:
        print(f"OVERTURNED-SEED: IQR {iqr:.3f} >= 0.20 -> single-seed value was fragile.")

    out = os.path.join(HERE, 'results', 'r6_potential_refit.json')
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, 'w') as f:
        json.dump({'convergence_snaps': snaps, 'converged': converged,
                   'sweep_slopes': slopes.tolist(), 'sweep_r2': r2s.tolist(),
                   'median_slope': med, 'iqr': iqr, 'force_slope_analytic': med - 1}, f, indent=2)
    print(f"\nsaved -> {out}")


if __name__ == "__main__":
    main()
