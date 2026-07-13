# Exp 138 Geometrogenesis Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Test whether directed causal growth + renewal decay dynamically selects polynomial ball growth (locality), bridged from a Trugenberger-condensation positive control, per `docs/superpowers/specs/2026-07-10-exp138-geometrogenesis-design.md`.

**Architecture:** Three gated phases, each with its PREREG frozen before its code runs: I0 (ball-growth-exponent instrument + signed controls), P0 (equilibrium cycle-condensation on random regular graphs under a declared Jost–Liu curvature action), P1 (frontier accretion with immutable past + cycle-closure survival, small grid + in-grid signed controls). Skeptic pass after P0 and after P1, before their RESULTS docs.

**Tech Stack:** Python (numpy, scipy), reusing `experiments/137_participation_ratio/graphs.py` via sys.path (project convention, cf. Exp 137 importing Exp 134).

## Global Constraints

- Directory: `experiments/138_geometrogenesis/`; results JSONs to gitignored `results/`; console logs `results_*_console.txt` committed.
- Every stochastic choice uses an explicit seeded `numpy.random.default_rng`; NO dict/set iteration-order dependence anywhere (K=12 census lesson); no salted `hash()` for seeds — use fixed integers or `zlib.crc32`.
- PREREGs frozen in order I0 → P0 → P1; each later PREREG may import numeric bands only from earlier phase results.
- Long runs: `python -u`, background, moving-average ETA prints.
- No coordinates anywhere in P1 dynamics; attachment locality is graph-distance only.
- ≥10 seeds per stochastic configuration; deterministic fixtures get size-sweeps instead.
- All z/σ language: bootstrap/spread-stability, never population claims.

---

### Task 1: Scaffold, PREREG_I0, instrument, calibration run (gate G-I0)

**Files:**
- Create: `experiments/138_geometrogenesis/PREREG_I0.md`
- Create: `experiments/138_geometrogenesis/instrument.py`
- Create: `experiments/138_geometrogenesis/i0_calibration.py`
- Create: `experiments/138_geometrogenesis/tests/test_instrument.py`

**Interfaces:**
- Produces: `instrument.shell_counts(adj, sources, r_max) -> np.ndarray` (mean shell counts N̄(r), index r=0..r_max); `instrument.fit_exponent(nbar) -> dict` with keys `{"e_hat": float, "r2_poly": float, "rate_exp": float, "r2_exp": float, "cls": "poly"|"exp", "window": (r_lo, r_hi)}`; `instrument.classify(adj, rng, n_sources=64) -> dict` (adds sampled sources). Later tasks rely on these exact names.

- [ ] **Step 1: Write PREREG_I0.md** — freeze BEFORE instrument code: estimator definition (below), controls, gate:
  - Estimator: mean BFS shell counts N̄(r) over `n_sources=64` uniformly sampled sources (all nodes if N<64). Fit window: r ∈ [2, r_peak] where r_peak = argmax N̄(r), requiring ≥4 points (else classification = "degenerate"). Polynomial fit: least squares on (log r, log N̄); exponential fit: (r, log N̄). `cls = "poly"` iff R²_poly ≥ R²_exp, else "exp".
  - Controls (signed): torus2d(24) → poly, ê≈1; torus3d(12) → poly, ê≈2; random 6-regular N=1728 (10 seeds) → exp; balanced binary tree depth 10 → exp.
  - **Gate G-I0:** all four controls classified correctly; lattice bands frozen as ê ± 0.25 around measured torus values (band_2d, band_3d recorded in results JSON); expander/tree must classify "exp" with rate_exp > 0.3. FAIL any → stop, redesign estimator.
- [ ] **Step 2: Write failing unit tests** in `tests/test_instrument.py`:

```python
import sys
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[0] / "137_participation_ratio"))
from instrument import shell_counts, fit_exponent
from graphs import torus3d, balanced_tree  # reuse Exp 137 generators

def test_torus3d_is_polynomial_exponent_2():
    adj = torus3d(10)
    nbar = shell_counts(adj, sources=list(range(0, 1000, 20)), r_max=8)
    f = fit_exponent(nbar)
    assert f["cls"] == "poly" and 1.6 < f["e_hat"] < 2.4

def test_tree_is_exponential():
    adj = balanced_tree(10)
    nbar = shell_counts(adj, sources=[0], r_max=9)
    f = fit_exponent(nbar)
    assert f["cls"] == "exp" and f["rate_exp"] > 0.3
```

  (If `graphs.py` lacks `balanced_tree`, it has `tree`/`binary_tree` — check and use the actual name; do not duplicate the generator.)
