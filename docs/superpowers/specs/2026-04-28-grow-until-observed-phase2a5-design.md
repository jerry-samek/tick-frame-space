---
title: Grow Until Observed — Phase 2A.5 (Experiment 132)
date: 2026-04-28
status: spec sketch — pending review and brainstorm
theory: docs/theory/raw/132_untested_capacitor.md (RAW 132 §3.5 H5.7, §10.11)
internal precedents: RAW 044 (Fallible Commit), Exp 64_109 v8 (self-subtracting transport), Exp 64_109 v21 (frozen planet bug)
phase 2 result: HONEST NEGATIVE; god-view measurement was framework-incompatible
predecessor specs: 2026-04-28-grow-until-observed-phase2-design.md (Phase 2)
---

# Experiment 132 Phase 2A.5: Self-Subtracting Transport via Three-Run Superposition

## Why this spec exists

Phase 2 measured god-view substrate state — direct read of charge, threshold, load across all cells. The result was a falsification: H3.5 (threshold(r) monotonic), H4.1 (load(r) monotonic), H5.1 (drift toward planet) all rejected.

But Phase 2's measurement violated a framework principle the RAW 132 v0–v3 didn't engage with: **observers in this substrate must subtract their own contribution to perceive external fields** (RAW 044 Fallible Commit Principle, Exp 64_109 v8 self-subtracting transport). Without self-subtraction, an entity reads its own dominant field and sees itself as static — the "frozen planet" bug from Exp 64_109 v21.

Phase 2A.5 is the entity-relative version of Phase 2's measurement, designed around the framework's prior commitment to self-subtracting transport.

## Goal

Test whether the test pattern's *perceived* environment around a planet — measured via self-subtraction rather than god view — exhibits the radial profile shapes (H3.5, H4.1) and drift signal (H5.1) that Phase 2's god-view measurement could not detect.

This is **not a re-tuning of Phase 2's parameters.** It is a measurement-methodology fix grounded in prior framework commitments.

## What Phase 2A.5 tests (the H5.7 hypothesis)

Per RAW 132 §3.5 H5.7 (added in v3.1): an entity-relative observer must subtract its own contribution from substrate state. Operationally this means: for measurements done at radius r from a planet "from the test pattern's perspective," subtract whatever the test pattern alone would produce at radius r in an empty substrate.

The simplest implementation: **superposition test via three runs.**

| Run | Setup | Measures |
|---|---|---|
| **R1: planet-only** | 21×21×3 substrate, planet K=4 only, no test pattern. | threshold(r), load(r), all cells/connectors. This IS the test pattern's perceived environment under H5.7 (since the test pattern's self-subtracted contribution would equal whatever it would produce alone; if H5.7 holds, the test pattern *should* see this profile when in the combined run). |
| **R2: test-only** | 21×21×3 substrate, test K=4 only, no planet. | threshold(r), load(r), all cells/connectors centered on test. This is what the test pattern subtracts from its perception of the combined run. |
| **R3: planet + test combined** | Same as Phase 2 (which we already ran on 2026-04-28). | god-view profile — full substrate state at all cells/connectors. |

**The superposition prediction:** if H5.7 (self-subtracting transport) holds and superposition is valid in this substrate, then:

```
R3_at_test_cells − R2_at_test_cells ≈ R1_at_test_cells
```

i.e., the test pattern's perceived environment in R3 (combined run, with self-subtraction) equals the planet-only profile R1 evaluated at the test cells' locations.

**Three possible outcomes:**

1. **Superposition holds, R1 matches the difference exactly.** H5.7 is operationally consistent; self-subtraction is well-defined; the test pattern's perceived environment is exactly the planet-only field. Phase 2's failure was purely measurement methodology — entity-relative measurement should reveal H3.5, H4.1, H5.1 at correct functional shapes.

2. **Superposition holds approximately, with deviations attributable to interaction.** The substrate has nonlinear coupling between patterns; self-subtraction works but is not a simple linear difference. Phase 2A.5 then becomes the basis for designing a more refined entity-relative measurement.

