package eu.jerrysamek.tickspace.model.entity;

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
  public Stream<SubstrateModelUpdate> onTick(BigInteger tickCount) {
    if (tickCount.equals(BigInteger.ONE)) { // seed ... TODO
      return Stream.of(model -> {
        var coordinates = new BigInteger[model.getDimensionalSize().getDimensionCount()];
        Arrays.fill(coordinates, BigInteger.ZERO);

        var position = new Position(coordinates);
        entities.put(position, new SingleEntityModel(UUID.randomUUID(), position, BigInteger.ONE, BigInteger.ZERO, new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO})));
      });
    }

    return snapshot()
        .stream()
        .flatMap(originalEntity -> {
              var originalPosition = new AtomicReference<>(originalEntity.getPosition());

              return originalEntity
                  .onTick(tickCount)
                  .map(entityModelUpdate -> substrate ->
                      entityModelUpdate
                          .update(substrate)
                          .forEach(updatedEntity -> {
                            var newPosition = updatedEntity.getPosition();

                            entities.compute(newPosition, (_, collidingEntity) -> {
                              if (collidingEntity == null || updatedEntity.equals(collidingEntity)) {
                                return updatedEntity;
                              } else {
                                return CollidingEntityModel.of(updatedEntity, collidingEntity);
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
}
