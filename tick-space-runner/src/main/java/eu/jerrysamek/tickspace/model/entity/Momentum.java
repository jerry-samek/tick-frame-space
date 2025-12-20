package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

public value record Momentum(FlexInteger cost, Vector vector) {

  public FlexInteger totalCost() {
    // Use Vector operations for cleaner code
    return vector.scale(cost).sumComponents();
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
  public static Momentum merge(Momentum m1, Momentum m2, FlexInteger energy1, FlexInteger energy2) {
    var dimensions = m1.vector().dimensions();

    // Handle zero energy edge case
    if (energy1.equals(FlexInteger.ZERO) && energy2.equals(FlexInteger.ZERO)) {
      return new Momentum(FlexInteger.ONE, Vector.zero(dimensions)); // Default at-rest state
    }

    var totalEnergy = energy1.add(energy2);

    // Compute momentum for each entity: p = energy × (vector/cost)
    // Working in integer domain: p[i] × cost = energy × vector[i]
    // Cross-multiply to avoid division: p1×c2 + p2×c1

    // Use Vector operations instead of manual loops
    var momentum1Scaled = m1.vector().scale(energy1.multiply(m2.cost()));
    var momentum2Scaled = m2.vector().scale(energy2.multiply(m1.cost()));
    var totalMomentumVec = momentum1Scaled.add(momentum2Scaled);

    // Common denominator
    var costProduct = m1.cost().multiply(m2.cost());

    // Check for zero total momentum (annihilation or both at rest)
    if (totalMomentumVec.isZero()) {
      // Perfect annihilation or both at rest
      return new Momentum(FlexInteger.ZERO, Vector.zero(dimensions));
    }

    // Calculate magnitude of total momentum
    var momentumMagnitude = totalMomentumVec.magnitude();

    // Normalize direction vector to enforce the speed limit (max component = 1)
    var newVector = totalMomentumVec.normalizeMaxComponent();

    // Calculate a new cost (inverse of speed)
    // speed = |momentum| / (total_energy × cost_product)
    // cost = (total_energy × cost_product) / |momentum|
    var newCost = totalEnergy.multiply(costProduct).divide(momentumMagnitude);

    // Ensure minimum cost (speed limit)
    if (newCost.compareTo(FlexInteger.ONE) < 0) {
      newCost = FlexInteger.ONE;  // Maximum speed limit (speed of light analogue)
    }

    return new Momentum(newCost, newVector);
  }
}
