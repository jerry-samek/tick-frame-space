package eu.jerrysamek.tickspace.model.substrate;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeUpdate;

import java.math.BigInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

/**
 * Represents the substrate model that manages dimensional sizes.
 * Receives updates from TickTimeModel and updates its dimensional length accordingly.
 */
public class SubstrateModel implements TickTimeConsumer<TickTimeUpdate> {

  /**
   * Cached metadata for each offset to optimize cost calculations.
   * Stores precomputed magnitudes to avoid repeated expensive calculations.
   */
  public record OffsetMetadata(Vector offset, BigInteger magnitude) {}

  private final DimensionalSize dimensionalSize;
  private final EntitiesRegistry registry;
  private final Vector[] offsets;
  private final OffsetMetadata[] offsetMetadata;

  /**
   * Creates a SubstrateModel with the specified number of dimensions.
   *
   * @param dimensionCount the number of dimensions
   */
  public SubstrateModel(int dimensionCount, EntitiesRegistry registry) {
    this.dimensionalSize = new DimensionalSize(dimensionCount);
    this.registry = registry;
    this.offsets = generateOffsets(dimensionCount);

    // Precompute offset metadata for performance optimization
    this.offsetMetadata = new OffsetMetadata[offsets.length];
    for (int i = 0; i < offsets.length; i++) {
      this.offsetMetadata[i] = new OffsetMetadata(
          offsets[i],
          offsets[i].magnitude()  // Cache the magnitude
      );
    }
  }

  /**
   * Called when a tick occurs. Increments all dimensions by 1.
   */
  @Override
  public Stream<TickAction<TickTimeUpdate>> onTick(BigInteger tickCount) {
    return Stream.concat(
        dimensionalSize
            .onTick(tickCount)
            .map(tickAction -> new TickAction<>(tickAction.type(), () -> tickAction.action().run())),
        registry
            .onTick(tickCount)
            .filter(substrateModelUpdateTickAction -> substrateModelUpdateTickAction.type() == TickActionType.UPDATE)
            .map(TickAction::action)
            .map(substrateModelUpdate -> new TickAction<>(TickActionType.UPDATE, () -> substrateModelUpdate.update(this))));
  }

  /**
   * Gets the dimensional size.
   *
   * @return the dimensional size
   */
  public DimensionalSize getDimensionalSize() {
    return dimensionalSize;
  }

  /**
   * Gets all potential offsets entities can move to
   *
   * @return the offset vectors
   */
  public Vector[] getOffsets() {
    return offsets;
  }

  /**
   * Gets precomputed metadata for all offsets (includes cached magnitudes).
   * Use this for optimized cost calculations.
   *
   * @return the offset metadata array
   */
  public OffsetMetadata[] getOffsetMetadata() {
    return offsetMetadata;
  }

  /**
   * Generates all neighbor offsets for N-dimensional space.
   * Returns all combinations of {-1, 0, 1}^N except the all-zero vector.
   * Each offset vector has exactly dimensionCount elements.
   * <p>
   * Examples:
   * - 1D: 2 offsets ([-1], [1])
   * - 2D: 8 offsets (faces + corners of a square)
   * - 3D: 26 offsets (faces + edges + corners of a cube)
   * - 4D: 80 offsets (all neighbors in 4D space)
   *
   * @param dimensionCount number of dimensions
   * @return array of offset vectors (3^N - 1 total)
   */
  private static Vector[] generateOffsets(int dimensionCount) {
    // Total combinations: 3^dimensionCount (each dim can be -1, 0, or 1)
    var totalCombinations = (int) Math.pow(3, dimensionCount);

    // Exclude all-zero vector: 3^dimensionCount - 1
    var offsets = new Vector[totalCombinations - 1];

    var offsetIndex = 0;

    // Iterate through all base-3 combinations
    for (var i = 0; i < totalCombinations; i++) {
      var components = new BigInteger[dimensionCount];
      var value = i;
      var isZeroVector = true;

      // Convert i to base-3 representation, each digit becomes a dimension value
      for (var dim = 0; dim < dimensionCount; dim++) {
        var digit = value % 3;
        value /= 3;

        // Map base-3 digit to offset value:
        // 0 → -1, 1 → 0, 2 → +1
        components[dim] = switch (digit) {
          case 0 -> ONE.negate();  // -1
          case 1 -> ZERO;          //  0
          case 2 -> ONE;           // +1
          default -> throw new IllegalStateException("Invalid base-3 digit: " + digit);
        };

        if (!components[dim].equals(ZERO)) {
          isZeroVector = false;
        }
      }

      // Skip the all-zero vector [0, 0, ..., 0]
      if (!isZeroVector) {
        offsets[offsetIndex++] = Vector.of(components);
      }
    }

    return offsets;
  }

  /**
   * Flips double-buffered state after all tick actions complete.
   * Called by TickTimeModel to ensure buffer swap happens AFTER
   * all parallel entity updates finish.
   */
  public void flip() {
    registry.flip();
  }

  @Override
  public String toString() {
    return "SubstrateModel{" +
        "dimensionalSize=" + dimensionalSize +
        '}';
  }
}
