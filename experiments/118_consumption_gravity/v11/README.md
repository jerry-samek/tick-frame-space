# Experiment 118 v11: Newtonian Entities — Forward Default, Deposits Deflect

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Author: Tom (theory), Claude (spec)

---

## The Lesson Chain: v7 → v10

| Version | What it proved | What it got wrong |
|---------|---------------|-------------------|
| v7 | Traversal time ∝ length creates time well, star binds | No inertia — planet random-walks in the well |
| v8 | RAW 128 partition doesn't engage (1-tick idle window) | Store = 0 across all runs |
| v9 | Same result, partition still inactive | v9 diagnostic: "orbits" are bound random walks |
| v10 | Pure reactive = deadlock. Aristotelian physics doesn't work. | Entities froze — waiting for triggers that never come |

**The v10 deadlock is the most important result.** It proved experimentally
that entities cannot be purely reactive. Motion does not require continuous
energy input. Aristotle was wrong. Newton was right.

---

## The Newton Correction

### The insight (from the session, before v10 ran):

> Energy is not directly responsible for maintaining motion. Motion is
> just a visualization artifact of the substrate state. What is changing
> is the strength of the direction vector — more like acceleration.
> Where there is no energy present, there still might be a minimal
> vector of movement. — Tom, April 2, 2026

### What this means for the model:

**Newton's First Law on the graph:**
An entity that has arrived at a node from direction D will continue in
direction D unless deflected by incoming deposits. No deposits = no
deflection = straight line on the graph.

**Newton's Second Law on the graph:**
Incoming deposits during the charging phase accumulate a deflection
vector. The deflection is toward the deposit source (gravity). The
strength is proportional to the number of deposits received and their
directional coherence.

**The entity tick cycle:**

```
ARRIVE at node (from direction D)
    ↓
CHARGE: sit idle for CHARGING_TIME ticks
    During this phase:
    - Accumulate incoming deposits on local connectors
    - Each deposit adds to a deflection vector pointing
      toward the deposit's source direction
    - The charging phase IS the RAW 128 idle window
    ↓
ROUTE: combine forward default (D) with accumulated deflection
    final_direction = D + deflection_from_deposits
    Choose the connector best aligned with final_direction
    ↓
DEPOSIT: append one quantum to the chosen connector
    ↓
TRAVERSE: travel along connector for L ticks (time ∝ length)
    ↓
ARRIVE at next node → repeat
```

### What changes from v10:

| v10 (Aristotelian) | v11 (Newtonian) |
|--------------------|-----------------|
| No trigger = frozen | No trigger = continue forward |
| Motion requires energy | Motion is default, energy changes direction |
| Deadlock on initialization | Works from tick 1 |
| Deposits CAUSE motion | Deposits DEFLECT motion |

### What stays from v7-v10:

- Connector = deposits (v4 ontology, confirmed)
- Traversal time ∝ connector length (v7 time well)
- Deposit-on-arrival, one per traversal (v7)
- Charging phase with idle window (v10 concept, now with forward default)
- Accumulated deposits on connectors for routing signal (v6/v7)

---

## The Charging Phase

### Purpose

The charging phase serves THREE functions simultaneously:

1. **Idle window for RAW 128.** The entity sits at a node for multiple
   ticks. In-flight quanta can arrive and be absorbed. This is the
   window that was 1 tick in v7-v9 (too narrow) and infinite in v10
   (deadlock). v11 sets it to a fixed CHARGING_TIME.

2. **Deflection accumulation.** During the charging phase, the entity
   monitors its local connectors. Any NEW deposits (from other entities
   hopping along nearby connectors) contribute to a deflection vector.
   More deposits from the star direction = stronger deflection toward
   the star. The deflection is the INTEGRAL of deposit arrivals over
   the charging phase.

