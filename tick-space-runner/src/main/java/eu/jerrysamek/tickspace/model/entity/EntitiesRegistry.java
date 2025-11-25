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
import java.util.concurrent.atomic.AtomicBoolean;
import java.util.stream.Stream;

public class EntitiesRegistry implements TickTimeConsumer<SubstrateModelUpdate> {

  private final Map<Position, EntityModel> entities = new ConcurrentHashMap<>();

  @Override
  public Stream<SubstrateModelUpdate> onTick(BigInteger tickCount) {
    if (tickCount.equals(BigInteger.ONE)) { // seed ...
      return Stream.of(model -> {
        var coordinates = new BigInteger[model.getDimensionalSize().getDimensionCount()];
        Arrays.fill(coordinates, BigInteger.ZERO);

        var position = new Position(coordinates);

        entities.put(position, new EntityModel(UUID.randomUUID(), position, BigInteger.ONE, BigInteger.ZERO, new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO})));
      });
    }

    return snapshot()
        .stream()
        .flatMap(entityModel -> {
              var originalRemoved = new AtomicBoolean(false); // check to verify the entity is removed only once

              return entityModel
                  .onTick(tickCount)
                  .map(entityModelUpdate -> substrate -> {
                        var updatedEntity = entityModelUpdate.update(substrate);
                        var newPosition = updatedEntity.getPosition();

                        entities.put(newPosition, updatedEntity);

                        if (!entityModel.getPosition().equals(newPosition)
                            && originalRemoved.compareAndSet(false, true)) {
                          entities.remove(entityModel.getPosition());
                        }
                      }
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
