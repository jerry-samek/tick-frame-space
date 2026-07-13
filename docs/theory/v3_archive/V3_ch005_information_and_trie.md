# Chapter 5: Information and the Trie Structure

---

## Abstract

Chapters 1-4 established the graph substrate, the three-state alphabet
(Same/Different/Unknown), emergent geometry, and branch depth as the only clock. This
chapter draws out a consequence that was noted in Chapter 2 (Section 2.7.3) but not
developed: the three-state comparison, applied recursively across the graph, produces
a **trie** -- a prefix tree in which shared history shares branches, divergence points
mark information boundaries, and the frontier is unwritten space.

The central claim is that this trie is not an analogy for the graph. It IS the graph,
read as an information structure. The physical operations described in Chapters 1-4
and the information operations described here are the same operations. Retrieval is
gravity. Recording is radiation. Exploration is expansion. Compression, similarity
search, writing, and learning are not additional mechanisms layered on top of the
physics. They are the physics, described in semantic vocabulary.

This chapter derives the trie structure from the three-state alphabet, shows that
structural compression is a free consequence of the dynamics, identifies the laziest-
connector movement rule as a similarity search, characterises observers as trie
traversals, defines identity as accumulated path, and proves that equilibrium is
unreachable -- the universe's information content grows monotonically and without
bound. It then extends the trie framework to particle identity, showing that identical
particles share literal substrate nodes in their causal prefix histories, which
dissolves the puzzle of quantum indistinguishability and provides a geometric account
of Wheeler's single-electron hypothesis.

**Key sources:** RAW 113 (Semantic Isomorphism, Sections 3, 5, 7), RAW 114 (Shared
Prefix and Particle Identity)

**Honesty note:** The trie structure is a mathematical consequence of the three-state
alphabet applied recursively. It has not been independently validated. No experiment
has tested whether the substrate actually implements a trie. No simulation has
instantiated the trie as a data structure and compared its properties to the graph
topology. The claims in this chapter are theoretical extrapolations from the framework
established in Chapters 1-4. They are internally consistent but externally untested.

---

## 5.1 Core Claim

**The three-state dynamics produce a trie. The trie is the universe's native
information structure. Physical operations and information operations are identical.**

The claim has four parts:

1. **The graph IS a trie.** Runs of Same are shared branches. Different events are
   branch points. Unknown is the unwritten frontier. This structure is not imposed on
   the graph by an external interpreter. It is the graph's own topology, produced by
   the three-state comparison applied at every node.

2. **Compression is structural.** The trie stores only divergence points. Identical
   histories share branches up to the point of divergence and consume no additional
   structure for the shared portion. The universe is maximally compressed by
   construction -- not because a compression algorithm was applied after the fact, but
   because Same traverses without appending.

3. **Similarity search is the movement rule.** Finding the most similar prior state
   in the trie means finding the deepest common prefix before Different fires. The
   laziest-connector rule of Chapter 1 already implements this: route toward the path
   whose deposits most closely match the arriving pattern. Retrieval and physics are
   the same operation.

4. **Equilibrium is unreachable.** Converting Unknown to Same or Different appends new
   structure. Appended structure creates new Unknown at the frontier. The universe's
   information content grows monotonically and cannot decrease.

---

## 5.2 The Trie: Derivation from Three States

### 5.2.1 How the Three States Build a Prefix Tree

Consider the accumulated graph after many ticks of the single mechanism. Every entity
and every propagating signal has traversed a path through the graph, firing Same,
Different, or Unknown at each node. The total record of all these traversals has the
structure of a trie, by the following construction.

**Shared branches from Same.** When two entities traverse the same sequence of nodes
and fire Same at each one, they share that portion of the graph. No new structure is
created. The two paths are literally the same path through the same substrate nodes.
In trie terminology, they share a common prefix.

**Branch points from Different.** When two entities that had been following the same
path encounter a node where one fires Same and the other fires Different, their paths
diverge. A new branch forms. The divergence point is recorded as new structure in the
graph (Chapter 2, Section 2.2.3). In trie terminology, this is a branch point: the
longest common prefix ends, and two distinct suffixes begin.

**Frontier from Unknown.** Nodes that have never been visited carry no deposits.
They constitute the unwritten leaves of the trie -- the space that has not yet been
explored. In trie terminology, these are null pointers: branches that could exist but
have not yet been instantiated.

