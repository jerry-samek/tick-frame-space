# Predictions from the Tick-Frame Substrate vs. Pattern Model

**Original source**: https://copilot.microsoft.com/shares/nCry94EuKhKZJU3LMRnuV
**Date**: January 2026
**Status**: Theoretical prediction - observational test proposal

---

## Core Hypothesis

Measured light speed is an effective propagation speed of a wiggling, structured EM pattern. Substrate causal speed ($c_{\text{sub}}$) is the geometric step limit of the underlying tick-frame substrate and can be slightly larger than the measured speed. The fractional slowdown of the EM pattern is $\delta = 1 - v_{\text{em}}/c_{\text{sub}}$. For small $\delta$ the time delay scales linearly with distance:

$$
\Delta t \approx \frac{D}{c} \cdot \delta
$$

---

## Quantitative Examples (Selected Cases)

| Distance | $D / c$ (s) | $\Delta t$ ($\delta = 10^{-12}$) | $\Delta t$ ($\delta = 10^{-9}$) | Interpretation |
|----------|-------------|----------------------------------|--------------------------------|----------------|
| 1 kpc | $1.03 \times 10^{11}$ s | 0.10 s | 103 s | Galactic pulsar / transient: sub-s to minutes |
| 1 Mpc | $1.03 \times 10^{14}$ s | 102 s | $1.03 \times 10^5$ s (~1.2 day) | Nearby galaxy: minutes to days |
| 100 Mpc | $1.03 \times 10^{16}$ s | $1.03 \times 10^4$ s (~2.9 h) | $1.03 \times 10^7$ s (~119 days) | Cosmological transient: hours to months |

---

## Comparison with Typical Interstellar Dispersion Delays

| DM (pc/cm³) | Freq pair (MHz) | Dispersion $\Delta t$ (s) |
|-------------|-----------------|---------------------------|
| 10 | 1400 – 5000 | $1.95 \times 10^{-5}$ s (0.0195 ms) |
| 100 | 1400 – 5000 | $1.95 \times 10^{-4}$ s (0.195 ms) |
| 100 | 400 – 1400 | $2.38 \times 10^{-3}$ s (2.38 ms) |
| 1000 | 400 – 1400 | $2.38 \times 10^{-2}$ s (23.8 ms) |

**Takeaway**: ISM dispersion in GHz bands typically produces ms-scale delays for moderate DM. A substrate-pattern delay with $\delta \sim 10^{-12}$ at kpc distances can be $\sim 0.1$ s, larger than GHz dispersion but smaller than low-frequency or very high-DM delays.

---

## Observable Signatures and Experimental Strategy

### Observable Signatures

1. **Distance scaling**: measured $\Delta t$ grows linearly with distance after removing known effects, with $\Delta t/(D/c) \approx \delta$.

2. **Non-$\nu^{-2}$ residuals**: EM arrival delays that do not follow standard dispersion law after careful DM/scattering correction.

3. **GW vs EM timing**: causal (substrate) waveforms arriving earlier than EM impulses, after accounting for propagation effects.

4. **Best targets**: short, bright impulses with clean lines of sight (low DM), or non-radio impulses (X/$\gamma$) where electron dispersion is irrelevant.

### Practical Experiment Design

1. **Formalize prediction**: produce $\Delta t(\delta, D, \text{pattern width})$ curves.

2. **Simulate end-to-end**: source → ISM/IGM → instrument, include DM variability, scattering, lensing, and instrument latencies.

3. **Pilot observations**: coordinated wideband campaigns on low-DM pulsars and short transients (FRB/GRB) with precise timing and independent clocks.

4. **Calibration**: atomic/GPS time standards, end-to-end latency budgets, continuous DM monitoring.

5. **Statistical test**: Bayesian model comparison (standard vs substrate-pattern) across multiple events; require pre-defined decision thresholds.

---

## Practical Assessment and Conclusion

**Detectability window**: with favorable geometry and low ISM contamination, $\delta \gtrsim 10^{-12}$ can produce sub-second to minute delays at galactic distances and is potentially detectable with current instruments.

**Main obstacles**: ISM/IGM dispersion and scattering, lensing/wave-optics effects, and instrument systematics can mask tiny delays; success requires luck (clean LOS) plus rigorous methodology.

**Final statement**: the model predicts systematic, distance-scaled EM delays relative to substrate causal signals. Detecting them demands targeted simulations, carefully chosen sources, and tightly controlled multi-band timing campaigns.

---

## Next Steps

If you want, I can now:

**(A)** Prepare the simulation parameter set and expected $\Delta t$ curves for a shortlist of candidate sources, or

**(B)** Draft a one-page experimental proposal for a pilot observing campaign.
