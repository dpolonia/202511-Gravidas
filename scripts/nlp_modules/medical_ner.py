"""
Medical Entity Recognition Module
===================================

Extracts medical entities (conditions, symptoms, medications, procedures)
from interview transcripts using scispaCy.

Capability #1 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)

# Try to import scispaCy
try:
    import spacy
    SCISPACY_AVAILABLE = True

    # Try to load the model
    try:
        NLP_MODEL = spacy.load("en_core_sci_md")
        logger.info("✓ Medical NER model loaded successfully")
    except OSError:
        logger.warning("Medical NER model not found. Install with:")
        logger.warning("  pip install scispacy")
        logger.warning("  pip install https://s3-us-west-2.amazonaws.com/ai2-s3-scispacy/releases/v0.5.3/en_core_sci_md-0.5.3.tar.gz")
        NLP_MODEL = None
        SCISPACY_AVAILABLE = False
except ImportError:
    SCISPACY_AVAILABLE = False
    NLP_MODEL = None
    logger.warning("scispaCy not available. Install with: pip install scispacy")


def extract_medical_entities(text: str) -> Dict[str, List[Dict[str, Any]]]:
    """
    Extract medical entities from text using scispaCy.

    Args:
        text: Input text (interview transcript)

    Returns:
        Dictionary with categorized medical entities:
        {
            'conditions': [{'text': 'diabetes', 'start': 10, 'end': 18}],
            'symptoms': [{'text': 'nausea', 'start': 25, 'end': 31}],
            'medications': [{'text': 'insulin', 'start': 40, 'end': 47}],
            'procedures': [{'text': 'ultrasound', 'start': 55, 'end': 65}],
            'anatomy': [{'text': 'placenta', 'start': 70, 'end': 78}],
            'all_entities': [...]
        }
    """
    if not SCISPACY_AVAILABLE or NLP_MODEL is None:
        return {
            'conditions': [],
            'symptoms': [],
            'medications': [],
            'procedures': [],
            'anatomy': [],
            'all_entities': [],
            'error': 'scispaCy not available'
        }

    try:
        # Process text
        doc = NLP_MODEL(text)

        # Categorize entities
        entities = {
            'conditions': [],
            'symptoms': [],
            'medications': [],
            'procedures': [],
            'anatomy': [],
            'all_entities': []
        }

        # Entity type mapping
        entity_mapping = {
            'DISEASE': 'conditions',
            'SIGN_OR_SYMPTOM': 'symptoms',
            'CHEMICAL': 'medications',
            'PROCEDURE': 'procedures',
            'ANATOMY': 'anatomy'
        }

        for ent in doc.ents:
            entity_info = {
                'text': ent.text,
                'label': ent.label_,
                'start': ent.start_char,
                'end': ent.end_char
            }

            # Add to all entities
            entities['all_entities'].append(entity_info)

            # Add to specific category
            category = entity_mapping.get(ent.label_)
            if category:
                entities[category].append(entity_info)

        # Add statistics
        entities['statistics'] = {
            'total_entities': len(entities['all_entities']),
            'unique_conditions': len(set(e['text'].lower() for e in entities['conditions'])),
            'unique_symptoms': len(set(e['text'].lower() for e in entities['symptoms'])),
            'unique_medications': len(set(e['text'].lower() for e in entities['medications'])),
            'unique_procedures': len(set(e['text'].lower() for e in entities['procedures']))
        }

        return entities

    except Exception as e:
        logger.error(f"Error in medical entity extraction: {e}")
        return {
            'conditions': [],
            'symptoms': [],
            'medications': [],
            'procedures': [],
            'anatomy': [],
            'all_entities': [],
            'error': str(e)
        }


def extract_pregnancy_specific_terms(text: str) -> Dict[str, List[str]]:
    """
    Extract pregnancy-specific medical terms using pattern matching.

    This is a fallback/enhancement that works even without scispaCy.
    """
    pregnancy_terms = {
        'trimesters': ['first trimester', 'second trimester', 'third trimester',
                      '1st trimester', '2nd trimester', '3rd trimester'],
        'complications': ['preeclampsia', 'gestational diabetes', 'placenta previa',
                         'gestational hypertension', 'preterm labor', 'ectopic pregnancy',
                         'miscarriage', 'stillbirth', 'breach', 'premature rupture'],
        'symptoms': ['morning sickness', 'nausea', 'vomiting', 'swelling', 'edema',
                    'back pain', 'contractions', 'bleeding', 'spotting', 'cramping'],
        'tests': ['ultrasound', 'amniocentesis', 'glucose test', 'blood test',
                 'urine test', 'genetic testing', 'doppler', 'non-stress test'],
        'measurements': ['gestational age', 'fetal heart rate', 'blood pressure',
                        'fundal height', 'cervical dilation', 'effacement']
    }

    text_lower = text.lower()
    found_terms = {category: [] for category in pregnancy_terms}

    for category, terms in pregnancy_terms.items():
        for term in terms:
            if term in text_lower:
                found_terms[category].append(term)

    return found_terms


def analyze_medical_content(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive medical content analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Dictionary with medical entity analysis results
    """
    # Extract full interview text
    transcript = interview_data.get('transcript', [])
    full_text = ' '.join([turn.get('text', '') for turn in transcript])

    # Extract medical entities
    medical_entities = extract_medical_entities(full_text)

    # Extract pregnancy-specific terms
    pregnancy_terms = extract_pregnancy_specific_terms(full_text)

    # Combine results
    analysis = {
        'medical_entities': medical_entities,
        'pregnancy_terms': pregnancy_terms,
        'has_medical_content': (
            len(medical_entities.get('all_entities', [])) > 0 or
            any(len(terms) > 0 for terms in pregnancy_terms.values())
        ),
        'medical_complexity_score': calculate_medical_complexity(
            medical_entities, pregnancy_terms
        )
    }

    return analysis


