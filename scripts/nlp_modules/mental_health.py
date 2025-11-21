"""
Mental Health Screening Module
================================

Automated screening for depression (PHQ-9) and anxiety (GAD-7) from interview
transcripts. Identifies mental health risk indicators and tracks longitudinal patterns.

⚠️ IMPORTANT DISCLAIMER:
This module is for RESEARCH and SCREENING purposes only. It does NOT provide
clinical diagnoses. All positive screens should be followed up with proper
clinical assessment by qualified healthcare professionals.

Capability #7 of 11 Advanced NLP Enhancements
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

# Try to import transformer models for advanced screening
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger.info("✓ Transformers available for mental health screening")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Using pattern-based screening only.")

# Global model cache
_mental_health_model = None
_model_name = None

# PHQ-9 Depression Screening Indicators
PHQ9_INDICATORS = {
    'anhedonia': {
        'keywords': ['no interest', 'not enjoy', 'lost pleasure', 'no pleasure', 'nothing fun',
                    'don\'t care', 'apathetic', 'numb', 'empty', 'flat', 'unmotivated'],
        'weight': 1.0
    },
    'depressed_mood': {
        'keywords': ['depressed', 'sad', 'hopeless', 'down', 'miserable', 'unhappy',
                    'blue', 'gloomy', 'despair', 'low mood', 'tearful', 'crying'],
        'weight': 1.0
    },
    'sleep_disturbance': {
        'keywords': ['can\'t sleep', 'insomnia', 'wake up', 'trouble sleeping', 'restless',
                    'sleep problems', 'too much sleep', 'oversleep', 'sleep all day'],
        'weight': 0.8
    },
    'fatigue': {
        'keywords': ['tired', 'exhausted', 'no energy', 'fatigued', 'drained', 'worn out',
                    'lack energy', 'sluggish', 'weak', 'lethargic'],
        'weight': 0.7
    },
    'appetite_change': {
        'keywords': ['no appetite', 'not eating', 'lost appetite', 'overeating', 'eating too much',
                    'weight loss', 'weight gain', 'food aversion'],
        'weight': 0.7
    },
    'low_self_worth': {
        'keywords': ['worthless', 'failure', 'let everyone down', 'disappointed', 'shame',
                    'guilty', 'blame myself', 'hate myself', 'not good enough'],
        'weight': 1.0
    },
    'concentration_difficulty': {
        'keywords': ['can\'t focus', 'can\'t concentrate', 'trouble thinking', 'scattered',
                    'forgetful', 'mind blank', 'can\'t remember', 'distracted'],
        'weight': 0.8
    },
    'psychomotor_change': {
        'keywords': ['slowed down', 'moving slow', 'restless', 'fidgety', 'can\'t sit still',
                    'agitated', 'pacing'],
        'weight': 0.7
    },
    'suicidal_ideation': {
        'keywords': ['better off dead', 'hurt myself', 'end it all', 'suicidal', 'kill myself',
                    'want to die', 'no point living', 'wish I was dead'],
        'weight': 2.0  # Critical indicator
    }
}

# GAD-7 Anxiety Screening Indicators
GAD7_INDICATORS = {
    'excessive_worry': {
        'keywords': ['worry', 'worried', 'anxious', 'nervous', 'stress', 'stressed',
                    'can\'t stop worrying', 'overthinking', 'ruminating'],
        'weight': 1.0
    },
    'difficulty_controlling_worry': {
        'keywords': ['can\'t control', 'overwhelming', 'consumed by', 'can\'t stop thinking',
                    'obsessing', 'constant worry', 'spiraling'],
        'weight': 1.0
    },
    'restlessness': {
        'keywords': ['restless', 'on edge', 'keyed up', 'tense', 'wound up', 'jittery',
                    'nervous energy', 'can\'t relax'],
        'weight': 0.8
    },
    'fatigue': {
        'keywords': ['tired', 'exhausted', 'drained', 'worn out', 'no energy'],
        'weight': 0.7
    },
    'concentration_difficulty': {
        'keywords': ['can\'t focus', 'can\'t concentrate', 'mind racing', 'scattered',
                    'trouble thinking', 'distracted'],
        'weight': 0.8
    },
    'irritability': {
        'keywords': ['irritable', 'angry', 'short temper', 'snapping', 'frustrated',
                    'on edge', 'annoyed', 'impatient'],
        'weight': 0.8
    },
    'muscle_tension': {
        'keywords': ['tense', 'tight muscles', 'tension', 'stiff', 'aching', 'sore muscles'],
        'weight': 0.7
    },
    'sleep_disturbance': {
        'keywords': ['can\'t sleep', 'trouble sleeping', 'restless sleep', 'wake up worrying',
                    'insomnia', 'racing thoughts at night'],
        'weight': 0.8
    }
}

# Pregnancy-Specific Mental Health Indicators
PREGNANCY_SPECIFIC_INDICATORS = {
    'prenatal_depression': {
        'keywords': ['regret pregnancy', 'don\'t want baby', 'trapped', 'burden',
                    'can\'t bond', 'scared of motherhood', 'not ready'],
        'weight': 1.5
    },
    'prenatal_anxiety': {
        'keywords': ['afraid of delivery', 'fear childbirth', 'worry about baby',
                    'constant checking', 'catastrophizing', 'something wrong with baby'],
        'weight': 1.2
    },
    'social_isolation': {
        'keywords': ['alone', 'isolated', 'no support', 'no one understands',
                    'withdrawn', 'avoiding people', 'lonely'],
        'weight': 1.0
    }
}


def load_mental_health_model(model_name: str = 'mental-bert'):
    """
    Load a mental health classification model.

    Args:
        model_name: Model identifier ('mental-bert', 'clinical-bert', etc.)

    Returns:
        Loaded model pipeline or None
    """
    global _mental_health_model, _model_name

    if not TRANSFORMERS_AVAILABLE:
        return None

    if _mental_health_model is not None and _model_name == model_name:
        return _mental_health_model

    # Note: These are placeholder model names. In production, you would use
    # actual fine-tuned models for mental health classification
    model_mapping = {
        'mental-bert': 'distilbert-base-uncased',  # Placeholder
        'clinical-bert': 'emilyalsentzer/Bio_ClinicalBERT'
    }

    try:
        actual_model = model_mapping.get(model_name, model_name)
        logger.info(f"Loading mental health model: {actual_model}")
        # This would load a fine-tuned model for mental health classification
        # For now, using base model as placeholder
        logger.warning("Using base model - production should use fine-tuned mental health models")
        _model_name = model_name
        return None  # Return None for now, pattern-based only
    except Exception as e:
        logger.error(f"Error loading mental health model: {e}")
        return None


def screen_depression_phq9(text: str, context: str = 'general') -> Dict[str, Any]:
    """
    Screen for depression indicators using PHQ-9 framework.

    Args:
        text: Interview transcript text
        context: 'general' or 'pregnancy' for context-specific screening

    Returns:
        Dictionary with PHQ-9 screening results:
        {
            'phq9_score': 12,  # 0-27 scale
            'severity': 'moderate',  # minimal, mild, moderate, moderately_severe, severe
            'risk_level': 'medium',
            'indicators_present': ['depressed_mood', 'fatigue', ...],
            'indicator_details': {...},
            'requires_followup': True,
            'critical_flags': ['suicidal_ideation']
        }
    """
    text_lower = text.lower()

    # Detect indicators
    indicators_found = {}
    total_score = 0.0

    for indicator_name, indicator_data in PHQ9_INDICATORS.items():
        keywords = indicator_data['keywords']
        weight = indicator_data['weight']

        # Count keyword matches
        matches = []
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(keyword)

        if matches:
            # Score based on frequency and weight
            frequency = len(matches)
            indicator_score = min(3, frequency) * weight  # Cap at 3 per indicator
            indicators_found[indicator_name] = {
                'score': indicator_score,
                'matches': matches,
                'frequency': frequency
            }
            total_score += indicator_score

    # Add pregnancy-specific indicators if applicable
    if context == 'pregnancy':
        for indicator_name, indicator_data in PREGNANCY_SPECIFIC_INDICATORS.items():
            if 'depression' in indicator_name:
                keywords = indicator_data['keywords']
                weight = indicator_data['weight']

                matches = []
                for keyword in keywords:
                    if keyword in text_lower:
                        matches.append(keyword)

                if matches:
                    frequency = len(matches)
                    indicator_score = min(3, frequency) * weight
                    indicators_found[indicator_name] = {
                        'score': indicator_score,
                        'matches': matches,
                        'frequency': frequency
                    }
                    total_score += indicator_score

    # Normalize to PHQ-9 scale (0-27)
    # Rough mapping based on indicator weights
    phq9_score = min(27, int(total_score * 1.5))

    # Determine severity
    if phq9_score < 5:
        severity = 'minimal'
    elif phq9_score < 10:
        severity = 'mild'
    elif phq9_score < 15:
        severity = 'moderate'
    elif phq9_score < 20:
        severity = 'moderately_severe'
    else:
        severity = 'severe'

    # Determine risk level
    if phq9_score < 5:
        risk_level = 'low'
    elif phq9_score < 15:
        risk_level = 'medium'
    else:
        risk_level = 'high'

    # Critical flags
    critical_flags = []
    if 'suicidal_ideation' in indicators_found:
        critical_flags.append('suicidal_ideation')
        risk_level = 'critical'

    # Determine if follow-up needed
    requires_followup = (phq9_score >= 10 or len(critical_flags) > 0)

    return {
        'phq9_score': phq9_score,
        'severity': severity,
        'risk_level': risk_level,
        'indicators_present': list(indicators_found.keys()),
        'num_indicators': len(indicators_found),
        'indicator_details': indicators_found,
        'requires_followup': requires_followup,
        'critical_flags': critical_flags,
        'screening_method': 'pattern-based'
    }


def screen_anxiety_gad7(text: str, context: str = 'general') -> Dict[str, Any]:
    """
    Screen for anxiety indicators using GAD-7 framework.

    Args:
        text: Interview transcript text
        context: 'general' or 'pregnancy' for context-specific screening

    Returns:
        Dictionary with GAD-7 screening results:
        {
            'gad7_score': 9,  # 0-21 scale
            'severity': 'moderate',  # minimal, mild, moderate, severe
            'risk_level': 'medium',
            'indicators_present': [...],
            'indicator_details': {...},
            'requires_followup': True
        }
    """
    text_lower = text.lower()

    # Detect indicators
    indicators_found = {}
    total_score = 0.0

    for indicator_name, indicator_data in GAD7_INDICATORS.items():
        keywords = indicator_data['keywords']
        weight = indicator_data['weight']

        # Count keyword matches
        matches = []
        for keyword in keywords:
            if keyword in text_lower:
                matches.append(keyword)

        if matches:
            frequency = len(matches)
            indicator_score = min(3, frequency) * weight
            indicators_found[indicator_name] = {
                'score': indicator_score,
                'matches': matches,
                'frequency': frequency
            }
            total_score += indicator_score

    # Add pregnancy-specific anxiety indicators
    if context == 'pregnancy':
        for indicator_name, indicator_data in PREGNANCY_SPECIFIC_INDICATORS.items():
            if 'anxiety' in indicator_name:
                keywords = indicator_data['keywords']
                weight = indicator_data['weight']

                matches = []
                for keyword in keywords:
                    if keyword in text_lower:
                        matches.append(keyword)

                if matches:
                    frequency = len(matches)
                    indicator_score = min(3, frequency) * weight
                    indicators_found[indicator_name] = {
                        'score': indicator_score,
                        'matches': matches,
                        'frequency': frequency
                    }
                    total_score += indicator_score

    # Normalize to GAD-7 scale (0-21)
    gad7_score = min(21, int(total_score * 1.2))

    # Determine severity
    if gad7_score < 5:
        severity = 'minimal'
    elif gad7_score < 10:
        severity = 'mild'
    elif gad7_score < 15:
        severity = 'moderate'
    else:
        severity = 'severe'

    # Determine risk level
    if gad7_score < 5:
        risk_level = 'low'
    elif gad7_score < 15:
        risk_level = 'medium'
    else:
        risk_level = 'high'

    # Determine if follow-up needed
    requires_followup = (gad7_score >= 10)

    return {
        'gad7_score': gad7_score,
        'severity': severity,
        'risk_level': risk_level,
        'indicators_present': list(indicators_found.keys()),
        'num_indicators': len(indicators_found),
        'indicator_details': indicators_found,
        'requires_followup': requires_followup,
        'screening_method': 'pattern-based'
    }


def screen_mental_health(interview_data: Dict[str, Any],
                        context: str = 'pregnancy') -> Dict[str, Any]:
    """
    Comprehensive mental health screening of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field
        context: 'general' or 'pregnancy'

    Returns:
        Dictionary with complete mental health screening results
    """
    # Extract interview text
    transcript = interview_data.get('transcript', [])
    if isinstance(transcript, list):
        full_text = ' '.join([turn.get('text', '') for turn in transcript])

        # Separate persona and interviewer for per-speaker analysis
        persona_texts = []
        interviewer_texts = []

        for turn in transcript:
            text = turn.get('text', '')
            speaker = turn.get('speaker', 'unknown').lower()

            if 'persona' in speaker or 'participant' in speaker or 'patient' in speaker:
                persona_texts.append(text)
            elif 'interviewer' in speaker or 'doctor' in speaker or 'clinician' in speaker:
                interviewer_texts.append(text)

        persona_text = ' '.join(persona_texts)
        interviewer_text = ' '.join(interviewer_texts)
    else:
        full_text = str(transcript)
        persona_text = full_text
        interviewer_text = ""

    # Screen for depression (PHQ-9)
    depression_screening = screen_depression_phq9(full_text, context)

    # Screen for anxiety (GAD-7)
    anxiety_screening = screen_anxiety_gad7(full_text, context)

    # Screen persona specifically (more clinically relevant)
    persona_depression = None
    persona_anxiety = None
    if persona_text:
        persona_depression = screen_depression_phq9(persona_text, context)
        persona_anxiety = screen_anxiety_gad7(persona_text, context)

    # Overall risk assessment
    overall_risk = _assess_overall_risk(depression_screening, anxiety_screening)

    # Social support assessment
    social_support = _assess_social_support(full_text)

    # Pregnancy-specific concerns (if applicable)
    pregnancy_concerns = {}
    if context == 'pregnancy':
        pregnancy_concerns = _assess_pregnancy_mental_health(full_text)

    return {
        'depression_screening': depression_screening,
        'anxiety_screening': anxiety_screening,
        'persona_depression': persona_depression,
        'persona_anxiety': persona_anxiety,
        'overall_risk_level': overall_risk,
        'social_support': social_support,
        'pregnancy_concerns': pregnancy_concerns if context == 'pregnancy' else None,
        'requires_clinical_followup': (
            depression_screening.get('requires_followup', False) or
            anxiety_screening.get('requires_followup', False) or
            len(depression_screening.get('critical_flags', [])) > 0
        ),
        'critical_alerts': depression_screening.get('critical_flags', []),
        'context': context,
        'disclaimer': 'This is a screening tool only, not a diagnostic instrument. Clinical assessment required.'
    }


def track_longitudinal_mental_health(screenings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Track mental health patterns across multiple screenings over time.

    Args:
        screenings: List of mental health screening results (chronologically ordered)

    Returns:
        Dictionary with longitudinal analysis
    """
    if not screenings:
        return {'error': 'No screenings provided'}

    # Extract scores over time
    phq9_scores = []
    gad7_scores = []
    timestamps = []

    for i, screening in enumerate(screenings):
        depression = screening.get('depression_screening', {})
        anxiety = screening.get('anxiety_screening', {})

        phq9_scores.append(depression.get('phq9_score', 0))
        gad7_scores.append(anxiety.get('gad7_score', 0))
        timestamps.append(i)  # Use index as time if no timestamp provided

    # Calculate trends
    phq9_trend = _calculate_trend(phq9_scores)
    gad7_trend = _calculate_trend(gad7_scores)

    # Identify concerning patterns
    concerning_patterns = []

    if phq9_trend > 0.5:
        concerning_patterns.append('increasing_depression')
    if gad7_trend > 0.5:
        concerning_patterns.append('increasing_anxiety')

    if phq9_scores[-1] > phq9_scores[0] + 5:
        concerning_patterns.append('significant_depression_worsening')
    if gad7_scores[-1] > gad7_scores[0] + 5:
        concerning_patterns.append('significant_anxiety_worsening')

    # Check for persistent high risk
    high_risk_count = sum(1 for s in screenings
                          if s.get('overall_risk_level') in ['high', 'critical'])
    if high_risk_count >= len(screenings) * 0.6:
        concerning_patterns.append('persistent_high_risk')

    return {
        'num_screenings': len(screenings),
        'phq9_scores': phq9_scores,
        'gad7_scores': gad7_scores,
        'phq9_trend': phq9_trend,  # -1 (improving) to +1 (worsening)
        'gad7_trend': gad7_trend,
        'depression_trajectory': _categorize_trend(phq9_trend),
        'anxiety_trajectory': _categorize_trend(gad7_trend),
        'concerning_patterns': concerning_patterns,
        'requires_intervention': len(concerning_patterns) > 0,
        'latest_phq9': phq9_scores[-1],
        'latest_gad7': gad7_scores[-1],
        'peak_phq9': max(phq9_scores),
        'peak_gad7': max(gad7_scores)
    }


