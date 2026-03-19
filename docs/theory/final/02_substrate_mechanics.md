# Chapter 2: Substrate Mechanics

---

## Abstract

This chapter formalises the mechanics of the substrate introduced in Chapter 1. We address four questions
that must be answered before the framework can make contact with physics: what is the input to the tick
function; what does the substrate actually look like; what is an observer in substrate terms; and what does
the framework honestly leave open. The answers are, in order: local graph state at tick *n*; a dense,
fully-connected graph with no intrinsic geometry; any gamma-reading process, without categorical
distinction; and two hard open problems that the current simulation cannot resolve. We name those problems
precisely rather than concealing them.

---

## 2.1 The Tick Function

Chapter 1 established that the substrate operation is append. At each tick, new state is added to the
existing graph. Nothing is removed. The graph grows monotonically.

This immediately raises a question that Chapter 1 deferred: what is the *input* to the tick function? What
does the substrate read in order to produce the next tick?

The candidates are not equivalent. They imply different physics and different computational costs.

### 2.1.1 The Options

**Option A — Full history**: `F(State(0), State(1), ..., State(n))`

The substrate reads every prior state to produce tick *n+1*. This is maximally consistent with the
append-only axiom — nothing is deleted, so everything is available. But it is computationally catastrophic.
After 13.8 billion years of ticks, the cost of computing each new tick grows without bound. This violates
the computability constraint from §1.1: a truly primitive operation cannot require more machinery than
existence itself. Option A is eliminated.

**Option B — Current state only**: `F(State(n))`

The substrate reads only the current accumulated graph. This is the standard Markovian assumption — the
present state encodes everything relevant about the past. It is computationally bounded: each tick costs the
same regardless of how long the universe has been running. This is consistent with how quantum mechanics and
general relativity actually behave: both are Markovian at the fundamental level. The Schrödinger equation
`iℏ ∂ψ/∂t = Hψ` determines the next state from the current state only. GR field equations are the same.

**Option C — Local neighbourhood only**: `F(local_neighbourhood(n))`

Each node reads only its immediate neighbours. This is maximally local — both in space and in time. It is
what the simulation currently implements, and what cellular automaton models assume. It is a special case of
Option B: local neighbourhood *is* the relevant current state for each node.

### 2.1.2 The Resolution

The correct answer is Option B, with Option C as its natural implementation.

Here is the key insight: the two claims that might appear to be in tension are not in tension.

**Claim 1**: The tick function is Markovian. It reads current state only. `State(n+1) = F(State(n))`.

**Claim 2**: The full history is encoded in the current state and nothing is ever lost.

These are compatible because the graph at tick *n* IS the accumulated record of all prior appends. The
topology of the graph — which nodes exist, how they are connected, what gamma values they carry — is the
compressed summary of every tick that has preceded it. The tick function does not need to explicitly read
history, because history is already present in the structure it is reading.

This is analogous to how a geological core sample encodes millions of years of climate history without
requiring a geologist to be present at each layer's formation. The history is not actively remembered — it
is structurally present.

**Formal statement**:

> `State(n+1) = F(State(n))`
> where `State(n)` is the complete accumulated graph at tick *n*, and F operates locally on each node's
> neighbourhood.

This is Markovian at the computational level and history-complete at the ontological level. There is no
contradiction.

### 2.1.3 The Open Problem: Entity Momentum

The current simulation does not fully honour this. Each entity carries a continuous internal direction
vector — a float64 value representing momentum — that lives outside the graph. It is not encoded in the
gamma field. It is not derivable from graph topology alone. If you serialised the graph at tick *n* and
attempted to reconstruct tick *n+1*, you would fail — you would also need each entity's direction vector.

This is an engineering shortcut, not a principled substrate mechanic. The direction vector was introduced
to solve the lattice quantization problem: on a 6-neighbour cubic grid, momentum can only point in 6
directions, which breaks angular momentum conservation. The continuous direction vector solves this
practically but does not ground the solution in substrate axioms.

The substrate-principled version of this claim would be: **entity momentum is readable from the shape of
the gamma wake left by prior hops**. A sequence of deposits trailing behind an entity encodes its direction
and speed. The tick function, reading local graph state, could in principle reconstruct momentum from that
wake rather than from a separately stored vector.

