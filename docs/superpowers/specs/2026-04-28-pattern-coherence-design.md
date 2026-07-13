---
title: Pattern Coherence (Experiment 134)
date: 2026-04-28
status: spec — pending Phase 1 implementation
branch: feature/exp-134-pattern-coherence (to be created)
predecessor: experiments/133_closed_loop_substrate (closed 2026-04-26)
---

# Experiment 134: Pattern Coherence (Phase 1)

## Motivating principle

> "What is easier than redrawing myself again and again."

A pattern in tick-frame substrate is a configuration of cells that *exists by being continuously rerendered*, not by being preserved as data. In vacuum (no external γ field), the pattern's full energy budget per K-tick cycle goes into exact self-redraw. The pattern is therefore a *fixed point* of a renewal rule — it persists indefinitely, by construction, without parameter tuning.

This principle, attributed to Doc 28 (Temporal Surfing) and Doc 29 (Imbalance), is operational and falsifiable: either we can construct a discrete-substrate renewal rule whose fixed points are localized clusters, or we cannot.

## Goal (Phase 1)

Construct a sign-blind transactional renewal rule on a discrete signed-integer 3D substrate, and exhibit at least three pattern fixtures (F1, F2, F3) that are exact fixed points under that rule for arbitrary tick counts.

## Background

### Predecessor experiments

- **Exp 133 (closed 2026-04-26)** — closed-loop integer hold-and-fire substrate. Conservation worked exactly. Source+sink yielded ρ ∝ r⁻¹ but smoothed force-law slope was −0.65, not Newton's −2. Test patterns dissipated within ~400 ticks under any rule variant. The Doc 28 commitment failed *operationally* at the entity scale: cell-level renewal worked, entity-level renewal did not, because the rule had no design that held a pattern coherent.
- **Exp 51_v10_on56_v18 v2 (2026-02-11)** — V18 canvas substrate. Single-cell test particles with float velocity, leapfrog integration, and trilinear-interpolated gradient produced 5/6 stable Keplerian orbits with dE/E0 = +0.000. **But:** these were Newtonian point particles riding on a substrate canvas, not patterns made of substrate. The substrate side was honest (γ field from accumulated paint, no PDE); the orbiter side was hand-coded Newtonian mechanics.

### The honest gap

The April 17 memory flagged "pattern self-coherence" as the real frontier. Exp 133's closure named the same gap from the other side: *even with a substrate that produces Newton's force, our test patterns dissipate too fast to feel it.*

Phase 1 of Exp 134 closes the **minimum honest version** of this gap: not a moving pattern, not a pattern in a field, just a pattern that exists in vacuum for arbitrary T because the renewal rule says so.

### Theoretical commitments

| Source | Commitment |
|---|---|
| Doc 28 (Temporal Surfing) | Identity is renewal, not preservation. Each tick the pattern is reconstructed from the canvas. |
| Doc 29 (Imbalance) | Matter/antimatter asymmetry follows from sign symmetry of substrate, not from special rules. |
| User / RAW theory | Only another γ field can decohere a pattern. Vacuum coherence is automatic. |
| RAW 130 ("rotates because it consumes") | Each tick has a budget. In vacuum, budget = exact self-redraw cost. External γ diverts budget. |
| User / RAW theory | Renewal is **transactional**: a K-cell pattern requires exactly K ticks per refresh cycle. |

## Section 1: Substrate and pattern shape

### Substrate

3D integer lattice. Each cell `(x, y, z)` carries one **signed integer** γ value; default 0.

**Decay** (every tick, every nonzero cell):
```
γ -= sign(γ)
```
Symmetric drift toward 0. Cells at γ = ±1 expire to 0 this tick.

**Paint** (signed, additive):
```
γ[cell] += amount   # amount is signed integer
```
Same channel for matter and antimatter — sign of the paint determines pattern type. Overlap of opposite signs cancels naturally (integer addition); annihilation requires no special rule.

**No diffusion, no smoothing, no PDE.** The substrate's only intrinsic dynamic is decay.

### Pattern fixtures (Phase 1)

A pattern of period K is a closed cycle of K cells where each consecutive pair (including last↔first) is **face-adjacent** on the cubic lattice. Three test fixtures, ascending difficulty:

