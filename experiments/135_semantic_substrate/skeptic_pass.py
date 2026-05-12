"""
Experiment 135 — Skeptic-pass harness.

Runs the tests the skeptic subagent demanded before any Phase 5:

  5a — Multi-seed sweep across phases 1-4 (100 seeds).
  5b — Do-nothing baseline: 6 fake observers fed uniform random tokens, top-1.
  5c — Adversarial fixtures: observer-attach permutation, star topology,
       null injection (only unknowns).
  5d — Goal-post reversion: Phase 2 at original (threshold=50, bias=[50,25,15,10]),
       Phase 3 reporting strict alongside semantic, Phase 4 at threshold=200.

All emit raw counts; aggregation/interpretation in RESULTS_skeptic_pass.md.
Single-script harness — no test framework, no per-test files. Output is a
JSON blob to skeptic_pass_results.json plus a human-readable text dump.
"""
from __future__ import annotations
import json
import random
import statistics
import sys
import time
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cell import Cell, Response, State
from substrate import Substrate
from fixture import Injector


# ----------------------------------------------------------------------------
# Fixture builders (reused / adversarial)
# ----------------------------------------------------------------------------

def build_k6_ring(substrate: Substrate) -> list[Cell]:
    cells = [Cell(spectrum={i}) for i in range(6)]
    for c in cells:
        substrate.add_cell(c)
    for i, c in enumerate(cells):
        prev_c = cells[(i - 1) % 6]
        next_c = cells[(i + 1) % 6]
        c.connectors.extend([prev_c, next_c])
    return cells


def build_k6_star(substrate: Substrate) -> list[Cell]:
    """c0 in centre, c1..c5 each connected only to c0 (no peripheral edges)."""
    cells = [Cell(spectrum={i}) for i in range(6)]
    for c in cells:
        substrate.add_cell(c)
    centre = cells[0]
    for c in cells[1:]:
        centre.connectors.append(c)
        c.connectors.append(centre)
    return cells


def attach_observer(
    substrate: Substrate, host: Cell,
    learning_threshold: int = 200, crystallization_size: int = 3,
) -> Cell:
    observer = Cell(
        spectrum=set(),
        learning_threshold=learning_threshold,
        crystallization_size=crystallization_size,
    )
    substrate.add_cell(observer)
    host.connectors.append(observer)
    observer.connectors.append(host)
    return observer


# ----------------------------------------------------------------------------
# Phase 1 run + measurement
# ----------------------------------------------------------------------------

def run_phase1(seed: int, n_ticks: int = 10_000, cadence: int = 15) -> dict:
    s = Substrate()
    ring = build_k6_ring(s)
    inj = Injector(seed=seed)
    n_known = 0
    n_unknown = 0
    max_pending_observed = 0

    for t in range(1, n_ticks + 1):
        if t % cadence == 1:
            tok = inj.next_token()
            s.inject(ring[0], token=tok)
            if tok < 6:
                n_known += 1
            else:
                n_unknown += 1
        s.tick()
        max_pending_observed = max(
            max_pending_observed,
            max((len(c.pending) for c in s.cells), default=0),
        )

    spawned = {child for (_, _, child, _) in s.spawn_log}
    spawn_spectra = sorted({tuple(sorted(c.spectrum)) for c in spawned})
    spawn_tokens = sorted({tok for (_, _, _, tok) in s.spawn_log})

    # Strict known routing: token i consumed at ring[i] specifically.
    known_strict_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and cell is ring[tok]
    )
    # Semantic known routing: any cell whose spectrum contains the token.
    known_semantic_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and tok in cell.spectrum
    )
    n_known_consumed = sum(1 for (_, _, tok, _) in s.consume_log if tok < 6)
    n_unknown_consumed = sum(1 for (_, _, tok, _) in s.consume_log if tok >= 6)

    n_unknown_consumed_by_spawned = sum(
        1 for (_, cell, tok, _) in s.consume_log if tok >= 6 and cell in spawned
    )

    n_consumed = len(s.consume_log)
    n_in_flight_at_end = sum(1 for c in s.cells if c.current_deposit is not None)
    n_pending_at_end = sum(len(c.pending) for c in s.cells)
    max_age = max((age for (_, _, _, age) in s.consume_log), default=0)

    # Ring integrity check
    ring_intact = all(
        ring[i].spectrum == {i}
        and ring[(i - 1) % 6] in ring[i].connectors
        and ring[(i + 1) % 6] in ring[i].connectors
        for i in range(6)
    )

    return {
        "seed": seed,
        "n_known_injected": n_known,
        "n_unknown_injected": n_unknown,
        "n_consumed": n_consumed,
        "n_in_flight_at_end": n_in_flight_at_end,
        "n_pending_at_end": n_pending_at_end,
        "n_spawned": len(s.spawn_log),
        "spawn_tokens": spawn_tokens,
        "spawn_spectra_count": len(spawn_spectra),
        "ring_intact": ring_intact,
        "known_strict_correct": known_strict_correct,
        "known_semantic_correct": known_semantic_correct,
        "n_known_consumed": n_known_consumed,
        "n_unknown_consumed": n_unknown_consumed,
        "n_unknown_consumed_by_spawned": n_unknown_consumed_by_spawned,
        "max_consumed_age": max_age,
        "max_pending_observed": max_pending_observed,
        "n_total_cells_at_end": len(s.cells),
    }