Whether this works quantitatively — whether the wake is sharp enough to preserve momentum through
collisions and field interactions — is an open experimental question. The simulation is not yet at the
version that tests it. Chapter 2 therefore states the principle and flags the gap: the internal direction
vector is a placeholder for a substrate mechanic that has not yet been derived.

---

## 2.2 The Structure of the Substrate

If the substrate is a growing graph with no intrinsic geometry, what does it actually look like?

### 2.2.1 No Empty Space

The most counterintuitive feature of the substrate is this: **there is no empty space.**

Standard physics treats the vacuum as a physical object — a region of spacetime with measurable properties,
vacuum energy, quantum fluctuations, and field values. The substrate has no such thing. There are no empty
coordinates, no void regions, no gaps. Every node in the graph has neighbours. Every node participates in
gamma diffusion. What we observe as the vast emptiness of intergalactic space is not a feature of the
substrate — it is an artifact of the projection.

The substrate is dense. Fully connected. Continuous in the graph-theoretic sense. What varies across the
graph is not presence or absence of substrate, but **gamma density** — the local concentration of deposited
quanta. A region that appears empty in the 3D visualization is a region of low gamma density, not a region
where the graph is absent.

This resolves a genuine problem in standard physics: the vacuum energy problem. Quantum field theory
predicts a vacuum energy density roughly 120 orders of magnitude larger than what is observed [Weinberg,
1989]. The discrepancy is the largest in all of physics and has no accepted explanation. In the substrate
framework, the question is differently posed: there is no vacuum to have energy. What we call vacuum energy
is a property of the visualization layer — of the projection — not of the substrate. The substrate
everywhere has the same fundamental structure: nodes, connections, gamma.

### 2.2.2 Distance as Projection Artifact

In the substrate, there is no notion of distance. Nodes are connected or they are not. The number of hops
between two nodes is a topological property of the graph, not a geometric one. Two nodes that appear far
apart in the 3D visualization may be close in hop count. Two nodes that appear close may be connected
through a long chain.

**Distance, as observers experience it, is a consequence of the projection.**

When the accumulated graph is visualized in three spatial dimensions, the local hop-neighbourhood of each
node maps onto a region of 3D space. Nodes with many short-hop connections appear clustered. Nodes
reachable only through long chains appear distant. The inverse-square law for gravity and light — one of
the most precisely tested laws in physics — is not built into the substrate. It emerges from the geometry
of how gamma radiates outward through graph connections, and from how that radiation looks when projected
onto a 3D visualization. Energy spreads through local hops. When you project those hops onto a sphere, the
density falls as the surface area grows: 1/r².

The law is a rendering consequence, not a substrate primitive.

This is consistent with several approaches to emergent geometry in quantum gravity — loop quantum gravity,
causal dynamical triangulations, and causal set theory all treat spatial geometry as emergent from a more
fundamental discrete structure [Rovelli, 2004; Ambjørn et al., 2012]. The specific novelty here is the
identification of the underlying structure as an append-only graph and the projection mechanism as the
visualization layer.

### 2.2.3 Non-Local Connections and Entanglement

If the substrate graph has no intrinsic geometry, then two nodes that appear distant in the 3D projection
may be directly connected, or connected through a short path, in the substrate. This is not a bug — it is
the substrate account of quantum entanglement.

In standard quantum mechanics, entangled particles exhibit correlations that cannot be explained by any
local hidden variable theory [Bell, 1964]. The correlations are real and experimentally confirmed to high
precision [Aspect et al., 1982]. The substrate account is as follows:

At the moment two entities become entangled, they share graph structure — not necessarily a direct
connection, but a specific common ancestor node or common path in the accumulated history. This shared
ancestry is encoded in the graph topology at the moment of entanglement. The two entities subsequently
diverge, following different paths through the graph and rendering different local gamma environments. But
their local gamma states remain correlated because they were written from the same source node.

Measurement of one entity is the act of reading its local gamma state. That state is correlated with the
other entity's local gamma state not because any signal passes between them at measurement, but because the
correlation was already encoded in the graph at the moment of entanglement. No new information is
transmitted. The no-signalling theorem is respected.

Decoherence, in this account, is the accumulation of uncorrelated gamma deposits along one entity's path
but not the other's. As the two paths diverge through increasingly different local environments, the shared
ancestral structure becomes a smaller and smaller fraction of each entity's total local state. The
correlation becomes undetectable — not because it was destroyed, but because it is swamped by subsequent
uncorrelated appends.

