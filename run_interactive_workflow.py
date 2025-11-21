#!/usr/bin/env python3
"""
Interactive Gravidas Workflow Launcher
=======================================

Launch the complete Gravidas workflow with an interactive menu interface.
No command-line arguments needed - just select from menus!

Usage:
    python run_interactive_workflow.py
"""

import sys
import subprocess
from pathlib import Path

# ANSI color codes for pretty output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.END}\n")

def print_section(text):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}>>> {text}{Colors.END}\n")

def print_option(number, text, details=""):
    """Print a menu option."""
    if details:
        print(f"{Colors.GREEN}{number}.{Colors.END} {Colors.BOLD}{text}{Colors.END} - {details}")
    else:
        print(f"{Colors.GREEN}{number}.{Colors.END} {Colors.BOLD}{text}{Colors.END}")

def get_choice(prompt, min_val, max_val):
    """Get a validated numeric choice from user."""
    while True:
        try:
            choice = input(f"\n{Colors.YELLOW}{prompt} [{min_val}-{max_val}]: {Colors.END}")
            choice = int(choice)
            if min_val <= choice <= max_val:
                return choice
            else:
                print(f"{Colors.RED}Please enter a number between {min_val} and {max_val}{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Workflow cancelled by user{Colors.END}")
            sys.exit(0)

def get_custom_number(prompt, default, min_val=1, max_val=10000):
    """Get a custom number from user."""
    while True:
        try:
            value = input(f"\n{Colors.YELLOW}{prompt} (default {default}): {Colors.END}")
            if not value:
                return default
            value = int(value)
            if min_val <= value <= max_val:
                return value
            else:
                print(f"{Colors.RED}Please enter a number between {min_val} and {max_val}{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Workflow cancelled by user{Colors.END}")
            sys.exit(0)

def select_scale():
    """Select workflow scale (quick presets)."""
    print_section("Step 1: Select Workflow Scale")

    print_option(1, "Quick Test", "10 personas, 10 records, 3 interviews (~7 min, $0.05)")
    print_option(2, "Small Run", "25 personas, 25 records, 10 interviews (~30 min, $0.50)")
    print_option(3, "Medium Run", "50 personas, 50 records, 25 interviews (~1.5 hrs, $2)")
    print_option(4, "Standard Run", "100 personas, 100 records, 50 interviews (~3 hrs, $10)")
    print_option(5, "Large Run", "500 personas, 500 records, 200 interviews (~15 hrs, $60)")
    print_option(6, "Production Run", "1000 personas, 1000 records, 500 interviews (~40 hrs, $150)")
    print_option(7, "Custom", "Enter custom values")

    choice = get_choice("Select scale", 1, 7)

    scale_configs = {
        1: {"personas": 10, "records": 10, "interviews": 3},
        2: {"personas": 25, "records": 25, "interviews": 10},
        3: {"personas": 50, "records": 50, "interviews": 25},
        4: {"personas": 100, "records": 100, "interviews": 50},
        5: {"personas": 500, "records": 500, "interviews": 200},
        6: {"personas": 1000, "records": 1000, "interviews": 500},
    }

    if choice == 7:
        # Custom values
        personas = get_custom_number("Number of personas", 100, 1, 10000)
        records = get_custom_number("Number of health records", personas, 1, 10000)
        interviews = get_custom_number("Number of interviews", min(50, personas), 1, 1000)
        return {"personas": personas, "records": records, "interviews": interviews}
    else:
        return scale_configs[choice]

def select_provider():
    """Select AI provider."""
    print_section("Step 2: Select AI Provider")

    print_option(1, "Anthropic Claude", "Best for medical quality, nuanced responses")
    print_option(2, "OpenAI GPT", "Broad knowledge, structured outputs")
    print_option(3, "Google Gemini", "Fastest, large context, cost-effective")
    print_option(4, "xAI Grok", "Research applications, reasoning")

    choice = get_choice("Select provider", 1, 4)

    providers = {
        1: "anthropic",
        2: "openai",
        3: "google",
        4: "xai"
    }

    return providers[choice]

