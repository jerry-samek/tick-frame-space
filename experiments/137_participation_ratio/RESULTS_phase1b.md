# Exp 137 Phase 1b — RESULTS: redesigned applicability gate

**Date run:** 2026-07-04 (gate + skeptic pass + skeptic-mandated follow-ups, one session).
**Pre-registration:** `PREREG_phase1b.md` (frozen 2026-07-03, before this run).
**Code:** `phase1b_gate.py` (the registered gate), `phase1b_skeptic_tests.py` (post-gate distinguishing tests T-A..T-E, demanded by the skeptic pass, run before this doc was written).
**Raw output:** `results_phase1b_gate_console.txt`, `results_phase1b_skeptic_console.txt`, `results/phase1b_gate.json`, `results/phase1b_skeptic_tests.json`.

---

## Verdict

**Registered letter: PASS** (G-M1 ∧ G-M2 ∧ G-M3, exactly as pre-registered, no mid-run changes, no patches, first-try run).

**Skeptic-corrected content — what is actually certified:**

1. **Readout M does NOT read "3D embedding." It reads the survivor's coupling-graph structure.** The decisive test (T-B): the same spectral readout on the two fixtures' *abstract* ring graphs — no lattice, no renewal rule — reproduces the CUBE>FLAT ordering (3.93 vs 2.23). The embedding enters only through the adjacency graph it induces. Every claim below is worded accordingly; the word "embedding" in PREREG §1/§5 was a category error (the whole pipeline factors through the radius-2 adjacency graph; two survivors with isomorphic local graphs would read bit-identically regardless of how they sit in Z³).
2. **At fixed period K, M's dpr_sub distinguishes survivors with different coupling graphs — and this replicates on a fresh pair discovered after the gate froze.** Exhaustive enumeration (T-C) found a previously unknown 3D survivor at K=10; the new planar/3D pair separates in the same direction with a gap 3× the K8 gap (6.900±0.024 vs 5.450±0.024). This, not the gate run, is the non-circular confirmation.
3. **Period K remains the instrument's dominant axis.** dpr_sub is strictly monotone in K (2.85 → 3.78 → 4.36 → 5.45 planar), and the K6→K8 planar step (0.58) exceeds the K8 cube–flat gap (0.48). Supported statement: *dpr_sub is not a function of K alone*; fixed-K contrasts only.
4. **Complete survivor census for K ≤ 10 (new substrate result, proven by enumeration):** K=4: 1 survivor (planar square); K=6: 1 (planar 3×2 perimeter; **no 3D K=6 survivor exists**); K=8: exactly 2 (FLAT_K8, CUBE_K8 — the frozen pair provably exhausts K=8); K=10: exactly 2 (planar 5×2 perimeter + one 3D survivor, 6 cells in z=0 / 4 in z=1). PREREG §3's "open substrate question" is now answered for cycles: **the rule does sustain 3D cycles at K≠8** (K=10 yes, K=6 no). Non-cycle survivors remain unaddressed.
5. **Instrument regime boundary:** the gap is stable across the on-ring kick family (magnitude 1..K, horizon 3K..12K, both pattern signs: same sign, z = 8–29 in all 24 cells) but **reverses under off-ring +K kicks** (CUBE 24.2 < FLAT 29.5). The frozen readout M is on-ring ±1 only, so the gate is unaffected — but this independently falsifies any "dimension reader" interpretation: a dimension reading should not flip with kick type; a graph-spectral response to a different perturbation operator can.

**Consequence for Test 3:** runnable, with re-scoped wording. The family now has two same-K contrast pairs (K=8, K=10) plus a planar K-ladder. Test 3's question becomes: does a survivor's M-rank track its *coupling-graph structure* (chords/regularity) or its *intrinsic 1-cycle extent*, and do more-self-maintaining patterns read lower or higher rank — always benchmark-relative at fixed K, never absolute. The "embedding-vs-intrinsic" framing of PREREG §5 is renamed "graph-structure-vs-intrinsic" (user-approved 2026-07-04, recorded with the god-view scope correction as RAW 134 Addendum C §15).

## Gate results (registered)

