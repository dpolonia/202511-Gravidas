# Workflow Quick Reference Card

## One-Line Commands for Common Scenarios

### Testing & Development

```bash
# Quick system test (7 min, $0.05)
python run_complete_workflow.py --quick-test

# Fast iteration test (2 min, $0.02)
python run_complete_workflow.py --personas 5 --records 5 --interviews 2 --provider google --model gemini-2.5-flash
```

### Standard Research Runs

```bash
# Standard run with Claude (3 hrs, $10)
python run_complete_workflow.py --personas 100 --records 100 --interviews 50

# Budget run with Gemini (3 hrs, $5)
python run_complete_workflow.py --personas 100 --records 100 --interviews 50 --provider google --model gemini-2.5-flash

# Premium quality with Opus (5 hrs, $80)
python run_complete_workflow.py --personas 100 --records 100 --interviews 50 --provider anthropic --model claude-opus-4-1
```

### Interview Type Studies

```bash
# Prenatal Care (DEFAULT)
python run_complete_workflow.py --personas 50 --interviews 25

# High-Risk Pregnancy
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/high_risk_pregnancy.json

# Mental Health Screening
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/mental_health_screening.json

# Genetic Counseling
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/genetic_counseling.json

# Postpartum Care
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/postpartum_care.json
```

### Provider Comparisons

```bash
# Compare all 4 providers (run separately)
python run_complete_workflow.py --quick-test --provider anthropic --model claude-haiku-4-5
python run_complete_workflow.py --quick-test --provider openai --model gpt-4o-mini
python run_complete_workflow.py --quick-test --provider google --model gemini-2.5-flash
python run_complete_workflow.py --quick-test --provider xai --model grok-4-fast
```

### Large Production Runs

```bash
# Large dataset for publication (40 hrs, $120)
python run_complete_workflow.py --personas 1000 --records 1000 --interviews 500 --provider anthropic --model claude-sonnet-4-5

# Budget large run (30 hrs, $50)
python run_complete_workflow.py --personas 1000 --records 1000 --interviews 500 --provider google --model gemini-2.5-flash
```

---

## Variable Reference

| Variable | What It Controls | Typical Values |
|----------|------------------|----------------|
| `--personas N` | Number of synthetic patient profiles | 5-1000 |
| `--records N` | Number of FHIR health records | 5-1000 |
| `--interviews N` | Number of AI interviews to conduct | 2-500 |
| `--provider` | Which AI company to use | anthropic, openai, google, xai |
| `--model` | Specific AI model | claude-haiku-4-5, gpt-4o-mini, gemini-2.5-flash, grok-4-fast |
| `--protocol` | Interview topic/focus | prenatal_care, high_risk_pregnancy, mental_health_screening, genetic_counseling, postpartum_care |

---

## AI Models Quick Reference

### Cost-Optimized (Fastest & Cheapest)
```bash
--provider google --model gemini-2.5-flash      # $0.15/$1.25 per 1M - FASTEST
--provider anthropic --model claude-haiku-4-5   # $1/$5 per 1M
--provider openai --model gpt-4o-mini           # $0.15/$0.60 per 1M
--provider xai --model grok-4-fast              # $0.20/$0.50 per 1M
```

### Balanced (Recommended)
```bash
--provider anthropic --model claude-sonnet-4-5  # $3/$15 per 1M - RECOMMENDED
--provider google --model gemini-2.5-pro        # $1.25/$10 per 1M
--provider openai --model gpt-4o                # $2.50/$10 per 1M
--provider xai --model grok-4                   # $3/$15 per 1M
```

### Premium Quality
```bash
--provider anthropic --model claude-opus-4-1    # $15/$75 per 1M - BEST QUALITY
--provider openai --model gpt-5                 # $1.25/$10 per 1M
```

---

## Interview Protocols Quick Reference

| Protocol | Focus Area | Use When |
|----------|------------|----------|
| `prenatal_care.json` | Routine prenatal visits | Standard pregnancy care |
| `high_risk_pregnancy.json` | Complications, risks | Medical complexity, complications |
| `mental_health_screening.json` | Psychological wellbeing | Mental health research |
| `genetic_counseling.json` | Genetic risks, testing | Hereditary conditions |
| `postpartum_care.json` | Post-birth recovery | Postpartum period focus |
| `pregnancy_experience.json` | Overall journey | Qualitative research |

---

## Time & Cost Estimates

| Scale | Personas | Records | Interviews | Time | Cost (Claude Haiku) | Cost (Gemini Flash) |
|-------|----------|---------|------------|------|---------------------|---------------------|
| **Quick Test** | 10 | 10 | 3 | 7 min | $0.05 | $0.02 |
| **Small** | 25 | 25 | 10 | 30 min | $0.50 | $0.20 |
| **Medium** | 50 | 50 | 25 | 1.5 hrs | $2 | $1 |
| **Standard** | 100 | 100 | 50 | 3 hrs | $10 | $5 |
| **Large** | 500 | 500 | 200 | 15 hrs | $60 | $30 |
| **Production** | 1000 | 1000 | 500 | 40 hrs | $150 | $75 |

---

## Output Locations

After each run, find your data here:
```
data/personas/personas.json              # Synthetic patient profiles
data/health_records/health_records.json  # FHIR medical records
data/matched/matched_personas.json       # Matched pairs
data/interviews/interview_*.json         # AI interview transcripts
data/analysis/interview_summary.csv      # Statistical analysis
outputs/complete_workflow_report.json    # Execution summary
```

Archives saved to: `archives/workflow_run_YYYYMMDD_HHMMSS/`

---

## Most Common Commands

```bash
# 1. Test everything is working
python run_complete_workflow.py --quick-test

# 2. Standard research run
python run_complete_workflow.py --personas 100 --interviews 50

# 3. Budget large dataset
python run_complete_workflow.py --personas 500 --interviews 200 --provider google --model gemini-2.5-flash

# 4. High-quality clinical study
python run_complete_workflow.py --personas 100 --interviews 50 --provider anthropic --model claude-opus-4-1 --protocol Script/interview_protocols/high_risk_pregnancy.json

# 5. Multi-protocol study (run 3 times)
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/prenatal_care.json
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/mental_health_screening.json
python run_complete_workflow.py --personas 50 --interviews 25 --protocol Script/interview_protocols/high_risk_pregnancy.json
```

---

## Getting Help

```bash
# Show all options
python run_complete_workflow.py --help

# View full customization guide
cat WORKFLOW_CUSTOMIZATION_GUIDE.md

# Check system status
python run_complete_workflow.py --quick-test
```

---

**Quick Start:** `python run_complete_workflow.py --quick-test`
**Full Guide:** `WORKFLOW_CUSTOMIZATION_GUIDE.md`
**Project Docs:** `RPATRICIO.md`
