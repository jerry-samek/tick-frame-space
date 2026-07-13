"""Inspect the 2/100 Phase 1 seeds with max_age > 1000 in the post-fix run."""
import json
from pathlib import Path

d = json.loads(Path("skeptic_pass_results.json").read_text())
rows = d["phase1"]["rows"]

outliers = sorted(
    [(r["seed"], r["max_consumed_age"], r["max_pending_observed"], r["n_spawned"],
      r["n_in_flight_at_end"], r["n_pending_at_end"])
     for r in rows if r["max_consumed_age"] > 1000],
    key=lambda x: -x[1],
)
print("Phase 1 outliers (max_age > 1000) post-fix:")
print(f"  {'seed':>5}  {'max_age':>8}  {'max_pending':>12}  {'n_spawned':>10}  {'in_flight':>10}  {'pending_end':>12}")
for seed, age, pend, spawn, infl, pend_end in outliers:
    print(f"  {seed:>5}  {age:>8}  {pend:>12}  {spawn:>10}  {infl:>10}  {pend_end:>12}")

# How does post-fix compare to the rest of the distribution?
import statistics
ages = [r["max_consumed_age"] for r in rows]
print(f"\nFull distribution: median={statistics.median(ages):.0f}, "
      f"95th={sorted(ages)[94]}, 99th={sorted(ages)[98]}, max={max(ages)}")
print(f"Outliers ({len(outliers)}/100) are all > 1000; rest are <= {sorted(ages)[97]}")

# Phase 4 threshold=200 post-fix picture
p4t200 = d["phase4_threshold200"]["rows"]
print("\nPhase 4 threshold=200 (revert) post-fix:")
from collections import Counter
print(f"  n_crystallized: {Counter(r['n_crystallized'] for r in p4t200)}")
print(f"  distinct_spectra: {Counter(r['distinct_spectra'] for r in p4t200)}")
print(f"  n_spawned: {Counter(r['n_spawned'] for r in p4t200)}")
print(f"  has_known: {sum(1 for r in p4t200 if r['has_known_token_spawn'])}/100")
print(f"  has_dup: {sum(1 for r in p4t200 if r['has_duplicate_spawn'])}/100")

# Phase 4 STAR per-token spawn count
p4s = d["phase4_star"]["rows"]
seed42_star = p4s[42]
print(f"\nPhase 4 STAR seed=42 spawn_tokens: {seed42_star['spawn_tokens']}")
from collections import Counter
print(f"  per-token count: {Counter(seed42_star['spawn_tokens'])}")

# Check: in Phase 4 ring outliers (n_spawned=4), is it really c0 observer that absorbed?
p4 = d["phase4"]["rows"]
nspawn_4_seeds = [r for r in p4 if r["n_spawned"] == 4]
print(f"\nPhase 4 n_spawned == 4 in {len(nspawn_4_seeds)} seeds. Verifying c0-observer absorption hypothesis:")
for r in nspawn_4_seeds:
    spawn_set = set(r["spawn_tokens"])
    expected = {6, 7, 8, 9, 10}
    missing = expected - spawn_set
    obs_c0_spec = set(r["per_observer_spectrum"][0])
    other_obs = [set(s) for s in r["per_observer_spectrum"][1:]]
    abs_at_c0 = missing & obs_c0_spec
    abs_elsewhere = [missing & s for s in other_obs if missing & s]
    print(f"  seed={r['seed']}: missing={missing} obs_c0={obs_c0_spec} other_obs_with_missing={abs_elsewhere}")
