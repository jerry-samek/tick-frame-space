# Exp 138 P1d — Annealing-Tension Test — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test whether the geometric phase needs mutation of the frozen past (annealing) or forward re-branching suffices, per `docs/superpowers/specs/2026-07-12-exp138-p1d-annealing-tension-design.md`.

**Architecture:** Four gated phases, each PREREG frozen before its code runs. I0′ builds a dimension instrument that survives a random-graph null (the P1c prerequisite). The dissipation engine (growth + shed → flux-biased re-branch → Eddington cap) lives in a new `p1d_engine.py` with two orthogonal knobs (W_mut = mutation window, R_branch = re-branch reach). Phase A holds W_mut=0 and sweeps R_branch × N; the verdict is the scaling of the geometric threshold. Phase B allows W_mut>0 to see if mutation buys anything.

**Tech Stack:** Python (numpy, scipy), reusing `experiments/137_participation_ratio/graphs.py` and `experiments/138_geometrogenesis/{instrument.py, p1c_recon.py, p0_autopsy.py}` via sys.path (project convention).

## Global Constraints

- Directory: `experiments/138_geometrogenesis/`; results JSONs to gitignored `results/`; console logs `results_*_console.txt` committed.
- Every stochastic choice uses an explicit seeded `numpy.random.default_rng`; NO dict/set iteration-order dependence (K=12 census lesson) — always iterate `sorted(...)` then index by rng.
- PREREGs frozen in order: I0′ → P1d(A) → P1d(B); each later PREREG may import numeric bands only from earlier results JSONs.
- Long runs: `python -u`, background, moving-average ETA.
- No coordinates in the engine; all locality is graph-distance.
- ≥10 seeds per stochastic configuration.
- Geometric target is COMOVING: scale-free growth (polynomial-in-time, stationary shape) AND finite-d — never absolute stationarity (Addendum F §18.2).
- All z/σ language: bootstrap/spread-stability, never population claims.
- Mandatory skeptic pass (fresh subagent) after Phase I0′ and after Phase A, before their RESULTS docs; anti-rescue clause.

---

### Task 1: Null-safe dimension instrument + PREREG_I0prime + calibration gate

**Files:**
- Create: `experiments/138_geometrogenesis/PREREG_I0prime.md`
- Create: `experiments/138_geometrogenesis/dimension_instrument.py`
- Create: `experiments/138_geometrogenesis/i0prime_calibration.py`
- Create: `experiments/138_geometrogenesis/tests/test_dimension_instrument.py`

**Interfaces:**
- Consumes: `instrument.fit_exponent`, `instrument.shell_counts` (Exp 138 Phase 0); `p1c_recon.ds_sparse`; `graphs.{torus2d,torus3d,binary_tree,random_regular}`.
- Produces: `dimension_instrument.short_cycle_density(adj) -> float` (4- and 6-cycles per node); `dimension_instrument.classify_dimension(adj, rng, n_sources=64) -> dict` with keys `{"shell_cls": "poly"|"exp"|"degenerate", "d_shell": float, "d_spectral": float, "cyc_density": float, "is_manifold": bool}`. `is_manifold` is the P1d gate observable.

- [ ] **Step 1: Write PREREG_I0prime.md** — freeze BEFORE code. Estimator: a graph reads `is_manifold = True` iff **(shell_cls == "poly")** AND **(cyc_density ≥ cyc_thresh)**, where cyc_density = mean count of undirected 4-cycles through a node. Rationale for the two-part rule and why it is P1c-proof: the P1c failure was gating on spectral d_s alone (random 4-regular reads d_s≈2.0). The shell classifier already reads random-regular as `exp` (Exp 138 i0 calibration, 10/10), and random regular graphs are locally tree-like (≈0 short cycles) while lattices are dense in 4-cycles — so cyc_density is an independent second discriminator that random graphs fail hard. d_spectral is REPORTED (the dimension value, with its known lattice-calibrated bias) but does NOT gate.
  - Signed controls (the null is mandatory): torus2d(24), torus3d(12) → is_manifold True; binary_tree(10) → False (shell exp); **random_regular(N,4)** and **random_regular(N,6)**, 10 seeds each → False (the P1c null — must fail on BOTH shell_cls and cyc_density).
  - Gate G-I0′: all lattice controls True; tree and BOTH random-regular controls False (≥9/10 seeds each). Freeze `cyc_thresh` = halfway (geometric mean) between the min lattice cyc_density and the max random cyc_density; record `control_margin` = that gap. FAIL any → the two-part rule is insufficient; redesign under a fresh PREREG (candidate 3rd feature named: spectral-gap / d_shell-vs-d_spectral agreement) — do NOT weaken the null.
