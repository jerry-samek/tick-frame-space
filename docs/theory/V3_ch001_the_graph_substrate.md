# V3 Chapter 1: The Graph Substrate

### *Physical Foundation of the Tick-Frame Universe*

**Version:** 3.0
**Date:** March 2026
**Status:** Consolidated from RAW 111, RAW 112
**Supersedes:** V2 ch001 (Temporal Ontology)
**Key sources:** RAW 122 (The Derivation Chain), RAW 111 (Space Is Connections), RAW 112 (The Single Mechanism)
**Experimental status:** Mechanisms validated on lattice substrates; graph substrate under active testing

---

## Abstract

This chapter establishes the physical foundation of the V3 tick-frame theory: the
universe is a graph. Nodes connected by edges constitute the entire substrate. There is
no manifold, no metric tensor, no coordinate system, no continuum at any scale. All
physical phenomena reduce to a single operation applied by every entity at every
tick: deposit on a connector, hop, connector extends. Connectors are not geometric
edges added as primitives; they are persistent chains of deposits linking nodes,
accumulated over time. The graph is append-only: every deposit is permanent, every
connector extension is permanent, every hop leaves a permanent record in the topology.
Nothing that has happened can be undone.

The graph substrate is not an assumption. It is derived from two observations that
cannot be denied without self-contradiction: *existence exists* and *process exists*.
From these, self-recognition (1=1) follows as the minimal operation, the trit
(Same/Different/Unknown) follows as the minimal vocabulary, and the append-only graph
follows as the minimal structure that can accumulate results without deletion. The full
derivation is in RAW 122 (The Derivation Chain). This chapter develops the graph's
physical consequences.

This framework claims to derive gravity, inertia, momentum, cosmological expansion,
and zero-point energy from the single operation, with no additional mechanisms and
approaching zero free parameters. One parameter -- deposit strength per hop -- remains
underived as of March 2026.

The chapter distinguishes carefully between what the theory predicts, what lattice-based
simulations have demonstrated, and what remains unvalidated on the graph substrate
itself. The single mechanism is a theoretical claim. The simulations approximate it.
The gap between the two is explicitly documented.

---

## 1. Core Claim

The substrate of the universe is a graph: a collection of nodes connected by edges.
Nothing else exists. There is no space in which the graph is embedded. There is no time
external to the graph's update cycle. The graph is not a model of something more
fundamental. It is the fundamental thing.

This claim is derived, not assumed. The derivation (RAW 122) proceeds:

1. **Existence exists** — undeniable; denial uses existence.
2. **Process exists** — undeniable; denial is a process.
3. Existence + process → the minimal operation is self-recognition: **1=1** (RAW 117).
4. Self-recognition requires a vocabulary of exactly three outcomes: **Same, Different,
   Unknown** (RAW 113). A binary system cannot represent the unresolved frontier.
   More than three states introduces redundancy not derivable from the root observations.
5. Results cannot be deleted (deletion would require something to un-exist, contradicting
   observation 1). Therefore the substrate is **append-only**.
6. Self-recognition + trit + append-only = **an ever-growing graph** where nodes are
   entities, edges are permanent records of interactions, and growth proceeds by addition
   only, never by removal.

From this substrate and one operation, the theory claims that all observable physics
emerges. The operation is:

```
deposit on a connector -> hop -> connector extends
```

The claim is strong and specific. It is falsifiable: if any physical phenomenon requires
a mechanism that cannot be reduced to this operation, the claim is wrong. The sections
that follow develop the operation from its components and trace its claimed consequences.

---

## 2. The Three Primitives

### 2.1 Nodes

A node is a discrete site. It exists or it does not. Nodes have no intrinsic properties
beyond existence and the state they carry. They have no position, no coordinates, no
spatial embedding. The concept of "where a node is" has no meaning at the substrate
level. Location is a derived quantity that emerges from the pattern of connections
(Chapter 3, Emergent Geometry).

### 2.2 Edges

An edge is a connection between two nodes. It exists or it does not. All edges are
equivalent at the primitive level -- there is no "length" of an edge. An edge connects
node A to node B; that is its entire content.

RAW 111 introduces edges as one of three primitives alongside nodes and state. RAW 112
then argues that edges are not actually independent primitives but are themselves
deposit chains (Section 3 below). This reduces the primitive count, but for clarity
this chapter presents the construction in stages: first the graph with edges as given,
then the identification of edges with deposit history.

### 2.3 State

