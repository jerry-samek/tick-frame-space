package eu.jerrysamek.tickspace.model.exportimport;

import java.io.DataInput;
import java.io.DataOutput;
import java.io.IOException;
import java.math.BigInteger;

/**
 * Binary snapshot format specification and utilities.
 * <p>
 * Format:
 * [Header: 32 bytes]
 * - Magic: "TKSN" (4 bytes)
 * - Version: 1 (4 bytes)
 * - Tick count (8 bytes - long)
 * - Entity count (4 bytes - int)
 * - Dimension count (4 bytes - int)
 * - Reserved (8 bytes)
 * <p>
 * [Entity Records: variable length]
 * Each entity:
 * - Position vector (dimensionCount × varLong)
 * - Energy (varLong)
 * - Generation (varLong)
 * - Momentum cost (varLong)
 * - Momentum vector (dimensionCount × varLong)
 * - Birth tick (varLong)
 * <p>
 * VarLong encoding:
 * - 1 byte for values 0-127
 * - 2-9 bytes for larger values (continuation bit encoding)
 */
public class BinarySnapshotFormat {

  // Magic number "TKSN" (Tick Space Snapshot)
  public static final int MAGIC = 0x544B534E;

  // Format version
  public static final int VERSION = 1;

  // Header size in bytes
  public static final int HEADER_SIZE = 32;

  /**
   * Writes a variable-length encoded long value.
   * Uses continuation bit encoding - most significant bit indicates more bytes follow.
   *
   * @param out   output stream
   * @param value long value to encode
   */
  public static void writeVarLong(DataOutput out, long value) throws IOException {
    // Handle negative values by zigzag encoding
    var encoded = (value << 1) ^ (value >> 63);

    while ((encoded & ~0x7FL) != 0) {
      out.writeByte((byte) ((encoded & 0x7F) | 0x80));
      encoded >>>= 7;
    }
    out.writeByte((byte) (encoded & 0x7F));
  }

  /**
   * Reads a variable-length encoded long value.
   */
  public static long readVarLong(DataInput in) throws IOException {
    var result = 0L;
    var shift = 0;
    byte b;

    do {
      b = in.readByte();
      result |= (long) (b & 0x7F) << shift;
      shift += 7;
    } while ((b & 0x80) != 0);

    // Decode zigzag
    return (result >>> 1) ^ -(result & 1);
  }

  /**
   * Writes a BigInteger as a variable-length encoded long.
   * Assumes value fits in long range.
   */
  public static void writeBigInteger(DataOutput out, BigInteger value) throws IOException {
    writeVarLong(out, value.longValue());
  }

  /**
   * Reads a BigInteger from variable-length encoded long.
   */
  public static BigInteger readBigInteger(DataInput in) throws IOException {
    return BigInteger.valueOf(readVarLong(in));
  }

  /**
   * Estimates the size in bytes for a varLong encoding.
   */
  public static int varLongSize(long value) {
    var encoded = (value << 1) ^ (value >> 63);
    var bytes = 1;
    while ((encoded & ~0x7FL) != 0) {
      bytes++;
      encoded >>>= 7;
    }
    return bytes;
  }

  private BinarySnapshotFormat() {
  }
}
