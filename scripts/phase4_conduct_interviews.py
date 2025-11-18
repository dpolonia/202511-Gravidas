#!/usr/bin/env python3
"""
Phase 4 Interview Conductor with Real-Time Cost Monitoring

Enhanced interview conductor with:
- Real-time cost tracking
- RED alerts every €5 spent per model
- Budget monitoring and approval workflow
- Cost breakdown per interview

Usage:
    python scripts/phase4_conduct_interviews.py \
        --provider anthropic \
        --model claude-haiku-4-5 \
        --protocol Script/interview_protocols/prenatal_care.json \
        --count 16
"""

import json
import logging
import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime as dt

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import utilities
from utils.common_loaders import load_config
from utils.cost_monitor import CostMonitor, Colors, get_monitor
from utils.budget_tracker import BudgetTracker
from enhanced_models_database import get_model_info, calculate_cost
from universal_ai_client import AIClientFactory

# Setup logging
Path('logs').mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/phase4_conduct_interviews.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


def load_matched_personas(matched_file: str = 'outputs/matched_personas.json') -> List[Dict[str, Any]]:
    """Load matched persona-record pairs."""
    logger.info(f"Loading matched personas from {matched_file}")
    try:
        with open(matched_file, 'r') as f:
            matched = json.load(f)
        logger.info(f"Loaded {len(matched)} matched pairs")
        return matched
    except FileNotFoundError:
        logger.error(f"Matched personas file not found: {matched_file}")
        sys.exit(1)


def list_available_protocols(protocol_dir: str = 'Script/interview_protocols') -> List[Dict[str, Any]]:
    """
    List all available interview protocols.

    Returns:
        List of protocol metadata dictionaries
    """
    protocols = []
    protocol_path = Path(protocol_dir)

    if not protocol_path.exists():
        logger.warning(f"Protocol directory not found: {protocol_dir}")
        return protocols

    for protocol_file in protocol_path.glob('*.json'):
        try:
            with open(protocol_file, 'r') as f:
                protocol = json.load(f)
                protocols.append({
                    'file': str(protocol_file),
                    'name': protocol.get('name', 'Unknown'),
                    'category': protocol.get('category', 'unknown'),
                    'version': protocol.get('version', '1.0'),
                    'description': protocol.get('description', ''),
                    'duration_min': protocol.get('estimated_duration_minutes', 0),
                    'num_questions': len(protocol.get('questions', []))
                })
        except Exception as e:
            logger.warning(f"Could not load protocol {protocol_file}: {e}")

    return sorted(protocols, key=lambda x: x['name'])


def display_available_protocols():
    """Display formatted list of available protocols."""
    protocols = list_available_protocols()

    if not protocols:
        print(f"{Colors.YELLOW}No interview protocols found.{Colors.RESET}")
        return

    print(f"\n{Colors.CYAN}{'='*80}{Colors.RESET}")
    print(f"{Colors.CYAN}{Colors.BOLD}  Available Interview Protocols{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")

    for i, protocol in enumerate(protocols, 1):
        print(f"{Colors.BOLD}{i}. {protocol['name']}{Colors.RESET} (v{protocol['version']})")
        print(f"   {Colors.WHITE}File:{Colors.RESET} {protocol['file']}")
        print(f"   {Colors.WHITE}Category:{Colors.RESET} {protocol['category']}")
        print(f"   {Colors.WHITE}Duration:{Colors.RESET} ~{protocol['duration_min']} minutes")
        print(f"   {Colors.WHITE}Questions:{Colors.RESET} {protocol['num_questions']}")
        print(f"   {Colors.WHITE}Description:{Colors.RESET} {protocol['description'][:80]}...")
        print()

    print(f"{Colors.CYAN}{'='*80}{Colors.RESET}\n")


def load_interview_protocol(protocol_file: str) -> Dict[str, Any]:
    """Load interview protocol."""
    logger.info(f"Loading interview protocol from {protocol_file}")
    try:
        with open(protocol_file, 'r') as f:
            protocol = json.load(f)
        logger.info(f"Loaded protocol: {protocol.get('name', 'Unknown')}")
        return protocol
    except FileNotFoundError:
        logger.error(f"Protocol file not found: {protocol_file}")
        print(f"\n{Colors.RED}Error: Protocol file not found: {protocol_file}{Colors.RESET}")
        print(f"{Colors.YELLOW}Use --list-protocols to see available protocols.{Colors.RESET}\n")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in protocol file: {e}")
        print(f"\n{Colors.RED}Error: Invalid JSON in protocol file: {protocol_file}{Colors.RESET}\n")
        sys.exit(1)


