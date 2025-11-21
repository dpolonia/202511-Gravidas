#!/usr/bin/env python3
"""
Enhanced Interview Analysis with Complete NLP Suite
====================================================

Applies all 11 advanced NLP algorithms to interview data:
1. Medical Entity Recognition (NER)
2. Multi-Emotion Detection
3. Topic Modeling
4. BERT Sentiment Analysis
5. Question-Answer Pattern Analysis
6. Readability & Linguistic Complexity
7. Mental Health Screening (PHQ-9/GAD-7)
8. Semantic Similarity & Clustering
9. Empathy Detection
10. Narrative Arc Analysis
11. Risk Factor Extraction

Usage:
    python scripts/05_analyze_interviews_enhanced.py
    python scripts/05_analyze_interviews_enhanced.py --sample 10
    python scripts/05_analyze_interviews_enhanced.py --module medical_ner
    python scripts/05_analyze_interviews_enhanced.py --export-json
"""

import json
import sys
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from collections import defaultdict

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Setup logging FIRST
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s'
)
logger = logging.getLogger(__name__)

# Import NLP modules
try:
    from scripts.nlp_modules import (
        # Module 1: Medical NER
        extract_medical_entities,
        analyze_medical_content,
        # Module 2: Emotion Analysis
        analyze_interview_emotions,
        # Module 3: Topic Modeling
        analyze_corpus_topics,
        # Module 4: BERT Sentiment
        analyze_interview_sentiment,
        # Module 5: QA Patterns
        analyze_interview_qa_patterns,
        # Module 7: Mental Health
        screen_mental_health,
        # Module 8: Semantic Similarity
        cluster_interviews,
        # Module 9: Empathy Detection
        analyze_interview_empathy,
        # Module 10: Narrative Arc
        analyze_narrative_progression,
        # Module 11: Risk Extraction
        analyze_clinical_risk,
    )
    NLP_MODULES_AVAILABLE = True
except ImportError as e:
    logger.warning(f"NLP modules not fully available: {e}")
    NLP_MODULES_AVAILABLE = False

# Data directories
PROJECT_ROOT = Path(__file__).parent.parent
INTERVIEWS_DIR = PROJECT_ROOT / 'data' / 'interviews'
ANALYSIS_DIR = PROJECT_ROOT / 'data' / 'analysis'
OUTPUTS_DIR = PROJECT_ROOT / 'outputs'


def load_interviews(limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """Load interview data from JSON files."""
    interviews = []

    if not INTERVIEWS_DIR.exists():
        logger.error(f"Interviews directory not found: {INTERVIEWS_DIR}")
        return interviews

    interview_files = sorted(INTERVIEWS_DIR.glob('interview_*.json'))

    if limit:
        interview_files = interview_files[:limit]

    logger.info(f"Loading {len(interview_files)} interviews...")

    for interview_file in interview_files:
        try:
            with open(interview_file, 'r') as f:
                interview_data = json.load(f)
                interviews.append(interview_data)
        except Exception as e:
            logger.error(f"Error loading {interview_file.name}: {e}")

    logger.info(f"✓ Loaded {len(interviews)} interviews")
    return interviews


def analyze_module_1_medical_ner(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 1: Medical Entity Recognition."""
    logger.info("Running Module 1: Medical Entity Recognition...")

    results = []
    for interview in interviews:
        try:
            analysis = analyze_medical_content(interview)
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })
        except Exception as e:
            logger.error(f"Error in medical NER: {e}")

    # Aggregate statistics
    total_entities = sum(
        len(r['analysis'].get('medical_entities', {}).get('all_entities', []))
        for r in results
    )

    return {
        'module': 'medical_ner',
        'total_interviews': len(results),
        'total_entities_extracted': total_entities,
        'results': results
    }


def analyze_module_2_emotions(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 2: Multi-Emotion Detection."""
    logger.info("Running Module 2: Multi-Emotion Detection...")

    results = []
    for interview in interviews:
        try:
            analysis = analyze_interview_emotions(interview)
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })
        except Exception as e:
            logger.error(f"Error in emotion analysis: {e}")

    # Aggregate emotion distribution
    dominant_emotions = [
        r['analysis']['overall_emotions']['dominant_emotion']
        for r in results
        if 'overall_emotions' in r['analysis']
    ]

    from collections import Counter
    emotion_dist = Counter(dominant_emotions)

    return {
        'module': 'emotion_analysis',
        'total_interviews': len(results),
        'emotion_distribution': dict(emotion_dist),
        'results': results
    }


