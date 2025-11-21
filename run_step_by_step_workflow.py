#!/usr/bin/env python3
"""
GRAVIDAS Step-by-Step Interactive Workflow
============================================

Execute the complete workflow interactively, stage by stage, with the ability to:
- Configure each stage before running
- Review results after each stage
- Pause, skip, or repeat stages
- Make decisions based on intermediate results

Usage:
    python run_step_by_step_workflow.py
"""

import sys
import os
import subprocess
import time
import json
from pathlib import Path
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    DIM = '\033[2m'
    END = '\033[0m'

def clear_screen():
    """Clear terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print formatted header."""
    width = 80
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'═' * width}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(width)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'═' * width}{Colors.END}\n")

def print_stage_header(stage_num, stage_name, description):
    """Print stage header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}┌{'─' * 78}┐{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}│ STAGE {stage_num}: {stage_name.upper():<67}│{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}│ {description:<76}│{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}└{'─' * 78}┘{Colors.END}\n")

def print_success(msg):
    print(f"{Colors.GREEN}✓ {msg}{Colors.END}")

def print_error(msg):
    print(f"{Colors.RED}✗ {msg}{Colors.END}")

def print_warning(msg):
    print(f"{Colors.YELLOW}⚠ {msg}{Colors.END}")

def print_info(msg):
    print(f"{Colors.CYAN}ℹ {msg}{Colors.END}")

def print_menu(options):
    """Print menu options."""
    for key, (label, desc) in options.items():
        if desc:
            print(f"  {Colors.GREEN}[{key}]{Colors.END} {Colors.BOLD}{label}{Colors.END} - {desc}")
        else:
            print(f"  {Colors.GREEN}[{key}]{Colors.END} {Colors.BOLD}{label}{Colors.END}")

def get_input(prompt, valid_options=None, default=None):
    """Get user input with validation."""
    while True:
        try:
            suffix = f" (default: {default})" if default else ""
            user_input = input(f"{Colors.YELLOW}{prompt}{suffix}: {Colors.END}").strip()

            if not user_input and default is not None:
                return default

            if valid_options and user_input.lower() not in [v.lower() for v in valid_options]:
                print(f"{Colors.RED}Invalid option. Choose from: {', '.join(valid_options)}{Colors.END}")
                continue

            return user_input.lower() if valid_options else user_input
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Operation cancelled.{Colors.END}")
            return None

def get_number(prompt, default, min_val=1, max_val=10000):
    """Get numeric input with validation."""
    while True:
        try:
            user_input = input(f"{Colors.YELLOW}{prompt} (default: {default}): {Colors.END}").strip()
            if not user_input:
                return default
            value = int(user_input)
            if min_val <= value <= max_val:
                return value
            print(f"{Colors.RED}Please enter a number between {min_val} and {max_val}{Colors.END}")
        except ValueError:
            print(f"{Colors.RED}Please enter a valid number{Colors.END}")
        except KeyboardInterrupt:
            return default

def confirm(prompt, default=True):
    """Get yes/no confirmation."""
    default_str = "Y/n" if default else "y/N"
    while True:
        try:
            response = input(f"{Colors.YELLOW}{prompt} [{default_str}]: {Colors.END}").strip().lower()
            if not response:
                return default
            if response in ['y', 'yes']:
                return True
            if response in ['n', 'no']:
                return False
            print(f"{Colors.RED}Please enter 'y' or 'n'{Colors.END}")
        except KeyboardInterrupt:
            return False

def run_command(cmd, description, show_output=True):
    """Run a command and return success status."""
    print(f"\n{Colors.DIM}$ {' '.join(cmd)}{Colors.END}\n")

    start_time = time.time()
    try:
        if show_output:
            result = subprocess.run(cmd, check=False)
            success = result.returncode == 0
        else:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            success = result.returncode == 0
            if not success:
                print(f"{Colors.RED}{result.stderr}{Colors.END}")

        elapsed = time.time() - start_time

        if success:
            print_success(f"{description} completed in {elapsed:.1f}s")
        else:
            print_error(f"{description} failed (exit code: {result.returncode})")

        return success, elapsed
    except Exception as e:
        print_error(f"Error: {e}")
        return False, 0

def wait_for_continue():
    """Wait for user to press Enter to continue."""
    input(f"\n{Colors.CYAN}Press Enter to continue...{Colors.END}")


class InteractiveWorkflow:
    """Step-by-step interactive workflow manager."""

    def __init__(self):
        self.config = {
            'personas': 10,
            'records': 10,
            'interviews': 10,
            'provider': 'anthropic',
            'model': None,
            'protocol': 'Script/interview_protocols/prenatal_care.json',
            'run_dir': None,
            'objective': None
        }
        self.stage_results = {}
        self.current_stage = 0

        # Define all stages
        self.stages = [
            ('Configuration', 'Set up workflow parameters', self.stage_configuration),
            ('Generate Personas', 'Create synthetic pregnant women profiles', self.stage_personas),
            ('Generate Health Records', 'Create FHIR-compliant medical records', self.stage_records),
            ('Match Personas to Records', 'Semantic matching with Hungarian algorithm', self.stage_matching),
            ('Conduct Interviews', 'AI-powered interview simulation', self.stage_interviews),
            ('Analyze Interviews', 'Extract insights and detect anomalies', self.stage_analysis),
            ('Validate Results', 'Quality checks and validation', self.stage_validation),
            ('Generate Academic Report', 'Create systematic research report', self.stage_report),
            ('Journal Selection', 'Recommend and format for publication', self.stage_journal),
            ('Summary', 'Review final results and outputs', self.stage_summary),
        ]

    def run(self):
        """Run the interactive workflow."""
        clear_screen()
        print_header("GRAVIDAS STEP-BY-STEP INTERACTIVE WORKFLOW")

        print(f"""
{Colors.CYAN}Welcome to the GRAVIDAS interactive workflow!{Colors.END}

