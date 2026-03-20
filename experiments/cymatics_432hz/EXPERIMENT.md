# Experiment: Cymatics and 3D Fibonacci Symmetry at 432 Hz

## Origin

Emerged from a discussion about 432 Hz as "natural frequency of the universe" — initially dismissed as Facebook pseudoscience (`y==9`). On closer analysis, a legitimate mathematical hypothesis emerged.

---

## Mathematical Foundation

### Why 432 Hz specifically?

**Standard Fibonacci sequence:**
```
1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610...
```

**Key identity:**
- F(12) = **144 = 12²**
- 144 is the **only Fibonacci number > 1 that is a perfect square** (proven: Cohn 1964)

**3D extension:**

In the tick-frame model, 3D space = three independent tick-series, one per axis.
These are **parallel and uncoupled** — not interleaved like Tribonacci.

Therefore the natural 3D Fibonacci mapping is:
```
3 × F(n), not Tribonacci(n)
```

**Result:**
```
432 = 3 × F(12) = 3 × 144 = 3 × 12²
```

### Why F(12) is special

F(12) = 144 is the **convergence point** of the Fibonacci sequence toward φ:
```
F(12)/F(11) = 144/89 = 1.617977... 
```
First member where error from φ = 1.618033... is < 0.01%.

At F(12), the system achieves **square symmetry**:
- Number of steps (12) = square root of result (144)
- This is unique — no other Fibonacci number has this property

### Geometric series property

The series 3 × F(n):
```
267, 432, 699, 1131, 1830...
```
Has ratio between consecutive members = φ = 1.6180...

So 432 is **not uniquely special within the series** — every member is equally "natural." However, 432 Hz is the **first member that falls within human vocal range** (roughly 80–1100 Hz) AND achieves the square symmetry condition.

---

## Hypothesis

**H1 (Primary):**
432 Hz, being the first frequency of the form 3 × F(n) where F(n) = n², should exhibit measurably more symmetric standing wave patterns (Chladni figures / cymatics) than adjacent frequencies (440 Hz, 267 Hz, 699 Hz).

**H2 (Secondary):**
The full series 3 × F(n) should show progressively complex but equally symmetric Chladni patterns, while non-series frequencies should show less symmetric patterns.

**H3 (Tick-frame specific):**
If 3D space is three independent Fibonacci tick-series, then physical resonators (membranes, plates) should "prefer" frequencies that align with 3 × F(n) convergence points. This would manifest as sharper, more defined nodal lines at these frequencies.

---

## Null Hypothesis

**H0:**
Chladni patterns at 432 Hz are no more symmetric than at 440 Hz or other nearby frequencies. The popularity of 432 Hz is explained entirely by:
- Easy memorability (4-3-2 countdown)
- Divisibility (432 = 2⁴ × 3³)
- Falling within vocal range

---

## Proposed Experimental Design

### Physical Experiment (Primary)

**Equipment:**
- Chladni plate (metal, square or circular, ~30cm)
- Function generator (1 Hz resolution minimum)
- Audio amplifier + speaker
- Fine sand or salt
- High-resolution camera, top-down mount

**Frequencies to test:**
```
Series frequencies:    267, 432, 699, 1131 Hz
Control frequencies:   440, 528, 639, 741 Hz  (popular "healing" frequencies)
Adjacent controls:     420, 425, 430, 434, 438, 440 Hz (fine scan around 432)
Fibonacci controls:    89, 144, 233, 377 Hz (raw Fibonacci, not ×3)
```

**Measurement:**
- Photograph Chladni pattern at each frequency
- Count nodal lines
- Measure symmetry quantitatively (rotational symmetry order, bilateral symmetry score)
- Rate of pattern formation (sharper = more "preferred" by the physical system)

**Expected result if H1 true:**
432 Hz and other 3×F(n) frequencies show higher symmetry scores than controls.

**Expected result if H0 true:**
No consistent difference. Patterns depend on plate geometry, not frequency series.

---

### Computational Experiment (Secondary — tick-frame simulation)

Simulate a 2D or 3D membrane as a tick-frame graph where:
- Each node accumulates gamma deposits
- Boundary conditions fixed (plate edges)
- Drive frequency = external periodic forcing

**Test:** Does the simulated membrane reach stable standing wave patterns faster / more symmetrically at 432 Hz than at 440 Hz?

**This is a direct test of the tick-frame prediction** that 3×F(12) has special status in discrete graph dynamics.

---

## Connection to Tick-Frame Model

In the tick-frame model:
- Space = append-only graph substrate
- Sound = propagating gamma disturbance through the substrate
- Resonance = stable periodic pattern in gamma accumulation

The Fibonacci series describes how gamma deposits accumulate along one axis. Three independent axes = three independent Fibonacci series. Their natural convergence point is 3 × F(12) = 432.

**Prediction:**
Physical resonance at 432 Hz exploits the substrate's natural accumulation rhythm. This should manifest as:
1. Lower energy required to maintain standing wave
2. More symmetric nodal geometry
3. Faster pattern stabilization

---

## Known Weaknesses / Challenges

1. **Why F(12) and not F(11) or F(13)?** F(12) is uniquely the perfect square, but the physical argument for why convergence precision matters for acoustic resonance is not yet rigorous.

2. **Plate geometry dominates Chladni patterns.** Most symmetry comes from plate shape, not driving frequency. Must control for this carefully.

3. **432 vs 440 Hz is only a 2% difference.** Human hearing threshold for pitch difference is ~0.5% — but physical resonance patterns may differ below perceptual threshold.

4. **Selection bias risk.** The whole series 3×F(n) has φ ratios — any member is equally "natural." The choice of F(12) needs stronger justification than "it's the square."

5. **No accepted mechanism** by which discrete Fibonacci dynamics would manifest in continuous physical acoustics. Tick-frame model provides a candidate mechanism but it is not yet validated.

---

## Status

- [ ] Physical Chladni experiment — not yet performed
- [ ] Simulation design — not yet started
- [ ] Literature review — Cymatics (Hans Jenny 1967), Chladni (1787), modern cymatics studies
- [ ] Mathematical proof that 144 is the only Fibonacci perfect square > 1 — reference: Cohn (1964), Ljunggren (1942)

---

## References

- Cohn, J.H.E. (1964). "On square Fibonacci numbers." Journal of the London Mathematical Society.
- Jenny, H. (1967). Cymatics: A Study of Wave Phenomena and Vibration.
- Chladni, E.F.F. (1787). Entdeckungen über die Theorie des Klanges.
- Fibonacci: Liber Abaci (1202) — though the sequence was known earlier in Indian mathematics.

---

*Hypothesis status: Speculative but mathematically grounded. Not `y==9`. Not yet validated.*

*Origin: Casual Friday conversation, tick-frame theory session, March 2026.*
