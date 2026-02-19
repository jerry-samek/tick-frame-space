# RAW 111: Space Is Connections

**Author:** Tom  
**Date:** February 2026  
**Status:** Working document  
**Prerequisites:** RAW 109 (c and isotropy from topology), RAW 110 (local dimensionality), Experiment 64_109 v1–v9

---

## Abstract

This document establishes that physical space is not a fundamental entity. There is no manifold, no metric tensor, no
continuum. Space is an emergent description of a graph: nodes connected by edges. Distance is hop count. Time is a tick
counter. The speed of light is one hop per tick — a structural fact, not a dynamical constant. What we experience as
spacetime geometry is the view from inside the graph, where every measurement instrument is itself a pattern on the same
substrate, co-deforming with it, and therefore unable to detect the discreteness directly.

This claim is supported by nine iterations of Experiment 64_109, which demonstrate that gravitational attraction,
inertia, orbital dynamics, conservation laws, and Hawking-like radiation all emerge from integer quanta spreading on a
graph — with no spatial coordinates used in the physics.

---

## 1. The Claim

Physical space is not a container in which events occur. It is the pattern of connections between discrete nodes. Two
entities are "near" each other if they are connected by few hops. They are "far" if connected by many hops. There is no
underlying continuous space in which the nodes are embedded. The graph IS the space.

This is not an approximation. It is not "space is discrete at the Planck scale but continuous above it." The continuum
does not exist at any scale. What appears continuous is the result of very large hop counts between macroscopic objects,
the same way a digital photograph appears continuous when the pixel count is high enough.

---

## 2. Primitives

The model requires exactly three primitives:

1. **Nodes** — discrete sites that either exist or do not.
2. **Edges** — connections between nodes. An edge either exists or it does not. There is no "length" of an edge. All
   edges are equivalent.
3. **State** — each node holds a value (in the tick-frame model: an integer quantum count in balanced ternary). State
   propagates along edges.

From these three primitives, the following quantities are derived, not assumed:

| Derived quantity    | Definition                                                          |
|---------------------|---------------------------------------------------------------------|
| Distance            | Minimum hop count between two nodes                                 |
| Time                | Global tick counter (commit cycle)                                  |
| Speed of light      | 1 hop per tick — the maximum rate of state propagation              |
| Velocity            | Hops per tick for a moving pattern (always ≤ c)                     |
| Mass                | Commitment cost: ticks required to update state before hopping      |
| Energy              | Bound quanta in a self-sustaining pattern                           |
| Momentum            | Internal direction vector of a moving pattern                       |
| Gravity             | Gradient in external quantum density (deficit from absorbed quanta) |
| Spacetime curvature | Variation in connection density across the graph                    |

None of these require coordinates, metrics, or embedding dimensions.

---

## 3. What Experiment 64_109 Proved

Nine versions of the three-body experiment on a graph systematically established which features of physics require
spatial geometry and which do not.

### 3.1 Gravity Is Topological (v1)

Deposit-spread-follow produces attraction on ANY connected graph, including random Watts-Strogatz graphs with no spatial
structure. Entity A deposits gamma, the field spreads outward through edges, entity B reads the gradient pointing toward
A's deposit peak, and moves toward it. The mechanism requires only graph connectivity.

**Implication:** Gravitational attraction does not require space. It requires connections.

### 3.2 Orbits Require Local Dimensionality (v1–v2, RAW 110)

On a random graph, entities attract but collapse to the same node. There is no perpendicular direction to sustain
angular momentum. On a lattice graph (where each node has structured neighbors corresponding to orthogonal directions),
entities overshoot and remain in bound orbits.

**Implication:** Orbital mechanics requires local dimensionality — a property of the connection pattern, not of an
embedding space. The lattice provides this structure. The random graph does not.

### 3.3 Movement Is Existence (v3)

Entities that stop moving freeze permanently (the d=0 singularity). When every entity hops every tick — with gradient as
preference, not permission — the system self-regulates. Entities pass through each other and separate naturally.

**Implication:** In the graph model, existence requires continuous state propagation. A pattern that stops propagating
ceases to exist. This is not a design choice; it is forced by the model's failure modes.

### 3.4 Mass Is Commitment Cost (v5)

An entity with mass M sits at its current node for M ticks before hopping. Its velocity is exactly v = c/M. This is not
imposed — it emerges from the commit-counter mechanism. The entity needs M ticks to process its state before making a
decision. Heavier patterns are slower because they have more internal state to commit.

**Implication:** The relationship between mass and velocity is structural, not dynamical. There is no force slowing down
massive objects. They are simply slower to commit.

### 3.5 Integer Quanta and Emergent Brownian Motion (v6)

When gamma is quantized as integers, individual quanta cannot split. Each quantum goes to ONE neighbor per tick. This
breaks the symmetry of deterministic diffusion and produces genuine Brownian motion of cluster centers. The diffusion
coefficient scales as D ~ 1/M², giving v_rms ~ c/M — the same mass-velocity relation that v5 imposed by fiat.

