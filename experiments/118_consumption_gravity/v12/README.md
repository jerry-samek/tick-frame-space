# Experiment 118 v12: Same Reinforces, Different Extends

## Status: READY FOR IMPLEMENTATION
## Date: April 2, 2026
## Author: Tom (theory), Claude (spec)

---

## The Star Binding Problem (v4–v11)

Every version since v4 has the same issue: the star expands from initial
radius ~3.8 to ~14.5 (3.8× expansion). The star fills 70% of the graph
volume. No deposit gradient survives. Every orbit mechanism we've tested
works in principle but fails because the star is too diffuse.

| Version | Star radius | Why it expanded |
|---------|------------|-----------------|
| v4 | 14.5 | Weak routing (2:1 signal) |
| v5 | 14.5 | Propagating deposits, no gradient |
| v6 | 14.5 | Density saturates on finite graph |
| v7 | 8.5 (frozen) / 12.0 (active) | Time well helps but internal growth still inflates |
| v9 | ~14 | Same as v7 active variant |
| v11 | 14.5 | Forward default carries nodes outward, weak deflection |

**The root cause:** Every hop deposits on the traversed connector. The
connector grows by 1. Star-internal connectors carry the heaviest
traffic (80 nodes hopping internally). They grow fastest. The star's
internal space inflates from its own activity.

**The theoretical fix from RAW 113:**

| Event | RAW 113 meaning | Effect on connector |
|-------|----------------|-------------------|
| **Same** | Follow — no new structure | Reinforcement. Connector doesn't grow. |
| **Different** | Diverge — new structure | Extension. Connector grows by 1. |
| **Unknown** | Write — new frontier | Extension. Connector grows by 1. |

A star node hopping along a star-dominated connector is a **Same** event.
The deposit matches what's already there. It reinforces the existing
pattern. No new structure is created. The connector doesn't grow.

A planet node hopping along a star-dominated connector is a **Different**
event. The deposit diverges from the existing pattern. New structure IS
created. The connector grows.

**This directly solves star binding:** star-internal connectors (all Same
traffic) don't grow. Star nodes hop quickly on short connectors. The star
stays compact. Only boundary connectors with mixed traffic (Different
events) grow, creating the physical distance between star and planet.

---

## The Unified v12 Model

v12 combines all working elements from v4–v11 with the Same/Different
extension rule:

### From v4: Connector = deposits
The connector IS its deposits. Nothing underneath. Length is measured in
deposit units.

### From v7: Traversal time ∝ connector length
Long connectors take proportionally more ticks to traverse. This creates
time dilation.

### From v7: Deposit-on-arrival
One deposit per completed traversal, placed when the entity arrives at
the destination node.

### From v11: Newton's first law (forward default)
Entities continue in their arrival direction unless deflected by incoming
deposits. No deadlock.

### From v11: Charging phase with deflection
Entities sit idle for CHARGING_TIME ticks, accumulating deflection from
nearby deposit events. The deflection vector biases the next routing
decision.

### NEW in v12: Same/Different extension rule
Connectors grow ONLY from Different deposits. Same deposits are appended
to the connector's history (for routing signal purposes) but do NOT
increase the connector's effective length (for traversal time purposes).

---

## Same vs Different: The Extension Rule

### How it works

Each connector tracks two counts:

