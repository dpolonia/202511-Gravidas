#!/usr/bin/env python3
"""
Match personas to health records based on age compatibility and socioeconomic factors.

This script:
1. Loads personas and health records
2. Computes compatibility scores based on:
   - Age compatibility (60% weight)
   - Socioeconomic factors (40% weight)
3. Creates optimal matches using weighted algorithm
4. Saves matched persona-record pairs

Usage:
    python scripts/03_match_personas_records.py [--algorithm weighted]
"""

import json
import logging
import sys
import argparse
import random
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

# Import common loaders
from utils.common_loaders import load_config, load_personas, load_health_records

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/03_match_personas_records.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def calculate_age_compatibility(persona_age: int, record_age: int, tolerance: int = 2) -> float:
    """
    Calculate age compatibility score (0.0 to 1.0).

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
        # Within tolerance: linear decrease from 1.0 to 0.8
        return 1.0 - (age_diff / tolerance) * 0.2
    elif age_diff <= tolerance * 2:
        # Beyond tolerance but close: 0.8 to 0.5
        return 0.8 - ((age_diff - tolerance) / tolerance) * 0.3
    elif age_diff <= tolerance * 3:
        # Further away: 0.5 to 0.2
        return 0.5 - ((age_diff - tolerance * 2) / tolerance) * 0.3
    else:
        # Too far: exponential decay
        return max(0.0, 0.2 * (0.5 ** ((age_diff - tolerance * 3) / 5)))


def normalize_education(education: str) -> int:
    """Convert education level to numeric scale (0-4)."""
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


def calculate_socioeconomic_compatibility(
    persona: Dict[str, Any],
    record: Dict[str, Any]
) -> float:
    """
    Calculate socioeconomic compatibility score (0.0 to 1.0).

    Considers:
    - Education level
    - Income level
    - Marital status

    Returns:
        Compatibility score
    """
    score = 0.0
    factors = 0

    # Education compatibility
    if persona.get('education') and persona['education'] != 'unknown':
        persona_edu = normalize_education(persona['education'])
        # For records without explicit education, infer from other factors
        record_edu = normalize_education(persona.get('education', 'unknown'))

        edu_diff = abs(persona_edu - record_edu)
        edu_score = max(0.0, 1.0 - edu_diff / 5.0)
        score += edu_score
        factors += 1

    # Income compatibility
    if persona.get('income_level') and persona['income_level'] != 'unknown':
        persona_income = normalize_income(persona['income_level'])
        record_income = normalize_income(persona.get('income_level', 'unknown'))

        income_diff = abs(persona_income - record_income)
        income_score = max(0.0, 1.0 - income_diff / 4.0)
        score += income_score
        factors += 1

    # Marital status match
    if persona.get('marital_status') and persona['marital_status'] != 'unknown':
        # Exact match gets full points
        if persona['marital_status'] == persona.get('marital_status', 'unknown'):
            score += 1.0
        else:
            score += 0.5  # Partial credit for mismatch
        factors += 1

    # Average the scores
    if factors > 0:
        return score / factors
    else:
        return 0.5  # Default neutral score


def calculate_compatibility_score(
    persona: Dict[str, Any],
    record: Dict[str, Any],
    age_weight: float = 0.6,
    socioeconomic_weight: float = 0.4,
    age_tolerance: int = 2
) -> float:
    """
    Calculate overall compatibility score between persona and health record.

    Args:
        persona: Persona dictionary
        record: Health record dictionary
        age_weight: Weight for age compatibility (0-1)
        socioeconomic_weight: Weight for socioeconomic factors (0-1)
        age_tolerance: Age difference tolerance

    Returns:
        Overall compatibility score (0.0 to 1.0)
    """
    # Age compatibility
    persona_age = persona.get('age', 0)
    record_age = record.get('age', 0)

    if persona_age == 0 or record_age == 0:
        age_score = 0.5  # Unknown age
    else:
        age_score = calculate_age_compatibility(persona_age, record_age, age_tolerance)

    # Socioeconomic compatibility
    socioeconomic_score = calculate_socioeconomic_compatibility(persona, record)

    # Weighted combination
    total_score = (age_score * age_weight) + (socioeconomic_score * socioeconomic_weight)

    return total_score


def build_compatibility_matrix(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    config: Dict[str, Any]
) -> np.ndarray:
    """
    Build compatibility matrix for all persona-record pairs.

    Args:
        personas: List of personas
        records: List of health records
        config: Configuration dictionary

    Returns:
        NumPy array of compatibility scores
    """
    matching_config = config.get('matching', {})
    weights = matching_config.get('weights', {})
    age_weight = weights.get('age_compatibility', 0.6)
    socioeconomic_weight = weights.get('socioeconomic_factors', 0.4)
    age_tolerance = matching_config.get('age_tolerance', 2)

    logger.info("Computing compatibility matrix...")

    n_personas = len(personas)
    n_records = len(records)

    # Initialize matrix
    matrix = np.zeros((n_personas, n_records))

    # Calculate scores
    for i, persona in enumerate(personas):
        if (i + 1) % 1000 == 0:
            logger.info(f"[PROGRESS] Computed compatibility for {i + 1}/{n_personas} personas")

        for j, record in enumerate(records):
            score = calculate_compatibility_score(
                persona,
                record,
                age_weight,
                socioeconomic_weight,
                age_tolerance
            )
            matrix[i, j] = score

    logger.info("Compatibility matrix computed")
    return matrix


def match_optimal(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    compatibility_matrix: np.ndarray
) -> List[Tuple[int, int, float]]:
    """
    Find optimal matches using Hungarian algorithm.

    Args:
        personas: List of personas
        records: List of health records
        compatibility_matrix: Compatibility scores matrix

    Returns:
        List of (persona_idx, record_idx, score) tuples
    """
    logger.info("Running matching algorithm (optimal assignment)...")

    # Hungarian algorithm minimizes cost, so we use negative scores
    cost_matrix = -compatibility_matrix

    # Find optimal assignment
    persona_indices, record_indices = linear_sum_assignment(cost_matrix)

    # Create matches with scores
    matches = []
    for persona_idx, record_idx in zip(persona_indices, record_indices):
        score = compatibility_matrix[persona_idx, record_idx]
        matches.append((persona_idx, record_idx, score))

    logger.info(f"Created {len(matches)} optimal matches")
    return matches


def match_greedy(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    compatibility_matrix: np.ndarray
) -> List[Tuple[int, int, float]]:
    """
    Find matches using greedy algorithm (best available match).

    Args:
        personas: List of personas
        records: List of health records
        compatibility_matrix: Compatibility scores matrix

    Returns:
        List of (persona_idx, record_idx, score) tuples
    """
    logger.info("Running matching algorithm (greedy)...")

    matches = []
    used_records = set()

    for persona_idx in range(len(personas)):
        if (persona_idx + 1) % 1000 == 0:
            logger.info(f"[PROGRESS] Matched {persona_idx + 1}/{len(personas)} personas")

        # Find best available record
        best_score = -1
        best_record_idx = -1

        for record_idx in range(len(records)):
            if record_idx not in used_records:
                score = compatibility_matrix[persona_idx, record_idx]
                if score > best_score:
                    best_score = score
                    best_record_idx = record_idx

        if best_record_idx >= 0:
            matches.append((persona_idx, best_record_idx, best_score))
            used_records.add(best_record_idx)

    logger.info(f"Created {len(matches)} greedy matches")
    return matches


def match_random(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    compatibility_matrix: np.ndarray
) -> List[Tuple[int, int, float]]:
    """
    Create random matches (baseline for comparison).

    Args:
        personas: List of personas
        records: List of health records
        compatibility_matrix: Compatibility scores matrix

    Returns:
        List of (persona_idx, record_idx, score) tuples
    """
    logger.info("Running matching algorithm (random)...")

    record_indices = list(range(len(records)))
    random.shuffle(record_indices)

    matches = []
    for persona_idx, record_idx in enumerate(record_indices[:len(personas)]):
        score = compatibility_matrix[persona_idx, record_idx]
        matches.append((persona_idx, record_idx, score))

    logger.info(f"Created {len(matches)} random matches")
    return matches


def create_matched_pairs(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    matches: List[Tuple[int, int, float]]
) -> List[Dict[str, Any]]:
    """
    Create matched persona-record pairs.

    Args:
        personas: List of personas
        records: List of health records
        matches: List of (persona_idx, record_idx, score) tuples

    Returns:
        List of matched pairs
    """
    logger.info("Creating matched pairs...")

    matched_pairs = []

    for persona_idx, record_idx, score in matches:
        pair = {
            'persona': personas[persona_idx],
            'health_record': records[record_idx],
            'compatibility_score': score,
            'age_difference': abs(personas[persona_idx].get('age', 0) - records[record_idx].get('age', 0))
        }
        matched_pairs.append(pair)

    return matched_pairs


def calculate_statistics(matched_pairs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate matching statistics."""
    scores = [pair['compatibility_score'] for pair in matched_pairs]
    age_diffs = [pair['age_difference'] for pair in matched_pairs]

    stats = {
        'total_matches': len(matched_pairs),
        'average_compatibility_score': np.mean(scores),
        'min_compatibility_score': np.min(scores),
        'max_compatibility_score': np.max(scores),
        'average_age_difference': np.mean(age_diffs),
        'max_age_difference': np.max(age_diffs),
        'matches_within_2_years': sum(1 for diff in age_diffs if diff <= 2),
        'matches_within_5_years': sum(1 for diff in age_diffs if diff <= 5)
    }

    return stats


