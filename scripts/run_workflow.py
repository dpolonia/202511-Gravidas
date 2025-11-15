#!/usr/bin/env python3
"""
Gravidas Workflow Orchestrator

This script orchestrates the complete Gravidas pipeline:
1. Generates synthetic personas with semantic healthcare attributes
2. Extracts health records from FHIR data
3. Matches personas to health records using semantic matching
4. Conducts AI-powered interviews with matched pairs
5. Analyzes interviews with comprehensive NLP and clinical analytics
6. Validates semantic tree implementation

Usage:
    python scripts/run_workflow.py
    python scripts/run_workflow.py --config config/workflow_config.yaml
    python scripts/run_workflow.py --personas 50 --provider claude --model claude-4.5-haiku
    python scripts/run_workflow.py --preset quick_test
    python scripts/run_workflow.py --stage analyze_interviews --json-output
"""

import json
import logging
import sys
import os
import argparse
import subprocess
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple
import yaml
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Setup logging
def setup_logging(log_file: str = "logs/workflow.log", level: str = "INFO"):
    """Setup logging configuration."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='[%(levelname)s] %(asctime)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class WorkflowConfig:
    """Load and manage workflow configuration."""

    def __init__(self, config_file: str = "config/workflow_config.yaml"):
        """Load workflow configuration from YAML file."""
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if not Path(self.config_file).exists():
            logger.error(f"Configuration file not found: {self.config_file}")
            raise FileNotFoundError(f"Configuration file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            config = yaml.safe_load(f)

        logger.info(f"✅ Loaded workflow configuration from {self.config_file}")
        return config

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return default
        return value if value is not None else default

    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self.config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value


class PipelineStage:
    """Represents a pipeline stage with script execution and topic highlighting."""

    def __init__(self, name: str, config: Dict[str, Any], workflow_config: WorkflowConfig):
        """Initialize pipeline stage."""
        self.name = name
        self.config = config
        self.workflow_config = workflow_config
        self.enabled = config.get('enabled', True)
        self.script = config.get('script', '')
        self.description = config.get('description', '')
        self.parameters = config.get('parameters', {})
        self.topics = config.get('topics_addressed', [])

    def _expand_parameters(self) -> Dict[str, Any]:
        """Expand parameter templates (e.g., ${workflow.execution.num_personas})."""
        expanded = {}

        for key, value in self.parameters.items():
            if isinstance(value, str) and value.startswith('${') and value.endswith('}'):
                # Extract template variable
                template_key = value[2:-1]  # Remove ${ and }

                # Handle nested template variables like ${ai_provider.providers.${ai_provider.active_provider}.model}
                if '${' in template_key:
                    # Recursively expand nested variables
                    while '${' in template_key:
                        # Find innermost ${...} pattern
                        start = template_key.rfind('${')
                        end = template_key.find('}', start)
                        if end == -1:
                            break

                        inner_var = template_key[start+2:end]
                        inner_value = self.workflow_config.get(inner_var)

                        if inner_value is not None:
                            template_key = template_key[:start] + str(inner_value) + template_key[end+1:]
                        else:
                            break

                expanded_value = self.workflow_config.get(template_key)
                expanded[key] = expanded_value if expanded_value is not None else value
            else:
                expanded[key] = value

        return expanded

    def _build_command(self) -> List[str]:
        """Build command line arguments for the script."""
        command = [sys.executable, self.script]
        expanded_params = self._expand_parameters()

        for key, value in expanded_params.items():
            # Convert snake_case to --dashed-case
            param_name = '--' + key.replace('_', '-')

            # Handle boolean flags (add flag only if True, skip if False)
            if isinstance(value, bool):
                if value:
                    command.append(param_name)
                # If False, skip this parameter entirely
            else:
                # Regular parameter with value
                command.append(param_name)
                command.append(str(value))

        return command

    def run(self) -> Tuple[bool, str]:
        """Execute the pipeline stage."""
        if not self.enabled:
            logger.info(f"⏭️  Stage '{self.name}' is disabled, skipping...")
            return True, "Skipped"

        logger.info(f"\n{'='*80}")
        logger.info(f"🔄 STAGE: {self.name.upper().replace('_', ' ')}")
        logger.info(f"{'='*80}")
        logger.info(f"Description: {self.description}\n")

        # Display topics being addressed
        logger.info(f"📋 Topics Addressed in This Stage:")
        for i, topic in enumerate(self.topics, 1):
            logger.info(f"   ✓ Topic {i}: {topic}")
        logger.info("")

        # Build and execute command
        command = self._build_command()
        logger.info(f"📝 Executing: {' '.join(command)}\n")

        try:
            start_time = time.time()
            result = subprocess.run(command, capture_output=False, text=True, check=False)
            elapsed_time = time.time() - start_time

            if result.returncode == 0:
                logger.info(f"\n✅ Stage '{self.name}' completed successfully ({elapsed_time:.2f}s)\n")
                return True, f"Completed in {elapsed_time:.2f}s"
            else:
                logger.error(f"\n❌ Stage '{self.name}' failed with return code {result.returncode}\n")
                return False, f"Failed with return code {result.returncode}"

        except Exception as e:
            logger.error(f"\n❌ Stage '{self.name}' encountered error: {str(e)}\n")
            return False, str(e)


class WorkflowOrchestrator:
    """Main workflow orchestrator that manages pipeline execution."""

    def __init__(self, config: WorkflowConfig):
        """Initialize orchestrator."""
        self.config = config
        self.stages: Dict[str, PipelineStage] = {}
        self.results: Dict[str, Dict[str, Any]] = {}
        self.start_time = None
        self.end_time = None

    def load_stages(self) -> None:
        """Load all pipeline stages from configuration."""
        pipeline_stages_config = self.config.get('pipeline_stages', {})

        for stage_name, stage_config in pipeline_stages_config.items():
            stage = PipelineStage(stage_name, stage_config, self.config)
            self.stages[stage_name] = stage

        logger.info(f"✅ Loaded {len(self.stages)} pipeline stages")

    def execute_stage(self, stage_name: str) -> bool:
        """Execute a single pipeline stage."""
        if stage_name not in self.stages:
            logger.error(f"❌ Stage '{stage_name}' not found in pipeline")
            return False

        stage = self.stages[stage_name]
        success, message = stage.run()

        self.results[stage_name] = {
            'success': success,
            'message': message,
            'timestamp': datetime.now().isoformat()
        }

        return success

    def execute_all_stages(self, continue_on_error: bool = False) -> bool:
        """Execute all pipeline stages in order."""
        logger.info("\n" + "="*80)
        logger.info("🚀 STARTING GRAVIDAS WORKFLOW PIPELINE")
        logger.info("="*80 + "\n")

        self.start_time = time.time()
        all_success = True

        for stage_name in self.stages.keys():
            success = self.execute_stage(stage_name)

            if not success:
                all_success = False
                if not continue_on_error:
                    logger.error(f"\n❌ Pipeline stopped at stage '{stage_name}'")
                    break
                else:
                    logger.warning(f"⚠️  Continuing despite failure in stage '{stage_name}'")

        self.end_time = time.time()
        return all_success

    def execute_stages(self, stage_names: List[str]) -> bool:
        """Execute specific pipeline stages."""
        logger.info("\n" + "="*80)
        logger.info(f"🚀 EXECUTING GRAVIDAS WORKFLOW ({len(stage_names)} stages)")
        logger.info("="*80 + "\n")

        self.start_time = time.time()
        all_success = True

        for stage_name in stage_names:
            if stage_name not in self.stages:
                logger.error(f"❌ Stage '{stage_name}' not found")
                all_success = False
                continue

            success = self.execute_stage(stage_name)
            if not success:
                all_success = False

        self.end_time = time.time()
        return all_success

    def generate_summary_report(self) -> Dict[str, Any]:
        """Generate comprehensive summary report."""
        elapsed_time = self.end_time - self.start_time if self.end_time and self.start_time else 0

        successful_stages = sum(1 for r in self.results.values() if r['success'])
        failed_stages = len(self.results) - successful_stages

        report = {
            'workflow': self.config.get('workflow.name', 'Unknown'),
            'timestamp': datetime.now().isoformat(),
            'execution_time_seconds': elapsed_time,
            'total_stages': len(self.results),
            'successful_stages': successful_stages,
            'failed_stages': failed_stages,
            'overall_status': 'SUCCESS' if failed_stages == 0 else 'FAILURE',
            'stages': self.results,
            'configuration': {
                'ai_provider': self.config.get('ai_provider.active_provider'),
                'ai_model': self.config.get('ai_provider.providers.' + self.config.get('ai_provider.active_provider') + '.model'),
                'num_personas': self.config.get('workflow.execution.num_personas'),
                'num_health_records': self.config.get('workflow.execution.num_health_records'),
            }
        }

        return report

    def print_summary(self) -> None:
        """Print execution summary to console."""
        report = self.generate_summary_report()

        logger.info("\n" + "="*80)
        logger.info("📊 WORKFLOW EXECUTION SUMMARY")
        logger.info("="*80)

        logger.info(f"\n📋 Workflow: {report['workflow']}")
        logger.info(f"🕐 Execution Time: {report['execution_time_seconds']:.2f} seconds")
        logger.info(f"📈 Stages: {report['successful_stages']}/{report['total_stages']} successful")
        logger.info(f"🤖 AI Provider: {report['configuration']['ai_provider']}")
        logger.info(f"🧠 AI Model: {report['configuration']['ai_model']}")
        logger.info(f"👥 Personas Generated: {report['configuration']['num_personas']}")
        logger.info(f"📋 Health Records: {report['configuration']['num_health_records']}")

        logger.info(f"\n📝 Stage Results:")
        for stage_name, result in report['stages'].items():
            status = "✅" if result['success'] else "❌"
            logger.info(f"   {status} {stage_name}: {result['message']}")

        logger.info(f"\n🎯 Overall Status: {report['overall_status']}")
        logger.info("="*80 + "\n")

        return report

    def save_report(self, output_file: str = "outputs/workflow_report.json") -> None:
        """Save execution report to JSON file."""
        Path(output_file).parent.mkdir(parents=True, exist_ok=True)
        report = self.generate_summary_report()

        with open(output_file, 'w') as f:
            json.dump(report, f, indent=2)

        logger.info(f"📄 Report saved to: {output_file}")


def apply_preset(config: WorkflowConfig, preset_name: str) -> None:
    """Apply a preset configuration."""
    presets = config.get('presets', {})

    if preset_name not in presets:
        logger.error(f"❌ Preset '{preset_name}' not found")
        return

    preset = presets[preset_name]
    logger.info(f"✅ Applying preset: {preset_name}")
    logger.info(f"   Description: {preset.get('description', 'N/A')}")

    if 'num_personas' in preset:
        config.set('workflow.execution.num_personas', preset['num_personas'])
    if 'num_health_records' in preset:
        config.set('workflow.execution.num_health_records', preset['num_health_records'])
    if 'interview_batch_size' in preset:
        config.set('workflow.execution.interview_batch_size', preset['interview_batch_size'])
    if 'num_workers' in preset:
        config.set('workflow.execution.max_workers', preset['num_workers'])


def main():
    """Main workflow orchestrator entry point."""
    parser = argparse.ArgumentParser(
        description='Gravidas Workflow Orchestrator - Execute complete pipeline',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run complete workflow with default configuration
  python scripts/run_workflow.py

  # Run with custom configuration file
  python scripts/run_workflow.py --config config/workflow_config.yaml

  # Override specific parameters
  python scripts/run_workflow.py --personas 50 --provider claude --model claude-4.5-haiku

  # Use preset configuration
  python scripts/run_workflow.py --preset quick_test

  # Execute only specific stages
  python scripts/run_workflow.py --stages generate_personas,match_personas_records,analyze_interviews

  # Continue execution even if a stage fails
  python scripts/run_workflow.py --continue-on-error
        """
    )

    parser.add_argument('--config', type=str, default='config/workflow_config.yaml',
                        help='Path to workflow configuration file')
    parser.add_argument('--preset', type=str, choices=['quick_test', 'standard', 'production'],
                        help='Use preset configuration (quick_test, standard, production)')
    parser.add_argument('--personas', type=int,
                        help='Number of personas to generate (overrides config)')
    parser.add_argument('--records', type=int,
                        help='Number of health records to generate (overrides config)')
    parser.add_argument('--provider', type=str, choices=['anthropic', 'openai', 'google'],
                        help='AI provider (anthropic, openai, google)')
    parser.add_argument('--model', type=str,
                        help='AI model name (overrides config)')
    parser.add_argument('--stages', type=str,
                        help='Comma-separated list of stages to execute')
    parser.add_argument('--continue-on-error', action='store_true',
                        help='Continue execution even if a stage fails')
    parser.add_argument('--report', type=str, default='outputs/workflow_report.json',
                        help='Output file for execution report')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    try:
        # Load configuration
        config = WorkflowConfig(args.config)

        # Apply preset if specified
        if args.preset:
            apply_preset(config, args.preset)

        # Override configuration with command-line arguments
        if args.personas:
            config.set('workflow.execution.num_personas', args.personas)
        if args.records:
            config.set('workflow.execution.num_health_records', args.records)
        if args.provider:
            config.set('ai_provider.active_provider', args.provider)
        if args.model:
            # Set model for active provider
            active_provider = config.get('ai_provider.active_provider')
            config.set(f'ai_provider.providers.{active_provider}.model', args.model)

        # Create orchestrator
        orchestrator = WorkflowOrchestrator(config)
        orchestrator.load_stages()

        # Execute stages
        if args.stages:
            stage_names = [s.strip() for s in args.stages.split(',')]
            success = orchestrator.execute_stages(stage_names)
        else:
            success = orchestrator.execute_all_stages(continue_on_error=args.continue_on_error)

        # Generate and save report
        report = orchestrator.print_summary()
        orchestrator.save_report(args.report)

        # Exit with appropriate code
        sys.exit(0 if success else 1)

    except Exception as e:
        logger.error(f"❌ Workflow execution failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
