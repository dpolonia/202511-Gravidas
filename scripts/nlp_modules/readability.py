"""
Readability & Linguistic Complexity Module
===========================================

Measures communication complexity, readability scores, and assesses
health literacy matching between interviewer and participant.

Capability #6 of 11 Advanced NLP Enhancements
"""

import logging
import re
from typing import Dict, List, Any, Optional
import math

logger = logging.getLogger(__name__)

# Try to import textstat
try:
    import textstat
    TEXTSTAT_AVAILABLE = True
    logger.info("✓ textstat available for readability metrics")
except ImportError:
    TEXTSTAT_AVAILABLE = False
    logger.warning("textstat not available. Install with: pip install textstat")


def calculate_readability_scores(text: str) -> Dict[str, Any]:
    """
    Calculate multiple readability scores for text.

    Args:
        text: Input text

    Returns:
        Dictionary with readability metrics:
        {
            'flesch_reading_ease': 65.2,  # 0-100, higher = easier
            'flesch_kincaid_grade': 8.5,  # US grade level
            'smog_index': 10.2,           # Years of education
            'coleman_liau_index': 9.8,
            'automated_readability_index': 9.5,
            'dale_chall_score': 8.2,
            'reading_level': 'high_school',
            'complexity': 'medium'
        }
    """
    if not text or len(text.strip()) < 100:
        return {
            'error': 'Text too short for reliable readability analysis',
            'text_length': len(text)
        }

    if TEXTSTAT_AVAILABLE:
        try:
            scores = {
                'flesch_reading_ease': textstat.flesch_reading_ease(text),
                'flesch_kincaid_grade': textstat.flesch_kincaid_grade(text),
                'smog_index': textstat.smog_index(text),
                'coleman_liau_index': textstat.coleman_liau_index(text),
                'automated_readability_index': textstat.automated_readability_index(text),
                'dale_chall_score': textstat.dale_chall_readability_score(text),
                'difficult_words': textstat.difficult_words(text),
                'lexicon_count': textstat.lexicon_count(text, removepunct=True),
                'syllable_count': textstat.syllable_count(text),
                'sentence_count': textstat.sentence_count(text)
            }

            # Determine reading level
            grade = scores['flesch_kincaid_grade']
            if grade < 6:
                reading_level = 'elementary'
            elif grade < 9:
                reading_level = 'middle_school'
            elif grade < 13:
                reading_level = 'high_school'
            elif grade < 16:
                reading_level = 'college'
            else:
                reading_level = 'graduate'

            # Determine overall complexity
            fre = scores['flesch_reading_ease']
            if fre >= 80:
                complexity = 'very_easy'
            elif fre >= 60:
                complexity = 'easy'
            elif fre >= 50:
                complexity = 'medium'
            elif fre >= 30:
                complexity = 'difficult'
            else:
                complexity = 'very_difficult'

            scores['reading_level'] = reading_level
            scores['complexity'] = complexity
            scores['method'] = 'textstat'

            return scores

        except Exception as e:
            logger.error(f"Error calculating readability with textstat: {e}")
            return _calculate_readability_manual(text)
    else:
        return _calculate_readability_manual(text)


def _calculate_readability_manual(text: str) -> Dict[str, Any]:
    """
    Manual calculation of basic readability metrics.

    Fallback when textstat is not available.
    """
    # Count basic statistics
    sentences = re.split(r'[.!?]+', text.strip())
    sentences = [s for s in sentences if s.strip()]
    sentence_count = len(sentences)

    words = re.findall(r'\b[a-zA-Z]+\b', text)
    word_count = len(words)

    # Simple syllable count (rough estimate)
    syllable_count = sum(_count_syllables(word) for word in words)

    # Calculate Flesch-Kincaid Grade Level (manual)
    if sentence_count > 0 and word_count > 0:
        avg_words_per_sentence = word_count / sentence_count
        avg_syllables_per_word = syllable_count / word_count

        # Flesch-Kincaid Grade = 0.39 * (words/sentences) + 11.8 * (syllables/words) - 15.59
        fk_grade = 0.39 * avg_words_per_sentence + 11.8 * avg_syllables_per_word - 15.59
        fk_grade = max(0, fk_grade)

        # Flesch Reading Ease = 206.835 - 1.015 * (words/sentences) - 84.6 * (syllables/words)
        fre = 206.835 - 1.015 * avg_words_per_sentence - 84.6 * avg_syllables_per_word
        fre = max(0, min(100, fre))
    else:
        fk_grade = 0
        fre = 50

    # Determine reading level
    if fk_grade < 6:
        reading_level = 'elementary'
    elif fk_grade < 9:
        reading_level = 'middle_school'
    elif fk_grade < 13:
        reading_level = 'high_school'
    else:
        reading_level = 'college'

    # Determine complexity
    if fre >= 60:
        complexity = 'easy'
    elif fre >= 50:
        complexity = 'medium'
    else:
        complexity = 'difficult'

    return {
        'flesch_reading_ease': round(fre, 2),
        'flesch_kincaid_grade': round(fk_grade, 2),
        'word_count': word_count,
        'sentence_count': sentence_count,
        'syllable_count': syllable_count,
        'avg_words_per_sentence': round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
        'avg_syllables_per_word': round(syllable_count / word_count, 2) if word_count > 0 else 0,
        'reading_level': reading_level,
        'complexity': complexity,
        'method': 'manual'
    }


