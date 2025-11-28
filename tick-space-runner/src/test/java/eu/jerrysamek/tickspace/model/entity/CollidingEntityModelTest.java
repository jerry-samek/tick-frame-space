package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CollidingEntityModelTest {

  private SubstrateModel substrateModel;
  private Position testPosition;

  @BeforeEach
  void setUp() {
    EntitiesRegistry registry = new EntitiesRegistry();
    substrateModel = new SubstrateModel(3, registry);
    testPosition = new Position(Vector.of(BigInteger.ZERO, BigInteger.ZERO, BigInteger.ZERO));
  }

  @Test
  @DisplayName("Naive collision of opposite momentums should result in low momentum (annihilation tendency)")
  void testNaiveCollision_OppositeMomentums() {
    // Given: two entities with opposite momentums
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(100),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(100),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.valueOf(-1), BigInteger.ZERO, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: should result in annihilation (null) or very low momentum
    if (result != null) {
      // If not annihilated, momentum should be close to zero
      assertTrue(result.getMomentum().totalCost().compareTo(BigInteger.valueOf(10)) < 0,
          "Opposite collision should result in very low momentum, got: " + result.getMomentum());
    }
  }

  @Test
  @DisplayName("Naive collision of same direction momentums should combine momentum")
  void testNaiveCollision_SameDirection() {
    // Given: two entities moving in same direction
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(100),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(100),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    // Debug: compute merged momentum manually
    var mergedMomentum = Momentum.merge(
        entity1.getMomentum(),
        entity2.getMomentum(),
        entity1.getEnergy().value(),
        entity2.getEnergy().value()
    );

    System.out.println("DEBUG: Same direction collision");
    System.out.println("  Entity1 energy: " + entity1.getEnergy().value());
    System.out.println("  Entity2 energy: " + entity2.getEnergy().value());
    System.out.println("  Total energy: " + entity1.getEnergy().merge(entity2.getEnergy()).value());
    System.out.println("  Merged momentum cost: " + mergedMomentum.cost());
    System.out.println("  Merged momentum vector: " + mergedMomentum.vector());
    System.out.println("  Merged totalCost(): " + mergedMomentum.totalCost());
    System.out.println("  Energy after depletion: " + entity1.getEnergy().merge(entity2.getEnergy()).value().subtract(mergedMomentum.totalCost()));

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: should preserve direction
    assertNotNull(result, "Same direction collision should not annihilate");
    assertEquals(BigInteger.ONE, result.getMomentum().vector().get(0),
        "Should maintain X direction");
    assertEquals(BigInteger.ZERO, result.getMomentum().vector().get(1),
        "Y should remain zero");
  }

  @Test
  @DisplayName("Naive collision should not create runaway low-cost momentum")
  void testNaiveCollision_NoRunawayMomentum() {
    // Given: two typical entities
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(500),
        BigInteger.ONE,
        new Momentum(BigInteger.valueOf(15), Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(300),
        BigInteger.ONE,
        new Momentum(BigInteger.valueOf(20), Vector.of(BigInteger.ZERO, BigInteger.ONE, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: resulting momentum cost should not be unreasonably low
    assertNotNull(result, "Perpendicular collision should create merged entity");

    BigInteger resultCost = result.getMomentum().cost();
    System.out.println("Merged momentum cost: " + resultCost);
    System.out.println("Merged momentum vector: " + result.getMomentum().vector());

    // Cost should be reasonable - not drop to 1 or 2 (which would be runaway speed)
    assertTrue(resultCost.compareTo(BigInteger.ONE) > 0,
        "Cost should be greater than 1");

    // For this scenario, cost shouldn't drop below parent costs significantly
    assertTrue(resultCost.compareTo(BigInteger.valueOf(5)) >= 0,
        "Cost should not drop too low (runaway check), got: " + resultCost);
  }

  @Test
  @DisplayName("Naive collision should deplete energy appropriately")
  void testNaiveCollision_EnergyDepletion() {
    // Given: two entities with known energies
    BigInteger energy1 = BigInteger.valueOf(1000);
    BigInteger energy2 = BigInteger.valueOf(500);

    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        energy1,
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        energy2,
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ONE, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: energy should be less than sum (due to totalCost depletion)
    assertNotNull(result, "Should create merged entity");
    BigInteger totalInputEnergy = energy1.add(energy2);
    BigInteger resultEnergy = result.getEnergy().value();

    System.out.println("Input energy: " + totalInputEnergy);
    System.out.println("Result energy: " + resultEnergy);
    System.out.println("Energy lost: " + totalInputEnergy.subtract(resultEnergy));

    assertTrue(resultEnergy.compareTo(totalInputEnergy) < 0,
        "Collision should deplete some energy");
    assertTrue(resultEnergy.compareTo(BigInteger.ZERO) > 0,
        "Should have positive energy remaining");
  }

  @Test
  @DisplayName("Naive collision with very different energies should weight toward heavier entity")
  void testNaiveCollision_EnergyWeighting() {
    // Given: heavy entity vs light entity, perpendicular directions
    var heavy = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(9000),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var light = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(1000),
        BigInteger.ONE,
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ZERO, BigInteger.ONE, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, heavy, light);

    // Then: direction should be biased toward heavy entity
    assertNotNull(result, "Should create merged entity");
    BigInteger xComponent = result.getMomentum().vector().get(0).abs();
    BigInteger yComponent = result.getMomentum().vector().get(1).abs();

    System.out.println("Heavy entity direction: X=" + xComponent + ", Y=" + yComponent);

    assertTrue(xComponent.compareTo(yComponent) > 0,
        "X component should dominate due to heavy entity mass");
  }

  @Test
  @DisplayName("Collision should not decrease cost below parent costs (speed limit enforcement)")
  void testNaiveCollision_CostShouldNotDecrease() {
    // Given: two entities with moderate cost moving in same direction
    BigInteger parentCost = BigInteger.valueOf(15);
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(1000),
        BigInteger.ONE,
        new Momentum(parentCost, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(1000),
        BigInteger.ONE,
        new Momentum(parentCost, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: cost should not drop significantly below parent costs
    assertNotNull(result, "Should create merged entity");
    BigInteger resultCost = result.getMomentum().cost();

    System.out.println("Parent cost: " + parentCost);
    System.out.println("Result cost: " + resultCost);
    System.out.println("Cost ratio: " + resultCost.multiply(BigInteger.valueOf(100)).divide(parentCost) + "%");

    // Cost should not drop to speed-of-light (1) from collision
    assertTrue(resultCost.compareTo(BigInteger.valueOf(5)) >= 0,
        "Collision should not create runaway speed, cost dropped from " + parentCost + " to " + resultCost);
  }

  @Test
  @DisplayName("Naive collision should increment generation")
  void testNaiveCollision_GenerationIncrement() {
    // Given: two entities with different generations
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(500),
        BigInteger.valueOf(5),
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        testPosition,
        BigInteger.valueOf(500),
        BigInteger.valueOf(3),
        new Momentum(BigInteger.TEN, Vector.of(BigInteger.ZERO, BigInteger.ONE, BigInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(substrateModel, entity1, entity2);

    // Then: generation should be max + 1
    assertNotNull(result, "Should create merged entity");
    assertEquals(BigInteger.valueOf(6), result.getGeneration(),
        "Generation should be max(5,3) + 1 = 6");
  }
}
