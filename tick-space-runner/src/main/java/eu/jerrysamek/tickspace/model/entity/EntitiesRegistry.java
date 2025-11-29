package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.ModelBreakingException;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModelUpdate;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.Collection;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;

public class EntitiesRegistry implements TickTimeConsumer<SubstrateModelUpdate> {

  // Single entity map - no double-buffering needed with event-driven scheduling!
  // Only entities in currentTickEntities are modified; waiting entities stay untouched
  private final Map<Position, EntityModel> entities = new ConcurrentHashMap<>();

  // Event-driven scheduling: track which entities need to act on which tick
  private final Map<BigInteger, Set<Position>> tickSchedule = new ConcurrentHashMap<>();

  @Override
  public Stream<TickAction<SubstrateModelUpdate>> onTick(BigInteger tickCount) {
    if (tickCount.equals(BigInteger.ONE)) { // seed ... TODO
      return Stream.of(new TickAction<>(TickActionType.UPDATE, model -> {
        int dimensionCount = model.getDimensionalSize().getDimensionCount();
        var position = new Position(Vector.zero(dimensionCount));
        var momentum = new Momentum(BigInteger.ONE, Vector.zero(dimensionCount));
        var seedEntity = new SingleEntityModel(model, UUID.randomUUID(), BigInteger.ONE, position, BigInteger.ONE, BigInteger.ZERO, momentum);
        entities.put(position, seedEntity);

        // Schedule the seed entity for its first action
        scheduleEntity(seedEntity);
      }));
    }

    // Get and remove entities scheduled for this tick (train has left the station!)
    var currentTickEntities = tickSchedule.remove(tickCount);
    if (currentTickEntities == null) {
      currentTickEntities = Collections.emptySet();
    }

    // No need to copy waiting entities - they stay in place!
    // Only process entities are scheduled to act this tick
    return currentTickEntities.stream()
        .map(entities::get)
        .filter(Objects::nonNull)  // Safety check
        .flatMap(originalEntity -> {
          // Remove entity from the old position (will be replaced or removed)
          entities.remove(originalEntity.getPosition());

          return originalEntity
              .onTick(tickCount)
              .map(tickAction -> new TickAction<>(TickActionType.UPDATE,
                  substrate -> tickAction.action()
                      .update(substrate)
                      .forEach(updatedEntity -> {
                        // Validation
                        if (updatedEntity.getEnergy().value().compareTo(BigInteger.ZERO) < 0) {
                          throw new ModelBreakingException("Energy is too low! " + originalEntity + " => " + updatedEntity);
                        }

                        if (updatedEntity.getMomentum().cost().compareTo(BigInteger.ONE) < 0) {
                          throw new ModelBreakingException("Momentum is too low! " + originalEntity + " => " + updatedEntity);
                        }

                        var newPosition = updatedEntity.getPosition();

                        // Write to entities in-place - collision handling via compute()
                        var nextEntity = entities.compute(newPosition, (_, collidingEntity) -> {
                          if (collidingEntity == null || updatedEntity.getIdentity().equals(collidingEntity.getIdentity())) {
                            // No collision or same entity
                            return updatedEntity;
                          } else {
                            // Collision with a waiting entity - merge
                            return CollidingEntityModel.naive(substrate, updatedEntity, collidingEntity);
                          }
                        });

                        // Schedule for next action
                        scheduleEntity(nextEntity);
                      })
              ));
        });
  }

  private void scheduleEntity(EntityModel entity) {
    if (entity == null) return;
    var nextTick = entity.getNextPossibleAction();
    tickSchedule.computeIfAbsent(nextTick, _ -> ConcurrentHashMap.newKeySet())
        .add(entity.getPosition());
  }

  /**
   * No-op now that we use event-driven scheduling with single buffer.
   * Kept for compatibility with TickTimeModel.
   * Schedule cleanup happens automatically via remove() in onTick().
   */
  public void flip() {
    // Nothing to do! Event-driven scheduling removes entries as processed
  }

  public Collection<EntityModel> snapshot() {
    // Event-driven optimization: only scheduled entities are modified during tick
    // Waiting entities remain untouched, so safe to return values() without copying
    return entities.values();
  }

  public int count() {
    return entities.size();
  }

  public void destroy() {
    entities.clear();
    tickSchedule.clear();
  }

  /**
   * Adds an entity to the registry and schedules it for its next action.
   * Used for snapshot restoration.
   */
  public void addEntity(Position position, EntityModel entity) {
    entities.put(position, entity);
    scheduleEntity(entity);
  }
}
