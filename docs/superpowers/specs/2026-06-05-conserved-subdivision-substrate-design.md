# Conserved-Subdivision Substrate — Design Spec

### *Does a local, difference-driven wrapping rule select emergent 3D space?*

**Date:** 2026-06-05
**Status:** Design (approved in brainstorm). Awaiting user spec-review, then implementation plan.
**Tentative experiment dir:** `experiments/136_conserved_subdivision/` (created at implementation).
**Provenance:** Idea by Tom (time-as-wrapping/division). Spec by Claude. Grounded by two literature passes (2026-06-05) — see §12.
**Supersedes nothing. Confronts:** RAW 401 §1 settled walls; RAW 402; the 118–135 arc.

---

## 0. The meta-goal of this spec

Previous experiments (118–135) repeatedly failed not for lack of ideas but for **under-specification**: criteria moved after seeing data, single-seed results were published then overturned, mechanisms were named that never engaged, and negatives were reframed instead of accepted (see RAW 401/402). **This spec is written to be un-gameable:** the observable, the nulls, the pass thresholds, the seed count, and the program falsifier are all fixed *here, before any code*. The implementation plan may choose functional forms, but it may **not** change anything in §7–§9 after seeing results. Any deviation is logged as a separate exploratory finding, never the headline.

---

## 1. The idea (faithful one-paragraph statement)

Time is not a separate axis; it is **wrapping/growth**. The substrate is **one conserved whole** that, each tick, **adds boundaries** — partitioning existing regions into more regions — and *nothing is ever created or subtracted, only cut* ("infinity and new infinity": you cannot make a bigger whole, only finer partitions). Total measure is fixed forever; region count grows. Growth is locally invisible because the measuring apparatus subdivides too (only dimensionless ratios are observable); the things that *don't* subdivide (photons / empty space) are what reveal it. **Space, motion, gravity, GR, QM are not substrate properties — they are reconstructed by reading the grown structure from the leaves (now) back toward the root (origin).** Where boundaries are added is decided by a **local, mechanical, NAND-gate-like "observer"** — the trit (Same/Different/Unknown) — with no global view and nothing anthropomorphic. **This experiment tests only the foundation: does that local difference-driven subdivision produce emergent 3D space at all?** Gravity, photons/redshift, and QM are explicitly deferred (§11).

---

## 2. Honest positioning (what is novel, what is borrowed, what the odds are)

Per the scientist discipline, this is stated against named prior art, not in a vacuum.

| Pillar of the idea | Owner in the literature | Status |
|---|---|---|
| Append-only frontier growth + geometry-as-readout (claims 1, 4 / "can't subtract, only wrap") | **Causal-set Classical Sequential Growth**, Rideout–Sorkin 1999 (gr-qc/9904062) — the near-identical twin | Borrowed ontology. CSG's fixed-past = "only wrap." |
| Conserved division (each cut splits a measure, total fixed) | **Microcanonical multiplicative cascade**, Mandelbrot 1974 | Borrowed; its lognormal/multifractal/self-similar output is a *known null*, not new physics. |
| Growth invisible because rulers co-grow (claim 3) | **Wetterich 2013 (1303.6878), Dicke, shape dynamics** | Borrowed; conformally equivalent to FRW — *empirically null unless it predicts a discreteness signature* (deferred with photons, §11). |
| Growth pushes you "up" = gravity (claim 5) | **MTW equivalence principle** (legit weak form) / **McCutcheon Expansion Theory** (refuted strong form) | Deferred (§11); uniform growth provably cannot give attraction (Price–Romano). |

**The one genuinely novel seam:** a **deterministic, exactly-conserving, *local-rule*** growth law inside the causal-set ontology, where a **local difference-driver selects manifoldlike structure**. No published *local, append-only* rule has ever been shown to select 3+1D — CSG itself falls into the Kleitman–Rothschild pancake regime, and the only *demonstrated* escape (Benincasa–Dowker–Glaser link action; Carlip–Loomis 2018/2022) is **global and energetic**. So "a local difference-driver biases growth away from pancakes and toward flat 3D" is **the central falsifiable hypothesis** of this experiment, not its premise.

