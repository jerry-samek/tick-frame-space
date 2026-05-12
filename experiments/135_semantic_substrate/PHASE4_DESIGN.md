# Experiment 135 Phase 4 — Design

**Status:** Design settled 2026-05-01. Ready to implement.
**Builds on:** Phase 3 (canvas-rule change + Learning observer at c0). No mechanism changes.

---

## Phase 4 question

**Do Learning observers at different ring cells learn different specializations, or do they all converge?**

If observers at different sites crystallize to different tokens — reflecting their host's local "exhaust pattern" — that's strong evidence the substrate's semantic structure has *positional* differentiation: where a cell sits in the topology shapes what it learns. If they all converge to the same token, the substrate is too uniform and observers don't specialize.

---

## Setup

- K=6 ring (Phase 1, preset Crystallized spectra `{i}` for `c_i`).
- **6 observers**, one attached to each ring cell.
- Phase 1 stream at `c0` (50/50 known/unknown, seed=42), cadence=30.
- 10,000 ticks.
- Observer params: `learning_threshold=50`, `crystallization_size=1` (one most-frequent token per observer).

### Why these params

- **Smaller threshold (50 vs Phase 3's 200):** observers at non-c0 cells see less traffic. Token i reaches `c_i` only via deposits walking the ring (and only when `c_i`'s neighbors are canvased before `c_i` — many tokens are intercepted earlier). At threshold=200 most non-c0 observers wouldn't crystallize within the run.
- **Crystallization size = 1:** with smaller threshold, top-1 is the most-stable selection. Phase 2 showed top-3 needs ≥200 observations to be reliable; top-1 only needs ~10-20 dominant observations.
- **Cadence=30:** same as Phase 3 — keeps c0 from saturating after spawned children + observer pile up.

### Why no mechanism changes

Phase 3's canvas-rule change (Different over Unknown) already handles observers cleanly. No cell or substrate code changes for Phase 4 — just a new fixture (multiple `attach_observer` calls) and a new deliverable test.

---

## Predictions

Each observer attached to ring cell `c_i` sees tokens for which `c_i` self-check fails AND canvas reaches the observer (no early Same-termination on a closer match).

- **`observer_c0`:** sees tokens not in `{0}` for which c0's canvas exhausts. Spawned children of c0 hold `{6..10}`; c0's ring neighbors are `c5={5}` and `c1={1}`. So canvas terminates Same on tokens 5, 1, 6-10 (early). Tokens 2, 3, 4 have no early-Same match — observer always sees them. Predicted spectrum: most likely `{3}` or `{4}` (the ones with highest per-token frequency without competing termination).
- **`observer_c1`:** sees tokens for which c1's canvas exhausts. c1's neighbors are c0={0}, c2={2}, observer_c1. Tokens 0, 2 terminate Same early. Other tokens canvas-exhaust → observer sees them. Predicted: one of {3, 4, 5} (tokens that walk forward through c1 toward their home).
- **`observer_c_i`** generally: sees tokens that walk through `c_i` and aren't `c_(i-1).spectrum` or `c_(i+1).spectrum` (the immediate neighbors).

Predicted heterogeneity: each observer specializes to a **different** token because each ring cell has different immediate neighbors blocking different tokens via early-Same.

### Cascade prediction

Once observers crystallize, they intercept tokens at the first observer the deposit reaches. This may cascade — a token that previously walked all the way to its ring home now gets intercepted at the first observer along its path. Observers crystallizing earlier will dominate (capture tokens before later observers get the chance to learn them).

This is a real dynamic to measure, not necessarily a problem. RAW 133's "patterns first" claim implies routing is by classification, not by topological role.

---

## Success criteria

1. **Phase 3 invariants hold:** ring intact, spawn count = 5 with spectra `{6..10}`, semantic routing = 100% (every consumed token's home cell has the token in spectrum).
2. **All 6 observers crystallize** within the 10K-tick run.
3. **No observer learns its host's token:** for each observer attached to `c_i`, `i not in observer.spectrum` (because `c_i` self-consumes `i` before canvasing).
4. **Heterogeneity:** at least 3 distinct spectra across the 6 observers (observers don't all converge).

### Anomaly trigger

If all 6 observers crystallize to the same token: heterogeneity fails. The substrate is too uniform — observers don't specialize. That's an interesting *negative* result and worth documenting; it would suggest Phase 4+ needs to explore richer fixtures (multiple injection points, biased streams) to produce specialization.

---

## File changes

- `phase4_test.py`: deliverable. Uses existing `build_k6_ring` and `attach_observer`.
- `phase4_run.log`: captured output.
- `RESULTS_phase4.md`: outcome.

No changes to `cell.py`, `substrate.py`, `fixture.py`, or any earlier phase tests.

---

## Estimated work: 30 minutes

- 15 min: write phase4_test.py
- 15 min: run + RESULTS doc