3. **Superposition fails — R3 − R2 is not even close to R1.** Patterns interact through substrate in ways that don't decompose linearly. H5.7's straightforward formulation is wrong; either substrate dynamics are inherently nonlinear under multi-pattern conditions, OR the framework's self-subtracting transport principle from Exp 64_109 v8 needs revisiting on capacitor substrate.

## What Phase 2A.5 deliberately does NOT do

- **Does not retune any parameter from Phase 2.** Same `baseline_threshold = 100`, `adaptation_rate = 0.1`, `relaxation_rate = 0.05`, `deposit_amount = 50`, `load_coefficient = 0.1`. Phase 2's failure was in measurement, not parameters.
- **Does not implement source-tagging in the substrate.** The three-run superposition test answers H5.7's main question without needing per-deposit `source_pattern_id` tags. (If superposition fails, source-tagging becomes the next experiment — but that's a Phase 2A.6.)
- **Does not modify substrate dynamics.** Same `tick.py`, same `capacitor.py`, same `connectors.py`.
- **Does not address H4.1 (load mechanism) tuning.** If R1 alone shows flat load(r), then the load mechanism itself needs revisiting — that's Phase 2A.2.
- **Does not change substrate scale or connectivity pattern.** 21×21×3, full lattice connectivity, same as Phase 2.

## Three-run experimental setup

### Run R1: planet-only

Same substrate setup as Phase 2 EXCEPT no test pattern. Bootstrap only the planet K=4. Run 5,000 cycles. Record snapshots of (charge, threshold, load) at the same intervals as Phase 2 (every 100 ticks).

This produces the **planet-only profile**: threshold(r) and load(r) around planet, uncontaminated by test pattern's halo.

### Run R2: test-only

Same substrate setup as Phase 2 EXCEPT no planet. Bootstrap only the test K=4 at its original position (15.5, 10.5, 1). Run 5,000 cycles. Record snapshots.

This produces the **test-only profile**: threshold(r) and load(r) around test pattern position, uncontaminated by planet's halo. Required as the subtraction term.

### Run R3: combined (already done as Phase 2)

Phase 2's existing run is R3. We don't need to re-run it. We have `experiments/132_grow_until_observed/phase2_run.log` and the snapshots in memory from that run (or can re-run if needed).

### Post-hoc analysis

For each cell `c` at distance `r` from planet centroid AND for each connector `e` at distance `r` from planet centroid:

- `R1[c]`, `R2[c]`, `R3[c]` for thresholds
- `R1[e]`, `R2[e]`, `R3[e]` for loads

Compute `R3 − R2 − R1` — the residual after self-subtraction. If H5.7 holds, this residual should be near zero everywhere.

Then plot:
- `R1(r)` from planet center: the "true" planet profile.
- `R3(r) − R2(r)` from planet center, restricted to test-pattern-region cells: the entity-relative measurement.
- Compare shape, magnitude.

## Phase 2A.5 success criteria

The experiment "passes" if it can answer cleanly which of the three outcomes (above) is the case. Specifically:

- **Define linearity statistic:** `χ² = sum over cells of (R3[c] − R2[c] − R1[c])² / R1[c]²`. Smaller is better.
- **Define entity-relative profile:** measure `(R3 − R2)(r)` from planet centroid, fit to functional forms (1/r², 1/r, exponential, etc.).

Phase 2A.5 reports:
1. Outcome category (1/2/3 from above).
2. Linearity statistic χ².
3. Entity-relative threshold(r) and load(r) profiles, with monotonicity check.
4. Comparison to GR shapes (preliminary, full quantitative fit is Phase 3).

## Falsification implications

If Phase 2A.5 outcome is **(1) superposition holds + R1 shows monotonic profile + entity-relative drift detectable**: H3.5, H4.1, H5.1 are not falsified — Phase 2's god-view measurement was just wrong methodology. Phase 3 (quantitative GR fit) becomes feasible.

If Phase 2A.5 outcome is **(2) approximate superposition with corrections**: entity-relative measurement framework needs refinement. The test pattern's perception is more subtle than simple subtraction. Phase 2A.6 (source-tagged measurement) becomes the next step.

