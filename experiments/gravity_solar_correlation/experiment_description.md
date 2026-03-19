# Experiment: Gravity-Solar Radiation Correlation

**Date:** March 19, 2026
**Status:** Complete — NULL RESULT
**Result:** No detectable solar-gravity coupling at < 0.03 nm/s^2

---

## Hypothesis

If photons are `different` events propagating through deposit chains (RAW 113),
solar radiation should carry a gravitational signal. This would manifest as a
positive gravity residual during daytime, absent at night, in superconducting
gravimeter data after removing all classical effects.

**Tick-frame prediction:** positive correlation between solar irradiance and
gravity residuals in Level 3 corrected data.

**Classical prediction:** no correlation after standard corrections.

**Historical motivation:** Saxl & Allen (1971) Phys Rev D 3(4):823 reported
anomalous 5% gravity increase during the 1970 solar eclipse at Harvard.

---

## Data Sources

### Gravity: IGETS Level 3 Residuals

**Source:** International Geodynamics and Earth Tide Service (IGETS)
**Access:** https://isdc.gfz-potsdam.de/igets-data-base/ (free registration required)
**Format:** GGP (Global Geodynamics Project) ASCII files, hourly
**Processing:** IGETS Central Bureau (Jean-Paul Boy, Strasbourg)

Level 3 = gravity residuals with tides, atmospheric pressure, polar motion,
ocean loading, and drift corrections applied. The `res_fil` column is the
filtered residual — this is what we analyze.

#### Stations used

| Station | IGETS Code | Lat | Lon | Elev | Type | Instrument | Years |
|---------|-----------|-----|-----|------|------|------------|-------|
| Onsala | os054 | 57.39N | 11.93E | 8m | Coastal, surface | GWR OSG054 | 2014-2018 |
| Moxa (lower) | mo034-1 | 50.65N | 11.62E | 455m | Inland, underground | GWR CD034_L | 2014-2018 |
| Moxa (upper) | mo034-2 | 50.65N | 11.62E | 455m | Inland, underground | GWR CD034_U | 2014-2018 |
| Membach | mb021 | 50.61N | 6.01E | 250m | Inland, underground | GWR C021 | 2014-2020 |
| Zugspitze | zu052 | 47.42N | 10.98E | 2939m | Surface, Alpine peak | GWR OSG052 | 2019-2020 |

#### How to download

1. Register at https://isdc.gfz-potsdam.de/ (free, institutional email)
2. Navigate to IGETS data base
3. For each station, download Level 3 monthly files (RESMIN = residual minute/hourly)
4. File naming: `IGETS-SG-RESMIN-{code}-{YYYYMM}r2.ggp`
5. Place in `data/{Station}/{YYYY}/` directory structure

#### File format

```
yyyymmdd hhmmss   res_fil res_nofil     tides  rotation  atm_load     drift     g_fil     p_fil
77777777
20160101      0     8.793     8.793  -241.013    -7.770   -13.137   210.372   -42.755     8.926
20160101    100     8.908     8.908  -242.069    -7.771   -13.119   210.372   -43.679     8.917
```

- Column 1: date (YYYYMMDD)
- Column 2: time (HHMM00)
- Column 3: `res_fil` = **filtered residual** (what we analyze)
- Columns 4-10: individual correction components and raw gravity

#### Citations

- Onsala: Scherneck, H.-G. et al. (2022). doi:10.5880/igets.os.l1.001
- Moxa: Kroner, C. et al. GFZ Data Services
- Membach: Van Camp, M. et al. Royal Observatory of Belgium
- Zugspitze: Wziontek, H. et al. BKG Frankfurt

### Solar Irradiance: NASA POWER API

**Source:** NASA Prediction Of Worldwide Energy Resources
**Access:** https://power.larc.nasa.gov/ (no registration, free API)
**Parameter:** ALLSKY_SFC_SW_DWN (all-sky surface shortwave downward irradiance)
**Resolution:** Hourly
**Units:** W/m^2

#### API template

```
https://power.larc.nasa.gov/api/temporal/hourly/point?
  parameters=ALLSKY_SFC_SW_DWN
  &community=RE
  &longitude={LON}
  &latitude={LAT}
  &start={YYYY}0101
  &end={YYYY}1231
  &format=JSON
```

The analysis scripts automatically download and cache solar data per
station coordinates. No manual download needed — just run the scripts.

---

## Analysis Pipeline

### Scripts (in execution order)

| Script | Purpose | Input | Output |
|--------|---------|-------|--------|
| `analyze.py` | Synthetic pipeline + signal injection test | — | Validates detection capability |
| `run_L3_detrended.py` | Single-station (Onsala) multi-year | Onsala L3 | Identified seasonal artifact |
| `run_multi_station.py` | 4-instrument multi-station analysis | All L3 | **Main result: null at underground** |
| `run_zugspitze_membach.py` | Surface vs underground comparison | ZU + MB L3 | Surface confounds confirmed |