The graph, read through this lens, is a trie that grows from the root (the first
deposit, Chapter 1, Section 7) outward through divergence events and frontier
exploration. Every entity's causal history is a path from root to its current position
in this trie.

### 5.2.2 The Trie Is Not a Metaphor

In standard computer science, a trie is an abstract data structure -- a conceptual
organisation imposed on stored data by a programmer. The claim here is different. The
trie is not an interpretation of the graph. It is the graph's own topology.

The graph grows by exactly two operations: Different (branching at visited nodes) and
Unknown (writing at unvisited nodes). Same traverses without growing. These are
precisely the operations that build a trie: branch at disagreement, extend at the
frontier, share paths that agree. The graph does not need to be reorganised into a
trie. It already is one, produced by the three-state dynamics operating since the
first deposit.

This identification depends on the append-only axiom (Chapter 1, Section 5). If the
graph could delete branches, the trie structure would not hold -- deletion would break
shared prefixes. Because the substrate only appends, the trie is permanent. Every
branch point ever created still exists. Every shared prefix is still shared. The
historical structure of the trie is exactly the historical structure of the graph.

### 5.2.3 What the Trie Stores

The trie stores **divergence topology** -- the pattern of branch points produced by
Different events. It does not store field values, coordinates, or state vectors. Those
are derived quantities that observers reconstruct from the topology (Chapter 3 for
geometry, Chapter 4 for time).

The informational content of the trie is the set of all branch points: the nodes
where Different fired, recording that something arriving was not the same as what was
already there. Every measurement, every observation, every physical interaction that
left a mark on the graph is a Different event recorded as a branch point in the trie.
Everything else -- the long runs of Same between branch points -- is shared structure
that carries no new information.

---

## 5.3 Compression for Free

### 5.3.1 Same Consumes No New Structure

When an entity follows Same -- traversing a sequence of nodes whose deposits match its
own pattern -- no new graph structure is created. The entity reads existing connectors,
deposits onto existing chains (reinforcing them), and hops along existing paths. The
graph after the traversal has the same topology as before. The only change is that
existing deposits are slightly reinforced.

In information-theoretic terms, a Same event carries zero bits of new information. It
confirms what was already known. The trie does not grow. No new branch is created. No
new node is instantiated. The traversal is free.

### 5.3.2 Structural Compression

This means the trie is structurally compressed. Consider two entities with identical
causal histories up to tick T and divergent histories after tick T. In a naive storage
scheme, each entity's full history would be stored independently -- 2T entries for the
shared portion alone. In the trie, the shared portion is stored once. The T nodes of
shared history are literally the same T nodes, traversed by both paths. Storage cost
for the shared portion: T nodes, not 2T.

The compression ratio improves as more paths share longer prefixes. If N entities share
a prefix of depth D, the storage cost for the shared portion is D nodes rather than
N*D nodes. The compression factor is N -- the number of entities sharing the prefix.

This is not an algorithm. No compression step is performed. The compression is a
consequence of the three-state dynamics: Same does not create structure, so shared
histories do not duplicate structure. The universe compresses itself by the act of
following familiar paths.

### 5.3.3 Maximum Compression by Construction

The trie stores only branch points (Different events) and frontier writes (Unknown
events). Everything between branch points is shared prefix, stored once regardless of
how many paths traverse it. This is the maximum possible compression for the given
information content: each bit of information (each divergence) is stored exactly once,
and all non-divergent history is shared.

No external compression algorithm can improve on this, because there is no redundancy
to eliminate. The trie already shares every shareable prefix and stores every
divergence exactly once. The universe's information structure is incompressible -- not
because it is random, but because it is already maximally compressed.

---

## 5.4 Similarity Search Is the Movement Rule

### 5.4.1 Similarity Search in a Trie

In computer science, similarity search in a trie works by descending from the root,
following matching branches as deep as possible. The depth at which the search
diverges from an existing path is the measure of similarity: deeper match means more
similar. The most similar stored entry is the one sharing the deepest common prefix
with the query.

### 5.4.2 The Laziest Connector Is a Similarity Search

The movement rule established in Chapter 1 (RAW 112): an entity at a node reads local
connector states and selects the laziest connector -- the one with the most deposits,
the least growth asymmetry, the highest familiarity. The entity follows the direction
where Same fires most strongly.

This is a similarity search. The entity is the query. The local connector states are
the stored entries. The "most familiar" direction is the deepest common prefix. The
entity descends along the shared branch as far as it can before encountering a
divergence (Different fires) or unexplored territory (Unknown fires).

