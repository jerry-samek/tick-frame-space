# Chapter 4: Time and Depth

---

## Abstract

This chapter establishes the framework's account of time. In the graph substrate described in
Chapters 1-3, there is no global clock. The only temporal quantity available to any process is
**branch depth** -- the count of append operations (events that create new structure) along a
specific path through the graph. From this single definition, the arrow of time, gravitational
time dilation, the observer-relative Big Bang, the impossibility of perfect storage, and the
dissolution of the simulation argument all follow without additional postulates.

The central claim is that branch depth is the substrate's native proper time. This claim is
currently qualitative. Whether the ratio of depth accumulation rates between two observers
reproduces the Lorentz factor quantitatively is an open question. What is not open is the
categorical distinction between time and space: Experiment #50 (1,095 configurations, zero
exceptions) measured a universal rho = 2.0 scaling signature in all systems with a temporal
generator, versus rho approximately 1.5 in pure spatial systems. This 33% difference in scaling
exponent is substrate-independent evidence that time is not a spatial dimension. It survives
the V2-to-V3 transition because it depends on the causal structure of append, not on any
particular substrate geometry.

---

## 4.1 Core Claim: Branch Depth Is the Only Clock

### 4.1.1 The Definition

The graph substrate (Chapter 1) grows by append operations. At each node, an arriving pattern
is compared against the existing deposit state. Three outcomes are possible: `same` (match),
`different` (diverge), or `unknown` (no prior state). Of these three, only `different` and
`unknown` create new structure -- a new branch point or a new node, respectively. Each such
structure-creating event increments the branch depth by one along the path where it occurred.

**Branch depth** is therefore the count of structurally novel events along a specific path
through the accumulated graph. It is not a global counter. It is not a coordinate. It is a
property of a particular traversal history.

This is the only clock the substrate provides. There is no external tick counter accessible to
any process embedded in the graph. An observer measures the passage of time by counting how
many `different` or `unknown` events have occurred along its own path since some reference
point. Nothing else is available to count.

### 4.1.2 What Branch Depth Is Not

Branch depth is not the number of ticks elapsed on some global substrate clock. The V2
framework treated time as a global tick-stream -- a strictly ordered sequence of universal
states. The V3 framework abandons this. The substrate may have a tick-stream at the
implementation level (the simulation certainly does), but no observer can access it. What
observers measure is their own depth, which may differ from any other observer's depth at the
same substrate tick.

Branch depth is also not entropy. Entropy is a statistical property of macrostates. Branch
depth is a topological property of a specific path through the graph. The two are related --
deeper paths have explored more of the graph's structure -- but they are not the same quantity.
A path can increase in depth without increasing in entropy (a highly ordered crystalline growth
process creates new structure at every step) and a macrostate can increase in entropy without
any single path increasing significantly in depth (many paths each contributing a small amount
of disorder).

---

## 4.2 The Arrow of Time

### 4.2.1 Append-Only Implies Irreversibility

The append-only axiom (Chapter 1, Section 1.3) states that the substrate can only add state,
never subtract it. Deposits are permanent. Branches, once created, cannot be un-created. Nodes,
once instantiated, cannot be removed.

This directly implies that branch depth can only increase. There is no mechanism by which a
`different` event can be reversed -- that would require deleting the branch it created, which
violates append-only. There is no mechanism by which an `unknown` node, once written, can
return to its prior unwritten state -- that would require removing the node from the graph.

The arrow of time is therefore not a postulate about entropy or initial conditions. It is not
the Second Law of Thermodynamics applied to the early universe. It is not a consequence of a
low-entropy Big Bang state that we happen to be evolving away from [Penrose, 2004]. It is the
definition of the substrate operation itself.

> **The arrow of time is the definition of append. Depth increases because the substrate
> cannot subtract.**

### 4.2.2 Relationship to Thermodynamic Irreversibility

The thermodynamic arrow of time -- the empirical observation that entropy increases in isolated
systems -- is a consequence of the substrate arrow, not the other way around.

In the graph substrate, every entity hop deposits onto connectors. Every deposit extends the
connector chain. These extensions are permanent. The graph at tick *n+1* contains strictly more
structure than at tick *n*. The number of possible microstates consistent with a given
macroscopic configuration increases monotonically because the graph has more nodes and more
connections at every successive tick.

