#!/usr/bin/env python3
"""
Experiment 118 v10: Store and Reconstruct — The Agent Test

Phase 1 (Store): Feed video through the v8/v9 cascade mechanism with
consumption logging — each entity records WHAT it consumed and WHEN.

Phase 2 (Reconstruct): An agent traverses the trie from root to leaves,
reads consumption logs, and reconstructs delta frames pixel by pixel.

Two modes:
  Mode A (bytestream N=1): exact pixel values, deterministic position
  Mode B (spatial tokens): self-locating (x,y,delta) but quantized

Quality measured by PSNR per frame and depth contribution analysis.
"""

import os
import sys
import math
import time
import csv
import numpy as np
from collections import Counter, defaultdict

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# --- Config ------------------------------------------------------------------
FRAME_SIZE       = (64, 64)    # h, w
FPS              = 24
DURATION         = 10
SCENE_CUT_FRAME  = 120
N_FRAMES         = FPS * DURATION

# Mode B spatial
SPATIAL_QUANT    = 8
DELTA_LEVELS     = 8
TOKENS_PER_FRAME = 64

# Mechanism
TARGET_COVERAGE  = 0.5
SEED_THRESHOLD   = 60
MAX_DEPTH        = 20

BASE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(BASE, "results")


# --- Video -------------------------------------------------------------------

def generate_synthetic_video(n_frames=N_FRAMES, size=FRAME_SIZE):
    h, w = size
    rng = np.random.RandomState(42)
    frames = []
    for t in range(n_frames):
        if t < SCENE_CUT_FRAME:
            bg = np.tile(np.linspace(40, 80, w), (h, 1)).astype(np.uint8)
        else:
            bg = np.tile(np.linspace(80, 40, w), (h, 1)).astype(np.uint8)
        frame = bg.copy()
        ax = int(t * (w - 8) / n_frames)
        frame[24:32, ax:ax + 8] = 220
        frame[48:56, 16:24] = 128
        noise = rng.normal(0, 5, size).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        frames.append(frame)
    return frames


def load_real_video(path, size=FRAME_SIZE):
    try:
        import cv2
    except ImportError:
        return None
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
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
    return frames if len(frames) > 1 else None


def compute_frame_diffs(frames):
    diffs = []
    for i in range(1, len(frames)):
        diff = frames[i].astype(np.int16) - frames[i - 1].astype(np.int16)
        diff = np.clip(diff + 128, 0, 255).astype(np.uint8)
        diffs.append(diff)
    return diffs


# --- Token Streams -----------------------------------------------------------

def ngram_stream_from_bytes(data, n):
    length = len(data)
    i = 0
    while True:
        yield tuple(data[(i + j) % length] for j in range(n))
        i += 1


