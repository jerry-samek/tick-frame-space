"""Exp 138 P1d — the DISSIPATION CHANNEL on the directed-growth substrate.
Implements PREREG_P1d.md. NOT a result until skeptic-passed.

Directed growth + re-convergence selection (as in p1_growth) PLUS the RAW 135
driven-dissipative loop that Exp 138 P1 lacked: each tick every alive element
SHEDS metabolism c as flux, the flux DILUTES one hop (row-stochastic = 1/N(r)),
and is REABSORBED (Eddington-capped). Deposit nets reab - c; below D_min an
element STARVES (a death channel the pure-removal P1 did not have). Survival is
thus coupled to the flux economy: elements where flux POOLS survive, where it
LEAKS starve.

Ablation knob `mode` (PREREG_P1d):
  none          -- no reabsorption (pure loss). CONTROL.
  scalar_flux   -- reabsorb in proportion to local flux. A.8 predicts BLIND to
                   plaquettes -> flux pools nowhere in particular.
  reconvergence -- reabsorb only where the element sits on a short cycle
                   (topology-GATED). *** SMUGGLING-RISK ARM (PREREG): it keys on
                   the neighbourhood structure it is supposed to PRODUCE; a
                   positive here is WEAKER than a scalar_flux positive and MUST
                   be reported as such. Its value is the CONTRAST with none/scalar.

Read the final LCC with the frozen two-legged gate. Hold RAW 136 §9's outcomes:
(a) low-d manifold, (b) scale-free-but-crumple, (c) explode/freeze. A negative is
a result, not a knob to tune.
"""

import math
import sys
import time
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from p1_growth import _ball, _on_cycle, _lcc  # reuse tested helpers  # noqa: E402
from plaquette_closure_probe import plaquette_Q  # noqa: E402
from boundary_layer_dim import perceived_dim  # noqa: E402
from two_legged_gate import legs, LOWD_MANIFOLDS, CV_HI  # noqa: E402
from graphs import torus2d, random_regular, binary_tree  # noqa: E402

ALIVE_CAP = 12000
RHO = 2


