# Experiment 118 v10: Store and Reconstruct — The Agent Test

## Purpose

v9 demonstrated that the consumption-transformation trie decomposes video into
temporal persistence layers. The root learns "no change," children handle
increasing magnitudes of change, deeper entities capture fine detail. The trie
IS the decomposition. But v9 only stored — it never retrieved.

**v10 tests the other half: can a single agent, traversing the stored trie from
root to leaves, reconstruct the original video from the deposit history?**

This is the test that proves the trie is a functional memory, not just a
classifier. Any system can categorize. The question is: does the categorization
preserve enough information to reconstruct the original signal?

Additionally: **how much space does the trie representation take compared to
the original video?** If the trie compresses, it proves the consumption mechanism
found redundancy. If it expands, we learn what overhead the hierarchy costs.

---

## Key Insight: The Model Is Useless Without the Agent

The trie from v9 is a dead structure. Deposits sit on connectors. Entities have
spectra. Nodes are claimed. But nothing is happening. Without an agent traversing
it, making comparisons, consuming deposits and accumulating state, the trie is
a book nobody reads.

The agent is the reader. It starts at the root with zero knowledge and builds
understanding by traversing the hierarchy, reading deposits at each level,
and accumulating layers of detail. The reconstruction IS the traversal.

This is why v10 has two distinct phases:
- **Phase 1 (Store):** Build the trie from v9's mechanism. This is the model.
- **Phase 2 (Reconstruct):** Send an agent through the trie. This is the reader.

Neither phase works without the other.

---

## Design

### Phase 1: Store (reuse v9 mechanism)

Run v9's consumption-transformation on a video (synthetic or real). The trie
forms with entities at multiple depths, each having consumed specific patterns
from the stream.

At the end of Phase 1, save the complete trie state:
- Every entity: depth, spectrum, consumed count, parent
- Every entity's consumed deposits: the actual token values it consumed, in order
- Every entity's rejected deposits: what it passed to its child

This is the "written memory." The book on the shelf.

### Phase 2: Reconstruct (NEW — the agent)

A reconstruction agent starts at the root with an empty frame buffer. It
traverses the trie from root to deepest leaf, and at each depth level reads
what that entity consumed. It uses the consumed deposits to reconstruct the
video frame by frame.

#### The Reconstruction Logic

The key insight: each entity consumed specific tokens at specific ticks (frames).
The entity's consumption log is a record of WHAT it recognized and WHEN. The
agent reads these logs depth by depth and layers them together:

```python
class ReconstructionAgent:
    def __init__(self, trie, frame_shape=(64, 64)):
        self.trie = trie
        self.frame_shape = frame_shape
        self.frames = {}

    def reconstruct(self):
        """Traverse trie root to leaves, accumulating frame data."""
        self._visit(self.trie.root, depth=0)
        return self.frames

    def _visit(self, entity, depth):
        """Read this entity's consumption log and add to reconstruction."""
        for frame_idx, token in entity.consumption_log:
            if frame_idx not in self.frames:
                self.frames[frame_idx] = np.full(
                    self.frame_shape, 128, dtype=np.uint8
                )
            self._apply_token(self.frames[frame_idx], token, depth)

        for child in entity.children:
            self._visit(child, depth + 1)
```

#### Reconstruction Modes

**Mode A — Bytestream reconstruction:**

Each entity consumed bytes at sequential positions in the flattened frame.
Each consumed token must be logged with its frame index AND position:

```python
consumption_log.append({
    'frame': current_frame_index,
    'position': byte_position_in_frame,  # 0 to 4095 for 64x64
    'value': byte_value,
    'tick': current_tick,
})
```

**Mode B — Spatial reconstruction (RECOMMENDED):**

Spatial tokens are self-locating — position is part of the token:

```python
for entry in entity.consumption_log:
    frame_idx = entry['frame']
    x, y, val = entry['token']
    frame[y * 8 : y * 8 + 8, x * 8 : x * 8 + 8] = val
```

