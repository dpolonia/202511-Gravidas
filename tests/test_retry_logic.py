"""
Tests for scripts/utils/retry_logic.py

Tests retry decorators and configuration for API calls.
"""

import pytest
import time
from scripts.utils.retry_logic import (
    exponential_backoff_retry,
    linear_backoff_retry,
    RetryConfig,
    RetryError
)


@pytest.mark.retry
@pytest.mark.unit
class TestExponentialBackoffRetry:
    """Tests for exponential_backoff_retry decorator."""

    def test_successful_call_no_retry(self):
        """Test that successful calls don't trigger retries."""
        call_count = [0]

        @exponential_backoff_retry(max_retries=3, initial_delay=0.1)
        def successful_function():
            call_count[0] += 1
            return "success"

        result = successful_function()

        assert result == "success"
        assert call_count[0] == 1  # Should only be called once

    def test_eventual_success_with_retries(self):
        """Test function that fails then succeeds."""
        call_count = [0]

        @exponential_backoff_retry(max_retries=3, initial_delay=0.1)
        def fail_twice_then_succeed():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception(f"Failure {call_count[0]}")
            return "success"

        start_time = time.time()
        result = fail_twice_then_succeed()
        elapsed = time.time() - start_time

        assert result == "success"
        assert call_count[0] == 3
        # Should have delays: 0.1s + 0.2s = 0.3s minimum
        assert elapsed >= 0.3

    def test_all_retries_exhausted(self):
        """Test that RetryError is raised after max retries."""
        call_count = [0]

        @exponential_backoff_retry(max_retries=2, initial_delay=0.1)
        def always_fails():
            call_count[0] += 1
            raise ValueError("Always fails")

        with pytest.raises(RetryError) as exc_info:
            always_fails()

        assert call_count[0] == 3  # Initial call + 2 retries
        assert "failed after 2 retries" in str(exc_info.value)

    def test_exponential_backoff_timing(self):
        """Test that delays follow exponential pattern."""
        call_count = [0]
        call_times = []

        @exponential_backoff_retry(max_retries=3, initial_delay=0.1, exponential_base=2.0)
        def record_timing():
            call_times.append(time.time())
            call_count[0] += 1
            if call_count[0] < 4:
                raise Exception("Fail")
            return "success"

        record_timing()

        # Check delays between calls
        # Delay 1: ~0.1s, Delay 2: ~0.2s, Delay 3: ~0.4s
        if len(call_times) >= 2:
            delay1 = call_times[1] - call_times[0]
            assert 0.08 <= delay1 <= 0.15  # ~0.1s with tolerance

        if len(call_times) >= 3:
            delay2 = call_times[2] - call_times[1]
            assert 0.18 <= delay2 <= 0.25  # ~0.2s with tolerance

    def test_max_delay_cap(self):
        """Test that max_delay caps the retry delay."""
        call_count = [0]

        @exponential_backoff_retry(max_retries=5, initial_delay=10.0, max_delay=0.2, exponential_base=2.0)
        def test_max_cap():
            call_count[0] += 1
            if call_count[0] < 3:
                raise Exception("Fail")
            return "success"

        start_time = time.time()
        test_max_cap()
        elapsed = time.time() - start_time

        # Even though initial_delay is 10s, max_delay caps it at 0.2s
        # So total delay should be ~0.4s (2 retries * 0.2s cap)
        assert elapsed < 1.0  # Much less than if delays weren't capped

    def test_specific_exception_types(self):
        """Test retry only on specific exception types."""
        call_count = [0]

        @exponential_backoff_retry(max_retries=3, initial_delay=0.1, exceptions=(ValueError,))
        def raise_different_exceptions():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("This should retry")
            elif call_count[0] == 2:
                raise TypeError("This should NOT retry")

        with pytest.raises(TypeError):
            raise_different_exceptions()

        # Should have called twice: once for ValueError (retried), once for TypeError (not retried)
        assert call_count[0] == 2

    def test_on_retry_callback(self):
        """Test that on_retry callback is called."""
        callback_calls = []

        def record_retry(attempt, exception, delay):
            callback_calls.append({
                'attempt': attempt,
                'exception': str(exception),
                'delay': delay
            })

        @exponential_backoff_retry(max_retries=2, initial_delay=0.1, on_retry=record_retry)
        def fail_twice():
            if len(callback_calls) < 2:
                raise Exception("Fail")
            return "success"

        fail_twice()

        assert len(callback_calls) == 2
        assert callback_calls[0]['attempt'] == 1
        assert callback_calls[1]['attempt'] == 2