def spatial_token_list(diffs, tokens_per_frame=TOKENS_PER_FRAME,
                       sq=SPATIAL_QUANT, dl=DELTA_LEVELS):
    h, w = diffs[0].shape
    x_step = max(1, w // sq)
    y_step = max(1, h // sq)
    tokens = []
    for diff in diffs:
        flat = diff.flatten()
        deviations = np.abs(flat.astype(np.int16) - 128)
        top_idx = np.argsort(deviations)[-tokens_per_frame:]
        for idx in top_idx:
            y, x = divmod(int(idx), w)
            val = int(diff[y, x])
            x_q = x // x_step
            y_q = y // y_step
            delta_q = val * dl // 256
            tokens.append((x_q, y_q, delta_q))
    return tokens


# --- Entity Model (v8 + consumption logging) ---------------------------------

class Seed:
    __slots__ = ('tokens', 'birth_tick')
    def __init__(self, tick):
        self.tokens = []        # [(tick, token), ...]
        self.birth_tick = tick
    def feed(self, token, tick):
        self.tokens.append((tick, token))


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
        self.consumption_log = []  # [(tick, token), ...]
        self.learning_log = []     # [(tick, token), ...] — preserves position during learning

    def observe(self, token, tick):
        self.obs_counts[token] += 1
        self.learning_ticks += 1
        self.learning_log.append((tick, token))
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

    def grow(self, tick, token):
        self.consumed += 1
        self.consumption_log.append((tick, token))

    def coverage(self):
        return self.post_hits / self.post_total if self.post_total > 0 else 0.0


def process(entity, token, tick, all_entities, events):
    if entity.learning:
        entity.observe(token, tick)
        return
    entity.post_total += 1
    if token in entity.spectrum:
        entity.post_hits += 1
        entity.grow(tick, token)
        return
    entity.rejected += 1
    if entity.children:
        process(entity.children[0], token, tick, all_entities, events)
        return
    if entity.depth >= MAX_DEPTH:
        return
    if entity.seed is None:
        entity.seed = Seed(tick)
    entity.seed.feed(token, tick)
    if len(entity.seed.tokens) >= SEED_THRESHOLD:
        name = f"d{entity.depth + 1}_e{len(all_entities)}"
        child = Entity(name, depth=entity.depth + 1,
                       parent=entity, birth_tick=tick)
        # Transfer seed's tick-stamped tokens to child's learning_log
        for seed_tick, seed_token in entity.seed.tokens:
            child.obs_counts[seed_token] += 1
            child.learning_ticks += 1
            child.learning_log.append((seed_tick, seed_token))
        if child.learning_ticks >= child.learning_window:
            child._crystallize()
        entity.children.append(child)
        all_entities.append(child)
        events.append((tick, name, child.depth))
        entity.seed = None


# --- Phase 1: Store ----------------------------------------------------------

def store_bytestream(diffs):
    """Run cascade on flattened diff bytes (N=1). Returns entities + metadata."""
    bytestream = b''.join(d.tobytes() for d in diffs)
    total_ticks = len(bytestream)
    pixels_per_frame = FRAME_SIZE[0] * FRAME_SIZE[1]

    print(f"\n  Phase 1 — Store (bytestream N=1, {total_ticks} bytes)")
    root = Entity("root", depth=0, birth_tick=0)
    all_entities = [root]
    events = []
    stream = ngram_stream_from_bytes(bytestream, 1)

    t0 = time.time()
    log_every = max(1, total_ticks // 5)
    for tick in range(total_ticks):
        token = next(stream)
        process(root, token, tick, all_entities, events)
        if (tick + 1) % log_every == 0:
            n_ent = len(all_entities)
            max_d = max(e.depth for e in all_entities)
            print(f"    t={tick+1:>7}/{total_ticks}  entities={n_ent}  "
                  f"depth={max_d}  root_consumed={root.consumed}")

    elapsed = time.time() - t0
    total_consumed = sum(e.consumed for e in all_entities)
    print(f"  Stored in {elapsed:.1f}s  "
          f"consumed={total_consumed}/{total_ticks} "
          f"({100*total_consumed/total_ticks:.1f}%)")
    return all_entities, pixels_per_frame, total_ticks


def store_spatial(diffs):
    """Run cascade on spatial tokens. Returns entities + metadata."""
    tokens = spatial_token_list(diffs)
    total_ticks = len(tokens)

    print(f"\n  Phase 1 — Store (spatial, {total_ticks} tokens)")
    root = Entity("root", depth=0, birth_tick=0)
    all_entities = [root]
    events = []

    t0 = time.time()
    log_every = max(1, total_ticks // 5)
    for tick in range(total_ticks):
        token = tokens[tick]
        process(root, token, tick, all_entities, events)
        if (tick + 1) % log_every == 0:
            n_ent = len(all_entities)
            max_d = max(e.depth for e in all_entities)
            print(f"    t={tick+1:>7}/{total_ticks}  entities={n_ent}  "
                  f"depth={max_d}  root_consumed={root.consumed}")

    elapsed = time.time() - t0
    total_consumed = sum(e.consumed for e in all_entities)
    print(f"  Stored in {elapsed:.1f}s  "
          f"consumed={total_consumed}/{total_ticks} "
          f"({100*total_consumed/total_ticks:.1f}%)")
    return all_entities, TOKENS_PER_FRAME, total_ticks


# --- Phase 2: Reconstruct ----------------------------------------------------

def reconstruct_bytestream(all_entities, n_diff_frames, pixels_per_frame):
    """Reconstruct delta frames from bytestream entity logs (consumed + learning)."""
    print(f"\n  Phase 2 — Reconstruct (bytestream)")
    recon = np.full((n_diff_frames, pixels_per_frame), 128, dtype=np.uint8)

    # Track which depth contributed each pixel
    depth_map = np.full((n_diff_frames, pixels_per_frame), -1, dtype=np.int8)

    pixels_consumed = 0
    pixels_from_learning = 0
    for entity in all_entities:
        # Consumed tokens (post-crystallization — exact spectrum match)
        for tick, token in entity.consumption_log:
            frame_idx = tick // pixels_per_frame
            pixel_pos = tick % pixels_per_frame
            if frame_idx < n_diff_frames:
                recon[frame_idx, pixel_pos] = token[0]
                depth_map[frame_idx, pixel_pos] = entity.depth
                pixels_consumed += 1
        # Learning-phase tokens (pre-crystallization — position preserved)
        for tick, token in entity.learning_log:
            frame_idx = tick // pixels_per_frame
            pixel_pos = tick % pixels_per_frame
            if frame_idx < n_diff_frames:
                recon[frame_idx, pixel_pos] = token[0]
                depth_map[frame_idx, pixel_pos] = entity.depth
                pixels_from_learning += 1

    total_pixels = n_diff_frames * pixels_per_frame
    total_placed = pixels_consumed + pixels_from_learning
    print(f"  Placed {total_placed}/{total_pixels} pixels "
          f"({100*total_placed/total_pixels:.1f}%)")
    print(f"    from consumption: {pixels_consumed}")
    print(f"    from learning:    {pixels_from_learning}")

    # Reshape to 2D frames
    h, w = FRAME_SIZE
    recon_frames = [recon[i].reshape(h, w) for i in range(n_diff_frames)]
    depth_frames = [depth_map[i].reshape(h, w) for i in range(n_diff_frames)]
    return recon_frames, depth_frames


def reconstruct_spatial(all_entities, n_diff_frames):
    """Reconstruct delta frames from spatial entity logs (consumed + learning)."""
    print(f"\n  Phase 2 — Reconstruct (spatial)")
    h, w = FRAME_SIZE
    recon = [np.full((h, w), 128, dtype=np.uint8) for _ in range(n_diff_frames)]
    depth_frames = [np.full((h, w), -1, dtype=np.int8) for _ in range(n_diff_frames)]

    patch_h = h // SPATIAL_QUANT
    patch_w = w // SPATIAL_QUANT
    pixels_consumed = 0
    pixels_from_learning = 0

    def place_token(frame_idx, token, entity_depth, is_learning):
        nonlocal pixels_consumed, pixels_from_learning
        if frame_idx >= n_diff_frames:
            return
        x_q, y_q, delta_q = token
        delta_val = (delta_q * 256 + 128) // DELTA_LEVELS
        y0, y1 = y_q * patch_h, (y_q + 1) * patch_h
        x0, x1 = x_q * patch_w, (x_q + 1) * patch_w
        recon[frame_idx][y0:y1, x0:x1] = delta_val
        depth_frames[frame_idx][y0:y1, x0:x1] = entity_depth
        if is_learning:
            pixels_from_learning += patch_h * patch_w
        else:
            pixels_consumed += patch_h * patch_w

    for entity in all_entities:
        for tick, token in entity.consumption_log:
            place_token(tick // TOKENS_PER_FRAME, token, entity.depth, False)
        for tick, token in entity.learning_log:
            place_token(tick // TOKENS_PER_FRAME, token, entity.depth, True)

    total_pixels = n_diff_frames * h * w
    total_placed = pixels_consumed + pixels_from_learning
    print(f"  Placed {total_placed}/{total_pixels} pixel-equivalents "
          f"({100*total_placed/total_pixels:.1f}%)")
    print(f"    from consumption: {pixels_consumed}")
    print(f"    from learning:    {pixels_from_learning}")
    return recon, depth_frames


def deltas_to_frames(delta_frames, first_frame):
    """Convert delta frames back to video frames using first frame as anchor."""
    frames = [first_frame.copy()]
    for delta in delta_frames:
        signed = delta.astype(np.int16) - 128
        new = np.clip(frames[-1].astype(np.int16) + signed, 0, 255)
        frames.append(new.astype(np.uint8))
    return frames


# --- Quality Metrics ---------------------------------------------------------

def compute_psnr(original, reconstructed):
    mse = np.mean((original.astype(float) - reconstructed.astype(float)) ** 2)
    if mse == 0:
        return float('inf')
    return 10 * math.log10(255.0 ** 2 / mse)


def compute_depth_contribution(depth_frames, original_diffs, recon_diffs):
    """How much each depth level contributes to reconstruction quality."""
    max_d = max(d.max() for d in depth_frames)
    contrib = {}
    for d in range(-1, max_d + 1):
        pixel_count = sum(np.sum(df == d) for df in depth_frames)
        # Compute error for pixels at this depth
        errors = []
        for orig, rec, dm in zip(original_diffs, recon_diffs, depth_frames):
            mask = dm == d
            if mask.any():
                err = np.mean(np.abs(orig[mask].astype(float) -
                                     rec[mask].astype(float)))
                errors.append(err)
        avg_error = np.mean(errors) if errors else 0
        label = "unplaced" if d == -1 else f"depth_{d}"
        contrib[label] = {
            'pixels': pixel_count,
            'avg_error': avg_error,
        }
    return contrib


# --- Plotting ----------------------------------------------------------------

def plot_reconstruction(video_name, mode_name, original_frames, recon_frames,
                        psnr_values, depth_contrib):
    """Generate side-by-side comparison plot."""
    # Pick representative frames
    n = len(original_frames)
    indices = [0, n // 4, n // 2, 3 * n // 4, n - 1]
    indices = [i for i in indices if i < n]
    n_show = len(indices)

    fig, axes = plt.subplots(4, max(n_show, 3), figsize=(4 * max(n_show, 3), 14))
    fig.suptitle(
        f"v10: Store & Reconstruct — {video_name} / {mode_name}\n"
        f"Mean PSNR: {np.mean(psnr_values):.1f} dB", fontsize=12)

    # Row 0: original frames
    for i, idx in enumerate(indices):
        axes[0, i].imshow(original_frames[idx], cmap='gray', vmin=0, vmax=255)
        axes[0, i].set_title(f'Original #{idx}', fontsize=8)
        axes[0, i].axis('off')
    axes[0, 0].set_ylabel('Original', fontsize=10)

    # Row 1: reconstructed frames
    for i, idx in enumerate(indices):
        axes[1, i].imshow(recon_frames[idx], cmap='gray', vmin=0, vmax=255)
        axes[1, i].set_title(f'PSNR={psnr_values[idx]:.1f}dB', fontsize=8)
        axes[1, i].axis('off')
    axes[1, 0].set_ylabel('Reconstructed', fontsize=10)

    # Row 2: error heatmaps
    for i, idx in enumerate(indices):
        err = np.abs(original_frames[idx].astype(float) -
                     recon_frames[idx].astype(float))
        axes[2, i].imshow(err, cmap='hot', vmin=0, vmax=60)
        axes[2, i].set_title(f'MAE={np.mean(err):.1f}', fontsize=8)
        axes[2, i].axis('off')
    axes[2, 0].set_ylabel('Error', fontsize=10)

    # Row 3: PSNR over time + depth contribution
    # PSNR timeline
    ax = axes[3, 0]
    ax.plot(psnr_values, 'b-', lw=0.8)
    ax.set(xlabel='Frame', ylabel='PSNR (dB)', title='PSNR over time')
    ax.axhline(y=np.mean(psnr_values), color='r', ls='--', lw=0.5)

    # Depth contribution
    ax = axes[3, 1]
    labels = sorted(depth_contrib.keys())
    pixels = [depth_contrib[l]['pixels'] for l in labels]
    total_px = sum(pixels)
    fracs = [p / total_px if total_px > 0 else 0 for p in pixels]
    ax.bar(range(len(labels)), fracs, color='steelblue', alpha=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6, rotation=45)
    ax.set(ylabel='Pixel fraction', title='Depth contribution')

    # Depth error
    ax = axes[3, 2]
    errors = [depth_contrib[l]['avg_error'] for l in labels]
    ax.bar(range(len(labels)), errors, color='coral', alpha=0.8)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, fontsize=6, rotation=45)
    ax.set(ylabel='Avg pixel error', title='Error by depth')

    # Hide unused
    for i in range(3, axes.shape[1]):
        if i >= 3:
            axes[3, i].axis('off')
    for row in range(3):
        for i in range(n_show, axes.shape[1]):
            axes[row, i].axis('off')

    plt.tight_layout()
    safe = mode_name.replace('/', '_').replace(' ', '_')
    fig_path = os.path.join(OUT, f'v10_{video_name}_{safe}.png')
    plt.savefig(fig_path, dpi=150)
    print(f"  Plot: {fig_path}")


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


# --- Main: run one video -----------------------------------------------------

def run_video(video_name, frames):
    print(f"\n{'#' * 60}")
    print(f"VIDEO: {video_name} ({len(frames)} frames)")
    print(f"{'#' * 60}")

    first_frame = frames[0].copy()
    diffs = compute_frame_diffs(frames)
    n_diff = len(diffs)
    print(f"  {n_diff} diff frames, first frame saved as anchor")

    results = []

    # ===== Mode A: Bytestream N=1 =====
    print(f"\n{'=' * 50}")
    print("MODE A: Bytestream N=1")
    print(f"{'=' * 50}")

    entities_a, ppf, total_ticks = store_bytestream(diffs)
    total_consumed = sum(e.consumed for e in entities_a)
    print_tree(entities_a[0], total_consumed)

    recon_diffs_a, depth_a = reconstruct_bytestream(entities_a, n_diff, ppf)
    recon_frames_a = deltas_to_frames(recon_diffs_a, first_frame)

    # Match lengths (recon has n_diff+1 frames including anchor)
    orig_for_compare = frames[:len(recon_frames_a)]
    psnr_a = [compute_psnr(o, r) for o, r in
              zip(orig_for_compare, recon_frames_a)]
    mean_psnr_a = np.mean([p for p in psnr_a if p != float('inf')])

    depth_contrib_a = compute_depth_contribution(depth_a, diffs, recon_diffs_a)

    print(f"\n  Mean PSNR: {mean_psnr_a:.1f} dB")
    print(f"  Depth contribution:")
    for label in sorted(depth_contrib_a.keys()):
        c = depth_contrib_a[label]
        print(f"    {label:<12} {c['pixels']:>8} pixels  "
              f"avg_error={c['avg_error']:.2f}")

    plot_reconstruction(video_name, "bytestream_N1",
                        orig_for_compare, recon_frames_a,
                        psnr_a, depth_contrib_a)

    results.append({
        'mode': 'bytestream_N1',
        'mean_psnr': mean_psnr_a,
        'n_entities': len(entities_a),
        'consumed_frac': total_consumed / total_ticks,
        'depth': max(e.depth for e in entities_a),
    })

    # ===== Mode B: Spatial =====
    print(f"\n{'=' * 50}")
    print("MODE B: Spatial tokens")
    print(f"{'=' * 50}")

    entities_b, tpf, total_ticks_b = store_spatial(diffs)
    total_consumed_b = sum(e.consumed for e in entities_b)
    print_tree(entities_b[0], total_consumed_b)

    recon_diffs_b, depth_b = reconstruct_spatial(entities_b, n_diff)
    recon_frames_b = deltas_to_frames(recon_diffs_b, first_frame)

    orig_for_compare_b = frames[:len(recon_frames_b)]
    psnr_b = [compute_psnr(o, r) for o, r in
              zip(orig_for_compare_b, recon_frames_b)]
    mean_psnr_b = np.mean([p for p in psnr_b if p != float('inf')])

    depth_contrib_b = compute_depth_contribution(depth_b, diffs, recon_diffs_b)

    print(f"\n  Mean PSNR: {mean_psnr_b:.1f} dB")
    print(f"  Depth contribution:")
    for label in sorted(depth_contrib_b.keys()):
        c = depth_contrib_b[label]
        print(f"    {label:<12} {c['pixels']:>8} pixels  "
              f"avg_error={c['avg_error']:.2f}")

    plot_reconstruction(video_name, "spatial",
                        orig_for_compare_b, recon_frames_b,
                        psnr_b, depth_contrib_b)

    results.append({
        'mode': 'spatial',
        'mean_psnr': mean_psnr_b,
        'n_entities': len(entities_b),
        'consumed_frac': total_consumed_b / total_ticks_b,
        'depth': max(e.depth for e in entities_b),
    })

    # ===== Summary =====
    print(f"\n{'=' * 60}")
    print(f"RECONSTRUCTION SUMMARY — {video_name}")
    print(f"{'=' * 60}")
    print(f"{'Mode':<20} {'PSNR':>8} {'Entities':>9} {'Consumed':>9} {'Depth':>6}")
    print('-' * 60)
    for r in results:
        print(f"{r['mode']:<20} {r['mean_psnr']:>7.1f}dB "
              f"{r['n_entities']:>9} {r['consumed_frac']:>8.1%} "
              f"{r['depth']:>6}")

    return results


def run():
    os.makedirs(OUT, exist_ok=True)

    # Find the real video
    real_path = None
    if len(sys.argv) > 1:
        real_path = sys.argv[1]
    else:
        for candidate in [
            os.path.join(BASE, "data", "input.mp4"),
            os.path.join(BASE, "input.mp4"),
            os.path.join(os.path.dirname(BASE), "v9", "data", "input.mp4"),
        ]:
            if os.path.exists(candidate):
                real_path = candidate
                break

    if real_path:
        print(f"Loading real video: {real_path}")
        frames = load_real_video(real_path)
        if frames:
            print(f"  {len(frames)} frames loaded")
            run_video("real", frames)
        else:
            print("  Failed to load video, falling back to synthetic")
            frames = generate_synthetic_video()
            run_video("synthetic", frames)
    else:
        print("No video found, using synthetic")
        frames = generate_synthetic_video()
        run_video("synthetic", frames)


if __name__ == '__main__':
    run()
