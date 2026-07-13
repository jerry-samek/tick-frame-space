# Experiment 03 — Reversibility results

**Sample / region:** `data/FLAC_11_secs_Small_75d2275409.flac` channel 0, t=1.0..2.0s (same as Exp 02).
**Decomposition:** Daubechies-8 wavelet, 7 levels, periodization padding (`pywt.wavedec`).
**Reconstruction:** verified before any analysis.

---

## TL;DR

| Hypothesis | Verdict | One-line reason |
|---|---|---|
| **Reversibility** | **PASS** | max\|x − x_rec\| = 6.66e-16, rms = 1.21e-16. Wavelet decomposition is bit-lossless within float64 precision. |
| **H1'' — energy isolation survives** | **PASS** | W3 (cD5, 689-1378 Hz) holds **93.3%** of energy. W3+W4 together hold 98.9%. The lossless decomposition isolates the dominant content essentially as cleanly as Butterworth did (97.2% in B4). |
| **H2'' — TP regularity survives** | **PASS** | W3's TP_density / (2 × peak) = **0.90**. Six of eight sub-bands fall in [0.82, 1.01]. Per-band TP regularity is preserved under reversibility. |
| **H3'' — residual structure survives** | **FAIL** | W3 LPC8 residual max\|R\| = **0.142**. Criterion was ≥ 0.5. **The dramatic per-band residual autocorrelation in Exp 02 (max\|R\| = 0.94 in B4) was largely filter-induced**, not signal-induced. The trie has much less work to do than Exp 02 suggested. |

**This is a hard-but-clean finding.** The codec design's structural premises (band-split is the right move, TPs become useful per-band) survive the reversibility test. **The trie-on-residual claim does not.** Exp 02's H3' was an artifact of using a non-lossless filterbank.

---

## Reconstruction verification (the gating condition)

Before any analysis: did the wavelet decomposition perfectly reconstruct the input?

```
max |x - waverec(wavedec(x))|  =  6.66e-16
rms |x - waverec(wavedec(x))|  =  1.21e-16
```

That's machine epsilon (`2.22e-16`) × 3. **Reconstruction is bit-equivalent at float64 precision.** The decomposition is suitable for a near-lossless float codec. (For a true integer-lossless codec, the next step would be the integer 5/3 wavelet via lifting, e.g., `bior2.2` — out of scope here, but trivial to swap.)

---

## Numbers

| measurement | W0 cA7 (0-172) | W1 cD7 (172-345) | W2 cD6 (345-689) | **W3 cD5 (689-1378)** | W4 cD4 (1378-2756) | W5 cD3 (2756-5512) | W6 cD2 (5512-11025) | W7 cD1 (11025-22050) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| effective sample rate (Hz) | 345 | 345 | 689 | 1378 | 2756 | 5512 | 11025 | 22050 |
| n samples (coefficients) | 345 | 345 | 690 | 1379 | 2757 | 5513 | 11025 | 22050 |
| **energy_pct** | 0.0 | 0.0 | 0.8 | **93.3** | 5.6 | 0.2 | 0.0 | 0.0 |
| peak_freq_hz (coef domain) | 156 | 98 | 260 | 430 | 1061 | 2123 | 5234 | 9968 |
| top3_energy_pct (in coef FFT) | 10.7 | 19.1 | 19.2 | 18.6 | 18.1 | 4.0 | 2.0 | 0.8 |
| tp_density_hz (coef domain) | 242 | 195 | 471 | 774 | 2007 | 4278 | 8604 | 18288 |
| **tp_density / 2·peak** | 0.78 | 0.99 | 0.91 | **0.90** | 0.95 | 1.01 | 0.82 | 0.92 |
| raw_entropy_bits | 6.74 | 7.89 | 8.18 | 9.30 | 8.73 | 7.81 | 7.59 | 5.72 |
| lpc8_resid_entropy | 7.92 | 7.56 | 7.79 | 7.80 | 8.14 | 7.78 | 7.45 | 4.48 |
| **lpc8_resid_max\|R\|** | 0.410 | 0.162 | 0.163 | **0.142** | 0.274 | 0.247 | 0.093 | 0.059 |
| lpc8_resid_mean\|R\| | 0.051 | 0.062 | 0.052 | 0.052 | 0.083 | 0.076 | 0.035 | 0.021 |

W3 = the dominant sub-band (where the 1050 Hz tone lives). Bold column.

### Side-by-side comparison with Exp 02 (Butterworth)

Approximate frequency-range alignment between Butterworth bands (Exp 02) and wavelet sub-bands (Exp 03):

