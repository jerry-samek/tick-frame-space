#!/usr/bin/env python3
"""
Experiment 128 v11 - Phase 4: Gravitational Time Dilation from rho(r)

Phase 1 measured the deposit density profile rho(r) on a 3D random
geometric graph and found rho(r) ~ A/r (the 3D Poisson potential
around a point source).

Phase 4 asks: if local clock-rate is modulated by local deposit load
(a node busy routing deposits has less capacity for its own cycle),
does the resulting gamma(r) match Einstein's gravitational redshift
form in the weak field?

Einstein (weak field):
    gamma_grav(r) = sqrt(1 + 2 phi / c^2)  ~=  1 + phi / c^2
                 ~=  1 - GM / (r c^2)

Our substrate:
    gamma_grav_local = 1 / (1 + rho_local / rho_scale)

    where rho_scale is a free coupling to be fit. In weak field
    (rho << rho_scale):
        gamma_grav ~=  1 - rho_local / rho_scale
                   ~=  1 - (A / rho_scale) / r

So gamma(r) should have a 1/r departure from 1, matching Einstein's
functional form. The coefficient (A / rho_scale) maps to GM_eff / c^2.

Falsification targets:
  - Does (1 - gamma) vs r go as 1/r on log-log? (slope -1)
  - Is the coefficient consistent with what A from Phase 1 already
    told us about the graph's gravitational coupling?

If both hold, that's the gravitational time dilation side of Einstein
falling out of the already-measured Phase 1 field, with a single free
coupling constant (rho_scale). We are NOT running a fresh simulation
with explicit clocks -- we are reinterpreting the field we already
have. If you want the clock sim, that's a follow-up.
"""

import os
import sys
import time
import numpy as np

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from phase1_star_only import build_graph, propagate_step
import phase1_star_only as p1

# Smaller graph -- convergence needs less work for this analysis
p1.N_NODES = 100_000
p1.SPHERE_R = 60.0
p1.TARGET_K = 24
p1.STAR_COUNT = 50
p1.L_STAR = 1.0
p1.BOUNDARY_FRACTION = 0.95
p1.SEED = 42

PROP_TICKS = 2000

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "results")
os.makedirs(OUT, exist_ok=True)


def measure_field():
    print("-- Phase 1 propagation (reused) --")
    pos, src, dst, degrees = build_graph()
    r_of = np.linalg.norm(pos, axis=1)

    star_ids = np.argsort(r_of)[:p1.STAR_COUNT]
    boundary_mask = r_of > p1.BOUNDARY_FRACTION * p1.SPHERE_R

    rho = np.zeros(p1.N_NODES, dtype=np.float32)
    rho[star_ids] = p1.L_STAR

    t0 = time.time()
    for tick in range(1, PROP_TICKS + 1):
        rho = propagate_step(rho, src, dst, degrees, p1.N_NODES)
        rho[star_ids] = p1.L_STAR
        rho[boundary_mask] = 0.0
        if tick % 500 == 0:
            interior = ~boundary_mask
            interior[star_ids] = False
            total = float(rho[interior].sum())
            print(f"  t={tick}  total_interior_rho={total:.1f}")
            sys.stdout.flush()
    print(f"  propagation: {time.time() - t0:.1f}s")

    return pos, r_of, rho, boundary_mask, star_ids


def bin_profile(r_of, rho, boundary_mask, star_ids):
    interior = ~boundary_mask
    interior[star_ids] = False
    r_min = 2.0
    r_max = p1.BOUNDARY_FRACTION * p1.SPHERE_R
    bin_edges = np.logspace(np.log10(r_min), np.log10(r_max), 40)
    bin_centers = np.sqrt(bin_edges[:-1] * bin_edges[1:])
    mean_rho = np.zeros(len(bin_centers))
    for i in range(len(bin_centers)):
        m = (r_of >= bin_edges[i]) & (r_of < bin_edges[i+1]) & interior
        if m.sum() > 0:
            mean_rho[i] = rho[m].mean()
    return bin_centers, mean_rho


