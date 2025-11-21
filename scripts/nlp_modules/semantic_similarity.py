"""
Semantic Similarity Module
===========================

Measures semantic similarity between interviews using Sentence-BERT (SBERT).
Enables clustering of similar pregnancy experiences and cross-interview analysis.

Capability #8 of 11 Advanced NLP Enhancements
"""

import logging
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

logger = logging.getLogger(__name__)

# Try to import sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
    import torch
    SBERT_AVAILABLE = True
    logger.info("✓ Sentence-BERT available for semantic similarity")
except ImportError:
    SBERT_AVAILABLE = False
    logger.warning("sentence-transformers not available. Install with: pip install sentence-transformers")

# Try to import sklearn for clustering
try:
    from sklearn.cluster import KMeans, AgglomerativeClustering
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available. Install with: pip install scikit-learn")

# Global model cache
_sbert_model = None
_model_name = None


def load_sbert_model(model_name: str = 'all-MiniLM-L6-v2'):
    """
    Load a Sentence-BERT model for semantic encoding.

    Popular models:
    - 'all-MiniLM-L6-v2' (Recommended - fast, good quality, 384 dims)
    - 'all-mpnet-base-v2' (Highest quality, slower, 768 dims)
    - 'paraphrase-multilingual-MiniLM-L12-v2' (Multilingual)
    - 'multi-qa-MiniLM-L6-cos-v1' (Optimized for Q&A)

    Args:
        model_name: HuggingFace model identifier

    Returns:
        Loaded SentenceTransformer model or None
    """
    global _sbert_model, _model_name

    if not SBERT_AVAILABLE:
        return None

    if _sbert_model is not None and _model_name == model_name:
        return _sbert_model

    try:
        logger.info(f"Loading Sentence-BERT model: {model_name}")
        _sbert_model = SentenceTransformer(model_name)
        _model_name = model_name
        logger.info(f"✓ SBERT model loaded: {model_name}")
        return _sbert_model
    except Exception as e:
        logger.error(f"Error loading SBERT model: {e}")
        return None


def encode_text(text: str, model_name: str = 'all-MiniLM-L6-v2') -> Optional[np.ndarray]:
    """
    Encode text into semantic embedding vector.

    Args:
        text: Input text
        model_name: SBERT model to use

    Returns:
        Numpy array of embeddings or None
    """
    if not SBERT_AVAILABLE:
        return None

    model = load_sbert_model(model_name)
    if model is None:
        return None

    try:
        embedding = model.encode(text, convert_to_numpy=True)
        return embedding
    except Exception as e:
        logger.error(f"Error encoding text: {e}")
        return None


def compute_similarity(text1: str, text2: str,
                      model_name: str = 'all-MiniLM-L6-v2') -> float:
    """
    Compute semantic similarity between two texts.

    Args:
        text1: First text
        text2: Second text
        model_name: SBERT model to use

    Returns:
        Similarity score (0.0 to 1.0), or 0.0 on error
    """
    if not SBERT_AVAILABLE:
        return _fallback_similarity(text1, text2)

    model = load_sbert_model(model_name)
    if model is None:
        return _fallback_similarity(text1, text2)

    try:
        # Encode both texts
        embeddings = model.encode([text1, text2], convert_to_numpy=True)

        # Compute cosine similarity
        if SKLEARN_AVAILABLE:
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
        else:
            # Manual cosine similarity
            similarity = _cosine_similarity(embeddings[0], embeddings[1])

        return float(similarity)
    except Exception as e:
        logger.error(f"Error computing similarity: {e}")
        return _fallback_similarity(text1, text2)


def compute_similarity_matrix(texts: List[str],
                              model_name: str = 'all-MiniLM-L6-v2',
                              batch_size: int = 32) -> np.ndarray:
    """
    Compute pairwise similarity matrix for multiple texts.

    Args:
        texts: List of text strings
        model_name: SBERT model to use
        batch_size: Batch size for encoding

    Returns:
        N x N similarity matrix
    """
    n = len(texts)

    if not SBERT_AVAILABLE:
        logger.warning("SBERT not available, using fallback")
        return _fallback_similarity_matrix(texts)

    model = load_sbert_model(model_name)
    if model is None:
        return _fallback_similarity_matrix(texts)

    try:
        # Encode all texts
        logger.info(f"Encoding {n} texts with SBERT...")
        embeddings = model.encode(texts, batch_size=batch_size,
                                 convert_to_numpy=True, show_progress_bar=False)

        # Compute similarity matrix
        if SKLEARN_AVAILABLE:
            similarity_matrix = cosine_similarity(embeddings)
        else:
            # Manual computation
            similarity_matrix = np.zeros((n, n))
            for i in range(n):
                for j in range(n):
                    similarity_matrix[i, j] = _cosine_similarity(embeddings[i], embeddings[j])

        return similarity_matrix
    except Exception as e:
        logger.error(f"Error computing similarity matrix: {e}")
        return _fallback_similarity_matrix(texts)


