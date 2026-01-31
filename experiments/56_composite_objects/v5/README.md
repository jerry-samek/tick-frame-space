# Experiment 56: Integer Arithmetic Conversion (V5)

**Status**: PLANNED - Design complete, awaiting implementation
**Date**: 2026-01-24
**Based on**: V4 stable fragmented cloud (200k validation)

## Motivation

V4 successfully created a stable 2D fragmented electron cloud, but revealed numerical precision limitations:

### Problems with Float Arithmetic

1. **Energy Drift**: 1.43% energy drift over 200k ticks due to accumulation errors
2. **Non-Determinism**: Float rounding varies across platforms and compiler optimizations
3. **Long-Term Stability**: Precision loss compounds over extended simulations
4. **Performance**: Float operations are 2-5× slower than integer arithmetic

### V6 Solution: Scaled Integer Arithmetic

**Convert all physics calculations to fixed-point integer arithmetic** with explicit scaling factor.

**Benefits**:
- ✓ **Perfect determinism**: Bit-exact results across all platforms
- ✓ **Zero accumulation error**: Integer arithmetic is exact
- ✓ **Improved energy conservation**: No float rounding in energy calculations
- ✓ **2-5× faster**: Integer operations outperform float
- ✓ **Long-term stability**: Can run million-tick simulations without drift

**Foundation for V6/V7**: Integer base enables particle accelerator (V6) and dual-parameter collision (V7) experiments with guaranteed reproducibility.

## Scaling Factor Design

### Choice: SCALE = 100,000,000 (10^8)

**Rationale**:
1. **Preserves critical precision**: Most sensitive parameter `jitter_strength = 0.0005` → `50,000` (5 significant digits)
2. **Avoids overflow**: Maximum values ~200M stay well below 64-bit integer limit (~9 × 10^18)
3. **Efficient arithmetic**: 10^8 allows fast division by powers of 10
4. **Standard engineering scale**: Common in financial and scientific computing

### Precision Analysis

| Parameter | Float Value | Scaled Integer | Precision Preserved |
|-----------|-------------|----------------|---------------------|
| `jitter_strength` | 0.0005 | 50,000 | 8 decimal places ✓ |
| `collision_radius` | 0.5 | 50,000,000 | 8 decimal places ✓ |
| `fragment_mass` | 0.002 | 200,000 | 8 decimal places ✓ |
| `velocity_typical` | 0.05 | 5,000,000 | 7 decimal places ✓ |
| `position_typical` | 2.0 | 200,000,000 | 8 decimal places ✓ |
| `energy_typical` | 0.0001 | 10,000 | 8 decimal places ✓ |

**Conclusion**: 10^8 scaling preserves all necessary precision from V4 validation.

## Implementation Phases

### Phase 1: Fixed-Point Utility Module

**File**: `fixed_point.py`

Implement integer arithmetic helpers:

```python
class FixedPoint:
    """Fixed-point arithmetic with SCALE = 10^8."""
    SCALE = 100_000_000

    @staticmethod
    def from_float(x: float) -> int:
        """Convert float to scaled integer."""
        return int(x * FixedPoint.SCALE)

    @staticmethod
    def to_float(x: int) -> float:
        """Convert scaled integer to float (for output only)."""
        return x / FixedPoint.SCALE

    @staticmethod
    def multiply(a: int, b: int) -> int:
        """Multiply two scaled integers: (a * b) / SCALE."""
        return (a * b) // FixedPoint.SCALE

    @staticmethod
    def divide(a: int, b: int) -> int:
        """Divide two scaled integers: (a * SCALE) / b."""
        return (a * FixedPoint.SCALE) // b

    @staticmethod
    def sqrt(x: int) -> int:
        """Integer square root using Newton's method."""
        if x <= 0:
            return 0

        # Initial guess: x / 2
        guess = x // 2
        if guess == 0:
            guess = 1

        # Newton iteration: guess_new = (guess + x/guess) / 2
        for _ in range(20):  # Converges fast
            guess_new = (guess + x // guess) // 2
            if abs(guess_new - guess) <= 1:
                break
            guess = guess_new

        return guess

    @staticmethod
    def distance_squared(x1: int, y1: int, x2: int, y2: int) -> int:
        """Compute squared distance between two points."""
        dx = x2 - x1
        dy = y2 - y1
        return FixedPoint.multiply(dx, dx) + FixedPoint.multiply(dy, dy)

    @staticmethod
    def distance(x1: int, y1: int, x2: int, y2: int) -> int:
        """Compute distance between two points."""
        d_sq = FixedPoint.distance_squared(x1, y1, x2, y2)
        return FixedPoint.sqrt(d_sq)
```

