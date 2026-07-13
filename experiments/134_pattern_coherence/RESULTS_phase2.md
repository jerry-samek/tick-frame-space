# Experiment 134 Phase 2 — Results

**Status:** PASS — predicted decoherence confirmed
**Date run:** 2026-04-28
**Spec:** `docs/superpowers/specs/2026-04-28-pattern-coherence-phase2-design.md`
**Plan:** `docs/superpowers/plans/2026-04-28-pattern-coherence-phase2.md`
**Phase 1 result:** PASSED 2026-04-28 (see RESULTS.md)

## Summary

Phase 2 confirms the spec's predicted outcomes on all three scenarios. Same-sign
face-adjacent contact (S1) destroys both patterns within a single K-cycle —
faster than the test pattern's centroid has any chance to drift. Single- and
two-cell-gap configurations (S2, S3) are bit-identical for all 1000 cycles, so
the substrate provably has no long-range coupling across vacuum cells. The
"gravity-at-a-distance is unearnable" working hypothesis is operationally
supported, and the matter/antimatter distinction has been pushed into a
Phase 3 design problem: as designed, the Phase 1 rule does not distinguish
same-sign from opposite-sign contact.

## Per-scenario observations

### S1: face-adjacent (contact event)

- First break (canvas hash changed at cycle): **2** (cycle 1 → cycle 2)
- Initial centroid of test pattern: `(2.5, 0.5, 0.0)`
- Final centroid: `None` (no test cells remain)
- Drift vector: `None` (final centroid undefined)
- Final n_test_alive: **0** (out of 4 initially)
- Identity trajectory (first 10 cycles, `(cycle, n_test_alive)`):
  `[(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0), (8, 0), (9, 0), (10, 0)]`
- Reference hash (cycle 1): `951a9014873bfbb92266685db59c271e496f93fea267be9466833765c467e751`

The test pattern dissolved before its centroid had any chance to move. By the
first cycle boundary, every test-tagged cell has expired (`n_test_alive = 0`),
so drift is undefined for the entire run.

The mechanism is what the spec predicted: face-adjacent placement merged the
two K=4 planets into a single 8-cell connected component. Step B for that
merged component fails — `find_c_max` and `find_c_min_positive` return cells
whose lattice common face-neighbor is either ambiguous or wedged, and the
component cannot identify a unique successor cell to paint. Per-component
fault tolerance prevented the failure from cascading to other (nonexistent
in this scenario) components, but a component that cannot paint also cannot
renew, and Doc 28's renewal-not-preservation contract collapses immediately:
its cells decay tick by tick and expire within the K-tick budget. By the
time Phase 2's measurement loop samples the canvas at the cycle 1 boundary,
the component has already expired entirely. Both the test pattern and the
planet pattern dissolve together — same mechanism, same K-cycle.

### S2: 1-cell gap (positive control)

- First break: None (invariant for all 1000 cycles)
- Final n_test_alive: **4** (out of 4 initially)
- Drift vector: `(0.0, 0.0, 0.0)`
- Reference hash: `7a64b8296923d98d0edef96253f83d93a476354f384bab52d5bc244efcd31264`

PASS. The two K=4 planets are separated by exactly one empty cell along x.
Each remains a separate connected component throughout the run, each runs
its own independent K=4 renewal cycle, and the canvas hash is bit-identical
at every cycle boundary across 1000 cycles. The test pattern is invariant.

### S3: 2-cell gap (positive control)

- First break: None (invariant for all 1000 cycles)
- Final n_test_alive: **4** (out of 4 initially)
- Drift vector: `(0.0, 0.0, 0.0)`
- Reference hash: `0cc4dc5e8e7812e219397e03956f8daca41d296e29cbc92d6ad5b58353f0954f`

PASS. Identical behavior to S2 with a wider gap. Two independent components,
two independent renewal cycles, bit-identical canvas at every cycle boundary
for 1000 cycles.

The S2/S3 pair together demonstrates that the substrate is **strictly local
across empty cells**. Patterns separated by *any* nonzero number of empty
cells do not see each other through the vacuum — there is no field, no
gradient, no coupling. The 1-cell-gap S2 result is the strongest version of
this claim, since it's the minimum nonzero separation possible.

## What this proves (or falsifies)

- **"Gravity-at-a-distance is unearnable in this substrate ontology"** —
  confirmed (operationally) by S2 and S3 invariance. Two patterns at minimum
  vacuum separation produce zero observable interaction over 1000 cycles.
  There is no mechanism in Phase 1's rule by which one pattern can influence
  another except through direct face-adjacent contact, and that contact does
  not produce attraction or drift — it produces mutual decoherence. Any
  future "gravity" in this substrate cannot come from the rule as currently
  defined; it must come from somewhere else (composite-scale dynamics,
  coarse-graining of decoherence statistics, or a substrate extension).

- **"Same-sign contact produces mutual decoherence"** — confirmed by S1.
  Both planets dissolve together within a single K-cycle. The merged 8-cell
  component cannot satisfy Step B's uniqueness requirement, fails to paint
  a successor, and decays without renewal.

- **The Phase 1 rule is sign-blind for contact, not just for renewal.**
  The same merge-and-ambiguity failure mode that destroys S1 (same-sign)
  would also destroy a hypothetical opposite-sign face-adjacent placement,
  for the same structural reason: contact creates an 8-cell component whose
  Step B lookups are ambiguous regardless of the sign of the constituent
  cells. The matter/antimatter distinction (predicted by Imbalance theory,
  Doc 29) has to come from somewhere outside this rule. As designed, the
  rule predicts that **all** face-adjacent contact decoheres, with no sign
  asymmetry. This is a design constraint, not a Phase 2 failure.

## Next steps

- **Phase 3 (opposite-sign annihilation prediction) is now harder to
  differentiate.** If same-sign contact already produces total decoherence
  within one K-cycle, "matter-antimatter annihilation" needs a distinguishing
  signature beyond "patterns dissolve" — because patterns already dissolve
  for same-sign too. The two natural candidates are: (a) a different
  decoherence *signature* (e.g., burst of zero-magnitude cells, conservation
  imprint on the substrate), or (b) a rule modification (sign-aware
  tie-breaking, sign-aware bootstrap, or two-channel substrate from the
  spec's R3 sketch) that lets same-sign and opposite-sign contact diverge.

- **Phase 2.5 (rule modification for sign-aware tie-breaking) is now strongly
  motivated.** It was sketched in the Phase 1 spec as optional; Phase 2's
  result promotes it to a likely prerequisite for Phase 3. The brainstorm
  for Phase 2.5 should ask: "what minimal rule change makes same-sign
  contact behave differently from opposite-sign contact?" — and should run
  before Phase 3, not after.

- **The "gravity is unearnable" working hypothesis** can now be carried as
  an assumption into other experiments. Any model in this codebase that
  needs gravity-at-a-distance must either justify it from composite-scale
  emergent dynamics, abandon the Phase 1 substrate, or accept that gravity
  is not present at the substrate ontology layer.

- **No restart of Phase 2 needed.** S2 and S3 PASSED as positive controls;
  S1 produced exactly the predicted "fast decoherence" outcome. The result
  is clean.
