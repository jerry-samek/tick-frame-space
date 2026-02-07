# V17 - Canvas Ontology with Sparse Storage

## Overview

V17 implements the **canvas/renderer** model for tick-frame physics with sparse gamma storage, achieving O(entities) memory instead of O(grid³).

## Conceptual Foundation

### The Canvas Model

The key insight is that the gamma field **IS** the tick window state - not "memory of history" but "the canvas with all paint on it".

```
Renderer (stateless temporal process)
    ↓ reads canvas state
Canvas (accumulated paint from all ticks)
    ↓ gradient influences
Next Paint Position (renderer's decision)
    ↓ new paint added to
Canvas (state for next tick)
```

### Ontological Principles

1. **Renderer is stateless**: It only sees the current canvas, decides where to paint next
2. **Canvas IS the state**: No external memory - the accumulated paint is the only state
3. **Tick independence preserved**: Each tick only sees current canvas state (which happens to be accumulated)
4. **Patterns are gamma-bound**: Not position-bound. The renderer keeps painting in the same region because **gradient points to existing paint**

### What "Staying Still" Means

- NOT about coordinates
- The renderer keeps painting in the same region because **gradient points to existing paint**
- Patterns are gamma-bound, not position-bound
- Expanding space gives more canvas, but renderer stays near its paint

## Architecture

```
v17/
├── __init__.py           # Package exports
├── config_v17.py         # Simplified config (no grid size!)
├── canvas.py             # Canvas3D - sparse gamma storage
├── renderer.py           # Renderer - stateless paint decision
├── evolution.py          # TickEvolution - orchestration
├── experiment_v17.py     # Experiments and tests
├── results/              # Experiment outputs
└── README.md             # This file
```

## Key Classes

### Canvas3D

The tick window state with sparse gamma storage.

```python
class Canvas3D:
    """Sparse gamma storage using dict."""

    gamma: Dict[Tuple[int,int,int], float]  # Only non-zero values stored

    def get_gamma(self, pos) -> float:
        """Get gamma at position (0.0 if never painted)."""

    def paint(self, pos, strength=1.0):
        """Add paint to canvas at position."""

    def get_gradient(self, pos) -> Tuple[float, float, float]:
        """Compute gradient from sparse neighbors."""

    def get_effective_gamma(self, pos, radius=3) -> float:
        """Normalized local gamma for energy budget."""
```

### Renderer

Stateless entity that decides where to paint.

```python
class Renderer:
    """Stateless temporal process."""

    last_paint_pos: Tuple[int,int,int]  # Where we last painted

    def render_tick(self, canvas) -> Optional[Tuple[int,int,int]]:
        """Decide where to paint. Returns None if skipped."""
        # 1. Compute gradient at current position
        # 2. Skip probability = |gradient| * sensitivity (time dilation)
        # 3. If gradient significant: move toward higher gamma
        # 4. If gradient ~zero: small random jitter
        # 5. Paint at new position
```

### TickEvolution

Orchestrates the canvas/renderer model.

```python
class TickEvolution:
    """Tick evolution orchestrator."""

    canvas: Canvas3D
    renderers: List[Renderer]

    def evolve_one_tick(self):
        """One tick: create renderer, all renderers paint."""
```

## Physical Model

Gradient-following movement with time dilation resistance:

| Constant | Value | Meaning |
|----------|-------|---------|
| `SKIP_SENSITIVITY` | 0.01 | Skip probability per unit gradient |
| `JITTER_STRENGTH` | 0.1 | Random step probability when gradient ~0 |
| `GRADIENT_THRESHOLD` | 0.01 | Below this, use jitter instead of gradient |
| `GAMMA_IMPRINT` | 1.0 | One action = one paint |
| `ENERGY_PER_TICK` | 1.0 | Entity receives 1 energy/tick |
| `LOCAL_RADIUS` | 3 | Radius for effective gamma sampling |

