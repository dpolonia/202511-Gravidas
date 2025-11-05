# Getting Started Guide

## Quick Start: 5 Minutes to Your First Interview

This guide will walk you through conducting AI-powered interviews with synthetic personas in just a few minutes.

---

## Prerequisites

Before you begin, ensure you have:

1. **Python 3.11+** installed
2. **Git** installed
3. **API Key** from at least one provider:
   - Anthropic Claude: https://console.anthropic.com/
   - OpenAI GPT: https://platform.openai.com/api-keys
   - Google Gemini: https://ai.google.dev/

---

## Step 1: Clone the Repository

```bash
# Clone the repository
git clone https://github.com/dpolonia/202511-Gravidas.git
cd 202511-Gravidas
```

---

## Step 2: Install Dependencies

```bash
# Install required Python packages
pip install -r requirements.txt
```

**Required packages:**
- anthropic (Claude API)
- openai (GPT API)
- google-generativeai (Gemini API)
- pyyaml, python-dotenv
- datasets, pandas, numpy, scipy

---

## Step 3: Get Your API Keys

### Option A: Use Environment Variables (Recommended)

Create a `.env` file in the project root:

```bash
# Copy the example file
cp .env.example .env

# Edit with your API keys
nano .env
```

Add your API keys:
```bash
ANTHROPIC_API_KEY=your-anthropic-key-here
OPENAI_API_KEY=your-openai-key-here
GOOGLE_API_KEY=your-google-key-here
XAI_API_KEY=your-xai-key-here
```

### Option B: Manual Entry (Interactive Mode)

You can enter API keys manually when running the interactive launcher (Step 4).

---

## Step 4: Run the Interactive Launcher

**This is the easiest way to get started!**

```bash
python scripts/interactive_interviews.py
```

You'll be guided through:

### 4.1 API Key Setup
```
═══════════════════════════════════════════════════════════════════
  API KEY SETUP
═══════════════════════════════════════════════════════════════════

Choose how to provide API keys:

  1. Load from .env file (if exists)
  2. Enter manually for this session
  3. Add key for specific provider

Selection (1-3):
```

**Choose option 1** if you created the `.env` file in Step 3.

### 4.2 Generate Test Data (First Time Only)

If no interview data exists, you'll see:

```
Missing Data Files

The matched personas file is required but doesn't exist:
  data/matched/matched_personas.json

Would you like to generate 10 test personas for testing?
  ✓ Quick setup (generates in <1 second)
  ✓ Includes diverse demographic profiles
  ✓ Ready for immediate use

Generate test data now? (yes/no): yes
```

**Type `yes`** to generate 10 sample personas.

### 4.3 Number of Interviews

```
Enter number of interviews to conduct (1-10000): 1
```

**Start with 1** to test the system.

### 4.4 Select Provider and Model

```
Available Providers:
  1. Anthropic (Claude) - 3 models
  2. OpenAI (GPT) - 3 models
  3. Google (Gemini) - 4 models

Select provider (1-3): 1
```

Then select a model:

```
#    Model                     Quality      Est. Cost    Est. Time    Notes
─────────────────────────────────────────────────────────────────────────────
1    Claude Sonnet 4.5         Excellent    $  0.04      0 minutes     ⭐ RECOMMENDED 🔄 BATCH
2    Claude Haiku 4.5          Very Good    $  0.01      0 minutes     🔄 BATCH
3    Claude Opus 4.1           Excellent    $  0.20      0 minutes     🔄 BATCH

Select model (number): 1
```

**Choose 1** for Claude Sonnet 4.5 (recommended).

### 4.5 Batch Mode (Optional)

If you selected 100+ interviews, you'll see:

```
💡 Batch API Available!
   - 50% cost savings
   - ~24 hour turnaround time
   - Ideal for large volumes (100+ interviews)

Use Batch API? (yes/no): no
```

**Type `no`** for your first test (real-time is faster for testing).

### 4.6 Confirm and Run

```
Interview Configuration:
  Provider:         Anthropic (Claude)
  Model:            Claude Sonnet 4.5
  Model ID:         claude-sonnet-4-5-20250929
  Quality:          Excellent
  Batch Mode:       ✗ No (Real-time)

  Num Interviews:   1
  Estimated Cost:   $0.04
  Estimated Time:   0 minutes

  Output Directory: data/interviews/

Proceed with interviews? (yes/no): yes
```

