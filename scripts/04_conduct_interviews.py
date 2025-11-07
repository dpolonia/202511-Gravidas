#!/usr/bin/env python3
"""
Conduct AI-powered interviews with synthetic personas using their health records.

This script:
1. Loads matched persona-record pairs
2. Loads interview protocol
3. Initializes selected AI model (Claude, OpenAI, or Gemini)
4. Conducts structured interviews following protocol
5. Saves interview transcripts

Usage:
    python scripts/04_conduct_interviews.py \
        --model claude \
        --protocol Script/interview_protocols/prenatal_care.json \
        --count 10
"""

import json
import logging
import sys
import os
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
import datetime
from datetime import datetime as dt

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # python-dotenv not installed, will use system environment variables

try:
    import yaml
    from anthropic import Anthropic
    import openai
    import google.generativeai as genai
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import common loaders and retry logic
from utils.common_loaders import load_config, get_api_key
from utils.retry_logic import RetryConfig, exponential_backoff_retry

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/04_conduct_interviews.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class AIProvider:
    """Base class for AI providers."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate AI response given conversation history."""
        raise NotImplementedError


class ClaudeProvider(AIProvider):
    """Anthropic Claude provider with retry logic."""

    def __init__(self, config: Dict[str, Any], model: str = None, retry_config: RetryConfig = None):
        super().__init__(config)
        # Load API key securely from environment variables only
        api_key = get_api_key('anthropic')
        self.client = Anthropic(api_key=api_key)
        # Use specified model or fall back to default_model or hardcoded default
        self.model = model or config.get('default_model', 'claude-4.5-sonnet')
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.7)
        self.retry_config = retry_config

        logger.info(f"Initialized Claude provider with model: {self.model}")
        if retry_config:
            logger.info(f"Retry logic enabled: {retry_config.max_retries} max retries, {retry_config.strategy} backoff")

    def _make_api_call(self, system_message: str, conversation_messages: List[Dict[str, str]]) -> str:
        """Make the actual API call (wrapped with retry if configured)."""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            system=system_message,
            messages=conversation_messages
        )
        return response.content[0].text

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Claude with retry logic."""
        try:
            # Separate system message from conversation
            system_message = ""
            conversation_messages = []

            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                else:
                    conversation_messages.append({
                        'role': msg['role'],
                        'content': msg['content']
                    })

            # Apply retry decorator if retry_config is provided
            if self.retry_config:
                # Create decorator and apply it
                retry_decorator = self.retry_config.create_decorator(
                    exceptions=(Exception,)  # Retry on any API error
                )
                api_call = retry_decorator(self._make_api_call)
            else:
                api_call = self._make_api_call

            return api_call(system_message, conversation_messages)

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise


class OpenAIProvider(AIProvider):
    """OpenAI GPT provider with retry logic."""

    def __init__(self, config: Dict[str, Any], model: str = None, retry_config: RetryConfig = None):
        super().__init__(config)
        # Load API key securely from environment variables only
        api_key = get_api_key('openai')
        openai.api_key = api_key
        self.client = openai.OpenAI(api_key=api_key)
        # Use specified model or fall back to default_model or hardcoded default
        self.model = model or config.get('default_model', 'gpt-5')
        self.max_tokens = config.get('max_tokens', 4096)
        self.temperature = config.get('temperature', 0.7)
        self.retry_config = retry_config

        logger.info(f"Initialized OpenAI provider with model: {self.model}")
        if retry_config:
            logger.info(f"Retry logic enabled: {retry_config.max_retries} max retries, {retry_config.strategy} backoff")

    def _make_api_call(self, messages: List[Dict[str, str]]) -> str:
        """Make the actual API call (wrapped with retry if configured)."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=self.max_tokens,
            temperature=self.temperature
        )
        return response.choices[0].message.content

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using OpenAI with retry logic."""
        try:
            # Apply retry decorator if retry_config is provided
            if self.retry_config:
                retry_decorator = self.retry_config.create_decorator(
                    exceptions=(Exception,)  # Retry on any API error
                )
                api_call = retry_decorator(self._make_api_call)
            else:
                api_call = self._make_api_call

            return api_call(messages)

        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise


class GeminiProvider(AIProvider):
    """Google Gemini provider with retry logic."""

    def __init__(self, config: Dict[str, Any], model: str = None, retry_config: RetryConfig = None):
        super().__init__(config)
        # Load API key securely from environment variables only
        api_key = get_api_key('google')
        genai.configure(api_key=api_key)
        # Use specified model or fall back to default_model or hardcoded default
        model_name = model or config.get('default_model', 'gemini-2.5-pro')
        self.model = genai.GenerativeModel(model_name)
        self.model_name = model_name
        self.temperature = config.get('temperature', 0.7)
        self.retry_config = retry_config

        logger.info(f"Initialized Gemini provider with model: {model_name}")
        if retry_config:
            logger.info(f"Retry logic enabled: {retry_config.max_retries} max retries, {retry_config.strategy} backoff")

    def _make_api_call(self, conversation: List[Dict[str, Any]]) -> str:
        """Make the actual API call (wrapped with retry if configured)."""
        chat = self.model.start_chat(history=conversation[:-1] if len(conversation) > 1 else [])
        response = chat.send_message(conversation[-1]['parts'][0] if conversation else "")
        return response.text

    def generate_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate response using Gemini with retry logic."""
        try:
            # Convert messages to Gemini format
            # Gemini uses a simpler format: system + alternating user/model
            conversation = []
            system_message = ""

            for msg in messages:
                if msg['role'] == 'system':
                    system_message = msg['content']
                elif msg['role'] == 'user':
                    conversation.append({'role': 'user', 'parts': [msg['content']]})
                elif msg['role'] == 'assistant':
                    conversation.append({'role': 'model', 'parts': [msg['content']]})

            # Prepend system message to first user message
            if conversation and system_message:
                conversation[0]['parts'][0] = f"{system_message}\n\n{conversation[0]['parts'][0]}"

            # Apply retry decorator if retry_config is provided
            if self.retry_config:
                retry_decorator = self.retry_config.create_decorator(
                    exceptions=(Exception,)  # Retry on any API error
                )
                api_call = retry_decorator(self._make_api_call)
            else:
                api_call = self._make_api_call

            return api_call(conversation)

        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise


