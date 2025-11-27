import json
import csv
import math
import sys
import numpy as np
from collections import Counter

# Load frame
with open(sys.argv[1], "r") as f:
    data = json.load(f)

N = len(data)

generations = [e["generation"] for e in data]
energies = [e["energy"]["energy"] for e in data]
momentum_costs = [e["momentum"]["cost"] for e in data]
positions = [e["position"]["coordinates"] for e in data]
momentum_vectors = [e["momentum"]["vector"] for e in data]

# --- Basic stats ---
stats = {
    "total_entities": int(N),
    "generation": {
        "avg": float(np.mean(generations)),
        "min": int(np.min(generations)),
        "max": int(np.max(generations)),
    },
    "energy": {
        "total": float(np.sum(energies)),
        "avg": float(np.mean(energies)),
        "min": float(np.min(energies)),
        "max": float(np.max(energies)),
        "variance": float(np.var(energies)),
        "entropy": float(-sum((c/N)*math.log((c/N), 2) for c in Counter(energies).values())),
    },
    "momentum": {
        "avg_cost": float(np.mean(momentum_costs)),
        "avg_vector": [float(x) for x in np.mean(momentum_vectors, axis=0)],
        "variance_magnitude": float(np.var([math.sqrt(sum(v_i**2 for v_i in v)) for v in momentum_vectors])),
    },
    "position": {
        "bounding_box": {
            "x": {"min": int(min(p[0] for p in positions)), "max": int(max(p[0] for p in positions))},
            "y": {"min": int(min(p[1] for p in positions)), "max": int(max(p[1] for p in positions))},
            "z": {"min": int(min(p[2] for p in positions)), "max": int(max(p[2] for p in positions))},
        },
        "radial_density": {
            "avg_radius": float(np.mean([math.sqrt(x**2+y**2+z**2) for x,y,z in positions])),
        }
    }
}

# --- Save JSON ---
with open("stats.json", "w") as f:
    json.dump(stats, f, indent=4)

# --- Save CSV ---
with open("stats.csv", "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["Metric", "Value"])
    writer.writerow(["Total Entities", stats["total_entities"]])
    writer.writerow(["Average Generation", stats["generation"]["avg"]])
    writer.writerow(["Min Generation", stats["generation"]["min"]])
    writer.writerow(["Max Generation", stats["generation"]["max"]])
    writer.writerow(["Total Energy", stats["energy"]["total"]])
    writer.writerow(["Average Energy", stats["energy"]["avg"]])
    writer.writerow(["Min Energy", stats["energy"]["min"]])
    writer.writerow(["Max Energy", stats["energy"]["max"]])
    writer.writerow(["Energy Variance", stats["energy"]["variance"]])
    writer.writerow(["Energy Entropy", stats["energy"]["entropy"]])
    writer.writerow(["Average Momentum Cost", stats["momentum"]["avg_cost"]])
    writer.writerow(["Average Momentum Vector", stats["momentum"]["avg_vector"]])
    writer.writerow(["Momentum Variance Magnitude", stats["momentum"]["variance_magnitude"]])
    writer.writerow(["Bounding Box X", stats["position"]["bounding_box"]["x"]])
    writer.writerow(["Bounding Box Y", stats["position"]["bounding_box"]["y"]])
    writer.writerow(["Bounding Box Z", stats["position"]["bounding_box"]["z"]])
    writer.writerow(["Average Radius", stats["position"]["radial_density"]["avg_radius"]])

print("Statistics saved to stats.json and stats.csv")
