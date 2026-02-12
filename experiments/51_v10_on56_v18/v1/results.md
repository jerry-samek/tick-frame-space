# Experiment 51: V10-on-V18 Orbital Dynamics Results

**Date**: 2026-02-11
**Status**: Complete
**Verdict**: The reaction-diffusion PDE was **essential physics**, not scaffolding.

---

## Executive Summary

0 orbits out of 25 process-configurations across 5 experimental runs. The V18 canvas substrate (pure gamma accumulation)
cannot support orbital dynamics. The experiment identifies three specific capabilities that the V10 PDE provided and
that canvas accumulation cannot replicate.

---

## Experimental Runs

| Run | Planets | Speed Limit | Gradient      | Formation | Orbital | Approach A Result             |
|-----|---------|-------------|---------------|-----------|---------|-------------------------------|
| 1   | 100     | 1 (=c)      | Standard      | 200       | 1000    | STUCK (5/5)                   |
| 2   | 100     | 5           | Standard      | 200       | 1000    | ESCAPE (4/5), STUCK (1/5)     |
| 3   | 100     | 1 (=c)      | Smoothed r=30 | 200       | 1000    | COLLAPSE (5/5)                |
| 4   | 100     | 5           | Smoothed r=30 | 200       | 1000    | COLLAPSE (3/5), CHAOTIC (2/5) |
| 5   | 200     | 5           | Smoothed r=30 | 300       | 2000    | COLLAPSE (4/5), CHAOTIC (1/5) |

Approach B (pure V18 gradient-following, no velocity): All 30 ring processes stayed at their initial radii across all
runs. Standard gradient is zero at r=20-50, so they random-walk in place.

---

## Detailed Classification (Run 5 - Best Configuration)

| Label | Start r | Classification | r_mean | r_std | Eccentricity | Revolutions | L_conservation |
|-------|---------|----------------|--------|-------|--------------|-------------|----------------|
| T1    | 30      | COLLAPSE       | 10.9   | 3.8   | 1.000        | 0.76        | 1.219          |
| T2    | 30      | COLLAPSE       | 9.4    | 3.8   | 0.881        | 7.69        | 1.163          |
| T3    | 20      | COLLAPSE       | 10.7   | 4.0   | 1.000        | 1.10        | 1.200          |
| T4    | 50      | COLLAPSE       | 8.8    | 4.2   | 1.000        | 0.48        | 1.265          |
| T6    | 40      | CHAOTIC        | 12.7   | 4.7   | 0.566        | 0.42        | 1.166          |

Notes:

- T2 (radial infall control, zero initial velocity) shows 7.7 "revolutions" but these are random angle-wraps from
  bouncing through the center, not orbits.
- L_conservation ~1.2 means angular momentum standard deviation exceeds the mean. For V10 circular orbits this was <
  0.05.

### Comparison with V10 Benchmarks

| Metric              | V10 Result   | V18 Result         | Gap                              |
|---------------------|--------------|--------------------|----------------------------------|
| Stable orbit rate   | 100% (18/18) | 0% (0/25)          | Total failure                    |
| Circular orbits     | 78%          | 0%                 | No angular momentum conservation |
| Eccentricity (best) | 0.014        | 0.566 (T6 chaotic) | Not comparable                   |
| L conservation      | ~0.05        | ~1.2               | 24x worse                        |

---

## Root Cause Analysis

### Finding 1: Standard gradient has zero range

The planet gamma field extends only to r=7 (cluster radius). `get_gradient()` samples pos+-1, so any position beyond r=8
sees identically zero gradient. Without the smoothed gradient workaround, there is no gravitational force at orbital
distances.

```
Standard gradient at test distances (all runs):
  r=10: 0.0000    r=20: 0.0000    r=30: 0.0000    r=50: 0.0000
```

This alone rules out orbits under standard V18 physics. V10's reaction-diffusion PDE diffused gamma outward, creating a
smooth field extending to infinity.

### Finding 2: Smoothed gradient produces constant-magnitude force

Even with the smoothed gradient workaround (sampling hemispheres of radius 30), the force magnitude saturates at all
orbital distances:

```
Smoothed gradient magnitude (Run 5, 200 planets, sample_radius=30):
  r= 5:  55,593
  r=10:  55,155
  r=15:  54,094
  r=20:  54,092  <-- identical from here
  r=30:  54,092
  r=40:  54,092
  r=50:  54,092
```