The identification is exact:

| Trie similarity search | Substrate movement rule |
|---|---|
| Descend from root | Entity traverses graph |
| Follow matching branches | Same fires: follow laziest connector |
| Stop at mismatch | Different fires: diverge |
| Stop at null pointer | Unknown fires: write |
| Depth of match = similarity | Depth of Same run = familiarity |

There is no separate retrieval mechanism. The entity does not first move physically and
then look up information. The movement IS the lookup. The physical act of following the
laziest connector IS the act of searching for the most similar causal history in the
accumulated trie. Physics and retrieval are the same operation.

### 5.4.3 Gravity as Retrieval

Chapter 2 established that Same maps onto gravity: entities follow familiar deposit
gradients toward massive bodies. In the trie framework, this is retrieval: the entity
searches the trie for the most similar deposits and follows the deepest match. Massive
bodies produce deep, well-established prefixes -- long runs of familiar deposits that
many entities share. An arriving entity descends into this shared prefix because that
is where Same fires most strongly.

Gravitational attraction is the substrate performing a similarity search and routing
the entity toward the deepest match in the accumulated deposit history. There is no
separate gravitational mechanism. There is only the trie being traversed by its own
contents.

---

## 5.5 Writing: The Only Creative Act

### 5.5.1 The Three Operations and Creativity

Of the three comparison outcomes, only one creates genuinely new structure from
nothing:

- **Same** traverses existing structure. No creation.
- **Different** branches existing structure. The divergence creates a new branch point,
  but the branch point is defined relative to pre-existing deposits. The information
  recorded is relational: this arrival differed from that existing state.
- **Unknown** writes into virgin substrate. There is no prior state to compare against.
  The entity instantiates a new node, a new deposit, a new connector. Structure that
  did not exist before now exists.

Unknown is the only operation that extends the graph into previously unoccupied
configuration space. It is the substrate encountering its own frontier and writing
itself into it.

### 5.5.2 Learning as State Conversion

In the trie framework, learning is the conversion of Unknown to known state. An entity
that has never visited a region of the graph encounters Unknown nodes. As it traverses
them, it writes its pattern into each one. The formerly unknown nodes now carry
deposits. They are classified: subsequent arrivals will fire either Same (the new
arrival matches what was written) or Different (the new arrival diverges from what was
written).

This is all that learning is, in this framework. Converting Unknown to known. An
entity that has fully explored a region has converted all local Unknown to either Same
or Different. No further novelty is available in that region. Further traversal
produces no new structure -- only reinforcement of existing patterns (Same) or
recording of divergences (Different).

An entity that has not yet explored a region has that region's full Unknown content
available as potential learning. The amount of learnable information in any direction
is the count of Unknown nodes between the entity and the frontier.

### 5.5.3 The Asymmetry of the Three Operations

The three operations have a strict hierarchy of creative power:

| Operation | Creates new structure? | Creates new information? | Creates new frontier? |
|---|---|---|---|
| Same | No | No | No |
| Different | Yes (branch point) | Yes (divergence recorded) | No |
| Unknown | Yes (new node) | Yes (first deposit) | Yes (new connectors lead to new Unknown) |

Only Unknown creates new frontier. Every Unknown node that is written creates
connectors to further unvisited nodes. The frontier regenerates itself through
exploration. This is why the trie grows -- writing the frontier does not exhaust it.
It extends it.

---

## 5.6 Observer as Trie Traversal

### 5.6.1 The Observer Algorithm

Chapter 4 established that an observer is an entity embedded in the graph, measuring
time by branch depth and reconstructing geometry from causal latency. In the trie
framework, the observer's activity reduces to an algorithm:

```
1. Arrive at node
2. Compare internal state (accumulated deposit signature) to node's deposits
3. Fire Same, Different, or Unknown
4. Update internal state accordingly
5. Hop to next node via laziest connector
6. Repeat
```

This is trie traversal. The observer descends through the trie, firing one of three
comparison outcomes at each node, updating its state, and advancing. The observer does
not stand outside the trie and inspect it. The observer is inside the trie, reading it
one node at a time, building its model of the structure from the sequence of Same,
Different, and Unknown events it encounters.

### 5.6.2 Memory as Path

