package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.ModelBreakingException;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModelUpdate;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.*;
import java.util.concurrent.ConcurrentHashMap;
import java.util.stream.Stream;

public class EntitiesRegistry implements TickTimeConsumer<SubstrateModelUpdate> {

  // Double-buffering: read from 'entities', write to 'nextEntities', then swap
  private Map<Position, EntityModel> entities = new ConcurrentHashMap<>();
  private Map<Position, EntityModel> nextEntities;

  @Override
  public Stream<TickAction<SubstrateModelUpdate>> onTick(BigInteger tickCount) {
    if (tickCount.equals(BigInteger.ONE)) { // seed ... TODO
      return Stream.of(new TickAction<>(TickActionType.UPDATE, model -> {
        var coordinates = new BigInteger[model.getDimensionalSize().getDimensionCount()];
        Arrays.fill(coordinates, BigInteger.ZERO);

        var position = new Position(coordinates);
        entities.put(position, new SingleEntityModel(model, UUID.randomUUID(), position, BigInteger.ONE, BigInteger.ZERO, new Momentum(BigInteger.ONE, new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO})));
      }));
    }

    // Pre-allocate the next tick's map - assume 50% max growth per tick to avoid resizing
    int currentSize = entities.size();
    int nextCapacity = Math.max(1024, (int) (currentSize * 1.5));
    nextEntities = new ConcurrentHashMap<>(nextCapacity);

    // Process all entities from the current tick's immutable snapshot
    return entities.values()
        .stream()
        .flatMap(originalEntity ->
              originalEntity
                  .onTick(tickCount)
                  .map(tickAction -> {
                    if (tickAction.type() == TickActionType.WAIT) {
                      // WAIT: entity stays at same position - copy to next map
                      return new TickAction<>(TickActionType.UPDATE,
                          substrate ->
                              nextEntities.put(originalEntity.getPosition(), originalEntity)
                      );
                    } else {
                      // UPDATE: process entity movement/division
                      return new TickAction<>(TickActionType.UPDATE,
                          substrate -> {
                              tickAction.action()
                                  .update(substrate)
                                  .forEach(updatedEntity -> {
                                    // Validation
                                    if (updatedEntity.getEnergy().getEnergy().compareTo(BigInteger.ZERO) < 0) {
                                      throw new ModelBreakingException("Energy is too low! " + originalEntity + " => " + updatedEntity);
                                    }

                                    if (updatedEntity.getMomentum().cost().compareTo(BigInteger.ONE) < 0) {
                                      throw new ModelBreakingException("Momentum is too low! " + originalEntity + " => " + updatedEntity);
                                    }

                                    var newPosition = updatedEntity.getPosition();

                                    // Write to nextEntities - collision handling via compute()
                                    nextEntities.compute(newPosition, (_, collidingEntity) -> {
                                      if (collidingEntity == null || updatedEntity.getIdentity().equals(collidingEntity.getIdentity())) {
                                        return updatedEntity;
                                      } else {
                                        return CollidingEntityModel.naive(substrate, updatedEntity, collidingEntity);
                                      }
                                    });
                                  });
                          }
                      );
                    }
                  })
        );
  }

  /**
   * Flips the entity buffers after all tick actions have completed.
   * MUST be called by TickTimeModel after all futures have completed.
   * Thread-safe: single-threaded execution guaranteed by TickTimeModel.
   */
  public void flip() {
    if (nextEntities != null) {
      entities = nextEntities;  // Atomic pointer swap
      nextEntities = null;       // Allow GC of an old map
    }
  }

  public Collection<EntityModel> snapshot() {
    // Double-buffering optimization: 'entities' is immutable during tick processing
    // All writes go to 'nextEntities', so we can safely return values() without copying
    // This eliminates ~24MB allocation per tick for 3M entities!
    return entities.values();
  }

  public int count() {
    return entities.size();
  }

  public void destroy() {
    entities.clear();
  }
}
