# Experiment 118 v8: Store-or-Move Energy Partition

## Status: READY FOR IMPLEMENTATION
## Date: April 1, 2026
## Author: Tom (theory — RAW 128), Claude (spec)

---

## What v7 Achieved and What's Missing

v7 produced the first orbital motion on graph substrate: gravitational binding
via time well (traversal time proportional to connector length), radial
oscillation, and sustained 3D orbits when tangential velocity was manually
seeded.

**What's missing:** v7 has no momentum. Each routing decision is independent —
no memory of travel direction. Orbital motion requires a seeded tangential
kick. The mechanism preserves angular momentum but doesn't generate it.

RAW 128 identifies the missing mechanism: **the energy partition**.

---

## The Core Mechanism: Store or Move

### The single rule (RAW 128)

When an entity node's capacitor discharges, one quantum propagates to the
next node. At that node:

- **Next node's capacitor IDLE** -> quantum absorbed -> **STORED** (connector
  grows, mass increases, entity slows)
- **Next node's capacitor BUSY** -> quantum can't be absorbed -> **CONTINUES**
  propagating forward through the graph (momentum)

**There is no choice.** The local capacitor availability determines the outcome.

### What "idle" and "busy" mean

A node's capacitor is **busy** if:
- The node is an entity node currently IN_TRANSIT (traversing a connector,
  capacitor occupied with the traversal)
- The node is an entity node currently IDLE but processing a deposit this tick
  (one discharge per tick limit)

A node's capacitor is **idle** if:
- The node is an entity node in IDLE state that hasn't processed anything yet
  this tick
- The node is an unclaimed node (no entity capacitor at all)

**Wait — unclaimed nodes.** RAW 128 says unclaimed space has idle capacitors
that absorb everything (sparse region -> all stored). But an unclaimed node
has no entity capacitor. What does "absorption" mean for an unclaimed node?

**Resolution:** An unclaimed node is NOT idle — it has NO capacitor. A quantum
arriving at an unclaimed node cannot be absorbed (nothing to absorb it) and
cannot be processed. It **continues forward**. Only entity nodes have
capacitors. Only entity capacitors can absorb.

This means: in empty space (no entities), quanta propagate freely at c = 1
hop/tick. They only stop when they reach an entity node with an idle capacitor.
This is physically correct: photons travel through vacuum until they hit matter.

### Corrected rule for unclaimed nodes

| Receiving node | Capacitor state | Outcome |
|---------------|----------------|---------|
| Entity node, IDLE, not yet fired this tick | Idle | **STORED** — absorbed, connector grows |
| Entity node, IDLE, already fired this tick | Busy | **CONTINUES** — propagates forward |
| Entity node, IN_TRANSIT | Busy | **CONTINUES** — propagates forward |
| Unclaimed node (no entity) | No capacitor | **CONTINUES** — propagates forward |

### What happens to continuing quanta

A quantum that continues:
1. Follows the forward-continuation path (most aligned outgoing connector
   from the arrival direction, using graph embedding geometry)
2. **Deposits on the connector it traverses** — the quantum IS a deposit,
   append-only, it marks every connector it passes through
3. At the next node, the same check: idle entity capacitor? absorbed. Else
   continues.
4. The quantum propagates at 1 hop per tick (c = speed of light)

**Critical: continuing quanta DEPOSIT on connectors.** This is what creates
the momentum wake. An entity's unabsorbed discharges propagate forward,
depositing the entity's group tag on connectors ahead of it. When the entity
arrives at those connectors later, it reads its own forward deposits and
routes toward them. This IS momentum — not as a parameter, but as deposits
in the graph.

---

## How This Produces Orbits

### Near the star (perihelion)

All star nodes are busy (in transit or just fired). Planet discharges arrive
at star nodes -> busy -> continue forward. The planet's discharges propagate
THROUGH the star and deposit on connectors beyond. At perihelion, the planet's
forward wake (its own deposits beyond the star) competes with the star's
gravitational pull. Forward deposits win -> planet swings through.

### Far from star (aphelion)

The planet's discharges propagate outward through empty space (unclaimed
nodes, no capacitors). They continue until they hit... what? In a finite
graph, they eventually return or reach the boundary. If the graph is large
enough, the planet's discharges spread and dilute. No concentrated forward
wake. Routing dominated by the star's gravitational signal (behind the
planet). Planet decelerates, falls back.

**Wait — unclaimed nodes have no capacitor, so quanta continue through them.
This means quanta propagate through ALL of empty space at c. They deposit on
every connector they pass, creating a trail. Eventually every connector in
the graph has deposits from the planet. This IS the v6 saturation problem.**

**The key difference from v6:** In v6, deposits accumulated uniformly because
the ENTITY deposited everywhere via random walk. In v8, the entity deposits
locally (one connector per arrival). The UNABSORBED QUANTA deposit along their
forward path. The forward path is directional (forward-continuation), not
random. So the deposits accumulate along BEAMS from the entity, not uniformly.

