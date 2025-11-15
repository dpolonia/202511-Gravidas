#!/usr/bin/env python3
"""
Debug Semantic Tree Generation Failures

This script analyzes semantic tree generation across all Synthea FHIR health records
to identify failure patterns and missing FHIR fields.

Phase 1, Task 1.1.1 - v1.2.0 Implementation

Purpose:
- Load all FHIR health records from Synthea output
- Attempt to build semantic tree for each record
- Log all exceptions with full stack traces
- Identify which FHIR fields are missing most often
- Generate detailed failure report

Output:
- logs/semantic_tree_failures_report.json - Structured failure analysis
- logs/debug_semantic_trees.log - Detailed execution log
"""

import json
import logging
import sys
import traceback
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from collections import Counter, defaultdict
from datetime import datetime

# Ensure scripts directory is in path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import semantic tree building functions
try:
    from scripts.utils.fhir_semantic_extractor import build_semantic_tree_from_fhir
except ImportError:
    print("ERROR: Cannot import fhir_semantic_extractor. Make sure scripts/utils/fhir_semantic_extractor.py exists.")
    sys.exit(1)

# Create logs directory
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/debug_semantic_trees.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def extract_patient_info_from_fhir(fhir_data: Dict[str, Any]) -> Tuple[Optional[str], Optional[int]]:
    """
    Extract patient ID and age from FHIR bundle.

    Args:
        fhir_data: FHIR bundle dictionary

    Returns:
        Tuple of (patient_id, age)
    """
    patient_id = None
    age = None

    try:
        entries = fhir_data.get('entry', [])

        for entry in entries:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType', '')

            if resource_type == 'Patient':
                patient_id = resource.get('id', 'unknown')

                # Calculate age from birthDate
                birth_date_str = resource.get('birthDate')
                if birth_date_str:
                    from datetime import datetime
                    birth_date = datetime.fromisoformat(birth_date_str.replace('Z', '+00:00'))
                    age = (datetime.now() - birth_date).days // 365

                break

    except Exception as e:
        logger.warning(f"Error extracting patient info: {e}")

    return patient_id, age


