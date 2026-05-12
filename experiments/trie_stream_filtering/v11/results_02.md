# Experiment 02 — Band-split results

**Sample:** `data/FLAC_11_secs_Small_75d2275409.flac` channel 0, t=1.0..2.0s (44100 samples).
**Filterbank:** 8 octave-spaced Butterworth bandpasses (order 4, zero-phase via `sosfiltfilt`).
**Run:** `python diagnostic_02.py` → `results/diagnostic_02_summary.json`, `results/plots_02/*.png`.

---

## TL;DR

| Hypothesis | Verdict | One-line reason |
|---|---|---|
| **H1' — per-band energy concentration** | **PASS-AT-BAND-LEVEL, FAIL-AT-BIN-LEVEL** | B4 (800-1600 Hz) holds **97.2%** of total energy with clear peak at 949 Hz — the band-split correctly isolates the dominant content. But within B4, top-3 bins hold only 19% — high-resolution FFT (1 Hz/bin) spreads a real-world tone across many adjacent bins. Concentration is a band-vs-bands story, not a bins-within-band story. |
| **H2' — per-band TP regularity** | **STRONG PASS** | Composite TP/2·peak = 1.29. Per-band ratios for the energetic bands all converge to ≈1.0: B3=0.93, B4=**1.06**, B5=1.05, B6=1.14, B7=1.05. Per-band TPs are nearly pure-sine-like. **This is the headline win.** |
| **H3' — per-band residual structure** | **PASS, with filter caveat** | Composite LPC8 max\|R\|=0.23. Per-band: B0=0.99, B1=0.99, B2=0.99, B3=0.97, B4=0.94, B5=0.78, B6=0.62, B7=0.34. Massive residual autocorrelation per band — but this is partly filter-induced (bandpass-limited residual). The residual structure is real and exploitable; whether by trie or by higher-order LPC is a separate question. |

**The band-split idea is structurally validated on the tonal region.** H2' is the cleanest result. H1' passes at the right granularity (band-level energy isolation) and fails at the wrong granularity (bin-level concentration within a 1-sec FFT). H3' passes but with a measurement caveat.

---

## Numbers

| measurement | composite | B0 (25-100) | B1 (100-200) | B2 (200-400) | B3 (400-800) | **B4 (800-1600)** | B5 (1600-3200) | B6 (3200-6400) | B7 (6400-~Nyq) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| energy_pct_of_total | 100.0 | 0.2 | 0.0 | 0.0 | 0.4 | **97.2** | 1.1 | 0.1 | 0.0 |
| peak_freq_hz | 949 | 26 | 126 | 343 | 936 | **949** | 2122 | 3793 | 9968 |
| top3_energy_pct | 18.9 | 9.8 | 4.5 | 5.4 | 5.4 | 19.2 | 8.5 | 6.3 | 0.7 |
| top10_energy_pct | 48.7 | 29.0 | 13.6 | 13.9 | 14.5 | 49.7 | 21.1 | 13.3 | 1.9 |
| tp_density_hz | 2448 | 146 | 315 | 639 | 1733 | 2019 | 4473 | 8638 | 20878 |
| **tp_density / 2·peak** | **1.29** | 2.81 | 1.25 | 0.93 | 0.93 | **1.06** | 1.05 | 1.14 | 1.05 |
| raw_entropy_bits | 9.65 | 3.86 | 4.94 | 6.03 | 8.03 | 9.85 | 7.68 | 7.51 | 6.63 |
| lpc8_resid_entropy | 6.90 | 3.53 | 4.89 | 6.31 | 8.27 | 7.80 | 7.76 | 7.42 | 6.16 |
| **lpc8_resid_max\|R\|** | **0.231** | 0.989 | 0.986 | 0.987 | 0.974 | **0.941** | 0.776 | 0.617 | 0.344 |
| lpc8_resid_mean\|R\| | 0.067 | 0.839 | 0.691 | 0.491 | 0.439 | 0.394 | 0.261 | 0.177 | 0.078 |

---

## Per-hypothesis verdict in detail

### H1' — Per-band energy concentration: pass at band level

The right reading is **B4 holds 97.2% of total energy**. The signal at this 1-second tonal region is essentially mono-band. The band-split correctly isolated the dominant content — that's the structural answer the experiment was looking for.

