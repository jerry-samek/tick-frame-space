# Persistence / Survival Axioms

## Principle: Persistence

Entities must accumulate sufficient energy across multiple ticks to maintain existence.  
Persistence is defined as the ability to renew across tick‑samples without exhausting the energy budget.

- **Requirement:** Energy must not be consumed entirely in a single tick.
- **Condition:** Accumulation must exceed the survival threshold before observation.
- **Invariant:** Entities that fail to accumulate collapse into history.

## Principle: Survival

Survival is tested at the moment of observation (sample tick).  
An entity must have enough reserve energy to pass the survival threshold.

- **Requirement:** Reserve energy ≥ survival threshold at sample tick.
- **Condition:** Entities with insufficient reserve collapse immediately.
- **Invariant:** Survival is binary — either commit to sample log or collapse.

---

### Extension: Binding Energy Exhaustion

**Principle:**  
Artificial or forced binding of entities requires such a high energy threshold that, once overcome, there is
insufficient reserve energy left for long‑term survival. These entities therefore collapse quickly at the first sample
tick.

**Relation to Persistence / Survival axioms:**

- **Persistence** demands energy accumulation across multiple ticks.
- **Survival** requires a sufficient reserve at the moment of observation.
- **Binding Energy Exhaustion** is a special case where the binding threshold consumes the reserve, causing the entity
  to fail both persistence and survival tests.

**Consequence:**  
Short‑lived particles (e.g., artificially created ones) disappear rapidly because their energy investment in binding
leaves them unable to sustain existence within the tick‑frame universe.
