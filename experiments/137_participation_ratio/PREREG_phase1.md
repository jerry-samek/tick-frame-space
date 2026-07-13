# Exp 137 Phase 1 — PRE-REGISTRATION (T6 applicability gate first)

**Date registered:** 2026-07-03 (design pass; no Phase 1 measurement run yet)
**Implements:** RAW 134 §8.1 Test 3 (stability-selection: do self-maintaining Exp 134 patterns read low observer-rank, or expand?) and §12.3 (claim-5 falsifier).
**Depends on:** Exp 137 Phase 0 PASS (`RESULTS_phase0.md`): instrument = benchmark-relative discriminator of geometry-shaped correlation structure under fixed noise-driven dynamics, validated by signed controls, NOT a dimension reader.
**Gate-before-experiment:** T6 (skeptic-mandated in Phase 0 review). Test 3 is BLOCKED until a readout regime passes T6.

---

## 0. Why a gate, not just a run — the confound, measured

Phase 0's instrument was calibrated on **noise-driven diffusion** (each cell gets an i.i.d. innovation every step). Exp 134 survivors are **exact fixed points of a deterministic rule**: a reentrant "head" (max |γ|) circulates one cell per tick around a Hamiltonian ring, so the substrate state is strictly **period-K** (K = ring length). Reconnaissance (`experiments/134_pattern_coherence`, run 2026-07-03):

| fixture | K | period | each cell's trajectory | raw-limit-cycle D_PR |
|---|---|---|---|---|
| F1_K4_SQUARE | 4 | 4 | sawtooth 4,3,2,1,… | **2.78** |
| F2_K6_PERIMETER | 6 | 6 | sawtooth 6,…,1,… | **3.72** |
| F3_K8_RING | 8 | 8 | sawtooth 8,…,1,… | **4.19** |

**The reading is pure period arithmetic.** D_PR is strictly monotone in K because a period-K sawtooth has ≤ K−1 nonzero Fourier components, and the K phase-shifted taps form a circulant correlation matrix whose rank is exactly that Fourier support. **It has nothing to do with the 3D embedding.** A K=4 ring reading "≈3" would be counting the period, not measuring geometry — exactly the trap flagged when Phase 1 was banked. Applying Phase 0's readout to the raw limit cycle is therefore invalid, and "non-NaN" (the crude T6 as first stated) is nowhere near sufficient: the raw cycle is non-NaN and still meaningless.

**Second, deeper finding (surfaced to the user, not silently patched):** *every* Exp 134 survivor is a topological **1-cycle** (a ring, intrinsic dimension 1) regardless of K. So Test 3's original contrast — "survivors cluster at LOW rank vs. the falsifier that they EXPAND" — has **no high-dimensional survivor to expand relative to**. As written, "low" is nearly tautological (rings are low-D) and confounded (rank tracks K). Test 3 needs reframing (§4); that reframing is a decision for the user, flagged here, not made unilaterally.

## 1. What T6 must certify

A candidate **readout regime R** (a way of driving the pattern and extracting channel time-series) is APPLICABLE iff it passes T6.1–T6.3 below. The gate is about the *regime*, not the pattern.

### Literature frame (scientist pass, 2026-07-03)

The Exp 134 pattern is textbook **reentrant excitation on a ring** (cardiac-tissue / excitable-media canon: circulating pulse, refractory tail, excitable gap). The established way to probe such a deterministic reentrant orbit *without* reading its trivial period is the **vulnerable-window / phase-dependent perturbation response**, and its discrete-system formalization is **damage spreading** — the Derrida Boolean-derivative construction and the resulting **CA / Boolean-network maximal Lyapunov exponent** (Bagnoli–Rechtman, *Damage spreading and Lyapunov exponents in cellular automata*, arXiv:cond-mat/9811159). Key inherited fact: *periodic attractor → damage collapses; chaotic → damage spreads.* The bridge back to Phase 0's noise-driven calibration is the **fluctuation–dissipation** relation: the fluctuation correlation structure under weak stochastic driving equals the linear perturbation-response structure. This is not a loose analogy — it names the exact observable (divergence field of a perturbed vs. reference copy) and predicts, in advance, that a *stable* survivor's damage collapses (a Test-3-relevant signal in its own right).

### Candidate regimes (pre-registered; R2 is the primary)

- **R0 — raw limit cycle (the NULL to be rejected).** Tap γ on the ring cells over time. Reads period (measured: 2.78/3.72/4.19). Included so T6.2 has a concrete null.
- **R1 — ambient stochastic driving.** Add a small integer perturbation to random cells each tick, measure fluctuation correlations. RISK: Exp 134's rule is sign-blind, transactional, exactly conserving; injected noise breaks its invariants and may destroy the pattern rather than probe it. Held as fallback.
- **R2 — perturbation-response / damage field (PRIMARY).** For each of many (phase φ, site s, sign ±) triples: copy the fixed point, perturb cell s's γ by ±1 at cycle-phase φ, evolve the perturbed and reference copies with the **exact same rule** for W ticks, record the divergence field d_i(t) = γ_i^pert(t) − γ_i^ref(t) over a fixed cell window. The **channels are the cells; the samples are the (φ,s,±,t) ensemble.** Correlation matrix of the divergence field → the Phase-0 observables (D_PR, dpr_sub, mds_dim90c). Uses the exact rule twice, injects nothing, cannot corrupt the pattern. This is the damage-spreading observable and, by fluctuation–dissipation, the in-calibration analog of Phase 0's noise regime.

