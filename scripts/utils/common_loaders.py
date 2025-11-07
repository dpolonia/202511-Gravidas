"""
Common data loading functions for Synthetic Gravidas Pipeline

This module consolidates duplicated data loading functions that were
previously scattered across multiple scripts.
"""

import json
import logging
import os
import sys
from typing import Dict, Any, List, Optional
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: yaml package not installed.")
    print("Please run: pip install pyyaml")
    sys.exit(1)

# Import custom exceptions
from utils.exceptions import (
    ConfigurationError,
    MissingConfigError,
    InvalidDataFormatError,
    DataValidationError,
    InvalidAPIKeyError
)
from utils.validators import validate_config

# Get logger for this module
logger = logging.getLogger(__name__)


def get_api_key(provider: str, allow_config: bool = False) -> str:
    """
    Load API key securely from environment variables.

    This function enforces security best practices by loading API keys
    only from environment variables, not from config files.

    Args:
        provider: Provider name ('anthropic', 'openai', 'google', 'xai')
        allow_config: If True, allow fallback to config file (NOT RECOMMENDED)

    Returns:
        API key string

    Raises:
        InvalidAPIKeyError: If API key not found or appears to be a placeholder

    Example:
        >>> api_key = get_api_key('anthropic')
        >>> # Key loaded from ANTHROPIC_API_KEY environment variable

    Security Notes:
        - API keys should NEVER be committed to version control
        - Always use .env file or environment variables
        - The allow_config parameter is deprecated and should not be used
    """
    provider = provider.lower()
    env_var_name = f"{provider.upper()}_API_KEY"

    # Try to load from environment first (ALWAYS preferred)
    api_key = os.getenv(env_var_name)

    if api_key:
        # Check if it's a placeholder
        if "PLACEHOLDER" in api_key.upper() or "USE-ENVIRONMENT" in api_key.upper():
            raise InvalidAPIKeyError(
                f"{env_var_name} contains a placeholder value, not a real API key. "
                f"Please set a real API key in your environment or .env file."
            )

        logger.debug(f"✅ Loaded API key for {provider} from environment variable {env_var_name}")
        return api_key

    # Environment variable not found
    error_msg = (
        f"❌ API key for '{provider}' not found in environment variables.\n"
        f"\n"
        f"Expected environment variable: {env_var_name}\n"
        f"\n"
        f"To fix this:\n"
        f"1. Copy .env.example to .env:  cp .env.example .env\n"
        f"2. Edit .env and add your API key: {env_var_name}=your-key-here\n"
        f"3. The .env file will be loaded automatically by python-dotenv\n"
        f"\n"
        f"Alternative: Set environment variable directly:\n"
        f"  export {env_var_name}='your-key-here'  # Linux/Mac\n"
        f"  set {env_var_name}=your-key-here       # Windows CMD\n"
        f"  $env:{env_var_name}='your-key-here'    # Windows PowerShell\n"
        f"\n"
        f"⚠️  SECURITY: Never commit API keys to git or put them in config files!"
    )

    logger.error(error_msg)
    raise InvalidAPIKeyError(error_msg)


def load_config(config_path: str = "config/config.yaml",
                validate: bool = True,
                raise_on_error: bool = False) -> Dict[str, Any]:
    """
    Load and validate configuration from YAML file.

    Args:
        config_path: Path to config YAML file (default: config/config.yaml)
        validate: Whether to validate config after loading (default: True)
        raise_on_error: If True, raise exceptions instead of returning empty dict

    Returns:
        Dictionary containing configuration, or empty dict if file not found

    Raises:
        MissingConfigError: If file not found and raise_on_error=True
        ConfigurationError: If YAML parsing fails and raise_on_error=True

    Example:
        >>> config = load_config()
        >>> api_key = config.get('api_keys', {}).get('anthropic', {}).get('api_key')
    """
    try:
        # Check if file exists
        config_file = Path(config_path)
        if not config_file.exists():
            error_msg = f"Config file not found: {config_path}"
            logger.error(error_msg)
            if raise_on_error:
                raise MissingConfigError(error_msg)
            return {}

        # Load YAML
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Validate it's a dictionary
        if not isinstance(config, dict):
            error_msg = f"Config must be a dictionary, got {type(config).__name__}"
            logger.error(error_msg)
            if raise_on_error:
                raise ConfigurationError(error_msg)
            return {}

        logger.debug(f"Loaded config from {config_path}")

        # Validate configuration
        if validate:
            is_valid, warnings = validate_config(config)
            if warnings:
                logger.warning(f"Configuration validation warnings for {config_path}:")
                for warning in warnings:
                    logger.warning(f"  - {warning}")

            if not is_valid and raise_on_error:
                raise ConfigurationError(
                    f"Configuration validation failed: {'; '.join(warnings)}"
                )

        return config

    except yaml.YAMLError as e:
        error_msg = f"Error parsing YAML config at {config_path}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise ConfigurationError(error_msg) from e
        return {}
    except Exception as e:
        if isinstance(e, (MissingConfigError, ConfigurationError)):
            raise
        error_msg = f"Unexpected error loading config from {config_path}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise ConfigurationError(error_msg) from e
        return {}


