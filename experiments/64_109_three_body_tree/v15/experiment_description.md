# v15: One Mechanism — Growth Asymmetry Nudge

## Date: February 22, 2026
## Status: Completed — radial collapse only, no orbits

## Hypothesis

v14 proved cascade drift (instantaneous growth rates) was the dominant binding
mechanism — the edge profile flattened to 1% variation but bodies stayed bound.
v15 strips to ONE mechanism: the nudge buffer. No internal_direction, no frame
rotation, no Bresenham, no commit cycle. Entity is passive — the graph pushes it.

The critical question: does growth asymmetry alone produce ORBITS or just RADIAL FALL?

## Implementation

### MacroBody (~50 lines replacing v14's ~150)

```python
def advance(self, field, tick):
    # 1. Deposit gamma
    field.deposit(self.node, self.bid, self.mass * self.deposit_rate)
    # 2. Read growth asymmetry → accumulate in nudge_buffer / inertia
    for ax in range(3):
        g_plus = field.last_growth[self.node, ax * 2]
        g_minus = field.last_growth[self.node, ax * 2 + 1]
        self.nudge_buffer[ax] += (g_minus - g_plus) / self.inertia
    # 3. When component reaches +/-1 → hop
    # 4. After hop: edge asymmetry deflects nudge_buffer (geodesic tilt)
```

### ContinuousGammaField — two new helpers

- `neighbor_in_direction(node, axis, sign)` — O(1) lookup
- `move_gamma(bid, old_node, new_node)` — transfer tagged gamma inline

### Removed from v14

`commit_mass`, `commit_counter`, `internal_direction`, `hop_accumulator`,
`cascade_buffer`, `physical_position`, `physical_trajectory`, `prev_node`

### Added

`deposit_rate`, `inertia`, `nudge_buffer` — the ONLY motion state

## Results

### 10/10 verification tests pass

Tests 1-7: unchanged field tests (gamma conservation, peak retention, etc.)
Test 8: nudge accumulation produces hops from growth asymmetry
Test 9: nudge_buffer preserves momentum with H=0 (no growth → no decay)
Test 10: move_gamma conserves gamma exactly

### Momentum conservation confirmed (G=0, deposit_strength=0.001)

**Phase 1** (50K ticks): Distance locked at 10.0, nudge_buffer perfectly preserved
at [0, +0.300, 0], zero hops. Growth asymmetry too weak to reach hop threshold.

**Phase 2** (50K ticks): Same result. L=-300 constant. Nudge does NOT decay.

**The nudge buffer is a clean conserved quantity when no forces act.**

### Radial collapse under active dynamics

Parameter sweep to find settings where bodies actually move:

| Config | Hops/5K ticks | Behavior |
|--------|--------------|----------|
| H=0.1, dep=0.001, i=1.0 | 0 | No motion (nudge ~0.06/1K ticks) |
| H=0.1, dep=0.001, i=0.1 | 4 | Slow radial fall |
| H=0.1, dep=0.001, i=0.01 | 210 | Fast radial oscillation |
| H=1.0, dep=0.001, i=1.0 | 4 | Same as H=0.1/i=0.1 (saturated) |

**Key finding**: H doesn't matter (gamma denominator saturates the growth formula).
**Inertia is the only effective lever.**

Higher deposit_strength (0.1, 1.0) produces MORE gamma which suppresses ALL edge
growth, killing the asymmetry signal. Lower deposit (0.001) gives the strongest signal.

### Tangential nudge consumed, not replenished

With tangential_nudge=3.0, inertia=0.1:

| Tick | Distance | Position | nudge_buffer |
|------|----------|----------|-------------|
| 10 | 12 | (+10,+2) | [-0.15, +0.97] |
| 100 | 11 | (+9,+2) | [-0.63, +0.54] |
| 200 | 4 | (+3,+1) | [-0.19, -0.71] |
| 500 | 2 | (+2,+0) | [-0.33, -0.97] |
| 3000 | 0 | (+0,+0) | [-0.00, -0.00] |

Tangential nudge produces initial y-hops, then gets consumed and NOT replenished.
Radial nudge dominates. All configurations converge to d=0.

### Geodesic tilt attempted — still collapses

Added v14's tilt formula after each hop: `nudge_buffer[ax] += -(e_plus - e_minus) / e_sum`