def _count_syllables(word: str) -> int:
    """
    Rough syllable count for a word.

    Simple rule-based approach.
    """
    word = word.lower()
    vowels = 'aeiouy'
    syllable_count = 0
    previous_was_vowel = False

    for char in word:
        is_vowel = char in vowels
        if is_vowel and not previous_was_vowel:
            syllable_count += 1
        previous_was_vowel = is_vowel

    # Adjust for silent 'e'
    if word.endswith('e'):
        syllable_count -= 1

    # At least one syllable
    return max(1, syllable_count)


def calculate_medical_terminology_density(text: str) -> Dict[str, Any]:
    """
    Calculate the density of medical terminology in text.

    Higher density = more specialized medical language.
    """
    # Common medical terms and prefixes
    medical_terms = [
        'pregnancy', 'prenatal', 'trimester', 'gestational', 'fetal',
        'ultrasound', 'cervical', 'placenta', 'amniotic', 'contractions',
        'preeclampsia', 'hypertension', 'diabetes', 'medication', 'diagnosis',
        'symptoms', 'treatment', 'procedure', 'examination', 'monitor'
    ]

    medical_prefixes = ['pre', 'post', 'hyper', 'hypo', 'anti', 'neo', 'endo', 'epi']
    medical_suffixes = ['itis', 'osis', 'ectomy', 'otomy', 'gram', 'scopy', 'plasty']

    text_lower = text.lower()
    words = re.findall(r'\b[a-z]+\b', text_lower)

    # Count medical terms
    exact_medical_count = sum(1 for term in medical_terms if term in text_lower)

    # Count words with medical affixes
    affix_count = sum(1 for word in words
                     if any(word.startswith(prefix) for prefix in medical_prefixes)
                     or any(word.endswith(suffix) for suffix in medical_suffixes))

    # Count technical words (3+ syllables, uncommon)
    technical_words = [word for word in words if _count_syllables(word) >= 3]

    total_words = len(words)
    medical_density = (exact_medical_count + affix_count) / total_words if total_words > 0 else 0

    if medical_density >= 0.15:
        terminology_level = 'very_high'
    elif medical_density >= 0.10:
        terminology_level = 'high'
    elif medical_density >= 0.05:
        terminology_level = 'moderate'
    else:
        terminology_level = 'low'

    return {
        'medical_terms_count': exact_medical_count,
        'medical_affix_count': affix_count,
        'technical_words_count': len(technical_words),
        'total_words': total_words,
        'medical_density': round(medical_density, 3),
        'terminology_level': terminology_level
    }


def analyze_health_literacy_match(interviewer_text: str, persona_text: str) -> Dict[str, Any]:
    """
    Analyze the match between interviewer and persona communication complexity.

    Good health communication should match the patient's literacy level.

    Args:
        interviewer_text: Text spoken by interviewer/doctor
        persona_text: Text spoken by persona/patient

    Returns:
        Dictionary with literacy matching analysis
    """
    # Calculate readability for both
    interviewer_scores = calculate_readability_scores(interviewer_text)
    persona_scores = calculate_readability_scores(persona_text)

    # Calculate medical terminology density
    interviewer_medical = calculate_medical_terminology_density(interviewer_text)
    persona_medical = calculate_medical_terminology_density(persona_text)

    # Compare complexity levels
    if 'flesch_kincaid_grade' in interviewer_scores and 'flesch_kincaid_grade' in persona_scores:
        interviewer_grade = interviewer_scores['flesch_kincaid_grade']
        persona_grade = persona_scores['flesch_kincaid_grade']

        grade_difference = abs(interviewer_grade - persona_grade)

        if grade_difference <= 2:
            match_quality = 'excellent'
        elif grade_difference <= 4:
            match_quality = 'good'
        elif grade_difference <= 6:
            match_quality = 'fair'
        else:
            match_quality = 'poor'

        # Assess if interviewer is too complex
        if interviewer_grade > persona_grade + 3:
            recommendation = 'Interviewer should simplify language'
        elif interviewer_grade < persona_grade - 3:
            recommendation = 'Interviewer could use more technical terms'
        else:
            recommendation = 'Communication complexity is well-matched'

    else:
        match_quality = 'unable_to_assess'
        grade_difference = None
        recommendation = 'Insufficient text for analysis'

    return {
        'interviewer_readability': interviewer_scores,
        'persona_readability': persona_scores,
        'interviewer_medical_density': interviewer_medical,
        'persona_medical_density': persona_medical,
        'grade_level_difference': grade_difference,
        'match_quality': match_quality,
        'recommendation': recommendation
    }