def load_personas(personas_file: str,
                  validate: bool = False,
                  raise_on_error: bool = True) -> List[Dict[str, Any]]:
    """
    Load and optionally validate personas from JSON file.

    Args:
        personas_file: Path to personas JSON file
        validate: Whether to validate each persona (default: False)
        raise_on_error: If True, raise exceptions. If False, call sys.exit()

    Returns:
        List of persona dictionaries

    Raises:
        InvalidDataFormatError: If file format is invalid
        DataValidationError: If validation fails

    Example:
        >>> personas = load_personas('data/personas/personas.json')
        >>> print(f"Loaded {len(personas)} personas")
    """
    logger.info(f"Loading personas from {personas_file}")

    try:
        # Check if file exists
        personas_path = Path(personas_file)
        if not personas_path.exists():
            error_msg = f"Personas file not found: {personas_file}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        # Load JSON
        with open(personas_file, 'r', encoding='utf-8') as f:
            personas = json.load(f)

        # Validate it's a list
        if not isinstance(personas, list):
            error_msg = f"Personas file must contain a list, got {type(personas).__name__}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        logger.info(f"✅ Loaded {len(personas)} personas")

        # Validate individual personas if requested
        if validate:
            try:
                from utils.validators import validate_persona
            except ImportError:
                from scripts.utils.validators import validate_persona
            validation_errors = []

            for i, persona in enumerate(personas):
                is_valid, warnings = validate_persona(persona, strict=False)
                if warnings:
                    logger.warning(f"Persona {i} ({persona.get('id', 'unknown')}): {', '.join(warnings)}")
                if not is_valid:
                    validation_errors.append(f"Persona {i}: {', '.join(warnings)}")

            if validation_errors and raise_on_error:
                error_msg = f"Persona validation failed:\n" + "\n".join(validation_errors[:5])
                if len(validation_errors) > 5:
                    error_msg += f"\n... and {len(validation_errors) - 5} more errors"
                raise DataValidationError(error_msg)

        return personas

    except json.JSONDecodeError as e:
        error_msg = f"Error parsing personas JSON at {personas_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)
    except Exception as e:
        if isinstance(e, (InvalidDataFormatError, DataValidationError)):
            raise
        error_msg = f"Unexpected error loading personas from {personas_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)


