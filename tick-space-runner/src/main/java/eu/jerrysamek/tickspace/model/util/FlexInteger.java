package eu.jerrysamek.tickspace.model.util;

import java.math.BigInteger;

/**
 * FlexInteger: A memory-efficient integer wrapper that uses primitive long internally
 * and auto-promotes to BigInteger only when overflow occurs.
 * <p>
 * This class provides a drop-in replacement for BigInteger with significant performance
 * and memory advantages:
 * <ul>
 *   <li>Memory: 8 bytes (long) vs 32-48 bytes (BigInteger object)</li>
 *   <li>Performance: Native CPU arithmetic vs object allocation + GC</li>
 *   <li>Safety: Automatic overflow detection and promotion to BigInteger</li>
 * </ul>
 * <p>
 * Thread-safe: Immutable by design (all operations return new instances).
 * <p>
 * Usage:
 * <pre>
 * FlexInteger x = FlexInteger.of(100);
 * FlexInteger y = x.add(FlexInteger.ONE);
 * int cmp = y.compareTo(FlexInteger.ZERO);
 * </pre>
 *
 * @author tick-frame-space optimization
 */
public final class FlexInteger implements Comparable<FlexInteger> {

  // Constants - pre-allocated for common values
  public static final FlexInteger ZERO = new FlexInteger(0L, null, false);
  public static final FlexInteger ONE = new FlexInteger(1L, null, false);
  public static final FlexInteger TEN = new FlexInteger(10L, null, false);

  private final long longValue;
  private final BigInteger bigValue;
  private final boolean isBig;

  // Private constructor - use factory methods
  private FlexInteger(long longValue, BigInteger bigValue, boolean isBig) {
    this.longValue = longValue;
    this.bigValue = bigValue;
    this.isBig = isBig;
  }

  /**
   * Factory method: Creates a FlexInteger from a long value.
   *
   * @param value the long value
   * @return FlexInteger instance
   */
  public static FlexInteger of(long value) {
    // Return cached constants for common values
    if (value == 0L) {
      return ZERO;
    }
    if (value == 1L) {
      return ONE;
    }
    if (value == 10L){
      return TEN;
    }

    return new FlexInteger(value, null, false);
  }

  /**
   * Factory method: Creates a FlexInteger from a BigInteger value.
   * Uses long representation if the value fits, otherwise stores as BigInteger.
   *
   * @param value the BigInteger value
   * @return FlexInteger instance
   */
  public static FlexInteger of(BigInteger value) {
    if (value == null) {
      throw new IllegalArgumentException("BigInteger value cannot be null");
    }

    // Check if it fits in long range
    if (value.bitLength() < 63 || (value.bitLength() == 63 && value.signum() == -1)) {
      long longVal = value.longValue();
      // Verify no precision loss
      if (BigInteger.valueOf(longVal).equals(value)) {
        return of(longVal);
      }
    }

    // Value too large for long, store as BigInteger
    return new FlexInteger(0L, value, true);
  }

  /**
   * Factory method: Creates a FlexInteger from an int value.
   *
   * @param value the int value
   * @return FlexInteger instance
   */
  public static FlexInteger of(int value) {
    return of((long) value);
  }

  /**
   * Adds another FlexInteger to this one.
   * Auto-promotes to BigInteger on overflow.
   *
   * @param other the value to add
   * @return new FlexInteger with the sum
   */
  public FlexInteger add(FlexInteger other) {
    if (!isBig && !other.isBig) {
      try {
        return of(Math.addExact(longValue, other.longValue));
      } catch (ArithmeticException e) {
        // Overflow - promote to BigInteger
        return of(BigInteger.valueOf(longValue).add(BigInteger.valueOf(other.longValue)));
      }
    }
    // At least one is BigInteger
    return of(toBigInteger().add(other.toBigInteger()));
  }

  /**
   * Subtracts another FlexInteger from this one.
   * Auto-promotes to BigInteger on overflow.
   *
   * @param other the value to subtract
   * @return new FlexInteger with the difference
   */
  public FlexInteger subtract(FlexInteger other) {
    if (!isBig && !other.isBig) {
      try {
        return of(Math.subtractExact(longValue, other.longValue));
      } catch (ArithmeticException e) {
        // Overflow - promote to BigInteger
        return of(BigInteger.valueOf(longValue).subtract(BigInteger.valueOf(other.longValue)));
      }
    }
    return of(toBigInteger().subtract(other.toBigInteger()));
  }

  /**
   * Multiplies this FlexInteger by another.
   * Auto-promotes to BigInteger on overflow.
   *
   * @param other the value to multiply by
   * @return new FlexInteger with the product
   */
  public FlexInteger multiply(FlexInteger other) {
    if (!isBig && !other.isBig) {
      try {
        return of(Math.multiplyExact(longValue, other.longValue));
      } catch (ArithmeticException e) {
        // Overflow - promote to BigInteger
        return of(BigInteger.valueOf(longValue).multiply(BigInteger.valueOf(other.longValue)));
      }
    }
    return of(toBigInteger().multiply(other.toBigInteger()));
  }

  /**
   * Divides this FlexInteger by another.
   *
   * @param other the divisor
   * @return new FlexInteger with the quotient
   * @throws ArithmeticException if divisor is zero
   */
  public FlexInteger divide(FlexInteger other) {
    if (other.equals(ZERO)) {
      throw new ArithmeticException("Division by zero");
    }

    if (!isBig && !other.isBig) {
      return of(longValue / other.longValue);
    }
    return of(toBigInteger().divide(other.toBigInteger()));
  }

