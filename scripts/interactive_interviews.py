#!/usr/bin/env python3
"""
Interactive Interview Launcher

Provides a user-friendly interface for:
1. Managing API keys (config, environment, or manual entry)
2. Selecting number of interviews
3. Choosing AI provider and model
4. Viewing cost and time estimates
5. Running interviews

Usage:
    python scripts/interactive_interviews.py
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess

try:
    import yaml
    from dotenv import load_dotenv
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install python-dotenv pyyaml")
    sys.exit(1)


# Model metadata with costs and performance
MODELS_DATABASE = {
    'anthropic': {
        'name': 'Anthropic (Claude)',
        'models': {
            'claude-4.1-opus': {
                'name': 'Claude 4.1 Opus',
                'cost_input': 15.0,
                'cost_output': 75.0,
                'tokens_per_second': 50,
                'quality': 'Excellent',
                'description': 'Complex reasoning, autonomous agents, high-stakes analysis'
            },
            'claude-4.5-sonnet': {
                'name': 'Claude 4.5 Sonnet',
                'cost_input': 3.0,
                'cost_output': 15.0,
                'tokens_per_second': 80,
                'quality': 'Excellent',
                'description': 'Agentic workhorse, advanced coding (Recommended)',
                'recommended': True
            },
            'claude-4.5-haiku': {
                'name': 'Claude 4.5 Haiku',
                'cost_input': 1.0,
                'cost_output': 5.0,
                'tokens_per_second': 120,
                'quality': 'Very Good',
                'description': 'Near-frontier speed, fast applications'
            },
            'claude-3-haiku': {
                'name': 'Claude 3 Haiku',
                'cost_input': 0.25,
                'cost_output': 1.25,
                'tokens_per_second': 150,
                'quality': 'Good',
                'description': 'Ultra-fast, simple Q&A, testing'
            }
        }
    },
    'openai': {
        'name': 'OpenAI (GPT-5)',
        'models': {
            'gpt-5-pro': {
                'name': 'GPT-5 Pro',
                'cost_input': 15.0,
                'cost_output': 120.0,
                'tokens_per_second': 40,
                'quality': 'Excellent',
                'description': 'Peak performance, mission-critical reasoning'
            },
            'gpt-5': {
                'name': 'GPT-5',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'tokens_per_second': 70,
                'quality': 'Excellent',
                'description': 'Advanced tasks, complex coding (Recommended)',
                'recommended': True
            },
            'gpt-5-mini': {
                'name': 'GPT-5 Mini',
                'cost_input': 0.25,
                'cost_output': 2.0,
                'tokens_per_second': 100,
                'quality': 'Very Good',
                'description': 'Capable & fast, smart chatbots'
            },
            'gpt-5-nano': {
                'name': 'GPT-5 Nano',
                'cost_input': 0.05,
                'cost_output': 0.40,
                'tokens_per_second': 140,
                'quality': 'Good',
                'description': 'High-throughput, classification, testing'
            }
        }
    },
    'google': {
        'name': 'Google (Gemini)',
        'models': {
            'gemini-2.5-pro': {
                'name': 'Gemini 2.5 Pro',
                'cost_input': 1.25,
                'cost_output': 10.0,
                'tokens_per_second': 75,
                'quality': 'Excellent',
                'description': 'Advanced thinking model, complex coding (Recommended)',
                'recommended': True
            },
            'gemini-2.5-flash': {
                'name': 'Gemini 2.5 Flash',
                'cost_input': 0.30,
                'cost_output': 2.50,
                'tokens_per_second': 110,
                'quality': 'Very Good',
                'description': 'Enterprise workhorse, high-volume agents'
            },
            'gemini-2.5-flash-lite': {
                'name': 'Gemini 2.5 Flash Lite',
                'cost_input': 0.10,
                'cost_output': 0.40,
                'tokens_per_second': 130,
                'quality': 'Good',
                'description': 'High-volume, low-latency, simple chatbots'
            },
            'gemini-2.0-flash': {
                'name': 'Gemini 2.0 Flash',
                'cost_input': 0.05,
                'cost_output': 0.20,
                'tokens_per_second': 145,
                'quality': 'Good',
                'description': 'Legacy model, experimental, prototyping'
            }
        }
    },
    'xai': {
        'name': 'xAI (Grok)',
        'models': {
            'grok-2': {
                'name': 'Grok 2',
                'cost_input': 2.0,
                'cost_output': 10.0,
                'tokens_per_second': 60,
                'quality': 'Excellent',
                'description': 'Advanced reasoning, real-time knowledge'
            },
            'grok-2-mini': {
                'name': 'Grok 2 Mini',
                'cost_input': 0.50,
                'cost_output': 2.5,
                'tokens_per_second': 90,
                'quality': 'Very Good',
                'description': 'Fast, capable, good value'
            }
        }
    }
}

# Average tokens per interview (for cost estimation)
AVG_INPUT_TOKENS_PER_INTERVIEW = 3000
AVG_OUTPUT_TOKENS_PER_INTERVIEW = 2000


def clear_screen():
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_header(title: str):
    """Print a formatted header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def print_section(title: str):
    """Print a section title."""
    print(f"\n{'─' * 70}")
    print(f"  {title}")
    print('─' * 70)


