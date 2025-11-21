# Gravidas Workflow Customization Guide

Complete guide to customizing all aspects of the Gravidas synthetic data generation workflow.

## Table of Contents
1. [Quick Reference](#quick-reference)
2. [Basic Customization](#basic-customization)
3. [AI Provider & Model Selection](#ai-provider--model-selection)
4. [Interview Protocols](#interview-protocols)
5. [Advanced Configurations](#advanced-configurations)
6. [Complete Examples](#complete-examples)

---

## Quick Reference

### Command Structure
```bash
python run_complete_workflow.py [OPTIONS]
```

### Available Options
| Option | Description | Default | Examples |
|--------|-------------|---------|----------|
| `--personas N` | Number of personas to generate | 100 | `--personas 50` |
| `--records N` | Number of health records | 100 | `--records 200` |
| `--interviews N` | Number of interviews | 10 | `--interviews 25` |
| `--provider NAME` | AI provider | anthropic | `--provider openai` |
| `--model NAME` | Specific AI model | (auto) | `--model gpt-4o-mini` |
| `--protocol FILE` | Interview protocol | prenatal_care | `--protocol high_risk` |
| `--continue-on-error` | Don't stop on errors | (off) | N/A |
| `--quick-test` | Run minimal test | (off) | N/A |

---

## Basic Customization

### 1. Scale Configuration

#### Small Test Run
```bash
python run_complete_workflow.py \
  --personas 10 \
  --records 10 \
  --interviews 5
```
**Use case:** Quick testing, debugging
**Time:** ~5-10 minutes
**Cost:** ~$0.10-0.50

#### Standard Research Run
```bash
python run_complete_workflow.py \
  --personas 100 \
  --records 100 \
  --interviews 50
```
**Use case:** Standard research dataset
**Time:** ~2-4 hours
**Cost:** ~$5-15

#### Large Production Run
```bash
python run_complete_workflow.py \
  --personas 1000 \
  --records 1000 \
  --interviews 500
```
**Use case:** Large-scale research, publication
**Time:** ~20-40 hours
**Cost:** ~$50-150

### 2. Quick Test Mode
```bash
python run_complete_workflow.py --quick-test
```
- Generates: 10 personas, 10 records, 3 interviews
- Perfect for: System verification, testing changes
- Time: ~7 minutes

---

## AI Provider & Model Selection

### Available Providers

#### 1. Anthropic Claude (Default)
**Best for:** High-quality medical conversations, nuanced responses

```bash
# Use default Claude model
python run_complete_workflow.py --provider anthropic

# Specify Claude model
python run_complete_workflow.py \
  --provider anthropic \
  --model claude-sonnet-4-5
```

**Available Models:**
- `claude-opus-4-1` - Most capable ($15/$75 per 1M tokens)
- `claude-sonnet-4-5` - **Recommended** - Best balance ($3/$15)
- `claude-sonnet-4-5-20250929` - Specific version ($3/$15)
- `claude-haiku-4-5` - **Default** - Fastest, cheapest ($1/$5)

#### 2. OpenAI GPT
**Best for:** Broad knowledge, structured outputs

```bash
python run_complete_workflow.py \
  --provider openai \
  --model gpt-4o-mini
```

**Available Models:**
- `gpt-5` - Latest generation ($1.25/$10 per 1M tokens)
- `gpt-5-mini` - Efficient ($0.25/$2)
- `gpt-5-nano` - Ultra-low cost ($0.05/$0.40)
- `gpt-4o` - Multimodal ($2.50/$10)
- `gpt-4o-mini` - **Recommended** ($0.15/$0.60)
- `gpt-4-1` - GPT-4.1 ($2/$8)

#### 3. Google Gemini
**Best for:** Large context, fast processing

```bash
python run_complete_workflow.py \
  --provider google \
  --model gemini-2.5-flash
```

**Available Models:**
- `gemini-3-pro-preview` - PREVIEW - Next generation (pricing TBD)
- `gemini-2.5-flash` - **Recommended** - Fast ($0.15/$1.25)
- `gemini-2.5-pro` - Most capable stable ($1.25/$10)
- `gemini-2.5-pro-long` - Extended context ($2.50/$15)

#### 4. xAI Grok
**Best for:** Research applications, reasoning

```bash
python run_complete_workflow.py \
  --provider xai \
  --model grok-4-fast
```

**Available Models:**
- `grok-4-fast` - **Recommended** - Fast reasoning ($0.20/$0.50)
- `grok-4` - Most capable ($3/$15)
- `grok-3-mini` - Budget option ($0.30/$0.50)

---

## Interview Protocols

### Available Protocols

Located in: `Script/interview_protocols/`

#### 1. Prenatal Care (Default)
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/prenatal_care.json
```
**Focus:** Standard prenatal visits, routine care
**Topics:** Checkups, nutrition, lifestyle, symptoms

#### 2. High-Risk Pregnancy
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/high_risk_pregnancy.json
```
**Focus:** Complications, advanced monitoring
**Topics:** Medical complications, specialist care, risk factors

#### 3. Mental Health Screening
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/mental_health_screening.json
```
**Focus:** Psychological wellbeing, mood disorders
**Topics:** Depression, anxiety, support systems, coping

#### 4. Genetic Counseling
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/genetic_counseling.json
```
**Focus:** Genetic risks, family history
**Topics:** Inherited conditions, testing, decision-making

#### 5. Postpartum Care
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/postpartum_care.json
```
**Focus:** Post-birth recovery, newborn care
**Topics:** Recovery, breastfeeding, bonding, adjustment

#### 6. Pregnancy Experience
```bash
python run_complete_workflow.py \
  --protocol Script/interview_protocols/pregnancy_experience.json
```
**Focus:** Overall pregnancy journey
**Topics:** Personal experiences, emotions, relationships

---

## Advanced Configurations

### Configuration File Editing

Edit `config/config.yaml` or `config/workflow_config.yaml` for system-wide defaults:

```yaml
# config/config.yaml
active_provider: "anthropic"
active_model: "claude-haiku-4-5"

api_keys:
  anthropic:
    api_key: "${ANTHROPIC_API_KEY}"
    max_tokens: 4096
    temperature: 0.7
```

### Environment Variables

Set in `.env` file:
```bash
# AI Provider API Keys
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=...
XAI_API_KEY=...

# System Configuration
MAX_RETRIES=3
RETRY_DELAY=1.0
```

### Error Handling

#### Continue on Errors
```bash
python run_complete_workflow.py \
  --continue-on-error \
  --personas 100
```
- Continues workflow even if a stage fails
- Useful for partial data collection
- Check logs for failure details

---

## Complete Examples

### Example 1: Cost-Optimized Large Run
**Goal:** Generate large dataset at minimum cost

```bash
python run_complete_workflow.py \
  --personas 500 \
  --records 500 \
  --interviews 100 \
  --provider google \
  --model gemini-2.5-flash \
  --protocol Script/interview_protocols/prenatal_care.json
```

**Estimated Cost:** ~$15-25
**Time:** ~10-15 hours
**Best for:** Budget-conscious research

### Example 2: High-Quality Clinical Research
**Goal:** Maximum quality for publication

```bash
python run_complete_workflow.py \
  --personas 200 \
  --records 200 \
  --interviews 100 \
  --provider anthropic \
  --model claude-opus-4-1 \
  --protocol Script/interview_protocols/high_risk_pregnancy.json
```

**Estimated Cost:** ~$100-150
**Time:** ~15-20 hours
**Best for:** Academic publication, grant-funded research

### Example 3: Multi-Protocol Study
Run multiple times with different protocols:

```bash
# Run 1: Prenatal Care
python run_complete_workflow.py \
  --personas 100 --records 100 --interviews 30 \
  --protocol Script/interview_protocols/prenatal_care.json

# Run 2: Mental Health
python run_complete_workflow.py \
  --personas 100 --records 100 --interviews 30 \
  --protocol Script/interview_protocols/mental_health_screening.json

# Run 3: High-Risk
python run_complete_workflow.py \
  --personas 100 --records 100 --interviews 30 \
  --protocol Script/interview_protocols/high_risk_pregnancy.json
```

### Example 4: Provider Comparison Study
Test different AI providers:

```bash
# Claude
python run_complete_workflow.py --quick-test \
  --provider anthropic --model claude-haiku-4-5

# OpenAI
python run_complete_workflow.py --quick-test \
  --provider openai --model gpt-4o-mini

# Google
python run_complete_workflow.py --quick-test \
  --provider google --model gemini-2.5-flash

# xAI
python run_complete_workflow.py --quick-test \
  --provider xai --model grok-4-fast
```

### Example 5: Rapid Prototyping
**Goal:** Fast iterations during development

```bash
python run_complete_workflow.py \
  --personas 5 \
  --records 5 \
  --interviews 2 \
  --provider google \
  --model gemini-2.5-flash \
  --continue-on-error
```

**Time:** ~2-3 minutes
**Cost:** ~$0.05
**Best for:** Development, testing changes

---

## Cost Optimization Tips

### 1. Choose Right Model for Task
- **Haiku/Mini models** for testing and validation
- **Sonnet/Standard models** for production
- **Opus/Pro models** only for critical quality needs

### 2. Use Batch Processing
- Generate multiple personas/records in single run
- More efficient than repeated small runs

### 3. Cache-Friendly Providers
- Google Gemini: Excellent context caching (1M tokens)
- Anthropic: Good batch API support
- OpenAI: Solid batch processing

### 4. Smart Interview Distribution
```bash
# Instead of 100 interviews across 10 personas (10 each):
python run_complete_workflow.py --personas 10 --interviews 100

# Do: 100 interviews across 50 personas (2 each):
python run_complete_workflow.py --personas 50 --interviews 100
```
More diverse data, similar cost.

---

## Output Locations

All runs save to:
```
data/
├── personas/personas.json
├── health_records/health_records.json
├── matched/matched_personas.json
├── interviews/interview_*.json
├── analysis/interview_summary.csv
└── validation/validation_report.json

outputs/
└── complete_workflow_report.json

logs/
└── *.log
```

To archive results:
```bash
# Manual archive with custom name
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
ARCHIVE_NAME="my_study_${TIMESTAMP}"
mkdir -p "archives/$ARCHIVE_NAME"
cp -r data/* "archives/$ARCHIVE_NAME/"
```

---

## Troubleshooting

### Common Issues

**Issue:** "API key not found"
```bash
# Check .env file exists and has correct keys
cat .env | grep API_KEY
```

**Issue:** "Model not found"
```bash
# Verify model name is correct (case-sensitive)
# Check config/workflow_config.yaml for available models
```

**Issue:** "Stage failed"
```bash
# Use continue-on-error to complete other stages
python run_complete_workflow.py --continue-on-error

# Check logs for details
tail -f logs/04_conduct_interviews.log
```

---

## Next Steps

1. **Test the workflow:**
   ```bash
   python run_complete_workflow.py --quick-test
   ```

2. **Run your custom configuration:**
   ```bash
   python run_complete_workflow.py \
     --personas 50 \
     --provider openai \
     --model gpt-4o-mini \
     --protocol Script/interview_protocols/prenatal_care.json
   ```

3. **Archive your results:**
   ```bash
   # Results automatically archived after each run
   ls -lh archives/
   ```

---

**Need Help?**
- Check `RPATRICIO.md` for project overview
- See `QUICK_START_WORKFLOW.md` for getting started
- Review `config/workflow_config.yaml` for all options
- Check `logs/` directory for detailed execution logs

**Version:** Gravidas v2.0.0 - Complete Workflow Edition
**Last Updated:** 2025-11-20
