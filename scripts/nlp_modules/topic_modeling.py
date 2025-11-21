"""
Topic Modeling Module
======================

Discovers hidden topics automatically from interview transcripts using
BERTopic (transformer-based) or LDA (classical method).

Capability #3 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
from collections import Counter
import re

logger = logging.getLogger(__name__)

# Try to import BERTopic
try:
    from bertopic import BERTopic
    from sklearn.feature_extraction.text import CountVectorizer
    BERTOPIC_AVAILABLE = True
    logger.info("✓ BERTopic available for topic modeling")
except ImportError:
    BERTOPIC_AVAILABLE = False
    logger.warning("BERTopic not available. Install with: pip install bertopic")

# Try to import LDA (alternative)
try:
    from gensim import corpora
    from gensim.models import LdaModel
    from gensim.parsing.preprocessing import STOPWORDS
    import nltk
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    LDA_AVAILABLE = True
    logger.info("✓ Gensim LDA available as backup")
except ImportError:
    LDA_AVAILABLE = False
    logger.warning("Gensim not available. Install with: pip install gensim")


def discover_topics(texts: List[str],
                   num_topics: int = 5,
                   method: str = 'bertopic',
                   min_topic_size: int = 2) -> Dict[str, Any]:
    """
    Discover topics from a collection of texts.

    Args:
        texts: List of interview transcripts or text segments
        num_topics: Number of topics to discover (for LDA)
        method: 'bertopic' or 'lda'
        min_topic_size: Minimum size of topics (for BERTopic)

    Returns:
        Dictionary with topic modeling results:
        {
            'topics': [
                {
                    'topic_id': 0,
                    'label': 'Prenatal Care',
                    'keywords': ['doctor', 'appointment', 'ultrasound', 'checkup'],
                    'size': 15,
                    'representative_docs': [...]
                }
            ],
            'document_topics': [0, 1, 0, 2, ...],  # Topic assignment per document
            'topic_distribution': {0: 0.35, 1: 0.25, 2: 0.20, ...},
            'method': 'bertopic'
        }
    """
    if method == 'bertopic' and BERTOPIC_AVAILABLE:
        return _discover_with_bertopic(texts, min_topic_size)
    elif method == 'lda' and LDA_AVAILABLE:
        return _discover_with_lda(texts, num_topics)
    else:
        # Fallback to rule-based clustering
        return _discover_with_rules(texts)


def _discover_with_bertopic(texts: List[str], min_topic_size: int = 2) -> Dict[str, Any]:
    """Discover topics using BERTopic (transformer-based)."""
    try:
        # Configure BERTopic
        # Use CountVectorizer to remove common pregnancy terms that might dominate
        vectorizer_model = CountVectorizer(
            ngram_range=(1, 2),
            stop_words='english',
            min_df=1
        )

        # Initialize BERTopic
        topic_model = BERTopic(
            min_topic_size=min_topic_size,
            vectorizer_model=vectorizer_model,
            verbose=False,
            calculate_probabilities=False  # Faster
        )

        # Fit model
        topics, probabilities = topic_model.fit_transform(texts)

        # Get topic info
        topic_info = topic_model.get_topic_info()

        # Build topic list
        topic_list = []
        for _, row in topic_info.iterrows():
            topic_id = row['Topic']
            if topic_id == -1:
                continue  # Skip outlier topic

            # Get top words for this topic
            topic_words = topic_model.get_topic(topic_id)
            keywords = [word for word, score in topic_words[:10]]

            # Generate label from top 3 keywords
            label = ' & '.join(keywords[:3]).title()

            # Get representative documents
            representative_docs = []
            try:
                rep_docs = topic_model.get_representative_docs(topic_id)
                representative_docs = [doc[:200] + "..." if len(doc) > 200 else doc
                                      for doc in rep_docs[:3]]
            except:
                pass

            topic_list.append({
                'topic_id': int(topic_id),
                'label': label,
                'keywords': keywords,
                'size': int(row['Count']),
                'representative_docs': representative_docs
            })

        # Calculate topic distribution
        topic_counts = Counter(topics)
        total_docs = len(texts)
        topic_distribution = {
            int(topic_id): count / total_docs
            for topic_id, count in topic_counts.items()
            if topic_id != -1
        }

        return {
            'topics': topic_list,
            'document_topics': [int(t) for t in topics],
            'topic_distribution': topic_distribution,
            'num_topics': len(topic_list),
            'outliers': sum(1 for t in topics if t == -1),
            'method': 'bertopic'
        }

    except Exception as e:
        logger.error(f"Error in BERTopic modeling: {e}")
        return {
            'topics': [],
            'error': str(e),
            'method': 'bertopic'
        }


def _discover_with_lda(texts: List[str], num_topics: int = 5) -> Dict[str, Any]:
    """Discover topics using LDA (Latent Dirichlet Allocation)."""
    try:
        # Preprocess texts
        def preprocess(text):
            # Lowercase and tokenize
            text = text.lower()
            tokens = re.findall(r'\b[a-z]{3,}\b', text)
            # Remove stopwords
            tokens = [t for t in tokens if t not in STOPWORDS]
            return tokens

        processed_texts = [preprocess(text) for text in texts]

        # Create dictionary and corpus
        dictionary = corpora.Dictionary(processed_texts)
        dictionary.filter_extremes(no_below=1, no_above=0.8)
        corpus = [dictionary.doc2bow(text) for text in processed_texts]

        # Train LDA model
        lda_model = LdaModel(
            corpus=corpus,
            id2word=dictionary,
            num_topics=num_topics,
            random_state=42,
            passes=10,
            alpha='auto',
            per_word_topics=True
        )

        # Extract topics
        topic_list = []
        for topic_id in range(num_topics):
            # Get top words
            topic_words = lda_model.show_topic(topic_id, topn=10)
            keywords = [word for word, score in topic_words]

            # Generate label
            label = ' & '.join(keywords[:3]).title()

            # Count documents in this topic
            topic_size = sum(1 for doc_topics in [lda_model.get_document_topics(doc)
                                                   for doc in corpus]
                           if doc_topics and max(doc_topics, key=lambda x: x[1])[0] == topic_id)

            topic_list.append({
                'topic_id': topic_id,
                'label': label,
                'keywords': keywords,
                'size': topic_size,
                'representative_docs': []
            })

        # Get document topic assignments (dominant topic per document)
        document_topics = []
        for doc in corpus:
            doc_topics = lda_model.get_document_topics(doc)
            if doc_topics:
                dominant_topic = max(doc_topics, key=lambda x: x[1])[0]
                document_topics.append(dominant_topic)
            else:
                document_topics.append(-1)

        # Calculate distribution
        topic_counts = Counter(document_topics)
        total_docs = len(texts)
        topic_distribution = {
            topic_id: count / total_docs
            for topic_id, count in topic_counts.items()
            if topic_id != -1
        }

        return {
            'topics': topic_list,
            'document_topics': document_topics,
            'topic_distribution': topic_distribution,
            'num_topics': num_topics,
            'method': 'lda'
        }

    except Exception as e:
        logger.error(f"Error in LDA modeling: {e}")
        return {
            'topics': [],
            'error': str(e),
            'method': 'lda'
        }


def _discover_with_rules(texts: List[str]) -> Dict[str, Any]:
    """
    Fallback rule-based topic clustering using pregnancy-specific themes.

    This works even without external libraries.
    """
    # Predefined pregnancy topics with keywords
    topic_keywords = {
        0: {
            'label': 'Prenatal Care & Appointments',
            'keywords': ['doctor', 'appointment', 'visit', 'checkup', 'prenatal',
                        'obstetrician', 'ob', 'clinic', 'office']
        },
        1: {
            'label': 'Physical Symptoms & Discomfort',
            'keywords': ['nausea', 'pain', 'tired', 'fatigue', 'swelling', 'sick',
                        'headache', 'backache', 'uncomfortable', 'cramping']
        },
        2: {
            'label': 'Emotional Wellbeing & Mental Health',
            'keywords': ['worried', 'anxious', 'stress', 'scared', 'happy', 'excited',
                        'emotional', 'mood', 'feeling', 'overwhelmed']
        },
        3: {
            'label': 'Tests & Medical Procedures',
            'keywords': ['ultrasound', 'test', 'blood', 'urine', 'scan', 'screening',
                        'genetic', 'amniocentesis', 'glucose', 'lab']
        },
        4: {
            'label': 'Support & Relationships',
            'keywords': ['partner', 'husband', 'family', 'support', 'mother', 'friend',
                        'help', 'alone', 'spouse', 'father']
        },
        5: {
            'label': 'Delivery & Birth Planning',
            'keywords': ['delivery', 'birth', 'labor', 'hospital', 'cesarean', 'c-section',
                        'natural', 'epidural', 'contractions', 'due date']
        },
        6: {
            'label': 'Complications & High-Risk',
            'keywords': ['complication', 'risk', 'concern', 'problem', 'preeclampsia',
                        'diabetes', 'high blood pressure', 'gestational', 'dangerous']
        }
    }

    # Score each document for each topic
    document_topics = []
    topic_sizes = {i: 0 for i in range(7)}

    for text in texts:
        text_lower = text.lower()
        topic_scores = {}

        for topic_id, topic_info in topic_keywords.items():
            score = sum(1 for keyword in topic_info['keywords'] if keyword in text_lower)
            topic_scores[topic_id] = score

        # Assign to dominant topic
        if topic_scores and max(topic_scores.values()) > 0:
            dominant_topic = max(topic_scores.items(), key=lambda x: x[1])[0]
            document_topics.append(dominant_topic)
            topic_sizes[dominant_topic] += 1
        else:
            document_topics.append(-1)  # No topic match

    # Build topic list
    topic_list = []
    for topic_id, topic_info in topic_keywords.items():
        if topic_sizes[topic_id] > 0:
            topic_list.append({
                'topic_id': topic_id,
                'label': topic_info['label'],
                'keywords': topic_info['keywords'][:10],
                'size': topic_sizes[topic_id],
                'representative_docs': []
            })

    # Calculate distribution
    total_docs = len(texts)
    topic_distribution = {
        topic_id: size / total_docs
        for topic_id, size in topic_sizes.items()
        if size > 0
    }

    return {
        'topics': topic_list,
        'document_topics': document_topics,
        'topic_distribution': topic_distribution,
        'num_topics': len(topic_list),
        'method': 'rule-based'
    }


def analyze_interview_topics(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Topic analysis for a single interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Dictionary with topic analysis
    """
    # Extract speaker turns
    transcript = interview_data.get('transcript', [])

    # Split into persona and interviewer turns
    persona_turns = []
    interviewer_turns = []

    for turn in transcript:
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown').lower()

        if 'persona' in speaker or 'participant' in speaker or 'patient' in speaker:
            persona_turns.append(text)
        elif 'interviewer' in speaker or 'doctor' in speaker or 'clinician' in speaker:
            interviewer_turns.append(text)

    # Analyze topics in persona responses
    if len(persona_turns) >= 2:
        persona_topics = discover_topics(persona_turns, num_topics=3, min_topic_size=1)
    else:
        persona_topics = None

    # Analyze full interview
    all_turns = [turn.get('text', '') for turn in transcript if turn.get('text')]
    if len(all_turns) >= 2:
        overall_topics = discover_topics(all_turns, num_topics=5, min_topic_size=1)
    else:
        overall_topics = None

    return {
        'persona_topics': persona_topics,
        'overall_topics': overall_topics,
        'num_turns': len(transcript),
        'num_persona_turns': len(persona_turns),
        'num_interviewer_turns': len(interviewer_turns)
    }


