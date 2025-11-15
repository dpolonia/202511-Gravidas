#!/usr/bin/env python3
"""
Calibrate Anomaly Detection for Matching Algorithm

This script analyzes matching score distributions across all persona-record pairs
to calibrate the anomaly detection threshold for the matching algorithm.

Phase 1, Task 1.3 - v1.2.0 Implementation

Purpose:
- Analyze matching score distributions (semantic, demographic, blended)
- Calculate statistical measures (mean, median, std dev, percentiles)
- Identify outliers and anomalous matches
- Calibrate anomaly threshold based on statistical analysis
- Validate threshold against edge cases
- Generate recommendations for production configuration

Output:
- Console report with distribution analysis
- logs/anomaly_calibration_report.json - Detailed calibration data
- Recommended threshold values for production use
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Tuple
import statistics
import numpy as np
from datetime import datetime

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
    """
    Load health records and build semantic trees.

    Args:
        limit: Maximum number of records to load (None for all)

    Returns:
        List of health records with semantic trees
    """
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
    """
    Calculate blended matching score.

    Args:
        persona: Persona dictionary
        record: Health record dictionary
        semantic_weight: Weight for semantic component (0.0-1.0)

    Returns:
        Tuple of (total_score, breakdown)
    """
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


def analyze_score_distribution(
    personas: List[Dict[str, Any]],
    records: List[Dict[str, Any]],
    semantic_weight: float = 0.6
) -> Dict[str, Any]:
    """
    Analyze the distribution of matching scores.

    Args:
        personas: List of personas
        records: List of health records
        semantic_weight: Weight for semantic component

    Returns:
        Dictionary with distribution statistics
    """
    logger.info(f"Calculating scores for {len(personas)} personas × {len(records)} records...")

    all_scores = []
    best_match_scores = []
    persona_statistics = []

    for persona in personas:
        persona_scores = []

        for record in records:
            score, breakdown = calculate_blended_score(persona, record, semantic_weight)

            all_scores.append(score)
            persona_scores.append({
                'score': score,
                'record_id': record['patient_id'],
                'breakdown': breakdown
            })

        # Sort to find best match for this persona
        persona_scores.sort(key=lambda x: x['score'], reverse=True)
        best_match = persona_scores[0]
        best_match_scores.append(best_match['score'])

        persona_statistics.append({
            'persona_id': persona['id'],
            'persona_name': persona['name'],
            'best_match_score': best_match['score'],
            'best_match_record': best_match['record_id'][:30],
            'median_score': statistics.median([s['score'] for s in persona_scores]),
            'mean_score': statistics.mean([s['score'] for s in persona_scores]),
            'worst_match_score': persona_scores[-1]['score']
        })

    logger.info(f"✓ Calculated {len(all_scores)} total scores")

    # Calculate distribution statistics
    stats = {
        'all_scores': {
            'count': len(all_scores),
            'min': min(all_scores),
            'max': max(all_scores),
            'mean': statistics.mean(all_scores),
            'median': statistics.median(all_scores),
            'std_dev': statistics.stdev(all_scores),
            'percentiles': {
                '1st': np.percentile(all_scores, 1),
                '5th': np.percentile(all_scores, 5),
                '10th': np.percentile(all_scores, 10),
                '25th': np.percentile(all_scores, 25),
                '50th': np.percentile(all_scores, 50),
                '75th': np.percentile(all_scores, 75),
                '90th': np.percentile(all_scores, 90),
                '95th': np.percentile(all_scores, 95),
                '99th': np.percentile(all_scores, 99)
            }
        },
        'best_match_scores': {
            'count': len(best_match_scores),
            'min': min(best_match_scores),
            'max': max(best_match_scores),
            'mean': statistics.mean(best_match_scores),
            'median': statistics.median(best_match_scores),
            'std_dev': statistics.stdev(best_match_scores),
            'percentiles': {
                '1st': np.percentile(best_match_scores, 1),
                '5th': np.percentile(best_match_scores, 5),
                '10th': np.percentile(best_match_scores, 10),
                '25th': np.percentile(best_match_scores, 25),
                '50th': np.percentile(best_match_scores, 50),
                '75th': np.percentile(best_match_scores, 75),
                '90th': np.percentile(best_match_scores, 90),
                '95th': np.percentile(best_match_scores, 95),
                '99th': np.percentile(best_match_scores, 99)
            }
        },
        'persona_statistics': persona_statistics,
        'semantic_weight': semantic_weight
    }

    return stats, all_scores, best_match_scores


def identify_outliers(scores: List[float], stats: Dict[str, Any]) -> Dict[str, Any]:
    """
    Identify outliers using multiple methods.

    Methods:
    1. IQR method (values < Q1 - 1.5*IQR or > Q3 + 1.5*IQR)
    2. Z-score method (|z| > 3)
    3. Modified Z-score using MAD (|z| > 3.5)

    Args:
        scores: List of scores
        stats: Statistics dictionary

    Returns:
        Dictionary with outlier analysis
    """
    q1 = stats['percentiles']['25th']
    q3 = stats['percentiles']['75th']
    iqr = q3 - q1

    # IQR method
    lower_fence = q1 - 1.5 * iqr
    upper_fence = q3 + 1.5 * iqr
    iqr_outliers = [s for s in scores if s < lower_fence or s > upper_fence]

    # Z-score method
    mean = stats['mean']
    std_dev = stats['std_dev']
    z_scores = [(s - mean) / std_dev for s in scores]
    z_outliers = [scores[i] for i, z in enumerate(z_scores) if abs(z) > 3]

    # Modified Z-score (MAD)
    median = stats['median']
    mad = statistics.median([abs(s - median) for s in scores])
    modified_z_scores = [0.6745 * (s - median) / mad if mad > 0 else 0 for s in scores]
    mad_outliers = [scores[i] for i, z in enumerate(modified_z_scores) if abs(z) > 3.5]

    return {
        'iqr_method': {
            'lower_fence': lower_fence,
            'upper_fence': upper_fence,
            'outlier_count': len(iqr_outliers),
            'outlier_percentage': len(iqr_outliers) / len(scores) * 100,
            'outliers': sorted(iqr_outliers)
        },
        'z_score_method': {
            'outlier_count': len(z_outliers),
            'outlier_percentage': len(z_outliers) / len(scores) * 100,
            'outliers': sorted(z_outliers)
        },
        'mad_method': {
            'mad': mad,
            'outlier_count': len(mad_outliers),
            'outlier_percentage': len(mad_outliers) / len(scores) * 100,
            'outliers': sorted(mad_outliers)
        }
    }


def calibrate_threshold(
    all_scores_stats: Dict[str, Any],
    best_match_stats: Dict[str, Any],
    all_scores: List[float],
    best_match_scores: List[float]
) -> Dict[str, Any]:
    """
    Calibrate anomaly detection threshold.

    Strategy:
    1. Use percentile-based approach for best matches
    2. Consider standard deviations from mean
    3. Validate against business requirements

    Args:
        all_scores_stats: Statistics for all scores
        best_match_stats: Statistics for best match scores
        all_scores: List of all scores
        best_match_scores: List of best match scores

    Returns:
        Dictionary with threshold recommendations
    """
    # Method 1: Percentile-based (5th percentile of best matches)
    percentile_5th = best_match_stats['percentiles']['5th']
    percentile_10th = best_match_stats['percentiles']['10th']

    # Method 2: Mean - 2*StdDev (captures ~95% of normal distribution)
    mean_2sd = best_match_stats['mean'] - (2 * best_match_stats['std_dev'])

    # Method 3: Q1 - 1.5*IQR (standard outlier detection)
    q1 = best_match_stats['percentiles']['25th']
    q3 = best_match_stats['percentiles']['75th']
    iqr = q3 - q1
    iqr_threshold = q1 - 1.5 * iqr

    # Method 4: Median - 2*MAD (robust to outliers)
    median = best_match_stats['median']
    mad = statistics.median([abs(s - median) for s in best_match_scores])
    mad_threshold = median - 2 * mad

    # Recommendation: Use the most conservative (highest) threshold
    # that still catches genuinely poor matches
    recommended_threshold = max(percentile_5th, mean_2sd, iqr_threshold, mad_threshold)

    # Ensure threshold is reasonable (not below 0.3 or above 0.7)
    recommended_threshold = max(0.3, min(0.7, recommended_threshold))

    # Calculate how many matches would be flagged as anomalous
    flagged_all = sum(1 for s in all_scores if s < recommended_threshold)
    flagged_best = sum(1 for s in best_match_scores if s < recommended_threshold)

    return {
        'methods': {
            'percentile_5th': percentile_5th,
            'percentile_10th': percentile_10th,
            'mean_minus_2sd': mean_2sd,
            'iqr_outlier': iqr_threshold,
            'mad_outlier': mad_threshold
        },
        'recommended_threshold': recommended_threshold,
        'threshold_reasoning': 'Maximum of multiple methods for conservative detection',
        'impact': {
            'flagged_from_all_matches': flagged_all,
            'flagged_from_all_matches_pct': flagged_all / len(all_scores) * 100,
            'flagged_from_best_matches': flagged_best,
            'flagged_from_best_matches_pct': flagged_best / len(best_match_scores) * 100
        }
    }


def generate_report(
    stats: Dict[str, Any],
    all_scores: List[float],
    best_match_scores: List[float]
):
    """Generate and display calibration report."""

    logger.info("="*80)
    logger.info("ANOMALY DETECTION CALIBRATION - Phase 1, Task 1.3")
    logger.info("="*80)
    logger.info("")

    logger.info(f"Semantic Weight: {stats['semantic_weight']}")
    logger.info(f"Total Scores Analyzed: {stats['all_scores']['count']}")
    logger.info("")

    logger.info("-"*80)
    logger.info("ALL SCORES DISTRIBUTION")
    logger.info("-"*80)
    s = stats['all_scores']
    logger.info(f"  Count: {s['count']}")
    logger.info(f"  Range: {s['min']:.4f} - {s['max']:.4f}")
    logger.info(f"  Mean: {s['mean']:.4f} ± {s['std_dev']:.4f}")
    logger.info(f"  Median: {s['median']:.4f}")
    logger.info(f"  Percentiles:")
    for pct_name, pct_value in s['percentiles'].items():
        logger.info(f"    {pct_name:6s}: {pct_value:.4f}")
    logger.info("")

    logger.info("-"*80)
    logger.info("BEST MATCH SCORES DISTRIBUTION")
    logger.info("-"*80)
    s = stats['best_match_scores']
    logger.info(f"  Count: {s['count']}")
    logger.info(f"  Range: {s['min']:.4f} - {s['max']:.4f}")
    logger.info(f"  Mean: {s['mean']:.4f} ± {s['std_dev']:.4f}")
    logger.info(f"  Median: {s['median']:.4f}")
    logger.info(f"  Percentiles:")
    for pct_name, pct_value in s['percentiles'].items():
        logger.info(f"    {pct_name:6s}: {pct_value:.4f}")
    logger.info("")

    logger.info("-"*80)
    logger.info("OUTLIER ANALYSIS - All Scores")
    logger.info("-"*80)
    outliers_all = identify_outliers(all_scores, stats['all_scores'])
    for method_name, method_data in outliers_all.items():
        logger.info(f"  {method_name}:")
        logger.info(f"    Outlier count: {method_data['outlier_count']} ({method_data['outlier_percentage']:.1f}%)")
        if method_data['outlier_count'] > 0:
            outlier_samples = method_data['outliers'][:5]
            logger.info(f"    Sample outliers: {[f'{s:.4f}' for s in outlier_samples]}")
    logger.info("")

    logger.info("-"*80)
    logger.info("OUTLIER ANALYSIS - Best Match Scores")
    logger.info("-"*80)
    outliers_best = identify_outliers(best_match_scores, stats['best_match_scores'])
    for method_name, method_data in outliers_best.items():
        logger.info(f"  {method_name}:")
        logger.info(f"    Outlier count: {method_data['outlier_count']} ({method_data['outlier_percentage']:.1f}%)")
        if method_data['outlier_count'] > 0:
            outlier_samples = method_data['outliers'][:5]
            logger.info(f"    Sample outliers: {[f'{s:.4f}' for s in outlier_samples]}")
    logger.info("")

    logger.info("-"*80)
    logger.info("THRESHOLD CALIBRATION")
    logger.info("-"*80)
    threshold_analysis = calibrate_threshold(
        stats['all_scores'],
        stats['best_match_scores'],
        all_scores,
        best_match_scores
    )

    logger.info(f"  Threshold Calculation Methods:")
    for method_name, method_value in threshold_analysis['methods'].items():
        logger.info(f"    {method_name:20s}: {method_value:.4f}")
    logger.info("")
    logger.info(f"  RECOMMENDED THRESHOLD: {threshold_analysis['recommended_threshold']:.4f}")
    logger.info(f"  Reasoning: {threshold_analysis['threshold_reasoning']}")
    logger.info("")
    logger.info(f"  Impact Analysis:")
    logger.info(f"    Flagged from all matches: {threshold_analysis['impact']['flagged_from_all_matches']} ({threshold_analysis['impact']['flagged_from_all_matches_pct']:.1f}%)")
    logger.info(f"    Flagged from best matches: {threshold_analysis['impact']['flagged_from_best_matches']} ({threshold_analysis['impact']['flagged_from_best_matches_pct']:.1f}%)")
    logger.info("")

    logger.info("-"*80)
    logger.info("PERSONA-LEVEL STATISTICS (Top 5 and Bottom 5)")
    logger.info("-"*80)

    # Sort personas by best match score
    persona_stats = sorted(stats['persona_statistics'], key=lambda x: x['best_match_score'], reverse=True)

    logger.info("  Top 5 Best Matches:")
    for i, p in enumerate(persona_stats[:5], 1):
        logger.info(f"    {i}. {p['persona_name']:30s} - Best: {p['best_match_score']:.4f}, Mean: {p['mean_score']:.4f}, Median: {p['median_score']:.4f}")

    logger.info("")
    logger.info("  Bottom 5 Best Matches:")
    for i, p in enumerate(persona_stats[-5:], 1):
        logger.info(f"    {i}. {p['persona_name']:30s} - Best: {p['best_match_score']:.4f}, Mean: {p['mean_score']:.4f}, Median: {p['median_score']:.4f}")

    logger.info("")

    logger.info("="*80)
    logger.info("CALIBRATION SUMMARY")
    logger.info("="*80)
    logger.info(f"✅ Analyzed {stats['all_scores']['count']} total matching scores")
    logger.info(f"✅ Analyzed {stats['best_match_scores']['count']} best match scores")
    logger.info(f"✅ Recommended anomaly threshold: {threshold_analysis['recommended_threshold']:.4f}")
    logger.info("")

    # Recommendations
    logger.info("RECOMMENDATIONS:")
    if threshold_analysis['impact']['flagged_from_best_matches_pct'] < 5:
        logger.info(f"  ✅ Threshold is conservative: only {threshold_analysis['impact']['flagged_from_best_matches_pct']:.1f}% of best matches flagged")
    elif threshold_analysis['impact']['flagged_from_best_matches_pct'] < 10:
        logger.info(f"  ⚠️  Threshold is moderate: {threshold_analysis['impact']['flagged_from_best_matches_pct']:.1f}% of best matches flagged")
    else:
        logger.info(f"  ⚠️  Threshold may be too strict: {threshold_analysis['impact']['flagged_from_best_matches_pct']:.1f}% of best matches flagged")

    if stats['best_match_scores']['mean'] > 0.7:
        logger.info(f"  ✅ Matching quality is high (mean best match score: {stats['best_match_scores']['mean']:.4f})")
    elif stats['best_match_scores']['mean'] > 0.5:
        logger.info(f"  ⚠️  Matching quality is moderate (mean best match score: {stats['best_match_scores']['mean']:.4f})")
    else:
        logger.info(f"  ❌ Matching quality is low (mean best match score: {stats['best_match_scores']['mean']:.4f})")

    logger.info("")
    logger.info("="*80)

    # Save detailed report
    report_path = Path('logs/anomaly_calibration_report.json')
    report_path.parent.mkdir(exist_ok=True)

    report_data = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'semantic_weight': stats['semantic_weight'],
            'total_scores': stats['all_scores']['count'],
            'best_match_count': stats['best_match_scores']['count']
        },
        'distribution': {
            'all_scores': stats['all_scores'],
            'best_match_scores': stats['best_match_scores']
        },
        'outlier_analysis': {
            'all_scores': outliers_all,
            'best_match_scores': outliers_best
        },
        'threshold_calibration': threshold_analysis,
        'persona_statistics': stats['persona_statistics']
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"✓ Detailed report saved to: {report_path}")
    logger.info("")


def main():
    """Main execution."""
    try:
        logger.info("Starting anomaly detection calibration...")
        logger.info("")

        # Load data
        logger.info("Loading personas and health records...")
        personas = load_personas()
        records = load_health_records(limit=None)

        if not personas or not records:
            logger.error("Failed to load data")
            return False

        logger.info("")

        # Analyze distribution with default semantic weight (0.6)
        stats, all_scores, best_match_scores = analyze_score_distribution(
            personas,
            records,
            semantic_weight=0.6
        )

        logger.info("")

        # Generate report
        generate_report(stats, all_scores, best_match_scores)

        return True

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