| ID | K | Shape | Cells (z = 0) | Purpose |
|----|---|-------|----------------|---------|
| **F1** | 4 | 2×2 square | (0,0,0), (1,0,0), (1,1,0), (0,1,0) | Minimum viable fixture. Smallest K for which the rule is non-degenerate (see "fixture geometric constraints" below). |
| **F2** | 6 | 2×3 rectangle perimeter | (0,0), (1,0), (2,0), (2,1), (1,1), (0,1) at z=0 | Larger cycle; introduces an *internal* lattice adjacency (the bridge (1,0)↔(1,1)) that is not a cycle adjacency. Tests that the rule's uniqueness is robust to non-cycle pattern adjacencies. |
| **F3** | 8 | 3×3 hollow ring | perimeter of 3×3 grid at z=0; interior (1,1) excluded | Non-trivial K, all pattern adjacencies are cycle adjacencies (no internal bridges). Confirms rule scales to larger K. |

All three are designed to be **exact fixed points by construction**. The Phase 1 test verifies the implementation realizes that.

#### Fixture geometric constraints

For Step B to uniquely identify the cell to paint, every Phase 1 fixture must satisfy:

> For every pair of cycle-positions X, Y at cycle-distance 2, all lattice cells that are face-adjacent to **both** X and Y must themselves be pattern cells.

F1, F2, F3 each satisfy this. Future fixtures designed differently may not, in which case the rule needs supplementing — flagged as a Phase 1.5 concern.

#### Why K = 2 is excluded

K = 2 is degenerate: the max-|γ| cell and the min-positive-|γ| cell are the same cell after Step A (only one cell remains nonzero). Step B's two-condition lookup collapses to one condition, and uniqueness fails. The smallest non-degenerate Hamiltonian cycle on the cubic lattice with face-adjacency has K = 4.

### Acknowledged compromise: geometry is hand-designed

Shapes F1–F3 are predetermined. We are *not* testing whether the substrate spontaneously generates coherent shapes; we are testing whether a renewal rule preserves a chosen shape exactly. Spontaneous shape generation is a Phase 1.5 / Family-2 question (cellular-automaton still-lifes on signed substrate) and explicitly deferred.

## Section 2: The renewal rule (sign-blind, transactional)

### Per-tick procedure

**Step A — Decay** (every nonzero cell):
```
γ[cell] -= sign(γ[cell])
```

