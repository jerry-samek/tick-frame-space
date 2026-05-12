# Experiment 03 — Reversibility: do per-band metrics survive a lossless decomposition?

**Status:** description (not yet implemented).
**Sample / region:** same as Exp 02 — `data/FLAC_11_secs_Small_75d2275409.flac` channel 0, t=1.0..2.0s.
**Estimated work:** ~80 lines Python (pywt + reuse Exp 02 measurement functions), ~1 min wall time.

---

## Why this experiment exists

Exp 02 used Butterworth bandpasses (zero-phase via `sosfiltfilt`) for the band split. **That filterbank is not lossless** — the forward+backward filtering loses bits. A lossless codec cannot use it.

Exp 02's verdicts for the codec design rest on per-band metrics. Specifically:
- H2' STRONG PASS: per-band TP_density / (2 × peak) ≈ 1.0 in the dominant band.
- H3' PASS with caveat: per-band LPC residual has high autocorrelation, possibly partly filter-induced.

If those metrics depend on the Butterworth filter's specific properties, they may not survive on a lossless decomposition. That would invalidate the codec design at this layer.

This experiment substitutes a **reversible wavelet decomposition** (pywt) for the Butterworth filterbank and re-measures the same hypotheses. Only metrics that survive the move to lossless are real.

---

## Question

Do the per-band findings of Exp 02 (H1'/H2' band-isolation, H2' TP regularity, H3' residual structure) hold under a reversible wavelet decomposition?

---

## Method

### Reversibility verification (preflight)

Before any analysis, verify that the chosen decomposition perfectly reconstructs the input. This is a **gating condition** — if reconstruction error is larger than floating-point epsilon, the decomposition is not suitable for a lossless codec and the experiment is a non-starter.

- Compute `coeffs = pywt.wavedec(x, wavelet='db8', level=7, mode='periodization')`.
- Reconstruct: `x_rec = pywt.waverec(coeffs, wavelet='db8', mode='periodization')`.
- Measure `max |x - x_rec|`. Pass condition: < 1e-10 (floating-point near-zero).

If pass: proceed. If fail: change wavelet (try db4, sym4, bior2.2 = "5/3 reversible") or change padding mode.

### Decomposition

Use **Daubechies-8 (`db8`)** as the default wavelet and **7-level decomposition** to get 8 sub-bands at 44.1 kHz:

| Band | Wavelet output | Approximate freq range (Hz) | Sample rate (effective) |
|---|---|---|---|
| W0 (approx) | cA7 | 0 – 172 | 344.5 |
| W1 | cD7 | 172 – 344 | 689 |
| W2 | cD6 | 344 – 689 | 1378 |
| W3 | cD5 | 689 – 1378 | 2756 |
| W4 | cD4 | 1378 – 2756 | 5512 |
| W5 | cD3 | 2756 – 5512 | 11025 |
| W6 | cD2 | 5512 – 11025 | 22050 |
| W7 | cD1 | 11025 – 22050 | 44100 |

Each wavelet sub-band has its own effective sample rate (downsampled). This is a structural difference from Exp 02's filterbank (which kept all bands at 44.1 kHz).

**Important consequence:** TP density measured on a wavelet sub-band must be interpreted at the sub-band's effective sample rate, not at the original 44.1 kHz. This is built into the comparison.

### Why db8 / 7 levels

- `db8` is a smooth wavelet with reasonable frequency selectivity. Common choice for audio.
- 7 levels gives 8 sub-bands, matching Exp 02's 8-band split for direct comparison.
- `mode='periodization'` keeps coefficient arrays compact and well-defined for fixed-length signals.

If results are murky, fallback wavelets to try: **`bior2.2`** (the "5/3" wavelet — *bit-reversible* via lifting; used in JPEG2000 lossless mode), **`sym8`** (similar to db8 but more symmetric, less phase distortion), **`coif3`**.

### Measurements per sub-band