#### Applying Delta Frames to Reconstruct Video

The trie stores DELTA frames. To reconstruct actual frames:

```python
def deltas_to_frames(delta_frames, first_frame):
    frames = [first_frame]
    for delta in sorted(delta_frames.keys()):
        signed_delta = delta_frames[delta].astype(int) - 128
        new_frame = np.clip(
            frames[-1].astype(int) + signed_delta, 0, 255
        ).astype(np.uint8)
        frames.append(new_frame)
    return frames
```

**Important:** Store the first raw frame separately as anchor (I-frame).

---

## Storage Size Comparison (CRITICAL MEASUREMENT)

This is the question that determines whether the trie is a viable storage format
or just an interesting decomposition.

### What to Measure

**Original video size:**
```python
# Raw uncompressed frames
raw_size = n_frames * height * width * bytes_per_pixel
# e.g., 240 frames × 64 × 64 × 1 byte (grayscale) = 983,040 bytes

# Compressed mp4 (if input was mp4)
mp4_size = os.path.getsize(input_video_path)
```

**Trie storage size — measure EVERY component:**
```python
# 1. First frame (I-frame anchor) — stored raw
anchor_size = height * width  # e.g., 4,096 bytes for 64x64

# 2. Entity metadata (spectra, parent pointers, depth)
entity_meta_size = 0
for entity in all_entities:
    entity_meta_size += len(entity.spectrum) * bytes_per_token  # spectrum
    entity_meta_size += 8  # parent pointer, depth, etc.

# 3. Consumption logs — THIS IS THE BIG ONE
log_size = 0
for entity in all_entities:
    for entry in entity.consumption_log:
        # Each entry: frame_index (2 bytes) + token (N bytes) + position (2 bytes)
        log_size += 2 + token_size + 2  # adjust for actual token representation

# 4. Total trie storage
trie_total = anchor_size + entity_meta_size + log_size
```

### Report Format

```
=== STORAGE COMPARISON ===

Original video:
  Raw (uncompressed):    983,040 bytes  (240 frames × 64×64 × 1 byte)
  MP4 (H.264 compressed): XX,XXX bytes  (if available)

Trie storage:
  Anchor frame:            4,096 bytes
  Entity metadata:         X,XXX bytes  (N entities × avg_spectrum_size)
  Consumption logs:      XXX,XXX bytes  (total logged entries × entry_size)
  ─────────────────────────────────
  Total trie:            XXX,XXX bytes

Compression ratios:
  Trie / Raw:              X.XXx  (< 1.0 = trie is smaller)
  Trie / MP4:              X.XXx  (< 1.0 = trie beats H.264... unlikely but worth checking)

Breakdown by depth:
  depth 0 (root):   XXX,XXX bytes  (XX.X% of trie)  consumed XX.X% of tokens
  depth 1:          XXX,XXX bytes  (XX.X% of trie)  consumed XX.X% of tokens
  depth 2:          XXX,XXX bytes  (XX.X% of trie)  consumed XX.X% of tokens
  ...

Information density:
  Bytes per frame (raw):        4,096
  Bytes per frame (trie):       X,XXX
  Bytes per consumed token:     X.XX
  Tokens per frame (original):  4,096  (one per pixel)
  Tokens per frame (consumed):  X,XXX  (sum across all entities)
  Coverage:                     XX.X%  (consumed / total tokens)
```

### What the Comparison Tells Us

**If trie < raw (compression ratio < 1.0):**
The trie found redundancy. Static pixels were consumed once by the root and
not re-stored every frame. Repeating motion patterns were consumed once by
their entity. The trie IS compressing, and the compression comes from the
consumption mechanism itself — not from a compression algorithm applied
afterward. This is the key result.

**If trie ≈ raw (ratio near 1.0):**
The trie preserved all information but didn't compress. The consumption log
is roughly as large as the original data. The hierarchy adds structure
(searchable, layered) but not compression. This is still useful — it's an
indexed version of the video, not a smaller one.

