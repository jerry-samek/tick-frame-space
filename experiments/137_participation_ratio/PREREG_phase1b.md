# Exp 137 Phase 1b — REDESIGNED applicability gate (inside-consistent) — PRE-REGISTRATION

**Date registered:** 2026-07-03 (design pass; redesign of the Phase-1 T6 gate after its INCONCLUSIVE verdict).
**Supersedes:** `PREREG_phase1.md` (T6). The T6 gate was mis-designed (hollow pass condition; period≡embedding confound on coplanar fixtures; god-view regime). See `RESULTS_phase1.md`.
**Anti-rescue compliance:** this is a *fresh* pre-registration with its own gates and its own required skeptic pass, per the T6 anti-rescue clause. Nothing here is a post-hoc rescue of T6; the readout and fixtures are redesigned from the recon findings below.
**Recon that shaped this design:** `phase1b_recon.py` (`results_phase1b_recon_console.txt`), `phase1_t6_embed.py`.

---

## 0. Two recon findings that force the redesign

**F1 — R1 (continuous ambient stochastic driving) is INFEASIBLE on Exp 134.** Exp 134 survivors are *fragile exact fixed points with no noise-stable basin*, not robust attractors. Under magnitude jitter at every tick, the reentrant sync (which cell is c_max determines where renewal paints) desyncs and the ring loses a cell within ~6–38 ticks even at the gentlest p=0.005, and even with hole-deletion suppressed (`phase1b_recon.py`, both fixtures, 12 seeds). So there is **no steady-state fluctuation to read**, and the fluctuation–dissipation bridge has nothing to stand on. The literal "R1 = drive with noise, read own-channel covariance" plan dies here. This is itself a substrate finding (consistent with `project_134_phase2`: same-sign contact = mutual decoherence; these patterns are delicate).

**F2 — the inside-consistency R1 was meant to deliver is achievable via memory-subtraction (readout M).** For a **periodic** survivor, R2's "reference universe" is NOT a god-view counterfactual: the pattern is period-K, so its unperturbed continuation equals the observer's **own memorized past** K ticks. The divergence `d(t) = γ_actual(t) − γ_template((φ₀+t) mod K)` is therefore inside-computable from the observer's memory of its periodic orbit — no second universe. Numerically M ≡ R2 (the template equals the reference orbit), so T6's R2 numbers stand as **inside-valid for periodic patterns**.

**Scope correction to the god-view concession (RAW 134 §12.5 / Addendum A §13.2c) — flagged for the user, not silently edited.** The readout is god-view *iff the reference is a counterfactual unknowable from inside* — which holds for **aperiodic** patterns but NOT for periodic survivors (reference = memory). The precise statement: **the instrument's inside-validity is co-extensive with the pattern's predictability-from-memory.** This scopes, and partially walks back, the blanket "R2 is god-view" of the last session. Proposed as a RAW 134 refinement pending user approval.

## 1. What the redesigned gate certifies

The T6 gate asked the wrong (unidentifiable) question. The property Test 3 actually needs is: **does the inside-consistent readout M distinguish survivors by their 3D embedding at FIXED period K** — i.e., read geometry, not just period/size? The recon says yes, decisively: at K=8, M separates the cube embedding from the planar one at **21 pooled-sd** (CUBE 4.84±0.02 vs FLAT 4.36±0.03, bootstrap over the perturbation ensemble). Phase 1b makes that the gate.

## 2. Readout M (frozen)