**Implication:** The mass-velocity relation is not a model choice. It is a consequence of integer quantum statistics on
a graph.

### 3.6 Hawking-Like Evaporation (v6)

Self-gravitating integer clusters are metastable. Stochastic boundary fluctuations drive a positive-feedback cascade: a
quantum escapes → the peak weakens → escape probability increases → more quanta escape. Without a restoring force, peaks
dissolve in approximately 2 million ticks.

**Implication:** The discreteness of quanta introduces an evaporation mechanism analogous to Hawking radiation. This was
not designed into the model. It emerged from integer statistics on the graph.

### 3.7 Self-Subtraction Enables Detection (v8)

A pattern's own gamma (~400 at center) drowns any signal from a distant pattern (~0.05 at 10 hops). By tagging each
quantum with its source entity and computing external_gamma = total − own_tag, entities become sensitive to each other's
fields. Distance decreases from 10 to 4 hops in 50,000 ticks. Three-body dynamics emerge with close encounters and
rebounds.

**Implication:** Self-interaction must be subtracted for gravity to function. This is the graph analog of self-energy
regularization in field theory. The principle is not optional — without it, no pattern can detect any other pattern.

### 3.8 Continuous Momentum on Discrete Substrate (v9)

A 6-neighbor lattice quantizes hop directions to 90° steps. No gradient can deflect an entity from one lattice direction
to another in a single step. The solution: the entity maintains a continuous internal direction vector. Each hop, the
gradient nudges this vector by 1/mass. The actual hop goes to whichever lattice neighbor is closest. Over many hops, the
small nudges accumulate and the direction rotates smoothly.

Three-body simulations with tangential initial momentum show genuine gravitational scattering: entities approach,
deflect, rebound, and reapproach for 100,000 ticks without merger or escape. Angular momentum is approximately
conserved.

**Implication:** Internal state can be continuous even when the substrate is discrete. The pattern's trajectory is
smooth; only the individual hops are quantized. This is analogous to sub-pixel rendering — the accumulated path has
higher resolution than any single step.

---

## 4. Why the Graph Is Undetectable from Inside

The Michelson-Morley experiment found no evidence of a preferred frame or discrete substrate. This is predicted by the
graph model, not contradicted by it.

Every measurement instrument is itself a pattern on the graph. A ruler is a chain of bound quanta spanning some number
of hops. A clock is a cyclically committing pattern counting its own ticks. When the graph structure changes (e.g.,
connection density increases), the ruler changes by the same factor — it is made of the same stuff. The measurement
returns the same number.

This is co-deformation: the measuring apparatus and the measured phenomenon share the same substrate. Any change to the
substrate affects both equally. From inside, the graph looks continuous, isotropic, and homogeneous — because every
deviation is invisible to instruments built from the same deviating material.

The speed of light appears constant in all reference frames because it is not a speed. It is the structural propagation
rate: one hop per tick. Every observer, regardless of their own motion (which is a pattern of hops), measures the same
thing: state changes propagate at one hop per tick along edges. There is no relative velocity to add or subtract because
the observer's motion and the signal's propagation are both hop sequences on the same graph.

---

## 5. Reinterpreting Spacetime Concepts

### 5.1 Distance

Not a property of space. A property of the graph. The minimum hop count between two nodes. This is always a non-negative
integer. "Continuous distance" is the macroscopic approximation when hop counts are large.

### 5.2 Time

Not a flow. A counter. The global tick at which all state commits atomically. Each tick: read committed state, compute
new state, commit. Time is discrete, universal (within a causal domain), and irreversible (the tick counter only
increments).

### 5.3 Spacetime Curvature

Not bending of a manifold. Variation in connection density. A region with more connections per node has shorter
effective distances (fewer hops to traverse). A massive pattern, by binding quanta to local nodes, alters the connection
utilization — paths through the pattern are modified. Distant patterns respond to this altered topology. That response
is gravity.

### 5.4 Dimensions

Not fundamental. The graph has no intrinsic dimension. Dimensionality is a LOCAL property of the connection pattern (RAW
110). A node with 6 neighbors arranged as ±x, ±y, ±z has local dimensionality 3. A node on a random graph has local
dimensionality ~0. The fact that our observable universe appears 3-dimensional means the local connection pattern of the
substrate is approximately cubic — not that "3D space exists."

### 5.5 Expansion

The graph can grow. New nodes, new edges. Connection density decreases. Hop count between distant regions increases.
From inside, measured with co-deforming rulers, this appears as expansion of space. Accelerating expansion (dark energy)
corresponds to accelerating graph growth.

---

## 6. Implications

### 6.1 Disconnected Regions

If a subgraph has no edges connecting it to our connected component, it is undetectable by any signal propagating
through connections. It has mass (bound quanta). It has internal dynamics. But no photon can reach it. No gravitational
quantum can leak from it to us.

