#!/usr/bin/env python3
"""
Synthetic Gravidas Pipeline - End-to-End Orchestrator v1.0.1

🚀 Complete pipeline automation with user choice for:
   - Sample size (1-10,000 personas and interviews)
   - AI model and provider selection
   - Cost optimization and batch processing
   - Real-time progress monitoring

Usage:
    python run_pipeline.py                    # Interactive mode
    python run_pipeline.py --count 100        # Quick run with 100 interviews
    python run_pipeline.py --help             # Show all options

Features:
   ✅ Complete end-to-end automation (5 stages)
   ✅ 60+ AI models from 15+ providers (OpenAI, Anthropic, Google, Azure, AWS, etc.)
   ✅ Dynamic cost estimation with batch mode savings
   ✅ Progress tracking and error recovery
   ✅ Scientific reproducibility with fixed seeds
   ✅ Comprehensive validation and quality checks

Author: Synthetic Gravidas Research Team
Version: 1.0.1 (2025-11-07)
"""

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
import subprocess
import logging

# Import shared modules
try:
    import yaml
    from dotenv import load_dotenv
    import pandas as pd
    import numpy as np
except ImportError as e:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install python-dotenv pyyaml pandas numpy")
    print(f"Missing: {e}")
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

# Import our model database and utilities
sys.path.append(str(Path(__file__).parent))

from scripts.interactive_interviews import (
    clear_screen, 
    print_header, 
    print_section,
    format_time,
    get_api_keys,
    load_env_file,
    load_config
)
from scripts.enhanced_models_database import (
    ENHANCED_MODELS_DATABASE,
    get_available_providers,
    get_provider_models,
    get_model_info,
    calculate_cost,
    get_recommended_models,
    PROVIDER_AUTH_REQUIREMENTS
)
from scripts.universal_ai_client import (
    AIResponse,
    BaseAIClient
)

# Pipeline configuration
PIPELINE_VERSION = "1.0.1"
PIPELINE_STAGES = [
    {
        "id": 1,
        "name": "Persona Generation",
        "script": "scripts/01b_generate_personas.py",
        "description": "Generate synthetic personas with AI",
        "output": "data/personas/personas.json",
        "required": True
    },
    {
        "id": 2,
        "name": "Health Record Generation", 
        "script": "scripts/02_generate_health_records.py",
        "description": "Create FHIR health records via Synthea",
        "output": "data/health_records/*.json",
        "required": True
    },
    {
        "id": 3,
        "name": "Optimal Matching",
        "script": "scripts/03_match_personas_records.py", 
        "description": "Match personas to health records",
        "output": "data/matched/matched_personas.json",
        "required": True
    },
    {
        "id": 4,
        "name": "AI Interviews",
        "script": "scripts/04_conduct_interviews.py",
        "description": "Conduct structured interviews",
        "output": "data/interviews/*.json", 
        "required": True
    },
    {
        "id": 5,
        "name": "Analysis & Export",
        "script": "scripts/analyze_interviews.py",
        "description": "Generate comprehensive analysis",
        "output": "data/analysis/interview_summary.csv",
        "required": True
    }
]

# Now using the comprehensive enhanced models database from AImodels.csv
# This includes 15+ providers with 60+ models and accurate pricing

# Average tokens per interview (updated based on v1.0 data)
AVG_INPUT_TOKENS_PER_INTERVIEW = 3200
AVG_OUTPUT_TOKENS_PER_INTERVIEW = 1800

