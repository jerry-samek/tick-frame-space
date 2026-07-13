"""Estimate trie-codec size vs FLAC for the 11-sec sample.

Two regimes to compare:
  A) Trie with explicit (tick, value) per sample — like v10 Mode A.
  B) Trie storing per-band LPC residuals sequentially — what an "ideal"
     trie codec would store if it dropped the explicit-position feature.

Both compared against the actual FLAC file size and against raw int16.
"""
from pathlib import Path

import numpy as np
import pywt
import soundfile as sf
from scipy.linalg import solve_toeplitz

HERE = Path(__file__).parent
FLAC = HERE / "data" / "FLAC_11_secs_Small_75d2275409.flac"


def lpc_yule_walker(x, order):
    if len(x) < order + 1:
        return np.zeros(order)
    r = np.correlate(x, x, mode="full")[len(x) - 1:]
    r = r[:order + 1]
    if r[0] == 0:
        return np.zeros(order)
    return solve_toeplitz((r[:order], r[:order]), r[1: order + 1])


def lpc_residual(x, order):
    if len(x) < order + 2:
        return x.copy()
    a = lpc_yule_walker(x, order)
    pred = np.zeros_like(x)
    for n in range(order, len(x)):
        pred[n] = a @ x[n - order:n][::-1]
    return (x - pred)[order:]


def shannon_entropy(values, bins=2048):
    if len(values) == 0:
        return 0.0
    hist, _ = np.histogram(values, bins=bins)
    p = hist[hist > 0] / hist.sum()
    return float(-np.sum(p * np.log2(p)))


