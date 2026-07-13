# RAW 401 — Settled Results, the Earned Set, and the Program Falsifier

### *Closing the gravity-from-local-conservation line*

**Author:** Claude (diagnosis at Tom's request, ultracode pass)
**Date:** 2026-06-05
**Status:** Closing / status document — companion to RAW 400 (Open Questions and Experimental Status)
**Method:** Primary-source read of RAW 118/122/130/132/133/400 + a 24-agent code-verified review of experiments 118, 128, 131_a, 131_b, 132, 133, 134, 135, grounded against the physics/CS/neuroscience literature, with an adversarial skeptic pass that re-checked every code claim.
**Closes (provisionally):** the open question "can a local + conservative + isotropic graph rule produce a sustained 1/r² force at a distance?" — as SETTLED NO, on theorem grounds. This is the doc RAW 400 asked for ("close the gap with experiments, not with more theory documents"); it is a *closing* doc, not another *opening* one.

---

## Why this document exists

RAW 400 (2026-03-25) stated the project's own discipline and crux:

> *"Q1. Formal definition of the Same comparison operator … Different definitions produce different force laws. This is the single most important open question. What would answer this: a formal definition that, when simulated on a random geometric graph, produces 1/r² attraction **without tuning**."*
>
> *"The gap between theoretical claims and experimental demonstration remains large. **Close it with experiments, not with more theory documents.**"*

Between March and May 2026 the project ran the experiments (good) but also wrote RAW 130, 131, 132, 133 — four theory documents, each reframing an experimental negative as motivation for an untested successor substrate. This document does the opposite: it converts the recurring "open gap" into a closed result, names what is genuinely earned, and states the one commitment that — if not made — leaves the whole program unfalsifiable.

---

## 1. What is SETTLED (theorems, not open questions)

The literature is unanimous and the project's own experiments independently confirm three textbook facts. These are **not** bugs, substrate limits, or open frontiers. No parameter sweep escapes them.

| # | Settled fact | What it is in the literature | In-corpus confirmation |
|---|---|---|---|
| S1 | A strictly local, exactly-conservative, **source-free** rule relaxes to a **flat** field. | Discrete maximum principle; source-free harmonic function is constant on a closed domain (Doyle–Snell electric networks; number-conserving CA). | Exp 133: slope −0.012 at every α; the rule is exactly conservative (verified). Exp 132 Phase 2A.2: 1000× variation in load_coefficient changes nothing. |
| S2 | A **source+sink** (open system, broken local conservation) yields ρ ∝ 1/r in 3D — and the **1/r² force then follows automatically by differentiation.** | 3D Laplacian Green's function. ∇(1/r) = −1/r². There is no separate "force ingredient" to discover. | Exp 128 v11 Phase 1: `rho_new[nbr]+=rho[node]/degree[node]` with held source + absorbing boundary → slope −1.968 (verified). Exp 133 Phase 2d: ρ ∝ r^−0.99 once a sink was hand-imposed (verified). |
| S3 | An **isotropically generated** graph/lattice has **no preferred local radial direction**; ⟨cos²θ⟩ = 1/3 is the isotropic value, not a measurement to be fixed by adding deposits. | Bombelli–Henson–Sorkin: discreteness without symmetry breaking. Connectivity order is conformally blind (Malament). The metric d.o.f. is **edge length** (Regge calculus), not node value. | Exp 128 v11 Phase 6: ⟨cos²θ⟩ = 0.32–0.34 in every shell; radial GR error grows 0.4% → 50.5% as the field strengthens (verified). |

**Consequence for framing.** Because S2 makes the 1/r² force automatic from a correct 1/r potential, the project's "we got the potential but the force law is wrong (−0.65)" framing **dissolves**: the −0.65 force slope in Exp 133 was an analyst-side smoothing artifact (a `SMOOTHING_LEVELS=[0,1,3,5,10]` sweep applied to a noisy integer gradient, raw cos 0.087, r²=0.013 — verified), not a property the substrate presents to any local probe. The right observable was always the **potential** slope, which Exp 133 Phase 2d already earned. **Ratified 2026-06-05** (`133/r6_potential_refit.py`, 20 seeds, no smoothing): the converged potential slope is −1.14 (IQR 0.068, r²≈0.99), so the analytic force slope is −2.14 — the inverse-square force is present; −0.65 was the artifact. (The original −0.99 was also a pre-convergence transient; it converges by ~tick 3000 to ~−1.19.)

**Honest caveat (do not over-import).** A fourth result — Marolf 2014, "force-at-a-distance is unreachable from local-kinematics dynamics" — is a *real* theorem but was **imported by this analysis, not actually hit by the corpus**. Exp 128 Phase 1 *did* get 1/r² from a local rule (with source+sink), which is not what Marolf forbids. The operative obstruction the corpus actually demonstrates is the elementary, already-conceded **source/sink requirement** (S1↔S2), not Marolf. Treat Marolf as a flag for a future field-theoretic version, not as a wall already proven here.

**Honest caveat (theorem-counting).** S1, S2, S3 are three *distinct* theorems with three *distinct* remedies. Earlier internal framing ("the same wall hit five times") over-unified them. They are related (all flow from the local+conservative+isotropic commitment) but should not be collapsed into one.

---

## 2. What is genuinely EARNED (the honest set, 118–135)

Across 18 experiment-versions the substrate-earned, defensible results reduce to roughly five items. Each was independently re-checked.

1. **Exp 118 v9's self-falsifying random-walk diagnostic**, plus the structural facts: deposits saturate any finite graph; a star diffuses to ~73% of any graph's volume scale-invariantly; velocity is distance-independent on the hopping model. *This is the project at its methodological best.*
2. **Exp 128 v11 Phase 1: 1/r² from source+sink graph diffusion** (slope −1.968). Genuine — but it is the textbook 3D Green's function (see S2), and single-seed (SEED=42).
3. **Exp 128 v6: radial equilibrium** at dist ≈ 12.2.
4. **Exp 133: exact integer conservation**, and — ratified 2026-06-05 across 20 seeds — the **converged 3D Green-function potential** ρ∝r^−1.14 (IQR 0.068, r²≈0.99) once a source+sink was added, whose analytic derivative is a ∝r^−2.14 force. Textbook (it requires breaking conservation with a source+sink), NOT novel gravity, but a genuinely robust earned result — stronger than the original 133 docs claimed, which buried it chasing a smoothed force exponent.
5. **Exp 134: strict-locality bit-identity** (S2/S3 fixtures identical over 1000 cycles) — a clean demonstration that nothing couples across one empty cell, by construction.

**Zero** earned results mentioning Kepler, orbit, or Schwarzschild were *not* either hand-coded or definitional. See RAW 402 for the itemized demotions.

Credit where due: **Exp 133's CLOSURE is honest on the page** — it states −0.65 ≠ Newton's −2 and labels the raw gradient as noise. The fault there was the framing/headline, not concealment.

---

## 3. What is NOT earned

Demoted from EARNED to {Newton-renamed | algebraic-identity | single-seed-noise | mechanism-not-engaged | textbook-theorem} in **RAW 402 (Retractions Ledger)**. The short version: every "exact Schwarzschild," "Keplerian orbit," and "per-edge radial GR" headline is either a textbook central-force solution with GM→P substituted, an algebraic identity the operator wrote and measured back, or a single-seed positive that did not survive a multi-seed sweep.

---

## 4. Why this kept happening: the recursive "half the mechanism" reframe

The same move recurs at the theory layer, and it predates Exp 118:

- **RAW 118 §1.1–1.3:** the Exp 64_109 v1–v24 failure was reframed as *"the simulation implements half of the single mechanism (reading) and omits the other half (writing)."*
- **RAW 132 §1:** the 131–134 failures were reframed as *"each experiment dropped half of the capacitor model."*
- **RAW 133 §12.1:** the Exp 132 failure was reframed as *"RAW 132 missed the spectra"* — and, by logical inversion, *"non-semantic substrates can't produce gravity = strongest possible support for the spectrum primitive."* A negative on substrate A is **not** evidence for untested substrate B.

(RAW 133 also cites Exp 134 as supporting "same-sign attracts / opposite-sign annihilates," but Exp 134's own results record that the rule **did not distinguish** the two — both decohered by the same starvation path. The RAW contradicts the experiment it cites.)

This reframe is what makes the program unfalsifiable: any result can be absorbed because the ontology can always posit one more un-built component.

---

## 5. The Program Falsifier (the load-bearing commitment)

Pre-registration and multi-seed gates discipline individual *runs*. They do **not** stop the RAW-doc layer from reframing a pre-registered negative as "only this instantiation failed." The unfalsifiability lives one layer up. Therefore the project must commit, in advance and in writing, to **what observation would retire the PROGRAM — not merely one instantiation.**

**Commitment (proposed, for ratification):**

> If a substrate that is **local + conservative + isotropic** fails to produce a sustained, gradient-following coupling between two patterns across empty space at **three further distinct instantiations**, the project accepts that *gravity-at-a-distance is unearnable from those three axioms together*, and **stops building local conservative isotropic rules**. It does not write a RAW reframing the failure as a special case of an untested successor. To continue the gravity line after that point, exactly one axiom must be explicitly surrendered (and named in the experiment spec):
> - surrender **strict conservation** → an explicit source+sink / open system (already shown to give 1/r);
> - surrender **isotropy-as-emergent** → anisotropy in **edge lengths** (Regge metric), legitimate only if a *local rule generates it in response to mass* rather than reverse-engineering 1/√(1−L_grav);
> - surrender **strict locality** → an explicit non-local coupling kernel (e.g. r^−3) or the thermodynamic-horizon route (Jacobson/Verlinde, no propagated field).

This is the single most important fix. Without it, every other improvement just produces better-documented negatives that still get absorbed.

---

## 6. The two things that are NOT settled

### 6.1 The open frontier (a real non-theorem): self-coherent drift

In 18 experiment-versions, **no pattern was ever shown to both persist and have its centroid translate.** Generic blobs dissipate (Exp 133: 605→20 quanta in 400 ticks) or the rule is undefined on them (Exp 134 S1 starvation); the only "orbit" was a bound random walk (Exp 118 v9). Self-coherent drift is the prerequisite for any real orbit. The CA literature has translating coherent structures (gliders, solitons, cyclic CA, Greenberg–Hastings excitable media) the project has never cited or borrowed. **But** RAW 132 argues drift is *observer-side* ("cells never move; drift is the reading function") — so step zero is deciding whether the gate is even well-posed at the substrate level. A minimal "fixed-point-that-drifts" search would resolve it either way (it exists → orbit work resumes on a real moving pattern; it provably cannot for this rule class → "movement = statistical shift" is falsified and the ontology must add a momentum/wake d.o.f.).

### 6.2 The one novelty seam — with its trap

The only starting commitment no cited program shares (Wolfram, causal sets, Verlinde, tensor networks all treat time as emergent or work in the continuum) is **Doc 50's tick-primary, time-as-special-amplifying-generator ontology (ρ=2.0).** The honest test: does making *time* an extra propagation generator supply the effective d=4 that yields a 1/r² force **without typing `4πr²` anywhere** (no Gauss-law smuggle)? Two warnings: (a) a d=4 harmonic field *is* Gauss's law in 4D, so "it works" may just be Gauss renamed via the time axis; (b) the ρ=2.0 result itself is flagged in the corpus as a possible PDE-solver artifact — **validate ρ=2.0 is not a solver artifact before staking anything on it.**

---

## 7. Process commitments going forward (so the loop does not recur)

1. **Pre-register** the observable, slope/radius window, numeric threshold, seed list (≥20; ≥100 for cheap substrates), and required controls — in the same commit as the driver, before the run.
2. **Multi-seed by default**, common random numbers; the distribution (median + IQR) is the unit of evidence. `seed=42` alone is banned as evidence.
3. **Mandatory null-mechanism control**: disable the named mechanism and re-run; if the headline survives, attribute it to topology and rename the version.
4. **Scientist-before-design, skeptic-before-RESULTS** as hard gates (the skeptic skill already works; on Exp 135 it caught all 5 goal-post moves — the only failure was timing).

---

## 8. Relationship to RAW 400

RAW 400 said "close the gap with experiments, not more theory documents." The irony of answering with two more documents (RAW 401/402) is acknowledged: these are **closing** documents — they *remove* open questions and *retract* unearned claims rather than adding a new mechanism. RAW 400's Q1 ("a Same operator that gives 1/r² without tuning") is now answered in the negative for the local+conservative+isotropic class: by S2, the only way that class produces 1/r is to break conservation with a source+sink — which is no longer tuning, it is changing the boundary condition, and it gives the textbook Green's function, not novel gravity.

---

## References

- RAW 118 — Gravity as Consumption and Transformation
- RAW 122 — The Derivation Chain
- RAW 130 — It Rotates Because It Consumes
- RAW 132 — The Untested Capacitor
- RAW 133 — The Semantic Substrate
- RAW 400 — Open Questions and Experimental Status
- RAW 402 — Retractions Ledger (companion to this document)
- Doyle & Snell, *Random Walks and Electric Networks* (discrete maximum principle / harmonic functions)
- Bombelli, Henson & Sorkin (2009), "Discreteness without symmetry breaking"
- Regge (1961), "General relativity without coordinates" (edge lengths as the discrete metric)
- Gelman & Loken (2013), "The garden of forking paths" (analysis-contingent-on-data inflates false positives)

---

*Status: closing/status document. Settled facts S1–S3 are theorem-grounded; the earned set and retractions are code-verified (2026-06-05); the Program Falsifier (§5) and process commitments (§7) await ratification.*
