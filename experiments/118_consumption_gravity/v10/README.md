# Experiment 118 v10: Reactive Entities — Fire on Incoming Deposit

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Author: Tom (theory), Claude (spec)

---

## Why v10 Exists

### The v9 diagnostic proved three things:

1. **The tangential motion in v7-v9 is a random walk, not an orbit.**
   A pure random walk on the same graph produces the same per-hop angular
   displacement. The "orbit" is a bound random walk that looks orbital
   in angular projection.

2. **Routing decisions are near-random.** Score margins between best and
   second-best connectors are < 0.1. The planet is flipping coins, not
   navigating a gradient.

3. **The RAW 128 store/move/radiate partition doesn't engage.** Entity
   nodes are idle for 1 tick per ~200 tick cycle. In-flight quanta (~4)
   almost never find that window. Store = 0 across all runs.

### The root cause: entities fire spontaneously

In v7-v9, entity nodes fire every time they arrive at a new node. They
don't wait for anything. They arrive, route, deposit, depart — all in
one tick. This means:

- **Idle window = 1 tick** — too narrow for RAW 128 absorption
- **Velocity = c on short connectors** — unrealistically fast
- **No momentum** — each hop is an independent routing decision with
  near-random margins, no directional memory
- **Hop rate independent of environment** — the planet hops at the same
  rate whether it's near the star (rich field) or in deep space (empty)

### The fix: entities fire in RESPONSE to incoming deposits

RAW 126 says the capacitor charges from external deposits and fires
when threshold is reached. The entity doesn't fire spontaneously — it
fires because something arrived and triggered its capacitor.

In v10, entity nodes WAIT until a deposit arrives on one of their
local connectors (another entity hops along a connector connected to
this node). That arrival event charges the capacitor. When threshold
is reached, the entity fires, discharges one quantum, and departs.

This single change gives:

- **Large idle window** — the entity sits at the node for as many ticks
  as it takes for a deposit to arrive. In sparse regions: hundreds of
  ticks. In dense regions: a few ticks. During this ENTIRE window, the
  node can absorb in-flight quanta (RAW 128).

- **Velocity from local flux** — the entity's hop rate IS the local
  deposit arrival rate. Near star: fast (many star nodes depositing
  on nearby connectors). Far from star: slow (rare traffic). Planet
  velocity scales with distance from star. Naturally.

- **Momentum from incoming direction** — the deposit that triggered the
  capacitor came from a specific direction (a star node hopped along
  a specific connector). The entity's discharge is biased in that
  direction. The incoming deposit carries directional energy that
  transfers to the outgoing discharge. This IS momentum — not as a
  parameter, but as a consequence of the capacitor being triggered
  by a directional event.

- **Planet can't move into Unknown** — if there are zero deposits
  arriving on any connector, the capacitor never charges, the entity
  never fires, the entity never hops. It's frozen. Matter can only
  move where there's energy (deposits) to power it. Gravity becomes
  literally the only thing that moves matter.

---

## The Entity Tick Cycle

### Three states per entity node:

```
CHARGING  →  FIRING  →  IN_TRANSIT  →  CHARGING
   ↑                                      │
   └──────────────────────────────────────┘
```

### State: CHARGING (idle, waiting for trigger)

The entity node sits at a graph node. Each tick:

1. Check: has any entity hopped along one of my k local connectors
   this tick?
2. If YES: that hop deposited a quantum on that connector. The
   quantum's arrival direction is known (which connector, which
   direction). The capacitor charges: `charge += 1`.
3. If NO: nothing happens. Stay idle. Continue waiting.
4. If `charge >= THRESHOLD`: transition to FIRING.

**During the ENTIRE charging phase, the node is idle.** This is the
absorption window for RAW 128 in-flight quanta. Any in-flight quantum
arriving at this node during the charging phase gets absorbed (stored).