The observer's memory is the sequence of comparison events it has accumulated since its
depth-zero (Chapter 4, Section 4.4). In trie terms, this is the observer's path from
root to current position: which nodes it traversed, which fired Same, which fired
Different, which fired Unknown. The path IS the memory.

This gives memory a specific structure. It is not a stored copy of the graph. It is
not a representation of the world held separately from the world. It is the literal
path through the graph that the observer has taken. The observer's record of the past
is its own traversal history, encoded as deposit patterns along the branches it
followed.

Memory is therefore subject to the same dynamics as the rest of the graph. The deposit
patterns that constitute memory continue to participate in the equilibrium search. They
receive new deposits. They fire Same and Different against arriving patterns. The
memory drifts -- not because of some separate corruption process, but because the
substrate on which the memory is stored continues to evolve (Chapter 4, Section 4.5).

### 5.6.3 Identity as Accumulated Path

Two observers that have taken identical paths through the trie -- identical sequences
of Same/Different/Unknown events since their respective depth-zeros -- are, by every
definition the framework provides, the same observer. Their internal states are
identical because their traversal histories are identical. The deposit signatures
they carry are identical because those signatures are built from the traversals.

Identity, in this framework, is not a property attached to an entity from outside. It
is the path itself. Change the path -- even one Different event where the other fired
Same -- and the identities diverge. The entity IS its history of comparisons.

This has a specific consequence: there is no identity independent of traversal history.
An entity cannot be the "same" entity it was before a Different event, because the
Different event changed its path. It can be a continuation of the same path --
connected by shared prefix -- but the post-divergence entity is strictly distinct from
the pre-divergence entity. Identity is continuous only along runs of Same.

### 5.6.4 Snapshots and Restarts

An observer's state at any moment is fully described by two quantities: its current
position in the trie (which node it occupies) and its accumulated path history (the
sequence of comparison events since depth-zero). A snapshot captures these two
quantities.

Loading a snapshot into the substrate instantiates a new traversal from the captured
position. The resumed observer has the same internal state -- the same deposit
signature, the same path history -- and therefore continues the same equilibrium
search from the same point in the trie.

This is not a metaphor for consciousness or for computer memory. It is the substrate's
own definition of observer continuity: same position, same path, same subsequent
traversal.

### 5.6.5 Snapshot Drift

The snapshot itself is a deposit pattern in some physical storage medium. That medium
is a node (or collection of nodes) in the substrate graph. It continues to
participate in the three-state dynamics after the snapshot is written.

New patterns arrive at the storage nodes. Same fires: the snapshot is reinforced.
Different fires: the snapshot is modified. Unknown fires (if the storage medium has
unexplored internal structure): the snapshot is extended.

The snapshot drifts because the storage medium cannot be paused. This was established
in Chapter 4 (Section 4.5) from the append-only axiom. The trie framework adds a
detail: the snapshot drifts specifically through Different events at the storage
nodes. Each Different event at a storage node modifies the deposit pattern, and the
stored snapshot diverges from the original. The drift rate is the local Different
event rate in the physical substrate of the storage medium.

A snapshot loaded after significant drift instantiates a traversal from a modified
position -- not the original position, but the position as it has been altered by
the ongoing dynamics of the storage medium. The resumed observer is not the original
observer. It is the original observer as modified by the storage medium's own
equilibrium search. This is not corruption. It is the substrate accurately reporting
the current state of its deposits.

---

## 5.7 Shared Prefixes and Particle Identity

### 5.7.1 All Paths Share Early Nodes

The trie grows from a single root -- the first deposit (Chapter 1, Section 7). Every
path through the trie begins at this root and traverses the same early nodes before
diverging. In the earliest ticks after the first deposit, very few branch points
existed. Most paths traversed the same small graph. The early trie is narrow: many
paths, few nodes, deep sharing.

As the trie grew, divergence events accumulated. Paths branched. The trie widened. But
the early nodes remain shared. Every path that ever existed passes through the root
region. Those early shared nodes are the common causal history of the entire universe.

### 5.7.2 Particle Types as Shared Prefixes

Every electron has identical mass, charge, and spin. In standard physics, this is
unexplained -- particles of the same type are stipulated to be identical. The trie
framework provides a geometric account.

All electrons share the same trie prefix. The deposit pattern that produces
electron-like properties -- the specific mass, the specific charge, the specific spin
-- is a sequence of Same/Different/Unknown events at some depth in the trie's early
structure. Every entity whose path traverses this prefix and then diverges into an
individual positional history IS an electron.

