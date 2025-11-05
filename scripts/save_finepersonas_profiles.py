#!/usr/bin/env python3
"""
Extract and save complete FinePersonas profiles for traceability.

This script:
1. Loads matched personas data
2. Extracts the complete FinePersonas profile for each persona
3. Saves individual profile files for easy reference
4. Creates an index file for quick lookup

Usage:
    python scripts/save_finepersonas_profiles.py
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/save_finepersonas_profiles.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def extract_and_save_profiles(
    matched_file: str = "data/matched/matched_personas.json",
    output_dir: str = "data/finepersonas_profiles"
):
    """
    Extract FinePersonas profiles from matched data and save individually.

    Args:
        matched_file: Path to matched personas file
        output_dir: Directory to save individual profile files
    """
    logger.info(f"Loading matched personas from {matched_file}")

    try:
        with open(matched_file, 'r') as f:
            matched_data = json.load(f)
        logger.info(f"Loaded {len(matched_data)} matched persona-record pairs")
    except FileNotFoundError:
        logger.error(f"Matched personas file not found: {matched_file}")
        logger.error("Please run the matching script first: python scripts/03_match_personas_records.py")
        sys.exit(1)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Extract and save profiles
    profiles_index = []
    saved_count = 0

    for matched_pair in matched_data:
        persona = matched_pair.get('persona', {})
        persona_id = persona.get('id')

        if persona_id is None:
            logger.warning(f"Skipping persona without ID")
            continue

        # Create complete profile
        profile = {
            'persona_id': persona_id,
            'source_dataset': 'HuggingFace FinePersonas-v0.1',
            'dataset_url': 'https://huggingface.co/datasets/argilla/FinePersonas-v0.1',
            'extracted_data': {
                'id': persona.get('id'),
                'age': persona.get('age'),
                'gender': persona.get('gender'),
                'description': persona.get('description', ''),
                'education': persona.get('education'),
                'occupation': persona.get('occupation'),
                'marital_status': persona.get('marital_status'),
                'income_level': persona.get('income_level')
            },
            'raw_finepersonas_data': persona.get('raw_data', {}),
            'notes': 'This is the complete FinePersonas profile for traceability purposes'
        }

        # Save individual profile file
        profile_filename = f"persona_{persona_id:05d}_profile.json"
        profile_filepath = output_path / profile_filename

        with open(profile_filepath, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

        saved_count += 1
        logger.debug(f"Saved profile {persona_id} to {profile_filename}")

        # Add to index
        profiles_index.append({
            'persona_id': persona_id,
            'age': persona.get('age'),
            'gender': persona.get('gender'),
            'occupation': persona.get('occupation'),
            'profile_file': profile_filename,
            'description_preview': persona.get('description', '')[:100]
        })

    # Save index file
    index_file = output_path / 'profiles_index.json'
    with open(index_file, 'w', encoding='utf-8') as f:
        json.dump({
            'total_profiles': len(profiles_index),
            'source_dataset': 'HuggingFace FinePersonas-v0.1',
            'dataset_url': 'https://huggingface.co/datasets/argilla/FinePersonas-v0.1',
            'profiles': profiles_index
        }, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Saved {saved_count} FinePersonas profiles to {output_dir}/")
    logger.info(f"✅ Created index file: {index_file}")

    # Print summary
    print()
    print("=" * 80)
    print("FINEPERSONAS PROFILES SAVED")
    print("=" * 80)
    print()
    print(f"📁 Location: {output_dir}/")
    print(f"📊 Total Profiles: {saved_count}")
    print(f"📋 Index File: profiles_index.json")
    print()
    print("Files created:")
    print(f"  • {saved_count} individual profile files: persona_XXXXX_profile.json")
    print(f"  • 1 index file: profiles_index.json")
    print()
    print("Each profile contains:")
    print("  • Persona ID and demographics")
    print("  • Complete FinePersonas raw data")
    print("  • Source dataset information")
    print("  • Traceability metadata")
    print()

    return saved_count


def main():
    """Main execution function."""
    logger.info("=" * 80)
    logger.info("FinePersonas Profile Extraction and Storage")
    logger.info("=" * 80)

    saved_count = extract_and_save_profiles()

    if saved_count > 0:
        print("✅ Profile extraction complete!")
        print()
        print("Next steps:")
        print("  1. Profiles are ready for traceability")
        print("  2. Each interview will reference these profile files")
        print("  3. Use profiles_index.json for quick lookups")
    else:
        logger.error("❌ No profiles were saved. Check the log for errors.")
        sys.exit(1)


if __name__ == "__main__":
    main()