**THRESHOLD = 1 for v10.** The entity fires as soon as one deposit
arrives on any connector. This is the minimum threshold — the fastest
possible response. Higher thresholds can be tested in v11 if needed.

### State: FIRING (routing decision + discharge)

The capacitor has reached threshold. The entity makes its routing
decision and discharges:

1. **Routing signal:** Read accumulated deposit counts on all k local
   connectors. Compute routing scores (total deposits per connector).

2. **Momentum bias:** The triggering deposit arrived from a specific
   direction. Bias the routing toward the FORWARD continuation of that
   direction:

   ```python
   trigger_dir = normalize(pos[my_node] - pos[trigger_source_node])
   
   for each neighbor N:
       deposit_score = total_deposits(connector_to_N)
       outgoing_dir = normalize(pos[N] - pos[my_node])
       forward = dot(trigger_dir, outgoing_dir)
       
       routing_weight = deposit_score + incoming_deposit_count * max(0, forward)
   ```

   The momentum strength is NOT a parameter. It IS the incoming deposit
   count on the triggering connector. Rich connector (near star) = strong
   forward push. Sparse connector (far from star) = weak push, gravity
   dominates.

3. **Discharge:** Emit one quantum onto the chosen connector. Reset
   charge to 0. Record the emission direction.

4. **Depart:** Transition to IN_TRANSIT on the chosen connector.

### State: IN_TRANSIT (traversing connector)

Same as v7/v9:
- Traversal takes `connector.length` ticks
- No deposit during transit (deposit-on-arrival, not deposit-per-tick)
- On arrival: deposit one quantum on the traversed connector, transition
  to CHARGING

---

## What "Deposit Arrives on My Connector" Means

The entity detects when another entity hops along one of its connectors.
Specifically: entity node E sits at graph node P. P has k neighbors
(N₁, N₂, ... Nₖ) connected by connectors. If ANY entity node (star or
planet) hops along connector (P, Nᵢ) — either from P to Nᵢ or from Nᵢ
to P — that hop deposited a quantum on connector (P, Nᵢ). Entity E
detects this.

Implementation: each tick, after all entity hops are resolved, check
which connectors received new deposits. For each CHARGING entity node,
check if any of its local connectors received a deposit this tick.

```python
# After all entity hops are processed:
for entity_node in charging_entities:
    for connector in entity_node.local_connectors:
        if connector.deposits_this_tick > 0:
            entity_node.charge += connector.deposits_this_tick
            entity_node.last_trigger_connector = connector
            entity_node.last_trigger_direction = connector.last_deposit_direction
```

Need to track `deposits_this_tick` per connector (reset each tick) and
`last_deposit_direction` (which end the depositing entity came from).

---

## Why This Produces Real Orbits

### Momentum from directional triggering

When a star node at position S hops along connector (S, P) toward the
planet at P, it deposits a quantum on that connector. The planet
detects this. Its capacitor fires. The triggering direction is S → P.
The planet's discharge is biased FORWARD from the trigger — in the
direction away from S (continuing the momentum of the incoming deposit).

At perihelion: many star nodes near the planet, depositing from all
directions but predominantly from the star's center. The planet gets
triggered frequently (fast hops) with strong forward bias (the deposits
came from the star direction, so forward = away from star). This is
the swing-through — momentum carries the planet past the star.

At aphelion: few star nodes nearby. Rare triggers. Slow hops. Weak
forward bias. The routing signal (accumulated deposits toward the star)
dominates. The planet falls back inward.

### Velocity scaling

The planet's hop rate = the rate of deposits arriving on its connectors.
This scales with the local star-node traffic:

- **Inside the star (r < star_radius):** Star nodes everywhere.
  Multiple deposits per tick on planet's connectors. Planet hops
  frequently. High velocity.

- **At star surface (r ≈ star_radius):** Some star nodes nearby.
  Moderate deposit rate. Moderate velocity.

- **Outside the star (r > star_radius):** Only occasional star-node
  wanderers. Rare deposits. Slow velocity. The planet crawls.

