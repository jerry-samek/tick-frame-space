# Chapter 3: Emergent Geometry

---

## Abstract

The graph substrate introduced in Chapters 1 and 2 has no intrinsic geometry. Nodes connect to nodes via
edges. There are no coordinates, no distances, no angles, no metric tensor. Yet observers embedded in the
graph reconstruct a three-dimensional Euclidean space with remarkable consistency. This chapter explains how.

The central tool is the **causal latency matrix** — the table of signal arrival-time differences between
pairs of events. An observer who collects enough events can seek the smallest number of coordinate axes
that reproduces all observed latencies. That number is the observer's **reconstructed dimension**. It is an
observer property, not a substrate property: different observers, with different horizons and different
filtering rules, may reconstruct different dimensionalities from the same underlying graph.

We derive why three dimensions emerge as the natural minimal embedding for observers in our universe,
drawing on three independent lines of argument: the change geometry of the balanced ternary state (RAW 108),
the perpendicularity requirement for orbital persistence (RAW 110), and the configuration independence
observed in dimensional sweep experiments (Experiment 15). We then show that dimensionality is a local
property of each node's neighbourhood, not a global property of the graph, and that this local character
has physical consequences ranging from black hole interiors to the Big Bang.

Finally, we address the relationship between geometry and expansion. Dense bodies — stars, galaxies —
automatically resist the expansion of their local graph through the self-pinning mechanism derived in
RAW 112 and confirmed in Experiment 64\_109 v22. Galaxies do not expand; the space between them does.
This is not assumed. It is derived from the single operation of Chapter 1.

**Honesty note.** The latency matrix reconstruction is a theoretical framework. No experiment has yet
reconstructed geometry from causal latency on the graph substrate. The 3D optimality results (Experiment 15)
were obtained on regular lattices, not random graphs. Self-pinning was observed but with a global placeholder
H, not traversal-driven expansion. These gaps are stated precisely in Section 7.

---

## 3.1 The Causal Latency Matrix

### 3.1.1 Setup

Consider a set of events $E = \{E_1, E_2, \ldots, E_n\}$ detected by an observer embedded in the graph.
Each event has an arrival time $t_i$ — the tick at which the observer registers it. The observer does not
know the graph topology. It does not know how many hops separate any two events. It knows only what it
detects and when.

Define the **causal latency matrix**:

$$L_{ij} = t_j - t_i$$

This is an antisymmetric matrix: $L_{ij} = -L_{ji}$, with $L_{ii} = 0$. It records the temporal separation
between every pair of events as seen by this observer.

### 3.1.2 The Reconstruction Problem

The observer asks: what is the smallest integer $d$ for which there exists an assignment of coordinates
$X_i \in \mathbb{R}^d$ such that

$$L_{ij} = \frac{1}{c} \cdot \|X_j - X_i\|$$

for all pairs, where $c$ is the effective speed of information propagation?

The **dimension of the observer's reconstructed space** is precisely this minimal $d$.

This is a classical multidimensional scaling (MDS) problem. Given a distance matrix, find the lowest-rank
embedding that reproduces it. The mathematics is well understood. What is novel is the ontological claim:
this is not a data analysis technique applied to an already-spatial universe. It is the *definition* of what
space is.

### 3.1.3 Operational Procedure

1. The observer collects events and their arrival times.
2. It builds the latency matrix $L$.
3. It seeks the smallest $d$ for which coordinates $X_i \in \mathbb{R}^d$ can reproduce $L$ within
   measurement tolerance.
4. If three independent latency gradients exist, the observer reconstructs 3D space.
5. If four exist, the observer reconstructs 4D space.

The procedure is finite, mechanical, and requires no prior knowledge of the substrate. The observer does
not need to know it lives on a graph. It does not need to assume Euclidean geometry. It reconstructs
whatever geometry is consistent with its observations.

### 3.1.4 Worked Examples

**1D reconstruction.** Three events with arrival times $t_1 = 0$, $t_2 = 3$, $t_3 = 4$. The distances
$d_{12} = 3$, $d_{13} = 4$, $d_{23} = 1$ are consistent along a line: $x_1 = 0$, $x_2 = 3$, $x_3 = 4$.
Minimal dimension: 1.

**2D reconstruction.** Four events with pairwise distances forming a square. No line can embed them
without distortion. A plane suffices. Minimal dimension: 2.

**3D reconstruction.** Four events with pairwise distances forming a tetrahedron. No plane can embed them.
Three coordinate axes suffice. Minimal dimension: 3.

**4D and beyond.** Five events at equal pairwise distances (a regular 4-simplex) require four axes. Six
such events require five. The pattern continues: $n + 1$ equidistant events require $n$ dimensions. There
is no upper bound in principle.

The key point: dimension is not fixed at 3. It is whatever the observer's latency data requires. That our
universe appears three-dimensional is a fact about the latency structure of its events, not a fact about
the substrate.

---

## 3.2 Dimension as Observer Property

### 3.2.1 The Ontological Claim

In standard physics, dimension is a property of spacetime. The manifold is four-dimensional. All observers
agree. The dimension is observer-independent.

In the graph substrate, dimension is a property of the observer's reconstruction. The substrate has no
dimension. It is a graph. Dimension appears when an observer processes its detected events through the
latency matrix procedure. Different observers, collecting different events from different locations with
different causal horizons, may reconstruct different dimensions.

