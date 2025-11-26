package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public class SingleEntityModel implements EntityModel {

  private final UUID identity;
  private final BigInteger energy;
  private final BigInteger generation;
  private final Position position;
  private final Momentum momentum;

  private final List<BigInteger> childEnergyThresholds;
  private final BigInteger completeDivisionThreshold;

  public SingleEntityModel(UUID identity, Position position, BigInteger initialEnergy, BigInteger generation, Momentum momentum) {
    var thresholds = Stream.of(OFFSETS)
        .map(bigIntegers -> Utils.computeEnergyCost(momentum.vector(), bigIntegers, momentum.cost(), generation))
        .toList();

    this(identity, position, initialEnergy, generation, momentum,
        thresholds,
        thresholds.stream().reduce(ZERO, BigInteger::add)
    );
  }

  private SingleEntityModel(UUID identity, Position position, BigInteger energy, BigInteger generation, Momentum momentum, List<BigInteger> childEnergyThresholds, BigInteger completeDivisionThreshold) {
    this.identity = identity;
    this.energy = energy;
    this.position = position;
    this.generation = generation;
    this.momentum = momentum;
    this.childEnergyThresholds = childEnergyThresholds;
    this.completeDivisionThreshold = completeDivisionThreshold;
  }

  @Override
  public UUID getIdentity() {
    return identity;
  }

  @Override
  public BigInteger getEnergy() {
    return energy;
  }

  @Override
  public Position getPosition() {
    return position;
  }

  @Override
  public BigInteger getGeneration() {
    return generation;
  }

  @Override
  public Momentum getMomentum() {
    return momentum;
  }


  @Override
  public Stream<EntityModelUpdate> onTick(BigInteger tickCount) {
    var newEnergy = energy.add(ONE);

    return Stream.of(_ -> {
      if (newEnergy.compareTo(completeDivisionThreshold) >= 0) {
        // Six axis-aligned offsets (octahedral shell)
        var index = new AtomicInteger(0);
        return childEnergyThresholds.stream()
            .map(childCost -> {
              var offset = OFFSETS[index.getAndIncrement()];

              return new SingleEntityModel(
                  UUID.randomUUID(),
                  position.offset(offset),
                  ZERO,
                  generation.add(ONE),
                  new Momentum(momentum.cost().add(childCost), offset));
            });
      } else if (newEnergy.compareTo(momentum.cost()) >= 0) {
        return Stream.of(new SingleEntityModel(identity, position.offset(momentum.vector()), newEnergy, generation, momentum, childEnergyThresholds, completeDivisionThreshold));
      } else {
        return Stream.of(new SingleEntityModel(identity, position, newEnergy, generation, momentum, childEnergyThresholds, completeDivisionThreshold));
      }
    });
  }

  @Override
  public final boolean equals(Object o) {
    if (!(o instanceof SingleEntityModel that)) return false;

    return identity.equals(that.identity);
  }

  @Override
  public int hashCode() {
    return identity.hashCode();
  }

  @Override
  public String toString() {
    return "EntityModel{" +
        "energy=" + energy +
        ", position=" + position +
        '}';
  }

}