- **Far from star (r >> star_radius):** Zero star traffic. Zero
  deposits. Planet frozen. No movement without incoming energy.

This naturally produces Keplerian velocity profile: fast at perihelion,
slow at aphelion, zero at infinity.

### RAW 128 engagement

The charging phase lasts from arrival until the next deposit arrives.
Far from the star: this could be hundreds or thousands of ticks. During
this entire window, in-flight quanta (from the star's discharges that
propagated outward) can reach the planet and be absorbed.

The in-flight quanta serve a different role now: they're not the
primary trigger (star-node hops are). They're ADDITIONAL energy that
gets absorbed during the idle window. The store/move partition engages
naturally because the entity is idle for long enough.

But for v10 Phase 1, we can test WITHOUT in-flight quanta first.
The reactive triggering + momentum bias might be sufficient for
orbits. Add in-flight quanta in Phase 2 if needed.

---

## Implementation

### Connector changes

Add per-tick tracking:

```python
class Connector:
    def __init__(self, geometric_length):
        self.initial_length = geometric_length
        self.deposits = {}
        self.total = 0
        # NEW: per-tick tracking
        self.deposits_this_tick = 0
        self.last_deposit_source = None  # node the depositing entity came from
        self.last_deposit_dest = None    # node the depositing entity went to
    
    def append(self, group_tag, source_node, dest_node):
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        self.deposits_this_tick += 1
        self.last_deposit_source = source_node
        self.last_deposit_dest = dest_node
    
    def reset_tick(self):
        self.deposits_this_tick = 0
```

### Entity node changes

```python
class EntityNode:
    STATE_CHARGING = 0
    STATE_FIRING = 1
    STATE_TRANSIT = 2
    
    def __init__(self, node, group, spectrum):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.state = self.STATE_CHARGING
        self.charge = 0
        self.trigger_direction = None  # direction of triggering deposit
        self.transit_edge = None
        self.transit_remaining = 0
        self.transit_dest = None
        self.arrived_from = None  # node we arrived from (for deposit-on-arrival)
    
    def tick(self, graph, rng):
        if self.state == self.STATE_TRANSIT:
            self.transit_remaining -= 1
            if self.transit_remaining <= 0:
                # ARRIVE: deposit on the traversed connector
                eid = graph.edge_id(self.arrived_from, self.node)
                # Wait: we're arriving at transit_dest, not self.node yet
                dest = self.transit_dest
                eid = graph.edge_id(self.node, dest)
                graph.connectors[eid].append(self.group, self.node, dest)
                self.arrived_from = self.node
                self.node = dest
                self.state = self.STATE_CHARGING
                self.charge = 0
            return
        
        if self.state == self.STATE_CHARGING:
            # Check local connectors for new deposits this tick
            neighbors = graph.neighbors(self.node)
            for nb in neighbors:
                eid = graph.edge_id(self.node, nb)
                conn = graph.connectors[eid]
                if conn.deposits_this_tick > 0:
                    self.charge += conn.deposits_this_tick
                    # Record trigger direction
                    if conn.last_deposit_source is not None:
                        self.trigger_direction = conn.last_deposit_source
            
            if self.charge >= THRESHOLD:
                self.state = self.STATE_FIRING
                # Fall through to firing
            else:
                return  # Stay idle, keep charging
        
        if self.state == self.STATE_FIRING:
            neighbors = graph.neighbors(self.node)
            if not neighbors:
                self.state = self.STATE_CHARGING
                self.charge = 0
                return
            
            # Routing: deposit count + momentum bias from trigger direction
            scores = np.zeros(len(neighbors))
            for i, nb in enumerate(neighbors):
                eid = graph.edge_id(self.node, nb)
                conn = graph.connectors[eid]
                scores[i] = sum(conn.deposits.values())
            
            # Momentum bias from triggering deposit direction
            momentum = np.zeros(len(neighbors))
            if self.trigger_direction is not None:
                trigger_dir = graph.pos[self.node] - graph.pos[self.trigger_direction]
                trigger_len = np.linalg.norm(trigger_dir)
                if trigger_len > 1e-15:
                    trigger_dir /= trigger_len
                    # Incoming deposit count as momentum strength
                    trigger_eid = graph.edge_id(self.node, self.trigger_direction)
                    trigger_conn = graph.connectors[trigger_eid]
                    trigger_strength = trigger_conn.deposits_this_tick
                    
                    for i, nb in enumerate(neighbors):
                        out_dir = graph.pos[nb] - graph.pos[self.node]
                        out_len = np.linalg.norm(out_dir)
                        if out_len > 1e-15:
                            out_dir /= out_len
                            forward = np.dot(trigger_dir, out_dir)
                            momentum[i] = trigger_strength * max(0, forward)
            
            weights = scores + momentum + BASE_WEIGHT
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
            self.arrived_from = self.node
            
            # Reset for next cycle
            self.charge = 0
            self.trigger_direction = None
```

