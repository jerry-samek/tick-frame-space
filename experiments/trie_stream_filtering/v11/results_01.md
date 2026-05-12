# Experiment 01 — Diagnostic results

**Sample:** `data/FLAC_11_secs_Small_75d2275409.flac` (44.1 kHz stereo, 10.6 s, channel 0 used).
**Blocks analysed:** 100 ms (4410 samples) at 1.0 s, 5.0 s, 9.5 s.
**Run:** `python diagnostic_01.py` → `results/diagnostic_01_run.log`, `results/diagnostic_01_summary.json`, `results/plots_01/*.png`.

---

## TL;DR

| Hypothesis | Verdict | One-line reason |
|---|---|---|
| **H1 — energy concentration at a few dominant frequencies** | **PARTIAL** | Strongly true on the tonal block (top-3 = 91%), false on the busy block (top-3 = 12%). Single universal basis won't work; per-block adaptive basis is required. |
| **H2 — turning-point informativeness** | **PARTIAL** | TP density / (2 × peak frequency) ranges 1.21 → 3.37 across blocks. TPs reflect the dominant component only when content is mono-tonal. **Strongly supports band-split + per-band TP.** |
| **H3 — residual has structure beyond LPC** | **PASS** | LPC8 residual autocorrelation has max\|R\| = 0.22–0.36 at non-trivial lags. Residual is NOT white. Trie / longer-range predictor has room to compress further than (LPC + Rice). |

**The codec idea is not falsified, but the original "fixed universal basis + raw-signal TPs" formulation is.** Diagnostic supports a different shape: **per-block adaptive band decomposition + per-band TP encoding + trie compression of the residual**.

---

## Numbers

| measurement | start (1.0 s) | middle (5.0 s) | end (9.5 s) |
|---|---:|---:|---:|
| peak FFT freq (Hz) | 1050 | 1080 | 1380 |
| top-3 energy % | **91.2** | 57.9 | 12.3 |
| top-10 energy % | 94.5 | 81.2 | 33.0 |
| top-50 energy % | 97.8 | 96.3 | 71.0 |
| top-100 energy % | 99.2 | 98.6 | 91.1 |
| TP count (per 100 ms block) | 254 | 399 | 930 |
| TP density (Hz) | 2540 | 3990 | 9300 |
| TP density / (2 × peak) | **1.21** | 1.85 | **3.37** |
| raw entropy (int16) | 11.93 | 11.98 | 10.20 |
| delta entropy (int16) | 11.18 | 11.36 | 8.64 |
| LPC4 residual entropy* | 7.77 | 7.80 | 5.65 |
| LPC8 residual entropy* | 7.57 | 7.69 | 5.49 |
| LPC8 residual var | 3.5e-5 | 1.0e-4 | 3.4e-5 |
| **LPC8 residual max\|R\| (lags 2..50)** | **0.349** | 0.221 | 0.357 |
| LPC8 residual mean\|R\| (lags 2..50) | 0.128 | 0.077 | 0.084 |

\* hist-entropy with 1024 bins; under-estimate vs the int16-equivalent metric by ~2 bits, but trends are the right shape. Real-codec relevant value is ≈ LPC residual entropy + 2.

---

## Per-hypothesis verdict in detail

### H1 — Energy concentration: PARTIAL

**Strongly true** on block 1 (91% in top-3 bins). The signal at 1.0 s is dominated by a few sinusoidal components. A "given frequencies" prior with K=3 captures the bulk of the signal there.

**Marginal** on block 2 (58% in top-3, 81% in top-10). The signal at 5.0 s has more harmonic content but is still concentrated.

**Decisively false** on block 3 (12% in top-3, 33% in top-10, only 71% in top-50). At 9.5 s the energy is spread across many bins. A small fixed basis won't capture it.

**What this implies for the codec:** the original "universal fixed basis" formulation (Option 1 from the design discussion) is not viable across this sample. **Adaptive per-block basis (Option 2)** is required. Per-block metadata cost (which K frequencies, with what amplitudes) becomes a real budget consideration.

### H2 — TP informativeness: PARTIAL

The diagnostic ratio TP_density / (2 × peak_freq) — which equals 1 if TPs are exactly the turning points of a pure sine at the peak frequency — comes in at **1.21**, **1.85**, **3.37**. Higher ratios mean TPs are dominated by harmonics or noise, not the fundamental.

Block 1 (1.21) is consistent with a near-tonal signal where harmonics add ~20% TP overhead.
Block 2 (1.85) suggests strong harmonic structure (each harmonic doubles the TP rate).
Block 3 (3.37) is harmonically rich and/or transient.

**Implication:** TP encoding on the **raw composite signal** is informative only for mono-tonal content, which a generic codec cannot assume. **The band-split idea is not optional — it's required.** Within a narrow band, the signal is closer to mono-tonal and TPs become meaningful. Without bands, TPs do not buy compression.

### H3 — Residual structure beyond LPC: PASS

LPC8 reduces sample entropy substantially (raw int16 ~12 bits → LPC8 residual ~7.5 bits hist ≈ ~9.5 bits int16-equivalent — a 2.5–3 bit reduction).

