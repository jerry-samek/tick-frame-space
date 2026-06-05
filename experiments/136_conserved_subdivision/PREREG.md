# Exp 136 — PRE-REGISTRATION (frozen 2026-06-05)

RESULTS docs may only report against this. Substrate thresholds (§A.3) may NOT change after seeing results. Instrument fit-windows (battery probes) MAY be calibrated until the calibration gate passes, then frozen.

Spec: `docs/superpowers/specs/2026-06-05-conserved-subdivision-substrate-design.md`
Plan: `docs/superpowers/plans/2026-06-05-conserved-subdivision-phase0.md`

## A.1 Substrate representation (pinned)
- Measure = `fractions.Fraction`, total always `Fraction(1)`; conservation = exact sum, every tick.
- Bare cut: each selected leaf → k=2 children, equal halves.
- Bare adjacency: on splitting leaf c (leaf-neighbors Nbr(c)), the 2 children are mutually adjacent AND each inherits adjacency to every member of Nbr(c)'s children. (Deliberately densifying — characterizing where that lands is Phase 0b's point.)
- Bare selection: ALL leaves split each tick (uniform refinement).
- Bare x(c): the leaf's boundary-address (bit-string root→leaf). Same/Different = address shared-prefix length. (Branch-chain NAND, ancestral/spatial non-locality = Phase-1 toggles.)

## A.2 Ingredient toggles (all OFF in Phase 0; Phase 1 flips one at a time, first-pass forms pre-registered)
- nonlocality: none | ancestral(R_anc=4) | spatial(R_sp=2)
- diff_direction: equal split | principal-difference-axis split (Verma–Kpotufe–Dasgupta)
- loops: bare(all-glue) | boundary-matched gluing
- penalty: none | layering+curvature (suppress only-min/only-max relations; bias chain-lengthening; penalize Ollivier-Ricci < kappa_min=-0.3)

## A.3 Locked pass thresholds
**CALIBRATION UPDATE (frozen 2026-06-05, at the gate, BEFORE any substrate run):** the graph
dimension estimators read ~0.4-0.5 LOW in absolute terms on finite graphs (a known bias confirmed
on the Poisson-3D positive control). Per spec §9, WIN is therefore **benchmark-relative** — match the
Poisson-3D calibrated reference and be separated from the nulls — NOT an abstract 3.0. Frozen reference
values (Poisson-3D, n=8000, deg~7.5): **d_s ≈ 2.5, d_H ≈ 2.6, loop_density ≈ 2.7, Ollivier-Ricci ≈ 0**.
2D-grid reference: d_s≈1.9, d_H≈1.8, loops≈1.0. Tree: d_s≈1.1, loops≈0.
- Dimension WIN requires ALL: d_s ∈ [2.2,3.2] AND within ±0.4 of the Poisson-3D control; d_H ∈ [2.2,3.2];
  d_s − (2D-control d_s) > 0.4 (distinctly above 2D); loop_density > 0.3 and increasing;
  Dirichlet energy not decaying below 10% of initial; Ollivier-Ricci median ∈ [−0.2,+0.2] (flat).
- Calibration finding: **Ollivier-Ricci flags POSITIVE curvature (clustered/complete) vs flat (~0); it does
  NOT flag sparse trees as negative** (pendant-edge effect). Tree/hyperbolic detection = spectral-dim (lowest)
  + loop_density (~0) + diameter scaling (log N). Ricci is the flatness / positive-curvature probe only.
- Myrheim-Meyer (Minkowski) deferred; poset probe = product-order ordering dimension (`1 - log2(f)`).
  chain height exponent ~1/d retained as a secondary poset probe.
- Betti-number stability (3-manifold) is a WIN refinement deferred to Phase 1+ (needs an embedding;
  Phase 0 characterizes via d_s/d_H/loops/Ricci, all pure or POT-based).
- Seeds: ≥20 per reported number (Phase 1; bare rule is deterministic — Phase 0b reports 1 run/N + finite-size scaling). Report median + IQR.
- Scale: finite-size scaling required; dimension claim must hold (not drift to 2) up to ≥ n=5000 leaves.
- Calibration gate: battery must return WIN-band for Poisson-3D, ~2 for 2D grid, ~4/3 d_s for tree, and FAIL all bands for Eden blob and diffusion field. Else instruments not trusted; no substrate result counts.

## A.4 Program falsifier
If the full Phase-1 rule still misses the WIN band at scale across seeds → record a clean negative and STOP. No sixth ingredient, no reframe. A new attempt must explicitly surrender a named commitment (go global/energetic, or abandon strict locality).

## Modeling notes (pinned)
- Poset for Myrheim-Meyer / chain probes = transitive closure of the history tree parent→child relation. (Space is read from leaf-adjacency; MM/chain are poset probes.)
- Betti for the coordinate-free leaf-graph = computed on a spectral/spring embedding (calibration uses point clouds with exact ground truth).
