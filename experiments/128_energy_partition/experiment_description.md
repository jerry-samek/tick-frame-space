# Experiment 128: The Energy Partition — Entities as Deposit Patterns

## Status: SPEC
## Date: April 3, 2026
## Author: Tom (theory), Claude (spec)
## Theory: RAW 128 (Store, Move, or Radiate), RAW 113 (Same/Different/Unknown)
## Supersedes: Experiment 118 (Consumption-Transformation Gravity, v1-v17)

---

## Why This Experiment Exists

Experiment 118 ran 17 versions testing whether entities hopping on a random
geometric graph produce orbital mechanics. Result: gravitational binding YES,
coherent orbits NO. The v9 diagnostic proved all "orbits" are bound random
walks.

The deepest finding from 118: **the graph doesn't move. What moves is
statistics.** Entity "position" on the graph is a simplification. In the
theory, an entity IS a deposit pattern — a statistical distribution of
Same-tagged deposits across a region of connectors. "Movement" is this
distribution shifting through the network.

Experiment 128 tests this: **entities are not objects at graph nodes. Entities
are deposit patterns on connectors. The pattern shifts as new deposits are
added and old deposits become statistically dominated. Movement is visualization
of statistical change.**

---

## What Experiment 118 Proved (Carry Forward)

1. **Connector = deposits.** The connector IS its deposit chain. Nothing underneath.
   Length = initial geometric distance + Different deposit count.
2. **Same/Different extension rule.** Same deposits reinforce (no growth). Different
   deposits extend (growth). Internal connectors stay short.
3. **Consumption.** Same deposits consume (reclassify) one Different deposit.
   Connectors can shrink. Equilibrium distances from production/consumption balance.
4. **Newton I.** Forward continuation is necessary. Pure reactive = deadlock.
5. **Traversal time proportional to length.** Time dilation from connector length.
6. **Star thermal equilibrium.** 80 random-walking nodes fill 73% of any graph.
   Scale-invariant. This is thermodynamics, not a bug.
7. **The photon builds the road.** Propagating deposits create/extend connectors.

## What Experiment 118 Got Wrong

1. **Entities as point objects hopping between graph nodes.** The theory says
   entities ARE patterns, not objects. An entity's "position" is the statistical
   center of its deposit distribution, not which node it occupies.
2. **Movement as graph traversal.** Entities don't teleport between nodes. The
   deposit pattern SHIFTS through the connector network as new deposits are added.
3. **Pre-built graph as the universe.** The graph should grow from entity activity,
   not be fully constructed at initialization. Space is CREATED by deposits, not
   pre-existing.

---

## The New Model: Entities as Patterns

### What an entity IS

An entity is a contiguous region of connectors where one family's deposits
dominate. The "star" is the region where star-tagged deposits (s0, s1, s2, s3)
are the majority on every connector. The "planet" is the region where
planet-tagged deposits (p0, p1) dominate.

The entity doesn't have a "position" separate from its deposit distribution.
The entity IS the distribution.

### What movement IS

Movement is the statistical shift of the dominant-deposit boundary. When the
star deposits on a connector at the edge of its region, the star's boundary
extends by one connector. When the planet's deposits consume star deposits
on a boundary connector (Same reclassifies Different), the planet's boundary
advances.

"The star moved closer to the planet" means: the boundary between star-dominant
and planet-dominant regions shifted toward the planet. No entity hopped. No
node changed ownership. The STATISTICS changed.

### What the graph IS

The graph is the connector network. Nodes are junctions where connectors meet.
Connectors carry deposits. The graph structure (which nodes connect to which)
is determined by the deposit history — connectors exist BECAUSE deposits
were placed along paths.

In this model, the graph can GROW: new connectors are created when propagating
deposits reach frontier nodes (Unknown territory). The universe expands as
radiation reaches new regions.

### The energy partition (RAW 128)

Each deposit quantum, when it reaches the boundary between two entities, has
three possible outcomes:

1. **STORE**: The deposit is absorbed by the receiving entity's spectrum
   (Same → consumed, connector shrinks). The entity's mass grows (more
   deposits in its region). No movement.

