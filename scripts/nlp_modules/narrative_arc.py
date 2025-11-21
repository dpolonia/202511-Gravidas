"""
Narrative Arc Analysis Module
===============================

Analyzes the emotional journey and story progression through pregnancy interviews.
Identifies turning points, tracks sentiment trajectories, and categorizes narrative
arc patterns (e.g., progressive, regressive, stable, U-shaped, inverted-U).

Capability #10 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np
from collections import defaultdict

logger = logging.getLogger(__name__)

# Try to import signal processing for change point detection
try:
    from scipy import signal
    from scipy.ndimage import gaussian_filter1d
    SCIPY_AVAILABLE = True
    logger.info("✓ SciPy available for advanced narrative analysis")
except ImportError:
    SCIPY_AVAILABLE = False
    logger.warning("SciPy not available. Using simplified change point detection.")

# Try to import ruptures for sophisticated change point detection
try:
    import ruptures as rpt
    RUPTURES_AVAILABLE = True
    logger.info("✓ Ruptures available for change point detection")
except ImportError:
    RUPTURES_AVAILABLE = False
    logger.warning("Ruptures not available. Install with: pip install ruptures")

# Classic narrative arc patterns (from storytelling theory)
NARRATIVE_ARC_TYPES = {
    'progressive': 'Steadily improving emotional state (rags to riches)',
    'regressive': 'Steadily declining emotional state (tragedy)',
    'stable': 'Relatively constant emotional state throughout',
    'u_shaped': 'Initial decline followed by recovery (man in hole)',
    'inverted_u': 'Initial improvement followed by decline (Icarus)',
    'complex': 'Multiple ups and downs, no clear pattern',
    'emotional_roller_coaster': 'Extreme fluctuations throughout'
}


def analyze_sentiment_trajectory(interview_data: Dict[str, Any],
                                 sentiment_source: str = 'auto') -> Dict[str, Any]:
    """
    Analyze sentiment trajectory throughout an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field
        sentiment_source: 'auto', 'vader', 'bert', or pre-computed sentiment data

    Returns:
        Dictionary with sentiment trajectory analysis
    """
    transcript = interview_data.get('transcript', [])

    if not isinstance(transcript, list) or len(transcript) == 0:
        return {'error': 'Invalid or empty transcript'}

    # Extract sentiment for each turn
    sentiments = []
    positions = []
    speakers = []

    for i, turn in enumerate(transcript):
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown')

        # Get or compute sentiment
        if sentiment_source == 'auto':
            # Try to use existing sentiment data
            if 'sentiment' in turn:
                sentiment_score = turn['sentiment'].get('compound', 0.0)
            else:
                # Compute simple sentiment
                sentiment_score = _compute_simple_sentiment(text)
        else:
            sentiment_score = _compute_simple_sentiment(text)

        sentiments.append(sentiment_score)
        positions.append(i / len(transcript))  # Normalized position (0-1)
        speakers.append(speaker)

    # Smooth the sentiment trajectory
    if len(sentiments) >= 5:
        smoothed = _smooth_trajectory(sentiments)
    else:
        smoothed = sentiments

    # Calculate trajectory metrics
    trajectory_metrics = {
        'sentiment_values': sentiments,
        'smoothed_trajectory': smoothed,
        'positions': positions,
        'num_turns': len(sentiments),
        'overall_trend': _calculate_overall_trend(sentiments),
        'volatility': float(np.std(sentiments)) if sentiments else 0.0,
        'range': float(max(sentiments) - min(sentiments)) if sentiments else 0.0,
        'mean_sentiment': float(np.mean(sentiments)) if sentiments else 0.0,
        'final_sentiment': float(sentiments[-1]) if sentiments else 0.0,
        'initial_sentiment': float(sentiments[0]) if sentiments else 0.0,
        'sentiment_change': float(sentiments[-1] - sentiments[0]) if sentiments else 0.0
    }

    return trajectory_metrics


def detect_turning_points(trajectory: List[float],
                          positions: Optional[List[float]] = None,
                          method: str = 'peaks') -> Dict[str, Any]:
    """
    Detect significant turning points in emotional trajectory.

    Args:
        trajectory: List of sentiment/emotion values
        positions: Optional list of normalized positions (0-1)
        method: 'peaks', 'changepoint', or 'derivative'

    Returns:
        Dictionary with turning points:
        {
            'turning_points': [
                {'position': 0.25, 'index': 5, 'type': 'peak', 'value': 0.8},
                {'position': 0.60, 'index': 12, 'type': 'trough', 'value': -0.4}
            ],
            'num_turning_points': 2,
            'major_shifts': [...],
            'method': 'peaks'
        }
    """
    if not trajectory or len(trajectory) < 3:
        return {'error': 'Trajectory too short for turning point detection'}

    if positions is None:
        positions = np.linspace(0, 1, len(trajectory))

    trajectory_array = np.array(trajectory)
    turning_points = []

    if method == 'peaks':
        # Find local maxima and minima
        if SCIPY_AVAILABLE:
            # Find peaks (local maxima)
            peaks, peak_properties = signal.find_peaks(trajectory_array, prominence=0.1)
            # Find troughs (local minima)
            troughs, trough_properties = signal.find_peaks(-trajectory_array, prominence=0.1)

            for peak_idx in peaks:
                turning_points.append({
                    'position': float(positions[peak_idx]),
                    'index': int(peak_idx),
                    'type': 'peak',
                    'value': float(trajectory_array[peak_idx]),
                    'prominence': float(peak_properties['prominences'][list(peaks).index(peak_idx)])
                })

            for trough_idx in troughs:
                turning_points.append({
                    'position': float(positions[trough_idx]),
                    'index': int(trough_idx),
                    'type': 'trough',
                    'value': float(trajectory_array[trough_idx]),
                    'prominence': float(trough_properties['prominences'][list(troughs).index(trough_idx)])
                })
        else:
            # Simple peak detection without scipy
            for i in range(1, len(trajectory_array) - 1):
                if trajectory_array[i] > trajectory_array[i-1] and trajectory_array[i] > trajectory_array[i+1]:
                    # Local maximum
                    prominence = min(trajectory_array[i] - trajectory_array[i-1],
                                   trajectory_array[i] - trajectory_array[i+1])
                    if prominence > 0.1:
                        turning_points.append({
                            'position': float(positions[i]),
                            'index': int(i),
                            'type': 'peak',
                            'value': float(trajectory_array[i]),
                            'prominence': float(prominence)
                        })
                elif trajectory_array[i] < trajectory_array[i-1] and trajectory_array[i] < trajectory_array[i+1]:
                    # Local minimum
                    prominence = min(trajectory_array[i-1] - trajectory_array[i],
                                   trajectory_array[i+1] - trajectory_array[i])
                    if prominence > 0.1:
                        turning_points.append({
                            'position': float(positions[i]),
                            'index': int(i),
                            'type': 'trough',
                            'value': float(trajectory_array[i]),
                            'prominence': float(prominence)
                        })

    elif method == 'changepoint' and RUPTURES_AVAILABLE:
        # Use ruptures library for change point detection
        try:
            algo = rpt.Pelt(model="rbf").fit(trajectory_array.reshape(-1, 1))
            change_points = algo.predict(pen=1.0)

            for cp_idx in change_points[:-1]:  # Exclude last point (end of series)
                if cp_idx < len(trajectory):
                    turning_points.append({
                        'position': float(positions[cp_idx]),
                        'index': int(cp_idx),
                        'type': 'change_point',
                        'value': float(trajectory_array[cp_idx]),
                        'prominence': None
                    })
        except Exception as e:
            logger.warning(f"Change point detection failed: {e}")
            return detect_turning_points(trajectory, positions, method='peaks')

    elif method == 'derivative':
        # Detect points where derivative changes sign significantly
        derivative = np.diff(trajectory_array)
        sign_changes = np.where(np.diff(np.sign(derivative)))[0] + 1

        for idx in sign_changes:
            if 0 < idx < len(trajectory):
                turning_points.append({
                    'position': float(positions[idx]),
                    'index': int(idx),
                    'type': 'inflection',
                    'value': float(trajectory_array[idx]),
                    'prominence': abs(float(derivative[idx-1] - derivative[min(idx, len(derivative)-1)]))
                })

    # Sort by position
    turning_points.sort(key=lambda x: x['position'])

    # Identify major shifts (large changes in sentiment)
    major_shifts = []
    threshold = 0.4  # Minimum change to be considered major

    for i in range(len(trajectory_array) - 1):
        change = abs(trajectory_array[i+1] - trajectory_array[i])
        if change >= threshold:
            major_shifts.append({
                'from_position': float(positions[i]),
                'to_position': float(positions[i+1]),
                'from_index': int(i),
                'to_index': int(i+1),
                'magnitude': float(change),
                'direction': 'positive' if trajectory_array[i+1] > trajectory_array[i] else 'negative',
                'from_value': float(trajectory_array[i]),
                'to_value': float(trajectory_array[i+1])
            })

    return {
        'turning_points': turning_points,
        'num_turning_points': len(turning_points),
        'major_shifts': major_shifts,
        'num_major_shifts': len(major_shifts),
        'method': method
    }


def classify_narrative_arc(trajectory: List[float],
                          positions: Optional[List[float]] = None) -> Dict[str, Any]:
    """
    Classify the overall narrative arc pattern.

    Args:
        trajectory: List of sentiment/emotion values
        positions: Optional list of normalized positions

    Returns:
        Dictionary with arc classification
    """
    if not trajectory or len(trajectory) < 3:
        return {'error': 'Trajectory too short for classification'}

    if positions is None:
        positions = np.linspace(0, 1, len(trajectory))

    trajectory_array = np.array(trajectory)

    # Divide into thirds for pattern analysis
    third = len(trajectory) // 3
    if third == 0:
        third = 1

    first_third = trajectory_array[:third]
    middle_third = trajectory_array[third:2*third]
    last_third = trajectory_array[2*third:]

    first_avg = np.mean(first_third) if len(first_third) > 0 else 0
    middle_avg = np.mean(middle_third) if len(middle_third) > 0 else 0
    last_avg = np.mean(last_third) if len(last_third) > 0 else 0

    # Calculate overall trend
    overall_trend = last_avg - first_avg

    # Calculate volatility
    volatility = np.std(trajectory_array)

    # Classify arc type
    arc_type = None
    confidence = 0.0

    if volatility > 0.5:
        # High volatility
        arc_type = 'emotional_roller_coaster'
        confidence = min(volatility / 0.7, 1.0)

    elif abs(overall_trend) < 0.2:
        # Stable
        arc_type = 'stable'
        confidence = 1.0 - abs(overall_trend) / 0.2

    elif overall_trend > 0.3:
        # Progressive (improving)
        arc_type = 'progressive'
        confidence = min(overall_trend / 0.5, 1.0)

    elif overall_trend < -0.3:
        # Regressive (declining)
        arc_type = 'regressive'
        confidence = min(abs(overall_trend) / 0.5, 1.0)

    elif middle_avg < first_avg and middle_avg < last_avg:
        # U-shaped (man in hole)
        arc_type = 'u_shaped'
        dip_magnitude = min(first_avg - middle_avg, last_avg - middle_avg)
        confidence = min(dip_magnitude / 0.4, 1.0)

    elif middle_avg > first_avg and middle_avg > last_avg:
        # Inverted U (Icarus)
        arc_type = 'inverted_u'
        peak_magnitude = min(middle_avg - first_avg, middle_avg - last_avg)
        confidence = min(peak_magnitude / 0.4, 1.0)

    else:
        # Complex pattern
        arc_type = 'complex'
        confidence = 0.6

    return {
        'arc_type': arc_type,
        'arc_description': NARRATIVE_ARC_TYPES.get(arc_type, 'Unknown pattern'),
        'confidence': float(confidence),
        'overall_trend': float(overall_trend),
        'volatility': float(volatility),
        'first_third_avg': float(first_avg),
        'middle_third_avg': float(middle_avg),
        'last_third_avg': float(last_avg),
        'trajectory_shape': _describe_trajectory_shape(first_avg, middle_avg, last_avg)
    }


def analyze_emotional_peaks(trajectory: List[float],
                           transcript: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Identify and analyze emotional peaks and troughs in the narrative.

    Args:
        trajectory: Sentiment/emotion trajectory
        transcript: Optional transcript for context extraction

    Returns:
        Dictionary with peak/trough analysis
    """
    if len(trajectory) < 3:
        return {'error': 'Trajectory too short'}

    trajectory_array = np.array(trajectory)

    # Find highest and lowest points
    peak_idx = int(np.argmax(trajectory_array))
    trough_idx = int(np.argmin(trajectory_array))

    peak_value = float(trajectory_array[peak_idx])
    trough_value = float(trajectory_array[trough_idx])

    peak_context = None
    trough_context = None

    if transcript and len(transcript) > peak_idx:
        peak_context = transcript[peak_idx].get('text', '')[:200]

    if transcript and len(transcript) > trough_idx:
        trough_context = transcript[trough_idx].get('text', '')[:200]

    # Calculate emotional range
    emotional_range = peak_value - trough_value

    # Detect all significant peaks and troughs
    turning_points = detect_turning_points(trajectory, method='peaks')

    peaks = [tp for tp in turning_points.get('turning_points', []) if tp['type'] == 'peak']
    troughs = [tp for tp in turning_points.get('turning_points', []) if tp['type'] == 'trough']

    return {
        'highest_point': {
            'index': peak_idx,
            'position': peak_idx / len(trajectory),
            'value': peak_value,
            'context': peak_context
        },
        'lowest_point': {
            'index': trough_idx,
            'position': trough_idx / len(trajectory),
            'value': trough_value,
            'context': trough_context
        },
        'emotional_range': float(emotional_range),
        'num_peaks': len(peaks),
        'num_troughs': len(troughs),
        'all_peaks': peaks[:5],  # Top 5 peaks
        'all_troughs': troughs[:5]  # Top 5 troughs
    }