**Honest odds (stated up front, in the doc, per RAW 401):**
- **~10–20%** — a clean, pre-registered 3D plateau (d_s and d_H both ≈3, stable across a decade and across seeds, with stable 3-manifold homology).
- **~50–60%** — a third face of the same trap: pancake (if equalization wins entropically), hyperbolic tree, or featureless cloud (if it over-smooths).
- **~20–30%** — an instructive partial result (finite emergent dimension but hyperbolic; or a 3D-ish window that drifts to ~2 at scale — itself a publishable diagnosis if instrumented).

A clean negative here is **genuinely informative** (no local rule has ever done this), which is why it is worth running despite the low prior.

---

## 3. Why this is a different attack than 118–135

It sidesteps the three RAW 401 walls from a new side:
- **Conservation-flatness (killed 133):** "expansion" is conservative *division*, so growth and exact conservation coexist by construction — expansion is a *readout*, not an addition.
- **Force-at-a-distance / locality (Marolf):** no bulk force; everything is local growth. (Gravity, when we get to it, is local proper-acceleration, not action-at-a-distance.)
- **The readout (the RAW 132 §3.5 gap every prior experiment fumbled):** here the readout *is* the physics and is specified and measured explicitly (§5–§6 and §9).

And it directly confronts the two new walls the literature surfaced — tree→hyperbolic and the pancake trap — instead of walking into them (as Exp 131 did).

---

## 4. The two failure modes the rule is built to avoid

The literature is blunt that the rule **as literally named ("equalize") is self-defeating**, and gives the two-sided danger:

1. **Over-equalization → featureless cloud.** Pure equalization = graph diffusion = projection onto the Laplacian kernel = homogenization (GNN over-smoothing theorem; Oono–Suzuki, Cai–Wang 2020). **This is precisely the in-house NAND "cloud-with-clumps"** (`project_nand_cloud_artifact`). A faithful equalizer reproduces the artifact from a new direction.
2. **Pure subdivision → tree → hyperbolic.** Subdividing one region with parent→child links alone is a tree (spectral dim 4/3; Krioukov 2010; **Exp 131 confirmed in-house**). Reading leaf-boundary-adjacency only helps if non-sibling leaves **glue into loops**.

The mechanism in §6 is therefore explicitly an **anti-diffusion, loop-building, layering-penalizing** rule — not an equalizer in the naïve sense.

---

## 5. Substrate ontology

- **Genesis (forced, no scaffold):** tick 0 = one cell holding the whole measure (μ=1) — "existence." Tick 1 = the **first boundary**, splitting it into two cells (the first distinction, 1=1; RAW 117/122). Nothing may be seeded beyond this. **3D, if it appears, must EMERGE; it is never assumed.**
- **Conserved quantity:** total measure Σ_leaves μ(c) = 1 at every tick, exactly (microcanonical — children's measures sum *exactly* to the parent's, not in expectation). This is the headline differentiator vs CSG/Wolfram/graphity, which conserve no global sum.
- **Append-only:** boundaries, once recorded, are permanent. No coarsening, no averaging, no deletion ("can't subtract, only wrap").
- **Two graphs, kept distinct:**
  - **History tree** — parent→children; root = origin, depth = birth tick. *Bookkeeping only; never read as space.*
  - **Leaf boundary-adjacency graph** — which current leaves share a boundary *now*. **This is "space."** The readout (§6.4) operates only on this graph.

---

## 6. The division rule (the five required ingredients)

The implementation plan pins functional forms; the spec fixes the **properties the rule must satisfy** (each is independently ablatable in Phase 1, §8). Each leaf's compared feature `x(c)` is its **accumulated branch chain** (equivalently its trie-path / boundary-address; see §6.1): Same/Different between neighbors is read off where their chains diverge. The exact chain-construction (how branch structure builds the circuit) and genesis of the first distinction are pinned in §13.1.