```python
class Connector:
    def __init__(self, geometric_length):
        self.initial_length = geometric_length
        self.deposits = {}          # {group: count} — ALL deposits
        self.total = 0              # all deposits (for routing signal)
        self.different_count = 0    # only Different deposits (for length)
        self.deposits_this_tick = 0
        self.last_deposit_source = None
    
    @property
    def length(self):
        """Effective length = initial + Different deposits only."""
        return self.initial_length + self.different_count
    
    @property
    def density(self):
        """Total deposits per unit length — the routing signal."""
        return self.total / self.length if self.length > 0 else 0.0
    
    def append(self, group_tag, depositor_spectrum):
        """
        Append a deposit. Same deposits reinforce (no length change).
        Different deposits extend (length += 1).
        
        group_tag: the depositing entity's group (e.g. 's0', 'p1')
        depositor_spectrum: the set of groups the depositor considers Same
        """
        self.deposits[group_tag] = self.deposits.get(group_tag, 0) + 1
        self.total += 1
        self.deposits_this_tick += 1
        
        # Is this deposit Same or Different relative to the connector?
        # Check: does the depositor's spectrum match the dominant type?
        dominant = self._dominant_family()
        depositor_family = self._family_of(group_tag)
        
        if dominant is None:
            # First deposit on this connector — Unknown → extends
            self.different_count += 1
        elif depositor_family != dominant:
            # Different family → new structure → extends
            self.different_count += 1
        # else: Same family → reinforcement → no extension
    
    def _family_of(self, group_tag):
        """Map group tag to entity family."""
        if group_tag.startswith('s'):
            return 'star'
        elif group_tag.startswith('p'):
            return 'planet'
        return 'unknown'
    
    def _dominant_family(self):
        """Which family has the most deposits on this connector?"""
        star_count = sum(v for k, v in self.deposits.items() if k.startswith('s'))
        planet_count = sum(v for k, v in self.deposits.items() if k.startswith('p'))
        if star_count == 0 and planet_count == 0:
            return None
        return 'star' if star_count >= planet_count else 'planet'
    
    def reset_tick(self):
        self.deposits_this_tick = 0
        self.last_deposit_source = None
```

### What this means physically

**Star-internal connectors:** All deposits are star-family. Every deposit
is Same. `different_count` stays 0. `length` stays at `initial_length`.
Traversal time stays short. Star nodes hop quickly. Star stays compact.

**Star-planet boundary connectors:** Both star and planet deposits. When
a star node deposits on a connector that's planet-dominant → Different →
extends. When a planet deposits on a star-dominant connector → Different
→ extends. The boundary grows from both sides. This IS the space between
the two bodies.

**Planet-internal connectors:** All planet-family deposits. Same. No
growth. Planet stays compact too.

**Empty connectors:** First deposit is always Different (Unknown → new
frontier). Subsequent deposits from the same family are Same (reinforce).

### Routing signal uses TOTAL deposits, not just Different

The routing still reads total deposit count (Same + Different). Same
deposits contribute to the routing signal — they make the connector
"richer" in matching deposits, which attracts entities. Same deposits
reinforce the gravitational field without inflating the space.

```python
# Routing score for entity with spectrum S on connector C:
matching = sum(C.deposits.get(g, 0) for g in S)
# Use matching count for routing (includes Same deposits)
routing_score = matching  # or matching / C.length for density
```

This means star-internal connectors accumulate lots of Same deposits →
strong routing signal → strong inward pull. But the connectors don't
grow → no time dilation trap → star nodes stay active.

---

## The Complete Entity Tick Cycle

Same as v11, with the extension rule applied at deposit time:

```
ARRIVE at node (from direction D)
    Deposit on traversed connector:
      - If Same family as connector dominant → no length change
      - If Different family → connector length += 1
    ↓
CHARGE: sit idle for CHARGING_TIME ticks
    Accumulate deflection from nearby deposit events
    (RAW 128 idle window — in-flight quanta can be absorbed)
    ↓
ROUTE: forward (D) + deflection → combined direction
    Score outgoing connectors by direction alignment + deposit count
    Choose connector, begin traversal
    ↓
TRAVERSE: travel along connector for connector.length ticks
    ↓
ARRIVE → repeat
```

### Entity Node Implementation

```python
class EntityNode:
    STATE_CHARGING = 0
    STATE_ROUTING = 1
    STATE_TRANSIT = 2
    
    def __init__(self, node, group, spectrum, family):
        self.node = node
        self.group = group          # e.g. 's0', 'p1'
        self.spectrum = spectrum    # e.g. {'s0','s1','s2','s3'}
        self.family = family        # e.g. 'star' or 'planet'
        self.state = self.STATE_CHARGING
        self.charge_ticks = 0
        self.arrival_dir = None
        self.arrived_from = None
        self.deflection = np.zeros(3)
        self.transit_edge = None
        self.transit_remaining = 0
        self.transit_dest = None
```

