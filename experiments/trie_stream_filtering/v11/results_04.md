# Experiment 04 — Cross-band correlation results

**Sample / region:** `data/FLAC_11_secs_Small_75d2275409.flac` channel 0, t=1.0..2.0s (same as Exp 02/03).
**Decomposition:** db8, 7 levels, periodization. Parent band W3 (cD5, 689–1378 Hz), child band W4 (cD4, 1378–2756 Hz), zerotree alignment W3[k] ↔ (W4[2k], W4[2k+1]), offset 0 (selected on train, also the a priori default).
**Process:** pre-registered criteria in `EXPERIMENT_04_crossband.md`; two skeptic passes (one after the first run — which caught an unregistered deviation and a wrong premise — and one after the controls). Run artifacts: `results/diagnostic_04_summary.json`, `results/diagnostic_04b_summary.json`, `results/plots_04/`.

---

## TL;DR

| Hypothesis | Formal verdict | What it actually means |
|---|---|---|
| **H1 — raw cross-band dependency exists** | **PASS** (MI 0.210 vs null p99 0.088) | Real, robust — but it is **db8 filter leakage of the fundamental**, not harmonic structure. The sample has no meaningful 2nd harmonic (0.26% energy at ~2100 Hz). |
| **H2 — dependency survives per-band LPC** | **marginal PASS** (MI 0.0775 vs p99 0.0740) | At the detection boundary and identified as **shared loudness envelope**: collapses under local variance normalization (0.0775 → 0.0494, below null). Not robust: excluding LPC warm-up pairs flips it to FAIL (0.0720 vs 0.0743). |
| **H3 — exploitable by trie/context model (held-out)** | **FAIL** (+0.031 bits/sym vs 0.10 margin; sanity OK) | Net parent gain at matched temporal context: **+0.009 ± 0.020 bits/sym = zero**. Foreordained: the bias-corrected H2 effect (~0.016 bits) was already below the margin. |

**Interpretation-matrix row: H1 pass / H2 marginal / H3 fail → the v11 open question closes NEGATIVE.**
The Exp 03 hint that motivated this experiment (W4 residual max|R| = 0.274, "harmonics correlate across bands") is now fully explained by two mundane mechanisms — filter leakage of the fundamental and a shared loudness envelope — neither of which a trie can or should exploit beyond what an envelope/gain coder already does.

---

## The wrong premise, caught by the data

The design premise was "W4 contains the 2nd harmonic of W3's ~1050 Hz tone." It does not:

- The region's spectrum has two tones near 949 and 1060 Hz; energy at 2050–2150 Hz is **0.26%** of the signal.
- W4's nominal band (1378–2756 Hz) carries only ~1.4% of raw signal energy, yet W4 coefficients hold 5.6% — the difference is the **fundamental leaking through db8's wide transition band**. W4's coefficient-domain spectrum peaks at the leaked fundamental, not at any alias of 2100 Hz.
- Synthetic control: a **pure 1050 Hz tone with no harmonics** produces strong cross-band dependency in raw coefficients (mag_r = 0.63, MI = 1.72 — 8× the real sample's). Direct energy accounting: db8 routes **6.8%** of the tone's W3+W4 energy into W4, ~570,000× the −60 dB noise floor. (The surrogate pass/fail verdict on this synthetic is itself uninformative — a circular-shift null does not destroy dependency on periodic deterministic signals; it passed in only 7/10 surrogate seeds. The leakage claim rests on the energy accounting and effect size, not on that test.)

## Controls (diagnostic_04b)

**Control B — envelope normalization (the decisive one for H2).** Local variance normalization (rolling σ, ~23 ms time-matched windows: 64 coefs in W4, 32 in W3):

| | MI (bits) | null p99 | verdict |
|---|---:|---:|---|
| residual, baseline | 0.0775 | 0.0723 | marginal PASS |
| residual, envelope-normalized | **0.0494** | 0.0756 | **FAIL** (mag_r 0.256 → 0.044) |
| raw, baseline | 0.2098 | 0.0918 | PASS |
| raw, envelope-normalized | **0.1890** | 0.0900 | **PASS** |

The raw-band survival is the **positive control for the normalization pipeline**: rolling-σ normalization preserves phase-locked dependency (the leaked tone) while removing shared-variance dependency. So the residual-level collapse is informative: **what survives LPC is the loudness envelope, and only the loudness envelope.**

**Control A — synthetic harmonics.** Tone + genuine 2nd harmonic at 0.26% (the real sample's level) and at 5%: the H2-type test detects nothing in either case. Caveat on scope: on periodic material the circular-shift null has reduced power (synthetic residual nulls inflate to 0.07–0.16), and the pure-tone synthetic residual retains signed cross-band r ≈ 0.73 after edge removal — so this control bounds **the test**, not the physics. The claim "LPC absorbs stationary harmonics" is NOT established here; what is established is that the H2 procedure as designed cannot detect harmonic coupling at these levels, which further deflates what Exp 03's hint could ever have meant under this analysis.

## H3 details

Patched run (pre-registered LPC procedure), 16-symbol alphabet, train/val/test = 1378/551/828, Laplace smoothing:

| model | context | val (bits/sym) | test (bits/sym) |
|---|---|---:|---:|
| M0 | none (marginal) | 2.916 | **3.105** |
| M1 | prev W4 symbol @8 | 2.982 | 3.166 |
| M2 | parent W3 @4 | 2.915 | 3.108 |
| M3 | prev @4 + parent @4 | 2.985 | 3.135 |

- M3 advantage over M1: +0.031 bits/sym < pre-registered 0.10 margin → **FAIL**. Misaligned-parent surrogate: +0.026 ± 0.020 → sanity OK (the small advantage is reproduced without alignment).
- **Net parent gain at matched temporal context: +0.009 bits/sym** (aligned-vs-matched −0.017, rolled-vs-matched −0.026 ± 0.020). Zero.
- M0 beats every contextual model on test. Decomposition (skeptic-verified): the M1 penalty of +0.062 is ~+0.041 Laplace count-fragmentation (measured on shuffled targets) plus ~0.02 mild train→test nonstationarity (also visible as the 0.19-bit val→test gap — the same loudness envelope Control B identified). Consistent with near-white residuals; no anomaly remains untraced.
- Internal consistency: bias-corrected H2 MI ≈ 0.077 − 0.061 (null mean) = **0.016 bits** — the information ceiling for any context model was already 6× below the pass margin before H3 ran.

## Deviations from pre-registration (both caught by skeptic pass 1, both fixed and re-run)

1. **LPC fit split (material).** First run fit LPC on the train half; the design pre-registered full-region fit ("as in Exp 03"). The train-only fit created a shared heteroscedastic mismatch envelope in both bands that inflated H2 MI to 0.128 (~65% over the pre-registered 0.0775) and broke H3 entirely (all models worse than uniform on test; random parent context "gained" +0.165 bits/sym via fragmentation-toward-uniform). All reported numbers are from the corrected re-run.
2. **σ3 quantizer scale (minor).** Design said train-split σ; first run used full-region σ for the parent band. Corrected to σ over the first 50% of the r3 array in band-index space (note: band-index prefix, not the exact train-split parent-pair set — a residual imprecision, immaterial at this effect size).

## What this changes

- **v11's only open question is now answered.** SUMMARY.md's "cross-band correlation, never tested" → tested, mechanism identified, negative. The trie has no role here: the only structure surviving per-band LPC is the loudness envelope, which a gain/envelope coder handles natively and which sits at the very boundary of detectability (0.016 bits bias-corrected).
- **Exp 03's surprise #4 is retracted as a hint.** W4's elevated residual max|R| was leakage + envelope, not harmonic coupling. Per-band LPC + entropy coding remains approximately optimal on this material; the v11 closure verdict stands, now with no asterisk.
- **Scope limits.** One sample, one region, one wavelet family, n_pairs = 2757. A signal with strong *modulated* harmonics (vibrato, attack transients) was not tested and remains formally open — but nothing observed here motivates pursuing it, and the test as designed has limited power on such material anyway (periodic-signal null weakness, Control A).

## Relation to prior art

The outcome matches the literature consulted at design time: wavelet-HMT work locates cross-scale dependency in magnitudes/variances ("persistence"), which is exactly what we found — the magnitude envelope — and zerotree coders exploit precisely that and nothing finer. The experiment's contribution is local and deflationary: on this material, after per-band LPC, the magnitude dependency that remains is the audible loudness envelope at ~0.016 bits/symbol — real, precedented, and too small to matter.

---

*Run 2026-06-10. One patched re-run + two controls. Two skeptic passes; first caught an unregistered deviation that had inflated the key statistic by 65% and a wrong design premise; second verified the controls and required six edits, all incorporated. Exp 04 closes the v11 arc with no open questions.*