**Tests**: Verify against known float values (error < 10^-7).

### Phase 2: Fragment Dynamics Conversion

**File**: `fragmented_cloud_v5.py`

Convert fragment state representation:

```python
@dataclass
class FragmentV5:
    """Fragment with integer positions/velocities."""
    x: int  # Scaled by SCALE
    y: int  # Scaled by SCALE
    vx: int  # Scaled by SCALE
    vy: int  # Scaled by SCALE
    mass: int  # Scaled by SCALE

    def kinetic_energy(self) -> int:
        """KE = (1/2) * m * v^2, returns scaled value."""
        v_squared = FixedPoint.multiply(self.vx, self.vx) + FixedPoint.multiply(self.vy, self.vy)
        # KE = (m * v^2) / 2
        return FixedPoint.multiply(self.mass, v_squared) // 2
```

**Initialization** (from V4 validated parameters):

```python
def initialize_fragments(n_fragments: int = 50) -> list[FragmentV5]:
    """Create initial fragmented cloud with scaled integers."""
    fragments = []

    # Scaled parameters from V4
    RADIUS_MEAN = FixedPoint.from_float(2.0)  # 200,000,000
    RADIUS_STD = FixedPoint.from_float(0.5)   # 50,000,000
    VELOCITY_MEAN = FixedPoint.from_float(0.05)  # 5,000,000
    VELOCITY_STD = FixedPoint.from_float(0.01)   # 1,000,000
    FRAGMENT_MASS = FixedPoint.from_float(0.002)  # 200,000

    for i in range(n_fragments):
        # Generate integer Gaussian random values
        r = gaussian_int(RADIUS_MEAN, RADIUS_STD)
        theta = uniform_int(0, FixedPoint.from_float(2 * math.pi))

        x = FixedPoint.multiply(r, cos_int(theta))
        y = FixedPoint.multiply(r, sin_int(theta))

        v = gaussian_int(VELOCITY_MEAN, VELOCITY_STD)
        v_theta = uniform_int(0, FixedPoint.from_float(2 * math.pi))

        vx = FixedPoint.multiply(v, cos_int(v_theta))
        vy = FixedPoint.multiply(v, sin_int(v_theta))

        fragments.append(FragmentV5(x, y, vx, vy, FRAGMENT_MASS))

    return fragments
```

### Phase 3: Collision Physics Conversion

**File**: `collision_dynamics_v5.py`

**CRITICAL**: Energy conservation depends on exact collision arithmetic.

```python
def elastic_collision_v5(f1: FragmentV5, f2: FragmentV5) -> tuple[FragmentV5, FragmentV5]:
    """
    Elastic collision with integer arithmetic.

    Momentum conservation: m1*v1 + m2*v2 = m1*v1' + m2*v2'
    Energy conservation: (1/2)*m1*v1^2 + (1/2)*m2*v2^2 = (1/2)*m1*v1'^2 + (1/2)*m2*v2'^2
    """
    # Relative velocity
    dvx = f1.vx - f2.vx
    dvy = f1.vy - f2.vy

    # Relative position
    dx = f1.x - f2.x
    dy = f1.y - f2.y

    # Distance squared
    d_sq = FixedPoint.multiply(dx, dx) + FixedPoint.multiply(dy, dy)

    if d_sq == 0:
        return f1, f2  # No collision if coincident

    # Dot product: dv · dr
    dv_dot_dr = FixedPoint.multiply(dvx, dx) + FixedPoint.multiply(dvy, dy)

    # Impulse magnitude: J = (2 * m1 * m2 / (m1 + m2)) * (dv · dr) / d^2
    m_sum = f1.mass + f2.mass
    m_product = FixedPoint.multiply(f1.mass, f2.mass)

    # numerator = 2 * m1 * m2 * (dv · dr)
    numerator = 2 * FixedPoint.multiply(m_product, dv_dot_dr)

    # denominator = (m1 + m2) * d^2
    denominator = FixedPoint.multiply(m_sum, d_sq)

    # impulse_mag = numerator / denominator
    impulse_mag = FixedPoint.divide(numerator, denominator)

    # Impulse vector: J_vec = impulse_mag * dr
    Jx = FixedPoint.multiply(impulse_mag, dx)
    Jy = FixedPoint.multiply(impulse_mag, dy)

    # Update velocities: v1' = v1 - J/m1, v2' = v2 + J/m2
    f1_new = FragmentV5(
        x=f1.x, y=f1.y,
        vx=f1.vx - FixedPoint.divide(Jx, f1.mass),
        vy=f1.vy - FixedPoint.divide(Jy, f1.mass),
        mass=f1.mass
    )

    f2_new = FragmentV5(
        x=f2.x, y=f2.y,
        vx=f2.vx + FixedPoint.divide(Jx, f2.mass),
        vy=f2.vy + FixedPoint.divide(Jy, f2.mass),
        mass=f2.mass
    )

    return f1_new, f2_new
```