- [ ] **Step 2: Write failing tests** in `tests/test_dimension_instrument.py`:

```python
import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))
from dimension_instrument import short_cycle_density, classify_dimension
from graphs import torus2d, random_regular

def test_lattice_reads_manifold():
    r = classify_dimension(torus2d(24), np.random.default_rng(0))
    assert r["is_manifold"] is True
    assert r["cyc_density"] > 0.5  # square lattice: ~1 four-cycle per node

def test_random_regular_is_not_manifold():
    rng = np.random.default_rng(1)
    r = classify_dimension(random_regular(1728, 4, rng), rng)
    assert r["is_manifold"] is False  # the P1c null: d_s alone would say ~2
    assert r["cyc_density"] < 0.2     # locally tree-like

def test_classify_is_seed_deterministic():
    a = classify_dimension(torus2d(16), np.random.default_rng(5))
    b = classify_dimension(torus2d(16), np.random.default_rng(5))
    assert a == b
```

- [ ] **Step 3: Run tests, verify FAIL** (`cd experiments/138_geometrogenesis && python -m pytest tests/test_dimension_instrument.py -q` → import error).
- [ ] **Step 4: Implement `dimension_instrument.py`:**

```python
"""Exp 138 P1d — null-safe dimension instrument (PREREG_I0prime.md).

is_manifold gate = (shell classifier reads poly) AND (4-cycle density high).
Random regular graphs fool spectral d_s (P1c) but fail BOTH of these:
they read shell-exp and are locally tree-like (~0 short cycles). d_spectral
is reported as the dimension value, not gated.
"""
import sys
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))

from instrument import fit_exponent, shell_counts   # noqa: E402
from p1c_recon import ds_sparse                      # noqa: E402

CYC_THRESH = 0.35  # frozen by G-I0'; overwritten from results/i0prime.json when present

def short_cycle_density(adj):
    """Mean number of undirected 4-cycles through a node."""
    sets = [set(adj[i]) for i in range(len(adj))]
    total = 0
    for v in range(len(adj)):
        nb = sorted(sets[v])
        for i in range(len(nb)):
            for j in range(i + 1, len(nb)):
                # common neighbours of nb[i],nb[j] other than v => 4-cycle v-nb[i]-x-nb[j]
                total += len((sets[nb[i]] & sets[nb[j]]) - {v})
    return total / (2 * len(adj))  # each 4-cycle counted twice per node pair

def classify_dimension(adj, rng, n_sources=64):
    nbar = shell_counts(adj, sorted(int(x) for x in
                        (rng.choice(len(adj), min(n_sources, len(adj)), replace=False)
                         if len(adj) > n_sources else range(len(adj)))))
    shell = fit_exponent(nbar)
    cyc = short_cycle_density(adj)
    d_spec = ds_sparse(adj) if len(adj) >= 64 else float("nan")
    is_manifold = (shell["cls"] == "poly") and (cyc >= CYC_THRESH)
    return {"shell_cls": shell["cls"], "d_shell": shell["e_hat"],
            "d_spectral": d_spec, "cyc_density": cyc,
            "is_manifold": bool(is_manifold)}
```

