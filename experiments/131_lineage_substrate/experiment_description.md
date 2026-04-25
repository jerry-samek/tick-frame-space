# Experiment 131 — The Lineage Substrate

## Status: IN PROGRESS — Phase 1 flow rule falsified, needs repair
## Date: April 18, 2026

---

## Progress Log

### 2026-04-18 — Phase 1 (naive averaging diffusion): FALSIFIED

Ran three tree configurations with naive averaging diffusion on 3D-
embedded tree (k=8, D=5, 37k nodes):

| Config | BOUNDARY_FRACTION | offsets | slope ρ(r) |
|--------|-------------------|---------|------------|
| v2     | 0.70              | gaussian | **−0.99 ± 0.16** |
| v3     | 0.50              | uniform  | **−2.01 ± 0.67** |
| v4     | 0.90              | uniform  | **−0.17 ± 0.08** |

v2's "slope ≈ −1" looked like Newton recovery initially. Phase 2
(tangential Schwarzschild transfer) revealed ρ(r) is not a clean power
law — fit slope depends heavily on window. v3/v4 confirmed the v2 slope
was a lucky middle between two failure modes, not a physical law. Moving
the boundary changes the answer qualitatively from −2 (cliff-dominated)
through 0 (saturated pool).

**Falsifies:** RAW 131's specific claim that tree + naive averaging-
diffusion produces 3D Poisson 1/r.

**Does not falsify:** RAW 131's core ontology (ancestral connections,
+1/tick as the fluid, spatial distance as derived). Only the specific
flow rule.

### Next step (not yet tried): conductance-weighted flow

Edge conductance ∝ 1/length (electric-resistor analogy). Should make
diffusion respect 3D geometry despite tree topology. Natural rescue for
RAW 131. If it fails, we accept ρ(r) ∝ 1/r² as tree's natural field
(reinterpret Exp 128 targets) or reject tree substrate entirely.

See memory entry: project_131_tree_newton_falsified.md

---
## Author: Tom (insight), Claude (spec)
## Theory: RAW 131 (The Lineage Substrate)
## Supersedes: Experiment 128 (Energy Partition, v1–v11)
## Related: Experiment 55/56 (composite objects — pattern coherence)

---

## Why This Experiment Exists

Experiment 128 v11 earned 1/r² field geometry, Keplerian orbits, exact
Schwarzschild **tangential** time dilation, and the equivalence principle.
It failed, cleanly and reproducibly, on Schwarzschild **radial**: on a 3D
random geometric graph (RGG) with isotropic diffusion, no scalar observable
under any linear-local propagation rule reads `g_rr = 1/(1 − L_grav)`. Four
diagnostics (Phase 6, 6b, 6c, 6d, 6e) converged on the same negative.

RAW 131 proposes the failure is **ontological**, not parametric. The RGG is
the wrong substrate. Connections between entities are not built by spatial
propagation; they are **ancestral** — present from the moment their
lineages split from a common ancestor. Propagation doesn't create the
connection; it flows `+1/tick` of energy along a connection that already
exists.

Experiment 131 tests whether a lineage-tree substrate can recover the
Experiment 128 positive results (1/r², Kepler, tangential γ, equivalence
principle) and, on top of that, earn Schwarzschild **radial** and
perihelion precession from composite-object pattern coherence on the tree.

---

## Hypothesis

The fundamental substrate is a lineage tree, not a spatial graph.
- Every entity has exactly one parent (split from).
- The tree is built incrementally as entities split, but each edge is
  permanent once established.
- Each global tick, every entity receives `+1/tick` energy for existing.
  That energy flows along lineage edges.
- Spatial distance between two entities is derived, not primitive: it is
  proportional to the depth of their lowest common ancestor (LCA):
  `r(A, B) := d_LCA(A, B) / α`, where `α` is the tree's self-similarity
  constant.
- For a tree with approximately constant branching factor and 3D
  spatial embedding (volume at depth d scaling as d³), the linear
  relation `d_LCA ∝ r` recovers finite `c = 1 / (2α)`.

---

## Phase 0 — Minimal Two-Seed Tree (build-and-measure sanity check)

### Goal

Build the simplest lineage-tree substrate that has two identifiable
seeds (a "star" lineage and a "planet" lineage) sharing an LCA. Flow
`+1/tick` through the tree. Measure the apparent correlation / coupling
between star and planet as a function of LCA depth. Check that a notion
of "distance" is consistent.

### Setup

- Tree with branching factor `k` (start with `k = 2` for cleanliness).
- Depth `D`; `N ≈ k^D` leaves.
- Two leaves selected as "star" and "planet"; vary `d_LCA` between them
  from 1 to `D`.
