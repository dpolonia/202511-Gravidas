#!/usr/bin/env python3
"""
GRAVIDAS COMPLETE WORKFLOW RUNNER
==================================
Executes the entire end-to-end pipeline for synthetic pregnancy data generation.

Usage:
    python run_complete_workflow.py
    python run_complete_workflow.py --personas 50 --provider anthropic
    python run_complete_workflow.py --quick-test
    python run_complete_workflow.py --help

Stages:
    1. Generate Personas (synthetic pregnant women)
    2. Generate Health Records (FHIR medical data)
    3. Match Personas to Records (semantic matching)
    4. Conduct Interviews (AI-powered interviews)
    5. Analyze Interviews (extract insights)
    6. Validate Implementation (quality checks)
"""

import sys
import os
import argparse
import subprocess
import time
from datetime import datetime
from pathlib import Path
import json

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}[Stage {stage_num}/6] {stage_name}{Colors.ENDC}")
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
    """Run the complete workflow."""
    
    start_time = time.time()
    results = {}
    
    print_header("GRAVIDAS COMPLETE WORKFLOW")
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Provider: {args.provider}")
    print(f"Model: {args.model or 'default'}")
    print(f"Personas: {args.personas}")
    print(f"Health Records: {args.records}")
    
    # Check prerequisites
    if not check_prerequisites():
        print_error("Prerequisites check failed. Please fix the issues above.")
        return False
    
    # Stage 1: Generate Personas
    print_stage(1, "Generate Personas", "Creating synthetic pregnant women profiles")
    cmd = [
        'python', 'scripts/01b_generate_personas.py',
        '--count', str(args.personas),
        '--output', 'data/personas'
    ]
    success, elapsed, output = run_command(cmd, "Generate Personas", timeout=600)
    results['stage1_personas'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    if not success and not args.continue_on_error:
        print_error("Stage 1 failed. Aborting workflow.")
        return False
    
    # Stage 2: Generate Health Records
    print_stage(2, "Generate Health Records", "Creating synthetic FHIR medical records")
    cmd = [
        'python', 'scripts/02_generate_health_records.py',
        '--count', str(args.records),
        '--output', 'data/health_records'
    ]
    success, elapsed, output = run_command(cmd, "Generate Health Records", timeout=1200)
    results['stage2_records'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    if not success and not args.continue_on_error:
        print_error("Stage 2 failed. Aborting workflow.")
        return False
    
    # Stage 3: Match Personas to Records
    print_stage(3, "Match Personas to Records", "Semantic matching using Hungarian algorithm")
    cmd = [
        'python', 'scripts/03_match_personas_records_enhanced.py',
        '--personas', 'data/personas/personas.json',
        '--records', 'data/health_records/health_records.json',
        '--output', 'data/matched'
    ]
    success, elapsed, output = run_command(cmd, "Match Personas to Records", timeout=300)
    results['stage3_matching'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    if not success and not args.continue_on_error:
        print_error("Stage 3 failed. Aborting workflow.")
        return False
    
    # Stage 4: Conduct Interviews
    print_stage(4, "Conduct Interviews", f"AI-powered interviews using {args.provider}")
    cmd = [
        'python', 'scripts/04_conduct_interviews.py',
        '--protocol', args.protocol,
        '--count', str(args.interviews),
        '--matched', 'data/matched/matched_personas.json',
        '--output', 'data/interviews',
        '--provider', args.provider
    ]
    if args.model:
        cmd.extend(['--model', args.model])
    
    success, elapsed, output = run_command(cmd, "Conduct Interviews", timeout=3600)
    results['stage4_interviews'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    if not success and not args.continue_on_error:
        print_error("Stage 4 failed. Aborting workflow.")
        return False
    
    # Stage 5: Analyze Interviews
    print_stage(5, "Analyze Interviews", "Extracting insights and detecting anomalies")
    cmd = [
        'python', 'scripts/analyze_interviews.py',
        '--export-json',
        '--export-csv',
        '--show-details',
        '--show-clinical',
        '--show-anomalies'
    ]
    success, elapsed, output = run_command(cmd, "Analyze Interviews", timeout=300)
    results['stage5_analysis'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    if not success and not args.continue_on_error:
        print_error("Stage 5 failed. Aborting workflow.")
        return False
    
    # Stage 6: Validate Implementation
    print_stage(6, "Validate Implementation", "Quality checks and semantic tree validation")
    cmd = [
        'python', 'scripts/test_semantic_implementation.py',
        '--personas', 'data/personas/personas.json',
        '--records', 'data/health_records/health_records.json',
        '--output', 'data/validation'
    ]
    success, elapsed, output = run_command(cmd, "Validate Implementation", timeout=300)
    results['stage6_validation'] = {
        'success': success,
        'time': elapsed,
        'command': ' '.join(cmd)
    }
    
    # Print Summary
    total_time = time.time() - start_time
    print_workflow_summary(results, total_time, args)
    
    # Save results
    save_workflow_results(results, total_time, args)
    
    return all(stage['success'] for stage in results.values())

def print_workflow_summary(results, total_time, args):
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
    
    print(f"\n{Colors.BOLD}Output Locations:{Colors.ENDC}")
    print(f"  Personas:      data/personas/personas.json")
    print(f"  Health Records: data/health_records/health_records.json")
    print(f"  Matched Pairs:  data/matched/matched_personas.json")
    print(f"  Interviews:     data/interviews/")
    print(f"  Analysis:       data/analysis/interview_summary.csv")
    print(f"  Validation:     data/validation/")

def save_workflow_results(results, total_time, args):
    """Save workflow results to JSON file."""
    output_dir = Path('outputs')
    output_dir.mkdir(exist_ok=True)
    
    report = {
        'workflow': 'Gravidas Complete Pipeline',
        'timestamp': datetime.now().isoformat(),
        'total_time_seconds': total_time,
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
    
    output_file = output_dir / 'complete_workflow_report.json'
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)
    
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
    
    args = parser.parse_args()
    
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
