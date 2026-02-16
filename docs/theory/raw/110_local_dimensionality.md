# RAW 110 — Local Dimensionality: Experimental Confirmation from Graph Dynamics

### *Why Orbits Require Perpendicularity and What That Means for Space*

**Date**: February 14, 2026
**Status**: Experimental result with theoretical integration
**Depends on**: RAW 108 (Three Dimensions from Trit Change Geometry), RAW 109 (Apparent Isotropy of c), Experiment 64 (Three-Body on Lattice), Experiment 65 (Three-Body on Graph)
**Falsifiable**: Yes — predicts relationship between local graph connectivity and orbital stability

---

## 1. The Experiment That Broke Space

Experiment 65 removed geometry from physics. Three entities were placed on a random graph — no coordinates, no distances, no metric, no spatial embedding. The only primitives: nodes, edges, a gamma field, and the rule deposit-spread-follow.

**Result**: Gravity worked. The entities attracted. Deposits spread through the graph, creating gradients. Entities followed gradients toward each other. Mutual attraction emerged from topology alone, with no concept of space.

Then everything collapsed to distance zero. No orbits. No energy exchange. No persistence. All three entities fell into the same node and stopped.

On the 256³ cubic lattice (Experiment 64), the same deposit-spread-follow rule produced chaotic three-body dynamics: close encounters, energy exchange, bound orbits, 20,000 ticks of sustained interaction.

The difference: the lattice has perpendicular directions. The random graph does not.

---

## 2. What the Graph Was Missing

### 2.1 Radial Gradient Only

On a random Watts-Strogatz graph with high rewiring (β = 0.95), the neighborhood of any node is unstructured. When entity A follows the gradient toward entity B, every neighbor of A's current node is either closer to B (lower hop count) or farther from B (higher hop count). There is no neighbor that is **equidistant to B but in a different direction**.

This is the definition of a locally one-dimensional topology. Every gradient is radial. There is no "sideways."

### 2.2 Why Orbits Need Sideways

An orbit is the balance of two competing tendencies:

1. **Radial attraction**: gradient pulls entity toward the source
2. **Tangential momentum**: entity's tendency to keep moving perpendicular to the gradient

If there is no perpendicular direction, tendency (2) cannot exist. The entity has only two options: fall in or stay put. There is no third option. No sideways. No orbit.

On the cubic lattice, entity at position (10, 5, 0) being attracted toward (0, 0, 0) has neighbors at (9, 5, 0) — closer to source — but also at (10, 6, 0) — same distance, different direction. That second neighbor is the perpendicular escape route. It enables the entity to convert radial infall into tangential motion. That conversion is angular momentum. Angular momentum is impossible without perpendicular directions.

### 2.3 The Minimum Requirement

For stable orbits, each node must have at least one neighbor that is approximately equidistant to any given gradient source but reachable via a different path. Formally: for any gradient direction at node N, there must exist a neighbor M such that the gradient component along N→M is approximately zero.

This requires the neighborhood to span at least two independent directions. For three-body dynamics with full chaotic exchange, three independent directions are needed — matching RAW 108's prediction from trit change geometry.

---

## 3. Dimensionality is Local, Not Global

### 3.1 The Key Insight

Experiment 65's failure was not that the graph was "wrong." It was that the graph lacked **local dimensionality** — structured neighborhoods providing perpendicular options at each node.

This reframes dimensionality entirely:

> **Dimensionality is not a property of the universe. It is a property of each node's neighborhood.**

A graph can have nodes with different local dimensionalities. Some regions could be locally 3D (rich perpendicular structure), others locally 1D (chain-like connectivity), others locally 2D (planar connectivity). The physics at each node depends on its local dimensionality.

### 3.2 Formal Definition

The **local dimensionality** D(n) of node n is the number of independent directions in its neighborhood. Formally: the rank of the matrix whose columns are the gradient-orthogonal components of vectors to each neighbor.

On a cubic lattice: D(n) = 3 everywhere (uniform 3D).
On a random graph: D(n) ≈ 0-1 (no consistent perpendicular structure).
On an FCC lattice: D(n) = 3 everywhere (12 equidistant neighbors spanning 3D).
On a graph with mixed structure: D(n) varies by node.