2. **MOVE**: The deposit advances the boundary (Different → extends the
   connector into the other entity's region). The depositing entity "moved"
   — its statistical boundary shifted forward.

3. **RADIATE**: The deposit goes sideways — perpendicular to the boundary.
   It neither grows the entity (not stored) nor advances the boundary (not
   forward). It propagates into empty space, extending a connector in a
   new direction. Energy leaves the entity pair.

The partition is determined by the LOCAL GEOMETRY at the boundary, not by
an agent's decision. Same as RAW 128: one quantum, three outcomes, no choice.

---

## Implementation Approach

### Phase 0: Minimal Model — One Connector, Two Entities

Start with the simplest possible test: a single connector chain between
a "star" and a "planet." No graph. Just a 1D chain of deposits.

```
[s][s][s][s][s][s]|[p][p][p][p]
                  ^
             boundary position
```

Each tick:
1. Star deposits one quantum at its end (rightward)
2. Planet deposits one quantum at its end (leftward)
3. Where they meet: Same consumes Different
4. The boundary position shifts based on net deposit balance
5. Track: boundary position over time (= "distance")

**This tests:** Does the consumption equilibrium work in 1D? Does the
boundary oscillate? What sets the equilibrium position?

### Phase 1: Branching — 2D/3D Connector Network

Extend from 1D to a small graph (100-500 nodes). Still no entity hopping.
Entities are regions of deposit dominance. Deposits propagate outward from
each entity's core. Where they meet: consumption dynamics.

**This tests:** Does the equilibrium generalize from 1D to networks? Do
the three-way partition ratios (store/move/radiate) emerge from geometry?

### Phase 2: Orbital Motion from Pattern Shift

On a larger graph, test whether the deposit-pattern boundary between star
and planet traces an orbit. The star pattern is centered. The planet pattern
is off-center. The boundary between them should oscillate (radial binding)
and potentially rotate (orbital motion) based on the asymmetry of deposit
arrival rates from different directions.

**This tests:** Does the deposit-statistics model produce orbital motion
without entity hopping?

### Phase 3: Growing Graph

Start with a minimal graph (just the star cluster). Let propagating deposits
create new connectors at the frontier (Unknown nodes). The universe expands
as the star's radiation reaches new territory. Introduce planet deposits
after the star field has propagated. Watch the planet pattern emerge from
the star's reject stream.

**This tests:** Does the hierarchy (star → planet → moon) emerge naturally
from the deposit dynamics on a growing graph?

---

## Key Differences from Experiment 118

| Aspect | Exp 118 (v4-v17) | Exp 128 |
|--------|------------------|---------|
| Entity | Object at a graph node | Deposit pattern on a region of connectors |
| Movement | Entity hops between nodes | Pattern boundary shifts from deposit statistics |
| Position | Which node the entity is at | Statistical center of deposit distribution |
| Graph | Pre-built, fixed topology | Grows from deposit propagation (Phase 3) |
| Orbit | Entity traces a path through graph | Boundary between patterns oscillates/rotates |
| Speed | Hops per tick (limited by charging) | Rate of boundary shift (limited by deposit rate) |
| Gravity | Routing toward rich deposit field | Consumption of Different at the boundary |

---

## Parameters (Phase 0)

| Parameter | Value | Meaning |
|-----------|-------|---------|
| CHAIN_LENGTH | 100 | Initial connectors in the 1D chain |
| STAR_RATE | 1 | Star deposits per tick |
| PLANET_RATE | 1 | Planet deposits per tick |
| INITIAL_BOUNDARY | 50 | Starting boundary position (middle) |

No BASE_WEIGHT, no CHARGING_TIME, no graph construction.
The ONLY dynamics are: deposit, consume, shift boundary.

---

## What Success Looks Like

### Phase 0:
- Boundary oscillates around an equilibrium position
- Equilibrium position depends on deposit rate ratio
- Consumption rate matches production rate at equilibrium

### Phase 1:
- Store/move/radiate ratios emerge from geometry
- Equilibrium distances form on the network
- The three-way partition matches RAW 128 predictions

### Phase 2:
- The planet's deposit pattern boundary traces an orbit
- The orbit has angular coherence > 0.3 (real rotation, not random walk)
- Orbital velocity depends on distance from star pattern center
- The orbit is a PATTERN phenomenon, not an object phenomenon

### Phase 3:
- The graph grows from the star's radiation
- The planet pattern EMERGES from the star's reject stream
- The hierarchy forms naturally: star → planet → (moon?)

---

## Connection to Theory

RAW 128 describes the energy partition at the quantum level. Experiment 128
tests whether this partition, applied to deposit patterns on a graph, produces
orbital mechanics.

RAW 113 describes Same/Different/Unknown. The entity boundary IS the
Same/Different boundary on the connector network. The frontier (Unknown) is
where the graph grows.

RAW 118 describes gravity as consumption and transformation. The gravitational
binding IS the consumption equilibrium at the entity boundary — Same deposits
consume Different, maintaining the distance.

The trie_stream_filtering experiments (v4-v10) showed that hierarchical
structure self-organizes from stream filtering. Experiment 128 Phase 3 tests
whether the SAME mechanism produces gravitational hierarchy (star → planet →
moon) when applied to deposit patterns on a growing graph.

---

## Results

### Phase 0: 1D Chain (April 3, 2026)
- Boundary stable at midpoint for equal rates. Consumption balances production.
- Unequal rates: stronger entity dominates entire chain (binary, no intermediate).
- 1D has no geometric dilution — no equilibrium possible with unequal rates.

### Phase 1: Deposit Patterns on Graph (April 3, 2026)
- **Boundary FORMS from geometric dilution.** Star dominance falls with distance.
- 80 star sources push boundary to hop d=3. 10 sources only d=1.
- **Mass = node count confirmed.** More sources = wider dominance.
- Consumption active at the boundary (405k consumed in 5k ticks).
- The deposit-pattern model produces real gravitational field structure.

### Phase 2: Boundary Dynamics (April 3, 2026)
- Test D (self-tracking): planet COM drifts toward star — gravitational
  attraction as pure pattern drift. No entity hopping.
- **Test F (tangential momentum + gravity): COHERENCE 0.438 — first EVER
  above the 0.3 threshold.** The planet deposit pattern traces a coherent
  arc around the star. Net angle 194 degrees. Clear curved trajectory.
- The deposit-statistics model produces COHERENT ORBITAL MOTION for the
  first time in the entire experiment line (118 + 128).
- **Test G (ellipse attempt, 50k ticks): COHERENCE 0.478.** Gravity from
  actual deposit density gradient (no fixed constant). Planet spirals in
  from r=10 to equilibrium at r~4.8, damped oscillation 3.5-6.4. Net angle
  only 7 degrees — the planet settles at equilibrium rather than orbiting.
  The gravity/momentum balance needs to be derived from deposit dynamics,
  not hand-tuned (grav * 0.01 was too weak for closed orbit, too strong
  for escape).

### Key: what made coherence > 0.3 finally work
1. Entities are patterns (deposit COM), not objects hopping on graph nodes
2. Momentum = persistence of COM-shift direction (pattern inertia)
3. Gravity = deflection toward star center (from deposit field)
4. The pattern moves smoothly through the graph — no discrete graph-topology
   randomness from node-to-node routing decisions

### What's needed for closed elliptical orbits
The gravity/momentum balance must emerge from the deposit field itself,
not from hand-tuned scaling constants. The deposit density gradient IS
the gravitational field. The pattern-shift persistence IS momentum. The
orbit should close when these two are in natural balance — when the
centripetal acceleration from the density gradient equals v^2/r from the
pattern drift velocity. This balance exists (Test F produced a coherent
arc) but finding the self-consistent scaling remains open.

### v3: Simultaneous star+planet, 500k graph, 5 planet nodes (April 3-5)
- Star and planet from tick 0 (no warmup — the interaction defines both)
- Star equilibrated at r=45.9 (56% of R=80, better than 73% at N=80)
- Planet (5 nodes): wild oscillation dist 2.8-52.9. Probability cloud.
- Ejection event at t=890k-970k: planet launched from dist=3.4 to dist=53
  by the star's internal deposit traffic (CME-like event)
- Planet returned (dist=27 at t=1M) — binding survived the ejection
- Consumption: 70k consumed, mechanism active
- Key insight: the star needs the planet to define its own edge. Without
  the Different entity, the star has no boundary (v2 showed unbounded
  expansion during star-only warmup)

### v4/v5: 500 planet nodes, vectorized substrate (April 5-6)
- v4: object-based (14 t/s). v5: numpy vectorized (535 t/s). 38x speedup.
- Same physics, verified: both produce identical trajectories
- Planet diffused from r=6 to r=57 (same diffusion problem as the star)
- Planet COM fell to dist=4.3 and stabilized (no oscillation, no ejection)
- 0.5 oscillations — planet fell in once and stayed. Merged with star.
- Planet node cohesion problem: unsolvable with pre-placed nodes. Planet
  must EMERGE from reject stream (Phase 3 prerequisite).

### v6: Deposit dominance tracking (April 6)
- **The breakthrough measurement.** Track WHERE each family's deposits
  dominate on connectors, not where entity nodes are.
- Node-based: planet merged at dist=4.6 (looks like absorption)
- Deposit-based: planet region at dist=12.2 (distinct territory!)
- Star deposit region r=35.6 (smaller than node cloud r=41.4)
- Planet territory: 360k edges (vs star's 4.9M). Real but small.
- Deposit distance stabilized at 12.2 for 200k+ ticks — REAL equilibrium
- Dominance gradient: 100% star at d=0-9, transition at d=10-15, planet
  presence at d=15-19
- Tangential: near zero (8 deg total). Purely radial equilibrium. No
  asymmetry in the deposit dynamics to generate sideways motion.

### v7: Tangential reject stream as velocity (April 6)
- Planet routing biased tangentially (perpendicular to gravity direction).
- 500k run: coherence 0.867, net -26.5 degrees. Consistent direction.
- **7M full revolution run: tangential motion DIED after 500k ticks.**
  The -25 degrees happened during the infall phase only. Once equilibrium
  was reached, zero further rotation. The tangential bias only curves
  EXISTING motion. When radial motion stops, there's nothing to curve.

### v8: Tangential reject stream as acceleration (April 6)
- Gravity and tangential as ACCELERATION (bend forward direction each tick).
- Result: noisy oscillation, big swings (+-15 deg/step), random direction.
  Coherence 0.333. The bending flips direction from per-tick deposit noise.
- Deposit distance collapsed to 7.5 (planet consumed by star).

### The tangential motion problem (v7+v8)

The planet's production is ISOTROPIC — deposits go in all directions
equally. Consumption is directional (from star-facing side, shortening
those connectors). Production lengthens connectors in all directions.
The only asymmetry is radial. No tangential production = no rotation.

**The orbit requires a BENT PIPE**: intake from star side, output 90
degrees tangentially. The bent pipe requires internal planet structure
that redirects the processing stream. Without it, the planet can only
approach/retreat radially, never orbit.

The bent pipe requires **Phase 3**: emergent internal hierarchy from
consumption dynamics. Pre-placed nodes diffuse before structure forms.

## Experiment 128 Summary (v1-v8, April 3-6, 2026)

### What's proven:
1. **Radial equilibrium from production/consumption balance** (v6: deposit
   distance 12.2, stable 200k+ ticks). This IS gravitational binding.
2. **Deposit dominance regions are the correct entity measurement** (v6:
   node positions show merger at dist=4.6, deposit regions show distinct
   territories at dist=12.2).
3. **Mass = source count** (Phase 1: more sources = wider dominance).
4. **Consumption mechanics work** (all versions: Same reclassifies
   Different, connectors can shrink).
5. **The star needs the planet to define its edge** (v2 vs v3).
6. **Vectorization: 38x speedup** (v5: 535 t/s).
7. **Phase 2 hand-coded momentum produces coherent arcs** (0.438/0.478
   coherence) but this is not emergent — it's Newtonian integration
   dressed as deposit dynamics.

### What's not solved:
1. **Sustained tangential motion** — v7 tangential bias produces one-time
   25-degree deflection during infall, then decays to zero. v8 acceleration
   model produces noisy oscillation. Neither sustains rotation.
2. **Planet self-binding** — 500 nodes diffuse instantly. No internal
   structure possible with pre-placed nodes.
3. **The bent pipe** — planet needs internal structure to redirect
   production tangentially. This is the Phase 3 problem.

### The core finding:
**Radial binding is solved. Tangential motion requires internal structure.**

The consumption mechanism (Same eats Different, connectors shrink/grow)
produces stable radial equilibrium between deposit dominance regions.
This IS gravity in the deposit-statistics model.

But orbital motion requires the planet to have ASYMMETRIC production:
intake radial (from star), output tangential (perpendicular). This
asymmetry can only come from internal processing hierarchy — a layered
structure where the flow through the planet is redirected. Without
internal structure, the planet's production is isotropic, and the only
dynamics are radial (approach/retreat).

### v9 ODE: Abstracted Consumption Equations (April 6)
- Stripped the graph away. Pure ODE: F = -consumed/r².
- **Perfect Keplerian orbits** (35-1812 revolutions). T² ∝ r³.
- Tangential thrust (excess or redirect) always causes escape.
- **"It rotates because it consumes."** Consumption IS the centripetal
  force. Documented as RAW 130.
- **Critical caveat:** F = -consumed/r² assumes 3D geometric dilution.
  The 1/r² was assumed, not derived from graph dynamics. The ODE
  relabels GM as L×R/4π — a reinterpretation, not a derivation.

### v10: Consumption IS Movement (April 6)
- Entity consumes, and that IS its movement. Each consumed deposit
  shifts the pattern center by the deposit's direction. The consumption
  IS the tick (RAW 028 temporal surfing).
- Graph attempt: star deposits don't reach r=40 (local field problem).
- **Minimal orbit**: fake star, geometric flux, 10% resistance.
  Perfect circular orbit at v_circ. Elliptical at sub-circular.
  82 revolutions. Keplerian dynamics from consumption force.
- **Honest assessment:** uses flux = L/(4πr²) = Newton renamed.
  The gap between graph dynamics and 1/r² force remains open.

## Experiment 128 Final Summary (v1-v10, April 3-6, 2026)

### What's proven:
1. Radial equilibrium from production/consumption balance (v6)
2. Deposit dominance regions are the correct entity measurement (v6)
3. Mass = source count (Phase 1)
4. Consumption mechanics work (all versions)
5. Consumption IS centripetal force → Keplerian orbits (v9 ODE, v10 minimal)
6. Tangential thrust destabilizes orbits — excess leaves system (v9 ODE)
7. Angular momentum is INHERITED, not generated (RAW 130)

### What's not proven:
1. That graph dynamics produce 1/r² force law (the remaining gap)
2. Emergent planet formation from reject stream (Phase 3)
3. Internal planet structure producing directed processing (bent pipe)

### The remaining gap:
Graph experiments → deposits dilute with distance (geometric spreading)
ODE → consumption force with 1/r² produces orbits
**NOT connected:** graph deposit dilution → measurable 1/r² force → orbit

This may be a mathematical theorem (geometric dilution on 3D RGG → 1/r²
in the large-N limit), not a simulation problem.

### Key theoretical contributions:
- **RAW 130:** "It rotates because it consumes"
- **RAW 129:** Experimental connections (Breit-Wheeler, quantum battery,
  CME, planetary structure, quantum-classical transition)
- **RAW 128 v2:** Three-way partition (store/move/radiate)

### Path forward:
1. **Mathematical proof:** Show 1/r² force from geometric dilution on graphs
2. **Phase 3:** Emergent planet from star's reject stream
3. **GPU scale** (causal-cone-engine) for emergent internal structure
4. **Analytical orbital mechanics** from consumption equations

---

*The entity consumes. The consumption IS the movement.*
*The orbit is maintained by consumption — stop consuming, fly off straight.*
*The force law comes from geometry. The force constant comes from physics.*
*GM = star_emission × planet_resistance / 4π.*
*Six days, 25+ versions, two experiments, one sentence: it rotates because it consumes.*
