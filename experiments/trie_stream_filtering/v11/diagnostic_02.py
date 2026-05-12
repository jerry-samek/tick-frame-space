"""
Experiment 02 — band-split diagnostic.

Take 1 second of the tonal region (t=1.0..2.0s), split into 8 octave-spaced
bands, run the same measurements as Exp 01 per band, compare to composite.

Tests H1' (per-band energy concentration), H2' (per-band TP regularity),
H3' (per-band residual structure).
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.linalg import solve_toeplitz
from scipy.signal import butter, sosfiltfilt

HERE = Path(__file__).parent
SAMPLE = HERE / "data" / "FLAC_11_secs_Small_75d2275409.flac"
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)
PLOTS_DIR = RESULTS_DIR / "plots_02"
PLOTS_DIR.mkdir(exist_ok=True)

REGION_START_S = 1.0
REGION_DUR_S = 1.0
LPC_ORDER = 8
TOP_K = (3, 10, 50)

# Octave-spaced band edges (Hz). Each (low, high) → bandpass; (None, low) → highpass.
BAND_EDGES_HZ = [
    (25,    100),
    (100,   200),
    (200,   400),
    (400,   800),
    (800,   1600),
    (1600,  3200),
    (3200,  6400),
    (6400,  None),  # None high → highpass to Nyquist
]


# ----- shared with Exp 01 (re-implemented for self-containment) -----

def lpc_yule_walker(x: np.ndarray, order: int) -> np.ndarray:
    r = np.correlate(x, x, mode="full")[len(x) - 1:]
    r = r[: order + 1]
    if r[0] == 0:
        return np.zeros(order)
    return solve_toeplitz((r[:order], r[:order]), r[1: order + 1])


def lpc_residual(x: np.ndarray, order: int) -> np.ndarray:
    a = lpc_yule_walker(x, order)
    pred = np.zeros_like(x)
    for n in range(order, len(x)):
        pred[n] = a @ x[n - order: n][::-1]
    return (x - pred)[order:]


def shannon_entropy(values: np.ndarray, bins: int = 1024) -> float:
    hist, _ = np.histogram(values, bins=bins)
    p = hist[hist > 0] / hist.sum()
    return float(-np.sum(p * np.log2(p)))


def turning_points(x: np.ndarray) -> int:
    d = np.diff(x)
    sgn = np.sign(d)
    return int((np.diff(sgn) != 0).sum())


def autocorr(x: np.ndarray, max_lag: int) -> np.ndarray:
    x = x - x.mean()
    if x.std() == 0:
        return np.zeros(max_lag + 1)
    full = np.correlate(x, x, mode="full")[len(x) - 1:]
    return full[: max_lag + 1] / full[0]


# ----- band split -----

def make_bandpass(low: float | None, high: float | None, sr: int, order: int = 4):
    nyq = sr / 2 - 1
    if low is None:
        return butter(order, min(high, nyq), fs=sr, btype="lowpass", output="sos")
    if high is None:
        return butter(order, low, fs=sr, btype="highpass", output="sos")
    high = min(high, nyq)
    return butter(order, [low, high], fs=sr, btype="bandpass", output="sos")


def split_bands(x: np.ndarray, sr: int, edges_hz):
    out = []
    for low, high in edges_hz:
        sos = make_bandpass(low, high, sr)
        y = sosfiltfilt(sos, x)
        out.append(y)
    return out


# ----- per-signal measurement -----

def analyse(x: np.ndarray, sr: int, total_energy: float | None = None) -> dict:
    n = len(x)
    spec = np.fft.rfft(x)
    mag = np.abs(spec)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    energy = mag ** 2
    e_total = energy.sum()
    if total_energy is None:
        total_energy = e_total
    out = {
        "n_samples": n,
        "energy_pct_of_total": float(100 * e_total / total_energy) if total_energy > 0 else 0.0,
        "peak_freq_hz": float(freqs[1 + np.argmax(mag[1:])]) if len(mag) > 1 else 0.0,
    }
    for k in TOP_K:
        kth = np.partition(energy, -k)[-k:] if len(energy) >= k else energy
        out[f"top{k}_energy_pct"] = float(100 * kth.sum() / e_total) if e_total > 0 else 0.0
    n_tps = turning_points(x)
    out["n_tps"] = n_tps
    out["tp_density_hz"] = float(n_tps * sr / n)
    out["tp_density_over_2_peakfreq"] = (
        float(out["tp_density_hz"] / (2 * out["peak_freq_hz"]))
        if out["peak_freq_hz"] > 0 else None
    )
    out["raw_entropy_bits"] = shannon_entropy(x)
    out["delta_entropy_bits"] = shannon_entropy(np.diff(x))
    resid = lpc_residual(x, LPC_ORDER)
    out["lpc_residual_entropy_bits"] = shannon_entropy(resid)
    out["lpc_residual_var"] = float(np.var(resid))
    ac = autocorr(resid, max_lag=50)
    tail = np.abs(ac[2:50])
    out["lpc_residual_max_abs_R"] = float(tail.max())
    out["lpc_residual_mean_abs_R"] = float(tail.mean())
    return out, mag, freqs, ac


# ----- main -----

def main():
    print(f"Loading {SAMPLE}")
    data, sr = sf.read(SAMPLE)
    if data.ndim > 1:
        data = data[:, 0]
    s0 = int(REGION_START_S * sr)
    s1 = int((REGION_START_S + REGION_DUR_S) * sr)
    x = data[s0:s1]
    print(f"  Region: {REGION_START_S:.1f}..{REGION_START_S + REGION_DUR_S:.1f}s "
          f"= {len(x)} samples at {sr} Hz")

    # Composite analysis
    composite_out, comp_mag, comp_freqs, comp_ac = analyse(x, sr)
    composite_total_energy = (np.abs(np.fft.rfft(x)) ** 2).sum()

    # Per-band analysis
    bands = split_bands(x, sr, BAND_EDGES_HZ)
    band_results = []
    band_specs = []
    band_acs = []
    for (low, high), b in zip(BAND_EDGES_HZ, bands):
        b_out, b_mag, b_freqs, b_ac = analyse(b, sr, total_energy=composite_total_energy)
        b_out["edge_low_hz"] = low
        b_out["edge_high_hz"] = high
        band_results.append(b_out)
        band_specs.append((b_freqs, b_mag))
        band_acs.append(b_ac)

    # Print table
    print()
    print("=" * 130)
    headers = ["measurement", "composite",
               *[f"B{i}({lo}-{hi or '~Nyq'})" for i, (lo, hi) in enumerate(BAND_EDGES_HZ)]]
    rows = [
        ("energy_pct_of_total",
            f"{composite_out['energy_pct_of_total']:.1f}",
            [f"{b['energy_pct_of_total']:.1f}" for b in band_results]),
        ("peak_freq_hz",
            f"{composite_out['peak_freq_hz']:.0f}",
            [f"{b['peak_freq_hz']:.0f}" for b in band_results]),
        ("top3_energy_pct",
            f"{composite_out['top3_energy_pct']:.1f}",
            [f"{b['top3_energy_pct']:.1f}" for b in band_results]),
        ("top10_energy_pct",
            f"{composite_out['top10_energy_pct']:.1f}",
            [f"{b['top10_energy_pct']:.1f}" for b in band_results]),
        ("tp_density_hz",
            f"{composite_out['tp_density_hz']:.0f}",
            [f"{b['tp_density_hz']:.0f}" for b in band_results]),
        ("tp_density / 2*peak",
            f"{composite_out['tp_density_over_2_peakfreq']:.2f}"
            if composite_out['tp_density_over_2_peakfreq'] is not None else "n/a",
            [f"{b['tp_density_over_2_peakfreq']:.2f}"
             if b['tp_density_over_2_peakfreq'] is not None else "n/a"
             for b in band_results]),
        ("raw_entropy_bits",
            f"{composite_out['raw_entropy_bits']:.2f}",
            [f"{b['raw_entropy_bits']:.2f}" for b in band_results]),
        ("lpc_resid_entropy",
            f"{composite_out['lpc_residual_entropy_bits']:.2f}",
            [f"{b['lpc_residual_entropy_bits']:.2f}" for b in band_results]),
        ("lpc_resid_max|R|",
            f"{composite_out['lpc_residual_max_abs_R']:.3f}",
            [f"{b['lpc_residual_max_abs_R']:.3f}" for b in band_results]),
        ("lpc_resid_mean|R|",
            f"{composite_out['lpc_residual_mean_abs_R']:.3f}",
            [f"{b['lpc_residual_mean_abs_R']:.3f}" for b in band_results]),
    ]
    fmt = "{:<22s}  {:>10s}  " + "  ".join("{:>10s}" for _ in BAND_EDGES_HZ)
    print(fmt.format(*headers))
    print("-" * 130)
    for label, comp, vals in rows:
        print(fmt.format(label, comp, *vals))
    print("=" * 130)

    # Plots
    fig, axs = plt.subplots(8, 1, figsize=(12, 10), sharex=True)
    t = np.arange(len(x)) / sr * 1000
    for i, (ax, b) in enumerate(zip(axs, bands)):
        ax.plot(t, b, lw=0.4)
        lo, hi = BAND_EDGES_HZ[i]
        ax.set_title(f"B{i} ({lo}-{hi or '~Nyq'} Hz)", fontsize=8)
        ax.set_ylabel("amp", fontsize=8)
    axs[-1].set_xlabel("ms")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "01_band_waveforms.png", dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(8, 1, figsize=(12, 10), sharex=True)
    for i, (ax, (f, m)) in enumerate(zip(axs, band_specs)):
        ax.semilogy(f, m + 1e-12, lw=0.5)
        lo, hi = BAND_EDGES_HZ[i]
        ax.set_title(f"FFT B{i} ({lo}-{hi or '~Nyq'}) peak={band_results[i]['peak_freq_hz']:.0f}Hz",
                     fontsize=8)
        ax.set_xlim(0, 8000)
    axs[-1].set_xlabel("Hz")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "02_band_ffts.png", dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(8, 1, figsize=(12, 10), sharex=True)
    for i, (ax, ac) in enumerate(zip(axs, band_acs)):
        ax.plot(np.arange(len(ac)), ac, lw=0.6)
        ax.axhline(0, color="k", lw=0.3)
        lo, hi = BAND_EDGES_HZ[i]
        ax.set_title(f"LPC8 residual autocorr B{i} ({lo}-{hi or '~Nyq'}) "
                     f"max|R|={band_results[i]['lpc_residual_max_abs_R']:.3f}", fontsize=8)
    axs[-1].set_xlabel("lag (samples)")
    fig.tight_layout()
    fig.savefig(PLOTS_DIR / "03_band_lpc_resid_autocorr.png", dpi=110)
    plt.close(fig)

    print(f"\nSaved 3 plots to {PLOTS_DIR}")

    # Save numbers
    summary = {
        "composite": composite_out,
        "bands": [{"edge_low_hz": lo, "edge_high_hz": hi, **b}
                  for (lo, hi), b in zip(BAND_EDGES_HZ, band_results)],
        "region": [REGION_START_S, REGION_START_S + REGION_DUR_S],
    }
    (RESULTS_DIR / "diagnostic_02_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print("Saved summary to results/diagnostic_02_summary.json")


if __name__ == "__main__":
    main()
