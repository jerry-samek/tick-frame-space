# Experiment 118 v9: Three-Way Partition (Store / Move / Radiate)

## Status: READY FOR IMPLEMENTATION
## Date: April 1, 2026
## Author: Tom (theory — RAW 128 v2), Claude (spec)

---

## What v8 Got Right and What It Missed

v8 achieved the first emergent orbit — a planet orbiting a star WITHOUT a seeded
tangential kick (1869 total degrees, 9.5 radial oscillations over 200k ticks).
The planet was properly placed outside the star body (initial distance 19.6, star
radius 17.5).

**What v8 missed:** The store/move partition barely engaged. Total absorbed = 0.
In-flight quanta at steady state = 4. The forward-momentum wake predicted by
RAW 128 was essentially absent. The tangential motion came from graph-topology
asymmetry in the routing, not from the capacitor-availability mechanism.

**Why:** v8's deposit-on-arrival (from v7) places the deposit directly on the
arrival connector, bypassing the store/move check at the destination node. The
discharge quantum never actually PROPAGATES to the next node for evaluation —
it's stored immediately as part of the connector. The in-flight quanta system
was bolted on top of a mechanism that already stored everything.

**The fix for v9:** The deposit-on-arrival mechanic must be REPLACED, not
augmented. When a node arrives at its destination (traversal complete), its
capacitor fires. The discharged quantum does NOT deposit on the arrival
connector. Instead, it PROPAGATES to the next node, where its fate is
determined by the local environment:

1. **STORE** — next node's capacitor is idle → quantum absorbed, deposited on
   the connector between the two nodes. Connector grows. Mass increases.
2. **MOVE** — next node's capacitor is busy, forward path available → quantum
   continues forward. Deposits on the traversed connector. Momentum wake.
3. **RADIATE** — next node's capacitor is busy, forward path saturated or
   unavailable → quantum goes sideways/outward. Deposits on that connector.
   Energy leaves the entity's neighborhood.

ALL three outcomes deposit on a connector. The connector model (length = deposits)
is preserved. The difference is WHERE the deposit ends up: locally (store), ahead
(move), or sideways (radiate).

---

## The Core Change from v8

### v8 tick sequence (broken)

```
Node arrives at destination
  -> deposit on arrival connector (ALWAYS — bypasses partition)
  -> create DischargeEvent
  -> check destination node: idle? -> absorbed (redundant, deposit already placed)
                             busy? -> in-flight quantum (but deposit already placed)
```

The deposit-on-arrival makes the partition meaningless. The connector already grew.

### v9 tick sequence (fixed)

```
Node arrives at destination
  -> capacitor fires
  -> quantum PROPAGATES to next node (via a chosen outgoing connector)
  -> at next node: check capacitor availability
     -> IDLE: quantum absorbed on THAT connector (store)
     -> BUSY, forward available: quantum continues forward (move)
     -> BUSY, no forward: quantum goes sideways (radiate)
```

The key difference: **the deposit happens at the RECEIVING end, not the SENDING
end.** The quantum must reach a node with an idle capacitor before it becomes a
deposit. Until then, it propagates and deposits on every connector it traverses
(creating the wake).

### What "capacitor fires" means in v9

When a node completes a traversal (transit_remaining reaches 0):
1. The node arrives at the destination graph position
2. Its capacitor fires — it produces one quantum of its group tag
3. The quantum goes onto ONE outgoing connector (chosen by routing)
4. The quantum propagates at 1 hop/tick
5. At each node encountered:
   - Entity node, idle, hasn't fired this tick → ABSORBED (store)
   - Entity node, busy or already fired → CONTINUES
   - Non-entity node → CONTINUES
6. The quantum deposits on every connector it traverses

The node itself does NOT deposit on its arrival connector. The deposit comes
from the quantum's propagation path. If the quantum is immediately absorbed
by an idle neighbor (store), the deposit is on the connector between the
arrival node and that neighbor. If the quantum continues (move/radiate), the
deposits are on connectors further along its path.

### Routing still reads accumulated deposits

The routing signal is unchanged from v7/v8: absolute matching count per
connector + BASE_WEIGHT. The deposits from the three-way partition all end
up on connectors — they're just placed at different locations depending on
the outcome. The forward wake (move deposits ahead of the entity) biases
routing forward. The star's accumulated deposits (from star nodes' historical
traversals) provide the gravitational signal.

---

## Classifying Move vs Radiate

When a quantum continues (not absorbed), it takes an outgoing connector.
Which outcome it represents depends on the DIRECTION relative to the
entity's travel:

