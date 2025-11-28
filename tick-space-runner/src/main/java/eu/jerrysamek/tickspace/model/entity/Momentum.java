package eu.jerrysamek.tickspace.model.entity;

import java.math.BigInteger;
import java.util.Arrays;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public record Momentum(BigInteger cost, BigInteger[] vector) {

  public BigInteger totalCost() {
    // Optimized to avoid Stream overhead
    BigInteger total = ZERO;
    for (BigInteger component : vector) {
      total = total.add(component.multiply(cost));
    }
    return total;
  }

  /**
   * Merges two momentums using conservation of momentum in center-of-mass frame.
   * Uses conservation of momentum: p = energy × velocity
   * where velocity = vector / cost
   *
   * @param m1      First momentum
   * @param m2      Second momentum
   * @param energy1 First entity's energy (acts as "mass")
   * @param energy2 Second entity's energy (acts as "mass")
   * @return Combined momentum
   */
  public static Momentum merge(Momentum m1, Momentum m2, BigInteger energy1, BigInteger energy2) {
    int dimensions = m1.vector().length;

    // Handle zero energy edge case
    if (energy1.equals(ZERO) && energy2.equals(ZERO)) {
      BigInteger[] zeroVector = new BigInteger[dimensions];
      Arrays.fill(zeroVector, ZERO);
      return new Momentum(ONE, zeroVector); // Default at-rest state
    }

    BigInteger totalEnergy = energy1.add(energy2);

    // Compute momentum for each entity: p = energy × (vector/cost)
    // Working in integer domain: p[i] × cost = energy × vector[i]
    BigInteger[] totalMomentum = new BigInteger[dimensions];

    for (int i = 0; i < dimensions; i++) {
      // Momentum = energy × velocity = energy × (vector / cost)
      // Cross-multiply to avoid division: p1×c2 + p2×c1
      BigInteger momentum1 = m1.vector()[i].multiply(energy1);
      BigInteger momentum2 = m2.vector()[i].multiply(energy2);

      totalMomentum[i] = momentum1.multiply(m2.cost())
          .add(momentum2.multiply(m1.cost()));
    }

    // Common denominator
    BigInteger costProduct = m1.cost().multiply(m2.cost());

    // Check for zero total momentum (annihilation or both at rest)
    boolean isZeroMomentum = true;
    for (BigInteger p : totalMomentum) {
      if (!p.equals(ZERO)) {
        isZeroMomentum = false;
        break;
      }
    }

    if (isZeroMomentum) {
      // Perfect annihilation or both at rest
      BigInteger[] zeroVector = new BigInteger[dimensions];
      Arrays.fill(zeroVector, ZERO);
      return new Momentum(ZERO, zeroVector);
    }

    // Calculate magnitude of total momentum
    BigInteger momentumMagnitudeSq = ZERO;
    for (BigInteger p : totalMomentum) {
      momentumMagnitudeSq = momentumMagnitudeSq.add(p.pow(2));
    }

    BigInteger momentumMagnitude = momentumMagnitudeSq.sqrt();

    // Normalize direction vector to enforce speed limit
    // Find maximum component magnitude to normalize to unit speed
    BigInteger maxComponent = ZERO;
    for (BigInteger p : totalMomentum) {
      BigInteger abs = p.abs();
      if (abs.compareTo(maxComponent) > 0) {
        maxComponent = abs;
      }
    }

    BigInteger[] newVector = new BigInteger[dimensions];
    if (maxComponent.compareTo(ZERO) > 0) {
      // Normalize so max component = 1 (enforces speed-of-light limit)
      for (int i = 0; i < dimensions; i++) {
        newVector[i] = totalMomentum[i].divide(maxComponent);
      }
    } else {
      // All components are zero (shouldn't happen due to earlier check)
      Arrays.fill(newVector, ZERO);
    }

    // Calculate a new cost (inverse of speed)
    // speed = |momentum| / (total_energy × cost_product)
    // cost = (total_energy × cost_product) / |momentum|
    BigInteger newCost = totalEnergy.multiply(costProduct).divide(momentumMagnitude);

    // Ensure minimum cost (speed limit)
    if (newCost.compareTo(ONE) < 0) {
      newCost = ONE;  // Maximum speed limit (speed of light analogue)
    }

    return new Momentum(newCost, newVector);
  }
}
