"""
Experiment 04 — cross-band correlation in wavelet space.

Question: do W3 (fundamental ~1050 Hz) and W4 (2nd harmonic ~2100 Hz) share
dependency that (H1) exists beyond chance, (H2) survives per-band LPC, and
(H3) is exploitable by a trie/context model on HELD-OUT data?

Design notes (see EXPERIMENT_04_crossband.md):
- HMT literature: cross-scale dependency lives in magnitudes, not signed r.
  MI is the gating statistic; magnitude r reported alongside.
- CTW trap: in-sample conditional entropy always "improves". H3 uses
  train/validation/test time splits; config chosen on validation only.
- Null model: circular-shift surrogates (preserve marginals + within-band
  autocorrelation, destroy cross-band alignment).
"""
from __future__ import annotations
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pywt
import soundfile as sf
from scipy.linalg import solve_toeplitz

HERE = Path(__file__).parent
SAMPLE = HERE / "data" / "FLAC_11_secs_Small_75d2275409.flac"
RESULTS_DIR = HERE / "results"
RESULTS_DIR.mkdir(exist_ok=True)
PLOTS_DIR = RESULTS_DIR / "plots_04"
PLOTS_DIR.mkdir(exist_ok=True)

REGION_START_S = 1.0
REGION_DUR_S = 1.0
WAVELET = "db8"
LEVELS = 7
MODE = "periodization"
LPC_ORDER = 8

TRAIN_FRAC, VAL_FRAC = 0.50, 0.20          # remaining 0.30 = test
N_SURROGATES = 200
MIN_SHIFT = 32
MI_BINS = 16
TARGET_LEVELS = 16
SIGMA_CLIP = 4.0
H3_MARGIN = 0.10                            # bits/symbol, pre-registered
RNG = np.random.default_rng(20260610)


# ---------- shared pieces (style of diagnostic_03.py) ----------

def lpc_yule_walker(x: np.ndarray, order: int) -> np.ndarray:
    r = np.correlate(x, x, mode="full")[len(x) - 1:][: order + 1]
    if r[0] == 0:
        return np.zeros(order)
    return solve_toeplitz((r[:order], r[:order]), r[1: order + 1])


