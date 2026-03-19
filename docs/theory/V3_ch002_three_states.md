# Chapter 2: The Three-State Alphabet

---

## Abstract

Chapter 1 established the graph substrate and its single operation: deposit on a connector, hop,
connector extends. This chapter asks: what happens at the point of arrival? When an entity reaches a
node and its arriving pattern meets the existing deposit state, what are the possible outcomes?

The answer is that exactly three outcomes exist. The arriving pattern either **matches** the existing
deposits (Same), **diverges** from them (Different), or **encounters a node with no deposits**
(Unknown). These three states are not physical categories imposed from outside. They are the
exhaustive logical partition of all possible relationships between any arriving pattern and any
existing node state. No fourth state is constructible.

The theory proposes that these three comparison outcomes map directly onto the three fundamental
physical behaviours of the substrate: gravity (Same), radiation (Different), and expansion (Unknown).
If this mapping holds, the universe does not contain three separate forces or mechanisms. It contains
one comparison, applied at every node, at every tick, producing three possible results --- and those
results, accumulated across the graph, are what observers reconstruct as gravitational attraction,
electromagnetic radiation, and cosmological expansion.

This chapter derives the three-state alphabet from the single mechanism of Chapter 1, develops the
proposed physical mapping for each state, presents the theory's account of photon properties as path
geometry rather than intrinsic signal properties, and states plainly what remains unvalidated.

**Key source:** RAW 113 (Semantic Isomorphism: Same / Different / Unknown)

**Status:** The three-state mapping is a theoretical proposal. No experiment has yet tested whether
gravity, radiation, and expansion correspond to these three comparison outcomes. The mapping is
internally consistent and emerges naturally from the single mechanism, but internal consistency is
not validation.

---

## 2.1 Core Claim

**The substrate produces exactly three comparison outcomes at every node. These three outcomes are
the complete physical alphabet of the universe.**

| State | Condition | Operation | Proposed physical mapping |
|---|---|---|---|
| **Same** | Arriving pattern matches existing deposits | Follow --- no new structure created | Gravity |
| **Different** | Arriving pattern diverges from existing deposits | Branch --- this divergence IS the information | Radiation |
| **Unknown** | No deposits at node --- never visited | Write --- graph grows | Expansion |

The claim has three parts:

1. **Exhaustiveness.** These three are the only possible outcomes of comparing an arriving pattern to
   an existing node state. No fourth relationship exists.

2. **Physical correspondence.** Each outcome maps onto a distinct, observable physical phenomenon.
   The mapping is not arbitrary --- it follows from what each comparison outcome *does* to the graph
   structure.

3. **Unification.** Gravity, radiation, and expansion are not three forces requiring three separate
   explanations. They are three results of one operation.

---

## 2.2 Derivation: Why Three States and No More

### 2.2.1 The Comparison at Arrival

Recall from Chapter 1 the single mechanism (RAW 112): an entity arrives at a node, reads the local
state, deposits, and hops. The reading step is a comparison. The entity's arriving pattern --- its
accumulated deposit signature from prior traversals --- meets whatever deposits already exist at the
node.

This comparison has a definite structure. The node is in one of two conditions: it carries deposits
(it has been visited before), or it carries none (it has never been visited). If it carries deposits,
the arriving pattern either matches them or it does not.

This gives three cases:

1. **Node has deposits, and they match the arriving pattern.** The entity recognises the existing
   state as consistent with its own history. This is Same.

2. **Node has deposits, and they do not match.** The entity encounters a state that diverges from its
   own deposit signature. This is Different.

3. **Node has no deposits.** There is nothing to compare against. No match or mismatch is possible.
   This is Unknown.

### 2.2.2 No Fourth State Exists

The three cases are exhaustive because they partition a binary property (deposits exist / deposits do
not exist) and, within the "deposits exist" branch, a binary comparison (match / no match). The tree
is:

```
Does the node carry deposits?
  |
  +-- No  --> Unknown
  |
  +-- Yes --> Does the arriving pattern match?
                |
                +-- Yes --> Same
                |
                +-- No  --> Different
```

There is no room for a fourth state. Any candidate for a fourth state must either:

- Be a subcase of one of the three (e.g., "partial match" is a subcase of Different --- the pattern
  diverges, even if only partially), or
