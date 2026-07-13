# Experiment 135 Phase 2 — Design

**Status:** Design settled 2026-05-01. Ready to implement.
**Builds on:** `PHASE1_DESIGN.md` (mechanism unchanged; this phase adds learning to `Cell`).

---

## Phase 2 question

**Does v8-style spectrum crystallization work at the substrate-cell level, in isolation from canvas dynamics?**

Specifically: a cell that starts empty, observes a stream of tokens, and crystallizes to its top-K most-frequent observations after N observations — does this produce the right spectrum? Does it scale across multiple independent cells with different streams?

This is deliberately *not* an integration test with the Phase 1 canvas mechanism — that's Phase 3 (hybrid: preset pattern + Learning observers). Phase 2 isolates the learning primitive so we can debug it independently.

---

## What changes

### `Cell` gets four new fields and three new behaviors

New fields (additive — no Phase 1 field changes):

```
obs_counter:           Counter[int]    # tally of observed tokens
state:                 State            # Learning | Crystallized
learning_threshold:    int = 50         # observations before crystallization (config)
crystallization_size:  int = 3          # top-K tokens to keep in spectrum (config)
```

New `State` enum:

```python
class State(Enum):
    LEARNING = "learning"
    CRYSTALLIZED = "crystallized"
```

New methods on `Cell`:

```python
def observe(self, token: int) -> None:
    self.obs_counter[token] += 1
    if (self.state == State.LEARNING
            and sum(self.obs_counter.values()) >= self.learning_threshold):
        self.crystallize()

def crystallize(self) -> None:
    top_k = self.obs_counter.most_common(self.crystallization_size)
    self.spectrum = {token for (token, _) in top_k}
    self.state = State.CRYSTALLIZED
```

Modified method (additive — observation precedes classification):

```python
def classify(self, token: int) -> Response:
    self.observe(token)                    # NEW: always count
    if self.state == State.LEARNING:
        return Response.UNKNOWN
    if token in self.spectrum:
        return Response.SAME
    return Response.DIFFERENT
```

### `__post_init__` initializes state based on spectrum

A cell created with a preset spectrum (Phase 1 ring cells) starts `Crystallized`; a cell created empty (Phase 2 learners, Phase 1 spawned children) starts `Learning`.

```python
def __post_init__(self):
    if self.spectrum:
        self.state = State.CRYSTALLIZED
    else:
        self.state = State.LEARNING
```

### Phase 1 backward compatibility

- Phase 1 ring cells: preset spectrum → start `Crystallized` → `classify()` observes (counter grows) but spectrum is frozen. No behavior change.
- Phase 1 spawned children: created with `spectrum={t}` → start `Crystallized` for the same reason. No behavior change.
- All Phase 1 unit tests + the deliverable should still pass.

---

## Phase 2 design choices

These were settled during the brainstorm:

- **(a) Crystallization trigger:** count threshold. After observing `N=50` tokens, crystallize. Simplest and most debuggable knob.
- **(b) Spectrum size:** fixed top-K with `K=3`. Meaningful pass/fail; not trivial like K=1.
- **(b) Test deliverable:** 5 independent cells (no connectors), each driven by its own biased stream, verify each crystallizes to its expected top-3. Tests scale across multiple parallel cells.

Rejected alternatives:
- (c) Causal window `2 * birth_tick`: doesn't make sense for cells with `birth_tick=0`. Better suited for Phase 3 spawned-cell dynamics.
- (a) K=1: too trivial — single most-frequent always wins.
- (a) Single cell: scales-to-N is the more interesting claim.

---

## Phase 2 deliverable

**5 isolated cells, each with its own biased stream, ~70 observations each.**

Token streams (per cell, drawn from seeded RNG):

| Cell | Bias (token: weight) | Expected top-3 spectrum |
|------|------|------|
| `c0` | 0:50, 1:30, 2:15, 3:5    | `{0, 1, 2}` |
| `c1` | 4:50, 5:30, 6:15, 7:5    | `{4, 5, 6}` |
| `c2` | 8:50, 9:30, 10:15, 11:5  | `{8, 9, 10}` |
| `c3` | 12:50, 13:30, 14:15, 15:5 | `{12, 13, 14}` |
| `c4` | 16:50, 17:30, 18:15, 19:5 | `{16, 17, 18}` |

Each cell:
- Starts empty (`Learning`).
- Receives ≥ 50 observations via `cell.classify(token)`.
- Crystallizes to its top-3 most-frequent.

Drive cells directly — no Substrate, no canvas, no Deposit. The deliverable test is essentially:

```python
for cell, stream in zip(cells, streams):
    for token in stream[:70]:
        cell.classify(token)
    assert cell.state == State.CRYSTALLIZED
    assert cell.spectrum == expected[cell.creation_order]
```

### Success criteria

- Each cell ends `Crystallized` after observing ≥ 50 tokens.
- Each cell's spectrum matches the expected top-3 (above table) — test must pass with the seeded RNG.
- Crystallized spectrum is frozen: continuing to observe more tokens does not change it.
- Phase 1 deliverable still passes (regression check).

---

## Out of scope for Phase 2

- **Canvas integration with Learning cells.** What does the canvas mechanism do when a neighbor responds `Unknown` because it's `Learning` (not because it's empty-by-default)? This is the architectural question Phase 3 has to answer.
- **Spectrum updating after crystallization.** Once crystallized, spectrum is frozen. Phase 2 doesn't test "re-learning" or "spectrum decay."
- **Causal window** (v8's `learning_window = 2 * birth_tick`). Will revisit in Phase 3 when we have substrate-wide spawn dynamics that produce non-zero birth ticks.
- **Adaptive top-K** (covering target fraction of observed). The fixed K=3 keeps the test deterministic.

---

## File changes

```
experiments/135_semantic_substrate/
├── cell.py                    # MODIFY: add State enum, fields, observe(), crystallize(); modify classify(); add __post_init__
├── phase2_test.py             # CREATE: 5-cell deliverable
├── tests/
│   └── test_cell.py           # MODIFY: add tests for observe(), crystallize(), state transitions
├── phase2_run.log             # CREATE (after run): captured output
└── RESULTS_phase2.md          # CREATE (after run): outcome documentation
```

No changes to `substrate.py`, `fixture.py`, or any Phase 1 deliverable file.

---

## Estimated work

~1 hour. Smaller scope than Phase 1: just an additive feature on `Cell`, no canvas changes.

- 15 min: extend `cell.py` with State, fields, observe(), crystallize()
- 15 min: add unit tests for new behaviors
- 15 min: write phase2_test.py deliverable
- 15 min: run + write `RESULTS_phase2.md`
