#!/usr/bin/env python3
"""
Enhanced matching algorithm with semantic tree similarity scoring.

This script:
1. Supports N personas -> M health records matching (N >= M)
2. Uses semantic tree similarity for intelligent matching
3. Combines semantic and demographic factors
4. Tracks detailed match quality metrics with explanations
5. Provides comprehensive quality analysis and reporting
6. Generates semantic alignment reports for matches

Key improvements:
- Semantic tree-based similarity scoring (5 components)
- Healthcare-specific matching factors
- Quality-based selection from large pools
- Detailed semantic alignment reports
- Match explainability for clinical review
- Blended demographic + semantic scoring

Semantic Components Scored:
- Demographics: Age, location alignment
- Socioeconomic: Healthcare access, employment, insurance
- Health Profile: Health consciousness, pregnancy readiness, conditions
- Behavioral: Physical activity, smoking, nutrition, sleep
- Psychosocial: Mental health, stress, support, family planning

Usage:
    python scripts/03_match_personas_records_enhanced.py
    python scripts/03_match_personas_records_enhanced.py --semantic-weight 0.7
"""

import json
import logging
import sys
import argparse
from pathlib import Path
from typing import List, Dict, Any, Tuple
import numpy as np

try:
    import yaml
    from scipy.optimize import linear_sum_assignment
    from tqdm import tqdm
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import common loaders and semantic matching utilities
from utils.common_loaders import load_config, load_personas, load_health_records
from utils.semantic_matcher import calculate_semantic_matching_score, generate_semantic_alignment_report

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/03_match_personas_records_enhanced.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def calculate_age_compatibility(persona_age: int, record_age: int, tolerance: int = 2) -> float:
    """
    Calculate age compatibility score with enhanced precision.

    Args:
        persona_age: Persona age
        record_age: Health record age
        tolerance: Age difference tolerance in years

    Returns:
        Compatibility score (1.0 = perfect match, 0.0 = incompatible)
    """
    age_diff = abs(persona_age - record_age)

    if age_diff == 0:
        return 1.0
    elif age_diff <= tolerance:
        # Within tolerance: linear decrease from 1.0 to 0.85
        return 1.0 - (age_diff / tolerance) * 0.15
    elif age_diff <= tolerance * 2:
        # Beyond tolerance but acceptable: 0.85 to 0.60
        return 0.85 - ((age_diff - tolerance) / tolerance) * 0.25
    elif age_diff <= tolerance * 3:
        # Further away: 0.60 to 0.30
        return 0.60 - ((age_diff - tolerance * 2) / tolerance) * 0.30
    else:
        # Too far: exponential decay
        return max(0.0, 0.30 * (0.5 ** ((age_diff - tolerance * 3) / 5)))


def normalize_education(education: str) -> int:
    """Convert education level to numeric scale (0-5)."""
    education_map = {
        'no_degree': 0,
        'unknown': 1,
        'high_school': 2,
        'bachelors': 3,
        'masters': 4,
        'doctorate': 5
    }
    return education_map.get(education.lower(), 1)


def normalize_income(income: str) -> int:
    """Convert income level to numeric scale (0-4)."""
    income_map = {
        'low': 0,
        'lower_middle': 1,
        'middle': 2,
        'upper_middle': 3,
        'high': 4,
        'unknown': 2  # Default to middle
    }
    return income_map.get(income.lower(), 2)


def calculate_occupation_compatibility(persona_occupation: str, persona_education: str) -> float:
    """
    Calculate occupation compatibility score based on occupation and education alignment.

    High-skilled occupations require higher education for full compatibility.

    Returns:
        Compatibility score (0.0 to 1.0)
    """
    if not persona_occupation:
        return 0.5  # Neutral score for unknown

    occupation = persona_occupation.lower()
    education_level = normalize_education(persona_education)

    # High-skilled occupations
    high_skilled = ['doctor', 'professor', 'scientist', 'engineer', 'lawyer', 'researcher']
    # Medium-skilled occupations
    medium_skilled = ['teacher', 'nurse', 'accountant', 'manager', 'analyst', 'designer']
    # Lower-skilled occupations
    lower_skilled = ['clerk', 'cashier', 'retail', 'assistant', 'driver', 'worker']

    # Check occupation category
    for occ in high_skilled:
        if occ in occupation:
            # High-skilled: expect masters/doctorate
            if education_level >= 4:
                return 1.0
            elif education_level == 3:
                return 0.8
            else:
                return 0.6

    for occ in medium_skilled:
        if occ in occupation:
            # Medium-skilled: expect bachelors
            if education_level >= 3:
                return 1.0
            elif education_level == 2:
                return 0.8
            else:
                return 0.6

    for occ in lower_skilled:
        if occ in occupation:
            # Lower-skilled: any education acceptable
            return 1.0

    # Unknown occupation category: give benefit of the doubt
    return 0.7


