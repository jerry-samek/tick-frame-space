"""Exp 137 Phase 1 — T6 applicability gate (PREREG_phase1.md).

Certifies whether a readout regime lets the Phase-0 observer-rank instrument
be applied to Exp 134 survivor patterns without reading their trivial period-K.

Regimes:
  R0 — raw limit-cycle tap series (the NULL the gate must reject; reads period).
  R2 — perturbation-response / damage field (PRIMARY; deterministic analog of
       the noise-driven calibration regime, via fluctuation-dissipation).

Gates:
  T6.1  non-degeneracy of R2 on K4.
  T6.2a coupling-existence surrogate (per-channel shuffle): real must differ.
  T6.2b period-decoupling K-ladder: R0 gives a strictly-K-monotone ladder;
        R2 must NOT reproduce that trivial ladder to escape the period confound.
  T6.3  calibration transfer: R2 impulse-response on the Phase-0 graph fixtures
        must reproduce Phase 0's signed separation (fluctuation-dissipation).
"""

import json
import sys
import time
from pathlib import Path

import numpy as np
from scipy import sparse

HERE = Path(__file__).resolve().parent
EXP134 = HERE.parents[0] / "134_pattern_coherence"
sys.path.insert(0, str(EXP134))
sys.path.insert(0, str(HERE))

from substrate import face_neighbors            # noqa: E402  (Exp 134)
from rule import bootstrap                       # noqa: E402  (Exp 134)
from multipattern import tick_multi              # noqa: E402  (Exp 134)
from fixtures import (                            # noqa: E402  (Exp 134)
    F1_K4_SQUARE, F2_K6_PERIMETER, F3_K8_RING)

from readout import dpr_raw, dpr_sub             # noqa: E402  (Exp 137 Phase 0)
from phase0b_deconfound import mds_dim90c        # noqa: E402  (Exp 137 Phase 0b)
from dynamics import walk_matrix                 # noqa: E402
from graphs import torus3d, random_regular, sample_bundle  # noqa: E402

FIXTURES = {"K4": F1_K4_SQUARE, "K6": F2_K6_PERIMETER, "K8": F3_K8_RING}
W_FACTOR = 6          # perturbation-response horizon = W_FACTOR * K ticks
VAR_EPS = 1e-9        # channel is "active" if its sample variance exceeds this


# ---------- shared observable extraction ----------

def observables(samples):
    """samples: (n_samples, n_channels). Drop zero-variance channels, then
    report rank observables on the active-channel correlation matrix."""
    v = samples.var(axis=0)
    active = np.where(v > VAR_EPS)[0]
    if active.size < 2:
        return {"n_active": int(active.size), "dpr_raw": float("nan"),
                "dpr_sub": float("nan"), "mds_dim90c": float("nan"),
                "frac_nonzero": float(np.mean(np.any(np.abs(samples) > 0, axis=1)))}
    c = np.corrcoef(samples[:, active].T)
    c = np.nan_to_num(c, nan=0.0)
    return {"n_active": int(active.size), "dpr_raw": dpr_raw(c),
            "dpr_sub": dpr_sub(c), "mds_dim90c": mds_dim90c(c),
            "frac_nonzero": float(np.mean(np.any(np.abs(samples) > 0, axis=1)))}


def shuffle_null(samples, rng):
    """Per-channel independent permutation across samples: destroys cross-channel
    coupling, preserves each channel's marginal. (T6.2a coupling surrogate.)"""
    out = samples.copy()
    for j in range(out.shape[1]):
        out[:, j] = out[rng.permutation(out.shape[0]), j]
    return out


# ---------- Exp 134 regimes ----------

def limit_cycle_phases(cycle, sign=1):
    cv = {}
    bootstrap(cv, cycle, sign)
    return [dict(cv) for _ in _advance(cv, len(cycle))]


def _advance(cv, n):
    for _ in range(n):
        snap = dict(cv)
        tick_multi(cv)
        yield snap


def ring_window(cycle):
    cells = set(cycle)
    for c in cycle:
        cells.update(face_neighbors(c))
    return sorted(cells)


def r0_limitcycle(cycle, sign=1):
    """R0: tap gamma on the ring cells over one long run (period-K series)."""
    K = len(cycle)
    cv = {}
    bootstrap(cv, cycle, sign)
    T = W_FACTOR * K + K
    series = []
    for _ in range(T):
        series.append([cv.get(c, 0) for c in cycle])
        tick_multi(cv)
    return np.array(series[K:], dtype=float)  # drop first period


