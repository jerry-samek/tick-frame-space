package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertTrue;

/**
 * Comprehensive tests for momentum cost calculations during entity division
 */
class MomentumTest {

  private SubstrateModel testSubstrateModel;
  private UUID testIdentity;
  private Position testPosition;

  @BeforeEach
  void setUp() {
    EntitiesRegistry registry = new EntitiesRegistry();
    testSubstrateModel = new SubstrateModel(2, registry);
    testIdentity = UUID.randomUUID();
    testPosition = new Position(Vector.of(FlexInteger.ZERO, FlexInteger.ZERO));
  }

  @Test
  @DisplayName("Momentum costs should be correctly calculated for all 8 children in 2D space")
  void testMomentumCostsFor2DSpace() {
    // Given: parent with generation=5, cost=15, vector=[1, 0]
    FlexInteger parentGeneration = FlexInteger.of(5);
    FlexInteger parentMomentumCost = FlexInteger.of(15);
    FlexInteger initialEnergy = FlexInteger.of(1004); // 1004 + 1 = 1005, divisible by 15
    Vector parentMomentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);
    var tick = FlexInteger.of(2000);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        tick.subtract(initialEnergy),
        testPosition,
        parentGeneration,
        parentMomentum
    );

    // When: entity divides (use large tick to ensure tickCount >= endOfLife)
    var actions = entity.onTick(FlexInteger.of(10000)).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: 8 children created
    assertEquals(8, children.size());

    // Map children by their momentum vectors for easy lookup
    Map<String, EntityModel> childrenByVector = children.stream()
        .collect(Collectors.toMap(
            child -> child.getMomentum().vector().toString(),
            child -> child
        ));

    // Leading direction [1, 0] - same as parent, should have lowest cost
    EntityModel leading = childrenByVector.get("Vector[1, 0]");
    assertNotNull(leading, "Leading child [1, 0] should exist");
    FlexInteger leadingCost = leading.getMomentum().cost();
    assertEquals(FlexInteger.of(30), leadingCost, "Leading cost should be parentCost + childCost = 15 + 15");

    // Opposite direction [-1, 0] - reversal, should have highest cost among axis-aligned
    EntityModel opposite = childrenByVector.get("Vector[-1, 0]");
    assertNotNull(opposite, "Opposite child [-1, 0] should exist");
    FlexInteger oppositeCost = opposite.getMomentum().cost();
    assertEquals(FlexInteger.of(45), oppositeCost, "Opposite cost should include reversal penalty");

    // Perpendicular directions [0, 1] and [0, -1] - medium turn penalty
    EntityModel perpUp = childrenByVector.get("Vector[0, 1]");
    EntityModel perpDown = childrenByVector.get("Vector[0, -1]");
    assertNotNull(perpUp, "Perpendicular child [0, 1] should exist");
    assertNotNull(perpDown, "Perpendicular child [0, -1] should exist");
    assertEquals(FlexInteger.of(35), perpUp.getMomentum().cost(), "Perpendicular up should have medium penalty");
    assertEquals(FlexInteger.of(35), perpDown.getMomentum().cost(), "Perpendicular down should have medium penalty");

    // Diagonal directions - higher base cost due to distance
    EntityModel diagForwardUp = childrenByVector.get("Vector[1, 1]");
    EntityModel diagForwardDown = childrenByVector.get("Vector[1, -1]");
    EntityModel diagBackUp = childrenByVector.get("Vector[-1, 1]");
    EntityModel diagBackDown = childrenByVector.get("Vector[-1, -1]");

    assertNotNull(diagForwardUp, "Diagonal child [1, 1] should exist");
    assertNotNull(diagForwardDown, "Diagonal child [1, -1] should exist");
    assertNotNull(diagBackUp, "Diagonal child [-1, 1] should exist");
    assertNotNull(diagBackDown, "Diagonal child [-1, -1] should exist");

    // Forward diagonals should have a lower cost than backward diagonals
    assertTrue(diagForwardUp.getMomentum().cost().compareTo(diagBackUp.getMomentum().cost()) <= 0,
        "Forward diagonal should have lower or equal cost than backward diagonal");
  }

  @Test
  @DisplayName("Leading direction should always have the lowest momentum cost")
  void testLeadingDirectionHasLowestCost() {
    // Given
    FlexInteger parentGeneration = FlexInteger.of(3);
    FlexInteger parentMomentumCost = FlexInteger.of(20);
    FlexInteger initialEnergy = FlexInteger.of(999); // 999 + 1 = 1000, divisible by 20
    Vector parentMomentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);
    var tick = FlexInteger.of(2000);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        tick.subtract(initialEnergy),
        testPosition,
        parentGeneration,
        parentMomentum
    );

    // When
    var actions = entity.onTick(FlexInteger.of(10000)).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find leading child
    EntityModel leadingChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.ONE) && vector.get(1).equals(FlexInteger.ZERO);
        })
        .findFirst()
        .orElseThrow();

    FlexInteger leadingCost = leadingChild.getMomentum().cost();

    // All other children should have higher or equal cost
    children.stream()
        .filter(child -> !child.equals(leadingChild))
        .forEach(child -> {
          assertTrue(child.getMomentum().cost().compareTo(leadingCost) >= 0,
              "Child with vector " + child.getMomentum().vector() +
                  " has cost " + child.getMomentum().cost() +
                  " which should be >= leading cost " + leadingCost);
        });
  }

  @Test
  @DisplayName("Opposite direction should have highest cost among axis-aligned directions")
  void testOppositeDirectionHasHighestAxisAlignedCost() {
    // Given
    FlexInteger parentGeneration = FlexInteger.of(7);
    FlexInteger parentMomentumCost = FlexInteger.of(10);
    FlexInteger initialEnergy = FlexInteger.of(999); // 999 + 1 = 1000, divisible by 10
    Vector parentMomentumVector = Vector.of(FlexInteger.ZERO, FlexInteger.ONE);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);
    var tick = FlexInteger.of(2000);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        tick.subtract(initialEnergy),
        testPosition,
        parentGeneration,
        parentMomentum
    );

    // When
    var actions = entity.onTick(FlexInteger.of(10000)).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find opposite child [0, -1]
    EntityModel oppositeChild = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.ZERO) && vector.get(1).equals(FlexInteger.of(-1));
        })
        .findFirst()
        .orElseThrow();

    FlexInteger oppositeCost = oppositeChild.getMomentum().cost();

    // Get axis-aligned children (not diagonals)
    List<EntityModel> axisAligned = children.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return (vector.get(0).equals(FlexInteger.ZERO) && !vector.get(1).equals(FlexInteger.ZERO)) ||
              (vector.get(1).equals(FlexInteger.ZERO) && !vector.get(0).equals(FlexInteger.ZERO));
        })
        .toList();

    // Opposite should have highest cost among axis-aligned
    axisAligned.stream()
        .filter(child -> !child.equals(oppositeChild))
        .forEach(child -> {
          assertTrue(oppositeCost.compareTo(child.getMomentum().cost()) >= 0,
              "Opposite cost " + oppositeCost + " should be >= " +
                  child.getMomentum().vector() +
                  " cost " + child.getMomentum().cost());
        });
  }

  @Test
  @DisplayName("Higher generation should increase directional penalty")
  void testGenerationAffectsDirectionalPenalty() {
    // Given: two entities with different generations, same momentum
    FlexInteger lowGeneration = FlexInteger.of(2);
    FlexInteger highGeneration = FlexInteger.of(10);
    FlexInteger momentumCost = FlexInteger.of(20);
    Vector momentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    var tick = FlexInteger.of(10000);

    // Low generation entity
    FlexInteger lowGenEnergy = FlexInteger.of(999); // 999 + 1 = 1000, divisible by 20
    SingleEntityModel lowGenEntity = new SingleEntityModel(
        testSubstrateModel,
        UUID.randomUUID(),
        tick.subtract(lowGenEnergy),
        testPosition,
        lowGeneration,
        new Momentum(momentumCost, momentumVector)
    );

    // High generation entity
    FlexInteger highGenEnergy = FlexInteger.of(999);
    SingleEntityModel highGenEntity = new SingleEntityModel(
        testSubstrateModel,
        UUID.randomUUID(),
        tick.subtract(highGenEnergy),
        testPosition,
        highGeneration,
        new Momentum(momentumCost, momentumVector)
    );

    // When: both divide
    var lowGenActions = lowGenEntity.onTick(tick).toList();
    var highGenActions = highGenEntity.onTick(tick).toList();

    List<EntityModel> lowGenChildren = lowGenActions.getFirst().action().update(testSubstrateModel).toList();
    List<EntityModel> highGenChildren = highGenActions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find opposite children for both
    EntityModel lowGenOpposite = lowGenChildren.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.of(-1)) && vector.get(1).equals(FlexInteger.ZERO);
        })
        .findFirst()
        .orElseThrow();

    EntityModel highGenOpposite = highGenChildren.stream()
        .filter(child -> {
          Vector vector = child.getMomentum().vector();
          return vector.get(0).equals(FlexInteger.of(-1)) && vector.get(1).equals(FlexInteger.ZERO);
        })
        .findFirst()
        .orElseThrow();

    // Higher generation should have higher cost for same direction
    assertTrue(highGenOpposite.getMomentum().cost().compareTo(lowGenOpposite.getMomentum().cost()) > 0,
        "Higher generation opposite child should have higher cost due to depth scaling");
  }

  @Test
  @DisplayName("All child momentum costs should be positive")
  void testAllMomentumCostsArePositive() {
    // Given
    FlexInteger parentGeneration = FlexInteger.of(5);
    FlexInteger parentMomentumCost = FlexInteger.of(15);
    FlexInteger initialEnergy = FlexInteger.of(1004); // 1004 + 1 = 1005, divisible by 15
    Vector parentMomentumVector = Vector.of(FlexInteger.ONE, FlexInteger.ZERO);
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);
    var tick = FlexInteger.of(10000);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        tick.subtract(initialEnergy),
        testPosition,
        parentGeneration,
        parentMomentum
    );

    // When
    var actions = entity.onTick(FlexInteger.of(10000)).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then
    children.forEach(child -> {
      FlexInteger cost = child.getMomentum().cost();
      assertTrue(cost.compareTo(FlexInteger.ZERO) > 0,
          "Child with vector " + child.getMomentum().vector() +
              " has non-positive cost: " + cost);
    });
  }

  @Test
  @DisplayName("Merging two equal opposite momentums should result in zero momentum")
  void testMergeOppositeEqualMomentums() {
    // Given: two entities with equal energy and opposite momentums
    Momentum m1 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum m2 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.of(-1), FlexInteger.ZERO));
    FlexInteger energy = FlexInteger.of(100);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, energy, energy);

    // Then: should annihilate (zero momentum)
    assertEquals(FlexInteger.ZERO, result.cost(), "Cost should be zero for perfect annihilation");
    assertTrue(result.vector().isZero(), "Vector should be zero for perfect annihilation");
  }

  @Test
  @DisplayName("Merging two same-direction momentum's should add linearly")
  void testMergeSameDirectionMomentums() {
    // Given: two entities moving in the same direction [1, 0]
    Momentum m1 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum m2 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    FlexInteger energy1 = FlexInteger.of(50);
    FlexInteger energy2 = FlexInteger.of(50);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, energy1, energy2);

    // Then: should maintain same direction
    assertEquals(FlexInteger.ONE, result.vector().get(0), "X component should be 1");
    assertEquals(FlexInteger.ZERO, result.vector().get(1), "Y component should be 0");
    assertTrue(result.cost().compareTo(FlexInteger.ZERO) > 0, "Cost should be positive");
  }

  @Test
  @DisplayName("Merging momentums with different energies should weight by energy")
  void testMergeWeightedByEnergy() {
    // Given: heavy entity moving right [1,0], light entity moving up [0,1]
    Momentum heavy = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum light = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ZERO, FlexInteger.ONE));
    FlexInteger heavyEnergy = FlexInteger.of(900);
    FlexInteger lightEnergy = FlexInteger.of(100);

    // When: merge
    Momentum result = Momentum.merge(heavy, light, heavyEnergy, lightEnergy);

    // Then: should be biased toward heavy entity's direction
    assertTrue(result.vector().get(0).abs().compareTo(result.vector().get(1).abs()) > 0,
        "X component should dominate due to heavy entity");
  }

  @Test
  @DisplayName("Merging with zero energy should return default at-rest state")
  void testMergeWithZeroEnergy() {
    // Given: two entities with zero energy
    Momentum m1 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum m2 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ZERO, FlexInteger.ONE));

    // When: merge with zero energies
    Momentum result = Momentum.merge(m1, m2, FlexInteger.ZERO, FlexInteger.ZERO);

    // Then: should return default at-rest state
    assertEquals(FlexInteger.ONE, result.cost(), "Cost should be 1 for at-rest state");
    assertTrue(result.vector().isZero(), "Vector should be zero for at-rest state");
  }

  @Test
  @DisplayName("Merged momentum should respect speed limit (minimum cost of 1)")
  void testMergeRespectsSpeedLimit() {
    // Given: two very high-energy entities with low cost (high speed)
    Momentum m1 = new Momentum(FlexInteger.ONE, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum m2 = new Momentum(FlexInteger.ONE, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    FlexInteger veryHighEnergy = FlexInteger.of(10000);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, veryHighEnergy, veryHighEnergy);

    // Then: cost should not drop below 1 (speed limit)
    assertTrue(result.cost().compareTo(FlexInteger.ONE) >= 0,
        "Cost should be at least 1 (speed limit)");
  }

  @Test
  @DisplayName("Merged momentum vector must respect speed limit (max component = 1)")
  void testMergeRespectsSpeedOfLight() {
    // Given: two high-momentum entities moving in same direction
    Momentum m1 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum m2 = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    FlexInteger highEnergy = FlexInteger.of(10000);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, highEnergy, highEnergy);

    // Then: no component should exceed 1 (speed of light limit)
    for (int i = 0; i < result.vector().dimensions(); i++) {
      FlexInteger component = result.vector().get(i);
      assertTrue(component.abs().compareTo(FlexInteger.ONE) <= 0,
          "Vector component " + component + " exceeds speed of light (max=1)");
    }

    // And: at least one component should be exactly 1 (normalized)
    boolean hasUnitComponent = false;
    for (int i = 0; i < result.vector().dimensions(); i++) {
      if (result.vector().get(i).abs().equals(FlexInteger.ONE)) {
        hasUnitComponent = true;
        break;
      }
    }
    assertTrue(hasUnitComponent, "Normalized vector should have at least one component with magnitude 1");
  }

  @Test
  @DisplayName("Merging perpendicular momentums should produce diagonal result")
  void testMergePerpendicularMomentums() {
    // Given: one entity moving right [1,0], one moving up [0,1]
    Momentum right = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ONE, FlexInteger.ZERO));
    Momentum up = new Momentum(FlexInteger.TEN, Vector.of(FlexInteger.ZERO, FlexInteger.ONE));
    FlexInteger energy = FlexInteger.of(100);

    // When: merge with equal energies
    Momentum result = Momentum.merge(right, up, energy, energy);

    // Then: should be diagonal (both components non-zero)
    assertNotEquals(FlexInteger.ZERO, result.vector().get(0), "X component should be non-zero");
    assertNotEquals(FlexInteger.ZERO, result.vector().get(1), "Y component should be non-zero");

    // And: both components should have same magnitude (45-degree angle)
    assertEquals(result.vector().get(0).abs(), result.vector().get(1).abs(),
        "Equal energy perpendicular collision should produce 45-degree result");
  }
}