def calculate_medical_complexity(entities: Dict, pregnancy_terms: Dict) -> float:
    """
    Calculate a medical complexity score (0-100).

    Based on:
    - Number of unique conditions
    - Number of symptoms
    - Number of medications
    - Pregnancy-specific complications
    """
    stats = entities.get('statistics', {})

    # Base scores
    conditions_score = min(stats.get('unique_conditions', 0) * 10, 30)
    symptoms_score = min(stats.get('unique_symptoms', 0) * 5, 25)
    medications_score = min(stats.get('unique_medications', 0) * 8, 25)
    complications_score = min(len(pregnancy_terms.get('complications', [])) * 10, 20)

    total_score = conditions_score + symptoms_score + medications_score + complications_score

    return min(total_score, 100.0)


def get_summary_stats(all_interviews_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics across all interviews.

    Args:
        all_interviews_analysis: List of medical analysis results

    Returns:
        Summary statistics dictionary
    """
    total_interviews = len(all_interviews_analysis)

    if total_interviews == 0:
        return {}

    # Count interviews with medical content
    with_medical = sum(1 for a in all_interviews_analysis
                      if a.get('has_medical_content', False))

    # Aggregate all conditions
    all_conditions = []
    all_symptoms = []
    all_medications = []

    for analysis in all_interviews_analysis:
        entities = analysis.get('medical_entities', {})
        all_conditions.extend([e['text'].lower() for e in entities.get('conditions', [])])
        all_symptoms.extend([e['text'].lower() for e in entities.get('symptoms', [])])
        all_medications.extend([e['text'].lower() for e in entities.get('medications', [])])

    from collections import Counter

    return {
        'total_interviews': total_interviews,
        'interviews_with_medical_content': with_medical,
        'percentage_with_medical': (with_medical / total_interviews * 100) if total_interviews > 0 else 0,
        'unique_conditions': len(set(all_conditions)),
        'unique_symptoms': len(set(all_symptoms)),
        'unique_medications': len(set(all_medications)),
        'most_common_conditions': Counter(all_conditions).most_common(10),
        'most_common_symptoms': Counter(all_symptoms).most_common(10),
        'most_common_medications': Counter(all_medications).most_common(10)
    }


# Installation check function
def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    status = {
        'scispacy': SCISPACY_AVAILABLE,
        'model_loaded': NLP_MODEL is not None
    }
    return status


if __name__ == '__main__':
    # Test the module
    test_text = """
    Patient presents with gestational diabetes and high blood pressure at 28 weeks.
    She reports nausea, fatigue, and occasional headaches. Currently taking prenatal
    vitamins and metformin. Had an ultrasound last week showing normal fetal development.
    Experiencing some swelling in legs and feet.
    """

    print("Medical NER Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"scispaCy available: {status['scispacy']}")
    print(f"Model loaded: {status['model_loaded']}")
    print()

    # Extract entities
    result = extract_medical_entities(test_text)

    print(f"Conditions found: {len(result['conditions'])}")
    for entity in result['conditions']:
        print(f"  - {entity['text']}")

    print(f"\nSymptoms found: {len(result['symptoms'])}")
    for entity in result['symptoms']:
        print(f"  - {entity['text']}")

    print(f"\nMedications found: {len(result['medications'])}")
    for entity in result['medications']:
        print(f"  - {entity['text']}")

    print(f"\nProcedures found: {len(result['procedures'])}")
    for entity in result['procedures']:
        print(f"  - {entity['text']}")

    print(f"\nTotal entities: {result['statistics']['total_entities']}")

    # Test pregnancy-specific extraction
    pregnancy_result = extract_pregnancy_specific_terms(test_text)
    print(f"\nPregnancy-specific terms:")
    for category, terms in pregnancy_result.items():
        if terms:
            print(f"  {category}: {', '.join(terms)}")
