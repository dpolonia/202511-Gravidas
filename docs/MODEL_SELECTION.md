# Model Selection Guide

Quick guide for choosing between different AI models in the Synthetic Gravidas Pipeline.

## Quick Start

### Option 1: Edit config.yaml (Recommended)

Edit `config/config.yaml`:

```yaml
# Choose your provider
active_provider: "anthropic"  # anthropic, openai, or google

# Choose your model
active_model: "claude-4.5-sonnet"  # See available models below
```

Then run:
```bash
python scripts/04_conduct_interviews.py --count 10
```

### Option 2: Command Line Override

```bash
# Use a specific provider and model
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-4.5-sonnet \
  --count 10
```

---

## Available Models

### 🔶 Anthropic (Claude)

| Model | Cost (per 1M tokens) | Quality | Best For |
|-------|---------------------|---------|----------|
| `claude-4.1-opus` | $15/$75 | Excellent | Complex reasoning, high-stakes |
| **`claude-4.5-sonnet`** ⭐ | $3/$15 | Excellent | **Recommended - Best balance** |
| `claude-4.5-haiku` | $1/$5 | Very Good | High volume, cost optimization |
| `claude-3-haiku` | $0.25/$1.25 | Good | Testing, prototyping |

### 🔷 OpenAI (GPT-5)

| Model | Cost (per 1M tokens) | Quality | Best For |
|-------|---------------------|---------|----------|
| `gpt-5-pro` | $15/$120 | Excellent | Mission-critical tasks |
| **`gpt-5`** ⭐ | $1.25/$10 | Excellent | **Recommended - Advanced work** |
| `gpt-5-mini` | $0.25/$2 | Very Good | Fast, good value |
| `gpt-5-nano` | $0.05/$0.40 | Good | Maximum cost savings |

### 🟢 Google (Gemini)

| Model | Cost (per 1M tokens) | Quality | Best For |
|-------|---------------------|---------|----------|
| **`gemini-2.5-pro`** ⭐ | $1.25/$10 | Excellent | **Recommended - Advanced AI** |
| `gemini-2.5-flash` | $0.30/$2.50 | Very Good | Enterprise workloads |
| `gemini-2.5-flash-lite` | $0.10/$0.40 | Good | High-volume tasks |
| `gemini-2.0-flash` | $0.05/$0.20 | Good | Legacy, experimental |

---

## Usage Examples

### Example 1: Use Config Defaults

```bash
# Uses active_provider and active_model from config.yaml
python scripts/04_conduct_interviews.py --count 10
```

### Example 2: Test with Cheapest Model

```bash
# Test with lowest cost model
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-3-haiku \
  --count 5
```

### Example 3: Production with Best Quality

```bash
# Use best quality for important interviews
python scripts/04_conduct_interviews.py \
  --provider anthropic \
  --model claude-4.1-opus \
  --count 100
```

### Example 4: Compare Models

Run small batches with each provider to compare:

```bash
# Test Anthropic
python scripts/04_conduct_interviews.py \
  --provider anthropic --model claude-4.5-sonnet \
  --count 10 --output data/interviews/claude

# Test OpenAI
python scripts/04_conduct_interviews.py \
  --provider openai --model gpt-5 \
  --count 10 --output data/interviews/openai

# Test Google
python scripts/04_conduct_interviews.py \
  --provider google --model gemini-2.5-pro \
  --count 10 --output data/interviews/google
```

---

## Cost Estimation

### For 10,000 Interviews

Assuming average interview: 3,000 input tokens + 2,000 output tokens

| Provider | Model | Estimated Cost |
|----------|-------|----------------|
| Anthropic | claude-4.1-opus | $1,650 |
| Anthropic | **claude-4.5-sonnet** | **$390** ⭐ |
| Anthropic | claude-4.5-haiku | $130 |
| Anthropic | claude-3-haiku | $32.50 |
| OpenAI | gpt-5-pro | $2,850 |
| OpenAI | **gpt-5** | **$237.50** ⭐ |
| OpenAI | gpt-5-mini | $47.50 |
| OpenAI | gpt-5-nano | $9.50 |
| Google | **gemini-2.5-pro** | **$237.50** ⭐ |
| Google | gemini-2.5-flash | $59 |
| Google | gemini-2.5-flash-lite | $12 |
| Google | gemini-2.0-flash | $5.50 |

**Recommended for 10K interviews:** Claude 4.5 Sonnet, GPT-5, or Gemini 2.5 Pro

---

## Tips

### Start Small
Always test with 5-10 interviews before running 10,000:
```bash
python scripts/04_conduct_interviews.py --count 5
```

### Monitor Costs
Check your provider dashboard after first 100 interviews to verify costs.

### Mix and Match
Use expensive models for first 1,000, then switch to cheaper:
```bash
# First 1,000 with premium model
python scripts/04_conduct_interviews.py \
  --provider anthropic --model claude-4.1-opus \
  --count 1000 --start-index 0

# Next 9,000 with standard model
python scripts/04_conduct_interviews.py \
  --provider anthropic --model claude-4.5-sonnet \
  --count 9000 --start-index 1000
```

### Budget Testing
Use cheapest models for testing protocols:
```bash
python scripts/04_conduct_interviews.py \
  --provider openai --model gpt-5-nano \
  --protocol Script/interview_protocols/pregnancy_experience.json \
  --count 5
```

---

## Configuration File Reference

Your `config/config.yaml` should look like this:

```yaml
# ACTIVE MODEL SELECTION
active_provider: "anthropic"
active_model: "claude-4.5-sonnet"

api_keys:
  anthropic:
    api_key: "sk-ant-..."
    models:
      claude-4.1-opus: {...}
      claude-4.5-sonnet: {...}
      # ... etc

  openai:
    api_key: "sk-proj-..."
    models:
      gpt-5-pro: {...}
      # ... etc

  google:
    api_key: "AIza..."
    models:
      gemini-2.5-pro: {...}
      # ... etc
```

## Getting Help

```bash
# See all options
python scripts/04_conduct_interviews.py --help
```

---

## Summary

**For most users:**
1. Edit `active_provider` and `active_model` in `config/config.yaml`
2. Run: `python scripts/04_conduct_interviews.py --count 10`
3. Check results and costs
4. Scale up to full 10,000

**Recommended models:**
- **Best balance:** claude-4.5-sonnet ($390 for 10K)
- **Best value:** gpt-5 or gemini-2.5-pro (~$238 for 10K)
- **Budget:** gpt-5-nano ($9.50 for 10K)
