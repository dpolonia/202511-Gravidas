# Quick Start Guide - 5 Minutes to Your First Interview! 🚀

Get started with the Synthetic Gravidas Pipeline in just a few minutes.

---

## Option 1: Fastest Way (Recommended for Testing)

**Total time: ~2 minutes**

### Step 1: Setup Environment (30 seconds)

```bash
cd ~/202511-Gravidas

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Add API Key (30 seconds)

```bash
# Copy environment template
cp .env.example .env

# Edit and add your API key
nano .env
```

Add ONE of these (you only need one):
```bash
ANTHROPIC_API_KEY=sk-ant-YOUR-KEY-HERE
# OR
OPENAI_API_KEY=sk-proj-YOUR-KEY-HERE
# OR
GOOGLE_API_KEY=AIza-YOUR-KEY-HERE
```

Save and exit (Ctrl+X, then Y, then Enter)

### Step 3: Run Interactive Launcher (1 minute)

```bash
python scripts/interactive_interviews.py
```

The launcher will:
1. ✅ Detect your API key from .env
2. ✅ Offer to generate test data (10 sample personas)
3. ✅ Guide you through selecting a model
4. ✅ Show cost and time estimates
5. ✅ Run your first interview!

**Just follow the prompts and say "yes" when asked to generate test data!**

---

## Option 2: Manual Setup (Same Speed)

If you prefer to set everything up manually:

### Step 1: Generate Test Data

```bash
cd ~/202511-Gravidas
pip install -r requirements.txt
python scripts/generate_test_data.py
```

Output:
```
Generating test data for interview system...

✓ Created 10 matched persona-record pairs
✓ Saved to: data/matched/matched_personas.json

You can now run interviews!
```

### Step 2: Run an Interview

```bash
# Set your API key
export ANTHROPIC_API_KEY="sk-ant-YOUR-KEY-HERE"

# Run interview with command line
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-4.5-sonnet \
  --count 1

# OR use interactive mode
python scripts/interactive_interviews.py
```

---

## What Gets Created?

The test data generator creates:

```
data/
├── matched/
│   └── matched_personas.json    # 10 synthetic pregnant personas
└── interviews/
    └── interview_00001.json     # Your interview results
```

**Sample Personas:**
- Emma, 28, elementary school teacher, Boston
- Maria, 32, software engineer, San Francisco
- Aisha, 25, nurse, Chicago
- Jennifer, 35, accountant, Dallas
- ... and 6 more!

Each has:
- Realistic background and demographics
- Pregnancy-related health conditions
- Prenatal visit history
- Medications and observations

---

## Your First Interview

### Using Interactive Mode:

```
$ python scripts/interactive_interviews.py

╔═══════════════════════════════════════════════════════════════╗
║  API KEY MANAGEMENT                                           ║
╚═══════════════════════════════════════════════════════════════╝

Current API Keys Status:
  ✓ Anthropic (Claude)    sk-ant-...AA (from environment)

Options:
  2. Load from .env file
  3. Continue with current keys  ← SELECT THIS

╔═══════════════════════════════════════════════════════════════╗
║  MISSING DATA FILES                                           ║
╚═══════════════════════════════════════════════════════════════╝

⚠  The matched personas file doesn't exist yet.

You have two options:

  1. Generate test data (10 sample personas) - Quick!
     This creates sample data so you can try interviews immediately.

  2. Run the full pipeline first - Recommended for research

Generate test data now? (yes/no): yes  ← TYPE YES

Generating test data...
✓ Test data generated successfully!

╔═══════════════════════════════════════════════════════════════╗
║  INTERVIEW CONFIGURATION                                      ║
╚═══════════════════════════════════════════════════════════════╝

Enter number of interviews (1-10000): 1  ← START WITH 1

╔═══════════════════════════════════════════════════════════════╗
║  MODEL SELECTION (1 interview)                                ║
╚═══════════════════════════════════════════════════════════════╝

Available Providers:
  1. Anthropic (Claude)

Select provider: 1

#    Model                  Quality      Est. Cost    Est. Time
─────────────────────────────────────────────────────────────────
1    Claude 4.1 Opus       Excellent    $  1.65      1m
2    Claude 4.5 Sonnet     Excellent    $  0.39      1m  ⭐
3    Claude 4.5 Haiku      Very Good    $  0.13      1m
4    Claude 3 Haiku        Good         $  0.03      0m