**Movement model:**
1. Gradient pulls renderer toward higher gamma (like gravity toward mass)
2. `skip_prob` = |gradient| × SKIP_SENSITIVITY (resistance via time dilation)
3. If gradient > threshold: move one step in gradient direction
4. If gradient ≤ threshold: small random jitter with `JITTER_STRENGTH`

## Memory Comparison

| Scenario | V16 (Dense) | V17 (Sparse) |
|----------|-------------|--------------|
| 500 ticks, 176³ grid | ~2 GB | ~50 MB |
| 1000 ticks | Memory limit | ~100 MB |
| 10000 ticks | Impossible | ~1 GB |

Sparse storage scales with O(painted_cells), not O(grid_volume).

## Running Experiments

```bash
# Quick test (100 ticks)
python experiment_v17.py --test quick

# Standard run (1000 ticks)
python experiment_v17.py --test standard

# Long run (10000 ticks) - only possible with sparse storage!
python experiment_v17.py --test longrun --ticks 10000

# Memory scaling test
python experiment_v17.py --test memory

# Pattern formation test
python experiment_v17.py --test pattern

# Run all tests
python experiment_v17.py --test all

# Save results to JSON
python experiment_v17.py --test standard --save
```

## Metrics

| Metric | Description |
|--------|-------------|
| `painted_cells` | Number of cells with gamma > 0 |
| `memory_mb` | Actual memory usage |
| `r_mean` | Mean weighted radius of paint from origin |
| `gamma_sum` | Total paint on canvas |
| `skip_rate` | Fraction of ticks skipped |
| `gradient_mean` | Mean gradient magnitude at renderer positions |
| `renderer_r_mean` | Mean distance of renderers from origin |

## Why Sparse Storage is Correct

The canvas ontology clarifies that **only painted regions matter**:

1. **Unpainted regions have no gradient** - they don't influence renderer behavior
2. **Memory grows with paint, not with space** - space can be infinite
3. **The canvas IS the complete state** - nothing else needs to be stored
4. **Gradient computation is local** - only nearby paint matters

This makes sparse storage not just an optimization, but ontologically correct.

## Comparison with V16

V17 is behaviorally equivalent to V16 but with:

1. **No grid size parameter** - space is inherently infinite
2. **No expansion parameters** - no need to expand what's already infinite
3. **O(entities) memory** - not O(grid³)
4. **Cleaner ontology** - code reflects the canvas/renderer model

The physics (skip probability, jitter, gamma accumulation) are identical.

## Behavioral Differences from V16

V17 has intentional architectural differences that affect dynamics:

### V16: Per-Entity Layers
- Each entity owns a dedicated layer
- Pattern evolution happens within that layer
- Gamma field is shared, but pattern cells are per-entity
- Patterns self-reinforce through layer jitter

### V17: Shared Canvas
- All entities share a single canvas
- No per-entity pattern tracking
- Renderers paint to shared gamma field
- Each renderer tracks only its last paint position

### Observed Behavior (After Gradient-Following Fix)
- **Origin accumulation**: New renderers paint at origin, creating high gamma concentration
- **Gradient following**: Renderers move toward higher gamma (pulled toward mass)
- **Skip-based resistance**: Time dilation prevents falling directly into center
- **Stable clustering**: Balance between pull and skip creates stable position

The gradient-following model acts like gravity:
- Gradient pulls renderer toward gamma mass (like gravitational attraction)
- Skip mechanism provides resistance (like time dilation near mass)
- Balance determines stable orbital-like position near the gamma center

### Expected Behavior
- `r_mean` should stabilize (not grow linearly)
- Renderers cluster near origin where gamma accumulates
- Higher gamma = more time dilation = slower local time

## Future Directions

1. **Multi-scale analysis**: With unlimited ticks, study long-term pattern dynamics
2. **Equilibrium detection**: When does r_mean stabilize?
3. **Pattern fragmentation**: Do patterns naturally find stable sizes?
4. **Collision behavior**: What happens when patterns overlap?
5. **Per-renderer layers**: Extend to V17.1 with per-renderer pattern tracking
