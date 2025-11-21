# Quick Start: Complete Workflow

## Overview

The `run_complete_workflow.py` script runs the entire Gravidas pipeline end-to-end in a single command.

## Features

✓ All 6 stages automated
✓ Progress tracking with colored output
✓ Prerequisite checking
✓ Error handling with continue-on-error option
✓ Detailed JSON report generation
✓ Multiple AI provider support
✓ Quick test mode for validation

## Quick Start

### 1. Basic Usage (Default Settings)

```bash
python run_complete_workflow.py
```

This will:
- Generate 100 personas
- Generate 100 health records
- Match personas to records
- Conduct 10 interviews using Anthropic Claude
- Analyze interviews
- Validate implementation

### 2. Quick Test Mode

```bash
python run_complete_workflow.py --quick-test
```

Minimal run for testing (10 personas, 10 records, 3 interviews)

### 3. Custom Configuration

```bash
# Use OpenAI with specific model
python run_complete_workflow.py \
    --provider openai \
    --model gpt-4o-mini \
    --personas 50 \
    --interviews 20

# Use Google Gemini
python run_complete_workflow.py \
    --provider google \
    --model gemini-2.5-flash \
    --personas 100

# Continue even if a stage fails
python run_complete_workflow.py --continue-on-error
```

### 4. Production Run

```bash
python run_complete_workflow.py \
    --personas 1000 \
    --records 1000 \
    --interviews 100 \
    --provider anthropic \
    --model claude-sonnet-4-5-20250929
```

## Command Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `--personas N` | Number of personas to generate | 100 |
| `--records N` | Number of health records | 100 |
| `--interviews N` | Number of interviews to conduct | 10 |
| `--provider NAME` | AI provider (anthropic/openai/google/xai) | anthropic |
| `--model NAME` | Specific model to use | provider default |
| `--protocol PATH` | Interview protocol file | prenatal_care.json |
| `--continue-on-error` | Continue if a stage fails | false |
| `--quick-test` | Run minimal test | false |
| `--help` | Show help message | - |

## The 6 Stages

### Stage 1: Generate Personas
Creates synthetic pregnant women profiles with demographics, health history, and semantic trees.

**Output:** `data/personas/personas.json`

### Stage 2: Generate Health Records
Creates FHIR-compliant medical records using Synthea.

**Output:** `data/health_records/health_records.json`

### Stage 3: Match Personas to Records
Uses Hungarian algorithm for optimal semantic matching.

**Output:** `data/matched/matched_personas.json`

### Stage 4: Conduct Interviews
AI-powered clinical interviews using selected provider/model.

**Output:** `data/interviews/interview_*.json`

### Stage 5: Analyze Interviews
Extract insights, detect anomalies, calculate costs.

**Output:** `data/analysis/interview_summary.csv`

### Stage 6: Validate Implementation
Quality checks and semantic tree validation.

**Output:** `data/validation/validation_report.json`

## Output Files

After completion, you'll find:

```
data/
├── personas/
│   ├── personas.json
│   └── personas_summary.json
├── health_records/
│   └── health_records.json
├── matched/
│   └── matched_personas.json
├── interviews/
│   ├── interview_00001.json
│   ├── interview_00002.json
│   └── ...
├── analysis/
│   ├── interview_summary.csv
│   └── interview_analysis.json
└── validation/
    └── validation_report.json

outputs/
└── complete_workflow_report.json
```

## Examples

### Medical Research Setup
```bash
# Generate large dataset for research
python run_complete_workflow.py \
    --personas 500 \
    --records 500 \
    --interviews 50 \
    --provider anthropic
```

### Cost Optimization
```bash
# Use cheapest models
python run_complete_workflow.py \
    --provider openai \
    --model gpt-5-nano \
    --personas 100
```

### Testing New Provider
```bash
# Test xAI Grok
python run_complete_workflow.py \
    --quick-test \
    --provider xai \
    --model grok-4-fast
```

### Compare Providers
```bash
# Run same workflow with different providers
for provider in anthropic openai google xai; do
    python run_complete_workflow.py \
        --quick-test \
        --provider $provider \
        2>&1 | tee logs/test_${provider}.log
done
```

## Troubleshooting

### Prerequisites Failed
Ensure all required directories and files exist:
- `scripts/` directory
- `config/workflow_config.yaml`
- `.env` file with API keys

### Stage Failed
Check the specific stage log file in `logs/` directory.

### API Errors
Verify API keys in `.env`:
```bash
cat .env | grep API_KEY
```

### Timeout
Increase timeout for large runs by editing the script's `timeout` parameters.

## Performance Tips

1. **Start Small**: Use `--quick-test` first
2. **Monitor Costs**: Start with cheap models (gpt-5-nano, grok-4-fast)
3. **Use Batch Size**: For production, split into smaller batches
4. **Check Logs**: Review `logs/` directory for detailed output
5. **Incremental Runs**: Use `--continue-on-error` to resume after failures

## Next Steps

After successful workflow completion:

1. **Review Results:**
   ```bash
   cat outputs/complete_workflow_report.json
   ```

2. **Analyze Data:**
   ```bash
   python scripts/generate_cost_dashboard.py
   ```

3. **Export Data:**
   Open `data/analysis/interview_summary.csv` in Excel/spreadsheet

4. **Validate Quality:**
   Review `data/validation/validation_report.json`

## Support

For issues or questions:
- Check logs in `logs/` directory
- Review error messages in terminal output
- Consult `docs/PROVIDERS_AND_MODELS.md` for model options
- See `RPATRICIO.md` for detailed component documentation

---

**Created:** November 2025  
**Version:** 1.0.0  
**Compatible with:** Gravidas v2.0.0+