def load_matched_personas(matched_file: str) -> List[Dict[str, Any]]:
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
        sys.exit(1)


def create_ai_provider(provider_name: str, config: Dict[str, Any], model: str = None, retry_config: RetryConfig = None) -> AIProvider:
    """
    Create AI provider instance with optional retry logic.

    Args:
        provider_name: Provider name (anthropic/claude, openai, google/gemini)
        config: Configuration dictionary
        model: Optional model name to use
        retry_config: Optional RetryConfig for API call retry logic

    Returns:
        AIProvider instance with retry logic configured
    """
    providers_config = config.get('api_keys', {})

    # If no model specified, try to get from config
    if not model:
        model = config.get('active_model')

    # Normalize provider names (support both old and new conventions)
    provider_map = {
        'claude': 'anthropic',
        'anthropic': 'anthropic',
        'openai': 'openai',
        'gemini': 'google',
        'google': 'google'
    }

    normalized_provider = provider_map.get(provider_name.lower())
    if not normalized_provider:
        raise ValueError(f"Unknown provider: {provider_name}. Use: anthropic, openai, or google")

    # Get provider config
    provider_config = providers_config.get(normalized_provider, {})

    # Create provider instance with retry config
    if normalized_provider == 'anthropic':
        return ClaudeProvider(provider_config, model=model, retry_config=retry_config)
    elif normalized_provider == 'openai':
        return OpenAIProvider(provider_config, model=model, retry_config=retry_config)
    elif normalized_provider == 'google':
        return GeminiProvider(provider_config, model=model, retry_config=retry_config)
    else:
        raise ValueError(f"Unknown provider: {provider_name}")