**Step B — Paint** (one event per tick):
1. Find `c_max` = the cell with maximum `|γ|` anywhere on the canvas.
2. Find `c_min` = the cell with minimum *positive* `|γ|` anywhere on the canvas.
3. Find `c₀` = the unique cell with `γ = 0` that is face-adjacent to **both** `c_max` and `c_min`. (Phase 1 fixtures are designed so this `c₀` exists and is unique — see Section 1's geometric constraints.)
4. Set `γ[c₀]` to `sign(γ[c_max]) × (|γ[c_max]| + 1)`.

**No hidden state.** The rule is fully a function of canvas content. Pattern period K is encoded in the canvas itself: after Step A, max |γ| = K − 1, min positive |γ| = 1, and the unique γ = 0 cell common to both their face-neighborhoods is the cell to paint.

### Sign-blindness and antimatter emergence

The rule reads sign from cells, never from configuration. Initialize positive seed → matter pattern. Initialize negative seed → antimatter pattern. **Same rule, both worlds.** Antimatter is not engineered into the rule; it is the natural CP-mirror of matter under sign-symmetric substrate arithmetic.

### Transactional renewal

The unit of "the pattern existing for one moment" is **one full K-tick cycle**, not one substrate tick. A K = 50 pattern requires *exactly* 50 ticks to complete one rerender. The rule cannot refresh faster (it has only one paint event per substrate tick); the pattern cannot survive skipping any cell (any skipped cell decays to 0 and breaks the cycle).

**Implication:** larger patterns are intrinsically slower. K is the pattern's natural time unit. A K = 4 pattern lives 12.5× faster than a K = 50 pattern relative to substrate time. This is a scale-dependent timescale dropping out of the substrate for free; it connects directly to mass / time-dilation arcs in Phase 2 and beyond.

### Why this is a fixed point in vacuum (proof sketch)

**Invariant:** at any tick, the K pattern cells carry γ values that are a sign-consistent permutation of `{±1, ±2, …, ±K}`, arranged so that consecutive cycle positions hold values differing by exactly 1.

- Step A subtracts 1 from each magnitude → multiset becomes `{0, 1, …, K−1}`. Exactly one cell is at 0 (the just-expired cell at the cycle's "tail").
- Step B finds `c_max` (now at K−1, the most-recently-painted cell, located one cycle step ahead of the just-expired cell) and `c_min` (now at 1, located one cycle step behind the just-expired cell). The unique γ = 0 cell face-adjacent to both is the just-expired cell itself. Step B paints it at magnitude K, sign matching `c_max`.
- Multiset returns to `{1, 2, …, K}`. Cycle ordering is preserved: the freshly painted cell's value (K) is exactly one greater than `c_max`'s value (K−1), and one less than nothing (it is the new "head" of the cycle).

Therefore, after one tick, the pattern's cell set is unchanged, the multiset of γ values is unchanged, and the cycle ordering is unchanged. After K ticks, the canvas state is bit-identical to K ticks earlier. ∎

### Bootstrap

Seed the canvas at tick 0 with the K cycle cells pre-loaded as `{±K, ±(K−1), …, ±1}` in cycle order (sign chosen by experimenter — positive for a matter pattern, negative for antimatter). Step A + Step B start firing at tick 1. No special-case "initialization phase".

## Section 3: Success criterion, falsification, deliverables

### Success criterion (binary)

For each fixture F1, F2, F3:

> **Canvas state at tick (B + n·K) is bit-identical to canvas state at tick (B + K)**, for all n ∈ [1, 10000].

Where B is the bootstrap end-tick and K is the fixture's period. "Bit-identical" means every cell's γ value matches exactly. **No tolerance, no approximation** — the theoretical claim is *exact* invariance, so the test is exact equality.

The check is **transactional**: state is sampled at K-tick boundaries, framed as "the pattern's renewal transaction completed correctly," not "the pattern looks the same at random samples."

Implementation: hash the canvas state at tick (B + K), then at every subsequent (B + n·K) re-hash and compare.

### Falsification modes

- **Drift:** state at (B + n·K) differs from state at (B + K) for any n. Even a single bit difference fails the criterion. Record the fixture, the tick, and which cells diverged — that is itself informative.
- **Wedged state:** Step B cannot find a γ = 0 cell face-adjacent to both `c_max` and `c_min`. Means the fixture geometry is broken or bootstrap left an unrecoverable canvas.
- **Non-uniqueness:** Step B finds multiple γ = 0 cells face-adjacent to both `c_max` and `c_min`. Means the fixture violates the geometric constraint in Section 1 and the rule needs supplementing.

If any fixture fails Phase 1, we record the failure and either fix the fixture or revisit the rule. We do **not** move to Phase 2 with a partially-working Phase 1.

### Deliverables

```
experiments/134_pattern_coherence/
├── README.md            # quick overview, run instructions
├── substrate.py         # sparse 3D signed-integer canvas, decay primitive
├── rule.py              # Step A, Step B, bootstrap helper
├── fixtures.py          # F1 (2×2 square, K=4), F2 (2×3 perimeter, K=6), F3 (3×3 ring, K=8)
├── phase1_test.py       # pytest: bit-identity over 10000 cycles
└── RESULTS.md           # written after run; pass/fail + hashes + anomalies
```

### Implementation constraints

- Python (consistent with project).
- Sparse dict-based canvas (matches v18 style; only nonzero cells stored).
- Integer-only (Python int sufficient at K ≤ 50; no BigInt needed).
- 3D-native, but Phase 1 fixtures planar (z = 0).
- No vectorization (single pattern, single paint per tick — trivial perf).
- No matplotlib; pytest assertions are the deliverable.

### What Phase 1 explicitly does NOT do

- No planet field, no external γ source.
- No drift measurement, no orbital mechanics, no annihilation test.
- No multi-pattern simulation (one pattern at a time).
- No visualizations beyond optional dev-time ASCII canvas dump for sanity inspection.
- No performance optimization.

### Estimated scope

Single session, a few hours. Phase 1 is small by design: a precise, falsifiable test of a construction. If it passes cleanly, we move to Phase 2 (planet contrast issue + drift mechanics). If it fails, the failure is informative on its own.

## Section 4: Phase 2/3 forward-compat

### Phase 2 (drift under same-sign external γ) — kept openable, not built

The "background contrast" issue is the load-bearing Phase 2 design decision. When a planet field is added, background γ may equal or exceed pattern γ at single-cell scale, and Step B's `max |γ|` lookup may misfire.

Three resolutions, all compatible with Phase 1 substrate:

- **R1: Make K large.** Pattern γ values O(1000), planet γ at orbital radius O(100); Step B still locates the pattern. Pros: zero rule changes. Cons: very slow patterns, sluggish tests.
- **R2: Step B reads γ relative to local background.** Replace `max |γ|` with `max |γ − local_mean|`. Adds one line. **Recommended starting point for Phase 2.**
- **R3: Two-channel substrate.** Pattern γ and field γ stored separately. Cleaner physically but breaks the unified-substrate principle and loses natural annihilation.

Phase 1 keeps all three options open by not committing to absolute-γ semantics in Step B's spec wording.

### Phase 3 (annihilation) — already implicit, no new work

Two patterns of opposite sign with overlapping support: signed-integer arithmetic + sign-blind Step B produce decoherence cascade automatically. No new rule. Phase 3 = a different `phase3_setup.py` initialization. Already supported by Phase 1 architecture.

### K-dependent timescale (a Phase 2+ prediction)

Patterns in slowly-changing external fields (background change ≪ K) renew successfully. Patterns in rapidly-changing fields (background change ~ K or faster) cannot — their renewal transaction can't keep up. This naturally predicts a Planck-like cutoff at which patterns can no longer survive in a given field gradient. Worth tracking as Phase 2 develops.

## Open questions

1. **Minimum viable K under this rule.** F1 has K = 4, the smallest cycle on which the two-condition Step B (max + min positive) is non-degenerate. K = 2 was excluded by spec self-review. A different rule formulation might rescue K = 2 — worth re-examining if the K-scaling question becomes important.
2. **Spontaneous pattern emergence (Family 2).** Hand-designed shapes are a Phase 1 compromise. Are there local-update rules whose still-lifes are localized clusters (Conway's GoL Block analogue, but on signed substrate)? Phase 1.5 question.
3. **Phase 2 contrast: which resolution?** Decision deferred until Phase 2 design (R1, R2, R3 in Section 4).
4. **K-scaling and mass.** If K is the pattern's natural time unit, and mass-time-dilation correlates with energy density, does K scale with anything that maps to mass? Phase 2+ question.
5. **Fixture geometric constraint generality.** F1/F2/F3 all satisfy "every cycle-distance-2 pair has all common face-neighbors as pattern cells." For arbitrary Hamiltonian cycles on the cubic lattice, is this constraint always satisfiable, or does it limit which shapes are admissible patterns? Phase 1.5 question.

## Risks and constraints

- **Geometry is hand-designed.** Phase 1 fixtures are predetermined Hamiltonian cycles. We are not testing emergence of shape, only preservation of given shape. This is the principal honest compromise of the design.
- **The "single painter" is bookkeeping, not state.** Step B is fully a function of the canvas. The painter's "current position" is recoverable from cell γ values alone. But the *cycle definition* (which cells form the pattern, in what order) is implicit in the canvas configuration; it is not stored elsewhere.
- **Phase 1 cannot test Doc 28 in pure isolation.** The seed is hand-designed. Doc 28's stronger claim — "patterns spontaneously emerge from substrate dynamics" — is out of scope and may require Family 2 or a different substrate ontology.
- **Predecessor branch is unmerged.** Experiment 133's closure work (CLOSURE.md, phase 2b/2c/2d/2e/2f/3b drivers) is uncommitted on `feature/exp-133-closed-loop-substrate`. Should be committed before branching for Exp 134.

## Branch and timing

- New branch `feature/exp-134-pattern-coherence`, off `main` after Exp 133's closure files are committed.
- Phase 1 implementation: estimated single-session work (a few hours).
- Phase 2 design: separate brainstorming session, separate spec.
- Phase 3 design: separate brainstorming session, separate spec.