The momentum wake is a beam, not a cloud. It's strong along the forward
direction and absent perpendicular to it. This creates directional bias
without uniform saturation.

### The orbit cycle

```
Aphelion: discharges propagate through empty space, spread, dilute.
  No concentrated wake. Star signal dominates. Planet falls inward.
    |
Falling: approaching star. Discharges hit star boundary nodes.
  Some idle star nodes absorb (store). Some busy nodes reject (continue).
  Partial forward wake builds. Increasing velocity.
    |
Perihelion: star core. All busy. All discharges continue through.
  Maximum forward wake. Maximum velocity. Planet swings past.
    |
Climbing: leaving star. Discharges propagate outward.
  Hit idle boundary nodes -> absorbed. Wake dissipates.
  Star signal behind -> deceleration. Planet slows.
    |
Aphelion: dead stop. Star signal pulls back. Cycle repeats.
```

---

## Implementation

### Architecture

Three types of objects in the simulation:

1. **Entity nodes** — have capacitors, make routing decisions, discharge quanta
2. **Connectors** — chains of deposits, length = initial + deposit count
3. **In-flight quanta** — unabsorbed discharges propagating through the graph

v7 had only (1) and (2). v8 adds (3).

### In-flight quantum

```python
class InFlightQuantum:
    """A discharged quantum propagating through the graph."""

    def __init__(self, group, node, from_edge):
        self.group = group         # deposit tag (s0, p1, etc.)
        self.node = node           # current node position
        self.from_edge = from_edge # edge it arrived on (for forward-continuation)

    def tick(self, graph, entity_idle_set, forward_redirect):
        """Propagate one hop. Returns True if absorbed, False if continues."""
        # Check: is current node an idle entity capacitor?
        if self.node in entity_idle_set:
            # ABSORBED — store
            return True

        # CONTINUES — find forward connector, deposit, move
        out_edge = forward_redirect[self.from_edge]
        graph.connectors[out_edge].append(self.group)  # deposit on connector
        next_node = ... # destination of out_edge
        self.node = next_node
        self.from_edge = out_edge
        return False
```

### Modified entity tick

```python
def tick(self, graph, rng):
    if self.in_transit:
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            # ARRIVED: capacitor fires, discharge one quantum
            # The quantum goes to the destination node
            # -> check if next node is idle -> store or create in-flight
            self.node = self.transit_dest
            self.in_transit = False
            self.capacitor_fired_this_tick = True

            # Create the discharged quantum
            return DischargeEvent(self.group, self.transit_edge, self.transit_dest)
        return None

    # IDLE: make routing decision
    # Read local deposits INCLUDING forward wake (in-flight quanta ahead)
    ...
    # Begin traversal
    ...
```

### Tick loop

```python
for tick in range(1, TICKS + 1):
    # Phase 1: Entity nodes tick (transit or route)
    #   - Nodes in transit: decrement timer, arrive if done
    #   - Arriving nodes: discharge quantum -> create DischargeEvent
    #   - Idle nodes: read deposits, choose direction, begin traversal
    discharge_events = []
    for entity in [star, planet]:
        for en in entity.entity_nodes:
            event = en.tick(graph, rng)
            if event:
                discharge_events.append(event)

    # Phase 2: Process discharge events
    #   Each discharged quantum checks the destination node
    new_in_flight = []
    idle_entity_nodes = get_idle_entity_nodes(star, planet)
    for event in discharge_events:
        if event.dest_node in idle_entity_nodes:
            # STORED: deposit on connector, node absorbs
            graph.connectors[event.edge].append(event.group)
            idle_entity_nodes.discard(event.dest_node)  # now busy
        else:
            # CONTINUES: becomes in-flight quantum
            q = InFlightQuantum(event.group, event.dest_node, event.edge)
            new_in_flight.append(q)

    # Phase 3: Propagate existing in-flight quanta
    surviving = []
    for q in in_flight_quanta:
        absorbed = q.tick(graph, idle_entity_nodes, forward_redirect)
        if absorbed:
            idle_entity_nodes.discard(q.node)  # absorbed -> now busy
        else:
            surviving.append(q)

    in_flight_quanta = surviving + new_in_flight
```

### Forward redirect table

Same as v5's forward propagation: precomputed at construction. For each
directed edge d (A->B), find the outgoing edge from B most aligned with
the direction A->B using graph embedding geometry.

```python
forward_redirect[d] = argmax(dot(dir_AB, dir_BC)) for all outgoing edges B->C
```

Precomputed once. Deterministic. No randomness in propagation.

### Entity routing — reads forward wake

The entity's routing signal now includes deposits from in-flight quanta
that passed through nearby connectors. These appear as regular deposits
on the connectors (because in-flight quanta deposit on every connector
they traverse). No special treatment needed — the routing reads total
deposits per connector, which includes wake deposits.

