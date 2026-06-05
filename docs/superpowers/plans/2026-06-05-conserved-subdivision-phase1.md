# Conserved-Subdivision Substrate — Phase 1 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: superpowers:subagent-driven-development or superpowers:executing-plans. Steps use `- [ ]`.

**Goal:** Test whether a **spatially-local, difference-driven, loop-closing** conserved-subdivision rule — operating *within the global tick-foliation* — lifts the substrate off the Phase-0 K_N floor toward a **stable finite emergent dimension** (target: benchmark-relative 3D), with pre-registered controls that isolate the *rule* from mere sparsity.

**Architecture (and the key framing):** We are **not** strictly local in time. Synchronized ticks are a **global temporal foliation** (Doc 49: tick-stream as absolute substrate) — the same structure CDT uses to reach an integer dimension, and the *one* assumption the framework takes as irreducible. Locality is **spatial only** (the gluing acts on the leaf-adjacency graph). This places us in CDT's regime (global time + spatial locality, which *did* earn integer-d), **not** Trugenberger's strictly-local regime (which collapses to a circle, d=1). The rule fuses: selective inheritance (breaks K_N) + typed difference-driven cut (axis alphabet grown by data, never pre-sized) + a cross-lineage loop-closure pass (escapes the tree) + a conserved-resource cap (holds growth polynomial without naming a dimension). Dimension is read **spectrally from the leaf-graph, never from the axis-label count**.

**Anti-solipsism (Tom 2026-06-05 — the physical content behind the circle-collapse failure mode):** a single stream subdividing in *lockstep* is solipsistic — no "other" to be next to — and that is itself the route to the d→1 circle (Trugenberger collapse = a stream folding onto itself). Genuine structure requires the stream to **fork into quasi-independent sub-streams** that (a) **diverge** (each cuts along *its own* local difference, not in lockstep) yet (b) carry a **shared-prefix memory from the common root** (RAW 114 shared-prefix identity; RAW 116 single-entity continuity; RAW 038 observer-separation). The loops that escape the tree are **independent sub-streams re-meeting within a shared frame**, not a monolith folding onto itself. NOTE the honest tension with Exp 131: shared-prefix *depth alone* (lineage distance) gave a tree → hyperbolic (falsified), so the shared prefix is the **gate** (who may match), NOT the metric (the space comes from divergent sub-streams re-contacting).

**Tech stack:** reuses Phase-0 `substrate.py`, `battery.py` (calibrated, frozen), `nulls.py`; adds `rule.py`, `controls.py`, drivers. Python 3.13, numpy/scipy/networkx, POT, gudhi.

**Spec:** `docs/superpowers/specs/2026-06-05-conserved-subdivision-substrate-design.md`. **Builds on:** `RESULTS_phase0.md` (bare = K_N; gluing is foundational). **Grounding:** gluing-rule pass 2026-06-05 (NGF, CDT, Trugenberger, Verma-Kpotufe-Dasgupta).

---

## A. PRE-REGISTRATION (Phase 1 additions; append to PREREG.md, frozen before any run)

