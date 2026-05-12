---
title: Grow Until Observed — Phase 1 (Experiment 132)
date: 2026-04-28
status: spec — pending Phase 1 implementation
theory: docs/theory/raw/132_untested_capacitor.md (RAW 132)
predecessor experiments: 131_a (lineage falsified), 131_b (anisotropic connectors partial), 133 (closed-loop falsified), 134 (CA renewal: vacuum coherent, no field-at-distance)
---

# Experiment 132 Phase 1: Capacitor Substrate Vacuum Self-Coherence

## Goal

Test whether a single K=4 renewal pattern can be sustained as a stable
firing cycle under the three-layer "grow until observed" mechanism
(RAW 132 §5) on a cubic lattice substrate, in vacuum (no other patterns
present).

This is the smallest non-trivial test of RAW 132's reframe: **the four
prior experiments (131_a, 131_b, 133, 134) each dropped half of the
capacitor model; Phase 1 tests whether implementing all three layers
together — charging phase, adaptive threshold, connector load — can
produce sustained pattern coherence in vacuum.**

## What Phase 1 is NOT

- Not a test of drift or gravity-at-a-distance (Phase 2).
- Not a test of GR metric reproduction (Phase 3).
- Not a test on RGG (Phase 1 uses cubic for debugging clarity; RGG follows).
- Not a test of matter/antimatter symmetry (capacitor sign-handling is
  a separate design question; Phase 1 uses positive matter only).
- Not a search for an "exact fixed point" in Exp 134's bit-identity sense
  — capacitor dynamics are *adaptive by design*, so the equivalent of
  fixed-point invariance is **cycle-structure invariance** (see §5).

## Background

### Why this experiment exists

RAW 132 (2026-04-28) reframed the four-experiment triangulation arc
(131_a/131_b/133/134) as evidence not of a "discrete-substrate limit"
but of "four simplifications of an unimplemented capacitor model." Each
prior experiment implemented at most two of the three substrate layers
specified in RAW 126/127 + RAW 132 §3.3, §3.4:

| Exp | Implemented | Dropped |
|---|---|---|
| 131_a | Lineage tree + integer flow | No charging, no discharge |
| 131_b | Anisotropic-RGG + propagation | No discrete discharge events |
| 133 | Integer hold-and-fire | No continuous charging *between* fires |
| 134 | Integer paint + decay + threshold | No real charging — paint instantaneous |

This experiment implements all three layers together for the first time.

### What "all three layers" means operationally

Per RAW 132 §5:

| Layer | What grows during charging | What happens at discharge |
|---|---|---|
| **Charging phase** (RAW 127) | Real charge level, 0 → threshold | Resets to 0; emits deposits to all connectors |
| **Adaptive threshold** (§3.3) | Threshold value, slowly rises with firing history | Each discharge raises threshold by adaptation amount |
| **Connector load** (§3.4) | Deposits in transit on each edge | Discharge releases deposits into connectors; load increases |

In vacuum, all three values settle at steady-state values that depend
on the firing rate of the test pattern's cycle.

## Substrate

### Cubic lattice

3D cubic lattice. Each cell has up to 6 face-adjacent neighbors. Phase 1
uses a small bounded region (e.g., 10×10×10 cells, with the test pattern
in the z=0 plane near origin). Boundary cells have fewer than 6
neighbors — this is the substrate's structural inhomogeneity baseline.

### Cell datatype

Each cell carries:

```python
@dataclass
class Cell:
    charge_level: float        # current charge, 0 ≤ charge ≤ threshold
    threshold: float           # current threshold (adaptive)
    last_discharge_tick: int   # tick of most recent discharge (-1 if never fired)
    state: CellState           # Empty | Charging | Discharged (Discharged is 1-tick transient)
```

Cells with `state = Empty` and `charge_level = 0` are non-pattern background.
They exist on the substrate but never fire unless deposits arrive.

### Connector datatype

Each connector (edge between face-adjacent cells) carries:

```python
@dataclass
class Connector:
    current_load: int          # count of deposits currently in transit
    in_transit: list[Deposit]  # each deposit has a remaining_propagation_time
```

Connectors are **uniform by construction** — same base propagation time for
all. Their *current state* (load) modulates propagation per RAW 132 §3.4.

## Three-Layer Mechanism (Operational)

### Per-tick procedure

