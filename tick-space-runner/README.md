# Tick-Space Runner

Java implementation of a discrete tick-frame substrate simulation engine based on tick-frame physics theory.

## Overview

This project implements a working computational model of a tick-frame universe where:
- Time advances in discrete **ticks** (not continuous)
- Space expands with each tick following dimensional growth rules
- Entities are **collision patterns** that persist through temporal renewal
- The substrate operates deterministically at the root layer

This is an operational validation of theoretical principles developed in `docs/theory/`, particularly:
- **Temporal Surfing Principle** (Doc 28) - entities persist through continual renewal
- **Collision Persistence Principle** (Doc 30) - entities as collision patterns
- **Imbalance Theory** (Doc 29) - matter-antimatter emergence from expansion
- **Horizon Boundaries** (Doc 26) - observable limits in causal cones

## Architecture

### Core Components

#### 1. `TickTimeModel`
**Location:** `src/main/java/eu/jerrysamek/tickspace/model/ticktime/`

The fundamental time engine that drives the entire simulation.

**Key features:**
- Discrete time advancement (ticks as `BigInteger`)
- Scheduled execution at 10 ms intervals
- Parallel task execution using a work-stealing pool
- Performance monitoring (update time, execution time per tick)
- Fires `onTick()` events to registered consumers

**Usage:**
```java
var tickTime = new TickTimeModel(substrate, afterTickCallback);
tickTime.start();
```

#### 2. `SubstrateModel`
**Location:** `src/main/java/eu/jerrysamek/tickspace/model/substrate/`

Represents the dimensional substrate that expands with each tick.

**Key features:**
- Manages dimensional growth (`DimensionalSize`)
- N-dimensional space (configurable, typically 3D; based on the experiments)
- Receives tick updates and propagates to entity registry
- Coordinates substrate expansion and entity evolution

**Components:**
- `DimensionalSize` - tracks dimensional lengths per tick
- `Position` - N-dimensional coordinate wrapper
- `SubstrateModelUpdate` - update functor interface

**Initialization:**
```java
var substrate = new SubstrateModel(3, entitiesRegistry);  // 3D space
```

#### 3. `EntitiesRegistry`
**Location:** `src/main/java/eu/jerrysamek/tickspace/model/entity/`

Central registry managing all entities in the substrate using spatial indexing.

**Key features:**
- Concurrent spatial hash map (`Position` → `EntityModel`)
- Collision detection and resolution
- Entity lifecycle management (creation, movement, collision, death)
- Snapshot generation for analysis/visualization
- Seeding at tick=1 with an initial entity at origin

**Collision handling:**
- When two entities occupy same position → `CollidingEntityModel` created
- Collision patterns can persist or dissolve based on energy dynamics

**Methods:**
```java
Collection<EntityModel> snapshot()  // Current entity state
int count()                          // Total entity count
```

### Entity Models

#### `EntityModel` (Abstract)
**Location:** `src/main/java/eu/jerrysamek/tickspace/model/entity/EntityModel.java`

Base abstraction for all entities in the substrate.

**Properties:**
- `uuid` - unique identifier
- `position` - N-dimensional coordinates
- `energy` - entity energy level
- `depth` - hierarchy depth (for composite entities)
- `momentum` - directional movement vector

**Lifecycle:**
- Each entity processes `onTick()` → generates `EntityModelUpdate`
- Updates applied by registry → new position/state
- Entities can spawn, move, collide, or dissolve

#### `SingleEntityModel`
Simple atomic entity with position, energy, and momentum.

**Behavior:**
- Moves, according to momentum vector, each tick
- Energy may dissipate over time
- Represents fundamental particle-like substrate units

#### `CollidingEntityModel`
**Location:** `src/main/java/eu/jerrysamek/tickspace/model/entity/CollidingEntityModel.java`

Composite entity formed when two entities occupy the same position.

**Theory:** Implements **Collision Persistence Principle** - entities persist through collision patterns, not static identity.

**Behavior:**
- Combines energy and momentum from colliding entities
- May fragment, persist, or dissolve based on collision dynamics
- Represents emergent structures from substrate interactions

**Factory:**
```java
CollidingEntityModel.of(entity1, entity2)
```

#### Supporting Classes
- `Momentum` - encapsulates direction and magnitude
- `CollisionModel` - collision detection and energy transfer logic
- `Utils` - substrate manipulation utilities

## Runners

### 1. LocalApp
**Location:** `src/main/java/eu/jerrysamek/tickspace/runner/LocalApp.java`

Primary simulation runner that executes tick-frame substrate and exports JSON snapshots.

**Configuration:**
- Dimensional space: 3D
- Snapshot interval: every 1000 ticks
- Output directory: `W:\data\snapshots\`
- File format: `time-frame.{tick}.json`

**Features:**
- Asynchronous snapshot serialization (separate daemon thread)
- Jackson JSON serialization
- Real-time statistics logging (dimensional size, entity count)
- Continuous execution until manually stopped or OOM occurs

**Run:**
```bash
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"
```

**Output example:**
```
====== tick 5000 ======
 - dimensional bounds: DimensionalSize{dimensionCount=3, dimensions=[5001, 5001, 5001]}
 - entities: 1523
 - new snapshot generated
 - statistics: update=12.45 ms, execution=87.32 ms, total=99.77 ms
====== tick 5001 ======
 - dimensional bounds: DimensionalSize{dimensionCount=3, dimensions=[5002, 5002, 5002]}
 - entities: 1547
 - statistics: update=11.89 ms, execution=89.21 ms, total=101.10 ms
