# Experiment 49: Dynamic Sliding Window Temporal Rendering

## Executive Summary

This experiment extends Experiment 44_05's O(n) bucketing optimization by replacing **double-buffering** with a **dynamic sliding window** that adapts its temporal memory based on available performance budget. The window maintains as much tick history as the FPS target allows, and expired frames are compressed into a "holographic horizon layer" rather than being discarded.

**Key Innovation:** Instead of fixed 2× memory for two snapshots, the window dynamically adjusts from 1× to 100× memory depending on entity count and FPS target, maximizing temporal addressability within computational constraints.

**Theoretical Foundation:** Connects Experiment 44_05's rendering optimization to Theory Documents 26 (Horizon Boundaries), 46 (Temporal Visualization), and 49 (Temporal Ontology) by implementing temporal memory as a first-class observable phenomenon.

---

## Hypothesis

**Primary:**
> A dynamic sliding window that adapts its size to maintain target FPS will maximize temporal addressability (observer memory depth) without performance degradation, enabling temporal effects (trails, motion blur, playback) that are impossible with double-buffering.

**Secondary:**
> Expired frames beyond the horizon boundary can be compressed into a holographic statistical representation (density fields, energy distributions) that preserves aggregate historical information at negligible computational cost.

---

## Motivation: Why Sliding Window?

### Limitations of Double-Buffering (44_05)

Experiment 44_05 successfully demonstrated O(n) bucketing for painter's algorithm ordering, using double-buffering to decouple CPU (simulation) and GPU (rendering) at zero synchronization cost. However, double-buffering has inherent limitations:

1. **No temporal memory**: Each buffer holds exactly one frame. Historical data is immediately lost.
2. **Fixed memory**: Always 2× current state, regardless of available budget.
3. **No temporal effects**: Cannot render entity trails, motion blur, or temporal interpolation.
4. **No playback control**: Cannot rewind, pause, or inspect past states.
5. **Horizon discontinuity**: Old data vanishes instantly instead of fading beyond a horizon.

### Sliding Window Advantages

A **dynamic sliding window** addresses these limitations:

1. **Temporal memory**: Retains last N ticks (where N adapts to performance).
2. **Dynamic memory**: Uses available budget optimally (if running at 10ms/frame with 16.67ms target, can afford 1.67× more history).
3. **Temporal effects**: Can render from multiple frames simultaneously (trails, blur).
4. **Playback control**: Can navigate backward/forward through window.
5. **Holographic horizon**: Old data compresses into statistical background instead of vanishing.

### Connection to Tick-Frame Theory

**Theory Document 49 (Temporal Ontology)** establishes:
- **Existence buffer**: Entities operate within a finite temporal buffer (current tick + accessible memory)
- **Temporal addressability**: The buffer is not time itself, but the scope of accessible temporal information

**This experiment implements that concept literally:**
- Window size = existence buffer size (how many ticks the observer can "remember")
- Dynamic sizing = computational limits on temporal addressability
- Holographic horizon = information compression beyond the addressable buffer
- Playback controls = observer manipulation of temporal navigation within buffer

**Theory Document 26 (Horizon Boundaries):**
- Observable limits in causal cones
- Entities outside the horizon cannot influence each other within finite tick budgets
- **Sliding window embodies this**: Data beyond window boundary (horizon) becomes inaccessible for direct rendering but persists as compressed aggregate (holographic principle)

---

## Architecture

### 1. Data Structure: Ring Buffer with Lag Bucketing

```
Ring Buffer Structure:
═══════════════════════════════════════════════════════════════

Temporal Dimension (ring buffer, wraps around):
    ┌─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┬─────┐
    │ T-9 │ T-8 │ T-7 │ T-6 │ T-5 │ T-4 │ T-3 │ T-2 │ T-1 │ T-0 (head)
    └─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┴─────┘
                                    └──────────────────────┘
                                    Current window (size=5)

Lag Dimension (buckets for each time offset):
For each time offset above, store array of lag buckets [0..99]:

Time T-0: [Lag 0]→Entity→Entity→None
          [Lag 1]→Entity→None
          [Lag 2]→Entity→Entity→Entity→None
          ...
          [Lag 99]→Entity→None

Combined structure:
buffer[lag][time_offset] = EntityNode (linked list head)
```