def save_matched_pairs(matched_pairs: List[Dict[str, Any]], output_dir: str):
    """Save matched pairs to JSON file."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save all matched pairs
    output_file = output_path / "matched_personas.json"
    with open(output_file, 'w') as f:
        json.dump(matched_pairs, f, indent=2)

    logger.info(f"Saved {len(matched_pairs)} matched pairs to {output_file}")

    # Save statistics
    stats = calculate_statistics(matched_pairs)
    stats_file = output_path / "matching_statistics.json"
    with open(stats_file, 'w') as f:
        json.dump(stats, f, indent=2)

    logger.info(f"Saved statistics to {stats_file}")

    # Log key statistics
    logger.info(f"Average compatibility score: {stats['average_compatibility_score']:.3f}")
    logger.info(f"Average age difference: {stats['average_age_difference']:.2f} years")
    logger.info(f"Matches within 2 years: {stats['matches_within_2_years']} ({stats['matches_within_2_years']/len(matched_pairs)*100:.1f}%)")


def main():
    parser = argparse.ArgumentParser(description='Match personas to health records')
    parser.add_argument('--personas', type=str, default='data/personas/personas.json', help='Personas file')
    parser.add_argument('--records', type=str, default='data/health_records/health_records.json', help='Health records file')
    parser.add_argument('--output', type=str, default='data/matched', help='Output directory')
    parser.add_argument('--algorithm', type=str, default='optimal', choices=['optimal', 'greedy', 'random'], help='Matching algorithm')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')
    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    logger.info("=== Persona-Record Matching Script Started ===")

    # Load configuration
    config = load_config(args.config)

    # Load data
    personas = load_personas(args.personas)
    records = load_health_records(args.records)

    # Ensure equal counts
    min_count = min(len(personas), len(records))
    if len(personas) != len(records):
        logger.warning(f"Unequal counts: {len(personas)} personas, {len(records)} records")
        logger.info(f"Using first {min_count} of each")
        personas = personas[:min_count]
        records = records[:min_count]

    try:
        # Build compatibility matrix
        compatibility_matrix = build_compatibility_matrix(personas, records, config)

        # Run matching algorithm
        if args.algorithm == 'optimal':
            matches = match_optimal(personas, records, compatibility_matrix)
        elif args.algorithm == 'greedy':
            matches = match_greedy(personas, records, compatibility_matrix)
        else:  # random
            matches = match_random(personas, records, compatibility_matrix)

        # Create matched pairs
        matched_pairs = create_matched_pairs(personas, records, matches)

        # Save results
        save_matched_pairs(matched_pairs, args.output)

        logger.info(f"[SUCCESS] Matched {len(matched_pairs)} persona-record pairs")
        logger.info("=== Persona-Record Matching Script Completed ===")

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
