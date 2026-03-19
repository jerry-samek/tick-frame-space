"""Gravity-Solar Radiation Correlation Analysis

Hypothesis (tick-frame model): If photons are `different` events propagating
through deposit chains (RAW 113), solar radiation should carry a gravitational
signal detectable in gravimeter residuals after removing classical effects.

Reference: Saxl & Allen (1971) Phys Rev D 3(4):823 — anomalous 5% gravity
increase during solar eclipse at Harvard.

Usage:
    python -u analyze.py
    python -u analyze.py --year 2016
    python -u analyze.py --use-synthetic  # skip API, use synthetic gravity

March 2026
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False
    print("WARNING: requests not installed. Using synthetic data only.")

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR.mkdir(exist_ok=True)
DATA_DIR.mkdir(exist_ok=True)

# Wettzell station coordinates (iGrav006 superconducting gravimeter)
LAT = 49.1453
LON = 12.8786


# ===========================================================================
# Data acquisition
# ===========================================================================

def download_solar_irradiance(year=2016):
    """Download hourly solar irradiance from NASA POWER API.

    Returns dict: {datetime_str: W/m^2}
    """
    cache = DATA_DIR / f"solar_{year}.json"
    if cache.exists():
        print(f"  Loading cached solar data: {cache}")
        with open(cache) as f:
            return json.load(f)

    if not HAS_REQUESTS:
        return None

    url = (f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
           f"parameters=ALLSKY_SFC_SW_DWN&community=RE"
           f"&longitude={LON}&latitude={LAT}"
           f"&start={year}0101&end={year}1231&format=JSON")

    print(f"  Downloading solar irradiance for {year} from NASA POWER...")
    t0 = time.time()
    try:
        r = requests.get(url, timeout=120)
        r.raise_for_status()
    except Exception as e:
        print(f"  ERROR: {e}")
        return None

    data = r.json()
    params = data.get('properties', {}).get('parameter', {})
    solar = params.get('ALLSKY_SFC_SW_DWN', {})

    # Cache
    with open(cache, 'w') as f:
        json.dump(solar, f)

    elapsed = time.time() - t0
    print(f"  Downloaded {len(solar)} hourly records in {elapsed:.1f}s")
    return solar


def parse_solar_to_arrays(solar_dict):
    """Convert NASA POWER dict to numpy arrays.

    Keys are like '2016010100' (YYYYMMDDHH).
    Returns (timestamps_hours_since_epoch, irradiance_wm2).
    """
    times = []
    values = []
    for key, val in sorted(solar_dict.items()):
        if val < -900:  # NASA POWER missing value sentinel
            continue
        year = int(key[:4])
        month = int(key[4:6])
        day = int(key[6:8])
        hour = int(key[8:10])
        try:
            dt = datetime(year, month, day, hour)
        except ValueError:
            continue
        # Hours since start of year
        epoch = datetime(year, 1, 1)
        hours = (dt - epoch).total_seconds() / 3600.0
        times.append(hours)
        values.append(float(val))

    return np.array(times), np.array(values)


def generate_synthetic_gravity(n_hours, seed=42):
    """Generate synthetic gravity residuals for pipeline testing.

    Components:
    - Tidal signal removed (Level 3 residuals have this done)
    - Small 24h component (0.5 nanogal) — the signal we're looking for
    - White noise at 0.1 microGal RMS
    - Small seasonal drift
    """
    rng = np.random.default_rng(seed)
    t = np.arange(n_hours, dtype=np.float64)

    # White noise: 0.1 microGal = 100 nanogal RMS
    noise = rng.normal(0, 100.0, n_hours)  # nanogal

    # Inject tiny 24h signal: 0.5 nanogal amplitude (well below noise)
    # Phase aligned with solar noon (hour 12 of day)
    signal_24h = 0.5 * np.cos(2 * np.pi * t / 24.0 - np.pi)  # peak at noon

    # Seasonal drift: 2 nanogal over the year
    seasonal = 2.0 * np.sin(2 * np.pi * t / (365.25 * 24))

    gravity = noise + signal_24h + seasonal

    return t, gravity


# ===========================================================================
# Analysis
# ===========================================================================

def cross_correlate(x, y, max_lag=48):
    """Compute normalized cross-correlation for lags -max_lag to +max_lag.

    Returns (lags, correlations).
    """
    x = (x - np.mean(x)) / (np.std(x) + 1e-15)
    y = (y - np.mean(y)) / (np.std(y) + 1e-15)
    n = len(x)
    lags = np.arange(-max_lag, max_lag + 1)
    corr = np.zeros(len(lags))
    for i, lag in enumerate(lags):
        if lag >= 0:
            corr[i] = np.mean(x[:n - lag] * y[lag:])
        else:
            corr[i] = np.mean(x[-lag:] * y[:n + lag])
    return lags, corr


def fft_analysis(signal, dt_hours=1.0):
    """Compute FFT and return (periods_hours, amplitudes).

    Returns only positive frequencies.
    """
    n = len(signal)
    fft_vals = np.fft.rfft(signal - np.mean(signal))
    freqs = np.fft.rfftfreq(n, d=dt_hours)
    amplitudes = 2.0 * np.abs(fft_vals) / n

    # Convert to periods (skip DC)
    mask = freqs > 0
    periods = 1.0 / freqs[mask]
    amps = amplitudes[mask]

    return periods, amps


def day_night_analysis(gravity, solar, threshold=50.0):
    """Compare gravity residuals during day (solar > threshold) vs night.

    Returns (day_mean, day_std, night_mean, night_std, t_stat, p_value).
    """
    day_mask = solar > threshold
    night_mask = solar <= threshold

    g_day = gravity[day_mask]
    g_night = gravity[night_mask]

    if len(g_day) < 10 or len(g_night) < 10:
        return None

    day_mean = np.mean(g_day)
    day_std = np.std(g_day)
    night_mean = np.mean(g_night)
    night_std = np.std(g_night)

    # Welch's t-test
    n1, n2 = len(g_day), len(g_night)
    se = np.sqrt(day_std**2 / n1 + night_std**2 / n2)
    t_stat = (day_mean - night_mean) / (se + 1e-15)

    # Approximate degrees of freedom (Welch-Satterthwaite)
    v1 = day_std**2 / n1
    v2 = night_std**2 / n2
    df = (v1 + v2)**2 / (v1**2 / (n1 - 1) + v2**2 / (n2 - 1) + 1e-15)

    # Approximate p-value using normal (good for large df)
    p_value = 2 * (1 - 0.5 * (1 + np.sign(abs(t_stat)) *
                (1 - np.exp(-abs(t_stat) * (4/np.pi + 0.14 * t_stat**2) /
                 (1 + 0.14 * t_stat**2))**0.5)))
    # Clamp to [0, 1]
    p_value = np.clip(p_value, 0, 1)

    return day_mean, day_std, night_mean, night_std, t_stat, p_value, n1, n2


def bootstrap_significance(gravity, solar, n_bootstrap=1000, seed=42):
    """Shuffle solar time series, recompute correlation. Returns p-value.

    The actual correlation is compared against the null distribution of
    correlations from shuffled solar data.
    """
    rng = np.random.default_rng(seed)
    actual_corr = np.corrcoef(gravity, solar)[0, 1]

    null_corrs = np.zeros(n_bootstrap)
    for i in range(n_bootstrap):
        shuffled = rng.permutation(solar)
        null_corrs[i] = np.corrcoef(gravity, shuffled)[0, 1]

    p_value = np.mean(np.abs(null_corrs) >= np.abs(actual_corr))
    return actual_corr, null_corrs, p_value


# ===========================================================================
# Plotting
# ===========================================================================

def plot_correlation(lags, corr, actual_r, p_boot, tag=''):
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    ax = axes[0]
    ax.plot(lags, corr, 'b-', linewidth=1.5)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.axvline(0, color='red', linestyle=':', alpha=0.5, label='zero lag')
    ax.set_xlabel('Lag (hours)')
    ax.set_ylabel('Cross-correlation')
    ax.set_title('Gravity Residuals vs Solar Irradiance')
    ax.legend()
    ax.grid(True, alpha=0.3)

    ax = axes[1]
    ax.hist(corr, bins=20, alpha=0.7, color='steelblue')
    ax.set_xlabel('Correlation')
    ax.set_ylabel('Count (lag bins)')
    ax.set_title(f'Correlation Distribution\nr={actual_r:.6f}, p_boot={p_boot:.4f}')
    ax.grid(True, alpha=0.3)

    fig.suptitle(f'Cross-Correlation Analysis{" (" + tag + ")" if tag else ""}',
                 fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'correlation_analysis{("_" + tag) if tag else ""}.png',
                dpi=150)
    plt.close()


def plot_fft(periods_grav, amps_grav, periods_solar, amps_solar, tag=''):
    fig, axes = plt.subplots(2, 1, figsize=(14, 8), sharex=True)

    ax = axes[0]
    mask = (periods_grav >= 4) & (periods_grav <= 200)
    ax.plot(periods_grav[mask], amps_grav[mask], 'b-', linewidth=0.8)
    for p in [12, 24, 48]:
        ax.axvline(p, color='red', linestyle=':', alpha=0.4, label=f'{p}h')
    ax.set_ylabel('Amplitude (nanogal)')
    ax.set_title('Gravity Residuals — FFT Spectrum')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')

    ax = axes[1]
    mask = (periods_solar >= 4) & (periods_solar <= 200)
    ax.plot(periods_solar[mask], amps_solar[mask], 'orange', linewidth=0.8)
    for p in [12, 24, 48]:
        ax.axvline(p, color='red', linestyle=':', alpha=0.4)
    ax.set_xlabel('Period (hours)')
    ax.set_ylabel('Amplitude (W/m^2)')
    ax.set_title('Solar Irradiance — FFT Spectrum')
    ax.grid(True, alpha=0.3)
    ax.set_xscale('log')

    fig.suptitle(f'FFT Analysis{" (" + tag + ")" if tag else ""}', fontweight='bold')
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'fft_spectrum{("_" + tag) if tag else ""}.png', dpi=150)
    plt.close()


def plot_day_night(day_night_result, tag=''):
    if day_night_result is None:
        return
    day_mean, day_std, night_mean, night_std, t_stat, p_val, n_day, n_night = day_night_result

    fig, ax = plt.subplots(figsize=(8, 6))
    bars = ax.bar(['Day\n(solar > 50 W/m^2)', 'Night\n(solar <= 50 W/m^2)'],
                  [day_mean, night_mean],
                  yerr=[day_std / np.sqrt(n_day), night_std / np.sqrt(n_night)],
                  capsize=5, color=['#f0ad4e', '#5bc0de'], edgecolor='black')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    ax.set_ylabel('Mean gravity residual (nanogal)')
    ax.set_title(f'Day vs Night Gravity Residuals\n'
                 f't={t_stat:.3f}, p={p_val:.4f}, '
                 f'day: {day_mean:.2f}+/-{day_std:.1f} (n={n_day}), '
                 f'night: {night_mean:.2f}+/-{night_std:.1f} (n={n_night})')
    ax.grid(True, alpha=0.3, axis='y')

    fig.tight_layout()
    fig.savefig(RESULTS_DIR / f'day_night_comparison{("_" + tag) if tag else ""}.png',
                dpi=150)
    plt.close()


# ===========================================================================
# Main
# ===========================================================================

def main():
    parser = argparse.ArgumentParser(description='Gravity-Solar Correlation Analysis')
    parser.add_argument('--year', type=int, default=2016)
    parser.add_argument('--use-synthetic', action='store_true',
                        help='Use synthetic gravity (skip real data attempt)')
    parser.add_argument('--inject-signal', type=float, default=0.0,
                        help='Inject artificial signal (nanogal amplitude) for validation')
    args = parser.parse_args()

    print("=" * 70)
    print("GRAVITY-SOLAR RADIATION CORRELATION ANALYSIS")
    print(f"  Year: {args.year}")
    print(f"  Station: Wettzell ({LAT}N, {LON}E)")
    print("=" * 70)

    # --- Step 1: Solar irradiance ---
    print("\n--- Step 1: Solar Irradiance ---")
    solar_dict = download_solar_irradiance(args.year)
    if solar_dict is None:
        print("  FAILED to get solar data. Cannot proceed.")
        return

    t_solar, solar = parse_solar_to_arrays(solar_dict)
    n_hours = len(solar)
    print(f"  Solar: {n_hours} hours, range [{np.min(solar):.1f}, {np.max(solar):.1f}] W/m^2")
    print(f"  Mean daytime (>50): {np.mean(solar[solar > 50]):.1f} W/m^2")

    # --- Step 2: Gravity data ---
    print("\n--- Step 2: Gravity Data ---")
    using_synthetic = args.use_synthetic
    gravity_source = "synthetic"

    # Check for real gravity data file
    real_data_files = list(DATA_DIR.glob("*grav*")) + list(DATA_DIR.glob("*IGETS*"))
    if real_data_files and not using_synthetic:
        print(f"  Found potential gravity data: {real_data_files[0]}")
        print("  TODO: Parse real gravity data format")
        print("  Falling back to synthetic.")
        using_synthetic = True
    else:
        using_synthetic = True

    if using_synthetic:
        print("  Generating synthetic gravity residuals...")
        t_grav, gravity = generate_synthetic_gravity(n_hours)
        gravity_source = "synthetic"
        print(f"  Gravity: {len(gravity)} hours, RMS={np.std(gravity):.1f} nanogal")

        if args.inject_signal > 0:
            print(f"  INJECTING artificial signal: {args.inject_signal} nanogal at 24h")
            signal = args.inject_signal * np.cos(2 * np.pi * t_grav / 24.0 - np.pi)
            # Scale by solar irradiance (normalized)
            solar_norm = solar / (np.max(solar) + 1e-15)
            gravity += signal * solar_norm
            gravity_source = f"synthetic + {args.inject_signal} nGal injected"

    # --- Step 3: Align time series ---
    print("\n--- Step 3: Align Time Series ---")
    n = min(len(solar), len(gravity))
    solar_aligned = solar[:n]
    gravity_aligned = gravity[:n]
    print(f"  Aligned: {n} common hours")

    # --- Step 4: Cross-correlation ---
    print("\n--- Step 4: Cross-Correlation ---")
    lags, corr = cross_correlate(gravity_aligned, solar_aligned, max_lag=72)
    peak_lag = lags[np.argmax(np.abs(corr))]
    peak_corr = corr[np.argmax(np.abs(corr))]
    zero_lag_corr = corr[lags == 0][0]
    print(f"  Zero-lag correlation: r = {zero_lag_corr:.6f}")
    print(f"  Peak correlation: r = {peak_corr:.6f} at lag = {peak_lag} hours")

    # --- Step 5: FFT ---
    print("\n--- Step 5: FFT Analysis ---")
    periods_grav, amps_grav = fft_analysis(gravity_aligned)
    periods_solar, amps_solar = fft_analysis(solar_aligned)

    # Find 24h and 12h peaks
    for target_period in [24.0, 12.0]:
        idx_grav = np.argmin(np.abs(periods_grav - target_period))
        idx_solar = np.argmin(np.abs(periods_solar - target_period))
        print(f"  {target_period:.0f}h: gravity={amps_grav[idx_grav]:.3f} nGal, "
              f"solar={amps_solar[idx_solar]:.1f} W/m^2")

    # --- Step 6: Day vs night ---
    print("\n--- Step 6: Day vs Night Comparison ---")
    dn_result = day_night_analysis(gravity_aligned, solar_aligned)
    if dn_result:
        day_mean, day_std, night_mean, night_std, t_stat, p_val, n_day, n_night = dn_result
        print(f"  Day:   mean={day_mean:+.3f} nGal, std={day_std:.1f}, n={n_day}")
        print(f"  Night: mean={night_mean:+.3f} nGal, std={night_std:.1f}, n={n_night}")
        print(f"  Difference: {day_mean - night_mean:+.3f} nGal")
        print(f"  t-statistic: {t_stat:.3f}, p-value: {p_val:.4f}")
        if p_val < 0.05:
            print(f"  ** SIGNIFICANT at p < 0.05 **")
        else:
            print(f"  Not significant (p > 0.05)")

    # --- Step 7: Bootstrap significance ---
    print("\n--- Step 7: Bootstrap Significance ---")
    actual_r, null_corrs, p_boot = bootstrap_significance(
        gravity_aligned, solar_aligned, n_bootstrap=1000)
    print(f"  Actual correlation: r = {actual_r:.6f}")
    print(f"  Null distribution: mean={np.mean(null_corrs):.6f}, "
          f"std={np.std(null_corrs):.6f}")
    print(f"  Bootstrap p-value: {p_boot:.4f}")
    if p_boot < 0.05:
        print(f"  ** SIGNIFICANT at p < 0.05 **")
    else:
        print(f"  Not significant (p > 0.05)")

    # --- Step 8: Plots ---
    print("\n--- Step 8: Generating Plots ---")
    tag = f"{args.year}_{gravity_source.split()[0]}"
    plot_correlation(lags, corr, actual_r, p_boot, tag=tag)
    plot_fft(periods_grav, amps_grav, periods_solar, amps_solar, tag=tag)
    plot_day_night(dn_result, tag=tag)
    print(f"  Saved to {RESULTS_DIR}/")

    # --- Step 9: Summary ---
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    summary = f"""Gravity-Solar Correlation Analysis
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Station: Wettzell ({LAT}N, {LON}E)
Year: {args.year}
Gravity source: {gravity_source}
Hours analyzed: {n}