def analyze_fhir_bundle_structure(fhir_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Analyze FHIR bundle structure to identify available resources and fields.

    Args:
        fhir_data: FHIR bundle dictionary

    Returns:
        Dictionary with structural analysis
    """
    analysis = {
        'has_entries': False,
        'entry_count': 0,
        'resource_types': Counter(),
        'has_patient': False,
        'has_conditions': False,
        'has_medications': False,
        'has_encounters': False,
        'has_observations': False,
        'condition_count': 0,
        'medication_count': 0,
        'encounter_count': 0,
        'observation_count': 0,
        'observation_types': Counter(),
        'missing_fields': defaultdict(list)
    }

    try:
        entries = fhir_data.get('entry', [])

        if not entries:
            analysis['missing_fields']['root'].append('entry field missing or empty')
            return analysis

        analysis['has_entries'] = True
        analysis['entry_count'] = len(entries)

        for entry in entries:
            resource = entry.get('resource', {})
            resource_type = resource.get('resourceType', 'Unknown')

            analysis['resource_types'][resource_type] += 1

            if resource_type == 'Patient':
                analysis['has_patient'] = True
                # Check for required patient fields
                if not resource.get('birthDate'):
                    analysis['missing_fields']['Patient'].append('birthDate')
                if not resource.get('gender'):
                    analysis['missing_fields']['Patient'].append('gender')

            elif resource_type == 'Condition':
                analysis['has_conditions'] = True
                analysis['condition_count'] += 1
                # Check for required condition fields
                if not resource.get('code', {}).get('coding'):
                    analysis['missing_fields']['Condition'].append('code.coding')

            elif resource_type == 'MedicationRequest':
                analysis['has_medications'] = True
                analysis['medication_count'] += 1
                # Check for required medication fields
                if not resource.get('medicationCodeableConcept', {}).get('coding'):
                    analysis['missing_fields']['MedicationRequest'].append('medicationCodeableConcept.coding')

            elif resource_type == 'Encounter':
                analysis['has_encounters'] = True
                analysis['encounter_count'] += 1

            elif resource_type == 'Observation':
                analysis['has_observations'] = True
                analysis['observation_count'] += 1

                # Identify observation type
                coding = resource.get('code', {}).get('coding', [])
                if coding:
                    obs_code = coding[0].get('code', 'unknown')
                    obs_display = coding[0].get('display', 'unknown')
                    analysis['observation_types'][f"{obs_code}: {obs_display}"] += 1

    except Exception as e:
        logger.error(f"Error analyzing FHIR bundle structure: {e}")
        analysis['error'] = str(e)

    return analysis


def attempt_semantic_tree_build(
    fhir_file: Path
) -> Dict[str, Any]:
    """
    Attempt to build semantic tree from a FHIR file and capture detailed diagnostics.

    Args:
        fhir_file: Path to FHIR JSON file

    Returns:
        Dictionary with attempt results
    """
    result = {
        'file': str(fhir_file.name),
        'success': False,
        'patient_id': None,
        'age': None,
        'error_type': None,
        'error_message': None,
        'stack_trace': None,
        'bundle_analysis': None,
        'semantic_tree': None
    }

    try:
        # Load FHIR data
        logger.debug(f"Loading FHIR file: {fhir_file.name}")

        with open(fhir_file, 'r') as f:
            fhir_data = json.load(f)

        # Analyze bundle structure
        result['bundle_analysis'] = analyze_fhir_bundle_structure(fhir_data)

        # Extract patient info
        patient_id, age = extract_patient_info_from_fhir(fhir_data)
        result['patient_id'] = patient_id or fhir_file.stem
        result['age'] = age or 30  # Default age if missing

        logger.debug(f"Patient ID: {result['patient_id']}, Age: {result['age']}")

        # Attempt to build semantic tree
        logger.debug(f"Building semantic tree for {result['patient_id']}")

        semantic_tree = build_semantic_tree_from_fhir(
            fhir_data=fhir_data,
            patient_id=result['patient_id'],
            age=result['age']
        )

        # If we got here, success!
        result['success'] = True
        result['semantic_tree'] = {
            'patient_id': semantic_tree.patient_id,
            'age': semantic_tree.age,
            'condition_count': len(semantic_tree.conditions),
            'chronic_disease_count': semantic_tree.chronic_disease_count,
            'overall_health_status': semantic_tree.overall_health_status,
            'pregnancy_profile': {
                'has_pregnancy_codes': semantic_tree.pregnancy_profile.has_pregnancy_codes,
                'pregnancy_stage': semantic_tree.pregnancy_profile.pregnancy_stage,
                'risk_level': semantic_tree.pregnancy_profile.risk_level
            }
        }

        logger.info(f"✓ SUCCESS: {result['patient_id']} - Semantic tree built successfully")

    except Exception as e:
        # Capture full exception details
        result['error_type'] = type(e).__name__
        result['error_message'] = str(e)
        result['stack_trace'] = traceback.format_exc()

        logger.error(f"✗ FAILED: {fhir_file.name}")
        logger.error(f"  Error Type: {result['error_type']}")
        logger.error(f"  Error Message: {result['error_message']}")
        logger.debug(f"  Stack Trace:\n{result['stack_trace']}")

    return result


def analyze_failure_patterns(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze patterns across all failures to identify common issues.

    Args:
        results: List of attempt results

    Returns:
        Dictionary with failure pattern analysis
    """
    analysis = {
        'total_records': len(results),
        'successful': 0,
        'failed': 0,
        'success_rate': 0.0,
        'error_types': Counter(),
        'error_messages': Counter(),
        'missing_resources': {
            'no_patient': 0,
            'no_conditions': 0,
            'no_medications': 0,
            'no_encounters': 0,
            'no_observations': 0
        },
        'bundle_statistics': {
            'avg_entry_count': 0,
            'avg_condition_count': 0,
            'avg_medication_count': 0,
            'avg_encounter_count': 0,
            'avg_observation_count': 0
        },
        'observation_type_counts': Counter(),
        'failed_record_files': [],
        'successful_record_files': []
    }

    successful_results = []
    failed_results = []

    for result in results:
        if result['success']:
            analysis['successful'] += 1
            successful_results.append(result)
            analysis['successful_record_files'].append(result['file'])
        else:
            analysis['failed'] += 1
            failed_results.append(result)
            analysis['failed_record_files'].append(result['file'])

            if result['error_type']:
                analysis['error_types'][result['error_type']] += 1

            if result['error_message']:
                # Truncate long error messages for counting
                msg = result['error_message'][:200]
                analysis['error_messages'][msg] += 1

        # Analyze bundle structure
        if result['bundle_analysis']:
            bundle = result['bundle_analysis']

            if not bundle.get('has_patient'):
                analysis['missing_resources']['no_patient'] += 1
            if not bundle.get('has_conditions'):
                analysis['missing_resources']['no_conditions'] += 1
            if not bundle.get('has_medications'):
                analysis['missing_resources']['no_medications'] += 1
            if not bundle.get('has_encounters'):
                analysis['missing_resources']['no_encounters'] += 1
            if not bundle.get('has_observations'):
                analysis['missing_resources']['no_observations'] += 1

            # Update observation type counts
            for obs_type, count in bundle.get('observation_types', {}).items():
                analysis['observation_type_counts'][obs_type] += count

    # Calculate success rate
    if analysis['total_records'] > 0:
        analysis['success_rate'] = (analysis['successful'] / analysis['total_records']) * 100

    # Calculate bundle statistics (from all records)
    entry_counts = []
    condition_counts = []
    medication_counts = []
    encounter_counts = []
    observation_counts = []

    for result in results:
        if result['bundle_analysis']:
            b = result['bundle_analysis']
            entry_counts.append(b.get('entry_count', 0))
            condition_counts.append(b.get('condition_count', 0))
            medication_counts.append(b.get('medication_count', 0))
            encounter_counts.append(b.get('encounter_count', 0))
            observation_counts.append(b.get('observation_count', 0))

    if entry_counts:
        analysis['bundle_statistics']['avg_entry_count'] = sum(entry_counts) / len(entry_counts)
        analysis['bundle_statistics']['avg_condition_count'] = sum(condition_counts) / len(condition_counts)
        analysis['bundle_statistics']['avg_medication_count'] = sum(medication_counts) / len(medication_counts)
        analysis['bundle_statistics']['avg_encounter_count'] = sum(encounter_counts) / len(encounter_counts)
        analysis['bundle_statistics']['avg_observation_count'] = sum(observation_counts) / len(observation_counts)

    return analysis


def generate_recommendations(analysis: Dict[str, Any]) -> List[str]:
    """
    Generate actionable recommendations based on failure analysis.

    Args:
        analysis: Failure pattern analysis

    Returns:
        List of recommendation strings
    """
    recommendations = []

    # Success rate recommendations
    if analysis['success_rate'] < 50:
        recommendations.append(
            "🔴 CRITICAL: Success rate below 50%. Major issues with FHIR parsing. "
            "Review error types and implement robust null-checking immediately."
        )
    elif analysis['success_rate'] < 95:
        recommendations.append(
            "🟡 WARNING: Success rate below 95% target. Additional error handling needed."
        )
    else:
        recommendations.append(
            "✅ SUCCESS: Success rate meets ≥95% target. Semantic tree generation is robust."
        )

    # Missing resources recommendations
    if analysis['missing_resources']['no_patient'] > 0:
        recommendations.append(
            f"⚠️  {analysis['missing_resources']['no_patient']} records missing Patient resource. "
            "This is unusual for Synthea output. Verify FHIR files are valid."
        )

    if analysis['missing_resources']['no_observations'] > analysis['total_records'] * 0.5:
        recommendations.append(
            f"⚠️  {analysis['missing_resources']['no_observations']} records have no Observations. "
            "Vital signs (BP, gestational age, fetal heart rate) will be missing. "
            "Consider re-running Synthea with pregnancy observation modules enabled."
        )

    # Error type recommendations
    top_errors = analysis['error_types'].most_common(3)
    for error_type, count in top_errors:
        pct = (count / analysis['failed']) * 100 if analysis['failed'] > 0 else 0

        if error_type == 'NoneType':
            recommendations.append(
                f"🔧 FIX: {error_type} errors ({count} occurrences, {pct:.1f}% of failures). "
                "Implement null-checking in FHIR field access (Task 1.1.2)."
            )
        elif error_type == 'KeyError':
            recommendations.append(
                f"🔧 FIX: {error_type} errors ({count} occurrences, {pct:.1f}% of failures). "
                "Add try-except blocks around dictionary access (Task 1.1.2)."
            )
        elif error_type == 'IndexError':
            recommendations.append(
                f"🔧 FIX: {error_type} errors ({count} occurrences, {pct:.1f}% of failures). "
                "Check list lengths before accessing indices (Task 1.1.2)."
            )
        else:
            recommendations.append(
                f"🔍 INVESTIGATE: {error_type} errors ({count} occurrences, {pct:.1f}% of failures). "
                "Review stack traces in failure details."
            )

    return recommendations


def main():
    """Main execution function."""
    logger.info("="*80)
    logger.info("Semantic Tree Generation Debug Analysis - Phase 1, Task 1.1.1")
    logger.info("="*80)

    # Find all FHIR files
    fhir_dir = Path('synthea/output/fhir')

    if not fhir_dir.exists():
        logger.error(f"FHIR directory not found: {fhir_dir}")
        logger.error("Please ensure Synthea has generated FHIR output.")
        sys.exit(1)

    fhir_files = sorted(fhir_dir.glob('*.json'))

    if not fhir_files:
        logger.error(f"No FHIR JSON files found in {fhir_dir}")
        sys.exit(1)

    logger.info(f"Found {len(fhir_files)} FHIR files to analyze")
    logger.info("")

    # Process all files
    results = []

    for idx, fhir_file in enumerate(fhir_files, 1):
        logger.info(f"Processing {idx}/{len(fhir_files)}: {fhir_file.name}")

        result = attempt_semantic_tree_build(fhir_file)
        results.append(result)

        # Progress update every 10 files
        if idx % 10 == 0:
            successes = sum(1 for r in results if r['success'])
            logger.info(f"  Progress: {successes}/{idx} successful ({successes/idx*100:.1f}%)")
            logger.info("")

    logger.info("="*80)
    logger.info("Analysis Complete - Generating Report")
    logger.info("="*80)

    # Analyze failure patterns
    analysis = analyze_failure_patterns(results)

    # Generate recommendations
    recommendations = generate_recommendations(analysis)

    # Create comprehensive report
    report = {
        'metadata': {
            'timestamp': datetime.now().isoformat(),
            'fhir_directory': str(fhir_dir),
            'total_files_analyzed': len(fhir_files),
            'phase': 'Phase 1, Task 1.1.1',
            'version': 'v1.2.0'
        },
        'summary': {
            'total_records': analysis['total_records'],
            'successful': analysis['successful'],
            'failed': analysis['failed'],
            'success_rate_percent': round(analysis['success_rate'], 2)
        },
        'failure_analysis': {
            'error_types': dict(analysis['error_types']),
            'top_error_messages': dict(analysis['error_messages'].most_common(10)),
            'missing_resources': analysis['missing_resources']
        },
        'bundle_statistics': analysis['bundle_statistics'],
        'observation_analysis': {
            'total_observation_types': len(analysis['observation_type_counts']),
            'top_observation_types': dict(analysis['observation_type_counts'].most_common(20))
        },
        'recommendations': recommendations,
        'failed_records': analysis['failed_record_files'],
        'successful_records': analysis['successful_record_files'][:10],  # First 10 successes
        'detailed_failures': [
            {
                'file': r['file'],
                'patient_id': r['patient_id'],
                'error_type': r['error_type'],
                'error_message': r['error_message'],
                'bundle_has_patient': r['bundle_analysis'].get('has_patient') if r['bundle_analysis'] else None,
                'bundle_has_observations': r['bundle_analysis'].get('has_observations') if r['bundle_analysis'] else None
            }
            for r in results if not r['success']
        ][:50]  # First 50 detailed failures
    }

    # Save full report
    report_file = Path('logs/semantic_tree_failures_report.json')
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)

    logger.info(f"✓ Full report saved to: {report_file}")

    # Print summary to console
    print("\n" + "="*80)
    print("SEMANTIC TREE GENERATION - DEBUG SUMMARY")
    print("="*80)
    print(f"\nTotal Records Analyzed: {analysis['total_records']}")
    print(f"Successful: {analysis['successful']} ({analysis['success_rate']:.1f}%)")
    print(f"Failed: {analysis['failed']} ({100-analysis['success_rate']:.1f}%)")
    print(f"\nTarget Success Rate: ≥95%")

    if analysis['success_rate'] >= 95:
        print("Status: ✅ TARGET MET")
    elif analysis['success_rate'] >= 80:
        print("Status: 🟡 NEEDS IMPROVEMENT")
    else:
        print("Status: 🔴 CRITICAL - MAJOR FIXES NEEDED")

    print("\n" + "-"*80)
    print("TOP ERROR TYPES:")
    print("-"*80)
    for error_type, count in analysis['error_types'].most_common(5):
        pct = (count / analysis['failed']) * 100 if analysis['failed'] > 0 else 0
        print(f"  {error_type}: {count} occurrences ({pct:.1f}% of failures)")

    print("\n" + "-"*80)
    print("MISSING RESOURCES:")
    print("-"*80)
    for resource, count in analysis['missing_resources'].items():
        if count > 0:
            pct = (count / analysis['total_records']) * 100
            print(f"  {resource}: {count} records ({pct:.1f}%)")

    print("\n" + "-"*80)
    print("RECOMMENDATIONS:")
    print("-"*80)
    for idx, rec in enumerate(recommendations, 1):
        print(f"\n{idx}. {rec}")

    print("\n" + "="*80)
    print(f"Detailed report: {report_file}")
    print(f"Full log: logs/debug_semantic_trees.log")
    print("="*80)

    # Return exit code based on success rate
    if analysis['success_rate'] >= 95:
        return 0
    else:
        return 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except Exception as e:
        logger.error(f"FATAL ERROR: {e}")
        logger.error(traceback.format_exc())
        sys.exit(1)
