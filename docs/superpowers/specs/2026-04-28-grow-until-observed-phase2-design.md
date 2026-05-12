---
title: Grow Until Observed — Phase 2 (Experiment 132)
date: 2026-04-28
status: spec — pending Phase 2 implementation
theory: docs/theory/raw/132_untested_capacitor.md (RAW 132 — see §3.5 and §3.6 in particular)
phase 1 result: PASS (5,000-cycle K=4 cycle sustained; substrate primitives validated)
predecessor specs: 2026-04-28-grow-until-observed-design.md (Phase 1)
---

# Experiment 132 Phase 2: Hypothesis-Elimination on Capacitor Substrate with Planet

## Goal

Run a single instrumented experimental run on the capacitor substrate with a planet pattern and a test pattern, recording full substrate state per tick, and post-hoc apply multiple competing hypotheses (from RAW 132 §3) to test them simultaneously without re-running the experiment. Phase 2 is **not** a parameter-tuning exercise toward "drift appears" — it is a falsification round.

## What Phase 2 tests

Per RAW 132 §3.6, Phase 2 simultaneously tests:

| Hypothesis | What it predicts | Falsified if... |
|---|---|---|
| **H3.5** (adaptive thresholds + connectivity baseline) | threshold(r) profile around planet rises toward center, matching GR time-dilation factor 1/(1−2M/r) shape | threshold(r) is flat, or rises in wrong direction, or shape doesn't match GR family |
| **H4.1** (load-driven connector propagation) | load(r) profile around planet rises toward center, matching GR's g_rr stretching factor | load(r) is flat, or wrong direction, or wrong shape |
| **H5.1** (centroid of recent firings) | test pattern's reading-centroid shifts toward planet over many cycles ("drift") | reading-centroid stays stationary, or drifts away from planet |
| **H5.3** (threshold-elevation centroid) | test pattern's reading shifts in some direction (possibly different from H5.1) | reading stays stationary |
| **H5.4** (discharge-density-map peak) | similar to H5.1 but more robust | similar |
| **H5.5** (connectivity-of-firing centroid) | test pattern's reading shifts only if connected fired-cells form a coherent moving cluster | reading discontinuous |

**Provisional substrate commitments (from RAW 132 §3 and Phase 1 PASS):**
- §3.1: H1.1 — entity = cell sustained ≥50% threshold ≥1 tick
- §3.2: H2.1 — deterministic firing at threshold
- §3.3: H3.5 — adaptive thresholds with connectivity baseline ✓ Phase 1 confirmed
- §3.4: H4.1 — load-driven connector propagation
- §3.5: H5.1 primary; H5.3, H5.4, H5.5 post-hoc on same data

## What Phase 2 is NOT

- Not a test of drift mechanisms via rule extension (recruitment/dropout). Drift is *observer-side per RAW 132 §3.5*; no substrate-rule changes.
- Not a Schwarzschild-fitting exercise. Phase 2 measures shapes; quantitative GR-fit is Phase 3.
- Not a parameter-tuning toward desired outcome. The four §3.6 hypotheses (H3.5, H4.1, H5.1, plus the H5.x post-hoc panel) are tested as written.
- Not RGG. Phase 2 stays cubic (RAW 132 §7 recommendation).
- Not multi-planet mass-scaling. Single planet for Phase 2A; multi-planet is Phase 2B if Phase 2A produces interesting profiles.

## Background

### Phase 1 PASS

Exp 132 Phase 1 (2026-04-28) demonstrated that a K=4 capacitor cycle sustains for 5,000 cycles under the three-layer mechanism in vacuum. Working parameters (deposit_amount=50, adaptation_rate=0.1, relaxation_rate=0.05) have predictable structure: cycle-ignition floor `deposit ≥ K × bootstrap_charge_step × baseline` and steady-state stability `adapt ≈ (K−2) × relax`. This validated H3.5 (B+C combined) at the substrate-vacuum level. Phase 1 also kept `load_coefficient = 0` — connector mechanism implemented but not exercised.

### What Phase 2 changes

Three structural changes from Phase 1:

