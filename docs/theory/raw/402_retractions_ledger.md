# RAW 402 — Retractions Ledger

### *Demoting unearned claims from the canonical record*

**Author:** Claude (diagnosis at Tom's request, ultracode pass)
**Date:** 2026-06-05
**Status:** Ledger / correction document — companion to RAW 401 (Settled Results) and RAW 400 (Open Questions)
**Provenance of evidence:** All code references verified 2026-06-05 by direct file read during the diagnosis pass, and the key items independently re-checked by an adversarial skeptic agent. File:line citations should be re-confirmed against current code before any external (publication) use, as files may move.
**Disposition note:** These are *recommended demotions* enacted at Tom's request. They downgrade claims; they do not delete the experiments, which retain value as honest negatives or as the structural facts in RAW 401 §2.

---

## Why this exists

Several claims recorded as wins (in CLOSURE docs, READMEs, and the memory index) were, on code-level inspection, either Newton/Schwarzschild renamed, algebraic identities the operator wrote and measured back, single-seed positives that did not survive a multi-seed sweep, or mechanisms that never engaged. Left in the EARNED column, they get reused as load-bearing in the next RAW (the cross-RAW re-crediting failure mode). This ledger demotes each with its evidence and a disposition.

**Classification key:**
`NEWTON-RENAMED` · `ALGEBRAIC-IDENTITY` · `SINGLE-SEED-NOISE` · `MECHANISM-NOT-ENGAGED` · `TEXTBOOK-THEOREM` · `TRANSIENT-NOT-CONVERGED` · `ANALYSIS-ARTIFACT`

**Disposition key:**
`SETTLED-NEGATIVE` (close it) · `RE-STATE` (rewrite the claim honestly, no new run) · `NEEDS-RERUN` (a clean re-run could still earn something) · `UNVERIFIED` (a corpus claim I could not confirm; flag, don't assert)

---

## Ledger

### R1 — 128 v9/v10 + RAW 130: "clean Keplerian orbits / Kepler III earned"
- **Classification:** NEWTON-RENAMED
- **Evidence:** `flux = L_STAR / (4*np.pi*r*r)` is literally typed in `128/v9_ode/orbit.py:67`, `128/v9_ode/orbit_v2.py:53`, `128/v10/minimal_orbit.py:74`. This is Newton's inverse-square dilution input by hand. RAW 130's `F=−consumed/r²`, `v=√(P/r)`, `T²=(4π²/P)r³` are the textbook central-force results (GM→P substituted); the ODE integrates a hand-written 1/r² force and recovers conic-section orbits — the 1687 result that *any* central 1/r² force gives Kepler.
- **Disposition:** RE-STATE as "ODE confirms a hand-coded 1/r² force produces Kepler orbits (expected)." Note RAW 130's distinct prediction (T² ∝ r³ with constant ∝ planet capacity P, not star mass M) contradicts observation and was "fixed" only by tuning C_cap ∝ M, which cancels by construction.

### R2 — 128 v11 Phase 5: "EXACT Schwarzschild tangential, machine precision 2.22e-16"
- **Classification:** ALGEBRAIC-IDENTITY
- **Evidence:** the operator wrote `γ = √(1−L_grav−L_vel)` and noted it equals the Schwarzschild tangential formula; `phase5_unified_dilation.py` comments admit *"we do not actually move clocks on the graph … v as an analytical load parameter."* No clock was simulated. The baseline it "beats" is a deliberately-wrong multiplicative weak-field form. Phase 6d "√(1−L_grav) to 2.22e-16" is a definitional identity (machine precision = it's an equality, not a measurement).
- **Disposition:** RE-STATE / SETTLED-NEGATIVE for the GR claim. The only substrate output is the scalar ρ(r) from Phase 1; everything downstream is analytic. Mass-independence (Phase 3.1B) is cancellation by construction (C_cap=1.5M ⇒ a=0.5 const).

### R3 — 131_b: "per-edge Schwarzschild radial earned, ratio 1.01 at r=5"
- **Classification:** ALGEBRAIC-IDENTITY (circular)
- **Evidence:** `phase1_anisotropic_field.py:110–111` writes `stretch = √(cos²θ·inv + (1−cos²θ))` with `inv = 1/(1−L)`; for radial edges (cos²θ→1) this **is** `stretch² = 1/(1−L)` by construction. `phase2b` then "measures" 1/(1−L) back on edges pre-filtered to cos²θ≥0.9 — **n_used = 6 edges at r=5.** The 1/√(1−L_grav) factor was reverse-engineered in 128 v11 Phase 6 and re-injected. CLOSURE itself admits "our rule has reproduced the metric it was engineered to reproduce."
- **Disposition:** RE-STATE as definitional. **Foreground the genuine independent negative instead:** horizon does NOT scale r_s ∝ M (log-slope 0.19–0.58 vs 1.0).

### R4 — 118 v7 "FIRST ORBIT" and v8 "FIRST EMERGENT ORBIT"
- **Classification:** SINGLE-SEED-NOISE + MECHANISM-NOT-ENGAGED (already self-retracted by v9)
- **Evidence:** v7's planet sat inside the star body (dist 2.4–10.7 < star r≈12). v8's store/move mechanism never engaged (store fraction 0.000, absorbed=0). The v9 20-trial random-walk control: pure random walk D3 = 1,770,371 deg vs the "orbit" 2,254 deg; net angular std ~5,530 dwarfs the single-seed means (6202/1869/2254) — the motion is diffusion.
- **Disposition:** SETTLED-NEGATIVE. Codify the v9 retraction in the v7/v8 records and the memory index.

### R5 — 132 Phase 2/2A: "substrate saturation / planet field washes out across the lattice"
- **Classification:** MECHANISM-NOT-ENGAGED — **VERIFIED 2026-06-05**
- **Evidence:** deposit_amount=50 with full face-adjacency means 2 cumulative arrivals fire a cell, charge never decays, and a fire emits to all 6 face-neighbors → an ignition front that fills the lattice.
- **RATIFICATION (2026-06-05, `132/r5_ignition_control.py`, pre-registered, one run per config):** a single K=4 seed — **planet alone OR test alone** — ignites the whole 21×21×3 lattice into a clean **2-tick checkerboard** (662/0/661/0 per tick = every cell fires once per 2-tick period; 19/19 alternation), with threshold(r) around the planet centroid **flat at 100.050 at every radius** (spread 0.02% of baseline). Empty config fires 0 cells (sanity passed). **No localized planet field exists**, so H3.5/H4.1's "falsifications" were vacuous, as claimed. Refinement: the two-seed *full* run runs at 63–66%/tick (not a clean checkerboard) with a *bumpy, non-monotonic* threshold(r) (108–116, spread 8.5%) — still not a planet field, but not the clean blink either.
- **Disposition:** SETTLED-NEGATIVE for the "planet field" framing. (Phase 2A.4 partial-connectivity remains the right *forward* experiment, but is no longer needed to retire the saturation claim.)

### R6 — 133: "source+sink yields ρ ∝ r⁻¹ (−0.99)" as converged, and "−0.65 force law"
- **Classification:** TRANSIENT-NOT-CONVERGED (the −0.99) + ANALYSIS-ARTIFACT (the −0.65) — **RATIFIED 2026-06-05**
- **Evidence:** the −0.99 is a still-draining transient (total_E 683k→207k; slope walking −0.32→−0.99), not a demonstrated steady state. The −0.65 "force slope" only appears after an analyst-side k-hop smoothing sweep (`phase2f.py`, `SMOOTHING_LEVELS=[0,1,3,5,10]`); the raw gradient is noise (cos 0.087, r²=0.013). Per RAW 401 S2, the force is anyway automatic from a correct potential, so the force-exponent metric was the wrong observable.
- **RATIFICATION (2026-06-05, `133/r6_potential_refit.py`, pre-registered, no smoothing):** O1 convergence (seed 42): the far-field potential slope walks −0.65→−0.84→−1.04→−1.17→−1.19 and *converges* by ~tick 3000 (Δslope 0.002 over the last 1000 ticks; interior energy stable ~201k) — **confirming the −0.99 at tick 2000 was a pre-convergence transient.** O2 seed sweep (20 seeds, 5000 ticks): potential slope **median −1.141, IQR 0.068, mean r²=0.989** — a converged, seed-robust **3D Green-function potential** (slightly steeper than the ideal −1.0 from the finite absorbing sink at r=0.45; NOT "exactly −1"). The **analytic** force slope = potential slope − 1 = **−2.14** — the inverse-square force is encoded in the potential. **The −0.65 was a finite-difference+smoothing artifact, decisively (−2.1 vs −0.65).** This also tests and rejects the alternative that "integer quantization changes the universality class" — it does not; the macro potential is the clean Green function. Caveat: the *per-cell* gradient remains noise (phase2e r²=0.013), so the 1/r² force is felt by a multi-cell pattern, not a point probe.
- **Disposition:** DONE. The −0.99 (transient) and −0.65 (artifact) are demoted; the genuinely-earned 133 result is upgraded to "converged, seed-robust 3D Green-function potential ρ∝r^−1.14 → analytic force ∝r^−2.14" (textbook, requires the source+sink, NOT novel gravity) — folded into RAW 401 §2.

### R7 — 135 Phases 1–4: all "PASSED"
- **Classification:** SINGLE-SEED-NOISE
- **Evidence:** all four phases passed on seed=42; the 100-seed skeptic sweep overturned every quantitative criterion (Phase 2 ORIGINAL params 19/100; Phase 4 "all 6 crystallize" 0/100; max_age median 526 not 339). The two "emergent findings" ({4} known-token spawn, duplicate-spawn) are reproducible **bugs** (59/100, 29/100), since patched to 0/100.
- **Disposition:** RE-STATE all four as cross-seed distributions. Already substantially captured in `RESULTS_skeptic_pass.md`; ensure the README headline matches the sweep, not seed=42.

### R8 — RAW 133's inferential claims
- **R8a:** *"non-semantic substrates can't produce gravity = strongest possible support for the spectrum primitive."*
  - **Classification:** logical inversion. A negative on substrate A is not evidence for untested substrate B.
  - **Disposition:** RETRACT the inference. The spectrum substrate remains entirely untested.
- **R8b:** *"134 supports same-sign attracts / opposite-sign annihilates."*
  - **Classification:** contradicted by the cited experiment. Exp 134's rule did **not** distinguish same-sign from opposite-sign contact (both decohered via the same ValueError-starvation path); same-sign attraction was never demonstrated.
  - **Disposition:** RETRACT. RAW 133's matter/antimatter section is unsupported by 134.

### R9 — Triumphalist status in 000/997/999 + any "GR/Einstein recovered" language
- **Classification:** mixed (NEWTON-RENAMED / ALGEBRAIC-IDENTITY)
- **Evidence:** the project's own RAW 200/400 already say "coherence is not validation; the gap remains large." The "experimentally validated ToE" tone in the meta docs was never reconciled with that self-assessment.
- **Disposition:** RE-STATE meta-doc status to match the project's own later honesty and the earned set in RAW 401 §2.

---

## Affected memory files (flag, do not silently overwrite)

These memory-index entries currently record retraction candidates as wins; update their framing to point at this ledger:

- `project_128_v11_phase4_5_einstein.md` — records "EXACT Schwarzschild tangential / unified SR+GR" (R2). Should note: algebraic identity, no clock simulated.
- `project_132_closure.md` — foregrounds "per-edge Schwarzschild radial earned (ratio 1.01)" (R3). Should foreground the independent negative (horizon does not scale r_s ∝ M) instead.
- `project_118_v7_first_orbit.md` — records "first orbital motion" (R4). Already retracted by v9; note it.

(Left for Tom's ratification; not auto-edited, since they record his own results.)

---

## Net effect

After this ledger, the substrate-EARNED quantitative set across 118–135 is the ~5 items in RAW 401 §2, and **zero** earned items mention Kepler, orbit, or Schwarzschild that were not either hand-coded or definitional.

---

## References

- RAW 401 — Settled Results, the Earned Set, and the Program Falsifier
- RAW 400 — Open Questions and Experimental Status
- RAW 130, 132, 133 — the documents whose headline claims are demoted here
- `feedback_honest_emergence_claims` (memory) — "flag Newton/Kepler when it's in code; never smuggle it into emergent claims"
