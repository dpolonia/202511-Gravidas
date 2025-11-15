# Run Gravidas Pipeline End-to-End

**Complete Guide to Running the Full Pipeline with Custom Settings**

---

## 🎯 Quick Overview

The Gravidas pipeline has **6 stages** that run automatically:

1. **Generate Personas** - Create synthetic patient profiles
2. **Generate Health Records** - Extract FHIR health data
3. **Match Personas to Records** - Optimal semantic matching
4. **Conduct Interviews** - AI-powered conversations
5. **Analyze Interviews** - Comprehensive NLP analysis
6. **Validate Implementation** - Quality checks

You can choose:
- **Number of interviews** (10, 25, 50, 100, or custom)
- **AI model** (Claude, GPT, Gemini, or Grok)

---

## 🚀 METHOD 1: INTERACTIVE MODE (Recommended for Beginners)

### Step 1: Launch Interactive Runner

```bash
python run_interactive.py
```

### Step 2: Choose Number of Interviews

You'll see:
```
Available Presets:

  1. Quick Test       - 10 interviews   (~2-3 min,  ~$0.80)
  2. Standard         - 100 interviews  (~30 min,   ~$8)
  3. Production       - 1000 interviews (~4 hours,  ~$80)
  4. Custom           - Choose your own number

Select option (1-4):
```

**Choose:**
- `1` for quick test (10 interviews)
- `2` for standard run (100 interviews)
- `3` for production (1000 interviews)
- `4` for custom number

### Step 3: Choose AI Model

You'll see:
```
Available Models:

Anthropic Claude:
  1. Claude Sonnet 4.5 (Recommended)
  2. Claude Opus 4.1
  3. Claude Haiku 4.5

Google Gemini:
  4. Gemini 2.5 Flash (Best Value ⭐)
  5. Gemini 2.5 Pro

OpenAI:
  6. GPT-5
  7. GPT-5 Mini

xAI Grok:
  8. Grok 4 Fast (Fastest)
  9. Grok 4

Select model (1-9):
```

**Recommendations:**
- `1` - Claude Sonnet (best balance)
- `4` - Gemini Flash (best value)
- `8` - Grok Fast (fastest & cheapest)

### Step 4: Confirm and Run

Review the configuration:
```
Your Configuration:
  Interviews:       10
  AI Provider:      Anthropic
  Model:            Claude Sonnet 4.5
  Estimated Cost:   $0.56 - $1.04
  Estimated Time:   ~2 minutes

Proceed with this configuration? (yes/no):
```

Type `yes` and press Enter.

### Step 5: Monitor Progress

The pipeline will run all 6 stages automatically:
```
✅ Stage 'generate_personas' completed successfully (26.48s)
✅ Stage 'generate_health_records' completed successfully (16.87s)
✅ Stage 'match_personas_records' completed successfully (1.85s)
✅ Stage 'conduct_interviews' completed successfully (2784.83s)
✅ Stage 'analyze_interviews' completed successfully (12.45s)
✅ Stage 'validate_implementation' completed successfully (3.21s)

🎯 Overall Status: SUCCESS
```

### Step 6: Check Results

Results are automatically saved:
```bash
# Analysis results (CSV)
cat data/analysis/interview_summary.csv

# Analysis results (JSON)
cat data/analysis/interview_analysis.json

# Workflow report
cat outputs/workflow_report.json
```

---

## ⚡ METHOD 2: COMMAND-LINE MODE (For Advanced Users)

### Basic Syntax

```bash
python scripts/run_workflow.py [OPTIONS]
```

### Quick Examples

**10 interviews with default model (Claude Sonnet):**
```bash
python scripts/run_workflow.py --preset quick_test
```

**25 interviews with Gemini Flash (cheapest):**
```bash
python scripts/run_workflow.py --personas 25 --records 25 --provider google --model gemini-2.5-flash
```

