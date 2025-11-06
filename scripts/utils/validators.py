"""
Input validation functions for the synthetic gravidas pipeline.

This module provides validation for all data inputs to ensure data quality
and prevent errors downstream.
"""

from typing import Dict, Any, List, Optional, Tuple
import logging

# Handle both direct and package imports
try:
    from utils.exceptions import (
        InvalidAgeError,
        InvalidPregnancyWeekError,
        InvalidCompatibilityScoreError,
        MissingRequiredFieldError,
        InvalidTypeError,
        DataValidationError
    )
except ImportError:
    from scripts.utils.exceptions import (
        InvalidAgeError,
        InvalidPregnancyWeekError,
        InvalidCompatibilityScoreError,
        MissingRequiredFieldError,
        InvalidTypeError,
        DataValidationError
    )

logger = logging.getLogger(__name__)


# Age Validation
def validate_age(age: Any, min_age: int = 12, max_age: int = 60, field_name: str = "age") -> int:
    """
    Validate age is within valid range for pregnancy.

    Args:
        age: Age value to validate
        min_age: Minimum valid age (default: 12)
        max_age: Maximum valid age (default: 60)
        field_name: Name of field for error messages

    Returns:
        Validated age as integer

    Raises:
        InvalidTypeError: If age is not a number
        InvalidAgeError: If age is outside valid range
    """
    # Type check
    if not isinstance(age, (int, float)):
        raise InvalidTypeError(field_name, "int or float", type(age).__name__)

    # Convert to int
    age_int = int(age)

    # Range check
    if age_int < min_age or age_int > max_age:
        raise InvalidAgeError(age_int, min_age, max_age)

    return age_int


def validate_pregnancy_week(week: Any, min_week: int = 1, max_week: int = 42,
                           field_name: str = "pregnancy_week") -> int:
    """
    Validate pregnancy week is within valid range.

    Args:
        week: Pregnancy week to validate
        min_week: Minimum valid week (default: 1)
        max_week: Maximum valid week (default: 42)
        field_name: Name of field for error messages

    Returns:
        Validated week as integer

    Raises:
        InvalidTypeError: If week is not a number
        InvalidPregnancyWeekError: If week is outside valid range
    """
    # Type check
    if not isinstance(week, (int, float)):
        raise InvalidTypeError(field_name, "int or float", type(week).__name__)

    # Convert to int
    week_int = int(week)

    # Range check
    if week_int < min_week or week_int > max_week:
        raise InvalidPregnancyWeekError(week_int, min_week, max_week)

    return week_int


def validate_compatibility_score(score: Any, field_name: str = "compatibility_score") -> float:
    """
    Validate compatibility score is between 0.0 and 1.0.

    Args:
        score: Score to validate
        field_name: Name of field for error messages

    Returns:
        Validated score as float

    Raises:
        InvalidTypeError: If score is not a number
        InvalidCompatibilityScoreError: If score is outside [0.0, 1.0]
    """
    # Type check
    if not isinstance(score, (int, float)):
        raise InvalidTypeError(field_name, "float", type(score).__name__)

    # Convert to float
    score_float = float(score)

    # Range check
    if score_float < 0.0 or score_float > 1.0:
        raise InvalidCompatibilityScoreError(score_float)

    return score_float


def validate_required_fields(data: Dict[str, Any], required_fields: List[str],
                            data_type: str = "data") -> None:
    """
    Validate that all required fields are present in data.

    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        data_type: Type of data for error messages

    Raises:
        MissingRequiredFieldError: If any required field is missing
    """
    for field in required_fields:
        if field not in data:
            raise MissingRequiredFieldError(field, data_type)


def validate_type(value: Any, expected_type: type, field_name: str) -> None:
    """
    Validate that value has expected type.

    Args:
        value: Value to validate
        expected_type: Expected Python type
        field_name: Name of field for error messages

    Raises:
        InvalidTypeError: If value has wrong type
    """
    if not isinstance(value, expected_type):
        raise InvalidTypeError(
            field_name,
            expected_type.__name__,
            type(value).__name__
        )


