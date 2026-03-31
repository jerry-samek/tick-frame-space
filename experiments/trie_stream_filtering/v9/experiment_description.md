# Experiment 118 v9: Temporal Stream — Video Frame Decomposition

## Purpose

v7 and v8 tested the consumption-transformation mechanism on static data streams
(text, DNA, random bytes). These streams have sequential structure but no inherent
temporal dimension — the order matters but there's no "frame rate."

**v9 tests the mechanism on a genuinely temporal stream: video frames.**

A video is a discrete sampling of continuous reality at a fixed frame rate. Each
frame is one snapshot. The consumption-transformation mechanism, operating on
sequential frames, should naturally decompose the video into layers of temporal
persistence — without being told what "background," "object," or "motion" are.

This directly tests the "continuous sampling" question from RAW 123 §4: if the
universe's stream is a discrete sampling of something continuous, does the
consumption-transformation mechanism discover the temporal structure of the
source? Video is the perfect test case because we KNOW the continuous source
(physical reality) and the sampling rate (frame rate).

**Prediction:** The mechanism should produce a hierarchy where:
- Depth 0 (root): static background — the most persistent pattern across frames
- Depth 1-2: slowly moving or stable objects
- Depth 3+: rapid motion, lighting changes, fine detail
- Deepest: noise, compression artifacts — consumed depth 0 (no structure)

This is equivalent to what video codecs do (I-frames, P-frames, B-frames) — but
discovered by the mechanism, not programmed.

---

## Design

### Input: Video as Byte Stream

A video clip is converted to a sequence of frames. Each frame is a 2D pixel array.
The mechanism receives frames sequentially, one per tick.

**Two modes of feeding:**

**Mode A — Raw frames:**
Each tick, the mechanism receives one complete frame as a flattened byte array
(or downsampled patch). The token at each tick is the entire frame. Entities
learn to recognize recurring frame patterns.

Problem: frames are large (even 64×64 = 4096 bytes). At N=1 (single pixels),
this is just pixel frequency sorting. At N=frame_size, each frame is unique
(no two frames are identical). Neither extreme is useful.

**Mode B — Frame differences (RECOMMENDED):**
Each tick, the mechanism receives the DIFFERENCE between consecutive frames:
`delta[t] = frame[t] - frame[t-1]`. The token is what CHANGED, not what IS.

This is much more informative:
- Static background → delta ≈ 0 everywhere → root consumes "no change"
- Moving object → delta has non-zero region at object boundary → rejected
- Scene cut → delta is large everywhere → massive rejection event

The root entity naturally learns "no change" as its spectrum (the most common
pattern in most videos is "nothing happened at this pixel"). Everything that
DID change is rejected and routed to children.

**Mode C — Patch-based (MOST SCALABLE):**
Divide each frame into small patches (e.g., 8×8 pixels). Each patch is one token.
Feed patches left-to-right, top-to-bottom, frame by frame. The mechanism sees a
stream of patches, some recurring (background regions) and some varying (motion
regions).

This is closest to how real video codecs work (macroblocks in H.264).

### Recommended: Start with Mode B (frame differences)

Frame differences are the simplest input with the richest temporal structure.
The mechanism operates on delta frames:

```python
def frame_difference_stream(video_path, resize=(64, 64)):
    """Yield frame differences as flattened byte arrays."""
    cap = cv2.VideoCapture(video_path)
    prev_frame = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        # Convert to grayscale, resize for manageability
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, resize)
        
        if prev_frame is not None:
            # Signed difference, shifted to 0-255 range
            diff = gray.astype(int) - prev_frame.astype(int)
            diff = np.clip(diff + 128, 0, 255).astype(np.uint8)
            yield diff.flatten()
        
        prev_frame = gray
    
    cap.release()
```

### Token Extraction from Delta Frames

Each delta frame is 64×64 = 4096 pixels. Too large for a single token.
Tokenize by extracting features:

**Option 1: Patch tokens**
Divide the delta frame into 8×8 patches (64 patches per frame). Each patch
is a 64-byte token. Feed 64 tokens per tick (one per patch position).

**Option 2: Histogram tokens**
Compute a histogram of the delta frame (how many pixels changed by how much).
The histogram is a compact summary of "how much changed." Feed one histogram
token per tick.

**Option 3: Spatial position tokens (RECOMMENDED for first test)**
For each delta frame, extract the N pixels with the largest absolute change.
Each token is (x, y, delta_value) — where something changed and by how much.
The root learns "small changes" (most common). Large changes are rejected
outward. Motion boundaries become the reject stream.

```python
def extract_motion_tokens(delta_frame, top_n=100, quantize=8):
    """Extract top-N changed pixels as tokens."""
    flat = delta_frame.flatten()
    # Quantize to reduce token space
    quantized = (flat // quantize) * quantize
    
    # Find top N pixels by absolute change from 128 (no-change value)
    deviations = np.abs(quantized.astype(int) - 128)
    top_indices = np.argsort(deviations)[-top_n:]
    
    tokens = []
    for idx in top_indices:
        y, x = divmod(idx, delta_frame.shape[1])
        val = quantized[idx]
        # Token = (spatial_position_quantized, change_value)
        token = (x // 8, y // 8, val)
        tokens.append(token)
    
    return tokens
```