```

### 2. Simple3DServer
**Location:** `src/main/java/eu/jerrysamek/tickspace/runner/Simple3DServer.java`

⚠️ **STATUS: NOT YET READY** - Placeholder for real-time 3D visualization server.

**Intended purpose:**
- WebSocket server on `ws://localhost:8080/viewcone`
- Stream live substrate state to 3D visualization clients
- Viewcone-based rendering (observable horizon)

**Current state:**
- Generates dummy brick data (random energy field)
- Basic Undertow WebSocket infrastructure in place
- **NOT CONNECTED TO ACTUAL SUBSTRATE MODEL**

**Roadmap:**
- Integrate with `SubstrateModel` and `EntitiesRegistry`
- Implement viewcone filtering based on observer position
- Support client-side 3D rendering (Three.js, Unity, etc.)
- Optimize for large entity counts (spatial culling)

## JSON Snapshot Format

Snapshots are exported as JSON arrays of entity objects:

```json
[
  {
    "uuid": "550e8400-e29b-41d4-a716-446655440000",
    "position": {
      "coordinates": [12, -5, 8]
    },
    "energy": 1523,
    "depth": 0,
    "momentum": {
      "magnitude": 10,
      "direction": [1, 0, 0]
    }
  },
  ...
]
```

**Analysis tools:** See `scripts/README.md` for Python analysis scripts:
- `snapshot-stats.py` - statistical summaries by radial shells
- `snapshot-visualization.py` - 3D scatter plots
- `snapshot-energy-histogram.py` - energy distributions and density profiles

## Building and Running

### Prerequisites
- Java 25+ (uses virtual threads, pattern matching)
- Maven 3.9+

### Build
```bash
mvn clean package
```

### Run Local Simulation
```bash
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"
```

**Note:** Ensure output directory exists:
```bash
mkdir -p W:\data\snapshots
```

### Dependencies
- **Undertow** (2.3.20) - lightweight HTTP/WebSocket server
- **Jackson** (2.18.2) - JSON serialization

## Key Observations from Current Implementation

### Emergence Patterns
- **Over-coherence:** Current `EntityModel` implementation produces structures that are too uniform
- **Anisotropy deficit:** Need more irregular, chaotic emergence patterns
- **Collision dynamics:** Balancing persistence vs. dissolution rates remains challenging

### Performance
- Typical tick execution: ~100ms total
  - Update phase: ~10-20ms (entity state updates)
  - Execution phase: ~80-90ms (parallel entity processing)
- Scales with entity count (currently tested up to ~10K entities)
- Bottleneck: collision detection in dense regions

### Theoretical Validation
- ✅ Entities do exhibit temporal surfing behavior
- ✅ Collision patterns create composite structures
- ✅ Expansion follows dimensional growth rules
- ⚠️ Emergence complexity lower than expected (too deterministic)
- ⚠️ Matter-antimatter asymmetry not yet clearly observable

## Theoretical Foundation

This implementation operationalizes concepts from the tick-frame physics theory:

**Core documents:**
- `docs/theory/28 Temporal Surfing Principle.md` - entities surf time through renewal
- `docs/theory/29 Imbalance Theory in Tick‑Frame Universe.md` - structural asymmetry
- `docs/theory/30 Collision Persistence Principle in Tick-Frame.md` - collision-based identity
- `docs/theory/27 Length Definition in Tick‑Frame Substrate.md` - temporal measurement
- `docs/theory/26 Horizon Boundaries in Tick‑Frame Subst.md` - observable limits

**Experimental validation:**
- `docs/theory/00 Meta-Critical Theory Development Log.md` - Section 10 documents this implementation phase
- 3,960 dimensional simulations (1D-5D) validated substrate behavior
- Java implementation tests collision theory in practice

## Development Status

**Phase 7 (Operational Substrate):** IN PROGRESS

**Completed:**
- ✅ Tick-time engine with parallel execution
- ✅ Substrate model with dimensional expansion
- ✅ Entity registry with collision detection
- ✅ Single and colliding entity models
- ✅ JSON snapshot export system
- ✅ LocalApp runner with statistics

**In Progress:**
- ⚠️ Refining entity dynamics to reduce over-coherence
- ⚠️ Tuning collision persistence parameters
- ⚠️ Optimizing performance for larger entity counts

**Not Started:**
- ❌ Simple3DServer integration with substrate model
- ❌ Real-time visualization client
- ❌ Viewcone-based rendering
- ❌ Advanced collision patterns (multi-entity interactions)
- ❌ Energy dissipation and conservation laws

## Future Enhancements

1. **Emergence tuning:**
   - Introduce stochastic perturbations at substrate level
   - Experiment with different collision resolution strategies
   - Implement energy conservation and dissipation rules

2. **Visualization:**
   - Complete Simple3DServer integration
   - Build web-based 3D viewer (Three.js)
   - Real-time entity tracking and lineage visualization

3. **Analysis:**
   - Time-series analysis across snapshots
   - Collision event tracking and pattern detection
   - Automated emergence metrics (complexity, entropy, structure)

4. **Performance:**
   - Spatial indexing optimization (octree, grid partitioning)
   - GPU acceleration for collision detection
   - Distributed substrate across multiple nodes

5. **Theoretical validation:**
   - Measure imbalance emergence quantitatively
   - Track matter-antimatter analogue formation
   - Validate horizon boundary predictions

## License

See `LICENSE` file in project root.

## References

- Theory documentation: `docs/theory/`
- Snapshot analysis scripts: `scripts/README.md`
- Development log: `docs/theory/00 Meta-Critical Theory Development Log.md`