Cross-correlation:
  Zero-lag r = {zero_lag_corr:.6f}
  Peak r = {peak_corr:.6f} at lag = {peak_lag}h
  Bootstrap p-value = {p_boot:.4f}

Day vs Night:
  Day mean: {day_mean:+.3f} +/- {day_std:.1f} nGal (n={n_day})
  Night mean: {night_mean:+.3f} +/- {night_std:.1f} nGal (n={n_night})
  Difference: {day_mean - night_mean:+.3f} nGal
  t = {t_stat:.3f}, p = {p_val:.4f}

FFT peaks:
  24h gravity: {amps_grav[np.argmin(np.abs(periods_grav - 24.0))]:.3f} nGal
  12h gravity: {amps_grav[np.argmin(np.abs(periods_grav - 12.0))]:.3f} nGal

Interpretation:
  {'SIGNIFICANT correlation detected' if p_boot < 0.05 else 'No significant correlation'} (bootstrap p={p_boot:.4f})
  {'SIGNIFICANT day/night difference' if p_val < 0.05 else 'No significant day/night difference'} (t-test p={p_val:.4f})

Notes:
  - Gravity data is {'SYNTHETIC (pipeline test only)' if 'synthetic' in gravity_source else 'REAL gravimeter data'}
  - {'Signal injected for validation' if args.inject_signal > 0 else 'No artificial signal injected'}
  - Classical expectation: no correlation after standard corrections
  - Tick-frame prediction: positive correlation between solar irradiance and local gravity
"""
    print(summary)

    with open(RESULTS_DIR / 'statistical_summary.txt', 'w') as f:
        f.write(summary)
    print(f"  Summary saved to {RESULTS_DIR / 'statistical_summary.txt'}")


if __name__ == '__main__':
    main()