```
For each tick:

  1. Threshold relaxation:
       For each cell where last_discharge_tick < current_tick - 1:
         threshold = max(baseline, threshold - relaxation_rate)

  2. Connector propagation:
       For each connector:
         For each deposit in transit:
           propagation_time_remaining -= 1 / (1 + load_coefficient × current_load)
           If propagation_time_remaining ≤ 0:
             Move deposit from connector to destination cell
             current_load -= 1

  3. Charge accumulation:
       For each cell receiving deposits this tick:
         charge_level += deposit_amount × num_arriving_deposits

  4. Threshold check (firing):
       For each cell where charge_level ≥ threshold:
         state = Discharged (transient)
         charge_level = 0
         threshold += adaptation_rate
         last_discharge_tick = current_tick
         Emit deposits to all connected neighbors
           (each gets one deposit on its connector with full propagation_time_base)

  5. State cleanup:
       For each cell where state = Discharged:
         state = Empty (back to ground state, ready to charge again)
```

### Initial bootstrap

To start the K=4 cycle, seed the four cells with staggered initial charges:

| Cell | Initial charge (fraction of baseline_threshold) |
|---|---|
| C0 = (0,0,0) | 1.00 (about to fire on tick 1) |
| C1 = (1,0,0) | 0.75 (will fire ~1 tick after C0) |
| C2 = (1,1,0) | 0.50 (will fire ~1 tick after C1) |
| C3 = (0,1,0) | 0.25 (will fire ~1 tick after C2) |

After bootstrap, the system runs autonomously. Charges accumulate from
deposits emitted by neighboring cells' discharges; thresholds adapt;
connector loads equilibrate.

## Pattern Fixture: K=4 Capacitor Cycle

Same geometry as Exp 134's F1 fixture (2×2 square at z=0): C0=(0,0,0),
C1=(1,0,0), C2=(1,1,0), C3=(0,1,0). Cycle order: C0 → C1 → C2 → C3 → C0.

In vacuum, only these 4 cells participate in the cycle. All other
substrate cells stay at `state = Empty`, `charge_level = 0`,
`threshold = baseline`.

## Parameters

Phase 1 requires committing to provisional values for 7 parameters,
then tuning them until a sustained cycle is found.

| Parameter | Provisional value | Tunable? |
|---|---|---|
| `baseline_threshold` | 100.0 | Yes (controls cycle period) |
| `adaptation_rate` | 0.5 (per discharge) | Yes (controls fatigue speed) |
| `relaxation_rate` | 0.05 (per idle tick) | Yes (controls recovery speed) |
| `deposit_amount` | 30.0 (per emission) | Yes (controls charging speed) |
| `load_coefficient` | 0.0 for Phase 1 (deferred) | Defer to Phase 2 |
| `propagation_time_base` | 1.0 (one tick) | Likely fixed |
| `bootstrap_charge_step` | 0.25 × baseline_threshold | Set by K=4 division |

**Load coefficient deferred:** for vacuum self-coherence, deposit traffic
is sparse (one pattern firing every few ticks). Connector load barely
exceeds 0–2 deposits at any time, so propagation time barely deviates
from `propagation_time_base`. Phase 1 can use `load_coefficient = 0`
and still claim the connector layer is "implemented" — the mechanism is
present but not exercised. Phase 2's planet introduces real load
gradients; Phase 2 is when load_coefficient gets tuned.

**Initial parameter search strategy:** start with the provisional values;
if the cycle dies (cells stop firing) or runs away (thresholds explode
or charge_level diverges), bisect the failing parameter. Document the
working region.

## Success Criterion (Phase 1)

**Cycle-structure invariance**, not bit-identity:

> Over at least **5,000 cycles** (≥ 20,000 substrate ticks at K=4), the
> following are stable:
> 1. **Cycle membership:** the same 4 cells (C0, C1, C2, C3) participate
>    in every cycle. No new cells join the cycle; no cycle cells stop firing.
> 2. **Cycle order:** cells fire in the same sequence (C0 → C1 → C2 → C3 → C0)
>    every cycle.
> 3. **Steady-state thresholds:** each cell's threshold settles within
>    ±10% of a steady-state value after a warm-up period (≤ 100 cycles).
>    No runaway growth, no collapse to baseline.
> 4. **Steady-state charge dynamics:** each cell's charge_level traces
>    the same waveform every cycle (0 → threshold → 0 → ...) within ±10%.

If all four hold for 5,000+ cycles, Phase 1 is **PASS**.

## Falsification Modes

- **Cycle dies.** After bootstrap, cells stop firing within a few cycles.
  Investigate: are deposits insufficient to charge neighbors? (Increase
  `deposit_amount`.) Is threshold relaxation too slow? (Cells become
  stuck above threshold.)
- **Cycle runs away.** Thresholds grow without bound, or charge_level
  exceeds threshold by more than `deposit_amount`. Investigate: is
  adaptation rate too high? Is firing rate too fast?
