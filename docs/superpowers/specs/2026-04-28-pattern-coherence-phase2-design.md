---
title: Pattern Coherence Phase 2 (Experiment 134)
date: 2026-04-28
status: spec — pending Phase 2 implementation
predecessor: Phase 1 PASSED 2026-04-28 (see RESULTS.md and project_134_phase1_pass memory)
sibling spec: docs/superpowers/specs/2026-04-28-pattern-coherence-design.md (Phase 1)
---

# Experiment 134 Phase 2: Multi-Pattern Contact Physics

## Motivating principle

Phase 1 demonstrated that a sign-blind transactional renewal rule produces exact fixed-point clusters in vacuum. Phase 2 asks the next question: **what happens when two such patterns coexist on the same substrate, and one is placed in contact (or near-contact) with the other?**

The original Phase 2 ambition was "drift under same-sign external γ" — the gravity story. Through brainstorming we surfaced a structural fact that reshaped the goal:

> **The substrate has no long-range coupling.** Decay is strictly per-cell. Paint is strictly to one cell. Two patterns separated by even one empty cell are completely invisible to each other under Phase 1's rule.

Adding any long-range mechanism (halo, diffusion, field propagation) would smuggle back exactly the kind of distributed-field dynamics the project has empirical reason to be skeptical of (the user's prior NAND-chain attempts at spontaneous pattern emergence produced "cloud with minor clumps, more like visual artifact than real patterns"). So Phase 2 commits to the substrate's stated ontology and reframes the question:

> **Phase 2 is contact physics, not gravity-at-a-distance.** Place test pattern face-adjacent (or near-face-adjacent) to a planet pattern. Observe what the unmodified Phase 1 rule does when two patterns share a connected component.

If gravity-at-a-distance is unearnable in this substrate ontology, that itself is a major (negative) result — and the right one to confront before designing rule modifications.

## Goal

Run the unmodified Phase 1 rule on a multi-pattern substrate. Place a test K=4 pattern face-adjacent to a planet K=4 pattern, with positive-control scenarios at 1-cell and 2-cell separation. Capture three observables (identity, centroid, cycle invariance) per scenario. Document what the substrate *actually does* at contact — no rule tuning toward a desired outcome.

## Background

### Phase 1 result

Phase 1 PASSED on 2026-04-28: four fixture configurations (F1+, F1−, F2, F3) verified bit-identical at every K-tick boundary over 10,000 cycles each. Same `tick()` produced matter and antimatter as CP-mirror images. The rule and substrate are stable and well-characterized in vacuum.

### What Phase 1's rule was *implicitly* committed to

Phase 1's `tick()` was: decay everything once, run Step B once. **One paint event per universe-tick.** This was a single-pattern abstraction. Phase 2 needs to generalize to many patterns coexisting; the natural generalization is **one paint event per pattern per tick**, with patterns identified topologically as face-connected components of nonzero cells.

### Why decoherence-on-contact is the predicted outcome

Two K=4 patterns whose cells become face-adjacent fuse into one 8-cell connected component. Step B on this component encounters:
- Two cells at γ=4 → ambiguous c_max
- Two cells at γ=1 → ambiguous c_min (after one decay tick)
- The geometric constraint that guarantees uniqueness in single-pattern fixtures may not hold across the merged structure

These are exactly the wedged / non-uniqueness failure modes from Phase 1's falsification list. Predicted Phase 2 outcome: **mutual decoherence at the contact site**, with both patterns dissolving over a small number of ticks. Whether this prediction holds is what Phase 2 measures.

### What this rules out for now

- **Long-range "gravity":** patterns at distance ≥ 1 empty cell don't see each other; no drift mechanism exists in this substrate without adding distributed-field machinery (rejected on principle and on NAND-cloud precedent).
- **Same-sign attraction (matter-attracts-matter):** the rule does not distinguish same-sign from opposite-sign contact. Both produce the same merge-and-ambiguity. If we want differentiated behavior, the rule needs modification — that is a Phase 2.5 question, not Phase 2's.

## Section 1: Multi-pattern rule architecture

### Per-tick procedure

1. **Step A — decay** (unchanged from Phase 1): `γ -= sign(γ)` for every nonzero cell.
2. **Identify components:** scan canvas, partition nonzero cells into face-connected components (BFS/DFS over the canvas dict using `face_neighbors`).
3. **Step B per component:** for each component independently, run Phase 1's Step B logic locally:
   - `c_max` = cell in this component with maximum |γ|
   - `c_min` = cell in this component with minimum positive |γ|
   - `c_0` = unique γ=0 cell face-adjacent to both `c_max` and `c_min`
   - Paint `c_0` at `sign(γ[c_max]) × (|γ[c_max]| + 1)`
4. **Failure modes are per-component.** A component that wedges (no valid `c_0`) or non-uniques (multiple candidates) fails *that component only*. Its cells continue to decay over the next K ticks without renewal, and it dissolves. Other components on the canvas are unaffected.

### Bookkeeping for measurement

A parallel dict `pattern_id: dict[Cell, str]` tags cells at bootstrap with their pattern of origin (e.g., `"test"`, `"planet"`). The substrate dynamics ignore this dict — it exists *only* for measurement. A cell can be tagged at bootstrap and remain tagged even if its γ value evolves; the tag is removed when the cell expires (γ → 0, removed from canvas).

### What changes vs. Phase 1

- `tick()` is renamed `tick_multi()` and runs Step B per component (Phase 1's `tick()` is preserved unchanged for backward-compat).
- `find_c_max`, `find_c_min_positive`, `find_c0` are extended (or wrapped) to operate on a *subset* of the canvas (one component) rather than the whole canvas.
- `connected_components(canvas)` is added as a substrate-level helper.

Phase 1's `substrate.py`, `rule.py`, and `fixtures.py` modules are reused. Phase 2 logic is additive: new modules `multipattern.py`, `observation.py`, `scenarios.py`, `phase2_test.py`. No edits to Phase 1 files.

## Section 2: Planet and test pattern setup

### Planet (single K=4 square)

The simplest non-trivial planet: one K=4 square at fixed position.

- Cells after bootstrap: `{(0,0,0): 4, (1,0,0): 3, (1,1,0): 2, (0,1,0): 1}`
- Sign: +1 (matter)
- In vacuum, this is Phase 1 fixture F1 — verified fixed point for 10,000 cycles.

Single-square planet keeps Phase 2 binary: contact event involves exactly one planet pattern fusing with the test. Larger planet clusters add planet-internal failure modes that obscure the contact question. Stretch question deferred.

### Test pattern (K=4 square at three scenarios)

Same K=4 shape as planet, run as three separate scenario configurations:

| Scenario | Test cells (after bootstrap) | Distance to planet | Connectivity |
|---|---|---|---|
| **S1: face-adjacent** | `{(2,0,0): 4, (3,0,0): 3, (3,1,0): 2, (2,1,0): 1}` | (2,0,0) ↔ (1,0,0) face-adj | One 8-cell component |
| **S2: 1-cell gap** | `{(3,0,0): 4, (4,0,0): 3, (4,1,0): 2, (3,1,0): 1}` | nearest cells 2 apart | Two separate components |
| **S3: 2-cell gap** | `{(4,0,0): 4, (5,0,0): 3, (5,1,0): 2, (4,1,0): 1}` | nearest cells 3 apart | Two separate components |

**S1 is the contact event** (predicted decoherence).

**S2 and S3 are positive controls** for substrate locality. Under the no-long-range-coupling framing, both should remain invariant fixed points indefinitely. If either changes, the rule has unexpected coupling — diagnostic gold.

### Sign convention

All Phase 2 scenarios are **same-sign only (matter-matter)**. Opposite-sign (matter-antimatter) is exactly Phase 3's annihilation prediction and is deliberately deferred.

### Run length

**1000 cycles (4000 substrate ticks) per scenario.** Phase 1's 10,000 cycles was about asymptotic invariance; Phase 2's interesting events happen in the first few ticks for S1 (or never for S2/S3). 1000 cycles is plenty to confirm S2/S3 invariance and capture S1's full dissolution trajectory.

## Section 3: Observables, falsification, deliverables

### Three observables tracked per scenario

**Identity (A):** at every K-tick boundary, count `n_test_alive` = number of cells tagged `"test"` at bootstrap that are still in the canvas (γ ≠ 0). Trajectory: `[(cycle_n, n_test_alive)]` for n = 1..1000.

**Centroid (B):** at every K-tick boundary, compute geometric centroid of tagged-`"test"` cells still alive. Trajectory: `[(cycle_n, centroid_xyz)]`. Drift vector = centroid(n) − centroid(1). When zero tagged cells alive, centroid is None.

**Cycle invariance (C):** at every K-tick boundary, hash the entire canvas state with SHA-256 (same hash function as Phase 1). Reference = hash at cycle 1. First break = smallest n where hash(n) ≠ reference.

### Predicted outcomes (to be confirmed or falsified)

| Scenario | Identity | Centroid | Cycle invariance |
|---|---|---|---|
| **S1 (face-adjacent)** | test cells start dying at cycle 1 | drifts as cells die asymmetrically | breaks at cycle 1 |
| **S2 (1-cell gap)** | all 4 test cells alive throughout 1000 cycles | stationary | invariant for all 1000 cycles |
| **S3 (2-cell gap)** | same as S2 | same as S2 | same as S2 |

### Falsification modes

- **Locality violation:** S2 or S3 shows *any* change in canvas state. Means the rule isn't strictly local. Most likely cause: bug in connected-component detection. Less likely but interesting: emergent long-range behavior we didn't predict.
- **Graceful contact:** S1 produces a stable trajectory (test pattern survives in some recognizable form). Would mean the rule resolves merged-component ambiguity non-trivially. Investigate trajectory and determine whether tie-breaking is producing the resolution.
- **Catastrophic decoherence:** S1's failure cascades beyond the 8-cell merged component to unrelated cells. Should not happen given per-component independence. Indicates a bug in component isolation.
- **Asymmetric dissolution:** S1's test cells die *faster* than planet cells (or vice versa). Tells us which side "wins" the ambiguous lookup tie-break.

### Deliverables

Layered on top of Phase 1's existing directory (additive, no edits to Phase 1 files):

```
experiments/134_pattern_coherence/
├── ... existing Phase 1 files (substrate.py, rule.py, fixtures.py, etc.) ...
├── multipattern.py       # connected_components, step_b_component, tick_multi
├── observation.py        # pattern_id tracker, observable extraction
├── scenarios.py          # S1, S2, S3 setup definitions
├── tests/
│   ├── ... existing tests/ ...
│   ├── test_multipattern.py
│   └── test_observation.py
├── phase2_test.py        # Phase 2 deliverable: runs S1/S2/S3, captures observables,
│                         #                       asserts on positive controls
└── RESULTS_phase2.md     # actual observed results per scenario
```

### Implementation constraints

- Python 3, pytest, stdlib only (matches Phase 1).
- Connected-component detection: BFS over canvas dict, face-adjacency. O(N) per tick where N = number of nonzero cells.
- Performance is not a concern at this scale (4 + 4 = 8 cells, 1000 cycles).

### What Phase 2 explicitly does NOT do

- No opposite-sign (matter-antimatter) — Phase 3.
- No multi-planet-pattern clusters — Phase 2.5+ if Phase 2 reveals interesting contact dynamics worth amplifying.
- No drift mechanism design — separate brainstorm if Phase 2 reveals contact-decoherence and we want to revisit "is gravity earnable here."
- No long-range coupling mechanisms (halo, diffusion, etc.) — explicitly rejected on principle and on NAND-cloud precedent.
- No visualization — pytest assertions + recorded observables in RESULTS_phase2.md are the deliverable.

## Open questions

1. **Tie-breaking determinism in Step B's c_max / c_min.** Python's `max()` / `min()` with a key function returns the first encountered extremum. Dict iteration order in Python 3.7+ is insertion order. So the result of S1's first ambiguous lookup depends on which cells were inserted first into the canvas. This is *deterministic but ad-hoc*. Phase 2's RESULTS_phase2.md should document the observed tie-break behavior; Phase 2.5+ may need a principled tie-breaker if same-sign attraction is to be earned.
2. **Does S1's connected component stay a connected component after the first dissolution event?** If a single tick's failure causes the component to split into pieces (e.g., two corner cells die simultaneously, leaving a gap), subsequent ticks might apply Step B to each fragment independently, with new failure modes. Trajectory recording should reveal this if it happens.
3. **Is "gravity-at-a-distance unearnable in this substrate ontology" a final result, or a Phase 2 working hypothesis?** This spec commits to it as a hypothesis. If a future experiment finds a principled long-range mechanism that doesn't recreate the NAND-cloud failure, the framework can be revisited.

## Risks and constraints

- **Geometry is hand-designed.** Phase 1's compromise carries forward — both planet and test patterns are predetermined Hamiltonian cycles. Phase 2 does not test pattern emergence. The user has flagged that "spontaneous behavior may be the issue until the end" of this research arc.
- **Phase 2 result is informative either way, but a "decoherence" result limits future ambition.** If S1 shows mutual decoherence, the substrate as designed cannot produce gravity-like behavior — the next step is either rule modification (Phase 2.5) or accepting "this substrate has different physics than ours."
- **The "no rule tuning" commitment is hard.** If Phase 2 shows decoherence and we are tempted to add tie-breaking rules to "rescue" same-sign attraction, that would be exactly the failure mode Phase 1's framing committed against. RESULTS_phase2.md should record what the rule does, not what we wish it did.

## Phase numbering note

This is Phase 2 of Experiment 134. Phase 1 (vacuum fixed point) is done.

- Phase 2 (this spec): contact physics, same-sign only, unmodified rule.
- Phase 2.5 (future, if motivated): rule modification for tie-breaking — only if Phase 2 reveals decoherence and we have a principled reason.
- Phase 3 (future): opposite-sign contact (annihilation prediction).
- Family 2 / Phase 1.5 (future, gated): spontaneous shape emergence — explicitly deferred and may stay deferred for the duration of this research arc.
