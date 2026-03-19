"""Multi-station detrended L3 gravity-solar analysis.

Three stations, four instruments, all Level 3 corrected.
Onsala: coastal Sweden (control for ocean loading)
Moxa: inland underground Germany (two sensors)
Membach: inland underground Belgium

Usage:
    python -u run_multi_station.py
    python -u run_multi_station.py --years 2014 2015 2016 2017 2018
"""
import argparse
import calendar
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timezone

try:
    from scipy import stats
    HAS_SCIPY = True
except ImportError:
    HAS_SCIPY = False

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"

STATIONS = {
    "Onsala": {
        "lat": 57.3858, "lon": 11.9266, "elev": 8,
        "type": "coastal, surface",
        "data_dir": DATA_DIR / "Onsala",
        "pattern": "IGETS-SG-RESMIN-os054-{year}{month:02d}r2.ggp",
        "subdir": "{year}",
    },
    "Moxa-L": {
        "lat": 50.6450, "lon": 11.6160, "elev": 455,
        "type": "inland, underground",
        "data_dir": DATA_DIR / "Moxa" / "m1",
        "pattern": "IGETS-SG-RESMIN-mo034-1-{year}{month:02d}r2.ggp",
        "subdir": "{year}",
    },
    "Moxa-U": {
        "lat": 50.6450, "lon": 11.6160, "elev": 455,
        "type": "inland, underground",
        "data_dir": DATA_DIR / "Moxa" / "m2",
        "pattern": "IGETS-SG-RESMIN-mo034-2-{year}{month:02d}r2.ggp",
        "subdir": "{year}",
    },
    "Membach": {
        "lat": 50.6093, "lon": 6.0066, "elev": 250,
        "type": "inland, underground",
        "data_dir": DATA_DIR / "Membach",
        "pattern": "IGETS-SG-RESMIN-mb021-{year}{month:02d}r2.ggp",
        "subdir": "{year}",
    },
}


def parse_ggp(filepath):
    """Parse a GGP file. Returns list of (hour_offset_from_midnight_jan1, residual)."""
    records = []
    with open(filepath) as f:
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
                res = float(parts[2])
            except (ValueError, IndexError):
                continue
            records.append((datestr, timestr, res))
    return records


def load_station_year(station_name, year):
    """Load all months for a station/year. Returns hourly array."""
    info = STATIONS[station_name]
    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    n_hours = 8784 if is_leap else 8760
    gravity = np.full(n_hours, np.nan)
    t0 = datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()

    for month in range(1, 13):
        fname = info["pattern"].format(year=year, month=month)
        subdir = info["subdir"].format(year=year)
        fpath = info["data_dir"] / subdir / fname
        if not fpath.exists():
            continue
        for datestr, timestr, res in parse_ggp(fpath):
            y = int(datestr[:4])
            m = int(datestr[4:6])
            d = int(datestr[6:8])
            hh = int(timestr) // 100
            mm = int(timestr) % 100
            try:
                dt = datetime(y, m, d, hh, mm, tzinfo=timezone.utc)
            except ValueError:
                continue
            idx = int((dt.timestamp() - t0) / 3600)
            if 0 <= idx < n_hours:
                gravity[idx] = res

    valid = np.sum(~np.isnan(gravity))
    return gravity, n_hours, valid