The routing is the same as v7: absolute matching count + BASE_WEIGHT.
The wake deposits naturally bias the forward direction.

---

## Phases

### Phase 0: Store/Move Validation

Simple test: one entity node, one discharge, check that:
- Discharge at idle entity neighbor -> absorbed (connector grows)
- Discharge at busy entity neighbor -> in-flight quantum created
- In-flight quantum propagates at 1 hop/tick
- In-flight quantum deposits on each traversed connector
- In-flight quantum absorbed when it reaches idle entity node

### Phase 1: Star Equilibrium

Same as v7: 80 star nodes, 4 groups, 100k ticks.
Additional measurements:
- Number of in-flight quanta over time
- Fraction of discharges stored vs continuing (the partition ratio)
- In-flight quantum lifetime (hops before absorption)

Expected: star core is busy -> high motion fraction. Star surface is mixed.
The partition ratio should vary with position within the star.

### Phase 2: Planet WITHOUT Seeded Kick (THE CRITICAL TEST)

Planet placed outside star (cluster placement: find one node beyond star
radius, take its 4 nearest neighbors). NO tangential kick. All planet
nodes start IDLE at their positions.

**The prediction from RAW 128:** The planet falls toward the star. As it
enters the dense star field, its discharges encounter busy capacitors
and propagate forward through the star. This creates a forward wake.
At perihelion, the wake biases routing forward. The planet swings past
instead of reversing. Tangential motion emerges from the store/move
partition without being seeded.

**If this works:** RAW 128 is validated. Momentum is derived from the
single mechanism. Orbital motion emerges from capacitor availability.

**If this fails (pure radial oscillation):** The forward wake is too
weak relative to the gravitational signal. The mechanism is correct
but the balance doesn't produce enough tangential bias. May need larger
graph or more star nodes.

### Phase 3: Comparison with v7 Phase 2b

If Phase 2 produces orbital motion, compare quantitatively with v7's
seeded-kick orbits:
- Orbital period
- Eccentricity
- Angular momentum evolution
- Store/move ratio vs distance

---

## Parameters

Same as v7:

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass |
| PLANET_COUNT | 5 | Planet mass |
| BASE_WEIGHT | 1.0 | Thermal energy |

**New derived quantities (not parameters):**
- Store/move ratio (from capacitor availability)
- In-flight quantum count (from mechanism)
- Momentum wake length (from graph topology)
- Forward-continuation table (from graph geometry)

---

## File Structure

```
v8/
+-- README.md              (this file)
+-- graph.py               (from v7, unchanged)
+-- entity.py              (modified: discharge events, capacitor state)
+-- propagation.py         (NEW: in-flight quanta, forward redirect)
+-- phase0_validation.py   (store/move basic test)
+-- phase1_star.py         (star equilibrium with partition)
+-- phase2_orbit.py        (THE TEST: planet without seeded kick)
+-- results/
```

---

## What's New vs v7

| Aspect | v7 | v8 |
|--------|----|----|
| Discharge | Deposit on arrival connector | Quantum propagates to next node |
| Next node idle | Always stores | **STORES** (absorbed) |
| Next node busy | Always stores (no check) | **CONTINUES** (in-flight quantum) |
| In-flight quanta | None | Propagate at c, deposit on traversed connectors |
| Momentum | None (requires seeded kick) | Wake of unabsorbed discharges ahead of entity |
| Tangential velocity | Must be seeded manually | **Should emerge from store/move partition** |
| Forward propagation | Not used | Precomputed forward-redirect (from v5) |

---

## Traps to Avoid

### Trap 17: Quanta Accumulation
If most discharges become in-flight quanta and never get absorbed (no idle
entity nodes in the graph), the in-flight count explodes. Mitigation: quanta
that exit the graph (reach boundary with no outgoing edges) are destroyed.
Quanta that return to an entity node eventually get absorbed. Monitor the
in-flight count — it should reach a steady state, not grow without bound.

### Trap 18: Forward Wake Saturation
If in-flight quanta deposit on every connector they traverse, they eventually
saturate the graph (same as v6). Difference: wake deposits are directional
(along beams, not uniform). But on a 9-hop-diameter graph, beams wrap around.
Monitor: is the wake concentrated or diffuse?

### Trap 19: Idle Detection Timing
The "idle" check must be done at the right moment in the tick cycle. If entity
A discharges and its quantum reaches entity B, but B hasn't ticked yet this
tick, is B "idle"? Resolution: process in phases. Phase 1: all entities tick
(discharge or route). Phase 2: process discharge events. Phase 3: propagate
in-flight. This ensures the idle/busy state is well-defined.

---

*RAW 128: One quantum, no choice, the environment decides.*
*v8 tests: does the store/move partition produce orbits without a kick?*
