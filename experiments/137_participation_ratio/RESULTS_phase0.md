# Exp 137 Phase 0 — RESULTS (calibration gate + skeptic-mandated deconfounding)

**Date:** 2026-07-03
**Verdict:** **Instrument conditionally validated — by the Phase 0b signed controls, NOT by the gate battery.** The pre-registered gates (G1–G5) all pass on the retuned run, but the gate battery itself was shown insufficient (run 1 passed G1–G4 while demonstrably geometry-blind). The evidential weight rests on Phase 0b: degree-matched controls do not collapse (15–30 pooled sd), a signed amplitude-monotonicity violation (~9σ) falsifies the scalar-confound null in the geometry-predicted direction, and destroy-controls land on the noise ceiling. The instrument is **not** a dimension reader; it is a benchmark-relative discriminator of geometry-shaped correlation structure, usable for later phases only under fixed dynamics with benchmark anchors.

## What ran

1. **Run 1 (PREREG dynamics: plain walk `P = D⁻¹A`, λ=0.9):** G1–G4 passed, **G5 (positive control) FAILED** — lattice3d d1/d6 = 0.006/0.007 (flat, at the sampling floor √(2/πT) ≈ 0.0056); lattice2d = 0.008/0.015 (**inverted**). `PHASE0_PASS = False`. Console: `results_phase0_console.txt`.
2. **Retune (the single G5-permitted deviation — see Deviations):** root cause traced before patching: (a) correlations below the sampling floor at λ=0.9; (b) all lattice/tree fixtures are bipartite and AR(1) amplifies the checkerboard mode (μ≈−1) as much as the smooth mode (mode variance ∝ 1/(1−λ²μ²), sign-symmetric), so opposite-parity (odd-distance) pairs partially cancel while same-parity (even-distance) pairs add — hence d6 > d1. Fix: lazy walk `(I+P)/2` (spectrum → [0,1]) + λ=0.99, selected via `diagnostic_dynamics.py` scan, then frozen.
3. **Run 2 (retuned):** all gates pass. Console: `results_phase0_console_retuned.txt`; data: `results/phase0_calibration.json`.
4. **Phase 0b (skeptic-mandated deconfounding, T1/T2/T4 + continuous observable):** `phase0b_deconfound.py`; data: `results/phase0b_deconfound.json`.

## Run 2 results (mean ± sd, 10 seeds)

| fixture | dpr_raw | dpr_sub | mds_dim90 | corr d1/d6 |
|---|---|---|---|---|
| lattice3d (deg 6) | 57.47±0.45 | 59.13±0.27 | 55.00±0.00 | 0.213/0.021 |
| lattice2d (deg 4) | 27.74±1.89 | 38.18±1.06 | 51.70±0.46 | 0.402/0.073 |
| expander (3-reg) | 53.16±1.37 | 54.16±0.96 | 52.00±0.00 | 0.387/0.020 |
| tree (bin, d10) | 23.94±3.71 | 27.54±3.07 | 38.90±1.76 | 0.651/0.086 |
| null_indep | 63.80±0.01 | 62.81±0.01 | 57.00±0.00 | — |
| null_corr | 1.02±0.00 | 62.80±0.01 | 57.00±0.00 | — |

Gates: G1 ✓ (all 6 pairs; NB all pairs separate on `dpr_sub` alone — nothing rests on the degenerate zero-sd branch, see Skeptic §c), G2 ✓ (55.0 > 51.7), G3 ✓ (no observable near [2.5, 3.5]), G4 ✓, G5 ✓ (0.213 ≥ 2×0.021; 0.402 ≥ 2×0.073). `PHASE0_PASS = True` — **with the evidential caveat above.**

## Phase 0b — deconfounding results (mean ± sd, 10 seeds)

| fixture | dpr_sub | mds_dim90c | corr d1/d6 |
|---|---|---|---|
| lattice3d (3D, deg 6) | 59.13±0.27 | 54.41±0.08 | 0.213/0.021 |
| **expander6** (deg 6, matched) | 62.24±0.10 | 55.41±0.10 | 0.154/0.015 |
| lattice2d (2D, deg 4) | 38.18±1.06 | 51.08±0.15 | 0.402/0.073 |
| **expander4** (deg 4, matched) | 61.60±0.28 | 54.85±0.25 | 0.254/0.015 |
| **moore2d** (2D, deg 8) | 46.43±0.63 | 53.08±0.05 | 0.309/0.044 |
| lattice3d_uniformtaps (T4i) | 61.03±0.24 | 54.84±0.11 | — |
| lattice3d_shuffled (T4ii) | 62.81±0.00 | 56.10±0.01 | — |

**T1 (degree-matched adversarial):** no collapse — expander6 vs lattice3d separate by **15.2 pooled sd**; expander4 vs lattice2d by **30.3**. The "degree meter" null is dead.

**Signed amplitude-monotonicity violation (the decisive datum):** expander4 has *higher* d1 amplitude than lattice3d (0.254 vs 0.213); a scalar amplitude meter must therefore read it *lower*. It reads **higher** (61.60 vs 59.13, ≈9σ) — the direction geometry predicts (expander above 3D lattice). The scalar-confound null is falsified by sign, not by margin.

