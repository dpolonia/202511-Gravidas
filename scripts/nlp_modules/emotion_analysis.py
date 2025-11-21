"""
Emotion Analysis Module
========================

Detects multiple discrete emotions (joy, fear, anger, sadness, disgust,
surprise, trust, anticipation) from interview transcripts using NRCLex.

Capability #2 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional
from collections import Counter

logger = logging.getLogger(__name__)

# Try to import NRCLex
try:
    from nrclex import NRCLex
    NRCLEX_AVAILABLE = True
    logger.info("✓ NRCLex emotion analysis available")
except ImportError:
    NRCLEX_AVAILABLE = False
    logger.warning("NRCLex not available. Install with: pip install NRCLex")

# Alternative: text2emotion (backup)
try:
    import text2emotion as te
    TEXT2EMOTION_AVAILABLE = True
    logger.info("✓ text2emotion available as backup")
except ImportError:
    TEXT2EMOTION_AVAILABLE = False


def analyze_emotions(text: str, method: str = 'nrclex') -> Dict[str, Any]:
    """
    Analyze emotions in text using NRCLex or text2emotion.

    Args:
        text: Input text (interview transcript)
        method: 'nrclex' or 'text2emotion'

    Returns:
        Dictionary with emotion analysis:
        {
            'emotions': {
                'fear': 0.15,
                'anger': 0.05,
                'anticipation': 0.20,
                'trust': 0.25,
                'surprise': 0.10,
                'positive': 0.35,
                'negative': 0.10,
                'sadness': 0.08,
                'disgust': 0.02,
                'joy': 0.30
            },
            'dominant_emotion': 'joy',
            'emotional_intensity': 0.65,  # 0-1 scale
            'emotional_valence': 0.25,    # -1 (negative) to +1 (positive)
            'top_emotional_words': [('happy', 'joy'), ('worried', 'fear'), ...],
            'method': 'nrclex'
        }
    """
    if method == 'nrclex' and NRCLEX_AVAILABLE:
        return _analyze_with_nrclex(text)
    elif method == 'text2emotion' and TEXT2EMOTION_AVAILABLE:
        return _analyze_with_text2emotion(text)
    else:
        # Fallback to rule-based
        return _analyze_with_rules(text)


def _analyze_with_nrclex(text: str) -> Dict[str, Any]:
    """Analyze emotions using NRCLex (NRC Emotion Lexicon)."""
    try:
        emotion_obj = NRCLex(text)

        # Get raw emotion frequencies
        raw_emotions = emotion_obj.affect_frequencies

        # NRCLex provides: fear, anger, anticipation, trust, surprise,
        # positive, negative, sadness, disgust, joy
        emotions = {
            'fear': raw_emotions.get('fear', 0.0),
            'anger': raw_emotions.get('anger', 0.0),
            'anticipation': raw_emotions.get('anticipation', 0.0),
            'trust': raw_emotions.get('trust', 0.0),
            'surprise': raw_emotions.get('surprise', 0.0),
            'positive': raw_emotions.get('positive', 0.0),
            'negative': raw_emotions.get('negative', 0.0),
            'sadness': raw_emotions.get('sadness', 0.0),
            'disgust': raw_emotions.get('disgust', 0.0),
            'joy': raw_emotions.get('joy', 0.0)
        }

        # Find dominant emotion (excluding positive/negative sentiment)
        discrete_emotions = {k: v for k, v in emotions.items()
                            if k not in ['positive', 'negative']}
        dominant_emotion = max(discrete_emotions.items(),
                              key=lambda x: x[1])[0] if discrete_emotions else 'neutral'

        # Calculate emotional intensity (sum of all emotions)
        emotional_intensity = sum(discrete_emotions.values())

        # Calculate valence (positive - negative)
        emotional_valence = emotions['positive'] - emotions['negative']

        # Get top emotional words
        top_words = emotion_obj.top_emotions[:10] if hasattr(emotion_obj, 'top_emotions') else []

        return {
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'emotional_intensity': min(emotional_intensity, 1.0),
            'emotional_valence': max(-1.0, min(1.0, emotional_valence)),
            'top_emotional_words': top_words,
            'raw_emotion_scores': emotion_obj.raw_emotion_scores if hasattr(emotion_obj, 'raw_emotion_scores') else {},
            'method': 'nrclex'
        }

    except Exception as e:
        logger.error(f"Error in NRCLex emotion analysis: {e}")
        return {
            'emotions': {},
            'error': str(e),
            'method': 'nrclex'
        }


def _analyze_with_text2emotion(text: str) -> Dict[str, Any]:
    """Analyze emotions using text2emotion (backup method)."""
    try:
        emotions_raw = te.get_emotion(text)

        # text2emotion provides: Happy, Angry, Surprise, Sad, Fear
        # Map to our standard set
        emotions = {
            'joy': emotions_raw.get('Happy', 0.0),
            'anger': emotions_raw.get('Angry', 0.0),
            'surprise': emotions_raw.get('Surprise', 0.0),
            'sadness': emotions_raw.get('Sad', 0.0),
            'fear': emotions_raw.get('Fear', 0.0),
            'trust': 0.0,  # Not provided by text2emotion
            'anticipation': 0.0,
            'disgust': 0.0,
            'positive': emotions_raw.get('Happy', 0.0),
            'negative': emotions_raw.get('Sad', 0.0) + emotions_raw.get('Angry', 0.0)
        }

        discrete_emotions = {k: v for k, v in emotions.items()
                            if k not in ['positive', 'negative']}
        dominant_emotion = max(discrete_emotions.items(),
                              key=lambda x: x[1])[0] if discrete_emotions else 'neutral'

        emotional_intensity = sum(discrete_emotions.values())
        emotional_valence = emotions['positive'] - emotions['negative']

        return {
            'emotions': emotions,
            'dominant_emotion': dominant_emotion,
            'emotional_intensity': min(emotional_intensity, 1.0),
            'emotional_valence': max(-1.0, min(1.0, emotional_valence)),
            'top_emotional_words': [],
            'method': 'text2emotion'
        }

    except Exception as e:
        logger.error(f"Error in text2emotion analysis: {e}")
        return {
            'emotions': {},
            'error': str(e),
            'method': 'text2emotion'
        }


def _analyze_with_rules(text: str) -> Dict[str, Any]:
    """
    Fallback rule-based emotion detection using pregnancy-specific keywords.

    This works even without external libraries.
    """
    text_lower = text.lower()

    # Pregnancy-specific emotion keywords
    emotion_keywords = {
        'joy': ['happy', 'excited', 'thrilled', 'delighted', 'joyful', 'wonderful',
                'amazing', 'blessed', 'grateful', 'love', 'beautiful'],
        'fear': ['worried', 'scared', 'afraid', 'anxious', 'terrified', 'nervous',
                 'panic', 'concern', 'frightened', 'stress'],
        'anticipation': ['waiting', 'expecting', 'looking forward', 'hope', 'plan',
                        'prepare', 'ready', 'soon', 'future', 'upcoming'],
        'trust': ['confident', 'trust', 'believe', 'faith', 'sure', 'certain',
                  'reassured', 'comfortable', 'safe', 'secure'],
        'surprise': ['surprised', 'unexpected', 'shocked', 'sudden', 'amazed',
                    'astonished', 'didn\'t expect'],
        'sadness': ['sad', 'depressed', 'upset', 'disappointed', 'grief', 'loss',
                   'crying', 'tears', 'lonely', 'miserable'],
        'anger': ['angry', 'frustrated', 'annoyed', 'irritated', 'mad', 'furious',
                 'upset', 'resentful'],
        'disgust': ['disgusted', 'revolted', 'sick', 'nauseous', 'gross', 'awful',
                   'terrible', 'horrible']
    }

    # Count emotion keywords
    emotion_counts = {emotion: 0 for emotion in emotion_keywords}

    for emotion, keywords in emotion_keywords.items():
        for keyword in keywords:
            emotion_counts[emotion] += text_lower.count(keyword)

    # Normalize by text length (per 100 words)
    word_count = len(text_lower.split())
    if word_count == 0:
        word_count = 1

    emotions = {
        emotion: min(count / word_count * 100, 1.0)
        for emotion, count in emotion_counts.items()
    }

    # Add positive/negative
    emotions['positive'] = emotions['joy'] + emotions['trust'] + emotions['anticipation']
    emotions['negative'] = emotions['fear'] + emotions['sadness'] + emotions['anger'] + emotions['disgust']

    discrete_emotions = {k: v for k, v in emotions.items()
                        if k not in ['positive', 'negative']}
    dominant_emotion = max(discrete_emotions.items(),
                          key=lambda x: x[1])[0] if discrete_emotions else 'neutral'

    emotional_intensity = sum(discrete_emotions.values())
    emotional_valence = emotions['positive'] - emotions['negative']

    return {
        'emotions': emotions,
        'dominant_emotion': dominant_emotion,
        'emotional_intensity': min(emotional_intensity, 1.0),
        'emotional_valence': max(-1.0, min(1.0, emotional_valence)),
        'top_emotional_words': [],
        'method': 'rule-based'
    }


def analyze_interview_emotions(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive emotion analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Dictionary with emotion analysis for entire interview and per-speaker
    """
    # Extract full interview text
    transcript = interview_data.get('transcript', [])
    full_text = ' '.join([turn.get('text', '') for turn in transcript])

    # Overall emotion analysis
    overall_emotions = analyze_emotions(full_text)

    # Per-speaker analysis
    persona_texts = []
    interviewer_texts = []

    for turn in transcript:
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown')

        if speaker.lower() in ['persona', 'participant', 'patient']:
            persona_texts.append(text)
        elif speaker.lower() in ['interviewer', 'doctor', 'clinician']:
            interviewer_texts.append(text)

    persona_emotions = analyze_emotions(' '.join(persona_texts)) if persona_texts else None
    interviewer_emotions = analyze_emotions(' '.join(interviewer_texts)) if interviewer_texts else None

    # Emotion trajectory (analyze by thirds of interview)
    third = len(transcript) // 3
    if third > 0:
        beginning_text = ' '.join([t.get('text', '') for t in transcript[:third]])
        middle_text = ' '.join([t.get('text', '') for t in transcript[third:2*third]])
        end_text = ' '.join([t.get('text', '') for t in transcript[2*third:]])

        emotion_trajectory = {
            'beginning': analyze_emotions(beginning_text),
            'middle': analyze_emotions(middle_text),
            'end': analyze_emotions(end_text)
        }
    else:
        emotion_trajectory = None

    return {
        'overall_emotions': overall_emotions,
        'persona_emotions': persona_emotions,
        'interviewer_emotions': interviewer_emotions,
        'emotion_trajectory': emotion_trajectory,
        'emotional_complexity': calculate_emotional_complexity(overall_emotions)
    }