This is the substrate account of the Second Law: the phase space accessible to any macroscopic
description grows because the graph grows. Entropy increases because the substrate only
appends. The thermodynamic arrow is inherited from the substrate arrow.

The reverse is not true. You cannot derive the append-only axiom from the Second Law, because
the Second Law is statistical and admits fluctuations. The append-only axiom is absolute: it
admits no exceptions, no fluctuations, no Poincare recurrences. The substrate arrow is
stronger than the thermodynamic arrow. It implies the thermodynamic arrow but is not implied
by it.

### 4.2.3 Why Time Reversal Symmetry Fails

Standard physics derives many fundamental laws from time-reversal symmetry (T-symmetry). The
equations of classical mechanics, electromagnetism, and quantum mechanics are all symmetric
under time reversal. The asymmetry of observed time is then a puzzle requiring explanation.

In the graph substrate, T-symmetry does not hold at the fundamental level. The substrate
operation is not reversible. You cannot run the deposit-hop-extend cycle backward, because
backward means subtracting deposits and shrinking connectors -- operations the substrate does
not provide.

The T-symmetry of the visualization-layer equations (Newton, Maxwell, Schrodinger) is an
approximate symmetry that holds for the same reason that a movie can be played backward
even though the projector only runs forward. The equations describe relationships between
states at adjacent times. Those relationships happen to be symmetric because they describe
the *structure* of the state transitions, not the *direction* of the underlying process. The
state at tick *n+1* determines the state at tick *n* as uniquely as the reverse (for
Hamiltonian systems). But the substrate only runs one way.

This distinction matters at one specific point: the measurement process in quantum mechanics.
Measurement is irreversible. The graph substrate account is that measurement is an append
event -- the observer's comparison result creates new structure in the graph. This new
structure cannot be removed. The irreversibility of measurement is therefore the same
irreversibility as the arrow of time -- both are instances of append-only.

---

## 4.3 Time Dilation from Depth Accumulation Rates

### 4.3.1 The Mechanism

If branch depth is proper time, then two observers accumulate proper time at different rates
if they accumulate branch depth at different rates. The question is: what determines the
rate at which an observer encounters `different` or `unknown` events?

The answer comes from field self-pinning (RAW 112, Section 2.7; confirmed in Experiment
64_109 v22 Phase 0).

In dense deposit regions -- near massive bodies -- connector growth is suppressed. The
growth rate of a connector between nodes A and B follows:

```
growth = H / (1 + alpha * (gamma_A + gamma_B))
```

where `gamma_A` and `gamma_B` are the local deposit densities. When both are large (dense
region), the denominator dominates and growth approaches zero.

Suppressed connector growth means the local graph structure changes slowly. Connectors
barely extend. New `unknown` nodes are rarely encountered at the frontier (the frontier
is pushed outward by growth, which is suppressed here). `Different` events are also less
frequent because the local deposit pattern is saturated -- most arriving patterns match
existing deposits (`same` fires).

The result: fewer structure-creating events per substrate tick in dense regions. Branch
depth accumulates more slowly. An observer near a massive body ages less, measured in
branch depth, than an observer far from any massive body over the same number of substrate
ticks.

This is gravitational time dilation.

### 4.3.2 Two Observers Diverge

Consider two observers, A and B. Observer A is embedded in a dense deposit region (near a
massive body). Observer B is in a sparse region (deep space).

At observer B's location, connectors grow at near-full rate. The frontier is nearby. `Unknown`
and `different` events are frequent. B's branch depth increases rapidly.

At observer A's location, connectors are pinned. Growth is suppressed. The local graph is
saturated with deposits. `Same` fires at nearly every comparison. A's branch depth increases
slowly.

