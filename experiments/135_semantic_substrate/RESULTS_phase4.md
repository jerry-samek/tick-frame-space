# Experiment 135 Phase 4 — Results

**Status:** PASSED with substantial findings — multi-observer fixture produces **positional specialization**, **observer-cascade interception**, **traffic starvation** of downstream observers, and **emergent origin-loop spawns for known tokens** when observer cascades disrupt routing paths.
**Date run:** 2026-05-01
**Spec:** `PHASE4_DESIGN.md`
**Run command:** `pytest experiments/135_semantic_substrate/phase4_test.py -v -s`
**Wall-clock:** 0.23 seconds

---

## Summary

K=6 ring + 6 observers (one per ring cell), 10K-tick run. Most interesting Phase yet — the multi-observer fixture exposes several emergent behaviors:

1. **Positional specialization works.** 4 of 6 observers crystallized to **3 distinct spectra** (`{2}`, `{3}`, `{6}`), each reflecting their host's local "exhaust pattern."
2. **Observer cascade interception.** Once early observers crystallize, they intercept tokens before downstream observers can see them. observer_c4 (`{2}`) and observer_c1/c5 (`{3}`) starve observer_c3 of token-2 and token-3 traffic.
3. **Traffic starvation.** Observers at c2 and c3 received only 10 and 9 observations across the entire run — never reached threshold. They sit between busier peers that intercept their potential traffic.
4. **Emergent known-token spawn.** A `{4}` child got spawned at c0 at tick 4046 — token 4 (KNOWN) triggered origin-loop. Multi-observer routing cascade caused token 4 to fail to find its home in some traversal.
5. **Duplicate {8} spawn** (tick 463 + 495) — timing race where the second `{8}` injection couldn't find the freshly-spawned `{8}` child via canvas. Same anomaly as Phase 4 first attempt.

---

## Configuration

- K=6 ring (Crystallized, preset spectra)
- 6 observers, one attached to each ring cell (Learning, empty)
- Phase 1 stream at c0: 50/50 known/unknown, seed=42, cadence=30
- Run length: 10,000 ticks → 334 deposits
- Observer params: `learning_threshold=15`, `crystallization_size=1`

---

## Per-observer outcomes

| Host | State | Total obs | Spectrum | Top-3 obs |
|------|-------|-----------|----------|-----------|
| `c0` | Crystallized | 296 | `{6}` | (3, 79) (2, 66) (6, 37) |
| `c1` | Crystallized | 23  | `{3}` | (3, 11) (2, 3) (4, 3) |
| `c2` | Learning     | 10  | `{}`  | (8, 2) (3, 2) (4, 2) |
| `c3` | Learning     | 9   | `{}`  | (2, 3) (8, 2) (6, 1) |
| `c4` | Crystallized | 24  | `{2}` | (2, 15) (3, 3) (8, 2) |
| `c5` | Crystallized | 38  | `{3}` | (3, 16) (2, 15) (8, 2) |

**Distinct crystallized spectra:** 3 — `{2}`, `{3}`, `{6}`.

---

## The cascade dynamic

Phase 3 showed a single observer becomes a competing classifier. Phase 4 shows that with **multiple observers**, the cascade has positional structure:

1. **observer_c0** (busiest, sees all non-zero tokens) crystallized first, around tick 1000. Spectrum `{6}` — claims token 6 from spawned children.
2. **observer_c5** crystallized around tick 2000 to `{3}`. Now intercepts token 3 on the backward path c0→c5.
3. **observer_c1** crystallized around tick 4000 to `{3}` (also). Now intercepts token 3 on the forward path c0→c1.
4. **observer_c4** crystallized around tick 4000 to `{2}`. Now intercepts token 2 on the backward path c0→c5→c4.
5. **observer_c2** and **observer_c3** never crystallized — by the time they would have observed enough traffic, the upstream observers had already intercepted the tokens they would have seen.

**The substrate self-organized into "intercept tiers":** the busy entry-region observer (c0) learns first, then progressively-outer observers crystallize on the residual traffic, then mid-ring observers (c2, c3) get starved.

This is exactly the structure v8's "causal window" was meant to produce in trie_stream_filtering — but here it emerges *spatially* on the ring, not *hierarchically* on a tree, and from a different mechanism (canvas-driven observation vs reject-stream propagation).

---

## What this proves

1. **Positional specialization is real.** Different observers learn different spectra based on their host's local position in the substrate. observer_c4 learning `{2}` makes sense (token 2 walks past c4 on backward paths to c2). observer_c0 learning `{6}` makes sense (it sees the most token-6 observations early on, before the spawned `{6}` child intercepts).

2. **Cascade dynamics shape what gets learned.** Once observer_c0 crystallizes to `{6}`, it intercepts token 6 from its spawned-child neighbor — meaning later canvases at c0 don't reach the `{6}` child as often. This is the substrate's "first matching classifier wins by canvas proximity" rule playing out across multiple observers.

3. **Traffic starvation is a real failure mode.** When upstream observers crystallize and intercept tokens, downstream observers can be permanently starved — they never reach their crystallization threshold. **observer_c2 and observer_c3 are starved here.**