# ----------------------------------------------------------------------------
# Phase 2 run + measurement
# ----------------------------------------------------------------------------

def run_phase2(
    seed: int,
    learning_threshold: int,
    bias_weights: list[int],
    n_observations: int = None,
) -> dict:
    """5 isolated cells, each with disjoint 4-token alphabet, biased streams."""
    if n_observations is None:
        n_observations = max(250, learning_threshold + 50)
    cells = [
        Cell(
            spectrum=set(),
            learning_threshold=learning_threshold,
            crystallization_size=3,
        )
        for _ in range(5)
    ]
    expected = [
        {0, 1, 2}, {4, 5, 6}, {8, 9, 10}, {12, 13, 14}, {16, 17, 18},
    ]
    bias_offsets = [0, 4, 8, 12, 16]
    rng = random.Random(seed)

    matches = []
    for i, cell in enumerate(cells):
        offset = bias_offsets[i]
        alphabet = [offset + j for j in range(4)]
        stream = rng.choices(alphabet, weights=bias_weights, k=n_observations)
        for tok in stream:
            cell.classify(tok)
        matches.append(cell.spectrum == expected[i])

    return {
        "seed": seed,
        "learning_threshold": learning_threshold,
        "bias_weights": list(bias_weights),
        "all_match": all(matches),
        "per_cell_match": matches,
        "n_match": sum(matches),
        "spectra": [sorted(c.spectrum) for c in cells],
        "states_crystallized": [c.state == State.CRYSTALLIZED for c in cells],
    }


# ----------------------------------------------------------------------------
# Phase 3 run + measurement
# ----------------------------------------------------------------------------

def run_phase3(
    seed: int,
    n_ticks: int = 10_000,
    cadence: int = 30,
    learning_threshold: int = 200,
) -> dict:
    s = Substrate()
    ring = build_k6_ring(s)
    obs = attach_observer(
        s, ring[0],
        learning_threshold=learning_threshold,
        crystallization_size=3,
    )
    inj = Injector(seed=seed)

    for t in range(1, n_ticks + 1):
        if t % cadence == 1:
            s.inject(ring[0], token=inj.next_token())
        s.tick()

    spawned = {child for (_, _, child, _) in s.spawn_log}

    # Strict (Phase 1 inheritance): known token i consumed at ring[i].
    known_strict_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and cell is ring[tok]
    )
    # Semantic: any cell whose spectrum contains the token.
    known_semantic_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and tok in cell.spectrum
    )
    n_known_consumed = sum(1 for (_, _, tok, _) in s.consume_log if tok < 6)
    n_consumed_by_observer = sum(1 for (_, c, _, _) in s.consume_log if c is obs)
    observer_intercepts = sum(
        1 for (_, c, tok, _) in s.consume_log
        if c is obs and tok in obs.spectrum
    )

    return {
        "seed": seed,
        "learning_threshold": learning_threshold,
        "n_consumed": len(s.consume_log),
        "n_consumed_by_observer": n_consumed_by_observer,
        "observer_intercepts": observer_intercepts,
        "n_spawned": len(s.spawn_log),
        "spawn_tokens": sorted({tok for (_, _, _, tok) in s.spawn_log}),
        "observer_spectrum": sorted(obs.spectrum),
        "observer_state": obs.state.value,
        "observer_total_obs": sum(obs.obs_counter.values()),
        "observer_top5": [(t, c) for (t, c) in obs.obs_counter.most_common(5)],
        "n_known_consumed": n_known_consumed,
        "known_strict_correct": known_strict_correct,
        "known_semantic_correct": known_semantic_correct,
        "ring_intact": all(ring[i].spectrum == {i} for i in range(6)),
    }


