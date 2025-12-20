package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.ModelBreakingException;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModelUpdate;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.Collection;
import java.util.Collections;
import java.util.Map;
import java.util.Objects;
import java.util.Set;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;

public class EntitiesRegistryLegacy implements EntitiesRegistry {

  // Single entity map - no double-buffering needed with event-driven scheduling!
  // Only entities in currentTickEntities are modified; waiting entities stay untouched
  private final Map<Position, EntityModel> entities = new ConcurrentHashMap<>();

  // Event-driven scheduling: track which entities need to act on which tick
  private final Map<FlexInteger, Set<Position>> tickSchedule = new ConcurrentHashMap<>();

  @Override
  public Stream<TickAction<SubstrateModelUpdate>> onTick(FlexInteger tickCount) {
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
                        if (updatedEntity.getEnergy(tickCount).compareTo(FlexInteger.ZERO) < 0) {
                          throw new ModelBreakingException("Energy is too low! " + originalEntity + " => " + updatedEntity);
                        }

                        if (updatedEntity.getMomentum().cost().compareTo(FlexInteger.ONE) < 0) {
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
                            return CollidingEntityModel.naive(tickCount, substrate, updatedEntity, collidingEntity);
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

  @Override
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