3. **Velocity scaling with distance.** The charging time creates a
   natural velocity limit. The entity hops, traverses (L ticks), then
   sits (CHARGING_TIME ticks). Total cycle time = L + CHARGING_TIME.
   Velocity = 1 hop / (L + CHARGING_TIME) in graph units. This is
   always < c, and decreases as connectors grow (larger L).

### What CHARGING_TIME should be

**Option A: Fixed constant.** CHARGING_TIME = 50 ticks. Simple. Every
entity waits the same amount. The idle window is 50 ticks — vastly
better than 1 tick (v7-v9). But it's a free parameter.

**Option B: Proportional to connector length.** CHARGING_TIME = L (the
length of the connector just traversed). Physical meaning: the entity
"processes" its traversal experience. Long journey = more to process
= longer rest. Total cycle: L (traverse) + L (charge) = 2L.
Velocity = 1/2L. No free parameter.

**Option C: Proportional to entity mass.** CHARGING_TIME = node_count.
A 5-node planet charges for 5 ticks. An 80-node star charges for 80
ticks (per node). Physical meaning: heavier entities are more sluggish.
This is inertia — mass resists change in motion.

**Recommendation: start with Option A (fixed 50 ticks).** It's the
simplest to implement and debug. If it works, try Option B (proportional
to L) which eliminates the parameter. Option C is interesting but adds
complexity.

---

## The Routing Decision: Forward + Deflection

### Forward default

The entity arrived from node P via connector C. Its arrival direction:

```python
arrival_dir = normalize(pos[current_node] - pos[previous_node])
```

Without any deflection, the entity would choose the outgoing connector
most aligned with arrival_dir:

```python
for each neighbor N:
    out_dir = normalize(pos[N] - pos[current_node])
    forward_score = dot(arrival_dir, out_dir)
```

### Deflection from deposits

During the charging phase, the entity tracked which connectors received
new deposits and from which direction:

```python
deflection = np.zeros(3)  # accumulated deflection vector

# For each deposit that arrived during charging:
for deposit in deposits_during_charging:
    deposit_dir = normalize(pos[current_node] - pos[deposit_source])
    deflection += deposit_dir  # toward the deposit source
```

The deflection vector points TOWARD the source of deposits. If most
deposits came from the star direction, the deflection points toward the
star. This IS gravitational acceleration — a deflection toward the
mass source proportional to the flux from that direction.

### Combined routing

```python
# Combine forward (inertia) with deflection (gravity)
combined_dir = arrival_dir + deflection
combined_dir = normalize(combined_dir) if norm(combined_dir) > 0 else arrival_dir

# Score each outgoing connector
for i, nb in enumerate(neighbors):
    out_dir = normalize(pos[nb] - pos[current_node])
    
    # Alignment with combined direction
    direction_score = dot(combined_dir, out_dir)
    
    # Deposit count on connector (routing toward richer connectors)
    deposit_score = total_deposits(connector_to_nb) / max_deposits
    
    routing_weight = max(0, direction_score) + deposit_score * DEPOSIT_WEIGHT + BASE_WEIGHT
```

Note: `direction_score` can be negative (backward connectors). The
`max(0, ...)` prevents backward routing. The entity can slow down
(choose a less-forward connector) but not reverse in one hop.

### First hop (no arrival direction)

At tick 0 or after first placement, the entity has no arrival direction.
For the FIRST hop only:
- Route based on deposit counts alone (no forward default)
- Or random if no deposits exist yet

After the first hop, arrival_dir is set and forward default kicks in.

---

## Implementation

### Entity Node States

```python
class EntityNode:
    STATE_CHARGING = 0
    STATE_ROUTING = 1
    STATE_TRANSIT = 2
    
    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.state = self.STATE_CHARGING
        self.charge_ticks = 0
        self.arrival_dir = None  # None = first hop, no inertia yet
        self.arrived_from = None
        self.deflection = np.zeros(3)  # accumulated during charging
        self.deposits_received = 0  # count during charging
        self.transit_edge = None
        self.transit_remaining = 0
        self.transit_dest = None
```