Such regions would be gravitationally invisible and electromagnetically dark. Their presence might be inferred only
through their influence on the graph topology itself — if the existence of a disconnected mass region changes the global
structure (path counts, connection density) of the connected component. The degree to which this occurs, and whether it
accounts for observed phenomena attributed to dark matter or dark energy, is an open question that requires further
theoretical development.

### 6.2 Causality and the Speed Limit

The speed of light is not a speed limit on objects. It is the propagation rate of causality through connections. An
entity bonded to the graph (with active connections to neighboring nodes) cannot exceed this rate because its state
updates propagate through those bonds.

An entity with NO active connections to the graph is not constrained by hop-distance or propagation rate. It has no
position in the graph. When it reconnects, it can do so at any node — not because it "traveled faster than light," but
because it was never in the spatial graph during the disconnected interval. This mechanism may relate to quantum
tunneling: the entity does not traverse the intermediate nodes. It disconnects and reconnects.

### 6.3 Entanglement

Two entities sharing a direct bond (edge) that does not correspond to spatial proximity in the graph — i.e., an edge
that shortcuts the local structure — would exhibit correlated state changes without a signal propagating through the
spatial graph. The correlation is not "faster than light." It is not in space at all. The bond exists outside the
spatial connection pattern. Measuring one end updates state along the bond edge in one tick, regardless of the spatial
hop count between the two nodes.

This reframes entanglement from a nonlocal spatial phenomenon to a local graph phenomenon: the two nodes ARE neighbors (
connected by an edge), even though they are spatially distant (many hops apart through the main graph). The mystery
dissolves when space is recognized as a derived quantity and graph adjacency as fundamental.

---

## 7. Relationship to General Relativity

General relativity describes spacetime as a smooth Lorentzian manifold with curvature determined by the stress-energy
tensor. The graph model makes no reference to manifolds or tensors. The relationship between the two frameworks is one
of emergence:

- **GR is the continuum limit.** When the node count is large and the connection pattern is regular, the graph's
  properties converge to those of a smooth manifold. Hop counts become continuous distances. Tick counts become
  continuous time. Connection density variation becomes curvature.

- **GR cannot see the mechanism.** Einstein's equations describe the relationship between curvature and energy. They do
  not explain WHY mass curves spacetime. In the graph model, mass is a self-sustaining pattern that alters local
  connection utilization. The curvature (connection density variation) is a consequence of the pattern's presence. GR
  describes the result. The graph model describes the cause.

- **GR breaks at singularities.** The graph model has a natural minimum distance: 1 hop. There is no zero-distance
  singularity. No infinite density. No information paradox. The graph simply has a minimum resolution.

---

## 8. Open Questions

1. **Maximum connectivity per node.** Is there a fundamental limit on the number of edges per node? If so, what
   determines it? Preliminary considerations suggest a connection to the balanced ternary (trit) structure of the
   tick-frame model, where each node may have a small fixed number of connectors. The consequences of bounded
   connectivity for phase structure and state formation require separate treatment.

2. **Graph dynamics.** Do edges form and break? If so, what rules govern their creation and destruction? Static graphs
   produce static spacetime. Dynamic graphs could produce expansion, contraction, and topology change.

3. **Recovery of known physics.** The experiments demonstrate gravitational attraction, inertia, and three-body
   scattering. Do electromagnetic phenomena, quantum interference, and nuclear forces also emerge from the same
   substrate? Experiments 66+ address some of these questions.

4. **Observational signatures.** If the graph model is correct, what observable predictions distinguish it from
   continuous spacetime at accessible energy scales? Candidates include Planck-scale angular momentum noise (observed in
   v9 as ±8 oscillation from lattice quantization) and discrete signatures in gravitational wave spectra.

5. **Classical limit.** The v9 three-body results show gravitational scattering rather than clean Keplerian orbits. The
   stochastic gamma field introduces noise at the quantum level. The transition from quantum-noisy scattering to clean
   classical orbits should occur as quanta counts increase (many quanta averaging out fluctuations). This transition has
   not yet been demonstrated computationally.

---

## 9. Summary

Space is not a thing. It is a description of how things are connected. Distance is counting hops. Time is counting
ticks. The speed of light is one hop per tick. Mass is a pattern that takes multiple ticks to commit. Gravity is
detecting the deficit left by another pattern's bound quanta. Orbital mechanics is momentum being nudged by that deficit
over many hops.

Nine experiment versions, each failing in a specific way, each pointing toward the next piece of real physics, converged
on a model where three entities interact gravitationally on a discrete graph with exact integer conservation, no
programmed forces, and no spatial coordinates in the physics. The graph is the space. The connections are the geometry.
Everything else is what it looks like from inside.

---

## References

- RAW 109 — Speed of light and isotropy from graph topology
- RAW 110 — Local dimensionality as critical variable for orbital mechanics
- Experiment 64_109 v1–v9 — Three-body dynamics on graph substrate
- Beane, S.R. et al. (2012) — Constraints on the universe as a numerical simulation