- Require a third branch at the top level (neither "deposits exist" nor "deposits do not exist"),
  which contradicts the law of excluded middle for a discrete graph where node state is either
  present or absent.

The exhaustiveness does not depend on the details of the comparison operator. Whatever formal
definition "match" eventually receives (see Open Questions, Section 2.8), the logical structure
remains: match, no match, or nothing to compare against. Three states. No more.

### 2.2.3 Relationship to the Append-Only Axiom

The append-only guarantee from Chapter 1 constrains what happens *after* each comparison:

- **Same** does not create new graph structure. The entity follows existing connectors. Nothing is
  appended to the topology (though the deposit reinforces the existing path).

- **Different** creates a new branch. The divergence point is recorded as new structure in the graph.
  This is an append operation.

- **Unknown** creates a new node entry. The entity writes its state into previously unvisited
  territory. This is also an append operation.

Only Same is non-creative --- it traverses existing structure without extending the graph. Different
and Unknown are the two modes of graph growth. This is consistent with the append-only axiom: the
graph grows through divergence (branching at known nodes) and through frontier exploration (writing
to unknown nodes). It never shrinks, because no comparison outcome deletes structure.

---

## 2.3 Same: The Proposed Mechanism of Gravity

### 2.3.1 The Proposal

The theory proposes that gravity is the macroscopic consequence of Same firing at many nodes across
many ticks. When an entity traverses the graph, it follows the path of least resistance --- the
laziest connector, in the language of RAW 112. The laziest connector is the one whose deposits most
closely match the entity's own accumulated pattern. This is the direction where Same fires most
strongly.

Massive bodies produce dense deposit fields. Those deposits spread through connectors into the
surrounding graph. At any node near a massive body, the connectors pointing toward the body carry
dense, well-established deposits. The connectors pointing away carry sparser deposits. An arriving
entity reads this asymmetry. The direction toward the massive body is the direction where the
arriving pattern most closely matches existing deposits --- the direction of Same.

The entity follows Same. It moves toward the massive body. Accumulated across many entities and
many ticks, this produces what observers reconstruct as gravitational attraction.

### 2.3.2 What This Account Provides

If the mapping holds, several features of gravity follow without additional postulates:

**Universality.** Every entity performs the same comparison at every node. There is no entity that is
exempt from reading local deposits. Therefore every entity with a deposit signature is subject to the
routing effect of dense deposit fields. This would account for gravity's universality --- its coupling
to all forms of energy and matter --- without needing to postulate a separate gravitational charge.

**Weakness.** Same does not create new structure. It follows existing paths. It is the *absence* of
creative action --- the comparison outcome that changes nothing. A force that consists of "follow the
familiar path" is inherently weaker than forces that create or redirect structure, because it operates
by reinforcement rather than by injection of new information. The theory proposes this as the reason
gravity is weaker than electromagnetism by a factor of approximately 10^36: gravity is the routing
effect of familiarity, not the injection of new divergence. This proposal has no quantitative
derivation.

**Equivalence to inertia.** In Chapter 1 (RAW 112, Section 2.3), inertia was derived as deposit
commitment cost per hop --- an entity with more accumulated deposits takes longer to change state.
Same reinforces this: an entity following familiar deposits is an entity following its own inertial
history. The equivalence principle (gravitational mass equals inertial mass) would follow from the
fact that both are properties of the same deposit signature. The entity's resistance to acceleration
(inertia) and its coupling to external deposit fields (gravity) are both determined by how much
deposit history it carries.

### 2.3.3 Connection to Self-Pinning

Chapter 1 described field self-pinning (RAW 112, Section 2.7): dense bodies suppress local connector
growth because high gamma density in the denominator of the growth rule makes local expansion
negligible. Self-pinning is the macroscopic consequence of Same dominating locally. In a region
saturated with deposits from a massive body, every arriving entity finds Same at every node.
Connectors do not grow because no entity encounters Different or Unknown --- the region is fully
explored, fully familiar. The graph is locally frozen. This is gravitational stability.

### 2.3.4 Honest Limitations

The Same-to-gravity mapping is qualitative. The following quantitative questions are open:

- **Force law.** Does the deposit density gradient produced by the single mechanism fall off as
  1/r^2? The theory expects this from the geometry of deposit spreading through a locally
  three-dimensional graph, but no formal derivation exists. Experiment 64_109 v22 has demonstrated
  curved trajectories from deposit gradients but has not yet demonstrated a closed orbit or measured
  the force law exponent.

