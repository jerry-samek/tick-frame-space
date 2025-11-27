package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.ModelBreakingException;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModelUpdate;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Collection;
import java.util.Map;
import java.util.UUID;
import java.util.concurrent.ConcurrentHashMap;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

public class EntitiesRegistry implements TickTimeConsumer<SubstrateModelUpdate> {

  private final Map<Position, EntityModel> entities = new ConcurrentHashMap<>();

  @Override
  public Stream<TickAction<SubstrateModelUpdate>> onTick(BigInteger tickCount) {
    if (tickCount.equals(BigInteger.ONE)) { // seed ... TODO
      return Stream.of(new TickAction<>(TickActionType.UPDATE, model -> {
        var coordinates = new BigInteger[model.getDimensionalSize().getDimensionCount()];
        Arrays.fill(coordinates, BigInteger.ZERO);

        var position = new Position(coordinates);
        entities.put(position, new SingleEntityModel(model, UUID.randomUUID(), position, BigInteger.ONE, BigInteger.ZERO, new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO})));
      }));
    }

    return snapshot()
        .stream()
        .flatMap(originalEntity -> {
              var originalPosition = new AtomicReference<>(originalEntity.getPosition());

              return originalEntity
                  .onTick(tickCount)
                  .filter(entityModelUpdateTickAction -> entityModelUpdateTickAction.type() == TickActionType.UPDATE)
                  .map(TickAction::action)
                  .map(entityModelUpdate ->
                      new TickAction<>(TickActionType.UPDATE,
                          substrate ->
                              entityModelUpdate
                                  .update(substrate)
                                  .forEach(updatedEntity -> {
                                    var newPosition = updatedEntity.getPosition();
                                    if (updatedEntity.getMomentum().cost().compareTo(BigInteger.TEN) < 0) {
                                      throw new ModelBreakingException("Momentum is too low! " + originalEntity + " => " + updatedEntity);
                                    }

                                    entities.compute(newPosition, (_, collidingEntity) -> {
                                      if (collidingEntity == null || updatedEntity.getIdentity().equals(collidingEntity.getIdentity())) {
                                        return updatedEntity;
                                      } else {
                                        return CollidingEntityModel.naive(substrate, updatedEntity, collidingEntity);
                                      }
                                    });

                                    originalPosition.updateAndGet(position -> {
                                      if (position != null && !position.equals(newPosition)) {
                                        entities.remove(position);

                                        return null;
                                      }

                                      return position;
                                    });
                                  })
                      )
                  );
            }
        );
  }

  public Collection<EntityModel> snapshot() {
    return new ArrayList<>(entities.values());
  }

  public int count() {
    return entities.size();
  }

  public void destroy() {
    entities.clear();
  }
}
