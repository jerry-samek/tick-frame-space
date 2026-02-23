# v14 Summary: Connector Bandwidth Gravity

## Date: February 22, 2026
## Status: STRONG PASS

## What v14 Proved

Gravity emerges from one local rule. No forces, no coupling constants, no
background metric. Two equal masses orbit each other from purely local
edge expansion dynamics on a graph where gamma diffuses freely.

## The Rule

```
de/dt = H / (1 + alpha * (gamma_A + gamma_B))
```

Each edge reads ONLY its two endpoints' gamma. That's it. Everything else
follows: the edge profile, the frame rotation, the binding, the orbits.

## The Key Discovery: G = 0

v13 used self-gravitation (G > 0) to concentrate gamma near mass. This
created a pipe problem: gamma piled up within r=0-3, creating a step-function
edge profile. Edges were suppressed near the mass but uniform everywhere else.
A planet at r=10 saw flat edges — no tilt, no binding.

The fix was the opposite of intuition: **remove self-gravitation entirely**.
Set G=0 and let gamma diffuse freely through the graph.

Why this works: the steady-state of 3D diffusion from a continuous source is
gamma proportional to 1/r. This is Result 2 from RAW 170. It's not a tuned parameter — it's
what diffusion does in three spatial dimensions. The 1/r gamma profile produces
a smooth edge length gradient extending across the entire lattice.

With G=0 and deposit_strength=0.001 (scaling gamma into the transition regime
where 1 + alpha*gamma goes from ~1 at vacuum to ~10 near mass), the edge
profile is smooth, extended, and creates meaningful tilt at all radii.

## Architecture

```
Entity deposits gamma at its node (every tick)
  -> Gamma diffuses freely (G=0, no self-gravitation)
  -> Steady state: gamma ~ 1/r from source
  -> Edges grow: de/dt = H / (1 + alpha * (gamma_A + gamma_B))
  -> Near mass: high gamma at both endpoints -> slow growth -> short edges
  -> Far from mass: low gamma -> fast growth -> long edges
  -> Body hops "forward" (Bresenham accumulator, commit cycle)
  -> At new node: frame rotated by edge asymmetry (geodesic frame rotation)
  -> tilt[ax] = -(e_plus - e_minus) / (e_plus + e_minus)
  -> "Forward" now points slightly toward mass
  -> Cascade drift: local edge growth asymmetry displaces body toward mass
  -> Over many hops: orbit emerges
```

Two independent binding mechanisms work together:
1. **Geodesic frame rotation** (from accumulated edge lengths)
2. **Cascade drift** (from per-tick edge growth rate asymmetry via last_growth)

The cascade drift turns out to be the dominant long-term mechanism. Even when
accumulated edge lengths become nearly uniform (edge profile flattens as all
edges grow), the instantaneous growth rate still differs based on local gamma,
which follows the bodies as they deposit each tick.

## Results

### Phase 0: Edge Profile (PASS)

Parameters: G=0, deposit_strength=0.001, mass=1000, side=40, 50K formation + 50K expansion

| Time | e_near | e_far | Ratio |
|------|--------|-------|-------|
| t=12500 | 1.92 | 5.74 | 2.98 |
| t=25000 | 2.82 | 9.86 | 3.50 |
| t=50000 | 4.54 | 16.80 | 3.70 |

Gamma profile: smooth 1/r decay from ~10 at center to ~0.5 at r=19.
Edge profile: smooth variation extending across entire lattice. No step function.

Compare with G=10: step function, all variation within r=0-3, ratio 50:1 but
concentrated. G=0 gives a gentler gradient (3.7:1) but it extends everywhere.

### Phase 1: Star-Planet (PASS)

Parameters: G=0, deposit_strength=0.001, mass=1000, side=40, 50K formation + 50K dynamics

- Tilt at planet (r=10): 0.0103
- Edge profile: e_star=4.44, e_planet=14.85
- **Range: [1.4, 26.9], 69 reversals**
- Planet hops: 10,000 (star stationary, commit=999999)
- Bound chaotic orbit — planet oscillates between close approach and apoapsis

Also tested G=10 (original parameters): Range [1.4, 25.6], 66 reversals.
Both G=0 and G=10 produce binding. G=0 has smoother edge profile but
comparable orbit dynamics.

### Phase 2: Equal Mass Binary — THE ACID TEST (STRONG PASS)

Parameters: G=0, deposit_strength=0.001, mass=100 each, commit=10, separation=10, side=60

- Both bodies deposit gamma equally
- Both shape the metric
- Both respond to the metric
- Opposite tangential initial directions

**50K ticks:** Range [3.2, 39.6], 55 reversals. Both bodies: 5000 hops each.

