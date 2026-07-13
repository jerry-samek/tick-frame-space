"""Exp 138 P0 — resume after the 2026-07-11 01:15 kill (machine sleep).

Runs are seed-deterministic, so the 32 finals recorded in
results_p0_console.txt are exact; this script re-runs ONLY the 18 missing
(J, seed) cells, merges, evaluates gate G-P0 exactly as registered, and
writes results/p0.json. The splice is declared in RESULTS_p0.md.
"""

import json
import re
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from p0_condensation import LADDER, N_SEEDS, _cell  # noqa: E402

CONSOLE = HERE / "results_p0_console.txt"
PAT = re.compile(r"J=([0-9.]+) seed=(\d+): cls=(\w+) e_hat=([-0-9.]+) "
                 r"sq/edge=([0-9.]+) drift=([+-][0-9.]+) \(([0-9.]+)s\)")


def recovered():
    out = {}
    for line in CONSOLE.read_text().splitlines():
        m = PAT.search(line)
        if m:
            J, seed = float(m.group(1)), int(m.group(2))
            out[(J, seed)] = {
                "coupling": J, "seed": seed, "recovered_from_console": True,
                "checkpoints": [{"sweep": 1500, "cls": m.group(3),
                                 "e_hat": float(m.group(4)),
                                 "squares_per_edge": float(m.group(5)),
                                 "energy_drift": float(m.group(6))}],
                "wall_sec": float(m.group(7))}
    return out


def main():
    t0 = time.time()
    rec = recovered()
    print(f"recovered {len(rec)} finals from console", flush=True)
    missing = [(J, 1000 + s) for J in LADDER for s in range(N_SEEDS)
               if (J, 1000 + s) not in rec]
    print(f"running {len(missing)} missing cells: "
          f"{sorted(set(J for J, _ in missing))}", flush=True)
    with Pool(16) as pool:
        fresh = pool.map(_cell, missing)
    runs = list(rec.values()) + fresh
    g = {}
    for J in LADDER:
        finals = [r["checkpoints"][-1]["cls"] for r in runs
                  if r["coupling"] == J]
        g[f"poly_count_J{J}"] = finals.count("poly")
    n_low = g[f"poly_count_J{LADDER[0]}"]
    g["exists_condensing_J"] = any(g[f"poly_count_J{J}"] >= 8 for J in LADDER)
    g["low_J_stays_exp"] = (N_SEEDS - n_low) >= 8
    g["G_P0_PASS"] = bool(g["exists_condensing_J"] and g["low_J_stays_exp"])
    print("\n=== gate G-P0 ===")
    for k, v in g.items():
        print(f"  {k}: {v}")
    print(f"wall clock: {round(time.time() - t0, 1)}s")
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p0.json").write_text(json.dumps(
        {"prereg": "PREREG_P0.md", "resume_note": "32/50 finals recovered "
         "from console after 2026-07-11 kill; 18 re-run (seed-deterministic)",
         "runs": runs, "gate": g}, indent=2, default=float))


if __name__ == "__main__":
    main()