- **Cycle drifts.** Pattern survives but cell membership changes — a
  fifth cell joins the cycle, or one of the original 4 stops firing.
  Investigate: are connectors leaking deposits to non-pattern cells? Is
  the bootstrap unstable?
- **Cycle is parameter-fragile.** Sustained cycle exists only for a
  narrow parameter window; small perturbations kill it. This is a
  PARTIAL pass — the mechanism works but is fragile. Document the
  working region's size as part of the result.
- **No parameter region works.** No combination of values produces a
  sustained cycle. This is the strong falsification: the three-layer
  mechanism cannot support pattern coherence on its own. Phase 2 and 3
  become moot.

## Deliverables

```
experiments/132_grow_until_observed/
├── README.md                 (already exists, update to reference RESULTS)
├── capacitor.py              # Cell datatype + adaptive threshold dynamics
├── connectors.py             # Connector datatype + load-driven propagation
├── substrate.py              # Cubic lattice setup + face_neighbors helper
├── tick.py                   # Per-tick driver implementing the 5-step procedure above
├── fixture.py                # K=4 cycle definition + bootstrap procedure
├── parameters.py             # Default parameter values (with comments on tuning)
├── tests/
│   ├── test_capacitor.py     # Unit tests: charging, firing, threshold dynamics
│   ├── test_connectors.py    # Unit tests: deposit propagation, load tracking
│   ├── test_tick.py          # Integration tests: full per-tick behavior
│   └── test_fixture.py       # Bootstrap + first-few-ticks behavior
├── phase1_test.py            # The deliverable: 5000-cycle sustainment test
├── phase1_run.log            # Captured output
└── RESULTS_phase1.md         # Outcome documentation
```

### Implementation constraints

- Python 3, stdlib + `dataclasses`. No numpy needed at this scale (substrate
  is small; per-tick cost is O(cells × neighbors) which is trivial for
  10×10×10).
- Float arithmetic for charge_level and threshold; integer for tick counts
  and load.
- TDD throughout, following Exp 134 Phase 1's pattern.
- Tests use the no-prefix import style with a `conftest.py` adding the
  experiment dir to sys.path (matching Exp 134).

## Three Sub-Questions Phase 1 Answers

1. **Can a sustained cycle exist?** Binary. Yes if any parameter combination
   gives 5,000-cycle invariance.
2. **Is it parameter-fragile or robust?** Quantitative. The size of the
   working parameter region tells us how delicate the mechanism is.
   A narrow region suggests fragility; a broad region suggests robustness.
3. **What does the steady state look like?** Descriptive. Record threshold(t)
   and load(t) profiles for the working configuration; these become the
   baseline against which Phase 2's perturbations are compared.

## Out of Scope (Phase 1)

- Planet pattern, drift, gradient response — Phase 2.
- GR-metric profile, Schwarzschild fitting — Phase 3.
- RGG substrate — Phase 1 stays cubic.
- Matter/antimatter sign-handling — capacitor sign-blind design is a
  separate question.
- Connector load tuning (`load_coefficient = 0` for Phase 1).
- Multi-pattern interactions — Phase 2 introduces the planet pattern; Phase 1
  is single-pattern only.
- Performance optimization — substrate is small enough for naïve loops.

## Risks and Constraints

- **Geometry hand-designed.** Same compromise as Exp 134 Phase 1 — patterns
  are predetermined, not emergent. Family 2 / spontaneous emergence is
  parallel and parked.
- **Parameter tuning may consume a significant fraction of Phase 1 effort.**
  If the provisional values don't immediately work, finding any working
  region requires iteration. Budget for this; document the search.
- **The "five steps" per tick is provisional.** Order matters
  (relaxation before propagation? after?). If the obvious order doesn't
  work, alternate orderings should be considered.
- **No claim of QM reproduction in Phase 1.** RAW 132 §4's "beyond QM"
  claims are only relevant once the substrate is shown to support
  coherent patterns at all. Phase 1 is the prerequisite, not the test.

## Next Phases (sketched, not built)

- **Phase 2:** add a planet pattern (a second K=4 cycle, or a denser
  cluster of patterns); observe whether the test pattern's cycle is
  perturbed by the planet's emitted deposits propagating through
  connectors. If yes, drift in some direction. If no, locality holds
  even on capacitor substrate (which would be a strong negative
  result).
- **Phase 3:** if Phase 2 shows drift, measure threshold(r) and
  connector_load(r) profiles around the planet. Compare to GR's time
  dilation factor (∝ 1/(1−2M/r)?) and g_rr stretching factor. The
  five-row outcome table from RAW 132 §6 applies.