### Tick order (CRITICAL)

The order of operations within one tick matters:

```python
for tick in range(TICKS):
    # 1. Reset per-tick deposit counters on all connectors
    for conn in graph.all_connectors:
        conn.reset_tick()
    
    # 2. Process all IN_TRANSIT entities (they may arrive and deposit)
    for entity_node in all_entity_nodes:
        if entity_node.state == STATE_TRANSIT:
            entity_node.tick(graph, rng)
    
    # 3. Now check CHARGING entities (they read deposits_this_tick)
    for entity_node in all_entity_nodes:
        if entity_node.state == STATE_CHARGING:
            entity_node.tick(graph, rng)
    
    # 4. Process FIRING entities
    for entity_node in all_entity_nodes:
        if entity_node.state == STATE_FIRING:
            entity_node.tick(graph, rng)
```

Transit entities deposit first → charging entities detect those deposits
→ firing entities route and depart. This ensures the trigger-response
chain works within one tick.

---

## Phases

### Phase 1: Star Equilibrium

**Setup:** Same as v7-v9 (80 star nodes, 4 groups, 5000-node graph).

**Expected differences from v9:**
- Star nodes in CHARGING state wait for neighboring star nodes to
  deposit. Inside the star: constant mutual triggering → high hop
  rate. Boundary: less triggering → slower hops.
- Star should bind MORE tightly because boundary nodes hop less
  frequently (less traffic) than interior nodes (lots of traffic).
  The velocity gradient reinforces binding — faster interior, slower
  boundary.

**Measurements:** Same as v9, plus:
- Fraction of star nodes in each state (CHARGING, FIRING, TRANSIT)
- Mean charging time (ticks from arrival to next trigger)
- Charging time vs distance from star COM

**Success criteria:**
1. Star binds (mean_r < 10, COM drift < 3)
2. Charging time increases with distance from center (velocity gradient)
3. Hop rate inside star > hop rate at boundary

### Phase 2: Planet — The Real Orbit Test

**Setup:** Star pre-equilibrated. Planet outside star. NO tangential kick.

**Expected behavior with reactive triggering + momentum:**
1. Planet starts in CHARGING state. Waits for deposits.
2. Eventually a star node wanders near and deposits on planet's connector.
3. Planet fires, biased in the forward direction of the incoming deposit.
4. Planet hops toward the star (the deposit came from star-ward).
5. As planet approaches star, triggering rate increases → planet
   accelerates.
6. Near perihelion: high triggering rate, strong momentum bias from
   the concentrated star-direction deposits → planet swings PAST the
   star instead of reversing.
7. Planet climbs outward. Triggering rate drops. Planet decelerates.
8. At aphelion: rare triggers. Planet nearly frozen. Gravitational
   routing signal dominates. Falls back inward.
9. Repeat → orbit.