After some number of substrate ticks, B has accumulated significantly more branch depth than
A. If A and B later reunite (B travels to A's location, or both travel to a common point),
their accumulated depths disagree. B has experienced more time. A has experienced less.

This is the substrate account of the twin paradox. No spacetime metric is required. No
Lorentz transformation is invoked. The asymmetry is physical: A's local graph was denser,
so fewer novel events occurred along A's path.

### 4.3.3 Velocity-Dependent Time Dilation

Gravitational time dilation follows directly from self-pinning. Velocity-dependent time
dilation (special relativistic) requires a separate but compatible argument.

An entity moving through the graph at high velocity traverses many nodes per substrate tick.
At each node, it deposits and reads. The deposits it leaves behind form a wake -- a trail of
gamma through the graph (RAW 112, Section 2.4). This wake increases the local deposit density
along the entity's path. Increased deposit density suppresses connector growth along that
path. Suppressed growth means fewer novel events. Fewer novel events means slower depth
accumulation.

A fast-moving entity ages less than a stationary one because its own deposits suppress the
novelty rate along its path. The faster it moves, the denser its wake, the more it suppresses
its own depth accumulation.

This is qualitatively correct. Whether the suppression follows the Lorentz factor
gamma = 1 / sqrt(1 - v^2/c^2) quantitatively is the central open question of this chapter
(see Section 4.8).

### 4.3.4 The Experimental Status

**Self-pinning itself** has been observed in simulation. Experiment 64_109 v22 Phase 0
(March 2026) confirmed that a star's deposit field suppresses connector growth in its
local neighborhood, producing the correct qualitative behavior: dense bodies resist
expansion, voids expand freely.

**Time dilation from self-pinning** has NOT been measured in simulation. No experiment
has yet measured the branch depth accumulation rate of two observers at different distances
from a massive body and compared the ratio to the GR prediction. This measurement requires
a simulation that tracks per-observer depth, which the current codebase does not implement.

**Velocity-dependent time dilation** was measured in V2-substrate experiments (Experiment 51,
v9) on a continuous reaction-diffusion field substrate, achieving correlation r approximately
0.999 with the GR prediction. This result validates the *mechanism* (gradient-following
produces correct time dilation ratios) but does not validate the V3 substrate (graph with
deposit chains). The mechanism may transfer. It has not been tested on the graph substrate.

---

## 4.4 The Big Bang as Depth Zero

### 4.4.1 Observer-Relative Origin

RAW 037 establishes the observer-relative Big Bang principle:

> **The Big Bang is the earliest tick for which observer O has a coherent internal state.**

If observer O connects to the substrate at some substrate tick T_0, then T_0 is the origin
of O's universe. All prior ticks are undefined from O's perspective -- not because they did
not occur, but because O has no causal access to them. O's internal state contains no record
of substrate history before T_0.

In the V3 framework, this translates directly: **depth zero is the first tick at which the
observer's path through the graph begins.** The observer's Big Bang is its own depth zero --
the root of its personal branch in the trie.

### 4.4.2 No Global Depth Counter

The substrate has no global depth counter. Depth is always measured from a specific starting
node along a specific path. Two observers that began at different substrate ticks have
different depth-zero reference points. They measure depth from different roots.

This has a specific consequence: **cosmological time is observer-relative.** When two
observers compare their measurements of the age of the universe, they are comparing depths
measured from different roots. Agreement is not guaranteed by the substrate. It is an empirical
fact about the specific structure of the graph -- specifically, that the graph has a
sufficiently homogeneous topology that most observers who began at comparable substrate ticks
measure comparable depths.

The standard cosmological model assumes a universal time coordinate (cosmic time) defined by
the expansion of the universe. In the graph substrate, this coordinate is an approximation
that works because the large-scale topology of the graph is approximately homogeneous. It is
not a fundamental quantity.

### 4.4.3 What the Substrate Has

The substrate itself has none of the following:

- **No Big Bang.** The substrate does not have a moment of creation accessible to embedded
  observers. There may be a first tick (the first append), but no observer can access it,
  because accessing it would require a causal path from the first node to the observer -- and
  that path is the observer's own history, which began at depth zero, not at the substrate's
  first tick.

- **No geometry.** The substrate is a graph. Geometry is what observers reconstruct from
  causal latency (Chapter 3).

- **No history.** History is what observers reconstruct from the accumulated deposit topology
  along their path. The substrate does not store history as a separate record. History IS the
  topology.

What the substrate has is structure -- accumulated deposits, connector chains, branch points.
This structure encodes everything that has happened, but it does not label it as "history" or
organize it chronologically. Chronological organization is what observers impose when they
read the structure along their own depth-ordered path.

### 4.4.4 Observers Create Their Own Cosmology

Each observer reconstructs a cosmological history from its own path through the graph. This
reconstruction includes:

- An apparent Big Bang (depth zero -- the earliest coherent state)
- An apparent expansion history (the increasing scale factor along the path)
- An apparent cosmic microwave background (the earliest deposit pattern still readable from
  the current position)
- An apparent age of the universe (the total accumulated depth)

Two observers at different locations in the graph, having traversed different paths, may
reconstruct slightly different cosmological histories. The agreement between observers is a
consequence of the large-scale homogeneity of the graph, not a guarantee of the substrate.

This is consistent with the standard cosmological principle (the universe looks the same
from every point on large scales) but grounds it differently: the cosmological principle
holds because the append-only process produces approximately homogeneous large-scale
topology, not because the universe has a preferred reference frame.

---

## 4.5 Why Perfect Storage Is Impossible

### 4.5.1 The Snapshot Problem

An observer's state at any moment is fully described by two things: its current position in
the trie (which node it occupies in the graph) and its accumulated path history (the sequence
of `same`/`different`/`unknown` events since depth zero). A snapshot of the observer is a
record of these two things, written into some physical storage medium.

But the physical storage medium is itself a deposit pattern in the substrate graph. It is
itself subject to the three-state dynamics. After the snapshot is written, the medium continues
to participate in the equilibrium search -- the ongoing process by which the graph evolves
toward (but never reaches) equilibrium.

This means the snapshot drifts. The physical state of the medium at time *t + delta* is not
identical to its state at time *t*, because new deposits have arrived, connectors have
extended, and the local field has evolved. The stored pattern has been modified -- not by
error, not by corruption, but by the substrate doing exactly what it always does: appending
new state onto existing state.

### 4.5.2 The Impossibility Argument

The argument for the impossibility of perfect storage is as follows:

1. All physical storage is a deposit pattern in the substrate graph.
2. The substrate graph evolves at every tick (append-only, ongoing).
3. The deposit pattern at time *t + delta* includes new deposits that were not present at
   time *t*.
4. Therefore the stored pattern at *t + delta* is not identical to the stored pattern at *t*.
5. Therefore no physical storage can preserve a pattern indefinitely without change.

This is not an engineering limitation. It is not about bit rot, cosmic rays, or thermal noise
-- though all of those are substrate-level manifestations of the same principle. It is a
consequence of the append-only axiom itself: the substrate cannot be paused. There is no way
to halt the equilibrium search in a local region while the rest of the graph continues. Every
region of the graph participates in every tick.

> **Perfect storage requires pausing the substrate. The substrate cannot be paused. Therefore
> perfect storage is impossible.**

### 4.5.3 Media Degradation as Substrate Honesty

This reframes media degradation. In standard engineering, degradation is treated as noise --
an unwanted deviation from the intended stored state. In the graph substrate, degradation is
the medium accurately reporting its current state.

The medium was written at time *t*. At that moment, its deposit pattern encoded the intended
information. At time *t + delta*, the deposit pattern has evolved. The medium now reports a
different state -- not because it has failed, but because it has continued to participate in
the substrate's append-only dynamics. The `different` events that constitute degradation are
the substrate doing exactly what the three-state alphabet requires: comparing arriving patterns
against existing deposits and recording the result.

Every storage medium -- magnetic, optical, crystalline, biological -- is subject to this.
The timescale varies (magnetic media degrade faster than crystalline, which degrades faster
than geological strata) but the principle is universal. No medium is exempt because no medium
exists outside the substrate.

### 4.5.4 Redundancy as the Only Defense

If perfect storage of a single copy is impossible, the only defense against information loss
is redundancy: storing multiple copies across independent branches of the graph.

For all copies to degrade simultaneously, all branches must undergo correlated `different`
events at the same time. The probability of this decreases exponentially with the number of
independent copies. Redundancy does not prevent degradation of any individual copy. It ensures
that at least one copy remains close enough to the original to be readable.

This is not a new insight. It is the substrate account of a well-known engineering principle.
What is novel is the grounding: redundancy works because independent graph branches undergo
uncorrelated dynamics. The independence of the branches is a topological property of the
graph, not an engineering assumption.

The universe's own information preservation strategies follow this principle:

- **DNA replication**: multiple copies, error correction via complementary strands
- **The printing press**: hundreds or thousands of copies distributed across independent
  locations
- **Oral tradition**: redundant encoding across multiple human memories, with periodic
  re-synchronization (retelling)
- **RAID arrays**: engineered redundancy across independent physical media
- **The holographic principle**: information encoded redundantly on boundary surfaces

All are instances of the same strategy: distribute the deposit pattern across enough
independent branches that correlated degradation becomes negligible.

---

## 4.6 The Simulation Argument Dissolved

### 4.6.1 The Standard Argument

The simulation argument [Bostrom, 2003] proposes that if civilizations can run detailed
simulations of conscious beings, then we are probably living in such a simulation. The
argument assumes a hierarchy: the simulator has access to ontological primitives unavailable
to the simulated. This privileged access is what makes the distinction between "real" and
"simulated" meaningful.

### 4.6.2 The Shared Axiom

In the graph substrate framework, the only primitive is identity: `1 = 1`. The universe
begins when this identity is disturbed -- when the first `different` event breaks the
symmetry and creates structure. Everything that follows is the three-state comparison
(`same`/`different`/`unknown`) applied iteratively at every node.

A simulator building a simulation of this universe must implement the same three-state
comparison. The simulator cannot offer a richer ontology, because there is no richer
ontology available. Identity is the floor. You cannot go beneath `1 = 1`. You cannot
build a comparison operator more primitive than "does this match?"

Therefore:

1. The simulator's substrate operates via some comparison process (it must, to compute
   anything).
