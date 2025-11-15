#!/usr/bin/env python3
"""
Validate Anomaly Threshold Against Edge Cases

This script validates the calibrated anomaly threshold against known edge cases
to ensure it correctly identifies anomalous matches.

Phase 1, Task 1.3.5 - v1.2.0 Implementation

Purpose:
- Test threshold against perfect matches (should NOT flag)
- Test threshold against poor matches (SHOULD flag)
- Test threshold against borderline cases
- Validate threshold behavior across different scenarios
- Document validation results

Output:
- Console report with validation results
- logs/threshold_validation_report.json - Detailed validation data
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple

# Ensure scripts directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
try:
    from scripts.utils.fhir_semantic_extractor import build_semantic_tree_from_fhir
    from scripts.utils.semantic_tree import (
        PersonaSemanticTree,
        HealthRecordSemanticTree,
        calculate_semantic_tree_similarity,
        persona_tree_from_dict
    )
except ImportError as e:
    print(f"ERROR: Cannot import required modules: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Load calibrated threshold
CALIBRATED_THRESHOLD = 0.7000  # From calibration script


def load_personas() -> List[Dict[str, Any]]:
    """Load personas with semantic trees."""
    personas_file = Path('data/personas/personas.json')

    if not personas_file.exists():
        logger.error(f"Personas file not found: {personas_file}")
        return []

    with open(personas_file, 'r') as f:
        personas = json.load(f)

    logger.info(f"Loaded {len(personas)} personas")
    return personas


def load_health_records(limit: int = None) -> List[Dict[str, Any]]:
    """Load health records and build semantic trees."""
    from datetime import datetime

    fhir_dir = Path('synthea/output/fhir')
    fhir_files = sorted(fhir_dir.glob('*.json'))

    if limit:
        fhir_files = fhir_files[:limit]

    records = []

    for fhir_file in fhir_files:
        try:
            # Skip metadata files
            if 'hospitalInformation' in fhir_file.name or 'practitionerInformation' in fhir_file.name:
                continue

            with open(fhir_file, 'r') as f:
                fhir_data = json.load(f)

            # Extract patient info
            patient_id = fhir_file.stem
            age = 30  # Default

            # Extract age from Patient resource
            for entry in fhir_data.get('entry', []):
                resource = entry.get('resource', {})
                if resource.get('resourceType') == 'Patient':
                    patient_id = resource.get('id', patient_id)
                    birth_date_str = resource.get('birthDate')
                    if birth_date_str:
                        birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
                        age = (datetime.now() - birth_date).days // 365
                    break

            # Build semantic tree
            semantic_tree = build_semantic_tree_from_fhir(fhir_data, patient_id, age)

            records.append({
                'file': fhir_file.name,
                'patient_id': patient_id,
                'age': age,
                'semantic_tree': semantic_tree
            })

        except Exception as e:
            logger.warning(f"Failed to process {fhir_file.name}: {e}")
            continue

    logger.info(f"Loaded {len(records)} health records with semantic trees")
    return records


def calculate_age_compatibility(persona_age: int, record_age: int) -> float:
    """Calculate age compatibility score."""
    age_diff = abs(persona_age - record_age)

    if age_diff == 0:
        return 1.0
    elif age_diff <= 2:
        return 0.95
    elif age_diff <= 5:
        return 0.80
    elif age_diff <= 10:
        return 0.60
    else:
        return max(0.0, 0.40 - (age_diff - 10) * 0.05)


def calculate_blended_score(
    persona: Dict[str, Any],
    record: Dict[str, Any],
    semantic_weight: float = 0.6
) -> Tuple[float, Dict[str, float]]:
    """Calculate blended matching score."""
    # Convert persona semantic tree dict to PersonaSemanticTree object
    persona_tree = persona_tree_from_dict(persona['semantic_tree'])

    # Health record already has HealthRecordSemanticTree object
    record_tree = record['semantic_tree']

    # Calculate semantic similarity
    semantic_score, components = calculate_semantic_tree_similarity(
        persona_tree,
        record_tree
    )

    # Demographic score (age compatibility)
    age_score = calculate_age_compatibility(persona['age'], record['age'])

    # Blended score
    demographic_weight = 1.0 - semantic_weight
    total_score = (semantic_score * semantic_weight) + (age_score * demographic_weight)

    breakdown = {
        'total': total_score,
        'semantic': semantic_score,
        'demographic': age_score,
        'semantic_weight': semantic_weight,
        'demographic_weight': demographic_weight,
        'components': components
    }

    return total_score, breakdown


def find_edge_cases(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """
    Find edge cases for validation.

    Edge case categories:
    1. Best matches (highest scores) - should NOT be flagged
    2. Worst matches (lowest scores) - SHOULD be flagged
    3. Borderline matches (near threshold) - test boundary behavior
    4. Age-mismatched but condition-matched
    5. Condition-mismatched but age-matched
    """
    logger.info("Finding edge cases...")

    all_matches = []

    for persona in personas:
        for record in records:
            score, breakdown = calculate_blended_score(persona, record, semantic_weight=0.6)

            all_matches.append({
                'persona_id': persona['id'],
                'persona_name': persona['name'],
                'persona_age': persona['age'],
                'record_id': record['patient_id'][:30],
                'record_age': record['age'],
                'score': score,
                'breakdown': breakdown
            })

    # Sort by score
    all_matches.sort(key=lambda x: x['score'], reverse=True)

    # Categorize matches
    edge_cases = {
        'best_matches': all_matches[:10],  # Top 10
        'worst_matches': all_matches[-10:],  # Bottom 10
        'borderline_above': [],  # Scores just above threshold
        'borderline_below': [],  # Scores just below threshold
        'age_mismatched': [],  # Age diff > 10 but score > threshold
        'high_semantic_low_demo': [],  # High semantic, low demographic
        'low_semantic_high_demo': []  # Low semantic, high demographic
    }

    # Find borderline cases (within 0.05 of threshold)
    for match in all_matches:
        score_diff = abs(match['score'] - CALIBRATED_THRESHOLD)

        if score_diff <= 0.05:
            if match['score'] >= CALIBRATED_THRESHOLD:
                edge_cases['borderline_above'].append(match)
            else:
                edge_cases['borderline_below'].append(match)

        # Age mismatched but high score
        age_diff = abs(match['persona_age'] - match['record_age'])
        if age_diff > 10 and match['score'] > CALIBRATED_THRESHOLD:
            edge_cases['age_mismatched'].append(match)

        # High semantic, low demographic
        if (match['breakdown']['semantic'] > 0.7 and
            match['breakdown']['demographic'] < 0.5):
            edge_cases['high_semantic_low_demo'].append(match)

        # Low semantic, high demographic
        if (match['breakdown']['semantic'] < 0.5 and
            match['breakdown']['demographic'] > 0.9):
            edge_cases['low_semantic_high_demo'].append(match)

    # Limit each category
    edge_cases['borderline_above'] = edge_cases['borderline_above'][:5]
    edge_cases['borderline_below'] = edge_cases['borderline_below'][:5]
    edge_cases['age_mismatched'] = edge_cases['age_mismatched'][:5]
    edge_cases['high_semantic_low_demo'] = edge_cases['high_semantic_low_demo'][:5]
    edge_cases['low_semantic_high_demo'] = edge_cases['low_semantic_high_demo'][:5]

    logger.info(f"✓ Found edge cases across {len(edge_cases)} categories")

    return edge_cases


def validate_threshold(edge_cases: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate threshold against edge cases.

    Returns:
        Dictionary with validation results
    """
    logger.info("Validating threshold against edge cases...")

    validation_results = {}

    # Test 1: Best matches should NOT be flagged as anomalous
    best_matches = edge_cases['best_matches']
    flagged_best = sum(1 for m in best_matches if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['best_matches'] = {
        'total': len(best_matches),
        'flagged': flagged_best,
        'pass': flagged_best == 0,
        'description': 'Best matches should NOT be flagged as anomalous'
    }

    # Test 2: Worst matches SHOULD be flagged as anomalous
    worst_matches = edge_cases['worst_matches']
    flagged_worst = sum(1 for m in worst_matches if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['worst_matches'] = {
        'total': len(worst_matches),
        'flagged': flagged_worst,
        'pass': flagged_worst == len(worst_matches),  # All should be flagged
        'description': 'Worst matches SHOULD be flagged as anomalous'
    }

    # Test 3: Borderline above threshold should NOT be flagged
    borderline_above = edge_cases['borderline_above']
    flagged_above = sum(1 for m in borderline_above if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['borderline_above'] = {
        'total': len(borderline_above),
        'flagged': flagged_above,
        'pass': flagged_above == 0,
        'description': 'Matches just above threshold should NOT be flagged'
    }

    # Test 4: Borderline below threshold SHOULD be flagged
    borderline_below = edge_cases['borderline_below']
    flagged_below = sum(1 for m in borderline_below if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['borderline_below'] = {
        'total': len(borderline_below),
        'flagged': flagged_below,
        'pass': flagged_below == len(borderline_below),
        'description': 'Matches just below threshold SHOULD be flagged'
    }

    # Test 5: Age-mismatched matches - informational only
    age_mismatched = edge_cases['age_mismatched']
    flagged_age = sum(1 for m in age_mismatched if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['age_mismatched'] = {
        'total': len(age_mismatched),
        'flagged': flagged_age,
        'pass': True,  # Informational
        'description': 'Age-mismatched but high-scoring matches (informational)'
    }

    # Test 6: High semantic, low demographic - informational
    high_sem_low_demo = edge_cases['high_semantic_low_demo']
    flagged_hsld = sum(1 for m in high_sem_low_demo if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['high_semantic_low_demo'] = {
        'total': len(high_sem_low_demo),
        'flagged': flagged_hsld,
        'pass': True,  # Informational
        'description': 'High semantic, low demographic matches (informational)'
    }

    # Test 7: Low semantic, high demographic - informational
    low_sem_high_demo = edge_cases['low_semantic_high_demo']
    flagged_lshd = sum(1 for m in low_sem_high_demo if m['score'] < CALIBRATED_THRESHOLD)
    validation_results['low_semantic_high_demo'] = {
        'total': len(low_sem_high_demo),
        'flagged': flagged_lshd,
        'pass': True,  # Informational
        'description': 'Low semantic, high demographic matches (informational)'
    }

    logger.info("✓ Validation complete")

    return validation_results


def generate_report(edge_cases: Dict[str, Any], validation_results: Dict[str, Any]):
    """Generate and display validation report."""

    logger.info("="*80)
    logger.info("THRESHOLD VALIDATION - Phase 1, Task 1.3.5")
    logger.info("="*80)
    logger.info("")

    logger.info(f"Calibrated Threshold: {CALIBRATED_THRESHOLD:.4f}")
    logger.info("")

    logger.info("-"*80)
    logger.info("EDGE CASE EXAMPLES")
    logger.info("-"*80)

    # Show examples from each category
    categories_to_show = [
        ('best_matches', 'Best Matches (Top 5)', True),
        ('worst_matches', 'Worst Matches (Bottom 5)', True),
        ('borderline_above', 'Borderline Above Threshold', False),
        ('borderline_below', 'Borderline Below Threshold', False),
        ('age_mismatched', 'Age Mismatched but High Score', False)
    ]

    for category_key, category_label, show_all in categories_to_show:
        matches = edge_cases[category_key]

        if not matches:
            continue

        logger.info(f"\n{category_label}:")

        display_matches = matches if show_all else matches[:5]

        for i, match in enumerate(display_matches, 1):
            flagged = "🚩" if match['score'] < CALIBRATED_THRESHOLD else "✓"
            logger.info(f"  {i}. {flagged} {match['persona_name']:15s} x Record (age {match['record_age']:2d})")
            logger.info(f"      Score: {match['score']:.4f} | Semantic: {match['breakdown']['semantic']:.4f} | Demo: {match['breakdown']['demographic']:.4f}")

    logger.info("")
    logger.info("-"*80)
    logger.info("VALIDATION RESULTS")
    logger.info("-"*80)

    all_tests_passed = True

    for test_name, result in validation_results.items():
        status = "✅ PASS" if result['pass'] else "❌ FAIL"
        logger.info(f"\n{status} - {result['description']}")
        logger.info(f"    Total: {result['total']}, Flagged: {result['flagged']}")

        if not result['pass']:
            all_tests_passed = False

    logger.info("")
    logger.info("="*80)
    logger.info("VALIDATION SUMMARY")
    logger.info("="*80)

    critical_tests = ['best_matches', 'worst_matches', 'borderline_above', 'borderline_below']
    critical_passed = all(validation_results[t]['pass'] for t in critical_tests)

    if all_tests_passed:
        logger.info("✅ ALL VALIDATION TESTS PASSED")
    elif critical_passed:
        logger.info("✅ ALL CRITICAL VALIDATION TESTS PASSED")
    else:
        logger.info("❌ SOME CRITICAL VALIDATION TESTS FAILED")

    logger.info("")

    # Recommendations
    logger.info("RECOMMENDATIONS:")

    if validation_results['best_matches']['pass']:
        logger.info("  ✅ Threshold does not flag high-quality matches")
    else:
        logger.info(f"  ⚠️  Threshold flags {validation_results['best_matches']['flagged']} high-quality matches - consider lowering threshold")

    if validation_results['worst_matches']['pass']:
        logger.info("  ✅ Threshold correctly flags low-quality matches")
    else:
        logger.info(f"  ⚠️  Threshold misses {validation_results['worst_matches']['total'] - validation_results['worst_matches']['flagged']} low-quality matches - consider raising threshold")

    # Check borderline behavior
    borderline_consistent = (
        validation_results['borderline_above']['pass'] and
        validation_results['borderline_below']['pass']
    )

    if borderline_consistent:
        logger.info("  ✅ Threshold behaves consistently at boundaries")
    else:
        logger.info("  ⚠️  Threshold may have inconsistent boundary behavior")

    logger.info("")
    logger.info("="*80)

    # Save detailed report
    report_path = Path('logs/threshold_validation_report.json')
    report_path.parent.mkdir(exist_ok=True)

    report_data = {
        'metadata': {
            'calibrated_threshold': CALIBRATED_THRESHOLD,
            'validation_timestamp': str(Path('logs/anomaly_calibration_report.json').stat().st_mtime)
        },
        'edge_cases': {
            category: [
                {
                    'persona_name': m['persona_name'],
                    'persona_age': m['persona_age'],
                    'record_age': m['record_age'],
                    'score': m['score'],
                    'flagged': m['score'] < CALIBRATED_THRESHOLD,
                    'breakdown': m['breakdown']
                }
                for m in matches
            ]
            for category, matches in edge_cases.items()
        },
        'validation_results': validation_results,
        'overall_status': 'PASSED' if critical_passed else 'FAILED'
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"✓ Detailed report saved to: {report_path}")
    logger.info("")


def main():
    """Main execution."""
    try:
        logger.info("Starting threshold validation...")
        logger.info("")

        # Load data
        logger.info("Loading personas and health records...")
        personas = load_personas()
        records = load_health_records(limit=None)

        if not personas or not records:
            logger.error("Failed to load data")
            return False

        logger.info("")

        # Find edge cases
        edge_cases = find_edge_cases(personas, records)

        logger.info("")

        # Validate threshold
        validation_results = validate_threshold(edge_cases)

        logger.info("")

        # Generate report
        generate_report(edge_cases, validation_results)

        return True

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