# ----------------------------------------------------------------------------
# Phase 4 run + measurement
# ----------------------------------------------------------------------------

def run_phase4(
    seed: int,
    n_ticks: int = 10_000,
    cadence: int = 30,
    learning_threshold: int = 15,
    crystallization_size: int = 1,
    observer_attach_perm: list[int] | None = None,
    fixture: str = "ring",
) -> dict:
    s = Substrate()
    if fixture == "ring":
        ring = build_k6_ring(s)
    elif fixture == "star":
        ring = build_k6_star(s)
    else:
        raise ValueError(f"unknown fixture: {fixture}")

    perm = observer_attach_perm if observer_attach_perm is not None else list(range(6))
    observers = [
        attach_observer(
            s, ring[perm[i]],
            learning_threshold=learning_threshold,
            crystallization_size=crystallization_size,
        )
        for i in range(6)
    ]
    inj = Injector(seed=seed)

    for t in range(1, n_ticks + 1):
        if t % cadence == 1:
            s.inject(ring[0], token=inj.next_token())
        s.tick()

    spawned = {child for (_, _, child, _) in s.spawn_log}
    spawn_tokens = sorted([tok for (_, _, _, tok) in s.spawn_log])
    has_known_token_spawn = any(tok < 6 for tok in spawn_tokens)

    # duplicate spawn check: more than one spawn for the same token.
    token_spawn_counter = Counter(spawn_tokens)
    has_duplicate_spawn = any(c > 1 for c in token_spawn_counter.values())

    crystallized_states = [o.state == State.CRYSTALLIZED for o in observers]
    n_crystallized = sum(crystallized_states)
    crystallized_spectra = [
        frozenset(o.spectrum) for o in observers if o.state == State.CRYSTALLIZED
    ]
    distinct_spectra = len(set(crystallized_spectra))

    # Did any observer learn its host's token? (design said no.)
    host_token_violations = []
    for i, o in enumerate(observers):
        host_idx = perm[i]
        if o.state == State.CRYSTALLIZED and host_idx in o.spectrum:
            host_token_violations.append((i, host_idx, sorted(o.spectrum)))

    known_strict_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and cell is ring[tok]
    )
    known_semantic_correct = sum(
        1 for (_, cell, tok, _) in s.consume_log
        if tok < 6 and tok in cell.spectrum
    )
    n_known_consumed = sum(1 for (_, _, tok, _) in s.consume_log if tok < 6)

    return {
        "seed": seed,
        "fixture": fixture,
        "learning_threshold": learning_threshold,
        "crystallization_size": crystallization_size,
        "observer_attach_perm": list(perm),
        "n_spawned": len(s.spawn_log),
        "spawn_tokens": spawn_tokens,
        "has_known_token_spawn": has_known_token_spawn,
        "has_duplicate_spawn": has_duplicate_spawn,
        "n_crystallized": n_crystallized,
        "distinct_spectra": distinct_spectra,
        "host_token_violations": host_token_violations,
        "per_observer_state": [o.state.value for o in observers],
        "per_observer_obs": [sum(o.obs_counter.values()) for o in observers],
        "per_observer_spectrum": [sorted(o.spectrum) for o in observers],
        "n_consumed": len(s.consume_log),
        "n_known_consumed": n_known_consumed,
        "known_strict_correct": known_strict_correct,
        "known_semantic_correct": known_semantic_correct,
        "ring_intact": all(ring[i].spectrum == {i} for i in range(6)),
    }


# ----------------------------------------------------------------------------
# Do-nothing baseline (5b)
# ----------------------------------------------------------------------------

def run_do_nothing_baseline(
    seed: int,
    n_observers: int = 6,
    threshold: int = 15,
    crystallization_size: int = 1,
    alphabet_size: int = 10,  # tokens {1..10}
) -> dict:
    """6 isolated Cells, each fed `threshold` random samples from {1..alphabet_size},
    crystallized at top-K. No substrate, no canvas. Tests whether Phase 4's distinct-
    spectra count is distinguishable from pure counting noise."""
    rng = random.Random(seed)
    observers = [
        Cell(
            spectrum=set(),
            learning_threshold=threshold,
            crystallization_size=crystallization_size,
        )
        for _ in range(n_observers)
    ]
    for o in observers:
        for _ in range(threshold):
            tok = rng.randint(1, alphabet_size)
            o.classify(tok)
    crystallized = [o for o in observers if o.state == State.CRYSTALLIZED]
    distinct_spectra = len({frozenset(o.spectrum) for o in crystallized})
    return {
        "seed": seed,
        "n_crystallized": len(crystallized),
        "distinct_spectra": distinct_spectra,
        "spectra": [sorted(o.spectrum) for o in observers],
    }