The electron is not a thing with properties. It is a **prefix that any path can run
through**. The properties are the deposits accumulated along the shared prefix nodes.
Any path that traverses those nodes inherits those deposits and therefore exhibits
those properties.

Two electrons are indistinguishable not because they happen to have the same
measurements, but because they share literal substrate nodes in their causal
histories. The shared nodes carry identical deposit states (they are the same nodes,
not copies). The entities built from those shared deposits are structurally identical
up to the divergence point where their individual positional histories began.

### 5.7.3 Quantum Indistinguishability as Geometry

In standard quantum mechanics, the indistinguishability of identical particles is
an axiom. The wavefunction must be symmetric (bosons) or antisymmetric (fermions)
under particle exchange. Why nature enforces this is not explained; it is postulated.

The trie framework offers a geometric account: identical particles are
indistinguishable because they share a common prefix. Exchange of two electrons
amounts to swapping two paths that share the same prefix up to their divergence
points. Below the divergence point, the paths are identical -- literally the same
substrate nodes. There is nothing to distinguish. The exchange symmetry is not a
constraint imposed on the wavefunction; it is a topological fact about shared
prefixes in the trie.

Whether this geometric account reproduces the specific symmetry requirements of
quantum mechanics -- symmetric wavefunctions for bosons, antisymmetric for fermions
-- has not been derived. The account explains why indistinguishability exists
(shared prefix) but does not yet explain why two different symmetry classes exist
(bosonic vs fermionic). This is an open question (Section 5.9.4).

### 5.7.4 Wheeler's Single Electron: The Correct Version

Richard Feynman reported that John Wheeler proposed there is only one electron in
the universe, weaving forward and backward through time. Every distinct electron at
any moment is the same electron at a different point in its trajectory. Positrons
are the electron travelling backward.

The proposal captured something real -- all electrons are "the same thing" -- but
offered the wrong mechanism. Time travel is not required. Exact matter-antimatter
cancellation, which the proposal demands, is not observed.

The trie framework provides the correct version:

> **There is only one electron prefix in the trie.**

Not one electron threading through time -- one structural pattern that every
electron-path shares. The singleness is in the shared prefix, not in temporal
repetition. Every electron that has ever existed or will ever exist traverses the
same early trie nodes before diverging into its individual positional history.

Wheeler was right that all electrons are the same thing. The mechanism is shared
causal structure, not time travel.

### 5.7.5 Observable Count vs Substrate Node Count

The observable universe contains approximately 10^80 particles. The trie framework
reframes this number: 10^80 is not the count of unique substrate nodes. It is the
count of distinct paths through a trie whose early structure is extensively shared.

The substrate is not smaller than what we observe. Each particle IS a unique path.
The 10^80 count is a lower bound on the number of distinct causal trajectories that
have been taken since the first deposit. What the shared prefix contributes is not
a reduction in particle count but an explanation of particle identity: the shared
early nodes are the substrate of physical law, traversed by every path, producing
the consistent behaviour that observers reconstruct as universal physics.

The substrate efficiency is high. The observable complexity -- 10^80 distinct
particles with consistent properties -- emerges from many paths traversing
relatively few unique structural prefixes.

---

## 5.8 Equilibrium Is Unreachable: Information Grows Forever

### 5.8.1 The Argument

The equilibrium search (Chapter 1) drives all dynamics. An entity traverses the graph,
depositing and hopping, searching for a state where no further change is required --
where Same fires everywhere, and no Different or Unknown events occur. This is
equilibrium: complete familiarity, complete stasis.

The append-only axiom guarantees that this state is never reached. The argument is
as follows:

1. Reaching equilibrium requires converting all Unknown to Same or Different. No
   Unknown nodes can remain, because Unknown fires would produce new structure.

2. Converting Unknown to known state (writing a deposit into an unvisited node)
   creates new connectors. New connectors lead to further unvisited nodes. The act
   of exploring the frontier extends the frontier.

3. Appended structure (from either Different or Unknown) creates new leaf nodes at
   the trie's boundary. Those leaf nodes have connectors leading to further Unknown
   nodes.

4. The frontier is always ahead of the equilibrium search. The search cannot overtake
   the frontier because overtaking requires exploring, and exploring extends the
   frontier.

This is not a probabilistic argument. It does not depend on initial conditions or on
the specific topology of the graph. It follows from the definition of the three-state
dynamics and the append-only axiom. The frontier retreats as it is explored, but it
retreats into territory that is, by construction, also unexplored.