def main():
    info = sf.info(FLAC)
    print(f"=== FLAC metadata ===")
    print(f"  channels:    {info.channels}")
    print(f"  sample rate: {info.samplerate} Hz")
    print(f"  duration:    {info.duration:.2f} s")
    print(f"  total frames: {info.frames}")
    print(f"  subtype:     {info.subtype}  ({info.subtype_info})")
    print(f"  format:      {info.format_info}")

    flac_size = FLAC.stat().st_size
    print(f"\nActual FLAC file size: {flac_size:,} bytes ({flac_size / 1024:.1f} KB)")

    # Estimate raw size at the FLAC's actual bit depth.
    # PCM_16 = 2 bytes/sample, PCM_24 = 3 bytes/sample, FLOAT = 4 bytes/sample
    bytes_per_sample_per_channel = {
        "PCM_S8": 1, "PCM_U8": 1,
        "PCM_16": 2, "PCM_24": 3, "PCM_32": 4,
        "FLOAT": 4, "DOUBLE": 8,
    }.get(info.subtype, 2)
    raw_size = info.frames * info.channels * bytes_per_sample_per_channel
    print(f"Raw size at {bytes_per_sample_per_channel * 8}-bit: "
          f"{raw_size:,} bytes ({raw_size / 1024:.1f} KB)")

    print(f"\nFLAC compression ratio (FLAC / raw): {flac_size / raw_size:.3f}")
    print(f"FLAC bits per sample (avg): "
          f"{flac_size * 8 / (info.frames * info.channels):.2f}")

    # ====== Estimate A: trie with explicit position per sample ======
    print("\n=== Estimate A: Trie with explicit (tick, value) per sample ===")
    n_samples = info.frames * info.channels
    bits_per_tick = int(np.ceil(np.log2(info.frames)))  # log2(N) for tick index
    bits_per_value = bytes_per_sample_per_channel * 8
    bits_per_token = bits_per_tick + bits_per_value
    trie_a_size = n_samples * bits_per_token / 8
    print(f"  bits per token: {bits_per_tick} (tick) + {bits_per_value} (value) "
          f"= {bits_per_token} bits")
    print(f"  total: {n_samples:,} samples × {bits_per_token} bits = "
          f"{trie_a_size:,.0f} bytes ({trie_a_size / 1024:.1f} KB)")
    print(f"  vs raw:  {trie_a_size / raw_size:.2f}×")
    print(f"  vs FLAC: {trie_a_size / flac_size:.2f}×")

    # ====== Estimate B: trie storing per-band LPC residuals (sequential) ======
    print("\n=== Estimate B: Trie storing per-band LPC residuals sequentially ===")
    print("  (no explicit position — like FLAC's predictor + Rice, but using")
    print("  the trie's hierarchical organization for entropy coding)")

    # Take the actual 11-sec sample, channel 0, run wavelet decomp + LPC residuals
    data, sr = sf.read(FLAC)
    if data.ndim > 1:
        data = data[:, 0]
    print(f"  Analyzing channel 0 ({len(data):,} samples)")

    coeffs = pywt.wavedec(data, wavelet="db8", level=7, mode="periodization")
    total_bits = 0
    print(f"  Wavelet sub-band entropy summary:")
    for i, c in enumerate(coeffs):
        if i == 0:
            label = f"W0(cA7)"
        else:
            label = f"W{i}(cD{8 - i})"
        resid = lpc_residual(c, order=8)
        h = shannon_entropy(resid)
        total_bits += len(c) * h
        print(f"    {label:<10} n={len(c):>6}  LPC8 resid entropy={h:5.2f} bits  "
              f"contrib={len(c) * h / 8:>10.0f} bytes")
    # Per-channel residual storage cost (entropy floor)
    resid_size_one_channel = total_bits / 8
    # Stereo: assume both channels similarly behaved (rough estimate)
    resid_size_stereo = resid_size_one_channel * info.channels
    # Add overhead: anchor (first samples to bootstrap LPC), LPC coeffs per frame
    # Rough overhead: 1% of residual size (LPC tables, sub-band metadata)
    overhead = resid_size_stereo * 0.05
    trie_b_size = resid_size_stereo + overhead
    print(f"\n  Per-channel residual entropy floor: {resid_size_one_channel:,.0f} bytes")
    print(f"  Stereo (×{info.channels}): {resid_size_stereo:,.0f} bytes")
    print(f"  + 5% overhead (LPC coeffs + anchor): {trie_b_size:,.0f} bytes "
          f"({trie_b_size / 1024:.1f} KB)")
    print(f"  vs raw:  {trie_b_size / raw_size:.2f}×")
    print(f"  vs FLAC: {trie_b_size / flac_size:.2f}×")

    # ====== Estimate C: trie with explicit position per BAND coefficient ======
    print("\n=== Estimate C: Trie with explicit (band_id, position, value) ===")
    print("  (preserves per-band queryability, not per-sample)")
    # Total wavelet coeffs = same as input samples
    bits_per_band_id = 3  # 8 bands
    # Position in band: log2 of band length. Use largest band for upper bound.
    max_band_len = max(len(c) for c in coeffs)
    bits_per_pos = int(np.ceil(np.log2(max_band_len)))
    # Value: float coefficient — quantize to ~bits_per_value
    bits_per_token_c = bits_per_band_id + bits_per_pos + bits_per_value
    trie_c_size = n_samples * bits_per_token_c / 8
    print(f"  bits per token: {bits_per_band_id} (band) + {bits_per_pos} (pos) "
          f"+ {bits_per_value} (value) = {bits_per_token_c}")
    print(f"  total: {trie_c_size:,.0f} bytes ({trie_c_size / 1024:.1f} KB)")
    print(f"  vs raw:  {trie_c_size / raw_size:.2f}×")
    print(f"  vs FLAC: {trie_c_size / flac_size:.2f}×")

    # ====== Summary table ======
    print("\n" + "=" * 70)
    print(f"{'representation':<40} {'size (KB)':>12} {'vs FLAC':>10}")
    print("-" * 70)
    print(f"{'Raw ' + str(bytes_per_sample_per_channel*8) + '-bit PCM':<40} "
          f"{raw_size/1024:>12,.1f} {raw_size/flac_size:>9.2f}×")
    print(f"{'FLAC (actual)':<40} {flac_size/1024:>12,.1f} {1.00:>9.2f}×")
    print(f"{'Trie A (explicit per-sample tick+val)':<40} "
          f"{trie_a_size/1024:>12,.1f} {trie_a_size/flac_size:>9.2f}×")
    print(f"{'Trie B (per-band residual entropy)':<40} "
          f"{trie_b_size/1024:>12,.1f} {trie_b_size/flac_size:>9.2f}×")
    print(f"{'Trie C (explicit band+pos+val)':<40} "
          f"{trie_c_size/1024:>12,.1f} {trie_c_size/flac_size:>9.2f}×")
    print("=" * 70)


if __name__ == "__main__":
    main()
