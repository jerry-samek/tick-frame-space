# Exp 138 — Geometrogenesis: Directed Growth + Renewal Decay vs the Locality Wall

**Date:** 2026-07-10
**Status:** Design approved (Tom, 2026-07-10). Next: implementation plan.
**Question:** Can a substrate's *dynamics* select polynomial ball growth N(r) ∝ r^(d−1) — locality — without smuggled coordinates, lattices, or equilibrium annealing?
**Stakes:** RAW 134's five-fold convergence names this THE wall (§5, §13.2, §14.3, §16.2, §17.3). Addendum E: a substrate that selects r² ball growth gets Newton's 1/r² tail for free. Every prior in-house attempt (Exp 136 conserved subdivision; the 118–135 arc's fixed graphs) either assumed geometry or got expander/tree.

## 1. Prior art this design stands on (scientist pass, 2026-07-10)

- **Trugenberger, "Combinatorial Quantum Gravity" (arXiv:1610.05934); Kelly & Trugenberger (arXiv:1811.12905):** random regular graphs + Ollivier-Ricci curvature action, equilibrium Metropolis → second-order transition; short cycles condense; geometric (manifold-like) ordered phase. **The known graph-side positive.** Price: global equilibrium Hamiltonian — no time, no causal structure, god-view annealing.
- **2D causal set MCMC, Benincasa-Dowker action (Surya et al., arXiv:1110.6244; Glaser, arXiv:2306.09904):** phase transition between manifold-like and layered non-manifold orders. Causal-native but d=2 and sample space restricted to 2-orders (dimension partially assumed).
- **Prior negatives, priced:** Bolognesi (arXiv:1004.3128) — recursion DAGs *without selection* give no generic manifold; Rideout-Sorkin classical sequential growth → KR pancakes; Exp 136 — symmetric conservative kinematics → expander or tree; quantum graphity's leftover "disordered locality."
- **The gap Exp 138 targets:** nobody has shown geometric-phase selection under **directed causal growth with an immutable past**. The only known positives use equilibrium annealing, which the framework's arrow (tick-stream immutability, Doc 49) forbids. Either outcome is a contribution: selection under growth = the framework's first earned locality; a clean negative = "equilibrium is load-bearing," sharpening the wall into a theorem-shaped statement about the framework's own arrow.

## 2. Design decisions (made with Tom, 2026-07-10)

- **Bridge structure:** Phase 0 replicates the known positive as the *positive control* before the native phase runs (chosen over native-first and replication-only).
- **Native selector:** **growth + renewal decay** — selection as *survival* (Doc 28 renewal), not Metropolis acceptance (chosen over weighted sequential growth and a two-arm design).

## 3. Phase I0 — instrument calibration

**Observable (primary):** ball-growth exponent. For node v, N_v(r) = |{u : d(u,v) = r}| over graph shells (and, in Phase 1, over causal-depth shells). Estimator: fit log N(r) vs log r over the pre-plateau window → exponent ê; classify {polynomial: ê stable, finite | exponential: log N(r) vs r linear}. Exact estimator windowing frozen in I0 before any dynamics run.
**Signed controls:** 3D torus lattice (polynomial, defines the PASS band for ê), random 6-regular graph (expander — log-linear), balanced tree (exponential). Reuse Exp 136 Phase-0 battery observables (diameter vs log N) and Exp 137's bundle readout as secondary cross-checks.
**Gate G-I0 (reachable-range rule, applied to the decision rule itself):** the estimator must separate all three controls with signed margins, and both the PASS band and FAIL classifications must be attainable by construction *before* Phase 0/1 register anything. Lessons baked in from 136/137: signed opposite-prediction controls only, no resampling nulls, all tie-breaking in every rule explicitly specified with seeded RNG (the K=12 tie-breaking lesson), ≥10 seeds per configuration, moving-average ETA on long runs.

## 4. Phase 0 — positive control: Trugenberger condensation under our instrument

**Setup:** random regular graphs, N ≈ 500–1000, degree k = 2d (d = 3 target → k = 6). Action: Ollivier-curvature-based / short-cycle condensation term per Kelly-Trugenberger. Equilibrium Metropolis sweeps across the coupling range where the transition is reported.
**Curvature implementation:** exact small-support W₁ transport per edge OR the Jost-Liu combinatorial bound; both implemented, cross-validated on small graphs; the cheaper one used at scale only after agreement is demonstrated. (Implementation-plan decision, spec requires the validation.)
**Gate G-P0:** our I0 estimator detects the transition — disordered phase reads expander-like, condensed phase reads polynomial (inside or near the lattice band). PASS = the geometric phase is reachable within graph dynamics AND our battery sees it.
**If G-P0 fails:** stop; diagnose instrument vs replication via the I0 controls; nothing native runs on an unproven instrument. Report honestly (a failed replication of a published claim is itself reportable).

## 5. Phase 1 — the native experiment: directed accretion + renewal decay

**Substrate (framework axioms only):**
- **Growth:** DAG grown from a seed. Each tick, new calls attach to the causal frontier; parents drawn from a bounded *graph-distance* neighborhood of a frontier element (relational locality — no coordinates anywhere). Past immutable: dead elements remain in the record, become unattachable.
- **Renewal decay (the selector):** an element persists only if its neighborhood *re-converges* — participates in an undirected short cycle (a merge: two paths from a common ancestor re-meeting) of length ≤ L within a renewal window of W ticks. Frontier that never closes cycles decays. Survival, not acceptance: no global energy, no annealing, no god-view.
- This implements RAW 134 §13.4's job description literally: branching produces bʳ; survival must prune to polynomial.

**Sweep:** small grid over branching factor b, attachment radius ρ_att, cycle length L, renewal window W. ≥10 seeds per cell. Growth to ~10⁴–10⁵ elements per run or stationarity of the live graph, whichever first.

**Observables:** primary (GATING) — ball-growth exponent of the *live graph* over graph-distance shells (the I0 PASS band is defined on graph shells, so only that comparison is calibrated); causal-depth shells N(r) reported alongside as the §13.4-native view, not gated. Both tracked across growth epochs. Secondary — Exp 136 battery, degree distribution, cycle census, Exp 137 D_PR bundle readout as cross-check.

**Pre-registered outcomes (decision rules frozen before Phase 1 runs, PASS band imported from I0):**
- **GEOMETRIC SELECTION:** stable polynomial plateau inside the lattice-control band, sustained across growth epochs, robust across seeds and a non-degenerate region of the grid → the framework's first earned locality. Feeds Addendum E (gravity tail) and the claim-5 program (§16.2's "reachable falsifier" fixture class).
- **HONEST NEGATIVE:** expander/tree phases across the entire grid → *renewal-decay under directed growth is insufficient; equilibrium is load-bearing.* Recorded as the sharpest statement of the wall to date: the framework's arrow forbids the annealing the only known positives use.
- **KNIFE-EDGE:** polynomial only on a measure-zero tuned sliver of the grid → negative per RAW 134 §12.1's criterion (a knife-edge is not a selection).

