# Multi-Provider Usage Guide

**All AI providers are now ACTIVE and ready to use!**

---

## 🌟 Available Providers

All 4 providers are configured and enabled in your `.env` file:

| Provider | Model | Cost/1M Tokens | Speed | Best For |
|----------|-------|----------------|-------|----------|
| **Anthropic** | claude-sonnet-4-5-20250929 | $3/$15 | ⚡⚡ | Best balance ⭐ |
| **OpenAI** | gpt-5 | $1.25/$10 | ⚡⚡ | High quality |
| **Google** | gemini-2.5-flash | $0.15/$1.25 | ⚡⚡⚡ | Best value 💰 |
| **xAI** | grok-4-fast | $0.20/$0.50 | ⚡⚡⚡ | Fastest ⚡ |

---

## 🚀 Quick Start - Switch Providers

### Method 1: Command Line (Fastest)

```bash
# Use Anthropic Claude (Default - Best Balance)
python scripts/run_workflow.py --preset quick_test --provider anthropic

# Use Google Gemini (Best Value)
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-flash

# Use OpenAI GPT-5 (High Quality)
python scripts/run_workflow.py --preset quick_test --provider openai --model gpt-5

# Use xAI Grok (Fastest & Cheapest)
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4-fast
```

### Method 2: Edit Config File

Edit `config/workflow_config.yaml`:

```yaml
ai_provider:
  active_provider: "anthropic"  # Change to: "openai", "google", or "xai"
```

Then run:
```bash
python scripts/run_workflow.py --preset quick_test
```

### Method 3: Interactive Runner

```bash
python run_interactive.py
```

Select your preferred provider and model from the menu.

---

## 📋 Provider Details

### 1. Anthropic Claude (Recommended)

**When to use:**
- Best overall balance of quality and cost
- Complex medical reasoning
- High-quality interview responses
- Default choice for production

**Available models:**
```bash
# Best balance (RECOMMENDED)
--provider anthropic --model claude-sonnet-4-5-20250929

# Maximum quality (expensive)
--provider anthropic --model claude-opus-4-1

# Fast and economical
--provider anthropic --model claude-haiku-4-5
```

**Example:**
```bash
python scripts/run_workflow.py --preset quick_test \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929
```

---

### 2. Google Gemini (Best Value)

**When to use:**
- Budget-conscious projects
- High volume of interviews
- Fast iteration and testing
- Cost optimization

**Available models:**
```bash
# Fast and cheap (RECOMMENDED FOR VALUE)
--provider google --model gemini-2.5-flash

# Best quality Gemini
--provider google --model gemini-2.5-pro

# Ultra-budget option
--provider google --model gemini-2.5-flash-lite
```

**Example:**
```bash
python scripts/run_workflow.py --preset quick_test \
  --provider google \
  --model gemini-2.5-flash
```

**Note:** Free tier has quota limits (10 requests/day). Upgrade for production use.

---

### 3. OpenAI GPT-5

**When to use:**
- High-quality outputs required
- Balanced performance
- Familiar with GPT ecosystem

**Available models:**
```bash
# Recommended OpenAI model
--provider openai --model gpt-5

# Best GPT performance
--provider openai --model gpt-5-pro

# Budget GPT option
--provider openai --model gpt-5-mini
```

**Example:**
```bash
python scripts/run_workflow.py --preset quick_test \
  --provider openai \
  --model gpt-5
```

---

### 4. xAI Grok (Fastest)

**When to use:**
- Maximum speed required
- Cost optimization
- High volume processing
- Real-time applications

**Available models:**
```bash
# Best value - very fast (RECOMMENDED)
--provider xai --model grok-4-fast

# Most capable Grok
--provider xai --model grok-4

# Budget option
--provider xai --model grok-3
```

**Example:**
```bash
python scripts/run_workflow.py --preset quick_test \
  --provider xai \
  --model grok-4-fast
```

---

## 🎯 Use Case Recommendations

### Development & Testing
```bash
# Fastest iteration - Grok
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4-fast

# Best value - Gemini
python scripts/run_workflow.py --preset quick_test --provider google --model gemini-2.5-flash
```

### Production - Quality Priority
```bash
# Best balance - Claude Sonnet
python scripts/run_workflow.py --preset standard --provider anthropic --model claude-sonnet-4-5-20250929

# Maximum quality - Claude Opus
python scripts/run_workflow.py --preset standard --provider anthropic --model claude-opus-4-1
```

