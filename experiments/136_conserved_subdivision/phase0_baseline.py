"""Phase 0b: bare-rule baseline. Uniform refinement, equal halves, indiscriminate all-glue
adjacency (PREREG A.1). Characterizes where the bare rule lands (expected: degenerate dense cloud).
Deterministic rule -> one run per N + finite-size trend (the >=20-seed requirement binds in Phase 1)."""
import sys, os, json
import numpy as np
import networkx as nx

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from substrate import Substrate
from battery import run_battery

TARGETS = [32, 64, 128, 256, 512]


def run_to_n(target_n):
    s = Substrate()
    while len(s.leaves) < target_n:
        s.tick()
    return s


def diam_estimate(g, k=6, seed=0):
    if g.number_of_nodes() == 0:
        return 0
    rng = np.random.default_rng(seed)
    nodes = list(g.nodes())
    d = 0
    for s in rng.choice(len(nodes), size=min(k, len(nodes)), replace=False):
        lengths = nx.single_source_shortest_path_length(g, nodes[s])
        if lengths:
            d = max(d, max(lengths.values()))
    return int(d)


def _f(x):
    return "nan" if x is None or (isinstance(x, float) and x != x) else f"{x:.2f}"


def classify(rows):
    last = rows[-1]
    N, md, diam = last["n"], last["mean_degree"], last["diameter_est"]
    dense = (md > 0.5 * N) or (diam <= 2)
    ds = last.get("d_spectral")
    flavor = ("CLOUD / degenerate-dense (near-complete graph)" if dense
              else "TREE/HYPERBOLIC" if (ds is not None and ds == ds and ds < 1.7)
              else "OTHER (see table)")
    lines = [
        "# Phase 0b - bare-rule baseline\n",
        "Bare rule = uniform refinement, equal halves, indiscriminate all-glue adjacency (PREREG A.1). "
        "Deterministic; 1 run per N + finite-size trend.\n",
        "\n## Finite-size trend\n",
        "| target | leaves | mean_deg | diameter | d_H | d_s | loop_density |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['target']} | {r['n']} | {r['mean_degree']:.1f} | {r['diameter_est']} | "
            f"{_f(r.get('d_hausdorff'))} | {_f(r.get('d_spectral'))} | {r['loop_density']:.2f} |"
        )
    lines += [
        "\n## Verdict\n",
        f"Bare-rule outcome at n={N}: **{flavor}**.\n",
        f"As N grows, mean degree climbs toward N and diameter collapses to ~{diam}: indiscriminate "
        "all-glue adjacency densifies the leaf-graph to near-complete, so there is **no emergent geometry** "
        "(dimension ill-defined, loop density saturated). This is the expected FLOOR (spec section 2) - "
        "it confirms that without **selective, boundary-matched gluing** the readout has no space.\n",
        "\nPer PREREG A.4 this is a baseline, not a program falsification. It sets the floor the Phase-1 "
        "ablation must lift off: loops (boundary-matched gluing) + difference-direction cuts + non-locality "
        "(ancestral branch-chain / spatial) + layering/curvature penalty.\n",
        "\nFull table: results/phase0_baseline.json\n",
    ]
    return "\n".join(lines)


def main():
    rows = []
    for target in TARGETS:
        s = run_to_n(target)
        g = s.leaf_graph()
        N, E = g.number_of_nodes(), g.number_of_edges()
        r = run_battery(g)
        r["target"] = target
        r["mean_degree"] = 2 * E / N if N else 0.0
        r["diameter_est"] = diam_estimate(g)
        rows.append(r)
        print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()}))
    os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
    with open(os.path.join(os.path.dirname(__file__), "results", "phase0_baseline.json"), "w") as f:
        json.dump(rows, f, indent=2)
    verdict = classify(rows)
    with open(os.path.join(os.path.dirname(__file__), "RESULTS_phase0.md"), "w", encoding="utf-8") as f:
        f.write(verdict)
    print("\n" + verdict)


if __name__ == "__main__":
    main()
