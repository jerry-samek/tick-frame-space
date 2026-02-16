# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Tick-Frame Space is a discrete tick-based physics simulation engine implementing a speculative model where time advances in discrete ticks, space expands with each tick, and entities are collision patterns that persist through temporal renewal. This is an experimental project exploring computational physics on "garden leave" - don't take it too seriously, but feel free to correct assumptions.

**Key Principles:**
- Time is discrete (ticks as `BigInteger`)
- Space expands following dimensional growth rules
- Entities are collision patterns, not static objects
- Everything is deterministic at the substrate layer (no randomness)
- All values are natural numbers (`BigInteger`) - no fractions
- Energy is a function of time (linear, not conserved from initial state)

## Development Commands

### Build and Test
```bash
# Build the entire project
mvn clean package

# Run tests
mvn test

# Run a single test class
mvn test -Dtest=SingleEntityModelTest

# Run a specific test method
mvn test -Dtest=SingleEntityModelTest#testOnTick_WaitWhenEnergyNotDivisible
```

### Run Simulation
```bash
# Run the main substrate simulation (LocalApp)
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.LocalApp"

# Run the 3D server (NOT YET READY - generates dummy data only)
mvn exec:java -pl tick-space-runner -Dexec.mainClass="eu.jerrysamek.tickspace.runner.Simple3DServer"
```

**Important:** LocalApp outputs JSON snapshots to `W:\data\snapshots\` every 1000 ticks. Ensure this directory exists before running.

### Running Python Scripts in Background
When running long-running Python scripts (experiments, simulations) in the background, always use `python -u` (unbuffered stdout) so output can be monitored in real-time. Without `-u`, Python fully buffers stdout when redirected to a file, producing 0 bytes until the process exits.

### Python Analysis Tools
```bash
# Statistical analysis by radial shells
python scripts/snapshot-stats.py W:\data\snapshots\time-frame.5000.json

# 3D visualization
python scripts/snapshot-visualization.py W:\data\snapshots\time-frame.5000.json

# Energy distribution and density profiles
python scripts/snapshot-energy-histogram.py W:\data\snapshots\time-frame.5000.json
```

## Architecture

### Core Component Relationships

The simulation operates through a tick-based event propagation pattern:

```
TickTimeModel (10ms scheduled ticks)
    ↓ onTick(BigInteger tickCount)
SubstrateModel (manages dimensional expansion)
    ↓ propagates to
EntitiesRegistry (spatial hash map: Position → EntityModel)
    ↓ calls onTick() on each entity
EntityModel instances (SingleEntityModel, CollidingEntityModel)
    ↓ return TickAction<EntityModelUpdate>
