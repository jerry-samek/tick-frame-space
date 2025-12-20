package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistryLegacy;
import eu.jerrysamek.tickspace.model.entity.Momentum;
import eu.jerrysamek.tickspace.model.entity.SingleEntityModel;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.nio.file.Path;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class BinarySnapshotTest {

  @TempDir
  Path tempDir;

  private SubstrateModel substrateModel;
  private EntitiesRegistryLegacy registry;
  private SnapshotManager snapshotManager;

  @BeforeEach
  void setUp() {
    registry = new EntitiesRegistryLegacy();
    substrateModel = new SubstrateModel(3, registry);
    snapshotManager = new SnapshotManager(true);
  }

  @Test
  @DisplayName("Should save and load snapshot with single entity")
  void testSaveAndLoadSingleEntity() throws IOException {
    // Given: Create a simple entity
    var position = new Position(Vector.of(FlexInteger.of(10), FlexInteger.of(20), FlexInteger.of(30)));
    var momentum = new Momentum(FlexInteger.of(5), Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO));
    var entity = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        FlexInteger.of(950),
        position,
        FlexInteger.ZERO,
        momentum
    );

    registry.addEntity(position, entity);
    FlexInteger tickCount = FlexInteger.of(1000);

    // When: Save snapshot
    var snapshot = snapshotManager.createSnapshot(tickCount, registry, 3);
    Path snapshotFile = tempDir.resolve("snapshot.bin");
    snapshotManager.save(snapshot, snapshotFile);

    // Then: File exists and has reasonable size
    assertTrue(snapshotFile.toFile().exists());
    long fileSize = snapshotFile.toFile().length();
    assertTrue(fileSize > 0 && fileSize < 1000, "File size should be small for single entity");

    // When: Load snapshot
    var loadedSnapshot = snapshotManager.load(snapshotFile, substrateModel);

    // Then: Snapshot matches
    assertEquals(tickCount, loadedSnapshot.tickCount());
    assertEquals(3, loadedSnapshot.dimensionCount());
    assertEquals(1, loadedSnapshot.entityCount());

    var loadedEntity = loadedSnapshot.entities().iterator().next();
    assertEquals(position, loadedEntity.getPosition());
    assertEquals(FlexInteger.of(50), loadedEntity.getEnergy(loadedSnapshot.tickCount()));
    assertEquals(FlexInteger.of(5), loadedEntity.getMomentum().cost());
  }

  @Test
  @DisplayName("Should handle multiple entities")
  void testMultipleEntities() throws IOException {
    // Given: Create multiple entities
    for (int i = 0; i < 10; i++) {
      var position = new Position(Vector.of(
          FlexInteger.of(i),
          FlexInteger.of(i * 2),
          FlexInteger.of(i * 3)
      ));
      var momentum = new Momentum(FlexInteger.of(i + 1), Vector.of(FlexInteger.ONE, FlexInteger.ZERO, FlexInteger.ZERO));
      var entity = new SingleEntityModel(
          substrateModel,
          UUID.randomUUID(),
          FlexInteger.of(100 - i * 10),
          position,
          FlexInteger.ZERO,
          momentum
      );
      registry.addEntity(position, entity);
    }

    // When: Save and load
    var snapshot = snapshotManager.createSnapshot(FlexInteger.of(500), registry, 3);
    Path snapshotFile = tempDir.resolve("multi_snapshot.bin");
    snapshotManager.save(snapshot, snapshotFile);

    var loadedSnapshot = snapshotManager.load(snapshotFile, substrateModel);

    // Then: All entities loaded
    assertEquals(10, loadedSnapshot.entityCount());
    assertEquals(FlexInteger.of(500), loadedSnapshot.tickCount());
  }

  @Test
  @DisplayName("VarLong encoding should work for various values")
  void testVarLongEncoding() throws IOException {
    long[] testValues = {0, 1, 127, 128, 255, 256, 65535, 65536, Integer.MAX_VALUE, Long.MAX_VALUE};

    for (long value : testValues) {
      java.io.ByteArrayOutputStream baos = new java.io.ByteArrayOutputStream();
      java.io.DataOutputStream out = new java.io.DataOutputStream(baos);

      BinarySnapshotFormat.writeVarLong(out, value);
      out.flush();

      java.io.ByteArrayInputStream bais = new java.io.ByteArrayInputStream(baos.toByteArray());
      java.io.DataInputStream in = new java.io.DataInputStream(bais);

      long decoded = BinarySnapshotFormat.readVarLong(in);
      assertEquals(value, decoded, "VarLong encoding failed for value: " + value);
    }
  }
}
