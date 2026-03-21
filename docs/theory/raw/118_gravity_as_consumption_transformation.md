# RAW 118 — Gravity as Consumption and Transformation of Connectors

### *Why Direction Change in an Append-Only Universe Requires Transforming Other into Same*

**Author:** Tom
**Date:** March 21, 2026
**Status:** Working document — theoretical revision of gravitational mechanism
**Prerequisites:** RAW 111 (Space Is Connections), RAW 112 (The Single Mechanism),
RAW 113 (Semantic Isomorphism: Same / Different / Unknown)
**Supersedes:** The passive-reading gravity model used in Experiment 64_109 v1–v24
**Falsifiable:** Yes — predicts equilibrium distance from single mechanism without
global expansion parameter; predicts negligible but non-zero gravitational shielding;
predicts gravity and radiation pressure are two regimes of one saturation curve

---

## Abstract

This document identifies a critical gap between the V3 theory (RAW 111–113) and the
simulation experiments (64_109 v1–v24). The theory claims that all physics reduces to
one operation: deposit on a connector, hop, connector extends. The simulation
implements gravity as passive field reading: entities detect connector growth asymmetry
and route toward lower-growth connectors, but their traversal does not affect the
connectors they cross. Entities read the menu but never eat.

This omission removes the outward pressure mechanism that should balance gravitational
attraction. Without traversal-driven connector extension, dense regions have no internal
pressure and collapse unconditionally — explaining why no experiment version has achieved
stable orbits on the graph substrate.