@pytest.mark.retry
@pytest.mark.unit
class TestLinearBackoffRetry:
    """Tests for linear_backoff_retry decorator."""

    def test_linear_backoff_successful(self):
        """Test successful call with linear backoff."""
        call_count = [0]

        @linear_backoff_retry(max_retries=3, delay=0.1)
        def succeed_immediately():
            call_count[0] += 1
            return "success"

        result = succeed_immediately()

        assert result == "success"
        assert call_count[0] == 1

    def test_linear_backoff_eventual_success(self):
        """Test eventual success with linear delays."""
        call_count = [0]

        @linear_backoff_retry(max_retries=3, delay=0.1)
        def fail_once():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail once")
            return "success"

        start_time = time.time()
        result = fail_once()
        elapsed = time.time() - start_time

        assert result == "success"
        assert call_count[0] == 2
        # Should have one 0.1s delay
        assert elapsed >= 0.1

    def test_linear_backoff_timing(self):
        """Test that delays are linear (constant)."""
        call_count = [0]
        call_times = []

        @linear_backoff_retry(max_retries=3, delay=0.15)
        def record_linear_timing():
            call_times.append(time.time())
            call_count[0] += 1
            if call_count[0] < 4:
                raise Exception("Fail")
            return "success"

        record_linear_timing()

        # All delays should be approximately equal (~0.15s)
        delays = [call_times[i+1] - call_times[i] for i in range(len(call_times) - 1)]
        for delay in delays:
            assert 0.13 <= delay <= 0.18  # ~0.15s with tolerance


@pytest.mark.retry
@pytest.mark.unit
class TestRetryConfig:
    """Tests for RetryConfig class."""

    def test_retry_config_creation(self):
        """Test creating RetryConfig with parameters."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=120.0,
            exponential_base=3.0,
            strategy='exponential'
        )

        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 120.0
        assert config.exponential_base == 3.0
        assert config.strategy == 'exponential'

    def test_retry_config_from_dict(self):
        """Test creating RetryConfig from configuration dict."""
        config_dict = {
            'retry': {
                'max_retries': 4,
                'initial_delay': 1.5,
                'max_delay': 90.0,
                'exponential_base': 2.5,
                'strategy': 'linear'
            }
        }

        config = RetryConfig.from_config(config_dict)

        assert config.max_retries == 4
        assert config.initial_delay == 1.5
        assert config.max_delay == 90.0
        assert config.exponential_base == 2.5
        assert config.strategy == 'linear'

    def test_retry_config_defaults(self):
        """Test RetryConfig with default values."""
        config_dict = {}  # Empty config
        config = RetryConfig.from_config(config_dict)

        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.exponential_base == 2.0
        assert config.strategy == 'exponential'

    def test_retry_config_partial_values(self):
        """Test RetryConfig with partial configuration."""
        config_dict = {
            'retry': {
                'max_retries': 5,
                'strategy': 'linear'
                # Missing other values - should use defaults
            }
        }

        config = RetryConfig.from_config(config_dict)

        assert config.max_retries == 5
        assert config.strategy == 'linear'
        assert config.initial_delay == 1.0  # Default
        assert config.max_delay == 60.0  # Default

    def test_create_exponential_decorator(self):
        """Test creating exponential backoff decorator from config."""
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            strategy='exponential'
        )

        decorator = config.create_decorator()
        call_count = [0]

        @decorator
        def test_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count[0] == 2

    def test_create_linear_decorator(self):
        """Test creating linear backoff decorator from config."""
        config = RetryConfig(
            max_retries=2,
            initial_delay=0.1,
            strategy='linear'
        )

        decorator = config.create_decorator()
        call_count = [0]

        @decorator
        def test_func():
            call_count[0] += 1
            if call_count[0] < 2:
                raise Exception("Fail")
            return "success"

        result = test_func()
        assert result == "success"
        assert call_count[0] == 2

    def test_decorator_with_custom_exceptions(self):
        """Test creating decorator with custom exception types."""
        config = RetryConfig(max_retries=2, initial_delay=0.1)

        decorator = config.create_decorator(exceptions=(ValueError,))

        call_count = [0]

        @decorator
        def test_func():
            call_count[0] += 1
            if call_count[0] == 1:
                raise ValueError("Retryable")
            elif call_count[0] == 2:
                raise TypeError("Not retryable")

        with pytest.raises(TypeError):
            test_func()

        assert call_count[0] == 2


@pytest.mark.retry
@pytest.mark.integration
class TestRetryIntegration:
    """Integration tests for retry logic with realistic scenarios."""

    def test_api_call_simulation(self):
        """Simulate API call with transient failures."""
        call_count = [0]
        api_responses = [
            Exception("Network timeout"),
            Exception("Rate limit exceeded"),
            {"status": "success", "data": "result"}
        ]

        @exponential_backoff_retry(max_retries=3, initial_delay=0.1)
        def simulated_api_call():
            response = api_responses[call_count[0]]
            call_count[0] += 1
            if isinstance(response, Exception):
                raise response
            return response

        result = simulated_api_call()

        assert result['status'] == "success"
        assert call_count[0] == 3  # Failed twice, succeeded third time

    def test_retry_config_in_pipeline(self, sample_config):
        """Test retry config integration with pipeline configuration."""
        config = RetryConfig.from_config(sample_config)

        assert config.max_retries == 3
        assert config.strategy == 'exponential'

        # Use this config to create a decorator
        decorator = config.create_decorator()

        # Simulate pipeline function
        call_count = [0]

        @decorator
        def pipeline_operation():
            call_count[0] += 1
            if call_count[0] < 2:
                raise ConnectionError("Transient network error")
            return {"processed": True}

        result = pipeline_operation()

        assert result['processed'] is True
        assert call_count[0] == 2