### 2. Dynamic Window Sizing Algorithm

**Goal:** Maximize window size while maintaining target FPS.

**Calculation:**
```python
def adjust_window_size(self, frame_time_ms, target_fps):
    """
    Dynamically adjust window size based on performance budget.

    Logic:
    - Target frame time = 1000 / target_fps (e.g., 16.67ms for 60 FPS)
    - Current frame time = measured actual time
    - Spare budget = target_time - frame_time
    - If spare budget > 0: Can afford larger window
    - If spare budget < 0: Must shrink window

    Window size = floor(target_time / frame_time)
    Bounded by [1, max_window_size]
    """
    target_time = 1000 / target_fps

    if frame_time_ms < 0.1:  # Safety: avoid division by zero
        return self.max_window_size

    # How many frames can we afford?
    affordable_size = int(target_time / frame_time_ms)

    # Clamp to bounds
    new_size = max(1, min(affordable_size, self.max_window_size))

    # Smooth adjustment (avoid thrashing)
    if abs(new_size - self.current_window_size) > 2:
        self.current_window_size = new_size

    return self.current_window_size
```

**Example Scenarios:**

| Entity Count | Frame Time | Target FPS | Affordable Window | Temporal Memory |
|--------------|------------|------------|-------------------|-----------------|
| 1,000 | 2ms | 60 | min(16.67/2, 100) = 8 | 8 ticks = 267ms @ 30 tps |
| 10,000 | 10ms | 60 | min(16.67/10, 100) = 1 | 1 tick = 33ms @ 30 tps |
| 50,000 | 20ms | 60 | min(16.67/20, 100) = 0 → 1 | 1 tick (minimum) |
| 1,000 | 2ms | 120 | min(8.33/2, 100) = 4 | 4 ticks = 133ms @ 30 tps |

**Key Insight:** Window size automatically trades off with entity count. Few entities = deep temporal memory. Many entities = shallow memory but still maintains FPS target.

### 3. Ring Buffer Operations

**On Tick (Write):**
```python
def on_tick(self, entities):
    """
    1. Clear current head position (overwrite oldest frame if window full)
    2. Bucket entities by lag into head position
    3. If overwriting old frame, compress it to holographic horizon
    4. Advance head pointer (circular)
    """
    old_frame = self.get_frame_at(self.head)  # Save for compression

    # Clear head position
    for lag in range(self.max_history):
        self.buffer[lag][self.head] = None

    # Bucket entities
    for entity in entities:
        lag = entity.temporal_lag
        # Prepend to linked list at [lag][head]
        self.buffer[lag][self.head] = EntityNode(
            entity,
            next=self.buffer[lag][self.head]
        )

    # Compress expired frame to horizon
    if old_frame and self.head >= self.current_window_size:
        self.holographic_horizon.compress_frame(old_frame)

    # Advance head (circular)
    self.head = (self.head + 1) % self.max_window_size
```

**Read Frame (Render):**
```python
def get_frame(self, offset=0):
    """
    Get frame N ticks in the past.
    offset=0: Current frame (head - 1)
    offset=1: One tick back
    ...
    offset=window_size-1: Oldest frame in window
    """
    if offset >= self.current_window_size:
        return None  # Outside window

    # Ring buffer index calculation
    index = (self.head - 1 - offset) % self.max_window_size

    # Return array of linked list heads for all lags
    return [self.buffer[lag][index] for lag in range(self.max_history)]
```

### 4. Holographic Horizon Layer

**Purpose:** Instead of discarding frames that fall off the window, compress them into a statistical representation that preserves aggregate information.

**Theory Connection:** This implements the "holographic principle" concept where information about a volume can be encoded on its boundary surface. Here, temporal information beyond the horizon is encoded as a 2D density field.

