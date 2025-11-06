#!/usr/bin/env python3
"""
Validate pipeline data files before running the main pipeline.

This script validates personas, health records, matched pairs, and configuration
to catch errors early and ensure data quality.

Usage:
    python scripts/validate_pipeline_data.py --all
    python scripts/validate_pipeline_data.py --config
    python scripts/validate_pipeline_data.py --personas data/personas/personas.json
    python scripts/validate_pipeline_data.py --records data/health_records/health_records.json
    python scripts/validate_pipeline_data.py --matched data/matched/matched_personas.json
"""

import argparse
import sys
import logging
from pathlib import Path
from typing import Dict, Any, List

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.utils.common_loaders import load_config, load_personas, load_health_records, load_matched_pairs
from scripts.utils.validators import (
    validate_config,
    validate_persona,
    validate_health_record,
    validate_matched_pair
)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def print_separator(char='=', length=60):
    """Print a separator line."""
    print(char * length)


def print_header(title: str):
    """Print a formatted header."""
    print_separator()
    print(f"  {title}")
    print_separator()


def validate_config_file(config_path: str) -> bool:
    """Validate configuration file."""
    print_header("Validating Configuration")

    try:
        config = load_config(config_path, validate=False, raise_on_error=True)

        if not config:
            logger.error(f"❌ Config file is empty or invalid: {config_path}")
            return False

        # Validate config
        is_valid, warnings = validate_config(config)

        print(f"📄 Config file: {config_path}")
        print(f"📊 Sections: {', '.join(config.keys())}")

        if warnings:
            print(f"\n⚠️  Validation Warnings ({len(warnings)}):")
            for warning in warnings:
                print(f"   - {warning}")

        if is_valid:
            print(f"\n✅ Configuration is valid")
        else:
            print(f"\n❌ Configuration has errors")

        return is_valid

    except Exception as e:
        logger.error(f"❌ Error validating config: {e}")
        return False


def validate_personas_file(personas_path: str) -> bool:
    """Validate personas file."""
    print_header("Validating Personas")

    try:
        personas = load_personas(personas_path, validate=False, raise_on_error=True)

        print(f"📄 Personas file: {personas_path}")
        print(f"📊 Total personas: {len(personas)}")

        # Validate each persona
        errors = []
        warnings_count = 0

        for i, persona in enumerate(personas):
            is_valid, warnings = validate_persona(persona, strict=False)

            if warnings:
                warnings_count += len(warnings)
                if len(errors) < 5:  # Show first 5 errors
                    persona_id = persona.get('id', f'index_{i}')
                    errors.append(f"Persona {persona_id}: {'; '.join(warnings[:2])}")

        if errors:
            print(f"\n⚠️  Validation Issues Found ({warnings_count} total):")
            for error in errors:
                print(f"   - {error}")
            if warnings_count > 5:
                print(f"   ... and {warnings_count - len(errors)} more issues")

        if warnings_count == 0:
            print(f"\n✅ All personas are valid")
            return True
        else:
            print(f"\n⚠️  {warnings_count} validation warnings found")
            return True  # Warnings don't fail validation

    except Exception as e:
        logger.error(f"❌ Error validating personas: {e}")
        return False


def validate_health_records_file(records_path: str) -> bool:
    """Validate health records file."""
    print_header("Validating Health Records")

    try:
        records = load_health_records(records_path, validate=False, raise_on_error=True)

        print(f"📄 Health records file: {records_path}")
        print(f"📊 Total records: {len(records)}")

        # Validate each record
        errors = []
        warnings_count = 0

        for i, record in enumerate(records):
            is_valid, warnings = validate_health_record(record, strict=False)

            if warnings:
                warnings_count += len(warnings)
                if len(errors) < 5:  # Show first 5 errors
                    record_id = record.get('id', f'index_{i}')
                    errors.append(f"Record {record_id}: {'; '.join(warnings[:2])}")

        if errors:
            print(f"\n⚠️  Validation Issues Found ({warnings_count} total):")
            for error in errors:
                print(f"   - {error}")
            if warnings_count > 5:
                print(f"   ... and {warnings_count - len(errors)} more issues")

        if warnings_count == 0:
            print(f"\n✅ All health records are valid")
            return True
        else:
            print(f"\n⚠️  {warnings_count} validation warnings found")
            return True  # Warnings don't fail validation

    except Exception as e:
        logger.error(f"❌ Error validating health records: {e}")
        return False


