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
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from collections import Counter
import argparse


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


def calculate_interview_cost(interview: Dict[str, Any], model: str = 'claude-sonnet-4-5-20250929') -> Dict[str, float]:
    """Calculate estimated cost for an interview based on token usage."""
    transcript = interview['transcript']

    # Separate input (interviewer + system) and output (persona)
    input_text = ' '.join([t['text'] for t in transcript if t['speaker'] == 'Interviewer'])
    output_text = ' '.join([t['text'] for t in transcript if t['speaker'] == 'Persona'])

    # Estimate tokens
    input_tokens = estimate_tokens(input_text)
    output_tokens = estimate_tokens(output_text)

    # Get pricing
    costs = MODEL_COSTS.get(model, {'input': 3.0, 'output': 15.0})

    # Calculate costs (per million tokens)
    input_cost = (input_tokens / 1_000_000) * costs['input']
    output_cost = (output_tokens / 1_000_000) * costs['output']
    total_cost = input_cost + output_cost

    return {
        'input_tokens': input_tokens,
        'output_tokens': output_tokens,
        'total_tokens': input_tokens + output_tokens,
        'input_cost': input_cost,
        'output_cost': output_cost,
        'total_cost': total_cost,
        'model': model
    }


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

    persona_text = ' '.join([t['text'].lower() for t in persona_turns])

    # Word counts
    total_words = sum(len(t['text'].split()) for t in transcript)
    persona_words = sum(len(t['text'].split()) for t in persona_turns)

    # Topic mentions
    topics = {
        'pregnancy': ['pregnant', 'pregnancy', 'baby', 'trimester'],
        'healthcare': ['doctor', 'appointment', 'medical', 'prenatal'],
        'symptoms': ['nausea', 'pain', 'tired', 'fatigue', 'sick'],
        'emotions': ['nervous', 'anxious', 'excited', 'worried', 'happy'],
        'support': ['husband', 'family', 'support', 'help', 'partner'],
        'financial': ['insurance', 'coverage', 'cost', 'afford', 'pay'],
    }

    topic_counts = {}
    for topic, keywords in topics.items():
        count = sum(persona_text.count(keyword) for keyword in keywords)
        topic_counts[topic] = count

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
        'total_turns': len(transcript),
        'total_words': total_words,
        'persona_words': persona_words,
        'avg_response_length': persona_words // len(persona_turns) if persona_turns else 0,
        'persona_name': name_match.group(1) if name_match else 'Unknown',
        'weeks_pregnant': weeks_match.group(1) if weeks_match else 'Unknown',
        'topic_pregnancy': topic_counts['pregnancy'],
        'topic_healthcare': topic_counts['healthcare'],
        'topic_symptoms': topic_counts['symptoms'],
        'topic_emotions': topic_counts['emotions'],
        'topic_support': topic_counts['support'],
        'topic_financial': topic_counts['financial'],
        'input_tokens': cost_info['input_tokens'],
        'output_tokens': cost_info['output_tokens'],
        'total_tokens': cost_info['total_tokens'],
        'cost_usd': cost_info['total_cost'],
        'model': cost_info['model'],
    }

    # Add clinical info
    analysis.update({
        'num_conditions': clinical_info.get('num_conditions', 0),
        'num_medications': clinical_info.get('num_medications', 0),
        'num_procedures': clinical_info.get('num_procedures', 0),
        'num_encounters': clinical_info.get('num_encounters', 0),
        'num_observations': clinical_info.get('num_observations', 0),
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
        'filename', 'timestamp', 'total_turns', 'total_words',
        'persona_words', 'avg_response_length',
        'topic_pregnancy', 'topic_healthcare', 'topic_symptoms',
        'topic_emotions', 'topic_support', 'topic_financial',
        'input_tokens', 'output_tokens', 'total_tokens', 'cost_usd', 'model',
        'num_conditions', 'num_medications', 'num_procedures', 'num_encounters', 'num_observations',
        'top_conditions', 'condition_onsets', 'pregnancy_conditions',
        'active_medications', 'medication_dates', 'encounter_types',
        'fetal_heart_rate', 'pregnancy_duration_weeks', 'blood_pressure', 'weight'
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

    # Aggregate statistics
    total_words = sum(a['total_words'] for a in analyses)
    total_turns = sum(a['total_turns'] for a in analyses)
    avg_words = total_words // len(analyses)
    avg_turns = total_turns // len(analyses)

    print(f"💬 AGGREGATE STATISTICS:")
    print(f"   Total Words: {total_words:,}")
    print(f"   Total Turns: {total_turns:,}")
    print(f"   Avg Words per Interview: {avg_words:,}")
    print(f"   Avg Turns per Interview: {avg_turns}")
    print()

    # Cost statistics
    total_cost = sum(a['cost_usd'] for a in analyses)
    avg_cost = total_cost / len(analyses)
    total_tokens = sum(a['total_tokens'] for a in analyses)

    print(f"💰 COST ANALYSIS:")
    print(f"   Total Cost: ${total_cost:.4f}")
    print(f"   Avg Cost per Interview: ${avg_cost:.4f}")
    print(f"   Total Tokens: {total_tokens:,}")
    print(f"   Avg Tokens per Interview: {total_tokens // len(analyses):,}")
    print(f"   Model: {analyses[0]['model']}")
    print()

    # Age distribution
    ages = [a['persona_age'] for a in analyses]
    print(f"👥 AGE DISTRIBUTION:")
    print(f"   Range: {min(ages)} - {max(ages)} years")
    print(f"   Average: {sum(ages) / len(ages):.1f} years")
    print()

    # Clinical statistics
    avg_conditions = sum(a['num_conditions'] for a in analyses) / len(analyses)
    avg_medications = sum(a['num_medications'] for a in analyses) / len(analyses)
    avg_encounters = sum(a['num_encounters'] for a in analyses) / len(analyses)
    avg_observations = sum(a['num_observations'] for a in analyses) / len(analyses)

    print(f"🏥 CLINICAL SUMMARY:")
    print(f"   Avg Conditions per Person: {avg_conditions:.1f}")
    print(f"   Avg Medications per Person: {avg_medications:.1f}")
    print(f"   Avg Healthcare Encounters: {avg_encounters:.1f}")
    print(f"   Avg Clinical Observations: {avg_observations:.1f}")
    print()

    # Topic coverage
    print(f"🏷️  TOPIC COVERAGE (Average Mentions):")
    topics = ['pregnancy', 'healthcare', 'symptoms', 'emotions', 'support', 'financial']
    for topic in topics:
        avg = sum(a[f'topic_{topic}'] for a in analyses) / len(analyses)
        print(f"   {topic.capitalize():15} {avg:.1f}")
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
        print(f"  Words: {a['persona_words']:,} | Turns: {a['total_turns']}")
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


def main():
    parser = argparse.ArgumentParser(description="Analyze interview data with cost tracking and clinical information")
    parser.add_argument('--export-csv', action='store_true',
                        help='Export analysis to CSV file')
    parser.add_argument('--show-details', action='store_true',
                        help='Show detailed list of all interviews')
    parser.add_argument('--show-clinical', action='store_true',
                        help='Show clinical information for each interview')
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

    # Print summary
    print_summary(analyses)

    # Show details if requested
    if args.show_details:
        print_detailed_list(analyses)

    # Show clinical info if requested
    if args.show_clinical:
        print_clinical_details(analyses)

    # Export to CSV if requested
    if args.export_csv:
        export_to_csv(analyses)


if __name__ == "__main__":
    main()
