"""Exp 137 Phase 1b — skeptic-mandated distinguishing tests (run BEFORE RESULTS).

The skeptic pass on the gate run (see RESULTS_phase1b.md, Skeptic review)
found the gate's registered PASS evidentially near-empty and demanded:

  T-A  instrument-settings sweep (multi-seed analog on a deterministic
       substrate): kick magnitude x horizon x pattern sign (+ off-ring kick).
       Does the CUBE>FLAT dpr_sub gap survive every cell?
  T-B  adversarial abstract-graph surrogate (decisive): the same spectral
       readout on the two fixtures' ABSTRACT ring graphs (C8+2 chords vs cube
       graph), no lattice, no renewal rule. Ordering reproduced => M reads
       adjacency structure; the word "embedding" must be dropped.
  T-C  exhaustive fixture enumeration (resolves PREREG_phase1b.md sec. 3's
       "resolve first" clause properly): ALL closed self-avoiding K-cycles in
       Z^3 up to isometry x cyclic shift x reversal, K in {4,6,8,10};
       sustains() on every class; M on every survivor. Decides whether
       FLAT_K8/CUBE_K8 exhaust K=8 and whether dpr_sub sorts by 3D-extent or
       by chord count across a wider family.
  T-D  do-nothing baseline: raw unperturbed series (R0) and per-channel
       shuffle surrogate on the K8 pair — does anything separate WITHOUT the
       perturbation-divergence machinery?
  T-E  reconcile the two observables: print both 8x8 M-correlation matrices
       and full eigenspectra; state mechanistically why dpr_sub separates and
       mds_dim90c does not.
"""

import json
import sys
import time
from itertools import product
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "134_pattern_coherence"))
sys.path.insert(0, str(HERE))

from fixtures import F3_K8_RING                                  # noqa: E402
from multipattern import tick_multi                              # noqa: E402
from substrate import face_neighbors                             # noqa: E402
from phase1_t6 import (                                           # noqa: E402
    graph_impulse_corr, limit_cycle_phases, observables,
    r0_limitcycle, ring_window, shuffle_null)
from phase1_t6_embed import CUBE_K8, sustains                    # noqa: E402
from phase1b_gate import bootstrap_m, readout_m, separation      # noqa: E402
from readout import dpr_sub, dpr_raw                             # noqa: E402
from phase0b_deconfound import mds_dim90c                        # noqa: E402

PAIR = {"FLAT_K8": F3_K8_RING, "CUBE_K8": CUBE_K8}


# ---------- shared helpers ----------

def ring_graph(cycle):
    """Induced face-adjacency graph among ring cells, as index adjacency."""
    idx = {c: i for i, c in enumerate(cycle)}
    adj = [[] for _ in cycle]
    for c, i in idx.items():
        for nb in face_neighbors(c):
            j = idx.get(nb)
            if j is not None:
                adj[i].append(j)
    return adj

def chord_count(cycle):
    adj = ring_graph(cycle)
    edges = sum(len(a) for a in adj) // 2
    return edges - len(cycle)

def planarity_rank(cycle):
    m = np.array(cycle, float)
    return int(np.linalg.matrix_rank(m - m.mean(axis=0)))


# ---------- T-A: instrument-settings sweep ----------

def readout_m_generic(cycle, sign=1, mag=1, w_factor=6, offring=False):
    K = len(cycle)
    W = w_factor * K
    window = ring_window(cycle)
    template = limit_cycle_phases(cycle, sign)
    ring = set(cycle)
    if offring:
        collar = sorted({nb for c in cycle for nb in face_neighbors(c)} - ring)
        kicks = [(c, K) for c in collar]
    else:
        kicks = [(s, sgn * mag) for s in cycle for sgn in (+1, -1)]
    samples = []
    for phi in range(K):
        for cell, dv in kicks:
            per = dict(template[phi])
            per[cell] = per.get(cell, 0) + dv
            if per[cell] == 0:
                del per[cell]
            for t in range(1, W + 1):
                try:
                    tick_multi(per)
                except Exception:  # noqa: BLE001 (wedged/dead: divergence still defined)
                    pass
                ref = template[(phi + t) % K]
                samples.append([per.get(c, 0) - ref.get(c, 0) for c in window])
    return np.array(samples, dtype=float)