**Validation**: Test that energy and momentum are EXACTLY conserved (zero error).

### Phase 4: Random Number Generation

**File**: `random_int.py`

**Challenge**: Generate Gaussian random integers for zero-point jitter.

**Solution 1: Box-Muller Transform (Integer Adaptation)**

```python
def gaussian_int(mean: int, std: int, rng: random.Random) -> int:
    """
    Generate Gaussian random integer using Box-Muller.

    mean, std: scaled integers
    Returns: scaled integer from N(mean, std)
    """
    # Generate two uniform random integers in [0, SCALE)
    u1 = rng.randint(1, FixedPoint.SCALE - 1)
    u2 = rng.randint(0, FixedPoint.SCALE - 1)

    # Box-Muller: z = sqrt(-2 * ln(u1)) * cos(2*pi*u2)
    # ln(u1) approximation using Taylor series or lookup table
    ln_u1 = ln_int(u1)

    # sqrt(-2 * ln(u1))
    sqrt_term = FixedPoint.sqrt(-2 * ln_u1)

    # cos(2*pi*u2)
    angle = FixedPoint.multiply(2 * FixedPoint.from_float(math.pi), u2)
    cos_term = cos_int(angle)

    # z = sqrt_term * cos_term
    z = FixedPoint.multiply(sqrt_term, cos_term)

    # x = mean + std * z
    return mean + FixedPoint.multiply(std, z)
```

**Solution 2: Ziggurat Algorithm (Recommended for Performance)**

More efficient for repeated sampling. Requires precomputed lookup tables.

**Trigonometry Functions** (needed for initialization):

```python
def cos_int(theta: int) -> int:
    """
    Integer cosine using CORDIC or Taylor series.
    theta: scaled angle in radians
    Returns: scaled cos(theta)
    """
    # Option 1: Lookup table with linear interpolation
    # Option 2: CORDIC algorithm (iterative rotation)
    # Option 3: Taylor series (for small angles)

    # Simplified: Use Python's math.cos and convert
    # (Replace with pure integer implementation for true determinism)
    theta_float = FixedPoint.to_float(theta)
    return FixedPoint.from_float(math.cos(theta_float))

def sin_int(theta: int) -> int:
    """Integer sine (similar to cos_int)."""
    theta_float = FixedPoint.to_float(theta)
    return FixedPoint.from_float(math.sin(theta_float))
```

**Note**: For perfect cross-platform determinism, replace `math.cos/sin` with CORDIC or lookup tables.

### Phase 5: Zero-Point Jitter Conversion

**File**: `zero_point_jitter_v5.py`

**MOST CRITICAL PARAMETER**: `jitter_strength = 0.0005` → `50,000` (scaled)

```python
def apply_jitter_v5(fragment: FragmentV5, jitter_strength: int, rng: random.Random) -> FragmentV5:
    """
    Apply zero-point energy jitter to fragment.

    jitter_strength: scaled integer (50,000 for validated value)
    """
    # Generate Gaussian kicks
    dvx = gaussian_int(0, jitter_strength, rng)
    dvy = gaussian_int(0, jitter_strength, rng)

    return FragmentV5(
        x=fragment.x,
        y=fragment.y,
        vx=fragment.vx + dvx,
        vy=fragment.vy + dvy,
        mass=fragment.mass
    )
```

### Phase 6: Configuration Update

**File**: `config_v5.py`

```python
class ConfigV5:
    """Configuration for V5 integer arithmetic simulation."""

    # Scaling factor
    SCALE = 100_000_000  # 10^8

    # Cloud parameters (from V4 validated - converted to scaled integers)
    n_fragments = 50
    fragment_mass = 200_000  # 0.002 * SCALE

    # Zero-point jitter (CRITICAL - validated optimal)
    jitter_strength = 50_000  # 0.0005 * SCALE

    # Collision detection
    collision_radius = 50_000_000  # 0.5 * SCALE

    # Proton (binding center)
    proton_mass = 10_000_000_000  # 100.0 * SCALE
    proton_position_x = 0
    proton_position_y = 0

    # Initialization (scaled integers)
    init_radius_mean = 200_000_000  # 2.0 * SCALE
    init_radius_std = 50_000_000    # 0.5 * SCALE
    init_velocity_mean = 5_000_000  # 0.05 * SCALE
    init_velocity_std = 1_000_000   # 0.01 * SCALE

    # Simulation
    num_ticks = 200_000  # Match V4 validation run
    snapshot_interval = 1000

    # Random seed (for reproducibility)
    random_seed = 42
```