- **Equivalence principle.** The argument that gravitational mass equals inertial mass because both
  derive from deposit history is suggestive but not formalised. A formal proof would require a
  precise definition of "deposit signature" and a demonstration that the comparison operator treats
  the entity's own history and external deposits symmetrically.

- **Comparison operator.** The formal definition of what constitutes a "match" between arriving
  pattern and existing deposits is not established. The qualitative description --- follow the laziest
  connector, the one with deposits most similar to the entity's own --- is clear in intent but
  imprecise in mechanism. This is the most fundamental open question in the three-state framework.

---

## 2.4 Different: The Proposed Mechanism of Radiation

### 2.4.1 The Proposal

The theory proposes that radiation is the macroscopic consequence of Different propagating through
the graph. This requires a specific claim about what a photon is.

**A photon is not an entity that arrives at a node and checks its state.** A photon IS a Different
event propagating. It does not compare --- it is the comparison result, already fired, moving forward
through the graph.

When Different fires at a node --- the arriving pattern diverges from existing deposits --- the
divergence does not remain local. It propagates. The record of what differed moves through the graph
along connectors, node by node. That propagating divergence signal is the photon.

This is a significant ontological claim. In standard physics, a photon is a quantum of the
electromagnetic field --- an excitation of a field that exists everywhere. In the three-state
framework, a photon is not a thing at all. It is an event --- a Different comparison result ---
propagating through the graph.

### 2.4.2 Photon Interactions as Comparison Outcomes

The photon (propagating Different event) encounters nodes as it traverses the graph. At each node,
the propagating divergence meets the existing deposit state, and one of three outcomes fires:

- **Same fires.** The divergence pattern matches the receiving node's deposits. The signal is
  **absorbed**. Deposits reinforce. The divergence has been reconciled into the existing deposit
  structure. The propagation ceases. In standard physics terms: the photon is absorbed by an atom
  whose energy levels match the photon's frequency.

- **Different fires.** The propagating divergence encounters a different divergence. The signal
  **scatters** or **refracts**. A new branch forms. The propagation continues in a new direction. In
  standard physics terms: the photon is scattered by matter.

- **Unknown fires.** The divergence reaches the frontier --- a node with no deposits. The signal
  **writes** the divergence into new territory. The graph extends. The propagation continues into
  uncharted substrate. In standard physics terms: light propagates into empty space.

Absorption is Same. Propagation through vacuum is the signal writing into Unknown. Scattering is
Different encountering Different. The entire phenomenology of photon-matter interaction, the theory
proposes, reduces to the three-state alphabet applied to a propagating divergence event.

### 2.4.3 The Speed of Propagation

A Different event propagates at one hop per tick. This is the maximum rate of state propagation
through the graph --- the speed of light. It is not a dynamical constant tuned to a specific value.
It is a structural fact about the substrate: information crosses one edge per tick, and cannot cross
more, because the tick function is local (Chapter 1, Section 2.1).

The universality of *c* --- the fact that all photons travel at the same speed regardless of their
source's motion --- follows from the fact that Different always propagates at one hop per tick. The
propagation rate is a property of the substrate, not of the signal. The source's motion affects the
pattern that fires Different, not the rate at which the result propagates.

---

## 2.5 Photon Properties as Path Geometry

### 2.5.1 The Central Claim

At the substrate level, the Different signal carries nothing except the fact that it fired and the
path it took. There is no frequency encoded in the signal. There is no amplitude. There is no
polarization. These quantities do not exist as intrinsic properties of the propagating divergence.

All observable photon properties are **path geometry** --- properties of the sequence of nodes the
Different event traversed and the directions in which it fired.

This is perhaps the most counterintuitive claim in the three-state framework. Standard physics treats
frequency, amplitude, and polarization as intrinsic properties of the electromagnetic wave. The
theory proposes instead that they are descriptions of the path structure, reconstructed by the
absorbing observer from the topological signature of the arriving signal.

### 2.5.2 Frequency as Firing Rate

**Frequency** is the rate of Different events per unit branch depth along the propagation path.

