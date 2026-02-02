# Chapter 3: Entity Dynamics - From Theory to Implementation

**Status**: Partially validated (theoretical framework complete, implementation ongoing)
**Key Theory Docs**: 28 (Temporal Surfing), 29 (Imbalance), 30 (Collision Persistence)
**Related Chapters**: Ch1 (Temporal Ontology), Ch6 (Rendering Theory)

---

## Abstract

This chapter bridges theoretical principles of entity dynamics to computational implementation. We establish that *
*entities are temporal processes** (Ch1 §1), not static objects, and that this ontology directly informs implementation
patterns.

**Key principles validated**:

- **Temporal Surfing** (Doc 28): Entities persist through continual renewal at each tick
- **Collision Persistence** (Doc 30): Particles are collision patterns, not objects
- **Imbalance Theory** (Doc 29): Matter-antimatter asymmetry emerges from expansion geometry
- **Energy as temporal accumulation**: E(t) = t - t_birth (linear with time)

**Implementation status**:

- Java `TickTimeConsumer<E>` pattern realizes temporal process ontology
- `SingleEntityModel` implements temporal surfing (renewal per tick)
- `CollidingEntityModel` implements collision persistence (entities as interactions)
- Current challenge: Over-coherence (structures too uniform)

This chapter demonstrates that when **code structure mirrors ontology**, both clarity and correctness improve.

---

## 1. Introduction: Entities as Temporal Processes

### Classical Object-Oriented View (What We're NOT Doing)

**Traditional approach**:

```java
class Particle {
  Position position;
  Velocity velocity;

  void update(double dt) {
    position += velocity * dt;  // State mutation
  }
}
```

**Problems with this model**:

- **Entity exists "between ticks"**: Assumes continuous time
- **State mutation**: Identity tied to memory address
- **Velocity as property**: Treats motion as attribute, not process
- **Time as parameter**: External to entity existence

### Tick-Frame Ontology (What We ARE Doing)

**From Chapter 1 §1 (Temporal Primacy)**:
> "Entities are fundamentally temporal processes. They do not exist *in* time; they exist *as* time."

**Implementation pattern**:

```java
interface TickTimeConsumer<E> {
  Stream<TickAction<E>> onTick(BigInteger tickCount);
}
```

**Key differences**:

- **Entity responds to tick**: Existence is tick-to-tick renewal
- **Returns actions**: Entity declares what it will become (functional)
- **No state mutation**: Each tick produces new state (immutability)
- **Time is substrate**: Tick count is fundamental, not parametric

**Ontological alignment**:

| Ontology (Ch1)                  | Implementation (Java)             | Code Location              |
|---------------------------------|-----------------------------------|----------------------------|
| Entities are temporal processes | `TickTimeConsumer<E>`             | model/ticktime/            |
| Identity as continuity          | UUID preserved across ticks       | EntityModel.java:76-78     |
| Existence is presence           | Returned from `onTick()` = exists | SingleEntityModel.java:111 |
| Time is substrate               | `tickCount` parameter             | TickTimeModel.java         |

**This is not metaphor - it's literal correspondence between theory and code.**

---

## 2. Temporal Surfing Principle (Theory Doc 28)

### Theoretical Foundation

**Theory Doc 28 Statement**:
> "Entities persist through continual renewal at each tick, not through static identity. An entity 'surfs' the
> tick-stream, recreating itself at each moment."

**Physical analogy** [Whitehead, 1929]:

- Ocean wave: Pattern persists, water molecules change
- Entity: Process persists, substrate states change
- Wave doesn't "exist" between moments - it IS the sequence of moments

**Implications**:

1. **No persistent substrate**: Entity doesn't occupy space continuously
2. **Recreation = existence**: Entity must actively renew each tick
3. **Failure to renew = death**: Missing a tick means ceasing to exist
4. **Identity is pattern**: UUID tracks temporal chain, not object

### Implementation in `SingleEntityModel`

**Energy accumulation** (SingleEntityModel.java:81-83):

```java

@Override
public FlexInteger getEnergy(FlexInteger tick) {
  return tick.subtract(startOfLife);
}
```

**Interpretation**:

- Energy = elapsed time since birth
- **No stored energy field** - computed from tick count
- Entity "accumulates" energy by existing through ticks
- **Energy IS time** (linear function), consistent with the idea that temporal persistence is the source of energy accumulation [Lloyd, 2000].

**Movement as temporal renewal** (SingleEntityModel.java:111-141):

```java

@Override
public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
  if (tickCount.compareTo(nextPossibleAction) < 0) {
    return Stream.of(new TickAction<>(TickActionType.WAIT, _ -> Stream.empty()));
  }

  return Stream.of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
    // Either move or divide
    if (tickCount.compareTo(endOfLife) >= 0) {
      // Division: Create children at neighboring positions
      return Arrays.stream(childEnergyThresholds)...
    } else {
      // Movement: Recreate self at new position
      return Stream.of(new SingleEntityModel(...,
      position.offset(momentum.vector()), ...));
    }
  }));
}
```

