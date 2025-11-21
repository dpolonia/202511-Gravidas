"""
Empathy Detection Module
=========================

Measures empathetic responses in conversations and evaluates interviewer
communication quality. Assesses emotional support, validation, and
person-centered communication.

Capability #9 of 11 Advanced NLP Enhancements
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import numpy as np

logger = logging.getLogger(__name__)

# Try to import transformer models for advanced empathy detection
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger.info("✓ Transformers available for empathy detection")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Using pattern-based empathy detection.")

# Empathy Indicator Categories
EMPATHY_INDICATORS = {
    'emotional_validation': {
        'patterns': [
            r'\b(that|it) (must be|sounds|seems) (difficult|hard|challenging|tough|scary|overwhelming)',
            r'\bI (can )?(understand|imagine|see) (how|why|that)',
            r'\bthat makes sense',
            r'\b(you\'re|youre|you are) (right|justified) (to feel|in feeling)',
            r'\banyone would feel',
            r'\bit\'s (natural|normal|understandable) to feel'
        ],
        'keywords': ['validate', 'understandable', 'natural', 'normal', 'makes sense',
                    'of course', 'absolutely', 'certainly'],
        'weight': 1.5
    },
    'emotional_exploration': {
        'patterns': [
            r'\bhow (do|did) (you|that make you) feel',
            r'\bwhat (are|were) you feeling',
            r'\btell me more about',
            r'\bcan you (describe|explain|share)',
            r'\bhelp me understand'
        ],
        'keywords': ['tell me more', 'share', 'describe', 'explain', 'elaborate'],
        'weight': 1.2
    },
    'reflective_listening': {
        'patterns': [
            r'\bso (what )?you\'?re (saying|feeling|experiencing)',
            r'\bit sounds like',
            r'\bwhat I\'m hearing',
            r'\bif I understand (correctly|right)',
            r'\blet me (make sure|check if|see if)'
        ],
        'keywords': ['sounds like', 'hearing', 'understand correctly', 'paraphrase'],
        'weight': 1.3
    },
    'affirmation_support': {
        'patterns': [
            r'\byou\'?re (doing|handling) (great|well|amazing|wonderful)',
            r'\bthat\'?s (brave|courageous|strong|resilient)',
            r'\bI\'m (proud|impressed|amazed)',
            r'\byou (should be|can be) proud',
            r'\byou\'?ve (got|have) this'
        ],
        'keywords': ['proud', 'strong', 'brave', 'good job', 'well done',
                    'impressive', 'admirable'],
        'weight': 1.0
    },
    'concern_compassion': {
        'patterns': [
            r'\bI\'m (sorry|concerned|worried) (that|about|to hear)',
            r'\bthat (sounds|must be) (difficult|painful|hard)',
            r'\bI (care|worry) about',
            r'\bthinking of you',
            r'\bhere for you'
        ],
        'keywords': ['sorry', 'concerned', 'care', 'support', 'here for you',
                    'thinking of you'],
        'weight': 1.4
    },
    'shared_experience': {
        'patterns': [
            r'\bI (also|too) (felt|experienced|had)',
            r'\bmany (people|women|mothers) (feel|experience)',
            r'\byou\'?re not alone',
            r'\bothers (have )?felt this way',
            r'\bthis is common'
        ],
        'keywords': ['not alone', 'common', 'many people', 'others feel'],
        'weight': 1.1
    },
    'reassurance': {
        'patterns': [
            r'\bit\'?s (going to|gonna) be (okay|alright|fine)',
            r'\bthings will (get better|improve|work out)',
            r'\byou\'?ll (get through|be okay|be fine)',
            r'\bwe\'?ll (help|support|work through)',
            r'\btogether we (can|will)'
        ],
        'keywords': ['be okay', 'work out', 'get better', 'together'],
        'weight': 1.0
    }
}

# Non-empathetic/dismissive patterns (negative indicators)
NON_EMPATHETIC_PATTERNS = {
    'dismissive': [
        r'\bjust (get over|move on|forget about|deal with)',
        r'\bit\'?s not (that bad|a big deal)',
        r'\bdon\'t (worry|stress|be|feel)',
        r'\byou\'re (overreacting|being dramatic)',
        r'\beveryone (feels|goes through) (this|that)'
    ],
    'minimizing': [
        r'\bat least',
        r'\bcould be worse',
        r'\bthink positive',
        r'\blook on the bright side'
    ],
    'advice_giving': [  # Premature advice without exploration
        r'\byou should (just|really)',
        r'\bwhat you need to do is',
        r'\bmy advice is',
        r'\bhave you tried (just)?'
    ],
    'judgmental': [
        r'\byou shouldn\'t (feel|think|be)',
        r'\bthat\'s (wrong|bad|silly) (to|of you)',
        r'\bwhy would you',
        r'\bwhy did(n\'t)? you'
    ]
}


def detect_empathy_in_turn(text: str, speaker_role: str = 'interviewer') -> Dict[str, Any]:
    """
    Detect empathy indicators in a single conversation turn.

    Args:
        text: Turn text
        speaker_role: 'interviewer', 'clinician', 'persona', etc.

    Returns:
        Dictionary with empathy analysis for this turn
    """
    text_lower = text.lower()

    # Detect positive empathy indicators
    empathy_scores = {}
    total_empathy_score = 0.0
    indicators_found = []

    for category, data in EMPATHY_INDICATORS.items():
        category_score = 0.0
        matches = []

        # Check patterns
        for pattern in data['patterns']:
            if re.search(pattern, text_lower):
                matches.append(f"pattern:{pattern[:30]}...")
                category_score += 1.0

        # Check keywords
        for keyword in data['keywords']:
            if keyword in text_lower:
                matches.append(f"keyword:{keyword}")
                category_score += 0.5

        if category_score > 0:
            weighted_score = category_score * data['weight']
            empathy_scores[category] = {
                'raw_score': float(category_score),
                'weighted_score': float(weighted_score),
                'matches': matches[:3]  # Top 3 matches
            }
            total_empathy_score += weighted_score
            indicators_found.append(category)

    # Detect negative indicators (non-empathetic)
    negative_indicators = {}
    total_negative_score = 0.0

    for category, patterns in NON_EMPATHETIC_PATTERNS.items():
        matches = []
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matches.append(pattern[:30])

        if matches:
            negative_indicators[category] = matches
            total_negative_score += len(matches) * 0.5

    # Calculate net empathy score
    net_score = total_empathy_score - total_negative_score

    # Normalize to 0-1 scale
    empathy_level = min(max(net_score / 3.0, 0.0), 1.0)

    # Categorize empathy level
    if empathy_level >= 0.7:
        category = 'high'
    elif empathy_level >= 0.4:
        category = 'moderate'
    elif empathy_level >= 0.2:
        category = 'low'
    else:
        category = 'minimal'

    return {
        'empathy_score': float(empathy_level),
        'empathy_category': category,
        'total_positive_indicators': len(indicators_found),
        'total_negative_indicators': len(negative_indicators),
        'empathy_indicators': empathy_scores,
        'negative_indicators': negative_indicators,
        'net_score': float(net_score),
        'is_empathetic': empathy_level >= 0.4
    }


def analyze_interview_empathy(interview_data: Dict[str, Any],
                              interviewer_roles: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Comprehensive empathy analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field
        interviewer_roles: List of speaker identifiers for interviewers
                          (default: ['interviewer', 'doctor', 'clinician'])

    Returns:
        Dictionary with complete empathy analysis
    """
    if interviewer_roles is None:
        interviewer_roles = ['interviewer', 'doctor', 'clinician', 'provider']

    transcript = interview_data.get('transcript', [])

    if not isinstance(transcript, list) or len(transcript) == 0:
        return {'error': 'Invalid or empty transcript'}

    # Analyze each turn
    interviewer_turns = []
    persona_turns = []
    all_turn_analyses = []

    for i, turn in enumerate(transcript):
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown').lower()

        # Detect empathy in this turn
        turn_empathy = detect_empathy_in_turn(text, speaker)
        turn_empathy['turn_index'] = i
        turn_empathy['speaker'] = speaker
        turn_empathy['position'] = i / len(transcript)

        all_turn_analyses.append(turn_empathy)

        # Categorize by speaker
        if any(role in speaker for role in interviewer_roles):
            interviewer_turns.append(turn_empathy)
        else:
            persona_turns.append(turn_empathy)

    # Calculate interviewer empathy metrics
    if interviewer_turns:
        interviewer_empathy = _calculate_speaker_empathy(interviewer_turns)
    else:
        interviewer_empathy = {'error': 'No interviewer turns found'}

    # Calculate persona's empathy (less relevant but interesting)
    if persona_turns:
        persona_empathy = _calculate_speaker_empathy(persona_turns)
    else:
        persona_empathy = None

    # Track empathy over time
    empathy_trajectory = [turn['empathy_score'] for turn in all_turn_analyses]
    positions = [turn['position'] for turn in all_turn_analyses]

    # Identify high empathy moments
    high_empathy_moments = [
        {
            'turn_index': turn['turn_index'],
            'position': turn['position'],
            'empathy_score': turn['empathy_score'],
            'indicators': list(turn['empathy_indicators'].keys())
        }
        for turn in all_turn_analyses
        if turn['empathy_score'] >= 0.6
    ]

    # Identify low empathy / problematic moments
    problematic_moments = [
        {
            'turn_index': turn['turn_index'],
            'position': turn['position'],
            'empathy_score': turn['empathy_score'],
            'negative_indicators': list(turn['negative_indicators'].keys())
        }
        for turn in all_turn_analyses
        if len(turn['negative_indicators']) > 0
    ]

    # Calculate empathy responsiveness (empathy after emotional turns)
    responsiveness = _calculate_empathy_responsiveness(all_turn_analyses, transcript)

    # Overall interview empathy quality
    overall_quality = _assess_overall_empathy_quality(
        interviewer_empathy,
        empathy_trajectory,
        problematic_moments
    )

    return {
        'interviewer_empathy': interviewer_empathy,
        'persona_empathy': persona_empathy,
        'empathy_trajectory': empathy_trajectory,
        'positions': positions,
        'high_empathy_moments': high_empathy_moments,
        'problematic_moments': problematic_moments,
        'empathy_responsiveness': responsiveness,
        'overall_quality': overall_quality,
        'turn_by_turn': all_turn_analyses
    }


