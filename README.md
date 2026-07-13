# Tick-Frame Space
*Coherence over Orthodoxy: a model is valid if it is internally consistent, falsifiable, and explanatory, regardless of its alignment with current physical dogma.*

A speculative discrete-physics model exploring whether a single operation on a raw graph — **read from the inside, never from a god's-eye view** — can produce everything we observe. My pet project on "garden leave." Don't take it too seriously, but feel free to correct me if I'm wrong (I definitely am). I'm an engineer, not a scientist. I just have plenty of spare memory-time to think about crazy stuff.

## What This Is

One mechanism, iterated on a graph at every tick:

> **An entity deposits on a connector, hops, and the connector extends.**

Everything is deterministic at the substrate layer — no randomness, no infinity, no continuum. But the load-bearing idea isn't the mechanism; it's the **point of view**.

### The reconciliation: there is no god-view

The project started (V1–V3) describing the world from the outside — a graph you look *at*, with a geometry you measure. That framing kept hitting walls, and it took a long time to see why: **the outside view doesn't exist in this ontology.** There is no observer who sees the whole graph. There are only patterns inside it, each reading what has *arrived* — and every hard problem, once re-derived from the inside, dissolved. The current frontier is that reconciliation.

Read inside-out:

- **Time** is the order you read your own causal depth. The future is unseeable because it isn't computed yet.
- **Space** is *rendered delay*: a pattern reads the lag (arrival delay) of deposits reaching it. "Empty space" is the time-delay between deposits, nothing more.
- **Dimension** is what an embedded observer's channels resolve — the correlation-rank of its incoming lags. A lattice *looks* low-dimensional from inside; an expander looks high-dimensional. Not a property of the graph — a property of the reading.
- **Gravity** is the *shadow* a consumer casts in the ambient renewal-flux — a force (you're pushed into the well), attractive, and it carries the local dimension (1/r in 3D, log in 2D).
- **Light** is the spent exhaust a self-holding pattern must shed; it streams at *c* because, unbound, it has no clock of its own.
- **Observer = renderer = being.** Any pattern that re-renders itself *is* a full participant: it exists (re-renders), it observes (consuming the lag-flux is perceiving), and it renders itself into everyone else's world (its shadow and shedding are what others read). There's no special observer; the world is the mutual rendering of all of them.

### The Three States (the mechanism underneath)

Every interaction still reduces to one of three comparison outcomes — the alphabet the deposit/hop/extend operation speaks:

| State | Physics | Information |
|-------|---------|-------------|
| **Same** | Gravity — reincorporate | Retrieval — no new structure |
| **Different** | Radiation — shed divergence | Information — branch point |
| **Unknown** | Expansion — write the frontier | Learning — new structure |

No fourth state exists.

## One substrate, one act

The synthesis is a single engine — a pipe network with an ambient renewal-flux flooding through it (no coordinate grid). From **one consuming pattern** on it, the same act produces:

- **gravity** — its consumption carves an attractive well (the graph Green's function of the local dimension);
- **perception** — its taps read the lag-structure of the flux they consume, yielding a perceived dimension;
- **a coherence limit** — its own metabolism is produced over its volume but shed through its surface, so past a critical size the core saturates and it decoheres → a *maximum stable pattern* (the framework's Eddington/Chandrasekhar bound).

Perceiving = gravitating = being, on one substrate. See `experiments/138_geometrogenesis/flooding_lag_substrate.py`.

## Honest status — the negatives are the point

This is a speculative model with **no real-world experimental validation**. What makes it worth taking seriously (if anything does) is that it is developed against an adversarial skeptic discipline: every "result" is attacked by a fresh reviewer before it's believed, and the recurring lesson — recorded and reused — is that **when something is stuck, a god-view assumption has been smuggled in.**

### What has been demonstrated (in-model, mostly toy scale)
- **A candidate gravity mechanism that clears all three classical LeSage problems**, each by the same god-view→inside-out correction: the **sign** (gravity is the ambient shadow, not consumption of a star's light), **drag** (a renewing pattern reads at rest in its own frame, so its bulk velocity is undraggable — orbits stay stable where a persistent body decays), and **heating** (gravity shadows the renewal *rate*, not energy, so it's ~1000× cooler than classical; residual heat becomes the coherence/Eddington limit above).
- **Dimension is measurable inside-out.** A boundary-layer, lag-correlation reader cleanly separates the exact adversarial zoo (hypercubes, honeycomb, expanders, small-world) that defeated every god-view detector — because from inside, an expander genuinely *looks* high-dimensional. This is the framework's own dimension definition (correlation-rank, à la Cao–Carroll–Michalakis) grounded in propagation delay.
- **The relational point of view**, concretely: with no god-view, "planet orbits star" is not privileged — the planet's frame sees the star orbit *it*; all frames agree on the invariant lags, none on who moves.

### What has NOT been demonstrated (the open wall)
- **The substrate-side wall — the big one.** Does a growing, directed-time substrate actually *select* a low-dimensional (geometric) phase, or an expander/tree? A first-cut recon says the growth engine's selection produces **no** geometry (its output reads the same with and without selection). This is the geometrogenesis problem, shared with all of discrete quantum gravity, and it is **unsolved here** (see `RESULTS_p1d_recon.md`). The mechanism these results point to — a dissipation/exhaust channel driving self-organized criticality — is designed but not built.
- The toy demonstrations (orbits, wells, coherence) run on the substrate's *principles* but not all fully graph-native (some are ODE/diffusion-level).
- No connection to real-world experimental physics. The one banked testable difference from standard QM remains the interferometry prediction (Exp 62 — which-path detection without destroying interference).

## Theory documentation

The theory has prior versions (V1 raw docs → V2 geometric → V3 graph-first, all archived). **V4 is the current consolidation — the inside-out synthesis of the RAW 134–137 arc**, which reframes the whole 118–138 gravity/geometrogenesis line. V4 is a live frontier, not a finished theory: the geometrogenesis wall (does the substrate select geometry?) is open, and V4 says so throughout.

| Document | Title |
|----------|-------|
| RAW 134 | The Inside-Out Substrate — tick ≠ time; observer as merge; objectivity = invariance, not god-view |
| RAW 135 | The Bound Engine and Its Exhaust — mass, light, gravity from one loop; all three LeSage killers resolved |
| RAW 136 | The Manifold Is an Attractor — geometry as a self-organized critical phase (the open substrate-side wall) |
| RAW 137 | The Measurement Is Inside-Out — dimension from lag; the observer-side wall is a god-view artifact |

- **V4 chapters** (inside-out consolidation, current): `docs/theory/V4_README.md` and `V4_ch01`–`ch08` + `V4_glossary.md`. The prior graph-first consolidation is in `docs/theory/v3_archive/`.
- **Raw documents:** 130+ in `docs/theory/raw/`. The **5xx series is explicitly highly speculative**; the main sequence (001–499) holds theory, results, and testable predictions.
- **Reading paths:** skeptics → `V4_ch08` (honest status), then RAW 137 §6/§9. Physicists → `V4_ch01` → `ch04` → `ch03`, then RAW 134 → 135 → 137. CS → `V4_ch01` (tick = recursive call) → `V4_ch06` (trie) → `V4_ch03`.

## Quick start (current frontier: Python)

The active work is the `138_geometrogenesis` line (the flooding-lag substrate and the inside-out instruments):

```bash
cd experiments/138_geometrogenesis
python flooding_lag_substrate.py    # one engine: gravity + perception + coherence
python boundary_layer_dim.py        # the inside-out dimension instrument vs the adversarial zoo
python two_flux_gravity.py          # gravity as the ambient-shadow force (the Eddington crossover)
python orbit_drag_renewal.py        # renewal defeats LeSage drag
python orbiting_patterns.py         # relational PoV: no god-view, only lags
```

The **tick-space-runner** Java module is a legacy substrate simulation (Chapter-15 / geometric-lattice era) and predates the graph-first and inside-out paradigms; kept for reference.

## Project structure

```
tick-frame-space/
  experiments/
    138_geometrogenesis/   Current frontier: flooding-lag substrate, inside-out instruments
    137_participation_ratio/  Observer-rank / graph tooling
    118_.. 136_..          The gravity/geometrogenesis arc
    64_109_three_body_tree/   Earlier graph-orbital experiments
  docs/theory/
    raw/                   130+ raw documents (RAW 134-137 = current frontier)
    V4_*.md                V4 inside-out consolidation (current)
    v3_archive/ v2_archive/ archive/ review/   Superseded / transitional
  tick-space-runner/       Legacy Java substrate simulation
  scripts/                 Python analysis tools for JSON snapshots
```

## AI-assisted development

AI is a tool for materialization, not invention. The theory and every reframe originate from human thought during garden leave; AI helps make it concrete and — crucially — helps attack it. The single most productive pattern this project has found is the **fresh-context skeptic**: a reviewer with none of the operator's investment, dispatched to find the smuggled god-view, the goal-post move, the unearned claim. Most of what survives did so because it survived that.

- **Claude (Anthropic)** — articulation, experimental design, literature grounding, the adversarial skeptic passes, honest accounting.
- **GitHub Copilot** — code completion.

The human provides the vision and the reframes; AI helps test them to destruction.

**Speculation disclaimer:** a speculative computational model of discrete physics. Real computational progress, zero real-world experimental validation. Read the "Honest status" section as the truth, not the abstract.
