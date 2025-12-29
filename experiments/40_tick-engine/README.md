# 39_tick-engine: Unified Tick-Frame Physics Engine

**A pluggable, law-agnostic engine for exploring tick-frame physics theories.**

## Overview

This is a **unified engine architecture** that separates physics simulation from substrate laws. You can:

✅ **Plug in different laws** - XOR, Quaternion, Game of Life, custom rules
✅ **Run comparative experiments** - Same initial conditions, different laws
✅ **Validate theory** - Implement theoretical laws exactly as documented
✅ **Visualize any law** - Generic 3D rendering adapts to state type
✅ **Async tick-visualization** - Observer-relative time built-in

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Law Interface                        │
│  (Protocol defining how laws must behave)               │
└─────────────────────────────────────────────────────────┘
                           ▲
                           │ implements
                           │
        ┌──────────────────┴──────────────────┐
        │                                     │
   Law-000 XOR                         Law-Quaternion
   (binary states)                     (quaternion states)
        │                                     │
        └──────────────────┬──────────────────┘
                           │ used by
                           ▼
              ┌────────────────────────┐
              │   Generic Substrate    │
              │  (law-parameterized)   │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │   Generic TickEngine   │
              │  (async producer)      │
              └────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  VisualizationEngine   │
              │  (async consumer)      │
              └────────────────────────┘
```

## Directory Structure

```
39_tick-engine/
├── engine/                      # Generic engine (law-agnostic)
│   ├── law_interface.py         # Protocol definition for laws
│   ├── substrate.py             # Generic substrate class
│   ├── tick_engine.py           # Async tick producer
│   └── visualization_engine.py  # Async viz consumer
│
├── laws/                        # Pluggable law implementations
│   ├── law000_xor.py           # Theoretical Law-000 (binary XOR)
│   └── law_quaternion.py       # Experimental quaternion law
│
├── examples/                    # Example runners
│   ├── run_law000_xor.py       # Run XOR evolution
│   └── run_law_quaternion.py   # Run quaternion evolution
│
└── README.md                    # This file
```

## Quick Start

### Running Law-000 XOR

```bash
cd experiments/39_tick-engine
python examples/run_law000_xor.py
```

**Output:**
```
[Viz 1] Tick 5 (dt=5)
  States: 0:· 1:█ 2:· 3:· 4:·

[Viz 2] Tick 10 (dt=5)
  States: 0:█ 1:· 2:█ 3:· 4:█
```

### Running Law-Quaternion

```bash
cd experiments/39_tick-engine
python examples/run_law_quaternion.py
```

**Output:**
```
[Viz 1] Tick 10 (dt=10)
  Node 0: q=(0.888, 0.175, 0.426, 0.000)
    → 3D coords: (0.175, 0.426, 0.000)
    → Energy: 0.460
```

## Creating a New Law

### 1. Define Your Law Class

```python
# laws/my_custom_law.py

from typing import Dict, List, Tuple

class MyCustomLaw:
    name = "My Custom Law"
    description = "What this law does"

    StateType = float  # or int, tuple, etc.

    def initial_state(self, node_id: int) -> float:
        return 0.0

    def evolve(self, graph, state, tick) -> Dict[int, float]:
        new_state = {}
        for node, neighbors in graph.items():
            # Your evolution logic here
            new_state[node] = ...
        return new_state

    def should_grow(self, node_id, node_state, neighbors, neighbor_states) -> bool:
        # Growth condition
        return ...

    def to_3d_coords(self, state_value: float) -> Tuple[float, float, float]:
        # Map state to 3D space
        return (state_value, 0.0, 0.0)

    def to_color(self, state_value: float) -> Tuple[int, int, int]:
        # Map state to RGB
        return (int(state_value * 255), 0, 0)
```

### 2. Create a Runner

```python
# examples/run_my_law.py

from engine.substrate import Substrate
from engine.tick_engine import TickEngine
from engine.visualization_engine import VisualizationEngine
from laws.my_custom_law import MyCustomLaw

law = MyCustomLaw()
graph = {0: [1], 1: [0, 2], 2: [1]}
initial_state = {0: 0.0, 1: 1.0, 2: 0.0}

substrate = Substrate(graph, initial_state, law)
engine = TickEngine(substrate)
viz = VisualizationEngine(engine, law)

engine.start()
# ... consume visualizations
engine.stop()
```

### 3. Run It

```bash
python examples/run_my_law.py
```

That's it! The unified engine handles everything else.

## Law Interface Specification

All laws must implement these methods:

| Method | Purpose | Returns |
|--------|---------|---------|
| `initial_state(node_id)` | State for new nodes | `StateType` |
| `evolve(graph, state, tick)` | Core evolution rule | `Dict[int, StateType]` |
| `should_grow(...)` | Growth condition | `bool` |
| `to_3d_coords(state)` | Visualization mapping | `(x, y, z)` |
| `to_color(state)` | Color mapping | `(r, g, b)` |

Optional methods:
- `state_summary(state)` → Human-readable string
- `state_energy(state)` → Scalar energy metric

## Included Laws

### Law-000 XOR

**Theory:** `docs/theory/39_0 Law‑000 XOR Parity Rule.md`

**State:** Binary {0, 1}

**Evolution:** `S'(n) = S(n) ⊕ P(n) ⊕ chaos`

**Properties:**
- Parameter-free
- Deterministic
- Pure XOR parity logic
- Theoretical baseline

### Law-Quaternion