def analyze_narrative_progression(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive narrative arc analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Complete narrative arc analysis
    """
    # Extract sentiment trajectory
    trajectory_analysis = analyze_sentiment_trajectory(interview_data)

    if 'error' in trajectory_analysis:
        return trajectory_analysis

    trajectory = trajectory_analysis['sentiment_values']
    positions = trajectory_analysis['positions']

    # Classify narrative arc
    arc_classification = classify_narrative_arc(trajectory, positions)

    # Detect turning points
    turning_points = detect_turning_points(trajectory, positions, method='peaks')

    # Analyze emotional peaks
    transcript = interview_data.get('transcript', [])
    peaks_analysis = analyze_emotional_peaks(trajectory, transcript)

    # Extract key moments (highest positive/negative sentiment turns)
    key_moments = _extract_key_moments(trajectory, transcript)

    # Analyze narrative stages (beginning, middle, end)
    stages = _analyze_narrative_stages(trajectory, transcript)

    # Calculate narrative coherence
    coherence = _calculate_narrative_coherence(trajectory)

    return {
        'trajectory': trajectory_analysis,
        'arc_classification': arc_classification,
        'turning_points': turning_points,
        'emotional_peaks': peaks_analysis,
        'key_moments': key_moments,
        'narrative_stages': stages,
        'coherence': coherence,
        'summary': _generate_narrative_summary(
            arc_classification,
            trajectory_analysis,
            turning_points,
            peaks_analysis
        )
    }


def compare_narrative_arcs(interviews: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Compare narrative arcs across multiple interviews.

    Args:
        interviews: List of interview dictionaries

    Returns:
        Comparative analysis of narrative patterns
    """
    if not interviews:
        return {'error': 'No interviews provided'}

    arc_types = defaultdict(int)
    trajectories = []
    overall_trends = []

    for interview in interviews:
        analysis = analyze_narrative_progression(interview)

        if 'error' not in analysis:
            arc_type = analysis['arc_classification']['arc_type']
            arc_types[arc_type] += 1

            trajectories.append(analysis['trajectory']['sentiment_values'])
            overall_trends.append(analysis['trajectory']['overall_trend'])

    # Find most common arc type
    most_common_arc = max(arc_types.items(), key=lambda x: x[1]) if arc_types else ('unknown', 0)

    # Calculate average trajectory
    if trajectories:
        # Normalize all to same length for averaging
        normalized_trajectories = [_normalize_trajectory_length(t, 20) for t in trajectories]
        avg_trajectory = np.mean(normalized_trajectories, axis=0).tolist()
    else:
        avg_trajectory = []

    return {
        'num_interviews': len(interviews),
        'arc_type_distribution': dict(arc_types),
        'most_common_arc': most_common_arc[0],
        'most_common_arc_count': most_common_arc[1],
        'average_trajectory': avg_trajectory,
        'average_overall_trend': float(np.mean(overall_trends)) if overall_trends else 0.0,
        'trend_variance': float(np.var(overall_trends)) if overall_trends else 0.0
    }


# Helper functions

def _compute_simple_sentiment(text: str) -> float:
    """
    Compute simple sentiment score using basic positive/negative word lists.
    Returns score in range [-1, 1].
    """
    if not text:
        return 0.0

    text_lower = text.lower()

    # Basic positive words
    positive_words = ['good', 'great', 'happy', 'wonderful', 'excellent', 'amazing',
                     'love', 'excited', 'blessed', 'grateful', 'beautiful', 'joy',
                     'better', 'improved', 'comfortable', 'positive', 'hopeful']

    # Basic negative words
    negative_words = ['bad', 'terrible', 'awful', 'horrible', 'sad', 'worried',
                     'anxious', 'scared', 'afraid', 'difficult', 'hard', 'pain',
                     'worse', 'problem', 'concern', 'negative', 'stress']

    positive_count = sum(1 for word in positive_words if word in text_lower)
    negative_count = sum(1 for word in negative_words if word in text_lower)

    total = positive_count + negative_count
    if total == 0:
        return 0.0

    sentiment = (positive_count - negative_count) / max(total, 1)
    return float(np.clip(sentiment, -1, 1))


def _smooth_trajectory(trajectory: List[float], window_size: int = 3) -> List[float]:
    """Smooth trajectory using moving average or gaussian filter."""
    if len(trajectory) < window_size:
        return trajectory

    if SCIPY_AVAILABLE:
        # Use gaussian smoothing
        sigma = window_size / 3.0
        smoothed = gaussian_filter1d(trajectory, sigma=sigma)
        return smoothed.tolist()
    else:
        # Simple moving average
        smoothed = []
        for i in range(len(trajectory)):
            start = max(0, i - window_size // 2)
            end = min(len(trajectory), i + window_size // 2 + 1)
            smoothed.append(np.mean(trajectory[start:end]))
        return smoothed


def _calculate_overall_trend(trajectory: List[float]) -> float:
    """Calculate overall trend using linear regression."""
    if len(trajectory) < 2:
        return 0.0

    x = np.arange(len(trajectory))
    y = np.array(trajectory)

    # Linear regression
    slope = np.polyfit(x, y, 1)[0]

    return float(slope)


def _describe_trajectory_shape(first: float, middle: float, last: float) -> str:
    """Generate human-readable description of trajectory shape."""
    if middle < first and middle < last:
        return "Dip in middle with recovery"
    elif middle > first and middle > last:
        return "Peak in middle with decline"
    elif last > first and last > middle:
        return "Steady improvement throughout"
    elif last < first and last < middle:
        return "Steady decline throughout"
    elif abs(last - first) < 0.2:
        return "Relatively stable throughout"
    else:
        return "Complex pattern with variations"


def _extract_key_moments(trajectory: List[float],
                        transcript: List[Dict[str, Any]],
                        top_k: int = 3) -> Dict[str, List[Dict[str, Any]]]:
    """Extract the most emotionally significant moments."""
    if not transcript or len(transcript) != len(trajectory):
        return {'most_positive': [], 'most_negative': []}

    # Combine trajectory with transcript
    combined = [(trajectory[i], i, transcript[i]) for i in range(len(trajectory))]

    # Sort by sentiment
    sorted_positive = sorted(combined, key=lambda x: x[0], reverse=True)
    sorted_negative = sorted(combined, key=lambda x: x[0])

    most_positive = [
        {
            'index': idx,
            'position': idx / len(trajectory),
            'sentiment': float(sent),
            'text': turn.get('text', '')[:200],
            'speaker': turn.get('speaker', 'unknown')
        }
        for sent, idx, turn in sorted_positive[:top_k]
    ]

    most_negative = [
        {
            'index': idx,
            'position': idx / len(trajectory),
            'sentiment': float(sent),
            'text': turn.get('text', '')[:200],
            'speaker': turn.get('speaker', 'unknown')
        }
        for sent, idx, turn in sorted_negative[:top_k]
    ]

    return {
        'most_positive': most_positive,
        'most_negative': most_negative
    }


def _analyze_narrative_stages(trajectory: List[float],
                              transcript: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Analyze beginning, middle, and end stages of narrative."""
    if len(trajectory) < 3:
        return {}

    third = len(trajectory) // 3

    beginning = trajectory[:third]
    middle = trajectory[third:2*third]
    end = trajectory[2*third:]

    return {
        'beginning': {
            'avg_sentiment': float(np.mean(beginning)),
            'volatility': float(np.std(beginning)),
            'trend': _calculate_overall_trend(beginning)
        },
        'middle': {
            'avg_sentiment': float(np.mean(middle)),
            'volatility': float(np.std(middle)),
            'trend': _calculate_overall_trend(middle)
        },
        'end': {
            'avg_sentiment': float(np.mean(end)),
            'volatility': float(np.std(end)),
            'trend': _calculate_overall_trend(end)
        }
    }


def _calculate_narrative_coherence(trajectory: List[float]) -> Dict[str, Any]:
    """Calculate how coherent/smooth the narrative is."""
    if len(trajectory) < 2:
        return {'coherence_score': 1.0}

    # Calculate smoothness (lower derivative variance = more coherent)
    derivative = np.diff(trajectory)
    derivative_variance = np.var(derivative)

    # Normalize to 0-1 scale (higher = more coherent)
    coherence_score = 1.0 / (1.0 + derivative_variance)

    return {
        'coherence_score': float(coherence_score),
        'smoothness': float(1.0 - min(derivative_variance, 1.0)),
        'average_change_magnitude': float(np.mean(np.abs(derivative)))
    }


def _generate_narrative_summary(arc_classification: Dict,
                               trajectory: Dict,
                               turning_points: Dict,
                               peaks: Dict) -> str:
    """Generate human-readable summary of narrative arc."""
    arc_type = arc_classification.get('arc_type', 'unknown')
    trend = trajectory.get('overall_trend', 0.0)
    num_turning_points = turning_points.get('num_turning_points', 0)

    trend_word = "improving" if trend > 0.1 else "declining" if trend < -0.1 else "stable"

    summary = f"This interview follows a {arc_type} narrative arc with {trend_word} overall sentiment. "
    summary += f"There are {num_turning_points} significant turning points throughout the conversation. "

    emotional_range = peaks.get('emotional_range', 0)
    if emotional_range > 0.8:
        summary += "The emotional journey shows significant variation from high to low points. "
    elif emotional_range < 0.3:
        summary += "The emotional tone remains relatively consistent throughout. "

    return summary


def _normalize_trajectory_length(trajectory: List[float], target_length: int) -> List[float]:
    """Normalize trajectory to target length using interpolation."""
    if len(trajectory) == target_length:
        return trajectory

    x_old = np.linspace(0, 1, len(trajectory))
    x_new = np.linspace(0, 1, target_length)

    normalized = np.interp(x_new, x_old, trajectory)
    return normalized.tolist()


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'scipy': SCIPY_AVAILABLE,
        'ruptures': RUPTURES_AVAILABLE,
        'has_narrative_arc': True,  # Basic functionality always available
        'advanced_changepoint': RUPTURES_AVAILABLE
    }


if __name__ == '__main__':
    # Test the module
    test_interview = {
        'transcript': [
            {'speaker': 'interviewer', 'text': 'How are you feeling today?'},
            {'speaker': 'persona', 'text': 'I\'m feeling wonderful! Really excited about the pregnancy.'},
            {'speaker': 'interviewer', 'text': 'That\'s great to hear. Any concerns?'},
            {'speaker': 'persona', 'text': 'Well, I am a bit worried about the delivery. It\'s scary to think about.'},
            {'speaker': 'interviewer', 'text': 'That\'s very normal. Tell me more.'},
            {'speaker': 'persona', 'text': 'I guess I just need to stay positive. My partner is very supportive.'},
            {'speaker': 'interviewer', 'text': 'Support is important. How do you feel now?'},
            {'speaker': 'persona', 'text': 'Much better actually. Talking about it helps. I feel hopeful about everything.'}
        ]
    }

    print("Narrative Arc Analysis Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Narrative arc analysis available: {status['has_narrative_arc']}")
    print(f"SciPy available: {status['scipy']}")
    print(f"Ruptures available: {status['ruptures']}")
    print()

    # Analyze narrative
    print("Analyzing test interview narrative...")
    result = analyze_narrative_progression(test_interview)

    print(f"\nARC CLASSIFICATION:")
    arc = result['arc_classification']
    print(f"  Type: {arc['arc_type']}")
    print(f"  Description: {arc['arc_description']}")
    print(f"  Confidence: {arc['confidence']:.2f}")
    print(f"  Overall Trend: {arc['overall_trend']:.3f}")

    print(f"\nTRAJECTORY METRICS:")
    traj = result['trajectory']
    print(f"  Initial Sentiment: {traj['initial_sentiment']:.3f}")
    print(f"  Final Sentiment: {traj['final_sentiment']:.3f}")
    print(f"  Sentiment Change: {traj['sentiment_change']:.3f}")
    print(f"  Volatility: {traj['volatility']:.3f}")

    print(f"\nTURNING POINTS:")
    tp = result['turning_points']
    print(f"  Number of turning points: {tp['num_turning_points']}")
    for point in tp.get('turning_points', [])[:3]:
        print(f"  - {point['type']} at position {point['position']:.2f} (value: {point['value']:.3f})")

    print(f"\nNARRATIVE SUMMARY:")
    print(f"  {result['summary']}")
