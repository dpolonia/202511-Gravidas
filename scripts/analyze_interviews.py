#!/usr/bin/env python3
"""
Analyze interview data and export summaries with cost tracking and clinical information.

This script:
1. Loads all interview JSON files
2. Extracts key themes and topics
3. Calculates interview costs based on token usage
4. Extracts clinical information from health records
5. Generates CSV summaries for analysis
6. Creates statistical reports

Usage:
    python scripts/analyze_interviews.py
    python scripts/analyze_interviews.py --export-csv
    python scripts/analyze_interviews.py --show-details
    python scripts/analyze_interviews.py --show-clinical
"""

import json
import csv
import re
import logging
import sys
import statistics
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import argparse

# NLP imports with fallback handling
try:
    import nltk
    from nltk.tokenize import word_tokenize
    from nltk.corpus import stopwords
    from nltk.stem import WordNetLemmatizer
    # Ensure required NLTK data is available
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        nltk.download('punkt', quiet=True)
    try:
        nltk.data.find('corpora/stopwords')
    except LookupError:
        nltk.download('stopwords', quiet=True)
    try:
        nltk.data.find('corpora/wordnet')
    except LookupError:
        nltk.download('wordnet', quiet=True)
    NLTK_AVAILABLE = True
except ImportError:
    NLTK_AVAILABLE = False

# Sentiment analysis with fallback
try:
    from nltk.sentiment import SentimentIntensityAnalyzer
    VADER_AVAILABLE = NLTK_AVAILABLE
    if NLTK_AVAILABLE:
        try:
            nltk.data.find('sentiment/vader_lexicon.zip')
        except LookupError:
            nltk.download('vader_lexicon', quiet=True)
except ImportError:
    VADER_AVAILABLE = False


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Model pricing per 1M tokens (input, output)
MODEL_COSTS = {
    'claude-sonnet-4-5-20250929': {'input': 3.0, 'output': 15.0},
    'claude-haiku-4-5': {'input': 1.0, 'output': 5.0},
    'claude-opus-4-1': {'input': 15.0, 'output': 75.0},
    'gpt-5': {'input': 1.25, 'output': 10.0},
    'gpt-5-pro': {'input': 2.5, 'output': 20.0},
    'gpt-5-chatgpt': {'input': 0.5, 'output': 2.0},
    'gemini-2.5-pro': {'input': 1.25, 'output': 10.0},
    'gemini-2.5-flash': {'input': 0.15, 'output': 0.60},
    'gemini-2.5-pro-thinking': {'input': 1.25, 'output': 10.0},
    'gemini-2.5-flash-thinking': {'input': 0.15, 'output': 0.60},
}

# Required fields for validation
INTERVIEW_REQUIRED_FIELDS = {
    'transcript', 'persona_id', 'persona_age', 'timestamp', 'filename'
}
TRANSCRIPT_REQUIRED_FIELDS = {'speaker', 'text'}
MATCHED_PERSONA_REQUIRED_FIELDS = {'persona', 'health_record'}


def validate_matched_persona_schema(persona_data: Dict[str, Any], filename: str = 'unknown') -> Tuple[bool, Optional[str]]:
    """
    Validate matched persona JSON schema.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(persona_data, dict):
        return False, "Matched persona entry is not a dictionary"

    missing_fields = MATCHED_PERSONA_REQUIRED_FIELDS - set(persona_data.keys())
    if missing_fields:
        return False, f"Missing required fields: {missing_fields}"

    # Validate persona structure
    persona = persona_data.get('persona', {})
    if not isinstance(persona, dict):
        return False, "Persona field is not a dictionary"
    if 'id' not in persona:
        return False, "Persona missing 'id' field"

    # Validate health_record structure
    health_record = persona_data.get('health_record', {})
    if not isinstance(health_record, dict):
        return False, "Health record is not a dictionary"

    return True, None


def validate_interview_schema(interview_data: Dict[str, Any], filename: str = 'unknown') -> Tuple[bool, Optional[str]]:
    """
    Validate interview JSON schema and required fields.

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not isinstance(interview_data, dict):
        return False, "Interview data is not a dictionary"

    missing_fields = INTERVIEW_REQUIRED_FIELDS - set(interview_data.keys())
    if missing_fields:
        return False, f"Missing required fields: {missing_fields}"

    # Validate transcript structure
    transcript = interview_data.get('transcript')
    if not isinstance(transcript, list):
        return False, "Transcript is not a list"

    if len(transcript) == 0:
        return False, "Transcript is empty"

    # Validate each transcript entry
    for i, entry in enumerate(transcript):
        if not isinstance(entry, dict):
            return False, f"Transcript entry {i} is not a dictionary"

        missing_transcript_fields = TRANSCRIPT_REQUIRED_FIELDS - set(entry.keys())
        if missing_transcript_fields:
            return False, f"Transcript entry {i} missing fields: {missing_transcript_fields}"

        # Validate speaker field
        speaker = entry.get('speaker', '')
        if speaker not in ['Interviewer', 'Persona']:
            return False, f"Transcript entry {i} has invalid speaker: '{speaker}' (must be 'Interviewer' or 'Persona')"

        # Validate text field is string
        if not isinstance(entry.get('text'), str):
            return False, f"Transcript entry {i} text is not a string"

    # Validate persona_age is numeric
    persona_age = interview_data.get('persona_age')
    if not isinstance(persona_age, (int, float)):
        try:
            int(persona_age)
        except (ValueError, TypeError):
            return False, f"persona_age '{persona_age}' is not numeric"

    return True, None


# Initialize NLP tools if available
LEMMATIZER = None
SENTIMENT_ANALYZER = None

if NLTK_AVAILABLE:
    LEMMATIZER = WordNetLemmatizer()
if VADER_AVAILABLE:
    SENTIMENT_ANALYZER = SentimentIntensityAnalyzer()


def tokenize_and_lemmatize(text: str) -> List[str]:
    """
    Tokenize and lemmatize text with fallback to simple split.

    Returns:
        List of lemmatized tokens
    """
    if not NLTK_AVAILABLE or LEMMATIZER is None:
        # Fallback: simple tokenization
        return [word.lower() for word in text.split()]

    try:
        tokens = word_tokenize(text.lower())
        lemmatized = [LEMMATIZER.lemmatize(token) for token in tokens
                     if token.isalnum()]  # Filter out punctuation
        return lemmatized
    except Exception as e:
        logger.debug(f"Lemmatization failed: {e}, using simple split")
        return [word.lower() for word in text.split()]


def analyze_sentiment(text: str) -> Dict[str, float]:
    """
    Analyze sentiment of text using VADER.

    Returns:
        Dict with sentiment scores (positive, negative, neutral, compound)
    """
    if not VADER_AVAILABLE or SENTIMENT_ANALYZER is None:
        return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}

    try:
        scores = SENTIMENT_ANALYZER.polarity_scores(text)
        return {
            'positive': scores['pos'],
            'negative': scores['neg'],
            'neutral': scores['neu'],
            'compound': scores['compound']
        }
    except Exception as e:
        logger.debug(f"Sentiment analysis failed: {e}")
        return {'positive': 0.0, 'negative': 0.0, 'neutral': 1.0, 'compound': 0.0}


def extract_key_phrases(text: str, top_n: int = 10) -> List[Tuple[str, int]]:
    """
    Extract key phrases (most frequent tokens) from text.

    Returns:
        List of (phrase, frequency) tuples
    """
    tokens = tokenize_and_lemmatize(text)

    # Remove common stopwords if NLTK available
    if NLTK_AVAILABLE:
        try:
            stop_words = set(stopwords.words('english'))
            tokens = [t for t in tokens if t not in stop_words and len(t) > 2]
        except Exception:
            tokens = [t for t in tokens if len(t) > 2]

    counter = Counter(tokens)
    return counter.most_common(top_n)


