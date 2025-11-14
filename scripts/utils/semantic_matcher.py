#!/usr/bin/env python3
"""
Semantic Tree Matching and Similarity Calculation

This module provides advanced matching between persona and health record semantic trees.

Features:
- Component-wise semantic similarity scoring
- Weighted hierarchical tree matching
- Semantic alignment reporting
- Explainable matching decisions
"""

import logging
from typing import Dict, List, Any, Tuple, Optional
import numpy as np

from utils.semantic_tree import (
    PersonaSemanticTree,
    HealthRecordSemanticTree,
    calculate_semantic_tree_similarity
)

logger = logging.getLogger(__name__)


# ==================== DETAILED COMPONENT SCORING ====================

def score_demographics_alignment(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Tuple[float, Dict[str, Any]]:
    """
    Score demographic alignment between persona and record.

    Returns:
        Tuple of (score, breakdown)
    """
    breakdown = {}

    # Age alignment (most important for pregnancy)
    persona_age = persona_tree.get('demographics', {}).get('age', 0)
    record_age = record_tree.get('age', 0)

    if persona_age == 0 or record_age == 0:
        age_score = 0.5
    else:
        age_diff = abs(persona_age - record_age)
        if age_diff == 0:
            age_score = 1.0
        elif age_diff <= 2:
            age_score = 0.95 - (age_diff / 2.0) * 0.15
        elif age_diff <= 5:
            age_score = 0.80 - ((age_diff - 2) / 3.0) * 0.20
        else:
            age_score = max(0.0, 0.60 - ((age_diff - 5) / 10.0) * 0.60)

    breakdown['age_score'] = age_score
    breakdown['age_difference'] = age_diff if persona_age and record_age else None

    # Location type consideration (demographic diversity)
    persona_location = persona_tree.get('demographics', {}).get('location_type', 'unknown')
    location_score = 0.8  # Neutral - location doesn't heavily impact pregnancy matching

    breakdown['location_type'] = persona_location
    breakdown['location_score'] = location_score

    # Weighted average
    demo_score = (age_score * 0.8 + location_score * 0.2)

    return demo_score, breakdown


def score_socioeconomic_alignment(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Tuple[float, Dict[str, Any]]:
    """
    Score socioeconomic alignment.

    Returns:
        Tuple of (score, breakdown)
    """
    breakdown = {}

    # Healthcare access alignment
    persona_access = persona_tree.get('health_profile', {}).get('healthcare_access', 3)
    record_access = record_tree.get('healthcare_utilization', {}).get('estimated_healthcare_access', 3)

    access_diff = abs(persona_access - record_access)
    if access_diff == 0:
        access_score = 1.0
    elif access_diff == 1:
        access_score = 0.85
    elif access_diff == 2:
        access_score = 0.65
    else:
        access_score = max(0.3, 1.0 - (access_diff * 0.2))

    breakdown['healthcare_access_score'] = access_score
    breakdown['healthcare_access_diff'] = access_diff

    # Employment status - infer from healthcare utilization
    persona_employment = persona_tree.get('socioeconomic', {}).get('employment_status', 'employed')
    utilization_freq = record_tree.get('healthcare_utilization', {}).get('visit_frequency', 'regular')

    # Employed people with good healthcare tend to have regular visits
    employment_utilization_map = {
        'employed': {'frequent': 0.9, 'regular': 1.0, 'occasional': 0.8, 'rare': 0.6},
        'self_employed': {'frequent': 0.8, 'regular': 0.9, 'occasional': 0.8, 'rare': 0.5},
        'student': {'frequent': 0.7, 'regular': 0.8, 'occasional': 0.9, 'rare': 0.6},
        'homemaker': {'frequent': 0.8, 'regular': 0.9, 'occasional': 0.8, 'rare': 0.6},
        'unemployed': {'frequent': 0.6, 'regular': 0.7, 'occasional': 0.8, 'rare': 0.7},
        'disabled': {'frequent': 0.9, 'regular': 1.0, 'occasional': 0.8, 'rare': 0.6}
    }

    employment_score = employment_utilization_map.get(
        persona_employment, {'frequent': 0.7, 'regular': 0.8, 'occasional': 0.7, 'rare': 0.6}
    ).get(utilization_freq, 0.7)

    breakdown['employment_status'] = persona_employment
    breakdown['visit_frequency'] = utilization_freq
    breakdown['employment_utilization_score'] = employment_score

    # Insurance alignment
    persona_insurance = persona_tree.get('socioeconomic', {}).get('insurance_status', 'insured')
    insurance_score = 0.8  # Neutral - most records have some insurance

    breakdown['insurance_status'] = persona_insurance
    breakdown['insurance_score'] = insurance_score

    # Weighted average
    socio_score = (access_score * 0.5 + employment_score * 0.3 + insurance_score * 0.2)

    return socio_score, breakdown


def score_health_profile_alignment(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Tuple[float, Dict[str, Any]]:
    """
    Score health profile alignment - core matching criterion.

    Returns:
        Tuple of (score, breakdown)
    """
    breakdown = {}

    # Health consciousness alignment
    persona_consciousness = persona_tree.get('health_profile', {}).get('health_consciousness', 3)
    primary_care = record_tree.get('healthcare_utilization', {}).get('primary_care_engagement', 3)

    consciousness_diff = abs(persona_consciousness - primary_care)
    if consciousness_diff == 0:
        consciousness_score = 1.0
    elif consciousness_diff <= 1:
        consciousness_score = 0.9
    else:
        consciousness_score = max(0.5, 1.0 - (consciousness_diff * 0.15))

    breakdown['health_consciousness_score'] = consciousness_score
    breakdown['health_consciousness_diff'] = consciousness_diff

    # Healthcare access alignment (already in socioeconomic but impacts health profile)
    persona_healthcare_access = persona_tree.get('health_profile', {}).get('healthcare_access', 3)
    record_healthcare_access = record_tree.get('healthcare_utilization', {}).get('estimated_healthcare_access', 3)

    access_diff = abs(persona_healthcare_access - record_healthcare_access)
    if access_diff == 0:
        access_score = 1.0
    else:
        access_score = max(0.5, 1.0 - (access_diff * 0.2))

    breakdown['healthcare_access_score'] = access_score

    # Pregnancy readiness alignment with risk profile
    persona_readiness = persona_tree.get('health_profile', {}).get('pregnancy_readiness', 3)
    record_risk = record_tree.get('pregnancy_profile', {}).get('risk_level', 3)

    # Higher readiness should align with lower risk (1-2)
    # Lower readiness acceptable with higher risk (4-5)
    readiness_normalized = (persona_readiness - 1) / 4.0  # 0.0 to 1.0
    risk_normalized = (record_risk - 1) / 4.0  # 0.0 to 1.0

    # Invert risk: 1.0 means low risk, 0.0 means high risk
    risk_compatibility = 1.0 - risk_normalized

    readiness_alignment = 1.0 - abs(readiness_normalized - risk_compatibility)
    breakdown['pregnancy_readiness_score'] = readiness_alignment
    breakdown['pregnancy_readiness'] = persona_readiness
    breakdown['pregnancy_risk_level'] = record_risk

    # Health conditions compatibility
    persona_conditions = persona_tree.get('health_profile', {}).get('reported_health_conditions', [])
    record_chronic = record_tree.get('chronic_disease_count', 0)

    # Personas with conditions should match records with chronic diseases
    if persona_conditions and record_chronic > 0:
        condition_score = 1.0  # Good match
    elif not persona_conditions and record_chronic == 0:
        condition_score = 1.0  # Good match
    elif persona_conditions and record_chronic == 0:
        condition_score = 0.7  # Mild mismatch
    else:
        condition_score = 0.8  # Mild mismatch

    breakdown['health_conditions_score'] = condition_score
    breakdown['persona_has_conditions'] = len(persona_conditions) > 0
    breakdown['record_has_chronic'] = record_chronic > 0

    # Weighted average (health profile is critical)
    health_score = (
        consciousness_score * 0.30 +
        access_score * 0.25 +
        readiness_alignment * 0.25 +
        condition_score * 0.20
    )

    return health_score, breakdown


def score_behavioral_alignment(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Tuple[float, Dict[str, Any]]:
    """
    Score behavioral lifestyle alignment.

    Returns:
        Tuple of (score, breakdown)
    """
    breakdown = {}

    # Physical activity alignment with overall health
    persona_activity = persona_tree.get('behavioral', {}).get('physical_activity_level', 3)
    health_status = record_tree.get('overall_health_status', 'fair')

    health_status_map = {'excellent': 5, 'good': 4, 'fair': 3, 'poor': 2, 'complex': 1}
    health_score_value = health_status_map.get(health_status, 3)

    activity_diff = abs(persona_activity - health_score_value)
    if activity_diff == 0:
        activity_alignment = 1.0
    elif activity_diff <= 1:
        activity_alignment = 0.85
    else:
        activity_alignment = max(0.5, 1.0 - (activity_diff * 0.15))

    breakdown['physical_activity_score'] = activity_alignment
    breakdown['physical_activity_level'] = persona_activity
    breakdown['health_status'] = health_status

    # Smoking status and disease burden
    persona_smoking = persona_tree.get('behavioral', {}).get('smoking_status', 'never')
    comorbidity = record_tree.get('comorbidity_index', 0.0)

    smoking_risk_map = {'never': 0.2, 'former': 0.4, 'current': 0.8}
    persona_risk = smoking_risk_map.get(persona_smoking, 0.3)

    # Current smokers should have higher disease burden
    smoking_alignment = 1.0 - abs(persona_risk - min(comorbidity, 1.0)) * 0.5
    smoking_alignment = max(0.5, min(1.0, smoking_alignment))

    breakdown['smoking_status'] = persona_smoking
    breakdown['smoking_alignment_score'] = smoking_alignment
    breakdown['comorbidity_index'] = comorbidity

    # Alcohol consumption compatibility
    persona_alcohol = persona_tree.get('behavioral', {}).get('alcohol_consumption', 'never')
    alcohol_score = 0.8  # Neutral - most records compatible with various alcohol use

    breakdown['alcohol_consumption'] = persona_alcohol
    breakdown['alcohol_score'] = alcohol_score

    # Nutrition awareness alignment (inferred from health status)
    persona_nutrition = persona_tree.get('behavioral', {}).get('nutrition_awareness', 3)
    nutrition_expected = health_score_value  # Assume good health = good nutrition

    nutrition_diff = abs(persona_nutrition - nutrition_expected)
    nutrition_score = max(0.6, 1.0 - (nutrition_diff * 0.15))

    breakdown['nutrition_awareness'] = persona_nutrition
    breakdown['nutrition_score'] = nutrition_score

    # Weighted average
    behavioral_score = (
        activity_alignment * 0.30 +
        smoking_alignment * 0.25 +
        alcohol_score * 0.20 +
        nutrition_score * 0.25
    )

    return behavioral_score, breakdown


def score_psychosocial_alignment(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Tuple[float, Dict[str, Any]]:
    """
    Score psychosocial alignment - mental health and social support.

    Returns:
        Tuple of (score, breakdown)
    """
    breakdown = {}

    # Mental health alignment
    persona_mental = persona_tree.get('psychosocial', {}).get('mental_health_status', 3)
    # Infer mental health from pregnancy risk (complications can reflect mental burden)
    record_risk = record_tree.get('pregnancy_profile', {}).get('risk_level', 3)

    # Better mental health aligns with lower risk
    mental_expected = 5 - record_risk  # Inverted: low risk = better mental health
    mental_diff = abs(persona_mental - mental_expected)

    if mental_diff == 0:
        mental_score = 1.0
    elif mental_diff <= 1:
        mental_score = 0.85
    else:
        mental_score = max(0.5, 1.0 - (mental_diff * 0.15))

    breakdown['mental_health_status'] = persona_mental
    breakdown['mental_health_score'] = mental_score

    # Stress alignment
    persona_stress = persona_tree.get('psychosocial', {}).get('stress_level', 3)
    # Higher stress aligns with higher disease burden
    expected_stress = 6 - record_tree.get('healthcare_utilization', {}).get('primary_care_engagement', 3)

    stress_diff = abs(persona_stress - expected_stress)
    stress_score = max(0.5, 1.0 - (stress_diff * 0.15))

    breakdown['stress_level'] = persona_stress
    breakdown['stress_score'] = stress_score

    # Social support alignment
    persona_support = persona_tree.get('psychosocial', {}).get('social_support', 3)
    # Infer from healthcare engagement (higher engagement often = better support)
    primary_care = record_tree.get('healthcare_utilization', {}).get('primary_care_engagement', 3)

    support_score = 1.0 - abs((persona_support - 1) / 4.0 - (primary_care - 1) / 4.0)
    support_score = max(0.5, min(1.0, support_score))

    breakdown['social_support'] = persona_support
    breakdown['social_support_score'] = support_score

    # Family planning attitudes alignment
    persona_planning = persona_tree.get('psychosocial', {}).get('family_planning_attitudes', 'uncertain')
    # Infer from pregnancy profile
    has_pregnancy = record_tree.get('pregnancy_profile', {}).get('has_pregnancy_codes', False)

    if (persona_planning == 'wants_children' and has_pregnancy) or \
       (persona_planning in ['uncertain', 'does_not_want'] and not has_pregnancy):
        planning_score = 1.0
    else:
        planning_score = 0.7

    breakdown['family_planning_attitudes'] = persona_planning
    breakdown['has_pregnancy_codes'] = has_pregnancy
    breakdown['planning_score'] = planning_score

    # Weighted average
    psychosocial_score = (
        mental_score * 0.30 +
        stress_score * 0.20 +
        support_score * 0.25 +
        planning_score * 0.25
    )

    return psychosocial_score, breakdown


# ==================== COMPREHENSIVE SEMANTIC MATCHING ====================

def calculate_semantic_matching_score(
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any],
    weights: Optional[Dict[str, float]] = None
) -> Tuple[float, Dict[str, Any]]:
    """
    Calculate comprehensive semantic matching score with detailed breakdown.

    Args:
        persona_tree: Persona semantic tree (as dict)
        record_tree: Health record semantic tree (as dict)
        weights: Optional custom weights for components

    Returns:
        Tuple of (total_score, detailed_breakdown)
    """
    if weights is None:
        weights = {
            'demographics': 0.15,
            'socioeconomic': 0.15,
            'health_profile': 0.35,
            'behavioral': 0.15,
            'psychosocial': 0.20
        }

    # Calculate component scores
    demo_score, demo_breakdown = score_demographics_alignment(persona_tree, record_tree)
    socio_score, socio_breakdown = score_socioeconomic_alignment(persona_tree, record_tree)
    health_score, health_breakdown = score_health_profile_alignment(persona_tree, record_tree)
    behavioral_score, behavioral_breakdown = score_behavioral_alignment(persona_tree, record_tree)
    psychosocial_score, psychosocial_breakdown = score_psychosocial_alignment(persona_tree, record_tree)

    # Compile detailed breakdown
    breakdown = {
        'demographics': {
            'score': demo_score,
            'details': demo_breakdown
        },
        'socioeconomic': {
            'score': socio_score,
            'details': socio_breakdown
        },
        'health_profile': {
            'score': health_score,
            'details': health_breakdown
        },
        'behavioral': {
            'score': behavioral_score,
            'details': behavioral_breakdown
        },
        'psychosocial': {
            'score': psychosocial_score,
            'details': psychosocial_breakdown
        },
        'component_scores': {
            'demographics': demo_score,
            'socioeconomic': socio_score,
            'health_profile': health_score,
            'behavioral': behavioral_score,
            'psychosocial': psychosocial_score
        }
    }

    # Calculate weighted total
    total_score = (
        demo_score * weights['demographics'] +
        socio_score * weights['socioeconomic'] +
        health_score * weights['health_profile'] +
        behavioral_score * weights['behavioral'] +
        psychosocial_score * weights['psychosocial']
    )

    breakdown['total_semantic_score'] = total_score
    breakdown['weights_used'] = weights

    return total_score, breakdown


def generate_semantic_alignment_report(
    persona_idx: int,
    record_idx: int,
    semantic_score: float,
    breakdown: Dict[str, Any],
    persona_tree: Dict[str, Any],
    record_tree: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Generate human-readable semantic alignment report.

    Returns:
        Comprehensive alignment report
    """
    # Determine strengths and weaknesses
    component_scores = breakdown.get('component_scores', {})
    sorted_components = sorted(component_scores.items(), key=lambda x: x[1], reverse=True)

    strengths = [comp for comp, score in sorted_components[:2] if score >= 0.8]
    weaknesses = [comp for comp, score in sorted_components if score < 0.7]

    # Generate summary
    if semantic_score >= 0.85:
        match_quality = 'excellent'
        summary = 'Strong semantic alignment across all dimensions'
    elif semantic_score >= 0.75:
        match_quality = 'good'
        summary = 'Good overall semantic fit with minor variations'
    elif semantic_score >= 0.65:
        match_quality = 'fair'
        summary = 'Acceptable semantic alignment with some notable differences'
    else:
        match_quality = 'poor'
        summary = 'Limited semantic alignment; may require further review'

    # Key alignment insights
    insights = []

    health_profile = breakdown.get('health_profile', {}).get('details', {})
    if health_profile.get('pregnancy_readiness_score', 0) >= 0.8:
        insights.append('Excellent pregnancy readiness and risk level alignment')
    elif health_profile.get('pregnancy_readiness_score', 0) < 0.6:
        insights.append('Pregnancy readiness and risk level may be misaligned')

    if health_profile.get('health_consciousness_score', 0) >= 0.8:
        insights.append('Strong health consciousness and medical engagement alignment')

    behavioral = breakdown.get('behavioral', {}).get('details', {})
    if behavioral.get('smoking_alignment_score', 0) >= 0.8:
        insights.append('Lifestyle factors (smoking, activity) well-aligned')

    psychosocial = breakdown.get('psychosocial', {}).get('details', {})
    if psychosocial.get('social_support_score', 0) >= 0.8:
        insights.append('Strong social support and mental health alignment')

    report = {
        'persona_idx': persona_idx,
        'record_idx': record_idx,
        'total_semantic_score': semantic_score,
        'match_quality': match_quality,
        'summary': summary,
        'component_breakdown': component_scores,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'key_insights': insights,
        'detailed_breakdown': breakdown
    }

    return report
