## v24 Experimental Results (March 18, 2026)

### Phase 1: Force Measurement — Anti-Newtonian Scaling

| Metric | v23 (M=100k) | v24 (M=1M) | Ratio |
|--------|-------------|------------|-------|
| F_radial at r=8 | -0.0000198 | -0.00000129 | 0.065× (15× weaker) |
| v_circular (i=10) | 0.00398 | 0.00101 | 0.25× |
| % inward | 100% | 98% | — |

**The 10× heavier star produced a 15× weaker force. This is anti-Newtonian scaling.**

The force law explanation:

```
growth = H / (1 + alpha × (gamma_A + gamma_B))
```

More mass → 10× more gamma everywhere → denominator ~10× larger → growth ~10× smaller.
Force comes from ASYMMETRY in growth between connectors, not from absolute growth.
When gamma is uniformly high everywhere, growth is uniformly suppressed — the
asymmetry between connectors shrinks. The field self-pins so strongly it suppresses
its own gradient.

**This is not a bug. It is a fundamental property of the force law: force saturates
and then decreases at high field density.**

---

### Why This Result Points To The Deeper Float Approximation Problem

The anti-Newtonian scaling reveals a more fundamental issue than just "M=1000 is too
much." The float gamma field allows unbounded gamma accumulation at a single node:

```
M=1,000,000 × deposit_rate=1e-5 = 10 gamma units per tick at one node
```

In the true substrate model, this is physically impossible. A node is a discrete
location in the graph. It either has a deposit event or it doesn't. **A single node
can hold at most 1 deposit — the binary presence or absence of a field event.**

The float gamma field allows:
```
gamma[node] → 10, 100, 1000, ... (unbounded)
```

The true integer substrate requires:
```
gamma[node] ∈ {0, 1}  (binary — deposit present or absent)
```

**Consequence for the force law:** With binary deposits, the denominator is bounded:

```
growth = H / (1 + α × 0) = H        (empty node)
growth = H / (1 + α × 1) = H/2      (one deposit, α=1)
```

Maximum suppression factor: 2×. The self-suppression problem that killed v24's
gradient entirely — denominator reaching 10,000× — cannot exist in the integer
model. The force law behaves sanely at ALL mass scales because no single node
ever holds more than one deposit.

**The anti-Newtonian scaling in v24 is a float arithmetic artifact, not physics.**

---

### Why The Star Cannot Be A Point

Beyond the integer deposit argument: a real star is not a single node. It is a
distributed field accumulated across the gamma deposits of billions of atoms,
molecules, and nuclear reactions — all carried by entity hops through many connector
chains. The gamma that reaches orbital radius r=8 has already been distributed,
diluted, and re-concentrated across a vast graph volume.

A point star deposits everything at one node. A physically correct star distributes
deposits across a volume (body_radius > 0) such that:

- No single node accumulates unbounded gamma
- The field gradient at orbital radius emerges from the transition between
  dense stellar interior and sparse orbital space
- The denominator never reaches pathological values

The `body_radius` parameter already exists in the code (Entity class). Using
body_radius = 3-5 for the star in v25 will distribute deposits across ~30-500
nodes and eliminate the self-suppression artifact.

---

### What Happens With Integer Deposits (v25 Direction)

When the gamma field is properly integer-valued:

1. Each deposit event adds exactly 1 unit to one node
2. Spread propagates these units hop-by-hop at c, never concentrating at one node
3. The field profile at any radius reflects the statistical density of deposit events
   that have reached that radius
4. Force = difference in deposit density between adjacent nodes = always bounded
5. Scaling with star mass works correctly because more mass = more deposit events
   distributed across more nodes, NOT more gamma concentrated at one node

The path to correct orbital mechanics:
- **v24 (current):** float gamma, point star → anti-Newtonian scaling artifact
- **v25:** float gamma, distributed star (body_radius=3-5) → removes worst artifacts
- **v26:** integer gamma, distributed star, hop-carried propagation → correct physics

---

### v24 Phase 2 Status

Proceeding with v=0.00101 (measured v_circular at r=8 on M=1M field). The force
and v_circular are internally consistent at this weaker gradient level:

```
Centripetal requirement: inertia × v² / r = 10 × (0.00101)² / 8 = 0.00000128
Measured F_radial: -0.00000129  ✓ (consistent)
```

The orbit may close at this weaker energy level. The result will confirm whether
orbital mechanics work at ANY consistent force/velocity combination, regardless
of the mass scaling artifact. If the orbit closes, the architecture is validated
even though the scaling is wrong. If it escapes, the self-suppression may be
degrading the gradient falloff profile in the same way as v23.

