# V7: Pattern Motion Dynamics

**Date**: 2026-01-30
**Status**: IN PROGRESS
**Based on**: V6 validated stability (jitter=0.119, hybrid_strong field confinement)

---

## Overview

V6 established **spatial stability** - patterns remain confined with near-zero drift. V7 now investigates **motion dynamics**: are patterns stationary, diffusing, or exhibiting coherent motion (e.g., orbital)?

**Key questions:**
1. Do patterns move at all, or are they locked in place?
2. If moving, is it random walk (diffusion) or directed motion?
3. Is there emergent orbital motion around the gamma center?
4. Do patterns maintain identity, or dissolve and reform?

---

## V7 Components

### 1. Velocity Tracking

Track instantaneous velocity for each pattern:

```python
class VelocityTracker:
    def compute_velocity(self, current_pos, previous_pos, dt=1):
        """Velocity = (x2-x1, y2-y1) / dt"""
        vx = (current_pos[0] - previous_pos[0]) / dt
        vy = (current_pos[1] - previous_pos[1]) / dt
        return (vx, vy)

    def compute_speed(self, velocity):
        """Speed = |v| = sqrt(vx^2 + vy^2)"""
        return math.sqrt(velocity[0]**2 + velocity[1]**2)
```

**Metrics:**
- Mean speed across all patterns
- Speed distribution (histogram)
- Speed vs radius (are outer patterns faster?)

---

### 2. Motion History / Trajectories

Store position time-series per pattern:

```python
class MotionHistory:
    def __init__(self, n_patterns: int, max_history: int = 1000):
        self.positions = [[] for _ in range(n_patterns)]
        self.velocities = [[] for _ in range(n_patterns)]
        self.max_history = max_history

    def record(self, pattern_id: int, pos: tuple, vel: tuple, tick: int):
        """Record position and velocity at given tick."""
        self.positions[pattern_id].append((tick, pos[0], pos[1]))
        self.velocities[pattern_id].append((tick, vel[0], vel[1]))
```

**Analysis:**
- Trajectory plots (2D path visualization)
- Mean Squared Displacement (MSD): `<|r(t) - r(0)|^2>`
- MSD scaling: `MSD ~ t^alpha`
  - α = 1: Normal diffusion (random walk)
  - α < 1: Subdiffusion (trapped)
  - α > 1: Superdiffusion (directed motion)
  - α = 2: Ballistic motion

---

### 3. Orbital Motion Detection

Check for coherent rotation around gamma center:

```python
class OrbitalAnalyzer:
    def compute_angular_position(self, pos, center):
        """Angle theta from center."""
        dx = pos[0] - center[0]
        dy = pos[1] - center[1]
        return math.atan2(dy, dx)

    def compute_angular_velocity(self, theta_current, theta_previous, dt=1):
        """Angular velocity omega = d(theta)/dt"""
        d_theta = theta_current - theta_previous
        # Handle wraparound
        if d_theta > math.pi:
            d_theta -= 2 * math.pi
        elif d_theta < -math.pi:
            d_theta += 2 * math.pi
        return d_theta / dt

    def estimate_orbital_period(self, omega_mean):
        """Period T = 2*pi / |omega|"""
        if abs(omega_mean) > 1e-10:
            return 2 * math.pi / abs(omega_mean)
        return float('inf')  # No rotation
```

**Metrics:**
- Mean angular velocity (ω) per pattern
- Angular velocity vs radius (Keplerian? Rigid body?)
- Rotation direction coherence (all same direction?)
- Estimated orbital period

---

### 4. Pattern Identity Tracking

Track whether patterns persist as coherent structures:

```python
class PatternIdentityTracker:
    def compute_local_energy(self, grid, center, radius=7):
        """Sum |field| in local region around pattern."""
        # Uses existing compute_field_center_of_mass logic
        ...

    def compute_coherence(self, grid, center, radius=7):
        """Measure how concentrated the field is (vs spread out)."""
        # High coherence = tight pattern
        # Low coherence = diffuse/dissolved
        ...

    def detect_dissolution(self, energy_history, threshold=0.5):
        """Pattern dissolved if energy drops below threshold of initial."""
        ...

    def detect_reformation(self, energy_history, threshold=0.8):
        """Pattern reformed if energy recovers above threshold."""
        ...
```