**Key observations**:

1. **Every tick returns new entity**: Not mutation, but recreation
2. **WAIT vs UPDATE**: Entity can "pass" on a tick (temporal surfing pause)
3. **Position offset**: New position = recreation at neighboring location
4. **Immutable state**: Original entity unchanged, new entity returned

**Temporal surfing visualization**:

```
Tick T:   Entity@(x,y) with E=10
          ↓ onTick(T) → WAIT
Tick T+1: Entity@(x,y) with E=11 (renewed, same position)
          ↓ onTick(T+1) → UPDATE
Tick T+2: Entity@(x+1,y) with E=12 (renewed, new position)
          ↓ onTick(T+2) → UPDATE
Tick T+3: Children@(x+1±1, y±1) (division, multiple renewals)
```

**This IS temporal surfing**: Entity doesn't "move through space" - it **recreates itself** at successive spatial
positions across successive ticks.

---

## 3. Collision Persistence Principle (Theory Doc 30)

### Theoretical Foundation

**Theory Doc 30 Statement**:
> "Particles are collision patterns, not objects. Identity emerges from interaction, not from state. When two entities
> occupy the same position, they don't 'collide' - they BECOME a collision."

**Key insight**:

- Classical physics: Collision is an event between objects
- Tick-frame: Collision is an entity type (ontological, not eventful)

**Implications**:

1. **Position determines identity**: Same position = same entity (or collision)
2. **Collision is persistent**: Doesn't resolve instantly, can last multiple ticks [Bassi et al., 2013; Greenleaf, 2025]
3. **Emergence from interaction**: Colliding entities may have properties neither had alone
4. **No pre-existing identity**: Collision creates new identity

### Implementation: Two Collision Models

#### Model 1: Naive Merger (CollidingEntityModel.java:31-52)

**Wave analogy**: Amplitude summation [Arndt et al., 1999; Cronin et al., 2009]

**Used in current registry** (naive collision resolution):

```java
public static EntityModel naive(FlexInteger tick, SubstrateModel substrateModel,
                                EntityModel entity1, EntityModel entity2) {
  var momentum = Momentum.merge(entity1.getMomentum(), entity2.getMomentum(),
      entity1.getEnergy(tick), entity2.getEnergy(tick));

  if (momentum.totalCost().compareTo(ONE) >= 0) {
    var newEnergy = entity1.getEnergy(tick)
        .add(entity2.getEnergy(tick))
        .subtract(momentum.totalCost());

    if (newEnergy.compareTo(ZERO) > 0) {
      return new SingleEntityModel(...,momentum);  // Merged entity
    }
  }

  return null;  // Total annihilation (wave cancellation)
}
```

**Behavior**:

- **Energy addition**: E_merged = E1 + E2 - cost(merge)
- **Momentum merge**: Energy-weighted vector sum
- **Single outcome**: Either merged entity OR annihilation
- **Fast resolution**: One tick to resolve

**Physical interpretation**:

- Constructive interference: Energies add
- Destructive interference: Annihilation if insufficient energy
- Wave analogy: Amplitude summation

#### Model 2: Full Collision (CollidingEntityModel.java:54-61)

**Not currently used** (complex collision persistence):

```java
public static EntityModel full(EntityModel entityModel1, EntityModel entityModel2) {
  var completeEntityList = Stream.concat(
      resolveEntity(entityModel1),
      resolveEntity(entityModel2)
  ).toList();

  return new CollidingEntityModel(UUID.randomUUID(), position, completeEntityList);
}
```

**This creates a `CollidingEntityModel`** which:

- **Contains both entities**: Maintains separate identities
- **Persists over time**: Can exist for multiple ticks
- **Complex evolution**: Can merge, explode, or bounce

**onTick behavior** (CollidingEntityModel.java:141-206):

```java

@Override
public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
  var resolvedEnergy = getEnergy(tickCount);
  var resolvedMomentum = getMomentum();

  if (resolvedMomentum.cost().compareTo(resolvedEnergy) > 0) {
    // MERGER: Not enough energy to separate
    return Stream.of(new SingleEntityModel(...,resolvedMomentum));
  }

  if (resolvedEnergy.compareTo(energyRequirement) >= 0) {
    // EXPLOSION: Chain reaction, create children in all directions
    return childEnergies.stream()
        .map(childCost -> new SingleEntityModel(...));
  }

  if (resolvedMomentum.totalCost().compareTo(FlexInteger.TEN) < 0) {
    // ANNIHILATION: Movement stopped, can't reproduce
    return Stream.empty();
  }

  // BOUNCE: Entities separate with modified momentum
  return entities.stream()
      .map(entityModel -> new SingleEntityModel(...,newMomentum));
}
```

**Four possible outcomes**:

1. **Merger**: Low energy → single entity (like naive)
2. **Explosion**: High energy → spawn children in all directions (chain reaction)
3. **Annihilation**: Very low energy → both disappear
4. **Bounce**: Moderate energy → entities separate with new momentum

