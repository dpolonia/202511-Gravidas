# 🚀 Clean Run Tutorial

## Overview

This tutorial guides you through performing a complete clean run of the Synthetic Gravidas Pipeline after archiving previous data.

## ✅ Pre-Run Status

**Data Archive Created:** `archive/20251107_051149_previous_run/`
- Previous interviews, personas, health records archived
- Log files backed up
- Fresh data directories ready

**Configuration Ready:**
- ✅ API keys loaded from `.env` file
- ✅ Active provider: `anthropic`
- ✅ Active model: `claude-3-5-sonnet-20241022`

## 🎯 Clean Run Steps

### Step 1: Verify Configuration

```bash
# Check your API configuration
cat config/config.yaml

# Verify API keys are configured to load from .env file
grep -E "(ANTHROPIC_API_KEY|OPENAI_API_KEY|GOOGLE_API_KEY|XAI_API_KEY|HF_TOKEN)" config/config.yaml

# Verify your .env file contains API keys
grep -E "(ANTHROPIC_API_KEY|OPENAI_API_KEY|GOOGLE_API_KEY|XAI_API_KEY|HF_TOKEN)" .env
```

### Step 2: Run the Complete Pipeline

Execute the 4-stage pipeline in order:

#### Stage 1: Retrieve Personas (10,000 female personas)
```bash
cd /home/dpolonia/202511-Gravidas
python scripts/01_retrieve_personas.py

# Expected output:
# - data/personas/personas.json (10,000 personas)
# - data/personas/personas_summary.json
```

#### Stage 2: Generate Health Records
```bash
python scripts/02_generate_health_records.py

# Expected output:
# - data/health_records/health_records.json
# - data/health_records/record_*.json files
```

#### Stage 3: Match Personas with Records
```bash
python scripts/03_match_personas_records_enhanced.py

# Expected output:
# - data/matched/matched_personas.json
# - data/matched/match_quality_metrics.json
# - data/matched/matching_statistics.json
```

#### Stage 4: Conduct Interviews
```bash
# Option A: Interactive launcher (recommended)
python scripts/interactive_interviews.py

# Option B: Direct script
python scripts/04_conduct_interviews.py

# Expected output:
# - data/interviews/interview_*.json files
# - data/analysis/interview_summary.csv
```

### Step 3: Monitor Progress

Check logs during execution:
```bash
# Monitor current pipeline stage
tail -f logs/*.log

# Check data generation progress
ls -la data/*/
```

### Step 4: Verify Results

```bash
# Count generated files
echo "Personas: $(ls data/personas/*.json 2>/dev/null | wc -l)"
echo "Health Records: $(ls data/health_records/record_*.json 2>/dev/null | wc -l)"
echo "Interviews: $(ls data/interviews/interview_*.json 2>/dev/null | wc -l)"

# Check file sizes
du -sh data/*/
```

## 🔧 Configuration Options

### Interview Configuration

Edit interview parameters in `scripts/04_conduct_interviews.py` or modify `config/config.yaml`:

```yaml
# In config/config.yaml
active_provider: "anthropic"  # or "openai", "google", "xai"
active_model: "claude-3-5-sonnet-20241022"  # Change to preferred model

interview:
  max_turns: 20
  batch_size: 10  # Number of interviews to run in parallel
```

```python
# Or edit scripts/04_conduct_interviews.py
num_interviews = 100  # Adjust as needed
protocol_file = "Script/interview_protocols/pregnancy_experience.json"
```

### Cost Optimization

For large runs (100+ interviews):
```bash
# Use batch API for 50% cost savings
python scripts/04_conduct_interviews.py --use-batch-api
```

### Model Selection

Supported models and estimated costs (per 1,000 interviews):

| Provider | Model | Cost Estimate |
|----------|-------|---------------|
| Anthropic | Claude 3.5 Sonnet | $15-25 |
| OpenAI | GPT-4o | $20-30 |
| Google | Gemini 1.5 Pro | $10-20 |
| xAI | Grok 4 Fast | $5-10 |
| xAI | Grok 3 Mini | $6-12 |

