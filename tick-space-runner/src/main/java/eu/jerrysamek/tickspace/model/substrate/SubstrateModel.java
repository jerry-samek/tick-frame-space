package eu.jerrysamek.tickspace.model.substrate;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeUpdate;

import java.math.BigInteger;
import java.util.stream.Stream;

/**
 * Represents the substrate model that manages dimensional sizes.
 * Receives updates from TickTimeModel and updates its dimensional length accordingly.
 */
public class SubstrateModel implements TickTimeConsumer<TickTimeUpdate> {

  private final DimensionalSize dimensionalSize;
  private final EntitiesRegistry registry;

  /**
   * Creates a SubstrateModel with the specified number of dimensions.
   *
   * @param dimensionCount the number of dimensions
   */
  public SubstrateModel(int dimensionCount, EntitiesRegistry registry) {
    this.dimensionalSize = new DimensionalSize(dimensionCount);
    this.registry = registry;
  }

  /**
   * Called when a tick occurs. Increments all dimensions by 1.
   */
  @Override
  public Stream<TickTimeUpdate> onTick(BigInteger tickCount) {
    return Stream.concat(
        dimensionalSize
            .onTick(tickCount)
            .map(dimensionalSizeUpdate -> dimensionalSizeUpdate::run),
        registry
            .onTick(tickCount)
            .map(substrateModelUpdate -> () -> substrateModelUpdate.update(this)));
  }

  /**
   * Gets the dimensional size.
   *
   * @return the dimensional size
   */
  public DimensionalSize getDimensionalSize() {
    return dimensionalSize;
  }

  @Override
  public String toString() {
    return "SubstrateModel{" +
        "dimensionalSize=" + dimensionalSize +
        '}';
  }
}