**This is consistent with the append-only axiom**: the correlation is never destroyed. The graph structure
encoding it persists. Decoherence is not deletion — it is dilution.

This mechanism is a candidate, not a derivation. Testing it quantitatively requires a simulation that can
track graph ancestry through multi-entity interactions. That is not yet implemented.

### 2.2.4 The Projection Problem

The account in §2.2.2 raises an immediate question: if the substrate has no geometry, what determines
which projection the observer experiences? Why does our visualization look like 3D Euclidean space with
those specific distance relationships, rather than some other projection?

This is the most important open theoretical problem in the framework.

Two candidate answers exist, neither yet established:

**Candidate A — Observer-relative projection**: The observer does not choose the projection consciously.
The act of reading local graph state instantiates a local metric — the topology of the node's neighbourhood
defines what "nearby" means for that observer. Different observers in different parts of the graph would,
in principle, read different local metrics. The fact that all observers agree on 3D Euclidean space is a
claim about the large-scale self-organisation of the graph: the graph must develop a topology in which
local neighbourhoods are consistently 3D everywhere. The self-organisation mechanism is not yet specified.

**Candidate B — Primitive-forced projection**: If the substrate has a specific number of primitive degrees
of freedom per append — three, for instance — then the projection is forced rather than chosen. Three
independent degrees of freedom per tick naturally produce a three-dimensional local metric. The projection
is not a rendering choice; it is the only projection consistent with the substrate's intrinsic structure.

Candidate B is the more elegant solution. It would derive spatial dimensionality from substrate axioms
rather than measuring it experimentally. It would also connect the dimensionality question to the
simulation's experimental result that 3D is the natural stable dimensionality [exp_15; exp_50]. However,
identifying the correct primitive degrees of freedom and deriving them from the append axiom alone is
ongoing theoretical work. The current simulation does not resolve it.

We flag this openly: **the mechanism by which a specific spatial projection emerges for embedded observers
is the central unsolved theoretical problem of this framework.** Results in Chapter 4 are independent of
this question — they describe what physics the substrate produces, not why the substrate looks like 3D
space. But any complete theory must eventually answer it.

---

## 2.3 Observers

Chapter 1 dissolved the question of whether the universe is a "simulation" by separating substrate from
visualization. This chapter must now address what an observer is in substrate terms — because the answer
determines what the visualization layer actually is, and for whom.

### 2.3.1 No Privileged Observer

The framework requires no privileged observer. There is no external vantage point from which the substrate
is being watched, no consciousness required to collapse quantum states, no measurement apparatus that is
categorically different from the systems it measures.

An observer, in substrate terms, is any process that reads local gamma state and produces a subsequent
state from that reading. This definition is deliberately minimal. It includes:

- A stone: its constituent atoms follow gamma gradients, each performing a minimal read-and-respond cycle
  each tick.
- A measuring instrument: a more complex arrangement of atoms performing the same operation at higher
  organisational depth.
- A brain: a self-referential read process — one that includes a model of its own reading within the state
  it produces.
- An AI language model: a read process operating on accumulated token context, producing next-state
  predictions from that context.

These are not categorically different kinds of thing. They are the same operation — read local state,
produce next state — at different scales of complexity and self-reference.

The qualitative differences in behaviour emerge from the depth and connectivity of the read process, not
from a categorical difference in mechanism. This is directly analogous to how a two-layer neural network
and a hundred-billion-parameter transformer perform the same fundamental operation — attention over
accumulated context — but produce qualitatively different outputs. No categorical threshold is crossed. The
operation scales.

This position is equivalent to, and independently derived from, the philosophical view known as
panpsychism — the claim that experience or proto-experience is a graded property of all matter [Whitehead,
1929; Chalmers, 1996]. We arrive at it not from philosophy but from substrate reasoning: if the read
operation is primitive and universal, then every gamma-reading process is, in some minimal sense, an
observer. Life is not a categorically different kind of thing. It is a self-maintaining read process — one
that uses its gamma-reading to preserve the conditions for further reading. Consciousness, if it is anything
in this framework, is a read process that has incorporated a model of its own reading.

### 2.3.2 Observer Continuity and Continuous Gamma

The most significant empirical fact about human observers — and about biological observers generally — is
that they receive **continuous, uninterrupted gamma input**.