def analyze(bin_centers, mean_rho):
    """Fit Einstein's weak-field form to (1 - gamma) vs r.

    Under gamma_local = 1 / (1 + rho/rho_scale):
      1 - gamma ~=  rho / rho_scale        (weak field)
      With rho = A/r:
      1 - gamma ~=  (A/rho_scale) * (1/r)
      log(1 - gamma) ~=  log(A/rho_scale)  -  log(r)
    So slope should be exactly -1 if our interpretation tracks Einstein.

    Fit is restricted to the intermediate range [4, 0.5*R] where the
    graph profile most cleanly follows 1/r. Outside: source saturation
    (inner) and boundary absorption (outer) bend the curve.
    """
    fit_lo = 4.0
    fit_hi = 0.5 * p1.SPHERE_R
    valid = (mean_rho > 0) & (bin_centers >= fit_lo) & (bin_centers <= fit_hi)
    r_fit = bin_centers[valid]
    rho_fit = mean_rho[valid]

    # Full range (for plotting)
    valid_all = mean_rho > 0
    r = bin_centers[valid_all]
    rho = mean_rho[valid_all]

    # Fit A from rho(r) = A/r on log-log, restricted range
    slope_rho, intercept_rho = np.polyfit(np.log(r_fit), np.log(rho_fit), 1)
    A_fit = np.exp(intercept_rho) if abs(slope_rho + 1.0) < 0.5 else \
            np.exp(intercept_rho) * r_fit[0] ** (slope_rho + 1)
    print(f"  Phase 1 field fit (r in [{fit_lo:.1f},{fit_hi:.1f}]):")
    print(f"    rho(r) slope = {slope_rho:.3f}   (expect ~ -1 in clean 3D)")

    # Set rho_scale >> rho for weak-field linearity. Shape is what we test.
    rho_scale = rho.max() * 2.0
    gamma = 1.0 / (1.0 + rho / rho_scale)
    one_minus_gamma = 1.0 - gamma

    gamma_fit = 1.0 / (1.0 + rho_fit / rho_scale)
    omg_fit = 1.0 - gamma_fit

    # Fit (1 - gamma) vs r on log-log, restricted range
    slope_g, intercept_g = np.polyfit(np.log(r_fit), np.log(omg_fit), 1)
    coeff = np.exp(intercept_g)
    print(f"  (1 - gamma) slope   = {slope_g:.3f}   (Einstein weak-field: -1.000)")
    print(f"  coefficient in 1/r  = {coeff:.4f}")

    return r, rho, gamma, one_minus_gamma, rho_scale, slope_g, A_fit, \
           slope_rho, (fit_lo, fit_hi)


def plot(r, rho, gamma, one_minus_gamma, rho_scale, slope_g, A_fit,
         slope_rho, fit_range):
    fig, axes = plt.subplots(1, 3, figsize=(17, 5))

    # 1) Density profile
    ax = axes[0]
    ax.loglog(r, rho, 'bo-', ms=3, lw=0.8, label='measured rho(r)')
    rr = np.logspace(np.log10(r.min()), np.log10(r.max()), 200)
    ax.loglog(rr, A_fit / rr, 'k--', lw=1, alpha=0.5, label=f'A/r fit, A={A_fit:.2f}')
    ax.set_xlabel('r'); ax.set_ylabel('rho(r)')
    ax.set_title('Phase 1 field (reused)')
    ax.legend(fontsize=9); ax.grid(True, which='both', alpha=0.3)

    # 2) gamma(r)
    ax = axes[1]
    ax.plot(r, gamma, 'go-', ms=3, lw=0.8)
    ax.axhline(1.0, color='gray', ls=':', alpha=0.5)
    ax.set_xlabel('r'); ax.set_ylabel(r'$\gamma_{grav}(r)$')
    ax.set_title('Local clock rate gamma(r) = 1 / (1 + rho/rho_scale)')
    ax.grid(True, alpha=0.3)

    # 3) (1 - gamma) vs r on log-log -- the Einstein-form test
    ax = axes[2]
    ax.loglog(r, one_minus_gamma, 'ro-', ms=3, lw=0.8,
              label=f'measured, slope={slope_g:.3f}')
    ax.axvspan(fit_range[0], fit_range[1], color='yellow', alpha=0.1,
               label=f'fit range [{fit_range[0]:.0f},{fit_range[1]:.0f}]')
    # 1/r reference anchored to middle of fit range
    mid = np.sqrt(fit_range[0] * fit_range[1])
    mid_val = np.interp(mid, r, one_minus_gamma)
    ax.loglog(rr, mid_val * (mid / rr), 'k--', lw=1, alpha=0.4,
              label='Einstein 1/r (slope -1)')
    ax.set_xlabel('r'); ax.set_ylabel(r'$1 - \gamma_{grav}$')
    ax.set_title('Einstein weak-field redshift test')
    ax.legend(fontsize=9); ax.grid(True, which='both', alpha=0.3)

    plt.suptitle('Phase 4: gravitational time dilation from rho(r)', fontsize=13)
    plt.tight_layout()
    path = os.path.join(OUT, 'phase4_time_dilation.png')
    plt.savefig(path, dpi=140)
    plt.close()
    print(f"  saved: {path}")


def run():
    pos, r_of, rho, boundary_mask, star_ids = measure_field()
    bin_centers, mean_rho = bin_profile(r_of, rho, boundary_mask, star_ids)

    print()
    print("-- Gravitational redshift analysis --")
    r, rho_binned, gamma, one_minus_gamma, rho_scale, slope_g, A_fit, \
        slope_rho, fit_range = analyze(bin_centers, mean_rho)

    # Effective gravitational coupling
    # gamma ~= 1 - GM_eff / (r * c^2)  =>  GM_eff/c^2 = A / rho_scale
    GM_eff_over_c2 = A_fit / rho_scale
    print()
    print(f"  Effective GM/c^2  = {GM_eff_over_c2:.4f} (natural units)")
    print(f"  (this is the coefficient of 1/r in 1-gamma)")
    print()

    if abs(slope_g + 1.0) < 0.1:
        verdict = "YES -- slope is -1 within tolerance, matches Einstein's 1/r form"
    else:
        verdict = f"QUESTIONABLE -- slope {slope_g:.3f} differs from Einstein's -1"
    print(f"  Does it match Einstein?  {verdict}")

    plot(r, rho_binned, gamma, one_minus_gamma, rho_scale, slope_g, A_fit,
         slope_rho, fit_range)


if __name__ == '__main__':
    run()
