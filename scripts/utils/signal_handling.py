"""
Signal handling for graceful shutdown and cancellation.

This module provides:
- CTRL-C (SIGINT) handling
- Graceful shutdown with cleanup
- Save progress before exit
- User prompts for confirmation
"""

import signal
import sys
from typing import Optional, Callable
import logging

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Handle graceful shutdown on SIGINT/SIGTERM.

    Example:
        >>> shutdown = GracefulShutdown()
        >>> shutdown.register_cleanup(save_progress)
        >>> shutdown.enable()
        >>>
        >>> # User presses CTRL-C
        >>> # cleanup functions are called automatically
    """

    def __init__(self):
        """Initialize graceful shutdown handler."""
        self.shutdown_requested = False
        self.cleanup_functions = []
        self.original_sigint = None
        self.original_sigterm = None

    def register_cleanup(self, func: Callable, *args, **kwargs):
        """
        Register a cleanup function to call on shutdown.

        Args:
            func: Cleanup function to call
            *args: Arguments to pass to function
            **kwargs: Keyword arguments to pass to function

        Example:
            >>> shutdown.register_cleanup(save_results, results)
            >>> shutdown.register_cleanup(close_connections)
        """
        self.cleanup_functions.append((func, args, kwargs))
        logger.debug(f"Registered cleanup function: {func.__name__}")

    def _signal_handler(self, signum, frame):
        """Handle signal."""
        if self.shutdown_requested:
            # Second CTRL-C, force exit
            print("\n\n⚠️  Force exit requested. Exiting immediately...")
            sys.exit(1)

        self.shutdown_requested = True
        print("\n\n⚠️  Shutdown requested (CTRL-C detected)")

        # Ask user if they want to save progress
        try:
            response = input("Save progress before exit? (Y/n): ").strip().lower()
            save_progress = response != 'n'
        except (EOFError, KeyboardInterrupt):
            save_progress = True
            print()

        if save_progress:
            print("Saving progress and cleaning up...")
            self._run_cleanup()
            print("✅ Progress saved successfully")
        else:
            print("⚠️  Exiting without saving progress")

        sys.exit(0)

    def _run_cleanup(self):
        """Run all registered cleanup functions."""
        for func, args, kwargs in self.cleanup_functions:
            try:
                logger.debug(f"Running cleanup: {func.__name__}")
                func(*args, **kwargs)
            except Exception as e:
                logger.error(f"Cleanup function {func.__name__} failed: {e}")
                print(f"⚠️  Warning: Cleanup failed for {func.__name__}: {e}")

    def enable(self):
        """Enable signal handlers."""
        self.original_sigint = signal.signal(signal.SIGINT, self._signal_handler)
        try:
            self.original_sigterm = signal.signal(signal.SIGTERM, self._signal_handler)
        except (AttributeError, ValueError):
            # SIGTERM not available on all platforms
            pass
        logger.debug("Signal handlers enabled")

    def disable(self):
        """Disable signal handlers (restore original)."""
        if self.original_sigint:
            signal.signal(signal.SIGINT, self.original_sigint)
        if self.original_sigterm:
            try:
                signal.signal(signal.SIGTERM, self.original_sigterm)
            except (AttributeError, ValueError):
                pass
        logger.debug("Signal handlers disabled")

    def __enter__(self):
        """Context manager entry."""
        self.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disable()


class OperationCanceller:
    """
    Context manager for cancellable long-running operations.

    Example:
        >>> with OperationCanceller("Processing interviews") as canceller:
        ...     for i in range(1000):
        ...         if canceller.is_cancelled():
        ...             print("Operation cancelled by user")
        ...             break
        ...         process_item(i)
    """

    def __init__(self, operation_name: str,
                 save_on_cancel: Optional[Callable] = None):
        """
        Initialize operation canceller.

        Args:
            operation_name: Name of the operation
            save_on_cancel: Optional function to call on cancellation
        """
        self.operation_name = operation_name
        self.save_on_cancel = save_on_cancel
        self.cancelled = False
        self.shutdown = GracefulShutdown()

        # Register cleanup if provided
        if save_on_cancel:
            self.shutdown.register_cleanup(save_on_cancel)

    def is_cancelled(self) -> bool:
        """Check if operation was cancelled."""
        return self.shutdown.shutdown_requested

    def __enter__(self):
        """Context manager entry."""
        self.shutdown.enable()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.shutdown.disable()


def setup_signal_handlers(cleanup_func: Optional[Callable] = None,
                         message: Optional[str] = None):
    """
    Setup simple signal handlers for graceful shutdown.

    Args:
        cleanup_func: Optional cleanup function to call
        message: Optional custom message to show

    Example:
        >>> def save_results():
        ...     print("Saving results...")
        ...     # Save code here
        >>>
        >>> setup_signal_handlers(save_results, "Saving partial results...")
    """
    def signal_handler(signum, frame):
        print("\n\n⚠️  Operation cancelled (CTRL-C)")

        if message:
            print(message)

        if cleanup_func:
            try:
                cleanup_func()
                print("✅ Cleanup completed")
            except Exception as e:
                print(f"⚠️  Cleanup failed: {e}")

        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    try:
        signal.signal(signal.SIGTERM, signal_handler)
    except (AttributeError, ValueError):
        pass  # Not available on all platforms


def with_cancellation(operation_name: str):
    """
    Decorator to make function cancellable with CTRL-C.

    Args:
        operation_name: Name of the operation

    Example:
        >>> @with_cancellation("Processing interviews")
        ... def process_interviews():
        ...     for i in range(1000):
        ...         process_item(i)
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            with OperationCanceller(operation_name):
                return func(*args, **kwargs)
        return wrapper
    return decorator


# Export public API
__all__ = [
    'GracefulShutdown',
    'OperationCanceller',
    'setup_signal_handlers',
    'with_cancellation',
]
