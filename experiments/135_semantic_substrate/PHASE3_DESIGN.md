# Experiment 135 Phase 3 — Design

**Status:** Design settled 2026-05-01. Ready to implement.
**Builds on:** Phases 1 (substrate + canvas) and 2 (cell-level learning).

---

## Phase 3 question

**Can a Learning observer cell, attached to a Crystallized ring, learn coherently from passing canvas traffic without breaking Phase 1's mechanism?**

This is the integration test: Phase 1 mechanism (canvas + spawn) + Phase 2 mechanism (observe + crystallize) running together on a hybrid fixture (preset pattern + Learning observer).

---

## Mechanism change: canvas exhaust prefers Different over Unknown

Phase 1's canvas-exhaust rule was: *"any Unknown responder → spawn."* Phase 3 has Learning cells (observers) that respond Unknown. Under the old rule, every canvas where an observer was queried would trigger a spurious spawn.

**New rule:**

```
Canvas exhausts (no Same found among non-predecessor non-dead-paths neighbors):
1. If any responder said Different → forward to first Different.
2. Else if any responder said Unknown → spawn at this cell.
3. Else (no responders — empty canvas) → bounce to predecessor, or spawn if no predecessor.
```

Different takes precedence over Unknown. Spawn-on-Unknown only fires when *all* responders are Unknown — meaning none of the neighbors is in a position to route the deposit further. This matches Phase 1 behavior exactly when no Learning cells exist (ring cells always say Different/Same, never Unknown).

**Phase 1 backward compat:** All Phase 1 deliverable behavior preserved. The K=6 ring has only Crystallized cells; canvas always finds Different. The one unit test that exercised the old "Unknown → spawn" path (`test_canvas_exhaustion_with_unknown_spawns_child`) needs updating — the original setup had c1 Different + c2 Unknown, which under the new rule forwards to c1 instead of spawning. Test setup needs both neighbors empty/Learning to verify the all-Unknown spawn branch.

---

## Phase 3 fixture

K=6 ring (Phase 1 setup) + **1 observer cell attached to `c0`**.

```
            observer_c0 (empty, Learning)
                 |
c0 — c1 — c2 — c3 — c4 — c5 — c0   (ring; preset spectra)
```

- `observer_c0`: empty spectrum, Learning state.
- Bidirectional connector between `c0` and `observer_c0`: both add the other to their `connectors` list.
- `c0.connectors` becomes `[c5, c1, observer_c0]` (degree 3 initially, growing to 8 once spawned children are added).

### Stream

Same as Phase 1 (50/50 known/unknown, seed=42, alphabet `{0..5}` known + `{6..10}` unknown), but **cadence relaxed to 30 ticks** (was 15) — c0's degree at steady state is 8 (2 ring + 5 spawned + 1 observer), giving canvas time of ~16 ticks. Cadence 30 keeps c0 from saturating.

### Run length: 10,000 ticks

→ ~333 deposits → ~300 observations at c0's observer (every non-`{0}` deposit's canvas queries the observer). Comfortably above the `learning_threshold=200`, so observer crystallizes.

---

## Predictions

Observer at c0 sees canvas queries for **all tokens except `0`** (which c0 self-consumes without canvasing). With the 50/50 mix:

- 6 known tokens, equally distributed: ~8.33% per token total.
- 5 unknown tokens, equally distributed: ~10% per token total.
- c0 self-consumes ~8.33% (token=0); remaining 91.67% canvas → observer sees all of those.

Per-token frequency at observer:
- Each known non-zero (1-5): ~9.1% of observations.
- Each unknown (6-10): ~10.9% of observations.

**Expected top-3:** three of the five unknowns (since unknowns have higher per-token frequency than known-non-zeros). Which three depends on RNG draw — the 1.8% gap between unknown (~10.9%) and known-non-zero (~9.1%) is meaningful but not huge. With ~300 observations, expected counts are ~33 (unknowns) vs ~27 (knowns) — separation is tight but reliable across runs with the same seed.

The honest acceptance criterion: observer's spectrum **should be a subset of `{1..10}`** (not include 0), and the spectrum **should be self-consistent with `obs_counter.most_common(3)`**. We don't predict exact tokens because RNG variance at the unknown-vs-known boundary is real — we predict the *kind* of pattern.

---

## Success criteria

1. **Phase 1 success criteria all hold** at the observer-augmented fixture (ring integrity, known-token routing, exactly 5 spawns at c0, etc.).
2. **Observer accumulated enough observations** (`>= learning_threshold = 200`).
3. **Observer crystallized** (`state == State.CRYSTALLIZED`).
4. **Observer spectrum is self-consistent** — equals top-3 of its `obs_counter`.
5. **Observer spectrum does not contain token 0** (c0 self-consumes 0 before canvasing, so observer should never observe it).
6. **Observer spectrum is a subset of `{1..10}`**.

---

## What this proves (if it passes)

- Canvas mechanism cleanly accommodates Learning cells without spurious spawns.
- A Learning observer attached to a busy cell crystallizes from passing traffic.
- Phase 1 + Phase 2 mechanisms compose without interference.

## What this does not prove

- Observer crystallizing to a *meaningful* spectrum (it crystallizes to whatever it sees most, which depends on injection bias). Phase 4+ would test "observer attached to c_i crystallizes to spectrum reflecting c_i's role."
- Multiple observers learning different specializations from different positions. Phase 4+ test.
- Spawned children as Learning cells (they're still pre-Crystallized in Phase 3). Future phase.

---

## File changes

- `substrate.py`: `_decide_after_canvas` reordered (Different before Unknown).
- `tests/test_substrate.py`: update `test_canvas_exhaustion_with_unknown_spawns_child` setup (both neighbors empty so Unknown is the only response type).
- `fixture.py`: add `attach_observer(substrate, host)` helper (returns observer Cell).
- `phase3_test.py`: deliverable.
- `RESULTS_phase3.md`: outcome.

---

## Estimated work: ~1 hour

- 15 min: substrate rule change + Phase 1 test fix
- 10 min: observer fixture helper
- 20 min: phase3_test.py
- 15 min: run + RESULTS doc