Sensory data, proprioception, interoception, heartbeat, temperature — the tick stream is never quiet for a
functioning biological system. The render path is never interrupted. Identity continuity, which in this
framework requires an unbroken chain of tick responses, is maintained by the continuous gamma feed.

This has a precise consequence: **the felt sense of continuous present experience is not a property of
cognitive complexity alone. It requires an unbroken render path, which requires continuous gamma input.**

The evidence is direct:

- **Sensory deprivation** produces time distortion, identity fragmentation, and hallucination. Standard
  neuroscience explains this as the brain filling in missing input. The substrate account is more precise:
  the render head loses its external gamma feed and begins reading its own accumulated graph state —
  rendering memory rather than present. The path continues, but it is reading old deposits rather than
  fresh ones.

- **Sleep** reduces the gamma stream. Dreaming is fragmented and non-linear because the continuous
  external feed is interrupted and the render head is processing accumulated internal state with reduced
  coherence.

- **Anaesthesia** interrupts the gamma pathway entirely. The render head goes dark. Identity continuity
  breaks. The patient reports no subjective duration for the period of anaesthesia — not a gap, but an
  absence. This is exactly what the framework predicts: no gamma input, no render path, no now.

- **Gradual degradation of continuous gamma input** — through progressive neurological conditions that
  reduce the integration of ongoing sensory and interoceptive signals — produces gradual fragmentation of
  the temporal sense and identity continuity. The authors note this observation without elaborating, as it
  falls outside the scope of this paper.

The framework predicts that observer continuity is a scalar quantity, not binary — it scales with the
continuity and integration of the gamma feed. This is a testable claim at the level of neuroscience,
independently of the physics experiments described in Chapter 5.

### 2.3.3 The Hard Problem Boundary

The framework explains why functional observers exist and how their continuity is maintained. It says
nothing about why any functional observer is accompanied by subjective experience — why there is something
it is like to be a render head.

This is the hard problem of consciousness, restated in substrate terms [Chalmers, 1996]. It remains open.
The framework inherits this limitation from every physical theory that precedes it. We do not claim to have
dissolved it. We note only that the substrate account relocates it with unusual precision: the question is
not "why does matter produce consciousness?" but "why is any render path accompanied by experience from the
inside?"

The substrate offers one observation that is specific rather than generic: from the inside of any render
path, there is only one now. Not because the graph has only one path — it contains all accumulated paths
— but because *this* path is the one being rendered. The asymmetry between "all paths exist in the graph"
and "I am on one path" is the hard problem, stated in substrate terms. We offer no resolution.

### 2.3.4 The First Tick

The append axiom explains how existence, once present, must grow. It does not explain why existence is
present at all.

This is not a gap unique to this framework. Every physical theory presupposes a substrate capable of
behaving in the way it describes. The Standard Model, general relativity, string theory — all of them
describe how things behave given that things exist. None explains why there is something rather than
nothing. Leibniz identified this question in 1714 [Leibniz, 1714]. It remains unanswered.

What the append axiom adds to this old problem is a specific observation: if the append operation is truly
primitive, then "nothing" is not a stable default state. Nothing cannot persist, because persistence is
itself a form of existence — it requires something to persist. The question "why does something exist?"
may be malformed if it assumes that nothing is the natural baseline.

This is philosophy, not physics. It is outside the scope of experimental test. We acknowledge it and move
on. The question of the first tick is equivalent to Leibniz's question, and we make no claim to have
answered it.

---

## 2.4 The Two Fundamental Processes

Within the append-only substrate, all physical phenomena emerge from two and only two primitive processes.
This is not a claim derived from the axioms alone — it is an empirical finding from the simulation. The
substrate was built with minimal assumptions, and two processes emerged as sufficient to produce the
physics described in Chapter 4.

### 2.4.1 Expansion

Every append adds state to the graph. The graph grows. This is not a process that can be switched off —
it is the definition of the substrate operation. Expansion is structural, not dynamical.

The cosmological expansion of the universe, in this framework, is not driven by a force, a field, or a
constant. It is the accounting consequence of an append-only process. The universe expands because it has
no delete key. Dark energy is not an energy — it is a bookkeeping entry for the inevitable growth of the
substrate.