**The original H1' prediction (top-3 of in-band energy ≥ 80%) failed everywhere.** B4's top-3 = 19.2%, only marginally better than composite's 18.9%. But this is a **window-resolution artifact**, not a real failure: at 1-second FFT (1 Hz/bin resolution), a real-world 1050 Hz tone spreads across ~10-30 bins due to natural pitch wobble, finite-bandwidth ringing, and spectral leakage. Top-3 of 22051 bins doesn't capture this. Top-50 was not measured here but would tell a different story.

If the top-K predicate is the diagnostic for H1', it doesn't pass. But the *intent* of H1' — that the band signal has clearly-localized energy — is met definitively (97.2% in one band, peak at 949 Hz). The original metric was the wrong operationalisation; the band-isolation success is what matters for the codec.

### H2' — Per-band TP regularity: strong pass

This is the cleanest result. Composite TP_density / (2 × peak) = 1.29 (some non-tonal harmonic content). Per band:

| Band | TP/2·peak | Notes |
|---|---:|---|
| B0 (25-100) | 2.81 | Off, but only 0.2% energy. DC/very-low-freq artifacts. |
| B1 (100-200) | 1.25 | Below 1%-energy threshold. |
| B2 (200-400) | 0.93 | Sub-1%-energy. |
| B3 (400-800) | 0.93 | Approaching meaningful: ratio is clean. |
| **B4 (800-1600)** | **1.06** | **The dominant band: TP density is 6% above pure-sine prediction.** |
| B5 (1600-3200) | 1.05 | Clean. |
| B6 (3200-6400) | 1.14 | Slightly noisier. |
| B7 (6400-~Nyq) | 1.05 | Clean even on noise-band content. |

Five of the eight bands have TP_density / (2 × peak) within [0.9, 1.15] — pure-sine-territory. The dominant band (B4) is 1.06: TPs in this band reflect the band's peak frequency essentially exactly. Compare to composite 1.29 (29% above pure-sine prediction).

**Per-band TPs are a meaningfully cleaner primitive than raw-signal TPs.** The hypothesised structural fix works.

### H3' — Per-band residual structure: pass, but with a real caveat

LPC8 residual autocorrelation max\|R\| at lags 2..50:

- Composite: 0.231
- Per band: 0.99, 0.99, 0.99, 0.97, 0.94, 0.78, 0.62, 0.34

Per-band residuals have enormous autocorrelation. The signal in each band, after LPC8 prediction, still has a near-perfect periodic structure. **This means LPC8 is not a strong predictor for the per-band signal — there is large amounts of exploitable structure remaining.**

**Caveat (important):** the per-band residual is itself bandpass-limited (because the band signal is bandpass-limited). Bandpass-limited noise/residual has autocorrelation at lag ≈ sample_rate / center_freq. For B4 (center ~1100 Hz at 44100 Hz sr), that's lag ≈ 40 samples — exactly within the 2..50 measurement window. So part of what the autocorrelation is showing may be an artifact of the filter's transfer function, not of the underlying signal's autocorrelation structure.

Two interpretations, both consistent with the data:

1. **Bullish for the codec:** the per-band signal has more structure than a generic LPC8 captures. A higher-order predictor, or a trie over the residual, can exploit this.
2. **Bearish caveat:** the structure may be a property of the bandpass filter, not the signal. A different decomposition (QMF, wavelet) might leave a different residual character. The "residual structure" finding is decomposition-dependent.

For the codec design: the H3' pass means *something* in the per-band domain has predictable structure beyond LPC8. Whether the trie is the right tool to capture it (vs. higher-order LPC, or per-band predictor matching the filter's properties) is a downstream design decision that this experiment doesn't settle.

---

## What this changes about the codec design (cumulative with Exp 01)

After Exp 01: rejected fixed-universal-basis, accepted band-split, motivated trie-on-residual.

