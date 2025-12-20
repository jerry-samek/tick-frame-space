package eu.jerrysamek.tickspace.model.exportimport;

import eu.jerrysamek.tickspace.model.entity.EntityModel;
import eu.jerrysamek.tickspace.model.substrate.Vector;
import eu.jerrysamek.tickspace.model.util.FlexInteger;

import java.io.BufferedOutputStream;
import java.io.DataOutput;
import java.io.DataOutputStream;
import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.util.zip.GZIPOutputStream;

/**
 * Writes simulation snapshots to compact binary format.
 * Supports optional GZIP compression for additional space savings.
 */
public class BinarySnapshotWriter {

  private final boolean compress;

  public BinarySnapshotWriter(boolean compress) {
    this.compress = compress;
  }

  public BinarySnapshotWriter() {
    this(true); // Default: compress
  }

  /**
   * Writes snapshot to file.
   */
  public void write(SimulationSnapshot snapshot, Path path) throws IOException {
    try (var fileOut = Files.newOutputStream(path)) {
      var out = compress ? new GZIPOutputStream(fileOut) : fileOut;
      try (var dataOut = new DataOutputStream(new BufferedOutputStream(out))) {
        writeSnapshot(snapshot, dataOut);
      }
    }
  }

  /**
   * Writes snapshot to output stream.
   */
  public void writeSnapshot(SimulationSnapshot snapshot, DataOutput out) throws IOException {
    // Write header
    writeHeader(snapshot, out);

    // Write entities
    for (var entity : snapshot.entities()) {
      writeEntity(entity, snapshot.tickCount(), snapshot.dimensionCount(), out);
    }
  }

  private void writeHeader(SimulationSnapshot snapshot, DataOutput out) throws IOException {
    out.writeInt(BinarySnapshotFormat.MAGIC);
    out.writeInt(BinarySnapshotFormat.VERSION);
    out.writeLong(snapshot.tickCount().longValue());
    out.writeInt(snapshot.entityCount());
    out.writeInt(snapshot.dimensionCount());
    out.writeLong(0); // Reserved
  }

  private void writeEntity(EntityModel entity, FlexInteger tick, int dimensionCount, DataOutput out) throws IOException {
    // Position vector
    var position = entity.getPosition().coordinates();
    for (var i = 0; i < dimensionCount; i++) {
      BinarySnapshotFormat.writeBigInteger(out, position.get(i).toBigInteger());
    }

    // Energy
    BinarySnapshotFormat.writeBigInteger(out, entity.getEnergy(tick).toBigInteger());

    // Generation
    BinarySnapshotFormat.writeBigInteger(out, entity.getGeneration().toBigInteger());

    // Momentum cost
    BinarySnapshotFormat.writeBigInteger(out, entity.getMomentum().cost().toBigInteger());

    // Momentum vector
    Vector momentum = entity.getMomentum().vector();
    for (var i = 0; i < dimensionCount; i++) {
      BinarySnapshotFormat.writeBigInteger(out, momentum.get(i).toBigInteger());
    }

    // Birth tick
    BinarySnapshotFormat.writeBigInteger(out, entity.tickOfBirth().toBigInteger());
  }

  /**
   * Estimates the compressed size of a snapshot.
   */
  public long estimateSize(SimulationSnapshot snapshot) {
    long size = BinarySnapshotFormat.HEADER_SIZE;

    // Estimate per entity: ~7 values × ~2 bytes average (varLong for small values)
    // Position (3D) + Energy + Generation + MomentumCost + Momentum(3D) + BirthTick
    var fieldsPerEntity = snapshot.dimensionCount() * 2 + 4;
    size += (long) snapshot.entityCount() * fieldsPerEntity * 2; // Conservative estimate

    // GZIP typically achieves 50-70% compression on this data
    return compress ? size / 2 : size;
  }
}
