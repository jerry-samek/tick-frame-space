# ⚖️ Fallible Commit Principle

## Definition

Every commit (decision boundary) is an **irreversible choice** that closes the observer’s buffer.  
Since the commit occurs only after visualization, it is always at least one buffer behind the substrate.  
This means that the decision can be **fallible**: it may close a horizon that does not correspond to the optimal image
of reality.

## Mechanism

- **Buffer closure**: the commit fixes a tick sequence that already belongs to the past.
- **New buffer**: a new window immediately opens to collect further ticks.
- **Visualization**: runs on the closed buffer and may reveal that the decision was “wrong.”

## Consequences

- **Irreversibility**: a fallible commit cannot be corrected, because the buffer is closed.
- **Lag of reality**: the observer always reconstructs the past, never the live tick stream.
- **Cardinality 1**: if there is only one main observer, no branching of reality occurs.
    - Visualization instances are merely different interpretations of a single buffer.
    - Divergence is unified in the decision of the main observer.
- **Cardinality >1**: only with multiple independent observers do separate branches of reality emerge (
  *Observer-Separated Multiverse Principle*).

## Philosophical Layer

The Fallible Commit Principle shows that **reality is inherently risky**: every decision may lead to deviation.  
With cardinality 1, this deviation manifests only as differences in interpretation, not as branching worlds.  
Plurality of worlds arises only with plurality of observers — each commit then defines its own horizon of reality.
