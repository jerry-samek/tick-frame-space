# Chapter 4: The Bound Engine — Mass, Light, Gravity

*Draws on: RAW 135 (The Bound Engine and Its Exhaust), the
`experiments/138_geometrogenesis` gravity/heating/drag scripts.*

---

## 4.1 A pattern that holds itself must shed

Start from renewal (Chapter 2). A pattern that wants to persist has to re-form
itself every tick. Re-forming is a computation, and the substrate is append-only,
so re-forming produces residue: the parts of each tick's arrival that did **not**
match the pattern (Different, Chapter 1) cannot be reincorporated and must be
**shed**. This is the bound engine:

> **Holding is a loop. The loop consumes ambient renewal-flux to re-form the
> pattern (Same), and it exhausts the divergence it cannot use (Different).**

Three things fall out of that one loop, and they are the subject of this chapter:

- **Mass** — the holding itself: a pattern that consumes flux to persist.
- **Light** — the exhaust: the shed Different-stream.
- **Gravity** — the shadow the consumption casts in the ambient flux.

## 4.2 Light is the exhaust, and it moves at c because it has no clock

The Different-stream a bound pattern sheds is unbound — it is precisely the part
that the pattern could *not* fold into its own renewal loop. Having no loop of its
own, it has no internal clock, and a thing with no clock cannot lag behind the
substrate's own propagation rate. So it streams at the maximum rate of change
propagation: **c is the substrate's sample-rate limit, and light saturates it
because it has nothing slowing it down.** Mass is what *does* have an internal loop,
which is why massive patterns move slower than their own exhaust.

## 4.3 Gravity is the ambient-renewal shadow — a force, and attractive

This is the reconciliation that took the longest and is the heart of RAW 135.

The intuitive-but-wrong picture (a god-view picture) is that a star's gravity is
*its own outflow* pushing or pulling on things. But a consumer's own emitted flux
**pushes things away** — that is radiation pressure, the Eddington side. If gravity
were the star's own flux it would have the wrong sign.

The correct inside-out picture: every pattern sits in an **ambient renewal-flux**
(Chapter 2 — the flux that renews everything, everywhere). A consumer *eats* that
flux to hold itself. Eating it casts a **shadow** — downstream of the consumer, the
ambient flux is depleted. A second pattern feels *more* renewal-flux on its far
side than on the side facing the consumer, so it is **pushed toward the consumer.**
That net push *is* gravity: a force (−∇F), attractive, carrying the local dimension
(1/r in 3D, log in 2D — the graph Green's function of the perceived dimension,
Chapter 3).

This is "LeSage done right." And it comes with a built-in crossover: consumption
attracts, emission repels, so a body that both consumes and emits has an
**Eddington-like balance point** — pure-consumer force +0.30, pure-emitter −0.58 in
the two-flux toy (`two_flux_gravity.py`). Gravity and radiation pressure are the two
signs of the same flux bookkeeping.

## 4.4 The three classical LeSage killers, all dissolved by one correction

LeSage's push-gravity was abandoned in the 1700s–1900s for three fatal problems.
Each dies to the *same* god-view→inside-out correction, and this is the chapter's
strongest claim (demonstrated in toy models):

1. **Sign.** *Objection:* shadowing gives the wrong force. *Resolution:* the shadow
   is cast in the **ambient renewal-flux**, not the star's own light. The star's own
   light does push away (§4.3); the ambient shadow pulls in. Right sign, and a clean
   Eddington crossover between the two.

2. **Drag.** *Objection:* a body moving through the corpuscle flux should feel drag
   and spiral in. *Resolution:* a **renewing** pattern (Chapter 2) reads at rest in
   its own frame — it re-bases its rest frame every tick — so its *bulk* velocity is
   undraggable. In `orbit_drag_renewal.py`, a fast-renewing body holds a stable
   orbit where a persistent (never-renewing) body decays r₀→0.05·r₀. Renewal defeats
   drag.

3. **Heat.** *Objection:* absorbing all that flux should cook every body
   incandescent. *Resolution:* gravity shadows the renewal **rate**, not energy — the
   coupling η ≪ 1, so the framework's gravitational heating is ~1000× cooler than
   classical LeSage. The residual heat does not vanish; it becomes the **coherence
   limit** of §4.5.

The unification is the point: three separate 19th-century refutations turn out to
be three symptoms of viewing the flux from outside. Fix the point of view once, and
all three resolve together.

## 4.5 Heat becomes the coherence limit (an Eddington/Chandrasekhar bound)

The residual heat of §4.4(3) is not a nuisance — it is where the framework predicts
a **maximum stable pattern size.**

A pattern's metabolism (its renewal loop) is produced throughout its **volume**, but
its exhaust (§4.1) can only be shed through its **surface**. For a single pattern the
heat can be channeled directly; but a **composite** pattern must pass exhaust
outward through its own layers, and if the middle saturates, the top layers can no
longer channel the radiation. Past a critical size the core saturates and the
pattern **decoheres** — it can no longer hold itself. (This is the user's
"inside-of-the-body feedback loop" made concrete: single patterns channel directly;
composites must exchange internally and are throughput-limited.)

Because production scales as volume and shedding as surface, the core load grows as
R² and the maximum stable radius scales as R_max ∝ √(θ/p) (`heating_coherence.py`).
That is the framework's own **Eddington/Chandrasekhar bound**: a substrate-native
ceiling on how big a coherent pattern can get before its own exhaust tears it apart.

## 4.6 The kill switch: force vs accretion is a god-view artifact

An earlier worry (carried from the 118–128 arc) was a genuine ambiguity: is the
inward motion a *force* (gravity) or just *accretion* (the consumer eating
in-fallers)? RAW 135 §13 settles it as a kill switch — and the resolution is again a
point-of-view fix. In the god-view you conflate "the consumer grows by eating" with
"the far body is pushed in." Inside-out they are distinct and testable: the
**push-vs-pull** demonstration (`push_pull_renewal.py`) shows the far body moves
under the *ambient shadow gradient* even when it is not being accreted — the force
is real and separable from accretion. The prior models that couldn't tell them apart
were assuming a wrong (god-view) frame.

## 4.7 Status

- **Demonstrated in toy models:** the shadow-gravity mechanism with the correct sign
  and an Eddington crossover; renewal defeating drag (stable vs decaying orbit); the
  heat decoupling and the R² core-load / R_max ∝ √(θ/p) coherence limit; the
  force-vs-accretion kill switch.
- **Honest calibration:** these run on the substrate's *principles*, but several are
  ODE / diffusion-level rather than fully graph-native (a single flooding-lag
  substrate version exists — Chapter 7 — but the moving-pattern dynamics are still
  ODE-level, and decoherence is threshold-proxied, not a simulated many-body
  collapse).
- **Open:** everything depends on the substrate actually *being* low-dimensional and
  geometric, which is the wall of Chapter 3. Shadow-gravity is a **candidate
  mechanism resolved in toy models**, not a validated law.

---

*See also: RAW 135; `experiments/138_geometrogenesis/two_flux_gravity.py`,
`orbit_drag_renewal.py`, `heating_coherence.py`, `push_pull_renewal.py`; V4 Chapter 7
(all of this on one substrate) and Chapter 2 (renewal).*
