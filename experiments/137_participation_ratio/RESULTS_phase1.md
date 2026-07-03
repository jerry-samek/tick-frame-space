# Exp 137 Phase 1 — T6 applicability gate — RESULTS

**Date:** 2026-07-03
**Verdict:** **INCONCLUSIVE — the gate as pre-registered is mis-designed, and the primary regime is a god-view probe.** The registered pass condition (T6.1 ∧ T6.2a ∧ T6.3) evaluates **True**, but that pass is **hollow**: T6.2a is trivially passable, and the substantive period-escape test (T6.2b) was mis-filed as "evidence," fails, and is anyway **unidentifiable** on the coplanar fixture set. The instrument is **neither validated nor cleanly refuted** for Exp 134 survivors. Two independent critiques (skeptic subagent; operator's own "do you observe it from inside?" — RAW 134 §12.5) converge on this. The constructive yield is real: a genuinely 3D survivor now exists to break the confound, and the ontologically honest regime (R1/FDT) is identified.

## What ran

- **`phase1_t6.py`** — R0 (raw limit cycle) and R2 (perturbation-response / damage field) on K4/K6/K8; T6.3 fluctuation–dissipation transfer on Phase-0 graphs. `results/phase1_t6.json`, `results_phase1_console.txt`.
- **`phase1_t6_sweep.py`** — magnitude {1,2,3,5} × horizon {6,20} robustness. `results_phase1_sweep_console.txt`.
- **`phase1_t6_embed.py`** — the three skeptic-mandated decisive tests (E/C/S). `results_phase1_embed_console.txt`.

## Core data

**R0 vs R2 ladders (dpr_sub, K4/K6/K8):** R0 = 1.80 / 2.86 / 3.44; R2 = 2.86 / 3.78 / 4.36. Both **strictly K-monotone**. R2 `n_active` = 4/6/8 (exactly K). `frac_nonzero` ≈ 0.88–0.94 (damage persists as a bounded on-ring phase-shift; it does **not** collapse — contra the naive "periodic attractor kills perturbations").

**T6.3 transfer (fluctuation–dissipation):** R2 impulse-response reproduces Phase-0's *sign*: expander6 59.94 > lattice3d 45.58 (Phase-0 noise-driven ref: 62.24 > 59.13). Only qualitative — lattice3d fell −23%, gap widened 3.1→14.4 (the deterministic Green's function is more concentrated than the steady-state covariance).

**(E) Fixed-K, different embedding — the decisive test the original gate omitted.** A Hamiltonian cycle on the unit cube (`CUBE_K8`) **sustains** as a period-8 fixed point (so a genuinely 3D survivor exists). R2 dpr_sub: **CUBE_K8 = 4.83 vs FLAT_K8 = 4.45** — a 0.38 gap, *comparable to a full period-step* in the K-ladder (steps 0.6–0.9). The instrument therefore reads embedding **weakly but non-negligibly** — it is **not** purely period-confounded.

**(C) Confinement is probe-dependent, not structural (skeptic vindicated).** On-ring perturbations stay confined even at magnitude K (off-ring hits 0, `n_active` = 8). But an **off-ring +K deposit floods the 3D collar**: `n_active` 8→36, off-plane hits ≈ 5000, dpr_sub 4.4→27.5. My earlier "damage never leaves the ring, so embedding can't matter by construction" claim was **wrong** — it held only for on-ring kicks.

**(S) Proper T6.2a statistics.** 100 shuffle surrogates, registered 2-pooled-sd test: z = 29 / 411 / 1443 → passes on all K. My earlier `>1.0` constant (which failed K4 at 0.133) was the artifact; the *registered* criterion passes trivially — which is exactly why it is hollow.

## Why the verdict is INCONCLUSIVE, not PASS or FAIL

1. **The registered pass condition is hollow.** PREREG §2 pass = T6.1 ∧ T6.2a ∧ T6.3. All three are True. But **T6.2a cannot fail for any coupled signal**: a full per-channel shuffle destroys *all* cross-channel correlation, so real always differs from surrogate whenever any coupling exists — including a fully period-confounded signal. T6.2a tests coupling-existence, never period-escape. The pass certifies nothing about geometry-reading.
2. **The substantive test was mis-filed and fails.** The period-escape test is T6.2b (break the K-monotone ladder). PREREG filed it as "reported evidence," not a gate; R2's ladder is strictly K-monotone → it does **not** escape. (The earlier code wrongly promoted T6.2b to a hard gate — a skeptic-caught deviation, now corrected.)
3. **T6.2b is unidentifiable on this fixture set anyway.** F1/F2/F3 are all coplanar rings differing *only* in K, so period ≡ size ≡ embedding. Even a perfect geometry-reader returns a monotone ladder here. The K-ladder cannot separate "reads period" from "reads extent."
4. **The primary regime is god-view.** R2 differences two counterfactual universes (γ_pert − γ_ref) and indexes cells by global coordinates — exactly the god-view slip RAW 134 §12.5 names as a recurring wrong turn. No embedded observer can subtract a counterfactual twin. (This *strengthens* any negative — god-view is an upper bound on inside-extractable information — but it means even a pass would have measured the wrong thing ontologically.)