## 6. Traps pre-named

1. **Bolognesi is the prior negative for unselected recursion DAGs.** Exp 138's delta is the decay term; that is what is being tested, and the RESULTS doc must say so regardless of outcome.
2. **Cycle length L is a rule parameter (local structure), not smuggled geometry — but the PASS band is.** The band comes from I0 controls, frozen before Phase 1; tuning it after seeing Phase-1 data is the smuggle.
3. **Tie-breaking:** every choice point in growth/decay (which frontier element, which parents, decay order) uses declared, seeded randomness — no dict/set iteration order anywhere (K=12 census lesson).
4. **Ordering/exhaustion asymmetry:** Phase 1's grid must include cells *expected* to fail (pure growth, no decay: Bolognesi control; decay with L=∞: no selection) as in-experiment signed controls.
5. **Skeptic passes mandatory** after Phase 0 and after Phase 1, before any RESULTS doc; anti-rescue clause applies (no post-hoc regimes without fresh pre-registration).

## 7. Cost & tooling

Python, background runs with `python -u`. Phase 0 is the heavy part (per-edge curvature over MCMC sweeps): hours-scale with the combinatorial bound, validated against exact transport on small graphs. Phase 1 growth/decay is local bookkeeping: minutes-to-hours per grid cell. Directory: `experiments/138_geometrogenesis/` with PREREG_I0/P0/P1 frozen in that order.

## 8. What this experiment cannot do (scope honesty)

It cannot solve geometrogenesis in general; it tests ONE selector (cycle-closure renewal) under ONE growth discipline (frontier accretion, immutable past) against ONE known equilibrium positive. It does not target d=3 specifically (exponent value is reported, not gated). It does not touch Lorentz invariance (the framework has already paid with it — RAW 134 §10 Sorkin/Belenchia fork). A GEOMETRIC SELECTION outcome would be the start of a research line, not its end: stability under perturbation, the gravity tail (Addendum E), and the claim-5 falsifier would each need their own pre-registered follow-ups.
