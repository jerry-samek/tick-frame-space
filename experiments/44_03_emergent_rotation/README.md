# Experiment 44_03: Emergent 3D Rotation from 2D+Temporal Entities

## Hypothesis

**Primary Question:** Can individual entities moving in 2D space create visual patterns that resemble 3D rotation when rendered with temporal depth, where the z-axis is not spatial but represents tick history?

**Core Principle:** There are no rigid geometric objects in nature. A "triangle" is an emergent collision pattern from individual entities following deterministic movement rules.

## Theoretical Framework

### The 2D+Time Interpretation

1. **Space is 2D:** Entities exist and move in `[x, y]` coordinates only
2. **Time is discrete:** Each tick advances by 1, entities cannot skip or reverse
3. **Depth is temporal:** What appears as z-coordinate is the temporal buffer - past positions rendered with perspective
4. **Surfing constraint:** All entities "surf" forward at 1 tick per tick - this is the maximum temporal velocity

### The Asymmetric Rotation Constraint

**Around temporal axis (z-rotation in visualization):**
- Equivalent to rotation in the [x,y] plane
- No temporal constraint - entities can rotate freely
- Energy cost: linear with angular velocity

**Around spatial axes (x/y-rotation in visualization):**
- Would require changing temporal velocity
- **Cannot speed up:** Maximum is 1 tick/tick (already surfing)
- **Can only slow down:** Spending energy on [x,y] movement = falling behind temporal stream
- Creates asymmetry: can only rotate "backward" (into past), never "forward" (into future)

### Energy Budget Model

Each entity has energy that increases linearly with time:
- `energy(t) = t`
- Moving in [x,y] costs energy proportional to distance
- Entities that spend more energy on spatial movement accumulate "temporal lag"
- Temporal lag = how many ticks behind the "present" this entity appears to be

## Experiment Design

### Phase 1: Triangle Pattern Formation

**Setup:**
- Spawn entities at three vertices of a triangle in 2D space
- Entities have no knowledge of "triangle" - they follow local rules only
- Each entity can spawn children to fill the pattern

**Movement Rules:**
- Energy-based movement: entity can move when `energy % momentum_cost == 0`
- Collision detection: entities at same [x,y] merge or bounce
- No global coordination - all decisions are local

**Visualization:**
- Render last N ticks with perspective projection toward vanishing point
- Color entities by temporal lag (recent = bright, old = dim)
- Depth factor = temporal lag / max_history

### Phase 2: Attempted Z-Axis Rotation (2D Rotation)

**Action:** Apply rotational force around the triangle centroid in [x,y] plane

**Expected Result:**
- ✓ Should work naturally - this is standard 2D rotation
- ✓ Entities follow curved paths in [x,y]
- ✓ Temporal buffer shows rotation smoothly
- Energy cost: moderate, proportional to angular displacement

**Success Criteria:**
- Pattern maintains coherence through rotation
- All entities remain at similar temporal lag (synchronized in time)
- Visual appearance: triangle rotating "flat" on screen

### Phase 3: Attempted X-Axis Rotation (Pitch Forward)

**Action:** Try to "tilt" the triangle forward (rotate around x-axis)

**This requires:** Some vertices to appear "closer in time" (reduce temporal lag)

**Expected Result:**
- ✗ Should FAIL or require infinite energy
- ✗ Cannot reduce temporal lag below zero
- ✗ Entities cannot "catch up" to present if they've spent energy on spatial movement

**Observable Behavior:**
- Entities that try to move "forward" hit temporal constraint
- Pattern fragments or distorts
- Asymmetry emerges: some entities can't complete the rotation

**Success Criteria (for proving constraint):**
- Clear mathematical limit prevents forward rotation
- Energy calculation shows infinite/undefined cost for lag reduction
- Visual: triangle cannot tilt toward viewer without breaking

### Phase 4: Attempted X-Axis Rotation (Pitch Backward)

**Action:** Try to "tilt" the triangle backward (rotate around x-axis away from viewer)

**This requires:** Some vertices to increase temporal lag (fall behind)

**Expected Result:**
- ✓ Should WORK with energy cost
- ✓ Entities can spend extra energy to slow down (increase lag)
- ✓ Creates visual appearance of depth/tilting

**Mechanism:**
- Top vertex: spends energy on [x,y] movement → accumulates lag → appears "further back"
- Bottom vertices: minimize movement → stay near present → appear "closer"
- Temporal buffer captures this lag differential as apparent depth