**Metrics:**
- Local energy per pattern over time
- Coherence metric (field concentration)
- Pattern lifetime (ticks until dissolution)
- Reformation events (dissolved then reformed)

---

## Experiment Design

### Experiment 7A: Velocity and MSD

**Goal**: Characterize pattern motion type (diffusion vs directed)

**Protocol**:
1. Initialize 50 patterns at r ≈ 20 (V6 optimal config)
2. Run 10k ticks with hybrid_strong field confinement
3. Record positions every 10 ticks
4. Compute MSD and fit α exponent

**Expected outcomes**:
- α ≈ 0 (subdiffusion): Patterns trapped in gamma well
- α ≈ 1 (diffusion): Random walk within confined zone
- α > 1 (superdiffusion): Directed motion / drift

### Experiment 7B: Orbital Motion

**Goal**: Detect emergent rotation around gamma center

**Protocol**:
1. Same setup as 7A
2. Compute angular position θ(t) for each pattern
3. Compute angular velocity ω(t)
4. Check for coherent rotation

**Expected outcomes**:
- ω ≈ 0: No orbital motion (patterns locked or random)
- ω ≠ 0, same sign: Coherent rotation (all patterns orbit)
- ω varies with r: Differential rotation (Keplerian-like)

### Experiment 7C: Pattern Lifetime

**Goal**: Measure pattern persistence and identity

**Protocol**:
1. Same setup as 7A
2. Track local energy for each pattern
3. Detect dissolution/reformation events
4. Compute lifetime statistics

**Expected outcomes**:
- Long lifetime (>1000 ticks): Stable pattern identity
- Short lifetime (<100 ticks): Patterns dissolve/reform frequently
- Bimodal: Some stable, some transient

---

## File Structure

```
v7/
├── README.md                    # This file
├── velocity_tracker.py          # Velocity computation
├── motion_history.py            # Trajectory storage and MSD
├── orbital_analyzer.py          # Angular velocity and orbital detection
├── pattern_identity.py          # Coherence and lifetime tracking
├── config_v7.py                 # V7 configuration (inherits V6 optimal)
├── experiment_7a_msd.py         # MSD and diffusion analysis
├── experiment_7b_orbital.py     # Orbital motion detection
├── experiment_7c_lifetime.py    # Pattern identity persistence
└── results/                     # Experiment outputs
```

---

## Success Criteria

### Minimal Success
- [ ] Velocity tracking works (non-NaN, reasonable values)
- [ ] MSD computed for 10k ticks
- [ ] Angular velocity computed for all patterns
- [ ] Local energy tracked per pattern

### Target Success
- [ ] MSD scaling exponent α determined (with confidence)
- [ ] Orbital motion presence/absence confirmed
- [ ] Mean pattern lifetime estimated
- [ ] Visualizations: trajectories, MSD plot, ω distribution

### Stretch Success
- [ ] ω(r) relationship characterized (Keplerian?)
- [ ] Pattern dissolution/reformation dynamics understood
- [ ] Phase diagram: motion type vs jitter strength
- [ ] Connection to physical diffusion constants

---

## Dependencies

**From V6 (copy or import):**
- `planck_grid.py` - Grid infrastructure
- `pattern_library.py` - Pattern definitions
- `sample_cell.py` - SampleCell and PatternInstance
- `planck_jitter.py` - Jitter application
- `evolution_rules.py` - Tick evolution with field confinement
- `pattern_tracking.py` - COM detection (basis for velocity)
- `config_v6.py` - Optimal parameters (jitter=0.119, hybrid_strong)

**New for V7:**
- `velocity_tracker.py`
- `motion_history.py`
- `orbital_analyzer.py`
- `pattern_identity.py`

---

## References

- V6 Jitter Sweep: Critical jitter = 0.119, stable existence band 0.115-0.119
- V6 Phase 4A: Field confinement (creation_sensitivity=2.0, decay_threshold=1.5, decay_rate=0.05)
- V6 stability: 0.06% radius drift, 0.04 COM drift at jitter=0.119

---

**Status**: COMPLETE ✅
**Completed**: 2026-01-30
**Key Finding**: Phase transition at critical jitter (0.119) - rotation direction bifurcation
**See**: RESULTS_SUMMARY.md for full analysis