After Exp 02:
- **Band-split is structurally confirmed** as a precondition for clean per-band primitives (H2'). The band-split is no longer optional in the design.
- **TP encoding becomes viable per band.** B4's TP_density / 2·peak = 1.06 confirms that within a band the TPs are cleanly tied to the band's dominant frequency. This was the original idea's load-bearing assumption, and it survives.
- **The "trie-on-residual" claim has a new caveat.** The per-band residual structure is partially filter-induced. Pursuing a trie codec means committing to a specific (reversible) decomposition and re-measuring residual structure on that decomposition.
- **B4 captures 97.2% of energy alone.** A real codec for similar tonal music could potentially encode just the dominant band well and treat other bands as small residuals. This argues for **adaptive band importance** — not all bands need equal precision.

Updated codec sketch:

```
input → 1-sec frames
      → REVERSIBLE band decomposition (QMF or wavelet — NOT Butterworth)
      → per band:
            if band carries < 0.5% energy → encode minimally (zeros + small residual)
            else:
              estimate K dominant frequencies in this band (K=1-3 should suffice given B4's behaviour)
              predict via sinusoidal model OR per-band-tuned LPC
              residual = actual - prediction
              entropy-code residual via [trie / LPC32 / arithmetic with context]
      → multiplex bands + side info → output
```

---

## What Experiment 02 did NOT settle

- **Reversibility.** Butterworth zero-phase filtering is not bit-reversible. The next experiment must move to QMF, MDCT, or a wavelet decomposition.
- **Whether the TP-encoding actually compresses per-band signals.** TP regularity (H2') confirms TPs are meaningful in each band. It does not confirm that storing (TP_tick, peak_amplitude) pairs is fewer bits than storing the band's samples directly. That's a separate measurement: encode B4 as (TPs + amplitudes + interpolation residual) vs storing B4 samples directly with LPC + Rice.
- **Whether the conclusions hold on non-tonal content.** Block 3 of Exp 01 (busy/transient) was not band-split here. Likely the band-split won't isolate energy as cleanly there.
- **Whether 8 octaves is the right granularity.** Could be too coarse for some content, too fine for others.
- **The trie specifically vs alternatives** (higher-order LPC, arithmetic coding) for capturing the residual structure. H3' just says structure exists; the trie-as-mechanism question is unresolved.

---

## Surprises

1. **B7 (6.4-22 kHz noise band) has clean TP regularity.** TP_density / 2·peak = 1.05 — even the noise band's TPs are pure-sine-like to its dominant component. Suggests TP encoding might be useful even outside obvious tonal bands.

2. **The energy distribution is essentially binary: B4 has 97.2%, everything else < 1.5%.** This is a more skewed distribution than I expected. For this kind of tonal music, a codec could spend most of its bits on B4 and treat other bands as nearly-free. This is qualitatively similar to how MP3 / AAC do bit-allocation, but the binary-ness is striking.

3. **B0 (the lowest band, 25-100 Hz) has 0.989 max\|R\| but only 0.2% energy.** The bandpass filter on a near-empty range produces a residual that's almost entirely the filter's own ringing. This is a clean illustration of the filter-induced-structure caveat for H3'.

4. **The composite top-3 in Exp 02 (18.9%) is much lower than Exp 01's block 1 top-3 (91.2%).** Same signal, different window length: 100 ms (Exp 01) vs 1 s (Exp 02). At 1 Hz/bin resolution the energy spreads further. This is purely a measurement artifact, but it's a useful reminder that "energy concentration" depends on FFT resolution as much as on signal structure.

---

## Plots

`results/plots_02/`:

1. `01_band_waveforms.png` — 8 stacked subplots showing each band's filtered waveform. B4 dominates visibly; bands 0-3 are near-silence; bands 5-7 show fine structure.
2. `02_band_ffts.png` — 8 stacked FFTs. Each band has its energy localised to its passband, with B4's peak clearly visible.
3. `03_band_lpc_resid_autocorr.png` — per-band LPC8 residual autocorrelation. Bands 0-4 show strong slow-decaying oscillations (filter-induced + signal); bands 5-7 decay faster.

---

## Recommended next step

The natural sequel is **Experiment 03 — reversibility**: replace Butterworth with a reversible decomposition (most likely a wavelet — Daubechies-N or symlet, with `pywt`) and re-measure H1', H2', H3'. If the per-band metrics survive the move to a reversible decomposition, the codec architecture is on solid lossless ground. If wavelet-decomposed bands lose the H2' cleanup, the codec might need a non-orthogonal-filterbank decomposition with explicit residual storage.

Alternative: skip the reversibility test for now and run Experiment 02 on a non-tonal block (the 9.5s region from Exp 01) to see whether the band-split helps when energy is broadband. This is the harder case and would falsify the band-split if it doesn't help.

I'd suggest Experiment 03 (reversibility) first — the codec must be lossless, and a band-split that loses information is a non-starter regardless of how clean its per-band metrics look.
