# sliding_window.py
"""
Simple ring buffer sliding window for snapshots and metadata.
Stores small low-res snapshots for fields and full entity metadata.
"""

from collections import deque
import numpy as np

class SlidingWindow:
    def __init__(self, max_size=16):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)  # each entry: dict with metadata

    def on_tick(self, s_t, entities, core_lowres, residual_lowres):
        """
        Save a snapshot: scale, entity states, low-res copies of fields.
        core_lowres/residual_lowres are small arrays (e.g., 64x64).
        """
        snap = {
            's': float(s_t),
            'entities': [e.copy() for e in entities],  # assume dict-like
            'core_lr': core_lowres.copy(),
            'res_lr': residual_lowres.copy()
        }
        self.buffer.append(snap)

    def get_frame(self, offset=0):
        """
        offset=0 -> most recent (head)
        offset=1 -> one tick back
        """
        if offset >= len(self.buffer):
            return None
        # deque stores oldest->newest; index from end
        return self.buffer[-1 - offset]

    def current_window_size(self):
        return len(self.buffer)
