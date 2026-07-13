# Experiment 02 — Band-split diagnostic

**Status:** description (not yet implemented).
**Sample:** `data/FLAC_11_secs_Small_75d2275409.flac`, channel 0, **1 second from t=1.0 to t=2.0** (the tonal region — block 1 from Exp 01 was the cleanest H1 case).
**Estimated work:** ~80 lines Python, ~1 min wall time.

---

## Why this experiment exists

Experiment 01 produced two PARTIAL verdicts (H1, H2) that pointed to band decomposition as the structural fix:

- H1 partial: top-3 energy = 91% on tonal block, 12% on busy block. A single fixed basis can't span both.
- H2 partial: TP_density / (2 × peak) ranged 1.21 → 3.37. TPs reflect the dominant component only on near-mono-tonal content.

The proposed fix in both cases: split the signal into bands first, then run the per-band analysis where the in-band signal is much closer to mono-tonal.

This experiment tests **whether the band-split actually delivers that cleanup** on the easiest-case content (tonal region). If it doesn't help even here, the architectural commitment to band decomposition is not justified.

---

## Question

Is the per-band picture meaningfully cleaner than the composite-signal picture, on a tonal 1-second region?

Operationalised: for each of 8 octave-spaced bands, compute the same metrics as Exp 01, and compare against the composite-signal metrics on the same 1-second region.

---

## Hypotheses

### H1' — Per-band energy concentration

**Claim:** for each band that contains meaningful energy (≥1% of total signal energy), the in-band top-3 frequency bins hold ≥80% of in-band energy.

**Predicts true:** the band signal is near-tonal, so a 1-3-frequency prior captures it.
**Predicts false:** band-internal energy is broad — bands contain too many components.

### H2' — Per-band TP regularity

**Claim:** for each meaningful band, TP_density / (2 × in-band-peak-freq) is in [0.7, 1.5] — i.e., the band's TPs reflect the band's dominant frequency cleanly.

**Predicts true:** within a narrower frequency range, TPs match the dominant in-band component.
**Predicts false:** TPs in a band still don't reflect the band's peak — interpretation is unclear (filter ringing? multiple in-band components?).

### H3' — Per-band residual structure

**Claim:** in each meaningful band, the LPC residual still has measurable autocorrelation at lags 2..50 (max\|R\| ≥ 0.15).

**Predicts true:** structure remains in the band-residual that something beyond LPC could exploit.
**Predicts false:** band-residual is essentially white. Per-band, LPC + Rice is already optimal.

(Aside: H3 already passed in Exp 01 on the composite. H3' tests whether per-band LPC residuals retain enough structure to motivate per-band trie compression. If H3' fails on most bands, the trie should operate **across** bands rather than within them.)

---

## Method

### Band split

Use 8 octave-spaced bandpass filters (Butterworth, order 4, applied via `sosfiltfilt` for zero-phase response):

| Band | Range (Hz) |
|---|---|
| B0 | 25 – 100 |
| B1 | 100 – 200 |
| B2 | 200 – 400 |
| B3 | 400 – 800 |
| B4 | 800 – 1600 |
| B5 | 1600 – 3200 |
| B6 | 3200 – 6400 |
| B7 | 6400 – 22050 (lowpass at Nyquist) |

The 1.0–2.0 s region's peak frequency was 1050 Hz (Exp 01), so most of the energy will land in B4 (800–1600 Hz), with harmonics at B5, B6.

**Note: this filterbank is NOT lossless** (zero-phase IIR filters). For diagnostic purposes we only care about whether per-band signals expose cleaner structure — a real codec would need a reversible decomposition (QMF, wavelet, or MDCT). Out of scope here.

### Measurements per band

Same as Exp 01, on each band's filtered signal:

1. In-band energy as % of total signal energy (which bands actually carry the signal?)
2. In-band peak frequency
3. In-band top-3 / top-10 / top-50 energy concentration (H1')
4. In-band TP count and density (H2' numerator)
5. In-band TP_density / (2 × in-band peak) (H2')
6. In-band raw / delta entropy
7. In-band LPC8 residual entropy (H3' floor)
8. In-band LPC8 residual autocorrelation max\|R\| at lags 2..50 (H3')

Plus: composite-signal version of the same metrics on the unfiltered 1-second region for direct comparison.

---

## Decision rules

| Outcome pattern | Conclusion |
|---|---|
| H1', H2', H3' all pass on the bands carrying ≥80% of energy | Band-split is the right architectural move. Build a per-band predictor. |
| H1' passes per-band but H2' fails (TP ratio still off) | TPs are the wrong primitive even per-band. Drop TP encoding; keep band-split + LPC + trie. |
| H1' passes per-band AND H2' passes per-band but H3' fails | Per-band signals ARE near-mono-tonal but the LPC residual is white. Codec compression comes from prediction, not from trie-on-residual. Trie should operate cross-band or across time, not within a band's residual. |
| H1' fails per-band (energy still spread within bands) | 8 octaves isn't fine enough. Need finer bands (third-octave?). Or the signal's structure isn't octave-aligned. |
| H1', H2' barely improve over composite | The band-split is not the structural fix it was hypothesised to be. Need a different decomposition. |

---

## What this experiment does NOT decide

- **Reversibility of the band split.** This filterbank is not lossless. A real codec needs QMF, wavelet, or MDCT. Out of scope.
- **Whether 8 octaves is the right granularity.** Only one granularity tested.
- **Whether the conclusions hold on non-tonal content.** Block 3 from Exp 01 (busy/transient) is not analysed here — that's a follow-up.
- **Whether the trie specifically can compress the residual.** Only autocorrelation is measured; trie compression would be a separate experiment.

---

## Output

`results_02.md` with:
- Per-band table of the 7 metrics + composite for comparison.
- Plots: per-band waveforms, per-band FFTs, per-band LPC residual autocorrelations.
- Verdict per hypothesis (H1', H2', H3') with evidence cited.
- Surprises / unexpected band behaviours.

---

## Estimated effort

~80 lines Python (scipy.signal.butter + sosfiltfilt + reuse Exp 01 measurement functions). Single run, ~1 minute wall time.
