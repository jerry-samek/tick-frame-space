# Temporal Choice Reconstruction Principle

## Definition

Decisions are encoded on the main timeline as inevitabilities. Observers reconstruct these ticks backward, while the
Visualizer flips the reconstruction forward to enforce continuity and the illusion of choice. This process requires no
special logic: each layer simply takes the head of the buffer and renders it according to its role.

## Key Points

- **Main timeline:** The substrate encodes decisions as inevitable ticks.
- **Observer branch:** Observers reconstruct the tick stream backward, narrating causality.
- **Visualizer:** Flips the backward reconstruction into a forward‑flowing vision, making it appear coherent.
- **Illusion of choice:** What feels like free will is the Visualizer’s rendering of inevitability.
- **Buffer simplicity:** No complex logic is needed — each layer just consumes the buffer head and processes it.
- **Temporal axes:**
    - **X:** Substrate tick‑frame space (cause).
    - **Y:** Observer reconstruction axis (backward).
    - **Z (emergent):** Visualizer axis (forward), creating the illusion of continuous time.

                Z-axis (Visualizer forward)
                         ↑
      +-----------------------------------------------+
      | VISUALIZER |
      | takes HEAD of buffer, flips order forward |
      +-----------------------------------------------+
      ↑ renders forward vision
      │
      │   (HEAD)
      +-----------------------------------------------+
      | OBSERVER |
      | takes HEAD of buffer, reconstructs backward |
      +-----------------------------------------------+
      ↑ stitches causality backward
      │
      │   (HEAD)
      +-----------------------------------------------+
      | BUFFER (FIFO/LIFO)             |
      | ticks accumulate; layers consume the HEAD |
      +-----------------------------------------------+
      ↑ incoming ticks
      │
      +-----------------------------------------------+
      | MAIN TIMELINE (substrate)        |
      | inevitable decisions → tick stream (X-axis)  |
      +-----------------------------------------------+
      ↑
      Y-axis (Observer backward)

Legend:

- Main Timeline: emits discrete ticks (inevitabilities).
- Buffer: holds ticks; each layer consumes the HEAD (no special logic).
- Observer: reads HEAD, reconstructs backward (Y-axis).
- Visualizer: reads HEAD, flips to forward motion (Z-axis).