# ----------------------------------------------------------------------------
# Sweep harness
# ----------------------------------------------------------------------------

def sweep_phase1(seeds: list[int]) -> list[dict]:
    return [run_phase1(s) for s in seeds]

def sweep_phase2_original(seeds: list[int]) -> list[dict]:
    """Original design: threshold=50, bias=[50,25,15,10]."""
    return [run_phase2(s, learning_threshold=50, bias_weights=[50, 25, 15, 10],
                       n_observations=70) for s in seeds]

def sweep_phase2_shipped(seeds: list[int]) -> list[dict]:
    """Shipped: threshold=200, bias=[60,25,12,3]."""
    return [run_phase2(s, learning_threshold=200, bias_weights=[60, 25, 12, 3],
                       n_observations=250) for s in seeds]

def sweep_phase3_default(seeds: list[int]) -> list[dict]:
    return [run_phase3(s) for s in seeds]

def sweep_phase4_default(seeds: list[int]) -> list[dict]:
    return [run_phase4(s) for s in seeds]

def sweep_phase4_threshold200(seeds: list[int]) -> list[dict]:
    """Goal-post reversion: Phase 3 threshold for Phase 4 fixture."""
    return [run_phase4(s, learning_threshold=200, crystallization_size=1)
            for s in seeds]

def sweep_phase4_permuted(seeds: list[int]) -> list[dict]:
    """Adversarial fixture A: observer attach order permuted (rotate by 3)."""
    perm = [3, 4, 5, 0, 1, 2]
    return [run_phase4(s, observer_attach_perm=perm) for s in seeds]

def sweep_phase4_star(seeds: list[int]) -> list[dict]:
    """Adversarial fixture B: star topology."""
    return [run_phase4(s, fixture="star") for s in seeds]


def sweep_phase1_unknown_only(seeds: list[int]) -> list[dict]:
    """Adversarial fixture C: null injection — only unknown tokens (no knowns)."""
    out = []
    for seed in seeds:
        s = Substrate()
        ring = build_k6_ring(s)
        inj = Injector(seed=seed, known_probability=0.0)
        n_unknown = 0
        max_pending = 0
        for t in range(1, 10_001):
            if t % 15 == 1:
                tok = inj.next_token()
                s.inject(ring[0], token=tok)
                n_unknown += 1
            s.tick()
            max_pending = max(max_pending, max((len(c.pending) for c in s.cells), default=0))
        out.append({
            "seed": seed,
            "n_unknown_injected": n_unknown,
            "n_consumed": len(s.consume_log),
            "n_spawned": len(s.spawn_log),
            "spawn_tokens": sorted({tok for (_, _, _, tok) in s.spawn_log}),
            "max_pending": max_pending,
            "max_age": max((age for (_, _, _, age) in s.consume_log), default=0),
            "ring_intact": all(ring[i].spectrum == {i} for i in range(6)),
        })
    return out


def sweep_baseline(seeds: list[int]) -> list[dict]:
    return [run_do_nothing_baseline(s) for s in seeds]


# ----------------------------------------------------------------------------
# Aggregation utilities
# ----------------------------------------------------------------------------

def summarize_int(values: list[int]) -> dict:
    if not values:
        return {"n": 0}
    return {
        "n": len(values),
        "min": min(values),
        "max": max(values),
        "mean": round(statistics.mean(values), 2),
        "median": statistics.median(values),
        "stdev": round(statistics.stdev(values), 2) if len(values) > 1 else 0.0,
    }


def summarize_phase1(rows: list[dict]) -> dict:
    return {
        "n_seeds": len(rows),
        "n_spawned_distribution": Counter(r["n_spawned"] for r in rows),
        "ring_intact_count": sum(r["ring_intact"] for r in rows),
        "known_strict_pct": [
            round(100 * r["known_strict_correct"] / r["n_known_consumed"], 2)
            if r["n_known_consumed"] else None
            for r in rows
        ],
        "known_semantic_pct": [
            round(100 * r["known_semantic_correct"] / r["n_known_consumed"], 2)
            if r["n_known_consumed"] else None
            for r in rows
        ],
        "max_age_summary": summarize_int([r["max_consumed_age"] for r in rows]),
        "max_pending_summary": summarize_int([r["max_pending_observed"] for r in rows]),
        "all_strict_100": sum(
            1 for r in rows
            if r["n_known_consumed"]
            and r["known_strict_correct"] == r["n_known_consumed"]
        ),
        "max_age_over_339": sum(1 for r in rows if r["max_consumed_age"] > 339),
        "max_age_over_1000": sum(1 for r in rows if r["max_consumed_age"] > 1000),
    }