def compare_interviewer_empathy(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare empathy levels across multiple interviews/interviewers.

    Args:
        interviews: List of interview dictionaries

    Returns:
        Comparative empathy analysis
    """
    if not interviews:
        return {'error': 'No interviews provided'}

    empathy_scores = []
    empathy_categories = []
    high_quality_count = 0

    for interview in interviews:
        analysis = analyze_interview_empathy(interview)

        if 'error' not in analysis:
            interviewer = analysis.get('interviewer_empathy', {})
            score = interviewer.get('average_empathy_score', 0.0)
            category = interviewer.get('empathy_level', 'unknown')

            empathy_scores.append(score)
            empathy_categories.append(category)

            quality = analysis.get('overall_quality', {})
            if quality.get('quality_rating') in ['excellent', 'good']:
                high_quality_count += 1

    category_counts = Counter(empathy_categories)

    return {
        'num_interviews': len(interviews),
        'average_empathy_score': float(np.mean(empathy_scores)) if empathy_scores else 0.0,
        'empathy_score_range': {
            'min': float(min(empathy_scores)) if empathy_scores else 0.0,
            'max': float(max(empathy_scores)) if empathy_scores else 0.0,
            'std': float(np.std(empathy_scores)) if empathy_scores else 0.0
        },
        'empathy_distribution': dict(category_counts),
        'high_quality_percentage': (high_quality_count / len(interviews) * 100) if interviews else 0.0,
        'consistency': 1.0 - (np.std(empathy_scores) if empathy_scores else 1.0)
    }


def measure_empathy_gap(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Measure empathy gap - when persona expresses distress but interviewer
    doesn't respond empathetically.

    Args:
        interview_data: Interview dictionary

    Returns:
        Empathy gap analysis
    """
    transcript = interview_data.get('transcript', [])

    if len(transcript) < 2:
        return {'error': 'Transcript too short'}

    gaps = []

    for i in range(len(transcript) - 1):
        current_turn = transcript[i]
        next_turn = transcript[i + 1]

        current_speaker = current_turn.get('speaker', '').lower()
        next_speaker = next_turn.get('speaker', '').lower()

        # Check if current turn is persona expressing distress
        if 'persona' in current_speaker or 'patient' in current_speaker:
            current_text = current_turn.get('text', '').lower()

            # Detect distress indicators
            distress_score = _detect_distress(current_text)

            if distress_score > 0.5:
                # Check if next turn (interviewer) is empathetic
                if 'interviewer' in next_speaker or 'doctor' in next_speaker:
                    next_text = next_turn.get('text', '')
                    empathy = detect_empathy_in_turn(next_text)

                    # Gap exists if distress is high but empathy response is low
                    if empathy['empathy_score'] < 0.3:
                        gaps.append({
                            'position': i / len(transcript),
                            'distress_turn_index': i,
                            'response_turn_index': i + 1,
                            'distress_level': float(distress_score),
                            'empathy_response': empathy['empathy_score'],
                            'gap_magnitude': float(distress_score - empathy['empathy_score']),
                            'distress_context': current_text[:150]
                        })

    # Calculate overall gap metrics
    if gaps:
        avg_gap = np.mean([g['gap_magnitude'] for g in gaps])
        max_gap = max(g['gap_magnitude'] for g in gaps)
    else:
        avg_gap = 0.0
        max_gap = 0.0

    return {
        'empathy_gaps': gaps,
        'num_gaps': len(gaps),
        'average_gap_magnitude': float(avg_gap),
        'max_gap_magnitude': float(max_gap),
        'has_significant_gaps': len(gaps) > 0 and avg_gap > 0.5
    }


# Helper functions

def _calculate_speaker_empathy(turn_analyses: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate aggregate empathy metrics for a speaker."""
    empathy_scores = [turn['empathy_score'] for turn in turn_analyses]
    empathetic_turns = sum(1 for turn in turn_analyses if turn['is_empathetic'])

    # Count indicator types used
    all_indicators = []
    for turn in turn_analyses:
        all_indicators.extend(turn['empathy_indicators'].keys())

    indicator_counts = Counter(all_indicators)
    most_used_indicators = indicator_counts.most_common(3)

    # Average empathy score
    avg_score = np.mean(empathy_scores)

    # Determine empathy level
    if avg_score >= 0.6:
        level = 'high'
    elif avg_score >= 0.4:
        level = 'moderate'
    elif avg_score >= 0.2:
        level = 'low'
    else:
        level = 'minimal'

    return {
        'average_empathy_score': float(avg_score),
        'empathy_level': level,
        'num_turns': len(turn_analyses),
        'empathetic_turn_percentage': (empathetic_turns / len(turn_analyses) * 100) if turn_analyses else 0.0,
        'most_used_indicators': [
            {'indicator': ind, 'count': count}
            for ind, count in most_used_indicators
        ],
        'empathy_consistency': float(1.0 - np.std(empathy_scores)) if empathy_scores else 0.0
    }


def _calculate_empathy_responsiveness(turn_analyses: List[Dict[str, Any]],
                                     transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Calculate how responsive empathy is to emotional content."""
    if len(turn_analyses) < 2:
        return {'responsiveness_score': 0.0}

    responsive_pairs = 0
    total_emotional_turns = 0

    for i in range(len(turn_analyses) - 1):
        current_turn = turn_analyses[i]
        next_turn = turn_analyses[i + 1]

        # Check if current turn has emotional content
        current_text = transcript[i].get('text', '')
        emotion_level = _detect_emotional_content(current_text)

        if emotion_level > 0.4:
            total_emotional_turns += 1

            # Check if next turn shows empathy
            if next_turn['empathy_score'] >= 0.4:
                responsive_pairs += 1

    responsiveness_score = (responsive_pairs / total_emotional_turns) if total_emotional_turns > 0 else 0.0

    return {
        'responsiveness_score': float(responsiveness_score),
        'total_emotional_turns': total_emotional_turns,
        'responsive_pairs': responsive_pairs,
        'responsiveness_category': 'high' if responsiveness_score >= 0.7 else 'moderate' if responsiveness_score >= 0.4 else 'low'
    }


def _assess_overall_empathy_quality(interviewer_empathy: Dict[str, Any],
                                    trajectory: List[float],
                                    problematic_moments: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Assess overall empathy quality of interview."""
    avg_score = interviewer_empathy.get('average_empathy_score', 0.0)
    consistency = interviewer_empathy.get('empathy_consistency', 0.0)
    num_problems = len(problematic_moments)

    # Calculate quality score
    quality_score = (avg_score * 0.5) + (consistency * 0.3) - (num_problems * 0.05)
    quality_score = max(0.0, min(1.0, quality_score))

    # Determine rating
    if quality_score >= 0.8:
        rating = 'excellent'
    elif quality_score >= 0.6:
        rating = 'good'
    elif quality_score >= 0.4:
        rating = 'fair'
    else:
        rating = 'needs_improvement'

    return {
        'quality_score': float(quality_score),
        'quality_rating': rating,
        'strengths': _identify_strengths(interviewer_empathy),
        'areas_for_improvement': _identify_improvements(interviewer_empathy, num_problems)
    }


def _identify_strengths(interviewer_empathy: Dict[str, Any]) -> List[str]:
    """Identify empathy strengths."""
    strengths = []

    avg_score = interviewer_empathy.get('average_empathy_score', 0.0)
    if avg_score >= 0.6:
        strengths.append('High overall empathy')

    consistency = interviewer_empathy.get('empathy_consistency', 0.0)
    if consistency >= 0.7:
        strengths.append('Consistent empathetic responses')

    indicators = interviewer_empathy.get('most_used_indicators', [])
    if indicators:
        top_indicator = indicators[0]['indicator']
        strengths.append(f'Strong use of {top_indicator.replace("_", " ")}')

    return strengths if strengths else ['Shows some empathy']


def _identify_improvements(interviewer_empathy: Dict[str, Any],
                          num_problems: int) -> List[str]:
    """Identify areas for improvement."""
    improvements = []

    avg_score = interviewer_empathy.get('average_empathy_score', 0.0)
    if avg_score < 0.4:
        improvements.append('Increase use of empathetic language')

    if num_problems > 2:
        improvements.append('Avoid dismissive or minimizing language')

    consistency = interviewer_empathy.get('empathy_consistency', 0.0)
    if consistency < 0.5:
        improvements.append('Maintain consistent empathy throughout')

    percentage = interviewer_empathy.get('empathetic_turn_percentage', 0.0)
    if percentage < 40:
        improvements.append('Respond empathetically more frequently')

    return improvements if improvements else ['Continue current approach']


def _detect_distress(text: str) -> float:
    """Detect distress level in text."""
    text_lower = text.lower()

    distress_indicators = [
        'worried', 'scared', 'afraid', 'anxious', 'terrified', 'panic',
        'stressed', 'overwhelmed', 'can\'t cope', 'too much', 'breaking down',
        'crying', 'tears', 'sobbing', 'desperate', 'hopeless', 'helpless'
    ]

    count = sum(1 for indicator in distress_indicators if indicator in text_lower)

    return min(count / 3.0, 1.0)


def _detect_emotional_content(text: str) -> float:
    """Detect emotional content level in text."""
    text_lower = text.lower()

    emotional_words = [
        'feel', 'feeling', 'felt', 'emotion', 'happy', 'sad', 'angry',
        'worried', 'excited', 'scared', 'love', 'hate', 'frustrated',
        'disappointed', 'grateful', 'blessed', 'anxious', 'nervous'
    ]

    count = sum(1 for word in emotional_words if word in text_lower)

    return min(count / 4.0, 1.0)


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'transformers': TRANSFORMERS_AVAILABLE,
        'has_empathy_detection': True,  # Pattern-based always available
        'advanced_models_available': False  # Would need fine-tuned empathy models
    }


if __name__ == '__main__':
    # Test the module
    test_interview = {
        'transcript': [
            {
                'speaker': 'interviewer',
                'text': 'How have you been feeling about your pregnancy?'
            },
            {
                'speaker': 'persona',
                'text': 'I\'m really scared about the delivery. I can\'t stop worrying about it.'
            },
            {
                'speaker': 'interviewer',
                'text': 'That sounds really difficult. I can understand why you\'d feel worried about that. Many women feel this way. Tell me more about what specifically worries you.'
            },
            {
                'speaker': 'persona',
                'text': 'I\'m afraid something will go wrong. What if the baby gets hurt?'
            },
            {
                'speaker': 'interviewer',
                'text': 'Don\'t worry, everything will be fine. You just need to think positive.'
            },
            {
                'speaker': 'persona',
                'text': 'I guess... but it\'s hard.'
            },
            {
                'speaker': 'interviewer',
                'text': 'I hear you. That fear makes complete sense, and it\'s natural to feel this way. We\'re here to support you through this.'
            }
        ]
    }

    print("Empathy Detection Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Empathy detection available: {status['has_empathy_detection']}")
    print(f"Transformers available: {status['transformers']}")
    print()

    # Analyze empathy
    print("Analyzing test interview...")
    result = analyze_interview_empathy(test_interview)

    print(f"\nINTERVIEWER EMPATHY:")
    interviewer = result['interviewer_empathy']
    print(f"  Average Empathy Score: {interviewer['average_empathy_score']:.3f}")
    print(f"  Empathy Level: {interviewer['empathy_level']}")
    print(f"  Empathetic Turn %: {interviewer['empathetic_turn_percentage']:.1f}%")
    print(f"  Consistency: {interviewer['empathy_consistency']:.3f}")

    print(f"\n  Most Used Indicators:")
    for ind in interviewer['most_used_indicators']:
        print(f"    - {ind['indicator'].replace('_', ' ').title()}: {ind['count']} times")

    print(f"\nHIGH EMPATHY MOMENTS:")
    for moment in result['high_empathy_moments'][:3]:
        print(f"  Turn {moment['turn_index']} (position {moment['position']:.2f})")
        print(f"    Score: {moment['empathy_score']:.3f}")
        print(f"    Indicators: {', '.join(moment['indicators'])}")

    print(f"\nPROBLEMATIC MOMENTS:")
    for moment in result['problematic_moments']:
        print(f"  Turn {moment['turn_index']} (position {moment['position']:.2f})")
        print(f"    Score: {moment['empathy_score']:.3f}")
        print(f"    Issues: {', '.join(moment['negative_indicators'])}")

    print(f"\nOVERALL QUALITY:")
    quality = result['overall_quality']
    print(f"  Quality Score: {quality['quality_score']:.3f}")
    print(f"  Rating: {quality['quality_rating']}")
    print(f"  Strengths: {', '.join(quality['strengths'])}")
    print(f"  Areas for Improvement: {', '.join(quality['areas_for_improvement'])}")

    # Test empathy gap
    print(f"\nEMPATHY GAP ANALYSIS:")
    gap_analysis = measure_empathy_gap(test_interview)
    print(f"  Number of Gaps: {gap_analysis['num_gaps']}")
    if gap_analysis['num_gaps'] > 0:
        print(f"  Average Gap Magnitude: {gap_analysis['average_gap_magnitude']:.3f}")
        print(f"  Significant Gaps: {gap_analysis['has_significant_gaps']}")
