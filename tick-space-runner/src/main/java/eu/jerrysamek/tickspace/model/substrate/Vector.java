package eu.jerrysamek.tickspace.model.substrate;

import java.math.BigInteger;
import java.util.Arrays;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

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

  private final BigInteger[] components;
  private final int dimensions;

  // Private constructor - use factory methods
  private Vector(BigInteger[] components) {
    this.components = components.clone(); // Defensive copy for immutability
    this.dimensions = components.length;
  }

  /**
   * Factory: Creates a zero vector of specified dimensions.
   */
  public static Vector zero(int dimensions) {
    var components = new BigInteger[dimensions];
    Arrays.fill(components, ZERO);
    return new Vector(components);
  }

  /**
   * Factory: Creates a vector from components.
   */
  public static Vector of(BigInteger... components) {
    if (components == null || components.length == 0) {
      throw new IllegalArgumentException("Vector must have at least one component");
    }
    return new Vector(components);
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
  public BigInteger get(int index) {
    return components[index];
  }

  /**
   * Returns a defensive copy of components array.
   * Use sparingly - prefer vector methods.
   */
  public BigInteger[] toArray() {
    return components.clone();
  }

  /**
   * Computes the dot product with another vector.
   */
  public BigInteger dot(Vector other) {
    var minLength = Math.min(dimensions, other.dimensions);
    var result = ZERO;
    for (var i = 0; i < minLength; i++) {
      result = result.add(components[i].multiply(other.components[i]));
    }
    return result;
  }

  /**
   * Computes the squared magnitude (more efficient than magnitude).
   */
  public BigInteger magnitudeSquared() {
    var result = ZERO;
    for (var component : components) {
      result = result.add(component.multiply(component));
    }
    return result;
  }

  /**
   * Computes the Euclidean magnitude.
   */
  public BigInteger magnitude() {
    return sqrt(magnitudeSquared());
  }

  /**
   * Adds another vector component-wise.
   */
  public Vector add(Vector other) {
    if (dimensions != other.dimensions) {
      throw new IllegalArgumentException("Vectors must have same dimensions: " + dimensions + " vs " + other.dimensions);
    }
    var result = new BigInteger[dimensions];
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
    var result = new BigInteger[dimensions];
    for (var i = 0; i < dimensions; i++) {
      result[i] = components[i].subtract(other.components[i]);
    }
    return new Vector(result);
  }

  /**
   * Multiplies by a scalar.
   */
  public Vector scale(BigInteger scalar) {
    var result = new BigInteger[dimensions];
    for (var i = 0; i < dimensions; i++) {
      result[i] = components[i].multiply(scalar);
    }
    return new Vector(result);
  }

  /**
   * Finds the maximum absolute component value.
   */
  public BigInteger maxComponent() {
    var max = ZERO;
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

    if (max.compareTo(ZERO) == 0) {
      return Vector.zero(dimensions);
    }

    var result = new BigInteger[dimensions];
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
      if (!component.equals(ZERO)) {
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
  public BigInteger sumComponents() {
    var sum = ZERO;
    for (var component : components) {
      sum = sum.add(component);
    }
    return sum;
  }

  /**
   * Integer square root (floor) - utility method.
   */
  private static BigInteger sqrt(BigInteger x) {
    if (x.compareTo(ZERO) < 0) {
      throw new IllegalArgumentException("Cannot take square root of negative number: " + x);
    }
    if (x.equals(ZERO) || x.equals(ONE)) {
      return x;
    }

    var r = ZERO;
    var bit = ONE.shiftLeft(x.bitLength() / 2 + 1);

    while (bit.compareTo(ZERO) > 0) {
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
    return Arrays.hashCode(components);
  }

  @Override
  public String toString() {
    return "Vector" + Arrays.toString(components);
  }
}