Beyond r~15, one hemisphere captures all planet gamma while the other captures none. The asymmetry saturates to a
constant. Combined with sign-only acceleration (`int(sign(grad))` = +-1), every process experiences the same unit force
at every distance.

For circular orbits, the gravitational force must decrease with distance (F ~ 1/r^2 or similar) so that v^2/r = F(r) has
a solution at some equilibrium radius. With F = constant, no such equilibrium exists.

### Finding 3: Integer velocity destroys angular momentum

The combination of:

- Sign-only acceleration (+-1, discards gradient magnitude)
- Per-component speed clamping (vx, vy each in [-max_speed, max_speed])
- Integer position updates (staircase trajectories)

...catastrophically violates angular momentum conservation. L_z = x*vy - y*vx fluctuates wildly with std/mean > 1.0
across all processes. Without angular momentum conservation, circular or elliptical orbits are impossible by definition.

---

## What the PDE Provided (Three Essential Ingredients)

| Ingredient              | V10 (PDE)                                          | V18 (Canvas)                                  | Impact                           |
|-------------------------|----------------------------------------------------|-----------------------------------------------|----------------------------------|
| **Field shape**         | Smooth 1/r potential via Laplacian diffusion       | Hard spike at r<7, void beyond                | No force at orbital distances    |
| **Force magnitude**     | Continuous `accel = k * grad` preserving magnitude | Sign-only `accel = sign(grad)` = constant +-1 | No equilibrium radius possible   |
| **Continuous dynamics** | Float position/velocity, smooth curves             | Integer lattice, staircase trajectories       | No angular momentum conservation |

---

## Approach B: Pure V18 (No Velocity)

All 30 processes (rings at r=20, r=30, r=50) remained at approximately their initial radii after 1000-2000 ticks. They
don't feel the planet because standard gradient is zero at those distances. They don't collapse, don't orbit, and don't
find stable equilibria. They simply random-walk via the jitter mechanism in `CompositeProcess.step()`.

This answers the secondary question: *"Does the canvas substrate produce spatial structure?"* No. Without velocity,
processes are inert at distances beyond the paint cloud.

---

## Verdict: README Outcome #2 + #3

This maps to the README's predicted outcomes:

> **Essential physics** -- the PDE was doing real work that canvas accumulation cannot replicate. Orbits require smooth
> continuous fields.

> **Integer lattice cannot support orbits without continuous math.** The discrete-to-continuous transition is a real
> physics problem, not a detail.

More specifically: **the PDE was providing a properly-shaped gravitational potential.** Canvas accumulation creates a
step-function potential (paint concentrated at r<7), not a smooth well. Even with workarounds to extend the gradient
range, the force law is flat (constant magnitude at all distances), which cannot support orbits.

---

## What This Means for the Project

1. **V18 is not the canonical substrate for orbital dynamics.** The six-parameter PDE cannot be deleted.
2. **The specific missing ingredient is field diffusion.** If canvas accumulation included a Laplacian smoothing step (
   `gamma_new = gamma + alpha * laplacian(gamma)`), the field would extend outward with proper 1/r falloff. This is one
   parameter (alpha), not six.
3. **The integer velocity problem is secondary.** Even with float velocity, constant-force dynamics wouldn't produce
   stable orbits. The field shape must be fixed first.
4. **Theory implication:** "Continuous-seeming trajectories from discrete steps" requires either (a) diffusive field
   evolution producing smooth potentials, or (b) an entirely different mechanism for producing distance-dependent force.

---

## Files

```
experiments/51_v10_on56_v18/
  README.md                  -- Experiment design specification
  results.md                 -- This file
  orbital_process.py         -- OrbitalTestProcess + helpers
  experiment_orbital.py      -- Main experiment runner
  analysis.py                -- Trajectory classification + plots
  results/
    orbital_sl1_standard_p100.json
    orbital_sl5_standard_p100.json
    orbital_sl1_smoothed_p100.json
    orbital_sl5_smoothed_p100.json
    orbital_sl5_smoothed_p200.json
    summary_dashboard.png    -- 6-panel composite figure
    radial_distance.png      -- r(t) curves (key diagnostic)
    trajectories_xy.png      -- X-Y trajectory paths
    gamma_profile.png        -- Radial gamma distribution
    gradient_vs_distance.png -- Standard vs smoothed gradient
    angular_momentum.png     -- L(t) conservation check
    approach_b_histogram.png -- Approach B final distances
```
