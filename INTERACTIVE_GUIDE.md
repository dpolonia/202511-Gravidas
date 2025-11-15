# Interactive Pipeline Runner - User Guide

**Easy, menu-driven interface to run the Gravidas pipeline**

---

## 🚀 Quickest Way to Run

```bash
# Option 1: Run the Python script directly
python run_interactive.py

# Option 2: Use the shell wrapper
./run.sh
```

That's it! The script will guide you through the rest.

---

## 📋 What the Interactive Runner Does

The interactive runner provides a **user-friendly menu** where you can:

1. ✅ **Choose number of interviews** - Pick from presets or enter custom number
2. ✅ **Select AI model** - See all available models with costs and speeds
3. ✅ **Review your configuration** - See estimated cost and time before running
4. ✅ **Run the pipeline** - Automatically execute with your selections
5. ✅ **Get results** - See where to find your output files

**No need to remember command-line arguments!**

---

## 📖 Step-by-Step Walkthrough

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

You'll be presented with options:

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

**What to choose:**
- **Option 1 (Quick Test)** - Perfect for first-time users or testing
- **Option 2 (Standard)** - Good for regular production runs
- **Option 3 (Production)** - Large-scale data generation
- **Option 4 (Custom)** - Enter any number from 1 to 10,000

**Example:** Type `1` and press Enter for quick test

---

### Step 3: Choose AI Model

You'll see all available models with details:

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

**Recommendations:**
- **Option 1 (Claude Sonnet)** - Best overall balance (default)
- **Option 4 (Gemini Flash)** - Best value for money ⭐
- **Option 8 (Grok 4 Fast)** - Fastest execution
- **Option 2 (Claude Opus)** - Highest quality

**Example:** Type `1` for Claude Sonnet (recommended)

---

### Step 4: Confirm and Run

You'll see a summary of your configuration:

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

**What happens next:**
1. Type `yes` to proceed (or `no` to cancel)
2. The script automatically runs the pipeline with your selections
3. Progress is shown in real-time
4. Results are saved to `data/` and `outputs/`

---

## 💡 Example Sessions

### Example 1: Quick Test with Default Model

```bash
$ python run_interactive.py

Select option (1-4): 1          # Quick Test
Select model (1-9): 1           # Claude Sonnet
Proceed? (yes/no): yes

✓ Pipeline runs automatically
✓ Results saved to data/analysis/
```

---

### Example 2: Custom Run with Budget Model

```bash
$ python run_interactive.py

Select option (1-4): 4          # Custom
Enter number: 25                # 25 interviews

Select model (1-9): 4           # Gemini Flash (cheapest)
Proceed? (yes/no): yes

✓ 25 interviews with Gemini Flash
✓ Total cost: ~$0.50
```

---

### Example 3: Production Run with Best Quality

```bash
$ python run_interactive.py

Select option (1-4): 2          # Standard (100 interviews)
Select model (1-9): 2           # Claude Opus (best quality)
Proceed? (yes/no): yes

✓ 100 interviews with Claude Opus
✓ Total cost: ~$40-50
✓ Time: ~30 minutes
```

---

## 🎯 Model Selection Guide

### Choose by Priority

**Best Overall Balance:**
```
Option 1: Claude Sonnet 4.5
```

**Best Value (Lowest Cost):**
```
Option 4: Gemini 2.5 Flash ⭐
```

**Fastest Speed:**
```
Option 8: Grok 4 Fast
```

**Highest Quality:**
```
Option 2: Claude Opus 4.1
```

---

## 📊 Cost Estimates

The script automatically calculates estimated costs:

| Interviews | Claude Sonnet | Gemini Flash | GPT-5 | Grok 4 Fast |
|-----------|---------------|--------------|-------|-------------|
| 10        | ~$0.80        | ~$0.10       | ~$0.55| ~$0.05      |
| 25        | ~$2.00        | ~$0.25       | ~$1.35| ~$0.13      |
| 50        | ~$4.00        | ~$0.50       | ~$2.70| ~$0.25      |
| 100       | ~$8.00        | ~$1.00       | ~$5.40| ~$0.50      |