**If trie > raw (ratio > 1.0):**
The trie expanded the data. Entity metadata and logging overhead exceed
the savings from consumption. This is expected for short videos with many
entities — the overhead is amortized over longer streams. Report the
crossover point: how long would the video need to be for the trie to break
even?

**Compare trie vs H.264:**
H.264 is the world's most optimized video codec, developed over decades.
The trie will almost certainly lose this comparison for actual compression
ratio. BUT: H.264 is a black box — you can't query it, can't retrieve by
temporal layer, can't do similarity search within it. The trie is an
indexed, queryable, hierarchically organized representation. The comparison
is not "which is smaller" but "what can you DO with each representation."

### Progressive Reconstruction Size

An interesting additional measurement: what is the trie storage size at each
depth level? This shows how much data the agent needs to read for each quality
tier:

```
Depth 0 only:    X,XXX bytes → PSNR XX dB  (just background)
Depth 0+1:       X,XXX bytes → PSNR XX dB  (background + coarse motion)
Depth 0+1+2:     X,XXX bytes → PSNR XX dB  (+ medium detail)
Full depth:    XXX,XXX bytes → PSNR XX dB  (complete reconstruction)
```

This is the trie's killer feature over flat storage: you can get a coarse
answer by reading only the first few levels. H.264 can't do this — you need
the complete bitstream to decode any frame.

---

## Quality Metrics

### Per-frame metrics:

**PSNR (Peak Signal-to-Noise Ratio):**
```python
mse = np.mean((original - reconstructed) ** 2)
psnr = 10 * np.log10(255**2 / mse) if mse > 0 else float('inf')
```
- PSNR > 40 dB: excellent (nearly lossless)
- PSNR 30-40 dB: good (minor artifacts)
- PSNR 20-30 dB: poor (visible degradation)
- PSNR < 20 dB: bad (major loss)

**SSIM (Structural Similarity Index):**
```python
from skimage.metrics import structural_similarity as ssim
score = ssim(original, reconstructed)
```

**Pixel error histogram:**
Distribution of |original - reconstructed| across all pixels.

### Depth contribution analysis:

For each depth level, measure:
- How many pixels does this level contribute to the reconstruction?
- What is the PSNR improvement from adding this level?
- Storage bytes at this level vs PSNR gain (bits per dB)

---

## Parameters

```python
# Video (same as v9)
VIDEO_SOURCE = "synthetic"  # or path to real video
FRAME_SIZE = (64, 64)
FPS = 24
DURATION = 10

# Tokenization (use spatial mode for self-locating tokens)
TOKEN_MODE = "spatial"
TOKENS_PER_FRAME = 100
QUANTIZE_STEP = 8

# Trie building (from v8/v9)
N_NODES = 10000
COVERAGE = 0.5
GROWTH_COST = 5
PLANET_THRESHOLD = 30
REJECTION_HOPS = 5
EXTEND_RATE = 0.01

# Phase 1
STORE_TICKS = DURATION * FPS  # 240 for 10s at 24fps

# Phase 2 — no parameters, agent just reads
```

---

## Implementation Plan

### Step 1: Modify v9 to Log Consumption Details

Each consumed token logged with frame index, token value, and position.

### Step 2: Store First Frame Separately

First raw frame saved as anchor before delta computation.

### Step 3: Implement Reconstruction Agent

Traverse trie root to leaves, reading consumption logs, layering tokens
into frame buffers.

### Step 4: Compare and Measure

Compute PSNR, SSIM per frame. Compute storage sizes for all components.
Generate the storage comparison report.

### Step 5: Progressive Reconstruction

Reconstruct at each depth level (depth 0 only, depth 0+1, depth 0+1+2, ...)
and measure PSNR at each level. This shows the quality-vs-storage tradeoff
curve — the trie's unique capability.

---

## Output

### Visual output:
1. **Side-by-side frames:** Original | Reconstructed | Error heatmap
   Show 6-8 representative frames.