A high-frequency photon fired Different rapidly at many successive nodes. Each node it traversed
triggered a divergence comparison. The path is densely punctuated with branching events.

A low-frequency photon coasted through long runs of Same between events, firing Different rarely. The
path has long stretches of traversal through familiar deposits, interrupted by infrequent divergence
events.

The difference between a gamma ray and a radio wave, in this account, is not a difference in the
signal. It is a difference in how often the propagating divergence encountered non-matching deposits
along its path. Dense, highly structured regions produce high-frequency paths (many divergence events
per depth). Sparse, uniform regions produce low-frequency paths (few divergence events per depth).

When the signal arrives at an absorbing node, what gets deposited is the topological signature of the
path --- the sequence of Same and Different firings. The absorber reads the firing rate from this
signature. That is what is measured as frequency.

### 2.5.3 Amplitude as Parallel Path Count

**Amplitude** is the number of parallel paths carrying the same Different signal simultaneously.

A bright signal is many parallel branches, all carrying coherent divergence patterns. A dim signal
is few branches. Amplitude is not a property of a single path --- it is a property of how many paths
fire coherently.

This maps onto the standard quantum account where intensity is proportional to photon number. Each
parallel path is one "photon." The total amplitude is the superposition of all parallel paths.

The critical distinction from standard physics is ontological: in the standard account, photon number
is a property of the field mode. In the three-state account, photon number is the count of parallel
branches in the graph that carry the same divergence signature.

### 2.5.4 Polarization as Firing Direction

**Polarization** is the geometric orientation of the Different firing directions relative to the
local graph structure.

At each node, the divergence event fires along specific connectors. Which connectors the divergence
preferred --- the directional pattern of the branching --- encodes the polarization state. Vertical
polarization means the divergence consistently fired along one axis of the local graph neighbourhood.
Horizontal polarization means it consistently fired along a perpendicular axis. Circular polarization
means the firing direction rotated systematically with each successive node.

Polarization is substrate geometry, not signal property. It is determined by the relationship between
the propagating divergence and the local connector structure at each node along the path.

### 2.5.5 Interference as Deposit Arithmetic

Interference follows naturally from the path geometry account.

Two Different signals arriving at the same node from different paths carry different topological
signatures. Each signature encodes a sequence of divergence events --- a pattern of Same and
Different firings.

- **Constructive interference.** The two path signatures are in phase --- their Different firing
  patterns align. Their deposits add. The node receives reinforced divergence. The combined signal
  is stronger than either individual path.

- **Destructive interference.** The two path signatures are out of phase --- their Different firing
  patterns are offset by half a cycle. Their deposits partially or fully cancel. The node receives
  reduced or zero net divergence.

No wave equation is needed. No superposition principle is postulated. The geometry of arrival at a
single node determines the interference outcome. Two paths, each carrying a topological record of
their traversal, meet at a node. The deposits add or subtract depending on the relative alignment of
their firing patterns.

This is deposit arithmetic, not wave mechanics. The theory proposes that what observers describe as
the wave nature of light is the substrate performing addition and subtraction of path geometries at
shared nodes.

### 2.5.6 Honest Limitations of the Path Geometry Account

The photon-as-path-geometry proposal is qualitative. The following are not yet established:

- **Spectral lines.** The theory claims frequency is the firing rate of Different events per depth.
  For this to be physically meaningful, the ratio of firing rates for different paths must reproduce
  the observed frequency ratios for known spectral lines (e.g., the Balmer series of hydrogen).
  No such derivation exists.

- **Planck's relation.** The relationship E = hv, connecting photon energy to frequency, would need
  to be derived from the path geometry account. Specifically: why should the energy deposited at
  absorption be proportional to the firing rate along the path? The theory does not yet answer this.

- **Quantitative interference.** The deposit addition/subtraction account of interference is
  qualitative. Reproducing quantitative interference patterns (e.g., double-slit fringe spacings)
  from the path geometry model has not been attempted.

- **Photon emission.** The account describes propagation and absorption but does not yet explain what
  triggers the initial Different event. What physical process at an emitting atom causes a divergence
  event to fire and begin propagating? The theory says "the arriving pattern diverges from existing
  deposits," but the mechanism by which an atom's state change produces a propagating Different event
  needs formalisation.

---

## 2.6 Unknown: The Proposed Mechanism of Expansion

### 2.6.1 The Proposal