**Data Structure:**
```python
class HolographicHorizon:
    """
    Compresses expired frames into statistical aggregate.
    """
    def __init__(self, grid_resolution=(100, 100)):
        self.density_grid = np.zeros(grid_resolution, dtype=np.float32)
        self.energy_grid = np.zeros(grid_resolution, dtype=np.float32)
        self.total_frames = 0
        self.decay_factor = 0.99  # Slow fade over time

    def compress_frame(self, entities):
        """
        Add frame to holographic layer by binning entities into grid.
        """
        # Decay existing data slightly
        self.density_grid *= self.decay_factor
        self.energy_grid *= self.decay_factor

        # Bin entities into grid
        for entity in entities:
            grid_x = int((entity.x / SCREEN_WIDTH) * self.grid_resolution[0])
            grid_y = int((entity.y / SCREEN_HEIGHT) * self.grid_resolution[1])

            # Clamp to bounds
            grid_x = max(0, min(grid_x, self.grid_resolution[0] - 1))
            grid_y = max(0, min(grid_y, self.grid_resolution[1] - 1))

            # Accumulate
            self.density_grid[grid_y, grid_x] += 1.0
            self.energy_grid[grid_y, grid_x] += entity.temporal_lag

        self.total_frames += 1

    def render(self, screen):
        """
        Render holographic horizon as background heat map.
        """
        # Normalize density for visualization
        max_density = self.density_grid.max()
        if max_density < 0.01:
            return  # Nothing to render

        normalized = self.density_grid / max_density

        # Render as colored grid cells
        cell_width = SCREEN_WIDTH // self.grid_resolution[0]
        cell_height = SCREEN_HEIGHT // self.grid_resolution[1]

        for y in range(self.grid_resolution[1]):
            for x in range(self.grid_resolution[0]):
                density = normalized[y, x]
                if density > 0.01:  # Threshold for visibility
                    # Color: blue (low density) → red (high density)
                    color = (
                        int(255 * density),
                        int(100 * (1 - density)),
                        int(255 * (1 - density))
                    )
                    alpha = int(128 * density)  # Semi-transparent

                    rect = pygame.Rect(
                        x * cell_width,
                        y * cell_height,
                        cell_width,
                        cell_height
                    )

                    # Draw with transparency
                    surface = pygame.Surface((cell_width, cell_height))
                    surface.set_alpha(alpha)
                    surface.fill(color)
                    screen.blit(surface, rect)
```

**Visual Effect:** The horizon appears as a ghostly heat map in the background, showing where entities *used* to be before falling off the observable window. It fades slowly over time (exponential decay) and adapts to movement patterns.

---

## Temporal Effects

### 1. Entity Trails

Render an entity's position across multiple frames in the window, creating a motion trail.

```python
def render_with_trails(self, sliding_window, trail_length=5):
    """
    Render entities with temporal trails.
    """
    for offset in range(min(trail_length, sliding_window.current_window_size)):
        frame = sliding_window.get_frame(offset)
        if not frame:
            break

        # Fade older positions
        fade = 1.0 - (offset / trail_length)
        alpha = int(255 * fade)

        # Render all entities in this frame
        for lag in range(len(frame)):
            current = frame[lag]
            while current:
                entity = current.entity

                # Apply depth scaling
                depth_scale = 1.0 / (1.0 + lag * DEPTH_FACTOR)
                screen_x = int(entity.x * depth_scale + CAMERA_X * (1 - depth_scale))
                screen_y = int(entity.y * depth_scale + CAMERA_Y * (1 - depth_scale))
                radius = max(1, int(BASE_RADIUS * depth_scale * fade))

                # Faded color
                color = tuple(int(c * fade) for c in entity.color)

                # Draw with transparency
                surface = pygame.Surface((radius * 2, radius * 2))
                surface.set_alpha(alpha)
                pygame.draw.circle(surface, color, (radius, radius), radius)
                screen.blit(surface, (screen_x - radius, screen_y - radius))

                current = current.next
```

