"""Phase 1a landscape probe: uniform refinement (Arm U) x memory-resonance rules -> measured d.

For each coordinateless edge rule, build the leaf connection-graph at increasing depth and
measure intrinsic dimension (battery). Pre-registered question/verdict per PREREG A.6:
  WIN-band  : d_s in [2.2,3.2], finite & stable, loops>0.3, flat Ricci, separated from nulls
  CIRCLE    : d_s -> ~1
  HYPERBOLIC: d_s grows without bound / diameter ~ log N
  K_N       : mean degree -> N
"""
import sys, os, json
import numpy as np
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from coordinateless import RULES, build_graph, measure_conserved
from battery import hausdorff_dim, spectral_dim, loop_density, ricci_summary


def diam_estimate(g, k=8, seed=0):
    rng = np.random.default_rng(seed); nodes = list(g.nodes()); d = 0
    for s in rng.choice(len(nodes), size=min(k, len(nodes)), replace=False):
        lengths = nx.single_source_shortest_path_length(g, nodes[s])
        if lengths:
            d = max(d, max(lengths.values()))
    return int(d)


def classify(row):
    if row["mean_deg"] > 0.5 * row["n"]:
        return "K_N"
    ds = row["d_spectral"]
    if ds != ds:
        return "?"
    if ds < 1.6:
        return "CIRCLE/low-d"
    if 2.2 <= ds <= 3.2:
        return "WIN-band(check stability+nulls)"
    if ds > 4.0 or row["diam"] <= max(2, int(np.log2(row["n"]) + 1)):
        return "HYPERBOLIC/expander"
    return "intermediate"


def main():
    DEPTHS = [8, 9, 10, 11]   # 256..2048 leaves
    assert measure_conserved(8), "measure not conserved"
    results = []
    print(f"{'rule':28s} {'depth':>5s} {'N':>6s} {'deg':>6s} {'diam':>5s} "
          f"{'d_s':>6s} {'d_H':>6s} {'loops':>7s} {'ricci':>7s}  flavor")
    for name, fn in RULES.items():
        for depth in DEPTHS:
            g = build_graph(depth, fn)
            if not nx.is_connected(g):
                comp = max(nx.connected_components(g), key=len)
                g = g.subgraph(comp).copy()
                conn = f"(largest cc {g.number_of_nodes()})"
            else:
                conn = ""
            N = g.number_of_nodes(); E = g.number_of_edges()
            row = {
                "rule": name, "depth": depth, "n": N,
                "mean_deg": 2 * E / N if N else 0,
                "diam": diam_estimate(g),
                "d_spectral": spectral_dim(g),
                "d_hausdorff": hausdorff_dim(g),
                "loop_density": loop_density(g),
                "ricci": ricci_summary(g)["median"],
            }
            row["flavor"] = classify(row)
            results.append(row)
            print(f"{name:28s} {depth:>5d} {N:>6d} {row['mean_deg']:>6.1f} {row['diam']:>5d} "
                  f"{row['d_spectral']:>6.2f} {row['d_hausdorff']:>6.2f} "
                  f"{row['loop_density']:>7.2f} {row['ricci']:>+7.2f}  {row['flavor']} {conn}")
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "results", "phase1a_coordinateless.json"), "w") as f:
        json.dump(results, f, indent=2)

    print("\n=== finite-size read (does d_s stay finite & ~constant, or drift?) ===")
    for name in RULES:
        ds = [r["d_spectral"] for r in results if r["rule"] == name]
        trend = "->".join(f"{x:.2f}" for x in ds)
        print(f"  {name:28s} d_s by depth: {trend}")


if __name__ == "__main__":
    main()
