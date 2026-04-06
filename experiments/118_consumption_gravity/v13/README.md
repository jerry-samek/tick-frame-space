# Experiment 118 v13: Accumulated Density + Same Rule + Length Momentum

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Author: Tom (theory), Claude (spec)

---

## Why This Combination Works (When v6 and v12 Alone Didn't)

### v6 failed: accumulated density saturates
Routing on matching_density = deposits / length. But length grew with
deposits (every hop extends connector). So density → deposits/deposits
→ 1.0 everywhere. Uniform. No gradient.

### v12 proved: Same rule prevents length inflation
Star-internal connectors stay at initial length (~2.9). They accumulate
deposits but don't grow. After 50k ticks: 62,000 deposits across
connectors that are still length ~3.

### v12 + v6 = the gradient that never existed before

Star-internal connectors: 1000 Same deposits, length 3.
→ density = 1000/3 = 333

Boundary connectors: 10 deposits, length 3.
→ density = 10/3 = 3.3

**Ratio: 100:1.** This gradient CANNOT saturate because the denominator
(length) is FIXED by the Same rule. The numerator (deposit count) grows
forever. The gradient gets STRONGER over time, not weaker.

This is why v6 failed and v13 should work: v6 had density = N/N → 1.
v13 has density = N/constant → grows without bound near the center.

---

## The Three Mechanisms Combined

### 1. Same/Different Extension Rule (from v12)
- Same deposits don't extend connectors (reinforcement only)
- Different deposits extend connectors (new structure)
- Star-internal connectors stay short
- Boundary connectors grow from mixed traffic

### 2. Accumulated Density Routing (from v6, now viable)
- Each connector has a permanent deposit history
- Routing reads accumulated matching density = deposits / length
- With the Same rule: density gradient is real and growing
- This is the GRAVITATIONAL FIELD — always present, always directional
- NOT dependent on deposits arriving during the charging phase

### 3. Length-Proportional Momentum (new in v13)
- Forward continuation strength = last traversed connector length
- Short connectors (star interior, L≈3) → weak momentum → easily
  deflected by the accumulated density gradient → star binds
- Long connectors (boundary, L grows from Different) → strong momentum
  → hard to deflect → orbital inertia

---

## The Routing Decision

```python
# At routing time, the entity has:
# - arrival_dir: direction from the last hop (normalized)
# - last_traversal_length: length of the connector just traversed
# - All local connectors with their accumulated deposit histories

# 1. FORWARD (inertia): proportional to last connector length
forward = last_traversal_length * arrival_dir  # vector, magnitude = L

# 2. GRAVITY (accumulated field): toward densest matching connector
#    This reads the PERMANENT accumulated state, not live deposits.
#    It is ALWAYS present. No dependency on charging-phase events.
gravity = np.zeros(3)
for each neighbor N:
    eid = edge_id(my_node, N)
    conn = connectors[eid]
    matching = sum(conn.deposits.get(g, 0) for g in my_spectrum)
    density = matching / conn.length  # THIS is now a real gradient
    direction = normalize(pos[N] - pos[my_node])
    gravity += density * direction

# 3. COMBINE
combined = forward + gravity
combined = normalize(combined)

# 4. SCORE outgoing connectors by alignment with combined direction
for i, nb in enumerate(neighbors):
    out_dir = normalize(pos[nb] - pos[my_node])
    alignment = dot(combined, out_dir)
    weights[i] = max(0, alignment) + BASE_WEIGHT
```

### Why this routing works for BOTH star and planet:

**Star interior node (L≈3):**
- Forward = 3 × arrival_dir
- Gravity = sum of density × direction across ~24 connectors. Interior
  connectors have density ~300+ (many deposits, short length). The
  gravity vector points toward the densest region (star center).
  Magnitude: ~300 × 24 directions... but the directions partially
  cancel (roughly isotropic inside). Net gravity magnitude: maybe ~50
  (from the asymmetry between "toward center" and "toward boundary").
