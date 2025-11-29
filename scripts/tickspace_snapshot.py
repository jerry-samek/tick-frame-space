"""
Tick Space Binary Snapshot Reader

Python library for reading binary snapshots created by the Java simulation.
Compatible with the binary format described in the exportimport package README.

Usage:
    from tickspace_snapshot import SnapshotReader

    reader = SnapshotReader()
    snapshot = reader.read('simulation_tick_5000.snap')

    print(f"Tick: {snapshot.tick_count}")
    print(f"Entities: {len(snapshot.entities)}")

    for entity in snapshot.entities:
        print(f"Position: {entity.position}, Energy: {entity.energy}")
"""

import gzip
import struct
from dataclasses import dataclass
from typing import List, BinaryIO
from pathlib import Path


# Constants from BinarySnapshotFormat.java
MAGIC = 0x544B534E  # "TKSN"
VERSION = 1
HEADER_SIZE = 32


@dataclass
class Entity:
    """Represents a single entity from the snapshot."""
    position: List[int]
    energy: int
    generation: int
    momentum_cost: int
    momentum_vector: List[int]
    birth_tick: int


@dataclass
class Snapshot:
    """Represents a complete simulation snapshot."""
    tick_count: int
    dimension_count: int
    entities: List[Entity]

    @property
    def entity_count(self):
        return len(self.entities)


class VarLongDecoder:
    """Decoder for variable-length long integers with zigzag encoding."""

    @staticmethod
    def read_varlong(stream: BinaryIO) -> int:
        """
        Reads a variable-length encoded long value.

        Uses continuation bit encoding where MSB = 1 means more bytes follow.
        Values are zigzag encoded to handle negatives efficiently.
        """
        result = 0
        shift = 0

        while True:
            byte_val = stream.read(1)
            if not byte_val:
                raise EOFError("Unexpected end of stream while reading varlong")

            b = byte_val[0]
            result |= (b & 0x7F) << shift
            shift += 7

            if (b & 0x80) == 0:
                break

        # Decode zigzag: (n >>> 1) ^ -(n & 1)
        return (result >> 1) ^ -(result & 1)


class SnapshotReader:
    """Reads binary snapshots created by the Java simulation."""

    def __init__(self):
        self.decoder = VarLongDecoder()

    def read(self, filepath: str) -> Snapshot:
        """
        Reads a snapshot from a file.

        Automatically detects and handles GZIP compression.

        Args:
            filepath: Path to the snapshot file

        Returns:
            Snapshot object containing all data

        Raises:
            ValueError: If file has invalid magic number or unsupported version
            IOError: If file cannot be read
        """
        path = Path(filepath)

        with open(path, 'rb') as f:
            # Check for GZIP magic bytes (0x1F 0x8B)
            magic_bytes = f.read(2)
            f.seek(0)

            is_gzipped = (magic_bytes[0] == 0x1F and magic_bytes[1] == 0x8B)

            if is_gzipped:
                with gzip.open(f, 'rb') as gz:
                    return self._read_snapshot(gz)
            else:
                return self._read_snapshot(f)

    def _read_snapshot(self, stream: BinaryIO) -> Snapshot:
        """Reads snapshot from a binary stream."""
        header = self._read_header(stream)
        entities = self._read_entities(stream, header)

        return Snapshot(
            tick_count=header['tick_count'],
            dimension_count=header['dimension_count'],
            entities=entities
        )

    def _read_header(self, stream: BinaryIO) -> dict:
        """
        Reads and validates the 32-byte header.

        Header format:
        - Magic: 4 bytes (0x544B534E "TKSN")
        - Version: 4 bytes (int, currently 1)
        - Tick count: 8 bytes (long)
        - Entity count: 4 bytes (int)
        - Dimension count: 4 bytes (int)
        - Reserved: 8 bytes (unused)
        """
        header_bytes = stream.read(HEADER_SIZE)
        if len(header_bytes) < HEADER_SIZE:
            raise IOError("File too short, invalid snapshot")

        # Unpack header: >IIqII8x (big-endian)
        # I = unsigned int (4 bytes)
        # q = long long (8 bytes)
        # 8x = 8 bytes padding (reserved)
        magic, version, tick_count, entity_count, dimension_count = struct.unpack(
            '>IIqII8x', header_bytes
        )

        if magic != MAGIC:
            raise ValueError(f"Invalid magic number: 0x{magic:08X} (expected 0x{MAGIC:08X})")

        if version != VERSION:
            raise ValueError(f"Unsupported version: {version} (expected {VERSION})")

        return {
            'tick_count': tick_count,
            'entity_count': entity_count,
            'dimension_count': dimension_count
        }

    def _read_entities(self, stream: BinaryIO, header: dict) -> List[Entity]:
        """Reads all entity records from the stream."""
        entities = []
        entity_count = header['entity_count']
        dimension_count = header['dimension_count']

        for i in range(entity_count):
            entity = self._read_entity(stream, dimension_count)
            entities.append(entity)

        return entities

    def _read_entity(self, stream: BinaryIO, dimension_count: int) -> Entity:
        """
        Reads a single entity record.

        Entity format:
        - Position vector: dimension_count × VarLong
        - Energy: VarLong
        - Generation: VarLong
        - Momentum cost: VarLong
        - Momentum vector: dimension_count × VarLong
        - Birth tick: VarLong
        """
        # Read position vector
        position = [self.decoder.read_varlong(stream) for _ in range(dimension_count)]

        # Read scalar fields
        energy = self.decoder.read_varlong(stream)
        generation = self.decoder.read_varlong(stream)
        momentum_cost = self.decoder.read_varlong(stream)

        # Read momentum vector
        momentum_vector = [self.decoder.read_varlong(stream) for _ in range(dimension_count)]

        # Read birth tick
        birth_tick = self.decoder.read_varlong(stream)

        return Entity(
            position=position,
            energy=energy,
            generation=generation,
            momentum_cost=momentum_cost,
            momentum_vector=momentum_vector,
            birth_tick=birth_tick
        )


def read_snapshot(filepath: str) -> Snapshot:
    """
    Convenience function to read a snapshot file.

    Args:
        filepath: Path to the snapshot file

    Returns:
        Snapshot object

    Example:
        snapshot = read_snapshot('simulation_tick_5000.snap')
        print(f"Loaded {snapshot.entity_count} entities from tick {snapshot.tick_count}")
    """
    reader = SnapshotReader()
    return reader.read(filepath)


if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python tickspace_snapshot.py <snapshot_file>")
        print("\nExample:")
        print("  python tickspace_snapshot.py simulation_tick_5000.snap")
        sys.exit(1)

    # Read and display snapshot info
    snapshot = read_snapshot(sys.argv[1])

    print("=" * 60)
    print("Tick Space Snapshot Info")
    print("=" * 60)
    print(f"Tick Count:      {snapshot.tick_count:,}")
    print(f"Dimensions:      {snapshot.dimension_count}D")
    print(f"Entity Count:    {snapshot.entity_count:,}")
    print("=" * 60)

    # Show first few entities
    print("\nFirst 5 entities:")
    for i, entity in enumerate(snapshot.entities[:5]):
        print(f"\nEntity {i+1}:")
        print(f"  Position:       {entity.position}")
        print(f"  Energy:         {entity.energy}")
        print(f"  Generation:     {entity.generation}")
        print(f"  Momentum Cost:  {entity.momentum_cost}")
        print(f"  Momentum Vec:   {entity.momentum_vector}")
        print(f"  Birth Tick:     {entity.birth_tick}")

    if snapshot.entity_count > 5:
        print(f"\n... and {snapshot.entity_count - 5:,} more entities")
