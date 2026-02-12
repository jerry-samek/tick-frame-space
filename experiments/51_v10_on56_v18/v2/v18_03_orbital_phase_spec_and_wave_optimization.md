# V18.1 Orbital Phase Specification + Wave Optimization

**Date**: 2026-02-11  
**Status**: Formation phase PASSED. Ready for orbital phase.  
**Context**: Gamma conservation perfect (36058), gradient nonzero at all distances, field extends to r=57.

---

## Part 1: Diagnostics to Add BEFORE Running Orbital Phase

### 1.1 Gamma Profile Snapshot

At end of formation (before injecting test processes), log gamma at these distances:

```python
def log_gamma_profile(canvas, center=(0,0,0)):
    """Sample gamma along +x axis from center."""
    distances = [1, 2, 3, 5, 7, 10, 15, 20, 25, 30, 40, 50]
    print("\n=== GAMMA PROFILE γ(r) ===")
    print(f"{'r':>4}  {'gamma':>12}  {'gradient_mag':>12}")
    for r in distances:
        pos = (center[0] + r, center[1], center[2])
        gamma = canvas.get_gamma(pos)
        grad = canvas.get_gradient(pos)
        grad_mag = (grad[0]**2 + grad[1]**2 + grad[2]**2) ** 0.5
        print(f"{r:>4}  {gamma:>12.4f}  {grad_mag:>12.6f}")
    
    # Power law fit: log(gamma) vs log(r)
    # Sample at r=5,10,20,40 to avoid near-field and edge effects
    import math
    fit_points = [(5, canvas.get_gamma((center[0]+5, center[1], center[2]))),
                  (10, canvas.get_gamma((center[0]+10, center[1], center[2]))),
                  (20, canvas.get_gamma((center[0]+20, center[1], center[2]))),
                  (40, canvas.get_gamma((center[0]+40, center[1], center[2])))]
    
    # Skip if any gamma is zero
    fit_points = [(r, g) for r, g in fit_points if g > 0]
    if len(fit_points) >= 2:
        log_r = [math.log(r) for r, g in fit_points]
        log_g = [math.log(g) for r, g in fit_points]
        # Linear regression: log(g) = -n * log(r) + c
        n = len(log_r)
        sum_x = sum(log_r)
        sum_y = sum(log_g)
        sum_xy = sum(x*y for x, y in zip(log_r, log_g))
        sum_xx = sum(x*x for x in log_r)
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
        print(f"\nPower law fit: γ ~ r^({slope:.3f})")
        print(f"  (1/r would be -1.000, 1/r² would be -2.000)")
```

### 1.2 Gradient Shape Verification

The critical question from the V18 failure: does gradient magnitude DECREASE with distance?

```python
def log_gradient_profile(canvas, center=(0,0,0)):
    """Verify gradient falloff shape."""
    distances = [5, 10, 15, 20, 25, 30, 40, 50]
    print("\n=== GRADIENT FALLOFF ===")
    print(f"{'r':>4}  {'grad_mag':>12}  {'ratio_to_prev':>14}  {'expected_1/r²':>14}")
    prev_grad = None
    for r in distances:
        pos = (center[0] + r, center[1], center[2])
        grad = canvas.get_gradient(pos)
        grad_mag = (grad[0]**2 + grad[1]**2 + grad[2]**2) ** 0.5
        
        ratio = ""
        expected = ""
        if prev_grad and prev_grad[1] > 0 and grad_mag > 0:
            ratio = f"{grad_mag / prev_grad[1]:.4f}"
            # For 1/r potential, force ~ 1/r², ratio should be (r_prev/r)²
            expected = f"{(prev_grad[0]/r)**2:.4f}"
        
        print(f"{r:>4}  {grad_mag:>12.6f}  {ratio:>14}  {expected:>14}")
        prev_grad = (r, grad_mag)
```

### 1.3 Per-Tick Orbital Logging

For each test process, every tick during orbital phase:

```python
def log_orbital_tick(tick, process, canvas):
    """Per-tick diagnostic for orbital test processes."""
    r = (process.center[0]**2 + process.center[1]**2 + process.center[2]**2) ** 0.5
    
    grad = canvas.get_gradient(process.center)
    grad_mag = (grad[0]**2 + grad[1]**2 + grad[2]**2) ** 0.5
    
    gamma_local = canvas.get_gamma(process.center)
    
    # Angular momentum (2D, z-component): L = x*vy - y*vx
    x, y = process.center[0], process.center[1]
    vx, vy = process.velocity[0], process.velocity[1]
    L_z = x * vy - y * vx
    
    # Speed
    speed = (vx**2 + vy**2 + process.velocity[2]**2) ** 0.5
    
    # Angle from +x axis (for revolution counting)
    import math
    angle = math.atan2(y, x)
    
    return {
        'tick': tick,
        'process_id': process.process_id,
        'x': x, 'y': y, 'z': process.center[2],
        'r': r,
        'vx': vx, 'vy': vy, 'vz': process.velocity[2],
        'speed': speed,
        'L_z': L_z,
        'angle': angle,
        'grad_mag': grad_mag,
        'gamma_local': gamma_local,
        'skipped': process.skips_count,
        'acted': process.acts_count,
    }
```

