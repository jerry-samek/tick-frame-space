package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.UUID;

public interface EntityModel extends TickTimeConsumer<EntityModelUpdate> {

  UUID getIdentity();

  FlexInteger getEnergy(FlexInteger tick);

  FlexInteger tickOfBirth();

  Position getPosition();

  FlexInteger getGeneration();

  Momentum getMomentum();

  FlexInteger getNextPossibleAction();
}
