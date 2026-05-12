# Experiment 135 Phase 1 — Design

**Status:** Design settled 2026-05-01. Ready to implement.
**Supersedes:** Phase 1 sketch in `README.md` (which assumed an RGG substrate and a direct trie-memory port — both abandoned in this brainstorm).

---

## Divergence from README scaffolding

Yesterday's `README.md` proposed Phase 1 as "port trie-memory's classifying-trie node to a 3D RGG of ≥10⁴ cells." Today's brainstorm settled on a different, smaller, more honest Phase 1:

- **No RGG, no 3D.** Substrate has pure topology, no geometric position. Geometry is a seed-time scaffold; it doesn't live in the dynamics.
- **No port from trie-memory.** Fresh synthesis. Trie-memory's mechanic is the inspiration, but the implementation is built from scratch in Python so we don't inherit Rust assumptions or hierarchical-tree topology.
- **Small structured seed, not 10⁴ cells.** Phase 1 fixture is a K=6 ring with preset spectra — directly comparable to Exp 134's K=6 fixture, just under the new mechanism.
- **No learning yet.** Spectra are preset. Learning (v8 causal-window style) is a Phase 2 question.
- **No DepositToken / RGB / density / Hamming distance.** Tokens are opaque integer labels. Substrate uses set membership (`==` only) — no math.

Why the change: pulling on the brainstorming threads exposed several places where the README scaffolding was importing assumptions we hadn't earned (geometric embedding, depth-based thresholds, RGB structure). Stripping them out left us with a substrate that is much closer to the RAW 133 / RAW 113 / RAW 044 minimum and much further from RGG. Worth being explicit that we're testing a different substrate than 128 v11, not the same one.

---

## Phase 1 question

**Does a coherent K=6 ring pattern persist under deposit pressure when the substrate runs the reactive-canvas + topology-growth mechanism?**

Concretely: when we feed a stream of half-known / half-novel tokens into one ring cell, does the ring (a) stay coherent, (b) grow honest substructure on novelty, (c) saturate or break?

This is Exp 134 Phase 1's question (does the seed pattern survive renewal?) re-asked under the RAW 133 mechanism (semantic differentiation at every cell, growth on Unknown).

---

## Substrate ontology

The substrate is a directed multigraph that **grows over time**. There is no fixed cell count, no fixed edge count, no geometric embedding.

### Cell

```
Cell:
  spectrum:  set[int]                # opaque labels this cell classifies as Same
  connectors: list[Cell]             # other cells this one is linked to (round-robin order)
  pending:    queue[Deposit]         # deposits waiting to be processed
  state:      Idle | Canvasing(...)  # current activity
```

A cell has no position. Its identity is `id(self)` (Python object identity), not a coordinate.

### Connector

A connector is a directed link from cell A to cell B. The link is bidirectional in semantics (either side can canvas the other) but stored on each side independently — so when A spawns a new child C, both A and C get the connector entry.

No edge weights, no labels, no decay.

### Deposit

```
Deposit:
  token:        int                 # opaque label
  predecessor:  Cell | None         # the cell that just forwarded this to its current holder
  origin:       Cell                # original injection cell (functional: triggers origin-loop spawn)
  age:          int                 # ticks since injection (for diagnostics)
```

**`predecessor`** gives a forwarded deposit *directional momentum*: when a cell canvases, it skips the predecessor. Without this, a deposit traversing a ring would oscillate between two cells indefinitely (each cell, on receiving an all-Different canvas, would forward back to where it came from).

**`origin`** is functional, not just diagnostic. If a deposit walks the substrate and returns to its origin cell (with a non-None predecessor), that means it has explored a closed loop without finding a `Same` or `Unknown` host. Spawn at origin — the substrate had no slot for it, so grow one. This terminates the case where every cell in the existing structure is populated and none classifies the deposit as Same.

Tokens are integers used **only for equality**. The substrate never does `<`, `>`, `+`, `-`, `abs`, distance, or thresholds on token values. Tokens are conceptually opaque labels; using `int` is convenience.