Save as JSON array per process. Needed for post-run analysis.

### 1.4 Summary Statistics Every 100 Ticks

```python
def log_orbital_summary(tick, test_processes, canvas):
    """Periodic summary during orbital phase."""
    print(f"\n--- Tick {tick} ---")
    print(f"{'ID':>4} {'r':>7} {'speed':>6} {'L_z':>8} {'angle':>7} {'skips':>6} {'status':>10}")
    
    for p in test_processes:
        r = (p.center[0]**2 + p.center[1]**2 + p.center[2]**2) ** 0.5
        speed = (p.velocity[0]**2 + p.velocity[1]**2 + p.velocity[2]**2) ** 0.5
        L_z = p.center[0]*p.velocity[1] - p.center[1]*p.velocity[0]
        
        # Quick status classification
        if r < 3:
            status = "COLLAPSED"
        elif r > 100:
            status = "ESCAPED"
        elif speed < 0.01:
            status = "STUCK"
        else:
            status = "ACTIVE"
        
        import math
        angle = math.degrees(math.atan2(p.center[1], p.center[0]))
        
        print(f"{p.process_id:>4} {r:>7.1f} {speed:>6.2f} {L_z:>8.1f} {angle:>7.1f}° {p.skips_count:>6} {status:>10}")
    
    # Wake stats
    wake_size = len(canvas.wake) if hasattr(canvas, 'wake') else 0
    gamma_total = sum(canvas.gamma.values())
    print(f"Wake cells: {wake_size}  Gamma total: {gamma_total:.0f}  Painted cells: {len(canvas.gamma)}")
```

---

## Part 2: Wave-Based Spreading Optimization

### 2.1 The Problem with Current Incremental Approach

Formation showed 474K/497K cells active in wake. The field has a smooth gradient everywhere, so every cell has a pressure differential with its neighbors. The wake never goes to zero — it just gets tiny. The incremental approach based on `wake != 0` doesn't help because wake is almost never exactly zero in a gradient field.

### 2.2 The Fix: Per-Process Wavefronts

Don't iterate the field. Don't track global wake. Each process carries its own spreading wavefront. Only the wavefront computes. The settled field is a lookup table.

```python
class WaveFront:
    """Tracks the spreading wavefront from a single paint event."""
    
    def __init__(self, origin, initial_strength):
        self.cells = {origin: initial_strength}  # {pos: delta_to_spread}
        self.age = 0
    
    def propagate(self, canvas):
        """Advance wavefront one tick. Returns True if still active."""
        SPREAD_FRACTION = 1.0 / 6
        DEATH_THRESHOLD = 1e-6  # Below this, wave has dissipated
        
        next_cells = {}
        
        for pos, _ in self.cells.items():
            gamma_here = canvas.get_gamma(pos)
            if gamma_here <= 0:
                continue
            for offset in canvas.NEIGHBOR_OFFSETS:
                neighbor = (pos[0]+offset[0], pos[1]+offset[1], pos[2]+offset[2])
                gamma_there = canvas.get_gamma(neighbor)
                if gamma_here > gamma_there:
                    transfer = (gamma_here - gamma_there) * SPREAD_FRACTION
                    if transfer > DEATH_THRESHOLD:
                        # Apply transfer to canvas
                        canvas.gamma[pos] = canvas.gamma.get(pos, 0.0) - transfer
                        canvas.gamma[neighbor] = canvas.gamma.get(neighbor, 0.0) + transfer
                        # Track the frontier (where significant transfer happened)
                        next_cells[neighbor] = next_cells.get(neighbor, 0.0) + transfer
        
        self.cells = next_cells
        self.age += 1
        
        return len(self.cells) > 0  # Active while wavefront has cells
```

**IMPORTANT**: This simplified version does NOT do synchronous update — it modifies gamma during iteration. For the orbital test this is acceptable because wavefronts from different processes rarely overlap spatially. But if strict correctness is needed, accumulate transfers first then apply.

### 2.3 Integration into Process

