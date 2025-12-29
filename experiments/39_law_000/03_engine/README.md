# 03_engine: Asynchronous Tick-Frame Engine

## Architecture Overview

This framework decouples simulation from visualization using a **producer-consumer pattern**:

### Components

**1. TickEngine (Producer)**
- Runs simulation in background thread independently
- Generates tick snapshots at maximum speed
- Stores snapshots in bounded buffer (FIFO queue)
- Automatically collapses graph every 10 ticks to keep it bounded

**2. VisualizationEngine (Consumer)**
- Consumes snapshots at its own pace
- Only pulls next tick when ready (non-blocking)
- Computes backward state difference: Δt = tick(n) - tick(n-v)
- Tracks processing time and lag statistics

**3. TickSnapshot (Data)**
- Immutable snapshot of substrate state at specific tick
- Contains: tick number, graph, quaternion state, timestamp
- Deep-copied to avoid mutation

### Key Features

✓ **Independent tick production** - Simulation never blocks on visualization
✓ **Backward state computation** - Edge diff computed from tick delta
✓ **Variable visualization rate** - dt varies based on processing speed
✓ **Bounded buffer** - Last 200 snapshots kept (configurable)
✓ **Thread-safe** - Lock-protected snapshot queue
✓ **Lag tracking** - Monitor how far behind visualization is

## Example Output

```
[Viz 1] Tick 26 (dt=26, lag=0 ticks)
  Graph: 10 nodes
  Edges: +5 -0
  Buffer: 26 snapshots (1, 26)

[Viz 2] Tick 71 (dt=45, lag=0 ticks)
  Graph: 10 nodes
  Edges: +5 -5
  Buffer: 71 snapshots (1, 71)
```

- **dt=26, dt=45**: Variable tick deltas show async consumption
- **lag=0**: Visualization keeping up with simulation
- **Buffer (1, 71)**: Oldest and newest tick in buffer

## Running

```bash
cd experiments/39_law_000/03_engine
python main.py
```

## Configuration

In `main.py`:
- `SAMPLE_INTERVAL = 25` - Visualize every N ticks
- `BUFFER_SIZE = 200` - Keep last N snapshots
- `MAX_VISUALIZATIONS = 40` - Stop after N visualizations

In `tick_engine.py:65-66`:
- Collapse frequency: every 10 ticks
- Collapse size: keep 5 edges

## Architecture Diagram

```
┌─────────────────┐
│  TickEngine     │ (Background Thread)
│  - Compute      │
│  - Grow         │
│  - Apply Law    │
│  - Collapse     │
└────────┬────────┘
         │ produces
         ▼
┌─────────────────┐
│ Snapshot Buffer │ (Thread-safe Queue)
│  maxlen=200     │
└────────┬────────┘
         │ consumes when ready
         ▼
┌─────────────────┐
│ VizEngine       │ (Main Thread)
│  - Pull next    │
│  - Compute Δt   │
│  - Edge diff    │
│  - Render       │
└─────────────────┘
```

## Why This Design?

**Problem**: Old framework blocked simulation during visualization
- Rendering PNG takes time
- Exporting JSON/CSV takes time
- Simulation waited for each visualization to complete

**Solution**: Decouple with async architecture
- Simulation runs at max speed independently
- Visualization processes snapshots when ready
- Backward computation from tick delta
- No blocking, no waiting

## Theory Connection

This implements the **Observer-Relative Tick Principle**:
- Each observer (visualization) experiences time at its own rate
- Simulation tick-frame advances independently
- Delta computed backward from observer's last observation
- Matches tick-frame theory: observers don't share universal "now"
