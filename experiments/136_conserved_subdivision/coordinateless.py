"""Coordinateless conserved-subdivision substrate (Phase 1, per the 2026-06-05 reframe).

NO coordinates, NO dyadic boxes, NO spatial axes. A cell is just its ADDRESS = the replayed
memory (bit-string path root->leaf). "Space" is a pure connection-graph; edges come from
MEMORY-RESONANCE (a re-meeting rule on addresses). Dimension is the MEASURED intrinsic
dimension of that graph (battery d_s/d_H) — an objective relational property, read not invented.

Phase 1a landscape probe: uniform refinement (Arm U) + several resonance rules -> measure d_s.
Question: does any coordinateless memory-resonance rule lift off K_N to a finite d>1?
"""
from fractions import Fraction
import networkx as nx


def uniform_leaves(depth):
    """All 2**depth addresses at a given depth (uniform refinement = Arm U)."""
    return [format(i, "0{}b".format(depth)) for i in range(2 ** depth)]


def measure_conserved(depth):
    """Sanity: uniform leaves each carry 1/2**depth; total == 1 exactly."""
    return sum(Fraction(1, 2 ** depth) for _ in range(2 ** depth)) == Fraction(1)


def _flip(c):
    return "1" if c == "0" else "0"


# ---- memory-resonance edge rules (all coordinateless, on equal-depth addresses) ----
def edges_siblings(leaves):
    """Only siblings (share all but last bit). Perfect matching -> disconnected."""
    s = set(leaves); E = []
    for a in leaves:
        b = a[:-1] + _flip(a[-1])
        if b in s and a < b:
            E.append((a, b))
    return E


def edges_hamming1(leaves):
    """Differ in exactly one bit (hypercube Q_n). Degree = depth."""
    s = set(leaves); E = []
    for a in leaves:
        for i in range(len(a)):
            b = a[:i] + _flip(a[i]) + a[i + 1:]
            if b in s and a < b:
                E.append((a, b))
    return E


def edges_mirror(leaves):
    """Shared prefix [0,p), opposite at p, COMPLEMENT suffix (p,n):
    two sub-streams that diverged at p and then mirrored each other. Degree = depth."""
    s = set(leaves); E = []
    for a in leaves:
        n = len(a)
        for p in range(n):
            suffix = "".join(_flip(c) for c in a[p + 1:])
            b = a[:p] + _flip(a[p]) + suffix
            if b in s and a < b:
                E.append((a, b))
    return E


def edges_lastk(leaves, k=3):
    """Local: differ in exactly one of the LAST k bits AND agree on the first n-k
    (a k-hypercube within each shared (n-k)-prefix block). Connected only within blocks."""
    s = set(leaves); E = []
    for a in leaves:
        n = len(a)
        for i in range(max(0, n - k), n):
            b = a[:i] + _flip(a[i]) + a[i + 1:]
            if b in s and a < b:
                E.append((a, b))
    return E


RULES = {
    "hamming1(hypercube)": edges_hamming1,
    "mirror(prefix+complement)": edges_mirror,
    "lastk=3(local)": lambda lv: edges_lastk(lv, 3),
    "lastk=5(local)": lambda lv: edges_lastk(lv, 5),
}


def build_graph(depth, edge_fn):
    leaves = uniform_leaves(depth)
    g = nx.Graph()
    g.add_nodes_from(leaves)
    g.add_edges_from(edge_fn(leaves))
    return g


# ---- Arm F: capacitor-driven async forking (coordinateless) ----
def _resonant(a, b):
    """Variable-depth memory-resonance: lengths differ by <=1 AND Hamming-1 over the
    shorter length (share a prefix-frame, differ in one distinction)."""
    L = min(len(a), len(b))
    if abs(len(a) - len(b)) > 1:
        return False
    return sum(1 for k in range(L) if a[k] != b[k]) == 1


def _resonance_degree(leaves):
    deg = {a: 0 for a in leaves}
    n = len(leaves)
    for i in range(n):
        a = leaves[i]
        for j in range(i + 1, n):
            b = leaves[j]
            if _resonant(a, b):
                deg[a] += 1; deg[b] += 1
    return deg


def run_arm_f(threshold, target_n=1024, max_ticks=300):
    """Each leaf is a capacitor: charge += local difference (resonance degree) each tick;
    fires (forks into +'0'/'1', charge reset) when charge >= threshold. Async, global-state-independent."""
    leaves = ["0", "1"]                       # genesis: existence + first boundary
    charge = {"0": 0.0, "1": 0.0}
    for _ in range(max_ticks):
        if len(leaves) >= target_n:
            break
        deg = _resonance_degree(leaves)
        new = []
        for a in leaves:
            charge[a] = charge.get(a, 0.0) + (deg[a] if deg[a] > 0 else 0.5)
            if charge[a] >= threshold:
                for bit in "01":
                    c = a + bit; new.append(c); charge[c] = 0.0
                charge.pop(a, None)
            else:
                new.append(a)
        leaves = new
    return leaves


def build_graph_var(leaves):
    g = nx.Graph(); g.add_nodes_from(leaves)
    n = len(leaves)
    for i in range(n):
        a = leaves[i]
        for j in range(i + 1, n):
            b = leaves[j]
            if _resonant(a, b):
                g.add_edge(a, b)
    return g