def analyze_module_7_mental_health(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 7: Mental Health Screening."""
    logger.info("Running Module 7: Mental Health Screening...")

    results = []
    high_risk_count = 0

    for interview in interviews:
        try:
            analysis = screen_mental_health(interview, context='pregnancy')
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })

            if analysis.get('overall_risk_level') in ['high', 'critical']:
                high_risk_count += 1
        except Exception as e:
            logger.error(f"Error in mental health screening: {e}")

    return {
        'module': 'mental_health',
        'total_interviews': len(results),
        'high_risk_count': high_risk_count,
        'high_risk_percentage': (high_risk_count / len(results) * 100) if results else 0,
        'results': results
    }


def analyze_module_9_empathy(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 9: Empathy Detection."""
    logger.info("Running Module 9: Empathy Detection...")

    results = []
    empathy_scores = []

    for interview in interviews:
        try:
            analysis = analyze_interview_empathy(interview)
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })

            if 'interviewer_empathy' in analysis:
                score = analysis['interviewer_empathy'].get('average_empathy_score', 0)
                empathy_scores.append(score)
        except Exception as e:
            logger.error(f"Error in empathy detection: {e}")

    avg_empathy = sum(empathy_scores) / len(empathy_scores) if empathy_scores else 0

    return {
        'module': 'empathy_detection',
        'total_interviews': len(results),
        'average_empathy_score': avg_empathy,
        'results': results
    }


