package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntitiesRegistry;
import eu.jerrysamek.tickspace.model.entity.Momentum;
import eu.jerrysamek.tickspace.model.entity.SingleEntityModel;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;

import java.io.IOException;
import java.math.BigInteger;
import java.nio.file.Path;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class BinarySnapshotTest {

  @TempDir
  Path tempDir;

  private SubstrateModel substrateModel;
  private EntitiesRegistry registry;
  private SnapshotManager snapshotManager;

  @BeforeEach
  void setUp() {
    registry = new EntitiesRegistry();
    substrateModel = new SubstrateModel(3, registry);
    snapshotManager = new SnapshotManager(true);
  }

  @Test
  @DisplayName("Should save and load snapshot with single entity")
  void testSaveAndLoadSingleEntity() throws IOException {
    // Given: Create a simple entity
    var position = new Position(Vector.of(BigInteger.valueOf(10), BigInteger.valueOf(20), BigInteger.valueOf(30)));
    var momentum = new Momentum(BigInteger.valueOf(5), Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO));
    var entity = new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(),
        BigInteger.valueOf(100),
        position,
        BigInteger.valueOf(50),
        BigInteger.ZERO,
        momentum
    );

    registry.addEntity(position, entity);
    BigInteger tickCount = BigInteger.valueOf(1000);

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
    assertEquals(BigInteger.valueOf(50), loadedEntity.getEnergy().value());
    assertEquals(BigInteger.valueOf(5), loadedEntity.getMomentum().cost());
  }

  @Test
  @DisplayName("Should handle multiple entities")
  void testMultipleEntities() throws IOException {
    // Given: Create multiple entities
    for (int i = 0; i < 10; i++) {
      var position = new Position(Vector.of(
          BigInteger.valueOf(i),
          BigInteger.valueOf(i * 2),
          BigInteger.valueOf(i * 3)
      ));
      var momentum = new Momentum(BigInteger.valueOf(i + 1), Vector.of(BigInteger.ONE, BigInteger.ZERO, BigInteger.ZERO));
      var entity = new SingleEntityModel(
          substrateModel,
          UUID.randomUUID(),
          BigInteger.valueOf(i),
          position,
          BigInteger.valueOf(i * 10),
          BigInteger.ZERO,
          momentum
      );
      registry.addEntity(position, entity);
    }

    // When: Save and load
    var snapshot = snapshotManager.createSnapshot(BigInteger.valueOf(500), registry, 3);
    Path snapshotFile = tempDir.resolve("multi_snapshot.bin");
    snapshotManager.save(snapshot, snapshotFile);

    var loadedSnapshot = snapshotManager.load(snapshotFile, substrateModel);

    // Then: All entities loaded
    assertEquals(10, loadedSnapshot.entityCount());
    assertEquals(BigInteger.valueOf(500), loadedSnapshot.tickCount());
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