The theory proposes that cosmological expansion is the macroscopic consequence of Unknown firing at
the frontier of the graph.

The graph frontier consists of nodes that have never been reached by any deposit. They carry no
state. When an entity or propagating signal reaches such a node, no comparison is possible. There is
no existing deposit to match or diverge from. The entity writes its state into the node. A new node
is instantiated in the graph's causal structure. A new connector is created. The graph grows.

This is expansion: not a force pushing matter apart, not a cosmological constant of arbitrary
magnitude, but the substrate writing itself into previously unvisited configuration space. Expansion
happens at the frontier because the frontier is, by definition, where Unknown fires.

### 2.6.2 Why Expansion Happens in Voids, Not in Galaxies

Dense regions never encounter Unknown. They are saturated with deposits --- every node has been
visited many times by many entities. The entire local graph is explored, characterised as either
Same or Different. There is no Unknown remaining.

Only the frontier, where the equilibrium search (Chapter 1) has not yet propagated, encounters
Unknown. Only there does the graph grow. This is why expansion happens in voids, not in galaxies.
The observation that galaxies do not expand while the space between them does --- the Hubble flow ---
is, in this account, a direct consequence of the three-state alphabet: dense regions are locally
exhausted of Unknown, while sparse regions are full of it.

This connects to the self-pinning mechanism described in Chapter 1 (RAW 112, Section 2.7). Dense
bodies suppress local connector growth because their high deposit density ensures Same dominates
locally. The three-state account makes this more precise: self-pinning is the local exhaustion of
Unknown. Where everything is already known, nothing grows.

### 2.6.3 The Frontier Is Permanently Young

The append-only axiom guarantees that the frontier always exists. Every Unknown node that gets
written creates new connectors. Those connectors lead to further unvisited nodes. The frontier
recedes as it is explored, but it recedes into territory that is, by construction, also unexplored.
Unknown always lies ahead of the equilibrium search.

This means expansion cannot stop. The graph always has an unvisited frontier. The universe, in this
account, does not have a fixed size that it is expanding into. The frontier IS the expansion. There
is no pre-existing space being filled. The act of encountering Unknown creates the space.

### 2.6.4 Expansion Rate as Movement Statistics

Chapter 1 established (RAW 112, Section 2.5) that the expansion rate is the mean connector extension
per tick summed across all connectors --- which equals the total deposit activity of all entities. The
three-state account adds a refinement: expansion is specifically the rate at which Unknown is
converted to known state. Every time an entity or signal writes into an Unknown node, the graph
extends. The expansion rate is the global rate of Unknown-to-known conversion.

More entities moving faster means more frontier encounters per tick. Fewer entities or slower
movement means fewer frontier encounters. The theory proposes that the accelerating expansion of the
observable universe corresponds to increasing total movement activity as structures form, process,
and radiate --- not a mysterious dark energy with arbitrary magnitude, but a ledger entry in the
append-only deposit record.

### 2.6.5 Honest Limitations

- **Hubble constant.** The theory claims expansion rate is derivable from movement statistics. This
  has not been demonstrated. A quantitative derivation should connect H_0 to the mean
  deposit-per-hop across all entities in the observable universe. If the two quantities agree without
  fitting, this would constitute a strong validation. No such derivation exists.

- **Accelerating expansion.** The qualitative account (more movement activity implies faster
  expansion) is consistent with observation but does not predict the specific acceleration profile
  measured by DESI DR2 or supernova surveys.

- **H as placeholder.** The current simulation (Experiment 64_109 v22) uses a global expansion
  parameter H applied to all connectors every tick. This is a placeholder for the correct mechanism:
  connectors extend only when traversed. The simulation has not yet implemented traversal-driven
  expansion.

---

## 2.7 The Unification Claim

### 2.7.1 One Comparison, Three Outcomes

If the three-state mapping holds, the universe does not contain three separate mechanisms:

- There is no gravitational force. There is Same --- entities following familiar deposits.
- There is no electromagnetic field. There is Different --- divergence propagating through the graph.
- There is no dark energy. There is Unknown --- the frontier being written.

The three phenomena are three outcomes of one comparison. They cannot be separated because they are
not separate things. Any node, at any tick, fires exactly one of the three. The physical consequences
accumulate from those firings.

