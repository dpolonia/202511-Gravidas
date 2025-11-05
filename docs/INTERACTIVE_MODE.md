# Interactive Interview Mode

**The easiest way to run interviews with the Synthetic Gravidas Pipeline!**

## Quick Start

```bash
cd ~/202511-Gravidas
python scripts/interactive_interviews.py
```

That's it! The interactive launcher guides you through everything.

---

## Features

### ✨ **User-Friendly Interface**

- Step-by-step guided workflow
- No command-line arguments to remember
- Visual cost and time estimates
- Real-time model comparisons

### 🔑 **Flexible API Key Management**

Three ways to provide API keys:

**A. Load from Environment File (.env)**
```bash
# Copy the example file
cp .env.example .env

# Edit with your keys
nano .env

# Run interactive mode - it auto-loads .env
python scripts/interactive_interviews.py
```

**B. Use Existing config.yaml**

The launcher automatically detects keys in `config/config.yaml`

**C. Manual Entry During Runtime**

Enter API keys directly in the interactive menu - no file editing needed!

### 📊 **Smart Model Selection**

- View all available models for each provider
- See cost estimates for YOUR number of interviews
- See time estimates for completion
- Recommended models clearly marked ⭐
- Model descriptions and quality ratings

### 🌍 **Multi-Provider Support**

- **Anthropic (Claude)**: 4 models
- **OpenAI (GPT-5)**: 4 models
- **Google (Gemini)**: 4 models
- **xAI (Grok)**: 2 models *(coming soon)*

Easy to add more providers!

---

## How It Works

### Step 1: API Key Management

```
╔═══════════════════════════════════════════════════════════════════╗
║  API KEY MANAGEMENT                                               ║
╚═══════════════════════════════════════════════════════════════════╝

Current API Keys Status:

  ✓ Anthropic (Claude)           sk-ant-...x4AA (from environment)
  ✓ OpenAI (GPT-5)               sk-proj-...QoA (from environment)
  ✓ Google (Gemini)              AIza...WNw     (from config.yaml)
  ✗ xAI (Grok)                   No API key

Options:
  1. Add/Update API key manually
  2. Load from .env file
  3. Continue with current keys
  4. Exit

Select option (1-4):
```

**What you can do:**
- View which providers have API keys configured
- See where keys are loaded from (environment, config, manual)
- Add missing keys
- Update existing keys
- Load keys from .env file

### Step 2: Number of Interviews

```
╔═══════════════════════════════════════════════════════════════════╗
║  INTERVIEW CONFIGURATION                                          ║
╚═══════════════════════════════════════════════════════════════════╝

How many interviews would you like to conduct?

  Recommended ranges:
    • Testing: 1-10 interviews
    • Pilot study: 10-100 interviews
    • Full study: 100-10,000 interviews

Enter number of interviews (1-10000):
```

**Enter any number from 1 to 10,000**

This is used to calculate accurate cost and time estimates for each model.

### Step 3: Provider Selection

```
╔═══════════════════════════════════════════════════════════════════╗
║  MODEL SELECTION (1,000 interviews)                               ║
╚═══════════════════════════════════════════════════════════════════╝

Available Providers:

  1. Anthropic (Claude)              (4 models available)
  2. OpenAI (GPT-5)                  (4 models available)
  3. Google (Gemini)                 (4 models available)

Select provider (number):
```

**Only shows providers with configured API keys**

### Step 4: Model Selection with Cost/Time Estimates

```
╔═══════════════════════════════════════════════════════════════════╗
║  MODEL SELECTION - Anthropic (Claude)                             ║
╚═══════════════════════════════════════════════════════════════════╝
Number of interviews: 1,000

#    Model                     Quality      Est. Cost       Est. Time    Notes
─────────────────────────────────────────────────────────────────────────────────
1    Claude 4.1 Opus           Excellent    $ 165.00       1h 40m
2    Claude 4.5 Sonnet         Excellent    $  39.00       1h 2m        ⭐ RECOMMENDED
3    Claude 4.5 Haiku          Very Good    $  13.00       50m
4    Claude 3 Haiku            Good         $   3.25       40m

Description:
  1. Complex reasoning, autonomous agents, high-stakes analysis
  2. Agentic workhorse, advanced coding (Recommended)
  3. Near-frontier speed, fast applications
  4. Ultra-fast, simple Q&A, testing

Select model (number):
```

