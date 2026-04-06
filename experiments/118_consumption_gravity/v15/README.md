# Experiment 118 v15: Propagating Deposits Build Connectors

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Author: Tom (theory), Claude (spec)

---

## The Insight

The diagram from the session:

```
<star> p>p>p>p> <planet>
```

The connector between star and planet is a chain of deposits. Each "p"
is a deposit quantum. The connector IS these deposits. There is no limit
on connector length — the limit is the current tick number (how far
light has traveled).

**v5's error:** Empty tubes that deposits ride on. Wrong ontology.

**v4-v14's error:** Deposits sit where they're placed. No propagation.
The gravitational field only reaches as far as the star nodes physically
random-walked (~15 graph units). Beyond that: zero signal.

**v15's correction:** When an entity deposits a quantum, that quantum
PROPAGATES outward at c=1 hop/tick through the graph. At each node it
passes through, it deposits on the connector — GROWING it. The quantum
IS a photon. The trail it leaves IS the connector being built. The
connector is created by the radiation, not pre-existing.

After T ticks, the star's radiation wavefront has reached T hops from
the star. The gravitational field extends T hops. On a 50k-node graph,
after 300k warmup ticks the field covers the entire graph.

The density falls with distance because the wavefront diverges on the
graph (geometric dilution). Near the star: high deposit density. Far:
low. This IS the 1/r^2 gradient — from propagation physics, not from
local random walk.

---

## The Two Layers

### Layer 1: Entity nodes (slow, local)

Entity nodes sit at graph positions. They hop along connectors. They
route based on the accumulated deposit field on their local connectors.
Same mechanics as v13:

- Forward default (Newton I)
- Accumulated density gravity (matching deposits / connector length)
- Length-proportional momentum (forward = L * arrival_dir)
- Same/Different extension rule (Same reinforces, Different extends)
- Charging phase (idle ticks between hops)
- Deposit-on-arrival (one quantum per completed traversal)

Entities are SLOW. They hop every ~50-100 ticks. They represent matter.

### Layer 2: Propagating quanta (fast, global)

