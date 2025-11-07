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



# Import centralized model registry
from utils.models import (
    MODELS_REGISTRY as MODELS_DATABASE,
    AVG_INPUT_TOKENS_PER_INTERVIEW,
    AVG_OUTPUT_TOKENS_PER_INTERVIEW,
    estimate_cost,
    get_model_info
)



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
    # ⚠️  DEPRECATED: Loading from config is not recommended for security
    config = load_config()
    api_keys_config = config.get('api_keys', {})

    for provider in ['anthropic', 'openai', 'google', 'xai']:
        if provider not in keys:
            provider_config = api_keys_config.get(provider, {})
            api_key = provider_config.get('api_key', '')

            # Skip placeholders (your-, PLACEHOLDER, USE-ENVIRONMENT)
            if api_key and not api_key.startswith('your-') and 'PLACEHOLDER' not in api_key.upper() and 'USE-ENVIRONMENT' not in api_key.upper():
                keys[provider] = {
                    'key': api_key,
                    'source': 'config.yaml ⚠️ (not recommended)'
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
    num_interviews: int,
    use_batch: bool = False
) -> Tuple[float, int, bool]:
    """
    Calculate estimated cost and time for interviews.

    Args:
        model_info: Model metadata
        num_interviews: Number of interviews
        use_batch: Whether to use batch API pricing

    Returns:
        Tuple of (cost in USD, time in minutes, batch_available)
    """
    # Check if batch is available for this model
    batch_available = model_info.get('batch_available', False)

    # Calculate cost
    if use_batch and batch_available:
        input_cost_per_million = model_info['batch_input']
        output_cost_per_million = model_info['batch_output']
    else:
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
    # For batch mode, add significant time (24 hours typical)
    if use_batch and batch_available:
        # Batch processing: assume 24 hour turnaround time
        total_minutes = 24 * 60
    else:
        # Real-time processing
        seconds_per_interview = (tokens_per_interview / tokens_per_second) * 1.2
        total_seconds = seconds_per_interview * num_interviews
        total_minutes = int(total_seconds / 60)

    return total_cost, total_minutes, batch_available


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
        cost, time_min, batch_available = calculate_cost_and_time(model_info, num_interviews)

        recommended = " ⭐ RECOMMENDED" if model_info.get('recommended') else ""
        batch_badge = " 🔄 BATCH" if batch_available else ""

        print(f"{i:<4} {model_info['name']:<25} {model_info['quality']:<12} "
              f"${cost:>7.2f}{'':>6} {format_time(time_min):<12} {recommended}{batch_badge}")

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


def check_data_files() -> bool:
    """
    Check if required data files exist, offer to generate test data if not.

    Returns:
        True if data exists or was generated, False if user cancelled
    """
    matched_file = Path("data/matched/matched_personas.json")

    if matched_file.exists():
        return True

    # Data doesn't exist, offer to generate test data
    clear_screen()
    print_header("MISSING DATA FILES")

    print("⚠  The matched personas file doesn't exist yet.")
    print()
    print("You have two options:")
    print()
    print("  1. Generate test data (10 sample personas) - Quick!")
    print("     This creates sample data so you can try interviews immediately.")
    print()
    print("  2. Run the full pipeline first - Recommended for research")
    print("     This retrieves real personas and generates health records.")
    print()
    print("For option 2, run these commands:")
    print("  python scripts/01_retrieve_personas.py")
    print("  python scripts/02_generate_health_records.py")
    print("  python scripts/03_match_personas_records.py")
    print()

    choice = input("Generate test data now? (yes/no): ").strip().lower()

    if choice in ['yes', 'y']:
        print("\nGenerating test data...")
        try:
            subprocess.run(['python', 'scripts/generate_test_data.py'], check=True)
            print("\n✓ Test data generated successfully!")
            input("\nPress Enter to continue...")
            return True
        except subprocess.CalledProcessError:
            print("\n✗ Failed to generate test data")
            input("\nPress Enter to continue...")
            return False
    else:
        print("\nPlease run the pipeline steps or generate test data first.")
        input("\nPress Enter to continue...")
        return False


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
    # Check if data files exist
    if not check_data_files():
        return False

    clear_screen()
    print_header("CONFIRMATION")

    model_info = MODELS_DATABASE[provider]['models'][model_id]

    # Ask about batch mode if available
    use_batch = False
    batch_available = model_info.get('batch_available', False)

    if batch_available and num_interviews >= 100:
        print("\n💡 Batch API Available!")
        print("   - 50% cost savings")
        print("   - ~24 hour turnaround time")
        print("   - Ideal for large volumes (100+ interviews)")
        print()
        batch_choice = input("Use Batch API? (yes/no): ").strip().lower()
        use_batch = batch_choice in ['yes', 'y']

    cost, time_min, _ = calculate_cost_and_time(model_info, num_interviews, use_batch)

    print("Interview Configuration:")
    print()
    print(f"  Provider:         {MODELS_DATABASE[provider]['name']}")
    print(f"  Model:            {model_info['name']}")
    print(f"  Model ID:         {model_id}")
    print(f"  Quality:          {model_info['quality']}")
    print(f"  Batch Mode:       {'✓ Yes (50% discount)' if use_batch else '✗ No (Real-time)'}")
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

        # Add batch flag if selected
        if use_batch:
            cmd.append('--batch')

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
        elif provider == 'aws':
            env['AWS_ACCESS_KEY_ID'] = api_key
            # Note: AWS also needs secret key, region, etc.
        elif provider == 'mistral':
            env['MISTRAL_API_KEY'] = api_key

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