  /**
   * Returns the remainder of dividing this FlexInteger by another.
   *
   * @param other the divisor
   * @return new FlexInteger with the remainder
   * @throws ArithmeticException if divisor is zero
   */
  public FlexInteger remainder(FlexInteger other) {
    if (other.equals(ZERO)) {
      throw new ArithmeticException("Division by zero");
    }

    if (!isBig && !other.isBig) {
      return of(longValue % other.longValue);
    }
    return of(toBigInteger().remainder(other.toBigInteger()));
  }

  /**
   * Returns the negation of this FlexInteger.
   *
   * @return new FlexInteger with negated value
   */
  public FlexInteger negate() {
    if (!isBig) {
      if (longValue == Long.MIN_VALUE) {
        // Special case: -Long.MIN_VALUE overflows, promote to BigInteger
        return of(BigInteger.valueOf(longValue).negate());
      }
      return of(-longValue);
    }
    return of(bigValue.negate());
  }

  /**
   * Returns the absolute value of this FlexInteger.
   *
   * @return new FlexInteger with absolute value
   */
  public FlexInteger abs() {
    if (!isBig) {
      if (longValue == Long.MIN_VALUE) {
        // Special case: abs(Long.MIN_VALUE) overflows, promote to BigInteger
        return of(BigInteger.valueOf(longValue).abs());
      }
      return of(Math.abs(longValue));
    }
    return of(bigValue.abs());
  }

  /**
   * Returns the maximum of this FlexInteger and another.
   *
   * @param other the value to compare with
   * @return the larger of the two values
   */
  public FlexInteger max(FlexInteger other) {
    return compareTo(other) >= 0 ? this : other;
  }

  /**
   * Returns the minimum of this FlexInteger and another.
   *
   * @param other the value to compare with
   * @return the smaller of the two values
   */
  public FlexInteger min(FlexInteger other) {
    return compareTo(other) <= 0 ? this : other;
  }

  /**
   * Shifts this FlexInteger left by n bits.
   *
   * @param n number of bits to shift
   * @return new FlexInteger with shifted value
   */
  public FlexInteger shiftLeft(int n) {
    if (n < 0) {
      throw new IllegalArgumentException("Negative shift count: " + n);
    }

    if (!isBig && n < 63) {
      try {
        // Check if shift would overflow
        long result = longValue << n;
        // Verify no overflow occurred
        if ((result >> n) == longValue) {
          return of(result);
        }
      } catch (ArithmeticException e) {
        // Fall through to BigInteger
      }
    }

    return of(toBigInteger().shiftLeft(n));
  }

  /**
   * Shifts this FlexInteger right by n bits.
   *
   * @param n number of bits to shift
   * @return new FlexInteger with shifted value
   */
  public FlexInteger shiftRight(int n) {
    if (n < 0) {
      throw new IllegalArgumentException("Negative shift count: " + n);
    }

    if (!isBig) {
      return of(longValue >> n);
    }
    return of(bigValue.shiftRight(n));
  }

  /**
   * Returns the number of bits in the minimal two's-complement representation
   * of this FlexInteger, excluding a sign bit.
   *
   * @return number of bits in the representation
   */
  public int bitLength() {
    if (!isBig) {
      return 64 - Long.numberOfLeadingZeros(longValue < 0 ? ~longValue : longValue);
    }
    return bigValue.bitLength();
  }

  /**
   * Returns the signum function of this FlexInteger.
   *
   * @return -1, 0, or 1 as the value is negative, zero, or positive
   */
  public int signum() {
    if (!isBig) {
      return Long.signum(longValue);
    }
    return bigValue.signum();
  }

  /**
   * Converts this FlexInteger to a BigInteger.
   *
   * @return BigInteger representation
   */
  public BigInteger toBigInteger() {
    if (!isBig) {
      return BigInteger.valueOf(longValue);
    }
    return bigValue;
  }

  /**
   * Returns the value as a long.
   * May lose precision if the value doesn't fit in a long.
   *
   * @return long value
   */
  public long longValue() {
    if (!isBig) {
      return longValue;
    }
    return bigValue.longValue();
  }

  /**
   * Returns the value as an int.
   * May lose precision if the value doesn't fit in an int.
   *
   * @return int value
   */
  public int intValue() {
    return (int) longValue();
  }

  /**
   * Checks if this value is represented as a BigInteger internally.
   *
   * @return true if using BigInteger representation
   */
  public boolean isBigInteger() {
    return isBig;
  }

  @Override
  public int compareTo(FlexInteger other) {
    if (!isBig && !other.isBig) {
      return Long.compare(longValue, other.longValue);
    }
    return toBigInteger().compareTo(other.toBigInteger());
  }

  @Override
  public boolean equals(Object obj) {
    if (this == obj) return true;
    if (!(obj instanceof FlexInteger other)) return false;

    if (!isBig && !other.isBig) {
      return longValue == other.longValue;
    }
    return toBigInteger().equals(other.toBigInteger());
  }

  @Override
  public int hashCode() {
    if (!isBig) {
      return Long.hashCode(longValue);
    }
    return bigValue.hashCode();
  }

  @Override
  public String toString() {
    if (!isBig) {
      return Long.toString(longValue);
    }
    return bigValue.toString();
  }
}
