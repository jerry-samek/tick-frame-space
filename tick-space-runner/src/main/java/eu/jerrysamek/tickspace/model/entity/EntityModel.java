package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.math.BigInteger;
import java.util.UUID;

public interface EntityModel extends TickTimeConsumer<EntityModelUpdate> {

  UUID getIdentity();

  EnergyState getEnergy();

  Position getPosition();

  BigInteger getGeneration();

  Momentum getMomentum();
}
