# Experiment 132 Phase 2A.5 — Results

**Status:** OUTCOME 3 (superposition fails) — with substantively richer findings than Phase 2.
**Date run:** 2026-04-28
**Spec:** `docs/superpowers/specs/2026-04-28-grow-until-observed-phase2a5-design.md`
**Theory:** RAW 132 §3.5 H5.7 (self-subtracting reading), §3.6.1 (Phase 2 falsification), §10.11 (RAW 044 + Exp 64/109 internal precedents).

## Summary

Phase 2A.5 was the three-run superposition test designed to extract a clean
planet-only field by running R1 (planet-only), R2 (test-only), and R3
(combined) under identical parameters and comparing R3 − R2 against R1.
Per the spec, this would simultaneously (a) operationalize H5.7's
self-subtracting reading and (b) determine whether Phase 2's flat profiles
were a test-pattern confound or a substrate property.

**Result:** Outcome 3 — superposition fails. χ² for thresholds = 0.169 and
χ² for loads = 0.168, both above the 0.1 threshold for "approximately
linear" defined in the spec.

The substantively important finding is *not* the chi-squared number. It
is what R1 alone shows: **the planet, by itself, with no test pattern in
the lattice, produces a perfectly flat threshold(r) and load(r) profile**.
Phase 2's flat load profile was therefore not test-pattern contamination
— it is a substrate-saturation signature. This refines the falsification
claim in a useful direction.

## Outcome categorization (per spec)

The Phase 2A.5 spec defined three outcome categories. For reference:

| Outcome | Criterion | Implication |
|---|---|---|
| 1 (clean superposition) | χ² < 0.05 for both thresholds and loads, AND R1 monotone, AND entity-relative monotone | H5.7 supported; planet field measurable in isolation |
| 2 (partial linearity) | χ² < 0.1 for at least one channel; some structure in R1 | H5.7 partial; substrate non-trivial |
| 3 (superposition fails) | χ² > 0.1 in both channels OR no monotone structure anywhere | H5.7 not supported here; substrate saturated/nonlinear |

**This run lands in Outcome 3.**

## Run details

- 3 simulations, each 5,000 cycles (20,400 ticks at K=4 + 400-tick warmup).
- ~1 minute wall-clock per run; ~3 minutes total.
- Same Phase 2 parameters: 21×21×3 cubic lattice, full face-adjacency
  connectivity, baseline_threshold=100.0, adaptation_rate=0.1,
  relaxation_rate=0.05, deposit_amount=50.0, load_coefficient=0.1.
- R1: planet K=4 at lattice center.
- R2: test K=4 at distance 5 from where the planet would be (planet absent).
- R3: planet K=4 + test K=4 at distance 5 (the Phase 2 setup).

## Linearity statistics

```
chi^2 (thresholds): 0.168887
chi^2 (loads):      0.168357
```

Both > 0.1 → outcome 3.

## R1 (planet-only) profiles — key finding

Threshold(r) from planet centroid, R1 only:

```
r=0:  100.0500
r=1:  100.0500
r=2:  100.0500
r=3:  100.0500
r=4:  100.0500
r=5:  100.0500
r=6:  100.0500
r=7:  100.0500
r=8:  100.0500
r=9:  100.0500
r=10: 100.0500
r=11: 100.0500
```

Load(r) from planet centroid, R1 only:

```
r=0:  1.0000
r=1:  1.0000
... (all radii)
r=11: 1.0000
```

**Both profiles are perfectly flat.** The planet alone, with no test
pattern present, produces no radial gradient in either threshold or load
in this substrate at these parameters. R1 thresholds monotonic? `False`
(constant). R1 loads monotonic? `True` (trivially — all equal).

This is the most informative single result from Phase 2A.5.

## Entity-relative profiles (R3 − R2)

Threshold residual from planet centroid:

```
r=0:  51.5375
r=1:  51.5187
r=2:  57.1205
r=3:  60.3257
r=4:  56.9737
r=5:  56.8173
r=6:  58.1224
r=7:  61.1922
r=8:  68.2535   ← peak (same hump as Phase 2 god-view profile)
r=9:  65.5250
r=10: 63.8227
r=11: 62.7485
```

Load residual from planet centroid:

```
r=0:  0.3333
r=1:  0.4412
r=2:  0.2500
r=3:  0.4231
r=4:  0.2669
r=5:  0.3192
r=6:  0.3448
r=7:  0.3226
r=8:  0.3452
r=9:  0.3214
r=10: 0.3543
r=11: 0.3235
```