This document formalizes the correct mechanism: **gravity operates through consumption
and transformation of connectors**, not through passive reading of a field gradient.
Consumption is specifically the transformation of `Different` (foreign deposits) into
`Same` (the entity's own pattern). Entities absorb deposits from the connectors they
traverse, transform them from other-signature to self-signature, deposit their own
pattern onto the connector, and extend the connector through that deposit. Attraction
and repulsion are two aspects of the same act. The equilibrium between consumption
routing (inward) and traversal extension (outward) is the mechanism of gravitational
binding.

---

## 1. The Problem: Passive Reading Cannot Produce Orbits

### 1.1 What the Theory Says

RAW 112 §2.1 defines the single operation:

```
read local field state
→ select laziest connector
→ deposit on that connector
→ hop
→ connector extends
```

Every hop modifies the graph. The connector is longer after traversal than before.
The entity leaves a deposit — a permanent addition to the connector chain. The graph
is different after every hop by every entity.

### 1.2 What the Simulation Does

Experiment 64_109 (all versions v1–v24) implements the force mechanism as:

```python
growth = H / (1 + alpha * (gamma_A + gamma_B))
push = force_coeff * (mean_growth - growth) / inertia
```

The entity reads connector growth rates (suppressed by local gamma density), computes
asymmetry against the local mean, and accelerates toward the lowest-growth connector.
When the entity hops:

```python
graph.move_gamma(self.bid, old_node, new_node)
self.node = new_node
```

Gamma is transferred from the old node to the new node. That is the entire hop
operation. **No deposit on the traversed connector. No extension of the connector.
No transformation of the connector's state.**

The only connector extension mechanism is `graph.expand_edges()` — global H applied
uniformly every tick, suppressed by local gamma density. The entities' hops have zero
effect on connector length.

### 1.3 The Consequence

The simulation implements half of the single mechanism (reading) and omits the other
half (writing). The reading half produces attraction. The writing half should produce
repulsion (every traversal extends the connector, pushing the endpoints apart). Without
the writing half, there is no equilibrium. Dense clusters collapse because nothing
opposes the inward routing.

Furthermore, global H with gamma-density suppression actively inverts the correct
pressure profile. Dense regions — where traversal traffic should be highest and
therefore extension should be strongest — experience the least expansion. The
simulation's expansion mechanism has the wrong sign for dense objects.

This explains every failure mode in the experimental arc: point-mass collapse (all
versions), escape without capture (v22–v23), anti-Newtonian force scaling from float
self-suppression (v24), and the inability to achieve closed orbits despite correct
qualitative attraction.

---

## 2. The Correct Mechanism: Consumption-Transformation

### 2.1 Why Append-Only Forces This

In an append-only universe, exactly three things can happen to an entity at a node:
follow existing structure (`Same`), create a branch (`Different`), or write to the
frontier (`Unknown`). None of these is "be deflected by a force." Force has no socket
in the architecture.

The entity changes direction by **what it reads at the current node**. If connectors
in one direction carry deposits matching the entity's pattern (`Same`), and connectors
in another direction carry non-matching deposits (`Different`), the entity routes
toward `Same`. That routing IS the direction change.

But reading is not free. In an append-only substrate, every interaction leaves a trace.
The entity cannot inspect a connector without affecting it. The act of comparing the
arriving pattern to the connector's deposits is itself a deposit event — the entity's
pattern is written onto the connector as part of the comparison. The connector is
transformed by the reading.

This is not a design choice. It is forced by the append-only axiom. If the entity
could read without writing, information would be extracted from the connector without
any record of the extraction. That extraction would be a deletion — the connector
loses the information that "entity X read me at tick T." Deletions are forbidden.
Therefore readings must leave deposits. Therefore traversal transforms connectors.

### 2.2 The Full Hop Operation

The correct single operation, stated completely:

```
1. Entity arrives at node A
2. Entity reads deposits on all k local connectors (comparison step)
3. Entity identifies the connector with the richest transformable deposits
4. Entity CONSUMES deposits from connector A→B
   — absorbs the connector's deposit signature into its own directional state
   — transforms foreign deposits (Different) into self-pattern (Same)
5. Entity DEPOSITS its own transformed pattern onto connector A→B
   — the connector now carries entity-signature where it previously carried other
6. Entity hops from A to B
7. Connector A→B is longer (old deposits + new entity deposits = longer chain)
```

Steps 4 and 5 are what the simulation omits. They are not optional embellishments
of the single mechanism. They are the mechanism.

### 2.3 Consumption Is Transformation of Different into Same

This is the central insight that corrects the passive-reading model.

In the passive model, gravity routes entities toward regions where `Same` already
dominates — toward familiar deposits. The entity follows what matches.

In the consumption model, the entity is drawn toward the **richest source of
transformable deposits** — which are `Different`, not `Same`. A star's deposits
at the planet's location are star-signature, not planet-signature. They are
`Different` from the planet's perspective. But they are dense, rich, and
transformable. The planet routes toward them because that is where the most
transformation is possible.

**Consumption is the act of transforming `Different` into `Same`.** The entity
absorbs foreign deposits and overwrites them with its own pattern. What was
other-signature becomes self-signature. What was `Different` becomes `Same`.

This reframes the three-state alphabet at the point of traversal:

| Before traversal                                         | After traversal                                        | What happened                    |
|----------------------------------------------------------|--------------------------------------------------------|----------------------------------|
| Connector carries star-signature (`Different` to planet) | Connector carries planet-signature (`Same` to planet)  | Consumption: Different → Same    |
| Connector carries planet's own prior deposits (`Same`)   | Connector carries reinforced planet-signature (`Same`) | Self-reinforcement: Same → Same  |
| Connector carries no deposits (`Unknown`)                | Connector carries planet-signature (`Same` to planet)  | Frontier writing: Unknown → Same |

In all three cases, the entity converts toward `Same`. But the gravitational
routing — the direction change — comes specifically from the `Different → Same`
transformation. That is where the richest deposits are. That is where the most
connector extension occurs (because transformation adds the entity's deposits
ON TOP of the existing foreign deposits, creating the longest chains). That is
where gravity points.

**Gravity is the substrate's tendency to transform `Different` into `Same`.**

The gravitational field near a star looks like a gradient of `Different` to an
approaching entity: dense star-deposits that are not the entity's own pattern.
The entity is drawn toward the densest `Different` because that is where the
most transformation is available. As the entity (and others before it) traverse
the region, they transform those deposits — and the region gradually becomes more
`Same` to subsequent visitors. The field is not static. It is continuously being
consumed and replenished.

### 2.4 Transformation as the Meaning of Deposit

When the entity consumes star-signature deposits from a connector and deposits its
own pattern in return, the connector is transformed. Before traversal: the connector
carried star-signature. After traversal: the connector carries a mixture of star-
signature (unconsumed residual) and entity-signature (newly deposited).

The deposit is not a passive label. It is the physical transformation of the
connector's state. The entity has changed the graph by traversing it. Every hop
rewrites the local topology.

### 2.5 Why the Star Must Continuously Deposit

If consumption transforms `Different` into `Same`, the star's deposit field is
being consumed by every entity that traverses it. Connectors near the star that
originally carried star-signature are gradually transformed into planet-signature,
debris-signature, photon-signature — whatever passed through.

For the gravitational gradient to persist, the star must continuously replenish
its deposits. Each tick, the star deposits fresh star-signature onto its local
connectors. Those deposits spread outward through the graph. Meanwhile, orbiting
entities consume and transform the outer reaches of the field.

Gravity is a **dynamic equilibrium between production and consumption** — not a
static field. The star produces `Different` (from the perspective of everything
else). Everything else consumes and transforms it toward their own `Same`. The
gradient persists only as long as production exceeds consumption at each radius.

### 2.6 Gravity Never Reaches Zero

The append-only axiom guarantees that every deposit ever made is still in the
graph. A star that has been depositing for a million ticks has sent deposits
propagating outward through connectors for a million ticks. Those deposits spread,
dilute, get consumed and transformed by everything they pass through — but they
never reach zero. At enormous distances the deposits are sparse. Maybe one connector
in a thousand carries a single quantum of star-signature. But it is there.

An entity at that distance has k connectors. Perhaps 23 carry nothing from the
star. One carries a single quantum. That tick, the entity consumes that one quantum
and routes slightly starward. Next tick, maybe a different connector has one. Or
maybe none do for several ticks. Then one appears. The routing is stochastic,
intermittent, noisy — but it has a net bias toward the star, because the star-
signature deposits, however sparse, are never exactly isotropic.

This produces a **transition from deterministic to stochastic gravity** as a
function of deposit density:

| Distance regime | Deposit density per connector       | Gravity character                         |
|-----------------|-------------------------------------|-------------------------------------------|
| Near the star   | Many quanta per connector           | Deterministic: strong, smooth attraction  |
| Intermediate    | ~1 quantum per connector            | Noisy: intermittent routing with net bias |
| Far             | << 1 quantum per connector per tick | Stochastic: Brownian drift with weak bias |

There is no gravitational horizon — no radius beyond which gravity is zero. The
star's influence extends everywhere its deposits have ever propagated, which
(given enough time) is the entire connected graph. It just becomes progressively
noisier with distance, transitioning from deterministic force to Brownian drift.

This is consistent with Newtonian gravity (1/r² to infinity, never zero) and
also consistent with the Brownian motion observed in Experiment 64_109 v6, where
integer quanta on a lattice produced genuine stochastic drift of cluster centers
with diffusion coefficient D ~ 1/M². That was not a simulation artifact — it was
the correct low-density behavior of integer consumption on the graph.

The earlier version of this document (§2.5 in the first draft) incorrectly
predicted a "gravitational horizon" — a hard cutoff radius. This was wrong. The
append-only axiom forbids any deposit from reaching zero. Gravity is infinite in
reach but finite in precision: at sufficient distance it becomes indistinguishable
from noise.

---

## 3. Mass as Consumption Capacity

### 3.1 Why Point-Mass Is Wrong

The simulation (v1–v24) represents a star as a single node with a mass parameter
(e.g., mass=1000 or mass=1000000). This node has k connectors (typically k=24 on
the random geometric graph, k=6 on the cubic lattice). Regardless of the mass label,
the node can only interact with k connectors per tick.

A genuinely massive entity should be a **distributed pattern spanning many nodes**.
A star with mass 1000 should occupy hundreds or thousands of nodes, each with its
own k connectors. The star's total consumption capacity scales with its spatial
extent:

```
total_receptors = N_nodes × k
```

where N_nodes is the number of nodes the entity occupies and k is local connectivity.

A single node with mass=1000 has the same consumption capacity as a single node with
mass=1. The mass label tells the field "I'm heavy" but doesn't consume like a heavy
object. This is why the point-mass simulation cannot produce correct gravitational
dynamics: the source has the wrong consumption/radiation profile.

### 3.2 Mass as Receptor Count

In the consumption model, mass is operationally defined as:

> **Mass = total consumption capacity = number of connectors the entity can process
> per tick.**

This scales with spatial extent. A 1-node entity has mass proportional to k. A
100-node entity has mass proportional to 100k. The relationship between mass and
size is structural, not parameterized.

A massive entity:

- Consumes more incoming deposits per tick (more receptors)
- Deposits more of its own pattern per tick (more output connectors)
- Extends more connectors per tick (more traversals)
- Creates a larger deposit field (more source nodes)
- Has a higher inertia (more internal state to redistribute before hopping)

All of these scale with N_nodes, not with a mass label.

### 3.3 Why Dense Clusters Collapse in the Simulation

If you place 1000 entities on nearby nodes in the current simulation, every entity
reads every other entity's deposits and routes toward the center of deposit density.
Nothing opposes the collapse because:

1. The entities don't extend connectors through traversal (omitted from simulation)
2. Global H is suppressed in the dense region (wrong pressure sign)
3. There is no radiation mechanism (`Different` is not implemented)

In the correct mechanism: 1000 entities hopping through local connectors every tick
would produce enormous traversal-driven extension. The denser the cluster, the more
hops per tick, the more extension, the more outward pressure. Equilibrium should
emerge at the density where consumption routing (inward) balances traversal extension
(outward).

---

## 4. The Equilibrium Mechanism

### 4.1 Two-Body Case

Consider two entities, A and B, separated by a chain of connectors.

**Inward mechanism (attraction):**
Entity A's deposits spread outward through connectors. At B's location, connectors
pointing toward A carry denser deposits — rich, transformable `Different`. B routes
toward A to consume and transform those deposits. Similarly, A routes toward B.

**Outward mechanism (repulsion):**
Every time B hops toward A, B deposits on the traversed connector, extending it.
Every time A hops toward B, A deposits on the traversed connector, extending it.
The connectors between A and B are the most heavily traversed in the system. They
experience the most extension.

**Equilibrium:**
At close range: traversal rate is high (many hops through short connectors), extension
is rapid, outward pressure dominates. Distance increases.

At far range: deposit field is dilute, `Different` signal is weak, consumption rate
is low, traversal rate is low, extension is minimal. Inward routing dominates.
Distance decreases.

At some intermediate distance: consumption rate equals extension rate. The entities
maintain stable separation without any external parameter.

### 4.2 Multi-Body Case (Star + Planet)

A star (distributed cluster, many nodes) radiates deposits outward through all its
connectors. A planet (small pattern, few nodes) sits at distance r.

The planet consumes star-deposits from its k local connectors. The consumption is
limited by the planet's receptor count (k × N_planet_nodes). The star's deposit
flux at distance r scales as:

```
flux(r) ~ deposit_rate_star / (4π r²)     [in 3D-like graph topology]
```

The planet can only consume:

```
consumed = min(flux(r) × cross_section, receptor_capacity)
```

At the planet's location, the consumed deposits are transformed (star-signature →
planet-signature) and radiated outward. The total deposit density is approximately
conserved: what the planet consumed as `Different`, it replaced with its own output
(now `Same` to the planet, `Different` to everyone else). From far away, the field
looks like star + planet. No significant shielding.