| gate | criterion | result | outcome |
|---|---|---|---|
| G-M1 | CUBE_K8 vs FLAT_K8 ≥ 2 pooled sd (dpr_sub) | 4.839±0.019 vs 4.361±0.028, z = 19.94 | PASS |
| G-M2 | FLAT_K8 set A vs set B < 2 sd | z = 0.07 | PASS (but see Skeptic review: tautological) |
| G-M3 | expander6 > lattice3d under impulse readout | 59.94 > 45.58 | PASS (regression re-run of T6.3, zero new bits) |
| G-M4 | inside-consistency by construction | memorized-template reference; position-free observables | holds |

Secondary observable: **mds_dim90c does NOT separate the K8 pair** (4.77±0.02 vs 4.81±0.02). See T-E for the traced mechanism.

Confound check (post-gate): both K8 fixtures have n_active = 8 (divergence confined to ring cells; collars all zero-variance) and identical frac_nonzero (0.938) — the separation is carried by correlation structure, not channel count.

## Skeptic review

Fresh-context skeptic pass run on the raw gate output *before* any results narrative was written (per skeptic skill). Its bottom line: "registered-letter PASS, evidential content near zero" — G-M1 re-executed a number known from recon, G-M2 was arithmetically unfailable, G-M3 was a rerun, and "reads embedding" is a category error. Every objection and its resolution:

| # | objection | resolution |
|---|---|---|
| 1 | **G-M1 circularity:** the decisive statistic (≈21 sd) was measured by the recon before the PREREG froze; on a deterministic substrate the gate run could not fail. | **ACCEPTED.** The gate run is downgraded to an implementation check (memorized-template `readout_m` reproduces `r2_damage`: 19.94 vs 21.10 across bootstrap seeds). The non-circular evidence is the K=10 replication (T-C), on a pair that did not exist when the gate froze. |
| 2 | **G-M2 tautology:** two bootstrap means over the same deterministic matrix differ by ~0.1·sd; P(fail) ≈ 10⁻⁸⁸. Same defect class as T6.2a. | **ACCEPTED** as registered-hollow. Known limitation: a deterministic substrate has no population variability for a true negative control. The *meaningful* null that exists is T-D: R0 gap = 0.000 and shuffled-M gap = 0.002 (vs M gap 0.478) — the discrimination requires the coupling structure of the divergence field, and vanishes without it. |
| 3 | **Observable forking:** dpr_sub chosen as decisive after the recon showed it separates; mds_dim90c (which does NOT separate) demoted to "reported." | **ACCEPTED + FIXED via T-E.** Disclosed at build time; now mechanistically traced: CUBE's M-correlation spectrum has four near-degenerate leading eigenvalues [1.71, 1.64, 1.57, 1.53] (mirroring the cube graph Q₃'s eigenvalue degeneracy), FLAT's has three-then-gap [2.21, 1.94, 1.68 ǀ 0.68…]. dpr_sub is a spectral-*shape* (inverse-Simpson) statistic and resolves this; mds_dim90c is a 90%-cumulative-mass *count* and lands ≈4.8 for both. All claims are explicitly dpr_sub-specific. |
| 4 | **"Reads embedding" is a category error** — the pipeline factors through the adjacency graph. | **FIXED via T-B.** Confirmed: abstract ring graphs reproduce the ordering (cube graph 3.93 > C8+2chords 2.23). All claims reworded to "reads coupling-graph structure." |
| 5 | **PREREG §3 "resolve first" demoted to non-gating; the three probes were predicted failures (due-diligence theater).** | **FIXED via T-C.** Exhaustive enumeration of all closed self-avoiding K-cycles in Z³ up to isometry × cyclic shift × reversal, K ∈ {4,6,8,10}; `sustains()` on every class. Census in Verdict §4; the K=8 pair is proven exhaustive; a new 3D K=10 survivor found. |
| 6 | **CUBE>FLAT mechanism untraced** (chord count / degree homogeneity suspected). | **FIXED via T-B + T-E.** The suspected null — "M measures degree-regularity/chord structure, nothing about 3D per se" — is *confirmed as the parsimonious reading*. In the K≤10 family, 3D-ness and chord count co-vary perfectly, so they cannot be decoupled by these fixtures; T-B settles attribution at the graph level. |
| 7 | **Single contrast pair (n=1).** | **FIXED via T-C.** Second same-K pair found at K=10; separation replicates, same sign, larger gap (1.45 vs 0.48). |
| 8 | **σ-laundering:** z=19.94 is bootstrap-resampling stability on a fixed deterministic matrix, not population separation. | **ACCEPTED.** All z values in this doc are bootstrap-stability z, stated as such. There is exactly one realization of each fixture. |
| 9 | **G-M3 rerun adds zero information.** | **ACCEPTED.** Kept as a regression check only. |
| 10 | **"Test 3 runnable" overstated (fixture starvation).** | **FIXED via T-C** — the starvation was real at the time of the claim and was resolved by enumeration, not by the gate. Test 3 is runnable with the re-scoped wording in Verdict. |
| 11 | **Settings fragility unexplored.** | **FIXED via T-A.** Stable across sign × magnitude × horizon on-ring (24/24 cells, z ≥ 8.4); ordering reverses off-ring (+K collar kick) — recorded as the instrument's regime boundary. |