**200K ticks (overnight):** Range [2.8, 39.7], 61 reversals. Both bodies: 20,000 hops each.
Started at d=10, ended at d=10.0. No sign of unbinding.

Edge profile nearly flat by end of 200K run (189.0-191.0, ~1% variation) yet
bodies STILL bound. Binding sustained by cascade drift from instantaneous
growth rate differences, not accumulated edge asymmetry.

### Phase 3: Three-Body (PASS — no hierarchy)

Parameters: G=0, deposit_strength=0.001, star=1000, planet=1.0, moon=0.1, side=80

- All three bodies remain bound through 50K ticks
- Star-Planet: oscillates 10-42 hops
- Star-Moon: oscillates 2-42 hops
- Planet-Moon: oscillates 6-44 hops
- No hierarchy: moon does not preferentially orbit planet
- All three are bound to star's well, chaotic three-body motion
- Moon's gamma deposit (0.0001/tick) too weak to create a local well

This is a PASS (bound) but not EXCEPTIONAL (no hierarchical orbits).
For hierarchy, the planet would need enough gamma to create its own
resolvable well at the moon's orbital radius.

## Parameters That Matter

| Parameter | Value | Role |
|-----------|-------|------|
| G | 0.0 | No self-gravitation. Let gamma diffuse to natural 1/r |
| H | 0.001 | Expansion rate |
| alpha_expand | 1.0 | How much gamma suppresses edge growth |
| deposit_strength | 0.001 | Scales gamma into transition regime (1+alpha*gamma ~ 1-10) |
| formation_ticks | 50000 | Time for gamma to reach 1/r steady state |

The critical insight: deposit_strength must be tuned so gamma values at
the orbital radius are order 1 (not 1000). This puts the edge growth
denominator in the transition regime where the gamma RATIO matters.

## What Changed from v13

| Feature | v13 (pathfinder) | v14 (connector bandwidth) |
|---------|-----------------|--------------------------|
| Edge rule | de/dt = H/(1+alpha*M/r) | de/dt = H/(1+alpha*(gamma_A+gamma_B)) |
| Information | Global (needs M, r) | Local (two endpoints only) |
| Self-gravitation | G=0.1 best | G=0 (free diffusion) |
| Cascade drift | Negligible | Dominant long-term binding mechanism |
| Equal mass test | Not attempted | STRONG PASS |
| advance() method | Two methods (advance + advance_cascade) | Single advance() using cascade |
| gradient_coupling | Required | Removed entirely |

## What Would Make It Better

1. **Hierarchical orbits.** Planet needs enough gamma to create a resolvable
   local well for the moon. May need higher deposit_strength for planet
   relative to its mass, or longer connector maintenance range.

2. **Cleaner orbits.** Current trajectories are chaotic (bound but not
   elliptical). The k=6 lattice discreteness contributes, but the orbit
   closure gap (total tilt per orbit < 2pi) is the main issue. A steeper
   tilt function or higher-order frame rotation correction could help.

3. **Stable edge profile.** Currently edges grow continuously and the
   accumulated profile flattens over time. A mechanism to reach edge
   length equilibrium (e.g., edge decay, or expansion balanced by
   contraction in high-gamma regions) would give long-term stability.

4. **Performance.** The 216K-512K node grids are slow (formation ~60-150 min).
   Sparse gamma arrays and vectorized spread could help significantly.

## The Physics

The full chain that produces gravity from one local rule:

1. **Entities deposit gamma** at their graph node every tick
2. **Gamma diffuses** through the graph (standard diffusion, G=0)
3. **Steady-state profile** is 1/r — this is 3D diffusion, not a parameter
4. **Edges grow** by de/dt = H/(1+alpha*(gamma_A+gamma_B)) — local two-endpoint rule
5. **Edge profile** emerges: short near mass (high gamma), long far (low gamma)
6. **Bodies hop** forward using Bresenham accumulator and commit cycle
7. **Frame rotation** at each hop: tilt = -(e_plus - e_minus)/(e_plus + e_minus)
8. **Cascade drift** from per-tick growth rate asymmetry adds inward displacement
9. **Result**: bound orbits, including equal-mass binaries

No forces. No M/r. No coupling constants. No hand-set profiles.
Just deposit, diffuse, expand, hop, rotate, drift. Repeat.

## Files

```
v14/
  experiment_description.md    Design document
  connector_funnel_update.md   Analysis of G-concentration problem (superseded by G=0 solution)
  macro_bodies.py              Implementation (~1500 lines)
  summary.md                   This file
  results/
    phase0_edge_expansion.png  Edge profile from G=0 diffusion
    phase1_summary_*.png       Star-planet orbit results
    phase2_summary_*.png       Equal mass binary results (50K and 200K ticks)
    phase3_summary_G0.png      Three-body results
```
