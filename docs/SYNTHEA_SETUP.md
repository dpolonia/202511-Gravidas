# Synthea Setup and Configuration Guide

Complete guide to installing, configuring, and running Synthea for generating pregnancy-related health records.

## Table of Contents

1. [What is Synthea?](#what-is-synthea)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running Synthea](#running-synthea)
5. [SNOMED Codes for Pregnancy](#snomed-codes-for-pregnancy)
6. [Troubleshooting](#troubleshooting)

---

## What is Synthea?

Synthea is an open-source synthetic patient generator that creates realistic, synthetic patient records including:
- Demographics
- Medical conditions
- Medications
- Procedures
- Encounters
- Observations

For this project, we use Synthea to generate pregnancy-related health records in FHIR format.

---

## Installation

### Prerequisites

**Java 11 or higher** is required. Check your Java version:

```bash
java -version
```

If you don't have Java 11+, install it:

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install openjdk-11-jdk
```

**macOS (using Homebrew):**
```bash
brew install openjdk@11
```

**Windows:**
Download and install from: https://www.oracle.com/java/technologies/downloads/

### Clone Synthea Repository

```bash
cd /home/user/202511-Gravidas
git clone https://github.com/synthetichealth/synthea.git
cd synthea
```

### Verify Installation

**Linux/macOS:**
```bash
./run_synthea -h
```

**Windows:**
```bash
.\run_synthea.bat -h
```

You should see the Synthea help message. If you get a "Permission denied" error on Linux/macOS:

```bash
chmod +x run_synthea
```

---

## Configuration

### 1. Main Configuration File

Edit the main Synthea configuration:

```bash
cd /home/user/202511-Gravidas/synthea
nano src/main/resources/synthea.properties
```

### 2. Key Settings for Pregnancy Records

Add or modify these settings:

```properties
# Generate only pregnancy-related modules
generate.only_modules = pregnancy,prenatal_care,maternal_health

# Demographics
generate.demographics.default_file = demographics.csv
generate.gender = F  # Female only
generate.ages.min = 12
generate.ages.max = 60

# Append mode to generate multiple patients
exporter.fhir.export = true
exporter.fhir.use_us_core_ig = true
exporter.fhir.transaction_bundle = true

# Output directory
exporter.baseDirectory = ./output/

# FHIR version
exporter.fhir.use_shr_extensions = false

# Clinical modules
generate.append_numbers_to_person_names = true
```

### 3. Enable Pregnancy Modules

Check that pregnancy-related modules are available:

```bash
ls src/main/resources/modules/
```

You should see files like:
- `pregnancy.json`
- `prenatal_care.json`
- `maternal_health.json`

If not, ensure you have the latest Synthea version:

```bash
git pull origin master
```

### 4. Configure Demographics (Optional)

Create a demographics file to control patient characteristics:

```bash
nano src/main/resources/geography/demographics.csv
```

Example content:
```csv
STNAME,POPESTIMATE
Massachusetts,6950000
```

---

## Running Synthea

### Basic Usage

Generate a single patient:

```bash
./run_synthea
```

Generate 10 patients:

```bash
./run_synthea -p 10
```

Generate patients in a specific state:

```bash
./run_synthea -p 10 Massachusetts
```

### For This Project

The Python script `scripts/02_generate_health_records.py` automates Synthea execution, but you can also run manually:

```bash
cd /home/user/202511-Gravidas/synthea

# Generate 10,000 female patients with pregnancy records
./run_synthea -p 10000 -g F --age-range 12-60
```

**Note**: Generating 10,000 patients may take 2-4 hours.

### Output Location

Generated records are saved to:

```
synthea/output/fhir/
```

Each patient gets a separate JSON file with FHIR-formatted data.

---

## SNOMED Codes for Pregnancy

Synthea uses SNOMED-CT codes for medical concepts. Here are key pregnancy-related codes:

### Primary Pregnancy Codes

| SNOMED Code | Description |
|-------------|-------------|
| 77386006 | Pregnancy (finding) |
| 72892002 | Normal pregnancy |
| 289256004 | Pregnancy on oral contraceptive |
| 102872000 | Pregnancy on intrauterine contraceptive device |
| 237238006 | Pregnancy with uncertain dates |

### Prenatal Care

| SNOMED Code | Description |
|-------------|-------------|
| 249166004 | Antenatal care |
| 424441002 | Prenatal initial visit |
| 424619006 | Prenatal visit |
| 169560008 | Antenatal care: second trimester |
| 169561007 | Antenatal care: third trimester |

### Pregnancy Complications

| SNOMED Code | Description |
|-------------|-------------|
| 15938005 | Gestational diabetes mellitus |
| 48194001 | Pregnancy-induced hypertension |
| 398254007 | Pre-eclampsia |
| 237292005 | Threatened miscarriage |
| 47200007 | High risk pregnancy |

### Pregnancy Observations

| SNOMED Code | Description |
|-------------|-------------|
| 118185001 | Finding related to pregnancy |
| 364320009 | Pregnancy observable |
| 271442007 | Duration of pregnancy |
| 57036006 | Fetal heart rate |

### Labor and Delivery

| SNOMED Code | Description |
|-------------|-------------|
| 177141003 | Normal delivery procedure |
| 386639001 | Cesarean section |
| 11466000 | Cesarean delivery |
| 289257008 | Finding of stage of labor |

### Filtering by SNOMED Codes

The Python script `scripts/02_generate_health_records.py` filters Synthea output to include only records containing these pregnancy-related codes.

To manually filter FHIR records:

```bash
# Search for pregnancy code in FHIR bundles
cd /home/user/202511-Gravidas/synthea/output/fhir
grep -l "77386006" *.json
```

---

## Troubleshooting

### Issue 1: Java Out of Memory

**Error:**
```
java.lang.OutOfMemoryError: Java heap space
```

**Solution:**
Increase Java heap size:

```bash
export JAVA_OPTS="-Xmx4g"
./run_synthea -p 10000
```

Or edit `run_synthea` script:

```bash
nano run_synthea
```

Change the line:
```bash
java -jar synthea.jar "$@"
```

To:
```bash
java -Xmx4g -jar synthea.jar "$@"
```

### Issue 2: No Pregnancy Records Generated

**Problem:** Synthea generates patients but no pregnancy conditions.

**Solution:**

1. Verify pregnancy module is enabled:
```bash
cat src/main/resources/synthea.properties | grep "generate.only_modules"
```

2. Check module files exist:
```bash
ls src/main/resources/modules/pregnancy*
```

3. Generate more patients (pregnancy is probabilistic):
```bash
./run_synthea -p 20000  # Generate extra to ensure 10k with pregnancy
```

### Issue 3: Permission Denied

**Error:**
```
bash: ./run_synthea: Permission denied
```

**Solution:**
```bash
chmod +x run_synthea
./run_synthea
```

### Issue 4: Slow Generation

**Problem:** Generating 10,000 patients takes too long.

**Solutions:**

1. **Use parallel processing** (if available):
```bash
# Split into batches of 1000
for i in {1..10}; do
  ./run_synthea -p 1000 &
done
wait
```

2. **Disable unnecessary modules**:
Edit `synthea.properties`:
```properties
generate.only_modules = pregnancy
```

3. **Use faster storage**:
Set output to SSD drive:
```properties
exporter.baseDirectory = /path/to/fast/ssd/output/
```

### Issue 5: Invalid FHIR Format

**Error:** Generated records don't parse as valid FHIR.

**Solution:**

1. Update Synthea to latest version:
```bash
cd /home/user/202511-Gravidas/synthea
git pull origin master
./gradlew build
```

2. Verify FHIR export is enabled:
```properties
exporter.fhir.export = true
```

3. Check FHIR version compatibility in config.

---

## Advanced Configuration

### Custom Pregnancy Probabilities

Edit pregnancy module to increase occurrence:

```bash
nano src/main/resources/modules/pregnancy.json
```

Find the "Initial" state and adjust probabilities:

```json
{
  "type": "Simple",
  "distributed_transition": [
    {
      "distribution": 0.8,
      "transition": "Become_Pregnant"
    },
    {
      "distribution": 0.2,
      "transition": "Not_Pregnant"
    }
  ]
}
```

### Export Formats

Synthea supports multiple export formats. Configure in `synthea.properties`:

```properties
# Enable multiple formats
exporter.fhir.export = true
exporter.ccda.export = false
exporter.csv.export = false
exporter.text.export = false
```

For this project, we use **FHIR JSON** format only.

---

## Validation

After generation, validate your records:

### Count Generated Patients

```bash
cd /home/user/202511-Gravidas/synthea/output/fhir
ls -1 *.json | wc -l
```

### Check for Pregnancy Records

```bash
# Count files containing pregnancy SNOMED code
grep -l "77386006" *.json | wc -l
```

### Validate FHIR Format

Use FHIR validator (optional):

```bash
# Install FHIR validator
wget https://github.com/hapifhir/org.hl7.fhir.core/releases/latest/download/validator_cli.jar

# Validate a record
java -jar validator_cli.jar output/fhir/patient_001.json
```

---

## Integration with Pipeline

The `scripts/02_generate_health_records.py` script automates this entire process:

1. Reads personas from `data/personas/`
2. Configures Synthea based on persona demographics
3. Runs Synthea to generate matching records
4. Filters by pregnancy SNOMED codes
5. Converts to simplified JSON format
6. Saves to `data/health_records/`

You don't need to manually configure Synthea if using the automated script.

---

## Resources

- **Synthea GitHub**: https://github.com/synthetichealth/synthea
- **Synthea Wiki**: https://github.com/synthetichealth/synthea/wiki
- **SNOMED CT Browser**: https://browser.ihtsdotools.org/
- **FHIR Specification**: https://www.hl7.org/fhir/

---

## Summary

You now have Synthea installed and configured to generate pregnancy-related health records. The automated Python scripts handle most of the complexity, but this guide provides the foundation for customization and troubleshooting.

Next step: Run `scripts/02_generate_health_records.py` to generate your 10,000 health records!