# Helper functions

def _assess_overall_risk(depression: Dict, anxiety: Dict) -> str:
    """Assess overall mental health risk level."""
    depression_risk = depression.get('risk_level', 'low')
    anxiety_risk = anxiety.get('risk_level', 'low')

    # Critical if any critical flags
    if depression_risk == 'critical' or anxiety_risk == 'critical':
        return 'critical'

    # High if either is high
    if depression_risk == 'high' or anxiety_risk == 'high':
        return 'high'

    # Medium if either is medium
    if depression_risk == 'medium' or anxiety_risk == 'medium':
        return 'medium'

    return 'low'


def _assess_social_support(text: str) -> Dict[str, Any]:
    """Assess social support level from text."""
    text_lower = text.lower()

    positive_support = ['partner support', 'family help', 'friends', 'support group',
                       'people help', 'not alone', 'someone to talk']
    negative_support = ['no support', 'alone', 'isolated', 'no one', 'by myself',
                       'no help', 'no family', 'no friends']

    positive_count = sum(1 for keyword in positive_support if keyword in text_lower)
    negative_count = sum(1 for keyword in negative_support if keyword in text_lower)

    if negative_count > positive_count:
        level = 'low'
    elif positive_count > negative_count:
        level = 'high'
    else:
        level = 'medium'

    return {
        'level': level,
        'positive_indicators': positive_count,
        'negative_indicators': negative_count
    }


