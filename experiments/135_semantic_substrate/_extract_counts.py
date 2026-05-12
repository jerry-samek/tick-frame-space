import json, sys
from pathlib import Path
d = json.loads(Path("skeptic_pass_results.json").read_text())

print("=== Phase 1 ===")
rows = d["phase1"]["rows"]
print(f"max_pending > 20:  {sum(1 for r in rows if r['max_pending_observed'] > 20)}/100")
print(f"max_pending > 50:  {sum(1 for r in rows if r['max_pending_observed'] > 50)}/100")
print(f"max_age > 339:     {sum(1 for r in rows if r['max_consumed_age'] > 339)}/100")
print(f"max_age > 1000:    {sum(1 for r in rows if r['max_consumed_age'] > 1000)}/100")
unresolved = sum(1 for r in rows if (r['n_in_flight_at_end'] + r['n_pending_at_end']) > 0.05 * (r['n_known_injected'] + r['n_unknown_injected']))
print(f"unresolved > 5%:   {unresolved}/100")
seed42 = next(r for r in rows if r["seed"]==42)
print(f"seed=42: n_spawned={seed42['n_spawned']} max_age={seed42['max_consumed_age']} max_pending={seed42['max_pending_observed']}")

print("\n=== Phase 4 default seed=42 ===")
p4d = d["phase4"]["rows"]
s42 = next(r for r in p4d if r["seed"]==42)
print(f"n_crystallized={s42['n_crystallized']}, distinct_spectra={s42['distinct_spectra']}")
print(f"n_spawned={s42['n_spawned']}, spawn_tokens={s42['spawn_tokens']}")
print(f"has_known_token_spawn={s42['has_known_token_spawn']}, has_duplicate_spawn={s42['has_duplicate_spawn']}")
print(f"per_observer_spectrum={s42['per_observer_spectrum']}")

print("\n=== Phase 2 ORIGINAL — failure pattern ===")
p2o = d["phase2_original"]["rows"]
print(f"all_match: {sum(1 for r in p2o if r['all_match'])}/100")
print(f"per_cell_match_rate: {[round(100*sum(r['per_cell_match'][i] for r in p2o)/100, 1) for i in range(5)]}")
# What are the typical wrong spectra?
from collections import Counter
spectra_per_cell = [Counter() for _ in range(5)]
for r in p2o:
    for i, s in enumerate(r["spectra"]):
        spectra_per_cell[i][tuple(s)] += 1
for i, c in enumerate(spectra_per_cell):
    print(f"  cell{i} top spectra: {c.most_common(3)}")

print("\n=== Phase 4 star — duplicate spawn structure ===")
p4s = d["phase4_star"]["rows"]
seed0 = p4s[0]
print(f"seed0 spawn_tokens={seed0['spawn_tokens']}")
print(f"seed0 per_observer_obs={seed0['per_observer_obs']}")
print(f"seed0 per_observer_state={seed0['per_observer_state']}")

print("\n=== Phase 3 spectrum stability ===")
p3 = d["phase3"]["rows"]
spec_counts = Counter(tuple(r["observer_spectrum"]) for r in p3)
print(f"observer_spectrum distribution: {spec_counts.most_common(5)}")
deviating_seed = next((r for r in p3 if tuple(r["observer_spectrum"]) != (2,3,4)), None)
if deviating_seed:
    print(f"deviating seed: {deviating_seed['seed']} -> {deviating_seed['observer_spectrum']}")

print("\n=== Baseline distinct_spectra distribution ===")
b = d["baseline_random_observers"]["rows"]
print(f"distinct_spectra distribution: {Counter(r['distinct_spectra'] for r in b).most_common()}")

print("\n=== Phase 4 default vs baseline — distinct_spectra side-by-side ===")
p4d = d["phase4"]["rows"]
print(f"Phase 4 distinct_spectra: {Counter(r['distinct_spectra'] for r in p4d).most_common()}")
print(f"Baseline distinct_spectra: {Counter(r['distinct_spectra'] for r in b).most_common()}")
import statistics
print(f"Phase 4 median distinct_spectra: {statistics.median(r['distinct_spectra'] for r in p4d)}")
print(f"Baseline median distinct_spectra: {statistics.median(r['distinct_spectra'] for r in b)}")
