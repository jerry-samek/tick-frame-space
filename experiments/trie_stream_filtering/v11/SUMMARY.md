# v11 — Summary and closure

**Status: CLOSED 2026-05-12.**
**Goal:** explore whether trie stream filtering (v4-v10) can serve as the basis of a lossless audio codec.
**Outcome:** the trie is not the right tool for lossless audio compression. The "layered WAV" framing is the honest characterization. The codec direction is shelved; one specific scientific question remains open (cross-band correlation, never tested).

---

## What was done

Three diagnostic experiments + one size estimate, on the 11-second FLAC sample `data/FLAC_11_secs_Small_75d2275409.flac` (44.1 kHz, 24-bit, stereo).

### Exp 01 — raw-signal diagnostic
*Did the 11-sec sample have the structure the codec design assumes?*

Three hypotheses tested on 3 × 100ms blocks:
- **H1 (energy concentration at a few frequencies):** PARTIAL — top-3 holds 91% on tonal block, only 12% on busy block.
- **H2 (turning-point informativeness):** PARTIAL — TP_density / (2·peak) ranged 1.21 → 3.37 across blocks.
- **H3 (residual structure beyond LPC):** PASS — LPC8 residual max|R| = 0.22–0.36 at non-trivial lags.

Conclusion: the codec idea wasn't falsified, but the *original* "fixed universal basis + raw-signal TPs" formulation was. The data motivated band decomposition.

### Exp 02 — Butterworth band-split
*Does per-band analysis clean up the H1/H2 partial verdicts on tonal content?*

- **H1' (per-band energy):** PASS at band level — B4 (800-1600 Hz) holds 97.2% of energy.
- **H2' (per-band TP regularity):** STRONG PASS — B4 TP/2·peak = 1.06; most bands within [0.9, 1.15].
- **H3' (per-band residual):** PASS but with a caveat — per-band LPC residual max|R| = 0.94 in dominant band.

Conclusion: band-split is structurally validated. **But:** Butterworth zero-phase filtering is not lossless. The H3' "strong pass" might be filter-induced.

### Exp 03 — reversibility (wavelet)
*Do the per-band findings survive a lossless decomposition?*