**50 interviews with GPT-5:**
```bash
python scripts/run_workflow.py --personas 50 --records 50 --provider openai --model gpt-5
```

**100 interviews with Grok Fast (fastest):**
```bash
python scripts/run_workflow.py --preset standard --provider xai --model grok-4-fast
```

### Complete Options

```bash
python scripts/run_workflow.py \
  --preset <preset_name> \          # quick_test, standard, or production
  --personas <number> \             # Number of personas to generate
  --records <number> \              # Number of health records to generate
  --provider <provider_name> \      # anthropic, openai, google, or xai
  --model <model_name>              # Specific model ID
```

---

## 📊 Choosing Number of Interviews

### Recommended Presets

| Preset | Interviews | Time | Cost (Claude) | Cost (Gemini) | Best For |
|--------|-----------|------|---------------|---------------|----------|
| `quick_test` | 10 | ~5 min | ~$0.80 | ~$0.10 | Testing, validation |
| `standard` | 100 | ~1 hour | ~$8.00 | ~$1.00 | Regular analysis |
| `production` | 1000 | ~8 hours | ~$80.00 | ~$10.00 | Large-scale research |

### Custom Numbers

For any custom number (1-10,000):

```bash
# 25 interviews
python scripts/run_workflow.py --personas 25 --records 25

# 250 interviews
python scripts/run_workflow.py --personas 250 --records 250

# 5000 interviews
python scripts/run_workflow.py --personas 5000 --records 5000
```

**Note:** `--personas` and `--records` should match for 1:1 interviews.

---

## 🤖 Choosing AI Model

### All Available Models

**Anthropic Claude:**
```bash
# Best balance - RECOMMENDED
--provider anthropic --model claude-sonnet-4-5-20250929

# Maximum quality (expensive)
--provider anthropic --model claude-opus-4-1

# Fast and economical
--provider anthropic --model claude-haiku-4-5
```

**Google Gemini:**
```bash
# Best value - CHEAPEST ⭐
--provider google --model gemini-2.5-flash

# High quality
--provider google --model gemini-2.5-pro
```

**OpenAI GPT:**
```bash
# Recommended GPT
--provider openai --model gpt-5

# Budget option
--provider openai --model gpt-5-mini
```

**xAI Grok:**
```bash
# Fastest & cheapest ⚡
--provider xai --model grok-4-fast

# Most capable Grok
--provider xai --model grok-4
```

### Model Comparison

| Model | Provider | Cost/1M | Speed | Quality | Best For |
|-------|----------|---------|-------|---------|----------|
| **Claude Sonnet** | Anthropic | $3/$15 | ⚡⚡ | ★★★★★ | **Balanced (Default)** |
| **Gemini Flash** | Google | $0.15/$1.25 | ⚡⚡⚡ | ★★★★ | **Best Value** |
| **Grok Fast** | xAI | $0.20/$0.50 | ⚡⚡⚡ | ★★★★ | **Speed & Value** |
| **GPT-5** | OpenAI | $1.25/$10 | ⚡⚡ | ★★★★★ | **Quality** |
| **Claude Opus** | Anthropic | $15/$75 | ⚡ | ★★★★★ | **Max Quality** |

---

## 📝 Complete End-to-End Examples

### Example 1: Quick Test with Best Balance

```bash
# 10 interviews with Claude Sonnet
python scripts/run_workflow.py --preset quick_test

# Result: ~5 minutes, ~$0.80
```

### Example 2: Cost-Optimized Run

```bash
# 100 interviews with Gemini Flash (cheapest)
python scripts/run_workflow.py --preset standard --provider google --model gemini-2.5-flash

# Result: ~1 hour, ~$1.00
```

### Example 3: Speed-Optimized Run

```bash
# 100 interviews with Grok Fast (fastest)
python scripts/run_workflow.py --preset standard --provider xai --model grok-4-fast

# Result: ~45 minutes, ~$0.50
```

### Example 4: Quality-Optimized Run

