"""Zugspitze vs Membach: surface high-altitude vs underground comparison.

Zugspitze: 2939m surface, maximum solar exposure
Membach: 250m underground, shielded from direct solar

If solar radiation affects gravity, Zugspitze should show larger signal.
"""
import numpy as np
import calendar
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from datetime import datetime, timezone
from pathlib import Path

try:
    from scipy import stats
except ImportError:
    stats = None

DATA_DIR = Path(__file__).parent / "data"
RESULTS_DIR = Path(__file__).parent / "results"

STATIONS = {
    "Zugspitze": {
        "lat": 47.4207, "lon": 10.9847, "elev": 2939,
        "type": "surface, high-altitude (2939m)",
        "dir": DATA_DIR / "Zugspitze",
        "pat": "IGETS-SG-RESMIN-zu052-{year}{month:02d}r2.ggp",
    },
    "Membach": {
        "lat": 50.6093, "lon": 6.0066, "elev": 250,
        "type": "underground (250m)",
        "dir": DATA_DIR / "Membach",
        "pat": "IGETS-SG-RESMIN-mb021-{year}{month:02d}r2.ggp",
    },
}


def parse_ggp_year(base_dir, pattern, year):
    t0 = datetime(year, 1, 1, tzinfo=timezone.utc).timestamp()
    is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    n_hours = 8784 if is_leap else 8760
    gravity = np.full(n_hours, np.nan)
    for month in range(1, 13):
        fname = base_dir / str(year) / pattern.format(year=year, month=month)
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
                    ds, ts, res = parts[0], parts[1], float(parts[2])
                except (ValueError, IndexError):
                    continue
                y, m, d = int(ds[:4]), int(ds[4:6]), int(ds[6:8])
                hh, mm = int(ts) // 100, int(ts) % 100
                try:
                    dt = datetime(y, m, d, hh, mm, tzinfo=timezone.utc)
                except ValueError:
                    continue
                idx = int((dt.timestamp() - t0) / 3600)
                if 0 <= idx < n_hours:
                    gravity[idx] = res
    return gravity, n_hours


def get_solar(lat, lon, year):
    cache = DATA_DIR / f"solar_{lat:.2f}_{lon:.2f}_{year}.json"
    if cache.exists():
        with open(cache) as f:
            return json.load(f)
    import requests
    url = (f"https://power.larc.nasa.gov/api/temporal/hourly/point?"
           f"parameters=ALLSKY_SFC_SW_DWN&community=RE"
           f"&longitude={lon}&latitude={lat}"
           f"&start={year}0101&end={year}1231&format=JSON")
    print(f"  Downloading solar ({lat:.1f}N, {lon:.1f}E) {year}...")
    r = requests.get(url, timeout=120)
    r.raise_for_status()
    sd = r.json()["properties"]["parameter"]["ALLSKY_SFC_SW_DWN"]
    with open(cache, "w") as f:
        json.dump(sd, f)
    return sd


def solar_to_array(sd, year):
    is_leap = (year % 4 == 0 and year % 100 != 0) or year % 400 == 0
    n = 8784 if is_leap else 8760
    solar = np.zeros(n)
    for k, v in sd.items():
        if v < -900:
            continue
        try:
            dt = datetime(int(k[:4]), int(k[4:6]), int(k[6:8]),
                          int(k[8:10]), tzinfo=timezone.utc)
        except (ValueError, IndexError):
            continue
        t0 = datetime(year, 1, 1, tzinfo=timezone.utc)
        idx = int((dt - t0).total_seconds() / 3600)
        if 0 <= idx < n:
            solar[idx] = v
    return solar


def detrend(g, h, yr):
    dt = g.copy()
    for month in range(1, 13):
        db = sum(calendar.monthrange(yr, m)[1] for m in range(1, month))
        di = calendar.monthrange(yr, month)[1]
        mask = (h >= db * 24) & (h < (db + di) * 24)
        if mask.sum() > 0:
            dt[mask] -= g[mask].mean()
    return dt