- [ ] **Step 3: Run tests, verify FAIL** (`python -m pytest tests/test_instrument.py -q` → import error).
- [ ] **Step 4: Implement `instrument.py`** — BFS shells (reuse `graphs.bfs_distances`), mean over sources, both fits per PREREG; nothing else (YAGNI).
- [ ] **Step 5: Tests pass.**
- [ ] **Step 6: Write + run `i0_calibration.py`** — runs the four controls, prints table, evaluates G-I0, writes `results/i0.json` (including frozen bands) and `results_i0_console.txt`.
- [ ] **Step 7: Commit** (`Exp 138 I0: instrument + calibration gate`).

### Task 2: Curvature module (exact vs Jost–Liu, validation)

**Files:**
- Create: `experiments/138_geometrogenesis/curvature.py`
- Create: `experiments/138_geometrogenesis/tests/test_curvature.py`

**Interfaces:**
- Produces: `curvature.kappa_exact(adj, i, j) -> float` (Ollivier κ = 1 − W₁ between uniform neighbor measures, W₁ via `scipy.optimize.linprog`, graph distances from bounded BFS); `curvature.kappa_jl(adj, i, j) -> float` (Jost–Liu lower bound); `curvature.validate(adj_list, edges, tol) -> dict`.

- [ ] **Step 1: Failing tests** — known values + bound property:

```python
def test_jl_is_lower_bound_on_random_graphs():
    rng = np.random.default_rng(0)
    adj = random_regular(60, 4, rng)
    for (i, j) in sample_edges(adj, 30, rng):
        assert kappa_jl(adj, i, j) <= kappa_exact(adj, i, j) + 1e-9

def test_exact_on_complete_k4():
    adj = [[1,2,3],[0,2,3],[0,1,3],[0,1,2]]
    for j in (1,2,3):
        assert abs(kappa_exact(adj, 0, j) - 0.5) < 1e-6  # K4: kappa = 1/2
```

- [ ] **Step 2: Verify FAIL. Step 3: Implement. Step 4: Tests pass.**
  - Jost–Liu (uniform measures, unweighted): with d_i, d_j degrees and t = #common neighbors of (i,j): `kappa_jl = -(1 - 1/d_i - 1/d_j - t/min(d_i,d_j))_+ - (1 - 1/d_i - 1/d_j - t/max(d_i,d_j))_+ + t/max(d_i,d_j)` where `(x)_+ = max(x, 0)`.
- [ ] **Step 5: Commit** (`Exp 138: Ollivier curvature exact + Jost-Liu, cross-validated`).

### Task 3: PREREG_P0 + condensation engine + smoke run

**Files:**
- Create: `experiments/138_geometrogenesis/PREREG_P0.md`
- Create: `experiments/138_geometrogenesis/p0_condensation.py`
- Create: `experiments/138_geometrogenesis/tests/test_p0.py`

**Interfaces:**
- Produces: `p0_condensation.metropolis_run(n, k, coupling, sweeps, seed, use_exact=False) -> dict` (final adjacency, energy trace, acceptance rate); CLI `python -u p0_condensation.py --sweep` runs the coupling ladder.

- [ ] **Step 1: Write PREREG_P0.md** — freeze: N=512, k=4 (the best-documented Kelly–Trugenberger regime: emergent 2D-lattice-like phase); action `H = -J * sum_edges kappa_jl(i,j)` (DECLARED: JL bound as the action, not exact κ — sign-level replication of cycle condensation under OUR declared action, not numeric replication of published curves); move = degree-preserving double-edge swap ((a,b),(c,d) → (a,c),(b,d), rejected if multi-edge/self-loop); ΔH computed on the edge set within distance 1 of touched vertices; Metropolis at β=1 over coupling ladder J ∈ {0.5, 1, 2, 4, 8}; 2000 sweeps (1 sweep = N attempted moves), 10 seeds per J; observables per checkpoint: energy, triangle+square census, I0 classification of the graph.
  - **Gate G-P0 (frozen):** ∃ J in the ladder where ≥8/10 seeds end classified `poly` by the I0 instrument, AND at small J ≥8/10 remain `exp` (the transition is visible, signed both ways). Secondary (reported): square-count jump, ê value vs band_2d.
  - Escape hatch declared: if no J condenses, one further pre-registered extension (J ∈ {16, 32}, 5000 sweeps) is permitted ONCE; beyond that P0 FAILS and the program stops for diagnosis.
