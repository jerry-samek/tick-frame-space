"""Level 3 detrended analysis — seasonal artifact removed.

Subtracts monthly mean from each hourly value, then reruns all tests
on the detrended residuals. Multi-year if data available.

Usage:
    python -u run_L3_detrended.py
"""
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timezone

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False


def parse_ggp_year(year):
    """Parse all GGP files for a year. Returns (hours_since_jan1, residuals)."""
    base = DATA_DIR / "Level3" / str(year)
    if not base.exists():
        return None, None

    timestamps = []
    residuals = []
    t0 = datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()

    for month in range(1, 13):
        fname = base / f"IGETS-SG-RESMIN-os054-{year}{month:02d}r2.ggp"
        if not fname.exists():
            continue
        with open(fname) as f:
            in_data = False
            for line in f:
                if line.startswith("77777777"):
                    in_data = True
                    continue
                if not in_data:
                    continue
                if line.startswith("99999999"):
                    break
                parts = line.split()
                if len(parts) < 3:
                    continue
                try:
                    datestr = parts[0]
                    timestr = parts[1]
                    res_fil = float(parts[2])
                except (ValueError, IndexError):
                    continue
                y = int(datestr[:4])
                m = int(datestr[4:6])
                d = int(datestr[6:8])
                hh = int(timestr) // 100
                mm = int(timestr) % 100
                try:
                    dt = datetime(y, m, d, hh, mm, tzinfo=timezone.utc)
                except ValueError:
                    continue
                hour_idx = (dt.timestamp() - t0) / 3600.0
                timestamps.append(hour_idx)
                residuals.append(res_fil)

    if not timestamps:
        return None, None
    return np.array(timestamps), np.array(residuals)


