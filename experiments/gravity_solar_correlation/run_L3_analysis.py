"""Level 3 gravity-solar correlation analysis — the real test.

Onsala SG054 Level 3 residuals: tides, atmospheric pressure, polar motion,
ocean loading, and instrument drift ALL removed. What remains should be
white noise if classical physics is complete.

Any correlation with solar irradiance in these residuals would be genuinely
unexplained by classical corrections.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"

data = np.load(DATA_DIR / 'onsala_2016_L3_aligned.npz')
gravity = data['gravity_nms2']
solar = data['solar_wm2']
hours = data['hours']
n = len(gravity)

print("=" * 70)
print("LEVEL 3 ANALYSIS: Onsala SG054 vs Solar Irradiance (2016)")
print("  Corrections applied: tides, atm pressure, polar motion,")
print("  ocean loading, drift (DDW99+HW95/FES2014c, ERA5/IB)")
print("=" * 70)
print(f"Data: {n} hours")
print(f"Gravity L3: mean={gravity.mean():.3f}, std={gravity.std():.3f} nm/s^2")
print(f"Solar: {np.sum(solar > 50)} daytime hours, mean={solar[solar>50].mean():.1f} W/m^2")
print()

# === 1. Direct correlation ===
print("--- Direct Correlation ---")
actual_r = np.corrcoef(gravity, solar)[0, 1]
print(f"  Pearson r = {actual_r:.6f}")

# === 2. Bootstrap ===
print("--- Bootstrap (n=5000) ---")
rng = np.random.default_rng(42)
null_corrs = np.array([np.corrcoef(gravity, rng.permutation(solar))[0, 1]
                        for _ in range(5000)])
p_boot = np.mean(np.abs(null_corrs) >= np.abs(actual_r))
print(f"  Null: mean={np.mean(null_corrs):.6f}, std={np.std(null_corrs):.6f}")
print(f"  |actual r| = {abs(actual_r):.6f}")
print(f"  Bootstrap p = {p_boot:.4f}")
if p_boot < 0.05:
    print(f"  ** SIGNIFICANT at p < 0.05 **")
elif p_boot < 0.10:
    print(f"  * Marginal (0.05 < p < 0.10) *")
else:
    print(f"  Not significant")

# === 3. Cross-correlation ===
print("--- Cross-Correlation ---")
max_lag = 72
gn = (gravity - np.mean(gravity)) / (np.std(gravity) + 1e-15)
sn = (solar - np.mean(solar)) / (np.std(solar) + 1e-15)
lags = np.arange(-max_lag, max_lag + 1)
corr = np.zeros(len(lags))
for i, l in enumerate(lags):
    if l >= 0:
        corr[i] = np.mean(gn[:n-l] * sn[l:])
    else:
        corr[i] = np.mean(gn[-l:] * sn[:n+l])
zero_lag = corr[lags == 0][0]
peak_idx = np.argmax(np.abs(corr))
print(f"  Zero-lag r = {zero_lag:.6f}")
print(f"  Peak |r| = {corr[peak_idx]:.6f} at lag = {lags[peak_idx]}h")

# === 4. Day vs Night ===
print("--- Day vs Night ---")
day_mask = solar > 50
night_mask = solar <= 50
g_day = gravity[day_mask]
g_night = gravity[night_mask]
diff = np.mean(g_day) - np.mean(g_night)
se = np.sqrt(np.var(g_day)/len(g_day) + np.var(g_night)/len(g_night))
t_stat = diff / (se + 1e-15)
print(f"  Day:   {np.mean(g_day):+.4f} +/- {np.std(g_day):.3f} nm/s^2 (n={len(g_day)})")
print(f"  Night: {np.mean(g_night):+.4f} +/- {np.std(g_night):.3f} nm/s^2 (n={len(g_night)})")
print(f"  Difference: {diff:+.4f} nm/s^2")
print(f"  t = {t_stat:.4f}")
# Proper p-value from scipy if available, else approximate
try:
    from scipy import stats
    _, p_ttest = stats.ttest_ind(g_day, g_night, equal_var=False)
    print(f"  p (Welch t-test) = {p_ttest:.6f}")
    if p_ttest < 0.05:
        print(f"  ** SIGNIFICANT at p < 0.05 **")
    else:
        print(f"  Not significant")
except ImportError:
    p_ttest = None
    print(f"  (scipy not available for exact p-value)")

# === 5. FFT ===
print("--- FFT ---")
fft_g = np.fft.rfft(gravity - np.mean(gravity))
fft_s = np.fft.rfft(solar - np.mean(solar))
freqs = np.fft.rfftfreq(n, d=1.0)
amps_g = 2 * np.abs(fft_g) / n
amps_s = 2 * np.abs(fft_s) / n
periods = np.zeros_like(freqs)
periods[1:] = 1.0 / freqs[1:]
for target in [24.0, 12.0, 8.0, 6.0]:
    idx = np.argmin(np.abs(periods - target))
    print(f"  {target:.0f}h: gravity={amps_g[idx]:.4f} nm/s^2, solar={amps_s[idx]:.1f} W/m^2")

# === 6. Seasonal breakdown ===
print("--- Seasonal Day-Night (Summer vs Winter) ---")
# Summer: May-Aug (hours 2880-5856), Winter: Nov-Feb (hours 0-1416 + 7320-8784)
for season, mask_func in [
    ("Summer (May-Aug)", lambda h: (h >= 2880) & (h < 5856)),
    ("Winter (Nov-Feb)", lambda h: (h < 1416) | (h >= 7320)),
]:
    season_mask = mask_func(hours)
    s_day = gravity[season_mask & day_mask]
    s_night = gravity[season_mask & night_mask]
    if len(s_day) > 10 and len(s_night) > 10:
        s_diff = np.mean(s_day) - np.mean(s_night)
        print(f"  {season}: day={np.mean(s_day):+.3f}, night={np.mean(s_night):+.3f}, "
              f"diff={s_diff:+.4f} nm/s^2 (n_day={len(s_day)}, n_night={len(s_night)})")

# === PLOTS ===
print("\n--- Generating Plots ---")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 1. Cross-correlation
ax = axes[0, 0]
ax.plot(lags, corr, 'b-', linewidth=1.5)
ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.axvline(0, color='red', linestyle=':', alpha=0.5)
# Significance bounds (approximate 95% CI for white noise)
sig_bound = 1.96 / np.sqrt(n)
ax.axhline(sig_bound, color='green', linestyle=':', alpha=0.5, label=f'95% CI (+/-{sig_bound:.4f})')
ax.axhline(-sig_bound, color='green', linestyle=':', alpha=0.5)
ax.set_xlabel('Lag (hours)')
ax.set_ylabel('Cross-correlation')
ax.set_title(f'Cross-Correlation (r={zero_lag:.5f})')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 2. FFT gravity L3
ax = axes[0, 1]
mask = (periods > 4) & (periods < 200)
ax.plot(periods[mask], amps_g[mask], 'b-', linewidth=0.8)
for p in [12, 24, 48]:
    ax.axvline(p, color='red', linestyle=':', alpha=0.4, label=f'{p}h')
ax.set_xlabel('Period (hours)')
ax.set_ylabel('Amplitude (nm/s^2)')
ax.set_title('L3 Gravity Residual FFT')
ax.set_xscale('log')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 3. Day vs Night
ax = axes[0, 2]
ax.bar(['Day (>50 W/m2)', 'Night'],
       [np.mean(g_day), np.mean(g_night)],
       yerr=[np.std(g_day)/np.sqrt(len(g_day)),
             np.std(g_night)/np.sqrt(len(g_night))],
       capsize=5, color=['#f0ad4e', '#5bc0de'], edgecolor='black')
ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.set_ylabel('Mean L3 residual (nm/s^2)')
ax.set_title(f'Day vs Night (diff={diff:+.4f}, t={t_stat:.2f})')
ax.grid(True, alpha=0.3, axis='y')

# 4. Bootstrap null
ax = axes[1, 0]
ax.hist(null_corrs, bins=60, alpha=0.7, color='gray', label='null (n=5000)')
ax.axvline(actual_r, color='red', linewidth=2, label=f'actual r={actual_r:.5f}')
ax.axvline(-abs(actual_r), color='red', linewidth=1, linestyle=':', alpha=0.5)
ax.set_xlabel('Correlation')
ax.set_ylabel('Count')
ax.set_title(f'Bootstrap (p={p_boot:.4f})')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 5. Scatter: gravity vs solar (hourly)
ax = axes[1, 1]
daytime = solar > 10
ax.scatter(solar[daytime], gravity[daytime], s=1, alpha=0.2, color='orange')
ax.scatter(solar[~daytime], gravity[~daytime], s=1, alpha=0.1, color='blue')
# Linear fit
if np.sum(daytime) > 10:
    z = np.polyfit(solar[daytime], gravity[daytime], 1)
    x_fit = np.linspace(10, solar.max(), 100)
    ax.plot(x_fit, np.polyval(z, x_fit), 'r-', linewidth=2,
            label=f'slope={z[0]:.6f} nm/s^2 per W/m^2')
ax.set_xlabel('Solar irradiance (W/m^2)')
ax.set_ylabel('L3 gravity residual (nm/s^2)')
ax.set_title('Scatter: Gravity vs Solar')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 6. Time series (1 month, summer for best solar contrast)
ax = axes[1, 2]
june_mask = (hours >= 3624) & (hours < 4344)  # June 2016
ax2 = ax.twinx()
ax.plot(hours[june_mask] - 3624, gravity[june_mask], 'b-', linewidth=0.5, alpha=0.7)
ax2.plot(hours[june_mask] - 3624, solar[june_mask], 'orange', linewidth=0.5, alpha=0.7)
ax.set_xlabel('Hours (June 2016)')
ax.set_ylabel('L3 residual (nm/s^2)', color='blue')
ax2.set_ylabel('Solar (W/m^2)', color='orange')
ax.set_title('June 2016: L3 Gravity + Solar')
ax.grid(True, alpha=0.3)

fig.suptitle('Onsala SG054 LEVEL 3: Gravity-Solar Correlation (2016)',
             fontweight='bold', fontsize=14)
fig.tight_layout()
out = RESULTS_DIR / 'onsala_2016_L3_analysis.png'
fig.savefig(out, dpi=150)
print(f"  Saved: {out}")
plt.close()

# === Summary ===
print(f"\n{'='*70}")
print("LEVEL 3 RESULT SUMMARY")
print(f"{'='*70}")
print(f"  Correlation:       r = {actual_r:+.6f}")
print(f"  Bootstrap p:       {p_boot:.4f}")
print(f"  Day-night diff:    {diff:+.4f} nm/s^2 (t={t_stat:.3f})")
print(f"  24h FFT amplitude: {amps_g[np.argmin(np.abs(periods-24))]:.4f} nm/s^2")
print(f"  Direction:         {'POSITIVE (tick-frame consistent)' if actual_r > 0 else 'NEGATIVE (opposite to prediction)'}")
print(f"  Significance:      {'SIGNIFICANT' if p_boot < 0.05 else 'NOT significant'}")
print()
print("  Corrections removed: tides (DDW99+HW95/FES2014c), atmospheric")
print("  pressure (ERA5/IB), polar motion+LOD, ocean loading, drift")
print(f"{'='*70}")
