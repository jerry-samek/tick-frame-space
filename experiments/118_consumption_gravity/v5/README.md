# Experiment 118 v5: Fixed-Graph Deposit Propagation

## Status: DESIGN — waiting for v4 results
## Date: March 31, 2026
## Author: Tom (theory), Claude (spec)

---

## Why v5 Exists

v4 was written and implementation started before a critical theoretical
correction emerged during the same session. v4 conflates two distinct
concepts:

1. **Deposits** (photons, Different events) — signals that TRAVEL on connectors
2. **Connectors** (space, structure) — the fixed graph linking nodes

v4 says "connector length = deposit count" — making every deposit extend
space. This means every photon from the Sun makes the Sun-Earth distance
grow. Everything becomes a light sail. This is physically wrong.

v5 corrects this: **connectors are fixed-length roads. Deposits travel on
them. The road doesn't get longer because cars drove on it.**

### Key correction from v4 → v5

| Concept | v4 (wrong) | v5 (corrected) |
|---------|-----------|----------------|
| Connector length | Grows with every deposit | Fixed at graph construction |
| Deposits | Accumulate statically on connector | Propagate along connector at c = 1 hop/tick |
| "Pressure" | Connector extension pushes planet | Routing away from saturated directions |
| Orbital motion | Spatial curve in 3D embedding | Cycle through graph nodes |
| Velocity | Emergent from hop direction | No velocity vector — pure routing decisions |
| Force | Implicit in density routing | No force — routing IS physics |
| What grows connectors | Deposits (wrong) | Only Unknown events at frontier (not applicable in bounded system) |

---

## Theory Basis

### The core picture (from tonight's discussion)

```
(star) >p>p>p>p>p> (planet)
```

- Star nodes discharge quanta onto connectors (radiation)
- Quanta propagate along connectors at 1 hop per tick (push-driven light,
  RAW 112 — "new deposits displace old ones down connectors like a tube")
