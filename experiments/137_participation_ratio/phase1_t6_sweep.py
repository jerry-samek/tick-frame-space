"""Exp 137 Phase 1 — T6 robustness sweep (pre-empts skeptic artifact challenge).

Tests whether the T6 FAIL (R2 rank strictly K-monotone) is an artifact of
perturbation magnitude or horizon. Structural prediction: for a SURVIVOR the
divergence field is eventually period-K (heal-to-phase-shift) or the pattern
DISSOLVES (no longer a survivor) — either way rank stays <= K-1 and monotone;
no (mag, W) in the survivor regime should break K-monotonicity.
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from substrate import face_neighbors
from rule import bootstrap
from multipattern import tick_multi
from fixtures import F1_K4_SQUARE, F2_K6_PERIMETER, F3_K8_RING
from readout import dpr_sub
from phase1_t6 import observables, ring_window, limit_cycle_phases

FIX = {"K4": F1_K4_SQUARE, "K6": F2_K6_PERIMETER, "K8": F3_K8_RING}


def r2_damage(cycle, mag, w_factor, sign=1):
    K = len(cycle)
    W = w_factor * K
    window = ring_window(cycle)
    phases = limit_cycle_phases(cycle, sign)
    samples = []
    dissolved = 0
    total = 0
    for phi in range(K):
        base = phases[phi]
        for s in cycle:
            for sgn in (+1, -1):
                total += 1
                ref = dict(base)
                per = dict(base)
                per[s] = per.get(s, 0) + sgn * mag
                if per[s] == 0:
                    del per[s]
                for _ in range(W):
                    tick_multi(ref)
                    tick_multi(per)
                    samples.append([per.get(c, 0) - ref.get(c, 0) for c in window])
                # dissolution check: perturbed pattern lost cells vs reference
                if len([c for c in per if per[c] != 0]) < K:
                    dissolved += 1
    return np.array(samples, float), dissolved / total


def main():
    print(f"{'fixture':<8}{'mag':>4}{'Wfac':>6}{'dpr_sub':>10}{'n_act':>7}{'dissolv%':>10}")
    for name, cyc in FIX.items():
        for mag in (1, 2, 3, 5):
            for wf in (6, 20):
                s, diss = r2_damage(cyc, mag, wf)
                o = observables(s)
                print(f"{name:<8}{mag:>4}{wf:>6}{o['dpr_sub']:>10.3f}"
                      f"{o['n_active']:>7}{100*diss:>9.1f}%", flush=True)

    # decisive check: is the K-ladder monotone at EVERY (mag, wf)?
    print("\n--- K-monotonicity of R2 dpr_sub ladder at each (mag, wf) ---")
    broken = 0
    for mag in (1, 2, 3, 5):
        for wf in (6, 20):
            ladder = []
            for name in ("K4", "K6", "K8"):
                s, _ = r2_damage(FIX[name], mag, wf)
                ladder.append(observables(s)["dpr_sub"])
            mono = ladder[0] < ladder[1] < ladder[2]
            if not mono:
                broken += 1
            print(f"mag={mag} wf={wf}: ladder={[round(x,2) for x in ladder]} "
                  f"strictly_K_monotone={mono}", flush=True)
    print(f"\nladders broken (non-monotone): {broken}/8  "
          f"=> FAIL is {'ARTIFACT (breakable)' if broken else 'STRUCTURAL (unbreakable in survivor regime)'}")


if __name__ == "__main__":
    main()