def build_system_prompt(persona: Dict[str, Any], health_record: Dict[str, Any], protocol: Dict[str, Any]) -> str:
    """Build system prompt with persona and health record context."""

    persona_desc = persona.get('description', '')
    age = persona.get('age', 'unknown')
    education = persona.get('education', 'unknown')
    occupation = persona.get('occupation', 'unknown')
    marital_status = persona.get('marital_status', 'unknown')

    # Summarize health record
    conditions = health_record.get('conditions', [])
    conditions_str = ', '.join([c.get('display', 'Unknown') for c in conditions[:5]])

    system_prompt = f"""You are conducting a medical research interview with a synthetic persona. Your goal is to gather detailed information following the interview protocol.

PERSONA BACKGROUND:
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


def conduct_interview(
    ai_provider: AIProvider,
    persona: Dict[str, Any],
    health_record: Dict[str, Any],
    protocol: Dict[str, Any],
    max_turns: int = 20
) -> Dict[str, Any]:
    """
    Conduct a single interview.

    Returns:
        Interview transcript and metadata
    """
    # Build system prompt
    system_prompt = build_system_prompt(persona, health_record, protocol)

    # Initialize conversation
    messages = [
        {'role': 'system', 'content': system_prompt}
    ]

    transcript = []
    questions = protocol.get('questions', [])

    logger.info(f"Starting interview with {len(questions)} protocol questions")

    # Introduction
    intro_message = f"Hello, thank you for participating in this interview. I'm going to ask you some questions about your health and experiences. Let's begin."

    messages.append({'role': 'user', 'content': intro_message})
    transcript.append({'speaker': 'Interviewer', 'text': intro_message, 'timestamp': dt.now().isoformat()})

    # Get initial response
    try:
        response = ai_provider.generate_response(messages)
        messages.append({'role': 'assistant', 'content': response})
        transcript.append({'speaker': 'Persona', 'text': response, 'timestamp': dt.now().isoformat()})
    except Exception as e:
        logger.error(f"Failed to get initial response: {e}")
        return None

    # Ask protocol questions
    for i, question in enumerate(questions[:max_turns]):
        question_text = question.get('text', '')

        logger.debug(f"Question {i+1}/{len(questions)}: {question_text[:50]}...")

        messages.append({'role': 'user', 'content': question_text})
        transcript.append({'speaker': 'Interviewer', 'text': question_text, 'timestamp': dt.now().isoformat()})

        try:
            response = ai_provider.generate_response(messages)
            messages.append({'role': 'assistant', 'content': response})
            transcript.append({'speaker': 'Persona', 'text': response, 'timestamp': dt.now().isoformat()})

            # Rate limiting
            time.sleep(0.5)

        except Exception as e:
            logger.error(f"Failed to get response for question {i+1}: {e}")
            break

    # Conclusion
    outro_message = "Thank you for your time and for sharing your experiences with me. This concludes our interview."
    messages.append({'role': 'user', 'content': outro_message})
    transcript.append({'speaker': 'Interviewer', 'text': outro_message, 'timestamp': dt.now().isoformat()})

    try:
        response = ai_provider.generate_response(messages)
        transcript.append({'speaker': 'Persona', 'text': response, 'timestamp': dt.now().isoformat()})
    except Exception as e:
        logger.warning(f"Failed to get conclusion response: {e}")

    # Build interview record
    persona_id = persona.get('id')
    finepersonas_profile_file = f"persona_{persona_id:05d}_profile.json" if persona_id else None

    interview = {
        'persona_id': persona_id,
        'persona_age': persona.get('age'),
        'persona_source': 'HuggingFace FinePersonas-v0.1',
        'persona_description': persona.get('description', ''),
        'persona_profile_file': finepersonas_profile_file,
        'synthea_patient_id': health_record.get('patient_id'),
        'synthea_source_file': health_record.get('source_file'),
        'protocol': protocol.get('name'),
        'timestamp': dt.now().isoformat(),
        'transcript': transcript,
        'metadata': {
            'total_turns': len(transcript),
            'questions_asked': len(questions),
            'persona_traceability': {
                'persona_id': persona_id,
                'source_dataset': 'HuggingFace FinePersonas-v0.1',
                'dataset_url': 'https://huggingface.co/datasets/argilla/FinePersonas-v0.1',
                'profile_file': finepersonas_profile_file,
                'profile_path': f"data/finepersonas_profiles/{finepersonas_profile_file}" if finepersonas_profile_file else None,
                'age': persona.get('age'),
                'gender': persona.get('gender'),
                'education': persona.get('education'),
                'occupation': persona.get('occupation'),
                'marital_status': persona.get('marital_status'),
                'income_level': persona.get('income_level'),
                'description': persona.get('description', '')
            },
            'synthea_traceability': {
                'patient_id': health_record.get('patient_id'),
                'source_file': health_record.get('source_file'),
                'source_path': f"data/health_records/{health_record.get('source_file')}" if health_record.get('source_file') else None,
                'num_conditions': len(health_record.get('conditions', [])),
                'num_encounters': len(health_record.get('encounters', []))
            }
        }
    }

    return interview


def save_interview(interview: Dict[str, Any], output_dir: str, interview_num: int):
    """Save interview transcript."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / f"interview_{interview_num:05d}.json"
    with open(output_file, 'w') as f:
        json.dump(interview, f, indent=2)

    logger.debug(f"Saved interview to {output_file}")