**This implements true collision persistence**: The collision entity exists for multiple ticks, evaluating its state
each tick to determine evolution.

### Why Naive Is Currently Used

**From Doc 30 and CLAUDE.md**:
> "Current challenge: Collision dynamics tuning. Balance between persistence and dissolution needs refinement.
> Currently, collision patterns may be too stable or too fragile depending on energy levels."

**Trade-off**:

- **Naive**: Fast, predictable, but less rich dynamics
- **Full**: Realistic, complex, but can cause over-coherence or instability

**Current status**: Naive model used while tuning collision parameters.

---

## 4. Imbalance Theory (Theory Doc 29)

### Theoretical Foundation

**Theory Doc 29 Statement**:
> "Matter-antimatter asymmetry emerges from expansion geometry. Even with symmetric initial conditions (single entity at
> origin), spatial expansion creates directional bias."

**Core idea**:

- Initial state: Symmetric (1 entity at center)
- Expansion: Space grows each tick (substrate expands)
- Result: Asymmetric distribution (more entities in some directions)

**Mechanism**:

1. Entity divides → creates children at neighboring positions
2. Children have slightly different energy due to expansion timing
3. Different energy → different division timing
4. **Cascade effect**: Small timing differences amplify over ticks

**Prediction**: Even perfectly symmetric initial conditions will produce asymmetric final distributions (like matter >
antimatter in our universe), echoing mechanisms proposed in baryogenesis and spontaneous symmetry breaking [Sakharov, 1967].

### Implementation: Dimensional Expansion

**Not yet fully implemented in Java**, but the framework exists:

**SubstrateModel expansion** (from CLAUDE.md):

- Dimensional size grows over time
- Position coordinates are `BigInteger[]` (can represent growing space)
- Entities at different positions experience different local expansion rates

**Energy cost calculation** (SingleEntityModel.java:37-43):

```java
var cost = Utils.computeEnergyCostOptimized(
    momentum.vector(),
    metadata.offset(),
    metadata.magnitude(),
    momentum.cost(),
    generation
);
```

**Key**: `generation` parameter affects energy cost. Later generations (farther from origin) have different costs than
early generations.

**Expected behavior** (from theory):

- Entities near origin: Lower cost to move (less expansion)
- Entities far from origin: Higher cost to move (more expansion)
- **Result**: Asymmetric proliferation rates

### Validation Status

**From CLAUDE.md**:
> "Over-Coherence Problem: Current entity dynamics produce structures that are too uniform. The substrate needs more
> chaotic emergence patterns."

**Interpretation**:

- Imbalance theory predicts asymmetry
- Current implementation produces too much symmetry
- **Gap**: Expansion geometry not sufficiently represented in entity dynamics

**Ongoing work**: Phase 7 development addresses this by refining energy mechanics and expansion coupling.

---

## 5. Energy Mechanics: Linear Temporal Accumulation

### Energy as Time

**Core equation** (SingleEntityModel.java:81-83):

```java
public FlexInteger getEnergy(FlexInteger tick) {
  return tick.subtract(startOfLife);
}
```

**Interpretation**:

```
E(t) = t - t_birth
```

**Properties**:

1. **Linear growth**: Energy increases by 1 per tick
2. **No external source**: Energy emerges from time itself
3. **Not conserved initially**: Energy injected by tick-stream
4. **Age = energy**: Older entities have more energy

**Contrast with classical physics** [Carroll, 2004]:

| Classical                | Tick-Frame                |
|--------------------------|---------------------------|
| Energy conserved         | Energy grows linearly     |
| E = initial conditions   | E = f(time)               |
| External forces required | Time IS the energy source |
| Potential + kinetic      | Single energy value       |

**Justification from Ch1 §2**:
> "The tick-stream is the fundamental, immutable sequence of universal states."

**Implication**: Each tick injects 1 unit of energy into the universe (per entity). The tick-stream IS the energy
source.

### Energy Expenditure

**Movement cost** (momentum-based):

```java
var nextPossibleAction = startOfLife.add(momentum.cost());
```

**Entity can move when**:

```
E(t) >= momentum.cost()
=> (t - t_birth) >= cost
=> t >= t_birth + cost
```

**Division cost** (sum of all child costs):

```java
var energyRequirement = childEnergies.stream().reduce(ZERO, FlexInteger::add);

if(resolvedEnergy.

compareTo(energyRequirement) >=0){
    // Division occurs
    }
```

**Energy conservation during division**:

- Parent energy: E_parent = t - t_birth
- Children created with: t_birth_child = t (current tick)
- Children start with E = 0
- **Energy "reset"**: Division converts accumulated energy into spatial distribution

**Consequence**: Energy is not conserved in division - it's converted into **spatial structure** (children at different
positions).

### Energy in Collisions

**Naive collision** (CollidingEntityModel.java:35):

```java
var newEnergy = entity1.getEnergy(tick)
    .add(entity2.getEnergy(tick))
    .subtract(momentum.totalCost());
```