This is not relativistic frame-dependence, where all observers agree on the underlying 4D manifold and
disagree only on coordinates. This is deeper: the *number of axes* itself depends on the observer's access
to events.

### 3.2.2 When Observers Agree

In practice, observers embedded in the same region of the graph, with overlapping causal horizons and
similar detection capabilities, will reconstruct the same dimensionality. This is because:

- They detect approximately the same set of events.
- Those events have the same latency structure (it is one graph).
- The minimal embedding dimension for that structure is unique.

Agreement on 3D space is not a substrate property. It is a convergence result: observers with sufficient
overlap in their causal horizons converge on the same reconstruction. This convergence is robust precisely
because the latency structure of the graph is a stable property of the graph, not of any individual
observer.

### 3.2.3 When Observers Disagree

Disagreement arises when observers have access to qualitatively different event sets:

- An observer at a black hole horizon detects events with a latency structure that is locally
  one-dimensional (all gradients point radially inward). It reconstructs $d = 1$.
- An observer at the frontier of the graph, where few connections exist, may detect too few events to
  reconstruct any consistent embedding. Its dimension is undefined or zero.
- An observer in a cosmic void, where the graph is sparse, may reconstruct $d = 3$ but with higher
  residual error than an observer in a dense region with rich connectivity.

These are not exotic edge cases. They are the physical content of the framework. The number "3" is not
a law of the substrate. It is the outcome of a reconstruction procedure applied by observers in a
particular regime — the regime of mature, well-connected graph regions with sufficient deposit history
to support three independent latency gradients.

### 3.2.4 Dimension as Rank

There is a precise mathematical characterisation. Form the $n \times n$ matrix of squared distances from
the latency matrix:

$$D_{ij}^2 = (cL_{ij})^2$$

Apply double centring to obtain the Gram matrix $G$:

$$G_{ij} = -\frac{1}{2}\left(D_{ij}^2 - \frac{1}{n}\sum_k D_{ik}^2 - \frac{1}{n}\sum_k D_{kj}^2 + \frac{1}{n^2}\sum_{k,l} D_{kl}^2\right)$$

The rank of $G$ is the embedding dimension. If $G$ has exactly three nonzero eigenvalues, the observer
reconstructs 3D. If it has two, the observer reconstructs 2D. The dimension is the rank of the Gram matrix
of the latency data. No more, no less.

This connects dimension to information content. Three nonzero eigenvalues means three independent directions
of variation in the latency data. Three independent causal gradients. Three axes along which events spread
in a way that cannot be collapsed.

---

## 3.3 Why Three Dimensions

The framework must explain why observers in our universe consistently reconstruct $d = 3$ rather than 2, 4,
or some other number. There are three independent arguments, each arriving at the same conclusion from a
different starting point.

### 3.3.1 Argument from Trit Change Geometry (RAW 108)

The fundamental state unit of the substrate is the balanced ternary trit, taking values $\{+1, 0, -1\}$.
At each tick, exactly one of three components is active. A transition between ticks involves one component
deactivating and a different component activating. This gives three independent binary change channels:

$$\Delta C_{+} = |C_{+}(t+1) - C_{+}(t)| \in \{0, 1\}$$
$$\Delta C_{0} = |C_{0}(t+1) - C_{0}(t)| \in \{0, 1\}$$
$$\Delta C_{-} = |C_{-}(t+1) - C_{-}(t)| \in \{0, 1\}$$

For any nontrivial transition, exactly two flags are 1 and one is 0. These three channels are independent,
exhaustive, and minimal: no channel can be removed without losing transition information.

To faithfully represent the change history of a trit, an embedding space requires one axis per independent
change channel. Two axes cause aliasing — distinct transitions map to the same point. Four axes are
redundant — no fourth channel of information exists.

**Conclusion.** The minimal embedding dimension for the change space of a balanced ternary state is 3. If
the substrate's fundamental state is ternary, observers reconstructing its change history will need exactly
three spatial axes.

Each nontrivial transition occurs in one of three planes, determined by which change channel is unchanged:

| Unchanged channel | Active channels | Transition plane |
|-------------------|-----------------|------------------|
| $C_{+}$ | $C_0$, $C_{-}$ | The $(0, -1)$ plane |
| $C_0$ | $C_{+}$, $C_{-}$ | The $(+1, -1)$ plane |
| $C_{-}$ | $C_{+}$, $C_0$ | The $(+1, 0)$ plane |

Over multiple ticks, the process rotates between these three planes. A sequence of transitions traces a
path through 3D by switching which plane is active at each step. Space is not a container in which
transitions occur. Space is the lossless plot of the transition history.

### 3.3.2 Argument from Dimensional Sweep Experiments (Experiment 15)

Experiment 15 (Chapter 2, Dimensional Framework) performed a systematic sweep across spatial dimensions
$d = 1$ through $d = 5$, measuring structural stability, configuration dependence, and scaling behaviour.
The results:

| Dimension | CV (coefficient of variation) | SPBI (stability) | Configuration dependence |
|-----------|-------------------------------|-------------------|--------------------------|
| 1D | Degenerate — collapse | N/A | N/A |
| 2D | 22.7% | Low | High — fragile |
| **3D** | **5.3%** | **2.23 (maximum)** | **None — universal** |
| 4D | 3.8% | Moderate | None — over-stabilised |
| 5D | 2.1% | Low | None — trivially stable |