## Post-gate distinguishing tests (skeptic-mandated, not pre-registered)

Run after the gate, before this doc; labeled follow-ups, not rescues — none alters a registered gate outcome, they bound what the pass *means*.

- **T-A (settings sweep):** gap positive and z ∈ [8.4, 28.8] in all 24 on-ring cells (sign ±1 × mag {1,2,3,8} × W {3K,6K,12K}); pattern-sign symmetric (sign-blind rule, as expected). Off-ring +K kick: ordering reverses, dpr_sub jumps to ~24–29 (collar channels activate; different perturbation operator). |
- **T-B (abstract-graph surrogate):** FLAT ring graph (C8 + chords {(1,6),(2,5)}, degrees 2/3 mixed) dpr_sub 2.23; cube graph (C8 + 4 chords, 3-regular, vertex-transitive) 3.93. Ordering reproduced ⇒ adjacency structure suffices. |
- **T-C (exhaustive census):** classes/survivors — K=4: 1/1, K=6: 3/1, K=8: 11/2, K=10: 73/2. New 3D K=10 survivor: cells (0,0,0),(1,0,0),(2,0,0),(2,1,0),(1,1,0),(0,1,0),(0,1,1),(1,1,1),(1,0,1),(0,0,1); rank 3, 5 chords, degrees [2,2,3,3,3,3,3,3,4,4]; dpr_sub 6.900±0.024 vs planar K=10 5.450±0.024. Wall clock 228 s total. |
- **T-D (do-nothing baseline):** R0 raw-series dpr_sub identical for both K8 fixtures (3.441 vs 3.441, gap 0.000); per-channel-shuffled M gap 0.002. The perturbation-divergence coupling structure is what discriminates. |
- **T-E (observable reconciliation):** spectra and mechanism in Skeptic review #3. Both |corr| matrices show antipodal pair-blocks (~0.44–0.60); CUBE's is homogeneous across pairs, FLAT's is not. |

## Known limitations

- G-M2 is registered-hollow (Skeptic #2); the operative null is T-D. Any future gate on a deterministic substrate must use a structural null (shuffle/abstract-graph), not a resampling null.
- All z values are bootstrap-stability, not population, z.
- Attribution below the graph level is impossible in this family: 3D-ness ⟺ more chords among K≤10 survivors. A fixture where they decouple (a planar survivor with cube-graph-like regularity, or a 3D survivor with C8-like inhomogeneity) does not exist under the rule for K≤10; K=12 enumeration (~minutes-to-hours) could be run if Test 3 needs it.
- Census covers cycles only; non-cycle survivors (PREREG §3's second open question) remain unprobed.
- The god-view scope correction (PREREG §0) and the "graph-structure-vs-intrinsic" rewording of RAW 134 §8/§12.3 were both **approved by the user 2026-07-04** and recorded as RAW 134 Addendum C (§15).

## What this proves / does not prove

- **Proves:** the inside-consistent readout M, restricted to on-ring ±1 kicks and the dpr_sub observable, discriminates same-period Exp 134 survivors by their ring coupling-graph structure, replicated on a post-registration K=10 pair; the K≤10 cycle-survivor census is exhaustive; the instrument's dominant axis remains period K.
- **Does not prove:** that M reads dimension, embedding, or geometry in any sense beyond the induced adjacency graph; that the discrimination extends to non-cycle survivors, other rules, or off-ring perturbations (it provably reverses there); anything about Test 3's actual question (stability-selection vs rank) — that experiment is now unblocked but has not run.