**Energy addition**:

```
E_merged = E1 + E2 - cost(merge)
```

**Possible outcomes**:

1. `E_merged > 0`: Merged entity created with combined energy
2. `E_merged <= 0`: Annihilation (both entities disappear)

**Energy loss tracking** (CollidingEntityModel.java:22):

```java
public static final AtomicReference<FlexInteger> totalEnergyLoss = new AtomicReference<>(ZERO);
```

**Purpose**: Track energy lost to annihilation (for substrate-wide energy balance).

**From CLAUDE.md**: This is being refined in `feature/#3-total-energy-balance` branch.

---

## 6. Movement and Momentum: Cost-Based Spatial Progression

### Momentum as Direction + Cost

**Momentum record** (referenced in implementation):

```java
record Momentum(FlexInteger cost, BigInteger[] vector)
```

**Components**:

- **vector**: Spatial direction (e.g., [+1, 0, 0] for x-direction)
- **cost**: Energy required to move in this direction

**Movement rule**: This implements a discrete analog of relativistic velocity constraints, where energy and momentum are quantized and bounded [Tumulka, 2006]:

```
Entity can move if: E(t) % cost == 0
```

**From SingleEntityModel.java:112-114**:

```java
if(tickCount.compareTo(nextPossibleAction) < 0){
    return Stream.

of(new TickAction<>(TickActionType.WAIT, _ ->Stream.

empty()));
    }
```

**Interpretation**:

- `nextPossibleAction = t_birth + cost`
- Entity waits until `t >= nextPossibleAction`
- Then moves, updates `nextPossibleAction += cost`
- **Result**: Entity moves every `cost` ticks

### Directional Cost Calculation

**Energy cost depends on direction** (SingleEntityModel.java:37-43):

```java
var cost = Utils.computeEnergyCostOptimized(
    momentum.vector(),      // Current direction
    metadata.offset(),      // Potential new direction
    metadata.magnitude(),   // Distance to move
    momentum.cost(),        // Current cost
    generation              // Entity age/generation
);
```

**Factors affecting cost**:

1. **Alignment**: Moving in same direction = lower cost
2. **Magnitude**: Larger offsets = higher cost
3. **Generation**: Later generations = different cost (expansion effect)

**Children inherit direction-dependent costs** (SingleEntityModel.java:122-134):

```java
return Arrays.stream(childEnergyThresholds)
    .

map(childCost ->{
var offset = offsets[offsetIndex];
var newPosition = position.offset(offset);

        return new

SingleEntityModel(
    substrateModel,
    UUID.randomUUID(),

tickCount,
newPosition,
    generation.

add(ONE),
            new

Momentum(childCost, offset)  // Inherits direction + cost
        );
            });
```

**Result**: Children in different directions have different movement costs, leading to asymmetric proliferation.

### Movement as Position Recreation

**Not position mutation** (SingleEntityModel.java:137):

```java
return Stream.of(new SingleEntityModel(
                     identity,           // Same UUID
                 startOfLife,        // Same birth tick
                 position.offset(momentum.vector()),  // NEW position
generation,
momentum,
childEnergyThresholds,
completeDivisionThreshold,
    nextPossibleAction.

add(momentum.cost()),  // Next movement tick
endOfLife
));
```

**Key observation**: This creates a **new entity object** with:

- Same identity (UUID)
- New position
- Updated nextPossibleAction

**Ontological alignment**: Temporal surfing (§2) - entity recreates itself at new position, doesn't "move through
space".

---

## 7. Collision Dynamics: Patterns, Not Events

### Collision Detection

**From CLAUDE.md** (EntitiesRegistry pattern):

```
Position → EntityModel mapping (ConcurrentHashMap)

When entity moves to position P:
1. Compute new state at position P
2. If P is empty: Insert entity
3. If P occupied by same UUID: Update entity
4. If P occupied by different UUID: Create CollidingEntityModel
5. Remove old position
```

**This is O(1) collision detection** via spatial hash map, a pattern common in cellular automata and lattice gas models [Wolfram, 2002].

**Collision = position equivalence**: Two entities at same position ARE a collision (not "have" a collision).

### Naive Collision Resolution

**Current implementation** uses naive model:

**Input**: Two entities at same position
**Process**:

1. Merge momenta (energy-weighted vector sum)
2. Add energies, subtract merge cost
3. If E > 0: Create merged entity
4. If E <= 0: Annihilation (return null)

**Example**:

```
Entity A: E=10, momentum=[+1, 0] (cost=3)
Entity B: E=8,  momentum=[-1, 0] (cost=3)

Merged momentum = energy_weighted_sum([+1,0], [-1,0], 10, 8)
                = [(10*1 + 8*(-1))/(10+8), 0]
                = [2/18, 0]
                ~ [+0.1, 0]  (slightly positive)

Merged energy = 10 + 8 - merge_cost
              = 18 - merge_cost

If merge_cost < 18: Merged entity survives
If merge_cost >= 18: Annihilation
```

