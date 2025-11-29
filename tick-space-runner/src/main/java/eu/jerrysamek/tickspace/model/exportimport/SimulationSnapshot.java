package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.util.Collection;

/**
 * Immutable snapshot of simulation state at a specific tick.
 * Can be serialized to/from binary format for save/load functionality.
 */
public record SimulationSnapshot(
    FlexInteger tickCount,
    int dimensionCount,
    Collection<EntityModel> entities) {

  public SimulationSnapshot {
    if (tickCount == null) {
      throw new IllegalArgumentException("tickCount cannot be null");
    }
    if (dimensionCount <= 0) {
      throw new IllegalArgumentException("dimensionCount must be positive");
    }
    if (entities == null) {
      throw new IllegalArgumentException("entities cannot be null");
    }
  }

  public int entityCount() {
    return entities.size();
  }
}