The tick logic is identical to v11 EXCEPT the deposit-on-arrival call:

```python
# On arrival after transit:
conn = graph.connectors[eid]
conn.append(self.group, self.spectrum)  # spectrum determines Same/Different
```

Everything else (charging, deflection accumulation, forward+deflection
routing) stays exactly as v11.

---

## Phases

### Phase 1: Star Equilibrium — The Critical Test

**Setup:** 80 star nodes, 4 groups, 5000-node graph. CHARGING_TIME = 50.

**Prediction:** Star-internal connectors don't grow (all Same traffic).
Star nodes hop on short connectors. Mean radius stays near initial
(~3.8) or expands only slightly from random walk diffusion (maybe ~5-6).

**This is the test of the Same/Different extension rule.** If the star
stays compact (r < 6), the rule works. If it expands to ~14 again, the
rule doesn't help and the star binding problem has a different cause.

**Measurements:**
1. **Star COM and drift** (should be < 2.0 with compact star)
2. **Star mean/max radius** (TARGET: < 6, ideally < 5)
3. **Internal connector length** — should stay near initial_length
   because no Different deposits. Track mean and max.
4. **Boundary connector length** — should grow slowly from occasional
   star-node excursions where the node deposits on a non-star-dominated
   connector.
5. **Same/Different deposit counts** — globally, how many deposits were
   classified Same vs Different? For a star-only run, almost all should
   be Same.
6. **Hop rate** — should stay HIGH (short internal connectors → fast
   hops). Compare to v7/v11 where hop rate dropped as connectors grew.
7. **Deflection at boundary nodes** — should point consistently inward
   (toward the dense center with high deposit count).
8. **Deposit gradient** — mean deposit count on connectors at hop
   distance d from star COM. With a compact star, this should show a
   clear peak at d=0, falling off with d.

**Success criteria:**
1. Star mean radius < 6 (was 14.5 in every previous version)
2. COM drift < 2.0
3. Internal connector mean length < 2× initial
4. Hop rate stays approximately constant over the run (no slowdown)
5. Deposit gradient exists (center density > 3× boundary density)

**If this works:** The star binding problem that plagued v4–v11 is
solved. The deposit gradient exists. The gravitational field has
structure. Proceed to Phase 2.

**If star COLLAPSES (r → 0):** The Same rule removes all internal
pressure. Without connector growth, there's nothing preventing total
collapse. May need to keep a small Same-extension rate (e.g., 10% of
Different rate) as "internal pressure." But try zero first.

**If star STILL EXPANDS (r → 14):** The expansion isn't caused by
connector growth. It's caused by the random walk itself — nodes wander
outward even on short connectors. The forward default (v11) might be
carrying them out. May need stronger deflection or reduced BASE_WEIGHT.

### Phase 2: Planet Introduction — The Real Test

**After star equilibrium confirmed (compact, r < 6).**

**Setup:**
- Star from Phase 1 (compact, well-equilibrated)
- Planet: 5 nodes, groups p0/p1, spectrum {p0,p1}, family 'planet'
- Placed at graph distance 15–18 from star COM (well outside the star)
- NO tangential kick
- CHARGING_TIME = 50

**What should happen with compact star + extension rule:**

1. Planet approaches star (routing toward rich deposit field)
2. Planet deposits on connectors it traverses:
   - On star-dominated connectors → Different → connector GROWS
   - This creates physical distance between planet and star
3. Star deposits on boundary connectors when star nodes pass near planet:
   - On planet-dominated connectors → Different → connectors GROW
4. The boundary region expands from BOTH sides depositing Different
5. At equilibrium: planet's approach rate = boundary growth rate
6. The planet is bound at a distance determined by the growth dynamics

**The orbit mechanism:**
- Forward default (inertia) carries planet past perihelion
- Deflection (gravity) from star's deposit field curves the path
- Boundary growth (Different extension) prevents collapse
- The balance should produce a closed or quasi-closed orbit

**Measurements:**
1. Planet COM distance from star COM over time
2. Angular displacement (tangential motion diagnostic)
3. Connector length profile: star-internal, boundary, planet-internal
4. Same vs Different deposit rate over time
5. Per-hop tangential component (the v9 diagnostic, repeated)
6. Deflection magnitude vs distance from star
7. Random walk comparison (same hop rate, no deposits)