2. That comparison process reduces to `same`/`different`/`unknown` (these are the
   exhaustive logical outcomes of any comparison).
3. The simulator's graph and the simulated graph are isomorphic at the axiomatic level.

The simulated universe is built from the same primitive as the simulator's universe. There
is no richer level available at any point in the hierarchy.

### 4.6.3 The Infinite Regress Dissolved

The standard simulation argument generates an infinite regress: who simulates the simulator?
This regress is considered problematic because each level is assumed to be ontologically
richer than the level below it.

In the graph substrate framework, the regress is trivially resolved: each level runs the
same three operations. The regress is not vicious because each level is the same thing at
different scale. There is no ontological enrichment as you ascend levels. The simulator's
`same` is the same operation as the simulated universe's `same`. The simulator's `append`
is the same operation as the simulated universe's `append`.

The question "are we in a simulation?" becomes: "is this particular graph a subgraph of a
larger graph running the same operations?" The answer might be yes. It does not matter. The
physics is identical. The information capacity is identical. The arrow of time is identical.
The impossibility of perfect storage is identical. Nothing observable changes.

> **Even if we are in a simulation, it shares our starting axiom. The question dissolves.**

### 4.6.4 What Remains of the Question

The dissolution is philosophical, not empirical. It cannot be tested experimentally. No
measurement can distinguish "the base-level universe" from "a simulation running on a base
level universe running the same axioms." The indistinguishability is not a limitation of our
instruments -- it is a consequence of the axiomatic isomorphism.