Each node carries a value. In the tick-frame model, this value is an integer quantum
count in balanced ternary (+1, 0, -1). State propagates along edges. The rules governing
propagation are local: a node reads only the state of its immediate neighbors (nodes
connected by direct edges).

### 2.4 What Is Not Primitive

The following quantities are derived from the three primitives, not assumed:

| Quantity            | Derivation from graph                                        |
|---------------------|--------------------------------------------------------------|
| Distance            | Minimum hop count between two nodes                          |
| Speed of light      | 1 hop per tick -- the maximum propagation rate along edges   |
| Velocity            | Hops per tick for a moving pattern (always <= c)             |
| Mass                | Commitment cost: ticks required to update state before hop   |
| Energy              | Bound quanta in a self-sustaining pattern                    |
| Momentum            | Direction persistence of a moving pattern's deposit trail    |
| Gravity             | Gradient in external quantum density across connectors       |
| Dimension           | Local property of the connection pattern, not the substrate  |
| Geometry            | Observer reconstruction from causal latency, not physical    |
| Spacetime curvature | Variation in connection density across the graph             |

None of these require coordinates, metrics, or embedding dimensions.

---

## 3. Connectors as Deposit Chains

### 3.1 What a Connector Actually Is

RAW 112 makes a specific claim about the nature of edges: a connector between node A
and node B is not an independent primitive object. It is a persistent chain of deposits
linking A to B.

