#!/usr/bin/env python3
"""
Generate pregnancy-related health records using Synthea.

This script:
1. Loads persona data
2. Configures Synthea to generate matching demographics
3. Runs Synthea to create health records with pregnancy conditions
4. Filters records for pregnancy-related SNOMED codes
5. Converts FHIR records to simplified JSON format

Usage:
    python scripts/02_generate_health_records.py [--count COUNT] [--personas PERSONAS_FILE]
"""

import json
import logging
import sys
import argparse
import subprocess
import os
import glob
from pathlib import Path
from typing import List, Dict, Any
import time

try:
    import yaml
    from tqdm import tqdm
except ImportError:
    print("ERROR: Required packages not installed.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

# Import common loaders
from utils.common_loaders import load_config, load_personas

# Create logs directory if it doesn't exist
Path('logs').mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler('logs/02_generate_health_records.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


# Pregnancy-related SNOMED codes
PREGNANCY_SNOMED_CODES = [
    "77386006",   # Pregnancy
    "72892002",   # Normal pregnancy
    "289256004",  # Pregnancy on oral contraceptive
    "102872000",  # Pregnancy on intrauterine contraceptive device
    "237238006",  # Pregnancy with uncertain dates
    "249166004",  # Antenatal care
    "424441002",  # Prenatal initial visit
    "424619006",  # Prenatal visit
    "169560008",  # Antenatal care: second trimester
    "169561007",  # Antenatal care: third trimester
    "15938005",   # Gestational diabetes mellitus
    "48194001",   # Pregnancy-induced hypertension
    "398254007",  # Pre-eclampsia
    "237292005",  # Threatened miscarriage
    "47200007",   # High risk pregnancy
    "118185001",  # Finding related to pregnancy
    "364320009",  # Pregnancy observable
    "271442007",  # Duration of pregnancy
    "57036006",   # Fetal heart rate
    "177141003",  # Normal delivery procedure
    "386639001",  # Cesarean section
    "11466000",   # Cesarean delivery
    "289257008",  # Finding of stage of labor
]


def check_synthea_installation(synthea_path: str) -> bool:
    """Check if Synthea is installed and accessible."""
    executable = Path(synthea_path) / "run_synthea"
    executable_bat = Path(synthea_path) / "run_synthea.bat"

    if executable.exists() or executable_bat.exists():
        logger.info(f"Found Synthea at {synthea_path}")
        return True
    else:
        logger.error(f"Synthea not found at {synthea_path}")
        logger.error("Please install Synthea first:")
        logger.error("  cd /home/user/202511-Gravidas")
        logger.error("  git clone https://github.com/synthetichealth/synthea.git")
        return False


def run_synthea(
    synthea_path: str,
    count: int,
    output_dir: str,
    state: str = "Massachusetts",
    age_range: str = "12-60"
) -> bool:
    """
    Run Synthea to generate patient records.

    Args:
        synthea_path: Path to Synthea installation
        count: Number of patients to generate
        output_dir: Output directory for FHIR records
        state: US state for demographics
        age_range: Age range (e.g., "12-60")

    Returns:
        True if successful, False otherwise
    """
    logger.info(f"Running Synthea to generate {count} patient records...")

    # Determine which executable to use
    if os.name == 'nt':  # Windows
        executable = str(Path(synthea_path) / "run_synthea.bat")
    else:  # Linux/Mac
        executable = "./run_synthea"

    # Build Synthea command
    # Note: Synthea generates all patients in one run, we can't specify exact pregnancy records
    # We'll generate more than needed and filter later
    cmd = [
        executable,
        "-p", str(count),
        "-g", "F",  # Female only
        "-a", age_range,
        state
    ]

    logger.info(f"Executing: {' '.join(cmd)}")

    try:
        # Run Synthea (this may take a while)
        process = subprocess.Popen(
            cmd,
            cwd=synthea_path,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        # Monitor progress
        start_time = time.time()
        last_update = start_time

        while True:
            # Check if process is still running
            if process.poll() is not None:
                break

            # Print progress every 30 seconds
            current_time = time.time()
            if current_time - last_update > 30:
                elapsed = int(current_time - start_time)
                logger.info(f"[PROGRESS] Synthea still running... ({elapsed}s elapsed)")
                last_update = current_time

            time.sleep(5)

        # Get final output
        stdout, stderr = process.communicate()

        if process.returncode == 0:
            logger.info("Synthea completed successfully")
            return True
        else:
            logger.error(f"Synthea failed with return code {process.returncode}")
            logger.error(f"STDERR: {stderr}")
            return False

    except Exception as e:
        logger.error(f"Failed to run Synthea: {e}")
        return False


def has_pregnancy_code(fhir_record: Dict[str, Any]) -> bool:
    """
    Check if FHIR record contains pregnancy-related SNOMED codes.

    Args:
        fhir_record: Parsed FHIR JSON record

    Returns:
        True if record contains pregnancy codes
    """
    record_str = json.dumps(fhir_record).lower()

    for code in PREGNANCY_SNOMED_CODES:
        if code in record_str:
            return True

    return False


def extract_health_record(fhir_file: str) -> Dict[str, Any] | None:
    """
    Extract simplified health record from FHIR file.

    Returns:
        Simplified health record dict, or None if no pregnancy data
    """
    try:
        with open(fhir_file, 'r') as f:
            fhir_data = json.load(f)
    except Exception as e:
        logger.warning(f"Failed to parse {fhir_file}: {e}")
        return None

    # Check for pregnancy codes
    if not has_pregnancy_code(fhir_data):
        return None

    # Extract key information
    record = {
        'source_file': os.path.basename(fhir_file),
        'patient_id': None,
        'age': None,
        'conditions': [],
        'procedures': [],
        'observations': [],
        'medications': [],
        'encounters': [],
        'raw_fhir': fhir_data
    }

    # Parse FHIR Bundle entries
    entries = fhir_data.get('entry', [])

    for entry in entries:
        resource = entry.get('resource', {})
        resource_type = resource.get('resourceType', '')

        if resource_type == 'Patient':
            record['patient_id'] = resource.get('id')
            # Calculate age from birthDate
            birth_date = resource.get('birthDate', '')
            if birth_date:
                from datetime import datetime
                birth_year = int(birth_date[:4])
                current_year = datetime.now().year
                record['age'] = current_year - birth_year

        elif resource_type == 'Condition':
            condition = {
                'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('code', {}).get('coding', [{}])[0].get('display'),
                'onset': resource.get('onsetDateTime', '')
            }
            record['conditions'].append(condition)

        elif resource_type == 'Procedure':
            procedure = {
                'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('code', {}).get('coding', [{}])[0].get('display'),
                'performed': resource.get('performedDateTime', '')
            }
            record['procedures'].append(procedure)

        elif resource_type == 'Observation':
            observation = {
                'code': resource.get('code', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('code', {}).get('coding', [{}])[0].get('display'),
                'value': resource.get('valueQuantity', {}).get('value'),
                'unit': resource.get('valueQuantity', {}).get('unit'),
                'date': resource.get('effectiveDateTime', '')
            }
            record['observations'].append(observation)

        elif resource_type == 'MedicationRequest':
            medication = {
                'code': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('code'),
                'display': resource.get('medicationCodeableConcept', {}).get('coding', [{}])[0].get('display'),
                'authored': resource.get('authoredOn', '')
            }
            record['medications'].append(medication)

        elif resource_type == 'Encounter':
            encounter = {
                'type': resource.get('type', [{}])[0].get('coding', [{}])[0].get('display'),
                'period_start': resource.get('period', {}).get('start'),
                'period_end': resource.get('period', {}).get('end')
            }
            record['encounters'].append(encounter)

    return record


def process_synthea_output(synthea_output_dir: str, target_count: int) -> List[Dict[str, Any]]:
    """
    Process Synthea FHIR output files and extract pregnancy records.

    Args:
        synthea_output_dir: Directory containing FHIR JSON files
        target_count: Target number of records to extract

    Returns:
        List of health records
    """
    logger.info(f"Processing Synthea output from {synthea_output_dir}")

    fhir_files = glob.glob(os.path.join(synthea_output_dir, "*.json"))
    logger.info(f"Found {len(fhir_files)} FHIR files")

    health_records = []
    processed = 0

    for fhir_file in fhir_files:
        processed += 1

        if processed % 100 == 0:
            logger.info(f"[PROGRESS] Processed {processed}/{len(fhir_files)} files, "
                       f"found {len(health_records)} pregnancy records")

        record = extract_health_record(fhir_file)

        if record:
            health_records.append(record)

        # Stop when we have enough
        if len(health_records) >= target_count:
            break

    logger.info(f"Extracted {len(health_records)} pregnancy-related health records from {processed} files")

    return health_records[:target_count]


def save_health_records(records: List[Dict[str, Any]], output_dir: str):
    """Save health records to JSON files."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Save all records in one file
    output_file = output_path / "health_records.json"
    with open(output_file, 'w') as f:
        json.dump(records, f, indent=2)

    logger.info(f"Saved {len(records)} health records to {output_file}")

    # Also save individual record files
    for i, record in enumerate(records):
        record_file = output_path / f"record_{i:05d}.json"
        with open(record_file, 'w') as f:
            json.dump(record, f, indent=2)

    logger.info(f"Saved {len(records)} individual record files to {output_dir}")


def main():
    parser = argparse.ArgumentParser(description='Generate health records using Synthea')
    parser.add_argument('--count', type=int, default=10000, help='Number of health records to generate')
    parser.add_argument('--personas', type=str, default='data/personas/personas.json', help='Personas file')
    parser.add_argument('--output', type=str, default='data/health_records', help='Output directory')
    parser.add_argument('--config', type=str, default='config/config.yaml', help='Config file path')
    parser.add_argument('--skip-synthea', action='store_true', help='Skip Synthea execution (process existing files)')
    args = parser.parse_args()

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    logger.info("=== Health Records Generation Script Started ===")

    # Load configuration
    config = load_config(args.config)
    synthea_config = config.get('synthea', {})

    synthea_path = "./synthea"
    synthea_output = synthea_config.get('executable', './synthea/output/fhir')
    if not synthea_output.endswith('output/fhir'):
        synthea_output = os.path.join(synthea_path, 'output', 'fhir')

    # Check Synthea installation
    if not args.skip_synthea:
        if not check_synthea_installation(synthea_path):
            logger.error("Please install Synthea first. See docs/SYNTHEA_SETUP.md")
            sys.exit(1)

        # Load personas
        personas = load_personas(args.personas)

        # Run Synthea
        # Note: We generate more records than needed because not all will have pregnancy data
        # A good heuristic is to generate 2-3x the target count
        generate_count = min(args.count * 3, 30000)  # Cap at 30k for safety

        success = run_synthea(
            synthea_path=synthea_path,
            count=generate_count,
            output_dir=synthea_output,
            state=synthea_config.get('state', 'Massachusetts')
        )

        if not success:
            logger.error("Synthea execution failed")
            sys.exit(1)

    # Process Synthea output
    try:
        health_records = process_synthea_output(synthea_output, args.count)

        if len(health_records) < args.count:
            logger.warning(f"Only found {len(health_records)} pregnancy records, target was {args.count}")
            logger.warning("Consider running Synthea again with more patients")

        # Save results
        save_health_records(health_records, args.output)

        logger.info(f"[SUCCESS] Generated {len(health_records)} health records")
        logger.info("=== Health Records Generation Script Completed ===")

    except Exception as e:
        logger.error(f"Script failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()
