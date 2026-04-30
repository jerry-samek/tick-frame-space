# Experiment 135 — The Semantic Substrate

**Theory:** [`docs/theory/raw/133_semantic_substrate.md`](../../docs/theory/raw/133_semantic_substrate.md) (RAW 133, written 2026-04-30)
**Status:** Folder scaffolded. Design specified. No implementation yet.

---

## What this experiment is

The synthesis of three earned-but-disconnected primitives:

1. **Continuous propagation on RGG** — Exp 128 v11's substrate (earned 1/r² gradient, Newton orbits, exact tangential Schwarzschild, time dilation, equivalence principle). Untouched here.
2. **Renewal patterns as honest entities** — Exp 134 Phase 1's commitment (Doc 28 operational, sign-blind matter/antimatter from substrate signedness). Pattern membership is dynamic; identity is renewal-cycle, not cell-set.
3. **Same / Different / Unknown classification at every node** — RAW 113 made operational by `W:/workspace/trie-memory` (163 passing tests, MCP server, content-addressable path keys, Learning→Crystallized state machine, two-mechanism architecture).

RAW 133 argues these are the same primitive viewed from different angles, and that **the substrate's missing piece is semantic differentiation at every node**. Without it, Exp 132 Phase 2/2A.5/2A.2 saturated uniformly across 1000× variation in `load_coefficient`. With it, the saturation should resolve into structure: gradients, recruitment, drift, observation, matter-antimatter — all from one mechanism.

---

## Why this experiment is *cheaper* than RAW 133's original Phase 1 sketch

Initial RAW 133 Phase 1 was "validate spectrum primitive with 2 cells." That work is **already done at scale in trie-memory** (163 tests, deployed as MCP server). Phase 1 of Exp 135 is therefore:

> **Port trie-memory's classifying-trie node primitive to a substrate cell datatype on a 3D Random Geometric Graph. Demonstrate that Same/Different/Unknown + Learning→Crystallized works at substrate scale (≥10⁴ cells, RGG topology, real-time-tick dynamics).**

Not "build it from scratch." Port + validate at substrate scale.

---

## Predecessor experiments

