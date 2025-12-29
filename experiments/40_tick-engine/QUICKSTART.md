# Quick Start Guide

## Install & Run (5 minutes)

### 1. Navigate to the engine

```bash
cd experiments/39_tick-engine
```

### 2. Run Law-000 XOR (Theoretical Baseline)

```bash
python examples/run_law000_xor.py
```

**Expected Output:**
```
LAW-000 XOR: Theoretical Baseline Evolution
============================================

[Viz 1] Tick 669 (dt=669)
  Graph: 130 nodes, 120 new edges
  States: 21679:X 21680:X 21681:X ...

[Viz 2] Tick 685 (dt=16)
  Graph: 20 nodes, 10 new edges
  States: 22339:. 22340:. 22341:. ...
```

### 3. Run Law-Quaternion (3D Spatial Dynamics)

```bash
python examples/run_law_quaternion.py
```

**Expected Output:**
```
LAW-QUATERNION: 3D Movement via Quaternion Algebra
===================================================

[Viz 1] Tick 633 (dt=633)
  Graph: 61 nodes
  Node 6026: q=(0.778, 0.241, 0.581, 0.000)
    3D: (0.241, 0.581, 0.000)
    Energy: 0.629
```

## What Just Happened?

✅ **Asynchronous Tick Engine** - Simulation ran in background at max speed
✅ **Observer-Relative Time** - Variable dt (669, 16, 22...) proves async consumption
✅ **Law Pluggability** - Same engine, different physics laws
✅ **Graph Dynamics** - Automatic growth and collapse

## Key Observations

### Law-000 XOR Behavior
- **Binary states** (X=active, .=inactive)
- **Pure XOR evolution** - theoretical baseline
- **Growth/collapse cycles** - graph oscillates between 20-130 nodes
- **Fast execution** - thousands of ticks in seconds

### Law-Quaternion Behavior
- **Quaternion states** (w, x, y, z)
- **3D spatial dynamics** - nodes move in imaginary space
- **Energy decay** - tends toward identity quaternion (1,0,0,0)
- **Smooth evolution** - renormalization keeps magnitudes bounded

## Next Steps

### Create Your Own Law

```python
# laws/my_law.py
class MyLaw:
    name = "My Law"
    StateType = float

    def evolve(self, graph, state, tick):
        # Your physics here
        return new_state
```

### Run Comparative Experiments

```python
# Compare same initial conditions with different laws
law_a = Law000_XOR()
law_b = LawQuaternion()

# Run both, analyze differences
```

### Modify Parameters

Edit the example files:
- `sample_interval` - visualization frequency
- `collapse_interval` - graph cleanup frequency
- `buffer_size` - tick snapshot history

## Common Issues

**Q: Graph grows too fast, runs out of memory**

A: Reduce `collapse_interval` or make `should_grow()` more restrictive

---

**Q: Visualization lags behind simulation**

A: Increase `sample_interval` to reduce viz load

---

**Q: Want to see more ticks**

A: Change `max_visualizations` in the example files

## Architecture at a Glance

```
Law (physics rules)
  ↓
Substrate (graph + states)
  ↓
TickEngine (async producer)
  ↓
VisualizationEngine (async consumer)
  ↓
Your analysis/visualization
```

## Read More

- **Full Documentation:** See README.md
- **Theory Background:** See `docs/theory/`
- **Law Interface:** See `engine/law_interface.py`

---

**Have fun experimenting! 🚀**
