# Experiment: Orbital Dynamics on V18 Canvas Substrate

**Codename**: The Scaffolding Test  
**Priority**: CRITICAL — This is the single most informative experiment the project can run right now.  
**Substrate**: V18 (Canvas3D_V18 + CompositeProcess)  
**Date**: February 2026  
**Author**: Claude (audit role), to be implemented via Claude Code

---

## The Question

**Do stable orbits emerge from the V18 canvas substrate using only gradient-following and skip-based time dilation — without the reaction-diffusion PDE that v10 relied on?**

This experiment determines whether the six-parameter reaction-diffusion field dynamics in v10 (α, γ, scale, R, D, E_max) were:

1. **Scaffolding** — temporary support structure that can be removed. The canvas accumulation alone produces a field that supports orbits. *(Best case)*
2. **Essential physics** — the PDE was doing real work that canvas accumulation cannot replicate. Orbits require smooth continuous fields. *(Important negative result)*
3. **Partially redundant** — some PDE features emerge from canvas accumulation, others don't. *(Most likely — tells us exactly what's missing)*

---

## Why This Matters

V10 showed 100% orbital success with 78% circular orbits. But v10's gamma field came from:

```
L[t+1] = L + dt × (α∇²L + S − γL²)     ← reaction-diffusion (scipy Laplacian)
E[t+1] = min(E_max, E + dt × (R − D×L))  ← regeneration-drainage
γ_grav  = 1 / (capacity_from_load × capacity_from_energy)
```

V18's gamma field comes from:

```
γ[pos] += 1    ← process paints at position
```

That's it. No diffusion. No damping. No regeneration. No energy field. The field is just accumulated paint. If orbits still emerge from this, the reaction-diffusion was never the physics — it was numerical smoothing that the discrete accumulation provides naturally at sufficient density.

---

## Experimental Setup

### Phase 0: Planet Formation (ticks 0–500)

Before testing orbits, we need a gamma mass to orbit around. Create it the V18 way:

- **500 SimpleDegenerateProcess instances** created at/near origin (0,0,0)
- Each process paints γ += 1 per tick at its position
- Processes follow gradient toward each other → cluster at origin
- After 500 ticks: dense gamma concentration at center

**Measurement at end of Phase 0:**
- Total gamma at center cluster
- Radial gamma profile γ(r) — does it have a gradient suitable for orbits?
- Gradient magnitude vs distance — is it smooth or spiky?

**Critical check**: If the gamma profile is too spiky (integer steps, no smoothing), orbits may be impossible. This would immediately tell us that the PDE's diffusion was essential — it was providing field smoothness that discrete paint cannot.

### Phase 1: Orbital Test (ticks 500–5000)

Inject test processes at various distances with tangential velocity.

**Problem: V18 processes don't have velocity.** The current `CompositeProcess.step()` moves one integer cell per tick via gradient-following. There's no velocity vector, no momentum, no inertia. A process released tangentially will simply turn and walk toward the gradient.

This is itself a critical finding. V10 entities had continuous position and velocity vectors updated by `acceleration = k × ∇γ`. V18 processes have integer position and no velocity. **You can't orbit without inertia.**

**Two approaches:**

#### Approach A: Add Minimal Velocity to V18 (Conservative)

Extend `CompositeProcess` with an integer velocity vector:

```python
class OrbitalTestProcess(CompositeProcess):
    def __init__(self, ..., velocity=(0,0,0)):
        super().__init__(...)
        self.velocity = velocity  # integer steps per tick
    
    def step(self, canvas):
        # 1. Read gradient
        grad = canvas.get_gradient(self.center)
        
        # 2. Gradient modifies velocity (integer acceleration)
        #    This is the v10 rule on integer lattice
        accel = tuple(int(np.sign(g)) for g in grad)
        self.velocity = tuple(v + a for v, a in zip(self.velocity, accel))
        
        # 3. Speed limit: |v| ≤ 1 cell/tick (c = 1)
        speed_sq = sum(v*v for v in self.velocity)
        if speed_sq > 1:
            # Normalize to unit speed (pick dominant axis)
            max_axis = max(range(3), key=lambda i: abs(self.velocity[i]))
            self.velocity = tuple(
                int(np.sign(self.velocity[i])) if i == max_axis else 0
                for i in range(3)
            )
        
        # 4. Skip check (time dilation from local gamma)
        gamma_local = canvas.get_effective_gamma(self.center, local_radius=3)
        if gamma_local * SKIP_SENSITIVITY >= 1.0:
            self.skips_count += 1
            return True  # skip but survive
        
        # 5. Move by velocity
        self.center = tuple(c + v for c, v in zip(self.center, self.velocity))
        
        # 6. Paint at new position
        canvas.paint_imprint(self.process_id, {(0,0,0): 1.0}, self.center)
        
        self.acts_count += 1
        self.age_ticks += 1
        return True
```

