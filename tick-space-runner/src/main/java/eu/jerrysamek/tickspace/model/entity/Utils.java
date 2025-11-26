package eu.jerrysamek.tickspace.model.entity;

import java.math.BigInteger;
import java.util.Arrays;

public class Utils {

  // Compute energy cost for child move relative to parent momentum
  public static BigInteger computeEnergyCost(BigInteger[] parentMomentum,
                                             BigInteger[] childOffset,
                                             BigInteger momentumCost,
                                             BigInteger depth) {
    // --- Base spatial norm (your current logic) ---
    BigInteger normSquared = Arrays.stream(childOffset)
        .map(c -> c.multiply(momentumCost).pow(2))
        .reduce(BigInteger.ZERO, BigInteger::add);

    BigInteger baseNorm = sqrt(normSquared);

    // --- Directional change penalty ---
    BigInteger rotationPenalty = directionalPenalty(parentMomentum, childOffset, depth);

    // --- Final cost ---
    return baseNorm.add(rotationPenalty);
  }

  // Penalty based on an angle between parent momentum and child offset
  private static BigInteger directionalPenalty(BigInteger[] parent, BigInteger[] child, BigInteger depth) {
    // Dot product
    BigInteger dot = BigInteger.ZERO;
    for (int i = 0; i < parent.length; i++) {
      dot = dot.add(parent[i].multiply(child[i]));
    }

    // Magnitudes
    BigInteger parentNormSq = Arrays.stream(parent).map(c -> c.pow(2)).reduce(BigInteger.ZERO, BigInteger::add);
    BigInteger childNormSq = Arrays.stream(child).map(c -> c.pow(2)).reduce(BigInteger.ZERO, BigInteger::add);

    BigInteger parentNorm = sqrt(parentNormSq);
    BigInteger childNorm = sqrt(childNormSq);

    // Cosine similarity scaled to integer domain
    // cosθ ≈ dot / (|p||c|)
    BigInteger denom = parentNorm.multiply(childNorm);
    int angleCategory;
    if (denom.equals(BigInteger.ZERO)) {
      angleCategory = 0; // no penalty if parent momentum is zero
    } else {
      // Compare dot to denom fractions to classify angle
      int cmp = dot.compareTo(denom); // dot vs |p||c|
      if (cmp >= 0) {
        angleCategory = 0; // same direction
      } else if (dot.signum() < 0) {
        angleCategory = 3; // reversal
      } else {
        angleCategory = 1; // small/medium turn
      }
    }

    // Depth scaling: older lineages pay more to rotate
    return BigInteger.valueOf(angleCategory).multiply(depth);
  }

  // Integer-safe sqrt (floor)
  private static BigInteger sqrt(BigInteger x) {
    BigInteger r = BigInteger.ZERO;
    BigInteger bit = BigInteger.ONE.shiftLeft(x.bitLength() / 2 + 1);
    while (bit.compareTo(BigInteger.ZERO) > 0) {
      BigInteger t = r.add(bit);
      if (t.multiply(t).compareTo(x) <= 0) {
        r = t;
      }
      bit = bit.shiftRight(1);
    }
    return r;
  }
}
