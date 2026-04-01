# Experiment 118 v7: Connector-Geometry Orbital Mechanics

## Status: READY FOR IMPLEMENTATION
## Date: April 1, 2026
## Author: Tom (theory), Claude (spec)

---

## What v4–v6 Taught Us

| Version | Ontology | Routing | Result | Lesson |
|---------|----------|---------|--------|--------|
| v4 | Connector = deposits ✅ | Weak (1 + recent) | Star expands 3.8× | Right ontology, weak routing |
| v5 | Fixed empty graph ❌ | Propagating flows | Uniform density, no gradient | Wrong ontology — no empty tubes |
| v5 fwd | Fixed empty graph ❌ | Forward beams | Deposits pile at boundary | Beams don't diverge on small graph |
| v6 | Connector = deposits ✅ | Accumulated density | Saturates to 97% uniform | Density ratio saturates on finite graph |

**The saturation theorem**: On a finite graph, any single-type random walk
eventually deposits on all connectors uniformly. No density gradient survives.
This kills all routing schemes based on deposit density ratios.

**The real mechanism**: Orbital mechanics don't come from field gradients.
They come from the GEOMETRIC FACT that a planet has limited star-facing
connectors and can't accept the star's full deposit output.

---

## The Core Model

### Connector = chain of deposits (v4 ontology, confirmed)

```
A —[d₁][d₂][d₃][d₄][d₅]— B
    ^^^^^^^^^^^^^^^^^^^^^
    this IS the connector
    nothing underneath
```

- Length = deposit count + initial geometric length
- Each entity hop appends one deposit → connector grows by 1
- Append-only: deposits never removed

### Traversal time proportional to connector length

A node traversing a connector of length L takes L ticks to complete the
traversal. During those L ticks:
- The node is "in transit" — it has left the source but not arrived at
  the destination
- Each tick in transit, the node deposits one quantum onto the connector
  → the connector grows by 1 during traversal
- This means: traversal of length-L connector adds L deposits, so the
  connector becomes length 2L after one traversal

**This produces compound growth with NO free parameter.** The growth per
traversal is proportional to current length. No EXTEND_RATE needed.

**This IS gravitational time dilation.** A node deep inside the star
(long internal connectors) takes many ticks per hop. Its effective clock
rate (hops per external time) is slow. A node on the boundary (short
connectors) hops quickly. Fast clock. Exactly the gravitational time
dilation from RAW 126 — clocks slow where the deposit density is high.

### Star self-binding from time dilation

Star nodes near the center traverse long internal connectors. Each
traversal takes many ticks. During those ticks, they deposit on the
internal connector, making it longer, making future traversals even
slower. The center becomes a time trap: nodes that enter spend
increasingly long there.

Meanwhile, boundary nodes traverse short connectors. Quick hops. They
can reach the boundary and occasionally escape, depositing on external
connectors. But the probability of escape decreases as internal
connectors grow — the routing signal (absolute deposit count) is
overwhelmingly toward the center, and even random walks are biased
inward by the sheer count difference.

The star binds because its center is a time well. Not because of a
density gradient — because of a TIME gradient (long connectors = slow
traversal = nodes spend more time inside).

### How the star radiates

Star surface nodes occasionally hop outward onto short boundary
connectors. This is fast (short connector → quick traversal). The
deposit they leave on the boundary connector is the star's "radiation."
Over many ticks, surface nodes make many short outward hops and
occasional long inward hops, creating a net outward deposit flow at the
boundary.

Radiation rate emerges from: surface area × short-connector hop rate.
No parameter.

---

## The Planet: Limited Star-Facing Connectors

### The geometric bottleneck

A planet node has k≈24 connectors. In a 3D random geometric graph,
roughly 1/4 of those point in any given hemisphere direction. So
approximately k_star ≈ 6 connectors face generally toward the star.
The rest face sideways or away.

The planet can only receive star deposits through those ~6 connectors.
It can only process (consume/transform) deposits on those connectors
at a rate of 1 per tick per planet node. A 5-node planet processes
at most 5 deposits per tick from the star direction.

### Three regimes

