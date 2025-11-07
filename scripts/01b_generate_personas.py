#!/usr/bin/env python3
"""
Generate synthetic personas using AI models.

Since FinePersonas dataset doesn't contain individual personas with demographics,
we'll generate our own using Claude/GPT with controlled demographic parameters.

This script:
1. Generates 20,000 diverse female personas (age 12-60)
2. Ensures demographic distribution (age, education, income, marital status)
3. Creates rich, realistic persona descriptions
4. Saves in same format as original pipeline expected

Usage:
    python scripts/01b_generate_personas.py --count 20000
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any
import random
import os
from datetime import datetime as dt

# Load environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import yaml
    import anthropic
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install anthropic pyyaml python-dotenv")
    sys.exit(1)

# Import common loaders
from utils.common_loaders import load_config, get_api_key

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/01b_generate_personas.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class PersonaGenerator:
    """Generate realistic personas using Claude."""

    def __init__(self, config: Dict[str, Any]):
        """Initialize the persona generator."""
        # Load API key securely from environment variables only
        api_key = get_api_key('anthropic')
        self.client = anthropic.Anthropic(api_key=api_key)
        self.model = "claude-3-haiku-20240307"  # Fast and cheap for generation

    def generate_batch(self, count: int, batch_size: int = 100) -> str:
        """Generate a batch of personas."""
        prompt = f"""Generate {batch_size} diverse, realistic female personas for a pregnancy study. Each persona should be a woman aged 12-60 who could potentially be pregnant or considering pregnancy.

For each persona, provide:
1. Name and age
2. Brief background (occupation, education, location)
3. Marital/relationship status
4. Socioeconomic details (education level, income bracket)
5. Personality traits or relevant life circumstances

Format each persona as a short paragraph (3-4 sentences). Make them diverse in:
- Age (range 12-60, but focus on 18-45)
- Education (high school, bachelors, masters, doctorate, no degree)
- Income level (low, lower_middle, middle, upper_middle, high)
- Marital status (single, married, partnered, divorced, widowed)
- Occupation (vary widely)
- Location (different cities/regions)
- Life circumstances

Example format:
"Sarah is a 28-year-old elementary school teacher living in Boston. She has a bachelor's degree in education and works at a public school. She is married and lives in a middle-income household. Sarah is health-conscious and enjoys running and yoga in her free time."

