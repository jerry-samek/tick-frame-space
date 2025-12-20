# Energy Constant Principle (Engineering Formulation)

**Definition**  
The simulation must enforce a hard invariant:

    (sumEntityEnergy / t) - sumMomentumCosts ≈ 0

for every tick. Any deviation beyond tolerance indicates leakage or misallocation in the model.

---

## Implementation Checklist

- **Substrate ledger:**  
  Track per‑entity energy values and momentum costs.

- **Temporal normalization:**  
  At tick t, compute and assert:

      double normalizedEnergy = (sumEntityEnergy / t) - sumMomentumCosts;
      assert Math.abs(normalizedEnergy) < EPSILON;

- **Audit routine:**  
  Log normalizedEnergy each tick; ensure values stay in a small interval around zero.

- **Diagnostics:**  
  If drift occurs, record frame ID, entity count, and growth rates for debugging.

- **Renderer honesty:**  
  Visualize normalized energy, not raw exponential values, to reflect persistence accurately.

---

## Engineering Echo

This principle is the unit test of the cosmos:

- **Per‑tick check:**  
  Compute

      (sumEntityEnergy / t) - sumMomentumCosts

  and assert that the result stays within a small interval around zero.

- **Leak detection:**  
  If the invariant drifts, the substrate is leaking energy or misallocating momentum.

- **Stability criterion:**  
  If the invariant holds, the universe remains stable: exponential growth or decay is normalized by time, collisions are accounted for, and persistence is measured honestly.

In practice, this echo means your simulation is always checking that entities surf time without breaking the zero‑sum ledger. Stability isn’t about raw magnitudes, but about normalized balance across ticks.
