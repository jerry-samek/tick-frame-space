# Exp 137 Test 3 — stability-selection vs observer-rank — PRE-REGISTRATION

**Date registered:** 2026-07-04, after Phase 1b PASS (skeptic-corrected scope), BEFORE any Test-3 code is written or run.
**Gate:** Phase 1b (`RESULTS_phase1b.md`) — readout M validated as a fixed-K discriminator of coupling-graph structure (NOT embedding/dimension), replicated on the post-registration K=10 pair.
**Question (RAW 134 §8.1 / §12.3, as re-scoped by Addendum C §15.2):** do more-self-maintaining survivors read **lower** observer-rank (claim 5: stability-selection favors low-rank patterns; "cluster low" relative to the ambient benchmark), or do they **expand** toward the ambient reading (the falsifier)? Secondary: does a survivor's M-rank track its **coupling-graph structure** or its **intrinsic 1-cycle extent**?

## 1. Related work (scientist pass, 2026-07-04)

Readout M is damage spreading (Derrida-style): a localized state change and the divergence field it produces. Robustness-via-damage-spreading is the standard instrument for CA/Boolean networks (damage spreading & Lyapunov spectra of CA/RBNs, Chaos Solitons Fractals 2024; Kauffman frozen/chaotic phases; "Stability and Geometry of Attractors in Neural Cellular Automata", arXiv:2604.12720 — closest neighbor, studies attractor geometry vs stability in trained NCA). The specific correlate tested here — robustness vs participation ratio of the damage-correlation matrix — was not found in the search; the question appears open.

## 2. Fixtures (frozen): the complete K≤10 survivor family

All six survivors from Phase 1b's exhaustive census (proven complete for cycles, K ∈ {4,6,8,10}): FLAT_K4, FLAT_K6, FLAT_K8, CUBE_K8, FLAT_K10 (5×2 perimeter), TOWER_K10 (the 3D K=10 survivor). Two same-K contrast pairs: (FLAT_K8, CUBE_K8), (FLAT_K10, TOWER_K10).

## 3. Readings (frozen)

- **M(survivor):** the Phase-1b frozen readout (on-ring ±1 exhaustive ensemble, W=6K, memorized-template reference, dpr_sub decisive, bootstrap B=200). Values already measured in Phase 1b; recomputed here unchanged.
- **Impulse anchors at matched channel count N=K** (all via the frozen `graph_impulse_corr`, lam=0.99, W=200):
  - `CK` — abstract cycle graph C_K (the *intrinsic 1-cycle* anchor);
  - `RG` — the survivor's abstract ring graph (the *graph-structure* prediction);
  - `LAT` — lattice3d (12³ torus), K taps sampled as a radius-6 bundle, 10 bundle seeds → mean ± sd (the *ambient* benchmark of claim 5);
  - `EXP` — expander6 (1728 nodes, 6-regular), K taps, 10 seeds → mean ± sd (max-mixing reference, reported).
- **Calibrated position** (benchmark-relative, never absolute): `pos = (RG − CK) / (LAT_mean − CK)` — 0 = fully intrinsic-1-cycle-like, 1 = ambient-like. Computed within the impulse pipeline only (M and impulse values are not compared in absolute terms; their consistency is T3-B).

## 4. Self-maintenance scores (frozen; the graded quantity claim 5 needs)

- **S1 — kick-battery survival fraction** (deterministic, exhaustive): perturbations = on-ring ±1 (K phases × K sites × 2 signs), on-ring ±K (same ensemble), off-ring +K on every collar cell × K phases, single-cell deletion × K sites × K phases. After each kick: evolve 50·K ticks (exceptions = death); **survival** = exactly K nonzero cells at every tick of one further period AND state(t) == state(t+K) (translated/phase-shifted survivors count as survival; grown/mutated states count as non-survival, tallied separately).
- **S2 — noise time-to-death:** Phase-1b-recon r1_drive (magnitude jitter, p=0.005), 12 seeds, T=4000; per-seed tick of first alive<K; score = median across seeds.
- **Trap pre-named:** single ±1 on-ring kicks are known to be absorbed (T6 §C), so S1 may saturate at/near 1.0 for all fixtures on that stratum; the battery therefore includes the harsher strata (±K, off-ring, deletion). If S1 still has zero variance across fixtures, T3-C falls to S2 alone; that is reported, not patched.

## 5. Pre-registered questions and decision rules

- **T3-A (claim-5 falsifier — decisive).** For each survivor, where does `pos` sit? Family-level verdicts: **CLUSTER-LOW** if pos ≤ 0.5 for all six; **EXPAND (claim 5 falsified)** if any survivor's RG ≥ LAT_mean − 2·LAT_sd (ambient-indistinguishable or beyond); **INTERMEDIATE** otherwise (report the profile; claim 5 unsupported-but-unfalsified as "cluster low", i.e., its strong form fails).
- **T3-B (rank attribution — consistency extension of Phase-1b T-B to all six).** Spearman rank correlation between M dpr_sub and RG dpr_sub across the six survivors. Pre-registered: ρ ≥ 0.8 = M tracks graph structure family-wide; ρ < 0.8 = the T-B attribution does NOT generalize (flagged as an open anomaly, no rescue).
- **T3-C (robustness × rank — the stability-selection test).** Within each same-K pair, and for each robustness score (S1, S2): sign of (robustness difference) × (M dpr_sub difference). Claim 5 predicts **negative** (more robust → lower rank). Four sign readings (2 pairs × 2 scores). Verdicts: ≥3 negative = claim-5-consistent; ≥3 positive = claim-5-falsified (survivor robustness associates with rank *expansion*); otherwise INCONCLUSIVE. Cross-K correlations are reported as descriptive only (period K dominates rank; cross-K is confounded by construction).
- **T3-D (reported, non-decisive):** normalized rank dpr_sub/(K−1) per survivor vs matched-N LAT/EXP normalized readings — the "toward-ambient" profile in one table.

## 6. Anti-rescue

Whatever T3-A/B/C return is the result. No post-hoc regimes, no alternative observables, no re-weighting of the battery. Anomalies get traced or reported as open, per the standing skeptic discipline. A skeptic pass on the raw output is mandatory before RESULTS_test3.md.

## 7. Honest scope

- n = 6 survivors, 2 same-K pairs: T3-C is a sign test on four readings, not a correlation study. The census being provably complete for K≤10 means this is the WHOLE population, not a sample — but inference to "stability-selection in general" from four signs stays weak, and is stated as such.
- Rank readings are bootstrap-stability values on deterministic fixtures (Phase-1b Skeptic #8); anchors LAT/EXP carry real bundle-seed variance.
- Claim 5's original phrasing (RAW 134 §12.3) concerned *perceived dimension of observers*; this test operationalizes its Exp-134 shadow (rank of damage-correlation structure of self-maintaining patterns). Supporting/falsifying THIS is evidence about, not proof of, claim 5.
