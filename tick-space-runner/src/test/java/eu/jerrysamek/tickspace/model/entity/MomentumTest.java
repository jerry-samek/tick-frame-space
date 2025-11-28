package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.List;
import java.util.Map;
import java.util.UUID;
import java.util.stream.Collectors;

import static org.junit.jupiter.api.Assertions.*;

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
    testPosition = new Position(new BigInteger[]{BigInteger.ZERO, BigInteger.ZERO});
  }

  @Test
  @DisplayName("Momentum costs should be correctly calculated for all 8 children in 2D space")
  void testMomentumCostsFor2DSpace() {
    // Given: parent with generation=5, cost=15, vector=[1, 0]
    BigInteger parentGeneration = BigInteger.valueOf(5);
    BigInteger parentMomentumCost = BigInteger.valueOf(15);
    BigInteger initialEnergy = BigInteger.valueOf(1004); // 1004 + 1 = 1005, divisible by 15
    BigInteger[] parentMomentumVector = new BigInteger[]{BigInteger.ONE, BigInteger.ZERO};
    Momentum parentMomentum = new Momentum(parentMomentumCost, parentMomentumVector);

    SingleEntityModel entity = new SingleEntityModel(
        testSubstrateModel,
        testIdentity,
        testPosition,
        initialEnergy,
        parentGeneration,
        parentMomentum
    );

    // When: entity divides
    var actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: 8 children created
    assertEquals(8, children.size());

    // Map children by their momentum vectors for easy lookup
    Map<String, EntityModel> childrenByVector = children.stream()
        .collect(Collectors.toMap(
            child -> Arrays.toString(child.getMomentum().vector()),
            child -> child
        ));

    // Leading direction [1, 0] - same as parent, should have lowest cost
    EntityModel leading = childrenByVector.get("[1, 0]");
    assertNotNull(leading, "Leading child [1, 0] should exist");
    BigInteger leadingCost = leading.getMomentum().cost();
    assertEquals(BigInteger.valueOf(30), leadingCost, "Leading cost should be parentCost + childCost = 15 + 15");

    // Opposite direction [-1, 0] - reversal, should have highest cost among axis-aligned
    EntityModel opposite = childrenByVector.get("[-1, 0]");
    assertNotNull(opposite, "Opposite child [-1, 0] should exist");
    BigInteger oppositeCost = opposite.getMomentum().cost();
    assertEquals(BigInteger.valueOf(45), oppositeCost, "Opposite cost should include reversal penalty");

    // Perpendicular directions [0, 1] and [0, -1] - medium turn penalty
    EntityModel perpUp = childrenByVector.get("[0, 1]");
    EntityModel perpDown = childrenByVector.get("[0, -1]");
    assertNotNull(perpUp, "Perpendicular child [0, 1] should exist");
    assertNotNull(perpDown, "Perpendicular child [0, -1] should exist");
    assertEquals(BigInteger.valueOf(35), perpUp.getMomentum().cost(), "Perpendicular up should have medium penalty");
    assertEquals(BigInteger.valueOf(35), perpDown.getMomentum().cost(), "Perpendicular down should have medium penalty");

    // Diagonal directions - higher base cost due to distance
    EntityModel diagForwardUp = childrenByVector.get("[1, 1]");
    EntityModel diagForwardDown = childrenByVector.get("[1, -1]");
    EntityModel diagBackUp = childrenByVector.get("[-1, 1]");
    EntityModel diagBackDown = childrenByVector.get("[-1, -1]");

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
    BigInteger parentGeneration = BigInteger.valueOf(3);
    BigInteger parentMomentumCost = BigInteger.valueOf(20);
    BigInteger initialEnergy = BigInteger.valueOf(999); // 999 + 1 = 1000, divisible by 20
    BigInteger[] parentMomentumVector = new BigInteger[]{BigInteger.ONE, BigInteger.ZERO};
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
    var actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find leading child
    EntityModel leadingChild = children.stream()
        .filter(child -> {
          BigInteger[] vector = child.getMomentum().vector();
          return vector[0].equals(BigInteger.ONE) && vector[1].equals(BigInteger.ZERO);
        })
        .findFirst()
        .orElseThrow();

    BigInteger leadingCost = leadingChild.getMomentum().cost();

    // All other children should have higher or equal cost
    children.stream()
        .filter(child -> !child.equals(leadingChild))
        .forEach(child -> {
          assertTrue(child.getMomentum().cost().compareTo(leadingCost) >= 0,
              "Child with vector " + Arrays.toString(child.getMomentum().vector()) +
                  " has cost " + child.getMomentum().cost() +
                  " which should be >= leading cost " + leadingCost);
        });
  }

  @Test
  @DisplayName("Opposite direction should have highest cost among axis-aligned directions")
  void testOppositeDirectionHasHighestAxisAlignedCost() {
    // Given
    BigInteger parentGeneration = BigInteger.valueOf(7);
    BigInteger parentMomentumCost = BigInteger.valueOf(10);
    BigInteger initialEnergy = BigInteger.valueOf(999); // 999 + 1 = 1000, divisible by 10
    BigInteger[] parentMomentumVector = new BigInteger[]{BigInteger.ZERO, BigInteger.ONE};
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
    var actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find opposite child [0, -1]
    EntityModel oppositeChild = children.stream()
        .filter(child -> {
          BigInteger[] vector = child.getMomentum().vector();
          return vector[0].equals(BigInteger.ZERO) && vector[1].equals(BigInteger.valueOf(-1));
        })
        .findFirst()
        .orElseThrow();

    BigInteger oppositeCost = oppositeChild.getMomentum().cost();

    // Get axis-aligned children (not diagonals)
    List<EntityModel> axisAligned = children.stream()
        .filter(child -> {
          BigInteger[] vector = child.getMomentum().vector();
          return (vector[0].equals(BigInteger.ZERO) && !vector[1].equals(BigInteger.ZERO)) ||
              (vector[1].equals(BigInteger.ZERO) && !vector[0].equals(BigInteger.ZERO));
        })
        .toList();

    // Opposite should have highest cost among axis-aligned
    axisAligned.stream()
        .filter(child -> !child.equals(oppositeChild))
        .forEach(child -> {
          assertTrue(oppositeCost.compareTo(child.getMomentum().cost()) >= 0,
              "Opposite cost " + oppositeCost + " should be >= " +
                  Arrays.toString(child.getMomentum().vector()) +
                  " cost " + child.getMomentum().cost());
        });
  }

  @Test
  @DisplayName("Higher generation should increase directional penalty")
  void testGenerationAffectsDirectionalPenalty() {
    // Given: two entities with different generations, same momentum
    BigInteger lowGeneration = BigInteger.valueOf(2);
    BigInteger highGeneration = BigInteger.valueOf(10);
    BigInteger momentumCost = BigInteger.valueOf(20);
    BigInteger[] momentumVector = new BigInteger[]{BigInteger.ONE, BigInteger.ZERO};

    // Low generation entity
    BigInteger lowGenEnergy = BigInteger.valueOf(999); // 999 + 1 = 1000, divisible by 20
    SingleEntityModel lowGenEntity = new SingleEntityModel(
        testSubstrateModel,
        UUID.randomUUID(),
        testPosition,
        lowGenEnergy,
        lowGeneration,
        new Momentum(momentumCost, momentumVector)
    );

    // High generation entity
    BigInteger highGenEnergy = BigInteger.valueOf(999);
    SingleEntityModel highGenEntity = new SingleEntityModel(
        testSubstrateModel,
        UUID.randomUUID(),
        testPosition,
        highGenEnergy,
        highGeneration,
        new Momentum(momentumCost, momentumVector)
    );

    // When: both divide
    var lowGenActions = lowGenEntity.onTick(BigInteger.ONE).toList();
    var highGenActions = highGenEntity.onTick(BigInteger.ONE).toList();

    List<EntityModel> lowGenChildren = lowGenActions.getFirst().action().update(testSubstrateModel).toList();
    List<EntityModel> highGenChildren = highGenActions.getFirst().action().update(testSubstrateModel).toList();

    // Then: find opposite children for both
    EntityModel lowGenOpposite = lowGenChildren.stream()
        .filter(child -> {
          BigInteger[] vector = child.getMomentum().vector();
          return vector[0].equals(BigInteger.valueOf(-1)) && vector[1].equals(BigInteger.ZERO);
        })
        .findFirst()
        .orElseThrow();

    EntityModel highGenOpposite = highGenChildren.stream()
        .filter(child -> {
          BigInteger[] vector = child.getMomentum().vector();
          return vector[0].equals(BigInteger.valueOf(-1)) && vector[1].equals(BigInteger.ZERO);
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
    BigInteger parentGeneration = BigInteger.valueOf(5);
    BigInteger parentMomentumCost = BigInteger.valueOf(15);
    BigInteger initialEnergy = BigInteger.valueOf(1004); // 1004 + 1 = 1005, divisible by 15
    BigInteger[] parentMomentumVector = new BigInteger[]{BigInteger.ONE, BigInteger.ZERO};
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
    var actions = entity.onTick(BigInteger.ONE).toList();
    List<EntityModel> children = actions.getFirst().action().update(testSubstrateModel).toList();

    // Then
    children.forEach(child -> {
      BigInteger cost = child.getMomentum().cost();
      assertTrue(cost.compareTo(BigInteger.ZERO) > 0,
          "Child with vector " + Arrays.toString(child.getMomentum().vector()) +
              " has non-positive cost: " + cost);
    });
  }

  @Test
  @DisplayName("Merging two equal opposite momentums should result in zero momentum")
  void testMergeOppositeEqualMomentums() {
    // Given: two entities with equal energy and opposite momentums
    Momentum m1 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum m2 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.valueOf(-1), BigInteger.ZERO});
    BigInteger energy = BigInteger.valueOf(100);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, energy, energy);

    // Then: should annihilate (zero momentum)
    assertEquals(BigInteger.ZERO, result.cost(), "Cost should be zero for perfect annihilation");
    assertTrue(Arrays.stream(result.vector()).allMatch(v -> v.equals(BigInteger.ZERO)),
        "Vector should be zero for perfect annihilation");
  }

  @Test
  @DisplayName("Merging two same-direction momentum's should add linearly")
  void testMergeSameDirectionMomentums() {
    // Given: two entities moving in the same direction [1, 0]
    Momentum m1 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum m2 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    BigInteger energy1 = BigInteger.valueOf(50);
    BigInteger energy2 = BigInteger.valueOf(50);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, energy1, energy2);

    // Then: should maintain same direction
    assertEquals(BigInteger.ONE, result.vector()[0], "X component should be 1");
    assertEquals(BigInteger.ZERO, result.vector()[1], "Y component should be 0");
    assertTrue(result.cost().compareTo(BigInteger.ZERO) > 0, "Cost should be positive");
  }

  @Test
  @DisplayName("Merging momentums with different energies should weight by energy")
  void testMergeWeightedByEnergy() {
    // Given: heavy entity moving right [1,0], light entity moving up [0,1]
    Momentum heavy = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum light = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ONE});
    BigInteger heavyEnergy = BigInteger.valueOf(900);
    BigInteger lightEnergy = BigInteger.valueOf(100);

    // When: merge
    Momentum result = Momentum.merge(heavy, light, heavyEnergy, lightEnergy);

    // Then: should be biased toward heavy entity's direction
    assertTrue(result.vector()[0].abs().compareTo(result.vector()[1].abs()) > 0,
        "X component should dominate due to heavy entity");
  }

  @Test
  @DisplayName("Merging with zero energy should return default at-rest state")
  void testMergeWithZeroEnergy() {
    // Given: two entities with zero energy
    Momentum m1 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum m2 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ONE});

    // When: merge with zero energies
    Momentum result = Momentum.merge(m1, m2, BigInteger.ZERO, BigInteger.ZERO);

    // Then: should return default at-rest state
    assertEquals(BigInteger.ONE, result.cost(), "Cost should be 1 for at-rest state");
    assertTrue(Arrays.stream(result.vector()).allMatch(v -> v.equals(BigInteger.ZERO)),
        "Vector should be zero for at-rest state");
  }

  @Test
  @DisplayName("Merged momentum should respect speed limit (minimum cost of 1)")
  void testMergeRespectsSpeedLimit() {
    // Given: two very high-energy entities with low cost (high speed)
    Momentum m1 = new Momentum(BigInteger.ONE, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum m2 = new Momentum(BigInteger.ONE, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    BigInteger veryHighEnergy = BigInteger.valueOf(10000);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, veryHighEnergy, veryHighEnergy);

    // Then: cost should not drop below 1 (speed limit)
    assertTrue(result.cost().compareTo(BigInteger.ONE) >= 0,
        "Cost should be at least 1 (speed limit)");
  }

  @Test
  @DisplayName("Merged momentum vector must respect speed limit (max component = 1)")
  void testMergeRespectsSpeedOfLight() {
    // Given: two high-momentum entities moving in same direction
    Momentum m1 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum m2 = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    BigInteger highEnergy = BigInteger.valueOf(10000);

    // When: merge
    Momentum result = Momentum.merge(m1, m2, highEnergy, highEnergy);

    // Then: no component should exceed 1 (speed of light limit)
    for (BigInteger component : result.vector()) {
      assertTrue(component.abs().compareTo(BigInteger.ONE) <= 0,
          "Vector component " + component + " exceeds speed of light (max=1)");
    }

    // And: at least one component should be exactly 1 (normalized)
    boolean hasUnitComponent = false;
    for (BigInteger component : result.vector()) {
      if (component.abs().equals(BigInteger.ONE)) {
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
    Momentum right = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ONE, BigInteger.ZERO});
    Momentum up = new Momentum(BigInteger.TEN, new BigInteger[]{BigInteger.ZERO, BigInteger.ONE});
    BigInteger energy = BigInteger.valueOf(100);

    // When: merge with equal energies
    Momentum result = Momentum.merge(right, up, energy, energy);

    // Then: should be diagonal (both components non-zero)
    assertNotEquals(BigInteger.ZERO, result.vector()[0], "X component should be non-zero");
    assertNotEquals(BigInteger.ZERO, result.vector()[1], "Y component should be non-zero");

    // And: both components should have same magnitude (45-degree angle)
    assertEquals(result.vector()[0].abs(), result.vector()[1].abs(),
        "Equal energy perpendicular collision should produce 45-degree result");
  }
}