def t_a():
    print("=== T-A: instrument-settings sweep (gap must hold same-sign, >=2sd, "
          "in every cell) ===", flush=True)
    rows = []
    for sign, mag, wf in product((+1, -1), (1, 2, 3, 8), (3, 6, 12)):
        st = {}
        for name, cyc in PAIR.items():
            s = readout_m_generic(cyc, sign=sign, mag=mag, w_factor=wf)
            st[name] = bootstrap_m(s, seed=abs(hash((name, sign, mag, wf))) % 2**32)
        gap = st["CUBE_K8"]["dpr_sub_mean"] - st["FLAT_K8"]["dpr_sub_mean"]
        z = separation(st["CUBE_K8"], st["FLAT_K8"])
        rows.append({"sign": sign, "mag": mag, "w_factor": wf,
                     "gap": gap, "z": z})
        print(f"  sign={sign:+d} mag={mag} W={wf}K: "
              f"CUBE={st['CUBE_K8']['dpr_sub_mean']:.3f} "
              f"FLAT={st['FLAT_K8']['dpr_sub_mean']:.3f} "
              f"gap={gap:+.3f} z={z:.1f}", flush=True)
    # off-ring +K kick, default sign/horizon
    st = {}
    for name, cyc in PAIR.items():
        s = readout_m_generic(cyc, offring=True)
        st[name] = bootstrap_m(s, seed=abs(hash((name, "offring"))) % 2**32)
    gap = st["CUBE_K8"]["dpr_sub_mean"] - st["FLAT_K8"]["dpr_sub_mean"]
    z = separation(st["CUBE_K8"], st["FLAT_K8"])
    rows.append({"sign": 1, "mag": "offring+K", "w_factor": 6, "gap": gap, "z": z})
    print(f"  offring +K   W=6K: CUBE={st['CUBE_K8']['dpr_sub_mean']:.3f} "
          f"FLAT={st['FLAT_K8']['dpr_sub_mean']:.3f} gap={gap:+.3f} z={z:.1f}")
    stable = all(r["gap"] > 0 and r["z"] >= 2.0 for r in rows)
    print(f"  T-A verdict: {'STABLE (gap same-sign >=2sd in all cells)' if stable else 'COLLAPSES somewhere'}")
    return {"cells": rows, "stable": stable}


# ---------- T-B: abstract-graph surrogate ----------

def t_b():
    print("\n=== T-B: abstract ring-graph surrogate (no lattice, no rule) ===",
          flush=True)
    out = {}
    for name, cyc in PAIR.items():
        adj = ring_graph(cyc)
        o = graph_impulse_corr(adj, list(range(len(adj))))
        out[name] = o
        print(f"  {name} ring graph (chords={chord_count(cyc)}, "
              f"degrees={[len(a) for a in adj]}): dpr_sub={o['dpr_sub']:.3f}")
    reproduced = out["CUBE_K8"]["dpr_sub"] > out["FLAT_K8"]["dpr_sub"]
    print(f"  T-B verdict: ordering CUBE>FLAT "
          f"{'REPRODUCED on abstract graphs -> M reads adjacency structure, not embedding' if reproduced else 'NOT reproduced -> dynamics add non-graph content'}")
    return {"readings": {k: v["dpr_sub"] for k, v in out.items()},
            "ordering_reproduced": bool(reproduced)}


# ---------- T-C: exhaustive enumeration ----------

_STEPS = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]

def _signed_perms():
    ops = []
    for perm in ((0, 1, 2), (0, 2, 1), (1, 0, 2), (1, 2, 0), (2, 0, 1), (2, 1, 0)):
        for sx, sy, sz in product((1, -1), repeat=3):
            ops.append((perm, (sx, sy, sz)))
    return ops

_OPS = _signed_perms()

def _apply(op, c):
    perm, sgn = op
    return (sgn[0] * c[perm[0]], sgn[1] * c[perm[1]], sgn[2] * c[perm[2]])

def canonical(cycle):
    """Min over isometry x cyclic shift x reversal of the origin-anchored tuple."""
    K = len(cycle)
    best = None
    for op in _OPS:
        cells = [_apply(op, c) for c in cycle]
        for rev in (cells, cells[::-1]):
            for s in range(K):
                rot = rev[s:] + rev[:s]
                o = rot[0]
                t = tuple((c[0] - o[0], c[1] - o[1], c[2] - o[2]) for c in rot)
                if best is None or t < best:
                    best = t
    return best