**A.5 The rule (pinned, per grounding §recommended_gluing_rule).** Each `Cell` gains `faces: list[(axis_label:int, side:±1, key)]` and feature `x` (genesis x = length-1 zero vector; accumulates signed half-steps per cut). Tick:
1. **Selective inheritance:** a parent-neighbor edge `ap~bp` is inherited by **exactly one** child-pair (the children retaining the co-located portion of that shared face), not k². → degree O(#faces), independent of N. (Breaks K_N.)
2. **Typed difference-driven cut:** cut along the principal-difference axis of `{x(n)−x(c) : n∈Nbr(c)}` (Verma-Kpotufe-Dasgupta) at the measure-median (= equal-measure bisector for k=2). Assign an axis_label: **reuse** an existing label if direction aligns (cos>0.8) with one already in the cell's address, else **mint a fresh label**. Children get `x ± half-step` and faces `(label,+1)/(label,−1)`. **The axis-label alphabet is grown by data, NEVER pre-sized to 3** — this is what keeps dimension an output.
   **x(c) is MEMORY = the whole replayed path (Tom 2026-06-05).** x(c) is the accumulated signed cut-steps per axis-label summed along the *entire* path root→leaf — a coordinate-free position vector indexed by the data-grown axis alphabet. Ontologically it is **re-derived by full Prolog-style replay** (no random access into the middle; the only operations are extend-at-leaf and replay-from-root — the strongest form of append-only, and Doc 28 renewal = reconstitute-by-replay; cf. RAW 123/125, RAW 044). Memoize the running sum for speed, but the semantics is whole-path replay.
3. **Sibling edge:** the two children are mutually adjacent across their new internal face. (Keep; free.)
4. **Loop-closure pass (NEW, required code addition — `glue()` structurally cannot do this):** after steps 1–3, one global pass over all leaf faces; index by `(axis_label, quantized x-position, measure-key)` where x-position is the **whole-path-replayed accumulated position** (step 2). Add an edge between any two cells with **anti-parallel** (same label, opposite side) **co-located** (replayed accumulated-position vectors coincide within fixed smear) faces — **but only between sub-streams whose axis-labels trace to a shared-prefix ancestor** (the shared prefix makes the labels commensurable / same frame; this is the "prefixed memory from shared root" gate). A loop is thus **two different whole-paths arriving at the same place from opposite sides** — the coordinate-free analogue of two refinement routes reaching adjacent cells. **Exp-131 guard (do not repeat):** path-LENGTH is NOT distance; the replay yields relative *position* for matching only — the metric/space is the matched-adjacency graph, never lineage-distance (which gave a tree).
5. **Smear (weak non-locality):** the co-location match and the neighborhood read use a **FIXED** tolerance (`R_sp=2` hops / fixed position-quantization grid). FIXED is load-bearing — a growing window re-creates K_N.
6. **Conserved-resource cap (emergence firewall):** each cell holds **≤1 matched neighbor per oriented face it owns**; face budget grows **only when the cell is cut** (never a global degree/loop target). Trugenberger hard-core guard: reject a step-4 edge that makes two short cycles on one cell share >1 edge (cap short-cycles-per-edge at a small constant, `C_max=1`). **The cap is a RESOURCE (faces), not a TARGET (degree/loops)** — this distinction is what separates emergent-d from assumed-d.
7. **Readout:** leaf-graph → calibrated Phase-0 battery. Dimension = fitted d_s/d_H, **never** the axis-label count.

**A.6 Three pre-named failure signatures (frozen; a near-miss in any is a failure, not a caveat):**
- `d_s → N` (toward complete): gluing too generous / cap off.
- `d_s → ~1` (circle/tree collapse, **Trugenberger mode**): loops not forming, or rule only lengthens one chain.
- `d_s` growing without bound (hyperbolic/expander, **NGF/over-smoothing mode**): smear or cap too generous.
- **Capacitor STALL or RUNAWAY** (Arm F only): *stall* = firing stops, substrate frozen at coarse N (threshold too high vs charge rate); *runaway* = firing creates fresh difference → more firing → degree climbs back toward K_N (threshold too low / cap too loose). Both are failures; the threshold×cap balance must sit between them.

**A.7 Emergence check (frozen):** report `(#axis labels minted)` vs `(measured d_s)`. If they are forced equal, dimension was **assumed**, and the result is **void on its own terms**.

**A.8 Three controls (pre-registered; run on the IDENTICAL seed set & N-ladder, median+IQR):**
- **Config-model** (degree-preserving rewiring): destroys spatial correlation, keeps degree sequence. PASS requires structured `d_s≈3, loops>0.3 rising` while config-model gives `loops~1/N, d_s ill-defined`. Structured≈config ⇒ dimension came from sparsity, **falsified**.
- **Orientation-blind matched-count** (NAND-cloud repro): same #cross-lineage edges/tick but random child-pairs (ignore label/side/position). Structured≈orientation-blind ⇒ the boundary-MATCH does no work, **artifact**.
- **Shuffled-feature** (random-axis cut): permute `x` before the principal-axis read. Tests whether cut *direction* carries geometry.

**A.9 WIN (frozen, benchmark-relative per A.3):** structured run in the A.3 band (d_s∈[2.2,3.2] & within ±0.4 of Poisson-3D control; d_H∈[2.2,3.2]; distinctly above 2D control; loops>0.3 rising; flat Ricci) **AND** cleanly separated from ALL THREE controls **AND** holding (no drift toward 2 or 1) to **n≥5000 across ≥20 seeds**. **A.4 program falsifier stands:** miss ⇒ clean negative, STOP, next attempt surrenders a named commitment (go explicitly foliated/CDT-like or energetic).

**A.10 Solipsism null + independent-forking (Tom 2026-06-05; the headline mechanism test).** Differential, independent subdivision is **promoted from a deferred ablation to a primary ingredient** — it is the proposed cure for the d→1 collapse, not a refinement. Two pre-registered, contrasting predictions on the SAME glued base, controls, seeds, and N-ladder:
- **Uniform lockstep refinement (all leaves split identically each tick) = the SOLIPSISM NULL.** Prediction: collapses toward **d≈1 (circle)** or stays trivially low — a single stream folding onto itself.
- **Differential independent forking = CAPACITOR FIRING (Tom 2026-06-05; trit-as-capacitor, RAW 126/127/132).** Each leaf is a capacitor: it *integrates* local difference into a charge; it *fires* (cuts/forks along its principal-difference axis, A.5 step 2) the moment its **own** charge crosses a threshold — on whatever tick that happens, set by its local charging rate, **independent of global state**; charge resets on fire. So (a) difference-threshold and (b) asynchrony are one mechanism. Sub-streams diverge because heavy-difference leaves fire often, uniform ones rarely. Re-meeting gated by shared-prefix frame (A.5 step 4). This is **structurally anti-cloud** — the capacitor resolves difference by *recording a boundary (firing)*, never by averaging. Prediction: lifts off to a finite d>1 with growing loop density.
  **Tick vs firing (no contradiction):** the global tick remains the foliation/metronome (Doc 49, the licensed "one"); firing is event-driven *on top of it* (discrete-time integrate-and-fire) — global ordering + local asynchronous threshold-crossings.
  **New pinned params (pre-register):** firing `threshold`; `charge←difference` accumulation function (provisional: charge += sum of |x(c)−x(n)| over current neighbors per tick; fire at charge≥threshold; reset to 0). Adaptive threshold (RAW 132 §3.3) is a DEFERRED toggle, not in the first Arm-F run.
- **Adjudication:** uniform→collapse AND differential→lift-off ⇒ the solipsism diagnosis is confirmed and independence is the active ingredient. Differential≈uniform (both collapse, or both lift) ⇒ solipsism framing is wrong — report it. (This makes Tom's insight falsifiable rather than assumed.)

---

## File Structure

- `experiments/136_conserved_subdivision/substrate.py` — MODIFY: `Cell.faces`, `Cell.x`; `tick(...)` gains a `loop_closure` hook + face bookkeeping.
- `rule.py` — CREATE: `Rule` dataclass (toggles: `loop_closure, pa_cut, smear, cap, penalty`) + `selective_glue`, `typed_cut`, `loop_closure_pass`, `resource_cap`.
- `controls.py` — CREATE: `config_model_rewire(g)`, `orientation_blind_glue(...)`, `shuffle_features(...)`.
- `phase1a_base.py` — CREATE: glued base (steps 1+3+4+6, simplest cut) → battery + config control → lift-off decision → `RESULTS_phase1a.md`.
- `phase1b_ablation.py` — CREATE (only after 1a lifts off): the ablation ladder → `RESULTS_phase1b.md`.
- `tests/test_rule.py`, `tests/test_controls.py` — CREATE.

---

## Task 1: Extend Cell with faces + feature; preserve conservation

**Files:** Modify `substrate.py`; Test `tests/test_rule.py`.

- [ ] **Step 1: failing test**

```python
# tests/test_rule.py
from fractions import Fraction
from substrate import Substrate

def test_cell_has_faces_and_feature():
    s = Substrate()
    c = s.leaves[0]
    assert hasattr(c, "faces") and hasattr(c, "x")

def test_conservation_still_exact_with_faces():
    s = Substrate()
    for _ in range(6):
        s.tick()
        assert sum(c.measure for c in s.leaves) == Fraction(1)
```

- [ ] **Step 2: run, verify fail.**
- [ ] **Step 3: implement** — add `faces: list = field(default_factory=list)` and `x: tuple = (0.0,)` to `Cell`; in `tick`, when a child is created, set its `x` and append the new face pair (axis label + side). For Task 1 keep the bare equal-split + sequential axis label `depth` so the test passes without the full rule:

```python
# in Cell dataclass add:
#   x: tuple = (0.0,)
#   faces: list = field(default_factory=list)
# in tick(), where children are created (bare default), tag faces+x:
#   axis = len(c.address)                      # sequential label (Task 5 replaces with PA-cut)
#   child.x = c.x ; child.faces = list(c.faces) + [(axis, +1 if bit=="0" else -1)]
```

- [ ] **Step 4: run, verify pass.**
- [ ] **Step 5 (commit checkpoint).**

---

## Task 2: Selective inheritance — break K_N (the decisive degree-bound test)

**Files:** Create `rule.py`; Modify `substrate.py` (pass `glue` from rule); Test `tests/test_rule.py`.

- [ ] **Step 1: failing test** — the bare rule gave mean degree = N−1 (K_N); selective inheritance must keep degree BOUNDED as N grows.

```python
def test_selective_inheritance_breaks_KN():
    from rule import Rule, run_to_n
    s = run_to_n(Rule(loop_closure=False, pa_cut=False), target_n=512)
    g = s.leaf_graph()
    mean_deg = 2 * g.number_of_edges() / g.number_of_nodes()
    assert mean_deg < 12          # bounded, NOT ~511 (K_N)
```

- [ ] **Step 2: run, verify fail.**
- [ ] **Step 3: implement** `rule.py` with `Rule` toggles + `selective_glue` (a parent-neighbor edge inherited by exactly one co-located child pair) and `run_to_n(rule, target_n)`. Selective rule: glue child `a` of `ap` to child `b` of `bp` iff `a` and `b` carry the anti-parallel co-located portion of the face that carried `ap~bp` (use the face key recorded in Task 1). Wire `substrate.tick(glue=rule.glue, split=rule.split)`.

```python
# rule.py (selective inheritance core; full bodies filled by implementer following A.5 step 1)
from dataclasses import dataclass
from substrate import Substrate

@dataclass
class Rule:
    loop_closure: bool = True
    pa_cut: bool = True
    smear: int = 2
    cap: int = 1
    penalty: bool = False
    def split(self, c):
        return [(c.measure/2, "0"), (c.measure/2, "1")]   # Task 5 upgrades to PA-cut
    def glue(self, a_child, b_child, a_par, b_par):
        # selective: inherit a parent edge on exactly one co-located child pair (A.5 step 1)
        # returns True iff a_child and b_child retain the shared sub-face of a_par|b_par
        ...   # implement via the face key recorded in Task 1; one pair True, rest False

def run_to_n(rule, target_n):
    s = Substrate()
    while len(s.leaves) < target_n:
        s.tick(split=rule.split, glue=rule.glue,
               loop_closure=(rule.loop_closure and __import__('rule').loop_closure_pass) or None)
    return s
```

- [ ] **Step 4: run, verify pass** (mean degree bounded, K_N broken).
- [ ] **Step 5 (commit checkpoint).**

---

## Task 3: Cross-lineage loop-closure pass (escape the tree)

**Files:** Modify `substrate.py` (add `loop_closure` post-pass hook); add `loop_closure_pass` to `rule.py`; Test `tests/test_rule.py`.

- [ ] **Step 1: failing test** — without loop-closure the selectively-glued graph is a tree (loops≈0); with it, cross-lineage loops appear.

```python
def test_loop_closure_creates_cross_lineage_loops():
    from rule import Rule, run_to_n
    from battery import loop_density
    s_off = run_to_n(Rule(loop_closure=False), 512); s_on = run_to_n(Rule(loop_closure=True), 512)
    assert loop_density(s_off.leaf_graph()) < 0.05      # tree-like without it
    assert loop_density(s_on.leaf_graph()) > 0.1        # loops with it
```

- [ ] **Step 2: run, verify fail.**
- [ ] **Step 3: implement** the second pass (A.5 step 4): in `substrate.tick`, after building `new_adj`, if a `loop_closure` callable is supplied, call it to add cross-lineage edges by face-index matching (anti-parallel + co-located within fixed smear). Implement `rule.loop_closure_pass(leaves, adj, smear)` building the face index and adding matched edges, subject to the resource cap (Task 4).
- [ ] **Step 4: run, verify pass.**
- [ ] **Step 5 (commit checkpoint).**

---

## Task 4: Conserved-resource cap (the K_N firewall, dimension-agnostic)

**Files:** Modify `rule.py` (`resource_cap` inside `loop_closure_pass`); Test `tests/test_rule.py`.

- [ ] **Step 1: failing test** — degree stays bounded as N grows AND short-cycles-per-edge capped.

```python
def test_resource_cap_bounds_degree_and_cycles():
    from rule import Rule, run_to_n
    for n in (512, 2048):
        g = run_to_n(Rule(loop_closure=True, cap=1), n).leaf_graph()
        assert 2*g.number_of_edges()/g.number_of_nodes() < 16   # bounded at all N (no K_N regress)
```

- [ ] **Step 2: run, verify fail (if uncapped loop-closure over-connects).**
- [ ] **Step 3: implement** the cap: ≤1 matched neighbor per oriented face; reject a match that would make two short cycles on one cell share >1 edge (`C_max`). Resource = faces (grows only on cut); never a degree target.
- [ ] **Step 4: run, verify pass.**
- [ ] **Step 5 (commit checkpoint).**

---

## Task 5: Typed difference-driven cut (PA-tree; axis alphabet grown by data)

**Files:** Modify `rule.py` (`typed_cut` replacing `split`); Test `tests/test_rule.py`.

- [ ] **Step 1: failing test** — axis-label alphabet grows with data, is NOT pre-sized to 3.

```python
def test_axis_alphabet_grows_not_presized():
    from rule import Rule, run_to_n
    s = run_to_n(Rule(pa_cut=True), 2048)
    labels = set(ax for c in s.leaves for (ax, _side) in c.faces)
    assert len(labels) > 3        # data-grown, not capped at 3 (would be assumed-d)
```

- [ ] **Step 2: run, verify fail.**
- [ ] **Step 3: implement** `typed_cut` (A.5 step 2): principal-difference axis of `{x(n)−x(c)}` over `Nbr(c)` (max-variance / top eigenvector); cut at measure-median; reuse axis label if cos>0.8 with an address axis, else mint fresh; set children `x ± half-step`, faces tagged.
- [ ] **Step 4: run, verify pass.**
- [ ] **Step 5 (commit checkpoint).**

---

## Task 6: Controls (config-model, orientation-blind, shuffle)

**Files:** Create `controls.py`; Test `tests/test_controls.py`.

- [ ] **Step 1: failing tests**

```python
# tests/test_controls.py
import networkx as nx
from controls import config_model_rewire
def test_config_model_preserves_degree_sequence():
    g = nx.random_geometric_graph(500, 0.12, seed=0)
    h = config_model_rewire(g, seed=0)
    assert sorted(d for _,d in g.degree()) == sorted(d for _,d in h.degree())
```

- [ ] **Step 2: run, verify fail.**
- [ ] **Step 3: implement** `config_model_rewire` (double-edge-swap to exhaustion / `nx.configuration_model` from the degree sequence, simple-graph-ified), `orientation_blind_glue` (replace step-4 matching with same-count random child-pairs), `shuffle_features` (permute `x`).
- [ ] **Step 4: run, verify pass.**
- [ ] **Step 5 (commit checkpoint).**

---

## Task 7: Phase 1a — glued-base lift-off test (the decisive gate)

**Files:** Create `phase1a_base.py`; output `RESULTS_phase1a.md`.

Build the glued base = steps 1+3+4+6 (selective inheritance + siblings + loop-closure + cap). Then run the **two pre-registered A.10 arms** on that base, both with battery + config-model control, ≥20 seeds, N-ladder [512, 1000, 2000, 5000]:
- **Arm U (solipsism null):** uniform lockstep refinement (all leaves split each tick), simplest cut (equal halves, sequential axis labels). Prediction: d→≈1 (circle) / trivial.
- **Arm F (candidate):** **capacitor firing** — each leaf integrates local difference into charge and fires (cuts along its principal-difference axis) when its own charge crosses threshold, asynchronously, independent of global state; charge resets on fire (A.10; RAW 126/127/132). Sub-streams diverge because charging rates differ; re-meeting shared-prefix-gated. Prediction: finite d>1, loops rising. Watch the **stall/runaway** band (A.6).

**Decision gate (pre-registered, A.6 + A.10):** compare U vs F.
- lands at finite `1 < d_s < N` with `loop_density > 0.3` rising, separated from config-model → **LIFT-OFF**, proceed to Phase 1b.
- `d_s → ~1` (circle/Trugenberger) or `d_s → N` (K_N) or unbounded (hyperbolic) → that is likely the answer; report as honest negative per A.4 (the base cannot lift off; the difference-cut/smear in 1b may still rescue, but only if the base shows *some* finite 2<d structure to stabilize).

- [ ] **Step 1: write driver** (battery from Phase 0; config control from Task 6; loop over seeds & N; classify against A.6 signatures; write RESULTS_phase1a.md with median+IQR table and the lift-off verdict).
- [ ] **Step 2: run** `python -u phase1a_base.py`. (Heavy probes guarded by Phase-0's mean-degree Ricci guard; expect bounded degree so Ricci computes.)
- [ ] **Step 3:** read RESULTS_phase1a.md; **STOP and report to the user at this gate** (it is the decisive Phase-1 result).
- [ ] **Step 4 (commit checkpoint).**

---

## Task 8: Phase 1b — ablation ladder (ONLY if 1a lifts off)

**Files:** Create `phase1b_ablation.py`; output `RESULTS_phase1b.md`.

Per grounding ablation order, one toggle flipped at a time on the glued base, each with battery + all three controls, ≥20 seeds, N-ladder, pre-registered predicted effect:
1. loop-closure ON vs OFF (tree/non-tree switch — confirm).
2. PA-cut vs sequential-axis (expect: stabilizes d across scale).
3. smear R_sp=2 vs 0 (expect: knife-edge brittle; growing smear → K_N sanity).
4. cap C_max=1 vs 2 vs off (firewall margin).
5. penalty ON last (only if 1–4 near the band).

- [ ] **Step 1: write driver** (ablation loop; for each config: structured + 3 controls; record median+IQR; emergence check A.7 (labels vs d_s gap); classify vs A.6).
- [ ] **Step 2: run.**
- [ ] **Step 3:** write RESULTS_phase1b.md — which ingredient(s) move d toward the benchmark, the emergence-gap, control separations; apply A.9 WIN / A.4 falsifier. **STOP and report.**
- [ ] **Step 4 (commit checkpoint).**

---

## Self-Review (against spec + grounding)

- Spec §6 ingredients: A.5 steps 1–6 = the five ingredients (selective inheritance is the K_N fix Phase 0 demanded; loop-closure = "build loops"; typed cut = difference-direction + ancestral feature; smear = weak non-locality; cap = the firewall). ✓
- Spec §8 ablation (null-first, lead with gluing): Task 7 builds the glued base first; Task 8 ablates on top, loop-closure switch first. ✓
- Spec §9 battery + nulls: reused from Phase 0 (frozen, calibrated). Controls (A.8) added per the "pure-random gives no structure" point. ✓
- Spec §10 falsifier + benchmark-relative WIN: A.9/A.4. ✓
- Global-tick-foliation framing (Doc 49 = CDT foliation = the licensed "one"): in Architecture + A. ✓
- Emergence integrity: A.7 labels-vs-d_s gap; axis alphabet never pre-sized (Task 5 test); cap is a resource not a target (Task 4). ✓
- Placeholder scan: the two `...` bodies (selective `glue`, loop-closure) are specified by A.5 steps 1 & 4 with the exact match condition (anti-parallel + co-located faces); implementer fills the face-key arithmetic. These are the genuinely novel algorithmic cores — flagged as the highest-risk code (grounding: "required code addition, not a parameter").
- Honest risk (carried from grounding): dominant outcome is d→1 (circle) or hyperbolic; clean 3D is ~10–20%; the config-model + orientation-blind controls are the defense against a false positive; finite-size scaling to n≥5000 is where near-misses die.

---

## Execution note
Phase 1a is the decisive gate — **stop there and report** before Phase 1b. Per the user's preference: no branch/PR ceremony; nothing committed without explicit say. The deepest honest possibility remains live and pre-accepted (A.4): a strictly-spatial-local rule within the tick-foliation may still collapse to a circle or blow up hyperbolic — in which case the clean negative tells us the *next* commitment to surrender (explicit foliation geometry à la CDT, or an energetic action), and that is itself the finding.