def analyze_themes_advanced(text: str, keywords_map: Dict[str, List[str]]) -> Dict[str, Dict[str, Any]]:
    """
    Advanced theme analysis using both substring and lemmatized token matching.

    Returns:
        Dict mapping theme names to counts and top phrases
    """
    tokens = tokenize_and_lemmatize(text)
    token_counter = Counter(tokens)

    theme_results = {}
    for theme, keywords in keywords_map.items():
        # Count substring matches (original behavior)
        substring_count = sum(text.lower().count(kw.lower()) for kw in keywords)

        # Count lemmatized token matches
        lemmatized_keywords = []
        for kw in keywords:
            lemmatized_kw = tokenize_and_lemmatize(kw)
            lemmatized_keywords.extend(lemmatized_kw)

        token_count = sum(token_counter.get(lkw, 0) for lkw in lemmatized_keywords)

        # Use average of both methods for robustness
        final_count = (substring_count + token_count) / 2.0

        theme_results[theme] = {
            'count': final_count,
            'substring_matches': substring_count,
            'token_matches': token_count
        }

    return theme_results


def analyze_conversation_dynamics(transcript: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Analyze conversation dynamics (turn-taking, response lengths, engagement).

    Returns:
        Dict with conversation metrics
    """
    if not transcript:
        return {'avg_turn_length': 0, 'talk_ratio': 0, 'interaction_balance': 0}

    persona_turns = [t for t in transcript if t['speaker'] == 'Persona']
    interviewer_turns = [t for t in transcript if t['speaker'] == 'Interviewer']

    persona_words = sum(len(t['text'].split()) for t in persona_turns)
    interviewer_words = sum(len(t['text'].split()) for t in interviewer_turns)
    total_words = persona_words + interviewer_words

    # Calculate metrics
    persona_talk_ratio = persona_words / total_words if total_words > 0 else 0
    avg_persona_turn = persona_words / len(persona_turns) if persona_turns else 0
    avg_interviewer_turn = interviewer_words / len(interviewer_turns) if interviewer_turns else 0

    # Interaction balance (0 = perfectly balanced, 1 = completely imbalanced)
    interaction_balance = abs(persona_talk_ratio - 0.5) * 2

    return {
        'persona_turns': len(persona_turns),
        'interviewer_turns': len(interviewer_turns),
        'total_turns': len(transcript),
        'persona_words': persona_words,
        'interviewer_words': interviewer_words,
        'avg_persona_turn_length': round(avg_persona_turn, 1),
        'avg_interviewer_turn_length': round(avg_interviewer_turn, 1),
        'persona_talk_ratio': round(persona_talk_ratio, 2),
        'interaction_balance': round(interaction_balance, 2)
    }


def calculate_dispersion_metrics(values: List[float]) -> Dict[str, float]:
    """
    Calculate statistical dispersion metrics for a list of values.

    Returns:
        Dict with mean, median, stdev, variance, min, max
    """
    if not values:
        return {
            'mean': 0.0,
            'median': 0.0,
            'stdev': 0.0,
            'variance': 0.0,
            'min': 0.0,
            'max': 0.0,
            'q1': 0.0,
            'q3': 0.0
        }

    try:
        sorted_values = sorted(values)
        n = len(values)

        # Basic statistics
        mean = sum(values) / n
        median = statistics.median(values)
        stdev = statistics.stdev(values) if n > 1 else 0.0
        variance = statistics.variance(values) if n > 1 else 0.0

        # Quartiles (Q1, Q3)
        q1_index = n // 4
        q3_index = (3 * n) // 4
        q1 = sorted_values[q1_index] if q1_index < n else sorted_values[-1]
        q3 = sorted_values[q3_index] if q3_index < n else sorted_values[-1]

        return {
            'mean': round(mean, 2),
            'median': round(median, 2),
            'stdev': round(stdev, 2),
            'variance': round(variance, 2),
            'min': round(min(values), 2),
            'max': round(max(values), 2),
            'q1': round(q1, 2),
            'q3': round(q3, 2)
        }
    except Exception as e:
        logger.debug(f"Dispersion calculation failed: {e}")
        return {
            'mean': 0.0,
            'median': 0.0,
            'stdev': 0.0,
            'variance': 0.0,
            'min': 0.0,
            'max': 0.0,
            'q1': 0.0,
            'q3': 0.0
        }


def load_matched_personas(matched_file: str = "data/matched/matched_personas.json") -> Tuple[Dict[int, Dict[str, Any]], List[str]]:
    """
    Load matched personas with health records, indexed by persona_id.

    Returns:
        Tuple of (personas_dict, validation_errors)
    """
    validation_errors = []

    try:
        with open(matched_file, 'r') as f:
            matched = json.load(f)
    except FileNotFoundError:
        logger.warning(f"⚠️  Warning: Could not load {matched_file}")
        return {}, [f"File not found: {matched_file}"]
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON in {matched_file}: {e}"
        logger.error(f"❌ {error_msg}")
        validation_errors.append(error_msg)
        return {}, validation_errors

    if not isinstance(matched, list):
        error_msg = f"Expected list of matched personas, got {type(matched).__name__}"
        logger.error(f"❌ {error_msg}")
        validation_errors.append(error_msg)
        return {}, validation_errors

    personas_dict = {}
    for i, m in enumerate(matched):
        is_valid, error_msg = validate_matched_persona_schema(m, matched_file)
        if not is_valid:
            error_full = f"Matched persona entry {i}: {error_msg}"
            logger.warning(f"⚠️  Skipping invalid entry: {error_full}")
            validation_errors.append(error_full)
            continue

        try:
            persona_id = m['persona']['id']
            personas_dict[persona_id] = m
        except (KeyError, TypeError) as e:
            error_full = f"Matched persona entry {i}: Failed to extract persona ID: {e}"
            logger.warning(f"⚠️  Skipping entry: {error_full}")
            validation_errors.append(error_full)

    logger.info(f"✅ Loaded {len(personas_dict)} valid matched personas")
    if validation_errors:
        logger.info(f"   {len(validation_errors)} entries skipped due to validation errors")

    return personas_dict, validation_errors


def load_interviews(interview_dir: str = "data/interviews") -> Tuple[List[Dict[str, Any]], List[str]]:
    """
    Load all interview JSON files with comprehensive error handling.

    Returns:
        Tuple of (interviews_list, validation_errors)
    """
    interview_path = Path(interview_dir)
    interviews = []
    validation_errors = []

    if not interview_path.exists():
        error_msg = f"Interview directory not found: {interview_dir}"
        logger.error(f"❌ {error_msg}")
        validation_errors.append(error_msg)
        return interviews, validation_errors

    interview_files = sorted(interview_path.glob("interview_*.json"))
    if not interview_files:
        logger.warning(f"⚠️  No interview files found in {interview_dir}")
        return interviews, []

    logger.info(f"Found {len(interview_files)} interview files to process")

    for file in interview_files:
        try:
            with open(file, 'r') as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            error_msg = f"Malformed JSON in {file.name}: {e}"
            logger.warning(f"⚠️  Skipping: {error_msg}")
            validation_errors.append(error_msg)
            continue
        except Exception as e:
            error_msg = f"Error reading {file.name}: {e}"
            logger.warning(f"⚠️  Skipping: {error_msg}")
            validation_errors.append(error_msg)
            continue

        # Validate schema before adding
        is_valid, error_msg = validate_interview_schema(data, file.name)
        if not is_valid:
            error_full = f"{file.name}: {error_msg}"
            logger.warning(f"⚠️  Skipping: {error_full}")
            validation_errors.append(error_full)
            continue

        # Add filename for tracking
        data['filename'] = file.name
        interviews.append(data)

    logger.info(f"✅ Loaded {len(interviews)} valid interview(s)")
    if validation_errors:
        logger.info(f"   {len(validation_errors)} file(s) skipped due to errors")

    return interviews, validation_errors


def estimate_tokens(text: str) -> int:
    """Estimate token count (rough approximation: 1 token ≈ 0.75 words)."""
    words = len(text.split())
    return int(words / 0.75)


def calculate_interview_cost(interview: Dict[str, Any], model: Optional[str] = None) -> Dict[str, Any]:
    """
    Calculate comprehensive cost breakdown for an interview with confidence intervals.

    Args:
        interview: Interview data with transcript
        model: Override model (otherwise uses interview data or default)

    Returns:
        Dict with precise costs, token breakdown, and confidence intervals
    """
    # Extract model from interview if not provided
    if model is None:
        model = interview.get('model', interview.get('interview_model', 'claude-sonnet-4-5-20250929'))

    transcript = interview.get('transcript', [])

    # Separate input (interviewer) and output (persona)
    input_text = ' '.join([t['text'] for t in transcript if t['speaker'] == 'Interviewer'])
    output_text = ' '.join([t['text'] for t in transcript if t['speaker'] == 'Persona'])

    # Count words for estimation variance
    input_words = len(input_text.split()) if input_text else 0
    output_words = len(output_text.split()) if output_text else 0
    total_words = input_words + output_words

    # Token estimation with confidence intervals
    # Standard: 1 token ≈ 0.75 words
    # Conservative (max tokens): 1 token ≈ 0.8 words (more tokens)
    # Optimistic (min tokens): 1 token ≈ 0.7 words (fewer tokens)
    input_tokens_std = estimate_tokens(input_text)
    output_tokens_std = estimate_tokens(output_text)

    input_tokens_max = int(input_words / 0.8)  # Conservative estimate
    output_tokens_max = int(output_words / 0.8)
    input_tokens_min = int(input_words / 0.7)  # Optimistic estimate
    output_tokens_min = int(output_words / 0.7)

    # Get pricing
    costs = MODEL_COSTS.get(model, {'input': 3.0, 'output': 15.0})

    # Calculate costs (per million tokens)
    # Standard estimate
    input_cost_std = (input_tokens_std / 1_000_000) * costs['input']
    output_cost_std = (output_tokens_std / 1_000_000) * costs['output']
    total_cost_std = input_cost_std + output_cost_std

    # Confidence interval (min/max)
    input_cost_min = (input_tokens_min / 1_000_000) * costs['input']
    output_cost_min = (output_tokens_min / 1_000_000) * costs['output']
    total_cost_min = input_cost_min + output_cost_min

    input_cost_max = (input_tokens_max / 1_000_000) * costs['input']
    output_cost_max = (output_tokens_max / 1_000_000) * costs['output']
    total_cost_max = input_cost_max + output_cost_max

    return {
        # Token breakdown
        'input_tokens': input_tokens_std,
        'output_tokens': output_tokens_std,
        'total_tokens': input_tokens_std + output_tokens_std,
        'input_words': input_words,
        'output_words': output_words,
        'total_words': total_words,
        # Token confidence intervals
        'input_tokens_min': input_tokens_min,
        'input_tokens_max': input_tokens_max,
        'output_tokens_min': output_tokens_min,
        'output_tokens_max': output_tokens_max,
        'total_tokens_min': input_tokens_min + output_tokens_min,
        'total_tokens_max': input_tokens_max + output_tokens_max,
        # Cost breakdown (standard estimate)
        'input_cost': input_cost_std,
        'output_cost': output_cost_std,
        'total_cost': total_cost_std,
        # Cost confidence intervals
        'cost_min': total_cost_min,
        'cost_max': total_cost_max,
        'cost_range': total_cost_max - total_cost_min,
        # Model and pricing info
        'model': model,
        'input_price_per_m_tokens': costs['input'],
        'output_price_per_m_tokens': costs['output']
    }


# SNOMED Code Categories for Clinical Classification
SNOMED_CLINICAL_CATEGORIES = {
    'cardiovascular': ['hypertension', 'heart disease', 'cardiac', 'valve', 'arrhythmia', 'angina'],
    'endocrine': ['diabetes', 'thyroid', 'metabolic', 'hormone', 'polycystic ovary'],
    'respiratory': ['asthma', 'pneumonia', 'bronch', 'copd', 'lung disease'],
    'infectious': ['infection', 'tuberculosis', 'hiv', 'hepatitis', 'bacterial', 'viral'],
    'gastrointestinal': ['gastric', 'ulcer', 'crohn', 'colitis', 'liver', 'hepatic'],
    'renal': ['kidney', 'renal', 'nephro', 'glomerulo', 'urinary', 'dialysis'],
    'hematologic': ['anemia', 'leukemia', 'lymphoma', 'blood', 'clotting', 'sickle cell'],
    'psychiatric': ['depression', 'anxiety', 'bipolar', 'schizophrenia', 'ocd', 'ptsd'],
    'neurologic': ['epilepsy', 'seizure', 'parkinson', 'alzheimer', 'stroke', 'migraine'],
    'rheumatologic': ['arthritis', 'lupus', 'rheumatoid', 'connective tissue', 'vasculitis'],
    'obstetric_complication': ['preeclampsia', 'gestational', 'gestational hypertension', 'placenta previa',
                              'abruption', 'iugr', 'intrauterine growth', 'preterm'],
    'pregnancy_related': ['pregnancy', 'prenatal', 'gravida', 'multipara', 'antepartum', 'postpartum'],
}

# Obstetric Risk Factors (1-5 scale impact)
OBSTETRIC_RISK_FACTORS = {
    'advanced_maternal_age': {'term': 'age > 35', 'risk_level': 3, 'baseline_weight': 0.05},
    'maternal_obesity': {'term': 'bmi > 30', 'risk_level': 3, 'baseline_weight': 0.08},
    'diabetes': {'term': 'diabetes', 'risk_level': 4, 'baseline_weight': 0.12},
    'hypertension': {'term': 'hypertension', 'risk_level': 4, 'baseline_weight': 0.10},
    'previous_complications': {'term': 'previous', 'risk_level': 3, 'baseline_weight': 0.08},
    'multiple_pregnancy': {'term': 'multiple', 'risk_level': 3, 'baseline_weight': 0.07},
    'smoking': {'term': 'smoking|tobacco', 'risk_level': 3, 'baseline_weight': 0.06},
    'substance_use': {'term': 'substance|alcohol|drug', 'risk_level': 4, 'baseline_weight': 0.10},
    'mental_health': {'term': 'depression|anxiety|psychiatric', 'risk_level': 2, 'baseline_weight': 0.05},
    'anemia': {'term': 'anemia', 'risk_level': 2, 'baseline_weight': 0.04},
}


def categorize_condition(condition_name: str) -> str:
    """
    Categorize a condition into clinical categories based on SNOMED keywords.

    Returns:
        Clinical category name, or 'other' if no match
    """
    condition_lower = condition_name.lower()

    for category, keywords in SNOMED_CLINICAL_CATEGORIES.items():
        if any(keyword.lower() in condition_lower for keyword in keywords):
            return category

    return 'other'


def calculate_obstetric_risk_score(health_record: Dict[str, Any], persona_age: int) -> Dict[str, Any]:
    """
    Calculate pregnancy-specific obstetric risk score (1-5 scale).

    Returns:
        Dict with risk_score, risk_factors_present, risk_level, recommendations
    """
    conditions = health_record.get('conditions', [])
    medications = health_record.get('medications', [])
    observations = health_record.get('observations', [])

    condition_texts = ' '.join([c.get('display', '').lower() for c in conditions])
    medication_texts = ' '.join([m.get('display', '').lower() for m in medications])
    observation_texts = ' '.join([o.get('display', '').lower() for o in observations])
    all_text = f"{condition_texts} {medication_texts} {observation_texts}"

    risk_score = 1.0  # Start at baseline (low risk)
    risk_factors_present = []

    # Check advanced maternal age
    if persona_age >= 35:
        risk_score += 0.5
        risk_factors_present.append('Advanced maternal age (≥35 years)')

    # Check other risk factors
    for factor_name, factor_info in OBSTETRIC_RISK_FACTORS.items():
        if factor_name == 'advanced_maternal_age':
            continue  # Already handled
        if re.search(factor_info['term'], all_text, re.IGNORECASE):
            risk_score += factor_info['baseline_weight']
            risk_factors_present.append(factor_name.replace('_', ' ').title())

    # Cap risk score at 5
    risk_score = min(risk_score, 5.0)

    # Determine risk level
    if risk_score <= 1.5:
        risk_level = 'Low'
        recommendations = 'Standard prenatal care recommended'
    elif risk_score <= 2.5:
        risk_level = 'Low-Moderate'
        recommendations = 'Enhanced monitoring recommended'
    elif risk_score <= 3.5:
        risk_level = 'Moderate'
        recommendations = 'Specialist consultation and monthly monitoring recommended'
    elif risk_score <= 4.5:
        risk_level = 'High'
        recommendations = 'High-risk prenatal program and frequent specialist follow-up recommended'
    else:
        risk_level = 'Very High'
        recommendations = 'Intensive maternal-fetal medicine management recommended'

    return {
        'obstetric_risk_score': round(risk_score, 2),
        'risk_level': risk_level,
        'risk_factors_count': len(risk_factors_present),
        'risk_factors': '; '.join(risk_factors_present) if risk_factors_present else 'None identified',
        'recommendations': recommendations
    }


def categorize_clinical_conditions(health_record: Dict[str, Any]) -> Dict[str, int]:
    """
    Categorize all conditions into clinical categories.

    Returns:
        Dict mapping category names to condition counts
    """
    conditions = health_record.get('conditions', [])
    category_counts = {}

    for condition in conditions:
        condition_name = condition.get('display', '')
        category = categorize_condition(condition_name)

        if category not in category_counts:
            category_counts[category] = 0
        category_counts[category] += 1

    return category_counts


def extract_clinical_info(health_record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract detailed clinical information from health record."""
    conditions = health_record.get('conditions', [])
    medications = health_record.get('medications', [])
    procedures = health_record.get('procedures', [])
    encounters = health_record.get('encounters', [])
    observations = health_record.get('observations', [])

    # Get top conditions with onset dates
    condition_names = [c.get('display', 'Unknown') for c in conditions[:10]]
    condition_onsets = [c.get('onset', 'Unknown') for c in conditions[:10]]

    # Get active medications with dates
    med_names = [m.get('display', 'Unknown') for m in medications[:10]]
    med_dates = [m.get('authored', 'Unknown') for m in medications[:10]]

    # Get procedures
    proc_names = [p.get('display', 'Unknown') for p in procedures[:5]]

    # Find pregnancy-related conditions
    pregnancy_conditions = [c.get('display', '') for c in conditions
                           if any(term in c.get('display', '').lower()
                                 for term in ['pregnancy', 'prenatal', 'antepartum', 'gravida'])]

    # Get encounter types
    encounter_types = [e.get('type', 'Unknown') for e in encounters[:10]]

    # Extract key observations
    fetal_heart_rate = None
    pregnancy_duration = None
    blood_pressure = None
    weight = None

    for obs in observations:
        display = obs.get('display', '').lower()
        value = obs.get('value')
        unit = obs.get('unit', '')

        if 'fetal heart' in display and fetal_heart_rate is None:
            fetal_heart_rate = f"{value} {unit}"
        elif 'duration of pregnancy' in display and pregnancy_duration is None:
            pregnancy_duration = f"{value} {unit}"
        elif 'blood pressure' in display and blood_pressure is None:
            blood_pressure = f"{value} {unit}"
        elif 'weight' in display and weight is None:
            weight = f"{value} {unit}"

    # Categorize conditions into clinical categories
    condition_categories = categorize_clinical_conditions(health_record)
    categories_summary = '; '.join([f"{cat}({count})" for cat, count in sorted(condition_categories.items())])

    return {
        'num_conditions': len(conditions),
        'num_medications': len(medications),
        'num_procedures': len(procedures),
        'num_encounters': len(encounters),
        'num_observations': len(observations),
        'top_conditions': condition_names,
        'condition_onsets': condition_onsets,
        'active_medications': med_names,
        'medication_dates': med_dates,
        'procedures': proc_names,
        'pregnancy_conditions': pregnancy_conditions,
        'encounter_types': encounter_types,
        'fetal_heart_rate': fetal_heart_rate or 'N/A',
        'pregnancy_duration_weeks': pregnancy_duration or 'N/A',
        'blood_pressure': blood_pressure or 'N/A',
        'weight': weight or 'N/A',
        'condition_categories': condition_categories,
        'condition_categories_summary': categories_summary or 'No conditions',
    }


def analyze_interview(interview: Dict[str, Any], matched_personas: Dict[int, Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """
    Extract key metrics from a single interview.

    Returns:
        Analysis dict or None if analysis fails due to missing critical data
    """
    # Defensive validation of required fields
    if not interview.get('transcript'):
        logger.warning(f"⚠️  Cannot analyze {interview.get('filename', 'unknown')}: Missing or empty transcript")
        return None

    if 'persona_age' not in interview:
        logger.warning(f"⚠️  Cannot analyze {interview.get('filename', 'unknown')}: Missing persona_age")
        return None

    transcript = interview['transcript']
    persona_turns = [t for t in transcript if t['speaker'] == 'Persona']
    interviewer_turns = [t for t in transcript if t['speaker'] == 'Interviewer']

    # Get separate texts
    persona_text = ' '.join([t['text'] for t in persona_turns])
    interviewer_text = ' '.join([t['text'] for t in interviewer_turns])

    # Word counts
    total_words = sum(len(t['text'].split()) for t in transcript)
    persona_words = sum(len(t['text'].split()) for t in persona_turns)
    interviewer_words = sum(len(t['text'].split()) for t in interviewer_turns)

    # Advanced conversation dynamics
    conversation_dynamics = analyze_conversation_dynamics(transcript)

    # Topic mentions with advanced analysis
    topics = {
        'pregnancy': ['pregnant', 'pregnancy', 'baby', 'trimester', 'prenatal', 'birth'],
        'healthcare': ['doctor', 'appointment', 'medical', 'prenatal', 'clinic', 'hospital', 'physician', 'checkup'],
        'symptoms': ['nausea', 'pain', 'tired', 'fatigue', 'sick', 'morning sickness', 'cramps', 'headache'],
        'emotions': ['nervous', 'anxious', 'excited', 'worried', 'happy', 'scared', 'stress', 'stress'],
        'support': ['husband', 'family', 'support', 'help', 'partner', 'mother', 'friend', 'spouse'],
        'financial': ['insurance', 'coverage', 'cost', 'afford', 'pay', 'expense', 'money', 'bill'],
    }

    # Advanced theme analysis (combines substring and token matching)
    topic_analysis = analyze_themes_advanced(persona_text.lower(), topics)
    topic_counts = {topic: int(data['count']) for topic, data in topic_analysis.items()}

    # Sentiment analysis of persona responses
    persona_sentiment = analyze_sentiment(persona_text)

    # Extract key phrases from persona
    persona_key_phrases = extract_key_phrases(persona_text, top_n=5)
    persona_key_phrases_str = '; '.join([phrase[0] for phrase in persona_key_phrases]) if persona_key_phrases else 'N/A'

    # Extract details
    name_match = re.search(r"i'm (\w+),", persona_text)
    weeks_match = re.search(r"(\d+) weeks", persona_text)

    # Calculate costs
    cost_info = calculate_interview_cost(interview)

    # Get clinical information
    persona_id = interview.get('persona_id', 0)
    clinical_info = {}
    if persona_id in matched_personas:
        health_record = matched_personas[persona_id].get('health_record', {})
        clinical_info = extract_clinical_info(health_record)

    analysis = {
        'persona_id': persona_id,
        'persona_age': interview['persona_age'],
        'persona_source': interview.get('persona_source', 'HuggingFace FinePersonas-v0.1'),
        'persona_description': interview.get('persona_description', ''),
        'persona_profile_file': interview.get('persona_profile_file', 'N/A'),
        'synthea_patient_id': interview.get('synthea_patient_id', 'N/A'),
        'synthea_source_file': interview.get('synthea_source_file', 'N/A'),
        'filename': interview['filename'],
        'timestamp': interview['timestamp'],
        'total_turns': conversation_dynamics['total_turns'],
        'persona_turns': conversation_dynamics['persona_turns'],
        'interviewer_turns': conversation_dynamics['interviewer_turns'],
        'total_words': total_words,
        'persona_words': persona_words,
        'interviewer_words': interviewer_words,
        'avg_response_length': conversation_dynamics['avg_persona_turn_length'],
        'avg_interviewer_turn_length': conversation_dynamics['avg_interviewer_turn_length'],
        'persona_talk_ratio': conversation_dynamics['persona_talk_ratio'],
        'interaction_balance': conversation_dynamics['interaction_balance'],
        'persona_name': name_match.group(1) if name_match else 'Unknown',
        'weeks_pregnant': weeks_match.group(1) if weeks_match else 'Unknown',
        'topic_pregnancy': topic_counts['pregnancy'],
        'topic_healthcare': topic_counts['healthcare'],
        'topic_symptoms': topic_counts['symptoms'],
        'topic_emotions': topic_counts['emotions'],
        'topic_support': topic_counts['support'],
        'topic_financial': topic_counts['financial'],
        'persona_sentiment_positive': round(persona_sentiment['positive'], 3),
        'persona_sentiment_negative': round(persona_sentiment['negative'], 3),
        'persona_sentiment_neutral': round(persona_sentiment['neutral'], 3),
        'persona_sentiment_compound': round(persona_sentiment['compound'], 3),
        'persona_key_phrases': persona_key_phrases_str,
        # Token breakdown
        'input_tokens': cost_info['input_tokens'],
        'output_tokens': cost_info['output_tokens'],
        'total_tokens': cost_info['total_tokens'],
        'input_words': cost_info['input_words'],
        'output_words': cost_info['output_words'],
        'total_words': cost_info['total_words'],
        # Token confidence intervals
        'input_tokens_min': cost_info['input_tokens_min'],
        'input_tokens_max': cost_info['input_tokens_max'],
        'output_tokens_min': cost_info['output_tokens_min'],
        'output_tokens_max': cost_info['output_tokens_max'],
        'total_tokens_min': cost_info['total_tokens_min'],
        'total_tokens_max': cost_info['total_tokens_max'],
        # Cost breakdown
        'input_cost': cost_info['input_cost'],
        'output_cost': cost_info['output_cost'],
        'cost_usd': cost_info['total_cost'],
        'cost_min': cost_info['cost_min'],
        'cost_max': cost_info['cost_max'],
        'cost_range': cost_info['cost_range'],
        # Model and pricing
        'model': cost_info['model'],
        'input_price_per_m_tokens': cost_info['input_price_per_m_tokens'],
        'output_price_per_m_tokens': cost_info['output_price_per_m_tokens'],
    }

    # Calculate obstetric risk score if health record available
    obstetric_risk = {
        'obstetric_risk_score': 1.0,
        'risk_level': 'Unknown',
        'risk_factors_count': 0,
        'risk_factors': 'Unknown',
        'recommendations': 'N/A'
    }
    if persona_id in matched_personas:
        obstetric_risk = calculate_obstetric_risk_score(matched_personas[persona_id].get('health_record', {}), interview['persona_age'])

    # Add clinical info
    analysis.update({
        'num_conditions': clinical_info.get('num_conditions', 0),
        'num_medications': clinical_info.get('num_medications', 0),
        'num_procedures': clinical_info.get('num_procedures', 0),
        'num_encounters': clinical_info.get('num_encounters', 0),
        'num_observations': clinical_info.get('num_observations', 0),
        'condition_categories': clinical_info.get('condition_categories_summary', 'N/A'),
        'top_conditions': '; '.join(clinical_info.get('top_conditions', [])[:5]),
        'condition_onsets': '; '.join(clinical_info.get('condition_onsets', [])[:5]),
        'pregnancy_conditions': '; '.join(clinical_info.get('pregnancy_conditions', [])[:3]),
        'active_medications': '; '.join(str(m) for m in clinical_info.get('active_medications', [])[:5] if m is not None),
        'medication_dates': '; '.join(str(d) for d in clinical_info.get('medication_dates', [])[:5] if d is not None),
        'encounter_types': '; '.join(clinical_info.get('encounter_types', [])[:5]),
        'fetal_heart_rate': clinical_info.get('fetal_heart_rate', 'N/A'),
        'pregnancy_duration_weeks': clinical_info.get('pregnancy_duration_weeks', 'N/A'),
        'blood_pressure': clinical_info.get('blood_pressure', 'N/A'),
        'weight': clinical_info.get('weight', 'N/A'),
        # Obstetric risk assessment
        'obstetric_risk_score': obstetric_risk['obstetric_risk_score'],
        'obstetric_risk_level': obstetric_risk['risk_level'],
        'obstetric_risk_factors_count': obstetric_risk['risk_factors_count'],
        'obstetric_risk_factors': obstetric_risk['risk_factors'],
        'obstetric_recommendations': obstetric_risk['recommendations'],
    })

    return analysis


def export_to_csv(analyses: List[Dict[str, Any]], output_file: str = "data/analysis/interview_summary.csv"):
    """Export analysis results to CSV."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        'persona_id', 'persona_age', 'persona_name', 'weeks_pregnant',
        'persona_source', 'persona_description', 'persona_profile_file',
        'synthea_patient_id', 'synthea_source_file',
        'filename', 'timestamp',
        # Conversation dynamics
        'total_turns', 'persona_turns', 'interviewer_turns', 'total_words',
        'persona_words', 'interviewer_words', 'avg_response_length',
        'avg_interviewer_turn_length', 'persona_talk_ratio', 'interaction_balance',
        # Topic analysis
        'topic_pregnancy', 'topic_healthcare', 'topic_symptoms',
        'topic_emotions', 'topic_support', 'topic_financial',
        # Sentiment and key phrases
        'persona_sentiment_positive', 'persona_sentiment_negative',
        'persona_sentiment_neutral', 'persona_sentiment_compound',
        'persona_key_phrases',
        # Cost analysis - word and token breakdown
        'input_words', 'output_words', 'total_words',
        'input_tokens', 'output_tokens', 'total_tokens',
        'input_tokens_min', 'input_tokens_max', 'output_tokens_min', 'output_tokens_max',
        'total_tokens_min', 'total_tokens_max',
        # Cost analysis - pricing and confidence intervals
        'input_cost', 'output_cost', 'cost_usd', 'cost_min', 'cost_max', 'cost_range',
        'model', 'input_price_per_m_tokens', 'output_price_per_m_tokens',
        # Clinical data
        'num_conditions', 'num_medications', 'num_procedures', 'num_encounters', 'num_observations',
        'condition_categories',
        'top_conditions', 'condition_onsets', 'pregnancy_conditions',
        'active_medications', 'medication_dates', 'encounter_types',
        'fetal_heart_rate', 'pregnancy_duration_weeks', 'blood_pressure', 'weight',
        # Obstetric risk assessment
        'obstetric_risk_score', 'obstetric_risk_level', 'obstetric_risk_factors_count',
        'obstetric_risk_factors', 'obstetric_recommendations',
        # Anomaly detection flags
        'is_anomaly', 'anomaly_flags'
    ]

    with open(output_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(analyses)

    print(f"✅ Exported analysis to: {output_file}")


def print_summary(analyses: List[Dict[str, Any]]):
    """Print summary statistics."""
    if not analyses:
        print("No interviews found.")
        return

    print("=" * 80)
    print(f"INTERVIEW COLLECTION SUMMARY")
    print("=" * 80)
    print()
    print(f"📊 Total Interviews: {len(analyses)}")
    print()

    # Aggregate statistics with precise floating-point calculations
    total_words = sum(a['total_words'] for a in analyses)
    total_turns = sum(a['total_turns'] for a in analyses)
    avg_words = total_words / len(analyses)  # Floating-point division
    avg_turns = total_turns / len(analyses)  # Floating-point division

    # Dispersion metrics for words and turns
    words_per_interview = [a['total_words'] for a in analyses]
    turns_per_interview = [a['total_turns'] for a in analyses]
    words_dispersion = calculate_dispersion_metrics(words_per_interview)
    turns_dispersion = calculate_dispersion_metrics(turns_per_interview)

    print(f"💬 CONVERSATION DYNAMICS:")
    persona_words_list = [a['persona_words'] for a in analyses]
    interviewer_words_list = [a['interviewer_words'] for a in analyses]
    talk_ratio_list = [a['persona_talk_ratio'] for a in analyses]
    interaction_balance_list = [a['interaction_balance'] for a in analyses]

    persona_words_stats = calculate_dispersion_metrics(persona_words_list)
    interviewer_words_stats = calculate_dispersion_metrics(interviewer_words_list)
    talk_ratio_stats = calculate_dispersion_metrics(talk_ratio_list)
    interaction_balance_stats = calculate_dispersion_metrics(interaction_balance_list)

    print(f"   Total Words: {total_words:,}")
    print(f"   Total Turns: {total_turns:,} ({sum(a['persona_turns'] for a in analyses)} persona, {sum(a['interviewer_turns'] for a in analyses)} interviewer)")
    print(f"   Words per Interview: Mean={avg_words:.1f}, Median={words_dispersion['median']:.1f}, StdDev={words_dispersion['stdev']:.1f}")
    print(f"                        Min={words_dispersion['min']:.0f}, Q1={words_dispersion['q1']:.0f}, Q3={words_dispersion['q3']:.0f}, Max={words_dispersion['max']:.0f}")
    print(f"   Turns per Interview: Mean={avg_turns:.1f}, Median={turns_dispersion['median']:.1f}, StdDev={turns_dispersion['stdev']:.1f}")
    print(f"   Persona Words:       Mean={persona_words_stats['mean']:.1f}, Median={persona_words_stats['median']:.1f}, StdDev={persona_words_stats['stdev']:.1f}")
    print(f"   Interviewer Words:   Mean={interviewer_words_stats['mean']:.1f}, Median={interviewer_words_stats['median']:.1f}, StdDev={interviewer_words_stats['stdev']:.1f}")
    print(f"   Persona Talk Ratio:  Mean={talk_ratio_stats['mean']:.1%}, Median={talk_ratio_stats['median']:.1%} (range {talk_ratio_stats['min']:.0%} to {talk_ratio_stats['max']:.0%})")
    print(f"   Interaction Balance: Mean={interaction_balance_stats['mean']:.2f}, Median={interaction_balance_stats['median']:.2f} (0=balanced, 1=imbalanced)")
    print()

    # Cost statistics
    total_cost = sum(a['cost_usd'] for a in analyses)
    avg_cost = total_cost / len(analyses)
    total_tokens = sum(a['total_tokens'] for a in analyses)
    avg_tokens = total_tokens / len(analyses)

    # Token breakdown by speaker
    total_input_tokens = sum(a['input_tokens'] for a in analyses)
    total_output_tokens = sum(a['output_tokens'] for a in analyses)
    total_input_words = sum(a['input_words'] for a in analyses)
    total_output_words = sum(a['output_words'] for a in analyses)

    # Cost breakdown
    total_input_cost = sum(a['input_cost'] for a in analyses)
    total_output_cost = sum(a['output_cost'] for a in analyses)
    total_cost_min = sum(a['cost_min'] for a in analyses)
    total_cost_max = sum(a['cost_max'] for a in analyses)

    # Token and cost dispersion
    tokens_per_interview = [a['total_tokens'] for a in analyses]
    costs_per_interview = [a['cost_usd'] for a in analyses]
    tokens_min_per_interview = [a['total_tokens_min'] for a in analyses]
    tokens_max_per_interview = [a['total_tokens_max'] for a in analyses]
    cost_min_per_interview = [a['cost_min'] for a in analyses]
    cost_max_per_interview = [a['cost_max'] for a in analyses]

    tokens_stats = calculate_dispersion_metrics(tokens_per_interview)
    costs_stats = calculate_dispersion_metrics(costs_per_interview)
    tokens_min_stats = calculate_dispersion_metrics(tokens_min_per_interview)
    tokens_max_stats = calculate_dispersion_metrics(tokens_max_per_interview)

    print(f"💰 COST ANALYSIS:")
    print(f"   Total Cost (Standard): ${total_cost:.4f}")
    print(f"   Total Cost Range: ${total_cost_min:.4f} - ${total_cost_max:.4f}")
    print(f"   Cost Confidence Interval: ${costs_stats['min']:.4f} to ${costs_stats['max']:.4f} per interview")
    print(f"   Avg Cost per Interview: ${avg_cost:.4f} (StdDev=${costs_stats['stdev']:.4f})")
    print()
    print(f"   Token Breakdown (Standard):")
    print(f"      Input (Interviewer): {total_input_tokens:,} tokens from {total_input_words:,} words")
    print(f"      Output (Persona):    {total_output_tokens:,} tokens from {total_output_words:,} words")
    print(f"      Total:               {total_tokens:,} tokens")
    print(f"   Cost Breakdown (Standard):")
    print(f"      Input Cost:  ${total_input_cost:.4f}")
    print(f"      Output Cost: ${total_output_cost:.4f}")
    print(f"   Token Confidence Intervals per Interview:")
    print(f"      Min (Optimistic): {int(tokens_min_stats['min'])} - {int(tokens_min_stats['max'])} tokens")
    print(f"      Max (Conservative): {int(tokens_max_stats['min'])} - {int(tokens_max_stats['max'])} tokens")
    print(f"   Model: {analyses[0]['model']}")
    print(f"   Pricing: ${analyses[0]['input_price_per_m_tokens']:.2f}/M input tokens, ${analyses[0]['output_price_per_m_tokens']:.2f}/M output tokens")
    print()

    # Age distribution
    ages = [a['persona_age'] for a in analyses]
    ages_stats = calculate_dispersion_metrics(ages)
    print(f"👥 AGE DISTRIBUTION:")
    print(f"   Mean: {ages_stats['mean']:.1f} years, Median: {ages_stats['median']:.1f} years")
    print(f"   Range: {int(ages_stats['min'])} - {int(ages_stats['max'])} years")
    print(f"   StdDev: {ages_stats['stdev']:.1f}, Q1: {int(ages_stats['q1'])}, Q3: {int(ages_stats['q3'])}")
    print()

    # Clinical statistics
    conditions_list = [a['num_conditions'] for a in analyses]
    medications_list = [a['num_medications'] for a in analyses]
    encounters_list = [a['num_encounters'] for a in analyses]
    observations_list = [a['num_observations'] for a in analyses]

    conditions_stats = calculate_dispersion_metrics(conditions_list)
    medications_stats = calculate_dispersion_metrics(medications_list)
    encounters_stats = calculate_dispersion_metrics(encounters_list)
    observations_stats = calculate_dispersion_metrics(observations_list)

    print(f"🏥 CLINICAL SUMMARY:")
    print(f"   Conditions:      Mean={conditions_stats['mean']:.1f}, Median={conditions_stats['median']:.1f}, Range {int(conditions_stats['min'])}-{int(conditions_stats['max'])}")
    print(f"   Medications:     Mean={medications_stats['mean']:.1f}, Median={medications_stats['median']:.1f}, Range {int(medications_stats['min'])}-{int(medications_stats['max'])}")
    print(f"   Encounters:      Mean={encounters_stats['mean']:.1f}, Median={encounters_stats['median']:.1f}, Range {int(encounters_stats['min'])}-{int(encounters_stats['max'])}")
    print(f"   Observations:    Mean={observations_stats['mean']:.1f}, Median={observations_stats['median']:.1f}, Range {int(observations_stats['min'])}-{int(observations_stats['max'])}")
    print()

    # Topic coverage
    print(f"🏷️  TOPIC COVERAGE (Average Mentions):")
    topics = ['pregnancy', 'healthcare', 'symptoms', 'emotions', 'support', 'financial']
    for topic in topics:
        avg = sum(a[f'topic_{topic}'] for a in analyses) / len(analyses)
        print(f"   {topic.capitalize():15} {avg:.1f}")
    print()

    # Sentiment analysis
    avg_sentiment_positive = sum(a['persona_sentiment_positive'] for a in analyses) / len(analyses)
    avg_sentiment_negative = sum(a['persona_sentiment_negative'] for a in analyses) / len(analyses)
    avg_sentiment_compound = sum(a['persona_sentiment_compound'] for a in analyses) / len(analyses)

    print(f"😊 PERSONA SENTIMENT ANALYSIS:")
    print(f"   Avg Positive: {avg_sentiment_positive:.1%}")
    print(f"   Avg Negative: {avg_sentiment_negative:.1%}")
    print(f"   Avg Compound (Overall): {avg_sentiment_compound:.3f} (-1=negative, 0=neutral, 1=positive)")
    print()


def print_detailed_list(analyses: List[Dict[str, Any]]):
    """Print detailed list of all interviews."""
    print("=" * 80)
    print("INTERVIEW DETAILS")
    print("=" * 80)
    print()

    for a in analyses:
        print(f"Interview {a['persona_id']:04d}:")
        print(f"  Name: {a['persona_name']}, Age: {a['persona_age']}")
        print(f"  Weeks Pregnant: {a['weeks_pregnant']}")
        print(f"  Persona Source: {a.get('persona_source', 'N/A')}")
        print(f"  Persona Description: {a.get('persona_description', 'N/A')[:80]}...")
        print(f"  Persona Profile: data/finepersonas_profiles/{a.get('persona_profile_file', 'N/A')}")
        print(f"  Synthea Patient ID: {a.get('synthea_patient_id', 'N/A')}")
        print(f"  Synthea Source File: data/health_records/{a.get('synthea_source_file', 'N/A')}")
        print(f"  Conversation: {a['total_turns']} turns ({a['persona_turns']} persona, {a['interviewer_turns']} interviewer)")
        print(f"  Words: {a['persona_words']:,} persona | {a['interviewer_words']:,} interviewer | Talk ratio: {a['persona_talk_ratio']:.0%}")
        print(f"  Sentiment: Pos={a['persona_sentiment_positive']:.0%} Neg={a['persona_sentiment_negative']:.0%} Compound={a['persona_sentiment_compound']:.2f}")
        print(f"  Key Phrases: {a.get('persona_key_phrases', 'N/A')[:60]}...")
        print(f"  Cost: ${a['cost_usd']:.4f} ({a['total_tokens']:,} tokens)")
        print(f"  File: {a['filename']}")
        print()


def print_clinical_details(analyses: List[Dict[str, Any]]):
    """Print clinical information for each interview."""
    print("=" * 80)
    print("CLINICAL INFORMATION")
    print("=" * 80)
    print()

    for a in analyses:
        print(f"Interview {a['persona_id']:04d} - {a['persona_name']}, Age {a['persona_age']}")
        print(f"  Persona: {a.get('persona_description', 'N/A')[:100]}...")
        print(f"  Persona Source: {a.get('persona_source', 'N/A')}")
        print(f"  Synthea Patient ID: {a.get('synthea_patient_id', 'N/A')}")
        print(f"  Synthea Source File: {a.get('synthea_source_file', 'N/A')}")
        print()
        print(f"  Healthcare Profile:")
        print(f"    • Conditions: {a['num_conditions']}")
        print(f"    • Medications: {a['num_medications']}")
        print(f"    • Procedures: {a['num_procedures']}")
        print(f"    • Encounters: {a['num_encounters']}")
        print(f"    • Observations: {a['num_observations']}")
        print()

        # Vital Signs & Observations
        print(f"  Vital Signs & Key Observations:")
        print(f"    • Fetal Heart Rate: {a.get('fetal_heart_rate', 'N/A')}")
        print(f"    • Pregnancy Duration: {a.get('pregnancy_duration_weeks', 'N/A')}")
        print(f"    • Blood Pressure: {a.get('blood_pressure', 'N/A')}")
        print(f"    • Weight: {a.get('weight', 'N/A')}")
        print()

        if a.get('pregnancy_conditions'):
            print(f"  Pregnancy-Related Conditions:")
            conditions_with_dates = zip(
                a['pregnancy_conditions'].split('; ')[:3],
                a.get('condition_onsets', '').split('; ')[:3]
            )
            for condition, onset in conditions_with_dates:
                if condition:
                    print(f"    • {condition} (onset: {onset})")
            print()

        if a.get('top_conditions'):
            print(f"  All Medical Conditions:")
            conditions_with_dates = zip(
                a['top_conditions'].split('; ')[:5],
                a.get('condition_onsets', '').split('; ')[:5]
            )
            for condition, onset in conditions_with_dates:
                if condition and condition != 'Unknown':
                    print(f"    • {condition} (onset: {onset})")
            print()

        if a.get('active_medications'):
            meds = a['active_medications'].split('; ')[:5]
            med_dates = a.get('medication_dates', '').split('; ')[:5]
            if meds and meds[0]:
                print(f"  Active Medications:")
                for med, date in zip(meds, med_dates):
                    if med and med != 'Unknown':
                        print(f"    • {med} (prescribed: {date})")
                print()

        if a.get('encounter_types'):
            encounters = a['encounter_types'].split('; ')[:5]
            if encounters and encounters[0]:
                print(f"  Recent Healthcare Encounters:")
                for encounter in encounters:
                    if encounter and encounter != 'Unknown':
                        print(f"    • {encounter}")
                print()

        print()


def detect_anomalies(analyses: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Detect anomalies in interview data and flag them.

    Returns:
        Updated analyses list with 'anomaly_flags' added to each record
    """
    for analysis in analyses:
        flags = []

        # Get statistics for comparison
        all_words = [a['total_words'] for a in analyses]
        all_costs = [a['cost_usd'] for a in analyses]
        all_turns = [a['total_turns'] for a in analyses]
        all_sentiment = [a['persona_sentiment_compound'] for a in analyses]

        # Calculate quartiles for anomaly detection
        sorted_words = sorted(all_words)
        sorted_costs = sorted(all_costs)
        sorted_turns = sorted(all_turns)
        q1_words = sorted_words[len(sorted_words) // 4]
        q3_words = sorted_words[(3 * len(sorted_words)) // 4]
        iqr_words = q3_words - q1_words

        # Anomalies: extreme values (outside 1.5*IQR)
        if analysis['total_words'] < (q1_words - 1.5 * iqr_words) or analysis['total_words'] > (q3_words + 1.5 * iqr_words):
            flags.append('Unusual word count')

        if analysis['cost_usd'] > max(all_costs) * 0.9:
            flags.append('High cost')

        if analysis['total_turns'] < 3:
            flags.append('Very short conversation')

        if analysis['total_turns'] > max(all_turns) * 0.9:
            flags.append('Very long conversation')

        # Anomalies: extreme sentiment
        if analysis['persona_sentiment_compound'] < -0.5:
            flags.append('Very negative sentiment')
        elif analysis['persona_sentiment_compound'] > 0.8:
            flags.append('Very positive sentiment')

        # High obstetric risk
        if analysis.get('obstetric_risk_score', 0) >= 3.5:
            flags.append('High obstetric risk')

        # Missing data
        if analysis['synthea_patient_id'] == 'N/A':
            flags.append('No health record')

        analysis['anomaly_flags'] = '; '.join(flags) if flags else ''
        analysis['is_anomaly'] = len(flags) > 0

    return analyses


def filter_analyses(analyses: List[Dict[str, Any]], persona_id: Optional[int] = None,
                   min_turns: int = 0, min_cost: float = 0.0) -> List[Dict[str, Any]]:
    """
    Filter analyses based on criteria.

    Returns:
        Filtered list of analyses
    """
    filtered = analyses

    if persona_id is not None:
        filtered = [a for a in filtered if a['persona_id'] == persona_id]

    if min_turns > 0:
        filtered = [a for a in filtered if a['total_turns'] >= min_turns]

    if min_cost > 0:
        filtered = [a for a in filtered if a['cost_usd'] >= min_cost]

    return filtered


def main():
    parser = argparse.ArgumentParser(description="Analyze interview data with cost tracking and clinical information")
    parser.add_argument('--export-csv', action='store_true',
                        help='Export analysis to CSV file')
    parser.add_argument('--export-json', action='store_true',
                        help='Export analysis to JSON file')
    parser.add_argument('--show-details', action='store_true',
                        help='Show detailed list of all interviews')
    parser.add_argument('--show-clinical', action='store_true',
                        help='Show clinical information for each interview')
    parser.add_argument('--show-anomalies', action='store_true',
                        help='Flag and show anomalies in data')
    parser.add_argument('--json', action='store_true',
                        help='Output summary as JSON')
    parser.add_argument('--persona-id', type=int, default=None,
                        help='Filter results by persona ID')
    parser.add_argument('--min-turns', type=int, default=0,
                        help='Minimum number of conversation turns')
    parser.add_argument('--min-cost', type=float, default=0.0,
                        help='Minimum interview cost in USD')
    args = parser.parse_args()

    logger.info("=" * 80)
    logger.info("INTERVIEW ANALYSIS - DATA LOADING PHASE")
    logger.info("=" * 80)
    logger.info("")

    # Load matched personas with health records
    logger.info("Loading matched personas...")
    matched_personas, persona_errors = load_matched_personas()
    logger.info("")

    # Load and analyze interviews
    logger.info("Loading interviews...")
    interviews, interview_errors = load_interviews()

    if not interviews:
        logger.error("❌ No valid interviews loaded.")
        logger.info("   Run an interview first with: python scripts/04_conduct_interviews.py")
        return

    logger.info("")

    # Report validation errors if any
    if persona_errors:
        logger.info("")
        logger.warning(f"⚠️  Matched Personas Validation Issues ({len(persona_errors)}):")
        for error in persona_errors[:5]:  # Show first 5 errors
            logger.warning(f"   - {error}")
        if len(persona_errors) > 5:
            logger.warning(f"   ... and {len(persona_errors) - 5} more")

    if interview_errors:
        logger.info("")
        logger.warning(f"⚠️  Interview Validation Issues ({len(interview_errors)}):")
        for error in interview_errors[:5]:  # Show first 5 errors
            logger.warning(f"   - {error}")
        if len(interview_errors) > 5:
            logger.warning(f"   ... and {len(interview_errors) - 5} more")

    logger.info("")
    logger.info("=" * 80)
    logger.info("ANALYZING INTERVIEWS")
    logger.info("=" * 80)
    logger.info("")

    # Analyze all interviews
    analyses = [
        analysis for analysis in
        [analyze_interview(interview, matched_personas) for interview in interviews]
        if analysis is not None
    ]

    if not analyses:
        logger.error("❌ No interviews could be analyzed due to validation errors.")
        return

    # Detect anomalies
    analyses = detect_anomalies(analyses)

    # Apply filters
    original_count = len(analyses)
    analyses = filter_analyses(analyses, args.persona_id, args.min_turns, args.min_cost)
    if len(analyses) < original_count:
        logger.info(f"ℹ️  Filtered to {len(analyses)} interviews (from {original_count})")
    logger.info("")

    if not analyses:
        logger.error("❌ No interviews match the filter criteria.")
        return

    # Output as JSON if requested
    if args.json:
        json_output = {
            'summary': {
                'total_interviews': len(analyses),
                'anomalies_detected': sum(1 for a in analyses if a['is_anomaly']),
            },
            'interviews': analyses
        }
        print(json.dumps(json_output, indent=2))
        return

    # Print summary
    print_summary(analyses)

    # Show details if requested
    if args.show_details:
        print_detailed_list(analyses)

    # Show anomalies if requested
    if args.show_anomalies:
        anomalies = [a for a in analyses if a['is_anomaly']]
        if anomalies:
            print()
            print("=" * 80)
            print(f"⚠️  ANOMALIES DETECTED ({len(anomalies)} interviews)")
            print("=" * 80)
            print()
            for a in anomalies:
                print(f"Interview {a['persona_id']:04d}: {a['persona_name']}")
                print(f"  Flags: {a['anomaly_flags']}")
                print()

    # Show clinical info if requested
    if args.show_clinical:
        print_clinical_details(analyses)

    # Export to CSV if requested
    if args.export_csv:
        export_to_csv(analyses)

    # Export to JSON if requested
    if args.export_json:
        output_file = "data/analysis/interview_analysis.json"
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Add anomaly info for export
        export_data = {
            'metadata': {
                'total_interviews': original_count,
                'filtered_interviews': len(analyses),
                'anomalies_detected': sum(1 for a in analyses if a['is_anomaly']),
                'filters_applied': {
                    'persona_id': args.persona_id,
                    'min_turns': args.min_turns,
                    'min_cost': args.min_cost
                }
            },
            'interviews': analyses
        }

        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)
        print(f"✅ Exported analysis to: {output_file}")


if __name__ == "__main__":
    main()