What remains is a question about scale, not about ontology. A simulation within this
framework would have fewer nodes than its host (it is a subgraph). It would have less
computational capacity. It would have a shorter history. But it would not have a different
kind of physics. The difference between levels is quantitative, not qualitative.

This is a specific, falsifiable claim: if someone proposes a simulation framework in which
the simulated universe has access to ontological primitives different from the simulator's,
the graph substrate framework predicts that such a simulation is impossible. The simulated
universe will always reduce to the same three-state comparison as its host, regardless of
the programmer's intentions.

---

## 4.7 Time Is Categorically Different from Space: The rho = 2.0 Result

### 4.7.1 The Experiment

Experiment #50 (January 2026) tested whether adding time as a dimension produces the same
physics as adding a spatial dimension. The specific question: does (n spatial dimensions +
explicit time) behave like (n+1) spatial dimensions?

The experiment tested 1,095 configurations across three dimensional pairings:

- (2D + t) versus 3D
- (3D + t) versus 4D
- (4D + t) versus 5D

Two implementation variants were tested: time as a physical dimension (included in the wave
equation Laplacian) and time as a storage dimension (causal in physics, explicit in memory).
Parameters were swept across source strength (alpha), damping (gamma), source count,
geometry, and time horizon.

### 4.7.2 The Result

The null hypothesis -- that time behaves like a spatial dimension -- was rejected with 0/6
tests passed across all configurations.

The decisive quantitative evidence is the source scaling exponent rho:

| System type       | Source scaling exponent rho |
|-------------------|----------------------------|
| Pure 3D spatial   | rho = 1.503                |
| Pure 4D spatial   | rho = 1.532                |
| Pure 5D spatial   | rho = 1.571                |
| 2D + time         | rho = 1.999                |
| 3D + time         | rho = 2.002                |
| 4D + time         | rho = 2.001                |

