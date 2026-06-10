# Experiment 04 — Cross-band correlation in wavelet space

**Status:** designed 2026-06-10. The one question v11's closure left open (SUMMARY.md §"Untested").
**Framing:** NOT a codec experiment. A self-contained scientific question about harmonic structure:

> Do wavelet sub-bands carrying a fundamental (W3) and its 2nd harmonic (W4) share
> statistical dependency that (a) exists beyond chance, (b) survives per-band LPC,
> and (c) is exploitable by a trie/context model — measured honestly on held-out data?

The motivating datum: Exp 03 found W4's LPC8 residual max|R| = 0.274, *higher* than the
dominant band W3's 0.142, and W4 contains the 2nd harmonic of W3's 1050 Hz tone.
Per-band LPC structurally cannot see cross-band dependency.

---

## Related work (scientist pass, 2026-06-10)

Searched before designing. Three findings shaped this design:

1. **Wavelet hidden Markov trees** (Crouse/Nowak/Baraniuk lineage) model exactly this:
   cross-scale dependencies of wavelet coefficients in natural signals. Their key
   empirical claim: the dependency is in **magnitudes/variances** ("persistence of
   large coefficients across scales"), largely invisible to signed second-order
   statistics. → H1/H2 below measure magnitude correlation and mutual information,
   not just Pearson r.
2. **Zerotree coders (EZW/SPIHT)** exploit cross-band *magnitude* correlation while
   largely ignoring within-band correlation — the mirror image of per-band LPC. The
   *phenomenon* of exploitable cross-band dependency is therefore well precedented
   (in images, lossy). The narrow open question here is whether it survives per-band
   LPC on tonal *audio* and how many bits/coef it is worth.
3. **Context-tree weighting / PPM**: a trie on co-occurrences is a context model.
   The CTW literature's built-in trap: H(target | context) ≤ H(target) *always*
   in-sample, with equality iff independent. Any in-sample measurement will show
   "savings". → H3 is evaluated exclusively on **held-out** data, with config
   selection on a separate validation split.

Sources: wavelet-HMT survey hits via arxiv/ResearchGate (Crouse et al. lineage);
[EZW — Wikipedia](https://en.wikipedia.org/wiki/Embedded_zerotrees_of_wavelet_transforms);
[CTW — Wikipedia](https://en.wikipedia.org/wiki/Context_tree_weighting) (Willems,
Shtarkov & Tjalkens 1995).

Honesty note up front: even a full PASS has bounded codec impact — W4 carries 5.6% of
signal energy. The value of this experiment is the scientific answer, not a codec revival.

---

## Setup (identical to Exp 03 where possible, for comparability)

- Sample: `data/FLAC_11_secs_Small_75d2275409.flac`, channel 0, t = 1.0..2.0 s.
- Decomposition: db8, 7 levels, periodization (`pywt.wavedec`).
- Bands: **W3 = cD5** (689–1378 Hz, n=1379, fundamental ~1050 Hz),
  **W4 = cD4** (1378–2756 Hz, n=2757, 2nd harmonic ~2100 Hz).
- Alignment: zerotree parent-child — W3[k] ↔ (W4[2k], W4[2k+1]). Because db8 has
  group delay, the optimal alignment offset may not be 0: a small offset scan
  (W4 index shift −8..+8) is performed **on the train split only**, maximizing
  magnitude correlation; the chosen offset is then frozen for everything else.
- Splits (time-ordered, no shuffling): **train 50% / validation 20% / test 30%**
  of the aligned pair sequence.

## Hypotheses and pre-registered criteria

### H1 — raw cross-band dependency exists
On aligned (W3[k], W4-children) pairs, compute:
- signed Pearson r (expected ≈ 0 per HMT literature; reported, not gating),
- magnitude correlation r(|W3|, |W4|),
- mutual information I(qW3; qW4) with 16-bin quantization.

Null model: **200 circular-shift surrogates** (shift W4 sequence by random offsets
≥ 32 positions; preserves both marginals and within-band autocorrelation, destroys
cross-band alignment).

**PASS:** MI exceeds the 99th percentile of the surrogate null. (Magnitude r reported
alongside; MI is the gating statistic because it catches non-monotone dependency.)

### H2 — dependency survives per-band LPC
Same three measures + same surrogate test, computed on **per-band LPC8 residuals**
(LPC fit per band on the full region, as in Exp 03).

**PASS:** MI on residuals exceeds the 99th percentile of its surrogate null.

### H3 — dependency is exploitable by a cross-band context model (the trie test)
Quantize residuals per band: normalize by train-split σ, uniform 16-bin quantizer on
[−4σ, +4σ] (tails clipped). Context symbols may be coarsened (4/8/16 levels — grid).
Count-based trie with Laplace smoothing predicts the next W4 residual symbol.

Models:
- **M0** — order-0 marginal.
- **M1** — temporal context: previous W4 symbol(s) (within-band, what LPC+entropy
  coding can already reach).
- **M2** — cross-band context only: aligned W3 parent symbol(s).
- **M3** — combined: temporal + cross-band.

Config (context depth, context coarseness) selected by **validation** cross-entropy;
the single selected config per model is then evaluated **once on test**.

**PASS:** test cross-entropy(M3) ≤ test cross-entropy(M1) − **0.10 bits/symbol**.
**Sanity control:** the same M3 pipeline run on a shift-surrogate must show
< 0.05 bits/symbol advantage over M1 (guards against quantizer/smoothing artifacts).

### Interpretation matrix (pre-registered)
| Outcome | Conclusion |
|---|---|
| H1 fail | No cross-band dependency even raw. Direction closes; v11 closure stands fully. |
| H1 pass, H2 fail | Dependency exists but per-band LPC absorbs it. Trie has nothing left. Close. |
| H2 pass, H3 fail | Dependency survives LPC but our context model can't exploit it at this data size. Report honestly; distinguish "not exploitable" from "n too small" via the train-curve. |
| All pass | Cross-band structure is real and trie-exploitable. Quantify bits/coef; relate to zerotree/HMT precedent; decide separately whether any application follows. |

## Deliverables
- `diagnostic_04.py` — implementation.
- `results/diagnostic_04_summary.json`, `results/plots_04/`.
- `results_04.md` — per-hypothesis verdicts (skeptic pass before writing).
