package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

import static eu.jerrysamek.tickspace.model.util.FlexInteger.ONE;
import static eu.jerrysamek.tickspace.model.util.FlexInteger.ZERO;

public class CollidingEntityModel implements EntityModel {

  private final List<EntityModel> entities;
  private final UUID identity;
  private final Position position;

  public static final AtomicReference<FlexInteger> totalEnergyLoss = new AtomicReference<>(ZERO);

  /**
   * It resolves collision by ignoring the colliding entity. The proper model is the full. However, it is not working properly yet.
   *
   * @param entity1 EntityModel
   * @param entity2 EntityModel
   * @return only the entity1
   */
  public static EntityModel naive(FlexInteger tick, SubstrateModel substrateModel, EntityModel entity1, EntityModel entity2) {
    var momentum = Momentum.merge(entity1.getMomentum(), entity2.getMomentum(), entity1.getEnergy(tick), entity2.getEnergy(tick));
    if (momentum.totalCost().compareTo(ONE) >= 0) {
      // it naively solves merge and bounce by one single entity model
      var newEnergy = entity1.getEnergy(tick).add(entity2.getEnergy(tick)).subtract(momentum.totalCost());
      if (newEnergy.compareTo(ZERO) > 0) {
        return new SingleEntityModel(
            substrateModel,
            UUID.randomUUID(),
            entity1.tickOfBirth().min(entity2.tickOfBirth()),
            entity1.getPosition(),
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
  public FlexInteger getEnergy(FlexInteger tick) {
    return entities
        .stream()
        .map(entityModel -> entityModel.getEnergy(tick))
        .reduce(ZERO, FlexInteger::add);
  }

  @Override
  public FlexInteger tickOfBirth() {
    return entities
        .stream()
        .map(EntityModel::tickOfBirth)
        .reduce(ZERO, FlexInteger::min); // the oldest entity
  }

  @Override
  public Position getPosition() {
    return position;
  }

  @Override
  public FlexInteger getGeneration() {
    return entities.stream()
        .map(EntityModel::getGeneration)
        .max(FlexInteger::compareTo)
        .orElse(ZERO);
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
    FlexInteger resultEnergy = first.getEnergy(first.tickOfBirth()); // TODO

    for (int i = 1; i < entities.size(); i++) {
      var next = entities.get(i);
      result = Momentum.merge(result, next.getMomentum(), resultEnergy, next.getEnergy(next.tickOfBirth()));// TODO
      resultEnergy = resultEnergy.add(next.getEnergy(next.tickOfBirth()));// TODO
    }

    return result;
  }

  @Override
  public FlexInteger getNextPossibleAction() {
    // Colliding entities should act immediately
    return tickOfBirth();
  }

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
    var resolvedMomentum = getMomentum();
    var resolvedEnergy = getEnergy(tickCount);
    var generation = getGeneration();

    return Stream.of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
      if (resolvedMomentum.cost().compareTo(resolvedEnergy) > 0) {
        // merger ... not enough energy for them to continue by themselves
        var total = this.entities.stream()
            .map(EntityModel::getMomentum)
            .map(Momentum::cost)
            .reduce(ZERO, FlexInteger::add)
            .add(resolvedMomentum.cost());


        return Stream.of(
            new SingleEntityModel(substrateModel, UUID.randomUUID(), tickCount, position, getGeneration().add(ONE), new Momentum(total, resolvedMomentum.vector())));
      }

      var momentumCost = this.entities.stream()
          .map(EntityModel::getMomentum)
          .map(Momentum::cost)
          .reduce(ZERO, FlexInteger::add)
          .divide(FlexInteger.of(entities.size()));

      var offsets = substrateModel.getOffsets();
      var childEnergies = Stream.of(offsets)
          .map(bigIntegers -> Utils.computeEnergyCost(resolvedMomentum.vector(), bigIntegers, momentumCost, generation))
          .toList();

      var energyRequirement = childEnergies.stream().reduce(ZERO, FlexInteger::add);

      if (resolvedEnergy.compareTo(energyRequirement) >= 0) {
        // explosion > chain reaction

        var index = new AtomicInteger(0);
        return childEnergies.stream()
            .map(childCost -> {
              var offset = offsets[index.getAndIncrement()];

              return new SingleEntityModel(
                  substrateModel,
                  UUID.randomUUID(),
                  tickCount,
                  position.offset(offset),
                  generation.add(ONE),
                  new Momentum(childCost, offset));
            });
      }

      if (resolvedMomentum.totalCost().compareTo(FlexInteger.TEN) < 0) {
        // annihilation - movement stopped and can't reproduce
        return Stream.empty();
      }

      return entities.stream().map(entityModel -> {
        // bounce not enough to explode but enough to leave
        var newMomentum = Momentum.merge(
            entityModel.getMomentum(),
            resolvedMomentum,
            entityModel.getEnergy(tickCount),
            resolvedEnergy);

        return new SingleEntityModel(substrateModel, UUID.randomUUID(), tickCount, position.offset(newMomentum.vector()), generation, newMomentum);
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