**Theory:** Experimental (not in baseline theory)

**State:** Quaternion (w, x, y, z)

**Evolution:** `q'(n) = normalize(q(n) + 0.1 * dq)`

**Properties:**
- 3D spatial dynamics
- Chaos injection in real part
- Renormalization constraint
- Emergent cooling behavior

## Engine Features

### Asynchronous Architecture

**Tick Producer (TickEngine):**
- Runs in background thread
- Generates ticks at max speed
- Stores snapshots in bounded buffer (FIFO)
- Never blocks on visualization

**Visualization Consumer (VisualizationEngine):**
- Pulls ticks when ready
- Computes backward state differences
- Tracks lag and processing time
- Implements observer-relative time

### Observer-Relative Time

```
[Viz 1] Tick 25 (dt=25, lag=0)
[Viz 2] Tick 71 (dt=46, lag=0)  ← Variable dt!
[Viz 3] Tick 100 (dt=29, lag=0)
```

**Variable tick deltas** prove independent tick production and asynchronous consumption.

### Automatic Graph Management

- **Growth:** Delegated to law's `should_grow()` method
- **Collapse:** Periodic pruning to keep graph bounded
- **Horizon:** BFS-based distance limiting

## Theory Alignment

### ✅ Implements

- **No Future Principle** - Ticks generated one at a time
- **Observer Sleep** - Visualization skips ticks when overloaded
- **Temporal Surfing** - State renewal at each tick
- **Horizon Boundaries** - Bounded buffer = finite causal past
- **Observer-Relative Time** - Each viz has its own dt

### ⚠️ Partial

- **Collision Persistence** - No collision-based entities yet
- **Death on Renewal Failure** - Manual collapse, not organic

### ❌ Not Yet

- **Collision-based entity emergence**
- **Failure-driven decay**
- **Multi-law composition**

## Configuration

### TickEngine Parameters

```python
TickEngine(
    substrate=substrate,
    buffer_size=200,          # Snapshots to keep
    collapse_interval=10,     # Collapse every N ticks (0=never)
    collapse_size=5           # Edges to keep when collapsing
)
```

### VisualizationEngine Parameters

```python
VisualizationEngine(
    tick_engine=engine,
    law=law,
    sample_interval=25        # Visualize every N ticks
)
```

## Performance

**Typical Performance (10 ticks/ms):**
- Law-000 XOR: Ultra-fast (bitwise ops)
- Law-Quaternion: ~100 nodes/tick (floating-point)

**Bottlenecks:**
- Growth rate (exponential can saturate)
- Collapse frequency (graph cleanup overhead)
- State complexity (larger states = slower evolution)

**Optimization:**
- Increase `collapse_interval` for faster growth
- Decrease `sample_interval` for more frequent viz
- Use simpler state types for speed

## Comparative Experiments

### Same Initial Conditions, Different Laws

```python
# Run both laws with identical graphs
from laws.law000_xor import Law000_XOR
from laws.law_quaternion import LawQuaternion

graph = {0: [1], 1: [0, 2], 2: [1]}

# Law-000
law_xor = Law000_XOR()
state_xor = {0: 0, 1: 1, 2: 0}
substrate_xor = Substrate(graph.copy(), state_xor, law_xor)

# Law-Quaternion
law_quat = LawQuaternion()
state_quat = {0: (1,0,0,0), 1: (0,1,0,0), 2: (0,0,1,0)}
substrate_quat = Substrate(graph.copy(), state_quat, law_quat)

# Run both in parallel, compare results
```

## Extending the Engine

### Custom Visualization

Override `render_3d_points()` in VisualizationEngine:

```python
class CustomViz(VisualizationEngine):
    def custom_render(self, snapshot):
        # Your visualization logic
        return custom_output
```

### Multi-Law Substrates

```python
class CompositeLaw:
    def __init__(self, law_a, law_b, partition_fn):
        self.law_a = law_a
        self.law_b = law_b
        self.partition = partition_fn

    def evolve(self, graph, state, tick):
        # Apply law_a to region A, law_b to region B
        ...
```

### Export Snapshots

```python
# Export to JSON
import json
snapshot = engine.get_latest_snapshot()
with open("snapshot.json", "w") as f:
    json.dump({
        "tick": snapshot.tick,
        "graph": snapshot.graph,
        "state": snapshot.state
    }, f)
```

## Troubleshooting

**Problem:** Law not found when running examples

**Solution:** Make sure you're in the `39_tick-engine` directory

---

**Problem:** Visualization lags behind simulation

**Solution:** Increase `sample_interval` or decrease `collapse_interval`

---

**Problem:** Graph grows too fast, OOM

**Solution:** Reduce `collapse_interval` or make `should_grow()` more restrictive

---

**Problem:** States not visualizing correctly

**Solution:** Check `to_3d_coords()` and `to_color()` implementations

## Future Work

- [ ] Add more laws (Game of Life, Wave Equation, etc.)
- [ ] Implement collision-based entities
- [ ] Add failure-driven decay
- [ ] GPU acceleration for large graphs
- [ ] Real-time 3D visualization
- [ ] Snapshot replay system
- [ ] Comparative analysis tools
- [ ] Law composition framework

## Citation

If using this engine for research, please cite:

```
Tick-Frame Physics Engine
https://github.com/jerry-samek/tick-frame-space
experiments/39_tick-engine
```

## License

Same as parent project.

---

**Happy experimenting! 🚀**

For questions or contributions, see parent project README.