def build_system_prompt(persona: Dict[str, Any], health_record: Dict[str, Any], protocol: Dict[str, Any]) -> str:
    """Build system prompt with persona and health record context."""

    persona_desc = persona.get('description', '')
    name = persona.get('name', 'the participant')
    age = persona.get('age', 'unknown')
    education = persona.get('education', 'unknown')
    occupation = persona.get('occupation', 'unknown')
    marital_status = persona.get('marital_status', 'unknown')

    # Summarize health record
    conditions = health_record.get('conditions', [])
    conditions_str = ', '.join([c.get('display', 'Unknown') for c in conditions[:5]])

    system_prompt = f"""You are conducting a medical research interview with a synthetic persona named {name}. Your goal is to gather detailed information following the interview protocol.

PERSONA BACKGROUND:
- Name: {name}
- Age: {age}
- Education: {education}
- Occupation: {occupation}
- Marital Status: {marital_status}
- Description: {persona_desc}

HEALTH RECORD SUMMARY:
- Medical Conditions: {conditions_str}
- Number of encounters: {len(health_record.get('encounters', []))}
- Has pregnancy-related conditions: Yes

INTERVIEW PROTOCOL:
{protocol.get('description', '')}

INSTRUCTIONS:
1. Stay in character as an empathetic medical researcher
2. Follow the interview questions in order
3. Ask follow-up questions when appropriate
4. Be respectful and professional
5. Gather detailed information while being sensitive
6. The persona should respond naturally based on their background and health history

Remember: This is a synthetic persona for research purposes. Conduct the interview as if speaking with a real patient.
"""

    return system_prompt


