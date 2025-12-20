package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer.TickAction;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer.TickActionType;
import eu.jerrysamek.tickspace.model.util.FlexInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

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
    EntitiesRegistryLegacy registry = new EntitiesRegistryLegacy();
    testSubstrateModel = new SubstrateModel(2, registry);

    testIdentity = UUID.randomUUID();
    testPosition = new Position(Vector.of(FlexInteger.ZERO, FlexInteger.ZERO));
  }

  @Test
  @DisplayName("onTick should return WAIT action when current tick is before nextPossibleAction")
  void testOnTick_WaitWhenEnergyNotDivisible() {
    // Given: entity born at tick 1, momentum cost=3
    // nextPossibleAction = 1 + 3 = 4
    // So at tick 1, 2, 3 the entity should WAIT
    FlexInteger startOfLife = FlexInteger.ONE;
    FlexInteger momentumCost = FlexInteger.of(3);
    Momentum momentum = new Momentum(momentumCost, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        FlexInteger.ZERO,  // initialEnergy doesn't affect timing
        momentum
    );

    // When: check at tick 2 (before nextPossibleAction=4)
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(FlexInteger.of(2)).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.WAIT, actions.getFirst().type());
  }

  @Test
  @DisplayName("onTick should return UPDATE action with movement when tick reaches nextPossibleAction")
  void testOnTick_UpdateWithMovementWhenEnergyDivisible() {
    // Given: entity born at tick 1, momentum cost=3
    // nextPossibleAction = 1 + 3 = 4
    // At tick 4, entity should move
    FlexInteger startOfLife = FlexInteger.ONE;
    FlexInteger momentumCost = FlexInteger.of(3);
    Vector momentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum momentum = new Momentum(momentumCost, momentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        FlexInteger.ZERO,
        momentum
    );

    // When: tick at nextPossibleAction time (tick 4)
    FlexInteger currentTick = FlexInteger.of(4);
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(currentTick).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.UPDATE, actions.getFirst().type());

    // Execute the update action and verify the entity moved
    List<EntityModel> updatedEntities = actions.getFirst().action().update(testSubstrateModel).toList();
    assertEquals(1, updatedEntities.size());

    EntityModel updatedEntity = updatedEntities.getFirst();
    assertEquals(testIdentity, updatedEntity.getIdentity());
    // Energy = tickCount - startOfLife = 4 - 1 = 3
    assertEquals(FlexInteger.of(3), updatedEntity.getEnergy(FlexInteger.of(4)));

    // Verify position was updated by momentum vector
    Position expectedPosition = testPosition.offset(momentumVector);
    assertEquals(expectedPosition, updatedEntity.getPosition());
  }

  @Test
  @DisplayName("onTick should return UPDATE action with division when tick reaches endOfLife")
  void testOnTick_UpdateWithDivisionWhenEnergyExceedsThreshold() {
    // Given: entity born at tick 1, momentum cost=1
    // endOfLife = startOfLife + completeDivisionThreshold
    // For 2D space with cost=1, completeDivisionThreshold is ~8-10 (depends on directional penalties)
    // Use tick 1000 to ensure we're past endOfLife
    FlexInteger startOfLife = FlexInteger.ONE;
    FlexInteger momentumCost = FlexInteger.ONE;
    Vector momentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum momentum = new Momentum(momentumCost, momentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        FlexInteger.ZERO,
        momentum
    );

    // When: tick far past endOfLife
    FlexInteger currentTick = FlexInteger.of(1000);
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(currentTick).toList();

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
      assertEquals(FlexInteger.ONE, child.getGeneration()); // generation 0 + 1 = 1
      // Children were born at currentTick, so energy at currentTick = currentTick - currentTick = 0
      assertEquals(FlexInteger.ZERO, child.getEnergy(currentTick));
      // Energy at the next tick should be 1
      assertEquals(FlexInteger.ONE, child.getEnergy(currentTick.add(FlexInteger.ONE)));
    });
  }

  @Test
  @DisplayName("onTick should maintain entity state when tick is before nextPossibleAction")
  void testOnTick_MaintainStateWhenBelowThreshold() {
    // Given: entity born at tick 1, cost=2
    // nextPossibleAction = 1 + 2 = 3
    // At tick 1, entity should WAIT
    FlexInteger startOfLife = FlexInteger.ONE;
    FlexInteger momentumCost = FlexInteger.of(2);
    Momentum momentum = new Momentum(momentumCost, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        FlexInteger.ZERO,
        momentum
    );

    // When: tick before nextPossibleAction (tick 1 < 3)
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(FlexInteger.ONE).toList();

    // Then
    assertEquals(1, actions.size());
    assertEquals(TickActionType.WAIT, actions.getFirst().type());
  }

  @Test
  @DisplayName("onTick should correctly update generation and momentum during division")
  void testOnTick_GenerationIncrementDuringDivision() {
    // Given: parent with generation=5, and momentum vector [1, 0]
    // Use tick far past endOfLife to trigger division
    FlexInteger parentGeneration = FlexInteger.of(5);
    FlexInteger parentMomentumCost = FlexInteger.of(15);
    FlexInteger startOfLife = FlexInteger.ONE;
    Vector parentMomentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        parentGeneration,
        parentMomentum
    );

    // When: tick far past endOfLife to trigger division
    FlexInteger currentTick = FlexInteger.of(10000);
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(currentTick).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: all children should have incremented generation
    children.forEach(child -> assertEquals(FlexInteger.of(6), child.getGeneration()));

    // Should create 8 child entities (for 2D space)
    assertEquals(8, children.size());

    // Find the leading entity (same direction as parent: [1, 0])
    EntityModel leadingChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.ONE) && vector.get(1).equals(FlexInteger.ZERO);
        })
        .findFirst()
        .orElseThrow(() -> new AssertionError("Leading child not found"));

    // The leading entity's momentum cost should be lowest (the least directional change)
    FlexInteger leadingCost = leadingChild.getMomentum().cost();

    // Verify that at least some other children have higher momentum costs
    // (due to directional penalty from Utils.computeEnergyCost)
    long childrenWithHigherCost = children.stream()
        .filter(child -> child.getMomentum().cost().compareTo(leadingCost) > 0)
        .count();

    assertTrue(childrenWithHigherCost > 0,
        "Expected some children to have higher momentum cost than leading entity");

    // Verify all children have valid momentum costs (positive values)
    children.forEach(child ->
        assertTrue(child.getMomentum().cost().compareTo(FlexInteger.ZERO) > 0,
            "Child momentum cost must be positive")
    );

    // Verify that the opposite direction ([−1, 0]) has the highest cost due to reversal penalty
    EntityModel oppositeChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.of(-1)) && vector.get(1).equals(FlexInteger.ZERO);
        })
        .findFirst()
        .orElseThrow(() -> new AssertionError("Opposite direction child not found"));

    FlexInteger oppositeCost = oppositeChild.getMomentum().cost();
    assertTrue(oppositeCost.compareTo(leadingCost) >= 0,
        "Opposite direction should have higher or equal cost than leading direction");
  }

  @Test
  @DisplayName("Entity should maintain identity across non-division updates")
  void testOnTick_IdentityPreservedDuringMovement() {
    // Given: entity born at tick 1, cost=3
    // nextPossibleAction = 1 + 3 = 4
    // At tick 4, entity moves (but doesn't divide)
    FlexInteger startOfLife = FlexInteger.ONE;
    FlexInteger momentumCost = FlexInteger.of(3);
    Momentum momentum = new Momentum(momentumCost, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        startOfLife,
        testPosition,
        FlexInteger.ZERO,
        momentum
    );

    // When: tick at nextPossibleAction (move, not divide)
    FlexInteger currentTick = FlexInteger.of(4);
    List<TickAction<EntityModelUpdate>> actions = entity.onTick(currentTick).toList();
    List<EntityModel> updatedEntities = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then
    assertEquals(1, updatedEntities.size());
    assertEquals(testIdentity, updatedEntities.getFirst().getIdentity());
  }
}