*Estimates may vary ±30% based on actual conversation length*

---

## 🔍 After Running

### Where to Find Results

```bash
# Analysis results (CSV)
cat data/analysis/interview_summary.csv

# Analysis results (JSON)
cat data/analysis/interview_analysis.json

# Workflow report
cat outputs/workflow_report.json

# Execution logs
tail -50 logs/workflow.log

# Interview transcripts
ls data/interviews/
```

### Check the Summary

```bash
# Quick overview
cat outputs/workflow_report.json

# Detailed analysis
cat data/analysis/interview_summary.csv
```

---

## ⚠️ Prerequisites

Before running, make sure you have:

### 1. API Key Set

```bash
# For Anthropic (Claude)
export ANTHROPIC_API_KEY='your-key-here'

# For OpenAI (GPT)
export OPENAI_API_KEY='your-key-here'

# For Google (Gemini)
export GOOGLE_API_KEY='your-key-here'

# For xAI (Grok)
export XAI_API_KEY='your-key-here'
```

**The script will check for the correct API key automatically!**

See `API_KEY_SETUP.md` for detailed instructions.

### 2. Dependencies Installed

```bash
pip install -r requirements.txt
```

---

## 🆘 Troubleshooting

### "API key not found" Error

**Problem:** The script says your API key isn't set

**Solution:**
```bash
# Set the appropriate key for your chosen provider
export ANTHROPIC_API_KEY='your-key-here'

# Verify it's set
echo $ANTHROPIC_API_KEY
```

### Want to Cancel During Setup

**Action:** Press `Ctrl+C` at any prompt to cancel

### Wrong Selection

**Action:** Just press `Ctrl+C` and start over - it's fast!

### Want to See Command Before Running

**Action:** The script shows you the exact command before running:
```
Running command: python scripts/run_workflow.py --preset quick_test --model claude-sonnet-4-5-20250929
```

---

## 🔄 Running Again

Just run the script again - it's completely stateless:

```bash
python run_interactive.py
```

You can make different selections each time!

---

## 💪 Advanced: Bypassing Interactive Mode

If you already know what you want:

```bash
# Use command-line directly (faster for repeated runs)
python scripts/run_workflow.py --preset quick_test --model claude-sonnet-4-5-20250929

# See all options
python scripts/run_workflow.py --help
```

But for ease of use, the interactive runner is recommended!

---

## 📚 Related Documentation

- **Command-Line Options:** `RUN_PIPELINE.md`
- **Quick Reference:** `QUICK_REFERENCE.md`
- **API Setup:** `API_KEY_SETUP.md`
- **Full Guide:** `GETTING_STARTED.md`

---

## ✨ Features

✅ **No command-line arguments to remember**
✅ **See all options with costs before choosing**
✅ **Automatic cost and time estimation**
✅ **API key validation**
✅ **Beautiful colored output**
✅ **Confirmation before running**
✅ **Helpful error messages**
✅ **Results locations shown after completion**

---

## 🎓 Tips for First-Time Users

1. **Start with Quick Test (Option 1)**
   - Only 10 interviews
   - Costs less than $1
   - Takes 2-3 minutes
   - Perfect for testing

2. **Use Claude Sonnet or Gemini Flash**
   - Claude Sonnet: Best balance
   - Gemini Flash: Best value

3. **Check your API key first**
   ```bash
   echo $ANTHROPIC_API_KEY
   ```

4. **Review the summary before confirming**
   - Check the estimated cost
   - Confirm you have enough API credits

5. **Start over if needed**
   - Just press Ctrl+C and run again
   - No harm in restarting

---

## 🚀 Ready to Run?

```bash
python run_interactive.py
```

**That's it!** The script will guide you through the rest with clear prompts and helpful information.

Enjoy your AI-powered synthetic interviews! 🎉