def load_env_file() -> bool:
    """Load .env file if it exists."""
    env_path = Path('.env')
    if env_path.exists():
        load_dotenv(env_path)
        return True
    return False


def load_config() -> Dict[str, Any]:
    """Load configuration from YAML file."""
    config_path = Path('config/config.yaml')
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            print(f"Warning: Could not load config.yaml: {e}")
    return {}


def get_api_keys() -> Dict[str, Dict[str, str]]:
    """
    Get API keys from multiple sources.

    Priority: 1. Environment variables, 2. Config file

    Returns:
        Dict mapping provider to API key info
    """
    keys = {}

    # Load from environment variables
    env_loaded = load_env_file()

    # Check for API keys in environment
    if os.getenv('ANTHROPIC_API_KEY'):
        keys['anthropic'] = {
            'key': os.getenv('ANTHROPIC_API_KEY'),
            'source': 'environment'
        }

    if os.getenv('OPENAI_API_KEY'):
        keys['openai'] = {
            'key': os.getenv('OPENAI_API_KEY'),
            'source': 'environment'
        }

    if os.getenv('GOOGLE_API_KEY'):
        keys['google'] = {
            'key': os.getenv('GOOGLE_API_KEY'),
            'source': 'environment'
        }

    if os.getenv('XAI_API_KEY'):
        keys['xai'] = {
            'key': os.getenv('XAI_API_KEY'),
            'source': 'environment'
        }

    # Load from config file (if not in environment)
    config = load_config()
    api_keys_config = config.get('api_keys', {})

    for provider in ['anthropic', 'openai', 'google', 'xai']:
        if provider not in keys:
            provider_config = api_keys_config.get(provider, {})
            api_key = provider_config.get('api_key', '')

            if api_key and not api_key.startswith('your-'):
                keys[provider] = {
                    'key': api_key,
                    'source': 'config.yaml'
                }

    return keys


