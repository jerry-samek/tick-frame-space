# Tick‑Frame Experiment Architecture
### *Common substrate engine with modular observers*

This document defines the architecture for running all tick‑frame experiments using:

- one shared substrate engine
- many independent observers
- experiment configurations that select which observers run

The substrate never knows about physics.  
Observers never modify the substrate.  
Experiments are just configurations.

---

# 1. Core Concepts

## 1.1 Substrate State
Minimal representation of the universe at tick \(t\):

- **entities:** map of entity IDs to attributes
- **adjacency:** graph structure (adjacency list or edge set)
- **tick:** integer counter

No geometry, no forces, no fields.

## 1.2 Update Rule \(U\)
Local, memoryless rule:

\[
A(t+1) = U(A(t))
\]

- depends only on local adjacency
- synchronous
- stateless
- geometry‑free

## 1.3 Substrate Engine
Runs ticks and notifies observers.

Responsibilities:

- hold current `SubstrateState`
- apply update rule each tick
- notify observers before and after each tick

---

# 2. Engine Interface

## 2.1 SubstrateEngine

- `state`: current `SubstrateState`
- `update_rule`: implementation of \(U\)
- `observers`: list of attached observers

### Methods

- `add_observer(observer)`
- `run(max_ticks)`
- `_notify_pre_tick()`
- `_notify_post_tick()`

---

# 3. Update Rule Interface

## 3.1 UpdateRule

Defines the substrate transition:

- `step(state: SubstrateState) -> SubstrateState`

This is the only place where adjacency changes.

---

# 4. Observer Interface

Observers attach to the engine and compute derived quantities.

## 4.1 Observer

### Methods

- `on_pre_tick(state)` — optional
- `on_post_tick(state)` — main hook

Observers:

- never modify the substrate
- may keep internal memory
- may log or compute metrics

---

# 5. Experiment Configuration

Experiments are configurations, not separate engines.

## 5.1 ExperimentConfig

Fields:

- `name`
- `initial_state_builder`
- `update_rule`
- `observers`
- `max_ticks`

## 5.2 Running an Experiment

1. Build initial state
2. Create engine
3. Attach observers
4. Run for `max_ticks`

---

# 6. Observer Modules

Each experiment corresponds to one or more observers:

- **GenesisObserver** — adjacency frontier, density, horizon
- **RelativityObserver** — worldlines, causal classification
- **PiDriftObserver** — adjacency shells, π(t, R)
- **ConstantsDriftObserver** — α(t), G(t), h(t), Λ(t)
- **EntropyObserver** — reachable states, S(t)
- **ParticleObserver** — adjacency loops, identity stability
- **ForceCollapseObserver** — adjacency bias signatures

Observers are independent and can be combined arbitrarily.

---

# 7. Logging

Logging is handled by observers:

- each observer decides what to log
- logging cadence is observer‑specific
- outputs may be CSV, JSON, or in‑memory buffers

Engine does not log anything.

---

# 8. Summary

- **One substrate engine**
- **One update rule**
- **Many observers**
- **Experiments = configurations**

This architecture supports all tick‑frame experiments in a unified, modular way.
