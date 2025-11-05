#!/usr/bin/env python3
"""
Export interview transcripts to CSV format for analysis.

This utility converts JSON interview files to CSV format with options for:
- Flattened persona and metadata
- Turn-by-turn transcript export
- Statistical summaries

Usage:
    python scripts/utils/export_interviews.py \
        --input data/interviews/ \
        --output data/interviews_export.csv
"""

import json
import csv
import argparse
import glob
from pathlib import Path
from typing import List, Dict, Any
import sys


def load_interviews(input_dir: str) -> List[Dict[str, Any]]:
    """Load all interview JSON files from directory."""
    print(f"Loading interviews from {input_dir}")

    pattern = str(Path(input_dir) / "interview_*.json")
    interview_files = glob.glob(pattern)

    print(f"Found {len(interview_files)} interview files")

    interviews = []
    for filepath in sorted(interview_files):
        try:
            with open(filepath, 'r') as f:
                interview = json.load(f)
                interview['_source_file'] = Path(filepath).name
                interviews.append(interview)
        except Exception as e:
            print(f"Warning: Failed to load {filepath}: {e}")

    return interviews


def export_summary_csv(interviews: List[Dict[str, Any]], output_file: str):
    """
    Export interview summaries to CSV (one row per interview).

    Columns: interview_id, persona_age, education, occupation, marital_status,
             protocol, timestamp, total_turns, avg_response_length
    """
    print(f"Exporting summary to {output_file}")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'interview_id',
            'source_file',
            'persona_id',
            'persona_age',
            'education',
            'occupation',
            'marital_status',
            'protocol',
            'timestamp',
            'total_turns',
            'questions_asked',
            'avg_response_length'
        ])

        # Data rows
        for i, interview in enumerate(interviews):
            metadata = interview.get('metadata', {})
            persona_summary = metadata.get('persona_summary', {})
            transcript = interview.get('transcript', [])

            # Calculate average response length
            persona_responses = [
                turn['text'] for turn in transcript
                if turn.get('speaker') == 'Persona'
            ]
            avg_response_length = (
                sum(len(r) for r in persona_responses) / len(persona_responses)
                if persona_responses else 0
            )

            writer.writerow([
                i + 1,
                interview.get('_source_file', ''),
                interview.get('persona_id', ''),
                interview.get('persona_age', ''),
                persona_summary.get('education', ''),
                persona_summary.get('occupation', ''),
                persona_summary.get('marital_status', ''),
                interview.get('protocol', ''),
                interview.get('timestamp', ''),
                metadata.get('total_turns', 0),
                metadata.get('questions_asked', 0),
                round(avg_response_length, 2)
            ])

    print(f"Exported {len(interviews)} interview summaries")


def export_transcript_csv(interviews: List[Dict[str, Any]], output_file: str):
    """
    Export full transcripts to CSV (one row per turn).

    Columns: interview_id, turn_number, speaker, text, timestamp
    """
    print(f"Exporting full transcripts to {output_file}")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'interview_id',
            'source_file',
            'turn_number',
            'speaker',
            'text',
            'timestamp',
            'character_count'
        ])

        # Data rows
        for i, interview in enumerate(interviews):
            transcript = interview.get('transcript', [])
            source_file = interview.get('_source_file', '')

            for turn_num, turn in enumerate(transcript):
                writer.writerow([
                    i + 1,
                    source_file,
                    turn_num + 1,
                    turn.get('speaker', ''),
                    turn.get('text', ''),
                    turn.get('timestamp', ''),
                    len(turn.get('text', ''))
                ])

    print(f"Exported {sum(len(i.get('transcript', [])) for i in interviews)} transcript turns")


def export_persona_responses_csv(interviews: List[Dict[str, Any]], output_file: str):
    """
    Export only persona responses to CSV for text analysis.

    Columns: interview_id, question_number, question, response
    """
    print(f"Exporting persona responses to {output_file}")

    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)

        # Header
        writer.writerow([
            'interview_id',
            'source_file',
            'persona_age',
            'education',
            'turn_number',
            'question',
            'response',
            'response_length'
        ])

        # Data rows
        for i, interview in enumerate(interviews):
            transcript = interview.get('transcript', [])
            source_file = interview.get('_source_file', '')
            persona_summary = interview.get('metadata', {}).get('persona_summary', {})

            # Extract Q&A pairs
            current_question = ""
            for turn in transcript:
                if turn.get('speaker') == 'Interviewer':
                    current_question = turn.get('text', '')
                elif turn.get('speaker') == 'Persona' and current_question:
                    response = turn.get('text', '')
                    writer.writerow([
                        i + 1,
                        source_file,
                        interview.get('persona_age', ''),
                        persona_summary.get('education', ''),
                        turn.get('turn_number', ''),
                        current_question,
                        response,
                        len(response)
                    ])
                    current_question = ""  # Reset

    print(f"Exported persona responses")


def main():
    parser = argparse.ArgumentParser(description='Export interview transcripts to CSV')
    parser.add_argument('--input', type=str, required=True, help='Input directory with interview JSON files')
    parser.add_argument('--output', type=str, help='Output CSV file (for summary export)')
    parser.add_argument('--format', type=str, default='summary',
                       choices=['summary', 'transcript', 'responses', 'all'],
                       help='Export format')
    args = parser.parse_args()

    # Load interviews
    interviews = load_interviews(args.input)

    if not interviews:
        print("No interviews found!")
        sys.exit(1)

    # Determine output files
    if args.output:
        base_output = Path(args.output).stem
        output_dir = Path(args.output).parent
    else:
        base_output = "interviews_export"
        output_dir = Path(args.input)

    # Export based on format
    if args.format == 'summary' or args.format == 'all':
        output_file = output_dir / f"{base_output}_summary.csv"
        export_summary_csv(interviews, str(output_file))

    if args.format == 'transcript' or args.format == 'all':
        output_file = output_dir / f"{base_output}_transcript.csv"
        export_transcript_csv(interviews, str(output_file))

    if args.format == 'responses' or args.format == 'all':
        output_file = output_dir / f"{base_output}_responses.csv"
        export_persona_responses_csv(interviews, str(output_file))

    print("\nExport complete!")


if __name__ == '__main__':
    main()
