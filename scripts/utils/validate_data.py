#!/usr/bin/env python3
"""
Validate data files in the pipeline.

Checks:
- Personas: age range, required fields, data types
- Health records: pregnancy codes, FHIR structure
- Matched pairs: compatibility scores, consistency
- Interviews: completeness, transcript structure

Usage:
    python scripts/utils/validate_data.py --stage personas
    python scripts/utils/validate_data.py --stage all
"""

import json
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import sys


class ValidationResult:
    """Store validation results."""

    def __init__(self, stage: str):
        self.stage = stage
        self.errors = []
        self.warnings = []
        self.info = []
        self.passed = True

    def add_error(self, message: str):
        """Add an error (causes validation to fail)."""
        self.errors.append(message)
        self.passed = False

    def add_warning(self, message: str):
        """Add a warning (doesn't fail validation)."""
        self.warnings.append(message)

    def add_info(self, message: str):
        """Add informational message."""
        self.info.append(message)

    def print_summary(self):
        """Print validation summary."""
        print(f"\n{'='*60}")
        print(f"Validation Results: {self.stage}")
        print(f"{'='*60}")

        if self.info:
            print("\n[INFO]")
            for msg in self.info:
                print(f"  ✓ {msg}")

        if self.warnings:
            print("\n[WARNINGS]")
            for msg in self.warnings:
                print(f"  ⚠ {msg}")

        if self.errors:
            print("\n[ERRORS]")
            for msg in self.errors:
                print(f"  ✗ {msg}")

        print(f"\nStatus: {'PASSED ✓' if self.passed else 'FAILED ✗'}")
        print(f"{'='*60}\n")


def validate_personas(personas_file: str = "data/personas/personas.json") -> ValidationResult:
    """Validate personas data."""
    result = ValidationResult("Personas")

    # Check file exists
    if not Path(personas_file).exists():
        result.add_error(f"Personas file not found: {personas_file}")
        return result

    # Load data
    try:
        with open(personas_file, 'r') as f:
            personas = json.load(f)
    except Exception as e:
        result.add_error(f"Failed to load personas file: {e}")
        return result

    result.add_info(f"Loaded {len(personas)} personas")

    # Validate structure
    required_fields = ['age', 'gender', 'description']
    age_issues = 0
    gender_issues = 0
    missing_fields = 0

    for i, persona in enumerate(personas):
        # Check required fields
        for field in required_fields:
            if field not in persona:
                missing_fields += 1
                if missing_fields <= 5:  # Only show first 5
                    result.add_warning(f"Persona {i}: missing field '{field}'")

        # Check age range
        age = persona.get('age')
        if age is not None:
            if not (12 <= age <= 60):
                age_issues += 1
                if age_issues <= 5:
                    result.add_warning(f"Persona {i}: age {age} outside range 12-60")

        # Check gender
        gender = persona.get('gender')
        if gender and gender.lower() != 'female':
            gender_issues += 1
            if gender_issues <= 5:
                result.add_warning(f"Persona {i}: gender is '{gender}', expected 'female'")

    if missing_fields > 5:
        result.add_warning(f"... and {missing_fields - 5} more missing field issues")
    if age_issues > 5:
        result.add_warning(f"... and {age_issues - 5} more age range issues")
    if gender_issues > 5:
        result.add_warning(f"... and {gender_issues - 5} more gender issues")

    # Summary statistics
    ages = [p.get('age', 0) for p in personas if p.get('age')]
    if ages:
        result.add_info(f"Age range: {min(ages)}-{max(ages)}, average: {sum(ages)/len(ages):.1f}")

    education_dist = {}
    for p in personas:
        edu = p.get('education', 'unknown')
        education_dist[edu] = education_dist.get(edu, 0) + 1
    result.add_info(f"Education distribution: {dict(sorted(education_dist.items()))}")

    return result


def validate_health_records(records_file: str = "data/health_records/health_records.json") -> ValidationResult:
    """Validate health records data."""
    result = ValidationResult("Health Records")

    # Check file exists
    if not Path(records_file).exists():
        result.add_error(f"Health records file not found: {records_file}")
        return result

    # Load data
    try:
        with open(records_file, 'r') as f:
            records = json.load(f)
    except Exception as e:
        result.add_error(f"Failed to load health records file: {e}")
        return result

    result.add_info(f"Loaded {len(records)} health records")

    # Validate structure
    no_pregnancy = 0
    no_conditions = 0

    pregnancy_codes = ["77386006", "72892002", "249166004"]

    for i, record in enumerate(records):
        # Check for conditions
        conditions = record.get('conditions', [])
        if not conditions:
            no_conditions += 1
            continue

        # Check for pregnancy codes
        condition_codes = [c.get('code', '') for c in conditions]
        has_pregnancy = any(code in condition_codes for code in pregnancy_codes)

        if not has_pregnancy:
            no_pregnancy += 1
            if no_pregnancy <= 5:
                result.add_warning(f"Record {i}: no pregnancy-related SNOMED codes found")

    if no_conditions > 0:
        result.add_warning(f"{no_conditions} records have no conditions")

    if no_pregnancy > 5:
        result.add_warning(f"... and {no_pregnancy - 5} more records without pregnancy codes")

    # Statistics
    total_conditions = sum(len(r.get('conditions', [])) for r in records)
    result.add_info(f"Average conditions per record: {total_conditions/len(records):.1f}")

    total_encounters = sum(len(r.get('encounters', [])) for r in records)
    result.add_info(f"Average encounters per record: {total_encounters/len(records):.1f}")

    return result


