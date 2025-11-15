#!/usr/bin/env python3
"""
Interactive Pipeline Runner for Gravidas Synthetic Interview Pipeline

This script provides a user-friendly interface to:
1. Select the number of interviews to conduct
2. Choose the AI model to use
3. Run the complete pipeline with your selections

Usage:
    python run_interactive.py
"""

import os
import sys
import subprocess
from typing import Tuple, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^80}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*80}{Colors.END}\n")

def print_section(text: str):
    """Print a section header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{text}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * len(text)}{Colors.END}")

def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✓{Colors.END} {text}")

def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠{Colors.END} {text}")

def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}✗{Colors.END} {text}")

def print_info(text: str):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ{Colors.END} {text}")

def get_number_input(prompt: str, min_val: int = 1, max_val: int = 10000) -> int:
    """Get a numeric input from user with validation."""
    while True:
        try:
            value = input(f"{Colors.BOLD}{prompt}{Colors.END} ")
            value = int(value)
            if min_val <= value <= max_val:
                return value
            else:
                print_error(f"Please enter a number between {min_val} and {max_val}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print("\n\nCancelled by user.")
            sys.exit(0)

def get_choice_input(prompt: str, choices: list) -> str:
    """Get a choice input from user."""
    while True:
        try:
            choice = input(f"{Colors.BOLD}{prompt}{Colors.END} ").strip().lower()
            if choice in [str(i) for i in range(1, len(choices) + 1)]:
                return choice
            else:
                print_error(f"Please enter a number between 1 and {len(choices)}")
        except KeyboardInterrupt:
            print("\n\nCancelled by user.")
            sys.exit(0)

def select_preset() -> Tuple[Optional[int], Optional[str]]:
    """Let user select from presets or custom."""
    print_section("Step 1: Choose Number of Interviews")

    print("\nAvailable Presets:")
    print(f"\n  {Colors.BOLD}1.{Colors.END} {Colors.GREEN}Quick Test{Colors.END}       - 10 interviews   (~2-3 min,  ~$0.80)")
    print(f"  {Colors.BOLD}2.{Colors.END} {Colors.YELLOW}Standard{Colors.END}          - 100 interviews  (~30 min,   ~$8)")
    print(f"  {Colors.BOLD}3.{Colors.END} {Colors.RED}Production{Colors.END}        - 1000 interviews (~4 hours,  ~$80)")
    print(f"  {Colors.BOLD}4.{Colors.END} {Colors.CYAN}Custom{Colors.END}            - Choose your own number")

    choice = get_choice_input("\nSelect option (1-4):", ["1", "2", "3", "4"])

    if choice == "1":
        return 10, "quick_test"
    elif choice == "2":
        return 100, "standard"
    elif choice == "3":
        return 1000, "production"
    else:  # Custom
        num = get_number_input("\nEnter number of interviews (1-10000):", 1, 10000)
        return num, None

def select_model() -> Tuple[str, str]:
    """Let user select AI model."""
    print_section("Step 2: Choose AI Model")

    print("\nAvailable Models:\n")

    print(f"{Colors.BOLD}Anthropic Claude:{Colors.END}")
    print(f"  {Colors.BOLD}1.{Colors.END} {Colors.GREEN}Claude Sonnet 4.5{Colors.END} (Recommended)")
    print(f"     → Best balance of quality and cost")
    print(f"     → Cost: $3/$15 per 1M tokens | Speed: Medium | Quality: Excellent")

    print(f"\n  {Colors.BOLD}2.{Colors.END} {Colors.YELLOW}Claude Opus 4.1{Colors.END}")
    print(f"     → Maximum quality, highest cost")
    print(f"     → Cost: $15/$75 per 1M tokens | Speed: Slow | Quality: Exceptional")

    print(f"\n  {Colors.BOLD}3.{Colors.END} {Colors.CYAN}Claude Haiku 4.5{Colors.END}")
    print(f"     → Fast and economical")
    print(f"     → Cost: $1/$5 per 1M tokens | Speed: Fast | Quality: Very Good")

    print(f"\n{Colors.BOLD}Google Gemini:{Colors.END}")
    print(f"  {Colors.BOLD}4.{Colors.END} {Colors.GREEN}Gemini 2.5 Flash{Colors.END} (Best Value ⭐)")
    print(f"     → Most cost-effective option")
    print(f"     → Cost: $0.15/$1.25 per 1M tokens | Speed: Very Fast | Quality: Very Good")

    print(f"\n  {Colors.BOLD}5.{Colors.END} {Colors.YELLOW}Gemini 2.5 Pro{Colors.END}")
    print(f"     → Excellent quality, good value")
    print(f"     → Cost: $1.25/$10 per 1M tokens | Speed: Medium | Quality: Excellent")

    print(f"\n{Colors.BOLD}OpenAI:{Colors.END}")
    print(f"  {Colors.BOLD}6.{Colors.END} {Colors.YELLOW}GPT-5{Colors.END}")
    print(f"     → Latest flagship model")
    print(f"     → Cost: $1.25/$10 per 1M tokens | Speed: Medium | Quality: Excellent")

    print(f"\n  {Colors.BOLD}7.{Colors.END} {Colors.CYAN}GPT-5 Mini{Colors.END}")
    print(f"     → Fast and cost-effective")
    print(f"     → Cost: $0.25/$2 per 1M tokens | Speed: Fast | Quality: Very Good")

    print(f"\n{Colors.BOLD}xAI Grok:{Colors.END}")
    print(f"  {Colors.BOLD}8.{Colors.END} {Colors.GREEN}Grok 4 Fast{Colors.END} (Fastest)")
    print(f"     → Speed and value optimized")
    print(f"     → Cost: $0.20/$0.50 per 1M tokens | Speed: Very Fast | Quality: Very Good")

    print(f"\n  {Colors.BOLD}9.{Colors.END} {Colors.YELLOW}Grok 4{Colors.END}")
    print(f"     → Most capable Grok model")
    print(f"     → Cost: $3/$15 per 1M tokens | Speed: Medium | Quality: Excellent")

    choice = get_choice_input("\nSelect model (1-9):", ["1", "2", "3", "4", "5", "6", "7", "8", "9"])

    model_map = {
        "1": ("anthropic", "claude-sonnet-4-5-20250929"),
        "2": ("anthropic", "claude-opus-4-1"),
        "3": ("anthropic", "claude-haiku-4-5"),
        "4": ("google", "gemini-2.5-flash"),
        "5": ("google", "gemini-2.5-pro"),
        "6": ("openai", "gpt-5"),
        "7": ("openai", "gpt-5-mini"),
        "8": ("xai", "grok-4-fast"),
        "9": ("xai", "grok-4"),
    }

    return model_map[choice]

def estimate_cost(num_interviews: int, model_name: str) -> Tuple[float, float]:
    """Estimate cost range for the run."""
    # Average tokens per interview (based on actual data)
    # Input: ~300 tokens, Output: ~5000 tokens per interview
    avg_input_tokens = 300 * num_interviews
    avg_output_tokens = 5000 * num_interviews

    # Cost per 1M tokens (input, output)
    costs = {
        "claude-sonnet-4-5-20250929": (3.0, 15.0),
        "claude-opus-4-1": (15.0, 75.0),
        "claude-haiku-4-5": (1.0, 5.0),
        "gemini-2.5-flash": (0.15, 1.25),
        "gemini-2.5-pro": (1.25, 10.0),
        "gpt-5": (1.25, 10.0),
        "gpt-5-mini": (0.25, 2.0),
        "grok-4-fast": (0.20, 0.50),
        "grok-4": (3.0, 15.0),
    }

    input_cost, output_cost = costs.get(model_name, (3.0, 15.0))

    # Calculate estimated cost
    estimated = (avg_input_tokens / 1_000_000 * input_cost) + (avg_output_tokens / 1_000_000 * output_cost)

    # Min/max range (±30%)
    min_cost = estimated * 0.7
    max_cost = estimated * 1.3

    return min_cost, max_cost

def estimate_time(num_interviews: int) -> str:
    """Estimate execution time."""
    # Rough estimates based on actual runs
    # ~12-15 seconds per interview average
    minutes = (num_interviews * 13) / 60

    if minutes < 5:
        return f"~{int(minutes)} minutes"
    elif minutes < 60:
        return f"~{int(minutes)} minutes"
    else:
        hours = minutes / 60
        return f"~{hours:.1f} hours"

def check_api_key(provider: str) -> bool:
    """Check if API key is set for the provider."""
    key_map = {
        "anthropic": "ANTHROPIC_API_KEY",
        "openai": "OPENAI_API_KEY",
        "google": "GOOGLE_API_KEY",
        "xai": "XAI_API_KEY"
    }

    env_var = key_map.get(provider)
    if not env_var:
        return False

    return bool(os.environ.get(env_var))

def confirm_and_run(num_interviews: int, preset: Optional[str], provider: str, model: str):
    """Confirm selections and run the pipeline."""
    print_section("Step 3: Confirm and Run")

    # Get model display name
    model_names = {
        "claude-sonnet-4-5-20250929": "Claude Sonnet 4.5",
        "claude-opus-4-1": "Claude Opus 4.1",
        "claude-haiku-4-5": "Claude Haiku 4.5",
        "gemini-2.5-flash": "Gemini 2.5 Flash",
        "gemini-2.5-pro": "Gemini 2.5 Pro",
        "gpt-5": "GPT-5",
        "gpt-5-mini": "GPT-5 Mini",
        "grok-4-fast": "Grok 4 Fast",
        "grok-4": "Grok 4",
    }

    model_display = model_names.get(model, model)

    # Check API key
    if not check_api_key(provider):
        print_error(f"API key not found for {provider}")
        print_info(f"Please set your API key:")
        key_name = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY",
                    "google": "GOOGLE_API_KEY", "xai": "XAI_API_KEY"}[provider]
        print(f"    export {key_name}='your-key-here'")
        print_info(f"See API_KEY_SETUP.md for detailed instructions")
        sys.exit(1)

    # Estimate cost and time
    min_cost, max_cost = estimate_cost(num_interviews, model)
    time_est = estimate_time(num_interviews)

    print("\n" + "="*80)
    print(f"{Colors.BOLD}Your Configuration:{Colors.END}")
    print("="*80)
    print(f"  Interviews:       {Colors.BOLD}{num_interviews}{Colors.END}")
    print(f"  AI Provider:      {Colors.BOLD}{provider.capitalize()}{Colors.END}")
    print(f"  Model:            {Colors.BOLD}{model_display}{Colors.END}")
    print(f"  Estimated Cost:   {Colors.YELLOW}${min_cost:.2f} - ${max_cost:.2f}{Colors.END}")
    print(f"  Estimated Time:   {Colors.CYAN}{time_est}{Colors.END}")
    print("="*80 + "\n")

    # Confirm
    confirm = input(f"{Colors.BOLD}Proceed with this configuration? (yes/no): {Colors.END}").strip().lower()

    if confirm not in ['yes', 'y']:
        print_warning("Run cancelled by user.")
        sys.exit(0)

    # Build command
    cmd = ["python", "scripts/run_workflow.py"]

    if preset:
        cmd.extend(["--preset", preset])
    else:
        cmd.extend(["--personas", str(num_interviews)])
        cmd.extend(["--records", str(num_interviews)])

    if provider != "anthropic":  # anthropic is default
        cmd.extend(["--provider", provider])

    cmd.extend(["--model", model])

    print_section("Executing Pipeline")
    print_info(f"Running command: {' '.join(cmd)}\n")

    # Run the pipeline
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(os.path.abspath(__file__)))

        if result.returncode == 0:
            print_section("Pipeline Complete!")
            print_success("All stages completed successfully")
            print_info("Results saved to:")
            print(f"  • {Colors.CYAN}data/analysis/interview_summary.csv{Colors.END}")
            print(f"  • {Colors.CYAN}data/analysis/interview_analysis.json{Colors.END}")
            print(f"  • {Colors.CYAN}outputs/workflow_report.json{Colors.END}")
            print_info("\nView results:")
            print(f"  cat data/analysis/interview_summary.csv")
            print(f"  cat outputs/workflow_report.json")
        else:
            print_section("Pipeline Failed")
            print_error(f"Pipeline exited with code {result.returncode}")
            print_info("Check logs for details:")
            print(f"  tail -50 logs/workflow.log")
            print(f"  cat outputs/workflow_report.json")
            sys.exit(result.returncode)

    except KeyboardInterrupt:
        print_warning("\n\nPipeline interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error running pipeline: {e}")
        sys.exit(1)

def main():
    """Main interactive flow."""
    print_header("GRAVIDAS SYNTHETIC INTERVIEW PIPELINE")
    print_info("Interactive Setup - Choose Your Configuration\n")

    # Step 1: Select number of interviews
    num_interviews, preset = select_preset()

    # Step 2: Select model
    provider, model = select_model()

    # Step 3: Confirm and run
    confirm_and_run(num_interviews, preset, provider, model)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nCancelled by user.")
        sys.exit(0)
