# Experiment 118 v6: Unified Connector-as-Deposits Model

## Status: READY FOR IMPLEMENTATION
## Date: April 1, 2026
## Author: Tom (theory), Claude (spec)

---

## Why v6 Exists

v5 was a misstep. It introduced a dualism: a fixed immutable graph (the
"empty tube") plus deposits traveling on it. But the theory (RAW 111,
RAW 112) says space IS connections, and connections ARE accumulated
deposits. There is no empty tube. Remove all deposits from a connector
and the connector ceases to exist.

v4 had the right ontology: connector length = deposit count. Every hop
appends a deposit, the connector grows by one unit. The connector IS its
deposits. v4's failure was not the mechanism — it was the routing signal
(too weak, 2:1 ratio, star random-walked and expanded).

v6 combines:
- **v4's ontology**: connector = chain of deposits, length = deposit count
- **Phase 3's routing**: accumulated deposit composition determines routing
- **No propagation engine**: there are no "flows." There are only deposits
  on connectors and entities reading them.

---

## The Core Ontology

### What a connector IS

A connector between node A and node B is a chain of deposits:

```
A —[d₁][d₂][d₃][d₄][d₅][d₆]— B
    ^^^^^^^^^^^^^^^^^^^^^^
    this IS the connector
    there is nothing underneath
```

Each deposit d has a group tag (s0, s1, p0, etc.). The connector's
length is the number of deposits in the chain. Its composition is
the distribution of group tags across those deposits.

### What "radiation" IS

Radiation is not a deposit moving along a connector. It's what a
sequence of star-tagged deposits on a connector LOOKS LIKE when read
by an entity. If a planet reads a connector and finds [s0][s2][s1][s0]
at the near end, it interprets: "star signal from this direction." But
nothing traveled. Each deposit was placed individually by a star node
at a different tick. The deposits are all still there. They're the
connector itself.

RAW 112: "Light propagation is push-driven, not self-propagating. New
deposits displace old ones down connectors like a tube." The deposits
don't move. New ones at one end push the reading position at the other
end. The pattern shifts through the chain, but each deposit is static.

### What "expansion" IS

When a star node hops from A to B and deposits on connector A-B, the
connector grows by one unit. This is not a side effect. This IS
expansion. Space grows because traffic creates new structure. Dense
regions (high traffic) expand faster than sparse regions (low traffic).

This is exactly what RAW 112 §2.7 predicts: dense regions grow (more
deposits from more traffic). The star's internal space expands from
internal traffic. The space between star and planet grows from deposits
placed by star boundary nodes (radiation) and planet nodes (response).

---

## The Single Operation

Each entity node, each tick:

1. **READ**: Examine all k local connectors. For each connector, read
   the deposit composition (how many deposits of each group tag).

2. **ROUTE**: Compute a routing score per connector based on matching
   deposit density. Choose a connector to traverse.