def analyze(sname, sinfo, year):
    grav, n_hours = parse_ggp_year(sinfo["dir"], sinfo["pat"], year)
    n_valid = np.sum(~np.isnan(grav))
    if n_valid < 1000:
        return None

    sd = get_solar(sinfo["lat"], sinfo["lon"], year)
    solar = solar_to_array(sd, year)

    both = ~np.isnan(grav) & (solar >= 0)
    hrs = np.arange(n_hours, dtype=float)[both]
    g = grav[both]
    s = solar[both]
    n = len(g)
    gd = detrend(g, hrs, year)

    day = s > 50
    night = s <= 50
    g_day = gd[day]
    g_night = gd[night]
    diff = g_day.mean() - g_night.mean()
    se = np.sqrt(g_day.var() / len(g_day) + g_night.var() / len(g_night))
    t_stat = diff / (se + 1e-15)
    p_val = None
    if stats:
        _, p_val = stats.ttest_ind(g_day, g_night, equal_var=False)

    # Correlation
    r_corr = np.corrcoef(gd, s)[0, 1]

    # Hourly mean by time of day
    hod = (hrs % 24).astype(int)
    hourly_means = np.array([gd[hod == h].mean() for h in range(24)])
    hourly_sems = np.array([gd[hod == h].std() / np.sqrt((hod == h).sum())
                            for h in range(24)])
    solar_hourly = np.array([s[hod == h].mean() for h in range(24)])

    # Seasonal
    seasons = {}
    for sn, months in [("Winter", [1, 2, 11, 12]), ("Spring", [3, 4, 5]),
                        ("Summer", [6, 7, 8]), ("Autumn", [9, 10])]:
        sm = np.zeros(n, dtype=bool)
        for m in months:
            db = sum(calendar.monthrange(year, mm)[1] for mm in range(1, m))
            di = calendar.monthrange(year, m)[1]
            sm |= (hrs >= db * 24) & (hrs < (db + di) * 24)
        sd2 = gd[sm & day]
        sn3 = gd[sm & night]
        if len(sd2) > 10 and len(sn3) > 10:
            sdiff = sd2.mean() - sn3.mean()
            sse = np.sqrt(sd2.var() / len(sd2) + sn3.var() / len(sn3))
            st = sdiff / (sse + 1e-15)
            sp = None
            if stats:
                _, sp = stats.ttest_ind(sd2, sn3, equal_var=False)
            seasons[sn] = {"diff": sdiff, "t": st, "p": sp,
                           "n_day": len(sd2), "n_night": len(sn3)}

    return {
        "station": sname, "year": year, "n": n, "diff": diff, "se": se,
        "t": t_stat, "p": p_val, "r": r_corr,
        "n_day": len(g_day), "n_night": len(g_night),
        "hourly_means": hourly_means, "hourly_sems": hourly_sems,
        "solar_hourly": solar_hourly,
        "seasons": seasons,
    }


# ===== Main =====

years = [2019, 2020]

print("=" * 70)
print("ZUGSPITZE vs MEMBACH: Surface High-Altitude vs Underground")
print("=" * 70)
for sn, si in STATIONS.items():
    print(f"  {sn}: {si['lat']:.2f}N, {si['lon']:.2f}E, {si['elev']}m, {si['type']}")
print(f"  Years: {years}")
print()

all_results = []
for year in years:
    print(f"--- {year} ---")
    for sname, sinfo in STATIONS.items():
        r = analyze(sname, sinfo, year)
        if r is None:
            print(f"  {sname}: SKIP (insufficient data)")
            continue
        sig = " *" if r["p"] and r["p"] < 0.05 else ""
        p_str = f"p={r['p']:.4f}" if r["p"] else ""
        print(f"  {sname:12s}: n={r['n']:5d} diff={r['diff']:+.4f} "
              f"t={r['t']:.3f} r={r['r']:+.6f} {p_str}{sig}")
        all_results.append(r)

# Summary
print()
print("=" * 70)
print("COMPARISON SUMMARY")
print("=" * 70)
for sname in STATIONS:
    rs = [r for r in all_results if r["station"] == sname]
    if not rs:
        continue
    diffs = [r["diff"] for r in rs]
    m = np.mean(diffs)
    se = np.std(diffs) / np.sqrt(len(diffs)) if len(diffs) > 1 else abs(diffs[0])
    t = m / (se + 1e-15) if se > 0 else 0
    print(f"{sname} ({STATIONS[sname]['type']}):")
    print(f"  Combined: {m:+.4f} +/- {se:.4f} nm/s^2  t={t:.2f}")
    for sn2 in ["Winter", "Spring", "Summer", "Autumn"]:
        vals = [r["seasons"][sn2]["diff"] for r in rs if sn2 in r["seasons"]]
        if vals:
            sm = np.mean(vals)
            sse = np.std(vals) / np.sqrt(len(vals)) if len(vals) > 1 else abs(vals[0])
            st = sm / (sse + 1e-15) if sse > 0 else 0
            print(f"    {sn2:8s}: {sm:+.4f} +/- {sse:.4f}  t={st:.2f}")
    print()

zug = [r["diff"] for r in all_results if r["station"] == "Zugspitze"]
mem = [r["diff"] for r in all_results if r["station"] == "Membach"]

print("KEY COMPARISON:")
print(f"  Zugspitze (surface 2939m): {np.mean(zug):+.4f} nm/s^2")
print(f"  Membach   (underground):   {np.mean(mem):+.4f} nm/s^2")
print(f"  Difference:                {np.mean(zug) - np.mean(mem):+.4f} nm/s^2")
print()
print("INTERPRETATION:")
print("  If solar radiation affects gravity (tick-frame prediction),")
print("  Zugspitze (surface, max solar exposure) should show LARGER")
print("  signal than Membach (underground, shielded from direct solar).")

