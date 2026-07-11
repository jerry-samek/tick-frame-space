"""Exp 138 Phase P1b — multiplicative growth + re-convergence selection
(PREREG_P1b.md; supersedes the smoke-invalidated PREREG_P1.md rule).

Growth: every frontier element spawns w.p. q per tick (multiplicative).
Selection: past age W, survive only on a short cycle CONTAINING A YOUNGER
element (the future must re-converge onto you). Simultaneous decay pass per
tick; dirty-set re-verification (radius L-2 around edge changes) as an
exact optimization. Explosion cap and extinction are their own outcome
categories. All stochastic choices: seeded rng over id-sorted candidates.
"""

import json
import sys
import time
from collections import deque
from multiprocessing import Pool
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from instrument import fit_exponent, shell_counts  # noqa: E402

MAX_BIRTHS = 40000
ALIVE_CAP = 30000
CHECK_BIRTHS = 1000


def _ball(live_adj, start, radius):
    """Alive elements within distance <= radius of start (excl start)."""
    seen = {start}
    frontier = [start]
    out = []
    for _ in range(radius):
        nxt = []
        for v in frontier:
            for u in live_adj[v]:
                if u not in seen:
                    seen.add(u)
                    nxt.append(u)
                    out.append(u)
        frontier = nxt
    return sorted(out)


def _descends(u, v, parents_of, max_depth=8):
    """Is u a descendant of v (ancestor walk up to max_depth)? Conservative
    approximation for the T3 non-descendant selector: deeper descendants
    count as non-descendant (biases TOWARD survival)."""
    frontier = {u}
    for _ in range(max_depth):
        nxt = set()
        for x in frontier:
            for p in parents_of.get(x, ()):
                if p == v:
                    return True
                nxt.add(p)
        frontier = nxt
        if not frontier:
            break
    return False


def _on_cycle(live_adj, birth, v, L, need_younger, younger_extra=None):
    """Is v on an undirected cycle of length <= L (optionally containing an
    element younger than v, optionally further filtered by younger_extra)?
    Product-graph BFS over (node, younger_seen)."""
    bv = birth[v]
    ok_y = (lambda u: birth[u] > bv) if younger_extra is None else \
        (lambda u: birth[u] > bv and younger_extra(u))
    nbrs = sorted(live_adj[v])
    for ai in range(len(nbrs)):
        for bi in range(ai + 1, len(nbrs)):
            a, b = nbrs[ai], nbrs[bi]
            target_bonus = ok_y(b)
            start_flag = ok_y(a)
            if not need_younger:
                start_flag = True
            seen = {(a, start_flag)}
            q = deque([(a, 0, start_flag)])
            found = False
            while q:
                x, d, flag = q.popleft()
                if d >= L - 2:
                    continue
                for u in live_adj[x]:
                    if u == v:
                        continue
                    if u == b:
                        if flag or target_bonus or not need_younger:
                            found = True
                            q.clear()
                            break
                        continue  # may still reach b with flag via other path
                    nf = flag or (not need_younger) or ok_y(u)
                    if (u, nf) not in seen:
                        seen.add((u, nf))
                        q.append((u, d + 1, nf))
            if found:
                return True
    return False


def _lcc(live_adj, alive):
    best = []
    seen = set()
    for s in sorted(alive):
        if s in seen:
            continue
        comp = [s]
        seen.add(s)
        q = deque([s])
        while q:
            v = q.popleft()
            for u in live_adj[v]:
                if u not in seen:
                    seen.add(u)
                    comp.append(u)
                    q.append(u)
        if len(comp) > len(best):
            best = comp
    idx = {v: i for i, v in enumerate(sorted(best))}
    adj = [[] for _ in idx]
    for v, i in idx.items():
        adj[i] = sorted(idx[u] for u in live_adj[v] if u in idx)
    return adj