def r2_damage(cycle, sign=1, mag=1):
    """R2: divergence field of perturbed vs reference copies over the ensemble
    of (phase, ring-site, sign) perturbations."""
    K = len(cycle)
    W = W_FACTOR * K
    window = ring_window(cycle)
    phases = limit_cycle_phases(cycle, sign)
    samples = []
    for phi in range(K):
        base = phases[phi]
        for s in cycle:
            for sgn in (+1, -1):
                ref = dict(base)
                per = dict(base)
                per[s] = per.get(s, 0) + sgn * mag
                if per[s] == 0:
                    del per[s]
                for _ in range(W):
                    tick_multi(ref)
                    tick_multi(per)
                    samples.append([per.get(c, 0) - ref.get(c, 0) for c in window])
    return np.array(samples, dtype=float)


# ---------- T6.3 graph transfer (fluctuation-dissipation) ----------

def graph_impulse_corr(adj, taps, lam=0.99, W=200):
    """R2 on a graph: shared-noise perturbed-minus-reference divergence is the
    deterministic impulse response lam^t P^t e_s. Accumulate the centered
    tap-covariance over all sites s and times t (== the Phase-0 noise-driven
    covariance C = sum_t lam^{2t} P^t P^tT, restricted to taps)."""
    P = walk_matrix(adj)
    P = 0.5 * (sparse.identity(P.shape[0], format="csr") + P)  # lazy walk
    n = len(adj)
    sel = np.zeros((len(taps), n))
    sel[np.arange(len(taps)), taps] = 1.0
    R = sel                      # 64 x N  == tap rows of P^0
    s1 = np.zeros(len(taps))
    s2 = np.zeros((len(taps), len(taps)))
    ncol = 0
    for t in range(1, W + 1):
        R = R @ P                # 64 x N == tap rows of P^t
        block = (lam ** t) * R   # 64 x N, columns are samples over sites s
        s1 += block.sum(axis=1)
        s2 += block @ block.T
        ncol += block.shape[1]
    mean = s1 / ncol
    cov = s2 / ncol - np.outer(mean, mean)
    d = np.sqrt(np.clip(np.diag(cov), 1e-30, None))
    c = cov / np.outer(d, d)
    return {"dpr_raw": dpr_raw(c), "dpr_sub": dpr_sub(c), "mds_dim90c": mds_dim90c(c)}


# ---------- gate evaluation ----------

