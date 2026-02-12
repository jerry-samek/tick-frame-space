# V18.1 Specification: Canvas with Pressure-Based Gamma Spreading

**Status**: READY FOR IMPLEMENTATION  
**Date**: 2026-02-11  
**Based on**: V18 orbital test failure analysis + pressure spreading insight  
**Goal**: Add one mechanism to V18 canvas — local pressure equalization — and re-run orbital test

---

## Motivation

The V18 orbital test (`experiments/51_v10_on56_v18/results.md`) produced 0/25 orbits. Root cause analysis identified three missing ingredients. All three trace to one absence: **gamma doesn't spread.**

| Problem | Cause | How spreading fixes it |
|---------|-------|----------------------|
| Gradient range = 7 cells | Paint sits in a pile, no influence beyond pile edge | Spreading extends the field to all distances |
| Constant force magnitude | No distance-dependent falloff | Spreading on 3D lattice → 1/r profile (geometric) |
| No smooth potential well | Step-function gamma at pile boundary | Spreading creates gentle hill, not cliff |

The spreading mechanism is NOT Laplacian diffusion added as a PDE. It is **local pressure equalization** — a gamma-rich cell shares with gamma-poor neighbors because asymmetry is unstable.

---

## The One Rule

```
For each cell with gamma > 0:
    For each of its 6 neighbors:
        If neighbor has less gamma:
            Transfer a fraction of the difference.
```

### Formal Definition

```python
def spread_gamma(canvas, spread_fraction=1/6):
    """One tick of pressure equalization.
    
    For every painted cell, check each neighbor.
    If neighbor has less gamma, transfer spread_fraction 
    of the difference from self to neighbor.
    
    spread_fraction = 1/6 is NOT a free parameter.
    It means: divide pressure equally among 6 neighbors.
    On a 3D lattice with 6-connectivity, 1/6 is the only 
    value that treats all directions equally.
    
    This is conservative (total gamma preserved) and local 
    (only adjacent cells interact).
    """
    transfers = {}  # {pos: delta_gamma} accumulator
    
    for pos, gamma_here in canvas.gamma.items():
        if gamma_here <= 0:
            continue
        for neighbor in get_neighbors_6(pos):
            gamma_there = canvas.get_gamma(neighbor)
            if gamma_here > gamma_there:
                transfer = (gamma_here - gamma_there) * spread_fraction
                # Accumulate transfers (don't modify during iteration)
                transfers[pos] = transfers.get(pos, 0.0) - transfer
                transfers[neighbor] = transfers.get(neighbor, 0.0) + transfer
    
    # Apply all transfers at once (synchronous update)
    for pos, delta in transfers.items():
        new_gamma = canvas.get_gamma(pos) + delta
        if new_gamma > 0:
            canvas.gamma[pos] = new_gamma
        elif pos in canvas.gamma:
            del canvas.gamma[pos]  # Clean up zeros
```

### Why spread_fraction = 1/6

- 3D lattice, 6 neighbors
- Equal pressure in all directions = 1/6 per direction
- NOT a tunable parameter — it's geometry
- On a 2D lattice (4 neighbors) it would be 1/4
- The lattice connectivity determines it, not us

### Properties of This Rule

