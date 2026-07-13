# Experiment 134 Phase 1 — Results

**Status:** PASS
**Date run:** 2026-04-28
**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-pattern-coherence-phase1.md`

## Summary

Phase 1 verified bit-identity at every K-tick boundary for all 4 fixture
configurations over 10,000 cycles each (≈ 240,000 substrate ticks total
across the four runs). Zero drift, zero anomalies.

The rule earns its proof: a sign-blind transactional renewal rule on a
3D signed-integer substrate, applied to a Hamiltonian-cycle pattern that
satisfies the geometric constraint, produces an exact fixed point in
vacuum. Doc 28's "renewal not preservation" commitment is operational on
discrete substrate.

## Reference hashes

SHA-256 of canonicalized canvas state at the K-tick boundary (after one
post-bootstrap cycle to flush the bootstrap path through tick(); see
`phase1_test.py::_run_fixture_phase1`).

| Fixture | K | Sign | Reference hash | Cycles verified |
|---------|---|------|----------------|-----------------|
| F1 (2×2 square) | 4 | +1 | `2299a25689f156e014800521520538c59678988c63c2eb691c8ff9fd03aee176` | 10,000 |
| F1 (2×2 square) | 4 | −1 | `d8d410f2e786ce09e63e73ac890df9a94243adb9342a15f5737bdb1157c75267` | 10,000 |
| F2 (2×3 perimeter) | 6 | +1 | `8f15a588beec6ba0bf09662dd393db17b2b1ef2bc59b49e45ccde2f5f1943fa9` | 10,000 |
| F3 (4×2 perimeter) | 8 | +1 | `11c91de76ce24d700feae1f4044ae2019f7e4dc4b83dd9eae52898c11065d024` | 10,000 |

Wall-clock: 3.65 s for all four 10,000-cycle runs (Python 3.13.5, single thread).

## Anomalies

### Spec-time fixture choice was wrong; corrected during implementation

The spec named F3 as "3×3 hollow ring" (perimeter of 3×3 grid, K=8). On
implementation, the geometric-constraint test correctly flagged this as
invalid: cells (1,0,0) and (2,1,0) at cycle distance 2 have lattice
common face-neighbor (1,1,0), which is the *interior* cell of the 3×3
grid and not a pattern cell. The constraint requires all such common
face-neighbors to be pattern cells.

**F3 was replaced with a 4×2 rectangle perimeter (8 cells, no interior).**
The 4×2 grid has no interior cell because it has only 2 rows, so the
failure mode does not arise. All cycle-distance-2 pairs in F3 (4×2) have
their lattice common face-neighbors entirely within the pattern.

This is not a Phase 1 failure — it's the geometric-constraint test doing
its job at design time, before any tick was simulated. Update the spec
to match implementation if/when the spec is revised.

### Non-uniqueness unit test had a wrong setup

The first draft of `test_find_c0_non_uniqueness_raises` used (0,0,0) and
(2,0,0), which actually have a *unique* lattice common face-neighbor
((1,0,0)) — they differ by 2 in one coordinate. Real non-uniqueness
requires cells differing by 1 in two coordinates (e.g., (0,0,0) and
(1,1,0) share both (1,0,0) and (0,1,0)). Test corrected during
implementation.

## What this proves

- **Doc 28 is operational on discrete substrate.** A localized pattern
  can be a configuration that exists only by being continuously
  rerendered — and the rendering is exact in vacuum, by construction.
- **The renewal rule is sign-blind.** F1+ and F1− used identical rule
  code with no sign-discrimination, and produced symmetric matter and
  antimatter patterns. Antimatter is the natural CP-mirror, not
  engineered.
- **The renewal is transactional.** Bit-identity is checked at K-tick
  boundaries; the canvas state at any other tick within a cycle is *not*
  identical to the state at the same phase of an earlier cycle, but the
  full K-tick transaction reproduces the canvas exactly. K is the
  pattern's natural time unit.
- **The rule scales across K = 4, 6, 8.** No new mechanics needed to
  jump from F1 to F3; the same `tick()` does all three. Rule scales by
  geometry alone.

## What this does not prove

- Pattern shape *emergence* (Phase 1 fixtures are predetermined
  Hamiltonian cycles satisfying the geometric constraint — Family 2 /
  Phase 1.5 is the spontaneous-shape question).
- Drift under external γ field (Phase 2).
- Annihilation under opposite-sign overlap (Phase 3).
- Pattern coherence under field gradients faster than 1/K (Phase 2+
  prediction in the spec).

## Files

```
experiments/134_pattern_coherence/
├── README.md             # run instructions
├── conftest.py           # pytest path fix for leading-digit dir
├── __init__.py
├── substrate.py          # Canvas type + decay + face_neighbors
├── rule.py               # bootstrap + find_c_max + find_c_min_positive + find_c0 + step_b + tick
├── fixtures.py           # F1 (2x2 K=4), F2 (2x3 K=6), F3 (4x2 K=8)
├── phase1_test.py        # the Phase 1 deliverable (bit-identity 10k cycles)
├── tests/
│   ├── test_substrate.py # 8 unit tests
│   ├── test_rule.py      # 18 unit tests (1 corrected during run)
│   └── test_fixtures.py  # 9 validation tests (1 caught invalid F3 design)
└── RESULTS.md            # this file
```

35 unit tests + 4 deliverable tests = **39 tests, all passing**.

## Next phase

Phase 2: drift under same-sign external γ field. Spec sketches three
candidate resolutions (R1: large K; R2: gradient relative to local
background; R3: two-channel substrate). Recommended starting point: R2.
Separate brainstorming session and separate spec required.