- Quanta arrive at nodes, where the node's capacitor evaluates them
- If Same (matches spectrum): capacitor fires, quantum is consumed
  (transformed into entity's own pattern), entity deposits its own quantum
  outward
- If Different (doesn't match): quantum QUEUES at the node. The node's
  capacitor is charging on it, but hasn't fired yet. The quantum sits.

### What queuing means

A deposit arriving at a node whose capacitor is busy **cannot**:
- Pass through (traversing a node IS an interaction — append-only history)
- Reflect (changing direction is a state change — violates preservation)
- Be consumed without transformation (consumption IS transformation)

It **can only** queue. It exists on the connector, at the node boundary,
waiting for the capacitor to process it. This is the ONLY option consistent
with append-only.

### The non-dimensional insight

The graph has no inherent geometry. Connectors are relations, not roads in
space. There is no "star end" and "planet end" where things pile up. There
is no "outward" direction. The 3D embedding is visualization convenience.

When we say "the planet moves outward," what actually happens: the planet
node's capacitor is saturated from the star-facing connector. It routes to
a different connector — one with manageable deposit density. In the graph,
this is just choosing a different neighbor. In the visualization, this
neighbor happens to be further from the star cluster in the embedding
coordinates.

**The orbit is a cycle in the graph, not a curve in space.** The planet
visits a sequence of nodes. If the routing decisions are periodic, the
planet revisits similar nodes. The ellipse is the 3D projection of this
graph cycle.

---

## Core Mechanic: Deposit Propagation on Fixed Graph

### Graph construction (once, never modified)

Random geometric graph. N nodes, k≈24 neighbors each, embedded in a sphere.
The embedding is for VISUALIZATION ONLY. The physics operates on graph
topology — adjacency, not distance.

Connector "length" is fixed at construction. It represents the initial
geometric distance between connected nodes. It NEVER changes. It is used
only for two things:
1. Determining travel time (deposits take `length` ticks to traverse,
   or 1 tick if we treat each connector as 1 hop)
2. Visualization

### Deposit propagation

A deposit is a single quantum with a group tag (s0, s1, p0, etc.).
Deposits move along connectors at 1 hop per tick. When a deposit arrives
at a node:

1. The node's capacitor evaluates the deposit's tag against the node's
   spectrum.
2. **Same** (tag ∈ spectrum): capacitor fires. Deposit is consumed
   (transformed). The node produces one quantum of its own tag on one
   outgoing connector.
3. **Different** (tag ∉ spectrum): deposit queues at this node on the
   arriving connector. Capacitor charges. May fire later when threshold
   is reached (after accumulating enough charge from multiple deposits).
4. **Unknown** — no deposit arrives this tick on this connector. Capacitor
   idle. Nothing happens.

### One discharge per tick per node

The capacitor fires at most once per tick. One quantum in, one quantum out
(when it fires). If multiple deposits arrive on multiple connectors in the
same tick, the capacitor processes ONE (highest priority — see routing
below) and queues the rest.

### Entity as a set of nodes

An entity (star, planet) is a set of nodes that share a spectrum. The
entity's "mass" is its node count. The entity's "surface" is the set of
nodes that have connectors to non-entity nodes. The entity's "interior"
is nodes whose all connectors lead to other entity nodes.

Entity "movement" is: a node fires, hops to an adjacent node. This means
the entity gains one node and loses one node (the hopping node joins the
new location, vacates the old). Or equivalently: the entity's territory
shifts by one node per hop.

### Routing decision (the ONLY physics)

When a node's capacitor fires, it produces one quantum and sends it down
one connector. Which connector?

**Same-routing (gravity):** Route toward the connector with the richest
matching deposits — the direction where the entity's own pattern is
densest. This keeps entity nodes bound together (internal cohesion) and
moves the entity toward regions saturated with matching deposits.

**What happens near a foreign entity:** The planet node is surrounded by:
- Some connectors with planet-pattern deposits (Same → route here for
  cohesion)
- Some connectors with star-pattern deposits (Different → can't fire on
  these directly, but they charge the capacitor)
- Some connectors with nothing (Unknown → frontier)

The planet routes toward its own deposits (Same). But if it has very few
own-deposits (it just arrived, hasn't deposited much), it routes toward
the richest deposit source period — because ANY deposits charge the
capacitor faster than Unknown. This IS gravitational attraction: the
planet moves toward the star because the star's deposit field is the
richest source of charge in the graph.

### Saturation and "pressure"

When the planet is close to the star (few hops away), the star-facing
connectors are saturated with star-pattern deposits. The planet's
capacitor fires on the star-facing connector every tick — maximum
processing rate. But star deposits keep arriving faster than one per tick
(multiple star surface nodes emit toward the planet simultaneously).
Queue grows on the star-facing connectors.

Meanwhile, connectors in other directions have lower deposit density.
The planet's routing signal: all directions are saturated from the star
side, but some directions are less saturated than others. The planet
preferentially routes toward the less-saturated direction.

In a spherical graph embedding, "less saturated" directions are generally
those pointing away from the star — more nodes at larger radii, more
routes to dilute the signal. The planet's routing drifts outward, not
because it's pushed, but because it routes toward functional capacity.

At equilibrium: incoming flux = processing capacity. No saturation. No
preferential routing away from the star. The planet's routing is
dominated by its own internal Same-routing (cohesion) and the gentle
Same-routing toward the star (gravity).

---

## Open Questions for Implementation

### Q1: How do deposits propagate between non-entity nodes?

If a deposit reaches a node that has no entity (unclaimed node), what
happens? Options:

(a) The deposit passes through — unclaimed nodes are transparent. This
    is simple and means deposits propagate freely through empty space.

(b) The unclaimed node has a trivial capacitor — it fires on anything.
    The deposit triggers discharge, and the node re-emits the same
    deposit onward. Effectively the same as (a) but with explicit
    mechanism.

(c) The unclaimed node queues the deposit. Nothing processes it. The
    deposit sits there forever. Space becomes a deposit trap.

**Recommendation: option (a)** — unclaimed nodes pass deposits through.
Space is transparent. Deposits propagate freely until they reach an entity
node.

### Q2: How fast do deposits propagate?

If each connector is 1 hop, deposits move at 1 hop/tick = c. Fine. But
the graph has varying connectivity — some node pairs are connected by
short paths, some by long paths. The "speed of light" between two distant
nodes depends on the graph distance (hop count), not the Euclidean distance.

For the simulation: deposits propagate 1 hop per tick along each connector
they traverse. A deposit emitted by a star node reaches a planet node
`d_graph` ticks later, where `d_graph` is the shortest path length in the
graph.

### Q3: Can multiple deposits be on the same connector simultaneously?

Yes. A connector can carry multiple deposits traveling in the same or
opposite directions. Each deposit moves independently at 1 hop/tick. The
connector is a multi-lane road.

### Q4: Queue management at entity nodes

When deposits queue at an entity node, in what order are they processed?
Options:

(a) FIFO — first arrived, first processed. Simple queue.
(b) Priority — deposits from matching-group sources processed first
    (Same before Different).
(c) Random — each tick, one queued deposit is selected randomly.

**Recommendation: (a) FIFO** — simplest, no additional parameters.

### Q5: Where does the discharge quantum go?

When a node's capacitor fires (consumes one incoming deposit, transforms
it, produces one quantum of its own tag), which outgoing connector receives
the new quantum?

This IS the routing decision. The new quantum goes toward:
- The connector with the densest matching deposits (Same-routing)
- If no matching deposits anywhere: the connector with the densest
  deposits of any kind (charge-seeking)
- If no deposits anywhere: random

### Q6: Entity movement vs deposit emission

When we say the entity "hops," do we mean:

(a) The entity node literally moves — it vacates its current graph position
    and occupies the neighbor. The node's identity transfers.

(b) The entity doesn't move — it deposits a quantum outward. Over time, its
    deposit pattern shifts. The entity's "position" is the center of mass
    of its deposit field, which migrates through the graph.

Option (b) is more consistent with the theory (entities are deposit
patterns, not point objects). But it's harder to track and visualize.

**Recommendation for v5:** Start with option (a) — entities are sets of
nodes that physically hop. Track node positions. If the results are
instructive, v6 can try option (b).

---

## Implementation Phases

### Phase 1: Deposit Propagation Test (NO ENTITIES)

Before any star or planet, verify that deposits propagate correctly on
the fixed graph.

**Setup:**
- Build graph (N=5000, k≈24, sphere R=20)
- Place a single deposit at the center node
- Let it propagate for 100 ticks
- Verify: deposit reaches nodes at graph-distance d after d ticks
- Verify: no deposits are created or destroyed (conservation)
- Verify: connectors don't change length

**Measurements:**
- Number of deposits in the system over time (should be constant if no
  entity consumes them, or should grow only when deposits reach nodes
  that re-emit)
- Spatial distribution of deposits over time (should expand as a
  wavefront from the center)

### Phase 2: Star Formation and Equilibrium

**Setup:**
- Place 80 star nodes near origin, 4 groups (s0–s3)
- Star spectrum: {s0, s1, s2, s3} (mutually Same)
- Each star node operates independently — read connectors, route, fire,
  hop

**The star's internal dynamics should produce:**
1. Internal circulation (star nodes route toward each other — Same)
2. Gradual deposit buildup on internal connectors
3. Leakage at the boundary (some star nodes hop outward, deposit on
   boundary connectors)
4. Deposit field propagating outward from the star cluster

**Measurements (every 500 ticks):**
- Star COM, mean radius, max radius
- Internal deposit density (star-tagged deposits on internal connectors)
- Boundary deposit flux (star-tagged deposits arriving at non-star nodes
  per tick — the "luminosity")
- Queue depths at star surface nodes
- Star discharge rate (how many nodes fired this tick)

**Success criteria:**
1. Star cluster stays coherent (mean radius bounded)
2. Boundary deposit flux stabilizes (star has quasi-steady luminosity)
3. No runaway growth of anything (no connector extension to blow up)

### Phase 3: Planet Introduction — Radial Binding

Same as v4 Phase 2, but with corrected mechanics:

- Planet placed at ~2× star radius (graph distance)
- Planet routes based on deposit density on its connectors
- Expect: planet moves toward star (deposit field is the only signal)
- Expect: at close range, planet saturates, routes away
- Expect: radial oscillation (same as trie_stream_filtering v4)

**Critical new measurement:** Queue depth at planet-facing star nodes.
If the queue grows → the star's deposits are backing up → evidence of
the saturation mechanism.

### Phase 4: Tangential Motion

If Phase 3 produces radial oscillation:

(a) Check if any tangential component exists (it might be small but
    nonzero due to the star's instantaneous asymmetry)

(b) If purely radial: the graph might be too symmetric. Try a star with
    intentionally asymmetric internal structure (e.g. more nodes on one
    side). See if the asymmetry produces tangential nudges.

(c) Give the planet an initial "tangential hop" — manually move it to a
    node that's perpendicular to the radial direction before starting.
    See if the tangential component is maintained.

---

## What v5 Does NOT Have (and why)

- **No EXTEND_RATE** — connectors don't extend
- **No CONSUME_FRAC** — consumption is all-or-nothing (capacitor fires or doesn't)
- **No velocity vectors** — entities route, they don't fly
- **No force computation** — routing IS the force
- **No shared momentum** — each node routes independently
- **No damping** — no artificial friction
- **No decay factor** — temporal filtering from propagation delay, not decay
- **No global expansion** — the graph is fixed
- **No connector modification of any kind** — the substrate is immutable

The ONLY things that change tick to tick:
1. Which node each entity node occupies (hopping)
2. Where deposits are in the graph (propagation)
3. Queue states at entity nodes

---

## Relationship to v4

v4 will finish running and produce results. Those results will show:
- Whether "connector length = deposit count" produces a stable star (Phase 1)
- What the growth dynamics look like when connectors inflate
- The failure mode when deposits stretch space

v5 takes the same experimental goals but on the corrected substrate model.
Direct comparison of v4 and v5 results will show whether the correction
matters — or whether the approximation was good enough.

---

## Connection to RAW Documents

- **RAW 112 §3**: "Light propagation is push-driven, not self-propagating.
  New deposits displace old ones down connectors like a tube."
- **RAW 113 §2.2**: "A photon IS a Different event propagating."
- **RAW 125**: "Reading direction — outer deposit layers encountered first."
- **RAW 126**: "One complete Empty → Charging → Discharge cycle is one tick."
- **RAW 127**: "Observation requires discharge from the observed. The charging
  phase is structurally invisible."

---

*Supersedes: v4 (which conflated deposits with connector extension)*
*Key insight: connectors are fixed roads. Deposits travel on them.*
*Orbital mechanism: routing away from saturated directions, not connector extension.*
*Eccentricity: consumption capacity vs incoming flux mismatch.*
*The orbit is a graph cycle, not a spatial curve.*
