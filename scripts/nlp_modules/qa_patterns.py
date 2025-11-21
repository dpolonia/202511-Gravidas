"""
Question-Answer Pattern Analysis Module
========================================

Analyzes interview question types, response patterns, and communication
effectiveness using pattern matching and dependency parsing.

Capability #5 of 11 Advanced NLP Enhancements
"""

import logging
import re
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# Try to import spaCy for dependency parsing
try:
    import spacy
    try:
        NLP_MODEL = spacy.load("en_core_web_sm")
        SPACY_AVAILABLE = True
        logger.info("✓ spaCy available for QA pattern analysis")
    except OSError:
        logger.warning("spaCy model not found. Install with: python -m spacy download en_core_web_sm")
        SPACY_AVAILABLE = False
        NLP_MODEL = None
except ImportError:
    SPACY_AVAILABLE = False
    NLP_MODEL = None
    logger.warning("spaCy not available. Install with: pip install spacy")


# Question type patterns
QUESTION_PATTERNS = {
    'open_ended': [
        r'\bhow (do|did|does|would|will|can|could|should)',
        r'\bwhat (is|are|was|were|would|will)',
        r'\bwhy (do|did|does|would|will)',
        r'\btell me (about|more)',
        r'\bcan you (describe|explain|talk)',
        r'\bcould you (describe|explain|share)'
    ],
    'closed_ended': [
        r'\b(do|did|does|are|is|was|were|have|has|had|will|would|can|could) you',
        r'\bhave you (ever|been)',
        r'\bis (it|there|that)',
        r'^(yes|no)[,?]'
    ],
    'follow_up': [
        r'\band (then|what|how)',
        r'\bwhat else',
        r'\banything else',
        r'\bcan you (tell|share) me more'
    ],
    'reflective': [
        r'\bit sounds like',
        r'\bso (what )?you\'?re? (saying|feeling)',
        r'\bif I understand',
        r'\blet me (see if|check)'
    ],
    'empathetic': [
        r'\bthat (must|sounds) (be|like)',
        r'\bI (can understand|imagine)',
        r'\bthat\'?s? (difficult|challenging|hard)',
        r'\bhow (are|do) you (feeling|coping)'
    ]
}


def classify_question(text: str) -> Dict[str, Any]:
    """
    Classify a question into types.

    Args:
        text: Question text

    Returns:
        Dictionary with question classification:
        {
            'type': 'open_ended',
            'is_question': True,
            'question_words': ['how', 'what'],
            'complexity': 'high',
            'empathy_level': 'low'
        }
    """
    text_lower = text.lower().strip()

    # Check if it's actually a question
    is_question = (
        '?' in text or
        any(text_lower.startswith(word) for word in ['how', 'what', 'why', 'when', 'where', 'who', 'which', 'can', 'could', 'would', 'do', 'does', 'did', 'is', 'are'])
    )

    if not is_question:
        return {
            'type': 'statement',
            'is_question': False,
            'question_words': [],
            'complexity': 'n/a',
            'empathy_level': 'n/a'
        }

    # Classify by pattern matching
    matched_types = []
    for q_type, patterns in QUESTION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                matched_types.append(q_type)
                break

    # Determine primary type
    if 'empathetic' in matched_types:
        primary_type = 'empathetic'
    elif 'reflective' in matched_types:
        primary_type = 'reflective'
    elif 'follow_up' in matched_types:
        primary_type = 'follow_up'
    elif 'open_ended' in matched_types:
        primary_type = 'open_ended'
    elif 'closed_ended' in matched_types:
        primary_type = 'closed_ended'
    else:
        primary_type = 'other'

    # Extract question words (5W1H)
    question_words = []
    for word in ['how', 'what', 'why', 'when', 'where', 'who', 'which']:
        if word in text_lower:
            question_words.append(word)

    # Determine complexity
    complexity = 'low'
    if len(text.split()) > 15 or len(question_words) > 1:
        complexity = 'high'
    elif len(text.split()) > 8 or question_words:
        complexity = 'medium'

    # Determine empathy level
    empathy_keywords = ['feel', 'feeling', 'difficult', 'challenging', 'understand', 'imagine', 'sounds', 'must be']
    empathy_count = sum(1 for keyword in empathy_keywords if keyword in text_lower)

    if empathy_count >= 2 or 'empathetic' in matched_types:
        empathy_level = 'high'
    elif empathy_count == 1:
        empathy_level = 'medium'
    else:
        empathy_level = 'low'

    return {
        'type': primary_type,
        'all_types': matched_types,
        'is_question': True,
        'question_words': question_words,
        'complexity': complexity,
        'empathy_level': empathy_level,
        'word_count': len(text.split())
    }


