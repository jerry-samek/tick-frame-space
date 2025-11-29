package eu.jerrysamek.tickspace.model.util;

import org.junit.jupiter.api.Test;

import java.math.BigInteger;

import static org.junit.jupiter.api.Assertions.*;

class FlexIntegerTest {

  // === Factory Methods ===

  @Test
  void testOf_Long() {
    var x = FlexInteger.of(42L);
    assertEquals(42L, x.longValue());
    assertFalse(x.isBigInteger());
  }

  @Test
  void testOf_Int() {
    var x = FlexInteger.of(42);
    assertEquals(42, x.intValue());
    assertFalse(x.isBigInteger());
  }

  @Test
  void testOf_BigInteger_FitsInLong() {
    var big = BigInteger.valueOf(12345L);
    var x = FlexInteger.of(big);
    assertEquals(12345L, x.longValue());
    assertFalse(x.isBigInteger(), "Should use long representation when value fits");
  }

  @Test
  void testOf_BigInteger_TooLarge() {
    var big = new BigInteger("999999999999999999999999");
    var x = FlexInteger.of(big);
    assertEquals(big, x.toBigInteger());
    assertTrue(x.isBigInteger(), "Should use BigInteger for values that don't fit in long");
  }

  @Test
  void testOf_BigInteger_Null() {
    assertThrows(IllegalArgumentException.class, () -> FlexInteger.of((BigInteger) null));
  }

  // === Constants ===

  @Test
  void testConstants() {
    assertEquals(0L, FlexInteger.ZERO.longValue());
    assertEquals(1L, FlexInteger.ONE.longValue());
    assertEquals(10L, FlexInteger.TEN.longValue());
  }

  @Test
  void testConstants_CachedInstances() {
    assertSame(FlexInteger.ZERO, FlexInteger.of(0L));
    assertSame(FlexInteger.ONE, FlexInteger.of(1L));
    assertSame(FlexInteger.TEN, FlexInteger.of(10L));
  }

  // === Addition ===