The one point that would have *supported* a clean FAIL — confinement making embedding irrelevant — was **refuted by (C)** (confinement is probe-dependent) and by **(E)** (embedding *is* read, ~0.4 at fixed K). So "instrument inapplicable" is not supported. Nor is "applicable" (the pass is hollow). Hence inconclusive.

## Skeptic review

Fresh-context skeptic dispatched on the raw bundle before this doc.

- **T6.2b promoted evidence→gate (code vs PREREG §2).** FIXED — removed from the pass condition; reported as evidence only, per PREREG.
- **T6.2a's 2-sd test replaced by ad-hoc `>1.0`, no sd computed.** FIXED — 100 surrogates, pooled sd, registered criterion (`phase1_t6.py` T6.2a; z = 29/411/1443). Revealed the test is hollow.
- **`n_active ≡ K` "smoking gun" — confinement may be forced by weak perturbation.** FIXED by (C): confirmed on-ring confinement is real up to magnitude K, but **off-ring perturbation breaks it** (collar floods, rank 27.5). The skeptic's mechanism (reorder c_max/c_min → paint off-ring) is correct for off-ring injection. Confinement is not structural.
- **Fixed-K/different-embedding test absent.** FIXED by (E): built `CUBE_K8`, a sustaining 3D survivor; embedding shifts rank ~0.4 at fixed K.
- **"Instrument inapplicable" overstated.** ACCEPTED and downgraded to INCONCLUSIVE.
- **T6.3 "transfer confirmed" oversells a sign-only, magnitude-divergent match.** ACCEPTED — stated as qualitative/sign-only above.
- **Fixture set confounds period with embedding.** ACCEPTED as the central design flaw; drives the redesign below.

## Operator's own catch (RAW 134 §12.5) — god-view

The perturbation-response readout observes from **outside**: it subtracts two universes and reads coordinate-indexed cells. The inside-consistent regime is **R1 (ambient stochastic driving, read the bundle's own channel fluctuations, one universe, no subtraction)**, bridged to R2 by **fluctuation–dissipation** — which also predicts R1 yields the same correlation structure, so switching regimes makes the instrument honest without changing the physics. R1 was not run (integer transactional rule + injected noise risks dissolving the pattern; needs its own design). Recorded as the ontologically-correct path.

## Constructive outcome and next steps (no build without fresh pre-registration — anti-rescue clause)

The two critiques converted a premature FAIL into a usable diagnosis:

1. **A 3D survivor family exists.** `CUBE_K8` sustains and breaks the period≡embedding confound. A redesigned Phase 1 needs a fixture set with a **non-K axis of variation** (e.g., planar-vs-cube at fixed K, plus larger 3D cycles) so the K-ladder becomes identifiable. First open question: does the rule sustain 3D cycles at K≠8, and non-cycle survivors?
2. **Redesign the gate's substantive test.** Replace the hollow T6.2a with a **fixed-K embedding-discrimination** criterion (does rank separate CUBE_K8 from FLAT_K8 by ≥ some benchmark margin, with multi-seed noise-driven R1 statistics), since that is the property Test 3 actually needs.
3. **Move to the inside-consistent regime R1**, using fluctuation–dissipation to keep Phase-0's calibration valid.

Each requires its own pre-registration and skeptic pass. Test 3 (RAW 134 §8.1/§12.3) remains **not runnable** until a redesigned gate passes; the Test-3 reframe (PREREG_phase1 §4, deferred pending T6) stays deferred — the gate did not cleanly pass, so the reframe question is not yet live, but the embedding-vs-intrinsic option (A) is now the natural fit given (E).

## Deviations

- T6.2b pass-condition promotion (corrected to evidence-only) and T6.2a threshold (corrected to registered 2-sd) — both logged in `phase1_t6.py` comments and the Skeptic review above.
- `CUBE_K8`, off-ring/delete perturbations, wide 3D window, and 100-surrogate statistics are **new instruments added in response to the skeptic**, not changes to a frozen regime; they inform the redesign, they do not rescue the current gate (anti-rescue clause honored — no post-hoc regime was declared a pass).
