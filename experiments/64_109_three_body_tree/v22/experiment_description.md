# v22: Star Formation Before Planet Formation — Emergent Orbital Mechanics

## Date: March 14, 2026

## Status: Complete — handed off to v23

---

## What v21 Taught Us

v21 validated force-on-hop and eliminated velocity runaway. But four fundamental
problems remain that cannot be fixed by parameter tuning:

### Problem 1: Teleported Planet

The planet is placed by hand next to a star that has deposited zero gamma. The
planet escapes before any gravitational field exists. This is not a physics
problem — it is an architectural violation. No amount of warm-up fixes a planet
that was never part of the field.

v21 warm-up run result (tick 5000): d_c dropped from 8.89 to 0.80. The planet
fell in immediately — not because of bad physics but because it had no business
being there before the field formed.

### Problem 2: Preset Velocity

`tangential_momentum=0.1` is guessed, not derived. The correct orbital velocity
at any radius depends on the actual gamma gradient at that radius, which depends
on how long the star has been depositing. The only way to know the right velocity
is to read the field after it has formed.

### Problem 3: Velocity-to-Connector Projection Failure

At ~0.08c with k=24 connectors, the planet's velocity regularly falls into blind
spots in connector coverage. All projections become negative. The planet freezes
or barely moves. v21 diagnostic: ~3-5 hops per 5000 ticks. This is not slow
orbital motion — it is a trapped entity.

### Problem 4: Fixed Hop Threshold

```python
hop_threshold = graph.initial_mean_edge  # never updates
```

Edges expand with H. After 50k ticks at H=0.01, the mean edge is ~5x longer
than initial. The planet needs 5x more displacement before hopping. What looks
like time dilation is mostly this artifact.

---

## The Core Insight: Star Forms First

From RAW 112 and today's theoretical work:

> *An entity moves by spending deposits on connectors. The planet is a deposit
> pattern. It cannot exist before the field that formed it exists.*

The correct physical sequence:

```
1. Seed deposit at center node (tiny, not mass=100000)
2. Star grows via self-reinforcing accumulation over N ticks
3. Field reaches quasi-equilibrium at orbital radii
4. Proto-disk: ring of small deposits at orbital radius
   (NOT a planet object — just elevated field density)
5. Field motion at orbital radius determines inherited velocity
6. Planet coalesces from disk — velocity inherited, not assigned
7. Orbital dynamics emerge or don't
```

---

## v22 Architecture: Four Phases

### Phase 0: Star Formation Diagnostic (MANDATORY FIRST)

Run the star alone. No planet. No planet object. Measure the actual gamma
profile after formation.

```
seed_mass = 1.0  (not 100000 — let it grow)
deposit_rate = 1e-4  (higher than v21 — star needs to accumulate faster)
warm_ticks = 50000  (let field reach equilibrium)

After warm_ticks, measure:
  gamma at r = 2, 4, 6, 8, 10, 15, 20 nodes
  gradient at each r (gamma[r] - gamma[r+1])
  expansion scale factor a(t)
```

**This phase produces the only number that matters:**
The gamma gradient at the target orbital radius. Everything else follows.

### Phase 1: Orbital Velocity Derivation

From the gamma gradient measured in Phase 0, compute what orbital velocity
a test deposit would inherit from the field motion at radius r.

In the framework, the field rotates around the star as gamma spreads outward.
The tangential component of this rotation at radius r IS the natural orbital
velocity. Measure it rather than guessing it.

```
# After Phase 0, probe field rotation:
# Place N test particles at ring of nodes at r_target
# Give them zero initial velocity
# Run 1000 ticks
# Measure mean tangential displacement per tick
# This is v_orbital_natural
```