### Tick Logic

```python
def tick(self, graph, all_deposits_this_tick, rng):
    
    if self.state == self.STATE_TRANSIT:
        self.transit_remaining -= 1
        if self.transit_remaining <= 0:
            # ARRIVE: deposit on traversed connector
            dest = self.transit_dest
            eid = graph.edge_id(self.node, dest)
            graph.connectors[eid].append(self.group, self.node, dest)
            
            # Set arrival direction
            self.arrival_dir = graph.pos[dest] - graph.pos[self.node]
            norm = np.linalg.norm(self.arrival_dir)
            if norm > 1e-15:
                self.arrival_dir /= norm
            
            self.arrived_from = self.node
            self.node = dest
            self.state = self.STATE_CHARGING
            self.charge_ticks = 0
            self.deflection = np.zeros(3)
            self.deposits_received = 0
        return
    
    if self.state == self.STATE_CHARGING:
        self.charge_ticks += 1
        
        # Accumulate deflection from deposits arriving this tick
        for nb in graph.neighbors(self.node):
            eid = graph.edge_id(self.node, nb)
            conn = graph.connectors[eid]
            new_deps = conn.deposits_this_tick
            if new_deps > 0 and conn.last_deposit_source != self.node:
                # Deposit came from direction of nb (or wherever the
                # depositing entity came from)
                dep_source = conn.last_deposit_source
                if dep_source is not None:
                    toward_source = graph.pos[self.node] - graph.pos[dep_source]
                    norm = np.linalg.norm(toward_source)
                    if norm > 1e-15:
                        toward_source /= norm
                    self.deflection += toward_source * new_deps
                    self.deposits_received += new_deps
        
        # Check if charging phase is complete
        if self.charge_ticks >= CHARGING_TIME:
            self.state = self.STATE_ROUTING
            # Fall through to routing
        else:
            return
    
    if self.state == self.STATE_ROUTING:
        neighbors = graph.neighbors(self.node)
        if not neighbors:
            self.state = self.STATE_CHARGING
            self.charge_ticks = 0
            return
        
        # Build combined direction: forward (inertia) + deflection (gravity)
        if self.arrival_dir is not None:
            combined = self.arrival_dir.copy()
            combined += self.deflection
            norm = np.linalg.norm(combined)
            if norm > 1e-15:
                combined /= norm
            else:
                combined = self.arrival_dir.copy()
        else:
            # First hop: no inertia. Use deflection only, or random.
            norm = np.linalg.norm(self.deflection)
            if norm > 1e-15:
                combined = self.deflection / norm
            else:
                combined = None  # pure random
        
        # Score outgoing connectors
        weights = np.zeros(len(neighbors))
        for i, nb in enumerate(neighbors):
            out_dir = graph.pos[nb] - graph.pos[self.node]
            out_norm = np.linalg.norm(out_dir)
            if out_norm > 1e-15:
                out_dir /= out_norm
            
            # Direction alignment (inertia + gravity)
            if combined is not None:
                dir_score = np.dot(combined, out_dir)
                dir_score = max(0.0, dir_score)  # no backward hops
            else:
                dir_score = 0.0
            
            # Deposit richness (accumulated field)
            eid = graph.edge_id(self.node, nb)
            conn = graph.connectors[eid]
            dep_score = sum(conn.deposits.values())
            
            weights[i] = dir_score + dep_score * DEPOSIT_WEIGHT + BASE_WEIGHT
        
        weights /= weights.sum()
        chosen_idx = rng.choice(len(neighbors), p=weights)
        chosen_nb = neighbors[chosen_idx]
        chosen_eid = graph.edge_id(self.node, chosen_nb)
        chosen_conn = graph.connectors[chosen_eid]
        
        # Begin traversal
        self.state = self.STATE_TRANSIT
        self.transit_edge = chosen_eid
        self.transit_dest = chosen_nb
        self.transit_remaining = max(1, int(chosen_conn.length))
        
        return
```