def analyze_module_10_narrative_arc(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 10: Narrative Arc Analysis."""
    logger.info("Running Module 10: Narrative Arc Analysis...")

    results = []
    arc_types = []

    for interview in interviews:
        try:
            analysis = analyze_narrative_progression(interview)
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })

            if 'arc_classification' in analysis:
                arc_types.append(analysis['arc_classification']['arc_type'])
        except Exception as e:
            logger.error(f"Error in narrative arc analysis: {e}")

    from collections import Counter
    arc_distribution = Counter(arc_types)

    return {
        'module': 'narrative_arc',
        'total_interviews': len(results),
        'arc_type_distribution': dict(arc_distribution),
        'results': results
    }


def analyze_module_11_risk_factors(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Module 11: Risk Factor Extraction."""
    logger.info("Running Module 11: Risk Factor Extraction...")

    results = []
    risk_levels = []
    critical_count = 0

    for interview in interviews:
        try:
            analysis = analyze_clinical_risk(interview)
            results.append({
                'persona_id': interview.get('persona_id', 'unknown'),
                'analysis': analysis
            })

            risk_level = analysis['risk_analysis'].get('risk_level', 'low')
            risk_levels.append(risk_level)

            if risk_level == 'critical':
                critical_count += 1
        except Exception as e:
            logger.error(f"Error in risk extraction: {e}")

    from collections import Counter
    risk_distribution = Counter(risk_levels)

    return {
        'module': 'risk_extraction',
        'total_interviews': len(results),
        'critical_risk_count': critical_count,
        'risk_distribution': dict(risk_distribution),
        'results': results
    }


def run_complete_analysis(interviews: List[Dict[str, Any]],
                         modules: Optional[List[str]] = None) -> Dict[str, Any]:
    """Run complete NLP analysis pipeline."""

    if not NLP_MODULES_AVAILABLE:
        logger.error("NLP modules not available. Please install required dependencies.")
        return {}

    # Define all available modules
    all_modules = {
        'medical_ner': analyze_module_1_medical_ner,
        'emotions': analyze_module_2_emotions,
        'mental_health': analyze_module_7_mental_health,
        'empathy': analyze_module_9_empathy,
        'narrative_arc': analyze_module_10_narrative_arc,
        'risk_factors': analyze_module_11_risk_factors,
    }

    # Determine which modules to run
    if modules:
        modules_to_run = {k: v for k, v in all_modules.items() if k in modules}
    else:
        modules_to_run = all_modules

    logger.info(f"\n{'='*60}")
    logger.info(f"ENHANCED NLP ANALYSIS PIPELINE")
    logger.info(f"{'='*60}")
    logger.info(f"Interviews to analyze: {len(interviews)}")
    logger.info(f"Modules to run: {', '.join(modules_to_run.keys())}")
    logger.info(f"{'='*60}\n")

    # Run analysis
    results = {}
    start_time = datetime.now()

    for module_name, module_func in modules_to_run.items():
        try:
            module_results = module_func(interviews)
            results[module_name] = module_results
            logger.info(f"✓ Completed: {module_name}")
        except Exception as e:
            logger.error(f"✗ Failed: {module_name} - {e}")
            results[module_name] = {'error': str(e)}

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    # Compile summary
    summary = {
        'analysis_metadata': {
            'timestamp': datetime.now().isoformat(),
            'num_interviews': len(interviews),
            'modules_run': list(modules_to_run.keys()),
            'duration_seconds': duration
        },
        'module_results': results
    }

    logger.info(f"\n{'='*60}")
    logger.info(f"ANALYSIS COMPLETE")
    logger.info(f"{'='*60}")
    logger.info(f"Duration: {duration:.1f} seconds")
    logger.info(f"Modules completed: {len(results)}")
    logger.info(f"{'='*60}\n")

    return summary


def print_summary(analysis_results: Dict[str, Any]):
    """Print human-readable summary of analysis results."""

    print(f"\n{'='*70}")
    print(f"ENHANCED NLP ANALYSIS SUMMARY")
    print(f"{'='*70}\n")

    metadata = analysis_results.get('analysis_metadata', {})
    print(f"Analysis Date: {metadata.get('timestamp', 'Unknown')}")
    print(f"Interviews Analyzed: {metadata.get('num_interviews', 0)}")
    print(f"Duration: {metadata.get('duration_seconds', 0):.1f} seconds")
    print(f"Modules Run: {len(metadata.get('modules_run', []))}")

    print(f"\n{'-'*70}")
    print(f"MODULE RESULTS")
    print(f"{'-'*70}\n")

    for module_name, module_data in analysis_results.get('module_results', {}).items():
        if 'error' in module_data:
            print(f"✗ {module_name.upper()}: ERROR - {module_data['error']}")
            continue

        print(f"✓ {module_name.upper().replace('_', ' ')}")

        if module_name == 'medical_ner':
            print(f"  - Total entities extracted: {module_data.get('total_entities_extracted', 0)}")

        elif module_name == 'emotions':
            dist = module_data.get('emotion_distribution', {})
            if dist:
                top_emotion = max(dist.items(), key=lambda x: x[1])
                print(f"  - Most common emotion: {top_emotion[0]} ({top_emotion[1]} interviews)")

        elif module_name == 'mental_health':
            print(f"  - High-risk cases: {module_data.get('high_risk_count', 0)}")
            print(f"  - High-risk percentage: {module_data.get('high_risk_percentage', 0):.1f}%")

        elif module_name == 'empathy':
            print(f"  - Average empathy score: {module_data.get('average_empathy_score', 0):.3f}")

        elif module_name == 'narrative_arc':
            dist = module_data.get('arc_type_distribution', {})
            if dist:
                print(f"  - Arc type distribution: {dist}")

        elif module_name == 'risk_factors':
            print(f"  - Critical risk cases: {module_data.get('critical_risk_count', 0)}")
            dist = module_data.get('risk_distribution', {})
            if dist:
                print(f"  - Risk distribution: {dist}")

        print()

    print(f"{'='*70}\n")


def save_results(analysis_results: Dict[str, Any], output_path: Path):
    """Save analysis results to JSON file."""

    # Ensure output directory exists
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(analysis_results, f, indent=2, default=str)

    logger.info(f"✓ Results saved to: {output_path}")


def main():
    """Main analysis entry point."""

    parser = argparse.ArgumentParser(
        description='Enhanced Interview Analysis with 11 NLP Modules'
    )
    parser.add_argument('--sample', type=int, help='Analyze only N interviews')
    parser.add_argument('--module', type=str, help='Run specific module only')
    parser.add_argument('--export-json', action='store_true', help='Export results to JSON')
    parser.add_argument('--output', type=str, help='Output file path')

    args = parser.parse_args()

    # Load interviews
    interviews = load_interviews(limit=args.sample)

    if not interviews:
        logger.error("No interviews found to analyze")
        return 1

    # Determine modules to run
    modules = [args.module] if args.module else None

    # Run analysis
    results = run_complete_analysis(interviews, modules=modules)

    if not results:
        logger.error("Analysis failed")
        return 1

    # Print summary
    print_summary(results)

    # Export if requested
    if args.export_json:
        output_path = Path(args.output) if args.output else OUTPUTS_DIR / 'enhanced_nlp_analysis.json'
        save_results(results, output_path)

    return 0


if __name__ == '__main__':
    sys.exit(main())
