package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

class CollidingEntityModelTest {

  private SubstrateModel substrateModel;
  private Position testPosition;

  @BeforeEach
  void setUp() {
    EntitiesRegistryLegacy registry = new EntitiesRegistryLegacy();
    substrateModel = new SubstrateModel(3, registry);
    testPosition = new Position(Vector.of(FlexInteger.ZERO, FlexInteger.ZERO, FlexInteger.ZERO));
  }

  @Test
  @DisplayName("Naive collision of opposite momentums should result in low momentum (annihilation tendency)")
  void testNaiveCollision_OppositeMomentums() {
    // Given: two entities with opposite momentums
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.ONE,
        testPosition,
        FlexInteger.of(100),
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.TEN,
        testPosition,
        FlexInteger.of(100),
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.of(-1), FlexInteger.ZERO, FlexInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(FlexInteger.of(100), substrateModel, entity1, entity2);

    // Then: should result in annihilation (null) or very low momentum
    if (result != null) {
      // If not annihilated, momentum should be close to zero
      assertTrue(result.getMomentum().totalCost().compareTo(FlexInteger.of(10)) < 0,
          "Opposite collision should result in very low momentum, got: " + result.getMomentum());
    }
  }

  @Test
  @DisplayName("Naive collision of same direction momentums should combine momentum")
  void testNaiveCollision_SameDirection() {
    // Given: two entities moving in the same direction
    var tick = FlexInteger.ONE;
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        tick,
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        tick,
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    // Debug: compute merged momentum manually
    var mergedMomentum = Momentum.merge(
        entity1.getMomentum(),
        entity2.getMomentum(),
        entity1.getEnergy(FlexInteger.ONE),
        entity2.getEnergy(FlexInteger.ONE)
    );

    System.out.println("DEBUG: Same direction collision");
    System.out.println("  Entity1 energy: " + entity1.getEnergy(tick));
    System.out.println("  Entity2 energy: " + entity2.getEnergy(tick));
    System.out.println("  Total energy: " + entity1.getEnergy(tick).add(entity2.getEnergy(tick)));
    System.out.println("  Merged momentum cost: " + mergedMomentum.cost());
    System.out.println("  Merged momentum vector: " + mergedMomentum.vector());
    System.out.println("  Merged totalCost(): " + mergedMomentum.totalCost());
    System.out.println("  Energy after depletion: " + entity1.getEnergy(tick).add(entity2.getEnergy(tick)).subtract(mergedMomentum.totalCost()));

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(FlexInteger.of(100), substrateModel, entity1, entity2);

    // Then: should preserve a direction
    assertNotNull(result, "Same direction collision should not annihilate");
    assertEquals(FlexInteger.ONE, result.getMomentum().vector().get(0),
        "Should maintain X direction");
    assertEquals(FlexInteger.ZERO, result.getMomentum().vector().get(1),
        "Y should remain zero");
  }