- Combined: 3 forward + 50 gravity → gravity DOMINATES. Node curves
  toward center. Star binds.

**Planet on boundary (L≈100 after Different growth):**
- Forward = 100 × arrival_dir
- Gravity: boundary connectors have density ~3 (sparse deposits, some
  Different growth). 24 connectors × density ~3 × directional asymmetry
  → net gravity magnitude ~10-20 toward star.
- Combined: 100 forward + 15 gravity → forward dominates. Planet
  swings past. Orbital inertia.

**Planet at aphelion (L≈3, short local connectors):**
- Forward = 3 × arrival_dir
- Gravity: whatever star deposits exist on local connectors. Maybe
  density ~1-5 per connector. Net toward star: ~5-10.
- Combined: 3 forward + 7 gravity → gravity dominates. Planet curves
  inward. Gravitational capture.

**This automatically produces the orbital dynamics:** gravity dominates
at aphelion (capture), momentum dominates at perihelion (swing-through).
The transition depends on connector length, which depends on the
Same/Different traffic history. No parameters needed for the transition.

---

## The Charging Phase (Simplified from v11)

The charging phase still exists for TWO reasons:
1. **Velocity limit:** the node sits for CHARGING_TIME ticks between
   hops, preventing near-c velocities
2. **RAW 128 idle window:** in-flight quanta can be absorbed during
   this phase

But the charging phase is NO LONGER the primary gravity mechanism.
Gravity comes from the accumulated density field (always present).
The charging phase is a pause, not a data-collection window.

**Deflection from live deposits during charging is REMOVED.** It was
too weak (0.03 deposits per charging phase). The accumulated density
field replaces it entirely. Simpler, stronger, parameter-free.

The tick cycle:

```
ARRIVE at node
    Deposit on traversed connector (Same → no length change, Different → length += 1)
    Record arrival direction and last connector length
    ↓
CHARGE: sit idle for CHARGING_TIME ticks
    (RAW 128 absorption window — not used for routing)
    ↓
ROUTE: read accumulated density on all local connectors
    forward = last_length × arrival_dir
    gravity = sum(density × direction) across all connectors
    combined = forward + gravity
    Choose connector aligned with combined direction
    ↓
TRAVERSE: travel for connector.length ticks
    ↓
ARRIVE → repeat
```

---

## Implementation

### Connector (same as v12)

```python
class Connector:
    def __init__(self, geometric_length):
        self.initial_length = geometric_length
        self.deposits = {}          # {group: count}
        self.total = 0
        self.different_count = 0
    
    @property
    def length(self):
        return self.initial_length + self.different_count
    
    def append(self, group_tag, depositor_spectrum):
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        dominant = self._dominant_family()
        depositor_family = self._family_of(group_tag)
        if dominant is None or depositor_family != dominant:
            self.different_count += 1
    
    def matching_density(self, spectrum):
        matching = sum(v for k, v in self.deposits.items() if k in spectrum)
        return matching / self.length if self.length > 0 else 0.0
    
    def _family_of(self, group_tag):
        if group_tag.startswith('s'): return 'star'
        if group_tag.startswith('p'): return 'planet'
        return 'unknown'
    
    def _dominant_family(self):
        star = sum(v for k, v in self.deposits.items() if k.startswith('s'))
        planet = sum(v for k, v in self.deposits.items() if k.startswith('p'))
        if star == 0 and planet == 0: return None
        return 'star' if star >= planet else 'planet'
```

### Entity Node

