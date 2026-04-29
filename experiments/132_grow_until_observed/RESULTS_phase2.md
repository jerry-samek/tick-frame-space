# Experiment 132 Phase 2 — Results

**Status:** HONEST NEGATIVE — three of four hypotheses NOT SUPPORTED at this parameter set; one collapsed into agreement and is therefore inconclusive.
**Date run:** 2026-04-28
**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-phase2-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-grow-until-observed-phase2.md`
**Theory:** `docs/theory/raw/132_untested_capacitor.md` (RAW 132 §3.5, §3.6)

## Summary

Phase 2 instrumented run on a 21×21×3 cubic lattice with full face-adjacency
connectivity, planet K=4 + test K=4 patterns, 5000 cycles (20,000 ticks),
~7 minutes wall-clock. Phase 1's vacuum-coherence parameters were preserved
unchanged and `load_coefficient = 0.1` was activated. The two RAW 132 §3.6
provisional commitments under test (H3.5 monotonic threshold(r), H4.1
monotonic load(r)) **did not produce the predicted radial structure**. The
primary reading function (H5.1 centroid_recent) showed a +0.244 cell drift
in x — i.e. **away from** the planet — within the K-window centroid sampling
resolution (~0.5 cells), so it does not support drift toward the planet.
The alternative readings panel (H5.3/H5.4/H5.5) collapsed onto H5.1 within
0.05 cells, leaving the §3.5 reading-function distinction unresolved for
this scenario rather than supported.

This is a real falsification result for the simplest implementation of the
RAW 132 capacitor model. The reframe itself (capacitor model untested) is
not refuted — what was tested is one concrete instantiation of it, which
fails to produce gravitational drift at this scale and parameter set.

## Working parameters (Phase 2)

| Parameter | Phase 1 value | Phase 2 value | Notes |
|---|---|---|---|
| baseline_threshold | 100.0 | 100.0 | unchanged |
| adaptation_rate | 0.1 | 0.1 | unchanged |
| relaxation_rate | 0.05 | 0.05 | unchanged |
| deposit_amount | 50.0 | 50.0 | unchanged |
| load_coefficient | 0.0 | **0.1** | activated for Phase 2; not tuned |
| propagation_time_base | 1.0 | 1.0 | unchanged |
| bootstrap_charge_step | 0.25 | 0.25 | unchanged |

No tuning was performed inside Phase 2. The substrate inherited Phase 1's
working region and added `load_coefficient = 0.1` per spec.

## Per-hypothesis result table

| Hypothesis | Status | Evidence |
|---|---|---|
| H3.5 (threshold(r) monotonically decreasing around planet) | **FALSIFIED at this parameter set** | Profile non-monotonic; hump at r=8 (threshold = 168.3 vs 151.6 at r=0) |
| H4.1 (load(r) monotonically decreasing around planet) | **FALSIFIED at this parameter set** | Profile essentially flat at ~1.3 across all r; no detectable radial structure |
| H5.1 (test pattern drifts toward planet) | **NOT SUPPORTED** | Drift +0.244 in x (away from planet at x=10.5); magnitude within sampling noise of K-window centroid |
| H5.3 / H5.4 / H5.5 (alternative readings differ from H5.1) | **COLLAPSED — INCONCLUSIVE** | All three readings agree with H5.1 within 0.05 cells for this symmetric, stable test pattern |

## Per-hypothesis detail

### H3.5 — adaptive threshold profile

Cells binned by integer Manhattan-equivalent distance from planet centroid
`(10.5, 10.5, 1.0)`:

```
r=0:  151.59
r=1:  151.57
r=2:  157.17
r=3:  160.38
r=4:  157.02
r=5:  156.87
r=6:  158.17
r=7:  161.24
r=8:  168.30   ← peak (away from the planet)
r=9:  165.58
r=10: 163.87
r=11: 162.80
```

- Profile shape: **non-monotonic** — hump near r=8.
- threshold(0) = 151.59; threshold(7) = 161.24; threshold(8) = 168.30.
- Monotonically decreasing? **No.**
- **Result:** FALSIFIED at this parameter set.

The r=5–8 region samples both the planet's halo and the test pattern's
halo (the test pattern is centered at r=5 from the planet). The hump at
r=8 is consistent with the test-pattern halo dominating that band; this
contaminates the planet-only signal.

### H4.1 — connector load profile

Connectors binned by integer distance from planet centroid:

```
r=0:  1.33
r=1:  1.44
r=2:  1.25
r=3:  1.42
r=4:  1.27
r=5:  1.32
r=6:  1.34
r=7:  1.32
r=8:  1.35
r=9:  1.32
r=10: 1.35
r=11: 1.32
```

- Profile shape: **flat (≈1.3 everywhere)** — bin-to-bin variation ~0.1–0.2.
- load(0) = 1.33; load(7) = 1.32.
- Monotonically decreasing? **No.**
- **Result:** FALSIFIED at this parameter set.

With `load_coefficient = 0.1` and full lattice connectivity, deposits flow
to all available edges and load saturates uniformly. Either the coefficient
is too weak to set up a gradient before equilibrium, or load equilibrates
faster than any radial structure can develop on this substrate size.

### H5.1 — primary reading function (centroid_recent, K-window = 4)

```
First 3 samples (around tick 404):
  tick=404, centroid=(15.214286, 10.5, 1.0)
  tick=408, centroid=(15.214286, 10.5, 1.0)
  tick=412, centroid=(15.214286, 10.5, 1.0)