But the LPC8 residual is **not white**. Its autocorrelation at non-trivial lags (2..50 samples = ~45 µs to 1.1 ms) reaches:
- max\|R\| = **0.349** (block 1), **0.221** (block 2), **0.357** (block 3)
- mean\|R\| = 0.128, 0.077, 0.084

A residual with R(2..50) > 0.2–0.35 has exploitable structure. Standard Rice coding is optimal only for i.i.d. Laplacian residuals; here the residual is not i.i.d., so a longer-range predictor (or a trie capturing repeating residual patterns) can beat Rice on these blocks.

**Implication:** the codec's claim to add value beyond FLAC's (LPC + Rice) is **scientifically supported** — there's measurable structure LPC + Rice doesn't capture. Whether the trie specifically can capture it (as opposed to higher-order LPC, or a learned dictionary, or arithmetic coding with context modelling) is a separate question.

---

## What this changes about the codec design

The original design (from the discussion thread) had three implicit choices that the diagnostic invalidates or constrains:

1. ~~"Fixed universal basis"~~ → **per-block adaptive basis** (~5-12 frequencies signaled per ~100 ms block).
2. ~~"TP encoding on the raw signal"~~ → **band-split first, then per-band TP** (or per-band whatever-the-right-primitive-is).
3. ~~"Trie compresses residual"~~ → **plausible**, but the trie is one of several techniques that could exploit the LPC8-residual structure. Not unique to trie; the diagnostic does not establish that a trie is *better* than alternatives for this residual.

The shape of a viable codec, given these results:

```
input → frame (~100 ms blocks)
      → adaptive band decomposition (e.g., 8-32 bands)
      → per band:
            estimate K dominant frequencies (K small, 1-3)
            predict signal as sum of those (with phase + amplitude tracking)
            residual = actual - prediction
            entropy-code residual via [LPC + trie / arithmetic / ...]
      → multiplex band streams + metadata
      → output bitstream
```

This is closer to known transform codecs than the original sketch was. The novelty would be in (a) the prediction-as-prior-not-representation framing, and (b) the trie's role in residual compression. Both need separate experiments.

---

## What the diagnostic did NOT settle

- Whether a **trie** specifically (vs higher-order LPC, vs arithmetic coding) is the right tool for the residual structure. H3 passes for trie-or-equivalent; the diagnostic doesn't differentiate.
- Whether the conclusions hold on **other content** (speech, percussion, noise, electronic music). One sample, one set of three blocks. Block 3 already shows the assumptions stress.
- **Lossless integer arithmetic** constraints. The float-LPC residual measurements ignore quantization. A real codec needs fixed-point LPC and integer residuals.
- The **transient** question is not directly addressed. Block 3's high TP density and broad spectrum is *consistent with* transient content, but no direct transient detection was attempted.
- **Stereo / cross-channel** correlation is untested (we only used channel 0).

---

## Surprises

- **The strongest LPC residual structure is at the END of the sample (block 3, max\|R\| = 0.357), not in the most tonal block.** This is counter-intuitive — one might expect a tonal signal's LPC residual to be cleaner. The interpretation: block 3 has a mixture of components that LPC8 can only partially fit; what's left has more pattern structure than what's left after LPC fits a near-pure tone (block 1 had max\|R\| = 0.349 — close, but block 3's structure is distributed across more lags).
- **Block 3 has lower raw entropy (10.2 bits int16) than blocks 1 and 2 (~12 bits).** Despite being spectrally busier, block 3's amplitudes are more concentrated (likely lower overall volume / different musical passage). The relationship between "spectral spread" and "amplitude entropy" is not monotonic.
- **TP density on block 1 is already 1.21 × the pure-sine prediction**, not 1.0. Even the most tonal block has ~20% harmonic-driven extra TPs. A pure-sine TP encoding would lose this 20% as residual; the band-split version absorbs it into higher bands where it belongs.

---

## Plots

Saved to `results/plots_01/`:

1. `01_waveforms.png` — three blocks. Visual inspection: block 1 looks regular and periodic; block 3 looks denser / more chaotic.
2. `02_fft.png` — three FFT spectra. Block 1 has a clear peak; block 3 is much more spread.
3. `03_autocorr.png` — three autocorrelations. Block 1 is strongly periodic; block 3 less so.
4. `04_lpc_residual_autocorr.png` — LPC4 vs LPC8 residual autocorrelation per block. The non-trivial lags showing residual structure are visible here.

---

## Recommended next step

The diagnostic supports proceeding to a **mini-experiment 02**, but with the codec design updated per the H1/H2 findings:

> Take 1 second of the sample (one tonal region), apply a fixed band split (e.g., octave-spaced filterbank, 8 bands), measure within each band: (a) energy concentration, (b) TP regularity, (c) residual entropy after a per-band 1-3-frequency prediction. Verify that the per-band picture is meaningfully better than the composite picture from this diagnostic.

If experiment 02 shows per-band metrics significantly cleaner than composite, the codec architecture is on stable ground. If per-band metrics are still messy (e.g., bands still have spread spectra inside), the band-split idea has its own structural problem and the design needs another pass.
