# Exp 138 P1d — Does Geometrogenesis Require Annealing, or Does Forward Re-Branching Suffice?

**Date:** 2026-07-12
**Status:** Design approved (Tom, 2026-07-12). Next: implementation plan.
**Question:** Reaching the geometric phase needs *some* way for structure to reorganize. Does it require **mutation of the frozen past** (equilibrium annealing — forbidden by the immutable-past axiom), or does **forward-only re-branching** (immutable structural sharing — reading old commits and building new branches on them) suffice? This tests RAW 136 §12.3 — the deepest possible failure of the framework: that its own geometrogenesis is in tension with its own arrow.
**Banks:** the P1d of RAW 135 §9 and RAW 136 §9, sharpened by the three-mechanism decomposition (Tom, 2026-07-12).

## 1. Stakes and the sharpened question

RAW 136 reframed mode-selection as a self-organized critical *attractor* reachable by directed time + drive + dissipation. Its live residual (§12.3): a self-organized critical state might be reachable only via *annealing-in-disguise* — the substrate secretly relaxing/revisiting its frozen past — which the immutable-past axiom (RAW 134 §14) forbids. If geometry needs annealing, the framework's forward-time ontology cannot produce the geometry it claims space is.

Tom's refinement makes the test able to **acquit** the axiom, not merely fail to convict it. Reorganization has **three distinct mechanisms**, only one of which is annealing:

1. **Mutation** — edit a frozen commit in place. This *is* annealing; the axiom forbids it.
2. **Re-branching** — a new element forms a *read-only tap* to an old frozen commit; the commit is unchanged, a new branch depends on it. Forward-only, immutability fully intact. This is the framework's own **re-meeting / memoization** primitive (RAW 134 §1) and the standard persistent/functional-data-structure model (Okasaki; git commit-with-parent; copy-on-write).
3. **Pure forward** — an element only ever taps its birth-frontier, never reaches back (Exp 138 P1 — froze/exploded).

The experiment decomposes which mechanism the geometric phase actually requires, and at what *reach*. This wires directly into RAW 134 §12.1: re-branching **is** memoization, and its reach is exactly the "locality window" §12.1 said must be smuggled — so the same run also tests whether the RAW 135 flux *sets* that window dynamically (self-organized, not smuggled).

## 2. Two separated knobs

- **W_mut** — the mutation window: elements of age ≤ W_mut may have their committed γ-values edited; older are frozen. `W_mut = 0` = hard immutability (nothing ever edited); `W_mut → ∞` = full annealing (the P0/Metropolis reference regime).
- **R_branch** — the re-branch reach: how far back (in graph distance / causal depth) a newly-born element may form a read-only tap to an already-frozen element. `R_branch = 0` = pure forward (Exp 138 P1); larger = memoization reaching deeper into the past.

The two are orthogonal: W_mut governs *editing* the past, R_branch governs *referencing* it. Only W_mut > 0 violates the axiom.

## 3. The dissipation engine (RAW 135, the missing ingredient)

The substrate is the Exp 138 directed-growth DAG (drive + causality: frontier accretion, immutable past) **plus the RAW 135 exhaust loop**, which Exp 138 P1 lacked:

- Each active element sheds *depleted deposits* (spent, cannot rejoin its loop) at rate set by its own re-render; the exhaust streams outward over the frontier and **dilutes as 1/N(r)** (N(r) = distinct branches at causal depth r — the area-law exponent).
- Arriving exhaust does two opposite things (the §4/§5 engine of RAW 135): it **pushes** the receiver (momentum, repulsive) *and* is **consumed**, feeding a re-branch toward the source (attraction, up-flux). Consumption below capacity dominates (attraction ∝ 1/N(r)); the un-consumable excess pushes (radiation pressure). The **Eddington balance** between them is the self-regulator (SOC drive-vs-dissipation).
- **A re-branch is exactly how consumption acts**: consuming an arriving deposit forms a read-only tap to its (frozen, older) source — so R_branch is not an arbitrary knob, it is the *reach of the flux*. Near sources deliver strong flux → re-branch; distant sources dilute out → no re-branch. The bet of RAW 135/136 is that this *self-organizes* a bounded R_branch (local cycles reinforced, long chords starved) with no imposed window.

## 4. Design decisions (with Tom, 2026-07-12)

- **Three-mechanism decomposition** (chosen over the two-way mutation test): separate W_mut and R_branch so the axiom can be acquitted (re-branching suffices) or convicted (mutation needed), not just tested binary.
- **Primary arm holds the axiom rigid** (W_mut = 0) and sweeps R_branch × N; the verdict is the *scaling* of the geometric threshold. The comparison arm (W_mut > 0) asks whether mutation buys anything re-branching cannot.

## 5. Phases

### Phase I0 — a dimension instrument that survives a random-graph null (hard prerequisite)

Exp 138 P1c proved the spectral-dimension reader reads d_s ≈ 2.0 on a *random 4-regular graph* — the "2D band" admits expanders, so no geometric claim was certifiable. **P1d cannot proceed without fixing this.** Build a dimension instrument (spectral d_s and/or shell-growth, possibly combined) calibrated against signed controls that **include a random-graph null**: torus2d, torus3d (manifold, must read finite-d in-band), balanced tree (exp), 4- and 6-regular random graphs (**must NOT read as manifold** — the control P1c lacked). Gate G-I0': separate manifold from *all* of {tree, expander, random-regular} with signed margins, both PASS and FAIL demonstrably attainable (reachable-range rule on the decision rule itself). No P1d gate is believable until G-I0' passes.

