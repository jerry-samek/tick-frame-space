package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.List;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

import static eu.jerrysamek.tickspace.model.util.FlexInteger.ONE;
import static eu.jerrysamek.tickspace.model.util.FlexInteger.ZERO;

public class SingleEntityModel implements EntityModel {

  private final UUID identity;
  private final FlexInteger generation;
  private final Position position;
  private final Momentum momentum;

  private final List<FlexInteger> childEnergyThresholds;
  private final FlexInteger startOfLife;
  private final FlexInteger completeDivisionThreshold;
  private final FlexInteger nextPossibleAction;
  private final FlexInteger endOfLife;

  public SingleEntityModel(SubstrateModel model, UUID identity, FlexInteger startOfLife, Position position, FlexInteger generation, Momentum momentum) {
    // Optimize: use cached offset metadata to avoid expensive magnitude calculations
    var offsetMetadata = model.getOffsetMetadata();
    var thresholdsArray = new FlexInteger[offsetMetadata.length];
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

    this(identity, startOfLife, position, generation, momentum,
        List.of(thresholdsArray),
        divisionThreshold,
        startOfLife.add(momentum.cost()),
        divisionThreshold.add(startOfLife)
    );
  }

  private SingleEntityModel(
      UUID identity,
      FlexInteger startOfLife,
      Position position,
      FlexInteger generation,
      Momentum momentum,
      List<FlexInteger> childEnergyThresholds,
      FlexInteger completeDivisionThreshold, FlexInteger nextPossibleAction, FlexInteger endOfLife) {
    this.identity = identity;
    this.startOfLife = startOfLife;
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
  public FlexInteger getEnergy(FlexInteger tick) {
    return tick.subtract(startOfLife);
  }

  @Override
  public FlexInteger tickOfBirth() {
    return startOfLife;
  }

  @Override
  public Position getPosition() {
    return position;
  }

  @Override
  public FlexInteger getGeneration() {
    return generation;
  }

  @Override
  public Momentum getMomentum() {
    return momentum;
  }

  @Override
  public FlexInteger getNextPossibleAction() {
    return nextPossibleAction;
  }

  @Override
  public Stream<TickAction<EntityModelUpdate>> onTick(FlexInteger tickCount) {
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
                          generation.add(ONE),
                          new Momentum(momentum.cost().add(childCost), offset));
                    });
              } else {
                return Stream.of(new SingleEntityModel(identity, startOfLife, position.offset(momentum.vector()), generation, momentum, childEnergyThresholds, completeDivisionThreshold, nextPossibleAction.add(momentum.cost()), endOfLife));
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
        ", startOfLife=" + startOfLife +
        ", generation=" + generation +
        ", position=" + position +
        ", momentum=" + momentum +
        ", childEnergyThresholds=" + childEnergyThresholds +
        ", completeDivisionThreshold=" + completeDivisionThreshold +
        '}';
  }
}