### Video Source

Use a SHORT video clip with clear temporal structure:

**Option A: Synthetic test video (controlled)**
- 10 seconds, 24 fps = 240 frames
- Static background (solid color or simple pattern)
- One object moving left to right at constant speed
- One object stationary
- One scene cut (background change) at frame 120

This provides known ground truth: the mechanism should separate background,
moving object, stationary object, and scene cut into different trie levels.

**Option B: Real video clip**
- Any short clip from a creative commons source
- 5-15 seconds, downsampled to 64×64 grayscale
- More complex, harder to validate, but more convincing if it works

**Recommendation: Start with Option A (synthetic), then test Option B.**

---

## The Causal Window Applied to Video

v8's key insight: `learning_window = max(1, birth_tick)`. Entities born later
have longer learning windows and develop better spectra.

For video, this means:
- Root (tick 0): sees 1 frame difference. Learns "the most common change pattern
  in the first frame." Crude filter.
- Depth 1 entities (tick ~50): have seen ~50 frames. Know what changes regularly.
  Can filter periodic motion from noise.
- Depth 2+ entities (tick ~200+): have seen most of the clip. Deeply tuned to
  specific motion patterns or spatial regions.

The deeper entities are the best "scene understanding" — they've watched the
most video before crystallizing their spectra.

---

## Parameters

```python
# Video
VIDEO_SOURCE = "synthetic"  # or path to a real video file
FRAME_SIZE = (64, 64)       # downsampled resolution
FPS = 24                    # frame rate (for synthetic video)
DURATION = 10               # seconds (for synthetic video)

# Tokenization
TOKEN_MODE = "spatial"      # "patch", "histogram", or "spatial"
TOKENS_PER_FRAME = 100      # number of tokens extracted per frame
QUANTIZE_STEP = 8           # pixel value quantization (reduces token space)

# Graph
N_NODES = 10000
SPHERE_R = 20.0
TARGET_K = 24

# Learning (causal window from v8)
COVERAGE = 0.5

# Formation
GROWTH_COST = 5             # lower than v7/v8 — frames are fewer than text bytes
PLANET_THRESHOLD = 30       # lower threshold — fewer total events
REJECTION_HOPS = 5
EXTEND_RATE = 0.01

# Runtime
TICKS = DURATION * FPS      # one tick per frame (240 for 10s at 24fps)
# Note: if TOKENS_PER_FRAME > 1, total events = TICKS * TOKENS_PER_FRAME
LOG_EVERY = 24              # every second of video
MEASURE_EVERY = 12          # every half-second
```

---

## Synthetic Video Specification

```python
def generate_synthetic_video(n_frames=240, size=(64, 64)):
    """Generate test video with known temporal structure.
    
    Content:
    - Background: horizontal gradient (light left, dark right)
    - Object A: white 8x8 square moving left to right at 1 px/frame
    - Object B: gray 8x8 square stationary at (16, 48)
    - Scene cut at frame 120: background inverts
    - Noise: Gaussian noise with std=5 added to every frame
    """
    frames = []
    for t in range(n_frames):
        # Background
        if t < 120:
            bg = np.tile(np.linspace(40, 80, size[1]), (size[0], 1)).astype(np.uint8)
        else:
            bg = np.tile(np.linspace(80, 40, size[1]), (size[0], 1)).astype(np.uint8)
        
        frame = bg.copy()
        
        # Object A: moving square
        ax = int(t * (size[1] - 8) / n_frames)  # x moves left to right
        ay = 24
        frame[ay:ay+8, ax:ax+8] = 220
        
        # Object B: stationary square
        frame[48:56, 16:24] = 128
        
        # Noise
        noise = np.random.normal(0, 5, size).astype(np.int16)
        frame = np.clip(frame.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        
        frames.append(frame)
    
    return frames
```

---

## Measurements

### Per-frame diagnostics:
- Number of tokens consumed vs rejected at each trie level
- Which entities were active (received events)
- Total connector extension this tick

### Per-entity tracking:
- Birth tick (= which frame triggered formation)
- Spectrum (what motion patterns does it recognize?)
- Mass over time (node growth curve)
- Spatial correspondence (which pixel regions does it respond to?)

### Temporal analysis:
- **Static background detection:** Does the root entity's spectrum correspond
  to "no change" or "small change"? Does it consume most of the stream?
- **Motion separation:** Do moving objects form distinct entities at depth 1-2?
  Can we reconstruct Object A's trajectory from the trie structure?
- **Scene cut detection:** Does the background inversion at frame 120 produce
  a massive rejection event? Does it form new entities or restructure existing ones?
- **Noise vs signal:** Does noise (random pixel variation) produce consumed depth 0?
  Does signal (coherent motion) produce consumed depth > 0?

### The key test:
- **Feed the synthetic video.** Does the mechanism separate background, moving
  object, stationary object, and noise into different trie levels WITHOUT being
  told what any of these are?