def analyze_response_pattern(response: str, question_type: str = 'unknown') -> Dict[str, Any]:
    """
    Analyze response patterns.

    Args:
        response: Response text
        question_type: Type of question that prompted this response

    Returns:
        Dictionary with response analysis:
        {
            'word_count': 45,
            'sentence_count': 3,
            'elaboration': 'high',
            'specificity': 'medium',
            'confidence_level': 'medium',
            'contains_hedging': False
        }
    """
    # Basic statistics
    word_count = len(response.split())
    sentence_count = len(re.split(r'[.!?]+', response.strip()))

    # Elaboration level
    if word_count > 50:
        elaboration = 'high'
    elif word_count > 20:
        elaboration = 'medium'
    else:
        elaboration = 'low'

    # Specificity markers (numbers, dates, names, specific terms)
    specificity_markers = len(re.findall(r'\b\d+\b', response))  # Numbers
    specificity_markers += len(re.findall(r'\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|march|april|may|june|july|august|september|october|november|december)\b', response.lower()))  # Dates

    if specificity_markers >= 3:
        specificity = 'high'
    elif specificity_markers >= 1:
        specificity = 'medium'
    else:
        specificity = 'low'

    # Confidence level (hedging language)
    hedging_words = ['maybe', 'perhaps', 'possibly', 'might', 'could', 'I think', 'I guess', 'sort of', 'kind of', 'probably', 'not sure']
    hedging_count = sum(1 for word in hedging_words if word in response.lower())

    contains_hedging = hedging_count > 0

    if hedging_count >= 3:
        confidence_level = 'low'
    elif hedging_count >= 1:
        confidence_level = 'medium'
    else:
        confidence_level = 'high'

    # Emotional content
    emotional_words = ['happy', 'sad', 'worried', 'excited', 'scared', 'anxious', 'upset', 'frustrated', 'relieved', 'grateful']
    emotional_count = sum(1 for word in emotional_words if word in response.lower())

    emotional_content = 'high' if emotional_count >= 2 else ('medium' if emotional_count == 1 else 'low')

    return {
        'word_count': word_count,
        'sentence_count': sentence_count,
        'elaboration': elaboration,
        'specificity': specificity,
        'confidence_level': confidence_level,
        'contains_hedging': contains_hedging,
        'hedging_count': hedging_count,
        'emotional_content': emotional_content,
        'appropriateness': _assess_appropriateness(word_count, question_type)
    }


def _assess_appropriateness(word_count: int, question_type: str) -> str:
    """Assess if response length is appropriate for question type."""
    if question_type == 'open_ended':
        return 'appropriate' if word_count > 15 else 'too_brief'
    elif question_type == 'closed_ended':
        return 'appropriate' if word_count < 30 else 'over_elaborated'
    else:
        return 'appropriate'


