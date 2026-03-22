#!/usr/bin/env python3
"""
Experiment 118 v9: Temporal Stream — Video Frame Decomposition

Apply the v8 consumption-transformation mechanism to video frames.
Two token modes:
  Mode A — Byte stream from frame diffs (directly comparable to v7/v8)
  Mode B — Spatial tokens: (x_q, y_q, delta_q) tuples preserving position

Video sources:
  Synthetic — controlled ground truth (gradient bg, moving square, scene cut)
  Real — any video file via opencv (optional)

The mechanism should decompose video into layers of temporal persistence
without being told what "background," "motion," or "noise" are.
"""

import os
import math
import time
import csv
import sys
import numpy as np
from collections import Counter, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Config ------------------------------------------------------------------
FRAME_SIZE       = (64, 64)    # h, w
FPS              = 24
DURATION         = 10          # seconds
SCENE_CUT_FRAME  = 120
N_FRAMES         = FPS * DURATION  # 240

# Mode A
NGRAM_SIZES      = [1, 2, 4]

# Mode B
SPATIAL_QUANT    = 8           # bins per axis (64/8 = 8x8 grid)
DELTA_LEVELS     = 8           # quantized delta levels
TOKENS_PER_FRAME = 64

# Mechanism (from v8)
TARGET_COVERAGE  = 0.5
SEED_THRESHOLD   = 60
MAX_DEPTH        = 20

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "results")


# --- Video Generation -------------------------------------------------------

def generate_synthetic_video(n_frames=N_FRAMES, size=FRAME_SIZE):
    """Generate test video with known temporal structure.

    - Background: horizontal gradient (light left, dark right)
    - Object A: white 8x8 square moving left to right at 1 px/frame
    - Object B: gray 8x8 square stationary at (48, 16)
    - Scene cut at frame 120: background gradient inverts
    - Noise: Gaussian noise with std=5
    """
    h, w = size
    rng = np.random.RandomState(42)
    frames = []
    for t in range(n_frames):
        # Background gradient
        if t < SCENE_CUT_FRAME:
            bg = np.tile(np.linspace(40, 80, w), (h, 1)).astype(np.uint8)
        else:
            bg = np.tile(np.linspace(80, 40, w), (h, 1)).astype(np.uint8)

        frame = bg.copy()

        # Object A: moving square (left to right)
        ax = int(t * (w - 8) / n_frames)
        ay = 24
        frame[ay:ay + 8, ax:ax + 8] = 220

        # Object B: stationary square
        frame[48:56, 16:24] = 128

        # Gaussian noise
        noise = rng.normal(0, 5, size).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        frames.append(frame)

    return frames


def load_real_video(path, size=FRAME_SIZE):
    """Load real video as grayscale frames. Returns list of numpy arrays."""
    try:
        import cv2
    except ImportError:
        print("  cv2 not available, skipping real video")
        return None

    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"  Cannot open video: {path}")
        return None

    frames = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (size[1], size[0]))
        frames.append(gray)
    cap.release()
    print(f"  Loaded {len(frames)} frames from {path}")
    return frames if len(frames) > 1 else None


def compute_frame_diffs(frames):
    """Compute frame differences centered at 128 (no change)."""
    diffs = []
    for i in range(1, len(frames)):
        diff = frames[i].astype(np.int16) - frames[i - 1].astype(np.int16)
        diff = np.clip(diff + 128, 0, 255).astype(np.uint8)
        diffs.append(diff)
    return diffs


# --- Token Extraction -------------------------------------------------------

def diffs_to_bytestream(diffs):
    """Mode A: flatten all diff frames to a single byte array."""
    return b''.join(d.tobytes() for d in diffs)


def ngram_stream(data, n):
    """Yield sliding-window n-gram tuples (reused from v8)."""
    length = len(data)
    i = 0
    while True:
        yield tuple(data[(i + j) % length] for j in range(n))
        i += 1