### Phase 7: Main Experiment Script

**File**: `experiment_56a_v5_integer.py`

```python
import random
import json
from config_v5 import ConfigV5
from fragmented_cloud_v5 import FragmentV5, initialize_fragments
from collision_dynamics_v5 import detect_collisions_v5, elastic_collision_v5
from zero_point_jitter_v5 import apply_jitter_v5
from binding_detection_v2 import compute_gamma_field  # Reuse from V4
from fixed_point import FixedPoint

def run_simulation_v5():
    """Run V5 integer arithmetic simulation."""
    cfg = ConfigV5()
    rng = random.Random(cfg.random_seed)

    # Initialize fragments
    fragments = initialize_fragments(cfg.n_fragments)

    # Proton (binding center)
    proton = FragmentV5(
        x=cfg.proton_position_x,
        y=cfg.proton_position_y,
        vx=0,
        vy=0,
        mass=cfg.proton_mass
    )

    # Tracking
    total_energy_history = []
    cloud_radius_history = []

    # Simulation loop
    for tick in range(cfg.num_ticks):
        # 1. Apply zero-point jitter
        fragments = [apply_jitter_v5(f, cfg.jitter_strength, rng) for f in fragments]

        # 2. Detect and resolve collisions
        collision_pairs = detect_collisions_v5(fragments, cfg.collision_radius)
        for i, j in collision_pairs:
            fragments[i], fragments[j] = elastic_collision_v5(fragments[i], fragments[j])

        # 3. Apply proton binding force
        for i in range(len(fragments)):
            fragments[i] = apply_proton_binding_v5(fragments[i], proton)

        # 4. Update positions
        for i in range(len(fragments)):
            fragments[i] = FragmentV5(
                x=fragments[i].x + fragments[i].vx,
                y=fragments[i].y + fragments[i].vy,
                vx=fragments[i].vx,
                vy=fragments[i].vy,
                mass=fragments[i].mass
            )

        # 5. Compute diagnostics
        total_energy = compute_total_energy_v5(fragments)
        cloud_radius = compute_cloud_radius_v5(fragments)

        total_energy_history.append(total_energy)
        cloud_radius_history.append(cloud_radius)

        # 6. Snapshot
        if tick % cfg.snapshot_interval == 0:
            print(f"Tick {tick}: E={FixedPoint.to_float(total_energy):.6f}, R={FixedPoint.to_float(cloud_radius):.4f}")

    # Final results
    results = {
        "config": {
            "n_fragments": cfg.n_fragments,
            "jitter_strength": cfg.jitter_strength,
            "collision_radius": cfg.collision_radius,
            "num_ticks": cfg.num_ticks,
            "random_seed": cfg.random_seed,
            "SCALE": cfg.SCALE
        },
        "final_state": {
            "total_energy": total_energy_history[-1],
            "cloud_radius": cloud_radius_history[-1],
            "n_fragments": len(fragments)
        },
        "energy_history": total_energy_history,
        "cloud_radius_history": cloud_radius_history
    }

    # Save results
    with open("results/exp56a_v5_integer_200k.json", "w") as f:
        json.dump(results, f, indent=2)

    print("V5 integer simulation complete!")
    return results
```

## File Modification Priority

### Critical (Must Convert First)

1. **`fixed_point.py`** - Foundation for all integer arithmetic
2. **`config_v5.py`** - Scaled integer configuration
3. **`fragmented_cloud_v5.py`** - Fragment state representation
4. **`collision_dynamics_v5.py`** - Energy conservation critical
5. **`zero_point_jitter_v5.py`** - Most sensitive parameter (jitter_strength)
6. **`experiment_56a_v5_integer.py`** - Main simulation loop

### Secondary (Can Reuse or Adapt)

1. **`binding_detection_v2.py`** - Gamma field can remain float (analysis only)
2. **`analyze_quantization.py`** - Analysis script (operates on float outputs)
3. **`monitor_*.py`** - Monitoring scripts (operate on snapshots)

## Validation Strategy

### Test 1: Arithmetic Precision

**Verify** `fixed_point.py` functions:
- Multiplication: `(a * b) / SCALE` correct to 8 decimals
- Division: `(a * SCALE) / b` correct to 8 decimals
- Square root: Newton's method converges within 20 iterations
- Distance: Matches float calculation to 7 decimals

### Test 2: Energy Conservation