Three dimensions emerged as the Goldilocks zone: the first dimension with configuration independence, the
peak of the stability index, and low enough variance to be dynamically rich without being chaotic. Below
3D, dynamics are fragile and sensitive to initial conditions. Above 3D, dynamics are trivially stable —
over-constrained by excess degrees of freedom.

The physical interpretation: 3D is the minimal dimension in which the latency structure of events is
rich enough to support persistent structures (orbits, bound states, complex dynamics) yet constrained
enough to be non-trivial. Lower dimensions collapse causal richness. Higher dimensions dissolve constraint.

**Important caveat.** Experiment 15 was performed on regular lattices, not on random graphs. The
configuration independence result is a statement about lattice-based simulations. Whether it transfers to
the graph substrate is an open question that requires repeating the experiment on deposit-grown graphs.

### 3.3.3 Argument from Orbital Persistence (RAW 110, Experiments 64 and 65)

Experiment 65 removed geometry entirely. Three entities were placed on a random Watts-Strogatz graph — no
coordinates, no distances, no metric. The only primitives: nodes, edges, a gamma field, and the rule
deposit-spread-follow.

**Result.** Gravity worked. The entities attracted. Deposits spread through the graph, creating gradients.
Entities followed gradients toward each other. Mutual attraction emerged from topology alone.

Then everything collapsed to distance zero. No orbits. No energy exchange. No persistence. All three
entities fell into the same node and stopped.

On the $256^3$ cubic lattice (Experiment 64), the same rule produced chaotic three-body dynamics: close
encounters, energy exchange, bound orbits, 20,000 ticks of sustained interaction.

The difference: the lattice has perpendicular directions. The random graph does not.

**Why orbits need perpendicularity.** An orbit is the balance of two competing tendencies: radial
attraction (the gradient pulls the entity toward the source) and tangential momentum (the entity's tendency
to keep moving perpendicular to the gradient). If there is no perpendicular direction, the second tendency
cannot exist. The entity can only fall in or stay put. There is no orbit.

On the cubic lattice, an entity at position $(10, 5, 0)$ attracted toward $(0, 0, 0)$ has a neighbour at
$(9, 5, 0)$ — closer to the source — but also at $(10, 6, 0)$ — same distance, different direction. That
second neighbour is the perpendicular escape route. It enables conversion of radial infall into tangential
motion. That conversion is angular momentum. Angular momentum requires perpendicular directions.

For stable three-body dynamics, three independent perpendicular directions are needed. Two produce planar
orbits that are fragile. One produces radial collapse only. Three produce the full chaotic dynamics observed
in Experiment 64.

**Conclusion.** Three dimensions are necessary for the persistence of complex structure on the graph. Fewer
than three perpendicular directions at each node means everything collapses. Observers embedded in
collapsing regions would not persist long enough to reconstruct anything. Only regions with three or more
independent directions support structures that endure — and therefore support observers who reconstruct
space.

**Important caveat.** Experiment 65 used a Watts-Strogatz random graph ($\beta = 0.95$), not a
deposit-grown graph. The result demonstrates that random graphs lack the local structure needed for orbits,
but does not directly test whether the deposit-growth process produces sufficient local structure.

### 3.3.4 Convergence of the Three Arguments

The three arguments are logically independent:

1. **RAW 108 (algebra)**: The trit has three change channels. Three axes are needed to represent them.
2. **Experiment 15 (empirical)**: Three dimensions are the stability optimum in lattice simulations.
3. **RAW 110 / Experiment 65 (dynamics)**: Fewer than three perpendicular directions destroys persistence.

They arrive at the same number from different directions:

- The algebra says three is *necessary* (for lossless representation).
- The simulation says three is *optimal* (for dynamical stability).
- The dynamics says three is *required* (for structural persistence).

This convergence is the strongest evidence the framework has for the inevitability of 3D. It is not a
single fragile derivation. It is three independent constraints that happen to agree.

---

## 3.4 Configuration Independence

### 3.4.1 The Result

Experiment 15 tested multiple spatial configurations within each dimension — different lattice geometries,
different initial entity placements, different seed patterns. The key finding:

- In 2D, results varied significantly with configuration (CV = 22.7%).
- In 3D, results were independent of configuration (CV = 5.3%).
- In 4D and 5D, results were also configuration-independent but dynamically trivial.

**Configuration independence** means that the reconstructed physics does not depend on the specific
arrangement of entities. It depends only on the dimension.

### 3.4.2 Interpretation

Configuration independence is important because it is a necessary condition for the claim that geometry is
a read operation rather than a physical structure. If the physics depended sensitively on the specific
geometric configuration, then geometry would be doing real physical work — it would be a causal ingredient,
not merely a reconstruction.

Configuration independence says: as long as the dimension is correct, the specific coordinates do not
matter. This is consistent with the claim that coordinates are observer-assigned labels, not substrate
properties. The substrate supplies the latency structure. The observer assigns coordinates. The physics
depends on the structure, not the labels.

