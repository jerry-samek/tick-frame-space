# Tick-Frame Physics: V3 Theory

**Version:** 3.0
**Date:** March 2026
**Author:** Tom Samek
**Status:** Active development

---

## Foundation

The tick-frame framework rests on two observations that cannot be denied without
self-contradiction:

1. **Existence exists.** Something is here. Any attempt to deny it uses existence to do so.
2. **Process exists.** Something changes. Any attempt to deny it is itself a process.

From these two observations, without additional assumptions, the derivation chain proceeds:

- Existence subject to process → self-recognition → **1=1** (RAW 117)
- Self-recognition requires a vocabulary → **Same / Different / Unknown** (RAW 113)
- Results are append-only → **the graph substrate** (RAW 111, RAW 112)
- The graph generates space (RAW 111), time (RAW 112), mass and gravity (RAW 118),
  light (RAW 109, RAW 081), three spatial dimensions (RAW 108, RAW 040),
  electromagnetism (RAW 086, RAW 087)

The full derivation is in **[RAW 122 — The Derivation Chain](raw/122_the_derivation_chain.md)**.
It is the entry point to the entire framework. The derivation chain is logically
complete — no additional axioms are introduced. The one remaining free parameter
(deposit strength per hop) arises at the implementation level, not in the derivation
itself. Everything below follows from that chain.

---

## What This Theory Claims

The universe is a graph. Nodes connected by edges, nothing else. No manifold, no metric
tensor, no coordinate system, no continuum at any scale.

Every entity in this graph performs exactly one operation at every tick:

> **Deposit on a connector. Hop. Connector extends.**

Connectors are not geometric edges. They are persistent chains of deposits linking nodes,
accumulated over the history of the graph. The graph is append-only: every deposit is
permanent, every extension is permanent, every hop leaves a permanent record. Nothing
that has happened can be undone.

When an entity arrives at a node, its arriving pattern is compared against the existing
deposit state. There are exactly three possible outcomes:

| Outcome       | Condition                                        | Physical mapping |
|---------------|--------------------------------------------------|------------------|
| **Same**      | Arriving pattern matches existing deposits       | Gravity          |
| **Different** | Arriving pattern diverges from existing deposits | Radiation        |
| **Unknown**   | Node has no existing deposits                    | Expansion        |

These three outcomes are not imposed categories. They are the exhaustive logical partition
of all possible comparison results. No fourth state is constructible.

The claim is that this single operation, iterated across all entities at every tick,
produces gravity, inertia, momentum, cosmological expansion, zero-point energy, and
the three-dimensional space observers reconstruct. Geometry is not in the substrate.
Geometry is what observers reconstruct from causal latency matrices. Dimension is an
observer property, not a substrate property. Time is branch depth -- the count of
append operations along a specific path through the graph.

One free parameter remains underived: deposit strength per hop.

---

## Validation Status (March 2026)

This section distinguishes between what experiments have demonstrated and what the theory
claims but has not yet shown. The distinction matters because V3 uses a graph substrate,
while most experiments were conducted on lattice or field substrates from the V2 era.
A result on one substrate does not automatically transfer to another.

### Validated on V3 Graph Substrate

These results were obtained on the graph-based substrate using deposit-chain mechanics:

