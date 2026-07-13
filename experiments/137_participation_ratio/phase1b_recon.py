"""Exp 137 Phase 1b — R1 feasibility reconnaissance (informs PREREG_phase1b.md).

Questions before designing the R1 gate:
  (Q1) Can Exp 134's deterministic integer rule be driven stochastically without
       (a) dissolving the survivor or (b) spawning spurious growth (NAND-cloud)?
  (Q2) Is the inside-consistent readout (one noisy trajectory, tap-channel
       covariance — NO cross-universe subtraction) non-degenerate?
  (Q3) Does it distinguish the two same-K embeddings (CUBE_K8 vs FLAT_K8)?
       The property a redesigned Test-3 gate must have.

R1 driving: jitter magnitudes of EXISTING pattern cells only (never create
foreign nonzero cells -> cannot spawn junk). Read gamma at the K ring cells over
one trajectory; covariance -> dpr_sub, mds_dim90c. One universe, no god-view.
"""

import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from rule import bootstrap
from multipattern import tick_multi
from fixtures import F3_K8_RING
from readout import dpr_sub
from phase1_t6 import observables
from phase1_t6_embed import CUBE_K8, sustains

FIX = {"FLAT_K8": F3_K8_RING, "CUBE_K8": CUBE_K8}


def r1_drive(cycle, seed, p=0.05, T=4000, burn=500, sign=1):
    """One noisy trajectory: jitter existing cells' magnitudes by +/-1 w.p. p,
    then apply the deterministic tick. Return (tap series over ring cells,
    fraction of ticks with all K ring cells alive)."""
    rng = np.random.default_rng(seed)
    cv = {}
    bootstrap(cv, cycle, sign)
    taps = list(cycle)
    K = len(cycle)
    series = []
    alive_ticks = 0
    spawned = 0
    for t in range(burn + T):
        for c in list(cv.keys()):
            if rng.random() < p:
                cv[c] += 1 if rng.random() < 0.5 else -1
                if cv[c] == 0:
                    del cv[c]
        try:
            tick_multi(cv)
        except Exception:  # noqa: BLE001
            pass
        if t >= burn:
            series.append([cv.get(c, 0) for c in taps])
            ring_alive = sum(1 for c in taps if cv.get(c, 0) != 0)
            if ring_alive == K:
                alive_ticks += 1
            # spawn check: cells nonzero that are NOT ring cells
            spawned = max(spawned, sum(1 for c in cv if c not in set(taps) and cv[c] != 0))
    return np.array(series, float), alive_ticks / T, spawned


def memory_subtraction_bootstrap(B=200, seed=0):
    """M readout: R2's divergence field IS inside-consistent for a PERIODIC
    survivor — the 'reference' is the observer's own memorized period (the
    pattern repeats, so its unperturbed continuation == its remembered past),
    NOT a god-view counterfactual universe. Bootstrap over the perturbation
    ensemble to get the fixed-K embedding-separation margin (the redesigned
    gate's decisive statistic)."""
    from phase1_t6 import r2_damage, observables as _obs
    rng = np.random.default_rng(seed)

    def boot(cyc):
        s = r2_damage(cyc)
        n = s.shape[0]
        vals = [_obs(s[rng.integers(0, n, n)])["dpr_sub"] for _ in range(B)]
        return float(np.mean(vals)), float(np.std(vals))

    mf, sf = boot(F3_K8_RING)
    mc, sc = boot(CUBE_K8)
    pooled = np.sqrt((sf**2 + sc**2) / 2)
    z = abs(mc - mf) / pooled if pooled > 0 else float("inf")
    print("\n=== memory-subtraction readout: fixed-K embedding separation ===")
    print(f"FLAT_K8 dpr_sub = {mf:.3f} +/- {sf:.3f}")
    print(f"CUBE_K8 dpr_sub = {mc:.3f} +/- {sc:.3f}")
    print(f"separation = {z:.2f} pooled-sd ({'SEPARATES' if z >= 2 else 'below 2sd'})")


def main():
    print("sustains check:", {n: sustains(c)[0] for n, c in FIX.items()})
    print("\n### Q1/Q2: R1 continuous-noise driving (expected: dissolves fragile ring) ###")
    for p in (0.02, 0.05, 0.10, 0.20):
        print(f"\n--- p={p} ---")
        rows = {}
        for name, cyc in FIX.items():
            vals = []
            alive = []
            spawn = []
            for seed in range(8):
                s, af, sp = r1_drive(cyc, seed, p=p)
                o = observables(s)
                vals.append(o["dpr_sub"])
                alive.append(af)
                spawn.append(sp)
            rows[name] = (np.mean(vals), np.std(vals), np.mean(alive), max(spawn))
            print(f"  {name}: dpr_sub={np.mean(vals):.3f}+/-{np.std(vals):.3f} "
                  f"ring_alive_frac={np.mean(alive):.3f} max_spawned_cells={max(spawn)}")
        (mc, sc, _, _) = rows["CUBE_K8"]
        (mf, sf, _, _) = rows["FLAT_K8"]
        pooled = np.sqrt((sc**2 + sf**2) / 2)
        z = abs(mc - mf) / pooled if pooled > 0 else float("inf")
        print(f"  => CUBE vs FLAT separation = {z:.2f} pooled-sd "
              f"({'SEPARATES' if z >= 2 else 'does not separate'})")

    memory_subtraction_bootstrap()


if __name__ == "__main__":
    main()
