"""
Retry logic with exponential backoff for API calls.

This module provides decorators and utilities for retrying failed API calls
with configurable backoff strategies.
"""

import time
import logging
from functools import wraps
from typing import Callable, Type, Tuple, Optional

# Import custom exception (handle both direct and package imports)
try:
    from utils.exceptions import RetryError
except ImportError:
    from scripts.utils.exceptions import RetryError

logger = logging.getLogger(__name__)


def exponential_backoff_retry(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exponential_base: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,),
    on_retry: Optional[Callable] = None
):
    """
    Decorator that retries a function with exponential backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        initial_delay: Initial delay in seconds before first retry (default: 1.0)
        max_delay: Maximum delay between retries in seconds (default: 60.0)
        exponential_base: Base for exponential backoff calculation (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: all Exception)
        on_retry: Optional callback function called on each retry with (attempt, exception, delay)

    Returns:
        Decorated function that retries on failure

    Example:
        @exponential_backoff_retry(max_retries=5, initial_delay=2.0)
        def call_api():
            return api.request()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # If this was the last attempt, raise
                    if attempt == max_retries:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise RetryError(
                            operation=func.__name__,
                            attempts=max_retries,
                            last_error=e
                        ) from e

                    # Calculate delay with exponential backoff
                    delay = min(
                        initial_delay * (exponential_base ** attempt),
                        max_delay
                    )

                    # Log retry attempt
                    logger.warning(
                        f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    logger.info(
                        f"🔄 Retrying in {delay:.1f}s..."
                    )

                    # Call optional callback
                    if on_retry:
                        on_retry(attempt + 1, e, delay)

                    # Wait before retry
                    time.sleep(delay)

            # This should never be reached, but just in case
            raise RetryError(
                operation=func.__name__,
                attempts=max_retries,
                last_error=last_exception
            ) from last_exception

        return wrapper
    return decorator


def linear_backoff_retry(
    max_retries: int = 3,
    delay: float = 2.0,
    exceptions: Tuple[Type[Exception], ...] = (Exception,)
):
    """
    Decorator that retries a function with linear (fixed) backoff.

    Args:
        max_retries: Maximum number of retry attempts (default: 3)
        delay: Fixed delay in seconds between retries (default: 2.0)
        exceptions: Tuple of exception types to catch and retry (default: all Exception)

    Returns:
        Decorated function that retries on failure

    Example:
        @linear_backoff_retry(max_retries=3, delay=5.0)
        def call_api():
            return api.request()
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_retries:
                        logger.error(
                            f"❌ {func.__name__} failed after {max_retries} retries: {e}"
                        )
                        raise RetryError(
                            operation=func.__name__,
                            attempts=max_retries,
                            last_error=e
                        ) from e

                    logger.warning(
                        f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{max_retries + 1}): {e}"
                    )
                    logger.info(f"🔄 Retrying in {delay:.1f}s...")

                    time.sleep(delay)

            raise RetryError(
                operation=func.__name__,
                attempts=max_retries,
                last_error=last_exception
            ) from last_exception

        return wrapper
    return decorator


class RetryConfig:
    """Configuration class for retry behavior."""

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        strategy: str = "exponential"
    ):
        """
        Initialize retry configuration.

        Args:
            max_retries: Maximum number of retry attempts
            initial_delay: Initial delay before first retry
            max_delay: Maximum delay between retries
            exponential_base: Base for exponential backoff
            strategy: Retry strategy - "exponential" or "linear"
        """
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.strategy = strategy

    @classmethod
    def from_config(cls, config: dict) -> 'RetryConfig':
        """
        Create RetryConfig from configuration dictionary.

        Args:
            config: Configuration dictionary with retry settings

        Returns:
            RetryConfig instance
        """
        retry_config = config.get('retry', {})
        return cls(
            max_retries=retry_config.get('max_retries', 3),
            initial_delay=retry_config.get('initial_delay', 1.0),
            max_delay=retry_config.get('max_delay', 60.0),
            exponential_base=retry_config.get('exponential_base', 2.0),
            strategy=retry_config.get('strategy', 'exponential')
        )

    def create_decorator(self, exceptions: Tuple[Type[Exception], ...] = (Exception,)):
        """
        Create retry decorator based on this configuration.

        Args:
            exceptions: Tuple of exception types to catch

        Returns:
            Retry decorator function
        """
        if self.strategy == "linear":
            return linear_backoff_retry(
                max_retries=self.max_retries,
                delay=self.initial_delay,
                exceptions=exceptions
            )
        else:
            return exponential_backoff_retry(
                max_retries=self.max_retries,
                initial_delay=self.initial_delay,
                max_delay=self.max_delay,
                exponential_base=self.exponential_base,
                exceptions=exceptions
            )