def analyze_corpus_topics(interviews: List[Dict[str, Any]],
                         num_topics: int = 10,
                         method: str = 'bertopic') -> Dict[str, Any]:
    """
    Discover topics across entire interview corpus.

    Args:
        interviews: List of interview dictionaries
        num_topics: Number of topics to discover
        method: 'bertopic', 'lda', or 'rules'

    Returns:
        Corpus-level topic analysis
    """
    # Extract all interview texts
    texts = []
    interview_ids = []

    for idx, interview in enumerate(interviews):
        transcript = interview.get('transcript', [])
        full_text = ' '.join([turn.get('text', '') for turn in transcript])
        if full_text.strip():
            texts.append(full_text)
            interview_ids.append(idx)

    if not texts:
        return {
            'error': 'No text content found in interviews',
            'topics': [],
            'method': method
        }

    # Discover topics
    topic_results = discover_topics(texts, num_topics=num_topics, method=method)

    # Add interview IDs
    topic_results['interview_ids'] = interview_ids
    topic_results['total_interviews'] = len(texts)

    return topic_results


def get_topic_evolution(interviews: List[Dict[str, Any]],
                       time_field: str = 'timestamp') -> Dict[str, Any]:
    """
    Analyze how topics evolve over time (if interviews have timestamps).

    Args:
        interviews: List of interview dictionaries with time information
        time_field: Field name containing timestamp

    Returns:
        Topic evolution analysis
    """
    # Sort interviews by time
    sorted_interviews = sorted(interviews,
                              key=lambda x: x.get(time_field, ''),
                              reverse=False)

    # Split into time periods
    n = len(sorted_interviews)
    if n < 3:
        return {'error': 'Not enough interviews for temporal analysis'}

    third = n // 3
    periods = {
        'early': sorted_interviews[:third],
        'middle': sorted_interviews[third:2*third],
        'late': sorted_interviews[2*third:]
    }

    # Analyze topics in each period
    period_topics = {}
    for period_name, period_interviews in periods.items():
        period_topics[period_name] = analyze_corpus_topics(
            period_interviews,
            num_topics=5,
            method='rules'  # Use rules for consistency
        )

    return {
        'periods': period_topics,
        'total_interviews': n,
        'period_sizes': {k: len(v) for k, v in periods.items()}
    }


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'bertopic': BERTOPIC_AVAILABLE,
        'lda': LDA_AVAILABLE,
        'has_topic_modeling': BERTOPIC_AVAILABLE or LDA_AVAILABLE
    }


