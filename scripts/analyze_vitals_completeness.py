#!/usr/bin/env python3
"""
Analyze FHIR Data Completeness - Vital Signs Extraction

This script analyzes the completeness of vital signs extraction from FHIR records,
with focus on pregnancy-related measurements.

Phase 1, Task 1.2.7 - v1.2.0 Implementation

Purpose:
- Verify vital signs are being extracted from FHIR observations
- Calculate completeness percentages for each vital sign field
- Analyze data quality and distribution
- Identify records with pregnancy-related vitals

Output:
- Console report with completeness statistics
- logs/vitals_completeness_report.json - Detailed analysis data
"""

import json
import logging
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import statistics

# Ensure scripts directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import required modules
try:
    from scripts.utils.fhir_semantic_extractor import build_semantic_tree_from_fhir
except ImportError as e:
    print(f"ERROR: Cannot import required modules: {e}")
    sys.exit(1)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)


def load_and_analyze_vitals(limit: Optional[int] = None) -> Dict[str, Any]:
    """
    Load all FHIR records and analyze vital signs completeness.

    Args:
        limit: Maximum number of records to analyze (None for all)

    Returns:
        Dictionary with completeness statistics
    """
    fhir_dir = Path('synthea/output/fhir')

    if not fhir_dir.exists():
        logger.error(f"FHIR directory not found: {fhir_dir}")
        return {}

    fhir_files = sorted(fhir_dir.glob('*.json'))

    if limit:
        fhir_files = fhir_files[:limit]

    # Statistics collectors
    stats = {
        'total_records': 0,
        'records_with_vitals': {
            'gestational_age': 0,
            'bp_systolic': 0,
            'bp_diastolic': 0,
            'fetal_heart_rate': 0,
            'maternal_weight': 0,
            'maternal_height': 0,
            'maternal_bmi': 0,
            'weight_gain': 0
        },
        'value_ranges': {
            'gestational_age': [],
            'bp_systolic': [],
            'bp_diastolic': [],
            'fetal_heart_rate': [],
            'maternal_weight': [],
            'maternal_height': [],
            'maternal_bmi': [],
            'weight_gain': []
        },
        'pregnancy_records': 0,
        'errors': []
    }

    logger.info(f"Analyzing {len(fhir_files)} FHIR files...")
    logger.info("")

    for idx, fhir_file in enumerate(fhir_files, 1):
        # Skip metadata files
        if 'hospitalInformation' in fhir_file.name or 'practitionerInformation' in fhir_file.name:
            continue

        try:
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
                        from datetime import datetime
                        birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
                        age = (datetime.now() - birth_date).days // 365
                    break

            # Build semantic tree (includes vital signs extraction)
            semantic_tree = build_semantic_tree_from_fhir(fhir_data, patient_id, age)

            stats['total_records'] += 1

            # Extract pregnancy profile vitals
            pregnancy_profile = semantic_tree.pregnancy_profile

            # Check if this is a pregnancy-related record
            if pregnancy_profile.has_pregnancy_codes or pregnancy_profile.gestational_age_weeks is not None:
                stats['pregnancy_records'] += 1

            # Track completeness for each vital
            if pregnancy_profile.gestational_age_weeks is not None:
                stats['records_with_vitals']['gestational_age'] += 1
                stats['value_ranges']['gestational_age'].append(pregnancy_profile.gestational_age_weeks)

            if pregnancy_profile.blood_pressure_systolic is not None:
                stats['records_with_vitals']['bp_systolic'] += 1
                stats['value_ranges']['bp_systolic'].append(pregnancy_profile.blood_pressure_systolic)

            if pregnancy_profile.blood_pressure_diastolic is not None:
                stats['records_with_vitals']['bp_diastolic'] += 1
                stats['value_ranges']['bp_diastolic'].append(pregnancy_profile.blood_pressure_diastolic)

            if pregnancy_profile.fetal_heart_rate is not None:
                stats['records_with_vitals']['fetal_heart_rate'] += 1
                stats['value_ranges']['fetal_heart_rate'].append(pregnancy_profile.fetal_heart_rate)

            if pregnancy_profile.maternal_weight_kg is not None:
                stats['records_with_vitals']['maternal_weight'] += 1
                stats['value_ranges']['maternal_weight'].append(pregnancy_profile.maternal_weight_kg)

            if pregnancy_profile.maternal_height_cm is not None:
                stats['records_with_vitals']['maternal_height'] += 1
                stats['value_ranges']['maternal_height'].append(pregnancy_profile.maternal_height_cm)

            if pregnancy_profile.maternal_bmi is not None:
                stats['records_with_vitals']['maternal_bmi'] += 1
                stats['value_ranges']['maternal_bmi'].append(pregnancy_profile.maternal_bmi)

            if pregnancy_profile.weight_gain_kg is not None:
                stats['records_with_vitals']['weight_gain'] += 1
                stats['value_ranges']['weight_gain'].append(pregnancy_profile.weight_gain_kg)

            # Progress indicator
            if idx % 10 == 0:
                logger.info(f"  Processed {idx}/{len(fhir_files)} files...")

        except Exception as e:
            logger.warning(f"Error processing {fhir_file.name}: {e}")
            stats['errors'].append({
                'file': fhir_file.name,
                'error': str(e)
            })
            continue

    logger.info("")
    logger.info(f"✓ Analysis complete: {stats['total_records']} records processed")

    return stats


