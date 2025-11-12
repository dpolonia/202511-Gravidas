# Gravidas Workflow Pipeline Tutorial

**Complete End-to-End Guide for Executing the Synthetic Interview Pipeline**

---

## Table of Contents

1. [Overview](#overview)
2. [Quick Start](#quick-start)
3. [Installation & Setup](#installation--setup)
4. [Configuration](#configuration)
5. [Running the Workflow](#running-the-workflow)
6. [Understanding the Pipeline](#understanding-the-pipeline)
7. [Interpreting Results](#interpreting-results)
8. [Advanced Usage](#advanced-usage)
9. [Troubleshooting](#troubleshooting)
10. [Best Practices](#best-practices)

---

## Overview

The Gravidas Workflow Pipeline is a comprehensive system for generating and analyzing synthetic healthcare interviews. It combines:

- **Persona Generation** with rich healthcare attributes
- **Health Record Extraction** from FHIR data
- **Semantic Matching** of personas to health records
- **AI-Powered Interviews** using Claude, GPT, or Gemini
- **Advanced Analysis** with 7 specialized topics:
  - Data Loading & Validation
  - Advanced NLP Analysis
  - Quantitative Metrics
  - Cost Attribution
  - Clinical Analytics
  - Anomaly Detection
  - Reporting Outputs

### Key Features

✅ **Configurable Parameters** - Control number of personas, AI provider, and model
✅ **Topic Highlighting** - See exactly what's being analyzed at each step
✅ **Comprehensive Testing** - Validate all components of the pipeline
✅ **Multiple Output Formats** - CSV, JSON, and detailed reports
✅ **Error Handling** - Graceful error detection and recovery
✅ **Validation Framework** - Pre-flight checks and data quality assurance

---

## Quick Start

### For Impatient Developers

```bash
# 1. Validate your setup (takes 30 seconds)
python scripts/validate_workflow_setup.py

# 2. Run quick test with minimal data (10 personas, 10 records)
python scripts/run_workflow.py --preset quick_test

# 3. Run full workflow with default settings (100 personas)
python scripts/run_workflow.py

# 4. View results
cat outputs/workflow_report.json | python -m json.tool
```

That's it! The workflow will execute all 6 pipeline stages with progress echoing.

---

## Installation & Setup

### Prerequisites

- **Python**: 3.9 or later
- **Operating System**: Linux, macOS, or Windows (with WSL recommended)
- **Disk Space**: At least 1GB for test data, 10GB+ for production

### Step 1: Clone or Access the Repository

```bash
cd /home/user/202511-Gravidas
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install from requirements.txt
pip install -r requirements.txt

# Or install core packages manually
pip install anthropic openai google-generativeai pyyaml python-dotenv nltk pandas scipy requests
```

### Step 4: Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# .env file
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
```

Or set them system-wide:

```bash
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"
```

### Step 5: Validate Your Setup

```bash
python scripts/validate_workflow_setup.py
```

You should see:

```
✅ VALIDATION SUMMARY
✅ Passed: 45/45
⚠️  Warnings: 0
❌ Errors: 0

🎯 Status: ✅ READY TO RUN
```

---

## Configuration

### Configuration File Location

```
config/workflow_config.yaml
```

### Basic Configuration

The configuration file controls:

**Number of Personas to Interview**
```yaml
workflow:
  execution:
    num_personas: 100  # Change this to 10, 50, 100, 1000, etc.
```

**AI Provider Selection**
```yaml
ai_provider:
  active_provider: "anthropic"  # or "openai", "google"
```

**AI Model Selection**
```yaml
ai_provider:
  providers:
    anthropic:
      model: "claude-4.5-sonnet"  # Try: claude-4.5-haiku, claude-4.1-opus
    openai:
      model: "gpt-5"  # Try: gpt-5-mini, gpt-5-nano
    google:
      model: "gemini-2.5-flash"  # Try: gemini-2.5-pro, gemini-2.5-flash-lite
```

### Preset Configurations

Use presets for quick setup:

```yaml
presets:
  quick_test:
    num_personas: 10
    num_health_records: 10
  standard:
    num_personas: 100
    num_health_records: 100
  production:
    num_personas: 1000
    num_health_records: 1000
```

### Complete Configuration Reference

See `config/workflow_config.yaml` for all available options including:
- Pipeline stage enablement
- Data paths
- Logging settings
- Quality assurance thresholds
- Performance tuning parameters

---

## Running the Workflow

### Method 1: Default Execution

```bash
# Run complete workflow with default settings
python scripts/run_workflow.py
```

**Output:**
- 📝 Real-time progress on console
- 📄 Report saved to `outputs/workflow_report.json`
- 📊 Log file at `logs/workflow.log`

### Method 2: Use Preset

```bash
# Quick test (smallest dataset)
python scripts/run_workflow.py --preset quick_test

# Standard workflow (recommended for first run)
python scripts/run_workflow.py --preset standard

# Production run (large dataset)
python scripts/run_workflow.py --preset production
```

### Method 3: Custom Parameters

```bash
# Override specific configuration values
python scripts/run_workflow.py \
  --personas 50 \
  --records 50 \
  --provider claude \
  --model claude-4.5-haiku

# Execute only specific stages
python scripts/run_workflow.py \
  --stages generate_personas,analyze_interviews

# Continue even if a stage fails
python scripts/run_workflow.py --continue-on-error
```

### Method 4: Custom Configuration File

```bash
# Use custom configuration file
python scripts/run_workflow.py --config config/custom_workflow.yaml
```

### Method 5: With Custom Report Output

```bash
# Save report to custom location
python scripts/run_workflow.py --report reports/my_run_2025.json
```

---

## Understanding the Pipeline

### The 6 Pipeline Stages

#### Stage 1: Generate Personas 📊

**Script:** `scripts/01b_generate_personas.py`

**Topics Addressed:**
- Demographics (age, gender, location, ethnicity, language)
- Socioeconomic Status (education, income, occupation)
- Health Profile (health consciousness, healthcare access, pregnancy readiness)
- Behavioral Factors (activity, nutrition, smoking, alcohol, sleep)
- Psychosocial Factors (mental health, stress, social support)
- Semantic Tree Generation (hierarchical health attributes)

**Output:**
```json
data/personas/personas.json
├── 100 synthetic personas
├── Rich healthcare attributes
└── Semantic tree structures with 5 branches
```

**Example Persona:**
```json
{
  "id": 123,
  "name": "Maria",
  "age": 32,
  "gender": "female",
  "semantic_tree": {
    "demographics": { ... },
    "socioeconomic": { ... },
    "health_profile": { ... },
    "behavioral": { ... },
    "psychosocial": { ... }
  }
}
```

#### Stage 2: Generate Health Records 🏥

**Script:** `scripts/02_generate_health_records.py`

**Topics Addressed:**
- FHIR Data Extraction (from Synthea)
- Clinical Conditions (SNOMED code mapping)
- Medication Profiles (pregnancy safety)
- Healthcare Utilization (visit frequency, provider engagement)
- Pregnancy Profile (risk assessment, comorbidities)
- Semantic Tree Extraction (from clinical records)

**Output:**
```json
data/health_records/health_records.json
├── 100 health records
├── FHIR-compliant structure
└── Semantic tree with clinical attributes
```

**Example Record:**
```json
{
  "patient_id": "PATIENT_456",
  "age": 31,
  "semantic_tree": {
    "clinical_conditions": [...],
    "medication_profile": [...],
    "healthcare_utilization": [...],
    "pregnancy_profile": { ... },
    "health_status": "good"
  }
}
```

#### Stage 3: Match Personas to Records 🔗

**Script:** `scripts/03_match_personas_records_enhanced.py`

**Topics Addressed:**
- Demographic Similarity (age, location compatibility)
- Socioeconomic Alignment
- Health Profile Alignment
- Behavioral Alignment
- Psychosocial Alignment
- Optimal N-to-M Matching (Hungarian Algorithm)
- Blended Scoring (40% demographic + 60% semantic)

**Output:**
```json
data/matched/semantic_matches.json
└── Matched persona-record pairs with scores
```

**Example Match:**
```json
{
  "persona_id": 123,
  "record_id": "PATIENT_456",
  "semantic_score": 0.82,
  "component_scores": {
    "demographics": 0.88,
    "health_profile": 0.85,
    "behavioral": 0.76
  }
}
```

#### Stage 4: Conduct Interviews 🎤

**Script:** `scripts/04_conduct_interviews.py`

**Output:**
```json
data/interviews/
├── interview_001.json
├── interview_002.json
└── ...
```

**Example Interview:**
```json
{
  "interview_id": "INT_001",
  "persona_id": 123,
  "record_id": "PATIENT_456",
  "turns": [
    {
      "speaker": "interviewer",
      "text": "How are you feeling today?"
    },
    {
      "speaker": "persona",
      "text": "I'm doing well, thank you for asking."
    }
  ]
}
```

#### Stage 5: Analyze Interviews 📈

**Script:** `scripts/analyze_interviews.py`

**7 Topics Addressed:**

1. **Data Loading & Validation**
   - JSON schema validation
   - Error handling for malformed data
   - Graceful field validation

2. **Advanced NLP Analysis**
   - Tokenization and lemmatization
   - Sentiment analysis (VADER)
   - Key phrase extraction
   - Conversation dynamics

3. **Quantitative Metrics**
   - Dispersion analysis (mean, median, stdev)
   - Quartile-based reporting (Q1, Q3)
   - Word count statistics
   - Turn count analysis

4. **Cost Attribution**
   - Token estimation with confidence intervals
   - Per-speaker cost breakdown
   - Model-specific pricing
   - Total cost reporting

5. **Clinical Analytics**
   - SNOMED code categorization
   - Obstetric risk scoring (1-5 scale)
   - Condition classification
   - Health status assessment

6. **Anomaly Detection**
   - Statistical outlier detection
   - High-cost identification
   - Unusual sentiment patterns
   - Missing data detection

7. **Reporting Outputs**
   - CSV export with 40+ columns
   - JSON export with metadata
   - Filtering capabilities
   - Anomaly highlighting

**Output Files:**
```
outputs/
├── interview_analysis.csv (with 40+ columns)
├── interview_analysis.json (with metadata)
└── anomalies.json (if --show-anomalies)
```

#### Stage 6: Validate Implementation ✅

**Script:** `scripts/test_semantic_implementation.py`

**Topics Addressed:**
- Persona Semantic Tree Validation
- Health Record Semantic Tree Validation
- Semantic Matching Score Validation
- Demographic Diversity Analysis
- Clinical Data Quality Assessment
- Validation Report Generation

**Output:**
```json
data/validation/
├── validation_report.json
├── demographic_analysis.json
└── clinical_analysis.json
```

---

## Interpreting Results

### 1. Workflow Report

**File:** `outputs/workflow_report.json`

```json
{
  "workflow": "Gravidas Synthetic Interview Pipeline",
  "timestamp": "2025-11-12T17:30:00",
  "execution_time_seconds": 180.5,
  "total_stages": 6,
  "successful_stages": 6,
  "failed_stages": 0,
  "overall_status": "SUCCESS",
  "configuration": {
    "ai_provider": "anthropic",
    "ai_model": "claude-4.5-sonnet",
    "num_personas": 100,
    "num_health_records": 100
  },
  "stages": {
    "generate_personas": {
      "success": true,
      "message": "Generated 100 personas with semantic trees",
      "timestamp": "2025-11-12T17:30:05"
    },
    ...
  }
}
```

### 2. Analysis CSV Output

**File:** `outputs/interview_analysis.csv`

Contains 40+ columns including:
- Interview metadata (ID, persona, record, duration)
- NLP metrics (word count, sentiment, key phrases)
- Statistical measures (mean, median, stdev, quartiles)
- Cost breakdown (input/output tokens, costs per speaker)
- Clinical data (conditions, medications, risk scores)
- Anomaly flags (outlier indicators)

**View summary:**
```bash
# See first 5 rows
head -5 outputs/interview_analysis.csv

# Get column names
head -1 outputs/interview_analysis.csv | tr ',' '\n' | nl

# View specific interview
grep "interview_001" outputs/interview_analysis.csv
```

### 3. Analysis JSON Output

**File:** `outputs/interview_analysis.json`

```json
{
  "metadata": {
    "pipeline_version": "1.0",
    "execution_timestamp": "2025-11-12T17:30:00",
    "total_interviews": 100,
    "ai_provider": "anthropic",
    "ai_model": "claude-4.5-sonnet"
  },
  "interviews": [
    {
      "interview_id": "interview_001",
      "persona_id": 123,
      "record_id": "PATIENT_456",
      "nlp_analysis": {
        "sentiment_compound": 0.65,
        "key_phrases": ["healthcare", "pregnancy", "maternal care"],
        "token_count": 1250
      },
      "cost_analysis": {
        "input_tokens": 500,
        "output_tokens": 750,
        "estimated_cost": 0.045
      },
      "clinical_analysis": {
        "conditions": ["pregnancy", "gestational_diabetes"],
        "obstetric_risk_score": 2.5
      },
      "anomalies": []
    }
  ]
}
```

### 4. Validation Report

**File:** `data/validation/validation_report.json`

```json
{
  "personas_with_trees": 100,
  "records_with_trees": 100,
  "validation_passed": 98,
  "validation_failed": 2,
  "semantic_matching_scores": {
    "min": 0.45,
    "max": 0.92,
    "avg": 0.72
  }
}
```

---

## Advanced Usage

### Running Specific Stages Only

```bash
# Generate personas and analyze interviews only (skip matching and interviews)
python scripts/run_workflow.py \
  --stages generate_personas,analyze_interviews

# Multiple stages
python scripts/run_workflow.py \
  --stages generate_personas,match_personas_records,conduct_interviews
```

### Custom Configurations

**Create custom config:**

```yaml
# config/quick_claude_test.yaml
workflow:
  execution:
    num_personas: 20
    num_health_records: 20

ai_provider:
  active_provider: "anthropic"
  providers:
    anthropic:
      model: "claude-4.5-haiku"  # Fast & cheap
```

**Run with custom config:**

```bash
python scripts/run_workflow.py --config config/quick_claude_test.yaml
```

### Testing Individual Modules

```bash
# Test persona generation only
python scripts/01b_generate_personas.py --count 50 --output data/test_personas

# Test health record generation
python scripts/02_generate_health_records.py --count 50 --output data/test_records

# Test semantic matching
python scripts/03_match_personas_records_enhanced.py

# Test interview analysis
python scripts/analyze_interviews.py --export-format both
```

### Comprehensive Testing

```bash
# Run full test suite with quick settings
python scripts/test_workflow.py --quick

# Run tests and export results
python scripts/test_workflow.py --export-json test_results.json

# Full validation with detailed checking
python scripts/validate_workflow_setup.py --export-json validation_results.json
```

### Working with Interview Data

```bash
# Filter to specific persona
python scripts/analyze_interviews.py --persona-id 123

# Filter by minimum turns
python scripts/analyze_interviews.py --min-turns 10

# Filter by minimum cost
python scripts/analyze_interviews.py --min-cost 0.10

# Show anomalies in JSON output
python scripts/analyze_interviews.py --json --show-anomalies

# Export to JSON file
python scripts/analyze_interviews.py --export-json custom_analysis.json
```

---

## Troubleshooting

### Issue 1: "Configuration file not found"

**Problem:**
```
ERROR: Configuration file not found: config/workflow_config.yaml
```

**Solution:**
```bash
# Check if file exists
ls -la config/workflow_config.yaml

# If missing, create from template
cp config/config.yaml.template config/workflow_config.yaml

# Then run workflow
python scripts/run_workflow.py
```

### Issue 2: "API key not configured"

**Problem:**
```
ERROR: API Key: anthropic - Not configured
```

**Solution:**
```bash
# Set environment variable
export ANTHROPIC_API_KEY="sk-..."

# Or add to .env file
echo "ANTHROPIC_API_KEY=sk-..." >> .env

# Verify
python scripts/validate_workflow_setup.py
```

### Issue 3: "Required package not installed"

**Problem:**
```
ERROR: Package: nltk - Not installed
```

**Solution:**
```bash
# Install missing package
pip install nltk

# Or install all requirements
pip install -r requirements.txt

# Verify
python scripts/validate_workflow_setup.py
```

### Issue 4: "Stage failed with return code X"

**Problem:**
```
❌ Stage 'generate_personas' failed with return code 1
```

**Solution:**
```bash
# Check log file for details
tail -50 logs/workflow.log

# Run stage individually to see error
python scripts/01b_generate_personas.py --count 10 --output data/test

# Check for data issues
ls -la data/personas/
```

### Issue 5: "No interview data found"

**Problem:**
Analysis stage shows "Interview data not available (skipped)"

**Solution:**
```bash
# Make sure you ran conduct_interviews stage
ls -la data/interviews/

# If empty, run full workflow
python scripts/run_workflow.py

# Or run specific stages
python scripts/run_workflow.py --stages conduct_interviews,analyze_interviews
```

### Issue 6: "Low semantic tree coverage"

**Problem:**
```
WARNING: Only 45/100 personas have semantic trees
```

**Solution:**
```bash
# Regenerate personas with debugging
python scripts/01b_generate_personas.py --count 100 --output data/personas

# Check semantic tree structure
python -c "
import json
with open('data/personas/personas.json') as f:
    personas = json.load(f)
    p = personas[0]
    print('Keys:', list(p.get('semantic_tree', {}).keys()))
"
```

---

## Best Practices

### 1. Always Validate First

```bash
# Before running workflow, validate setup
python scripts/validate_workflow_setup.py

# Fix any errors reported
# Then proceed with workflow
```

### 2. Start Small, Scale Up

```bash
# 1. Test with preset
python scripts/run_workflow.py --preset quick_test

# 2. Move to standard
python scripts/run_workflow.py --preset standard

# 3. Run production if needed
python scripts/run_workflow.py --preset production
```

### 3. Save Configuration for Reproducibility

```bash
# Create named configuration
cp config/workflow_config.yaml config/my_experiment_v1.yaml

# Edit as needed
vim config/my_experiment_v1.yaml

# Use consistently
python scripts/run_workflow.py --config config/my_experiment_v1.yaml
```

### 4. Keep Logs for Debugging

```bash
# Check workflow log
cat logs/workflow.log

# Check specific stage log
grep "Stage" logs/workflow.log

# Archive logs
mkdir -p logs/archive/
mv logs/*.log logs/archive/$(date +%Y%m%d_%H%M%S)/
```

### 5. Document Your Runs

```json
// Document in JSON
{
  "run_id": "exp_001",
  "timestamp": "2025-11-12",
  "configuration": {
    "ai_provider": "anthropic",
    "ai_model": "claude-4.5-sonnet",
    "num_personas": 100
  },
  "results_file": "outputs/workflow_report.json",
  "notes": "Initial production test"
}
```

### 6. Monitor Resource Usage

```bash
# Watch CPU/memory during execution
watch -n 1 'ps aux | grep python'

# Check disk space
df -h

# Monitor in background
python scripts/run_workflow.py > execution.log 2>&1 &
```

### 7. Validate Output Quality

```bash
# Check persona semantic trees
python -c "
import json
with open('data/personas/personas.json') as f:
    personas = json.load(f)
    trees_count = sum(1 for p in personas if p.get('semantic_tree'))
    print(f'Personas with semantic trees: {trees_count}/{len(personas)}')
"

# Check interview analysis quality
python -c "
import json, csv
with open('outputs/interview_analysis.csv') as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f'Total interviews analyzed: {len(rows)}')
    print(f'Columns: {len(reader.fieldnames)}')
"
```

---

## Key Files and Locations

```
gravidas-project/
├── config/
│   ├── workflow_config.yaml          # Main configuration
│   └── config.yaml.template          # Template reference
├── scripts/
│   ├── run_workflow.py               # Main orchestrator
│   ├── test_workflow.py              # Test suite
│   ├── validate_workflow_setup.py    # Validation tool
│   ├── 01b_generate_personas.py      # Persona generation
│   ├── 02_generate_health_records.py # Health record generation
│   ├── 03_match_personas_records_enhanced.py # Semantic matching
│   ├── 04_conduct_interviews.py      # Interview conductor
│   └── analyze_interviews.py         # Analysis (7 topics)
├── data/
│   ├── personas/personas.json        # Generated personas
│   ├── health_records/health_records.json # Health records
│   ├── matched/semantic_matches.json # Matched pairs
│   ├── interviews/                   # Interview transcripts
│   └── validation/                   # Validation reports
├── outputs/
│   ├── workflow_report.json          # Execution report
│   ├── interview_analysis.csv        # Analysis (CSV)
│   └── interview_analysis.json       # Analysis (JSON)
├── logs/
│   ├── workflow.log                  # Workflow log
│   ├── test_workflow.log             # Test log
│   └── validation.log                # Validation log
└── docs/
    └── WORKFLOW_TUTORIAL.md          # This file!
```

---

## Next Steps

1. ✅ **Complete Setup**: Run `python scripts/validate_workflow_setup.py`
2. ✅ **First Run**: Execute `python scripts/run_workflow.py --preset quick_test`
3. ✅ **Review Results**: Check `outputs/workflow_report.json`
4. ✅ **Scale Up**: Move to `python scripts/run_workflow.py --preset standard`
5. ✅ **Customize**: Edit `config/workflow_config.yaml` for your needs
6. ✅ **Analyze**: Review `outputs/interview_analysis.csv` and JSON output
7. ✅ **Iterate**: Refine configuration and run again

---

## Support and Resources

### Documentation Files

- **SEMANTIC_TREE_GUIDE.md** - Deep dive into semantic tree architecture
- **WORKFLOW_TUTORIAL.md** - This file (you are here!)
- **README.md** - Project overview

### Troubleshooting Resources

- Check `logs/` directory for detailed error logs
- Run `python scripts/validate_workflow_setup.py` for diagnostic info
- Review configuration at `config/workflow_config.yaml`

### Getting Help

```bash
# Get help for workflow orchestrator
python scripts/run_workflow.py --help

# Get help for test suite
python scripts/test_workflow.py --help

# Get help for validation
python scripts/validate_workflow_setup.py --help

# Get help for analysis
python scripts/analyze_interviews.py --help
```

---

## Appendix: Common Commands Reference

```bash
# SETUP AND VALIDATION
python scripts/validate_workflow_setup.py
python scripts/validate_workflow_setup.py --export-json validation.json

# WORKFLOW EXECUTION
python scripts/run_workflow.py                                      # Full workflow
python scripts/run_workflow.py --preset quick_test                 # Quick test
python scripts/run_workflow.py --personas 50 --provider claude     # Custom
python scripts/run_workflow.py --stages generate_personas,analyze_interviews # Specific stages

# TESTING
python scripts/test_workflow.py                    # Full tests
python scripts/test_workflow.py --quick            # Quick tests
python scripts/test_workflow.py --export-json results.json # Export results

# INDIVIDUAL STAGES
python scripts/01b_generate_personas.py --count 100 --output data/personas
python scripts/02_generate_health_records.py --count 100 --output data/health_records
python scripts/03_match_personas_records_enhanced.py
python scripts/04_conduct_interviews.py --count 100
python scripts/analyze_interviews.py --export-format both
python scripts/test_semantic_implementation.py

# RESULT VIEWING
cat outputs/workflow_report.json | python -m json.tool
head outputs/interview_analysis.csv
python -c "import json; print(json.dumps(json.load(open('outputs/interview_analysis.json')), indent=2)[:500])"
```

---

**Last Updated:** 2025-11-12
**Version:** 1.0
**Status:** Production Ready

---

Happy analyzing! 🚀
