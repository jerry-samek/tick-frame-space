# Binary Snapshot Format

This package implements a compact binary format for saving and restoring simulation snapshots.

## Format Specification

### File Structure

```
[Header: 32 bytes]
[Entity Records: variable length]
```

### Header Format (32 bytes)

| Offset | Size | Field           | Description                          |
|--------|------|-----------------|--------------------------------------|
| 0      | 4    | Magic           | 0x544B534E ("TKSN")                  |
| 4      | 4    | Version         | Format version (currently 1)         |
| 8      | 8    | Tick Count      | Current simulation tick (long)       |
| 16     | 4    | Entity Count    | Number of entities in snapshot       |
| 20     | 4    | Dimension Count | Number of spatial dimensions         |
| 24     | 8    | Reserved        | Reserved for future use (zeroed)     |

### Entity Record Format (variable length)

Each entity is serialized as a sequence of variable-length encoded values:

| Field                 | Type    | Count            | Description                    |
|-----------------------|---------|------------------|--------------------------------|
| Position coordinates  | VarLong | dimensionCount   | Spatial position (x, y, z,...) |
| Energy                | VarLong | 1                | Entity energy level            |
| Generation            | VarLong | 1                | Entity generation (depth)      |
| Momentum cost         | VarLong | 1                | Movement cost                  |
| Momentum vector       | VarLong | dimensionCount   | Movement direction             |
| Birth tick            | VarLong | 1                | Tick when entity was created   |

**Total fields per entity:** `(dimensionCount × 2) + 4`

For 3D space: 10 values per entity

## Variable-Length Encoding (VarLong)

VarLong encoding compresses small numbers into fewer bytes using continuation bits.

### Encoding Algorithm

1. **Zigzag encoding** for signed values: `encoded = (value << 1) ^ (value >> 63)`
2. **Base-128 variable-length encoding**:
   - Each byte stores 7 bits of data + 1 continuation bit
   - MSB = 1: more bytes follow
   - MSB = 0: last byte

### Size Table

| Value Range            | Bytes | Example Values           |
|------------------------|-------|--------------------------|
| 0 to 63                | 1     | 0, 10, 50                |
| 64 to 8,191            | 2     | 100, 1000, 5000          |
| 8,192 to 1,048,575     | 3     | 10000, 100000, 500000    |
| 1,048,576 to 2^28-1    | 4     | 1M, 10M                  |
| 2^28 to 2^35-1         | 5     | 100M, 1B                 |
| Larger values          | 6-9   | 10B+                     |

### Examples

```
Value:    0 → Bytes: [0x00]                     (1 byte)
Value:  127 → Bytes: [0xFE, 0x01]              (2 bytes)
Value: 1000 → Bytes: [0xD0, 0x0F]              (2 bytes)
Value:   -1 → Bytes: [0x01]                     (1 byte, zigzag)
Value: -100 → Bytes: [0xC7, 0x01]              (2 bytes, zigzag)
```

## Compression

### GZIP Compression (Default)

- Automatically applied during write
- Auto-detected during read (GZIP magic bytes: 0x1F 0x8B)
- Typical compression ratio: 40-60%
- Can be disabled via `BinarySnapshotWriter(false)`

### Size Estimates

For a 3D simulation:

| Entities | Uncompressed | Compressed (GZIP) | JSON (approx) |
|----------|--------------|-------------------|---------------|
| 1,000    | ~20 KB       | ~10 KB            | ~200 KB       |
| 100,000  | ~2 MB        | ~1 MB             | ~20 MB        |
| 1,000,000| ~20 MB       | ~10 MB            | ~200 MB       |
| 3,000,000| ~60 MB       | ~30 MB            | ~600 MB       |

**Compression factor vs JSON: ~20x smaller**

## Usage

### Saving a Snapshot

