# Interactive Pipeline - Quick Start Guide

**The Easiest Way to Run the Gravidas Pipeline**

---

## 🚀 How to Start

Just run this command:

```bash
python run_interactive.py
```

That's it! The script will guide you through everything.

---

## 📋 Step-by-Step Walkthrough

### Step 1: Launch the Interactive Runner

```bash
python run_interactive.py
```

You'll see:
```
================================================================================
              GRAVIDAS SYNTHETIC INTERVIEW PIPELINE
================================================================================

ℹ Interactive Setup - Choose Your Configuration
```

---

### Step 2: Choose Number of Interviews

The script will show you:

```
Step 1: Choose Number of Interviews
------------------------------------

Available Presets:

  1. Quick Test       - 10 interviews   (~2-3 min,  ~$0.80)
  2. Standard         - 100 interviews  (~30 min,   ~$8)
  3. Production       - 1000 interviews (~4 hours,  ~$80)
  4. Custom           - Choose your own number

Select option (1-4):
```

**What to type:**

| Type | What You Get | Time | Cost (Approx) |
|------|--------------|------|---------------|
| `1` | 10 interviews (Quick Test) | ~5 minutes | ~$0.80 |
| `2` | 100 interviews (Standard) | ~1 hour | ~$8.00 |
| `3` | 1000 interviews (Production) | ~8 hours | ~$80.00 |
| `4` | Custom number (you choose) | Varies | Varies |

**Recommendation for first-time users:** Type `1` (Quick Test)

If you choose `4` (Custom), you'll be asked:
```
Enter number of interviews (1-10000):
```
Type any number from 1 to 10,000.

---

### Step 3: Choose AI Model

The script will show you all available models:

```
Step 2: Choose AI Model
------------------------

Available Models:

Anthropic Claude:
  1. Claude Sonnet 4.5 (Recommended)
     → Best balance of quality and cost
     → Cost: $3/$15 per 1M tokens | Speed: Medium | Quality: Excellent

  2. Claude Opus 4.1
     → Maximum quality, highest cost
     → Cost: $15/$75 per 1M tokens | Speed: Slow | Quality: Exceptional

  3. Claude Haiku 4.5
     → Fast and economical
     → Cost: $1/$5 per 1M tokens | Speed: Fast | Quality: Very Good

Google Gemini:
  4. Gemini 2.5 Flash (Best Value ⭐)
     → Most cost-effective option
     → Cost: $0.15/$1.25 per 1M tokens | Speed: Very Fast | Quality: Very Good

  5. Gemini 2.5 Pro
     → Excellent quality, good value
     → Cost: $1.25/$10 per 1M tokens | Speed: Medium | Quality: Excellent

OpenAI:
  6. GPT-5
     → Latest flagship model
     → Cost: $1.25/$10 per 1M tokens | Speed: Medium | Quality: Excellent

  7. GPT-5 Mini
     → Fast and cost-effective
     → Cost: $0.25/$2 per 1M tokens | Speed: Fast | Quality: Very Good

xAI Grok:
  8. Grok 4 Fast (Fastest)
     → Speed and value optimized
     → Cost: $0.20/$0.50 per 1M tokens | Speed: Very Fast | Quality: Very Good

  9. Grok 4
     → Most capable Grok model
     → Cost: $3/$15 per 1M tokens | Speed: Medium | Quality: Excellent

Select model (1-9):
```

**What to type:**

| Type | Model | Best For |
|------|-------|----------|
| `1` | Claude Sonnet 4.5 | **Best overall balance** (Recommended) ⭐ |
| `4` | Gemini 2.5 Flash | **Cheapest option** 💰 |
| `8` | Grok 4 Fast | **Fastest execution** ⚡ |
| `6` | GPT-5 | High quality |
| `2` | Claude Opus 4.1 | Maximum quality (expensive) |

**Recommendation for first-time users:** Type `1` (Claude Sonnet) or `4` (Gemini Flash)

---

### Step 4: Review and Confirm

The script will show you a summary:

```
Step 3: Confirm and Run
------------------------

================================================================================
Your Configuration:
================================================================================
  Interviews:       10
  AI Provider:      Anthropic
  Model:            Claude Sonnet 4.5
  Estimated Cost:   $0.56 - $1.04
  Estimated Time:   ~2 minutes
================================================================================

Proceed with this configuration? (yes/no):
```

**What to type:**
- Type `yes` and press Enter to start the pipeline
- Type `no` to cancel

---

### Step 5: Watch It Run

The pipeline will run all 6 stages automatically:

```
================================================================================
🔄 STAGE: GENERATE PERSONAS
================================================================================
✅ Stage 'generate_personas' completed successfully (26.48s)

================================================================================
🔄 STAGE: GENERATE HEALTH RECORDS
================================================================================
✅ Stage 'generate_health_records' completed successfully (16.87s)

================================================================================
🔄 STAGE: MATCH PERSONAS RECORDS
================================================================================
✅ Stage 'match_personas_records' completed successfully (1.85s)

================================================================================
🔄 STAGE: CONDUCT INTERVIEWS
================================================================================
✅ Stage 'conduct_interviews' completed successfully (2784.83s)

================================================================================
🔄 STAGE: ANALYZE INTERVIEWS
================================================================================
✅ Stage 'analyze_interviews' completed successfully (12.45s)

================================================================================
🔄 STAGE: VALIDATE IMPLEMENTATION
================================================================================
✅ Stage 'validate_implementation' completed successfully (3.21s)

🎯 Overall Status: SUCCESS
```

---

### Step 6: Find Your Results

After completion, the script shows you where to find results:

```
Pipeline Complete!

✓ All stages completed successfully
ℹ Results saved to:
  • data/analysis/interview_summary.csv
  • data/analysis/interview_analysis.json
  • outputs/workflow_report.json

View results:
  cat data/analysis/interview_summary.csv
  cat outputs/workflow_report.json
```

**Check your results:**

```bash
# Analysis spreadsheet
cat data/analysis/interview_summary.csv

# Analysis JSON
cat data/analysis/interview_analysis.json

# Workflow summary
cat outputs/workflow_report.json

# Interview transcripts
ls data/interviews/
```

---

## 💡 Complete Examples

### Example 1: First-Time User (Recommended)

```bash
$ python run_interactive.py

Select option (1-4): 1          # Quick Test (10 interviews)
Select model (1-9): 1           # Claude Sonnet (best balance)
Proceed? (yes/no): yes          # Confirm and run

✓ Pipeline runs for ~5 minutes
✓ Results saved to data/analysis/
✓ Total cost: ~$0.80
```

---

### Example 2: Budget-Conscious User

```bash
$ python run_interactive.py

Select option (1-4): 1          # Quick Test (10 interviews)
Select model (1-9): 4           # Gemini Flash (cheapest)
Proceed? (yes/no): yes          # Confirm and run

✓ Pipeline runs for ~5 minutes
✓ Results saved to data/analysis/
✓ Total cost: ~$0.10
```

---

### Example 3: Custom Number

```bash
$ python run_interactive.py

Select option (1-4): 4          # Custom
Enter number: 25                # 25 interviews
Select model (1-9): 8           # Grok Fast (fastest & cheap)
Proceed? (yes/no): yes          # Confirm and run

✓ Pipeline runs for ~15 minutes
✓ Results saved to data/analysis/
✓ Total cost: ~$0.13
```

---

### Example 4: Production Run

```bash
$ python run_interactive.py

Select option (1-4): 2          # Standard (100 interviews)
Select model (1-9): 4           # Gemini Flash (cost-effective)
Proceed? (yes/no): yes          # Confirm and run

✓ Pipeline runs for ~1 hour
✓ Results saved to data/analysis/
✓ Total cost: ~$1.00
```

---

## 🎯 Quick Decision Guide

### Choose Number of Interviews

**First time or testing?**
→ Type `1` (Quick Test - 10 interviews)

**Regular analysis or research?**
→ Type `2` (Standard - 100 interviews)

**Large-scale project?**
→ Type `3` (Production - 1000 interviews)

**Specific number in mind?**
→ Type `4` (Custom)

---

### Choose AI Model

**Want best overall quality for the price?**
→ Type `1` (Claude Sonnet) ⭐

**Want cheapest option?**
→ Type `4` (Gemini Flash) 💰

**Want fastest execution?**
→ Type `8` (Grok Fast) ⚡

**Want maximum quality (cost no object)?**
→ Type `2` (Claude Opus)

**Want OpenAI's latest?**
→ Type `6` (GPT-5)

---

## ⚠️ Before You Start

### 1. Make Sure API Key is Set

The script will check for you, but you can verify:

```bash
# Check your .env file
cat .env | grep API_KEY
```

You should see:
```
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...
```

If a key is missing, add it to `.env`:
```bash
echo "ANTHROPIC_API_KEY='your-key-here'" >> .env
```

### 2. Check You Have Enough Credits

Make sure your chosen provider has enough API credits:
- Quick Test: ~$0.10 - $1.00
- Standard: ~$1.00 - $10.00
- Production: ~$10.00 - $100.00