| Exp | What it earned | What it contributed to RAW 133 |
|---|---|---|
| **128 v11** | 1/r² gradient (slope −1.968), Newton orbits, exact tangential Schwarzschild, time dilation, equivalence principle. All on 3D RGG with pure-real propagation. | The substrate-physics primitive: RGG topology + propagation rule. Use unchanged. Failed at radial g_rr — spectrum-driven anisotropy may close that gap. |
| **131_a** (lineage_substrate) | (Falsified) | Negative result: lineage tree + local conductance flow doesn't recover Newton. Topology-without-propagation isn't enough. |
| **131_b** (anisotropic_connectors) | Per-edge Schwarzschild radial (ratio 1.01 at r=5) | Built-in connector anisotropy gives radial profile but fails horizon scaling (r_s ∝ M off by factor 0.19–0.58). RAW 133 reading: anisotropy from spectrum-classification is dynamic, scales with mass. |
| **133** (closed_loop_substrate) | Exact integer conservation; ρ ∝ r⁻¹ with sink | Strict closed-loop integer dynamics give wrong exponent (−0.65 vs Newton's −2). Test patterns dissipate before drifting. |
| **134 Phase 1** (pattern_coherence) | Bit-identical fixed-point patterns over 10K cycles, sign-blind matter/antimatter | The entity-renewal primitive: cycle structure as identity. Doc 28 operational. Use unchanged in vacuum case; refined in interaction case. |
| **134 Phase 2** | Substrate strict locality across empty cells; same-sign contact = decoherence | Strong negative: gravity-at-distance unearnable without long-range mechanism. RAW 133's leak-bearing patterns answer this. |
| **132 Phase 1** (grow_until_observed) | Sustained K=4 capacitor cycle (5K cycles) under three-layer mechanism | First combination of charging + adaptive threshold + connector load. Validated in vacuum. |
| **132 Phase 2 / 2A.5 / 2A.2** | Honest negative: substrate saturation is **structural**, not parametric | The non-semantic special case can't produce gradient. Empirical evidence that semantic differentiation is needed. |

## Operational precedent (the implementation we port from)

**[trie-memory](file:///W:/workspace/trie-memory)** — `W:/workspace/trie-memory`. Rust, 163 passing tests across 19 test files, MCP server (stdio + SSE), 5 honest-agent scenarios validated end-to-end.

Key files we'll port from:
- `src/trie/node.rs` — `Node`, `Classification` enum (Same/Different/Unknown), `NodeState` enum (Learning/Crystallized), `params_for_depth(depth) → (crystallization_threshold, spectrum_max_size)`, `classify`, `observe`, `consume`, `crystallize`
- `src/trie/write.rs` — `route()` with maturity gate, delta encoding
- `src/store/concept.rs` — `Concept`, `Binding`, `ConceptStore` for temporal co-occurrence binding
- `src/store/layer.rs` — `MemoryLayer`, `LayerStore` for tick-timeline bookkeeping

Not all of trie-memory ports cleanly:
- trie-memory uses a **hierarchical trie** (parent→children); Exp 135 uses a **3D RGG** (each node has ~6 face-adjacent neighbors, no privileged parent)
- trie-memory's "child" routing maps onto RGG's "neighbor" routing, but the depth-dependent threshold parameters need rethinking (RGG cells don't have a clean "depth from root")
- trie-memory is integer-only; RAW 133 commits to staying integer-only too (good)
- trie-memory has wall-clock timestamp + tick number; Exp 135 needs ticks only

Provisional adaptation: replace trie-memory's depth-based parameters with **connectivity-based** parameters (high-degree RGG nodes get broader spectra and slower crystallization; low-degree nodes get narrower/faster). This preserves the hierarchy intuition (broad recognition early, specific recognition deep) on a graph without explicit depth.

---

## Phases

Per RAW 133 §11, modified for the cheaper Phase 1 from §10.6:

### Phase 1 — Port the classifier primitive to RGG cells

- Define `Cell` datatype with: position (x, y, z), spectrum (Vec<u8> or Vec<u16>), state (Learning|Crystallized), buffer, visit_count, threshold, charge_level
- Build a 3D RGG (sprinkle N points in unit cube, connect within radius r)
- Implement the consume-reemit-classify rule: incoming token → classify → Same consumes, Different routes (to which neighbor?), Unknown reemits
- Adapt depth-dependent thresholds to **connectivity-dependent** thresholds (parametrized by node degree, not depth)
- Validate: send token streams to a single cell, watch crystallization; verify Same/Different/Unknown classification at substrate scale; verify content-addressable path keys
- **Goal:** RGG-of-classifier-cells produces same Same/Different/Unknown semantics as trie-memory does at hierarchy

### Phase 2 — Temporal-binding pattern formation

- Multiple cells crystallize on overlapping token streams in the same tick window
- Cells with aligned spectra and in-phase firings form a coherent renewal cycle (a pattern)
- Validate: vacuum coherence — a small seed pattern (K=4) sustains itself when no external input
- This is essentially Exp 134 Phase 1 with semantic spectra. Should reproduce 134's bit-identity (or close).

### Phase 3 — Recruitment and release dynamics

- Single seed pattern in a substrate region with variable ambient flux (more flux on one side, less on the other)
- Observe: cells in high-flux region get recruited (their spectra align with the seed's tokens); cells in low-flux region don't
- Pattern grows toward the high-flux side; centroid shifts
- This is observer-side drift mechanism from RAW 133 §4.3

### Phase 4 — Two-pattern interaction

- Planet seed (large) + test seed (small), both same-sign
- Planet absorbs ambient flux, recruits cells, grows; leak from planet biases test seed's spectrum
- Test seed's centroid drifts toward planet
- Compare drift profile to Newton's 1/r²
- This is RAW 132 Phase 2's question, finally answered

### Phase 5 — Quantitative GR fit

- Larger planet, measure threshold(r) and connector_load(r) profiles
- Fit to Schwarzschild metric components
- Test radial vs tangential anisotropy (closes 128 v11 Phase 6's open question)

### Phase 6 — Matter-antimatter annihilation

- Two seeds with opposite-sign spectra
- Bring them into contact
- Observe: decoherence cascade at boundary, energy release as Unknown reemits
- Tests RAW 133 §9's prediction

### Phase 7+ — Multi-pattern, real physics

Three-body, orbital mechanics, possibly atomic structure. Speculative; gated on Phase 5+ producing meaningful signal.

---

## Phase 1 scope (the next session's target)

Concrete deliverable: a working substrate-cell prototype on RGG that classifies incoming tokens as Same/Different/Unknown. Not a full physics simulation — just the recognition primitive at substrate scale.

### Phase 1 components needed

1. **`substrate.py`** — RGG construction (sprinkle N points, connect within radius), node degree calculation, neighbor lookup
2. **`cell.py`** — `Cell` dataclass + classify/observe/consume/crystallize methods (port from `trie-memory/src/trie/node.rs`)
3. **`spectrum.py`** — `Spectrum::crystallize_from`-equivalent (frequency-based set selection)
4. **`tokens.py`** — `DepositToken` datatype (initially borrow trie-memory's 4-bit-density + 4-bit-RGB, simplify if needed)
5. **`tick.py`** — per-tick driver: deposits in transit propagate; cells classify arriving tokens; crystallization triggers
6. **`fixture.py`** — initial setups: single cell, ring of N cells, RGG cluster
7. **`tests/`** — unit tests proving classification works at substrate scale
8. **`phase1_test.py`** — deliverable: validate Same/Different/Unknown semantics across ≥10⁴ cells

### Phase 1 success criterion

For a cell `c` with crystallized spectrum `S`:
- An incoming token `t ∈ S` is classified as Same and consumed (`c.visit_count` increments)
- An incoming token `t ∉ S` but within Hamming distance ≤ 1 is classified as Different and routed to a (specific) neighbor
- An incoming token `t` far from `S` is classified as Unknown and reemitted to all neighbors

Plus: across many cells receiving overlapping token streams, the resulting spectrum-graph is reproducible (same input → same crystallization pattern).

### Phase 1 success metric

Compare against trie-memory's empirical results:
- Crystallization happens within ~100–250 token observations per cell (matches trie-memory's depth-0 threshold of 256)
- Path keys (FNV hash of spectrum) are stable across runs
- Same/Different/Unknown classifications match trie-memory's behavior on identical input streams

---

## Phase 1 explicitly does NOT do

- No physics dynamics (no gradient, no field, no drift, no Schwarzschild)
- No renewal patterns (cells classify tokens; they don't yet form coherent cycles)
- No two-pattern interactions
- No GPU acceleration (correctness first; performance later)
- No causal-cone-engine integration
- No matter/antimatter — single-sign tokens only

These are Phases 2–6.

---

## File structure (planned)

```
experiments/135_semantic_substrate/
├── README.md                  # this file
├── conftest.py                # pytest sys.path fix
├── __init__.py
├── substrate.py               # RGG + neighbor topology
├── cell.py                    # Cell datatype + classify/observe/consume/crystallize
├── spectrum.py                # Spectrum primitive (frequency-based crystallization)
├── tokens.py                  # DepositToken
├── tick.py                    # Per-tick driver
├── fixture.py                 # Test fixtures (single cell, ring, RGG cluster)
├── tests/
│   ├── __init__.py
│   ├── test_substrate.py
│   ├── test_cell.py
│   ├── test_spectrum.py
│   ├── test_tokens.py
│   └── test_tick.py
├── phase1_test.py             # Phase 1 deliverable
├── phase1_run.log             # Captured output (when run)
└── RESULTS_phase1.md          # Outcome documentation
```

---

## Open questions (carried into Phase 1 design)

1. **What's "Different" precisely on RGG?** trie-memory routes Different to a specific child (well-defined in hierarchy). On RGG, "child" is ambiguous — every neighbor is equivalent. Provisional: route Different to the neighbor whose spectrum is most similar (smallest spectrum-difference). Tunable.
2. **What replaces depth-dependent thresholds?** trie-memory uses depth from root. RGG has no root. Provisional: use **connectivity degree** — high-degree cells (near the substrate's center, more neighbors) get broader spectra and slower crystallization; low-degree cells (boundary, fewer neighbors) get narrower spectra and faster crystallization.
3. **Token shape?** trie-memory's `DepositToken` is 4-bit density + 4-bit RGB = 16 bits. RAW 133 doesn't commit to a specific shape. Phase 1 uses trie-memory's directly; later phases may need richer tokens for matter-vs-antimatter, etc.
4. **Decay / release?** trie-memory is append-only. RAW 133 may need spectrum decay for release dynamics. Provisional Phase 1 commitment: append-only (no decay). Add decay in Phase 2+ if recruitment-without-release leads to runaway growth.

---

## Pick-up notes for next session

When you come back:

1. **Read RAW 133** (`docs/theory/raw/133_semantic_substrate.md`) if it's been more than a day — refresh the synthesis.
2. **Look at trie-memory** (`W:/workspace/trie-memory/src/trie/node.rs`) — this is what we're porting. Specifically `Node`, `Classification`, `NodeState`, `params_for_depth`, classify/observe/consume/crystallize.
3. **Brainstorm Phase 1 design** — questions in §"Open questions (carried into Phase 1 design)" above. Decide on:
   - Different-routing rule on RGG
   - Connectivity-vs-depth thresholds
   - Token shape (port directly or simplify)
   - Decay (or not)
4. **Implement Phase 1** — small TDD cycle, scaffold from `experiments/132_grow_until_observed/` style. Layer cell.py / spectrum.py / tokens.py / tick.py.
5. **Run + RESULTS** — same pattern as 132 Phase 1 / 134 Phase 1.

Estimated Phase 1 work: 1 focused session (2–4 hours). Phase 2 would be next session after.

---

## Status

- 2026-04-30 evening: experiment folder created. README.md drafted (this file). RAW 133 written + integrated trie-memory as §10.6. Stopping point for the day.
- Next session: brainstorm Phase 1 design (open questions above) → implement → run.
