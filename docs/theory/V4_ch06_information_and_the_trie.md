# Chapter 6: Information and the Trie

*Carried, mostly intact, from V3 ch005 (Information and the Trie), reframed
inside-out. Sources: RAW 113 (Semantic Isomorphism), RAW 114 (Shared Prefix and
Particle Identity).*

---

## 6.1 The graph is a trie

The three-state alphabet (Chapter 1), applied recursively under the append-only
axiom, builds a **trie** — a prefix tree — and this is not an analogy imposed from
outside. It **is** the graph, read as an information structure:

- **Same** traverses shared branches — a common prefix, no new structure.
- **Different** is a branch point — the longest common prefix ends, two suffixes
  begin.
- **Unknown** is the unwritten frontier — the trie's null pointers, not yet
  instantiated.

Because the substrate only appends (Chapter 1), the trie is permanent: every branch
point ever created still exists, every shared prefix is still shared. The graph does
not need to be *reorganized* into a trie; the three-state dynamics have been building
one since the first deposit. The physical operations of Chapters 2–4 and the
information operations here are the **same operations in two vocabularies** — this is
the semantic isomorphism.

## 6.2 Compression is free, and maximal

Same creates no structure, so identical histories do not duplicate structure: N
paths that share a prefix of depth D cost D nodes, not N·D. No compression *step* is
run — the universe compresses itself by the act of following familiar paths, and the
result is maximal (each divergence stored exactly once, all non-divergent history
shared). There is no redundancy left to remove.

## 6.3 Similarity search is the movement rule — and it is gravity

The laziest-connector movement rule (Chapter 1) *is* a trie similarity search:
descend from where you are, follow matching branches (Same) as deep as you can, stop
at a mismatch (Different) or at unwritten space (Unknown). The depth of the Same-run
is the degree of similarity.

| Trie similarity search | Substrate movement |
|---|---|
| Descend from root | Pattern traverses the graph |
| Follow matching branches | Same fires: follow the laziest connector |
| Stop at mismatch | Different fires: diverge |
| Stop at null pointer | Unknown fires: write the frontier |
| Depth of match = similarity | Depth of Same-run = familiarity |

So **retrieval and physics are one operation.** Gravity (Chapter 4) is the substrate
performing a similarity search: massive bodies are deep, well-established prefixes
(long runs of familiar deposits many paths share), and an arriving pattern descends
into that shared prefix because that is where Same fires strongest. In the inside-out
reading this is the *same fact* as the ambient-shadow force of Chapter 4 — "route
toward the deepest match" and "be pushed into the renewal shadow" are the physics and
information faces of one act.

## 6.4 Writing is the only creative act; equilibrium is unreachable

Of the three states, only **Unknown** creates genuinely new structure from virgin
substrate — and every Unknown write creates *more* frontier (new connectors to
further unvisited nodes). So the frontier regenerates itself faster than any
equilibrium search can consume it. The count of Different branch points grows
monotonically and without bound: **the universe's information content increases at
every tick, does not plateau, and cannot decrease.** Learning is exactly the
conversion of Unknown into Same-or-Different. The universe is not winding down; its
information capacity is still growing, and is largest at the always-young frontier.

## 6.5 Shared-prefix particle identity

Every path begins at the one root and shares early nodes before diverging. This gives
a geometric account of why identical particles are identical: **all electrons share
the same trie prefix.** An electron is not a thing-with-properties; it is a *prefix
any path can run through*, and the properties are the deposits along the shared
nodes. Two electrons are indistinguishable because they share **literal substrate
nodes** in their causal histories (the same nodes, not copies), so there is nothing
to tell apart below the divergence point.

This is Wheeler's single-electron insight with the mechanism corrected: not one
electron threading forward and backward through time (which would demand exact
matter–antimatter cancellation, unobserved), but **one electron *prefix* in the
trie** that every electron-path shares. Wheeler was right that all electrons are "the
same thing"; the mechanism is shared causal structure, not time travel.

## 6.6 Status and open questions

The trie is a **logical consequence** of the three-state alphabet plus append-only,
not an independent hypothesis — so its support is the support for the three-state
dynamics, and it has **not** been independently validated as a data structure in
simulation. Honest open items carried from V3:

- **The formal comparison operator** (what exactly makes Same vs Different) is
  undefined, and this blocks a faithful trie simulation. *This is the framework's
  most fundamental gap.*
- **Bosonic vs fermionic symmetry:** shared-prefix explains indistinguishability but
  not why two symmetry classes exist. Speculative candidate only.
- **Trie width-vs-depth tension** (~10⁸⁰ leaves vs ~10⁶¹ depth): three candidate
  resolutions, none derived.
- **Snapshot drift rate** predicted = local Different-rate; not yet measured.

None of the validating experiments (trie-based simulation, shared-prefix
measurement, information-growth counting, compression-ratio measurement) have been
run.

---

*See also: RAW 113, RAW 114; V4 Chapter 1 (the alphabet), Chapter 4 (gravity as
retrieval), Chapter 5 (path = identity, memory). Full V3 treatment preserved in
`v3_archive/V3_ch005_information_and_trie.md`.*