### Phase A — the primary tension test (W_mut = 0, sweep R_branch × N)

Run the dissipation engine with **hard immutability** (nothing ever edited). Sweep R_branch ∈ {small … large} × system size N ∈ {several sizes}, ≥10 seeds each. Measure, per cell: whether the substrate reaches the geometric phase (scale-free **and** finite-d in the validated band — RAW 136 §9 outcome (a)), the geometric threshold R_branch\*(N), and its **scaling with N**. Also report whether R_branch self-organizes (is the *effective* reach flux-set and bounded even when the *cap* is large?) — the §12.1 self-organized-vs-smuggled test.

### Phase B — the comparison arm (does mutation buy anything?)

Allow W_mut > 0 (soft annealing within a window). Ask whether any geometry appears that Phase A's W_mut = 0 could not reach — i.e., does editing the past buy geometry that re-branching alone cannot. This is the direct annealing-in-disguise conviction test.

## 6. Pre-registered outcomes (frozen before Phase A runs; bands from I0')

- **ACQUITTAL (best case):** geometry at **bounded R_branch, W_mut = 0** — forward re-branching with bounded reach produces the manifold, no mutation ever needed. If the effective R_branch is flux-set and bounded even at large cap, §12.1's smuggle is also escaped (self-organized locality). The immutable-past axiom is not merely safe — it is shown unnecessary to relax.
- **MIDDLE:** geometry only at **R_branch → O(N^α), α>0, W_mut = 0** — no mutation, but the present must re-reference an unbounded span of the past. Immutability survives; bounded-locality does not. A weaker tension, honestly reported.
- **CONVICTION (the §12.3 failure):** geometry only with **W_mut > 0** (Phase B beats Phase A at every R_branch) — annealing-in-disguise confirmed; the framework's geometrogenesis genuinely requires relaxing its own frozen past.
- **ENGINE-WRONG:** no geometry at any (R_branch, W_mut) including the annealing corner — the RAW 135 dissipation engine does not produce locality (§7 gap real; RAW 135 §12.1 kill switch fires).

## 7. Traps pre-named (this session's lessons, all mandatory)

- **Instrument null (P1c):** no d_s/shell gate calibrated only on clean lattices; the random-regular controls are gating. G-I0' is a hard prerequisite.
- **Reachable-range rule (Exp 137/138):** compute each decision rule's attainable range over the fixture/parameter class before freezing; both PASS and FAIL must be demonstrably reachable.
- **Engagement/dissipation census (P1b):** confirm the exhaust channel actually fires (shed rate, consumption rate, re-branch rate all nonzero and non-degenerate) before interpreting any outcome — a "no geometry" verdict is meaningless if the dissipation never engaged, exactly as P1b's selector never engaged (0.022%).
- **Comoving, not frozen (Addendum F §18.2):** the geometric target is scale-free *growth* (polynomial-in-time, stationary shape), not absolute stationarity (a freeze). The instrument and gate read growth-shape + finite-d, not static size.
- **Tie-breaking (K=12 census):** every stochastic choice seeded, id-sorted; no dict/set iteration-order dependence.
- **Two skeptic passes** minimum: after Phase I0' (is the instrument really null-safe?) and after Phase A (is the acquittal/middle verdict robust, or an artifact?), before any RESULTS. Anti-rescue: no post-hoc regimes without fresh pre-registration.

## 8. Prior art / grounding

- **Persistent (functional) data structures** (Okasaki); **git** (immutable commit + parent pointer); **copy-on-write** — the exact "re-branch without mutation" model; establishes that immutable structural sharing is a well-defined, powerful reorganization mode distinct from in-place mutation.
- **Self-organized criticality** (Bak–Tang–Wiesenfeld) — the drive-vs-dissipation self-tuning to a scale-free critical state without a tuned control parameter (RAW 136 §2).
- **CDT** (Ambjørn–Jurkiewicz–Loll) — directed time selects the finite-d phase (RAW 136 §4); the analogy-with-a-hole this experiment tries to close (CDT sums over manifold simplices; a from-scratch DAG must produce locality).
- **RAW 134 §1/§12.1** (re-meeting = memoization; the memoization knife-edge), **RAW 135** (the dissipation engine), **RAW 136** (the SOC/CDT selection principle), **Exp 138 P0/P1/P1c** (annealing reaches geometry; forward-without-dissipation freezes; the instrument-invalidity finding).

## 9. Cost & tooling

Python, background `python -u`. Reuses Exp 138's `p1_growth.py` (extend with the exhaust loop + W_mut/R_branch knobs) and the Exp 137 graph generators. Phase I0' is cheap (instrument calibration on fixed graphs). Phase A is the heavy part (dissipation dynamics × R_branch × N × seeds) — estimate hours; parallelize across cells. Directory: `experiments/138_geometrogenesis/`, PREREG_I0prime / PREREG_P1d frozen in order.

## 10. Scope honesty

This tests ONE engine (RAW 135 exhaust) under ONE growth discipline (frontier accretion, immutable past) with ONE selection principle (SOC + directed time), and decomposes the reorganization it needs into mutation vs re-branching. It does **not** prove the framework produces geometry in general; a positive (ACQUITTAL) would be the framework's first from-scratch geometric phase under its own arrow — the start of a research line, not its end (stability under perturbation, the gravity tail per RAW 135, and whether the phase is 3D specifically per Tegmark/§7 would each need their own pre-registered follow-ups). A CONVICTION or ENGINE-WRONG is a clean, publishable negative that locates the wall precisely. Every outcome is decisive; that is the point.
