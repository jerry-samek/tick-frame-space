# Exp 138 Phase I0b — REDESIGNED estimator — PRE-REGISTRATION

**Date:** 2026-07-10. **Supersedes** `PREREG_I0.md` (kept for the record).
**Why:** the I0 estimator failed its own expander control at unit-test time, before the calibration gate ran: on random_regular(1728, 6) the pre-peak window is 4 points and the log-log fit wins spuriously (ê = 3.84, classified `poly`, R²_poly 0.990 > R²_exp 0.956). Root cause: near-total saturation — an expander's shells are all boundary; the pre-peak window is too short for R² comparison alone. Fresh registration per I0's own FAIL rule; the redesign is calibrated only against the signed controls, no dynamics data exists yet.

## Estimator I0b (frozen)

- **Shell counts:** unchanged (mean BFS shells over 64 seeded-rng sources).
- **Window:** r ∈ [1, r_cut], r_cut = max r such that cumulative ball ≤ N/2. Require ≥ 3 points, else `degenerate`.
- **Features:** median shell ratio ρ_med = median{N̄(r+1)/N̄(r)} over the window; both fits (log-log → ê, R²_poly; semilog → rate, R²_exp) on the window.
- **Classification:** `exp` iff ρ_med ≥ 1.9 OR R²_exp > R²_poly; else `poly`.
  (Rationale: trees have ρ_med = b ≥ 2 exactly; expanders ρ_med ≈ k−1; lattices' early ratios decay below 1.9 by the median. The 1.9 threshold sits between the 2D/3D lattice medians and the binary tree's 2.0; the gate below verifies the margin empirically on all four controls.)

## Controls and Gate G-I0 (unchanged from PREREG_I0)

Same four signed controls, same expectations, same PASS bands construction (band_2d, band_3d = measured torus ê ± 0.25), expander ≥ 9/10 seeds `exp`. Additional recorded margin: min over exp-controls of ρ_med minus max over lattice-controls of ρ_med must be > 0.3 (the threshold must not sit on a knife edge).