2. **PSNR/SSIM over time:** Line plot per frame.

3. **Progressive reconstruction:** Same frame at depth 0, 0+1, 0+1+2, ..., full.
   Shows how quality builds with depth.

4. **Storage comparison chart:** Bar chart of raw vs mp4 vs trie, broken down
   by component (anchor, metadata, logs per depth).

5. **Quality vs storage curve:** PSNR (y-axis) vs cumulative bytes read (x-axis)
   for progressive reconstruction. Shows the trie's rate-distortion curve.

### Data output:
- Per-frame CSV: `frame, psnr, ssim, pixels_from_d0, pixels_from_d1, ...`
- Per-entity CSV: `entity, depth, tokens_consumed, tokens_rejected, storage_bytes`
- Storage summary CSV: `component, bytes, fraction`
- Progressive CSV: `max_depth, cumulative_bytes, psnr, ssim`

---

## Expected Results

### Storage prediction:
The trie should compress RELATIVE TO RAW for videos with lots of static content
(real video with background >> motion). The root consumes "no change" for ~60%
of all pixels — those pixels are stored ONCE in the root's spectrum, not
per-frame. That alone should give ~2-3× compression vs raw for static frames.

The trie will NOT beat H.264. H.264 uses motion estimation, DCT, entropy coding,
and 30 years of optimization. The trie uses three-branch comparison and
append-only logging. The comparison is interesting but the outcome is known.

The interesting comparison is **trie vs raw, per depth level** — showing that
the consumption mechanism naturally allocates more storage to complex content
(motion, detail) and less to simple content (static background).

### Quality prediction:
- Mode B (spatial): PSNR 25-35 dB (spatial tokens preserve position)
- Mode A (bytestream): PSNR 15-25 dB (position information partially lost)
- Progressive: root alone gives PSNR ~20 dB; each depth adds 2-5 dB

---

## Connection to Model-C v16

If the agent can reconstruct video from the trie:
- `store()` = Phase 1 (feed data through consumption-transformation)
- `retrieve()` = Phase 2 (agent traverses trie, reads deposits)
- Progressive retrieval = stop at any depth for coarse-to-fine answers
- Storage overhead = the cost of having an indexed, queryable representation

The trie is not trying to beat H.264 at compression. It's trying to be a
**queryable, hierarchically indexed, progressively retrievable** representation
that H.264 cannot be. You can't ask H.264 "what moved in frame 120?" You can
ask the trie — it's depth 1-2 entities that activated at frame 120.

---

## Experimental Results (March 22, 2026)

### Setup

- **Video:** Real video clip (family photo scene), 284 frames, downsampled to
  64×64 grayscale. Original mp4: 34.5 MB.
- **Mechanism:** v8 cascade with causal window (`learning_window = max(1, birth_tick)`),
  `TARGET_COVERAGE=0.5`, `SEED_THRESHOLD=60`, `MAX_DEPTH=20`.
- **Mode A:** Bytestream N=1 — frame diffs flattened to 1,159,168 bytes, fed as
  single-byte tokens through the cascade. Each tick maps deterministically to
  `frame_idx = tick // 4096, pixel_pos = tick % 4096`.
- **Mode B:** Spatial tokens — 64 quantized `(x_q, y_q, delta_q)` tokens per frame
  (8×8 spatial grid, 8 delta levels), 18,112 tokens total.

### Trie Structure (Mode A)

```
root       consumed=255,385 (22.0%)  w=1    spec=1   cov=22%  → learned (128,) = "no change"
  d1_e1    consumed=261,577 (22.6%)  w=131  spec=4   cov=29%  → small delta values near 128
    d2_e2  consumed=304,546 (26.3%)  w=481  spec=12  cov=47%  → medium deltas
      d3   consumed=154,971 (13.4%)  w=1808 spec=19  cov=46%  → larger changes
        d4 consumed= 88,038 ( 7.6%)  w=8358 spec=34  cov=51%  → significant motion
          d5 consumed=12,097 ( 1.0%)  w=59756 spec=41 cov=50%  → rare large changes
            d6 learning (12,019/805,802)                        → never crystallized
```