# Helper function for backward compatibility with calculate_cost_and_time
def calculate_cost_and_time(model_info: Dict[str, Any], sample_size: int, use_batch: bool = False) -> Tuple[float, int, bool]:
    """Calculate cost and time for a given model and sample size (backward compatibility)."""
    input_tokens = sample_size * AVG_INPUT_TOKENS_PER_INTERVIEW
    output_tokens = sample_size * AVG_OUTPUT_TOKENS_PER_INTERVIEW
    
    cost = calculate_cost(model_info, input_tokens, output_tokens, use_batch)
    time_min = max(10, sample_size // 10)  # Simplified time estimation
    batch_available = model_info.get('batch_available', False)
    
    return cost, time_min, batch_available

class PipelineOrchestrator:
    """Main pipeline orchestrator for end-to-end automation."""
    
    def __init__(self):
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.output_dir = Path(f"pipeline_runs/{self.session_id}")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup logging
        self.setup_logging()
        
        # Configuration
        self.config = {}
        self.api_keys = {}
        
    def setup_logging(self):
        """Setup comprehensive logging."""
        log_file = self.output_dir / "pipeline.log"
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler(sys.stdout)
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        self.logger.info(f"Pipeline session {self.session_id} started")
        
    def print_welcome(self):
        """Print welcome screen with pipeline information."""
        clear_screen()
        print_header("🚀 SYNTHETIC GRAVIDAS PIPELINE v1.0.1")
        
        print("Complete End-to-End Automation System")
        print()
        print("✨ NEW in v1.0.1:")
        print("   • Full pipeline orchestration with one command")
        print("   • 15+ AI providers with 60+ models from AImodels.csv")
        print("   • Universal AI client for seamless provider switching")
        print("   • Dynamic sample size selection (1-10,000)")
        print("   • Real-time cost estimation and optimization")
        print("   • Progress monitoring and error recovery")
        print("   • Batch API integration for ~50% cost savings")
        print()
        print("📊 Pipeline Stages:")
        for stage in PIPELINE_STAGES:
            print(f"   {stage['id']}. {stage['name']} - {stage['description']}")
        print()
        print(f"Session ID: {self.session_id}")
        print(f"Output Directory: {self.output_dir}")
        print()
        input("Press Enter to begin configuration...")
        
    def get_pipeline_config(self) -> Dict[str, Any]:
        """Interactive pipeline configuration."""
        clear_screen()
        print_header("PIPELINE CONFIGURATION")
        
        config = {}
        
        # Sample size selection
        print("📊 Sample Size Configuration")
        print()
        print("Choose your study size:")
        print("   1. Quick Test (10 personas + interviews) - ~$2, 5 minutes")
        print("   2. Pilot Study (100 personas + interviews) - ~$15, 30 minutes")  
        print("   3. Full Study (1,000 personas + interviews) - ~$150, 4 hours")
        print("   4. Large Study (5,000 personas + interviews) - ~$750, 18 hours")
        print("   5. Custom size")
        print()
        
        while True:
            choice = input("Select study size (1-5): ").strip()
            
            if choice == '1':
                config['sample_size'] = 10
                break
            elif choice == '2':
                config['sample_size'] = 100
                break
            elif choice == '3':
                config['sample_size'] = 1000
                break
            elif choice == '4':
                config['sample_size'] = 5000
                break
            elif choice == '5':
                while True:
                    try:
                        size = int(input("Enter custom size (1-10000): ").strip())
                        if 1 <= size <= 10000:
                            config['sample_size'] = size
                            break
                        else:
                            print("   ✗ Please enter a number between 1 and 10,000")
                    except ValueError:
                        print("   ✗ Please enter a valid number")
                break
            else:
                print("   ✗ Invalid choice, please select 1-5")
        
        # API keys
        self.api_keys = get_api_keys()
        if not self.api_keys:
            print("\n⚠️  No API keys found!")
            print("Please configure at least one API key in .env file or config.yaml")
            print("See env.example for template.")
            sys.exit(1)
            
        config['api_keys'] = self.api_keys
        
        # Stage selection
        print(f"\n🔧 Pipeline Stages (for {config['sample_size']:,} samples)")
        print()
        print("Which stages would you like to run?")
        print("   1. Full pipeline (all 5 stages) - Complete automation")
        print("   2. Interviews only (stage 4+5) - Use existing data")
        print("   3. Custom stage selection")
        print()
        
        while True:
            stage_choice = input("Select pipeline mode (1-3): ").strip()
            
            if stage_choice == '1':
                config['stages'] = [1, 2, 3, 4, 5]
                break
            elif stage_choice == '2':
                config['stages'] = [4, 5]
                break
            elif stage_choice == '3':
                print("\nSelect stages to run:")
                selected_stages = []
                for stage in PIPELINE_STAGES:
                    choice = input(f"   Run {stage['name']}? (y/n): ").strip().lower()
                    if choice in ['y', 'yes']:
                        selected_stages.append(stage['id'])
                config['stages'] = selected_stages
                break
            else:
                print("   ✗ Invalid choice, please select 1-3")
        
        return config
    
    def select_ai_model(self, sample_size: int) -> Tuple[str, str, Dict[str, Any]]:
        """Interactive AI model selection with cost estimation."""
        clear_screen()
        print_header(f"AI MODEL SELECTION ({sample_size:,} interviews)")
        
        # Filter available providers using enhanced database
        available_providers = {}
        for provider_id, provider_data in ENHANCED_MODELS_DATABASE.items():
            if provider_id in self.api_keys:
                available_providers[provider_id] = provider_data
        
        if not available_providers:
            print("✗ No API keys available for AI providers!")
            sys.exit(1)
        
        print("Available AI Models:")
        print()
        print(f"{'#':<3} {'Model':<30} {'Provider':<15} {'Quality':<12} {'Est. Cost':<12} {'Context':<10}")
        print("─" * 95)
        
        all_models = []
        for provider_id, provider_info in available_providers.items():
            for model_id, model_info in provider_info['models'].items():
                cost, time_min, batch_available = calculate_cost_and_time(
                    model_info, sample_size
                )
                
                all_models.append({
                    'provider': provider_id,
                    'model_id': model_id,
                    'model_info': model_info,
                    'cost': cost,
                    'time_min': time_min,
                    'batch_available': batch_available
                })
        
        # Sort by cost
        all_models.sort(key=lambda x: x['cost'])
        
        for i, model in enumerate(all_models, 1):
            model_info = model['model_info']
            recommended = " ⭐" if model_info.get('recommended') else ""
            batch_badge = " 🔄" if model['batch_available'] else ""
            context_k = f"{model_info['context_window']//1000}K"
            
            print(f"{i:<3} {model_info['name']:<30} {ENHANCED_MODELS_DATABASE[model['provider']]['name']:<15} "
                  f"{model_info['quality']:<12} ${model['cost']:>7.2f}{'':>3} {context_k:<10}"
                  f"{recommended}{batch_badge}")
        
        print()
        print("Legend: ⭐ Recommended  🔄 Batch API Available")
        print()
        
        # Model selection
        while True:
            try:
                choice = int(input("Select model (number): ").strip())
                if 1 <= choice <= len(all_models):
                    selected = all_models[choice - 1]
                    return selected['provider'], selected['model_id'], selected['model_info']
                else:
                    print(f"   ✗ Please enter a number between 1 and {len(all_models)}")
            except ValueError:
                print("   ✗ Please enter a valid number")
    
    def confirm_configuration(self, config: Dict[str, Any]) -> bool:
        """Show configuration summary and confirm."""
        clear_screen()
        print_header("CONFIGURATION SUMMARY")
        
        # Calculate total cost
        if 4 in config['stages']:  # Interview stage
            model_info = config['model_info']
            cost, time_min, batch_available = calculate_cost_and_time(
                model_info, config['sample_size']
            )
            
            # Check if batch mode should be used
            use_batch = batch_available and config['sample_size'] >= 100
            if use_batch:
                cost_batch, _, _ = calculate_cost_and_time(
                    model_info, config['sample_size'], use_batch=True
                )
                print("💡 Batch API Available!")
                print(f"   Real-time cost: ${cost:.2f}")
                print(f"   Batch cost: ${cost_batch:.2f} (50% savings)")
                print()
                batch_choice = input("Use Batch API? (y/n): ").strip().lower()
                config['use_batch'] = batch_choice in ['y', 'yes']
                cost = cost_batch if config['use_batch'] else cost
            else:
                config['use_batch'] = False
        else:
            cost = 0.0
            time_min = 10  # Estimation for other stages
            
        print("Pipeline Configuration:")
        print()
        print(f"   Session ID:        {self.session_id}")
        print(f"   Sample Size:       {config['sample_size']:,} personas/interviews")
        print(f"   Stages to Run:     {', '.join([f'{i}. {PIPELINE_STAGES[i-1]['name']}' for i in config['stages']])}")
        
        if 4 in config['stages']:
            print(f"   AI Provider:       {ENHANCED_MODELS_DATABASE[config['provider']]['name']}")
            print(f"   AI Model:          {config['model_info']['name']}")
            print(f"   Batch Mode:        {'✓ Yes (50% discount)' if config.get('use_batch') else '✗ No (Real-time)'}")
            print(f"   Estimated Cost:    ${cost:.2f}")
            print(f"   Estimated Time:    {format_time(time_min)}")
        
        print(f"   Output Directory:  {self.output_dir}")
        print()
        
        # Stage details
        print("Stage Details:")
        for stage_id in config['stages']:
            stage = PIPELINE_STAGES[stage_id - 1]
            print(f"   {stage_id}. {stage['name']}: {stage['description']}")
        
        print()
        confirm = input("Start pipeline? (y/n): ").strip().lower()
        return confirm in ['y', 'yes']
    
    def run_stage(self, stage_id: int, config: Dict[str, Any]) -> bool:
        """Run a specific pipeline stage."""
        stage = PIPELINE_STAGES[stage_id - 1]
        
        print()
        print_section(f"STAGE {stage_id}: {stage['name']}")
        
        self.logger.info(f"Starting stage {stage_id}: {stage['name']}")
        
        # Build command
        cmd = ['python', stage['script']]
        
        # Add stage-specific arguments
        if stage_id == 1:  # Persona generation
            cmd.extend(['--count', str(config['sample_size'])])
            
        elif stage_id == 2:  # Health record generation
            cmd.extend(['--count', str(config['sample_size'])])
            
        elif stage_id == 4:  # Interviews
            cmd.extend([
                '--provider', config['provider'],
                '--model', config['model_id'],
                '--count', str(config['sample_size'])
            ])
            
            if config.get('use_batch'):
                cmd.append('--batch')
        
        # Set environment variables
        env = os.environ.copy()
        for provider, key_info in config['api_keys'].items():
            if provider == 'anthropic':
                env['ANTHROPIC_API_KEY'] = key_info['key']
            elif provider == 'openai':
                env['OPENAI_API_KEY'] = key_info['key']
            elif provider == 'google':
                env['GOOGLE_API_KEY'] = key_info['key']
            elif provider == 'xai':
                env['XAI_API_KEY'] = key_info['key']
        
        # Run command
        try:
            print(f"▶️  Running: {' '.join(cmd)}")
            start_time = time.time()
            
            result = subprocess.run(
                cmd,
                check=True,
                env=env,
                capture_output=False,
                text=True
            )
            
            elapsed = time.time() - start_time
            self.logger.info(f"Stage {stage_id} completed in {elapsed:.1f}s")
            
            print(f"✅ Stage {stage_id} completed successfully ({elapsed:.1f}s)")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Stage {stage_id} failed: {e}")
            print(f"❌ Stage {stage_id} failed: {e}")
            return False
            
        except KeyboardInterrupt:
            self.logger.warning(f"Stage {stage_id} interrupted by user")
            print(f"⚠️  Stage {stage_id} interrupted by user")
            return False
    
    def run_pipeline(self, config: Dict[str, Any]) -> bool:
        """Run the complete pipeline."""
        print()
        print("=" * 70)
        print("  🚀 STARTING PIPELINE EXECUTION")
        print("=" * 70)
        
        self.logger.info(f"Starting pipeline with config: {config}")
        
        total_stages = len(config['stages'])
        start_time = time.time()
        
        for i, stage_id in enumerate(config['stages'], 1):
            print(f"\n📍 Progress: Stage {i}/{total_stages}")
            
            success = self.run_stage(stage_id, config)
            
            if not success:
                print(f"\n❌ Pipeline failed at stage {stage_id}")
                self.logger.error(f"Pipeline failed at stage {stage_id}")
                return False
        
        # Pipeline completed successfully
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 70)
        print("  🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 70)
        
        print(f"\nExecution Summary:")
        print(f"   Total Time:        {format_time(int(elapsed / 60))}")
        print(f"   Stages Completed:  {total_stages}")
        print(f"   Sample Size:       {config['sample_size']:,}")
        
        if 4 in config['stages']:
            print(f"   AI Model Used:     {config['model_info']['name']}")
            cost, _, _ = calculate_cost_and_time(
                config['model_info'], config['sample_size'], config.get('use_batch', False)
            )
            print(f"   Interview Cost:    ${cost:.2f}")
        
        print(f"   Session ID:        {self.session_id}")
        print(f"   Results Directory: {self.output_dir}")
        
        # Show output files
        print("\nGenerated Files:")
        if 5 in config['stages']:  # Analysis stage
            analysis_file = Path("data/analysis/interview_summary.csv")
            if analysis_file.exists():
                print(f"   📊 Analysis Report: {analysis_file}")
        
        if 4 in config['stages']:  # Interview stage
            interviews_dir = Path("data/interviews")
            if interviews_dir.exists():
                interview_count = len(list(interviews_dir.glob("interview_*.json")))
                print(f"   🎙️  Interview Files: {interview_count} files in {interviews_dir}")
        
        self.logger.info(f"Pipeline completed successfully in {elapsed:.1f}s")
        return True
    
    def run_interactive(self):
        """Run the pipeline in interactive mode."""
        # Welcome screen
        self.print_welcome()
        
        # Get configuration
        config = self.get_pipeline_config()
        
        # AI model selection (if interviews stage selected)
        if 4 in config['stages']:
            provider, model_id, model_info = self.select_ai_model(config['sample_size'])
            config.update({
                'provider': provider,
                'model_id': model_id, 
                'model_info': model_info
            })
        
        # Confirm configuration
        if not self.confirm_configuration(config):
            print("\nPipeline cancelled by user.")
            return False
        
        # Run pipeline
        return self.run_pipeline(config)


def main():
    """Main entry point with CLI argument support."""
    parser = argparse.ArgumentParser(
        description="Synthetic Gravidas Pipeline v1.0.1 - End-to-End Orchestrator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py                           # Interactive mode
  python run_pipeline.py --count 100               # Quick 100 interviews
  python run_pipeline.py --count 10 --test        # Test mode (fast)
  python run_pipeline.py --stages 4,5              # Run only interviews + analysis
  
For more information, visit: https://github.com/dpolonia/202511-Gravidas
        """
    )
    
    parser.add_argument(
        '--count', 
        type=int, 
        help='Number of interviews to conduct (1-10000)'
    )
    
    parser.add_argument(
        '--provider',
        choices=list(ENHANCED_MODELS_DATABASE.keys()),
        help='AI provider to use'
    )
    
    parser.add_argument(
        '--model',
        help='Specific model ID to use'
    )
    
    parser.add_argument(
        '--stages',
        help='Comma-separated list of stages to run (e.g., "1,2,3" or "4,5")'
    )
    
    parser.add_argument(
        '--batch',
        action='store_true',
        help='Use batch API for cost savings (if available)'
    )
    
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode with minimal data'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version=f'Synthetic Gravidas Pipeline v{PIPELINE_VERSION}'
    )
    
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = PipelineOrchestrator()
    
    # Handle CLI mode vs interactive mode
    if any([args.count, args.provider, args.model, args.stages, args.test]):
        # CLI mode - build config from arguments
        print_header(f"🚀 SYNTHETIC GRAVIDAS PIPELINE v{PIPELINE_VERSION}")
        print("Running in CLI mode...")
        
        config = {}
        
        # Sample size
        if args.test:
            config['sample_size'] = 10
        elif args.count:
            if not (1 <= args.count <= 10000):
                print("Error: Count must be between 1 and 10,000")
                sys.exit(1)
            config['sample_size'] = args.count
        else:
            config['sample_size'] = 100  # Default
        
        # Stages
        if args.stages:
            try:
                config['stages'] = [int(s.strip()) for s in args.stages.split(',')]
            except ValueError:
                print("Error: Invalid stages format. Use comma-separated numbers (e.g., '1,2,3')")
                sys.exit(1)
        else:
            config['stages'] = [1, 2, 3, 4, 5]  # Full pipeline
        
        # API keys
        orchestrator.api_keys = get_api_keys()
        if not orchestrator.api_keys:
            print("Error: No API keys configured. Please set up .env file or config.yaml")
            sys.exit(1)
        config['api_keys'] = orchestrator.api_keys
        
        # Model selection for interviews
        if 4 in config['stages']:
            if args.provider and args.model:
                if args.provider not in orchestrator.api_keys:
                    print(f"Error: No API key configured for {args.provider}")
                    sys.exit(1)
                
                if (args.provider not in ENHANCED_MODELS_DATABASE or 
                    args.model not in ENHANCED_MODELS_DATABASE[args.provider]['models']):
                    print(f"Error: Invalid provider/model combination")
                    sys.exit(1)
                
                config.update({
                    'provider': args.provider,
                    'model_id': args.model,
                    'model_info': ENHANCED_MODELS_DATABASE[args.provider]['models'][args.model]
                })
            else:
                print("Error: Provider and model must be specified for interview stage")
                sys.exit(1)
        
        config['use_batch'] = args.batch
        
        print(f"Configuration: {config['sample_size']} samples, stages {config['stages']}")
        
        # Run pipeline
        success = orchestrator.run_pipeline(config)
        sys.exit(0 if success else 1)
        
    else:
        # Interactive mode
        try:
            success = orchestrator.run_interactive()
            sys.exit(0 if success else 1)
        except KeyboardInterrupt:
            print("\n\nPipeline interrupted by user. Goodbye!")
            sys.exit(1)


if __name__ == '__main__':
    main()