**1. Close to star (high flux):** Star has many surface nodes facing
the planet. Multiple star deposits arrive per tick on the planet's ~6
star-facing connectors. Planet processes 5/tick. Excess deposits queue
on the star-facing connectors. Those connectors GROW (each queued
deposit is a new link in the chain). The star-planet distance increases
because the connectors between them are literally getting longer.

Not "pushed away" — the space between them grows from unconsumed
deposits. The planet doesn't move; the road gets longer.

**2. Far from star (low flux):** Star deposits arrive slowly on the
planet's star-facing connectors (diluted through the mesh over many
hops). Planet can consume everything. No queue. No growth on those
connectors. The planet's routing signal points toward the star
(the only direction with any deposits). Planet hops toward the star.
Distance decreases.

**3. Equilibrium:** Star deposit arrival rate on the planet's star-facing
connectors = planet consumption rate. No excess. No growth. No net
routing preference. Stable distance.

### Tangential motion from asymmetric overflow

When the planet approaches the star from one direction, only the
connectors on THAT side overflow. Say connectors c1, c2, c3 face the
star and overflow. Connectors c4, c5, c6 also face star-ward but from
a slightly different angle — they receive less flux (the mesh paths
from the star through them are longer or fewer). Connectors c7–c24
face sideways/away and receive little.

The planet routes toward non-saturated connectors. c4, c5, c6 are
unsaturated but still have some star signal → planet routes there.
In the 3D embedding, those connectors point at a slight angle to the
radial direction. The planet moves sideways.

This sideways motion IS tangential velocity. It emerges from the
asymmetric overflow pattern. Different connectors overflow at different
rates depending on the exact graph paths between star and planet.

As the planet moves sideways, the set of star-facing connectors
changes (new node, new neighbors). The overflow pattern shifts.
The tangential direction evolves. If the system is quasi-periodic,
this traces an orbit.

---

## Implementation

### Node states

```python
class NodeState:
    IDLE = 0        # at a node, ready to hop
    IN_TRANSIT = 1  # traversing a connector, not yet arrived
```

### Entity node

```python
class EntityNode:
    def __init__(self, node, group, spectrum):
        self.node = node              # current graph node
        self.group = group            # deposit tag (s0, p1, etc.)
        self.spectrum = spectrum      # set of matching groups
        self.state = NodeState.IDLE
        self.transit_edge = None      # which edge being traversed
        self.transit_remaining = 0    # ticks left to complete traversal
        self.transit_dest = None      # destination node
    
    def tick(self, graph, rng):
        if self.state == NodeState.IN_TRANSIT:
            # Deposit one quantum on the connector being traversed
            graph.connectors[self.transit_edge].append(self.group)
            self.transit_remaining -= 1
            
            if self.transit_remaining <= 0:
                # Arrived at destination
                self.node = self.transit_dest
                self.state = NodeState.IDLE
            return
        
        # IDLE: make routing decision
        neighbors = graph.neighbors(self.node)
        if not neighbors:
            return
        
        # Read connector deposit counts
        scores = []
        for nb in neighbors:
            eid = graph.edge_id(self.node, nb)
            conn = graph.connectors[eid]
            # Route toward highest MATCHING COUNT (not density)
            matching = sum(conn.deposits.get(g, 0) for g in self.spectrum)
            scores.append(matching)
        
        scores = np.array(scores, dtype=np.float64)
        weights = scores + BASE_WEIGHT
        weights /= weights.sum()
        
        chosen_idx = rng.choice(len(neighbors), p=weights)
        chosen_nb = neighbors[chosen_idx]
        chosen_eid = graph.edge_id(self.node, chosen_nb)
        chosen_conn = graph.connectors[chosen_eid]
        
        # Begin traversal — time proportional to connector length
        self.state = NodeState.IN_TRANSIT
        self.transit_edge = chosen_eid
        self.transit_dest = chosen_nb
        self.transit_remaining = max(1, int(chosen_conn.length))
        
        # First deposit of traversal
        chosen_conn.append(self.group)
```

### Connector

```python
class Connector:
    __slots__ = ('initial_length', 'deposits', 'total')
    
    def __init__(self, geometric_length):
        self.initial_length = geometric_length
        self.deposits = {}    # {group_tag: count}
        self.total = 0
    
    @property
    def length(self):
        return self.initial_length + self.total
    
    def append(self, group_tag):
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
```

### Planet routing (different from star)

