package eu.jerrysamek.tickspace.model.entity;

import eu.jerrysamek.tickspace.model.substrate.SubstrateModelUpdate;
import eu.jerrysamek.tickspace.model.ticktime.TickTimeConsumer;

import java.util.Collection;

public interface EntitiesRegistry extends TickTimeConsumer<SubstrateModelUpdate> {
  /**
   * Returns a snapshot of all entities.
   * Converts EntityData → EntityModel on-demand.
   */
  Collection<EntityModel> snapshot();
}