zug_m = np.mean(zug)
mem_m = np.mean(mem)
if zug_m > 0 and mem_m > 0 and zug_m > mem_m * 1.5:
    print("  -> Zugspitze IS larger and positive. Directionally consistent.")
    print("     But check if significant.")
elif abs(zug_m) < 0.03 and abs(mem_m) < 0.03:
    print("  -> Both near zero. No signal at either environment.")
else:
    print(f"  -> Zugspitze={zug_m:+.4f}, Membach={mem_m:+.4f}. No clear pattern.")

# === Plots ===
print("\n--- Generating plots ---")

fig, axes = plt.subplots(2, 2, figsize=(14, 10))

# 1. Diurnal pattern comparison
ax = axes[0, 0]
for sname, color, marker in [("Zugspitze", "#d9534f", "s"), ("Membach", "#5bc0de", "o")]:
    rs = [r for r in all_results if r["station"] == sname]
    if not rs:
        continue
    means = np.mean([r["hourly_means"] for r in rs], axis=0)
    sems = np.mean([r["hourly_sems"] for r in rs], axis=0)
    ax.errorbar(range(24), means, yerr=sems, fmt=f"{marker}-", color=color,
                markersize=4, linewidth=1.5, capsize=2, label=sname)
ax.axhline(0, color="gray", linestyle="--", alpha=0.5)
ax.set_xlabel("Hour of day (UTC)")
ax.set_ylabel("Mean detrended L3 residual (nm/s^2)")
ax.set_title("Diurnal Gravity Pattern (2019-2020 mean)")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# Solar overlay
ax2 = ax.twinx()
for sname, color in [("Zugspitze", "#d9534f"), ("Membach", "#5bc0de")]:
    rs = [r for r in all_results if r["station"] == sname]
    if rs:
        sol = np.mean([r["solar_hourly"] for r in rs], axis=0)
        ax2.plot(range(24), sol, color=color, linestyle=":", alpha=0.4)
ax2.set_ylabel("Solar (W/m^2)", alpha=0.5)

# 2. Year-by-year comparison
ax = axes[0, 1]
for sname, color in [("Zugspitze", "#d9534f"), ("Membach", "#5bc0de")]:
    rs = [r for r in all_results if r["station"] == sname]
    yrs = [r["year"] for r in rs]
    dfs = [r["diff"] for r in rs]
    ses = [r["se"] for r in rs]
    ax.errorbar(yrs, dfs, yerr=ses, fmt="o-", color=color, capsize=5,
                markersize=8, linewidth=2, label=sname)
ax.axhline(0, color="gray", linestyle="--")
ax.set_xlabel("Year")
ax.set_ylabel("Day-Night difference (nm/s^2)")
ax.set_title("Year-by-Year Comparison")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3)

# 3. Seasonal comparison
ax = axes[1, 0]
season_names = ["Winter", "Spring", "Summer", "Autumn"]
x = np.arange(len(season_names))
width = 0.35
for i, (sname, color) in enumerate([("Zugspitze", "#d9534f"), ("Membach", "#5bc0de")]):
    rs = [r for r in all_results if r["station"] == sname]
    means = []
    errs = []
    for sn2 in season_names:
        vals = [r["seasons"][sn2]["diff"] for r in rs if sn2 in r["seasons"]]
        means.append(np.mean(vals) if vals else 0)
        errs.append(np.std(vals) / np.sqrt(len(vals)) if len(vals) > 1 else 0)
    ax.bar(x + i * width - width / 2, means, width, yerr=errs, capsize=3,
           color=color, edgecolor="black", label=sname)
ax.axhline(0, color="gray", linestyle="--")
ax.set_xticks(x)
ax.set_xticklabels(season_names)
ax.set_ylabel("Day-Night diff (nm/s^2)")
ax.set_title("Seasonal: Zugspitze vs Membach")
ax.legend(fontsize=9)
ax.grid(True, alpha=0.3, axis="y")

# 4. Station comparison bar
ax = axes[1, 1]
snames = list(STATIONS.keys())
means = []
errs = []
for sname in snames:
    rs = [r["diff"] for r in all_results if r["station"] == sname]
    means.append(np.mean(rs) if rs else 0)
    errs.append(np.std(rs) / np.sqrt(len(rs)) if len(rs) > 1 else 0)
colors = ["#d9534f", "#5bc0de"]
ax.bar(snames, means, yerr=errs, capsize=5, color=colors, edgecolor="black")
ax.axhline(0, color="gray", linestyle="--")
ax.set_ylabel("Day-Night diff (nm/s^2)")
ax.set_title("Overall: Surface vs Underground")
ax.grid(True, alpha=0.3, axis="y")

fig.suptitle("Zugspitze (2939m surface) vs Membach (underground)",
             fontweight="bold", fontsize=14)
fig.tight_layout()
fig.savefig(RESULTS_DIR / "zugspitze_vs_membach.png", dpi=150)
print(f"  Saved: {RESULTS_DIR / 'zugspitze_vs_membach.png'}")
plt.close()

print("\nDone.")
