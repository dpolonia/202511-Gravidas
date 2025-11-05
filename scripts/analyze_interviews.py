#!/usr/bin/env python3
"""
Analyze interview data and export summaries.

This script:
1. Loads all interview JSON files
2. Extracts key themes and topics
3. Generates CSV summaries for analysis
4. Creates statistical reports

Usage:
    python scripts/analyze_interviews.py
    python scripts/analyze_interviews.py --export-csv
    python scripts/analyze_interviews.py --show-details
"""

import json
import csv
import re
from pathlib import Path
from typing import List, Dict, Any
from collections import Counter
import argparse


def load_interviews(interview_dir: str = "data/interviews") -> List[Dict[str, Any]]:
    """Load all interview JSON files."""
    interview_path = Path(interview_dir)
    interviews = []

    for file in sorted(interview_path.glob("interview_*.json")):
        with open(file, 'r') as f:
            data = json.load(f)
            data['filename'] = file.name
            interviews.append(data)

    return interviews


def analyze_interview(interview: Dict[str, Any]) -> Dict[str, Any]:
    """Extract key metrics from a single interview."""
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

    return {
        'persona_id': interview['persona_id'],
        'persona_age': interview['persona_age'],
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
    }


def export_to_csv(analyses: List[Dict[str, Any]], output_file: str = "data/analysis/interview_summary.csv"):
    """Export analysis results to CSV."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fieldnames = [
        'persona_id', 'persona_age', 'persona_name', 'weeks_pregnant',
        'filename', 'timestamp', 'total_turns', 'total_words',
        'persona_words', 'avg_response_length',
        'topic_pregnancy', 'topic_healthcare', 'topic_symptoms',
        'topic_emotions', 'topic_support', 'topic_financial'
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

    # Age distribution
    ages = [a['persona_age'] for a in analyses]
    print(f"👥 AGE DISTRIBUTION:")
    print(f"   Range: {min(ages)} - {max(ages)} years")
    print(f"   Average: {sum(ages) / len(ages):.1f} years")
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
        print(f"  Words: {a['persona_words']:,} | Turns: {a['total_turns']}")
        print(f"  File: {a['filename']}")
        print()


def main():
    parser = argparse.ArgumentParser(description="Analyze interview data")
    parser.add_argument('--export-csv', action='store_true',
                        help='Export analysis to CSV file')
    parser.add_argument('--show-details', action='store_true',
                        help='Show detailed list of all interviews')
    args = parser.parse_args()

    # Load and analyze interviews
    print("Loading interviews...")
    interviews = load_interviews()

    if not interviews:
        print("❌ No interviews found in data/interviews/")
        print("   Run an interview first with: python scripts/04_conduct_interviews.py")
        return

    print(f"✅ Loaded {len(interviews)} interview(s)")
    print()

    # Analyze all interviews
    analyses = [analyze_interview(interview) for interview in interviews]

    # Print summary
    print_summary(analyses)

    # Show details if requested
    if args.show_details:
        print_detailed_list(analyses)

    # Export to CSV if requested
    if args.export_csv:
        export_to_csv(analyses)


if __name__ == "__main__":
    main()