### 2.7.2 Interaction Between the Three States

The three states do not operate in isolation. They interact through the graph dynamics:

**Same suppresses Different and Unknown.** A region saturated with familiar deposits (high Same
density) has few divergence events and no frontier. This is a gravitationally bound, stable structure
--- a galaxy, a star, an atom. Internally, it is characterised by overwhelming Same.

**Different creates new Same.** When a divergence event propagates to a node and is absorbed (Same
fires), the node's deposit state is updated. The formerly-different pattern is now incorporated into
the local deposits. Future arrivals at that node are more likely to fire Same. Radiation, over time,
homogenises the deposit field --- converting Different into Same. This is thermalisation.

**Unknown is converted by both Same and Different.** The frontier retreats as entities and signals
explore it. Every Unknown node that is written becomes either a Same node (if subsequent arrivals
match) or a Different node (if subsequent arrivals diverge). The frontier is the only source of
genuinely new structure. Once it is explored, the graph dynamics reduce to Same-vs-Different.

**Different is the source of all information.** Same traverses without creating. Unknown writes
without comparing. Only Different records a distinction --- a branch point in the graph where
something was noted as non-matching. The informational content of the universe is, in this framework,
the accumulated set of Different events. Every measurement, every observation, every bit of data is
a Different event that was recorded as a branch point and later read by a Same-following observer.

### 2.7.3 The Trie Structure

The three-state dynamics produce a specific information structure: a **trie** (prefix tree). In
the graph:

- Long runs of Same are shared branches --- entities that followed the same path traverse the same
  connectors without creating new structure.
- Different events are branch points --- the nodes where two paths diverged.
- Unknown is the unwritten frontier --- the leaves that have not yet been explored.

This means the graph is naturally organised as a compressed prefix tree. Identical histories share
branches up to the point of divergence. The universe stores only the divergence points --- the places
where something new was encountered. This is structural compression. It is not an algorithm applied
after the fact. It is the inevitable consequence of how the three states interact with the
append-only axiom.

The implications of this trie structure --- information storage, retrieval, observer identity, and
the unreachability of equilibrium --- are developed in Chapter 5.

---

## 2.8 Evidence

### 2.8.1 What the Experiments Show

The three-state alphabet is a theoretical framework. No experiment has explicitly instantiated the
Same/Different/Unknown comparison as observable states. However, certain experimental results are
consistent with the framework's predictions:

**Gravity from deposit gradients (Experiments 64_109 v1-v22).** Entities following deposit gradients
toward massive bodies is consistent with the Same account. The laziest-connector rule produces
gravitational attraction on graph substrates, including random graphs with no spatial geometry
(v1). Curved trajectories from deposit gradients have been demonstrated (v22). However, these
experiments test the single mechanism (deposit-hop-extend), not the three-state comparison
specifically. The experiments would produce identical results regardless of whether the underlying
comparison is formally Same/Different/Unknown or some other local routing rule.

**Self-pinning (Experiment 64_109 v22, Phase 0).** Dense bodies suppressing local connector growth
is consistent with the claim that Same dominates in dense regions. The simulation demonstrates that
expansion occurs in voids but not in dense regions, matching the predicted behaviour. Again, this
tests the deposit mechanism, not the three-state framework per se.

**Field spreading as propagation (Experiments 51, 64_109).** Gamma quanta propagating through the
graph at one hop per tick is consistent with Different-as-radiation. The field spreading produces
effects interpreted as radiation in the 3D visualisation. But the experiment implements field
diffusion, not a "Different event" with the specific comparison semantics described in this chapter.

### 2.8.2 What the Experiments Do Not Show

- No experiment has tested the **photon-as-Different-event** claim. The simulations model radiation
  as field diffusion, not as propagating comparison outcomes.

- No experiment has demonstrated **photon properties as path geometry**. Frequency, amplitude, and
  polarization have not been measured in any simulation as properties of traversal paths.

- No experiment has tested **interference as deposit arithmetic**. The qualitative account has not
  been instantiated computationally.

- No experiment has directly measured the **Same comparison operator**. The laziest-connector rule
  in the simulation is a proxy for the theoretical concept of Same, but the formal comparison
  between arriving entity pattern and existing node deposits has not been implemented as a distinct
  computational step.