def calculate_statistics(values: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a list of values."""
    if not values:
        return {
            'count': 0,
            'min': None,
            'max': None,
            'mean': None,
            'median': None,
            'std_dev': None
        }

    return {
        'count': len(values),
        'min': min(values),
        'max': max(values),
        'mean': statistics.mean(values),
        'median': statistics.median(values),
        'std_dev': statistics.stdev(values) if len(values) > 1 else 0.0
    }


def generate_report(stats: Dict[str, Any]):
    """Generate and display completeness report."""

    logger.info("="*80)
    logger.info("VITAL SIGNS COMPLETENESS ANALYSIS - Phase 1, Task 1.2.7")
    logger.info("="*80)
    logger.info("")

    total = stats['total_records']

    if total == 0:
        logger.error("No records analyzed")
        return

    logger.info(f"Total Records Analyzed: {total}")
    logger.info(f"Pregnancy-Related Records: {stats['pregnancy_records']} ({stats['pregnancy_records']/total*100:.1f}%)")
    logger.info("")

    logger.info("-"*80)
    logger.info("VITAL SIGNS COMPLETENESS")
    logger.info("-"*80)

    # Completeness percentages
    vital_names = {
        'gestational_age': 'Gestational Age',
        'bp_systolic': 'Blood Pressure (Systolic)',
        'bp_diastolic': 'Blood Pressure (Diastolic)',
        'fetal_heart_rate': 'Fetal Heart Rate',
        'maternal_weight': 'Maternal Weight',
        'maternal_height': 'Maternal Height',
        'maternal_bmi': 'Maternal BMI',
        'weight_gain': 'Weight Gain'
    }

    for vital_key, vital_label in vital_names.items():
        count = stats['records_with_vitals'][vital_key]
        percentage = (count / total * 100) if total > 0 else 0
        logger.info(f"{vital_label:30s}: {count:3d}/{total} ({percentage:5.1f}%)")

    logger.info("")
    logger.info("-"*80)
    logger.info("VALUE STATISTICS")
    logger.info("-"*80)

    for vital_key, vital_label in vital_names.items():
        values = stats['value_ranges'][vital_key]
        stat = calculate_statistics(values)

        if stat['count'] > 0:
            logger.info(f"{vital_label}:")
            logger.info(f"  Count: {stat['count']}")
            logger.info(f"  Range: {stat['min']:.2f} - {stat['max']:.2f}")
            logger.info(f"  Mean: {stat['mean']:.2f} ± {stat['std_dev']:.2f}")
            logger.info(f"  Median: {stat['median']:.2f}")
            logger.info("")

    if stats['errors']:
        logger.info("-"*80)
        logger.info(f"ERRORS: {len(stats['errors'])} files had errors")
        logger.info("-"*80)
        for error in stats['errors'][:5]:  # Show first 5
            logger.info(f"  {error['file']}: {error['error']}")
        if len(stats['errors']) > 5:
            logger.info(f"  ... and {len(stats['errors']) - 5} more")
        logger.info("")

    logger.info("="*80)
    logger.info("SUMMARY")
    logger.info("="*80)

    # Key findings
    if stats['pregnancy_records'] > 0:
        logger.info(f"✅ Found {stats['pregnancy_records']} pregnancy-related records")
    else:
        logger.info("⚠️  No pregnancy-related records found")

    # Check if general vitals are being extracted
    general_vitals = ['bp_systolic', 'bp_diastolic', 'maternal_weight', 'maternal_height', 'maternal_bmi']
    general_coverage = sum(stats['records_with_vitals'][v] for v in general_vitals) / (len(general_vitals) * total) * 100

    if general_coverage > 80:
        logger.info(f"✅ General vitals extraction: {general_coverage:.1f}% average coverage")
    elif general_coverage > 50:
        logger.info(f"⚠️  General vitals extraction: {general_coverage:.1f}% average coverage (moderate)")
    else:
        logger.info(f"❌ General vitals extraction: {general_coverage:.1f}% average coverage (low)")

    # Check pregnancy-specific vitals
    pregnancy_vitals = ['gestational_age', 'fetal_heart_rate']
    pregnancy_coverage = sum(stats['records_with_vitals'][v] for v in pregnancy_vitals) / (len(pregnancy_vitals) * total) * 100

    if pregnancy_coverage > 10:
        logger.info(f"✅ Pregnancy-specific vitals: {pregnancy_coverage:.1f}% average coverage")
    else:
        logger.info(f"⚠️  Pregnancy-specific vitals: {pregnancy_coverage:.1f}% average coverage (expected - not all patients are pregnant)")

    logger.info("")
    logger.info("="*80)

    # Save detailed report
    report_path = Path('logs/vitals_completeness_report.json')
    report_path.parent.mkdir(exist_ok=True)

    # Prepare report data
    report_data = {
        'metadata': {
            'timestamp': str(Path('logs/semantic_tree_failures_report.json').stat().st_mtime),
            'total_records': total,
            'pregnancy_records': stats['pregnancy_records']
        },
        'completeness': {
            vital_key: {
                'count': stats['records_with_vitals'][vital_key],
                'percentage': (stats['records_with_vitals'][vital_key] / total * 100) if total > 0 else 0
            }
            for vital_key in vital_names.keys()
        },
        'statistics': {
            vital_key: calculate_statistics(stats['value_ranges'][vital_key])
            for vital_key in vital_names.keys()
        },
        'errors': stats['errors']
    }

    with open(report_path, 'w') as f:
        json.dump(report_data, f, indent=2)

    logger.info(f"✓ Detailed report saved to: {report_path}")
    logger.info("")


def main():
    """Main execution."""
    try:
        # Analyze all records
        stats = load_and_analyze_vitals(limit=None)

        # Generate report
        generate_report(stats)

        sys.exit(0)

    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