def manage_api_keys(current_keys: Dict[str, Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    """
    Interactive API key management.

    Returns:
        Updated API keys dictionary
    """
    clear_screen()
    print_header("API KEY MANAGEMENT")

    print("Current API Keys Status:")
    print()

    for provider, info in MODELS_DATABASE.items():
        provider_name = info['name']
        if provider in current_keys:
            key = current_keys[provider]['key']
            source = current_keys[provider]['source']
            masked_key = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
            print(f"  ✓ {provider_name:25} {masked_key:20} (from {source})")
        else:
            print(f"  ✗ {provider_name:25} {'No API key':20}")

    print()
    print("Options:")
    print("  1. Add/Update API key manually")
    print("  2. Load from .env file")
    print("  3. Continue with current keys")
    print("  4. Exit")

    choice = input("\nSelect option (1-4): ").strip()

    if choice == '1':
        # Manual API key entry
        print()
        print("Available providers:")
        provider_list = list(MODELS_DATABASE.keys())
        for i, (provider, info) in enumerate(MODELS_DATABASE.items(), 1):
            print(f"  {i}. {info['name']}")

        try:
            provider_choice = int(input("\nSelect provider (number): ").strip())
            if 1 <= provider_choice <= len(provider_list):
                provider = provider_list[provider_choice - 1]
                print(f"\nEnter API key for {MODELS_DATABASE[provider]['name']}:")
                api_key = input("API Key: ").strip()

                if api_key:
                    current_keys[provider] = {
                        'key': api_key,
                        'source': 'manual entry'
                    }
                    print(f"\n✓ API key for {MODELS_DATABASE[provider]['name']} updated!")
                    input("\nPress Enter to continue...")
        except (ValueError, IndexError):
            print("\nInvalid selection!")
            input("Press Enter to continue...")

        return manage_api_keys(current_keys)

    elif choice == '2':
        # Load from .env file
        if load_env_file():
            print("\n✓ Loaded .env file")
            current_keys = get_api_keys()
            input("Press Enter to continue...")
        else:
            print("\n✗ No .env file found in current directory")
            input("Press Enter to continue...")

        return manage_api_keys(current_keys)

    elif choice == '3':
        return current_keys

    elif choice == '4':
        print("\nExiting...")
        sys.exit(0)

    else:
        print("\nInvalid option!")
        input("Press Enter to continue...")
        return manage_api_keys(current_keys)


def get_interview_count() -> int:
    """
    Prompt user for number of interviews.

    Returns:
        Number of interviews (1-10,000)
    """
    clear_screen()
    print_header("INTERVIEW CONFIGURATION")

    print("How many interviews would you like to conduct?")
    print()
    print("  Recommended ranges:")
    print("    • Testing: 1-10 interviews")
    print("    • Pilot study: 10-100 interviews")
    print("    • Full study: 100-10,000 interviews")
    print()

    while True:
        try:
            count = input("Enter number of interviews (1-10000): ").strip()
            count = int(count)

            if 1 <= count <= 10000:
                return count
            else:
                print("  ✗ Please enter a number between 1 and 10,000")
        except ValueError:
            print("  ✗ Please enter a valid number")


def calculate_cost_and_time(
    model_info: Dict[str, Any],
    num_interviews: int
) -> Tuple[float, int]:
    """
    Calculate estimated cost and time for interviews.

    Args:
        model_info: Model metadata
        num_interviews: Number of interviews

    Returns:
        Tuple of (cost in USD, time in minutes)
    """
    # Calculate cost
    input_cost_per_million = model_info['cost_input']
    output_cost_per_million = model_info['cost_output']

    total_input_tokens = AVG_INPUT_TOKENS_PER_INTERVIEW * num_interviews
    total_output_tokens = AVG_OUTPUT_TOKENS_PER_INTERVIEW * num_interviews

    input_cost = (total_input_tokens / 1_000_000) * input_cost_per_million
    output_cost = (total_output_tokens / 1_000_000) * output_cost_per_million
    total_cost = input_cost + output_cost

    # Calculate time
    # Assuming sequential processing with some overhead
    tokens_per_second = model_info['tokens_per_second']
    tokens_per_interview = AVG_INPUT_TOKENS_PER_INTERVIEW + AVG_OUTPUT_TOKENS_PER_INTERVIEW

    # Add 20% overhead for network latency, processing, etc.
    seconds_per_interview = (tokens_per_interview / tokens_per_second) * 1.2
    total_seconds = seconds_per_interview * num_interviews
    total_minutes = int(total_seconds / 60)

    return total_cost, total_minutes


def format_time(minutes: int) -> str:
    """Format time in a human-readable way."""
    if minutes < 60:
        return f"{minutes} minutes"
    elif minutes < 1440:  # Less than 24 hours
        hours = minutes // 60
        mins = minutes % 60
        return f"{hours}h {mins}m"
    else:
        days = minutes // 1440
        hours = (minutes % 1440) // 60
        return f"{days}d {hours}h"


def select_provider_and_model(
    available_keys: Dict[str, Dict[str, str]],
    num_interviews: int
) -> Tuple[str, str]:
    """
    Interactive provider and model selection.

    Args:
        available_keys: Available API keys
        num_interviews: Number of interviews for cost estimation

    Returns:
        Tuple of (provider, model_id)
    """
    clear_screen()
    print_header(f"MODEL SELECTION ({num_interviews:,} interviews)")

    # Filter providers with API keys
    available_providers = {
        p: info for p, info in MODELS_DATABASE.items()
        if p in available_keys
    }

    if not available_providers:
        print("✗ No API keys available!")
        print("\nPlease configure API keys first.")
        input("\nPress Enter to continue...")
        return None, None

    # Select provider
    print("Available Providers:")
    print()

    provider_list = list(available_providers.keys())
    for i, (provider, info) in enumerate(available_providers.items(), 1):
        num_models = len(info['models'])
        print(f"  {i}. {info['name']:30} ({num_models} models available)")

    print()
    try:
        provider_choice = int(input("Select provider (number): ").strip())
        if not (1 <= provider_choice <= len(provider_list)):
            print("\n✗ Invalid selection!")
            input("Press Enter to continue...")
            return select_provider_and_model(available_keys, num_interviews)

        provider = provider_list[provider_choice - 1]
    except ValueError:
        print("\n✗ Invalid input!")
        input("Press Enter to continue...")
        return select_provider_and_model(available_keys, num_interviews)

    # Select model
    clear_screen()
    print_header(f"MODEL SELECTION - {MODELS_DATABASE[provider]['name']}")
    print(f"Number of interviews: {num_interviews:,}")
    print()

    models = MODELS_DATABASE[provider]['models']
    model_list = list(models.keys())

    print(f"{'#':<4} {'Model':<25} {'Quality':<12} {'Est. Cost':<15} {'Est. Time':<12} {'Notes'}")
    print("─" * 105)

    for i, (model_id, model_info) in enumerate(models.items(), 1):
        cost, time_min = calculate_cost_and_time(model_info, num_interviews)

        recommended = " ⭐ RECOMMENDED" if model_info.get('recommended') else ""

        print(f"{i:<4} {model_info['name']:<25} {model_info['quality']:<12} "
              f"${cost:>7.2f}{'':>6} {format_time(time_min):<12} {recommended}")

    print()
    print("Description:")
    for i, (model_id, model_info) in enumerate(models.items(), 1):
        print(f"  {i}. {model_info['description']}")

    print()
    try:
        model_choice = int(input("Select model (number): ").strip())
        if not (1 <= model_choice <= len(model_list)):
            print("\n✗ Invalid selection!")
            input("Press Enter to continue...")
            return select_provider_and_model(available_keys, num_interviews)

        model_id = model_list[model_choice - 1]
        return provider, model_id

    except ValueError:
        print("\n✗ Invalid input!")
        input("Press Enter to continue...")
        return select_provider_and_model(available_keys, num_interviews)


def confirm_and_run(
    provider: str,
    model_id: str,
    num_interviews: int,
    api_key: str
) -> bool:
    """
    Show confirmation and run interviews.

    Args:
        provider: Provider name
        model_id: Model ID
        num_interviews: Number of interviews
        api_key: API key to use

    Returns:
        True if interviews started, False otherwise
    """
    clear_screen()
    print_header("CONFIRMATION")

    model_info = MODELS_DATABASE[provider]['models'][model_id]
    cost, time_min = calculate_cost_and_time(model_info, num_interviews)

    print("Interview Configuration:")
    print()
    print(f"  Provider:         {MODELS_DATABASE[provider]['name']}")
    print(f"  Model:            {model_info['name']}")
    print(f"  Model ID:         {model_id}")
    print(f"  Quality:          {model_info['quality']}")
    print()
    print(f"  Num Interviews:   {num_interviews:,}")
    print(f"  Estimated Cost:   ${cost:.2f}")
    print(f"  Estimated Time:   {format_time(time_min)}")
    print()
    print(f"  Output Directory: data/interviews/")
    print()

    confirm = input("Proceed with interviews? (yes/no): ").strip().lower()

    if confirm in ['yes', 'y']:
        print("\n" + "=" * 70)
        print("  Starting Interviews...")
        print("=" * 70 + "\n")

        # Build command
        cmd = [
            'python',
            'scripts/04_conduct_interviews.py',
            '--provider', provider,
            '--model', model_id,
            '--count', str(num_interviews)
        ]

        # Set API key as environment variable
        env = os.environ.copy()
        if provider == 'anthropic':
            env['ANTHROPIC_API_KEY'] = api_key
        elif provider == 'openai':
            env['OPENAI_API_KEY'] = api_key
        elif provider == 'google':
            env['GOOGLE_API_KEY'] = api_key
        elif provider == 'xai':
            env['XAI_API_KEY'] = api_key

        try:
            # Run the interview script with API key in environment
            subprocess.run(cmd, check=True, env=env)
            return True
        except subprocess.CalledProcessError as e:
            print(f"\n✗ Error running interviews: {e}")
            input("\nPress Enter to continue...")
            return False
        except KeyboardInterrupt:
            print("\n\n✗ Interrupted by user")
            input("\nPress Enter to continue...")
            return False

    return False


def main_menu():
    """Main interactive menu."""
    while True:
        # Get API keys
        api_keys = get_api_keys()

        # API Key Management
        api_keys = manage_api_keys(api_keys)

        if not api_keys:
            print("\n✗ No API keys configured. Please add at least one API key.")
            input("\nPress Enter to continue...")
            continue

        # Get interview count
        num_interviews = get_interview_count()

        # Select provider and model
        provider, model_id = select_provider_and_model(api_keys, num_interviews)

        if not provider or not model_id:
            continue

        # Confirm and run
        api_key = api_keys[provider]['key']
        success = confirm_and_run(provider, model_id, num_interviews, api_key)

        if success:
            print("\n" + "=" * 70)
            print("  Interviews completed!")
            print("=" * 70)
            print()
            print("  Results saved to: data/interviews/")
            print()

            another = input("Run another batch? (yes/no): ").strip().lower()
            if another not in ['yes', 'y']:
                break
        else:
            print("\nReturning to main menu...")
            input("Press Enter to continue...")

    print("\nThank you for using the Synthetic Gravidas Pipeline!")


if __name__ == '__main__':
    try:
        main_menu()
    except KeyboardInterrupt:
        print("\n\nExiting...")
        sys.exit(0)
