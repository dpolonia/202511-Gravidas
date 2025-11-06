"""
Common data loading functions for Synthetic Gravidas Pipeline

This module consolidates duplicated data loading functions that were
previously scattered across multiple scripts.
"""

import json
import logging
import sys
from typing import Dict, Any, List
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: yaml package not installed.")
    print("Please run: pip install pyyaml")
    sys.exit(1)


# Get logger for this module
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config YAML file (default: config/config.yaml)
        
    Returns:
        Dictionary containing configuration, or empty dict if file not found
        
    Example:
        >>> config = load_config()
        >>> api_key = config.get('api_keys', {}).get('anthropic', {}).get('api_key')
    """
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        logger.debug(f"Loaded config from {config_path}")
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        return {}
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML config: {e}")
        return {}


def load_personas(personas_file: str) -> List[Dict[str, Any]]:
    """
    Load personas from JSON file.
    
    Args:
        personas_file: Path to personas JSON file
        
    Returns:
        List of persona dictionaries
        
    Raises:
        SystemExit: If file not found or cannot be parsed
        
    Example:
        >>> personas = load_personas('data/personas/personas.json')
        >>> print(f"Loaded {len(personas)} personas")
    """
    logger.info(f"Loading personas from {personas_file}")
    
    try:
        with open(personas_file, 'r') as f:
            personas = json.load(f)
        
        # Validate it's a list
        if not isinstance(personas, list):
            logger.error(f"Personas file must contain a list, got {type(personas)}")
            sys.exit(1)
            
        logger.info(f"✅ Loaded {len(personas)} personas")
        return personas
        
    except FileNotFoundError:
        logger.error(f"Personas file not found: {personas_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing personas JSON: {e}")
        sys.exit(1)


def load_health_records(records_file: str) -> List[Dict[str, Any]]:
    """
    Load health records from JSON file.
    
    Args:
        records_file: Path to health records JSON file
        
    Returns:
        List of health record dictionaries
        
    Raises:
        SystemExit: If file not found or cannot be parsed
        
    Example:
        >>> records = load_health_records('data/health_records/health_records.json')
        >>> print(f"Loaded {len(records)} health records")
    """
    logger.info(f"Loading health records from {records_file}")
    
    try:
        with open(records_file, 'r') as f:
            records = json.load(f)
        
        # Validate it's a list
        if not isinstance(records, list):
            logger.error(f"Health records file must contain a list, got {type(records)}")
            sys.exit(1)
            
        logger.info(f"✅ Loaded {len(records)} health records")
        return records
        
    except FileNotFoundError:
        logger.error(f"Health records file not found: {records_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing health records JSON: {e}")
        sys.exit(1)


def load_matched_pairs(matched_file: str) -> List[Dict[str, Any]]:
    """
    Load matched persona-record pairs from JSON file.
    
    Args:
        matched_file: Path to matched pairs JSON file
        
    Returns:
        List of matched pair dictionaries
        
    Raises:
        SystemExit: If file not found or cannot be parsed
        
    Example:
        >>> pairs = load_matched_pairs('data/matched/matched_personas.json')
        >>> print(f"Loaded {len(pairs)} matched pairs")
    """
    logger.info(f"Loading matched pairs from {matched_file}")
    
    try:
        with open(matched_file, 'r') as f:
            pairs = json.load(f)
        
        # Validate it's a list
        if not isinstance(pairs, list):
            logger.error(f"Matched pairs file must contain a list, got {type(pairs)}")
            sys.exit(1)
            
        logger.info(f"✅ Loaded {len(pairs)} matched pairs")
        return pairs
        
    except FileNotFoundError:
        logger.error(f"Matched pairs file not found: {matched_file}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Error parsing matched pairs JSON: {e}")
        sys.exit(1)


# Export public API
__all__ = [
    'load_config',
    'load_personas',
    'load_health_records',
    'load_matched_pairs',
]
