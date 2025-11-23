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

        entities.put(position, new EntityModel(UUID.randomUUID(), position, BigInteger.ONE, new Momentum(BigInteger.ONE, new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO})));
      });
    }

    return snapshot()
        .stream()
        .flatMap(entityModel -> entityModel
            .onTick(tickCount)
            .map(entityModelUpdate -> substrate -> {
                  var updatedEntity = entityModelUpdate.update(substrate);
                  if (entityModel.getPosition().equals(updatedEntity.getPosition())) {
                    entities.put(updatedEntity.getPosition(), updatedEntity);
                  } else {
                    entities.remove(entityModel.getPosition());

                    entities.put(updatedEntity.getPosition(), updatedEntity);
                  }
                }
            )
        );
  }

  public Collection<EntityModel> snapshot() {
    return new ArrayList<>(entities.values());
  }

  public int count() {
    return entities.size();
  }
}