**Success criteria:**
1. Planet bound (doesn't escape)
2. Net angular displacement > 500 degrees (better than v11's 1252)
3. Angular coherence > 0.3 (REAL orbit, not random walk)
4. Deflection VARIES with distance (gradient exists with compact star)
5. Boundary connectors grow while internal connectors don't

### Phase 3: Quantitative (STRETCH)

Only if Phase 2 shows coherent orbits.

1. Force vs distance (measure deflection at various radii)
2. Kepler III
3. Angular momentum
4. Energy budget (store/move/radiate ratios)

---

## Parameters

| Parameter | Value | Physical meaning |
|-----------|-------|-----------------|
| N_NODES | 5000 | Graph size |
| TARGET_K | 24 | Local connectivity |
| STAR_COUNT | 80 | Star mass |
| STAR_GROUPS | 4 | Internal star structure |
| PLANET_COUNT | 5 | Planet mass |
| PLANET_GROUPS | 2 | Internal planet structure |
| BASE_WEIGHT | 1.0 | Thermal noise |
| DEPOSIT_WEIGHT | 0.01 | Deposit count influence on routing |
| CHARGING_TIME | 50 | Idle ticks per hop cycle |

**Same parameters as v11.** The ONLY change is the extension rule
inside the Connector class. Everything else is identical.

---

## What's New in v12 (One Thing)

**Same deposits don't extend connectors. Different deposits do.**

That's it. One rule change. Everything else is v11 unchanged.

This rule comes directly from RAW 113:
- Same = follow, no new structure → reinforcement, no growth
- Different = diverge, new structure → extension, growth

It was in the theory from the beginning. We just never implemented it.

---

## Why This Should Work

The star binding problem exists because star-internal traffic inflates
internal connectors. Remove that inflation (Same → no growth), and the
star stays compact. A compact star has:

- **Strong deposit gradient:** 80 nodes in a small volume produce a
  dense deposit field that falls off sharply with distance.
- **Active internal dynamics:** Short connectors → fast hops → frequent
  deposits → strong routing signal → strong deflection for boundary nodes.
- **Clear boundary:** The star has a defined edge (where star nodes
  rarely venture). Beyond the edge, deposits are sparse. The gradient
  is steep.

A planet outside this compact star sees:
- **Strong directional signal:** The star's deposit field is concentrated
  in a specific direction. Not spread across 70% of the graph.
- **Real deflection:** Multiple star-node deposit events per charging
  phase, all from roughly the same direction (toward the star).
- **Different-driven boundary growth:** As the planet approaches, its
  deposits on star-dominated connectors create new structure (Different).
  The boundary physically grows. This prevents collapse.

---

## Traps to Avoid

### Trap 26: Same Extension Leak
Make sure Same deposits truly produce zero extension. Check that
`different_count` is not accidentally incremented for Same deposits.
Log the Same/Different classification counts every measurement interval.

### Trap 27: Dominant Family Flip
If a star-dominated connector receives many planet deposits, the
dominant family flips to 'planet'. Then new star deposits become
Different again and the connector grows from star traffic. This is
correct behavior — it means contested connectors grow from both sides.
Don't try to prevent it.

### Trap 28: Empty Connector First Deposit
The first deposit on any connector should be classified as Different
(Unknown → new frontier → extension). Without this, the very first star
deposits wouldn't extend anything and the initial graph wouldn't evolve.

### Trap 29: Total Collapse
If the star collapses to a point (all nodes on the same node), the
Same rule worked TOO well — there's zero internal pressure. Before
panicking: check if this is stable (all nodes at one point, not moving)
or transient (they converge then disperse). If stable collapse occurs,
add a minimal Same-extension rate or increase BASE_WEIGHT.

---

*Same reinforces. Different extends. The star stays compact.*
*One rule change from v11. Directly from RAW 113.*
*The star binding problem — persistent from v4 through v11 — should
finally be solved by implementing what the theory said all along.*