Root learned the single byte `(128,)` — "nothing changed at this pixel." This one
pattern accounts for 22% of all pixels across all frames. The hierarchy peels off
increasingly rare delta magnitudes, with coverage improving at each depth
(22% → 29% → 47% → 46% → 51% → 50%).

### First Run: Information Loss During Learning

**Initial PSNR: 11.9 dB (poor)** despite 92.9% of pixels placed with zero error.

Root cause analysis traced every unplaced pixel:

```
Entity     Learning window    Pixels absorbed (lost)    % of loss
d5_e5           59,756              59,756                72.4%
d4_e4            8,358               8,358                10.1%
d6_e6      805,802 (!)              12,019                14.6%
d3_e3            1,808               1,808                 2.2%
d2_e2              481                 481                 0.6%
d1_e1              131                 131                 0.2%
root                 1                   1                 0.0%
                                    ------
TOTAL                               82,554               100.0%
```

**All 82,554 unplaced pixels = all learning-absorbed pixels. Exact match. Zero dropped.**

The problem: `Entity.observe()` aggregated tokens into a `Counter` (`obs_counts[token] += 1`),
which records WHAT was seen and HOW MANY, but discards WHEN (= which tick = which pixel
position). The tick is the only link between a token value and its spatial location in
the frame. Without it, the token cannot be placed during reconstruction.

The causal window (`learning_window = birth_tick`) amplified this: d5 was born at tick
59,756 and needed 59,756 observations to crystallize. During those observations, ~14.6
frames worth of pixels were absorbed without position tracking.

**Temporal distribution of unplaced pixels:**
```
Frame 0:    29.5% unplaced  ← all entities learning simultaneously
Frame 1:    31.0%
Frame 10:   13.4%           ← root/d1 crystallized, d2-d5 still learning
Frame 50:    6.0%           ← most entities crystallized except d5
Frame 200:   2.5%           ← only d6 still learning
```

Early frames suffered most because all entities start in learning mode at once.
The delta-chain reconstruction then accumulated these errors: each unplaced pixel
creates a constant offset in all subsequent frames at that position.

**What values were lost:** Delta values ±33 to ±44 — medium-to-large pixel changes
at motion boundaries and contrast edges. These are the tokens that fell outside
all crystallized spectra (d0-d4 learned values closer to 128) but were too rare
for d5 to see during its long learning window.

### Fix: Learning Log

Added `learning_log = []` to Entity. During `observe(token, tick)`, the entity now
appends `(tick, token)` to `learning_log` alongside the existing Counter update.
Reconstruction uses both `consumption_log` (post-crystallization) and `learning_log`
(pre-crystallization) to place pixels.

Also modified `Seed` to store `(tick, token)` pairs instead of bare tokens, so
seed-buffered tokens (60 per entity × 6 entities = 360 tokens) transfer their
tick positions to the child entity's `learning_log` upon promotion.

### Second Run: Complete Reconstruction

**PSNR: 26.3 dB (good — from 11.9 dB)**

```
Placed 1,159,168/1,159,168 pixels (100.0%)
  from consumption: 1,076,614 (92.9%)
  from learning:       82,554 ( 7.1%)
  unplaced:                 0 ( 0.0%)

Error at every depth level: 0.00 (all placed pixels are exact)
```

The remaining PSNR gap from infinity comes solely from `uint8` clipping artifacts
in the delta-chain reconstruction (`np.clip(frame + signed_delta, 0, 255)`), not
from any information loss in the trie.

### Storage Analysis

```
Original mp4 (full res, color):       34,545 KB  (34.5 MB)
Raw 64×64 gray (284 frames):           1,136 KB
Diff frames (283 frames):              1,132 KB
First frame (I-frame anchor):              4 KB

Mode A trie (tick+value per pixel):     5,261 KB  (4.6× expansion vs raw diff)
Mode A trie (tick only, spectrum LUT):  4,210 KB  (3.7× expansion)
Mode B trie (spatial tokens):              87 KB  (0.08× — 92:1 compression, but 7.7 dB)
```