- Every tick:
  1. Every entity receives `+1` energy.
  2. Energy flows up the tree (entity sends a fraction to its parent)
     and down (parent distributes to children).
  3. Measure how much of the star's energy reaches the planet per tick.

### Observables

- **Apparent coupling** `K(d_LCA)` — energy transfer rate from star to
  planet per tick.
- **Propagation time** `τ(d_LCA)` — ticks required for a perturbation at
  the star to register at the planet.

### Success criteria

- `K(d_LCA) ∝ 1 / d_LCA²` (reproduces Newton if `r = d_LCA / α`).
- `τ(d_LCA) = 2 · d_LCA` exactly (finite c = 1 / (2α)).
- Both should hold regardless of specific choice of flow rule, as long
  as the rule is local and conservative on the tree.

### Failure modes

- If `K` scales as `1 / d_LCA³` or `exp(−d_LCA)` or anything other than
  `1 / d_LCA²`, the tree needs different branching structure or a
  different flow rule. Document.
- If `τ` is not strictly linear in `d_LCA`, the tree is not self-similar
  or the flow rule is wrong. Document.

---

## Phase 1 — Self-Similar Tree, Newton's Recovery

### Goal

Build a tree with 3D spatial embedding such that the relation
`r = d_LCA / α` holds with a consistent `α`. Verify that 1/r² emerges
for the field at a "test entity" distance r from a "star" entity.

### Setup

- Start from Phase 0's tree. Embed leaves in 3D space such that the
  branching at each level corresponds to spatial locality: a node at
  position **p** has children distributed within a sphere of radius
  `R_level` around **p**, with `R_level` shrinking geometrically with
  depth.
- Choose `R_level` and branching factor `k` such that the volume at
  depth `d` scales as `d³`.
- Place a "star" seed at the origin of an early-depth branch (say,
  depth 3 from root). Let its descendants form a cluster at the origin.
- Fire `+1/tick` through the tree. Measure the "field" (whatever the
  apparent coupling is) at leaves distributed spatially throughout the
  tree.

### Observables

- Field strength `ρ(r)` as a function of spatial distance r to the
  star cluster.
- Power-law slope of `ρ(r)` and `|∇ρ|(r)`.
- Compare to Phase 1 of Experiment 128's RGG result (slope −1.33 for ρ,
  −1.968 for gradient).

### Success criteria

- `ρ(r) ∝ 1/r` with slope in [−1.2, −0.8] (matching 3D Poisson).
- `|∇ρ|(r) ∝ 1/r²` with slope in [−2.1, −1.9].

### What this earns

If this passes, the tree ontology reproduces Experiment 128's 1/r²
result at lower cost (no spatial graph required — only lineage).
Newton's law emerges from lineage tree geometry.

---

## Phase 2 — Tangential Schwarzschild on the Tree

### Goal

Verify that exact Schwarzschild tangential proper time (Exp 128 Phase 5
result) survives the ontology shift. This is expected to be easy —
tangential motion is motion along lines of constant LCA depth, which
is a natural operation on a tree.

### Setup

- Same tree as Phase 1.
- Place a test entity at fixed lineage distance from the star.
- Move the test entity tangentially (along constant LCA depth). Measure
  local tick rate of its `+1/tick` absorption.

### Observables

- Local tick rate as a function of position and velocity.
- Compare to `γ = sqrt(1 − L_grav − L_vel)`.

### Success criteria

- Exact match to within numerical precision.

If this passes, Phase 5 transfers unchanged. This is a necessary check,
not a frontier.

---

## Phase 3 — Radial Schwarzschild from Tree Density

### Goal

Test whether the Schwarzschild radial factor `g_rr = 1/(1 − L_grav)`
emerges naturally from lineage tree structure — specifically, from how
many tree edges are needed per unit spatial extent in regions of high
branching density (near mass).

### Intuition

If the tree's local branching density increases near mass (because
mass is a cluster of many entities with shared recent ancestry), then
a radial step that crosses through a dense region requires traversing
more tree edges per unit spatial distance. That is exactly the
`g_rr = 1/(1 − L_grav)` factor.

### Setup

- Lineage tree with non-uniform branching: the "star" region has
  locally higher branching factor (more entities per unit volume).
- A test entity at spatial distance `r` from the star.
- Measure the ratio `(tree edges traversed) / (spatial distance moved)`
  for radial vs tangential motion at various `r`.

### Observables

- `ratio_radial(r)` and `ratio_tangential(r)`.
- Compare `ratio_radial(r) / ratio_tangential(r)` to `1/(1 − L_grav(r))`
  where `L_grav(r)` is defined from the local branching density.

### Success criteria

- Ratio matches `1/(1 − L_grav)` within 5% in the measured regime.

### What this earns