def conduct_interview_with_cost_tracking(
    ai_client,
    persona: Dict[str, Any],
    health_record: Dict[str, Any],
    protocol: Dict[str, Any],
    model_name: str,
    cost_monitor: CostMonitor,
    max_turns: int = 20
) -> Optional[Dict[str, Any]]:
    """
    Conduct a single interview with real-time cost tracking.

    Returns:
        Interview transcript and metadata including cost breakdown
    """
    # Build system prompt
    system_prompt = build_system_prompt(persona, health_record, protocol)

    # Initialize cost tracking for this interview
    interview_start_time = dt.now()
    cost_breakdown = {
        'turns': [],
        'total_input_tokens': 0,
        'total_output_tokens': 0,
        'total_cost_usd': 0.0,
        'total_cost_eur': 0.0
    }

    transcript = []
    questions = protocol.get('questions', [])

    logger.info(f"Starting interview with {len(questions)} protocol questions")
    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.BOLD}Interview Start:{Colors.RESET} {interview_start_time.strftime('%H:%M:%S')}")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}\n")

    # Introduction
    intro_message = "Hello, thank you for participating in this interview. I'm going to ask you some questions about your health and experiences. Let's begin."

    transcript.append({'speaker': 'Interviewer', 'text': intro_message, 'timestamp': dt.now().isoformat()})

    # Get initial response
    try:
        conversation_prompt = system_prompt + "\n\n" + intro_message

        ai_response = ai_client.generate(conversation_prompt)
        response_text = ai_response.content

        # Track cost
        turn_cost_usd = ai_response.cost_usd
        turn_cost_eur = turn_cost_usd * cost_monitor.USD_TO_EUR

        cost_breakdown['turns'].append({
            'turn': 0,
            'input_tokens': ai_response.usage['input_tokens'],
            'output_tokens': ai_response.usage['output_tokens'],
            'cost_usd': turn_cost_usd,
            'cost_eur': turn_cost_eur
        })

        cost_breakdown['total_input_tokens'] += ai_response.usage['input_tokens']
        cost_breakdown['total_output_tokens'] += ai_response.usage['output_tokens']
        cost_breakdown['total_cost_usd'] += turn_cost_usd
        cost_breakdown['total_cost_eur'] += turn_cost_eur

        # Add to cost monitor (triggers alerts if threshold crossed)
        cost_monitor.add_cost(model_name, turn_cost_usd, {
            'turn': 0,
            'interview_id': persona.get('persona_id', 'unknown'),
            'input_tokens': ai_response.usage['input_tokens'],
            'output_tokens': ai_response.usage['output_tokens']
        })

        # Display turn cost
        print(f"{Colors.WHITE}Turn 0 (Intro):{Colors.RESET} €{turn_cost_eur:.4f} | {Colors.YELLOW}Cumulative: €{cost_breakdown['total_cost_eur']:.4f}{Colors.RESET}")

        transcript.append({'speaker': 'Persona', 'text': response_text, 'timestamp': dt.now().isoformat()})

    except Exception as e:
        logger.error(f"Failed to get initial response: {e}")
        return None

    # Ask protocol questions
    for i, question in enumerate(questions[:max_turns]):
        question_text = question.get('text', '')

        transcript.append({'speaker': 'Interviewer', 'text': question_text, 'timestamp': dt.now().isoformat()})

        try:
            # Build conversation context
            conversation_context = system_prompt + "\n\nConversation so far:\n"
            for turn in transcript:
                conversation_context += f"{turn['speaker']}: {turn['text']}\n"
            conversation_context += "Persona:"

            ai_response = ai_client.generate(conversation_context)
            response_text = ai_response.content

            # Track cost
            turn_cost_usd = ai_response.cost_usd
            turn_cost_eur = turn_cost_usd * cost_monitor.USD_TO_EUR

            cost_breakdown['turns'].append({
                'turn': i + 1,
                'input_tokens': ai_response.usage['input_tokens'],
                'output_tokens': ai_response.usage['output_tokens'],
                'cost_usd': turn_cost_usd,
                'cost_eur': turn_cost_eur
            })

            cost_breakdown['total_input_tokens'] += ai_response.usage['input_tokens']
            cost_breakdown['total_output_tokens'] += ai_response.usage['output_tokens']
            cost_breakdown['total_cost_usd'] += turn_cost_usd
            cost_breakdown['total_cost_eur'] += turn_cost_eur

            # Add to cost monitor
            cost_monitor.add_cost(model_name, turn_cost_usd, {
                'turn': i + 1,
                'interview_id': persona.get('persona_id', 'unknown'),
                'input_tokens': ai_response.usage['input_tokens'],
                'output_tokens': ai_response.usage['output_tokens']
            })

            # Display turn cost
            print(f"{Colors.WHITE}Turn {i+1}/{len(questions)}:{Colors.RESET} €{turn_cost_eur:.4f} | {Colors.YELLOW}Cumulative: €{cost_breakdown['total_cost_eur']:.4f}{Colors.RESET}")

            transcript.append({'speaker': 'Persona', 'text': response_text, 'timestamp': dt.now().isoformat()})

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Failed to get response for question {i+1}: {e}")
            break

    # Conclusion
    outro_message = "Thank you for your time and for sharing your experiences with me. This concludes our interview."
    transcript.append({'speaker': 'Interviewer', 'text': outro_message, 'timestamp': dt.now().isoformat()})

    interview_end_time = dt.now()
    duration = (interview_end_time - interview_start_time).total_seconds()

    # Display interview summary
    print(f"\n{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}")
    print(f"{Colors.BOLD}Interview Complete{Colors.RESET}")
    print(f"{Colors.WHITE}Duration:{Colors.RESET} {duration:.1f}s")
    print(f"{Colors.WHITE}Total Turns:{Colors.RESET} {len(cost_breakdown['turns'])}")
    print(f"{Colors.WHITE}Total Tokens:{Colors.RESET} {cost_breakdown['total_input_tokens'] + cost_breakdown['total_output_tokens']:,}")
    print(f"{Colors.GREEN}{Colors.BOLD}Total Cost:{Colors.RESET} ${cost_breakdown['total_cost_usd']:.4f} USD / €{cost_breakdown['total_cost_eur']:.4f} EUR")
    print(f"{Colors.CYAN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.RESET}\n")

    # Return interview data with cost breakdown
    return {
        'interview_id': persona.get('persona_id', 'unknown'),
        'persona_id': persona.get('persona_id'),
        'transcript': transcript,
        'cost_breakdown': cost_breakdown,
        'metadata': {
            'model': model_name,
            'protocol': protocol.get('name', 'unknown'),
            'start_time': interview_start_time.isoformat(),
            'end_time': interview_end_time.isoformat(),
            'duration_seconds': duration
        }
    }


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Conduct interviews with cost monitoring (Phase 4)')
    parser.add_argument('--provider', type=str,
                       help='AI provider (anthropic, openai, google, xai)')
    parser.add_argument('--model', type=str,
                       help='Model name')
    parser.add_argument('--protocol', type=str,
                       help='Interview protocol file path')
    parser.add_argument('--count', type=int, default=10,
                       help='Number of interviews to conduct')
    parser.add_argument('--matched-file', type=str, default='outputs/matched_personas.json',
                       help='Matched personas file')
    parser.add_argument('--output-dir', type=str, default='outputs/phase4_interviews',
                       help='Output directory for interviews')
    parser.add_argument('--list-protocols', action='store_true',
                       help='List all available interview protocols and exit')

    args = parser.parse_args()

    # Handle --list-protocols
    if args.list_protocols:
        display_available_protocols()
        sys.exit(0)

    # Validate required args (not needed if listing protocols)
    if not args.provider or not args.model or not args.protocol:
        parser.error('--provider, --model, and --protocol are required (unless using --list-protocols)')

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Load matched personas and protocol
    matched_personas = load_matched_personas(args.matched_file)
    protocol = load_interview_protocol(args.protocol)

    # Limit to requested count
    if args.count < len(matched_personas):
        matched_personas = matched_personas[:args.count]

    # Create AI client
    logger.info(f"Creating AI client: {args.provider} / {args.model}")
    try:
        ai_client = AIClientFactory.create_client(args.provider, args.model)
    except Exception as e:
        logger.error(f"Failed to create AI client: {e}")
        sys.exit(1)

    # Initialize cost monitor
    cost_monitor = get_monitor()

    logger.info(f"Starting Phase 4 interview batch: {args.count} interviews")
    print(f"\n{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}  Phase 4 Interview Batch{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.WHITE}Provider:{Colors.RESET} {args.provider}")
    print(f"{Colors.WHITE}Model:{Colors.RESET} {args.model}")
    print(f"{Colors.WHITE}Protocol:{Colors.RESET} {protocol.get('name', 'Unknown')}")
    print(f"{Colors.WHITE}Interviews:{Colors.RESET} {args.count}")
    print(f"{Colors.BOLD}{Colors.GREEN}═══════════════════════════════════════════════════════════════{Colors.RESET}\n")

    # Conduct interviews
    interviews = []
    successful = 0
    failed = 0

    for i, matched in enumerate(matched_personas):
        persona = matched.get('persona', {})
        health_record = matched.get('health_record', {})

        logger.info(f"Conducting interview {i+1}/{args.count}")
        print(f"\n{Colors.BOLD}{Colors.BLUE}━━━ Interview {i+1}/{args.count} ━━━{Colors.RESET}")

        try:
            interview = conduct_interview_with_cost_tracking(
                ai_client=ai_client,
                persona=persona,
                health_record=health_record,
                protocol=protocol,
                model_name=args.model,
                cost_monitor=cost_monitor,
                max_turns=len(protocol.get('questions', []))
            )

            if interview:
                interviews.append(interview)
                successful += 1

                # Save individual interview
                interview_file = Path(args.output_dir) / f"interview_{i+1:03d}.json"
                with open(interview_file, 'w') as f:
                    json.dump(interview, f, indent=2)

            else:
                failed += 1

        except Exception as e:
            logger.error(f"Interview {i+1} failed: {e}")
            failed += 1

    # Final summary
    print(f"\n{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}  Batch Complete{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}═══════════════════════════════════════════════════════════════{Colors.RESET}")
    print(f"{Colors.GREEN}✅ Successful:{Colors.RESET} {successful}/{args.count}")
    print(f"{Colors.RED}❌ Failed:{Colors.RESET} {failed}/{args.count}")
    print()

    # Display cost status
    cost_monitor.display_status()

    # Save batch summary
    summary = {
        'timestamp': dt.now().isoformat(),
        'provider': args.provider,
        'model': args.model,
        'protocol': protocol.get('name', 'Unknown'),
        'interviews_planned': args.count,
        'interviews_successful': successful,
        'interviews_failed': failed,
        'total_cost_usd': cost_monitor.get_model_cost(args.model, in_eur=False),
        'total_cost_eur': cost_monitor.get_model_cost(args.model, in_eur=True),
        'interviews': [{'interview_id': i['interview_id'], 'cost_eur': i['cost_breakdown']['total_cost_eur']} for i in interviews]
    }

    summary_file = Path(args.output_dir) / 'batch_summary.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    logger.info(f"Batch summary saved to {summary_file}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