def grow(params, seed, max_births=MAX_BIRTHS):
    q_spawn = params["q"]
    p_par = params["p_parents"]
    L = params["L_cycle"]
    W = params["W_window"]
    decay = params.get("decay", True)
    need_younger = not params.get("any_cycle", False)
    rho = 2  # frozen in PREREG_P1b
    # --- skeptic-battery extensions (defaults preserve registered semantics) ---
    seed_ring = params.get("seed_ring", 0)      # T2: ring initial condition
    grace = params.get("grace", 0)              # T2: no decay before this tick
    quench_at = params.get("quench_at_alive")   # T5: switch q when alive >= this
    q2 = params.get("q2", q_spawn)              # T5: post-quench spawn rate
    nondesc = params.get("nondescendant", False)  # T3: younger must be non-descendant
    parents_of = {}                             # T3: lineage record

    rng = np.random.default_rng(seed)
    if seed_ring >= 3:
        live_adj = {i: {(i - 1) % seed_ring, (i + 1) % seed_ring}
                    for i in range(seed_ring)}
        birth = {i: 0 for i in range(seed_ring)}
        alive = set(range(seed_ring))
        dirty = set(range(seed_ring))
        n_born = seed_ring
    else:
        live_adj = {0: set()}
        birth = {0: 0}
        alive = {0}
        dirty = {0}
        n_born = 1
    deaths = 0
    tick = 0
    outcome = "ran"
    alive_traj = []
    checkpoints = []
    last_check = 0
    t0 = time.time()

    while n_born < max_births:
        tick += 1
        frontier = sorted(v for v in alive if tick - birth[v] <= W)
        if not frontier:
            outcome = "extinct"
            break
        if len(alive) > ALIVE_CAP:
            outcome = "exp-explosion"
            break
        # --- multiplicative births ---
        q_now = q2 if (quench_at is not None and len(alive) >= quench_at) \
            else q_spawn
        spawn_draws = rng.random(len(frontier))
        for f, draw in zip(frontier, spawn_draws):
            if draw >= q_now:
                continue
            cand = _ball(live_adj, f, rho)
            parents = {f}
            want = min(p_par - 1, len(cand))
            if want > 0:
                pick = rng.choice(len(cand), size=want, replace=False)
                parents |= {cand[int(i)] for i in pick}
            nid = n_born
            n_born += 1
            live_adj[nid] = set()
            birth[nid] = tick
            parents_of[nid] = tuple(sorted(parents))
            alive.add(nid)
            touched = {nid}
            for p in sorted(parents):
                live_adj[nid].add(p)
                live_adj[p].add(nid)
                touched.add(p)
            for t_ in touched:
                dirty.add(t_)
                dirty.update(_ball(live_adj, t_, max(L - 2, 1)))
        # --- simultaneous re-convergence decay pass ---
        if decay and tick > grace:
            check = {v for v in dirty if v in alive
                     and tick - birth[v] >= W}
            check |= {v for v in alive if tick - birth[v] == W}
            if nondesc:
                doomed = sorted(
                    v for v in check
                    if not _on_cycle(live_adj, birth, v, L, need_younger,
                                     lambda u, _v=v: not _descends(
                                         u, _v, parents_of)))
            else:
                doomed = sorted(v for v in check
                                if not _on_cycle(live_adj, birth, v, L,
                                                 need_younger))
            dirty = set()
            for v in doomed:
                deaths += 1
                alive.discard(v)
                for u in live_adj[v]:
                    live_adj[u].discard(v)
                    dirty.add(u)
                    dirty.update(_ball(live_adj, u, max(L - 2, 1)))
                live_adj[v] = set()
        alive_traj.append(len(alive))
        # --- checkpoints ---
        if n_born - last_check >= CHECK_BIRTHS:
            last_check = n_born
            adj = _lcc(live_adj, alive)
            if len(adj) >= 8:
                srcs = sorted(int(x) for x in
                              np.random.default_rng(seed * 31 + tick)
                              .choice(len(adj), min(64, len(adj)),
                                      replace=False))
                f_ = fit_exponent(shell_counts(adj, srcs))
            else:
                f_ = {"cls": "degenerate", "e_hat": float("nan"),
                      "r2_poly": float("nan"), "r2_exp": float("nan")}
            checkpoints.append({"births": n_born, "tick": tick,
                                "alive": len(alive), "deaths": deaths,
                                "lcc": len(adj),
                                "cls": f_["cls"], "e_hat": f_["e_hat"],
                                "r2_gap": (f_["r2_poly"] - f_["r2_exp"])
                                if f_["cls"] != "degenerate"
                                else float("nan")})
            if len(checkpoints) >= 3:
                a = [c["alive"] for c in checkpoints[-3:]]
                if max(a) - min(a) <= 0.05 * max(a):
                    outcome = "stationary"
                    break
    else:
        outcome = "max-births"

    out_graph = _lcc(live_adj, alive) if params.get("return_graph") else None
    return {"params": dict(params), "seed": seed, "n_born": n_born,
            "deaths": deaths, "final_alive": len(alive),
            "final_lcc_adj": out_graph,
            "outcome": outcome,
            "alive_trajectory": alive_traj[:: max(1, len(alive_traj) // 500)],
            "record_size": n_born, "n_alive": len(alive),
            "checkpoints": checkpoints,
            "wall_sec": round(time.time() - t0, 1)}


GRID = [dict(q=qs, p_parents=p, L_cycle=lc, W_window=w, decay=True)
        for qs in (0.3, 0.6) for p in (2, 3) for lc in (4, 6)
        for w in (8, 16)]
CONTROLS = [dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=False,
                 control="no_decay"),
            dict(q=0.3, p_parents=2, L_cycle=4, W_window=8, decay=True,
                 any_cycle=True, control="any_cycle"),
            dict(q=0.1, p_parents=2, L_cycle=4, W_window=4, decay=True,
                 control="extinct_side")]


def _cell(args):
    params, seed = args
    r = grow(params, seed)
    last = r["checkpoints"][-1] if r["checkpoints"] else {"cls": "none",
                                                          "lcc": 0}
    tag = params.get("control",
                     f"q{params['q']}p{params['p_parents']}"
                     f"L{params['L_cycle']}W{params['W_window']}")
    print(f"  {tag} seed={seed}: {r['outcome']} born={r['n_born']} "
          f"alive={r['final_alive']} deaths={r['deaths']} "
          f"lcc={last.get('lcc', 0)} cls={last.get('cls', 'none')} "
          f"e={last.get('e_hat', float('nan')):.2f} ({r['wall_sec']}s)",
          flush=True)
    return r


def main():
    if "--smoke" in sys.argv:
        for pset in (dict(q=0.3, p_parents=2, L_cycle=4, W_window=8,
                          decay=True),
                     CONTROLS[0], CONTROLS[1]):
            r = grow(dict(pset), seed=1, max_births=4000)
            tag = pset.get("control", "grid-cell")
            tr = [(c["births"], c["cls"], round(c["e_hat"], 2),
                   c["alive"], c["deaths"]) for c in r["checkpoints"]]
            print(f"{tag}: {r['outcome']} {tr}")
        return
    t0 = time.time()
    cells = ([(p, 2000 + s) for p in GRID for s in range(10)]
             + [(p, 2000 + s) for p in CONTROLS for s in range(10)])
    with Pool(16) as pool:
        results = pool.map(_cell, cells)
    (HERE / "results").mkdir(exist_ok=True)
    (HERE / "results" / "p1.json").write_text(
        json.dumps({"prereg": "PREREG_P1b.md", "runs": results}, indent=2,
                   default=float))
    print(f"\nwall clock: {round(time.time() - t0, 1)}s")


if __name__ == "__main__":
    main()
