"""
NLP Modules Package
===================

Advanced NLP analysis modules for interview data.

Modules:
1. medical_ner - Medical Entity Recognition (scispaCy)
2. emotion_analysis - Multi-Emotion Detection (NRCLex)
3. topic_modeling - Topic Discovery (BERTopic)
4. bert_sentiment - Transformer-based Sentiment (BERT)
5. qa_patterns - Question-Answer Pattern Analysis
6. readability - Linguistic Complexity Metrics
7. mental_health - Mental Health Screening
8. semantic_similarity - Semantic Similarity (SBERT)
9. empathy_detection - Empathy Detection
10. narrative_arc - Narrative Arc Analysis
11. risk_extraction - Risk Factor Extraction
"""

__version__ = '1.0.0'

# Module imports (with fallbacks for unavailable modules)
try:
    from .medical_ner import (
        extract_medical_entities,
        extract_pregnancy_specific_terms,
        analyze_medical_content
    )
except ImportError:
    extract_medical_entities = None
    extract_pregnancy_specific_terms = None
    analyze_medical_content = None

try:
    from .emotion_analysis import (
        analyze_emotions,
        analyze_interview_emotions,
        calculate_emotional_complexity
    )
except ImportError:
    analyze_emotions = None
    analyze_interview_emotions = None
    calculate_emotional_complexity = None

try:
    from .topic_modeling import (
        discover_topics,
        analyze_interview_topics,
        analyze_corpus_topics
    )
except ImportError:
    discover_topics = None
    analyze_interview_topics = None
    analyze_corpus_topics = None

try:
    from .bert_sentiment import (
        analyze_sentiment_bert,
        analyze_interview_sentiment,
        analyze_sentiment_segments
    )
except ImportError:
    analyze_sentiment_bert = None
    analyze_interview_sentiment = None
    analyze_sentiment_segments = None

try:
    from .qa_patterns import (
        classify_question,
        analyze_response_pattern,
        analyze_interview_qa_patterns
    )
except ImportError:
    classify_question = None
    analyze_response_pattern = None
    analyze_interview_qa_patterns = None

try:
    from .semantic_similarity import (
        compute_similarity,
        compute_similarity_matrix,
        find_similar_interviews,
        cluster_interviews,
        analyze_interview_similarity
    )
except ImportError:
    compute_similarity = None
    compute_similarity_matrix = None
    find_similar_interviews = None
    cluster_interviews = None
    analyze_interview_similarity = None

try:
    from .mental_health import (
        screen_depression_phq9,
        screen_anxiety_gad7,
        screen_mental_health,
        track_longitudinal_mental_health
    )
except ImportError:
    screen_depression_phq9 = None
    screen_anxiety_gad7 = None
    screen_mental_health = None
    track_longitudinal_mental_health = None

try:
    from .narrative_arc import (
        analyze_narrative_progression,
        analyze_sentiment_trajectory,
        detect_turning_points,
        classify_narrative_arc,
        compare_narrative_arcs
    )
except ImportError:
    analyze_narrative_progression = None
    analyze_sentiment_trajectory = None
    detect_turning_points = None
    classify_narrative_arc = None
    compare_narrative_arcs = None

try:
    from .empathy_detection import (
        detect_empathy_in_turn,
        analyze_interview_empathy,
        compare_interviewer_empathy,
        measure_empathy_gap
    )
except ImportError:
    detect_empathy_in_turn = None
    analyze_interview_empathy = None
    compare_interviewer_empathy = None
    measure_empathy_gap = None

try:
    from .risk_extraction import (
        extract_risk_factors,
        analyze_clinical_risk,
        track_risk_trajectory,
        compare_risk_profiles
    )
except ImportError:
    extract_risk_factors = None
    analyze_clinical_risk = None
    track_risk_trajectory = None
    compare_risk_profiles = None

__all__ = [
    'extract_medical_entities',
    'extract_pregnancy_specific_terms',
    'analyze_medical_content',
    'analyze_emotions',
    'analyze_interview_emotions',
    'calculate_emotional_complexity',
    'discover_topics',
    'analyze_interview_topics',
    'analyze_corpus_topics',
    'analyze_sentiment_bert',
    'analyze_interview_sentiment',
    'analyze_sentiment_segments',
    'classify_question',
    'analyze_response_pattern',
    'analyze_interview_qa_patterns',
    'compute_similarity',
    'compute_similarity_matrix',
    'find_similar_interviews',
    'cluster_interviews',
    'analyze_interview_similarity',
    'screen_depression_phq9',
    'screen_anxiety_gad7',
    'screen_mental_health',
    'track_longitudinal_mental_health',
    'analyze_narrative_progression',
    'analyze_sentiment_trajectory',
    'detect_turning_points',
    'classify_narrative_arc',
    'compare_narrative_arcs',
    'detect_empathy_in_turn',
    'analyze_interview_empathy',
    'compare_interviewer_empathy',
    'measure_empathy_gap',
    'extract_risk_factors',
    'analyze_clinical_risk',
    'track_risk_trajectory',
    'compare_risk_profiles'
]