def get_solar(lat, lon, year):
    """Load or download solar data."""
    cache = DATA_DIR / f"solar_{lat:.2f}_{lon:.2f}_{year}.json"
    if cache.exists():
        with open(cache) as f:
            solar_dict = json.load(f)
    elif HAS_REQUESTS:
        url = (f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
               f"parameters=ALLSKY_SFC_SW_DWN&community=RE"
               f"&longitude={lon}&latitude={lat}"
               f"&start={year}0101&end={year}1231&format=JSON")
        print(f"    Downloading solar ({lat:.1f}N, {lon:.1f}E) {year}...")
        r = requests.get(url, timeout=120)
        r.raise_for_status()
        solar_dict = r.json()["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
        with open(cache, "w") as f:
            json.dump(solar_dict, f)
    else:
        return None

    is_leap = (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)
    n_hours = 8784 if is_leap else 8760
    solar = np.zeros(n_hours)
    for key, val in solar_dict.items():
        if val < -900:
            continue
        try:
            dt = datetime(int(key[:4]), int(key[4:6]), int(key[6:8]),
                          int(key[8:10]), tzinfo=timezone.utc)
        except (ValueError, IndexError):
            continue
        t0 = datetime(year, 1, 1, tzinfo=timezone.utc)
        idx = int((dt - t0).total_seconds() / 3600)
        if 0 <= idx < n_hours:
            solar[idx] = val
    return solar


def detrend_monthly(gravity, hours_arr, year):
    """Subtract monthly mean."""
    dt = gravity.copy()
    for month in range(1, 13):
        days_before = sum(calendar.monthrange(year, m)[1] for m in range(1, month))
        days_in = calendar.monthrange(year, month)[1]
        h0, h1 = days_before * 24, (days_before + days_in) * 24
        mask = (hours_arr >= h0) & (hours_arr < h1)
        if np.sum(mask) > 0:
            dt[mask] -= np.mean(gravity[mask])
    return dt


def analyze_station_year(station_name, year):
    """Full detrended analysis for one station-year."""
    info = STATIONS[station_name]
    gravity, n_hours, n_valid = load_station_year(station_name, year)
    if n_valid < 1000:
        return None

    solar = get_solar(info["lat"], info["lon"], year)
    if solar is None:
        return None

    valid = ~np.isnan(gravity)
    both = valid & (solar >= 0)
    hrs = np.arange(n_hours, dtype=float)[both]
    grav = gravity[both]
    sol = solar[both]
    n = len(grav)
    if n < 1000:
        return None

    grav_dt = detrend_monthly(grav, hrs, year)

    day = sol > 50
    night = sol <= 50
    g_day = grav_dt[day]
    g_night = grav_dt[night]

    if len(g_day) < 50 or len(g_night) < 50:
        return None

    diff = np.mean(g_day) - np.mean(g_night)
    se = np.sqrt(np.var(g_day)/len(g_day) + np.var(g_night)/len(g_night))
    t_stat = diff / (se + 1e-15)
    p_val = None
    if HAS_SCIPY:
        _, p_val = stats.ttest_ind(g_day, g_night, equal_var=False)

    # Seasonal
    seasons = {}
    for sname, months in [("Winter", [1,2,11,12]), ("Spring", [3,4,5]),
                           ("Summer", [6,7,8]), ("Autumn", [9,10])]:
        s_mask = np.zeros(n, dtype=bool)
        for m in months:
            db = sum(calendar.monthrange(year, mm)[1] for mm in range(1, m))
            di = calendar.monthrange(year, m)[1]
            s_mask |= (hrs >= db*24) & (hrs < (db+di)*24)
        s_day = grav_dt[s_mask & day]
        s_night = grav_dt[s_mask & night]
        if len(s_day) > 10 and len(s_night) > 10:
            s_diff = np.mean(s_day) - np.mean(s_night)
            s_se = np.sqrt(np.var(s_day)/len(s_day) + np.var(s_night)/len(s_night))
            s_t = s_diff / (s_se + 1e-15)
            s_p = None
            if HAS_SCIPY:
                _, s_p = stats.ttest_ind(s_day, s_night, equal_var=False)
            seasons[sname] = {"diff": s_diff, "t": s_t, "p": s_p,
                              "n_day": len(s_day), "n_night": len(s_night)}

    return {
        "station": station_name, "year": year, "n": n,
        "diff": diff, "se": se, "t": t_stat, "p": p_val,
        "n_day": len(g_day), "n_night": len(g_night),
        "seasons": seasons,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--years", nargs="+", type=int,
                        default=[2014, 2015, 2016, 2017, 2018])
    args = parser.parse_args()

    print("=" * 70)
    print("MULTI-STATION DETRENDED LEVEL 3 ANALYSIS")
    print("=" * 70)
    for sname, info in STATIONS.items():
        print(f"  {sname}: {info['lat']:.2f}N, {info['lon']:.2f}E, "
              f"{info['elev']}m, {info['type']}")
    print(f"  Years: {args.years}")
    print()

    all_results = []
    for station_name in STATIONS:
        for year in args.years:
            print(f"  {station_name} / {year}...", end=" ", flush=True)
            r = analyze_station_year(station_name, year)
            if r is None:
                print("SKIP (insufficient data)")
                continue
            sig = "*" if r["p"] is not None and r["p"] < 0.05 else ""
            print(f"diff={r['diff']:+.4f} t={r['t']:.3f} "
                  f"p={r['p']:.4f}{sig}" if r["p"] else
                  f"diff={r['diff']:+.4f} t={r['t']:.3f}")
            all_results.append(r)

    # === Summary tables ===
    print(f"\n{'='*70}")
    print("RESULTS BY STATION (all years combined)")
    print(f"{'='*70}")
    print(f"{'Station':<12s} {'Type':<22s} {'Mean diff':>10s} {'SE':>8s} {'t':>8s} {'N_years':>8s}")
    for sname in STATIONS:
        rs = [r for r in all_results if r["station"] == sname]
        if not rs:
            continue
        diffs = [r["diff"] for r in rs]
        mean_d = np.mean(diffs)
        se_d = np.std(diffs) / np.sqrt(len(diffs))
        t_d = mean_d / (se_d + 1e-15)
        print(f"{sname:<12s} {STATIONS[sname]['type']:<22s} "
              f"{mean_d:>+10.4f} {se_d:>8.4f} {t_d:>8.2f} {len(rs):>8d}")

    # Grand combined
    all_diffs = [r["diff"] for r in all_results]
    grand_mean = np.mean(all_diffs)
    grand_se = np.std(all_diffs) / np.sqrt(len(all_diffs))
    grand_t = grand_mean / (grand_se + 1e-15)
    print(f"{'COMBINED':<12s} {'all stations':<22s} "
          f"{grand_mean:>+10.4f} {grand_se:>8.4f} {grand_t:>8.2f} {len(all_diffs):>8d}")

    # Seasonal across all stations
    print(f"\n{'='*70}")
    print("SEASONAL BREAKDOWN (all stations, all years)")
    print(f"{'='*70}")
    for sname in ["Winter", "Spring", "Summer", "Autumn"]:
        vals = [r["seasons"][sname]["diff"]
                for r in all_results if sname in r["seasons"]]
        if vals:
            m = np.mean(vals)
            s = np.std(vals) / np.sqrt(len(vals))
            t = m / (s + 1e-15)
            pos = sum(1 for v in vals if v > 0)
            print(f"  {sname:<8s}: {m:+.4f} +/- {s:.4f} nm/s^2  t={t:.2f}  "
                  f"{pos}/{len(vals)} positive")

    # Inland-only (Moxa + Membach)
    print(f"\n{'='*70}")
    print("INLAND UNDERGROUND ONLY (Moxa-L, Moxa-U, Membach)")
    print(f"{'='*70}")
    inland = [r for r in all_results if r["station"] in ("Moxa-L", "Moxa-U", "Membach")]
    if inland:
        inland_diffs = [r["diff"] for r in inland]
        im = np.mean(inland_diffs)
        ise = np.std(inland_diffs) / np.sqrt(len(inland_diffs))
        it = im / (ise + 1e-15)
        print(f"  Combined: {im:+.4f} +/- {ise:.4f} nm/s^2  t={it:.2f}  "
              f"N={len(inland_diffs)}")
        for sname in ["Winter", "Spring", "Summer", "Autumn"]:
            vals = [r["seasons"][sname]["diff"]
                    for r in inland if sname in r["seasons"]]
            if vals:
                m = np.mean(vals)
                s = np.std(vals) / np.sqrt(len(vals))
                t = m / (s + 1e-15)
                pos = sum(1 for v in vals if v > 0)
                print(f"    {sname:<8s}: {m:+.4f} +/- {s:.4f}  t={t:.2f}  "
                      f"{pos}/{len(vals)} positive")

    # === Plots ===
    print(f"\n--- Generating plots ---")

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # 1. By station bar chart
    ax = axes[0, 0]
    station_names = list(STATIONS.keys())
    station_means = []
    station_ses = []
    for sname in station_names:
        rs = [r for r in all_results if r["station"] == sname]
        if rs:
            d = [r["diff"] for r in rs]
            station_means.append(np.mean(d))
            station_ses.append(np.std(d) / np.sqrt(len(d)))
        else:
            station_means.append(0)
            station_ses.append(0)
    colors = ['#5bc0de', '#5cb85c', '#4cae4c', '#f0ad4e']
    ax.bar(station_names, station_means, yerr=station_ses, capsize=5,
           color=colors, edgecolor='black')
    ax.axhline(0, color='gray', linestyle='--')
    ax.axhline(grand_mean, color='red', linestyle='-', linewidth=2,
               label=f'grand mean={grand_mean:+.3f}')
    ax.set_ylabel('Day-Night diff (nm/s^2)')
    ax.set_title('By Station (detrended, all years)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis='y')

    # 2. By year, all stations
    ax = axes[0, 1]
    for i, sname in enumerate(station_names):
        yrs = [r["year"] for r in all_results if r["station"] == sname]
        dfs = [r["diff"] for r in all_results if r["station"] == sname]
        ax.plot(yrs, dfs, 'o-', color=colors[i], label=sname, markersize=5)
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_xlabel('Year')
    ax.set_ylabel('Day-Night diff (nm/s^2)')
    ax.set_title('Year-by-Year (detrended)')
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # 3. Seasonal, all stations combined
    ax = axes[1, 0]
    season_names = ["Winter", "Spring", "Summer", "Autumn"]
    season_colors = ['#5bc0de', '#5cb85c', '#f0ad4e', '#d9534f']
    season_means = []
    season_ses_plot = []
    for sname in season_names:
        vals = [r["seasons"][sname]["diff"]
                for r in all_results if sname in r["seasons"]]
        season_means.append(np.mean(vals) if vals else 0)
        season_ses_plot.append(np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0)
    ax.bar(season_names, season_means, yerr=season_ses_plot, capsize=5,
           color=season_colors, edgecolor='black')
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_ylabel('Day-Night diff (nm/s^2)')
    ax.set_title('Seasonal (all stations, all years)')
    ax.grid(True, alpha=0.3, axis='y')

    # 4. Inland seasonal
    ax = axes[1, 1]
    inland_season_means = []
    inland_season_ses = []
    for sname in season_names:
        vals = [r["seasons"][sname]["diff"]
                for r in inland if sname in r["seasons"]]
        inland_season_means.append(np.mean(vals) if vals else 0)
        inland_season_ses.append(np.std(vals)/np.sqrt(len(vals)) if len(vals) > 1 else 0)
    ax.bar(season_names, inland_season_means, yerr=inland_season_ses, capsize=5,
           color=season_colors, edgecolor='black')
    ax.axhline(0, color='gray', linestyle='--')
    ax.set_ylabel('Day-Night diff (nm/s^2)')
    ax.set_title('Seasonal — INLAND UNDERGROUND ONLY')
    ax.grid(True, alpha=0.3, axis='y')

    fig.suptitle('Multi-Station L3 Detrended: Gravity-Solar Day/Night',
                 fontweight='bold', fontsize=14)
    fig.tight_layout()
    fig.savefig(RESULTS_DIR / 'multi_station_analysis.png', dpi=150)
    print(f"  Saved: {RESULTS_DIR / 'multi_station_analysis.png'}")
    plt.close()

    print("\nDone.")


if __name__ == "__main__":
    main()