def analyze_interview_readability(interview_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Comprehensive readability analysis of an interview.

    Args:
        interview_data: Interview dictionary with 'transcript' field

    Returns:
        Dictionary with readability analysis
    """
    transcript = interview_data.get('transcript', [])

    # Separate speaker texts
    interviewer_texts = []
    persona_texts = []

    for turn in transcript:
        text = turn.get('text', '')
        speaker = turn.get('speaker', 'unknown').lower()

        if 'interviewer' in speaker or 'doctor' in speaker or 'clinician' in speaker:
            interviewer_texts.append(text)
        elif 'persona' in speaker or 'participant' in speaker or 'patient' in speaker:
            persona_texts.append(text)

    # Combine texts
    interviewer_full = ' '.join(interviewer_texts)
    persona_full = ' '.join(persona_texts)
    overall_text = interviewer_full + ' ' + persona_full

    # Calculate scores
    overall_readability = calculate_readability_scores(overall_text)
    interviewer_readability = calculate_readability_scores(interviewer_full) if interviewer_full else None
    persona_readability = calculate_readability_scores(persona_full) if persona_full else None

    # Health literacy matching
    literacy_match = None
    if interviewer_full and persona_full:
        literacy_match = analyze_health_literacy_match(interviewer_full, persona_full)

    return {
        'overall_readability': overall_readability,
        'interviewer_readability': interviewer_readability,
        'persona_readability': persona_readability,
        'literacy_match': literacy_match,
        'communication_assessment': _assess_communication_quality(literacy_match)
    }


def _assess_communication_quality(literacy_match: Optional[Dict]) -> str:
    """Assess overall communication quality based on literacy matching."""
    if not literacy_match:
        return 'unable_to_assess'

    match_quality = literacy_match.get('match_quality', 'unable_to_assess')

    if match_quality == 'excellent':
        return 'Communication is well-matched to patient literacy level'
    elif match_quality == 'good':
        return 'Communication is generally appropriate with minor mismatches'
    elif match_quality == 'fair':
        return 'Some communication complexity mismatch present'
    elif match_quality == 'poor':
        return 'Significant communication complexity mismatch - adjustment recommended'
    else:
        return 'Unable to assess communication quality'


def check_installation() -> Dict[str, bool]:
    """Check if required packages are installed."""
    return {
        'textstat': TEXTSTAT_AVAILABLE,
        'has_readability': True  # Works with or without textstat
    }


if __name__ == '__main__':
    # Test the module
    test_texts = {
        'simple': "The baby is doing well. You should come back next week. Everything looks good.",
        'moderate': "Your pregnancy is progressing normally. We'll schedule an ultrasound to monitor fetal development. Make sure to take your prenatal vitamins.",
        'complex': "The ultrasound revealed adequate amniotic fluid levels and appropriate fetal biometry for gestational age. We'll continue to monitor for any signs of intrauterine growth restriction."
    }

    print("Readability Analysis Module Test")
    print("=" * 50)

    # Check installation
    status = check_installation()
    print(f"textstat available: {status['textstat']}")
    print(f"Readability analysis available: {status['has_readability']}")
    print()

    for level, text in test_texts.items():
        print(f"\n{level.upper()} TEXT:")
        print(f"{text}\n")

        result = calculate_readability_scores(text)

        if 'error' not in result:
            print(f"  Flesch Reading Ease: {result.get('flesch_reading_ease', 'N/A')}")
            print(f"  Grade Level: {result.get('flesch_kincaid_grade', 'N/A')}")
            print(f"  Reading Level: {result.get('reading_level', 'N/A')}")
            print(f"  Complexity: {result.get('complexity', 'N/A')}")

            # Medical terminology
            medical = calculate_medical_terminology_density(text)
            print(f"  Medical Density: {medical['medical_density']:.1%}")
            print(f"  Terminology Level: {medical['terminology_level']}")
        else:
            print(f"  Error: {result['error']}")

    # Test literacy matching
    print("\n\nLITERACY MATCHING TEST:")
    print("-" * 50)
    doctor_text = "The ultrasound shows normal fetal development. Your blood pressure is slightly elevated, so we'll monitor that closely."
    patient_text = "Okay, that's good to hear. I've been feeling tired and a bit swollen lately."

    match = analyze_health_literacy_match(doctor_text, patient_text)
    print(f"Match Quality: {match.get('match_quality', 'N/A')}")
    print(f"Grade Difference: {match.get('grade_level_difference', 'N/A')}")
    print(f"Recommendation: {match.get('recommendation', 'N/A')}")