**Type `yes`** to start the interview!

---

## Step 5: View Results

After completion, you'll see:

```
[INFO] === AI Interview Script Started ===
[INFO] Provider: anthropic
[INFO] Model: claude-sonnet-4-5-20250929
[INFO] Conducting 1 interviews...
[INFO] [SUCCESS] Interview 1 completed (15 turns)
[INFO] === Interview Summary ===
[INFO] Successful interviews: 1
[INFO] Failed interviews: 0
[INFO] Total: 1
```

**Interview saved to:** `data/interviews/interview_00000.json`

### View the Interview

```bash
# View the interview transcript
cat data/interviews/interview_00000.json | python -m json.tool | less
```

Or open in any text editor:
```bash
# VS Code
code data/interviews/interview_00000.json

# Nano
nano data/interviews/interview_00000.json
```

---

## Alternative: Command Line Mode

If you prefer direct commands without the interactive menu:

```bash
# Quick test with Claude Sonnet 4.5 (1 interview)
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 1

# Batch mode for large volumes (1000 interviews)
python scripts/04_conduct_interviews.py \
  --provider google \
  --model gemini-2.5-flash \
  --count 1000 \
  --batch

# Using OpenAI GPT-5
python scripts/04_conduct_interviews.py \
  --provider openai \
  --model gpt-5 \
  --count 10
```

**Note:** Set the API key as environment variable first:

```bash
export ANTHROPIC_API_KEY="your-key-here"
python scripts/04_conduct_interviews.py --provider anthropic --model claude-sonnet-4-5-20250929 --count 1
```

---

## Common Workflows

### Workflow 1: Testing (1-10 interviews)

**Recommended model:** Claude Haiku 4.5 (fast and affordable)

```bash
python scripts/interactive_interviews.py
# Select: 5 interviews, Claude Haiku 4.5, Real-time mode
```

**Cost:** ~$0.05
**Time:** ~2 minutes

---

### Workflow 2: Small Dataset (100-1000 interviews)

**Recommended model:** Gemini 2.5 Flash (best price/performance)

```bash
python scripts/interactive_interviews.py
# Select: 500 interviews, Gemini 2.5 Flash, Batch mode
```

**Cost:** ~$78 (batch mode)
**Time:** ~24 hours (batch processing)

---

### Workflow 3: Large Dataset (10,000 interviews)

**Recommended model:** Claude Sonnet 4.5 (quality) or Gemini 2.5 Flash (cost)

```bash
python scripts/interactive_interviews.py
# Select: 10000 interviews, Claude Sonnet 4.5, Batch mode
```

**Cost:** $312.50 (batch mode)
**Time:** ~24 hours (batch processing)

**Alternative (cheapest):**
- Gemini 2.0 Flash: $56.25 (batch mode)

---

## Understanding the Output

Each interview JSON file contains:

```json
{
  "interview_id": 0,
  "timestamp": "2025-11-05T14:30:22",
  "provider": "anthropic",
  "model": "claude-sonnet-4-5-20250929",
  "persona": {
    "id": 1,
    "age": 28,
    "gender": "female",
    "description": "Emma is a 28-year-old elementary school teacher..."
  },
  "health_record": {
    "patient_id": "patient-1",
    "conditions": [...]
  },
  "protocol": {
    "name": "Prenatal Care Interview Protocol",
    "questions": [...]
  },
  "transcript": [
    {
      "speaker": "Interviewer",
      "text": "Can you tell me about your current life situation?",
      "timestamp": "2025-11-05T14:30:23"
    },
    {
      "speaker": "Participant",
      "text": "I'm a 28-year-old elementary school teacher...",
      "timestamp": "2025-11-05T14:30:25"
    }
  ],
  "metadata": {
    "total_turns": 15,
    "duration_seconds": 45
  }
}
```

---

## Troubleshooting

### Issue 1: "API key not configured"

**Error:**
```
[ERROR] Failed to initialize AI provider: Claude API key not configured
```