def analyze_turn_taking(transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Analyze turn-taking patterns in the interview.

    Args:
        transcript: List of turn dictionaries with 'speaker' and 'text'

    Returns:
        Dictionary with turn-taking analysis
    """
    if not transcript:
        return {'error': 'Empty transcript'}

    speakers = [turn.get('speaker', 'unknown') for turn in transcript]
    texts = [turn.get('text', '') for turn in transcript]

    # Identify speaker types
    interviewer_labels = ['interviewer', 'doctor', 'clinician', 'nurse']
    persona_labels = ['persona', 'participant', 'patient', 'interviewee']

    interviewer_turns = []
    persona_turns = []

    for idx, speaker in enumerate(speakers):
        speaker_lower = speaker.lower()
        if any(label in speaker_lower for label in interviewer_labels):
            interviewer_turns.append(idx)
        elif any(label in speaker_lower for label in persona_labels):
            persona_turns.append(idx)

    # Calculate statistics
    total_turns = len(transcript)
    interviewer_count = len(interviewer_turns)
    persona_count = len(persona_turns)

    # Average turn lengths
    interviewer_lengths = [len(texts[i].split()) for i in interviewer_turns]
    persona_lengths = [len(texts[i].split()) for i in persona_turns]

    avg_interviewer_length = sum(interviewer_lengths) / len(interviewer_lengths) if interviewer_lengths else 0
    avg_persona_length = sum(persona_lengths) / len(persona_lengths) if persona_lengths else 0

    # Turn distribution
    turn_ratio = persona_count / interviewer_count if interviewer_count > 0 else 0

    # Interruptions (consecutive turns by same speaker)
    interruptions = 0
    for i in range(1, len(speakers)):
        if speakers[i] == speakers[i-1]:
            interruptions += 1

    # Balance assessment
    if 0.8 <= turn_ratio <= 1.2:
        balance = 'balanced'
    elif turn_ratio > 1.2:
        balance = 'persona_dominant'
    else:
        balance = 'interviewer_dominant'

    return {
        'total_turns': total_turns,
        'interviewer_turns': interviewer_count,
        'persona_turns': persona_count,
        'turn_ratio': turn_ratio,
        'avg_interviewer_turn_length': avg_interviewer_length,
        'avg_persona_turn_length': avg_persona_length,
        'interruptions': interruptions,
        'balance': balance
    }


def analyze_interview_qa_patterns(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive QA pattern analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Dictionary with QA pattern analysis
    """
    transcript = interview_data.get('transcript', [])

    if not transcript:
        return {'error': 'No transcript found'}

    # Analyze each turn
    questions = []
    responses = []

    for i, turn in enumerate(transcript):
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown').lower()

        # Classify questions
        q_analysis = classify_question(text)
        if q_analysis['is_question']:
            q_analysis['turn_index'] = i
            q_analysis['speaker'] = speaker
            questions.append(q_analysis)

            # If there's a next turn, analyze the response
            if i + 1 < len(transcript):
                response_text = transcript[i + 1].get('text', '')
                r_analysis = analyze_response_pattern(response_text, q_analysis['type'])
                r_analysis['question_type'] = q_analysis['type']
                r_analysis['turn_index'] = i + 1
                responses.append(r_analysis)

    # Question type distribution
    question_types = [q['type'] for q in questions]
    type_distribution = dict(Counter(question_types))

    # Empathy distribution
    empathy_levels = [q['empathy_level'] for q in questions if q['empathy_level'] != 'n/a']
    empathy_distribution = dict(Counter(empathy_levels))

    # Response quality metrics
    avg_response_length = sum(r['word_count'] for r in responses) / len(responses) if responses else 0
    high_elaboration_responses = sum(1 for r in responses if r['elaboration'] == 'high')
    high_confidence_responses = sum(1 for r in responses if r['confidence_level'] == 'high')

    # Turn-taking analysis
    turn_taking = analyze_turn_taking(transcript)

    # Communication effectiveness score (0-100)
    effectiveness_score = calculate_communication_effectiveness(
        question_types, responses, turn_taking
    )

    return {
        'total_questions': len(questions),
        'total_responses': len(responses),
        'question_type_distribution': type_distribution,
        'empathy_distribution': empathy_distribution,
        'average_response_length': avg_response_length,
        'high_elaboration_rate': high_elaboration_responses / len(responses) if responses else 0,
        'high_confidence_rate': high_confidence_responses / len(responses) if responses else 0,
        'turn_taking': turn_taking,
        'communication_effectiveness': effectiveness_score,
        'questions': questions,
        'responses': responses
    }


def calculate_communication_effectiveness(question_types: List[str],
                                         responses: List[Dict],
                                         turn_taking: Dict) -> float:
    """
    Calculate communication effectiveness score (0-100).

    Based on:
    - Question type variety
    - Response quality
    - Turn balance
    """
    score = 0.0

    # Question variety (0-30 points)
    unique_types = len(set(question_types))
    variety_score = min(unique_types * 6, 30)
    score += variety_score

    # Open-ended ratio (0-20 points)
    open_ended_count = sum(1 for qt in question_types if qt == 'open_ended')
    open_ratio = open_ended_count / len(question_types) if question_types else 0
    score += open_ratio * 20

    # Response quality (0-30 points)
    if responses:
        avg_elaboration = sum(1 for r in responses if r['elaboration'] in ['medium', 'high']) / len(responses)
        score += avg_elaboration * 30

    # Turn balance (0-20 points)
    balance = turn_taking.get('balance', 'unbalanced')
    if balance == 'balanced':
        score += 20
    elif balance == 'persona_dominant':
        score += 15  # Still okay, persona should talk more
    else:
        score += 5

    return min(score, 100.0)


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'spacy': SPACY_AVAILABLE,
        'model_loaded': NLP_MODEL is not None,
        'has_qa_analysis': True  # Works with or without spaCy
    }


if __name__ == '__main__':
    # Test the module
    test_questions = [
        "How are you feeling today?",
        "Have you experienced any morning sickness?",
        "Can you tell me more about your symptoms?",
        "It sounds like that's been really difficult for you. How are you coping?",
        "What concerns do you have about the delivery?"
    ]

    test_responses = [
        "I'm feeling okay, a bit tired.",
        "Yes, especially in the mornings.",
        "Well, I've been having nausea and some back pain. It started about two weeks ago and has been pretty constant.",
        "I'm trying to stay positive. My family has been really supportive, which helps a lot.",
        "I'm worried about the pain and whether I'll need a c-section. The doctor mentioned some risks."
    ]

    print("QA Pattern Analysis Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"spaCy available: {status['spacy']}")
    print(f"Model loaded: {status['model_loaded']}")
    print(f"QA analysis available: {status['has_qa_analysis']}")
    print()

    print("Question Analysis:")
    print("-" * 50)
    for i, question in enumerate(test_questions, 1):
        result = classify_question(question)
        print(f"\n{i}. {question}")
        print(f"   Type: {result['type']}")
        print(f"   Complexity: {result['complexity']}")
        print(f"   Empathy: {result['empathy_level']}")

    print("\n\nResponse Analysis:")
    print("-" * 50)
    for i, (response, q_type) in enumerate(zip(test_responses, ['open_ended'] * len(test_responses)), 1):
        result = analyze_response_pattern(response, q_type)
        print(f"\n{i}. {response[:50]}...")
        print(f"   Words: {result['word_count']}")
        print(f"   Elaboration: {result['elaboration']}")
        print(f"   Confidence: {result['confidence_level']}")
        print(f"   Specificity: {result['specificity']}")