```python
class EntityNode:
    STATE_CHARGING = 0
    STATE_ROUTING = 1
    STATE_TRANSIT = 2
    
    def __init__(self, node, group, spectrum, family):
        self.node = node
        self.group = group
        self.spectrum = spectrum
        self.family = family
        self.state = self.STATE_CHARGING
        self.charge_ticks = 0
        self.arrival_dir = None
        self.arrived_from = None
        self.last_traversal_length = 1.0
        self.transit_edge = None
        self.transit_remaining = 0
        self.transit_dest = None
    
    def tick(self, graph, rng):
        
        if self.state == self.STATE_TRANSIT:
            self.transit_remaining -= 1
            if self.transit_remaining <= 0:
                dest = self.transit_dest
                eid = graph.edge_id(self.node, dest)
                conn = graph.connectors[eid]
                
                # Record traversal length BEFORE depositing
                self.last_traversal_length = conn.length
                
                # Deposit on arrival
                conn.append(self.group, self.spectrum)
                
                # Set arrival direction
                self.arrival_dir = graph.pos[dest] - graph.pos[self.node]
                norm = np.linalg.norm(self.arrival_dir)
                if norm > 1e-15:
                    self.arrival_dir /= norm
                
                self.arrived_from = self.node
                self.node = dest
                self.state = self.STATE_CHARGING
                self.charge_ticks = 0
            return
        
        if self.state == self.STATE_CHARGING:
            self.charge_ticks += 1
            if self.charge_ticks >= CHARGING_TIME:
                self.state = self.STATE_ROUTING
            else:
                return
        
        if self.state == self.STATE_ROUTING:
            neighbors = graph.neighbors(self.node)
            if not neighbors:
                self.state = self.STATE_CHARGING
                self.charge_ticks = 0
                return
            
            # GRAVITY: accumulated density field (always present)
            gravity = np.zeros(3)
            for nb in neighbors:
                eid = graph.edge_id(self.node, nb)
                conn = graph.connectors[eid]
                density = conn.matching_density(self.spectrum)
                direction = graph.pos[nb] - graph.pos[self.node]
                norm = np.linalg.norm(direction)
                if norm > 1e-15:
                    direction /= norm
                gravity += density * direction
            
            # FORWARD: proportional to last traversal length
            if self.arrival_dir is not None:
                forward = self.last_traversal_length * self.arrival_dir
            else:
                forward = np.zeros(3)
            
            # COMBINE
            combined = forward + gravity
            norm = np.linalg.norm(combined)
            if norm > 1e-15:
                combined /= norm
            elif self.arrival_dir is not None:
                combined = self.arrival_dir
            else:
                combined = None  # first hop, no signal: random
            
            # Score outgoing connectors
            weights = np.zeros(len(neighbors))
            for i, nb in enumerate(neighbors):
                out_dir = graph.pos[nb] - graph.pos[self.node]
                out_norm = np.linalg.norm(out_dir)
                if out_norm > 1e-15:
                    out_dir /= out_norm
                
                if combined is not None:
                    alignment = np.dot(combined, out_dir)
                    weights[i] = max(0.0, alignment)
                else:
                    weights[i] = 0.0
                
                weights[i] += BASE_WEIGHT
            
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

### Tick order (simplified from v11 — no live deposit detection needed)

```python
for tick in range(TICKS):
    # 1. Process all IN_TRANSIT entities (may arrive and deposit)
    for en in all_entity_nodes:
        if en.state == STATE_TRANSIT:
            en.tick(graph, rng)
    
    # 2. Process CHARGING entities (just count ticks)
    for en in all_entity_nodes:
        if en.state == STATE_CHARGING:
            en.tick(graph, rng)
    
    # 3. Process ROUTING entities (read accumulated field, choose direction)
    for en in all_entity_nodes:
        if en.state == STATE_ROUTING:
            en.tick(graph, rng)
