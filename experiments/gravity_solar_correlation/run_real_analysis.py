"""Run real-data gravity-solar correlation analysis on Onsala SG054 data."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
DATA_DIR = Path(__file__).parent / "data"

data = np.load(DATA_DIR / 'onsala_2016_aligned.npz')
gravity = data['gravity_nms2']
solar = data['solar_wm2']
hours = data['hours']
n = len(gravity)

print("=" * 70)
print("REAL DATA ANALYSIS: Onsala SG054 Gravity vs Solar Irradiance (2016)")
print("=" * 70)
print(f"Data: {n} hours, Onsala Space Observatory (57.39N, 11.93E)")
print(f"Gravity: channel 0, range [{gravity.min():.3f}, {gravity.max():.3f}] nm/s^2")
print(f"Solar: NASA POWER ALLSKY_SFC_SW_DWN")
print()

# === 1. Cross-correlation ===
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
print(f"  Peak |r| = {corr[peak_idx]:.6f} at lag = {lags[peak_idx]} hours")

# === 2. Bootstrap significance ===
print("--- Bootstrap Significance (n=2000) ---")
rng = np.random.default_rng(42)
actual_r = np.corrcoef(gravity, solar)[0, 1]
null_corrs = np.array([np.corrcoef(gravity, rng.permutation(solar))[0, 1]
                        for _ in range(2000)])
p_boot = np.mean(np.abs(null_corrs) >= np.abs(actual_r))
print(f"  Actual r = {actual_r:.6f}")
print(f"  Null: mean={np.mean(null_corrs):.6f}, std={np.std(null_corrs):.6f}")
print(f"  Bootstrap p = {p_boot:.4f}")
if p_boot < 0.05:
    print("  ** SIGNIFICANT at p < 0.05 **")
else:
    print("  Not significant")

# === 3. Day vs Night ===
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
print(f"  t = {t_stat:.3f}")

# === 4. FFT ===
print("--- FFT ---")
fft_g = np.fft.rfft(gravity - np.mean(gravity))
fft_s = np.fft.rfft(solar - np.mean(solar))
freqs = np.fft.rfftfreq(n, d=1.0)
amps_g = 2 * np.abs(fft_g) / n
amps_s = 2 * np.abs(fft_s) / n
periods = np.zeros_like(freqs)
periods[1:] = 1.0 / freqs[1:]
for target in [24.0, 12.0, 8.0]:
    idx = np.argmin(np.abs(periods - target))
    print(f"  {target:.0f}h: gravity={amps_g[idx]:.4f} nm/s^2, solar={amps_s[idx]:.1f} W/m^2")

# === 5. Coherence ===
print("--- Coherence at key periods ---")
cross_spec = fft_g * np.conj(fft_s)
psd_g = np.abs(fft_g)**2
psd_s = np.abs(fft_s)**2
coherence = np.abs(cross_spec)**2 / (psd_g * psd_s + 1e-30)
for target in [24.0, 12.0, 8.0]:
    idx = np.argmin(np.abs(periods - target))
    phase = np.angle(cross_spec[idx]) * 180 / np.pi
    print(f"  {target:.0f}h: coherence={coherence[idx]:.6f}, phase={phase:.1f} deg")

# === PLOTS ===
print("--- Generating Plots ---")
fig, axes = plt.subplots(2, 3, figsize=(18, 10))

# 1. Cross-correlation
ax = axes[0, 0]
ax.plot(lags, corr, 'b-', linewidth=1.5)
ax.axhline(0, color='gray', linestyle='--', alpha=0.5)
ax.axvline(0, color='red', linestyle=':', alpha=0.5)
ax.set_xlabel('Lag (hours)')
ax.set_ylabel('Cross-correlation')
ax.set_title(f'Cross-Correlation (r={zero_lag:.5f})')
ax.grid(True, alpha=0.3)

# 2. FFT gravity
ax = axes[0, 1]
mask = (periods > 4) & (periods < 200)
ax.plot(periods[mask], amps_g[mask], 'b-', linewidth=0.8)
for p in [12, 24, 48]:
    ax.axvline(p, color='red', linestyle=':', alpha=0.4, label=f'{p}h')
ax.set_xlabel('Period (hours)')
ax.set_ylabel('Amplitude (nm/s^2)')
ax.set_title('Gravity FFT')
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
ax.set_ylabel('Mean gravity (nm/s^2)')
ax.set_title(f'Day vs Night (diff={diff:+.4f}, t={t_stat:.2f})')
ax.grid(True, alpha=0.3, axis='y')

# 4. Bootstrap null distribution
ax = axes[1, 0]
ax.hist(null_corrs, bins=50, alpha=0.7, color='gray', label='null')
ax.axvline(actual_r, color='red', linewidth=2, label=f'actual r={actual_r:.5f}')
ax.set_xlabel('Correlation')
ax.set_ylabel('Count')
ax.set_title(f'Bootstrap (p={p_boot:.4f}, n=2000)')
ax.legend(fontsize=8)
ax.grid(True, alpha=0.3)

# 5. Coherence spectrum
ax = axes[1, 1]
mask = (periods > 4) & (periods < 200)
ax.plot(periods[mask], coherence[mask], 'purple', linewidth=0.8)
for p in [12, 24, 48]:
    ax.axvline(p, color='red', linestyle=':', alpha=0.4)
ax.set_xlabel('Period (hours)')
ax.set_ylabel('Coherence^2')
ax.set_title('Gravity-Solar Coherence')
ax.set_xscale('log')
ax.grid(True, alpha=0.3)

# 6. Time series (1 month)
ax = axes[1, 2]
month = hours < 720
ax2 = ax.twinx()
ax.plot(hours[month], gravity[month], 'b-', linewidth=0.5, alpha=0.7)
ax2.plot(hours[month], solar[month], 'orange', linewidth=0.5, alpha=0.7)
ax.set_xlabel('Hours (Jan 2016)')
ax.set_ylabel('Gravity (nm/s^2)', color='blue')
ax2.set_ylabel('Solar (W/m^2)', color='orange')
ax.set_title('January 2016: Gravity + Solar')
ax.grid(True, alpha=0.3)

fig.suptitle('Onsala SG054: Gravity-Solar Correlation (2016, REAL DATA)',
             fontweight='bold', fontsize=14)
fig.tight_layout()
fig.savefig(RESULTS_DIR / 'onsala_2016_real_analysis.png', dpi=150)
print(f"  Saved: {RESULTS_DIR / 'onsala_2016_real_analysis.png'}")
plt.close()

# Summary
sig_corr = "SIGNIFICANT" if p_boot < 0.05 else "NOT significant"
print(f"\n{'='*70}")
print(f"RESULT: Correlation is {sig_corr} (r={actual_r:.6f}, p={p_boot:.4f})")
print(f"Day-night difference: {diff:+.4f} nm/s^2 (t={t_stat:.3f})")
print(f"24h coherence: {coherence[np.argmin(np.abs(periods - 24))]:.6f}")
print(f"{'='*70}")