**Success Criteria:**
- Pattern achieves backward tilt
- Energy cost is finite and calculable
- Temporal lag gradient creates depth illusion
- Asymmetry confirmed: backward works, forward doesn't

### Phase 5: Maximum Rotation Angle Calculation

**Question:** What is the maximum tilt angle achievable given finite energy budget?

**Calculation:**
```
max_temporal_lag = energy_budget / movement_cost
max_depth_separation = max_temporal_lag * tick_rate
max_angle = arctan(max_depth_separation / triangle_height)
```

**Expected Result:**
- Clear mathematical limit based on energy and geometry
- Angle increases with energy budget
- Never reaches 90° (would require infinite energy)

## Observable Predictions

### If Hypothesis is CORRECT (z is temporal):

1. **Rotation asymmetry will be observed:**
   - Z-rotation: unrestricted
   - Backward x/y rotation: possible with energy cost
   - Forward x/y rotation: impossible or breaks pattern

2. **Energy signatures:**
   - Z-rotation: `E ∝ angular_velocity`
   - Backward rotation: `E ∝ lag_differential`
   - Forward rotation: `E → ∞` or undefined

3. **Pattern coherence:**
   - Triangle maintains identity during allowed rotations
   - Triangle fragments during forbidden rotations
   - Temporal lag correlates with apparent depth

### If Hypothesis is INCORRECT (z is spatial):

1. **No rotation asymmetry:**
   - All three rotation axes should be equivalent
   - Forward and backward tilt have same energy cost
   - No special constraint on any rotation direction

2. **Energy signatures:**
   - All rotations have similar energy profiles
   - No divergence or undefined costs

3. **Pattern coherence:**
   - Triangle rotates freely in all directions
   - No special fragmentation patterns

## Validation Metrics

### Quantitative:

1. **Energy cost ratio:**
   - `R = E(forward_tilt) / E(backward_tilt)`
   - If z is temporal: `R → ∞`
   - If z is spatial: `R ≈ 1`

2. **Maximum achievable angle:**
   - Backward tilt: finite angle based on energy
   - Forward tilt: should approach 0° or break

3. **Temporal lag distribution:**
   - During backward tilt: gradient from 0 to max_lag
   - During forward tilt: attempts to create negative lag (impossible)

### Qualitative:

1. **Visual pattern coherence:**
   - Does the triangle maintain shape during rotation?
   - Where does it fragment or distort?

2. **Temporal synchronization:**
   - Do entities remain in similar time frames during z-rotation?
   - Do they desynchronize during x/y rotation?

3. **Emergence:**
   - Can the rotation pattern emerge from local rules?
   - Or does it require global coordination (suggesting it's impossible)?

## Implementation Notes

### Entity Rules:
- Each entity: `[x, y, energy, temporal_lag, color]`
- Movement: local gradient following or pattern maintenance
- No entity knows about "triangle" globally

### Rendering:
- Perspective projection: `factor = temporal_lag / max_history`
- Position: `px = x * (1-factor) + vanish_x * factor`
- Size: shrinks with depth
- Color: fades with age

### Controls:
- Arrow keys: attempt different rotations
- Space: reset to initial state
- Tab: cycle visualization modes
- Numbers: select test phase

## Expected Timeline

1. **Phase 1:** Should complete successfully - pattern formation works
2. **Phase 2:** Should complete successfully - z-rotation works
3. **Phase 3:** Should FAIL - forward tilt hits constraint
4. **Phase 4:** Should complete with energy cost - backward tilt works
5. **Phase 5:** Should produce finite angle limit

## Success Criteria for Hypothesis Validation

**Hypothesis SUPPORTED if:**
- Forward rotation fails or fragments pattern
- Backward rotation succeeds with finite energy
- Energy cost ratio diverges
- Clear asymmetry between forward/backward observed
- Mathematical constraint matches theoretical prediction

**Hypothesis REJECTED if:**
- All rotations work equivalently
- No special constraint on forward rotation
- Energy costs are symmetric
- Pattern remains coherent in all directions

## Connection to Tick-Frame Theory

This experiment validates:
- **Temporal Surfing Principle (Doc 28):** Entities persist through renewal, not identity
- **Collision Persistence Principle (Doc 30):** Pattern is collision, not object
- **Discrete Time Constraint:** Cannot exceed tick rate
- **Energy-Time Coupling:** Movement in space trades off with temporal alignment

If validated, this suggests 3D space might be emergent from 2D+time substrate, with observed 3D being an artifact of temporal buffer visualization.
