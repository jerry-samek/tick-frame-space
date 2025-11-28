package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public class SingleEntityModel implements EntityModel {

  private final UUID identity;
  private final EnergyState energyState;
  private final BigInteger generation;
  private final Position position;
  private final Momentum momentum;

  private final List<BigInteger> childEnergyThresholds;
  private final BigInteger completeDivisionThreshold;

  public SingleEntityModel(SubstrateModel model, UUID identity, Position position, BigInteger initialEnergy, BigInteger generation, Momentum momentum) {
    // Optimize: use array-based loop instead of Stream to reduce allocation overhead
    var offsets = model.getOffsets();
    var thresholdsArray = new BigInteger[offsets.length];
    var completeDivisionThreshold = ZERO;

    for (int i = 0; i < offsets.length; i++) {
      var cost = Utils.computeEnergyCost(momentum.vector(), offsets[i], momentum.cost(), generation);
      thresholdsArray[i] = cost;
      completeDivisionThreshold = completeDivisionThreshold.add(cost);
    }

    this(identity, position, initialEnergy, generation, momentum,
        List.of(thresholdsArray),
        completeDivisionThreshold
    );
  }

  private SingleEntityModel(UUID identity, Position position, BigInteger energyState, BigInteger generation, Momentum momentum, List<BigInteger> childEnergyThresholds, BigInteger completeDivisionThreshold) {
    this.identity = identity;
    this.energyState = new EnergyState(energyState);
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
  public EnergyState getEnergy() {
    return energyState;
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
  public Stream<TickAction<EntityModelUpdate>> onTick(BigInteger tickCount) {
    var newEnergy = energyState.increase();

    if (newEnergy.remainder(momentum.cost()).compareTo(ZERO) != 0) {
      return Stream.of(new TickAction<>(TickActionType.WAIT, _ -> Stream.empty()));
    }

    return Stream
        .of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
              if (newEnergy.compareTo(completeDivisionThreshold) >= 0) {
                var offsets = substrateModel.getOffsets();
                // Create children with matching offset-cost pairs
                var index = new AtomicInteger(0);
                return childEnergyThresholds.stream()
                    .map(childCost -> {
                      var offsetIndex = index.getAndIncrement();
                      var offset = offsets[offsetIndex];
                      var newPosition = position.offset(offset);

                      return new SingleEntityModel(
                          substrateModel,
                          UUID.randomUUID(),
                          newPosition,
                          ONE,
                          generation.add(ONE),
                          new Momentum(momentum.cost().add(childCost), offset));
                    });
              } else if (newEnergy.remainder(momentum.cost()).compareTo(ZERO) == 0) {
                return Stream.of(new SingleEntityModel(identity, position.offset(momentum.vector()), newEnergy, generation, momentum, childEnergyThresholds, completeDivisionThreshold));
              } else {
                return Stream.of(new SingleEntityModel(identity, position, newEnergy, generation, momentum, childEnergyThresholds, completeDivisionThreshold));
              }
            })
        );
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
    return "SingleEntityModel{" +
        "identity=" + identity +
        ", energy=" + energyState.getEnergy() +
        ", generation=" + generation +
        ", position=" + position +
        ", momentum=" + momentum +
        ", childEnergyThresholds=" + childEnergyThresholds +
        ", completeDivisionThreshold=" + completeDivisionThreshold +
        '}';
  }
}