**For YOUR specific number of interviews, you see:**
- Exact cost estimate
- Exact time estimate
- Quality ratings
- Clear recommendations
- Model descriptions

### Step 5: Confirmation

```
╔═══════════════════════════════════════════════════════════════════╗
║  CONFIRMATION                                                      ║
╚═══════════════════════════════════════════════════════════════════╝

Interview Configuration:

  Provider:         Anthropic (Claude)
  Model:            Claude 4.5 Sonnet
  Model ID:         claude-4.5-sonnet
  Quality:          Excellent

  Num Interviews:   1,000
  Estimated Cost:   $39.00
  Estimated Time:   1h 2m

  Output Directory: data/interviews/

Proceed with interviews? (yes/no):
```

**Review everything before starting**

Type `yes` and interviews begin automatically!

---

## Example Usage Scenarios

### Scenario 1: First-Time Setup with .env

```bash
# 1. Copy environment template
cp .env.example .env

# 2. Edit with your API keys
nano .env
# Add: ANTHROPIC_API_KEY=sk-ant-...
# Add: OPENAI_API_KEY=sk-proj-...

# 3. Run interactive mode
python scripts/interactive_interviews.py

# 4. Choose option 2: "Load from .env file"
# 5. Select number of interviews: 10
# 6. Choose provider: Anthropic
# 7. Choose model: Claude 4.5 Sonnet
# 8. Confirm and run!
```

### Scenario 2: Quick Test with Manual Entry

```bash
# Run interactive mode
python scripts/interactive_interviews.py

# Choose option 1: "Add/Update API key manually"
# Enter your API key when prompted
# Select number of interviews: 5
# Choose cheapest model for testing
# Confirm and run!
```

### Scenario 3: Multiple Batches with Different Models

```bash
# Run interactive mode
python scripts/interactive_interviews.py

# First batch:
# - 100 interviews with Claude 4.5 Sonnet
# - Wait for completion

# System asks: "Run another batch?"
# Answer: yes

# Second batch:
# - 100 interviews with GPT-5 for comparison
# - Different model, same personas

# Compare results!
```

### Scenario 4: Add Grok Provider

```bash
# Run interactive mode
python scripts/interactive_interviews.py

# In API Key Management:
# Choose option 1: "Add/Update API key manually"
# Select: 4. xAI (Grok)
# Enter your Grok API key
# Continue with your interviews using Grok!
```

---

## Cost Examples

### For 100 Interviews:

| Provider | Model | Cost | Time |
|----------|-------|------|------|
| Anthropic | Claude 4.5 Sonnet | $3.90 | 6 min |
| OpenAI | GPT-5 | $2.38 | 7 min |
| Google | Gemini 2.5 Pro | $2.38 | 7 min |
| Anthropic | Claude 3 Haiku | $0.33 | 4 min |

### For 1,000 Interviews:

| Provider | Model | Cost | Time |
|----------|-------|------|------|
| Anthropic | Claude 4.5 Sonnet | $39.00 | 1h 2m |
| OpenAI | GPT-5 | $23.75 | 1h 11m |
| Google | Gemini 2.5 Pro | $23.75 | 1h 6m |
| OpenAI | GPT-5 Nano | $0.95 | 35m |

### For 10,000 Interviews:

| Provider | Model | Cost | Time |
|----------|-------|------|------|
| Anthropic | Claude 4.5 Sonnet | $390.00 | 10h 25m |
| OpenAI | GPT-5 | $237.50 | 11h 54m |
| Google | Gemini 2.5 Pro | $237.50 | 11h 6m |
| Anthropic | Claude 3 Haiku | $32.50 | 6h 40m |