- The three-state framework has not been tested on the **V3 graph substrate** (random geometric
  graph with deposit chains). The earlier experiments (51, 53, 55) used continuous field substrates
  or lattice substrates. The mechanism may transfer across substrates, but this has not been
  demonstrated.

### 2.8.3 What Would Constitute Validation

The three-state framework would gain significant support from the following experimental results,
in approximate order of achievability:

1. **Closed orbit from self-organised proto-disk.** If the Same routing mechanism produces a stable
   orbit --- not just a curved trajectory --- from a self-organised deposit field with no preset
   velocity, this would validate the gravitational account. This is the current target of
   Experiment 64_109 v22-v24.

2. **1/r^2 force law from deposit gradient.** Measuring the effective force between a massive deposit
   source and a test entity at varying radii, and finding inverse-square falloff, would connect the
   Same mechanism to the known gravitational force law.

3. **Different event propagation.** Implementing a simulation where a divergence event propagates
   through the graph (rather than field diffusion) and demonstrating that it behaves like radiation
   --- constant speed, absorption by matching deposits, scattering by non-matching deposits --- would
   test the Different-as-radiation claim directly.

4. **Interference from path geometry.** Implementing two propagating Different events arriving at
   the same node from different paths and demonstrating constructive/destructive interference from
   deposit addition/subtraction would test the core mechanism of the photon account.

5. **Measurable distinction between Same and Different.** If the simulation can be instrumented to
   classify each node-level comparison as Same, Different, or Unknown, and the statistical
   distribution of these classifications correlates with observed gravitational, radiative, and
   expansionary behaviour, this would test the mapping directly.

---

## 2.9 Open Questions

### 2.9.1 The Comparison Operator

What is the precise mathematical definition of "match" between an arriving entity's deposit
signature and a node's accumulated deposit state?

The qualitative description is clear: follow the laziest connector, the one whose deposits are most
similar to the entity's own history. But "most similar" requires a metric on deposit signatures. What
is that metric? Is it Hamming distance on a ternary string? A dot product on deposit vectors? A
topological property of path overlap?

This is the most fundamental open question in the framework. Without a formal comparison operator,
the distinction between Same and Different is intuitive but not computable. The three-state alphabet
cannot be implemented in simulation until this question is answered.

### 2.9.2 Photon Properties: Quantitative Derivation

The theory claims frequency is the firing rate of Different events per branch depth. For this to be
physically meaningful, the framework must derive:

- **Planck's relation.** Why is energy proportional to frequency? In the path geometry account, this
  would require showing that the energy deposited at absorption is proportional to the density of
  Different events along the propagation path. What mechanism enforces this proportionality?

- **Spectral lines.** The Balmer series and other atomic emission spectra have precise frequency
  ratios (e.g., the Rydberg formula). Can the firing rate of Different events through an atomic-scale
  deposit structure reproduce these ratios?

- **Photon emission mechanism.** What triggers the initial Different event at an emitting atom? The
  framework describes propagation and absorption but is silent on the physical process that initiates
  radiation.

### 2.9.3 Partial Match

The three-state partition treats the comparison as binary: match or no match. Physical interactions
are not binary --- they involve degrees of similarity. A photon of nearly the right frequency can
still be absorbed by an atom (line broadening). A gravitational field does not switch on and off at a
threshold distance.

How does the framework handle partial matches? The theory could accommodate this through probabilistic
firing: the closer the arriving pattern is to the existing deposits, the higher the probability of
Same firing (and the lower the probability of Different). But this introduces a probability measure
on comparison outcomes, which is not yet formalised. Whether this connects to the Born rule in quantum
mechanics is an open question.

### 2.9.4 Depth as Proper Time

RAW 113 proposes that branch depth --- the number of append operations since an observer's
depth-zero --- is proper time. If this is correct, then two observers at different locations in the
graph accumulate depth at different rates, and the ratio of their depth accumulation rates should
reproduce the Lorentz factor:

```
depth_rate_ratio = sqrt(1 - v^2/c^2)     (special relativity)
depth_rate_ratio = sqrt(1 - 2GM/rc^2)    (general relativity, weak field)
```

Does the three-state dynamics produce these specific ratios? Dense deposit regions (high Same
density) suppress local connector growth, which reduces the rate of append operations. This
qualitatively matches gravitational time dilation. But the quantitative correspondence has not been
derived or measured.