```

No per-tick connector resets needed. No deposits_this_tick tracking.
The routing reads the accumulated state, which is always current.
Simpler than v11/v12.

---

## Phases

### Phase 1: Star Equilibrium

**Setup:** 80 star nodes, 4 groups, 5000-node graph, CHARGING_TIME = 50.

**Prediction:** The accumulated density gradient is STRONG. After 1000
ticks: center connectors have ~100 deposits at length 3 → density ~33.
Boundary connectors have ~5 deposits at length 3 → density ~1.7. Ratio:
20:1. Star-interior nodes see strong inward gravity (density gradient
points toward center). Forward strength ~3 (short connectors). Gravity
~50+ (strong density asymmetry). Gravity dominates. Star binds.

The key ratio: gravity_magnitude / forward_strength. For star interior
this should be >> 1. For boundary it should be > 1 (still binding). Only
for long-connector traversals (planet boundary) should forward dominate.

**Measurements:**
1. Star COM and drift (target < 2.0)
2. Star mean/max radius (target < 8, ideally < 6)
3. Internal connector lengths (should stay ~3, from Same rule)
4. Accumulated density profile: mean density at hop distance d from COM
5. Gravity vector magnitude at interior vs boundary nodes
6. Forward/gravity ratio at interior vs boundary nodes
7. Hop rate (should stay high — short connectors)
8. Same/Different deposit counts

**Success criteria:**
1. Star mean radius < 8
2. COM drift < 2.0
3. Density at center > 10× density at boundary (real gradient)
4. Gravity/forward ratio > 3:1 at interior nodes
5. Internal connectors stay short (< 2× initial)

### Phase 2: Planet Introduction

**After star equilibrium.**

**Setup:**
- Compact star (r < 8) with strong density gradient
- Planet: 5 nodes outside star
- NO tangential kick
- Same CHARGING_TIME = 50

**Prediction:** Planet sees the star's density gradient from its
initial position. Gravity vector points firmly toward star (the only
direction with significant deposits). Planet falls inward.

As planet approaches on boundary connectors: those connectors grow
from Different deposits → planet's forward_strength increases with
each hop → at perihelion, forward_strength is large (long boundary
connectors) → planet swings past.

As planet recedes: local connectors are short → weak forward → gravity
pulls it back.

**Measurements:**
1. Planet COM distance from star COM
2. Angular displacement (the orbit test)
3. Angular coherence (> 0.3 for real orbit)
4. Forward_strength vs distance from star
5. Gravity magnitude vs distance from star
6. Forward/gravity ratio vs distance (should flip from gravity-dominated
   at aphelion to forward-dominated at perihelion)
7. Boundary connector growth (Different deposits)

**The decisive metric:** Does the forward/gravity ratio CHANGE with
orbital phase? If it flips between > 1 (perihelion, momentum) and < 1
(aphelion, gravity), we have a real orbit mechanism.

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass |
| PLANET_COUNT | 5 | Planet mass |
| BASE_WEIGHT | 0.1 | Thermal noise (reduced — direction should dominate) |
| CHARGING_TIME | 50 | Idle ticks per cycle |

**Note:** BASE_WEIGHT reduced from 1.0 to 0.1. With the gravity signal
now being strong (density ~30+ at center), the base weight should be
small relative to the directional signal. If BASE_WEIGHT = 1.0, it
adds ~1 to every connector's weight, which dilutes a direction_score
of ~0.9 into noise. At 0.1, it provides minimal randomness without
drowning the signal.

**No DEPOSIT_WEIGHT parameter.** The deposit influence is built into
the gravity vector through accumulated density. No separate weight
needed.

---

## What's Genuinely Different in v13

**The gravity mechanism reads the permanent accumulated field (v6 style),
not live deposits during charging (v11 style).** This is always present,
always directional, and with the Same rule preventing length inflation,
the density gradient is real and growing.

The charging phase becomes a simple timer (velocity limit + RAW 128
window), not the gravity detection mechanism. The code is simpler. The
physics is stronger.

Three mechanisms, one routing decision:
- **Same/Different rule** → star stays compact, boundary grows
- **Accumulated density** → star's gravity field is always present
- **Length-proportional momentum** → inertia scales with distance traveled

No mechanism fights the others. They unify naturally.

---

*v6's density routing + v12's Same rule + v13's length momentum.*
*The gradient that v6 couldn't produce now exists because Same
prevents denominator growth. The binding that v12 couldn't achieve
now works because the gradient provides the inward pull. The orbital
mechanics that v11 couldn't produce now work because long boundary
connectors provide the forward momentum.*
*Three failures combined into one success. Maybe.*