def summarize_phase2(rows: list[dict], label: str) -> dict:
    return {
        "label": label,
        "n_seeds": len(rows),
        "all_match_count": sum(1 for r in rows if r["all_match"]),
        "per_cell_match_rate": [
            round(100 * sum(r["per_cell_match"][i] for r in rows) / len(rows), 2)
            for i in range(5)
        ],
        "match_distribution": Counter(r["n_match"] for r in rows),
    }


def summarize_phase3(rows: list[dict]) -> dict:
    spectra_counter = Counter(tuple(r["observer_spectrum"]) for r in rows)
    return {
        "n_seeds": len(rows),
        "n_spawned_distribution": Counter(r["n_spawned"] for r in rows),
        "observer_crystallized_count": sum(
            1 for r in rows if r["observer_state"] == "crystallized"
        ),
        "observer_spectrum_distribution": dict(spectra_counter.most_common(10)),
        "spectrum_contains_unknowns_pct": round(100 * sum(
            1 for r in rows if any(t >= 6 for t in r["observer_spectrum"])
        ) / len(rows), 2),
        "spectrum_all_knowns_pct": round(100 * sum(
            1 for r in rows if r["observer_spectrum"] and all(t < 6 for t in r["observer_spectrum"])
        ) / len(rows), 2),
        "strict_routing_pct": [
            round(100 * r["known_strict_correct"] / r["n_known_consumed"], 2)
            if r["n_known_consumed"] else None
            for r in rows
        ],
        "semantic_routing_pct": [
            round(100 * r["known_semantic_correct"] / r["n_known_consumed"], 2)
            if r["n_known_consumed"] else None
            for r in rows
        ],
        "strict_routing_summary": summarize_int([
            r["known_strict_correct"] * 100 // r["n_known_consumed"]
            for r in rows if r["n_known_consumed"]
        ]),
    }


def summarize_phase4(rows: list[dict], label: str) -> dict:
    return {
        "label": label,
        "n_seeds": len(rows),
        "n_crystallized_distribution": Counter(r["n_crystallized"] for r in rows),
        "distinct_spectra_distribution": Counter(r["distinct_spectra"] for r in rows),
        "all_6_crystallized_count": sum(1 for r in rows if r["n_crystallized"] == 6),
        "at_least_3_distinct_count": sum(1 for r in rows if r["distinct_spectra"] >= 3),
        "n_spawned_distribution": Counter(r["n_spawned"] for r in rows),
        "n_spawned_summary": summarize_int([r["n_spawned"] for r in rows]),
        "has_known_token_spawn_count": sum(1 for r in rows if r["has_known_token_spawn"]),
        "has_duplicate_spawn_count": sum(1 for r in rows if r["has_duplicate_spawn"]),
        "host_token_violation_count": sum(
            1 for r in rows if r["host_token_violations"]
        ),
        "ring_intact_count": sum(1 for r in rows if r["ring_intact"]),
    }


def summarize_baseline(rows: list[dict]) -> dict:
    return {
        "n_seeds": len(rows),
        "n_crystallized_distribution": Counter(r["n_crystallized"] for r in rows),
        "distinct_spectra_distribution": Counter(r["distinct_spectra"] for r in rows),
        "at_least_3_distinct_count": sum(1 for r in rows if r["distinct_spectra"] >= 3),
        "all_6_crystallized_count": sum(1 for r in rows if r["n_crystallized"] == 6),
    }


def summarize_unknown_only(rows: list[dict]) -> dict:
    return {
        "n_seeds": len(rows),
        "n_spawned_distribution": Counter(r["n_spawned"] for r in rows),
        "max_pending_summary": summarize_int([r["max_pending"] for r in rows]),
        "max_age_summary": summarize_int([r["max_age"] for r in rows]),
        "ring_intact_count": sum(r["ring_intact"] for r in rows),
        "max_pending_over_20_count": sum(1 for r in rows if r["max_pending"] > 20),
        "max_age_over_1000_count": sum(1 for r in rows if r["max_age"] > 1000),
    }


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------

