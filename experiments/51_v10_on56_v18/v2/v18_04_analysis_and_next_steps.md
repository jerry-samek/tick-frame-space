# V18.1 Orbital Results — Analysis and Next Steps

**Date**: 2026-02-11  
**In response to**: V18.1 orbital phase results (0/6 orbits, two root causes)

---

## What We Learned

Two independent problems. Must be tested separately.

| Problem | What's broken | How we know |
|---------|--------------|-------------|
| Field shape (r^-3.55 vs r^-1) | Spreading hasn't reached equilibrium | Gamma peaks at r=13, not monotonic from center |
| Integer velocity | Sign-only acceleration destroys angular momentum | T1 (tangential) behaves same as T2 (radial) |

Testing both at once means we can't tell which fix mattered. Split them.

---

## Step 1: Analytical 1/r Baseline (DO THIS FIRST)

Skip the spreading entirely. Initialize the gamma field as 1/r directly. This isolates the velocity problem from the field problem.

```python
def initialize_analytical_field(canvas, center=(0,0,0), total_mass=45000, r_max=100):
    """Plant a 1/r gamma field directly.
    
    gamma(r) = total_mass / (4 * pi * r)  for r >= 1
    
    This is the steady-state solution of the spreading rule.
    We skip the spreading and go straight to equilibrium.
    
    total_mass should match formation output (~45,000) for comparison.
    """
    import math
    
    placed_total = 0.0
    
    for x in range(-r_max, r_max + 1):
        for y in range(-r_max, r_max + 1):
            for z in range(-r_max, r_max + 1):
                r = math.sqrt(x*x + y*y + z*z)
                if r < 1:
                    r = 1  # Avoid singularity at origin
                if r > r_max:
                    continue
                    
                gamma = total_mass / (4 * math.pi * r)
                
                if gamma > 1e-6:  # Don't store negligible values
                    pos = (center[0]+x, center[1]+y, center[2]+z)
                    canvas.gamma[pos] = gamma
                    placed_total += gamma
    
    # Rescale so total matches target
    scale = total_mass / placed_total
    for pos in canvas.gamma:
        canvas.gamma[pos] *= scale
    
    print(f"Analytical field: {len(canvas.gamma)} cells, total gamma = {sum(canvas.gamma.values()):.0f}")
```

**IMPORTANT**: This is a TEST, not a replacement for spreading. If orbits work on analytical 1/r but not on spread field, we know the field is the problem. If orbits fail on analytical 1/r too, the field was never the issue — it's all velocity.

### Verification after initialization

```python
# Check the profile is actually 1/r
for r in [1, 2, 5, 10, 20, 30, 50, 80]:
    pos = (r, 0, 0)
    g = canvas.get_gamma(pos)
    expected = total_mass / (4 * math.pi * r)  # Before rescaling
    print(f"r={r:>3}: gamma={g:.2f}, grad_mag={grad_mag:.6f}")

# Check gradient decreases with distance
# For 1/r potential: force ~ 1/r², gradient ratio (r1/r2)² 
```

### Run orbital test on analytical field

Same 6 test processes. Same configurations. Same logging. **With sign-only acceleration first** — this tells us whether the field alone is enough, or whether the accumulator is also needed.

Expected outcome: probably still chaotic bouncing because sign-only acceleration is the primary angular momentum killer. But the PATTERN of bouncing will be different — instead of a narrow r=5-18 band, processes should oscillate across a wider range in the 1/r well.

---

## Step 2: Velocity Accumulator (THEN THIS)

Run on the SAME analytical 1/r field, with the fractional accumulator replacing sign-only acceleration.

