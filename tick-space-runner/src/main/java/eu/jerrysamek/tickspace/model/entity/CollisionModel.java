package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;

import java.math.BigInteger;
import java.util.*;

public class CollisionModel {

    public enum OutcomeType { MERGE, BOUNCE, DISAPPEAR }

    public static class CollisionOutcome {
        public final OutcomeType type;
        public final Optional<EntityModel> survivor;
        public final List<EntityModel> bounced;
        public final List<EntityModel> removed;

        public CollisionOutcome(OutcomeType type,
                                Optional<EntityModel> survivor,
                                List<EntityModel> bounced,
                                List<EntityModel> removed) {
            this.type = type;
            this.survivor = survivor;
            this.bounced = bounced;
            this.removed = removed;
        }
    }

    public static CollisionOutcome resolveCollision(List<EntityModel> claimants, boolean hasOccupant) {
        if (claimants.isEmpty()) return new CollisionOutcome(OutcomeType.DISAPPEAR, Optional.empty(), List.of(), List.of());

        // --- Priority: occupant inertia ---
        claimants.sort(Comparator.comparing((EntityModel e) -> hasOccupant ? 0 : 1) // occupant first
                .thenComparing(e -> e.getEnergy().negate())                  // higher energy first
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
            EntityModel merged = mergeEntities(claimants);
            return new CollisionOutcome(OutcomeType.MERGE, Optional.of(merged), List.of(), List.of());
        } else if (dotSum.equals(BigInteger.ZERO)) {
            // Divergent but not opposed → BOUNCE
            List<EntityModel> bounced = new ArrayList<>();
            for (EntityModel e : claimants) {
                bounced.add(bounceEntity(e));
            }
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

    private static EntityModel mergeEntities(List<EntityModel> claimants) {
        BigInteger totalEnergy = claimants.stream().map(EntityModel::getEnergy).reduce(BigInteger.ZERO, BigInteger::add);
        BigInteger maxGeneration = claimants.stream().map(EntityModel::getGeneration).max(BigInteger::compareTo).orElse(BigInteger.ZERO);
        Position position = claimants.get(0).getPosition();
        Momentum momentum = claimants.get(0).getMomentum(); // simplify: take first's momentum
        BigInteger newCost = momentum.cost().add(BigInteger.ONE);

        return new EntityModel(
            UUID.randomUUID(),
            position,
            totalEnergy,
            maxGeneration.add(BigInteger.ONE),
            new Momentum(newCost, momentum.vector())
        );
    }

    private static EntityModel bounceEntity(EntityModel e) {
        // Simplified bounce: invert momentum
        BigInteger[] m = e.getMomentum().vector();
        BigInteger[] bounced = new BigInteger[m.length];
        for (int i = 0; i < m.length; i++) {
            bounced[i] = m[i].negate();
        }

        BigInteger newEnergy = e.getEnergy().subtract(BigInteger.ONE).max(BigInteger.ZERO);

        return new EntityModel(
            e.getIdentity(),
            e.getPosition(),
            newEnergy,
            e.getGeneration(),
            new Momentum(e.getMomentum().cost(), bounced)
        );
    }
}