### Tick Order

```python
for tick in range(TICKS):
    # 1. Reset per-tick deposit counters
    for conn in graph.all_connectors:
        conn.reset_tick()
    
    # 2. Process IN_TRANSIT entities (may arrive and deposit)
    for en in all_entity_nodes:
        if en.state == STATE_TRANSIT:
            en.tick(graph, rng)
    
    # 3. Process CHARGING entities (read new deposits, accumulate deflection)
    for en in all_entity_nodes:
        if en.state == STATE_CHARGING:
            en.tick(graph, rng)
    
    # 4. Process ROUTING entities (make hop decision)
    for en in all_entity_nodes:
        if en.state == STATE_ROUTING:
            en.tick(graph, rng)
```

---

## Phases

### Phase 1: Star Equilibrium

**Setup:** 80 star nodes, 4 groups, 5000-node graph. CHARGING_TIME = 50.

**Expected behavior:**
- Star nodes arrive at nodes, sit for 50 ticks accumulating deflection
  from neighboring star-node hops
- Interior: lots of deflection from all directions → roughly isotropic
  → forward default dominates → star nodes circulate
- Boundary: deflection mostly from interior (more star nodes inside) →
  deflection points inward → star nodes route back to center
- Star should self-bind tighter than v7-v9 because boundary nodes are
  ACTIVELY deflected inward, not just randomly walking

**Measurements:**
1. Star COM and drift
2. Mean/max radius
3. Mean connector length (internal vs boundary)
4. Fraction in each state (CHARGING, ROUTING, TRANSIT)
5. Mean deflection magnitude at interior vs boundary nodes
6. Hop rate (should be ~ 1 / (mean_connector_length + CHARGING_TIME))

**Success criteria:**
1. Star binds: mean_r < 10 (ideally < 8)
2. COM drift < 3
3. Deflection magnitude at boundary > interior (directional inward pull)
4. No deadlock (all nodes cycle through states)

### Phase 2: Planet — The Real Orbit Test

**Setup:** Star pre-equilibrated. Planet 5 nodes, placed outside star.
NO tangential kick.

**The critical prediction:**

The planet arrives at a node. Sits for 50 ticks. During those 50 ticks,
star nodes occasionally hop along nearby connectors, depositing. The
deposits come from star-ward direction. The planet accumulates a
deflection vector pointing toward the star.

After 50 ticks, the planet routes: forward (inertia) + toward-star
(deflection). If the deflection is strong enough to significantly bend
the forward direction, the planet curves. If not, it goes mostly
straight.

At perihelion: high deposit flux → strong deflection → path curves
sharply. But the forward default ensures the planet doesn't reverse —
it curves AROUND the star. The angular momentum from the curve carries
it past.

At aphelion: low flux → weak deflection → path barely curves →
entity nearly continues straight. Gravity slowly bends it back inward.

**This should produce a REAL orbit — not a random walk — because:**
1. Forward continuation provides inertia (v7-v9 lacked this)
2. Deflection provides gravity (all versions had this)
3. The combination of inertia + gravity IS orbital mechanics
4. The charging phase provides the timescale for deflection accumulation

**Diagnostic measurements (same as v9 diagnostic):**
1. Per-hop tangential component (signed)
2. Random walk comparison (same hop rate, no deposits)
3. Deflection vector at each hop (magnitude and direction)
4. Forward component vs deflection component of each routing decision
5. Is the tangential accumulation COHERENT (orbit) or RANDOM (walk)?

**The decisive test:** Compare the per-hop tangential distribution to
v9. In v9, it was centered on zero with no bias (random walk). In v11,
if the momentum mechanism works, it should show a CONSISTENT SIGN
during each orbital arc (positive while swinging one way, negative
while swinging back). The SIGN should correlate with the orbital phase.

### Phase 3: Quantitative Tests (STRETCH)

Only if Phase 2 shows real orbits (coherent tangential motion, not
random walk).