- [ ] **Step 2: Failing test** — swap correctness + determinism:

```python
def test_double_edge_swap_preserves_degrees_and_determinism():
    r1 = metropolis_run(64, 4, coupling=2.0, sweeps=5, seed=7)
    r2 = metropolis_run(64, 4, coupling=2.0, sweeps=5, seed=7)
    assert r1["energy_trace"] == r2["energy_trace"]
    assert all(len(nbrs) == 4 for nbrs in r1["adj"])
```

- [ ] **Step 3: FAIL. Step 4: Implement (JL fast path; local ΔH; seeded rng only). Step 5: PASS.**
- [ ] **Step 6: Smoke run** — N=128, J=4, 200 sweeps, 2 seeds; verify energy decreases and square census moves. Not gated; sanity only.
- [ ] **Step 7: Commit** (`Exp 138 P0: prereg + condensation engine + smoke`).

### Task 4: P0 production run → gate → skeptic → RESULTS_p0

**Files:**
- Create: `experiments/138_geometrogenesis/results_p0_console.txt`
- Create: `experiments/138_geometrogenesis/RESULTS_p0.md`

- [ ] **Step 1:** Background run `python -u p0_condensation.py --sweep 2>&1 | tee results_p0_console.txt` (est. hours; JL is O(1)/edge; if a single (J, seed) cell exceeds ~20 min, halve sweeps for the remaining ladder and LOG the deviation in RESULTS — do not change the gate).
- [ ] **Step 2:** Evaluate G-P0 exactly as registered; write `results/p0.json`.
- [ ] **Step 3:** MANDATORY skeptic pass (fresh subagent, full bundle: claim, raw per-seed classifications, energy traces, deviations). Address objections FIXED/ACCEPTED.
- [ ] **Step 4:** Write `RESULTS_p0.md` with Skeptic review section. If G-P0 FAILED: stop the program here, RESULTS records the diagnosis path (instrument vs replication via I0 controls), and P1 does not run.
- [ ] **Step 5: Commit.**

### Task 5: PREREG_P1 + growth engine + unit tests + smoke

**Files:**
- Create: `experiments/138_geometrogenesis/PREREG_P1.md`
- Create: `experiments/138_geometrogenesis/p1_growth.py`
- Create: `experiments/138_geometrogenesis/tests/test_p1.py`

**Interfaces:**
- Produces: `p1_growth.grow(params, seed, max_births=20000) -> dict` (live adjacency at end, alive-count trajectory, exponent trajectory via I0 instrument every 1000 births, death census). `params` dataclass/dict: `{"p_parents": int, "rho_att": int, "L_cycle": int, "W_window": int, "m_new_per_tick": int, "decay": bool}`.