**T2 (dimension–degree decoupling, opposite-sign predictions):** moore2d (2D, deg 8) reads **below** lattice3d on both observables (dpr_sub −12.7; mds_dim90c −1.33) — the geometry-predicted sign. (Caveat: measured amplitudes came out 0.309 vs 0.213 rather than the naive 1/deg ordering — in diffusion the amplitude/decay profile is itself dimension-shaped, so T2's sign is consistent with geometry but was not the clean opposite-sign test as designed. The expander4 violation above is the clean signed result.)

**T4 (destroy-controls):** per-channel time shuffle lands exactly on the null_indep reading (62.81 = 62.81); uniform taps move toward the ceiling (61.03 vs ball 59.13). Structure destroyed → null, as required of a real instrument.

**A3 resolution (continuous observable):** mds_dim90c has normal seed variance (lattice3d 54.41±0.08) — the zero-sd integer readings were quantization, not insensitivity.

## What the instrument IS and IS NOT (frozen calibration findings)

- It is a **benchmark-relative discriminator**: under fixed dynamics (lazy walk, λ=0.99), the four geometry classes and the degree-matched adversarial fixtures are robustly separated, with signed orderings matching geometry (tree < 2D < 2D-Moore < 3D < expanders < noise ceiling on dpr_sub).
- It is **NOT a dimension reader**: absolute readings sit near the N_tap-dependent noise ceiling (55 vs intrinsic 3) and are modulated by correlation amplitude — lattice2d and moore2d share dimension 2 but read 38.2 vs 46.4. Any later-phase use must compare against benchmark fixtures run under identical dynamics, never read absolute values as dimension.
- **Scope by construction:** D_PR is close to a mean-square-correlation functional; "it reads correlation statistics" is unfalsifiable because the correlation matrix is *all an embedded bundle has* (the inside-out constraint). The validated claim is exactly: geometry shapes the bundle's correlation structure in ways these observables detect, benchmark-relative. Nothing stronger.

## Deviations (per PREREG §Deviations)

1. **λ: 0.9 → 0.99.** Covered by the pre-registered G5 retune clause ("parameters (λ, R)").
2. **Walk operator: `P = D⁻¹A` → lazy `(I+P)/2`.** EXCEEDS the letter of the retune clause (which covers parameters, not the propagator). Flagged by the skeptic review; accepted as honest-in-substance (root cause — bipartite checkerboard mode — traced before the patch, mechanism verifiable, tuning scan preserved), unregistered-in-form. Recorded here as its own deviation.

## Skeptic review

Fresh-context skeptic subagent dispatched on the raw bundle before this doc was written. Objections and resolutions:

- **(b) Walk-operator swap exceeds the retune authorization.** ACCEPTED — recorded as deviation #2 above; PREREG untouched.
- **(c) G1 zero-variance branch is degenerate (0-sd integer separations).** FIXED — continuous observable `mds_dim90c` added (Phase 0b) shows normal variance; verified that all six G1 pairs separate on continuous `dpr_sub` alone, so no gate outcome rests on the degenerate branch.
- **(d) Unit tests not updated after retune (hybrid config).** FIXED — test now exercises the frozen defaults; 8/8 pass.
- **A2: amplitude/degree confound is a complete rival theory.** FIXED by T1 + the signed violation — degree-matched fixtures do not collapse (15–30 sd) and expander4 > lattice3d violates amplitude-monotonicity at ~9σ in the geometry-predicted direction. The residual truth in A2 is kept as a frozen finding: amplitude modulates readings (lattice2d ≠ moore2d), hence benchmark-relative use only.
- **A3: zero seed-variance (quantization vs insensitivity).** FIXED — quantization confirmed (54.41±0.08 continuous under 55.00±0.00 integer).
- **Unlisted anomaly: expander < lattice3d inversion in run 2 (3-regular).** RESOLVED by T1: with degree matched, the expander reads *above* the lattice as geometry predicts; the run-2 inversion was the amplitude modulation acting across unmatched degrees — consistent with the frozen finding, no longer evidence against geometry-reading.
- **G1–G4 satisfiable by a geometry-blind instrument (run 1).** ACCEPTED — the single most important process finding: the gate battery alone is insufficient; signed deconfounding controls are now a standing requirement for any future instrument claim in this experiment line. This is why the verdict credits Phase 0b, not the gates.
- **G3 unfailable as instantiated (readings never near 3).** ACCEPTED — the [2.5, 3.5] tripwire is kept but acknowledged as weak here; the honesty burden is carried by T1/T2/T4-style signed controls instead.
- **T3 (amplitude-equalized comparison) not run.** ACCEPTED with commitment — required protocol for any future *quantitative* cross-fixture comparison; not needed for this phase's sign-based verdict.
- **T5 (100-seed / R / N_tap sweep) not run.** ACCEPTED with commitment — mandatory before any later-phase claim that rests on margins smaller than ~3 pooled sd (Exp 135 lesson: 100-seed sweeps changed verdicts).
- **T6 (applicability to Exp 134 survivors — constant fixed-point series ⇒ NaN correlations).** ACCEPTED as the **first gate of Phase 1**: the Phase 1 pre-registration must define the dynamic readout regime (sub-K-cycle hold-and-fire dynamics, or perturbation response) and verify non-degenerate tap series before any survivor measurement. "Usable for later phases" in this doc's verdict explicitly excludes this unresolved applicability question.

## Phase 1 prerequisites (carried forward)

1. T6 applicability gate (above) — first gate of Phase 1 PREREG.
2. Identical-dynamics benchmark anchors run alongside any new substrate.
3. T3 amplitude-equalization for quantitative comparisons; T5 sweep for narrow margins.