def _assess_pregnancy_mental_health(text: str) -> Dict[str, Any]:
    """Assess pregnancy-specific mental health concerns."""
    text_lower = text.lower()

    concerns = {
        'bonding_concerns': ['can\'t bond', 'don\'t feel connected', 'not excited',
                            'no attachment', 'don\'t feel pregnant'],
        'birth_anxiety': ['afraid of delivery', 'fear childbirth', 'scared of labor',
                         'terrified of birth'],
        'parenting_anxiety': ['not ready', 'won\'t be good mother', 'can\'t handle',
                             'overwhelmed', 'scared of responsibility'],
        'body_image': ['hate my body', 'feel ugly', 'disgusted by', 'can\'t stand']
    }

    results = {}
    for concern_type, keywords in concerns.items():
        matches = [kw for kw in keywords if kw in text_lower]
        results[concern_type] = {
            'present': len(matches) > 0,
            'matches': matches
        }

    return results


def _calculate_trend(scores: List[float]) -> float:
    """
    Calculate trend from a series of scores.
    Returns: -1 (improving) to +1 (worsening)
    """
    if len(scores) < 2:
        return 0.0

    # Simple linear trend
    x = np.arange(len(scores))
    y = np.array(scores)

    # Calculate slope
    try:
        slope = np.polyfit(x, y, 1)[0]
        # Normalize to -1 to 1 range
        max_possible_change = max(scores) - min(scores)
        if max_possible_change > 0:
            normalized_slope = slope / (max_possible_change / len(scores))
            return float(np.clip(normalized_slope, -1, 1))
        return 0.0
    except:
        return 0.0


