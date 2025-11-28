package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer.TickAction;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer.TickActionType;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class SingleEntityModelTest {

  private SubstrateModel testSubstrateModel;
  private UUID testIdentity;
  private Position testPosition;

  @BeforeEach
  void setUp() {
    // Create a real SubstrateModel with 2D space for testing
    EntitiesRegistry registry = new EntitiesRegistry();
    testSubstrateModel = new SubstrateModel(2, registry);

    testIdentity = UUID.randomUUID();
    testPosition = new Position(Vector.of(BigInteger.ZERO, BigInteger.ZERO));
  }

  @Test
  @DisplayName("onTick should return WAIT action when energy is not divisible by momentum cost")
  void testOnTick_WaitWhenEnergyNotDivisible() {
    // Given: entity with energy=5, momentum cost=3
    // After increase: energy=6, which is divisible by 3
    // So we need energy=4 to get 5 after increase (5 % 3 = 2, not divisible)
    BigInteger initialEnergy = BigInteger.valueOf(4);
    BigInteger momentumCost = BigInteger.valueOf(3);
    Momentum momentum = new Momentum(momentumCost, Vector.of(BigInteger.ONE, BigInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        BigInteger.ZERO,
        momentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.WAIT, actions.getFirst().type());
  }

  @Test
  @DisplayName("onTick should return UPDATE action with movement when energy is divisible by momentum cost")
  void testOnTick_UpdateWithMovementWhenEnergyDivisible() {
    // Given: entity with energy that will be divisible after increase
    // Energy = 2, cost = 3, after increase = 3 (divisible by 3)
    BigInteger initialEnergy = BigInteger.valueOf(2);
    BigInteger momentumCost = BigInteger.valueOf(3);
    Vector momentumVector = Vector.of(BigInteger.ONE, BigInteger.ZERO);
    Momentum momentum = new Momentum(momentumCost, momentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        BigInteger.ZERO,
        momentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.UPDATE, actions.getFirst().type());

    // Execute the update action and verify the entity moved
    List<EntityModel> updatedEntities = actions.getFirst().action().update(testSubstrateModel).toList();
    assertEquals(1, updatedEntities.size());

    EntityModel updatedEntity = updatedEntities.getFirst();
    assertEquals(testIdentity, updatedEntity.getIdentity());
    assertEquals(BigInteger.valueOf(3), updatedEntity.getEnergy().value());

    // Verify position was updated by momentum vector
    Position expectedPosition = testPosition.offset(momentumVector);
    assertEquals(expectedPosition, updatedEntity.getPosition());
  }

  @Test
  @DisplayName("onTick should return UPDATE action with division when energy exceeds threshold")
  void testOnTick_UpdateWithDivisionWhenEnergyExceedsThreshold() {
    // Given: entity with very high energy that exceeds the division threshold
    // We need to calculate what the division threshold would be
    // a Division threshold = sum of all child energy thresholds
    // For simplicity, let's use a high energy value
    BigInteger initialEnergy = BigInteger.valueOf(1000);
    BigInteger momentumCost = BigInteger.ONE;
    Vector momentumVector = Vector.of(BigInteger.ONE, BigInteger.ZERO);
    Momentum momentum = new Momentum(momentumCost, momentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        BigInteger.ZERO,
        momentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.UPDATE, actions.getFirst().type());

    // Execute the update action
    List<EntityModel> updatedEntities = actions.getFirst().action().update(testSubstrateModel).toList();

    // Should create 8 child entities (for 2D space with 8 neighbors)
    assertEquals(8, updatedEntities.size());

    // Verify all children have different identities (not the parent's)
    updatedEntities.forEach(child -> {
      assertNotEquals(testIdentity, child.getIdentity());
      assertEquals(BigInteger.ONE, child.getGeneration()); // generation + 1
      assertEquals(BigInteger.ONE, child.getEnergy().value());
    });
  }

  @Test
  @DisplayName("onTick should maintain entity state when energy stays below movement threshold")
  void testOnTick_MaintainStateWhenBelowThreshold() {
    // Given: entity with energy=0, cost=2
    // After increase: energy=1, which is not divisible by 2
    BigInteger initialEnergy = BigInteger.ZERO;
    BigInteger momentumCost = BigInteger.valueOf(2);
    Momentum momentum = new Momentum(momentumCost, Vector.of(BigInteger.ONE, BigInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        BigInteger.ZERO,
        momentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.WAIT, actions.getFirst().type());
  }

  @Test
  @DisplayName("onTick should correctly update generation and momentum during division")
  void testOnTick_GenerationIncrementDuringDivision() {
    // Given: parent with generation=5, high energy, and momentum vector [1, 0]
    // Energy must be set so that (initialEnergy + 1) % momentumCost == 0
    BigInteger parentGeneration = BigInteger.valueOf(5);
    BigInteger parentMomentumCost = BigInteger.valueOf(15);
    BigInteger initialEnergy = BigInteger.valueOf(1004); // 1004 + 1 = 1005, which is divisible by 15
    Vector parentMomentumVector = Vector.of(BigInteger.ONE, BigInteger.ZERO);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        parentGeneration,
        parentMomentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: all children should have incremented generation
    children.forEach(child -> assertEquals(BigInteger.valueOf(6), child.getGeneration()));

    // Should create 8 child entities (for 2D space)
    assertEquals(8, children.size());

    // Find the leading entity (same direction as parent: [1, 0])
    EntityModel leadingChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(BigInteger.ONE) && vector.get(1).equals(BigInteger.ZERO);
        })
        .findFirst()
        .orElseThrow(() -> new AssertionError("Leading child not found"));

    // The leading entity's momentum cost should be lowest (the least directional change)
    BigInteger leadingCost = leadingChild.getMomentum().cost();

    // Verify that at least some other children have higher momentum costs
    // (due to directional penalty from Utils.computeEnergyCost)
    long childrenWithHigherCost = children.stream()
        .filter(child -> child.getMomentum().cost().compareTo(leadingCost) > 0)
        .count();

    assertTrue(childrenWithHigherCost > 0,
        "Expected some children to have higher momentum cost than leading entity");

    // Verify all children have valid momentum costs (positive values)
    children.forEach(child ->
        assertTrue(child.getMomentum().cost().compareTo(BigInteger.ZERO) > 0,
            "Child momentum cost must be positive")
    );

    // Verify that the opposite direction ([−1, 0]) has the highest cost due to reversal penalty
    EntityModel oppositeChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(BigInteger.valueOf(-1)) && vector.get(1).equals(BigInteger.ZERO);
        })
        .findFirst()
        .orElseThrow(() -> new AssertionError("Opposite direction child not found"));

    BigInteger oppositeCost = oppositeChild.getMomentum().cost();
    assertTrue(oppositeCost.compareTo(leadingCost) >= 0,
        "Opposite direction should have higher or equal cost than leading direction");
  }

  @Test
  @DisplayName("Entity should maintain identity across non-division updates")
  void testOnTick_IdentityPreservedDuringMovement() {
    // Given
    BigInteger initialEnergy = BigInteger.valueOf(2);
    BigInteger momentumCost = BigInteger.valueOf(3);
    Momentum momentum = new Momentum(momentumCost, Vector.of(BigInteger.ONE, BigInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        BigInteger.ZERO,
        momentum
    );

    // When
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> updatedEntities = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then
    assertEquals(1, updatedEntities.size());
    assertEquals(testIdentity, updatedEntities.getFirst().getIdentity());
  }
}