**Effect:** Each entity leaves a fading trail showing its recent path through space, creating beautiful motion streaks.

### 2. Motion Blur

Blend multiple frame positions into a single blurred image.

```python
def render_with_motion_blur(self, sliding_window, blur_samples=3):
    """
    Render entities with motion blur by blending positions.
    """
    # Accumulate entity positions across frames
    blended_entities = {}

    for offset in range(min(blur_samples, sliding_window.current_window_size)):
        frame = sliding_window.get_frame(offset)
        if not frame:
            break

        weight = 1.0 / (offset + 1)  # Closer frames weighted more

        for lag in range(len(frame)):
            current = frame[lag]
            while current:
                entity = current.entity
                key = entity.uuid  # Track same entity across frames

                if key not in blended_entities:
                    blended_entities[key] = {
                        'x': 0, 'y': 0, 'lag': lag,
                        'color': entity.color, 'weight_sum': 0
                    }

                # Accumulate weighted position
                blended_entities[key]['x'] += entity.x * weight
                blended_entities[key]['y'] += entity.y * weight
                blended_entities[key]['weight_sum'] += weight

                current = current.next

    # Render blended positions
    for data in blended_entities.values():
        if data['weight_sum'] < 0.01:
            continue

        # Average position
        x = data['x'] / data['weight_sum']
        y = data['y'] / data['weight_sum']
        lag = data['lag']

        # Apply depth scaling and render
        depth_scale = 1.0 / (1.0 + lag * DEPTH_FACTOR)
        screen_x = int(x * depth_scale + CAMERA_X * (1 - depth_scale))
        screen_y = int(y * depth_scale + CAMERA_Y * (1 - depth_scale))
        radius = max(1, int(BASE_RADIUS * depth_scale))

        pygame.draw.circle(screen, data['color'], (screen_x, screen_y), radius)
```

**Effect:** Fast-moving entities appear blurred along their motion vector, similar to camera motion blur in photography.

### 3. Ghost Images

Render semi-transparent "ghosts" at previous positions.

```python
def render_with_ghosts(self, sliding_window, ghost_interval=2):
    """
    Render ghost images at regular intervals in the past.
    """
    for offset in range(0, sliding_window.current_window_size, ghost_interval):
        frame = sliding_window.get_frame(offset)
        if not frame:
            break

        # Ghosts become more transparent with age
        alpha = int(128 * (1.0 - offset / sliding_window.current_window_size))

        # Render frame with transparency
        # (similar to trail rendering but at discrete intervals)
```

---

## Temporal Playback Controls

Enable observer navigation through the sliding window.

### Playback State Machine

```python
class PlaybackController:
    def __init__(self):
        self.mode = 'LIVE'  # LIVE, PAUSED, REWIND, FASTFORWARD
        self.playback_offset = 0  # How many frames back from current
        self.playback_speed = 1.0  # Multiplier for simulation rate

    def handle_input(self, event):
        if event.key == pygame.K_SPACE:
            self.toggle_pause()
        elif event.key == pygame.K_LEFT:
            self.rewind()
        elif event.key == pygame.K_RIGHT:
            self.fastforward()
        elif event.key == pygame.K_HOME:
            self.jump_to_oldest()
        elif event.key == pygame.K_END:
            self.jump_to_live()

    def toggle_pause(self):
        if self.mode == 'LIVE':
            self.mode = 'PAUSED'
            self.playback_offset = 0  # Freeze at current frame
        else:
            self.mode = 'LIVE'
            self.playback_offset = 0

    def rewind(self):
        """Step backward one frame."""
        self.mode = 'PAUSED'
        self.playback_offset = min(
            self.playback_offset + 1,
            sliding_window.current_window_size - 1
        )

    def fastforward(self):
        """Step forward one frame."""
        self.mode = 'PAUSED'
        self.playback_offset = max(0, self.playback_offset - 1)
        if self.playback_offset == 0:
            self.mode = 'LIVE'
```

### Rendering with Playback