def load_health_records(records_file: str,
                       validate: bool = False,
                       raise_on_error: bool = True) -> List[Dict[str, Any]]:
    """
    Load and optionally validate health records from JSON file.

    Args:
        records_file: Path to health records JSON file
        validate: Whether to validate each health record (default: False)
        raise_on_error: If True, raise exceptions. If False, call sys.exit()

    Returns:
        List of health record dictionaries

    Raises:
        InvalidDataFormatError: If file format is invalid
        DataValidationError: If validation fails

    Example:
        >>> records = load_health_records('data/health_records/health_records.json')
        >>> print(f"Loaded {len(records)} health records")
    """
    logger.info(f"Loading health records from {records_file}")

    try:
        # Check if file exists
        records_path = Path(records_file)
        if not records_path.exists():
            error_msg = f"Health records file not found: {records_file}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        # Load JSON
        with open(records_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

        # Validate it's a list
        if not isinstance(records, list):
            error_msg = f"Health records file must contain a list, got {type(records).__name__}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        logger.info(f"✅ Loaded {len(records)} health records")

        # Validate individual records if requested
        if validate:
            try:
                from utils.validators import validate_health_record
            except ImportError:
                from scripts.utils.validators import validate_health_record
            validation_errors = []

            for i, record in enumerate(records):
                is_valid, warnings = validate_health_record(record, strict=False)
                if warnings:
                    logger.warning(f"Record {i} ({record.get('id', 'unknown')}): {', '.join(warnings)}")
                if not is_valid:
                    validation_errors.append(f"Record {i}: {', '.join(warnings)}")

            if validation_errors and raise_on_error:
                error_msg = f"Health record validation failed:\n" + "\n".join(validation_errors[:5])
                if len(validation_errors) > 5:
                    error_msg += f"\n... and {len(validation_errors) - 5} more errors"
                raise DataValidationError(error_msg)

        return records

    except json.JSONDecodeError as e:
        error_msg = f"Error parsing health records JSON at {records_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)
    except Exception as e:
        if isinstance(e, (InvalidDataFormatError, DataValidationError)):
            raise
        error_msg = f"Unexpected error loading health records from {records_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)


def load_matched_pairs(matched_file: str,
                      validate: bool = False,
                      raise_on_error: bool = True) -> List[Dict[str, Any]]:
    """
    Load and optionally validate matched persona-record pairs from JSON file.

    Args:
        matched_file: Path to matched pairs JSON file
        validate: Whether to validate each matched pair (default: False)
        raise_on_error: If True, raise exceptions. If False, call sys.exit()

    Returns:
        List of matched pair dictionaries

    Raises:
        InvalidDataFormatError: If file format is invalid
        DataValidationError: If validation fails

    Example:
        >>> pairs = load_matched_pairs('data/matched/matched_personas.json')
        >>> print(f"Loaded {len(pairs)} matched pairs")
    """
    logger.info(f"Loading matched pairs from {matched_file}")

    try:
        # Check if file exists
        matched_path = Path(matched_file)
        if not matched_path.exists():
            error_msg = f"Matched pairs file not found: {matched_file}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        # Load JSON
        with open(matched_file, 'r', encoding='utf-8') as f:
            pairs = json.load(f)

        # Validate it's a list
        if not isinstance(pairs, list):
            error_msg = f"Matched pairs file must contain a list, got {type(pairs).__name__}"
            logger.error(error_msg)
            if raise_on_error:
                raise InvalidDataFormatError(error_msg)
            sys.exit(1)

        logger.info(f"✅ Loaded {len(pairs)} matched pairs")

        # Validate individual pairs if requested
        if validate:
            try:
                from utils.validators import validate_matched_pair
            except ImportError:
                from scripts.utils.validators import validate_matched_pair
            validation_errors = []

            for i, pair in enumerate(pairs):
                is_valid, warnings = validate_matched_pair(pair, strict=False)
                if warnings:
                    persona_id = pair.get('persona', {}).get('id', 'unknown') if isinstance(pair.get('persona'), dict) else 'unknown'
                    logger.warning(f"Pair {i} (persona {persona_id}): {', '.join(warnings)}")
                if not is_valid:
                    validation_errors.append(f"Pair {i}: {', '.join(warnings)}")

            if validation_errors and raise_on_error:
                error_msg = f"Matched pair validation failed:\n" + "\n".join(validation_errors[:5])
                if len(validation_errors) > 5:
                    error_msg += f"\n... and {len(validation_errors) - 5} more errors"
                raise DataValidationError(error_msg)

        return pairs

    except json.JSONDecodeError as e:
        error_msg = f"Error parsing matched pairs JSON at {matched_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)
    except Exception as e:
        if isinstance(e, (InvalidDataFormatError, DataValidationError)):
            raise
        error_msg = f"Unexpected error loading matched pairs from {matched_file}: {e}"
        logger.error(error_msg)
        if raise_on_error:
            raise InvalidDataFormatError(error_msg) from e
        sys.exit(1)


# Export public API
__all__ = [
    'get_api_key',
    'load_config',
    'load_personas',
    'load_health_records',
    'load_matched_pairs',
]