**The critical test:** Does the momentum bias from directional triggering
produce systematic tangential velocity? Or is it still a random walk?

**Diagnostic (same as v9 diagnostic):**
- Per-hop tangential component: signed, tracked over time
- Random walk comparison: 20 trials of pure random walk at same hop rate
- Is the tangential accumulation coherent (orbit) or random (walk)?

**Measurements:**
1. Planet distance from star COM
2. Planet hop rate over time (should correlate with distance)
3. Tangential angle accumulation
4. Momentum direction vs routing direction at each hop
5. Charging time at each node (should increase with distance)
6. Partition: of the planet's hops, how many were triggered by star
   deposits vs planet deposits vs in-flight quanta?

### Phase 3: Quantitative Tests (if Phase 2 shows real orbits)

1. Force vs distance
2. T² vs r³ (Kepler III)
3. Angular momentum conservation
4. Velocity vs distance profile (should match √(1/r) for circular)

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass (node count) |
| PLANET_COUNT | 5 | Planet mass (node count) |
| BASE_WEIGHT | 1.0 | Thermal motion |
| THRESHOLD | 1 | Min deposits to trigger (1 = react immediately) |

**Derived (not parameters):**
- Planet velocity (from local deposit arrival rate)
- Momentum strength (from incoming deposit count)
- Orbital distance (from flux balance)
- Charging time (from local traffic density)

---

## What's Genuinely New in v10

1. **Reactive entities.** Entities don't fire spontaneously. They fire
   in response to incoming deposits. This is RAW 126 properly
   implemented — the capacitor charges from external energy.

2. **Velocity from flux.** The entity's hop rate IS the local deposit
   arrival rate. No velocity parameter. Speed emerges from environment.

3. **Momentum from trigger direction.** The incoming deposit came from
   a specific direction. The outgoing discharge is biased forward.
   Momentum is directional energy transfer, not a stored variable.

4. **Large idle window.** The charging phase can last hundreds of ticks.
   Plenty of time for RAW 128 in-flight quanta to be absorbed. The
   partition mechanism can finally engage.

5. **Matter can't move into the void.** No incoming deposits = no
   triggers = no hops. The entity is frozen in Unknown territory.
   Only deposit fields (gravity) can move matter.

---

## Connection to the Diagnostic Results

| v9 diagnostic finding | v10 response |
|----------------------|-------------|
| Tangential motion = random walk | Momentum bias gives systematic direction |
| Score margins tiny (near-random routing) | Momentum term breaks the near-random tie |
| Planet moves at near-c on short connectors | Reactive triggering limits hop rate to flux |
| RAW 128 idle window too narrow (1 tick) | Charging phase provides hundreds of ticks |
| Store = 0 (no absorption) | Large idle window enables absorption |

---

## Traps to Avoid

### Trap 17: Spontaneous Emission
v7-v9 entities fired every time they arrived at a node. v10 entities
WAIT for a trigger. Do not add spontaneous emission "to keep things
moving." If the entity isn't triggered, it should sit.

### Trap 18: Symmetric Triggering
When a star node hops from A to B, it deposits on connector (A,B).
This should trigger charging entities at BOTH A and B (the deposit
is on their shared connector). Make sure both endpoints detect the
deposit.

### Trap 19: Self-Triggering
When an entity deposits on arrival (deposit-on-arrival from v7), that
deposit should NOT trigger the same entity's next charging phase. The
entity just deposited — it doesn't immediately re-trigger on its own
deposit. Only EXTERNAL deposits (from other entities) trigger.

### Trap 20: Tick Order
Transit arrivals must be processed BEFORE charging checks. Otherwise,
charging entities won't see deposits from entities that arrived this
tick. See the tick order section above.

---

*Reactive entities. Velocity from flux. Momentum from trigger direction.*
*The planet can only move where there is energy to move it.*
*No deposits = no motion. Gravity is the only engine.*