def enum_cycles(K):
    """All closed self-avoiding face-adjacent K-cycles through the origin,
    deduped up to isometry x cyclic shift x reversal."""
    classes = {}
    path = [(0, 0, 0)]
    used = {(0, 0, 0)}

    def dfs():
        if len(path) == K:
            last = path[-1]
            if abs(last[0]) + abs(last[1]) + abs(last[2]) == 1:
                classes.setdefault(canonical(path), list(path))
            return
        c = path[-1]
        remaining = K - len(path)
        for dx, dy, dz in _STEPS:
            n = (c[0] + dx, c[1] + dy, c[2] + dz)
            if n in used:
                continue
            if abs(n[0]) + abs(n[1]) + abs(n[2]) > remaining:  # can't close
                continue
            used.add(n)
            path.append(n)
            dfs()
            path.pop()
            used.remove(n)

    dfs()
    return list(classes.values())

def t_c():
    print("\n=== T-C: exhaustive enumeration of closed K-cycles up to isometry ===",
          flush=True)
    out = {}
    for K in (4, 6, 8, 10):
        t0 = time.time()
        classes = enum_cycles(K)
        survivors = []
        for cyc in classes:
            ok, _ = sustains(cyc)
            if ok:
                survivors.append(cyc)
        out[str(K)] = {"classes": len(classes), "survivors": []}
        print(f"  K={K}: {len(classes)} cycle classes, "
              f"{len(survivors)} sustain ({time.time()-t0:.1f}s)", flush=True)
        for cyc in survivors:
            st = bootstrap_m(readout_m(cyc), seed=abs(hash(tuple(cyc))) % 2**32)
            rec = {"cells": cyc, "rank": planarity_rank(cyc),
                   "chords": chord_count(cyc),
                   "degrees": sorted(len(a) for a in ring_graph(cyc)),
                   "dpr_sub": st["dpr_sub_mean"], "sd": st["dpr_sub_sd"]}
            out[str(K)]["survivors"].append(rec)
            print(f"    survivor rank={rec['rank']} chords={rec['chords']} "
                  f"degrees={rec['degrees']} dpr_sub={rec['dpr_sub']:.3f}"
                  f"+/-{rec['sd']:.3f} cells={cyc}")
    return out


# ---------- T-D: do-nothing baseline ----------

def t_d():
    print("\n=== T-D: do-nothing baseline (R0 raw series; shuffled M) ===",
          flush=True)
    out = {}
    rng = np.random.default_rng(7)
    for name, cyc in PAIR.items():
        r0 = observables(r0_limitcycle(cyc))
        m = readout_m(cyc)
        msh = observables(shuffle_null(m, rng))
        out[name] = {"R0_dpr_sub": r0["dpr_sub"], "Mshuf_dpr_sub": msh["dpr_sub"]}
        print(f"  {name}: R0 dpr_sub={r0['dpr_sub']:.3f}  "
              f"shuffled-M dpr_sub={msh['dpr_sub']:.3f}")
    d_r0 = abs(out["CUBE_K8"]["R0_dpr_sub"] - out["FLAT_K8"]["R0_dpr_sub"])
    d_sh = abs(out["CUBE_K8"]["Mshuf_dpr_sub"] - out["FLAT_K8"]["Mshuf_dpr_sub"])
    print(f"  |R0 gap|={d_r0:.3f}  |shuffled-M gap|={d_sh:.3f} "
          f"(M gap was 0.478)")
    return {"per_fixture": out, "r0_gap": d_r0, "shuffled_gap": d_sh}


# ---------- T-E: reconcile the observables ----------

def t_e():
    print("\n=== T-E: why does dpr_sub separate while mds_dim90c does not? ===",
          flush=True)
    out = {}
    for name, cyc in PAIR.items():
        s = readout_m(cyc)
        v = s.var(axis=0)
        act = np.where(v > 1e-9)[0]
        c = np.corrcoef(s[:, act].T)
        eig = np.sort(np.linalg.eigvalsh(c))[::-1]
        out[name] = {"eigs": eig.tolist(), "dpr_raw": dpr_raw(c),
                     "dpr_sub": dpr_sub(c), "mds_dim90c": mds_dim90c(c)}
        print(f"  {name}: eigenspectrum {np.round(eig, 3)}")
        print(f"    dpr_raw={dpr_raw(c):.3f} dpr_sub={dpr_sub(c):.3f} "
              f"mds_dim90c={mds_dim90c(c)}")
        print(f"    |corr| matrix:\n{np.round(np.abs(c), 2)}")
    return out


def main():
    t0 = time.time()
    res = {"T_E": t_e(), "T_D": t_d(), "T_B": t_b(), "T_A": t_a(), "T_C": t_c()}
    res["wall_clock_sec"] = round(time.time() - t0, 1)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "phase1b_skeptic_tests.json").write_text(
        json.dumps(res, indent=2, default=float))
    print(f"\nwall clock: {res['wall_clock_sec']}s")


if __name__ == "__main__":
    main()
