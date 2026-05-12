"""
Experiment 01 — diagnostic: does the 11-sec FLAC sample have the structure
the codec design assumes?

Three hypotheses (see EXPERIMENT_01_diagnostic.md):
  H1 — energy concentration at a few dominant frequencies
  H2 — turning-point informativeness
  H3 — residual structure beyond a basic LPC predictor

10 measurements per block, run on 3 blocks (start/middle/end).
Outputs numbers to stdout and 4 PNG plots; the report (results_01.md)
is written separately.
"""
from __future__ import annotations
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import soundfile as sf
from scipy.linalg import solve_toeplitz

HERE = Path(__file__).parent
SAMPLE = HERE / "data" / "FLAC_11_secs_Small_75d2275409.flac"
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)
PLOTS_DIR = RESULTS_DIR / "plots_01"
PLOTS_DIR.mkdir(exist_ok=True)

BLOCK_MS = 100              # 4410 samples at 44.1 kHz
LPC_ORDERS = (4, 8)         # try both
TOP_K = (3, 10, 50, 100)    # for energy concentration


def load_mono(path: Path) -> tuple[np.ndarray, int]:
    data, sr = sf.read(path)
    if data.ndim > 1:
        data = data[:, 0]   # left channel
    return data, sr


def lpc_yule_walker(x: np.ndarray, order: int) -> np.ndarray:
    """Estimate LPC coefficients a[1..order] via Yule-Walker.
    The forward predictor is x_hat[n] = -sum(a[k] * x[n-k]) for k=1..order."""
    r = np.correlate(x, x, mode="full")[len(x) - 1:]      # autocorr from lag 0
    r = r[: order + 1]
    if r[0] == 0:
        return np.zeros(order)
    # Solve Toeplitz(r[0..p-1]) @ a = r[1..p]
    a = solve_toeplitz((r[:order], r[:order]), r[1: order + 1])
    return a


def lpc_predict_and_residual(x: np.ndarray, order: int) -> tuple[np.ndarray, np.ndarray]:
    """Returns (predicted, residual) where predicted[n] estimates x[n] from x[n-1..n-p]."""
    a = lpc_yule_walker(x, order)
    pred = np.zeros_like(x)
    for n in range(order, len(x)):
        pred[n] = a @ x[n - order: n][::-1]
    residual = x - pred
    # Don't count the warmup region (no prediction available)
    return pred[order:], residual[order:]


def shannon_entropy(values: np.ndarray, bins: int = 1024) -> float:
    """Shannon entropy in bits, computed via histogram (continuous-valued samples)."""
    hist, _ = np.histogram(values, bins=bins)
    p = hist[hist > 0] / hist.sum()
    return float(-np.sum(p * np.log2(p)))


def integer_entropy(values: np.ndarray) -> float:
    """Entropy of the exact integer-valued sample distribution.
    Useful when samples are quantized integers (raw or first-difference)."""
    vals, counts = np.unique(values, return_counts=True)
    p = counts / counts.sum()
    return float(-np.sum(p * np.log2(p)))


def turning_points(x: np.ndarray) -> np.ndarray:
    """Indices where the sign of the first difference changes."""
    d = np.diff(x)
    sgn = np.sign(d)
    # Sign-change detection
    sgn_change = np.diff(sgn)
    return np.nonzero(sgn_change != 0)[0] + 1


def autocorr(x: np.ndarray, max_lag: int) -> np.ndarray:
    x = x - x.mean()
    if x.std() == 0:
        return np.zeros(max_lag + 1)
    full = np.correlate(x, x, mode="full")
    full = full[len(x) - 1:]
    return full[: max_lag + 1] / full[0]


