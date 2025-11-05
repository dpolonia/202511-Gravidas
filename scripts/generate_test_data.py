#!/usr/bin/env python3
"""
Generate sample matched personas for testing the interview system.

This creates a small dataset of 10 synthetic matched persona-record pairs
so you can test the interview system without running the full pipeline.

Usage:
    python scripts/generate_test_data.py
"""

import json
from pathlib import Path
import random

# Sample personas
SAMPLE_PERSONAS = [
    {
        "id": 1,
        "age": 28,
        "gender": "female",
        "description": "Emma is a 28-year-old elementary school teacher living in Boston. She is married and expecting her first child.",
        "education": "bachelors",
        "occupation": "teacher",
        "marital_status": "married",
        "income_level": "middle"
    },
    {
        "id": 2,
        "age": 32,
        "gender": "female",
        "description": "Maria is a 32-year-old software engineer in San Francisco. She has a master's degree and is pregnant with her second child.",
        "education": "masters",
        "occupation": "software engineer",
        "marital_status": "married",
        "income_level": "upper_middle"
    },
    {
        "id": 3,
        "age": 25,
        "gender": "female",
        "description": "Aisha is a 25-year-old nurse in Chicago. She is single and expecting her first child.",
        "education": "bachelors",
        "occupation": "nurse",
        "marital_status": "single",
        "income_level": "middle"
    },
    {
        "id": 4,
        "age": 35,
        "gender": "female",
        "description": "Jennifer is a 35-year-old accountant in Dallas. She is married with one child and is currently pregnant with her second.",
        "education": "bachelors",
        "occupation": "accountant",
        "marital_status": "married",
        "income_level": "upper_middle"
    },
    {
        "id": 5,
        "age": 29,
        "gender": "female",
        "description": "Sophia is a 29-year-old retail manager in Seattle. She has a high school diploma and is expecting twins.",
        "education": "high_school",
        "occupation": "retail manager",
        "marital_status": "married",
        "income_level": "middle"
    },
    {
        "id": 6,
        "age": 31,
        "gender": "female",
        "description": "Lisa is a 31-year-old graphic designer in Portland. She is married and this is her first pregnancy.",
        "education": "bachelors",
        "occupation": "graphic designer",
        "marital_status": "married",
        "income_level": "middle"
    },
    {
        "id": 7,
        "age": 27,
        "gender": "female",
        "description": "Rachel is a 27-year-old paralegal in Miami. She has an associate's degree and is expecting her first child.",
        "education": "high_school",
        "occupation": "paralegal",
        "marital_status": "single",
        "income_level": "lower_middle"
    },
    {
        "id": 8,
        "age": 33,
        "gender": "female",
        "description": "Amanda is a 33-year-old doctor in New York. She is married and pregnant with her first child.",
        "education": "doctorate",
        "occupation": "physician",
        "marital_status": "married",
        "income_level": "high"
    },
    {
        "id": 9,
        "age": 26,
        "gender": "female",
        "description": "Jessica is a 26-year-old customer service representative in Phoenix. She has a high school education and is expecting her second child.",
        "education": "high_school",
        "occupation": "customer service",
        "marital_status": "married",
        "income_level": "lower_middle"
    },
    {
        "id": 10,
        "age": 30,
        "gender": "female",
        "description": "Sarah is a 30-year-old marketing manager in Atlanta. She has a bachelor's degree and is pregnant with her first child.",
        "education": "bachelors",
        "occupation": "marketing manager",
        "marital_status": "married",
        "income_level": "upper_middle"
    }
]

def generate_health_record(persona):
    """Generate a simplified health record for a persona."""

    # Pregnancy-related conditions based on age and other factors
    conditions = [
        {
            "code": "77386006",
            "display": "Pregnancy",
            "onset": "2024-01-15"
        },
        {
            "code": "72892002",
            "display": "Normal pregnancy",
            "onset": "2024-01-15"
        }
    ]

    # Add occasional complications
    if persona['age'] > 35 or random.random() < 0.2:
        conditions.append({
            "code": "48194001",
            "display": "Pregnancy-induced hypertension",
            "onset": "2024-05-20"
        })

    if persona['age'] > 30 and random.random() < 0.15:
        conditions.append({
            "code": "15938005",
            "display": "Gestational diabetes mellitus",
            "onset": "2024-06-10"
        })

    # Prenatal visits
    encounters = []
    for month in range(1, 8):
        encounters.append({
            "type": "Prenatal visit",
            "period_start": f"2024-0{month}-01",
            "period_end": f"2024-0{month}-01"
        })

    # Observations
    observations = [
        {
            "code": "57036006",
            "display": "Fetal heart rate",
            "value": random.randint(120, 160),
            "unit": "beats/min",
            "date": "2024-07-15"
        },
        {
            "code": "271442007",
            "display": "Duration of pregnancy",
            "value": random.randint(28, 36),
            "unit": "weeks",
            "date": "2024-08-01"
        }
    ]

    # Medications
    medications = [
        {
            "code": "6068007",
            "display": "Prenatal vitamin",
            "authored": "2024-01-20"
        }
    ]

    if "diabetes" in str(conditions):
        medications.append({
            "code": "325072002",
            "display": "Insulin",
            "authored": "2024-06-15"
        })

    return {
        "source_file": f"patient_{persona['id']}.json",
        "patient_id": f"patient-{persona['id']}",
        "age": persona['age'],
        "conditions": conditions,
        "procedures": [],
        "observations": observations,
        "medications": medications,
        "encounters": encounters,
        "raw_fhir": {}
    }

def main():
    print("Generating test data for interview system...")
    print()

    # Create directories
    Path("data/matched").mkdir(parents=True, exist_ok=True)
    Path("data/personas").mkdir(parents=True, exist_ok=True)
    Path("data/health_records").mkdir(parents=True, exist_ok=True)

    # Generate matched pairs
    matched_pairs = []

    for persona in SAMPLE_PERSONAS:
        health_record = generate_health_record(persona)

        matched_pair = {
            "persona": persona,
            "health_record": health_record,
            "compatibility_score": random.uniform(0.85, 0.95),
            "age_difference": 0
        }

        matched_pairs.append(matched_pair)

    # Save matched pairs
    output_file = "data/matched/matched_personas.json"
    with open(output_file, 'w') as f:
        json.dump(matched_pairs, f, indent=2)

    print(f"✓ Created {len(matched_pairs)} matched persona-record pairs")
    print(f"✓ Saved to: {output_file}")
    print()
    print("You can now run interviews!")
    print()
    print("Try:")
    print("  python scripts/interactive_interviews.py")
    print()
    print("Or:")
    print("  python scripts/04_conduct_interviews.py \\")
    print("    --provider anthropic \\")
    print("    --model claude-4.5-sonnet \\")
    print("    --count 5")
    print()

if __name__ == '__main__':
    main()
