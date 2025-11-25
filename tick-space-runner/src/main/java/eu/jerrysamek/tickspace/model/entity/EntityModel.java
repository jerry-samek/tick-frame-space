package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.Arrays;
import java.util.UUID;
import java.util.concurrent.atomic.AtomicInteger;
import java.util.stream.Stream;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public class EntityModel implements TickTimeConsumer<EntityModelUpdate> {
  private static BigInteger[][] OFFSETS = { // TODO dimensions
      {ONE, ZERO, ZERO}, {ONE.negate(), ZERO, ZERO},
      {ZERO, ONE, ZERO}, {ZERO, ONE.negate(), ZERO},
      {ZERO, ZERO, ONE}, {ZERO, ZERO, ONE.negate()},

      // Edges (12)
      {ONE, ONE, ZERO}, {ONE, ONE.negate(), ZERO}, {ONE.negate(), ONE, ZERO}, {ONE.negate(), ONE.negate(), ZERO},
      {ONE, ZERO, ONE}, {ONE, ZERO, ONE.negate()}, {ONE.negate(), ZERO, ONE}, {ONE.negate(), ZERO, ONE.negate()},
      {ZERO, ONE, ONE}, {ZERO, ONE, ONE.negate()}, {ZERO, ONE.negate(), ONE}, {ZERO, ONE.negate(), ONE.negate()},

      // Corners (8)
      {ONE, ONE, ONE}, {ONE, ONE, ONE.negate()}, {ONE, ONE.negate(), ONE}, {ONE, ONE.negate(), ONE.negate()},
      {ONE.negate(), ONE, ONE}, {ONE.negate(), ONE, ONE.negate()}, {ONE.negate(), ONE.negate(), ONE}, {ONE.negate(), ONE.negate(), ONE.negate()}
  };

  private final UUID identity;
  private BigInteger energy;
  private final BigInteger generation;
  private final Position position;
  private final Momentum momentum;

  public EntityModel(UUID identity, Position position, BigInteger initialEnergy, BigInteger generation, Momentum momentum) {
    this.identity = identity;
    this.energy = initialEnergy;
    this.position = position;
    this.generation = generation;
    this.momentum = momentum;
  }

  public UUID getIdentity() {
    return identity;
  }

  public BigInteger getEnergy() {
    return energy;
  }

  public Position getPosition() {
    return position;
  }

  public BigInteger getGeneration() {
    return generation;
  }

  public Momentum getMomentum() {
    return momentum;
  }


  @Override
  public Stream<EntityModelUpdate> onTick(BigInteger tickCount) {
    var newEnergy = energy.add(ONE);

    var childEnergies = Stream.of(OFFSETS)
        .map(bigIntegers -> computeEnergyCost(momentum.vector(), bigIntegers, momentum.cost(), generation))
        .toList();

    var energyRequirement = childEnergies.stream().reduce(ZERO, BigInteger::add);

    if (newEnergy.compareTo(energyRequirement) >= 0) {

      // Six axis-aligned offsets (octahedral shell)
      AtomicInteger index = new AtomicInteger(0);
      return childEnergies.stream()
          .map(childCost -> _ -> {
            var offset = OFFSETS[index.getAndIncrement()];

            return new EntityModel(
                UUID.randomUUID(),
                position.offset(offset),
                ZERO,
                generation.add(ONE),
                new Momentum(momentum.cost().add(childCost), offset));
          });
    } else if (newEnergy.compareTo(momentum.cost()) >= 0) {
      return Stream.of(_ -> new EntityModel(identity, position.offset(momentum.vector()), newEnergy, generation, momentum));
    } else {
      energy = newEnergy; // update inner state but nothing else

      return Stream.empty();
    }
  }

  @Override
  public String toString() {
    return "EntityModel{" +
        "energy=" + energy +
        ", position=" + position +
        '}';
  }

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