**Criticism of Approach A**: We're adding velocity and acceleration back, which is physics we claim should emerge. But v10 did the same thing — the question is whether the *field shape* from canvas accumulation can support orbits given Newtonian-style dynamics.

#### Approach B: Pure V18 — No Velocity (Radical)

Use only the existing V18 `step()` with gradient-following and skip. Don't add velocity. Instead, test whether **clustering geometry** differs from simple collapse — i.e., do processes find stable radii rather than all falling to center?

This is the purer test but answers a different question: "Does the canvas substrate produce spatial structure?" rather than "Does it produce orbits?"

**Recommendation: Run both.** Approach B first (5 minutes to set up, uses existing code), then Approach A.

---

### Test Configurations

**Planet**: 500 processes, clustered at origin, 500 ticks of pre-evolution

**Orbital test processes** (Approach A, injected at tick 500):

| ID | Starting position | Initial velocity | Expected behavior |
|----|------------------|------------------|-------------------|
| T1 | (30, 0, 0) | (0, 1, 0) | Circular orbit attempt |
| T2 | (30, 0, 0) | (0, 0, 0) | Radial infall (control) |
| T3 | (20, 0, 0) | (0, 1, 0) | Closer orbit (stronger field) |
| T4 | (50, 0, 0) | (0, 1, 0) | Farther orbit (weaker field) |
| T5 | (30, 0, 0) | (0, 0, 1) | Out-of-plane orbit |
| T6 | (40, 0, 0) | (0, 1, 0) | Medium distance |

Note: positions are integer cells from origin. Velocity (0,1,0) means 1 cell/tick tangential = c. May need slower speeds — but on integer lattice, 1 cell/tick IS the minimum nonzero speed. This is itself a constraint worth investigating.

**Pure V18 test** (Approach B):

| ID | Starting position | Setup |
|----|------------------|-------|
| B1–B10 | Ring at r=30 | 10 processes equally spaced on ring |
| B11–B20 | Ring at r=20 | 10 processes at closer ring |
| B21–B30 | Ring at r=50 | 10 processes at outer ring |

Question: Do they all collapse to center, or do some find stable radii?

---

## Measurements

### Per-tick tracking (every tick):

For each test process:
- Position (x, y, z)
- Distance from origin r = |pos|
- Velocity (if Approach A)
- Skip/act status
- Local gamma at position
- Local gradient magnitude at position

### Derived metrics (computed post-run):

- **r(t)** trajectory — distance from origin over time
- **Orbital classification**: circular (r stable), elliptical (r oscillates), collapsing (r → 0), escaping (r → ∞), other
- **Eccentricity** (if oscillating): e = (r_max − r_min) / (r_max + r_min)
- **Orbital period** (if oscillating): ticks per radial cycle
- **Angular momentum**: L = r × v_tangential — is it conserved?
- **Gamma profile**: γ(r) at start of orbital test — what does the field look like?

### Success Criteria

| Outcome | Criterion | What it means |
|---------|-----------|---------------|
| **ORBIT** | r oscillates around stable value, entity completes ≥2 full revolutions | Canvas substrate supports orbital dynamics |
| **STABLE RADIUS** | r converges to nonzero value (no oscillation required) | Weaker but still interesting — equilibrium exists |
| **COLLAPSE** | r → 0 monotonically | Field too steep, no centrifugal barrier on discrete lattice |
| **ESCAPE** | r → ∞ monotonically | Field too weak at test distance |
| **CHAOTIC** | r fluctuates wildly, no pattern | Discrete lattice + integer velocity = no stable dynamics |

### Comparison with V10

| Metric | V10 result | V18 target | Notes |
|--------|-----------|------------|-------|
| Stable orbit rate | 100% (18/18) | ≥1 orbit | Even one orbit is a win |
| Circular orbits | 78% (14/18) | Any | Integer lattice makes circles unlikely |
| Eccentricity (circular) | 0.014–0.095 | < 0.5 | Relaxed — discrete lattice is harder |
| Time to stabilize | ~500 ticks | ~1000 ticks | Allow more time for integer dynamics |

---

## Expected Difficulties

### 1. Integer Velocity Problem