This wizard will guide you through each stage of the research pipeline:

  1. Configure workflow parameters
  2. Generate synthetic personas
  3. Generate FHIR health records
  4. Match personas to records
  5. Conduct AI-powered interviews
  6. Analyze interview results
  7. Validate implementation
  8. Generate academic report
  9. Select journal and format paper

At each stage, you can:
  • Configure stage-specific options
  • Run the stage
  • Review results
  • Continue, skip, or go back
""")

        if not confirm("Ready to begin?"):
            print("\nWorkflow cancelled. Goodbye!")
            return

        # Run stages
        while self.current_stage < len(self.stages):
            stage_name, stage_desc, stage_func = self.stages[self.current_stage]

            clear_screen()
            print_stage_header(self.current_stage, stage_name, stage_desc)

            result = stage_func()

            if result == 'quit':
                print("\nWorkflow ended. Goodbye!")
                return
            elif result == 'back' and self.current_stage > 0:
                self.current_stage -= 1
            elif result == 'skip':
                print_warning(f"Skipping {stage_name}")
                self.current_stage += 1
            elif result == 'repeat':
                continue  # Repeat current stage
            else:
                self.current_stage += 1

        print_header("WORKFLOW COMPLETE")
        print_success("All stages completed successfully!")

    def stage_configuration(self):
        """Configure workflow parameters."""
        print(f"{Colors.BOLD}Select workflow scale:{Colors.END}\n")

        presets = {
            '1': ('Quick Test', '10 personas, 10 records, 5 interviews (~10 min)', 10, 10, 5),
            '2': ('Small Run', '25 personas, 25 records, 10 interviews (~30 min)', 25, 25, 10),
            '3': ('Medium Run', '50 personas, 50 records, 20 interviews (~1.5 hrs)', 50, 50, 20),
            '4': ('Standard Run', '100 personas, 100 records, 50 interviews (~3 hrs)', 100, 100, 50),
            '5': ('Custom', 'Enter your own values', None, None, None),
        }

        for key, (name, desc, _, _, _) in presets.items():
            print(f"  {Colors.GREEN}[{key}]{Colors.END} {Colors.BOLD}{name}{Colors.END} - {desc}")

        choice = get_input("\nSelect scale", ['1', '2', '3', '4', '5'], '1')
        if choice is None:
            return 'quit'

        if choice == '5':
            self.config['personas'] = get_number("Number of personas", 100)
            self.config['records'] = get_number("Number of health records", self.config['personas'])
            self.config['interviews'] = get_number("Number of interviews", min(50, self.config['personas']))
        else:
            _, _, p, r, i = presets[choice]
            self.config['personas'] = p
            self.config['records'] = r
            self.config['interviews'] = i

        # Select provider
        print(f"\n{Colors.BOLD}Select AI Provider:{Colors.END}\n")
        providers = {
            '1': ('Anthropic Claude', 'Best quality, recommended'),
            '2': ('OpenAI GPT', 'Fast, cost-effective'),
        }
        print_menu(providers)

        provider_choice = get_input("\nSelect provider", ['1', '2'], '1')
        self.config['provider'] = 'anthropic' if provider_choice == '1' else 'openai'

        # Publication objective
        print(f"\n{Colors.BOLD}Publication Objective (for journal selection):{Colors.END}")
        print("  Examples: 'healthcare management', 'clinical practice', 'health policy'\n")

        objective = get_input("Enter objective (optional)", default="")
        if objective:
            self.config['objective'] = objective

        # Create run directory
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.config['run_dir'] = Path(f"archive/run_{timestamp}")
        self.config['run_dir'].mkdir(parents=True, exist_ok=True)

        # Create subdirectories
        for subdir in ['data/personas', 'data/health_records', 'data/matched',
                       'data/interviews', 'data/analysis', 'data/validation',
                       'outputs', 'logs', 'config']:
            (self.config['run_dir'] / subdir).mkdir(parents=True, exist_ok=True)

        # Summary
        print(f"\n{Colors.BOLD}Configuration Summary:{Colors.END}")
        print(f"  Personas:    {self.config['personas']}")
        print(f"  Records:     {self.config['records']}")
        print(f"  Interviews:  {self.config['interviews']}")
        print(f"  Provider:    {self.config['provider'].title()}")
        print(f"  Output Dir:  {self.config['run_dir']}")
        if self.config['objective']:
            print(f"  Objective:   {self.config['objective']}")

        wait_for_continue()
        return 'next'

    def stage_personas(self):
        """Generate synthetic personas."""
        print(f"This stage will generate {self.config['personas']} synthetic pregnant women profiles.")
        print(f"Output: {self.config['run_dir']}/data/personas/\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Use existing data'),
            'b': ('Back', 'Return to configuration'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        # Run stage
        cmd = [
            'python', 'scripts/01b_generate_personas.py',
            '--count', str(self.config['personas']),
            '--output', str(self.config['run_dir'] / 'data/personas')
        ]

        success, elapsed = run_command(cmd, "Persona generation")
        self.stage_results['personas'] = {'success': success, 'time': elapsed}

        if success:
            # Show sample output
            personas_file = self.config['run_dir'] / 'data/personas/personas.json'
            if personas_file.exists():
                try:
                    with open(personas_file) as f:
                        data = json.load(f)
                    print(f"\n{Colors.BOLD}Sample Output:{Colors.END}")
                    print(f"  Generated {len(data)} personas")
                    if data:
                        sample = data[0]
                        print(f"  Sample: {sample.get('name', 'N/A')}, Age: {sample.get('age', 'N/A')}")
                except:
                    pass

        wait_for_continue()
        return 'next' if success else self._handle_failure("Persona generation")

    def stage_records(self):
        """Generate health records."""
        print(f"This stage will generate {self.config['records']} FHIR-compliant health records.")
        print(f"Output: {self.config['run_dir']}/data/health_records/\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Use existing data'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        cmd = [
            'python', 'scripts/02_generate_health_records.py',
            '--count', str(self.config['records']),
            '--output', str(self.config['run_dir'] / 'data/health_records')
        ]

        success, elapsed = run_command(cmd, "Health record generation")
        self.stage_results['records'] = {'success': success, 'time': elapsed}

        wait_for_continue()
        return 'next' if success else self._handle_failure("Health record generation")

    def stage_matching(self):
        """Match personas to records."""
        print("This stage matches personas to health records using semantic similarity.")
        print(f"Output: {self.config['run_dir']}/data/matched/\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Use existing matches'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        personas_file = self.config['run_dir'] / 'data/personas/personas.json'
        records_file = self.config['run_dir'] / 'data/health_records/health_records.json'

        cmd = [
            'python', 'scripts/03_match_personas_records_enhanced.py',
            '--personas', str(personas_file),
            '--records', str(records_file),
            '--output', str(self.config['run_dir'] / 'data/matched')
        ]

        success, elapsed = run_command(cmd, "Persona-record matching")
        self.stage_results['matching'] = {'success': success, 'time': elapsed}

        if success:
            # Show matching stats
            stats_file = self.config['run_dir'] / 'data/matched/matching_statistics.json'
            if stats_file.exists():
                try:
                    with open(stats_file) as f:
                        stats = json.load(f)
                    print(f"\n{Colors.BOLD}Matching Results:{Colors.END}")
                    print(f"  Total matches: {stats.get('total_matches', 'N/A')}")
                    print(f"  Average score: {stats.get('average_score', 'N/A'):.3f}")
                except:
                    pass

        wait_for_continue()
        return 'next' if success else self._handle_failure("Matching")

    def stage_interviews(self):
        """Conduct interviews."""
        print(f"This stage will conduct {self.config['interviews']} AI-powered interviews.")
        print(f"Provider: {self.config['provider'].title()}")
        print(f"Output: {self.config['run_dir']}/data/interviews/\n")

        print(f"{Colors.YELLOW}Note: This is the most time-consuming stage (~2 min per interview).{Colors.END}\n")

        options = {
            'r': ('Run this stage', ''),
            'c': ('Change count', 'Modify number of interviews'),
            's': ('Skip', 'Use existing interviews'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 'c', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'
        elif choice == 'c':
            self.config['interviews'] = get_number("Number of interviews", self.config['interviews'])
            return 'repeat'

        matched_file = self.config['run_dir'] / 'data/matched/matched_personas.json'

        cmd = [
            'python', 'scripts/04_conduct_interviews.py',
            '--protocol', self.config['protocol'],
            '--count', str(self.config['interviews']),
            '--matched', str(matched_file),
            '--output', str(self.config['run_dir'] / 'data/interviews'),
            '--provider', self.config['provider']
        ]

        success, elapsed = run_command(cmd, "Interview simulation")
        self.stage_results['interviews'] = {'success': success, 'time': elapsed}

        wait_for_continue()
        return 'next' if success else self._handle_failure("Interview simulation")

    def stage_analysis(self):
        """Analyze interviews."""
        print("This stage analyzes interview data and extracts insights.")
        print(f"Output: {self.config['run_dir']}/data/analysis/\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Use existing analysis'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        cmd = [
            'python', 'scripts/analyze_interviews.py',
            '--input', str(self.config['run_dir'] / 'data/interviews'),
            '--output', str(self.config['run_dir'] / 'data/analysis'),
            '--matched', str(self.config['run_dir'] / 'data/matched/matched_personas.json'),
            '--export-json', '--export-csv'
        ]

        success, elapsed = run_command(cmd, "Interview analysis")
        self.stage_results['analysis'] = {'success': success, 'time': elapsed}

        wait_for_continue()
        return 'next' if success else self._handle_failure("Analysis")

    def stage_validation(self):
        """Validate results."""
        print("This stage performs quality validation checks.")
        print(f"Output: {self.config['run_dir']}/data/validation/\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Skip validation'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        cmd = [
            'python', 'scripts/test_semantic_implementation.py',
            '--personas', str(self.config['run_dir'] / 'data/personas/personas.json'),
            '--records', str(self.config['run_dir'] / 'data/health_records/health_records.json'),
            '--output', str(self.config['run_dir'] / 'data/validation')
        ]

        success, elapsed = run_command(cmd, "Validation")
        self.stage_results['validation'] = {'success': success, 'time': elapsed}

        wait_for_continue()
        return 'next'  # Continue even if validation has warnings

    def stage_report(self):
        """Generate academic report."""
        print("This stage generates a systematic academic report from the research data.")
        print(f"Output: {self.config['run_dir']}/outputs/academic_report.md\n")

        options = {
            'r': ('Run this stage', ''),
            's': ('Skip', 'Skip report generation'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        report_output = self.config['run_dir'] / 'outputs/academic_report.md'

        cmd = [
            'python', 'scripts/06_generate_academic_report.py',
            '--provider', self.config['provider'],
            '--interviews', str(self.config['run_dir'] / 'data/interviews'),
            '--analysis', str(self.config['run_dir'] / 'data/analysis/interview_analysis.json'),
            '--output', str(report_output)
        ]

        success, elapsed = run_command(cmd, "Academic report generation")
        self.stage_results['report'] = {'success': success, 'time': elapsed}

        if success and report_output.exists():
            print(f"\n{Colors.GREEN}Report generated: {report_output}{Colors.END}")
            if confirm("\nWould you like to preview the report?", default=False):
                # Show first 30 lines
                with open(report_output) as f:
                    lines = f.readlines()[:30]
                print(f"\n{Colors.DIM}{''.join(lines)}{Colors.END}")
                print(f"{Colors.DIM}... (truncated){Colors.END}")

        wait_for_continue()
        return 'next' if success else self._handle_failure("Report generation")

    def stage_journal(self):
        """Journal selection and paper formatting."""
        print("This stage recommends suitable journals and formats your paper.")
        print(f"Output: {self.config['run_dir']}/outputs/formatted_paper.md\n")

        options = {
            'r': ('Run with auto-select', 'Automatically select best journal'),
            'i': ('Run interactive', 'Choose journal from recommendations'),
            's': ('Skip', 'Skip journal selection'),
            'b': ('Back', 'Return to previous stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 'i', 's', 'b', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'b':
            return 'back'
        elif choice == 's':
            return 'skip'

        report_path = self.config['run_dir'] / 'outputs/academic_report.md'
        paper_output = self.config['run_dir'] / 'outputs/formatted_paper.md'

        cmd = [
            'python', 'scripts/07_journal_selector.py',
            '--report', str(report_path),
            '--output', str(paper_output),
            '--provider', self.config['provider']
        ]

        if choice == 'r':
            cmd.append('--auto-select')

        if self.config['objective']:
            cmd.extend(['--objective', self.config['objective']])

        success, elapsed = run_command(cmd, "Journal selection")
        self.stage_results['journal'] = {'success': success, 'time': elapsed}

        wait_for_continue()
        return 'next' if success else self._handle_failure("Journal selection")

    def stage_summary(self):
        """Show final summary."""
        print_header("WORKFLOW SUMMARY")

        # Show stage results
        print(f"{Colors.BOLD}Stage Results:{Colors.END}\n")

        total_time = 0
        successful = 0

        for i, (name, _, _) in enumerate(self.stages[1:-1], 1):  # Skip config and summary
            stage_key = name.lower().replace(' ', '_').replace('-', '_')
            result = self.stage_results.get(stage_key, {})

            status = "✓ Success" if result.get('success') else "⊘ Skipped" if not result else "✗ Failed"
            time_str = f"{result.get('time', 0):.1f}s" if result.get('time') else "-"

            color = Colors.GREEN if result.get('success') else Colors.YELLOW if not result else Colors.RED
            print(f"  {color}{i}. {name:<30} {status:<15} {time_str}{Colors.END}")

            if result.get('success'):
                successful += 1
                total_time += result.get('time', 0)

        print(f"\n{Colors.BOLD}Summary:{Colors.END}")
        print(f"  Total stages completed: {successful}/{len(self.stages) - 2}")
        print(f"  Total time: {total_time/60:.1f} minutes")

        # Show output locations
        print(f"\n{Colors.BOLD}Output Locations:{Colors.END}")
        print(f"  Archive:        {self.config['run_dir']}")
        print(f"  Personas:       {self.config['run_dir']}/data/personas/")
        print(f"  Health Records: {self.config['run_dir']}/data/health_records/")
        print(f"  Interviews:     {self.config['run_dir']}/data/interviews/")
        print(f"  Analysis:       {self.config['run_dir']}/data/analysis/")
        print(f"  Report:         {self.config['run_dir']}/outputs/academic_report.md")
        print(f"  Paper:          {self.config['run_dir']}/outputs/formatted_paper.md")

        wait_for_continue()
        return 'next'

    def _handle_failure(self, stage_name):
        """Handle stage failure."""
        print(f"\n{Colors.BOLD}Stage failed. What would you like to do?{Colors.END}\n")

        options = {
            'r': ('Retry', 'Run the stage again'),
            'c': ('Continue', 'Skip to next stage'),
            'q': ('Quit', 'Exit workflow'),
        }
        print_menu(options)

        choice = get_input("\nSelect action", ['r', 'c', 'q'], 'r')

        if choice == 'q':
            return 'quit'
        elif choice == 'c':
            return 'next'
        else:
            return 'repeat'


def main():
    """Main entry point."""
    try:
        workflow = InteractiveWorkflow()
        workflow.run()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Workflow interrupted by user.{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}Error: {e}{Colors.END}")
        sys.exit(1)


if __name__ == '__main__':
    main()