Updates applied → new positions, collisions detected, entities created/destroyed
```

### Key Design Patterns

**1. Tick Propagation Pattern**
- `TickTimeConsumer<E>` interface defines entities that respond to ticks
- Returns `Stream<TickAction<E>>` where actions are either WAIT or UPDATE
- UPDATE actions execute in parallel via work-stealing pool
- Pattern allows deterministic parallel execution without race conditions

**2. Collision-Based Entity Identity**
- Entities don't have persistent identity through movement
- When two entities occupy the same position → `CollidingEntityModel` created
- Implements "Collision Persistence Principle" (theory doc 30)
- See `EntitiesRegistry.java:59-65` for collision resolution logic

**3. Spatial Indexing**
- `ConcurrentHashMap<Position, EntityModel>` in `EntitiesRegistry`
- Position is an N-dimensional coordinate record with structural equality
- Enables O(1) collision detection during entity updates
- Clean-up of old positions happens atomically during entity movement

### Entity Lifecycle

**Creation:**
- Initial seed at tick=1: single entity at origin `[0,0,0]` (see `EntitiesRegistry.java:24-31`)
- Entities can spawn children during division when energy exceeds threshold
- Collisions create new `CollidingEntityModel` instances

**Movement:**
- Entity calls `onTick()` → energy increases by 1
- If `newEnergy % momentum.cost == 0` → entity can move
- Movement updates position in registry, old position removed
- See `SingleEntityModel.java:73-106` for movement logic

**Collision:**
- Two entities at same position → `CollidingEntityModel.naive()` factory
- Combines energy and momentum from both entities
- Can persist, fragment, or dissolve based on collision dynamics

**Death:**
- Not explicitly modeled yet - entities persist unless absorbed by collision
- Energy cannot go below zero (enforced in `EntitiesRegistry.java:51-53`)

### Module Structure

**tick-space-runner** (Java 25 Maven project)
- `model/ticktime/` - Time engine and tick consumer interface
- `model/substrate/` - Dimensional substrate, position, dimensional size
- `model/entity/` - Entity models, registry, collision logic
- `runner/` - Application runners (LocalApp, Simple3DServer)
- `server/` - WebSocket infrastructure (not yet connected to substrate)

**scripts/** (Python analysis tools)
- Snapshot statistics and visualization scripts
- Operate on JSON output from LocalApp

**docs/theory/** (40+ theoretical documents)
- Mathematical and conceptual foundation
- Key docs: 28 (Temporal Surfing), 29 (Imbalance), 30 (Collision Persistence)

**experiments/** (Python dimensional simulations)
- v6-gpu: 3,960 dimensional sweeps (1D-5D)
- v7: Focused saturation and analysis
- v7-final: Goldilocks zone and LHB validation

## Important Implementation Details

### BigInteger Everywhere
All numeric values use `BigInteger` to avoid floating-point drift and maintain exact determinism. This includes:
- Tick counts
- Positions (N-dimensional coordinates)
- Energy values
- Momentum costs and vectors
- Dimensional sizes

### Parallel Execution Safety
`TickTimeModel.start()` creates a work-stealing pool with `2 × CPU cores` threads. Entity updates are submitted as futures and blocked on completion before next tick. This ensures:
- All tick N updates complete before tick N+1 begins
- Deterministic execution order despite parallelism
- No race conditions in entity state

### Energy Mechanics
`EnergyState.increase()` is called at the start of each entity's `onTick()`. Energy increases linearly with time, but movement and division consume energy implicitly through momentum cost and threshold checks. This is currently under refinement - the model shows "over-coherence" with structures too uniform.

### Collision Detection Edge Cases
When an entity moves to a new position:
1. Registry atomically computes the new position entry
2. If position is empty → insert entity
3. If position occupied by same UUID → update entity (shouldn't happen)
4. If position occupied by different entity → create `CollidingEntityModel`
5. Old position is removed only after new position is secured

See `EntitiesRegistry.java:59-76` for the atomic update logic.

### Testing Approach
Tests use Mockito to mock `SubstrateModel` dependency. Key pattern:
- Mock `getOffsets()` to return test offset vectors (2D/3D space)
- Create `SingleEntityModel` with controlled energy/momentum
- Call `onTick()` and verify returned actions
- Execute action's `update()` method with mock substrate
- Assert on resulting entity states

## Known Issues and Current Work

**Over-Coherence Problem:**
Current entity dynamics produce structures that are too uniform. The substrate needs more chaotic emergence patterns. This is being addressed in Phase 7 development.

**Collision Dynamics Tuning:**
Balance between persistence and dissolution needs refinement. Currently, collision patterns may be too stable or too fragile depending on energy levels.

**Performance Bottleneck:**
Collision detection becomes expensive in dense regions. Typical performance: ~100ms/tick (~10-20ms updates, ~80-90ms execution). Scales tested up to ~10K entities.

**Simple3DServer Status:**
The WebSocket server infrastructure exists but is NOT connected to the actual substrate model. It currently generates dummy brick data. Integration is planned but not started.

## Theoretical Foundation

This implementation validates tick-frame physics theory developed in `docs/theory/`.

**Note:** The current Java implementation is based on the earlier **Chapter 15** model ("Minimal Model Recommendation for Time-Visualization Testing" and the dimensional experiments). The theoretical framework has since evolved to Chapter 49's more refined ontology, but the Java codebase has not yet been updated to reflect these newer concepts.

### Current Theoretical Framework (Chapter 49)

**Temporal Ontology of the Tick-Frame Universe (Doc 49):** A unified framework establishing:
- **Temporal Primacy:** Entities are fundamentally temporal processes, not objects in time
- **Tick-Stream as Absolute Substrate:** The strictly ordered, immutable sequence of universal states
- **Space as Emergent Visualization:** Space emerges from differences between successive ticks
- **Sample Rate Limit:** The speed of light as the maximum rate of change propagation
- **Temporal Integrity Law:** Physical processes must maintain causal readability and identity continuity

This ontology forms the conceptual backbone of the tick-frame universe model and represents the current theoretical understanding.

### Key Historical Concepts (Implemented in Java)

**Temporal Surfing Principle (Doc 28):** Entities persist through continual renewal at each tick, not through static identity.

**Collision Persistence Principle (Doc 30):** Particles are collision patterns, not objects. Identity emerges from interaction, not from state.

**Imbalance Theory (Doc 29):** Matter-antimatter asymmetry emerges from expansion geometry. The model predicts structural imbalance even with symmetric initial conditions.

**Horizon Boundaries (Doc 26):** Observable limits in causal cones. Entities outside the horizon cannot influence each other within finite tick budgets.

**Dimensional Closure Framework (Doc 15-01):** Experimental validation that stable substrates emerge at 4D-5D spatial dimensions under tick-time updates.

**Dimensional Equivalence Rejection (Doc 50, Doc 50_01):** Experimental proof (2026-01-15) that time is NOT a spatial dimension. Testing 1,095 configurations across (2D+t, 3D+t, 4D+t), ALL systems diverge from (3D, 4D, 5D) baseline behavior. **Key finding: ρ=2.0 signature** - all (n+t) systems show quadratic source scaling (ρ=2.0) vs sub-quadratic scaling (ρ≈1.5) in pure spatial dimensions. Combined with Experiment 44 kinematic constraints (rotation asymmetry, v≤1 tick/tick), this constitutes conclusive evidence that **time is a special generator with accumulative/amplifying properties**, fundamentally different from spatial dimensions. Validates Doc 49 (Temporal Ontology): time is primary substrate, space is emergent, and dimensional closure (4D-5D) refers to **spatial dimensions only**.

## Code Style Notes

- Java 25 features: pattern matching, records, virtual threads
- Prefer immutability: `Position`, `Momentum` are records
- Functional streams over imperative loops
- `BigInteger` constants: use `BigInteger.ZERO`, `BigInteger.ONE`, not `valueOf()`
- Indentation: 2 spaces (not tabs)
- Use var instead of type wherever it is possible

## Git Workflow

Currently on branch: `feature/#3-total-energy-balance`

The main branch is not explicitly set in git config. When creating PRs, verify the target branch with the user.

Recent commits show work on energy balance calculations and collision models. Tests are being added for core components (see `SingleEntityModelTest.java`).

## Tools (Maven, Java, Python)
W:\\tools