3. **DEPOSIT**: Append one deposit (with this node's group tag) onto
   the chosen connector. The connector grows by 1.

4. **HOP**: Move to the neighbor at the other end of the chosen
   connector.

That's it. One operation. Deposit → hop → connector extends.
The single mechanism of RAW 112.

---

## Routing Signal

### What makes this different from v4

v4's routing used a weak signal: `weight = 1 + recent_other_group`.
This gave a 2:1 preference at best. The star random-walked.

v6 routes on the FULL accumulated deposit composition:

```python
for each connector to neighbor N:
    matching = count of deposits on this connector whose group ∈ my_spectrum
    length = total deposit count on this connector (= connector length)
    
    routing_score = matching / length   # matching deposit DENSITY
```

A connector with 500 star deposits out of 600 total has density 0.83.
A connector with 2 star deposits out of 100 total has density 0.02.
The routing prefers the first: 40:1 ratio, not 2:1.

### The routing decision

```python
weights = np.array([routing_score(c) for c in my_connectors])
weights += BASE_WEIGHT  # thermal motion: prevents total collapse
weights /= weights.sum()
chosen = weighted_random_choice(weights)
```

BASE_WEIGHT is the only free parameter. Physical meaning: thermal
energy preventing gravitational collapse. If BASE_WEIGHT = 0, all
nodes collapse to the single densest connector. If BASE_WEIGHT = ∞,
pure random walk (no binding).

### What spectrum matches what

Same as v4:
- Star groups {s0, s1, s2, s3} are mutually Same
- Planet groups {p0, p1} are mutually Same
- Star and planet groups are mutually Different

A star node routes toward connectors rich in star-pattern deposits.
A planet node routes toward connectors rich in planet-pattern deposits.

---

## Data Structure

### Connector

```python
class Connector:
    __slots__ = ('initial_length', 'deposits', 'total')
    
    def __init__(self, geometric_length):
        self.initial_length = geometric_length  # from graph construction
        self.deposits = {}    # {group_tag: count}
        self.total = 0        # total deposit count
    
    @property
    def length(self):
        return self.initial_length + self.total
    
    def append(self, group_tag):
        """The single mutation operation. Append-only."""
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
    
    def matching_density(self, spectrum):
        """Fraction of deposits matching the given spectrum."""
        if self.total == 0:
            return 0.0
        matching = sum(v for k, v in self.deposits.items() if k in spectrum)
        return matching / self.length
```

Note: `length = initial_length + total`. The initial geometric length
is the "primordial" connector created at graph construction (the
initial condition). Entity traffic adds on top. Over time, the deposit
count dominates and the initial length becomes negligible.

### Reading direction (RAW 125)

An entity at node A reading connector A-B reads the most RECENT deposits
first (nearest to A). For v6 Phase 1, we don't track deposit ordering —
we use the aggregate composition (matching/total). This loses temporal
information but is sufficient for routing.

If Phase 1 works and Phase 2 needs tangential motion, we can add a
"recent window" that tracks the last W deposits separately.

---

## Phase 1: Star Equilibrium

### Setup

- Graph: random geometric graph, N=5000, k≈24, sphere R=20
- Star: 80 nodes placed near origin, 4 groups (s0–s3)
- Star spectrum: {s0, s1, s2, s3}
- BASE_WEIGHT: start with 1.0, adjust if needed
- Ticks: 50,000
- No planet. Star only.

### Each tick, each star node:

```python
def tick(node, group, spectrum, connectors, neighbors, rng):
    # READ: compute routing score per connector
    scores = []
    for c in connectors_at(node):
        scores.append(c.matching_density(spectrum))
    
    scores = np.array(scores)
    weights = scores + BASE_WEIGHT
    weights /= weights.sum()
    
    # ROUTE
    chosen_idx = rng.choice(len(neighbors), p=weights)
    chosen_conn = connectors_at(node)[chosen_idx]
    
    # DEPOSIT (append-only)
    chosen_conn.append(group)
    
    # HOP
    node = neighbors[chosen_idx]
    return node
```

### Measurements (every 500 ticks):

1. **Star COM** and drift from initial
2. **Star mean radius** and max radius
3. **Mean connector length** for:
   - Internal connectors (both endpoints occupied by star nodes)
   - Boundary connectors (one star, one non-star)
   - External connectors (both non-star, within 2 hops of star)
4. **Deposit density profile**: mean matching_density as a function
   of hop distance from star COM node
5. **Routing signal ratio**: at each star node, max(score)/min(score)
   across its connectors — averaged over all star nodes
6. **Total deposits** in the system (should = 80 × tick_number)

### Success criteria:

1. **Star compact**: mean radius < 8 (less than 2× initial ~3.84)
2. **COM stable**: drift < 3.0
3. **Gradient exists**: matching_density at d=0 > matching_density at d=4
   by at least 5:1
4. **Routing directional**: mean signal ratio > 3:1
5. **No runaway**: max connector length < 1000 at 50k ticks
   (v1 reached 1e28; v4 reached 97 — linear growth is fine)

### Expected behavior:

The star should find an equilibrium where:
- Internal routing keeps nodes circulating near center
- Internal connectors grow from traffic (star expands slightly)
- Expansion reduces internal density, which weakens routing signal
- Weakened signal allows more random walks, which spreads deposits
  to boundary connectors
- Equilibrium: internal routing strength = thermal exploration pressure

The star should "breathe" — expand slightly, deposit on outer
connectors, then contract as the center accumulates more relative
density. If this oscillation is damped, we get stable equilibrium.
If undamped, we get a pulsating star. Both are physically meaningful.

### If BASE_WEIGHT needs tuning:

- Star collapses (mean radius → 0): BASE_WEIGHT too low. Try 5.0, 10.0.
- Star expands (mean radius → 14+): BASE_WEIGHT too high. Try 0.1, 0.01.
- Document the sensitivity: how does equilibrium radius depend on
  BASE_WEIGHT? This tells us how "thermal" the system is.

---

## Phase 2: Planet Introduction

Only after Phase 1 succeeds.

### The gravitational reach question

The star's deposit field extends only where star nodes have traversed.
Star nodes mostly stay near the center (if binding works). Occasionally
they random-walk outward, depositing on distant connectors, then return.
These stray deposits form the gravitational field tail.

The planet, placed at distance ~2× star radius, needs to see star
deposits on its local connectors. Whether it does depends on how far
star nodes wander during the warmup phase.

### Setup

- Star from Phase 1 (pre-equilibrated, ~50k ticks of deposit buildup)
- Planet: 5-10 nodes, groups p0/p1, spectrum {p0, p1}
- Planet placed at graph distance ~2× star equilibrium radius
- Zero initial velocity (pure routing)

### Planet routing

Same as star routing, but with planet spectrum. The planet routes toward
connectors rich in planet-pattern deposits (Same → internal cohesion).

But initially, the planet has no deposits on any connectors. Its
connectors are either empty (Unknown) or carry star deposits (Different).
The planet can't route toward Same because there IS no Same signal yet.

**Bootstrap for planet:** On the first few ticks, the planet deposits
on random connectors (all routing scores are 0, so weights = BASE_WEIGHT
for all directions → pure random walk). As it deposits, it creates its
own local field. After a few hundred ticks, it has enough planet-pattern
deposits on nearby connectors to start routing toward its own field
(self-binding).

**Gravitational attraction:** The planet also detects star deposits on
some of its connectors (from the star's random walk tail). These are
Different — they don't match the planet's spectrum. But they're not
Unknown either. They're signal.

For the planet to be attracted to the star, it needs to route toward
the direction with the richest TOTAL deposits (not just matching). The
reasoning: the planet's capacitor charges on ANY deposits, not just
matching ones (RAW 126 — capacitor charges from any incoming energy).
Routing toward the richest deposit source moves the planet toward the
star.

**Combined routing for planet:**

```python
# Self-binding: route toward own deposits (Same)
same_score = matching_density(planet_spectrum)

# Gravitational attraction: route toward any deposits
total_density = total_deposits / connector_length

# Combined signal
routing_score = same_score + GRAVITY_SENSITIVITY * total_density
```

GRAVITY_SENSITIVITY determines how strongly the planet responds to
foreign deposits. If 0 → no gravity, pure self-binding. If large →
strong attraction to star field.

**Wait — is GRAVITY_SENSITIVITY a new free parameter?**

Maybe not. If the planet routes toward the richest deposit field
regardless of type (matching or foreign), then routing_score =
total_deposits / length. No distinction between Same and Different for
routing purposes. The distinction matters for CONSUMPTION (capacitor
fires on Same, charges on Different), but for ROUTING, any deposit is
better than no deposit.

Try: routing_score = total_deposits / connector_length. No extra
parameter. The planet routes toward the densest connector, period.
Self-binding emerges because the planet's own deposits are the densest
nearby. Gravitational attraction emerges because the star's deposit
trail (on distant connectors) is the richest signal at the planet's
location.

### Measurements:

- Planet COM distance from star COM
- Planet mean radius (cohesion)
- Deposit composition on connectors near the planet (star vs planet
  deposits)
- Buffer effect: total deposits on star-planet boundary connectors

### Success criteria:

1. Planet moves toward star (attraction)
2. Planet reaches minimum distance and recedes (buffer overflow)
3. Radial oscillation (bound state)

---

## What v6 Does NOT Have

- No propagation engine (no flows, no directed edges for transport)
- No "fixed graph" (connectors grow from deposits)
- No consumption-by-subtraction (deposits are permanent, append-only)
- No velocity vectors (entities route, don't fly)
- No force computation (routing IS force)
- No decay factor (no time-based weakening)
- No global expansion parameter (expansion comes from traffic)

The ONLY free parameter is BASE_WEIGHT (thermal motion).
One candidate additional parameter for Phase 2: whether routing uses
matching deposits only (pure Same-routing) or total deposits (any
signal). This is a binary choice, not a continuous parameter.

---

## Connection to v4 Results

v4 Phase 1 showed:
- Internal connectors: linear growth to ~80-97 at 50k ticks ✅
  (correct — that's 80-97 deposits, which IS the connector)
- No runaway (v1 had 1e28+) ✅
- Star expanded ~3.8x ⚠️ (routing too weak — v6 fixes this)
- Radiation leaked to boundary ✅ (boundary connectors got deposits)

v6 should reproduce v4's correct results (linear connector growth,
no runaway, radiation leakage) while fixing the routing problem
(star binding through accumulated deposit density routing).

---

## File Structure

```
v6/
├── README.md              (this file)
├── graph.py               (graph with Connector class, edge_deposits)
├── entity.py              (entity nodes with accumulated-deposit routing)
├── phase1_star.py         (star equilibrium test)
├── phase2_planet.py       (planet introduction)
└── results/
```

Runtime: PYTHONUNBUFFERED=1, log every 1000 ticks.

---

*v4 had the right ontology. v5 was a wrong turn. v6 reunifies.*
*The connector IS the deposits. There is nothing underneath.*
