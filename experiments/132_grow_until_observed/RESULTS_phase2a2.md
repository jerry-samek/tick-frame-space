# Experiment 132 Phase 2A.2 — Results (Load Coefficient Sweep)

**Status:** STRUCTURAL FALSIFICATION — saturation is NOT parameter-tunable
**Date run:** 2026-04-28
**Spec:** derived from Phase 2A.5 outcome 3 → 2A.2 next-step recommendation
**Theory:** RAW 132 §3.6.1 + §3.4 (H4.1 load-driven connector propagation)
**Phase 2A.5 result:** outcome 3 (superposition fails); R1 alone showed flat profiles

## Summary

Load coefficient swept over **three orders of magnitude** — `{0.001, 0.01, 0.05, 0.1, 0.5, 1.0}` — on the planet-only substrate (no test pattern). Every sweep value produces an **identical** steady state: threshold(r) = 100.0500 at every radius, load(r) = 1.0000 at every radius.

The substrate's flat-profile saturation seen in Phases 2 and 2A.5 is **structural** to the three-layer mechanism with full lattice connectivity. Tuning `load_coefficient` does not break out of it.

## Sweep summary table

| `load_coefficient` | threshold(r) range | thr monotonic↓ | load(r) range | load monotonic↓ |
|---:|---:|:---:|---:|:---:|
| 0.001 | 0.0033 | False | 0.0000 | True (trivially flat) |
| 0.01  | 0.0033 | False | 0.0000 | True (trivially flat) |
| 0.05  | 0.0033 | False | 0.0000 | True (trivially flat) |
| 0.1   | 0.0033 | False | 0.0000 | True (trivially flat) |
| 0.5   | 0.0033 | False | 0.0000 | True (trivially flat) |
| 1.0   | 0.0033 | False | 0.0000 | True (trivially flat) |

**Interpretation of "monotonic↓ True for load":** misleading — every cell has load 1.0 exactly, so the profile is *trivially* monotonic (a == b counts as a ≥ b). The `_is_monotonic_decreasing` helper does not distinguish "flat" from "actually decreasing." Only the threshold-range column carries signal, and it shows 0.0033 across the entire sweep — that's the planet's 4 cells at threshold 100.1 vs the rest at 100.0500 averaging into the integer-distance bins. Identical structure across 1000× variation in `load_coefficient`.

## What this proves

1. **The substrate-saturation finding from Phase 2A.5 is structural, not parametric.** Three orders of magnitude in `load_coefficient` produces identical steady-state profiles. The mechanism is not failing to *find* a working regime — every regime in the swept range has the same flat saturation.

2. **H4.1 (load-driven connector propagation as substrate-firmware spatial stretching) is more decisively falsified for the current substrate architecture.** Phase 2 showed flat load profile at one parameter; Phase 2A.5 showed flat load with no test confound; Phase 2A.2 shows flat load across a wide parameter range. The mechanism does not produce gradient under any tested `load_coefficient` value with full lattice connectivity.

3. **Phase 2A.4 (partial connectivity) is now the priority next experiment.** If saturation is structural to "every face-adjacent pair has a connector," then reducing connectivity (cycle-only + selective halo, or sparser face-adjacency) is the design lever that hasn't been tested. If saturation persists even with partial connectivity, then the three-layer mechanism itself (charge + adaptive threshold + load) has a fundamental limit.

## What this does not prove

- That the three-layer mechanism categorically fails — partial connectivity hasn't been tested.
- That `load_coefficient` is irrelevant — it might matter outside the sweep range, or for non-equilibrium dynamics, or for transient (pre-steady-state) profiles. We measured only steady state.
- That Phase 1's sustained K=4 cycle was lucky — Phase 1 had cycle-only wiring, not full lattice connectivity, so its dynamics are different. Cycle-only wiring is essentially Phase 2A.4's target.

## Anomalies

- The interpretation message printed by `phase2a2_test.py` reads "AT LEAST ONE sweep value produces monotonic decreasing profile" because the load profiles are trivially monotonic when all values are 1.0. This is a bug in the categorization logic — flat does not equal monotonic-decreasing in the sense the experiment cared about. Should be fixed in any future re-runs (`thr_range > some_threshold` instead of `monotonic`).

## Next steps

**Phase 2A.4 — partial connectivity** is now the highest-priority next experiment. Hypothesis: saturation comes from full lattice connectivity flooding all cells with deposits; reducing connectivity (cycle connectors only, or cycle + ε halo) lets gradients form before equilibrium.

If 2A.4 still shows flat profiles, the three-layer mechanism itself doesn't admit gradients on this substrate — at which point RAW 132's H3.5/H4.1 should be considered structurally falsified, and a different mechanism is needed for spatial stretching.

If 2A.4 produces gradient → the working substrate architecture is "cycle-bound connectors," and Phases 2 and 2A.5 were measuring the wrong substrate. RAW 132 §3.4 would need updating.

## Files

- `phase2a2_test.py` — sweep runner
- `phase2a2_run.log` — full run output (~270 lines, all 6 sweep details)
- `RESULTS_phase2a2.md` — this file

## Wall-clock

4 minutes 26 seconds for all 6 runs (each 5,000 cycles on 21×21×3 substrate).