def analyse_block(x: np.ndarray, sr: int, label: str) -> dict:
    n = len(x)
    out: dict = {"label": label, "n_samples": n, "sr": sr}

    # FFT
    spec = np.fft.rfft(x)
    mag = np.abs(spec)
    freqs = np.fft.rfftfreq(n, 1.0 / sr)
    energy = mag ** 2
    total_energy = energy.sum()
    out["peak_freq_hz"] = float(freqs[1 + np.argmax(mag[1:])])  # ignore DC
    for k in TOP_K:
        kth = np.partition(energy, -k)[-k:]
        out[f"top{k}_energy_pct"] = float(100 * kth.sum() / total_energy)

    # Turning points
    tps = turning_points(x)
    out["n_tps"] = int(len(tps))
    out["tp_density_hz"] = float(len(tps) * sr / n)
    out["tp_density_over_2_peakfreq"] = (
        float(out["tp_density_hz"] / (2 * out["peak_freq_hz"]))
        if out["peak_freq_hz"] > 0 else None
    )

    # Autocorrelation
    ac = autocorr(x, max_lag=min(n // 2, sr // 50))  # up to ~20ms lag
    out["autocorr"] = ac

    # Entropy of raw samples (float -> histogram)
    out["raw_entropy_bits"] = shannon_entropy(x)
    out["delta_entropy_bits"] = shannon_entropy(np.diff(x))

    # Integer entropy if we quantize to 16-bit
    x_int16 = np.round(x * 32767).astype(np.int32)
    out["raw_entropy_bits_int16"] = integer_entropy(x_int16)
    out["delta_entropy_bits_int16"] = integer_entropy(np.diff(x_int16))

    # LPC residual
    for p in LPC_ORDERS:
        pred, resid = lpc_predict_and_residual(x, p)
        out[f"lpc{p}_residual_entropy_bits"] = shannon_entropy(resid)
        out[f"lpc{p}_residual_var"] = float(np.var(resid))
        out[f"lpc{p}_residual_autocorr"] = autocorr(resid, max_lag=50)

    out["spec_freqs"] = freqs
    out["spec_mag"] = mag
    return out


def render_plots(blocks: list[dict], outdir: Path):
    # Waveforms (one strip per block)
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    for ax, b in zip(axs, blocks):
        t = np.arange(b["n_samples"]) / b["sr"] * 1000
        ax.plot(t, b["_x_for_plot"], lw=0.5)
        ax.set_title(f"Block: {b['label']}")
        ax.set_ylabel("amp")
    axs[-1].set_xlabel("ms within block")
    fig.tight_layout()
    fig.savefig(outdir / "01_waveforms.png", dpi=120)
    plt.close(fig)

    # FFT spectra
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    for ax, b in zip(axs, blocks):
        ax.semilogy(b["spec_freqs"], b["spec_mag"] + 1e-12, lw=0.6)
        ax.set_title(f"FFT: {b['label']} (peak {b['peak_freq_hz']:.1f} Hz)")
        ax.set_ylabel("|X(f)|")
    axs[-1].set_xlabel("freq (Hz)")
    fig.tight_layout()
    fig.savefig(outdir / "02_fft.png", dpi=120)
    plt.close(fig)

    # Autocorrelation of raw signal
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    for ax, b in zip(axs, blocks):
        lags_ms = np.arange(len(b["autocorr"])) * 1000.0 / b["sr"]
        ax.plot(lags_ms, b["autocorr"], lw=0.6)
        ax.axhline(0, color="k", lw=0.3)
        ax.set_title(f"Autocorrelation: {b['label']}")
        ax.set_ylabel("R(lag) / R(0)")
    axs[-1].set_xlabel("lag (ms)")
    fig.tight_layout()
    fig.savefig(outdir / "03_autocorr.png", dpi=120)
    plt.close(fig)

    # LPC residual autocorrelation (compare order 4 and 8)
    fig, axs = plt.subplots(3, 1, figsize=(12, 6), sharex=True)
    for ax, b in zip(axs, blocks):
        for p, color in zip(LPC_ORDERS, ("C0", "C1")):
            ac = b[f"lpc{p}_residual_autocorr"]
            ax.plot(np.arange(len(ac)), ac, label=f"LPC{p}", lw=0.7, color=color)
        ax.axhline(0, color="k", lw=0.3)
        ax.legend(loc="upper right", fontsize=8)
        ax.set_title(f"LPC residual autocorr: {b['label']}")
        ax.set_ylabel("R(lag) / R(0)")
    axs[-1].set_xlabel("lag (samples)")
    fig.tight_layout()
    fig.savefig(outdir / "04_lpc_residual_autocorr.png", dpi=120)
    plt.close(fig)


def print_block_table(blocks: list[dict]):
    print()
    print("=" * 100)
    headers = ["measurement", *[b["label"] for b in blocks]]
    rows = [
        ("peak_freq_hz",          [f"{b['peak_freq_hz']:.1f}" for b in blocks]),
        ("top3_energy_pct",       [f"{b['top3_energy_pct']:.1f}" for b in blocks]),
        ("top10_energy_pct",      [f"{b['top10_energy_pct']:.1f}" for b in blocks]),
        ("top50_energy_pct",      [f"{b['top50_energy_pct']:.1f}" for b in blocks]),
        ("top100_energy_pct",     [f"{b['top100_energy_pct']:.1f}" for b in blocks]),
        ("n_tps",                 [f"{b['n_tps']}" for b in blocks]),
        ("tp_density_hz",         [f"{b['tp_density_hz']:.1f}" for b in blocks]),
        ("tp_density / 2*peak",   [f"{b['tp_density_over_2_peakfreq']:.2f}"
                                   if b['tp_density_over_2_peakfreq'] is not None else "n/a"
                                   for b in blocks]),
        ("raw_entropy(int16)",    [f"{b['raw_entropy_bits_int16']:.2f}" for b in blocks]),
        ("delta_entropy(int16)",  [f"{b['delta_entropy_bits_int16']:.2f}" for b in blocks]),
        ("raw_entropy(hist)",     [f"{b['raw_entropy_bits']:.2f}" for b in blocks]),
        ("delta_entropy(hist)",   [f"{b['delta_entropy_bits']:.2f}" for b in blocks]),
        ("lpc4_resid_entropy",    [f"{b['lpc4_residual_entropy_bits']:.2f}" for b in blocks]),
        ("lpc8_resid_entropy",    [f"{b['lpc8_residual_entropy_bits']:.2f}" for b in blocks]),
        ("lpc4_resid_var",        [f"{b['lpc4_residual_var']:.6f}" for b in blocks]),
        ("lpc8_resid_var",        [f"{b['lpc8_residual_var']:.6f}" for b in blocks]),
    ]
    fmt = "{:<26s}  " + "  ".join("{:>14s}" for _ in blocks)
    print(fmt.format(*headers))
    print("-" * 100)
    for label, vals in rows:
        print(fmt.format(label, *vals))
    print("=" * 100)


def lpc_residual_autocorr_summary(blocks: list[dict]) -> dict:
    """Per-block: max abs autocorr at lags 2..50 in the LPC8 residual.
    Used to assess H3 (residual structure beyond LPC)."""
    out = {}
    for b in blocks:
        ac = b["lpc8_residual_autocorr"]
        # Skip lag 0 (always 1) and lag 1 (often near 0 by LPC construction)
        if len(ac) > 50:
            tail = np.abs(ac[2:50])
            out[b["label"]] = {
                "max_abs": float(tail.max()),
                "mean_abs": float(tail.mean()),
                "tail_99pct": float(np.percentile(tail, 99)),
            }
    return out


def main():
    print(f"Loading {SAMPLE} ...")
    x, sr = load_mono(SAMPLE)
    print(f"  {len(x)} samples, {sr} Hz, {len(x)/sr:.2f}s")

    block_size = sr * BLOCK_MS // 1000
    starts = {
        "start (1.0s)":  int(1.0 * sr),
        "middle (5.0s)": int(5.0 * sr),
        "end (9.5s)":    int(9.5 * sr),
    }
    blocks: list[dict] = []
    for label, s in starts.items():
        blk = x[s : s + block_size]
        b = analyse_block(blk, sr, label)
        b["_x_for_plot"] = blk
        blocks.append(b)

    print_block_table(blocks)

    # H3 sub-summary: residual autocorr structure beyond LPC
    print("\nLPC8 residual autocorr (lags 2..50):")
    for lbl, stats in lpc_residual_autocorr_summary(blocks).items():
        print(f"  {lbl:<16s}  max|R|={stats['max_abs']:.3f}  "
              f"mean|R|={stats['mean_abs']:.3f}  99pct|R|={stats['tail_99pct']:.3f}")

    # Plots
    render_plots(blocks, PLOTS_DIR)
    print(f"\nSaved 4 plots to {PLOTS_DIR}")

    # Pickle the numbers for the report
    import json
    summary = []
    for b in blocks:
        d = {k: v for k, v in b.items()
             if not isinstance(v, np.ndarray) and not k.startswith("_")}
        summary.append(d)
    (RESULTS_DIR / "diagnostic_01_summary.json").write_text(json.dumps(summary, indent=2, default=str))
    print(f"Saved summary numbers to results/diagnostic_01_summary.json")


if __name__ == "__main__":
    main()