Below three dimensions, configuration independence breaks down. The physics *does* depend on the specific
arrangement. This means 2D and lower are regimes where the reconstruction procedure fails to fully capture
the causal structure — there is not enough room in the embedding to absorb geometric variation. In 3D, the
embedding has exactly enough room. In 4D and above, it has too much — the excess freedom absorbs all
variation, producing trivial stability.

### 3.4.3 The Scaling Signature

Experiment 15 also measured the universal scaling exponent $\rho$ — the power-law relationship between
source density and field saturation:

- 3D: $\rho \approx 1.503$ (sub-quadratic, physically rich)
- 4D: $\rho \approx 1.5$ (similar, but dynamics over-stabilised)
- (3D + time): $\rho \approx 2.0$ (quadratic — qualitatively different)

The $\rho = 2.0$ signature for (3D + time) systems, versus $\rho \approx 1.5$ for pure 3D, was the
decisive evidence from Experiment 50 that time is not a spatial dimension. Time produces quadratic source
scaling because it has accumulative properties that spatial dimensions lack. This validated the categorical
distinction between time (the ordering of transitions) and space (the content of transitions) derived in
RAW 108 Section 6.

---

## 3.5 Local Dimensionality

### 3.5.1 The Key Insight

Experiments 64 and 65 revealed that dimensionality is not a global property of the graph. It is a local
property of each node's neighbourhood.

A graph can have nodes with different local dimensionalities. Some regions could be locally 3D (rich
perpendicular structure), others locally 1D (chain-like connectivity), others locally 2D (planar
connectivity). The physics at each node depends on its local dimensionality, not on the global structure
of the graph.

### 3.5.2 Formal Definition

The **local dimensionality** $D(n)$ of node $n$ is the number of independent directions in its
neighbourhood. Formally, it is the rank of the matrix whose columns are the gradient-orthogonal components
of vectors to each neighbour.

For a given gradient direction (say, toward another entity), a neighbour $M$ of node $N$ contributes a
perpendicular direction if the gradient component along $N \to M$ is approximately zero — that is, $M$ is
at roughly the same distance from the source as $N$, but reachable via a different path.

The rank of the set of all such perpendicular directions is $D(n) - 1$ (the gradient itself accounts for
one direction). For full 3D dynamics, $D(n) = 3$: one radial direction plus two independent perpendicular
directions.

On specific topologies:

| Topology | $D(n)$ | Character |
|----------|--------|-----------|
| Cubic lattice ($256^3$) | 3 everywhere | Uniform 3D |
| FCC lattice | 3 everywhere | 12 equidistant neighbours spanning 3D |
| Random Watts-Strogatz ($\beta = 0.95$) | $\approx 0$--$1$ | No consistent perpendicular structure |
| Mixed-structure graph | Varies by node | Heterogeneous dimensionality |

### 3.5.3 Physics Depends on Local Dimensionality

| $D(n)$ | Dynamical behaviour | Physical analogue |
|--------|---------------------|-------------------|
| 0 | No movement possible | Frozen / trapped |
| 1 | Radial collapse only | Black hole interior (1D infall) |
| 2 | Planar orbits, fragile | 2D universe (unstable per Experiment 15) |
| 3 | Full 3D orbits, stable | Our observable universe |
| 4+ | Over-stabilised, diffuse | No physical analogue observed |

This table reproduces Experiment 15's dimensional sweep results, but now as a prediction about graph
topology rather than an observation about lattice choice.

### 3.5.4 Black Holes as Dimensional Collapse