def validate_matched_pairs_file(matched_path: str) -> bool:
    """Validate matched pairs file."""
    print_header("Validating Matched Pairs")

    try:
        pairs = load_matched_pairs(matched_path, validate=False, raise_on_error=True)

        print(f"📄 Matched pairs file: {matched_path}")
        print(f"📊 Total pairs: {len(pairs)}")

        # Validate each pair
        errors = []
        warnings_count = 0

        for i, pair in enumerate(pairs):
            is_valid, warnings = validate_matched_pair(pair, strict=False)

            if warnings:
                warnings_count += len(warnings)
                if len(errors) < 5:  # Show first 5 errors
                    persona_id = 'unknown'
                    if isinstance(pair.get('persona'), dict):
                        persona_id = pair['persona'].get('id', 'unknown')
                    errors.append(f"Pair {i} (persona {persona_id}): {'; '.join(warnings[:2])}")

        if errors:
            print(f"\n⚠️  Validation Issues Found ({warnings_count} total):")
            for error in errors:
                print(f"   - {error}")
            if warnings_count > 5:
                print(f"   ... and {warnings_count - len(errors)} more issues")

        if warnings_count == 0:
            print(f"\n✅ All matched pairs are valid")
            return True
        else:
            print(f"\n⚠️  {warnings_count} validation warnings found")
            return True  # Warnings don't fail validation

    except Exception as e:
        logger.error(f"❌ Error validating matched pairs: {e}")
        return False


def main():
    """Main validation function."""
    parser = argparse.ArgumentParser(
        description="Validate pipeline data files",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument('--config', type=str,
                       help='Path to config file (default: config/config.yaml)')
    parser.add_argument('--personas', type=str,
                       help='Path to personas JSON file')
    parser.add_argument('--records', type=str,
                       help='Path to health records JSON file')
    parser.add_argument('--matched', type=str,
                       help='Path to matched pairs JSON file')
    parser.add_argument('--all', action='store_true',
                       help='Validate all data files with default paths')

    args = parser.parse_args()

    # If no arguments, show help
    if not any([args.config, args.personas, args.records, args.matched, args.all]):
        parser.print_help()
        sys.exit(1)

    all_valid = True

    # Validate config
    if args.config or args.all:
        config_path = args.config or "config/config.yaml"
        if Path(config_path).exists():
            valid = validate_config_file(config_path)
            all_valid = all_valid and valid
            print()
        else:
            logger.warning(f"Config file not found: {config_path}")

    # Validate personas
    if args.personas or args.all:
        personas_path = args.personas or "data/personas/personas.json"
        if Path(personas_path).exists():
            valid = validate_personas_file(personas_path)
            all_valid = all_valid and valid
            print()
        else:
            logger.warning(f"Personas file not found: {personas_path}")

    # Validate health records
    if args.records or args.all:
        records_path = args.records or "data/health_records/health_records.json"
        if Path(records_path).exists():
            valid = validate_health_records_file(records_path)
            all_valid = all_valid and valid
            print()
        else:
            logger.warning(f"Health records file not found: {records_path}")

    # Validate matched pairs
    if args.matched or args.all:
        matched_path = args.matched or "data/matched/matched_personas.json"
        if Path(matched_path).exists():
            valid = validate_matched_pairs_file(matched_path)
            all_valid = all_valid and valid
            print()
        else:
            logger.warning(f"Matched pairs file not found: {matched_path}")

    # Final summary
    print_separator()
    if all_valid:
        print("✅ All validations passed")
        sys.exit(0)
    else:
        print("❌ Some validations failed")
        sys.exit(1)


if __name__ == '__main__':
    main()