- **Reversibility verification:** max reconstruction error 6.66e-16 (machine epsilon × 3). PASS.
- **H1'' (energy isolation):** PASS — W3 holds 93.3% of energy.
- **H2'' (TP regularity):** PASS — W3 TP/2·peak = 0.90.
- **H3'' (residual structure):** **FAIL** — W3 LPC8 residual max|R| = 0.142 (Exp 02's analogous band was 0.94).

**The key consequence:** the dramatic per-band residual autocorrelation in Exp 02 was largely Butterworth-filter-induced. Under a real lossless decomposition, per-band residuals are nearly white. The trie's role as a **residual compressor** is not supported.

### Size estimate
*How big would a trie codec be vs FLAC?*

| Representation | Size (KB) | vs FLAC |
|---|---:|---:|
| Raw 24-bit PCM | 2,738 | 1.51× |
| FLAC (actual) | 1,815 | 1.00× |
| Trie A — per-sample (tick+value), v10 style | 4,906 | **2.70×** |
| Trie B — per-band LPC residual entropy floor | 775 | 0.43× |
| Trie C — per-coef (band+pos+value) | 5,134 | 2.83× |

Trie B's "better than FLAC" is misleading — it's the Shannon floor for sequential per-band LPC + arithmetic coding (which is what MPEG-4 ALS / OptimFROG do, not a trie). The moment you keep the trie's distinguishing feature (explicit position → queryable / progressive), you're back to 2.7–2.9× FLAC.

With gzip on top of Trie A, the tick stream compresses well and the multiplier drops to ~1.5–1.8× FLAC. Still bigger, and the gzip recovery is itself a hint: if the trie's "advantage" can be undone by a general-purpose entropy coder, the trie isn't doing information-theoretic work — it's organizing the same information differently.

---

## What survives, what doesn't

**Survives:**
- Band decomposition is structurally sound (works lossless via wavelet).
- Per-band TPs are a clean primitive for tonal content.
- Phase 3 / observer-cell ideas are unaffected (different lineage).

**Falsified:**
- "Trie compresses better than (per-band LPC + Rice/arithmetic) by exploiting residual structure" — not supported by Exp 03's wavelet data.
- "Fixed universal frequency basis" — Exp 01 showed energy distribution is content-dependent.
- "Raw-signal TPs are useful directly" — Exp 01 showed they're only meaningful on near-mono-tonal content.

**Untested (only open scientific question):**
- **Cross-band / cross-time correlation.** Exp 03's W4 (2nd-harmonic band) had max|R| = 0.274 — higher than the dominant W3's 0.142. Harmonics correlate across bands, and per-band LPC can't see that. **A trie operating cross-band might still add value LPC alone can't.** This is the one direction the diagnostics did not rule out.

---

## Why v11 is closing here

Three reasons:

1. **The central novelty claim is unsupported.** The trie's job in the codec was supposed to be "compress per-band residual better than entropy coding." Exp 03 shows the residual is mostly white per band — there's nothing for the trie to learn. The codec without that role is just (band decomposition + per-band LPC + Rice), which is approximately MPEG-4 ALS — not novel.

2. **The progressive/queryable use case doesn't justify the size cost in 2026.** v10 already showed the trie *expands* storage by ~4.6× as a flat memory; v11 narrowed that to ~2.7× FLAC (~1.5× with gzip) but the value proposition is "indexed/progressive retrieval," which gigabit fiber and small audio file sizes largely obviated.

3. **The remaining open question (cross-band correlation) is a different experiment.** Exp 04 would not be "more of the codec axis." It would be: "does the trie capture harmonic structure across bands that single-band predictors can't?" That's a self-contained question, separable from the codec framing, and could be picked up later if someone wants to investigate it.

---

## File inventory

```
v11/
├── data/                                  # input FLACs (downloaded 2026-05-09)
├── EXPERIMENT_01_diagnostic.md            # raw-signal diagnostic — description
├── diagnostic_01.py                       # implementation
├── results_01.md                          # per-hypothesis verdicts
├── EXPERIMENT_02_bandsplit.md             # Butterworth band-split — description
├── diagnostic_02.py
├── results_02.md
├── EXPERIMENT_03_reversibility.md         # wavelet (db8) — description
├── diagnostic_03.py
├── results_03.md
├── _estimate_trie_size.py                 # vs-FLAC size estimate
├── _check_env.py                          # initial env sanity
├── SUMMARY.md                             # this file
└── results/                               # all run outputs (plots, JSON, run logs)
    ├── diagnostic_01_summary.json
    ├── diagnostic_01_run.log
    ├── diagnostic_02_summary.json
    ├── diagnostic_02_run.log
    ├── diagnostic_03_summary.json
    ├── plots_01/                          # waveform, FFT, autocorr, LPC resid autocorr
    ├── plots_02/                          # per-band waveform, FFT, LPC resid autocorr
    └── plots_03/                          # per-sub-band waveform, FFT
```

---

## If anyone picks this up

The natural next move is **NOT** more codec diagnostics. It is:

1. **Frame Exp 04 narrowly as "cross-band correlation in wavelet space."** Take 1-3 seconds of tonal content. Decompose with db8. Measure correlations between coefficient sequences at different sub-bands — specifically, between W3 (fundamental) and W4 (2nd harmonic). If those correlations have stable patterns, design a small trie that operates on (W3-coef, W4-coef) co-occurrences and measure whether it compresses below independent per-band LPC.

2. **OR pivot off compression entirely.** Trie pattern-learning for audio classification, motif detection, or queryable indexing — none of which compete with FLAC and all of which could leverage the trie's actual strengths from v4-v10.

The codec framing was a wrong-target. The trie does several things well. Compression of generic lossless audio is not one of them.

---

*Closed 2026-05-12. Three experiments, one size estimate, one honest negative result. Scientific posture preserved across three skeptic-style verdicts. The codec idea was falsified at the right layer (residual structure under lossless decomposition), not after building the whole codec.*