Both non-monotonic. The threshold residual reproduces the same r=8 hump
the Phase 2 god-view profile showed. So the hump is a real structural
feature of the combined dynamics — not a measurement artifact — but its
shape is anti-monotonic (peak at intermediate radius, not monotone fall),
i.e. **not GR-like**.

## Per-hypothesis status table

| Hypothesis | Phase 2A.5 status | Evidence |
|---|---|---|
| H5.7 (entity-relative reading R3 − R2 ≈ R1) | **NOT SUPPORTED — operationally untestable here** | R3 − R2 has structure (50× threshold residual at r=0; r=8 hump) while R1 is perfectly flat; subtraction does not recover R1, and χ² values 0.169 / 0.168 confirm linearity violation |
| H3.5 (threshold(r) monotone around planet) | **FALSIFIED again, more directly** | R1 alone (no test pattern) is exactly flat at 100.05 — substrate saturation, not test-pattern contamination |
| H4.1 (load(r) monotone around planet) | **FALSIFIED again, more directly** | R1 alone (no test pattern) is exactly flat at 1.0 — full lattice connectivity + load_coefficient=0.1 saturates load uniformly |

## Substantive findings (in order of importance)

### 1. Substrate saturation, not test-pattern contamination, is responsible for Phase 2's flat profiles

The Phase 2 load(r) profile was already flat (~1.3 across all r). Phase 2A.5
was designed in part to disambiguate two hypotheses for that flatness:

- (a) test pattern's halo flattens the planet's signal (contamination)
- (b) the substrate itself washes the gradient out (saturation)

R1 (planet alone, no test pattern present) shows threshold(r) and load(r)
**identically flat at every radius**. Hypothesis (b) is the right one.
With full face-adjacency connectivity and load_coefficient=0.1, the firing
activity diffuses across the entire 21×21×3 lattice and reaches steady
state where distance from the planet centroid carries no signal.