def spatial_token_stream(diffs, tokens_per_frame=TOKENS_PER_FRAME,
                         sq=SPATIAL_QUANT, dl=DELTA_LEVELS):
    """Mode B: yield (x_q, y_q, delta_q) tuples from frame diffs."""
    h, w = diffs[0].shape
    x_step = max(1, w // sq)
    y_step = max(1, h // sq)

    for diff in diffs:
        flat = diff.flatten()
        deviations = np.abs(flat.astype(np.int16) - 128)
        top_idx = np.argsort(deviations)[-tokens_per_frame:]

        for idx in top_idx:
            y, x = divmod(int(idx), w)
            val = int(diff[y, x])
            # Quantize
            x_q = x // x_step
            y_q = y // y_step
            delta_q = val * dl // 256  # 0..dl-1
            yield (x_q, y_q, delta_q)


# --- Entity Model (from v8) -------------------------------------------------

class Seed:
    __slots__ = ('tokens', 'birth_tick')
    def __init__(self, tick):
        self.tokens = []
        self.birth_tick = tick
    def feed(self, token):
        self.tokens.append(token)


class Entity:
    def __init__(self, name, depth=0, parent=None, birth_tick=0):
        self.name = name
        self.depth = depth
        self.parent = parent
        self.birth_tick = birth_tick
        self.learning_window = max(1, birth_tick)
        self.spectrum = set()
        self.learning = True
        self.obs_counts = Counter()
        self.learning_ticks = 0
        self.consumed = 0
        self.rejected = 0
        self.children = []
        self.seed = None
        self.post_hits = 0
        self.post_total = 0

    def observe(self, token):
        self.obs_counts[token] += 1
        self.learning_ticks += 1
        if self.learning_ticks >= self.learning_window:
            self._crystallize()

    def _crystallize(self):
        total = sum(self.obs_counts.values())
        if total == 0:
            self.learning = False
            return
        cum = 0
        for ngram, count in self.obs_counts.most_common():
            self.spectrum.add(ngram)
            cum += count
            if cum / total >= TARGET_COVERAGE:
                break
        self.learning = False
        self.obs_counts.clear()

    def grow(self):
        self.consumed += 1

    def coverage(self):
        return self.post_hits / self.post_total if self.post_total > 0 else 0.0


def process(entity, token, tick, all_entities, events):
    if entity.learning:
        entity.observe(token)
        return
    entity.post_total += 1
    if token in entity.spectrum:
        entity.post_hits += 1
        entity.grow()
        return
    entity.rejected += 1
    if entity.children:
        process(entity.children[0], token, tick, all_entities, events)
        return
    if entity.depth >= MAX_DEPTH:
        return
    if entity.seed is None:
        entity.seed = Seed(tick)
    entity.seed.feed(token)
    if len(entity.seed.tokens) >= SEED_THRESHOLD:
        name = f"d{entity.depth + 1}_e{len(all_entities)}"
        child = Entity(name, depth=entity.depth + 1,
                       parent=entity, birth_tick=tick)
        for t in entity.seed.tokens:
            child.obs_counts[t] += 1
            child.learning_ticks += 1
        if child.learning_ticks >= child.learning_window:
            child._crystallize()
        entity.children.append(child)
        all_entities.append(child)
        events.append((tick, name, child.depth))
        entity.seed = None


# --- Tree Display ------------------------------------------------------------

def print_tree(entity, total, prefix="", is_last=True, max_depth=10):
    if entity.depth > max_depth:
        return
    pct = 100 * entity.consumed / total if total > 0 else 0
    spec = len(entity.spectrum)
    cov = entity.coverage()
    if entity.learning:
        status = f"learning ({entity.learning_ticks}/{entity.learning_window})"
    else:
        status = f"spec={spec} cov={cov:.0%}"
    born = f" born={entity.birth_tick}" if entity.depth > 0 else ""
    connector = "`-- " if entity.depth > 0 else ""
    print(f"{prefix}{connector}{entity.name}  "
          f"consumed={entity.consumed} ({pct:.1f}%)  "
          f"w={entity.learning_window}  {status}{born}")
    child_prefix = prefix + ("    " if is_last else "|   ")
    items = list(entity.children)
    if entity.seed:
        items = items + [entity.seed]
    for i, item in enumerate(items):
        last = (i == len(items) - 1)
        if isinstance(item, Entity):
            print_tree(item, total, child_prefix, last, max_depth)
        else:
            conn = "`-- " if last else "|-- "
            print(f"{child_prefix}{conn}[seed: "
                  f"{len(item.tokens)}/{SEED_THRESHOLD}]")
    if entity.depth == max_depth:
        deep = sum(1 for c in entity.children if c.depth > max_depth)
        if deep:
            print(f"{child_prefix}  ... {deep} deeper entities omitted")


def fmt_token(t):
    if len(t) <= 3 and all(isinstance(v, int) for v in t):
        if len(t) == 3:
            return f"({t[0]},{t[1]},{t[2]})"
        return repr(t)
    try:
        s = bytes(t).decode('ascii')
        if all(c.isprintable() or c in ' \n\t' for c in s):
            return repr(s)
    except Exception:
        pass
    return '(' + ','.join(f'{b:02x}' for b in t) + ')'


# --- Single Run --------------------------------------------------------------

def run_single(mode_name, token_iter, total_ticks, log_every=5000):
    """Run the cascade mechanism on a token stream. Returns result dict."""
    print(f"\n{'=' * 60}")
    print(f"{mode_name}")

    root = Entity("root", depth=0, birth_tick=0)
    all_entities = [root]
    events = []

    # Per-frame tracking for timeline (frame = tick for Mode B,
    # or tick/frame_pixels for Mode A)
    per_tick_depth = []

    t0 = time.time()
    for tick in range(total_ticks):
        token = next(token_iter)
        process(root, token, tick, all_entities, events)

        if (tick + 1) % log_every == 0:
            max_d = max(e.depth for e in all_entities)
            n_ent = len(all_entities)
            rate = (tick + 1) / (time.time() - t0)
            print(f"  t={tick + 1:>7}  entities={n_ent:>3}  depth={max_d}  "
                  f"root_consumed={root.consumed:>6}  ({rate:.0f} t/s)")

    elapsed = time.time() - t0
    max_depth = max(e.depth for e in all_entities)
    total_consumed = sum(e.consumed for e in all_entities)
    root_pct = 100 * root.consumed / total_consumed if total_consumed else 0

    consumed_depth = max((e.depth for e in all_entities if e.consumed > 0),
                         default=0)

    crystallized = [e for e in all_entities if not e.learning]
    avg_coverage = (sum(e.coverage() for e in crystallized) / len(crystallized)
                    if crystallized else 0.0)

    mass_by_depth = defaultdict(int)
    for e in all_entities:
        mass_by_depth[e.depth] += e.consumed

    print(f"\n  --- Result ---")
    print(f"  Depth: {max_depth}  Consumed depth: {consumed_depth}  "
          f"Entities: {len(all_entities)}")
    print(f"  Root consumed: {root.consumed} ({root_pct:.1f}%)  "
          f"Root window: {root.learning_window}")
    print(f"  Root spectrum: {len(root.spectrum)} tokens  "
          f"Root coverage: {root.coverage():.1%}")
    print(f"  Avg coverage: {avg_coverage:.1%}")
    print(f"  Time: {elapsed:.1f}s")

    # Show root spectrum
    if root.spectrum:
        sample = sorted(root.spectrum)[:8]
        print(f"  Root spectrum sample: "
              + ", ".join(fmt_token(t) for t in sample))

    print()
    print_tree(root, total_consumed)

    return {
        'mode': mode_name,
        'depth': max_depth,
        'consumed_depth': consumed_depth,
        'n_entities': len(all_entities),
        'root_pct': root_pct,
        'root_spectrum_size': len(root.spectrum),
        'avg_coverage': avg_coverage,
        'mass_by_depth': dict(mass_by_depth),
        'all_entities': all_entities,
        'events': events,
        'total_ticks': total_ticks,
        'elapsed': elapsed,
    }


# --- Plotting ----------------------------------------------------------------

def plot_results(results, diffs, frames, video_name):
    """Generate plots for all runs on one video source."""
    n_runs = len(results)
    fig, axes = plt.subplots(2, max(n_runs, 3), figsize=(6 * max(n_runs, 3), 10))
    if n_runs < 3:
        # Pad axes for consistent indexing
        pass
    fig.suptitle(
        f"Exp 118 v9: Video Frame Decomposition — {video_name}\n"
        f"{len(frames)} frames at {FRAME_SIZE[1]}x{FRAME_SIZE[0]}  "
        f"COVERAGE={TARGET_COVERAGE}  SEED={SEED_THRESHOLD}",
        fontsize=11)

    # --- Row 0: Mass by depth for each run ---
    for i, r in enumerate(results):
        ax = axes[0, i] if n_runs > 1 else axes[0]
        max_d = r['depth']
        if max_d == 0:
            ax.set_title(r['mode'])
            continue
        depths = list(range(max_d + 1))
        masses = [r['mass_by_depth'].get(d, 0) for d in depths]
        total = sum(masses)
        fracs = [m / total if total > 0 else 0 for m in masses]
        ax.bar(depths, fracs, color='steelblue', alpha=0.8)
        ax.set(xlabel='Depth', ylabel='Mass fraction',
               title=f"{r['mode']}\ndepth={max_d} cons_dep={r['consumed_depth']}")
        ax.set_xticks(depths)

    # Fill unused top panels with frame samples
    for i in range(n_runs, axes.shape[1]):
        ax = axes[0, i]
        if len(frames) > 0:
            ax.imshow(frames[0], cmap='gray', vmin=0, vmax=255)
            ax.set_title('Frame 0')
            ax.axis('off')

    # --- Row 1: Sample diff frames + entity activation ---
    # Show diff frames at key moments
    key_frames = [0, SCENE_CUT_FRAME - 2, SCENE_CUT_FRAME - 1,
                  min(SCENE_CUT_FRAME, len(diffs) - 1)]
    key_frames = [f for f in key_frames if f < len(diffs)]

    n_show = min(len(key_frames), axes.shape[1])
    for i in range(n_show):
        ax = axes[1, i]
        idx = key_frames[i]
        ax.imshow(diffs[idx], cmap='RdBu_r', vmin=0, vmax=255)
        ax.set_title(f'Diff frame {idx + 1}\n(128=no change)')
        ax.axis('off')

    # Fill remaining with entity formation timeline
    for i in range(n_show, axes.shape[1]):
        ax = axes[1, i]
        # Show formation events from last run
        r = results[-1]
        if r['events']:
            ticks = [t for t, _, _ in r['events']]
            depths = [d for _, _, d in r['events']]
            ax.scatter(ticks, depths, c='tab:orange', s=40,
                       edgecolors='k', linewidths=0.5)
            ax.set(xlabel='Tick', ylabel='Depth',
                   title=f"Entity formation\n({r['mode']})")

    plt.tight_layout()
    fig_path = os.path.join(OUT, f'v9_{video_name}.png')
    plt.savefig(fig_path, dpi=150)
    print(f"\nPlot: {fig_path}")


# --- Main --------------------------------------------------------------------

def run_on_video(video_name, frames):
    """Run all modes on a set of frames. Returns list of results."""
    print(f"\n{'#' * 60}")
    print(f"VIDEO: {video_name} ({len(frames)} frames, "
          f"{FRAME_SIZE[1]}x{FRAME_SIZE[0]})")
    print(f"{'#' * 60}")

    diffs = compute_frame_diffs(frames)
    print(f"  {len(diffs)} diff frames computed")

    # Stats on diff frames
    all_diff_bytes = np.concatenate([d.flatten() for d in diffs])
    no_change_frac = np.mean(np.abs(all_diff_bytes.astype(int) - 128) < 5)
    print(f"  No-change pixels (|delta| < 5): {no_change_frac:.1%}")

    results = []

    # --- Mode A: byte stream ---
    bytestream = diffs_to_bytestream(diffs)
    print(f"  Byte stream: {len(bytestream)} bytes")

    for n in NGRAM_SIZES:
        total_ticks = len(bytestream)  # process all bytes
        stream = ngram_stream(bytestream, n)
        log_every = max(1, total_ticks // 10)
        r = run_single(f"{video_name}/bytestream N={n}",
                        stream, total_ticks, log_every)
        r['video'] = video_name
        r['token_mode'] = 'bytestream'
        r['ngram_n'] = n
        results.append(r)

    # --- Mode B: spatial tokens ---
    # Pre-collect all tokens so we know the total count
    spatial_tokens = list(spatial_token_stream(diffs))
    total_ticks = len(spatial_tokens)
    print(f"\n  Spatial tokens: {total_ticks} "
          f"({TOKENS_PER_FRAME}/frame x {len(diffs)} frames)")

    stream = iter(spatial_tokens)
    log_every = max(1, total_ticks // 10)
    r = run_single(f"{video_name}/spatial",
                    stream, total_ticks, log_every)
    r['video'] = video_name
    r['token_mode'] = 'spatial'
    r['ngram_n'] = 0
    results.append(r)

    # --- Plots ---
    plot_results(results, diffs, frames, video_name)

    return results


def run():
    os.makedirs(OUT, exist_ok=True)

    all_results = []

    # --- Synthetic video ---
    print("Generating synthetic video...")
    syn_frames = generate_synthetic_video()
    print(f"  {len(syn_frames)} frames generated")
    syn_results = run_on_video("synthetic", syn_frames)
    all_results.extend(syn_results)

    # --- Real video (optional) ---
    real_path = None
    if len(sys.argv) > 1:
        real_path = sys.argv[1]
    elif os.path.exists(os.path.join(BASE, "data", "input.mp4")):
        real_path = os.path.join(BASE, "data", "input.mp4")
    elif os.path.exists(os.path.join(BASE, "input.mp4")):
        real_path = os.path.join(BASE, "input.mp4")

    if real_path:
        real_frames = load_real_video(real_path)
        if real_frames:
            real_results = run_on_video("real", real_frames)
            all_results.extend(real_results)

    # --- Summary Table ---
    print(f"\n{'=' * 100}")
    print("SUMMARY TABLE")
    print(f"{'=' * 100}")
    print(f"{'Mode':<30} {'Ticks':>8} {'Depth':>6} {'ConsDep':>8} "
          f"{'Entities':>9} {'Root%':>6} {'AvgCov':>7}")
    print('-' * 100)
    for r in all_results:
        print(f"{r['mode']:<30} {r['total_ticks']:>8} {r['depth']:>6} "
              f"{r['consumed_depth']:>8} "
              f"{r['n_entities']:>9} {r['root_pct']:>5.1f}% "
              f"{r['avg_coverage']:>6.1%}")

    # --- CSV ---
    csv_path = os.path.join(OUT, 'v9_summary.csv')
    with open(csv_path, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['mode', 'video', 'token_mode', 'ngram_n', 'total_ticks',
                     'depth', 'consumed_depth', 'n_entities', 'root_pct',
                     'root_spectrum_size', 'avg_coverage'])
        for r in all_results:
            w.writerow([r['mode'], r.get('video', ''),
                        r.get('token_mode', ''), r.get('ngram_n', ''),
                        r['total_ticks'], r['depth'], r['consumed_depth'],
                        r['n_entities'], f"{r['root_pct']:.2f}",
                        r['root_spectrum_size'],
                        f"{r['avg_coverage']:.4f}"])
    print(f"\nCSV: {csv_path}")

    # --- Entity CSV ---
    ent_csv = os.path.join(OUT, 'v9_entities.csv')
    with open(ent_csv, 'w', newline='') as f:
        w = csv.writer(f)
        w.writerow(['mode', 'name', 'depth', 'parent',
                     'learning_window', 'spectrum_size', 'coverage',
                     'consumed', 'rejected', 'birth_tick'])
        for r in all_results:
            for e in r['all_entities']:
                w.writerow([r['mode'], e.name, e.depth,
                            e.parent.name if e.parent else '',
                            e.learning_window, len(e.spectrum),
                            f"{e.coverage():.4f}",
                            e.consumed, e.rejected, e.birth_tick])
    print(f"Entity CSV: {ent_csv}")


if __name__ == '__main__':
    run()
