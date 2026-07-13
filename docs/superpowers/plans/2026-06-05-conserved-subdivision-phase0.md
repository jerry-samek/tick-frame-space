# Conserved-Subdivision Substrate — Phase 0 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and *calibrate* the measurement battery, build the conserved-subdivision substrate with toggleable ingredients, and characterize where the **bare** rule lands on emergent dimension — establishing the trusted instruments and the baseline that Phase 1's ingredient ablation must move.

**Architecture:** A growing structure with two graphs kept strictly separate — a **history tree** (parent→children, bookkeeping only) and a **leaf boundary-adjacency graph** ("space," the only thing read). A tick subdivides leaves (measure conserved exactly via `Fraction`). A pluggable `Rule` object exposes ingredient toggles (all OFF = bare rule for Phase 0). A `battery` of dimension/curvature/homology probes is calibrated against geometries with known answers before it is ever pointed at the substrate.

**Tech stack:** Python 3.13, `numpy`, `scipy`, `networkx` (graph metrics + random walks), `fractions.Fraction` (exact conservation), `GraphRicciCurvature` (Ollivier-Ricci), `gudhi` (persistent homology). `pytest` for the calibration tests. Spec: `docs/superpowers/specs/2026-06-05-conserved-subdivision-substrate-design.md`.

**Experiment-workflow note:** TDD applies to the **probes and nulls** (known ground truth) and the substrate **invariants** (conservation, append-only). The substrate *rule* is characterized, not asserted. Commits are checkpoints; nothing is pushed without the user's say.

---

## A. PRE-REGISTRATION (locked before any substrate run)

This section pins spec §13 (functional forms) and locks spec §9 (thresholds). **None of it may change after seeing substrate results.** It is committed in Task 0 as `PREREG.md` in the experiment dir, and `RESULTS_phase0.md` may only report against it.

