#!/usr/bin/env python3
"""
Testing and Validation Framework for Semantic Tree Implementation

This module provides:
1. Validation functions for semantic tree completeness
2. Unit tests for semantic matching components
3. Integration tests for the full pipeline
4. Sample data generation for testing
5. Test reporting and analysis
"""

import json
import logging
from typing import Dict, List, Any, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


# ==================== VALIDATION FUNCTIONS ====================

def validate_persona_semantic_tree(persona: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that a persona has a complete semantic tree.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check if semantic_tree exists
    if not persona.get('semantic_tree'):
        issues.append("Missing semantic_tree field")
        return False, issues

    tree = persona['semantic_tree']

    # Check demographics
    demo = tree.get('demographics', {})
    if not demo:
        issues.append("Missing demographics branch")
    else:
        required_demo_fields = ['age', 'gender', 'location_type']
        for field in required_demo_fields:
            if field not in demo:
                issues.append(f"Missing demographics.{field}")

    # Check socioeconomic
    socio = tree.get('socioeconomic', {})
    if not socio:
        issues.append("Missing socioeconomic branch")
    else:
        required_socio_fields = ['education_level', 'income_bracket', 'employment_status', 'insurance_status']
        for field in required_socio_fields:
            if field not in socio:
                issues.append(f"Missing socioeconomic.{field}")

    # Check health_profile
    health = tree.get('health_profile', {})
    if not health:
        issues.append("Missing health_profile branch")
    else:
        required_health_fields = ['health_consciousness', 'healthcare_access', 'pregnancy_readiness']
        for field in required_health_fields:
            if field not in health:
                issues.append(f"Missing health_profile.{field}")

    # Check behavioral
    behavioral = tree.get('behavioral', {})
    if not behavioral:
        issues.append("Missing behavioral branch")
    else:
        required_behavioral_fields = ['physical_activity_level', 'smoking_status', 'alcohol_consumption']
        for field in required_behavioral_fields:
            if field not in behavioral:
                issues.append(f"Missing behavioral.{field}")

    # Check psychosocial
    psycho = tree.get('psychosocial', {})
    if not psycho:
        issues.append("Missing psychosocial branch")
    else:
        required_psycho_fields = ['mental_health_status', 'stress_level', 'social_support', 'marital_status']
        for field in required_psycho_fields:
            if field not in psycho:
                issues.append(f"Missing psychosocial.{field}")

    is_valid = len(issues) == 0
    return is_valid, issues


def validate_health_record_semantic_tree(record: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that a health record has a complete semantic tree.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    # Check if semantic_tree exists
    if not record.get('semantic_tree'):
        issues.append("Missing semantic_tree field")
        return False, issues

    tree = record['semantic_tree']

    # Check required top-level fields
    required_fields = [
        'patient_id', 'age', 'conditions', 'medications',
        'healthcare_utilization', 'pregnancy_profile', 'overall_health_status'
    ]

    for field in required_fields:
        if field not in tree:
            issues.append(f"Missing {field} field")

    # Validate medications profile
    meds = tree.get('medications', {})
    if meds:
        if 'pregnancy_safety' not in meds:
            issues.append("Missing medications.pregnancy_safety")
        if 'medication_count' not in meds:
            issues.append("Missing medications.medication_count")

    # Validate healthcare utilization
    util = tree.get('healthcare_utilization', {})
    if util:
        required_util = ['visit_frequency', 'primary_care_engagement', 'estimated_healthcare_access']
        for field in required_util:
            if field not in util:
                issues.append(f"Missing healthcare_utilization.{field}")

    # Validate pregnancy profile
    preg = tree.get('pregnancy_profile', {})
    if preg:
        required_preg = ['has_pregnancy_codes', 'risk_level']
        for field in required_preg:
            if field not in preg:
                issues.append(f"Missing pregnancy_profile.{field}")

    is_valid = len(issues) == 0
    return is_valid, issues


def validate_semantic_tree_ranges(persona: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate that semantic tree values are within acceptable ranges.

    Returns:
        Tuple of (is_valid, list_of_issues)
    """
    issues = []

    tree = persona.get('semantic_tree', {})
    if not tree:
        return True, []

    # Check 1-5 scale fields
    scale_1_5_fields = [
        ('health_profile.health_consciousness', ['health_profile', 'health_consciousness']),
        ('health_profile.healthcare_access', ['health_profile', 'healthcare_access']),
        ('health_profile.pregnancy_readiness', ['health_profile', 'pregnancy_readiness']),
        ('behavioral.physical_activity_level', ['behavioral', 'physical_activity_level']),
        ('behavioral.nutrition_awareness', ['behavioral', 'nutrition_awareness']),
        ('behavioral.sleep_quality', ['behavioral', 'sleep_quality']),
        ('psychosocial.mental_health_status', ['psychosocial', 'mental_health_status']),
        ('psychosocial.stress_level', ['psychosocial', 'stress_level']),
        ('psychosocial.social_support', ['psychosocial', 'social_support']),
        ('psychosocial.relationship_stability', ['psychosocial', 'relationship_stability']),
        ('psychosocial.financial_stress', ['psychosocial', 'financial_stress']),
    ]

    for field_name, path in scale_1_5_fields:
        value = tree
        for key in path:
            value = value.get(key, None)
            if value is None:
                break

        if value is not None:
            if not isinstance(value, int) or not (1 <= value <= 5):
                issues.append(f"{field_name} out of range [1-5]: {value}")

    # Check age range
    age = tree.get('demographics', {}).get('age')
    if age and (age < 12 or age > 60):
        issues.append(f"demographics.age out of range [12-60]: {age}")

    return len(issues) == 0, issues


# ==================== TESTING UTILITIES ====================

def test_persona_tree_generation(personas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Test persona semantic tree generation completeness.

    Returns:
        Dictionary with test results
    """
    results = {
        'total_personas': len(personas),
        'personas_with_trees': 0,
        'personas_without_trees': 0,
        'validation_passed': 0,
        'validation_failed': 0,
        'range_validation_passed': 0,
        'range_validation_failed': 0,
        'issues_found': []
    }

    for i, persona in enumerate(personas):
        # Check tree existence
        if persona.get('semantic_tree'):
            results['personas_with_trees'] += 1

            # Validate completeness
            is_valid, issues = validate_persona_semantic_tree(persona)
            if is_valid:
                results['validation_passed'] += 1
            else:
                results['validation_failed'] += 1
                results['issues_found'].append({
                    'persona_id': persona.get('id', i),
                    'issues': issues
                })

            # Validate ranges
            range_valid, range_issues = validate_semantic_tree_ranges(persona)
            if range_valid:
                results['range_validation_passed'] += 1
            else:
                results['range_validation_failed'] += 1
                results['issues_found'].append({
                    'persona_id': persona.get('id', i),
                    'range_issues': range_issues
                })
        else:
            results['personas_without_trees'] += 1

    return results


def test_health_record_tree_generation(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Test health record semantic tree generation completeness.

    Returns:
        Dictionary with test results
    """
    results = {
        'total_records': len(records),
        'records_with_trees': 0,
        'records_without_trees': 0,
        'validation_passed': 0,
        'validation_failed': 0,
        'issues_found': []
    }

    for i, record in enumerate(records):
        # Check tree existence
        if record.get('semantic_tree'):
            results['records_with_trees'] += 1

            # Validate completeness
            is_valid, issues = validate_health_record_semantic_tree(record)
            if is_valid:
                results['validation_passed'] += 1
            else:
                results['validation_failed'] += 1
                results['issues_found'].append({
                    'record_id': record.get('patient_id', i),
                    'issues': issues
                })
        else:
            results['records_without_trees'] += 1

    return results


def test_semantic_matching_scores(personas: List[Dict[str, Any]], records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Test semantic matching score calculation on sample pairs.

    Returns:
        Dictionary with test results
    """
    from utils.semantic_matcher import calculate_semantic_matching_score

    results = {
        'total_test_pairs': 0,
        'successful_calculations': 0,
        'failed_calculations': 0,
        'score_statistics': {
            'min': 1.0,
            'max': 0.0,
            'avg': 0.0,
            'samples': []
        }
    }

    # Test a sample of 10 pairs
    test_limit = min(len(personas), len(records), 10)
    scores = []

    for i in range(test_limit):
        persona = personas[i]
        record = records[i]

        if persona.get('semantic_tree') and record.get('semantic_tree'):
            try:
                score, breakdown = calculate_semantic_matching_score(
                    persona['semantic_tree'],
                    record['semantic_tree']
                )

                results['successful_calculations'] += 1
                scores.append(score)

                results['score_statistics']['samples'].append({
                    'persona_id': persona.get('id', i),
                    'record_id': record.get('patient_id', i),
                    'score': score,
                    'components': breakdown.get('component_scores', {})
                })

            except Exception as e:
                results['failed_calculations'] += 1
                logger.warning(f"Failed to calculate score for pair {i}: {e}")

        results['total_test_pairs'] += 1

    # Calculate statistics
    if scores:
        results['score_statistics']['min'] = min(scores)
        results['score_statistics']['max'] = max(scores)
        results['score_statistics']['avg'] = sum(scores) / len(scores)

    return results


# ==================== REPORT GENERATION ====================

def generate_validation_report(
    persona_results: Dict[str, Any],
    record_results: Dict[str, Any],
    matching_results: Dict[str, Any],
    output_file: str = 'data/validation_report.json'
) -> None:
    """
    Generate comprehensive validation report.
    """
    report = {
        'test_summary': {
            'personas': {
                'total': persona_results['total_personas'],
                'with_trees': persona_results['personas_with_trees'],
                'validation_passed': persona_results['validation_passed'],
                'validation_failed': persona_results['validation_failed'],
                'success_rate': (persona_results['validation_passed'] / max(1, persona_results['personas_with_trees'])) * 100 if persona_results['personas_with_trees'] > 0 else 0
            },
            'records': {
                'total': record_results['total_records'],
                'with_trees': record_results['records_with_trees'],
                'validation_passed': record_results['validation_passed'],
                'validation_failed': record_results['validation_failed'],
                'success_rate': (record_results['validation_passed'] / max(1, record_results['records_with_trees'])) * 100 if record_results['records_with_trees'] > 0 else 0
            },
            'matching': {
                'test_pairs': matching_results['total_test_pairs'],
                'successful': matching_results['successful_calculations'],
                'failed': matching_results['failed_calculations'],
                'success_rate': (matching_results['successful_calculations'] / max(1, matching_results['total_test_pairs'])) * 100 if matching_results['total_test_pairs'] > 0 else 0
            }
        },
        'detailed_results': {
            'personas': persona_results,
            'records': record_results,
            'matching': matching_results
        }
    }

    # Save report
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"Validation report saved to {output_file}")

    # Print summary
    logger.info("=" * 60)
    logger.info("VALIDATION TEST SUMMARY")
    logger.info("=" * 60)
    logger.info(f"Personas: {persona_results['personas_with_trees']}/{persona_results['total_personas']} with semantic trees")
    logger.info(f"  Validation: {persona_results['validation_passed']}/{persona_results['personas_with_trees']} passed "
                f"({report['test_summary']['personas']['success_rate']:.1f}%)")
    logger.info(f"\nRecords: {record_results['records_with_trees']}/{record_results['total_records']} with semantic trees")
    logger.info(f"  Validation: {record_results['validation_passed']}/{record_results['records_with_trees']} passed "
                f"({report['test_summary']['records']['success_rate']:.1f}%)")
    logger.info(f"\nMatching Tests: {matching_results['successful_calculations']}/{matching_results['total_test_pairs']} successful "
                f"({report['test_summary']['matching']['success_rate']:.1f}%)")

    if matching_results['score_statistics']['samples']:
        logger.info(f"  Semantic Scores: min={matching_results['score_statistics']['min']:.3f}, "
                    f"max={matching_results['score_statistics']['max']:.3f}, "
                    f"avg={matching_results['score_statistics']['avg']:.3f}")

    logger.info("=" * 60)

    return report


# ==================== DATA QUALITY CHECKS ====================

def check_demographic_diversity(personas: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check demographic diversity in persona pool.
    """
    analysis = {
        'age_distribution': {},
        'education_distribution': {},
        'income_distribution': {},
        'employment_status_distribution': {},
        'health_consciousness_distribution': {},
        'healthcare_access_distribution': {},
        'pregnancy_readiness_distribution': {}
    }

    for persona in personas:
        # Demographic
        age = persona.get('age')
        if age:
            age_bracket = f"{(age // 10) * 10}-{(age // 10) * 10 + 9}"
            analysis['age_distribution'][age_bracket] = analysis['age_distribution'].get(age_bracket, 0) + 1

        education = persona.get('education')
        if education:
            analysis['education_distribution'][education] = analysis['education_distribution'].get(education, 0) + 1

        income = persona.get('income_level')
        if income:
            analysis['income_distribution'][income] = analysis['income_distribution'].get(income, 0) + 1

        # Semantic tree data
        tree = persona.get('semantic_tree', {})
        if tree:
            employment = tree.get('socioeconomic', {}).get('employment_status')
            if employment:
                analysis['employment_status_distribution'][employment] = \
                    analysis['employment_status_distribution'].get(employment, 0) + 1

            health_consciousness = tree.get('health_profile', {}).get('health_consciousness')
            if health_consciousness:
                analysis['health_consciousness_distribution'][health_consciousness] = \
                    analysis['health_consciousness_distribution'].get(health_consciousness, 0) + 1

            healthcare_access = tree.get('health_profile', {}).get('healthcare_access')
            if healthcare_access:
                analysis['healthcare_access_distribution'][healthcare_access] = \
                    analysis['healthcare_access_distribution'].get(healthcare_access, 0) + 1

            pregnancy_readiness = tree.get('health_profile', {}).get('pregnancy_readiness')
            if pregnancy_readiness:
                analysis['pregnancy_readiness_distribution'][pregnancy_readiness] = \
                    analysis['pregnancy_readiness_distribution'].get(pregnancy_readiness, 0) + 1

    return analysis


def check_clinical_data_quality(records: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Check clinical data quality in health record pool.
    """
    analysis = {
        'total_records': len(records),
        'with_conditions': 0,
        'with_medications': 0,
        'with_encounters': 0,
        'health_status_distribution': {},
        'pregnancy_risk_distribution': {},
        'comorbidity_statistics': {
            'min': 1.0,
            'max': 0.0,
            'avg': 0.0
        }
    }

    comorbidity_scores = []

    for record in records:
        # Basic data
        if record.get('conditions'):
            analysis['with_conditions'] += 1

        if record.get('medications'):
            analysis['with_medications'] += 1

        if record.get('encounters'):
            analysis['with_encounters'] += 1

        # Semantic tree data
        tree = record.get('semantic_tree', {})
        if tree:
            health_status = tree.get('overall_health_status')
            if health_status:
                analysis['health_status_distribution'][health_status] = \
                    analysis['health_status_distribution'].get(health_status, 0) + 1

            pregnancy_risk = tree.get('pregnancy_profile', {}).get('risk_level')
            if pregnancy_risk:
                analysis['pregnancy_risk_distribution'][pregnancy_risk] = \
                    analysis['pregnancy_risk_distribution'].get(pregnancy_risk, 0) + 1

            comorbidity = tree.get('comorbidity_index', 0.0)
            comorbidity_scores.append(comorbidity)

    # Calculate comorbidity statistics
    if comorbidity_scores:
        analysis['comorbidity_statistics']['min'] = min(comorbidity_scores)
        analysis['comorbidity_statistics']['max'] = max(comorbidity_scores)
        analysis['comorbidity_statistics']['avg'] = sum(comorbidity_scores) / len(comorbidity_scores)

    return analysis