On a continuous grid (v10), an entity at r=30 with v=0.3c traces a smooth circle. On an integer lattice (v18), velocity is (0,1,0) or (1,0,0) — no fractions. This means:

- Minimum nonzero speed = 1 cell/tick = c
- No slow orbits possible unless we use skip-based effective velocity
- Trajectory is a staircase, not a curve

**Possible resolution**: Use skip mechanism as velocity modulator. Process with velocity (0,1,0) that skips 70% of ticks has effective speed 0.3c. This naturally connects time dilation to effective velocity — which is exactly the theoretical claim.

### 2. Gamma Profile Shape

V10's reaction-diffusion produces smooth ∇²-regulated field. Canvas accumulation produces spiky gamma at painted cells, zero elsewhere. Gradient at positions between painted cells will be noisy.

**Possible resolution**: The `get_effective_gamma(radius=3)` sampling might smooth this enough. Or it might not — finding out is the point.

### 3. No Centrifugal Barrier

V10 entities maintained tangential velocity through continuous position updates. On integer lattice, gradient-following always points toward center. Without a mechanism to maintain tangential motion, everything collapses.

**This is the core test.** If orbits require continuous velocity that the substrate can't provide, then the theory needs to explain how momentum emerges from list operations.

### 4. Dimensionality

V18 is 3D. V10 was 2D. Running in 2D simplifies visualization and analysis. Consider a 2D variant (Canvas2D_V18) for this test, or restrict all positions to z=0 plane.

**Recommendation**: Run in 2D first. If orbits emerge, repeat in 3D.

---

## What Each Outcome Means for the Project

### If orbits emerge (even messy ones):
- The reaction-diffusion PDE was scaffolding. Canvas accumulation IS the physics.
- V18 becomes the canonical substrate. All future experiments build on it.
- The six PDE parameters can be deleted from the project forever.
- Paper-worthy result: "Orbital dynamics emerge from pure gamma accumulation without field equations."

### If only stable radii (no orbits):
- Canvas provides gravitational attraction but not orbital mechanics.
- Need to understand what the PDE contributed: field smoothness? Continuous velocity? Angular momentum conservation?
- V18 needs one specific addition (whatever the PDE was providing) — tells us exactly what.

### If everything collapses:
- Integer lattice cannot support orbits without continuous math.
- The discrete-to-continuous transition is a real physics problem, not a detail.
- Theory needs to explain how continuous-seeming trajectories emerge from discrete steps.
- Most informative failure mode — points directly at what needs solving next.

### If everything escapes:
- Canvas gamma field too weak or wrong shape at orbital distances.
- Need more planet processes or more pre-evolution ticks.
- Re-run with 2000 planet processes and 2000 ticks pre-evolution.

---

## Implementation Notes for Claude Code

### Files to create:
```
experiments/v18_orbital_test/
├── README.md                    ← This document
├── orbital_process.py           ← OrbitalTestProcess (Approach A)
├── experiment_orbital.py        ← Main experiment runner
├── analysis.py                  ← Post-run analysis and plotting
└── results/                     ← Output directory
```

### Dependencies:
- Import from `experiments/56_composite_objects/v18/` (Canvas3D_V18, CompositeProcess, etc.)
- numpy (for gradient computation — already in v18)
- matplotlib (for trajectory plots)
- No scipy. No reaction-diffusion. No Lorentz formula. If any of these appear in the code, the experiment is contaminated.

### Forbidden imports:
```python
# NONE of these may appear anywhere in this experiment:
from scipy.ndimage import laplace      # No PDE
import math; math.sqrt(1 - v**2/c**2)  # No Lorentz factor
# No analytical gamma formulas
# No continuous position (float coordinates)
# No predefined gravitational profiles
```

### Run sequence:
1. Phase 0: Create planet, evolve 500 ticks, save gamma profile
2. Inspect gamma profile — is gradient smooth enough for orbits?
3. Phase 1B: Pure V18 test (Approach B) — ring of processes, measure collapse vs stability
4. Phase 1A: Orbital test (Approach A) — processes with integer velocity
5. Analysis: classify trajectories, compare with v10

---

## One More Thing

If this experiment produces even one stable orbit on the V18 canvas — with integer positions, no PDE, no Lorentz factor, no continuous math — it will be the strongest result in the entire repository. Not because orbits are hard (they're classical mechanics), but because it would prove that **a sparse dict of integer gamma values, accumulated by painting one cell per tick, self-organizes into a field that supports Keplerian dynamics**.

That's the kind of result that survives peer review.

And if it fails, the failure mode tells you exactly what to work on next — which is worth more than another successful experiment on the wrong substrate.