- **Star formation gradient** from seed deposit (Exp #64_109, v22-v23)
- **Force measurement** and derived orbital velocity from deposit gradients (v22-v23)
- **Curved trajectories** under gravitational force (v22-v23)
- **Radial reversal** and velocity stabilization (v23)
- **Self-pinning:** dense bodies resist expansion drift (v22)
- **Gravitational binding from consumption-transformation** with H=0 — planet
  oscillates around equilibrium instead of collapsing or escaping (Exp #118, v1-v2)

### Validated on V2 Substrates, Plausibly Substrate-Independent

These results were obtained on lattice or field substrates but concern properties of
discrete time or kinematic constraints that do not depend on substrate geometry:

- **rho=2.0 signature** proves time is not a spatial dimension (Exp #50, 1095
  configurations tested across 2D+t, 3D+t, 4D+t -- all show quadratic source scaling
  vs sub-quadratic in pure spatial dimensions)
- **3D optimality** as the stable dimensional configuration (Exp #15, lattice substrate)
- **Two independent gravity implementations converge** on the same qualitative behavior
  (Exp #51 on continuous field + Exp #64_109 on graph substrate)
- **Rotation asymmetry 933x** -- kinematic constraint on discrete tick dynamics (Exp #44)

### Validated in April 2026 (Experiments 118 + 128)

These results come from two experiment lines (April 1-6, 2026, 27 versions total):

- **Gravitational binding from consumption** — planet attracted, confined, oscillates
  radially. Every version of Exp 118 v7+ demonstrates this. (Exp #118, v7-v17)
- **Same/Different consumption rule** — Same deposits consume (reclassify) Different
  deposits. Connectors can shrink. Equilibrium distances from production/consumption
  balance. (Exp #118 v16, Exp #128 v6)
- **Deposit dominance regions as entity measurement** — entities ARE regions where
  their deposits dominate, not objects at graph nodes. Reveals structure invisible
  to node tracking. (Exp #128 v6)
- **Closed orbits from consumption gravity (ODE)** — consumption force F=-consumed/r²
  produces Keplerian orbits with T²∝r³. Up to 1,812 revolutions. (Exp #128 v9-v10)
- **RAW 130: "It rotates because it consumes"** — consumption IS the centripetal force.
  Angular momentum is inherited from formation. Kepler's three laws follow.
- **Star thermal equilibrium** — 80+ nodes fill 73% of graph volume, scale-invariant.
  Not a bug — thermodynamics at this particle count. (Exp #118 v12, v14)
- **Newton I required** — pure reactive entities deadlock (Aristotle's physics).
  Forward continuation as default is necessary. (Exp #118 v10-v11)

### Partially Validated / Open Gaps

- **1/r² force law** — derived in the ODE from geometric dilution (flux=L/4πr²).
  The graph experiments show deposits dilute with distance but the EXACT power law
  from graph dynamics has not been measured. The ODE relabels GM as L×R/4π.
  **Gap: graph → 1/r² force not yet proven.** (RAW 130, Exp #128 v9)
- **Emergent planet formation** — the planet should EMERGE from the star's reject
  stream, not be pre-placed. Pre-placed nodes diffuse before structure forms.
  (Exp #128 v3-v5). **Requires Phase 3 implementation.**

### Not Yet Validated

- **Three-state alphabet** as observable, distinguishable states in simulation
- **Photon as path geometry** rather than intrinsic signal
- **Time dilation from depth accumulation** (quantitative match to GR predictions)
- **The single mechanism itself** -- all simulations to date use float approximations
  of what the theory describes as integer-only deposit operations on a pure graph
- **Graph → 1/r² force law** — the connection between graph deposit dynamics and
  the consumption force law used in the ODE

The gap between the graph dynamics and the ODE remains significant. The consumption
mechanism is validated. The force law derivation from graphs is not. Chapter 7 maps
this gap precisely. RAW 130 provides the theoretical framework.

---

## Reading Paths

The V3 theory is eight chapters. Not all readers need all chapters. Choose your entry
point based on what you care about.

### For physicists

Start with the foundation and its consequences:

1. [RAW 122: The Derivation Chain](raw/122_the_derivation_chain.md) -- the two root
   observations and what follows from them
2. [Chapter 1: The Graph Substrate](V3_ch001_the_graph_substrate.md) -- nodes, edges,
   the single operation, deposit chains
3. [Chapter 2: The Three States](V3_ch002_three_states.md) -- Same/Different/Unknown
   as the complete physical alphabet
4. [Chapter 7: Experimental Status](V3_ch007_experimental_status.md) -- what has been
   measured, on which substrate, with what confidence

Then fill in as needed: Ch3 (emergent geometry), Ch4 (time as branch depth), Ch8 (open
questions and falsification targets).

### For computer scientists

Start with the information structure:

1. [Chapter 5: Information and the Trie](V3_ch005_information_and_trie.md) -- the graph
   read as a prefix tree, shared history as shared branches
2. [Chapter 1: The Graph Substrate](V3_ch001_the_graph_substrate.md) -- the physical
   operations that build the trie
3. [Chapter 2: The Three States](V3_ch002_three_states.md) -- comparison as the only
   computation

Then: Ch3 (how observers reconstruct coordinates from latency matrices), Ch4 (branch
depth as time).

### For philosophers

Start with the axiom derivation and what it implies for observation and identity:

1. [RAW 122: The Derivation Chain](raw/122_the_derivation_chain.md) -- existence exists,
   process exists, and what follows without additional assumptions
2. [Chapter 4: Time and Depth](V3_ch004_time_and_depth.md) -- arrow of time, observer-
   relative Big Bang, dissolution of the simulation argument
3. [Chapter 6: Observer and Consciousness](V3_ch006_observer_and_consciousness.md) --
   identity as trie traversal, memory as branch topology
4. [Chapter 5: Information and the Trie](V3_ch005_information_and_trie.md) -- what
   "information" means in a graph with no external reference frame

Note: Chapter 6 is highly speculative throughout. No predictions from the observer model
have been experimentally validated.

### Quick overview

1. This README -- what the theory claims, what is proven, what is not
2. [Chapter 7: Experimental Status](V3_ch007_experimental_status.md) -- the honest
   accounting of every result
3. [Chapter 8: Open Questions](V3_ch008_open_questions.md) -- where the gaps are

---

## Complete Chapter List

| Chapter                                       | Title                      | Key sources               |
|-----------------------------------------------|----------------------------|---------------------------|
| [Foundation](raw/122_the_derivation_chain.md) | The Derivation Chain       | RAW 122                   |
| [Ch1](V3_ch001_the_graph_substrate.md)        | The Graph Substrate        | RAW 122, RAW 111, RAW 112 |
| [Ch2](V3_ch002_three_states.md)               | The Three States           | RAW 122, RAW 113          |
| [Ch3](V3_ch003_emergent_geometry.md)          | Emergent Geometry          | RAW 108, RAW 109, RAW 110 |
| [Ch4](V3_ch004_time_and_depth.md)             | Time and Depth             | RAW 112, V2 ch001         |
| [Ch5](V3_ch005_information_and_trie.md)       | Information and the Trie   | RAW 113, Ch2              |
| [Ch6](V3_ch006_observer_and_consciousness.md) | Observer and Consciousness | RAW 035, RAW 042, RAW 116 |
| [Ch7](V3_ch007_experimental_status.md)        | Experimental Status        | All experiments           |
| [Ch8](V3_ch008_open_questions.md)             | Open Questions             | All chapters              |

---

## What Changed from V2

Version 2 (January-February 2026) consolidated the first ~76 raw documents into 13
chapters. It was built on a specific set of assumptions:

> **V2 Core Assumption (Superseded):** Time is the primary substrate. Entities are
> temporal processes on a tick-stream. Space is emergent from temporal gradients.
> Geometry is Euclidean at the Planck scale. Connectors are edges on a discrete lattice.

Between February and March 2026, RAW documents 108-113 established a fundamentally
different substrate. The V3 framework replaces V2's geometric lattice with a raw graph
that has no intrinsic geometry at all.

| Concept    | V2 (Geometric Era)                 | V3 (Graph Era)                           |
|------------|------------------------------------|------------------------------------------|
| Substrate  | Discrete Euclidean lattice         | Raw graph, no geometry                   |
| Space      | Emergent from temporal gradients   | Emergent from observer latency matrix    |
| Time       | Primary substrate (tick-stream)    | Branch depth -- observer property        |
| Connectors | Edges on fixed grid                | Deposit chains                           |
| Dimension  | Substrate property (3D Goldilocks) | Observer property (minimal embedding)    |
| Geometry   | Planck-scale voxels                | Observer reconstruction from causal data |
| Gravity    | Time gradient following            | Same -- familiarity routing              |
| Radiation  | Propagating disturbance            | Different -- divergence propagating      |
| Expansion  | Dark energy / field dilution       | Unknown -- frontier writing              |

The shift is not incremental. V2 assumed geometry was physical at the smallest scale
and time was the primary substrate. V3 assumes neither. The graph has no geometry.
Time is branch depth. Space is what observers compute from signal arrival differences.

Many V2 results survive because they tested mechanisms rather than substrates. The
rho=2.0 signature, rotation asymmetry, and O(n) bucketing are properties of discrete
time, not of any particular spatial substrate. Results that depended on lattice geometry
(3D optimality, time dilation correlations, collision physics) need re-validation on
the graph substrate.

### V2 Archive

V2 chapters are preserved in [v2_archive/](v2_archive/). The V2 archive README documents
which results survive the substrate change and which need re-validation. V2 remains
useful as historical reference and because many of its mechanism-level insights carry
forward.

---

## Repository Structure

```
docs/theory/
  V3_README.md              ← You are here
  V3_ch001..V3_ch008.md     ← V3 consolidated chapters
  v2_archive/               ← V2 chapters (13) and supporting documents
  raw/                       ← Original research documents (RAW 000-117+)
  review/                    ← Review notes
  final/                     ← Published versions
```

Experimental code and results are in `experiments/` at the repository root. Key
experiments referenced by V3: #15 (dimensional closure), #44 (kinematic constraints),
#50 (dimensional equivalence rejection), #51 (time dilation), #64_109 (three-body
tree, graph substrate gravity), #118 (consumption-transformation gravity, 17 versions,
CLOSED April 2026), #128 (energy partition / deposit patterns, 10 versions, April 2026).

Key RAW documents from April 2026: RAW 128 (Energy Partition: Store, Move, or Radiate),
RAW 129 (Experimental Connections), RAW 130 (It Rotates Because It Consumes).