def validate_persona(persona: Dict[str, Any], strict: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate a persona dictionary.

    Args:
        persona: Persona dictionary to validate
        strict: If True, raise exceptions. If False, return warnings.

    Returns:
        Tuple of (is_valid, warnings_list)

    Raises:
        Various validation errors if strict=True
    """
    warnings = []
    is_valid = True

    try:
        # Check required fields
        required_fields = ['age', 'gender', 'description']
        if strict:
            validate_required_fields(persona, required_fields, "persona")
        else:
            for field in required_fields:
                if field not in persona:
                    warnings.append(f"Missing required field: {field}")
                    is_valid = False

        # Validate age if present
        if 'age' in persona and persona['age'] is not None:
            try:
                validate_age(persona['age'])
            except (InvalidAgeError, InvalidTypeError) as e:
                if strict:
                    raise
                warnings.append(str(e))
                is_valid = False

        # Validate gender if present
        if 'gender' in persona and persona['gender']:
            if persona['gender'].lower() not in ['female', 'f']:
                msg = f"Gender is '{persona['gender']}', expected 'female' for pregnancy study"
                if strict:
                    raise DataValidationError(msg)
                warnings.append(msg)

        # Validate pregnancy week if present
        if 'pregnancy_week' in persona and persona['pregnancy_week'] is not None:
            try:
                validate_pregnancy_week(persona['pregnancy_week'])
            except (InvalidPregnancyWeekError, InvalidTypeError) as e:
                if strict:
                    raise
                warnings.append(str(e))
                is_valid = False

        # Validate education if present
        if 'education' in persona and persona['education']:
            valid_education = ['no_degree', 'high_school', 'bachelors', 'masters',
                             'doctorate', 'unknown', 'college', 'graduate']
            if persona['education'].lower() not in valid_education:
                msg = f"Unknown education level: {persona['education']}"
                warnings.append(msg)

        # Validate income level if present
        if 'income_level' in persona and persona['income_level']:
            valid_income = ['low', 'lower_middle', 'middle', 'upper_middle',
                          'high', 'unknown']
            if persona['income_level'].lower() not in valid_income:
                msg = f"Unknown income level: {persona['income_level']}"
                warnings.append(msg)

    except Exception as e:
        if strict:
            raise
        warnings.append(str(e))
        is_valid = False

    return is_valid, warnings


def validate_health_record(record: Dict[str, Any], strict: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate a health record dictionary.

    Args:
        record: Health record dictionary to validate
        strict: If True, raise exceptions. If False, return warnings.

    Returns:
        Tuple of (is_valid, warnings_list)

    Raises:
        Various validation errors if strict=True
    """
    warnings = []
    is_valid = True

    try:
        # Check required fields
        required_fields = ['id']
        if strict:
            validate_required_fields(record, required_fields, "health_record")
        else:
            for field in required_fields:
                if field not in record:
                    warnings.append(f"Missing required field: {field}")
                    is_valid = False

        # Validate age if present
        if 'age' in record and record['age'] is not None:
            try:
                validate_age(record['age'])
            except (InvalidAgeError, InvalidTypeError) as e:
                if strict:
                    raise
                warnings.append(str(e))
                is_valid = False

        # Validate gestational age if present
        if 'gestational_age_weeks' in record and record['gestational_age_weeks'] is not None:
            try:
                validate_pregnancy_week(record['gestational_age_weeks'], field_name='gestational_age_weeks')
            except (InvalidPregnancyWeekError, InvalidTypeError) as e:
                if strict:
                    raise
                warnings.append(str(e))
                is_valid = False

        # Validate data types for common fields
        type_checks = {
            'conditions': list,
            'medications': list,
            'allergies': list
        }

        for field, expected_type in type_checks.items():
            if field in record and record[field] is not None:
                if not isinstance(record[field], expected_type):
                    msg = f"Field '{field}' should be {expected_type.__name__}, got {type(record[field]).__name__}"
                    if strict:
                        raise InvalidTypeError(field, expected_type.__name__, type(record[field]).__name__)
                    warnings.append(msg)
                    is_valid = False

    except Exception as e:
        if strict:
            raise
        warnings.append(str(e))
        is_valid = False

    return is_valid, warnings


def validate_matched_pair(pair: Dict[str, Any], strict: bool = False) -> Tuple[bool, List[str]]:
    """
    Validate a matched persona-record pair.

    Args:
        pair: Matched pair dictionary to validate
        strict: If True, raise exceptions. If False, return warnings.

    Returns:
        Tuple of (is_valid, warnings_list)

    Raises:
        Various validation errors if strict=True
    """
    warnings = []
    is_valid = True

    try:
        # Check required fields
        required_fields = ['persona', 'health_record', 'compatibility_score']
        if strict:
            validate_required_fields(pair, required_fields, "matched_pair")
        else:
            for field in required_fields:
                if field not in pair:
                    warnings.append(f"Missing required field: {field}")
                    is_valid = False

        # Validate compatibility score
        if 'compatibility_score' in pair:
            try:
                validate_compatibility_score(pair['compatibility_score'])
            except (InvalidCompatibilityScoreError, InvalidTypeError) as e:
                if strict:
                    raise
                warnings.append(str(e))
                is_valid = False

        # Validate nested persona
        if 'persona' in pair and isinstance(pair['persona'], dict):
            persona_valid, persona_warnings = validate_persona(pair['persona'], strict=False)
            warnings.extend(persona_warnings)
            if not persona_valid:
                is_valid = False

        # Validate nested health record
        if 'health_record' in pair and isinstance(pair['health_record'], dict):
            record_valid, record_warnings = validate_health_record(pair['health_record'], strict=False)
            warnings.extend(record_warnings)
            if not record_valid:
                is_valid = False

        # Check age consistency
        if ('persona' in pair and 'health_record' in pair and
            isinstance(pair['persona'], dict) and isinstance(pair['health_record'], dict)):
            persona_age = pair['persona'].get('age')
            record_age = pair['health_record'].get('age')
            score = pair.get('compatibility_score', 0)

            if persona_age and record_age:
                age_diff = abs(persona_age - record_age)
                # If ages differ significantly but score is high, warn
                if age_diff > 10 and score > 0.8:
                    warnings.append(
                        f"Suspicious: Large age difference ({age_diff} years) "
                        f"but high compatibility score ({score:.2f})"
                    )

    except Exception as e:
        if strict:
            raise
        warnings.append(str(e))
        is_valid = False

    return is_valid, warnings


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate configuration dictionary.

    Args:
        config: Configuration dictionary to validate

    Returns:
        Tuple of (is_valid, warnings_list)
    """
    warnings = []
    is_valid = True

    # Check for active provider
    if 'active_provider' not in config:
        warnings.append("Missing 'active_provider' in config")
        is_valid = False
    else:
        valid_providers = ['anthropic', 'openai', 'google']
        if config['active_provider'].lower() not in valid_providers:
            warnings.append(
                f"Invalid provider '{config['active_provider']}'. "
                f"Valid options: {', '.join(valid_providers)}"
            )
            is_valid = False

    # Check for API keys section
    if 'api_keys' not in config:
        warnings.append("Missing 'api_keys' section in config")
        is_valid = False
    else:
        provider = config.get('active_provider', '').lower()
        if provider and provider not in config['api_keys']:
            warnings.append(f"No API key configuration for provider '{provider}'")
            is_valid = False

    # Validate numeric parameters
    if 'interview' in config:
        interview_cfg = config['interview']

        if 'max_turns' in interview_cfg:
            max_turns = interview_cfg['max_turns']
            if not isinstance(max_turns, int) or max_turns < 1:
                warnings.append("'interview.max_turns' must be a positive integer")
                is_valid = False

        if 'batch_size' in interview_cfg:
            batch_size = interview_cfg['batch_size']
            if not isinstance(batch_size, int) or batch_size < 1:
                warnings.append("'interview.batch_size' must be a positive integer")
                is_valid = False

    # Validate retry configuration
    if 'retry' in config:
        retry_cfg = config['retry']

        if 'max_retries' in retry_cfg:
            max_retries = retry_cfg['max_retries']
            if not isinstance(max_retries, int) or max_retries < 0:
                warnings.append("'retry.max_retries' must be a non-negative integer")
                is_valid = False

        if 'initial_delay' in retry_cfg:
            delay = retry_cfg['initial_delay']
            if not isinstance(delay, (int, float)) or delay <= 0:
                warnings.append("'retry.initial_delay' must be a positive number")
                is_valid = False

    return is_valid, warnings
