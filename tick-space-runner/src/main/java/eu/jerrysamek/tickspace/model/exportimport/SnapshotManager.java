package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Path;

/**
 * High-level manager for creating and restoring simulation snapshots.
 * Handles coordination between TickTimeModel, SubstrateModel, and EntitiesRegistry.
 */
public class SnapshotManager {

  private final BinarySnapshotWriter writer;
  private final BinarySnapshotReader reader;

  public SnapshotManager(boolean compress) {
    this.writer = new BinarySnapshotWriter(compress);
    this.reader = new BinarySnapshotReader();
  }

  public SnapshotManager() {
    this(true); // Default: compressed
  }

  /**
   * Creates a snapshot of the current simulation state.
   *
   * @param tickCount current tick
   * @param registry entities registry
   * @param dimensionCount number of dimensions
   * @return snapshot
   */
  public SimulationSnapshot createSnapshot(FlexInteger tickCount, EntitiesRegistry registry,
                                           int dimensionCount) {
    return new SimulationSnapshot(
        tickCount,
        dimensionCount,
        registry.snapshot() // Gets all entities
    );
  }

  /**
   * Saves a snapshot to file.
   */
  public void save(SimulationSnapshot snapshot, Path path) throws IOException {
    writer.write(snapshot, path);
  }

  /**
   * Loads a snapshot from file.
   */
  public SimulationSnapshot load(Path path, SubstrateModel substrateModel) throws IOException {
    return reader.read(path, substrateModel);
  }

  /**
   * Restores simulation state from a snapshot.
   * Note: This should be called when the simulation is stopped.
   *
   * @param snapshot the snapshot to restore
   * @param registry the entities registry to populate
   * @return the tick count from the snapshot
   */
  public FlexInteger restore(SimulationSnapshot snapshot, EntitiesRegistry registry) {
    // Clear current state
    registry.destroy();

    // Restore entities and rebuild schedule
    for (var entity : snapshot.entities()) {
      var position = entity.getPosition();
      registry.addEntity(position, entity);
    }

    return snapshot.tickCount();
  }

  /**
   * Estimates the file size for a snapshot.
   */
  public long estimateFileSize(SimulationSnapshot snapshot) {
    return writer.estimateSize(snapshot);
  }
}