**Note**: These are estimates. Actual costs may vary based on interview length and API pricing changes.

---

## Advanced Features

### Environment Variables

The launcher checks these environment variables (in order):

1. **From .env file** (if exists)
2. **From system environment**
3. **From config.yaml**
4. **Manual entry**

Supported variables:
```bash
ANTHROPIC_API_KEY
OPENAI_API_KEY
GOOGLE_API_KEY
XAI_API_KEY
HF_TOKEN
```

### Adding Custom Providers

To add a new AI provider (e.g., Cohere, Mistral):

1. Edit `scripts/interactive_interviews.py`
2. Add to `MODELS_DATABASE` dictionary:

```python
'cohere': {
    'name': 'Cohere',
    'models': {
        'command-r-plus': {
            'name': 'Command R+',
            'cost_input': 3.0,
            'cost_output': 15.0,
            'tokens_per_second': 70,
            'quality': 'Excellent',
            'description': 'Advanced reasoning and generation'
        }
    }
}
```

3. The launcher automatically detects and shows new providers!

### Batch Processing

The launcher asks after each batch completes:

```
Run another batch? (yes/no):
```

This lets you:
- Run multiple batches without restarting
- Test different models
- Continue after breaks
- Compare model performance

---

## Troubleshooting

### "No API keys available"

**Solution**: Add at least one API key:
- Option 1: Create `.env` file with your keys
- Option 2: Edit `config/config.yaml` with your keys
- Option 3: Use manual entry in the interactive menu

### "Invalid API key"

**Solution**: Check that your API key is correct:
- Anthropic keys start with `sk-ant-`
- OpenAI keys start with `sk-proj-` or `sk-`
- Google keys start with `AIza`
- No extra spaces or quotes

### Interviews fail to start

**Solution**: Make sure you have:
- Matched personas file at `data/matched/matched_personas.json`
- Interview protocol at `Script/interview_protocols/`
- Run previous pipeline steps first (retrieve, generate, match)

### Cost estimates seem wrong

**Note**: Estimates are based on average:
- Input tokens: 3,000 per interview
- Output tokens: 2,000 per interview

Actual usage may vary based on:
- Interview protocol complexity
- Response length
- Model behavior

---

## Tips

### 💡 Start Small

Always test with 5-10 interviews before running thousands:

```
Enter number of interviews: 5
```

This helps you:
- Verify API keys work
- Check output quality
- Confirm costs match estimates

### 💡 Use Recommended Models

Models marked with ⭐ offer the best balance of quality and cost.

### 💡 Compare Models

Run small batches with different models to find your preference:

```bash
# First run: 10 interviews with Claude
# Second run: 10 interviews with GPT
# Third run: 10 interviews with Gemini
# Compare results and choose your favorite!
```

### 💡 Budget Testing

Use cheapest models for testing protocols:
- Claude 3 Haiku: $0.33 per 100 interviews
- GPT-5 Nano: $0.10 per 100 interviews
- Gemini 2.0 Flash: $0.06 per 100 interviews

### 💡 Production Quality

Use recommended models for final data collection:
- Claude 4.5 Sonnet: Best overall quality
- GPT-5: Strong reasoning
- Gemini 2.5 Pro: Good balance

---

## Command-Line Alternative

If you prefer the command line, you can still use:

```bash
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-4.5-sonnet \
  --count 100
```

But the interactive mode is much easier! 😊

---

## Summary

The interactive launcher provides:

- ✅ Easy API key management (3 methods)
- ✅ Visual model comparison
- ✅ Accurate cost estimates
- ✅ Time estimates
- ✅ Support for all providers
- ✅ Easy to add custom providers
- ✅ No command-line arguments needed
- ✅ Batch processing support

**Just run:**
```bash
python scripts/interactive_interviews.py
```

And follow the prompts!
