package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;

import java.math.BigInteger;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Comparator;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public class CollisionModel {

  public enum OutcomeType {MERGE, BOUNCE, DISAPPEAR}

  public record CollisionOutcome(
      OutcomeType type,
      Optional<EntityModel> survivor,
      List<EntityModel> bounced,
      List<EntityModel> removed) {
  }

  public static CollisionOutcome resolveCollision(SubstrateModel model, List<EntityModel> claimants) {
    if (claimants.isEmpty()) return new CollisionOutcome(OutcomeType.DISAPPEAR, Optional.empty(), List.of(), List.of());

    // --- Priority: occupant inertia ---
    claimants.sort(Comparator.comparing((EntityModel e) -> e.getEnergy().getEnergy().negate())                  // higher energy first
        .thenComparing(EntityModel::getGeneration)                   // deeper lineage favored
        .thenComparing(EntityModel::getIdentity));                   // deterministic tie

    EntityModel first = claimants.get(0);

    // --- Simple classification ---
    if (claimants.size() == 1) {
      // No collision
      return new CollisionOutcome(OutcomeType.MERGE, Optional.of(first), List.of(), List.of());
    }

    // Compute alignment (dot product sign)
    BigInteger[] m0 = first.getMomentum().vector();
    BigInteger dotSum = BigInteger.ZERO;
    for (EntityModel e : claimants) {
      dotSum = dotSum.add(dot(m0, e.getMomentum().vector()));
    }

    if (dotSum.compareTo(BigInteger.ZERO) > 0) {
      // Mostly aligned → MERGE
      EntityModel merged = mergeEntities(model, claimants);
      return new CollisionOutcome(OutcomeType.MERGE, Optional.of(merged), List.of(), List.of());
    } else if (dotSum.equals(BigInteger.ZERO)) {
      // Divergent but not opposed → BOUNCE
      List<EntityModel> bounced = bounceEntities(model, claimants);

      return new CollisionOutcome(OutcomeType.BOUNCE, Optional.empty(), bounced, List.of());
    } else {
      // Strong opposition → DISAPPEAR lowest-priority
      List<EntityModel> removed = new ArrayList<>(claimants.subList(1, claimants.size()));
      return new CollisionOutcome(OutcomeType.DISAPPEAR, Optional.of(first), List.of(), removed);
    }
  }

  // --- Helpers ---
  private static BigInteger dot(BigInteger[] a, BigInteger[] b) {
    BigInteger result = BigInteger.ZERO;
    for (int i = 0; i < Math.min(a.length, b.length); i++) {
      result = result.add(a[i].multiply(b[i]));
    }
    return result;
  }

  private static EntityModel mergeEntities(SubstrateModel model, List<EntityModel> claimants) {
    // --- Energy: sum all energies (conservation of energy) ---
    BigInteger totalEnergy = claimants.stream()
        .map(EntityModel::getEnergy)
        .map(EnergyState::getEnergy)
        .reduce(BigInteger.ZERO, BigInteger::add);

    // --- Generation: take deepest lineage and increment ---
    BigInteger maxGeneration = claimants.stream()
        .map(EntityModel::getGeneration)
        .max(BigInteger::compareTo)
        .orElse(BigInteger.ZERO);

    // --- Position: all claimants target the same cell ---
    Position position = claimants.get(0).getPosition();

    // --- Momentum: vector sum (conservation of momentum) ---
    // p_total = Σ p_i (each entity's momentum vector is added component-wise)
    BigInteger[] mergedVector = new BigInteger[claimants.get(0).getMomentum().vector().length];
    Arrays.fill(mergedVector, BigInteger.ZERO);

    for (EntityModel e : claimants) {
      BigInteger[] vec = e.getMomentum().vector();
      for (int i = 0; i < mergedVector.length; i++) {
        mergedVector[i] = mergedVector[i].add(vec[i]);
      }
    }

    // --- Cost: based on resulting momentum magnitude ---
    // sqrt(Σ component²) gives the magnitude of the merged momentum
    BigInteger momentumMagnitudeSq = BigInteger.ZERO;
    for (BigInteger component : mergedVector) {
      momentumMagnitudeSq = momentumMagnitudeSq.add(component.multiply(component));
    }
    BigInteger newCost = sqrt(momentumMagnitudeSq).add(BigInteger.ONE);

    Momentum mergedMomentum = new Momentum(newCost, mergedVector);

    // --- Construct merged entity ---
    return new SingleEntityModel(
        model,
        UUID.randomUUID(),
        position,
        totalEnergy,
        maxGeneration.add(BigInteger.ONE),
        mergedMomentum
    );
  }

  // Integer-safe sqrt (floor)
  private static BigInteger sqrt(BigInteger x) {
    if (x.compareTo(BigInteger.ZERO) <= 0) return BigInteger.ZERO;
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


  private static List<EntityModel> bounceEntities(SubstrateModel model, List<EntityModel> claimants) {
    // Inelastic collision: conserve momentum but dissipate some energy
    List<EntityModel> bounced = new ArrayList<>();

    // --- Calculate center of mass momentum ---
    BigInteger[] totalMomentum = new BigInteger[claimants.get(0).getMomentum().vector().length];
    Arrays.fill(totalMomentum, BigInteger.ZERO);
    BigInteger totalEnergy = BigInteger.ZERO;

    for (EntityModel e : claimants) {
      BigInteger[] vec = e.getMomentum().vector();
      for (int i = 0; i < totalMomentum.length; i++) {
        totalMomentum[i] = totalMomentum[i].add(vec[i]);
      }
      totalEnergy = totalEnergy.add(e.getEnergy().getEnergy());
    }

    // --- For each entity, compute reflection relative to center of mass ---
    for (EntityModel e : claimants) {
      BigInteger[] m = e.getMomentum().vector();
      BigInteger[] newVec = new BigInteger[m.length];

      // Compute relative momentum: p_rel = p_entity - p_cm/n
      BigInteger n = BigInteger.valueOf(claimants.size());
      for (int i = 0; i < m.length; i++) {
        BigInteger p_cm_component = totalMomentum[i].divide(n);
        BigInteger p_rel = m[i].subtract(p_cm_component);
        // Reflect relative momentum and add back center of mass motion
        newVec[i] = p_cm_component.subtract(p_rel);
      }

      // --- Energy dissipation (inelastic collision) ---
      // Energy loss proportional to relative momentum squared (kinetic energy loss)
      BigInteger relMomentumSq = BigInteger.ZERO;
      for (int i = 0; i < m.length; i++) {
        BigInteger p_cm_component = totalMomentum[i].divide(n);
        BigInteger p_rel = m[i].subtract(p_cm_component);
        relMomentumSq = relMomentumSq.add(p_rel.multiply(p_rel));
      }

      // Energy loss: roughly 10-30% of relative kinetic energy
      BigInteger energyLoss = sqrt(relMomentumSq).divide(BigInteger.valueOf(5)).max(BigInteger.ONE);
      BigInteger newEnergy = e.getEnergy().getEnergy().subtract(energyLoss).max(BigInteger.ZERO);

      bounced.add(new SingleEntityModel(
          model,
          e.getIdentity(),
          e.getPosition(),  // entities return to their previous position after bounce
          newEnergy,
          e.getGeneration(),
          new Momentum(e.getMomentum().cost(), newVec)
      ));
    }

    return bounced;
  }

}
