# RAW 131 — The Lineage Substrate

### *Connections Are Ancestral, Not Spatial*

**Author:** Tom (insight), Claude (articulation)
**Date:** April 18, 2026
**Status:** Reframing draft. Tests pending in Experiment 131.
**Prerequisites:** RAW 128 (Energy Partition), RAW 130 (It Rotates Because It Consumes)
**Closes:** Experiment 128 v11 Phases 6/6b/6c/6d/6e — four converging
negatives on radial Schwarzschild from isotropic-RGG + linear-local rules

---

## Abstract

Experiment 128 v11 earned 1/r² field geometry, Keplerian orbits, and exact
Schwarzschild **tangential** proper time — all on a 3D random geometric
graph (RGG) substrate with isotropic diffusion. It **did not** earn
Schwarzschild **radial**: four diagnostics on the same substrate (edge-flow
anisotropy, per-node flux vector, proper-time discrepancy integration,
gradient-biased propagation) all converged on the same negative. The
substrate reads radial gravity as `gamma ∝ (1 − L_grav)` where GR reads
`g_rr = 1/(1 − L_grav)` — reciprocal in shape, off by exactly
`sqrt(1 − L_grav)` in gamma-ratio.

This RAW proposes the failure is ontological, not parametric: the RGG is
the wrong substrate. The substrate is a **lineage tree**, not a spatial
graph. Spatial distance is derived, not primitive. Propagation does not
build connections — connections are already there through common
ancestry, established when the two lineages split. What the `+1/tick`
mechanism does is **flow** along those always-present connections, not
establish them.

The super-ionic state of Earth's inner core provides the intuition pump:
an iron lattice (static structure) with hydrogen flowing through it
(dynamic fluid). The structure doesn't move; the fluid does. In our
framework, the lineage tree is the lattice and `+1/tick` energy is the
fluid.

---

## 1. The Lattice and the Fluid

In a super-ionic state, the iron lattice is crystalline — its topology
is fixed. Hydrogen ions stream through the lattice's pre-existing
channels. The channels don't form as the hydrogen flows; they were there
first. The flow just uses them.

Map this onto tick-frame:

**Lattice (structure, static):** the lineage tree. Every entity has
exactly one parent (the entity it split from). The tree is built
incrementally as entities split, but each edge, once established, is
permanent. Two entities whose lineages diverged at entity A are connected
through A — forever — regardless of where they drift spatially.

**Fluid (flow, dynamic):** the `+1/tick` per entity. Every global tick,
every entity receives one unit of energy for continuing to exist. That
unit enters the tree at the entity and propagates along its lineage
edges. The flow pattern through the tree determines correlations between
distant entities.

Under this reading, a "gravitational connection" between the star and
the Earth is not a force field propagated through space. It is a
continuous shared-lineage update, mediated by the tree path that connects
them through their lowest common ancestor.

---

## 2. The Two Modes of Connection

Lineage delivers two distinct things to any pair of entities (S, P):

### 2.1 Correlation (static)

S and P share every ancestor above their LCA. Their connection *exists*
from the moment their lineages split. No message traverses anywhere to
establish the bond — it is a structural fact of the tree.

Consequence: the influence of a pattern on another pattern is present
from the moment the two lineages separate, not after a signal arrives.
Gravity has always been there.

### 2.2 Change-propagation (dynamic)

If S's state changes, how does P learn? Only through the tree. Signal
travels up S's subtree to the LCA, then down P's subtree to reach P.

Let `d_LCA(S, P)` = depth of the lowest common ancestor below both S and
P. Update time between S and P is `2 · d_LCA(S, P)`.

**Consequence — the speed of light.** For a self-similar tree (branching
factor approximately constant, volume at depth d scaling as d³ in 3D
spatial embedding), the LCA depth of a spatially-distant pair scales
linearly with spatial distance:

```
d_LCA(r) ≈ α · r
```

Update time = `2α · r`. The ratio `r / update_time = 1 / (2α)` is a
constant. That constant is `c`.

Under this ontology, `c` is not a speed of anything in space. It is the
rate at which state changes traverse the lineage tree, which *projects*
onto spatial distance at a fixed ratio because the tree is self-similar.
The "ancient node" at which two distant entities meet is not a bottleneck
— it is an unavoidable waypoint, and the path length through it is what
**defines** spatial distance in this framework.

---

## 3. Consequences

### 3.1 The cosmological horizon is LCA-depth-limited

Two entities whose LCA is the primordial seed cannot exchange a completed
state update within the current tick count. That is, literally, the
cosmological horizon. The universe's age in ticks puts an upper bound
on how far a change can traverse through the lineage tree, which
translates to a maximum spatial reach.

Observationally: light from the edge of the observable universe was
emitted ~13.8 Gyr ago, near the primordial era. Its emission source sits
near the primordial seed in the lineage tree. That "near the beginning
of time" is precisely the condition for being at the horizon.

### 3.2 Spatial distance is a derived quantity

Spatial distance does not need to be assumed. It falls out of lineage
geometry:

```
r(A, B) := d_LCA(A, B) / α
```

where `α` is the tree's self-similarity constant. Geometric 1/r² laws
(Newton, Coulomb) become consequences of tree branching, not assumptions.
For 3D embedding, the number of descendants at depth d scales as d³;
two distinct depth-d descendants are at spatial distance ~d; the
"interaction density" at distance r is proportional to 1/(number of
entities at depth r) ≈ 1/r³... and the flux through a sphere scales as
1/r², recovering Newton.

