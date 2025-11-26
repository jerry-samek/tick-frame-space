package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.UUID;

import static java.math.BigInteger.ONE;
import static java.math.BigInteger.ZERO;

public interface EntityModel extends TickTimeConsumer<EntityModelUpdate> {

  BigInteger[][] OFFSETS = { // TODO dimensions
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

  UUID getIdentity();

  BigInteger getEnergy();

  Position getPosition();

  BigInteger getGeneration();

  Momentum getMomentum();
}