def find_similar_interviews(target_interview: Dict[str, Any],
                           all_interviews: List[Dict[str, Any]],
                           top_k: int = 5,
                           model_name: str = 'all-MiniLM-L6-v2') -> List[Dict[str, Any]]:
    """
    Find interviews most similar to a target interview.

    Args:
        target_interview: Interview to find matches for
        all_interviews: Pool of all interviews
        top_k: Number of similar interviews to return
        model_name: SBERT model to use

    Returns:
        List of similar interviews with similarity scores
    """
    # Extract text from target
    target_text = _extract_interview_text(target_interview)

    # Extract texts from all interviews
    all_texts = [_extract_interview_text(interview) for interview in all_interviews]

    # Compute similarities
    similarities = []
    for i, interview_text in enumerate(all_texts):
        if i < len(all_interviews):  # Safety check
            similarity = compute_similarity(target_text, interview_text, model_name)
            similarities.append({
                'interview': all_interviews[i],
                'similarity': similarity,
                'index': i
            })

    # Sort by similarity (descending)
    similarities.sort(key=lambda x: x['similarity'], reverse=True)

    # Return top k (excluding exact match if present)
    results = []
    for item in similarities:
        # Skip if it's the exact same interview (similarity ~1.0)
        if item['similarity'] < 0.999:
            results.append(item)
            if len(results) >= top_k:
                break

    return results


def cluster_interviews(interviews: List[Dict[str, Any]],
                      num_clusters: int = 5,
                      method: str = 'kmeans',
                      model_name: str = 'all-MiniLM-L6-v2') -> Dict[str, Any]:
    """
    Cluster interviews based on semantic similarity.

    Args:
        interviews: List of interview dictionaries
        num_clusters: Number of clusters to create
        method: 'kmeans' or 'hierarchical'
        model_name: SBERT model to use

    Returns:
        Dictionary with clustering results:
        {
            'cluster_labels': [0, 1, 0, 2, ...],
            'clusters': {
                0: [interview_indices],
                1: [...],
                ...
            },
            'cluster_sizes': [15, 12, 18, ...],
            'cluster_representatives': [interview_idx, ...],
            'silhouette_score': 0.45
        }
    """
    if not interviews:
        return {'error': 'No interviews provided'}

    # Extract texts
    texts = [_extract_interview_text(interview) for interview in interviews]

    if not SBERT_AVAILABLE or not SKLEARN_AVAILABLE:
        return _fallback_clustering(interviews, num_clusters)

    model = load_sbert_model(model_name)
    if model is None:
        return _fallback_clustering(interviews, num_clusters)

    try:
        # Encode all interviews
        logger.info(f"Encoding {len(texts)} interviews for clustering...")
        embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=False)

        # Perform clustering
        if method == 'kmeans':
            clusterer = KMeans(n_clusters=num_clusters, random_state=42, n_init=10)
        elif method == 'hierarchical':
            clusterer = AgglomerativeClustering(n_clusters=num_clusters)
        else:
            raise ValueError(f"Unknown clustering method: {method}")

        cluster_labels = clusterer.fit_predict(embeddings)

        # Organize clusters
        clusters = {}
        for i, label in enumerate(cluster_labels):
            if label not in clusters:
                clusters[label] = []
            clusters[label].append(i)

        # Find representative (centroid-closest) for each cluster
        cluster_representatives = []
        for cluster_id in range(num_clusters):
            cluster_indices = clusters.get(cluster_id, [])
            if cluster_indices:
                # Find interview closest to cluster center
                cluster_embeddings = embeddings[cluster_indices]
                centroid = cluster_embeddings.mean(axis=0)

                # Find closest to centroid
                distances = [_euclidean_distance(embeddings[idx], centroid)
                           for idx in cluster_indices]
                closest_idx = cluster_indices[np.argmin(distances)]
                cluster_representatives.append(closest_idx)
            else:
                cluster_representatives.append(None)

        # Calculate silhouette score
        try:
            from sklearn.metrics import silhouette_score
            silhouette = silhouette_score(embeddings, cluster_labels)
        except:
            silhouette = None

        return {
            'cluster_labels': cluster_labels.tolist(),
            'clusters': {int(k): v for k, v in clusters.items()},
            'cluster_sizes': [len(clusters.get(i, [])) for i in range(num_clusters)],
            'cluster_representatives': cluster_representatives,
            'silhouette_score': float(silhouette) if silhouette is not None else None,
            'method': method,
            'num_clusters': num_clusters,
            'embedding_dim': embeddings.shape[1]
        }

    except Exception as e:
        logger.error(f"Error clustering interviews: {e}")
        return {'error': str(e)}


