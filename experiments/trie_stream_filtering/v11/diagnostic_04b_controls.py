"""
Experiment 04b — controls required by the skeptic pass before results_04.md.

Control A (leakage): run the H1/H2 dependency pipeline on synthetic signals:
  (i)   pure 1050 Hz tone (no harmonics) + low noise floor
  (ii)  same tone + 2nd harmonic at the REAL sample's measured level (0.26% energy)
  (iii) same tone + 2nd harmonic at 5% energy (what a strongly harmonic signal gives)
If (i) reproduces most of the real sample's MI, the detected dependency is db8
filter leakage of the fundamental, not harmonic structure.

Control B (envelope): recompute H1/H2 MI on the REAL sample after local
variance normalization (rolling sigma, window 64 coefs). Collapse toward the
null => the dependency is a shared loudness envelope; survival => pair-level
structure beyond the envelope.
"""
from __future__ import annotations
import json
from pathlib import Path

import numpy as np
import pywt
import soundfile as sf

from diagnostic_04 import (
    SAMPLE, RESULTS_DIR, WAVELET, LEVELS, MODE, LPC_ORDER,
    REGION_START_S, REGION_DUR_S,
    lpc_yule_walker, lpc_residual_full, dependency_measures,
)

ROLL_WIN = 64
TONE_HZ = 1050.0
NOISE_DB = -60.0


def h1_h2_for_signal(x: np.ndarray, label: str) -> dict:
    coeffs = pywt.wavedec(x, wavelet=WAVELET, level=LEVELS, mode=MODE)
    w3, w4 = coeffs[3], coeffs[4]
    h1 = dependency_measures(w3, w4, 0, f"{label}/raw")
    r3 = lpc_residual_full(w3, lpc_yule_walker(w3, LPC_ORDER))
    r4 = lpc_residual_full(w4, lpc_yule_walker(w4, LPC_ORDER))
    h2 = dependency_measures(r3, r4, 0, f"{label}/resid")
    for h in (h1, h2):
        h.pop("null_mi")
    return {"h1": h1, "h2": h2}


def rolling_normalize(x: np.ndarray, win: int) -> np.ndarray:
    pad = win // 2
    xx = np.pad(x, pad, mode="reflect")
    sq = np.convolve(xx ** 2, np.ones(win) / win, mode="same")[pad:-pad]
    sigma = np.sqrt(np.maximum(sq, 1e-30))
    return x / sigma


def main():
    rng = np.random.default_rng(20260610)
    sr = 44100
    n = int(REGION_DUR_S * sr)
    t = np.arange(n) / sr
    noise = 10 ** (NOISE_DB / 20) * rng.standard_normal(n)

    fundamental = np.sin(2 * np.pi * TONE_HZ * t)
    e_fund = float(np.sum(fundamental ** 2))

    def harmonic_at_energy_pct(pct: float) -> np.ndarray:
        # amplitude so that harmonic energy = pct% of the total
        a = np.sqrt((pct / 100.0) * e_fund / ((1 - pct / 100.0) * 0.5 * n))
        return a * np.sin(2 * np.pi * 2 * TONE_HZ * t)

    signals = {
        "synthetic_pure_tone": fundamental + noise,
        "synthetic_harmonic_0.26pct": fundamental + harmonic_at_energy_pct(0.26) + noise,
        "synthetic_harmonic_5pct": fundamental + harmonic_at_energy_pct(5.0) + noise,
    }

    out = {}
    print("==== Control A: synthetic leakage ====")
    for label, x in signals.items():
        res = h1_h2_for_signal(x.astype(np.float64), label)
        out[label] = res
        for hk in ("h1", "h2"):
            h = res[hk]
            print(f"  {label:>28s} {hk}: MI={h['mi_bits']:.4f} "
                  f"(null mean {h['null_mi_mean']:.4f}, p99 {h['null_mi_p99']:.4f}) "
                  f"mag_r={h['magnitude_r']:+.3f} -> {'PASS' if h['pass'] else 'FAIL'}")

    print("\n==== Control B: envelope normalization (real sample) ====")
    data, sr_f = sf.read(SAMPLE)
    if data.ndim > 1:
        data = data[:, 0]
    s0 = int(REGION_START_S * sr_f)
    s1 = int((REGION_START_S + REGION_DUR_S) * sr_f)
    x = data[s0:s1].astype(np.float64)
    coeffs = pywt.wavedec(x, wavelet=WAVELET, level=LEVELS, mode=MODE)
    w3, w4 = coeffs[3], coeffs[4]
    r3 = lpc_residual_full(w3, lpc_yule_walker(w3, LPC_ORDER))
    r4 = lpc_residual_full(w4, lpc_yule_walker(w4, LPC_ORDER))

    # baseline (pre-registered full-region LPC) for side-by-side reference
    base = dependency_measures(r3, r4, 0, "real/resid_baseline"); base.pop("null_mi")
    n3 = rolling_normalize(r3, ROLL_WIN // 2)   # W3 has half the rate of W4
    n4 = rolling_normalize(r4, ROLL_WIN)
    norm = dependency_measures(n3, n4, 0, "real/resid_envnorm"); norm.pop("null_mi")
    out["real_resid_baseline"] = base
    out["real_resid_envnorm"] = norm
    print(f"  baseline resid:   MI={base['mi_bits']:.4f} (p99 {base['null_mi_p99']:.4f}) "
          f"mag_r={base['magnitude_r']:+.3f} -> {'PASS' if base['pass'] else 'FAIL'}")
    print(f"  env-normalized:   MI={norm['mi_bits']:.4f} (p99 {norm['null_mi_p99']:.4f}) "
          f"mag_r={norm['magnitude_r']:+.3f} -> {'PASS' if norm['pass'] else 'FAIL'}")

    # also raw-coefficient envelope control (H1 analogue)
    base_raw = dependency_measures(w3, w4, 0, "real/raw_baseline"); base_raw.pop("null_mi")
    nw3 = rolling_normalize(w3, ROLL_WIN // 2)
    nw4 = rolling_normalize(w4, ROLL_WIN)
    norm_raw = dependency_measures(nw3, nw4, 0, "real/raw_envnorm"); norm_raw.pop("null_mi")
    out["real_raw_baseline"] = base_raw
    out["real_raw_envnorm"] = norm_raw
    print(f"  raw baseline:     MI={base_raw['mi_bits']:.4f} (p99 {base_raw['null_mi_p99']:.4f}) "
          f"-> {'PASS' if base_raw['pass'] else 'FAIL'}")
    print(f"  raw env-norm:     MI={norm_raw['mi_bits']:.4f} (p99 {norm_raw['null_mi_p99']:.4f}) "
          f"-> {'PASS' if norm_raw['pass'] else 'FAIL'}")

    (RESULTS_DIR / "diagnostic_04b_summary.json").write_text(
        json.dumps(out, indent=2, default=str))
    print("\nSaved summary to results/diagnostic_04b_summary.json")


if __name__ == "__main__":
    main()