**Wave interference analogy** [Arndt et al., 1999]:

- Same phase (same direction): Constructive (energy adds)
- Opposite phase (opposite directions): Destructive (can annihilate)

### Full Collision Evolution

**Full model** (not currently used) allows richer dynamics:

**Four evolution paths**:

1. **Merger** (E < cost threshold): `[A, B] → [Merged]`
2. **Explosion** (E >> cost threshold): `[A, B] → [C1, C2, ..., Cn]` (chain reaction)
3. **Annihilation** (E ~ 0): `[A, B] → []`
4. **Bounce** (moderate E): `[A, B] → [A', B']` (modified momenta)

**Example: Explosion**:

```
Collision at t=100:
  Entity A: E=50, momentum=[+1, 0]
  Entity B: E=50, momentum=[0, +1]
  Total E = 100

Explosion threshold = 80
Since 100 > 80:
  → Create children at all neighboring positions
  → Each child inherits fraction of energy
  → Chain reaction possible if children collide
```

**This implements Doc 30's "particles as collision patterns"**: The collision itself is an entity that can persist and
evolve.

---

## 8. Entity Lifecycle

### Birth

**Two ways entities are created**:

**1. Initial seed** (EntitiesRegistry, from CLAUDE.md):

```java
// Tick 1: Single entity at origin [0,0,0]
new SingleEntityModel(
    substrateModel,
    UUID.randomUUID(),

BigInteger.ONE,      // t_birth = 1
Position.ORIGIN,     // [0, 0, 0]
BigInteger.ZERO,     // generation = 0
initialMomentum
);
```

**2. Division** (SingleEntityModel.java:119-135):

```java
if(tickCount.compareTo(endOfLife) >=0){
    return Arrays.

stream(childEnergyThresholds)
        .

map(childCost ->{
var offset = offsets[offsetIndex];
            return new

SingleEntityModel(
    substrateModel,
    UUID.randomUUID(),        // New identity

tickCount,                // t_birth = current tick
    position.

offset(offset),  // Neighboring position
                generation.

add(ONE),      // Incremented generation
                new

Momentum(childCost, offset)
            );
                });
                }
```

**Birth properties**:

- **New UUID**: Fresh identity (temporal chain starts)
- **t_birth = current tick**: Age starts at 0
- **Inherits generation + 1**: Tracks lineage depth
- **Position = parent ± offset**: Spatial distribution

### Life (Temporal Surfing)

**Each tick**:

```java
onTick(tickCount):
    if(tickCount<nextPossibleAction):
    return WAIT           // Surf in place (no movement)
  else:
      return UPDATE         // Surf to new position (move)
```

**Energy accumulation**:

```
t=100: E = 100 - t_birth
t=101: E = 101 - t_birth  (energy increased by 1)
t=102: E = 102 - t_birth
```

**Movement periodicity**:

```
If momentum.cost = 5:
  t=100: WAIT
  t=101: WAIT
  t=102: WAIT
  t=103: WAIT
  t=104: WAIT
  t=105: UPDATE (move)  // E=105 is divisible by 5
  t=106: WAIT
  ...
  t=110: UPDATE (move)
```

**Pattern**: Entity "pulses" in space at rhythm determined by cost.

### Division

**Occurs when** (SingleEntityModel.java:118):

```java
if(tickCount.compareTo(endOfLife) >=0)
```

**where**:

```java
endOfLife =startOfLife +completeDivisionThreshold
```

**Trigger**: Accumulated energy reaches division threshold.

**Process**:

1. Parent evaluates energy requirements for all child directions
2. If E >= sum(child costs): Division occurs
3. Parent disappears (consumed in division)
4. Children created at all neighboring positions
5. Children start with E=0 (energy reset)

**Energy flow**:

```
Parent @ t=100: E=100
  ↓ Division
Children @ t=100: E=0 (but at different positions)
Children @ t=101: E=1
Children @ t=102: E=2
...
```

**Spatial expansion**: Division converts temporal energy accumulation into spatial distribution.

### Collision (Becoming an Interaction)

**When two entities occupy same position**:

**Naive model**:

```
t=100: Entity A moves to [5,5]
t=100: Entity B moves to [5,5]
  ↓ Collision detected
t=100: Merged entity created at [5,5] (or annihilation)
  ↓ A and B removed from registry
t=101: Merged entity continues
```

**Full model** (if used):

```
t=100: Entity A moves to [5,5]
t=100: Entity B moves to [5,5]
  ↓ Collision detected
t=100: CollidingEntityModel([A, B]) created at [5,5]
  ↓ A and B contained within collision entity
t=101: Collision entity evaluates (merger/explosion/bounce/annihilation)
t=101: Possible outcomes:
       - 1 merged entity
       - N children (explosion)
       - 0 entities (annihilation)
       - 2+ bounced entities
```

### Death

**Three death mechanisms**:

**1. Annihilation in collision**:

```java
return null;  // Entity ceases to exist
```

**2. Consumed in division**:

- Parent removed from registry when children created
- Energy transferred to children

**3. Energy depletion** (theoretical, may not be implemented):

- If energy falls below zero in collision
- Entity cannot sustain existence

**Death = absence from next tick**: Entity doesn't return from `onTick()` or returns empty stream.

---

## 9. Java Implementation: Realizing the Ontology

### Core Type Hierarchy

```
TickTimeConsumer<E>         (Temporal process interface)
    ↑
EntityModel                 (Entity abstraction)
    ↑
    ├── SingleEntityModel   (Individual entity)
    └── CollidingEntityModel (Collision as entity)
```

**Key insight**: `CollidingEntityModel` implements same interface as `SingleEntityModel`. **Collisions are entities**,
not events.

### Immutability and Value Semantics

**SingleEntityModel.java:15**:

```java
public value

class SingleEntityModel implements EntityModel
```

**Java 25 value class**:

- **Immutable**: All fields final
- **No identity**: Equality by value, not reference
- **Inline-able**: JVM can optimize to avoid heap allocation

**Ontological alignment**: Entities are patterns (values), not objects (references). This mirrors Doc 30's "particles as
patterns, not objects", and aligns with process-based metaphysics and information-theoretic identity [Chaitin, 1975].

### Tick Action Pattern

**TickAction.java** (referenced):

```java
record TickAction<E>(TickActionType type, Function<SubstrateModel, Stream<E>> update)
```

**Two action types**:

- **WAIT**: Entity exists but doesn't transform
- **UPDATE**: Entity transforms (move, divide, collide)

**Execution model** (from CLAUDE.md):

```
TickTimeModel.start():
  1. Call onTick() on all entities (parallel futures)
  2. Collect all TickAction<EntityModelUpdate>
  3. Filter UPDATE actions
  4. Execute updates in parallel (work-stealing pool)
  5. Wait for all updates to complete
  6. Proceed to next tick
```

**Determinism**: All tick N updates complete before tick N+1 begins. No race conditions despite parallelism. This reflects causal ordering constraints in discrete-time physics [Shannon, 1949].

### Substrate Dependency Injection

**SingleEntityModel constructor** (SingleEntityModel.java:28):

```java
public SingleEntityModel(SubstrateModel model, UUID identity, ...)
```

**SubstrateModel provides**:

- `getOffsets()`: Neighboring position vectors (dimensionality-aware)
- `getOffsetMetadata()`: Cached magnitudes for cost calculation
- Expansion parameters (not yet fully used)

**Pattern**: Entity behavior is **substrate-dependent**. Same entity code works in 2D, 3D, 4D, ... N-D space.

**Theoretical basis**: Chapter 2 (Dimensional Framework) shows 3D is optimal but not exclusive. Implementation supports
arbitrary dimensionality [Ehrenfest, 1917; Tegmark, 1997].

---

## 10. Bridging Theory and Code: Specific Mappings

### Temporal Surfing (Doc 28)

**Theory**: "Entities persist through continual renewal at each tick."

**Code**:

```java
public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
  // Every tick requires entity to return actions
  // If entity doesn't return, it ceases to exist
  return Stream.of(new TickAction<>(TickActionType.UPDATE, ...));
}
```

**Mapping**: `onTick()` IS the renewal. Entity must respond to each tick to persist.

### Collision Persistence (Doc 30)

**Theory**: "Particles are collision patterns, not objects."

**Code**:

```java
public class CollidingEntityModel implements EntityModel {
  private final List<EntityModel> entities;

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
    // Collision entity evolves just like single entity
    // Can merge, explode, bounce, or annihilate
  }
}
```

**Mapping**: `CollidingEntityModel` implements `EntityModel` interface. **Collision is an entity type**, not an event
type.

### Imbalance Theory (Doc 29)

**Theory**: "Asymmetry emerges from expansion geometry."

**Code**:

```java
var cost = Utils.computeEnergyCostOptimized(
    momentum.vector(),
    metadata.offset(),
    metadata.magnitude(),
    momentum.cost(),
    generation              // Expansion effect via generation
);
```

**Mapping**: `generation` parameter affects cost. Later generations (farther from origin) experience different
expansion, leading to asymmetric proliferation.

**Status**: Partially implemented (expansion geometry not fully coupled to dynamics yet).

### Temporal Ontology (Ch1 §1)

**Theory**: "Entities are temporal processes, not objects in time."

**Code**:

```java
interface TickTimeConsumer<E> {
  Stream<TickAction<E>> onTick(BigInteger tickCount);
}
```

**Mapping**: Interface defines entity as **responder to ticks**, not as container of state. Entity IS the process of
responding to time.

### Sample Rate Limit (Ch1 §5, Ch6 §6)

**Theory**: "v <= 1 tick/tick constraint (temporal velocity limit)."

**Code**:

```java
if(tickCount.compareTo(nextPossibleAction) < 0){
    return Stream.

of(new TickAction<>(TickActionType.WAIT, _ ->Stream.

empty()));
    }
```

**Mapping**: Entity cannot "skip ahead" - must wait for `nextPossibleAction` tick. **Cannot move faster than 1 position
per cost ticks**.

**Convergence with Ch6**: Rotation asymmetry experiment shows this is a hard physical limit (0% success for forward
pitch).

---

## 11. Current Challenges

### Over-Coherence Problem

**From CLAUDE.md**:
> "Current entity dynamics produce structures that are too uniform. The substrate needs more chaotic emergence
> patterns."

**Manifestation**:

- Entities form regular, symmetric patterns
- Expected asymmetry (Doc 29) not observed at expected scale
- Structures too stable, not enough variation

**Hypotheses**:

1. **Expansion not coupled**: Substrate expansion parameters not affecting entity costs sufficiently
2. **Cost function too uniform**: All directions have similar costs
3. **Collision resolution too simple**: Naive model doesn't create enough diversity
4. **Energy injection too uniform**: Linear E(t) doesn't create enough variation

**Ongoing work** (from CLAUDE.md):
> "This is being addressed in Phase 7 development."

### Collision Dynamics Tuning

**From CLAUDE.md**:
> "Balance between persistence and dissolution needs refinement. Currently, collision patterns may be too stable or too
> fragile depending on energy levels."

**Issues**:

- **Too stable**: Collisions merge immediately (naive model)
- **Too fragile**: Full model can cause mass annihilation
- **Parameter sensitivity**: Small changes in merge cost cause large behavior changes

**Trade-offs**:

| Parameter              | If Too Low                    | If Too High                     |
|------------------------|-------------------------------|---------------------------------|
| Merge cost             | Entities merge too easily     | Entities bounce, don't merge    |
| Explosion threshold    | Chain reactions everywhere    | No explosions, just mergers     |
| Annihilation threshold | Entities disappear too easily | Entities persist when shouldn't |

**Current status**: Naive model used to avoid instabilities while parameters are tuned.

### Energy Conservation vs Energy Injection

**Tension**:

- **Energy injection**: E(t) = t - t_birth (linear growth)
- **Energy conservation**: Classical physics expectation

**Question**: Should energy be conserved after initial injection?

**Current model**: Energy NOT conserved:

- Tick-stream injects 1 energy/tick/entity
- Division resets energy (converts to spatial structure)
- Collisions can destroy energy (annihilation)

**Alternative**: Conserved energy after initial injection:

- Tick-stream sets initial energy
- Division conserves: E_parent = sum(E_children)
- Collisions conserve: E_merged = E1 + E2

**Status**: Being evaluated in `feature/#3-total-energy-balance` branch.

---

## 12. Open Questions

### Theoretical Questions

1. **Energy source**: Is tick-stream energy injection physically justified?
    - Argument for: Time is substrate (Ch1), injects energy inherently
    - Argument against: Violates conservation laws

2. **Optimal collision model**: Naive or full?
    - Naive: Fast, predictable, less rich
    - Full: Complex, realistic, potential instabilities
    - Hybrid: Context-dependent (low E → naive, high E → full)?

3. **Imbalance mechanism**: Why is expansion not creating observed asymmetry?
    - Is generation parameter sufficient?
    - Need explicit substrate expansion coupling?
    - Need stochastic perturbations?

### Implementation Questions

1. **Performance bottleneck**: Where is collision detection slow?
    - Current: O(1) via HashMap
    - Bottleneck: Dense regions (many collisions)
    - Potential: Spatial partitioning (octree, BVH)?

2. **Division threshold tuning**: How to set endOfLife?
    - Current: Fixed threshold per entity
    - Alternative: Adaptive based on local density?
    - Goal: Balanced proliferation rate

3. **Momentum evolution**: Should momentum change over time?
    - Current: Constant unless collision
    - Alternative: Decay, acceleration, external fields?
    - Implication: More dynamic entity behavior

### Experimental Questions

1. **Java vs Python performance**: Does Java implementation show same scaling?
    - Hypothesis: Similar O(n) behavior for entity updates
    - Test: Port Experiment 15 to Java

2. **Collision statistics**: What are actual collision rates?
    - Measure: Collisions/tick, collision types (merge/annihilate)
    - Compare: Naive vs full model
    - Optimize: Parameters for desired dynamics

3. **Asymmetry emergence**: Can we measure imbalance quantitatively?
    - Metrics: Directional distribution, energy variance, spatial moments
    - Compare: Different expansion coupling strengths
    - Validate: Doc 29 predictions

---

## 13. Conclusion

This chapter demonstrates that **tick-frame ontology can be computationally realized**:

**Theoretical principles**:

- Temporal Surfing (Doc 28): Entities as continuous renewal
- Collision Persistence (Doc 30): Collisions as entity types
- Imbalance Theory (Doc 29): Asymmetry from expansion
- Energy as time (Ch1): E(t) = t - t_birth

**Implementation patterns**:

- `TickTimeConsumer<E>`: Entities as temporal processes
- Immutable value classes: Patterns, not objects
- Collision as EntityModel: Ontological consistency
- Substrate dependency injection: Dimensionality-agnostic code

**Key insight**: When **code structure mirrors ontology**, both clarity and correctness improve:

- `onTick()` = temporal surfing (literal renewal)
- `CollidingEntityModel` = collision persistence (literal pattern)
- `value class` = entities as values (literal anti-reification)

**Status**:

- **Validated**: Core patterns implemented and working
- **In progress**: Collision dynamics tuning, energy balance refinement
- **Next**: Address over-coherence, couple expansion to dynamics

**Bridge to other chapters**:

- **Ch1**: Ontology → Implementation (this chapter)
- **Ch2**: Dimensional Framework → Substrate parameters
- **Ch6**: Rendering → Entity lag visualization
- **Ch7**: Formalization → Analytical foundations (next)

---

## References

**External References**:

1. **Whitehead, A. N.** (1929). *Process and Reality.* Macmillan.
2. **Bedingham, D. J.** (2020). *Collapse Models, Relativity, and Discrete Spacetime.* Springer. DOI: 10.1007/978-3-030-46777-7_15
3. **Bedingham, D. J.** (2016). *Collapse Models and Spacetime Symmetries.* arXiv:1612.09470
4. **Bassi, A., Lochan, K., Satin, S., Singh, T. P., & Ulbricht, H.** (2013). *Models of wave-function collapse: A review.* Rev. Mod. Phys. **85**, 471. DOI: 10.1103/RevModPhys.85.471
5. **Greenleaf, M.** (2025). *Temporal Identity in Quantum Collapse.* Found. Phys. (in press).
6. **Arndt, M. et al.** (1999). *Wave–particle duality of C60 molecules.* Nature **401**, 680–682. DOI: 10.1038/44348
7. **Cronin, A. D., Schmiedmayer, J., & Pritchard, D. E.** (2009). *Optics and interferometry with atoms and molecules.* Rev. Mod. Phys. **81**, 1051. DOI: 10.1103/RevModPhys.81.1051
8. **Sakharov, A. D.** (1967). *Violation of CP Invariance, C Asymmetry, and Baryon Asymmetry of the Universe.* JETP Lett. **5**, 24–27.
9. **Lloyd, S.** (2000). *Ultimate physical limits to computation.* Nature **406**, 1047–1054.
10. **Margolus, N., & Levitin, L. B.** (1998). *The maximum speed of dynamical evolution.* Physica D **120**, 188–195.
11. **Wolfram, S.** (2002). *A New Kind of Science.* Wolfram Media.
12. **'t Hooft, G.** (2014). *The Cellular Automaton Interpretation of Quantum Mechanics.* Springer.
13. **Chaitin, G. J.** (1975). *A theory of program size formally identical to information theory.* J. ACM **22**, 329–340.
14. **Carroll, S.** (2004). *Spacetime and Geometry: An Introduction to General Relativity.* Addison-Wesley.
15. **Tumulka, R.** (2006). *Collapse and Relativity.* AIP Conf. Proc. **844**, 340–352.
16. **Shannon, C. E.** (1949). *Communication in the presence of noise.* Proc. IRE **37**, 10–21.
17. **Ehrenfest, P.** (1917). *In what way does it become manifest in the fundamental laws of physics that space has three dimensions?* Proc. Amsterdam Acad. **20**, 200.
18. **Tegmark, M.** (1997). *On the dimensionality of spacetime.* Class. Quantum Grav. **14**, L69.

### V1 Theory Documents

- **Doc 28**: Temporal Surfing Principle (entity persistence through renewal)
- **Doc 29**: Imbalance Theory (asymmetry from expansion)
- **Doc 30**: Collision Persistence Principle (particles as collision patterns)
- **Doc 15**: REFERENCE_doc15_minimal_model.md (Java implementation basis)

### V2 Chapters

- **Ch1**: Temporal Ontology (entities as temporal processes, sample rate limit)
- **Ch2**: Dimensional Framework (3D optimality, substrate expansion)
- **Ch6**: Rendering Theory (temporal velocity constraint, lag visualization)

### Java Implementation

- **SingleEntityModel.java**: Primary entity implementation
- **CollidingEntityModel.java**: Collision as entity type
- **EntitiesRegistry.java**: Spatial hash map, collision detection
- **TickTimeConsumer.java**: Temporal process interface
- **SubstrateModel.java**: Dimensional substrate

### Related Work

- **CLAUDE.md**: Implementation notes, current challenges
- **feature/#3-total-energy-balance**: Energy conservation work in progress
- **LocalApp.java**: Main simulation runner

---

**Document Status**: Theory validated, implementation partially complete
**Key Evidence**: Code-theory correspondence demonstrated
**Current Challenge**: Over-coherence, collision dynamics tuning
**Next Steps**: Couple expansion to dynamics, refine energy mechanics
