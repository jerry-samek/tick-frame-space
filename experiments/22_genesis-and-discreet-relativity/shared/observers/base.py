"""
Observer Base Class
===================

Abstract base class for tick-frame observers and logging utilities.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pathlib import Path
import csv
import json


class Observer(ABC):
    """
    Abstract base class for substrate observers.

    Observers:
    - Never modify the substrate
    - May keep internal memory
    - May log or compute metrics
    - Receive notifications before and after each tick
    """

    def __init__(self, name: str, log_interval: int = 1, output_dir: Optional[str] = None):
        """
        Initialize the observer.

        Args:
            name: Observer name (used for logging)
            log_interval: How often to log (every N ticks)
            output_dir: Directory for output files (None = no file logging)
        """
        self.name = name
        self.log_interval = log_interval
        self.output_dir = Path(output_dir) if output_dir else None
        self.memory: Dict[str, Any] = {}  # Internal state storage

        # Create output directory if specified
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)

    def on_pre_tick(self, state: 'SubstrateState') -> None:
        """
        Called before the update rule is applied.

        Args:
            state: Current substrate state (before update)
        """
        pass  # Default: do nothing

    @abstractmethod
    def on_post_tick(self, state: 'SubstrateState') -> None:
        """
        Called after the update rule is applied.

        This is the main hook for observers to compute metrics.

        Args:
            state: Current substrate state (after update)
        """
        pass

    def should_log(self, tick: int) -> bool:
        """
        Determine if this tick should be logged.

        Args:
            tick: Current tick number

        Returns:
            True if this tick should be logged
        """
        return tick % self.log_interval == 0

    def log_csv(self, filename: str, data: Dict[str, Any], headers: Optional[List[str]] = None) -> None:
        """
        Append data to a CSV file.

        Args:
            filename: CSV filename (will be created in output_dir)
            data: Dictionary of column_name -> value
            headers: Optional list of column names (auto-detected if None)
        """
        if not self.output_dir:
            return

        filepath = self.output_dir / filename
        file_exists = filepath.exists()

        # Use provided headers or infer from data
        fieldnames = headers or list(data.keys())

        with open(filepath, 'a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)

            # Write header if file is new
            if not file_exists:
                writer.writeheader()

            writer.writerow(data)

    def log_json(self, filename: str, data: Any, mode: str = 'append') -> None:
        """
        Write data to a JSON file.

        Args:
            filename: JSON filename (will be created in output_dir)
            data: Data to write (must be JSON-serializable)
            mode: 'append' (list) or 'overwrite' (single object)
        """
        if not self.output_dir:
            return

        filepath = self.output_dir / filename

        if mode == 'append':
            # Append to a JSON array
            if filepath.exists():
                with open(filepath, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            else:
                existing = []

            existing.append(data)

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(existing, f, indent=2)

        elif mode == 'overwrite':
            # Overwrite with new data
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)

    def log_text(self, filename: str, text: str, mode: str = 'a') -> None:
        """
        Write text to a file.

        Args:
            filename: Text filename (will be created in output_dir)
            text: Text to write
            mode: File open mode ('a' = append, 'w' = overwrite)
        """
        if not self.output_dir:
            return

        filepath = self.output_dir / filename

        with open(filepath, mode, encoding='utf-8') as f:
            f.write(text)


# Import guard to prevent circular imports
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from substrate import SubstrateState