If it passes: exact Schwarzschild radial emerges from lineage geometry
without any substrate reshaping or extra rules. That closes Experiment
128's open frontier.

If it doesn't: we learn which assumption of RAW 131 is too strong.
Specifically:
- If the tree is too sparse near mass: mass doesn't bend space enough.
- If the branching is too fast: over-stretching, `g_rr > 1/(1 − L_grav)`.
- If the relation is wrong functionally: RAW 131's diagnosis is wrong
  and the problem is deeper.

---

## Phase 4 — Cosmological Horizon from LCA Depth

### Goal

Verify that entities whose LCA is the primordial seed cannot exchange
state updates within the current tick count. That is, the cosmological
horizon falls out of LCA geometry.

### Setup

- Build a tree with an obvious "primordial" root.
- Pick two leaves whose LCA is at or very near the root.
- Perturb one; measure whether the other ever sees the perturbation
  within N ticks, for various N.

### Observables

- First-arrival tick for the perturbation.
- Compare to `2 · d_LCA`.

### Success criteria

- First-arrival tick = `2 · d_LCA` exactly.
- If the universe's age in ticks is T and `d_LCA > T/2`, no arrival
  within lifetime. That pair is beyond the horizon.

---

## Phase 5 — Pattern Coherence on the Tree (Exp 55/56 integration)

### Goal

Place a multi-entity "planet" pattern on the tree. Test whether its
spatial extent adapts to local tree density such that internal coherence
is preserved under radial motion.

### Setup

- Build the Phase 3 tree with non-uniform branching near a "star"
  region.
- Define a "planet" as a small connected subtree of leaves whose
  lineages share recent ancestry.
- Move the planet radially toward the star. Measure:
  (a) spatial extent of the planet subtree,
  (b) internal tick-rate variation across the planet,
  (c) pattern integrity (does the subtree stay connected?).

### Observables

- `extent_radial(r)` and `extent_tangential(r)` as functions of distance
  to star.
- Internal tick-rate variance as a function of r.

### Success criteria

- Planet's proper (internal) size is invariant.
- Coordinate radial extent grows as `1/(1 − L_grav)` as planet nears
  star, preserving proper size against local tick-rate gradient.
- This IS radial GR for extended objects.

---

## Open Questions Going In

1. **What is the flow rule?** `+1/tick` enters every entity. Does it flow
   only up toward the root, only down toward leaves, or bidirectionally?
   Each choice gives different physics; we'll have to pick one and justify.
   A natural starting choice: each entity forwards a fraction of its
   received energy up to parent; parent redistributes to all children.
2. **What tree building rule?** Is the tree fixed at construction time,
   or does it grow (new leaves being born) during the simulation?
   Phase 0/1 use fixed trees for simplicity; Phase 5 may need dynamic.
3. **How is mass defined?** Not obvious. Candidate: mass of a pattern =
   number of entities in its subtree. Candidate: mass = total `+1/tick`
   flow it contributes. These might give different coupling laws.
4. **How to reconcile with Java lineage?** The Java codebase has entity
   lineage (tick-of-birth, parent tracking, fission into children), but
   its dynamics are spatial (collision at same position, momentum
   movement). Does the tree substrate predict a specific form for those
   dynamics, or is the Java substrate a higher-layer visualization of
   the tree's lineage flow?

---

## Failure Mode Catalog (what to write down if it doesn't work)

| Phase | What's tested | If it fails, what we learn |
|---|---|---|
| 0 | Newton from tree | Tree topology does not naturally give 1/r² — need a different branching rule or flow rule |
| 1 | Newton with 3D embedding | Embedding rule is wrong; tree is not self-similar enough |
| 2 | Tangential Schwarzschild | Something in RAW 131 breaks Phase 5's scalar γ result — very serious |
| 3 | Radial Schwarzschild | Tree density doesn't produce 1/(1 − L_grav) — the whole motivation of RAW 131 is wrong, or the mapping mass → local branching is too simple |
| 4 | Horizon | LCA depth doesn't limit causal contact — tree is not actually the full story |
| 5 | Pattern coherence | Planet doesn't stretch, or stretches wrongly — Exp 55/56 frontier still open |

A failure anywhere is informative. The goal is to discriminate between:
- the ontology is right but needs refinement
- the ontology is wrong and Exp 128's RGG was closer after all
- the problem is somewhere we haven't looked (e.g., not substrate, not
  pattern — maybe the flow rule is the missing layer)

---

## One-Sentence Summary

Experiment 131 tests whether a lineage tree substrate, with `+1/tick`
flowing through always-present ancestral connections, reproduces
everything Experiment 128 earned (1/r², Kepler, tangential Schwarzschild,
equivalence principle) plus the one thing it couldn't (Schwarzschild
radial) as a consequence of pattern coherence on a non-uniform tree.