- [ ] **Step 5: Run tests, verify PASS.** If `test_random_regular_is_not_manifold` fails because cyc_density ≥ CYC_THRESH on random-4-regular, the two-part rule is genuinely insufficient — STOP and escalate per PREREG (the null is non-negotiable; do not lower nothing to make it pass).
- [ ] **Step 6: Write + run `i0prime_calibration.py`** — runs all controls (torus2d/3d, tree, random-4-reg ×10, random-6-reg ×10), evaluates G-I0′, computes and writes frozen `cyc_thresh` + `control_margin` + reported d_spectral bands to `results/i0prime.json` and `results_i0prime_console.txt`. Print the table.
- [ ] **Step 7: MANDATORY skeptic pass** (fresh subagent) on the I0′ result: is the instrument really null-safe, or does the two-part rule leak (e.g. a messy near-manifold random graph that reads poly+high-cyc)? Address FIXED/ACCEPTED.
- [ ] **Step 8: Commit** (`Exp 138 P1d I0': null-safe dimension instrument (shell-poly AND 4-cycle-density), random-graph null gated`).

### Task 2: Dissipation growth engine (p1d_engine.py)

**Files:**
- Create: `experiments/138_geometrogenesis/p1d_engine.py`
- Create: `experiments/138_geometrogenesis/tests/test_p1d_engine.py`

**Interfaces:**
- Consumes: `graphs.bfs_distances`.
- Produces: `p1d_engine.grow_dissipative(params, seed, checkpoint_every=1000) -> dict`. `params` dict: `{"q": float, "W_mut": int, "R_branch": int, "C_cap": int, "W_active": int, "N_target": int}`. Returns `{"adj": {id:sorted_list}, "birth": {...}, "n_born": int, "gamma_edits": int, "rebranch_count": int, "shed_count": int, "final_alive_lcc": adj_list, "checkpoints": [...], "outcome": str}`.

- [ ] **Step 1: Write failing tests** in `tests/test_p1d_engine.py`:

```python
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))
from p1d_engine import grow_dissipative

BASE = dict(q=0.3, W_mut=0, R_branch=2, C_cap=2, W_active=4, N_target=1500)

def test_deterministic():
    a = grow_dissipative(dict(BASE), seed=3)
    b = grow_dissipative(dict(BASE), seed=3)
    assert a["n_born"] == b["n_born"]
    assert a["rebranch_count"] == b["rebranch_count"]

def test_wmut0_never_edits_gamma():
    r = grow_dissipative(dict(BASE, W_mut=0), seed=3)
    assert r["gamma_edits"] == 0  # hard immutability: no committed value ever changed

def test_wmut_positive_does_edit():
    r = grow_dissipative(dict(BASE, W_mut=8), seed=3)
    assert r["gamma_edits"] > 0  # annealing arm actually mutates

def test_rebranch_respects_reach():
    # no tap may span graph distance > R_branch at creation; checked via engine invariant flag
    r = grow_dissipative(dict(BASE, R_branch=2), seed=3)
    assert r["max_tap_reach"] <= 2

def test_engagement_nonzero_and_nondegenerate():
    r = grow_dissipative(dict(BASE), seed=3)
    assert 0 < r["rebranch_count"] < r["shed_count"]  # P1b lesson: channel must fire, not saturate
```

- [ ] **Step 2: Verify FAIL. Step 3: Implement `p1d_engine.py`:**

