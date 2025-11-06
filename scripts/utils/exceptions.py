"""
Custom exception classes for the synthetic gravidas pipeline.

This module provides specific exception types for different error scenarios,
making error handling more precise and debugging easier.
"""


class PipelineError(Exception):
    """Base exception for all pipeline errors."""
    pass


# Configuration Errors
class ConfigurationError(PipelineError):
    """Raised when configuration is invalid or missing."""
    pass


class InvalidAPIKeyError(ConfigurationError):
    """Raised when API key is missing or invalid."""
    pass


class MissingConfigError(ConfigurationError):
    """Raised when required configuration is missing."""
    pass


# Data Errors
class DataError(PipelineError):
    """Base exception for data-related errors."""
    pass


class FileNotFoundError(DataError):
    """Raised when required data file is not found."""
    pass


class InvalidDataFormatError(DataError):
    """Raised when data format is invalid (e.g., malformed JSON)."""
    pass


class DataValidationError(DataError):
    """Raised when data fails validation checks."""
    pass


# Validation Errors
class ValidationError(PipelineError):
    """Base exception for validation errors."""
    pass


class InvalidAgeError(ValidationError):
    """Raised when age is outside valid range (12-60)."""

    def __init__(self, age: int, min_age: int = 12, max_age: int = 60):
        self.age = age
        self.min_age = min_age
        self.max_age = max_age
        super().__init__(
            f"Invalid age {age}. Must be between {min_age} and {max_age} years."
        )


class InvalidPregnancyWeekError(ValidationError):
    """Raised when pregnancy week is outside valid range (1-42)."""

    def __init__(self, week: int, min_week: int = 1, max_week: int = 42):
        self.week = week
        self.min_week = min_week
        self.max_week = max_week
        super().__init__(
            f"Invalid pregnancy week {week}. Must be between {min_week} and {max_week}."
        )


class InvalidCompatibilityScoreError(ValidationError):
    """Raised when compatibility score is outside valid range (0.0-1.0)."""

    def __init__(self, score: float):
        self.score = score
        super().__init__(
            f"Invalid compatibility score {score}. Must be between 0.0 and 1.0."
        )


class MissingRequiredFieldError(ValidationError):
    """Raised when required field is missing from data."""

    def __init__(self, field_name: str, data_type: str = "data"):
        self.field_name = field_name
        self.data_type = data_type
        super().__init__(
            f"Missing required field '{field_name}' in {data_type}."
        )


class InvalidTypeError(ValidationError):
    """Raised when field has wrong type."""

    def __init__(self, field_name: str, expected_type: str, actual_type: str):
        self.field_name = field_name
        self.expected_type = expected_type
        self.actual_type = actual_type
        super().__init__(
            f"Field '{field_name}' has wrong type. Expected {expected_type}, got {actual_type}."
        )


# Matching Errors
class MatchingError(PipelineError):
    """Base exception for matching-related errors."""
    pass


class NoMatchFoundError(MatchingError):
    """Raised when no suitable match can be found."""

    def __init__(self, persona_id: str, min_score: float = 0.0):
        self.persona_id = persona_id
        self.min_score = min_score
        super().__init__(
            f"No match found for persona '{persona_id}' with minimum score {min_score}."
        )


class InsufficientDataError(MatchingError):
    """Raised when there's not enough data for matching."""

    def __init__(self, data_type: str, required: int, available: int):
        self.data_type = data_type
        self.required = required
        self.available = available
        super().__init__(
            f"Insufficient {data_type}: need {required}, have {available}."
        )


# Interview Errors
class InterviewError(PipelineError):
    """Base exception for interview-related errors."""
    pass


class APIError(InterviewError):
    """Raised when API call fails."""

    def __init__(self, provider: str, message: str, original_error: Exception = None):
        self.provider = provider
        self.message = message
        self.original_error = original_error
        super().__init__(
            f"API error from {provider}: {message}"
        )


class InterviewProtocolError(InterviewError):
    """Raised when interview protocol is invalid."""

    def __init__(self, protocol_file: str, message: str):
        self.protocol_file = protocol_file
        self.message = message
        super().__init__(
            f"Invalid interview protocol in {protocol_file}: {message}"
        )


class MaxTurnsExceededError(InterviewError):
    """Raised when interview exceeds maximum turns."""

    def __init__(self, max_turns: int, persona_id: str = None):
        self.max_turns = max_turns
        self.persona_id = persona_id
        msg = f"Interview exceeded maximum turns ({max_turns})"
        if persona_id:
            msg += f" for persona {persona_id}"
        super().__init__(msg)


# Health Record Errors
class HealthRecordError(PipelineError):
    """Base exception for health record errors."""
    pass


class SyntheaError(HealthRecordError):
    """Raised when Synthea execution fails."""

    def __init__(self, message: str, synthea_path: str = None):
        self.message = message
        self.synthea_path = synthea_path
        super().__init__(
            f"Synthea error: {message}" +
            (f" (path: {synthea_path})" if synthea_path else "")
        )


class FHIRParsingError(HealthRecordError):
    """Raised when FHIR data parsing fails."""

    def __init__(self, message: str, file_path: str = None):
        self.message = message
        self.file_path = file_path
        super().__init__(
            f"FHIR parsing error: {message}" +
            (f" in {file_path}" if file_path else "")
        )


# Retry Errors
class RetryError(PipelineError):
    """Raised when all retry attempts are exhausted."""

    def __init__(self, operation: str, attempts: int, last_error: Exception = None):
        self.operation = operation
        self.attempts = attempts
        self.last_error = last_error
        super().__init__(
            f"Operation '{operation}' failed after {attempts} attempts." +
            (f" Last error: {last_error}" if last_error else "")
        )