def calculate_emotional_complexity(emotion_data: Dict[str, Any]) -> float:
    """
    Calculate emotional complexity score (0-100).

    Based on:
    - Emotional intensity
    - Number of different emotions present
    - Emotional valence (mixed emotions)
    """
    emotions = emotion_data.get('emotions', {})

    # Remove positive/negative from discrete emotion count
    discrete_emotions = {k: v for k, v in emotions.items()
                        if k not in ['positive', 'negative'] and v > 0.05}

    # Intensity score (0-30)
    intensity = emotion_data.get('emotional_intensity', 0.0)
    intensity_score = min(intensity * 30, 30)

    # Diversity score (0-40) - more diverse emotions = higher complexity
    diversity_score = min(len(discrete_emotions) * 5, 40)

    # Ambivalence score (0-30) - mixed emotions = higher complexity
    valence = abs(emotion_data.get('emotional_valence', 0.0))
    ambivalence_score = (1.0 - valence) * 30  # Lower valence = more ambivalence

    total_score = intensity_score + diversity_score + ambivalence_score

    return min(total_score, 100.0)


def get_emotion_summary(all_interviews_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate emotion summary statistics across all interviews.

    Args:
        all_interviews_analysis: List of emotion analysis results

    Returns:
        Summary statistics dictionary
    """
    if not all_interviews_analysis:
        return {}

    # Aggregate dominant emotions
    dominant_emotions = []
    emotional_intensities = []
    emotional_valences = []

    for analysis in all_interviews_analysis:
        overall = analysis.get('overall_emotions', {})
        if overall:
            dominant_emotions.append(overall.get('dominant_emotion', 'neutral'))
            emotional_intensities.append(overall.get('emotional_intensity', 0.0))
            emotional_valences.append(overall.get('emotional_valence', 0.0))

    # Count emotion frequencies
    emotion_counts = Counter(dominant_emotions)

    return {
        'total_interviews': len(all_interviews_analysis),
        'dominant_emotions_distribution': dict(emotion_counts),
        'most_common_emotion': emotion_counts.most_common(1)[0] if emotion_counts else ('neutral', 0),
        'average_emotional_intensity': sum(emotional_intensities) / len(emotional_intensities) if emotional_intensities else 0.0,
        'average_emotional_valence': sum(emotional_valences) / len(emotional_valences) if emotional_valences else 0.0,
        'emotional_range': {
            'min_intensity': min(emotional_intensities) if emotional_intensities else 0.0,
            'max_intensity': max(emotional_intensities) if emotional_intensities else 0.0,
            'min_valence': min(emotional_valences) if emotional_valences else 0.0,
            'max_valence': max(emotional_valences) if emotional_valences else 0.0
        }
    }


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'nrclex': NRCLEX_AVAILABLE,
        'text2emotion': TEXT2EMOTION_AVAILABLE,
        'has_emotion_analysis': NRCLEX_AVAILABLE or TEXT2EMOTION_AVAILABLE
    }


if __name__ == '__main__':
    # Test the module
    test_text = """
    I'm so excited about the baby coming! But I'm also really worried about
    the delivery. The doctor said everything looks good, which is reassuring.
    Sometimes I feel sad thinking about all the changes ahead. My partner has
    been amazing and supportive. I'm nervous but also looking forward to
    meeting our little one. The morning sickness has been terrible though.
    """

    print("Emotion Analysis Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"NRCLex available: {status['nrclex']}")
    print(f"text2emotion available: {status['text2emotion']}")
    print(f"Emotion analysis available: {status['has_emotion_analysis']}")
    print()

    # Analyze emotions
    result = analyze_emotions(test_text)

    print(f"Method used: {result.get('method', 'unknown')}")
    print(f"\nDominant emotion: {result.get('dominant_emotion', 'N/A')}")
    print(f"Emotional intensity: {result.get('emotional_intensity', 0.0):.2f}")
    print(f"Emotional valence: {result.get('emotional_valence', 0.0):.2f}")

    print(f"\nEmotion breakdown:")
    emotions = result.get('emotions', {})
    for emotion, score in sorted(emotions.items(), key=lambda x: x[1], reverse=True):
        if score > 0.01:
            print(f"  {emotion}: {score:.3f}")

    if result.get('top_emotional_words'):
        print(f"\nTop emotional words:")
        for word_info in result['top_emotional_words'][:5]:
            print(f"  - {word_info}")
