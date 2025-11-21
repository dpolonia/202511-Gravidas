"""
BERT Sentiment Analysis Module
================================

Transformer-based sentiment analysis using pre-trained BERT models.
More accurate and context-aware than traditional methods like VADER.

Capability #4 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)

# Try to import transformers
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    import torch
    TRANSFORMERS_AVAILABLE = True
    logger.info("✓ Transformers library available for BERT sentiment")
except ImportError:
    TRANSFORMERS_AVAILABLE = False
    logger.warning("Transformers not available. Install with: pip install transformers torch")

# Global model cache
_sentiment_model = None
_model_name = None


def load_sentiment_model(model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english'):
    """
    Load a pre-trained sentiment analysis model.

    Popular models:
    - 'distilbert-base-uncased-finetuned-sst-2-english' (Fast, good quality)
    - 'cardiffnlp/twitter-roberta-base-sentiment' (Social media text)
    - 'nlptown/bert-base-multilingual-uncased-sentiment' (5-star ratings)
    - 'j-hartmann/emotion-english-distilroberta-base' (Emotions)
    """
    global _sentiment_model, _model_name

    if not TRANSFORMERS_AVAILABLE:
        return None

    if _sentiment_model is not None and _model_name == model_name:
        return _sentiment_model

    try:
        logger.info(f"Loading BERT sentiment model: {model_name}")
        _sentiment_model = pipeline(
            "sentiment-analysis",
            model=model_name,
            device=0 if torch.cuda.is_available() else -1  # Use GPU if available
        )
        _model_name = model_name
        logger.info("✓ BERT sentiment model loaded successfully")
        return _sentiment_model
    except Exception as e:
        logger.error(f"Error loading BERT model: {e}")
        return None


def analyze_sentiment_bert(text: str,
                          model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english',
                          max_length: int = 512) -> Dict[str, Any]:
    """
    Analyze sentiment using BERT-based transformer model.

    Args:
        text: Input text
        model_name: HuggingFace model identifier
        max_length: Maximum token length (BERT limit is 512)

    Returns:
        Dictionary with sentiment analysis:
        {
            'label': 'POSITIVE' or 'NEGATIVE',
            'score': 0.95,  # Confidence score
            'positive_score': 0.95,
            'negative_score': 0.05,
            'sentiment_category': 'very_positive',
            'model': 'distilbert...'
        }
    """
    if not TRANSFORMERS_AVAILABLE:
        return {
            'error': 'Transformers library not available',
            'label': 'UNKNOWN',
            'score': 0.0
        }

    # Load model
    model = load_sentiment_model(model_name)
    if model is None:
        return {
            'error': 'Failed to load model',
            'label': 'UNKNOWN',
            'score': 0.0
        }

    try:
        # Truncate text if too long
        if len(text.split()) > max_length:
            text = ' '.join(text.split()[:max_length])

        # Run inference
        result = model(text)[0]

        label = result['label']
        score = result['score']

        # Normalize to positive/negative scores
        if label.upper() in ['POSITIVE', 'POS', '5 STARS', '4 STARS']:
            positive_score = score
            negative_score = 1.0 - score
        elif label.upper() in ['NEGATIVE', 'NEG', '1 STAR', '2 STARS']:
            negative_score = score
            positive_score = 1.0 - score
        else:  # NEUTRAL or other
            positive_score = 0.5
            negative_score = 0.5

        # Categorize sentiment
        if positive_score >= 0.8:
            category = 'very_positive'
        elif positive_score >= 0.6:
            category = 'positive'
        elif positive_score >= 0.4:
            category = 'neutral'
        elif positive_score >= 0.2:
            category = 'negative'
        else:
            category = 'very_negative'

        return {
            'label': label.upper(),
            'score': float(score),
            'positive_score': float(positive_score),
            'negative_score': float(negative_score),
            'sentiment_category': category,
            'model': model_name,
            'method': 'bert'
        }

    except Exception as e:
        logger.error(f"Error in BERT sentiment analysis: {e}")
        return {
            'error': str(e),
            'label': 'UNKNOWN',
            'score': 0.0,
            'method': 'bert'
        }


def analyze_sentiment_segments(text: str,
                               segment_size: int = 100,
                               model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english') -> Dict[str, Any]:
    """
    Analyze sentiment across text segments (for long documents).

    Useful for tracking sentiment changes throughout an interview.

    Args:
        text: Full text to analyze
        segment_size: Number of words per segment
        model_name: BERT model to use

    Returns:
        Dictionary with segment-level sentiment analysis
    """
    words = text.split()
    segments = []

    # Split into segments
    for i in range(0, len(words), segment_size):
        segment_text = ' '.join(words[i:i+segment_size])
        if segment_text.strip():
            segments.append(segment_text)

    if not segments:
        return {'error': 'No segments to analyze', 'segments': []}

    # Analyze each segment
    segment_results = []
    for idx, segment in enumerate(segments):
        result = analyze_sentiment_bert(segment, model_name)
        result['segment_id'] = idx
        result['segment_position'] = idx / len(segments)  # 0.0 to 1.0
        segment_results.append(result)

    # Calculate overall statistics
    positive_scores = [r['positive_score'] for r in segment_results if 'positive_score' in r]
    negative_scores = [r['negative_score'] for r in segment_results if 'negative_score' in r]

    overall_positive = np.mean(positive_scores) if positive_scores else 0.5
    overall_negative = np.mean(negative_scores) if negative_scores else 0.5

    # Detect sentiment trajectory
    if len(positive_scores) >= 3:
        early = np.mean(positive_scores[:len(positive_scores)//3])
        late = np.mean(positive_scores[-len(positive_scores)//3:])
        sentiment_trend = late - early  # Positive = improving, negative = declining
    else:
        sentiment_trend = 0.0

    return {
        'segments': segment_results,
        'num_segments': len(segments),
        'overall_sentiment': {
            'positive_score': float(overall_positive),
            'negative_score': float(overall_negative),
            'sentiment_category': _categorize_sentiment(overall_positive)
        },
        'sentiment_trend': float(sentiment_trend),
        'sentiment_stability': float(np.std(positive_scores)) if positive_scores else 0.0,
        'method': 'bert-segments'
    }


def analyze_interview_sentiment(interview_data: Dict[str, Any],
                                model_name: str = 'distilbert-base-uncased-finetuned-sst-2-english') -> Dict[str, Any]:
    """
    Comprehensive BERT-based sentiment analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field
        model_name: BERT model to use

    Returns:
        Dictionary with multi-level sentiment analysis
    """
    transcript = interview_data.get('transcript', [])

    # Overall interview sentiment
    full_text = ' '.join([turn.get('text', '') for turn in transcript])
    overall_sentiment = analyze_sentiment_bert(full_text, model_name)

    # Per-speaker sentiment
    persona_texts = []
    interviewer_texts = []

    for turn in transcript:
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown').lower()

        if 'persona' in speaker or 'participant' in speaker or 'patient' in speaker:
            persona_texts.append(text)
        elif 'interviewer' in speaker or 'doctor' in speaker or 'clinician' in speaker:
            interviewer_texts.append(text)

    persona_sentiment = None
    if persona_texts:
        persona_full = ' '.join(persona_texts)
        persona_sentiment = analyze_sentiment_bert(persona_full, model_name)

    interviewer_sentiment = None
    if interviewer_texts:
        interviewer_full = ' '.join(interviewer_texts)
        interviewer_sentiment = analyze_sentiment_bert(interviewer_full, model_name)

    # Segment analysis (sentiment trajectory)
    segment_analysis = analyze_sentiment_segments(full_text, segment_size=100, model_name=model_name)

    # Per-turn analysis (for detailed tracking)
    turn_sentiments = []
    for turn in transcript:
        text = turn.get('text', '')
        if text.strip():
            turn_sentiment = analyze_sentiment_bert(text, model_name)
            turn_sentiment['speaker'] = turn.get('speaker', 'unknown')
            turn_sentiments.append(turn_sentiment)

    return {
        'overall_sentiment': overall_sentiment,
        'persona_sentiment': persona_sentiment,
        'interviewer_sentiment': interviewer_sentiment,
        'segment_analysis': segment_analysis,
        'turn_sentiments': turn_sentiments,
        'sentiment_metrics': {
            'overall_positivity': overall_sentiment.get('positive_score', 0.5),
            'persona_positivity': persona_sentiment.get('positive_score', 0.5) if persona_sentiment else None,
            'sentiment_trend': segment_analysis.get('sentiment_trend', 0.0),
            'sentiment_stability': segment_analysis.get('sentiment_stability', 0.0)
        }
    }


def compare_bert_vs_vader(text: str) -> Dict[str, Any]:
    """
    Compare BERT sentiment with VADER sentiment for analysis.

    Useful for understanding differences between methods.
    """
    # BERT sentiment
    bert_result = analyze_sentiment_bert(text)

    # VADER sentiment (if available)
    try:
        from nltk.sentiment import SentimentIntensityAnalyzer
        vader = SentimentIntensityAnalyzer()
        vader_scores = vader.polarity_scores(text)

        return {
            'bert': {
                'positive': bert_result.get('positive_score', 0.0),
                'negative': bert_result.get('negative_score', 0.0),
                'category': bert_result.get('sentiment_category', 'unknown')
            },
            'vader': {
                'positive': vader_scores['pos'],
                'negative': vader_scores['neg'],
                'neutral': vader_scores['neu'],
                'compound': vader_scores['compound']
            },
            'agreement': abs(bert_result.get('positive_score', 0.5) - vader_scores['pos']) < 0.3
        }
    except ImportError:
        return {
            'bert': bert_result,
            'vader': None,
            'error': 'VADER not available'
        }


def _categorize_sentiment(positive_score: float) -> str:
    """Helper to categorize sentiment from positive score."""
    if positive_score >= 0.8:
        return 'very_positive'
    elif positive_score >= 0.6:
        return 'positive'
    elif positive_score >= 0.4:
        return 'neutral'
    elif positive_score >= 0.2:
        return 'negative'
    else:
        return 'very_negative'


def get_sentiment_summary(all_interviews_analysis: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate sentiment summary statistics across all interviews.

    Args:
        all_interviews_analysis: List of BERT sentiment analysis results

    Returns:
        Summary statistics dictionary
    """
    if not all_interviews_analysis:
        return {}

    # Aggregate metrics
    overall_positivities = []
    persona_positivities = []
    sentiment_trends = []
    sentiment_categories = []

    for analysis in all_interviews_analysis:
        metrics = analysis.get('sentiment_metrics', {})

        if metrics.get('overall_positivity') is not None:
            overall_positivities.append(metrics['overall_positivity'])

        if metrics.get('persona_positivity') is not None:
            persona_positivities.append(metrics['persona_positivity'])

        if metrics.get('sentiment_trend') is not None:
            sentiment_trends.append(metrics['sentiment_trend'])

        overall = analysis.get('overall_sentiment', {})
        if overall.get('sentiment_category'):
            sentiment_categories.append(overall['sentiment_category'])

    return {
        'total_interviews': len(all_interviews_analysis),
        'average_positivity': float(np.mean(overall_positivities)) if overall_positivities else 0.5,
        'average_persona_positivity': float(np.mean(persona_positivities)) if persona_positivities else None,
        'average_sentiment_trend': float(np.mean(sentiment_trends)) if sentiment_trends else 0.0,
        'sentiment_distribution': dict(zip(*np.unique(sentiment_categories, return_counts=True))),
        'positivity_range': {
            'min': float(np.min(overall_positivities)) if overall_positivities else 0.0,
            'max': float(np.max(overall_positivities)) if overall_positivities else 0.0,
            'std': float(np.std(overall_positivities)) if overall_positivities else 0.0
        },
        'improving_sentiment_interviews': sum(1 for t in sentiment_trends if t > 0.1),
        'declining_sentiment_interviews': sum(1 for t in sentiment_trends if t < -0.1)
    }


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'transformers': TRANSFORMERS_AVAILABLE,
        'cuda_available': torch.cuda.is_available() if TRANSFORMERS_AVAILABLE else False,
        'has_bert_sentiment': TRANSFORMERS_AVAILABLE
    }