def grow_dissipative(params, seed, max_births=4000):
    q, W, L, p_par = params["q"], params["W_window"], params["L_cycle"], params["p_parents"]
    c, D0, cap = params["c"], params["D0"], params["cap"]
    alpha, D_min, mode = params["alpha"], params["D_min"], params["mode"]

    rng = np.random.default_rng(seed)
    live_adj = {0: set()}; birth = {0: 0}; dep = {0: D0}; alive = {0}
    n_born = 1; tick = 0
    shed_tot = reab_tot = 0.0; starve_d = select_d = 0
    traj = []; outcome = "ran"

    while n_born < max_births:
        tick += 1
        frontier = sorted(v for v in alive if tick - birth[v] <= W)
        if not frontier:
            outcome = "extinct"; break
        if len(alive) > ALIVE_CAP:
            outcome = "explosion"; break
        # --- multiplicative births ---
        for f, d in zip(frontier, rng.random(len(frontier))):
            if d >= q:
                continue
            cand = _ball(live_adj, f, RHO); parents = {f}
            want = min(p_par - 1, len(cand))
            if want > 0:
                parents |= {cand[int(i)] for i in
                            rng.choice(len(cand), size=want, replace=False)}
            nid = n_born; n_born += 1
            live_adj[nid] = set(); birth[nid] = tick; dep[nid] = D0; alive.add(nid)
            for pnt in parents:
                live_adj[nid].add(pnt); live_adj[pnt].add(nid)
        # --- re-convergence selection (same rule as P1) ---
        doomed = [v for v in alive if tick - birth[v] >= W
                  and not _on_cycle(live_adj, birth, v, L, True)]
        for v in doomed:
            select_d += 1; alive.discard(v); dep.pop(v, None)
            for u in live_adj[v]:
                live_adj[u].discard(v)
            live_adj[v] = set()
        if not alive:
            outcome = "extinct"; break
        # --- DISSIPATION LOOP: shed -> dilute -> reabsorb -> net -> starve ---
        shed = {v: c for v in alive}
        shed_tot += c * len(alive)
        phi = {}
        for v in alive:                         # dilute one hop (1/N(r))
            s = 0.0
            for u in live_adj[v]:
                s += shed[u] / (len(live_adj[u]) or 1)
            phi[v] = s
        for v in alive:
            if mode == "none":
                reab = 0.0
            elif mode == "scalar_flux":
                reab = min(cap, alpha * phi[v])
            else:  # reconvergence -- topology-gated (SMUGGLING-RISK ARM)
                on_cyc = _on_cycle(live_adj, birth, v, L, False)
                reab = min(cap, alpha * phi[v]) if on_cyc else 0.0
            reab_tot += reab
            dep[v] += reab - c
        starved = [v for v in alive if dep[v] < D_min]
        for v in starved:
            starve_d += 1; alive.discard(v); dep.pop(v, None)
            for u in live_adj[v]:
                live_adj[u].discard(v)
            live_adj[v] = set()
        traj.append(len(alive))
        if len(traj) >= 40 and len(traj) % 10 == 0 and len(alive) > 20:
            a = traj[-20:]
            if max(a) - min(a) <= 0.05 * max(a):
                outcome = "stationary"; break
    else:
        outcome = "max-births"

    adj = _lcc(live_adj, alive)
    return {"params": dict(params), "seed": seed, "outcome": outcome,
            "n_born": n_born, "final_alive": len(alive), "lcc": len(adj),
            "lcc_adj": adj, "tick": tick,
            "shed_frac": 1.0, "reab_over_shed": (reab_tot / shed_tot) if shed_tot else 0.0,
            "starve_deaths": starve_d, "select_deaths": select_d,
            "traj": traj[:: max(1, len(traj) // 60)]}


def gate_thresholds(rng):
    cal = {nm: legs(nm, g, rng) for nm, g in
           [("torus2d(30)", torus2d(30)), ("binary_tree(11)", binary_tree(11)),
            ("random_reg", random_regular(1600, 4, rng))]}
    m, t, e = cal["torus2d(30)"], cal["binary_tree(11)"], cal["random_reg"]
    return math.sqrt(m["Qg"] * max(t["Qg"], e["Qg"])), 2.0 * m["D"]


def read_gate(adj, rng, Qg_lo, D_lo):
    if len(adj) < 40:
        return "degenerate", float("nan"), float("nan"), float("nan")
    nodes = sorted(int(x) for x in rng.choice(len(adj), min(300, len(adj)), replace=False))
    _, qg, _ = plaquette_Q(adj, nodes, rng)
    D = float(np.median([perceived_dim(adj, seed=s) for s in (1, 2, 3)]))
    deg = np.array([len(a) for a in adj], float)
    cv = float(deg.std() / deg.mean()) if deg.mean() > 0 else float("nan")
    if qg >= Qg_lo and D <= D_lo and cv <= CV_HI:
        v = "MANIFOLD"
    elif cv > CV_HI:
        v = "hub/irregular"
    elif D > D_lo:
        v = "expander/crumple"
    else:
        v = "tree/sparse"
    return v, qg, D, cv


# alpha=1 => reab = min(cap, phi): reabsorption REDISTRIBUTES shed flux (one-hop
# diffusion conserves total: sum phi = sum shed), and the cap only ever REDUCES
# it, so reab/shed <= 1 (dissipative). Net dep change = min(cap,phi)-c: an element
# gains only where flux POOLS above c, starves where it leaks below c. If flux is
# blind/uniform (A.8) net ~ 0 everywhere => neutral, no selection (a pre-registered
# tell, not a manifold).
BASE = dict(q=0.5, W_window=8, L_cycle=4, p_parents=2,
            c=1.0, D0=3.0, cap=1.5, alpha=1.0, D_min=0.0)


def run_fine(Qg_lo, D_lo):
    """Fine dissipation-strength sweep: hold growth, sweep c toward extinction, to
    resolve whether cv crosses 0.60 robustly (a manifold window) or asymptotes/
    collapses (outcome b). scalar_flux only (reconvergence==scalar in the coarse
    sweep). 5 seeds/c."""
    print("FINE dissipation-strength sweep: q=0.40 fixed, cap=1.5, mode=scalar_flux, "
          "5 seeds/c.\n")
    print(f"{'c':>5}{'#ext':>6}{'#manif':>8}{'cv min..max':>15}{'Qg~':>7}{'D~':>6}"
          "   per-seed verdicts")
    for c in [1.0, 1.1, 1.2, 1.3, 1.4, 1.5]:
        res = []
        for sd in range(1, 6):
            r = grow_dissipative(dict(BASE, mode="scalar_flux", q=0.40, c=c),
                                 sd, max_births=3000)
            v, qg, D, cv = read_gate(r["lcc_adj"], np.random.default_rng(99 + sd),
                                     Qg_lo, D_lo)
            res.append((r["outcome"], v, qg, D, cv))
        ext = sum(1 for o, v, *_ in res if v == "degenerate" or o == "extinct")
        manif = sum(1 for _, v, *_ in res if v == "MANIFOLD")
        good = [(qg, D, cv) for _, v, qg, D, cv in res if v != "degenerate"]
        if good:
            cvs = [g[2] for g in good]
            cvr = f"{min(cvs):.2f}..{max(cvs):.2f}"
            qgm, Dm = np.mean([g[0] for g in good]), np.mean([g[1] for g in good])
        else:
            cvr, qgm, Dm = "--", float("nan"), float("nan")
        vs = ",".join(v[:5] for _, v, *_ in res)
        print(f"{c:>5.1f}{ext:>6}{manif:>8}{cvr:>15}{qgm:>7.2f}{Dm:>6.1f}   {vs}",
              flush=True)
    print("\nReading (PREREG_P1d): #manif ~0 with cv asymptoting >0.60 while #ext rises "
          "with c -> outcome (b) (dissipation erodes hubs but does not reach a regular "
          "manifold before collapse). A c-band with cv robustly <0.60, #manif=5, low "
          "#ext -> a genuine manifold window (a).")


def main():
    rng = np.random.default_rng(0)
    smoke = "--smoke" in sys.argv
    Qg_lo, D_lo = gate_thresholds(rng)
    print(f"P1d dissipation channel. Frozen gate: Qg_lo={Qg_lo:.3f} D_lo={D_lo:.2f}")
    print("engagement census: reab/shed (dissipation must MOVE flux, P1b lesson); "
          "starve vs select deaths.\n")
    if "--fine" in sys.argv:
        run_fine(Qg_lo, D_lo); return

    modes = ["none", "scalar_flux", "reconvergence"]
    ratios = [("drive>diss", dict(q=0.5, c=1.0)), ("drive~diss", dict(q=0.3, c=1.4))]
    seeds = [1] if smoke else [1, 2]
    mb = 1500 if smoke else 4000

    print(f"{'mode':<14}{'ratio':<11}{'seed':<5}{'outcome':<12}{'lcc':>6}"
          f"{'reab/shed':>10}{'starve':>8}{'select':>8}   gate (Qg,D,cv)")
    for mode in modes:
        for rname, rp in ratios:
            for sd in seeds:
                p = dict(BASE, mode=mode, **rp)
                t0 = time.time()
                r = grow_dissipative(p, sd, max_births=mb)
                v, qg, D, cv = read_gate(r["lcc_adj"], np.random.default_rng(99 + sd),
                                         Qg_lo, D_lo)
                print(f"{mode:<14}{rname:<11}{sd:<5}{r['outcome']:<12}{r['lcc']:>6}"
                      f"{r['reab_over_shed']:>10.3f}{r['starve_deaths']:>8}"
                      f"{r['select_deaths']:>8}   {v} ({qg:.2f},{D:.1f},{cv:.2f})"
                      f"  [{time.time()-t0:.0f}s]", flush=True)
    print("\nReading (pre-registered, PREREG_P1d): compare modes. If none/scalar_flux "
          "-> crumple/extinct and ONLY reconvergence -> MANIFOLD, the selection is "
          "topology-gated (smuggling arm) = §7 gap unclosed by flux. If scalar_flux "
          "-> MANIFOLD, that's the strong (surprising, contra-A.8) positive. If NO "
          "mode -> MANIFOLD, outcome (b): dissipation does not produce finite-d "
          "locality. Engagement: reab/shed ~0 => channel not firing (run tests nothing).")


if __name__ == "__main__":
    main()