1. Force vs distance (vary initial distance, measure deflection)
2. Kepler III: T² vs r³
3. Angular momentum conservation quality
4. Velocity vs distance (should match √(GM/r) profile)

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass |
| PLANET_COUNT | 5 | Planet mass |
| BASE_WEIGHT | 1.0 | Thermal noise in routing |
| DEPOSIT_WEIGHT | 0.01 | How much deposit count influences routing vs direction (start low — direction should dominate) |
| CHARGING_TIME | 50 | Ticks of idle charging per hop (the idle window) |

**New parameters vs v7:** CHARGING_TIME and DEPOSIT_WEIGHT.

CHARGING_TIME is the most important new parameter. It controls:
- The idle window duration (RAW 128 engagement)
- The deflection accumulation time (how much gravity bends the path)
- The velocity ceiling (hop cycle = L + CHARGING_TIME)

If orbits work at CHARGING_TIME = 50, test sensitivity: try 10, 25,
100, 200. The orbital behavior should be QUALITATIVELY the same across
a range (binding + tangential motion). The QUANTITATIVE details (orbital
radius, period) will depend on CHARGING_TIME.

DEPOSIT_WEIGHT should be LOW (0.01 or less). The primary routing signal
is the direction vector (forward + deflection). Deposit counts on
connectors are a secondary signal for tie-breaking when direction
scores are similar. If DEPOSIT_WEIGHT is too high, it dominates
direction and we're back to v6-style density routing (which saturates).

---

## What's Genuinely New in v11

1. **Newton's First Law on the graph.** Forward continuation as default.
   No deposits = no deflection = straight line. The entity doesn't need
   energy to maintain motion. It needs energy to CHANGE motion.

2. **Deflection as gravity.** Deposits arriving during the charging
   phase deflect the entity's path. The deflection vector points toward
   the deposit source. This is gravitational acceleration — not a force
   applied to a velocity, but a directional bias accumulated over the
   charging window.

3. **Charging phase as the timescale.** 50 ticks of idle charging
   provides: (a) the RAW 128 absorption window, (b) time to accumulate
   directional deflection, (c) natural velocity limit.

4. **No deadlock.** Forward default means the entity always has a
   direction to go, even with zero incoming deposits.

---

## Traps to Avoid

### Trap 21: Aristotelian Triggering
v10 proved that "reactive only" deadlocks. Entities MUST have forward
continuation as default. Do NOT make firing conditional on receiving a
deposit. The charging phase is a TIMER, not a trigger-wait.

### Trap 22: Direction Score Domination
If direction scores (dot products) dominate the routing entirely, the
entity ignores the deposit landscape and just goes straight. Need some
deposit-count influence for gravity at large distances where deflection
per hop is tiny. DEPOSIT_WEIGHT provides this — but keep it LOW.

### Trap 23: Backward Hops
The `max(0, dir_score)` prevents the entity from choosing connectors
that point backward (against combined direction). Without this, the
entity could reverse at perihelion — destroying the orbit. The entity
can slow down (choose a weakly-forward connector) but not U-turn.

### Trap 24: Deflection from Own Deposits
When the entity deposits on arrival, that deposit is on ITS OWN
connector. During the next charging phase, the entity should NOT
count its own deposit as deflection input. Only EXTERNAL deposits
(from other entities that hopped during the charging window) contribute
to deflection. Check: `conn.last_deposit_source != self.node`.

### Trap 25: First Hop Inertia
On the very first hop (no arrival direction), the entity has no forward
default. It routes based on deposit landscape or random. After the
first hop, arrival_dir is set. Make sure the first hop doesn't
accidentally set arrival_dir to zero or NaN.

---

*Newton on a graph. Forward is default. Deposits deflect.*
*The orbit is the balance between inertia (keep going) and gravity
(curve toward the mass). Not a random walk. Not a powered trajectory.
The natural consequence of two laws implemented on a finite graph.*