if __name__ == '__main__':
    # Test the module
    test_texts = [
        "I'm so excited about the baby! Everything has been going wonderfully. I feel blessed and happy.",
        "I'm really worried about the complications. The doctor said there might be risks and I'm scared.",
        "The appointment went okay. Nothing special to report. Everything seems normal I guess.",
        "I started feeling better after the first trimester ended. Now I'm looking forward to meeting the baby!"
    ]

    print("BERT Sentiment Analysis Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Transformers available: {status['transformers']}")
    print(f"CUDA available: {status['cuda_available']}")
    print(f"BERT sentiment available: {status['has_bert_sentiment']}")
    print()

    if status['has_bert_sentiment']:
        print("Analyzing test texts...")
        print()

        for i, text in enumerate(test_texts, 1):
            print(f"Text {i}: {text[:60]}...")
            result = analyze_sentiment_bert(text)

            print(f"  Label: {result.get('label', 'N/A')}")
            print(f"  Confidence: {result.get('score', 0.0):.3f}")
            print(f"  Positive: {result.get('positive_score', 0.0):.3f}")
            print(f"  Negative: {result.get('negative_score', 0.0):.3f}")
            print(f"  Category: {result.get('sentiment_category', 'N/A')}")
            print()

        # Test segment analysis
        long_text = ' '.join(test_texts)
        print("Testing segment analysis on combined text...")
        segment_result = analyze_sentiment_segments(long_text, segment_size=20)
        print(f"  Number of segments: {segment_result.get('num_segments', 0)}")
        print(f"  Overall positivity: {segment_result.get('overall_sentiment', {}).get('positive_score', 0.0):.3f}")
        print(f"  Sentiment trend: {segment_result.get('sentiment_trend', 0.0):.3f}")
        print(f"  Sentiment stability: {segment_result.get('sentiment_stability', 0.0):.3f}")

    else:
        print("BERT sentiment analysis not available.")
        print("Install with: pip install transformers torch")
