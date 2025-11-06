#!/usr/bin/env python3
"""
Enhanced diagnostic to see actual FinePersonas data structure.
"""

import json
from datasets import load_dataset

print("=" * 70)
print("DETAILED FINEPERSONAS INSPECTION")
print("=" * 70)

# Load first 50 records
dataset = load_dataset(
    'argilla/FinePersonas-v0.1',
    split='train[:50]',
    token=None
)

print(f"\n[1] Sample of PERSONA field (first 5 records):")
print("-" * 70)
for i in range(5):
    print(f"\n--- Record {i+1} ---")
    print(f"ID: {dataset[i]['id']}")
    print(f"PERSONA TEXT:")
    print(dataset[i]['persona'])
    print(f"\nLABELS: {dataset[i]['labels']}")

print("\n" + "=" * 70)
print("[2] Checking if LABELS contain demographic info:")
print("-" * 70)

# Check if labels have demographic data
labels_with_age = 0
labels_with_gender = 0
labels_with_female = 0

for i in range(len(dataset)):
    labels = dataset[i].get('labels', [])
    labels_str = ' '.join(str(label).lower() for label in labels)

    if any(word in labels_str for word in ['age', 'years', 'old']):
        labels_with_age += 1
    if any(word in labels_str for word in ['gender', 'male', 'female', 'sex']):
        labels_with_gender += 1
    if any(word in labels_str for word in ['female', 'woman']):
        labels_with_female += 1

print(f"\nIn {len(dataset)} records:")
print(f"  - Labels with age info: {labels_with_age}")
print(f"  - Labels with gender info: {labels_with_gender}")
print(f"  - Labels with female indicators: {labels_with_female}")

print("\n" + "=" * 70)
print("[3] Testing current extraction logic:")
print("-" * 70)

import re

def extract_age(text):
    patterns = [
        r'age[:\s]+(\d+)',
        r'(\d+)\s*years?\s*old',
        r'aged?\s+(\d+)',
        r'Age:\s*(\d+)',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            age = int(match.group(1))
            if 0 < age < 120:
                return age
    return None

def extract_gender(text):
    text_lower = text.lower()
    female_keywords = [
        'woman', 'female', 'she', 'her', 'mother', 'wife',
        'daughter', 'sister', 'lady', 'girl', 'ms.', 'mrs.'
    ]
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

# Test extraction on all 50 records
extracted_count = 0
female_in_range = 0

print("\nTesting extraction on 50 sample records:")
for i in range(len(dataset)):
    persona_text = dataset[i]['persona']
    age = extract_age(persona_text)
    gender = extract_gender(persona_text)

    if age and gender:
        extracted_count += 1
        if gender == 'female' and 12 <= age <= 60:
            female_in_range += 1

print(f"\nResults:")
print(f"  - Records with both age AND gender extracted: {extracted_count}/{len(dataset)} ({extracted_count/len(dataset)*100:.1f}%)")
print(f"  - Female, age 12-60: {female_in_range}/{len(dataset)} ({female_in_range/len(dataset)*100:.1f}%)")

print("\n" + "=" * 70)
print("[4] Projection for full dataset:")
print("-" * 70)

if female_in_range > 0:
    match_rate = female_in_range / len(dataset)
    print(f"\nMatch rate from sample: {match_rate*100:.2f}%")
    print(f"\nTo get 20,000 personas:")
    print(f"  - Need to process: ~{int(20000 / match_rate):,} records")
    print(f"  - At current rate (21 from 10.7M): This would take forever!")
    print(f"  - Expected records to process: ~{int(20000 / match_rate):,}")
else:
    print("\n⚠️  No matches found in sample!")
    print("The extraction logic needs to be fixed!")

print("\n" + "=" * 70)
print("RECOMMENDATIONS:")
print("-" * 70)
print("\n1. If match rate is < 1%: Dataset might not be suitable")
print("2. If match rate is 1-10%: Extraction logic is working")
print("3. Check if we can use 'labels' field for faster filtering")
print("4. Consider pre-filtering dataset before extraction")
print("\n" + "=" * 70)