The planet needs to route toward the star, not just toward its own
deposits. Two options:

**Option A: Route on TOTAL count (any deposits)**
```python
matching = sum(conn.deposits.values())  # any group, not just spectrum
```
The planet moves toward wherever the most deposits are. Near the star,
that's toward the star. Far from everything, that's toward its own
previous deposits. No extra parameter.

**Option B: Route on matching count for self-binding, total count for
gravity**
```python
self_score = sum(conn.deposits.get(g, 0) for g in self.spectrum)
total_score = sum(conn.deposits.values())
score = self_score + total_score  # or weighted combination
```

**Recommendation: start with Option A (total count).** Simpler, no
parameters. Self-binding emerges because planet deposits are densest
near the planet. Gravity emerges because star deposits are densest
toward the star. Both signals are captured by total count.

---

## Phases

### Phase 0: Traversal Time Validation

Before anything else, verify the traversal-time mechanic works:

- Create a simple graph (20 nodes, chain topology)
- Place one entity node at one end
- Let it traverse connectors and verify:
  - Traversal takes `length` ticks
  - Each tick in transit deposits one quantum
  - Connector length doubles per traversal
  - Second traversal takes 2× as long as first
  - Growth is compound: length after n traversals = initial × 2^n

### Phase 1: Star Equilibrium

**Setup:**
- Graph: random geometric graph, N=5000, k≈24, sphere R=20
- Star: 80 nodes, 4 groups, spectrum = {s0, s1, s2, s3}
- BASE_WEIGHT = 1.0
- Ticks: 100,000 (longer because traversals take time now)

**Expected behavior:**
- Star internal connectors grow from traffic → traversal times increase
- Center nodes slow down (time dilation) → spend more ticks inside
- Surface nodes remain fast → occasionally escape and deposit outward
- The star should reach an equilibrium where:
  - Internal time dilation traps most nodes
  - Surface radiation rate is quasi-steady
  - Mean radius fluctuates within a bounded range

**Measurements:**
1. Star COM and drift
2. Star mean/max radius
3. Mean connector length: internal vs boundary vs external
4. Fraction of star nodes in IDLE vs IN_TRANSIT state
5. Effective tick rate: hops per 1000 ticks (should decrease over time
   as connectors grow)
6. Total deposits per region (internal, boundary, external)

**Success criteria:**
1. Star mean radius < 2× initial (better binding than v4–v6)
2. COM drift < 3.0
3. Internal connector length > boundary connector length (time well)
4. Effective tick rate decreases over time (time dilation confirmed)
5. No runaway: internal connectors grow, but the growth RATE decreases
   because nodes are spending more time in transit

**Critical check: does compound growth run away?**

v1 had runaway because compound extension was exponential and unbounded.
v7's compound growth is SELF-LIMITING: as connectors grow, traversal
takes longer, so fewer traversals happen per unit time. Growth per unit
time = (traversals/time) × (growth/traversal). Traversals/time ∝ 1/length.
Growth/traversal ∝ length. So growth/time ∝ length/length = constant.

Wait — that means length grows LINEARLY in time, not exponentially.
The compound growth per traversal is offset by the longer traversal time.

```
length(t) ∝ t (linear)
traversal_time ∝ length ∝ t
traversals_completed ∝ log(t) (each takes longer)
deposits_per_traversal ∝ length ∝ t
total_deposits ∝ t (linear)
```

Actually let me be more careful. If length = L, one traversal takes L
ticks and adds L deposits (one per tick). So after the traversal,
length = 2L. The next traversal takes 2L ticks, adds 2L deposits,
length = 4L. Then 8L, 16L...

That IS exponential: L(n) = L₀ × 2^n where n = traversal count.
But the TIME to reach traversal n is:
T(n) = L₀ + 2L₀ + 4L₀ + ... + 2^(n-1) × L₀ = L₀ × (2^n - 1)

So L = L₀ × 2^n and T = L₀ × (2^n - 1) ≈ L. Therefore L ∝ T.

**Linear growth in real time.** The same as v4's result (connectors
grew to ~80-97 at 50k ticks — linear). The compound-per-traversal
mechanism produces the SAME linear-in-time growth as v4's simple
one-deposit-per-hop. The self-limiting property works.