def select_model(provider):
    """Select specific AI model based on provider."""
    print_section(f"Step 3: Select {provider.title()} Model")

    models = {
        "anthropic": [
            ("claude-haiku-4-5", "Fast & Cheap", "$1/$5 per 1M tokens - Fastest Claude"),
            ("claude-sonnet-4-5", "Recommended", "$3/$15 per 1M tokens - Best balance"),
            ("claude-sonnet-4-5-20250929", "Specific Version", "$3/$15 per 1M tokens"),
            ("claude-opus-4-1", "Premium Quality", "$15/$75 per 1M tokens - Highest quality"),
        ],
        "openai": [
            ("gpt-4o-mini", "Recommended", "$0.15/$0.60 per 1M tokens - Best value"),
            ("gpt-4o", "Standard", "$2.50/$10 per 1M tokens - Multimodal"),
            ("gpt-5-mini", "Efficient", "$0.25/$2 per 1M tokens"),
            ("gpt-5", "Latest", "$1.25/$10 per 1M tokens - Latest generation"),
            ("gpt-5-nano", "Ultra-cheap", "$0.05/$0.40 per 1M tokens"),
            ("gpt-4-1", "GPT-4.1", "$2/$8 per 1M tokens"),
        ],
        "google": [
            ("gemini-2.5-flash", "Recommended", "$0.15/$1.25 per 1M tokens - FASTEST"),
            ("gemini-2.5-pro", "High Quality", "$1.25/$10 per 1M tokens - Most capable"),
            ("gemini-2.5-pro-long", "Extended Context", "$2.50/$15 per 1M tokens - 200k+ context"),
            ("gemini-3-pro-preview", "Preview", "Next generation - Pricing TBD"),
        ],
        "xai": [
            ("grok-4-fast", "Recommended", "$0.20/$0.50 per 1M tokens - Fast reasoning"),
            ("grok-4", "Premium", "$3/$15 per 1M tokens - Most capable"),
            ("grok-3-mini", "Budget", "$0.30/$0.50 per 1M tokens"),
        ]
    }

    provider_models = models[provider]

    for i, (model_name, category, details) in enumerate(provider_models, 1):
        print_option(i, f"{model_name} [{category}]", details)

    print_option(len(provider_models) + 1, "Use default", "Let system choose best model")

    choice = get_choice("Select model", 1, len(provider_models) + 1)

    if choice == len(provider_models) + 1:
        return None  # Use default
    else:
        return provider_models[choice - 1][0]

def select_protocol():
    """Select interview protocol."""
    print_section("Step 4: Select Interview Protocol")

    protocols = [
        ("prenatal_care.json", "Prenatal Care", "Routine prenatal visits and care"),
        ("high_risk_pregnancy.json", "High-Risk Pregnancy", "Complications and advanced monitoring"),
        ("mental_health_screening.json", "Mental Health", "Psychological wellbeing, mood disorders"),
        ("genetic_counseling.json", "Genetic Counseling", "Genetic risks and family history"),
        ("postpartum_care.json", "Postpartum Care", "Post-birth recovery and newborn care"),
        ("pregnancy_experience.json", "Pregnancy Experience", "Overall pregnancy journey"),
    ]

    for i, (filename, name, description) in enumerate(protocols, 1):
        print_option(i, name, description)

    choice = get_choice("Select interview protocol", 1, len(protocols))

    return f"Script/interview_protocols/{protocols[choice - 1][0]}"

def select_options():
    """Select additional options."""
    print_section("Step 5: Additional Options")

    print(f"{Colors.BOLD}Continue on error?{Colors.END}")
    print("  If a stage fails, should the workflow continue with remaining stages?")
    print("  1. No  - Stop on first error (recommended)")
    print("  2. Yes - Continue even if stages fail")

    continue_choice = get_choice("Select option", 1, 2)
    continue_on_error = (continue_choice == 2)

    return {"continue_on_error": continue_on_error}

def show_summary(config):
    """Display configuration summary."""
    print_header("WORKFLOW CONFIGURATION SUMMARY")

    print(f"{Colors.BOLD}Data Generation:{Colors.END}")
    print(f"  Personas:       {config['personas']}")
    print(f"  Health Records: {config['records']}")
    print(f"  Interviews:     {config['interviews']}")

    print(f"\n{Colors.BOLD}AI Configuration:{Colors.END}")
    print(f"  Provider:       {config['provider'].title()}")
    print(f"  Model:          {config['model'] if config['model'] else 'Default'}")

    print(f"\n{Colors.BOLD}Interview Settings:{Colors.END}")
    print(f"  Protocol:       {Path(config['protocol']).stem.replace('_', ' ').title()}")

    print(f"\n{Colors.BOLD}Options:{Colors.END}")
    print(f"  Continue on error: {'Yes' if config['continue_on_error'] else 'No'}")

    print(f"\n{Colors.BOLD}Output:{Colors.END}")
    print(f"  Results will be saved to: data/")
    print(f"  Archive will be created in: archives/")

    # Estimate time and cost
    personas = config['personas']
    interviews = config['interviews']

    # Rough estimates
    persona_time = personas * 3  # ~3 seconds per persona
    records_time = personas * 2   # ~2 seconds per record
    matching_time = 5             # ~5 seconds
    interview_time = interviews * 120  # ~2 minutes per interview
    analysis_time = 5             # ~5 seconds

    total_seconds = persona_time + records_time + matching_time + interview_time + analysis_time
    total_minutes = total_seconds / 60
    total_hours = total_minutes / 60

    if total_hours >= 1:
        time_estimate = f"{total_hours:.1f} hours"
    else:
        time_estimate = f"{total_minutes:.1f} minutes"

    print(f"\n{Colors.BOLD}Estimated Time:{Colors.END} {time_estimate}")

    # Cost estimates (rough, based on Haiku rates)
    # Assume ~500 tokens per persona, ~1000 per record, ~5000 per interview
    total_tokens = (personas * 500) + (personas * 1000) + (interviews * 5000)
    cost_per_1m = 1.0  # Haiku input rate
    estimated_cost = (total_tokens / 1000000) * cost_per_1m * 2  # x2 for output

    print(f"{Colors.BOLD}Estimated Cost:{Colors.END} ${estimated_cost:.2f} (approximate)")