```bash
# 50 interviews with Claude Opus (best quality)
python scripts/run_workflow.py --personas 50 --records 50 --provider anthropic --model claude-opus-4-1

# Result: ~1 hour, ~$20
```

### Example 5: Custom Configuration

```bash
# 25 interviews with GPT-5
python scripts/run_workflow.py \
  --personas 25 \
  --records 25 \
  --provider openai \
  --model gpt-5

# Result: ~20 minutes, ~$1.35
```

### Example 6: Production Run with Cost Optimization

```bash
# 1000 interviews with Gemini Flash
python scripts/run_workflow.py \
  --preset production \
  --provider google \
  --model gemini-2.5-flash

# Result: ~6-8 hours, ~$10
```

---

## 🔍 What Happens During Each Stage

### Stage 1: Generate Personas (~2-3 min for 10)
```
Creating synthetic patient profiles with:
- Demographics (age, location, ethnicity)
- Socioeconomic data (education, income)
- Health profile (conditions, lifestyle)
- Pregnancy intentions and history
- Semantic tree structures
```

### Stage 2: Generate Health Records (~2 min for 10)
```
Extracting FHIR health data:
- Running Synthea patient generator
- Extracting clinical conditions
- Medication profiles
- Healthcare utilization
- Pregnancy risk assessment
```

### Stage 3: Match Personas to Records (~2-3 sec for 10)
```
Optimal matching using:
- Semantic similarity (60% weight)
- Demographic compatibility (40% weight)
- Hungarian algorithm for optimization
- Quality scoring and validation
```

### Stage 4: Conduct Interviews (varies by model)
```
AI-powered interviews:
- 15 protocol questions per interview
- Multi-turn conversations
- Healthcare context preservation
- Transcript generation
```

**Time estimates:**
- 10 interviews: ~3-5 minutes
- 100 interviews: ~30-45 minutes
- 1000 interviews: ~5-8 hours

### Stage 5: Analyze Interviews (~1-2 min for 10)
```
Comprehensive analysis:
- NLP (tokenization, sentiment, key phrases)
- Quantitative metrics (statistics, dispersion)
- Cost attribution (token estimation)
- Clinical analytics (SNOMED, risk scoring)
- Anomaly detection
```

### Stage 6: Validate Implementation (~1-2 sec)
```
Quality validation:
- Semantic tree completeness
- Data quality scoring
- Demographic diversity analysis
- Clinical data assessment
```

---

## 📊 Output Files

After completion, you'll find:

### Analysis Results
```bash
data/analysis/interview_summary.csv      # Spreadsheet format
data/analysis/interview_analysis.json    # JSON format
```

### Interview Transcripts
```bash
data/interviews/interview_*.json         # Individual transcripts
```

### Quality Reports
```bash
data/validation/validation_report.json   # Validation results
outputs/workflow_report.json             # Complete workflow summary
```

### Logs
```bash
logs/workflow.log                        # Detailed execution log
```

---

## ⚙️ Advanced Options

### Run Specific Stages Only

```bash
# Only conduct interviews (using existing personas/records)
python scripts/run_workflow.py --stages conduct_interviews

# Only analyze interviews
python scripts/run_workflow.py --stages analyze_interviews

# Multiple stages
python scripts/run_workflow.py --stages match_personas_records,conduct_interviews
```

### Resume from Failed Stage

If a stage fails, resume from that stage:

```bash
# Check which stage failed
cat outputs/workflow_report.json

# Resume from the failed stage
python scripts/run_workflow.py --stages conduct_interviews
```

---

## 💰 Cost Estimation

### Quick Reference

**10 Interviews:**
- Claude Sonnet: ~$0.80
- Gemini Flash: ~$0.10
- Grok Fast: ~$0.05

**100 Interviews:**
- Claude Sonnet: ~$8.00
- Gemini Flash: ~$1.00
- Grok Fast: ~$0.50

