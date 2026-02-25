# v19: Smoother Orbits — Velocity Damping and Inertia Scaling

v18 proved self-sustaining gravity works: expansion + radiation + edge-weighted
spread produces real orbital dynamics. But the 3D trajectories show sharp
directional changes — jerky, not smooth.

**Root causes:**
1. Discrete graph (k=12): only 12 force directions per node. Each hop gives a
   completely different neighbor set → force direction jumps abruptly.
2. No velocity damping: velocity accumulates additively without dissipation.
   Speed runs away (|v|: 0.4 → 2.9 over 500K ticks), compounding angular noise.

## New Parameters

### Velocity damping (`--drag`)

```python
self.velocity *= (1.0 - drag)  # applied each tick after acceleration
```

Physical justification: in expanding space, peculiar velocities decay as 1/a(t).
The drag parameter captures this Hubble-drag-like effect. Bodies moving through
an expanding medium should lose kinetic energy to the expanding edges.

- `drag=0.0`: v18 behavior (no damping, backward compatible)
- `drag=0.001`: gentle damping, e-folding time = 1000 ticks
- `drag=0.01`: aggressive damping, e-folding time = 100 ticks

### Inertia scaling (`--inertia-mode`)

- `constant` (default, v18 behavior): inertia stays at `--inertia` value
- `mass`: inertia = current mass (equivalence principle — lighter = more responsive)
- `initial_mass`: inertia = initial mass (constant but mass-scaled)

**Note:** At v18's mass scale (100K), `inertia_mode=mass` makes gravitational
acceleration ~1e-8/tick — bodies barely feel gravity. This mode may need reduced
mass scale or different parameter regime.

## Sweep Design

### Round 1: Drag Calibration
Phase 2 binary, k=12, N=10000, 50K ticks.
```
drag = [0.0, 0.0001, 0.0005, 0.001, 0.005, 0.01]
```

### Round 2: Best Drag × Inertia Mode (9 runs)
```
drag = [best_low, best_mid, best_high]
inertia_mode = [constant, mass, initial_mass]
```

### Round 3: Higher k (3 runs)
```
k = [12, 24, 36]  # with winning drag + inertia_mode
```

### Round 4: Long Validation (1 run)
Winner at N=30000, 200K ticks.

## Smoothness Metrics

New dashboard plot (`phase{N}_smoothness{suffix}.png`):
- Speed |v| vs time — flat = circular orbit
- Comoving distance vs time — regular oscillation = stable orbit
- Out-of-plane fraction |v_z|/|v| — near 0 = planar orbit
- Angular momentum L_z vs time — constant sign = stable orbital plane

## File Structure

```
v19/
  experiment_description.md  (this file)
  macro_bodies.py            (copy v18 + drag + inertia_mode + smoothness plots)
  results/
```

## Base Parameters (from v18)

- N=10000 (sweep), N=30000 (validation)
- k=12 (default), sweep to k=36
- H=0.01, alpha_expand=1.0, G=0.0
- mass=100000, deposit_strength=1e-5
- separation=10, tangential_momentum=0.1
- weighted_spread=True

February 2026

---

## Results Summary

### Round 1: Drag Calibration (Phase 2 binary, k=12, N=10000, 50K ticks)

Drag sweep results: `drag=0.001` was the sweet spot. Lower values (0, 0.0001)
showed speed runaway; higher values (0.005, 0.01) over-damped and killed orbits.

### Round 2: Inertia Mode (Phase 2 binary, drag=0.001)

- `constant` (inertia=1): best — responsive to gravity, stable orbits
- `initial_mass`: inertia=100K → acceleration ~1e-8/tick, bodies barely move
- `mass`: same problem at early ticks, improves as mass decays but too slow

Winner: `drag=0.001, inertia_mode=constant`.

### Round 3: Higher k (Phase 2 binary, drag=0.001, N=10000)

- k=12: baseline jitter, 12 connectors/node
- k=24: noticeably smoother, 24 connectors give better angular resolution
- k=36: marginal improvement over k=24, diminishing returns

Winner: `k=24`.

### Round 4: Star-Planet Validation (Phase 1, drag=0.001, k=24, N=30000)

Best run: `star_k24_30k` — 50K ticks, separation=10.
- Final |v|=0.075, d_comov=0.26, 1981 hops
- Orbit is bound and persistent in comoving coordinates
- But still jagged: speed oscillates 0-0.4, angular momentum flips sign,
  large out-of-plane fraction

### Round 5: Scale Hypothesis — Larger Orbital Separation

**Hypothesis:** Jitter is quantization noise from small orbits. At sep=10 the
orbit circumference is ~81 hops with 24 directions per hop (~4.4° angular
resolution). Increase separation so the orbit spans more hops.

**Runs:**
- sep=50 (N=120K, radius=60, k=24, drag=0.001, 50K ticks): Planet free-falls
  from d_comov=49.78 to ~0.2 by tick 10K. No circular orbit — the gradient at
  sep=50 is too weak for v=0.1 tangential momentum. Planet spirals in and
  bounces chaotically near the star. 2914 hops, 281 reversals. Worse than
  baseline on all smoothness metrics.
- sep=100 (N=240K, radius=120, k=24, drag=0.001): Killed at tick 20K. Same
  inward collapse — d_comov=97.86→0.66 by tick 10K. Even slower progress
  (~32 min per 5K ticks).

**Result: Scale hypothesis disproven.** The jitter is NOT just quantization.
Larger separations fail because:
1. Single-node star has only ~24 connectors in ~24 random directions. The gamma
   gradient is angularly lumpy — strong toward some neighbors, zero in gaps.
2. At sep=50+, the planet sits in the far field where this lumpiness dominates.
   The gradient may point sideways or backwards depending on which connectors
   happen to be nearest.
3. The tangential momentum (v=0.1) was implicitly tuned for the gradient strength
   at sep=10 — not valid at larger distances.

**Key insight:** In real physics, a point mass creates a smooth 1/r field
(Newton's shell theorem). But our single-node star deposits through ~24
connectors in random directions — the angular coverage has holes. The fix
isn't more distance, it's more **angular coverage**: a distributed star
occupying many nodes, depositing through hundreds of connectors in all
directions. Mass spread over volume, not concentrated at a point.

This motivates **v20: Distributed Bodies**.
