package eu.jerrysamek.tickspace.model.substrate;

import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.Arrays;

/**
 * Immutable vector class for N-dimensional integer vectors.
 * Thread-safe: Immutable by design.
 * <p>
 * Use factory methods to create vectors:
 * - Vector.zero(dimensions) - creates zero vector
 * - Vector.of(components...) - creates vector from components
 * - SubstrateModel.createVector() - recommended for entity code
 */
public final class Vector {

  private final FlexInteger[] components;
  private final int dimensions;
  private final int hash;

  // Private constructor - use factory methods
  private Vector(FlexInteger[] components) {
    this.components = components.clone(); // Defensive copy for immutability
    this.dimensions = components.length;
    this.hash = computeSpatialHash(components);
  }

  /**
   * Better hash function for spatial coordinates.
   * Uses long values and prime mixing to reduce collisions.
   */
  private static int computeSpatialHash(FlexInteger[] components) {
    // For small values (fit in long), use optimized spatial hashing
    long hash = 0x517cc1b727220a95L; // Random prime seed

    for (int i = 0; i < components.length; i++) {
      // Convert to long (safe since values fit in long range)
      long value = components[i].longValue();

      // Mix using prime multipliers (different per dimension)
      // These primes are chosen to minimize collisions in 3D space
      long prime = switch (i % 3) {
        case 0 -> 73856093L;   // X axis
        case 1 -> 19349663L;   // Y axis
        case 2 -> 83492791L;   // Z axis
        default -> 50331653L;  // Higher dimensions
      };

      hash ^= value * prime;
    }

    // Final avalanche mixing
    hash ^= (hash >>> 32);
    hash *= 0x27d4eb2d165667c5L;
    hash ^= (hash >>> 29);

    return (int) hash;
  }

  /**
   * Factory: Creates a zero vector of specified dimensions.
   */
  public static Vector zero(int dimensions) {
    var components = new FlexInteger[dimensions];
    Arrays.fill(components, FlexInteger.ZERO);
    return new Vector(components);
  }

  /**
   * Factory: Creates a vector from components.
   */
  public static Vector of(FlexInteger... components) {
    if (components == null || components.length == 0) {
      throw new IllegalArgumentException("Vector must have at least one component");
    }
    return new Vector(components);
  }

  /**
   * Factory: Creates a vector from long components (convenience method).
   */
  public static Vector of(long... components) {
    if (components == null || components.length == 0) {
      throw new IllegalArgumentException("Vector must have at least one component");
    }
    var flexComponents = new FlexInteger[components.length];
    for (int i = 0; i < components.length; i++) {
      flexComponents[i] = FlexInteger.of(components[i]);
    }
    return new Vector(flexComponents);
  }

  /**
   * Gets the number of dimensions.
   */
  public int dimensions() {
    return dimensions;
  }

  /**
   * Gets a component by index.
   */
  public FlexInteger get(int index) {
    return components[index];
  }

  /**
   * Returns a defensive copy of components array.
   * Use sparingly - prefer vector methods.
   */
  public FlexInteger[] toArray() {
    return components.clone();
  }

  /**
   * Computes the dot product with another vector.
   */
  public FlexInteger dot(Vector other) {
    var minLength = Math.min(dimensions, other.dimensions);
    var result = FlexInteger.ZERO;
    for (var i = 0; i < minLength; i++) {
      result = result.add(components[i].multiply(other.components[i]));
    }
    return result;
  }

  /**
   * Computes the squared magnitude (more efficient than magnitude).
   */
  public FlexInteger magnitudeSquared() {
    var result = FlexInteger.ZERO;
    for (var component : components) {
      result = result.add(component.multiply(component));
    }
    return result;
  }

  /**
   * Computes the Euclidean magnitude.
   */
  public FlexInteger magnitude() {
    return sqrt(magnitudeSquared());
  }

  /**
   * Adds another vector component-wise.
   */
  public Vector add(Vector other) {
    if (dimensions != other.dimensions) {
      throw new IllegalArgumentException("Vectors must have same dimensions: " + dimensions + " vs " + other.dimensions);
    }
    var result = new FlexInteger[dimensions];
    for (var i = 0; i < dimensions; i++) {
      result[i] = components[i].add(other.components[i]);
    }
    return new Vector(result);
  }

  /**
   * Subtracts another vector component-wise.
   */
  public Vector subtract(Vector other) {
    if (dimensions != other.dimensions) {
      throw new IllegalArgumentException("Vectors must have same dimensions: " + dimensions + " vs " + other.dimensions);
    }
    var result = new FlexInteger[dimensions];
    for (var i = 0; i < dimensions; i++) {
      result[i] = components[i].subtract(other.components[i]);
    }
    return new Vector(result);
  }

  /**
   * Multiplies by a scalar.
   */
  public Vector scale(FlexInteger scalar) {
    var result = new FlexInteger[dimensions];
    for (var i = 0; i < dimensions; i++) {
      result[i] = components[i].multiply(scalar);
    }
    return new Vector(result);
  }

  /**
   * Finds the maximum absolute component value.
   */
  public FlexInteger maxComponent() {
    var max = FlexInteger.ZERO;
    for (var component : components) {
      var abs = component.abs();
      if (abs.compareTo(max) > 0) {
        max = abs;
      }
    }
    return max;
  }

  /**
   * Normalizes so maximum component has magnitude 1 (enforces speed limit).
   */
  public Vector normalizeMaxComponent() {
    var max = maxComponent();

    if (max.compareTo(FlexInteger.ZERO) == 0) {
      return Vector.zero(dimensions);
    }

    var result = new FlexInteger[dimensions];
    for (int i = 0; i < dimensions; i++) {
      result[i] = components[i].divide(max);
    }
    return new Vector(result);
  }

  /**
   * Checks if this is the zero vector.
   */
  public boolean isZero() {
    for (var component : components) {
      if (!component.equals(FlexInteger.ZERO)) {
        return false;
      }
    }
    return true;
  }

  /**
   * Sums all components of the vector.
   * Useful for computing total costs or other aggregate values.
   *
   * @return sum of all components
   */
  public FlexInteger sumComponents() {
    var sum = FlexInteger.ZERO;
    for (var component : components) {
      sum = sum.add(component);
    }
    return sum;
  }

  /**
   * Integer square root (floor) - utility method.
   */
  private static FlexInteger sqrt(FlexInteger x) {
    if (x.compareTo(FlexInteger.ZERO) < 0) {
      throw new IllegalArgumentException("Cannot take square root of negative number: " + x);
    }
    if (x.equals(FlexInteger.ZERO) || x.equals(FlexInteger.ONE)) {
      return x;
    }

    var r = FlexInteger.ZERO;
    var bit = FlexInteger.ONE.shiftLeft(x.bitLength() / 2 + 1);

    while (bit.compareTo(FlexInteger.ZERO) > 0) {
      var t = r.add(bit);
      if (t.multiply(t).compareTo(x) <= 0) {
        r = t;
      }
      bit = bit.shiftRight(1);
    }

    return r;
  }

  @Override
  public boolean equals(Object o) {
    if (this == o) return true;
    if (!(o instanceof Vector vector)) return false;
    return Arrays.equals(components, vector.components);
  }

  @Override
  public int hashCode() {
    return hash;
  }

  @Override
  public String toString() {
    return "Vector" + Arrays.toString(components);
  }
}
