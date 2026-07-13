# Experiment 01 — Diagnostic: does the 11-sec sample have the structure our codec design assumes?

**Status:** description (not yet implemented).
**Sample:** `data/FLAC_11_secs_Small_75d2275409.flac`
**Estimated work:** ~50 lines Python (soundfile + numpy + matplotlib), ~5 min wall time.

---

## Why this experiment exists

The codec design under discussion rests on **three layered assumptions**. Before implementing any codec, we want to know whether the assumptions hold on a real signal:

1. **Energy concentration assumption** — a small number of dominant frequencies hold most of the signal's energy. Justifies the "given frequencies" prior (the prediction model).
2. **Turning-point informativeness assumption** — for tonal content, the spacing between TPs reflects the dominant frequency cleanly enough to be a useful primitive. Justifies TP encoding.
3. **Residual structure assumption** — after subtracting a frequency-prior or TP-based prediction, the residual has hierarchical/repeating structure beyond what a static entropy coder (Rice, Huffman) could capture. Justifies the trie.

Each can fail independently. If we skip this and run a full codec implementation that assumes all three hold on a signal where one or two don't, we'd produce poor compression numbers without learning *why*. This experiment factors the assumptions so each can be falsified cheaply.

It is **not** a codec experiment. It is **diagnostic** — a single read of one signal to update our design priors.

---

## Question

Does the 11-sec FLAC sample exhibit each of the three structural properties the codec design assumes? Pass / fail / partial for each, with quantitative evidence.

---

## Hypotheses and predictions

### H1 — Energy concentration

**Claim:** in any 100 ms block, the top-K spectral bins (for some small K, ~3–10) hold most of the energy.

**Predictions if true:**
- Top-3 bins: >50% of total energy.
- Top-10 bins: >80%.
- Spectrum has clear peaks rather than being broadband.

**Predictions if false:**
- Energy spread roughly uniformly across the spectrum (broadband / noisy content).
- No clear peaks; flat-ish FFT magnitude.

**What "false" implies:** the "given frequencies" prior buys little. The codec's compression has to come from elsewhere (likely LPC or wavelet decomposition).

### H2 — TP informativeness

**Claim:** the count of turning points per second is close to 2× the dominant frequency, suggesting TPs reflect the dominant component rather than being dominated by noise/harmonics.

**Predictions if true:**
- TP density / (2 × peak FFT frequency) is between 0.7 and 1.5.
- TP spacing distribution is concentrated (not uniform).

**Predictions if false:**
- TP density much higher than 2× the dominant freq (means TPs are noise-driven).
- TP spacing distribution is broad / random.

**What "false" implies:** TPs are not the right primitive at the composite-signal level. The TP encoding might still work *per band* after decomposition, but the simple version (TPs on the raw signal) doesn't.

### H3 — Residual structure beyond static entropy coding

**Claim:** an LPC-style predictor leaves a residual whose entropy is significantly lower than raw-sample entropy, *but* the residual still contains pattern structure (autocorrelation, repeating sequences) that a trie could exploit beyond what Rice coding alone would.

This is the trickiest to diagnose without actually building the trie. We approximate it with two measurements:

**Predictions if true:**
- LPC residual entropy ≪ raw-sample entropy (signal is at least somewhat predictable).
- LPC residual still has measurable autocorrelation at lags > 1 (residual has structure beyond first-order Markov).