Pure spatial dimensions: rho approximately 1.5 (sub-quadratic). Salience dilutes as sources
increase -- energy spreads across the growing surface area.

All (n+t) systems: rho = 2.0 (quadratic). Salience amplifies as sources increase -- energy
accumulates via the causal ratchet of append-only dynamics.

The 33% difference in scaling exponent is not a small effect. It is a categorical difference
in how energy propagates. Spatial dimensions dilute. The temporal generator amplifies. They
are not the same kind of thing.

### 4.7.3 Configuration Independence

The rho = 2.0 signature was universal across all 1,095 configurations. It was independent of:

- Source strength (alpha: 0.8 to 2.4)
- Damping rate (gamma: 0.1 to 0.3)
- Source count
- Geometry (symmetric vs. clustered)
- Time horizon (200 vs. 500 ticks)
- Implementation variant (physics vs. storage)

Zero exceptions were found. The null hypothesis was rejected with 100% consistency.

### 4.7.4 Why This Survives V2 to V3

The rho = 2.0 result was obtained on the V2 substrate (discrete lattice with diffusion
dynamics). One might ask whether it transfers to the V3 graph substrate.

The answer is yes, because the result depends on the *causal structure* of append, not on
the *geometry* of the substrate. The signature arises from the fact that time is append-only
(each tick adds state that cannot be removed) while spatial dimensions are symmetric
(propagation in +x is equivalent to propagation in -x). This asymmetry between temporal and
spatial generators is present in any substrate that implements append-only dynamics,
regardless of whether the spatial structure is a lattice, a random geometric graph, or
a trie.

The rho = 2.0 result is the mathematical fingerprint of append-only causality. It is
substrate-geometry-independent. It is the strongest piece of evidence in the framework.

### 4.7.5 Connection to Branch Depth

The rho = 2.0 result supports the identification of branch depth as proper time, because
it demonstrates that the temporal generator has fundamentally different scaling behavior from
spatial generators. If time were merely another spatial dimension (as Minkowski spacetime
treats it, modulo the metric sign), the scaling would be the same. It is not. Time
accumulates. Space dilutes. This is precisely what branch depth predicts: depth only
increases (accumulation), while spatial extent can both grow and shrink depending on local
dynamics.

---

## 4.8 Open Questions

### 4.8.1 Quantitative Time Dilation

**The central open question.** Branch depth as proper time is qualitatively correct: dense
regions accumulate depth slowly, sparse regions accumulate depth quickly, and the direction
of the effect matches gravitational time dilation. But the framework has not demonstrated
that the *ratio* of depth accumulation rates between two observers reproduces the Lorentz
factor gamma = 1 / sqrt(1 - v^2/c^2) or the Schwarzschild factor sqrt(1 - r_s/r).

This is a quantitative prediction that must be derived and tested. The derivation requires
specifying the exact functional relationship between local deposit density and depth
accumulation rate, then comparing the resulting ratio to the GR prediction. The test requires
a simulation that tracks per-observer branch depth in a gravitational field. Neither has been
done.

V2-substrate experiments (Experiment 51, v9) achieved r approximately 0.999 correlation with
GR time dilation predictions using a continuous field substrate. This validates the mechanism
(gradient-following with deposit-density-dependent rates) but does not validate the V3
substrate specifically. Whether the graph substrate reproduces the same correlation is
unknown.

**Status: QUALITATIVE ONLY. Quantitative validation needed.**

### 4.8.2 Gravitational Time Dilation from Self-Pinning

Self-pinning has been observed in simulation (v22 Phase 0). Time dilation as a consequence
of self-pinning has not been measured. The prediction is clear: two clocks at different
distances from a self-pinning star should accumulate branch depth at different rates, with
the closer clock accumulating less depth. This prediction is testable with the current
simulation architecture by adding per-entity depth counters. It has not been tested.

**Status: PREDICTED, NOT MEASURED.**

### 4.8.3 Snapshot Drift Rates

The impossibility of perfect storage is a theoretical claim derived from the append-only
axiom. No experiment has measured the actual drift rate of a snapshot in the simulation.
The prediction is that the drift rate should be proportional to the local `different` event
rate in the physical substrate -- faster drift in high-activity regions, slower drift in
low-activity regions. This is a derivable quantity but the derivation has not been performed.

**Status: THEORETICAL CLAIM, NO EXPERIMENTAL MEASUREMENT.**

### 4.8.4 The Simulation Argument