def calculate_marital_status_compatibility(persona_status: str, record_age: int) -> float:
    """
    Calculate marital status compatibility considering age.

    Args:
        persona_status: Marital status from persona
        record_age: Age from health record

    Returns:
        Compatibility score (0.0 to 1.0)
    """
    if not persona_status or persona_status == 'unknown':
        return 0.5

    status = persona_status.lower()

    # Pregnancy context: married/partnered status is more common
    if status in ['married', 'partnered', 'domestic_partnership']:
        # Married/partnered is common for pregnancy, slight boost
        return 1.0
    elif status == 'single':
        # Single pregnancies are also common, neutral score
        return 0.8
    elif status in ['divorced', 'separated']:
        # Less common but acceptable
        return 0.7
    elif status == 'widowed':
        # Rare for pregnancy age range
        if record_age < 35:
            return 0.5
        else:
            return 0.6

    return 0.5


def calculate_enhanced_compatibility_score(
    persona: Dict[str, Any],
    record: Dict[str, Any],
    weights: Dict[str, float] = None
) -> Tuple[float, Dict[str, float]]:
    """
    Calculate enhanced compatibility score with detailed breakdown.

    Default weights:
    - Age: 0.40 (most important for medical context)
    - Education: 0.20
    - Income: 0.15
    - Marital status: 0.15
    - Occupation: 0.10

    Args:
        persona: Persona dictionary
        record: Health record dictionary
        weights: Custom weight dictionary

    Returns:
        Tuple of (total_score, score_breakdown)
    """
    if weights is None:
        weights = {
            'age': 0.40,
            'education': 0.20,
            'income': 0.15,
            'marital_status': 0.15,
            'occupation': 0.10
        }

    breakdown = {}

    # Age compatibility (most important)
    persona_age = persona.get('age', 0)
    record_age = record.get('age', 0)

    if persona_age == 0 or record_age == 0:
        age_score = 0.5
    else:
        age_score = calculate_age_compatibility(persona_age, record_age, tolerance=2)

    breakdown['age'] = age_score

    # Education compatibility
    persona_edu = normalize_education(persona.get('education', 'unknown'))
    # For records, we don't have education, so we use a neutral comparison
    # In a larger pool, education diversity will naturally emerge
    edu_score = 0.7 + (persona_edu / 5.0) * 0.3  # 0.7 to 1.0 range
    breakdown['education'] = edu_score

    # Income compatibility
    persona_income = normalize_income(persona.get('income_level', 'unknown'))
    # Middle income is most common, slight preference
    income_distance = abs(persona_income - 2)  # Distance from middle class
    income_score = 1.0 - (income_distance / 4.0) * 0.3  # 0.7 to 1.0 range
    breakdown['income'] = income_score

    # Marital status compatibility
    marital_score = calculate_marital_status_compatibility(
        persona.get('marital_status', 'unknown'),
        record_age
    )
    breakdown['marital_status'] = marital_score

    # Occupation compatibility
    occupation_score = calculate_occupation_compatibility(
        persona.get('occupation', ''),
        persona.get('education', 'unknown')
    )
    breakdown['occupation'] = occupation_score

    # Calculate weighted total
    total_score = sum(breakdown[key] * weights[key] for key in weights.keys())

    return total_score, breakdown


