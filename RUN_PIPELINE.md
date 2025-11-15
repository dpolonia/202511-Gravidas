# How to Run the Gravidas Pipeline End-to-End

**Quick Reference Guide for Running Complete Workflows**

---

## 🚀 Quick Start - Run Complete Pipeline

### Option 1: Using Presets (Recommended)

```bash
# Quick test with 10 interviews (fast, for testing)
python scripts/run_workflow.py --preset quick_test

# Standard run with 100 interviews (normal production)
python scripts/run_workflow.py --preset standard

# Large production run with 1000 interviews
python scripts/run_workflow.py --preset production
```

### Option 2: Custom Number of Interviews

```bash
# Run with custom number of personas/interviews
python scripts/run_workflow.py --personas 25 --records 25

# Run with 50 personas and 50 records
python scripts/run_workflow.py --personas 50 --records 50
```

---

## 🤖 Choosing Your AI Model

### Anthropic Claude (Default)

```bash
# Use Claude Sonnet 4.5 (recommended - best balance)
python scripts/run_workflow.py --preset quick_test --model claude-sonnet-4-5-20250929

# Use Claude Opus 4.1 (most capable, higher cost)
python scripts/run_workflow.py --preset quick_test --model claude-opus-4-1

# Use Claude Haiku 4.5 (fastest, lowest cost)
python scripts/run_workflow.py --preset quick_test --model claude-haiku-4-5
```

### OpenAI GPT

```bash
# Use GPT-5 (flagship)
python scripts/run_workflow.py --preset quick_test --provider openai --model gpt-5

# Use GPT-5 mini (cost-effective)
python scripts/run_workflow.py --preset quick_test --provider openai --model gpt-5-mini

# Use GPT-4o (multimodal)
python scripts/run_workflow.py --preset quick_test --provider openai --model gpt-4o
```

### Google Gemini

```bash
# Use Gemini 2.5 Pro (recommended)
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-pro

# Use Gemini 2.5 Flash (fast and cost-effective)
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-flash
```

### xAI Grok

```bash
# Use Grok 4 Fast (best value)
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4-fast

# Use Grok 4 (most capable)
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4
```

---

## 📝 Complete Examples

### Example 1: Quick Test with Claude Sonnet

```bash
# 10 interviews with Claude Sonnet 4.5
python scripts/run_workflow.py --preset quick_test
```

**Output:**
- 10 synthetic personas
- 10 health records
- 10 matched pairs
- 10 AI interviews (~$0.80 total cost)
- Full analysis and validation

**Time:** ~2-3 minutes

---

### Example 2: Medium Run with GPT-5

```bash
# 50 interviews with GPT-5
python scripts/run_workflow.py \
  --personas 50 \
  --records 50 \
  --provider openai \
  --model gpt-5
```

**Output:**
- 50 synthetic personas
- 50 health records
- 50 matched pairs
- 50 AI interviews (~$4-6 total cost)
- Full analysis and validation

**Time:** ~10-15 minutes

---

### Example 3: Production Run with Gemini

```bash
# 100 interviews with Gemini 2.5 Flash (cost-effective)
python scripts/run_workflow.py \
  --preset standard \
  --provider google \
  --model gemini-2.5-flash
```

**Output:**
- 100 synthetic personas
- 100 health records
- 100 matched pairs
- 100 AI interviews (~$2-3 total cost)
- Full analysis and validation

**Time:** ~20-30 minutes

---

## 🎯 Run Specific Stages Only

### Start from Existing Data

```bash
# If you already have personas and records, skip to matching
python scripts/run_workflow.py \
  --stages match_personas_records,conduct_interviews,analyze_interviews

# Only conduct interviews (if personas/records/matching already done)
python scripts/run_workflow.py --stages conduct_interviews

# Only analyze existing interviews
python scripts/run_workflow.py --stages analyze_interviews
```

### Run Individual Stages

```bash
# 1. Generate personas only
python scripts/run_workflow.py --stages generate_personas --personas 20

# 2. Generate health records only
python scripts/run_workflow.py --stages generate_health_records --records 20

# 3. Match personas to records
python scripts/run_workflow.py --stages match_personas_records

# 4. Conduct interviews with specific model
python scripts/run_workflow.py --stages conduct_interviews --model claude-sonnet-4-5-20250929

# 5. Analyze interviews
python scripts/run_workflow.py --stages analyze_interviews

# 6. Validate implementation
python scripts/run_workflow.py --stages validate_implementation
```

---

## 🔧 Advanced Options

### Custom Configuration

```bash
# Use custom config file
python scripts/run_workflow.py --config my_custom_config.yaml

# Continue on error (don't stop if a stage fails)
python scripts/run_workflow.py --preset quick_test --continue-on-error

# Custom output report location
python scripts/run_workflow.py --preset quick_test --report my_report.json

# Verbose logging
python scripts/run_workflow.py --preset quick_test --verbose
```

### Combining Options

```bash
# Complete custom run
python scripts/run_workflow.py \
  --personas 75 \
  --records 75 \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --verbose \
  --report outputs/my_run_$(date +%Y%m%d).json
```

---

## 📊 Available Models & Costs

### Anthropic Claude

| Model | Cost (Input/Output per 1M tokens) | Speed | Quality |
|-------|-----------------------------------|-------|---------|
| `claude-opus-4-1` | $15.00 / $75.00 | Slow | Exceptional ⭐⭐⭐⭐⭐ |
| `claude-sonnet-4-5-20250929` | $3.00 / $15.00 | Medium | Excellent ⭐⭐⭐⭐ |
| `claude-haiku-4-5` | $1.00 / $5.00 | Fast | Very Good ⭐⭐⭐ |