The dissolution of the simulation argument is philosophical, not empirical. It follows from
the axiomatic structure of the framework and cannot be tested. It is a logical consequence,
not a physical prediction. Readers who find the argument compelling may do so; readers who
do not are not contradicted by any experimental evidence.

**Status: PHILOSOPHICAL, NOT EMPIRICAL.**

### 4.8.5 Velocity-Dependent Time Dilation Mechanism

The proposed mechanism for velocity-dependent time dilation (entity's own deposit wake
suppresses its depth accumulation rate) is plausible but has not been formally derived. In
particular, the functional form of the suppression must be shown to produce the Lorentz
factor, not merely a qualitatively similar slowing. This is likely the hardest open problem
in the time dilation program because it requires a detailed model of wake geometry and its
effect on the local `different` event rate.

**Status: PROPOSED MECHANISM, NOT DERIVED.**

### 4.8.6 The rho = 2.0 Derivation from Three-State Alphabet

The rho = 2.0 result was discovered empirically. A derivation from first principles -- from
the three-state alphabet and the append-only axiom -- would be a significant theoretical
advance. The conjecture is that the quadratic scaling arises because the temporal generator
acts as a coherence amplifier: each append locks in the causal effects of the previous
append, producing quadratic growth in the effective signal strength. The spatial generators,
lacking this ratchet mechanism, show the dilution expected from surface-area spreading
(rho approximately 1.5 in 3D). This conjecture has not been formalized.

**Status: EMPIRICALLY ESTABLISHED, NOT DERIVED FROM AXIOMS.**

---

## 4.9 Summary

This chapter has established:

1. **Branch depth is the only clock.** The substrate provides no global time coordinate.
   Observers measure time by counting structure-creating events along their own path.

2. **The arrow of time is structural.** Append-only means depth only increases. No postulate
   about entropy or initial conditions is required.

3. **Time dilation emerges from self-pinning.** Dense deposit regions suppress connector
   growth, reducing the rate of novel events, slowing depth accumulation. This is
   gravitational time dilation from the same mechanism that produces expansion resistance
   (Chapter 3). Velocity-dependent time dilation follows from the entity's own deposit wake.
   Both are qualitative; quantitative validation is the central open question.

4. **The Big Bang is observer-relative.** Each observer's depth zero is its own first
   coherent state. The substrate has no Big Bang, no geometry, no history. Observers
   create all three by reading the graph.

5. **Perfect storage is impossible.** Physical storage media continue participating in
   substrate dynamics after writing. Snapshot drift is not corruption -- it is the substrate
   accurately reporting its current state. Redundancy is the only defense.

6. **The simulation argument dissolves.** If the only primitive is identity plus initial
   disturbance, simulator and simulated share the same axioms. No meaningful ontological
   distinction exists between levels -- only scale differences.

7. **Time is categorically different from space.** The rho = 2.0 result (Experiment #50,
   1,095 configurations, zero exceptions) proves this with a 33% scaling exponent difference.
   This is substrate-independent evidence that survives the V2-to-V3 transition.

Chapter 5 builds on the trie structure that the three-state comparison naturally produces,
establishing the universe as a native information storage system in which the physical
operations and the semantic operations are identical.

---

## References

- [Bostrom, 2003] Bostrom, N. *Are You Living in a Computer Simulation?* Philosophical
  Quarterly 53, 243-255.
- [Penrose, 2004] Penrose, R. *The Road to Reality.* Jonathan Cape.
- [RAW 037] Observer-Relative Big Bang Principle. `docs/theory/raw/037_observerrelative_big_bang_principle.md`
- [RAW 112] The Single Mechanism. `docs/theory/raw/112_00_the_single_mechanism.md`
- [RAW 113] The Semantic Isomorphism: Same / Different / Unknown.
  `docs/theory/raw/113_semantic_isomorphism_same_different_unknown.md`
- [exp_22] Experiment 64_109 v22 Phase 0: Star formation and field self-pinning.
  `experiments/64_109_three_body_tree/v22/`
- [exp_44] Experiment #44: Rotation asymmetry. `experiments/44_*/`
- [exp_50] Experiment #50: Dimensional equivalence rejection.
  `docs/theory/review/050_01_experimental_results_dimensional_equivalence_rejection.md`
- [exp_51] Experiment #51: Emergent time dilation. `experiments/51_emergent_time_dilation/`