def analyze_interview_similarity(interview_data: Dict[str, Any],
                                 all_interviews: List[Dict[str, Any]],
                                 model_name: str = 'all-MiniLM-L6-v2') -> Dict[str, Any]:
    """
    Comprehensive similarity analysis for a single interview.

    Args:
        interview_data: Target interview
        all_interviews: All interviews for comparison
        model_name: SBERT model to use

    Returns:
        Dictionary with similarity analysis
    """
    # Find similar interviews
    similar = find_similar_interviews(
        interview_data,
        all_interviews,
        top_k=5,
        model_name=model_name
    )

    # Extract interview text
    interview_text = _extract_interview_text(interview_data)

    # Encode interview
    embedding = encode_text(interview_text, model_name)

    return {
        'similar_interviews': similar,
        'num_similar_above_70': sum(1 for s in similar if s['similarity'] > 0.7),
        'num_similar_above_80': sum(1 for s in similar if s['similarity'] > 0.8),
        'num_similar_above_90': sum(1 for s in similar if s['similarity'] > 0.9),
        'average_similarity_top5': np.mean([s['similarity'] for s in similar]) if similar else 0.0,
        'max_similarity': similar[0]['similarity'] if similar else 0.0,
        'embedding_available': embedding is not None,
        'embedding_dim': len(embedding) if embedding is not None else 0
    }


def find_topic_themes(interviews: List[Dict[str, Any]],
                     similarity_threshold: float = 0.75,
                     model_name: str = 'all-MiniLM-L6-v2') -> Dict[str, Any]:
    """
    Discover thematic groups based on semantic similarity.

    Args:
        interviews: List of interviews
        similarity_threshold: Minimum similarity to group together
        model_name: SBERT model to use

    Returns:
        Dictionary with thematic groups
    """
    # Compute similarity matrix
    texts = [_extract_interview_text(interview) for interview in interviews]
    similarity_matrix = compute_similarity_matrix(texts, model_name)

    # Find groups based on threshold
    n = len(interviews)
    visited = set()
    themes = []

    for i in range(n):
        if i in visited:
            continue

        # Find all interviews similar to this one
        similar_indices = [j for j in range(n)
                          if similarity_matrix[i, j] >= similarity_threshold and j != i]

        if similar_indices:
            theme_group = [i] + similar_indices
            themes.append(theme_group)
            visited.update(theme_group)

    return {
        'num_themes': len(themes),
        'themes': themes,
        'theme_sizes': [len(theme) for theme in themes],
        'similarity_threshold': similarity_threshold,
        'coverage': len(visited) / n if n > 0 else 0.0
    }


# Helper functions

def _extract_interview_text(interview: Dict[str, Any]) -> str:
    """Extract full text from interview dictionary."""
    transcript = interview.get('transcript', [])
    if isinstance(transcript, list):
        texts = [turn.get('text', '') for turn in transcript]
        return ' '.join(texts)
    elif isinstance(transcript, str):
        return transcript
    else:
        return interview.get('text', '')


def _cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Manual cosine similarity computation."""
    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def _euclidean_distance(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """Compute Euclidean distance between vectors."""
    return np.linalg.norm(vec1 - vec2)


def _fallback_similarity(text1: str, text2: str) -> float:
    """
    Fallback similarity using simple word overlap (Jaccard).
    Used when SBERT is not available.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    if not words1 or not words2:
        return 0.0

    intersection = words1.intersection(words2)
    union = words1.union(words2)

    return len(intersection) / len(union) if union else 0.0