1. **Full lattice connectivity.** Phase 1 wired connectors only along the K=4 cycle (4 connectors total). Phase 2 wires connectors between every pair of face-adjacent cells in a bounded substrate region, so deposits can flow between patterns through the substrate.
2. **Two patterns: planet and test.** Phase 1 had one K=4 pattern. Phase 2 has two: a planet (K=4 cycle at fixed position) and a test (K=4 cycle at distance r ≥ 3 cells away, far enough not to merge into one connected component at bootstrap).
3. **`load_coefficient > 0`.** The connector load mechanism is now exercised. Provisional: `load_coefficient = 0.1`. Phase 2 may need to tune this; if cycles destabilize, lower it.

### The §3.6 single-run-multiple-readings design

Per RAW 132 §3.6: Phase 2 is **one experimental run** with full state recording, then **multiple post-hoc analyses** applying different reading functions and profile measurements to the same recorded data. This is the core scientific-elimination discipline — every hypothesis we want to test gets distinguished from the same data, no re-runs.

## Substrate setup

### Bounded cubic lattice

Cubic lattice in a bounded region: e.g., 11×11×3 cells (242 cells in z = 0, ±1, ±2 layers... wait, simplified to 21×21×3 for clearer radial profiles). All face-adjacent cell pairs in this region get a connector at initialization. Connectors uniform; only their load varies dynamically.

**Substrate dimensions:** 21 × 21 × 3 (cells x by y by z). 1323 cells total. Center of mass at (10, 10, 1). Plenty of room for measuring radial profiles out to r ≈ 8 cells from planet.

**Why bounded:** unbounded substrate would mean infinite cells with infinite connectors. Bounded gives a finite simulation. Boundary cells have fewer face-neighbors (5 or fewer), which means lower baseline threshold under H3.2 (connectivity-baseline). This is acceptable; it's the same boundary effect Phase 1 already accommodated.

### Planet pattern

K=4 cycle at fixed position in the lattice center plane (z=1):

```
Planet cycle: (10, 10, 1) → (11, 10, 1) → (11, 11, 1) → (10, 11, 1) → back
```

Bootstrap with same staggered initial charges as Phase 1 (1.00, 0.75, 0.50, 0.25 of baseline_threshold).

Planet sits at center of measurement region. Its firing produces deposits that propagate through the substrate.

### Test pattern

K=4 cycle at offset 5 cells in +x from planet (still in z=1 plane):

```
Test cycle: (15, 10, 1) → (16, 10, 1) → (16, 11, 1) → (15, 11, 1) → back
```

Bootstrap with same staggered initial charges.

Test pattern's nearest cell (15, 10, 1) is at Manhattan distance 4 from planet's nearest cell (11, 10, 1), separated by 3 empty cells. The planet's cycle and the test's cycle do not share connected substrate components at bootstrap.

### Connectors

Every pair of face-adjacent cells in the 21×21×3 region has a Connector. Total: ~3 × (21×20×3 + 21×3 + 21×20×3 + ...) ≈ a few thousand connectors. (Implementation will compute the exact count.)

In vacuum, only cycle-cell connectors carry deposits (planet emits deposits to its 4 cycle-neighbors; non-cycle-neighbor connectors stay at load=0). But the cycle cells ALSO have non-cycle face-neighbors. The planet's firing emits deposits to ALL face-adjacent cells, not just cycle-neighbors. So:

- A planet cell at (10, 10, 1) has face-neighbors:
  - (11, 10, 1) — planet cycle-next
  - (9, 10, 1) — substrate
  - (10, 11, 1) — planet cycle-prev
  - (10, 9, 1) — substrate
  - (10, 10, 2) — substrate
  - (10, 10, 0) — substrate
- When this cell fires, it emits deposits to ALL six. Two go to cycle-neighbors (sustaining the cycle); four leak into the substrate.
- Substrate cells that receive deposits accumulate charge. If they cross threshold (which requires sustained input), they fire too — but this should be rare with appropriate parameter tuning.

This is the structural change that makes Phase 2 different from Phase 1: deposits propagate through the substrate, creating a "halo" of charged-but-not-firing cells around each pattern. The halo's strength and shape is what Phase 2 measures.

## Three-layer mechanism (Phase 2 active)

All three layers exercised:

| Layer | Phase 1 | Phase 2 |
|---|---|---|
| Charging phase | Active in cycle cells; non-cycle cells stay at 0 | Active in cycle cells AND non-cycle cells receiving leakage deposits (halo) |
| Adaptive threshold | Active for cycle cells; their thresholds rise to ~100.1 | Active everywhere; cycle cells rise; halo cells with sustained input also rise |
| Connector load | Mechanism implemented; coefficient=0 means no propagation effect | `load_coefficient = 0.1` (tunable); connectors near patterns develop loads; propagation slows in dense regions |