### Production - Cost Priority
```bash
# Best value - Gemini Flash
python scripts/run_workflow.py --preset production --provider google --model gemini-2.5-flash

# Fastest & cheap - Grok Fast
python scripts/run_workflow.py --preset production --provider xai --model grok-4-fast
```

### Large Scale (1000+ interviews)
```bash
# Cost-effective at scale - Gemini
python scripts/run_workflow.py --personas 1000 --records 1000 \
  --provider google --model gemini-2.5-flash

# Speed-optimized - Grok
python scripts/run_workflow.py --personas 1000 --records 1000 \
  --provider xai --model grok-4-fast
```

---

## 💡 Cost Comparison

**For 100 interviews (estimated):**

| Provider | Model | Estimated Cost | Time |
|----------|-------|----------------|------|
| Google | gemini-2.5-flash | ~$1.00 | ~25 min |
| xAI | grok-4-fast | ~$0.50 | ~20 min |
| Anthropic | claude-sonnet-4-5 | ~$8.00 | ~30 min |
| OpenAI | gpt-5 | ~$5.40 | ~30 min |
| Anthropic | claude-opus-4-1 | ~$40.00 | ~45 min |

**For 1000 interviews (estimated):**

| Provider | Model | Estimated Cost | Time |
|----------|-------|----------------|------|
| Google | gemini-2.5-flash | ~$10.00 | ~4 hours |
| xAI | grok-4-fast | ~$5.00 | ~3 hours |
| Anthropic | claude-sonnet-4-5 | ~$80.00 | ~5 hours |
| OpenAI | gpt-5 | ~$54.00 | ~5 hours |

---

## 🔧 API Key Management

All API keys are stored in `.env` and automatically loaded:

```bash
# View your configuration
cat .env

# Keys required:
ANTHROPIC_API_KEY=sk-ant-...
OPENAI_API_KEY=sk-proj-...
GOOGLE_API_KEY=AIza...
XAI_API_KEY=xai-...
```

**All keys are automatically loaded - no manual export needed!**

---

## 🔄 Switching Between Providers

### During Development
```bash
# Test with cheapest
python scripts/run_workflow.py --preset quick_test --provider xai --model grok-4-fast

# Validate with best quality
python scripts/run_workflow.py --preset quick_test --provider anthropic --model claude-sonnet-4-5-20250929
```

### For Different Datasets
```bash
# Small dataset (10 interviews) - use best quality
python scripts/run_workflow.py --personas 10 --records 10 --provider anthropic

# Large dataset (1000 interviews) - optimize for cost
python scripts/run_workflow.py --personas 1000 --records 1000 --provider google
```

---

## 📊 Multi-Provider Comparison

Run the same dataset with multiple providers to compare:

```bash
# Run with Claude
python scripts/run_workflow.py --preset quick_test --provider anthropic
mv data/interviews data/interviews_claude

# Run with Gemini
python scripts/run_workflow.py --preset quick_test --provider google
mv data/interviews data/interviews_gemini

# Run with GPT
python scripts/run_workflow.py --preset quick_test --provider openai
mv data/interviews data/interviews_gpt

# Compare results
diff data/interviews_claude data/interviews_gemini
```

---

## ✅ Provider Status

Check which providers are configured:

```bash
# View config
cat config/workflow_config.yaml | grep -A 5 "enabled: true"
```

All providers show:
- ✅ Anthropic - ENABLED
- ✅ OpenAI - ENABLED
- ✅ Google - ENABLED
- ✅ xAI - ENABLED

---

## 🆘 Troubleshooting

### "API key not found" Error
```bash
# Check your .env file
cat .env | grep API_KEY

# Verify key is loaded
python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('ANTHROPIC_API_KEY'))"
```

### Rate Limit Errors
```bash
# Reduce batch size
python scripts/run_workflow.py --preset quick_test --provider google

# Or switch to different provider
python scripts/run_workflow.py --preset quick_test --provider anthropic
```

### Provider Not Working
```bash
# Test provider directly
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-sonnet-4-5-20250929 \
  --count 1 \
  --protocol Script/interview_protocols/prenatal_care.json
```

---

## 🎓 Best Practices

1. **Development:** Start with `--preset quick_test` using Grok or Gemini
2. **Testing:** Validate with Claude Sonnet on small dataset
3. **Production:** Choose based on quality vs. cost needs
4. **Large Scale:** Use Gemini or Grok for cost optimization

**All providers are ready to use - just switch and go!** 🚀