def _fallback_similarity_matrix(texts: List[str]) -> np.ndarray:
    """Fallback similarity matrix using word overlap."""
    n = len(texts)
    matrix = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            matrix[i, j] = _fallback_similarity(texts[i], texts[j])

    return matrix


def _fallback_clustering(interviews: List[Dict[str, Any]],
                        num_clusters: int) -> Dict[str, Any]:
    """Simple fallback clustering based on keyword similarity."""
    logger.warning("Using fallback clustering (word overlap)")

    texts = [_extract_interview_text(interview) for interview in interviews]
    similarity_matrix = _fallback_similarity_matrix(texts)

    # Simple greedy clustering
    n = len(interviews)
    cluster_labels = [-1] * n
    current_cluster = 0

    for i in range(n):
        if cluster_labels[i] == -1:
            cluster_labels[i] = current_cluster
            # Assign similar items to same cluster
            for j in range(i + 1, n):
                if cluster_labels[j] == -1 and similarity_matrix[i, j] > 0.3:
                    cluster_labels[j] = current_cluster
            current_cluster += 1
            if current_cluster >= num_clusters:
                break

    # Assign remaining to closest cluster
    for i in range(n):
        if cluster_labels[i] == -1:
            cluster_labels[i] = 0

    # Organize results
    clusters = {}
    for i, label in enumerate(cluster_labels):
        if label not in clusters:
            clusters[label] = []
        clusters[label].append(i)

    return {
        'cluster_labels': cluster_labels,
        'clusters': clusters,
        'cluster_sizes': [len(clusters.get(i, [])) for i in range(num_clusters)],
        'method': 'fallback',
        'warning': 'SBERT not available, using simple word overlap'
    }


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'sentence_transformers': SBERT_AVAILABLE,
        'sklearn': SKLEARN_AVAILABLE,
        'has_semantic_similarity': SBERT_AVAILABLE,
        'cuda_available': torch.cuda.is_available() if SBERT_AVAILABLE else False
    }


if __name__ == '__main__':
    # Test the module
    test_interviews = [
        {
            'transcript': [
                {'text': 'I am having a wonderful pregnancy. Everything is going great with the baby.'},
                {'text': 'No complications so far. Very excited about becoming a mother.'}
            ]
        },
        {
            'transcript': [
                {'text': 'My pregnancy has been challenging. I have gestational diabetes.'},
                {'text': 'Managing my blood sugar is difficult but the doctors are helping.'}
            ]
        },
        {
            'transcript': [
                {'text': 'This has been an amazing experience. The baby is healthy and growing well.'},
                {'text': 'I feel blessed and grateful for this pregnancy journey.'}
            ]
        }
    ]

    print("Semantic Similarity Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"Sentence-BERT available: {status['sentence_transformers']}")
    print(f"scikit-learn available: {status['sklearn']}")
    print(f"CUDA available: {status['cuda_available']}")
    print()

    if status['has_semantic_similarity']:
        # Test similarity between two interviews
        text1 = _extract_interview_text(test_interviews[0])
        text2 = _extract_interview_text(test_interviews[2])

        print("Testing similarity between Interview 0 and Interview 2:")
        similarity = compute_similarity(text1, text2)
        print(f"  Similarity score: {similarity:.3f}")
        print()

        # Test clustering
        print("Testing clustering of 3 interviews:")
        clustering = cluster_interviews(test_interviews, num_clusters=2)
        print(f"  Cluster labels: {clustering.get('cluster_labels', 'N/A')}")
        print(f"  Cluster sizes: {clustering.get('cluster_sizes', 'N/A')}")
        if clustering.get('silhouette_score'):
            print(f"  Silhouette score: {clustering['silhouette_score']:.3f}")
        print()

        # Test finding similar interviews
        print("Finding interviews similar to Interview 1:")
        similar = find_similar_interviews(test_interviews[1], test_interviews, top_k=2)
        for i, item in enumerate(similar):
            print(f"  {i+1}. Interview {item['index']}: similarity = {item['similarity']:.3f}")
    else:
        print("Semantic similarity not available.")
        print("Install with: pip install sentence-transformers scikit-learn")