The planet's connectors toward the star extend with each traversal. The planet's
connectors away from the star experience less traffic and extend less. The asymmetry
in extension rate produces a net outward drift that balances the inward consumption
routing.

### 4.3 The Self-Regulating Star

A star is a cluster of many entities, each consuming and depositing at every tick.
Internal connectors (between star-nodes) experience maximum traversal traffic. This
produces maximum extension — internal pressure.

The star doesn't collapse because its own internal traversal traffic pushes its
connectors apart. The denser the core, the more traffic, the more extension, the
more pressure. This is the append-only analogue of hydrostatic equilibrium —
without requiring radiation pressure from nuclear fusion as a separate mechanism.

Whether this internal traversal pressure is sufficient to prevent collapse for
realistic entity counts is an empirical question that requires simulation. It is
possible that additional mechanisms (radiation via `Different` events) are needed
for full stability. The point is that the traversal pressure exists and is currently
absent from all simulations.

---

## 5. Gravitational Shielding: Predicted Negligible

### 5.1 The Consumer-Producer Cycle

An entity is not a pure consumer. It consumes incoming deposits AND radiates its own
deposits outward. Every tick: absorb from local connectors, transform `Different` to
`Same`, deposit outward through all k connectors (which are now `Different` from
everyone else's perspective).

When a planet sits between a star and a test particle:

- The planet consumes some star-deposits arriving from the star-facing side
  (transforming star-`Different` into planet-`Same`)
- The planet radiates its own deposits outward through all connectors, including
  those facing the test particle (producing planet-`Different` for the test particle)
- The total deposit density at the test particle's location ≈ star field + planet
  field - small absorption loss

### 5.2 The Absorption Loss

The planet's consumption-radiation cycle is not perfectly efficient. Some deposit
energy goes into internal state maintenance — binding energy, self-pinning. The
planet radiates slightly less than it consumes. There is a small net absorption.

The shielding fraction is approximately:

```
shielding ~ binding_efficiency_loss × (cross_section / 4π r²)
```

For the Moon during a solar eclipse (the Allais effect scenario):

- The Moon's binding loss fraction is small (the Moon is not a significant energy sink
  relative to the Sun's output)
- The Moon's angular cross-section as seen from Earth's surface is ~0.5°
- The predicted shielding effect is orders of magnitude below current gravimeter
  sensitivity

This is consistent with the observational record: one questionable observation
(Allais, 1954), no confirmed replication, generally attributed to instrumental
artifact.

### 5.3 Comparison with GR

General relativity predicts exactly zero gravitational shielding. The consumption
model predicts negligible but non-zero shielding, proportional to the absorber's
binding efficiency loss. This is in principle a falsifiable difference, though the
predicted magnitude is likely below any achievable measurement precision for
astronomical bodies.

The distinction becomes potentially significant for extreme objects: a black hole
(maximum binding efficiency, maximum absorption) should produce measurable shielding.
Whether this connects to known black hole physics (e.g., the no-hair theorem, or
the membrane paradigm where the horizon absorbs incoming radiation) is an open
question.

---

## 6. Connectors vs Deposits: The Saturation Threshold

### 6.1 The Distinction

A critical distinction must be maintained between two concepts that are easy to
conflate:

**Connectors** are the permanent structural links between nodes — the persistent
deposit chains that constitute the graph topology. They are the roads. They are
built by prior deposits. They persist because the append-only axiom forbids their
removal. Once a connector exists, it exists forever. It can be extended (made
longer) but never deleted.

**Deposits** are what connectors carry — the accumulated patterns left by entities
that traversed or deposited onto those connectors. They are the cargo on the roads.
Different entities deposit different signatures. The connector accumulates all of
them (append-only).

**Radiation is not a connector.** A photon propagating across the universe is a
`Different` event consuming the deposits carried by the connectors it traverses.
It does not consume the connectors themselves. The photon eats the cargo, not the
road. After the photon passes, the connector is still there — other photons can
follow the same path. But the deposits on that connector have been partially
transformed (the photon left its own signature in exchange for what it consumed).

This is why we can see galaxies billions of light-years away. The connectors
spanning that distance are permanent infrastructure, built by the accumulated
deposit history of the universe. Photons traverse those connectors, consuming
deposits along the way. Each consumption event depletes the photon's pattern
slightly — the photon has less to deposit at each successive hop than it had at the
previous one. Over billions of hops, this cumulative depletion manifests as
cosmological redshift: the photon arrives with a lower `Different` firing rate
(lower frequency) and fewer parallel paths (lower amplitude) than it had at
emission.

The connectors remain after the photon passes. The next photon follows the same
roads. Space is transparent precisely because connectors are permanent and photons
consume only deposits, not structure.

### 6.2 Why Space Is Transparent

In cosmic voids, connectors carry almost no deposits — few entities have ever
traversed them, so their cargo is sparse. A photon passing through a void
encounters connectors with minimal deposits. There is almost nothing to consume.
The photon passes through with negligible energy loss.

Near massive bodies, connectors carry dense deposits from the body's continuous
radiation. A photon passing through this region encounters rich deposits. It
consumes more. It loses more energy. This is gravitational redshift — a photon
climbing out of a gravitational well loses energy not because of spacetime
curvature, but because it consumed dense deposits during traversal through the
deposit-rich region.

### 6.3 The Saturation Unification

With the connector/deposit distinction in place, the relationship between gravity
and radiation pressure becomes a single saturation curve.

An entity sits at its node. Its k connectors each carry deposits — placed there by
the star, by other entities, by prior traversals. Each tick, the entity processes
those deposits through its receptors. Processing IS consumption — transformation of
`Different` into `Same`.

The entity has a finite receptor capacity: it can process at most k × efficiency
deposits per tick (where efficiency depends on pattern match quality and entity
complexity). The incoming deposit flux depends on the environment — how much
`Different` material is arriving on connectors each tick.

The ratio of incoming flux to receptor capacity determines everything:

**Undersaturated (flux < capacity):**
The entity can consume and transform all incoming deposits. It successfully converts
incoming `Different` to `Same`. The connectors toward the richest source get consumed
preferentially. The entity routes toward the source. Connectors extend modestly
(one entity's deposit per traversal).

Net effect: **pull — gravitational attraction.**

**Oversaturated (flux > capacity):**
The entity cannot consume fast enough. Unconsumed deposits accumulate on the
incoming connectors. They are append-only — they cannot be removed. The connector
chains grow from the excess. The entity's connectors extend faster than the entity
can process them. The structural growth of overburdened connectors pushes the entity
outward.

Net effect: **push — radiation pressure.**

**Balanced (flux ≈ capacity):**
Consumption matches arrival. Connectors extend at exactly the rate needed to
maintain current distance. The entity is in equilibrium.

Net effect: **stable configuration.**

### 6.4 One Mechanism, One Threshold

The critical insight: pull and push are not two forces. They are two regimes of one
consumption process, separated by a saturation threshold:

```
consumption_rate > deposit_arrival_rate  →  entity hungry   →  pull toward source
consumption_rate < deposit_arrival_rate  →  entity overfed  →  push from source
consumption_rate = deposit_arrival_rate  →  equilibrium     →  stable distance
```

This maps onto an observed astrophysical phenomenon: the **Eddington luminosity**.
The Eddington limit is the exact threshold where radiation pressure outward equals
gravitational attraction inward for infalling material around a luminous body.
Below the Eddington limit: matter falls in (gravity wins). Above it: matter is
blown outward (radiation pressure wins).

Standard physics treats gravity and radiation pressure as two independent forces
with independent coupling constants (G and σ_Thomson) that happen to cancel at a
particular luminosity. In the consumption model, they are the same force — deposit
consumption — operating below and above a saturation threshold. The Eddington
luminosity is the point where incoming deposit flux per receptor equals one
processing cycle per tick. The cancellation is not coincidental. It is structural.

### 6.5 Testable Consequence

If push and pull are two regimes of the same mechanism, the transition between them
should be governed by a single saturation curve — smooth, with a specific shape
determined by the receptor saturation function. Near the crossover, the net force
passes through zero continuously.

In standard physics (two independent forces), the transition is the intersection of
two straight lines (gravity ∝ M, radiation pressure ∝ L). In the consumption model,
the transition follows a saturation curve (similar to Michaelis-Menten enzyme
kinetics or Langmuir adsorption isotherms).

The shape of the force-vs-flux curve near the Eddington limit is in principle
measurable for systems where luminosity can be varied continuously (e.g., variable
stars, accretion disks with varying accretion rates). If the transition follows a
saturation curve rather than a linear crossing, this constitutes observational
evidence for the consumption model.

---

## 7. Implications for Experiment Design

### 7.1 What Must Change

The next experiment version must implement:

1. **Traversal-driven connector extension.** When entity E hops from node A to node B,
   the A→B connector length increases by an amount proportional to E's deposit.
   This replaces global H as the expansion mechanism.

2. **Distributed mass.** The star must be a cluster of many nodes, not a single node
   with a mass label. Each node in the cluster deposits and consumes independently.
   The cluster's total mass = its total receptor count.

3. **Consumption on traversal.** When entity E traverses connector A→B, the deposits
   on A→B are partially absorbed by E (transforming `Different` to `Same` within E)
   and replaced by E's own deposits (now `Different` from the perspective of others).
   The connector's state is transformed by the traversal.

### 7.2 Proposed Experiment: Equilibrium Distance from Single Mechanism

**Objective:** Demonstrate that two entities on a graph substrate, interacting only
through the full single mechanism (consume-transform-deposit-extend), achieve a stable
separation distance without any global expansion parameter (H=0).

**Setup:**

- Graph: Random geometric graph, N=10000–30000 nodes, k=24
- Entity A: Cluster of ~100 nodes, depositing every tick, consuming from local
  connectors
- Entity B: Small pattern, 1–5 nodes, depositing and consuming
- H = 0 (no global expansion)
- Initial separation: ~20 hops

**Protocol:**

1. Let both entities deposit for 5000 ticks to establish fields
2. Release entity B with zero initial velocity
3. Measure: does B fall toward A indefinitely (collapse), escape, or stabilize at
   an equilibrium distance?

**Success criterion:**

- B reaches a minimum distance and then maintains approximately constant separation
  for >10000 ticks
- The equilibrium distance depends on the ratio of A's deposit rate to B's
  receptor count
- No global parameters (H, drag, jitter) are used

**Failure modes:**

- B collapses onto A → traversal extension is too weak to balance consumption routing
- B escapes → traversal extension overwhelms consumption routing
- B oscillates without damping → the mechanism lacks a dissipation channel

Each failure mode is informative: it identifies which aspect of the single mechanism
needs refinement.

### 7.3 Proposed Experiment: Distributed Star with Orbiting Test Particle

**Objective:** Demonstrate a stable orbit (closed or quasi-closed trajectory) of a
test particle around a distributed star, using only the full single mechanism.

**Setup:**

- Graph: Random geometric graph, N=50000–100000 nodes, k=24
- Star: Cluster of ~500 nodes bound through mutual consumption and internal
  traversal pressure. Formed through self-assembly (many entities deposited at
  nearby nodes, allowed to reach internal equilibrium).
- Test particle: 1 node, given tangential initial velocity
- H = 0

**Protocol:**

1. Phase 0 (star formation): Seed 500 entities at nearby nodes. Run until cluster
   reaches internal equilibrium (stable mean radius, no further contraction).
   If cluster collapses to a point, the experiment fails — traversal extension is
   insufficient for internal pressure.
2. Phase 1 (field establishment): Continue depositing until the star's gradient
   extends to orbital distances (~50 hops). Monitor radial profile for 1/r²
   convergence.
3. Phase 2 (orbit test): Place test particle at ~40 hops with tangential velocity.
   Run for >50000 ticks. Measure orbital parameters.

**Success criterion:**

- Star maintains stable spatial extent through internal traversal pressure
- Deposit gradient approximates 1/r² at orbital distances
- Test particle completes >1 full orbit without escape or collapse
- Angular momentum is approximately conserved

This experiment has never been attempted because the traversal-driven extension
mechanism has never been implemented. It is the primary experimental target for
validating the consumption-transformation model.

---

## 8. Connection to Existing Documents

| Concept                             | This document                                              | Prior document    |
|-------------------------------------|------------------------------------------------------------|-------------------|
| Single mechanism                    | Expanded: consume-transform-deposit-extend                 | RAW 112 §2.1      |
| Gravity as Same                     | Corrected: gravity = transformation of Different into Same | RAW 113 §2.1      |
| Self-pinning                        | Reinterpreted: traversal pressure, not H suppression       | RAW 112 §2.7      |
| Mass as commitment cost             | Extended: mass = receptor count = consumption capacity     | RAW 112 §2.3      |
| Space is connections                | Unchanged — connectors are deposit chains                  | RAW 111           |
| Append-only axiom                   | Used to derive why traversal must transform                | RAW 112 §4        |
| Three-state alphabet                | Deepened: consumption = Different → Same transformation    | RAW 113 §1        |
| Point-mass limitation               | Identified: single-node mass is structurally wrong         | Exp 64_109 v1–v24 |
| Gravitational shielding             | Predicted negligible from consumer-producer cycle          | New               |
| Equilibrium from single mech.       | Predicted: consumption vs extension balance                | New               |
| Gravity-radiation unification       | Pull and push are undersaturated/oversaturated regimes     | New               |
| Eddington limit                     | Reinterpreted as receptor saturation threshold             | New               |
| Deterministic-stochastic transition | Gravity becomes Brownian drift at low density              | New               |

---

## 9. What This Document Does NOT Claim

1. **It does not claim the consumption model is correct.** It claims the consumption
   model is the only mechanism compatible with the append-only axiom and the three-
   state alphabet. Whether the resulting dynamics match observed physics requires
   simulation and comparison. The model might be wrong. The prediction might fail.

2. **It does not solve the orbit problem.** It identifies why the orbit problem has
   not been solved (missing half of the single mechanism) and proposes what the
   correct implementation should look like. Whether the correct implementation
   actually produces orbits is an empirical question.

3. **It does not derive the gravitational constant.** The receptor-count model
   suggests G emerges from the ratio of local connectivity (k) to geometric
   spreading factor (4πr² in 3D topology). The precise derivation requires knowing
   the functional form of consumption efficiency, which is not yet specified.

4. **It does not address electromagnetism.** The consumption model describes the
   `Same` mechanism (gravity) and the `Different → Same` transformation. The
   `Different` mechanism (radiation/EM) is not yet reformulated in V3 graph-first
   language. That reformulation requires solving gravity first — once stable orbital
   dynamics exist, rotation of bound systems will produce helical deposit trails
   that should map onto the V2 magnetic field description (RAW 086) without
   additional postulates. But this is expected, not demonstrated.

---

## 10. Open Questions

1. **Consumption efficiency function.** What fraction of a connector's deposits does
   an entity absorb per traversal? Is it proportional to the entity's receptor
   count? Is it proportional to the `Same` match quality (i.e., how transformable
   the `Different` deposits are)? Is there a maximum absorption rate per connector
   per tick?

2. **Extension magnitude.** By how much does a connector extend per traversal? Is it
   proportional to the entity's deposit (mass-dependent)? Is it a fixed quantum per
   hop? The ratio of extension to consumption determines the equilibrium distance.

3. **Self-consumption.** An entity's own deposits spread into its local connectors.
   When the entity hops, does it consume its own prior deposits? Those deposits are
   `Same`, not `Different` — so consumption (which is `Different → Same`
   transformation) would not apply. This suggests self-deposits are traversed but
   not consumed — the entity reinforces its own connectors without extending them
   as much. If correct, this naturally produces the self-subtraction behavior
   already needed for field reading.

4. **Radiation pressure.** Is traversal-driven extension sufficient to prevent
   gravitational collapse of a distributed star, or is radiation (`Different` events
   propagating outward) also required? If radiation is required, the experiment
   cannot succeed with `Same` alone — the `Different` mechanism must be implemented
   first.

5. **Dissipation channel.** For stable orbits (not just equilibrium distance), the
   system needs a mechanism to dissipate excess kinetic energy. In the consumption
   model, each traversal transforms the connector — some of the entity's kinetic
   energy is deposited into the connector chain as extension. This is a natural
   dissipation mechanism (kinetic energy → graph extension). Whether the dissipation
   rate produces stable orbits or overdamped/underdamped oscillation is an empirical
   question.

6. **Conservation laws.** If the entity consumes deposits and replaces them with its
   own pattern, is total deposit mass conserved? What is the conserved quantity?
   Is it total deposit count (number of deposits in the graph), total deposit
   energy (some function of deposit density × connector length), or something else?

7. **Deterministic-stochastic transition radius.** §2.6 establishes that gravity
   transitions from deterministic to stochastic as deposit density per connector
   drops below ~1 quantum. At what radius does this transition occur for a given
   star mass? Is this transition radius consistent with the observed boundary
   between Keplerian orbital dynamics (deterministic) and the diffuse dynamics
   of the outer Oort cloud (stochastic)? The transition should depend on the
   star's deposit rate and the graph's local connectivity — both potentially
   derivable quantities.

8. **Saturation curve shape.** §6.5 predicts the gravity-to-radiation-pressure
   transition follows a saturation curve, not a linear crossing. What is the
   functional form of this curve? Does it match Michaelis-Menten kinetics
   (v = V_max × [S] / (K_m + [S]))? Is the Eddington luminosity derivable from
   the receptor saturation function without introducing separate coupling constants
   for gravity and radiation?

9. **Cosmological redshift.** §6.1 attributes cosmological redshift to cumulative
   deposit consumption along the photon's path. Does this produce the correct
   redshift-distance relationship (Hubble's law: z ∝ d for small z)? The consumption
   per hop should be small and approximately constant in empty space, producing
   linear cumulative depletion — which matches Hubble's law qualitatively. The
   quantitative prediction requires knowing the consumption rate per hop in
   intergalactic connectors, which is not yet specified.

---

## 11. Summary

The V3 theory's single mechanism — deposit, hop, extend — contains both attraction
and repulsion in one operation. Attraction: the entity routes toward the richest
transformable deposits (`Different` that can become `Same`). Repulsion: every traversal
extends the connector (append-only deposit adds to the chain).

**Consumption is the transformation of `Different` into `Same`.** The entity does
not follow familiarity — it creates familiarity by consuming and transforming foreign
deposits into its own pattern. Gravity is the substrate's tendency to convert
`Different` into `Same`.

**Gravity never reaches zero.** The append-only axiom guarantees that every deposit
persists forever. At large distances, deposits become sparse and gravity transitions
from deterministic attraction to stochastic Brownian drift — but it never vanishes.
There is no gravitational horizon, only a transition in character.

**Gravity and radiation pressure are two regimes of one mechanism.** Below receptor
saturation: pull (the entity consumes everything, routes toward the source). Above
receptor saturation: push (unconsumed deposits extend the connectors, pushing the
entity away). The Eddington luminosity is the saturation threshold. The transition
is structural, not a coincidental balance of independent forces.

**Connectors are permanent. Deposits are consumed.** Radiation is the consumption
of deposits carried by connectors, not the consumption of the connectors themselves.
This is why space is transparent and why we can see galaxies at cosmological distances.

The simulation (Experiment 64_109 v1–v24) implements only the attraction half. Entities
read connector asymmetry but do not consume deposits, do not transform connectors, and
do not extend connectors through traversal. The only expansion is global H, which is
suppressed in dense regions — the opposite of traversal-driven pressure.

This omission is the structural reason why no experiment version has achieved stable
orbits. The fix is not a parameter adjustment. It is implementing the full single
mechanism as the theory describes it.

**Status: Theoretical. Awaiting implementation and experimental test.**

---

## References

- RAW 111 — Space Is Connections (February 2026)
- RAW 112 — The Single Mechanism (March 2026)
- RAW 113 — The Semantic Isomorphism: Same / Different / Unknown (March 2026)
- Experiment 64_109 v1–v24 — Three-Body Dynamics on Graph Substrate
- Experiment 64_109 v6 — Integer quanta Brownian motion (stochastic gravity observed)
- Allais, M. (1959) — "Should the Laws of Gravitation be Reconsidered?" (anomalous
  pendulum observations during solar eclipse)

---

*Date: March 21, 2026*
*Status: DRAFT*
*Depends on: RAW 111, RAW 112, RAW 113*
*Supersedes: Passive-reading gravity model in Experiment 64_109 v1–v24*
*Opens: Consumption efficiency function, extension magnitude, self-consumption,
radiation pressure requirement, dissipation channel, conservation laws,
deterministic-stochastic transition, saturation curve shape, cosmological redshift
derivation, equilibrium experiment, distributed-star orbit experiment*