*(This derivation is sketched, not finished. Experiment 131 tests it.)*

### 3.3 Why tangential Schwarzschild was easy, radial was hard

An entity is a point on the tree. Time dilation is a property of that
point — how fast `+1/tick` flows in its local subtree context. That's a
scalar local quantity. It projects onto tangential (perpendicular-to-r)
motion without any asymmetry, because tangential motion is motion along
lines of constant LCA depth. Phase 5's exact-Schwarzschild tangential
result **is** tree-topology preserving motion.

Radial motion is motion between different LCA depths. It crosses lineage
shells. The effective "length" of a radial step is not one tree edge —
it depends on how the lineage tree is structured locally. In a tree with
non-uniform branching, a radial step can require more tree traversal per
unit spatial distance in regions where the tree is "denser." That is
the `1/(1 − L_grav)` stretching factor.

Under this reading, the factor is not a property of space and not a
property of a substrate connector. It is a property of **lineage tree
density** — how much tree-traversal is required per unit spatial extent
in regions where many entities share recent ancestry (i.e., near mass).

### 3.4 Phase 6 negative results are feature, not bug

The isotropic RGG used in Experiment 128 v11 Phases 1–6 projects spatial
geometry directly into the substrate. It was the shortest path to 1/r²,
and it worked. But the RGG has no lineage information. Every edge is
symmetric; no node has a notion of "who its parent is." Directional
asymmetries that depend on shared ancestry cannot exist on a pure RGG.

Four diagnostics confirmed this: no scalar observable on the RGG + linear
rules reads `1/(1 − L_grav)`. The diagnoses were not telling us the
framework was wrong — they were telling us we had the wrong substrate.

### 3.5 Pattern coherence has a natural definition

A pattern on a lineage tree is a set of entities whose lineages share
sufficient recent ancestry that they are updated coherently by the same
`+1/tick` flows. The "planet" is not an arbitrary cluster of spatial
nodes — it is a subtree. Pattern coherence is preserved iff the subtree
stays intact.

Radial motion of a planet near mass crosses LCA shells. The subtree has
to re-anchor at each shell. The cost of re-anchoring scales with how
much ancestry is newly shared or newly diverged — which in strong field
is exactly the `1/(1 − L_grav)` factor, on this framing. Pattern
coherence on a lineage tree *is* g_rr stretching.

---

## 4. What Survives From Experiment 128

| Result                                        | Earned on RGG | Expected to survive on tree                 |
|-----------------------------------------------|---------------|---------------------------------------------|
| 1/r² field geometry                           | Phase 1       | Yes — from tree self-similarity             |
| Keplerian orbits                              | Phase 2       | Yes — same mathematics, rederived           |
| Mass-independence of orbital period           | Phase 3.1     | Yes, but needs reinterpretation             |
| Gravitational redshift 1/r shape              | Phase 4       | Yes — local tick-rate invariant             |
| Exact Schwarzschild tangential                | Phase 5       | Yes — tangential = constant-LCA-depth       |
| Exact Schwarzschild radial                    | *Failed*      | Open — to derive in Exp 131                 |
| Perihelion precession                         | *Not tried*   | Open                                        |

The "failed" line is what motivated this RAW. The "open" lines are what
Experiment 131 must address.

---

## 5. Falsification Targets for Experiment 131

1. **Newton on the tree.** Build a minimal lineage tree with two seeds
   (star, planet) sharing an LCA at depth d. Let `+1/tick` flow. Measure
   the apparent "force" between them (defined as something concrete —
   e.g., correlation strength, or rate of momentum transfer via the tree
   path). Does it scale as `1 / r²` when `r = d_LCA / α`?

2. **Tree self-similarity.** Does a tree with branching factor roughly
   constant and 3D spatial embedding produce the linear `d_LCA ∝ r`
   relation needed for finite c?

3. **Horizon.** Two entities whose LCA is the primordial seed should
   have no mutual influence within the current tick count. Verify.

4. **Pattern coherence.** A multi-node pattern on the tree should adapt
   its radial extent in regions of high local branching density such
   that its effective "proper size" stays fixed. The adaptation factor
   should be `1/(1 − L_grav)`. This is the full radial GR test.

If (1)–(3) pass, we have a tree ontology that recovers all Experiment
128 results at less cost. If (4) passes, we have radial GR earned.

If any fail, we know which subset of the intuition is wrong, and by how
much.

---

## 6. What This Does Not Claim

- That the tree **is** the substrate in the ultimate sense. Only that it
  is a better substrate than the RGG for the class of problems
  Experiment 128 uncovered.
- That `+1/tick` and lineage connections are sufficient for all physics.
  Quantum effects, electromagnetism, collision physics — none of these
  are addressed here.
- That the derivation of spatial distance from lineage depth is complete.
  Section 3.2 sketches it. Experiment 131 is where it has to be tested
  or abandoned.

---

## 7. One-Sentence Summary

The connection between two patterns was always there — established when
their lineages split from a common ancestor — and what each tick delivers
is not a new connection but `+1/tick` worth of flow through the one that
already exists; spatial distance, the speed of light, and Schwarzschild's
radial stretching are consequences of how the lineage tree is structured,
not of anything propagating through space.
