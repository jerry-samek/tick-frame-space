#!/usr/bin/env python3
"""
Quick test to verify the linked list bucketing implementation works correctly.
"""

import sys
from dataclasses import dataclass


@dataclass
class Entity:
    x: float
    y: float
    temporal_lag: int
    color: tuple = (100, 200, 255)


class EntityNode:
    __slots__ = ['entity', 'next']

    def __init__(self, entity, next=None):
        self.entity = entity
        self.next = next


def test_linked_list_bucketing():
    """Test that linked list bucketing works correctly"""
    print("Testing linked list bucketing implementation...")

    # Create test entities
    entities = [
        Entity(100, 100, temporal_lag=5),
        Entity(200, 200, temporal_lag=10),
        Entity(300, 300, temporal_lag=5),  # Same lag as first
        Entity(400, 400, temporal_lag=10),  # Same lag as second
        Entity(500, 500, temporal_lag=15),
    ]

    MAX_HISTORY = 100

    # Create buckets
    buckets = [None] * MAX_HISTORY

    # Bucket entities
    print(f"\nBucketing {len(entities)} entities...")
    for entity in entities:
        lag = entity.temporal_lag
        buckets[lag] = EntityNode(entity, next=buckets[lag])
        print(f"  Entity at ({entity.x}, {entity.y}) -> lag={lag}")

    # Verify bucketing
    print("\nVerifying buckets...")
    total_count = 0
    for lag in range(MAX_HISTORY):
        head = buckets[lag]
        if head:
            # Count entities in this bucket
            count = 0
            current = head
            coords = []
            while current:
                count += 1
                total_count += 1
                coords.append(f"({current.entity.x}, {current.entity.y})")
                current = current.next

            print(f"  Lag {lag}: {count} entities - {', '.join(coords)}")

    print(f"\nTotal entities bucketed: {total_count}")
    print(f"Expected: {len(entities)}")

    if total_count == len(entities):
        print("\n[PASS] All entities correctly bucketed!")

        # Test clearing
        print("\nTesting O(1) clear...")
        buckets[:] = [None] * MAX_HISTORY

        cleared_count = sum(1 for head in buckets if head is not None)
        print(f"Entities after clear: {cleared_count}")

        if cleared_count == 0:
            print("\n[PASS] Clear operation works!")
            return True
        else:
            print("\n[FAIL] Clear operation failed!")
            return False
    else:
        print("\n[FAIL] Entity count mismatch!")
        return False


if __name__ == "__main__":
    success = test_linked_list_bucketing()
    sys.exit(0 if success else 1)