Same metrics as Exp 02, computed on each wavelet coefficient array, with the sub-band's effective sample rate used for any frequency-derived measurement:

1. Energy as % of total signal energy (sum of squared coefficients vs sum of squared raw samples).
2. Peak frequency in the sub-band's FFT (interpreted at effective sample rate).
3. Top-3 / top-10 bin energy concentration within the sub-band.
4. TP count and density (at effective sample rate).
5. TP_density / (2 × peak) — the H2' diagnostic.
6. Raw / delta entropy.
7. LPC8 residual entropy (still LPC-order=8; sub-band may need lower order, but keep consistent for comparability).
8. LPC8 residual autocorrelation max\|R\| at lags 2..50 — the H3' diagnostic.

Compare each sub-band W_i to the corresponding Butterworth band B_i from Exp 02 by approximate frequency range alignment.

### Hypotheses (refined)

- **H1'' — Energy isolation survives reversibility.** The wavelet sub-band corresponding to the dominant Butterworth band (B4: 800-1600 Hz) holds approximately the same fraction of total energy. Predict W3 (~689-1378 Hz) and W4 (~1378-2756 Hz) together hold > 90% of energy.

- **H2'' — TP regularity survives reversibility.** For sub-bands carrying ≥1% of energy, TP_density / (2 × peak) is in [0.7, 1.5] when measured at the sub-band's effective sample rate.

- **H3'' — Residual structure survives reversibility.** LPC8 residual on the dominant sub-band has max\|R\| at lags 2..50 of at least 0.5. (Lower bound chosen below Exp 02's 0.94 to allow for the structural difference between wavelet and Butterworth filtering, while still establishing meaningful structure.)

---

## Decision rules

| Outcome pattern | Conclusion |
|---|---|
| Reconstruction passes; H1'', H2'', H3'' all pass | Reversible decomposition supports the codec design. Architecture is on solid lossless ground. Proceed with codec implementation. |
| Reconstruction passes; H1'' passes; H2'' fails (TP ratio off) | Wavelet sub-bands don't expose TP regularity the way Butterworth did. Either accept this and drop TP encoding, or try a different wavelet (e.g., a wavelet better matched to sinusoidal content). |
| Reconstruction passes; H3'' fails (max\|R\| < 0.5 per band) | Exp 02's high residual autocorrelation was filter-induced, not signal-induced. Trie-on-residual loses one of its motivations; codec compression has to come from prediction, not residual structure. Re-evaluate trie's role. |
| Reconstruction passes; H1'' fails (energy not isolated to one or two sub-bands) | Wavelet decomposition doesn't isolate the signal's content the way octave bandpasses did. May need a non-octave wavelet packet decomposition, or a different decomposition entirely (MDCT). |
| Reconstruction fails | Pywt+chosen wavelet is not lossless at this precision. Try `bior2.2` (integer-reversible 5/3 wavelet), or use float64 throughout and accept tiny rounding (~1e-15). |

---

## What this experiment does NOT decide

- **Which wavelet is best for the codec.** This experiment uses one or two wavelets diagnostically.
- **Whether the conclusions hold on non-tonal content** (Exp 01's 9.5s region was not band-split in either Exp 02 or this experiment).
- **Whether per-band TP encoding actually compresses.** That's still the open question downstream of these diagnostics.
- **Cross-band correlation in the wavelet domain.** Wavelet sub-bands of a transient often correlate in time (a piano hit produces simultaneous coefficients in many sub-bands). The codec might want to exploit this. Out of scope here.

---

## Output

`results_03.md` with:
- Reconstruction error verification (pass/fail).
- Per-sub-band table of metrics.
- Side-by-side comparison with Exp 02's Butterworth bands (by approximate frequency range).
- Verdict per H1''/H2''/H3''.
- Honest caveats about wavelet-specific structure that may differ from Butterworth.

---

## Estimated effort

~80 lines Python. Reuse measurement functions from Exp 02. Single run.
