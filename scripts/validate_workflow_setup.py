#!/usr/bin/env python3
"""
Workflow Setup Validation and Error Handling

This script validates the complete workflow setup before execution:
1. Configuration file validation (YAML syntax, required fields)
2. Python environment validation (Python version, required packages)
3. File and directory structure validation
4. API key and credential validation
5. Data file validation
6. Script execution capability validation
7. Detailed error reporting and recovery suggestions

Usage:
    python scripts/validate_workflow_setup.py
    python scripts/validate_workflow_setup.py --config config/workflow_config.yaml
    python scripts/validate_workflow_setup.py --check-only
    python scripts/validate_workflow_setup.py --fix-issues
"""

import json
import sys
import os
import subprocess
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import logging
import argparse
import importlib

# Setup logging
def setup_logging(log_file: str = "logs/validation.log", level: str = "INFO"):
    """Setup logging configuration."""
    Path(log_file).parent.mkdir(parents=True, exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='[%(levelname)s] %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger(__name__)


logger = setup_logging()


class ValidationResult:
    """Represents validation check result."""

    def __init__(self, name: str, passed: bool, message: str, severity: str = "INFO"):
        """Initialize validation result."""
        self.name = name
        self.passed = passed
        self.message = message
        self.severity = severity  # INFO, WARNING, ERROR

    def __str__(self) -> str:
        """String representation."""
        status = "✅" if self.passed else "❌"
        return f"{status} {self.name}: {self.message}"


class WorkflowValidator:
    """Comprehensive workflow validation and error handling."""

    def __init__(self, config_file: str = "config/workflow_config.yaml"):
        """Initialize validator."""
        self.config_file = config_file
        self.config = None
        self.validation_results: List[ValidationResult] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_result(self, result: ValidationResult) -> None:
        """Add validation result."""
        self.validation_results.append(result)

        if result.passed:
            logger.info(str(result))
        elif result.severity == "ERROR":
            logger.error(str(result))
            self.errors.append(result.message)
        else:
            logger.warning(str(result))
            self.warnings.append(result.message)

    # ========================================================================
    # 1. CONFIGURATION VALIDATION
    # ========================================================================

    def validate_config_file(self) -> bool:
        """Validate configuration file exists and is valid YAML."""
        logger.info("\n" + "="*80)
        logger.info("1️⃣  CONFIGURATION FILE VALIDATION")
        logger.info("="*80 + "\n")

        # Check file exists
        if not Path(self.config_file).exists():
            self.add_result(ValidationResult(
                "Config File Exists",
                False,
                f"Configuration file not found: {self.config_file}",
                "ERROR"
            ))
            return False

        self.add_result(ValidationResult(
            "Config File Exists",
            True,
            f"Found at {self.config_file}"
        ))

        # Check YAML syntax
        try:
            import yaml
            with open(self.config_file, 'r') as f:
                self.config = yaml.safe_load(f)

            self.add_result(ValidationResult(
                "YAML Syntax",
                True,
                "Configuration YAML is valid"
            ))

            # Check required top-level keys
            required_keys = ['workflow', 'ai_provider', 'pipeline_stages', 'data_paths']
            missing_keys = [k for k in required_keys if k not in self.config]

            if missing_keys:
                self.add_result(ValidationResult(
                    "Required Configuration Keys",
                    False,
                    f"Missing keys: {', '.join(missing_keys)}",
                    "ERROR"
                ))
                return False

            self.add_result(ValidationResult(
                "Required Configuration Keys",
                True,
                f"All required top-level keys present"
            ))

            return True

        except Exception as e:
            self.add_result(ValidationResult(
                "YAML Syntax",
                False,
                f"Invalid YAML syntax: {str(e)}",
                "ERROR"
            ))
            return False

    def validate_config_values(self) -> bool:
        """Validate configuration values are correct."""
        logger.info("2️⃣  CONFIGURATION VALUES VALIDATION\n")

        all_valid = True

        # Validate AI provider
        active_provider = self.config.get('ai_provider', {}).get('active_provider')
        valid_providers = ['anthropic', 'openai', 'google']

        if active_provider not in valid_providers:
            self.add_result(ValidationResult(
                "AI Provider",
                False,
                f"Invalid provider '{active_provider}'. Must be one of: {', '.join(valid_providers)}",
                "ERROR"
            ))
            all_valid = False
        else:
            self.add_result(ValidationResult(
                "AI Provider",
                True,
                f"Valid provider: {active_provider}"
            ))

        # Validate execution parameters
        num_personas = self.config.get('workflow', {}).get('execution', {}).get('num_personas')
        if not isinstance(num_personas, int) or num_personas < 1:
            self.add_result(ValidationResult(
                "Number of Personas",
                False,
                f"Invalid num_personas: {num_personas}. Must be positive integer",
                "ERROR"
            ))
            all_valid = False
        else:
            self.add_result(ValidationResult(
                "Number of Personas",
                True,
                f"num_personas = {num_personas}"
            ))

        # Validate data paths
        data_paths = self.config.get('data_paths', {})
        if not data_paths.get('base_dir'):
            self.add_result(ValidationResult(
                "Data Paths",
                False,
                "data_paths.base_dir not configured",
                "ERROR"
            ))
            all_valid = False
        else:
            self.add_result(ValidationResult(
                "Data Paths",
                True,
                f"Base data directory: {data_paths.get('base_dir')}"
            ))

        return all_valid

    # ========================================================================
    # 2. PYTHON ENVIRONMENT VALIDATION
    # ========================================================================

    def validate_python_version(self) -> bool:
        """Validate Python version."""
        logger.info("\n" + "="*80)
        logger.info("3️⃣  PYTHON ENVIRONMENT VALIDATION")
        logger.info("="*80 + "\n")

        current_version = sys.version_info
        required_version = (3, 9)  # Python 3.9+

        if current_version >= required_version:
            self.add_result(ValidationResult(
                "Python Version",
                True,
                f"Python {current_version.major}.{current_version.minor}.{current_version.micro} (required: 3.9+)"
            ))
            return True
        else:
            self.add_result(ValidationResult(
                "Python Version",
                False,
                f"Python {current_version.major}.{current_version.minor} detected. Required: 3.9+",
                "ERROR"
            ))
            return False

    def validate_required_packages(self) -> bool:
        """Validate required Python packages are installed."""
        logger.info("4️⃣  REQUIRED PACKAGES VALIDATION\n")

        required_packages = self.config.get('environment', {}).get('required_packages', [])
        if not required_packages:
            required_packages = [
                'anthropic', 'openai', 'google-generativeai',
                'pyyaml', 'python-dotenv', 'nltk', 'pandas', 'scipy', 'requests'
            ]

        all_installed = True
        for package in required_packages:
            # Convert package name to module name
            module_name = package.replace('-', '_')

            try:
                importlib.import_module(module_name)
                self.add_result(ValidationResult(
                    f"Package: {package}",
                    True,
                    "Installed"
                ))
            except ImportError:
                self.add_result(ValidationResult(
                    f"Package: {package}",
                    False,
                    f"Not installed. Run: pip install {package}",
                    "ERROR"
                ))
                all_installed = False

        return all_installed

    # ========================================================================
    # 3. FILE AND DIRECTORY STRUCTURE VALIDATION
    # ========================================================================

    def validate_directory_structure(self) -> bool:
        """Validate directory structure."""
        logger.info("\n" + "="*80)
        logger.info("5️⃣  DIRECTORY STRUCTURE VALIDATION")
        logger.info("="*80 + "\n")

        required_dirs = [
            'scripts',
            'config',
            'data',
            'logs',
            'outputs'
        ]

        all_exist = True
        for directory in required_dirs:
            if Path(directory).exists():
                self.add_result(ValidationResult(
                    f"Directory: {directory}",
                    True,
                    f"Found"
                ))
            else:
                self.add_result(ValidationResult(
                    f"Directory: {directory}",
                    False,
                    f"Directory does not exist. Run: mkdir -p {directory}",
                    "WARNING"
                ))
                all_exist = False

        return all_exist

    def validate_script_files(self) -> bool:
        """Validate required script files exist."""
        logger.info("6️⃣  REQUIRED SCRIPTS VALIDATION\n")

        required_scripts = [
            'scripts/01b_generate_personas.py',
            'scripts/02_generate_health_records.py',
            'scripts/03_match_personas_records_enhanced.py',
            'scripts/04_conduct_interviews.py',
            'scripts/analyze_interviews.py',
            'scripts/test_semantic_implementation.py',
            'scripts/run_workflow.py',
            'scripts/test_workflow.py'
        ]

        all_exist = True
        for script in required_scripts:
            if Path(script).exists():
                # Check if executable
                is_executable = os.access(script, os.X_OK)
                status = "Executable" if is_executable else "Not executable"

                self.add_result(ValidationResult(
                    f"Script: {script}",
                    True,
                    status
                ))
            else:
                self.add_result(ValidationResult(
                    f"Script: {script}",
                    False,
                    "Script not found",
                    "ERROR"
                ))
                all_exist = False

        return all_exist

    # ========================================================================
    # 4. API KEY AND CREDENTIAL VALIDATION
    # ========================================================================

    def validate_api_keys(self) -> bool:
        """Validate API keys are configured."""
        logger.info("\n" + "="*80)
        logger.info("7️⃣  API KEY AND CREDENTIAL VALIDATION")
        logger.info("="*80 + "\n")

        active_provider = self.config.get('ai_provider', {}).get('active_provider')
        providers_config = self.config.get('ai_provider', {}).get('providers', {})

        all_valid = True

        for provider_name, provider_config in providers_config.items():
            api_key = provider_config.get('api_key', '')

            # Check for environment variable reference
            if api_key.startswith('${') and api_key.endswith('}'):
                env_var = api_key[2:-1]  # Extract variable name
                actual_key = os.getenv(env_var)

                if actual_key:
                    is_valid = not actual_key.startswith('your-')
                else:
                    is_valid = False

                status_msg = f"Environment variable '{env_var}'"
            else:
                is_valid = not api_key.startswith('your-') and len(api_key) > 0
                status_msg = "Direct configuration"

            if is_valid:
                status = "✅ Configured"
            else:
                status = "❌ Not configured"
                all_valid = False if provider_name == active_provider else all_valid

            severity = "WARNING" if provider_name != active_provider else "ERROR" if not is_valid else "INFO"
            self.add_result(ValidationResult(
                f"API Key: {provider_name}",
                is_valid,
                f"{status} ({status_msg})",
                severity
            ))

        return all_valid

    # ========================================================================
    # 5. DATA FILE VALIDATION
    # ========================================================================

    def validate_data_files(self) -> bool:
        """Validate existing data files."""
        logger.info("\n" + "="*80)
        logger.info("8️⃣  DATA FILE VALIDATION")
        logger.info("="*80 + "\n")

        data_paths = self.config.get('data_paths', {})
        warnings_only = True

        # Check personas
        personas_dir = Path(data_paths.get('personas', 'data/personas'))
        personas_file = personas_dir / 'personas.json'

        if personas_file.exists():
            try:
                with open(personas_file, 'r') as f:
                    personas = json.load(f)
                    count = len(personas) if isinstance(personas, list) else 0

                self.add_result(ValidationResult(
                    "Personas Data",
                    True,
                    f"Found {count} personas"
                ))
            except json.JSONDecodeError:
                self.add_result(ValidationResult(
                    "Personas Data",
                    False,
                    "Invalid JSON in personas.json",
                    "WARNING"
                ))
        else:
            self.add_result(ValidationResult(
                "Personas Data",
                False,
                f"personas.json not found at {personas_file}",
                "WARNING"
            ))

        # Check health records
        records_dir = Path(data_paths.get('health_records', 'data/health_records'))
        records_file = records_dir / 'health_records.json'

        if records_file.exists():
            try:
                with open(records_file, 'r') as f:
                    records = json.load(f)
                    count = len(records) if isinstance(records, list) else 0

                self.add_result(ValidationResult(
                    "Health Records Data",
                    True,
                    f"Found {count} records"
                ))
            except json.JSONDecodeError:
                self.add_result(ValidationResult(
                    "Health Records Data",
                    False,
                    "Invalid JSON in health_records.json",
                    "WARNING"
                ))
        else:
            self.add_result(ValidationResult(
                "Health Records Data",
                False,
                f"health_records.json not found at {records_file}",
                "WARNING"
            ))

        return warnings_only

    # ========================================================================
    # 6. SCRIPT EXECUTION CAPABILITY VALIDATION
    # ========================================================================

    def validate_script_execution(self) -> bool:
        """Validate scripts can be executed."""
        logger.info("\n" + "="*80)
        logger.info("9️⃣  SCRIPT EXECUTION VALIDATION")
        logger.info("="*80 + "\n")

        test_scripts = [
            'scripts/run_workflow.py',
            'scripts/test_workflow.py',
            'scripts/analyze_interviews.py'
        ]

        all_executable = True

        for script in test_scripts:
            try:
                result = subprocess.run(
                    [sys.executable, script, '--help'],
                    capture_output=True,
                    text=True,
                    timeout=5
                )

                if result.returncode == 0:
                    self.add_result(ValidationResult(
                        f"Script Execution: {script}",
                        True,
                        "Can execute with --help"
                    ))
                else:
                    self.add_result(ValidationResult(
                        f"Script Execution: {script}",
                        False,
                        f"Script failed: {result.stderr[:100]}",
                        "WARNING"
                    ))
                    all_executable = False

            except subprocess.TimeoutExpired:
                self.add_result(ValidationResult(
                    f"Script Execution: {script}",
                    False,
                    "Script execution timed out",
                    "WARNING"
                ))
                all_executable = False

            except Exception as e:
                self.add_result(ValidationResult(
                    f"Script Execution: {script}",
                    False,
                    f"Error testing script: {str(e)[:100]}",
                    "WARNING"
                ))

        return all_executable

    # ========================================================================
    # 7. COMPREHENSIVE VALIDATION REPORT
    # ========================================================================

    def run_all_validations(self) -> bool:
        """Run all validation checks."""
        logger.info("\n" + "="*80)
        logger.info("🔍 GRAVIDAS WORKFLOW SETUP VALIDATION")
        logger.info("="*80)

        # Run validation steps
        config_file_valid = self.validate_config_file()
        if not config_file_valid:
            logger.error("\n❌ Configuration file validation failed. Cannot proceed.")
            return False

        self.validate_config_values()
        python_version_valid = self.validate_python_version()
        packages_valid = self.validate_required_packages()
        dirs_valid = self.validate_directory_structure()
        scripts_valid = self.validate_script_files()
        api_keys_valid = self.validate_api_keys()
        self.validate_data_files()
        scripts_executable = self.validate_script_execution()

        # Determine overall status
        critical_checks = [
            config_file_valid,
            python_version_valid,
            packages_valid,
            scripts_valid,
            api_keys_valid
        ]

        all_passed = all(critical_checks)

        return all_passed

    def print_summary(self) -> Dict[str, Any]:
        """Print validation summary."""
        error_count = len(self.errors)
        warning_count = len(self.warnings)
        passed_count = sum(1 for r in self.validation_results if r.passed)
        total_count = len(self.validation_results)

        logger.info("\n" + "="*80)
        logger.info("📊 VALIDATION SUMMARY")
        logger.info("="*80)

        logger.info(f"\n✅ Passed: {passed_count}/{total_count}")
        logger.info(f"⚠️  Warnings: {warning_count}")
        logger.info(f"❌ Errors: {error_count}")

        if self.errors:
            logger.info("\n📋 Critical Errors:")
            for error in self.errors:
                logger.info(f"   ❌ {error}")

        if self.warnings:
            logger.info("\n⚠️  Warnings:")
            for warning in self.warnings:
                logger.info(f"   ⚠️  {warning}")

        status = "✅ READY TO RUN" if error_count == 0 else "❌ SETUP REQUIRED"
        logger.info(f"\n🎯 Status: {status}")
        logger.info("="*80 + "\n")

        return {
            'total_checks': total_count,
            'passed': passed_count,
            'warnings': warning_count,
            'errors': error_count,
            'status': 'READY' if error_count == 0 else 'SETUP_REQUIRED',
            'error_details': self.errors,
            'warning_details': self.warnings
        }


def main():
    """Main validation entry point."""
    parser = argparse.ArgumentParser(
        description='Validate Gravidas workflow setup',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run full validation
  python scripts/validate_workflow_setup.py

  # Validate specific config file
  python scripts/validate_workflow_setup.py --config config/custom_config.yaml

  # Check only (no fixes)
  python scripts/validate_workflow_setup.py --check-only

  # Export validation report
  python scripts/validate_workflow_setup.py --export-json validation_report.json
        """
    )

    parser.add_argument('--config', type=str, default='config/workflow_config.yaml',
                        help='Path to workflow configuration file')
    parser.add_argument('--check-only', action='store_true',
                        help='Only check without attempting fixes')
    parser.add_argument('--export-json', type=str,
                        help='Export validation report to JSON file')
    parser.add_argument('--verbose', action='store_true',
                        help='Enable verbose logging')

    args = parser.parse_args()

    try:
        # Create validator
        validator = WorkflowValidator(args.config)

        # Run validations
        all_passed = validator.run_all_validations()

        # Print summary
        summary = validator.print_summary()

        # Export report if requested
        if args.export_json:
            Path(args.export_json).parent.mkdir(parents=True, exist_ok=True)
            with open(args.export_json, 'w') as f:
                json.dump(summary, f, indent=2)
            logger.info(f"📄 Validation report saved to: {args.export_json}")

        # Exit with appropriate code
        sys.exit(0 if all_passed else 1)

    except Exception as e:
        logger.error(f"❌ Validation failed: {str(e)}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
