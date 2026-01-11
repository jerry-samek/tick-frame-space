# Experiment 44_04: Multi-Entity Temporal Depth

## Hypothesis

**If the third dimension (z-axis) is truly temporal displacement, then using `temporal_lag` DIRECTLY as the z-coordinate should simplify rendering dramatically while producing natural 3D-like depth perception.**

This experiment extends 44_03's findings by:
1. Testing with many entities (100+) instead of just 3
2. Using temporal_lag as z without complex transformations
3. Demonstrating emergent depth patterns from simple rules
4. Validating that rotation asymmetry scales to multi-entity systems

## Core Principle

```python
# 44_03 approach (complex):
depth_factor = temporal_lag / MAX_HISTORY
px = x * (1 - depth_factor) + vanishing_point_x * depth_factor
# + size scaling, color fading, perspective calculations...

# 44_04 approach (simple):
entity.z = entity.temporal_lag  # Direct mapping, no transformation!
```

**The simplicity itself validates the theory** - if z IS temporal, we shouldn't need complex mappings.

## Entity Patterns to Test

### Pattern 1: Grid Formation
**Purpose:** Validate structured depth with regular spatial arrangement

- 10×10 grid of entities in XY plane
- Temporal lag varies by position (e.g., diagonal gradient)
- Tests: Do entities maintain grid structure while appearing at different depths?

**Expected:** Clear layered grid with depth perception matching lag distribution

### Pattern 2: Random Cloud
**Purpose:** Test emergent depth from unstructured lag distribution

- 100+ entities at random XY positions
- Random temporal lag values (0-50)
- Tests: Does natural 3D cloud appearance emerge without explicit 3D positioning?

**Expected:** Convincing point cloud with automatic depth sorting

### Pattern 3: Concentric Shells
**Purpose:** Validate radial depth gradients

- Entities arranged in concentric circles
- Lag increases with radius (outer shells = higher lag = further back)
- Tests: Do shells appear as distinct depth layers?

**Expected:** "Onion layer" structure with clear separation between shells

### Pattern 4: Temporal Wave
**Purpose:** Test dynamic temporal lag changes

- Entities oscillate in temporal lag over time
- Creates "wave" motion in z-axis
- Tests: Can entities move smoothly through temporal space?

**Expected:** Fluid wave-like motion in apparent depth

## Rendering Philosophy

**44_03 Complexity:**
- Perspective projection toward vanishing point
- Size scaling based on depth factor
- Color fading with age
- Lag visualization bars
- Triangle edge connections
- ~50+ lines of rendering code

**44_04 Simplicity:**
- Direct z = temporal_lag
- Simple depth sorting
- Basic scaling: `size = base_size / (1 + z * factor)`
- Color by depth (optional)
- **Target: < 15 lines of rendering code**

**Why simpler is better:**
If the theory is correct, treating temporal_lag as z should "just work" without elaborate transformations. Complexity would suggest we're fighting against the natural representation.

## Validation Criteria

### Primary Validations:

1. **Rendering Simplicity**
   - Render function < 15 lines
   - No vanishing point calculations needed
   - No complex perspective math
   - **Metric:** Lines of code in render function

2. **Depth Perception Accuracy**
   - Visual depth matches temporal_lag values exactly
   - Entities sort correctly by lag without explicit z-buffer
   - **Metric:** User perception test (does it look 3D?)

