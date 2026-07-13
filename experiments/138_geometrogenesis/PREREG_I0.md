# Exp 138 Phase I0 — ball-growth-exponent instrument — PRE-REGISTRATION

**Date registered:** 2026-07-10, BEFORE `instrument.py` exists.
**Spec:** `docs/superpowers/specs/2026-07-10-exp138-geometrogenesis-design.md` §3.
**Role:** the instrument that gates P0 and P1. Reachable-range rule applied to the decision rule itself: G-I0 requires both the `poly` and `exp` classifications to be demonstrably attainable on signed controls before any dynamics run.

## Estimator (frozen)

- **Shell counts:** N̄(r) = mean over sources of |{u : d(u, source) = r}|, BFS on the undirected graph; `n_sources = 64` uniformly sampled without replacement (all nodes if N < 64), seeded rng.
- **Fit window:** r ∈ [2, r_peak] where r_peak = argmax_r N̄(r). Require ≥ 4 points (r_peak ≥ 5); fewer → classification `degenerate` (counts as FAIL for whatever gate consumes it).
- **Polynomial fit:** least squares on (log r, log N̄(r)) over the window → slope ê, R²_poly.
- **Exponential fit:** least squares on (r, log N̄(r)) over the same window → rate, R²_exp.
- **Classification:** `poly` iff R²_poly ≥ R²_exp else `exp`.

## Signed controls (frozen)

| control | expected cls | expected ê / rate |
|---|---|---|
| torus2d(24) (N=576) | poly | ê ≈ 1 |
| torus3d(12) (N=1728) | poly | ê ≈ 2 |
| random_regular(1728, 6), 10 seeds | exp | rate > 0.3 |
| binary_tree(10) (N=2047) | exp | rate > 0.3 |

## Gate G-I0 (frozen)

All four controls classified as expected (expander: ≥ 9/10 seeds). On PASS, freeze in `results/i0.json`:
- `band_2d` = [ê_2d − 0.25, ê_2d + 0.25], `band_3d` = [ê_3d − 0.25, ê_3d + 0.25] from the measured torus values.
These bands are the ONLY numeric imports later phases may take from I0. FAIL → stop, redesign estimator under a fresh PREREG; no post-hoc window tuning against dynamics data, ever.
