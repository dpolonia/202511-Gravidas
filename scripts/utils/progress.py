"""
Progress tracking utilities for pipeline operations.

This module provides real-time progress tracking with:
- Progress bars with ETA
- Rate/throughput calculations
- Time elapsed and remaining
- Percentage completion
- Custom status messages
"""

import time
from typing import Optional, Any
from datetime import datetime, timedelta
import sys


class ProgressTracker:
    """
    Real-time progress tracker with ETA and rate calculations.

    Example:
        >>> tracker = ProgressTracker(total=100, description="Processing items")
        >>> for i in range(100):
        ...     # Do work
        ...     tracker.update(1)
        >>> tracker.finish("✅ Complete!")
    """

    def __init__(self, total: int, description: str = "Progress",
                 unit: str = "items", show_rate: bool = True,
                 show_eta: bool = True, bar_width: int = 40):
        """
        Initialize progress tracker.

        Args:
            total: Total number of items to process
            description: Description of the operation
            unit: Unit name for items (e.g., 'items', 'files', 'interviews')
            show_rate: Whether to show processing rate
            show_eta: Whether to show estimated time remaining
            bar_width: Width of progress bar in characters
        """
        self.total = total
        self.description = description
        self.unit = unit
        self.show_rate = show_rate
        self.show_eta = show_eta
        self.bar_width = bar_width

        self.current = 0
        self.start_time = time.time()
        self.last_update_time = self.start_time

        # For rate calculation
        self.update_times = []
        self.update_counts = []

        self._finished = False

    def update(self, increment: int = 1, status: Optional[str] = None):
        """
        Update progress by increment.

        Args:
            increment: Number of items completed
            status: Optional status message to display
        """
        if self._finished:
            return

        self.current += increment
        current_time = time.time()

        # Track for rate calculation
        self.update_times.append(current_time)
        self.update_counts.append(self.current)

        # Keep only recent history (last 10 updates)
        if len(self.update_times) > 10:
            self.update_times.pop(0)
            self.update_counts.pop(0)

        self.last_update_time = current_time

        # Display progress
        self._display(status)

    def _calculate_rate(self) -> float:
        """Calculate current processing rate (items per second)."""
        if len(self.update_times) < 2:
            return 0.0

        time_diff = self.update_times[-1] - self.update_times[0]
        count_diff = self.update_counts[-1] - self.update_counts[0]

        if time_diff == 0:
            return 0.0

        return count_diff / time_diff

    def _calculate_eta(self) -> Optional[float]:
        """Calculate estimated time remaining in seconds."""
        if self.current == 0:
            return None

        elapsed = time.time() - self.start_time
        rate = self.current / elapsed

        if rate == 0:
            return None

        remaining = self.total - self.current
        return remaining / rate

    def _format_time(self, seconds: float) -> str:
        """Format time duration in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"

        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)

        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        return f"{hours}h {remaining_minutes}m"

    def _display(self, status: Optional[str] = None):
        """Display current progress."""
        if not sys.stdout.isatty():
            # Not a terminal, don't show progress bar
            return

        # Calculate percentage
        percentage = (self.current / self.total * 100) if self.total > 0 else 0

        # Create progress bar
        filled = int((self.current / self.total) * self.bar_width) if self.total > 0 else 0
        bar = '█' * filled + '░' * (self.bar_width - filled)

        # Build status line
        parts = [
            f"\r{self.description}",
            f"[{bar}]",
            f"{self.current}/{self.total}",
            f"({percentage:.1f}%)"
        ]

        # Add rate if requested
        if self.show_rate:
            rate = self._calculate_rate()
            if rate > 0:
                parts.append(f"{rate:.1f} {self.unit}/s")

        # Add ETA if requested
        if self.show_eta:
            eta_seconds = self._calculate_eta()
            if eta_seconds is not None and eta_seconds > 0:
                eta_str = self._format_time(eta_seconds)
                parts.append(f"ETA: {eta_str}")

        # Add custom status if provided
        if status:
            parts.append(f"| {status}")

        # Print progress line
        line = ' '.join(parts)
        sys.stdout.write(line + ' ' * 10)  # Extra spaces to clear previous longer lines
        sys.stdout.flush()

    def finish(self, message: Optional[str] = None):
        """
        Mark progress as complete and show final message.

        Args:
            message: Final message to display (default: "✅ Complete")
        """
        if self._finished:
            return

        self._finished = True
        self.current = self.total

        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)

        if message is None:
            message = "✅ Complete"

        # Clear line and show final message
        if sys.stdout.isatty():
            sys.stdout.write('\r' + ' ' * 100 + '\r')
            final_line = f"{message} | {self.total} {self.unit} in {elapsed_str}"

            # Add average rate
            if self.total > 0 and elapsed > 0:
                avg_rate = self.total / elapsed
                final_line += f" ({avg_rate:.2f} {self.unit}/s)"

            print(final_line)
        else:
            print(f"{message} | {self.total} {self.unit} in {elapsed_str}")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if not self._finished:
            if exc_type is None:
                self.finish()
            else:
                self.finish("❌ Failed")


class SimpleProgress:
    """
    Simple progress indicator without a progress bar.

    Useful for operations where total count is unknown.

    Example:
        >>> progress = SimpleProgress("Loading files")
        >>> progress.update("Found config.yaml")
        >>> progress.update("Found data.json")
        >>> progress.finish("✅ Loaded 2 files")
    """

    def __init__(self, description: str = "Processing"):
        """
        Initialize simple progress indicator.

        Args:
            description: Operation description
        """
        self.description = description
        self.start_time = time.time()
        self.count = 0
        self._finished = False

    def update(self, message: Optional[str] = None):
        """
        Update progress with optional message.

        Args:
            message: Status message to display
        """
        if self._finished:
            return

        self.count += 1

        if sys.stdout.isatty():
            elapsed = time.time() - self.start_time
            elapsed_str = self._format_time(elapsed)

            if message:
                line = f"\r⏳ {self.description}: {message} (elapsed: {elapsed_str})"
            else:
                line = f"\r⏳ {self.description}... ({self.count} processed, {elapsed_str})"

            sys.stdout.write(line + ' ' * 20)
            sys.stdout.flush()

    def _format_time(self, seconds: float) -> str:
        """Format time duration."""
        if seconds < 60:
            return f"{int(seconds)}s"
        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)
        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"
        hours = minutes // 60
        remaining_minutes = minutes % 60
        return f"{hours}h {remaining_minutes}m"

    def finish(self, message: str = "✅ Complete"):
        """
        Mark progress as complete.

        Args:
            message: Final message
        """
        if self._finished:
            return

        self._finished = True
        elapsed = time.time() - self.start_time
        elapsed_str = self._format_time(elapsed)

        if sys.stdout.isatty():
            sys.stdout.write('\r' + ' ' * 100 + '\r')

        print(f"{message} ({elapsed_str})")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        if not self._finished:
            if exc_type is None:
                self.finish()
            else:
                self.finish("❌ Failed")


# Export public API
__all__ = ['ProgressTracker', 'SimpleProgress']
