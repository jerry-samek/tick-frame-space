package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public class CollidingEntityModel implements EntityModel {

  private final List<EntityModel> entities;
  private final UUID identity;
  private final Position position;

  private static Stream<EntityModel> resolveEntity(EntityModel entity) {
    if (entity instanceof CollidingEntityModel collidingEntityModel) {
      return collidingEntityModel.entities.stream();
    }
    return Stream.of(entity);
  }

  public static EntityModel of(EntityModel entityModel1, EntityModel entityModel2) {
    var completeEntityList = Stream.concat(
            resolveEntity(entityModel1),
            resolveEntity(entityModel2))
        .toList();

    return new CollidingEntityModel(UUID.randomUUID(), entityModel1.getPosition(), completeEntityList);
  }

  private CollidingEntityModel(UUID identity, Position position, List<EntityModel> entityModel) {
    this.identity = identity;
    this.entities = entityModel;
    this.position = position;
  }

  @Override
  public UUID getIdentity() {
    return identity;
  }

  @Override
  public BigInteger getEnergy() {
    return entities
        .stream()
        .map(EntityModel::getEnergy)
        .reduce(BigInteger.ZERO, BigInteger::add);
  }

  @Override
  public Position getPosition() {
    return position;
  }

  @Override
  public BigInteger getGeneration() {
    return entities.stream()
        .map(EntityModel::getGeneration)
        .max(BigInteger::compareTo)
        .orElse(BigInteger.ZERO);
  }

  @Override
  public Momentum getMomentum() {
    return entities.stream()
        .map(EntityModel::getMomentum)
        .reduce(CollidingEntityModel::computeMomentum).orElse(null);
  }

  private static Momentum computeMomentum(Momentum momentum1, Momentum momentum2) {
    var vector1 = momentum1.vector();
    var vector2 = momentum2.vector();

    var mergedVector = new BigInteger[vector1.length];
    var mergedCost = BigInteger.ZERO;

    for (int i = 0; i < mergedVector.length; i++) {
      var cv1 = vector1[i].multiply(momentum1.cost());
      var cv2 = vector2[i].multiply(momentum2.cost());

      mergedVector[i] = cv1.add(cv2);
      mergedCost = mergedCost.add(mergedVector[i].pow(2));
    }

    var newCost = mergedCost.sqrt();

    var annihilation = BigInteger.ZERO.equals(newCost);
    if (annihilation) {
      return new Momentum(BigInteger.ZERO, mergedVector);
    } else {

      for (int i = 0; i < mergedVector.length; i++) {
        mergedVector[i] = mergedVector[i].divide(newCost);
      }

      return new Momentum(newCost, mergedVector);
    }
  }

  @Override
  public Stream<EntityModelUpdate> onTick(BigInteger tickCount) {
    var resolvedMomentum = getMomentum();
    var resolvedEnergy = getEnergy();
    var generation = getGeneration();

    return Stream.of(_ -> {
      if (resolvedMomentum.cost().compareTo(resolvedEnergy) > 0) {
        // merger ... not enough energy for them to continue by themselves
        return Stream.of(
            new SingleEntityModel(UUID.randomUUID(), position, resolvedEnergy, getGeneration().add(ONE), resolvedMomentum));
      }

      // effective annihilation because movement has stopped - it won't be in the next frame
      var childEnergies = Stream.of(OFFSETS)
          .map(bigIntegers -> Utils.computeEnergyCost(resolvedMomentum.vector(), bigIntegers, resolvedMomentum.cost(), generation))
          .toList();

      var energyRequirement = childEnergies.stream().reduce(ZERO, BigInteger::add);

      if (resolvedEnergy.compareTo(energyRequirement) >= 0) {
        // explosion > chain reaction

        var index = new AtomicInteger(0);
        return childEnergies.stream()
            .map(childCost -> {
              var offset = OFFSETS[index.getAndIncrement()];

              return new SingleEntityModel(
                  UUID.randomUUID(),
                  position.offset(offset),
                  resolvedEnergy.subtract(energyRequirement).divide(BigInteger.valueOf(26)), // dimension*3-1 TODO
                  generation.add(ONE),
                  new Momentum(resolvedMomentum.cost().add(childCost.min(BigInteger.TEN)), offset));
            });
      }

      var perChildEnergy = resolvedEnergy.divide(BigInteger.valueOf(entities.size()));
      if (resolvedMomentum.totalCost().compareTo(BigInteger.TEN) < 0) {
        // annihilation - movement stopped and can't reproduce
        return Stream.empty();
      }

      return entities.stream().map(entityModel -> {
        // bounce not enough to explode but enough to leave
        var newMomentum = computeMomentum(entityModel.getMomentum(), resolvedMomentum);

        return new SingleEntityModel(UUID.randomUUID(), position.offset(newMomentum.vector()), perChildEnergy, generation, newMomentum);
      });
    });
  }
}