**6.1 The observer = a branch-history NAND-chain (not a single NAND).** The classifier at a leaf is **not** a flat single-gate comparison; it is a **chain of NANDs whose structure is the leaf's own lineage** — the path of cuts from root to that leaf. The classification a leaf performs is therefore conditioned on its *entire branch*, and the circuit *deepens* as the tree grows. This is exactly the **trie-path classifier already operational in `trie-memory`** (RAW 133 §10.6; RAW 114/123/125): two leaves are Same/Different by where their chains agree/diverge (shared-prefix depth). NAND is functionally complete, so the chain is fully mechanical — no global state, no anthropomorphism.
This supplies the **non-locality the pancake-escape requires (Surya 2011)** along the **lineage/depth**, and because a history-dependent chain is *not* memoryless, it structurally resists the diffusion→cloud collapse (it cannot simply relax to the neighbor average). **Open, hence ablated (§8):** ancestral (branch-depth) non-locality may or may not be sufficient on its own; a finite-range **spatial-neighborhood** smearing (Surya's ε) is the alternative/additional source and is tested separately.

**6.2 Cut where Different; record, never average.** A boundary is inserted where a cell's neighborhood is **Different**; Sames get no cut; the unprocessed frontier is **Unknown**. The recorded boundary is **preserved by a residual/identity term** so later comparisons cannot wash it out. *Early failure detector:* Dirichlet energy `E = Σ_{i~j}(x_i − x_j)²` of the leaf field must stay bounded away from zero; exponential decay = collapse to the cloud (caught in the first ticks).

**6.3 Cut *direction* from local difference geometry** (not fixed dyadic bisection). Per Verma–Kpotufe–Dasgupta 2012, splits aligned with the principal-difference axis track **intrinsic** dimension; axis-aligned/recursive bisection locks onto ambient/pancake behavior. The trit chooses **where/along-what** to cut, not merely **whether**.

**6.4 Build loops (escape the tree).** When a cut is made, non-sibling leaves that come to share the new boundary are **glued** into the leaf-adjacency graph as first-class edges. **Loop density on leaf-adjacency is a primary order parameter** and must grow; staying tree-like ⇒ hyperbolic wall.

**6.5 Weakly-non-local layering penalty (local surrogate for the BDG cost).** Kleitman–Rothschild pancakes win by piling up tiny (2–3-element) relations (height≈3, width≈n/2). The rule must make cuts that create many short/small-cardinality relations **costly**, and **favor cuts that lengthen chains (causal depth) over widening antichains** — and **explicitly penalize negative curvature** (Ollivier–Ricci on leaf-adjacency) so it targets *flat* 3D rather than the generic hyperbolic attractor (Bianconi NGF's default).

**Readout (used by all measurements):** "space" = the leaf boundary-adjacency graph at a given tick. Distances = graph hops on it. Dimension/curvature/homology are measured on it. The history tree is never read as space.

---

## 7. Central hypothesis & pre-registered outcomes (one win, three failure modes)

**H (central, falsifiable):** *A local, finite-range, difference-driven, loop-building, layering-penalizing conserved-subdivision rule biases the grown structure away from the Kleitman–Rothschild pancake and the hyperbolic-tree attractors and toward a stable, flat, 3-dimensional leaf-adjacency space — a thing no purely local append-only rule has been shown to do.*

| Outcome | Reading | Signature (all pre-registered in §9) |
|---|---|---|
| **WIN** | emergent flat 3D | d_s and d_H both 3±0.2, plateau over ≥1 decade, matching; KR height ~ n^(1/3); Ollivier–Ricci ≈0; loop density growing; Dirichlet energy sustained; 3-manifold Betti numbers stable across seeds & thickening; **survives finite-size scaling to n ≫ 100** |
| **TRAP-pancake** | layered/2D | interval spectrum piles up at m=2,3; MM dim ~2.2–2.4; height≈const; ordering-fraction plateau |
| **TRAP-hyperbolic** | tree/small-world | d_s→4/3; diameter ~ log N; Ollivier–Ricci systematically negative; loop density ~0 |
| **CLOUD** | over-equalization (NAND-redux) | Dirichlet energy → 0; no rigid interval spectrum; seed-dependent; d_H ≠ d_s; isotropic everywhere (⟨cos²θ⟩≈1/3, the v11 Phase-6 failure value) |

---

## 8. Staged, null-first plan (ablation, not all-at-once)

Throwing all five ingredients in at once tells us nothing about which mattered. Build the null, then add ingredients one at a time, each with a **pre-registered prediction** of how it should move the probes.

- **Phase 0 — baselines + nulls.** (a) Build the three null models of §9 and the full measurement battery; verify the battery cleanly separates Poisson-3D (positive) from Eden/KPZ-blob and pure-diffusion (negatives). (b) Run the **bare** rule (6.2 only: cut-at-Different, no direction/loops/penalty) and record where it lands — expected: tree/hyperbolic or cloud. This establishes the baseline the ingredients must move.
- **Phase 1 — ingredient ablation.** Add, one at a time and cumulatively, in this order, each with a pre-registered predicted effect on the probes: (i) non-locality — tested as two separable sources, **ancestral branch-chain depth** vs **spatial-neighborhood smearing** (6.1), to learn which (if either) is needed; (ii) difference-direction cuts (6.3); (iii) loop-gluing (6.4); (iv) layering + curvature penalty (6.5). Report the dimension-probe trajectory after each. The deliverable is *which ingredient(s), if any, move the structure toward 3D*, with finite-size scaling.
- **Phase 2+ (DEFERRED, only if Phase 1 reaches a stable flat 3D):** photons/redshift (non-dividing regions), then mass-sourced inhomogeneous division rate → gravity (the equivalence-principle test, with its own pre-registered slope/tidal falsifier). Not in scope now.

---

## 9. Pre-registered measurement battery (LOCKED)

Three nulls; the driven substrate must be **rejected from all three** and **match the positive benchmark within fluctuations**. **Lock pass thresholds and seed count before running** (Exp 135 skeptic discipline). Seeds: **≥20** for every reported number; report median + IQR; **no single-seed headline**.

**Nulls:** (a) **Poisson sprinkling** of N points into the candidate 3D continuum — *positive benchmark*; (b) **Eden/KPZ compact blob** — "cloud-with-clumps" negative; (c) **pure-diffusion homogenized field** — over-smoothing negative.

**Probes (≥2 dimension probes must converge on 3, with thresholds):**
1. **Myrheim–Meyer interval-abundance spectrum** (Glaser–Surya 2013) on the poset — the single most diagnostic test and the cost the driver should minimize. Pass = rigid smooth curve matching the 3-sprinkling; pancake = m=2,3 pile-up, MM d≈2.2–2.4.
2. **KR longest-chain scaling** — height ~ n^(1/3) (3D) vs ≈const (pancake); ordering fraction r vs n.
3. **Spectral dimension** d_s from random-walk return P(σ)~σ^(−d_s/2) on leaf-adjacency — pass = plateau **3±0.2 over ≥1 decade** (CDT-style UV dip to ~2 allowed); tree = 4/3.
4. **Hausdorff** d_H from V(R)~R^d_H on leaf-adjacency, **require d_H≈d_s** (decoupling check); graph diameter vs N (N^(1/3) manifold / log N cloud / const pancake).
5. **Dirichlet-energy trace + loop density** — energy bounded away from 0 (no over-equalization); loop density growing (escapes tree).
6. **Ollivier–Ricci curvature distribution** on leaf edges — concentrated near 0 (flat) vs systematically negative (hyperbolic) vs broad bimodal (clumpy); plus the in-house ⟨cos²θ⟩ anisotropy probe (isotropic ≈1/3 everywhere = featureless, the v11 Phase-6 value).
7. **Stable 3-manifold homology** of thickened antichains (Major–Rideout–Surya 2009) + **multi-seed finite-size scaling** — sharp reproducible Betti numbers, clean scaling. A single clumpy snapshot is exactly what the artifact produces; **demand convergence, not one picture.**

---

## 10. Program falsifier (per RAW 401 §5)

> If the **full** five-ingredient driven rule, run **to scale (n ≫ 100)** and **across ≥20 seeds**, still lands in pancake, hyperbolic, or cloud on the locked battery — we **accept that a local conserved-subdivision rule cannot select flat 3D**, record it as a clean negative (informative: no local rule has), and **stop**. We do **not** reframe it as a special case of an un-built successor substrate, and we do **not** add a sixth ingredient post hoc to chase a 3D signal. A new attempt would require explicitly surrendering a named commitment (e.g. go global/energetic like BDG, or abandon strict locality) — stated in advance.

---

## 11. Scope — explicitly deferred (YAGNI)

Not in this experiment: gravity (claim 5), photons / redshift / "growth invisibility" observability (claim 3), QM/collapse, matter–antimatter, the equivalence-principle proper-acceleration test. All depend on first having an emergent space; none is worth building until §7 returns WIN. This deferral is itself a guard against the 118–135 pattern of reaching for the whole theory before the foundation holds.

---

## 12. Related work (citations to carry into the writeup)

- Rideout & Sorkin 1999, *Classical sequential growth dynamics for causal sets*, gr-qc/9904062 — closest program (and cautionary: lands in KR regime).
- Bombelli, Lee, Meyer, Sorkin 1987 — causal sets; "Order + Number = Geometry."
- Kleitman & Rothschild 1975 — asymptotic dominance of 3-layer posets (the pancake trap).
- Benincasa & Dowker 2010; Carlip–Loomis 2018/2022; Carlip 2024 review — discrete action suppressing non-manifoldlike orders (the *global* escape).
- Surya 2011 — 2D causal-set phase transition; non-locality parameter needed (strict locality insufficient).
- Glaser & Surya 2013 — interval-abundance spectrum (manifoldlikeness discriminator).
- Major, Rideout & Surya 2009 — spatial homology / manifoldlikeness certification.
- Verma, Kpotufe & Dasgupta 2012 — partition trees track intrinsic dimension via difference-aligned cuts.
- Bianconi & Rapisarda 2015 — Network Geometry with Flavor: local growth → finite emergent dimension (generically hyperbolic).
- Krioukov et al. 2010; Destri–Donetti 2002 — tree/network hyperbolicity, spectral dim 4/3.
- Oono–Suzuki 2020; Cai–Wang 2020 — GNN over-smoothing theorem (the cloud failure).
- Mandelbrot 1974 — microcanonical multiplicative cascade (the conserved-division null).
- Wetterich 2013 (1303.6878); Dicke — scale-invisibility / "universe without expansion" (deferred claim 3).
- Price & Romano gr-qc/0508052 — expansion does not bind local systems (deferred claim 5).
- In-house: RAW 401/402 (settled walls, retractions); Exp 131 (tree ≠ 3D); Exp 133 (integer conservation, flat field); `project_nand_cloud_artifact` (the cloud failure); Exp 135 skeptic-pass (pre-registration discipline).

---

## 13. Open items for the implementation plan (pinned there, pre-registered before running)

These are *functional-form* choices the plan must fix and pre-register; none may change after seeing results:
1. The cell feature `x(c)` = **branch-history NAND-chain / trie-path** (§6.1): exactly how the branch structure builds the chain (the key expressivity choice — from a near-flat gate up to a full path-dependent circuit; constrain it so it cannot overfit toward a 3D signal), how genesis assigns the first distinction, and how Same/Different/Unknown read off chain divergence. This reintroduces history at the cell level, but it is a **readout of the permanent branch, not new mutable memory** (append-only-consistent); build incrementally (child chain = parent chain + one gate).
2. The exact Same/Different/Unknown thresholds and the smearing range ε.
3. The cut-direction estimator (principal-difference axis) and how a cut updates leaf-adjacency (the loop-gluing rule).
4. The layering-penalty and curvature-penalty functional forms and their (pre-registered) weights.
5. N-schedule for finite-size scaling and the locked numeric pass thresholds for each probe.
6. Implementation substrate/representation (poset + leaf-adjacency graph; vectorized vs object) and performance budget.