Select model: 2  ← CHOOSE RECOMMENDED

╔═══════════════════════════════════════════════════════════════╗
║  CONFIRMATION                                                  ║
╚═══════════════════════════════════════════════════════════════╝

  Provider:         Anthropic (Claude)
  Model:            Claude 4.5 Sonnet
  Num Interviews:   1
  Estimated Cost:   $0.04
  Estimated Time:   1 minute

Proceed with interviews? yes  ← CONFIRM

[INFO] Starting interview with Emma, 28-year-old teacher...
[SUCCESS] Interview completed!
```

### View Results:

```bash
# See the interview transcript
cat data/interviews/interview_00000.json

# Or pretty print it
python -m json.tool data/interviews/interview_00000.json | less
```

---

## Next Steps

### Scale Up

Once you've tested with 1 interview:

```bash
# Try 10 interviews
python scripts/interactive_interviews.py
# Select: 10 interviews
```

### Use Full Pipeline

For research with real data (10,000 personas):

```bash
# Step 1: Retrieve personas (15-30 minutes)
python scripts/01_retrieve_personas.py

# Step 2: Generate health records (2-4 hours, requires Synthea)
# See docs/SYNTHEA_SETUP.md
python scripts/02_generate_health_records.py

# Step 3: Match personas (5-10 minutes)
python scripts/03_match_personas_records.py

# Step 4: Run interviews (varies by model)
python scripts/interactive_interviews.py
```

### Try Different Models

Compare quality across providers:

```bash
# Test with Claude
python scripts/interactive_interviews.py
# Select: Anthropic → Claude 4.5 Sonnet

# Test with OpenAI
python scripts/interactive_interviews.py
# Select: OpenAI → GPT-5

# Test with Gemini
python scripts/interactive_interviews.py
# Select: Google → Gemini 2.5 Pro
```

---

## Troubleshooting

### "No API keys available"

**Solution:**
```bash
# Check .env file exists
ls -la .env

# If not, create it
cp .env.example .env
nano .env  # Add your API key
```

### "Matched personas file not found"

**Solution:**
```bash
# Generate test data
python scripts/generate_test_data.py
```

### "Import error: No module named 'anthropic'"

**Solution:**
```bash
pip install -r requirements.txt
```

### Interview costs too high?

**Use cheaper models for testing:**
- Claude 3 Haiku: $0.03 per interview
- GPT-5 Nano: $0.01 per interview
- Gemini 2.0 Flash: $0.006 per interview

---

## Cost Examples

### Test Data (10 personas)

| Model | 1 Interview | 5 Interviews | 10 Interviews |
|-------|-------------|--------------|---------------|
| Claude 4.5 Sonnet | $0.04 | $0.20 | $0.39 |
| GPT-5 | $0.02 | $0.12 | $0.24 |
| Claude 3 Haiku | $0.003 | $0.02 | $0.03 |

### Full Pipeline (10,000 personas)

See [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md) for detailed cost breakdown.

---

## Summary

**Fastest path to first interview:**

```bash
# 1. Install
pip install -r requirements.txt

# 2. Add API key to .env
cp .env.example .env && nano .env

# 3. Run!
python scripts/interactive_interviews.py
# Say "yes" to generate test data
# Choose provider and model
# Confirm!
```

**Total time: 2 minutes** ⚡

**Cost: $0.04** 💰

**Result: Complete interview transcript!** 🎉

---

## Need Help?

- **Interactive Mode Guide:** [docs/INTERACTIVE_MODE.md](docs/INTERACTIVE_MODE.md)
- **API Key Setup:** [API_KEY_SETUP.md](API_KEY_SETUP.md)
- **Model Selection:** [docs/MODEL_SELECTION.md](docs/MODEL_SELECTION.md)
- **Full Tutorial:** [TUTORIAL.md](TUTORIAL.md)

---

## Ready? Let's Go! 🚀

```bash
cd ~/202511-Gravidas
python scripts/interactive_interviews.py
```

Follow the prompts and you'll have your first interview in minutes!