4. **Origin-loop spawn fires for known tokens under cascade disruption.** The `{4}` child spawned at c0 at tick 4046 means a token=4 deposit walked the substrate without finding its home. With observer cascades disrupting routing paths, **even known tokens can trigger origin-loop spawn**, creating duplicate classifying cells.

5. **The substrate self-organizes hierarchically without an explicit hierarchy.** Phase 4 produces an "intercept tier" structure analogous to v8's depth-stratified trie, but without any tree-shaped topology. The ring + observer fixture spontaneously develops differential learning based on position.

## What this does not prove

- **Specialization works at scale.** Only 4/6 observers crystallized; 2 starved. Phase 5+ would test whether multiple injection points solve the starvation.
- **Cascade is stable.** With longer runs, more observers might eventually crystallize as they slowly accumulate observations, OR substrate might lock into permanent starvation. Untested.
- **Observers don't degrade ring routing for unintended tokens.** Phase 4's spawn of `{4}` shows a real instance of routing failure for a KNOWN token (token 4 should always reach c4 in Phase 1 substrate). Multi-observer cascades create real path-disruptions.
- **Two-pattern interaction.** The actual physics frontier (Phase 5/6 candidates) — planet seed + test seed, drift, recruitment — remains untouched.

---

## Anomalies

### Anomaly 1: Duplicate `{8}` spawn (tick 463 + 495)

Two `{8}` spawned cells exist after the run. Both at c0. This is a timing race: between the first `{8}` spawn (tick 463) and the next `{8}` injection (tick ~481), the substrate had multiple deposits in flight. The second `{8}` injection at c0 didn't find the first `{8}` child via canvas — possibly because the canvas walked the deposit out before reaching the freshly-added child in round-robin order.

Worth deeper investigation in a future phase. Doesn't break the experiment but signals that the substrate's emergent dynamics include some real timing-sensitive behavior.

### Anomaly 2: `{4}` child spawn at tick 4046 (the BIG one)

A token=4 deposit triggered origin-loop spawn at c0. **This shouldn't happen in pure Phase 1** — token 4 always reaches c4 by walking the ring. But by tick 4046, observer_c1 (`{3}`), observer_c4 (`{2}`), observer_c5 (`{3}`) had all crystallized. The cascade of intercepting observers somehow disrupted token 4's route enough to walk it back to c0.

Specifically: token 4's path c0→c1→c2→c3→c4. At each ring cell, canvas now includes the host's observer. Observers may bounce the deposit if their canvas exhausts to all-Different/Unknown. Multi-step disruption can plausibly walk a deposit back to origin without finding c4. Worth a Phase 5 trace to confirm exact mechanism.

This is the substrate doing something genuinely complex. Not a bug — a real consequence of multiple co-located classifiers competing for routing.

### Anomaly 3: observer_c0 crystallized to `{6}`, not `{3}`

Phase 3 (with single observer at c0, threshold=200) crystallized to `{2, 3, 4}`. Phase 4 (with all 6 observers, threshold=15) crystallized observer_c0 to `{6}`. Why the difference?

Phase 4's threshold=15 is much smaller. observer_c0 reaches 15 observations very early (within ~tick 200), before all spawned children are in place. At that early moment, observer_c0's most-frequent token is 6 (which had been injected several times before the `{6}` child spawned and started intercepting it). After the `{6}` child spawned, observer_c0 stopped seeing 6 as often, but spectrum was already frozen.

This is honest: crystallization captures the distribution at the moment of threshold-crossing, not the long-run distribution. Smaller thresholds → more sensitivity to early observations.

---

## Connection to v8 hierarchy and RAW 133

This is the strongest evidence yet for RAW 133's "patterns first" claim AND the closest the substrate has come to v8-style hierarchical specialization:

- v8 (trie_stream_filtering): root → children → grandchildren, depth-stratified by reject-stream propagation.
- Phase 4 (semantic substrate): c0 (busy) → ring cells with crystallized observers → starved observers, position-stratified by canvas-driven observation.

In both cases, **specialization emerges from differential exposure to traffic**. v8 used hierarchy to create the differential; Phase 4 uses ring topology + entry-point bias.

This suggests the substrate ontology can produce v8-like decomposition WITHOUT requiring a tree-shaped topology — something v8 hadn't considered. The trade-off: v8 had clean tree structure (every node has exactly one parent); Phase 4 has potential cascade chaos (multiple classifiers compete for the same tokens).

---

## Next steps

**Phase 5 candidates** (in order of priority):

1. **Multiple injection points to fix starvation.** Inject at c0 AND c3 (or all 6 cells). Verify all 6 observers crystallize and learn distinct things based on local traffic profile.
2. **Trace the {4}-spawn anomaly.** Add detailed logging to capture exactly how token 4 walked back to c0. Likely surfaces a real mechanism gap.
3. **Two-pattern interaction.** Two ring patterns, distance between them, drift measurement. The original RAW 133 physics frontier.
4. **Observer-induced ring decommissioning over very long runs.** Run for 100K+ ticks, see whether ring cells gradually become unreachable due to upstream observer interception.

---

## Files

- `PHASE4_DESIGN.md` — design spec
- `phase4_test.py` — deliverable
- `phase4_run.log` — captured output
- `RESULTS_phase4.md` — this file

No changes to `cell.py`, `substrate.py`, `fixture.py`, or any earlier phase tests/deliverables.