def main():
    parser = argparse.ArgumentParser(
        description='Conduct AI interviews with synthetic personas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Use active_provider and active_model from config.yaml
  python scripts/04_conduct_interviews.py --count 10

  # Override provider and model
  python scripts/04_conduct_interviews.py --provider anthropic --model claude-4.5-sonnet --count 10

  # Use different protocol
  python scripts/04_conduct_interviews.py --protocol Script/interview_protocols/pregnancy_experience.json
        """
    )
    parser.add_argument('--matched', type=str, default='data/matched/matched_personas.json', help='Matched personas file')
    parser.add_argument('--protocol', type=str, default='Script/interview_protocols/prenatal_care.json', help='Interview protocol file')
    parser.add_argument('--provider', type=str, help='AI provider (anthropic, openai, google). If not specified, uses active_provider from config')
    parser.add_argument('--model', type=str, help='AI model name (e.g., claude-4.5-sonnet, gpt-5, gemini-2.5-pro). If not specified, uses active_model from config')
    parser.add_argument('--output', type=str, default='data/interviews', help='Output directory')
    parser.add_argument('--count', type=int, default=10, help='Number of interviews to conduct')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')
    parser.add_argument('--start-index', type=int, default=0, help='Starting index in matched personas')
    parser.add_argument('--batch', action='store_true', help='Use batch API mode (50%% cost savings, 24hr turnaround). Creates batch request file instead of running interviews immediately.')
    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    logger.info("=== AI Interview Script Started ===")

    # Load configuration
    config = load_config(args.config)

    # Determine provider and model
    provider = args.provider or config.get('active_provider', 'anthropic')
    model = args.model or config.get('active_model')

    logger.info(f"Provider: {provider}")
    logger.info(f"Model: {model}")

    # Load retry configuration
    retry_config = RetryConfig.from_config(config)
    logger.info(f"Retry configuration: max_retries={retry_config.max_retries}, strategy={retry_config.strategy}")

    # Load matched personas
    matched_personas = load_matched_personas(args.matched)

    # Load interview protocol
    protocol = load_interview_protocol(args.protocol)

    # Validate count
    available = len(matched_personas) - args.start_index
    if args.count > available:
        logger.warning(f"Requested {args.count} interviews but only {available} personas available")
        args.count = available

    # Initialize AI provider with retry logic
    logger.info(f"Initializing AI provider: {provider} with model: {model}")
    try:
        ai_provider = create_ai_provider(provider, config, model=model, retry_config=retry_config)
        logger.info(f"AI provider initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize AI provider: {e}")
        sys.exit(1)

    # Handle batch mode
    if args.batch:
        logger.info("BATCH MODE: Creating batch request file instead of running interviews immediately")
        logger.info(f"Note: Batch API offers 50% cost savings but requires ~24 hour processing time")

        batch_requests = []
        for i in range(args.count):
            persona_idx = args.start_index + i
            matched_pair = matched_personas[persona_idx]
            persona = matched_pair['persona']
            health_record = matched_pair['health_record']

            # Create initial prompt
            system_message = build_system_prompt(persona, health_record, protocol)
            first_question = protocol['questions'][0]['text']

            batch_requests.append({
                'custom_id': f'interview_{persona_idx}',
                'persona_id': persona_idx,
                'persona': persona,
                'health_record': health_record,
                'system_message': system_message,
                'first_question': first_question
            })

        # Save batch request file
        batch_dir = Path('data/batch_requests')
        batch_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.dt.now().strftime('%Y%m%d_%H%M%S')
        batch_file = batch_dir / f'batch_request_{provider}_{timestamp}.jsonl'

        with open(batch_file, 'w') as f:
            for req in batch_requests:
                f.write(json.dumps(req) + '\n')

        logger.info(f"✓ Created batch request file: {batch_file}")
        logger.info(f"✓ {len(batch_requests)} interview requests prepared")
        logger.info(f"\nNext steps:")
        logger.info(f"  1. Submit batch file to {provider} API")
        logger.info(f"  2. Wait for processing (~24 hours)")
        logger.info(f"  3. Download results when ready")
        logger.info(f"\nSee docs/BATCH_API.md for detailed instructions")
        return

    # Conduct interviews (real-time mode)
    logger.info(f"Conducting {args.count} interviews...")

    successful_interviews = 0
    failed_interviews = 0

    for i in range(args.count):
        persona_idx = args.start_index + i
        matched_pair = matched_personas[persona_idx]

        persona = matched_pair['persona']
        health_record = matched_pair['health_record']

        persona_name = persona.get('description', '')[:50]
        logger.info(f"\n[INTERVIEW {i+1}/{args.count}] Persona: {persona_name}...")

        try:
            interview = conduct_interview(
                ai_provider,
                persona,
                health_record,
                protocol,
                max_turns=config.get('interview', {}).get('max_turns', 20)
            )

            if interview:
                save_interview(interview, args.output, persona_idx)
                successful_interviews += 1
                logger.info(f"[SUCCESS] Interview {i+1} completed ({len(interview['transcript'])} turns)")
            else:
                failed_interviews += 1
                logger.error(f"[FAILED] Interview {i+1} failed")

        except Exception as e:
            failed_interviews += 1
            logger.error(f"[FAILED] Interview {i+1} error: {e}")

        # Rate limiting between interviews
        time.sleep(1)

    # Summary
    logger.info("\n=== Interview Summary ===")
    logger.info(f"Successful interviews: {successful_interviews}")
    logger.info(f"Failed interviews: {failed_interviews}")
    logger.info(f"Total: {args.count}")
    logger.info("=== AI Interview Script Completed ===")


if __name__ == '__main__':
    main()
