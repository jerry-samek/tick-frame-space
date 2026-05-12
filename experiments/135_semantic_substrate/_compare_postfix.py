import json
from pathlib import Path
d = json.loads(Path("skeptic_pass_results.json").read_text())

print("=== seed=42 after fix ===")
p1 = next(r for r in d["phase1"]["rows"] if r["seed"]==42)
p4 = next(r for r in d["phase4"]["rows"] if r["seed"]==42)
print(f"Phase 1: n_spawned={p1['n_spawned']}, max_age={p1['max_consumed_age']}, max_pending={p1['max_pending_observed']}")
print(f"Phase 4: n_crystallized={p4['n_crystallized']}, distinct_spectra={p4['distinct_spectra']}")
print(f"Phase 4: n_spawned={p4['n_spawned']}, spawn_tokens={p4['spawn_tokens']}")
print(f"Phase 4: has_known={p4['has_known_token_spawn']}, has_dup={p4['has_duplicate_spawn']}")
print(f"Phase 4: per_observer_spectrum={p4['per_observer_spectrum']}")

print("\n=== Before/After comparison ===")
print(f"{'Metric':<40} {'Before fix':<20} {'After fix':<20}")
print(f"{'-'*80}")
rows = [
    ("Phase 4: has_known_token_spawn", "59/100", f"{sum(1 for r in d['phase4']['rows'] if r['has_known_token_spawn'])}/100"),
    ("Phase 4: has_duplicate_spawn", "29/100", f"{sum(1 for r in d['phase4']['rows'] if r['has_duplicate_spawn'])}/100"),
    ("Phase 4: n_spawned == 5 exact", "35/100", f"{sum(1 for r in d['phase4']['rows'] if r['n_spawned']==5)}/100"),
    ("Phase 4: all 6 crystallize", "0/100", f"{sum(1 for r in d['phase4']['rows'] if r['n_crystallized']==6)}/100"),
    ("Phase 4: distinct_spectra >= 3", "89/100", f"{sum(1 for r in d['phase4']['rows'] if r['distinct_spectra']>=3)}/100"),
    ("Phase 4 STAR: all 6 crystallize", "0/100", f"{sum(1 for r in d['phase4_star']['rows'] if r['n_crystallized']==6)}/100"),
    ("Phase 4 STAR: distinct_spectra median", "1", "median 4 (range 3-5)"),
    ("Phase 1: ring intact", "100/100", f"{sum(1 for r in d['phase1']['rows'] if r['ring_intact'])}/100"),
    ("Phase 1: n_spawned == 5 exact", "67/100", f"{sum(1 for r in d['phase1']['rows'] if r['n_spawned']==5)}/100"),
    ("Phase 1: max_age > 1000", "34/100", f"{sum(1 for r in d['phase1']['rows'] if r['max_consumed_age']>1000)}/100"),
]
for label, before, after in rows:
    print(f"{label:<40} {before:<20} {after:<20}")