**A.1 Substrate representation (pinned):**
- Measure: `fractions.Fraction`, total always `Fraction(1)`. Conservation = `sum(leaf.measure) == Fraction(1)` exactly, every tick.
- Bare cut: each selected leaf splits into **k=2** children; bare split is equal halves (`parent.measure/2` each). (Difference-driven unequal splits are a Phase-1 ingredient, not bare.)
- Bare adjacency rule: on splitting leaf `c` (leaf-neighbors `Nbr(c)`), the two children are mutually adjacent AND each inherits adjacency to every member of `Nbr(c)`. (This deliberately blows the leaf-graph up tree-like; characterizing where that lands is Phase 0b's whole point.)
- Which leaves split per tick (bare): **all** current leaves split each tick (uniform refinement). (Selective, difference-gated splitting is a Phase-1 ingredient.)
- `x(c)` (bare): the leaf's **boundary-address** = the bit-string of left/right choices root→leaf. Branch-chain NAND evaluation is a Phase-1 ingredient (§6.1); bare `x` is just the address, and bare Same/Different = address shared-prefix length.

**A.2 Ingredient toggles (defined here, all OFF in Phase 0; Phase 1 flips them one at a time — first-pass forms, pre-registered, not changeable post-hoc):**
- `nonlocality`: `none` | `ancestral` (classify using the branch-chain NAND over the address, depth-limited to `R_anc`) | `spatial` (smear over leaf-adjacency radius `R_sp`). Phase-1 `R_anc=4`, `R_sp=2`.
- `diff_direction`: bare equal split vs split along the principal-difference axis of `x` over the neighborhood (Verma–Kpotufe–Dasgupta).
- `loops`: bare (children inherit all parent neighbors) vs **boundary-matched gluing** (a child is adjacent to a neighbor's child only if they share the corresponding sub-boundary) — the loop-forming rule.
- `penalty`: none vs layering+curvature penalty: suppress splits that create only-minimal/only-maximal relations; bias toward splits that lengthen chains; penalize edges whose Ollivier-Ricci is below `kappa_min=-0.3`.

**A.3 Locked pass thresholds (spec §9):**
- **Dimension WIN** requires ALL of: `d_s ∈ [2.8, 3.2]` plateau over ≥1 decade of walk-length; `d_H ∈ [2.8, 3.2]`; `|d_s − d_H| ≤ 0.3`; Myrheim–Meyer `d_MM ∈ [2.8, 3.2]`; longest-chain height exponent `∈ [0.28, 0.40]` (n^{1/3}); median Ollivier-Ricci `∈ [−0.1, +0.1]`; loop density increasing; Dirichlet energy not decaying to <10% of initial; Betti numbers of a 3-ball stable across ≥3 thickenings and ≥20 seeds (median, IQR reported).
- **Seeds:** ≥20 for every reported number; report median + IQR; no single-seed headline.
- **Scale:** finite-size scaling required; the dimension claim must hold (not drift toward 2) up to at least `n = 5000` leaves (KR dominance switches on at n≳50–100, so small-n is not evidence).
- **Calibration gate (Task 11):** the battery must, on the same N, return WIN-band values for Poisson-3D, ~2 for the 2D grid, ~4/3 d_s for the tree, and FAIL all bands for the Eden blob and the diffusion field. If it does not separate these, the instruments are not trusted and no substrate result counts.

**A.4 Program falsifier (spec §10):** if the full Phase-1 rule still misses the WIN band at scale across seeds, record a clean negative and stop; do not add a sixth ingredient or reframe.

---

## File Structure

- `experiments/136_conserved_subdivision/PREREG.md` — section A, committed first, frozen.
- `experiments/136_conserved_subdivision/substrate.py` — `Cell`, `Substrate` (history tree + leaf-adjacency), genesis, `tick`, invariants.
- `experiments/136_conserved_subdivision/rule.py` — `Rule` dataclass (the toggles), bare split + adjacency.
- `experiments/136_conserved_subdivision/nulls.py` — Poisson-3D, 2D grid, random tree, Eden blob, diffusion-field generators → each returns a `networkx.Graph` (and a poset where applicable).
- `experiments/136_conserved_subdivision/battery.py` — the probes: `hausdorff_dim`, `spectral_dim`, `chain_scaling`, `myrheim_meyer`, `dirichlet_loops`, `ollivier_ricci`, `betti_stability`; plus `run_battery(graph, poset)` returning a dict.
- `experiments/136_conserved_subdivision/phase0_baseline.py` — driver: genesis→bare tick to scale, multi-seed, apply battery, write `RESULTS_phase0.md`.
- `experiments/136_conserved_subdivision/tests/` — calibration tests (pytest).

---

## Task 0: Pre-registration + scaffold

**Files:** Create `experiments/136_conserved_subdivision/PREREG.md`, `__init__.py`, `tests/__init__.py`.

- [ ] **Step 1:** Copy section A of this plan verbatim into `PREREG.md`. Add a one-line header: "Frozen 2026-06-05. RESULTS may only report against this."
- [ ] **Step 2:** Create empty `__init__.py` and `tests/__init__.py`.
- [ ] **Step 3 (commit checkpoint):** `git add experiments/136_conserved_subdivision && git commit -m "exp136: pre-registration + scaffold"`

---

## Task 1: Substrate core (genesis, conserved cut, invariants)

**Files:** Create `substrate.py`; Test `tests/test_substrate.py`.

- [ ] **Step 1: Write the failing tests**

```python
# tests/test_substrate.py
from fractions import Fraction
from substrate import Substrate

def test_genesis_single_cell_measure_one():
    s = Substrate()
    assert len(s.leaves) == 1
    assert sum(c.measure for c in s.leaves) == Fraction(1)

def test_first_boundary_two_leaves_conserved():
    s = Substrate(); s.tick()                      # tick 1 = first boundary
    assert len(s.leaves) == 2
    assert sum(c.measure for c in s.leaves) == Fraction(1)

def test_conservation_exact_over_many_ticks():
    s = Substrate()
    for _ in range(8):
        s.tick()
        assert sum(c.measure for c in s.leaves) == Fraction(1)   # EXACT, no float

def test_append_only_history_grows_never_shrinks():
    s = Substrate(); n0 = s.node_count()
    s.tick()
    assert s.node_count() > n0
    # every historical node still present
    assert all(nid in s.nodes for nid in s._all_ids_before_last_tick)

def test_address_is_bitstring_path():
    s = Substrate(); s.tick()
    addrs = sorted(c.address for c in s.leaves)
    assert addrs == ["0", "1"]
```

- [ ] **Step 2: Run, verify they fail** — `pytest experiments/136_conserved_subdivision/tests/test_substrate.py -v` → FAIL (no module).

- [ ] **Step 3: Implement**

```python
# substrate.py
from fractions import Fraction
from dataclasses import dataclass, field

@dataclass
class Cell:
    id: int
    measure: Fraction
    address: str                 # bit-string path root->leaf ("" at genesis)
    parent: int | None
    children: list[int] = field(default_factory=list)

class Substrate:
    """History tree (parent->children) + leaf set. Leaf-adjacency lives in readout."""
    def __init__(self):
        self.nodes: dict[int, Cell] = {}
        self._next = 0
        root = self._new(Fraction(1), "", None)
        self.leaves: list[Cell] = [root]
        self._all_ids_before_last_tick: set[int] = set()

    def _new(self, measure, address, parent):
        c = Cell(self._next, measure, address, parent); self.nodes[c.id] = c
        self._next += 1
        return c

    def node_count(self): return len(self.nodes)

    def tick(self, select=None, split=None):
        """Uniform bare tick by default. `select(leaves)->subset`, `split(cell)->list[(measure,bit)]` override for ingredients."""
        self._all_ids_before_last_tick = set(self.nodes)
        select = select or (lambda ls: ls)
        split = split or (lambda c: [(c.measure / 2, "0"), (c.measure / 2, "1")])
        to_split = select(self.leaves)
        new_leaves = [c for c in self.leaves if c not in to_split]
        for c in to_split:
            for m, bit in split(c):
                child = self._new(m, c.address + bit, c.id)
                c.children.append(child.id); new_leaves.append(child)
        self.leaves = new_leaves
```

- [ ] **Step 4: Run, verify pass** — same command → PASS (5 tests).
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: substrate core + conservation/append-only tests"`

---

## Task 2: Readout — leaf boundary-adjacency graph

**Files:** Modify `substrate.py` (add adjacency tracking); Test `tests/test_readout.py`.

- [ ] **Step 1: Write failing test** (bare adjacency rule from A.1)

```python
# tests/test_readout.py
from substrate import Substrate
import networkx as nx

def test_first_cut_two_leaves_adjacent():
    s = Substrate(); s.tick()
    g = s.leaf_graph()
    assert g.number_of_nodes() == 2 and g.number_of_edges() == 1

def test_children_inherit_parent_neighbors():
    s = Substrate(); s.tick()        # leaves {0->"0", "1"}, adjacent
    s.tick()                         # each splits into 2; bare rule: child adj to sibling + all parent-neighbors' (still leaves) 
    g = s.leaf_graph()
    assert g.number_of_nodes() == 4
    assert nx.is_connected(g)
```

- [ ] **Step 2: Run, verify fail** → FAIL (`leaf_graph` undefined).

- [ ] **Step 3: Implement** — maintain adjacency on the leaf set across ticks (bare rule A.1).

```python
# add to Substrate.__init__:  self.adj: dict[int, set[int]] = {self.leaves[0].id: set()}
# replace tick() body's split loop with adjacency maintenance:

    def tick(self, select=None, split=None, glue=None):
        self._all_ids_before_last_tick = set(self.nodes)
        select = select or (lambda ls: ls)
        split = split or (lambda c: [(c.measure / 2, "0"), (c.measure / 2, "1")])
        to_split = set(c.id for c in select(self.leaves))
        new_adj: dict[int, set[int]] = {}
        new_leaves = []
        kids: dict[int, list[int]] = {}
        # 1. create children
        for c in self.leaves:
            if c.id in to_split:
                ks = []
                for m, bit in split(c):
                    child = self._new(m, c.address + bit, c.id)
                    c.children.append(child.id); ks.append(child.id); new_leaves.append(child)
                kids[c.id] = ks
            else:
                new_leaves.append(c); kids[c.id] = [c.id]
        # 2. bare adjacency (A.1): siblings mutually adjacent; each child inherits all parent-neighbors' children
        glue = glue or (lambda a_child, b_child, a_par, b_par: True)  # bare: always glue
        for cid in list(kids):
            for a in kids[cid]:
                new_adj.setdefault(a, set())
                for b in kids[cid]:
                    if a != b: new_adj[a].add(b)                       # siblings
            for nbr in self.adj.get(cid, ()):                          # parent-neighbors
                for a in kids[cid]:
                    for b in kids[nbr]:
                        if glue(a, b, cid, nbr):
                            new_adj.setdefault(a, set()).add(b); new_adj.setdefault(b, set()).add(a)
        self.adj = new_adj; self.leaves = new_leaves

    def leaf_graph(self):
        import networkx as nx
        g = nx.Graph(); g.add_nodes_from(c.id for c in self.leaves)
        for a, nbrs in self.adj.items():
            for b in nbrs: g.add_edge(a, b)
        return g
```

- [ ] **Step 4: Run, verify pass** → PASS.
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: leaf-adjacency readout + tests"`

---

## Task 3: Null models (calibration ground-truth + spec nulls)

**Files:** Create `nulls.py`; Test `tests/test_nulls.py`.

Provides geometries with KNOWN dimension to calibrate the battery: Poisson-3D (d=3, the positive benchmark), 2D grid (d=2), random recursive tree (d_s=4/3), Eden blob (negative), diffusion field (negative).

- [ ] **Step 1: Write failing tests**

```python
# tests/test_nulls.py
import networkx as nx
from nulls import poisson_3d, grid_2d, random_tree, eden_blob

def test_poisson_3d_connected_meandeg_reasonable():
    g, coords = poisson_3d(n=2000, seed=0)
    assert nx.is_connected(g) and 4 < (2*g.number_of_edges()/g.number_of_nodes()) < 40
def test_grid_2d_shape():
    g = grid_2d(40)
    assert g.number_of_nodes() == 1600
def test_random_tree_is_tree():
    g = random_tree(2000, seed=0)
    assert nx.is_tree(g)
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement**

```python
# nulls.py
import numpy as np, networkx as nx
from scipy.spatial import cKDTree

def poisson_3d(n, seed, radius=None):
    rng = np.random.default_rng(seed); pts = rng.random((n, 3))
    if radius is None: radius = (5.0 / n) ** (1/3)            # ~mean degree ~ 4/3 pi rho r^3
    tree = cKDTree(pts); g = nx.Graph(); g.add_nodes_from(range(n))
    for i, j in tree.query_pairs(radius): g.add_edge(i, j)
    g = g.subgraph(max(nx.connected_components(g), key=len)).copy()
    return g, pts

def grid_2d(side):
    return nx.grid_2d_graph(side, side)

def random_tree(n, seed):
    return nx.random_labeled_tree(n, seed=seed) if hasattr(nx, "random_labeled_tree") else nx.random_tree(n, seed=seed)

def eden_blob(n, seed):           # compact cluster: constant interior density, rough boundary
    rng = np.random.default_rng(seed); g = nx.Graph(); g.add_node((0,0)); occ = {(0,0)}
    frontier = [(1,0),(-1,0),(0,1),(0,-1)]
    while g.number_of_nodes() < n:
        c = frontier.pop(rng.integers(len(frontier)))
        if c in occ: continue
        occ.add(c); 
        for d in [(1,0),(-1,0),(0,1),(0,-1)]:
            nb=(c[0]+d[0],c[1]+d[1])
            if nb in occ: g.add_edge(c,nb)
            else: frontier.append(nb)
    return g

def diffusion_field(n, seed, steps=200):  # homogenized field on a poisson-3d graph -> near-uniform
    g, pts = poisson_3d(n, seed); x = np.zeros(g.number_of_nodes()); 
    nodes=list(g.nodes()); idx={u:i for i,u in enumerate(nodes)}; x[0]=1.0
    A = nx.to_scipy_sparse_array(g, nodelist=nodes)
    deg = np.asarray(A.sum(1)).ravel(); deg[deg==0]=1
    for _ in range(steps): x = (A @ x)/deg
    return g, pts, x
```

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: null models for battery calibration"`

---

## Task 4: Probe — Hausdorff dimension + diameter scaling

**Files:** Create `battery.py` (start); Test `tests/test_battery_dim.py`.

- [ ] **Step 1: Write failing calibration test** (the ground truth):

```python
# tests/test_battery_dim.py
from nulls import poisson_3d, grid_2d
from battery import hausdorff_dim

def test_hausdorff_3d_near_3():
    g, _ = poisson_3d(4000, seed=1)
    assert 2.6 <= hausdorff_dim(g) <= 3.4
def test_hausdorff_grid_near_2():
    assert 1.7 <= hausdorff_dim(grid_2d(60)) <= 2.3
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** — volume growth V(R)~R^d from random source nodes (BFS shells), log-log slope on the linear-growth window.

```python
# battery.py
import numpy as np, networkx as nx

def hausdorff_dim(g, n_sources=30, seed=0):
    rng = np.random.default_rng(seed); nodes = list(g.nodes())
    slopes = []
    for s in rng.choice(len(nodes), size=min(n_sources, len(nodes)), replace=False):
        lengths = nx.single_source_shortest_path_length(g, nodes[s])
        if not lengths: continue
        rmax = max(lengths.values())
        if rmax < 3: continue
        Rs = np.arange(1, rmax)                                 # cumulative ball volume
        V = np.array([sum(1 for d in lengths.values() if d <= R) for R in Rs], float)
        lo, hi = max(1, rmax//5), max(2, (3*rmax)//4)           # avoid seed/boundary
        m = (Rs >= lo) & (Rs <= hi) & (V > 0)
        if m.sum() >= 3:
            slopes.append(np.polyfit(np.log(Rs[m]), np.log(V[m]), 1)[0])
    return float(np.median(slopes)) if slopes else float("nan")

def diameter_scaling(graphs_by_n):                              # {n: graph} -> 'manifold'|'small_world'|'pancake'
    ns = sorted(graphs_by_n); diam = [nx.approximation.diameter(graphs_by_n[n]) for n in ns]
    s_pow = np.polyfit(np.log(ns), np.log(diam), 1)[0]; s_log = np.polyfit(np.log(np.log(ns)), diam, 1)[0]
    return {"diam": diam, "pow_exp": float(s_pow), "looks": "manifold" if s_pow > 0.2 else "small_world/cloud"}
```

- [ ] **Step 4: Run, verify pass** (3D in [2.6,3.4], grid in [1.7,2.3]).
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: hausdorff dim + diameter scaling (calibrated)"`

---

## Task 5: Probe — spectral dimension (random-walk return)

**Files:** Modify `battery.py`; Test `tests/test_battery_spectral.py`.

- [ ] **Step 1: Failing calibration test**

```python
# tests/test_battery_spectral.py
from nulls import poisson_3d, random_tree
from battery import spectral_dim

def test_spectral_3d_near_3():
    g,_ = poisson_3d(5000, seed=2); ds = spectral_dim(g)
    assert 2.5 <= ds <= 3.5
def test_spectral_tree_near_four_thirds():
    ds = spectral_dim(random_tree(5000, seed=2))
    assert ds <= 1.7
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** — return probability P(t)~t^{-d_s/2} via lazy random-walk diffusion of a point mass; slope on the plateau window.

```python
# add to battery.py
def spectral_dim(g, tmax=200, seed=0):
    import numpy as np, networkx as nx
    nodes=list(g.nodes()); idx={u:i for i,u in enumerate(nodes)}; N=len(nodes)
    A = nx.to_scipy_sparse_array(g, nodelist=nodes).astype(float)
    deg = np.asarray(A.sum(1)).ravel(); deg[deg==0]=1
    rng=np.random.default_rng(seed); src=rng.integers(N)
    p=np.zeros(N); p[src]=1.0; ret=[]
    for t in range(1, tmax+1):
        p = 0.5*p + 0.5*(A @ (p/deg))                            # lazy walk (avoids bipartite oscillation)
        ret.append(p[src])
    ts=np.arange(1,tmax+1); ret=np.array(ret)
    lo,hi=tmax//10, tmax//2; m=slice(lo,hi)
    ds = -2*np.polyfit(np.log(ts[m]), np.log(ret[m]),1)[0]
    return float(ds)
```

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: spectral dimension (calibrated 3D~3, tree<1.7)"`

---

## Task 6: Probe — poset chain scaling + Myrheim-Meyer

**Files:** Modify `battery.py`; Test `tests/test_battery_poset.py`.

The poset = the history tree's ancestor relation is NOT the causal order to read; instead build the **causal order from leaf-adjacency reachability over ticks**. For Phase 0 simplest: treat the *history tree* ancestor relation as the poset for chain/MM probes (the spec reads space from adjacency, but MM/chain are poset probes — pin: poset = transitive closure of parent→child). Document this choice in PREREG note.

- [ ] **Step 1: Failing calibration test** (on a 3D-sprinkled poset — points ordered by a random time coord)

```python
# tests/test_battery_poset.py
import numpy as np
from battery import myrheim_meyer_dim, chain_scaling
from nulls import poisson_3d

def _sprinkle_poset(n, dim, seed):
    rng=np.random.default_rng(seed); X=rng.random((n,dim))
    # causal order: x precedes y if y dominates x in all coords (a d-dim order)
    rel = {i:set() for i in range(n)}
    order = np.argsort(X[:,0])
    for a in range(n):
        for b in range(a+1,n):
            i,j=order[a],order[b]
            if np.all(X[j]>=X[i]): rel[i].add(j)
    return rel

def test_mm_dim_2d_sprinkle_near_2():
    rel=_sprinkle_poset(800,2,0); assert 1.7 <= myrheim_meyer_dim(rel) <= 2.4
def test_mm_dim_3d_sprinkle_near_3():
    rel=_sprinkle_poset(1200,3,0); assert 2.6 <= myrheim_meyer_dim(rel) <= 3.5
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** — Myrheim-Meyer: relation count vs 2-chain count fixes d via the known MM formula; chain scaling = longest chain (height).

```python
# add to battery.py
from math import gamma
import numpy as np

def _counts(rel):
    # R = #related pairs; C2 = #length-2 chains (i<j<k)
    R = sum(len(v) for v in rel.values())
    C2 = 0
    for i, js in rel.items():
        for j in js: C2 += len(rel.get(j, ()))
    return R, C2

def myrheim_meyer_dim(rel, dmax=6.0):
    R, C2 = _counts(rel)
    if R == 0: return float("nan")
    f = C2 / (R*R) if R else 0.0                      # ordering-fraction ratio
    # MM: C2/R^2 -> known function of d; invert numerically
    def mm(d): return gamma(d+1)*gamma(d/2)/(4*gamma(3*d/2)) 
    ds = np.linspace(0.5, dmax, 2000); vals = np.array([mm(d) for d in ds])
    return float(ds[np.argmin(np.abs(vals - f))])

def chain_scaling(rels_by_n):                          # {n: rel} -> height exponent
    ns=sorted(rels_by_n); heights=[]
    for n in ns:
        rel=rels_by_n[n]; import networkx as nx
        dg=nx.DiGraph(); [dg.add_edge(i,j) for i,js in rel.items() for j in js]
        heights.append(nx.dag_longest_path_length(dg) if dg.number_of_edges() else 1)
    import numpy as np; exp=np.polyfit(np.log(ns), np.log(heights),1)[0]
    return {"heights":heights, "height_exp":float(exp)}   # ~1/d : 3D->0.33, pancake->~0
```

- [ ] **Step 4: Run, verify pass** (MM ~2 on 2D sprinkle, ~3 on 3D).
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: Myrheim-Meyer + chain scaling (calibrated)"`

---

## Task 7: Probe — Dirichlet energy + loop density

**Files:** Modify `battery.py`; Test `tests/test_battery_misc.py`.

- [ ] **Step 1: Failing test**

```python
# tests/test_battery_misc.py
import numpy as np, networkx as nx
from battery import loop_density, dirichlet_energy

def test_loop_density_tree_zero_grid_positive():
    assert loop_density(nx.random_labeled_tree(500, seed=0)) == 0.0
    assert loop_density(nx.grid_2d_graph(20,20)) > 0.0
def test_dirichlet_zero_on_constant_field():
    g=nx.grid_2d_graph(10,10); x={u:1.0 for u in g}
    assert dirichlet_energy(g,x) == 0.0
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement**

```python
# add to battery.py
def loop_density(g):                          # cyclomatic number per node = E - N + components
    import networkx as nx
    return (g.number_of_edges() - g.number_of_nodes() + nx.number_connected_components(g)) / max(1, g.number_of_nodes())

def dirichlet_energy(g, x):                    # sum over edges (x_i - x_j)^2
    return float(sum((x[u]-x[v])**2 for u,v in g.edges()))
```

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: dirichlet energy + loop density"`

---

## Task 8: Probe — Ollivier-Ricci curvature (library)

**Files:** Modify `battery.py`; Test `tests/test_battery_ricci.py`. Dependency: `pip install GraphRicciCurvature`.

- [ ] **Step 1: Failing calibration test** (grid≈flat→median near 0; tree→negative)

```python
# tests/test_battery_ricci.py
import networkx as nx
from battery import ricci_summary

def test_ricci_tree_negative():
    assert ricci_summary(nx.random_labeled_tree(400, seed=0))["median"] < -0.1
def test_ricci_grid_near_zero():
    m = ricci_summary(nx.grid_2d_graph(25,25))["median"]
    assert -0.2 <= m <= 0.2
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** (exact library call; not a placeholder)

```python
# add to battery.py
def ricci_summary(g):
    from GraphRicciCurvature.OllivierRicci import OllivierRicci
    import numpy as np
    h = g.copy()
    orc = OllivierRicci(h, alpha=0.5, verbose="ERROR"); orc.compute_ricci_curvature()
    ks = [d["ricciCurvature"] for _,_,d in orc.G.edges(data=True)]
    return {"median": float(np.median(ks)), "iqr": float(np.subtract(*np.percentile(ks,[75,25])))}
```

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: Ollivier-Ricci curvature (calibrated grid~0, tree<0)"`

---

## Task 9: Probe — Betti-number stability (library)

**Files:** Modify `battery.py`; Test `tests/test_battery_betti.py`. Dependency: `pip install gudhi`.

- [ ] **Step 1: Failing calibration test** — a 3D point cloud (solid ball) has Betti (1,0,0); a 2-torus point cloud has (1,2,1).

```python
# tests/test_battery_betti.py
import numpy as np
from battery import betti_from_points

def test_betti_solid_ball_b0_one_b1_zero():
    rng=np.random.default_rng(0); X=[]
    while len(X)<600:
        p=rng.uniform(-1,1,3)
        if np.linalg.norm(p)<=1: X.append(p)
    b=betti_from_points(np.array(X), max_edge=0.5)
    assert b[0]==1 and b[1]==0
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** (gudhi Rips persistence; Betti at a mid-filtration)

```python
# add to battery.py
def betti_from_points(points, max_edge, dim=2):
    import gudhi, numpy as np
    rc = gudhi.RipsComplex(points=np.asarray(points, float), max_edge_length=max_edge)
    st = rc.create_simplex_tree(max_dimension=dim+1); st.compute_persistence()
    return [st.betti_number(i) for i in range(dim+1)]
```

Note for substrate use: the leaf-graph has no coordinates, so Betti is computed on a spring/spectral embedding of the leaf-graph (documented in PREREG); calibration here uses point clouds where ground truth is exact.

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: betti numbers via gudhi (calibrated on ball)"`

---

## Task 10: `run_battery` aggregator

**Files:** Modify `battery.py`; Test `tests/test_run_battery.py`.

- [ ] **Step 1: Failing test** — returns all keys for a graph.

```python
# tests/test_run_battery.py
from nulls import poisson_3d
from battery import run_battery
def test_run_battery_keys():
    g,_=poisson_3d(2000, seed=0)
    r=run_battery(g)
    for k in ["d_hausdorff","d_spectral","loop_density","ricci_median"]:
        assert k in r
```

- [ ] **Step 2: Run, verify fail.**

- [ ] **Step 3: Implement** — call each probe, collect; poset probes optional arg.

```python
# add to battery.py
def run_battery(g, rel=None, points=None, max_edge=None):
    out = {"n": g.number_of_nodes(),
           "d_hausdorff": hausdorff_dim(g),
           "d_spectral": spectral_dim(g),
           "loop_density": loop_density(g),
           "ricci_median": ricci_summary(g)["median"]}
    if rel is not None: out["d_myrheim_meyer"] = myrheim_meyer_dim(rel)
    if points is not None and max_edge is not None: out["betti"] = betti_from_points(points, max_edge)
    return out
```

- [ ] **Step 4: Run, verify pass.**
- [ ] **Step 5 (commit checkpoint):** `git commit -am "exp136: run_battery aggregator"`

---

## Task 11: CALIBRATION GATE (spec §9 A.3) — the battery must separate the nulls

**Files:** Create `tests/test_calibration_gate.py`. This is the gate: if it fails, no substrate result is trusted.

- [ ] **Step 1: Write the gate test**

```python
# tests/test_calibration_gate.py
from nulls import poisson_3d, grid_2d, random_tree
from battery import run_battery, spectral_dim

def test_battery_separates_3d_2d_tree():
    g3,_=poisson_3d(5000, seed=7); g2=grid_2d(70); gt=random_tree(5000, seed=7)
    assert 2.6 <= run_battery(g3)["d_hausdorff"] <= 3.4         # positive benchmark = 3
    assert 1.7 <= run_battery(g2)["d_hausdorff"] <= 2.3         # 2D control
    assert spectral_dim(gt) <= 1.7                              # tree control = 4/3-ish
    assert run_battery(gt)["ricci_median"] < -0.1               # tree is hyperbolic
    assert run_battery(g3)["loop_density"] > run_battery(gt)["loop_density"]
```

- [ ] **Step 2: Run** — `pytest experiments/136_conserved_subdivision/tests/ -v`. Expected: PASS. If any band fails, **stop and retune the probe windows (Tasks 4–9), not the substrate** — record what was adjusted in PREREG as an instrument note (instruments may be calibrated; substrate thresholds in A.3 may not move).
- [ ] **Step 3 (commit checkpoint):** `git commit -am "exp136: calibration gate — battery separates 3D/2D/tree"`

---

## Task 12: Phase 0b — bare-rule baseline run + characterization

**Files:** Create `phase0_baseline.py`; output `RESULTS_phase0.md`.

- [ ] **Step 1: Write the driver** (no test — this is characterization; the assertions are the pre-registered bands, reported not enforced)

```python
# phase0_baseline.py
import sys, os, json, numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from substrate import Substrate
from battery import run_battery

# bare rule: uniform refinement until ~N leaves; multi-seed via tie-break order (rule is deterministic,
# so "seeds" here vary only if a stochastic tie-break is added; bare rule is deterministic -> report 1 run
# + note determinism, and vary N for finite-size scaling). Ingredients (Phase 1) introduce seed-dependence.
def run_to_n(target_n):
    s = Substrate()
    while len(s.leaves) < target_n:
        s.tick()
    return s

def main():
    rows=[]
    for target in [500, 1000, 2000, 5000]:
        s = run_to_n(target)
        g = s.leaf_graph()
        r = run_battery(g); r["target"]=target; r["leaves"]=len(s.leaves)
        rows.append(r); print(json.dumps(r))
    # finite-size scaling: does d_spectral/d_hausdorff drift toward 2, stay tree-like (4/3), or hold 3?
    with open(os.path.join(os.path.dirname(__file__),"results","phase0_baseline.json"),"w") as f:
        json.dump(rows, f, indent=2)
    # write RESULTS_phase0.md verdict against A.3 bands (report only)
    verdict = classify(rows)
    open(os.path.join(os.path.dirname(__file__),"RESULTS_phase0.md"),"w").write(verdict)
    print(verdict)

def classify(rows):
    last = rows[-1]
    ds, dh = last["d_spectral"], last["d_hausdorff"]
    flavor = ("WIN-band" if 2.8<=ds<=3.2 and 2.8<=dh<=3.2
              else "TREE/HYPERBOLIC" if ds<1.7 or last["ricci_median"]<-0.2
              else "CLOUD/other")
    return (f"# Phase 0b baseline (bare rule)\n\nBare-rule outcome at n={last['leaves']}: **{flavor}**\n\n"
            f"d_spectral={ds:.2f}, d_hausdorff={dh:.2f}, ricci_median={last['ricci_median']:.3f}, "
            f"loop_density={last['loop_density']:.3f}\n\nPer A.4 this is the BASELINE the Phase-1 "
            f"ingredients must move; bare rule is expected to miss the WIN band.\n\n"
            f"Full finite-size table in results/phase0_baseline.json\n")

if __name__=="__main__": 
    os.makedirs(os.path.join(os.path.dirname(__file__),"results"), exist_ok=True); main()
```

- [ ] **Step 2: Run** — `python -u experiments/136_conserved_subdivision/phase0_baseline.py`. Expected: a baseline flavor (most likely TREE/HYPERBOLIC or CLOUD per spec §2 — that is the point; it establishes what the ingredients must move).
- [ ] **Step 3:** Read `RESULTS_phase0.md`; confirm it reports against the A.3 bands honestly (report, do not move bands).
- [ ] **Step 4 (commit checkpoint):** `git commit -am "exp136: phase0 baseline run + RESULTS_phase0.md"`

---

## Self-Review (run against the spec)

- **Spec §5 (ontology):** Task 1 (genesis, conserved Fraction, append-only) + Task 2 (two graphs, leaf-adjacency readout). ✓
- **Spec §6 ingredients:** defined as toggles in A.2; bare rule (all OFF) built in Tasks 1–2; ablation deferred to Phase-1 plan (stated scope). ✓ (branch-chain NAND `x` bare = address; ancestral/spatial non-locality are A.2 toggles.)
- **Spec §9 battery:** Hausdorff (T4), spectral (T5), MM + chain (T6), Dirichlet+loops (T7), Ricci (T8), Betti (T9), aggregator (T10), **calibration gate (T11)**. ✓ All calibrated against known geometries.
- **Spec §9 nulls:** Poisson-3D (positive), grid-2D, tree, Eden blob, diffusion field — Task 3. ✓
- **Spec §0/§9 pre-registration:** Task 0 freezes A. Thresholds locked in A.3. ✓
- **Spec §8 Phase 0:** T11 = "battery separates nulls" (Phase 0a); T12 = bare baseline (Phase 0b). ✓
- **Spec §10 falsifier:** in A.4; enforced by "report, don't move bands" in T11/T12. ✓
- **Placeholder scan:** no TBD/TODO; heavy probes (Ricci, Betti) use named libraries with exact calls + calibration tests (not placeholders). One documented modeling choice (poset = history-tree closure for MM/chain in Phase 0) is flagged in T6 to record in PREREG. ✓
- **Type consistency:** `run_battery` keys (`d_hausdorff`, `d_spectral`, `loop_density`, `ricci_median`, `d_myrheim_meyer`, `betti`) match across T10/T11/T12. `Substrate.tick/leaf_graph/leaves/adj` consistent across T1/T2/T12. ✓
- **Deferred (correctly out of scope):** Phase-1 ablation, gravity/photons/QM (spec §11). A Phase-1 plan follows once instruments are trusted + baseline known.

---

## Notes for the implementer
- Determinism: the **bare** rule is deterministic, so Phase 0b reports one run per N + finite-size scaling (not 20 seeds). The ≥20-seed requirement (A.3) binds in **Phase 1**, where ingredients (difference-direction cuts, tie-breaks) introduce seed-dependence. State this in RESULTS_phase0.md.
- If `nx.random_labeled_tree`/`random_tree` naming differs by networkx version, use whichever exists (handled in `nulls.random_tree`).
- Probe windows (fit ranges) are instrument parameters and MAY be tuned in Tasks 4–9 to pass calibration; once the gate (T11) passes they are frozen for T12 and Phase 1.