def validate_matched_pairs(matched_file: str = "data/matched/matched_personas.json") -> ValidationResult:
    """Validate matched persona-record pairs."""
    result = ValidationResult("Matched Pairs")

    # Check file exists
    if not Path(matched_file).exists():
        result.add_error(f"Matched pairs file not found: {matched_file}")
        return result

    # Load data
    try:
        with open(matched_file, 'r') as f:
            matched = json.load(f)
    except Exception as e:
        result.add_error(f"Failed to load matched pairs file: {e}")
        return result

    result.add_info(f"Loaded {len(matched)} matched pairs")

    # Validate structure
    missing_persona = 0
    missing_record = 0
    age_mismatches = 0

    for i, pair in enumerate(matched):
        if 'persona' not in pair:
            missing_persona += 1
        if 'health_record' not in pair:
            missing_record += 1

        # Check compatibility score
        score = pair.get('compatibility_score')
        if score is None:
            result.add_warning(f"Pair {i}: missing compatibility score")
        elif score < 0.3:
            result.add_warning(f"Pair {i}: very low compatibility score ({score:.2f})")

        # Check age difference
        age_diff = pair.get('age_difference')
        if age_diff is not None and age_diff > 5:
            age_mismatches += 1
            if age_mismatches <= 5:
                result.add_warning(f"Pair {i}: large age difference ({age_diff} years)")

    if missing_persona > 0:
        result.add_error(f"{missing_persona} pairs missing persona data")
    if missing_record > 0:
        result.add_error(f"{missing_record} pairs missing health record data")
    if age_mismatches > 5:
        result.add_warning(f"... and {age_mismatches - 5} more pairs with large age differences")

    # Statistics
    scores = [p.get('compatibility_score', 0) for p in matched]
    if scores:
        result.add_info(f"Compatibility scores - min: {min(scores):.2f}, max: {max(scores):.2f}, avg: {sum(scores)/len(scores):.2f}")

    age_diffs = [p.get('age_difference', 0) for p in matched]
    if age_diffs:
        result.add_info(f"Age differences - min: {min(age_diffs)}, max: {max(age_diffs)}, avg: {sum(age_diffs)/len(age_diffs):.1f}")

    return result


def validate_interviews(interviews_dir: str = "data/interviews") -> ValidationResult:
    """Validate interview data."""
    result = ValidationResult("Interviews")

    # Check directory exists
    if not Path(interviews_dir).exists():
        result.add_error(f"Interviews directory not found: {interviews_dir}")
        return result

    # Load interview files
    import glob
    pattern = str(Path(interviews_dir) / "interview_*.json")
    interview_files = glob.glob(pattern)

    if not interview_files:
        result.add_warning(f"No interview files found in {interviews_dir}")
        return result

    result.add_info(f"Found {len(interview_files)} interview files")

    # Validate each interview
    short_interviews = 0
    missing_transcript = 0

    for i, filepath in enumerate(interview_files[:100]):  # Check first 100
        try:
            with open(filepath, 'r') as f:
                interview = json.load(f)

            # Check required fields
            if 'transcript' not in interview:
                missing_transcript += 1
                continue

            transcript = interview['transcript']

            # Check transcript length
            if len(transcript) < 5:
                short_interviews += 1
                if short_interviews <= 5:
                    result.add_warning(f"Interview {Path(filepath).name}: very short transcript ({len(transcript)} turns)")

        except Exception as e:
            result.add_warning(f"Failed to load {Path(filepath).name}: {e}")

    if missing_transcript > 0:
        result.add_error(f"{missing_transcript} interviews missing transcript")
    if short_interviews > 5:
        result.add_warning(f"... and {short_interviews - 5} more short interviews")

    return result


def main():
    parser = argparse.ArgumentParser(description='Validate pipeline data')
    parser.add_argument('--stage', type=str, default='all',
                       choices=['personas', 'health_records', 'matched', 'interviews', 'all'],
                       help='Which stage to validate')
    args = parser.parse_args()

    results = []

    if args.stage in ['personas', 'all']:
        results.append(validate_personas())

    if args.stage in ['health_records', 'all']:
        results.append(validate_health_records())

    if args.stage in ['matched', 'all']:
        results.append(validate_matched_pairs())

    if args.stage in ['interviews', 'all']:
        results.append(validate_interviews())

    # Print all results
    for result in results:
        result.print_summary()

    # Overall status
    all_passed = all(r.passed for r in results)
    print(f"Overall Status: {'ALL PASSED ✓' if all_passed else 'SOME FAILED ✗'}\n")

    sys.exit(0 if all_passed else 1)


if __name__ == '__main__':
    main()