**Predictions if false:**
- LPC residual entropy ≈ raw entropy (signal isn't predictable at all — unlikely for real audio).
- LPC residual is essentially white noise (no autocorrelation at any lag) — entropy coding alone is optimal, no role for the trie.

**What "false" implies:** depends on which way it falls. If signal is unpredictable, no codec helps much (probably means the sample is unusual). If LPC residual is white, the trie buys nothing over standard Rice coding — the codec architecture has no scientific justification beyond LPC + Rice (which is what FLAC already does).

---

## Measurements

For one representative 100 ms block (4410 samples at 44.1 kHz, mono — pick channel 0 of the FLAC):

| # | Measurement | Purpose |
|---|---|---|
| 1 | Plot of the 4410 samples (waveform) | Visual sanity. Is it tonal, transient, noisy? |
| 2 | FFT magnitude spectrum | Where's the energy? |
| 3 | Energy concentration: % in top 3 / 10 / 50 / 100 / all bins | Quantifies H1. |
| 4 | Number of zero-crossings (proxy for TP count of a centered signal) AND number of true TPs (sign-change of first difference) | Quantifies H2 numerator. |
| 5 | Peak FFT frequency (bin with highest magnitude after DC removal) | Quantifies H2 denominator. |
| 6 | Autocorrelation function plot, especially around the predicted lag = 1 / peak_freq | Independent check that the signal is periodic at the FFT-claimed frequency. |
| 7 | Shannon entropy of the raw 16-bit (or 24-bit) sample values | Raw baseline (bits/sample). |
| 8 | Shannon entropy of first differences | Does naive delta encoding reduce entropy? |
| 9 | LPC residual entropy (4th- or 8th-order LPC fit on the block, residual = raw − predicted) | The floor any frequency-prior + trie codec must beat to be meaningful. |
| 10 | Autocorrelation of the LPC residual at lags 2..50 | Does residual have structure beyond what LPC captured (i.e., room for trie)? |

Run on **3 different 100 ms blocks** within the 11-sec sample (start, middle, end), to check whether the signal's structure is consistent or block-dependent.

---

## Decision rules (what we conclude from the numbers)

| Pattern of results | What we conclude | Next step |
|---|---|---|
| H1, H2, H3 all pass | Codec design rests on real structure. Proceed to mini-experiment 02. | Implement frequency-prior + TP encoding, measure compression vs FLAC. |
| H1 passes, H2 fails, H3 passes | Frequency prior is real but TP encoding isn't the right primitive at this level. | Drop TP, keep frequency-prior + LPC + trie. |
| H1 passes, H2 partial (clean per-band), H3 passes | Confirms band-split + per-band TP idea. | Add band decomposition before TP encoding. |
| H1 fails | Sample isn't tonal (or this codec target is non-tonal content). | Either pick a different signal class, or rethink whether frequency-prior is the right approach for this corpus. |
| H3's "residual beyond LPC has no structure" | The trie has no work to do beyond entropy coding. | The codec's claim to be more than (LPC + Rice) — i.e., FLAC — has no support. Don't build a clone of FLAC; the design needs a different angle. |

---

## What this experiment does NOT decide

- Whether the codec, once built, is faster or slower than FLAC.
- Whether the codec is competitive on **diverse** content (this is one sample, likely tonal music — explicitly limited).
- Whether the trie can actually learn the residual structure (that's a separate experiment after we commit to an architecture).
- Anything about lossless integer arithmetic constraints — that's an implementation question, not a structural one.

---

## Open design questions before running

1. **Block size.** 100 ms (4410 samples) is a guess. Smaller blocks → more transient sensitivity but worse FFT resolution. Larger → vice versa. Worth running at 50 ms, 100 ms, 200 ms and seeing if the diagnostic conclusions are stable.
2. **Mono vs stereo.** Most codecs treat channels independently or use mid/side. For diagnostic, picking channel 0 only is fine. Stereo correlation is a separate axis.
3. **LPC order.** 4th order is small and fast; 8th order captures more. Try both, see which gives lower residual entropy.
4. **What counts as "low entropy"?** Need a baseline. Options:
   - Raw 16-bit sample entropy (probably ~13–14 bits/sample for music — not 16 because of correlation).
   - Theoretical entropy of i.i.d. samples drawn from the sample's amplitude distribution.
   - FLAC's own residual entropy on the same block (need to look inside a FLAC frame to extract).

---

## Output

A short report (`results_01.md`) with:
- The 9 numbers (or a small table) per block × 3 blocks.
- 4 plots saved as PNGs: waveform, FFT spectrum, autocorrelation, residual autocorrelation.
- Verdict per hypothesis: pass / partial / fail, with one-line justification.
- Any surprises that didn't fit the hypotheses.

The report should fit on one screen. The plots should be inspectable as images.

---

## Estimated effort

~50 lines of Python (soundfile, numpy, scipy.signal for LPC, matplotlib). Single sitting, ~30 min including writing the report. No persistent infrastructure.