#!/usr/bin/env python3
"""
GRAVIDAS COMPLETE WORKFLOW RUNNER
==================================
Executes the entire end-to-end pipeline for synthetic pregnancy data generation.

All runs are automatically archived to timestamped directories in archive/.
A run summary with configuration and results is generated after each run.

Usage:
    python run_complete_workflow.py
    python run_complete_workflow.py --personas 50 --provider anthropic
    python run_complete_workflow.py --quick-test
    python run_complete_workflow.py --help
    python run_complete_workflow.py --list-runs  # Show previous runs

Stages:
    1. Generate Personas (synthetic pregnant women)
    2. Generate Health Records (FHIR medical data)
    3. Match Personas to Records (semantic matching)
    4. Conduct Interviews (AI-powered interviews)
    5. Analyze Interviews (extract insights)
    6. Validate Implementation (quality checks)
    7. Generate Academic Report (LLM-based systematic report)

Archive Structure:
    archive/
    ├── run_YYYYMMDD_HHMMSS/
    │   ├── data/
    │   │   ├── personas/
    │   │   ├── health_records/
    │   │   ├── matched/
    │   │   ├── interviews/
    │   │   ├── analysis/
    │   │   └── validation/
    │   ├── outputs/
    │   ├── logs/
    │   ├── config/
    │   └── RUN_SUMMARY.md
    ├── RUN_SUMMARY.md        # Latest run summary
    └── run_history.json      # All runs history
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
import json

# Add scripts directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from scripts.utils.archive_manager import ArchiveManager

# ANSI color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def print_header(text):
    """Print a formatted header."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{text.center(80)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*80}{Colors.ENDC}\n")