```python
class OrbitalTestProcess_V2(CompositeProcess):
    """Orbital process with fractional velocity accumulator."""
    
    def __init__(self, process_id, center, velocity=(0,0,0), speed_limit=5):
        super().__init__(process_id=process_id, center=center, 
                         internal_state=DegenerateState())
        self.velocity = tuple(velocity)
        self.speed_limit = speed_limit
        
        # NEW: fractional accumulator for sub-integer acceleration
        self.accel_accumulator = (0.0, 0.0, 0.0)
    
    def step(self, canvas):
        # 1. Read gradient (6 dict lookups)
        grad = canvas.get_gradient(self.center)
        grad_mag = (grad[0]**2 + grad[1]**2 + grad[2]**2) ** 0.5
        
        if grad_mag > 0:
            # 2. Accumulate fractional acceleration
            #    Use gradient MAGNITUDE, not just sign
            #    Normalize direction, scale by magnitude
            self.accel_accumulator = (
                self.accel_accumulator[0] + grad[0],
                self.accel_accumulator[1] + grad[1],
                self.accel_accumulator[2] + grad[2],
            )
        
        # 3. Extract integer part (when accumulator crosses threshold)
        int_accel = (
            int(self.accel_accumulator[0]),
            int(self.accel_accumulator[1]),
            int(self.accel_accumulator[2]),
        )
        
        # 4. Keep fractional remainder
        self.accel_accumulator = (
            self.accel_accumulator[0] - int_accel[0],
            self.accel_accumulator[1] - int_accel[1],
            self.accel_accumulator[2] - int_accel[2],
        )
        
        # 5. Update velocity
        self.velocity = (
            self.velocity[0] + int_accel[0],
            self.velocity[1] + int_accel[1],
            self.velocity[2] + int_accel[2],
        )
        
        # 6. Speed limit (clamp per-component)
        self.velocity = tuple(
            max(-self.speed_limit, min(self.speed_limit, v))
            for v in self.velocity
        )
        
        # 7. Skip check (time dilation from local gamma)
        gamma_local = canvas.get_gamma(self.center)
        skip_threshold = gamma_local * 0.001  # Very mild time dilation
        if skip_threshold >= 1.0:
            self.skips_count += 1
            return True
        
        # 8. Move
        self.center = tuple(c + v for c, v in zip(self.center, self.velocity))
        
        # 9. Paint (optional — tiny contribution to frozen sea)
        # canvas.gamma[self.center] = canvas.get_gamma(self.center) + 1.0
        
        self.acts_count += 1
        self.age_ticks += 1
        return True
```

### Key differences from sign-only