def _categorize_trend(trend_value: float) -> str:
    """Categorize trend value into descriptive category."""
    if trend_value < -0.3:
        return 'improving'
    elif trend_value > 0.3:
        return 'worsening'
    else:
        return 'stable'


def get_summary_statistics(all_screenings: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate summary statistics across all mental health screenings.

    Args:
        all_screenings: List of mental health screening results

    Returns:
        Summary statistics dictionary
    """
    if not all_screenings:
        return {}

    phq9_scores = []
    gad7_scores = []
    risk_levels = []

    for screening in all_screenings:
        depression = screening.get('depression_screening', {})
        anxiety = screening.get('anxiety_screening', {})

        phq9_scores.append(depression.get('phq9_score', 0))
        gad7_scores.append(anxiety.get('gad7_score', 0))
        risk_levels.append(screening.get('overall_risk_level', 'low'))

    # Count risk levels
    risk_counts = Counter(risk_levels)

    # Calculate percentages
    total = len(all_screenings)
    requires_followup = sum(1 for s in all_screenings
                           if s.get('requires_clinical_followup', False))

    return {
        'total_screenings': total,
        'average_phq9': np.mean(phq9_scores),
        'average_gad7': np.mean(gad7_scores),
        'phq9_range': {'min': min(phq9_scores), 'max': max(phq9_scores)},
        'gad7_range': {'min': min(gad7_scores), 'max': max(gad7_scores)},
        'risk_distribution': dict(risk_counts),
        'percentage_requiring_followup': (requires_followup / total * 100) if total > 0 else 0,
        'high_risk_percentage': (risk_counts.get('high', 0) + risk_counts.get('critical', 0)) / total * 100 if total > 0 else 0,
        'critical_alerts': sum(1 for s in all_screenings
                              if len(s.get('critical_alerts', [])) > 0)
    }


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'transformers': TRANSFORMERS_AVAILABLE,
        'has_mental_health_screening': True,  # Pattern-based always available
        'advanced_models_available': False  # Would need fine-tuned models
    }


if __name__ == '__main__':
    # Test the module
    test_interview = {
        'transcript': [
            {
                'speaker': 'interviewer',
                'text': 'How have you been feeling lately?'
            },
            {
                'speaker': 'persona',
                'text': 'Honestly, I\'ve been feeling really down. I\'m tired all the time and nothing seems fun anymore. I worry constantly about the baby and whether I\'ll be a good mother. I can\'t sleep at night because my mind is racing with worry.'
            },
            {
                'speaker': 'interviewer',
                'text': 'I\'m sorry to hear that. Can you tell me more about your support system?'
            },
            {
                'speaker': 'persona',
                'text': 'I feel pretty alone actually. My partner works a lot and I don\'t have family nearby. Sometimes I wonder if I made a mistake. I just feel hopeless about everything.'
            }
        ]
    }

    print("Mental Health Screening Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Mental health screening available: {status['has_mental_health_screening']}")
    print(f"Transformers available: {status['transformers']}")
    print()

    # Perform screening
    print("Screening test interview...")
    result = screen_mental_health(test_interview, context='pregnancy')

    print(f"\nDEPRESSION SCREENING (PHQ-9):")
    depression = result['depression_screening']
    print(f"  Score: {depression['phq9_score']}/27")
    print(f"  Severity: {depression['severity']}")
    print(f"  Risk Level: {depression['risk_level']}")
    print(f"  Indicators: {', '.join(depression['indicators_present'])}")

    print(f"\nANXIETY SCREENING (GAD-7):")
    anxiety = result['anxiety_screening']
    print(f"  Score: {anxiety['gad7_score']}/21")
    print(f"  Severity: {anxiety['severity']}")
    print(f"  Risk Level: {anxiety['risk_level']}")
    print(f"  Indicators: {', '.join(anxiety['indicators_present'])}")

    print(f"\nOVERALL ASSESSMENT:")
    print(f"  Overall Risk: {result['overall_risk_level']}")
    print(f"  Requires Follow-up: {result['requires_clinical_followup']}")
    print(f"  Social Support: {result['social_support']['level']}")

    if result['pregnancy_concerns']:
        print(f"\nPREGNANCY-SPECIFIC CONCERNS:")
        for concern, data in result['pregnancy_concerns'].items():
            if data['present']:
                print(f"  - {concern}: {', '.join(data['matches'])}")

    print(f"\n⚠️ DISCLAIMER: {result['disclaimer']}")