But the key difference from v4: **traversal time is now proportional
to length.** In v4, every hop took 1 tick regardless of connector
length. In v7, long connectors take many ticks to traverse. This
creates the time well that v4 lacked.

### Phase 2: Planet Introduction

**After star equilibrium established.**

**Setup:**
- Star from Phase 1 (pre-equilibrated)
- Planet: 5 nodes, groups p0/p1, spectrum {p0, p1}
- Placed at graph distance ~2× star equilibrium radius
- Zero initial velocity (all nodes IDLE)
- Route on total deposit count (Option A)

**Expected behavior:**
1. Planet nodes see star deposits on some local connectors
2. Route toward richest connectors → toward star
3. As planet approaches star, star-facing connectors receive more
   flux → connectors grow → traversal takes longer → effective
   distance increases
4. At some point, growth rate = approach rate → equilibrium
5. Asymmetric overflow on star-facing connectors → tangential routing

**Measurements:**
1. Planet COM distance from star COM (using graph hop distance AND
   Euclidean distance in embedding)
2. Star-facing connector lengths (the ~6 planet connectors pointing
   toward the star)
3. Non-star-facing connector lengths (the ~18 other connectors)
4. Planet node states (IDLE vs IN_TRANSIT, and which direction)
5. Tangential displacement (angular position around star)

**Success criteria:**
1. Planet moves toward star initially (attraction)
2. Planet's star-facing connectors grow faster than others (buffer)
3. Planet COM distance stabilizes or oscillates (binding)
4. ANY tangential motion (even small)

### Phase 3: Quantitative Tests (STRETCH)

Only if Phase 2 shows bound orbits.

1. Force vs distance (vary initial planet distance)
2. Kepler's third law (T² vs r³)
3. Angular momentum evolution
4. Eccentricity vs planet mass (node count)

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity ≈ dimensionality |
| STAR_COUNT | 80 | Star mass |
| PLANET_COUNT | 5 | Planet mass |
| BASE_WEIGHT | 1.0 | Thermal energy (the ONLY free parameter) |

**Derived (not set):**
- Connector growth rate (from traversal mechanics)
- Star radiation rate (from surface geometry)
- Orbital distance (from flux balance)
- Eccentricity (from capacity mismatch)

---

## What's New in v7 vs All Previous Versions

1. **Traversal time ∝ connector length** — nodes don't teleport across
   long connectors. This creates time dilation and makes compound growth
   self-limiting.

2. **IN_TRANSIT state** — nodes are either at a node (IDLE, can make
   routing decisions) or in a connector (IN_TRANSIT, depositing each
   tick). This is the first version with a real model of what happens
   DURING a hop.

3. **No density routing** — route on absolute matching count, not
   density ratio. Avoids the saturation problem.

4. **Geometric bottleneck as orbital mechanism** — the planet has
   limited star-facing connectors. Overflow on those connectors
   creates the equilibrium distance. Not field gradients.

5. **Tangential motion from asymmetric overflow** — different star-facing
   connectors overflow at different rates → planet routes sideways
   toward less-saturated directions.

---

## Traps to Avoid

### Trap 13: Instant Teleportation
v1–v6 all assumed 1 tick per hop regardless of connector length.
This means a connector of length 100 is traversed in the same time as
a connector of length 1. There's no time cost to distance. No time
dilation. v7 fixes this.

### Trap 14: Density Ratio Routing
v6 showed that matching/total saturates to uniform on a finite graph.
Don't use density ratios for routing. Use absolute counts.

### Trap 15: All-Connectors-Face-Star
The planet has k≈24 connectors. NOT all face the star. In 3D geometry,
roughly k/4 ≈ 6 face any given direction. The planet's star-facing
connector count is a GEOMETRIC PROPERTY of the graph, not a parameter.
Don't artificially connect all planet connectors to the star.

### Trap 16: Propagation Engine
There are no propagating flows. There are no directed edge buffers.
Deposits are placed on connectors by entity traversal. They don't
move after being placed. The connector IS the deposits. Don't build
a propagation engine.

---

*v4's ontology + traversal time + geometric bottleneck.*
*The orbit emerges from: limited star-facing connectors, compound
growth from unconsumed deposits, and asymmetric overflow routing.*
*One free parameter: BASE_WEIGHT (thermal motion).*