When an entity at node A deposits gamma (the theory's term for the quantum field value)
and that deposit propagates to node B, the propagation path constitutes the connector.
The connector exists because deposits were made along that path. It persists because
deposits are append-only and cannot be removed.

The claim, stated precisely:

> A connector IS a deposit chain. There are no connectors independent of deposits.

If this claim holds, it unifies the two apparent primitives -- field deposits and graph
edges -- into one. The graph is not a pre-existing substrate on which deposits occur.
The graph IS the accumulated deposit history, rendered as topology.

### 3.2 The Reduction of Primitives

Under this identification:

- **Before RAW 112:** Three primitives (nodes, edges, state).
- **After RAW 112:** Two primitives (nodes, state). Edges are derived from state
  history.

This is a theoretical claim, not an experimental result. The current simulations
(Experiment 64_109, all versions through v24) use graphs with pre-existing edges.
No simulation has yet constructed edges from deposit history alone. The connector
formation rule -- what determines which nodes become connected when sufficient deposit
density accumulates between them -- remains an open question (Section 10.2).

### 3.3 Consequences If the Claim Holds

If connectors are deposit chains, then:

1. **The graph topology is fully determined by field history.** Space is entirely
   derived from what has happened, not from initial conditions.

2. **New connections form where deposits accumulate.** Two previously unconnected
   nodes can become connected if the deposit field between them reaches sufficient
   density. This provides a mechanism for topology change without ad hoc edge creation
   rules.

3. **Connections cannot be destroyed.** Since deposits are permanent (Section 5),
   once a connector exists, it exists forever. It can be diluted by expansion until it
   carries negligible signal, but the deposit chain remains structurally present.

4. **The initial graph must be minimal.** If edges are deposit chains, the graph at
   the first tick has no edges (no deposits have occurred). The first deposit creates
   the first connector. This is addressed in Section 7 (The First Deposit).

---

## 4. The Single Operation

### 4.1 Statement

The theory claims that all physics reduces to one operation, applied by every entity
at every tick:

```
1. Read local field state (connector growth rates at current node)
2. Select the laziest connector (least resistance path)
3. Deposit on that connector
4. Hop to the neighboring node
5. Connector extends (deposit adds to the chain, making it longer)
```

Nothing else exists in the theory. No forces are added by hand. No expansion parameter
governs the growth rate. No decay constant removes old deposits. No drag coefficient
limits velocities. No jitter amplitude introduces noise. The theory claims that every
observable phenomenon is a consequence of this operation iterated across all entities
over all ticks.

### 4.2 Derived Consequences

The theory derives the following from the single operation. Each derivation is
summarized here and developed in detail in the indicated section.

**Gravity (Section 4.3).** A massive entity deposits continuously onto its local
connectors. Those deposits spread through the graph. At a distant node, connectors
pointing toward the mass carry different growth characteristics (suppressed by higher
deposit density) than connectors pointing away (lower deposit density). A second entity
at that node reads this asymmetry and selects the lower-resistance connector -- which
points toward the mass. The theory claims that gravity is local connector asymmetry
produced by another entity's deposit history.

**Inertia (Section 4.4).** A massive entity has more accumulated internal state --
more deposits to redistribute per hop. More deposits to spend means more ticks before
the next hop completes. The theory claims that inertia is deposit commitment cost per
hop: heavier patterns are slower not because a force resists them, but because they
have more to deposit before moving.

**Momentum (Section 4.5).** Between hops, an entity's previous deposits created a
connector trail that favors continued motion in the same direction. The entity does not
need to be pushed to continue moving. The theory claims that momentum is the inertia
of the deposit trail -- direction persists until a new hop reads new connector
asymmetry.

**Expansion (Section 4.6).** Every hop deposits onto the traversed connector. Every
deposit adds to the connector chain. A longer chain is a longer connector. Across the
entire graph, the cumulative effect of all deposits on all connectors is that distances
between all nodes increase. The theory claims that cosmological expansion is the
accumulated connector extension from all hops ever taken.

**Zero-point energy (Section 4.7).** An entity embedded in an expanding substrate
cannot be perfectly stationary. Expansion continuously extends the connectors around
it, shifting its neighboring nodes. The theory claims that zero-point energy is the
irreducible jitter produced by the substrate's own expansion acting on every embedded
entity.

### 4.3 Gravity as Connector Asymmetry

Consider a star (a dense deposit pattern at some node S) and a planet (a lighter
pattern at distant node P). The star deposits gamma onto its local connectors
continuously. Those deposits spread through the graph topology. At P, the connectors
pointing toward S carry higher cumulative deposit density than connectors pointing
away from S. In the expansion formula used by the current simulations:

```
growth = H / (1 + alpha * (gamma_A + gamma_B))
```

Higher gamma on a connector means a larger denominator, which means less growth.
Less growth means a shorter connector. The planet reads local connector states and
selects the laziest -- the one with least resistance, which is the one pointing
toward S (shorter, less growing). The planet hops toward the star.

The theory's claim: gravity is not a force transmitted through spacetime. It is a
local read operation on connector states that happen to be asymmetric because of
another entity's deposit history. No graviton, no curvature tensor, no action at
a distance. Just local field reads producing directed hops.

**Experimental status:** Gravity from deposit-spread-follow has been demonstrated on
lattice graphs in Experiment 64_109 v1-v9 (RAW 111, Section 3.1). Attraction works
on any connected graph, including random Watts-Strogatz graphs. On random geometric
graphs (v22-v24), the force produces curved trajectories and dissipative capture,
but closed orbits have not been achieved as of March 2026. The gap between "curved
trajectory" and "closed orbit" is under active investigation (v24).

### 4.4 Inertia as Commitment Cost

An entity with mass M has more accumulated internal deposit structure. Before it can
hop, it must commit its current state -- redistribute its deposits across its internal
structure. More deposits means more ticks per commitment cycle. The entity's velocity
is v = c/M: one hop every M ticks.

This relationship was first imposed by design in Experiment 64_109 v5 (commit-counter
mechanism). In v6, when gamma was quantized as integers, the same relationship emerged
from quantum statistics: individual quanta cannot split, so each quantum goes to one
neighbor per tick. The resulting diffusion coefficient scales as D ~ 1/M^2, giving
v_rms ~ c/M without explicit programming of the mass-velocity relation.

**Experimental status:** v = c/M validated on cubic lattice in v5. Integer quantum
statistics producing the same relation validated in v6. Not yet tested on random
geometric graphs.

### 4.5 Momentum as Trail Persistence

An entity moving in direction d deposits along connectors in that direction. Those
deposits reinforce the connector trail behind the entity. When the entity reaches its
next node and reads local connector states, the connectors in the forward direction
(continuation of d) are slightly favored by the trail's recent deposit history.
Direction persists until a sufficiently strong asymmetry (from another entity's
deposits) nudges the internal direction vector.

In the simulation, this is implemented as a continuous internal direction vector that
each hop nudges by a force term divided by mass (Experiment 64_109 v9). Over many hops,
small gradient-induced nudges accumulate and the direction rotates smoothly despite
the discrete hop substrate.

**Experimental status:** Continuous momentum on discrete substrate validated in v9 on
cubic lattice. Three-body scattering with angular momentum approximately conserved for
100,000 ticks. On random geometric graphs (v22-v24), momentum direction is maintained
through the leapfrog integrator, but long-term conservation has not been demonstrated.

### 4.6 Expansion as Accumulated Extension

This is the most distinctive claim of the single mechanism. The theory says: there
is no dark energy. There is no cosmological constant. There is no separate expansion
mechanism. Expansion is what happens when every entity deposits on every traversed
connector at every tick. Each deposit extends the connector slightly. Summed across
all entities and all connectors, the total extension per tick is the expansion rate.

The theory predicts:
- More entities moving faster produces more deposits per tick, producing faster expansion.
- Fewer entities or slower movement produces less deposit, producing slower expansion.
- Accelerating expansion corresponds to increasing total movement activity as structures
  form, process, and radiate.

In the current simulations, expansion is implemented as a global parameter H applied
to all connectors every tick. This is explicitly a placeholder for the correct
mechanism: connectors should extend only when traversed. The H parameter is the final
global constant that the theory claims should be eliminable (Section 8.2).

**Experimental status:** Global H-driven expansion is used in all versions of
Experiment 64_109. Traversal-driven expansion (the theory's prediction) has not been
implemented or tested. The transition from H to traversal-driven extension is identified
as a primary target for future work.

### 4.7 Zero-Point Energy as Expansion Jitter

An entity sitting at a node in an expanding graph experiences continuous perturbation:
its connectors grow, its neighbors drift, the local field shifts beneath it. Even
without deliberate movement, the substrate moves. The minimum field disturbance
experienced by any entity embedded in an expanding substrate is:

```
ZPE = minimum connector extension from expansion * local field coupling
```

The theory claims this is the origin of zero-point energy: not vacuum fluctuations
of unknown provenance, but the irreducible jitter of the expanding substrate acting
on everything embedded in it.

**Experimental status:** ZPE jitter was modeled in earlier experiments (RAW 072) on
continuous field substrates. It has not been derived quantitatively from expansion
rate on the graph substrate.

---

## 5. The Append-Only Guarantee

### 5.1 The Core Principle

Every deposit is permanent. Every connector extension is permanent. Every hop leaves
a permanent record in the graph topology. The theory models the universe as an
append-only ledger. Information is added; nothing is removed.

This is not a design choice motivated by aesthetics. It follows from the identification
of connectors with deposit chains: if a deposit is a physical event that occurred, it
cannot un-occur. The chain of deposits constituting a connector is a causal history.
Causal histories do not have deletions.

### 5.2 What "Nothing Can Be Destroyed" Means Physically

The append-only guarantee has specific physical consequences:

**Deposits persist forever.** A deposit made at tick 1 still exists at tick 10^100.
It has been diluted by expansion -- the connector it sits on has grown enormously,
reducing the deposit's contribution to local field density -- but the deposit itself
is structurally present in the graph topology.

**Connectors persist forever.** Once two nodes are connected by a deposit chain, they
remain connected. Spatial separation through expansion makes the connector very long,
reducing the signal it carries to negligible levels. But the edge exists. The two
nodes remain graph-adjacent even if they are cosmologically distant.

**Entities leave permanent wakes.** Every entity that has ever moved has deposited
along its path. Those deposits are the entity's causal history encoded in the graph.
In principle, the entire history of an entity's trajectory is readable from the
deposit topology, though in practice expansion dilutes old deposits beyond any
feasible detection threshold.

**The graph only grows.** Nodes are added (at the expanding frontier). Edges are
added (as deposit chains form). Neither is ever removed. The total information
content of the graph increases monotonically with tick count.

### 5.3 Dilution Is Not Destruction

A critical distinction: the append-only guarantee does not prevent the effective
weakening of old deposits. Expansion dilutes everything. A deposit that was significant
at tick 100 may be cosmologically negligible at tick 10^9. But "negligible" is not
"absent." The information is still there. It is spread across an enormously larger
graph, each piece contributing an infinitesimal fraction of the local field density.

In the integer substrate model (where gamma takes values in {0, 1} per node), dilution
means that the deposit-occupied nodes become an increasingly sparse subset of the total
graph as expansion adds new empty nodes. The deposits do not shrink. The graph grows
around them.

---

## 6. Connection to Unitarity and the Information Paradox

### 6.1 Unitarity

In quantum mechanics, unitarity is the principle that the total probability of all
possible outcomes remains exactly 1 -- information is never created or destroyed, only
transformed. The append-only guarantee provides a substrate-level mechanism for this:
the graph ledger never loses entries. Every quantum of information deposited into the
graph persists in the topology.

The theory claims that unitarity is not an axiom to be imposed on quantum mechanics
but a consequence of the physical substrate being append-only. If the substrate cannot
delete, the physics on that substrate cannot lose information. Unitarity is inherited.

### 6.2 The Black Hole Information Paradox

The information paradox arises from the apparent conflict between two principles in
standard physics: (1) information cannot be destroyed (unitarity), and (2) black holes
evaporate completely via Hawking radiation, leaving no record of what fell in.

In the graph model, the conflict does not arise. A black hole is an extremely dense
deposit region -- a subgraph with very high gamma density. Hawking-like evaporation
(demonstrated emergently in Experiment 64_109 v6 as stochastic boundary fluctuations
driving quantum escape cascades) disperses the deposits outward, diluting them across
an expanding graph. The deposits are not destroyed. They are spread. The information
about what fell in is encoded in the topology of the evaporated deposit distribution.

In practice, the dilution is so extreme that reconstruction is infeasible. But the
theory does not require practical reconstruction -- it requires that the information
remains structurally present. The append-only ledger guarantees this.

**Experimental status:** Hawking-like evaporation was observed in Experiment 64_109 v6
on a cubic lattice. Self-gravitating integer quantum clusters dissolved over approximately
2 million ticks through a positive-feedback cascade: quantum escapes from the boundary
weakened the peak, increasing escape probability, leading to complete dissolution. This
was not designed into the model; it emerged from integer statistics on the graph. The
information content of the dissolved cluster was not tracked, so the specific claim
about information preservation has not been experimentally tested.

### 6.3 Entanglement as Persistent Connection

RAW 111 proposes that quantum entanglement can be reframed as a graph phenomenon. Two
entangled particles share a direct edge (connector) that does not correspond to spatial
proximity in the main graph. This edge is a deposit chain formed during their original
interaction. Spatial separation through expansion makes the connector very long but
does not delete it (append-only guarantee).

The correlation between entangled measurements is then not "spooky action at a distance"
but a local graph operation: the two nodes ARE neighbors (connected by a direct edge),
even though they are spatially distant (many hops apart through the main graph). The
measurement at one end updates state along the shared connector in one tick, regardless
of the spatial hop count through the bulk graph.

**Experimental status:** This is a theoretical proposal. No simulation has tested
entanglement as persistent connector on the graph substrate.

---

## 7. The First Deposit

### 7.1 Symmetry Before the First Tick

Before any deposit: perfect equality. If the substrate begins as nodes with no state
and no edges (following the strict connector-as-deposit-chain identification), then
at tick zero there is no distinction between any two nodes. No gradient. No asymmetry.
No laziest connector. No preferred direction.

If the substrate begins with some minimal edge structure but zero state, the same
holds: every node is identical to every other node up to graph isomorphism.

### 7.2 The Symmetry-Breaking Event

The first deposit breaks this symmetry. A single deposit at one node creates a
distinction: this node has state, that node does not. The first asymmetry creates the
first gradient. The first gradient creates the first laziest connector (or, in the
strict model, the first deposit chain and therefore the first connector). The first
lazy connector enables the first hop. The first hop extends the first connector.

From that point forward, the single operation runs. Everything else is consequence.

### 7.3 The Minimum Unearned Assumption

The first deposit is the only event in the framework that is not derived from a prior
state. It is not explained by the theory. It is the minimum unearned assumption:
smaller, the theory argues, than any assumption in existing physics frameworks. Not a
singularity with infinite density. Not a quantum fluctuation with a probability
amplitude requiring a pre-existing Hilbert space. Not a multiverse selection event.

Just: one deposit at one node, once. The loop had to start somewhere.

The theory does not claim this is satisfying. It claims it is minimal. Whether
minimality of unearned assumptions is a virtue is a philosophical question, not a
physical one.

---

## 8. The Parameter Count

### 8.1 Parameters Eliminated by the Single Mechanism

Early simulations of tick-frame physics required multiple explicit parameters, each
encoding a mechanism that the theory now claims should emerge from the single operation:

| Parameter        | Purpose in early simulations         | Status under single mechanism       |
|------------------|--------------------------------------|-------------------------------------|
| Decay rate       | Prevent field saturation             | **Eliminated.** Expansion dilutes deposits without deletion. |
| Drag coefficient | Prevent velocity runaway             | **Eliminated.** Force-on-hop prevents runaway structurally. |
| Jitter amplitude | Introduce ZPE-like noise             | **Eliminated.** Derived from expansion rate (Section 4.7). |
| Expansion rate H | Control cosmological expansion       | **Claimed eliminable.** Theory derives expansion from total movement activity. Not yet implemented (see 8.2). |
| Deposit strength | Control gravitational field buildup  | **Residual.** Currently tunable. Should emerge from entity mass (see 8.3). |

### 8.2 The H Parameter: Placeholder for Traversal-Driven Expansion

In the current simulations (Experiment 64_109 v1-v24), expansion is controlled by
a global parameter H applied to all connectors every tick. The theory predicts that
H should not exist: connectors should extend only when traversed by an entity making
a deposit.

The self-pinning phenomenon discovered in v22 Phase 0 provides partial evidence for
this: dense deposit regions automatically resist H-driven expansion because their
high gamma density suppresses the growth formula's numerator. The simulation
self-corrects toward traversal-driven behavior despite using a global H.

However, the H placeholder has a known discrepancy: it applies expansion to
connectors that have never been traversed by any entity. In the correct mechanism,
those connectors would not extend at all. Removing H and implementing true
traversal-driven extension is the path to eliminating this parameter.

**Status:** Not implemented. The transition to traversal-driven expansion is
identified as a primary future target.

### 8.3 The Residual Parameter: Deposit Strength

The remaining tunable parameter is the deposit strength -- how much gamma an entity
deposits per hop. The theory claims this should emerge from the entity's internal
structure: an entity with more accumulated deposits should naturally spend more per
hop. The precise functional relationship has not been derived.

A universe with one mechanism and no free parameters is the theory's target. The
current simulation has one parameter remaining. Whether it can be eliminated without
introducing implicit assumptions elsewhere is an open question.

---

## 9. Self-Pinning: Dense Bodies Resist Expansion

### 9.1 The Discovery

During Experiment 64_109 v22 Phase 0 (March 2026), an emergent behavior was observed:
a star that deposits gamma continuously onto its local connectors creates a dense
field region where the expansion formula's denominator becomes large. Large denominator
means near-zero growth. The star's own deposit field suppresses expansion in its
neighborhood.

The effect is automatic. No special mechanism distinguishes expanding regions from
non-expanding regions. The deposit density itself makes the distinction:

- **Dense regions** (stars, planets, bound structures): high local gamma, large
  denominator, growth approaches zero. Local graph stays geometrically stable.
- **Empty voids**: zero gamma, denominator equals 1, connectors extend at full rate.
  Voids expand freely.
- **Net result**: expansion happens in empty regions. Dense regions opt out. This
  produces the observed Hubble flow pattern: galaxies do not expand, the space
  between them does.

### 9.2 The Pinning Frontier

The star's pinning radius grows over time. At early ticks, only the star's immediate
neighborhood is pinned. As deposits accumulate and the gamma field spreads outward,
the pinning frontier extends to larger radii.

v22 Phase 0 measurements with H=0.00001:

```
tick  5k:  g10/g5 = 0.321, delta = +0.016/1k ticks
tick 10k:  g10/g5 = 0.379, delta = +0.010/1k ticks
tick 15k:  g10/g5 = 0.425, delta = +0.009/1k ticks
tick 20k:  g10/g5 = 0.463, delta = +0.007/1k ticks
converging toward 0.500 (1/r equilibrium)
```

The star needed approximately 25-30k ticks to pin its field to r=10. The theory
interprets this as physically real: the time for the deposit wavefront to establish
stable field density at orbital distances is not a numerical artifact but the actual
time required for the single mechanism to propagate its effects outward.

### 9.3 Implications

Self-pinning supports the single mechanism's claim that expansion and gravitational
stability are not separate mechanisms requiring separate parameters. They are two
regimes of the same operation, distinguished by local deposit density.

**Experimental status:** Self-pinning was observed on a random geometric graph in v22
Phase 0 with a global H parameter. The observation is robust (repeated across multiple
H values). However, this is self-pinning against a global expansion parameter, not
self-pinning in a traversal-driven expansion regime. The theory predicts that
traversal-driven expansion would make self-pinning exact rather than approximate, but
this has not been tested.

---

## 10. Open Questions

### 10.1 The Connector Formation Rule

If connectors are deposit chains, what determines when two nodes become connected?
Does sufficient deposit density between two nodes automatically create a connector?
Is there a threshold? What is it?

This is arguably the most important open question in the V3 framework. If the
connector formation rule can be specified precisely, the graph topology becomes fully
determined by the deposit field, and the number of independent substrate properties
drops to the minimum. If it cannot be specified without introducing a new parameter,
the claim of zero free parameters fails.

### 10.2 Deposit Strength from Entity Mass

The single remaining tunable parameter -- deposit strength per hop -- should emerge
from the entity's internal deposit structure. An entity with more accumulated deposits
should naturally spend more per hop. The functional form of this relationship has not
been derived. Candidates include:
- Linear: deposit = k * mass (proportional spending)
- Square root: deposit = k * sqrt(mass) (diminishing returns)
- Logarithmic: deposit = k * log(mass) (asymptotic limit)

Without a derived deposit-mass relationship, the framework cannot claim zero free
parameters.

### 10.3 Traversal-Driven Expansion

The theory predicts that connectors extend only when traversed. The simulations use
a global H parameter applied to all connectors every tick. Implementing true
traversal-driven extension would:
- Eliminate the H parameter
- Make self-pinning exact rather than approximate
- Predict that a two-body system with one stationary star and one slowly moving
  planet experiences nearly zero expansion
- Allow quantitative comparison between predicted and observed Hubble constant

This is the highest-priority implementation target for closing the gap between theory
and simulation.

### 10.4 The Anti-Newtonian Scaling Problem

Experiment 64_109 v24 discovered that increasing star mass by 10x produced a 15x
weaker force at the orbital radius. The force law's denominator grows with gamma
density, so a more massive star suppresses its own gradient. This produces anti-
Newtonian scaling: more mass, less force.

The theory's response: this is a float arithmetic artifact. In the true integer
substrate where gamma takes values in {0, 1} per node, the denominator is bounded
at 2x maximum, and pathological self-suppression cannot occur. But this response
has not been validated. Implementing integer gamma deposits with hop-carried
propagation (rather than float diffusion) is required to test whether the force law
scales correctly in the discrete regime.

### 10.5 Closed Orbits on the Graph Substrate

As of March 2026, no version of Experiment 64_109 has achieved a closed orbit on
a random geometric graph. The progression:

| Version | Substrate        | Best result                              |
|---------|------------------|------------------------------------------|
| v1-v9   | Cubic lattice    | Three-body scattering, 100k ticks        |
| v22     | Random geometric | First curved trajectories, escape at 16k |
| v23     | Random geometric | Radial reversal, dissipative capture      |
| v24     | Random geometric | Anti-Newtonian scaling discovered         |

The lattice experiments (v1-v9) demonstrated gravitational attraction, inertia,
mass-velocity relation, Brownian motion, Hawking-like evaporation, and three-body
scattering -- all on a substrate with pre-defined local dimensionality. The random
geometric graph experiments (v22-v24) have demonstrated force, deceleration, curved
trajectories, and capture, but not stable orbits.

The theory predicts that closed orbits will emerge once the force law scales correctly
(either through integer gamma or distributed star mass). This prediction is testable
and falsifiable.

### 10.6 Quantitative Predictions

The framework currently has no quantitative predictions that distinguish it from
standard physics at accessible energy scales. The theory claims that the Hubble
constant H_0 should equal the mean deposit-per-hop across all entities in the
observable universe, and that the baryon asymmetry ratio (approximately 1 in 10^9
matter particles per photon) should be derivable from three-state encounter statistics
in an expanding field. Neither derivation has been completed.

---

## 11. Relationship to General Relativity

General relativity describes spacetime as a smooth Lorentzian manifold with curvature
determined by the stress-energy tensor. The graph model makes no reference to manifolds
or tensors.

The theory claims the relationship is one of emergence:

**GR is the continuum limit.** When node counts are large and connection patterns are
regular, the graph's properties converge to those of a smooth manifold. Hop counts
become continuous distances. Tick counts become continuous time. Connection density
variation becomes curvature. GR is the large-N approximation of the graph substrate.

**GR describes the result; the graph describes the cause.** Einstein's equations
relate curvature to energy distribution but do not explain why mass curves spacetime.
In the graph model, mass is a self-sustaining pattern that alters local connection
utilization through deposits. The curvature (connection density variation) is a
consequence of the deposit pattern's presence.

**GR breaks at singularities; the graph does not.** The graph has a natural minimum
distance: 1 hop. There is no zero-distance singularity, no infinite density. The
graph simply has a minimum resolution. Black holes are extremely dense deposit
regions, not infinities.

These claims are structural, not quantitative. The theory has not shown that the
graph model reproduces the Einstein field equations in any limit. This would require
demonstrating that the graph's connection density variations, under the deposit-hop-
extend operation, satisfy the specific tensor relationship that GR prescribes. No
such derivation exists.

---

## 12. Why the Graph Is Undetectable from Inside

RAW 111 argues that the discrete graph substrate is undetectable by any measurement
apparatus embedded in the graph, for a specific structural reason: co-deformation.

Every measurement instrument is itself a pattern on the graph. A ruler is a chain of
bound quanta spanning some number of hops. A clock is a cyclically committing pattern
counting its own ticks. When the graph structure changes -- connection density
increases, connectors extend, topology deforms -- the ruler changes by the same
factor. It is made of the same substrate. The measurement returns the same number.

The speed of light appears constant in all reference frames because it is not a speed
in the conventional sense. It is the structural propagation rate: one hop per tick
along edges. Every observer, regardless of their own motion pattern, measures the same
thing: state changes propagate at one hop per tick. There is no relative velocity to
add or subtract because the observer's motion and the signal's propagation are both
hop sequences on the same graph.

This argument predicts the null results of Michelson-Morley-type experiments. It also
predicts that no experiment conducted with apparatus embedded in the graph can
distinguish the graph from a continuum at any scale -- the discreteness is hidden by
co-deformation, the same way a digital photograph's pixels are invisible when the
camera is also pixelated at the same resolution.

**Caveat:** The co-deformation argument is qualitative. A rigorous proof would require
showing that every possible measurement apparatus made from graph patterns produces
results indistinguishable from continuous-spacetime predictions. This has not been
done.

---

## 13. Summary

The V3 theory claims:

1. **The universe is a graph.** Nodes and edges. Nothing else at the substrate level.

2. **Connectors are deposit chains.** Edges are not independent primitives; they are
   accumulated deposit histories linking nodes.

3. **One operation produces all physics.** Deposit on a connector, hop, connector
   extends. Gravity, inertia, momentum, expansion, and zero-point energy are all
   claimed to be consequences of this operation iterated universally.

4. **The graph is append-only.** Nothing is destroyed. Every deposit persists forever.
   Dilution by expansion reduces effective signal strength but does not remove
   structural information.

5. **The parameter count approaches zero.** Four previously tunable parameters
   (decay, drag, jitter, expansion rate) have been eliminated or are claimed
   eliminable. One residual parameter (deposit strength) remains.

6. **The first deposit is the only underived event.** Everything after follows from
   the single operation. The theory does not explain why the first deposit occurred.
   It claims this is the minimum possible unearned assumption.

**What has been demonstrated:**
- Gravity from deposit-spread-follow: validated on lattice graphs (v1-v9)
- Inertia as commitment cost: validated on lattice graph (v5-v6)
- Hawking-like evaporation from integer statistics: observed on lattice graph (v6)
- Three-body scattering with approximate angular momentum conservation: validated on
  lattice graph (v9)
- Star formation and self-pinning: observed on random geometric graph (v22)
- Curved trajectories and dissipative capture: observed on random geometric graph
  (v22-v23)

**What has not been demonstrated:**
- Closed orbit on graph substrate (lattice or random)
- Traversal-driven expansion replacing global H
- Integer gamma with hop-carried propagation
- Connector formation from deposit accumulation
- Any quantitative prediction distinguishing the theory from standard physics
- Recovery of Einstein field equations in the continuum limit

The gap between what the theory claims and what simulations have shown is large. The
theory is internally coherent and has produced qualitatively correct gravitational
behavior in multiple experiment versions. Quantitative validation of its core claims
remains the primary objective.

---

## References

- **RAW 111** -- Space Is Connections (February 2026). Establishes graph substrate,
  three primitives, co-deformation argument.
- **RAW 112** -- The Single Mechanism (March 2026). Derives all physics from deposit-
  hop-extend. Identifies connectors as deposit chains.
- **Experiment 64_109 v1-v9** -- Three-body dynamics on cubic lattice graph. Gravity,
  inertia, Brownian motion, Hawking evaporation, three-body scattering.
- **Experiment 64_109 v22** -- Star formation on random geometric graph. Self-pinning
  discovery. First curved trajectories.
- **Experiment 64_109 v23** -- Larger domain. Radial reversal and dissipative capture.
  Closed orbit not achieved.
- **Experiment 64_109 v24** -- Stronger gradient. Anti-Newtonian scaling from float
  self-suppression.
- **RAW 072** -- Jitter Scaling and Matter Growth (ZPE derivation, continuous field
  substrate).
- **RAW 108** -- Three Dimensions from Trit Change Geometry.
- **RAW 109** -- Speed of Light and Isotropy from Graph Topology.
- **RAW 110** -- Local Dimensionality as Critical Variable for Orbital Mechanics.

---

*Date: March 19, 2026*
*Status: V3 CONSOLIDATED*
*Supersedes: V2 ch001 (Temporal Ontology)*
*Depends on: RAW 111, RAW 112*
*Opens: Connector formation rule, deposit strength derivation, traversal-driven
expansion, integer gamma implementation, closed orbit target*