```python
def render_with_playback(self, sliding_window, playback_controller):
    """
    Render frame based on playback state.
    """
    if playback_controller.mode == 'LIVE':
        frame = sliding_window.get_frame(0)  # Current frame
    else:
        frame = sliding_window.get_frame(playback_controller.playback_offset)

    # Render frame (same as 44_05 bucketing approach)
    for lag in reversed(range(len(frame))):
        current = frame[lag]
        while current:
            self.draw_entity(current.entity, lag)
            current = current.next

    # HUD indicator
    if playback_controller.mode != 'LIVE':
        self.draw_playback_indicator(playback_controller)
```

---

## Performance Analysis

### Complexity Comparison

| Approach | Bucketing | Memory | Window Access | Total Complexity |
|----------|-----------|--------|---------------|------------------|
| **Sorting (baseline)** | O(n log n) | O(n) | N/A (no window) | O(n log n) |
| **Double Buffer (44_05)** | O(n) | O(2n) | N/A (2 frames only) | O(n) |
| **Sliding Window (49)** | O(n) | O(W×n) | O(1) with modulo | O(n) |

Where:
- n = entity count
- W = window size (dynamic, typically 1-100)

**Key Insight:** Bucketing complexity remains O(n) regardless of window size. Memory scales linearly with window size (W), but W adapts to maintain constant frame time.

### Memory Overhead Analysis

**Double Buffer (44_05):**
```
Memory = 2 × MAX_HISTORY × avg_entities_per_bucket × EntityNode_size
        = 2 × 100 × (10000 / 100) × 16 bytes
        = 320 KB for 10k entities
```

**Sliding Window (49):**
```
Memory = W × MAX_HISTORY × avg_entities_per_bucket × EntityNode_size
        = W × 100 × (10000 / 100) × 16 bytes
        = 160 KB × W

For W=5:  800 KB (2.5× more than double buffer)
For W=10: 1.6 MB (5× more)
For W=20: 3.2 MB (10× more)
```

**Holographic Horizon:**
```
Memory = grid_resolution² × (density + energy) × float32_size
        = 100 × 100 × 2 × 4 bytes
        = 80 KB (constant, independent of entity count)
```

**Trade-off:** Sliding window uses more memory but memory scales with window size, which automatically shrinks under load. At 10k entities with 60 FPS target, window typically stabilizes at W=1-5, giving ~320KB to 800KB (comparable to double buffer at low end).

### Expected Performance Characteristics

**Hypothesis:**
1. At low entity counts (< 5k): Large window (W=10-50), deep temporal memory
2. At medium entity counts (5k-20k): Medium window (W=2-10), moderate temporal effects
3. At high entity counts (> 20k): Small window (W=1-2), degrades to double-buffer behavior

**Frame Budget Validation:**

| Entity Count | Expected Frame Time (from 44_05) | Window Size @ 60 FPS | Window Size @ 120 FPS |
|--------------|-----------------------------------|----------------------|-----------------------|
| 1,000 | 1.2ms | min(16.67/1.2, 100) = 13 | min(8.33/1.2, 100) = 6 |
| 5,000 | 4.5ms | min(16.67/4.5, 100) = 3 | min(8.33/4.5, 100) = 1 |
| 10,000 | 8.8ms | min(16.67/8.8, 100) = 1 | min(8.33/8.8, 100) = 1 |
| 50,000 | 42ms | 1 (clamped) | 1 (clamped) |

**Conclusion:** Window size behaves inversely to entity count, automatically managing memory/performance trade-off.

---

## Interactive Controls Summary

| Key | Action | Description |
|-----|--------|-------------|
| **Space** | Pause/Resume | Toggle between LIVE and PAUSED modes |
| **←** | Rewind | Step backward one frame in window |
| **→** | Fast-forward | Step forward one frame toward LIVE |
| **Home** | Jump to oldest | Jump to oldest frame in window |
| **End** | Jump to live | Return to live simulation |
| **T** | Toggle trails | Enable/disable temporal trails |
| **B** | Toggle blur | Enable/disable motion blur |
| **G** | Toggle ghosts | Enable/disable ghost images |
| **H** | Toggle horizon | Show/hide holographic horizon layer |
| **F** | Cycle FPS target | 30 → 60 → 120 → 144 → Unlimited → 30 |
| **+** | Increase entities | Multiply count by 1.5× |
| **-** | Decrease entities | Divide count by 1.5× |
| **M** | Toggle mode | Switch between bucketing/sorting (for comparison) |
| **D** | Toggle HUD | Show/hide statistics overlay |