## 📊 Expected Timeline

| Stage | Time Estimate | Output Size |
|-------|---------------|-------------|
| Personas | 5-10 minutes | ~16KB |
| Health Records | 10-30 minutes | ~80MB |
| Matching | 2-5 minutes | ~43MB |
| Interviews (100) | 20-60 minutes | ~300KB |

## ⚠️ Troubleshooting

### Common Issues

**Synthea Not Found:**
```bash
# Ensure Synthea is properly set up
ls -la synthea/run_synthea
chmod +x synthea/run_synthea
```

**API Key Errors:**
```bash
# Verify .env file is loaded correctly
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('API Keys Status:')
print(f'Anthropic: {\"✅\" if os.getenv(\"ANTHROPIC_API_KEY\") else \"❌\"} {os.getenv(\"ANTHROPIC_API_KEY\", \"NOT_FOUND\")[:20]}...')
print(f'OpenAI: {\"✅\" if os.getenv(\"OPENAI_API_KEY\") else \"❌\"} {os.getenv(\"OPENAI_API_KEY\", \"NOT_FOUND\")[:20]}...')
print(f'Google: {\"✅\" if os.getenv(\"GOOGLE_API_KEY\") else \"❌\"} {os.getenv(\"GOOGLE_API_KEY\", \"NOT_FOUND\")[:20]}...')
print(f'xAI: {\"✅\" if os.getenv(\"XAI_API_KEY\") else \"❌\"} {os.getenv(\"XAI_API_KEY\", \"NOT_FOUND\")[:20]}...')
"
```

**Memory Issues:**
```bash
# Monitor system resources
free -h
df -h
```

### Recovery Options

**Restart from Specific Stage:**
```bash
# Skip to matching if personas/records exist
python scripts/03_match_personas_records_enhanced.py

# Resume interviews from last checkpoint
python scripts/04_conduct_interviews.py --resume
```

## 📈 Post-Run Analysis

After completion, analyze results:

```bash
# Generate interview summary
python scripts/analyze_interviews.py

# View results
cat data/analysis/interview_summary.csv
```

## 🗂️ Archive Management

Your previous run is archived in:
```
archive/20251107_051149_previous_run/
├── analysis/
├── interviews/
├── matched/
├── personas/
├── finepersonas_profiles/
├── health_records/
└── *.log files
```

To restore previous data:
```bash
# Restore specific dataset
cp -r archive/20251107_051149_previous_run/interviews/* data/interviews/

# Restore complete previous run
cp -r archive/20251107_051149_previous_run/* data/
```

## 🎯 Success Criteria

A successful clean run should produce:
- ✅ 10,000 personas generated
- ✅ Health records matched to personas
- ✅ Interview files created
- ✅ Analysis summary generated
- ✅ No critical errors in logs

## 📞 Support

- **Documentation:** See `docs/` directory
- **Model Guide:** `docs/MODEL_SELECTION.md`
- **API Setup:** `docs/API_CONFIGURATION.md`
- **Environment Variables:** Check `.env` file for API keys
- **Issues:** Check logs in `logs/` directory

## 🔧 Quick Setup Verification

Run this to verify everything is ready:

```bash
# Test configuration
python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('🚀 Ready for Clean Run!')
print('✅ Anthropic API:', 'Found' if os.getenv('ANTHROPIC_API_KEY') else 'Missing')
print('✅ OpenAI API:', 'Found' if os.getenv('OPENAI_API_KEY') else 'Missing') 
print('✅ Google API:', 'Found' if os.getenv('GOOGLE_API_KEY') else 'Missing')
print('✅ xAI API:', 'Found' if os.getenv('XAI_API_KEY') else 'Missing')
print('✅ HuggingFace:', 'Found' if os.getenv('HF_TOKEN') else 'Missing (Optional)')
print('✅ Data directories clean')
print('✅ Archive created')
"
```

---

**Ready to begin?** Start with Step 1 above! 🚀