**If v_orbital_natural ≈ 0 (field doesn't rotate):**
The spreading rule is isotropic and produces no net rotation.
This means proto-disk needs a small tangential asymmetry seed.
The seed amount should be the MINIMUM that produces measurable rotation.

### Phase 2: Proto-Disk Initialization

Do NOT create a planet object. Instead:

```python
# Find all nodes at distance r_target ± delta from star
ring_nodes = [n for n in graph.nodes
              if abs(graph.distance(star_node, n) - r_target) < delta]

# Deposit a small amount of gamma at each ring node
# Proportional to local field density (so it blends naturally)
for n in ring_nodes:
    small_deposit = gamma_at(n) * proto_disk_fraction
    graph.deposit(n, 'disk', small_deposit)

# Add slight tangential asymmetry:
# Nodes on one side of the ring get slightly more deposit
# This seeds rotation without forcing it
```

The proto-disk is NOT a planet. It is a perturbation in the field.

### Phase 3: Coalescing and Orbital Dynamics

Run the simulation. Watch the proto-disk deposits. Three outcomes possible:

**Outcome A — Stable orbit:** Disk deposits coalesce into a denser pattern
that orbits the star. Gamma at the dense node increases relative to neighbors.
The pattern becomes self-sustaining. This is a planet.

**Outcome B — Infall:** Disk deposits spiral inward and merge with star.
Orbital velocity was too low. Star grows. Record the accretion.

**Outcome C — Escape:** Disk deposits drift outward. Orbital velocity was too
high. Record the escape velocity.

All three outcomes are valid physics. Only Outcome A is an orbit.

---

## Displacement Model Fix

The v21 hop model projects velocity onto connectors each tick. This causes
blind spots when velocity direction falls between connectors.

**v22 displacement model:**

```python
# Entity maintains TRUE 3D displacement accumulator (not per-connector)
self.displacement_3d = np.zeros(3)

def advance(self, graph, tick):
    # ... deposit ...

    # Force on hop only (keep from v21)
    if self.just_hopped:
        force = self.compute_force(graph)
        self.velocity += force / self.inertia
        self.just_hopped = False

    # Accumulate displacement in TRUE 3D — no connector projection yet
    self.displacement_3d += self.velocity

    # Hop when 3D displacement magnitude reaches current mean edge length
    # (NOT initial — tracks expansion)
    hop_threshold = graph.avg_edge_length_at(self.node)

    if np.linalg.norm(self.displacement_3d) >= hop_threshold:
        # Find connector MOST ALIGNED with accumulated 3D displacement
        best_nb = None
        best_dot = -float('inf')
        for nb, eidx in graph.node_neighbors[self.node]:
            direction = graph.connector_direction(self.node, nb)
            dot = np.dot(self.displacement_3d / np.linalg.norm(self.displacement_3d),
                         direction)
            if dot > best_dot:
                best_dot = dot
                best_nb = nb

        # Hop to best-aligned connector (even if dot is negative — no blind spots)
        if best_nb is not None:
            # Subtract hop direction from displacement (keep residual)
            hop_dir = graph.connector_direction(self.node, best_nb)
            self.displacement_3d -= hop_dir * hop_threshold
            # ... perform hop ...
```

**Key changes from v21:**
- Displacement accumulates in raw 3D, not projected onto connectors
- Hop threshold is CURRENT mean edge length at node (tracks expansion)
- Best connector selected by alignment with full 3D displacement
- No blind spots — worst case hops in least-bad direction
- Residual displacement preserved in 3D after hop

---

## Parameters

| Parameter | v21 | v22 | Reason |
|-----------|-----|-----|--------|
| star_mass | 100000 | 1.0 (seed) | Star grows from seed |
| planet_mass | 1.0 | NOT SET | No planet object in Phase 0-2 |
| deposit_rate | 1e-5 | 1e-4 | Star needs to build field faster |
| H | 0.001 | 0.00001 | Expansion must not outrun gravity |
| separation | 8-20 | derived | From Phase 0 gamma profile |
| tangential_momentum | 0.1 | derived | From Phase 1 field rotation |
| warm_up | 5000 | 50000 | Field must reach equilibrium |
| hop_threshold | initial_mean_edge | current_mean_edge | Tracks expansion |

---

## Phase 0 Discovery: Field Self-Pinning

**Observed during first Phase 0 runs (March 14, 2026).**

The expand_edges formula suppresses expansion near dense gamma:

```
growth = H / (1 + alpha × (gamma_A + gamma_B))
```

A body that deposits ≈ what it receives maintains high local gamma.
High gamma → large denominator → growth ≈ 0.

**The body pins its own local graph.**

This produces physically correct cosmological behavior automatically:

- **Dense bodies** (stars, planets) deposit continuously → local gamma high →
  local edges barely extend → their neighborhood stays geometrically stable.
  Rulers made of the same matter don't change. From inside, nothing moves.

- **Empty voids** → no deposits → gamma ≈ 0 → denominator ≈ 1 →
  edges extend at full rate H → voids expand freely.

- **Net result**: expansion happens in empty regions. Dense regions opt out
  by maintaining their own field density. This is the observed Hubble flow —
  galaxies don't expand, the space between them does. No additional mechanism
  needed. H as a global constant is already void-weighted expansion.

**For Phase 0 specifically:**

The gradient instability observed at r=10-20 (g10/g5 ratio still climbing at
tick 5000) is the frontier between "pinned by star's deposit field" and
"free expansion region." The ratio climbing toward 0.5 (1/r equilibrium) is
the wavefront of the star's field gradually pinning more distant graph regions
as gamma propagates outward.

This means gradient stabilization time scales with how long the star needs to
extend its pinning radius to the target orbital distance. Running to tick
20000+ is physically motivated — not just numerically — because the star
genuinely needs that long to establish pinning at r=10.

**Implication for parameter H:**

H is currently a stand-in for traversal-driven expansion (RAW 112). The
correct physical mechanism replaces H entirely: connectors extend only when
traversed. In a two-body simulation with one stationary star and a slowly
moving planet, correct expansion ≈ zero. The self-pinning behavior observed
here is the simulation's approximation of that correct behavior — dense
regions resist H automatically through their own field density.

---

## Phase 2 Experimental Results (March 15, 2026)

### Summary of all Phase 2 runs

| Run | Config | ticks/hop | Result |
|-----|--------|-----------|--------|
| v_tan=0.003, continuous fc=1.0 | sub-circular | — | infall→bounce→escape ~t=5000 |
| v_tan=0.00396, continuous fc=1.0 | over-circular | — | coherent outward escape |
| hybrid bootstrap fc=1.0 | over-accelerates | — | frozen at v=0.00420, escape |
| fc=0.01 continuous | wrong regime | — | super-circular escape |
| force-on-hop, v=0.00396 | 20-sided polygon | 611 | escape ~t=8500 |
| k=48 | worse | 1189 | escape ~t=8500 |
| radius=20, r=5 | scale-invariant | 917 | escape ~t=7000 |
| leapfrog N=10, v=0.00396 | **first curved trajectories** | 611 | escape ~t=11000 |

### Key measurements

**F_radial at r=8** (395 nodes sampled):
- F_radial = -0.0000196 (100% inward — clean gradient)
- F_tangential = 0.0000074 (noise floor, ~3× smaller than radial)
- v_circular = sqrt(F_radial × r / inertia) = **0.00396** (inertia=10, fc=1.0)

**Hop interval diagnostic** (k=24, radius=30):
- Mean ticks/hop = 611 ± 49
- Hops per orbit = 20.8 (20-sided polygon — too coarse for stability)
- Each correction bends trajectory ~17° — errors compound

### Scale invariance finding

Increasing k or decreasing radius does not improve orbital stability:

| Config | ticks/hop | hops/orbit | escape tick |
|--------|-----------|------------|-------------|
| k=24, radius=30, r=8 | 611 | 20.8 | ~8500 |
| k=48, radius=30, r=8 | 1189 | 18.0 | ~8500 |
| k=24, radius=20, r=5 | 917 | 21.2 | ~7000 |

**Root cause:** v_circular and hop_threshold both scale with node spacing.
The ratio ticks/hop ≈ hop_threshold/v_circular is scale-invariant — it
cannot be improved by changing graph density or radius alone. This is an
intrinsic property of the architecture, not a parameter problem.

### Leapfrog breakthrough

Decoupling force updates from hops (FORCE_UPDATE_INTERVAL=10) produced the
first genuinely curved trajectories in any v22 run. Best particle (p14)
survived 11945 ticks with velocity declining 30% (0.00396→0.00278). Gravity
actively decelerating outward drift for the first time.

The leapfrog gives ~60 force corrections per orbit vs ~20 with force-on-hop.
This is the correct integrator for orbital mechanics on a discrete graph.

### CRITICAL: Two unfixed bugs in DiskParticle.advance()

All Phase 2 runs including the leapfrog run contained these bugs. The curved
trajectories appeared **despite** them. Fixing both is expected to significantly
improve orbit survival.

**Bug 1 — Frozen hop threshold:**
```python
hop_threshold = graph.initial_mean_edge  # WRONG — never updates
```
As H expands the graph over 20k ticks the threshold becomes progressively
too large. Planet effectively freezes in the second half of each run. Fix:
```python
hop_threshold = graph.avg_edge_length_at(self.node)
```

**Bug 3 — v22 displacement model never implemented:**
The code still uses v21 per-connector projection:
```python
best_proj = max dot product with velocity
self.disp[best_nb] += abs(best_proj)
```
But v22 design spec explicitly replaces this with true 3D displacement
accumulation. The blind-spot problem — where velocity falls between connectors
and all projections are small — was the entire motivation for v22. It was
designed and not implemented. Every Phase 2 run silently lost angular momentum
into connector blind spots.

Both bugs compound: planet barely moves (Bug 1) and loses angular momentum
silently (Bug 3).

### Bug-fix runs (March 15, 2026 — final v22 results)

Both bugs were fixed in DiskParticle.advance():
- Bug 1: `hop_threshold = max(graph.avg_edge_length_at(self.node), initial_mean_edge * 0.5)`
- Bug 3: True 3D displacement via `self.displacement_3d += self.velocity`

Results with both fixes applied:

| Run | v_tan | Best-3 escape | |v| trend | Notes |
|-----|-------|--------------|----------|-------|
| Leapfrog+3D, v=0.00396 | 0.00396 | ~13500 | 0.00396→0.00308 | Hop explosion at boundary (no floor) |
| **Leapfrog+3D+floor, v=0.0035** | **0.0035** | **~16041** | **0.0035→0.00252** | **Best v22 run** |

**Final best result (v_tan=0.0035):**
Particle p17 survived 16041 ticks. Velocity dropped 28% (0.0035→0.00252).
Clear arc trajectories visible. Velocity stabilized at ~0.0027 around tick 12000
— the particle found its natural orbital radius. The gradient at r>20 is too
weak to hold it in the finite domain (radius=30).

**v22 conclusion:** The physics works — leapfrog force + 3D displacement + local
hop threshold produces curved, decelerating trajectories for the first time in
this experiment arc. The remaining failure mode is purely domain size: the
orbit's natural radius exceeds the graph boundary. This motivates v23: larger
graph domain (radius=60, 80k nodes).

### Final v22 architecture (carried to v23)

- Leapfrog force: every 10 ticks, decoupled from hops
- True 3D displacement accumulation (no per-connector projection)
- Local hop threshold with floor (tracks expansion, prevents boundary blowup)
- v_circular derived from measured F_radial, not guessed

---

## Diagnostic Outputs (Required)

### Phase 0 outputs:
```
gamma_profile.csv:  tick, r, mean_gamma, gradient
  - Every 1000 ticks during formation
  - Radii: 2, 4, 6, 8, 10, 15, 20 nodes

star_growth.csv: tick, star_mass, total_gamma, scale_factor
  - Every 100 ticks

phase0_gamma_profile.png: gamma vs radius at multiple times
phase0_gamma_loglog.png: log-log to check power law (should approach 1/r²)
phase0_scale_factor.png: expansion over formation period
```

### Phase 1 outputs:
```
orbital_velocity_profile.csv: r, v_natural, v_keplerian_equivalent
  - Compare measured field rotation to Keplerian prediction

phase1_rotation_map.png: tangential velocity field around star
```

### Phase 2-3 outputs:
```
disk_evolution.csv: tick, disk_total_gamma, disk_peak_node, disk_peak_gamma
  - Track whether disk coalesces, spirals in, or escapes

comoving_distance.csv: tick, d_comoving, d_physical, a_scale
orbital_mechanics.png: comoving trajectory if orbit forms
angular_momentum.png: L_z over time
```

---

## Success Criteria

### Minimum (Phase 0 only):
- [x] Gamma profile reaches r=10 with measurable gradient after 20k ticks ✓
- [x] gamma(r) approaching 1/r power law at equilibrium ✓
- [x] Scale factor stays below 2x during formation (H=0.00001) ✓
- [ ] g10/g5 ratio stabilizes (delta < 0.005 per 1000 ticks) — needs ~27k ticks

### Intermediate (Phase 0-1):
- [x] F_radial measured: -0.0000196, 100% inward, 395 nodes ✓
- [x] v_circular derived: 0.00396 (not guessed) ✓
- [ ] Orbit closes and holds for 50+ hops

### Full success (Phase 0-3):
- [ ] Proto-disk deposit pattern remains coherent for 20k+ ticks
- [ ] Comoving distance oscillates (perihelion/aphelion) — Outcome A
- [ ] Angular momentum maintains consistent sign for 50+ consecutive hops
- [ ] Energy approximate conservation (no monotonic growth or decay)

---

## What Failure Tells Us

**If gamma doesn't reach r=10:** deposit_rate too low or H too high.
Expansion is outrunning field buildup. Lower H or raise deposit_rate.

**If field doesn't rotate:** The spreading rule is isotropic. Proto-disk
needs explicit tangential seed. This is expected and acceptable.

**If proto-disk always spirals in:** Derived orbital velocity is too low
even after measurement. The field rotation underestimates orbital velocity.
Consider whether gamma gradient is sufficient for orbit support.

**If proto-disk always escapes:** Derived orbital velocity is too high.
The field is not concentrated enough to provide centripetal force.

**If g10/g5 never stabilizes:** Star's pinning radius hasn't reached r=10.
Run longer or raise deposit_rate. The field wavefront needs more time.

**If scale invariance persists after bug fixes:** The leapfrog interval N
needs reduction. Try N=5 (double corrections per orbit). Or implement
sub-hop force interpolation.

All failures are information. None are dead ends.

---

## Implementation Notes for Claude Code

### File structure:
```
v22/
  experiment_description.md   (this file)
  star_formation.py           (Phase 0: star grows from seed, measure profile)
  orbital_velocity.py         (Phase 1: derive v_natural from field rotation)
  proto_disk.py               (Phase 2-3: disk + coalescing + orbital dynamics)
  results/
```

### Reuse from v21:
- `RandomGeometricGraph` class — unchanged
- `expand_edges()` — unchanged
- `spread()` — unchanged
- `growth_at_node_external()` — unchanged
- All plotting functions — unchanged

### New in v22:
- `Entity.displacement_3d` — replaces per-connector disp dict
- `Entity.hop_threshold` — uses current mean edge, not initial
- `StarSeed` — simple depositing entity, no velocity, grows mass from accumulation
- `ProtoDisk` — ring of small deposits, not an Entity object
- `measure_gamma_profile()` — radial gamma measurement
- `measure_field_rotation()` — tangential velocity field measurement

### Critical: No planet object in Phase 0 or Phase 1

The planet does not exist until the proto-disk produces a stable coalescing
pattern in Phase 3. Any code that creates a planet Entity before that point
is wrong.

---

## The Deeper Test

If Phase 0-3 succeeds and a planet coalesces naturally from the proto-disk
with inherited orbital velocity — the framework will have demonstrated:

1. Gravity emerges from deposit gradient ✓ (already shown)
2. Star formation is self-reinforcing ✓ (Phase 0)
3. Orbital velocity is determined by field geometry ✓ (Phase 1)
4. Planets form from field density fluctuations ✓ (Phase 2-3)
5. **Orbital mechanics requires no preset initial conditions** ✓ (the key result)

This is the cleanest possible validation of RAW 112's single mechanism claim:
everything that needs to happen, happens from deposits. Nothing is placed by hand.

---

## References

- RAW 112 — The Single Mechanism: Deposits, Movement, and Expansion as One Process
- RAW 113 — Semantic Isomorphism: Same/Different/Unknown
- RAW 111 — Space Is Connections
- RAW 110 — Local Dimensionality
- v21/experiment_description.md — what we learned and why we moved on
- docs/theory/honest_status.md — current validation status

---

*Date: March 14, 2026*
*Updated: March 15, 2026 — Complete. Bug fixes applied, final runs done.*
*Status: Complete — handed off to v23*
*Predecessor: v21 (force-on-hop, warm-up diagnostic)*
*Key departure: No planet object. Star grows from seed. Velocity derived, not assigned.*
*Phase 0 discovery: Field self-pinning — dense bodies resist expansion automatically.*
*Phase 2 discovery: Leapfrog N=10 produces first curved trajectories. Two bugs identified.*