When an entity deposits a quantum (on arrival after traversal), that
quantum enters the propagation system. It propagates outward at c=1
hop/tick using forward-continuation (v5's forward redirect table).

At each hop, the quantum DEPOSITS on the connector it traverses. This
is what grows the connector — the quantum IS a Different event on
non-matching connectors. The quantum builds the gravitational field
as it propagates.

Quanta are FAST. They hop every tick. They represent radiation/light.

### The ontological correction

v5 had quanta riding on fixed-length empty tubes. Wrong.
v15 has quanta BUILDING connectors as they propagate. The quantum's
trail IS the connector. The connector didn't exist before the quantum
passed — or rather, the connector was shorter before, and the quantum
made it longer by depositing.

No empty tubes. The connector IS its deposits, including the deposits
left by propagating quanta. All the way down.

---

## How Propagating Quanta Work

### Creation

When an entity node arrives at a destination (transit complete), it
deposits one quantum on the traversed connector. That quantum also
enters the propagation system:

```python
# On entity arrival:
connector.append(entity.group)          # deposit on local connector
propagation.add_quantum(entity.group,   # quantum enters propagation
                        dest_node,       # starts at destination
                        from_node)       # arrived from this direction
```

### Propagation (each tick)

Each in-flight quantum:
1. Follows the forward-continuation path (graph geometry)
2. Deposits on the connector it traverses (grows it if Different)
3. Advances to the next node
4. Propagates at c=1 hop/tick

```python
def tick_quantum(q, graph, forward_table):
    next_node = forward_table.next_node(q.from_node, q.node)
    edge = graph.edge(q.node, next_node)
    edge.append(q.group)  # deposit on connector — grows it if Different
    q.from_node = q.node
    q.node = next_node
```

### Termination

Quanta propagate until:
- They exit the graph boundary (no more neighbors) — destroyed
- They've propagated for MAX_HOPS (e.g., 500) — destroyed
- They reach an entity node that absorbs them (RAW 128 store) — future enhancement

For v15 Phase 1: no absorption. Quanta just propagate and expire at MAX_HOPS.
The deposits they left behind are permanent (on connectors).

### Effect on the gravitational field

After warmup (300k ticks), each of the 80 star nodes has hopped ~5000
times. Each hop produced one quantum. 80 × 5000 = 400,000 quanta have
propagated through the graph. Each quantum traveled up to 500 hops,
depositing on each connector. Total deposits from propagation:
~400,000 × 500 = 200 million deposits across the graph.

These deposits are NOT uniform. They follow the forward-continuation
paths from the star's position. Near the star: many quanta pass through
(high density). Far from star: fewer quanta (geometric dilution).

The density profile should approximate 1/r^2 because the surface area
of a sphere at distance r grows as r^2, and the same number of quanta
spread over that area.

---

## Reactive Charging Revisited

With propagating quanta, the deposit arrival rate at any node is:
- Near the star: MANY quanta pass through per tick (high flux)
- Far from star: FEW quanta per tick (low flux)

This naturally enables REACTIVE CHARGING (v10 idea) without deadlock:

The planet sits at a node. Propagating quanta from the star pass through
its local connectors, depositing as they go. Each deposit arrival
charges the planet's capacitor. When threshold is reached, the planet
fires and hops.

Near the star: quanta arrive every few ticks → fast charging → fast hops.
Far from star: quanta arrive rarely → slow charging → slow hops.
In empty space (no quanta at all): hit MAX_WAIT → fire on forward default.

**This gives velocity proportional to local flux — the Keplerian profile.**

### The charging cycle:

```
ARRIVE at node
    Deposit on traversed connector
    Emit quantum into propagation system
    Reset charge = 0
    ↓
CHARGING: wait for propagating quanta to arrive on local connectors
    Each arriving quantum: charge += 1
    If charge >= THRESHOLD: transition to ROUTING
    If ticks_waiting >= MAX_WAIT: transition to ROUTING (safety)
    ↓
ROUTING: forward + gravity
    Same as v13: forward = last_L * arrival_dir, gravity from density
    Choose connector, begin traversal
    ↓
TRAVERSE: travel for connector.length ticks
    ↓
ARRIVE → repeat
```

THRESHOLD = 1 for v15 (fire on first arriving quantum).
MAX_WAIT = 200 ticks (safety fallback — prevents infinite freeze far
from star, but should rarely trigger because propagating quanta reach
the entire graph).

---

## Implementation

### Files

```
v15/
├── README.md              (this file)
├── graph.py               (from v12/v13 — Same/Different Connector)
├── entity.py              (v13 routing + reactive charging)
├── propagation.py          (v5-style forward table + quantum propagation)
├── phase2_orbit.py         (combined: warmup + planet + propagation)
└── results/
```

### graph.py

From v12/v13 unchanged. Same/Different Connector class.

### propagation.py

Simplified v5 forward table + quantum list:

```python
class ForwardTable:
    """Precomputed forward-continuation for graph geometry."""
    # Same as v8/v9 — next_node(from, at) → best forward neighbor

class QuantumField:
    """Manages propagating quanta."""

    def add(self, group, node, from_node):
        """Create a new quantum."""

    def tick(self, graph):
        """Propagate all quanta one hop. Each deposits on traversed connector."""

    def deposits_this_tick_at(self, node):
        """Count quanta that deposited on connectors of this node this tick."""
```

### entity.py

v13 routing (forward + gravity from accumulated density + length momentum)
plus reactive charging:

```python
STATE_CHARGING = 0  # waiting for quantum arrivals
STATE_ROUTING = 1   # making hop decision
STATE_TRANSIT = 2   # traversing connector

def tick_charging(self, graph, quantum_field, tick):
    # Count quanta depositing on my local connectors this tick
    arrivals = quantum_field.deposits_this_tick_at(self.node)
    self.charge += arrivals
    self.ticks_waiting += 1

    if self.charge >= THRESHOLD or self.ticks_waiting >= MAX_WAIT:
        self.state = STATE_ROUTING
```

### Tick loop

```python
for tick in range(TICKS):
    # Phase 1: entity transit arrivals (deposit + emit quantum)
    for entity in [star, planet]:
        entity.tick_transit(graph, tick, quantum_field)

    # Phase 2: propagate ALL quanta one hop (they deposit on connectors)
    quantum_field.tick(graph)

    # Phase 3: entity charging (read quantum arrivals)
    for entity in [star, planet]:
        entity.tick_charging(graph, quantum_field, tick)

    # Phase 4: entity routing (read accumulated density field)
    for entity in [star, planet]:
        entity.tick_routing(graph, rng)
```

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 50,000 | Large graph (from v14) |
| SPHERE_R | 80.0 | Large universe |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass |
| PLANET_COUNT | 5 | Planet mass |
| BASE_WEIGHT | 0.1 | Thermal noise |
| THRESHOLD | 1 | Fire on first quantum arrival |
| MAX_WAIT | 200 | Safety fallback (ticks) |
| MAX_HOPS | 500 | Quantum propagation limit |

### Why MAX_HOPS = 500

The graph diameter is ~25 hops (R=80, rc=6.3, diameter ≈ 2*80/6.3 ≈ 25).
MAX_HOPS = 500 means each quantum traverses the graph ~20 times before
expiring. This ensures the field reaches everywhere, even after reflections
at the boundary.

### Why MAX_WAIT = 200

With 80 star nodes emitting quanta that propagate at c=1 hop/tick, the
average time between quantum arrivals at any node depends on distance:
- At the star surface: ~1-5 ticks (frequent)
- At r=40 (graph midpoint): ~20-50 ticks (moderate)
- At r=70 (near boundary): ~50-100 ticks (rare)

MAX_WAIT = 200 is 2-4× the worst-case arrival rate. It should almost
never trigger — it's only for truly isolated nodes.

---

## Phases

### Phase 1: Warmup + Star Equilibrium

300k ticks, star only, with propagating quanta.

**Measurements:**
1. Star mean radius (does propagation-based gravity bind the star?)
2. Quantum count over time (should reach steady state)
3. Deposit density profile (should show 1/r^2 from propagation)
4. Mean charging time at interior vs boundary (velocity gradient)
5. Star COM drift
6. Same/Different deposit counts (quanta produce mostly Different)

**Predictions:**
- The propagating quanta create a REAL density gradient (1/r^2)
- Star nodes see this gradient and route inward
- Whether this BINDS the star depends on gradient strength vs forward momentum
- At minimum: the gravitational field now reaches the entire graph

### Phase 2: Planet

Planet outside star. NO kick. Reactive charging.

**The critical prediction:**
- Planet's charging time depends on local quantum flux
- Near star: fast charging, fast hops (high velocity)
- Far from star: slow charging, slow hops (low velocity)
- The velocity profile IS the quantum flux profile IS 1/r^2
- Combined with forward default + density gravity:
  real orbital mechanics with distance-dependent velocity

**Success criteria:**
1. Planet velocity varies with distance (not flat like v14)
2. Planet bound (attracted + doesn't escape)
3. Angular coherence > 0.3
4. Charging time increases with distance from star

---

## Performance Concern

With 80 star nodes emitting quanta each hop (~5000 hops per node over
300k warmup = 400k quanta), and each quantum propagating for up to 500
hops, there could be 400k × 500 = 200M deposit operations.

But at any given tick, the active quanta = (quanta created in last 500
ticks) = (hop rate per tick) × 500. With ~80 hops per 50 ticks = 1.6
hops/tick → ~800 active quanta at steady state. Each propagates 1 hop
per tick. So: 800 quantum hops per tick + 800 deposit operations per
tick. Very manageable.

The connectors WILL grow from all the Different deposits. After 300k
ticks with ~800 quanta depositing each tick: ~240M deposits total.
Spread across ~574k connectors: ~418 deposits per connector on average.
Connectors grow from initial ~6 to ~424. Transit time increases
accordingly. Entity hop rate slows. This is natural — the universe
ages and distances grow.

---

## What Could Go Wrong

### Dead end 1: Saturation again
If propagating quanta deposit everywhere equally (no gradient), we're
back to v6. The forward-continuation should prevent this (quanta follow
beams, not diffuse randomly). But on a 25-hop-diameter graph, beams
scatter after a few bounces. Need to check.

### Dead end 2: Performance
If quantum propagation is too expensive (too many active quanta), the
simulation grinds to a halt. Budget: 800 quanta × 1 hop/tick should
be fine. But if star hop rate is much higher, or MAX_HOPS is too large,
could blow up.

### Dead end 3: Connector growth too fast
200M deposits growing connectors → connectors reach length ~400. Transit
time = 400 ticks. Entity hop rate drops to 1 per 450 ticks (400 transit
+ 50 MAX_WAIT). Very slow. But this IS the theory — the universe
expands, distances grow, things slow down.

### Dead end 4: Wrong gradient shape
Forward-continuation on a small graph (25 hops diameter) might not
produce 1/r^2. Beams could focus or scatter depending on graph topology.
The density profile might be flat (like v5 forward propagation showed
on the 5k graph). Need to measure.

---

*The photon builds the road as it travels.*
*The connector didn't exist before the radiation passed.*
*The gravitational field IS the accumulated radiation trail.*
*v5 was right about propagation. v4 was right about ontology.*
*v15 unifies: propagating deposits that build connectors.*