| Aspect | Sign-only | Accumulator |
|--------|-----------|-------------|
| Gradient at r=30 (weak, say 0.01) | accel = (0, 0, 0) or (±1,±1,±1) | accel accumulates 0.01/tick, fires ±1 every ~100 ticks |
| Gradient at r=5 (strong, say 0.5) | accel = (±1, ±1, ±1) same as above | accel fires every ~2 ticks |
| Tangential velocity preserved? | No — sign() flips tangential to radial | Yes — only radial component accumulates from radial gradient |
| Angular momentum | Destroyed | Preserved (gradient is radial, doesn't affect tangential) |

The last row is the critical one. A radial gradient adds to the radial accumulator component. The tangential component accumulates nothing from the gradient (it's perpendicular). So tangential velocity is preserved unless something explicitly changes it. That's angular momentum conservation.

---

## Step 3: Spreading Convergence Test (SEPARATE EXPERIMENT)

This doesn't need orbital processes. Just spread and measure.

```python
def test_spreading_convergence(n_planets=200, paint_ticks=250, max_spread_ticks=5000):
    """How many spread ticks to reach 1/r?
    
    Log the power law exponent every 100 spread ticks.
    Stop when exponent stabilizes near -1.0 (or doesn't).
    """
    canvas = Canvas3D_V18()
    
    # Paint phase
    for tick in range(paint_ticks):
        for planet in planets:
            planet.paint(canvas)
    
    # Spread phase with periodic measurement
    print("spread_tick  power_law  r_max  wake_cells")
    for spread_tick in range(max_spread_ticks):
        canvas.spread_gamma()  # Or incremental
        
        if spread_tick % 100 == 0:
            exponent = fit_power_law(canvas)
            r_max = measure_r_max(canvas)
            wake = len(canvas.wake)
            print(f"{spread_tick:>10}  {exponent:>9.3f}  {r_max:>5.1f}  {wake:>10}")
            
            # Early exit if converged
            if abs(exponent - (-1.0)) < 0.1:
                print(f"Converged to 1/r at spread tick {spread_tick}!")
                break
```

Expected: exponent starts at ~-3.5 (current), gradually approaches -1.0 as wavefront reaches equilibrium. If it takes 10,000 ticks to converge, that's important information — it means spreading needs MUCH more time than we gave it, or needs a different approach.

**This can run overnight.** It's not blocking the orbital test.

---

## Run Matrix

| Run | Field | Velocity | Purpose | Priority |
|-----|-------|----------|---------|----------|
| A | Analytical 1/r | Sign-only | Isolate: is field the problem? | **NOW** |
| B | Analytical 1/r | Accumulator | Isolate: does accumulator fix orbits? | **NOW** |
| C | Spread (250 ticks) | Accumulator | Does accumulator help even with steep field? | If time allows |
| D | Spread convergence | N/A (no processes) | How long to reach 1/r? | **Overnight** |

**Run A + B are the priority.** They answer the two questions independently:
- A: "Is 1/r sufficient for orbits with sign-only velocity?" (probably no)
- B: "Is 1/r + accumulator sufficient for orbits?" (this is the big test)

If B produces orbits: done. The spreading rule produces 1/r (eventually) and the accumulator handles integer velocity. Zero free parameters.

If B fails: we have a deeper problem — even the correct field with smooth velocity can't produce orbits on an integer lattice. That would mean the lattice itself is the issue.

---

## Performance Notes

### Analytical initialization is expensive but one-time

Filling all cells in a sphere of r=100:
- Cells: ~4.2 million (4/3 π × 100³)
- With 1e-6 cutoff: fewer, maybe ~1 million
- Initialization time: ~10-30 seconds
- After that: frozen sea, orbital phase runs at thousands of ticks/sec

### Reducing initialization radius

r=100 might be overkill. Test processes start at max r=50. Field at r=80 is negligible for dynamics. Use r_max=60 to cut volume by ~70%.

### 2D option

If 3D initialization is too slow, run the analytical test in 2D first:
- Replace z-loop with z=0
- Use gamma = total_mass / (2 * pi * r) for 2D (logarithmic potential, but 1/r force)
- Much faster initialization
- If orbits work in 2D, repeat in 3D

---

## Logging (Same as Before)

Keep all logging from the previous spec:
- Gamma profile at formation end
- Per-tick process state (position, velocity, L_z, gradient)
- Summary every 100 ticks
- Final classification and comparison table

Add one new metric for the accumulator runs:

```python
# Log accumulator state — shows sub-integer dynamics
{
    'tick': tick,
    'process_id': process.process_id,
    # ... existing fields ...
    'accel_accum_x': process.accel_accumulator[0],
    'accel_accum_y': process.accel_accumulator[1],
    'accel_accum_z': process.accel_accumulator[2],
}
```

This shows whether the accumulator is working — you should see it slowly building up in the tangential direction and periodically firing integer steps.

---

## One Key Prediction

If Run B (analytical 1/r + accumulator) produces orbits, the project has proven:

1. Spreading rule (1/6 sharing) produces the correct potential (verified by Run D)
2. Fractional accumulator preserves angular momentum on integer lattice
3. Zero free parameters (spread_fraction from geometry, accumulator is exact)
4. Six PDE parameters eliminated permanently

If Run B fails despite correct field and smooth velocity — the integer lattice fundamentally cannot support circular orbits and the theory needs continuous space, which is a much bigger problem.

Either way, we know by tonight.
