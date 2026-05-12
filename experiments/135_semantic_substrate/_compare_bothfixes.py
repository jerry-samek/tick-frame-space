import json, statistics
from pathlib import Path
from collections import Counter
d = json.loads(Path("skeptic_pass_results.json").read_text())

print("=== seed=42 with both fixes ===")
p1 = next(r for r in d["phase1"]["rows"] if r["seed"]==42)
p4 = next(r for r in d["phase4"]["rows"] if r["seed"]==42)
print(f"Phase 1: n_spawned={p1['n_spawned']}, max_age={p1['max_consumed_age']}, max_pending={p1['max_pending_observed']}")
print(f"Phase 4: n_crystallized={p4['n_crystallized']}, distinct_spectra={p4['distinct_spectra']}")
print(f"Phase 4: n_spawned={p4['n_spawned']}, spawn_tokens={p4['spawn_tokens']}")
print(f"Phase 4: has_known={p4['has_known_token_spawn']}, has_dup={p4['has_duplicate_spawn']}")
print(f"Phase 4: per_observer_spectrum={p4['per_observer_spectrum']}")

print("\n=== Pre-fix vs Post-fix (100 seeds each) ===")
print(f"{'Metric':<48} {'Pre-fix':<18} {'Post-fix':<18}")
print(f"{'-'*84}")
rows_to_show = [
    ("Phase 4: known-token spawn",         "59/100",  f"{sum(1 for r in d['phase4']['rows'] if r['has_known_token_spawn'])}/100"),
    ("Phase 4: duplicate spawn",            "29/100",  f"{sum(1 for r in d['phase4']['rows'] if r['has_duplicate_spawn'])}/100"),
    ("Phase 4: n_spawned == 5",             "35/100",  f"{sum(1 for r in d['phase4']['rows'] if r['n_spawned']==5)}/100"),
    ("Phase 4: distinct_spectra >= 3",      "89/100",  f"{sum(1 for r in d['phase4']['rows'] if r['distinct_spectra']>=3)}/100"),
    ("Phase 4: all 6 crystallize",          "0/100",   f"{sum(1 for r in d['phase4']['rows'] if r['n_crystallized']==6)}/100"),
    ("Phase 4 STAR: all 6 crystallize",     "0/100",   f"{sum(1 for r in d['phase4_star']['rows'] if r['n_crystallized']==6)}/100"),
    ("Phase 4 STAR: ring intact",           "100/100", f"{sum(1 for r in d['phase4_star']['rows'] if r['ring_intact'])}/100"),
    ("Phase 4 STAR: known-token spawn",     "0/100",   f"{sum(1 for r in d['phase4_star']['rows'] if r['has_known_token_spawn'])}/100"),
    ("Phase 4 STAR: duplicate spawn",       "100/100", f"{sum(1 for r in d['phase4_star']['rows'] if r['has_duplicate_spawn'])}/100"),
    ("Phase 1: ring intact",                "100/100", f"{sum(1 for r in d['phase1']['rows'] if r['ring_intact'])}/100"),
    ("Phase 1: n_spawned == 5",             "67/100",  f"{sum(1 for r in d['phase1']['rows'] if r['n_spawned']==5)}/100"),
    ("Phase 1: max_age > 1000",             "34/100",  f"{sum(1 for r in d['phase1']['rows'] if r['max_consumed_age']>1000)}/100"),
    ("Phase 1: max_pending > 20",           "34/100",  f"{sum(1 for r in d['phase1']['rows'] if r['max_pending_observed']>20)}/100"),
    ("Phase 3: n_spawned == 5",             "80/100",  f"{sum(1 for r in d['phase3']['rows'] if r['n_spawned']==5)}/100"),
    ("Phase 3: spectrum {2,3,4} reproduce", "99/100",  f"{sum(1 for r in d['phase3']['rows'] if tuple(r['observer_spectrum'])==(2,3,4))}/100"),
    ("Phase 3: strict known-routing >= 95%", "0/100",   f"{sum(1 for r in d['phase3']['rows'] if r['n_known_consumed'] and r['known_strict_correct']/r['n_known_consumed']>=0.95)}/100"),
    ("Phase 2 ORIGINAL: all-cells-pass",    "19/100",  f"{sum(1 for r in d['phase2_original']['rows'] if r['all_match'])}/100"),
]
for label, before, after in rows_to_show:
    print(f"{label:<48} {before:<18} {after:<18}")

print("\n=== Phase 1 max_age summary (post-fix) ===")
ages = [r["max_consumed_age"] for r in d["phase1"]["rows"]]
print(f"  median={statistics.median(ages)}, max={max(ages)}, mean={statistics.mean(ages):.1f}, std={statistics.stdev(ages):.1f}")
print(f"  Pre-fix: median=526, max=6560, mean=1346.2, std=1566.6")