def confirm_start():
    """Ask user to confirm before starting."""
    print(f"\n{Colors.YELLOW}{'='*80}{Colors.END}")
    print(f"{Colors.YELLOW}Ready to start workflow. This will begin generating data.{Colors.END}")
    print(f"{Colors.YELLOW}{'='*80}{Colors.END}\n")

    choice = input(f"{Colors.BOLD}Start workflow now? [Y/n]: {Colors.END}").strip().lower()

    if choice in ['n', 'no']:
        print(f"\n{Colors.YELLOW}Workflow cancelled by user{Colors.END}")
        sys.exit(0)

    return True

def run_workflow(config):
    """Execute the workflow with selected configuration."""
    print_header("STARTING GRAVIDAS WORKFLOW")

    # Build command
    cmd = [
        'python', 'run_complete_workflow.py',
        '--personas', str(config['personas']),
        '--records', str(config['records']),
        '--interviews', str(config['interviews']),
        '--provider', config['provider'],
        '--protocol', config['protocol']
    ]

    if config['model']:
        cmd.extend(['--model', config['model']])

    if config['continue_on_error']:
        cmd.append('--continue-on-error')

    print(f"{Colors.CYAN}Executing command:{Colors.END}")
    print(f"{Colors.BOLD}{' '.join(cmd)}{Colors.END}\n")

    print(f"{Colors.GREEN}{'='*80}{Colors.END}")
    print(f"{Colors.GREEN}Starting workflow execution...{Colors.END}")
    print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")

    # Run the workflow
    try:
        subprocess.run(cmd, check=True)

        print(f"\n{Colors.GREEN}{'='*80}{Colors.END}")
        print(f"{Colors.GREEN}✓ Workflow completed successfully!{Colors.END}")
        print(f"{Colors.GREEN}{'='*80}{Colors.END}\n")

        print(f"{Colors.BOLD}Results saved to:{Colors.END}")
        print(f"  data/personas/")
        print(f"  data/health_records/")
        print(f"  data/matched/")
        print(f"  data/interviews/")
        print(f"  data/analysis/")
        print(f"  outputs/complete_workflow_report.json")
        print(f"\n{Colors.BOLD}Archive created in:{Colors.END} archives/")

    except subprocess.CalledProcessError as e:
        print(f"\n{Colors.RED}{'='*80}{Colors.END}")
        print(f"{Colors.RED}✗ Workflow failed with error code {e.returncode}{Colors.END}")
        print(f"{Colors.RED}{'='*80}{Colors.END}\n")
        print(f"{Colors.YELLOW}Check logs/ directory for details{Colors.END}")
        sys.exit(1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Workflow interrupted by user{Colors.END}")
        sys.exit(1)

def main():
    """Main interactive workflow."""
    print_header("GRAVIDAS INTERACTIVE WORKFLOW LAUNCHER")

    print(f"{Colors.BOLD}Welcome!{Colors.END}")
    print("This interactive launcher will guide you through configuring and running")
    print("the complete Gravidas synthetic data generation workflow.\n")
    print(f"{Colors.CYAN}You'll be asked to select:{Colors.END}")
    print("  1. Workflow scale (number of personas, records, interviews)")
    print("  2. AI provider (Anthropic, OpenAI, Google, xAI)")
    print("  3. AI model (specific model within provider)")
    print("  4. Interview protocol (topic/focus area)")
    print("  5. Additional options")
    print(f"\n{Colors.YELLOW}Press Ctrl+C at any time to cancel{Colors.END}")

    input(f"\n{Colors.BOLD}Press Enter to begin...{Colors.END}")

    # Step 1: Scale
    scale_config = select_scale()

    # Step 2: Provider
    provider = select_provider()

    # Step 3: Model
    model = select_model(provider)

    # Step 4: Protocol
    protocol = select_protocol()

    # Step 5: Options
    options = select_options()

    # Combine configuration
    config = {
        **scale_config,
        'provider': provider,
        'model': model,
        'protocol': protocol,
        **options
    }

    # Show summary
    show_summary(config)

    # Confirm
    confirm_start()

    # Run workflow
    run_workflow(config)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Workflow cancelled by user{Colors.END}")
        sys.exit(0)