---

## 🆘 Troubleshooting

### "Cancelled by user"
**What happened:** You pressed Ctrl+C
**Solution:** Just run `python run_interactive.py` again

### "API key not found"
**What happened:** The script can't find your API key
**Solution:**
```bash
# Set the key for your chosen provider
export ANTHROPIC_API_KEY='your-key-here'
# Or add it to .env file
echo "ANTHROPIC_API_KEY='your-key-here'" >> .env
```

### Want to Start Over?
**Action:** Press `Ctrl+C` at any prompt, then run the script again

### Want to Cancel During Run?
**Action:** Press `Ctrl+C` - you can resume later using:
```bash
python scripts/run_workflow.py --stages <failed_stage_name>
```

---

## 📊 Cost Reference

### For 10 Interviews (Quick Test):
- Claude Sonnet: ~$0.80
- Gemini Flash: ~$0.10
- Grok Fast: ~$0.05
- GPT-5: ~$0.55
- Claude Opus: ~$4.00

### For 100 Interviews (Standard):
- Claude Sonnet: ~$8.00
- Gemini Flash: ~$1.00
- Grok Fast: ~$0.50
- GPT-5: ~$5.40
- Claude Opus: ~$40.00

### For 1000 Interviews (Production):
- Claude Sonnet: ~$80.00
- Gemini Flash: ~$10.00
- Grok Fast: ~$5.00
- GPT-5: ~$54.00
- Claude Opus: ~$400.00

---

## ✅ After Running

### Check Results

```bash
# Quick overview
cat outputs/workflow_report.json

# Detailed analysis (spreadsheet)
cat data/analysis/interview_summary.csv

# Detailed analysis (JSON)
cat data/analysis/interview_analysis.json

# Individual interviews
ls data/interviews/
cat data/interviews/interview_0.json
```

### Run Again with Different Settings

```bash
# Just run the interactive script again
python run_interactive.py

# Choose different number or model
# Previous results are preserved in data/ folders
```

---

## 🎓 Tips for Success

### 1. Start Small
Always test with Quick Test (10 interviews) first before running larger batches.

### 2. Choose Right Model
- **Learning/Testing:** Use Grok Fast or Gemini Flash
- **Production (Quality):** Use Claude Sonnet
- **Production (Budget):** Use Gemini Flash
- **Maximum Quality:** Use Claude Opus

### 3. Monitor Progress
The script shows real-time progress for each stage. You can also check logs:
```bash
# In another terminal
tail -f logs/workflow.log
```

### 4. Save Money
Start with cheaper models (Gemini Flash, Grok Fast) for testing, then use higher-quality models (Claude Sonnet) for final production runs.

---

## 🔄 Running Multiple Times

The interactive script is stateless - you can run it as many times as you want with different configurations:

```bash
# Run 1: Quick test with Claude
python run_interactive.py
# Select 1 (Quick Test), 1 (Claude Sonnet)

# Run 2: Test with Gemini
python run_interactive.py
# Select 1 (Quick Test), 4 (Gemini Flash)

# Run 3: Production with Grok
python run_interactive.py
# Select 2 (Standard), 8 (Grok Fast)
```

Each run creates new results. Previous results are preserved unless you clean them.

---

## 📖 More Information

- **Complete End-to-End Guide:** `cat RUN_END_TO_END.md`
- **Provider Comparison:** `cat PROVIDER_USAGE.md`
- **Quick Reference:** `cat QUICK_REFERENCE.md`
- **Full Documentation:** `cat INTERACTIVE_GUIDE.md`

---

## 🚀 Ready to Start?

Just run:

```bash
python run_interactive.py
```

Then:
1. Choose number of interviews (type `1` for quick test)
2. Choose AI model (type `1` for Claude Sonnet or `4` for Gemini Flash)
3. Type `yes` to confirm
4. Wait for results!

**That's it! The pipeline handles everything else automatically.** 🎉

---

## 📝 Summary Cheat Sheet

```bash
# START
python run_interactive.py

# CHOOSE INTERVIEWS
1 → Quick Test (10 interviews)
2 → Standard (100 interviews)
3 → Production (1000 interviews)
4 → Custom number

# CHOOSE MODEL
1 → Claude Sonnet (Best Balance) ⭐
4 → Gemini Flash (Best Value) 💰
8 → Grok Fast (Fastest) ⚡

# CONFIRM
yes → Start pipeline

# CHECK RESULTS
cat data/analysis/interview_summary.csv
cat outputs/workflow_report.json
```

---

**Happy Interviewing! 🎉**