if __name__ == '__main__':
    # Test the module
    test_texts = [
        "I had my prenatal appointment today. The doctor did an ultrasound and said everything looks good. My next checkup is in two weeks.",
        "I've been feeling so nauseous lately. The morning sickness is terrible. I'm also really tired all the time and my back hurts.",
        "I'm worried about the delivery. My partner is being supportive but I'm still anxious about labor and whether I'll need a c-section.",
        "They did genetic testing and screening. The blood test came back normal. I have to do a glucose test next month.",
        "My family has been amazing. My mother comes over to help and my husband is so supportive. I don't know what I'd do without them.",
        "The doctor is concerned about my blood pressure. They mentioned preeclampsia risk. I have to monitor it at home now."
    ]

    print("Topic Modeling Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"BERTopic available: {status['bertopic']}")
    print(f"LDA available: {status['lda']}")
    print(f"Topic modeling available: {status['has_topic_modeling']}")
    print()

    # Discover topics
    print("Discovering topics...")
    result = discover_topics(test_texts, num_topics=5)

    print(f"\nMethod used: {result.get('method', 'unknown')}")
    print(f"Number of topics: {result.get('num_topics', 0)}")
    print(f"Total documents: {len(test_texts)}")

    if result.get('topics'):
        print(f"\nDiscovered Topics:")
        for topic in result['topics']:
            print(f"\n  Topic {topic['topic_id']}: {topic['label']}")
            print(f"  Size: {topic['size']} documents")
            print(f"  Keywords: {', '.join(topic['keywords'][:5])}")

    if result.get('topic_distribution'):
        print(f"\nTopic Distribution:")
        for topic_id, proportion in sorted(result['topic_distribution'].items()):
            print(f"  Topic {topic_id}: {proportion:.1%}")