Near a black hole, the graph connections compress toward the centre (in the observer's reconstruction).
Local dimensionality decreases as perpendicular escape routes vanish:

- **Far from the centre:** $D(n) = 3$. Full orbits. Normal physics.
- **Approaching the horizon:** $D(n)$ drops below 3. Perpendicular structure weakens. Orbits become
  unstable.
- **Inside the horizon:** $D(n) \to 1$. Only the radial direction remains. No tangential motion.
  Infall is the only option.
- **At the singularity (if one exists):** $D(n) = 0$. No movement possible. Frozen.

This reproduces the classical result — nothing escapes a black hole — but derives it from graph topology
rather than metric curvature. The entity cannot orbit because the local graph has lost its perpendicular
structure. Not because spacetime curves; because the neighbourhood has no sideways.

### 3.5.5 The Big Bang as Dimensional Growth

At the earliest ticks, the graph has few nodes and few connections. Local dimensionality is low — perhaps
$D(n) = 0$ or 1 everywhere. Nothing can orbit. Everything collapses (or rather, nothing persists).

As the graph grows through the deposit process — entities depositing onto connectors, connectors extending,
new nodes forming — local dimensionality increases. At some critical moment, enough connections exist that
$D(n)$ reaches 3 somewhere. The first stable orbit forms. The first persistent structure appears.

**The emergence of three spatial dimensions is not instantaneous. It is a phase transition in the graph's
local dimensionality.**

Before the transition: only radial collapse. After: persistent structure, complex dynamics, observers.
This is a more fundamental version of the Big Bang — not an explosion in space, but the moment space
became three-dimensional enough to support persistence.

### 3.5.6 Dimensional Variability Across the Universe

If local dimensionality varies across the graph, the universe is a patchwork of dimensional phases:

| Region | Deposit density | Dimensional phase |
|--------|----------------|-------------------|
| Frontier (leaf nodes) | Minimal | Bootstrapping: $D < 3$ |
| Cosmic voids | Low | Early 3D, sparse dynamics |
| Galaxy filaments | Moderate | Mature 3D, rich dynamics |
| Galaxy centres | High | Late 3D, approaching saturation |
| Black hole interiors | Maximum | $D \to 1 \to 0$ |

All connected by the same graph. All governed by the same single operation. Different regions, different
local dimensionalities, different physics.

This variability has a speculative but testable consequence: regions with $D(n)$ slightly below 3 would
exhibit modified gravitational dynamics — excess infall compared to the 3D Newtonian prediction. An
observer modelling such a region under the assumption of uniform 3D would need to add invisible mass to
explain the excess. This is structurally identical to the dark matter problem. Whether the correspondence
is quantitatively correct is an open question requiring formal modelling (see Section 7).

---

## 3.6 Geometry Is Not Physical — It Is a Read Operation

### 3.6.1 The Core Claim

Geometry — the assignment of coordinates, distances, angles, and curvature — is not a property of the
substrate. It is an operation performed by observers on their detected events. The substrate has only
topology: which nodes connect to which. Geometry is what the topology looks like when projected onto a
coordinate system via the latency matrix procedure.

This is not merely a philosophical reframing. It has physical consequences.

### 3.6.2 The Drain Problem as Evidence

Experiment 64 ran three-body dynamics on a $256^3$ cubic lattice. The Bremsstrahlung drain — energy lost
to the field during close encounters — required three iterations to stabilise:

1. **Hard clamp at $v = 1.0$**: Unphysical wall. Energy not conserved.
2. **Point deposit of drained energy**: Gradient spike at source. Kick to $135c$. Exponential runaway.
   NaN.
3. **Uniform distribution of drained energy**: Stable, but required a tunable drain coefficient and
   inflated background gamma.

The root cause: on a lattice with continuous coordinates, two entities can occupy the same cell (distance =
0). The gradient at distance zero is infinite. Any energy deposited at a point creates a singularity.

Experiment 65 ran the same physics on a graph. The minimum distance between any two entities is one hop.
There is no zero distance. There is no singularity. There is no gradient spike. The topology
self-regulates without an explicit drain coefficient.

The drain problem was not a physics problem. It was a **coordinate singularity** — an artefact of the
geometric embedding, not of the underlying graph. Remove the embedding, remove the problem.

This parallels general relativity's treatment of the Schwarzschild singularity at $r = 2M$: it is a
coordinate artefact, resolved by choosing better coordinates. The graph substrate takes this further: there
are no coordinates to choose badly. The singularity never arises.

### 3.6.3 What "Read Operation" Means Precisely

When we say geometry is a read operation, we mean:

1. **The graph exists.** Nodes, edges, deposit values. This is the substrate reality.
2. **An observer detects events.** It registers arrival times.
3. **The observer computes.** It builds a latency matrix, finds the minimal embedding, assigns
   coordinates.
4. **The observer reports geometry.** "These events are separated by distance $d$ in three-dimensional
   Euclidean space."

Step 4 is the read operation. It is accurate — the coordinates reproduce the latency data. But it is not
the substrate. The substrate is Step 1. Steps 2-4 are the observer's reconstruction, performed every time
the observer processes new data.

Geometry is like a spreadsheet chart of raw data. The chart is an accurate representation. You can read
trends from it. You can make predictions. But the chart is not the data. If you extrapolate the chart
beyond its data range — as happens when you push coordinates to $r = 0$ — you get artefacts (singularities)
that do not exist in the data.

### 3.6.4 Curvature as Latency Gradient Variation

In general relativity, gravity is curvature of spacetime. In the graph substrate, what does curvature
correspond to?

It corresponds to spatial variation in the latency gradient. Near a dense body, the deposit field creates
asymmetric latencies: signals arriving from the direction of the body are delayed differently than signals
arriving from other directions. When the observer reconstructs coordinates from these asymmetric latencies,
the resulting geometry is curved — not because the graph is curved (graphs have no curvature), but because
the latency structure is non-uniform.

Curvature is the observer's geometric encoding of deposit-density gradients in the graph. The graph has
no curvature. The reconstruction has curvature because the data it encodes is non-uniform.

---

## 3.7 Self-Pinning: Dense Bodies Resist Expansion

### 3.7.1 The Problem

Chapter 1 established that expansion is the cumulative extension of connectors from all hops ever taken.
Every entity that moves deposits on the connector it traverses. Every deposit extends the connector
slightly. Across the entire graph, connectors grow. Space expands.

But galaxies do not expand. The Milky Way is not getting bigger. The distance between the Earth and the
Sun is not increasing. Expansion occurs between galaxy clusters, in the voids. Dense structures are
stable.

Standard cosmology handles this by asserting that gravitationally bound systems are exempt from expansion.
But it does not derive this exemption from first principles. It is assumed.

In the graph substrate, the exemption is derived.

### 3.7.2 The Mechanism

The connector growth rule in the current simulation suppresses expansion near high deposit density:

$$\text{growth} = \frac{H}{1 + \alpha \cdot (\gamma_A + \gamma_B)}$$

where $\gamma_A$ and $\gamma_B$ are the deposit densities at the two endpoint nodes of the connector, $H$
is the baseline expansion rate, and $\alpha$ is a coupling constant.

A body that deposits continuously — a star, for example — maintains high local $\gamma$. High local
$\gamma$ means the denominator is large. Large denominator means growth $\approx 0$. The local graph
barely extends.

**The body pins its own local graph. It opts out of expansion automatically.**

### 3.7.3 The Physical Consequence

This produces the correct cosmological behaviour:

- **Dense bodies** — stars, planets, galaxies — deposit continuously. Local $\gamma$ stays high. Local
  connectors barely extend. Their neighbourhood stays geometrically stable. Rulers made of the same
  matter do not change length. From inside, nothing moves.

- **Empty voids** — no deposits, $\gamma \approx 0$, denominator $\approx 1$, connectors extend at
  full rate $H$. Voids expand freely.

- **Net result**: expansion happens predominantly in empty regions. Dense regions self-regulate against
  expansion through their own field density. No explicit mechanism distinguishes expanding voids from
  stable galaxies. The distinction emerges from deposit density alone.

This is the observed Hubble flow: galaxies do not expand, the space between them does. Derived from the
single operation. Not assumed.

### 3.7.4 Experimental Confirmation (v22 Phase 0)

Experiment 64\_109 v22 Phase 0 ran a star formation diagnostic: a single seed deposit accumulating gamma
over 50,000 ticks with $H = 0.00001$. The star's gamma field was measured at multiple radii to track the
pinning frontier — the radius out to which the star successfully suppresses expansion.

The diagnostic tracked the ratio $g(r_2) / g(r_1)$ between two radii. When this ratio stabilises (changes
less than 0.005 per 1000 ticks), the star has pinned the graph out to $r_2$:

```
tick  5k:  g10/g5 = 0.321, delta = +0.016/1k
tick 10k:  g10/g5 = 0.379, delta = +0.010/1k
tick 15k:  g10/g5 = 0.425, delta = +0.009/1k
tick 20k:  g10/g5 = 0.463, delta = +0.007/1k
converging toward 0.500 (1/r equilibrium)
```

The star needed approximately 25,000-30,000 ticks to pin its field to $r = 10$. This is not a numerical
artefact. It is the time required for the deposit pattern to extend its pinning radius to orbital
distances. The star must form before the planet can orbit — a prediction that emerged from the single
mechanism rather than being imposed.

### 3.7.5 The Pinning Frontier

Self-pinning is not instantaneous. It propagates outward from the centre of a dense body as deposits
accumulate. At early ticks, only the immediate neighbourhood ($r < 2$--$3$) is pinned. Over time, the
pinning frontier extends to larger radii.

This has a physical consequence: the sequence of structure formation matters. A star must build its gamma
field and extend its pinning frontier to orbital distances *before* a planet can maintain a stable orbit at
those distances. Placing a planet next to a newly formed star produces immediate escape or infall — there
is no gravitational field yet to sustain an orbit. This was confirmed in v21, where a planet placed at
$r = 8$ next to a star with zero warm-up time fell immediately to $r = 0.8$.

The correct physical sequence, as implemented in v22: seed deposit forms, star accumulates gamma over
thousands of ticks, pinning frontier extends, proto-disk forms at radii where the field has stabilised,
planet coalesces from disk material inheriting the local field velocity. This sequence is derived, not
assumed.

### 3.7.6 Limitations of the Current Implementation

The current simulation uses a global constant $H$ applied to all connectors every tick. This is a
placeholder. The correct mechanism — connectors extend only when traversed by an entity — has not yet been
implemented. Under the correct mechanism:

- Connectors between dense bodies, which are frequently traversed, would extend but be counteracted by
  the high local deposit density (self-pinning applies).
- Connectors in empty voids, which are rarely traversed, would barely extend at all — the opposite of
  the current placeholder, which applies $H$ uniformly.

The self-pinning result demonstrates that the simulation already approximates the correct behaviour despite
the placeholder. Dense regions resist $H$ through field density. Sparse regions feel the full $H$ rate.
But the approximation is not exact. Replacing $H$ with traversal-driven expansion is the path to
eliminating the final global constant from the simulation.

---

## 3.8 Time Is Not a Spatial Dimension

### 3.8.1 The Experimental Result

Experiment 50 tested whether treating time as a fourth spatial dimension produces equivalent physics. The
test compared pure spatial dimensions $(3D, 4D, 5D)$ against spacetime configurations $(2D + t, 3D + t,
4D + t)$ across 1,095 configurations.

**All (n + t) systems diverged from $(n+1)D$ baseline behaviour.**

The decisive signature: the scaling exponent $\rho$.

| Configuration | $\rho$ |
|---------------|--------|
| Pure 3D | $\approx 1.5$ (sub-quadratic) |
| Pure 4D | $\approx 1.5$ (sub-quadratic) |
| 3D + time | $\approx 2.0$ (quadratic) |
| 2D + time | $\approx 2.0$ (quadratic) |

All systems with a temporal dimension showed $\rho = 2.0$. All pure spatial systems showed $\rho \approx
1.5$. The qualitative difference is categorical, not marginal.

### 3.8.2 Interpretation

Time has accumulative properties that spatial dimensions lack. In the change-geometry framework of
RAW 108, this distinction is derived: the three spatial axes correspond to the three change channels of
the trit (what changed). Time is the ordering of transitions (when it changed). These are categorically
different:

- **Space**: The content of each transition — which channels changed.
- **Time**: The sequential ordering — which transition came first.

Promoting time to a spatial axis is a category error. The ordering principle cannot become another channel
of content. The $\rho = 2.0$ signature is the experimental manifestation of this categorical difference.

### 3.8.3 3+1 as the Unique Decomposition

The combination of RAW 108 (three change channels require three axes) and Experiment 50 (time is not a
spatial axis) yields a unique decomposition: 3 spatial dimensions + 1 temporal ordering. Not 4 spatial.
Not 2 + 1. Not 4 + 1. Exactly 3 + 1.

This is a strong prediction. It asserts that no physical process in our universe requires a fourth spatial
dimension for its description. Apparent 4D phenomena (if any) would be artefacts of an incomplete 3D
description, not evidence of extra dimensions.

---

## 3.9 Evidence Summary

### 3.9.1 What Has Been Demonstrated

| Claim | Evidence | Substrate | Status |
|-------|----------|-----------|--------|
| 3D is the stability optimum | Experiment 15 (dimensional sweep) | Regular lattices | Validated on lattices |
| Time $\neq$ spatial dimension | Experiment 50 ($\rho = 2.0$ vs $\rho \approx 1.5$) | Regular lattices | Validated on lattices |
| Gravity emerges from topology alone | Experiment 65 (random graph attraction) | Watts-Strogatz graph | Validated |
| Orbits require perpendicularity | Experiment 65 vs 64 comparison | Graph vs lattice | Validated |
| Self-pinning suppresses local expansion | v22 Phase 0 (star formation diagnostic) | Random geometric graph | Confirmed at approximate level |
| Trit change geometry $\to$ 3D | RAW 108 algebraic derivation | N/A (theoretical) | Derived, not experimentally tested |
| Latency matrix $\to$ observer dimension | RAW 040 framework | N/A (theoretical) | Framework only |

### 3.9.2 What Has Not Been Demonstrated

- No experiment has reconstructed geometry from causal latency on the graph substrate. The latency matrix
  procedure is a theoretical framework without experimental instantiation.
- The 3D optimality result (Experiment 15) used regular lattices with pre-assigned geometry, not random or
  deposit-grown graphs. Whether the result transfers to the graph substrate is untested.
- Self-pinning was observed with a global placeholder $H$, not with the correct traversal-driven expansion
  mechanism.
- Local dimensionality was tested on Watts-Strogatz graphs versus cubic lattices, not on deposit-grown
  graphs. The critical question — whether the deposit-growth process naturally produces $D(n) = 3$ — has
  not been answered.
- The dark matter interpretation (dimensional deficit) is speculative. No quantitative comparison with
  observed dark matter distributions has been performed.
- Configuration independence was established on lattices. Whether it holds on arbitrary graph topologies
  is unknown.

---

## 3.10 Open Questions

### 3.10.1 Latency Reconstruction on Graph Substrate

**The question.** Can the latency matrix procedure actually reconstruct 3D space from signal propagation
on a deposit-grown graph?

**Why it matters.** The entire chapter rests on the claim that geometry is an observer reconstruction from
causal latencies. If the procedure fails on the actual substrate — if the latency structure of a
deposit-grown graph cannot be embedded in 3D without large residual error — the framework loses its
geometric foundation.

**What would constitute an answer.** Run signal propagation on a deposit-grown graph with hundreds of
nodes. Collect arrival times at multiple observer nodes. Apply classical MDS. Measure the residual error
as a function of embedding dimension. If the residual drops sharply at $d = 3$, the reconstruction works.
If it does not, the framework needs revision.

### 3.10.2 Natural Dimensionality of Deposit-Grown Graphs

**The question.** Does the deposit-growth process — entities hopping, depositing, connectors extending —
naturally produce graphs with local dimensionality $D(n) = 3$?

**Why it matters.** RAW 108 derives three dimensions algebraically. Experiment 15 confirms it on lattices.
But neither addresses whether the graph that the substrate *actually builds* has the right local structure.
If deposit-grown graphs naturally produce $D(n) = 3$, then three dimensions are not just derived and
optimal — they are inevitable. If not, the framework must explain why the substrate grows a graph with
a dimensionality that does not match its own algebraic derivation.

**What would constitute an answer.** This is Experiment 66 (planned, not yet implemented): let entities
build the graph through deposits alone, with no pre-existing lattice. Measure local dimensionality at
each node as the graph grows. Track $D(n)$ over time.

### 3.10.3 Configuration Independence on Graphs

**The question.** Does the configuration independence observed on 3D lattices hold on arbitrary graph
topologies with $D(n) = 3$?

**Why it matters.** Configuration independence is the bridge between "the substrate is a graph" and
"observers reconstruct unique 3D physics." If different graph topologies with the same local dimensionality
produce different physics, then geometry is doing physical work — contradicting the claim that it is merely
a read operation.

**What would constitute an answer.** Run identical dynamics on multiple graph topologies — cubic lattice,
FCC lattice, random graph with enforced $D(n) = 3$ — and compare statistical observables (scaling
exponents, stability indices, orbital characteristics).

### 3.10.4 Self-Pinning Without Global H

**The question.** Does self-pinning work correctly when expansion is driven by connector traversal rather
than a global constant?

**Why it matters.** The current implementation uses a placeholder ($H$ applied uniformly). Under
traversal-driven expansion, the expansion profile would be qualitatively different: connectors in empty
voids, rarely traversed, would barely extend. The self-pinning mechanism would still suppress expansion in
dense regions, but the baseline against which it is measured would change. The physical predictions might
shift.

**What would constitute an answer.** Implement traversal-driven expansion in the simulation. Run the v22
Phase 0 star formation diagnostic. Verify that the star still pins its local graph and that empty regions
still expand (they would need at least occasional traversal to drive expansion, which may require
re-examining what "empty" means in the graph model).

### 3.10.5 The Continuous Limit

**The question.** At large scales with many nodes and dense connectivity, does the discrete graph approach
continuous $\mathbb{R}^3$?

**Why it matters.** Observers experience space as continuous. If the graph substrate is correct, there
must be a regime in which the discrete hop-by-hop structure becomes indistinguishable from a smooth
manifold. The transition between discrete trit dynamics and smooth 3D space is currently unexplored.

**What would constitute an answer.** This is likely a theoretical derivation rather than an experiment.
Show that as node density increases and connectivity becomes sufficiently uniform, the latency matrix
procedure converges on a Euclidean embedding with residual error that decreases as $1/\sqrt{N}$ or faster.
If the convergence rate can be computed, it would set the scale at which discreteness becomes apparent —
presumably the Planck scale.

### 3.10.6 Dark Matter as Dimensional Deficit

**The question.** Can regions with $D(n)$ slightly below 3 quantitatively reproduce the observed dark
matter distribution?

**Why it matters.** If dimensional deficit produces gravitational effects that match observed galaxy
rotation curves and cluster dynamics without invisible mass, it would be a strong quantitative prediction
distinguishing this framework from both $\Lambda$CDM and MOND.

**What would constitute an answer.** Derive the gravitational anomaly produced by $D(n) = 2.8$ (for
example) in a region, and compare against the Navarro-Frenk-White profile used to fit dark matter halos.
If the profiles match for a physically motivated value of $D(n)$, the prediction is promising. If no
value of $D(n)$ fits, the hypothesis is falsified.

**Current status.** Speculative. No quantitative work has been done.

---

## 3.11 Summary

Geometry in the graph substrate is not a property of the physical world. It is a property of the
observer's reconstruction of the physical world.

The substrate is a graph: nodes connected by edges (deposit chains). It has no coordinates, no distances,
no angles. Observers embedded in the graph detect events, measure arrival times, build causal latency
matrices, and reconstruct the minimal coordinate system that reproduces their measurements. That
reconstruction is geometry.

Three dimensions emerge as the natural reconstruction for three independent reasons:

1. The balanced ternary state has three change channels, requiring three axes for lossless representation
   (RAW 108).
2. Three dimensions are the stability optimum in dimensional sweep experiments, with configuration
   independence and maximal structural complexity (Experiment 15).
3. Persistent structures (orbits, bound states) require three perpendicular directions at each graph node;
   fewer produces collapse (RAW 110, Experiment 65).

Time is categorically distinct from space — it is the ordering of transitions, not a change channel — as
confirmed by the $\rho = 2.0$ vs $\rho \approx 1.5$ signature in Experiment 50. The unique decomposition
is 3 + 1.

Dimensionality is local: each node has its own $D(n)$ determined by neighbourhood structure. This
produces a dimensional landscape ranging from $D = 0$ (frozen, black hole singularity) to $D = 3$ (our
observable universe) to $D > 3$ (over-stabilised, cosmic voids). The Big Bang is the phase transition
where $D(n)$ first reached 3 somewhere in the graph.

Dense bodies resist expansion automatically through self-pinning: high local deposit density suppresses
connector growth. Galaxies do not expand; the space between them does. This is derived from the single
operation of Chapter 1, not assumed.

The principal gap is experimental: no experiment has yet reconstructed geometry from causal latency on a
deposit-grown graph. The theoretical framework is internally consistent and supported by lattice-based
experiments, but the transfer from lattice to graph substrate remains unvalidated. Closing this gap is the
primary target for future experimental work.

---

## References

- **RAW 040** — Dimension Definition in Tick-Frame Space
- **RAW 040\_01** — Why 3D Emerges as the Natural Equilibrium
- **RAW 108** — Three Spatial Dimensions from Trit Change Geometry
- **RAW 110** — Local Dimensionality: Experimental Confirmation from Graph Dynamics
- **RAW 112** — The Single Mechanism (Section 2.7: Self-Pinning)
- **Experiment 15** — Dimensional Sweep (3,960 configurations, 1D-5D)
- **Experiment 50** — Spacetime vs Pure Dimensions ($\rho = 2.0$ vs $\rho \approx 1.5$)
- **Experiment 64** — Three-Body Gravitational Dynamics on Cubic Lattice ($256^3$)
- **Experiment 65** — Three-Body Gravitational Dynamics on Random Graph (Watts-Strogatz)
- **Experiment 64\_109 v22** — Star Formation and Field Self-Pinning (Phase 0)

---

*Date: March 19, 2026*
*Status: DRAFT*
*Depends on: V3\_ch001 (graph substrate), V3\_ch002 (three states), RAW 040, RAW 108, RAW 110, RAW 112*
*Opens: Experiment 66 (anemone model), latency reconstruction validation, dimensional deficit dark matter*
