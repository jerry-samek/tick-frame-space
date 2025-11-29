package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.entity.Momentum;
import eu.jerrysamek.tickspace.model.entity.SingleEntityModel;
import eu.jerrysamek.tickspace.model.substrate.Position;
import eu.jerrysamek.tickspace.model.substrate.SubstrateModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.io.BufferedInputStream;
import java.io.DataInput;
import java.io.DataInputStream;
import java.io.IOException;
import java.io.InputStream;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.ArrayList;
import java.util.List;
import java.util.UUID;
import java.util.zip.GZIPInputStream;

/**
 * Reads simulation snapshots from compact binary format.
 * Automatically detects GZIP compression.
 */
public class BinarySnapshotReader {

  /**
   * Reads snapshot from file.
   */
  public SimulationSnapshot read(Path path, SubstrateModel substrateModel) throws IOException {
    try (InputStream fileIn = Files.newInputStream(path)) {
      // Try to detect GZIP magic bytes
      BufferedInputStream buffered = new BufferedInputStream(fileIn);
      buffered.mark(2);
      int magic1 = buffered.read();
      int magic2 = buffered.read();
      buffered.reset();

      boolean isGzipped = (magic1 == 0x1f && magic2 == 0x8b);
      InputStream in = isGzipped ? new GZIPInputStream(buffered) : buffered;

      try (DataInputStream dataIn = new DataInputStream(in)) {
        return readSnapshot(dataIn, substrateModel);
      }
    }
  }

  /**
   * Reads snapshot from input stream.
   */
  public SimulationSnapshot readSnapshot(DataInput in, SubstrateModel substrateModel) throws IOException {
    // Read and validate the header
    SnapshotHeader header = readHeader(in);

    // Read entities
    List<EntityModel> entities = new ArrayList<>(header.entityCount);
    for (int i = 0; i < header.entityCount; i++) {
      entities.add(readEntity(in, header.dimensionCount, header.tickCount, substrateModel));
    }

    return new SimulationSnapshot(
        FlexInteger.of(header.tickCount),
        header.dimensionCount,
        entities
    );
  }

  private SnapshotHeader readHeader(DataInput in) throws IOException {
    int magic = in.readInt();
    if (magic != BinarySnapshotFormat.MAGIC) {
      throw new IOException(String.format("Invalid magic number: 0x%08X (expected 0x%08X)",
          magic, BinarySnapshotFormat.MAGIC));
    }

    int version = in.readInt();
    if (version != BinarySnapshotFormat.VERSION) {
      throw new IOException(String.format("Unsupported version: %d (expected %d)",
          version, BinarySnapshotFormat.VERSION));
    }

    long tickCount = in.readLong();
    int entityCount = in.readInt();
    int dimensionCount = in.readInt();
    in.readLong(); // Skip reserved bytes

    return new SnapshotHeader(tickCount, entityCount, dimensionCount);
  }

  private EntityModel readEntity(DataInput in, int dimensionCount, long currentTick,
                                 SubstrateModel substrateModel) throws IOException {
    // Read position vector
    FlexInteger[] posComponents = new FlexInteger[dimensionCount];
    for (int i = 0; i < dimensionCount; i++) {
      posComponents[i] = BinarySnapshotFormat.readBigInteger(in);
    }
    Position position = new Position(Vector.of(posComponents));

    // Read energy
    FlexInteger energy = BinarySnapshotFormat.readBigInteger(in);

    // Read generation
    FlexInteger generation = BinarySnapshotFormat.readBigInteger(in);

    // Read momentum cost
    FlexInteger momentumCost = BinarySnapshotFormat.readBigInteger(in);

    // Read momentum vector
    FlexInteger[] momComponents = new FlexInteger[dimensionCount];
    for (int i = 0; i < dimensionCount; i++) {
      momComponents[i] = BinarySnapshotFormat.readBigInteger(in);
    }
    Momentum momentum = new Momentum(momentumCost, Vector.of(momComponents));

    // Read birth tick
    FlexInteger birthTick = BinarySnapshotFormat.readBigInteger(in);

    // Reconstruct entity
    return new SingleEntityModel(
        substrateModel,
        UUID.randomUUID(), // Generate new UUID
        birthTick,
        position,
        generation,
        momentum
    );
  }

  private record SnapshotHeader(long tickCount, int entityCount, int dimensionCount) {
  }
}
