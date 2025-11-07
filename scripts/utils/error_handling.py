"""
Enhanced error handling with helpful recovery suggestions.

This module provides:
- User-friendly error messages
- Recovery suggestions
- Command examples for retry
- Contextual help
"""

import sys
import traceback
from typing import Optional, List, Dict, Any
import logging

logger = logging.getLogger(__name__)


class PipelineError(Exception):
    """
    Enhanced pipeline error with recovery suggestions.

    Example:
        >>> raise PipelineError(
        ...     "API rate limit exceeded",
        ...     suggestions=[
        ...         "Wait 60 seconds and retry",
        ...         "Use a different model with lower rate limit"
        ...     ],
        ...     retry_command="python script.py --resume-from 50"
        ... )
    """

    def __init__(self, message: str, suggestions: Optional[List[str]] = None,
                 retry_command: Optional[str] = None, context: Optional[Dict[str, Any]] = None):
        """
        Initialize pipeline error.

        Args:
            message: Error message
            suggestions: List of recovery suggestions
            retry_command: Command to retry the operation
            context: Additional context information
        """
        super().__init__(message)
        self.suggestions = suggestions or []
        self.retry_command = retry_command
        self.context = context or {}

    def format_error(self) -> str:
        """Format error with suggestions and retry command."""
        lines = [
            "",
            "❌ Error: " + str(self),
            ""
        ]

        if self.context:
            lines.append("Context:")
            for key, value in self.context.items():
                lines.append(f"  • {key}: {value}")
            lines.append("")

        if self.suggestions:
            lines.append("Try one of these:")
            for i, suggestion in enumerate(self.suggestions, 1):
                lines.append(f"  {i}. {suggestion}")
            lines.append("")

        if self.retry_command:
            lines.append("Command to retry:")
            lines.append(f"  {self.retry_command}")
            lines.append("")

        return "\n".join(lines)


def handle_api_error(error: Exception, operation: str, **context) -> PipelineError:
    """
    Handle API errors with helpful suggestions.

    Args:
        error: Original exception
        operation: Operation being performed
        **context: Additional context

    Returns:
        PipelineError with suggestions
    """
    error_str = str(error).lower()

    # Rate limit errors
    if "rate limit" in error_str or "429" in error_str:
        return PipelineError(
            f"API rate limit exceeded during {operation}",
            suggestions=[
                "Wait 60 seconds and retry",
                "Use a different model with lower rate limit",
                "Reduce the number of concurrent requests",
                "Check your API quota at the provider console"
            ],
            context=context
        )

    # Authentication errors
    elif "authentication" in error_str or "401" in error_str or "api key" in error_str:
        return PipelineError(
            f"API authentication failed during {operation}",
            suggestions=[
                "Check that your API key is correctly set in .env file",
                "Verify the API key is valid and not expired",
                "Ensure environment variables are loaded (cp .env.example .env)",
                "Generate a new API key if needed"
            ],
            context=context
        )

    # Network errors
    elif "connection" in error_str or "network" in error_str or "timeout" in error_str:
        return PipelineError(
            f"Network error during {operation}",
            suggestions=[
                "Check your internet connection",
                "Retry the operation",
                "Check if the API service is down (status page)",
                "Try again in a few minutes"
            ],
            context=context
        )

    # Model not found errors
    elif "model" in error_str and ("not found" in error_str or "invalid" in error_str):
        return PipelineError(
            f"Invalid model specified during {operation}",
            suggestions=[
                "Check the model name spelling",
                "Verify the model is available for your account",
                "Use a different model from the supported list",
                "Check model availability in the provider documentation"
            ],
            context=context
        )

    # Generic error
    else:
        return PipelineError(
            f"Error during {operation}: {error}",
            suggestions=[
                "Check the error message above for details",
                "Review the logs for more information",
                "Try running with --verbose for debug output",
                "Contact support if the issue persists"
            ],
            context=context
        )


