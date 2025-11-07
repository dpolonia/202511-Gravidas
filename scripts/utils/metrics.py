"""
Metrics collection and reporting for pipeline operations.

This module tracks and reports:
- Processing statistics (success/failure rates)
- Cost tracking (real-time and cumulative)
- Performance metrics (throughput, duration)
- Resource usage
- Summary reports
"""

import time
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PipelineMetrics:
    """
    Collect and report pipeline execution metrics.

    Example:
        >>> metrics = PipelineMetrics("Interview Pipeline")
        >>> metrics.start()
        >>> metrics.increment('interviews_completed')
        >>> metrics.add_cost(0.05)
        >>> metrics.stop()
        >>> print(metrics.summary())
    """

    def __init__(self, pipeline_name: str, log_dir: Optional[str] = None):
        """
        Initialize metrics collector.

        Args:
            pipeline_name: Name of the pipeline
            log_dir: Directory to save metrics logs (optional)
        """
        self.pipeline_name = pipeline_name
        self.log_dir = Path(log_dir) if log_dir else None

        # Timing
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # Counters
        self.counters: Dict[str, int] = {}

        # Cost tracking
        self.total_cost: float = 0.0
        self.cost_by_model: Dict[str, float] = {}

        # Performance
        self.operation_times: Dict[str, List[float]] = {}

        # Errors
        self.errors: List[Dict[str, Any]] = []

    def start(self):
        """Start timing the pipeline."""
        self.start_time = time.time()
        logger.info(f"Started metrics collection for {self.pipeline_name}")

    def stop(self):
        """Stop timing the pipeline."""
        self.end_time = time.time()
        logger.info(f"Stopped metrics collection for {self.pipeline_name}")

    def increment(self, counter_name: str, amount: int = 1):
        """
        Increment a counter.

        Args:
            counter_name: Name of the counter
            amount: Amount to increment (default: 1)
        """
        self.counters[counter_name] = self.counters.get(counter_name, 0) + amount

    def add_cost(self, cost: float, model: Optional[str] = None):
        """
        Add to cost tracking.

        Args:
            cost: Cost amount in dollars
            model: Optional model name for per-model tracking
        """
        self.total_cost += cost

        if model:
            self.cost_by_model[model] = self.cost_by_model.get(model, 0.0) + cost

    def record_operation_time(self, operation: str, duration: float):
        """
        Record time taken for an operation.

        Args:
            operation: Operation name
            duration: Duration in seconds
        """
        if operation not in self.operation_times:
            self.operation_times[operation] = []

        self.operation_times[operation].append(duration)

    def record_error(self, error_type: str, message: str, context: Optional[Dict[str, Any]] = None):
        """
        Record an error.

        Args:
            error_type: Type of error
            message: Error message
            context: Optional context information
        """
        error_record = {
            'timestamp': datetime.now().isoformat(),
            'type': error_type,
            'message': message,
            'context': context or {}
        }
        self.errors.append(error_record)
        logger.warning(f"Recorded error: {error_type} - {message}")

    def get_duration(self) -> Optional[float]:
        """Get total duration in seconds."""
        if self.start_time is None:
            return None

        end = self.end_time if self.end_time else time.time()
        return end - self.start_time

    def get_throughput(self, counter_name: str) -> Optional[float]:
        """
        Calculate throughput (items per second).

        Args:
            counter_name: Name of the counter to calculate throughput for

        Returns:
            Throughput in items/second, or None if not available
        """
        duration = self.get_duration()
        if duration is None or duration == 0:
            return None

        count = self.counters.get(counter_name, 0)
        return count / duration

    def get_success_rate(self, success_counter: str, total_counter: str) -> Optional[float]:
        """
        Calculate success rate as percentage.

        Args:
            success_counter: Name of success counter
            total_counter: Name of total counter

        Returns:
            Success rate as percentage (0-100), or None if not available
        """
        total = self.counters.get(total_counter, 0)
        if total == 0:
            return None

        success = self.counters.get(success_counter, 0)
        return (success / total) * 100

    def get_average_operation_time(self, operation: str) -> Optional[float]:
        """
        Get average time for an operation.

        Args:
            operation: Operation name

        Returns:
            Average duration in seconds, or None if not available
        """
        times = self.operation_times.get(operation, [])
        if not times:
            return None

        return sum(times) / len(times)

    def summary(self) -> Dict[str, Any]:
        """
        Generate summary dictionary of all metrics.

        Returns:
            Dictionary containing all metrics
        """
        duration = self.get_duration()

        summary = {
            'pipeline_name': self.pipeline_name,
            'start_time': datetime.fromtimestamp(self.start_time).isoformat() if self.start_time else None,
            'end_time': datetime.fromtimestamp(self.end_time).isoformat() if self.end_time else None,
            'duration_seconds': duration,
            'duration_formatted': self._format_duration(duration) if duration else None,
            'counters': self.counters,
            'total_cost': round(self.total_cost, 4),
            'cost_by_model': {k: round(v, 4) for k, v in self.cost_by_model.items()},
            'operation_times': {
                op: {
                    'count': len(times),
                    'total': round(sum(times), 2),
                    'average': round(sum(times) / len(times), 2),
                    'min': round(min(times), 2),
                    'max': round(max(times), 2)
                }
                for op, times in self.operation_times.items()
            },
            'errors': {
                'count': len(self.errors),
                'details': self.errors[-10:]  # Last 10 errors
            }
        }

        return summary

    def format_summary(self) -> str:
        """
        Format summary as human-readable text.

        Returns:
            Formatted summary string
        """
        summary = self.summary()
        lines = []

        # Header
        lines.append("=" * 80)
        lines.append(f"  {self.pipeline_name} - Metrics Summary")
        lines.append("=" * 80)
        lines.append("")

        # Duration
        if summary['duration_formatted']:
            lines.append(f"Duration: {summary['duration_formatted']}")
            lines.append("")

        # Counters
        if summary['counters']:
            lines.append("Counters:")
            for name, value in sorted(summary['counters'].items()):
                lines.append(f"  • {name}: {value:,}")
            lines.append("")

        # Cost
        if summary['total_cost'] > 0:
            lines.append(f"Total Cost: ${summary['total_cost']:.4f}")
            if summary['cost_by_model']:
                lines.append("  By Model:")
                for model, cost in sorted(summary['cost_by_model'].items(), key=lambda x: -x[1]):
                    lines.append(f"    • {model}: ${cost:.4f}")
            lines.append("")

        # Operation times
        if summary['operation_times']:
            lines.append("Operation Times:")
            for op, stats in sorted(summary['operation_times'].items()):
                lines.append(f"  • {op}:")
                lines.append(f"      Count: {stats['count']}")
                lines.append(f"      Average: {stats['average']:.2f}s")
                lines.append(f"      Range: {stats['min']:.2f}s - {stats['max']:.2f}s")
            lines.append("")

        # Errors
        if summary['errors']['count'] > 0:
            lines.append(f"Errors: {summary['errors']['count']}")
            if summary['errors']['details']:
                lines.append("  Recent errors:")
                for error in summary['errors']['details'][-5:]:
                    lines.append(f"    • [{error['type']}] {error['message']}")
            lines.append("")

        lines.append("=" * 80)

        return '\n'.join(lines)

    def _format_duration(self, seconds: float) -> str:
        """Format duration in human-readable form."""
        if seconds < 60:
            return f"{int(seconds)}s"

        minutes = int(seconds // 60)
        remaining_seconds = int(seconds % 60)

        if minutes < 60:
            return f"{minutes}m {remaining_seconds}s"

        hours = minutes // 60
        remaining_minutes = minutes % 60

        return f"{hours}h {remaining_minutes}m {remaining_seconds}s"

    def save_to_file(self, filename: Optional[str] = None):
        """
        Save metrics to JSON file.

        Args:
            filename: Output filename (auto-generated if None)
        """
        if self.log_dir:
            self.log_dir.mkdir(parents=True, exist_ok=True)

            if filename is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                filename = f"{self.pipeline_name.replace(' ', '_')}_{timestamp}.json"

            filepath = self.log_dir / filename

            with open(filepath, 'w') as f:
                json.dump(self.summary(), f, indent=2)

            logger.info(f"Saved metrics to {filepath}")
            return filepath
        else:
            logger.warning("No log directory configured, cannot save metrics")
            return None

    def __enter__(self):
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.stop()

        # Log summary
        print()
        print(self.format_summary())

        # Save to file if configured
        if self.log_dir:
            self.save_to_file()


class OperationTimer:
    """
    Context manager for timing individual operations.

    Example:
        >>> metrics = PipelineMetrics("My Pipeline")
        >>> with OperationTimer(metrics, "data_loading"):
        ...     load_data()  # This operation will be timed
    """

    def __init__(self, metrics: PipelineMetrics, operation_name: str):
        """
        Initialize operation timer.

        Args:
            metrics: PipelineMetrics instance to record to
            operation_name: Name of the operation being timed
        """
        self.metrics = metrics
        self.operation_name = operation_name
        self.start_time: Optional[float] = None

    def __enter__(self):
        """Start timing."""
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Stop timing and record."""
        if self.start_time:
            duration = time.time() - self.start_time
            self.metrics.record_operation_time(self.operation_name, duration)


# Export public API
__all__ = ['PipelineMetrics', 'OperationTimer']
