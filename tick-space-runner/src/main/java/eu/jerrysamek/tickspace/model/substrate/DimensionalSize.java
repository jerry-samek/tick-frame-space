package eu.jerrysamek.tickspace.model.substrate;

import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.stream.Stream;

/**
 * Holds dimensional lengths as BigInteger values.
 * Each dimension's length is stored independently in an array.
 */
public class DimensionalSize implements TickTimeConsumer<DimensionalSizeUpdate> {
  private final BigInteger[] dimensions;

  /**
   * Creates a DimensionalSize with the specified number of dimensions.
   * All dimensions are initialized to zero.
   *
   * @param dimensionCount the number of dimensions
   */
  public DimensionalSize(int dimensionCount) {
    if (dimensionCount <= 0) {
      throw new IllegalArgumentException("Dimension count must be positive");
    }

    this.dimensions = new BigInteger[dimensionCount];

    Arrays.fill(this.dimensions, BigInteger.ZERO);
  }

  /**
   * Gets the number of dimensions.
   *
   * @return the dimension count
   */
  public int getDimensionCount() {
    return dimensions.length;
  }

  /**
   * Gets the length of a specific dimension.
   *
   * @param index the dimension index
   * @return the length of the dimension
   */
  public BigInteger getDimensionSize(int index) {
    return dimensions[index];
  }

  @Override
  public Stream<TickAction<DimensionalSizeUpdate>> onTick(BigInteger tickCount) {
    return Stream.of(new TickAction<>(TickActionType.UPDATE, () -> Arrays.fill(dimensions, tickCount)));
  }

  @Override
  public String toString() {
    return "DimensionalSize" + Arrays.toString(dimensions);
  }
}
