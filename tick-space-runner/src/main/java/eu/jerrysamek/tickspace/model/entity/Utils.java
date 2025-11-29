package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Vector;

import java.math.BigInteger;

public class Utils {
  private Utils() {
  }

  // Compute energy cost for child move relative to parent momentum
  public static BigInteger computeEnergyCost(
      Vector parentMomentum,
      Vector childOffset,
      BigInteger momentumCost,
      BigInteger depth) {
    // --- Base spatial norm ---
    var scaledOffset = childOffset.scale(momentumCost);
    var baseNorm = scaledOffset.magnitude();

    // --- Directional change penalty ---
    var rotationPenalty = directionalPenalty(parentMomentum, childOffset, depth);

    // --- Final cost ---
    return baseNorm.add(rotationPenalty);
  }

  /**
   * Optimized version that uses precomputed offset magnitude.
   * Avoids expensive magnitude calculation by using cached value.
   *
   * @param parentMomentum     Parent entity's momentum vector
   * @param childOffset        Child offset direction
   * @param childOffsetMagnitude Precomputed magnitude of childOffset (cached)
   * @param momentumCost       Parent momentum cost
   * @param depth              Entity generation (depth in lineage tree)
   * @return Energy cost for this child direction
   */
  public static BigInteger computeEnergyCostOptimized(
      Vector parentMomentum,
      Vector childOffset,
      BigInteger childOffsetMagnitude,
      BigInteger momentumCost,
      BigInteger depth) {
    // --- Base spatial norm (optimized: use cached magnitude) ---
    // baseNorm = |childOffset × momentumCost| = |childOffset| × momentumCost
    var baseNorm = childOffsetMagnitude.multiply(momentumCost);

    // --- Directional change penalty ---
    var rotationPenalty = directionalPenalty(parentMomentum, childOffset, depth);

    // --- Final cost ---
    return baseNorm.add(rotationPenalty);
  }

  // Penalty based on an angle between parent momentum and child offset
  private static BigInteger directionalPenalty(Vector parent, Vector child, BigInteger depth) {
    // Dot product and magnitudes
    var dot = parent.dot(child);
    var parentNorm = parent.magnitude();
    var childNorm = child.magnitude();

    // Cosine similarity scaled to integer domain
    // cosθ ≈ dot / (|p||c|)
    var denom = parentNorm.multiply(childNorm);
    int angleCategory;
    if (denom.equals(BigInteger.ZERO)) {
      angleCategory = 0; // no penalty if parent momentum is zero
    } else {
      // Compare dot to denom fractions to classify angle
      var cmp = dot.compareTo(denom); // dot vs |p||c|
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
}