Generate exactly {batch_size} personas, each as a separate paragraph. Number them 1-{batch_size}."""

        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                temperature=0.9,  # High temperature for diversity
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )
            return response.content[0].text
        except Exception as e:
            logger.error(f"Failed to generate personas: {e}")
            raise


def parse_generated_personas(text: str, start_id: int) -> List[Dict[str, Any]]:
    """Parse generated persona text into structured format."""
    personas = []

    # Split by numbered lines (1., 2., 3., etc.)
    import re
    lines = text.strip().split('\n')

    current_text = ""
    current_number = None

    for line in lines:
        # Check if line starts with a number
        match = re.match(r'^(\d+)\.\s+(.+)$', line.strip())
        if match:
            # Save previous persona if exists
            if current_text:
                persona = parse_single_persona(current_text, start_id + current_number - 1)
                if persona:
                    personas.append(persona)

            current_number = int(match.group(1))
            current_text = match.group(2)
        else:
            # Continuation of current persona
            current_text += " " + line.strip()

    # Don't forget last persona
    if current_text and current_number:
        persona = parse_single_persona(current_text, start_id + current_number - 1)
        if persona:
            personas.append(persona)

    return personas


def parse_single_persona(text: str, persona_id: int) -> Dict[str, Any] | None:
    """Parse a single persona text into structured format."""
    import re

    # Extract age
    age_match = re.search(r'(\d+)-year-old', text)
    if not age_match:
        age_match = re.search(r'age[:\s]+(\d+)', text, re.IGNORECASE)

    age = int(age_match.group(1)) if age_match else random.randint(18, 45)

    # Extract name (usually first word or two)
    name_match = re.search(r'^([A-Z][a-z]+)\s+(?:is|works|lives)', text)
    name = name_match.group(1) if name_match else f"Person{persona_id}"

    # Infer education
    text_lower = text.lower()
    if 'doctorate' in text_lower or 'phd' in text_lower or 'ph.d' in text_lower:
        education = 'doctorate'
    elif 'master' in text_lower or "master's" in text_lower:
        education = 'masters'
    elif 'bachelor' in text_lower or "bachelor's" in text_lower or 'college degree' in text_lower:
        education = 'bachelors'
    elif 'high school' in text_lower:
        education = 'high_school'
    elif 'no degree' in text_lower or 'dropped out' in text_lower:
        education = 'no_degree'
    else:
        education = 'unknown'

    # Infer income
    if any(word in text_lower for word in ['wealthy', 'affluent', 'high income', 'executive', 'luxury']):
        income_level = 'high'
    elif any(word in text_lower for word in ['upper-middle', 'upper middle', 'professional', 'well-paid']):
        income_level = 'upper_middle'
    elif any(word in text_lower for word in ['middle income', 'middle-income', 'moderate income', 'average income']):
        income_level = 'middle'
    elif any(word in text_lower for word in ['lower-middle', 'lower middle', 'working class', 'modest income']):
        income_level = 'lower_middle'
    elif any(word in text_lower for word in ['low income', 'low-income', 'struggling', 'paycheck to paycheck']):
        income_level = 'low'
    else:
        income_level = 'middle'  # Default

    # Infer marital status
    if 'married' in text_lower:
        marital_status = 'married'
    elif any(word in text_lower for word in ['single', 'unmarried', 'never married']):
        marital_status = 'single'
    elif any(word in text_lower for word in ['partner', 'partnered', 'domestic partnership', 'long-term relationship']):
        marital_status = 'partnered'
    elif any(word in text_lower for word in ['divorced', 'separated']):
        marital_status = 'divorced'
    elif 'widowed' in text_lower:
        marital_status = 'widowed'
    else:
        marital_status = 'unknown'

    # Extract occupation (look for common patterns)
    occupation_match = re.search(r'(?:works as|employed as|job as a|is a|occupation:|works at)\s+(?:a|an)?\s*([a-z\s]+?)(?:\.|,|at|in|and|with)', text_lower)
    occupation = occupation_match.group(1).strip() if occupation_match else 'unknown'

    return {
        'id': persona_id,
        'age': age,
        'gender': 'female',
        'description': text.strip(),
        'education': education,
        'occupation': occupation,
        'marital_status': marital_status,
        'income_level': income_level,
        'raw_data': {'generated': True, 'timestamp': dt.now().isoformat()}
    }


def generate_personas(target_count: int, batch_size: int = 100) -> List[Dict[str, Any]]:
    """Generate target number of personas."""
    logger.info(f"=== Generating {target_count} Synthetic Personas ===")

    # Load config
    config = load_config()

    # Initialize generator
    generator = PersonaGenerator(config)

    all_personas = []
    batches_needed = (target_count + batch_size - 1) // batch_size

    for batch_num in range(batches_needed):
        personas_needed = min(batch_size, target_count - len(all_personas))
        logger.info(f"[Batch {batch_num + 1}/{batches_needed}] Generating {personas_needed} personas...")

        try:
            # Generate batch
            generated_text = generator.generate_batch(personas_needed, batch_size)

            # Parse personas
            batch_personas = parse_generated_personas(generated_text, len(all_personas) + 1)

            # Filter for valid personas (age 12-60, female)
            valid_personas = [
                p for p in batch_personas
                if p['age'] >= 12 and p['age'] <= 60 and p['gender'] == 'female'
            ]

            all_personas.extend(valid_personas)
            logger.info(f"  ✅ Generated {len(valid_personas)} valid personas (total: {len(all_personas)})")

            if len(all_personas) >= target_count:
                break

        except Exception as e:
            logger.error(f"  ❌ Batch {batch_num + 1} failed: {e}")
            continue

    return all_personas[:target_count]


def save_personas(personas: List[Dict[str, Any]], output_path: str):
    """Save personas to JSON file."""
    output_file = Path(output_path) / "personas.json"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(personas, f, indent=2, ensure_ascii=False)

    logger.info(f"✅ Saved {len(personas)} personas to {output_file}")

    # Save summary statistics
    summary_file = Path(output_path) / "personas_summary.json"
    summary = {
        'total_count': len(personas),
        'generation_method': 'AI-generated (Claude)',
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

    logger.info(f"✅ Saved summary statistics to {summary_file}")


def main():
    parser = argparse.ArgumentParser(description='Generate synthetic personas using AI')
    parser.add_argument('--count', type=int, default=20000, help='Number of personas to generate')
    parser.add_argument('--output', type=str, default='data/personas', help='Output directory')
    parser.add_argument('--batch-size', type=int, default=100, help='Personas per API call')
    args = parser.parse_args()

    logger.info("=== Synthetic Persona Generation Started ===")
    logger.info(f"Target: {args.count} personas")
    logger.info(f"Batch size: {args.batch_size}")

    try:
        # Generate personas
        personas = generate_personas(args.count, args.batch_size)

        if len(personas) < args.count:
            logger.warning(f"Generated {len(personas)} personas, target was {args.count}")

        # Save results
        save_personas(personas, args.output)

        logger.info(f"[SUCCESS] Generated {len(personas)} personas")
        logger.info("=== Persona Generation Completed ===")

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