---

## Validation Criteria

### 1. Functional Requirements

- ✅ Ring buffer correctly wraps around (no index errors)
- ✅ Dynamic window sizing adjusts smoothly with load
- ✅ Temporal effects render without artifacts
- ✅ Playback controls work reliably
- ✅ Holographic horizon compresses/renders correctly
- ✅ Still O(n) bucketing (matches 44_05 performance when W=1)

### 2. Performance Requirements

- ✅ Maintains 60 FPS at target entity counts
- ✅ Window size adapts within 2-3 frames of load change
- ✅ Memory overhead proportional to window size
- ✅ Holographic compression adds < 5% frame time overhead

### 3. Theoretical Validation

- ✅ Theory Doc 46 confirmed: Sorting is still not required
- ✅ Theory Doc 49 demonstrated: Temporal addressability is computationally bounded
- ✅ Theory Doc 26 illustrated: Horizon boundary is observable phenomenon
- ✅ Temporal memory depth inversely correlates with entity count (emergence of computational limits on observation)

---

## Expected Results

### Quantitative Predictions

1. **Bucketing performance matches 44_05** when window size = 1
2. **Memory scales linearly** with window size (measured in MB)
3. **Window size scales inversely** with entity count (power law expected)
4. **Temporal effects add 10-30% overhead** depending on trail length
5. **Holographic horizon adds < 5% overhead** (cheap statistical compression)

### Qualitative Observations

1. **Visual richness**: Temporal trails create more "organic" motion feeling
2. **Playback utility**: Rewind is useful for debugging entity interactions
3. **Horizon persistence**: Background heat map shows "ghost" of past activity
4. **Dynamic adaptation**: Window shrinks/grows visibly under load changes

---

## Connection to Tick-Frame Theory

### Theory Document 49: Temporal Ontology

**Concept:** "Existence buffer: Entities operate within a finite temporal buffer (current tick + accessible memory)"

**Implementation:** Sliding window *is* the existence buffer. Its dynamic size represents the observer's computational limit on temporal addressability.

**Key Insight:** This experiment makes **temporal memory a measurable quantity**:
- Buffer depth = W ticks
- Memory span = W × (1/tick_rate) seconds
- Observer limitation = function of computational budget

### Theory Document 26: Horizon Boundaries

**Concept:** "Observable limits in causal cones. Entities outside the horizon cannot influence each other within finite tick budgets."

**Implementation:**
- Window boundary = horizon
- Frames beyond window = beyond horizon
- Holographic layer = compressed information about beyond-horizon events

**Key Insight:** Horizon is not just spatial but **temporal**. The sliding window implements a temporal horizon where past events become inaccessible (fall off buffer) but their aggregate effect persists (holographic compression).

### Theory Document 46: Temporal Visualization

**Concept:** "Time as a dimension enables O(n) rendering through bucketing instead of O(n log n) sorting."

**Implementation:** Confirmed in 44_05, now extended in 49 to show that temporal bucketing works across multiple frames simultaneously (trails, blur, playback).

**Key Insight:** Temporal effects come "for free" once time is treated as a first-class bucketed dimension.

---

## Implementation Notes

### Technology Stack

- **Python 3.11+**
- **Pygame 2.5+** for rendering
- **NumPy** for holographic horizon grid operations
- **Dataclasses** for Entity structure
- **__slots__** for EntityNode memory optimization
- **Generators** for linked list iteration (lazy evaluation)
- **Idiomatic Python:** Simple loops, clear comprehensions, Pythonic style