def main():
    t0 = time.time()
    rng = np.random.default_rng(0)
    out = {"prereg": "PREREG_phase1.md", "regimes": {}, "graph_transfer": {},
           "gates": {}}

    # --- R0 and R2 on K4/K6/K8 (T6.2b ladder) + T6.1 + T6.2a ---
    r0, r2, r0_sh, r2_sh = {}, {}, {}, {}
    _r2_samples = {}
    for name, cyc in FIXTURES.items():
        s0 = r0_limitcycle(cyc)
        s2 = r2_damage(cyc)
        _r2_samples[name] = s2
        r0[name] = observables(s0)
        r2[name] = observables(s2)
        r0_sh[name] = observables(shuffle_null(s0, rng))
        r2_sh[name] = observables(shuffle_null(s2, rng))
        print(f"{name}: R0 dpr_sub={r0[name]['dpr_sub']:.3f} "
              f"(shuf {r0_sh[name]['dpr_sub']:.3f}) | "
              f"R2 dpr_sub={r2[name]['dpr_sub']:.3f} "
              f"(shuf {r2_sh[name]['dpr_sub']:.3f}) "
              f"n_active={r2[name]['n_active']} "
              f"frac_nz={r2[name]['frac_nonzero']:.3f}", flush=True)
    out["regimes"] = {"R0": r0, "R2": r2, "R0_shuffled": r0_sh, "R2_shuffled": r2_sh}

    # --- T6.3 graph transfer ---
    for gname, gen in (("lattice3d", lambda r: torus3d(12)),
                       ("expander6", lambda r: random_regular(1728, 6, r))):
        grng = np.random.default_rng(0)
        adj = gen(grng)
        _, taps, _ = sample_bundle(adj, 64, 6, grng)
        out["graph_transfer"][gname] = graph_impulse_corr(adj, taps)
        print(f"T6.3 {gname}: {out['graph_transfer'][gname]}", flush=True)

    # ---- gate decisions (pre-registered) ----
    g = {}
    # T6.1: R2 non-degenerate on K4
    g["T6_1_nondegenerate"] = (r2["K4"]["n_active"] >= 2
                               and np.isfinite(r2["K4"]["dpr_sub"]))
    # T6.2a: REGISTERED criterion — real differs from shuffle surrogate by >= 2
    # pooled sd. (Corrected from an earlier ad-hoc >1.0 constant that never
    # computed an sd — skeptic finding.) 100 surrogate shuffles per fixture.
    N_SURR = 100
    t62a_z = {}
    for k, cyc in FIXTURES.items():
        s = _r2_samples[k]
        surro = [observables(shuffle_null(s, rng))["dpr_sub"] for _ in range(N_SURR)]
        m, sd = float(np.mean(surro)), float(np.std(surro))
        z = abs(r2[k]["dpr_sub"] - m) / sd if sd > 0 else float("inf")
        t62a_z[k] = z
    g["T6_2a_z"] = t62a_z
    g["T6_2a_coupling"] = all(z >= 2.0 for z in t62a_z.values())
    # NOTE (recorded): T6.2a as operationalized is trivially passable — a full
    # per-channel shuffle destroys ALL cross-channel correlation, so any coupled
    # signal (incl. a period-confounded one) "differs from surrogate." It tests
    # coupling-existence, NOT period-escape. The substantive period-escape test
    # is T6.2b, which PREREG filed as evidence (not a gate). See RESULTS_phase1.md.
    g["T6_2a_is_hollow"] = True
    # T6.2b: R0 ladder is strictly K-monotone (the trivial signature)
    r0_ladder = [r0[k]["dpr_sub"] for k in ("K4", "K6", "K8")]
    r2_ladder = [r2[k]["dpr_sub"] for k in ("K4", "K6", "K8")]
    g["R0_ladder"] = r0_ladder
    g["R2_ladder"] = r2_ladder
    g["R0_strictly_K_monotone"] = r0_ladder[0] < r0_ladder[1] < r0_ladder[2]
    # R2 escapes the period confound IFF its rank ladder is NOT strictly
    # K-monotone. Strict monotonicity in K == "D_PR = f(K)" == the period/size
    # signature (a 1-cycle's cell count equals its period), regardless of any
    # constant offset from R0. (Corrected from an earlier offset-tolerant
    # criterion that spuriously passed a visibly monotone ladder.)
    r2_mono = r2_ladder[0] < r2_ladder[1] < r2_ladder[2]
    g["R2_strictly_K_monotone"] = r2_mono
    g["T6_2b_R2_escapes_period"] = not r2_mono
    # T6.3: R2 impulse reproduces Phase-0 signed separation (expander6 > lattice3d)
    gt = out["graph_transfer"]
    g["T6_3_transfer_sign"] = (gt["expander6"]["dpr_sub"] > gt["lattice3d"]["dpr_sub"])
    g["T6_3_detail"] = {"expander6_dpr_sub": gt["expander6"]["dpr_sub"],
                        "lattice3d_dpr_sub": gt["lattice3d"]["dpr_sub"],
                        "phase0_ref": "expander6 62.24 > lattice3d 59.13"}

    # PREREG §2 pass condition is exactly T6.1 ∧ T6.2a ∧ T6.3 (T6.2b is
    # "reported as evidence", NOT a gate — skeptic finding; earlier code wrongly
    # promoted it). Evaluated faithfully here:
    g["T6_PASS_registered"] = bool(g["T6_1_nondegenerate"] and g["T6_2a_coupling"]
                                   and g["T6_3_transfer_sign"])
    # ...but the registered pass is HOLLOW (T6_2a_is_hollow) and the substantive
    # period-escape test (T6.2b) FAILS (R2 strictly K-monotone) and is anyway
    # UNIDENTIFIABLE on this fixture set (all three fixtures are coplanar rings,
    # so period ≡ size ≡ embedding; the CUBE_K8 follow-up (phase1_t6_embed.py)
    # shows fixed-K embedding shifts rank by only ~0.4). Honest verdict:
    g["T6_VERDICT"] = "INCONCLUSIVE — registered pass is hollow; gate mis-designed; see RESULTS_phase1.md"
    out["gates"] = g
    out["wall_clock_sec"] = round(time.time() - t0, 1)

    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "phase1_t6.json").write_text(json.dumps(out, indent=2, default=float))

    print("\n=== T6 gate ===")
    for k, v in g.items():
        if not isinstance(v, dict):
            print(f"  {k}: {v}")
    print(f"\nT6_PASS_registered = {g['T6_PASS_registered']}  ->  {g['T6_VERDICT']}")


if __name__ == "__main__":
    main()
