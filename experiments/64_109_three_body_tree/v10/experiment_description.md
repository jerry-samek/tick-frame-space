# v10: Macro Bodies — Faking Astronomical Entities on an Expanding Graph

## Status: DESIGN

## Motivation

v1-v9 proved gravity emerges from topology at the sub-atomic scale:

- v1: Attraction on random graphs (no orbits — need dimensionality)
- v2: Orbits on structured lattice with mass as path commitment
- v5: v = c/M from commit-counter model
- v6: v ~ c/M emerges from integer stochastic dynamics (D ~ 1/M²)
- v8: Self-subtraction solves the SNR problem — entities detect each other's field
- v9: Continuous internal direction enables gravitational deflection and three-body scattering

But all experiments run at sub-atomic scale: ~1000 quanta per entity, 8000-node lattice,
stochastic noise dominates, 35K ticks before signal arrives. The dynamics are REAL but NOISY.

**The question**: can we scale this up to astronomical bodies and recover clean Newtonian
dynamics — orbital periods, Kepler's laws, three-body chaos — by "faking" the aggregate
behavior we've proven emerges at micro scale?

**The justification**: we KNOW the rules. We've derived them experimentally:

1. Gamma spreads at c (1 hop/tick)
2. Mass deposits gamma proportional to M (deeper well = stronger gravity)
3. Mass moves at v = c/M (heavier = slower, from commit-counter or stochastic D~1/M²)
4. Self-subtraction: entity follows gradient of OTHER entities' gamma only
5. Continuous internal direction: gradient nudges direction by 1/M per commit (v9)
6. Dimensionality required: structured lattice, not random graph (v1-v2)

At astronomical scale (M ~ 10³⁰), the law of large numbers makes stochastic effects
negligible. The integer quantum field converges to a deterministic continuous field.
We can therefore use floats instead of integers — not as an approximation but as the
correct large-number limit.

## Core Design: What We Fake and What We Don't

### What we fake (justified aggregation):

- **Mass as a number**: body has M = 10³⁰ instead of 10³⁰ individual quanta. Justified:
  v5/v6 showed the aggregate behavior (v=c/M, deposit=M×amount) is the correct emergent
  description.
- **Continuous field**: float gamma instead of integer quanta. Justified: at M=10³⁰,
  binomial distribution ≈ deterministic.
- **Macro-tick**: one simulation tick represents Δt real seconds. All physics scales
  linearly with Δt.

### What we DON'T fake (preserved from micro):

- **Graph topology**: bodies live on graph nodes, move by hopping edges
- **Gamma propagation at c**: field spreads 1 hop per tick, no action at a distance
- **Self-subtraction**: each body ignores its own field for movement
- **Continuous internal direction**: gradient nudges, not overwrites (v9)
- **Expansion**: edges grow each tick (new in v10)
- **Speed limit**: no body moves faster than c = 1 hop/tick

## Architecture

### Graph Substrate

3D periodic lattice, same as v2-v9. But MUCH larger — bodies need room to orbit.

| Parameter | Value | Rationale                                                |
|-----------|-------|----------------------------------------------------------|
| side      | 100   | 10⁶ nodes. Bodies at separation ~40 have room for orbits |
| k         | 6     | Standard cubic lattice (proven in v2-v9)                 |
| periodic  | Yes   | No edge effects                                          |

### Body Model

Each body is a single lattice node with properties:

```python
class MacroBody:
    mass: float  # M — aggregate mass (e.g., 1.0, 0.5, 0.1 in relative units)
    node: int  # Current lattice node
    internal_dir: vec3  # Continuous direction vector (from v9)
    commit_counter: int  # Ticks since last hop
    commit_mass: int  # Ticks between hops = ceil(M / M_ref)
    hops: int  # Total hops taken
    trajectory: list  # (tick, node, coords) history
```

**Speed**: v = c / commit_mass. A body with mass 1.0 might have commit_mass=10 (hops every
10 ticks). A body with mass 0.1 has commit_mass=1 (hops every tick, near c).