Last 3 samples (around tick 20400):
  tick=20392, centroid=(15.541667, 10.5, 1.0)
  tick=20396, centroid=(15.500000, 10.5, 1.0)
  tick=20400, centroid=(15.458333, 10.5, 1.0)
```

- Drift in x: **+0.244** (positive = away from planet at x=10.5).
- Magnitude is within the K-window centroid resolution (~0.5 cells; the
  centroid averages 4 cells fired in the last K=4 ticks).
- **Result:** NOT SUPPORTED. The sign is wrong (away, not toward) and
  the magnitude is at-or-below sampling noise.

### H5.3, H5.4, H5.5 — alternative readings panel

Final-tick readings (tick=20400):

- H5.3 centroid_threshold_elevated: `(15.500, 10.5, 1.0)`
- H5.4 peak_density_map:           `(15.458, 10.5, 1.0)`
- H5.5 centroid_connected_firing:  `(15.500, 10.5, 1.0)`

All three agree with H5.1 (`15.458`) within **0.05 cells**.

The §3.5 reading-function distinction (R5.1 vs the alternatives) **collapsed
for this scenario**: a symmetric, stable, K=4 test pattern firing in a
fixed cycle produces nearly identical centroids regardless of which
reading function is applied. This does not support H5.3/H5.4/H5.5; it
shows the panel cannot distinguish observers in this regime, and the
distinction may still matter for asymmetric or transient patterns.

## Phase 1 still passes

Phase 1's 5000-cycle vacuum-sustainment deliverable continues to pass in
0.12 s, confirming the `tick.py` cell-to-connectors index optimization
(introduced for Phase 2 performance) is faithful to Phase 1 semantics.

## Total tests: 50 passing

48 unit tests + 1 Phase 1 deliverable + 1 Phase 2 deliverable.

## Per-hypothesis falsification table (cumulative across experiments)

| Hypothesis | Status | Evidence |
|---|---|---|
| H3.5 (threshold(r) monotonic) | **partially falsified** | Phase 1 vacuum coherence works; Phase 2 monotonic profile does not appear at this scale (test pattern contamination is a confound) |
| H4.1 (load(r) monotonic) | **falsified at these parameters** | Phase 2 load profile flat ~1.3; either coefficient too weak or equilibration too fast |
| H5.1 (drift toward planet) | **not supported** | Phase 2 drift +0.244 (away) within sampling noise |
| H5.2 (charge-weighted) | falsified by RAW 127 | Theoretical (charging is structurally invisible) |
| H5.3 / H5.4 / H5.5 | **inconclusive (collapsed)** | All readings agree within 0.05 cells for this scenario |

## Key honest observations

1. **The test pattern is itself a confound for measuring the planet's
   profile.** The r=5–8 region samples the test pattern's halo, which
   contaminates the planet-only signal. The cleanest planet profile would
   come from a planet-only run (no test pattern). The current Phase 2
   measures the *combined* field of two coexisting patterns.

2. **`load_coefficient = 0.1` may be too weak, or load may equilibrate
   too fast.** With full lattice connectivity, deposits flow everywhere
   and load saturates uniformly. A larger coefficient might create a
   visible gradient before equilibrium — at the cost of cycle stability.

3. **The 21×21×3 substrate may be too small.** Patterns are 5 cells apart
   and K=4 means propagation reaches ~4 cells per cycle. The two patterns
   are effectively "in halo contact" even though their cycles do not
   merge. A larger lattice would give the field room to develop.

4. **Reading-function collapse is not surprising for symmetric, stable
   patterns.** The §3.5 distinction (different observers see different
   trajectories) may still matter for asymmetric or transient patterns,
   but cannot be tested with the current symmetric K=4 fixture.

## What this proves

- The Phase 2 setup as designed (21×21×3 lattice, full connectivity,
  K=4 planet + K=4 test at distance 5, `load_coefficient = 0.1`) **does
  not produce gravity-like coupling** between the two patterns.
- This is a real falsification result for the simplest implementation
  of the RAW 132 three-layer mechanism. The provisional commitments H3.5
  and H4.1 do not hold at this parameter set; H5.1 does not produce drift
  toward the planet.

## What this does NOT prove

- **Not** that the three-layer mechanism categorically fails at gravitational
  coupling. It might work at different parameters, on a larger substrate,
  or under partial-connectivity wiring.
- **Not** that RAW 132's reframe was wrong. The reframe (capacitor model
  untested) still holds. What has now been tested is the *simplest*
  capacitor implementation, which fails to produce drift in this scenario.
- **Not** that drift is impossible. Drift may need different reading
  functions, asymmetric setups, longer runs, or a different substrate
  geometry.

## Anomalies / surprises

- **The threshold hump at r=8** is the clearest non-trivial structure in
  the data. Its position coincides with the test pattern's halo extent,
  which suggests the threshold(r) measurement is reading both patterns'
  combined adaptation rather than the planet alone. This is a methodology
  finding — Phase 2A.1 (planet-only measurement) is the right next step.
- **Reading-function collapse** within 0.05 cells. Given the symmetric
  stable pattern, this is consistent with theory but means the H5.x panel
  cannot be distinguished here.
- **Drift sign is positive (away from planet).** Magnitude is within
  noise, so this is consistent with no-drift, but it is worth noting that
  no run direction was ever toward the planet — the centroid samples
  oscillate around 15.46 with no detectable bias toward x=10.5.

## Next steps proposal — Phase 2A (signal isolation before Phase 3)

Phase 3 (quantitative GR fit) is gated on Phase 2 producing meaningful
signal, which it did not. Recommended Phase 2A subphases before
returning to Phase 3:

- **Phase 2A.1: planet-only profile measurement.** Remove the test
  pattern, run the planet alone, measure threshold(r) and load(r) profiles.
  Isolates the planet's gravitational signature without test-pattern
  contamination. Cheapest experiment; should run first.

- **Phase 2A.2: load_coefficient sweep.** Try 0.5, 1.0, 5.0 (cycle
  stability permitting). See if load profile develops radial structure
  at higher coefficient.

- **Phase 2A.3: substrate scale.** Try 41×41×3 or larger. Measure
  profiles. See if a larger lattice allows a gradient to develop before
  patterns enter mutual halo contact.

- **Phase 2A.4: partial connectivity.** Wire only "patterns + cycle"
  connectors initially, let halo emerge from there rather than starting
  from full face-adjacency. Tests whether full connectivity is itself
  what flattens the load profile.

- **Phase 3 deferred** until Phase 2A produces a meaningful signal in
  at least one of {threshold(r), load(r), drift}.