| Range (Hz) | Exp 02 Butterworth | Exp 03 Wavelet (db8) |
|---|---|---|
| 800-1600 (Butterworth) ↔ 689-1378 (Wavelet) | B4: energy 97.2%, TP/2·peak 1.06, max\|R\| **0.941** | W3: energy **93.3%**, TP/2·peak **0.90**, max\|R\| **0.142** |
| 1600-3200 ↔ 1378-2756 | B5: 1.1%, 1.05, 0.776 | W4: 5.6%, 0.95, 0.274 |
| 400-800 ↔ 345-689 | B3: 0.4%, 0.93, 0.974 | W2: 0.8%, 0.91, 0.163 |

**Energy isolation: comparable (93-97% in dominant band). TP regularity: comparable (~0.9-1.1).**
**Residual structure: dramatically different — Butterworth 0.94 vs Wavelet 0.14 in the dominant band.**

---

## Per-hypothesis verdict

### H1'' — energy isolation survives reversibility: PASS

W3 holds 93.3% of total energy (vs Butterworth B4's 97.2%). Slightly less sharp, but well within "the dominant content lives in one band." W3+W4 together hold 98.9%.

The wavelet decomposition is essentially as good as the (non-lossless) Butterworth filterbank at isolating the dominant tonal content. **The band-split architectural choice survives the move to lossless.**

### H2'' — TP regularity survives reversibility: PASS

W3's TP_density / (2 × peak) = 0.90 (Exp 02 B4 was 1.06). Both are within the H2' "near-pure-sine" criterion of [0.7, 1.5]. Six of eight sub-bands cluster in [0.82, 1.01].

The interpretation is slightly different: in Exp 02, the band signal was at full sample rate and the TP measurement was on the original time scale. In Exp 03, the wavelet coefficients are downsampled (effective sample rate = sr / 2^level), and the TP measurement is on the coefficient time series. Both yield "near-mono-tonal" results in the dominant band.

**Per-band TPs remain a meaningful primitive under reversibility.** This was the load-bearing finding for the original "TP encoding" idea, and it still holds.

### H3'' — residual structure survives reversibility: FAIL

This is the consequential finding. The criterion was: dominant sub-band's LPC8 residual max\|R\| at lags 2..50 ≥ 0.5.

W3's max\|R\| = **0.142**. That's not zero — there's still some autocorrelation — but it's far below the threshold and far below Exp 02's 0.94 in the analogous band.

**Interpretation:** Exp 02's huge residual autocorrelation was largely a property of the Butterworth filter's transfer function, not a property of the underlying signal. A bandpass-limited time-series has correlated values at lags related to the filter's center frequency; once the LPC fits the dominant tone, the residual still carries the filter's own structure.

When we use a reversible decomposition (wavelet), the per-band residual is much closer to white. The remaining structure (max\|R\| ≈ 0.14) is small enough that an LPC + Rice coder is almost optimal — the trie has very little additional compression to extract.

For comparison, the **composite signal's** LPC8 residual in Exp 01 had max\|R\| = 0.349 (block 1, tonal). That's substantially MORE structure than any wavelet sub-band here. **Splitting into bands actually reduces residual structure** — because narrower-band signals are more predictable, LPC fits them better, and the residual has less room for additional exploitation.

---

## What this changes about the codec design (cumulative)

After Exp 01: rejected fixed-universal-basis; accepted band-split; H3 pass on composite suggested trie-on-residual would help.

After Exp 02: H1'/H2' confirmed band-split idea. H3' apparent strong pass per-band — suggested trie is even more useful.

After Exp 03: **the H3' apparent strong pass was filter-induced**. Under a real lossless decomposition, per-band residuals are nearly white. The trie has very limited compression to add over (per-band LPC + Rice).

**The codec design as originally framed had the trie doing residual compression as its central novelty.** That central novelty is now in question. What remains:

- Band-split + per-band sinusoidal/LPC prediction can compress reasonably (typical lossless codec results: ~50% of raw bitrate, in the ballpark of FLAC).
- The trie might still play a role, but a different one — for example:
  - **Cross-band correlation:** transient onsets produce simultaneous coefficient patterns across many wavelet sub-bands. A trie could exploit this co-occurrence structure that single-band LPC cannot see.
  - **Long-range temporal patterns within a band:** repeated motifs across seconds of music. LPC8 only looks 8 samples back; a trie can recognize motifs across many windows.
  - **Stream filtering for incomplete signals:** the trie's original use case in v4-v9 was filtering / classification, not compression. Maybe the codec direction was the wrong application.

**Honest restatement of where the codec idea stands:**
- A lossless codec built on band-split + per-band LPC + Rice would be approximately FLAC. Not novel.
- Adding a trie does NOT obviously improve compression beyond that, on this sample's tonal content.
- If the trie is to add value, it must capture structure that LPC + Rice doesn't — and Exp 03 shows that structure isn't simply "residual autocorrelation per band."
- **The codec idea may be misapplying the trie.** Worth stepping back to ask what the trie's strength actually is, vs. what audio compression needs.

---

## What this experiment did NOT settle

- **Cross-band / cross-time structure**, where the trie's pattern-learning might genuinely beat LPC + Rice. Not measured here.
- **Whether non-tonal content (Exp 01's 9.5s region) would show different residual structure** under wavelet decomposition. Possibly the residual is whiter still on transients (LPC handles them poorly, but wavelets handle them well).
- **Other wavelets / decomposition choices.** Only db8 tested. A different wavelet might leave more residual structure (e.g., a less smooth wavelet might leave more time-domain artifacts, which the trie could potentially exploit).
- **Integer-lossless reversibility.** Float reconstruction is essentially perfect (6.66e-16 error). Integer-exact lossless requires a different scheme (5/3 wavelet via lifting). Not tested but trivial swap.
- **Whether the codec, even without a strong trie role, would be competitive with FLAC on this content.** Direct comparison not run.

---

## Surprises

1. **W3's coefficient-domain peak frequency is 430 Hz, not 1050 Hz.** This is the wavelet detail's downsampling effect: the original 1050 Hz tone, after band-pass and downsample-by-32 (effective sr = 1378), gets baseband-shifted into the 0..689 Hz range of the coefficient time series. Confusing at first, but consistent with how DWT works. Future plots / diagnostics should be careful when interpreting "peak frequency in a wavelet sub-band."

2. **W7 (cD1, 11025-22050 Hz, mostly noise) has the lowest LPC residual entropy (4.48 bits).** This is because the band has very little energy and its coefficients have low variance. Low-variance signals quantize to fewer distinct values per histogram bin, which compresses well. Doesn't mean W7 is more compressible in an absolute sense — it means the band carries almost no information.

3. **The biggest residual autocorrelation is in W0 (cA7, 0-172 Hz) at max\|R\| = 0.41.** This band has 0.0% of total energy — it's essentially all numerical noise from the wavelet's edge effects. The "structure" is the wavelet's own residual at the lowest band. Not informative for the codec.

4. **W4 (cD4, 1378-2756 Hz) has 5.6% of energy and the largest LPC residual structure of any energy-carrying band (max\|R\| = 0.274).** This is likely the second harmonic of the dominant tone (2× 1050 ≈ 2100 Hz, which falls in this band). Harmonics are partly correlated to the fundamental, and a per-band LPC can't see that — it would require cross-band modeling. **This hints at where the trie might still add value: capturing cross-band harmonic structure.**

---

## Plots

`results/plots_03/`:

1. `01_wavelet_subbands.png` — eight stacked subplots showing each wavelet coefficient array. Note the differing lengths (downsampling per level). W3 is the visibly active one.
2. `02_wavelet_band_ffts.png` — FFT of each sub-band's coefficients, plotted at the sub-band's effective sample rate.

(LPC residual autocorrelation plot omitted this round — the per-band residuals are too close to white to show striking patterns.)

---

## Recommended next step

The honest scientific move is **not** another diagnostic experiment along the same axis. Three diagnostics in, the picture is:

- Codec architecture (band-split + per-band prediction) is sound and survives reversibility. ✓
- TP encoding has a clean per-band primitive. ✓
- The trie's role as residual compressor is **not supported**. ✗

The natural next step depends on what you want from the codec:

1. **If the goal is "build a lossless codec":** drop the trie, go with band-split + per-band LPC + Rice. You'd be reproducing FLAC's general architecture. Probably 95% of FLAC's compression with simpler code. Pragmatic but not novel.

2. **If the goal is "find a use for the trie in audio":** stop chasing residual compression. The trie's strength is **pattern learning across sequences** — its original v4-v9 application was filtering / classification of token streams. Reframe: what audio problem looks like *that*? Possibly: musical pattern recognition, speech feature extraction, motif detection in music — not compression.

3. **If the goal is "test the trie's role in cross-band / cross-time structure":** design Exp 04 around that specifically. Measure cross-sub-band correlation in wavelet space, see whether harmonics produce co-occurring patterns that a trie could exploit. This is the single thing the diagnostics so far have NOT ruled out.

I'd suggest pausing the codec direction and having a conversation about which of these three is the actual goal. The diagnostics have done their job — they've factored the design and identified that the original "trie compresses residual" framing isn't supported. Continuing without re-deciding the goal would be running on assumptions the data has already weakened.