- **Perturbation ensemble:** exhaustive over (phase φ ∈ 0..K−1, ring-site s, sign ±1), single ±1 kick (survivable — the ring absorbs single kicks as a persistent phase-shift, T6 §C).
- **Reference = memorized period:** `d(t) = γ_pert(t) − γ_ref(t)` where γ_ref is the unperturbed period-K continuation from phase φ (== the observer's memory). Horizon W = 6K.
- **Channels = tap cells** (ring cells + face-neighbor collar); drop zero-variance channels; observables `dpr_sub`, `mds_dim90c` on the active-channel correlation matrix. (Position-free observables — inside-computable, as in Phase 0.)
- **Statistics:** bootstrap B=200 resamples over the perturbation ensemble → mean ± sd per fixture. (Deterministic readout; bootstrap gives honest error bars.)

## 3. Fixture family (frozen) — the non-K axis T6 lacked

| fixture | K | embedding | role |
|---|---|---|---|
| `FLAT_K8` (F3_K8_RING) | 8 | planar 4×2 | embedding-discrimination pair |
| `CUBE_K8` | 8 | unit-cube Hamiltonian cycle (genuinely 3D) | embedding-discrimination pair |
| `FLAT_K8` seeds A vs B | 8 | planar | **same-embedding negative control** |
| K4 / K6 / K8 planar | 4/6/8 | planar | period-axis (reported, for context) |

A **second same-K pair** should be added if constructible (e.g., an L-shaped planar K8 vs FLAT_K8) to test embedding-discrimination beyond the single cube/plane contrast; if no third K=8 survivor exists under the rule, that is logged as a substrate limit. **Open substrate question (resolve first):** does the rule sustain 3D cycles at K≠8, and non-cycle survivors? Needed to widen the family.

## 4. Gates (pre-registered)

- **G-M1 (embedding discrimination — decisive):** M separates `CUBE_K8` from `FLAT_K8` by ≥ 2 pooled sd. (Recon: 21 sd — expected strong pass; the criterion is the honest bar, not the observed value.)
- **G-M2 (same-embedding negative control — the anti-artifact):** M does **NOT** separate `FLAT_K8` (bootstrap set A) from `FLAT_K8` (bootstrap set B) beyond 2 sd. If a fixture separates from *itself*, the "discrimination" is bootstrap noise, not geometry → gate FAILS. This is the control T6 never had.
- **G-M3 (calibration transfer):** the M/impulse readout on the Phase-0 graph fixtures reproduces Phase 0's signed separation (expander6 > lattice3d). (T6.3 already passed at sign level; re-verified here under M.)
- **G-M4 (inside-consistency audit):** the observable uses only channel time-series (correlation matrix), no global coordinates, and the reference is the memorized period (not a counterfactual). Confirmed by construction; stated so the god-view scope is explicit.

**PASS** = G-M1 ∧ G-M2 ∧ G-M3 (∧ G-M4 by construction). Note the pass condition now contains the DECISIVE test (G-M1) and its NEGATIVE CONTROL (G-M2) — fixing T6's hollowness (T6 gated on a trivially-passable coupling test).

**FAIL / anti-rescue:** if G-M1 fails (embedding not read) or G-M2 fails (self-separation), the instrument does not read embedding on Exp 134 survivors and Test 3 is not runnable; report it. No post-hoc regime without a further pre-registration.

## 5. If Phase 1b passes → Test 3 (frozen only after the gate)

With M validated as embedding-reading, Test 3 (RAW 134 §8.1/§12.3) becomes runnable in the **embedding-vs-intrinsic** framing (PREREG_phase1 §4 option A, now the natural fit): does a survivor's M-rank track its **intrinsic** 1-cycle extent or the **3D embedding** it occupies, and — the claim-5 falsifier — do more-self-maintaining patterns read **lower** rank, or expand toward the ambient-lattice benchmark? Benchmark anchors (1-cycle; lattice3d) under identical M; never absolute readings.

## 6. Deviations & scope

- The god-view scope correction (§0) is proposed for RAW 134, pending user approval — not applied here.
- Readout M is R2 reframed (reference = memory), not a new regime — so this is *not* a T6 anti-rescue violation: it does not re-run T6's failed criterion, it replaces the unidentifiable fixture axis and the hollow gate with an identifiable one (embedding discrimination) plus a negative control.
- **This design has NOT been run as a gate.** Building + running G-M1..G-M3 with the full fixture family and the same-embedding control, then a skeptic pass, is the next step.