  @Test
  void testAdd_NoOverflow() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(50L);
    var result = a.add(b);
    assertEquals(150L, result.longValue());
    assertFalse(result.isBigInteger());
  }

  @Test
  void testAdd_Overflow() {
    var a = FlexInteger.of(Long.MAX_VALUE);
    var b = FlexInteger.of(1L);
    var result = a.add(b);
    assertTrue(result.isBigInteger(), "Should promote to BigInteger on overflow");
    assertEquals(BigInteger.valueOf(Long.MAX_VALUE).add(BigInteger.ONE), result.toBigInteger());
  }

  @Test
  void testAdd_NegativeOverflow() {
    var a = FlexInteger.of(Long.MIN_VALUE);
    var b = FlexInteger.of(-1L);
    var result = a.add(b);
    assertTrue(result.isBigInteger(), "Should promote to BigInteger on negative overflow");
  }

  @Test
  void testAdd_MixedBigInteger() {
    var a = FlexInteger.of(new BigInteger("999999999999999999999999"));
    var b = FlexInteger.of(1L);
    var result = a.add(b);
    assertTrue(result.isBigInteger());
    assertEquals(new BigInteger("1000000000000000000000000"), result.toBigInteger());
  }

  // === Subtraction ===

  @Test
  void testSubtract_NoOverflow() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(30L);
    var result = a.subtract(b);
    assertEquals(70L, result.longValue());
    assertFalse(result.isBigInteger());
  }

  @Test
  void testSubtract_Overflow() {
    var a = FlexInteger.of(Long.MIN_VALUE);
    var b = FlexInteger.of(1L);
    var result = a.subtract(b);
    assertTrue(result.isBigInteger(), "Should promote to BigInteger on overflow");
  }

  @Test
  void testSubtract_NegativeResult() {
    var a = FlexInteger.of(50L);
    var b = FlexInteger.of(100L);
    var result = a.subtract(b);
    assertEquals(-50L, result.longValue());
    assertFalse(result.isBigInteger());
  }

  // === Multiplication ===

  @Test
  void testMultiply_NoOverflow() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(50L);
    var result = a.multiply(b);
    assertEquals(5000L, result.longValue());
    assertFalse(result.isBigInteger());
  }

  @Test
  void testMultiply_Overflow() {
    var a = FlexInteger.of(Long.MAX_VALUE);
    var b = FlexInteger.of(2L);
    var result = a.multiply(b);
    assertTrue(result.isBigInteger(), "Should promote to BigInteger on overflow");
    assertEquals(BigInteger.valueOf(Long.MAX_VALUE).multiply(BigInteger.TWO), result.toBigInteger());
  }

  @Test
  void testMultiply_ByZero() {
    var a = FlexInteger.of(123456L);
    var result = a.multiply(FlexInteger.ZERO);
    assertEquals(0L, result.longValue());
    assertSame(FlexInteger.ZERO, result);
  }

  // === Division ===

  @Test
  void testDivide_NoRemainder() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(5L);
    var result = a.divide(b);
    assertEquals(20L, result.longValue());
  }

  @Test
  void testDivide_WithRemainder() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(7L);
    var result = a.divide(b);
    assertEquals(14L, result.longValue());
  }

  @Test
  void testDivide_ByZero() {
    var a = FlexInteger.of(100L);
    assertThrows(ArithmeticException.class, () -> a.divide(FlexInteger.ZERO));
  }

  @Test
  void testDivide_BigInteger() {
    var a = FlexInteger.of(new BigInteger("1000000000000000000000000"));
    var b = FlexInteger.of(1000L);
    var result = a.divide(b);
    assertEquals(new BigInteger("1000000000000000000000"), result.toBigInteger());
  }

  // === Remainder ===

  @Test
  void testRemainder() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(7L);
    var result = a.remainder(b);
    assertEquals(2L, result.longValue());
  }

  @Test
  void testRemainder_NoRemainder() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(10L);
    var result = a.remainder(b);
    assertSame(FlexInteger.ZERO, result);
  }

  @Test
  void testRemainder_ByZero() {
    var a = FlexInteger.of(100L);
    assertThrows(ArithmeticException.class, () -> a.remainder(FlexInteger.ZERO));
  }

  // === Negate ===

  @Test
  void testNegate_Positive() {
    var a = FlexInteger.of(42L);
    var result = a.negate();
    assertEquals(-42L, result.longValue());
  }

  @Test
  void testNegate_Negative() {
    var a = FlexInteger.of(-42L);
    var result = a.negate();
    assertEquals(42L, result.longValue());
  }

  @Test
  void testNegate_Zero() {
    var result = FlexInteger.ZERO.negate();
    assertSame(FlexInteger.ZERO, result);
  }

  @Test
  void testNegate_MinValue() {
    var a = FlexInteger.of(Long.MIN_VALUE);
    var result = a.negate();
    assertTrue(result.isBigInteger(), "Negating Long.MIN_VALUE should overflow to BigInteger");
    assertEquals(BigInteger.valueOf(Long.MIN_VALUE).negate(), result.toBigInteger());
  }

  // === Absolute Value ===

  @Test
  void testAbs_Positive() {
    var a = FlexInteger.of(42L);
    var result = a.abs();
    assertEquals(42L, result.longValue());
  }

  @Test
  void testAbs_Negative() {
    var a = FlexInteger.of(-42L);
    var result = a.abs();
    assertEquals(42L, result.longValue());
  }

  @Test
  void testAbs_Zero() {
    var result = FlexInteger.ZERO.abs();
    assertSame(FlexInteger.ZERO, result);
  }

  @Test
  void testAbs_MinValue() {
    var a = FlexInteger.of(Long.MIN_VALUE);
    var result = a.abs();
    assertTrue(result.isBigInteger(), "abs(Long.MIN_VALUE) should overflow to BigInteger");
  }

  // === Max/Min ===

  @Test
  void testMax() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(200L);
    assertEquals(b, a.max(b));
    assertEquals(b, b.max(a));
  }

  @Test
  void testMin() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(200L);
    assertEquals(a, a.min(b));
    assertEquals(a, b.min(a));
  }

  // === Bit Operations ===

  @Test
  void testShiftLeft_NoOverflow() {
    var a = FlexInteger.of(1L);
    var result = a.shiftLeft(3);
    assertEquals(8L, result.longValue());
    assertFalse(result.isBigInteger());
  }

  @Test
  void testShiftLeft_Overflow() {
    var a = FlexInteger.of(Long.MAX_VALUE);
    var result = a.shiftLeft(1);
    assertTrue(result.isBigInteger(), "Large shift should promote to BigInteger");
  }

  @Test
  void testShiftLeft_Negative() {
    assertThrows(IllegalArgumentException.class, () -> FlexInteger.ONE.shiftLeft(-1));
  }

  @Test
  void testShiftRight() {
    var a = FlexInteger.of(16L);
    var result = a.shiftRight(2);
    assertEquals(4L, result.longValue());
  }

  @Test
  void testShiftRight_Negative() {
    assertThrows(IllegalArgumentException.class, () -> FlexInteger.ONE.shiftRight(-1));
  }

  @Test
  void testBitLength() {
    assertEquals(0, FlexInteger.ZERO.bitLength());
    assertEquals(1, FlexInteger.ONE.bitLength());
    assertEquals(7, FlexInteger.of(127L).bitLength());
    assertEquals(8, FlexInteger.of(128L).bitLength());
  }

  @Test
  void testSignum() {
    assertEquals(0, FlexInteger.ZERO.signum());
    assertEquals(1, FlexInteger.of(42L).signum());
    assertEquals(-1, FlexInteger.of(-42L).signum());
  }

  // === Comparison ===

  @Test
  void testCompareTo_Equal() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(100L);
    assertEquals(0, a.compareTo(b));
  }

  @Test
  void testCompareTo_Less() {
    var a = FlexInteger.of(50L);
    var b = FlexInteger.of(100L);
    assertTrue(a.compareTo(b) < 0);
  }

  @Test
  void testCompareTo_Greater() {
    var a = FlexInteger.of(200L);
    var b = FlexInteger.of(100L);
    assertTrue(a.compareTo(b) > 0);
  }

  @Test
  void testCompareTo_MixedBigInteger() {
    var a = FlexInteger.of(100L);
    var b = FlexInteger.of(new BigInteger("999999999999999999999999"));
    assertTrue(a.compareTo(b) < 0);
    assertTrue(b.compareTo(a) > 0);
  }

  // === Equality ===

  @Test
  void testEquals_Same() {
    var a = FlexInteger.of(42L);
    assertEquals(a, a);
  }

  @Test
  void testEquals_Equal() {
    var a = FlexInteger.of(42L);
    var b = FlexInteger.of(42L);
    assertEquals(a, b);
  }

  @Test
  void testEquals_NotEqual() {
    var a = FlexInteger.of(42L);
    var b = FlexInteger.of(43L);
    assertNotEquals(a, b);
  }

  @Test
  void testEquals_MixedBigInteger() {
    var a = FlexInteger.of(42L);
    var b = FlexInteger.of(BigInteger.valueOf(42L));
    assertEquals(a, b, "Should be equal regardless of internal representation");
  }

  @Test
  void testEquals_Null() {
    var a = FlexInteger.of(42L);
    assertNotEquals(null, a);
  }

  @Test
  void testEquals_DifferentType() {
    var a = FlexInteger.of(42L);
    assertNotEquals(a, "42");
  }

  // === Hash Code ===

  @Test
  void testHashCode_Consistent() {
    var a = FlexInteger.of(42L);
    var b = FlexInteger.of(42L);
    assertEquals(a.hashCode(), b.hashCode());
  }

  @Test
  void testHashCode_MixedRepresentation() {
    var a = FlexInteger.of(42L);
    var b = FlexInteger.of(BigInteger.valueOf(42L));
    assertEquals(a.hashCode(), b.hashCode(), "Hash codes should match for equal values");
  }

  // === Conversion ===

  @Test
  void testToBigInteger_Long() {
    var a = FlexInteger.of(42L);
    assertEquals(BigInteger.valueOf(42L), a.toBigInteger());
  }

  @Test
  void testToBigInteger_Big() {
    var big = new BigInteger("999999999999999999999999");
    var a = FlexInteger.of(big);
    assertEquals(big, a.toBigInteger());
  }

  @Test
  void testLongValue() {
    var a = FlexInteger.of(42L);
    assertEquals(42L, a.longValue());
  }

  @Test
  void testIntValue() {
    var a = FlexInteger.of(42L);
    assertEquals(42, a.intValue());
  }

  // === toString ===

  @Test
  void testToString_Long() {
    var a = FlexInteger.of(42L);
    assertEquals("42", a.toString());
  }

  @Test
  void testToString_Negative() {
    var a = FlexInteger.of(-42L);
    assertEquals("-42", a.toString());
  }

  @Test
  void testToString_BigInteger() {
    var big = new BigInteger("999999999999999999999999");
    var a = FlexInteger.of(big);
    assertEquals("999999999999999999999999", a.toString());
  }

  // === Complex Scenarios ===

  @Test
  void testChainedOperations() {
    var result = FlexInteger.of(10L)
        .add(FlexInteger.of(5L))
        .multiply(FlexInteger.of(2L))
        .subtract(FlexInteger.of(10L));
    assertEquals(20L, result.longValue());
  }

  @Test
  void testChainedOperations_WithOverflow() {
    var result = FlexInteger.of(Long.MAX_VALUE)
        .add(FlexInteger.ONE)
        .add(FlexInteger.ONE);
    assertTrue(result.isBigInteger());
  }

  @Test
  void testEnergyIncrement_Realistic() {
    // Simulate typical energy increment pattern
    var energy = FlexInteger.ZERO;
    for (int i = 0; i < 1000; i++) {
      energy = energy.add(FlexInteger.ONE);
    }
    assertEquals(1000L, energy.longValue());
    assertFalse(energy.isBigInteger(), "Typical energy values should stay in long range");
  }

  @Test
  void testMomentumCost_Realistic() {
    // Simulate typical momentum cost calculations
    var cost = FlexInteger.of(15L);
    var generation = FlexInteger.of(5L);
    var angleCategory = FlexInteger.of(2L);

    var result = cost.add(angleCategory.multiply(generation));
    assertEquals(25L, result.longValue());
    assertFalse(result.isBigInteger());
  }
}
