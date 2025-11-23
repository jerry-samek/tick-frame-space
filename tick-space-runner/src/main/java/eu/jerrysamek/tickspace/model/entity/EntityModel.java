package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.UUID;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.TWO;
import static java.math.BigInteger.ZERO;

public class EntityModel implements TickTimeConsumer<EntityModelUpdate> {

  private final UUID identity;
  private BigInteger energy;
  private final Position position;
  private final Momentum momentum;

  public EntityModel(UUID identity, Position position, BigInteger initialEnergy, Momentum momentum) {
    this.identity = identity;
    this.energy = initialEnergy;
    this.position = position;
    this.momentum = momentum;
  }

  public UUID getIdentity() {
    return identity;
  }

  public BigInteger getEnergy() {
    return energy;
  }

  public Position getPosition() {
    return position;
  }

  @Override
  public Stream<EntityModelUpdate> onTick(BigInteger tickCount) {
    var newEnergy = energy.add(ONE);

    long numChildren = 6;

    var energyRequirement = momentum.cost().multiply(BigInteger.valueOf(numChildren)).divide(BigInteger.TWO);
    // Division threshold: split if energy >= 6
    if (newEnergy.compareTo(energyRequirement) >= 0) {
      var childEnergy = newEnergy.divide(BigInteger.valueOf(numChildren));

      // Six axis-aligned offsets (octahedral shell)
      BigInteger[][] offsets = {
          {ONE, ZERO, ZERO}, {ONE.negate(), ZERO, ZERO},
          {ZERO, ONE, ZERO}, {ZERO, ONE.negate(), ZERO},
          {ZERO, ZERO, ONE}, {ZERO, ZERO, ONE.negate()}
      };

      return Arrays.stream(offsets)
          .map(offset -> _ -> new EntityModel(
              UUID.randomUUID(),
              position.offset(offset),
              childEnergy,
              new Momentum(momentum.cost().multiply(TWO), offset)
          ));
    } else if (newEnergy.compareTo(momentum.cost()) >= 0) {
      return Stream.of(_ -> new EntityModel(identity, position.offset(momentum.vector()), newEnergy, momentum));
    } else {
      energy = newEnergy; // update inner state but nothing else

      return Stream.empty();
    }
  }

  @Override
  public String toString() {
    return "EntityModel{" +
        "energy=" + energy +
        ", position=" + position +
        '}';
  }
}