---

## Mechanism

### Consume-canvas-route-spawn rule

When a cell C holds a deposit D with token t, predecessor P, and origin O (P is `None` for fresh-injected deposits; O is the injection cell):

1. **Self-check.** If `t in C.spectrum` → C consumes D. Done.

1a. **Origin-loop check.** If `C is O` and `P is not None` → D has returned to its origin after walking the substrate. C spawns a new child cell with `spectrum = {t}` and `connectors = [C]`. C appends the new child to its own connectors. D is consumed. (This handles the case where every existing cell has a populated, non-matching spectrum — the substrate has no Unknown slot anywhere along D's traversal path.)

2. **Canvas non-predecessor neighbors round-robin.** C asks each connector N (excluding P) one at a time, starting from `C.next_canvas_index`:
   - Send query `(t, C)` to N. (1 tick.)
   - N classifies: `Same` (`t in N.spectrum`), `Different` (`N.spectrum` non-empty, `t not in N.spectrum`), or `Unknown` (`N.spectrum` empty).
   - N sends response back to C. (1 tick.)
   - **Total per neighbor: 2 ticks.**
   - If N responded `Same` → C forwards D to N (D's predecessor becomes C). Canvas complete.

3. **Decide at canvas exhaustion** (no `Same` found among non-predecessor neighbors):
   - **If any responder said `Unknown`** → C **spawns a new child cell** with `spectrum = {t}` and `connectors = [C]`. C appends the new child to its own connectors. D is consumed (it created the cell that classifies it).
   - **Else if any responder said `Different`** → C forwards D to the first such responder (D's predecessor becomes C). The deposit walks forward through the substrate.
   - **Else (canvas was empty — C had no non-predecessor neighbors)** → C **bounces D back to its predecessor P** (D's new predecessor becomes C). P will then re-canvas, this time skipping C, and pick a different first-Different responder (or eventually trigger origin-loop spawn). This handles the leaf case: a degree-1 cell that just received a Different-forward has no other place to send the deposit, so it returns it.

**Why empty-canvas bounces instead of spawning:** Initial design had empty canvas spawn directly at C. Phase 1 implementation surfaced a cascade bug: every spawned child starts as a leaf (one connector back to its creator). When a deposit gets Different-forwarded to a leaf, the empty-canvas-spawn rule fires — creating a new leaf, which the next Different-forward also empty-canvas-spawns on, etc. Result: ~5 expected spawns balloon to ~27, scattered across many cells. Replacing empty-canvas-spawn with empty-canvas-bounce keeps the deposit walking the substrate; novel tokens now reliably trigger origin-loop spawn at origin (one spawn per distinct novel token, all parented to origin), which matches the design intent.

If `predecessor is None` and canvas is empty (C has no connectors at all), spawn at C (degenerate fallback — only relevant for an isolated cell, never happens in Phase 1's K=6 ring fixture).

### Why the asymmetry between Different and Unknown

- `Same` = "I match. Hand it over." → forward, terminate.
- `Different` = "I have an opinion, and it's not this." → forward (let D walk past me, looking for Same elsewhere).
- `Unknown` = "I am a blank slot, write me." → spawn a new home for D rather than overwrite a populated cell.

Spawning happens on Unknown (or empty-canvas) because that's the substrate's signal that it has *blank capacity*. Spawning on Different would overwrite an existing pattern — wrong direction. Forwarding through Different lets the deposit traverse the substrate looking for its proper home.

### Why the predecessor-skip

Without it, two-degree cells (like every cell in the K=6 ring) get into oscillations: A canvases, all neighbors say Different, A forwards to B; B canvases, A says Different, A is the only non-B neighbor, B forwards back to A. Forever.

Skipping the predecessor gives the deposit one-step memory of where it just came from. That's enough to walk a ring (A → B → C → ...) without backtracking, while still allowing the deposit to revisit a cell along a different path (since "predecessor" is only the immediate prior cell, not the full visited history).

### Concurrency

A cell processes one deposit at a time. While `state == Canvasing(...)`, additional deposits queue in `pending`. After current canvas resolves (consume / forward / spawn), the cell pops the next pending deposit and begins a new canvas next tick.

This means high-traffic cells develop queues — that's an interesting property to measure, not a bug.

### Tick semantics

The substrate runs on integer ticks. At each tick:
- All in-flight queries advance one step (sent → received, or received → response sent).
- Each cell that just received a response decides next action (continue canvas, terminate on Same, spawn on origin-loop / Unknown / empty-canvas, or forward on first-Different).
- Each idle cell with non-empty `pending` pops a deposit and starts a new canvas.
- The injector (Phase 1 fixture) emits a deposit every 15 ticks (see Phase 1 fixture below).

No parallelism inside the substrate. Order of cell-update within a tick is deterministic (sorted by `id(cell)`) so runs are reproducible.

---

## Phase 1 fixture

### Initial substrate: K=6 ring

```
c0 — c1 — c2 — c3 — c4 — c5 — c0   (ring)
```

Six cells. Each cell `c_i` has:
- `spectrum = {i}`           (one label, the cell's "own" token)
- `connectors = [c_{i-1 mod 6}, c_{i+1 mod 6}]`
- `pending = []`
- `state = Idle`

Tokens 0..5 are the "known" alphabet. Tokens ≥ 6 are "unknown."

### Injection

A single injector emits one deposit every 15 ticks into `c0` (always the same entry cell).

Each deposit's token is drawn from a seeded RNG:
- 50% probability: known token, sampled uniformly from `{0, 1, 2, 3, 4, 5}`.
- 50% probability: unknown token, sampled uniformly from a fixed unknown alphabet `{6, 7, 8, 9, 10}` (5 distinct unknowns).

Two design notes:

- **Why a small unknown alphabet (not unique-per-injection):** With `origin-loop spawn`, every distinct unknown token spawns exactly one child at `c0`. A small fixed alphabet means after the first ~5 distinct unknowns are seen, subsequent unknown injections find `Same` in already-spawned children — so we measure both the *initial spawn* behavior AND the *routing-into-spawned-children* behavior in one run. With unique-per-injection unknowns, we'd only ever see the spawn case (and `c0`'s degree would grow without bound).

- **Why cadence 1/15:** Each canvas takes `2 × (degree − skips)` ticks. `c0` starts at degree 2 (two ring neighbors) and grows to degree 7 (2 ring + 5 spawned children) at steady state. Worst-case `c0` canvas = 14 ticks (when canvasing all 7 neighbors with no skip — the fresh-injection case). Cadence 15 gives `c0` a 1-tick slack at steady state. If saturation forms anyway, that's a measurement; we can sweep cadence later.

### Run length

10,000 ticks → ~666 deposits → ~333 known + ~333 unknown. Of the unknowns, the first ~5 distinct tokens each spawn one child at `c0`; the remaining ~328 are re-injections that should find `Same` in those children.

---

## Measurements

Per-run, capture:

1. **Deposit fate distribution.** How many deposits ended as: `consumed-at-injection-cell` (rare — would only happen if c0's spectrum gains the token, which it can't in Phase 1), `consumed-after-walk` (followed Different-forward chain to a cell that classified Same), `spawned-via-origin-loop` (walked back to origin, triggered origin-loop spawn), `still-in-flight-at-end`.
2. **Hops-to-consumption distribution.** For each consumed deposit, how many forward hops did it take? Expected: known token `i` injected at `c0` takes `min(i, 6−i)` hops (round-robin order matters); spawned-children re-injections take 0 hops past `c0` (immediately Same-classified by a child).
3. **Topology growth curve.** `n_cells(t)` and `n_connectors(t)` sampled every 500 ticks. Expected: `n_cells` rises from 6 to 11 over the first ~75 unknown injections, then plateaus.
4. **Per-cell load.** Final `len(pending)` per cell (queue saturation), and total deposits-handled per cell. `c0` will be the busy cell.
5. **Canvas length distribution.** For each completed canvas, how many neighbors did it ask before terminating? Expected: canvases that find Same terminate early; canvases that exhaust go to full degree.
6. **Ring integrity check.** At end of run: each `c_i` for `i ∈ 0..5` still exists; its spectrum is unchanged; its original 2 ring connectors are still present. (Additional spawned-child connectors on `c0` are expected and counted separately.)
7. **Spawn shape.** Expected shape: 5 new cells, all children of `c0`. Each has spectrum of size 1, connectors of size 1 (back to `c0`). Verify by inspection at end of run.
8. **Tick-by-tick log.** Snapshot every 500 ticks of `(n_cells, n_connectors, n_in_flight, sum(len(pending)) over all cells, max(len(pending)) over all cells)`.

### Phase 1 success criteria

The mechanism passes Phase 1 if:

- **Ring integrity holds.** After 10K ticks, the original 6 ring cells still exist with unchanged spectra (`{i}` for cell `c_i`) and their original ring connectors intact (each ring cell still linked to its 2 ring neighbors). Spawned children may have been *added* to ring cells' connectors; nothing should be *removed*.
- **Known tokens get consumed at the right cell.** Token `i` injected at `c0` should walk the ring to `c_i` and be consumed there. Measurement: of the ~333 known-token deposits, ≥95% terminate by being consumed at the cell whose spectrum matches.
- **Unknown alphabet produces exactly the expected number of spawns.** With unknown alphabet of 5 distinct tokens, exactly 5 new cells should be spawned (each as a child of `c0`, each with spectrum `{u_i}` for the unknown token `u_i` that triggered the spawn). Measurement: `n_spawns == 5` (exact).
- **Re-injected unknowns route into spawned children.** After the first 5 distinct unknowns spawn their children, subsequent unknown injections should be `Same`-classified by the appropriate child and consumed there. Measurement: of the ~328 post-spawn unknown deposits, ≥95% are consumed by spawned children of `c0` (not by ring cells, not still in flight).
- **No livelock.** No deposit walks forever. Measurement: max age (in ticks) of any consumed deposit is bounded (provisionally <50 ticks); `still-in-flight-at-end` count is small (<5% of injected, accounting for in-flight at the time the run terminates).
- **Bounded queueing.** No cell's `pending` queue exceeds a sane threshold over the run. Measurement: `max(len(pending))` across all cells across all ticks should be ≲10. If higher, cadence is too aggressive (parameter issue, not mechanism failure) and we re-run with a larger gap.

The mechanism is interesting (worth deeper investigation) if:

- Ring degrades (cells lose their spectra or connectors). → mechanism is overwriting populated state, design bug.
- Spawn count != 5 (extras or missing). → origin-loop or canvas logic is wrong.
- Queues blow up dramatically (>100 deposits per cell). → back-pressure overwhelms substrate; cadence sweep needed.
- Deposits perpetually in-flight at end of run (>10%). → some deposits walking forever; cycle detection insufficient.

All of these are informative; what we *expect* is "ring persists, fan of 5 spawned children grows off `c0` for the unknown alphabet, all deposits eventually consumed, queues stay shallow."

---

## What Phase 1 enables (Phase 3+ research direction)

**Hop count is the substrate's natural distance measure.** Once Phase 1 confirms that deposits walk the substrate looking for Same (and the hops-to-consumption distribution can be measured), this opens a path that 128 v11 took the long way around to:

- Phase 3+ scenario: a "matter pattern" is a region of many populated cells with overlapping spectra. Deposits originating *near* the pattern (in graph distance) find Same matches in few hops. Deposits originating *far* from the pattern (or with tokens not represented in the pattern) walk further or trigger origin-loop spawns.
- The *density of in-flight deposits* as a function of graph distance from the pattern is a measurable, substrate-native quantity. Its falloff shape would be determined by topology alone — no 3D embedding required.
- If the falloff is inverse-power, this would explain physics' 1/r² *without* needing space to be a pre-existing geometric thing. Radial distance would be "exploration cost through the substrate"; the inverse-power law would be a topological consequence.
- This is the path 128 v11 hinted at on RGG (where r was Euclidean and the substrate carried 3D embedding); doing it on pure topology would earn the radial law from substrate dynamics alone.

The hops-to-consumption measurement (item 2 in Phase 1 measurements above) is the seed of this — a baseline distribution from a trivial fixture before we add the patterns that would let us actually measure radial behavior.

---

## Out of scope for Phase 1

- **Learning** (v8 causal-window — empty spectra crystallizing from observed traffic). Phase 2 question.
- **Decay** (spectra fading without reinforcement). Deferred until recruitment-without-release becomes a problem.
- **Trajectory-as-token** (option C from Q8 — tokens acquire identity by their substrate path, no a-priori labels). The radical RAW 133 commitment; deferred to test in a later phase once the cheaper mechanism is debugged.
- **Patterns that interact** (two seeds, planet + test). Phase 3+.
- **Field-like behavior** (gradients, drift, anything Newton-shaped). Phase 4+.
- **Antimatter / signed spectra.** Phase 6.

---

## File structure

```
experiments/135_semantic_substrate/
├── README.md                  # scaffolding (kept; superseded by this doc for Phase 1)
├── PHASE1_DESIGN.md           # this file — authoritative for Phase 1
├── conftest.py                # pytest sys.path
├── __init__.py
├── cell.py                    # Cell, Deposit, mechanism rule (consume/canvas/spawn/forward)
├── substrate.py               # multigraph driver: tick loop, in-flight queries, cell scheduling
├── fixture.py                 # K=6 ring builder + injector
├── tests/
│   ├── __init__.py
│   ├── test_cell.py           # unit: classify, canvas state machine, spawn, origin-loop
│   └── test_substrate.py      # unit: tick loop, query timing (2 ticks/query), reproducibility
├── phase1_test.py             # deliverable: 10K-tick run + measurements
├── phase1_run.log             # captured output
└── RESULTS_phase1.md          # outcome documentation
```

No `spectrum.py` (set is enough), no `tokens.py` (int is enough), no `tick.py` (substrate.py owns the tick loop). Smaller surface than the README scaffolding planned.

---

## Open questions deferred to later phases

(These were considered and explicitly deferred during the brainstorm, not forgotten.)

- **Q8.C — Trajectory-as-token.** RAW 133's most radical move; replaces a-priori valued tokens with substrate-acquired identity. Phase 1 uses opaque labels (Q8.A); Q8.C remains the honest target.
- **Spectra learning** (v8 causal-window). Phase 1 uses preset spectra; Phase 2 should add the Learning→Crystallized state machine.
- **Decay / release**. Phase 1 is append-only on connectors and spectra. If recruitment-without-release becomes a problem (runaway growth), add decay.
- **Most-similar canvas ordering** (Q5.C). Phase 1 uses round-robin (Q5.A). If round-robin produces too many bounces or wasted canvases, similarity-cached ordering is a tunable.
- **Mix ratios and cadence** (Q9 sub-questions). Phase 1 fixes 50/50 mix and 1-deposit-per-15-ticks. Sweep later.

---

## Estimated work

One focused session for Phase 1 implementation: ~3 hours.

- 30 min: scaffold (cell.py, substrate.py, conftest, fixture)
- 60 min: implement consume-canvas-spawn-bounce mechanism with TDD on cell.py
- 30 min: implement tick loop with TDD on substrate.py
- 30 min: write phase1_test.py, run it, capture log
- 30 min: write RESULTS_phase1.md

If the mechanism behaves on first run, that's the whole session. If not, debugging extends.
