"""
Experiment 03 — reversibility test via wavelet decomposition.

Replace Exp 02's Butterworth filterbank with a reversible wavelet decomposition
(pywt). Verify perfect reconstruction. Re-measure H1''/H2''/H3''.

Each wavelet sub-band has its own effective sample rate (downsampled by 2^level
for the detail bands, or 2^max_level for the approximation). Frequency-derived
metrics are interpreted at that sub-band's effective sample rate.
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pywt
import soundfile as sf
from scipy.linalg import solve_toeplitz

HERE = Path(__file__).parent
SAMPLE = HERE / "data" / "FLAC_11_secs_Small_75d2275409.flac"
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)
PLOTS_DIR = RESULTS_DIR / "plots_03"
PLOTS_DIR.mkdir(exist_ok=True)

REGION_START_S = 1.0
REGION_DUR_S = 1.0
WAVELET = "db8"
LEVELS = 7
MODE = "periodization"
LPC_ORDER = 8
TOP_K = (3, 10, 50)


# ---------- shared measurements (re-implemented for self-containment) ----------

def lpc_yule_walker(x: np.ndarray, order: int) -> np.ndarray:
    if len(x) < order + 1:
        return np.zeros(order)
    r = np.correlate(x, x, mode="full")[len(x) - 1:]
    r = r[: order + 1]
    if r[0] == 0:
        return np.zeros(order)
    return solve_toeplitz((r[:order], r[:order]), r[1: order + 1])


def lpc_residual(x: np.ndarray, order: int) -> np.ndarray:
    if len(x) < order + 2:
        return x.copy()
    a = lpc_yule_walker(x, order)
    pred = np.zeros_like(x)
    for n in range(order, len(x)):
        pred[n] = a @ x[n - order: n][::-1]
    return (x - pred)[order:]


def shannon_entropy(values: np.ndarray, bins: int = 1024) -> float:
    if len(values) == 0:
        return 0.0
    hist, _ = np.histogram(values, bins=bins)
    p = hist[hist > 0] / hist.sum()
    return float(-np.sum(p * np.log2(p)))


def turning_points(x: np.ndarray) -> int:
    if len(x) < 3:
        return 0
    d = np.diff(x)
    sgn = np.sign(d)
    return int((np.diff(sgn) != 0).sum())


def autocorr(x: np.ndarray, max_lag: int) -> np.ndarray:
    if len(x) < max_lag + 2:
        max_lag = max(0, len(x) - 2)
    if max_lag == 0:
        return np.array([1.0])
    x = x - x.mean()
    if x.std() == 0:
        return np.zeros(max_lag + 1)
    full = np.correlate(x, x, mode="full")[len(x) - 1:]
    return full[: max_lag + 1] / full[0]


def analyse_band(coef: np.ndarray, eff_sr: float, total_energy: float) -> dict:
    n = len(coef)
    e_band = float(np.sum(coef ** 2))
    out = {
        "n_samples": n,
        "eff_sr_hz": float(eff_sr),
        "energy_pct_of_total": 100.0 * e_band / total_energy if total_energy > 0 else 0.0,
    }
    if n < 4:
        out.update({k: None for k in (
            "peak_freq_hz", "top3_energy_pct", "top10_energy_pct",
            "tp_density_hz", "tp_density_over_2_peakfreq",
            "raw_entropy_bits", "lpc_residual_entropy_bits",
            "lpc_residual_max_abs_R", "lpc_residual_mean_abs_R",
        )})
        return out

    spec = np.fft.rfft(coef)
    mag = np.abs(spec)
    freqs = np.fft.rfftfreq(n, 1.0 / eff_sr)
    energy = mag ** 2
    e_total_bins = energy.sum()
    out["peak_freq_hz"] = float(freqs[1 + np.argmax(mag[1:])]) if len(mag) > 1 else 0.0
    for k in TOP_K:
        kk = min(k, len(energy))
        kth = np.partition(energy, -kk)[-kk:]
        out[f"top{k}_energy_pct"] = float(100 * kth.sum() / e_total_bins) if e_total_bins > 0 else 0.0

    n_tps = turning_points(coef)
    out["n_tps"] = n_tps
    out["tp_density_hz"] = float(n_tps * eff_sr / n)
    out["tp_density_over_2_peakfreq"] = (
        float(out["tp_density_hz"] / (2 * out["peak_freq_hz"]))
        if out["peak_freq_hz"] > 0 else None
    )
    out["raw_entropy_bits"] = shannon_entropy(coef)
    out["delta_entropy_bits"] = shannon_entropy(np.diff(coef))
    resid = lpc_residual(coef, LPC_ORDER)
    out["lpc_residual_entropy_bits"] = shannon_entropy(resid)
    out["lpc_residual_var"] = float(np.var(resid))
    ac = autocorr(resid, max_lag=min(50, len(resid) - 2))
    if len(ac) > 2:
        tail = np.abs(ac[2:])
        out["lpc_residual_max_abs_R"] = float(tail.max())
        out["lpc_residual_mean_abs_R"] = float(tail.mean())
    else:
        out["lpc_residual_max_abs_R"] = 0.0
        out["lpc_residual_mean_abs_R"] = 0.0
    return out


# ---------- main ----------

def main():
    print(f"Loading {SAMPLE}")
    data, sr = sf.read(SAMPLE)
    if data.ndim > 1:
        data = data[:, 0]
    s0 = int(REGION_START_S * sr)
    s1 = int((REGION_START_S + REGION_DUR_S) * sr)
    x = data[s0:s1].astype(np.float64)
    n_in = len(x)
    print(f"  Region: {REGION_START_S:.1f}..{REGION_START_S + REGION_DUR_S:.1f}s "
          f"= {n_in} samples at {sr} Hz")
    print(f"  Wavelet: {WAVELET}, levels={LEVELS}, mode={MODE}")

    # ---- Reversibility verification ----
    coeffs = pywt.wavedec(x, wavelet=WAVELET, level=LEVELS, mode=MODE)
    x_rec = pywt.waverec(coeffs, wavelet=WAVELET, mode=MODE)
    # waverec may return a slightly longer array depending on mode; trim
    x_rec = x_rec[:n_in]
    max_err = float(np.max(np.abs(x - x_rec)))
    rms_err = float(np.sqrt(np.mean((x - x_rec) ** 2)))
    print(f"\nReconstruction error: max={max_err:.3e}  rms={rms_err:.3e}")
    if max_err > 1e-10:
        print("  WARNING: reconstruction error larger than 1e-10. Wavelet may not be near-lossless at float precision.")
    else:
        print("  Reversibility: PASS (within float-epsilon).")

    # ---- Band naming and effective sample rates ----
    # coeffs is [cA_n, cD_n, cD_{n-1}, ..., cD_1]
    # cA_n covers DC..sr/2^(n+1) at effective sr/2^n
    # cD_k covers sr/2^(k+1) .. sr/2^k at effective sr/2^k
    band_names = [f"W0(cA{LEVELS})"] + [f"W{LEVELS - k + 1}(cD{k})" for k in range(LEVELS, 0, -1)]
    # Effective sample rates and frequency ranges
    band_info = []
    band_info.append({
        "name": band_names[0],
        "eff_sr": sr / (2 ** LEVELS),
        "freq_lo": 0.0,
        "freq_hi": sr / (2 ** (LEVELS + 1)),
    })
    for i, k in enumerate(range(LEVELS, 0, -1)):
        band_info.append({
            "name": band_names[i + 1],
            "eff_sr": sr / (2 ** k),
            "freq_lo": sr / (2 ** (k + 1)),
            "freq_hi": sr / (2 ** k),
        })

    # ---- Total energy (raw signal) ----
    total_energy = float(np.sum(x ** 2))

    # ---- Per-band analysis ----
    band_results = []
    for c, info in zip(coeffs, band_info):
        out = analyse_band(c, info["eff_sr"], total_energy)
        out["name"] = info["name"]
        out["freq_lo"] = info["freq_lo"]
        out["freq_hi"] = info["freq_hi"]
        band_results.append(out)

    # ---- Print table ----
    print()
    print("=" * 145)
    fmt_row = lambda label, vals: print(("{:<22s}  " + "  ".join("{:>12s}" for _ in vals)).format(label, *vals))
    headers = ["measurement"] + [
        f"{b['name']}({b['freq_lo']:.0f}-{b['freq_hi']:.0f})" for b in band_results
    ]
    print(("{:<22s}  " + "  ".join("{:>12s}" for _ in band_results)).format(*headers))
    print("-" * 145)
    rows = [
        ("eff_sr_hz",        [f"{b['eff_sr_hz']:.0f}" for b in band_results]),
        ("n_samples",        [f"{b['n_samples']}" for b in band_results]),
        ("energy_pct",       [f"{b['energy_pct_of_total']:.1f}" for b in band_results]),
        ("peak_freq_hz",     [f"{b['peak_freq_hz']:.0f}" if b['peak_freq_hz'] is not None else "n/a"
                              for b in band_results]),
        ("top3_energy_pct",  [f"{b['top3_energy_pct']:.1f}" if b['top3_energy_pct'] is not None else "n/a"
                              for b in band_results]),
        ("tp_density_hz",    [f"{b['tp_density_hz']:.0f}" if b['tp_density_hz'] is not None else "n/a"
                              for b in band_results]),
        ("tp_density/2*peak",[f"{b['tp_density_over_2_peakfreq']:.2f}"
                              if b['tp_density_over_2_peakfreq'] is not None else "n/a"
                              for b in band_results]),
        ("raw_entropy",      [f"{b['raw_entropy_bits']:.2f}" if b['raw_entropy_bits'] is not None else "n/a"
                              for b in band_results]),
        ("lpc_resid_entropy",[f"{b['lpc_residual_entropy_bits']:.2f}"
                              if b['lpc_residual_entropy_bits'] is not None else "n/a"
                              for b in band_results]),
        ("lpc_resid_max|R|", [f"{b['lpc_residual_max_abs_R']:.3f}"
                              if b['lpc_residual_max_abs_R'] is not None else "n/a"
                              for b in band_results]),
        ("lpc_resid_mean|R|",[f"{b['lpc_residual_mean_abs_R']:.3f}"
                              if b['lpc_residual_mean_abs_R'] is not None else "n/a"
                              for b in band_results]),
    ]
    for label, vals in rows:
        fmt_row(label, vals)
    print("=" * 145)

    # ---- Plots ----
    n_bands = len(band_results)
    fig, axs = plt.subplots(n_bands, 1, figsize=(12, 11), sharex=False)
    for i, (ax, c, b) in enumerate(zip(axs, coeffs, band_results)):
        ax.plot(np.arange(len(c)), c, lw=0.4)
        ax.set_title(f"{b['name']} ({b['freq_lo']:.0f}-{b['freq_hi']:.0f} Hz)  "
                     f"eff_sr={b['eff_sr_hz']:.0f}  n={b['n_samples']}", fontsize=8)
        ax.set_ylabel("coef", fontsize=7)
    axs[-1].set_xlabel("coefficient index")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_wavelet_subbands.png", dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(n_bands, 1, figsize=(12, 11), sharex=False)
    for i, (ax, c, b) in enumerate(zip(axs, coeffs, band_results)):
        if len(c) > 4:
            spec = np.abs(np.fft.rfft(c))
            f = np.fft.rfftfreq(len(c), 1.0 / b["eff_sr_hz"])
            ax.semilogy(f, spec + 1e-12, lw=0.5)
        ax.set_title(f"FFT {b['name']} (peak={b['peak_freq_hz']:.0f} Hz)" if b['peak_freq_hz'] is not None
                     else f"FFT {b['name']}", fontsize=8)
    axs[-1].set_xlabel("Hz")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "02_wavelet_band_ffts.png", dpi=110)
    plt.close(fig)

    print(f"\nSaved 2 plots to {PLOTS_DIR}")

    # ---- JSON summary ----
    summary = {
        "wavelet": WAVELET,
        "levels": LEVELS,
        "mode": MODE,
        "region": [REGION_START_S, REGION_START_S + REGION_DUR_S],
        "reconstruction_max_err": max_err,
        "reconstruction_rms_err": rms_err,
        "bands": band_results,
    }
    (RESULTS_DIR / "diagnostic_03_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print("Saved summary to results/diagnostic_03_summary.json")


if __name__ == "__main__":
    main()
