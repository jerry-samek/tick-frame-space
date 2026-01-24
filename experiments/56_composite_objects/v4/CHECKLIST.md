# CHECKLIST

## ✅ V4 Validated Physics Parameters (2026-01-24)

### ⚙️ Physics Parameters
- [x] **Proton mass & energy** scaled correctly (100.0 / 1000.0) ✓
- [x] **Electron total mass** reasonable (0.1 for 50 fragments) ✓
- [x] **Coupling constant** tuned (0.001 for smooth gradient force) ✓
- [x] **Jitter strength** balanced (0.0005 — CRITICAL: 0.001 causes runaway!) ✓
- [x] **Restitution** set for thermalization (0.8) ✓
- [x] **Collision radius** tuned (0.5 — optimal electron-like behavior, ~5 collisions/tick) ✓

---

### 🧪 Simulation Mechanics
- [x] **Gradient force** applied radially only ✓
- [x] **Collision detection** working (spatial collision_radius, not pattern_overlap) ✓
- [x] **Jitter injection** active every tick ✓
- [x] **Statistics update** includes KE, angular momentum, RMS radius ✓
- [x] **Field update interval** optimized (every 10 ticks) ✓

---

### 📊 Output & Analysis
- [x] **Snapshots** saved at regular intervals (every 200 ticks for 200k runs) ✓
- [x] **Phase space plot** enabled (radius vs KE) ✓
- [x] **Angular momentum tracking** active ✓
- [x] **Collision count logging** working ✓
- [x] **Drift threshold** set (<10% for validation) ✓
- [x] **Energy conservation tracking** (drift <5% for 200k ticks) ✓

---

### 🧠 Quantization Analysis (Completed)
- [x] **Energy histogram** for quantization test ✓
- [x] **Radial density profile** export for wavefunction comparison ✓
- [x] **Escape detection** logic active (check max radius) ✓
- [x] **Long tick count** validated (200k ticks) ✓
- [x] **Velocity distribution** analysis (Maxwell-Boltzmann test)
- [x] **Shell detection** algorithm (scipy peak finding)

---

## ✅ V4 Validation Results (2026-01-24)

### Critical Parameters Found
**OPTIMAL (200k tick stability)**:
- jitter_strength = **0.0005** (0.001 causes runaway!)
- collision_radius = **0.5** (electron-like, ~5 collisions/tick)

### 200k Tick Validation - PASSED ✓
- Cloud radius drift: **6.52%** (< 10% threshold)
- Energy conservation: **1.43%** drift (excellent)
- Fragments escaped: **0/50** (100% retention)
- Collision rate: **4.82/tick** (stable thermalization)
- Runtime: ~10 minutes

### Key Lessons Learned
1. **"Neutrino vs Electron" Insight**: Different collision parameters model different particle types
   - collision_radius=0.5 → ~5/tick (electron-like, strong binding)
   - pattern_overlap_threshold=0.01 → 0.01/tick (neutrino-like, weak interaction)
2. **Dual-Parameter System** (for V5): Separate spatial detection (when to check) from pattern overlap (collision type)
3. **Energy Balance Critical**: Jitter injection must be less than collision dissipation
4. **Collision Physics Validated**: Standard elastic collision formula is correct, energy conservation holds

---

## 📋 File References
- `FUTURE_IMPROVEMENTS.md` - Dual-parameter collision system for V5
- `PHASE_4_V4_RESULTS.md` - Complete analysis and findings
- `PHASE_4_V4_PLAN.md` - Original experimental design
- `results/exp56a_v4_50frags_200k.json` - Final successful 200k run (3.01 MB)