| Property | Value | Why it matters |
|----------|-------|---------------|
| **Conserves total gamma** | Yes — transfers, never creates or destroys | Mass conservation |
| **Local only** | Yes — only adjacent cells interact | Respects speed of light |
| **Propagation speed** | 1 cell per tick maximum | = c on the lattice |
| **Steady-state profile** | 1/r in 3D (Green's function of lattice Laplacian) | Correct gravitational potential |
| **No free parameters** | spread_fraction derived from geometry | Zero tuning |
| **Self-limiting** | Spreading stops when neighbors are equal | Equilibrium exists |
| **Handles spikes** | Steep gradients spread faster than gentle ones | Natural stability |

---

## Integration into V18 Tick Loop

Current V18 tick loop (`evolution_v18.py`):

```python
def evolve_one_tick(self):
    self.tick_count += 1
    # 1. Create new process
    # 2. Each process steps (paint + move)
    # 3. Wake field decays
    # 4. Record statistics
```

New V18.1 tick loop:

```python
def evolve_one_tick(self):
    self.tick_count += 1
    # 1. Create new process
    # 2. Each process steps (paint + move)
    # 3. Gamma spreading (pressure equalization)   ← NEW
    # 4. Wake field update (AFTER spreading)        ← MOVED
    # 5. Record statistics
```

Spreading happens AFTER painting and BEFORE wake update. This means:
- Processes paint at their location (local action)
- Paint spreads to neighbors (pressure equalization)
- Wake field captures the spreading as ∂γ/∂t
- Wake now includes both "new paint" and "spreading of old paint"

---

## Changes to Canvas3D_V18

### New method: `spread_gamma()`

Add to `canvas_v18.py`:

```python
def spread_gamma(self):
    """Pressure-based gamma equalization.
    
    Each cell shares 1/6 of its excess with each neighbor
    that has less gamma. Total gamma is conserved.
    
    This is the mechanism that:
    - Extends gravitational field beyond paint pile
    - Creates 1/r potential profile
    - Prevents lethal gradient spikes
    - Propagates at c (1 cell/tick)
    """
    SPREAD_FRACTION = 1.0 / len(self.NEIGHBOR_OFFSETS)  # 1/6 for 3D
    
    transfers = {}
    
    for pos, gamma_here in list(self.gamma.items()):
        if gamma_here <= 0:
            continue
        for offset in self.NEIGHBOR_OFFSETS:
            neighbor = (
                pos[0] + offset[0],
                pos[1] + offset[1],
                pos[2] + offset[2],
            )
            gamma_there = self.gamma.get(neighbor, 0.0)
            if gamma_here > gamma_there:
                transfer = (gamma_here - gamma_there) * SPREAD_FRACTION
                transfers[pos] = transfers.get(pos, 0.0) - transfer
                transfers[neighbor] = transfers.get(neighbor, 0.0) + transfer
    
    for pos, delta in transfers.items():
        new_val = self.gamma.get(pos, 0.0) + delta
        if new_val > 1e-10:
            self.gamma[pos] = new_val
            self._update_bounds(pos)
        elif pos in self.gamma:
            del self.gamma[pos]
```

### No other changes to canvas

- `get_gradient()` works unchanged (reads neighbor gamma, which is now smoother)
- `get_wake()` works unchanged (wake computed after spreading)
- `paint_imprint()` works unchanged (processes still paint normally)
- Sparse storage still works (spreading adds nearby cells but not distant ones)

---

## Experiment: Re-run Orbital Test on V18.1

### Phase 0: Verify Field Profile (ticks 0–500)

Same as original test: 100-200 planet processes at origin, let them paint and cluster.

**NEW measurement**: After 500 ticks, measure γ(r) profile.

Expected with spreading:
```
r=1:  high gamma (near source)
r=5:  moderate gamma
r=10: measurable gamma (was ZERO in V18)
r=20: measurable gamma (was ZERO in V18)
r=30: nonzero gamma (was ZERO in V18)
```

**Key check**: Does γ(r) approximate 1/r?
- Plot γ(r) on log-log scale
- Fit power law: γ ~ r^(-n)
- Target: n ≈ 1.0 (±0.3 acceptable for integer lattice)

If γ(r) doesn't extend beyond r=10, increase formation ticks (spreading propagates at 1 cell/tick, so 500 ticks = 500 cells maximum range).

### Phase 1: Orbital Test (ticks 500–5000)

Re-run exact same configurations from V18 test:

| ID | Start r | Initial velocity | 
|----|---------|-----------------|
| T1 | (30,0,0) | (0,1,0) tangential |
| T2 | (30,0,0) | (0,0,0) radial infall control |
| T3 | (20,0,0) | (0,1,0) closer orbit |
| T4 | (50,0,0) | (0,1,0) farther orbit |
| T5 | (30,0,0) | (0,0,1) out-of-plane |
| T6 | (40,0,0) | (0,1,0) medium distance |

Use OrbitalTestProcess from original experiment (Approach A with integer velocity).

### Phase 2: Integer Velocity Fix (if Phase 1 fails on Finding 3)

If the field profile is correct (1/r) but orbits still fail due to integer velocity:

Replace sign-only acceleration with proportional acceleration:

```python
# OLD (V18 test): discards magnitude
accel = tuple(int(np.sign(g)) for g in grad)

# NEW: preserve magnitude, scale by coupling
grad_mag = sqrt(sum(g*g for g in grad))
if grad_mag > 0:
    # Normalize direction, scale by magnitude
    # Use fractional accumulator for sub-integer acceleration
    self.velocity_accumulator = tuple(
        va + g / grad_mag * min(grad_mag, 1.0)
        for va, g in zip(self.velocity_accumulator, grad)
    )
    # Integer velocity from accumulator (when accumulator crosses integer)
    actual_velocity = tuple(int(va) for va in self.velocity_accumulator)
    self.velocity_accumulator = tuple(
        va - av for va, av in zip(self.velocity_accumulator, actual_velocity)
    )
    self.velocity = tuple(
        v + av for v, av in zip(self.velocity, actual_velocity)
    )
```

This preserves integer positions but allows sub-integer acceleration to accumulate over multiple ticks. Effectively: fractional forces build up until they're strong enough to cause an integer velocity change.

**Only use Phase 2 if Phase 1 shows correct field profile but angular momentum violation.**

---

## Success Criteria

### Minimum success (field validation):

- [ ] γ(r) extends to r=50+ after 500 formation ticks
- [ ] γ(r) power law exponent n ∈ [0.7, 1.5] (approximately 1/r)
- [ ] Gradient magnitude decreases with distance (not constant)
- [ ] Gradient at r=30 is nonzero and less than gradient at r=10

### Full success (orbital dynamics):

- [ ] At least 1 process completes 2+ revolutions
- [ ] At least 1 process with eccentricity < 0.5
- [ ] Angular momentum conservation: std/mean < 0.5 (was 1.2 in V18)
- [ ] Radial infall control (T2) behaves differently from tangential processes

### Comparison with V10 (`experiments/51_emergent_time_dilation/v10/RESULTS.md`):

| Metric | V10 | V18 (failed) | V18.1 target |
|--------|-----|--------------|--------------|
| Orbit rate | 100% | 0% | ≥ 50% |
| Circular orbits | 78% | 0% | ≥ 1 |
| L conservation | ~0.05 | ~1.2 | < 0.5 |
| Free parameters | 6 | 0 | 0 |

---

## What Each Outcome Means

### If V18.1 produces orbits with spreading (Phase 1):
- **The PDE was providing diffusion. Diffusion is pressure equalization. Pressure equalization has zero free parameters.**
- V18.1 becomes the canonical substrate. Six PDE parameters eliminated permanently.
- Paper: "Orbital dynamics from pure gamma accumulation with local pressure equalization."

### If field profile is correct but orbits fail (needs Phase 2):
- Spreading solves the field problem. Integer velocity is the remaining issue.
- Fractional accumulator solves it mechanically. Question becomes: is sub-integer acceleration physically justified?
- Still a strong result: 6 parameters → 0, with one engineering fix for lattice discretization.

### If field profile is wrong (doesn't reach 1/r):
- Spreading rate 1/6 per tick may be too slow for the formation timescale.
- Try: more formation ticks (1000, 2000), more planet processes (500, 1000).
- If still wrong: the lattice geometry doesn't produce the right Green's function. Fundamental problem.

### If field profile is right but force still constant:
- Gradient computation (`get_gradient` sampling pos±1) may be too local.
- Spreading creates the field, but single-cell finite difference can't see it.
- Try: multi-scale gradient (sample at pos±1, pos±3, pos±10, weight by distance).

---

## Files to Create / Modify

```
experiments/51_v10_on56_v18/
  v18_1/
    README.md                    ← This specification
    canvas_v18_1.py              ← Canvas3D_V18 + spread_gamma() method
    experiment_orbital_v18_1.py  ← Re-run orbital test on V18.1
    analysis_v18_1.py            ← Compare V18 vs V18.1 vs V10
    results/                     ← Output directory
```

### Import from existing:
- `experiments/56_composite_objects/v18/canvas_v18.py` → extend with spread_gamma()
- `experiments/56_composite_objects/v18/process.py` → use CompositeProcess unchanged
- `experiments/51_v10_on56_v18/orbital_process.py` → use OrbitalTestProcess unchanged
- `experiments/51_v10_on56_v18/analysis.py` → extend for comparison plots

### Forbidden imports (same as V18 test):
```python
# NONE of these may appear:
from scipy.ndimage import laplace       # No external PDE
from scipy import anything              # No scipy at all
import math; math.sqrt(1 - v**2/c**2)  # No Lorentz factor
# No analytical gamma formulas
# No predefined gravitational profiles (1/r, Schwarzschild, etc.)
# If 1/r emerges from spreading, great. If it doesn't, that's data.
```

---

## Key Philosophical Points for Implementation

1. **spread_fraction = 1/6 is geometry, not physics.** Don't parameterize it. Don't make it configurable. It's 1/(number of neighbors). Period.

2. **Spreading is conservative.** Total gamma in the system must be exactly preserved every tick. Add an assertion in tests: `sum(gamma_before) == sum(gamma_after)` (within float tolerance).

3. **Spreading happens synchronously.** Compute ALL transfers first, apply ALL at once. Don't update cells during iteration — that makes the result order-dependent, which violates the substrate principle of no preferred direction.

4. **The 1/r profile is a prediction, not a target.** If spreading produces 1/r^1.5 or 1/r^0.8, that's the actual physics of the model. Don't tune to match Newton. Measure what emerges and report honestly.

5. **Spreading IS the propagation of influence.** It moves at 1 cell/tick = c. This is not a coincidence — it's the substrate speed limit. Test this: inject a sudden gamma spike and measure how fast the spreading front moves. It should be exactly 1 cell/tick.

---

## One Sentence Summary

**V18.1 adds one mechanism to V18 — "if your neighbor has less gamma than you, share 1/6 of the difference" — and tests whether this single rule replaces the entire six-parameter reaction-diffusion PDE for orbital dynamics.**