  @Test
  @DisplayName("Naive collision should not create runaway low-cost momentum")
  void testNaiveCollision_NoRunawayMomentum() {
    // Given: two typical entities
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(300),
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.of(15), Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(500),
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.of(20), Vector.of(FlexInteger.ZERO, FlexInteger.ONE, FlexInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(FlexInteger.of(500), substrateModel, entity1, entity2);

    // Then: resulting momentum cost should not be unreasonably low
    assertNotNull(result, "Perpendicular collision should create merged entity");

    FlexInteger resultCost = result.getMomentum().cost();
    System.out.println("Merged momentum cost: " + resultCost);
    System.out.println("Merged momentum vector: " + result.getMomentum().vector());

    // Cost should be reasonable - not drop to 1 or 2 (which would be runaway speed)
    assertTrue(resultCost.compareTo(FlexInteger.ONE) > 0,
        "Cost should be greater than 1");

    // For this scenario, cost shouldn't drop below parent costs significantly
    assertTrue(resultCost.compareTo(FlexInteger.of(5)) >= 0,
        "Cost should not drop too low (runaway check), got: " + resultCost);
  }

  @Test
  @DisplayName("Naive collision should deplete energy appropriately")
  void testNaiveCollision_EnergyDepletion() {
    // Given: two entities with known energies at collision tick
    var collisionTick = FlexInteger.of(1500);
    var birthTick1 = FlexInteger.of(500);
    var birthTick2 = FlexInteger.of(1000);

    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        birthTick1,
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        birthTick2,
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ONE, FlexInteger.ZERO))
    );

    FlexInteger energy1 = entity1.getEnergy(collisionTick);  // 1500 - 500 = 1000
    FlexInteger energy2 = entity2.getEnergy(collisionTick);  // 1500 - 1000 = 500

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(collisionTick, substrateModel, entity1, entity2);

    // Then: energy should be less than sum (due to totalCost depletion)
    assertNotNull(result, "Should create merged entity");
    FlexInteger totalInputEnergy = energy1.add(energy2);
    FlexInteger resultEnergy = result.getEnergy(collisionTick);

    System.out.println("Input energy: " + totalInputEnergy);
    System.out.println("Result energy: " + resultEnergy);
    System.out.println("Energy lost: " + totalInputEnergy.subtract(resultEnergy));

    assertTrue(resultEnergy.compareTo(totalInputEnergy) < 0,
        "Collision should deplete some energy");
    assertTrue(resultEnergy.compareTo(FlexInteger.ZERO) > 0,
        "Should have positive energy remaining");
  }

  @Test
  @DisplayName("Naive collision with very different energies should weight toward heavier entity")
  void testNaiveCollision_EnergyWeighting() {
    // Given: heavy entity vs. light entity, perpendicular directions
    var collisionTick = FlexInteger.of(10000);

    var heavy = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(1000),  // Born at 1000, energy at 10000 = 9000
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var light = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(9000),  // Born at 9000, energy at 10000 = 1000
        testPosition,
        FlexInteger.ONE,
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ZERO, FlexInteger.ONE, FlexInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(collisionTick, substrateModel, heavy, light);

    // Then: direction should be biased toward heavy entity
    assertNotNull(result, "Should create merged entity");
    FlexInteger xComponent = result.getMomentum().vector().get(0).abs();
    FlexInteger yComponent = result.getMomentum().vector().get(1).abs();

    System.out.println("Heavy entity direction: X=" + xComponent + ", Y=" + yComponent);

    assertTrue(xComponent.compareTo(yComponent) > 0,
        "X component should dominate due to heavy entity mass");
  }

  @Test
  @DisplayName("Collision should not decrease cost below parent costs (speed limit enforcement)")
  void testNaiveCollision_CostShouldNotDecrease() {
    // Given: two entities with moderate cost moving in same direction
    var collisionTick = FlexInteger.of(2000);
    FlexInteger parentCost = FlexInteger.of(15);
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(1000),  // Energy at collision = 2000 - 1000 = 1000
        testPosition,
        FlexInteger.ONE,
        new Momentum(parentCost, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(1000),  // Energy at collision = 2000 - 1000 = 1000
        testPosition,
        FlexInteger.ONE,
        new Momentum(parentCost, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(collisionTick, substrateModel, entity1, entity2);

    // Then: cost should not drop significantly below parent costs
    assertNotNull(result, "Should create merged entity");
    FlexInteger resultCost = result.getMomentum().cost();

    System.out.println("Parent cost: " + parentCost);
    System.out.println("Result cost: " + resultCost);
    System.out.println("Cost ratio: " + resultCost.multiply(FlexInteger.of(100)).divide(parentCost) + "%");

    // Cost should not drop to speed-of-light (1) from collision
    assertTrue(resultCost.compareTo(FlexInteger.of(5)) >= 0,
        "Collision should not create runaway speed, cost dropped from " + parentCost + " to " + resultCost);
  }

  @Test
  @DisplayName("Naive collision should increment generation")
  void testNaiveCollision_GenerationIncrement() {
    // Given: two entities with different generations
    var collisionTick = FlexInteger.of(1000);
    var entity1 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(500),  // Energy at collision = 1000 - 500 = 500
        testPosition,
        FlexInteger.of(5),
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO))
    );

    var entity2 = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(500),  // Energy at collision = 1000 - 500 = 500
        testPosition,
        FlexInteger.of(3),
        new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ZERO, FlexInteger.ONE, FlexInteger.ZERO))
    );

    // When: naive collision
    EntityModel result = CollidingEntityModel.naive(collisionTick, substrateModel, entity1, entity2);

    // Then: generation should be max + 1
    assertNotNull(result, "Should create merged entity");
    assertEquals(FlexInteger.of(6), result.getGeneration(),
        "Generation should be max(5,3) + 1 = 6");
  }
}