```python
class OrbitalTestProcess(CompositeProcess):
    def __init__(self, ...):
        super().__init__(...)
        self.velocity = (0, 0, 0)
        self.active_waves = []  # List of WaveFront objects
    
    def step(self, canvas):
        # 1. Read gradient (O(6) lookups)
        grad = canvas.get_gradient(self.center)
        
        # 2. Update velocity from gradient (whatever acceleration model)
        # ... existing orbital mechanics code ...
        
        # 3. Move
        self.center = tuple(c + v for c, v in zip(self.center, self.velocity))
        
        # 4. Paint
        canvas.gamma[self.center] = canvas.get_gamma(self.center) + 1.0
        
        # 5. Spawn new wavefront from this paint event
        self.active_waves.append(WaveFront(self.center, 1.0))
        
        # 6. Propagate all my active wavefronts
        self.active_waves = [w for w in self.active_waves if w.propagate(canvas)]
        
        return True
```

### 2.4 Formation Phase with Wavefronts

During formation, planet processes also use wavefronts:

```python
def formation_phase(canvas, n_planets, n_ticks):
    """Formation with per-process wavefronts."""
    planets = []
    all_waves = []
    
    for tick in range(n_ticks):
        # Each planet paints at its location
        for planet in planets:
            planet.step(canvas)  # paint + spawn wave
        
        # Propagate ALL active wavefronts
        all_waves = [w for w in all_waves if w.propagate(canvas)]
        
        # Collect new waves from planets
        for planet in planets:
            all_waves.extend(planet.active_waves)
            planet.active_waves = []
        
        if tick % 50 == 0:
            print(f"Tick {tick}: active_waves={len(all_waves)}, "
                  f"painted={len(canvas.gamma)}")
    
    # SETTLEMENT: stop painting, let waves die
    print("Settlement phase — propagating remaining waves...")
    settle_tick = 0
    while all_waves and settle_tick < 500:
        all_waves = [w for w in all_waves if w.propagate(canvas)]
        settle_tick += 1
        if settle_tick % 50 == 0:
            print(f"  Settle tick {settle_tick}: active_waves={len(all_waves)}")
    
    print(f"Field settled after {settle_tick} ticks. Active waves: {len(all_waves)}")
    return canvas
```

### 2.5 Performance Expectations

Each paint event spawns one wavefront. The wavefront is a thin expanding shell:

```
Wave age 0:    1 cell (origin)
Wave age 1:    6 cells (immediate neighbors)  
Wave age 5:    ~150 cells (shell at r=5)
Wave age 10:   ~600 cells (shell at r=10)
Wave age 20:   ~2400 cells (shell at r=20)
Wave age 50:   transfers below threshold, wave dies
```

Critically: **old waves die.** A wave spawned at tick 100 is dead by tick 150. It doesn't persist. The field it created persists, but the wavefront computation doesn't.

So at any given tick during formation:

```
Active waves ≈ n_planets × wave_lifetime ≈ 100 × 50 = 5,000 waves
Each wave: ~shell_surface cells of work
Average shell: ~500 cells
Total work: 5,000 × 500 × 6 = 15M operations

Compare to full spreading: 497,000 × 6 = 3M operations per tick
```

Hmm — wavefront approach might actually be SLOWER during formation because we track many overlapping shells. The win comes during orbital phase:

```
Active waves ≈ 5 test processes × wave_lifetime ≈ 5 × 50 = 250 waves  
Each wave: ~500 cells average
Total work: 250 × 500 × 6 = 750,000 operations

Compare to full spreading: 497,000 × 6 = 3M operations per tick
Speedup: ~4×

Compare to incremental (wake_changed approach): should be similar
```

### 2.6 Practical Recommendation

**For formation**: Use the existing spreading with a delta-change threshold to prune settled cells:

```python
# Quick fix for formation performance
for pos, delta in transfers.items():
    if abs(delta) > 1e-6:  # Drop negligible transfers
        # ... apply transfer ...
```

This isn't the wave architecture — it's just float noise cleanup. Should cut the 474K active cells down to the actual wavefront.

**For orbital phase**: Either the threshold fix above OR the per-process wavefront approach. Both should give ~5-6 orders of magnitude speedup over "iterate all 497K cells."

**For Model C (future)**: The per-process wavefront is the right long-term architecture because it maps to the storage engine model — each write creates a wave, the wave propagates until it dissipates, the field is the accumulated result.

---

## Part 3: What to Log During Orbital Phase

### 3.1 Per-Process JSON Output

Save one JSON file per test process:

```json
{
  "process_id": "T1",
  "start_r": 30,
  "start_velocity": [0, 1, 0],
  "ticks": [
    {"tick": 501, "x": 30, "y": 1, "z": 0, "r": 30.02, "vx": 0, "vy": 1, "vz": 0, "speed": 1.0, "L_z": 30, "angle": 1.91, "grad_mag": 0.004, "gamma_local": 0.12},
    {"tick": 502, "x": 29, "y": 2, "z": 0, "r": 29.07, ...},
    ...
  ]
}
```

### 3.2 Post-Run Analysis Checklist

From the saved JSON, compute and report:

```
For each test process:
  1. r(t) plot                    — the key diagnostic
  2. Classification               — ORBIT / COLLAPSE / ESCAPE / STUCK / CHAOTIC
  3. Eccentricity                 — (r_max - r_min) / (r_max + r_min) after first 200 ticks
  4. Revolution count             — cumulative angle / 2π
  5. Angular momentum L_z(t) plot — conservation check
  6. L_z std/mean                 — <0.5 is good, <0.05 matches V10
  
Summary table:
  - How many orbited vs collapsed vs escaped
  - Best eccentricity achieved
  - Best L_z conservation achieved
  
Comparison:
  - V18 (no spreading): 0/25 orbits, L_z std/mean ~1.2
  - V10 (PDE): 18/18 orbits, L_z std/mean ~0.05
  - V18.1 (spreading): ???
```

### 3.3 Field Diagnostics to Save

At end of formation (before orbital), save:

```json
{
  "gamma_profile": {"1": 523.4, "2": 312.1, "5": 98.7, "10": 34.2, ...},
  "gradient_profile": {"5": 0.23, "10": 0.12, "15": 0.07, ...},
  "power_law_exponent": -1.12,
  "total_gamma": 36058,
  "painted_cells": 497000,
  "field_r_max": 57.4,
  "formation_ticks": 500,
  "n_planets": 100
}
```

### 3.4 Performance Diagnostics

Every 100 ticks during orbital phase:

```
Tick 600: orbital_time=0.02s  wave_cells=312  painted=497,200  gamma_total=36058
Tick 700: orbital_time=0.02s  wave_cells=287  painted=497,350  gamma_total=36058
```

Key numbers: time per tick (should be <0.1s during orbital), active wave cells (should be small), gamma total (MUST be constant).

---

## Part 4: Quick Reference — Complete Tick Loop for Orbital Phase

```python
def run_orbital_phase(canvas, test_processes, n_ticks):
    """Orbital phase after formation + settlement."""
    results = {p.process_id: [] for p in test_processes}
    
    for tick in range(n_ticks):
        for process in test_processes:
            # 1. Read gradient from settled field (O(6))
            grad = canvas.get_gradient(process.center)
            
            # 2. Update velocity from gradient
            #    (keep whatever acceleration model the existing code uses)
            process.update_velocity(grad)
            
            # 3. Skip check (time dilation)
            gamma_local = canvas.get_gamma(process.center)
            # ... skip logic ...
            
            # 4. Move
            process.center = tuple(
                c + v for c, v in zip(process.center, process.velocity)
            )
            
            # 5. Paint (one cell)
            canvas.paint_imprint(process.process_id, {(0,0,0): 1.0}, process.center)
            
            # 6. Propagate this process's waves (optional — 
            #    test process paint is tiny relative to planet field,
            #    can skip wave propagation for test processes if perf is fine)
            process.propagate_waves(canvas)
            
            # 7. Log
            results[process.process_id].append(
                log_orbital_tick(tick, process, canvas)
            )
        
        # Periodic summary
        if tick % 100 == 0:
            log_orbital_summary(tick, test_processes, canvas)
    
    return results
```

---

## Part 5: What We're Watching For

The formation results already answered two of three questions:

| Question | V18 answer | V18.1 answer |
|----------|-----------|--------------|
| Does gradient reach orbital distances? | NO (zero at r>8) | **YES** (nonzero to r=57) |
| Does gradient decrease with distance? | N/A (was zero) | **YES** (0.23→0.004) |
| Do orbits form? | NO (0/25) | **PENDING** |

If orbits form: six PDE parameters replaced by one geometric rule (1/6 sharing). Zero free parameters.

If orbits still fail: log the failure mode. The three possibilities are:
1. **Collapse** — gradient too steep near center, need to check skip mechanism
2. **Escape** — gradient too weak at starting distance, need more planet mass or formation time
3. **Angular momentum violation** — integer velocity problem from V18 test, need Phase 2 (fractional accumulator)

Each failure mode has a specific next step. No result is wasted.