**Problem 1**: In a spherically symmetric field, tilt is purely radial ([-0.007, 0, 0]).
It reinforces the gravitational pull instead of deflecting tangential momentum.

**Problem 2**: After each hop, `nudge_buffer[axis] -= sign` consumes the dominant
component, leaving magnitude ~0. The tilt (0.007 per hop) acts on ~0, producing ~0.
With ~14 hops before collapse, total tilt deflection is ~0.1 radians. An orbit needs 2π.

**Problem 3**: Magnitude-preserving rotation doesn't help for the same reason — after
hop subtraction, the buffer magnitude is near zero, so rotation preserves near-zero.

## Root Cause Analysis

### Why v14's frame rotation worked but v15's tilt doesn't

v14 had **two separate states**:
1. `cascade_buffer` — force accumulator (growth asymmetry). Determines **when** to hop.
2. `internal_direction` — unit velocity vector. Determines **where** to hop. Always
   magnitude 1.0, always available for rotation by edge tilt.

The tilt operated on a unit vector. After each hop, the direction was still unit length.
The tilt could accumulate 0.007 per hop over hundreds of hops, rotating the direction
from tangential to radial and back. The cascade buffer just triggered the hops.

v15 merged these into one buffer. The buffer is both force AND momentum. When the
buffer reaches ±1, the hop subtracts ±1, destroying the momentum signal. The tilt
has nothing left to rotate. **The integer hop quantization erases the directional
information that the tilt needs.**

### The fundamental tension

The single-buffer design is elegant: nudge = force accumulator = momentum = velocity.
But the hop discretization (threshold ±1, subtract ±1) creates a structural problem:

- **Before hop**: buffer has direction information (e.g., [-1.2, 0.5, 0])
- **After hop**: dominant component consumed ([-0.2, 0.5, 0])
- **Tilt adds**: ~0.007 to the residual. Negligible.
- **Next growth asymmetry**: adds ~0.017/tick radially. Dominates again.

The tangential component persists (0.5 survives the radial hop) but never reaches
the hop threshold because the radial component refills to ±1.0 first. The planet
always hops radially. Tangential hops require tangential nudge ≥ 1.0, which the
geometry doesn't provide (growth asymmetry in a spherically symmetric field is radial).

## What v15 Proved

1. **Momentum conservation works.** The nudge buffer is a clean conserved quantity.
   With H=0, it preserves perfectly. This is real momentum.

2. **Growth asymmetry produces gravity.** Bodies are pulled toward mass concentrations
   through local edge growth differences. No gradient, no action at a distance.

3. **One buffer cannot be both force and direction.** The integer hop quantization
   erases directional information. Geodesic deflection requires a persistent direction
   state that survives the hop.

4. **Edge tilt in spherical symmetry is purely radial.** The tilt formula
   `-(e_plus - e_minus) / e_sum` gives only radial components when the gamma field
   is spherically symmetric. It cannot generate tangential deflection.

5. **Inertia is the effective lever, not H.** The growth formula saturates at high
   gamma (H/gamma_sum → 0). Lower deposit_strength gives stronger signal. Inertia
   directly scales the nudge accumulation rate.

## Implications for v16

The single-buffer approach needs a mechanism to couple radial motion into tangential
motion. Options:

1. **Restore direction separation**: Keep nudge_buffer for force/triggering, add a
   unit direction vector for "which way." This is v14 made cleaner (no commit cycle,
   no Bresenham) but still two states. The direction gets tilted by edge asymmetry.

2. **Velocity-dependent deflection**: Apply tilt not from position (edge asymmetry)
   but from the body's motion relative to the graph. A moving body sees different
   growth on its leading edge vs trailing edge. This is a Coriolis-like effect.

3. **Continuous buffer, no threshold**: Remove the integer hop. Let the buffer
   represent a continuous position offset. The tilt can then always rotate a
   meaningful vector. Discretization happens at the graph level (which node
   is "closest" to the continuous position).

The key insight: **geodesic curvature requires velocity information**. A force
(growth asymmetry) tells you WHERE to accelerate. A geodesic tells you how your
existing VELOCITY curves through the geometry. These are fundamentally different
operations. v15 tried to collapse them into one and learned they can't be.

## File Structure

```
v15/
  experiment_description.md  (this file)
  macro_bodies.py            (field + nudge-only MacroBody)
  results/                   (plots from experiments)
```