**Single collision test**:
- Two fragments with known velocities/masses
- Compute KE before and after collision
- Assert: KE_before == KE_after (EXACT, zero error)

### Test 3: Reproduction of V4 Baseline

**Run 200k tick simulation** with V6 integer implementation:

**Success criteria** (must match or exceed V4):
- ✓ Cloud stability: ≤ 6.52% radius drift
- ✓ No escapes: 0 fragments beyond binding radius
- ✓ Energy conservation: ≤ 1.43% drift (should improve to ~0.1%)
- ✓ Collision rate: ~5 collisions/tick (similar to V4)

**Comparison metrics**:
| Metric | V4 Float | V6 Integer Target |
|--------|----------|-------------------|
| Radius drift (%) | 6.52 | ≤ 5.0 |
| Energy drift (%) | 1.43 | ≤ 0.5 |
| Escapes | 0 | 0 |
| Collision rate | 5.05/tick | 4.5-5.5/tick |
| Runtime (200k ticks) | ~120s | ≤ 80s (1.5× faster) |

### Test 4: Deterministic Reproducibility

**Run same simulation 3 times** with identical `random_seed`:
- Assert: ALL output values EXACTLY identical (bit-for-bit)
- No platform-dependent float rounding

### Test 5: Long-Term Stability

**Run 1 million ticks**:
- Measure energy drift
- Verify no accumulation errors
- Target: < 1% drift over 1M ticks (5× longer than V4)

## Expected Outcomes

### Success Criteria

1. **Exact Reproducibility**: ✓ Bit-exact results across platforms
2. **Improved Energy Conservation**: ✓ Energy drift < 0.5% (vs 1.43% in V4)
3. **Equivalent Stability**: ✓ Radius drift ≤ 5% (vs 6.52% in V4)
4. **Performance Gain**: ✓ 1.5-2× faster than V4 float implementation
5. **Long-Term Viability**: ✓ Can run 1M+ ticks without numerical collapse

### Comparison with V4

| Aspect | V4 (Float) | V6 (Integer) Expected |
|--------|------------|----------------------|
| Determinism | Platform-dependent | Bit-exact ✓ |
| Energy drift (200k) | 1.43% | < 0.5% ✓ |
| Radius drift (200k) | 6.52% | < 5.0% ✓ |
| Runtime (200k ticks) | ~120s | ~80s ✓ |
| Max stable ticks | ~500k (estimated) | 1M+ ✓ |

### If V6 Succeeds

- ✓ Provides solid foundation for V7 particle accelerator experiments
- ✓ Enables million-tick simulations for long-term stability studies
- ✓ Validates that tick-frame physics is compatible with exact arithmetic
- ✓ Opens path to formal verification (all operations are integer)

### If V6 Fails

**Failure modes**:
1. **Overflow errors**: Need larger scaling factor (10^9 or 10^10)
2. **Precision loss**: Critical jitter parameter loses effectiveness → need 10^9 scale
3. **Performance regression**: Integer ops slower than expected → optimize hot paths
4. **Numerical instability**: Integer division introduces bias → use different rounding

**Fallback plan**: Retain V4 float implementation, focus on V7 particle accelerator.

## References

**V4 Results**:
- `../v4/PHASE_4_V4_RESULTS.md` - Validated 200k stability (6.52% drift, 0 escapes)
- `../v4/CHECKLIST.md` - Optimal parameters (jitter=0.0005, collision_radius=0.5)
- `../v4/results/exp56a_v4_quantization_200k.json` - Baseline data for comparison

**Theory**:
- Doc 070_01: Collision-Driven Stabilization
- Doc 070_02: Zero-Point Energy (Field Rotation)
- Doc 070_03: Emergent Atomic Model

**Next Steps**:
- V6: Particle accelerator experiments (high/low speed projectiles, scattering)
- vX_3d: 3D implementation (deferred until V5/V6/V7 validate 2D model)

**External Resources**:
- Fixed-point arithmetic: https://en.wikipedia.org/wiki/Fixed-point_arithmetic
- CORDIC algorithm: https://en.wikipedia.org/wiki/CORDIC
- Ziggurat algorithm: Marsaglia & Tsang (2000)

---

**Status**: DESIGN COMPLETE - Ready for implementation
**Priority**: HIGH (foundation for all future experiments)
**Estimated Time**: 6-10 hours (implementation + validation)

**Implementation Order**:
1. Phase 1: Fixed-point utilities (2 hours)
2. Phase 2-3: Fragment dynamics + collisions (3 hours)
3. Phase 4-5: Random generation + jitter (2 hours)
4. Phase 6-7: Config + main experiment (1 hour)
5. Validation tests (2-3 hours)