def lpc_residual_full(x: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Full-length residual (pred=0 for the first `order` samples) so indices
    stay 1:1 with the coefficient arrays."""
    order = len(a)
    pred = np.zeros_like(x)
    for n in range(order, len(x)):
        pred[n] = a @ x[n - order: n][::-1]
    return x - pred


def quantile_bins(x: np.ndarray, n_bins: int) -> np.ndarray:
    """Equal-population bin edges (robust to heavy tails for MI estimation)."""
    qs = np.quantile(x, np.linspace(0, 1, n_bins + 1)[1:-1])
    return qs


def digitize(x: np.ndarray, edges: np.ndarray) -> np.ndarray:
    return np.digitize(x, edges)


def mutual_information_bits(qa: np.ndarray, qb: np.ndarray, n_bins: int) -> float:
    joint = np.zeros((n_bins, n_bins))
    np.add.at(joint, (qa, qb), 1)
    joint /= joint.sum()
    pa = joint.sum(axis=1, keepdims=True)
    pb = joint.sum(axis=0, keepdims=True)
    nz = joint > 0
    return float(np.sum(joint[nz] * np.log2(joint[nz] / (pa @ pb)[nz])))


# ---------- alignment ----------

def aligned_pairs(w3: np.ndarray, w4: np.ndarray, offset: int):
    """Zerotree parent-child pairs: for each W4 index j, parent k=(j-offset)//2.
    Returns (j_indices, k_indices) where both are valid."""
    j = np.arange(len(w4))
    k = (j - offset) // 2
    ok = (k >= 0) & (k < len(w3)) & ((j - offset) >= 0)
    return j[ok], k[ok]


def magnitude_corr(w3: np.ndarray, w4: np.ndarray, j: np.ndarray, k: np.ndarray) -> float:
    a, b = np.abs(w3[k]), np.abs(w4[j])
    if a.std() == 0 or b.std() == 0:
        return 0.0
    return float(np.corrcoef(a, b)[0, 1])


# ---------- dependency measures (H1 / H2) ----------

def dependency_measures(w3: np.ndarray, w4: np.ndarray, offset: int, label: str) -> dict:
    j, k = aligned_pairs(w3, w4, offset)
    a, b = w3[k], w4[j]
    signed_r = float(np.corrcoef(a, b)[0, 1])
    mag_r = float(np.corrcoef(np.abs(a), np.abs(b))[0, 1])
    edges_a = quantile_bins(a, MI_BINS)
    edges_b = quantile_bins(b, MI_BINS)
    qa, qb = digitize(a, edges_a), digitize(b, edges_b)
    mi = mutual_information_bits(qa, qb, MI_BINS)

    # circular-shift surrogates on the W4 side (in pair space)
    n = len(b)
    null_mi = np.empty(N_SURROGATES)
    for s in range(N_SURROGATES):
        shift = int(RNG.integers(MIN_SHIFT, n - MIN_SHIFT))
        null_mi[s] = mutual_information_bits(qa, np.roll(qb, shift), MI_BINS)
    p99 = float(np.percentile(null_mi, 99))
    return {
        "label": label,
        "n_pairs": int(n),
        "signed_r": signed_r,
        "magnitude_r": mag_r,
        "mi_bits": mi,
        "null_mi_mean": float(null_mi.mean()),
        "null_mi_p99": p99,
        "pass": bool(mi > p99),
        "null_mi": null_mi,
    }


# ---------- H3: trie / context models ----------

def coarsen(sym: np.ndarray, levels: int) -> np.ndarray:
    return sym * levels // TARGET_LEVELS


def quantize_residual(res: np.ndarray, sigma: float) -> np.ndarray:
    clipped = np.clip(res, -SIGMA_CLIP * sigma, SIGMA_CLIP * sigma)
    sym = np.floor((clipped + SIGMA_CLIP * sigma)
                   / (2 * SIGMA_CLIP * sigma) * TARGET_LEVELS).astype(int)
    return np.clip(sym, 0, TARGET_LEVELS - 1)


def context_arrays(target_sym, parent_sym_for_j, spec):
    """Build context tuple array for each position j (W4 pair space).
    spec: dict with 'prev_depth', 'prev_levels', 'use_parent', 'parent_levels'."""
    n = len(target_sym)
    cols = []
    start = spec["prev_depth"]
    for d in range(1, spec["prev_depth"] + 1):
        prev = np.empty(n, dtype=int)
        prev[d:] = coarsen(target_sym[:-d], spec["prev_levels"])
        prev[:d] = -1
        cols.append(prev)
    if spec["use_parent"]:
        cols.append(coarsen(parent_sym_for_j, spec["parent_levels"]))
    if not cols:  # M0
        return np.zeros((n, 0), dtype=int), 0
    return np.stack(cols, axis=1), start


def cross_entropy(ctx, start, target_sym, train_idx, eval_idx) -> float:
    counts: dict = {}
    for i in train_idx:
        if i < start:
            continue
        key = tuple(ctx[i])
        slot = counts.setdefault(key, np.zeros(TARGET_LEVELS))
        slot[target_sym[i]] += 1
    total_bits, n_eval = 0.0, 0
    for i in eval_idx:
        if i < start:
            continue
        key = tuple(ctx[i])
        slot = counts.get(key)
        if slot is None:
            p = 1.0 / TARGET_LEVELS
        else:
            p = (slot[target_sym[i]] + 1) / (slot.sum() + TARGET_LEVELS)
        total_bits -= np.log2(p)
        n_eval += 1
    return total_bits / n_eval if n_eval else float("nan")


MODEL_GRIDS = {
    "M0": [{"prev_depth": 0, "prev_levels": 0, "use_parent": False, "parent_levels": 0}],
    "M1": [{"prev_depth": 1, "prev_levels": 16, "use_parent": False, "parent_levels": 0},
           {"prev_depth": 1, "prev_levels": 8, "use_parent": False, "parent_levels": 0},
           {"prev_depth": 2, "prev_levels": 8, "use_parent": False, "parent_levels": 0},
           {"prev_depth": 2, "prev_levels": 4, "use_parent": False, "parent_levels": 0}],
    "M2": [{"prev_depth": 0, "prev_levels": 0, "use_parent": True, "parent_levels": 4},
           {"prev_depth": 0, "prev_levels": 0, "use_parent": True, "parent_levels": 8},
           {"prev_depth": 0, "prev_levels": 0, "use_parent": True, "parent_levels": 16}],
    "M3": [{"prev_depth": 1, "prev_levels": 8, "use_parent": True, "parent_levels": 4},
           {"prev_depth": 1, "prev_levels": 8, "use_parent": True, "parent_levels": 8},
           {"prev_depth": 1, "prev_levels": 8, "use_parent": True, "parent_levels": 16},
           {"prev_depth": 1, "prev_levels": 4, "use_parent": True, "parent_levels": 4},
           {"prev_depth": 2, "prev_levels": 4, "use_parent": True, "parent_levels": 4}],
}


def run_h3(target_sym, parent_sym_for_j, splits) -> dict:
    train_idx, val_idx, test_idx = splits
    out = {}
    for name, grid in MODEL_GRIDS.items():
        best = None
        for spec in grid:
            ctx, start = context_arrays(target_sym, parent_sym_for_j, spec)
            ce_val = cross_entropy(ctx, start, target_sym, train_idx, val_idx)
            if best is None or ce_val < best["ce_val"]:
                best = {"spec": spec, "ce_val": ce_val, "ctx": ctx, "start": start}
        ce_test = cross_entropy(best["ctx"], best["start"], target_sym, train_idx, test_idx)
        out[name] = {"spec": best["spec"], "ce_val_bits": float(best["ce_val"]),
                     "ce_test_bits": float(ce_test)}
    return out


# ---------- main ----------

def main():
    print(f"Loading {SAMPLE}")
    data, sr = sf.read(SAMPLE)
    if data.ndim > 1:
        data = data[:, 0]
    s0 = int(REGION_START_S * sr)
    s1 = int((REGION_START_S + REGION_DUR_S) * sr)
    x = data[s0:s1].astype(np.float64)
    print(f"  Region {REGION_START_S}..{REGION_START_S + REGION_DUR_S}s, "
          f"{len(x)} samples at {sr} Hz; {WAVELET} L{LEVELS} {MODE}")

    coeffs = pywt.wavedec(x, wavelet=WAVELET, level=LEVELS, mode=MODE)
    w3, w4 = coeffs[3], coeffs[4]            # cD5 (689-1378), cD4 (1378-2756)
    print(f"  W3(cD5): n={len(w3)}  W4(cD4): n={len(w4)}")

    # ---- offset scan (train portion of pair space only) ----
    n_train_j = int(TRAIN_FRAC * len(w4))
    best_off, best_mag = 0, -np.inf
    scan = {}
    for off in range(-8, 9):
        j, k = aligned_pairs(w3, w4, off)
        m = (j < n_train_j)
        if m.sum() < 100:
            continue
        c = magnitude_corr(w3, w4, j[m], k[m])
        scan[off] = c
        if c > best_mag:
            best_off, best_mag = off, c
    print(f"\nOffset scan (train-only magnitude r): best offset={best_off} "
          f"(r={best_mag:.3f}); offset 0 r={scan.get(0, float('nan')):.3f}")

    # ---- H1: raw coefficients ----
    h1 = dependency_measures(w3, w4, best_off, "raw")
    print(f"\nH1 raw: signed_r={h1['signed_r']:+.3f}  |mag_r|={h1['magnitude_r']:+.3f}  "
          f"MI={h1['mi_bits']:.4f} bits (null mean {h1['null_mi_mean']:.4f}, "
          f"p99 {h1['null_mi_p99']:.4f}) -> {'PASS' if h1['pass'] else 'FAIL'}")

    # ---- per-band LPC residuals (fit on FULL region, as pre-registered;
    # a train-only fit was an unregistered deviation caught by the skeptic
    # pass — it inflated H2 MI ~65% via a shared mismatch envelope) ----
    a3 = lpc_yule_walker(w3, LPC_ORDER)
    a4 = lpc_yule_walker(w4, LPC_ORDER)
    r3 = lpc_residual_full(w3, a3)
    r4 = lpc_residual_full(w4, a4)

    # ---- H2: residuals ----
    h2 = dependency_measures(r3, r4, best_off, "lpc_residual")
    print(f"H2 resid: signed_r={h2['signed_r']:+.3f}  |mag_r|={h2['magnitude_r']:+.3f}  "
          f"MI={h2['mi_bits']:.4f} bits (null mean {h2['null_mi_mean']:.4f}, "
          f"p99 {h2['null_mi_p99']:.4f}) -> {'PASS' if h2['pass'] else 'FAIL'}")

    # ---- H3: context models on quantized residuals ----
    j, k = aligned_pairs(r3, r4, best_off)
    sigma4 = float(r4[j[j < n_train_j]].std())
    sigma3 = float(r3[: int(TRAIN_FRAC * len(r3))].std())  # train-split only (pre-registered)
    target_sym = quantize_residual(r4[j], sigma4)
    parent_sym = quantize_residual(r3[k], sigma3)

    n = len(target_sym)
    i_train = np.arange(0, int(TRAIN_FRAC * n))
    i_val = np.arange(int(TRAIN_FRAC * n), int((TRAIN_FRAC + VAL_FRAC) * n))
    i_test = np.arange(int((TRAIN_FRAC + VAL_FRAC) * n), n)
    print(f"\nH3 splits: train={len(i_train)} val={len(i_val)} test={len(i_test)} "
          f"(alphabet {TARGET_LEVELS})")

    h3 = run_h3(target_sym, parent_sym, (i_train, i_val, i_test))
    for name in ("M0", "M1", "M2", "M3"):
        r = h3[name]
        print(f"  {name}: val={r['ce_val_bits']:.3f}  TEST={r['ce_test_bits']:.3f} "
              f"bits/sym  spec={r['spec']}")
    adv = h3["M1"]["ce_test_bits"] - h3["M3"]["ce_test_bits"]
    h3_pass = adv >= H3_MARGIN
    print(f"  M3 advantage over M1 on test: {adv:+.3f} bits/sym "
          f"(margin {H3_MARGIN}) -> {'PASS' if h3_pass else 'FAIL'}")

    # ---- H3 sanity: misaligned-parent surrogate ----
    sur_advs = []
    for s in range(20):
        shift = int(RNG.integers(MIN_SHIFT, n - MIN_SHIFT))
        h3_s = run_h3(target_sym, np.roll(parent_sym, shift), (i_train, i_val, i_test))
        sur_advs.append(h3_s["M1"]["ce_test_bits"] - h3_s["M3"]["ce_test_bits"])
    sur_advs = np.array(sur_advs)
    sanity_ok = bool(np.abs(sur_advs.mean()) < 0.05)
    print(f"  Surrogate (misaligned parent) M3-vs-M1 advantage: "
          f"mean {sur_advs.mean():+.3f} +- {sur_advs.std():.3f} bits/sym "
          f"-> sanity {'OK' if sanity_ok else 'VIOLATED'}")

    # ---- net parent gain at MATCHED temporal context (skeptic req 4a/4b):
    # compare M3's selected spec against (i) the same spec without the parent
    # column and (ii) the same spec with a rolled parent. The net gain
    # (i - M3) - (i - mean(ii)) isolates alignment-specific information from
    # the count-fragmentation-toward-uniform artifact. ----
    m3_spec = h3["M3"]["spec"]
    matched_spec = dict(m3_spec, use_parent=False, parent_levels=0)
    ctx_m, st_m = context_arrays(target_sym, parent_sym, matched_spec)
    ce_matched = cross_entropy(ctx_m, st_m, target_sym, i_train, i_test)
    rolled_ces = []
    for s in range(20):
        shift = int(RNG.integers(MIN_SHIFT, n - MIN_SHIFT))
        ctx_r, st_r = context_arrays(target_sym, np.roll(parent_sym, shift), m3_spec)
        rolled_ces.append(cross_entropy(ctx_r, st_r, target_sym, i_train, i_test))
    rolled_ces = np.array(rolled_ces)
    gain_aligned = ce_matched - h3["M3"]["ce_test_bits"]
    gain_rolled = ce_matched - rolled_ces
    net_parent_gain = gain_aligned - gain_rolled.mean()
    print(f"  Matched-context decomposition: matched-M1={ce_matched:.3f}, "
          f"aligned gain {gain_aligned:+.3f}, rolled gain {gain_rolled.mean():+.3f} "
          f"+- {gain_rolled.std():.3f} -> NET parent gain {net_parent_gain:+.3f} bits/sym")

    # ---- train-size curve (selected specs, test CE) ----
    curve = []
    for frac in (0.25, 0.5, 0.75, 1.0):
        sub = i_train[: int(frac * len(i_train))]
        row = {"train_frac_of_train": frac}
        for name in ("M1", "M3"):
            spec = h3[name]["spec"]
            ctx, start = context_arrays(target_sym, parent_sym, spec)
            row[name] = float(cross_entropy(ctx, start, target_sym, sub, i_test))
        curve.append(row)
    print("\nTrain curve (test bits/sym):")
    for row in curve:
        print(f"  {row['train_frac_of_train']:.2f} of train -> "
              f"M1={row['M1']:.3f}  M3={row['M3']:.3f}")

    # ---- plots ----
    j_r, k_r = aligned_pairs(w3, w4, best_off)
    fig, axs = plt.subplots(1, 2, figsize=(11, 4.5))
    axs[0].scatter(np.abs(w3[k_r]), np.abs(w4[j_r]), s=2, alpha=0.3)
    axs[0].set_xscale("log"); axs[0].set_yscale("log")
    axs[0].set_title(f"raw |W3| vs |W4| (mag_r={h1['magnitude_r']:.3f})", fontsize=9)
    axs[1].scatter(np.abs(r3[k]), np.abs(r4[j]), s=2, alpha=0.3)
    axs[1].set_xscale("log"); axs[1].set_yscale("log")
    axs[1].set_title(f"LPC resid |W3| vs |W4| (mag_r={h2['magnitude_r']:.3f})", fontsize=9)
    for ax in axs:
        ax.set_xlabel("|W3 parent|"); ax.set_ylabel("|W4 child|")
    fig.tight_layout(); fig.savefig(PLOTS_DIR / "01_magnitude_scatter.png", dpi=110)
    plt.close(fig)

    fig, axs = plt.subplots(1, 2, figsize=(11, 4))
    for ax, h, ttl in ((axs[0], h1, "raw"), (axs[1], h2, "LPC residual")):
        ax.hist(h["null_mi"], bins=40, alpha=0.7, label="surrogate null")
        ax.axvline(h["mi_bits"], color="r", lw=2, label=f"observed {h['mi_bits']:.3f}")
        ax.axvline(h["null_mi_p99"], color="k", ls="--", lw=1, label="null p99")
        ax.set_title(f"MI vs null — {ttl}", fontsize=9); ax.legend(fontsize=7)
        ax.set_xlabel("MI (bits)")
    fig.tight_layout(); fig.savefig(PLOTS_DIR / "02_mi_null.png", dpi=110)
    plt.close(fig)

    fig, ax = plt.subplots(figsize=(7, 4))
    names = ["M0", "M1", "M2", "M3"]
    vals = [h3[m]["ce_test_bits"] for m in names]
    ax.bar(names, vals)
    ax.axhline(h3["M1"]["ce_test_bits"], color="k", ls="--", lw=1)
    ax.errorbar([3], [h3["M1"]["ce_test_bits"] - sur_advs.mean()],
                yerr=[sur_advs.std()], fmt="x", color="r", label="M3 surrogate")
    ax.set_ylabel("test cross-entropy (bits/sym)")
    ax.set_title("Held-out cross-entropy by context model", fontsize=10)
    ax.legend(fontsize=8)
    fig.tight_layout(); fig.savefig(PLOTS_DIR / "03_model_comparison.png", dpi=110)
    plt.close(fig)
    print(f"\nSaved 3 plots to {PLOTS_DIR}")

    # ---- JSON summary ----
    strip = lambda h: {kk: vv for kk, vv in h.items() if kk != "null_mi"}
    summary = {
        "region": [REGION_START_S, REGION_START_S + REGION_DUR_S],
        "wavelet": WAVELET, "levels": LEVELS, "mode": MODE,
        "bands": {"parent": "W3(cD5)", "child": "W4(cD4)"},
        "offset_scan": {str(o): float(c) for o, c in scan.items()},
        "chosen_offset": best_off,
        "h1_raw": strip(h1),
        "h2_residual": strip(h2),
        "h3_models": h3,
        "h3_advantage_M3_vs_M1_test_bits": float(adv),
        "h3_margin": H3_MARGIN,
        "h3_pass": bool(h3_pass),
        "h3_surrogate_advantage_mean": float(sur_advs.mean()),
        "h3_surrogate_advantage_std": float(sur_advs.std()),
        "h3_sanity_ok": sanity_ok,
        "h3_matched_context_ce": float(ce_matched),
        "h3_gain_aligned": float(gain_aligned),
        "h3_gain_rolled_mean": float(gain_rolled.mean()),
        "h3_gain_rolled_std": float(gain_rolled.std()),
        "h3_net_parent_gain": float(net_parent_gain),
        "train_curve": curve,
        "splits": {"train": len(i_train), "val": len(i_val), "test": len(i_test)},
    }
    (RESULTS_DIR / "diagnostic_04_summary.json").write_text(
        json.dumps(summary, indent=2, default=str))
    print("Saved summary to results/diagnostic_04_summary.json")

    print("\n==== VERDICTS ====")
    print(f"H1 (raw cross-band dependency):      {'PASS' if h1['pass'] else 'FAIL'}")
    print(f"H2 (survives per-band LPC):          {'PASS' if h2['pass'] else 'FAIL'}")
    print(f"H3 (exploitable, held-out, sanity {'OK' if sanity_ok else 'BAD'}): "
          f"{'PASS' if h3_pass else 'FAIL'}")


if __name__ == "__main__":
    main()