```python
# Entity arrived from direction A -> B
# Quantum goes from B to C
# Compute alignment:
travel_dir = normalize(pos[B] - pos[A])  # entity's travel direction
quantum_dir = normalize(pos[C] - pos[B])  # quantum's outgoing direction
alignment = dot(travel_dir, quantum_dir)

if alignment > 0.3:    # roughly forward (within ~70 degrees)
    outcome = MOVE      # momentum
elif alignment < -0.3:  # roughly backward
    outcome = BACKWARD  # this shouldn't happen if quantum uses forward-continuation
else:
    outcome = RADIATE   # sideways — energy leaves
```

The threshold 0.3 is not a parameter — it's a classification for measurement.
The quantum's path is determined by the forward-continuation table (graph
geometry), not by this classification. The classification just tells us what
happened after the fact.

---

## The Three-Way Energy Budget

At each tick, the total discharged quanta partition into:

```
discharged = stored + moved + radiated
```

At orbital equilibrium (stable orbit):
- **stored ≈ 0** — no net mass growth (connector growth rate stabilizes)
- **moved ≈ 0** — no net acceleration (velocity fluctuates around mean)
- **radiated ≈ discharged** — planet re-emits everything it processes

This IS thermal equilibrium. The planet's "temperature" is its radiation
rate. The equilibrium distance is where the star's incoming flux equals
the planet's radiation rate.

### Measuring the partition

For each discharged quantum, track:
1. Was it absorbed at the first node? → **STORE**
2. Did it propagate forward (alignment > 0.3) before absorption/expiry? → **MOVE**
3. Did it propagate sideways (|alignment| < 0.3) or outward (alignment < -0.3)? → **RADIATE**

Aggregate per measurement interval. The partition ratio as a function of
planet-star distance is the key prediction from RAW 128 v2:

| Distance | Store | Move | Radiate | Physical meaning |
|----------|-------|------|---------|------------------|
| Near star (perihelion) | Low | High | High | All busy → momentum + radiation |
| Equilibrium distance | Low | Low | High | Balanced → thermal emission |
| Far from star (aphelion) | High | Low | Low | All idle → mass growth |

---

## Implementation

### Files

```
v9/
+-- README.md              (this file)
+-- graph.py               (from v7/v8, unchanged)
+-- entity.py              (modified: no deposit-on-arrival, quantum emission)
+-- propagation.py          (from v8, enhanced: track move/radiate classification)
+-- phase1_star.py          (star equilibrium with three-way partition)
+-- phase2_orbit.py         (THE TEST: orbit + partition measurement)
+-- results/
```

### Key changes from v8

**entity.py:**
- Remove deposit-on-arrival from transit completion
- On arrival: capacitor fires → create QuantumEmission event (group, source_node,
  dest_node, chosen_outgoing_connector)
- The routing decision at arrival chooses which outgoing connector the quantum
  goes to (same absolute-count routing as v7/v8)
- The node does NOT deposit on any connector directly. All deposits come from
  quantum propagation.

**propagation.py:**
- InFlightQuantum gains a `classification` field (STORE/MOVE/RADIATE)
- Classification determined on first hop by alignment with the emitting
  entity's travel direction
- Track totals: total_stored, total_moved, total_radiated
- Remove max_age expiry (or increase substantially) — quanta should propagate
  until absorbed or until they exit the graph's entity-occupied region

### Tick loop

```python
for tick in range(1, TICKS + 1):
    # Phase 1: entity nodes tick (transit countdown or routing decision)
    emissions = []
    for entity in [star, planet]:
        for en in entity.entity_nodes:
            emission = en.tick(graph, rng)
            if emission:
                emissions.append(emission)

    # Phase 2: process emissions — each quantum propagates to its first node
    idle_set = star.idle_node_set() | planet.idle_node_set()
    for em in emissions:
        # The quantum goes onto the chosen outgoing connector from the arrival node
        first_node = em.dest_node  # node at the other end of the chosen connector
        edge_key = em.edge_key     # the connector the quantum traverses

        if first_node in idle_set:
            # STORED: absorbed immediately. Deposit on the connector.
            graph.connectors[edge_key].append(em.group)
            idle_set.discard(first_node)
            field.total_stored += 1
        else:
            # CONTINUES: becomes in-flight quantum
            # Classify based on alignment with entity's travel direction
            field.add(em.group, first_node, em.src_node, em.travel_dir)
            # Also deposit on the first connector (quantum marks its path)
            graph.connectors[edge_key].append(em.group)

    # Phase 3: propagate existing in-flight quanta
    field.tick(idle_set)
```