The trie EXPANDS Mode A data by 4.6× because each pixel stores its position (tick)
alongside its value. Raw diff bytes encode position implicitly by sequential order
(1 byte/pixel). The trie needs 5 bytes/pixel (4B tick + 1B value).

### Progressive Decoding (Mode A)

The trie's unique advantage over flat storage: stop reading at any depth for
a partial reconstruction.

```
Depth levels read    Pixels recovered     Cumulative %
Root only               255,386               22%
+ depth 1               517,094               45%
+ depth 2               822,121               71%
+ depth 3               978,900               84%
+ depth 4             1,075,296               93%
+ depth 5             1,147,149               99%
+ depth 6             1,159,168              100%
```

This is progressive decoding: same principle as JPEG progressive mode or layered
video coding. Root is the cheapest, broadest layer (static background). Each deeper
level adds finer detail. You cannot do this with raw sequential bytes or H.264 —
they require the complete bitstream.

### Mode B (Spatial Tokens)

PSNR: 7.7 dB (poor). Quantization to 8 delta levels (instead of 256) destroys
too much precision. The 8×8 spatial patches are clearly visible as blocky artifacts.
However, the trie is tiny (87 KB) and tokens are self-locating — no tick needed.
A future version with finer quantization (32-64 delta levels) could improve this.

### Key Findings

1. **The trie IS a functional, reversible memory.** 100% of tokens are recoverable
   from `consumption_log` + `learning_log`. Every placed pixel has zero error.

2. **The causal window creates an information-loss hazard** during learning phases.
   The `Counter` aggregation in `observe()` discards position. Fix: always log
   `(tick, token)` during learning, same as during consumption.

3. **The trie does not compress (for Mode A).** It expands 4.6× because explicit
   position storage replaces implicit sequential ordering. The trie trades
   compactness for hierarchical queryability.

4. **Progressive retrieval is the trie's killer feature.** Reading only root +
   depth 1 recovers 45% of pixels with just 2 spectrum entries. H.264 cannot
   offer this — it needs the complete bitstream.

5. **Quality degrades from delta-chain clipping, not from the trie.** With all
   pixels placed at exact values, the only error source is `uint8` saturation
   in the cumulative delta application. Periodic key frames (I-frames every
   ~30 frames) would fix this, exactly as in real video codecs.

6. **Depth maps to temporal persistence.** Root = static (22%), depth 1-2 = slow
   change (49%), depth 3-4 = motion (21%), depth 5-6 = rare events + noise (8%).
   The mechanism discovered this decomposition without any knowledge of video.

### Comparison to Initial Predictions

| Prediction | Result |
|---|---|
| Mode A PSNR 15-25 dB | **26.3 dB** (after learning_log fix) |
| Mode B PSNR 25-35 dB | **7.7 dB** (quantization too coarse — prediction was wrong) |
| Root carries 50%+ of reconstruction | **22%** (causal window=1 makes root crude) |
| Trie compresses vs raw | **No, 4.6× expansion** (position overhead) |
| Progressive decoding works | **Yes** — 45% recovery from 2 levels |

The quality prediction for Mode A was inverted: bytestream with exact byte values
outperformed spatial tokens, contrary to the description's recommendation of Mode B.
The reason: Mode A preserves exact pixel values (no quantization), while Mode B's
coarse quantization (8 delta levels) destroys too much information. Position
tracking via tick is cheap (4 bytes) and precise, while spatial token position is
coarse (8×8 grid).

---

*Date: March 22, 2026*
*Depends on: v9 (Video Frame Decomposition), v8 (Causal Window)*
*Tests: Trie as reversible memory + storage efficiency*
*Connects to: Model-C v16 store()/retrieve() architecture*
