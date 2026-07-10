# Exp 137 — RESULTS: K=12 census + instrument verification

**Dates:** 2026-07-07 (census run) → 2026-07-10 (skeptic pass, D1–D7 verification battery, this doc).
**Scope as declared** (`k12_census.py` docstring, written before the run): census + instrument reconnaissance, NOT a registered decision test; any claim-5 test on these fixtures requires a fresh PREREG. The standing reachable-range rule was applied (C2).
**Code:** `k12_census.py` (enumerator + census C1–C5), `k12_verify.py` (skeptic-mandated battery D1–D7).
**Raw output:** `results_k12_census_console.txt`, `results_k12_verify_console.txt`, `results/k12_census.json`, `results/k12_verify.json`.

---

## Verdict

**The census is solid and externally validated. The instrument is not: readout M is not representative-invariant, and the root cause is a genuine substrate finding — the Exp 134 rule's tie-breaking is unspecified.**

1. **Census (C1, validated by D4/D5/D7):** 755 classes of closed self-avoiding 12-cycles in Z³ up to isometry × cyclic shift × reversal; **8 survivors**. Complete K≤12 survivor family: 1 / 1 / 2 / 2 / 8. External validation: raw closure counts match published cubic-lattice self-avoiding-polygon counts at all three K (138×24=3,312; 2,010×24=48,240; 31,754×24=762,096); pairwise duplicate scan of all K=8/K=10 class representatives found zero; the 2×2×3 box graph has exactly 4 Hamiltonian-cycle classes by direct enumeration (matching the census's chords=8 row); all 8 survivors have true minimal period 12. New fixture types: the first **non-rectangular planar survivor** (a staircase, chords=5) and the **box quadruplet** (four Hamiltonian orderings of the identical 2×2×3 cell set — all four survive).
2. **Claim-5 falsifier remains unreachable — now with scaling evidence (C2 + D6).** Census pos ceiling at K=12: 0.228 (non-monotone across K: 0.322 / 0.166 / 0.228). Constructed dense box cycles: pos = 0.082 (K=16), 0.134 (K=32), **0.027 (K=72)** — the ring graph's spectral reading grows far slower than the matched-K ambient anchor. On lattice-cycle fixtures the EXPAND falsifier is out of reach at every scale probed; a claim-5 test needs a different fixture class (consistent with RAW 134 §14's charge that lattice fixtures are off-ontology anyway).
3. **Survival concentrates at high chord count / compactness — the two unseparated (C3, skeptic's null accepted).** 0/466 classes with ≤3 chords survive; survival rate rises to 4/4 at chords=8. By distinct cell sets the survivors are 5 shapes (6×2 rectangle, staircase, two two-layer shapes, the box). Chord count co-varies with solidity; no claim about which selects. K-relative, not a law (the K=4 survivor has 0 chords).
4. **Test 3's fixed-chords hint: no update (C4, reframed per skeptic).** 3 of 4 survivor readings sit below their stratum medians (chords=4: −0.101 vs −0.013; chords=5: 0.074 vs 0.080; chords=6: −0.017 and 0.130 vs 0.104). Under an exchangeable null P ≈ 0.31. Unpowered; weakly in the hint's direction; not a replication and not a non-replication.
5. **The headline that had to be withdrawn, and what replaced it.** The box quadruplet — identical cell set, identical coupling graph by construction, RG identical to 6 decimals — reads M = 5.16 / 5.47 / 5.79 / 6.00 (point gaps up to 0.84; bootstrap jitter ±0.02). The intended headline "M reads dynamical flow ordering beyond graph structure" did NOT survive verification: **D1 shows per-class M is ill-defined** — reversal of one member's traversal shifts its reading by 17 bootstrap-sd, and *lattice rotation of the same ordered cycle* shifts three of four members by 7–25. The traced mechanism (single-kick trace): the unperturbed limit cycle is exactly rotation-covariant, but the very first ±1 kick creates an |γ| tie (kicked cell reaches the current maximum; verified tie at |γ|=12, divergence at tick 1), and **the rule resolves |γ| ties by dict/set iteration order — implementation-defined, not isometry-covariant.** What the quadruplet's M-spread measures is therefore some mixture of ordering-dependent dynamics and arbitrary tie resolution, and the two cannot be separated until the substrate specifies symmetric tie-breaking.
6. **Phase 1b's gate survives this (checked, not assumed):** the G-M1 FLAT/CUBE gap re-verified under representative / reversed / rotated variants: +0.476 / +0.570 / +0.539, z ≥ 20, same sign. Rep-dependence exists at K=8 (readings shift ≤0.075) but is an order of magnitude below the certified gap. The falsified Phase-1b sentence ("isomorphic local graphs would read bit-identically") received a dated Correction in `RESULTS_phase1b.md`.
7. **What M's driver is NOT (D2/D3):** not channel count within the quadruplet (n_active = 12 for all four; frac_nonzero identical) and not coarse death demography (S1 = 0.238–0.241, absorbed = 24/288, death median 5.0, max 11 — identical across all four). Remnant composition differs dramatically (one ordering leaves mostly 10-cell remnants, another mostly 6-cell, another mostly 4/6) and is the remaining physical candidate — but attribution is moot until tie-breaking is specified. Note: the two chords=6 survivors have UNEQUAL n_active (13 vs 15), so their M spread (5.99 vs 7.27) is partly channel-count; no claim made on that pair.

**The substrate finding (new, root-caused): Exp 134's renewal rule is isometry-covariant only on tie-free states.** Unperturbed survivors never hit ties (distinct |γ| values); damage dynamics hit them immediately. Every damage-based reading on this substrate inherits implementation-defined tie resolution. Before any further instrument work on Exp 134: **specify tie-breaking** — either isometry-covariantly (e.g., treat a tied state as wedged, like `find_c0` non-uniqueness already does) or as an explicit declared convention.

## Skeptic review

Fresh-context skeptic pass on the census bundle before this doc; D1–D7 run in response. Objections and resolutions:

| # | objection | resolution |
|---|---|---|
| 1 | Headline is an attribution claim shielded by "census" scope; it falsifies a certified Phase-1b sentence, which is owed a dated correction, not a "refinement." | **FIXED.** Correction appended to `RESULTS_phase1b.md`; headline withdrawn and replaced (Verdict 5) — the stronger claim did not even survive D1. |
| 2 | D1 (representative invariance) is a precondition for the headline: M(reversed/shifted/rotated rep) never checked. | **RUN — FAILED.** Shift-invariant (z ≤ 0.2); NOT reversal-invariant (z=17.1 on box[2]); NOT rotation-invariant (z = 24.8 / 11.0 / 7.3 on three members). Per-class M ill-defined at K=12. Mechanism traced to tie-breaking (Verdict 5). Phase-1b K8 gate re-verified rep-robust (Verdict 6). |
| 3 | D2: n_active/frac_nonzero discarded by the bootstrap wrapper; channel-count explanation unexcluded. | **RUN.** Quadruplet: n_active = 12 × 4, equal — excluded. Chords=6 pair: 13 vs 15 — their spread flagged as partly channel-count (Verdict 7). |
| 4 | D3: if M tracks death demography, "flow ordering" reduces to "M reads the corpse." | **RUN.** Coarse demography identical across the quadruplet (excluded as driver); remnant composition differs (remaining candidate; moot pending tie-breaking). |
| 5 | D4: box Hamiltonian-class count inferred, not checked. | **RUN.** Direct enumeration: exactly 4 classes. Confirmed. |
| 6 | D5: external validation available (SAP counts) and canonical() duplicate risk unchecked. | **RUN.** OEIS-consistent 3/3; zero duplicates among all K=8/K=10 representatives. |
| 7 | D6: "EXPAND unreachable on lattice cycles" claimed from a 3-point non-monotone series. | **RUN.** Constructed box cycles at K=16/32/72: pos 0.082/0.134/0.027. Claim now scoped: unreachable at K≤12 by census, and along the 2-layer box family to K=72 by construction. |
| 8 | D7: true periods unverified (48 divisible by proper divisors). | **RUN.** All 8 survivors: minimal period exactly 12. |
| 9 | C4 "does NOT replicate" is negative over-rotation on n=1,1,2. | **FIXED.** Reframed: 3/4 low, P ≈ 0.31, no update (Verdict 4). |
| 10 | Bundle arithmetic: "0/459" should be 0/466 (dropped chords=2 rank=2 row). | **FIXED.** 466 everywhere. |
| 11 | "57 bootstrap-σ" is σ-laundering recidivism. | **ACCEPTED.** Stated as point gaps ± resampling jitter throughout. |
| 12 | "Survival is chord-structured" overstates: 4/4 is one cell set ×4; chords ⟺ compactness unseparated; K-relative. | **ACCEPTED.** Verdict 3 reworded to the supportable form. |
| 13 | Proposed quadruplet-based claim-5 test is ill-posed: n=4 has no power, and S1-vs-M is circular (same kick-death process on both sides). | **ACCEPTED.** No claim-5 test will be built on this family. Post-D1, the quadruplet is not even a clean instrument-characterization family until tie-breaking is specified. |
| 14 | pos ceiling class is chords=5, beating chords=8 (RG non-monotone in chords) — undercuts chord-causal readings. | **ACCEPTED.** Noted in Verdict 3's wording; no chord-causal claim retained. |

## Known limitations

- All spread/σ figures are bootstrap-stability on deterministic fixtures, not population statistics.
- D6's scaling evidence covers the 2-layer box family only; solid boxes (e.g. 4×4×4) unprobed — the downward trend at K=72 (0.027) makes reachability implausible but unproven for all shapes.
- The chords=6 pair and all cross-shape M comparisons at K=12 carry both the channel-count and the tie-breaking caveats; only within-quadruplet comparisons controlled channel count, and those carry the tie-breaking caveat.
- The tie-breaking mechanism was traced on one kick (tie at first tick, divergence at first tick); a full census of tie events per trajectory was not run — the single trace suffices for existence, not for quantifying how much of the M-spread ties explain.

## What this proves / does not prove

- **Proves:** the complete, externally validated K≤12 cycle census (755 classes, 8 survivors, 5 shapes); the claim-5 falsifier's unreachability on lattice cycles at K≤12 and along box cycles to K=72; readout M is not a function of the coupling graph AND not a well-defined function of the pattern class (representative-dependent); the Exp 134 rule's isometry-covariance holds only on tie-free states, with tie resolution implementation-defined; Phase 1b's K8 gate discrimination is representative-robust.
- **Does not prove:** any claim-5 content in either direction; that "dynamical flow ordering" is a real signal axis (inseparable from tie-breaking arbitrariness as implemented); what selects survivors (chords vs compactness unseparated); ceiling behavior for arbitrary large-K shapes.

## Next steps (banked, in order)

1. **Substrate: specify tie-breaking in the Exp 134 rule** (isometry-covariant option: tied |γ| ⇒ wedge, mirroring `find_c0`'s existing non-uniqueness semantics; or an explicit declared convention). Re-run D1 after; only then revisit whether the quadruplet's M-spread has physical content.
2. **Claim 5 leaves this fixture class** — per Verdict 2 and RAW 134 §16.2: either a richer rule (non-cycle survivors) or the §14-faithful delay-native substrate.
3. The K=16 box (2×2×4) Hamiltonian-class family as a wider controlled family — only after (1).