def build_blended_compatibility_matrix(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    config: Dict[str, Any],
    semantic_weight: float = 0.6
) -> Tuple[np.ndarray, List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Build blended compatibility matrix combining demographic and semantic scoring.

    Args:
        personas: List of personas with semantic trees
        records: List of health records with semantic trees
        config: Configuration dictionary
        semantic_weight: Weight for semantic scoring (0.0-1.0)
                        0.0 = pure demographic, 1.0 = pure semantic

    Returns:
        Tuple of (compatibility_matrix, demographic_metrics, semantic_metrics)
    """
    demographic_weight = 1.0 - semantic_weight

    logger.info(f"Computing blended compatibility matrix for {len(personas)} personas × {len(records)} records...")
    logger.info(f"Semantic weight: {semantic_weight:.1%} | Demographic weight: {demographic_weight:.1%}")

    n_personas = len(personas)
    n_records = len(records)

    # Initialize matrices and metrics storage
    matrix = np.zeros((n_personas, n_records))
    demographic_metrics = []
    semantic_metrics = []

    # Get demographic weights
    matching_config = config.get('matching', {})
    demo_weights = matching_config.get('enhanced_weights', {
        'age': 0.40,
        'education': 0.20,
        'income': 0.15,
        'marital_status': 0.15,
        'occupation': 0.10
    })

    # Calculate scores
    for i, persona in enumerate(personas):
        if (i + 1) % 1000 == 0:
            logger.info(f"[PROGRESS] Computed compatibility for {i + 1}/{n_personas} personas")

        persona_demo_metrics = []
        persona_semantic_metrics = []

        for j, record in enumerate(records):
            # Calculate demographic score (baseline)
            demo_score, demo_breakdown = calculate_enhanced_compatibility_score(
                persona, record, demo_weights
            )

            # Calculate semantic score if semantic trees available
            semantic_score = 0.5
            semantic_breakdown = {}
            semantic_report = None

            if persona.get('semantic_tree') and record.get('semantic_tree'):
                try:
                    semantic_score, semantic_breakdown = calculate_semantic_matching_score(
                        persona['semantic_tree'],
                        record['semantic_tree']
                    )

                    # Generate alignment report
                    semantic_report = generate_semantic_alignment_report(
                        i, j, semantic_score, semantic_breakdown,
                        persona['semantic_tree'], record['semantic_tree']
                    )

                except Exception as e:
                    logger.warning(f"Failed to calculate semantic score for {i},{j}: {e}")
                    semantic_score = 0.5
                    semantic_breakdown = {}

            # Blend scores
            blended_score = (
                demo_score * demographic_weight +
                semantic_score * semantic_weight
            )

            matrix[i, j] = blended_score

            # Store metrics
            persona_demo_metrics.append({
                'persona_idx': i,
                'record_idx': j,
                'demographic_score': demo_score,
                'demographic_breakdown': demo_breakdown
            })

            persona_semantic_metrics.append({
                'persona_idx': i,
                'record_idx': j,
                'semantic_score': semantic_score,
                'semantic_breakdown': semantic_breakdown,
                'semantic_report': semantic_report,
                'blended_score': blended_score
            })

        demographic_metrics.append(persona_demo_metrics)
        semantic_metrics.append(persona_semantic_metrics)

    logger.info("✅ Blended compatibility matrix computed")
    return matrix, demographic_metrics, semantic_metrics


def build_compatibility_matrix(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> Tuple[np.ndarray, List[Dict[str, Any]]]:
    """
    Build enhanced compatibility matrix with detailed metrics.

    Args:
        personas: List of personas
        records: List of health records
        config: Configuration dictionary

    Returns:
        Tuple of (compatibility_matrix, detailed_metrics)
    """
    matching_config = config.get('matching', {})
    weights = matching_config.get('enhanced_weights', {
        'age': 0.40,
        'education': 0.20,
        'income': 0.15,
        'marital_status': 0.15,
        'occupation': 0.10
    })

    logger.info(f"Computing compatibility matrix for {len(personas)} personas × {len(records)} records...")
    logger.info(f"Using weights: {weights}")

    n_personas = len(personas)
    n_records = len(records)

    # Initialize matrix and metrics storage
    matrix = np.zeros((n_personas, n_records))
    all_metrics = []

    # Calculate scores
    for i, persona in enumerate(personas):
        if (i + 1) % 1000 == 0:
            logger.info(f"[PROGRESS] Computed compatibility for {i + 1}/{n_personas} personas")

        persona_metrics = []
        for j, record in enumerate(records):
            score, breakdown = calculate_enhanced_compatibility_score(
                persona, record, weights
            )
            matrix[i, j] = score

            # Store detailed metrics
            persona_metrics.append({
                'persona_idx': i,
                'record_idx': j,
                'total_score': score,
                'breakdown': breakdown
            })

        all_metrics.append(persona_metrics)

    logger.info("✅ Compatibility matrix computed")
    return matrix, all_metrics


def match_optimal_with_selection(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    compatibility_matrix: np.ndarray,
    detailed_metrics: List[Dict[str, Any]]
) -> Tuple[List[Tuple[int, int, float]], List[Dict[str, Any]]]:
    """
    Find optimal matches with quality metrics, supporting N personas -> M records.

    When N > M, selects the M best matches from the larger pool.

    Args:
        personas: List of personas (potentially larger than records)
        records: List of health records
        compatibility_matrix: Compatibility scores matrix
        detailed_metrics: Detailed scoring breakdown for each pair

    Returns:
        Tuple of (matches, match_quality_metrics)
    """
    n_personas = len(personas)
    n_records = len(records)

    logger.info(f"Running enhanced matching algorithm...")
    logger.info(f"Pool: {n_personas} personas → {n_records} health records")

    if n_personas < n_records:
        logger.warning(f"More records than personas! This will result in some unmatched records.")
        logger.warning(f"Consider generating more personas for better coverage.")

    # Hungarian algorithm works on square matrices, so we handle rectangular cases
    if n_personas == n_records:
        # Equal counts: standard optimal assignment
        cost_matrix = -compatibility_matrix
        persona_indices, record_indices = linear_sum_assignment(cost_matrix)
    else:
        # Unequal counts: find best assignments
        cost_matrix = -compatibility_matrix
        persona_indices, record_indices = linear_sum_assignment(cost_matrix)

    # Create matches with detailed quality metrics
    matches = []
    match_quality_metrics = []

    for persona_idx, record_idx in zip(persona_indices, record_indices):
        score = compatibility_matrix[persona_idx, record_idx]

        # Get detailed breakdown
        breakdown = detailed_metrics[persona_idx][record_idx]['breakdown']

        # Calculate quality category
        if score >= 0.85:
            quality = 'excellent'
        elif score >= 0.75:
            quality = 'good'
        elif score >= 0.65:
            quality = 'fair'
        else:
            quality = 'poor'

        matches.append((persona_idx, record_idx, score))

        match_quality_metrics.append({
            'persona_idx': persona_idx,
            'record_idx': record_idx,
            'compatibility_score': score,
            'quality_category': quality,
            'score_breakdown': breakdown,
            'persona_age': personas[persona_idx].get('age'),
            'record_age': records[record_idx].get('age'),
            'age_difference': abs(
                personas[persona_idx].get('age', 0) -
                records[record_idx].get('age', 0)
            )
        })

    logger.info(f"✅ Created {len(matches)} optimal matches")

    # Report quality distribution
    quality_counts = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
    for metric in match_quality_metrics:
        quality_counts[metric['quality_category']] += 1

    total = len(match_quality_metrics)
    logger.info(f"Quality distribution:")
    logger.info(f"  - Excellent (≥0.85): {quality_counts['excellent']} ({quality_counts['excellent']/total*100:.1f}%)")
    logger.info(f"  - Good (≥0.75): {quality_counts['good']} ({quality_counts['good']/total*100:.1f}%)")
    logger.info(f"  - Fair (≥0.65): {quality_counts['fair']} ({quality_counts['fair']/total*100:.1f}%)")
    logger.info(f"  - Poor (<0.65): {quality_counts['poor']} ({quality_counts['poor']/total*100:.1f}%)")

    return matches, match_quality_metrics


def create_matched_pairs_with_quality(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    matches: List[Tuple[int, int, float]],
    quality_metrics: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Create matched persona-record pairs with enhanced quality metrics.

    Args:
        personas: List of personas
        records: List of health records
        matches: List of (persona_idx, record_idx, score) tuples
        quality_metrics: Detailed quality metrics for each match

    Returns:
        List of matched pairs with quality information
    """
    logger.info("Creating matched pairs with quality metrics...")

    matched_pairs = []

    for i, (persona_idx, record_idx, score) in enumerate(matches):
        pair = {
            'persona': personas[persona_idx],
            'health_record': records[record_idx],
            'match_quality': {
                'compatibility_score': score,
                'quality_category': quality_metrics[i]['quality_category'],
                'score_breakdown': quality_metrics[i]['score_breakdown'],
                'age_difference': quality_metrics[i]['age_difference']
            }
        }
        matched_pairs.append(pair)

    return matched_pairs


def calculate_enhanced_statistics(
    matched_pairs: List[Dict[str, Any]],
    quality_metrics: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Calculate comprehensive matching statistics with quality analysis."""
    scores = [pair['match_quality']['compatibility_score'] for pair in matched_pairs]
    age_diffs = [pair['match_quality']['age_difference'] for pair in matched_pairs]

    # Quality distribution
    quality_dist = {'excellent': 0, 'good': 0, 'fair': 0, 'poor': 0}
    for pair in matched_pairs:
        quality_dist[pair['match_quality']['quality_category']] += 1

    # Score breakdown averages
    breakdown_keys = ['age', 'education', 'income', 'marital_status', 'occupation']
    breakdown_avgs = {}
    for key in breakdown_keys:
        scores_for_key = [m['score_breakdown'][key] for m in quality_metrics]
        breakdown_avgs[key] = np.mean(scores_for_key)

    stats = {
        'total_matches': len(matched_pairs),
        'compatibility_scores': {
            'average': float(np.mean(scores)),
            'median': float(np.median(scores)),
            'std_dev': float(np.std(scores)),
            'min': float(np.min(scores)),
            'max': float(np.max(scores)),
            'percentile_25': float(np.percentile(scores, 25)),
            'percentile_75': float(np.percentile(scores, 75))
        },
        'quality_distribution': {
            'excellent': quality_dist['excellent'],
            'excellent_pct': quality_dist['excellent'] / len(matched_pairs) * 100,
            'good': quality_dist['good'],
            'good_pct': quality_dist['good'] / len(matched_pairs) * 100,
            'fair': quality_dist['fair'],
            'fair_pct': quality_dist['fair'] / len(matched_pairs) * 100,
            'poor': quality_dist['poor'],
            'poor_pct': quality_dist['poor'] / len(matched_pairs) * 100
        },
        'age_differences': {
            'average': float(np.mean(age_diffs)),
            'median': float(np.median(age_diffs)),
            'max': int(np.max(age_diffs)),
            'within_2_years': int(sum(1 for d in age_diffs if d <= 2)),
            'within_2_years_pct': sum(1 for d in age_diffs if d <= 2) / len(age_diffs) * 100,
            'within_5_years': int(sum(1 for d in age_diffs if d <= 5)),
            'within_5_years_pct': sum(1 for d in age_diffs if d <= 5) / len(age_diffs) * 100
        },
        'score_breakdown_averages': breakdown_avgs
    }

    return stats


def convert_numpy_types(obj):
    """Convert numpy types to native Python types for JSON serialization."""
    if isinstance(obj, np.integer):
        return int(obj)
    elif isinstance(obj, np.floating):
        return float(obj)
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, dict):
        return {key: convert_numpy_types(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy_types(item) for item in obj]
    return obj


def save_enhanced_results(
    matched_pairs: List[Dict[str, Any]],
    quality_metrics: List[Dict[str, Any]],
    output_dir: str
):
    """Save enhanced matching results with quality metrics."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Convert numpy types to native Python types
    matched_pairs = convert_numpy_types(matched_pairs)
    quality_metrics = convert_numpy_types(quality_metrics)

    # Save matched pairs
    output_file = output_path / "matched_personas.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(matched_pairs, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved {len(matched_pairs)} matched pairs to {output_file}")

    # Save detailed quality metrics
    quality_file = output_path / "match_quality_metrics.json"
    with open(quality_file, 'w', encoding='utf-8') as f:
        json.dump(quality_metrics, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved quality metrics to {quality_file}")

    # Calculate and save statistics
    stats = calculate_enhanced_statistics(matched_pairs, quality_metrics)
    stats_file = output_path / "matching_statistics.json"
    with open(stats_file, 'w', encoding='utf-8') as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)
    logger.info(f"✅ Saved statistics to {stats_file}")

    # Log key statistics
    logger.info("=" * 60)
    logger.info("MATCHING QUALITY REPORT")
    logger.info("=" * 60)
    logger.info(f"Total matches: {stats['total_matches']}")
    logger.info(f"Average compatibility score: {stats['compatibility_scores']['average']:.3f}")
    logger.info(f"Median compatibility score: {stats['compatibility_scores']['median']:.3f}")
    logger.info(f"Score std deviation: {stats['compatibility_scores']['std_dev']:.3f}")
    logger.info("")
    logger.info("Quality Distribution:")
    logger.info(f"  - Excellent (≥0.85): {stats['quality_distribution']['excellent']} ({stats['quality_distribution']['excellent_pct']:.1f}%)")
    logger.info(f"  - Good (≥0.75): {stats['quality_distribution']['good']} ({stats['quality_distribution']['good_pct']:.1f}%)")
    logger.info(f"  - Fair (≥0.65): {stats['quality_distribution']['fair']} ({stats['quality_distribution']['fair_pct']:.1f}%)")
    logger.info(f"  - Poor (<0.65): {stats['quality_distribution']['poor']} ({stats['quality_distribution']['poor_pct']:.1f}%)")
    logger.info("")
    logger.info("Age Matching:")
    logger.info(f"  - Average age difference: {stats['age_differences']['average']:.2f} years")
    logger.info(f"  - Within 2 years: {stats['age_differences']['within_2_years']} ({stats['age_differences']['within_2_years_pct']:.1f}%)")
    logger.info(f"  - Within 5 years: {stats['age_differences']['within_5_years']} ({stats['age_differences']['within_5_years_pct']:.1f}%)")
    logger.info("")
    logger.info("Score Breakdown (Component Averages):")
    for component, score in stats['score_breakdown_averages'].items():
        logger.info(f"  - {component.capitalize()}: {score:.3f}")
    logger.info("=" * 60)


def main():
    parser = argparse.ArgumentParser(description='Enhanced persona-record matching with semantic tree similarity')
    parser.add_argument('--personas', type=str, default='data/personas/personas.json', help='Personas file')
    parser.add_argument('--records', type=str, default='data/health_records/health_records.json', help='Health records file')
    parser.add_argument('--output', type=str, default='data/matched', help='Output directory')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')
    parser.add_argument('--semantic-weight', type=float, default=0.6,
                        help='Weight for semantic scoring (0.0-1.0, default 0.6). 0.0=demographic only, 1.0=semantic only')
    parser.add_argument('--semantic-only', action='store_true', help='Use semantic matching only (equivalent to --semantic-weight 1.0)')
    args = parser.parse_args()

    # Handle semantic-only flag
    if args.semantic_only:
        semantic_weight = 1.0
    else:
        semantic_weight = args.semantic_weight

    # Validate weight
    if not (0.0 <= semantic_weight <= 1.0):
        logger.error(f"Semantic weight must be between 0.0 and 1.0, got {semantic_weight}")
        sys.exit(1)

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    logger.info("=" * 60)
    logger.info("ENHANCED PERSONA-RECORD MATCHING WITH SEMANTIC TREES STARTED")
    logger.info("=" * 60)

    # Load configuration
    config = load_config(args.config)

    # Load data
    personas = load_personas(args.personas)
    records = load_health_records(args.records)

    logger.info(f"Loaded {len(personas)} personas and {len(records)} health records")

    if len(personas) > len(records):
        logger.info(f"✅ Large pool mode: Selecting best {len(records)} matches from {len(personas)} personas")
    elif len(personas) < len(records):
        logger.warning(f"⚠️  More records than personas. Some records will be unmatched.")

    # Check for semantic trees
    has_semantic_personas = any(p.get('semantic_tree') for p in personas)
    has_semantic_records = any(r.get('semantic_tree') for r in records)

    if (has_semantic_personas and has_semantic_records) and semantic_weight > 0:
        logger.info(f"✅ Semantic trees detected. Using blended matching with {semantic_weight:.0%} semantic weight")
        use_semantic = True
    else:
        if semantic_weight > 0:
            logger.warning("⚠️  Semantic trees not found. Falling back to demographic matching only")
        semantic_weight = 0.0
        use_semantic = False

    try:
        # Build compatibility matrix
        if use_semantic and semantic_weight > 0:
            logger.info("Building blended compatibility matrix (demographic + semantic)...")
            compatibility_matrix, demographic_metrics, semantic_metrics = build_blended_compatibility_matrix(
                personas, records, config, semantic_weight=semantic_weight
            )

            # Store semantic metrics for output
            detailed_metrics = semantic_metrics
        else:
            logger.info("Building demographic compatibility matrix...")
            compatibility_matrix, detailed_metrics = build_compatibility_matrix(
                personas, records, config
            )

        # Run enhanced matching algorithm
        matches, quality_metrics = match_optimal_with_selection(
            personas, records, compatibility_matrix, detailed_metrics
        )

        # Create matched pairs with quality information
        matched_pairs = create_matched_pairs_with_quality(
            personas, records, matches, quality_metrics
        )

        # Save results with quality metrics
        save_enhanced_results(matched_pairs, quality_metrics, args.output)

        logger.info("=" * 60)
        logger.info("✅ ENHANCED MATCHING COMPLETED SUCCESSFULLY")
        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