### 2.9.5 The Strong and Weak Nuclear Forces

The three-state framework as presented accounts for gravity (Same), electromagnetism (Different), and
expansion (Unknown). It does not address the strong nuclear force or the weak nuclear force.

If the framework is correct, these forces must also be consequences of the three-state comparison.
The most natural candidates are:

- **Strong force.** Same at very short range --- deposits so dense that connectors are maximally
  reinforced, binding entities together. The asymptotic freedom of the strong force (weakening at
  short distances) might correspond to Same saturating at maximum deposit density.

- **Weak force.** Different at very short range --- divergence events within tightly bound deposit
  structures, triggering decay and transformation.

These are speculative. No derivation exists.

### 2.9.6 Connector Formation

If connectors are deposit chains (Chapter 1), what determines which nodes become connected? Does
sufficient deposit density between two nodes automatically create a connector? If so, the graph
topology is entirely determined by the deposit field, and the question "why are these two nodes
connected?" reduces to "what deposit history links them?" The formal rule for connector creation or
strengthening from deposit accumulation is not yet specified.

---

## 2.10 Summary

The three-state alphabet is a theoretical framework proposing that all physical phenomena reduce to
three comparison outcomes at the substrate level:

| State | Proposed physics | What it does to the graph | Information role |
|---|---|---|---|
| **Same** | Gravity | Follows existing structure | Retrieval |
| **Different** | Radiation | Creates branches | Recording |
| **Unknown** | Expansion | Writes new nodes | Exploration |

The framework's strengths:

- **Exhaustiveness.** Three states is a logical necessity, not a design choice. No fourth state is
  constructible from the comparison of an arriving pattern to an existing node state.

- **Unification.** Gravity, radiation, and expansion are proposed as three outcomes of one operation,
  not three separate mechanisms.

- **Consistency with the single mechanism.** The three states follow naturally from the
  deposit-hop-extend operation of Chapter 1. They are not additional postulates.

- **Internal coherence.** The interactions between the three states (Same suppresses Different and
  Unknown; Different creates new Same; Unknown is consumed by exploration) produce qualitatively
  correct physical behaviour: stable bound structures in expanding voids, thermalisation of
  radiation, and perpetual frontier growth.

The framework's limitations:

- **No experimental validation.** The mapping from comparison outcomes to physical forces has not been
  tested in any simulation. The experiments to date test the deposit mechanism, not the three-state
  comparison specifically.

- **No formal comparison operator.** The definition of "match" between arriving pattern and existing
  deposits is not formalised.

- **No quantitative photon derivation.** Frequency as firing rate, amplitude as path count, and
  polarization as firing direction are qualitative proposals without quantitative derivations.

- **Nuclear forces unaddressed.** The strong and weak forces are not yet incorporated.

- **Partial match problem.** The binary Same/Different distinction does not obviously accommodate
  continuous degrees of similarity.

The chapter that follows (Chapter 3) addresses how observers reconstruct spatial geometry from a
graph that has none --- how the three-state dynamics, operating on a raw graph, produce the
three-dimensional space that embedded observers perceive.

---

## References

- RAW 112 --- The Single Mechanism: Deposits, Movement, and Expansion as One Process
- RAW 113 --- The Semantic Isomorphism: Same / Different / Unknown
- RAW 111 --- Space Is Connections
- RAW 110 --- Local Dimensionality
- RAW 042 --- Temporal Choice Reconstruction Principle
- RAW 043 --- Void Asymmetry Principle
- RAW 037 --- Observer-Relative Big Bang Principle
- Experiment 64_109 v1-v22 --- Three-Body Dynamics on Graph Substrate (V3 substrate, partial)
- Experiment 51 --- Emergent Time Dilation (V2 substrate: continuous reaction-diffusion field)
- Experiment 53 --- Geodesic Emergence (V2 substrate: continuous reaction-diffusion field)
- Experiment 55 --- Collision Physics and Pauli Exclusion (V2 substrate: lattice)

---

*Date: March 19, 2026*
*Status: DRAFT*
*Depends on: V3_ch001 (The Graph Substrate), RAW 112, RAW 113*
*Opens: Formal comparison operator, photon properties quantitative derivation, depth as proper time,
nuclear forces, partial match / Born rule connection, connector formation rule*