### T6.1 — non-degeneracy
R yields a finite correlation matrix (no NaN) with ≥ 2 nonzero-variance channels on F1_K4. (R0 passes trivially — insufficient alone; hence T6.2/T6.3.)

### T6.2 — period-decoupling (the decisive gate)
R's reading must **not be a function of K alone.** Two pre-registered sub-tests, both required:
- **(a) Scrambled-period null.** Build a synthetic control with the *same* per-cell period-K sawtooth waveforms but **spatially independent** phase assignment (permute each cell's phase offset randomly, destroying ring adjacency). Run R on it. **If R reads the real pattern within 2 pooled sd of the scrambled-period control, R is reading period, not spatial coupling → REJECT R.** (R0 fails this by construction: R0 depends only on the per-cell waveforms, which are identical between real and scrambled.)
- **(b) Non-monotone-in-K signature.** Run R on K4/K6/K8. The R0 null is strictly K-monotone (2.78<3.72<4.19). A coupling-reading regime must break that monotone-in-K signature — either collapse the three (all are 1-cycles) or order them by embedding, but not reproduce the R0 ladder. Reported as evidence; (a) is the hard pass/fail.

### T6.3 — calibration-regime transfer
R must place readings on the **same benchmark scale Phase 0 validated**, or the reading is uncalibrated. Concretely: demonstrate the fluctuation–dissipation equivalence numerically on a **known Phase-0 fixture** — run R2's perturbation-response readout on the lattice3d/expander graphs under the frozen dynamics and show it reproduces the Phase-0 noise-driven separation (expander ≠ lattice3d, same sign, degree-matched no-collapse). If R2 on known geometry does NOT reproduce Phase 0's signed controls, R2 is a different instrument and Phase 0's calibration does not transfer → the gate fails on transfer even if T6.1/T6.2 pass.

## 2. Gate decision (pre-registered)

**PASS:** ∃ R (R2 primary, R1 fallback) passing T6.1 ∧ T6.2(a) ∧ T6.3. That R, with all its parameters (window W, ensemble size, cell window, perturbation magnitude), is then **frozen** and becomes the Test 3 readout.

**FAIL:** no candidate regime passes. Then the observer-rank instrument is **inapplicable to Exp 134 survivors**, Test 3 (RAW 134 §8.1/§12.3) cannot be run as designed, and *that inapplicability is the reported Phase 1 result.* **Pre-registered anti-rescue:** do not invent a fourth regime after seeing the data to save the gate; a post-hoc regime requires its own fresh pre-registration and skeptic pass.

## 3. If T6 passes — Test 3 execution (frozen only after the gate)

Measure the frozen R's rank observables on the K4/K6/K8 **survivors** vs. **dissolved** configurations (perturb a survivor past its wedge threshold, or use a known-failing fixture, e.g. the 3×3 ring that violates the geometric constraint). Pre-registered falsifier (RAW 134 §12.3): if surviving patterns' perturbation-response rank **expands** (approaches the ambient 3D-lattice benchmark or the noise ceiling) rather than staying **contracted** (ring-like, matching a 1-cycle benchmark), claim 5 (stability-selection fixes low observer-rank) is **refuted as stated**. Benchmark anchors (1-cycle graph; lattice3d) run under the identical frozen R alongside — never absolute readings (Phase 0 rule).

## 4. Test 3 reframe REQUIRED by the §0 finding

**Sequencing decision (user, 2026-07-03): DECIDE AFTER T6 RUNS.** The reframe is deferred until the gate tells us whether any readout regime is applicable at all — no point committing a Test 3 framing (and editing RAW 134 §8) before knowing there is a Test 3 to run. If T6 FAILS, this section is moot (inapplicability is the result). If T6 PASSES, choose among the options below before executing §3.

Because all current survivors are 1-cycles, the original "low vs. expand" contrast is weak. Three ways forward, to be chosen post-T6:

- **(A) Embedding-vs-intrinsic reframe (recommended).** Reframe Test 3 as: does a survivor's perturbation-response rank match its **intrinsic** 1-cycle dimension, or the **3D embedding** it sits in? Stability-selection's real claim becomes "a self-maintaining pattern reads as its own low intrinsic extent, not as the ambient substrate" — falsifiable, needs no new fixtures, and is the sharper question.
- **(B) Build higher-dimensional survivors.** Open prerequisite: does Exp 134's rule sustain anything but 1-cycles (linked rings, 2-complexes)? Unknown; would be its own experiment before Test 3.
- **(C) Accept the limitation.** Run Test 3 as a pure 1-cycle check with (A)'s benchmark, explicitly scoped as "cannot test the expansion falsifier without a high-D survivor."

## 5. Deviations

Any change to a frozen R parameter after the gate passes is a logged deviation (Phase 0 discipline). The anti-rescue clause (§2) is absolute: no post-hoc regime without fresh pre-registration.