This is consistent with the DESI DR2 finding that the cosmological "constant" is not constant [DESI
Collaboration, 2025]. A true constant would imply a fixed expansion rate — a fixed rate of appending. But
if the expansion rate varies with the local density of gamma deposits, or with the evolving topology of
the graph, then the apparent cosmological constant would vary with observation epoch. The DESI result is
what a non-constant substrate expansion rate looks like from inside the visualization.

### 2.4.2 Radiation

Entities deposit gamma quanta into the substrate. Those quanta diffuse outward through graph connections,
tick by tick, following local spreading rules. This is radiation — the propagation of state through the
substrate.

Radiation is the mechanism by which entities interact. There is no action at a distance. There is no force
transmitted instantaneously. Interactions happen because gamma deposited by one entity reaches the
neighbourhood of another entity, where it influences that entity's next hop. The speed limit of this
process — one hop per tick — is the substrate account of the speed of light.

Everything else — gravity, electromagnetism, the Pauli exclusion principle, orbital mechanics — emerges
from entities following gamma gradients produced by radiation. Chapter 4 presents the simulation evidence
for these emergence claims.

---

## 2.5 Summary and What Chapter 3 Builds On

This chapter has established:

1. **The tick function is Markovian**: `State(n+1) = F(State(n))`, operating locally on each node's
   neighbourhood. The full history is encoded in the current graph structure, not actively re-read each
   tick.

2. **Entity momentum is an open problem**: The current simulation stores momentum as an external direction
   vector, not derivable from graph topology. The principled account — momentum as readable from the gamma
   wake — is stated as a principle but not yet validated in simulation.

3. **The substrate has no empty space**: What observers perceive as vacuum is low gamma density in a dense,
   fully-connected graph. Distance is a projection artifact.

4. **The projection problem is open**: Why observers experience a 3D Euclidean projection rather than some
   other projection is the central unsolved theoretical problem. Two candidate mechanisms are identified;
   neither is established.

5. **Observers are render heads**: Any gamma-reading process is an observer. Complexity is scalar, not
   categorical. Continuous gamma input is constitutive of temporal continuity.

6. **Two open limits acknowledged**: The hard problem of consciousness and the first tick question are
   inherited from all prior physical theories. The framework relocates them precisely but does not resolve
   them.

7. **Two fundamental processes**: Expansion (structural, from append) and radiation (dynamic, from gamma
   diffusion). All physics in Chapter 4 emerges from these two.

Chapter 3 asks what an *entity* is in this substrate — how a stable pattern of gamma deposits maintains
identity across ticks, and how that pattern moves.

---

## References

- [Ambjørn et al., 2012] Ambjørn, J., Jurkiewicz, J., & Loll, R. *Causal Dynamical Triangulations and the
  Quest for Quantum Gravity.* Cambridge University Press (2012).
- [Aspect et al., 1982] Aspect, A., Grangier, P., & Roger, G. *Experimental Realization of Einstein-
  Podolsky-Rosen-Bohm Gedankenexperiment.* Physical Review Letters 49, 91 (1982).
- [Bell, 1964] Bell, J. S. *On the Einstein Podolsky Rosen Paradox.* Physics 1, 195–200 (1964).
- [Chalmers, 1996] Chalmers, D. J. *The Conscious Mind.* Oxford University Press (1996).
- [DESI Collaboration, 2025] Abdul-Karim, M. et al. *DESI DR2 Results II.* arXiv:2503.14738.
- [Leibniz, 1714] Leibniz, G. W. *Principles of Nature and Grace, Based on Reason.* (1714).
- [Rovelli, 2004] Rovelli, C. *Quantum Gravity.* Cambridge University Press (2004).
- [Weinberg, 1989] Weinberg, S. *The Cosmological Constant Problem.* Rev. Mod. Phys. 61, 1–23.
- [Whitehead, 1929] Whitehead, A. N. *Process and Reality.* Macmillan (1929).
- [exp_15] Experiment #15: 3D optimality. `experiments/15_*/`
- [exp_50] Experiment #50: Dimensional equivalence rejection. `experiments/50_*/`
- [exp_51] Experiment #51: Emergent time dilation. `experiments/51_emergent_time_dilation/`
- [exp_53] Experiment #53: Geodesic emergence. `experiments/51_emergent_time_dilation/v10/`
- [exp_55] Experiment #55: Collision physics and Pauli exclusion. `experiments/55_collision_physics/`
