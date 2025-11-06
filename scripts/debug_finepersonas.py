#!/usr/bin/env python3
"""
Debug script to inspect FinePersonas dataset structure.

This script loads a small sample of the dataset and shows:
- Actual field names
- Sample data structure
- How many records have the fields we need
"""

import json
import sys
from datasets import load_dataset

print("=" * 60)
print("FINEPERSONAS DATASET DIAGNOSTIC")
print("=" * 60)

print("\n[1/4] Loading sample from FinePersonas dataset...")
try:
    # Load just first 100 records to inspect
    dataset = load_dataset(
        'argilla/FinePersonas-v0.1',
        split='train[:100]',  # Just first 100 records
        token=None
    )
    print(f"✅ Loaded {len(dataset)} sample records")
except Exception as e:
    print(f"❌ Failed to load dataset: {e}")
    sys.exit(1)

print("\n[2/4] Inspecting dataset structure...")
print(f"\nDataset features (columns):")
for feature_name, feature_type in dataset.features.items():
    print(f"  - {feature_name}: {feature_type}")

print("\n[3/4] Examining first 3 records...")
for i in range(min(3, len(dataset))):
    print(f"\n--- Record {i+1} ---")
    record = dataset[i]
    print(json.dumps(record, indent=2, default=str))

print("\n[4/4] Checking field availability...")

# Check what fields actually exist
sample = dataset[0]
available_fields = list(sample.keys())
print(f"\nAvailable fields in records: {available_fields}")

# Check for persona/text fields
text_fields = [f for f in available_fields if 'persona' in f.lower() or 'text' in f.lower() or 'description' in f.lower()]
print(f"\nText-like fields: {text_fields}")

# Check for demographic fields
demo_fields = [f for f in available_fields if any(kw in f.lower() for kw in ['age', 'gender', 'sex', 'female', 'male'])]
print(f"Demographic fields: {demo_fields}")

# Sample the first few records to see patterns
print("\n[5/5] Analyzing first 10 records for patterns...")
age_found = 0
gender_found = 0
female_found = 0

for i in range(min(10, len(dataset))):
    record = dataset[i]
    record_str = str(record).lower()

    # Check for age patterns
    if any(word in record_str for word in ['age', 'years old', 'year-old']):
        age_found += 1

    # Check for gender patterns
    if any(word in record_str for word in ['gender', 'male', 'female', 'woman', 'man']):
        gender_found += 1

    # Check for female indicators
    if any(word in record_str for word in ['female', 'woman', 'she', 'her', 'mother', 'wife']):
        female_found += 1

print(f"\nIn first 10 records:")
print(f"  - Records mentioning age: {age_found}/10")
print(f"  - Records mentioning gender: {gender_found}/10")
print(f"  - Records with female indicators: {female_found}/10")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)
print("\nNext steps:")
print("1. Review the field names above")
print("2. Check the sample records structure")
print("3. Update parsing logic to match actual structure")