**Deposit**: Each tick (whether hopping or not), body deposits `mass × deposit_strength`
gamma at its current node. Heavier body = deeper gamma well. This is the macro equivalent
of v5's "entity sits for M ticks depositing M × amount."

### Gamma Field

Continuous (float64) field on the lattice. Separate tagged array per body (from v8).

```python
tagged[body_id] = float64[N_nodes]  # body's gamma contribution
gamma = sum(tagged[all])  # total field
external[body_id] = gamma - tagged[body_id]  # what body sees
```

**Spread rule** (deterministic limit of v6's stochastic spread):

```python
alpha_eff = alpha / (1.0 + G * gamma)  # self-gravitation slows spread near mass
outflow = alpha_eff * tagged[body_id]
inflow = A @ (outflow / degree)  # uniform to neighbors
tagged[body_id] = tagged[body_id] - outflow + inflow
```

At macro scale, this is clean diffusion with density-dependent coefficient. The mass
creates a potential well. Gamma leaking from the well IS the gravitational field.

### Graph Expansion

**New in v10.** Each tick, the graph expands. Implementation options:

**Option A — Edge weight growth**: Each edge has a weight that grows by factor (1 + H)
per tick. Hop cost = edge_weight ticks. As edges grow, hops take longer → effective
distances increase. Gamma attenuation per hop stays constant → field weakens over
longer effective distances.

**Option B — Node insertion**: Periodically insert new nodes along edges, increasing the
graph size. More physical (graph literally grows) but complex. Gamma spreads to new nodes
→ dilution.

**Option C — Scale factor**: Track a global scale factor a(t) = (1 + H)^t. Coordinates
scale by a(t). Gamma deposit and gradient computation account for scale. Simplest to
implement but least physical.

**Start with Option A** — edge weight growth. It preserves graph topology while naturally
implementing expansion. Bodies experience expansion as "it takes longer to reach neighbors"
which is exactly what cosmic expansion does.

H (expansion rate) is a free parameter. Set it very small (H = 10⁻⁶ per tick) so orbits
are quasi-stable over thousands of ticks, but measurably expand over millions.

### Movement Rule (from v9, adapted)

Each commit window (every commit_mass ticks):

1. Read external gamma at all 6 neighbors
2. Compute gradient unit vector (weighted by external gamma × direction)
3. Nudge internal_direction by (1/commit_mass) × gradient_unit
4. Re-normalize
5. Hop to neighbor with highest dot product with internal_direction
6. Transfer tagged gamma from old node to new node

Between commits: stay put, deposit gamma, field spreads.

### Calibration Against Newton

The key test: do macro body orbits match Newtonian predictions?

**Two-body circular orbit**: Place body A (mass M) at center, body B (mass m) at distance r
with tangential velocity v = sqrt(GM/r). In graph units:

- r = separation in hops
- v = hops per tick = c / commit_mass_B
- G = emerges from field spread (alpha, G_self_gravity)
- Period T = 2πr / v ticks

If the orbit is stable and period matches the Newtonian prediction, we've derived Newton
from topology at macro scale.

**Three-body comparison**: Run the famous figure-8 three-body solution (Chenciner & Montgomery
2000), Lagrange equilateral, and random configurations. Compare against numerical integration
of Newton's equations (scipy RK45 or similar). Measure:

- Orbital period error
- Trajectory divergence (Lyapunov exponent in chaotic regime)
- Energy conservation (should be approximate, not exact — expansion breaks it)
- Angular momentum conservation

### Unit Conversion: Ticks to Physics

Everything in the engine runs in natural graph units:

- Time: ticks
- Distance: hops
- Mass: deposit strength (relative)
- Speed: hops/tick (c = 1)

To convert to SI, multiply by Planck units:

- 1 tick = t_Planck = 5.391 × 10⁻⁴⁴ s
- 1 hop = l_Planck = 1.616 × 10⁻³⁵ m
- 1 mass unit = m_Planck = 2.176 × 10⁻⁸ kg

For macro-ticks (1 tick = Δt seconds):

- Δt = N_planck × t_Planck
- 1 hop = N_planck × l_Planck (if c = 1 hop/tick)

Choose N_planck so that orbital periods come out in reasonable tick counts (thousands,
not 10⁴⁰).

**Or**: work entirely in dimensionless units. Set G_eff = 1 by tuning field parameters.
Then 1 tick = whatever time unit makes the orbit period work. Extract G_eff from the
simulation by measuring acceleration at known distance and mass. Compare:

```
G_measured = a × r² / M
```

If G_measured is constant across distances and masses → Newtonian gravity confirmed.

## Measurements

### Primary: Does Newtonian gravity emerge?

1. **Two-body orbit**: period, eccentricity, stability over 1000+ orbits
2. **Kepler's third law**: T² ∝ r³ across different separations
3. **Force law**: measure acceleration at distances 5, 10, 20, 40 hops. Plot a vs 1/r².
   Linear = Newton confirmed.
4. **Mass dependence**: vary mass ratio. Does acceleration scale with M?

### Secondary: Three-body dynamics

5. **Lagrange points**: Place test body at L4/L5 of a two-body system. Stable?
6. **Figure-8 orbit**: Initialize with Chenciner-Montgomery conditions. How long does it
   survive?
7. **Chaotic scattering**: Random initial conditions, measure Lyapunov exponent.
   Compare with Newtonian numerical integration.
8. **Hierarchical outcome**: Does tight binary + distant third emerge (as in v2)?

### Tertiary: Expansion effects

9. **Orbital decay**: Does H > 0 cause orbits to spiral outward? At what H?
10. **Binding vs expansion**: What mass/separation is needed to overcome expansion?
    This defines the "cosmological constant" boundary.
11. **Hubble flow**: Place many bodies in a large lattice. Do unbound pairs recede
    at v = H × d? (Hubble's law)

### Quaternary: Mathematical extraction

12. **Derive G_eff**: From measured accelerations, extract the effective gravitational
    constant as a function of field parameters (alpha, G_self_gravity, deposit_strength).
13. **Derive force law exponent**: Fit a = k / r^n. Is n = 2.0 exactly?
14. **Derive mass-energy relation**: Body deposits M × amount per tick. Its gamma well
    depth is measurable. Relate well depth to M — is it E = M × c²?

## Success Criteria

### PASS (Newtonian gravity from graph)

- Two-body orbit stable for 100+ periods
- Period scales as T² ∝ r³ (Kepler's third law within 5%)
- Acceleration scales as 1/r² (within 10%)
- Three-body produces chaotic scattering matching Newton

### STRONG PASS (quantitative match)

- G_eff is constant to within 1% across r and M
- Force law exponent n = 2.0 ± 0.05
- Three-body Lyapunov exponent matches Newtonian integration within 20%
- Figure-8 orbit survives 10+ periods

### EXCEPTIONAL PASS (new physics)

- Deviation from 1/r² at very short range (lattice minimum distance)
- Deviation from 1/r² at very long range (expansion competing)
- Clean mathematical expression for G_eff in terms of alpha, G, deposit_strength
- Derivable E = Mc² analog

### FAIL

- No stable orbits (collapse or escape)
- Force law is not 1/r² (e.g., exponential — would mean graph doesn't reproduce Newtonian limit)
- G_eff varies wildly with distance (would mean field propagation doesn't mimic 1/r potential)

## Implementation Plan

### Phase 1: Deterministic continuous field

- Port TaggedGammaField to float64 (remove Binomial/Multinomial sampling)
- Verify: energy conservation, peak stability, self-subtraction
- Single body, no expansion

### Phase 2: Two-body orbit

- Place two bodies at separation r with tangential velocity
- Tune parameters until orbit is stable
- Measure period, verify Kepler

### Phase 3: Force law measurement

- Hold body A fixed (infinite mass), release body B from rest at various r
- Measure infall acceleration
- Plot a vs r, fit power law

### Phase 4: Expansion

- Add edge weight growth (Option A)
- Re-run two-body orbit with H > 0
- Find critical H where orbit unbinds

### Phase 5: Three-body

- Equilateral configuration with tangential velocities
- Random configurations
- Compare against scipy numerical integration of Newton's equations
- Statistical analysis over many seeds

### Phase 6: Mathematical extraction

- Derive G_eff formula from field parameters
- Test across parameter space
- Write up results

## Parameters to Explore

| Parameter    | Range       | Notes                                      |
|--------------|-------------|--------------------------------------------|
| side         | 50-200      | Lattice size (side³ nodes)                 |
| alpha        | 1/k = 0.167 | Speed of light (keep fixed)                |
| G_self       | 0.1-100     | Self-gravitation (controls peak tightness) |
| mass         | 0.1-100     | Body mass (relative units)                 |
| deposit_str  | 0.1-10      | Gamma deposited per tick per unit mass     |
| commit_mass  | 1-100       | Ticks between hops (v = c/commit_mass)     |
| separation   | 10-50       | Initial body separation (hops)             |
| H            | 0-10⁻⁴      | Expansion rate per tick                    |
| smooth_ticks | 10-100      | Field formation ticks before dynamics      |

## Relationship to Theory

This experiment tests the macro-limit of the tick-frame model. If v10 passes:

1. **Newtonian gravity is the macro limit of graph topology** — no force equation needed,
   Newton's laws emerge from count-and-multiply on a lattice.
2. **G is not a free constant** — it's derivable from the graph structure (alpha, k,
   deposit rate). The universe doesn't need a gravitational constant; it needs a
   lattice connectivity and a spread rate.
3. **Three-body problem on a discrete graph may have different chaotic properties** —
   the minimum distance of 1 hop regularizes close encounters. Chaos might be bounded.
4. **Expansion and gravity compete on the same substrate** — the "cosmological constant"
   emerges as the expansion rate H at which binding energy equals expansion work.
5. **Ticks × Planck = physics** — if orbital periods in ticks match real orbital periods
   when multiplied by Planck time, the engine IS a physics calculator.

## Results (February 20, 2026)

### Verdict: PARTIAL PASS — Stable orbit via time dilation, force law ~2.2, no quantization

### Key Achievements

1. **Force law n ≈ 2.2 in mid-field (r=3-20)**. Radial bin analysis on side=80 lattice revealed
   three regimes: near/mid field n≈2.2 (close to Newton's 2.0), far field n≈3.5 (propagation
   horizon — gamma hasn't arrived yet). The 0.2 excess over Newton is lattice anisotropy from
   k=6 cubic connectivity. G only scales magnitude, doesn't change exponent — this is a
   geometric property of the 3D cubic lattice.

2. **Gravitational time dilation stabilizes orbits**. Variable edge length based on local gamma
   density (edge_gamma_scale parameter) creates shorter effective hops near mass. Bodies move
   at constant v = c/M but cover less physical distance in the gamma well. This prevents
   runaway infall and produces stable orbits at r~2 (lattice minimum).

3. **433 stable revolutions** at mean r=1.97 over 30K ticks. Period = 20.3 ticks. No escape,
   no collapse. Orbit shape is a square (4 in-plane directions on k=6 lattice). Multiple
   square sizes visible (r~1 to r~5 excursions).

4. **Bresenham-like hop selection** gives infinite angular resolution on 6-direction lattice.
   Hop accumulator distributes hops across axes proportional to internal_direction, replacing
   argmax neighbor selection that was limited to 45° increments.

5. **Radial/tangential velocity decomposition** confirms orbital mechanics: tangential component
   dominant (~-0.7, clockwise), radial oscillates around ~0. Speed doesn't change — it rotates
   between radial and tangential. This is GR-like (constant speed, curved path) not Newtonian
   (variable speed, straight force).

### What Failed

1. **No orbit quantization**. Only r_start=10 captures to r~2 orbit. Other starting separations
   (4, 6, 8, 12, 15) either escape or scatter chaotically. No multiple shells. The r~2 orbit
   is the lattice floor, not a quantum shell — the body can't go lower.

2. **Equal-mass bodies don't orbit**. Two equal masses create turbulent mutual potential.
   Required asymmetric masses (heavy star + light planet) for stability.

3. **Narrow capture basin**. The coupling/gradient balance only works for a specific starting
   separation. This is parameter tuning, not universal attraction to stable orbits.

4. **Chaotic scattering at all other parameters**. Six parameter sweeps (coupling 0.005-0.15,
   G 0-10, separation 4-15, with/without formation ticks, with/without expansion) all produced
   chaotic scattering with 50-80 reversals and distance ranges of 2-40 hops.

### Physics Insights

**Force is turning rate, not acceleration.** Bodies move at constant v = c/M. Gravity doesn't
change speed — it changes direction. The gradient nudges the internal direction vector.
Stronger gradient = faster turning = tighter curve. This is general relativity's geodesic
motion, not Newtonian F=ma.

**Time dilation as orbital stabilizer.** Without variable edge length, all orbits are unstable
(constant speed + uniform lattice = no restoring force). With gamma-dependent edge compression,
bodies slow in the well and can't collapse further. The stabilization mechanism is purely
geometric — no angular momentum conservation required.

**Expansion is essential for movement.** On a static graph, gamma equilibrates and gradients
vanish. Continuous deposition + expansion creates steady-state gradients. Without expansion,
nothing moves. Expansion may be the fundamental cause of dynamics, not a cosmological
afterthought.

**The lattice shapes orbits.** k=6 cubic lattice produces square orbits (4 in-plane directions).
The force law exponent (2.2 vs 2.0) is a geometric fingerprint of the lattice connectivity.
Different k would produce different orbit shapes and different exponents.

**Speed vector partitioning.** The constant-speed body partitions its velocity between radial
(toward mass) and tangential (perpendicular). Near mass: gradient strong, radial dominates,
tangential shrinks. Far: gradient weak, tangential dominates. This is angular momentum
conservation without explicitly conserving angular momentum.

### Parameter Summary (Stable Orbit Configuration)

| Parameter | Value | Notes |
|-----------|-------|-------|
| side | 40 | 64K nodes |
| k | 6 | Cubic lattice |
| G | 0 | No self-gravitation (continuous deposition provides gradient) |
| star_mass | 100.0 | Heavy, nearly stationary |
| planet_mass | 1.0 | Light, fast |
| star_commit | 100 | v_star = c/100 |
| planet_commit | 5 | v_planet = c/5 |
| gradient_coupling | 0.002 | Calibrated for capture at r~10 |
| edge_gamma_scale | 0.002 | Time dilation strength |
| deposit_strength | 1.0 | Per tick per unit mass |
| separation | 10 | Initial distance (hops) |
| formation_ticks | 5000 | Field establishment before dynamics |
| momentum | perpendicular | Tangential initial velocity |

### Open Questions for v11

1. **k=26 lattice**: Does higher connectivity (a) reduce force law exponent toward 2.0,
   (b) produce circular instead of square orbits, (c) widen the capture basin?

2. **Multiple stable radii**: Can different time dilation curves (nonlinear edge_gamma_scale)
   create multiple stable orbits at different radii? Would require the restoring force to
   have multiple zero-crossings.

3. **Variable speed**: Allow commit_mass to vary with local gamma (body absorbs gamma →
   gets heavier → slows down). Creates mass-speed feedback that might produce Keplerian
   dynamics (speed up at periapsis, slow at apoapsis).

4. **Three-body with time dilation**: Does the stable orbit survive a third body?

5. **Echo gravity**: Replace self-subtraction with self-echo asymmetry detection. Body
   measures deficit in its own returning gamma field caused by other masses. Potentially
   much stronger signal.

6. **Kepler test**: Measure period at multiple stable radii (if achievable). Test T² ∝ r³.

## File Organization

```
experiments/64_109_three_body_tree/
├── experiment_description.md    (updated with v10 section)
├── v1/ - v9/                    (previous versions)
└── v10/                         (macro bodies)
    ├── experiment_description.md (this file)
    ├── macro_bodies.py          (main simulation)
    └── results/
```

## Dependencies

- v6/quantum_gamma.py (base QuantumGammaField → adapt to ContinuousGammaField)
- v6/gamma_field.py (SelfGravitatingField base)
- v9 Entity architecture (continuous internal direction)
- numpy, matplotlib, scipy (for Newtonian comparison)
