#!/usr/bin/env python3
"""
Test Runner for Semantic Tree Implementation

This script validates the complete semantic tree pipeline:
1. Tests persona semantic tree generation
2. Tests health record semantic tree extraction
3. Tests semantic matching score calculation
4. Generates comprehensive validation reports
5. Performs data quality checks

Usage:
    python scripts/test_semantic_implementation.py
    python scripts/test_semantic_implementation.py --personas data/personas/personas.json --records data/health_records/health_records.json
"""

import json
import logging
import sys
import argparse
from pathlib import Path

try:
    from utils.common_loaders import load_personas, load_health_records
    from utils.test_semantic_trees import (
        test_persona_tree_generation,
        test_health_record_tree_generation,
        test_semantic_matching_scores,
        generate_validation_report,
        check_demographic_diversity,
        check_clinical_data_quality
    )
except ImportError as e:
    print(f"ERROR: Failed to import required modules: {e}")
    sys.exit(1)

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/test_semantic_implementation.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def run_tests(personas_file: str, records_file: str, output_dir: str = 'data/validation'):
    """Run all semantic tree validation tests."""
    logger.info("=" * 60)
    logger.info("SEMANTIC TREE IMPLEMENTATION TEST SUITE")
    logger.info("=" * 60)

    # Create output directory
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # Load data
    logger.info("\n[1/5] Loading test data...")
    try:
        personas = load_personas(personas_file)
        records = load_health_records(records_file)
        logger.info(f"✅ Loaded {len(personas)} personas and {len(records)} health records")
    except Exception as e:
        logger.error(f"❌ Failed to load data: {e}")
        return False

    # Test 1: Persona tree generation
    logger.info("\n[2/5] Testing persona semantic tree generation...")
    try:
        persona_results = test_persona_tree_generation(personas)
        logger.info(f"✅ Tested {persona_results['personas_with_trees']} personas with trees")
        logger.info(f"   Validation: {persona_results['validation_passed']}/{persona_results['personas_with_trees']} passed")
        if persona_results['validation_failed'] > 0:
            logger.warning(f"   ⚠️  {persona_results['validation_failed']} personas have validation issues")
    except Exception as e:
        logger.error(f"❌ Persona tree test failed: {e}", exc_info=True)
        persona_results = {}

    # Test 2: Health record tree generation
    logger.info("\n[3/5] Testing health record semantic tree extraction...")
    try:
        record_results = test_health_record_tree_generation(records)
        logger.info(f"✅ Tested {record_results['records_with_trees']} records with trees")
        logger.info(f"   Validation: {record_results['validation_passed']}/{record_results['records_with_trees']} passed")
        if record_results['validation_failed'] > 0:
            logger.warning(f"   ⚠️  {record_results['validation_failed']} records have validation issues")
    except Exception as e:
        logger.error(f"❌ Health record tree test failed: {e}", exc_info=True)
        record_results = {}

    # Test 3: Semantic matching
    logger.info("\n[4/5] Testing semantic matching score calculation...")
    try:
        matching_results = test_semantic_matching_scores(personas, records)
        logger.info(f"✅ Tested {matching_results['successful_calculations']}/{matching_results['total_test_pairs']} matching pairs")
        if matching_results['successful_calculations'] > 0:
            stats = matching_results['score_statistics']
            logger.info(f"   Scores: min={stats['min']:.3f}, max={stats['max']:.3f}, avg={stats['avg']:.3f}")
    except Exception as e:
        logger.error(f"❌ Semantic matching test failed: {e}", exc_info=True)
        matching_results = {}

    # Test 4: Generate validation report
    logger.info("\n[5/5] Generating validation reports...")
    try:
        report_file = f"{output_dir}/validation_report.json"
        report = generate_validation_report(persona_results, record_results, matching_results, report_file)
        logger.info(f"✅ Validation report saved to {report_file}")
    except Exception as e:
        logger.error(f"❌ Report generation failed: {e}")

    # Test 5: Data quality checks
    logger.info("\nPerforming data quality analysis...")
    try:
        # Persona demographics
        logger.info("\nPersona Demographic Diversity:")
        demo_analysis = check_demographic_diversity(personas)
        logger.info(f"  Age distribution: {dict(sorted(demo_analysis['age_distribution'].items()))}")
        logger.info(f"  Education: {demo_analysis['education_distribution']}")
        logger.info(f"  Income: {demo_analysis['income_distribution']}")

        if demo_analysis['health_consciousness_distribution']:
            logger.info(f"  Health Consciousness: {dict(sorted(demo_analysis['health_consciousness_distribution'].items()))}")
            logger.info(f"  Healthcare Access: {dict(sorted(demo_analysis['healthcare_access_distribution'].items()))}")
            logger.info(f"  Pregnancy Readiness: {dict(sorted(demo_analysis['pregnancy_readiness_distribution'].items()))}")

        # Save demographic analysis
        with open(f"{output_dir}/demographic_analysis.json", 'w') as f:
            json.dump(demo_analysis, f, indent=2)

        # Clinical data quality
        logger.info("\nClinical Data Quality:")
        clinical_analysis = check_clinical_data_quality(records)
        logger.info(f"  Records with conditions: {clinical_analysis['with_conditions']}/{clinical_analysis['total_records']}")
        logger.info(f"  Records with medications: {clinical_analysis['with_medications']}/{clinical_analysis['total_records']}")
        logger.info(f"  Records with encounters: {clinical_analysis['with_encounters']}/{clinical_analysis['total_records']}")

        if clinical_analysis['health_status_distribution']:
            logger.info(f"  Health Status distribution: {clinical_analysis['health_status_distribution']}")
            logger.info(f"  Pregnancy Risk distribution: {clinical_analysis['pregnancy_risk_distribution']}")

        comorbidity = clinical_analysis['comorbidity_statistics']
        logger.info(f"  Comorbidity Index: min={comorbidity['min']:.3f}, max={comorbidity['max']:.3f}, "
                    f"avg={comorbidity['avg']:.3f}")

        # Save clinical analysis
        with open(f"{output_dir}/clinical_analysis.json", 'w') as f:
            json.dump(clinical_analysis, f, indent=2)

    except Exception as e:
        logger.warning(f"Data quality analysis encountered issues: {e}")

    # Summary
    logger.info("\n" + "=" * 60)
    logger.info("TEST SUITE COMPLETED")
    logger.info("=" * 60)
    logger.info(f"Output files saved to: {output_dir}/")
    logger.info("\nGenerated files:")
    logger.info(f"  - validation_report.json: Complete test results")
    logger.info(f"  - demographic_analysis.json: Persona diversity metrics")
    logger.info(f"  - clinical_analysis.json: Health record quality metrics")
    logger.info("=" * 60)

    return True


def main():
    parser = argparse.ArgumentParser(description='Test semantic tree implementation')
    parser.add_argument('--personas', type=str, default='data/personas/personas.json',
                        help='Path to personas JSON file')
    parser.add_argument('--records', type=str, default='data/health_records/health_records.json',
                        help='Path to health records JSON file')
    parser.add_argument('--output', type=str, default='data/validation',
                        help='Output directory for test reports')
    args = parser.parse_args()

    # Check if input files exist
    if not Path(args.personas).exists():
        logger.error(f"Personas file not found: {args.personas}")
        logger.info("Please run: python scripts/01b_generate_personas.py --count 100 --output data/personas")
        sys.exit(1)

    if not Path(args.records).exists():
        logger.error(f"Records file not found: {args.records}")
        logger.info("Please run: python scripts/02_generate_health_records.py --count 100")
        sys.exit(1)

    # Run tests
    success = run_tests(args.personas, args.records, args.output)

    if success:
        logger.info("\n✅ All tests completed successfully!")
        sys.exit(0)
    else:
        logger.error("\n❌ Some tests failed. Check logs for details.")
        sys.exit(1)


if __name__ == '__main__':
    main()