**Solution:**
```bash
# Check if .env file exists
cat .env

# If empty, add your API key
echo "ANTHROPIC_API_KEY=your-key-here" >> .env

# Or export directly
export ANTHROPIC_API_KEY="your-key-here"
```

---

### Issue 2: "Matched personas file not found"

**Error:**
```
[ERROR] Matched personas file not found: data/matched/matched_personas.json
```

**Solution:**
```bash
# Generate test data
python scripts/generate_test_data.py
```

Or run the interactive launcher, which will offer to generate test data automatically.

---

### Issue 3: "Model not found" (404 error)

**Error:**
```
[ERROR] Claude API error: model: claude-4.5-sonnet not found
```

**Solution:** Use the correct API model ID:
- ✅ Correct: `claude-sonnet-4-5-20250929`
- ❌ Wrong: `claude-4.5-sonnet`

See `docs/MODEL_NAMES.md` or `docs/AI_MODELS_DATABASE.csv` for all model IDs.

---

### Issue 4: Package installation fails

**Error:**
```
ERROR: Required packages not installed.
```

**Solution:**
```bash
# Install all dependencies
pip install -r requirements.txt

# If that fails, install individually
pip install anthropic openai google-generativeai
pip install pyyaml python-dotenv datasets pandas numpy scipy
```

---

## Next Steps

Once you've completed your first interview:

### 1. Scale Up
```bash
# Run 100 interviews
python scripts/interactive_interviews.py
# Select: 100 interviews, your preferred model
```

### 2. Analyze Results
```bash
# Count interviews
ls data/interviews/*.json | wc -l

# View all transcripts
for f in data/interviews/*.json; do
  echo "=== $f ==="
  python -m json.tool "$f" | head -50
done
```

### 3. Use Batch Mode for Large Volumes
```bash
# Generate 10,000 interviews with 50% cost savings
python scripts/interactive_interviews.py
# Select: 10000 interviews, Batch mode enabled
```

See `docs/BATCH_API.md` for batch processing instructions.

### 4. Explore Documentation

- **Model Comparison:** `docs/AI_MODELS_DATABASE.csv`
- **Cost Analysis:** `docs/COST_COMPARISON_10K_INTERVIEWS.csv`
- **Batch API Guide:** `docs/BATCH_API.md`
- **Model Names Reference:** `docs/MODEL_NAMES.md`
- **Full Tutorial:** `TUTORIAL.md`

---

## Cost Estimates

Based on 3,000 input tokens + 2,000 output tokens per interview:

| Interviews | Recommended Model | Mode | Cost |
|------------|-------------------|------|------|
| 1 | Claude Haiku 4.5 | Real-time | $0.01 |
| 10 | Claude Haiku 4.5 | Real-time | $0.10 |
| 100 | Gemini 2.5 Flash | Real-time | $3.13 |
| 100 | Gemini 2.5 Flash | Batch | $1.56 |
| 1,000 | Gemini 2.5 Flash | Batch | $15.63 |
| 10,000 | Gemini 2.5 Flash | Batch | $156.25 |
| 10,000 | Gemini 2.0 Flash | Batch | $56.25 |

---

## Support

**Documentation:**
- Quick Start: This file
- Full Tutorial: `TUTORIAL.md`
- API Keys Setup: `docs/API_KEY_SETUP.md`
- Batch Processing: `docs/BATCH_API.md`
- Model Reference: `docs/MODEL_NAMES.md`

**Repository:**
- GitHub: https://github.com/dpolonia/202511-Gravidas
- Branch: `claude/synthetic-gravidas-pipeline-011CUpt3YLnLffQE1REgHQoh`

**Common Commands:**
```bash
# Interactive mode (recommended)
python scripts/interactive_interviews.py

# Generate test data
python scripts/generate_test_data.py

# Command line mode
python scripts/04_conduct_interviews.py --help

# View logs
tail -f logs/04_conduct_interviews.log
```

---

## Summary

**Fastest way to start:**
1. `pip install -r requirements.txt`
2. Add API key to `.env` file
3. `python scripts/interactive_interviews.py`
4. Follow the prompts
5. View results in `data/interviews/`

**That's it!** You're now ready to conduct AI-powered interviews at scale. 🎉
