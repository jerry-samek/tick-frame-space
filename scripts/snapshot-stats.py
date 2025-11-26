import json
import sys
from collections import defaultdict

def process_snapshot(json_file, max_entities=None):
    """
    Stream through a large JSON snapshot of entities and compute shell-wise statistics.
    Assumes each entity has fields: x, y, z, energy, depth, momentum (list of ints).
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

    with open(json_file, "r") as f:
        data = json.load(f)

    for i, e in enumerate(data):
        if max_entities and i >= max_entities:
            break

        x, y, z = e['position']['coordinates']
        energy = int(e["energy"])
        depth = int(e.get("depth", 0))
        momentum = tuple(e.get("momentum", []))

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
