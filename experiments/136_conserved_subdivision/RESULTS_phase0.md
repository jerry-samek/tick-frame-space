# Phase 0b - bare-rule baseline

Bare rule = uniform refinement, equal halves, indiscriminate all-glue adjacency (PREREG A.1). Deterministic; 1 run per N + finite-size trend.


## Finite-size trend

| target | leaves | mean_deg | diameter | d_H | d_s | loop_density |
|---|---|---|---|---|---|---|
| 32 | 32 | 31.0 | 1 | nan | 0.00 | 14.53 |
| 64 | 64 | 63.0 | 1 | nan | 0.00 | 30.52 |
| 128 | 128 | 127.0 | 1 | nan | 0.00 | 62.51 |
| 256 | 256 | 255.0 | 1 | nan | 0.00 | 126.50 |
| 512 | 512 | 511.0 | 1 | nan | 0.00 | 254.50 |

## Verdict

Bare-rule outcome: **exactly the COMPLETE GRAPH K_N** (mean degree = N-1 at every N: 31, 63, 127, 255, 511; diameter = 1; d_s = 0 instant-mixing; loop density saturated; Ricci ~ +0.5 positively-curved, matching the complete-graph calibration). Not merely "near-complete" — it is the maximal-connectivity trivial limit.

Mechanistically inevitable: at genesis the two cells are adjacent, and indiscriminate all-glue makes every child inherit adjacency to every parent-neighbor's children, so adjacency propagates to all pairs -> K_N. There is **no emergent geometry** (dimension ill-defined).

## Implication for Phase 1 (baseline informing design, per null-first discipline)

This sharpens the Phase-1 plan: **selective, boundary-matched gluing (the "loops" ingredient) is not one of four co-equal ingredients — it is FOUNDATIONAL.** Without it the substrate is K_N regardless of any other ingredient. Therefore Phase 1 should be **re-ordered to lead with boundary-matched gluing** (it is what creates a non-trivial graph at all), and only then ablate non-locality / difference-direction cuts / layering+curvature penalty *on top of* a selectively-glued base. The all-glue bare rule is best understood as the "null of the null" (maximal degenerate), confirming the readout has zero geometry absent selective gluing.

Per PREREG A.4 this is a baseline, not a program falsification.

## Phase 0 status: COMPLETE
- Substrate core (exact conservation, append-only) + readout (leaf boundary-adjacency): built, tested.
- Measurement battery: built and CALIBRATED (gate passed; separates 3D/2D/tree/blob; over-smoothing detected). Estimators read ~0.5 low -> WIN is benchmark-relative (PREREG A.3, frozen).
- Bare baseline: K_N (this doc).
Next: Phase 1 plan (lead with boundary-matched gluing), pre-registered before any run.


Full table: results/phase0_baseline.json