If Phase 2A.5 outcome is **(3) superposition fails entirely**: the framework's self-subtracting transport principle from Exp 64_109 v8 doesn't transfer to capacitor substrate. RAW 132's H5.7 is falsified. The drift question may be unsolvable in this substrate ontology, OR a fundamentally different observation principle is needed.

If Phase 2A.5 outcome is **R1 itself shows flat profile**: the load(r) flatness from Phase 2 was not caused by test-pattern contamination but by load mechanism saturation/equilibration. Phase 2A.2 (load coefficient sweep) becomes priority.

## Implementation scope

Substantially smaller than Phase 2's plan, since most modules already exist:

- **No new substrate code.** Same Phase 1+2 modules.
- **Two additional setup configurations** — planet-only and test-only — adapted from Phase 2's setup.
- **One additional analysis script** — superposition test (R3 − R2 − R1) and entity-relative profile.
- **One additional deliverable test** — `phase2a5_test.py` running R1 and R2 (R3 reuses Phase 2's recorded data).
- **RESULTS_phase2a5.md** with per-outcome reporting.

Estimated effort: 2–3 hours including run time. R1 and R2 each take ~7 minutes (Phase 2's 21×21×3 substrate); analysis is fast.

## Deliverables

```
experiments/132_grow_until_observed/
├── ... existing Phase 1+2 files ...
├── phase2a5_setup_planet_only.py   # R1 setup (no test pattern)
├── phase2a5_setup_test_only.py     # R2 setup (no planet)
├── phase2a5_analysis.py            # Superposition test + entity-relative profiles
├── phase2a5_test.py                # Deliverable: runs R1 and R2, applies analysis
├── phase2a5_run.log                # Captured output
└── RESULTS_phase2a5.md             # Per-outcome report
```

## Open questions / risks

- **R2 setup question:** when we run "test-only," should we still have full lattice connectivity (the substrate's structural property) or only test pattern's cycle connectors? Phase 2 used full connectivity. Decision: keep full connectivity for R2 — the substrate's connectivity structure is part of what makes a pattern's halo what it is. Without other patterns to deposit into the lattice, halo cells stay quiescent (they receive only test pattern's deposits).
- **Definition of "test pattern position":** in R2 the test pattern is alone in substrate; its "centroid" is just its geometric center (15.5, 10.5, 1). In R3 the same. No drift between R2 and R3 is the null result for centroid-based reading; profile shape difference is the signal.
- **Cross-cell comparison validity:** R1 is centered on planet (10.5, 10.5, 1); R2 is centered on test (15.5, 10.5, 1). To compare R1's profile-at-test-cells to R3 − R2 at test cells, we evaluate R1 at the cells located at distance |r_test − r_planet| = 5 from planet centroid. This is straightforward but worth being explicit.
- **Connector midpoint vs cell position for load profile:** Phase 2 used midpoint. Maintain same convention.

## Phase numbering note

This is Phase 2A.5 — between Phase 2 and Phase 3. The "A" indicates "alternative measurement of Phase 2's hypotheses" rather than "next phase." Phase 2A.1 (planet-only), Phase 2A.2 (load coefficient sweep), Phase 2A.3 (larger substrate), Phase 2A.4 (partial connectivity) remain as parallel options if Phase 2A.5 reveals more is needed.

If Phase 2A.5 outcome (1) holds (superposition + monotonic profiles + drift signal), Phase 3 (quantitative GR fit) is unblocked. Otherwise, the next experiment is determined by which Phase 2A.x scenario the falsification points to.

## What this spec inherits

- Substrate primitives from Phase 1 (substrate.py, capacitor.py, connectors.py, tick.py, parameters.py, lattice.py).
- Recording infrastructure from Phase 2 (recording.py, profile.py, observer.py).
- Tuned parameters from Phase 1 + Phase 2 (no retuning).
- The R3 dataset from Phase 2 (already recorded; reused without re-running).

This spec proposes minimal addition for maximum hypothesis-test value, leveraging RAW 132 §3.6's elimination strategy: a single experimental run program (R1 + R2; R3 already done) tests H5.7 and resolves the methodological question raised by Phase 2's negative result.