- [ ] **Step 1: Write PREREG_P1.md** — freeze BEFORE engine code:
  - **Growth rule:** start = single seed element. Each tick, `m_new=4` new elements. For each: pick anchor f uniformly (seeded rng) from FRONTIER = alive elements with age ≤ W; parents = f + (p_parents−1) elements sampled uniformly from the ball of graph-distance ≤ ρ_att around f in the LIVE undirected graph (if fewer available, take all). New element: directed edges parent→child; birth tick recorded. Past immutable: dead elements retained in the record, unattachable.
  - **Renewal decay:** at each tick, every alive element with age ≥ W dies UNLESS it currently lies on an undirected cycle of length ≤ L in the live graph (check: for element v, some pair of its live neighbors connected by a path of length ≤ L−2 in the live graph with v removed; bounded BFS). Death removes it from the live graph; record retained.
  - **Grid:** p_parents ∈ {2,3} × ρ_att ∈ {2,3} × L ∈ {4,6} × W ∈ {8,16} = 16 cells; 10 seeds each. **In-grid signed controls:** (a) `decay=False` (pure growth — Bolognesi control, expect exp), (b) L=10⁶ (decay vacuous — expect exp or death-free tree), 10 seeds each.
  - **Stopping:** 20000 births or live-size stationarity (±5% over 2000 births) or extinction.
  - **Decision rules (bands imported from I0 results JSON, frozen):** GEOMETRIC SELECTION = ≥8/10 seeds in ≥2 non-adjacent grid cells end `poly` with ê inside band_2d or band_3d, sustained over the last 3 exponent checkpoints. HONEST NEGATIVE = no cell reaches it and controls behave as predicted. KNIFE-EDGE = exactly one cell reaches it (RAW 134 §12.1 criterion). Extinction everywhere = reported as its own outcome (decay too strong — parameter, not verdict).
  - **Reachable-range statement:** PASS attainable (I0 lattices prove the instrument's poly reading is reachable by graphs of this size); FAIL attainable (controls (a),(b) expected exp). Both directions live.
- [ ] **Step 2: Failing unit tests:**

```python
def test_growth_is_deterministic_and_past_immutable():
    p = dict(p_parents=2, rho_att=2, L_cycle=4, W_window=8, m_new_per_tick=4, decay=True)
    r1 = grow(p, seed=3, max_births=500)
    r2 = grow(p, seed=3, max_births=500)
    assert r1["alive_trajectory"] == r2["alive_trajectory"]
    assert r1["record_size"] >= 500 and r1["record_size"] >= r1["n_alive"]  # dead retained

def test_no_decay_control_never_kills():
    p = dict(p_parents=2, rho_att=2, L_cycle=4, W_window=8, m_new_per_tick=4, decay=False)
    r = grow(p, seed=3, max_births=500)
    assert r["deaths"] == 0
```

- [ ] **Step 3: FAIL. Step 4: Implement engine (seeded rng for every choice; frontier/ball sampling sorted-then-rng-indexed to kill iteration-order dependence). Step 5: PASS.**
- [ ] **Step 6: Smoke** — one cell, 2 seeds, 2000 births; verify exponent checkpoints produced, deaths occur, no crash at extinction.
- [ ] **Step 7: Commit** (`Exp 138 P1: prereg + growth/renewal engine + smoke`).

### Task 6: P1 grid run → gates → skeptic → RESULTS_p1 → synthesis

**Files:**
- Create: `experiments/138_geometrogenesis/results_p1_console.txt`
- Create: `experiments/138_geometrogenesis/RESULTS_p1.md`

- [ ] **Step 1:** Background grid run (16 cells + 2 controls) × 10 seeds, `python -u`, moving-average ETA. Est. minutes/run → hours total; parallelize across cells with `multiprocessing` if a smoke-run timing extrapolation exceeds 4 h.
- [ ] **Step 2:** Evaluate decision rules exactly as registered → `results/p1.json`.
- [ ] **Step 3:** MANDATORY skeptic pass (fresh subagent; bundle includes per-cell per-seed classifications, exponent trajectories, control outcomes, any deviations). FIXED/ACCEPTED ledger.
- [ ] **Step 4:** `RESULTS_p1.md` with Skeptic review; outcome-specific closing: GEOMETRIC → propose follow-up preregs (stability perturbation, Addendum E gravity-tail check) as banked items only; NEGATIVE → the "equilibrium is load-bearing" statement, worded per spec §5; either way propose RAW 134 Addendum F (pending user approval — never auto-edit the RAW).
- [ ] **Step 5: Commit. Update memory files** (project_138 memory + MEMORY.md index).

## Self-Review

- **Spec coverage:** I0 estimator+controls+reachable-range (Task 1); curvature validation requirement (Task 2); P0 replication, gate, stop-on-fail (Tasks 3–4); P1 growth+decay, grid, in-grid controls, three registered outcomes, knife-edge criterion (Tasks 5–6); traps: tie-breaking (Global Constraints + Task 5 Step 4), Bolognesi control (P1 grid), PASS-band freezing order (PREREG chain), skeptic passes (Tasks 4, 6). Covered.
- **Placeholder scan:** none — declared deferrals (e.g., `balanced_tree` name check) are instructions, not gaps.
- **Type consistency:** `shell_counts`/`fit_exponent`/`classify` names consistent across Tasks 1, 3 (I0 classification), 5–6 (checkpoints); `kappa_jl` used in Task 3's action matches Task 2.
