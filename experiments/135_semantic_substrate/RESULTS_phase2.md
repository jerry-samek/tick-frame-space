# Experiment 135 Phase 2 — Results

**Status:** PASSED — v8-style spectrum crystallization works at substrate-cell granularity, in isolation from canvas dynamics.
**Date run:** 2026-05-01
**Spec:** `PHASE2_DESIGN.md`
**Run command:** `pytest experiments/135_semantic_substrate/phase2_test.py -v -s`
**Wall-clock:** 0.03 seconds

---

## Summary

Five independent cells, each starting empty (`Learning` state), each driven by its own biased token stream of 250 observations, all crystallized correctly to their expected top-3 spectra. Crystallization fired at the configured threshold (200 observations); subsequent 50 observations did not change the spectrum. Phase 1's deliverable + 21 unit tests still pass — backward compatibility holds.

---

## Configuration

- 5 isolated cells (no connectors, no canvas, no Substrate)
- `learning_threshold = 200`
- `crystallization_size = 3`
- 250 observations per cell (200 to trigger crystallization + 50 post-crystallization to verify spectrum is frozen)
- Per-cell bias: `[60, 25, 12, 3]` weights over a disjoint 4-token alphabet
- Seeded RNG (seed=42)

---

## Per-cell results

| Cell | Bias | Top-3 expected | Spectrum learned | Counts (top tokens after 250 obs) |
|---|---|---|---|---|
| 0 | `0:60, 1:25, 2:12, 3:3` | `{0, 1, 2}` | `{0, 1, 2}` ✓ | (0, 156) (1, 52) (2, 32) (3, 10) |
| 1 | `4:60, 5:25, 6:12, 7:3` | `{4, 5, 6}` | `{4, 5, 6}` ✓ | (4, 142) (5, 67) (6, 34) (7, 7) |
| 2 | `8:60, 9:25, 10:12, 11:3` | `{8, 9, 10}` | `{8, 9, 10}` ✓ | (8, 145) (9, 73) (10, 25) (11, 7) |
| 3 | `12:60, 13:25, 14:12, 15:3` | `{12, 13, 14}` | `{12, 13, 14}` ✓ | (12, 137) (13, 65) (14, 36) (15, 12) |
| 4 | `16:60, 17:25, 18:12, 19:3` | `{16, 17, 18}` | `{16, 17, 18}` ✓ | (16, 154) (17, 71) (18, 22) (19, 3) |

All 5 cells: `state == Crystallized` after 200 observations; spectrum frozen against the next 50 observations.

---

## What this proves

1. **Cell-level learning works.** A cell that starts empty, observes a stream of tokens, and crystallizes to top-K most-frequent observations produces the right spectrum, deterministically, with seeded RNG.

2. **Crystallization is a clean state transition.** `Learning → Crystallized` at the configured threshold; spectrum is frozen post-crystallization (50 additional observations didn't alter the learned spectrum).

3. **Multiple cells learn independently.** No shared state between cells; no leak between observation streams. Each cell's spectrum reflects only its own observations.

4. **The mechanism is non-trivial.** Crystallized spectra correctly identified the top-3 against a 4th-rank distractor (weight ratio 12:3), even with RNG noise.

5. **Backward compatibility holds.** Phase 1's deliverable + all 21 Phase 1 unit tests still pass — adding learning to `Cell.classify()` does not break crystallized-cell behavior. Cells with preset spectra start `Crystallized` (via `__post_init__`) and observations are recorded but don't trigger re-crystallization.

---

## What this does not prove

- **Learning under canvas dynamics.** Phase 2 drove cells directly via `cell.classify()`. The interesting integration question — what does the canvas do when it queries a `Learning` cell, given that `Unknown` currently triggers spawn — is Phase 3.
- **Causal window** (v8's `learning_window = 2 * birth_tick`). Phase 2 used a fixed count threshold. Phase 3 (with substrate-spawned cells having non-zero birth ticks) is where causal windowing would actually matter.
- **Adaptive top-K.** Spectrum size is fixed at 3. Whether to use coverage-based adaptive top-K is a Phase 3+ question.
- **Spectrum updating after crystallization.** Once crystallized, fixed. Re-learning / decay / spectrum drift are deferred.

---

## Anomalies and tuning during the run

### Anomaly: First run failed on cell 2 due to RNG variance

Original spec used `learning_threshold=50` and bias `[50, 25, 15, 10]`. First run produced cell 2 spectrum `{8, 9, 11}` instead of `{8, 9, 10}` — at sample size 50, the variance on the 3rd/4th-rank tokens (expected counts ~7.5 and ~5) is high enough to flip them. Token 11 (weight 10) outdrew token 10 (weight 15) in the first 50 observations.

**Tuning, not redesign:** raised `learning_threshold` to 200 (more observations → less variance) and used a more separated distribution `[60, 25, 12, 3]` (clear gap between 3rd-rank weight 12 and 4th-rank weight 3). Both fixes applied, second run passed.

The mechanism is correct; the original parameters were just too aggressive for clean rank-3 separation. With proper sample size + bias spread, the crystallization is reliable.

---

## Connection to RAW 133's "patterns first" stance

Phase 2 did not test the substrate's claim that *patterns* (not single cells) are the primary unit of meaning. It tested the *primitive* — a single cell's ability to learn a spectrum. The interesting question — does a substrate of Learning cells form coherent classifications that *match* an external pattern they observe — is Phase 3.

Phase 2 is a prerequisite. Without working cell-level learning, Phase 3's "preset pattern + Learning observers" would be debugging at two levels. With Phase 2 confirmed, Phase 3 becomes a focused integration test.

---

## Next steps

**Phase 3 candidates** (per `RESULTS_phase1.md` next-steps list, now informed by Phase 2 results):

1. **Hybrid pattern + observer (option C from earlier brainstorm).** Phase 1 K=6 ring with preset spectra + a few empty Learning observer cells attached. Verify observers crystallize to spectra that *mirror* the pattern they observe. This is the real "does the substrate recognize patterns" test.
2. **Canvas semantics for Learning cells.** Currently a Learning cell returns `Unknown`, which triggers spawn at canvas exhaustion. For Phase 3, Learning cells need different canvas semantics — maybe Unknown means "forward to me, I'll observe" instead of "blank slot, spawn." This is the architectural question Phase 3 has to settle.
3. **Multiple injection points** to feed the observer cells with different traffic profiles.

---

## Files

- `PHASE2_DESIGN.md` — design spec
- `cell.py` — extended with `State` enum, `obs_counter`, `observe()`, `crystallize()`, modified `classify()`
- `tests/test_cell.py` — 7 new unit tests (state transitions, crystallization, frozen-spectrum check)
- `phase2_test.py` — 5-cell deliverable
- `phase2_run.log` — captured output
- `RESULTS_phase2.md` — this file