```python
"""Exp 138 P1d — dissipation growth engine (PREREG_P1d.md).

Growth (drive) + shed->flux-biased re-branch->Eddington cap (RAW 135
dissipation). Two knobs: W_mut (mutation window; 0=hard immutable) and
R_branch (re-branch reach). A re-branch = a read-only tap to a frozen
element (consumption). Mutation (W_mut>0) additionally increments the
consumed source's gamma. All choices seeded, id-sorted.
"""
import sys
from collections import deque
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))
from graphs import bfs_distances  # noqa: E402

ALIVE_CAP = 60000

def _ball_by_dist(adj, start, radius):
    """{dist: [nodes]} within radius of start (excl start), bounded BFS."""
    dist = {start: 0}; q = deque([start]); layers = {}
    while q:
        u = q.popleft()
        if dist[u] >= radius:
            continue
        for v in adj[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                layers.setdefault(dist[v], []).append(v)
                q.append(v)
    return layers

def _lcc(adj):
    best, seen = [], set()
    for s in sorted(adj):
        if s in seen: continue
        comp = [s]; seen.add(s); dq = deque([s])
        while dq:
            u = dq.popleft()
            for v in adj[u]:
                if v not in seen:
                    seen.add(v); comp.append(v); dq.append(v)
        if len(comp) > len(best): best = comp
    idx = {v: i for i, v in enumerate(sorted(best))}
    out = [[] for _ in idx]
    for v, i in idx.items():
        out[i] = sorted(idx[u] for u in adj[v] if u in idx)
    return out

def grow_dissipative(params, seed, checkpoint_every=1000):
    q = params["q"]; W_mut = params["W_mut"]; R = params["R_branch"]
    C_cap = params["C_cap"]; W_active = params["W_active"]; N_target = params["N_target"]
    rng = np.random.default_rng(seed)
    adj = {0: set()}; birth = {0: 0}; gamma = {0: 1}
    n = 1; tick = 0
    gamma_edits = rebranch_count = shed_count = 0
    max_tap_reach = 0
    checkpoints = []; outcome = "ran"
    from dimension_instrument import classify_dimension  # local import; instrument frozen in Task 1

    while n < N_target:
        tick += 1
        if len(adj) > ALIVE_CAP:
            outcome = "explosion"; break
        active = [v for v in adj if tick - birth[v] <= W_active]
        # --- growth (drive) ---
        for f in sorted(active):
            if rng.random() < q:
                nid = n; n += 1
                adj[nid] = {f}; adj[f].add(nid); birth[nid] = tick; gamma[nid] = 1
        # --- shed -> flux-biased re-branch (consumption) -> C_cap (Eddington) ---
        for v in sorted(list(adj)):
            shed_count += 1
            layers = _ball_by_dist(adj, v, R)
            consumed = 0
            for d in sorted(layers):                         # nearer first
                shell = sorted(u for u in layers[d]
                               if u not in adj[v] and tick - birth[u] > 0)
                # flux ~ 1/N(r): accept prob = min(1, C_cap / shell_size)
                p = min(1.0, C_cap / max(len(shell), 1))
                for u in shell:
                    if consumed >= C_cap: break
                    if rng.random() < p:
                        adj[v].add(u); adj[u].add(v)          # read-only tap (re-branch)
                        rebranch_count += 1; consumed += 1
                        max_tap_reach = max(max_tap_reach, d)
                        if W_mut > 0 and tick - birth[u] <= W_mut:
                            gamma[u] += 1; gamma_edits += 1     # mutation (annealing)
                if consumed >= C_cap: break
        if n % checkpoint_every < params["q"] * len(active) + 4:  # ~ once per checkpoint band
            lcc = _lcc(adj)
            cd = classify_dimension(lcc, np.random.default_rng(seed * 17 + tick)) \
                if len(lcc) >= 64 else {"is_manifold": False, "d_spectral": float("nan"),
                                        "shell_cls": "degenerate", "cyc_density": 0.0}
            checkpoints.append({"n": n, "tick": tick, "lcc": len(lcc),
                                "is_manifold": cd["is_manifold"],
                                "d_spectral": cd["d_spectral"],
                                "cyc_density": cd["cyc_density"],
                                "rebranch": rebranch_count, "shed": shed_count})
    else:
        outcome = "reached_N"

    return {"adj": {k: sorted(v) for k, v in adj.items()}, "n_born": n,
            "gamma_edits": gamma_edits, "rebranch_count": rebranch_count,
            "shed_count": shed_count, "max_tap_reach": max_tap_reach,
            "final_alive_lcc": _lcc(adj), "checkpoints": checkpoints,
            "outcome": outcome, "seed": seed, "params": dict(params)}
```

- [ ] **Step 4: Run tests, verify PASS.** If `test_engagement_nonzero_and_nondegenerate` fails (rebranch_count == 0 or == shed_count), tune C_cap/R_branch in the TEST's BASE only (not the engine) until the channel is non-degenerate at smoke scale — record the working smoke params for the recon.
- [ ] **Step 5: Commit** (`Exp 138 P1d: dissipation growth engine (shed->flux re-branch->C_cap), W_mut/R_branch knobs, immutability + engagement invariants tested`).

### Task 3: PREREG_P1d + reachable-range recon

