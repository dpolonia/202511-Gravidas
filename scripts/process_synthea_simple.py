#!/usr/bin/env python3
"""
Simple Synthea FHIR processor for Gravidas project.
Extracts essential demographics from Synthea FHIR files.
"""

import json
import glob
import sys
from datetime import datetime
from pathlib import Path

def extract_patient_demographics(fhir_bundle):
    """Extract basic demographics from FHIR bundle."""
    record = {
        "source_file": "",
        "patient_id": "",
        "age": 0,
        "conditions": [],
        "procedures": [],
        "observations": [],
        "medications": [],
        "encounters": [],
        "semantic_tree": {},
        "raw_fhir": fhir_bundle
    }

    # Find Patient resource
    for entry in fhir_bundle.get("entry", []):
        resource = entry.get("resource", {})
        resource_type = resource.get("resourceType")

        if resource_type == "Patient":
            record["patient_id"] = resource.get("id", "")

            # Calculate age from birthDate
            birth_date = resource.get("birthDate", "")
            if birth_date:
                try:
                    birth_year = int(birth_date.split("-")[0])
                    current_year = datetime.now().year
                    record["age"] = current_year - birth_year
                except:
                    record["age"] = 30  # default

        elif resource_type == "Condition":
            condition = {
                "code": resource.get("code", {}).get("coding", [{}])[0].get("code", ""),
                "display": resource.get("code", {}).get("text", "")
            }
            record["conditions"].append(condition)

        elif resource_type == "Procedure":
            procedure = {
                "code": resource.get("code", {}).get("coding", [{}])[0].get("code", ""),
                "display": resource.get("code", {}).get("text", "")
            }
            record["procedures"].append(procedure)

    return record

def main():
    # Get first 100 FHIR files
    fhir_dir = Path("synthea/output/fhir")
    fhir_files = sorted(fhir_dir.glob("*.json"))[:100]

    print(f"Processing {len(fhir_files)} FHIR files...")

    records = []
    for i, fhir_file in enumerate(fhir_files, 1):
        try:
            with open(fhir_file) as f:
                fhir_bundle = json.load(f)

            record = extract_patient_demographics(fhir_bundle)
            record["source_file"] = fhir_file.name
            records.append(record)

            if i % 10 == 0:
                print(f"  Processed {i}/{len(fhir_files)}")

        except Exception as e:
            print(f"  Error processing {fhir_file.name}: {e}")
            continue

    # Save to data/health_records
    output_dir = Path("data/health_records")
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = output_dir / "health_records.json"
    with open(output_file, 'w') as f:
        json.dump(records, f, indent=2)

    print(f"\n✅ Processed {len(records)} health records")
    print(f"✅ Saved to {output_file}")

    return 0

if __name__ == "__main__":
    sys.exit(main())