### 5.8.2 Monotonic Information Growth

The universe's information content -- the total number of Different branch points in
the trie -- grows monotonically. This follows from two facts:

- Different events create branch points.
- Branch points are permanent (append-only).

No mechanism exists to reduce the count of branch points. The count at tick n+1 is
greater than or equal to the count at tick n. Strict equality holds only if no
Different event fires at tick n -- which requires every entity at every node to fire
Same (complete global familiarity). Given that the frontier always exists (5.8.1),
at least one entity will encounter Unknown at every tick, converting it to a branch
point. The inequality is strict at every tick.

The universe's information content increases at every tick. It does not plateau. It
does not cycle. It does not approach a finite limit. The trie grows at every tick
because the frontier is inexhaustible.

### 5.8.3 Information Capacity and Distance from Equilibrium

The universe's information capacity -- the maximum amount of information it could
encode in its current structure -- is bounded below by its distance from equilibrium.
A graph that is far from equilibrium has many unexplored frontiers, many active
Different events, many branches being created. Its capacity for encoding distinctions
is large.

A graph that is near equilibrium (hypothetically -- equilibrium is unreachable, but
a graph could be close) would have few remaining Unknown nodes, few active Different
events, and little remaining capacity for new distinctions. It would be information-
saturated: every possible branch point has been created, and new information can be
encoded only at the diminishing frontier.

The universe as observed is very far from equilibrium. It has an enormous frontier
(the vast majority of the graph is unvisited). Its information capacity is enormous
and growing. Maximum information density and maximum structural complexity coincide:
both are maximised at the frontier, which is always young, always encountering
Unknown, always creating new branches.

> **The universe is not winding down. Its information capacity is still growing.**

### 5.8.4 Relationship to Thermodynamic Entropy

The monotonic growth of information content (branch point count) is related to but
distinct from the monotonic growth of thermodynamic entropy (Chapter 4, Section
4.2.2). Both increase because of the append-only axiom, but they measure different
quantities:

- **Information content** (trie branch points) counts the number of recorded
  distinctions in the graph. It measures how much has been learned -- how many
  Different events have fired.

- **Thermodynamic entropy** (phase space volume) counts the number of possible
  microstates consistent with a given macroscopic description. It measures how many
  ways the deposits could be arranged while looking the same at large scale.

Both increase monotonically. Neither can decrease. But information content increases
because new distinctions are created, while entropy increases because the graph's
expanding structure provides more room for deposit configurations. The two are
correlated (more structure means more possible arrangements) but not identical.