def main(n_seeds: int = 100):
    seeds = list(range(n_seeds))
    out: dict = {"n_seeds": n_seeds}
    t0 = time.time()

    print(f"=== Skeptic-pass over {n_seeds} seeds ===")

    print("[1/9] Phase 1 sweep ...", end=" ", flush=True)
    p1 = sweep_phase1(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase1"] = {"summary": summarize_phase1(p1), "rows": p1}

    print("[2/9] Phase 2 ORIGINAL params ...", end=" ", flush=True)
    p2_orig = sweep_phase2_original(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase2_original"] = {
        "summary": summarize_phase2(p2_orig, "ORIGINAL: threshold=50, bias=[50,25,15,10]"),
        "rows": p2_orig,
    }

    print("[3/9] Phase 2 SHIPPED params ...", end=" ", flush=True)
    p2_ship = sweep_phase2_shipped(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase2_shipped"] = {
        "summary": summarize_phase2(p2_ship, "SHIPPED: threshold=200, bias=[60,25,12,3]"),
        "rows": p2_ship,
    }

    print("[4/9] Phase 3 default sweep ...", end=" ", flush=True)
    p3 = sweep_phase3_default(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase3"] = {"summary": summarize_phase3(p3), "rows": p3}

    print("[5/9] Phase 4 default sweep ...", end=" ", flush=True)
    p4 = sweep_phase4_default(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase4"] = {"summary": summarize_phase4(p4, "DEFAULT: threshold=15, ring"), "rows": p4}

    print("[6/9] Phase 4 threshold=200 ...", end=" ", flush=True)
    p4_t200 = sweep_phase4_threshold200(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase4_threshold200"] = {
        "summary": summarize_phase4(p4_t200, "REVERT: threshold=200, ring"),
        "rows": p4_t200,
    }

    print("[7/9] Phase 4 observer-permuted ...", end=" ", flush=True)
    p4_perm = sweep_phase4_permuted(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase4_permuted"] = {
        "summary": summarize_phase4(p4_perm, "PERMUTED: observers attached in [3,4,5,0,1,2] order"),
        "rows": p4_perm,
    }

    print("[8/9] Phase 4 star fixture ...", end=" ", flush=True)
    p4_star = sweep_phase4_star(seeds); print(f"{time.time() - t0:.1f}s")
    out["phase4_star"] = {
        "summary": summarize_phase4(p4_star, "STAR: c0 hub, c1..c5 spokes, no peripheral edges"),
        "rows": p4_star,
    }

    print("[9/9] Adversarial / baseline ...", end=" ", flush=True)
    null_inj = sweep_phase1_unknown_only(seeds)
    baseline = sweep_baseline(seeds)
    print(f"{time.time() - t0:.1f}s")
    out["phase1_unknown_only"] = {
        "summary": summarize_unknown_only(null_inj),
        "rows": null_inj,
    }
    out["baseline_random_observers"] = {
        "summary": summarize_baseline(baseline),
        "rows": baseline,
    }

    out["wall_clock_seconds"] = round(time.time() - t0, 1)
    print(f"\nTotal: {out['wall_clock_seconds']}s")

    def _stringify_keys(obj):
        if isinstance(obj, dict):
            return {str(k): _stringify_keys(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [_stringify_keys(v) for v in obj]
        if isinstance(obj, Counter):
            return {str(k): v for k, v in obj.items()}
        return obj

    out_path = Path(__file__).parent / "skeptic_pass_results.json"
    out_path.write_text(json.dumps(_stringify_keys(out), default=str, indent=2))
    print(f"Wrote {out_path}")

    # Console summary
    print("\n=== SUMMARY ===\n")
    print("Phase 1:", out["phase1"]["summary"])
    print()
    print("Phase 2 ORIGINAL:", out["phase2_original"]["summary"])
    print("Phase 2 SHIPPED :", out["phase2_shipped"]["summary"])
    print()
    print("Phase 3 default:", out["phase3"]["summary"])
    print()
    print("Phase 4 default     :", out["phase4"]["summary"])
    print("Phase 4 threshold200:", out["phase4_threshold200"]["summary"])
    print("Phase 4 permuted    :", out["phase4_permuted"]["summary"])
    print("Phase 4 star        :", out["phase4_star"]["summary"])
    print()
    print("Adversarial — unknown-only Phase 1:", out["phase1_unknown_only"]["summary"])
    print("Baseline (random observers)        :", out["baseline_random_observers"]["summary"])


if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    main(n)