**1000 Interviews:**
- Claude Sonnet: ~$80.00
- Gemini Flash: ~$10.00
- Grok Fast: ~$5.00

**Formula:**
```
Cost = (interviews × avg_tokens_per_interview × cost_per_1M_tokens) / 1,000,000

Where:
- avg_tokens_per_interview ≈ 5,300 tokens
- cost_per_1M_tokens = model-specific (see table above)
```

---

## 🆘 Troubleshooting

### API Key Not Found

```bash
# Check your .env file
cat .env | grep API_KEY

# Set missing key
echo "ANTHROPIC_API_KEY='your-key-here'" >> .env
echo "GOOGLE_API_KEY='your-key-here'" >> .env
```

### Stage Failed

```bash
# Check logs
tail -100 logs/workflow.log

# Check workflow report
cat outputs/workflow_report.json

# Resume from failed stage
python scripts/run_workflow.py --stages <failed_stage_name>
```

### Out of Memory

For large runs (>1000 interviews):
```bash
# Run in smaller batches
python scripts/run_workflow.py --personas 500 --records 500
# Then run again for next batch
```

### Rate Limit Exceeded

```bash
# Switch to different provider
python scripts/run_workflow.py --preset quick_test --provider xai

# Or wait and retry (most rate limits reset after 1 minute)
```

---

## ✅ Best Practices

### 1. Start Small
```bash
# Always test with quick_test first
python scripts/run_workflow.py --preset quick_test
```

### 2. Choose Right Model for Use Case

**Development/Testing:**
```bash
--provider xai --model grok-4-fast  # Fastest
```

**Production (Quality Priority):**
```bash
--provider anthropic --model claude-sonnet-4-5-20250929  # Best balance
```

**Production (Cost Priority):**
```bash
--provider google --model gemini-2.5-flash  # Cheapest
```

### 3. Monitor Progress
```bash
# In another terminal, watch the log
tail -f logs/workflow.log
```

### 4. Check Results
```bash
# Quick overview
cat outputs/workflow_report.json | grep -E "status|success|failed"

# Detailed analysis
cat data/analysis/interview_summary.csv
```

---

## 🎓 Learning Path

### Beginners
1. Start with interactive mode: `python run_interactive.py`
2. Choose quick_test (10 interviews)
3. Use default model (Claude Sonnet)
4. Review results in `data/analysis/`

### Intermediate
1. Use command-line with presets
2. Try different models
3. Compare results across providers
4. Scale to 100 interviews

### Advanced
1. Custom interview counts
2. Run specific stages
3. Resume from failures
4. Optimize for cost or speed

---

## 📖 Additional Resources

- **Complete Guide:** `RUN_PIPELINE.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **Provider Guide:** `PROVIDER_USAGE.md`
- **Interactive Guide:** `INTERACTIVE_GUIDE.md`
- **API Setup:** `API_KEY_SETUP.md`

---

## 🚀 Ready to Run?

### Recommended First Run:

```bash
# Interactive mode (easiest)
python run_interactive.py

# OR command-line mode
python scripts/run_workflow.py --preset quick_test
```

### Choose Your Own:

```bash
# Custom number + specific model
python scripts/run_workflow.py \
  --personas <number> \
  --records <number> \
  --provider <anthropic|google|openai|xai> \
  --model <model-name>
```

---

## 🎯 Summary Cheat Sheet

```bash
# QUICK TEST (10 interviews)
python scripts/run_workflow.py --preset quick_test

# STANDARD (100 interviews)
python scripts/run_workflow.py --preset standard

# CUSTOM NUMBER
python scripts/run_workflow.py --personas 25 --records 25

# CHANGE MODEL
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-flash

# CHECK RESULTS
cat data/analysis/interview_summary.csv
cat outputs/workflow_report.json
```

---

**Happy Interviewing! 🎉**

For questions or issues, check the logs or review the complete documentation in `RUN_PIPELINE.md`.
