# Exp 138 Phase I0c — final estimator — PRE-REGISTRATION

**Date:** 2026-07-10. **Supersedes** `PREREG_I0b.md` (which superseded `PREREG_I0.md`; both kept).
**Iteration record (all pre-dynamics, all against signed controls only):**
1. I0 (R² on the [2, r_peak] window) failed the expander control at unit-test time — saturation makes the pre-peak window too short (4 pts, spurious `poly`, ê=3.84).
2. I0b fixed the window ([1, r_cut] with cumulative ball ≤ N/2) and added a ratio_med ≥ 1.9 OR-clause; the ratio feature failed its own margin condition — a balanced tree read from uniform random sources has ratio_med 1.40 < torus3d's 1.55 (leaf-heavy shell profiles are not cleanly geometric).
3. Diagnostic: with the I0b *window*, the pure R² comparison alone separates all four controls with correct signs (gaps: torus2d +0.100, torus3d +0.081, tree −0.089, expander −0.026). The ratio clause was unnecessary; it is dropped from classification (ratio_med stays as a reported diagnostic).

## Estimator I0c (frozen)

- Shell counts: mean BFS shells over 64 seeded-rng sources (unchanged).
- Window: r ∈ [1, r_cut], r_cut = max r with cumulative ball ≤ N/2; ≥3 points else `degenerate`.
- Fits: log-log → (ê, R²_poly); semilog → (rate, R²_exp).
- **Classification: `poly` iff R²_poly ≥ R²_exp, else `exp`.** Nothing else classifies.

## Gate G-I0 (frozen)

- All four controls correct: torus2d & torus3d `poly`; tree & expander (≥9/10 seeds) `exp` with rate > 0.3.
- **Margins are recorded, not thresholded:** the minimum |R²_poly − R²_exp| over the controls is frozen into `results/i0.json` as `control_margin`. Any later dynamics reading whose gap is below `control_margin` must be flagged **near-boundary** in that phase's results (fragility caveat), but the sign still classifies. This avoids inventing a numeric floor after seeing the data.
- On PASS: freeze `band_2d`, `band_3d` (torus ê ± 0.25) and `control_margin`. These are the only numeric imports later phases may take.