def print_stage(stage_num, stage_name, description):
    """Print stage information."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}[Stage {stage_num}/7] {stage_name}{Colors.ENDC}")
    print(f"{Colors.CYAN}{description}{Colors.ENDC}")
    print(f"{Colors.CYAN}{'-'*80}{Colors.ENDC}")

def print_success(message):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {message}{Colors.ENDC}")

def print_error(message):
    """Print error message."""
    print(f"{Colors.RED}✗ {message}{Colors.ENDC}")

def print_warning(message):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.ENDC}")

def print_info(message):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ {message}{Colors.ENDC}")

def run_command(command, stage_name, timeout=600):
    """
    Run a shell command and capture output.
    
    Args:
        command: Command to run (string or list)
        stage_name: Name of the stage for logging
        timeout: Maximum execution time in seconds
        
    Returns:
        tuple: (success: bool, elapsed_time: float, output: str)
    """
    start_time = time.time()
    
    try:
        if isinstance(command, str):
            command = command.split()
        
        print_info(f"Executing: {' '.join(command)}")
        
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False
        )
        
        elapsed_time = time.time() - start_time
        
        if result.returncode == 0:
            print_success(f"Stage completed in {elapsed_time:.2f} seconds")
            return True, elapsed_time, result.stdout
        else:
            print_error(f"Stage failed with return code {result.returncode}")
            if result.stderr:
                print(f"{Colors.RED}Error output:{Colors.ENDC}")
                print(result.stderr[-500:])  # Last 500 chars of error
            return False, elapsed_time, result.stderr
            
    except subprocess.TimeoutExpired:
        elapsed_time = time.time() - start_time
        print_error(f"Stage timed out after {elapsed_time:.2f} seconds")
        return False, elapsed_time, "Timeout exceeded"
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print_error(f"Unexpected error: {str(e)}")
        return False, elapsed_time, str(e)

def check_prerequisites():
    """Check if all prerequisites are met."""
    print_stage(0, "Prerequisites Check", "Verifying system requirements")
    
    all_good = True
    
    # Check Python version
    if sys.version_info < (3, 9):
        print_error(f"Python 3.9+ required, found {sys.version_info.major}.{sys.version_info.minor}")
        all_good = False
    else:
        print_success(f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    
    # Check for required directories
    required_dirs = ['scripts', 'data', 'config', 'Script/interview_protocols']
    for dir_path in required_dirs:
        if Path(dir_path).exists():
            print_success(f"Directory exists: {dir_path}")
        else:
            print_error(f"Missing directory: {dir_path}")
            all_good = False
    
    # Check for .env file
    if Path('.env').exists():
        print_success("Environment file (.env) found")
    else:
        print_warning("No .env file found - API keys may not be configured")
    
    # Check for config file
    if Path('config/workflow_config.yaml').exists():
        print_success("Workflow configuration found")
    else:
        print_error("Missing config/workflow_config.yaml")
        all_good = False
    
    return all_good

def run_workflow(args):
    """Run the complete workflow with automatic archiving."""

    start_time = time.time()
    results = {}

    # Initialize archive manager
    archive = ArchiveManager(base_dir="archive")

    # Create run configuration
    run_config = {
        'provider': args.provider,
        'model': args.model,
        'personas': args.personas,
        'records': args.records,
        'interviews': args.interviews,
        'protocol': args.protocol,
        'continue_on_error': args.continue_on_error,
        'quick_test': args.quick_test
    }

    # Create archive run directory
    run_dir = archive.create_run(run_config)
    paths = archive.get_data_paths()

    print_header("GRAVIDAS COMPLETE WORKFLOW")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model or 'default'}")
    print(f"Personas: {args.personas}")
    print(f"Health Records: {args.records}")
    print(f"\n{Colors.CYAN}Run Directory: {run_dir}{Colors.ENDC}")

    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix the issues above.")
        return False

    # Stage 1: Generate Personas
    print_stage(1, "Generate Personas", "Creating synthetic pregnant women profiles")
    cmd = [
        'python', 'scripts/01b_generate_personas.py',
        '--count', str(args.personas),
        '--output', str(paths['personas'])
    ]
    success, elapsed, output = run_command(cmd, "Generate Personas", timeout=600)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['personas'])
    }
    results['stage1_personas'] = stage_result
    archive.record_stage_result('stage1_personas', stage_result)

    if not success and not args.continue_on_error:
        print_error("Stage 1 failed. Aborting workflow.")
        total_time = time.time() - start_time
        archive.finalize_run(False, total_time)
        return False

    # Stage 2: Generate Health Records
    print_stage(2, "Generate Health Records", "Creating synthetic FHIR medical records")
    cmd = [
        'python', 'scripts/02_generate_health_records.py',
        '--count', str(args.records),
        '--output', str(paths['health_records'])
    ]
    success, elapsed, output = run_command(cmd, "Generate Health Records", timeout=1200)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['health_records'])
    }
    results['stage2_records'] = stage_result
    archive.record_stage_result('stage2_records', stage_result)

    if not success and not args.continue_on_error:
        print_error("Stage 2 failed. Aborting workflow.")
        total_time = time.time() - start_time
        archive.finalize_run(False, total_time)
        return False

    # Stage 3: Match Personas to Records
    print_stage(3, "Match Personas to Records", "Semantic matching using Hungarian algorithm")
    personas_file = paths['personas'] / 'personas.json'
    records_file = paths['health_records'] / 'health_records.json'
    cmd = [
        'python', 'scripts/03_match_personas_records_enhanced.py',
        '--personas', str(personas_file),
        '--records', str(records_file),
        '--output', str(paths['matched'])
    ]
    success, elapsed, output = run_command(cmd, "Match Personas to Records", timeout=300)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['matched'])
    }
    results['stage3_matching'] = stage_result
    archive.record_stage_result('stage3_matching', stage_result)

    if not success and not args.continue_on_error:
        print_error("Stage 3 failed. Aborting workflow.")
        total_time = time.time() - start_time
        archive.finalize_run(False, total_time)
        return False

    # Stage 4: Conduct Interviews
    print_stage(4, "Conduct Interviews", f"AI-powered interviews using {args.provider}")
    matched_file = paths['matched'] / 'matched_personas.json'
    cmd = [
        'python', 'scripts/04_conduct_interviews.py',
        '--protocol', args.protocol,
        '--count', str(args.interviews),
        '--matched', str(matched_file),
        '--output', str(paths['interviews']),
        '--provider', args.provider
    ]
    if args.model:
        cmd.extend(['--model', args.model])

    success, elapsed, output = run_command(cmd, "Conduct Interviews", timeout=3600)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['interviews'])
    }
    results['stage4_interviews'] = stage_result
    archive.record_stage_result('stage4_interviews', stage_result)

    if not success and not args.continue_on_error:
        print_error("Stage 4 failed. Aborting workflow.")
        total_time = time.time() - start_time
        archive.finalize_run(False, total_time)
        return False

    # Stage 5: Analyze Interviews
    print_stage(5, "Analyze Interviews", "Extracting insights and detecting anomalies")
    cmd = [
        'python', 'scripts/analyze_interviews.py',
        '--input', str(paths['interviews']),
        '--output', str(paths['analysis']),
        '--export-json',
        '--export-csv',
        '--show-details',
        '--show-clinical',
        '--show-anomalies'
    ]
    success, elapsed, output = run_command(cmd, "Analyze Interviews", timeout=300)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['analysis'])
    }
    results['stage5_analysis'] = stage_result
    archive.record_stage_result('stage5_analysis', stage_result)

    if not success and not args.continue_on_error:
        print_error("Stage 5 failed. Aborting workflow.")
        total_time = time.time() - start_time
        archive.finalize_run(False, total_time)
        return False

    # Stage 6: Validate Implementation
    print_stage(6, "Validate Implementation", "Quality checks and semantic tree validation")
    cmd = [
        'python', 'scripts/test_semantic_implementation.py',
        '--personas', str(personas_file),
        '--records', str(records_file),
        '--output', str(paths['validation'])
    ]
    success, elapsed, output = run_command(cmd, "Validate Implementation", timeout=300)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(paths['validation'])
    }
    results['stage6_validation'] = stage_result
    archive.record_stage_result('stage6_validation', stage_result)

    # Stage 7: Generate Academic Report
    print_stage(7, "Generate Academic Report", f"Creating systematic report using {args.provider}")
    report_output = paths['outputs'] / 'academic_report.md'
    cmd = [
        'python', 'scripts/06_generate_academic_report.py',
        '--provider', args.provider,
        '--interviews', str(paths['interviews']),
        '--analysis', str(paths['analysis'] / 'interview_analysis.json'),
        '--output', str(report_output)
    ]
    if args.model:
        cmd.extend(['--model', args.model])

    success, elapsed, output = run_command(cmd, "Generate Academic Report", timeout=600)
    stage_result = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd),
        'output_path': str(report_output)
    }
    results['stage7_report'] = stage_result
    archive.record_stage_result('stage7_report', stage_result)

    if not success:
        print_warning("Academic report generation failed, but workflow will complete.")

    # Calculate final results
    total_time = time.time() - start_time
    # Report generation failure shouldn't fail the whole workflow
    core_stages = ['stage1_personas', 'stage2_records', 'stage3_matching',
                   'stage4_interviews', 'stage5_analysis', 'stage6_validation']
    overall_success = all(results[s]['success'] for s in core_stages if s in results)

    # Finalize archive and generate summary
    summary_file = archive.finalize_run(overall_success, total_time)

    # Print Summary
    print_workflow_summary(results, total_time, args, run_dir)

    # Also save legacy results for backwards compatibility
    save_workflow_results(results, total_time, args, run_dir)

    print(f"\n{Colors.GREEN}Run archived to: {run_dir}{Colors.ENDC}")
    print(f"{Colors.GREEN}Run summary: {summary_file}{Colors.ENDC}")
    if results.get('stage7_report', {}).get('success'):
        print(f"{Colors.GREEN}Academic report: {report_output}{Colors.ENDC}")

    return overall_success

def print_workflow_summary(results, total_time, args, run_dir=None):
    """Print workflow execution summary."""
    print_header("WORKFLOW SUMMARY")

    successful = sum(1 for stage in results.values() if stage['success'])
    total_stages = len(results)

    print(f"{Colors.BOLD}Execution Summary:{Colors.ENDC}")
    print(f"  Total Time:        {total_time:.2f} seconds ({total_time/60:.1f} minutes)")
    print(f"  Stages Completed:  {successful}/{total_stages}")
    print(f"  Provider:          {args.provider}")
    print(f"  Model:             {args.model or 'default'}")
    print(f"  Personas:          {args.personas}")
    print(f"  Health Records:    {args.records}")
    print()

    print(f"{Colors.BOLD}Stage Results:{Colors.ENDC}")
    for stage_name, stage_info in results.items():
        status = f"{Colors.GREEN}✓ SUCCESS{Colors.ENDC}" if stage_info['success'] else f"{Colors.RED}✗ FAILED{Colors.ENDC}"
        print(f"  {stage_name:25} {status:20} ({stage_info['time']:.2f}s)")

    print()
    if successful == total_stages:
        print_success("All stages completed successfully!")
    else:
        print_warning(f"{total_stages - successful} stage(s) failed")

    # Show output locations (use run_dir if available)
    base_path = str(run_dir) if run_dir else "data"
    print(f"\n{Colors.BOLD}Output Locations:{Colors.ENDC}")
    if run_dir:
        print(f"  {Colors.CYAN}Archive Directory: {run_dir}{Colors.ENDC}")
        print(f"  Personas:       {run_dir}/data/personas/")
        print(f"  Health Records: {run_dir}/data/health_records/")
        print(f"  Matched Pairs:  {run_dir}/data/matched/")
        print(f"  Interviews:     {run_dir}/data/interviews/")
        print(f"  Analysis:       {run_dir}/data/analysis/")
        print(f"  Validation:     {run_dir}/data/validation/")
        print(f"  Run Summary:    {run_dir}/RUN_SUMMARY.md")
    else:
        print(f"  Personas:       data/personas/personas.json")
        print(f"  Health Records: data/health_records/health_records.json")
        print(f"  Matched Pairs:  data/matched/matched_personas.json")
        print(f"  Interviews:     data/interviews/")
        print(f"  Analysis:       data/analysis/interview_summary.csv")
        print(f"  Validation:     data/validation/")

def save_workflow_results(results, total_time, args, run_dir=None):
    """Save workflow results to JSON file."""
    # Save to archive directory if available, otherwise outputs/
    if run_dir:
        output_dir = Path(run_dir) / 'outputs'
    else:
        output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True, parents=True)

    report = {
        'workflow': 'Gravidas Complete Pipeline',
        'timestamp': datetime.now().isoformat(),
        'total_time_seconds': total_time,
        'run_directory': str(run_dir) if run_dir else None,
        'configuration': {
            'provider': args.provider,
            'model': args.model,
            'personas': args.personas,
            'records': args.records,
            'interviews': args.interviews,
            'protocol': args.protocol
        },
        'stages': results,
        'summary': {
            'total_stages': len(results),
            'successful_stages': sum(1 for s in results.values() if s['success']),
            'failed_stages': sum(1 for s in results.values() if not s['success'])
        }
    }

    output_file = output_dir / 'workflow_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2, default=str)

    print_info(f"Detailed report saved to: {output_file}")

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Run the complete Gravidas workflow end-to-end',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test with minimal data
  python run_complete_workflow.py --quick-test

  # Standard run with 100 personas
  python run_complete_workflow.py --personas 100

  # Use OpenAI instead of default Anthropic
  python run_complete_workflow.py --provider openai --model gpt-4o-mini

  # Continue even if a stage fails
  python run_complete_workflow.py --continue-on-error

  # Full production run
  python run_complete_workflow.py --personas 1000 --records 1000 --interviews 100

  # List previous runs
  python run_complete_workflow.py --list-runs

  # Cleanup old runs (keep last 5)
  python run_complete_workflow.py --cleanup-runs 5
        """
    )

    parser.add_argument('--personas', type=int, default=100,
                       help='Number of personas to generate (default: 100)')
    parser.add_argument('--records', type=int, default=100,
                       help='Number of health records to generate (default: 100)')
    parser.add_argument('--interviews', type=int, default=10,
                       help='Number of interviews to conduct (default: 10)')
    parser.add_argument('--provider', type=str, default='anthropic',
                       choices=['anthropic', 'openai', 'google', 'xai'],
                       help='AI provider to use (default: anthropic)')
    parser.add_argument('--model', type=str, default=None,
                       help='Specific model to use (default: provider default)')
    parser.add_argument('--protocol', type=str,
                       default='Script/interview_protocols/prenatal_care.json',
                       help='Interview protocol to use')
    parser.add_argument('--continue-on-error', action='store_true',
                       help='Continue workflow even if a stage fails')
    parser.add_argument('--quick-test', action='store_true',
                       help='Run quick test with minimal data (10 personas, 10 records, 3 interviews)')

    # Archive management arguments
    parser.add_argument('--list-runs', action='store_true',
                       help='List previous workflow runs')
    parser.add_argument('--cleanup-runs', type=int, metavar='N',
                       help='Cleanup old runs, keeping only the last N')

    args = parser.parse_args()

    # Handle archive management commands
    if args.list_runs:
        archive = ArchiveManager(base_dir="archive")
        runs = archive.list_runs(limit=20)
        if not runs:
            print("No previous runs found.")
        else:
            print_header("PREVIOUS WORKFLOW RUNS")
            print(f"{'Run ID':<25} {'Status':<10} {'Duration':<12} {'Personas':<10} {'Provider':<12}")
            print("-" * 75)
            for run in runs:
                status = f"{Colors.GREEN}SUCCESS{Colors.ENDC}" if run.get('success') else f"{Colors.RED}FAILED{Colors.ENDC}"
                duration = f"{run.get('total_time_seconds', 0):.1f}s"
                config = run.get('config_summary', {})
                personas = config.get('personas', 'N/A')
                provider = config.get('provider', 'N/A')
                print(f"{run.get('run_id', 'N/A'):<25} {status:<20} {duration:<12} {personas:<10} {provider:<12}")
            print()
            print(f"Run summaries are in: archive/RUN_SUMMARY.md (latest)")
            print(f"Full history: archive/run_history.json")
        sys.exit(0)

    if args.cleanup_runs:
        archive = ArchiveManager(base_dir="archive")
        print(f"Cleaning up old runs, keeping {args.cleanup_runs} most recent...")
        archive.cleanup_old_runs(keep_count=args.cleanup_runs)
        print_success("Cleanup complete.")
        sys.exit(0)

    # Apply quick-test preset
    if args.quick_test:
        args.personas = 10
        args.records = 10
        args.interviews = 3
        print_info("Quick test mode: 10 personas, 10 records, 3 interviews")

    # Run workflow
    try:
        success = run_workflow(args)
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print_error("\n\nWorkflow interrupted by user")
        sys.exit(130)
    except Exception as e:
        print_error(f"\n\nUnexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