**Files:**
- Create: `experiments/138_geometrogenesis/PREREG_P1d.md`
- Create: `experiments/138_geometrogenesis/p1d_recon.py`

**Interfaces:**
- Consumes: `p1d_engine.grow_dissipative`, `dimension_instrument.classify_dimension`.
- Produces: `results/p1d_recon.json` with per-(R_branch, N) engagement + outcome + is_manifold, used to freeze the Phase-A grid.

- [ ] **Step 1: Write `p1d_recon.py`** — before freezing the grid, probe: (a) does the channel engage (rebranch/shed in a non-degenerate band) across R_branch ∈ {1,2,3,4,6} at N=2000? (b) is BOTH a manifold AND a non-manifold outcome reachable somewhere in (R_branch, C_cap) at N=2000 — the reachable-range rule; if only non-manifold is ever reachable, Phase A can only return a negative and that must be stated up front; (c) rough N-scaling feasibility (wall-clock at N ∈ {1k,2k,4k,8k}). Print + write `results/p1d_recon.json`.
- [ ] **Step 2: Run `p1d_recon.py`**, read the engagement/reachability table.
- [ ] **Step 3: Write PREREG_P1d.md** — freeze using recon numbers:
  - Engine params frozen: q, C_cap, W_active (from recon's non-degenerate-engagement band); the frozen flux rule (accept prob = min(1, C_cap/shell_size), nearer-first) stated verbatim.
  - **Phase A grid:** W_mut = 0 (hard immutable) × R_branch ∈ {frozen set spanning recon's manifold/non-manifold boundary} × N ∈ {1000, 2000, 4000, 8000} × 10 seeds.
  - **Primary observable:** per (R_branch, N), fraction of seeds whose final LCC reads `is_manifold` AND whose growth is comoving (scale-free-in-time: the alive-trajectory is poly-in-time not exp-in-time, reusing the Addendum-F growth-shape test). Define `R_branch*(N)` = smallest R_branch with ≥8/10 seeds geometric.
  - **Verdict rule (frozen), the annealing-tension decision:** fit R_branch*(N) vs N. **ACQUITTAL** = R_branch*(N) bounded (no significant positive slope; plateaus at a constant across the four N). **MIDDLE** = R_branch*(N) grows as N^α, α significantly > 0. **ENGINE-WRONG (this arm)** = no (R_branch,N) cell reaches geometric. Also report whether the *effective* mean tap reach is bounded even when R_branch cap is large (the §12.1 self-organized-vs-smuggled sub-test).
  - **Reachability statement:** cite recon — is a manifold outcome reachable at W_mut=0 at all? Both verdict directions must be attainable or the gate is dishonest.
  - Anti-rescue; instrument = the frozen `is_manifold`; skeptic pass mandatory before RESULTS.
- [ ] **Step 4: Commit** (`Exp 138 P1d: recon + PREREG (W_mut=0 primary arm, R_branch*(N) scaling = the annealing-tension verdict)`).

### Task 4: Phase A run → verdict → skeptic → RESULTS

**Files:**
- Create: `experiments/138_geometrogenesis/p1d_run_A.py`
- Create: `experiments/138_geometrogenesis/results_p1d_A_console.txt`
- Create: `experiments/138_geometrogenesis/RESULTS_p1d_A.md`

- [ ] **Step 1: Write `p1d_run_A.py`** — runs the frozen Phase-A grid (W_mut=0 × R_branch × N × 10 seeds) via `multiprocessing.Pool`, computes per-cell geometric-fraction + comoving-fraction, derives `R_branch*(N)`, fits its N-scaling, and emits the frozen verdict (ACQUITTAL / MIDDLE / ENGINE-WRONG) to `results/p1d_A.json`. Moving-average ETA.
- [ ] **Step 2: Background run** `python -u p1d_run_A.py 2>&1 | tee results_p1d_A_console.txt` (est. hours; parallel across cells).
- [ ] **Step 3: Evaluate verdict** exactly as registered from `results/p1d_A.json`.
- [ ] **Step 4: MANDATORY skeptic pass** (fresh subagent, full bundle: per-cell per-seed is_manifold + comoving flags, R_branch*(N) fit, effective-reach data, engagement census, any deviations). Stress especially: is the "manifold" reading instrument-robust (re-run is_manifold under source resampling), is the growth-shape test being fooled, is engagement non-degenerate in every cell. Address FIXED/ACCEPTED.
- [ ] **Step 5: Write `RESULTS_p1d_A.md`** with a `## Skeptic review` section (each objection FIXED/ACCEPTED). State the verdict in the annealing-tension frame: does forward re-branching alone (W_mut=0) reach geometry, and is its reach bounded? If ENGINE-WRONG, Phase B still runs (mutation might rescue it — that would be the CONVICTION signal); if ACQUITTAL/MIDDLE, Phase B tests whether mutation adds anything.
- [ ] **Step 6: Commit + update memory** (project_138 memory + MEMORY.md index).

### Task 5: Phase B comparison (W_mut>0) → final verdict → skeptic → RESULTS

**Files:**
- Create: `experiments/138_geometrogenesis/p1d_run_B.py`
- Create: `experiments/138_geometrogenesis/results_p1d_B_console.txt`
- Create: `experiments/138_geometrogenesis/RESULTS_p1d_B.md`

- [ ] **Step 1: Write PREREG addendum** (in `PREREG_P1d.md`, a dated Phase-B section, frozen before Phase B runs): grid = W_mut ∈ {0, W_active, 2·W_active, ∞-proxy=N_target} × the R_branch value(s) at/below Phase A's threshold × N ∈ {2000, 4000} × 10 seeds. **Decision:** does any W_mut>0 cell reach geometric where the matched W_mut=0 cell did NOT? **CONVICTION** (annealing-in-disguise) = yes, robustly (≥2 R_branch values, ≥8/10 seeds, monotone in W_mut). **NO-BENEFIT** = mutation reaches nothing re-branching didn't → strengthens ACQUITTAL (the axiom is not just safe but unnecessary to relax). Reachability + anti-rescue as before.
- [ ] **Step 2: Write + background-run `p1d_run_B.py`**, `tee results_p1d_B_console.txt`.
- [ ] **Step 3: Evaluate** the CONVICTION / NO-BENEFIT decision → `results/p1d_B.json`.
- [ ] **Step 4: MANDATORY skeptic pass** (fresh subagent): is any apparent mutation-benefit an artifact (e.g. W_mut>0 just adds edges that inflate cyc_density without real geometry)? Cross-check is_manifold robustness and that the W_mut=0 baseline in Phase B reproduces Phase A. FIXED/ACCEPTED.
- [ ] **Step 5: Write `RESULTS_p1d_B.md`** + a short `RESULTS_p1d_SYNTHESIS.md` stating the final four-way verdict (ACQUITTAL / MIDDLE / CONVICTION / ENGINE-WRONG) against RAW 136 §12.3, and propose (pending user approval, never auto-edit) a RAW 135/136 addendum recording it.
- [ ] **Step 6: Commit + update memory.**

## Self-Review

- **Spec coverage:** I0′ null-safe instrument + random-graph null gate (Task 1); three-mechanism engine with W_mut/R_branch (Task 2); RAW 135 dissipation loop = shed/flux/C_cap (Task 2 Step 3); reachable-range recon (Task 3 Step 1); Phase A W_mut=0 sweep + R_branch*(N) scaling verdict (Task 4); Phase B W_mut>0 comparison (Task 5); comoving growth-shape (Tasks 3–4 observable); all four outcomes ACQUITTAL/MIDDLE/CONVICTION/ENGINE-WRONG (Tasks 3–5); traps — instrument null (Task 1), reachable-range (Task 3), engagement census (Tasks 2–3), tie-breaking (Global Constraints), skeptic passes (Tasks 1,4,5). Covered.
- **Placeholder scan:** frozen numeric ranges deferred to the recon are explicit instructions with the freezing rule stated, not gaps.
- **Type consistency:** `classify_dimension`/`is_manifold` consistent across Tasks 1,2,4,5; `grow_dissipative` param dict + return keys consistent across Tasks 2,3,4,5; `short_cycle_density`/`cyc_density` naming consistent.