### Method

1. Parse GGP Level 3 files (`res_fil` column)
2. Subtract monthly mean from each hour (seasonal detrend)
3. Classify hours: day (solar > 50 W/m^2) vs night (solar <= 50)
4. Welch's t-test for day-night mean difference
5. Bootstrap significance (n=5000 permutations)
6. Seasonal breakdown (Winter/Spring/Summer/Autumn)
7. Dual-sphere test at Moxa (L vs U)
8. Cross-station consistency check

### Running the analysis

```bash
# Prerequisites
pip install numpy matplotlib scipy requests

# Step 1: Validate pipeline with synthetic data
python -u analyze.py --use-synthetic
python -u analyze.py --use-synthetic --inject-signal 20.0  # confirm detection

# Step 2: Multi-station analysis (requires IGETS data in data/ directory)
python -u run_multi_station.py --years 2014 2015 2016 2017 2018

# Step 3: Zugspitze vs Membach (exploratory)
python -u run_zugspitze_membach.py
```

### Required directory structure

```
data/
  Onsala/{year}/IGETS-SG-RESMIN-os054-{YYYYMM}r2.ggp
  Moxa/m1/{year}/IGETS-SG-RESMIN-mo034-1-{YYYYMM}r2.ggp
  Moxa/m2/{year}/IGETS-SG-RESMIN-mo034-2-{YYYYMM}r2.ggp
  Membach/{year}/IGETS-SG-RESMIN-mb021-{YYYYMM}r2.ggp
  Zugspitze/{year}/IGETS-SG-RESMIN-zu052-{YYYYMM}r2.ggp
```

Solar data is auto-downloaded and cached in `data/solar_*.json`.

---

## Results Summary

### Main result: NULL at underground stations

| Station | Type | Day-Night diff (nm/s^2) | t | Verdict |
|---------|------|------------------------|---|---------|
| Onsala | Coastal surface | +0.18 +/- 0.09 | 2.13 | Ocean loading artifact |
| Moxa-L | Underground | +0.03 +/- 0.01 | 4.63 | Instrumental systematic |
| Moxa-U | Underground | +0.02 +/- 0.01 | 1.57 | Not significant |
| Membach | Underground | -0.01 +/- 0.04 | -0.34 | Null |
| Zugspitze | Surface 2939m | +1.15 +/- 0.46 | 2.53 | Thermal/hydrological |

### How each signal was resolved

- **Onsala:** winter signal (+0.89) absent at inland stations = ocean loading
- **Moxa-L:** not replicated by Moxa-U (upper sphere, 20cm away) = instrumental
- **Zugspitze:** inverted seasonal pattern (winter > summer) = snow melt, not photon flux
- **Membach:** consistent with zero across all years and seasons

### Upper bound

**< 0.03 nm/s^2** at underground stations after Level 3 corrections.
Six orders of magnitude below Saxl & Allen's claimed 5% anomaly.

---

## Implications

1. **No evidence for solar-gravity coupling** at current gravimeter precision
2. **Saxl & Allen (1971) is not reproduced** by modern superconducting gravimeters
3. **The tick-frame prediction is not falsified** (magnitude was never quantified)
   but gains no support from this data
4. **Upper bound established:** any future prediction of photon-gravity coupling
   must be consistent with < 0.03 nm/s^2 at Earth's surface under solar flux
5. **Surface stations cannot test this hypothesis** — environmental confounds
   dominate by orders of magnitude

---

## Note on Data Availability

The IGETS gravity data requires a free registration at GFZ-ISDC and cannot
be redistributed. The solar data is freely available from NASA POWER API
and is auto-downloaded by the scripts. To reproduce:

1. Register at https://isdc.gfz-potsdam.de/
2. Download Level 3 RESMIN files for the stations listed above
3. Place in the directory structure shown above
4. Run the scripts — solar data downloads automatically

---

## References

- Saxl, E.J. & Allen, M. (1971) "1970 Solar Eclipse as 'Seen' by a Torsion
  Pendulum." Phys. Rev. D 3(4):823-825.
- Boy, J.-P. et al. IGETS Level 3 processing documentation.
  https://isdc.gfz-potsdam.de/igets-data-base/
- NASA POWER Project. https://power.larc.nasa.gov/
- RAW 113 — Semantic Isomorphism: Same/Different/Unknown (tick-frame theory)

---

*5 instruments, 4 stations (3 underground + 1 surface), 2014-2020*
*~220,000 station-hours of Level 3 corrected data analyzed*
*Result: NULL at < 0.03 nm/s^2*