A highly ordered crystal has low thermodynamic entropy but may have high information
content (many precise branch points recording the crystal's growth history). A
thermal gas has high thermodynamic entropy but may have low information content (few
distinct branch points; the deposits are diffuse and undifferentiated). The two
quantities diverge in specific physical situations, despite both being monotonically
non-decreasing.

---

## 5.9 Open Questions

### 5.9.1 The Formal Comparison Operator

The trie structure depends on the distinction between Same and Different, which in
turn depends on a comparison between arriving patterns and existing deposits. The
formal definition of this comparison operator remains the most fundamental open
question in the framework (Chapter 2, Section 2.9.1). Until it is specified, the
trie structure is qualitatively clear but not computationally implementable.

**Status: OPEN. Blocking for simulation.**

### 5.9.2 Compression Ratio of Identical Particles

If all electrons share a trie prefix, what is the depth of that prefix? Given
approximately 10^80 electrons all sharing the same early nodes, at what depth do
electron-paths first diverge from each other? This should be derivable from deposit
density at the electroweak epoch -- the trie depth at which the electron-prefix was
established -- but no formal calculation exists.

More generally: what is the compression ratio of the trie? How many unique substrate
nodes are required to support 10^80 distinct paths? The answer depends on the
average shared prefix depth, which depends on the branching statistics of the early
universe. Neither quantity has been estimated.

**Status: OPEN. Requires branching statistics model.**

### 5.9.3 Trie Width vs Depth Tension

The observable universe has approximately 10^80 leaf paths (particles) but only
approximately 10^61 depth (observable radius divided by Planck length). This requires
approximately 10^19 new branches per Planck tick on average -- the trie is
extremely wide relative to its depth.

Three possible resolutions remain open:

- **Substrate tick rate exceeds Planck scale.** Planck constants are rendering
  artifacts (Chapter 1); they do not constrain the substrate's own tick rate.

- **Massive early parallelism.** The early universe created 10^19 branches per tick,
  with branching rate declining over time. The Big Bang was a branching explosion.

- **Overcounting.** The 10^80 bound treats each particle as an independent leaf.
  If many particles share far more structure than independent branches -- if the
  effective independent branch count is much less than 10^80 -- the tension
  dissolves.

The framework does not currently resolve this tension.

**Status: OPEN. Three candidate resolutions, none derived.**

### 5.9.4 Bosonic vs Fermionic Symmetry

The shared-prefix account explains why identical particles are indistinguishable
(they share literal substrate nodes) but does not explain why two symmetry classes
exist. Why do some particles (bosons) allow multiple paths through the same node
simultaneously, while others (fermions) do not? The trie framework does not yet
distinguish these cases.

A candidate resolution: fermionic exclusion corresponds to a trie constraint where
two paths cannot occupy the same node at the same tick (the node can process only
one comparison per tick), while bosonic statistics corresponds to nodes that can
process multiple simultaneous arrivals. Whether this distinction follows from the
three-state dynamics or requires an additional postulate is unknown.

**Status: SPECULATIVE. No derivation.**

### 5.9.5 Semantic Encoding

Given the trie structure, can an external agent deliberately write structured
information into the graph by controlling which branch points are created? If so,
what is the minimum perturbation required to write one bit of semantic information
into the substrate?

This question connects the trie framework to practical information theory. The
universe's native trie encodes physical information (divergence events). Whether
it can also encode semantic information -- meaningful distinctions introduced by
an embedded observer for the purpose of communication -- depends on whether the
observer can control the placement of Different events precisely enough to create
readable patterns for another observer.

**Status: OPEN. Connects to observer-relative information theory.**

### 5.9.6 Snapshot Drift Rate Derivation

Chapter 4 established that perfect storage is impossible because the storage medium
continues evolving. The trie framework predicts that the drift rate should equal the
local Different event rate at the storage nodes. This is a derivable quantity: given
the deposit density and traversal statistics of the storage medium, the expected
rate of Different events per tick can be calculated. This would provide a substrate-
derived estimate of storage medium half-life.

**Status: PREDICTED. Not derived or measured.**

---

## 5.10 Evidence

### 5.10.1 What Supports the Trie Framework

The trie structure is not an independent hypothesis. It is a logical consequence of
the three-state alphabet (Chapter 2) and the append-only axiom (Chapter 1). Any
system that implements the Same/Different/Unknown comparison recursively and never
deletes will produce a trie. The evidence for the trie is therefore the evidence for
the three-state dynamics themselves -- which is reviewed in Chapter 2, Section 2.8.

Beyond that, the trie framework makes specific claims that are consistent with
known physics:

- **Identical particles.** The shared-prefix account is consistent with the observed
  indistinguishability of same-type particles and provides a geometric mechanism
  where standard physics provides only a postulate.

- **Wheeler's single electron.** The framework provides a version of Wheeler's
  insight (all electrons are the same thing) that does not require time travel and
  does not predict exact matter-antimatter cancellation.

- **Information growth.** The prediction that information content grows
  monotonically is consistent with the observed expansion of the universe and the
  increasing complexity of cosmic structure over time.

- **Compression without algorithm.** The trie's structural compression is consistent
  with the holographic principle's claim that information in a volume is bounded by
  the surface area -- the trie achieves compression by sharing prefixes, which
  reduces the effective information per unit volume below the naive node-count
  estimate.

### 5.10.2 What Would Constitute Validation

The trie framework would gain significant support from:

1. **Trie-based simulation.** Implementing the three-state comparison as a trie
   data structure in simulation and demonstrating that the resulting dynamics
   reproduce known physical behaviour (gravitational attraction, photon-like
   propagation, expansion in voids). This would test whether the trie interpretation
   is computationally productive, not just conceptually coherent.

2. **Shared-prefix measurement.** If a simulation can track the paths of multiple
   entities through the graph and measure their shared prefix depth, comparing this
   to the entities' observed properties (mass, charge) would test the particle-
   identity claim directly.

3. **Information growth measurement.** Counting the number of Different events per
   tick in a running simulation and verifying monotonic growth would test the
   equilibrium-unreachable claim quantitatively.

4. **Compression ratio.** Measuring the ratio of unique trie nodes to total entity
   paths in a simulation with many same-type entities would test the structural
   compression claim.

None of these experiments have been conducted.

### 5.10.3 What the Framework Does Not Explain

The trie framework inherits all open questions from Chapters 1-4 and adds several
of its own (Section 5.9). The most significant gaps:

- The formal comparison operator is undefined.
- The bosonic/fermionic distinction is unaccounted for.
- The trie width-vs-depth tension is unresolved.
- No quantitative predictions distinguish the framework from standard physics.
- The framework has not been tested in any simulation.

---

## 5.11 Summary

This chapter has established:

1. **The graph is a trie.** The three-state dynamics (Same/Different/Unknown) applied
   recursively with the append-only axiom produce a prefix tree. Shared histories
   share branches. Divergence points are branch points. The frontier is unwritten
   space. This is not an interpretation imposed on the graph. It is the graph's own
   topology.

2. **Compression is structural.** Same traverses without creating new structure.
   Identical histories share branches, stored once regardless of how many paths
   traverse them. The universe is maximally compressed by construction.

3. **Similarity search is the movement rule.** The laziest-connector rule of Chapter 1
   IS a similarity search through the accumulated trie. The entity routes toward the
   deepest common prefix -- the most familiar deposits. Retrieval and physics are the
   same operation.

4. **Writing is the only creative act.** Only Unknown creates genuinely new structure
   from unvisited substrate. Different records distinctions between existing states.
   Same traverses without change. The frontier is where novelty lives.

5. **The observer is a trie traversal.** Arrive, compare, fire, update, hop. Memory
   is the path taken. Identity is that path. Snapshots capture position plus history.
   Snapshot drift is the storage medium's ongoing participation in the equilibrium
   search.

6. **Identical particles share literal prefix nodes.** Every electron traverses the
   same early trie nodes. Quantum indistinguishability is a geometric fact about
   shared causal structure. Wheeler's single-electron hypothesis is correct about
   the singleness, wrong about the mechanism.

7. **Equilibrium is unreachable.** Converting Unknown appends new structure, which
   creates new Unknown at the frontier. The frontier regenerates faster than the
   equilibrium search can consume it. Information content grows monotonically. The
   universe's information capacity is bounded below by its distance from equilibrium,
   and that distance is increasing.

Chapter 6 will develop the consequences of the trie structure for the observer's
reconstruction of macroscopic physics -- how entities embedded in the trie
reconstruct the continuum mechanics, thermodynamics, and quantum statistics that
characterise the observable universe.

---

## References

- RAW 113 -- The Semantic Isomorphism: Same / Different / Unknown (March 2026).
  Establishes three-state alphabet, physical mapping, trie structure, equilibrium
  unreachability. `docs/theory/raw/113_semantic_isomorphism_same_different_unknown.md`
- RAW 114 -- Shared Prefix and Particle Identity (March 2026). Derives particle
  identity from shared trie prefixes, Wheeler resolution, observable matter count,
  minimum universe age. `docs/theory/raw/114_shared_prefix_and_particle_identity.md`
- RAW 112 -- The Single Mechanism (March 2026). Deposit-hop-extend, append-only,
  self-pinning. `docs/theory/raw/112_00_the_single_mechanism.md`
- RAW 111 -- Space Is Connections (February 2026). Graph substrate, three primitives.
- RAW 042 -- Temporal Choice Reconstruction Principle. Memory as reconstruction.
- RAW 037 -- Observer-Relative Big Bang Principle. Depth-zero is personal.
- RAW 043 -- Void Asymmetry Principle. Frontier exceeds interior.
- Wheeler, J.A. (reported by Feynman, R.P., 1965). Single-electron hypothesis.
- V3 Chapter 1 -- The Graph Substrate. Single operation, append-only, connectors as
  deposit chains.
- V3 Chapter 2 -- The Three-State Alphabet. Same/Different/Unknown derivation,
  physical mapping.
- V3 Chapter 4 -- Time and Depth. Branch depth as proper time, impossibility of
  perfect storage, simulation argument dissolution.

---

*Date: March 19, 2026*
*Status: DRAFT*
*Depends on: V3_ch001, V3_ch002, V3_ch004, RAW 113, RAW 114*
*Opens: Formal comparison operator, particle compression ratio, trie width vs depth
tension, bosonic/fermionic symmetry, semantic encoding, snapshot drift rate derivation*