### OpenAI

| Model | Cost (Input/Output per 1M tokens) | Speed | Quality |
|-------|-----------------------------------|-------|---------|
| `gpt-5` | $1.25 / $10.00 | Medium | Excellent ⭐⭐⭐⭐⭐ |
| `gpt-5-mini` | $0.25 / $2.00 | Fast | Very Good ⭐⭐⭐⭐ |
| `gpt-4o` | $2.50 / $10.00 | Medium | Excellent ⭐⭐⭐⭐ |

### Google Gemini

| Model | Cost (Input/Output per 1M tokens) | Speed | Quality |
|-------|-----------------------------------|-------|---------|
| `gemini-2.5-pro` | $1.25 / $10.00 | Medium | Excellent ⭐⭐⭐⭐ |
| `gemini-2.5-flash` | $0.15 / $1.25 | Very Fast | Very Good ⭐⭐⭐⭐ |

### xAI Grok

| Model | Cost (Input/Output per 1M tokens) | Speed | Quality |
|-------|-----------------------------------|-------|---------|
| `grok-4` | $3.00 / $15.00 | Medium | Excellent ⭐⭐⭐⭐ |
| `grok-4-fast` | $0.20 / $0.50 | Very Fast | Very Good ⭐⭐⭐ |

**Recommended for best value:** `claude-sonnet-4-5-20250929` or `gemini-2.5-flash`

---

## 📋 Preset Configurations

### quick_test
- **Personas:** 10
- **Records:** 10
- **Purpose:** Testing, development
- **Time:** 2-3 minutes
- **Cost:** ~$0.80 (with Claude Sonnet)

### standard
- **Personas:** 100
- **Records:** 100
- **Purpose:** Normal production runs
- **Time:** 20-30 minutes
- **Cost:** ~$8-10 (with Claude Sonnet)

### production
- **Personas:** 1000
- **Records:** 1000
- **Purpose:** Large-scale data generation
- **Time:** 3-4 hours
- **Cost:** ~$80-100 (with Claude Sonnet)

---

## 🔍 Understanding Output

After running the pipeline, you'll find:

```
data/
├── personas/personas.json              ← Generated personas
├── health_records/health_records.json  ← FHIR health records
├── matched/matched_personas.json       ← Matched pairs
├── interviews/interview_*.json         ← Interview transcripts
├── analysis/
│   ├── interview_summary.csv           ← Analysis in CSV
│   └── interview_analysis.json         ← Analysis in JSON
└── validation/validation_report.json   ← Validation results

outputs/workflow_report.json            ← Workflow execution report
logs/workflow.log                       ← Execution logs
```

---

## ⚠️ Prerequisites

Before running, ensure you have:

1. **API Keys Set Up** (see `API_KEY_SETUP.md`)
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   # OR
   export OPENAI_API_KEY="your-key-here"
   # OR
   export GOOGLE_API_KEY="your-key-here"
   ```

2. **Dependencies Installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Synthea Available** (for health records)
   ```bash
   # Already included in ./synthea/
   # No additional setup needed
   ```

---

## 🆘 Troubleshooting

### Pipeline Fails at a Stage

```bash
# Check the logs
tail -f logs/workflow.log

# Check the error in workflow report
cat outputs/workflow_report.json

# Resume from specific stage
python scripts/run_workflow.py --stages conduct_interviews
```

### Out of API Credits

```bash
# Use a cheaper model
python scripts/run_workflow.py --preset quick_test --model gemini-2.5-flash

# Or reduce number of interviews
python scripts/run_workflow.py --personas 5 --records 5
```

### Want to Test Before Full Run

```bash
# Use quick_test preset first
python scripts/run_workflow.py --preset quick_test

# If successful, scale up
python scripts/run_workflow.py --preset standard
```

---

## 📚 Additional Resources

- **Configuration Details:** `config/workflow_config.yaml`
- **Model Reference:** `MODEL_NAMES_REFERENCE.md`
- **Getting Started:** `GETTING_STARTED.md`
- **API Setup:** `API_KEY_SETUP.md`
- **Pipeline Guide:** `PIPELINE_EXECUTION_GUIDE.md`

---

## 💡 Pro Tips

1. **Start small:** Always test with `--preset quick_test` first
2. **Choose wisely:** Use `gemini-2.5-flash` for cost-effective runs
3. **Monitor costs:** Check analysis output for cost estimates
4. **Save results:** Reports are saved automatically in `outputs/`
5. **Review logs:** Check `logs/workflow.log` for detailed execution info
6. **Resume failed runs:** Use `--stages` to continue from where it failed

---

## 🎯 Most Common Commands

```bash
# Quick test (recommended for first run)
python scripts/run_workflow.py --preset quick_test

# Production run with best value model
python scripts/run_workflow.py --preset standard --provider google --model gemini-2.5-flash

# Custom run with 30 interviews using Claude
python scripts/run_workflow.py --personas 30 --records 30 --model claude-sonnet-4-5-20250929

# Only analyze existing interviews
python scripts/run_workflow.py --stages analyze_interviews

# Continue from where it failed
python scripts/run_workflow.py --stages conduct_interviews,analyze_interviews
```

---

**Ready to run?** Start with:
```bash
python scripts/run_workflow.py --preset quick_test
```

This will generate 10 complete interviews in ~2-3 minutes for about $0.80! ✨