## Per-tick procedure (extended from Phase 1)

Same 5 steps as Phase 1 (§"Three-Layer Mechanism" in Phase 1 spec), plus instrumentation:

```
For each tick:

  1. Threshold relaxation (Phase 1 unchanged)
  2. Connector propagation (Phase 1 unchanged, but now load_coefficient > 0)
  3. Charge accumulation at receivers (Phase 1 unchanged)
  4. Threshold check + firing (Phase 1 unchanged); RECORD all firing events to history
  5. State cleanup (Phase 1 unchanged)

  RECORD substrate snapshot (every N ticks, e.g. every 100):
    - threshold per cell
    - charge_level per cell
    - load per connector
```

Recording per-tick firing events is cheap (just append to a list). Recording full substrate snapshots is more expensive; do it every 100 ticks to keep memory bounded but still get good radial-profile data.

## Observer reading functions (§3.5 — applied post-hoc to recorded firings)

Five reading functions, applied to the recorded firing-event history per the §3.6 single-run-multiple-readings design:

- **R5.1 (provisional, primary):** `centroid_recent(N=4)` — geometric centroid of all cells that fired in the last N=K=4 ticks. Computed at every K-tick boundary throughout the run.
- **R5.3:** `centroid_threshold_elevated(window)` — geometric centroid of all cells whose threshold has risen above baseline by ≥ X% during a recent window (e.g., last 100 ticks).
- **R5.4:** `peak_density_map(window, kernel)` — construct a 3D Gaussian-weighted density map of recent firing events; the entity's "position" is the peak. Window: last 100 ticks; kernel σ = 2 cells.
- **R5.5:** `centroid_connected_firing(N=4)` — geometric centroid of the largest connected component of cells that fired in last N ticks (face-adjacent forming a cluster).

R5.6 (Bayesian) is deferred — too much extra machinery for Phase 2.

Each reading function is computed for both the planet and the test pattern at every K-tick boundary, producing trajectory data.

## Phase 2 success criteria (per hypothesis)

Each hypothesis has its own success criterion; Phase 2 passes ALL OF THEM, NONE OF THEM, or some subset, and the result is reported per-hypothesis.

### H3.5 — adaptive threshold profile

> The threshold profile threshold(r) measured at the end of the run, where r is distance from planet centroid, should be **monotonically decreasing** with r and should level off at baseline (100.0) at large r.

Computed by: averaging final threshold values over cells at each distance r from planet centroid. Plot threshold(r) vs r; check monotonicity and level-off.

**Falsified if:** profile is flat (threshold uniform), or rises with r (anti-gravity), or non-monotonic.

### H4.1 — load profile

> The connector load profile load(r) measured at the end of the run, where r is distance from planet centroid (averaged over connectors with that distance), should be **monotonically decreasing** with r and should approach zero at large r.

Computed by: averaging final load values over connectors at distance r. Plot load(r) vs r; check monotonicity.

**Falsified if:** profile is flat (load uniform across substrate), or rises with r, or non-monotonic.

### H5.1 — primary reading function

> The test pattern's reading-centroid trajectory under R5.1 should drift **toward the planet** (centroid x-coordinate decreases from initial 15.5 toward planet's 10.5) over the 5,000 cycles. The drift may be small but must be statistically distinguishable from zero.

Computed by: linear regression of test centroid x-coordinate vs cycle number. Slope < 0 with sufficient confidence.

