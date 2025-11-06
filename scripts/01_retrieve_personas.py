#!/usr/bin/env python3
"""
Retrieve female personas (age 12-60) from HuggingFace FinePersonas dataset.

This script:
1. Connects to the HuggingFace FinePersonas-v0.1 dataset
2. Filters for female personas in fertile age range (12-60 years)
3. Extracts relevant demographic and socioeconomic information
4. Saves personas to JSON file

Supports retrieving any count of personas for enhanced matching:
- Default: 10,000 personas
- Enhanced matching: 20,000-50,000 personas (for better match quality)
- Custom: Any count via --count parameter

Usage:
    python scripts/01_retrieve_personas.py [--count COUNT] [--output OUTPUT]

Examples:
    # Retrieve 10K personas (default)
    python scripts/01_retrieve_personas.py

    # Retrieve 20K personas for enhanced matching
    python scripts/01_retrieve_personas.py --count 20000

    # Retrieve 50K personas for maximum match quality
    python scripts/01_retrieve_personas.py --count 50000
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import re

try:
    from datasets import load_dataset
    import yaml
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)


# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/01_retrieve_personas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """Load configuration from YAML file."""
    try:
        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        logger.error(f"Config file not found: {config_path}")
        logger.info("Using default configuration")
        return {
            'huggingface': {
                'dataset': 'argilla/FinePersonas-v0.1',
                'cache_dir': './data/hf_cache'
            },
            'persona_settings': {
                'target_count': 10000,
                'age_range': {'min': 12, 'max': 60},
                'gender_filter': 'female'
            },
            'data_paths': {
                'personas': './data/personas'
            }
        }


def extract_age(persona_text: str) -> int | None:
    """
    Extract age from persona description.

    Looks for patterns like:
    - "Age: 28"
    - "28 years old"
    - "aged 28"
    """
    patterns = [
        r'age[:\s]+(\d+)',
        r'(\d+)\s*years?\s*old',
        r'aged?\s+(\d+)',
        r'Age:\s*(\d+)',
    ]

    for pattern in patterns:
        match = re.search(pattern, persona_text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if 0 < age < 120:  # Sanity check
                return age

    return None


def extract_gender(persona_text: str) -> str | None:
    """
    Extract gender from persona description.

    Returns: 'female', 'male', or None
    """
    text_lower = persona_text.lower()

    # Female indicators
    female_keywords = [
        'woman', 'female', 'she', 'her', 'mother', 'wife',
        'daughter', 'sister', 'lady', 'girl', 'ms.', 'mrs.'
    ]

    # Male indicators
    male_keywords = [
        'man', 'male', 'he', 'his', 'him', 'father', 'husband',
        'son', 'brother', 'gentleman', 'boy', 'mr.'
    ]

    female_count = sum(1 for kw in female_keywords if kw in text_lower)
    male_count = sum(1 for kw in male_keywords if kw in text_lower)

    if female_count > male_count:
        return 'female'
    elif male_count > female_count:
        return 'male'

    return None


def extract_socioeconomic_info(persona_text: str) -> Dict[str, str]:
    """
    Extract socioeconomic factors from persona description.

    Returns dictionary with:
    - education: education level
    - occupation: job/career
    - marital_status: marital status
    - income_level: estimated income bracket
    """
    text_lower = persona_text.lower()
    info = {}

    # Education keywords
    education_indicators = {
        'high_school': ['high school', 'secondary school', 'hs diploma'],
        'bachelors': ['bachelor', 'undergraduate', 'college degree', 'ba ', 'bs ', 'b.a.', 'b.s.'],
        'masters': ['master', 'graduate degree', 'mba', 'ma ', 'ms ', 'm.a.', 'm.s.'],
        'doctorate': ['phd', 'doctorate', 'doctoral', 'ph.d.', 'd.phil'],
        'no_degree': ['no degree', 'no formal education', 'dropped out']
    }

    for level, keywords in education_indicators.items():
        if any(kw in text_lower for kw in keywords):
            info['education'] = level
            break

    # Occupation - extract from common patterns
    occupation_match = re.search(r'(?:works as|employed as|job as|profession|career)\s+(?:a|an)?\s*([a-z\s]+)', text_lower)
    if occupation_match:
        info['occupation'] = occupation_match.group(1).strip()

    # Marital status
    if any(word in text_lower for word in ['married', 'wife', 'husband', 'spouse']):
        info['marital_status'] = 'married'
    elif any(word in text_lower for word in ['single', 'unmarried', 'never married']):
        info['marital_status'] = 'single'
    elif any(word in text_lower for word in ['divorced', 'separated']):
        info['marital_status'] = 'divorced'
    elif 'widowed' in text_lower:
        info['marital_status'] = 'widowed'

    # Income level (estimates based on occupation/education mentions)
    if any(word in text_lower for word in ['executive', 'director', 'ceo', 'wealthy', 'affluent']):
        info['income_level'] = 'high'
    elif any(word in text_lower for word in ['professional', 'manager', 'engineer', 'doctor', 'lawyer']):
        info['income_level'] = 'upper_middle'
    elif any(word in text_lower for word in ['teacher', 'nurse', 'office', 'clerk', 'middle class']):
        info['income_level'] = 'middle'
    elif any(word in text_lower for word in ['retail', 'service', 'working class', 'hourly']):
        info['income_level'] = 'lower_middle'
    elif any(word in text_lower for word in ['unemployed', 'low income', 'struggling']):
        info['income_level'] = 'low'

    return info


def parse_persona(raw_persona: Dict[str, Any]) -> Dict[str, Any] | None:
    """
    Parse raw persona from dataset into structured format.

    Returns None if persona doesn't meet criteria.
    """
    # Get persona text (field name may vary in dataset)
    persona_text = raw_persona.get('persona', '') or raw_persona.get('text', '') or str(raw_persona)

    # Extract basic info
    age = extract_age(persona_text)
    gender = extract_gender(persona_text)

    # Filter: must be female and in age range
    if gender != 'female':
        return None
    if age is None or age < 12 or age > 60:
        return None

    # Extract socioeconomic info
    socioeconomic = extract_socioeconomic_info(persona_text)

    # Build structured persona
    persona = {
        'id': raw_persona.get('id', None),
        'age': age,
        'gender': gender,
        'description': persona_text,
        'education': socioeconomic.get('education', 'unknown'),
        'occupation': socioeconomic.get('occupation', 'unknown'),
        'marital_status': socioeconomic.get('marital_status', 'unknown'),
        'income_level': socioeconomic.get('income_level', 'unknown'),
        'raw_data': raw_persona
    }

    return persona


def retrieve_personas(
    dataset_name: str,
    target_count: int,
    age_min: int,
    age_max: int,
    hf_token: str | None = None,
    cache_dir: str | None = None
) -> List[Dict[str, Any]]:
    """
    Retrieve and filter personas from HuggingFace dataset.

    Args:
        dataset_name: HuggingFace dataset identifier
        target_count: Number of personas to retrieve
        age_min: Minimum age
        age_max: Maximum age
        hf_token: HuggingFace API token (optional)
        cache_dir: Cache directory for dataset

    Returns:
        List of parsed personas
    """
    logger.info(f"Connecting to HuggingFace dataset: {dataset_name}")

    try:
        dataset = load_dataset(
            dataset_name,
            split='train',
            token=hf_token,
            cache_dir=cache_dir,
            trust_remote_code=True
        )
        logger.info(f"Dataset loaded: {len(dataset)} total records")
    except Exception as e:
        logger.error(f"Failed to load dataset: {e}")
        raise

    logger.info(f"Filtering personas (age {age_min}-{age_max}, female)...")

    filtered_personas = []
    processed_count = 0

    for raw_persona in dataset:
        processed_count += 1

        # Progress indicator
        if processed_count % 1000 == 0:
            logger.info(f"Processed {processed_count} records, found {len(filtered_personas)} matching personas")

        persona = parse_persona(raw_persona)

        if persona:
            filtered_personas.append(persona)

            # Stop when we have enough
            if len(filtered_personas) >= target_count:
                break

    logger.info(f"Found {len(filtered_personas)} matching personas from {processed_count} records")

    # If we don't have enough, warn user
    if len(filtered_personas) < target_count:
        logger.warning(f"Only found {len(filtered_personas)} personas, target was {target_count}")

    return filtered_personas[:target_count]


def save_personas(personas: List[Dict[str, Any]], output_path: str):
    """Save personas to JSON file."""
    output_file = Path(output_path) / "personas.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(personas, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved {len(personas)} personas to {output_file}")

    # Also save summary statistics
    summary_file = Path(output_path) / "personas_summary.json"
    summary = {
        'total_count': len(personas),
        'age_distribution': {},
        'education_distribution': {},
        'marital_status_distribution': {},
        'income_distribution': {}
    }

    # Calculate distributions
    for persona in personas:
        age_bracket = f"{(persona['age'] // 10) * 10}-{(persona['age'] // 10) * 10 + 9}"
        summary['age_distribution'][age_bracket] = summary['age_distribution'].get(age_bracket, 0) + 1
        summary['education_distribution'][persona['education']] = summary['education_distribution'].get(persona['education'], 0) + 1
        summary['marital_status_distribution'][persona['marital_status']] = summary['marital_status_distribution'].get(persona['marital_status'], 0) + 1
        summary['income_distribution'][persona['income_level']] = summary['income_distribution'].get(persona['income_level'], 0) + 1

    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Saved summary statistics to {summary_file}")


def main():
    parser = argparse.ArgumentParser(description='Retrieve personas from HuggingFace FinePersonas dataset')
    parser.add_argument('--count', type=int, default=10000, help='Number of personas to retrieve')
    parser.add_argument('--output', type=str, default='data/personas', help='Output directory')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')
    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    logger.info("=== Persona Retrieval Script Started ===")

    # Load configuration
    config = load_config(args.config)

    hf_config = config.get('huggingface', {})
    persona_config = config.get('persona_settings', {})

    dataset_name = hf_config.get('dataset', 'argilla/FinePersonas-v0.1')
    cache_dir = hf_config.get('cache_dir', './data/hf_cache')
    hf_token = hf_config.get('token')

    age_min = persona_config.get('age_range', {}).get('min', 12)
    age_max = persona_config.get('age_range', {}).get('max', 60)

    # Log pool size information
    if args.count >= 50000:
        logger.info(f"🎯 LARGE POOL MODE: Retrieving {args.count:,} personas")
        logger.info("This large pool will enable maximum match quality selection")
    elif args.count >= 20000:
        logger.info(f"🎯 ENHANCED POOL MODE: Retrieving {args.count:,} personas")
        logger.info("This enhanced pool will improve match quality")
    else:
        logger.info(f"Retrieving {args.count:,} personas")

    # Retrieve personas
    try:
        personas = retrieve_personas(
            dataset_name=dataset_name,
            target_count=args.count,
            age_min=age_min,
            age_max=age_max,
            hf_token=hf_token,
            cache_dir=cache_dir
        )

        # Save results
        save_personas(personas, args.output)

        logger.info(f"[SUCCESS] Retrieved {len(personas)} personas")
        logger.info("=== Persona Retrieval Script Completed ===")

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
