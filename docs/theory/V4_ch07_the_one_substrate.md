# Chapter 7: The One Substrate

*Draws on: this session's consolidation —
`experiments/138_geometrogenesis/flooding_lag_substrate.py` — plus RAW 134–137 and
the external `causal-cone-engine` rendering prototype.*

---

## 7.1 The claim: one engine, one act

Chapters 3–5 read gravity, perception, dimension, coherence, and the observer as
separate faces of the inside-out ontology. This chapter makes the stronger,
concrete claim: **they are one engine.** A single substrate — a pipe network with an
ambient renewal-flux flooding through it, *no coordinate grid* — supports all of
them, and they come out of the **same act** of one consuming pattern.

The engine is `FloodingLagSubstrate(adj, decay, emission)`:

- ambient flux **floods** the pipes (diffuse + decay + emission);
- propagation is **multi-hop**, so **lag = path length** (Chapter 3: distance is
  delay, read from inside — no grid, no coordinates);
- a pattern is a **consumer** placed on the graph via `.add_mass()`;
- the system is advanced with `.step()` / `.relax()`.

## 7.2 What the one act produces

From that single consuming pattern, the *same* mechanism yields three things — this
is the synthesis, and it holds numerically on one object:

1. **Gravity.** `.gravity_force()` — the consumer's eating carves an attractive well
   in the ambient flux (Chapter 4's shadow; the graph Green's function of the local
   dimension). The force at r=2 is **+0.2967, identical to the standalone
   `two_flux_gravity.py`** — the unified engine reproduces the dedicated toy exactly.
2. **Perception / dimension.** `.perceived_dimension()` — the consumer's taps read
   the lag-structure of the flux they consume, yielding a perceived dimension
   (Chapter 3's boundary-layer instrument, now a method on the same object). The
   pattern *perceives by consuming.*
3. **A coherence limit.** `.core_load()` — metabolism produced over volume, shed
   through surface; past a critical size the core saturates and the pattern
   decoheres (Chapter 4's Eddington/Chandrasekhar bound, R² core load).

**Perceiving = gravitating = being, on one substrate.** The consumer does not do
three jobs; it does one — consume the ambient flux to hold itself — and gravity,
perception, and the coherence ceiling are three readings of that one consumption.

## 7.3 The field is pushed through the pipes to the observer

A note on a stubborn residue. Earlier framings kept a "field" as a background object,
which is a god-view smuggling (Chapter 1). The inside-out correction, realized in
this engine and in the external `causal-cone-engine` rendering prototype (a Rust
field-propagation renderer the user built independently), is that **the field is not
a background — it is pushed *through the pipes* to the observer, and the lag between
each entity and the observer is what creates the perception of depth.** There is no
field sitting in a space; there is flux propagating along connectors, and depth is
the accumulated lag on arrival. The renderer and the substrate are the same idea
from two directions: one propagates flux to draw a scene, the other propagates flux
to *be* one.

## 7.4 Each observer renders its own world — possibly its own universe

Because there is no god-view and no shared background (Chapter 5), each re-rendering
pattern consumes its own arriving flux and thereby **renders its own view of the
world.** Where two patterns are causally connected, their views glue (Chapter 3 §3.4,
Chapter 5 §5.4) into a shared, objective lag-structure. Where two patterns become
causally *disconnected*, they have no remaining way to affect each other — there is
"only pipeline, no geometry to interfere" — and they are, operationally, separate
universes. This is the sense in which "each observer creates its own universe view,
maybe even its own universe" is not mysticism but a direct consequence of
locality-plus-no-background: the world is exactly as large as what can reach you.

## 7.5 Status

- **Demonstrated:** one `FloodingLagSubstrate` object produces gravity, perceived
  dimension, and a coherence limit from one consuming pattern, with the gravity
  force reproducing the standalone toy exactly. This is the framework's tightest
  synthesis to date.
- **Honest calibration:** the engine runs on the substrate's principles, but it is
  still a *relaxation/diffusion* substrate — moving patterns on it are ODE-level
  (Chapter 4), decoherence is threshold-proxied, and the graph it runs on is
  supplied, not grown. Which returns us to the wall.
- **The wall, restated:** this chapter shows the one substrate can *host* all the
  physics once it is geometric. It does **not** show the substrate makes itself
  geometric — that is Chapter 3 §3.5 / Chapter 8, unsolved.

---

*See also: `experiments/138_geometrogenesis/flooding_lag_substrate.py`; RAW 134–137;
the external `causal-cone-engine` prototype; V4 Chapters 3, 4, 5, 8.*