def get_solar_year(year):
    """Load or download solar data for a year at Onsala coords."""
    LAT, LON = 57.3858, 11.9266
    cache = DATA_DIR / f"solar_onsala_{year}.json"
    if cache.exists():
        with open(cache) as f:
            solar_dict = json.load(f)
    else:
        import requests
        url = (f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
               f"parameters=ALLSKY_SFC_SW_DWN&community=RE"
               f"&longitude={LON}&latitude={LAT}"
               f"&start={year}0101&end={year}1231&format=JSON")
        print(f"  Downloading solar {year}...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        solar_dict = r.json()["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        with open(cache, "w") as f:
            json.dump(solar_dict, f)

    # Parse to array
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    n_hours = 8784 if is_leap else 8760
    solar = np.zeros(n_hours)
    for key, val in solar_dict.items():
        if val < -900:
            continue
        try:
            y = int(key[:4])
            m = int(key[4:6])
            d = int(key[6:8])
            h = int(key[8:10])
            dt = datetime(y, m, d, h, tzinfo=timezone.utc)
        except (ValueError, IndexError):
            continue
        t0 = datetime(year, 1, 1, tzinfo=timezone.utc)
        idx = int((dt - t0).total_seconds() / 3600)
        if 0 <= idx < n_hours:
            solar[idx] = val
    return solar, n_hours


def detrend_monthly(gravity, hours, year):
    """Subtract monthly mean from each hour."""
    detrended = gravity.copy()
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    import calendar
    for month in range(1, 13):
        days_before = sum(calendar.monthrange(year, m)[1] for m in range(1, month))
        days_in_month = calendar.monthrange(year, month)[1]
        h_start = days_before * 24
        h_end = h_start + days_in_month * 24
        mask = (hours >= h_start) & (hours < h_end)
        if np.sum(mask) > 0:
            detrended[mask] -= np.mean(gravity[mask])
    return detrended


def analyze_year(year, ax_summary=None, color='blue'):
    """Run full detrended analysis for one year. Returns result dict."""
    print(f"\n{'='*60}")
    print(f"  YEAR {year}")
    print(f"{'='*60}")

    grav_hours, grav_vals = parse_ggp_year(year)
    if grav_hours is None:
        print(f"  No gravity data for {year}")
        return None

    solar, n_hours = get_solar_year(year)

    # Build hourly gravity array
    gravity_hourly = np.full(n_hours, np.nan)
    for h, v in zip(grav_hours, grav_vals):
        idx = int(round(h))
        if 0 <= idx < n_hours:
            gravity_hourly[idx] = v

    valid = ~np.isnan(gravity_hourly)
    n_valid = np.sum(valid)
    print(f"  Gravity: {n_valid}/{n_hours} hours, "
          f"mean={np.nanmean(gravity_hourly):.3f}, std={np.nanstd(gravity_hourly):.3f}")

    # Both must have data
    both = valid & (solar >= 0)
    hours_arr = np.arange(n_hours, dtype=float)

    grav = gravity_hourly[both]
    sol = solar[both]
    hrs = hours_arr[both]
    n = len(grav)
    print(f"  Aligned: {n} hours")

    # Detrend
    grav_dt = detrend_monthly(grav, hrs, year)
    print(f"  Detrended: mean={grav_dt.mean():.4f}, std={grav_dt.std():.3f}")

    # Day vs night on detrended
    day = sol > 50
    night = sol <= 50
    g_day = grav_dt[day]
    g_night = grav_dt[night]
    diff = np.mean(g_day) - np.mean(g_night)
    se = np.sqrt(np.var(g_day)/len(g_day) + np.var(g_night)/len(g_night))
    t_stat = diff / (se + 1e-15)

    if HAS_SCIPY:
        _, p_ttest = stats.ttest_ind(g_day, g_night, equal_var=False)
    else:
        p_ttest = None

    print(f"  Day:   {np.mean(g_day):+.4f} +/- {np.std(g_day):.3f} (n={len(g_day)})")
    print(f"  Night: {np.mean(g_night):+.4f} +/- {np.std(g_night):.3f} (n={len(g_night)})")
    print(f"  Diff:  {diff:+.4f} nm/s^2, t={t_stat:.3f}" +
          (f", p={p_ttest:.6f}" if p_ttest is not None else ""))

    # Bootstrap on detrended
    rng = np.random.default_rng(year)
    actual_r = np.corrcoef(grav_dt, sol)[0, 1]
    null_corrs = np.array([np.corrcoef(grav_dt, rng.permutation(sol))[0, 1]
                            for _ in range(3000)])
    p_boot = np.mean(np.abs(null_corrs) >= np.abs(actual_r))
    print(f"  Correlation: r={actual_r:+.6f}, bootstrap p={p_boot:.4f}")

    # Seasonal within-season day/night
    import calendar
    season_results = {}
    for sname, months in [("Winter", [1,2,11,12]), ("Spring", [3,4,5]),
                           ("Summer", [6,7,8]), ("Autumn", [9,10])]:
        s_mask = np.zeros(n, dtype=bool)
        for m in months:
            days_before = sum(calendar.monthrange(year, mm)[1] for mm in range(1, m))
            days_in = calendar.monthrange(year, m)[1]
            h_start = days_before * 24
            h_end = h_start + days_in * 24
            s_mask |= (hrs >= h_start) & (hrs < h_end)
        s_day = grav_dt[s_mask & day]
        s_night = grav_dt[s_mask & night]
        if len(s_day) > 10 and len(s_night) > 10:
            s_diff = np.mean(s_day) - np.mean(s_night)
            s_se = np.sqrt(np.var(s_day)/len(s_day) + np.var(s_night)/len(s_night))
            s_t = s_diff / (s_se + 1e-15)
            s_p = None
            if HAS_SCIPY:
                _, s_p = stats.ttest_ind(s_day, s_night, equal_var=False)
            season_results[sname] = (s_diff, s_t, s_p, len(s_day), len(s_night))
            p_str = f", p={s_p:.4f}" if s_p is not None else ""
            sig = " *" if s_p is not None and s_p < 0.05 else ""
            print(f"    {sname:8s}: diff={s_diff:+.4f}, t={s_t:.3f}{p_str}{sig}")

    if ax_summary is not None:
        ax_summary.barh(str(year), diff, color=color, alpha=0.7,
                        xerr=se, capsize=3)

    return {
        "year": year,
        "n": n,
        "diff": diff,
        "t": t_stat,
        "p_ttest": p_ttest,
        "r": actual_r,
        "p_boot": p_boot,
        "seasons": season_results,
    }


# ===========================================================================
# Main
# ===========================================================================

print("=" * 70)
print("LEVEL 3 DETRENDED MULTI-YEAR ANALYSIS")
print("Onsala SG054 vs Solar Irradiance — Monthly Mean Removed")
print("=" * 70)

years = list(range(2014, 2019))
results = []

fig_summary, ax_summary = plt.subplots(figsize=(10, 6))

colors = plt.cm.viridis(np.linspace(0.2, 0.8, len(years)))
for year, color in zip(years, colors):
    r = analyze_year(year, ax_summary=ax_summary, color=color)
    if r is not None:
        results.append(r)

# Multi-year summary
print(f"\n{'='*70}")
print("MULTI-YEAR SUMMARY (Detrended)")
print(f"{'='*70}")
print(f"{'Year':>6s} {'N':>6s} {'Day-Night':>10s} {'t':>8s} {'p_ttest':>10s} {'r':>10s} {'p_boot':>8s}")
for r in results:
    p_str = f"{r['p_ttest']:.6f}" if r['p_ttest'] is not None else "N/A"
    print(f"{r['year']:>6d} {r['n']:>6d} {r['diff']:>+10.4f} {r['t']:>8.3f} {p_str:>10s} "
          f"{r['r']:>+10.6f} {r['p_boot']:>8.4f}")

# Average effect
diffs = [r["diff"] for r in results]
mean_diff = np.mean(diffs)
se_diff = np.std(diffs) / np.sqrt(len(diffs))
t_combined = mean_diff / (se_diff + 1e-15)
print(f"\nCombined: mean diff = {mean_diff:+.4f} +/- {se_diff:.4f} nm/s^2")
print(f"Combined t = {t_combined:.3f}")
print(f"Direction: {'POSITIVE (tick-frame consistent)' if mean_diff > 0 else 'NEGATIVE'}")

# Seasonal summary across years
print(f"\nSeasonal day-night difference (detrended, all years):")
for sname in ["Winter", "Spring", "Summer", "Autumn"]:
    s_diffs = [r["seasons"][sname][0] for r in results if sname in r["seasons"]]
    if s_diffs:
        s_mean = np.mean(s_diffs)
        s_se = np.std(s_diffs) / np.sqrt(len(s_diffs))
        s_t = s_mean / (s_se + 1e-15)
        print(f"  {sname:8s}: {s_mean:+.4f} +/- {s_se:.4f} nm/s^2 (n_years={len(s_diffs)}, t={s_t:.2f})")

# Summary plot
ax_summary.axvline(0, color='gray', linestyle='--')
ax_summary.axvline(mean_diff, color='red', linestyle='-', linewidth=2,
                    label=f'mean={mean_diff:+.4f}')
ax_summary.set_xlabel('Day-Night Difference (nm/s^2, detrended)')
ax_summary.set_title('Multi-Year Day-Night Gravity Difference (L3 Detrended)')
ax_summary.legend()
ax_summary.grid(True, alpha=0.3)
fig_summary.tight_layout()
fig_summary.savefig(RESULTS_DIR / 'multi_year_detrended_summary.png', dpi=150)
plt.close()

# Detailed plot for 2016
print("\n--- Generating 2016 detailed plots ---")
r2016 = [r for r in results if r["year"] == 2016]
if r2016:
    # Reload 2016 data for plotting
    grav_hours, grav_vals = parse_ggp_year(2016)
    solar, n_hours = get_solar_year(2016)
    gravity_hourly = np.full(n_hours, np.nan)
    for h, v in zip(grav_hours, grav_vals):
        idx = int(round(h))
        if 0 <= idx < n_hours:
            gravity_hourly[idx] = v
    valid = ~np.isnan(gravity_hourly)
    both = valid & (solar >= 0)
    hrs = np.arange(n_hours, dtype=float)[both]
    grav = gravity_hourly[both]
    sol = solar[both]
    grav_dt = detrend_monthly(grav, hrs, 2016)

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))

    # 1. Cross-correlation (detrended)
    ax = axes[0, 0]
    max_lag = 72
    gn = (grav_dt - np.mean(grav_dt)) / (np.std(grav_dt) + 1e-15)
    sn = (sol - np.mean(sol)) / (np.std(sol) + 1e-15)
    n = len(grav_dt)
    lags = np.arange(-max_lag, max_lag + 1)
    cc = np.array([np.mean(gn[:n-l]*sn[l:]) if l >= 0 else np.mean(gn[-l:]*sn[:n+l]) for l in lags])
    ax.plot(lags, cc, 'b-', linewidth=1.5)
    ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
    sig = 1.96 / np.sqrt(n)
    ax.axhline(sig, color='green', linestyle=':', alpha=0.5, label=f'95% CI')
    ax.axhline(-sig, color='green', linestyle=':', alpha=0.5)
    ax.set_xlabel('Lag (hours)')
    ax.set_ylabel('Cross-correlation')
    ax.set_title(f'Detrended Cross-Correlation 2016')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 2. Hourly mean by time of day
    ax = axes[0, 1]
    hour_of_day = (hrs % 24).astype(int)
    grav_by_hour = [grav_dt[hour_of_day == h] for h in range(24)]
    solar_by_hour = [sol[hour_of_day == h] for h in range(24)]
    means_g = [np.mean(g) for g in grav_by_hour]
    sems_g = [np.std(g)/np.sqrt(len(g)) for g in grav_by_hour]
    means_s = [np.mean(s) for s in solar_by_hour]
    ax2 = ax.twinx()
    ax.errorbar(range(24), means_g, yerr=sems_g, fmt='bo-', markersize=4,
                linewidth=1.5, capsize=2, label='gravity L3 detrended')
    ax2.plot(range(24), means_s, 'orange', linewidth=2, alpha=0.7, label='solar')
    ax.set_xlabel('Hour of day (UTC)')
    ax.set_ylabel('Mean L3 residual (nm/s^2)', color='blue')
    ax2.set_ylabel('Mean solar (W/m^2)', color='orange')
    ax.set_title('Diurnal Pattern (2016, detrended)')
    ax.axhline(0, color='gray', linestyle='--', alpha=0.3)
    ax.legend(loc='upper left', fontsize=8)
    ax2.legend(loc='upper right', fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Day vs Night per season
    ax = axes[0, 2]
    r16 = r2016[0]
    seasons = ["Winter", "Spring", "Summer", "Autumn"]
    s_diffs = [r16["seasons"].get(s, (0,0,0,0,0))[0] for s in seasons]
    s_colors = ['#5bc0de', '#5cb85c', '#f0ad4e', '#d9534f']
    ax.bar(seasons, s_diffs, color=s_colors, edgecolor='black')
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_ylabel('Day-Night difference (nm/s^2)')
    ax.set_title('2016 Seasonal Day-Night (detrended)')
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Bootstrap null (detrended)
    ax = axes[1, 0]
    rng = np.random.default_rng(2016)
    actual_r = np.corrcoef(grav_dt, sol)[0, 1]
    null = np.array([np.corrcoef(grav_dt, rng.permutation(sol))[0, 1] for _ in range(3000)])
    p = np.mean(np.abs(null) >= np.abs(actual_r))
    ax.hist(null, bins=60, alpha=0.7, color='gray', label='null')
    ax.axvline(actual_r, color='red', linewidth=2, label=f'r={actual_r:.5f}')
    ax.set_xlabel('Correlation')
    ax.set_title(f'Bootstrap Detrended (p={p:.4f})')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 5. Scatter detrended
    ax = axes[1, 1]
    daytime = sol > 10
    ax.scatter(sol[daytime], grav_dt[daytime], s=1, alpha=0.2, color='orange')
    ax.scatter(sol[~daytime], grav_dt[~daytime], s=1, alpha=0.1, color='blue')
    if np.sum(daytime) > 10:
        z = np.polyfit(sol[daytime], grav_dt[daytime], 1)
        xf = np.linspace(10, sol.max(), 100)
        ax.plot(xf, np.polyval(z, xf), 'r-', linewidth=2,
                label=f'slope={z[0]:.6f}')
    ax.set_xlabel('Solar (W/m^2)')
    ax.set_ylabel('Detrended L3 residual (nm/s^2)')
    ax.set_title('Scatter (detrended)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 6. Multi-year seasonal
    ax = axes[1, 2]
    for sname, color in zip(seasons, s_colors):
        vals = [r["seasons"].get(sname, (np.nan,))[0] for r in results]
        yrs = [r["year"] for r in results]
        ax.plot(yrs, vals, 'o-', color=color, label=sname, markersize=6)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_xlabel('Year')
    ax.set_ylabel('Day-Night diff (nm/s^2)')
    ax.set_title('Seasonal Day-Night Across Years')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    fig.suptitle('Onsala SG054 LEVEL 3 DETRENDED: Gravity-Solar (2016 + Multi-Year)',
                 fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'onsala_L3_detrended_2016.png', dpi=150)
    print(f"  Saved: {RESULTS_DIR / 'onsala_L3_detrended_2016.png'}")
    plt.close()

print("\nDone.")