def handle_file_error(error: Exception, file_path: str, operation: str) -> PipelineError:
    """
    Handle file-related errors.

    Args:
        error: Original exception
        file_path: Path to the file
        operation: Operation being performed

    Returns:
        PipelineError with suggestions
    """
    error_str = str(error).lower()

    # File not found
    if "no such file" in error_str or "not found" in error_str:
        return PipelineError(
            f"File not found: {file_path}",
            suggestions=[
                f"Check that the file exists: ls {file_path}",
                "Verify the file path is correct",
                "Run the previous pipeline step to generate the file",
                "Check if the file has a different name or location"
            ],
            context={'file_path': file_path, 'operation': operation}
        )

    # Permission denied
    elif "permission" in error_str:
        return PipelineError(
            f"Permission denied: {file_path}",
            suggestions=[
                f"Check file permissions: ls -l {file_path}",
                f"Try running with appropriate permissions",
                "Ensure the directory is writable",
                "Check if another process has the file locked"
            ],
            context={'file_path': file_path, 'operation': operation}
        )

    # Invalid format
    elif "json" in error_str or "parse" in error_str or "decode" in error_str:
        return PipelineError(
            f"Invalid file format: {file_path}",
            suggestions=[
                f"Validate the JSON format: python -m json.tool {file_path}",
                "Check if the file is corrupted",
                "Regenerate the file from the previous step",
                "Check if the file encoding is correct (should be UTF-8)"
            ],
            context={'file_path': file_path, 'operation': operation}
        )

    # Generic file error
    else:
        return PipelineError(
            f"File error during {operation}: {error}",
            suggestions=[
                f"Check the file exists: ls {file_path}",
                f"Verify file permissions and format",
                "Try regenerating the file",
                "Check available disk space"
            ],
            context={'file_path': file_path, 'operation': operation}
        )


def handle_validation_error(error: Exception, item_type: str, **context) -> PipelineError:
    """
    Handle validation errors.

    Args:
        error: Original exception
        item_type: Type of item being validated
        **context: Additional context

    Returns:
        PipelineError with suggestions
    """
    return PipelineError(
        f"Validation failed for {item_type}: {error}",
        suggestions=[
            f"Check the {item_type} data format",
            "Review validation requirements in the documentation",
            "Use the validation tool: python scripts/validate_pipeline_data.py",
            "Fix the data and retry the operation"
        ],
        context=context
    )


def setup_error_handlers():
    """
    Setup global exception handlers for better error messages.

    Call this at the start of main scripts.

    Example:
        >>> if __name__ == '__main__':
        ...     setup_error_handlers()
        ...     main()
    """
    def exception_handler(exc_type, exc_value, exc_traceback):
        """Global exception handler."""
        # Don't handle keyboard interrupt
        if issubclass(exc_type, KeyboardInterrupt):
            print("\n\n⚠️  Operation cancelled by user")
            print("Partial results may have been saved. Check the output directory.")
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return

        # Handle PipelineError specially
        if isinstance(exc_value, PipelineError):
            print(exc_value.format_error())
            logger.error(f"Pipeline error: {exc_value}", exc_info=False)
        else:
            # Log full traceback
            logger.error("Unhandled exception:", exc_info=(exc_type, exc_value, exc_traceback))

            # Show simplified error to user
            print("\n❌ Unexpected error occurred")
            print(f"\nError: {exc_type.__name__}: {exc_value}")
            print("\nFull traceback has been logged.")
            print("Try running with --verbose for more details.")

    sys.excepthook = exception_handler


def with_error_handling(func):
    """
    Decorator to wrap functions with enhanced error handling.

    Example:
        >>> @with_error_handling
        ... def process_interviews():
        ...     # Your code here
        ...     pass
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if isinstance(e, PipelineError):
                raise
            else:
                # Try to provide helpful context
                operation = func.__name__.replace('_', ' ')
                pipeline_error = handle_api_error(e, operation)
                raise pipeline_error from e

    return wrapper


def print_error(message: str, suggestions: Optional[List[str]] = None,
                retry_command: Optional[str] = None):
    """
    Print a formatted error message.

    Args:
        message: Error message
        suggestions: Optional recovery suggestions
        retry_command: Optional retry command

    Example:
        >>> print_error(
        ...     "Configuration file not found",
        ...     suggestions=["Create config.yaml from template",
        ...                 "Check file path"],
        ...     retry_command="cp config.yaml.template config.yaml"
        ... )
    """
    error = PipelineError(message, suggestions, retry_command)
    print(error.format_error())


def print_warning(message: str, details: Optional[str] = None):
    """
    Print a formatted warning message.

    Args:
        message: Warning message
        details: Optional additional details

    Example:
        >>> print_warning("API key not found", "Falling back to default configuration")
    """
    print(f"\n⚠️  Warning: {message}")
    if details:
        print(f"   {details}")
    print()


def print_success(message: str, details: Optional[str] = None):
    """
    Print a formatted success message.

    Args:
        message: Success message
        details: Optional additional details

    Example:
        >>> print_success("Pipeline completed", "Processed 100 items in 5 minutes")
    """
    print(f"\n✅ {message}")
    if details:
        print(f"   {details}")
    print()


# Export public API
__all__ = [
    'PipelineError',
    'handle_api_error',
    'handle_file_error',
    'handle_validation_error',
    'setup_error_handlers',
    'with_error_handling',
    'print_error',
    'print_warning',
    'print_success',
]