- **Feed a real video.** Does the hierarchy look like reasonable scene decomposition?

---

## Predictions

### For synthetic video:

| Component | Expected trie level | Reasoning |
|---|---|---|
| Static background | Depth 0 (root) | Most persistent pattern, most common delta ≈ 0 |
| Stationary object | Depth 0-1 (root or near-root) | Doesn't generate deltas, absorbed by background filter |
| Moving object edge (leading) | Depth 1-2 | Consistent delta pattern, periodic at object speed |
| Moving object edge (trailing) | Depth 1-2 | Same but opposite sign delta |
| Scene cut | Triggers mass rejection event | Background inversion = every pixel changes simultaneously |
| Noise | Deepest / unconsumed | Random per-pixel variation, no repeating pattern |

### For real video:

| Component | Expected behavior |
|---|---|
| Sky, walls, floor | Root consumes — low delta, high persistence |
| Walking person | Depth 1-2 — consistent motion pattern |
| Facial expression | Depth 3+ — fine detail on top of coarse motion |
| Camera shake | Depth 1 — global delta pattern affecting all pixels |
| Compression artifacts | Unconsumed — no temporal structure |

---

## Connection to RAW 123

### Continuous Sampling

Video IS discrete sampling of continuous reality. The frame rate determines
what temporal structure is visible to the mechanism:

- Motion slower than 1 pixel/frame → visible as smooth trajectory
- Motion faster than frame_size/2 per frame → aliased or invisible
- This is the Nyquist theorem applied to the consumption-transformation mechanism

RAW 123 §8.7 asks about a "cosmic Nyquist frequency." Video provides a concrete
testbed: the frame rate IS the Nyquist frequency, and the mechanism's ability
to discover structure is bounded by it.

### The First Token

In v8, the root at tick 0 sees one event and crystallizes on it. In v9, the
root at tick 0 sees one frame difference (frame 1 minus frame 0). That first
delta is the root's entire knowledge. It's the video equivalent of the Big Bang —
one snapshot of change, from which the entire hierarchy of motion understanding
must be built.

### Structure Discovery

v7/v8 showed that the mechanism discovers sequential structure in text (bigrams,
motifs) and correctly reports absence of structure in random data. v9 tests
whether it discovers TEMPORAL structure — patterns that persist or repeat across
frames. This is a stronger test because temporal structure is 2D (spatial × time)
rather than 1D (sequential bytes).

---

## Implementation Notes

### Dependencies

```python
# Standard
import numpy as np
from collections import defaultdict, Counter
import csv, os, time

# Video handling
import cv2  # pip install opencv-python

# Plotting
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
```

### Performance

At 64×64 resolution with 100 tokens per frame and 240 frames:
- Total events: 24,000
- This is smaller than v7/v8 (500K bytes). Processing should be fast.
- If results are promising, scale up to 128×128 and longer clips.

### Output

Standard v8 output plus:
- **Frame-by-frame consumption heatmap:** For each frame, show which pixel
  regions were consumed (by root vs children) and which were rejected.
  This visualizes the trie's "understanding" of each frame.
- **Entity activation timeline:** Which entities were active at each frame.
  This shows how the trie's filtering evolves over time.
- **Motion trajectory from trie:** Reconstruct Object A's position from the
  depth-1 entity's activation pattern. If the trie correctly separated the
  moving object, its trajectory should be recoverable.

Save frame-level diagnostics as CSV:
```
frame, n_consumed_root, n_consumed_d1, n_consumed_d2, n_rejected, n_entities, max_depth
```

---

## Success Criteria

### Minimum (v9 passes):
- Root entity learns "no change" as dominant pattern (delta ≈ 0)
- Moving object forms a distinct entity separate from background
- Scene cut at frame 120 produces a visible disruption in the trie

### Strong:
- Moving object's trajectory is recoverable from entity activation pattern
- Noise is correctly separated from signal (noise = deep/unconsumed, signal = shallow/consumed)
- Real video produces interpretable scene decomposition

### Maximum (breakthrough):
- The mechanism rediscovers video compression principles (I-frame/P-frame/B-frame separation)
  without any knowledge of video coding
- Temporal hierarchy depth correlates with motion complexity
- The "cosmic Nyquist" prediction is validated: structure faster than frame rate is invisible

---

## What This Tests

v7 tested: does the mechanism discover sequential structure in static data?
v8 tested: does causal learning window produce physically correct hierarchy?
**v9 tests: does the mechanism discover temporal structure in continuous-sampled data?**

If it works: the mechanism operates on temporal streams the same way it operates
on text and DNA — it finds structure where structure exists and reports absence
where it doesn't. Video is the closest analogue to the universe's actual data
stream (continuous reality sampled at a discrete rate).

If it fails: the mechanism may be limited to 1D sequential structure and unable
to decompose 2D spatio-temporal data. This would constrain the cosmic
interpretation (the universe's stream may need to be 1D, not multi-dimensional).

---

*Date: March 22, 2026*
*Depends on: v8 (Causal Window), RAW 123 (The Stream and the Trie)*
*Tests: Temporal structure discovery from continuous-sampled video stream*