### 3.3 Physics Depends on Local Dimensionality

| D(n) | Behavior | Physical analog |
|------|----------|----------------|
| 0 | No movement possible | Frozen / trapped |
| 1 | Radial collapse only | Black hole interior (1D infall) |
| 2 | Planar orbits, fragile | 2D universe (unstable per Exp #15) |
| 3 | Full 3D orbits, stable | Our universe |
| 4+ | Diffuse, over-stabilized | No physical analog observed |

This table reproduces Experiment #15's dimensional sweep results — but now as a prediction about graph topology rather than an observation about lattice choice.

---

## 4. Connection to RAW 108: The Trit Predicts Three

RAW 108 derived three spatial dimensions from the change structure of a balanced ternary state. Three values → three independent change channels → three orthogonal axes required for lossless representation.

Experiment 65 provides the converse:

- **RAW 108 (theory)**: Three change channels REQUIRE three dimensions. You need all three to represent the physics.
- **Experiment 65 (experiment)**: Fewer than three perpendicular directions DESTROYS orbital dynamics. You need all three for persistence.

Same conclusion, opposite directions. The algebra says three is necessary. The simulation shows fewer than three is fatal.

### 4.1 The Trit-Dimension-Orbit Chain

```
Trit has 3 values
    → 3 independent change channels (RAW 108 §3)
        → 3 perpendicular directions required (RAW 108 §4)
            → Nodes without 3 perpendicular directions collapse (Exp 65)
                → Only graphs with local D(n) ≥ 3 support persistent structure
                    → Universe appears 3D because it must be, for anything to exist
```

This chain is now complete from axiom to experiment. The trit is the input. Three-dimensional space is the output. The graph is the medium. Experiment 65 confirmed the critical link: remove perpendicularity, lose persistence.

### 4.2 Resolution of RAW 108 Open Question §10.2

RAW 108 asked: "Is the 3D lattice the unique topology consistent with trit change geometry?"

**Answer**: No. Any graph with local dimensionality D(n) ≥ 3 at every node is consistent. The cubic lattice is one such graph. The FCC lattice is another. A structured random graph with sufficient local dimensionality would also work. The requirement is not a specific topology but a minimum local connectivity property: **three independent directions at every node.**

The lattice is not special. Perpendicularity is.

---

## 5. Physical Consequences

### 5.1 Black Holes as Dimensional Collapse

Near a black hole, spacetime curvature compresses all directions toward the singularity. In the graph model, this means local dimensionality decreases as the graph connections compress toward the center.

At the event horizon: D(n) begins dropping below 3.
Inside the horizon: D(n) → 1. Only the radial direction remains. No perpendicular escape.
At the singularity: D(n) = 0. No movement possible. Frozen.

This reproduces the classical result — nothing escapes a black hole — but derives it from graph topology rather than metric curvature. The entity cannot orbit because the local graph has lost its perpendicular structure. It can only fall.

### 5.2 Big Bang as Dimensional Growth

At the earliest ticks, the graph has few nodes and few connections. Local dimensionality is low — perhaps D(n) = 0 or 1. Nothing can orbit. Everything collapses (or rather, nothing persists).

As the graph grows (through the anemone process — entities depositing and creating nodes), local dimensionality increases. At some critical moment, enough connections exist that D(n) reaches 3 somewhere. The first stable orbit forms. The first persistent structure appears.

**The emergence of three spatial dimensions is not instantaneous. It is a phase transition in the graph's local dimensionality.**

Before the transition: only collapse. After: persistent structure. This is a more fundamental version of the Big Bang — not an explosion in space, but the moment space became three-dimensional enough to support persistence.

### 5.3 Dark Matter as Dimensional Deficit

If local dimensionality varies across the graph, regions with D(n) slightly below 3 would produce:

- Weaker orbital stability
- Modified gravitational dynamics
- Excess infall compared to Newtonian prediction

An observer modeling this region with a uniform 3D assumption would need to add extra mass to explain the excess infall. That "extra mass" is dark matter — not actual mass, but the gravitational effect of reduced local dimensionality.

**Prediction**: Dark matter concentrations should correlate with regions of anomalous gravitational behavior that cannot be explained by visible mass distribution alone — which is exactly what is observed, reinterpreted as dimensional deficit rather than invisible matter.

*Note: This is speculative. Requires quantitative modeling to compare with observed dark matter distributions.*

### 5.4 Cosmic Voids as High Dimensionality

Conversely, regions of the graph with D(n) slightly above 3 would produce:

- Over-stabilized dynamics
- Weaker effective gravity
- Expansion / dilution

These are cosmic voids — regions where the graph has extra connectivity, making the local space "more than 3D," diffusing gravitational attraction, and preventing structure formation.

*Note: Equally speculative. Testable against void distribution data.*

---

## 6. The Drain Problem — Solved by Topology

### 6.1 The Lattice Drain Problem (Experiment 64)

On the cubic lattice, the Bremsstrahlung drain required three iterations to get right:

1. **Hard clamp at v=1.0**: Unphysical wall, energy not conserved
2. **Point deposit of drained energy**: Gradient spike at source → 135c kick → exponential runaway → NaN
3. **Uniform distribution of drained energy**: Stable, but required tunable coefficient and inflated background gamma

The root cause: on a lattice, two entities can occupy the same cell (distance = 0). The gradient at distance zero is infinite. Any energy deposited at a point creates a singularity.

### 6.2 The Graph Solution (Experiment 65)

On the graph, the minimum distance between any two entities is one hop. There is no zero distance. There is no singularity. There is no gradient spike.

- Entity deposits at its node: neighbors see the deposit at distance 1 hop.
- Maximum possible gradient: the full deposit value over one hop.
- No runaway: gradient is bounded by the deposit strength and the hop distance.
- No tunable drain coefficient: each hop naturally deposits energy into the traversed node.

**Result**: Experiment 65 ran 20,000 ticks with no velocity runaway, no NaN, no overflow, and no explicit drain. The topology self-regulates.

### 6.3 Why This Matters

The drain problem was not a physics problem. It was a **coordinate singularity** — an artifact of embedding the graph into continuous space where distance can be zero. Remove the embedding, remove the singularity.

This is the same insight as general relativity's treatment of the Schwarzschild singularity at r = 2M: it's a coordinate artifact, not a physical one. The physics is the graph. The singularity is the coordinate system. Remove the coordinates, remove the problem.

---

## 7. Performance: 200× Speedup

Experiment 65 ran at approximately 200 ticks per second. Experiment 64 ran at 1 tick per second on the same hardware.

The reason: the cubic lattice has 256³ ≈ 16.7 million cells. The graph has 50,000-100,000 nodes. Two orders of magnitude less computation for the same causal dynamics.

### 7.1 Why Empty Space is Expensive

On the lattice, the spreading kernel must update every cell every tick — including the millions of cells far from any entity, containing near-zero gamma, contributing nothing to the dynamics. The lattice computes empty space.

On the graph, only nodes with nonzero gamma participate in spreading. Only nodes connected to active regions carry signal. The graph computes only where things happen.

### 7.2 The Universe Doesn't Compute Empty Space

If the physical universe runs on a graph rather than a lattice, it is not computing the empty void between galaxies. It computes only where deposits exist — where matter is, where fields carry energy, where causal connections are active. The void is not empty space; it is the absence of graph.

This resolves the "why is the universe computable?" question. A 3D lattice at Planck scale requires ~10^185 cells in the observable universe — obviously uncomputable. A graph with nodes only where things happen requires far fewer — perhaps 10^80 nodes (one per baryon) plus field connections. Large, but finite and proportional to the actual content of the universe.

---

## 8. Predictions

### 8.1 Testable Within the Simulation Framework

1. **Structured graph recovers orbits**: Build a graph where each node has 6 neighbors arranged to span 3 independent directions (e.g., embed a lattice then randomize while preserving local dimensionality). Run three-body. Expect orbits.

2. **Local dimensionality threshold**: Systematically vary the perpendicular structure of the graph. Find the critical D(n) below which orbits fail and above which they succeed. Predict: D(n) = 2 is marginal, D(n) = 3 is robust.

3. **Mixed-dimensionality graph**: Create a graph where one region has D(n) = 3 and another has D(n) = 1. Place entities in both regions. Entities in D=3 should orbit; entities in D=1 should collapse. Same graph, different physics.

4. **Drain comparison**: Run identical three-body scenarios on lattice and graph. Compare peak velocities, energy conservation, and stability. Graph should self-regulate without explicit drain.

### 8.2 Testable in the Physical Universe

5. **Dark matter correlates with dimensional anomalies**: If dark matter is dimensional deficit, its distribution should correlate with gravitational anomalies in ways not fully explained by mass distribution. Compare with MOND-like modifications.

6. **Black hole interior dimensionality**: If the interior is D < 3, infalling matter should show qualitatively different dynamics than D = 3 predictions. Potential signatures in gravitational wave ringdown from mergers.

7. **Void properties**: If cosmic voids have D > 3, their expansion rate should differ from the Hubble flow in a specific, predictable way.

---

## 9. The Anemone Model (Forward Reference)

Experiment 65 used a fixed graph. The natural extension: let entities build the graph through their deposits. Each deposit creates a node. Connections form when deposit chains intersect — like sea anemones waving tentacles that touch and fuse.

In this model:
- Space doesn't pre-exist. It grows from interaction.
- Dimensionality emerges from branching patterns.
- Regions with many interacting entities develop rich connectivity (D ≥ 3) — space forms.
- Regions with no entities have no nodes — space doesn't exist there.

The critical question: does the anemone process naturally produce local dimensionality D = 3? If so, three spatial dimensions are not just derived from the trit (RAW 108) and required for persistence (this document), but INEVITABLE from the growth dynamics of an interacting graph.

This is Experiment 66. Planned, not yet implemented.

---

## 10. Summary

Experiment 65 removed geometry from physics and discovered exactly what breaks:

| Property | Lattice (Exp 64) | Random Graph (Exp 65) |
|----------|------------------|-----------------------|
| Gravity (attraction) | ✓ | ✓ |
| Orbits | ✓ | ✗ |
| Energy exchange | ✓ | ✗ |
| Persistence | ✓ | ✗ |
| Drain stability | Needed tuning | Self-regulating |
| Speed | 1 t/s | 200 t/s |
| Angular momentum | ±5000 (lattice artifact) | N/A (no orbits) |

**Gravity is topological.** It requires only deposit-spread-follow on any connected graph. No geometry needed.

**Orbits are dimensional.** They require perpendicular directions — at least D = 2 for planar orbits, D = 3 for full three-body chaos. Without perpendicularity, attraction exists but everything collapses.

**Dimensionality is local.** It is a property of each node's neighborhood, not a global property of the universe. Different regions of the same graph can have different local dimensionalities, producing different physics.

**The drain problem is geometric, not physical.** Removing the spatial embedding eliminates the zero-distance singularity. The graph self-regulates without explicit drain coefficients.

**Three spatial dimensions are necessary for persistence.** This confirms RAW 108's derivation from the trit and provides the physical mechanism: fewer than three perpendicular directions makes stable orbits impossible.

> **Space is not where things happen. Space is the perpendicularity that prevents things from collapsing.**

---

## References

- **RAW 108**: Three Spatial Dimensions from Trit Change Geometry
- **RAW 109**: The Apparent Isotropy of c on a Discrete Substrate
- **RAW 041**: Ternary XOR Tickstream
- **Experiment 15**: Dimensional Sweep (Ch2 §3, SPBI peak at d=3)
- **Experiment 50**: Spacetime vs Pure Dimensions (ρ=2.0 vs ρ=1.5)
- **Experiment 64**: Three-Body Gravitational Dynamics on Cubic Lattice
- **Experiment 65**: Three-Body Gravitational Dynamics on Pure Graph

---

*Date: 2026-02-14*
*Status: DRAFT*
*Depends on: RAW 108, RAW 109, Experiments 64, 65*
*Validates: Trit → 3D derivation, perpendicularity requirement, topological gravity*
*Opens: Experiment 66 (anemone model), dimensional deficit dark matter hypothesis*
