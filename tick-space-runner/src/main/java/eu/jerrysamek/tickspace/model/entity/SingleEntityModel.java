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
  private final BigInteger startOfLife;
  private final BigInteger completeDivisionThreshold;
  private final BigInteger nextPossibleAction;
  private final BigInteger endOfLife;

  public SingleEntityModel(SubstrateModel model, UUID identity, BigInteger startOfLife, Position position, BigInteger initialEnergy, BigInteger generation, Momentum momentum) {
    // Optimize: use cached offset metadata to avoid expensive magnitude calculations
    var offsetMetadata = model.getOffsetMetadata();
    var thresholdsArray = new BigInteger[offsetMetadata.length];
    var divisionThreshold = ZERO;

    for (int i = 0; i < offsetMetadata.length; i++) {
      var metadata = offsetMetadata[i];
      // Use an optimized version with precomputed magnitude
      var cost = Utils.computeEnergyCostOptimized(
          momentum.vector(),
          metadata.offset(),
          metadata.magnitude(),  // Use cached magnitude
          momentum.cost(),
          generation
      );
      thresholdsArray[i] = cost;
      divisionThreshold = divisionThreshold.add(cost);
    }

    this(identity, startOfLife, position, initialEnergy, generation, momentum,
        List.of(thresholdsArray),
        divisionThreshold,
        startOfLife.add(momentum.cost()),
        divisionThreshold.add(startOfLife)
    );
  }

  private SingleEntityModel(
      UUID identity,
      BigInteger startOfLife,
      Position position,
      BigInteger energyState,
      BigInteger generation,
      Momentum momentum,
      List<BigInteger> childEnergyThresholds,
      BigInteger completeDivisionThreshold, BigInteger nextPossibleAction, BigInteger endOfLife) {
    this.identity = identity;
    this.startOfLife = startOfLife;
    this.energyState = new EnergyState(energyState);
    this.position = position;
    this.generation = generation;
    this.momentum = momentum;
    this.childEnergyThresholds = childEnergyThresholds;
    this.completeDivisionThreshold = completeDivisionThreshold;
    this.nextPossibleAction = nextPossibleAction;
    this.endOfLife = endOfLife;
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
  public BigInteger tickOfBirth() {
    return startOfLife;
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
  public BigInteger getNextPossibleAction() {
    return nextPossibleAction;
  }

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(BigInteger tickCount) {
    if (tickCount.compareTo(nextPossibleAction) < 0) {
      return Stream.of(new TickAction<>(TickActionType.WAIT, _ -> Stream.empty()));
    }

    return Stream
        .of(new TickAction<>(TickActionType.UPDATE, substrateModel -> {
              if (tickCount.compareTo(endOfLife) >= 0) {
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
                          tickCount,
                          newPosition,
                          ONE,
                          generation.add(ONE),
                          new Momentum(momentum.cost().add(childCost), offset));
                    });
              } else {
                return Stream.of(new SingleEntityModel(identity, startOfLife, position.offset(momentum.vector()), tickCount.subtract(startOfLife), generation, momentum, childEnergyThresholds, completeDivisionThreshold, nextPossibleAction.add(momentum.cost()), endOfLife));
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
        ", energy=" + energyState.value() +
        ", generation=" + generation +
        ", position=" + position +
        ", momentum=" + momentum +
        ", childEnergyThresholds=" + childEnergyThresholds +
        ", completeDivisionThreshold=" + completeDivisionThreshold +
        '}';
  }
}