**Code Style:** The implementation uses clean, idiomatic Python with simple `for` loops and generators where appropriate. See [PYTHON_STYLE_NOTES.md](PYTHON_STYLE_NOTES.md) for style decisions and lessons learned about functional patterns in Python.

**Performance:** Direct while loops in rendering hot paths, conditional horizon extraction, and optimized bucketing. See [PERFORMANCE_NOTES.md](PERFORMANCE_NOTES.md) for performance analysis and optimizations vs double buffer (44_05).

### Code Structure

```
sliding_window_rendering.py (~600 lines):
├── Entity (dataclass)                  # Entity state
├── EntityNode (class)                  # Linked list node
├── SlidingWindow (class)               # Ring buffer + dynamics
│   ├── on_tick()                       # Bucket and advance
│   ├── get_frame(offset)               # Read frame N ticks back
│   ├── adjust_window_size()            # Dynamic sizing
│   └── get_stats()                     # Metrics
├── HolographicHorizon (class)          # Statistical compression
│   ├── compress_frame()                # Add frame to horizon
│   ├── render()                        # Draw heat map
│   └── get_stats()                     # Horizon metrics
├── PlaybackController (class)          # Temporal navigation
│   ├── handle_input()                  # Keyboard controls
│   ├── toggle_pause()                  # Pause/resume
│   └── get_render_offset()             # Current playback position
├── Simulation (class)                  # Physics (CPU)
│   ├── create_entities()               # Initialize
│   ├── update_tick()                   # Simulate one tick
│   └── get_stats()                     # Sim metrics
├── Renderer (class)                    # Visual output (GPU)
│   ├── render_bucketed()               # O(n) rendering
│   ├── render_with_trails()            # Temporal trails
│   ├── render_with_motion_blur()       # Motion blur
│   ├── render_with_ghosts()            # Ghost images
│   ├── draw_holographic_horizon()      # Horizon layer
│   └── draw_hud()                      # Statistics overlay
└── main()                              # Event loop
```

### Benchmark Structure

```
benchmark_sliding_vs_double.py (~300 lines):
├── approach_sorting()                  # O(n log n) baseline
├── approach_double_buffer()            # O(n) from 44_05
├── approach_sliding_window()           # O(n) with dynamic window
├── run_scaling_test()                  # 100 to 100k entities
├── run_window_size_test()              # Window vs entity count
├── run_memory_test()                   # Memory scaling
└── visualize_results()                 # Plot graphs
```

---

## Files to Create

1. **README.md** (this file) - Theory, design, validation criteria
2. **sliding_window_rendering.py** - Main interactive demo
3. **benchmark_sliding_vs_double.py** - Performance comparison
4. **RESULTS.md** - (Created after experiments run)

---

## Next Steps

1. ✅ Create README.md (this file)
2. ⏳ Implement sliding_window_rendering.py
3. ⏳ Implement benchmark_sliding_vs_double.py
4. ⏳ Run experiments and validate
5. ⏳ Document results in RESULTS.md
6. ⏳ Update main experiments README to reference 49

---

## Success Metrics

**Experiment is successful if:**

1. ✅ Dynamic window adapts correctly to entity count
2. ✅ Maintains target FPS across all entity counts tested
3. ✅ Temporal effects (trails/blur) render without visual artifacts
4. ✅ Playback controls work smoothly
5. ✅ Holographic horizon visualizes past activity meaningfully
6. ✅ Still O(n) bucketing (validates 44_05 at W=1)
7. ✅ Memory scales linearly with window size (measured)
8. ✅ Theory Doc 49's "existence buffer" concept is demonstrable

**Experiment reveals new insights if:**

- Window size vs entity count follows predictable scaling law
- Holographic compression preserves useful aggregate information
- Temporal effects enable new forms of visualization
- Observer limitations on temporal addressability are quantifiable

---

**Last Updated:** 2026-01-13
**Status:** Ready for implementation
**Related Experiments:** 44_05 (Double Buffer Rendering)
**Theory Documents:** 26 (Horizon), 46 (Temporal Visualization), 49 (Temporal Ontology)
