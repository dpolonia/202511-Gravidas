# Gravidas Pipeline - Quick Reference Card

---

## 🚀 Run Complete Pipeline

```bash
# Quick test (10 interviews, ~2 min, ~$0.80)
python scripts/run_workflow.py --preset quick_test

# Standard (100 interviews, ~30 min, ~$8)
python scripts/run_workflow.py --preset standard

# Production (1000 interviews, ~4 hours, ~$80)
python scripts/run_workflow.py --preset production
```

---

## 🤖 Choose AI Model

```bash
# Anthropic Claude (default, recommended)
python scripts/run_workflow.py --preset quick_test --model claude-sonnet-4-5-20250929

# OpenAI GPT
python scripts/run_workflow.py --preset quick_test --provider openai --model gpt-5

# Google Gemini (best value)
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-flash

# xAI Grok
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4-fast
```

---

## 🎯 Custom Number of Interviews

```bash
# 25 interviews
python scripts/run_workflow.py --personas 25 --records 25

# 50 interviews with specific model
python scripts/run_workflow.py --personas 50 --records 50 --model gemini-2.5-flash
```

---

## 🔧 Run Specific Stages

```bash
# Only conduct interviews
python scripts/run_workflow.py --stages conduct_interviews

# Only analyze existing interviews
python scripts/run_workflow.py --stages analyze_interviews

# Run multiple stages
python scripts/run_workflow.py --stages match_personas_records,conduct_interviews
```

---

## 📊 Available Models

| Model | Provider | Cost/1M | Speed | Best For |
|-------|----------|---------|-------|----------|
| `claude-sonnet-4-5-20250929` | Anthropic | $3/$15 | ⚡⚡ | Balanced (Recommended) |
| `gemini-2.5-flash` | Google | $0.15/$1.25 | ⚡⚡⚡ | Cost-effective |
| `gpt-5` | OpenAI | $1.25/$10 | ⚡⚡ | Quality |
| `grok-4-fast` | xAI | $0.20/$0.50 | ⚡⚡⚡ | Speed & value |
| `claude-opus-4-1` | Anthropic | $15/$75 | ⚡ | Maximum quality |
| `claude-haiku-4-5` | Anthropic | $1/$5 | ⚡⚡⚡ | Speed |

---

## 📁 Output Locations

```
data/personas/                  ← Generated personas
data/health_records/            ← FHIR health data
data/matched/                   ← Matched pairs
data/interviews/                ← Interview transcripts
data/analysis/                  ← Analysis results (CSV & JSON)
data/validation/                ← Validation reports
outputs/workflow_report.json    ← Workflow summary
logs/workflow.log               ← Execution logs
```

---

## ⚡ Most Used Commands

```bash
# 1. Test run (START HERE!)
python scripts/run_workflow.py --preset quick_test

# 2. Cost-effective 50 interviews
python scripts/run_workflow.py --personas 50 --records 50 --provider google --model gemini-2.5-flash

# 3. Re-analyze existing interviews
python scripts/run_workflow.py --stages analyze_interviews

# 4. Check results
cat data/analysis/interview_summary.csv
cat outputs/workflow_report.json
```

---

## 🆘 Quick Troubleshooting

```bash
# Check logs
tail -50 logs/workflow.log

# Check last report
cat outputs/workflow_report.json

# Resume from failed stage
python scripts/run_workflow.py --stages <failed_stage_name>

# Test with minimal data
python scripts/run_workflow.py --personas 5 --records 5
```

---

## 🔑 Setup (First Time Only)

```bash
# 1. Set API key (choose one)
export ANTHROPIC_API_KEY="your-key"
export OPENAI_API_KEY="your-key"
export GOOGLE_API_KEY="your-key"

# 2. Install dependencies
pip install -r requirements.txt

# 3. Test run
python scripts/run_workflow.py --preset quick_test
```

---

## 📚 Full Documentation

- **Complete Guide:** `RUN_PIPELINE.md`
- **Getting Started:** `GETTING_STARTED.md`
- **API Setup:** `API_KEY_SETUP.md`
- **File Structure:** `ACTIVE_FILES.md`
- **Cleanup Info:** `CLEANUP_SUMMARY.md`

---

## 💡 Pro Tips

✅ Always start with `--preset quick_test`
✅ Use `gemini-2.5-flash` for best value
✅ Check costs in analysis output
✅ Results auto-saved to `outputs/`
✅ Resume with `--stages` if interrupted

---

**First time?** Run this:
```bash
python scripts/run_workflow.py --preset quick_test
```
