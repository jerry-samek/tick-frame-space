"""Conserved-subdivision substrate: history tree (bookkeeping) + leaf boundary-adjacency (space).

Genesis = one cell of measure 1. Each tick subdivides leaves; measure conserved exactly (Fraction).
Bare rule (Phase 0): uniform refinement, equal halves, indiscriminate ("all-glue") adjacency.
The tick() hooks (select/split/glue) are where Phase-1 ingredients plug in.
"""
from fractions import Fraction
from dataclasses import dataclass, field
import networkx as nx


@dataclass
class Cell:
    id: int
    measure: Fraction
    address: str                       # bit-string path root->leaf ("" at genesis)
    parent: int | None
    children: list[int] = field(default_factory=list)


class Substrate:
    def __init__(self):
        self.nodes: dict[int, Cell] = {}
        self._next = 0
        root = self._new(Fraction(1), "", None)
        self.leaves: list[Cell] = [root]
        self.adj: dict[int, set[int]] = {root.id: set()}
        self._all_ids_before_last_tick: set[int] = set()

    def _new(self, measure, address, parent):
        c = Cell(self._next, measure, address, parent)
        self.nodes[c.id] = c
        self._next += 1
        return c

    def node_count(self):
        return len(self.nodes)

    def tick(self, select=None, split=None, glue=None):
        """One tick. Defaults = bare rule.
        select(leaves)->subset of leaves to split; split(cell)->[(measure,bit),...];
        glue(a_child,b_child,a_parent,b_parent)->bool (whether to add a leaf-adjacency edge).
        """
        self._all_ids_before_last_tick = set(self.nodes)
        select = select or (lambda ls: ls)
        split = split or (lambda c: [(c.measure / 2, "0"), (c.measure / 2, "1")])
        glue = glue or (lambda a, b, ap, bp: True)

        to_split = set(c.id for c in select(self.leaves))
        kids: dict[int, list[int]] = {}
        new_leaves: list[Cell] = []
        for c in self.leaves:
            if c.id in to_split:
                ks = []
                for m, bit in split(c):
                    child = self._new(m, c.address + bit, c.id)
                    c.children.append(child.id)
                    ks.append(child.id)
                    new_leaves.append(child)
                kids[c.id] = ks
            else:
                new_leaves.append(c)
                kids[c.id] = [c.id]

        new_adj: dict[int, set[int]] = {c.id: set() for c in new_leaves}
        # siblings mutually adjacent
        for cid, ks in kids.items():
            for a in ks:
                for b in ks:
                    if a != b:
                        new_adj[a].add(b)
        # inherit parent-neighbor adjacency (subject to glue)
        for cid, ks in kids.items():
            for nbr in self.adj.get(cid, ()):
                for a in ks:
                    for b in kids.get(nbr, ()):
                        if a != b and glue(a, b, cid, nbr):
                            new_adj[a].add(b)
                            new_adj[b].add(a)
        self.adj = new_adj
        self.leaves = new_leaves

    def leaf_graph(self) -> nx.Graph:
        g = nx.Graph()
        g.add_nodes_from(c.id for c in self.leaves)
        for a, nbrs in self.adj.items():
            for b in nbrs:
                g.add_edge(a, b)
        return g

    def poset_relations(self) -> dict[int, set[int]]:
        """Transitive closure of parent->child over CURRENT leaves' ancestry is trivial;
        for MM/chain probes we use the full history-tree ancestor relation among ALL nodes
        (PREREG modeling note). Returns {id: set(descendant ids)} via parent links."""
        rel: dict[int, set[int]] = {nid: set() for nid in self.nodes}
        # child is 'after' parent: relation parent -> child (and transitively)
        # build descendants by walking children
        def descendants(nid):
            out = set()
            stack = list(self.nodes[nid].children)
            while stack:
                d = stack.pop()
                if d not in out:
                    out.add(d)
                    stack.extend(self.nodes[d].children)
            return out
        for nid in self.nodes:
            rel[nid] = descendants(nid)
        return rel