```java
// Create snapshot manager (with compression enabled)
SnapshotManager manager = new SnapshotManager(true);

// Create snapshot from current state
SimulationSnapshot snapshot = manager.createSnapshot(
    tickCount,
    entitiesRegistry,
    dimensionCount
);

// Save to file
Path file = Path.of("simulation_tick_5000.snap");
manager.save(snapshot, file);

// Estimate file size before saving
long estimatedSize = manager.estimateFileSize(snapshot);
System.out.println("Snapshot size: ~" + estimatedSize / 1024 + " KB");
```

### Loading a Snapshot

```java
SnapshotManager manager = new SnapshotManager();

// Load from file (auto-detects compression)
SimulationSnapshot snapshot = manager.load(
    Path.of("simulation_tick_5000.snap"),
    substrateModel
);

// Restore simulation state
BigInteger resumeTickCount = manager.restore(snapshot, entitiesRegistry);

System.out.println("Resumed from tick: " + resumeTickCount);
System.out.println("Loaded " + snapshot.entityCount() + " entities");
```

### Direct Stream I/O

For advanced use cases, you can work directly with streams:

```java
// Write to custom output
BinarySnapshotWriter writer = new BinarySnapshotWriter(true);
try (DataOutputStream out = new DataOutputStream(...)) {
    writer.writeSnapshot(snapshot, out);
}

// Read from custom input
BinarySnapshotReader reader = new BinarySnapshotReader();
try (DataInputStream in = new DataInputStream(...)) {
    SimulationSnapshot snapshot = reader.readSnapshot(in, substrateModel);
}
```

## File Naming Convention

Recommended naming pattern:

```
simulation_tick_{tickCount}.snap
simulation_tick_5000.snap
simulation_tick_10000.snap.gz  (explicit .gz extension if desired)
```

## Version Compatibility

**Current Version:** 1

### Version History

- **Version 1** (Initial): Basic entity serialization with VarLong encoding

### Forward Compatibility

The format reserves 8 bytes in the header for future extensions. When reading:
- Unknown versions will throw `IOException`
- Reserved bytes are currently ignored but may be used in future versions

## Performance Characteristics

### Write Performance

- **Speed**: ~100-200 MB/s (uncompressed), ~50-100 MB/s (compressed)
- **Memory**: Streams entities, low memory overhead
- **Bottleneck**: GZIP compression (can be disabled for speed)

### Read Performance

- **Speed**: ~150-300 MB/s (uncompressed), ~80-150 MB/s (compressed)
- **Memory**: Allocates collection for all entities during load
- **Bottleneck**: Entity object creation

### 3M Entity Snapshot

- Write time: ~0.5-1.0 seconds
- Read time: ~1.0-2.0 seconds
- File size: ~30-40 MB (compressed)

## Implementation Details

### Classes

- `SimulationSnapshot` - Immutable data record
- `BinarySnapshotFormat` - Format constants and VarLong utilities
- `BinarySnapshotWriter` - Serialization logic
- `BinarySnapshotReader` - Deserialization logic
- `SnapshotManager` - High-level save/load/restore API

### Thread Safety

- Writers and readers are **not thread-safe**
- Create separate instances per thread
- Snapshots themselves are immutable

### Error Handling

- Invalid magic number → `IOException("Invalid magic number")`
- Unsupported version → `IOException("Unsupported version")`
- Corrupt data → `EOFException` or `IOException`
- File I/O errors → Standard Java `IOException`

## Testing

See `BinarySnapshotTest.java` for comprehensive test cases:

- Single entity save/load
- Multiple entities (10 entities)
- VarLong encoding edge cases
- File compression validation

Run tests:
```bash
mvn test -Dtest=BinarySnapshotTest
```

## Future Enhancements

Potential improvements for future versions:

1. **Delta encoding** - Store position deltas for spatially clustered entities
2. **Dictionary compression** - Compress repeated momentum vectors
3. **Incremental snapshots** - Only store changed entities since last snapshot
4. **Parallel I/O** - Multi-threaded compression/decompression
5. **Checksums** - CRC32 or SHA256 for data integrity
6. **Index** - Random access to specific entities without full deserialization
