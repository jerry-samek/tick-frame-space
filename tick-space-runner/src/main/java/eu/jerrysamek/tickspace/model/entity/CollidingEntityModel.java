package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.concurrent.atomic.AtomicReference;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.TEN;
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
    var momentum = computeMomentum(entity1.getMomentum(), entity2.getMomentum(), entity1.getEnergy().getEnergy(), entity2.getEnergy().getEnergy());
    if (momentum.cost().compareTo(TEN) >= 0) {
      // it naively solves merge and bounce by one single entity model
      return new SingleEntityModel(
          substrateModel,
          UUID.randomUUID(),
          entity1.getPosition(),
          entity1.getEnergy().merge(entity2.getEnergy()).getEnergy(),
          entity1.getGeneration().max(entity2.getGeneration()).add(ONE),
          momentum
      );
    } else {

      // total annihilation - or at least this is more like wave cancellation
      return null;
    }
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
    BigInteger resultEnergy = first.getEnergy().getEnergy();

    for (int i = 1; i < entities.size(); i++) {
      var next = entities.get(i);
      result = computeMomentum(result, next.getMomentum(), resultEnergy, next.getEnergy().getEnergy());
      resultEnergy = resultEnergy.add(next.getEnergy().getEnergy());
    }

    return result;
  }

  /**
   * Compute center-of-mass momentum from two colliding entities.
   * Uses conservation of momentum: p = energy × velocity
   * where velocity = vector / cost
   *
   * @param m1      First entity's momentum
   * @param m2      Second entity's momentum
   * @param energy1 First entity's energy (acts as "mass")
   * @param energy2 Second entity's energy (acts as "mass")
   * @return Combined momentum in a center-of-mass frame
   */
  private static Momentum computeMomentum(Momentum m1, Momentum m2,
                                          BigInteger energy1, BigInteger energy2) {
    int dimensions = m1.vector().length;

    // Handle zero energy edge case
    if (energy1.equals(ZERO) && energy2.equals(ZERO)) {
      BigInteger[] zeroVector = new BigInteger[dimensions];
      Arrays.fill(zeroVector, ZERO);
      return new Momentum(ONE, zeroVector); // Default at-rest state
    }

    BigInteger totalEnergy = energy1.add(energy2);

    // Compute momentum for each entity: p = energy × (vector/cost)
    // Working in integer domain: p[i] × cost = energy × vector[i]
    BigInteger[] totalMomentum = new BigInteger[dimensions];

    for (int i = 0; i < dimensions; i++) {
      // Momentum = energy × velocity = energy × (vector / cost)
      // Cross-multiply to avoid division: p1×c2 + p2×c1
      BigInteger momentum1 = m1.vector()[i].multiply(energy1);
      BigInteger momentum2 = m2.vector()[i].multiply(energy2);

      totalMomentum[i] = momentum1.multiply(m2.cost())
          .add(momentum2.multiply(m1.cost()));
    }

    // Common denominator
    BigInteger costProduct = m1.cost().multiply(m2.cost());

    // Check for zero total momentum (annihilation or both at rest)
    boolean isZeroMomentum = true;
    for (BigInteger p : totalMomentum) {
      if (!p.equals(ZERO)) {
        isZeroMomentum = false;
        break;
      }
    }

    if (isZeroMomentum) {
      // Perfect annihilation or both at rest
      BigInteger[] zeroVector = new BigInteger[dimensions];
      Arrays.fill(zeroVector, ZERO);
      return new Momentum(ZERO, zeroVector);
    }

    // Calculate magnitude of total momentum
    BigInteger momentumMagnitudeSq = ZERO;
    for (BigInteger p : totalMomentum) {
      momentumMagnitudeSq = momentumMagnitudeSq.add(p.pow(2));
    }

    BigInteger momentumMagnitude = momentumMagnitudeSq.sqrt();

    // Normalize direction vector
    BigInteger[] newVector = new BigInteger[dimensions];
    for (int i = 0; i < dimensions; i++) {
      newVector[i] = totalMomentum[i].divide(momentumMagnitude);
    }

    // Calculate a new cost (inverse of speed)
    // speed = |momentum| / (total_energy × cost_product)
    // cost = (total_energy × cost_product) / |momentum|
    BigInteger newCost = totalEnergy.multiply(costProduct).divide(momentumMagnitude);

    // Ensure minimum cost (speed limit)
    if (newCost.compareTo(ONE) < 0) {
      newCost = ONE;  // Maximum speed limit (speed of light analogue)
    }

    return new Momentum(newCost, newVector);
  }

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(BigInteger tickCount) {
    var resolvedMomentum = getMomentum();
    var resolvedEnergy = getEnergy();
    var generation = getGeneration();

    return Stream.of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
      if (resolvedMomentum.cost().compareTo(resolvedEnergy.getEnergy()) > 0) {
        // merger ... not enough energy for them to continue by themselves
        var total = this.entities.stream()
            .map(EntityModel::getMomentum)
            .map(Momentum::cost)
            .reduce(ZERO, BigInteger::add)
            .add(resolvedMomentum.cost());

        return Stream.of(
            new SingleEntityModel(substrateModel, UUID.randomUUID(), position, resolvedEnergy.getEnergy()
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

      if (resolvedEnergy.getEnergy().compareTo(energyRequirement) >= 0) {
        // explosion > chain reaction

        var index = new AtomicInteger(0);
        return childEnergies.stream()
            .map(childCost -> {
              var offset = offsets[index.getAndIncrement()];

              var newEnergy = resolvedEnergy.getEnergy().subtract(energyRequirement).divide(BigInteger.valueOf(26));

              return new SingleEntityModel(
                  substrateModel,
                  UUID.randomUUID(),
                  position.offset(offset),
                  newEnergy,
                  generation.add(ONE),
                  new Momentum(childCost, offset));
            });
      }

      var perChildEnergy = resolvedEnergy.getEnergy().divide(BigInteger.valueOf(entities.size()));
      if (resolvedMomentum.totalCost().compareTo(BigInteger.TEN) < 0) {
        // annihilation - movement stopped and can't reproduce
        return Stream.empty();
      }

      return entities.stream().map(entityModel -> {
        // bounce not enough to explode but enough to leave
        var newMomentum = computeMomentum(
            entityModel.getMomentum(),
            resolvedMomentum,
            entityModel.getEnergy().getEnergy(),
            resolvedEnergy.getEnergy());

        return new SingleEntityModel(substrateModel, UUID.randomUUID(), position.offset(newMomentum.vector()), perChildEnergy, generation, newMomentum);
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
