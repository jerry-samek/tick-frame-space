import sys
from collections import defaultdict
from tickspace_snapshot import read_snapshot

def process_snapshot(snapshot_file, max_entities=None):
    """
    Process binary snapshot and compute shell-wise statistics.
    Groups entities by Manhattan radius and computes energy, depth, and momentum stats.
    """

    # Aggregates per shell (Manhattan radius)
    shell_stats = defaultdict(lambda: {
        "count": 0,
        "energy_sum": 0,
        "energy_min": None,
        "energy_max": None,
        "depth_sum": 0,
        "momentum_hist": defaultdict(int)
    })

    snapshot = read_snapshot(snapshot_file)

    for i, entity in enumerate(snapshot.entities):
        if max_entities and i >= max_entities:
            break

        x, y, z = entity.position
        energy = entity.energy
        depth = entity.generation
        momentum = tuple(entity.momentum_vector)

        # Manhattan radius
        r = abs(x) + abs(y) + abs(z)

        stats = shell_stats[r]
        stats["count"] += 1
        stats["energy_sum"] += energy
        stats["depth_sum"] += depth

        if stats["energy_min"] is None or energy < stats["energy_min"]:
            stats["energy_min"] = energy
        if stats["energy_max"] is None or energy > stats["energy_max"]:
            stats["energy_max"] = energy

        stats["momentum_hist"][momentum] += 1

    # Print summary
    for r in sorted(shell_stats.keys()):
        s = shell_stats[r]
        avg_energy = s["energy_sum"] // s["count"]
        avg_depth = s["depth_sum"] // s["count"] if s["count"] > 0 else 0
        print(f"Shell {r}: count={s['count']}, "
              f"avg_energy={avg_energy}, min={s['energy_min']}, max={s['energy_max']}, "
              f"avg_depth={avg_depth}, unique_momenta={len(s['momentum_hist'])}")

    return shell_stats

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python reducer.py snapshot.json [max_entities]")
        sys.exit(1)

    json_file = sys.argv[1]
    max_entities = int(sys.argv[2]) if len(sys.argv) > 2 else None

    process_snapshot(json_file, max_entities)
