package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public class CollidingEntityModel implements EntityModel {

  private final List<EntityModel> entities;
  private final UUID identity;
  private final Position position;

  public static final AtomicReference<BigInteger> totalEnergyLoss = new AtomicReference<>(ZERO);

  /**
   * It resolves collision by ignoring the colliding entity. The proper model is the full. However, it is not working properly yet.
   *
   * @param entity1 EntityModel
   * @param entity2 EntityModel
   * @return only the entity1
   */
  public static EntityModel naive(SubstrateModel substrateModel, EntityModel entity1, EntityModel entity2) {
    var momentum = Momentum.merge(entity1.getMomentum(), entity2.getMomentum(), entity1.getEnergy().value(), entity2.getEnergy().value());
    if (momentum.totalCost().compareTo(ONE) >= 0) {
      // it naively solves merge and bounce by one single entity model
      var newEnergy = entity1.getEnergy().merge(entity2.getEnergy()).value().subtract(momentum.totalCost());
      if (newEnergy.compareTo(ZERO) > 0) {
        return new SingleEntityModel(
            substrateModel,
            UUID.randomUUID(),
            entity1.tickOfBirth().min(entity2.tickOfBirth()),
            entity1.getPosition(),
            newEnergy,
            entity1.getGeneration().max(entity2.getGeneration()).add(ONE),
            momentum
        );
      }
    }


    // total annihilation - or at least this is more like wave cancellation
    return null;

  }

  public static EntityModel full(EntityModel entityModel1, EntityModel entityModel2) {
    var completeEntityList = Stream.concat(
            resolveEntity(entityModel1),
            resolveEntity(entityModel2))
        .toList();

    return new CollidingEntityModel(UUID.randomUUID(), entityModel1.getPosition(), completeEntityList);
  }

  private static Stream<EntityModel> resolveEntity(EntityModel entity) {
    if (entity instanceof CollidingEntityModel collidingEntityModel) {
      return collidingEntityModel.entities.stream();
    }
    return Stream.of(entity);
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
  public EnergyState getEnergy() {
    return entities
        .stream()
        .map(EntityModel::getEnergy)
        .reduce(EnergyState.zero(), EnergyState::merge);
  }

  @Override
  public BigInteger tickOfBirth() {
    return entities
        .stream()
        .map(EntityModel::tickOfBirth)
        .reduce(ZERO, BigInteger::min); // the oldest entity
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
    // Compute center-of-mass momentum for all colliding entities
    if (entities.isEmpty()) {
      return null;
    }
    if (entities.size() == 1) {
      return entities.getFirst().getMomentum();
    }

    // Reduce with energy weighting
    var first = entities.getFirst();
    Momentum result = first.getMomentum();
    BigInteger resultEnergy = first.getEnergy().value();

    for (int i = 1; i < entities.size(); i++) {
      var next = entities.get(i);
      result = Momentum.merge(result, next.getMomentum(), resultEnergy, next.getEnergy().value());
      resultEnergy = resultEnergy.add(next.getEnergy().value());
    }

    return result;
  }

  @Override
  public BigInteger getNextPossibleAction() {
    // Colliding entities should act immediately
    return tickOfBirth();
  }

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(BigInteger tickCount) {
    var resolvedMomentum = getMomentum();
    var resolvedEnergy = getEnergy();
    var generation = getGeneration();

    return Stream.of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
      if (resolvedMomentum.cost().compareTo(resolvedEnergy.value()) > 0) {
        // merger ... not enough energy for them to continue by themselves
        var total = this.entities.stream()
            .map(EntityModel::getMomentum)
            .map(Momentum::cost)
            .reduce(ZERO, BigInteger::add)
            .add(resolvedMomentum.cost());


        return Stream.of(
            new SingleEntityModel(substrateModel, UUID.randomUUID(), tickCount, position, resolvedEnergy.value()
                .subtract(resolvedMomentum.cost()), getGeneration().add(ONE), new Momentum(total, resolvedMomentum.vector())));
      }

      var momentumCost = this.entities.stream()
          .map(EntityModel::getMomentum)
          .map(Momentum::cost)
          .reduce(ZERO, BigInteger::add)
          .divide(BigInteger.valueOf(entities.size()));

      var offsets = substrateModel.getOffsets();
      var childEnergies = Stream.of(offsets)
          .map(bigIntegers -> Utils.computeEnergyCost(resolvedMomentum.vector(), bigIntegers, momentumCost, generation))
          .toList();

      var energyRequirement = childEnergies.stream().reduce(ZERO, BigInteger::add);

      if (resolvedEnergy.value().compareTo(energyRequirement) >= 0) {
        // explosion > chain reaction

        var index = new AtomicInteger(0);
        return childEnergies.stream()
            .map(childCost -> {
              var offset = offsets[index.getAndIncrement()];

              var newEnergy = resolvedEnergy.value().subtract(energyRequirement).divide(BigInteger.valueOf(26));

              return new SingleEntityModel(
                  substrateModel,
                  UUID.randomUUID(),
                  tickCount,
                  position.offset(offset),
                  newEnergy,
                  generation.add(ONE),
                  new Momentum(childCost, offset));
            });
      }

      var perChildEnergy = resolvedEnergy.value().divide(BigInteger.valueOf(entities.size()));
      if (resolvedMomentum.totalCost().compareTo(BigInteger.TEN) < 0) {
        // annihilation - movement stopped and can't reproduce
        return Stream.empty();
      }

      return entities.stream().map(entityModel -> {
        // bounce not enough to explode but enough to leave
        var newMomentum = Momentum.merge(
            entityModel.getMomentum(),
            resolvedMomentum,
            entityModel.getEnergy().value(),
            resolvedEnergy.value());

        return new SingleEntityModel(substrateModel, UUID.randomUUID(), tickCount, position.offset(newMomentum.vector()), perChildEnergy, generation, newMomentum);
      });
    }));
  }

  @Override
  public String toString() {
    return "CollidingEntityModel{" +
        "entities=" + entities +
        ", identity=" + identity +
        ", position=" + position +
        '}';
  }
}