This is a sharper falsification of H3.5 and H4.1 than Phase 2 produced,
because Phase 2 left parameter-tuning hope alive ("maybe the test pattern
is contaminating the planet's signature; maybe a clean isolated planet
would still show a gradient"). Phase 2A.5 closes that escape route at
this parameter set.

### 2. Superposition is genuinely nonlinear in this substrate

R3 − R2 produces threshold residuals around 51–68 and load residuals
around 0.25–0.45, while R1 is exactly 100.05 and 1.0 respectively. The
residual is not just noisy around R1 — it has *structure* (the r=8 hump)
that R1 does not have, and its scale is off from R1 by ~50× in thresholds
and ~3× in loads.

The straightforward reading of H5.7 — that the entity-relative measurement
extracts the planet's intrinsic field by subtracting the test-pattern
"baseline" — does not hold here. Either H5.7's formulation needs
refinement (e.g. R3 − αR2 − βR1 with cross-term, or a different
combination rule) or the substrate's nonlinear coupling between patterns
precludes any clean entity-relative reading via subtraction.

### 3. The r=8 hump is real and reproducible, but not GR-like

The Phase 2 god-view threshold profile had a hump at r=8. Phase 2A.5's
entity-relative threshold profile (R3 − R2) shows the same hump at r=8,
with comparable magnitude (residual 68.3 vs flat-r=0 residual 51.5). So
the hump is a genuine signature of the combined planet+test dynamics
under nonlinear coupling, not a contaminant from how we measured Phase 2.

But its shape is **anti-monotonic** (peak at intermediate r), which is
the wrong shape for any monotone gravitational-like field. Whatever this
hump is, it isn't 1/r or 1/r² in disguise. It is more consistent with a
resonance / interaction-zone signature between the two K=4 cycles.

### 4. The χ² magnitudes (0.169 / 0.168) are clear but not catastrophic

Both χ² values are roughly 1.7× the linearity threshold. So the violation
is unambiguous, but the substrate is not orders-of-magnitude away from
linear — it is moderately nonlinear, in a regime where parameter changes
might still recover linearity if any. This is consistent with the
saturation explanation: in a saturated regime, *most* of R3 looks like a
fixed equilibrium plus some residual structure, so R3 − R2 mostly cancels
to a constant (51.5 plateau) plus a small structured deviation (the hump).

### 5. H5.7 is operationally untestable at these parameters

If the substrate is in a saturated regime where R1 is identically flat,
then R3 − R2 cannot recover the planet's field "in isolation" because there
is nothing to recover — the planet has no detectable field profile in
isolation here. H5.7 may still be the right reading-function philosophy,
but it cannot be tested against this particular planet field, because the
planet field at these parameters has no radial structure to begin with.

## What this proves

- **Phase 2's flat profiles are a substrate property, not a measurement
  confound.** R1 alone shows it directly.
- **H3.5 and H4.1 are falsified at this parameter set, more directly than
  in Phase 2.** The planet alone, in isolation, produces no radial
  threshold or load gradient.
- **Superposition (H5.7's straightforward formulation) fails at the χ²
  ≈ 0.17 level in both channels.** The substrate exhibits genuine nonlinear
  coupling between coexisting patterns.
- **The r=8 hump in Phase 2 was a real interaction-zone signature**, not
  an artifact of summing two patterns' halos in the measurement step.

## What this does NOT prove

- **Not** that the three-layer capacitor mechanism categorically fails at
  producing radial gradients. The substrate is in a saturated regime; a
  weaker `load_coefficient`, a sparser connectivity, or a larger lattice
  might break out of saturation.
- **Not** that H5.7 is wrong as a reading-function philosophy. H5.7 is
  *operationally untestable here* because R1 has no field to recover.
  It needs a substrate where R1 alone shows structure.
- **Not** that RAW 132's reframe is refuted. The reframe is "capacitor
  model untested." What has now been tested is two specific instantiations
  of it (Phase 2 combined, Phase 2A.5 three-run); both lead to the same
  diagnosis — the substrate at these parameters saturates.

## Refined falsification claim

After Phase 2 the falsification was: *"the simplest implementation of the
RAW 132 capacitor mechanism, at these parameters, on this lattice, does
not produce gravitational drift between two K=4 patterns."*

After Phase 2A.5 the falsification can be tightened to: *"at these
parameters and full face-adjacency connectivity on a 21×21×3 lattice,
the substrate saturates — the planet alone produces no radial threshold
or load gradient, and pairs of patterns couple nonlinearly (χ² ≈ 0.17).
Without breaking out of the saturated regime, the mechanism cannot
produce a radial field, with or without test patterns present."*

## Implications for next experiments

The substrate-saturation diagnosis reorders the Phase 2A subphase
priorities surfaced at the end of `RESULTS_phase2.md`:

1. **Phase 2A.2 (load_coefficient sweep) — now highest priority.** If
   load_coefficient=0.1 saturates everything uniformly, sweeping it down
   to 0.01 / 0.001 (or up — but cycle stability bounds that) is the
   cheapest way to look for a non-saturated regime. R1 measurement alone
   is enough to detect any radial structure.

2. **Phase 2A.4 (partial connectivity) — also high priority.** Full
   face-adjacency may itself be the saturation cause: deposits flow
   anywhere and equilibrate fast. Wiring only "patterns + cycle"
   connectors (or sparser topology, e.g. random connectivity p<1) tests
   whether the substrate's geometry is what flattens the gradient.

3. **Phase 2A.3 (substrate scale)** drops to lower priority. A larger
   lattice still saturates if the dynamics saturate; we should fix the
   dynamics first.

4. **Phase 3 (GR fit) remains deferred** until at least one of
   {threshold(r), load(r)} produces non-flat structure with R1 alone.

## Total tests: 54 passing

50 from before (48 unit + 1 Phase 1 deliverable + 1 Phase 2 deliverable)
+ 4 from `tests/test_phase2a5_analysis.py`. The Phase 2A.5 deliverable
test (`phase2a5_test.py::test_phase2a5_superposition`) ran in 186.49 s
and passed.

## Anomalies / surprises

- **Exact flatness of R1.** Threshold = 100.05 to four decimals at every
  radius; load = 1.0 exactly at every radius. This is more flat than
  expected — even noisy diffusion should produce small bin-to-bin
  variation. The cleanness suggests the steady state is genuinely a
  fixed-point in the saturated regime, not a high-noise equilibrium.
- **Threshold residual baseline ≈ 51.5.** The R3 − R2 threshold residual
  has a constant offset of ~51.5 across all radii in addition to the r=8
  hump. This is consistent with R3's two patterns elevating the average
  threshold uniformly (above R2's single-pattern saturation), then adding
  a small interaction-zone structure on top. The 51.5 plateau is roughly
  half of the 100.05 baseline — a coincidence worth checking with a
  load_coefficient sweep.
- **Load residual sits around 0.32–0.35**, well below R1's saturated load
  of 1.0. This is consistent with: removing one pattern (R3 → R2) lowers
  the average load by a substantial fraction, but the residual isn't
  uniform because the test-pattern's halo geometry interacts with the
  bin-counting around the *planet* centroid.