### What deposits WHERE

Every quantum deposits on EVERY connector it traverses. This is append-only
and consistent with the connector-as-deposits ontology.

- **Stored quantum:** deposits on 1 connector (the one between emitter and absorber)
- **Moving quantum:** deposits on N connectors (every hop of its forward path)
- **Radiated quantum:** deposits on N connectors (every hop of its sideways path)

The forward-wake deposits (from MOVE quanta) are concentrated along the
entity's travel direction. The radiation deposits are spread sideways.
The stored deposits are local. This spatial pattern IS the momentum/gravity/
radiation field structure.

---

## Phases

### Phase 1: Star Equilibrium + Partition Measurement

80 star nodes, 4 groups, 100k ticks. Same as v7/v8 Phase 1 but now
measuring the three-way partition.

**New measurements:**
- store/move/radiate counts per measurement interval
- Partition ratio vs time (does it stabilize?)
- In-flight quanta count over time
- Mean quantum lifetime before absorption

**Expected:** Star interior is dense (all busy) → high move + radiate
fraction. Star boundary is mixed. The three-way ratio should correlate
with position within the star.

### Phase 2: Planet Orbit + Energy Budget (THE TEST)

Planet WITHOUT seeded kick, same as v8 Phase 2. But now with:

1. **Three-way partition tracked at planet nodes** — store/move/radiate
   counts per interval as function of planet-star distance
2. **Energy budget:** star flux arriving at planet (from star deposits on
   planet-facing connectors) vs planet radiation (radiated quanta from
   planet nodes)
3. **Does the partition ratio change with distance as RAW 128 predicts?**
   Near star: more move + radiate. Far from star: more store.
4. **Does radiation provide orbital stability?** Compare orbit eccentricity
   and drift with v8 (which had no radiation mechanism).

**Success criteria:**
1. Planet orbits without kick (as in v8, but now with mechanism engaged)
2. Store/move/radiate ratio varies with distance from star
3. At steady-state orbit: store ≈ 0, move ≈ 0, radiate ≈ discharged
4. In-flight quanta count reaches steady state (not unlimited growth)
5. Forward wake is detectable: more matching deposits on forward connectors
   than perpendicular connectors at the planet's position

---

## Parameters

Same as v7/v8:

| Parameter | Value |
|-----------|-------|
| N_NODES | 5000 |
| TARGET_K | 24 |
| STAR_COUNT | 80 |
| PLANET_COUNT | 5 |
| BASE_WEIGHT | 1.0 |

**No new parameters.** The three-way partition is fully determined by local
capacitor availability and graph topology.

---

## What's New vs v8

| Aspect | v8 | v9 |
|--------|----|----|
| On arrival | Deposit on connector + emit quantum | Emit quantum only (no direct deposit) |
| Quantum fate | Store or move (2 outcomes) | Store, move, or radiate (3 outcomes) |
| Where deposit lands | Always on arrival connector | On whichever connector the quantum traverses |
| Forward wake | ~4 quanta (barely engaged) | Should be significant (all deposits go through quanta) |
| Radiation | Not tracked | Tracked and measured as energy outlet |
| Energy budget | Not measured | Measured: flux in vs radiation out |
| Orbital stability | No mechanism | Radiation provides negative feedback |

---

## Traps to Avoid

### Trap 20: Deposit-on-Arrival Leak
v9 MUST NOT deposit on the arrival connector. All deposits come from quantum
propagation. If a node deposits on arrival AND emits a quantum, it double-
deposits (one direct, one via quantum). The partition is meaningless if
deposits happen outside it.

### Trap 21: Quantum Buildup Without Limit
Without max_age, long-lived quanta accumulate forever. But with radiation
(sideways quanta eventually leave the entity's neighborhood), quanta that
enter sparse regions should be absorbed quickly (idle capacitors). Monitor
the in-flight count — it should plateau, not grow linearly.

### Trap 22: No Deposits at All
If the partition mechanism fails to produce ANY deposits (all quanta expire
without depositing), the connectors stop growing, traversal times freeze,
and the model reverts to v4's weak-signal behavior. Check: total deposits
should grow at ~80 per tick (one quantum per star node per routing decision).

---

*RAW 128 v2: Store, move, or radiate. One quantum, three outcomes.*
*v9 tests: does the three-way partition produce orbital stability?*
*Does the partition ratio change with distance as predicted?*
*Does radiation provide the energy outlet for stable orbits?*