3. **Scalability**
   - Handles 100+ entities smoothly (vs 44_03's 3-10)
   - Performance remains interactive at 30+ FPS
   - **Metric:** Frame rate with 100+ entities

4. **Rotation Asymmetry (Emergent)**
   - Apply rotational forces to entity cloud
   - Forward rotation (reduce lag) fails for all entities
   - Backward rotation (increase lag) succeeds with energy cost
   - Z-rotation (2D plane) works freely
   - **Metric:** Success rates match 44_03 asymmetry pattern

### Secondary Validations:

5. **Temporal Causality**
   - Entities at different lags interact differently
   - Large lag differences prevent collision
   - **Metric:** Emergence of temporal horizon

6. **Energy-Lag Coupling**
   - Entities that move more in XY accumulate more lag
   - Relationship should be linear: `lag ∝ xy_distance`
   - **Metric:** Correlation coefficient between movement and lag

7. **Pattern Coherence**
   - Structured patterns (grid, shells) maintain shape despite lag variations
   - Demonstrates that temporal depth is independent of spatial structure
   - **Metric:** Visual coherence over time

## Implementation Design

### Entity Model

```python
class Entity:
    """
    Minimal entity with direct temporal-as-spatial mapping.
    """
    def __init__(self, x, y, temporal_lag=0, color=(255, 255, 255)):
        self.x = x              # 2D spatial X
        self.y = y              # 2D spatial Y
        self.z = temporal_lag   # DIRECTLY temporal lag (not transformed)
        self.color = color
        self.energy = 0
        self.velocity = (0, 0)  # 2D velocity in XY

    def update(self, tick):
        """Movement in XY automatically creates lag"""
        self.energy += 1

        # Move in XY plane
        if self.energy >= MOVEMENT_COST:
            dx, dy = self.velocity
            distance = sqrt(dx*dx + dy*dy)

            self.x += dx
            self.y += dy

            # Energy spent on spatial movement = temporal lag accumulated
            self.z += distance * LAG_PER_DISTANCE
            self.energy -= MOVEMENT_COST
```

### Simplified Rendering

```python
def render(entities, screen):
    """
    Render entities using temporal_lag directly as z-coordinate.
    Should be dramatically simpler than 44_03.
    """
    # Sort by z (temporal lag) for correct depth order
    sorted_entities = sorted(entities, key=lambda e: -e.z)

    for entity in sorted_entities:
        # Simple depth scaling
        depth_scale = 1.0 / (1.0 + entity.z * DEPTH_FACTOR)

        # Screen position (simple perspective)
        screen_x = int(entity.x * depth_scale + camera_x * (1 - depth_scale))
        screen_y = int(entity.y * depth_scale + camera_y * (1 - depth_scale))

        # Size and color by depth
        radius = max(1, int(BASE_RADIUS * depth_scale))
        color = color_by_depth(entity.color, entity.z, max_z)

        pygame.draw.circle(screen, color, (screen_x, screen_y), radius)
```

**That's it. ~10 lines vs 44_03's 50+.**

## Controls

- **1-4:** Switch between entity patterns (grid, random, shells, wave)
- **W:** Apply forward "force" to all entities (try to reduce lag)
- **S:** Apply backward "force" to all entities (increase lag)
- **Q/A:** Rotate entire cloud in XY plane
- **Space:** Reset pattern
- **P:** Pause simulation
- **L:** Toggle lag value display
- **+/-:** Adjust entity count

## Expected Results

### If Hypothesis is Correct:

1. **Rendering will be trivial**
   - Direct z=temporal_lag mapping works naturally
   - No complex math needed
   - < 15 lines of render code

2. **Depth perception will be convincing**
   - Entities automatically sort by depth
   - Visual 3D appearance emerges naturally
   - User immediately perceives depth structure

3. **Asymmetry will replicate at scale**
   - Forward force: 0% success across all entities
   - Backward force: 93%+ success (energy-limited)
   - Z-rotation: 100% success (unrestricted)
   - Same pattern as 44_03 but with 100+ entities

4. **Performance will scale well**
   - Simpler rendering = better performance
   - Can handle 1000+ entities if needed
   - Proves theory is computationally efficient

### If Hypothesis is Incorrect:

1. **Rendering will require fixes**
   - Direct mapping won't produce good visuals
   - Need to add complex transformations
   - Code complexity increases

2. **Depth perception will be poor**
   - Entities don't sort correctly
   - Visual appearance is flat or wrong
   - User struggles to perceive depth

3. **No clear asymmetry**
   - Forward and backward forces behave similarly
   - Rotation works equally in all directions
   - Pattern from 44_03 doesn't scale

## Connection to 44_03 Results

Experiment 44_03 demonstrated:
- Forward pitch: 0% success (impossible)
- Backward pitch: 93.33% success (energy-limited)
- Z-rotation: 100% success (unrestricted)
- **933.33x asymmetry ratio**

Experiment 44_04 should show:
- Same asymmetry pattern but emergent from many entities
- Same temporal constraints but with simpler code
- **Validates that the constraint is fundamental, not an artifact of triangle geometry**

## Success Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Render code lines | < 15 | Count LOC in render function |
| Entity count | 100+ | Configurable, test up to 1000 |
| Frame rate | 30+ FPS | Measure with 100 entities |
| Forward success rate | ~0% | Log attempts and successes |
| Backward success rate | 90%+ | Log attempts and successes |
| Z-rotation success rate | 100% | Log attempts and successes |
| Depth perception | Convincing | User evaluation |
| Code complexity reduction | 70%+ | Compare to 44_03 |

## Theoretical Implications

If this experiment succeeds, it demonstrates:

1. **Simplicity validates truth**
   - Correct model should be simple to implement
   - Complex transformations suggest fighting against natural representation
   - "Nature uses the simplest mathematics"

2. **Z is fundamentally temporal**
   - Direct z=lag mapping works without modification
   - No need for spatial 3D concepts
   - Temporal interpretation is primary, not derived

3. **Emergent 3D from 2D+time**
   - Visual 3D appearance emerges from 2D entities with temporal lags
   - No true 3D space needed
   - Perception of depth is perception of temporal separation

4. **Scalability of constraints**
   - Rotation asymmetry is not specific to triangles
   - Same physics governs 3 entities or 1000 entities
   - Validates universality of temporal surfing constraint

## Future Extensions

- **44_05:** Temporal causality and collision horizons
- **44_06:** Energy model refinement with multi-entity interactions
- **44_07:** 3D visualization export (ironically, by treating temporal as spatial in 3D viewer)
- **44_08:** Integration with Java substrate simulation

## Files

- `multi_entity_depth.py` - Main experiment implementation
- `README.md` - This documentation
- `logs/` - Session logs (auto-created)
- `RESULTS.md` - Results report (created after testing)