**Falsified if:** slope = 0 (no drift), slope > 0 (drift away from planet), or trajectory chaotic (regression doesn't fit).

### H5.3, H5.4, H5.5 — alternative reading functions

> Each alternative reading function applied to the same recorded data should yield a trajectory. Phase 2 reports the trajectories side-by-side without claiming any one is "correct" — the comparison itself is informative.

**Falsified if:** any of them produces undefined trajectories (e.g., R5.5 if the firing pattern never forms a connected component).

## Falsification modes

- **No halo.** If non-cycle cells never charge above 50% of threshold and never fire, the halo is too weak to perturb the test pattern's environment. Tune `deposit_amount`, but with care — too high and runaway firing kills both patterns. If no parameter region produces both stable cycles AND a non-trivial halo, this is itself a falsification of the three-layer mechanism's ability to support gravitational coupling.
- **Cycle decoherence under load.** Setting `load_coefficient > 0` may destabilize the cycle. If the cycle dies under load_coefficient ≥ 0.01, H4.1's mechanism is real but its parameter space is incompatible with cycle sustainment, which is its own structural finding.
- **Cycle-merge.** Test pattern cycle and planet pattern cycle accidentally connect through halo firings, fusing into one component (Exp 134 Phase 2 contact-decoherence redux). If this happens, distance between patterns must be increased; alternatively, this finding tells us that any field-coupling automatically merges patterns and there's no way to have separate-but-interacting patterns at this scale.
- **All H5.x give identical trajectories.** Would mean reading-function choice doesn't matter for this regime — a slightly disappointing result that simplifies §3.5 by collapsing the hypotheses.

## Deliverables

```
experiments/132_grow_until_observed/
├── ... existing Phase 1 files ...
├── lattice.py            # Bounded cubic lattice helper (cell enumeration, full connector wiring)
├── observer.py           # R5.1/R5.3/R5.4/R5.5 reading functions
├── recording.py          # Substrate-state snapshots, firing-event log
├── profile.py            # threshold(r), load(r) post-hoc analysis
├── phase2_test.py        # The deliverable: full instrumented run + post-hoc analysis + per-hypothesis reporting
├── phase2_run.log        # Captured pytest output
└── RESULTS_phase2.md     # Per-hypothesis outcome table
```

## Implementation constraints

- Python 3, stdlib + dataclasses (matching Phase 1).
- No numpy at this scale — substrate is 1323 cells, run is 20,000 ticks; plain Python is fast enough.
- Recording: per-tick firing events, every-100-tick substrate snapshots. Memory budget: a few MB.
- Post-hoc analysis: separate from the run; takes recorded data and produces per-hypothesis tables/plots.
- Run length: 5,000 cycles (20,000 substrate ticks at K=4). Same as Phase 1.
- Wall-clock target: minutes, not hours. If too slow, reduce substrate to 11×11×3 (363 cells).

## Out of scope

- Phase 3: quantitative Schwarzschild-fitting, GR-shape recovery via χ² to 1/(1−2M/r), connection to Newton.
- Multi-planet mass scaling (Phase 2B if motivated).
- RGG substrate.
- H2.1 vs H2.2 (deterministic vs probabilistic firing) — both interesting but require different runs; Phase 2 stays H2.1.
- H4.4 (capacitor size as propagation modulator) — plausibly entangled with H3.5; deferred.
- H4.5 (refractory periods) — separate experiment.
- H5.6 (Bayesian inference reading) — too much machinery.
- Sign-blind matter/antimatter behavior on capacitor substrate.

## Risks and constraints

- **Halo strength is a new tuning dimension.** Phase 1 didn't have a halo; Phase 2 needs it to be present but not destabilizing. If the working region for "halo present + cycles stable + load coupling on" turns out narrow, Phase 2 becomes a tuning study before a falsification study. Document the search.
- **Reading-function choice affects what we see.** This is the §3.5 honest design — different observers see different drift trajectories. The post-hoc multi-reading panel is the answer to that, but if all readings agree, the §3.5 distinction collapses.
- **Bounded substrate has boundary effects.** Cells near the edge have fewer connectors (lower connectivity-baseline threshold). This may produce edge-firing artifacts that contaminate the radial profiles. Mitigation: measure profiles only out to r ≤ 7 (well inside the 11-cell radius from planet center).
- **Phase 2 may produce no clear signal.** If threshold(r) and load(r) are weak/flat and reading trajectories are noisy, Phase 2 falsifies the entire three-layer-grow-until-observed mechanism's ability to produce gravitational coupling. That is a strong-falsification result and should be reported honestly, not papered over by parameter search.

## Phase 3 sketch (if Phase 2 produces signal)

If Phase 2 shows clear threshold(r) and load(r) profiles plus reading-trajectory drift, Phase 3 quantitatively fits:
- threshold(r) to GR's time-dilation factor γ(r) and extracts an effective mass M.
- load(r) to GR's g_rr.
- Reading trajectory to Newton's inverse-square law (geodesic motion).

Phase 3 also extends to multi-planet (mass-scaling), RGG substrate, and possibly the matter-antimatter symmetry question.
